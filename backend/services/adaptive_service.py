"""Adaptive Loop Module (Phase 5).

Takes the gap cells from diagnostic_service and assembles a remediation
quiz from questions targeting the student's diagnosed weak concepts.
"""

import random
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.models import Question, Response, QuizSession
from core.schemas import MatrixCell


def build_remediation_quiz(
    db: Session, user_id: int, gap_cells: list[MatrixCell], target_count: int = 10
) -> list[Question]:
    """Pulls questions matching the student's weak topic/skill cells, prioritizing
    unattempted ones, and falling back to weak topic items for remediation."""
    if not gap_cells:
        return []

    attempted_ids = {
        row[0]
        for row in db.query(Response.question_id)
        .join(QuizSession, QuizSession.id == Response.session_id)
        .filter(QuizSession.user_id == user_id)
        .all()
    }

    fresh_candidates: list[Question] = []
    all_gap_candidates: list[Question] = []

    for cell in gap_cells:
        stmt = select(Question).where(
            Question.topic == cell.topic,
            Question.skill_type == cell.skill_type,
        )
        matches = db.execute(stmt).scalars().all()
        for q in matches:
            all_gap_candidates.append(q)
            if q.id not in attempted_ids:
                fresh_candidates.append(q)

    # Prioritize fresh questions, fallback to all gap questions if needed
    random.shuffle(fresh_candidates)
    random.shuffle(all_gap_candidates)

    selected: list[Question] = []
    seen_ids: set[int] = set()

    for q in fresh_candidates:
        if q.id not in seen_ids:
            seen_ids.add(q.id)
            selected.append(q)

    if len(selected) < target_count:
        for q in all_gap_candidates:
            if q.id not in seen_ids:
                seen_ids.add(q.id)
                selected.append(q)
            if len(selected) >= target_count:
                break

    return selected[:target_count]
