"""
Creative Center Category Mapping Service
Маппинг пользовательских ниш к категориям TikTok Creative Center
"""
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class CreativeCenterMapping:
    """Сервис для маппинга ниш пользователей к категориям Creative Center"""

    # Маппинг ниш к категориям Creative Center
    NICHE_TO_CATEGORY_MAPPING = {
        # Technology & Reviews
        "Tech Reviews": "Technology",
        "Technology": "Technology",
        "Gadgets": "Technology",
        "Software": "Technology",
        "AI & Machine Learning": "Technology",
        "Coding": "Education",
        "Programming": "Education",

        # Fashion & Beauty
        "Fashion Style": "Fashion & Beauty",
        "Fashion": "Fashion & Beauty",
        "Beauty Tips": "Fashion & Beauty",
        "Makeup": "Fashion & Beauty",
        "Skincare": "Fashion & Beauty",
        "Styling": "Fashion & Beauty",
        "Clothing": "Fashion & Beauty",

        # Food & Cooking
        "Food Recipes": "Food & Drink",
        "Cooking": "Food & Drink",
        "Baking": "Food & Drink",
        "Food": "Food & Drink",
        "Recipes": "Food & Drink",
        "Restaurant": "Food & Drink",
        "Cuisine": "Food & Drink",

        # Fitness & Health
        "Fitness Training": "Health & Fitness",
        "Fitness": "Health & Fitness",
        "Workout": "Health & Fitness",
        "Gym": "Health & Fitness",
        "Health": "Health & Fitness",
        "Wellness": "Health & Fitness",
        "Nutrition": "Health & Fitness",

        # Entertainment & Comedy
        "Comedy Skits": "Entertainment",
        "Comedy": "Entertainment",
        "Entertainment": "Entertainment",
        "Funny": "Entertainment",
        "Memes": "Entertainment",
        "Humor": "Entertainment",

        # Music & Performance
        "Music": "Music",
        "Singing": "Music",
        "Dancing": "Entertainment",
        "Performance": "Entertainment",
        "Instruments": "Music",

        # Education & Learning
        "Education": "Education",
        "Learning": "Education",
        "Tutorial": "Education",
        "Teaching": "Education",
        "Academic": "Education",
        "Knowledge": "Education",

        # Travel & Lifestyle
        "Travel Vlogs": "Travel & Lifestyle",
        "Travel": "Travel & Lifestyle",
        "Lifestyle": "Travel & Lifestyle",
        "Adventure": "Travel & Lifestyle",
        "Tourism": "Travel & Lifestyle",

        # Gaming
        "Gaming Content": "Gaming",
        "Gaming": "Gaming",
        "Video Games": "Gaming",
        "Esports": "Gaming",
        "Game Reviews": "Gaming",

        # Business & Finance
        "Business": "Business & Finance",
        "Entrepreneurship": "Business & Finance",
        "Marketing": "Business & Finance",
        "Finance": "Business & Finance",
        "Investment": "Business & Finance",

        # Arts & Crafts
        "Art": "Arts & Crafts",
        "Drawing": "Arts & Crafts",
        "Crafts": "Arts & Crafts",
        "DIY": "Arts & Crafts",
        "Creative": "Arts & Crafts",

        # Family & Parenting
        "Parenting": "Family & Parenting",
        "Kids": "Family & Parenting",
        "Family": "Family & Parenting",
        "Children": "Family & Parenting",

        # Pets & Animals
        "Pets": "Pets & Animals",
        "Animals": "Pets & Animals",
        "Dogs": "Pets & Animals",
        "Cats": "Pets & Animals",
    }

    # Доступные категории Creative Center (основные)
    CREATIVE_CENTER_CATEGORIES = [
        "ALL",
        "Technology",
        "Fashion & Beauty",
        "Food & Drink",
        "Health & Fitness",
        "Entertainment",
        "Music",
        "Education",
        "Travel & Lifestyle",
        "Gaming",
        "Business & Finance",
        "Arts & Crafts",
        "Family & Parenting",
        "Pets & Animals",
        "Sports",
        "News & Politics",
        "Automotive"
    ]

    # Маппинг стран к кодам
    COUNTRY_CODES = {
        "United States": "US",
        "United Kingdom": "GB",
        "Canada": "CA",
        "Australia": "AU",
        "Germany": "DE",
        "France": "FR",
        "Italy": "IT",
        "Spain": "ES",
        "Japan": "JP",
        "South Korea": "KR",
        "Brazil": "BR",
        "Mexico": "MX",
        "India": "IN",
        "Russia": "RU",
        "China": "CN"
    }

    @classmethod
    def map_niche_to_category(cls, niche: str) -> str:
        """
        Маппинг ниши пользователя к категории Creative Center

        Args:
            niche: Ниша пользователя (например, "Tech Reviews")

        Returns:
            Категория Creative Center (например, "Technology")
        """
        # Точное совпадение
        if niche in cls.NICHE_TO_CATEGORY_MAPPING:
            return cls.NICHE_TO_CATEGORY_MAPPING[niche]

        # Поиск по частичному совпадению
        niche_lower = niche.lower()
        for key, category in cls.NICHE_TO_CATEGORY_MAPPING.items():
            if key.lower() in niche_lower or niche_lower in key.lower():
                logger.info(
                    f"📍 Mapped niche '{niche}' to category '{category}' via partial match")
                return category

        # Поиск ключевых слов
        keywords_mapping = {
            "tech": "Technology",
            "fashion": "Fashion & Beauty",
            "beauty": "Fashion & Beauty",
            "food": "Food & Drink",
            "cook": "Food & Drink",
            "fitness": "Health & Fitness",
            "health": "Health & Fitness",
            "comedy": "Entertainment",
            "funny": "Entertainment",
            "music": "Music",
            "education": "Education",
            "learn": "Education",
            "travel": "Travel & Lifestyle",
            "lifestyle": "Travel & Lifestyle",
            "gaming": "Gaming",
            "game": "Gaming",
            "business": "Business & Finance",
            "finance": "Business & Finance"
        }

        for keyword, category in keywords_mapping.items():
            if keyword in niche_lower:
                logger.info(
                    f"📍 Mapped niche '{niche}' to category '{category}' via keyword '{keyword}'")
                return category

        # Дефолтная категория
        logger.warning(
            f"⚠️ Could not map niche '{niche}' to specific category, using 'ALL'")
        return "ALL"

    @classmethod
    def get_country_code(cls, country: str) -> str:
        """
        Получить код страны

        Args:
            country: Название страны

        Returns:
            Код страны (например, "US")
        """
        if country in cls.COUNTRY_CODES:
            return cls.COUNTRY_CODES[country]

        # Поиск по частичному совпадению
        country_lower = country.lower()
        for name, code in cls.COUNTRY_CODES.items():
            if country_lower in name.lower() or name.lower() in country_lower:
                return code

        # Если уже код страны
        if len(country) == 2 and country.upper() in cls.COUNTRY_CODES.values():
            return country.upper()

        # Дефолт - США
        return "US"

    @classmethod
    def get_supported_countries(cls) -> List[str]:
        """Получить список поддерживаемых стран"""
        return list(cls.COUNTRY_CODES.keys())

    @classmethod
    def get_supported_categories(cls) -> List[str]:
        """Получить список поддерживаемых категорий"""
        return cls.CREATIVE_CENTER_CATEGORIES

    @classmethod
    def detect_user_geo_from_profile(cls, profile_data: dict) -> str:
        """
        Определить географию пользователя из данных профиля

        Args:
            profile_data: Данные профиля пользователя

        Returns:
            Код страны
        """
        # Пока возвращаем дефолтное значение
        # В будущем можно анализировать bio, локацию и другие данные
        return "US"


# Глобальный экземпляр маппинга
creative_center_mapping = CreativeCenterMapping()
