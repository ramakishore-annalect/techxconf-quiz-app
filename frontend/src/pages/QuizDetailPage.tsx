import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { QuizDetail } from '@/types';
import { apiService } from '@/services/api';
import { Button } from '@/components/ui/Button';

const QuizDetailPage: React.FC = () => {
  const { quizId } = useParams<{ quizId: string }>();
  const navigate = useNavigate();
  const [quiz, setQuiz] = useState<QuizDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [startingQuiz, setStartingQuiz] = useState(false);

  useEffect(() => {
    if (quizId) {
      fetchQuiz();
    }
  }, [quizId]);

  const fetchQuiz = async () => {
    if (!quizId) return;

    try {
      setLoading(true);
      const data = await apiService.getQuiz(quizId);
      setQuiz(data);
    } catch (err) {
      setError('Failed to load quiz details');
      console.error('Error fetching quiz:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleStartQuiz = async () => {
    if (!quiz) return;

    try {
      setStartingQuiz(true);
      const session = await apiService.startQuizSession(quiz.id);
      // Store session data in sessionStorage for QuizPage to access
      sessionStorage.setItem(`quiz_session_${session.session_id}`, JSON.stringify(session));
      navigate(`/quiz/${quiz.id}/session/${session.session_id}`);
    } catch (err) {
      console.error('Error starting quiz:', err);
      setStartingQuiz(false);
      // Handle error (could show toast notification)
    }
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

  if (error || !quiz) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Quiz Not Found</h1>
          <p className="text-red-600 mb-6">{error || 'The requested quiz could not be found.'}</p>
          <div className="space-x-4">
            <Button variant="secondary" onClick={() => navigate('/quizzes')}>
              Back to Quizzes
            </Button>
            {quizId && (
              <Button onClick={fetchQuiz}>
                Try Again
              </Button>
            )}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <Button
          variant="secondary"
          onClick={() => navigate('/quizzes')}
          className="mb-4"
        >
          ← Back to Quizzes
        </Button>

        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{quiz.title}</h1>
            <p className="text-lg text-gray-600">{quiz.topics.join(', ')}</p>
          </div>
          <span className="inline-flex px-3 py-1 text-sm font-semibold rounded-full bg-green-100 text-green-800">
            Active
          </span>
        </div>
      </div>

      {/* Main content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          {/* Description */}
          {quiz.description && (
            <div className="card mb-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Description</h2>
              <p className="text-gray-700 leading-relaxed">{quiz.description}</p>
            </div>
          )}

          {/* Quiz Information */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Quiz Information</h2>
            <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <dt className="text-sm font-medium text-gray-500">Number of Questions</dt>
                <dd className="mt-1 text-lg text-gray-900">{quiz.total_questions}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Estimated Time</dt>
                <dd className="mt-1 text-lg text-gray-900">{quiz.estimated_time_minutes} minutes</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Topics</dt>
                <dd className="mt-1 text-lg text-gray-900">{quiz.topics.join(', ')}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Difficulties</dt>
                <dd className="mt-1 text-lg text-gray-900 capitalize">{quiz.difficulties.join(', ')}</dd>
              </div>
            </dl>

            {/* Difficulty Breakdown */}
            {quiz.question_breakdown && Object.keys(quiz.question_breakdown).length > 0 && (
              <div className="mt-6 pt-6 border-t border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Question Breakdown</h3>
                <div className="grid grid-cols-3 gap-4">
                  {Object.entries(quiz.question_breakdown).map(([difficulty, count]) => (
                    <div key={difficulty} className="text-center p-3 bg-gray-50 rounded-lg">
                      <div className="text-2xl font-bold text-gray-900">{count}</div>
                      <div className="text-sm text-gray-600 capitalize">{difficulty}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Sidebar */}
        <div className="lg:col-span-1">
          <div className="card sticky top-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Ready to Start?</h3>

            <p className="text-gray-600 text-sm mb-6">
              Click the button below to start taking this quiz. You'll answer {quiz.total_questions} questions
              covering {quiz.topics.join(', ')}.
            </p>

            <Button
              variant="primary"
              size="lg"
              onClick={handleStartQuiz}
              loading={startingQuiz}
              className="w-full"
            >
              {startingQuiz ? 'Starting...' : 'Start Quiz'}
            </Button>

            <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-md">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg
                    className="h-5 w-5 text-blue-400"
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fillRule="evenodd"
                      d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                      clipRule="evenodd"
                    />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-blue-700">
                    Estimated time: <strong>{quiz.estimated_time_minutes} minutes</strong>
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuizDetailPage;