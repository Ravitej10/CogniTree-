"""Phase 2: Question Generation Factory.

Generates schema-validated questions grounded in curriculum topics or uploaded
course documents. Generation fails explicitly when Gemini is unavailable or
returns invalid output; synthetic fallback questions are never stored.
"""

import json
import random
import re
import time
from sqlalchemy.orm import Session

from core.config import settings
from core.models import Question, SkillType, SourceDocument
from core.schemas import GeneratedQuestion


class QuestionGenerationError(RuntimeError):
    """Raised when Gemini cannot produce a valid question."""

# Try configuring Gemini if API key is present
_gemini_model = None
if settings.google_api_key and settings.google_api_key.strip():
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.google_api_key)
        _gemini_model = genai.GenerativeModel(model_name=settings.google_model)
    except Exception as e:
        print(f"[QuestionFactory] Gemini init warning: {e}")


_PROMPT_TEMPLATE = """You are an expert technical interviewer and educator writing a multiple-choice question for a student studying "{topic}", specifically "{subtopic}".

Base the question strictly on the context provided below:
---
{context}
---

Requirements:
- Exactly 4 distinct options (A, B, C, D).
- Exactly 1 unambiguous correct answer.
- Distractors must be plausible technical misconceptions, not silly jokes.
- Classify skill_type as "memorization" (definitions, bounds, syntax) or "application" (tracing, problem solving, analysis).
- Provide a clear 1-2 sentence concept explanation.

Respond ONLY with valid JSON in this exact structure:
{{
  "topic": "{topic}",
  "subtopic": "{subtopic}",
  "skill_type": "memorization" or "application",
  "question_text": "question string",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "answer_index": 0,
  "explanation": "explanation string"
}}
"""


def verify_gemini_connection() -> dict:
    """Checks that the configured model exists and supports text generation."""
    if _gemini_model is None:
        raise QuestionGenerationError(
            "Gemini is not initialized. Check GOOGLE_API_KEY and GOOGLE_MODEL."
        )

    try:
        import google.generativeai as genai
        available = {
            model.name.removeprefix("models/")
            for model in genai.list_models()
            if "generateContent" in model.supported_generation_methods
        }
    except Exception as exc:
        raise QuestionGenerationError(
            f"Could not query Gemini model availability: {exc}"
        ) from exc

    if settings.google_model not in available:
        raise QuestionGenerationError(
            f"Configured model '{settings.google_model}' is unavailable for generateContent."
        )

    return {"connected": True, "model": settings.google_model}


def _is_non_retryable_provider_error(exc: Exception) -> bool:
    """Returns True for errors that another immediate request cannot fix."""
    message = str(exc).lower()
    return any(
        marker in message
        for marker in (
            "400 ",
            "401 ",
            "403 ",
            "404 ",
            "429 ",
            "invalid api key",
            "permission denied",
            "quota exceeded",
        )
    )


def _provider_error_message(exc: Exception) -> str:
    message = str(exc)
    lowered = message.lower()
    if "429" in lowered or "quota exceeded" in lowered:
        return (
            "Gemini quota exceeded. Wait for the quota to reset, enable billing, "
            "or configure another supported model with available quota."
        )
    if "404" in lowered:
        return f"Gemini model '{settings.google_model}' was not found or is unavailable."
    if "401" in lowered or "403" in lowered or "api key" in lowered:
        return "Gemini authentication failed. Check GOOGLE_API_KEY and project permissions."
    return message


