import React from 'react';
import { Users, Heart, Video, CheckCircle, Target, Tag } from 'lucide-react';
import { TikTokProfile } from '../types';
import { formatNumber } from '../utils';

interface ProfileCardProps {
  profile: TikTokProfile;
}

const ProfileCard: React.FC<ProfileCardProps> = ({ profile }) => {
  return (
    <div className="bg-white rounded-xl sm:rounded-2xl shadow-xl border border-gray-200 p-4 sm:p-6 md:p-8 animate-fade-in hover:shadow-2xl transition-all duration-300">
      <div className="flex flex-col sm:flex-row items-start sm:items-start space-y-4 sm:space-y-0 sm:space-x-6">
        {/* Avatar - адаптивные размеры */}
        <div className="relative flex-shrink-0 w-20 h-20 sm:w-24 sm:h-24 mx-auto sm:mx-0">
          <img
            src={profile.avatar_url || '/default-avatar.png'}
            alt={`${profile.username} avatar`}
            className="w-full h-full rounded-full object-cover bg-gray-50 border-4 border-gray-200 shadow-xl hover:shadow-2xl transition-shadow"
            loading="lazy"
            referrerPolicy="no-referrer"
            crossOrigin="anonymous"
            onError={(e) => {
              const target = e.target as HTMLImageElement;
              console.warn(`❌ Failed to load avatar for @${profile.username}: ${target.src}`);
              // Avoid infinite loop if default avatar also fails
              if (target.src.includes('/default-avatar.png')) {
                console.warn('❌ Default avatar also failed, using CSS fallback');
                target.style.display = 'none';
                // Show initials as fallback
                const parentDiv = target.parentElement;
                const fallbackDiv = parentDiv?.querySelector('.avatar-fallback') as HTMLDivElement;
                if (fallbackDiv) {
                  fallbackDiv.style.display = 'flex';
                }
                return;
              }
              target.src = '/default-avatar.png';
            }}
            onLoad={(e) => {
              console.log(`✅ Avatar loaded successfully for @${profile.username}`);
              // Hide fallback when image loads
              const target = e.target as HTMLImageElement;
              const parentDiv = target.parentElement;
              const fallbackDiv = parentDiv?.querySelector('.avatar-fallback') as HTMLDivElement;
              if (fallbackDiv) {
                fallbackDiv.style.display = 'none';
              }
            }}
          />
          {/* Fallback initials display */}
          <div 
            className="avatar-fallback absolute inset-0 w-full h-full rounded-full bg-gradient-to-br from-gray-400 to-gray-600 flex items-center justify-center text-white text-xl font-bold border-4 border-gray-200"
            style={{ display: 'none' }}
          >
            {profile.username.slice(0, 2).toUpperCase()}
          </div>
          {profile.is_verified && (
            <div className="absolute -bottom-1 -right-1 bg-black rounded-full p-0.5 sm:p-1 shadow-sm">
              <CheckCircle className="w-3 h-3 sm:w-4 sm:h-4 text-white" />
            </div>
          )}
        </div>

        {/* Profile Info - адаптивные размеры */}
        <div className="flex-1 min-w-0 text-center sm:text-left">
          <div className="flex flex-col sm:flex-row items-center sm:items-center space-y-1 sm:space-y-0 sm:space-x-2 mb-2">
            <h3 className="text-xl sm:text-2xl font-bold text-black truncate font-orbitron">
              @{profile.username}
            </h3>
            {profile.is_verified && (
              <CheckCircle className="w-5 h-5 sm:w-6 sm:h-6 text-black flex-shrink-0" />
            )}
          </div>
          
          {profile.bio && (
            <p className="text-gray-600 text-sm sm:text-base mb-4 sm:mb-6 line-clamp-3 font-inter leading-relaxed">
              {profile.bio}
            </p>
          )}

          {/* Niche Analysis Section - адаптивные размеры */}
          {profile.niche_category && profile.niche_category !== "General Content Creator" && (
            <div className="mb-4 sm:mb-6 p-3 sm:p-4 bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg sm:rounded-xl border border-gray-200 shadow-sm">
              <div className="flex items-center space-x-2 sm:space-x-3 mb-2 sm:mb-3">
                <div className="w-7 h-7 sm:w-8 sm:h-8 bg-black rounded-full flex items-center justify-center flex-shrink-0">
                  <Target className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-white" />
                </div>
                <span className="font-bold text-black text-sm sm:text-base font-orbitron">Niche Analysis</span>
              </div>
              
              <div className="space-y-1.5 sm:space-y-2">
                <div>
                  <span className="text-xs sm:text-sm text-gray-500">Category: </span>
                  <span className="text-sm sm:text-base text-black font-semibold">{profile.niche_category}</span>
                </div>
                
                {profile.niche_description && (
                    <p className="text-xs sm:text-sm text-gray-600 leading-relaxed font-inter">
                      {profile.niche_description}
                    </p>
                )}
                
                {profile.key_topics && profile.key_topics.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {profile.key_topics.slice(0, 5).map((topic, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-2 py-1 sm:px-3 sm:py-1.5 rounded-full text-xs bg-white border border-gray-200 text-gray-700 font-medium shadow-sm hover:shadow-md transition-shadow"
                      >
                        <Tag className="w-2.5 h-2.5 sm:w-3 sm:h-3 mr-1" />
                        {topic}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Stats - адаптивная сетка */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 sm:gap-4 md:gap-6">
            <div className="text-center bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg sm:rounded-xl p-2 sm:p-3 md:p-4 border border-gray-200">
              <div className="flex items-center justify-center mb-1 sm:mb-2">
                <div className="w-6 h-6 sm:w-7 sm:h-7 md:w-8 md:h-8 bg-black rounded-full flex items-center justify-center">
                  <Users className="w-3 h-3 sm:w-3.5 sm:h-3.5 md:w-4 md:h-4 text-white" />
                </div>
              </div>
              <div className="text-base sm:text-lg md:text-xl font-bold text-black font-orbitron">
                {formatNumber(profile.follower_count)}
              </div>
              <div className="text-xs sm:text-sm text-gray-600 font-medium">Followers</div>
            </div>

            <div className="text-center bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg sm:rounded-xl p-2 sm:p-3 md:p-4 border border-gray-200">
              <div className="flex items-center justify-center mb-1 sm:mb-2">
                <div className="w-6 h-6 sm:w-7 sm:h-7 md:w-8 md:h-8 bg-gray-600 rounded-full flex items-center justify-center">
                  <Users className="w-3 h-3 sm:w-3.5 sm:h-3.5 md:w-4 md:h-4 text-white" />
                </div>
              </div>
              <div className="text-base sm:text-lg md:text-xl font-bold text-black font-orbitron">
                {formatNumber(profile.following_count)}
              </div>
              <div className="text-xs sm:text-sm text-gray-600 font-medium">Following</div>
            </div>

            <div className="text-center bg-gradient-to-br from-red-50 to-pink-50 rounded-lg sm:rounded-xl p-2 sm:p-3 md:p-4 border border-red-200">
              <div className="flex items-center justify-center mb-1 sm:mb-2">
                <div className="w-6 h-6 sm:w-7 sm:h-7 md:w-8 md:h-8 bg-red-500 rounded-full flex items-center justify-center">
                  <Heart className="w-3 h-3 sm:w-3.5 sm:h-3.5 md:w-4 md:h-4 text-white" fill="currentColor" />
                </div>
              </div>
              <div className="text-base sm:text-lg md:text-xl font-bold text-red-600 font-orbitron">
                {formatNumber(profile.likes_count)}
              </div>
              <div className="text-xs sm:text-sm text-red-500 font-medium">Likes</div>
            </div>

            <div className="text-center bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg sm:rounded-xl p-2 sm:p-3 md:p-4 border border-blue-200">
              <div className="flex items-center justify-center mb-1 sm:mb-2">
                <div className="w-6 h-6 sm:w-7 sm:h-7 md:w-8 md:h-8 bg-blue-500 rounded-full flex items-center justify-center">
                  <Video className="w-3 h-3 sm:w-3.5 sm:h-3.5 md:w-4 md:h-4 text-white" />
                </div>
              </div>
              <div className="text-base sm:text-lg md:text-xl font-bold text-blue-600 font-orbitron">
                {formatNumber(profile.video_count)}
              </div>
              <div className="text-xs sm:text-sm text-blue-500 font-medium">Videos</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfileCard;
