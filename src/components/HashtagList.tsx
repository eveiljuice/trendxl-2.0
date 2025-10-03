import React from 'react';
import { Hash } from 'lucide-react';

interface HashtagListProps {
  hashtags: string[];
}

const HashtagList: React.FC<HashtagListProps> = ({ hashtags }) => {
  if (hashtags.length === 0) return null;

  return (
    <div className="bg-white rounded-xl sm:rounded-2xl shadow-xl border border-gray-200 p-4 sm:p-6 md:p-8 animate-fade-in hover:shadow-2xl transition-all duration-300">
      <div className="flex items-center space-x-3 sm:space-x-4 mb-4 sm:mb-6">
        <div className="flex items-center justify-center w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-br from-green-400 to-emerald-500 rounded-lg sm:rounded-xl shadow-lg flex-shrink-0">
          <Hash className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
        </div>
        <div>
          <h3 className="text-lg sm:text-xl font-bold text-black font-orbitron">
            Trending Hashtags
          </h3>
          <p className="text-gray-600 text-xs sm:text-sm font-inter">Discovered for your content niche</p>
        </div>
      </div>
      
      <p className="text-gray-700 text-sm sm:text-base mb-4 sm:mb-6 font-inter leading-relaxed">
        AI discovered these trending hashtags for your content niche:
      </p>

      <div className="flex flex-wrap gap-2 sm:gap-3">
        {hashtags.map((hashtag, index) => (
          <span
            key={hashtag}
            className="
              inline-flex items-center px-3 py-1.5 sm:px-4 sm:py-2 bg-gradient-to-r from-gray-50 to-gray-100 
              rounded-full text-xs sm:text-sm font-semibold text-black border border-gray-200
              hover:from-gray-100 hover:to-gray-200 hover:shadow-md hover:scale-105
              transition-all duration-200 animate-fade-in cursor-pointer
              shadow-sm font-orbitron
            "
            style={{
              animationDelay: `${index * 50}ms`
            }}
          >
            <Hash className="w-2.5 h-2.5 sm:w-3 sm:h-3 mr-1 text-gray-600" />
            {hashtag}
          </span>
        ))}
      </div>
    </div>
  );
};

export default HashtagList;
