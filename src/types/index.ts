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
  
  // Niche analysis fields from Perplexity API
  niche_category?: string;
  niche_description?: string;
  key_topics?: string[];
  target_audience?: string;
  content_style?: string;
}

// TikTok Author Type
export interface TikTokAuthor {
  username: string;
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
  // Support for multiple images (for image posts or additional video thumbnails)
  images: string[];
  hashtags: string[];
  author: TikTokAuthor;
  tiktok_url: string; // Direct TikTok link
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
  // Support for multiple images (for image posts or additional video thumbnails)
  images: string[];
  hashtag: string;
  author: TikTokAuthor;
  tiktok_url?: string; // Direct TikTok link for better video access
  relevance_score?: number; // Content relevance score from GPT-4 Vision (0.0-1.0)
}

// Token Usage Types
export interface TokenUsage {
  openai_tokens: number;
  openai_prompt_tokens: number;
  openai_completion_tokens: number;
  perplexity_tokens: number;
  perplexity_prompt_tokens: number;
  perplexity_completion_tokens: number;
  ensemble_units: number;
  total_cost_estimate: number;
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
  tokenUsage: TokenUsage | null;
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

// Creative Center Hashtag Types
export interface CreativeCenterHashtag {
  name: string;
  url: string;
  volume?: number;
  growth?: number;
  score?: number;
}

export interface NicheHashtagRequest {
  niche: string;
  country: string;
  language: string;
  limit: number;
}

export interface NicheHashtagResponse {
  niche: string;
  country: string;
  language: string;
  category: string;
  total_found: number;
  hashtags: CreativeCenterHashtag[];
}

// Advanced Creative Center Analysis Types
export interface CreativeCenterAnalysisRequest {
  profile_url: string;
  country: string;
  language: string;
  hashtag_limit: number;
  videos_per_hashtag: number;
  auto_detect_geo: boolean;
}

export interface CreativeCenterAnalysisResponse {
  profile: TikTokProfile;
  creative_center_hashtags: CreativeCenterHashtag[];
  trends: TrendVideo[];
  analysis_summary: string;
  metadata: Record<string, any>;
}
