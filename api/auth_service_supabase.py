"""
Authentication service using Supabase Auth
Replaces SQLite-based authentication with Supabase Auth
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field
from supabase import Client
from supabase_client import get_supabase
import logging

logger = logging.getLogger(__name__)


class UserCreate(BaseModel):
    """User registration model"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=30)
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    """User login model"""
    email: EmailStr
    password: str


class UserProfile(BaseModel):
    """User profile model (public data)"""
    id: str  # UUID from Supabase
    email: str
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    created_at: str
    last_login: Optional[str] = None


class UserProfileUpdate(BaseModel):
    """User profile update model"""
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None


class Token(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str = "bearer"
    user: UserProfile


class TokenData(BaseModel):
    """Token data model"""
    user_id: str
    email: str


async def register_user(user_data: UserCreate) -> Dict[str, Any]:
    """
    Register a new user using Supabase Auth

    Args:
        user_data: User registration data

    Returns:
        Dict with access_token and user data

    Raises:
        ValueError: If registration fails
    """
    try:
        client = get_supabase()

        # Register user with Supabase Auth
        auth_response = client.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
            "options": {
                "data": {
                    "username": user_data.username,
                    "full_name": user_data.full_name
                }
            }
        })

        # Check if user is already registered
        if auth_response.user is None:
            # Check if this is a "user already exists" error
            error_msg = str(auth_response) if hasattr(
                auth_response, '__str__') else "No user returned"
            if "already" in error_msg.lower() or "exists" in error_msg.lower():
                raise ValueError(
                    "User with this email already exists. Please login instead.")
            raise ValueError("Registration failed: No user returned")

        # Create profile in public.profiles table (if needed)
        # Note: You may want to use Supabase triggers to auto-create profiles
        profile_data = {
            "id": auth_response.user.id,
            "email": user_data.email,
            "username": user_data.username,
            "full_name": user_data.full_name,
        }

        # Insert into profiles table (optional, can be done via trigger)
        try:
            client.table("profiles").insert(profile_data).execute()
        except Exception as e:
            logger.warning(f"Profile creation skipped (may use trigger): {e}")

        logger.info(f"✅ User registered: {user_data.email}")

        # Return response with or without session
        return {
            "access_token": auth_response.session.access_token if auth_response.session else "",
            "token_type": "bearer",
            "user": {
                "id": auth_response.user.id,
                "email": auth_response.user.email or user_data.email,
                "username": user_data.username,
                "full_name": user_data.full_name,
                "created_at": auth_response.user.created_at
            }
        }

    except ValueError as e:
        # Re-raise ValueError as-is for proper error messages
        logger.error(f"❌ Registration failed: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Registration failed: {e}")
        # Check for specific Supabase errors
        error_str = str(e)
        if "already" in error_str.lower() or "exists" in error_str.lower():
            raise ValueError(
                "User with this email already exists. Please login instead.")
        raise ValueError(f"Registration failed: {error_str}")


async def login_user(login_data: UserLogin) -> Dict[str, Any]:
    """
    Login user using Supabase Auth

    Args:
        login_data: User login credentials

    Returns:
        Dict with access_token and user data

    Raises:
        ValueError: If login fails
    """
    try:
        client = get_supabase()

        # Login with Supabase Auth
        auth_response = client.auth.sign_in_with_password({
            "email": login_data.email,
            "password": login_data.password
        })

        if auth_response.user is None or auth_response.session is None:
            raise ValueError("Invalid credentials")

        # Get user profile from metadata or database
        username = auth_response.user.user_metadata.get("username", "")
        full_name = auth_response.user.user_metadata.get("full_name", "")

        logger.info(f"✅ User logged in: {login_data.email}")

        return {
            "access_token": auth_response.session.access_token,
            "token_type": "bearer",
            "user": {
                "id": auth_response.user.id,
                "email": auth_response.user.email,
                "username": username,
                "full_name": full_name,
                "created_at": auth_response.user.created_at,
                "last_login": auth_response.user.last_sign_in_at
            }
        }

    except Exception as e:
        logger.error(f"❌ Login failed: {e}")
        raise ValueError(f"Login failed: Invalid credentials")


