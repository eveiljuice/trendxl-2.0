"""
Advanced Creative Center Discovery Service
Реализует сложную архитектуру AI-агента для пошагового поиска хештегов
"""
import logging
import asyncio
import json
from typing import Dict, Any, Optional, List
import httpx
from config import settings
from .creative_center_mapping import creative_center_mapping

logger = logging.getLogger(__name__)


class AdvancedCreativeCenterService:
    """
    Продвинутый сервис для поиска хештегов в Creative Center
    с пошаговой навигацией и интеллектуальной фильтрацией
    """

    def __init__(self):
        """Initialize service with Perplexity API configuration"""
        self.api_key = settings.perplexity_api_key
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.model = settings.perplexity_model
        self.temperature = settings.perplexity_temperature
        self.max_tokens = 800  # Increased for detailed responses

        # HTTP client with timeout and retry configuration
        self.client = httpx.AsyncClient(
            # Increased timeout for complex operations
            timeout=httpx.Timeout(120.0),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        )

        logger.info("✅ Advanced Creative Center service initialized")

    async def discover_hashtags_with_navigation(
        self,
        niche: str,
        country: str = "US",
        language: str = "en",
        limit: int = 10,
        auto_detect_geo: bool = False,
        profile_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Главный метод для поиска хештегов с пошаговой навигацией

        Архитектура:
        1. Определение географии пользователя
        2. Маппинг ниши к категории Creative Center
        3. Пошаговая навигация по Creative Center
        4. Анализ ~50 хештегов в категории
        5. Интеллектуальная фильтрация до топ-N хештегов

        Args:
            niche: Ниша пользователя (e.g., "Tech Reviews")
            country: Код страны для региональных трендов
            language: Языковой код
            limit: Максимальное количество хештегов для возврата
            auto_detect_geo: Автоматическое определение географии
            profile_data: Данные профиля для определения географии

        Returns:
            Словарь с результатами поиска и метаданными
        """
        logger.info(
            f"🚀 Starting advanced Creative Center navigation for niche: {niche}")

        try:
            # Шаг 1: Определение географии TikTok аккаунта через Perplexity
            if auto_detect_geo and profile_data:
                logger.info(
                    "🌍 Analyzing TikTok account origin with Perplexity...")

                # Import perplexity service for account origin analysis
                from .perplexity_service import perplexity_service

                # Extract data for analysis
                username = profile_data.get("username", "")
                bio = profile_data.get("bio", "")
                recent_captions = profile_data.get("recent_captions", [])
                follower_count = profile_data.get("follower_count", 0)
                video_count = profile_data.get("video_count", 0)

                # Analyze account origin
                account_origin = await perplexity_service.analyze_tiktok_account_origin(
                    username=username,
                    bio=bio,
                    recent_posts_content=recent_captions,
                    follower_count=follower_count,
                    video_count=video_count
                )

                actual_country = account_origin["country_code"]
                actual_language = account_origin["language"]
                logger.info(
                    f"🌍 Auto-detected TikTok account origin: {account_origin['country']} ({account_origin['confidence']} confidence)")
            else:
                actual_country = creative_center_mapping.get_country_code(
                    country)
                actual_language = language
                logger.info(f"🌍 Using specified geography: {actual_country}")

            # Шаг 2: Маппинг ниши к категории Creative Center
            category = creative_center_mapping.map_niche_to_category(niche)
            logger.info(
                f"📂 Mapped niche '{niche}' to Creative Center category '{category}'")

            # Шаг 3: Создание промпта для пошаговой навигации
            navigation_prompt = self._create_step_by_step_prompt(
                niche=niche,
                country=actual_country,
                language=actual_language,
                category=category,
                target_limit=limit
            )

            # Шаг 4: Выполнение навигации через Perplexity
            logger.info(f"🔍 Executing step-by-step navigation...")
            response_text = await self._make_perplexity_request(navigation_prompt)

            # Шаг 5: Парсинг и валидация результатов
            discovery_results = await self._parse_navigation_results(
                response_text=response_text,
                niche=niche,
                category=category,
                target_limit=limit
            )

            # Шаг 6: Дополнительная фильтрация по релевантности
            filtered_hashtags = await self._apply_relevance_filtering(
                hashtags=discovery_results.get('hashtags', []),
                niche=niche,
                target_limit=limit
            )

            logger.info(
                f"✅ Advanced discovery completed: {len(filtered_hashtags)} final hashtags")

            return {
                "niche": niche,
                "country": actual_country,
                "language": language,
                "category": discovery_results.get('category_used', category),
                "total_found": discovery_results.get('total_analyzed', 0),
                "hashtags": filtered_hashtags,
                "navigation_success": discovery_results.get('navigation_success', True)
            }

        except Exception as e:
            logger.error(f"❌ Advanced Creative Center discovery failed: {e}")
            return {
                "niche": niche,
                "country": country,
                "language": language,
                "category": "Unknown",
                "total_found": 0,
                "hashtags": [],
                "navigation_success": False
            }

    def _create_step_by_step_prompt(
        self,
        niche: str,
        country: str,
        language: str,
        category: str,
        target_limit: int
    ) -> str:
        """Создание детального промпта для пошаговой навигации"""

        base_url = f"https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/{language}"

        return f"""You are a professional TikTok Creative Center research agent. Execute this step-by-step navigation process:

## MISSION: Find the best hashtags for "{niche}" creators in {country} region

## STEP-BY-STEP NAVIGATION PROTOCOL:

### Step 1: Access Creative Center
- Navigate to: {base_url}
- Confirm you're on TikTok Creative Center hashtag inspiration page
- Verify the page loads correctly

### Step 2: Geographic Configuration
- Locate the country/region selector (usually top-right or in filters)
- Select region: {country}
- Wait for page to refresh with region-specific data
- Confirm hashtags now show {country}-specific trends

### Step 3: Category Selection  
- Find the industry/category filter menu
- Select category: "{category}"
- If "{category}" is unavailable, choose closest match from these options:
  * Technology, Fashion & Beauty, Food & Drink, Health & Fitness
  * Entertainment, Music, Education, Travel & Lifestyle, Gaming
  * Business & Finance, Arts & Crafts, Family & Parenting, Pets & Animals
- Wait for hashtags to load for selected category

### Step 4: Comprehensive Hashtag Analysis
- Study ALL hashtags displayed (typically 30-60 hashtags)
- For each hashtag, analyze:
  * Performance metrics (view counts, usage statistics)
  * Trend indicators (rising ↗, stable →, declining ↘)
  * Engagement rates and growth patterns
  * Relevance to "{niche}" content specifically

### Step 5: Smart Selection Criteria
From ALL analyzed hashtags, select top {target_limit} using this priority:
1. HIGH relevance to "{niche}" (not just popular hashtags)
2. STRONG performance metrics (views, usage)
3. POSITIVE growth trends (rising preferred)
4. BALANCED mix: niche-specific + some broader appeal
5. AVOID generic tags (#fyp, #viral) unless truly dominant for this niche

### Step 6: Return Structured Data
Provide ONLY this JSON format with NO additional text:

```json
{{
  "navigation_successful": true,
  "region_confirmed": "{country}",
  "category_used": "actual_category_name_selected",
  "total_hashtags_analyzed": 47,
  "selection_methodology": "relevance + performance + growth",
  "hashtags": [
    {{
      "name": "hashtag_without_hash",
      "url": "https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/{language}?hashtag=example",
      "volume": 1250000,
      "growth": 0.23,
      "score": 85.2,
      "relevance_score": 9.1,
      "relevance_reason": "Directly targets {niche} audience with proven engagement"
    }}
  ]
}}
```

## CRITICAL REQUIREMENTS:
- Actually browse the Creative Center interface systematically
- Use REAL data from {country} region and {category} category
- Prioritize hashtags genuinely relevant to "{niche}" creators
- Provide realistic metrics based on observed data
- Select hashtags that will help "{niche}" content get discovered

Execute this comprehensive analysis NOW for: "{niche}" in {country}"""

    async def _make_perplexity_request(self, prompt: str) -> str:
        """Execute Perplexity API request with retry logic"""
        max_retries = 3

        for attempt in range(max_retries):
            try:
                payload = {
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert TikTok Creative Center navigator with deep knowledge of social media trends, hashtag performance, and content discovery strategies. You have the ability to browse and analyze web content in real-time."
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
                    f"Making Perplexity request (attempt {attempt + 1})")

                response = await self.client.post(
                    self.base_url,
                    json=payload
                )

                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    logger.debug("✅ Perplexity request successful")
                    return content
                else:
                    logger.warning(
                        f"⚠️ Perplexity API error {response.status_code}: {response.text}")
                    if attempt == max_retries - 1:
                        raise Exception(
                            f"Perplexity API error: {response.status_code}")

            except Exception as e:
                logger.warning(
                    f"⚠️ Perplexity request attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise

                # Exponential backoff
                await asyncio.sleep(2 ** attempt)

        raise Exception("Perplexity API requests exhausted")

    async def _parse_navigation_results(
        self,
        response_text: str,
        niche: str,
        category: str,
        target_limit: int
    ) -> Dict[str, Any]:
        """Parse navigation results and extract hashtag data"""

        try:
            # Extract JSON from response
            text = response_text.strip()
            start_idx = text.find('{')
            end_idx = text.rfind('}')

            if start_idx != -1 and end_idx != -1:
                json_text = text[start_idx:end_idx + 1]
                data = json.loads(json_text)

                # Extract metadata
                navigation_successful = data.get('navigation_successful', True)
                region_confirmed = data.get('region_confirmed', 'US')
                category_used = data.get('category_used', category)
                total_analyzed = data.get('total_hashtags_analyzed', 0)

                # Extract and validate hashtags
                hashtags_data = data.get('hashtags', [])
                validated_hashtags = []

                # Get more for filtering
                for item in hashtags_data[:target_limit * 2]:
                    try:
                        name = str(item.get("name", "")).lstrip("#").strip()
                        url = str(item.get("url", "")).strip()
                        volume = item.get("volume")
                        growth = item.get("growth")
                        score = item.get("score")
                        relevance_score = item.get("relevance_score", 5.0)
                        relevance_reason = item.get("relevance_reason", "")

                        # Validation
                        if name and len(name) > 1:
                            # Generate URL if not provided
                            if not url or "ads.tiktok.com" not in url:
                                url = f"https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en?hashtag={name}"

                            hashtag_data = {
                                "name": name,
                                "url": url,
                                "volume": volume,
                                "growth": growth,
                                "score": score,
                                "relevance_score": relevance_score,
                                "relevance_reason": relevance_reason
                            }
                            validated_hashtags.append(hashtag_data)

                    except Exception as e:
                        logger.warning(f"⚠️ Failed to validate hashtag: {e}")
                        continue

                logger.info(
                    f"✅ Parsed {len(validated_hashtags)} hashtags from {total_analyzed} analyzed")

                return {
                    "hashtags": validated_hashtags,
                    "total_analyzed": total_analyzed,
                    "category_used": category_used,
                    "navigation_success": navigation_successful,
                    "region_confirmed": region_confirmed
                }

        except json.JSONDecodeError as e:
            logger.warning(f"⚠️ JSON parsing failed: {e}")
        except Exception as e:
            logger.warning(f"⚠️ Result parsing error: {e}")

        # Return empty results if parsing failed
        return {
            "hashtags": [],
            "total_analyzed": 0,
            "category_used": category,
            "navigation_success": False,
            "region_confirmed": "US"
        }

    async def _apply_relevance_filtering(
        self,
        hashtags: List[Dict[str, Any]],
        niche: str,
        target_limit: int
    ) -> List[Dict[str, Any]]:
        """Apply additional relevance filtering to select best hashtags"""

        if not hashtags:
            return []

        # Sort by relevance score (if available) and other metrics
        def calculate_final_score(hashtag):
            relevance_score = hashtag.get('relevance_score', 5.0)
            growth = hashtag.get('growth', 0.0) or 0.0
            score = hashtag.get('score', 50.0) or 50.0

            # Weighted scoring: relevance (40%) + growth (30%) + performance (30%)
            final_score = (relevance_score * 0.4) + \
                (growth * 100 * 0.3) + (score * 0.3)
            return final_score

        # Sort hashtags by final score
        sorted_hashtags = sorted(
            hashtags, key=calculate_final_score, reverse=True)

        # Take top N hashtags
        filtered = sorted_hashtags[:target_limit]

        logger.info(
            f"🎯 Applied relevance filtering: {len(filtered)} hashtags selected from {len(hashtags)}")

        return filtered

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Global service instance
advanced_creative_center_service = AdvancedCreativeCenterService()
