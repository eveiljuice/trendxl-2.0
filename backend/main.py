"""
TrendXL 2.0 Backend - FastAPI Application
"""
import logging
import asyncio
from contextlib import asynccontextmanager
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
    ErrorResponse,
    HealthCheckResponse
)
from services.trend_analysis_service import trend_service
from services.cache_service import cache_service
from utils import RateLimiter, get_current_timestamp

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Rate limiter
rate_limiter = RateLimiter(settings.max_requests_per_minute)


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

    logger.info(
        f"🔑 Ensemble API: {'✅ Configured' if ensemble_token else '❌ Missing'}")
    logger.info(
        f"🔑 OpenAI API: {'✅ Configured' if openai_key else '❌ Missing'}")

    if not ensemble_token or not openai_key:
        logger.warning(
            "⚠️  Some API keys missing - service will use fallback/demo mode")
    else:
        logger.info("✅ All services configured properly")

    yield

    # Shutdown
    logger.info("🛑 TrendXL 2.0 Backend shutting down...")

# Create FastAPI app
app = FastAPI(
    title="TrendXL 2.0 Backend API",
    description="TikTok Trend Analysis API using Ensemble Data and OpenAI",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
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
            "openai_api": True     # Will be tested in actual requests
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
            "openai_api": bool(getattr(settings, 'openai_api_key', None))
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
    request: TrendAnalysisRequest
):
    """
    Analyze TikTok profile trends

    This endpoint performs a complete trend analysis:
    1. Fetches user profile and posts
    2. Analyzes posts with AI to extract relevant hashtags  
    3. Searches trending videos for each hashtag
    4. Returns comprehensive analysis results
    """
    try:
        logger.info(f"🎯 Trend analysis requested for: {request.profile_url}")

        # Try to get cached result first
        from utils import extract_tiktok_username
        username = extract_tiktok_username(request.profile_url)
        cached_result = await trend_service.get_cached_analysis(username)

        if cached_result:
            logger.info(f"📋 Returning cached analysis for @{username}")
            return cached_result

        # Perform new analysis
        result = await trend_service.analyze_profile_trends(
            profile_input=request.profile_url,
            max_hashtags=5,
            videos_per_hashtag=2
        )

        logger.info(f"✅ Analysis completed for @{username}")
        return result

    except Exception as e:
        logger.error(f"Analysis failed: {e}")

        # Return appropriate error message
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        elif "rate limit" in str(e).lower():
            raise HTTPException(status_code=429, detail=str(e))
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
            "analyze": "/api/v1/analyze",
            "profile": "/api/v1/profile",
            "posts": "/api/v1/posts",
            "hashtag_search": "/api/v1/hashtag/search",
            "user_search": "/api/v1/users/search"
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
