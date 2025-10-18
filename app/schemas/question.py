"""Question and import schemas."""

from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, field_validator

from app.models import Difficulty, CorrectOption


class QuestionCreate(BaseModel):
    """Question creation schema."""

    original_xls_id: Optional[int] = None
    topic: str
    difficulty: Difficulty
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str

    @field_validator("topic")
    @classmethod
    def validate_topic(cls, v):
        """Validate topic length."""
        if not v or not v.strip():
            raise ValueError("Topic cannot be empty")
        if len(v.strip()) > 100:
            raise ValueError("Topic must be 100 characters or less")
        return v.strip()

    @field_validator("question_text", "option_a", "option_b", "option_c", "option_d")
    @classmethod
    def validate_text_fields(cls, v):
        """Validate text fields are not empty."""
        if not v or not v.strip():
            raise ValueError("Text field cannot be empty")
        return v.strip()


class AnswerCreate(BaseModel):
    """Answer creation schema."""

    correct_option: CorrectOption
    correct_text: str
    explanation: Optional[str] = None

    @field_validator("correct_text")
    @classmethod
    def validate_correct_text(cls, v):
        """Validate correct text is not empty."""
        if not v or not v.strip():
            raise ValueError("Correct text cannot be empty")
        return v.strip()

    @field_validator("explanation")
    @classmethod
    def validate_explanation(cls, v):
        """Validate explanation if provided."""
        if v and not v.strip():
            return None
        return v.strip() if v else None


class QuestionWithAnswer(BaseModel):
    """Question with answer for import."""

    question: QuestionCreate
    answer: AnswerCreate

    def validate_answer_matches_option(self):
        """Validate that the correct option matches one of the question options."""
        question_options = {
            CorrectOption.A: self.question.option_a,
            CorrectOption.B: self.question.option_b,
            CorrectOption.C: self.question.option_c,
            CorrectOption.D: self.question.option_d,
        }

        expected_text = question_options[self.answer.correct_option]
        if self.answer.correct_text != expected_text:
            raise ValueError(
                f"Correct answer text '{self.answer.correct_text}' does not match "
                f"option {self.answer.correct_option.value}: '{expected_text}'"
            )


class QuestionResponse(BaseModel):
    """Question response schema (without answer)."""

    id: UUID
    original_xls_id: Optional[int]
    topic: str
    difficulty: Difficulty
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    created_at: str

    model_config = {"from_attributes": True}

    def get_options_dict(self) -> Dict[str, str]:
        """Get options as a dictionary."""
        return {
            "A": self.option_a,
            "B": self.option_b,
            "C": self.option_c,
            "D": self.option_d,
        }


class QuestionWithAnswerResponse(QuestionResponse):
    """Question response with answer (for admin)."""

    answer: Optional[Dict] = None

    model_config = {"from_attributes": True}


class ImportResult(BaseModel):
    """Excel import result schema."""

    total_rows: int
    processed_questions: int
    processed_answers: int
    created_questions: int
    updated_questions: int
    skipped_questions: int
    errors: List[Dict[str, str]]
    warnings: List[Dict[str, str]]


class ImportError(BaseModel):
    """Import error details."""

    row_number: int
    field: Optional[str] = None
    error_message: str
    row_data: Optional[Dict] = None


class ImportValidationResult(BaseModel):
    """Import validation result."""

    is_valid: bool
    questions_data: List[QuestionWithAnswer]
    errors: List[ImportError]
    warnings: List[ImportError]


class QuestionUpdate(BaseModel):
    """Question update schema."""

    topic: Optional[str] = None
    difficulty: Optional[Difficulty] = None
    question_text: Optional[str] = None
    option_a: Optional[str] = None
    option_b: Optional[str] = None
    option_c: Optional[str] = None
    option_d: Optional[str] = None

    @field_validator("topic")
    @classmethod
    def validate_topic(cls, v):
        """Validate topic if provided."""
        if v is not None:
            if not v.strip():
                raise ValueError("Topic cannot be empty")
            if len(v.strip()) > 100:
                raise ValueError("Topic must be 100 characters or less")
            return v.strip()
        return v

    @field_validator("question_text", "option_a", "option_b", "option_c", "option_d")
    @classmethod
    def validate_text_fields(cls, v):
        """Validate text fields if provided."""
        if v is not None:
            if not v.strip():
                raise ValueError("Text field cannot be empty")
            return v.strip()
        return v


class AnswerUpdate(BaseModel):
    """Answer update schema."""

    correct_option: Optional[CorrectOption] = None
    correct_text: Optional[str] = None
    explanation: Optional[str] = None

    @field_validator("correct_text")
    @classmethod
    def validate_correct_text(cls, v):
        """Validate correct text if provided."""
        if v is not None:
            if not v.strip():
                raise ValueError("Correct text cannot be empty")
            return v.strip()
        return v

    @field_validator("explanation")
    @classmethod
    def validate_explanation(cls, v):
        """Validate explanation if provided."""
        if v is not None and not v.strip():
            return None
        return v.strip() if v else None