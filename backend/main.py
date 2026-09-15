from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import auth, diagnostics, ingestion, questions, quiz, tags
from core.database import Base, engine
from core import models

# In production, use Alembic migrations instead of create_all — this is
# here so `uvicorn app.main:app` works against a fresh database out of
# the box. See app/db/init_db.sql for the equivalent as raw SQL.
Base.metadata.create_all(bind=engine)

# Preserve existing local SQLite data while introducing canonical tag IDs.
from services.schema_migrations import backfill_existing_question_tags, ensure_question_tag_column

ensure_question_tag_column(engine)
backfill_existing_question_tags()

app = FastAPI(title="CogniTree API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],  # Vite / Next.js dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(ingestion.router)
app.include_router(questions.router)
app.include_router(quiz.router)
app.include_router(diagnostics.router)
app.include_router(tags.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/health/llm")
def llm_health_check():
    """Performs a live provider check without exposing the API key."""
    from services.question_factory import verify_gemini_connection

    return verify_gemini_connection()
