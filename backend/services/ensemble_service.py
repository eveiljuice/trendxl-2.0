"""
Ensemble Data API Service for TikTok data - Official SDK Implementation
"""
import logging
import math
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from ensembledata.api import EDClient, EDError
from models import TikTokProfile, TikTokPost
from utils import (
    extract_tiktok_username,
    extract_hashtags_from_text,
    retry_with_backoff,
    default_retry_condition,
    safe_get_nested
)
from config import settings

logger = logging.getLogger(__name__)


class EnsembleService:
    """Service for interacting with Ensemble Data API - Official SDK Implementation"""

    def __init__(self):
        """Initialize Ensemble Data client according to official documentation"""
        self.client = None
        self.initialized = False
        try:
            if settings.ensemble_api_token and len(settings.ensemble_api_token) > 10:
                self.client = EDClient(settings.ensemble_api_token)
                self.initialized = True
                logger.info(
                    "✅ Ensemble Data SDK client initialized successfully")
            else:
                logger.warning(
                    "⚠️ Ensemble API token not configured - service disabled")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Ensemble Data client: {e}")
            self.initialized = False

    def _run_in_executor(self, func, *args, **kwargs):
        """Run synchronous SDK calls in thread executor for async compatibility"""
        import concurrent.futures
        import asyncio

        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            return loop.run_in_executor(executor, lambda: func(*args, **kwargs))

    async def get_profile(self, username_or_url: str) -> TikTokProfile:
        """
        Get TikTok user profile information using official SDK

        Args:
            username_or_url: TikTok username or URL

        Returns:
            TikTokProfile object

        Raises:
            Exception: If profile cannot be retrieved
        """
        username = extract_tiktok_username(username_or_url)
        logger.info(f"📊 Fetching profile for user: @{username}")

        try:
            # Call SDK method in executor (official API: user_info_from_username)
            response = await self._run_in_executor(
                self.client.tiktok.user_info_from_username,
                username=username
            )

            # Log billing info according to official docs
            units_charged = getattr(response, 'units_charged', 0)
            if units_charged:
                logger.info(
                    f"💰 Ensemble units charged (profile): {units_charged}")

            # Extract profile data from official response structure
            profile_data = response.data if hasattr(
                response, 'data') else response
            user_data = profile_data.get("user", {}) if isinstance(
                profile_data, dict) else {}
            stats_data = profile_data.get("stats", {}) if isinstance(
                profile_data, dict) else {}

            # Parse according to official data structure
            profile = self._parse_profile_data(user_data, stats_data, username)

            logger.info(f"✅ Successfully retrieved profile for @{username}")
            return profile

        except EDError as e:
            logger.error(f"❌ Ensemble API error for @{username}: {e}")
            raise Exception(
                f"Could not retrieve profile for @{username}: API error - {str(e)}")
        except Exception as e:
            logger.error(f"❌ Failed to fetch profile for @{username}: {e}")
            raise Exception(
                f"Could not retrieve profile for @{username}: {str(e)}")

    async def get_posts(
        self,
        username_or_url: str,
        count: int = 20,
        cursor: Optional[str] = None
    ) -> List[TikTokPost]:
        """
        Get TikTok user's recent posts using official SDK

        Args:
            username_or_url: TikTok username or URL
            count: Number of posts to fetch (max 50)
            cursor: Pagination cursor (nextCursor from previous response)

        Returns:
            List of TikTokPost objects

        Raises:
            Exception: If posts cannot be retrieved
        """
        username = extract_tiktok_username(username_or_url)
        count = min(count, 50)  # Limit to 50 posts
        logger.info(f"📱 Fetching {count} posts for user: @{username}")

        try:
            # Calculate depth according to official docs (each depth = ~10 posts)
            # Max depth 5 as per best practices
            depth = min((count + 9) // 10, 5)

            # Prepare parameters for official SDK method
            params = {"username": username, "depth": depth}
            if cursor:
                params["cursor"] = cursor
                logger.info(f"🔄 Using pagination cursor: {cursor}")

            # Call official SDK method: client.tiktok.user_posts_from_username
            response = await self._run_in_executor(
                self.client.tiktok.user_posts_from_username,
                **params
            )

            # Log billing info according to official docs
            units_charged = getattr(response, 'units_charged', 0)
            if units_charged:
                logger.info(
                    f"💰 Ensemble units charged (posts): {units_charged}")

            # Extract posts data from official response structure
            posts_data = response.data if hasattr(
                response, 'data') else response
            posts_list = posts_data.get("data", []) if isinstance(
                posts_data, dict) else []
            next_cursor = posts_data.get("nextCursor") if isinstance(
                posts_data, dict) else None

            # Parse posts according to official data structure
            posts = self._parse_posts_data(posts_list, count)

            logger.info(
                f"✅ Successfully retrieved {len(posts)} posts for @{username}")
            if next_cursor:
                logger.info(f"🔗 Next cursor available: {next_cursor}")

            return posts

        except EDError as e:
            logger.error(f"❌ Ensemble API error for @{username}: {e}")
            error_msg = str(e).lower()

            # Provide specific error messages based on error type
            if "rate limit" in error_msg or "429" in error_msg:
                raise Exception(
                    f"API rate limit exceeded for @{username}. Please try again in a few minutes.")
            elif "not found" in error_msg or "404" in error_msg:
                raise Exception(
                    f"TikTok profile @{username} not found or is private/restricted.")
            elif "forbidden" in error_msg or "403" in error_msg:
                raise Exception(
                    f"Access denied to @{username}. This profile may be protected or geo-restricted.")
            else:
                raise Exception(
                    f"Unable to retrieve posts for @{username}. API error: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Failed to fetch posts for @{username}: {e}")
            raise Exception(
                f"Unable to retrieve posts for @{username}. Error: {str(e)}")

    async def search_hashtag_posts(
        self,
        hashtag: str,
        count: int = 10,
        period: int = 7,
        sorting: int = 1,
        cursor: Optional[int] = None
    ) -> List[TikTokPost]:
        """
        Search TikTok posts by hashtag using official SDK

        Args:
            hashtag: Hashtag to search (without #)
            count: Number of posts to fetch
            period: Search period in days (for full_hashtag_search)
            sorting: Sort order (not directly supported in hashtag_search)
            cursor: Pagination cursor (for hashtag_search)

        Returns:
            List of TikTokPost objects

        Raises:
            Exception: If search fails
        """
        clean_hashtag = hashtag.replace('#', '').strip()
        logger.info(
            f"🔍 Searching posts for hashtag: #{clean_hashtag} (period: {period} days)")

        try:
            # Try full_hashtag_search first (supports period filtering)
            if period > 0 and cursor is None:
                try:
                    response = await self._run_in_executor(
                        self.client.tiktok.full_hashtag_search,
                        hashtag=clean_hashtag,
                        # Min 30 days as per documentation
                        days=max(30, period),
                        max_cursor=min(2000, count * 10)  # Reasonable limit
                    )

                    # Log billing info
                    units_charged = getattr(response, 'units_charged', 0)
                    if units_charged:
                        logger.info(
                            f"💰 Ensemble units charged (full hashtag): {units_charged}")

                    # Extract data from full search response (official: res.data["data"])
                    hashtag_data = response.data if hasattr(
                        response, 'data') else response

                    # Debug: Log actual response structure
                    logger.debug(
                        f"🔍 Full hashtag response structure for #{clean_hashtag}: {list(hashtag_data.keys()) if isinstance(hashtag_data, dict) else type(hashtag_data)}")

                    posts_list = hashtag_data.get("data", []) if isinstance(
                        hashtag_data, dict) else []

                    logger.debug(
                        f"📊 Full hashtag search returned {len(posts_list)} posts for #{clean_hashtag}")

                    # If no results from full search, try regular hashtag_search
                    if not posts_list:
                        logger.info(
                            f"⚠️ Full hashtag search returned no results, trying regular search for #{clean_hashtag}")
                        regular_response = await self._run_in_executor(
                            self.client.tiktok.hashtag_search,
                            hashtag=clean_hashtag,
                            cursor=0
                        )
                        regular_data = regular_response.data if hasattr(
                            regular_response, 'data') else regular_response

                        # Debug: Log regular search response structure
                        logger.debug(
                            f"🔍 Regular hashtag response structure for #{clean_hashtag}: {list(regular_data.keys()) if isinstance(regular_data, dict) else type(regular_data)}")

                        posts_list = regular_data.get("data", []) if isinstance(
                            regular_data, dict) else []
                        logger.debug(
                            f"📊 Regular hashtag search returned {len(posts_list)} posts for #{clean_hashtag}")

                except Exception as full_search_error:
                    logger.info(
                        f"⚠️ Full hashtag search failed, fallback to regular search: {full_search_error}")
                    posts_list = await self._search_hashtag_with_cursor(clean_hashtag, count, cursor)
            else:
                # Use regular hashtag_search with cursor support
                posts_list = await self._search_hashtag_with_cursor(clean_hashtag, count, cursor)

            # Parse posts according to official data structure
            posts = self._parse_hashtag_posts(posts_list, clean_hashtag, count)

            logger.debug(
                f"📊 Raw posts found: {len(posts)} for #{clean_hashtag}")
            if posts:
                logger.debug(
                    f"📈 Sample post views: {[p.views for p in posts[:3]]}")

            # Filter posts by age (not older than specified period)
            if period > 0:
                from datetime import timezone
                period_days_ago = datetime.now(
                    timezone.utc) - timedelta(days=period)
                date_filtered_posts = []

                for post in posts:
                    try:
                        post_date = datetime.fromisoformat(
                            post.create_time.replace('Z', '+00:00'))
                        if post_date >= period_days_ago:
                            date_filtered_posts.append(post)
                    except (ValueError, AttributeError) as e:
                        logger.warning(
                            f"⚠️ Could not parse date for post {post.id}: {e}")
                        continue

                posts = date_filtered_posts
                logger.debug(
                    f"📅 Posts after date filtering ({period} days): {len(posts)}")

            # Filter high-quality results with more inclusive threshold
            # Start with posts that have at least some engagement
            quality_posts = [post for post in posts if post.views > 10]

            # If no posts with 10+ views, use even lower threshold
            if not quality_posts and posts:
                logger.info(
                    f"🔍 No posts > 10 views, using minimal threshold for #{clean_hashtag}")
                quality_posts = [post for post in posts if post.views > 0]

            # If still no posts, take all available posts
            if not quality_posts:
                quality_posts = posts
                logger.info(
                    f"🔍 Using all available posts for #{clean_hashtag}")

            final_posts = quality_posts[:count] if quality_posts else posts[:count]
            logger.info(
                f"✅ Found {len(final_posts)} quality posts for #{clean_hashtag} (requested: {count})")

            return final_posts

        except EDError as e:
            logger.error(
                f"❌ Ensemble API error for hashtag #{clean_hashtag}: {e}")
            error_msg = str(e).lower()

            # Provide specific error messages for hashtag search
            if "rate limit" in error_msg or "429" in error_msg:
                raise Exception(
                    f"API rate limit exceeded for hashtag #{clean_hashtag}. Please try again later.")
            elif "not found" in error_msg or "404" in error_msg:
                raise Exception(
                    f"No content found for hashtag #{clean_hashtag} or hashtag is restricted.")
            elif "forbidden" in error_msg or "403" in error_msg:
                raise Exception(
                    f"Access denied to hashtag #{clean_hashtag}. Content may be geo-restricted.")
            else:
                raise Exception(
                    f"Unable to search hashtag #{clean_hashtag}. API error: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Failed to search hashtag #{clean_hashtag}: {e}")
            raise Exception(
                f"Unable to search hashtag #{clean_hashtag}. Error: {str(e)}")

    async def search_popular_videos(
        self,
        count: int = 10,
        period: int = 7
    ) -> List[TikTokPost]:
        """
        Search for popular TikTok videos using trending keywords

        Args:
            count: Number of videos to return (max 50)
            period: Period in days to search (7, 30, 90, 180 days)

        Returns:
            List of popular TikTokPost objects
        """
        count = min(count, 50)
        logger.info(
            f"🔥 Searching for {count} popular videos (period: {period} days)")

        try:
            # Use trending keywords to find popular content
            popular_keywords = [
                "viral", "trending", "fyp", "foryou", "trend", "popular", "tiktok",
                "funny", "comedy", "dance", "music", "challenge"
            ]

            all_posts = []
            videos_per_keyword = max(2, count // len(popular_keywords) + 1)

            # Search with multiple popular keywords to get diverse content
            for keyword in popular_keywords[:6]:  # Use top 6 keywords
                try:
                    response = await self._run_in_executor(
                        self.client.tiktok.keyword_search,
                        keyword=keyword,
                        period=str(period),
                        count=videos_per_keyword
                    )

                    # Log billing info
                    units_charged = getattr(response, 'units_charged', 0)
                    if units_charged:
                        logger.info(
                            f"💰 Ensemble units charged (keyword '{keyword}'): {units_charged}")

                    # Extract data from response
                    search_data = response.data if hasattr(
                        response, 'data') else response
                    posts_list = search_data.get("data", []) if isinstance(
                        search_data, dict) else []

                    logger.debug(
                        f"🔍 Keyword '{keyword}' returned {len(posts_list)} posts")

                    # Convert to TikTokPost objects
                    for post_data in posts_list:
                        try:
                            post = await self._convert_to_tiktok_post(post_data)
                            if post and post.views > 1000:  # Filter for popular content only
                                all_posts.append(post)
                        except Exception as post_error:
                            logger.debug(
                                f"⚠️ Failed to convert post from keyword '{keyword}': {post_error}")
                            continue

                    # Add delay to avoid rate limiting
                    await asyncio.sleep(0.5)

                except Exception as keyword_error:
                    logger.warning(
                        f"⚠️ Failed to search keyword '{keyword}': {keyword_error}")
                    continue

            if not all_posts:
                logger.warning(
                    "⚠️ No popular videos found, using fallback method")
                # Fallback: try with general search
                try:
                    response = await self._run_in_executor(
                        self.client.tiktok.keyword_search,
                        keyword="tiktok",
                        period=str(period),
                        count=count
                    )

                    search_data = response.data if hasattr(
                        response, 'data') else response
                    posts_list = search_data.get("data", []) if isinstance(
                        search_data, dict) else []

                    for post_data in posts_list:
                        try:
                            post = await self._convert_to_tiktok_post(post_data)
                            if post:
                                all_posts.append(post)
                        except Exception:
                            continue
                except Exception as fallback_error:
                    logger.error(f"❌ Fallback search failed: {fallback_error}")

            # Remove duplicates based on aweme_id
            unique_posts = {}
            for post in all_posts:
                if post.aweme_id not in unique_posts:
                    unique_posts[post.aweme_id] = post

            # Sort by engagement (views + likes) and get top posts
            sorted_posts = sorted(
                unique_posts.values(),
                key=lambda p: (p.views or 0) + (p.likes or 0),
                reverse=True
            )

            final_posts = sorted_posts[:count]
            logger.info(f"✅ Found {len(final_posts)} popular videos")

            return final_posts

        except Exception as e:
            logger.error(f"❌ Popular videos search failed: {e}")
            return []

    async def _search_hashtag_with_cursor(
        self,
        hashtag: str,
        count: int,
        cursor: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Helper method for hashtag search with cursor pagination"""
        all_posts = []
        current_cursor = cursor
        attempts = 0
        max_attempts = min(5, (count + 19) // 20)  # Each page ~20 posts

        while len(all_posts) < count and attempts < max_attempts:
            try:
                # Call official hashtag_search method
                response = await self._run_in_executor(
                    self.client.tiktok.hashtag_search,
                    hashtag=hashtag,
                    cursor=current_cursor
                )

                # Log billing info
                units_charged = getattr(response, 'units_charged', 0)
                if units_charged:
                    logger.info(
                        f"💰 Ensemble units charged (hashtag page {attempts+1}): {units_charged}")

                # Extract data from response
                page_data = response.data if hasattr(
                    response, 'data') else response
                posts_batch = page_data.get(
                    "data", []) if isinstance(page_data, dict) else []
                next_cursor = page_data.get("nextCursor") if isinstance(
                    page_data, dict) else None

                if isinstance(posts_batch, list):
                    all_posts.extend(posts_batch)

                # Break if no more pages
                if not next_cursor:
                    break

                current_cursor = next_cursor
                attempts += 1

            except Exception as e:
                logger.warning(
                    f"⚠️ Error in hashtag search page {attempts+1}: {e}")
                break

        return all_posts

    async def search_users(self, query: str, count: int = 10) -> List[TikTokProfile]:
        """
        Search TikTok users by keyword - NOT SUPPORTED by Ensemble Data API

        Args:
            query: Search query
            count: Number of users to fetch

        Returns:
            Empty list (user search not supported by official API)

        Note:
            According to official Ensemble Data documentation, user search functionality 
            is not available. This method returns an empty list to maintain compatibility.
        """
        logger.warning(
            f"⚠️ User search not supported by Ensemble Data API for query: '{query}'")
        logger.info(
            f"🔍 Consider using alternative approaches like searching specific usernames directly")

        # Return empty list as user search is not supported by official API
        return []

    def _parse_profile_data(
        self,
        user_data: Dict[str, Any],
        stats_data: Dict[str, Any],
        username: str
    ) -> TikTokProfile:
        """
        Parse profile data from official API response structure

        Args:
            user_data: User object from response.data["user"]
            stats_data: Stats object from response.data["stats"] 
            username: Original username for fallback

        Returns:
            TikTokProfile object with validated data
        """
        if not isinstance(user_data, dict):
            logger.warning(
                f"Invalid user data format for @{username}: expected dict, got {type(user_data)}")
            user_data = {}

        if not isinstance(stats_data, dict):
            logger.warning(
                f"Invalid stats data format for @{username}: expected dict, got {type(stats_data)}")
            stats_data = {}

        # Safe integer conversion function
        def safe_int(value, default=0):
            """Safely convert value to non-negative integer"""
            if isinstance(value, (int, float)):
                return max(0, int(value))
            if isinstance(value, str) and value.isdigit():
                return max(0, int(value))
            return default

        # Extract username according to official API structure
        extracted_username = (
            safe_get_nested(user_data, ['unique_id']) or
            safe_get_nested(user_data, ['username']) or
            username
        )
        if not isinstance(extracted_username, str):
            extracted_username = str(
                extracted_username) if extracted_username else username

        # Extract bio/signature according to official API structure
        bio = safe_get_nested(user_data, ['signature']) or ""
        if not isinstance(bio, str):
            bio = str(bio) if bio is not None else ""

        # Extract stats according to official API structure with multiple fallbacks
        # Try stats object first, then user object as fallback
        follower_count = safe_int(
            safe_get_nested(stats_data, ['follower_count']) or
            safe_get_nested(user_data, ['follower_count']) or
            safe_get_nested(user_data, ['followerCount']) or
            safe_get_nested(stats_data, ['followerCount'])
        )
        following_count = safe_int(
            safe_get_nested(stats_data, ['following_count']) or
            safe_get_nested(user_data, ['following_count']) or
            safe_get_nested(user_data, ['followingCount']) or
            safe_get_nested(stats_data, ['followingCount'])
        )
        likes_count = safe_int(
            safe_get_nested(stats_data, ['total_favorited']) or
            safe_get_nested(user_data, ['total_favorited']) or
            safe_get_nested(user_data, ['totalFavorited']) or
            safe_get_nested(stats_data, ['totalFavorited']) or
            safe_get_nested(user_data, ['heartCount']) or
            safe_get_nested(stats_data, ['heartCount'])
        )
        video_count = safe_int(
            safe_get_nested(stats_data, ['aweme_count']) or
            safe_get_nested(user_data, ['aweme_count']) or
            safe_get_nested(user_data, ['awemeCount']) or
            safe_get_nested(stats_data, ['awemeCount']) or
            safe_get_nested(user_data, ['videoCount']) or
            safe_get_nested(stats_data, ['videoCount'])
        )

        # Debug logging for troubleshooting
        logger.debug(f"🔍 Profile metrics debug for @{extracted_username}:")
        logger.debug(
            f"  - Stats data keys: {list(stats_data.keys()) if stats_data else 'None'}")
        logger.debug(
            f"  - User data keys: {list(user_data.keys()) if user_data else 'None'}")
        logger.debug(
            f"  - Parsed: followers={follower_count}, following={following_count}, likes={likes_count}, videos={video_count}")

        # Extract avatar URL according to official API structure with comprehensive fallbacks
        avatar_url = self._extract_best_avatar_url(user_data, username)
        if not isinstance(avatar_url, str):
            avatar_url = str(avatar_url) if avatar_url else ""

        # Extract verification status according to official API structure
        verification_type = safe_get_nested(user_data, ['verification_type'])
        is_verified = (
            (isinstance(verification_type, (int, str)) and str(verification_type) == "1") or
            bool(safe_get_nested(user_data, ['is_verified']))
        )

        logger.debug(
            f"📋 Parsed profile @{extracted_username}: followers={follower_count}, videos={video_count}")

        return TikTokProfile(
            username=extracted_username,
            bio=bio[:500],  # Limit bio length for safety
            follower_count=follower_count,
            following_count=following_count,
            likes_count=likes_count,
            video_count=video_count,
            avatar_url=avatar_url[:500],  # Limit URL length for safety
            is_verified=is_verified
        )

    def _parse_posts_data(self, posts_list: List[Dict[str, Any]], count: int) -> List[TikTokPost]:
        """
        Parse posts data from official API response structure

        Args:
            posts_list: List of post objects from API response
            count: Maximum number of posts to return

        Returns:
            List of TikTokPost objects with validated data
        """
        if not isinstance(posts_list, list):
            logger.warning(
                f"Invalid posts data format: expected list, got {type(posts_list)}")
            return []

        posts = []
        for i, post_data in enumerate(posts_list[:count]):
            try:
                if not isinstance(post_data, dict):
                    logger.warning(
                        f"Invalid post data at index {i}: expected dict, got {type(post_data)}")
                    continue

                # Safe integer conversion
                def safe_int(value, default=0):
                    """Safely convert value to non-negative integer"""
                    if isinstance(value, (int, float)):
                        return max(0, int(value))
                    if isinstance(value, str) and value.isdigit():
                        return max(0, int(value))
                    return default

                # Extract post ID according to official API structure
                post_id = (
                    safe_get_nested(post_data, ['aweme_id']) or
                    safe_get_nested(post_data, ['id']) or
                    str(hash(str(post_data)))
                )

                # Extract caption/description according to official API structure
                caption = safe_get_nested(post_data, ['desc']) or ""
                if not isinstance(caption, str):
                    caption = str(caption) if caption is not None else ""

                # Extract statistics according to official API structure
                stats = safe_get_nested(post_data, ['statistics']) or {}
                views = safe_int(stats.get('play_count', 0))
                likes = safe_int(stats.get('digg_count', 0))
                comments = safe_int(stats.get('comment_count', 0))
                shares = safe_int(stats.get('share_count', 0))
                favorites = safe_int(stats.get('collect_count', 0))

                # Extract video URLs according to official API structure
                video_info = safe_get_nested(post_data, ['video']) or {}
                video_url = (
                    safe_get_nested(video_info, ['play_addr', 'url_list', 0]) or
                    safe_get_nested(
                        video_info, ['download_addr', 'url_list', 0]) or ""
                )

                # Generate TikTok URL for direct access
                author_info = safe_get_nested(post_data, ['author']) or {}
                author_username = (
                    safe_get_nested(author_info, ['unique_id']) or
                    safe_get_nested(author_info, ['username']) or ""
                )
                tiktok_url = f"https://www.tiktok.com/@{author_username}/video/{post_id}" if author_username else ""

                # Enhanced image extraction with improved EnsembleData API structure understanding
                # DEBUG: Log available keys for troubleshooting
                logger.debug(f"🔍 Post {post_id} structure analysis:")
                logger.debug(
                    f"   video_info keys: {list(video_info.keys()) if video_info else 'None'}")
                if video_info:
                    logger.debug(
                        f"   cover keys: {list(video_info.get('cover', {}).keys()) if video_info.get('cover') else 'None'}")
                    logger.debug(
                        f"   origin_cover keys: {list(video_info.get('origin_cover', {}).keys()) if video_info.get('origin_cover') else 'None'}")

                # Extract cover image URL with comprehensive fallbacks
                cover_image_url = self._extract_best_cover_image(
                    video_info, post_data, post_id)

                # Validate and clean cover image URL
                if cover_image_url and isinstance(cover_image_url, str):
                    cover_image_url = cover_image_url.strip()
                    # Ensure URL is valid (starts with http/https)
                    if not cover_image_url.startswith(('http://', 'https://')):
                        if cover_image_url.startswith('//'):
                            cover_image_url = 'https:' + cover_image_url
                        else:
                            logger.warning(
                                f"⚠️ Invalid cover image URL format: {cover_image_url}")
                            cover_image_url = ""

                    # Debug logging for image URLs
                    if cover_image_url:
                        logger.debug(
                            f"📸 Found cover image: {cover_image_url[:100]}...")
                    else:
                        logger.debug(
                            f"📸 No cover image found for post {post_id}")
                        # Debug: log available video_info keys
                        logger.debug(
                            f"🔍 Available video keys: {list(video_info.keys()) if video_info else 'None'}")
                else:
                    cover_image_url = ""

                # Extract additional images using improved method
                additional_images = self._extract_additional_images(
                    video_info, post_data, cover_image_url, post_id)

                # КРИТИЧНО: Если cover пустой, но есть additional images - используем первую как cover!
                if not cover_image_url and additional_images:
                    cover_image_url = additional_images[0]
                    # Остальные - в additional
                    additional_images = additional_images[1:]
                    logger.info(
                        f"✅ Post {post_id}: Used first additional image as cover")

                logger.info(
                    f"📸 Post {post_id}: cover='{cover_image_url[:80] if cover_image_url else 'None'}{'...' if cover_image_url and len(cover_image_url) > 80 else ''}'")
                logger.info(
                    f"📸 Post {post_id}: found {len(additional_images)} additional images")
                if additional_images:
                    for i, img in enumerate(additional_images[:3]):
                        logger.info(
                            f"📸 Post {post_id}: img[{i}] = '{img[:80]}{'...' if len(img) > 80 else ''}')")

                # Parse timestamp according to official API structure
                create_time = self._parse_timestamp(
                    safe_get_nested(post_data, ['create_time'])
                )

                # Validate required fields before creating post
                if not post_id:
                    logger.warning(
                        f"⚠️ Skipping post at index {i}: missing post_id")
                    continue

                # Ensure create_time is never empty (already guaranteed by _parse_timestamp)
                if not create_time:
                    logger.error(
                        f"⚠️ Critical: create_time is empty for post {post_id}")
                    import datetime
                    create_time = datetime.datetime.now(
                        datetime.timezone.utc).isoformat().replace('+00:00', 'Z')

                # Extract hashtags from description
                hashtags = extract_hashtags_from_text(caption)

                # Parse author information
                from models import TikTokAuthor
                author_avatar = self._extract_best_avatar_url(
                    author_info, author_username or "unknown")
                author_verified = bool(safe_get_nested(
                    author_info, ['is_verified']))

                author = TikTokAuthor(
                    username=author_username,
                    avatar_url=author_avatar[:500] if isinstance(
                        author_avatar, str) else "",
                    is_verified=author_verified
                )

                post = TikTokPost(
                    id=str(post_id),
                    caption=caption[:1000],  # Limit caption length for safety
                    views=views,
                    likes=likes,
                    comments=comments,
                    shares=shares,
                    favorites=favorites,
                    create_time=create_time,
                    video_url=video_url[:500] if isinstance(
                        video_url, str) else "",
                    cover_image_url=cover_image_url[:500] if isinstance(
                        cover_image_url, str) else "",
                    images=[img[:500] for img in additional_images if isinstance(
                        img, str)],  # Additional images with URL length limit
                    hashtags=hashtags[:10],  # Limit hashtags for safety
                    author=author,
                    tiktok_url=tiktok_url[:500] if isinstance(
                        tiktok_url, str) else ""
                )
                posts.append(post)

            except Exception as e:
                logger.warning(
                    f"⚠️ Failed to parse post data at index {i}: {e}")
                continue

        logger.debug(
            f"📱 Successfully parsed {len(posts)} posts from {len(posts_list)} raw posts")
        return posts

    def _parse_hashtag_posts(
        self,
        posts_list: List[Dict[str, Any]],
        hashtag: str,
        count: int
    ) -> List[TikTokPost]:
        """
        Parse hashtag search results into TikTokPost models

        Args:
            posts_list: List of post objects from hashtag search
            hashtag: The hashtag being searched
            count: Maximum number of posts to return

        Returns:
            List of TikTokPost objects
        """
        logger.debug(
            f"🔍 Parsing hashtag posts for #{hashtag}: {len(posts_list) if isinstance(posts_list, list) else 0} posts")

        # Use the same parsing logic as regular posts
        return self._parse_posts_data(posts_list, count)

    def _extract_best_cover_image(self, video_info: dict, post_data: dict, post_id: str) -> str:
        """
        Extract the best available cover image from TikTok post data
        Based on EnsembleData API structure with extensive fallbacks
        """
        cover_image_url = ""

        try:
            # Priority 1: Standard TikTok video covers (highest quality)
            cover_sources = [
                # High-quality covers
                ['cover', 'url_list', 0],
                ['cover', 'url_list', 1],
                ['cover', 'url_list', 2],
                ['origin_cover', 'url_list', 0],
                ['origin_cover', 'url_list', 1],
                ['origin_cover', 'url_list', 2],

                # Dynamic and AI covers
                ['dynamic_cover', 'url_list', 0],
                ['dynamic_cover', 'url_list', 1],
                ['ai_dynamic_cover', 'url_list', 0],
                ['ai_dynamic_cover', 'url_list', 1],
                ['ai_cover', 'url_list', 0],
                ['ai_cover', 'url_list', 1],

                # Alternative covers
                ['cover_original_scale', 'url_list', 0],
                ['cover_hd', 'url_list', 0],
                ['cover_medium', 'url_list', 0],
                ['cover_thumb', 'url_list', 0],

                # Direct URL fallbacks (no url_list)
                ['cover'],
                ['origin_cover'],
                ['dynamic_cover'],
                ['ai_dynamic_cover'],
                ['ai_cover']
            ]

            # Try video_info sources first
            if video_info:
                for source_path in cover_sources:
                    url = safe_get_nested(video_info, source_path)
                    if url and isinstance(url, str) and url.strip():
                        cover_image_url = url.strip()
                        logger.debug(
                            f"📸 Found cover from video_info.{'.'.join(source_path)}: {cover_image_url[:100]}")
                        break

            # Priority 2: Try post_data video covers if not found
            if not cover_image_url and post_data:
                post_video_sources = [
                    ['video', 'cover', 'url_list', 0],
                    ['video', 'cover_original_scale', 'url_list', 0],
                    ['video', 'cover_hd', 'url_list', 0],
                    ['video', 'cover_medium', 'url_list', 0],
                    ['video', 'cover_thumb', 'url_list', 0],
                    ['video', 'origin_cover', 'url_list', 0],
                    ['video', 'dynamic_cover', 'url_list', 0],
                ]

                for source_path in post_video_sources:
                    url = safe_get_nested(post_data, source_path)
                    if url and isinstance(url, str) and url.strip():
                        cover_image_url = url.strip()
                        logger.debug(
                            f"📸 Found cover from post_data.{'.'.join(source_path)}: {cover_image_url[:100]}")
                        break

            # Priority 3: Image carousel posts (TikTok supports image posts)
            if not cover_image_url:
                image_sources = [
                    ['image_post_info', 'images', 0, 'image_url', 'url_list', 0],
                    ['image_post_info', 'images', 0,
                        'display_image', 'url_list', 0],
                    ['image_post_info', 'images', 0,
                        'owner_watermark_image', 'url_list', 0],
                    ['images', 0, 'image_url', 'url_list', 0],
                    ['images', 0, 'display_image', 'url_list', 0],
                ]

                for source_path in image_sources:
                    url = safe_get_nested(post_data, source_path)
                    if url and isinstance(url, str) and url.strip():
                        cover_image_url = url.strip()
                        logger.debug(
                            f"📸 Found image from {'.'.join(source_path)}: {cover_image_url[:100]}")
                        break

            # Priority 4: Author avatar as last resort
            if not cover_image_url:
                author_sources = [
                    ['author', 'avatar_larger', 'url_list', 0],
                    ['author', 'avatar_medium', 'url_list', 0],
                    ['author', 'avatar_thumb', 'url_list', 0],
                ]

                for source_path in author_sources:
                    url = safe_get_nested(post_data, source_path)
                    if url and isinstance(url, str) and url.strip():
                        cover_image_url = url.strip()
                        logger.debug(
                            f"📸 Using author avatar from {'.'.join(source_path)}: {cover_image_url[:100]}")
                        break

            # Normalize URL
            if cover_image_url:
                # Fix protocol-relative URLs
                if cover_image_url.startswith('//'):
                    cover_image_url = 'https:' + cover_image_url
                # Validate URL format
                elif not cover_image_url.startswith(('http://', 'https://')):
                    logger.warning(
                        f"⚠️ Invalid image URL format for post {post_id}: {cover_image_url}")
                    cover_image_url = ""

            # Final validation
            if cover_image_url and len(cover_image_url) > 500:
                logger.warning(
                    f"⚠️ Image URL too long for post {post_id}, truncating")
                cover_image_url = cover_image_url[:500]

        except Exception as e:
            logger.error(
                f"❌ Error extracting cover image for post {post_id}: {e}")
            cover_image_url = ""

        # Log result
        if cover_image_url:
            logger.info(
                f"✅ Post {post_id}: Found cover image ({len(cover_image_url)} chars)")
        else:
            logger.warning(f"⚠️ Post {post_id}: No cover image found")
            # Log available structure for debugging
            if video_info:
                logger.debug(
                    f"   Available video_info keys: {list(video_info.keys())}")
            if post_data:
                logger.debug(
                    f"   Available post_data keys: {list(post_data.keys())}")

        return cover_image_url

    def _extract_additional_images(self, video_info: dict, post_data: dict, cover_image_url: str, post_id: str) -> List[str]:
        """
        Extract additional images from TikTok post (carousel images, alternative thumbnails)
        """
        additional_images = []

        try:
            # Priority 1: Image carousel posts (TikTok supports multiple images in one post)
            image_carousel_sources = [
                ['image_post_info', 'images'],
                ['images'],  # Alternative structure
            ]

            for carousel_path in image_carousel_sources:
                images_data = safe_get_nested(post_data, carousel_path) or []
                if isinstance(images_data, list) and images_data:
                    logger.debug(
                        f"📸 Post {post_id}: Found {len(images_data)} carousel images")

                    # Max 6 additional images
                    for i, img_data in enumerate(images_data[:6]):
                        if not isinstance(img_data, dict):
                            continue

                        # Try multiple sources for each image
                        img_url = None
                        for source in ['image_url', 'display_image', 'owner_watermark_image', 'user_watermark_image', 'thumbnail']:
                            url_candidates = [
                                safe_get_nested(
                                    img_data, [source, 'url_list', 0]),
                                safe_get_nested(
                                    img_data, [source, 'url_list', 1]),
                                safe_get_nested(
                                    img_data, [source]),  # Direct URL
                            ]

                            for url in url_candidates:
                                if url and isinstance(url, str) and url.strip():
                                    img_url = url.strip()
                                    break

                            if img_url:
                                break

                        # Validate and add image
                        if img_url and self._is_valid_image_url(img_url) and img_url != cover_image_url:
                            if img_url not in additional_images:
                                additional_images.append(img_url)
                                logger.debug(
                                    f"📸 Added carousel image {i+1}: {img_url[:80]}")

                    if additional_images:
                        break  # Found images in this source, no need to try others

            # Priority 2: Alternative video thumbnails/covers (if we have room for more)
            if len(additional_images) < 5 and video_info:
                alt_thumbnail_sources = [
                    # Different quality levels
                    ['cover', 'url_list'],
                    ['origin_cover', 'url_list'],
                    ['dynamic_cover', 'url_list'],
                    ['ai_dynamic_cover', 'url_list'],
                    ['ai_cover', 'url_list'],
                ]

                for source_path in alt_thumbnail_sources:
                    url_list = safe_get_nested(video_info, source_path) or []
                    if isinstance(url_list, list):
                        # Skip first few URLs if they might be the cover image
                        start_index = 1 if source_path[0] in [
                            'cover', 'origin_cover'] else 0

                        for i in range(start_index, min(len(url_list), start_index + 3)):
                            url = url_list[i]
                            if (url and isinstance(url, str) and
                                self._is_valid_image_url(url) and
                                url != cover_image_url and
                                    url not in additional_images):

                                additional_images.append(url.strip())
                                logger.debug(
                                    f"📸 Added alt thumbnail: {url[:80]}")

                                if len(additional_images) >= 5:
                                    break

                    if len(additional_images) >= 5:
                        break

            # Priority 3: Music/sound cover (if available and still have room)
            if len(additional_images) < 5:
                music_sources = [
                    ['music', 'cover_large', 'url_list', 0],
                    ['music', 'cover_medium', 'url_list', 0],
                    ['music', 'cover_thumb', 'url_list', 0],
                ]

                for source_path in music_sources:
                    url = safe_get_nested(post_data, source_path)
                    if (url and isinstance(url, str) and
                        self._is_valid_image_url(url) and
                        url != cover_image_url and
                            url not in additional_images):

                        additional_images.append(url.strip())
                        logger.debug(f"📸 Added music cover: {url[:80]}")
                        break

        except Exception as e:
            logger.error(
                f"❌ Error extracting additional images for post {post_id}: {e}")

        # Final validation and cleanup
        validated_images = []
        for img_url in additional_images:
            if len(img_url) <= 500:  # URL length limit
                validated_images.append(img_url)
            else:
                logger.warning(
                    f"⚠️ Image URL too long, skipping: {img_url[:100]}...")

        logger.debug(
            f"📸 Post {post_id}: Extracted {len(validated_images)} additional images")
        return validated_images

    def _is_valid_image_url(self, url: str) -> bool:
        """Validate image URL format and basic structure"""
        if not url or not isinstance(url, str):
            return False

        url = url.strip()

        # Fix protocol-relative URLs
        if url.startswith('//'):
            url = 'https:' + url

        # Must start with valid protocol
        if not url.startswith(('http://', 'https://')):
            return False

        # Basic URL structure validation
        if len(url) < 10 or len(url) > 500:
            return False

        # Should contain image-like patterns (optional but helpful)
        # Most TikTok images have these patterns
        return True

    def _parse_timestamp(self, timestamp: Optional[int]) -> str:
        """
        Parse timestamp to ISO format according to official API structure

        Args:
            timestamp: Unix timestamp from API response

        Returns:
            ISO formatted timestamp string (always valid, never empty)
        """
        import datetime

        # If timestamp is None, empty, or 0 - return current time in UTC
        if not timestamp:
            return datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00', 'Z')

        try:
            # Handle both integer and string timestamps
            if isinstance(timestamp, str):
                timestamp = int(timestamp)
            elif not isinstance(timestamp, (int, float)):
                logger.warning(
                    f"⚠️ Invalid timestamp type: {type(timestamp)}, using current time")
                return datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00', 'Z')

            # Create datetime from timestamp with UTC timezone
            dt = datetime.datetime.fromtimestamp(
                int(timestamp), datetime.timezone.utc)
            return dt.isoformat().replace('+00:00', 'Z')

        except (ValueError, TypeError, OSError) as e:
            logger.warning(
                f"⚠️ Failed to parse timestamp {timestamp}: {e}, using current time")
            return datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00', 'Z')

    def _extract_best_avatar_url(self, user_data: dict, username: str) -> str:
        """
        Extract the best available avatar URL from TikTok user data
        Based on EnsembleData API structure with comprehensive fallbacks and validation
        """
        avatar_url = ""

        try:
            # Priority 1: Standard TikTok avatar URLs (highest quality first)
            avatar_sources = [
                # High-quality avatars
                ['avatar_larger', 'url_list', 0],
                ['avatar_larger', 'url_list', 1],
                ['avatar_larger', 'url_list', 2],
                ['avatar_300x300', 'url_list', 0],
                ['avatar_168x168', 'url_list', 0],
                ['avatar_medium', 'url_list', 0],
                ['avatar_medium', 'url_list', 1],
                ['avatar_medium', 'url_list', 2],

                # Lower quality fallbacks
                ['avatar_thumb', 'url_list', 0],
                ['avatar_thumb', 'url_list', 1],
                ['avatar_thumb', 'url_list', 2],
                ['avatar_100x100', 'url_list', 0],
                ['avatar_68x68', 'url_list', 0],

                # Direct URL fallbacks (no url_list)
                ['avatar_larger'],
                ['avatar_medium'],
                ['avatar_thumb'],
                ['avatar_300x300'],
                ['avatar_168x168'],
                ['avatar_100x100'],
                ['avatar_68x68'],
            ]

            # Try all avatar sources
            for source_path in avatar_sources:
                url = safe_get_nested(user_data, source_path)
                if url and isinstance(url, str) and url.strip():
                    # Validate the URL
                    candidate_url = self._validate_and_fix_avatar_url(
                        url.strip(), username)
                    if candidate_url:
                        avatar_url = candidate_url
                        logger.debug(
                            f"📸 Found avatar from user_data.{'.'.join(source_path)}: {avatar_url[:100]}")
                        break

            # Priority 2: Alternative avatar structures
            if not avatar_url:
                alternative_sources = [
                    ['avatar', 'url_list', 0],
                    ['avatar', 'url_list', 1],
                    ['avatar_url'],
                    ['avatar'],
                    ['user_avatar'],
                    ['profile_pic'],
                    ['profile_image'],
                ]

                for source_path in alternative_sources:
                    url = safe_get_nested(user_data, source_path)
                    if url and isinstance(url, str) and url.strip():
                        candidate_url = self._validate_and_fix_avatar_url(
                            url.strip(), username)
                        if candidate_url:
                            avatar_url = candidate_url
                            logger.debug(
                                f"📸 Found avatar from alternative {'.'.join(source_path)}: {avatar_url[:100]}")
                            break

            # Log result
            if avatar_url:
                logger.info(
                    f"✅ User @{username}: Found avatar ({len(avatar_url)} chars)")
            else:
                logger.warning(f"⚠️ User @{username}: No avatar found")
                # Debug: log available user_data keys
                if user_data:
                    logger.debug(
                        f"   Available user_data keys: {list(user_data.keys())}")

        except Exception as e:
            logger.error(f"❌ Error extracting avatar for @{username}: {e}")
            avatar_url = ""

        return avatar_url

    def _validate_and_fix_avatar_url(self, url: str, username: str) -> str:
        """
        Validate and fix avatar URL format

        Args:
            url: Raw avatar URL
            username: Username for logging context

        Returns:
            Valid avatar URL or empty string if invalid
        """
        if not url:
            return ""

        try:
            url = url.strip()

            # Fix protocol-relative URLs
            if url.startswith('//'):
                url = 'https:' + url

            # Must start with valid protocol
            if not url.startswith(('http://', 'https://')):
                logger.warning(
                    f"⚠️ Invalid avatar URL format for @{username}: {url[:100]}")
                return ""

            # Basic URL structure validation
            if len(url) < 10:
                logger.warning(
                    f"⚠️ Avatar URL too short for @{username}: {url}")
                return ""

            if len(url) > 500:
                logger.warning(
                    f"⚠️ Avatar URL too long for @{username}, truncating")
                url = url[:500]

            # Check for common invalid patterns
            invalid_patterns = [
                'placeholder',
                'default_avatar',
                'no_image',
                'missing_image',
                'error',
                '404'
            ]

            url_lower = url.lower()
            for pattern in invalid_patterns:
                if pattern in url_lower:
                    logger.warning(
                        f"⚠️ Avatar URL contains invalid pattern '{pattern}' for @{username}")
                    return ""

            # Check for valid image-like extensions (optional but helpful)
            valid_extensions = ['.jpg', '.jpeg',
                                '.png', '.gif', '.webp', '.avif']
            has_extension = any(url_lower.endswith(ext)
                                for ext in valid_extensions)

            # Most TikTok avatars don't have extensions in URL, so this is just a helpful check
            if has_extension:
                logger.debug(
                    f"📸 Avatar URL has valid image extension for @{username}")

            return url

        except Exception as e:
            logger.error(f"❌ Error validating avatar URL for @{username}: {e}")
            return ""
