"""Small idempotent schema migration for the local SQLite prototype.

Alembic should replace this when deployment environments are introduced. This
migration exists so current student data survives the canonical-tag upgrade.
"""

from sqlalchemy import inspect, text

from core.database import SessionLocal
from core.models import Question, TagStatus
from services.tag_service import consolidate_known_alias_families, resolve_canonical_tag


def ensure_question_tag_column(engine) -> None:
    inspector = inspect(engine)
    if "questions" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("questions")}
    if "tag_id" not in columns:
        with engine.begin() as connection:
            connection.execute(
                text("ALTER TABLE questions ADD COLUMN tag_id INTEGER REFERENCES concept_tags(id)")
            )
            connection.execute(
                text("CREATE INDEX IF NOT EXISTS ix_questions_tag_id ON questions (tag_id)")
            )


def backfill_existing_question_tags() -> int:
    db = SessionLocal()
    updated = 0
    try:
        questions = db.query(Question).filter(Question.tag_id.is_(None)).all()
        for question in questions:
            tag, _ = resolve_canonical_tag(
                db,
                name=question.subtopic,
                definition=f"Canonical concept migrated from the existing subtopic '{question.subtopic}'.",
                subject=question.topic,
                status=TagStatus.APPROVED,
            )
            question.tag_id = tag.id
            updated += 1
        consolidate_known_alias_families(db)
        db.commit()
        return updated
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
