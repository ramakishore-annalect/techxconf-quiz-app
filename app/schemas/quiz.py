"""Quiz and session schemas."""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models import Difficulty, SessionStatus


class QuizListItem(BaseModel):
    """Quiz list item schema."""

    id: str  # We'll use topic as ID for now
    title: str
    description: Optional[str] = None
    total_questions: int
    topics: List[str]
    difficulties: List[str]
    estimated_time_minutes: int

    model_config = {"from_attributes": True}


class QuizDetail(BaseModel):
    """Quiz detail schema."""

    id: str
    title: str
    description: Optional[str] = None
    total_questions: int
    topics: List[str]
    difficulties: List[str]
    estimated_time_minutes: int
    question_breakdown: Dict[str, int]  # difficulty -> count
    topic_breakdown: Dict[str, int]  # topic -> count

    model_config = {"from_attributes": True}


class QuizStartRequest(BaseModel):
    """Start quiz request schema."""

    num_questions: int = Field(ge=1, le=100, description="Number of questions (1-100)")
    difficulty_mix: Optional[Dict[str, int]] = Field(
        None,
        description="Difficulty distribution (e.g., {'easy': 6, 'medium': 3, 'hard': 1})",
    )
    topics: Optional[List[str]] = Field(None, description="Filter by topics")
    seed: Optional[int] = Field(None, description="Seed for reproducible randomization")
    participant_name: str = Field(
        ..., min_length=1, max_length=100, description="Participant's full name"
    )
    participant_mobile: str = Field(
        ..., min_length=10, max_length=15, description="Participant's mobile number"
    )

    @field_validator("participant_mobile")
    @classmethod
    def validate_mobile(cls, v):
        """Validate mobile number."""
        # Remove spaces and dashes
        cleaned = v.replace(" ", "").replace("-", "")
        if not cleaned.isdigit():
            raise ValueError("Mobile number must contain only digits")
        if len(cleaned) != 10:
            raise ValueError("Mobile number must be exactly 10 digits")
        return cleaned

    @field_validator("difficulty_mix", mode="before")
    @classmethod
    def validate_difficulty_mix(cls, v, info):
        """Validate difficulty mix."""
        if v is None:
            return v

        if not isinstance(v, dict):
            raise ValueError("difficulty_mix must be a dictionary")

        valid_difficulties = {"easy", "medium", "hard"}
        for difficulty in v.keys():
            if difficulty not in valid_difficulties:
                raise ValueError(
                    f"Invalid difficulty '{difficulty}'. Must be one of {valid_difficulties}"
                )

        total_requested = sum(v.values())
        num_questions = info.data.get("num_questions", 0) if info.data else 0

        if total_requested != num_questions:
            raise ValueError(
                f"Sum of difficulty_mix values ({total_requested}) must equal num_questions ({num_questions})"
            )

        return v

    @field_validator("topics")
    @classmethod
    def validate_topics(cls, v):
        """Validate topics list."""
        if v is not None:
            # Remove duplicates while preserving order
            v = list(dict.fromkeys(v))
            # Filter out empty strings
            v = [topic.strip() for topic in v if topic and topic.strip()]
            return v if v else None
        return v


class QuizStartResponse(BaseModel):
    """Start quiz response schema."""

    session_id: UUID
    started_at: datetime
    expires_at: datetime
    questions_count: int
    first_question_index: int = 0
    topics: List[str]
    difficulty_distribution: Dict[str, int]
    seed: Optional[int] = None

    model_config = {"from_attributes": True}


class QuestionResponse(BaseModel):
    """Question response schema (without correct answer)."""

    index: int
    question_id: UUID
    question_text: str
    options: Dict[str, str]  # {"A": "option_text", ...}
    topic: str
    difficulty: str
    time_limit_seconds: int = 15  # Each question has 15 seconds

    model_config = {"from_attributes": True}


class SubmitAnswerRequest(BaseModel):
    """Submit answer request schema."""

    question_id: UUID
    selected_option: str = Field(
        pattern="^[ABCD]$", description="Selected option (A, B, C, or D)"
    )
    time_taken_ms: int = Field(ge=0, description="Time taken in milliseconds")

    @field_validator("selected_option")
    @classmethod
    def validate_selected_option(cls, v):
        """Validate selected option."""
        return v.upper()


class SubmitAnswerResponse(BaseModel):
    """Submit answer response schema."""

    question_id: UUID
    is_correct: bool
    current_score: int
    total_answered: int

    model_config = {"from_attributes": True}


class SessionResultItem(BaseModel):
    """Individual question result."""

    question_id: UUID
    question_text: str
    selected_option: Optional[str] = None  # None if question was skipped
    correct_option: str
    is_correct: bool
    explanation: Optional[str] = None
    time_taken_ms: int
    topic: str
    difficulty: str

    model_config = {"from_attributes": True}


class SessionResults(BaseModel):
    """Complete session results."""

    session_id: UUID
    score: int
    total_questions: int
    percentage: float
    time_taken_seconds: int
    started_at: datetime
    finished_at: datetime
    results: List[SessionResultItem]
    performance_by_topic: Dict[
        str, Dict[str, int]
    ]  # topic -> {correct: int, total: int}
    performance_by_difficulty: Dict[
        str, Dict[str, int]
    ]  # difficulty -> {correct: int, total: int}

    model_config = {"from_attributes": True}


class LeaderboardEntry(BaseModel):
    """Leaderboard entry schema."""

    rank: int
    display_name: str
    participant_mobile: Optional[str] = None
    score: int
    total_questions: int
    percentage: int
    time_taken_seconds: int
    created_at: datetime
    is_current_user: bool = False

    model_config = {"from_attributes": True}


class LeaderboardResponse(BaseModel):
    """Leaderboard response schema."""

    entries: List[LeaderboardEntry]
    total_entries: int
    current_user_rank: Optional[int] = None
    filters: Dict[str, Optional[str]]  # Applied filters

    model_config = {"from_attributes": True}


class SessionStatusResponse(BaseModel):
    """Session status response schema."""

    session_id: UUID
    status: SessionStatus
    current_question_index: int
    total_questions: int
    score: int
    started_at: datetime
    expires_at: datetime
    time_remaining_seconds: int
    progress_percentage: float

    model_config = {"from_attributes": True}
