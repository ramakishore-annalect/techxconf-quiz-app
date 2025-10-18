import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Question, QuizSession } from '@/types';
import { apiService } from '@/services/api';
import { Button } from '@/components/ui/Button';

const QuizPage: React.FC = () => {
  const { sessionId } = useParams<{ quizId: string; sessionId: string }>();
  const navigate = useNavigate();

  const [session, setSession] = useState<QuizSession | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState<number>(0);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [questionStartTime, setQuestionStartTime] = useState<number>(0);
  const [timeRemaining, setTimeRemaining] = useState<number>(0);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (sessionId) {
      loadSessionAndQuestion();
    }
  }, [sessionId]);

  // Per-question timer countdown effect
  useEffect(() => {
    if (!currentQuestion || loading || questionStartTime === 0) return;

    const questionTimeLimit = (currentQuestion.time_limit_seconds || 15) * 1000;

    console.log('Starting question timer:', {
      questionIndex: currentQuestionIndex,
      timeLimit: questionTimeLimit,
      startTime: questionStartTime
    });

    const timer = setInterval(() => {
      const elapsed = Date.now() - questionStartTime;
      const remaining = Math.max(0, questionTimeLimit - elapsed);
      setTimeRemaining(remaining);

      if (remaining <= 0) {
        clearInterval(timer);
        handleQuestionTimeExpired();
      }
    }, 1000);

    return () => clearInterval(timer);
  }, [currentQuestion, questionStartTime, loading]);

  const handleQuestionTimeExpired = async () => {
    if (!sessionId || submitting) return;

    console.log('Question time expired, moving to next question');

    // If no answer selected, skip this question (no score)
    if (!selectedAnswer) {
      await moveToNextQuestion();
    } else {
      // Submit the selected answer
      await handleSubmitAnswer();
    }
  };

  const loadSessionAndQuestion = async () => {
    if (!sessionId) return;

    try {
      setLoading(true);
      // Load session from sessionStorage
      const sessionData = sessionStorage.getItem(`quiz_session_${sessionId}`);
      if (!sessionData) {
        setError('Session not found. Please start the quiz again.');
        return;
      }

      const parsedSession: QuizSession = JSON.parse(sessionData);
      setSession(parsedSession);

      console.log('Session loaded:', parsedSession);

      // Load the first question (index 0)
      await loadQuestion(0);
    } catch (err) {
      setError('Failed to load quiz session');
      console.error('Error loading session:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadQuestion = async (questionIndex: number) => {
    if (!sessionId) return;

    try {
      console.log(`Loading question ${questionIndex} for session ${sessionId}`);
      const question = await apiService.getQuestion(sessionId, questionIndex);
      console.log('Question loaded successfully:', question);
      setCurrentQuestion(question);
      setCurrentQuestionIndex(questionIndex);
      setSelectedAnswer(null);

      // Start the timer for this question
      setQuestionStartTime(Date.now());
      const timeLimit = (question.time_limit_seconds || 15) * 1000;
      setTimeRemaining(timeLimit);
    } catch (err: any) {
      console.error('Error fetching question:', err);
      console.error('Error details:', {
        status: err?.response?.status,
        data: err?.response?.data,
        message: err?.message
      });
      // If 404, quiz is complete or session expired
      navigate(`/results/${sessionId}`);
    }
  };

  const moveToNextQuestion = async () => {
    if (!session || !sessionId) return;

    const nextIndex = currentQuestionIndex + 1;
    if (nextIndex < session.questions_count) {
      // Load next question
      await loadQuestion(nextIndex);
    } else {
      // Quiz completed, finish session
      try {
        await apiService.finishSession(sessionId);
        navigate(`/results/${sessionId}`);
      } catch (err) {
        console.error('Error finishing session:', err);
        navigate(`/results/${sessionId}`);
      }
    }
  };

  const handleSubmitAnswer = useCallback(async () => {
    if (!sessionId || !currentQuestion || !selectedAnswer || submitting) return;

    try {
      setSubmitting(true);
      const timeTaken = Date.now() - questionStartTime;

      await apiService.submitAnswer(sessionId, {
        question_id: currentQuestion.question_id,
        selected_option: selectedAnswer,
        time_taken_ms: timeTaken,
      });

      // Move to next question
      await moveToNextQuestion();
    } catch (err) {
      console.error('Error submitting answer:', err);
      setError('Failed to submit answer. Please try again.');
    } finally {
      setSubmitting(false);
    }
  }, [sessionId, currentQuestion, selectedAnswer, submitting, questionStartTime]);

  const getProgressPercentage = (): number => {
    if (!session || !session.questions_count) return 0;
    return Math.round(((currentQuestionIndex + 1) / session.questions_count) * 100);
  };

  const formatTime = (milliseconds: number): string => {
    const totalSeconds = Math.floor(milliseconds / 1000);
    const seconds = totalSeconds % 60;
    return `${seconds}s`;
  };

  const getTimeColor = (): string => {
    const timeInSeconds = timeRemaining / 1000;
    if (timeInSeconds < 5) return 'text-red-600';
    if (timeInSeconds < 10) return 'text-orange-600';
    return 'text-gray-900';
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-center items-center min-h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  if (error || !session || !currentQuestion) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Quiz Error</h1>
          <p className="text-red-600 mb-6">{error || 'Failed to load quiz'}</p>
          <Button onClick={() => navigate('/quizzes')}>
            Back to Quizzes
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header with progress and timer */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-2xl font-bold text-gray-900">
            Quiz: {session.topics.join(', ')}
          </h1>
          <div className={`text-2xl font-mono font-bold ${getTimeColor()}`}>
            ⏱️ {formatTime(timeRemaining)}
          </div>
        </div>

        {/* Time warning */}
        {timeRemaining < 5000 && timeRemaining > 0 && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm text-red-700">
              <strong>⚠️ Warning:</strong> Less than 5 seconds remaining! The question will auto-advance when time runs out.
            </p>
          </div>
        )}

        {/* Progress bar */}
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${getProgressPercentage()}%` }}
          ></div>
        </div>
        <p className="text-sm text-gray-600 mt-2">
          Question {currentQuestionIndex + 1} of {session.questions_count}
        </p>
      </div>

      {/* Question */}
      <div className="card mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">
          {currentQuestion.question_text}
        </h2>

        {/* Answer options */}
        <div className="space-y-3">
          {currentQuestion.options && Object.entries(currentQuestion.options).map(([key, value]) => (
            <label
              key={key}
              className={`flex items-center p-4 border rounded-lg cursor-pointer transition-colors ${selectedAnswer === key
                ? 'border-blue-600 bg-blue-50'
                : 'border-gray-300 hover:border-gray-400'
                }`}
            >
              <input
                type="radio"
                name="answer"
                value={key}
                checked={selectedAnswer === key}
                onChange={(e) => setSelectedAnswer(e.target.value)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
              />
              <span className="ml-3 text-gray-900">{value}</span>
            </label>
          ))}
        </div>

        {/* Submit button */}
        <div className="mt-8 flex justify-end">
          <Button
            variant="primary"
            onClick={handleSubmitAnswer}
            loading={submitting}
            disabled={!selectedAnswer || submitting}
          >
            {submitting ? 'Submitting...' : 'Submit Answer'}
          </Button>
        </div>
      </div>

      {/* Quiz info */}
      <div className="text-center text-gray-500 text-sm">
        <p>
          Each question has 15 seconds. Answer within the time limit or it will auto-advance.
        </p>
        <p className="mt-1">
          Once you submit an answer, you cannot go back to previous questions.
        </p>
      </div>
    </div>
  );
};

export default QuizPage;