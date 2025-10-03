"""
Script to set admin status for users by email
Usage: python set_admin.py <email> [--remove]
"""
import asyncio
import sys
from auth_service_supabase import set_user_admin_by_email
from config import settings


async def main():
    if len(sys.argv) < 2:
        print("❌ Usage: python set_admin.py <email> [--remove]")
        print("   Example: python set_admin.py admin@example.com")
        print("   Example: python set_admin.py admin@example.com --remove")
        sys.exit(1)

    email = sys.argv[1]
    is_admin = True

    # Check for --remove flag
    if len(sys.argv) > 2 and sys.argv[2] == "--remove":
        is_admin = False

    print(f"{'🔑 Setting' if is_admin else '❌ Removing'} admin status for: {email}")

    success = await set_user_admin_by_email(email, is_admin)

    if success:
        print(
            f"✅ {'Admin status granted' if is_admin else 'Admin status removed'} for {email}")
        print(
            f"   User can now {'access all services without subscription limits' if is_admin else 'no longer bypass subscription limits'}")
    else:
        print(
            f"❌ Failed to set admin status. User with email {email} may not exist.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
