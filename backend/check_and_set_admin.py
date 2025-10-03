"""
Check and set admin status with detailed output
"""
from supabase_client import get_supabase
from config import settings

email = "mannitiger13@gmail.com"

print(f"\n{'='*80}")
print(f"🔍 CHECKING AND SETTING ADMIN STATUS")
print(f"{'='*80}\n")

# Show Supabase connection info
print(f"📊 Supabase URL: {settings.supabase_url}")
print(f"🔑 Using Supabase connection\n")

client = get_supabase()

# Step 1: Find user
print(f"1️⃣ Looking for user: {email}")
response = client.table("profiles").select("*").eq("email", email).execute()

if not response.data or len(response.data) == 0:
    print(f"❌ User NOT found with email: {email}")
    print(f"\n💡 Make sure the user is registered in the system!")
    exit(1)

user = response.data[0]
print(f"✅ User found!")
print(f"   User ID: {user['id']}")
print(f"   Email: {user['email']}")
print(f"   Username: {user.get('username', 'N/A')}")
print(f"   Current is_admin: {user.get('is_admin', False)}")
print()

# Step 2: Update admin status
print(f"2️⃣ Setting is_admin = true...")
try:
    update_response = client.table("profiles").update(
        {"is_admin": True}
    ).eq("id", user['id']).execute()

    print(f"✅ Update executed!")
    print()

    # Step 3: Verify the update
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
            print(f"🎉 SUCCESS! Admin status set to TRUE")
            print(f"{'='*80}")
            print(f"\n✅ User {email} is now an ADMIN!\n")
        else:
            print(f"{'='*80}")
            print(f"⚠️  WARNING: Update executed but is_admin is still FALSE")
            print(f"{'='*80}")
            print(f"\n💡 Check database permissions or RLS policies!\n")
    else:
        print(f"❌ Could not verify update")

except Exception as e:
    print(f"❌ Error updating admin status: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
