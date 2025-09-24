import React from 'react';
import { TrendingUp, ExternalLink } from 'lucide-react';
import { TrendVideo } from '../types';
import TrendCard from './TrendCard';
import { getStaggerDelay } from '../utils';

interface TrendGridProps {
  trends: TrendVideo[];
  onTrendClick: (trend: TrendVideo) => void;
}

const TrendGrid: React.FC<TrendGridProps> = ({ trends, onTrendClick }) => {
  if (trends.length === 0) return null;

  return (
    <div className="section-spacing animate-slide-up">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center space-x-3">
          <div className="flex items-center justify-center w-10 h-10 bg-primary-accent/10 rounded-full">
            <TrendingUp className="w-5 h-5 text-primary-accent" />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-text-primary">
              Trending videos
            </h2>
            <p className="text-text-secondary">
              Found {trends.length} popular videos (niche-specific + trending content)
            </p>
          </div>
        </div>

        {/* View All Link */}
        <button className="
          flex items-center space-x-2 text-primary-accent hover:text-primary-accent-hover
          transition-colors duration-150
        ">
          <span className="text-sm font-medium">All trends</span>
          <ExternalLink className="w-4 h-4" />
        </button>
      </div>

      {/* Trends Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 items-stretch">
        {trends.map((trend, index) => (
          <div
            key={trend.id}
            style={{
              animationDelay: `${getStaggerDelay(index, 150)}ms`
            }}
            className="h-full"
          >
            <TrendCard
              trend={trend}
              onClick={onTrendClick}
            />
          </div>
        ))}
      </div>

      {/* Load More Button (for future implementation) */}
      {trends.length >= 10 && (
        <div className="text-center mt-8">
          <button className="
            px-6 py-3 
            bg-primary-card border border-primary-line rounded-btn
            text-text-primary hover:text-text-primary hover:border-primary-accent/30
            transition-all duration-150
          ">
            Load more
          </button>
        </div>
      )}
    </div>
  );
};

export default TrendGrid;
