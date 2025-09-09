import React from 'react';
import { Play, Heart, MessageCircle, Share, Eye, ExternalLink } from 'lucide-react';
import { TrendVideo } from '../types';
import { formatNumber, formatRelativeTime, truncateText } from '../utils';

interface TrendCardProps {
  trend: TrendVideo;
  onClick: (trend: TrendVideo) => void;
}

const TrendCard: React.FC<TrendCardProps> = ({ trend, onClick }) => {
  const handleClick = () => {
    onClick(trend);
  };

  const handleVideoClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (trend.video_url) {
      window.open(trend.video_url, '_blank', 'noopener,noreferrer');
    }
  };

  return (
    <div 
      className="
        card cursor-pointer group
        hover:border-primary-accent/30 hover:shadow-lg hover:shadow-primary-accent/5
        transition-all duration-300 ease-out
        animate-fade-in
      "
      onClick={handleClick}
    >
      {/* Video Thumbnail */}
      <div className="relative mb-4 overflow-hidden rounded-card">
        <div className="aspect-[9/16] max-h-64 bg-primary-line relative">
          {trend.cover_image_url ? (
            <img
              src={trend.cover_image_url}
              alt="Video thumbnail"
              className="w-full h-full object-cover"
              onError={(e) => {
                const target = e.target as HTMLImageElement;
                target.style.display = 'none';
              }}
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <Play className="w-12 h-12 text-text-secondary" />
            </div>
          )}
          
          {/* Play Overlay */}
          <div className="
            absolute inset-0 bg-black/20 
            flex items-center justify-center
            opacity-0 group-hover:opacity-100
            transition-opacity duration-200
          ">
            <div className="
              bg-white/90 rounded-full p-3
              transform scale-90 group-hover:scale-100
              transition-transform duration-200
            ">
              <Play className="w-6 h-6 text-primary-bg" fill="currentColor" />
            </div>
          </div>

          {/* Hashtag Badge */}
          <div className="absolute top-3 left-3">
            <span className="
              bg-primary-accent text-white text-xs font-medium
              px-2 py-1 rounded-btn
            ">
              #{trend.hashtag}
            </span>
          </div>

          {/* External Link Button */}
          {trend.video_url && (
            <button
              onClick={handleVideoClick}
              className="
                absolute top-3 right-3
                bg-black/50 hover:bg-black/70
                text-white p-2 rounded-full
                opacity-0 group-hover:opacity-100
                transition-all duration-200
              "
              title="Open video"
            >
              <ExternalLink className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="space-y-3">
        {/* Caption */}
        {trend.caption && (
          <p className="text-text-primary text-sm leading-relaxed">
            {truncateText(trend.caption, 120)}
          </p>
        )}

        {/* Stats */}
        <div className="flex items-center justify-between text-text-secondary text-sm">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-1">
              <Eye className="w-4 h-4" />
              <span>{formatNumber(trend.views)}</span>
            </div>
            <div className="flex items-center space-x-1">
              <Heart className="w-4 h-4" />
              <span>{formatNumber(trend.likes)}</span>
            </div>
            <div className="flex items-center space-x-1">
              <MessageCircle className="w-4 h-4" />
              <span>{formatNumber(trend.comments)}</span>
            </div>
            <div className="flex items-center space-x-1">
              <Share className="w-4 h-4" />
              <span>{formatNumber(trend.shares)}</span>
            </div>
          </div>
        </div>

        {/* Author & Date */}
        <div className="flex items-center justify-between pt-2 border-t border-primary-line">
          <div className="flex items-center space-x-2">
            {trend.author.avatar_url ? (
              <img
                src={trend.author.avatar_url}
                alt={trend.author.username}
                className="w-6 h-6 rounded-full object-cover"
              />
            ) : (
              <div className="w-6 h-6 rounded-full bg-primary-line"></div>
            )}
            <span className="text-text-secondary text-sm">
              @{trend.author.username || 'unknown'}
            </span>
          </div>
          <span className="text-text-secondary text-xs">
            {formatRelativeTime(trend.create_time)}
          </span>
        </div>
      </div>
    </div>
  );
};

export default TrendCard;
