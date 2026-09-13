import enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from core.database import Base


class SkillType(str, enum.Enum):
    MEMORIZATION = "memorization"
    APPLICATION = "application"


class DocumentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    quiz_sessions = relationship("QuizSession", back_populates="user")


class SourceDocument(Base):
    __tablename__ = "source_documents"

    id = Column(Integer, primary_key=True)
    filename = Column(String(512), nullable=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.PENDING, nullable=False)
    chunk_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    questions = relationship("Question", back_populates="source_document")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    topic = Column(String(255), nullable=False, index=True)
    subtopic = Column(String(255), nullable=False, index=True)
    skill_type = Column(Enum(SkillType), nullable=False, index=True)

    question_text = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)  # list[str], length 4
    answer_index = Column(Integer, nullable=False)  # 0-3
    explanation = Column(Text, nullable=False)

    source_document_id = Column(Integer, ForeignKey("source_documents.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    source_document = relationship("SourceDocument", back_populates="questions")
    responses = relationship("Response", back_populates="question")


class QuizSession(Base):
    __tablename__ = "quiz_sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_adaptive = Column(Boolean, default=False, nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="quiz_sessions")
    responses = relationship("Response", back_populates="session")


class Response(Base):
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("quiz_sessions.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    selected_index = Column(Integer, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    response_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("QuizSession", back_populates="responses")
    question = relationship("Question", back_populates="responses")
