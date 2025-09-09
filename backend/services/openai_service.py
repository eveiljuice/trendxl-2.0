"""
OpenAI Service for analyzing TikTok posts and extracting hashtags
"""
import json
import logging
from typing import List, Dict, Any
from openai import OpenAI
from models import TikTokPost, GPTAnalysisResponse
from utils import retry_with_backoff
from config import settings

logger = logging.getLogger(__name__)

class OpenAIService:
    """Service for OpenAI GPT analysis"""
    
    def __init__(self):
        """Initialize OpenAI client"""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.temperature = settings.openai_temperature
        self.max_tokens = settings.openai_max_tokens
        logger.info(f"OpenAI service initialized with model: {self.model}")
    
    async def analyze_posts_for_hashtags(
        self, 
        posts: List[TikTokPost], 
        profile_bio: str = ""
    ) -> GPTAnalysisResponse:
        """
        Analyze TikTok posts and extract trending hashtags using GPT
        
        Args:
            posts: List of TikTok posts to analyze
            profile_bio: User's profile bio for context
            
        Returns:
            GPTAnalysisResponse with top hashtags and analysis
            
        Raises:
            Exception: If analysis fails
        """
        if not posts:
            raise Exception("No posts provided for analysis")
        
        logger.info(f"Analyzing {len(posts)} posts for hashtag extraction")
        
        try:
            # Sort posts by engagement and take top 5 most popular
            top_posts = sorted(
                posts, 
                key=lambda p: p.views + p.likes * 10, 
                reverse=True
            )[:5]
            
            # Use retry with backoff for OpenAI API calls
            analysis = await retry_with_backoff(
                func=lambda: self._call_gpt_analysis(top_posts, profile_bio),
                max_retries=3,
                base_delay=1.0,
                retry_condition=self._should_retry_openai_error
            )
            
            logger.info(f"Successfully extracted hashtags: {analysis.top_hashtags}")
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze posts with GPT: {e}")
            
            # Try fallback hashtag extraction
            fallback_hashtags = self._generate_fallback_hashtags(posts)
            return GPTAnalysisResponse(
                top_hashtags=fallback_hashtags,
                analysis_summary="AI analysis failed, used fallback hashtag extraction based on post content frequency"
            )
    
    async def _call_gpt_analysis(
        self, 
        posts: List[TikTokPost], 
        profile_bio: str
    ) -> GPTAnalysisResponse:
        """Make actual GPT API call for analysis"""
        
        # Prepare context for GPT
        posts_context = []
        for i, post in enumerate(posts[:3]):  # Use top 3 posts
            posts_context.append(
                f"Post {i + 1}:\n"
                f"Caption: \"{post.caption}\"\n"
                f"Views: {post.views:,}\n"
                f"Likes: {post.likes:,}\n"
                f"Hashtags: {', '.join(post.hashtags)}"
            )
        
        posts_text = "\n\n".join(posts_context)
        
        system_prompt = """You are a TikTok trends expert. Your task is to analyze a user's most popular posts and extract 5 most relevant and trending hashtags.

Selection criteria for hashtags:
1. Frequency of use in popular posts
2. Current relevance and trending potential
3. Content theme relevance
4. Potential for finding similar trending videos
5. Popularity in TikTok community

IMPORTANT: Return hashtags WITHOUT the # symbol, separated by commas in JSON format."""

        user_prompt = f"""User Profile:
Bio: "{profile_bio}"

Top posts by engagement:
{posts_text}

Analyze these posts and extract 5 most relevant trending hashtags for finding similar popular videos. Return result in JSON format:

{{
  "top_hashtags": ["hashtag1", "hashtag2", "hashtag3", "hashtag4", "hashtag5"],
  "analysis_summary": "Brief explanation of hashtag selection (2-3 sentences)"
}}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            if not content:
                raise Exception("Empty response from GPT")
            
            # Parse JSON response
            try:
                analysis_data = json.loads(content)
                
                # Validate response structure
                if not isinstance(analysis_data.get('top_hashtags'), list):
                    raise Exception("Invalid response structure from GPT")
                
                # Clean and validate hashtags
                hashtags = []
                for tag in analysis_data['top_hashtags'][:5]:
                    clean_tag = str(tag).replace('#', '').lower().strip()
                    if clean_tag and len(clean_tag) > 0:
                        hashtags.append(clean_tag)
                
                if not hashtags:
                    raise Exception("No valid hashtags extracted from GPT response")
                
                return GPTAnalysisResponse(
                    top_hashtags=hashtags,
                    analysis_summary=analysis_data.get('analysis_summary', '')
                )
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse GPT response JSON: {e}")
                raise Exception("Invalid JSON response from GPT")
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            
            # Check for specific OpenAI errors
            if "api key" in str(e).lower():
                raise Exception("OpenAI API key authentication failed")
            elif "quota" in str(e).lower():
                raise Exception("OpenAI API quota exceeded")
            elif "rate limit" in str(e).lower():
                raise Exception("OpenAI API rate limit reached")
            else:
                raise Exception(f"OpenAI API error: {str(e)}")
    
    def _generate_fallback_hashtags(self, posts: List[TikTokPost]) -> List[str]:
        """
        Generate fallback hashtags when GPT analysis fails
        
        Args:
            posts: List of posts to extract hashtags from
            
        Returns:
            List of fallback hashtags
        """
        logger.info("Generating fallback hashtags from post content")
        
        # Count hashtag frequency across all posts
        hashtag_count: Dict[str, int] = {}
        
        for post in posts:
            for hashtag in post.hashtags:
                clean_tag = hashtag.replace('#', '').lower().strip()
                if clean_tag:
                    hashtag_count[clean_tag] = hashtag_count.get(clean_tag, 0) + 1
        
        # Sort by frequency and get top hashtags
        sorted_hashtags = sorted(
            hashtag_count.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        fallback_hashtags = [tag for tag, _ in sorted_hashtags[:5]]
        
        # Only use hashtags actually extracted from user content
        # No artificial defaults - only real hashtags from posts
        valid_hashtags = []
        for tag in fallback_hashtags:
            if len(tag) >= 3 and len(tag) <= 20 and tag.isalnum():  # Valid hashtag format
                valid_hashtags.append(tag)
        
        # If we have very few hashtags from content, that's the reality
        # Better to have 1-2 real hashtags than 5 fake ones
        if len(valid_hashtags) < 2:
            logger.warning(f"Only {len(valid_hashtags)} valid hashtags extracted from content")
        
        fallback_hashtags = valid_hashtags[:5]  # Max 5, but could be less
        
        logger.info(f"Generated fallback hashtags: {fallback_hashtags[:5]}")
        return fallback_hashtags[:5]
    
    def _should_retry_openai_error(self, error: Exception) -> bool:
        """
        Determine if OpenAI error should trigger a retry
        
        Args:
            error: Exception to check
            
        Returns:
            True if should retry, False otherwise
        """
        error_str = str(error).lower()
        
        # Retry on rate limits and server errors
        retry_conditions = [
            "rate limit",
            "server error",
            "timeout",
            "connection",
            "temporary"
        ]
        
        for condition in retry_conditions:
            if condition in error_str:
                return True
        
        # Don't retry on authentication or quota errors
        no_retry_conditions = [
            "api key",
            "authentication", 
            "quota",
            "billing"
        ]
        
        for condition in no_retry_conditions:
            if condition in error_str:
                return False
        
        return False
    
    async def test_connection(self) -> bool:
        """
        Test OpenAI API connection
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Test connection"}],
                max_tokens=5,
                temperature=0
            )
            
            return bool(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"OpenAI connection test failed: {e}")
            return False
