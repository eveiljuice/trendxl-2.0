"""
Authentication service for user management
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field
import logging

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
# Should be in .env
SECRET_KEY = "your-secret-key-change-this-in-production-use-env-variable"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


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
    id: int
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
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserProfile


class TokenData(BaseModel):
    """Token payload data"""
    user_id: Optional[int] = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def decode_access_token(token: str) -> Optional[TokenData]:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")

        if user_id is None:
            return None

        return TokenData(user_id=user_id)

    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        return None


def user_to_profile(user_dict: dict) -> UserProfile:
    """Convert database user dict to UserProfile model"""
    return UserProfile(
        id=user_dict["id"],
        email=user_dict["email"],
        username=user_dict["username"],
        full_name=user_dict.get("full_name"),
        avatar_url=user_dict.get("avatar_url"),
        bio=user_dict.get("bio"),
        created_at=user_dict["created_at"],
        last_login=user_dict.get("last_login")
    )
