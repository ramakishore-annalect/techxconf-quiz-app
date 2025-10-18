import React, { useState, useEffect } from 'react';
import { LeaderboardEntry } from '@/types';
import { apiService } from '@/services/api';
import { Button } from '@/components/ui/Button';

const LeaderboardPage: React.FC = () => {
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTopic, setSelectedTopic] = useState<string>('all');
  const [topics, setTopics] = useState<string[]>(['all']);

  useEffect(() => {
    fetchTopics();
  }, []);

  useEffect(() => {
    fetchLeaderboard();
  }, [selectedTopic]);

  const fetchTopics = async () => {
    try {
      const response = await apiService.getQuizzes();
      const uniqueTopics = [...new Set(response.map((quiz: any) => quiz.topics).flat())];
      setTopics(['all', ...uniqueTopics as string[]]);
    } catch (err) {
      console.error('Error fetching topics:', err);
    }
  };

  const fetchLeaderboard = async () => {
    try {
      setLoading(true);
      const topic = selectedTopic === 'all' ? undefined : selectedTopic;
      const data = await apiService.getLeaderboard(topic);
      setLeaderboard(data.entries);
    } catch (err) {
      setError('Failed to load leaderboard');
      console.error('Error fetching leaderboard:', err);
    } finally {
      setLoading(false);
    }
  };

  const getRankIcon = (rank: number): string => {
    switch (rank) {
      case 1:
        return '🥇';
      case 2:
        return '🥈';
      case 3:
        return '🥉';
      default:
        return `#${rank}`;
    }
  };

  const getRankColor = (rank: number): string => {
    switch (rank) {
      case 1:
        return 'text-yellow-600';
      case 2:
        return 'text-gray-600';
      case 3:
        return 'text-orange-600';
      default:
        return 'text-gray-800';
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

  if (error) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Leaderboard</h1>
          <p className="text-red-600 mb-6">{error}</p>
          <Button onClick={fetchLeaderboard}>
            Try Again
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Leaderboard</h1>
        <p className="text-gray-600 mb-6">
          See how you stack up against other quiz takers!
        </p>

        {/* Topic Filter */}
        <div className="flex flex-wrap gap-2">
          <span className="text-sm font-medium text-gray-700 flex items-center mr-4">
            Filter by topic:
          </span>
          {topics.map((topic) => (
            <Button
              key={topic}
              variant={selectedTopic === topic ? 'primary' : 'secondary'}
              size="sm"
              onClick={() => setSelectedTopic(topic)}
            >
              {topic === 'all' ? 'All Topics' : topic.charAt(0).toUpperCase() + topic.slice(1)}
            </Button>
          ))}
        </div>
      </div>

      {/* Leaderboard */}
      {leaderboard.length === 0 ? (
        <div className="text-center py-12">
          <h3 className="text-lg font-medium text-gray-900 mb-2">No results yet</h3>
          <p className="text-gray-600">
            {selectedTopic === 'all'
              ? 'No quiz results found. Be the first to take a quiz!'
              : `No results found for ${selectedTopic}. Take a quiz in this topic to appear here!`
            }
          </p>
        </div>
      ) : (
        <div className="card">
          <div className="overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Rank
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    User
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Score %
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Questions
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Correct
                  </th>
                  {selectedTopic === 'all' && (
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Time Taken
                    </th>
                  )}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {leaderboard.map((entry) => {
                  return (
                    <tr
                      key={`${entry.rank}-${entry.display_name}`}
                      className={`hover:bg-gray-50 ${entry.rank <= 3 ? 'bg-gradient-to-r from-yellow-50 to-transparent' : ''
                        } ${entry.is_current_user ? 'bg-blue-50' : ''}`}
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className={`text-lg font-bold ${getRankColor(entry.rank)}`}>
                          {getRankIcon(entry.rank)}
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10">
                            <div className="h-10 w-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center text-white font-semibold">
                              {entry.display_name.charAt(0).toUpperCase()}
                            </div>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">
                              {entry.display_name}
                              {entry.is_current_user && (
                                <span className="ml-2 text-xs text-blue-600">(You)</span>
                              )}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="text-sm font-medium text-gray-900">
                            {entry.percentage}%
                          </div>
                          <div className="ml-2 w-16 bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-blue-600 h-2 rounded-full"
                              style={{ width: `${Math.min(entry.percentage, 100)}%` }}
                            ></div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {entry.total_questions}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          {entry.score}/{entry.total_questions}
                        </span>
                      </td>
                      {selectedTopic === 'all' && (
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {Math.floor(entry.time_taken_seconds / 60)}m {entry.time_taken_seconds % 60}s
                        </td>
                      )}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Pagination info */}
          {leaderboard.length >= 50 && (
            <div className="px-6 py-3 bg-gray-50 text-center">
              <p className="text-sm text-gray-600">
                Showing top 50 results
              </p>
            </div>
          )}
        </div>
      )}

      {/* Call to action */}
      <div className="text-center mt-8">
        <p className="text-gray-600 mb-4">
          Want to improve your ranking? Take more quizzes!
        </p>
        <Button onClick={() => window.location.href = '/quizzes'}>
          Browse Quizzes
        </Button>
      </div>
    </div>
  );
};

export default LeaderboardPage;