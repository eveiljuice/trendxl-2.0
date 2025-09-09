import React from 'react';
import { Users, Heart, Video, CheckCircle } from 'lucide-react';
import { TikTokProfile } from '../types';
import { formatNumber } from '../utils';

interface ProfileCardProps {
  profile: TikTokProfile;
}

const ProfileCard: React.FC<ProfileCardProps> = ({ profile }) => {
  return (
    <div className="card animate-fade-in">
      <div className="flex items-start space-x-6">
        {/* Avatar */}
        <div className="relative flex-shrink-0">
          <img
            src={profile.avatar_url || '/default-avatar.png'}
            alt={`${profile.username} avatar`}
            className="w-20 h-20 rounded-full object-cover bg-primary-line"
            onError={(e) => {
              const target = e.target as HTMLImageElement;
              target.src = '/default-avatar.png';
            }}
          />
          {profile.is_verified && (
            <div className="absolute -bottom-1 -right-1 bg-primary-accent rounded-full p-1">
              <CheckCircle className="w-4 h-4 text-white" />
            </div>
          )}
        </div>

        {/* Profile Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-2 mb-2">
            <h3 className="text-xl font-bold text-text-primary truncate">
              @{profile.username}
            </h3>
            {profile.is_verified && (
              <CheckCircle className="w-5 h-5 text-primary-accent flex-shrink-0" />
            )}
          </div>
          
          {profile.bio && (
            <p className="text-text-secondary text-sm mb-4 line-clamp-2">
              {profile.bio}
            </p>
          )}

          {/* Stats */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="flex items-center justify-center mb-1">
                <Users className="w-4 h-4 text-text-secondary mr-1" />
              </div>
              <div className="text-lg font-semibold text-text-primary">
                {formatNumber(profile.follower_count)}
              </div>
              <div className="text-xs text-text-secondary">Followers</div>
            </div>

            <div className="text-center">
              <div className="flex items-center justify-center mb-1">
                <Users className="w-4 h-4 text-text-secondary mr-1" />
              </div>
              <div className="text-lg font-semibold text-text-primary">
                {formatNumber(profile.following_count)}
              </div>
              <div className="text-xs text-text-secondary">Following</div>
            </div>

            <div className="text-center">
              <div className="flex items-center justify-center mb-1">
                <Heart className="w-4 h-4 text-text-secondary mr-1" />
              </div>
              <div className="text-lg font-semibold text-text-primary">
                {formatNumber(profile.likes_count)}
              </div>
              <div className="text-xs text-text-secondary">Likes</div>
            </div>

            <div className="text-center">
              <div className="flex items-center justify-center mb-1">
                <Video className="w-4 h-4 text-text-secondary mr-1" />
              </div>
              <div className="text-lg font-semibold text-text-primary">
                {formatNumber(profile.video_count)}
              </div>
              <div className="text-xs text-text-secondary">Videos</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfileCard;
