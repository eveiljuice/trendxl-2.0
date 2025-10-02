"""
Structured error responses for better client-side handling
"""
from typing import Optional, Dict, Any
from fastapi import HTTPException


class AuthError(HTTPException):
    """Base authentication error with structured details"""

    def __init__(
        self,
        status_code: int,
        message: str,
        error_code: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status_code,
            detail={
                "error": message,
                "error_code": error_code,
                "details": details
            }
        )


class UserAlreadyExistsError(AuthError):
    """User with this email already exists"""

    def __init__(self, email: str):
        super().__init__(
            status_code=400,
            message=f"User with this email already exists. Please login instead.",
            error_code="USER_ALREADY_EXISTS",
            details={"email": email, "suggestion": "switch_to_login"}
        )


class UserNotFoundError(AuthError):
    """User with this email not found"""

    def __init__(self, email: str):
        super().__init__(
            status_code=404,
            message=f"User with email '{email}' not found. Please register first.",
            error_code="USER_NOT_FOUND",
            details={"email": email, "suggestion": "switch_to_register"}
        )


class InvalidCredentialsError(AuthError):
    """Invalid login credentials"""

    def __init__(self):
        super().__init__(
            status_code=401,
            message="Invalid email or password. Please check your credentials.",
            error_code="INVALID_CREDENTIALS",
            details={"suggestion": "check_credentials"}
        )


class InvalidEmailError(AuthError):
    """Invalid email format"""

    def __init__(self, email: str):
        super().__init__(
            status_code=400,
            message="Invalid email address format.",
            error_code="INVALID_EMAIL",
            details={"email": email}
        )


class WeakPasswordError(AuthError):
    """Password doesn't meet requirements"""

    def __init__(self, requirement: str = "at least 6 characters"):
        super().__init__(
            status_code=400,
            message=f"Password must be {requirement}.",
            error_code="WEAK_PASSWORD",
            details={"requirement": requirement}
        )


class InvalidUsernameError(AuthError):
    """Username doesn't meet requirements"""

    def __init__(self, requirement: str = "at least 3 characters"):
        super().__init__(
            status_code=400,
            message=f"Username must be {requirement}.",
            error_code="INVALID_USERNAME",
            details={"requirement": requirement}
        )


class EmailConfirmationRequiredError(AuthError):
    """Email confirmation required"""

    def __init__(self, email: str):
        super().__init__(
            status_code=403,
            message="Please confirm your email address. Check your inbox for confirmation link.",
            error_code="EMAIL_CONFIRMATION_REQUIRED",
            details={"email": email}
        )


class RateLimitError(AuthError):
    """Rate limit exceeded"""

    def __init__(self, retry_after: int = 60):
        super().__init__(
            status_code=429,
            message=f"Too many attempts. Please try again in {retry_after} seconds.",
            error_code="RATE_LIMIT_EXCEEDED",
            details={"retry_after": retry_after}
        )


def parse_supabase_error(error: Exception, context: str = "auth") -> AuthError:
    """
    Parse Supabase error and return appropriate structured error

    Args:
        error: The exception from Supabase
        context: Context of the error (auth, profile, etc.)

    Returns:
        Structured AuthError
    """
    error_str = str(error).lower()

    # User already exists
    if "already" in error_str or "exists" in error_str or "duplicate" in error_str:
        # Try to extract email if available
        return UserAlreadyExistsError(email="provided email")

    # Invalid credentials
    if "invalid" in error_str and ("password" in error_str or "credentials" in error_str):
        return InvalidCredentialsError()

    # User not found
    if "not found" in error_str or "does not exist" in error_str:
        return UserNotFoundError(email="provided email")

    # Email issues
    if "email" in error_str and "invalid" in error_str:
        return InvalidEmailError(email="provided email")

    # Password issues
    if "password" in error_str:
        return WeakPasswordError()

    # Rate limiting
    if "rate" in error_str or "too many" in error_str:
        return RateLimitError()

    # Default to generic auth error
    return AuthError(
        status_code=500,
        message=str(error),
        error_code="AUTH_ERROR",
        details={"original_error": error_str}
    )







