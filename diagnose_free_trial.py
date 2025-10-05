"""
Quick diagnostic script for free trial issue
"""
import asyncio
import sys
import os
from datetime import date

sys.path.insert(0, 'backend')

# First test: Check if Supabase connects
print("\n=== DIAGNOSTIC TEST ===\n")

print("[1] Loading Supabase client...")
try:
    from supabase_client import get_supabase, SUPABASE_KEY, SUPABASE_SERVICE_KEY, SUPABASE_URL
    print(f"✅ Supabase client loaded")
    print(f"   URL: {SUPABASE_URL}")
    print(f"   Using SERVICE_KEY: {bool(SUPABASE_SERVICE_KEY)}")
    print(f"   Key length: {len(SUPABASE_KEY)}")
except Exception as e:
    print(f"❌ Failed to load Supabase: {e}")
    sys.exit(1)

print("\n[2] Testing Supabase connection...")
try:
    client = get_supabase()
    # Try a simple query
    result = client.table('daily_free_analyses').select('*').limit(1).execute()
    print(f"✅ Connection successful!")
    print(f"   Tables accessible: daily_free_analyses")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print(f"   Error type: {type(e).__name__}")
    sys.exit(1)

print("\n[3] Testing RPC function...")
try:
    # Test if the function exists
    result = client.rpc('can_use_free_trial', {
        'p_user_id': '00000000-0000-0000-0000-000000000000'  # Dummy UUID
    }).execute()
    print(f"✅ RPC function 'can_use_free_trial' exists and works")
except Exception as e:
    print(f"❌ RPC function error: {e}")
    print(f"   This might be why free trial isn't working!")

print("\n[4] Checking daily_free_analyses table structure...")
try:
    result = client.table('daily_free_analyses').select('*').limit(0).execute()
    print(f"✅ Table 'daily_free_analyses' exists")
except Exception as e:
    print(f"❌ Table error: {e}")

print("\n[5] Checking for today's records...")
try:
    result = client.table('daily_free_analyses')\
        .select('*')\
        .eq('analysis_date', str(date.today()))\
        .execute()
    print(f"✅ Found {len(result.data)} record(s) for today")
    if result.data:
        print(f"   Records: {result.data}")
except Exception as e:
    print(f"❌ Query error: {e}")

print("\n=== END DIAGNOSTIC ===\n")
print("If all tests pass, the issue might be:")
print("1. User ID не правильный")
print("2. RPC функция не вызывается из-за ошибки")
print("3. Проблема на фронтенде с аутентификацией")
