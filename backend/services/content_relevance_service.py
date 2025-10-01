"""
Content Relevance Service using GPT-4 Vision
Analyzes images from trending posts to determine relevance to user's niche
"""
import asyncio
import logging
import base64
from io import BytesIO
from typing import List, Optional, Dict, Any
import httpx
from PIL import Image
from openai import AsyncOpenAI
from pydantic import BaseModel

from config import settings
from models import ContentRelevanceAnalysis, TrendVideo
from services.cache_service import cache_service

logger = logging.getLogger(__name__)


class ContentRelevanceService:
    """Service for analyzing content relevance using GPT-4 Vision"""

    def __init__(self):
        """Initialize the content relevance service"""
        self.openai_client = None
        self.initialized = False
        self.vision_model = settings.openai_vision_model
        self.temperature = settings.openai_vision_temperature
        self.max_tokens = settings.openai_vision_max_tokens
        self.max_images = settings.max_images_for_analysis

        # HTTP client for downloading images
        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            limits=httpx.Limits(max_connections=10)
        )

        try:
            if settings.openai_api_key and len(settings.openai_api_key) > 20:
                self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
                self.initialized = True
                logger.info("✅ Content Relevance Service initialized with GPT-4 Vision")
            else:
                logger.warning("⚠️ OpenAI API key not configured - content relevance disabled")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Content Relevance Service: {e}")
            self.initialized = False

    async def analyze_trends_relevance(
        self,
        trends: List[TrendVideo],
        user_niche_category: str,
        user_niche_description: str,
        user_key_topics: List[str]
    ) -> List[TrendVideo]:
        """
        Analyze relevance of trending videos to user's niche

        Args:
            trends: List of trending videos
            user_niche_category: User's niche category from Perplexity
            user_niche_description: User's niche description
            user_key_topics: User's key topics/interests

        Returns:
            List of trending videos with relevance analysis
        """
        logger.info(f"🎯 Analyzing content relevance for {len(trends)} trends")

        # Limit number of trends to analyze (cost control)
        trends_to_analyze = trends[:self.max_images]

        # Create analysis tasks for parallel processing
        analysis_tasks = []
        for trend in trends_to_analyze:
            if trend.cover_image_url:
                task = self._analyze_single_trend_relevance(
                    trend, user_niche_category, user_niche_description, user_key_topics
                )
                analysis_tasks.append(task)
            else:
                # No image available, use fallback text analysis
                trend.relevance_score = await self._analyze_text_relevance(
                    trend, user_niche_category, user_key_topics
                )

        # Execute all analysis tasks in parallel
        if analysis_tasks:
            try:
                await asyncio.gather(*analysis_tasks, return_exceptions=True)
            except Exception as e:
                logger.error(f"❌ Batch relevance analysis failed: {e}")

        # Sort trends by relevance score (highest first)
        analyzed_trends = sorted(
            trends_to_analyze,
            key=lambda t: t.relevance_score,
            reverse=True
        )

        # Add remaining trends without analysis
        if len(trends) > self.max_images:
            remaining_trends = trends[self.max_images:]
            for trend in remaining_trends:
                trend.relevance_score = 0.3  # Default moderate relevance
            analyzed_trends.extend(remaining_trends)

        logger.info(
            f"✅ Relevance analysis completed. Top score: {analyzed_trends[0].relevance_score:.2f}")
        return analyzed_trends

    async def _analyze_single_trend_relevance(
        self,
        trend: TrendVideo,
        user_niche_category: str,
        user_niche_description: str,
        user_key_topics: List[str]
    ) -> None:
        """Analyze relevance of a single trend (modifies trend in-place)"""
        try:
            # Check cache first
            cache_key = f"relevance:{trend.id}:{user_niche_category}"
            cached_analysis = await cache_service.get("relevance", cache_key)

            if cached_analysis:
                logger.debug(
                    f"📋 Using cached relevance analysis for trend {trend.id}")
                trend.content_relevance = ContentRelevanceAnalysis(
                    **cached_analysis)
                trend.relevance_score = trend.content_relevance.relevance_score
                return

            # Download and analyze image
            image_data = await self._download_image(trend.cover_image_url)
            if not image_data:
                # Fallback to text analysis
                trend.relevance_score = await self._analyze_text_relevance(
                    trend, user_niche_category, user_key_topics
                )
                return

            # Analyze with GPT-4 Vision
            analysis = await self._analyze_image_with_vision(
                image_data, trend, user_niche_category, user_niche_description, user_key_topics
            )

            if analysis:
                trend.content_relevance = analysis
                trend.relevance_score = analysis.relevance_score

                # Cache the result
                await cache_service.set(
                    "relevance", cache_key, analysis.model_dump(), ttl=3600  # 1 hour cache
                )
            else:
                # Fallback to text analysis
                trend.relevance_score = await self._analyze_text_relevance(
                    trend, user_niche_category, user_key_topics
                )

        except Exception as e:
            logger.warning(
                f"⚠️ Failed to analyze relevance for trend {trend.id}: {e}")
            # Fallback to text analysis
            trend.relevance_score = await self._analyze_text_relevance(
                trend, user_niche_category, user_key_topics
            )

    async def _download_image(self, image_url: str) -> Optional[bytes]:
        """Download image from URL"""
        try:
            logger.debug(f"📥 Downloading image: {image_url}")

            response = await self.http_client.get(image_url)
            if response.status_code == 200:
                # Verify it's an image and resize if needed
                image_data = response.content

                # Basic image validation and optimization
                try:
                    with Image.open(BytesIO(image_data)) as img:
                        # Convert to RGB if needed
                        if img.mode != 'RGB':
                            img = img.convert('RGB')

                        # Resize if too large (GPT-4V has size limits)
                        max_size = 1024
                        if img.width > max_size or img.height > max_size:
                            img.thumbnail((max_size, max_size),
                                          Image.Resampling.LANCZOS)

                            # Save optimized image
                            buffer = BytesIO()
                            img.save(buffer, format='JPEG',
                                     quality=85, optimize=True)
                            image_data = buffer.getvalue()

                except Exception as img_error:
                    logger.warning(f"⚠️ Image processing failed: {img_error}")
                    return None

                return image_data
            else:
                logger.warning(
                    f"⚠️ Failed to download image: {response.status_code}")
                return None

        except Exception as e:
            logger.warning(f"⚠️ Image download error: {e}")
            return None

    async def _analyze_image_with_vision(
        self,
        image_data: bytes,
        trend: TrendVideo,
        user_niche_category: str,
        user_niche_description: str,
        user_key_topics: List[str]
    ) -> Optional[ContentRelevanceAnalysis]:
        """Analyze image content relevance using GPT-4 Vision"""
        try:
            # Encode image to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')

            # Create analysis prompt
            prompt = self._create_vision_prompt(
                trend, user_niche_category, user_niche_description, user_key_topics
            )

            logger.debug(
                f"🔍 Analyzing image with GPT-4 Vision for trend {trend.id}")

            # Make API request to GPT-4 Vision
            response = await self.openai_client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}",
                                    "detail": "low"  # Use low detail to reduce costs
                                }
                            }
                        ]
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            # Parse response
            analysis_text = response.choices[0].message.content
            return self._parse_vision_response(analysis_text)

        except Exception as e:
            logger.error(f"❌ GPT-4 Vision analysis failed: {e}")
            return None

    def _create_vision_prompt(
        self,
        trend: TrendVideo,
        user_niche_category: str,
        user_niche_description: str,
        user_key_topics: List[str]
    ) -> str:
        """Create enhanced prompt for GPT-4 Vision analysis with better calibration"""

        topics_str = ", ".join(user_key_topics[:6])  # Increased to 6 topics
        engagement_rate = (trend.likes + trend.comments +
                           trend.shares) / max(trend.views, 1)

        # Create niche-specific calibration examples
        calibration_examples = self._get_niche_calibration_examples(
            user_niche_category)

        return f"""You are an expert TikTok trend analyst. Analyze this image for content relevance to a specific creator's niche with high precision.

TARGET CREATOR PROFILE:
- Primary Niche: {user_niche_category}
- Content Focus: {user_niche_description}
- Core Topics: {topics_str}
- Looking for: Content that matches their brand and audience

TREND POST PERFORMANCE:
- Caption: {trend.caption[:180]}
- Engagement Rate: {engagement_rate:.2%}
- Viral Metrics: {trend.views:,} views, {trend.likes:,} likes
- Context Hashtag: #{trend.hashtag}

DETAILED ANALYSIS FRAMEWORK:

1. VISUAL CONTENT AUDIT:
   - Main subjects: What/who is the primary focus?
   - Setting & environment: Where is this taking place?
   - Color palette & aesthetic: What's the visual style?
   - Activities & actions: What is happening in the scene?
   - Production quality: Professional vs casual content?

2. NICHE ALIGNMENT ASSESSMENT:
   - Direct match: Does this directly fit the creator's niche?
   - Thematic connection: Are there related themes or concepts?
   - Aesthetic consistency: Does the visual style align with their brand?
   - Audience crossover: Would this appeal to the same target audience?
   - Content format: Could the creator realistically create similar content?

3. TREND REPLICABILITY:
   - Format potential: Is this a trending format they could use?
   - Resource requirements: What would they need to recreate this?
   - Adaptation possibilities: How could they make this fit their niche?

4. PRECISION SCORING GUIDELINES:
   - 0.90-1.00: Perfect direct match - could be from their profile
   - 0.75-0.89: Very high relevance - strong thematic alignment
   - 0.60-0.74: Good relevance - clear connections to their niche
   - 0.45-0.59: Moderate relevance - some overlapping elements
   - 0.30-0.44: Low relevance - minimal connections
   - 0.00-0.29: Poor relevance - different niche entirely

{calibration_examples}

REQUIRED OUTPUT FORMAT (be precise with decimals):
```
Image Description: [Comprehensive 2-3 sentence description of visual content]
Content Category: [Specific primary category - be precise]
Visual Elements: [List 4-6 key elements: objects, people, setting, style, colors, mood]
Style Description: [Aesthetic style in 10-12 words]
Niche Alignment: [How does this connect to {user_niche_category}? Be specific]
Relevance Score: [X.XX] (Use 2 decimals, follow scoring guidelines precisely)
Relevance Explanation: [2-3 sentences: Why this score? What makes it relevant/irrelevant?]
Confidence Level: [0.XX] (How certain are you? Consider image clarity, niche specificity)
```

Be critical but fair. Score conservatively - only 0.70+ should indicate strong relevance."""

    def _get_niche_calibration_examples(self, niche_category: str) -> str:
        """Generate niche-specific scoring calibration examples"""
        niche_lower = niche_category.lower()

        if any(word in niche_lower for word in ['fashion', 'style', 'outfit', 'clothing']):
            return """
FASHION NICHE SCORING EXAMPLES:
- Fashion outfit showcase/styling: 0.85-0.95
- Beauty tutorial with fashion elements: 0.70-0.85
- Lifestyle content in stylish settings: 0.50-0.70
- Fashion accessories (jewelry, bags, shoes): 0.65-0.80
- Shopping hauls or fashion reviews: 0.75-0.90
- Completely unrelated content (cooking, tech): 0.10-0.30"""

        elif any(word in niche_lower for word in ['food', 'cooking', 'recipe', 'culinary']):
            return """
FOOD/COOKING NICHE SCORING EXAMPLES:
- Recipe tutorials and cooking videos: 0.85-0.95
- Food reviews and tastings: 0.75-0.90
- Restaurant visits and food exploration: 0.70-0.85
- Kitchen tools and cooking equipment: 0.60-0.75
- Food presentation and plating: 0.75-0.85
- Non-food content (fashion, tech): 0.10-0.30"""

        elif any(word in niche_lower for word in ['fitness', 'workout', 'health', 'gym']):
            return """
FITNESS/HEALTH NICHE SCORING EXAMPLES:
- Workout routines and exercise demos: 0.85-0.95
- Fitness motivation and transformation: 0.80-0.90
- Healthy eating and nutrition tips: 0.70-0.85
- Sports activities and athletic performance: 0.65-0.80
- Wellness and self-care content: 0.60-0.75
- Unrelated content (fashion, gaming): 0.10-0.30"""

        elif any(word in niche_lower for word in ['tech', 'technology', 'gadget', 'software']):
            return """
TECH NICHE SCORING EXAMPLES:
- Tech reviews and gadget demonstrations: 0.85-0.95
- Software tutorials and tips: 0.75-0.90
- Gaming content and reviews: 0.70-0.85
- Tech news and industry updates: 0.75-0.85
- DIY tech projects and modifications: 0.80-0.90
- Non-tech content (fashion, food): 0.10-0.30"""

        elif any(word in niche_lower for word in ['beauty', 'makeup', 'skincare', 'cosmetic']):
            return """
BEAUTY NICHE SCORING EXAMPLES:
- Makeup tutorials and transformations: 0.85-0.95
- Skincare routines and product reviews: 0.80-0.95
- Beauty tips and hacks: 0.75-0.90
- Fashion content with beauty elements: 0.60-0.75
- Self-care and wellness with beauty focus: 0.65-0.80
- Unrelated content (tech, sports): 0.10-0.30"""

        elif any(word in niche_lower for word in ['travel', 'adventure', 'explore', 'destination']):
            return """
TRAVEL NICHE SCORING EXAMPLES:
- Travel vlogs and destination showcases: 0.85-0.95
- Adventure activities and outdoor experiences: 0.80-0.90
- Cultural experiences and local exploration: 0.75-0.90
- Travel tips and budget advice: 0.75-0.85
- Food experiences while traveling: 0.65-0.80
- Home-based content (cooking, tech): 0.10-0.30"""

        else:
            return f"""
{niche_category.upper()} NICHE SCORING GUIDELINES:
- Direct niche match with clear thematic alignment: 0.75-0.95
- Related content with some niche overlap: 0.50-0.75
- Tangentially related or inspirational content: 0.35-0.55
- Minimal connection to the niche: 0.20-0.40
- Completely different niche/topic: 0.00-0.25"""

    def _parse_vision_response(self, response_text: str) -> Optional[ContentRelevanceAnalysis]:
        """Parse GPT-4 Vision response into structured analysis"""
        try:
            # Extract information using simple parsing
            lines = response_text.strip().split('\n')

            # Initialize default values
            image_description = "Visual content analysis"
            content_category = "General"
            relevance_score = 0.5
            relevance_explanation = "Moderate relevance to user niche"
            confidence_level = 0.7
            visual_elements = []

            # Parse each line
            for line in lines:
                line = line.strip()
                if line.startswith('Image Description:'):
                    image_description = line.replace(
                        'Image Description:', '').strip()
                elif line.startswith('Content Category:'):
                    content_category = line.replace(
                        'Content Category:', '').strip()
                elif line.startswith('Visual Elements:'):
                    elements_text = line.replace(
                        'Visual Elements:', '').strip()
                    visual_elements = [e.strip()
                                       for e in elements_text.split(',')]
                elif line.startswith('Relevance Score:'):
                    try:
                        score_text = line.replace(
                            'Relevance Score:', '').strip()
                        relevance_score = float(score_text)
                        relevance_score = max(
                            0.0, min(1.0, relevance_score))  # Clamp to 0-1
                    except:
                        relevance_score = 0.5
                elif line.startswith('Relevance Explanation:'):
                    relevance_explanation = line.replace(
                        'Relevance Explanation:', '').strip()
                elif line.startswith('Confidence Level:'):
                    try:
                        confidence_text = line.replace(
                            'Confidence Level:', '').strip()
                        confidence_level = float(confidence_text)
                        confidence_level = max(
                            0.0, min(1.0, confidence_level))  # Clamp to 0-1
                    except:
                        confidence_level = 0.7

            return ContentRelevanceAnalysis(
                image_description=image_description,
                content_category=content_category,
                relevance_score=relevance_score,
                relevance_explanation=relevance_explanation,
                confidence_level=confidence_level,
                visual_elements=visual_elements[:5]  # Limit to 5 elements
            )

        except Exception as e:
            logger.warning(f"⚠️ Failed to parse vision response: {e}")
            return None

    async def _analyze_text_relevance(
        self,
        trend: TrendVideo,
        user_niche_category: str,
        user_key_topics: List[str]
    ) -> float:
        """Enhanced weighted text-based relevance analysis with multiple factors"""
        try:
            relevance_score = 0.0

            # Prepare text for analysis
            text_content = f"{trend.caption} #{trend.hashtag}".lower()
            niche_words = user_niche_category.lower().split()

            # 1. EXACT NICHE MATCHING (Weight: 40% - highest priority)
            exact_niche_matches = sum(1 for word in niche_words if len(
                word) > 2 and word in text_content)
            if exact_niche_matches > 0:
                # Scale: 1 match = 0.2, 2+ matches = 0.4 (max)
                relevance_score += min(0.4, exact_niche_matches * 0.2)
                logger.debug(
                    f"🎯 Niche matches: {exact_niche_matches} -> +{min(0.4, exact_niche_matches * 0.2):.2f}")

            # 2. KEY TOPICS MATCHING (Weight: 30% - second priority)
            topic_matches = 0
            for topic in user_key_topics[:8]:  # Increased from 5 to 8
                if len(topic) > 2 and topic.lower() in text_content:
                    topic_matches += 1

            if topic_matches > 0:
                # Scale: 1 topic = 0.1, 3+ topics = 0.3 (max)
                topic_score = min(0.3, topic_matches * 0.1)
                relevance_score += topic_score
                logger.debug(
                    f"🔑 Topic matches: {topic_matches} -> +{topic_score:.2f}")

            # 3. ENGAGEMENT QUALITY FACTOR (Weight: 15%)
            engagement_rate = (trend.likes + trend.comments +
                               trend.shares) / max(trend.views, 1)
            if engagement_rate >= 0.08:      # 8%+ excellent
                relevance_score += 0.15
                logger.debug(
                    f"🚀 Excellent engagement ({engagement_rate:.1%}) -> +0.15")
            elif engagement_rate >= 0.05:    # 5%+ very good
                relevance_score += 0.12
                logger.debug(
                    f"⭐ High engagement ({engagement_rate:.1%}) -> +0.12")
            elif engagement_rate >= 0.03:    # 3%+ good
                relevance_score += 0.08
                logger.debug(
                    f"👍 Good engagement ({engagement_rate:.1%}) -> +0.08")
            elif engagement_rate >= 0.02:    # 2%+ decent
                relevance_score += 0.05
                logger.debug(
                    f"✅ Decent engagement ({engagement_rate:.1%}) -> +0.05")

            # 4. FRESHNESS/TEMPORAL RELEVANCE (Weight: 10%)
            days_old = self._calculate_content_age(trend.create_time)
            if days_old <= 3:        # Very fresh (0-3 days)
                relevance_score += 0.1
                logger.debug(f"🌟 Very fresh ({days_old}d) -> +0.1")
            elif days_old <= 7:      # Fresh (4-7 days)
                relevance_score += 0.07
                logger.debug(f"🆕 Fresh ({days_old}d) -> +0.07")
            elif days_old <= 14:     # Recent (8-14 days)
                relevance_score += 0.04
                logger.debug(f"📅 Recent ({days_old}d) -> +0.04")

            # 5. VIRAL POTENTIAL BONUS (Weight: 5%)
            if trend.views > 2000000:        # 2M+ mega viral
                relevance_score += 0.05
                logger.debug(f"💥 Mega viral (2M+ views) -> +0.05")
            elif trend.views > 1000000:      # 1M+ viral
                relevance_score += 0.04
                logger.debug(f"🔥 Viral (1M+ views) -> +0.04")
            elif trend.views > 500000:       # 500K+ popular
                relevance_score += 0.02
                logger.debug(f"📈 Popular (500K+ views) -> +0.02")

            # Final score normalization and quality bonus
            relevance_score = min(1.0, relevance_score)

            # Quality bonus for high-performing content
            if trend.likes > 50000 and engagement_rate > 0.04:
                relevance_score = min(1.0, relevance_score + 0.05)
            logger.debug(
                "🏆 Quality bonus for high-performing content -> +0.05")

            logger.info(
                f"📝 Enhanced text relevance for trend {trend.id}: {relevance_score:.3f} "
                f"(niche: {exact_niche_matches}, topics: {topic_matches}, "
                f"engagement: {engagement_rate:.1%}, age: {days_old}d)"
            )
            return relevance_score

        except Exception as e:
            logger.warning(f"⚠️ Text relevance analysis failed: {e}")
            return 0.3  # Default moderate relevance

    def _calculate_content_age(self, create_time: int) -> int:
        """Calculate days since content creation"""
        try:
            from datetime import datetime
            current_timestamp = datetime.now().timestamp()
            days_diff = (current_timestamp - create_time) / (24 * 60 * 60)
            return max(0, int(days_diff))  # Ensure non-negative
        except Exception:
            # If timestamp parsing fails, assume recent content
            return 1

    async def close(self):
        """Close HTTP client"""
        await self.http_client.aclose()


# Global content relevance service instance
content_relevance_service = ContentRelevanceService()
