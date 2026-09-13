import random
from collections import defaultdict
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from core.config import settings
from core.database import get_db
from core.security import get_current_user
from core.models import Question, QuizSession, Response, User
from core.schemas import (
    QuizCompletionResponse,
    QuizReviewItem,
    StartQuizResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
)

router = APIRouter(prefix="/api/quiz", tags=["quiz"])


def _balanced_sample(questions: list[Question], count: int) -> list[Question]:
    """Round-robins across subtopic/skill cells instead of over-sampling one tag."""
    groups: dict[tuple[str, str], list[Question]] = defaultdict(list)
    for question in questions:
        skill = question.skill_type.value if hasattr(question.skill_type, "value") else str(question.skill_type)
        groups[(question.subtopic, skill)].append(question)
    for group in groups.values():
        random.shuffle(group)

    keys = list(groups)
    random.shuffle(keys)
    selected: list[Question] = []
    while keys and len(selected) < count:
        next_keys = []
        for key in keys:
            if groups[key] and len(selected) < count:
                selected.append(groups[key].pop())
            if groups[key]:
                next_keys.append(key)
        keys = next_keys
    return selected


@router.post("/start", response_model=StartQuizResponse)
def start_quiz(
    topic: Optional[str] = Query(None, description="Optional topic filter"),
    subtopic: Optional[str] = Query(None, description="Optional fine-grained tag filter"),
    document_id: Optional[int] = Query(None, description="Optional source document filter"),
    count: Optional[int] = Query(10, ge=1, le=20, description="Number of questions (max 20)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Starts a quiz session with selectable question count (up to 20)."""
    query = db.query(Question)
    if topic:
        query = query.filter(Question.topic == topic)
    if subtopic:
        query = query.filter(Question.subtopic == subtopic)
    if document_id:
        query = query.filter(Question.source_document_id == document_id)

    questions_pool = query.all()
    if not questions_pool:
        target_desc = f" for {topic}" if topic else (f" for document #{document_id}" if document_id else "")
        detail = f"No questions found{target_desc}."
        if document_id:
            detail += " Generate questions from the document before starting its quiz."
        raise HTTPException(status_code=404, detail=detail)

    target_count = min(count or 10, 20)
    target_count = max(1, min(len(questions_pool), target_count))

    sampled_questions = _balanced_sample(questions_pool, target_count)

    session = QuizSession(user_id=current_user.id, is_adaptive=False)
    db.add(session)
    db.commit()
    db.refresh(session)

    return StartQuizResponse(session_id=session.id, questions=sampled_questions)


@router.post("/{session_id}/answer", response_model=SubmitAnswerResponse)
def submit_answer(
    session_id: int,
    payload: SubmitAnswerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = db.get(QuizSession, session_id)
    if session is None or session.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Quiz session not found.")

    question = db.get(Question, payload.question_id)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found.")

    is_correct = payload.selected_index == question.answer_index

    # Check if this question was already answered in this session (e.g. retry/update)
    existing_response = (
        db.query(Response)
        .filter(Response.session_id == session.id, Response.question_id == question.id)
        .first()
    )

    if existing_response:
        existing_response.selected_index = payload.selected_index
        existing_response.is_correct = is_correct
        existing_response.response_time_ms = payload.response_time_ms
    else:
        response = Response(
            session_id=session.id,
            question_id=question.id,
            selected_index=payload.selected_index,
            is_correct=is_correct,
            response_time_ms=payload.response_time_ms,
        )
        db.add(response)

    db.commit()

    return SubmitAnswerResponse(
        is_correct=is_correct,
        correct_index=question.answer_index,
        explanation=question.explanation,
    )


@router.post("/{session_id}/complete", response_model=QuizCompletionResponse)
def complete_quiz(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = db.get(QuizSession, session_id)
    if session is None or session.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Quiz session not found.")

    session.completed_at = func.now()
    db.commit()

    # Build full review details for completion
    responses = db.query(Response).filter(Response.session_id == session.id).all()
    reviews: list[QuizReviewItem] = []
    correct_count = 0

    for r in responses:
        q = db.get(Question, r.question_id)
        if q:
            if r.is_correct:
                correct_count += 1
            reviews.append(
                QuizReviewItem(
                    question_id=q.id,
                    topic=q.topic,
                    subtopic=q.subtopic,
                    skill_type=q.skill_type.value if hasattr(q.skill_type, "value") else str(q.skill_type),
                    question_text=q.question_text,
                    options=q.options,
                    selected_index=r.selected_index,
                    correct_index=q.answer_index,
                    is_correct=r.is_correct,
                    explanation=q.explanation,
                )
            )

    total_q = len(reviews)
    acc = int((correct_count / total_q) * 100) if total_q > 0 else 0

    return QuizCompletionResponse(
        session_id=session.id,
        total_questions=total_q,
        correct_count=correct_count,
        accuracy_percentage=acc,
        wrong_count=total_q - correct_count,
        reviews=reviews,
    )


@router.get("/{session_id}/review", response_model=QuizCompletionResponse)
def get_quiz_review(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return complete_quiz(session_id=session_id, db=db, current_user=current_user)
