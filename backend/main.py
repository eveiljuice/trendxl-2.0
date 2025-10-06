"""
TrendXL 2.0 Backend - FastAPI Application
"""
import os
import logging
import asyncio
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from config import settings
from models import (
    TikTokProfile,
    TrendAnalysisRequest,
    TrendAnalysisResponse,
    ProfileRequest,
    PostsRequest,
    PostsResponse,
    HashtagSearchRequest,
    HashtagSearchResponse,
    UserSearchRequest,
    UserSearchResponse,
    CreativeCenterHashtag,
    NicheHashtagRequest,
    NicheHashtagResponse,
    CreativeCenterAnalysisRequest,
    CreativeCenterAnalysisResponse,
    ErrorResponse,
    HealthCheckResponse
)
from services.trend_analysis_service import trend_service
from services.cache_service import cache_service
from services.perplexity_service import perplexity_service
from services.content_relevance_service import content_relevance_service
from services.advanced_creative_center_service import advanced_creative_center_service
from utils import RateLimiter, get_current_timestamp
from auth_service_supabase import (
    UserCreate, UserLogin, UserProfile, UserProfileUpdate, Token, TokenData,
    verify_password, get_password_hash, create_access_token, decode_access_token,
    user_to_profile, register_user, login_user, get_current_user as get_current_user_from_token,
    update_user_profile as update_profile_service, logout_user
)
# Import Supabase helpers
from supabase_client import (
    get_supabase,
    check_user_can_analyze,
    record_free_trial_usage,
    get_free_trial_info,
    insert_user as create_user_supabase,
    get_user_by_link,
    record_token_usage,
    get_user_token_usage,
    get_user_token_summary,
    get_user_token_usage_by_period,
    update_user_stripe_customer,
    update_user_subscription,
    get_user_subscription_info,
    check_active_subscription,
    get_user_by_stripe_customer_id
)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from error_responses import (
    UserAlreadyExistsError,
    UserNotFoundError,
    InvalidCredentialsError,
    parse_supabase_error
)
from stripe_service import (
    create_stripe_customer,
    create_subscription,
    get_subscription,
    get_customer_subscriptions,
    cancel_subscription,
    reactivate_subscription,
    create_checkout_session,
    create_public_payment_link
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Rate limiter
rate_limiter = RateLimiter(settings.max_requests_per_minute)

# Security
security = HTTPBearer(auto_error=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🚀 TrendXL 2.0 Backend starting up...")

    # Test service connections
    cache_healthy = await cache_service.health_check()
    logger.info(
        f"📋 Cache service: {'✅ Connected' if cache_healthy else '❌ Disconnected (fallback mode)'}")

    # Test API keys
    ensemble_token = getattr(settings, 'ensemble_api_token', None)
    openai_key = getattr(settings, 'openai_api_key', None)
    perplexity_key = getattr(settings, 'perplexity_api_key', None)

    logger.info(
        f"🔑 Ensemble API: {'✅ Configured' if ensemble_token else '❌ Missing'}")
    logger.info(
        f"🔑 OpenAI API: {'✅ Configured' if openai_key else '❌ Missing'}")
    logger.info(
        f"🔑 Perplexity API: {'✅ Configured' if perplexity_key else '❌ Missing'}")

    # Test Perplexity service health
    perplexity_healthy = await perplexity_service.health_check()
    logger.info(
        f"🎯 Perplexity service: {'✅ Connected' if perplexity_healthy else '❌ Disconnected (fallback mode)'}")

    if not ensemble_token or not openai_key or not perplexity_key:
        logger.warning(
            "⚠️  Some API keys missing - service will use fallback/demo mode")
    else:
        logger.info("✅ All services configured properly")

    yield

    # Shutdown
    logger.info("🛑 TrendXL 2.0 Backend shutting down...")
    await perplexity_service.close()
    await content_relevance_service.close()

# Create FastAPI app
# Check if running in serverless environment (Vercel)
is_serverless = os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME")

app = FastAPI(
    title="TrendXL 2.0 Backend API",
    description="TikTok Trend Analysis API using Ensemble Data and OpenAI",
    version="2.0.0",
    lifespan=None if is_serverless else lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=getattr(settings, 'cors_origin_regex', None),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting dependency - temporarily disabled
# async def check_rate_limit(http_request):
#     """Check rate limiting"""
#     client_ip = http_request.client.host if http_request.client else "unknown"
#
#     if not rate_limiter.is_allowed(client_ip):
#         reset_time = rate_limiter.get_reset_time(client_ip)
#         raise HTTPException(
#             status_code=429,
#             detail=f"Rate limit exceeded. Try again in {reset_time} seconds.",
#             headers={"Retry-After": str(reset_time)}
#         )

# Global exception handlers


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            code=f"HTTP_{exc.status_code}"
        ).model_dump()
    )


@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    """Handle validation errors"""
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error="Validation error in request data",
            code="VALIDATION_ERROR",
            details=exc.errors()
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            code="INTERNAL_ERROR"
        ).model_dump()
    )

