"""
Test script to verify free trial fix
"""
from supabase_client import (
    get_free_trial_info,
    can_use_free_trial,
    record_free_trial_usage,
    SUPABASE_SERVICE_KEY,
    SUPABASE_KEY
)
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, 'backend')


# ANSI Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


async def test_free_trial(user_id: str):
    """Test free trial system with fixed code"""

    print(f"\n{BLUE}{'='*80}")
    print(f"🧪 Testing Free Trial Fix")
    print(f"{'='*80}{RESET}\n")

    # Test 1: Check keys
    print(f"{BLUE}[1] Checking Supabase Keys{RESET}")
    print(f"   SERVICE_KEY exists: {bool(SUPABASE_SERVICE_KEY)}")
    print(
        f"   SERVICE_KEY length: {len(SUPABASE_SERVICE_KEY) if SUPABASE_SERVICE_KEY else 0}")
    print(f"   Using KEY (first 30 chars): {SUPABASE_KEY[:30]}...")
    if SUPABASE_SERVICE_KEY:
        print(f"   {GREEN}✅ Using SERVICE_ROLE_KEY{RESET}")
    else:
        print(f"   {YELLOW}⚠️ Using ANON_KEY (fallback){RESET}")

    # Test 2: Check current status
    print(f"\n{BLUE}[2] Checking Current Free Trial Status{RESET}")
    try:
        can_use = await can_use_free_trial(user_id)
        trial_info = await get_free_trial_info(user_id)

        print(f"   Can use free trial: {can_use}")
        if trial_info:
            print(f"   Today count: {trial_info.get('today_count', 0)}/1")
            print(
                f"   Total analyses: {trial_info.get('total_free_analyses', 0)}")

        if can_use:
            print(f"   {GREEN}✅ User can use free trial{RESET}")
        else:
            print(f"   {RED}❌ Free trial already used today{RESET}")
    except Exception as e:
        print(f"   {RED}❌ Error: {e}{RESET}")
        return

    # Test 3: Try to record usage (if available)
    if can_use:
        print(f"\n{BLUE}[3] Testing record_free_trial_usage(){RESET}")
        print(f"   {YELLOW}This will consume 1 free trial!{RESET}")
        response = input("   Continue? (y/n): ")

        if response.lower() == 'y':
            try:
                print(f"   Calling record_free_trial_usage...")
                success = await record_free_trial_usage(user_id, "test_profile_fix")

                if success:
                    print(
                        f"   {GREEN}✅ Successfully recorded free trial usage{RESET}")

                    # Verify
                    new_info = await get_free_trial_info(user_id)
                    if new_info:
                        print(f"   Verification:")
                        print(
                            f"      - Today count: {new_info.get('today_count')}/1")
                        print(
                            f"      - Can use: {new_info.get('can_use_today')}")
                else:
                    print(
                        f"   {RED}❌ record_free_trial_usage returned False{RESET}")

            except Exception as e:
                print(f"   {RED}❌ Exception caught: {type(e).__name__}{RESET}")
                print(f"   {RED}   Error: {e}{RESET}")
                print(
                    f"   {GREEN}✅ Exception properly raised (this is good!){RESET}")
        else:
            print(f"   {YELLOW}Skipped recording{RESET}")
    else:
        print(f"\n{BLUE}[3] Skipping record test{RESET}")
        print(f"   {YELLOW}Free trial already used today{RESET}")

    # Final status
    print(f"\n{BLUE}{'='*80}")
    print(f"📊 Final Status")
    print(f"{'='*80}{RESET}")

    final_info = await get_free_trial_info(user_id)
    if final_info:
        print(f"Today's usage: {final_info.get('today_count')}/1")
        print(f"Total analyses: {final_info.get('total_free_analyses')}")
        can_use = final_info.get('can_use_today')
        print(f"Can use today: {'Yes ✅' if can_use else 'No ❌'}")

    print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"{RED}Usage: python test_free_trial_fix.py <user-uuid>{RESET}")
        print(
            f"{YELLOW}Get your UUID from Supabase Dashboard > Authentication > Users{RESET}")
        sys.exit(1)

    user_id = sys.argv[1]
    asyncio.run(test_free_trial(user_id))
