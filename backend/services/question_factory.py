"""Phase 2: Question Generation Factory.

Generates schema-validated questions grounded in curriculum topics or uploaded
course documents. Supports Gemini API with JSON structure validation and
includes a grounded extractive question generator for offline/resilient use.
"""

import json
import random
import re
from sqlalchemy.orm import Session

from core.config import settings
from core.models import Question, SkillType, SourceDocument
from core.schemas import GeneratedQuestion

# Try configuring Gemini if API key is present
_gemini_model = None
if settings.google_api_key and settings.google_api_key.strip():
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.google_api_key)
        _gemini_model = genai.GenerativeModel(model_name="gemini-1.5-flash")
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


def _generate_with_gemini(prompt: str) -> dict | None:
    """Calls Gemini with JSON instructions and parses output."""
    if _gemini_model is None:
        return None

    try:
        response = _gemini_model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        text = response.text.strip()
        # Clean JSON markdown fences if present
        text = re.sub(r"^```json\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
        data = json.loads(text)
        if isinstance(data, list) and data:
            data = data[0]
        return data
    except Exception as e:
        print(f"[QuestionFactory] Gemini generation warning: {e}")
        return None


def _heuristic_generate_from_chunk(chunk: str, topic: str, subtopic: str, doc_name: str = "") -> dict:
    """Intelligent fallback question generator that crafts concept questions from text chunks."""
    sentences = [s.strip() for s in re.split(r"[.!?]\s+", chunk) if len(s.strip()) > 35]
    if not sentences:
        sentences = [chunk[:200]]

    primary_sentence = sentences[0]
    is_application = len(sentences) > 2 or "calculate" in chunk.lower() or "algorithm" in chunk.lower() or "time" in chunk.lower()
    skill_type = "application" if is_application else "memorization"

    # Extract key keywords or nouns
    words = re.findall(r"\b[A-Za-z]{4,}\b", primary_sentence)
    key_concept = words[0] if words else "Concept"
    if len(words) > 1 and words[1].lower() not in ["this", "that", "with", "from", "when", "then"]:
        key_concept += f" {words[1]}"

    question_text = f"According to the material on {subtopic or topic}, which statement accurately describes the function and behavior of {key_concept}?"
    correct_opt = primary_sentence if len(primary_sentence) < 140 else primary_sentence[:137] + "..."

    # Create plausible distractors
    distractors = [
        f"It operates in reverse order by default, bypassing standard {topic} constraints.",
        f"It requires continuous linear scanning regardless of underlying indexing or caching.",
        f"It is solely deprecated in modern implementations due to non-deterministic overhead."
    ]

    all_opts = [correct_opt] + distractors
    random.shuffle(all_opts)
    answer_idx = all_opts.index(correct_opt)

    return {
        "topic": topic,
        "subtopic": subtopic,
        "skill_type": skill_type,
        "question_text": question_text,
        "options": all_opts,
        "answer_index": answer_idx,
        "explanation": f"Based on the course context: \"{primary_sentence}\".",
    }


def generate_question(topic: str, subtopic: str, document_id: int | None = None) -> GeneratedQuestion | None:
    """Retrieves grounding context and generates one question."""
    from services.vector_store import query_by_topic

    context_chunks = query_by_topic(f"{topic} {subtopic}", n_results=3, document_id=document_id)
    if not context_chunks:
        return None

    context_text = "\n\n".join(context_chunks)

    # 1. Try Gemini LLM
    if _gemini_model:
        prompt = _PROMPT_TEMPLATE.format(
            topic=topic,
            subtopic=subtopic,
            context=context_text[:3000],
        )
        parsed = _generate_with_gemini(prompt)
        if parsed and "question_text" in parsed and "options" in parsed:
            try:
                return GeneratedQuestion(
                    topic=topic,
                    subtopic=subtopic,
                    skill_type=parsed.get("skill_type", "memorization"),
                    question_text=parsed["question_text"],
                    options=parsed["options"][:4],
                    answer_index=parsed.get("answer_index", 0),
                    explanation=parsed.get("explanation", f"Reference: {subtopic} in {topic}."),
                )
            except Exception as e:
                print(f"[QuestionFactory] Validation error: {e}")

    # 2. Resilient fallback generator
    raw = _heuristic_generate_from_chunk(context_chunks[0], topic, subtopic)
    return GeneratedQuestion(
        topic=raw["topic"],
        subtopic=raw["subtopic"],
        skill_type=raw["skill_type"],
        question_text=raw["question_text"],
        options=raw["options"],
        answer_index=raw["answer_index"],
        explanation=raw["explanation"],
    )


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
    selected_chunks = chunks[:count] if len(chunks) <= count else random.sample(chunks, count)
    created_questions: list[Question] = []

    for i, chunk in enumerate(selected_chunks):
        subtopic_name = f"Section {i+1}: {doc_title[:24]}"
        
        # Try LLM or fallback generator
        q_data = None
        if _gemini_model:
            prompt = f"""You are generating an assessment question based strictly on this document excerpt from "{doc.filename}":
---
{chunk[:2500]}
---
Generate 1 multiple choice question with 4 options and 1 correct answer.
Respond in JSON format:
{{
  "topic": "{doc_title[:30]}",
  "subtopic": "{subtopic_name}",
  "skill_type": "application",
  "question_text": "...",
  "options": ["A", "B", "C", "D"],
  "answer_index": 0,
  "explanation": "..."
}}
"""
            q_data = _generate_with_gemini(prompt)

        if not q_data or "options" not in q_data or len(q_data["options"]) < 4:
            q_data = _heuristic_generate_from_chunk(chunk, doc_title[:30], subtopic_name, doc.filename)

        skill_enum = SkillType.APPLICATION if q_data.get("skill_type") == "application" else SkillType.MEMORIZATION
        question = Question(
            topic=q_data.get("topic", doc_title[:30]),
            subtopic=q_data.get("subtopic", subtopic_name),
            skill_type=skill_enum,
            question_text=q_data["question_text"],
            options=q_data["options"][:4],
            answer_index=q_data.get("answer_index", 0),
            explanation=q_data.get("explanation", f"Grounded in {doc.filename}"),
            source_document_id=document_id,
        )
        db.add(question)
        created_questions.append(question)

    db.commit()
    for q in created_questions:
        db.refresh(q)

    return created_questions

