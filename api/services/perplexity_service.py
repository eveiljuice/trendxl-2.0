"""
Perplexity API Service for Niche Analysis
Uses Sonar model to analyze TikTok profiles and determine user niches
"""
import logging
import asyncio
import json
from typing import Dict, Any, Optional, List
import httpx
from pydantic import BaseModel
from config import settings
from .creative_center_mapping import creative_center_mapping

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
        self.initialized = False

        # HTTP client with timeout and retry configuration
        try:
            if self.api_key and len(self.api_key) > 20:
                self.client = httpx.AsyncClient(
                    timeout=httpx.Timeout(60.0),
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }
                )
                self.initialized = True
                logger.info("✅ Perplexity service initialized with Sonar model")
            else:
                self.client = None
                logger.warning("⚠️ Perplexity API key not configured - service disabled")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Perplexity client: {e}")
            self.client = None
            self.initialized = False

    async def analyze_user_niche(
        self,
        username: str,
        bio: str,
        recent_posts_content: list[str],
        follower_count: int = 0,
        video_count: int = 0
    ) -> tuple[NicheAnalysis, Dict[str, int]]:
        """
        Analyze user niche based on profile and content data

        Args:
            username: TikTok username
            bio: User bio/description
            recent_posts_content: List of recent post captions/descriptions
            follower_count: Number of followers
            video_count: Number of videos posted

        Returns:
            Tuple of (NicheAnalysis with detailed niche information, token_usage dict)
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
            response, token_usage = await self._make_api_request(prompt)

            # Parse the response into structured niche analysis
            niche_analysis = self._parse_niche_response(response)

            logger.info(
                f"✅ Niche analysis completed for @{username}: {niche_analysis.niche_category}")
            return niche_analysis, token_usage

        except Exception as e:
            logger.error(f"❌ Niche analysis failed for @{username}: {e}")
            # Return fallback analysis with zero tokens
            return self._create_fallback_analysis(username, bio), {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

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

    async def _make_api_request(self, prompt: str) -> tuple[str, Dict[str, int]]:
        """Make API request to Perplexity with retry logic and return token usage"""
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

                    # Extract token usage from response
                    usage = result.get("usage", {})
                    token_usage = {
                        "prompt_tokens": usage.get("prompt_tokens", 0),
                        "completion_tokens": usage.get("completion_tokens", 0),
                        "total_tokens": usage.get("total_tokens", 0)
                    }

                    logger.info(
                        f"💰 Perplexity tokens used: {token_usage['total_tokens']} (prompt: {token_usage['prompt_tokens']}, completion: {token_usage['completion_tokens']})")
                    logger.debug("✅ Perplexity API request successful")
                    return content, token_usage
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
        if self.client and not self.client.is_closed:
            try:
                await self.client.aclose()
            except Exception as e:
                logger.warning(f"⚠️ Failed to close Perplexity client: {e}")

    async def analyze_tiktok_account_origin(
        self,
        username: str,
        bio: str,
        recent_posts_content: list[str],
        follower_count: int = 0,
        video_count: int = 0
    ) -> tuple[Dict[str, str], Dict[str, int]]:
        """
        Analyze TikTok account to determine its country/region of origin

        Args:
            username: TikTok username
            bio: User bio/description  
            recent_posts_content: List of recent post captions
            follower_count: Number of followers
            video_count: Number of videos posted

        Returns:
            Tuple of (Dict with country, country_code, and language, token_usage dict)
        """
        logger.info(f"🌍 Analyzing TikTok account origin for @{username}")

        try:
            # Prepare context for analysis
            posts_text = "\n".join(recent_posts_content[:10])

            prompt = f"""Analyze this TikTok account to determine its country/region of origin based on language, content style, cultural references, and other indicators:

**Account Information:**
- Username: @{username}
- Bio: {bio or "No bio provided"}
- Followers: {follower_count:,}
- Total Videos: {video_count}

**Recent Content (Post Captions):**
{posts_text or "No recent posts available"}

**Analysis Task:**
Determine the most likely country/region this TikTok account is from based on:

1. **Language**: What language(s) are used in bio and posts?
2. **Cultural References**: Any local slang, cultural references, or regional topics?
3. **Content Style**: Does the content style match specific regional TikTok trends?
4. **Time/Location Indicators**: Any mentions of cities, events, or regional specifics?

**Required Output Format:**
Country: [Full country name, e.g., "United States", "United Kingdom", "Brazil"]
Country_Code: [2-letter ISO code, e.g., "US", "GB", "BR"]
Language: [Primary language code, e.g., "en", "pt", "es"]
Confidence: [High/Medium/Low - how confident you are in this assessment]

