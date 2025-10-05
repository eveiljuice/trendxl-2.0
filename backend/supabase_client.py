"""
Supabase client configuration and helpers
"""
import os
import logging
from typing import Optional
from supabase import create_client, Client
from postgrest.exceptions import APIError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
# Use service role key for backend operations (bypasses RLS)
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
SUPABASE_KEY = SUPABASE_SERVICE_KEY if SUPABASE_SERVICE_KEY else os.getenv(
    "SUPABASE_ANON_KEY", "")

# Initialize Supabase client
supabase: Optional[Client] = None


def init_supabase() -> Client:
    """Initialize Supabase client"""
    global supabase

    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error(
            "❌ SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY/SUPABASE_ANON_KEY not set in environment variables")
        raise ValueError(
            "Supabase configuration missing. Please set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY (or SUPABASE_ANON_KEY)")

    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("✅ Supabase client initialized successfully")
        return supabase
    except Exception as e:
        logger.error(f"❌ Failed to initialize Supabase client: {e}")
        raise


def get_supabase() -> Client:
    """Get Supabase client instance"""
    global supabase
    if supabase is None:
        supabase = init_supabase()
    return supabase

# Database helper functions


async def insert_user(link: str, parsed_niche: Optional[str] = None,
                      location: Optional[str] = None, followers: int = 0,
                      engagement_rate: float = 0.0, top_posts: list = None) -> dict:
    """Insert a new user into the database"""
    try:
        client = get_supabase()
        data = {
            "link": link,
            "parsed_niche": parsed_niche,
            "location": location,
            "followers": followers,
            "engagement_rate": engagement_rate,
            "top_posts": top_posts or []
        }

        response = client.table("users").insert(data).execute()
        logger.info(f"✅ User inserted: {link}")
        return response.data[0] if response.data else {}
    except APIError as e:
        logger.error(f"❌ Failed to insert user: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error inserting user: {e}")
        raise


async def get_user_by_link(link: str) -> Optional[dict]:
    """Get user by link"""
    try:
        client = get_supabase()
        response = client.table("users").select("*").eq("link", link).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"❌ Failed to get user by link: {e}")
        return None


async def insert_trend(user_id: str, trend_title: str, platform: str = "tiktok",
                       video_url: Optional[str] = None, stat_metrics: dict = None,
                       relevance_score: float = 0.0) -> dict:
    """Insert a new trend into the database"""
    try:
        client = get_supabase()
        data = {
            "user_id": user_id,
            "trend_title": trend_title,
            "platform": platform,
            "video_url": video_url,
            "stat_metrics": stat_metrics or {},
            "relevance_score": relevance_score
        }

        response = client.table("trend_feed").insert(data).execute()
        logger.info(f"✅ Trend inserted: {trend_title}")
        return response.data[0] if response.data else {}
    except Exception as e:
        logger.error(f"❌ Failed to insert trend: {e}")
        raise


async def get_trends_by_user(user_id: str, limit: int = 50) -> list:
    """Get trends for a specific user"""
    try:
        client = get_supabase()
        response = (client.table("trend_feed")
                    .select("*")
                    .eq("user_id", user_id)
                    .order("relevance_score", desc=True)
                    .order("created_at", desc=True)
                    .limit(limit)
                    .execute())
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"❌ Failed to get trends: {e}")
        return []


async def insert_interaction(user_id: str, trend_id: str, action_type: str) -> dict:
    """Log user interaction with a trend"""
    try:
        client = get_supabase()
        data = {
            "user_id": user_id,
            "trend_id": trend_id,
            "action_type": action_type
        }

        response = client.table("interaction_log").insert(data).execute()
        logger.info(f"✅ Interaction logged: {action_type}")
        return response.data[0] if response.data else {}
    except Exception as e:
        logger.error(f"❌ Failed to log interaction: {e}")
        raise


async def get_user_interactions(user_id: str, limit: int = 100) -> list:
    """Get user interaction history"""
    try:
        client = get_supabase()
        response = (client.table("interaction_log")
                    .select("*")
                    .eq("user_id", user_id)
                    .order("timestamp", desc=True)
                    .limit(limit)
                    .execute())
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"❌ Failed to get interactions: {e}")
        return []


