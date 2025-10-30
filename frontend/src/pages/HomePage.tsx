import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { BookOpen, Trophy, Users, Play, ArrowRight } from 'lucide-react';
import { quizApi } from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';
import Button from '@/components/ui/Button';
import type { Quiz, Leaderboard } from '@/types';

const HomePage: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const [featuredQuizzes, setFeaturedQuizzes] = useState<Quiz[]>([]);
  const [leaderboard, setLeaderboard] = useState<Leaderboard | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [quizzes, leaderboardData] = await Promise.all([
          quizApi.getQuizzes({ limit: 3 }),
          quizApi.getLeaderboard({ limit: 5 }),
        ]);
        setFeaturedQuizzes(quizzes);
        setLeaderboard(leaderboardData);
      } catch (error) {
        console.error('Failed to load homepage data:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, []);

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-800 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <div className="flex justify-center mb-8">
              <img src="/ogs-logo.png" alt="OGS Logo" className="h-16 w-auto" />
            </div>
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              TechXConf QuizApp
            </h1>
            <p className="text-xl md:text-2xl mb-8 text-primary-100">
              Challenge yourself. Compete. Conquer the leaderboard!
            </p>

            {isAuthenticated ? (
              <div className="space-y-4 md:space-y-0 md:space-x-4 md:flex md:justify-center">
                <Link to="/quizzes">
                  <Button size="lg" className="bg-white text-primary-600 hover:bg-gray-100 min-w-[200px]">
                    <Play className="h-5 w-5 mr-2" />
                    Start Quiz
                  </Button>
                </Link>
                <Link to="/leaderboard">
                  <Button size="lg" variant="secondary" className="bg-primary-500 hover:bg-primary-400 min-w-[200px]">
                    <Trophy className="h-5 w-5 mr-2" />
                    View Leaderboard
                  </Button>
                </Link>
              </div>
            ) : (
              <div className="space-y-4 md:space-y-0 md:space-x-4 md:flex md:justify-center">
                <Link to="/register">
                  <Button size="lg" className="bg-white text-primary-600 hover:bg-gray-100 min-w-[200px]">
                    Get Started
                  </Button>
                </Link>
                <Link to="/login">
                  <Button size="lg" variant="secondary" className="bg-primary-500 hover:bg-primary-400 min-w-[200px]">
                    Sign In
                  </Button>
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="bg-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
            <div className="space-y-4">
              <div className="bg-blue-100 rounded-full p-6 w-20 h-20 mx-auto flex items-center justify-center">
                <BookOpen className="h-10 w-10 text-blue-600" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900">100+</h3>
              <p className="text-gray-600">Quiz Questions</p>
            </div>
            <div className="space-y-4">
              <div className="bg-green-100 rounded-full p-6 w-20 h-20 mx-auto flex items-center justify-center">
                <Users className="h-10 w-10 text-green-600" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900">1000+</h3>
              <p className="text-gray-600">Active Users</p>
            </div>
            <div className="space-y-4">
              <div className="bg-purple-100 rounded-full p-6 w-20 h-20 mx-auto flex items-center justify-center">
                <Trophy className="h-10 w-10 text-purple-600" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900">50+</h3>
              <p className="text-gray-600">Quiz Topics</p>
            </div>
          </div>
        </div>
      </div>

      {/* Featured Quizzes */}
      <div className="bg-gray-50 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Featured Quizzes
            </h2>
            <p className="text-lg text-gray-600">
              Popular quizzes to test your knowledge
            </p>
          </div>

          {isLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {[1, 2, 3].map((i) => (
                <div key={i} className="card animate-pulse">
                  <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
                  <div className="h-3 bg-gray-200 rounded mb-2"></div>
                  <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                </div>
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {featuredQuizzes.map((quiz) => (
                <div key={quiz.id} className="card-hover group">
                  <div className="flex items-center mb-4">
                    <div className="p-2 bg-primary-100 rounded-lg mr-3">
                      <BookOpen className="h-6 w-6 text-primary-600" />
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 group-hover:text-primary-600 transition-colors">
                      {quiz.title}
                    </h3>
                  </div>
                  <p className="text-gray-600 mb-4">{quiz.description}</p>
                  <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                    <span>{quiz.total_questions} questions</span>
                    <span>{quiz.estimated_time_minutes} min</span>
                  </div>
                  <div className="flex flex-wrap gap-1 mb-4">
                    {quiz.difficulties.slice(0, 2).map((difficulty) => (
                      <span
                        key={difficulty}
                        className="px-2 py-1 bg-gray-100 text-gray-600 rounded-full text-xs"
                      >
                        {difficulty}
                      </span>
                    ))}
                  </div>
                  <Link to={`/quiz/${quiz.id}`}>
                    <Button className="w-full group-hover:bg-primary-700 transition-colors">
                      Start Quiz
                      <ArrowRight className="h-4 w-4 ml-2" />
                    </Button>
                  </Link>
                </div>
              ))}
            </div>
          )}

          <div className="text-center mt-12">
            <Link to="/quizzes">
              <Button variant="secondary" size="lg">
                View All Quizzes
                <ArrowRight className="h-5 w-5 ml-2" />
              </Button>
            </Link>
          </div>
        </div>
      </div>

      {/* Leaderboard Preview */}
      {leaderboard && leaderboard.entries.length > 0 && (
        <div className="bg-white py-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-gray-900 mb-4">
                Top Performers
              </h2>
              <p className="text-lg text-gray-600">
                See how you stack up against other quiz takers
              </p>
            </div>

            <div className="bg-gray-50 rounded-xl p-8">
              <div className="space-y-4">
                {leaderboard.entries.slice(0, 3).map((entry, index) => (
                  <div
                    key={entry.rank}
                    className="flex items-center justify-between p-4 bg-white rounded-lg shadow-sm"
                  >
                    <div className="flex items-center">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${index === 0 ? 'bg-yellow-100 text-yellow-800' :
                        index === 1 ? 'bg-gray-100 text-gray-800' :
                          'bg-orange-100 text-orange-800'
                        }`}>
                        {entry.rank}
                      </div>
                      <span className="ml-4 font-medium text-gray-900">
                        {entry.display_name}
                      </span>
                      {entry.is_current_user && (
                        <span className="ml-2 px-2 py-1 bg-primary-100 text-primary-800 text-xs rounded-full">
                          You
                        </span>
                      )}
                    </div>
                    <div className="text-right">
                      <div className="font-semibold text-gray-900">
                        {entry.score}/{entry.total_questions}
                      </div>
                      <div className="text-sm text-gray-500">
                        {entry.percentage}%
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="text-center mt-8">
                <Link to="/leaderboard">
                  <Button variant="secondary">
                    View Full Leaderboard
                    <ArrowRight className="h-4 w-4 ml-2" />
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default HomePage;