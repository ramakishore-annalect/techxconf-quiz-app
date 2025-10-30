"""Quiz session models."""

import enum
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    Boolean,
    DateTime,
    Enum,
    JSON,
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class SessionStatus(str, enum.Enum):
    """Quiz session status."""

    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    EXPIRED = "expired"
    ABANDONED = "abandoned"


class QuizSession(BaseModel):
    """Quiz session model."""

    __tablename__ = "quiz_sessions"

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )  # Nullable for anonymous users

    # Participant information (for non-logged-in users)
    participant_name = Column(String(100), nullable=True)
    participant_mobile = Column(String(15), nullable=True, index=True)

    # Session configuration
    quiz_definition = Column(JSON, nullable=False)  # List of question IDs and ordering
    seed = Column(Integer, nullable=True)  # For reproducible shuffles

    # Session lifecycle
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    finished_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=False)

    # Session state
    status = Column(
        Enum(SessionStatus), default=SessionStatus.IN_PROGRESS, nullable=False
    )
    current_question_index = Column(Integer, default=0, nullable=False)

    # Results
    score = Column(Integer, default=0, nullable=False)
    total_questions = Column(Integer, nullable=False)

    # Metadata
    session_metadata = Column(JSON, nullable=True)  # Additional session data

    # Relationships
    user = relationship("User", back_populates="quiz_sessions")
    session_answers = relationship(
        "SessionAnswer",
        back_populates="session",
        order_by="SessionAnswer.created_at",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return (
            f"<QuizSession(id={self.id}, user_id={self.user_id}, status={self.status})>"
        )

    @property
    def is_active(self) -> bool:
        """Check if session is active."""
        return (
            self.status == SessionStatus.IN_PROGRESS
            and datetime.utcnow() < self.expires_at
        )

    @property
    def is_finished(self) -> bool:
        """Check if session is finished."""
        return self.status == SessionStatus.FINISHED

    @property
    def is_expired(self) -> bool:
        """Check if session is expired."""
        return datetime.utcnow() >= self.expires_at

    @property
    def percentage_score(self) -> float:
        """Get percentage score."""
        if self.total_questions == 0:
            return 0.0
        return (self.score / self.total_questions) * 100

    def get_question_ids(self) -> List[str]:
        """Get list of question IDs for this session."""
        return self.quiz_definition.get("question_ids", [])

    def get_difficulty_mix(self) -> Dict[str, int]:
        """Get difficulty mix for this session."""
        return self.quiz_definition.get("difficulty_mix", {})

    # Indexes
    __table_args__ = (
        Index("idx_quiz_sessions_user_id", "user_id"),
        Index("idx_quiz_sessions_status", "status"),
        Index("idx_quiz_sessions_started_at", "started_at"),
        Index("idx_quiz_sessions_expires_at", "expires_at"),
    )


class SessionAnswer(BaseModel):
    """Session answer model - tracks user's answers to questions."""

    __tablename__ = "session_answers"

    session_id = Column(
        UUID(as_uuid=True), ForeignKey("quiz_sessions.id"), nullable=False
    )
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False)

    # Answer data
    selected_option = Column(String(1), nullable=False)  # A, B, C, or D
    is_correct = Column(Boolean, nullable=False)
    time_taken_ms = Column(Integer, nullable=False, default=0)

    # Relationships
    session = relationship("QuizSession", back_populates="session_answers")
    question = relationship("Question", back_populates="session_answers")

    def __repr__(self) -> str:
        return f"<SessionAnswer(session_id={self.session_id}, question_id={self.question_id}, correct={self.is_correct})>"

    # Indexes
    __table_args__ = (
        Index("idx_session_answers_session_id", "session_id"),
        Index("idx_session_answers_question_id", "question_id"),
        Index("idx_session_answers_created_at", "created_at"),
    )


class Leaderboard(BaseModel):
    """Leaderboard model - denormalized for fast reads."""

    __tablename__ = "leaderboard"

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )  # Nullable for anonymous
    session_id = Column(
        UUID(as_uuid=True), ForeignKey("quiz_sessions.id"), nullable=False
    )

    # Player info
    display_name = Column(String(100), nullable=True)
    participant_mobile = Column(
        String(15), nullable=True
    )  # Mobile number for anonymous participants

    # Performance metrics
    score = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    percentage = Column(Integer, nullable=False)  # Stored as integer (0-100)
    time_taken_seconds = Column(Integer, nullable=False)

    # Categorization
    topic = Column(String(100), nullable=True)  # If specific to a topic
    difficulty = Column(String(20), nullable=True)  # If specific to a difficulty

    # Relationships
    user = relationship("User")
    session = relationship("QuizSession")

    def __repr__(self) -> str:
        return f"<Leaderboard(user_id={self.user_id}, score={self.score}, percentage={self.percentage})>"

    # Indexes
    __table_args__ = (
        Index("idx_leaderboard_score", "score"),
        Index("idx_leaderboard_percentage", "percentage"),
        Index("idx_leaderboard_topic", "topic"),
        Index("idx_leaderboard_created_at", "created_at"),
        Index("idx_leaderboard_topic_score", "topic", "score"),
    )