async def insert_niche_adapter(domain: str, parsed_by_gpt_summary: Optional[str] = None,
                               topic_tags: list = None) -> dict:
    """Insert a new niche adapter"""
    try:
        client = get_supabase()
        data = {
            "domain": domain,
            "parsed_by_gpt_summary": parsed_by_gpt_summary,
            "topic_tags": topic_tags or []
        }

        response = client.table("niche_adapters").insert(data).execute()
        logger.info(f"✅ Niche adapter inserted: {domain}")
        return response.data[0] if response.data else {}
    except Exception as e:
        logger.error(f"❌ Failed to insert niche adapter: {e}")
        raise


async def get_niche_adapter_by_domain(domain: str) -> Optional[dict]:
    """Get niche adapter by domain"""
    try:
        client = get_supabase()
        response = client.table("niche_adapters").select(
            "*").eq("domain", domain).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"❌ Failed to get niche adapter: {e}")
        return None


async def record_token_usage(
    user_id: str,
    openai_prompt_tokens: int,
    openai_completion_tokens: int,
    perplexity_prompt_tokens: int,
    perplexity_completion_tokens: int,
    ensemble_units: int,
    total_cost_estimate: float,
    profile_analyzed: Optional[str] = None
) -> dict:
    """Record token usage for a user analysis"""
    try:
        client = get_supabase()

        openai_total = openai_prompt_tokens + openai_completion_tokens
        perplexity_total = perplexity_prompt_tokens + perplexity_completion_tokens

        data = {
            "user_id": user_id,
            "openai_prompt_tokens": openai_prompt_tokens,
            "openai_completion_tokens": openai_completion_tokens,
            "openai_total_tokens": openai_total,
            "perplexity_prompt_tokens": perplexity_prompt_tokens,
            "perplexity_completion_tokens": perplexity_completion_tokens,
            "perplexity_total_tokens": perplexity_total,
            "ensemble_units": ensemble_units,
            "total_cost_estimate": total_cost_estimate,
            "profile_analyzed": profile_analyzed
        }

        response = client.table("token_usage").insert(data).execute()
        logger.info(f"✅ Token usage recorded for user {user_id}")
        return response.data[0] if response.data else {}
    except Exception as e:
        logger.error(f"❌ Failed to record token usage: {e}")
        raise


async def get_user_token_usage(user_id: str, limit: int = 100, offset: int = 0) -> list:
    """Get token usage history for a user"""
    try:
        client = get_supabase()
        response = (client.table("token_usage")
                    .select("*")
                    .eq("user_id", user_id)
                    .order("analysis_timestamp", desc=True)
                    .limit(limit)
                    .range(offset, offset + limit - 1)
                    .execute())
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"❌ Failed to get token usage: {e}")
        return []


async def get_user_token_summary(user_id: str) -> dict:
    """Get aggregated token usage summary for a user"""
    try:
        client = get_supabase()

        # Get usage records
        response = client.table("token_usage").select(
            "*").eq("user_id", user_id).execute()
        records = response.data if response.data else []

        if not records:
            return {
                "total_analyses": 0,
                "total_openai_tokens": 0,
                "total_openai_prompt": 0,
                "total_openai_completion": 0,
                "total_perplexity_tokens": 0,
                "total_perplexity_prompt": 0,
                "total_perplexity_completion": 0,
                "total_ensemble_units": 0,
                "total_cost": 0.0,
                "first_analysis": None,
                "last_analysis": None
            }

        # Aggregate data
        total_analyses = len(records)
        total_openai_tokens = sum(
            r.get("openai_total_tokens", 0) for r in records)
        total_openai_prompt = sum(
            r.get("openai_prompt_tokens", 0) for r in records)
        total_openai_completion = sum(
            r.get("openai_completion_tokens", 0) for r in records)
        total_perplexity_tokens = sum(
            r.get("perplexity_total_tokens", 0) for r in records)
        total_perplexity_prompt = sum(
            r.get("perplexity_prompt_tokens", 0) for r in records)
        total_perplexity_completion = sum(
            r.get("perplexity_completion_tokens", 0) for r in records)
        total_ensemble_units = sum(r.get("ensemble_units", 0) for r in records)
        total_cost = sum(float(r.get("total_cost_estimate", 0))
                         for r in records)

        timestamps = [r.get("analysis_timestamp")
                      for r in records if r.get("analysis_timestamp")]
        first_analysis = min(timestamps) if timestamps else None
        last_analysis = max(timestamps) if timestamps else None

        return {
            "total_analyses": total_analyses,
            "total_openai_tokens": total_openai_tokens,
            "total_openai_prompt": total_openai_prompt,
            "total_openai_completion": total_openai_completion,
            "total_perplexity_tokens": total_perplexity_tokens,
            "total_perplexity_prompt": total_perplexity_prompt,
            "total_perplexity_completion": total_perplexity_completion,
            "total_ensemble_units": total_ensemble_units,
            "total_cost": total_cost,
            "first_analysis": first_analysis,
            "last_analysis": last_analysis
        }
    except Exception as e:
        logger.error(f"❌ Failed to get token summary: {e}")
        return {}


