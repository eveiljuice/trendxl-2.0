import React from 'react';
import { TrendingUp } from 'lucide-react';
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
    <div className="space-y-6 sm:space-y-8 animate-slide-up">
      {/* Enhanced Header - адаптивные отступы */}
      <div className="bg-white rounded-xl sm:rounded-2xl shadow-xl border border-gray-200 p-4 sm:p-6 md:p-8">
        <div className="flex flex-col sm:flex-row items-start sm:items-center space-y-3 sm:space-y-0 sm:space-x-4">
          <div className="flex items-center justify-center w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-br from-purple-400 to-indigo-500 rounded-lg sm:rounded-xl shadow-lg animate-pulse flex-shrink-0">
            <TrendingUp className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
          </div>
          <div className="flex-1 w-full">
            <h2 className="text-xl sm:text-2xl font-bold text-black font-orbitron mb-1">
              Trending Videos
            </h2>
            <p className="text-sm sm:text-base text-gray-600 font-inter">
              Discovered <span className="font-semibold text-black">{trends.length}</span> popular videos with niche-specific content
            </p>
          </div>
          <div className="text-left sm:text-right w-full sm:w-auto">
            <div className="text-xl sm:text-2xl font-bold text-purple-600 font-orbitron">
              {trends.length}
            </div>
            <div className="text-xs sm:text-sm text-gray-500 font-medium">Videos Found</div>
          </div>
        </div>
      </div>

      {/* Enhanced Trends Grid - адаптивная сетка: 1 на мобиле, 2 на планшете, 3-4 на десктопе */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-6 md:gap-8 items-stretch">
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
    </div>
  );
};

export default TrendGrid;
