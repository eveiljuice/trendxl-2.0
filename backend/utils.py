"""
Utility functions for TrendXL 2.0 Backend
"""
import re
import time
import asyncio
import logging
from typing import List, Optional, Callable, Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def extract_tiktok_username(profile_input: str) -> str:
    """
    Extract TikTok username from URL or username string
    
    Args:
        profile_input: TikTok URL or username
        
    Returns:
        Clean username without @ symbol
    """
    # Remove whitespace
    profile_input = profile_input.strip()
    
    # If it's a URL, extract username from it
    if profile_input.startswith(('http://', 'https://')):
        parsed = urlparse(profile_input)
        path = parsed.path.strip('/')
        
        # Handle different TikTok URL formats
        if path.startswith('@'):
            username = path[1:].split('/')[0]
        else:
            username = path.split('/')[0]
    else:
        # Remove @ symbol if present
        username = profile_input.lstrip('@')
    
    # Clean username (remove any remaining special characters)
    username = re.sub(r'[^a-zA-Z0-9._]', '', username)
    
    if not username:
        raise ValueError("Invalid TikTok username or URL")
    
    return username

def extract_hashtags_from_text(text: str) -> List[str]:
    """
    Extract hashtags from text using regex
    
    Args:
        text: Text to extract hashtags from
        
    Returns:
        List of hashtags (lowercase, without # symbol)
    """
    if not text:
        return []
    
    # Regex pattern to match hashtags (supports Unicode characters)
    hashtag_regex = r'#[\w\u4e00-\u9fff]+'
    matches = re.findall(hashtag_regex, text, re.IGNORECASE)
    
    # Clean and lowercase hashtags
    hashtags = [tag[1:].lower() for tag in matches if len(tag) > 1]
    
    # Remove duplicates while preserving order
    unique_hashtags = []
    for hashtag in hashtags:
        if hashtag not in unique_hashtags:
            unique_hashtags.append(hashtag)
    
    return unique_hashtags

async def retry_with_backoff(
    func: Callable[[], Any],
    max_retries: int = 3,
    base_delay: float = 1.0,
    exponential_base: float = 2.0,
    retry_condition: Optional[Callable[[Exception], bool]] = None
) -> Any:
    """
    Retry function with exponential backoff
    
    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds
        exponential_base: Base for exponential backoff
        retry_condition: Function to determine if error should trigger retry
        
    Returns:
        Result from successful function call
        
    Raises:
        Last exception if all retries fail
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            result = func()
            # Support both sync and async callables
            if asyncio.iscoroutine(result):
                return await result
            return result
        except Exception as e:
            last_exception = e
            
            # Check if we should retry this error
            if retry_condition and not retry_condition(e):
                raise e
            
            # Don't wait after the last attempt
            if attempt < max_retries:
                delay = base_delay * (exponential_base ** attempt)
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay:.2f}s: {e}")
                await asyncio.sleep(delay)
    
    # All retries exhausted
    raise last_exception

def default_retry_condition(error: Exception) -> bool:
    """
    Default retry condition for API requests
    
    Args:
        error: Exception to check
        
    Returns:
        True if should retry, False otherwise
    """
    # Retry on specific HTTP status codes and network errors
    if hasattr(error, 'response') and hasattr(error.response, 'status_code'):
        status = error.response.status_code
        # Retry on server errors and rate limits
        if status in [429, 502, 503, 504]:
            return True
    
    # Retry on connection errors
    if hasattr(error, 'code'):
        if error.code in ['ECONNRESET', 'ETIMEDOUT', 'ECONNREFUSED']:
            return True
    
    # Fallback: retry based on error message content (some SDKs raise plain Exceptions)
    err = str(error).lower()
    transient_markers = [
        'rate limit', 'too many requests', 'temporarily unavailable',
        'timeout', 'timed out', 'connection reset', 'connection aborted',
        '502', '503', '504'
    ]
    return any(marker in err for marker in transient_markers)

def validate_hashtag(hashtag: str) -> str:
    """
    Validate and clean hashtag
    
    Args:
        hashtag: Raw hashtag string
        
    Returns:
        Cleaned hashtag without # symbol
        
    Raises:
        ValueError: If hashtag is invalid
    """
    if not hashtag:
        raise ValueError("Hashtag cannot be empty")
    
    # Remove # symbol if present
    clean_hashtag = hashtag.lstrip('#').strip()
    
    # Validate hashtag format
    if not re.match(r'^[\w\u4e00-\u9fff]+$', clean_hashtag):
        raise ValueError("Invalid hashtag format")
    
    return clean_hashtag.lower()

def format_number(num: int) -> str:
    """
    Format large numbers for display
    
    Args:
        num: Number to format
        
    Returns:
        Formatted number string
    """
    if num >= 1_000_000_000:
        return f"{num / 1_000_000_000:.1f}B"
    elif num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}K"
    else:
        return str(num)

def get_current_timestamp() -> str:
    """
    Get current timestamp in ISO format
    
    Returns:
        ISO formatted timestamp string
    """
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

def safe_get_nested(data: dict, keys: List[str], default: Any = None) -> Any:
    """
    Safely get nested dictionary value
    
    Args:
        data: Dictionary to search in
        keys: List of keys to traverse
        default: Default value if key not found
        
    Returns:
        Value if found, default otherwise
    """
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self, max_requests: int, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed for given key"""
        now = time.time()
        window_start = now - self.window_seconds
        
        # Clean old requests
        if key in self.requests:
            self.requests[key] = [req_time for req_time in self.requests[key] if req_time > window_start]
        else:
            self.requests[key] = []
        
        # Check if under limit
        if len(self.requests[key]) < self.max_requests:
            self.requests[key].append(now)
            return True
        
        return False
    
    def get_reset_time(self, key: str) -> int:
        """Get time until rate limit resets"""
        if key not in self.requests or not self.requests[key]:
            return 0
        
        oldest_request = min(self.requests[key])
        reset_time = oldest_request + self.window_seconds
        return max(0, int(reset_time - time.time()))