async def get_user_token_usage_by_period(user_id: str, period_days: int = 30) -> dict:
    """Get token usage summary for a specific time period"""
    try:
        from datetime import datetime, timedelta
        client = get_supabase()

        # Calculate start date
        start_date = (datetime.utcnow() -
                      timedelta(days=period_days)).isoformat()

        # Get usage records in period
        response = (client.table("token_usage")
                    .select("*")
                    .eq("user_id", user_id)
                    .gte("analysis_timestamp", start_date)
                    .execute())
        records = response.data if response.data else []

        if not records:
            return {
                "period_days": period_days,
                "analyses_count": 0,
                "openai_tokens": 0,
                "perplexity_tokens": 0,
                "ensemble_units": 0,
                "total_cost": 0.0
            }

        # Aggregate data
        analyses_count = len(records)
        openai_tokens = sum(r.get("openai_total_tokens", 0) for r in records)
        perplexity_tokens = sum(
            r.get("perplexity_total_tokens", 0) for r in records)
        ensemble_units = sum(r.get("ensemble_units", 0) for r in records)
        total_cost = sum(float(r.get("total_cost_estimate", 0))
                         for r in records)

        return {
            "period_days": period_days,
            "analyses_count": analyses_count,
            "openai_tokens": openai_tokens,
            "perplexity_tokens": perplexity_tokens,
            "ensemble_units": ensemble_units,
            "total_cost": total_cost
        }
    except Exception as e:
        logger.error(f"❌ Failed to get token usage by period: {e}")
        return {}


# Stripe-related database functions

async def update_user_stripe_customer(user_id: str, stripe_customer_id: str) -> dict:
    """Update user's Stripe customer ID in profile"""
    try:
        client = get_supabase()
        response = (client.table("profiles")
                    .update({"stripe_customer_id": stripe_customer_id})
                    .eq("id", user_id)
                    .execute())
        logger.info(f"✅ Updated Stripe customer ID for user {user_id}")
        return response.data[0] if response.data else {}
    except Exception as e:
        logger.error(f"❌ Failed to update Stripe customer ID: {e}")
        raise


async def update_user_subscription(
    user_id: str,
    subscription_id: str,
    status: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> dict:
    """Update user's subscription information"""
    try:
        from datetime import datetime
        client = get_supabase()

        update_data = {
            "stripe_subscription_id": subscription_id,
            "stripe_subscription_status": status
        }

        if start_date:
            update_data["subscription_start_date"] = start_date
        if end_date:
            update_data["subscription_end_date"] = end_date

        response = (client.table("profiles")
                    .update(update_data)
                    .eq("id", user_id)
                    .execute())
        logger.info(f"✅ Updated subscription for user {user_id}: {status}")
        return response.data[0] if response.data else {}
    except Exception as e:
        logger.error(f"❌ Failed to update subscription: {e}")
        raise


async def get_user_subscription_info(user_id: str) -> Optional[dict]:
    """Get user's subscription information from profile"""
    try:
        client = get_supabase()
        response = (client.table("profiles")
                    .select("stripe_customer_id, stripe_subscription_id, stripe_subscription_status, subscription_start_date, subscription_end_date")
                    .eq("id", user_id)
                    .execute())
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"❌ Failed to get subscription info: {e}")
        return None


async def check_active_subscription(user_id: str) -> bool:
    """
    Check if user has an active subscription

    Args:
        user_id: Supabase user ID

    Returns:
        True if user has active subscription, False otherwise
    """
    try:
        subscription_info = await get_user_subscription_info(user_id)

        if not subscription_info:
            return False

        status = subscription_info.get("stripe_subscription_status", "")

        # Check if subscription is in active state
        # Active states: 'active', 'trialing'
        active_states = ['active', 'trialing']

        return status.lower() in active_states

    except Exception as e:
        logger.error(f"❌ Failed to check subscription status: {e}")
        return False