def _request_gemini_json(prompt: str) -> dict | list:
    """Calls Gemini and returns one parsed JSON object or array."""
    if _gemini_model is None:
        raise QuestionGenerationError(
            "Gemini is not initialized. Check GOOGLE_API_KEY and GOOGLE_MODEL."
        )

    last_error = None
    for attempt in range(settings.llm_generation_attempts):
        try:
            response = _gemini_model.generate_content(
                prompt,
                generation_config={
                    "response_mime_type": "application/json",
                    "temperature": 0.3,
                    "max_output_tokens": 8192,
                },
                request_options={
                    "timeout": settings.llm_request_timeout_seconds,
                    # Outer retries below can distinguish transient failures from
                    # quota/auth/model errors; disable the SDK's opaque retry loop.
                    "retry": None,
                },
            )
            text = response.text.strip()
            text = re.sub(r"^```json\s*", "", text)
            text = re.sub(r"\s*```$", "", text)
            data = json.loads(text)
            if not isinstance(data, (dict, list)):
                raise ValueError("Gemini did not return a JSON object or array.")
            return data
        except Exception as exc:
            last_error = exc
            if _is_non_retryable_provider_error(exc):
                raise QuestionGenerationError(_provider_error_message(exc)) from exc
            if attempt < settings.llm_generation_attempts - 1:
                time.sleep(2**attempt)

    raise QuestionGenerationError(
        f"Gemini generation failed after {settings.llm_generation_attempts} attempts: "
        f"{_provider_error_message(last_error)}"
    ) from last_error


def _generate_with_gemini(prompt: str) -> dict:
    """Generates and parses exactly one question object."""
    data = _request_gemini_json(prompt)
    if not isinstance(data, dict):
        raise QuestionGenerationError("Gemini returned an array when one question was requested.")
    return data


def _generate_many_with_gemini(prompt: str, expected_count: int) -> list[dict]:
    """Generates a batch of question objects in one provider request."""
    data = _request_gemini_json(prompt)
    if not isinstance(data, list):
        raise QuestionGenerationError("Gemini returned an object when a question array was requested.")
    if len(data) != expected_count:
        raise QuestionGenerationError(
            f"Gemini returned {len(data)} questions; expected exactly {expected_count}."
        )
    if not all(isinstance(item, dict) for item in data):
        raise QuestionGenerationError("Gemini returned a non-object item in the question array.")
    return data


def generate_question(topic: str, subtopic: str, document_id: int | None = None) -> GeneratedQuestion | None:
    """Retrieves grounding context and generates one question."""
    from services.vector_store import query_by_topic

    context_chunks = query_by_topic(f"{topic} {subtopic}", n_results=3, document_id=document_id)
    if not context_chunks:
        return None

    context_text = "\n\n".join(context_chunks)

    prompt = _PROMPT_TEMPLATE.format(
        topic=topic,
        subtopic=subtopic,
        context=context_text[:6000],
    )
    parsed = _generate_with_gemini(prompt)
    try:
        return GeneratedQuestion.model_validate(
            {**parsed, "topic": topic, "subtopic": subtopic}
        )
    except Exception as exc:
        raise QuestionGenerationError(
            f"Gemini returned an invalid question: {exc}"
        ) from exc


