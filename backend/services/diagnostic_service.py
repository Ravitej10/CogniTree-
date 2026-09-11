"""Phase 3: Evaluation & Adaptive Diagnostic Loop — the diagnostic half.

Turns a student's raw response log into the Topic x Skill-Type performance
grid described in the deck, and flags cells below the mastery threshold as
gaps. This is what separates "weak in Chemistry" from "weak in balancing
redox equations, specifically the application skill."
"""

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from core.config import settings
from core.models import Question, Response, QuizSession
from core.schemas import MatrixCell


def compute_matrix(db: Session, user_id: int) -> list[MatrixCell]:
    """Aggregates every response a student has ever given, grouped by
    topic and skill type, into accuracy cells."""
    rows = (
        db.query(
            Question.topic,
            Question.skill_type,
            func.count(Response.id).label("attempted"),
            func.sum(case((Response.is_correct.is_(True), 1), else_=0)).label("correct"),
        )
        .join(Response, Response.question_id == Question.id)
        .join(QuizSession, QuizSession.id == Response.session_id)
        .filter(QuizSession.user_id == user_id)
        .group_by(Question.topic, Question.skill_type)
        .all()
    )

    cells: list[MatrixCell] = []
    for topic, skill_type, attempted, correct in rows:
        correct = correct or 0
        accuracy = correct / attempted if attempted else 0.0
        cells.append(
            MatrixCell(
                topic=topic,
                skill_type=skill_type.value if hasattr(skill_type, "value") else skill_type,
                correct=correct,
                attempted=attempted,
                accuracy=round(accuracy, 3),
                is_gap=accuracy < settings.mastery_threshold,
            )
        )
    return cells


def get_gap_cells(db: Session, user_id: int) -> list[MatrixCell]:
    return [cell for cell in compute_matrix(db, user_id) if cell.is_gap]
