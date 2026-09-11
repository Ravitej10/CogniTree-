from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from core.database import get_db
from core.security import get_current_user
from core.models import Question, User
from core.schemas import QuestionResponse, QuestionWithAnswer

router = APIRouter(prefix="/api/questions", tags=["questions"])


class GenerateQuestionRequest(BaseModel):
    topic: str
    subtopic: str
    source_document_id: int | None = None
    count: int = 1


@router.get("", response_model=list[QuestionResponse])
def list_questions(
    topic: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lists questions in the question bank, optionally filtered by topic."""
    query = db.query(Question)
    if topic:
        query = query.filter(Question.topic == topic)
    return query.order_by(Question.id.asc()).all()


@router.get("/topics", response_model=list[str])
def list_topics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lists distinct topics available in the question bank."""
    topics = db.query(Question.topic).distinct().all()
    return [t[0] for t in topics]


@router.post("/generate", response_model=list[QuestionWithAnswer])
def generate_questions(
    payload: GenerateQuestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_teacher:
        raise HTTPException(status_code=403, detail="Only teachers can generate questions.")

    from services.question_factory import generate_and_store

    generated = []
    for _ in range(payload.count):
        question = generate_and_store(
            db, payload.topic, payload.subtopic, payload.source_document_id
        )
        if question is not None:
            generated.append(question)

    if not generated:
        raise HTTPException(
            status_code=422,
            detail="No question could be generated — check that course material for this topic has been ingested.",
        )

    return generated
