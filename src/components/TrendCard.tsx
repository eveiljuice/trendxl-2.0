import React, { useState, useEffect } from 'react';
import { Play, Heart, MessageCircle, Share, Eye, Target } from 'lucide-react';
import { TrendVideo } from '../types';
import { formatNumber, formatRelativeTime, truncateText } from '../utils';

interface TrendCardProps {
  trend: TrendVideo;
  onClick: (trend: TrendVideo) => void;
}

const TrendCard: React.FC<TrendCardProps> = ({ trend, onClick }) => {
  // Get all available images (cover + additional images)
  const allImages = [
    trend.cover_image_url,
    ...(trend.images || [])
  ].filter(Boolean);
  
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imageError, setImageError] = useState(false);
  const [retryCount, setRetryCount] = useState(0);
  const [currentImageSrc, setCurrentImageSrc] = useState(allImages[0] || '');
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);
  const [preloadedImages, setPreloadedImages] = useState<Set<string>>(new Set());
  
  const hasMultipleImages = allImages.length > 1;

  // Update currentImageSrc when trend changes
  useEffect(() => {
    const firstImage = allImages[0] || '';
    setCurrentImageSrc(firstImage);
    setSelectedImageIndex(0);
    setImageLoaded(false);
    setImageError(false);
    setRetryCount(0);
    
    // Debug: Log image information
    console.log('TrendCard Debug:', {
      id: trend.id,
      cover_image_url: trend.cover_image_url,
      images: trend.images,
      allImages: allImages,
      firstImage: firstImage
    });
  }, [trend.cover_image_url, trend.images]);

  // Preload alternative images for faster fallback
  useEffect(() => {
    const preloadImage = (src: string) => {
      if (!src || preloadedImages.has(src)) return;
      
      const img = new Image();
      img.crossOrigin = 'anonymous';
      img.onload = () => {
        setPreloadedImages(prev => new Set([...prev, src]));
        console.log(`✅ Preloaded image: ${src.substring(0, 50)}...`);
      };
      img.onerror = () => {
        console.log(`❌ Failed to preload: ${src.substring(0, 50)}...`);
      };
      img.src = src;
    };

    // Preload first few alternative images
    if (currentImageSrc) {
      for (let i = 1; i <= 2; i++) {
        const altSrc = getAlternativeImageSrc(currentImageSrc, i);
        if (altSrc && altSrc !== currentImageSrc) {
          preloadImage(altSrc);
        }
      }
    }

    // Preload next images in carousel (if available)
    if (hasMultipleImages && selectedImageIndex < allImages.length - 1) {
      const nextImage = allImages[selectedImageIndex + 1];
      if (nextImage) {
        preloadImage(nextImage);
      }
    }
  }, [currentImageSrc, selectedImageIndex, hasMultipleImages, allImages]);

  const handleClick = () => {
    onClick(trend);
  };

  // Enhanced function to get alternative image sources with better CORS handling
  const getAlternativeImageSrc = (originalSrc: string, attempt: number): string => {
    if (!originalSrc) return '';
    
    // Attempt different strategies for loading images
    switch (attempt) {
      case 0:
        return originalSrc; // Original URL
      case 1:
        // Try optimized image proxy with webP support and proper sizing
        if (originalSrc.startsWith('http')) {
          return `https://images.weserv.nl/?url=${encodeURIComponent(originalSrc)}&w=400&h=600&output=webp&q=85&fit=cover&a=attention`;
        }
        return originalSrc;
      case 2:
        // Try alternative proxy without webP
        if (originalSrc.startsWith('http')) {
          return `https://images.weserv.nl/?url=${encodeURIComponent(originalSrc)}&w=400&h=600&fit=cover&a=attention`;
        }
        return originalSrc;
      case 3:
        // Try direct access with cache busting and smaller size
        const cacheUrl = originalSrc.includes('?') 
          ? `${originalSrc}&t=${Date.now()}&sz=medium` 
          : `${originalSrc}?t=${Date.now()}&sz=medium`;
        return cacheUrl;
      case 4:
        // Try with different TikTok size parameters
        if (originalSrc.includes('tiktok') || originalSrc.includes('bytedance')) {
          return originalSrc.replace(/~\w+x\w+/, '~400x600')
                           .replace(/\?[^?]*$/, '')  // Remove query params
                           + `?${Date.now()}`;
        }
        return originalSrc;
      default:
        return originalSrc;
    }
  };

  // Handle image navigation
  const handleImageChange = (index: number, e: React.MouseEvent) => {
    e.stopPropagation();
    if (index >= 0 && index < allImages.length) {
      setSelectedImageIndex(index);
      setCurrentImageSrc(allImages[index]);
      setImageLoaded(false);
      setImageError(false);
      setRetryCount(0);
    }
  };

  const handleVideoPlay = (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent card click
    
    // Priority: tiktok_url > video_url > constructed TikTok URL
    const videoUrl = trend.tiktok_url || 
                    trend.video_url || 
                    (trend.author.username && trend.id ? 
                      `https://www.tiktok.com/@${trend.author.username}/video/${trend.id}` : null);
    
    if (videoUrl) {
      try {
        // Open video in new tab - TikTok will handle autoplay based on user settings
        const newWindow = window.open(videoUrl, '_blank', 'noopener,noreferrer');
        
        // Check if popup was blocked
        if (!newWindow) {
          // Fallback: navigate to video in current tab
          window.location.href = videoUrl;
        }
      } catch (error) {
        console.error('Failed to open video:', error);
        // Fallback: copy URL to clipboard
        navigator.clipboard?.writeText(videoUrl).then(() => {
          alert('Video URL copied to clipboard: ' + videoUrl);
        }).catch(() => {
          alert('Video URL: ' + videoUrl);
        });
      }
    }
  };

  const hasVideo = !!(trend.tiktok_url || trend.video_url || (trend.author.username && trend.id));

  return (
    <div 
      className="
        card cursor-pointer group h-full flex flex-col
        hover:border-primary-accent/30 hover:shadow-lg hover:shadow-primary-accent/5
        hover:scale-[1.02] active:scale-[0.98]
        transition-all duration-300 ease-out
        animate-fade-in
      "
      onClick={handleClick}
    >
      {/* Video Thumbnail */}
      <div className="relative mb-4 overflow-hidden rounded-card">
        <div className="aspect-[9/16] max-h-64 bg-secondary relative">
          {currentImageSrc && !imageError ? (
            <>
              {/* Loading skeleton */}
              {!imageLoaded && (
                <div className="absolute inset-0 bg-primary-line animate-pulse flex items-center justify-center">
                  <Play className="w-12 h-12 text-text-secondary opacity-50" />
                </div>
              )}
              <img
                src={currentImageSrc}
                alt={`Content thumbnail ${selectedImageIndex + 1}`}
                className={`w-full h-full object-cover transition-opacity duration-300 ${
                  imageLoaded ? 'opacity-100' : 'opacity-0'
                }`}
                onLoad={() => {
                  console.log(`✅ Image loaded successfully: ${currentImageSrc?.substring(0, 50)}...`);
                  setImageLoaded(true);
                  setImageError(false);
                }}
                onError={(e) => {
                  console.log(`❌ Image load error: ${currentImageSrc?.substring(0, 50)}...`, e);
                  
                  // Try alternative image sources up to 5 attempts (including original)
                  if (retryCount < 5) {
                    const nextAttempt = retryCount + 1;
                    const alternativeSrc = getAlternativeImageSrc(allImages[selectedImageIndex], nextAttempt);
                    
                    console.log(`🔄 Trying alternative source (attempt ${nextAttempt}): ${alternativeSrc?.substring(0, 50)}...`);
                    
                    if (alternativeSrc && alternativeSrc !== currentImageSrc) {
                      // Prioritize preloaded images for faster loading
                      const delay = preloadedImages.has(alternativeSrc) ? 50 : 500 * nextAttempt;
                      
                      setTimeout(() => {
                        setRetryCount(nextAttempt);
                        setCurrentImageSrc(alternativeSrc);
                        setImageLoaded(preloadedImages.has(alternativeSrc)); // Skip loading if preloaded
                      }, delay);
                    } else {
                      console.log(`💥 No more alternatives, showing fallback`);
                      setImageError(true);
                      setImageLoaded(true);
                    }
                  } else {
                    console.log(`💥 Max retry attempts reached, showing fallback`);
                    setImageError(true);
                    setImageLoaded(true);
                  }
                }}
                crossOrigin="anonymous"
                loading="lazy"
                referrerPolicy="no-referrer"
              />
            </>
          ) : (
            <div className="w-full h-full flex flex-col items-center justify-center bg-gradient-to-br from-primary-surface to-primary-line">
              <Play className="w-12 h-12 text-text-secondary mb-2" />
              <span className="text-xs text-text-secondary text-center px-2">
                {!currentImageSrc ? 'No image available' :
                 imageError ? 'Preview unavailable' : 
                 retryCount > 0 ? `Loading... (${retryCount + 1}/6)` : 
                 'Loading preview...'}
              </span>
              {/* Debug info */}
              {process.env.NODE_ENV === 'development' && (
                <div className="text-xs text-red-400 mt-1 text-center max-w-full overflow-hidden">
                  <div>Cover: {trend.cover_image_url ? '✅' : '❌'}</div>
                  <div>Images: {trend.images?.length || 0}</div>
                  <div>Current: {currentImageSrc ? '✅' : '❌'}</div>
                </div>
              )}
            </div>
          )}

          {/* Multi-Image Navigation Dots */}
          {hasMultipleImages && (
            <div className="absolute top-3 right-3 flex space-x-1">
              {allImages.map((_, index) => (
                <button
                  key={index}
                  onClick={(e) => handleImageChange(index, e)}
                  className={`
                    w-2 h-2 rounded-full transition-all duration-200
                    ${index === selectedImageIndex 
                      ? 'bg-white scale-125 shadow-lg' 
                      : 'bg-white/50 hover:bg-white/80'
                    }
                  `}
                  aria-label={`View image ${index + 1}`}
                />
              ))}
            </div>
          )}

          {/* Top Row - Left: Image Counter or Relevance Score */}
          <div className="absolute top-3 left-3 z-20">
            {hasMultipleImages ? (
              <div className="bg-black/70 text-white text-xs px-2 py-1 rounded-full backdrop-blur-sm mb-2">
                {selectedImageIndex + 1}/{allImages.length}
              </div>
            ) : null}
            
            {/* Relevance Score Badge */}
            {trend.relevance_score && trend.relevance_score > 0 && (
              <div className={`flex items-center space-x-1 px-2 py-1 rounded-full backdrop-blur-sm ${
                trend.relevance_score >= 0.8 ? 'bg-green-500/90' :
                trend.relevance_score >= 0.6 ? 'bg-yellow-500/90' :
                trend.relevance_score >= 0.4 ? 'bg-orange-500/90' :
                'bg-red-500/90'
              }`}>
                <Target className="w-3 h-3 text-white" />
                <span className="text-white text-xs font-medium">
                  {Math.round(trend.relevance_score * 100)}%
                </span>
              </div>
            )}
          </div>

          {/* Top Right - Hashtag Badge */}
          <div className="absolute top-3 right-3 z-10">
            <span className="
              bg-primary-accent/90 backdrop-blur-sm text-white text-xs font-medium
              px-3 py-1.5 rounded-full border border-white/20
              shadow-lg
            ">
              #{trend.hashtag}
            </span>
          </div>
          
          {/* Play Button Overlay - Only show button, minimal background */}
          {hasVideo && (
            <div className="absolute inset-0 flex items-center justify-center">
              <button
                onClick={handleVideoPlay}
                className="
                  bg-black/60 backdrop-blur-md border border-white/30
                  rounded-full p-4 
                  hover:bg-black/80 hover:border-white/50
                  hover:scale-110 active:scale-95
                  transition-all duration-200 ease-out
                  group/play
                  focus:outline-none focus:ring-2 focus:ring-white/50
                  shadow-lg
                "
                aria-label="Play video in new tab"
                title="Play video in new tab"
              >
                <Play 
                  className="w-8 h-8 text-white ml-1 group-hover/play:text-white drop-shadow-sm" 
                  fill="currentColor" 
                />
              </button>
            </div>
          )}

          {/* Subtle gradient overlay for better text readability */}
          <div className="absolute bottom-0 left-0 right-0 h-1/3 bg-gradient-to-t from-black/60 to-transparent pointer-events-none" />
        </div>
      </div>

      {/* Content */}
      <div className="space-y-3 flex-1 flex flex-col">
        {/* Caption */}
        {trend.caption && (
          <p className="text-text-primary text-sm leading-relaxed max-h-[60px] overflow-hidden">
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

         {/* Relevance Info - shown only if relevance score exists */}
         {trend.relevance_score && trend.relevance_score > 0 && (
           <div className="flex items-center justify-between text-xs text-text-secondary pt-2 border-t border-primary-line/50">
             <div className="flex items-center space-x-1">
               <Target className="w-3 h-3" />
               <span>
                 {trend.relevance_score >= 0.8 ? 'Highly relevant' :
                  trend.relevance_score >= 0.6 ? 'Relevant' :
                  trend.relevance_score >= 0.4 ? 'Somewhat relevant' :
                  'Low relevance'}
               </span>
             </div>
             <span className="text-xs">
               {Math.round(trend.relevance_score * 100)}% match
             </span>
           </div>
         )}

         {/* Author & Date */}
         <div className="flex items-center justify-between pt-2 border-t border-primary-line mt-auto">
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
