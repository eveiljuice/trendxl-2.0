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
    hashtag: str
    author: TikTokAuthor = Field(default_factory=TikTokAuthor)


class GPTAnalysisResponse(BaseModel):
    """Response from GPT analysis"""
    top_hashtags: List[str]
    analysis_summary: str = ""


class TrendAnalysisRequest(BaseModel):
    """Request model for trend analysis"""
    profile_url: str = Field(..., description="TikTok profile URL or username")


class TrendAnalysisResponse(BaseModel):
    """Complete trend analysis response"""
    profile: TikTokProfile
    posts: List[TikTokPost]
    hashtags: List[str]
    trends: List[TrendVideo]
    analysis_summary: str = ""


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
