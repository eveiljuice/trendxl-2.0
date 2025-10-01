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
    TrendAnalysisResponse,
    TokenUsage
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
        videos_per_hashtag: int = 8  # Increased from 2 to 8 to compensate for filters
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
        print(f"\n{'='*70}")
        print(f"🚀 TREND SERVICE: analyze_profile_trends() STARTED!")
        print(f"   Profile: {profile_input}")
        print(f"   Max hashtags: {max_hashtags}")
        print(f"   Videos per hashtag: {videos_per_hashtag}")
        print(f"{'='*70}\n")

        username = extract_tiktok_username(profile_input)
        print(f"✅ Extracted username: @{username}")
        logger.info(f"🚀 Starting trend analysis for profile: @{username}")

        # Initialize token usage tracking
        token_tracker = {
            "openai_prompt_tokens": 0,
            "openai_completion_tokens": 0,
            "perplexity_prompt_tokens": 0,
            "perplexity_completion_tokens": 0,
            "ensemble_units": 0
        }

        try:
            # Step 1: Get profile information (with caching)
            print(f"📊 Step 1: Fetching profile...")
            logger.info("📊 Step 1: Fetching profile information...")
            profile = await self._get_cached_profile(username, token_tracker)
            print(f"✅ Profile fetched: @{profile.username}")

            # Step 2: Get user's recent posts (with caching)
            logger.info("📱 Step 2: Loading recent posts...")
            posts = await self._get_cached_posts(username, settings.max_posts_per_user)

            if not posts:
                raise Exception(f"No posts found for user @{username}")

            # Step 3: Analyze posts with AI to extract trending hashtags
            logger.info("🤖 Step 3: Analyzing posts with AI...")
            analysis, openai_tokens = await self.openai_service.analyze_posts_for_hashtags(
                posts, profile.bio
            )

            # Track OpenAI tokens
            token_tracker["openai_prompt_tokens"] += openai_tokens.get(
                "prompt_tokens", 0)
            token_tracker["openai_completion_tokens"] += openai_tokens.get(
                "completion_tokens", 0)

            hashtags = analysis.top_hashtags[:max_hashtags]

            if not hashtags:
                raise Exception("No hashtags extracted from analysis")

            logger.info(f"✅ Extracted hashtags: {hashtags}")

            # Step 4: Search trending videos for each hashtag using official SDK
            logger.info("🔥 Step 4: Searching trending videos by hashtags...")
            trends = await self._search_trending_videos_optimized(
                hashtags, videos_per_hashtag
            )

            # ENSURE we get exactly 10 videos - this is mandatory requirement
            target_video_count = 10

            # If we don't have enough videos, try to get more niche-specific hashtags from Perplexity
            if len(trends) < target_video_count:
                logger.info(
                    f"📈 Got {len(trends)} videos, trying to get more niche-specific hashtags (target: {target_video_count})")

                # Get additional niche-specific hashtags from Perplexity with account origin analysis
                try:
                    from .perplexity_service import perplexity_service

                    # First, analyze account origin to determine country and language
                    logger.info(
                        f"🌍 Analyzing TikTok account origin for @{username}...")

                    # Get recent post captions for analysis
                    recent_captions = [
                        post.caption for post in posts if post.caption][:10]

                    account_origin, perplexity_tokens = await perplexity_service.analyze_tiktok_account_origin(
                        username=username,
                        bio=profile.bio or "",
                        recent_posts_content=recent_captions,
                        follower_count=profile.follower_count,
                        video_count=profile.video_count
                    )

                    # Track Perplexity tokens for account origin analysis
                    token_tracker["perplexity_prompt_tokens"] += perplexity_tokens.get(
                        "prompt_tokens", 0)
                    token_tracker["perplexity_completion_tokens"] += perplexity_tokens.get(
                        "completion_tokens", 0)

                    # Create more specific search query based on profile niche
                    niche_query = f"{profile.niche_category if profile.niche_category else 'content creation'} hashtags"

                    logger.info(
                        f"🔍 Requesting additional niche-specific hashtags for: {niche_query} (Account from: {account_origin['country']})")

                    # Get additional hashtags from Perplexity with account origin
                    additional_hashtag_data = await perplexity_service.discover_creative_center_hashtags(
                        niche=niche_query,
                        country=account_origin["country_code"],
                        language=account_origin["language"],
                        limit=5,  # Get 5 additional hashtags
                        account_origin=account_origin
                    )

                    if additional_hashtag_data:
                        additional_hashtags = [
                            h["name"] for h in additional_hashtag_data if h.get("name")]
                        needed_videos = target_video_count - len(trends)
                        videos_per_hashtag = max(
                            1, needed_videos // len(additional_hashtags)) if additional_hashtags else 0

                        if additional_hashtags and videos_per_hashtag > 0:
                            logger.info(
                                f"🔄 Searching {videos_per_hashtag} videos from {len(additional_hashtags)} additional niche hashtags: {additional_hashtags}")

                            additional_trends = await self._search_trending_videos_optimized(
                                additional_hashtags, videos_per_hashtag
                            )

                            if additional_trends:
                                logger.info(
                                    f"➕ Found {len(additional_trends)} additional videos from niche hashtags")

                                # Combine and deduplicate trends
                                all_trends = trends + additional_trends
                                seen_ids = set()
                                unique_trends = []

                                for trend in all_trends:
                                    if trend.id not in seen_ids:
                                        seen_ids.add(trend.id)
                                        unique_trends.append(trend)

                                # ENSURE we return exactly 10 videos - this is mandatory
                                if len(unique_trends) >= target_video_count:
                                    trends = unique_trends[:target_video_count]
                                    logger.info(
                                        f"✅ Final video count after niche search: {len(trends)}")
                                else:
                                    # If still not enough, pad with the best available videos
                                    trends = unique_trends
                                    logger.warning(
                                        f"⚠️ Could only find {len(trends)} videos (target: {target_video_count}). Using all available.")

                except Exception as e:
                    logger.warning(
                        f"⚠️ Failed to get additional niche hashtags: {e}")

            # Ensure we have at least some trends (requirement: exactly 10 videos)
            if not trends:
                logger.error(
                    "❌ No trending videos found for any hashtags")
                # Instead of failing, we'll try one more time with broader search
                logger.info(
                    "🔄 Attempting fallback search with broader parameters...")
                try:
                    # Try searching with a default popular hashtag as fallback
                    fallback_hashtags = ["fyp", "viral", "trending", "foryou"]
                    fallback_trends = await self._search_trending_videos_optimized(
                        fallback_hashtags, videos_per_hashtag
                    )
                    if fallback_trends:
                        trends = fallback_trends[:target_video_count]
                        logger.info(
                            f"✅ Fallback search successful: {len(trends)} videos")
                    else:
                        # If still no trends, create minimal response
                        logger.warning(
                            "⚠️ No trending content found. Returning empty results.")
                        trends = []
                except Exception as fallback_error:
                    logger.error(
                        f"❌ Fallback search also failed: {fallback_error}")
                    trends = []

            # Enhanced quality filtering and sorting
            logger.info(
                f"📊 Filtering {len(trends)} trends by quality metrics...")

            # Filter trends by quality criteria - СМЯГЧЕННЫЕ для получения 10+ видео
            quality_trends = []
            for trend in trends:
                # Calculate engagement rate
                engagement_rate = (
                    trend.likes + trend.comments + trend.shares) / max(trend.views, 1)

                # Filter 1: ЗНАЧИТЕЛЬНО смягченный engagement (0.1% вместо 2%)
                if engagement_rate < 0.001:
                    continue

                # Filter 2: СМЯГЧЕННЫЕ пороги (100+ views, 1+ like вместо 10K+ views, 200+ likes)
                if trend.views < 100 or trend.likes < 1:
                    continue

                # Filter 3: Freshness - only last 7 days for maximum relevance (НЕ ИЗМЕНЕНО)
                if self._days_since_creation(trend.create_time) > 7:
                    continue

                quality_trends.append(trend)

            logger.info(
                f"✅ {len(quality_trends)} trends passed quality filters")

            if not quality_trends:
                # Fallback: if no trends pass quality filters, use МИНИМАЛЬНЫЕ criteria for last 7 days
                logger.warning(
                    "⚠️ No trends passed quality filters, using minimal criteria for last 7 days...")
                quality_trends = [
                    t for t in trends
                    if t.views > 10 and t.likes > 0 and self._days_since_creation(t.create_time) <= 7
                ][:15]  # Top 15 для гарантии 10+

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
            )[:10]  # Top 10 videos by engagement metrics

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
                period=7  # Last 7 days only for maximum relevance
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

            # Calculate token usage and costs
            openai_total = token_tracker["openai_prompt_tokens"] + \
                token_tracker["openai_completion_tokens"]
            perplexity_total = token_tracker["perplexity_prompt_tokens"] + \
                token_tracker["perplexity_completion_tokens"]

            # Rough cost estimation (prices as of 2024)
            # GPT-4o: $2.50 per 1M input tokens, $10 per 1M output tokens
            # Perplexity Sonar: $1 per 1M input tokens, $3 per 1M output tokens
            # Ensemble Data: varies by endpoint, roughly $0.001 per unit
            openai_cost = (token_tracker["openai_prompt_tokens"] * 2.50 / 1_000_000 +
                           token_tracker["openai_completion_tokens"] * 10 / 1_000_000)
            perplexity_cost = (token_tracker["perplexity_prompt_tokens"] * 1.0 / 1_000_000 +
                               token_tracker["perplexity_completion_tokens"] * 3.0 / 1_000_000)
            ensemble_cost = token_tracker["ensemble_units"] * 0.001
            total_cost = openai_cost + perplexity_cost + ensemble_cost

            token_usage = TokenUsage(
                openai_tokens=openai_total,
                openai_prompt_tokens=token_tracker["openai_prompt_tokens"],
                openai_completion_tokens=token_tracker["openai_completion_tokens"],
                perplexity_tokens=perplexity_total,
                perplexity_prompt_tokens=token_tracker["perplexity_prompt_tokens"],
                perplexity_completion_tokens=token_tracker["perplexity_completion_tokens"],
                ensemble_units=token_tracker["ensemble_units"],
                total_cost_estimate=round(total_cost, 4)
            )

            logger.info(
                f"💰 Total token usage - OpenAI: {openai_total}, Perplexity: {perplexity_total}, Ensemble: {token_tracker['ensemble_units']} units")
            logger.info(f"💵 Estimated total cost: ${total_cost:.4f}")

            # Cache the complete analysis result
            await self._cache_analysis_result(
                username, profile, posts, hashtags, combined_trends, analysis.analysis_summary, token_usage
            )

            return TrendAnalysisResponse(
                profile=profile,
                posts=posts,
                hashtags=hashtags,
                trends=combined_trends,
                analysis_summary=analysis.analysis_summary,
                token_usage=token_usage
            )

        except Exception as e:
            logger.error(f"❌ Trend analysis failed for @{username}: {e}")
            raise Exception(f"Analysis failed for @{username}: {str(e)}")

    async def _get_cached_profile(
        self,
        username: str,
        token_tracker: Optional[Dict[str, int]] = None
    ) -> TikTokProfile:
        """Get profile with caching and niche analysis"""
        cache_key = f"profile:{username}"

        # Try to get from cache
        cached_profile = await cache_service.get("profile", username)
        if cached_profile:
            logger.info(f"📋 Using cached profile for @{username}")
            return TikTokProfile(**cached_profile)

        # Fetch from API
        profile = await self.ensemble_service.get_profile(username)

        # Enhance profile with niche analysis (with token tracking)
        profile = await self._enhance_profile_with_niche(profile, username, token_tracker)

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

    async def _enhance_profile_with_niche(
        self,
        profile: TikTokProfile,
        username: str,
        token_tracker: Optional[Dict[str, int]] = None
    ) -> TikTokProfile:
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
            niche_analysis, perplexity_tokens = await perplexity_service.analyze_user_niche(
                username=username,
                bio=profile.bio,
                recent_posts_content=post_captions,
                follower_count=profile.follower_count,
                video_count=profile.video_count
            )

            # Track Perplexity tokens if tracker provided
            if token_tracker is not None:
                token_tracker["perplexity_prompt_tokens"] += perplexity_tokens.get(
                    "prompt_tokens", 0)
                token_tracker["perplexity_completion_tokens"] += perplexity_tokens.get(
                    "completion_tokens", 0)

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

                # Check cache first with improved key structure (7 days only)
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
                        # Увеличено для лучшего покрытия
                        count=min(videos_per_hashtag * 3, 30),
                        period=7,  # ТОЛЬКО ПОСЛЕДНЯЯ НЕДЕЛЯ
                        sorting=1
                    )

                    if not posts:
                        logger.warning(
                            f"⚠️ No posts found for hashtag #{hashtag}")
                        continue

                    # Filter posts by age (STRICTLY last 7 days only)
                    from datetime import timezone
                    seven_days_ago = datetime.now(
                        timezone.utc) - timedelta(days=7)
                    filtered_posts = []

                    for post in posts:
                        try:
                            # Parse ISO timestamp and filter by date
                            post_date = datetime.fromisoformat(
                                post.create_time.replace('Z', '+00:00'))
                            if post_date >= seven_days_ago:
                                filtered_posts.append(post)
                        except (ValueError, AttributeError) as e:
                            logger.warning(
                                f"⚠️ Could not parse date for post {post.id}: {e}")
                            continue

                    # Use filtered posts or log warning
                    if not filtered_posts:
                        logger.warning(
                            f"⚠️ No posts within last 7 days found for hashtag #{hashtag}")
                        continue

                    posts = filtered_posts

                    # Convert to TrendVideo objects - prioritize quality but ensure we get enough videos
                    # Sort posts by views to get the most popular ones first
                    sorted_posts = sorted(
                        posts, key=lambda p: p.views, reverse=True)

                    # Take the best available posts, but ensure we get the required count
                    if len(sorted_posts) >= videos_per_hashtag:
                        selected_posts = sorted_posts[:videos_per_hashtag]
                        logger.info(
                            f"✅ Selected {len(selected_posts)} high-quality posts for #{hashtag}")
                    else:
                        # If we don't have enough posts, use all available
                        selected_posts = sorted_posts
                        logger.warning(
                            f"⚠️ Only {len(selected_posts)} posts available for #{hashtag} (target: {videos_per_hashtag})")

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
        analysis_summary: str,
        token_usage: Optional[TokenUsage] = None
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

            # Add token_usage if provided
            if token_usage:
                analysis_data["token_usage"] = token_usage.model_dump()

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

            # Extract token_usage if available
            token_usage = None
            if "token_usage" in cached_data:
                token_usage = TokenUsage(**cached_data["token_usage"])

            return TrendAnalysisResponse(
                profile=TikTokProfile(**cached_data["profile"]),
                posts=[TikTokPost(**post) for post in cached_data["posts"]],
                hashtags=cached_data["hashtags"],
                trends=[TrendVideo(**trend)
                        for trend in cached_data["trends"]],
                analysis_summary=cached_data.get("analysis_summary", ""),
                token_usage=token_usage
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
        videos_per_hashtag: int = 8  # Увеличено с 3 до 8 для гарантии 10+ видео
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
                        count=videos_per_hashtag * 5,  # Увеличено с *2 до *5 для компенсации фильтров
                        period=7,   # ONLY last 7 days for trending content
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

                # Apply ОЧЕНЬ мягкие quality filters для гарантии 10+ видео
                if engagement_rate >= 0.001 and video.views >= 100 and video.likes >= 1:  # ЗНАЧИТЕЛЬНО смягчено
                    quality_videos.append(video)
                else:
                    filtered_out_count += 1
                    logger.debug(
                        f"⚠️ Video filtered out: views={video.views}, likes={video.likes}, engagement={engagement_rate:.4f}")

            logger.info(
                f"📊 Quality filtering: {len(quality_videos)} videos passed, {filtered_out_count} filtered out")

            # If no videos pass quality filter, use МИНИМАЛЬНЫЙ threshold
            if not quality_videos:
                logger.warning(
                    "⚠️ No videos passed quality filter, using minimal threshold")
                for video in all_trend_videos:
                    if video.views >= 10:  # ОЧЕНЬ низкий threshold
                        quality_videos.append(video)

            # If still no videos, use ALL available videos
            if not quality_videos:
                logger.warning(
                    "⚠️ Using ALL available videos without any quality filter")
                quality_videos = all_trend_videos

            # Sort by combined score (engagement + Creative Center relevance)
            def calculate_video_score(video):
                engagement_score = (video.likes + video.comments *
                                    15 + video.shares * 20) / max(video.views, 1) * 50000
                relevance_bonus = getattr(
                    video, 'relevance_score', 0.0) * 10000
                return engagement_score + relevance_bonus

            # Get top videos from Creative Center hashtags (aim for 15-20 для гарантии 10+)
            niche_videos = sorted(
                quality_videos, key=calculate_video_score, reverse=True)[:20]

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
                    # Take top 15 after relevance analysis для гарантии 10+
                    niche_videos = analyzed_videos[:15]
                    logger.info(
                        f"✅ Content relevance analysis completed: {len(niche_videos)} final videos")
                except Exception as e:
                    logger.warning(
                        f"⚠️ Content relevance analysis failed: {e}")
                    # Fallback to top 15 для гарантии 10+
                    niche_videos = niche_videos[:15]
                    logger.info(
                        f"📋 Using fallback: {len(niche_videos)} videos after fallback")

            # For Creative Center analysis, focus only on hashtag-based results
            # No popular videos mixing - show pure Creative Center results
            final_videos = niche_videos

            # КРИТИЧНО: Убеждаемся что у нас минимум 10 видео
            if len(final_videos) < 10:
                logger.warning(
                    f"⚠️ Creative Center дал только {len(final_videos)} видео (нужно 10+)")
                logger.info(
                    "🔄 Пытаемся получить больше видео с увеличенными параметрами...")

                # Увеличиваем videos_per_hashtag для каждого хештега
                additional_videos = []
                for hashtag in hashtag_names:
                    try:
                        posts = await self.ensemble_service.search_hashtag_posts(
                            hashtag=hashtag,
                            count=15,  # Больше видео на хештег
                            period=7,
                            sorting=1
                        )

                        # Берем дополнительные видео
                        for post in posts[videos_per_hashtag:]:
                            if len(additional_videos) + len(final_videos) >= 15:
                                break
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
                                author=post.author,
                                relevance_score=0.5
                            )
                            # Проверяем что видео не дублируется
                            if not any(v.id == trend_video.id for v in final_videos):
                                additional_videos.append(trend_video)

                        if len(additional_videos) + len(final_videos) >= 15:
                            break
                    except Exception as e:
                        logger.warning(
                            f"⚠️ Не удалось получить дополнительные видео для #{hashtag}: {e}")
                        continue

                final_videos.extend(additional_videos)
                logger.info(
                    f"✅ Добавлено {len(additional_videos)} дополнительных видео. Итого: {len(final_videos)}")

            # Финальная обрезка до разумного количества
            final_videos = final_videos[:15]

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
