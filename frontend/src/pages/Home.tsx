import React from 'react';
import { Link } from 'react-router-dom';
import { Camera, Search, Users, Trophy, Sparkles, TrendingUp } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Home: React.FC = () => {
  const { user } = useAuth();

  const features = [
    {
      icon: Camera,
      title: 'Snap & Identify',
      description: 'Take a photo of any fashion item and get instant identification with shopping links.'
    },
    {
      icon: Search,
      title: 'Smart Recognition',
      description: 'Our AI-powered fashion recognition identifies brands, styles, and similar items.'
    },
    {
      icon: Users,
      title: 'Community Driven',
      description: 'Help build our database by contributing item references and earn points.'
    },
    {
      icon: Trophy,
      title: 'Earn Rewards',
      description: 'Gain points for contributions and unlock unlimited searches.'
    }
  ];

  const stats = [
    { label: 'Items Identified', value: '2.5M+', icon: Search },
    { label: 'Community Members', value: '150K+', icon: Users },
    { label: 'Fashion Brands', value: '10K+', icon: TrendingUp },
    { label: 'Daily Searches', value: '50K+', icon: Camera },
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-purple-900 via-purple-800 to-pink-800 text-white overflow-hidden">
        <div className="absolute inset-0 bg-[url('https://images.pexels.com/photos/1536619/pexels-photo-1536619.jpeg')] bg-cover bg-center opacity-10"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              Identify Any Fashion Item
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-pink-400">
                Instantly
              </span>
            </h1>
            <p className="text-xl md:text-2xl text-purple-100 mb-8 max-w-3xl mx-auto">
              Snap a photo and discover the exact brands, prices, and shopping links for any clothing item you see.
            </p>
            
            {user ? (
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                <Link
                  to="/camera"
                  className="bg-gradient-to-r from-yellow-400 to-pink-500 text-purple-900 px-8 py-4 rounded-xl font-bold text-lg hover:from-yellow-300 hover:to-pink-400 transition-all transform hover:scale-105 inline-flex items-center space-x-2"
                >
                  <Camera className="w-6 h-6" />
                  <span>Start Snapping</span>
                </Link>
                <div className="bg-white/10 backdrop-blur-sm px-6 py-3 rounded-xl">
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                      <Trophy className="w-5 h-5 text-yellow-400" />
                      <span className="font-semibold">{user.points} Points</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Search className="w-5 h-5 text-blue-400" />
                      <span>{user.searchesRemaining} Searches Left</span>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link
                  to="/register"
                  className="bg-gradient-to-r from-yellow-400 to-pink-500 text-purple-900 px-8 py-4 rounded-xl font-bold text-lg hover:from-yellow-300 hover:to-pink-400 transition-all transform hover:scale-105"
                >
                  Get Started Free
                </Link>
                <Link
                  to="/login"
                  className="bg-white/10 backdrop-blur-sm text-white px-8 py-4 rounded-xl font-bold text-lg hover:bg-white/20 transition-all border border-white/20"
                >
                  Sign In
                </Link>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => {
              const Icon = stat.icon;
              return (
                <div key={index} className="text-center">
                  <div className="bg-gradient-to-br from-purple-100 to-pink-100 w-16 h-16 rounded-xl flex items-center justify-center mx-auto mb-4">
                    <Icon className="w-8 h-8 text-purple-600" />
                  </div>
                  <div className="text-3xl font-bold text-gray-800 mb-2">{stat.value}</div>
                  <div className="text-gray-600 font-medium">{stat.label}</div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-800 mb-4">
              How SnapMyFit Works
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Our AI-powered platform makes fashion discovery effortless and rewarding
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <div key={index} className="bg-white rounded-xl p-8 shadow-lg hover:shadow-xl transition-shadow border border-gray-100">
                  <div className="bg-gradient-to-br from-purple-600 to-pink-600 w-14 h-14 rounded-xl flex items-center justify-center mb-6">
                    <Icon className="w-7 h-7 text-white" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-800 mb-3">{feature.title}</h3>
                  <p className="text-gray-600 leading-relaxed">{feature.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-purple-600 to-pink-600 text-white">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <Sparkles className="w-16 h-16 mx-auto mb-6 text-yellow-300" />
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Ready to Discover Fashion?
          </h2>
          <p className="text-xl mb-8 text-purple-100">
            Join thousands of fashion enthusiasts and start identifying items instantly.
          </p>
          {!user && (
            <Link
              to="/register"
              className="bg-white text-purple-600 px-8 py-4 rounded-xl font-bold text-lg hover:bg-gray-100 transition-all inline-flex items-center space-x-2"
            >
              <span>Start Your Fashion Journey</span>
              <Camera className="w-5 h-5" />
            </Link>
          )}
        </div>
      </section>
    </div>
  );
};

export default Home;