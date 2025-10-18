"""Quiz endpoints."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_optional_current_user
from app.services.quiz import QuizService
from app.schemas.quiz import (
    QuizListItem,
    QuizDetail,
    QuizStartRequest,
    QuizStartResponse,
    QuestionResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
    SessionResults,
    LeaderboardResponse,
)

router = APIRouter()


@router.get("/", response_model=List[QuizListItem])
async def get_quizzes(
    topic: Optional[str] = Query(None, description="Filter by topic"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty"),
    limit: int = Query(20, ge=1, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    db: AsyncSession = Depends(get_db),
):
    """Get list of available quizzes."""
    quiz_service = QuizService(db)
    return await quiz_service.get_quiz_list(topic, difficulty, limit, offset)


@router.get("/leaderboard", response_model=LeaderboardResponse)
async def get_leaderboard(
    topic: Optional[str] = Query(None, description="Filter by topic"),
    limit: int = Query(50, ge=1, le=100, description="Number of entries to return"),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_optional_current_user),
):
    """Get leaderboard entries."""
    quiz_service = QuizService(db)

    user_id = current_user.id if current_user else None
    return await quiz_service.get_leaderboard(topic, limit, user_id)


@router.get("/{quiz_id}", response_model=QuizDetail)
async def get_quiz_detail(quiz_id: str, db: AsyncSession = Depends(get_db)):
    """Get quiz details."""
    quiz_service = QuizService(db)
    quiz = await quiz_service.get_quiz_detail(quiz_id)

    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found"
        )

    return quiz


@router.post("/{quiz_id}/start", response_model=QuizStartResponse)
async def start_quiz(
    quiz_id: str,
    request: QuizStartRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_optional_current_user),
):
    """Start a quiz session."""
    quiz_service = QuizService(db)

    try:
        user_id = current_user.id if current_user else None
        return await quiz_service.start_quiz(quiz_id, request, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/sessions/{session_id}/question/{question_index}", response_model=QuestionResponse
)
async def get_session_question(
    session_id: UUID,
    question_index: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_optional_current_user),
):
    """Get a question from the session."""
    quiz_service = QuizService(db)

    user_id = current_user.id if current_user else None
    question = await quiz_service.get_session_question(
        session_id, question_index, user_id
    )

    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found or session expired",
        )

    return question


@router.post("/sessions/{session_id}/answer", response_model=SubmitAnswerResponse)
async def submit_answer(
    session_id: UUID,
    answer_request: SubmitAnswerRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_optional_current_user),
):
    """Submit an answer for a question."""
    quiz_service = QuizService(db)

    try:
        user_id = current_user.id if current_user else None
        response = await quiz_service.submit_answer(session_id, answer_request, user_id)

        if not response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or expired",
            )

        return response
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/sessions/{session_id}/finish", response_model=SessionResults)
async def finish_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_optional_current_user),
):
    """Finish a quiz session and get results."""
    quiz_service = QuizService(db)

    user_id = current_user.id if current_user else None
    results = await quiz_service.finish_session(session_id, user_id)

    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )

    return results


@router.get("/sessions/{session_id}/results", response_model=SessionResults)
async def get_session_results(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_optional_current_user),
):
    """Get results for a completed session."""
    quiz_service = QuizService(db)

    user_id = current_user.id if current_user else None
    results = await quiz_service.get_session_results(session_id, user_id)

    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session results not found"
        )

    return results
