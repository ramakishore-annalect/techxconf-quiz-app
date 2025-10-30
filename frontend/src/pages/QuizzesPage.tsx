import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Quiz } from '@/types';
import { apiService } from '@/services/api';
import { Button } from '@/components/ui/Button';

const QuizzesPage: React.FC = () => {
  const [quizzes, setQuizzes] = useState<Quiz[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchQuizzes();
  }, []);

  const fetchQuizzes = async () => {
    try {
      setLoading(true);
      const quizzes = await apiService.getQuizzes();
      setQuizzes(quizzes);
    } catch (err) {
      setError('Failed to load quizzes');
      console.error('Error fetching quizzes:', err);
    } finally {
      setLoading(false);
    }
  };

  // Note: Backend doesn't provide is_active field yet
  // For now, show all quizzes without filtering
  const filteredQuizzes = quizzes;

  const handleStartQuiz = (quizId: string) => {
    // Navigate to quiz detail page where user will enter participant info
    navigate(`/quiz/${quizId}`);
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-center items-center min-h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Available Quizzes</h1>
          <p className="text-red-600">{error}</p>
          <Button onClick={fetchQuizzes} className="mt-4">
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Available Quizzes</h1>
      </div>

      {filteredQuizzes.length === 0 ? (
        <div className="text-center py-12">
          <h3 className="text-lg font-medium text-gray-900 mb-2">No quizzes found</h3>
          <p className="text-gray-600">
            There are no quizzes available at the moment.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredQuizzes.map((quiz) => (
            <div key={quiz.id} className="card hover:shadow-lg transition-shadow duration-200">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-xl font-semibold text-gray-900 line-clamp-2">
                  {quiz.title}
                </h3>
                <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                  Active
                </span>
              </div>

              {quiz.description && (
                <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                  {quiz.description}
                </p>
              )}

              <div className="flex justify-between items-center text-sm text-gray-500 mb-4">
                <span>Topics: {quiz.topics.join(', ')}</span>
                <span>{quiz.total_questions} questions</span>
              </div>

              {quiz.estimated_time_minutes && (
                <p className="text-sm text-gray-500 mb-4">
                  Estimated time: {quiz.estimated_time_minutes} minutes
                </p>
              )}

              <div className="flex space-x-3">
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => navigate(`/quiz/${quiz.id}`)}
                  className="flex-1"
                >
                  View Details
                </Button>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => handleStartQuiz(quiz.id)}
                  className="flex-1"
                >
                  Start Quiz
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default QuizzesPage;