async def get_current_user(access_token: str) -> Dict[str, Any]:
    """
    Get current user from Supabase Auth token

    Args:
        access_token: JWT access token

    Returns:
        User profile data

    Raises:
        ValueError: If token is invalid
    """
    try:
        client = get_supabase()

        # Set the session with the token
        client.auth.set_session(access_token, refresh_token="")

        # Get user from token
        user_response = client.auth.get_user(access_token)

        if user_response.user is None:
            raise ValueError("Invalid token")

        user = user_response.user
        username = user.user_metadata.get("username", "")
        full_name = user.user_metadata.get("full_name", "")

        return {
            "id": user.id,
            "email": user.email,
            "username": username,
            "full_name": full_name,
            "avatar_url": user.user_metadata.get("avatar_url"),
            "bio": user.user_metadata.get("bio"),
            "created_at": user.created_at,
            "last_login": user.last_sign_in_at
        }

    except Exception as e:
        logger.error(f"❌ Get user failed: {e}")
        raise ValueError("Invalid or expired token")


async def update_user_profile(access_token: str, profile_data: UserProfileUpdate) -> Dict[str, Any]:
    """
    Update user profile using Supabase Auth

    Args:
        access_token: JWT access token
        profile_data: Profile update data

    Returns:
        Updated user profile

    Raises:
        ValueError: If update fails
    """
    try:
        client = get_supabase()

        # Update user metadata
        update_data = {}
        if profile_data.full_name is not None:
            update_data["full_name"] = profile_data.full_name
        if profile_data.avatar_url is not None:
            update_data["avatar_url"] = profile_data.avatar_url
        if profile_data.bio is not None:
            update_data["bio"] = profile_data.bio

        user_response = client.auth.update_user({
            "data": update_data
        })

        if user_response.user is None:
            raise ValueError("Update failed")

        user = user_response.user

        logger.info(f"✅ Profile updated for user: {user.email}")

        return {
            "id": user.id,
            "email": user.email,
            "username": user.user_metadata.get("username", ""),
            "full_name": user.user_metadata.get("full_name"),
            "avatar_url": user.user_metadata.get("avatar_url"),
            "bio": user.user_metadata.get("bio"),
            "created_at": user.created_at,
            "last_login": user.last_sign_in_at
        }

    except Exception as e:
        logger.error(f"❌ Profile update failed: {e}")
        raise ValueError(f"Profile update failed: {str(e)}")


async def logout_user(access_token: str) -> bool:
    """
    Logout user from Supabase Auth

    Args:
        access_token: JWT access token

    Returns:
        True if logout successful
    """
    try:
        client = get_supabase()
        client.auth.sign_out()
        logger.info("✅ User logged out")
        return True
    except Exception as e:
        logger.error(f"❌ Logout failed: {e}")
        return False


# Compatibility functions (not needed for Supabase Auth but kept for API compatibility)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Not used with Supabase Auth - Supabase handles password verification"""
    logger.warning("verify_password called but not used with Supabase Auth")
    return True


def get_password_hash(password: str) -> str:
    """Not used with Supabase Auth - Supabase handles password hashing"""
    logger.warning("get_password_hash called but not used with Supabase Auth")
    return ""


def create_access_token(data: dict) -> str:
    """Not used with Supabase Auth - Supabase creates JWT tokens"""
    logger.warning(
        "create_access_token called but not used with Supabase Auth")
    return ""


def decode_access_token(token: str) -> Optional[TokenData]:
    """
    Decode Supabase JWT token
    Note: Supabase handles token validation, this is for compatibility
    """
    try:
        client = get_supabase()
        user = client.auth.get_user(token)
        if user and user.user:
            return TokenData(user_id=user.user.id, email=user.user.email or "")
        return None
    except Exception as e:
        logger.error(f"Token decode failed: {e}")
        return None


def user_to_profile(user_dict: dict) -> UserProfile:
    """Convert user dict to UserProfile model"""
    from datetime import datetime

    # Convert datetime objects to ISO format strings
    created_at = user_dict.get("created_at", "")
    if isinstance(created_at, datetime):
        created_at = created_at.isoformat()
    elif not created_at:
        created_at = datetime.utcnow().isoformat()

    last_login = user_dict.get("last_login")
    if isinstance(last_login, datetime):
        last_login = last_login.isoformat()

    return UserProfile(
        id=user_dict.get("id", ""),
        email=user_dict.get("email", ""),
        username=user_dict.get("username", ""),
        full_name=user_dict.get("full_name"),
        avatar_url=user_dict.get("avatar_url"),
        bio=user_dict.get("bio"),
        created_at=created_at,
        last_login=last_login
    )