# Health check endpoint


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint"""
    cache_status = await cache_service.health_check()

    return HealthCheckResponse(
        status="healthy" if cache_status else "degraded",
        timestamp=get_current_timestamp(),
        services={
            "cache": cache_status,
            "ensemble_api": True,  # Will be tested in actual requests
            "openai_api": True,    # Will be tested in actual requests
            "perplexity_api": await perplexity_service.health_check()
        }
    )

# Simple connectivity test endpoint (no mock data)


@app.get("/api/v1/ping")
async def ping():
    """Simple ping endpoint to test connectivity"""
    return {
        "status": "ok",
        "message": "TrendXL 2.0 Backend is running",
        "timestamp": get_current_timestamp(),
        "version": "2.0.0"
    }

# Status endpoint


@app.get("/api/v1/status")
async def get_status():
    """Get detailed service status"""
    cache_healthy = await cache_service.health_check()

    return {
        "status": "running",
        "version": "2.0.0",
        "timestamp": get_current_timestamp(),
        "services": {
            "cache": cache_healthy,
            "ensemble_api": bool(getattr(settings, 'ensemble_api_token', None)),
            "openai_api": bool(getattr(settings, 'openai_api_key', None)),
            "perplexity_api": bool(getattr(settings, 'perplexity_api_key', None))
        },
        "config": {
            "debug": settings.debug,
            "host": settings.host,
            "port": settings.port
        }
    }

# Main trend analysis endpoint


@app.post("/api/v1/analyze", response_model=TrendAnalysisResponse)
async def analyze_trends(
    request: TrendAnalysisRequest,
    current_user: Optional[UserProfile] = Depends(get_current_user)
):
    """
    Analyze TikTok profile trends

    This endpoint performs a complete trend analysis:
    1. Fetches user profile and posts
    2. Analyzes posts with AI to extract relevant hashtags  
    3. Searches trending videos for each hashtag
    4. Returns comprehensive analysis results

    Free users get 1 analysis per day. Subscription required for unlimited access.
    """
    try:
        # Check if user is authenticated
        if not current_user:
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "Authentication required",
                    "message": "Please log in to use trend analysis.",
                    "action": "login"
                }
            )

        # Admins bypass all checks
        # Track if this is a free trial usage (before analysis)
        is_free_trial_usage = False

        if current_user.is_admin:
            logger.info(
                f"🔑 Admin user {current_user.username} bypassing all checks")
        else:
            # Check if user can analyze (subscription or free trial)
            can_analyze, reason, details = await check_user_can_analyze(current_user.id)

            if not can_analyze:
                trial_info = details.get("trial_info", {})
                today_count = trial_info.get(
                    "today_count", 0) if trial_info else 0

                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "Analysis limit reached",
                        "message": details.get("message", "You've used your free daily analysis. Subscribe to get unlimited access!"),
                        "today_count": today_count,
                        "action": "subscribe",
                        "type": "free_trial_exhausted"
                    }
                )

            # Log what type of access user is using
            if reason == "free_trial":
                is_free_trial_usage = True
                logger.info(
                    f"🎁 User {current_user.username} using FREE TRIAL (1/day)")
            elif reason == "active_subscription":
                logger.info(
                    f"💳 User {current_user.username} using SUBSCRIPTION")

        print(f"\n{'='*80}")
        print(f"🚀 BACKEND: NEW ANALYSIS REQUEST RECEIVED!")
        print(f"🎯 Profile URL: {request.profile_url}")
        print(f"👤 User: {current_user.username} (ID: {current_user.id})")
        print(f"{'='*80}\n")
        logger.info(f"🎯 Trend analysis requested for: {request.profile_url}")

        # Extract username for caching and tracking
        from utils import extract_tiktok_username
        username = extract_tiktok_username(request.profile_url)
        logger.info(f"✅ Extracted username from URL: '{username}'")
        print(f"✅ Extracted username: '{username}'")

        # CRITICAL: Record free trial usage IMMEDIATELY for free users
        # Free trial is consumed on EVERY request (cached or not)
        # Only paid subscribers get benefit of cached results
        if is_free_trial_usage:
            try:
                success = await record_free_trial_usage(current_user.id, username)
                if not success:
                    # Should not happen with new exception handling, but check anyway
                    logger.error(
                        f"❌ record_free_trial_usage returned False for {current_user.username}")
                    raise HTTPException(
                        status_code=500,
                        detail="Failed to record free trial usage. Please try again."
                    )
                logger.info(
                    f"🎁 Free trial used by {current_user.username} for @{username}")
            except HTTPException:
                raise  # Re-raise HTTP exceptions as-is
            except Exception as e:
                logger.error(f"❌ Failed to record free trial usage: {e}")
                logger.error(f"❌ Error type: {type(e).__name__}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to record free trial usage: {str(e)}"
                )

        # Check cache - but free trial users already consumed their attempt
        # Paid subscribers benefit from faster cached responses
        cached_result = await trend_service.get_cached_analysis(username)

        if cached_result:
            print(f"📋 BACKEND: Returning CACHED result for @{username}")
            if is_free_trial_usage:
                logger.info(
                    f"📋 Cached result for @{username} (free trial already consumed)")
            else:
                logger.info(f"📋 Cached result for @{username} (subscription)")
            return cached_result

        # Acquire lock to prevent duplicate processing
        lock_name = f"analysis:{current_user.id}:{username}"
        lock_acquired = await cache_service.acquire_lock(lock_name, timeout=60)

        if not lock_acquired:
            # Another request is already processing, wait and check cache
            logger.info(
                f"🔒 Analysis in progress for @{username}, waiting for result...")
            import asyncio
            await asyncio.sleep(2)  # Wait 2 seconds
            cached_result = await trend_service.get_cached_analysis(username)

            if cached_result:
                logger.info(f"📋 Found cached result after waiting")
                return cached_result
            else:
                raise HTTPException(
                    status_code=409,
                    detail="Analysis already in progress for this profile. Please wait a moment and try again."
                )

        try:
            print(f"🔄 BACKEND: Starting NEW analysis (no cache found)...")
            print(f"   - max_hashtags: 5")
            print(f"   - videos_per_hashtag: 8")

            # Perform new analysis - increased videos per hashtag to ensure 10+ total videos
            result = await trend_service.analyze_profile_trends(
                profile_input=request.profile_url,
                max_hashtags=5,
                videos_per_hashtag=8  # Increased from 4 to 8 to compensate for filters
            )
        finally:
            # Always release the lock
            await cache_service.release_lock(lock_name)

        print(f"✅ BACKEND: Analysis completed for @{username}")
        print(f"   - Found {len(result.trends)} trends")

        # Record token usage
        if result.token_usage:
            try:
                await record_token_usage(
                    user_id=current_user.id,
                    openai_prompt_tokens=result.token_usage.openai_prompt_tokens,
                    openai_completion_tokens=result.token_usage.openai_completion_tokens,
                    perplexity_prompt_tokens=result.token_usage.perplexity_prompt_tokens,
                    perplexity_completion_tokens=result.token_usage.perplexity_completion_tokens,
                    ensemble_units=result.token_usage.ensemble_units,
                    total_cost_estimate=result.token_usage.total_cost_estimate,
                    profile_analyzed=username
                )
                print(
                    f"💾 Token usage recorded for user {current_user.username}")
                logger.info(
                    f"💾 Token usage recorded for user {current_user.id}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to record token usage: {e}")

        print(f"{'='*80}\n")
        logger.info(f"✅ Analysis completed for @{username}")
        return result

    except Exception as e:
        print(f"\n❌ BACKEND ERROR: Analysis failed!")
        print(f"   Error: {e}")
        print(f"   Error type: {type(e).__name__}")
        print(f"{'='*80}\n")
        logger.error(f"Analysis failed: {e}")

        # Return appropriate error message
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        elif "rate limit" in str(e).lower() or "too many requests" in str(e).lower():
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again in a few minutes. The API has usage limits to ensure fair access for all users."
            )
        elif "authentication" in str(e).lower() or "api key" in str(e).lower():
            raise HTTPException(
                status_code=503, detail="API service temporarily unavailable")
        else:
            raise HTTPException(
                status_code=500, detail=f"Analysis failed: {str(e)}")

# Profile endpoint


@app.post("/api/v1/profile", response_model=TikTokProfile)
async def get_profile(
    request: ProfileRequest
    # rate_limit: None = Depends(check_rate_limit)
):
    """Get TikTok user profile information"""
    try:
        profile = await trend_service.get_profile_only(request.username)
        # Ensure response conforms to model even if mocked in tests
        if isinstance(profile, TikTokProfile):
            return profile
        # Try dict coercion first
        if isinstance(profile, dict):
            return TikTokProfile(**profile)
        # Fallback: build from attributes defensively
        return TikTokProfile(
            username=getattr(profile, 'username', ''),
            bio=getattr(profile, 'bio', '') or "",
            follower_count=int(getattr(profile, 'follower_count', 0) or 0),
            following_count=int(getattr(profile, 'following_count', 0) or 0),
            likes_count=int(getattr(profile, 'likes_count', 0) or 0),
            video_count=int(getattr(profile, 'video_count', 0) or 0),
            avatar_url=str(getattr(profile, 'avatar_url', '') or ""),
            is_verified=bool(getattr(profile, 'is_verified', False) or False),
        )
    except Exception as e:
        logger.error(f"Profile fetch failed for @{request.username}: {e}")

        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=404, detail=f"Profile @{request.username} not found")
        else:
            raise HTTPException(status_code=500, detail=str(e))

# Posts endpoint


@app.post("/api/v1/posts", response_model=PostsResponse)
async def get_posts(
    request: PostsRequest
    # rate_limit: None = Depends(check_rate_limit)
):
    """Get TikTok user posts"""
    try:
        posts = await trend_service.get_posts_only(
            username=request.username,
            count=request.count,
            cursor=request.cursor
        )

        return PostsResponse(
            posts=posts,
            cursor=None  # Cursor handling can be added later
        )
    except Exception as e:
        logger.error(f"Posts fetch failed for @{request.username}: {e}")

        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=404, detail=f"Posts for @{request.username} not found")
        else:
            raise HTTPException(status_code=500, detail=str(e))

# Hashtag search endpoint


@app.post("/api/v1/hashtag/search", response_model=HashtagSearchResponse)
async def search_hashtag(
    request: HashtagSearchRequest
    # rate_limit: None = Depends(check_rate_limit)
):
    """Search TikTok posts by hashtag"""
    try:
        posts = await trend_service.search_hashtag_only(
            hashtag=request.hashtag,
            count=request.count,
            period=request.period,
            sorting=request.sorting
        )

        return HashtagSearchResponse(
            posts=posts,
            cursor=None,  # Can be implemented for pagination
            total=len(posts)
        )
    except Exception as e:
        logger.error(f"Hashtag search failed for #{request.hashtag}: {e}")

        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=404, detail=f"No posts found for #{request.hashtag}")
        else:
            raise HTTPException(status_code=500, detail=str(e))

# User search endpoint


@app.post("/api/v1/users/search", response_model=UserSearchResponse)
async def search_users(
    request: UserSearchRequest
    # rate_limit: None = Depends(check_rate_limit)
):
    """Search TikTok users by keyword"""
    try:
        users = await trend_service.search_users_only(
            query=request.query,
            count=request.count
        )

        return UserSearchResponse(users=users)
    except Exception as e:
        logger.error(f"User search failed for '{request.query}': {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Creative Center hashtag discovery endpoint


@app.post("/api/v1/creative-center/hashtags", response_model=NicheHashtagResponse)
async def creative_center_hashtags(
    request: NicheHashtagRequest
    # rate_limit: None = Depends(check_rate_limit)
):
    """
    Discover popular Creative Center hashtags for a given niche and region via Perplexity agent.

    This endpoint uses Perplexity AI to browse TikTok Creative Center and find the most relevant
    and trending hashtags for the specified niche, country, and language.
    """
    try:
        logger.info(
            f"🔍 Creative Center hashtag discovery requested for niche: {request.niche}")

        # Check if Perplexity API key is configured
        if not getattr(settings, 'perplexity_api_key', None) or settings.perplexity_api_key.strip() in [
            "", "demo-perplexity-key", "your-perplexity-api-key-here"
        ]:
            raise HTTPException(
                status_code=503,
                detail="Perplexity API key is not configured. Creative Center discovery requires a valid Perplexity API key."
            )

        # Use advanced Creative Center service for step-by-step discovery
        discovery_results = await advanced_creative_center_service.discover_hashtags_with_navigation(
            niche=request.niche,
            country=request.country,
            language=request.language,
            limit=request.limit,
            auto_detect_geo=request.auto_detect_geo,
            profile_data=request.profile_data
        )

        # Convert hashtag data to CreativeCenterHashtag objects
        hashtags = []
        for hashtag_data in discovery_results.get('hashtags', []):
            try:
                hashtag = CreativeCenterHashtag(**hashtag_data)
                hashtags.append(hashtag)
            except Exception as e:
                logger.warning(
                    f"⚠️ Failed to create CreativeCenterHashtag from data: {e}")
                continue

        logger.info(
            f"✅ Advanced Creative Center discovery completed: found {len(hashtags)} hashtags for niche '{request.niche}'")

        return NicheHashtagResponse(
            niche=discovery_results.get('niche', request.niche),
            country=discovery_results.get('country', request.country),
            language=discovery_results.get('language', request.language),
            category=discovery_results.get('category', 'Unknown'),
            total_found=discovery_results.get('total_found', 0),
            hashtags=hashtags
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"❌ Creative Center hashtag discovery failed for niche '{request.niche}': {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Creative Center discovery failed: {str(e)}"
        )

# Advanced Creative Center + Ensemble analysis endpoint


@app.post("/api/v1/analyze-creative-center", response_model=CreativeCenterAnalysisResponse)
async def analyze_creative_center_complete(
    request: CreativeCenterAnalysisRequest,
    current_user: Optional[UserProfile] = Depends(get_current_user)
):
    """
    Complete Creative Center + Ensemble Data analysis workflow.

    This endpoint implements the advanced architecture:
    1. Discovers hashtags from Creative Center via Perplexity agent
    2. Searches trending videos for each hashtag via Ensemble Data
    3. Applies intelligent filtering and relevance analysis
    4. Returns comprehensive results with metadata
    
    Free users get 1 analysis per day. Subscription required for unlimited access.
    """
    try:
        from utils import extract_tiktok_username

        # Check if user is authenticated
        if not current_user:
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "Authentication required",
                    "message": "Please log in to use trend analysis.",
                    "action": "login"
                }
            )

        # Track if this is a free trial usage
        is_free_trial_usage = False

        # Admins bypass all checks
        if current_user.is_admin:
            logger.info(
                f"🔑 Admin user {current_user.username} bypassing all checks")
        else:
            # Check if user can analyze (subscription or free trial)
            can_analyze, reason, details = await check_user_can_analyze(current_user.id)

            if not can_analyze:
                trial_info = details.get("trial_info", {})
                today_count = trial_info.get(
                    "today_count", 0) if trial_info else 0

                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "Analysis limit reached",
                        "message": details.get("message", "You've used your free daily analysis. Subscribe to get unlimited access!"),
                        "today_count": today_count,
                        "action": "subscribe",
                        "type": "free_trial_exhausted"
                    }
                )

            # Log what type of access user is using
            if reason == "free_trial":
                is_free_trial_usage = True
                logger.info(
                    f"🎁 User {current_user.username} using FREE TRIAL for Creative Center analysis")
            elif reason == "active_subscription":
                logger.info(
                    f"💳 User {current_user.username} using SUBSCRIPTION for Creative Center analysis")

        username = extract_tiktok_username(request.profile_url)
        logger.info(
            f"🚀 Starting complete Creative Center analysis for @{username}")
        logger.info(f"👤 User: {current_user.username} (ID: {current_user.id})")

        # CRITICAL: Record free trial usage IMMEDIATELY for free users
        if is_free_trial_usage:
            try:
                success = await record_free_trial_usage(current_user.id, username)
                if not success:
                    logger.error(
                        f"❌ record_free_trial_usage returned False for {current_user.username}")
                    raise HTTPException(
                        status_code=500,
                        detail="Failed to record free trial usage. Please try again."
                    )
                logger.info(
                    f"🎁 Free trial used by {current_user.username} for @{username} (Creative Center)")
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"❌ Failed to record free trial usage: {e}")
                logger.error(f"❌ Error type: {type(e).__name__}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to record free trial usage: {str(e)}"
                )

        # Check API keys
        if not getattr(settings, 'perplexity_api_key', None) or settings.perplexity_api_key.strip() in [
            "", "demo-perplexity-key", "your-perplexity-api-key-here"
        ]:
            raise HTTPException(
                status_code=503,
                detail="Perplexity API key is required for Creative Center analysis"
            )

        # Step 1: Get user profile for niche detection
        profile = await trend_service.get_profile_only(username)
        logger.info(
            f"📊 Profile loaded for @{username}: {profile.niche_category}")

        # Step 2: Discover Creative Center hashtags using advanced agent
        cc_discovery = await advanced_creative_center_service.discover_hashtags_with_navigation(
            niche=profile.niche_category or "General Content Creator",
            country=request.country,
            language=request.language,
            limit=request.hashtag_limit,
            auto_detect_geo=request.auto_detect_geo,
            profile_data=profile.model_dump() if request.auto_detect_geo else None
        )

        cc_hashtags_data = cc_discovery.get('hashtags', [])
        if not cc_hashtags_data:
            raise HTTPException(
                status_code=404,
                detail="No relevant Creative Center hashtags found for this profile's niche"
            )

        logger.info(
            f"🎯 Found {len(cc_hashtags_data)} Creative Center hashtags")

        # Step 3: Analyze hashtags with Ensemble Data
        ensemble_analysis = await trend_service.analyze_creative_center_hashtags(
            profile_url=request.profile_url,
            creative_center_hashtags=cc_hashtags_data,
            videos_per_hashtag=request.videos_per_hashtag
        )

        # Step 4: Convert Creative Center data to model objects
        cc_hashtags = []
        for hashtag_data in cc_hashtags_data:
            try:
                cc_hashtag = CreativeCenterHashtag(**hashtag_data)
                cc_hashtags.append(cc_hashtag)
            except Exception as e:
                logger.warning(
                    f"⚠️ Failed to convert Creative Center hashtag: {e}")
                continue

        # Step 5: Prepare comprehensive response
        metadata = {
            "creative_center_category": cc_discovery.get('category', 'Unknown'),
            "total_cc_hashtags_analyzed": cc_discovery.get('total_found', 0),
            "navigation_successful": cc_discovery.get('navigation_success', True),
            "region_used": cc_discovery.get('country', request.country),
            "total_videos_found": len(ensemble_analysis.get('trends', [])),
            "analysis_method": "Creative Center + Ensemble Data integration"
        }

        logger.info(
            f"✅ Complete Creative Center analysis finished: {len(ensemble_analysis.get('trends', []))} trending videos")

        return CreativeCenterAnalysisResponse(
            profile=ensemble_analysis.get('profile', profile),
            creative_center_hashtags=cc_hashtags,
            trends=ensemble_analysis.get('trends', []),
            analysis_summary=ensemble_analysis.get('analysis_summary', ''),
            metadata=metadata
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Complete Creative Center analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Creative Center analysis failed: {str(e)}"
        )

# Cache management endpoints


@app.get("/api/v1/cache/stats")
async def get_cache_stats(  # rate_limit: None = Depends(check_rate_limit)
):
    """Get cache statistics"""
    try:
        stats = await cache_service.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Cache stats failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/cache/clear")
async def clear_cache(
    pattern: str = "*"
    # rate_limit: None = Depends(check_rate_limit)
):
    """Clear cache by pattern"""
    try:
        cleared = await cache_service.clear_pattern(pattern)
        return {"message": f"Cleared {cleared} cache entries", "pattern": pattern}
    except Exception as e:
        logger.error(f"Cache clear failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint for Railway and monitoring"""
    try:
        # Test basic services
        cache_status = "healthy"
        try:
            await cache_service.get_stats()
        except:
            cache_status = "degraded"

        return HealthCheckResponse(
            status="healthy",
            timestamp=get_current_timestamp(),
            services={
                "cache": cache_status,
                "api": "healthy"
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthCheckResponse(
            status="unhealthy",
            timestamp=get_current_timestamp(),
            services={"error": str(e)}
        )

# Authentication helper functions


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[UserProfile]:
    """Get current authenticated user from Supabase JWT token"""
    if not credentials:
        return None

    try:
        # Get user from Supabase Auth token
        user_data = await get_current_user_from_token(credentials.credentials)
        return user_to_profile(user_data)
    except Exception as e:
        logger.error(f"Failed to get user from token: {e}")
        return None


async def require_auth(
    current_user: Optional[UserProfile] = Depends(get_current_user)
) -> UserProfile:
    """Require authentication - raises 401 if not authenticated"""
    if not current_user:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated. Please log in."
        )
    return current_user


async def require_subscription(
    current_user: UserProfile = Depends(require_auth)
) -> UserProfile:
    """Require active subscription - raises 403 if no active subscription (admins bypass)"""
    # Admins bypass subscription requirement
    if current_user.is_admin:
        logger.info(
            f"🔑 Admin user {current_user.username} bypassing subscription requirement")
        return current_user

    has_active = await check_active_subscription(current_user.id)

    if not has_active:
        subscription_info = await get_user_subscription_info(current_user.id)
        status = subscription_info.get(
            "stripe_subscription_status") if subscription_info else None

        raise HTTPException(
            status_code=403,
            detail={
                "error": "Active subscription required",
                "message": "You need an active subscription to use this feature. Please subscribe to continue.",
                "subscription_status": status,
                "action": "subscribe"
            }
        )

    return current_user


# Authentication endpoints

@app.post("/api/v1/auth/register", response_model=Token)
async def register(user_data: UserCreate):
    """Register a new user using Supabase Auth and create Stripe customer"""
    try:
        # Register user with Supabase
        result = await register_user(user_data)
        logger.info(f"✅ User registered: {user_data.username}")

        # Convert user data to profile
        try:
            user_profile = user_to_profile(result["user"])
        except Exception as profile_error:
            logger.error(f"❌ Failed to create user profile: {profile_error}")
            raise ValueError(f"Failed to create user profile: {profile_error}")

        # Create Stripe customer for the new user (if Stripe is configured)
        try:
            if settings.stripe_api_key and settings.stripe_api_key.strip():
                stripe_customer = await create_stripe_customer(
                    email=user_data.email,
                    username=user_data.username,
                    user_id=user_profile.id
                )

                # Save Stripe customer ID to user profile
                await update_user_stripe_customer(
                    user_id=user_profile.id,
                    stripe_customer_id=stripe_customer["customer_id"]
                )

                logger.info(
                    f"✅ Stripe customer created for user {user_data.username}")
            else:
                logger.warning(
                    "⚠️ Stripe not configured, skipping customer creation")
        except Exception as stripe_error:
            # Don't fail registration if Stripe setup fails
            logger.error(
                f"⚠️ Stripe customer creation failed (non-fatal): {stripe_error}")

        return Token(
            access_token=result["access_token"],
            token_type=result.get("token_type", "bearer"),
            user=user_profile
        )

    except ValueError as e:
        error_str = str(e).lower()
        logger.error(f"❌ Registration ValueError: {e}")

        # Return structured error based on error type
        if "already" in error_str or "exists" in error_str:
            raise UserAlreadyExistsError(user_data.email)
        elif "email" in error_str and "invalid" in error_str:
            raise HTTPException(status_code=400, detail=str(e))
        elif "password" in error_str:
            raise HTTPException(status_code=400, detail=str(e))
        else:
            raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Registration unexpected error: {e}", exc_info=True)
        # Try to parse Supabase error
        try:
            raise parse_supabase_error(e, context="register")
        except:
            raise HTTPException(
                status_code=500, detail=f"Registration failed: {str(e)}")


@app.post("/api/v1/auth/login", response_model=Token)
async def login(credentials: UserLogin):
    """Login with email and password using Supabase Auth"""
    try:
        # Login with Supabase
        result = await login_user(credentials)
        logger.info(f"✅ User logged in: {credentials.email}")

        # Convert user data to profile
        try:
            user_profile = user_to_profile(result["user"])
            logger.debug(f"User profile created: {user_profile.email}")
        except Exception as profile_error:
            logger.error(f"❌ Failed to create user profile: {profile_error}")
            raise ValueError(f"Failed to create user profile: {profile_error}")

        token_response = Token(
            access_token=result["access_token"],
            token_type=result.get("token_type", "bearer"),
            user=user_profile
        )

        logger.debug(
            f"Token response created successfully for {credentials.email}")
        return token_response

    except ValueError as e:
        error_str = str(e).lower()
        logger.error(f"❌ Login ValueError: {e}")

        # Return structured error based on error type
        if "not found" in error_str or "does not exist" in error_str:
            raise UserNotFoundError(credentials.email)
        elif "invalid" in error_str and ("password" in error_str or "credentials" in error_str):
            raise InvalidCredentialsError()
        else:
            raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Login unexpected error: {e}", exc_info=True)
        # Try to parse Supabase error
        try:
            raise parse_supabase_error(e, context="login")
        except:
            raise HTTPException(
                status_code=500, detail=f"Login failed: {str(e)}")


@app.get("/api/v1/auth/me", response_model=UserProfile)
async def get_me(current_user: UserProfile = Depends(require_auth)):
    """Get current user profile"""
    return current_user


@app.put("/api/v1/auth/profile", response_model=UserProfile)
async def update_profile(
    profile_data: UserProfileUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: UserProfile = Depends(require_auth)
):
    """Update current user profile using Supabase"""
    try:
        # Update profile in Supabase
        updated_user = await update_profile_service(credentials.credentials, profile_data)

        logger.info(f"✅ Profile updated: {current_user.username}")

        return user_to_profile(updated_user)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Profile update failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Token usage endpoints


@app.get("/api/v1/usage/summary")
async def get_token_usage_summary(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get aggregated token usage summary for the current user

    Returns:
    - Total analyses count
    - Total tokens used for each service
    - Total estimated cost
    - First and last analysis timestamps
    """
    try:
        # Get current user from token
        user_profile = await get_current_user_from_token(credentials.credentials)

        # Get token usage summary
        summary = await get_user_token_summary(user_profile["id"])

        logger.info(
            f"📊 Token usage summary requested by user {user_profile['id']}")

        return {
            "success": True,
            "data": summary
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get token usage summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/usage/history")
async def get_token_usage_history(
    limit: int = 50,
    offset: int = 0,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get detailed token usage history for the current user

    Query params:
    - limit: Number of records to return (default: 50, max: 100)
    - offset: Offset for pagination (default: 0)

    Returns:
    - List of token usage records with timestamps
    """
    try:
        # Get current user from token
        user_profile = await get_current_user_from_token(credentials.credentials)

        # Limit max results
        limit = min(limit, 100)

        # Get token usage history
        history = await get_user_token_usage(user_profile["id"], limit, offset)

        logger.info(
            f"📜 Token usage history requested by user {user_profile['id']} (limit={limit}, offset={offset})")

        return {
            "success": True,
            "data": {
                "records": history,
                "count": len(history),
                "limit": limit,
                "offset": offset
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get token usage history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/usage/period")
async def get_token_usage_by_period(
    period_days: int = 30,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get token usage summary for a specific time period

    Query params:
    - period_days: Number of days to include (default: 30)

    Returns:
    - Analyses count in period
    - Total tokens used for each service in period
    - Total estimated cost in period
    """
    try:
        # Get current user from token
        user_profile = await get_current_user_from_token(credentials.credentials)

        # Validate period
        if period_days < 1 or period_days > 365:
            raise HTTPException(
                status_code=400, detail="period_days must be between 1 and 365")

        # Get token usage for period
        usage = await get_user_token_usage_by_period(user_profile["id"], period_days)

        logger.info(
            f"📅 Token usage by period requested by user {user_profile['id']} (period={period_days} days)")

        return {
            "success": True,
            "data": usage
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get token usage by period: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Free Trial endpoints

@app.get("/api/v1/free-trial/info")
async def get_free_trial_status(
    current_user: UserProfile = Depends(require_auth)
):
    """
    Get user's free trial information

    Returns information about daily free analysis usage:
    - Whether user can use free trial today
    - How many analyses used today
    - Total free analyses used
    """
    try:
        # Admins don't use free trial
        if current_user.is_admin:
            return {
                "is_admin": True,
                "has_subscription": True,
                "can_use_free_trial": False,
                "message": "Admin users have unlimited access"
            }

        # Check if user has subscription
        has_subscription = await check_active_subscription(current_user.id)

        if has_subscription:
            return {
                "is_admin": False,
                "has_subscription": True,
                "can_use_free_trial": False,
                "message": "You have an active subscription with unlimited access"
            }

        # Get free trial info
        trial_info = await get_free_trial_info(current_user.id)

        if not trial_info:
            return {
                "is_admin": False,
                "has_subscription": False,
                "can_use_free_trial": True,
                "today_count": 0,
                "total_free_analyses": 0,
                "daily_limit": 1,
                "message": "You have 1 free analysis available today"
            }

        can_use = trial_info.get("can_use_today", False)
        today_count = trial_info.get("today_count", 0)
        total_count = trial_info.get("total_free_analyses", 0)

        return {
            "is_admin": False,
            "has_subscription": False,
            "can_use_free_trial": can_use,
            "today_count": today_count,
            "total_free_analyses": total_count,
            "daily_limit": 1,
            "last_used": trial_info.get("last_used"),
            "message": f"You have used {today_count}/1 free analyses today" if not can_use else "You have 1 free analysis available today"
        }

    except Exception as e:
        logger.error(f"❌ Failed to get free trial info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Stripe subscription endpoints


@app.get("/api/v1/subscription/info")
async def get_subscription_info(
    current_user: UserProfile = Depends(require_auth)
):
    """Get current user's subscription information"""
    try:
        # Get subscription info from database
        db_subscription = await get_user_subscription_info(current_user.id)

        if not db_subscription or not db_subscription.get("stripe_subscription_id"):
            return {
                "has_subscription": False,
                "subscription": None
            }

        # Get latest subscription details from Stripe
        subscription = await get_subscription(db_subscription["stripe_subscription_id"])

        return {
            "has_subscription": True,
            "subscription": subscription
        }

    except Exception as e:
        logger.error(f"❌ Failed to get subscription info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/subscription/checkout")
async def create_subscription_checkout(
    success_url: str,
    cancel_url: str,
    current_user: UserProfile = Depends(require_auth)
):
    """Create a Stripe Checkout session for subscription"""
    try:
        # Get user's Stripe customer ID
        db_subscription = await get_user_subscription_info(current_user.id)

        if not db_subscription or not db_subscription.get("stripe_customer_id"):
            raise HTTPException(
                status_code=400,
                detail="Stripe customer not found. Please contact support."
            )

        # Create checkout session
        session = await create_checkout_session(
            customer_id=db_subscription["stripe_customer_id"],
            success_url=success_url,
            cancel_url=cancel_url
        )

        return {
            "checkout_url": session["url"],
            "session_id": session["session_id"]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to create checkout session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/subscription/create-payment-link")
async def create_payment_link_public(
    user_email: Optional[str] = None,
    success_url: Optional[str] = None,
    cancel_url: Optional[str] = None
):
    """
    Create a public payment link for subscription
    Anyone can use this to subscribe - no authentication required
    """
    try:
        # Use default URLs if not provided
        if not success_url:
            success_url = f"{settings.cors_origins[0]}/subscription/success?session_id={{CHECKOUT_SESSION_ID}}"
        if not cancel_url:
            cancel_url = f"{settings.cors_origins[0]}/"

        # Create public payment link
        payment_link = await create_public_payment_link(
            user_email=user_email or "",
            success_url=success_url,
            cancel_url=cancel_url
        )

        return {
            "success": True,
            "payment_url": payment_link["url"],
            "session_id": payment_link["session_id"],
            "expires_at": payment_link["expires_at"]
        }

    except Exception as e:
        logger.error(f"❌ Failed to create public payment link: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/subscription/check")
async def check_subscription_status(
    current_user: UserProfile = Depends(require_auth)
):
    """Check if current user has an active subscription"""
    try:
        has_active = await check_active_subscription(current_user.id)

        subscription_info = await get_user_subscription_info(current_user.id)

        return {
            "has_active_subscription": has_active,
            "subscription_status": subscription_info.get("stripe_subscription_status") if subscription_info else None,
            "subscription_end_date": subscription_info.get("subscription_end_date") if subscription_info else None
        }

    except Exception as e:
        logger.error(f"❌ Failed to check subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/subscription/cancel")
async def cancel_user_subscription(
    immediate: bool = False,
    current_user: UserProfile = Depends(require_auth)
):
    """Cancel user's subscription"""
    try:
        # Get user's subscription ID
        db_subscription = await get_user_subscription_info(current_user.id)

        if not db_subscription or not db_subscription.get("stripe_subscription_id"):
            raise HTTPException(
                status_code=404,
                detail="No active subscription found"
            )

        # Cancel subscription in Stripe
        result = await cancel_subscription(
            subscription_id=db_subscription["stripe_subscription_id"],
            immediate=immediate
        )

        # Update database
        await update_user_subscription(
            user_id=current_user.id,
            subscription_id=result["subscription_id"],
            status=result["status"]
        )

        return {
            "success": True,
            "message": "Subscription canceled successfully" if immediate else "Subscription will cancel at period end",
            "subscription": result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to cancel subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/subscription/reactivate")
async def reactivate_user_subscription(
    current_user: UserProfile = Depends(require_auth)
):
    """Reactivate a subscription that was set to cancel"""
    try:
        # Get user's subscription ID
        db_subscription = await get_user_subscription_info(current_user.id)

        if not db_subscription or not db_subscription.get("stripe_subscription_id"):
            raise HTTPException(
                status_code=404,
                detail="No subscription found"
            )

        # Reactivate subscription in Stripe
        result = await reactivate_subscription(
            subscription_id=db_subscription["stripe_subscription_id"]
        )

        # Update database
        await update_user_subscription(
            user_id=current_user.id,
            subscription_id=result["subscription_id"],
            status=result["status"]
        )

        return {
            "success": True,
            "message": "Subscription reactivated successfully",
            "subscription": result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to reactivate subscription: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Stripe webhook endpoint for handling subscription events
@app.post("/api/v1/webhook/stripe")
async def stripe_webhook(request: dict):
    """Handle Stripe webhook events"""
    try:
        # TODO: Verify webhook signature in production
        # from stripe import StripeClient
        # client = StripeClient(settings.stripe_api_key)
        # event = client.construct_event(payload, sig_header, settings.stripe_webhook_secret)

        event_type = request.get("type")
        data = request.get("data", {}).get("object", {})

        logger.info(f"📨 Received Stripe webhook: {event_type}")

        # Handle different event types
        if event_type == "customer.subscription.created":
            # New subscription created
            subscription_id = data.get("id")
            customer_id = data.get("customer")
            status = data.get("status")
            current_period_start = data.get("current_period_start")
            current_period_end = data.get("current_period_end")

            # Find user by Stripe customer ID
            user = await get_user_by_stripe_customer_id(customer_id)
            if user:
                from datetime import datetime
                await update_user_subscription(
                    user_id=user["id"],
                    subscription_id=subscription_id,
                    status=status,
                    start_date=datetime.fromtimestamp(
                        current_period_start).isoformat() if current_period_start else None,
                    end_date=datetime.fromtimestamp(
                        current_period_end).isoformat() if current_period_end else None
                )
                logger.info(
                    f"✅ Subscription created and saved: {subscription_id} for user {user['id']}")
            else:
                logger.warning(
                    f"⚠️ User not found for Stripe customer: {customer_id}")

        elif event_type == "customer.subscription.updated":
            # Subscription updated (status change, renewal, etc.)
            subscription_id = data.get("id")
            customer_id = data.get("customer")
            status = data.get("status")
            current_period_start = data.get("current_period_start")
            current_period_end = data.get("current_period_end")

            # Find user by Stripe customer ID
            user = await get_user_by_stripe_customer_id(customer_id)
            if user:
                from datetime import datetime
                await update_user_subscription(
                    user_id=user["id"],
                    subscription_id=subscription_id,
                    status=status,
                    start_date=datetime.fromtimestamp(
                        current_period_start).isoformat() if current_period_start else None,
                    end_date=datetime.fromtimestamp(
                        current_period_end).isoformat() if current_period_end else None
                )
                logger.info(
                    f"✅ Subscription updated: {subscription_id} - {status} for user {user['id']}")
            else:
                logger.warning(
                    f"⚠️ User not found for Stripe customer: {customer_id}")

        elif event_type == "customer.subscription.deleted":
            # Subscription canceled/ended
            subscription_id = data.get("id")
            customer_id = data.get("customer")

            # Find user by Stripe customer ID
            user = await get_user_by_stripe_customer_id(customer_id)
            if user:
                await update_user_subscription(
                    user_id=user["id"],
                    subscription_id=subscription_id,
                    status="canceled"
                )
                logger.info(
                    f"✅ Subscription canceled: {subscription_id} for user {user['id']}")
            else:
                logger.warning(
                    f"⚠️ User not found for Stripe customer: {customer_id}")

        elif event_type == "checkout.session.completed":
            # Checkout completed - link customer to user if needed
            session = data
            customer_id = session.get("customer")
            customer_email = session.get("customer_details", {}).get("email")
            subscription_id = session.get("subscription")

            logger.info(
                f"✅ Checkout completed: session={session.get('id')}, customer={customer_id}, email={customer_email}")

            # Try to find user by email and link Stripe customer
            if customer_email and customer_id:
                client = get_supabase()
                # Find user by email in auth.users
                try:
                    # Search in profiles table
                    response = client.table("profiles").select(
                        "*").eq("email", customer_email).execute()
                    if response.data:
                        user = response.data[0]
                        # Update Stripe customer ID if not set
                        if not user.get("stripe_customer_id"):
                            await update_user_stripe_customer(user["id"], customer_id)
                            logger.info(
                                f"✅ Linked Stripe customer {customer_id} to user {user['id']}")
                except Exception as e:
                    logger.error(f"❌ Failed to link customer: {e}")

        return {"received": True}

    except Exception as e:
        logger.error(f"❌ Webhook processing failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# Root endpoint


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "TrendXL 2.0 Backend API",
        "version": "2.0.0",
        "description": "TikTok Trend Analysis API",
        "endpoints": {
            "health": "/health",
            "auth_register": "/api/v1/auth/register",
            "auth_login": "/api/v1/auth/login",
            "auth_me": "/api/v1/auth/me",
            "auth_profile": "/api/v1/auth/profile",
            "subscription_info": "/api/v1/subscription/info",
            "subscription_checkout": "/api/v1/subscription/checkout",
            "subscription_cancel": "/api/v1/subscription/cancel",
            "subscription_reactivate": "/api/v1/subscription/reactivate",
            "analyze": "/api/v1/analyze",
            "profile": "/api/v1/profile",
            "posts": "/api/v1/posts",
            "hashtag_search": "/api/v1/hashtag/search",
            "user_search": "/api/v1/users/search",
            "creative_center_hashtags": "/api/v1/creative-center/hashtags",
            "analyze_creative_center": "/api/v1/analyze-creative-center"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if settings.debug else "warning"
    )
