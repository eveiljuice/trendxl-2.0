"""
Test script to reproduce login issue using Playwright
"""
import asyncio
from playwright.async_api import async_playwright
import json


async def test_login():
    """Test login flow and capture detailed error"""
    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Enable request/response logging
        async def log_request(request):
            print(f"\n📤 REQUEST: {request.method} {request.url}")
            if request.post_data:
                try:
                    data = json.loads(request.post_data)
                    # Hide password
                    if 'password' in data:
                        data['password'] = '***'
                    print(f"   Body: {json.dumps(data, indent=2)}")
                except:
                    print(f"   Body: {request.post_data[:100]}...")

        async def log_response(response):
            if '/api/v1/auth/' in response.url:
                print(f"\n📥 RESPONSE: {response.status} {response.url}")
                try:
                    body = await response.text()
                    print(f"   Body: {body[:500]}")
                except:
                    pass

        page.on("request", log_request)
        page.on("response", log_response)

        # Go to deployed site
        print("🌐 Opening site: https://endxl-2-0-01102025.vercel.app")
        await page.goto("https://endxl-2-0-01102025.vercel.app")
        await page.wait_for_load_state("networkidle")

        # Wait for auth dialog to appear
        print("\n⏳ Waiting for auth dialog...")
        await page.wait_for_selector('text="Welcome to Trendzl"', timeout=5000)

        # Click Login tab
        print("🔘 Clicking Login tab...")
        await page.click('button:has-text("Login")')
        await page.wait_for_timeout(500)

        # Fill in credentials
        print("\n📝 Filling credentials...")
        await page.fill('input[type="email"]', 's.kamaliev@generaition.org')
        # Replace with actual password
        await page.fill('input[type="password"]', 'your_actual_password_here')

        # Click login button
        print("🔑 Clicking Login button...")
        await page.click('button:has-text("Login")')

        # Wait for response
        await page.wait_for_timeout(3000)

        # Check if error message appears
        error = await page.query_selector('text="Ошибка"')
        if error:
            print("\n❌ Error detected!")
            error_text = await error.text_content()
            print(f"   Error message: {error_text}")

            # Try to get more details
            error_details = await page.query_selector('text="Login failed"')
            if error_details:
                details_text = await error_details.text_content()
                print(f"   Details: {details_text}")

        # Check if logged in successfully
        await page.wait_for_timeout(2000)
        success = await page.query_selector('text="Dashboard"') or await page.query_selector('text="Анализ"')
        if success:
            print("\n✅ Login successful!")
        else:
            print("\n❌ Login failed - still on login page")

        # Keep browser open for manual inspection
        print("\n⏸️  Press Enter to close browser...")
        input()

        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_login())











