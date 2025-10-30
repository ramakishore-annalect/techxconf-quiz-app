"""Quiz service."""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from uuid import UUID, uuid4

from sqlalchemy import func, select, distinct
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.models import (
    Question,
    Answer,
    QuizSession,
    SessionAnswer,
    Leaderboard,
    SessionStatus,
    Difficulty,
    User,
)
from app.schemas.quiz import (
    QuizStartRequest,
    QuizStartResponse,
    QuizListItem,
    QuizDetail,
    QuestionResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
    SessionResults,
    SessionResultItem,
    LeaderboardResponse,
    LeaderboardEntry,
)


class QuizService:
    """Quiz service for managing quizzes and sessions."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_quiz_list(
        self,
        topic: Optional[str] = None,
        difficulty: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[QuizListItem]:
        """Get list of available quizzes."""
        # For now, we'll create dynamic quizzes based on available topics
        query = select(
            Question.topic,
            func.count(Question.id).label("question_count"),
            func.array_agg(distinct(Question.difficulty)).label("difficulties"),
        ).group_by(Question.topic)

        if topic:
            query = query.where(Question.topic.ilike(f"%{topic}%"))

        if difficulty:
            try:
                diff_enum = Difficulty(difficulty.lower())
                query = query.where(Question.difficulty == diff_enum)
            except ValueError:
                pass  # Invalid difficulty, ignore filter

        query = query.limit(limit).offset(offset)
        result = await self.db.execute(query)
        topic_data = result.fetchall()

        quiz_list = []
        for topic_name, count, difficulties in topic_data:
            # Estimate time based on question count (1.5 minutes per question)
            estimated_time = max(5, int(count * 1.5))

            quiz_list.append(
                QuizListItem(
                    id=topic_name.lower().replace(" ", "_"),
                    title=f"{topic_name} Quiz",
                    description=f"Test your knowledge of {topic_name}",
                    total_questions=count,
                    topics=[topic_name],
                    difficulties=[d.value for d in difficulties if d],
                    estimated_time_minutes=estimated_time,
                )
            )

        return quiz_list

    async def get_quiz_detail(self, quiz_id: str) -> Optional[QuizDetail]:
        """Get quiz details."""
        # Extract topic from quiz_id (reverse of the ID creation logic)
        # Don't use .title() as topics might be uppercase like "AWS"
        topic_search = quiz_id.replace("_", " ")

        # Get question statistics for this topic
        query = (
            select(
                func.count(Question.id).label("total"),
                Question.difficulty,
                func.count(Question.id).label("count"),
            )
            .where(Question.topic.ilike(f"%{topic_search}%"))
            .group_by(Question.difficulty)
        )

        result = await self.db.execute(query)
        difficulty_stats = result.fetchall()

        if not difficulty_stats:
            return None

        total_questions = sum(stat.count for stat in difficulty_stats)
        question_breakdown = {}
        difficulties = []

        for stat in difficulty_stats:
            if stat.difficulty:
                question_breakdown[stat.difficulty.value] = stat.count
                difficulties.append(stat.difficulty.value)

        # Get topics for this quiz (in case there are variations)
        topic_query = select(distinct(Question.topic)).where(
            Question.topic.ilike(f"%{topic_search}%")
        )
        topic_result = await self.db.execute(topic_query)
        topics = [row[0] for row in topic_result.fetchall()]

        if not topics:
            return None

        # Use the actual topic name from database (preserves case like "AWS")
        actual_topic_name = topics[0]
        estimated_time = max(5, int(total_questions * 1.5))

        return QuizDetail(
            id=quiz_id,
            title=f"{actual_topic_name} Quiz",
            description=f"Comprehensive quiz covering {actual_topic_name} topics",
            total_questions=total_questions,
            topics=topics,
            difficulties=difficulties,
            estimated_time_minutes=estimated_time,
            question_breakdown=question_breakdown,
            topic_breakdown={topic: total_questions for topic in topics},
        )

    async def start_quiz(
        self, quiz_id: str, request: QuizStartRequest, user_id: Optional[UUID] = None
    ) -> QuizStartResponse:
        """Start a new quiz session."""
        # Check if this mobile number has already taken a quiz (completed session)
        existing_query = select(QuizSession).where(
            QuizSession.participant_mobile == request.participant_mobile,
            QuizSession.status == SessionStatus.FINISHED,
        )
        result = await self.db.execute(existing_query)
        existing_session = result.scalar_one_or_none()

        if existing_session:
            raise ValueError(
                f"This mobile number has already taken a quiz. "
                f"Each participant can only take the quiz once."
            )

        # Get available questions based on request criteria
        questions = await self._get_questions_for_quiz(quiz_id, request)

        if len(questions) < request.num_questions:
            raise ValueError(
                f"Not enough questions available. Requested: {request.num_questions}, "
                f"Available: {len(questions)}"
            )

        # Select and randomize questions
        selected_questions = await self._select_and_randomize_questions(
            questions, request.num_questions, request.difficulty_mix, request.seed
        )

        # Create quiz session with participant information
        session = await self._create_quiz_session(
            selected_questions,
            user_id,
            request.seed,
            request.participant_name,
            request.participant_mobile,
        )

        # Get topics and difficulty distribution
        topics = list(set(q.topic for q in selected_questions))
        difficulty_dist = {}
        for q in selected_questions:
            diff = q.difficulty.value
            difficulty_dist[diff] = difficulty_dist.get(diff, 0) + 1

        return QuizStartResponse(
            session_id=session.id,
            started_at=session.started_at,
            expires_at=session.expires_at,
            questions_count=len(selected_questions),
            first_question_index=0,
            topics=topics,
            difficulty_distribution=difficulty_dist,
            seed=request.seed,
        )

    async def get_session_question(
        self, session_id: UUID, question_index: int, user_id: Optional[UUID] = None
    ) -> Optional[QuestionResponse]:
        """Get a question from the session."""
        session = await self._get_session(session_id, user_id)
        if not session or not session.is_active:
            return None

        question_ids = session.get_question_ids()
        if question_index < 0 or question_index >= len(question_ids):
            return None

        question_id = UUID(question_ids[question_index])

        # Get question from database
        query = select(Question).where(Question.id == question_id)
        result = await self.db.execute(query)
        question = result.scalar_one_or_none()

        if not question:
            return None

        return QuestionResponse(
            index=question_index,
            question_id=question.id,
            question_text=question.question_text,
            options=question.get_options_dict(),
            topic=question.topic,
            difficulty=question.difficulty.value,
            time_limit_seconds=settings.QUESTION_TIME_LIMIT_SECONDS,
        )

    async def submit_answer(
        self,
        session_id: UUID,
        answer_request: SubmitAnswerRequest,
        user_id: Optional[UUID] = None,
    ) -> Optional[SubmitAnswerResponse]:
        """Submit an answer for a question in the session."""
        session = await self._get_session(session_id, user_id)
        if not session or not session.is_active:
            return None

        # Check if answer already exists for this question
        existing_answer = await self.db.execute(
            select(SessionAnswer).where(
                SessionAnswer.session_id == session_id,
                SessionAnswer.question_id == answer_request.question_id,
            )
        )
        if existing_answer.scalar_one_or_none():
            raise ValueError("Answer already submitted for this question")

        # Get question and correct answer
        query = (
            select(Question)
            .options(selectinload(Question.answer))
            .where(Question.id == answer_request.question_id)
        )
        result = await self.db.execute(query)
        question = result.scalar_one_or_none()

        if not question or not question.answer:
            raise ValueError("Question not found or has no answer")

        # Check if answer is correct
        is_correct = question.answer.is_correct_option(answer_request.selected_option)

        # Create session answer
        session_answer = SessionAnswer(
            session_id=session_id,
            question_id=answer_request.question_id,
            selected_option=answer_request.selected_option,
            is_correct=is_correct,
            time_taken_ms=answer_request.time_taken_ms,
        )

        self.db.add(session_answer)

        # Update session score
        if is_correct:
            session.score += 1

        await self.db.commit()

        # Get total answered questions
        total_answered_query = select(func.count(SessionAnswer.id)).where(
            SessionAnswer.session_id == session_id
        )
        total_answered_result = await self.db.execute(total_answered_query)
        total_answered = total_answered_result.scalar()

        return SubmitAnswerResponse(
            question_id=answer_request.question_id,
            is_correct=is_correct,
            current_score=session.score,
            total_answered=total_answered,
        )

    async def finish_session(
        self, session_id: UUID, user_id: Optional[UUID] = None
    ) -> Optional[SessionResults]:
        """Finish a quiz session and return results."""
        session = await self._get_session_with_answers(session_id, user_id)
        if not session:
            return None

        if session.status == SessionStatus.FINISHED:
            # Already finished, return existing results
            return await self._build_session_results(session)

        # Mark session as finished
        session.status = SessionStatus.FINISHED
        session.finished_at = datetime.utcnow()

        # Create leaderboard entry
        await self._create_leaderboard_entry(session)

        await self.db.commit()

        return await self._build_session_results(session)

    async def get_session_results(
        self, session_id: UUID, user_id: Optional[UUID] = None
    ) -> Optional[SessionResults]:
        """Get results for a completed session."""
        session = await self._get_session_with_answers(session_id, user_id)
        if not session or session.status != SessionStatus.FINISHED:
            return None

        return await self._build_session_results(session)

    async def get_leaderboard(
        self,
        topic: Optional[str] = None,
        limit: int = 50,
        user_id: Optional[UUID] = None,
    ) -> LeaderboardResponse:
        """Get leaderboard entries."""
        query = select(Leaderboard).order_by(
            Leaderboard.percentage.desc(),
            Leaderboard.score.desc(),
            Leaderboard.time_taken_seconds.asc(),
        )

        if topic:
            query = query.where(Leaderboard.topic.ilike(f"%{topic}%"))

        query = query.limit(limit)
        result = await self.db.execute(query)
        entries = result.scalars().all()

        # Build leaderboard response
        leaderboard_entries = []
        current_user_rank = None

        for i, entry in enumerate(entries, 1):
            is_current_user = entry.user_id == user_id if user_id else False
            if is_current_user:
                current_user_rank = i

            leaderboard_entries.append(
                LeaderboardEntry(
                    rank=i,
                    display_name=entry.display_name or "Anonymous",
                    participant_mobile=entry.participant_mobile,
                    score=entry.score,
                    total_questions=entry.total_questions,
                    percentage=entry.percentage,
                    time_taken_seconds=entry.time_taken_seconds,
                    created_at=entry.created_at,
                    is_current_user=is_current_user,
                )
            )

        return LeaderboardResponse(
            entries=leaderboard_entries,
            total_entries=len(entries),
            current_user_rank=current_user_rank,
            filters={"topic": topic},
        )

    # Private helper methods

    async def _get_questions_for_quiz(
        self, quiz_id: str, request: QuizStartRequest
    ) -> List[Question]:
        """Get questions available for the quiz."""
        # Extract topic from quiz_id (don't use .title() as topics might be uppercase)
        topic_search = quiz_id.replace("_", " ")

        query = select(Question).where(Question.topic.ilike(f"%{topic_search}%"))

        # Apply topic filter if specified in request
        if request.topics:
            topic_conditions = [
                Question.topic.ilike(f"%{topic}%") for topic in request.topics
            ]
            query = query.where(func.or_(*topic_conditions))

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def _select_and_randomize_questions(
        self,
        questions: List[Question],
        num_questions: int,
        difficulty_mix: Optional[Dict[str, int]],
        seed: Optional[int],
    ) -> List[Question]:
        """Select and randomize questions based on criteria."""
        if seed is not None:
            random.seed(seed)

        if difficulty_mix:
            # Select questions by difficulty
            selected = []
            questions_by_difficulty = {}

            # Group questions by difficulty
            for q in questions:
                diff = q.difficulty.value
                if diff not in questions_by_difficulty:
                    questions_by_difficulty[diff] = []
                questions_by_difficulty[diff].append(q)

            # Select required number from each difficulty
            for difficulty, count in difficulty_mix.items():
                available = questions_by_difficulty.get(difficulty, [])
                if len(available) < count:
                    raise ValueError(
                        f"Not enough {difficulty} questions available. "
                        f"Requested: {count}, Available: {len(available)}"
                    )
                selected.extend(random.sample(available, count))

            # Shuffle the final selection
            random.shuffle(selected)
            return selected
        else:
            # Random selection without difficulty constraints
            if len(questions) < num_questions:
                raise ValueError("Not enough questions available")

            selected = random.sample(questions, num_questions)
            random.shuffle(selected)
            return selected

    async def _create_quiz_session(
        self,
        questions: List[Question],
        user_id: Optional[UUID],
        seed: Optional[int],
        participant_name: Optional[str] = None,
        participant_mobile: Optional[str] = None,
    ) -> QuizSession:
        """Create a new quiz session."""
        # Set quiz expiration to 48 hours from now (reasonable completion time)
        expires_at = datetime.utcnow() + timedelta(hours=settings.SESSION_EXPIRE_HOURS)

        session = QuizSession(
            user_id=user_id,
            participant_name=participant_name,
            participant_mobile=participant_mobile,
            quiz_definition={
                "question_ids": [str(q.id) for q in questions],
                "seed": seed,
            },
            seed=seed,
            expires_at=expires_at,
            total_questions=len(questions),
        )

        self.db.add(session)
        await self.db.commit()
        await self.db.refresh(session)

        return session

    async def _get_session(
        self, session_id: UUID, user_id: Optional[UUID] = None
    ) -> Optional[QuizSession]:
        """Get quiz session by ID."""
        query = select(QuizSession).where(QuizSession.id == session_id)

        # If user_id is provided, ensure session belongs to user or is anonymous
        if user_id:
            query = query.where(
                (QuizSession.user_id == user_id) | (QuizSession.user_id.is_(None))
            )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _get_session_with_answers(
        self, session_id: UUID, user_id: Optional[UUID] = None
    ) -> Optional[QuizSession]:
        """Get quiz session with answers."""
        query = (
            select(QuizSession)
            .options(
                selectinload(QuizSession.session_answers)
                .selectinload(SessionAnswer.question)
                .selectinload(Question.answer)
            )
            .where(QuizSession.id == session_id)
        )

        if user_id:
            query = query.where(
                (QuizSession.user_id == user_id) | (QuizSession.user_id.is_(None))
            )

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _build_session_results(self, session: QuizSession) -> SessionResults:
        """Build session results from session data."""
        results = []
        performance_by_topic = {}
        performance_by_difficulty = {}

        # Get all question IDs from the session
        question_ids = [UUID(qid) for qid in session.get_question_ids()]

        # Get all questions for this session
        questions_query = (
            select(Question)
            .where(Question.id.in_(question_ids))
            .options(selectinload(Question.answer))
        )
        questions_result = await self.db.execute(questions_query)
        questions = {q.id: q for q in questions_result.scalars().all()}

        # Create a map of answered questions
        answered_questions = {
            answer.question_id: answer for answer in session.session_answers
        }

        # Process all questions in order
        for question_id in question_ids:
            question = questions.get(question_id)
            if not question:
                continue

            topic = question.topic
            difficulty = question.difficulty.value

            # Initialize topic/difficulty tracking
            if topic not in performance_by_topic:
                performance_by_topic[topic] = {"correct": 0, "total": 0}
            if difficulty not in performance_by_difficulty:
                performance_by_difficulty[difficulty] = {"correct": 0, "total": 0}

            # Update counters
            performance_by_topic[topic]["total"] += 1
            performance_by_difficulty[difficulty]["total"] += 1

            # Check if this question was answered
            session_answer = answered_questions.get(question_id)

            if session_answer:
                # Question was answered
                if session_answer.is_correct:
                    performance_by_topic[topic]["correct"] += 1
                    performance_by_difficulty[difficulty]["correct"] += 1

                selected_option = session_answer.selected_option
                is_correct = session_answer.is_correct
                time_taken_ms = session_answer.time_taken_ms
            else:
                # Question was skipped (not answered)
                selected_option = None
                is_correct = False
                time_taken_ms = 0

            # Get explanation
            explanation = None
            if question.answer:
                explanation = question.answer.explanation

            results.append(
                SessionResultItem(
                    question_id=question.id,
                    question_text=question.question_text,
                    selected_option=selected_option,
                    correct_option=(
                        question.answer.correct_option.value if question.answer else "?"
                    ),
                    is_correct=is_correct,
                    explanation=explanation,
                    time_taken_ms=time_taken_ms,
                    topic=topic,
                    difficulty=difficulty,
                )
            )

        # Calculate time taken
        time_taken_seconds = 0
        if session.started_at and session.finished_at:
            time_taken_seconds = int(
                (session.finished_at - session.started_at).total_seconds()
            )

        return SessionResults(
            session_id=session.id,
            score=session.score,
            total_questions=session.total_questions,
            percentage=session.percentage_score,
            time_taken_seconds=time_taken_seconds,
            started_at=session.started_at,
            finished_at=session.finished_at or datetime.utcnow(),
            results=results,
            performance_by_topic=performance_by_topic,
            performance_by_difficulty=performance_by_difficulty,
        )

    async def _create_leaderboard_entry(self, session: QuizSession) -> None:
        """Create leaderboard entry for completed session."""
        # Get display name - prioritize participant_name from session
        display_name = "Anonymous"
        if session.participant_name:
            display_name = session.participant_name
        elif session.user_id:
            user_query = select(User.display_name, User.email).where(
                User.id == session.user_id
            )
            user_result = await self.db.execute(user_query)
            user_data = user_result.first()
            if user_data:
                display_name = user_data.display_name or user_data.email.split("@")[0]

        # Calculate time taken
        time_taken = 0
        if session.started_at and session.finished_at:
            time_taken = int((session.finished_at - session.started_at).total_seconds())

        # Get primary topic (most common topic in the session)
        topics = await self._get_session_topics(session)
        primary_topic = topics[0] if topics else None

        leaderboard_entry = Leaderboard(
            user_id=session.user_id,
            session_id=session.id,
            display_name=display_name,
            participant_mobile=session.participant_mobile,  # Store mobile number
            score=session.score,
            total_questions=session.total_questions,
            percentage=int(session.percentage_score),
            time_taken_seconds=time_taken,
            topic=primary_topic,
        )

        self.db.add(leaderboard_entry)

    async def _get_session_topics(self, session: QuizSession) -> List[str]:
        """Get topics for a session."""
        question_ids = [UUID(qid) for qid in session.get_question_ids()]
        query = select(distinct(Question.topic)).where(Question.id.in_(question_ids))
        result = await self.db.execute(query)
        return [row[0] for row in result.fetchall()]
