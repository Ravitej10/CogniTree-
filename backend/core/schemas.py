from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field


# ---- Auth ----

class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str]

    class Config:
        from_attributes = True


# ---- Ingestion ----

class DocumentResponse(BaseModel):
    id: int
    filename: str
    status: str
    chunk_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# ---- Question generation (this is also the schema handed to the LLM
#      via `instructor` — see services/question_factory.py) ----

class GeneratedQuestion(BaseModel):
    """Strict schema the LLM must fill in. instructor validates the raw
    Gemini output against this and retries on validation failure, which is
    what prevents malformed distractors / missing fields from reaching the
    question bank."""

    question_text: str
    options: list[str] = Field(min_length=4, max_length=4)
    answer_index: int = Field(ge=0, le=3)
    explanation: str
    topic: str
    subtopic: str
    skill_type: Literal["memorization", "application"]


class QuestionResponse(BaseModel):
    id: int
    topic: str
    subtopic: str
    skill_type: str
    question_text: str
    options: list[str]
    # answer_index / explanation deliberately omitted from the quiz-taking
    # response — see schemas.QuestionWithAnswer for the review/explanation view.

    class Config:
        from_attributes = True


class QuestionWithAnswer(QuestionResponse):
    answer_index: int
    explanation: str


# ---- Quiz sessions ----

class StartQuizResponse(BaseModel):
    session_id: int
    questions: list[QuestionResponse]


class SubmitAnswerRequest(BaseModel):
    question_id: int
    selected_index: int = Field(ge=0, le=3)
    response_time_ms: Optional[int] = None


class SubmitAnswerResponse(BaseModel):
    is_correct: bool
    correct_index: int
    explanation: str


# ---- Diagnostics ----

class MatrixCell(BaseModel):
    topic: str
    subtopic: str
    skill_type: str
    correct: int
    attempted: int
    accuracy: float
    has_sufficient_evidence: bool
    is_gap: bool


class DiagnosticMatrixResponse(BaseModel):
    user_id: int
    threshold: float
    cells: list[MatrixCell]


class QuizReviewItem(BaseModel):
    question_id: int
    topic: str
    subtopic: str
    skill_type: str
    question_text: str
    options: list[str]
    selected_index: Optional[int]
    correct_index: int
    is_correct: bool
    explanation: str


class QuizCompletionResponse(BaseModel):
    session_id: int
    total_questions: int
    correct_count: int
    accuracy_percentage: int
    wrong_count: int
    reviews: list[QuizReviewItem]


class AdaptiveQuizResponse(BaseModel):
    session_id: int
    targeted_gaps: list[MatrixCell]
    questions: list[QuestionResponse]
