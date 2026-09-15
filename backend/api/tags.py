from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from core.models import ConceptTag, DocumentTagEvidence, Question, User
from core.schemas import (
    ConceptTagResponse,
    DocumentTagEvidenceResponse,
    ResolveTagRequest,
    ResolveTagResponse,
    TagAliasResponse,
)
from core.security import get_current_user
from services.tag_service import resolve_canonical_tag


router = APIRouter(prefix="/api/tags", tags=["taxonomy"])


def _tag_response(db: Session, tag: ConceptTag) -> ConceptTagResponse:
    return ConceptTagResponse(
        id=tag.id,
        name=tag.name,
        normalized_name=tag.normalized_name,
        definition=tag.definition,
        subject=tag.subject,
        parent_tag_id=tag.parent_tag_id,
        status=tag.status.value if hasattr(tag.status, "value") else str(tag.status),
        aliases=[TagAliasResponse.model_validate(alias) for alias in tag.aliases],
        question_count=db.query(Question).filter(Question.tag_id == tag.id).count(),
        evidence_count=(
            db.query(DocumentTagEvidence)
            .filter(DocumentTagEvidence.tag_id == tag.id)
            .count()
        ),
    )


@router.get("", response_model=list[ConceptTagResponse])
def list_tags(
    subject: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(ConceptTag)
    if subject:
        query = query.filter(ConceptTag.subject == subject)
    tags = query.order_by(ConceptTag.subject, ConceptTag.name).all()
    return [_tag_response(db, tag) for tag in tags]


@router.get("/documents/{document_id}", response_model=list[DocumentTagEvidenceResponse])
def list_document_tags(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    evidence = (
        db.query(DocumentTagEvidence)
        .filter(DocumentTagEvidence.document_id == document_id)
        .order_by(DocumentTagEvidence.chunk_index)
        .all()
    )
    responses = []
    for record in evidence:
        payload = DocumentTagEvidenceResponse.model_validate(record)
        payload.tag = _tag_response(db, record.tag)
        responses.append(payload)
    return responses


@router.get("/{tag_id}", response_model=ConceptTagResponse)
def get_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tag = db.get(ConceptTag, tag_id)
    if tag is None:
        raise HTTPException(status_code=404, detail="Concept tag not found.")
    return _tag_response(db, tag)


@router.post("/resolve", response_model=ResolveTagResponse)
def resolve_tag(
    payload: ResolveTagRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tag, match_method = resolve_canonical_tag(
        db,
        name=payload.name,
        definition=payload.definition,
        subject=payload.subject,
    )
    db.commit()
    db.refresh(tag)
    return ResolveTagResponse(match_method=match_method, tag=_tag_response(db, tag))