Be specific and provide your best assessment even with limited information."""

            response, token_usage = await self._make_api_request(prompt)
            result = self._parse_account_origin_response(response)
            return result, token_usage

        except Exception as e:
            logger.error(
                f"❌ Account origin analysis failed for @{username}: {e}")
            return {
                "country": "United States",
                "country_code": "US",
                "language": "en",
                "confidence": "Low"
            }, {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    def _parse_account_origin_response(self, response: str) -> Dict[str, str]:
        """Parse account origin analysis response"""
        try:
            lines = response.strip().split('\n')

            result = {
                "country": "United States",
                "country_code": "US",
                "language": "en",
                "confidence": "Low"
            }

            for line in lines:
                line = line.strip()
                if line.startswith('Country:'):
                    result["country"] = line.replace(
                        'Country:', '').strip().strip('"\'')
                elif line.startswith('Country_Code:'):
                    result["country_code"] = line.replace(
                        'Country_Code:', '').strip().strip('"\'').upper()
                elif line.startswith('Language:'):
                    result["language"] = line.replace(
                        'Language:', '').strip().strip('"\'').lower()
                elif line.startswith('Confidence:'):
                    result["confidence"] = line.replace(
                        'Confidence:', '').strip().strip('"\'')

            logger.info(
                f"✅ Account origin detected: {result['country']} ({result['country_code']}) - {result['confidence']} confidence")
            return result

        except Exception as e:
            logger.warning(f"⚠️ Failed to parse account origin response: {e}")
            return {
                "country": "United States",
                "country_code": "US",
                "language": "en",
                "confidence": "Low"
            }

    async def discover_creative_center_hashtags(
        self,
        niche: str,
        country: str = "US",
        language: str = "en",
        limit: int = 10,
        account_origin: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Use Perplexity Sonar (web-enabled) to find popular Creative Center hashtags
        for a given niche and region, returning structured results.

        Args:
            niche: User content niche (e.g., "Tech Reviews", "Fashion")
            country: Country code for regional trends
            language: Language code for content language
            limit: Maximum number of hashtags to return

        Returns:
            List of CreativeCenterHashtag data as dictionaries
        """
        # Use account origin if provided, otherwise use defaults
        if account_origin:
            actual_country = account_origin.get("country", country)
            actual_country_code = account_origin.get("country_code", country)
            actual_language = account_origin.get("language", language)
            confidence = account_origin.get("confidence", "Unknown")
            logger.info(
                f"🔍 Using detected account origin: {actual_country} ({confidence} confidence)")
        else:
            actual_country = country
            actual_country_code = country
            actual_language = language
            logger.info(f"🔍 Using default location: {country}")

        logger.info(
            f"🔍 Discovering Creative Center hashtags for niche: {niche} (Target: {actual_country}, Language: {actual_language})")

        try:
            # Creative Center URL pattern with regional focus
            base_url = f"https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/{actual_language}"
            region_hint = f"Focus specifically on {actual_country} ({actual_country_code}) region, Language: {actual_language}"

            # Structured JSON output format
            json_format = """{
  "hashtags": [
    {
      "name": "hashtag-without-#",
      "url": "https://ads.tiktok.com/business/creativecenter/...",
      "volume": 123456,
      "growth": 0.37,
      "score": 82.5
    }
  ]
}"""

            prompt = f"""You are a research agent specializing in TikTok trends. Browse TikTok Creative Center to find the most popular and trending hashtags for the niche: "{niche}".

{region_hint}
Start your research at: {base_url}

CRITICAL REQUIREMENTS:
- Find hashtags specifically relevant to "{niche}" that are popular in {actual_country}
- Look for regional variants and local trending topics for {actual_country} TikTok community
- Prioritize hashtags with high engagement and growth potential in the {actual_country} market
- Include niche-specific hashtags, trending variations, and culturally relevant topics for {actual_country}
- COMPLETELY AVOID generic hashtags like #fyp, #viral, #trending - focus on niche-specific content
- Look for recent trending data (last 7 days preferred, maximum 30 days)
- Consider local culture, language variants ({actual_language}), and regional interests specific to {actual_country}
- Focus on hashtags that would be used by content creators FROM {actual_country} in this niche

For each hashtag, gather:
- name: hashtag without the # symbol
- url: direct Creative Center URL for this hashtag
- volume: search/usage volume if available
- growth: growth percentage or trend indicator
- score: overall performance score if provided

Return EXACTLY this JSON format with no additional text:
{json_format}

Limit to top {limit} most relevant hashtags sorted by relevance and performance."""

            # Make API request to Perplexity
            response_text, token_usage = await self._make_api_request(prompt)

            # Try to extract and parse JSON from the response
            try:
                # Look for JSON in the response
                text = response_text.strip()

                # Try to find JSON boundaries
                start_idx = text.find('{')
                end_idx = text.rfind('}')

                if start_idx != -1 and end_idx != -1:
                    json_text = text[start_idx:end_idx + 1]
                    data = json.loads(json_text)

                    # Extract hashtags array
                    hashtags_data = data.get('hashtags', [])

                    # Validate and clean the data
                    results = []
                    for item in hashtags_data[:limit]:
                        try:
                            name = str(item.get("name", "")
                                       ).lstrip("#").strip()
                            url = str(item.get("url", "")).strip()
                            volume = item.get("volume", None)
                            growth = item.get("growth", None)
                            score = item.get("score", None)

                            # Basic validation
                            if name and url and "ads.tiktok.com" in url:
                                hashtag_data = {
                                    "name": name,
                                    "url": url,
                                    "volume": volume,
                                    "growth": growth,
                                    "score": score
                                }
                                results.append(hashtag_data)

                        except Exception as e:
                            logger.warning(
                                f"⚠️ Failed to parse hashtag item: {e}")
                            continue

                    logger.info(
                        f"✅ Found {len(results)} Creative Center hashtags for niche: {niche}")
                    return results

                else:
                    logger.warning(
                        "⚠️ No valid JSON found in Perplexity response")

            except json.JSONDecodeError as e:
                logger.warning(
                    f"⚠️ Failed to parse JSON from Perplexity response: {e}")

        except Exception as e:
            logger.error(
                f"❌ Creative Center hashtag discovery failed for niche '{niche}': {e}")

        # Return empty list if everything failed
        logger.info(f"📝 Returning empty hashtag list for niche: {niche}")
        return []

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
