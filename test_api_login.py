"""
Test login API directly to see detailed error
"""
import asyncio
import httpx
import json


async def test_login_api():
    """Test login API endpoint"""

    # Try production API
    API_URL = "https://endxl-2-0-01102025.vercel.app"

    print("🔍 Testing Login API")
    print(f"API URL: {API_URL}")
    print("="*60)

    # Test 1: Check if API is alive
    print("\n1️⃣ Testing API health...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_URL}/health", timeout=10.0)
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    # Test 2: Try login with the problematic account
    print("\n2️⃣ Testing Login endpoint...")
    email = "s.kamaliev@generaition.org"
    # NOTE: Replace with actual password for testing
    password = "test123456"  # This is probably wrong, but let's see the error

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_URL}/api/v1/auth/login",
                json={
                    "email": email,
                    "password": password
                },
                timeout=10.0
            )

            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")

            if response.status_code == 200:
                data = response.json()
                print(f"\n   ✅ Login successful!")
                print(f"   User: {data.get('user', {})}")
            else:
                print(f"\n   ❌ Login failed!")
                try:
                    error_data = response.json()
                    print(f"   Error: {json.dumps(error_data, indent=2)}")
                except:
                    pass

    except Exception as e:
        print(f"   ❌ Exception: {e}")

    # Test 3: Check if we can access /api/v1/auth/me without token
    print("\n3️⃣ Testing /me endpoint without auth...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_URL}/api/v1/auth/me",
                timeout=10.0
            )
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

    print("\n" + "="*60)
    print("Test complete!")

if __name__ == "__main__":
    asyncio.run(test_login_api())











