"""
Test script for Free Trial functionality
Run this to verify the free trial system is working correctly
"""
import asyncio
import sys
from supabase_client import (
    can_use_free_trial,
    record_free_trial_usage,
    get_free_trial_info,
    check_user_can_analyze,
    check_active_subscription
)

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_test(name: str):
    """Print test name"""
    print(f"\n{BLUE}{'='*80}")
    print(f"TEST: {name}")
    print(f"{'='*80}{RESET}\n")


def print_success(message: str):
    """Print success message"""
    print(f"{GREEN}✅ {message}{RESET}")


def print_error(message: str):
    """Print error message"""
    print(f"{RED}❌ {message}{RESET}")


def print_info(message: str):
    """Print info message"""
    print(f"{YELLOW}ℹ️  {message}{RESET}")


async def test_free_trial_system(user_id: str):
    """
    Test the free trial system with a specific user ID

    Args:
        user_id: Supabase user UUID to test with
    """
    print(f"\n{BLUE}{'='*80}")
    print(f"🧪 TESTING FREE TRIAL SYSTEM")
    print(f"{'='*80}{RESET}\n")
    print_info(f"Testing with user ID: {user_id}")

    # Test 1: Check if user has subscription
    print_test("Check Active Subscription")
    try:
        has_subscription = await check_active_subscription(user_id)
        if has_subscription:
            print_success("User has active subscription")
        else:
            print_info(
                "User does not have subscription (expected for free trial test)")
    except Exception as e:
        print_error(f"Failed to check subscription: {e}")
        return

    # Test 2: Check if user can use free trial
    print_test("Check Free Trial Eligibility")
    try:
        can_use = await can_use_free_trial(user_id)
        if can_use:
            print_success("User CAN use free trial today")
        else:
            print_info("User CANNOT use free trial today (already used)")
    except Exception as e:
        print_error(f"Failed to check free trial: {e}")
        return

    # Test 3: Get free trial info
    print_test("Get Free Trial Info")
    try:
        trial_info = await get_free_trial_info(user_id)
        if trial_info:
            print_success("Free trial info retrieved:")
            print(f"   - Can use today: {trial_info.get('can_use_today')}")
            print(f"   - Today count: {trial_info.get('today_count')}")
            print(
                f"   - Total free analyses: {trial_info.get('total_free_analyses')}")
            print(f"   - Last used: {trial_info.get('last_used')}")
        else:
            print_info("No free trial info yet (user hasn't used any)")
    except Exception as e:
        print_error(f"Failed to get free trial info: {e}")
        return

    # Test 4: Check if user can analyze
    print_test("Check User Can Analyze")
    try:
        can_analyze, reason, details = await check_user_can_analyze(user_id)
        if can_analyze:
            print_success(f"User CAN analyze (reason: {reason})")
            print(f"   Details: {details}")
        else:
            print_error(f"User CANNOT analyze (reason: {reason})")
            print(f"   Details: {details}")
    except Exception as e:
        print_error(f"Failed to check if user can analyze: {e}")
        return

    # Test 5: Record free trial usage (if eligible)
    if can_use and not has_subscription:
        print_test("Record Free Trial Usage")
        print_info("This will consume 1 free trial for today!")
        response = input("Continue? (y/n): ")

        if response.lower() == 'y':
            try:
                success = await record_free_trial_usage(user_id, "test_profile")
                if success:
                    print_success("Free trial usage recorded successfully")

                    # Verify the record was created
                    new_info = await get_free_trial_info(user_id)
                    if new_info:
                        print_success("Verification: Free trial info updated")
                        print(
                            f"   - Today count: {new_info.get('today_count')}")
                        print(
                            f"   - Can use today: {new_info.get('can_use_today')}")
                else:
                    print_error("Failed to record free trial usage")
            except Exception as e:
                print_error(f"Error recording free trial: {e}")
        else:
            print_info("Skipped recording free trial usage")

    # Final summary
    print(f"\n{BLUE}{'='*80}")
    print(f"✨ TEST SUMMARY")
    print(f"{'='*80}{RESET}\n")

    final_info = await get_free_trial_info(user_id)
    if final_info:
        print(f"Today's usage: {final_info.get('today_count')}/1")
        print(f"Total free analyses: {final_info.get('total_free_analyses')}")
        print(
            f"Can use today: {'Yes ✅' if final_info.get('can_use_today') else 'No ❌'}")
    else:
        print("No free trial usage recorded yet")


async def quick_check(user_id: str):
    """Quick check of free trial status"""
    can_analyze, reason, details = await check_user_can_analyze(user_id)

    print(f"\n{BLUE}Quick Free Trial Check{RESET}")
    print(f"User: {user_id}")
    print(f"Can analyze: {can_analyze}")
    print(f"Reason: {reason}")
    print(f"Details: {details}\n")


def main():
    """Main test function"""
    print(f"\n{BLUE}╔════════════════════════════════════════════╗")
    print(f"║  FREE TRIAL SYSTEM TEST SCRIPT            ║")
    print(f"╚════════════════════════════════════════════╝{RESET}\n")

    if len(sys.argv) < 2:
        print_error("Usage: python test_free_trial.py <user_uuid> [--quick]")
        print_info(
            "Example: python test_free_trial.py 12345678-1234-1234-1234-123456789abc")
        print_info(
            "Quick check: python test_free_trial.py 12345678-1234-1234-1234-123456789abc --quick")
        sys.exit(1)

    user_id = sys.argv[1]
    quick_mode = "--quick" in sys.argv

    try:
        if quick_mode:
            asyncio.run(quick_check(user_id))
        else:
            asyncio.run(test_free_trial_system(user_id))
    except KeyboardInterrupt:
        print_info("\nTest interrupted by user")
    except Exception as e:
        print_error(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
