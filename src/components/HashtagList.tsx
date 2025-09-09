import React from 'react';
import { Hash } from 'lucide-react';

interface HashtagListProps {
  hashtags: string[];
}

const HashtagList: React.FC<HashtagListProps> = ({ hashtags }) => {
  if (hashtags.length === 0) return null;

  return (
    <div className="card animate-fade-in">
      <div className="flex items-center space-x-3 mb-4">
        <div className="flex items-center justify-center w-8 h-8 bg-primary-accent/10 rounded-full">
          <Hash className="w-4 h-4 text-primary-accent" />
        </div>
        <h3 className="text-lg font-semibold text-text-primary">
          Key hashtags
        </h3>
      </div>
      
      <p className="text-text-secondary text-sm mb-4">
        AI analyzed the most popular posts and extracted these trending hashtags:
      </p>

      <div className="flex flex-wrap gap-2">
        {hashtags.map((hashtag, index) => (
          <span
            key={hashtag}
            className="
              inline-flex items-center px-3 py-1.5 
              bg-primary-accent/10 text-primary-accent 
              rounded-btn text-sm font-medium
              border border-primary-accent/20
              animate-fade-in
            "
            style={{
              animationDelay: `${index * 100}ms`
            }}
          >
            #{hashtag}
          </span>
        ))}
      </div>
    </div>
  );
};

export default HashtagList;
