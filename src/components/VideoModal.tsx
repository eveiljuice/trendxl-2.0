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
      className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      onClick={handleBackdropClick}
    >
      <div className="
        bg-primary-card border border-primary-line rounded-card
        max-w-2xl w-full max-h-[90vh] overflow-y-auto
        animate-fade-in
      ">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-primary-line">
          <div className="flex items-center space-x-3">
            <span className="bg-primary-accent text-white text-sm font-medium px-3 py-1 rounded-btn">
              #{trend.hashtag}
            </span>
            <h2 className="text-lg font-semibold text-text-primary">
              Trend details
            </h2>
          </div>
          <button
            onClick={onClose}
            className="
              p-2 hover:bg-primary-line rounded-btn
              text-text-secondary hover:text-text-primary
              transition-colors duration-150
            "
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Video Preview */}
          <div className="relative">
            <div className="aspect-[9/16] max-h-96 bg-primary-line rounded-card overflow-hidden">
              {trend.cover_image_url ? (
                <img
                  src={trend.cover_image_url}
                  alt="Video thumbnail"
                  className="w-full h-full object-cover"
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

            {/* Open Video Button */}
            {trend.video_url && (
              <button
                onClick={handleOpenVideo}
                className="
                  absolute bottom-4 right-4
                  btn-primary flex items-center space-x-2
                "
              >
                <ExternalLink className="w-4 h-4" />
                <span>Open video</span>
              </button>
            )}
          </div>

          {/* Caption */}
          {trend.caption && (
            <div>
              <h3 className="text-sm font-medium text-text-primary mb-2">Description</h3>
              <p className="text-text-secondary leading-relaxed">
                {trend.caption}
              </p>
            </div>
          )}

          {/* Stats Grid */}
          <div>
            <h3 className="text-sm font-medium text-text-primary mb-3">Statistics</h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="text-center p-3 bg-primary-bg rounded-btn">
                <Eye className="w-5 h-5 text-text-secondary mx-auto mb-1" />
                <div className="text-lg font-semibold text-text-primary">
                  {formatNumber(trend.views)}
                </div>
                <div className="text-xs text-text-secondary">Views</div>
              </div>

              <div className="text-center p-3 bg-primary-bg rounded-btn">
                <Heart className="w-5 h-5 text-red-400 mx-auto mb-1" />
                <div className="text-lg font-semibold text-text-primary">
                  {formatNumber(trend.likes)}
                </div>
                <div className="text-xs text-text-secondary">Likes</div>
              </div>

              <div className="text-center p-3 bg-primary-bg rounded-btn">
                <MessageCircle className="w-5 h-5 text-text-secondary mx-auto mb-1" />
                <div className="text-lg font-semibold text-text-primary">
                  {formatNumber(trend.comments)}
                </div>
                <div className="text-xs text-text-secondary">Comments</div>
              </div>

              <div className="text-center p-3 bg-primary-bg rounded-btn">
                <Share className="w-5 h-5 text-text-secondary mx-auto mb-1" />
                <div className="text-lg font-semibold text-text-primary">
                  {formatNumber(trend.shares)}
                </div>
                <div className="text-xs text-text-secondary">Shares</div>
              </div>
            </div>
          </div>

          {/* Author & Date */}
          <div className="flex items-center justify-between p-4 bg-primary-bg rounded-btn">
            <div className="flex items-center space-x-3">
              {trend.author.avatar_url ? (
                <img
                  src={trend.author.avatar_url}
                  alt={trend.author.username}
                  className="w-10 h-10 rounded-full object-cover"
                />
              ) : (
                <div className="w-10 h-10 rounded-full bg-primary-line"></div>
              )}
              <div>
                <div className="text-text-primary font-medium">
                  @{trend.author.username || 'unknown'}
                </div>
                <div className="text-text-secondary text-sm">
                  {formatRelativeTime(trend.create_time)}
                </div>
              </div>
            </div>
            
            {trend.author.is_verified && (
              <div className="bg-primary-accent text-white text-xs px-2 py-1 rounded-btn">
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
