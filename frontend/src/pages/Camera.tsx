import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import CameraCapture from '../components/Camera/CameraCapture';
import SearchResults from '../components/Search/SearchResults';
import { useAuth } from '../context/AuthContext';
import { FashionItem } from '../types';
import { Loader, AlertCircle, Sparkles } from 'lucide-react';

const Camera: React.FC = () => {
  const [capturedImage, setCapturedImage] = useState<string>('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [searchResults, setSearchResults] = useState<FashionItem[] | null>(null);
  const [confidence, setConfidence] = useState(0);
  const [error, setError] = useState<string>('');
  const { user, updateUserPoints } = useAuth();
  const navigate = useNavigate();

  // Mock fashion items for demo
  const mockFashionItems: FashionItem[] = [
    {
      id: '1',
      imageUrl: 'https://images.pexels.com/photos/1464625/pexels-photo-1464625.jpeg',
      brand: 'Zara',
      name: 'Oversized Blazer',
      description: 'Classic tailored blazer with structured shoulders and a relaxed fit. Perfect for professional and casual styling.',
      price: 89.90,
      category: 'Blazers',
      color: 'Navy Blue',
      confidence: 92,
      tags: ['business', 'casual', 'oversized'],
      shoppingLinks: [
        { store: 'Zara', url: '#', price: 89.90, availability: 'in-stock' },
        { store: 'H&M', url: '#', price: 79.99, availability: 'limited' },
        { store: 'ASOS', url: '#', price: 95.00, availability: 'in-stock' }
      ]
    },
    {
      id: '2',
      imageUrl: 'https://images.pexels.com/photos/1536619/pexels-photo-1536619.jpeg',
      brand: 'Nike',
      name: 'Air Max 270',
      description: 'Comfortable lifestyle sneaker with Max Air unit for all-day comfort and modern street style appeal.',
      price: 150.00,
      category: 'Sneakers',
      color: 'White/Black',
      confidence: 88,
      tags: ['athletic', 'casual', 'comfort'],
      shoppingLinks: [
        { store: 'Nike', url: '#', price: 150.00, availability: 'in-stock' },
        { store: 'Foot Locker', url: '#', price: 150.00, availability: 'in-stock' },
        { store: 'JD Sports', url: '#', price: 145.00, availability: 'limited' }
      ]
    }
  ];

  const handleImageCapture = async (imageData: string) => {
    if (!user) {
      navigate('/login');
      return;
    }

    if (user.searchesRemaining <= 0) {
      setError('No searches remaining. Contribute to the community to earn more searches!');
      return;
    }

    setCapturedImage(imageData);
    setIsAnalyzing(true);
    setError('');

    // Simulate AI analysis
    setTimeout(() => {
      const confidence = Math.floor(Math.random() * 30) + 70; // 70-100%
      setConfidence(confidence);
      setSearchResults(mockFashionItems);
      setIsAnalyzing(false);
      
      // Award points for search
      updateUserPoints(5);
      
      // Decrease searches remaining (in real app, this would be handled by backend)
      // This is just for demo purposes
    }, 3000);
  };

  const resetSearch = () => {
    setCapturedImage('');
    setSearchResults(null);
    setConfidence(0);
    setError('');
  };

  if (!user) {
    navigate('/login');
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-gray-800 mb-4">
            Fashion Item Recognition
          </h1>
          <p className="text-lg text-gray-600 mb-4">
            Snap a photo or upload an image to identify any fashion item instantly
          </p>
          <div className="bg-white rounded-xl p-4 inline-flex items-center space-x-6 shadow-sm border border-gray-100">
            <div className="flex items-center space-x-2">
              <Sparkles className="w-5 h-5 text-purple-600" />
              <span className="font-semibold text-gray-700">Searches: {user.searchesRemaining}</span>
            </div>
            <div className="text-sm text-gray-500">
              Earn more by contributing!
            </div>
          </div>
        </div>

        {error && (
          <div className="max-w-2xl mx-auto mb-8">
            <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-center space-x-3">
              <AlertCircle className="w-5 h-5 text-red-500" />
              <span className="text-red-700">{error}</span>
            </div>
          </div>
        )}

        {!capturedImage && !isAnalyzing && !searchResults && (
          <CameraCapture onImageCapture={handleImageCapture} />
        )}

        {capturedImage && isAnalyzing && (
          <div className="max-w-2xl mx-auto">
            <div className="bg-white rounded-2xl shadow-xl p-8 text-center">
              <img 
                src={capturedImage} 
                alt="Captured fashion item" 
                className="w-full max-w-md mx-auto rounded-xl shadow-lg mb-6"
              />
              <div className="flex items-center justify-center space-x-3 mb-4">
                <Loader className="w-6 h-6 animate-spin text-purple-600" />
                <span className="text-lg font-semibold text-gray-700">Analyzing your fashion item...</span>
              </div>
              <p className="text-gray-500">Our AI is identifying the brand, style, and finding shopping links for you.</p>
            </div>
          </div>
        )}

        {searchResults && (
          <div className="space-y-8">
            <div className="max-w-2xl mx-auto">
              <div className="bg-white rounded-2xl shadow-xl p-6">
                <img 
                  src={capturedImage} 
                  alt="Analyzed fashion item" 
                  className="w-full max-w-md mx-auto rounded-xl shadow-lg mb-4"
                />
                <div className="text-center">
                  <button
                    onClick={resetSearch}
                    className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-2 rounded-lg font-medium hover:from-purple-700 hover:to-pink-700 transition-all"
                  >
                    Search Another Item
                  </button>
                </div>
              </div>
            </div>

            <SearchResults items={searchResults} confidence={confidence} />
          </div>
        )}
      </div>
    </div>
  );
};

export default Camera;