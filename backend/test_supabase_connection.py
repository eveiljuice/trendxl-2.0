"""
Test Supabase connection and database operations
"""
from supabase_client import (
    get_supabase,
    insert_user,
    get_user_by_link,
    insert_trend,
    get_trends_by_user,
    insert_interaction,
    get_user_interactions,
    insert_niche_adapter,
    get_niche_adapter_by_domain
)
import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def test_connection():
    """Test basic Supabase connection"""
    print("🧪 Testing Supabase connection...")
    try:
        client = get_supabase()
        print("✅ Supabase client initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize Supabase client: {e}")
        return False


async def test_user_operations():
    """Test user CRUD operations"""
    print("\n🧪 Testing user operations...")

    test_link = "https://tiktok.com/@test_user_12345"

    try:
        # Insert user
        print("  → Inserting test user...")
        user = await insert_user(
            link=test_link,
            parsed_niche="Tech Reviews",
            location="US",
            followers=5000,
            engagement_rate=4.2,
            top_posts=[
                {"id": "post1", "views": 10000, "likes": 500},
                {"id": "post2", "views": 15000, "likes": 750}
            ]
        )
        print(f"  ✅ User inserted: {user.get('id')}")

        # Get user by link
        print("  → Fetching user by link...")
        fetched_user = await get_user_by_link(test_link)
        if fetched_user:
            print(f"  ✅ User fetched: {fetched_user.get('parsed_niche')}")
        else:
            print("  ❌ User not found")
            return False

        return user
    except Exception as e:
        print(f"  ❌ User operations failed: {e}")
        return None


async def test_trend_operations(user_id: str):
    """Test trend CRUD operations"""
    print("\n🧪 Testing trend operations...")

    try:
        # Insert trend
        print("  → Inserting test trend...")
        trend = await insert_trend(
            user_id=user_id,
            trend_title="AI Content Creation",
            platform="tiktok",
            video_url="https://tiktok.com/@test/video/123",
            stat_metrics={
                "views": 50000,
                "likes": 2500,
                "comments": 150,
                "shares": 80
            },
            relevance_score=8.5
        )
        print(f"  ✅ Trend inserted: {trend.get('id')}")

        # Get trends for user
        print("  → Fetching trends for user...")
        trends = await get_trends_by_user(user_id, limit=10)
        print(f"  ✅ Found {len(trends)} trends")

        return trend
    except Exception as e:
        print(f"  ❌ Trend operations failed: {e}")
        return None


async def test_interaction_operations(user_id: str, trend_id: str):
    """Test interaction logging"""
    print("\n🧪 Testing interaction operations...")

    try:
        # Log interaction
        print("  → Logging interaction...")
        interaction = await insert_interaction(
            user_id=user_id,
            trend_id=trend_id,
            action_type="watched"
        )
        print(f"  ✅ Interaction logged: {interaction.get('id')}")

        # Get user interactions
        print("  → Fetching user interactions...")
        interactions = await get_user_interactions(user_id, limit=10)
        print(f"  ✅ Found {len(interactions)} interactions")

        return True
    except Exception as e:
        print(f"  ❌ Interaction operations failed: {e}")
        return False


async def test_niche_adapter_operations():
    """Test niche adapter operations"""
    print("\n🧪 Testing niche adapter operations...")

    test_domain = "tech-reviews"

    try:
        # Insert niche adapter
        print("  → Inserting niche adapter...")
        adapter = await insert_niche_adapter(
            domain=test_domain,
            parsed_by_gpt_summary="Technology product reviews and comparisons",
            topic_tags=["tech", "reviews", "gadgets", "electronics"]
        )
        print(f"  ✅ Niche adapter inserted: {adapter.get('id')}")

        # Get niche adapter
        print("  → Fetching niche adapter...")
        fetched_adapter = await get_niche_adapter_by_domain(test_domain)
        if fetched_adapter:
            print(
                f"  ✅ Niche adapter fetched: {len(fetched_adapter.get('topic_tags', []))} tags")
        else:
            print("  ❌ Niche adapter not found")
            return False

        return True
    except Exception as e:
        print(f"  ❌ Niche adapter operations failed: {e}")
        return False


async def cleanup_test_data():
    """Clean up test data (optional)"""
    print("\n🧹 Cleaning up test data...")
    try:
        client = get_supabase()

        # Delete test user (cascade will delete related trends and interactions)
        await asyncio.to_thread(
            lambda: client.table("users")
            .delete()
            .eq("link", "https://tiktok.com/@test_user_12345")
            .execute()
        )

        # Delete test niche adapter
        await asyncio.to_thread(
            lambda: client.table("niche_adapters")
            .delete()
            .eq("domain", "tech-reviews")
            .execute()
        )

        print("✅ Test data cleaned up")
    except Exception as e:
        print(f"⚠️ Cleanup warning: {e}")


async def main():
    """Run all tests"""
    print("=" * 60)
    print("TrendXL 2.0 - Supabase Connection Test")
    print("=" * 60)

    # Test 1: Connection
    if not await test_connection():
        print("\n❌ Connection test failed. Please check your configuration.")
        return

    # Test 2: User operations
    user = await test_user_operations()
    if not user:
        print("\n❌ User operations failed.")
        return

    user_id = user.get('id')

    # Test 3: Trend operations
    trend = await test_trend_operations(user_id)
    if not trend:
        print("\n❌ Trend operations failed.")
        return

    trend_id = trend.get('id')

    # Test 4: Interaction operations
    if not await test_interaction_operations(user_id, trend_id):
        print("\n❌ Interaction operations failed.")
        return

    # Test 5: Niche adapter operations
    if not await test_niche_adapter_operations():
        print("\n❌ Niche adapter operations failed.")
        return

    # Cleanup
    await cleanup_test_data()

    print("\n" + "=" * 60)
    print("✅ All tests passed successfully!")
    print("=" * 60)
    print("\n📌 Next steps:")
    print("1. Update your Supabase keys in backend/.env")
    print("2. Apply the migration in Supabase Dashboard")
    print("3. Run: python backend/run_server.py")
    print("4. Test the application in your browser")

if __name__ == "__main__":
    asyncio.run(main())
