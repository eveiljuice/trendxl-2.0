#!/usr/bin/env python3
"""
Test Perplexity API connection and functionality
"""
from config import settings
from services.perplexity_service import perplexity_service
import asyncio
import sys
import os

# Add backend directory to path
sys.path.append('backend')


async def test_perplexity():
    """Test Perplexity API connection"""
    print("🧪 Testing Perplexity API...")
    print("=" * 40)

    # Check configuration
    print(f"API Key configured: {bool(settings.perplexity_api_key)}")
    print(f"Model: {settings.perplexity_model}")
    print(f"Key prefix: {settings.perplexity_api_key[:10]}...")

    # Test health check
    print("\n1️⃣ Testing health check...")
    try:
        health_ok = await perplexity_service.health_check()
        print(f"Health check result: {health_ok}")

        if not health_ok:
            print("❌ Health check failed!")
            return False

    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

    # Test niche analysis
    print("\n2️⃣ Testing niche analysis...")
    try:
        test_username = "testuser"
        test_bio = "Tech enthusiast sharing AI and coding tips"
        test_posts = [
            "Just built an amazing AI chatbot using Python!",
            "Machine learning tips for beginners #AI #Python",
            "Coding late night again... #developer #programming"
        ]

        print(f"Analyzing test profile: @{test_username}")
        print(f"Bio: {test_bio}")
        print(f"Posts: {len(test_posts)} sample posts")

        result = await perplexity_service.analyze_user_niche(
            username=test_username,
            bio=test_bio,
            recent_posts_content=test_posts,
            follower_count=1000,
            video_count=50
        )

        print(f"\n✅ Analysis successful!")
        print(f"Category: {result.niche_category}")
        print(f"Description: {result.niche_description}")
        print(f"Key Topics: {', '.join(result.key_topics)}")
        print(f"Confidence: {result.confidence_score}")

        return True

    except Exception as e:
        print(f"❌ Niche analysis error: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

    finally:
        await perplexity_service.close()

if __name__ == "__main__":
    success = asyncio.run(test_perplexity())

    if success:
        print("\n🎉 Perplexity API test PASSED!")
    else:
        print("\n❌ Perplexity API test FAILED!")
        print("Check your API key and network connection")