def generate_and_store(
    db: Session,
    topic: str,
    subtopic: str,
    source_document_id: int | None = None,
) -> Question | None:
    """Generates one question and commits it to the question bank."""
    generated = generate_question(topic, subtopic, document_id=source_document_id)
    if generated is None:
        return None

    skill_enum = SkillType.APPLICATION if generated.skill_type == "application" else SkillType.MEMORIZATION
    question = Question(
        topic=generated.topic,
        subtopic=generated.subtopic,
        skill_type=skill_enum,
        question_text=generated.question_text,
        options=generated.options,
        answer_index=generated.answer_index,
        explanation=generated.explanation,
        source_document_id=source_document_id,
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


def generate_from_document_chunks(
    db: Session,
    document_id: int,
    count: int = 5,
) -> list[Question]:
    """Generates up to `count` questions grounded directly in chunks of the given document."""
    from services.vector_store import get_all_chunks_for_document

    doc = db.get(SourceDocument, document_id)
    if not doc:
        return []

    chunks = get_all_chunks_for_document(document_id)
    if not chunks:
        return []

    doc_title = doc.filename.rsplit(".", 1)[0].replace("_", " ").title()
    # Four questions per tag gives two observations for each of the two skill
    # dimensions. Smaller requested batches intentionally use fewer tags rather
    # than producing one-off tags that cannot support diagnosis.
    tag_count = max(1, min(4, len(chunks), count // 4 or 1))
    selected_chunks = random.sample(chunks, tag_count)
    base_size, remainder = divmod(count, tag_count)
    group_sizes = [base_size + (1 if index < remainder else 0) for index in range(tag_count)]
    source_sections = "\n\n".join(
        f"[TAG GROUP {index + 1} — CREATE {group_sizes[index]} QUESTIONS]\n{chunk[:2500]}"
        for index, chunk in enumerate(selected_chunks)
    )
    prompt = f"""You are an expert educator generating an assessment from "{doc.filename}".

Create exactly {count} multiple-choice questions using the numbered tag groups below. For each group, first identify one meaningful, specific concept tag, then create the stated number of distinct questions for that same tag.

{source_sections}

Requirements for every question:
- Use clear, corrected English; never reproduce OCR corruption or truncated text.
- Test a meaningful technical concept, not an arbitrary phrase from the excerpt.
- Provide exactly 4 distinct, plausible options and exactly 1 correct answer.
- Within every group of 4 questions, create exactly 2 "memorization" questions and 2 "application" questions.
- All questions from the same group must use exactly the same concise subtopic tag.
- Questions must test different aspects or scenarios; do not paraphrase duplicates.
- Provide a concise explanation supported by the source.
- Do not use generic distractors about reverse order, deprecation, or linear scanning unless the source explicitly supports them.

Respond ONLY with a JSON array containing exactly {count} objects, grouped in source order:
[
  {{
    "topic": "{doc_title[:30]}",
    "subtopic": "specific shared concept tag",
    "skill_type": "memorization",
    "question_text": "...",
    "options": ["...", "...", "...", "..."],
    "answer_index": 0,
    "explanation": "..."
  }}
]
"""
    batch = _generate_many_with_gemini(prompt, count)
    generated_questions: list[GeneratedQuestion] = []

    for index, q_data in enumerate(batch):
        try:
            generated = GeneratedQuestion.model_validate(q_data)
        except Exception as exc:
            raise QuestionGenerationError(
                f"Gemini returned an invalid question at batch position {index + 1}: {exc}"
            ) from exc
        if len(set(generated.options)) != 4:
            raise QuestionGenerationError(
                f"Gemini returned duplicate options at batch position {index + 1}."
            )
        generated_questions.append(generated)

    offset = 0
    for group_index, group_size in enumerate(group_sizes):
        group = generated_questions[offset : offset + group_size]
        offset += group_size
        subtopics = {question.subtopic.strip().casefold() for question in group}
        if len(subtopics) != 1:
            raise QuestionGenerationError(
                f"Gemini used inconsistent subtopic tags in tag group {group_index + 1}."
            )
        if group_size >= 4:
            skills = [question.skill_type for question in group]
            if skills.count("memorization") < 2 or skills.count("application") < 2:
                raise QuestionGenerationError(
                    f"Gemini did not provide enough skill variety in tag group {group_index + 1}."
                )

    normalized_stems = {
        re.sub(r"\W+", " ", question.question_text.casefold()).strip()
        for question in generated_questions
    }
    if len(normalized_stems) != len(generated_questions):
        raise QuestionGenerationError("Gemini returned duplicate questions in the batch.")

    created_questions: list[Question] = []
    for generated in generated_questions:
        skill_enum = SkillType.APPLICATION if generated.skill_type == "application" else SkillType.MEMORIZATION
        question = Question(
            topic=generated.topic,
            subtopic=generated.subtopic,
            skill_type=skill_enum,
            question_text=generated.question_text,
            options=generated.options,
            answer_index=generated.answer_index,
            explanation=generated.explanation,
            source_document_id=document_id,
        )
        db.add(question)
        created_questions.append(question)

    db.commit()
    for q in created_questions:
        db.refresh(q)

    return created_questions
