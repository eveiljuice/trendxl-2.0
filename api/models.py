"""
Data models for TrendXL 2.0 Backend
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class TikTokProfile(BaseModel):
    """TikTok user profile model"""
    username: str
    bio: str = ""
    follower_count: int = 0
    following_count: int = 0
    likes_count: int = 0
    video_count: int = 0
    avatar_url: str = ""
    is_verified: bool = False
    # Niche analysis fields
    niche_category: str = ""
    niche_description: str = ""
    key_topics: List[str] = []
    target_audience: str = ""
    content_style: str = ""


class TikTokPost(BaseModel):
    """TikTok post model"""
    id: str
    caption: str = ""
    views: int = 0
    likes: int = 0
    comments: int = 0
    shares: int = 0
    favorites: int = 0
    create_time: str
    video_url: str = ""
    cover_image_url: str = ""
    # Support for multiple images (for image posts or additional video thumbnails)
    images: List[str] = Field(default_factory=list,
                              description="Additional images from the post")
    hashtags: List[str] = []
    author: "TikTokAuthor" = Field(default_factory=lambda: TikTokAuthor())
    tiktok_url: str = ""  # Direct TikTok link


class TikTokAuthor(BaseModel):
    """TikTok video author model"""
    username: str = ""
    avatar_url: str = ""
    is_verified: bool = False


class TrendVideo(BaseModel):
    """Trending video model"""
    id: str
    caption: str = ""
    views: int = 0
    likes: int = 0
    shares: int = 0
    comments: int = 0
    create_time: str
    video_url: str = ""
    cover_image_url: str = ""
    # Support for multiple images (for image posts or additional video thumbnails)
    images: List[str] = Field(default_factory=list,
                              description="Additional images from the post")
    hashtag: str
    author: TikTokAuthor = Field(default_factory=TikTokAuthor)
    # Content relevance analysis
    content_relevance: Optional["ContentRelevanceAnalysis"] = None
    relevance_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Content relevance score for sorting")


class GPTAnalysisResponse(BaseModel):
    """Response from GPT analysis"""
    top_hashtags: List[str]
    analysis_summary: str = ""


class ContentRelevanceAnalysis(BaseModel):
    """Content relevance analysis using GPT-4 Vision"""
    image_description: str
    content_category: str
    relevance_score: float = Field(
        ge=0.0, le=1.0, description="Relevance score from 0.0 to 1.0")
    relevance_explanation: str
    confidence_level: float = Field(
        ge=0.0, le=1.0, description="Confidence in analysis")
    visual_elements: List[str] = Field(
        default_factory=list, description="Key visual elements identified")


class TrendAnalysisRequest(BaseModel):
    """Request model for trend analysis"""
    profile_url: str = Field(..., description="TikTok profile URL or username")


class TokenUsage(BaseModel):
    """Token usage statistics for API calls"""
    openai_tokens: int = Field(
        default=0, description="Total OpenAI tokens used")
    openai_prompt_tokens: int = Field(
        default=0, description="OpenAI prompt tokens")
    openai_completion_tokens: int = Field(
        default=0, description="OpenAI completion tokens")
    perplexity_tokens: int = Field(
        default=0, description="Total Perplexity tokens used")
    perplexity_prompt_tokens: int = Field(
        default=0, description="Perplexity prompt tokens")
    perplexity_completion_tokens: int = Field(
        default=0, description="Perplexity completion tokens")
    ensemble_units: int = Field(
        default=0, description="Ensemble Data units charged")
    total_cost_estimate: float = Field(
        default=0.0, description="Estimated total cost in USD")


class TrendAnalysisResponse(BaseModel):
    """Complete trend analysis response"""
    profile: TikTokProfile
    posts: List[TikTokPost]
    hashtags: List[str]
    trends: List[TrendVideo]
    analysis_summary: str = ""
    token_usage: Optional[TokenUsage] = Field(
        default=None, description="API token usage statistics")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    code: str = "GENERAL_ERROR"
    details: Optional[Dict[str, Any]] = None


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    version: str = "2.0.0"
    services: Dict[str, bool] = {}


class EnsembleApiStats(BaseModel):
    """Ensemble Data API usage statistics"""
    units_charged: int = Field(
        default=0, description="Units charged for this request")
    request_type: str = Field(default="", description="Type of API request")
    timestamp: str = Field(default="", description="Request timestamp")


class ApiResponse(BaseModel):
    """Generic API response wrapper"""
    success: bool = Field(
        default=True, description="Whether the request was successful")
    data: Any = Field(description="Response data")
    stats: Optional[EnsembleApiStats] = Field(
        None, description="API usage statistics")
    message: Optional[str] = Field(None, description="Optional message")
    error: Optional[str] = Field(
        None, description="Error message if success=False")

# Request/Response models for individual endpoints


class ProfileRequest(BaseModel):
    """Request for profile information"""
    username: str = Field(..., description="TikTok username (without @)")


class PostsRequest(BaseModel):
    """Request for user posts"""
    username: str = Field(..., description="TikTok username (without @)")
    count: int = Field(default=20, ge=1, le=50,
                       description="Number of posts to fetch")
    cursor: Optional[str] = Field(None, description="Pagination cursor")


class HashtagSearchRequest(BaseModel):
    """Request for hashtag search"""
    hashtag: str = Field(..., description="Hashtag to search for (without #)")
    count: int = Field(default=10, ge=1, le=50,
                       description="Number of videos to fetch")
    period: int = Field(
        default=7, description="Search period in days (0,1,7,30,90,180)")
    sorting: int = Field(
        default=1, description="Sort order: 0=relevance, 1=likes")


class HashtagSearchResponse(BaseModel):
    """Response for hashtag search with pagination support"""
    posts: List[TikTokPost]
    next_cursor: Optional[int] = Field(
        None, description="Pagination cursor for next page (integer for hashtag search)")
    total_found: Optional[int] = Field(
        None, description="Total number of posts found")
    hashtag: Optional[str] = Field(
        None, description="The hashtag that was searched")


class UserSearchRequest(BaseModel):
    """Request for user search"""
    query: str = Field(..., description="Search query for users")
    count: int = Field(default=10, ge=1, le=50,
                       description="Number of users to fetch")


class UserSearchResponse(BaseModel):
    """Response for user search"""
    users: List[TikTokProfile]


class PostsResponse(BaseModel):
    """Response for user posts with pagination support"""
    posts: List[TikTokPost]
    next_cursor: Optional[str] = Field(
        None, description="Pagination cursor for next page")
    total_posts: Optional[int] = Field(
        None, description="Total number of posts (if available)")


# Creative Center Hashtag Models
class CreativeCenterHashtag(BaseModel):
    """Creative Center hashtag model"""
    name: str = Field(..., description="Hashtag without #")
    url: str = Field(..., description="Direct Creative Center hashtag URL")
    volume: Optional[int] = Field(
        None, description="Search/usage volume if available")
    growth: Optional[float] = Field(
        None, description="Growth metric (0..1) or %")
    score: Optional[float] = Field(
        None, description="Overall score if provided by source")


class NicheHashtagRequest(BaseModel):
    """Request for niche-based hashtag discovery from Creative Center"""
    niche: str = Field(..., description="User niche, e.g., 'Tech Reviews'")
    country: str = Field(
        default="US", description="Region code for Creative Center")
    language: str = Field(
        default="en", description="Language code for Creative Center")
    limit: int = Field(default=10, ge=1, le=25,
                       description="Number of hashtags to return")
    auto_detect_geo: bool = Field(
        default=False, description="Automatically detect user geography")
    profile_data: Optional[Dict[str, Any]] = Field(
        None, description="User profile data for geo detection")


class NicheHashtagResponse(BaseModel):
    """Response for niche-based hashtag discovery"""
    niche: str
    country: str
    language: str
    category: str = Field(description="Creative Center category used")
    total_found: int = Field(
        description="Total hashtags found before filtering")
    hashtags: List[CreativeCenterHashtag] = Field(default_factory=list)


# Advanced Creative Center Analysis Models
class CreativeCenterAnalysisRequest(BaseModel):
    """Request for complete Creative Center + Ensemble analysis"""
    profile_url: str = Field(..., description="TikTok profile URL or username")
    country: str = Field(
        default="US", description="Region code for Creative Center")
    language: str = Field(
        default="en", description="Language code for Creative Center")
    hashtag_limit: int = Field(
        default=5, ge=1, le=10, description="Number of Creative Center hashtags to discover")
    videos_per_hashtag: int = Field(
        default=3, ge=1, le=5, description="Number of videos per hashtag to analyze")
    auto_detect_geo: bool = Field(
        default=True, description="Automatically detect user geography")


class CreativeCenterAnalysisResponse(BaseModel):
    """Complete Creative Center + Ensemble analysis response"""
    profile: TikTokProfile
    creative_center_hashtags: List[CreativeCenterHashtag] = Field(
        default_factory=list)
    trends: List[TrendVideo] = Field(default_factory=list)
    analysis_summary: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)
