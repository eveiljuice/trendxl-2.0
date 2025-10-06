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


async def get_user_admin_status(user_id: str) -> bool:
    """
    Get admin status for a user from database

    Args:
        user_id: User UUID

    Returns:
        bool: True if user is admin, False otherwise
    """
    try:
        client = get_supabase()
        response = client.table("profiles").select(
            "is_admin").eq("id", user_id).execute()

        if response.data and len(response.data) > 0:
            return response.data[0].get("is_admin", False)
        return False
    except Exception as e:
        logger.error(f"Failed to get admin status for user {user_id}: {e}")
        return False


async def set_user_admin_status(user_id: str, is_admin: bool) -> bool:
    """
    Set admin status for a user

    Args:
        user_id: User UUID
        is_admin: Admin status to set

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        client = get_supabase()
        client.table("profiles").update(
            {"is_admin": is_admin}).eq("id", user_id).execute()
        logger.info(f"✅ Admin status set to {is_admin} for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to set admin status for user {user_id}: {e}")
        return False


async def set_user_admin_by_email(email: str, is_admin: bool) -> bool:
    """
    Set admin status for a user by email

    Args:
        email: User email
        is_admin: Admin status to set

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        client = get_supabase()
        response = client.table("profiles").select(
            "id").eq("email", email).execute()

        if not response.data or len(response.data) == 0:
            logger.error(f"User not found with email: {email}")
            return False

        user_id = response.data[0]["id"]
        return await set_user_admin_status(user_id, is_admin)
    except Exception as e:
        logger.error(f"Failed to set admin status by email {email}: {e}")
        return False


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
    is_admin: bool = False  # Admin users bypass all subscription limits


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

        # Get admin status from database
        is_admin = await get_user_admin_status(auth_response.user.id)

        # Return response with or without session
        return {
            "access_token": auth_response.session.access_token if auth_response.session else "",
            "token_type": "bearer",
            "user": {
                "id": auth_response.user.id,
                "email": auth_response.user.email or user_data.email,
                "username": user_data.username,
                "full_name": user_data.full_name,
                "created_at": auth_response.user.created_at,
                "is_admin": is_admin
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

        # Get admin status from database
        is_admin = await get_user_admin_status(auth_response.user.id)

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
                "last_login": auth_response.user.last_sign_in_at,
                "is_admin": is_admin
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
        ValueError: If token is invalid or expired
    """
    try:
        client = get_supabase()

        # Get user from token (Supabase validates JWT internally)
        user_response = client.auth.get_user(access_token)

        if user_response.user is None:
            raise ValueError("Invalid token")

        user = user_response.user
        username = user.user_metadata.get("username", "")
        full_name = user.user_metadata.get("full_name", "")

        # Get admin status from database
        is_admin = await get_user_admin_status(user.id)

        return {
            "id": user.id,
            "email": user.email,
            "username": username,
            "full_name": full_name,
            "avatar_url": user.user_metadata.get("avatar_url"),
            "bio": user.user_metadata.get("bio"),
            "created_at": user.created_at,
            "last_login": user.last_sign_in_at,
            "is_admin": is_admin
        }

    except Exception as e:
        error_msg = str(e).lower()

        # Check if token is expired
        if "expired" in error_msg or "invalid jwt" in error_msg:
            logger.warning(f"⚠️ Token expired or invalid: {e}")
            raise ValueError("Token expired. Please refresh your session.")

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

        # Get admin status from database
        is_admin = await get_user_admin_status(user.id)

        return {
            "id": user.id,
            "email": user.email,
            "username": user.user_metadata.get("username", ""),
            "full_name": user.user_metadata.get("full_name"),
            "avatar_url": user.user_metadata.get("avatar_url"),
            "bio": user.user_metadata.get("bio"),
            "created_at": user.created_at,
            "last_login": user.last_sign_in_at,
            "is_admin": is_admin
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
