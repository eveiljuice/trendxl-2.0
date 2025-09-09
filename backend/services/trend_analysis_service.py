"""
Main Trend Analysis Service - orchestrates the complete trend discovery process
Updated for official Ensemble Data SDK compatibility
"""
import asyncio
import logging
from typing import List, Dict, Any, Optional
from models import (
    TikTokProfile, 
    TikTokPost, 
    TrendVideo,
    TikTokAuthor,
    TrendAnalysisResponse
)
from services.ensemble_service import EnsembleService
from services.openai_service import OpenAIService
from services.cache_service import cache_service
from utils import extract_tiktok_username
from config import settings

logger = logging.getLogger(__name__)

class TrendAnalysisService:
    """Main service orchestrating trend analysis workflow"""
    
    def __init__(self):
        """Initialize all required services with official SDK integration"""
        self.ensemble_service = EnsembleService()
        self.openai_service = OpenAIService()
        logger.info("✅ Trend Analysis Service initialized with official Ensemble Data SDK")
    
    async def analyze_profile_trends(
        self, 
        profile_input: str,
        max_hashtags: int = 5,
        videos_per_hashtag: int = 2
    ) -> TrendAnalysisResponse:
        """
        Complete trend analysis workflow
        
        Args:
            profile_input: TikTok profile URL or username
            max_hashtags: Maximum number of hashtags to analyze
            videos_per_hashtag: Number of trending videos per hashtag
            
        Returns:
            TrendAnalysisResponse with complete analysis results
            
        Raises:
            Exception: If analysis fails
        """
        username = extract_tiktok_username(profile_input)
        logger.info(f"🚀 Starting trend analysis for profile: @{username}")
        
        try:
            # Step 1: Get profile information (with caching)
            logger.info("📊 Step 1: Fetching profile information...")
            profile = await self._get_cached_profile(username)
            
            # Step 2: Get user's recent posts (with caching)  
            logger.info("📱 Step 2: Loading recent posts...")
            posts = await self._get_cached_posts(username, settings.max_posts_per_user)
            
            if not posts:
                raise Exception(f"No posts found for user @{username}")
            
            # Step 3: Analyze posts with AI to extract trending hashtags
            logger.info("🤖 Step 3: Analyzing posts with AI...")
            analysis = await self.openai_service.analyze_posts_for_hashtags(
                posts, profile.bio
            )
            hashtags = analysis.top_hashtags[:max_hashtags]
            
            if not hashtags:
                raise Exception("No hashtags extracted from analysis")
            
            logger.info(f"✅ Extracted hashtags: {hashtags}")
            
            # Step 4: Search trending videos for each hashtag using official SDK
            logger.info("🔥 Step 4: Searching trending videos by hashtags...")
            trends = await self._search_trending_videos_optimized(
                hashtags, videos_per_hashtag
            )
            
            if not trends:
                logger.warning("⚠️ No trends found for extracted hashtags, trying popular backup hashtags...")
                # Try with popular backup hashtags if no trends found
                backup_hashtags = ['fyp', 'viral', 'trending', 'foryou', 'tiktok']
                trends = await self._search_trending_videos_optimized(backup_hashtags, videos_per_hashtag)
                
                if not trends:
                    # Real error handling without mock data
                    logger.error("❌ No trending videos found for any hashtags including backups")
                    raise Exception(
                        f"Unable to find trending content for profile @{username}. "
                        f"This could be due to: 1) Profile content is too niche, "
                        f"2) API rate limits exceeded, 3) Temporary service issues. "
                        f"Please try again later or with a different profile."
                    )
            
            # Sort trends by engagement and limit results
            sorted_trends = sorted(
                trends, 
                key=lambda t: t.views + t.likes * 10, 
                reverse=True
            )[:10]  # Top 10 trends
            
            logger.info(f"✅ Analysis completed! Found {len(sorted_trends)} trending videos")
            
            # Cache the complete analysis result
            await self._cache_analysis_result(
                username, profile, posts, hashtags, sorted_trends, analysis.analysis_summary
            )
            
            return TrendAnalysisResponse(
                profile=profile,
                posts=posts,
                hashtags=hashtags,
                trends=sorted_trends,
                analysis_summary=analysis.analysis_summary
            )
            
        except Exception as e:
            logger.error(f"❌ Trend analysis failed for @{username}: {e}")
            raise Exception(f"Analysis failed for @{username}: {str(e)}")
    
    async def _get_cached_profile(self, username: str) -> TikTokProfile:
        """Get profile with caching"""
        cache_key = f"profile:{username}"
        
        # Try to get from cache
        cached_profile = await cache_service.get("profile", username)
        if cached_profile:
            logger.info(f"📋 Using cached profile for @{username}")
            return TikTokProfile(**cached_profile)
        
        # Fetch from API
        profile = await self.ensemble_service.get_profile(username)
        
        # Cache the result
        await cache_service.set("profile", username, profile.model_dump())
        
        return profile
    
    async def _get_cached_posts(self, username: str, count: int) -> List[TikTokPost]:
        """Get posts with caching"""
        cache_key = f"posts:{username}:{count}"
        
        # Try to get from cache
        cached_posts = await cache_service.get("posts", cache_key)
        if cached_posts:
            logger.info(f"📱 Using cached posts for @{username}")
            return [TikTokPost(**post) for post in cached_posts]
        
        # Fetch from API
        posts = await self.ensemble_service.get_posts(username, count)
        
        # Cache the result
        await cache_service.set("posts", cache_key, [post.model_dump() for post in posts])
        
        return posts
    
    async def _search_trending_videos_optimized(
        self, 
        hashtags: List[str], 
        videos_per_hashtag: int
    ) -> List[TrendVideo]:
        """
        Search trending videos for multiple hashtags using optimized official SDK calls
        
        Args:
            hashtags: List of hashtags to search
            videos_per_hashtag: Number of videos per hashtag
            
        Returns:
            List of TrendVideo objects
        """
        all_trends = []
        
        # Process hashtags with optimized delay based on official SDK recommendations
        for i, hashtag in enumerate(hashtags):
            try:
                logger.info(f"🔍 Searching hashtag: #{hashtag} ({i + 1}/{len(hashtags)})")
                
                # Check cache first with improved key structure
                cache_key = f"hashtag_trends:{hashtag}:{videos_per_hashtag}:7d"
                cached_videos = await cache_service.get("trends", cache_key)
                
                if cached_videos:
                    logger.info(f"🎯 Using cached videos for #{hashtag}")
                    trend_videos = [
                        self._post_to_trend_video(TikTokPost(**post), hashtag)
                        for post in cached_videos
                    ]
                else:
                    # Search new videos using official SDK with optimized parameters
                    logger.debug(f"📡 Fetching fresh data for #{hashtag}")
                    posts = await self.ensemble_service.search_hashtag_posts(
                        hashtag=hashtag,
                        count=min(videos_per_hashtag * 2, 20),  # Optimized count, max 20
                        period=7,  # Last 7 days for trending content
                        sorting=1  # Sort by likes (highest engagement)
                    )
                    
                    if not posts:
                        logger.warning(f"⚠️ No posts found for hashtag #{hashtag}")
                        continue
                    
                    # Convert to TrendVideo objects with quality filtering
                    quality_posts = [p for p in posts if p.views > 100]  # Basic quality filter
                    selected_posts = (quality_posts or posts)[:videos_per_hashtag]
                    
                    trend_videos = [
                        self._post_to_trend_video(post, hashtag)
                        for post in selected_posts
                    ]
                    
                    # Cache the results with shorter TTL for trending content
                    await cache_service.set(
                        "trends", 
                        cache_key, 
                        [post.model_dump() for post in selected_posts],
                        ttl=settings.cache_trends_ttl
                    )
                    
                    logger.debug(f"✅ Found {len(trend_videos)} trend videos for #{hashtag}")
                
                all_trends.extend(trend_videos)
                
                # Add optimized delay between requests based on official SDK recommendations
                if i < len(hashtags) - 1:
                    await asyncio.sleep(settings.ensemble_request_delay)
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to search hashtag #{hashtag}: {e}")
                # Continue with other hashtags instead of failing completely
                continue
        
        logger.info(f"🎯 Total trending videos found: {len(all_trends)} across {len(hashtags)} hashtags")
        return all_trends
    
    def _post_to_trend_video(self, post: TikTokPost, hashtag: str) -> TrendVideo:
        """Convert TikTokPost to TrendVideo"""
        return TrendVideo(
            id=post.id,
            caption=post.caption,
            views=post.views,
            likes=post.likes,
            shares=post.shares,
            comments=post.comments,
            create_time=post.create_time,
            video_url=post.video_url,
            cover_image_url=post.cover_image_url,
            hashtag=hashtag,
            author=TikTokAuthor()  # Will be filled if available
        )
    
    async def _cache_analysis_result(
        self,
        username: str,
        profile: TikTokProfile,
        posts: List[TikTokPost],
        hashtags: List[str],
        trends: List[TrendVideo],
        analysis_summary: str
    ) -> None:
        """Cache complete analysis result"""
        try:
            analysis_data = {
                "profile": profile.model_dump(),
                "posts": [post.model_dump() for post in posts],
                "hashtags": hashtags,
                "trends": [trend.model_dump() for trend in trends],
                "analysis_summary": analysis_summary
            }
            
            await cache_service.set(
                "analysis", 
                username, 
                analysis_data, 
                ttl=settings.cache_trends_ttl
            )
            
            logger.info(f"💾 Cached complete analysis for @{username}")
            
        except Exception as e:
            logger.warning(f"Failed to cache analysis result: {e}")
    
    async def get_cached_analysis(self, username: str) -> Optional[TrendAnalysisResponse]:
        """Get cached analysis result"""
        try:
            cached_data = await cache_service.get("analysis", username)
            if not cached_data:
                return None
            
            return TrendAnalysisResponse(
                profile=TikTokProfile(**cached_data["profile"]),
                posts=[TikTokPost(**post) for post in cached_data["posts"]],
                hashtags=cached_data["hashtags"],
                trends=[TrendVideo(**trend) for trend in cached_data["trends"]],
                analysis_summary=cached_data.get("analysis_summary", "")
            )
            
        except Exception as e:
            logger.warning(f"Failed to get cached analysis for @{username}: {e}")
            return None
    
    async def get_profile_only(self, username: str) -> TikTokProfile:
        """Get profile information only"""
        return await self._get_cached_profile(username)
    
    async def get_posts_only(
        self, 
        username: str, 
        count: int = 20, 
        cursor: Optional[str] = None
    ) -> List[TikTokPost]:
        """Get posts only"""
        if cursor:
            # Don't cache paginated results
            return await self.ensemble_service.get_posts(username, count, cursor)
        else:
            return await self._get_cached_posts(username, count)
    
    async def search_hashtag_only(
        self, 
        hashtag: str, 
        count: int = 10, 
        period: int = 7, 
        sorting: int = 1
    ) -> List[TikTokPost]:
        """
        Search hashtag posts using official SDK with optimized caching
        
        Args:
            hashtag: Hashtag to search (without #)
            count: Number of posts to fetch
            period: Search period in days
            sorting: Sort order (0=relevance, 1=likes)
            
        Returns:
            List of TikTokPost objects
        """
        clean_hashtag = hashtag.replace('#', '').strip()
        cache_key = f"hashtag_search:{clean_hashtag}:{count}:{period}:{sorting}"
        
        logger.info(f"🔍 Searching hashtag #{clean_hashtag} (count={count}, period={period}d)")
        
        # Try cache first
        cached_posts = await cache_service.get("hashtag", cache_key)
        if cached_posts:
            logger.info(f"🎯 Using cached results for #{clean_hashtag}")
            return [TikTokPost(**post) for post in cached_posts]
        
        # Fetch from API using official SDK
        posts = await self.ensemble_service.search_hashtag_posts(
            hashtag=clean_hashtag, count=count, period=period, sorting=sorting
        )
        
        # Cache results with appropriate TTL
        await cache_service.set(
            "hashtag", 
            cache_key, 
            [post.model_dump() for post in posts],
            ttl=settings.cache_trends_ttl
        )
        
        logger.info(f"✅ Found {len(posts)} posts for #{clean_hashtag}")
        return posts
    
    async def search_users_only(self, query: str, count: int = 10) -> List[TikTokProfile]:
        """
        Search users - NOT SUPPORTED by official Ensemble Data API
        
        Args:
            query: Search query for users
            count: Number of users to fetch
            
        Returns:
            Empty list (user search not supported by official API)
            
        Note:
            According to official Ensemble Data documentation, user search is not available.
            Consider using direct profile lookup by username instead.
        """
        logger.warning(f"⚠️ User search not supported by Ensemble Data API for query: '{query}'")
        logger.info(f"💡 Consider searching for specific usernames directly using get_profile_only()")
        
        # Return empty list as user search is not supported by official API
        return []

# Global trend analysis service instance
trend_service = TrendAnalysisService()
