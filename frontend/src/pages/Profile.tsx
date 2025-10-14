import React from 'react';
import { Trophy, Star, Search, Plus, Calendar, TrendingUp } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Profile: React.FC = () => {
  const { user } = useAuth();

  if (!user) return null;

  const achievements = [
    { title: 'First Search', description: 'Completed your first fashion search', earned: true, points: 10 },
    { title: 'Contributor', description: 'Added 5 items to the database', earned: true, points: 50 },
    { title: 'Fashion Expert', description: 'Reached 100 points', earned: true, points: 100 },
    { title: 'Community Hero', description: 'Helped 50 users identify items', earned: false, points: 200 },
    { title: 'Trendsetter', description: 'Identified trending items first', earned: false, points: 150 },
  ];

  const recentActivity = [
    { type: 'search', item: 'Nike Air Max Sneakers', date: '2 hours ago', points: 5 },
    { type: 'contribution', item: 'Added Zara Blazer reference', date: '1 day ago', points: 25 },
    { type: 'search', item: 'Vintage Denim Jacket', date: '2 days ago', points: 5 },
    { type: 'contribution', item: 'Corrected H&M price info', date: '3 days ago', points: 15 },
  ];

  const levelProgress = ((user.points % 100) / 100) * 100;
  const nextLevelPoints = (user.level + 1) * 100;

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Profile Header */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
          <div className="flex flex-col md:flex-row items-center md:items-start space-y-6 md:space-y-0 md:space-x-8">
            <div className="w-24 h-24 bg-gradient-to-br from-purple-600 to-pink-600 rounded-full flex items-center justify-center text-white text-3xl font-bold">
              {user.name.charAt(0).toUpperCase()}
            </div>
            
            <div className="flex-1 text-center md:text-left">
              <h1 className="text-3xl font-bold text-gray-800 mb-2">{user.name}</h1>
              <p className="text-gray-600 mb-4">{user.email}</p>
              <div className="flex flex-wrap justify-center md:justify-start gap-4">
                <div className="bg-gradient-to-r from-purple-100 to-pink-100 px-4 py-2 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <Trophy className="w-5 h-5 text-purple-600" />
                    <span className="font-semibold text-purple-700">{user.points} Points</span>
                  </div>
                </div>
                <div className="bg-blue-100 px-4 py-2 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <Star className="w-5 h-5 text-blue-600" />
                    <span className="font-semibold text-blue-700">Level {user.level}</span>
                  </div>
                </div>
                <div className="bg-green-100 px-4 py-2 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <Search className="w-5 h-5 text-green-600" />
                    <span className="font-semibold text-green-700">{user.searchesRemaining} Searches</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Level Progress */}
          <div className="mt-8 pt-8 border-t border-gray-100">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-600">Progress to Level {user.level + 1}</span>
              <span className="text-sm text-gray-500">{user.points % 100}/{100} points</span>
            </div>
            <div className="bg-gray-200 rounded-full h-3">
              <div 
                className="bg-gradient-to-r from-purple-600 to-pink-600 h-3 rounded-full transition-all duration-1000"
                style={{ width: `${levelProgress}%` }}
              />
            </div>
            <p className="text-sm text-gray-500 mt-2">
              {100 - (user.points % 100)} points needed to reach Level {user.level + 1}
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Stats Cards */}
          <div className="lg:col-span-2 space-y-6">
            {/* Stats Overview */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-white rounded-xl p-6 shadow-lg text-center">
                <Search className="w-8 h-8 text-purple-600 mx-auto mb-2" />
                <div className="text-2xl font-bold text-gray-800">42</div>
                <div className="text-sm text-gray-600">Total Searches</div>
              </div>
              <div className="bg-white rounded-xl p-6 shadow-lg text-center">
                <Plus className="w-8 h-8 text-green-600 mx-auto mb-2" />
                <div className="text-2xl font-bold text-gray-800">{user.contributionsCount}</div>
                <div className="text-sm text-gray-600">Contributions</div>
              </div>
              <div className="bg-white rounded-xl p-6 shadow-lg text-center">
                <Calendar className="w-8 h-8 text-blue-600 mx-auto mb-2" />
                <div className="text-2xl font-bold text-gray-800">28</div>
                <div className="text-sm text-gray-600">Days Active</div>
              </div>
              <div className="bg-white rounded-xl p-6 shadow-lg text-center">
                <TrendingUp className="w-8 h-8 text-pink-600 mx-auto mb-2" />
                <div className="text-2xl font-bold text-gray-800">95%</div>
                <div className="text-sm text-gray-600">Accuracy</div>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-xl font-semibold text-gray-800 mb-6">Recent Activity</h3>
              <div className="space-y-4">
                {recentActivity.map((activity, index) => (
                  <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-4">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                        activity.type === 'search' ? 'bg-purple-100' : 'bg-green-100'
                      }`}>
                        {activity.type === 'search' ? 
                          <Search className="w-5 h-5 text-purple-600" /> :
                          <Plus className="w-5 h-5 text-green-600" />
                        }
                      </div>
                      <div>
                        <div className="font-medium text-gray-800">{activity.item}</div>
                        <div className="text-sm text-gray-500">{activity.date}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-semibold text-purple-600">+{activity.points} pts</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Achievements */}
          <div className="space-y-6">
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-xl font-semibold text-gray-800 mb-6">Achievements</h3>
              <div className="space-y-4">
                {achievements.map((achievement, index) => (
                  <div key={index} className={`p-4 rounded-lg border-2 ${
                    achievement.earned ? 
                      'border-yellow-200 bg-yellow-50' : 
                      'border-gray-200 bg-gray-50 opacity-50'
                  }`}>
                    <div className="flex items-start space-x-3">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                        achievement.earned ? 'bg-yellow-400' : 'bg-gray-300'
                      }`}>
                        <Trophy className="w-4 h-4 text-white" />
                      </div>
                      <div className="flex-1">
                        <div className="font-semibold text-gray-800">{achievement.title}</div>
                        <div className="text-sm text-gray-600 mb-2">{achievement.description}</div>
                        <div className="text-sm font-medium text-purple-600">
                          {achievement.points} points
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-gradient-to-br from-purple-600 to-pink-600 rounded-xl p-6 text-white">
              <h3 className="text-lg font-semibold mb-4">Earn More Points</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span>Daily search bonus</span>
                  <span className="font-semibold">+10 pts</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Add new item</span>
                  <span className="font-semibold">+25 pts</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Verify item info</span>
                  <span className="font-semibold">+15 pts</span>
                </div>
              </div>
              <button className="w-full mt-4 bg-white text-purple-600 px-4 py-2 rounded-lg font-medium hover:bg-gray-100 transition-colors">
                Start Contributing
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;