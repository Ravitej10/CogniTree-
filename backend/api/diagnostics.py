from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.config import settings
from core.database import get_db
from core.security import get_current_user
from core.models import QuizSession, User
from core.schemas import AdaptiveQuizResponse, DiagnosticMatrixResponse, QuestionResponse
from services.adaptive_service import build_remediation_quiz
from services.diagnostic_service import compute_matrix, get_gap_cells

router = APIRouter(prefix="/api/diagnostics", tags=["diagnostics"])


@router.get("/matrix", response_model=DiagnosticMatrixResponse)
def get_diagnostic_matrix(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Returns the student's live Topic x Skill-Type performance grid."""
    cells = compute_matrix(db, current_user.id)
    return DiagnosticMatrixResponse(
        user_id=current_user.id, threshold=settings.mastery_threshold, cells=cells
    )


@router.post("/adaptive-quiz", response_model=AdaptiveQuizResponse)
def start_adaptive_quiz(
    count: Optional[int] = Query(10, ge=1, le=20, description="Remediation question count"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Assembles and starts a remediation quiz targeted at the student's
    diagnosed gaps (Phase 5 — the adaptive loop)."""
    gap_cells = get_gap_cells(db, current_user.id)
    if not gap_cells:
        raise HTTPException(
            status_code=422,
            detail="No diagnosed gaps yet — complete a regular quiz first so the matrix has data.",
        )

    target_count = min(count or 10, 20)
    questions = build_remediation_quiz(db, current_user.id, gap_cells, target_count=target_count)
    if not questions:
        raise HTTPException(
            status_code=422,
            detail="No questions available for the diagnosed gaps yet.",
        )

    session = QuizSession(user_id=current_user.id, is_adaptive=True)
    db.add(session)
    db.commit()
    db.refresh(session)

    return AdaptiveQuizResponse(
        session_id=session.id,
        targeted_gaps=gap_cells,
        questions=[QuestionResponse.model_validate(q) for q in questions],
    )

