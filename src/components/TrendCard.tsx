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
        // Open video in new tab with specific window features
        const newWindow = window.open(
          videoUrl, 
          '_blank', 
          'noopener,noreferrer,width=800,height=900,menubar=no,toolbar=no,location=yes'
        );
        
        // Check if popup was blocked
        if (!newWindow || newWindow.closed || typeof newWindow.closed === 'undefined') {
          // Show user-friendly message instead of redirecting
          const message = `Please allow popups to open videos.\n\nVideo link: ${videoUrl}`;
          
          // Try to copy to clipboard
          navigator.clipboard?.writeText(videoUrl).then(() => {
            alert(message + '\n\n✅ Link copied to clipboard!');
          }).catch(() => {
            alert(message + '\n\nPlease copy this link manually.');
          });
        }
      } catch (error) {
        console.error('Failed to open video:', error);
        // Fallback: copy URL to clipboard
        navigator.clipboard?.writeText(videoUrl).then(() => {
          alert('Video link copied to clipboard: ' + videoUrl);
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
        bg-white rounded-xl sm:rounded-2xl shadow-lg border border-gray-200 cursor-pointer group h-full flex flex-col
        hover:border-gray-300 hover:shadow-2xl 
        hover:scale-[1.02] active:scale-[0.98]
        transition-all duration-300 ease-out
        animate-fade-in overflow-hidden
      "
      onClick={handleClick}
    >
      {/* Video Thumbnail - адаптивная высота */}
      <div className="relative overflow-hidden">
        <div className="aspect-[9/16] max-h-64 sm:max-h-72 md:max-h-80 bg-gray-100 relative">
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
            <div className="w-full h-full flex flex-col items-center justify-center bg-gradient-to-br from-gray-100 to-gray-200">
              <Play className="w-12 h-12 text-gray-400 mb-2" />
              <span className="text-xs text-gray-500 text-center px-2">
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

          {/* Multi-Image Navigation Dots - адаптивные размеры */}
          {hasMultipleImages && (
            <div className="absolute bottom-2 sm:bottom-3 right-2 sm:right-3 flex space-x-1 z-10">
              {allImages.map((_, index) => (
                <button
                  key={index}
                  onClick={(e) => handleImageChange(index, e)}
                  className={`
                    w-1.5 h-1.5 sm:w-2 sm:h-2 rounded-full transition-all duration-200
                    ${index === selectedImageIndex 
                      ? 'bg-white/90 scale-125 shadow-sm' 
                      : 'bg-white/40 hover:bg-white/70'
                    }
                  `}
                  aria-label={`View image ${index + 1}`}
                />
              ))}
            </div>
          )}

          {/* Image Counter - адаптивные отступы */}
          {hasMultipleImages && (
            <div className="absolute top-2 sm:top-3 left-2 sm:left-3 z-10">
              <div className="bg-black/50 text-white text-xs px-1.5 py-0.5 sm:px-2 sm:py-1 rounded backdrop-blur-sm">
                {selectedImageIndex + 1}/{allImages.length}
              </div>
            </div>
          )}
          
          {/* Play Button Overlay - адаптивные размеры */}
          {hasVideo && (
            <div className="absolute inset-0 flex items-center justify-center bg-black/20 hover:bg-black/30 transition-all duration-200">
              <button
                onClick={handleVideoPlay}
                className="
                  bg-white/95 backdrop-blur-sm border-2 border-gray-200
                  rounded-full p-3 sm:p-4 
                  hover:bg-white hover:border-gray-300 hover:scale-110 active:scale-95
                  transition-all duration-200 ease-out
                  group/play
                  focus:outline-none focus:ring-2 focus:ring-white/50
                  shadow-xl
                "
                aria-label="Play video in new tab"
                title="Click to open video in new tab"
              >
                  <Play 
                  className="w-6 h-6 sm:w-7 sm:h-7 md:w-8 md:h-8 text-black ml-0.5 sm:ml-1 group-hover/play:text-black" 
                  fill="currentColor" 
                />
              </button>
            </div>
          )}

          {/* Subtle gradient overlay for better text readability */}
          <div className="absolute bottom-0 left-0 right-0 h-1/3 bg-gradient-to-t from-black/60 to-transparent pointer-events-none" />
        </div>
      </div>

      {/* Content - адаптивные отступы */}
      <div className="space-y-2 sm:space-y-3 flex-1 flex flex-col p-3 sm:p-4 md:p-6">
        {/* Caption - адаптивные размеры */}
        {trend.caption && (
          <p className="text-black text-xs sm:text-sm leading-relaxed max-h-[50px] sm:max-h-[60px] overflow-hidden font-inter">
            {truncateText(trend.caption, 120)}
          </p>
        )}

        {/* Hashtag - адаптивные размеры */}
        <div className="flex items-center space-x-1.5 sm:space-x-2">
          <span className="text-xs text-gray-500 hidden sm:inline">Found via:</span>
          <span className="text-xs font-semibold text-blue-600 bg-blue-50 px-1.5 py-0.5 sm:px-2 sm:py-1 rounded-full">
            #{trend.hashtag}
          </span>
        </div>

        {/* Stats - адаптивные размеры */}
        <div className="flex items-center justify-between text-gray-600 text-xs sm:text-sm">
          <div className="flex items-center space-x-2 sm:space-x-3 md:space-x-4 flex-wrap">
            <div className="flex items-center space-x-0.5 sm:space-x-1">
              <Eye className="w-3 h-3 sm:w-4 sm:h-4" />
              <span className="text-xs sm:text-sm">{formatNumber(trend.views)}</span>
            </div>
            <div className="flex items-center space-x-0.5 sm:space-x-1">
              <Heart className="w-3 h-3 sm:w-4 sm:h-4" />
              <span className="text-xs sm:text-sm">{formatNumber(trend.likes)}</span>
            </div>
            <div className="flex items-center space-x-0.5 sm:space-x-1">
              <MessageCircle className="w-3 h-3 sm:w-4 sm:h-4" />
              <span className="text-xs sm:text-sm">{formatNumber(trend.comments)}</span>
            </div>
            <div className="flex items-center space-x-0.5 sm:space-x-1">
              <Share className="w-3 h-3 sm:w-4 sm:h-4" />
              <span className="text-xs sm:text-sm">{formatNumber(trend.shares)}</span>
            </div>
          </div>
        </div>


         {/* Author & Date - адаптивные размеры */}
         <div className="flex items-center justify-between pt-2 sm:pt-3 border-t border-gray-200 mt-auto">
           <div className="flex items-center space-x-1.5 sm:space-x-2 min-w-0 flex-1">
             {trend.author.avatar_url ? (
               <img
                 src={trend.author.avatar_url}
                 alt={trend.author.username}
                 className="w-5 h-5 sm:w-6 sm:h-6 rounded-full object-cover flex-shrink-0"
               />
             ) : (
               <div className="w-5 h-5 sm:w-6 sm:h-6 rounded-full bg-gray-200 flex-shrink-0"></div>
             )}
             <span className="text-gray-600 text-xs sm:text-sm font-medium truncate">
               @{trend.author.username || 'unknown'}
             </span>
           </div>
           <span className="text-gray-500 text-xs flex-shrink-0 ml-2">
             {formatRelativeTime(trend.create_time)}
           </span>
         </div>
      </div>
    </div>
  );
};

export default TrendCard;
