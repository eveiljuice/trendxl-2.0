import React, { useEffect } from 'react';
import { X, ExternalLink, Heart, MessageCircle, Share, Eye } from 'lucide-react';
import { TrendVideo } from '../types';
import { formatNumber, formatRelativeTime } from '../utils';

interface VideoModalProps {
  trend: TrendVideo | null;
  isOpen: boolean;
  onClose: () => void;
}

const VideoModal: React.FC<VideoModalProps> = ({ trend, isOpen, onClose }) => {
  // Handle escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen || !trend) return null;

  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const handleOpenVideo = () => {
    if (trend.video_url) {
      window.open(trend.video_url, '_blank', 'noopener,noreferrer');
    }
  };

  return (
    <div 
      className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-2 sm:p-4"
      onClick={handleBackdropClick}
    >
      <div className="bg-primary-card border border-primary-line rounded-lg sm:rounded-card max-w-2xl w-full max-h-[95vh] sm:max-h-[90vh] overflow-y-auto animate-fade-in">
        {/* Header - адаптивные отступы */}
        <div className="flex items-center justify-between p-3 sm:p-4 md:p-6 border-b border-primary-line">
          <div className="flex items-center space-x-2 sm:space-x-3">
            <span className="bg-primary-accent text-white text-xs sm:text-sm font-medium px-2 py-0.5 sm:px-3 sm:py-1 rounded-btn">
              #{trend.hashtag}
            </span>
            <h2 className="text-base sm:text-lg font-semibold text-text-primary">
              Trend details
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 sm:p-2 hover:bg-primary-line rounded-btn text-text-secondary hover:text-text-primary transition-colors duration-150"
          >
            <X className="w-4 h-4 sm:w-5 sm:h-5" />
          </button>
        </div>

        {/* Enhanced Content - адаптивные отступы */}
        <div className="p-3 sm:p-4 md:p-6 lg:p-8 space-y-4 sm:space-y-6 md:space-y-8">
          {/* Video Preview with Multi-Image Support - адаптивная высота */}
          <div className="relative">
            <div className="aspect-[9/16] max-h-80 sm:max-h-96 bg-secondary rounded-lg sm:rounded-card overflow-hidden">
              {trend.cover_image_url ? (
                <img
                  src={trend.cover_image_url}
                  alt="Content thumbnail"
                  className="w-full h-full object-cover"
                  loading="lazy"
                  referrerPolicy="no-referrer"
                  crossOrigin="anonymous"
                  onError={(e) => {
                    const target = e.target as HTMLImageElement
                    target.style.display = 'none'
                  }}
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <div className="text-center">
                    <div className="w-16 h-16 bg-primary-line rounded-full flex items-center justify-center mb-4">
                      <Eye className="w-8 h-8 text-text-secondary" />
                    </div>
                    <p className="text-text-secondary">Preview unavailable</p>
                  </div>
                </div>
              )}
            </div>

            {/* Additional Images Gallery - адаптивные размеры */}
            {trend.images && trend.images.length > 0 && (
              <div className="mt-2 sm:mt-3 flex space-x-1.5 sm:space-x-2 overflow-x-auto pb-2">
                {trend.images.slice(0, 5).map((imageUrl, index) => (
                  <div
                    key={index}
                    className="flex-shrink-0 w-12 h-12 sm:w-14 sm:h-14 md:w-16 md:h-16 bg-primary-line rounded-md overflow-hidden"
                  >
                    <img
                      src={imageUrl}
                      alt={`Additional image ${index + 1}`}
                      className="w-full h-full object-cover hover:scale-110 transition-transform cursor-pointer"
                      loading="lazy"
                      referrerPolicy="no-referrer"
                      crossOrigin="anonymous"
                      onClick={() => {
                        window.open(imageUrl, '_blank');
                      }}
                      onError={(e) => {
                        const target = e.target as HTMLImageElement
                        target.style.visibility = 'hidden'
                      }}
                    />
                  </div>
                ))}
                {trend.images.length > 5 && (
                  <div className="flex-shrink-0 w-12 h-12 sm:w-14 sm:h-14 md:w-16 md:h-16 bg-primary-line rounded-md flex items-center justify-center">
                    <span className="text-xs text-text-secondary">+{trend.images.length - 5}</span>
                  </div>
                )}
              </div>
            )}

            {/* Open Video Button - адаптивные размеры */}
            {trend.video_url && (
              <button
                onClick={handleOpenVideo}
                className="absolute bottom-2 right-2 sm:bottom-4 sm:right-4 btn-primary flex items-center space-x-1.5 sm:space-x-2 text-xs sm:text-sm px-2 py-1 sm:px-3 sm:py-2"
              >
                <ExternalLink className="w-3 h-3 sm:w-4 sm:h-4" />
                <span>Open video</span>
              </button>
            )}
          </div>

          {/* Caption - адаптивные размеры */}
          {trend.caption && (
            <div>
              <h3 className="text-xs sm:text-sm font-medium text-text-primary mb-1.5 sm:mb-2">Description</h3>
              <p className="text-xs sm:text-sm text-text-secondary leading-relaxed">
                {trend.caption}
              </p>
            </div>
          )}

          {/* Stats Grid - адаптивная сетка */}
          <div>
            <h3 className="text-xs sm:text-sm font-medium text-text-primary mb-2 sm:mb-3">Statistics</h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 sm:gap-3 md:gap-4">
              <div className="text-center p-2 sm:p-3 bg-primary-bg rounded-btn">
                <Eye className="w-4 h-4 sm:w-5 sm:h-5 text-text-secondary mx-auto mb-0.5 sm:mb-1" />
                <div className="text-sm sm:text-base md:text-lg font-semibold text-text-primary">
                  {formatNumber(trend.views)}
                </div>
                <div className="text-xs text-text-secondary">Views</div>
              </div>

              <div className="text-center p-2 sm:p-3 bg-primary-bg rounded-btn">
                <Heart className="w-4 h-4 sm:w-5 sm:h-5 text-red-400 mx-auto mb-0.5 sm:mb-1" />
                <div className="text-sm sm:text-base md:text-lg font-semibold text-text-primary">
                  {formatNumber(trend.likes)}
                </div>
                <div className="text-xs text-text-secondary">Likes</div>
              </div>

              <div className="text-center p-2 sm:p-3 bg-primary-bg rounded-btn">
                <MessageCircle className="w-4 h-4 sm:w-5 sm:h-5 text-text-secondary mx-auto mb-0.5 sm:mb-1" />
                <div className="text-sm sm:text-base md:text-lg font-semibold text-text-primary">
                  {formatNumber(trend.comments)}
                </div>
                <div className="text-xs text-text-secondary">Comments</div>
              </div>

              <div className="text-center p-2 sm:p-3 bg-primary-bg rounded-btn">
                <Share className="w-4 h-4 sm:w-5 sm:h-5 text-text-secondary mx-auto mb-0.5 sm:mb-1" />
                <div className="text-sm sm:text-base md:text-lg font-semibold text-text-primary">
                  {formatNumber(trend.shares)}
                </div>
                <div className="text-xs text-text-secondary">Shares</div>
              </div>
            </div>
          </div>

          {/* Author & Date - адаптивные отступы */}
          <div className="flex items-center justify-between p-2 sm:p-3 md:p-4 bg-primary-bg rounded-btn">
            <div className="flex items-center space-x-2 sm:space-x-3">
              {trend.author.avatar_url ? (
                <img
                  src={trend.author.avatar_url}
                  alt={trend.author.username}
                  className="w-8 h-8 sm:w-10 sm:h-10 rounded-full object-cover"
                />
              ) : (
                <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-primary-line"></div>
              )}
              <div>
                <div className="text-text-primary font-medium text-sm sm:text-base">
                  @{trend.author.username || 'unknown'}
                </div>
                <div className="text-text-secondary text-xs sm:text-sm">
                  {formatRelativeTime(trend.create_time)}
                </div>
              </div>
            </div>
            
            {trend.author.is_verified && (
              <div className="bg-primary-accent text-white text-xs px-1.5 py-0.5 sm:px-2 sm:py-1 rounded-btn">
                Verified
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default VideoModal;