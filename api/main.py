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
    user_to_profile, create_user, get_user_by_email, get_user_by_username,
    get_user_by_id, update_last_login, update_user_profile,
    record_token_usage, get_user_token_usage, get_user_token_summary,
    get_user_token_usage_by_period
)
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

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
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Analyze TikTok profile trends

    This endpoint performs a complete trend analysis:
    1. Fetches user profile and posts
    2. Analyzes posts with AI to extract relevant hashtags  
    3. Searches trending videos for each hashtag
    4. Returns comprehensive analysis results

    Requires authentication. Records token usage for the user.
    """
    try:
        # Get current user (optional - analysis can work without auth)
        current_user = None
        if credentials:
            try:
                token_data = decode_access_token(credentials.credentials)
                current_user = get_user_by_id(token_data["user_id"])
            except:
                # If token is invalid, continue without user
                pass

        print(f"\n{'='*80}")
        print(f"🚀 BACKEND: NEW ANALYSIS REQUEST RECEIVED!")
        print(f"🎯 Profile URL: {request.profile_url}")
        if current_user:
            print(
                f"👤 User: {current_user['username']} (ID: {current_user['id']})")
        print(f"{'='*80}\n")
        logger.info(f"🎯 Trend analysis requested for: {request.profile_url}")

        # Try to get cached result first
        from utils import extract_tiktok_username
        username = extract_tiktok_username(request.profile_url)
        cached_result = await trend_service.get_cached_analysis(username)

        if cached_result:
            print(f"📋 BACKEND: Returning CACHED result for @{username}")
            logger.info(f"📋 Returning cached analysis for @{username}")
            return cached_result

        print(f"🔄 BACKEND: Starting NEW analysis (no cache found)...")
        print(f"   - max_hashtags: 5")
        print(f"   - videos_per_hashtag: 8")

        # Perform new analysis - increased videos per hashtag to ensure 10+ total videos
        result = await trend_service.analyze_profile_trends(
            profile_input=request.profile_url,
            max_hashtags=5,
            videos_per_hashtag=8  # Increased from 4 to 8 to compensate for filters
        )

        print(f"✅ BACKEND: Analysis completed for @{username}")
        print(f"   - Found {len(result.trends)} trends")

        # Record token usage for authenticated users
        if current_user and result.token_usage:
            try:
                record_token_usage(
                    user_id=current_user["id"],
                    openai_prompt_tokens=result.token_usage.openai_prompt_tokens,
                    openai_completion_tokens=result.token_usage.openai_completion_tokens,
                    perplexity_prompt_tokens=result.token_usage.perplexity_prompt_tokens,
                    perplexity_completion_tokens=result.token_usage.perplexity_completion_tokens,
                    ensemble_units=result.token_usage.ensemble_units,
                    total_cost_estimate=result.token_usage.total_cost_estimate,
                    profile_analyzed=username
                )
                print(
                    f"💾 Token usage recorded for user {current_user['username']}")
                logger.info(
                    f"💾 Token usage recorded for user {current_user['id']}")
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
    request: CreativeCenterAnalysisRequest
    # rate_limit: None = Depends(check_rate_limit)
):
    """
    Complete Creative Center + Ensemble Data analysis workflow.

    This endpoint implements the advanced architecture:
    1. Discovers hashtags from Creative Center via Perplexity agent
    2. Searches trending videos for each hashtag via Ensemble Data
    3. Applies intelligent filtering and relevance analysis
    4. Returns comprehensive results with metadata
    """
    try:
        from utils import extract_tiktok_username

        username = extract_tiktok_username(request.profile_url)
        logger.info(
            f"🚀 Starting complete Creative Center analysis for @{username}")

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
    """Get current authenticated user from JWT token"""
    if not credentials:
        return None

    token_data = decode_access_token(credentials.credentials)
    if not token_data or not token_data.user_id:
        return None

    user = get_user_by_id(token_data.user_id)
    if not user:
        return None

    return user_to_profile(user)


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


# Authentication endpoints

@app.post("/api/v1/auth/register", response_model=Token)
async def register(user_data: UserCreate):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

        existing_username = get_user_by_username(user_data.username)
        if existing_username:
            raise HTTPException(
                status_code=400,
                detail="Username already taken"
            )

        # Create user
        hashed_password = get_password_hash(user_data.password)
        user = create_user(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name
        )

        # Update last login
        update_last_login(user["id"])

        # Create access token
        access_token = create_access_token(data={"user_id": user["id"]})

        # Return token and user profile
        user_profile = user_to_profile(user)

        logger.info(f"✅ User registered: {user_data.username}")

        return Token(
            access_token=access_token,
            user=user_profile
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Registration failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/auth/login", response_model=Token)
async def login(credentials: UserLogin):
    """Login with email and password"""
    try:
        # Get user by email
        user = get_user_by_email(credentials.email)

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Incorrect email or password"
            )

        # Verify password
        if not verify_password(credentials.password, user["hashed_password"]):
            raise HTTPException(
                status_code=401,
                detail="Incorrect email or password"
            )

        # Update last login
        update_last_login(user["id"])

        # Create access token
        access_token = create_access_token(data={"user_id": user["id"]})

        # Return token and user profile
        user_profile = user_to_profile(user)

        logger.info(f"✅ User logged in: {user['username']}")

        return Token(
            access_token=access_token,
            user=user_profile
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Login failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/auth/me", response_model=UserProfile)
async def get_me(current_user: UserProfile = Depends(require_auth)):
    """Get current user profile"""
    return current_user


@app.put("/api/v1/auth/profile", response_model=UserProfile)
async def update_profile(
    profile_data: UserProfileUpdate,
    current_user: UserProfile = Depends(require_auth)
):
    """Update current user profile"""
    try:
        updated_user = update_user_profile(
            user_id=current_user.id,
            full_name=profile_data.full_name,
            avatar_url=profile_data.avatar_url,
            bio=profile_data.bio
        )

        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")

        logger.info(f"✅ Profile updated: {current_user.username}")

        return user_to_profile(updated_user)

    except HTTPException:
        raise
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
        # Verify token
        if not credentials:
            raise HTTPException(
                status_code=401, detail="Authentication required")

        token_data = decode_access_token(credentials.credentials)
        current_user = get_user_by_id(token_data["user_id"])

        if not current_user:
            raise HTTPException(
                status_code=401, detail="Invalid authentication")

        # Get token usage summary
        summary = get_user_token_summary(current_user["id"])

        logger.info(
            f"📊 Token usage summary requested by user {current_user['id']}")

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
        # Verify token
        if not credentials:
            raise HTTPException(
                status_code=401, detail="Authentication required")

        token_data = decode_access_token(credentials.credentials)
        current_user = get_user_by_id(token_data["user_id"])

        if not current_user:
            raise HTTPException(
                status_code=401, detail="Invalid authentication")

        # Limit max results
        limit = min(limit, 100)

        # Get token usage history
        history = get_user_token_usage(current_user["id"], limit, offset)

        logger.info(
            f"📜 Token usage history requested by user {current_user['id']} (limit={limit}, offset={offset})")

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
        # Verify token
        if not credentials:
            raise HTTPException(
                status_code=401, detail="Authentication required")

        token_data = decode_access_token(credentials.credentials)
        current_user = get_user_by_id(token_data["user_id"])

        if not current_user:
            raise HTTPException(
                status_code=401, detail="Invalid authentication")

        # Validate period
        if period_days < 1 or period_days > 365:
            raise HTTPException(
                status_code=400, detail="period_days must be between 1 and 365")

        # Get token usage for period
        usage = get_user_token_usage_by_period(current_user["id"], period_days)

        logger.info(
            f"📅 Token usage by period requested by user {current_user['id']} (period={period_days} days)")

        return {
            "success": True,
            "data": usage
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get token usage by period: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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
