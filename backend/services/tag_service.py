"""Canonical concept-tag creation, reuse, aliasing, and evidence linking."""

import re
import unicodedata
from difflib import SequenceMatcher

from sqlalchemy.orm import Session

from core.models import (
    ConceptTag,
    DocumentTagEvidence,
    TagAlias,
    TagStatus,
)


_GENERIC_TAG_WORDS = {
    "basics",
    "concept",
    "concepts",
    "fundamentals",
    "implementation",
    "introduction",
    "overview",
    "principles",
}

# These are terminology equivalents, not merely similar topics. The list can
# grow safely as teachers approve additional aliases.
_KNOWN_ALIAS_FAMILIES = {
    "lexical analysis": {
        "lexical analyzer",
        "lexical analyser",
        "scanner",
        "scanning",
        "tokenization",
        "tokenisation",
    },
}


def normalize_tag_name(value: str) -> str:
    """Produces a stable comparison key without changing the display name."""
    normalized = unicodedata.normalize("NFKC", value).casefold().strip()
    normalized = re.sub(r"[^a-z0-9\s-]", " ", normalized)
    normalized = re.sub(r"[-\s]+", " ", normalized)
    return normalized.strip()


def _canonical_alias_name(value: str) -> str:
    normalized = normalize_tag_name(value)
    simplified = " ".join(
        word for word in normalized.split() if word not in _GENERIC_TAG_WORDS
    )
    for canonical, aliases in _KNOWN_ALIAS_FAMILIES.items():
        if normalized == canonical or normalized in aliases or simplified == canonical or simplified in aliases:
            return canonical
    return normalized


def _comparison_signature(value: str) -> str:
    words = [
        word
        for word in _canonical_alias_name(value).split()
        if word not in _GENERIC_TAG_WORDS
    ]
    return " ".join(words)


def _find_similar_tag(
    db: Session,
    *,
    subject: str,
    candidate_name: str,
    threshold: float = 0.88,
) -> ConceptTag | None:
    candidate_signature = _comparison_signature(candidate_name)
    if not candidate_signature:
        return None

    best_tag = None
    best_score = 0.0
    tags = db.query(ConceptTag).filter(ConceptTag.subject == subject).all()
    for tag in tags:
        names = [tag.name, *(alias.alias for alias in tag.aliases)]
        score = max(
            SequenceMatcher(
                None,
                candidate_signature,
                _comparison_signature(name),
            ).ratio()
            for name in names
        )
        if score > best_score:
            best_tag, best_score = tag, score

    return best_tag if best_score >= threshold else None


def add_alias(db: Session, tag: ConceptTag, alias: str) -> TagAlias | None:
    normalized = normalize_tag_name(alias)
    if not normalized or normalized == tag.normalized_name:
        return None

    existing = (
        db.query(TagAlias)
        .filter(
            TagAlias.tag_id == tag.id,
            TagAlias.normalized_alias == normalized,
        )
        .first()
    )
    if existing:
        return existing

    record = TagAlias(tag_id=tag.id, alias=alias.strip(), normalized_alias=normalized)
    db.add(record)
    db.flush()
    return record


