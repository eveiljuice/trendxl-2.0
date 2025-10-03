"""
Force set admin status using service role key (bypasses RLS)
"""
from supabase import create_client, Client
from config import settings

email = "mannitiger13@gmail.com"

print(f"\n{'='*80}")
print(f"🔓 FORCE SETTING ADMIN STATUS (BYPASSING RLS)")
print(f"{'='*80}\n")

# Check if service role key is available
if not settings.supabase_service_role_key or settings.supabase_service_role_key.strip() == "":
    print(f"❌ SUPABASE_SERVICE_ROLE_KEY not configured!")
    print(f"\n💡 Solutions:")
    print(f"   1. Add SUPABASE_SERVICE_ROLE_KEY to backend/.env")
    print(f"   2. Get it from: https://supabase.com/dashboard/project/YOUR_PROJECT/settings/api")
    print(f"   3. Look for 'service_role' key (secret)")
    print(f"\nOR disable RLS on profiles table for is_admin column")
    exit(1)

print(f"✅ Service role key found")
print(f"📊 Supabase URL: {settings.supabase_url}\n")

# Create client with service role key (bypasses RLS)
client: Client = create_client(
    settings.supabase_url,
    settings.supabase_service_role_key
)

# Step 1: Find user
print(f"1️⃣ Looking for user: {email}")
response = client.table("profiles").select("*").eq("email", email).execute()

if not response.data or len(response.data) == 0:
    print(f"❌ User NOT found with email: {email}")
    exit(1)

user = response.data[0]
print(f"✅ User found!")
print(f"   User ID: {user['id']}")
print(f"   Email: {user['email']}")
print(f"   Username: {user.get('username', 'N/A')}")
print(f"   Current is_admin: {user.get('is_admin', False)}")
print()

# Step 2: Force update with service role (bypasses RLS)
print(f"2️⃣ Force updating is_admin = true (using service role)...")
try:
    update_response = client.table("profiles").update(
        {"is_admin": True}
    ).eq("id", user['id']).execute()

    print(f"✅ Update executed with service role!")
    print()

    # Step 3: Verify
    print(f"3️⃣ Verifying update...")
    verify_response = client.table("profiles").select(
        "*").eq("email", email).execute()

    if verify_response.data and len(verify_response.data) > 0:
        updated_user = verify_response.data[0]
        print(f"✅ Verification successful!")
        print(f"   User ID: {updated_user['id']}")
        print(f"   Email: {updated_user['email']}")
        print(f"   Username: {updated_user.get('username', 'N/A')}")
        print(f"   ⭐ is_admin: {updated_user.get('is_admin', False)}")
        print()

        if updated_user.get('is_admin', False):
            print(f"{'='*80}")
            print(f"🎉 SUCCESS! Admin status FORCED to TRUE")
            print(f"{'='*80}")
            print(f"\n✅ User {email} is now an ADMIN!")
            print(f"✅ RLS policies bypassed using service role key\n")
        else:
            print(f"{'='*80}")
            print(f"❌ FAILED: Still FALSE even with service role")
            print(f"{'='*80}")
            print(f"\n💡 Check if column exists in database schema!\n")
    else:
        print(f"❌ Could not verify update")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
