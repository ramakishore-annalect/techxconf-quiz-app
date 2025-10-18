"""Question and Answer models."""

import enum
from sqlalchemy import Column, String, Text, Integer, ForeignKey, Enum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Difficulty(str, enum.Enum):
    """Question difficulty levels."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class CorrectOption(str, enum.Enum):
    """Correct answer options."""

    A = "A"
    B = "B"
    C = "C"
    D = "D"


class Question(BaseModel):
    """Question model."""

    __tablename__ = "questions"

    # Question content
    original_xls_id = Column(Integer, nullable=True, index=True)  # Original ID from XLS
    topic = Column(String(100), nullable=False, index=True)
    difficulty = Column(Enum(Difficulty), nullable=False, index=True)
    question_text = Column(Text, nullable=False)

    # Multiple choice options
    option_a = Column(Text, nullable=False)
    option_b = Column(Text, nullable=False)
    option_c = Column(Text, nullable=False)
    option_d = Column(Text, nullable=False)

    # Metadata
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Relationships
    created_by_user = relationship("User", back_populates="created_questions")
    answer = relationship("Answer", back_populates="question", uselist=False, cascade="all, delete-orphan")
    session_answers = relationship("SessionAnswer", back_populates="question", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Question(id={self.id}, topic={self.topic}, difficulty={self.difficulty})>"

    def get_options_dict(self) -> dict:
        """Get options as a dictionary."""
        return {
            "A": self.option_a,
            "B": self.option_b,
            "C": self.option_c,
            "D": self.option_d,
        }

    def get_option_by_letter(self, letter: str) -> str:
        """Get option text by letter."""
        options = self.get_options_dict()
        return options.get(letter.upper(), "")

    # Indexes
    __table_args__ = (
        Index("idx_questions_topic_difficulty", "topic", "difficulty"),
        Index("idx_questions_created_at", "created_at"),
    )


class Answer(BaseModel):
    """Answer model."""

    __tablename__ = "answers"

    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False, unique=True)
    correct_option = Column(Enum(CorrectOption), nullable=False)
    correct_text = Column(Text, nullable=False)  # The actual text of the correct answer
    explanation = Column(Text, nullable=True)  # Short explanation

    # Relationships
    question = relationship("Question", back_populates="answer")

    def __repr__(self) -> str:
        return f"<Answer(question_id={self.question_id}, correct_option={self.correct_option})>"

    def is_correct_option(self, selected_option: str) -> bool:
        """Check if the selected option is correct."""
        return selected_option.upper() == self.correct_option.value