async def get_user_by_stripe_customer_id(stripe_customer_id: str) -> Optional[dict]:
    """Get user by Stripe customer ID"""
    try:
        client = get_supabase()
        response = (client.table("profiles")
                    .select("*")
                    .eq("stripe_customer_id", stripe_customer_id)
                    .execute())
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"❌ Failed to get user by Stripe customer ID: {e}")
        return None


# ============================================================================
# Free Trial Functions (1 free analysis per day)
# ============================================================================

async def can_use_free_trial(user_id: str) -> bool:
    """
    Check if user can use their daily free trial (1 analysis per day)

    Args:
        user_id: Supabase user ID

    Returns:
        True if user can use free trial today, False otherwise
    """
    try:
        client = get_supabase()

        # Call the database function
        response = client.rpc('can_use_free_trial', {
                              'p_user_id': user_id}).execute()

        if response.data is not None:
            return bool(response.data)

        return False

    except Exception as e:
        logger.error(f"❌ Failed to check free trial eligibility: {e}")
        # FALLBACK: Allow free trial if tables don't exist (before migration)
        logger.warning(
            "⚠️ Allowing free trial (database may not be initialized)")
        return True


async def record_free_trial_usage(user_id: str, profile_analyzed: Optional[str] = None) -> bool:
    """
    Record a free trial analysis usage

    Args:
        user_id: Supabase user ID
        profile_analyzed: TikTok profile that was analyzed

    Returns:
        True if recorded successfully, False otherwise
    """
    try:
        client = get_supabase()

        # Call the database function
        client.rpc('record_free_trial_usage', {
            'p_user_id': user_id,
            'p_profile_analyzed': profile_analyzed
        }).execute()

        logger.info(f"✅ Recorded free trial usage for user {user_id}")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to record free trial usage: {e}")
        logger.error(f"❌ Error details: {type(e).__name__}: {str(e)}")
        # Re-raise exception so endpoint can handle it properly
        raise Exception(f"Failed to record free trial usage: {str(e)}") from e


async def get_free_trial_info(user_id: str) -> Optional[dict]:
    """
    Get detailed information about user's free trial usage

    Args:
        user_id: Supabase user ID

    Returns:
        Dict with free trial info or None
    """
    try:
        client = get_supabase()

        # Call the database function
        response = client.rpc('get_free_trial_info', {
                              'p_user_id': user_id}).execute()

        if response.data and len(response.data) > 0:
            return response.data[0]

        return None

    except Exception as e:
        logger.error(f"❌ Failed to get free trial info: {e}")

        # FALLBACK: If database tables don't exist, return default values
        # This prevents 404 errors and allows app to work before migration
        logger.warning(
            "⚠️ Returning default free trial info (database may not be initialized)")
        return {
            "can_use_today": True,
            "today_count": 0,
            "last_used": None,
            "total_free_analyses": 0
        }


async def check_user_can_analyze(user_id: str) -> tuple[bool, str, Optional[dict]]:
    """
    Check if user can perform an analysis (either has subscription or free trial available)

    Args:
        user_id: Supabase user ID

    Returns:
        Tuple of (can_analyze: bool, reason: str, details: dict)
    """
    try:
        # Check if user has active subscription
        has_subscription = await check_active_subscription(user_id)

        if has_subscription:
            return True, "active_subscription", {"type": "subscription"}

        # Check if user can use free trial
        can_use_trial = await can_use_free_trial(user_id)

        if can_use_trial:
            trial_info = await get_free_trial_info(user_id)
            return True, "free_trial", {"type": "free_trial", "info": trial_info}

        # User cannot analyze - no subscription and free trial exhausted
        trial_info = await get_free_trial_info(user_id)
        return False, "no_access", {
            "type": "no_access",
            "trial_info": trial_info,
            "message": "You've used your free daily analysis. Subscribe to get unlimited access!"
        }

    except Exception as e:
        logger.error(f"❌ Failed to check if user can analyze: {e}")
        return False, "error", {"type": "error", "message": str(e)}


# Initialize on module import
try:
    init_supabase()
except Exception as e:
    logger.warning(f"⚠️ Supabase client initialization deferred: {e}")
