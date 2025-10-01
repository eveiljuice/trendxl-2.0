"""
Configuration settings for TrendXL 2.0 Backend
"""
import os
import logging
from typing import List, Optional
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from pydantic import Field, ConfigDict, field_validator

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings"""

    # API Keys - Made optional for Railway deployment to allow health checks
    # Set default to empty string to prevent startup failure
    ensemble_api_token: str = Field(default="", env="ENSEMBLE_API_TOKEN")
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    perplexity_api_key: str = Field(default="", env="PERPLEXITY_API_KEY")

    # Optional API tokens for other services
    seatable_api_token: Optional[str] = Field(None, env="SEATABLE_API_TOKEN")

    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    # Disable debug in production
    debug: bool = Field(default=False, env="DEBUG")

    # Redis Configuration (Railway Redis addon URL format)
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    redis_private_url: Optional[str] = Field(
        None, env="REDIS_PRIVATE_URL")  # Railway private URL

    # CORS Settings
    cors_origins: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:5173",
            # Railway frontend service
            "https://trendxl-20-frontend-production.up.railway.app",
            # Allow all Railway domains for flexibility
            "*"  # Remove in production for better security
        ],
        env="CORS_ORIGINS"
    )
    # Regex для Railway доменов и localhost
    cors_origin_regex: Optional[str] = Field(
        default=r"https?://.*\.up\.railway\.app$|https?://.*\.railway\.app$|http://localhost:\d+$",
        env="CORS_ORIGIN_REGEX")

    # Rate Limiting
    max_requests_per_minute: int = Field(
        default=60, env="MAX_REQUESTS_PER_MINUTE")

    # Caching Settings (in seconds)
    cache_profile_ttl: int = Field(
        default=1800, env="CACHE_PROFILE_TTL")  # 30 min
    cache_posts_ttl: int = Field(
        default=900, env="CACHE_POSTS_TTL")      # 15 min
    cache_trends_ttl: int = Field(
        default=300, env="CACHE_TRENDS_TTL")    # 5 min

    # TikTok API Settings (according to official Ensemble Data documentation)
    max_posts_per_user: int = 50  # Increased for deeper analysis - more content context
    max_videos_per_hashtag: int = 10  # Hashtag search results per query
    max_hashtags_to_analyze: int = 5  # GPT analysis hashtag limit

    # Ensemble Data API Settings (based on official SDK documentation)
    # Max depth for user posts (each depth ≈ 10 posts)
    ensemble_max_depth: int = 5
    ensemble_max_cursor: int = 2000  # Max cursor for full_hashtag_search
    ensemble_retry_attempts: int = 3  # Retry attempts for API calls
    # Delay between requests (seconds) - increased for rate limiting
    ensemble_request_delay: float = 3.0

    # OpenAI Settings
    openai_model: str = "gpt-4o"
    openai_temperature: float = 0.3
    openai_max_tokens: int = 500

    # OpenAI Vision Settings for content relevance analysis
    # Updated from deprecated gpt-4-vision-preview (shutdown 2024-12-06)
    openai_vision_model: str = "gpt-4o"
    openai_vision_temperature: float = 0.2
    openai_vision_max_tokens: int = 300
    max_images_for_analysis: int = 20  # Increased for better relevance analysis

    # Perplexity Settings
    perplexity_model: str = "sonar"  # Updated to working model name
    perplexity_temperature: float = 0.2
    perplexity_max_tokens: int = 300

    model_config = ConfigDict(
        env_file=".env",  # Only backend .env file
        case_sensitive=False,
        env_file_encoding='utf-8',
        extra='ignore'  # Ignore extra fields from environment
    )

    @field_validator('ensemble_api_token')
    @classmethod
    def validate_ensemble_token(cls, v):
        """Validate Ensemble Data API token according to official SDK requirements"""
        # Allow empty for Railway health checks
        if not v or len(v.strip()) == 0:
            logger.warning(
                "⚠️ ENSEMBLE_API_TOKEN is missing. "
                "Set it in Railway environment variables: https://dashboard.ensembledata.com/"
            )
            return ""

        if len(v.strip()) < 10:
            logger.warning(
                "⚠️ ENSEMBLE_API_TOKEN appears too short. "
                "Get your API key from: https://dashboard.ensembledata.com/"
            )
            return v.strip()

        if v.strip() == "your-ensemble-api-token-here":
            logger.warning(
                "⚠️ ENSEMBLE_API_TOKEN is using placeholder value. "
                "Replace it with your real API token from: https://dashboard.ensembledata.com/"
            )
            return ""

        # Test token format (basic validation)
        token = v.strip()
        if not token.replace('-', '').replace('_', '').isalnum():
            logger.warning(
                "⚠️ Ensemble token format may be invalid (contains special characters)")

        logger.info("✅ Ensemble Data API token validated for official SDK")
        return token

    @field_validator('openai_api_key')
    @classmethod
    def validate_openai_key(cls, v):
        """Validate OpenAI API key"""
        # Allow empty for Railway health checks
        if not v or len(v.strip()) == 0:
            logger.warning(
                "⚠️ OPENAI_API_KEY is missing. "
                "Set it in Railway environment variables: https://platform.openai.com/api-keys"
            )
            return ""

        if len(v.strip()) < 20:
            logger.warning(
                "⚠️ OPENAI_API_KEY appears too short. "
                "Get your API key from: https://platform.openai.com/api-keys"
            )
            return v.strip()

        if v.strip() == "your-openai-api-key-here":
            logger.warning(
                "⚠️ OPENAI_API_KEY is using placeholder value. "
                "Replace it with your real API key from: https://platform.openai.com/api-keys"
            )
            return ""

        if not v.strip().startswith(('sk-', 'sk-proj-')):
            logger.warning(
                "⚠️ OPENAI_API_KEY format may be invalid. "
                "OpenAI API keys should start with 'sk-' or 'sk-proj-'"
            )
            return v.strip()

        logger.info("✅ OpenAI API key validated")
        return v.strip()

    @field_validator('perplexity_api_key')
    @classmethod
    def validate_perplexity_key(cls, v):
        """Validate Perplexity API key - now optional for startup"""
        if not v or v.strip() in ["demo-perplexity-key", "your-perplexity-api-key-here", ""]:
            logger.warning(
                "⚠️ PERPLEXITY_API_KEY is missing or using demo value. "
                "Get your API key from: https://www.perplexity.ai/settings/api "
                "Perplexity search features will not work without a valid key."
            )
            return v  # Allow demo key for startup

        token = v.strip()
        if len(token) < 20:
            logger.warning("⚠️ Perplexity key appears too short")
        elif not token.startswith('pplx-'):
            logger.warning(
                "⚠️ Perplexity API key format may be invalid (should start with 'pplx-')")
        else:
            logger.info("✅ Perplexity API key validated")

        return token


# Global settings instance
settings = Settings()