def resolve_canonical_tag(
    db: Session,
    *,
    name: str,
    definition: str,
    subject: str,
    status: TagStatus = TagStatus.APPROVED,
) -> tuple[ConceptTag, str]:
    """Returns a canonical tag and the match method used.

    Resolution order is deterministic: canonical name, alias, conservative
    lexical similarity, then creation. This prevents the LLM from owning IDs.
    """
    display_name = name.strip()
    normalized = normalize_tag_name(display_name)
    canonical_normalized = _canonical_alias_name(display_name)
    if not normalized:
        raise ValueError("A concept tag must have a non-empty name.")

    tag = (
        db.query(ConceptTag)
        .filter(
            ConceptTag.subject == subject,
            ConceptTag.normalized_name.in_({normalized, canonical_normalized}),
        )
        .first()
    )
    if tag:
        if normalized != tag.normalized_name:
            add_alias(db, tag, display_name)
        return tag, "exact"

    alias = (
        db.query(TagAlias)
        .join(ConceptTag, ConceptTag.id == TagAlias.tag_id)
        .filter(
            ConceptTag.subject == subject,
            TagAlias.normalized_alias == normalized,
        )
        .first()
    )
    if alias:
        return alias.tag, "alias"

    similar = _find_similar_tag(db, subject=subject, candidate_name=display_name)
    if similar:
        add_alias(db, similar, display_name)
        return similar, "similar"

    canonical_display = display_name
    if canonical_normalized != normalized:
        canonical_display = canonical_normalized.title()

    tag = ConceptTag(
        name=canonical_display,
        normalized_name=canonical_normalized,
        definition=definition.strip() or f"Concept from {subject}: {canonical_display}.",
        subject=subject.strip(),
        status=status,
    )
    db.add(tag)
    db.flush()

    if normalized != canonical_normalized:
        add_alias(db, tag, display_name)
    for alias_name in _KNOWN_ALIAS_FAMILIES.get(canonical_normalized, set()):
        add_alias(db, tag, alias_name)

    return tag, "created"


def link_document_evidence(
    db: Session,
    *,
    document_id: int,
    tag_id: int,
    chunk_index: int,
    source_excerpt: str,
    confidence: float = 1.0,
) -> DocumentTagEvidence:
    existing = (
        db.query(DocumentTagEvidence)
        .filter(
            DocumentTagEvidence.document_id == document_id,
            DocumentTagEvidence.tag_id == tag_id,
            DocumentTagEvidence.chunk_index == chunk_index,
        )
        .first()
    )
    if existing:
        return existing

    evidence = DocumentTagEvidence(
        document_id=document_id,
        tag_id=tag_id,
        chunk_index=chunk_index,
        source_excerpt=source_excerpt.strip()[:2000],
        confidence=max(0.0, min(confidence, 1.0)),
    )
    db.add(evidence)
    db.flush()
    return evidence


def consolidate_known_alias_families(db: Session) -> int:
    """Renames or merges existing tags that map to a known canonical family."""
    changed = 0
    for tag in list(db.query(ConceptTag).all()):
        canonical = _canonical_alias_name(tag.name)
        if canonical == tag.normalized_name:
            for alias_name in _KNOWN_ALIAS_FAMILIES.get(canonical, set()):
                add_alias(db, tag, alias_name)
            continue

        target = (
            db.query(ConceptTag)
            .filter(
                ConceptTag.subject == tag.subject,
                ConceptTag.normalized_name == canonical,
                ConceptTag.id != tag.id,
            )
            .first()
        )
        old_name = tag.name
        if target is None:
            tag.name = canonical.title()
            tag.normalized_name = canonical
            db.flush()
            add_alias(db, tag, old_name)
            for alias_name in _KNOWN_ALIAS_FAMILIES.get(canonical, set()):
                add_alias(db, tag, alias_name)
        else:
            from core.models import Question

            db.query(Question).filter(Question.tag_id == tag.id).update(
                {Question.tag_id: target.id}, synchronize_session=False
            )
            for evidence in list(tag.evidence):
                duplicate = (
                    db.query(DocumentTagEvidence)
                    .filter(
                        DocumentTagEvidence.document_id == evidence.document_id,
                        DocumentTagEvidence.tag_id == target.id,
                        DocumentTagEvidence.chunk_index == evidence.chunk_index,
                    )
                    .first()
                )
                if duplicate:
                    db.delete(evidence)
                else:
                    evidence.tag_id = target.id
            add_alias(db, target, old_name)
            for alias in list(tag.aliases):
                add_alias(db, target, alias.alias)
            db.delete(tag)
        changed += 1
    db.flush()
    return changed
