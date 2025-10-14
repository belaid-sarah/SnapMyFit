import React from 'react';
import { ExternalLink, Star, ShoppingBag, Tag } from 'lucide-react';
import { FashionItem } from '../../types';

interface SearchResultsProps {
  items: FashionItem[];
  confidence: number;
}

const SearchResults: React.FC<SearchResultsProps> = ({ items, confidence }) => {
  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return 'text-green-600 bg-green-100';
    if (confidence >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  return (
    <div className="space-y-6">
      {/* Confidence Score */}
      <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-800">Match Confidence</h3>
          <div className={`px-3 py-1 rounded-full text-sm font-medium ${getConfidenceColor(confidence)}`}>
            {confidence}% match
          </div>
        </div>
        <div className="mt-3 bg-gray-200 rounded-full h-2">
          <div 
            className="bg-gradient-to-r from-purple-600 to-pink-600 h-2 rounded-full transition-all duration-1000"
            style={{ width: `${confidence}%` }}
          />
        </div>
      </div>

      {/* Fashion Items */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {items.map((item) => (
          <div key={item.id} className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-100 hover:shadow-xl transition-shadow">
            <div className="aspect-square overflow-hidden">
              <img 
                src={item.imageUrl} 
                alt={item.name}
                className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
              />
            </div>
            
            <div className="p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-purple-600 bg-purple-100 px-2 py-1 rounded-full">
                  {item.brand}
                </span>
                <div className="flex items-center space-x-1">
                  <Star className="w-4 h-4 text-yellow-500 fill-current" />
                  <span className="text-sm text-gray-600">{item.confidence}%</span>
                </div>
              </div>
              
              <h4 className="text-lg font-semibold text-gray-800 mb-2">{item.name}</h4>
              <p className="text-gray-600 text-sm mb-3 line-clamp-2">{item.description}</p>
              
              <div className="flex flex-wrap gap-1 mb-4">
                {item.tags.slice(0, 3).map((tag) => (
                  <span key={tag} className="inline-flex items-center space-x-1 text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                    <Tag className="w-3 h-3" />
                    <span>{tag}</span>
                  </span>
                ))}
              </div>

              <div className="border-t pt-4 space-y-3">
                <div className="text-2xl font-bold text-gray-800">
                  ${item.price}
                </div>
                
                <div className="space-y-2">
                  {item.shoppingLinks.slice(0, 2).map((link, index) => (
                    <a
                      key={index}
                      href={link.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center justify-between w-full p-3 bg-gray-50 hover:bg-purple-50 rounded-lg transition-colors group"
                    >
                      <div className="flex items-center space-x-3">
                        <ShoppingBag className="w-4 h-4 text-gray-600 group-hover:text-purple-600" />
                        <div>
                          <div className="font-medium text-gray-800">{link.store}</div>
                          <div className="text-sm text-gray-500">${link.price}</div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`text-xs px-2 py-1 rounded-full ${
                          link.availability === 'in-stock' ? 'bg-green-100 text-green-600' :
                          link.availability === 'limited' ? 'bg-yellow-100 text-yellow-600' :
                          'bg-red-100 text-red-600'
                        }`}>
                          {link.availability.replace('-', ' ')}
                        </span>
                        <ExternalLink className="w-4 h-4 text-gray-400 group-hover:text-purple-600" />
                      </div>
                    </a>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SearchResults;