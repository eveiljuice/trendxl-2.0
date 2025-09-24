"""
Main Trend Analysis Service - orchestrates the complete trend discovery process
Updated for official Ensemble Data SDK compatibility
"""
import asyncio
import logging
from datetime import datetime, timedelta
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
from services.perplexity_service import perplexity_service
from services.content_relevance_service import content_relevance_service
from services.cache_service import cache_service
from utils import extract_tiktok_username
from config import settings
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class TrendAnalysisService:
    """Main service orchestrating trend analysis workflow"""

    def __init__(self):
        """Initialize all required services with official SDK integration"""
        self.ensemble_service = EnsembleService()
        self.openai_service = OpenAIService()
        logger.info(
            "✅ Trend Analysis Service initialized with official Ensemble Data SDK")

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

            # If we don't have enough videos (target is 10), try to get more
            target_video_count = 10
            if len(trends) < target_video_count:
                logger.info(
                    f"📈 Got {len(trends)} videos, trying to get more (target: {target_video_count})")

                # Try with popular backup hashtags
                backup_hashtags = ['fyp', 'viral', 'trending', 'foryou',
                                   'tiktok', 'dance', 'comedy', 'music', 'lifestyle']
                needed_videos = target_video_count - len(trends)
                videos_per_backup = max(
                    1, needed_videos // len(backup_hashtags))

                logger.info(
                    f"🔄 Searching {videos_per_backup} videos from {len(backup_hashtags)} backup hashtags")
                backup_trends = await self._search_trending_videos_optimized(
                    backup_hashtags, videos_per_backup
                )

                # Combine and deduplicate trends
                all_trends = trends + backup_trends
                seen_ids = set()
                unique_trends = []

                for trend in all_trends:
                    if trend.id not in seen_ids:
                        seen_ids.add(trend.id)
                        unique_trends.append(trend)

                trends = unique_trends[:target_video_count]
                logger.info(
                    f"✅ Final video count after backup search: {len(trends)}")

            if not trends:
                logger.error(
                    "❌ No trending videos found for any hashtags including backups")
                raise Exception(
                    f"Unable to find trending content for profile @{username}. "
                    f"This could be due to: 1) Profile content is too niche, "
                    f"2) API rate limits exceeded, 3) Temporary service issues. "
                    f"Please try again later or with a different profile."
                )

            # Enhanced quality filtering and sorting
            logger.info(
                f"📊 Filtering {len(trends)} trends by quality metrics...")

            # Filter trends by quality criteria
            quality_trends = []
            for trend in trends:
                # Calculate engagement rate
                engagement_rate = (
                    trend.likes + trend.comments + trend.shares) / max(trend.views, 1)

                # Filter 1: Minimum engagement rate (2%+)
                if engagement_rate < 0.02:
                    continue

                # Filter 2: Minimum performance thresholds
                if trend.views < 10000 or trend.likes < 200:
                    continue

                # Filter 3: Freshness - not older than 2 weeks
                if self._days_since_creation(trend.create_time) > 14:
                    continue

                quality_trends.append(trend)

            logger.info(
                f"✅ {len(quality_trends)} trends passed quality filters")

            if not quality_trends:
                # Fallback: if no trends pass quality filters, use relaxed criteria
                logger.warning(
                    "⚠️ No trends passed strict quality filters, using relaxed criteria...")
                quality_trends = [
                    t for t in trends if t.views > 5000 and t.likes > 50][:30]

            # Enhanced sorting with weighted metrics
            engagement_sorted_trends = sorted(
                quality_trends,
                key=lambda t: (
                    t.views * 0.3 +           # Views weight
                    t.likes * 8 +             # Likes are important
                    t.comments * 15 +         # Comments show engagement
                    t.shares * 20 +           # Shares indicate viral potential
                    # Bonus for high engagement rate
                    ((t.likes + t.comments + t.shares) / max(t.views, 1)) * 50000
                ),
                reverse=True
            )[:30]  # Increased from 20 to 30 for better selection

            # Step 5: Analyze content relevance with GPT-4 Vision
            logger.info(
                "🎨 Step 5: Analyzing content relevance with GPT-4 Vision...")
            relevance_sorted_trends = await content_relevance_service.analyze_trends_relevance(
                engagement_sorted_trends,
                profile.niche_category,
                profile.niche_description,
                profile.key_topics
            )

            # Take top 10 most relevant trends
            niche_trends = relevance_sorted_trends[:10]

            # Step 6: Get 10 popular videos to supplement niche-based trends
            logger.info(
                "🔥 Step 6: Getting popular videos for broader appeal...")
            popular_videos = await self.ensemble_service.search_popular_videos(
                count=10,
                period=7  # Last 7 days
            )

            # Convert popular videos to TrendVideo format
            popular_trends = []
            for post in popular_videos:
                try:
                    trend = await self._convert_post_to_trend(post)
                    if trend:
                        popular_trends.append(trend)
                except Exception as e:
                    logger.debug(
                        f"⚠️ Failed to convert popular video to trend: {e}")
                    continue

            # Combine niche trends with popular videos (remove duplicates)
            combined_trends = []
            seen_ids = set()

            # Add niche-based trends first
            for trend in niche_trends:
                if trend.id not in seen_ids:
                    combined_trends.append(trend)
                    seen_ids.add(trend.id)

            # Add popular trends that are not already included
            for trend in popular_trends:
                # Max 20 total
                if trend.id not in seen_ids and len(combined_trends) < 20:
                    combined_trends.append(trend)
                    seen_ids.add(trend.id)

            logger.info(
                f"✅ Analysis completed! Found {len(niche_trends)} niche trends + {len(popular_trends)} popular videos = {len(combined_trends)} total")

            # Cache the complete analysis result
            await self._cache_analysis_result(
                username, profile, posts, hashtags, combined_trends, analysis.analysis_summary
            )

            return TrendAnalysisResponse(
                profile=profile,
                posts=posts,
                hashtags=hashtags,
                trends=combined_trends,
                analysis_summary=analysis.analysis_summary
            )

        except Exception as e:
            logger.error(f"❌ Trend analysis failed for @{username}: {e}")
            raise Exception(f"Analysis failed for @{username}: {str(e)}")

    async def _get_cached_profile(self, username: str) -> TikTokProfile:
        """Get profile with caching and niche analysis"""
        cache_key = f"profile:{username}"

        # Try to get from cache
        cached_profile = await cache_service.get("profile", username)
        if cached_profile:
            logger.info(f"📋 Using cached profile for @{username}")
            return TikTokProfile(**cached_profile)

        # Fetch from API
        profile = await self.ensemble_service.get_profile(username)

        # Enhance profile with niche analysis
        profile = await self._enhance_profile_with_niche(profile, username)

        # Cache the enhanced result
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

    async def _enhance_profile_with_niche(self, profile: TikTokProfile, username: str) -> TikTokProfile:
        """Enhance profile with niche analysis using Perplexity"""
        try:
            logger.info(
                f"🎯 Enhancing profile with niche analysis for @{username}")

            # Get recent posts for niche analysis
            recent_posts = await self.ensemble_service.get_posts(username, count=10)
            post_captions = [
                post.caption for post in recent_posts if post.caption.strip()]

            logger.info(
                f"📱 Found {len(post_captions)} posts with captions for niche analysis")

            # Analyze niche using Perplexity
            niche_analysis = await perplexity_service.analyze_user_niche(
                username=username,
                bio=profile.bio,
                recent_posts_content=post_captions,
                follower_count=profile.follower_count,
                video_count=profile.video_count
            )

            # Update profile with niche information
            profile.niche_category = niche_analysis.niche_category
            profile.niche_description = niche_analysis.niche_description
            profile.key_topics = niche_analysis.key_topics
            profile.target_audience = niche_analysis.target_audience
            profile.content_style = niche_analysis.content_style

            logger.info(
                f"✅ Profile enhanced with niche: {niche_analysis.niche_category}")
            logger.info(
                f"📋 Niche description: {niche_analysis.niche_description}")
            logger.info(
                f"🎯 Key topics: {', '.join(niche_analysis.key_topics[:3])}")

        except Exception as e:
            logger.error(f"❌ Niche analysis failed for @{username}: {str(e)}")
            logger.error(f"📊 Error details: {type(e).__name__}")
            # Set fallback niche info
            profile.niche_category = "General Content Creator"
            profile.niche_description = "Content creator with diverse topics and engaging content"
            profile.key_topics = ["entertainment", "lifestyle", "social media"]
            profile.target_audience = "General TikTok audience"
            profile.content_style = "Mixed content style"

        return profile

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
                logger.info(
                    f"🔍 Searching hashtag: #{hashtag} ({i + 1}/{len(hashtags)})")

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
                        count=min(videos_per_hashtag * 2, 20),
                        period=30,  # Вместо 7 дней - 30 дней
                        sorting=1
                    )

                    if not posts:
                        logger.warning(
                            f"⚠️ No posts found for hashtag #{hashtag}")
                        continue

                    # Filter posts by age (not older than 30 days)
                    from datetime import timezone
                    thirty_days_ago = datetime.now(
                        timezone.utc) - timedelta(days=30)
                    filtered_posts = []

                    for post in posts:
                        try:
                            # Parse ISO timestamp and filter by date
                            post_date = datetime.fromisoformat(
                                post.create_time.replace('Z', '+00:00'))
                            if post_date >= thirty_days_ago:
                                filtered_posts.append(post)
                        except (ValueError, AttributeError) as e:
                            logger.warning(
                                f"⚠️ Could not parse date for post {post.id}: {e}")
                            continue

                    # Limit to the requested count after filtering
                    if not filtered_posts:
                        logger.warning(
                            f"⚠️ No posts within 30 days found for hashtag #{hashtag}")
                        continue

                    posts = filtered_posts[:min(videos_per_hashtag * 2, 20)]

                    # Convert to TrendVideo objects with more inclusive filtering
                    # More inclusive quality filter to get more videos
                    quality_posts = [p for p in posts if p.views > 10]

                    # If not enough quality posts, use all available posts
                    if len(quality_posts) < videos_per_hashtag and posts:
                        logger.info(
                            f"🔍 Using all {len(posts)} available posts for #{hashtag}")
                        selected_posts = posts[:videos_per_hashtag]
                    else:
                        selected_posts = quality_posts[:videos_per_hashtag]

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

                    logger.debug(
                        f"✅ Found {len(trend_videos)} trend videos for #{hashtag}")

                all_trends.extend(trend_videos)

                # Add optimized delay between requests based on official SDK recommendations
                if i < len(hashtags) - 1:
                    await asyncio.sleep(settings.ensemble_request_delay)

            except Exception as e:
                logger.warning(f"⚠️ Failed to search hashtag #{hashtag}: {e}")
                # Continue with other hashtags instead of failing completely
                continue

        logger.info(
            f"🎯 Total trending videos found: {len(all_trends)} across {len(hashtags)} hashtags")
        return all_trends

    def _post_to_trend_video(self, post: TikTokPost, hashtag: str) -> TrendVideo:
        """Convert TikTokPost to TrendVideo with full author data"""
        return TrendVideo(
            id=post.id,
            caption=post.caption,
            views=post.views,
            likes=post.likes,
            shares=post.shares,
            comments=post.comments,
            create_time=post.create_time,
            # Prefer TikTok URL for direct access
            video_url=post.tiktok_url or post.video_url,
            cover_image_url=post.cover_image_url,
            hashtag=hashtag,
            author=post.author  # Use parsed author data
        )

    def _days_since_creation(self, create_time: int) -> int:
        """Calculate days since content creation"""
        try:
            from datetime import datetime
            current_timestamp = datetime.now().timestamp()
            days_diff = (current_timestamp - create_time) / (24 * 60 * 60)
            return int(days_diff)
        except Exception:
            # If timestamp parsing fails, assume recent content
            return 1

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
                trends=[TrendVideo(**trend)
                        for trend in cached_data["trends"]],
                analysis_summary=cached_data.get("analysis_summary", "")
            )

        except Exception as e:
            logger.warning(
                f"Failed to get cached analysis for @{username}: {e}")
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

        logger.info(
            f"🔍 Searching hashtag #{clean_hashtag} (count={count}, period={period}d)")

        # Try cache first
        cached_posts = await cache_service.get("hashtag", cache_key)
        if cached_posts:
            logger.info(f"🎯 Using cached results for #{clean_hashtag}")
            return [TikTokPost(**post) for post in cached_posts]

        # Fetch from API using official SDK
        posts = await self.ensemble_service.search_hashtag_posts(
            hashtag=clean_hashtag, count=count, period=period, sorting=sorting
        )

        # Filter posts by age (not older than specified period)
        if period > 0:
            from datetime import timezone
            period_days_ago = datetime.now(
                timezone.utc) - timedelta(days=period)
            filtered_posts = []

            for post in posts:
                try:
                    post_date = datetime.fromisoformat(
                        post.create_time.replace('Z', '+00:00'))
                    if post_date >= period_days_ago:
                        filtered_posts.append(post)
                except (ValueError, AttributeError) as e:
                    logger.warning(
                        f"⚠️ Could not parse date for post {post.id}: {e}")
                    continue

            posts = filtered_posts

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
        logger.warning(
            f"⚠️ User search not supported by Ensemble Data API for query: '{query}'")
        logger.info(
            f"💡 Consider searching for specific usernames directly using get_profile_only()")

        # Return empty list as user search is not supported by official API
        return []

    async def analyze_creative_center_hashtags(
        self,
        profile_url: str,
        creative_center_hashtags: List[Dict[str, Any]],
        videos_per_hashtag: int = 3
    ) -> Dict[str, Any]:
        """
        Analyze Creative Center hashtags by searching trending videos for each hashtag

        This method integrates Creative Center discovery with Ensemble Data:
        1. Takes Creative Center hashtags as input
        2. Searches trending videos for each hashtag via Ensemble
        3. Analyzes and ranks results by relevance
        4. Returns comprehensive analysis

        Args:
            profile_url: User profile URL for context
            creative_center_hashtags: List of Creative Center hashtags with metrics
            videos_per_hashtag: Number of videos to fetch per hashtag

        Returns:
            Dictionary with comprehensive analysis results
        """
        from utils import extract_tiktok_username

        username = extract_tiktok_username(profile_url)
        logger.info(
            f"🔗 Analyzing {len(creative_center_hashtags)} Creative Center hashtags for @{username}")

        try:
            # Get user profile for context
            profile = await self._get_cached_profile(username)

            # Extract hashtag names for Ensemble search
            hashtag_names = []
            hashtag_metadata = {}

            for hashtag_data in creative_center_hashtags:
                name = hashtag_data.get('name', '').strip()
                if name:
                    hashtag_names.append(name)
                    hashtag_metadata[name] = hashtag_data

            if not hashtag_names:
                raise Exception(
                    "No valid hashtags found in Creative Center data")

            logger.info(
                f"🔍 Searching Ensemble Data for hashtags: {hashtag_names}")

            # Search trending videos for each Creative Center hashtag
            all_trend_videos = []
            for hashtag in hashtag_names:
                try:
                    logger.info(f"📱 Searching hashtag: #{hashtag}")

                    # Use Ensemble to find trending posts for this hashtag
                    posts = await self.ensemble_service.search_hashtag_posts(
                        hashtag=hashtag,
                        count=videos_per_hashtag * 2,  # Get more for filtering
                        period=30,  # 30 days for fresh content
                        sorting=1   # Sort by likes
                    )

                    if posts:
                        # Convert to TrendVideo objects with Creative Center metadata
                        for post in posts[:videos_per_hashtag]:
                            trend_video = TrendVideo(
                                id=post.id,
                                caption=post.caption,
                                views=post.views,
                                likes=post.likes,
                                shares=post.shares,
                                comments=post.comments,
                                create_time=post.create_time,
                                video_url=post.tiktok_url or post.video_url,
                                cover_image_url=post.cover_image_url,
                                images=post.images,
                                hashtag=hashtag,
                                author=post.author
                            )

                            # Add Creative Center metadata
                            cc_data = hashtag_metadata.get(hashtag, {})
                            trend_video.relevance_score = cc_data.get(
                                'relevance_score', 0.0)

                            all_trend_videos.append(trend_video)

                        logger.info(
                            f"✅ Found {len(posts[:videos_per_hashtag])} videos for #{hashtag}")
                    else:
                        logger.warning(f"⚠️ No videos found for #{hashtag}")

                except Exception as e:
                    logger.warning(
                        f"⚠️ Failed to search hashtag #{hashtag}: {e}")
                    continue

                # Add delay between requests
                if hashtag != hashtag_names[-1]:
                    await asyncio.sleep(settings.ensemble_request_delay)

            logger.info(
                f"🎯 Total trending videos collected: {len(all_trend_videos)}")

            if not all_trend_videos:
                raise Exception(
                    "No trending videos found for any Creative Center hashtags")

            # Apply quality filtering and sorting (softened filters)
            quality_videos = []
            filtered_out_count = 0

            for video in all_trend_videos:
                # Calculate engagement rate
                engagement_rate = (
                    video.likes + video.comments + video.shares) / max(video.views, 1)

                # Apply more lenient quality filters for better results
                if engagement_rate >= 0.005 and video.views >= 1000 and video.likes >= 10:  # Softened
                    quality_videos.append(video)
                else:
                    filtered_out_count += 1
                    logger.debug(
                        f"⚠️ Video filtered out: views={video.views}, likes={video.likes}, engagement={engagement_rate:.4f}")

            logger.info(
                f"📊 Quality filtering: {len(quality_videos)} videos passed, {filtered_out_count} filtered out")

            # If no videos pass quality filter, use all videos with basic threshold
            if not quality_videos:
                logger.warning(
                    "⚠️ No videos passed quality filter, using basic threshold")
                for video in all_trend_videos:
                    if video.views >= 100:  # Very basic threshold
                        quality_videos.append(video)

            # If still no videos, use all available
            if not quality_videos:
                logger.warning(
                    "⚠️ Using all available videos without quality filter")
                quality_videos = all_trend_videos

            # Sort by combined score (engagement + Creative Center relevance)
            def calculate_video_score(video):
                engagement_score = (video.likes + video.comments *
                                    15 + video.shares * 20) / max(video.views, 1) * 50000
                relevance_bonus = getattr(
                    video, 'relevance_score', 0.0) * 10000
                return engagement_score + relevance_bonus

            # Get top videos from Creative Center hashtags (aim for 10-15)
            niche_videos = sorted(
                quality_videos, key=calculate_video_score, reverse=True)[:15]

            logger.info(
                f"📋 After sorting: {len(niche_videos)} niche videos selected")

            # Apply content relevance analysis if available
            if hasattr(self, 'content_relevance_service') and niche_videos:
                try:
                    logger.info(
                        f"🎨 Applying content relevance analysis to {len(niche_videos)} videos...")
                    analyzed_videos = await content_relevance_service.analyze_trends_relevance(
                        niche_videos,
                        profile.niche_category,
                        profile.niche_description,
                        profile.key_topics
                    )
                    # Take top 10 after relevance analysis
                    niche_videos = analyzed_videos[:10]
                    logger.info(
                        f"✅ Content relevance analysis completed: {len(niche_videos)} final videos")
                except Exception as e:
                    logger.warning(
                        f"⚠️ Content relevance analysis failed: {e}")
                    niche_videos = niche_videos[:10]  # Fallback to top 10
                    logger.info(
                        f"📋 Using fallback: {len(niche_videos)} videos after fallback")

            # For Creative Center analysis, focus only on hashtag-based results
            # No popular videos mixing - show pure Creative Center results
            final_videos = niche_videos

            # Generate analysis summary
            analysis_summary = f"Found {len(final_videos)} high-quality videos from {len(hashtag_names)} Creative Center hashtags. Videos selected based on engagement metrics and Creative Center relevance scores."

            logger.info(
                f"✅ Creative Center analysis completed: {len(final_videos)} videos from Creative Center hashtags")

            return {
                "profile": profile,
                "posts": [],  # Not fetching user posts in this flow
                "hashtags": hashtag_names,
                "trends": final_videos,
                "analysis_summary": analysis_summary,
                "creative_center_metadata": hashtag_metadata,
                "total_cc_hashtags_analyzed": len(creative_center_hashtags)
            }

        except Exception as e:
            logger.error(
                f"❌ Creative Center hashtag analysis failed for @{username}: {e}")
            raise Exception(f"Creative Center analysis failed: {str(e)}")

    async def _convert_post_to_trend(self, post: TikTokPost) -> Optional[TrendVideo]:
        """
        Convert TikTokPost to TrendVideo format

        Args:
            post: TikTokPost object to convert

        Returns:
            TrendVideo object or None if conversion fails
        """
        try:
            return TrendVideo(
                id=post.id,
                caption=post.caption or "",
                views=post.views or 0,
                likes=post.likes or 0,
                shares=post.shares or 0,
                comments=post.comments or 0,
                create_time=post.create_time,
                video_url=post.tiktok_url or post.video_url or "",
                cover_image_url=post.cover_image_url or "",
                images=post.images or [],
                hashtag="popular",  # Mark as popular content
                author=post.author,
                relevance_score=0.5  # Default relevance score for popular content
            )
        except Exception as e:
            logger.debug(f"⚠️ Failed to convert post {post.id} to trend: {e}")
            return None


# Global trend analysis service instance
trend_service = TrendAnalysisService()
