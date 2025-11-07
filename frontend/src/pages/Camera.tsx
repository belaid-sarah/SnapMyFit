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

  const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

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

    try {
      // Convertir dataURL en Blob
      const res = await fetch(imageData);
      const blob = await res.blob();

      const formData = new FormData();
      formData.append('file', new File([blob], 'capture.jpg', { type: 'image/jpeg' }));

      const response = await fetch(`${API_BASE}/search`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Search failed: ${response.status} ${response.statusText} - ${errorText}`);
      }

      const data = await response.json();
      console.log('📦 Données reçues de l\'API:', data);
      
      const items: FashionItem[] = (data.results || []).map((r: any, idx: number) => ({
        id: r.path || r.ref || String(idx),
        imageUrl: r.imageUrl.startsWith('http') ? r.imageUrl : `${API_BASE}${r.imageUrl}`,
        brand: r.brand || r.type || data.type || 'Unknown',
        name: r.name || r.ref || 'Similar item',
        description: `Item similaire (${r.category || r.type || 'unknown'}) - Référence: ${r.ref || 'N/A'}`,
        price: r.price || Math.floor(Math.random() * 80) + 20,
        category: r.category || r.type || data.type || 'unknown',
        color: 'N/A',
        confidence: Math.floor(Math.random() * 20) + 80, // placeholder 80-100
        tags: [r.category || r.type || 'similar'],
        shoppingLinks: [
          { store: 'Store A', url: '#', price: r.price || Math.floor(Math.random() * 80) + 20, availability: 'in-stock' },
          { store: 'Store B', url: '#', price: r.price || Math.floor(Math.random() * 80) + 20, availability: 'limited' },
        ],
      }));

      setConfidence(Math.floor(Math.random() * 20) + 80);
      setSearchResults(items);
      updateUserPoints(5);
    } catch (e: any) {
      console.error('❌ Erreur lors de la recherche:', e);
      const errorMsg = e?.message || 'Failed to analyze image';
      setError(`Erreur: ${errorMsg}. Vérifiez que l'API est démarrée sur ${API_BASE}`);
    } finally {
      setIsAnalyzing(false);
    }
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