"""
Perplexity API Service for Niche Analysis
Uses Sonar model to analyze TikTok profiles and determine user niches
"""
import logging
import asyncio
from typing import Dict, Any, Optional
import httpx
from pydantic import BaseModel
from config import settings

logger = logging.getLogger(__name__)


class NicheAnalysis(BaseModel):
    """Niche analysis result model"""
    niche_category: str
    niche_description: str
    confidence_score: float
    key_topics: list[str]
    target_audience: str
    content_style: str


class PerplexityService:
    """Service for analyzing user niches using Perplexity Sonar model"""

    def __init__(self):
        """Initialize Perplexity service with API configuration"""
        self.api_key = settings.perplexity_api_key
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.model = settings.perplexity_model
        self.temperature = settings.perplexity_temperature
        self.max_tokens = settings.perplexity_max_tokens

        # HTTP client with timeout and retry configuration
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(60.0),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )

        logger.info("✅ Perplexity service initialized with Sonar model")

    async def analyze_user_niche(
        self,
        username: str,
        bio: str,
        recent_posts_content: list[str],
        follower_count: int = 0,
        video_count: int = 0
    ) -> NicheAnalysis:
        """
        Analyze user niche based on profile and content data

        Args:
            username: TikTok username
            bio: User bio/description
            recent_posts_content: List of recent post captions/descriptions
            follower_count: Number of followers
            video_count: Number of videos posted

        Returns:
            NicheAnalysis with detailed niche information
        """
        logger.info(
            f"🔍 Analyzing niche for @{username} using Perplexity Sonar")

        try:
            # Prepare context for analysis
            # Limit to 10 most recent
            posts_text = "\n".join(recent_posts_content[:10])

            # Create comprehensive prompt for niche analysis
            prompt = self._create_niche_analysis_prompt(
                username=username,
                bio=bio,
                posts_content=posts_text,
                follower_count=follower_count,
                video_count=video_count
            )

            # Make API request to Perplexity
            response = await self._make_api_request(prompt)

            # Parse the response into structured niche analysis
            niche_analysis = self._parse_niche_response(response)

            logger.info(
                f"✅ Niche analysis completed for @{username}: {niche_analysis.niche_category}")
            return niche_analysis

        except Exception as e:
            logger.error(f"❌ Niche analysis failed for @{username}: {e}")
            # Return fallback analysis
            return self._create_fallback_analysis(username, bio)

    def _create_niche_analysis_prompt(
        self,
        username: str,
        bio: str,
        posts_content: str,
        follower_count: int,
        video_count: int
    ) -> str:
        """Create comprehensive prompt for niche analysis"""

        return f"""Analyze this TikTok user's niche and content category based on their profile data:

**Profile Information:**
- Username: @{username}
- Bio: {bio or "No bio provided"}
- Followers: {follower_count:,}
- Total Videos: {video_count}

**Recent Content (Post Captions):**
{posts_content or "No recent posts available"}

**Analysis Task:**
Determine the user's primary niche/category and provide a structured analysis. Consider:

1. **Content Theme**: What main topics/themes do they focus on?
2. **Audience**: Who is their target demographic?
3. **Style**: What's their content style and approach?
4. **Industry/Vertical**: What industry or vertical do they operate in?

**Required Output Format (JSON-like structure):**
```
Niche Category: [Primary category - be specific, e.g., "Tech Reviews", "Fitness Training", "Comedy Skits", "Fashion Styling", "Food Recipes", etc.]

Niche Description: [2-3 sentence concise description of their niche and what makes them unique]

Confidence Score: [0.0-1.0 - how confident you are in this analysis]

Key Topics: [List 3-5 main topics/themes they cover]

Target Audience: [Primary demographic they target]

Content Style: [Their approach/style - e.g., "Educational tutorials", "Entertaining skits", "Lifestyle vlogs", etc.]
```

Focus on being specific and actionable. The niche should be clear enough to recommend relevant trending content.
"""

    async def _make_api_request(self, prompt: str) -> str:
        """Make API request to Perplexity with retry logic"""
        max_retries = 3

        for attempt in range(max_retries):
            try:
                payload = {
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert social media analyst specializing in TikTok content categorization and niche identification. Provide precise, actionable analysis based on user data."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                    "stream": False
                }

                logger.debug(
                    f"Making Perplexity API request (attempt {attempt + 1})")

                response = await self.client.post(
                    self.base_url,
                    json=payload
                )

                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    logger.debug("✅ Perplexity API request successful")
                    return content
                else:
                    logger.warning(
                        f"⚠️ Perplexity API returned status {response.status_code}: {response.text}")
                    if attempt == max_retries - 1:
                        raise Exception(
                            f"Perplexity API error: {response.status_code}")

            except Exception as e:
                logger.warning(
                    f"⚠️ Perplexity API attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise

                # Exponential backoff
                await asyncio.sleep(2 ** attempt)

        raise Exception("Perplexity API requests exhausted")

    def _parse_niche_response(self, response: str) -> NicheAnalysis:
        """Parse Perplexity response into structured NicheAnalysis"""
        try:
            # Extract information using simple parsing
            lines = response.strip().split('\n')

            # Initialize default values
            niche_category = "General Content Creator"
            niche_description = "Content creator with diverse topics"
            confidence_score = 0.5
            key_topics = ["entertainment", "lifestyle"]
            target_audience = "General audience"
            content_style = "Mixed content"

            # Parse each line looking for our structured data
            for line in lines:
                line = line.strip()
                if line.startswith('Niche Category:'):
                    niche_category = line.replace(
                        'Niche Category:', '').strip()
                elif line.startswith('Niche Description:'):
                    niche_description = line.replace(
                        'Niche Description:', '').strip()
                elif line.startswith('Confidence Score:'):
                    try:
                        score_text = line.replace(
                            'Confidence Score:', '').strip()
                        confidence_score = float(score_text)
                    except:
                        confidence_score = 0.7
                elif line.startswith('Key Topics:'):
                    topics_text = line.replace('Key Topics:', '').strip()
                    # Parse list format [item1, item2, item3] or comma-separated
                    if '[' in topics_text and ']' in topics_text:
                        topics_text = topics_text.strip('[]')
                    key_topics = [t.strip().strip('"\'')
                                  for t in topics_text.split(',')]
                elif line.startswith('Target Audience:'):
                    target_audience = line.replace(
                        'Target Audience:', '').strip()
                elif line.startswith('Content Style:'):
                    content_style = line.replace('Content Style:', '').strip()

            # Clean up extracted data
            niche_category = niche_category.strip('"\'')
            niche_description = niche_description.strip('"\'')
            target_audience = target_audience.strip('"\'')
            content_style = content_style.strip('"\'')

            return NicheAnalysis(
                niche_category=niche_category,
                niche_description=niche_description,
                confidence_score=max(0.0, min(1.0, confidence_score)),
                key_topics=key_topics[:5],  # Limit to 5 topics
                target_audience=target_audience,
                content_style=content_style
            )

        except Exception as e:
            logger.warning(f"⚠️ Failed to parse Perplexity response: {e}")
            # Return basic analysis from response text
            return self._create_basic_analysis_from_text(response)

    def _create_basic_analysis_from_text(self, text: str) -> NicheAnalysis:
        """Create basic analysis when parsing fails"""
        # Extract key information from free text
        text_lower = text.lower()

        # Determine category based on keywords
        if any(word in text_lower for word in ['tech', 'technology', 'gadget', 'review']):
            category = "Technology & Reviews"
        elif any(word in text_lower for word in ['fitness', 'workout', 'health', 'gym']):
            category = "Fitness & Health"
        elif any(word in text_lower for word in ['food', 'recipe', 'cooking', 'chef']):
            category = "Food & Cooking"
        elif any(word in text_lower for word in ['fashion', 'style', 'outfit', 'clothing']):
            category = "Fashion & Style"
        elif any(word in text_lower for word in ['comedy', 'funny', 'humor', 'entertainment']):
            category = "Comedy & Entertainment"
        elif any(word in text_lower for word in ['education', 'tutorial', 'learning', 'teach']):
            category = "Education & Tutorials"
        elif any(word in text_lower for word in ['music', 'song', 'dance', 'performance']):
            category = "Music & Performance"
        else:
            category = "Lifestyle & General Content"

        return NicheAnalysis(
            niche_category=category,
            niche_description=f"Content creator in {category.lower()} with engaging content for their audience.",
            confidence_score=0.6,
            key_topics=["entertainment", "lifestyle", "social media"],
            target_audience="General TikTok audience",
            content_style="Engaging social media content"
        )

    def _create_fallback_analysis(self, username: str, bio: str) -> NicheAnalysis:
        """Create fallback analysis when API fails"""
        logger.info(f"📝 Creating fallback niche analysis for @{username}")

        # Analyze bio for basic categorization
        bio_lower = (bio or "").lower()

        if any(word in bio_lower for word in ['tech', 'developer', 'programming', 'software']):
            category = "Technology & Tech"
        elif any(word in bio_lower for word in ['fitness', 'trainer', 'health', 'workout']):
            category = "Fitness & Health"
        elif any(word in bio_lower for word in ['food', 'chef', 'cooking', 'recipe']):
            category = "Food & Cooking"
        elif any(word in bio_lower for word in ['fashion', 'style', 'model', 'designer']):
            category = "Fashion & Style"
        elif any(word in bio_lower for word in ['music', 'artist', 'singer', 'musician']):
            category = "Music & Arts"
        elif any(word in bio_lower for word in ['business', 'entrepreneur', 'marketing']):
            category = "Business & Entrepreneurship"
        else:
            category = "Lifestyle & Entertainment"

        return NicheAnalysis(
            niche_category=category,
            niche_description=f"TikTok creator focused on {category.lower()} content with authentic engagement.",
            confidence_score=0.4,  # Lower confidence for fallback
            key_topics=["social media", "content creation", "engagement"],
            target_audience="TikTok community",
            content_style="Social media content"
        )

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    async def health_check(self) -> bool:
        """Check if Perplexity service is available"""
        try:
            # Simple test request
            test_prompt = "What is TikTok?"
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": test_prompt}],
                "max_tokens": 10
            }

            response = await self.client.post(self.base_url, json=payload)
            return response.status_code == 200

        except Exception as e:
            logger.warning(f"⚠️ Perplexity health check failed: {e}")
            return False


# Global Perplexity service instance
perplexity_service = PerplexityService()
