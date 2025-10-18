import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { SessionResults } from '@/types';
import { apiService } from '@/services/api';
import { Button } from '@/components/ui/Button';

const ResultsPage: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const navigate = useNavigate();
  const [results, setResults] = useState<SessionResults | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (sessionId) {
      fetchResults();
    }
  }, [sessionId]);

  const fetchResults = async () => {
    if (!sessionId) return;

    try {
      setLoading(true);
      const data = await apiService.getSessionResults(sessionId);
      setResults(data);
    } catch (err) {
      setError('Failed to load quiz results');
      console.error('Error fetching results:', err);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (percentage: number): string => {
    if (percentage >= 80) return 'text-green-600';
    if (percentage >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreMessage = (percentage: number): string => {
    if (percentage >= 90) return 'Excellent work!';
    if (percentage >= 80) return 'Great job!';
    if (percentage >= 70) return 'Good effort!';
    if (percentage >= 60) return 'Not bad, keep practicing!';
    return 'Keep studying and try again!';
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

  if (error || !results) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Results Not Found</h1>
          <p className="text-red-600 mb-6">{error || 'Quiz results could not be loaded.'}</p>
          <Button onClick={() => navigate('/quizzes')}>
            Back to Quizzes
          </Button>
        </div>
      </div>
    );
  }

  const scorePercentage = Math.round((results.score / results.total_questions) * 100);

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Quiz Results</h1>
        <p className="text-lg text-gray-600">Session: {results.session_id}</p>
      </div>

      {/* Score Summary */}
      <div className="card mb-8 text-center">
        <div className="mb-6">
          <div className={`text-6xl font-bold mb-2 ${getScoreColor(scorePercentage)}`}>
            {scorePercentage}%
          </div>
          <p className="text-xl text-gray-700 mb-4">{getScoreMessage(scorePercentage)}</p>
          <p className="text-gray-600">
            You answered {results.score} out of {results.total_questions} questions correctly
          </p>
        </div>

        {/* Progress circle or bar */}
        <div className="w-full bg-gray-200 rounded-full h-4">
          <div
            className={`h-4 rounded-full transition-all duration-1000 ${scorePercentage >= 80
              ? 'bg-green-500'
              : scorePercentage >= 60
                ? 'bg-yellow-500'
                : 'bg-red-500'
              }`}
            style={{ width: `${scorePercentage}%` }}
          ></div>
        </div>
      </div>

      {/* Detailed Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Quiz Statistics</h3>
          <dl className="space-y-3">
            <div className="flex justify-between">
              <dt className="text-gray-600">Total Questions:</dt>
              <dd className="font-medium">{results.total_questions}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-600">Correct Answers:</dt>
              <dd className="font-medium text-green-600">{results.score}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-600">Incorrect Answers:</dt>
              <dd className="font-medium text-red-600">
                {results.total_questions - results.score}
              </dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-600">Accuracy:</dt>
              <dd className={`font-medium ${getScoreColor(scorePercentage)}`}>
                {scorePercentage}%
              </dd>
            </div>
          </dl>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Session Details</h3>
          <dl className="space-y-3">
            <div className="flex justify-between">
              <dt className="text-gray-600">Started:</dt>
              <dd className="font-medium">
                {new Date(results.started_at).toLocaleString()}
              </dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-600">Completed:</dt>
              <dd className="font-medium">
                {new Date(results.finished_at).toLocaleString()}
              </dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-600">Duration:</dt>
              <dd className="font-medium">
                {results.time_taken_seconds > 60
                  ? `${Math.round(results.time_taken_seconds / 60)} minutes`
                  : `${results.time_taken_seconds} seconds`
                }
              </dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-600">Percentage:</dt>
              <dd className="font-medium capitalize">{results.percentage}%</dd>
            </div>
          </dl>
        </div>
      </div>

      {/* Question Details */}
      {results.results && results.results.length > 0 && (
        <div className="card mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Question Review</h3>
          <div className="space-y-4">
            {results.results.map((question, index) => {
              const isSkipped = !question.selected_option;
              return (
                <div
                  key={question.question_id}
                  className={`p-4 rounded-lg border ${question.is_correct
                      ? 'border-green-200 bg-green-50'
                      : isSkipped
                        ? 'border-gray-300 bg-gray-50'
                        : 'border-red-200 bg-red-50'
                    }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="font-medium text-gray-900">
                      Question {index + 1}
                    </h4>
                    <span
                      className={`inline-flex items-center px-2 py-1 text-xs font-semibold rounded-full ${question.is_correct
                          ? 'bg-green-100 text-green-800'
                          : isSkipped
                            ? 'bg-gray-100 text-gray-800'
                            : 'bg-red-100 text-red-800'
                        }`}
                    >
                      {question.is_correct ? '✓ Correct' : isSkipped ? '⊘ Skipped' : '✗ Incorrect'}
                    </span>
                  </div>

                  <p className="text-gray-700 mb-3">{question.question_text}</p>

                  <div className="text-sm space-y-1">
                    <div>
                      <span className="text-gray-600">Your answer: </span>
                      <span className={question.is_correct ? 'text-green-700' : isSkipped ? 'text-gray-500 italic' : 'text-red-700'}>
                        {question.selected_option || 'Not answered (time expired)'}
                      </span>
                    </div>
                    {!question.is_correct && (
                      <div>
                        <span className="text-gray-600">Correct answer: </span>
                        <span className="text-green-700 font-medium">{question.correct_option}</span>
                      </div>
                    )}
                    {question.explanation && (
                      <div className="mt-2 text-gray-600 italic">
                        <strong>Explanation:</strong> {question.explanation}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex justify-center space-x-4">
        <Button variant="secondary" onClick={() => navigate('/quizzes')}>
          Take Another Quiz
        </Button>
        <Button onClick={() => navigate('/')}>
          Go to Home
        </Button>
      </div>
    </div>
  );
};

export default ResultsPage;