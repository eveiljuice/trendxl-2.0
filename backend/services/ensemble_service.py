"""
Ensemble Data API Service for TikTok data - Official SDK Implementation
"""
import logging
import math
import asyncio
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
        try:
            self.client = EDClient(settings.ensemble_api_token)
            logger.info("✅ Ensemble Data SDK client initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Ensemble Data client: {e}")
            raise Exception(
                f"Ensemble Data client initialization failed: {str(e)}")

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

            # Filter high-quality results with more inclusive threshold
            quality_posts = [post for post in posts if post.views > 100]

            # If no quality posts, use lower threshold
            if not quality_posts and posts:
                logger.info(
                    f"🔍 No posts > 100 views, using lower threshold for #{clean_hashtag}")
                quality_posts = [post for post in posts if post.views > 10]

            final_posts = quality_posts[:count] if quality_posts else posts[:count]
            logger.info(
                f"✅ Found {len(final_posts)} quality posts for #{clean_hashtag}")

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

        # Extract avatar URL according to official API structure
        avatar_url = (
            safe_get_nested(user_data, ['avatar_larger', 'url_list', 0]) or
            safe_get_nested(user_data, ['avatar_medium', 'url_list', 0]) or
            safe_get_nested(user_data, ['avatar_thumb', 'url_list', 0]) or ""
        )
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

                # Extract cover image URL according to official API structure
                cover_image_url = (
                    safe_get_nested(video_info, ['cover', 'url_list', 0]) or
                    safe_get_nested(
                        video_info, ['origin_cover', 'url_list', 0]) or ""
                )

                # Parse timestamp according to official API structure
                create_time = self._parse_timestamp(
                    safe_get_nested(post_data, ['create_time'])
                )

                # Extract hashtags from description
                hashtags = extract_hashtags_from_text(caption)

                # Parse author information
                from models import TikTokAuthor
                author_avatar = (
                    safe_get_nested(author_info, ['avatar_larger', 'url_list', 0]) or
                    safe_get_nested(author_info, ['avatar_medium', 'url_list', 0]) or
                    safe_get_nested(
                        author_info, ['avatar_thumb', 'url_list', 0]) or ""
                )
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

    def _parse_timestamp(self, timestamp: Optional[int]) -> str:
        """
        Parse timestamp to ISO format according to official API structure

        Args:
            timestamp: Unix timestamp from API response

        Returns:
            ISO formatted timestamp string
        """
        import datetime

        if not timestamp:
            return datetime.datetime.now().isoformat() + 'Z'

        try:
            # Handle both integer and string timestamps
            if isinstance(timestamp, str):
                timestamp = int(timestamp)
            elif not isinstance(timestamp, (int, float)):
                return datetime.datetime.now().isoformat() + 'Z'

            # Create datetime from timestamp
            dt = datetime.datetime.fromtimestamp(int(timestamp))
            return dt.isoformat() + 'Z'

        except (ValueError, TypeError, OSError) as e:
            logger.warning(f"⚠️ Failed to parse timestamp {timestamp}: {e}")
            return datetime.datetime.now().isoformat() + 'Z'
