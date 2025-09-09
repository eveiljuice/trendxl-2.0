// TikTok Profile Data Types
export interface TikTokProfile {
  username: string;
  bio: string;
  follower_count: number;
  following_count: number;
  likes_count: number;
  video_count: number;
  avatar_url: string;
  is_verified: boolean;
}

// TikTok Post Data Types
export interface TikTokPost {
  id: string;
  caption: string;
  views: number;
  likes: number;
  comments: number;
  shares: number;
  favorites: number;
  create_time: string;
  video_url: string;
  cover_image_url: string;
  hashtags: string[];
}

// Hashtag Analysis Types
export interface HashtagAnalysis {
  hashtag: string;
  frequency: number;
  relevance_score: number;
}

// Trend Video Types
export interface TrendVideo {
  id: string;
  caption: string;
  views: number;
  likes: number;
  shares: number;
  comments: number;
  create_time: string;
  video_url: string;
  cover_image_url: string;
  hashtag: string;
  author: {
    username: string;
    avatar_url: string;
    is_verified: boolean;
  };
}

// API Response Types
export interface EnsembleApiResponse<T> {
  data: T;
  units_charged: number;
}

export interface GPTAnalysisResponse {
  top_hashtags: string[];
  analysis_summary: string;
}

// App State Types
export interface AppState {
  isLoading: boolean;
  profile: TikTokProfile | null;
  posts: TikTokPost[];
  hashtags: string[];
  trends: TrendVideo[];
  error: string | null;
}

// Component Props Types
export interface ProfileInputProps {
  onSubmit: (profileUrl: string) => void;
  isLoading: boolean;
}

export interface TrendCardProps {
  trend: TrendVideo;
  onClick: (trend: TrendVideo) => void;
}

export interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}
