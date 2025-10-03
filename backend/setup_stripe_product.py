"""
Automatically create Stripe product and price for TrendXL Pro
"""
from stripe import StripeClient, StripeError
from config import settings
import os
from pathlib import Path


def setup_stripe_product():
    """Create TrendXL Pro product and $29/month price"""

    print("\n" + "="*80)
    print("🚀 CREATING STRIPE PRODUCT & PRICE")
    print("="*80 + "\n")

    try:
        client = StripeClient(settings.stripe_api_key)

        # Check mode
        if settings.stripe_api_key.startswith("sk_test_"):
            mode = "TEST"
            print("📋 Mode: TEST (no real charges)")
        else:
            mode = "LIVE"
            print("💰 Mode: LIVE (real charges will occur)")

        print()

        # 1. Create Product
        print("1️⃣ Creating Product...")
        product = client.products.create(params={
            "name": "TrendXL Pro",
            "description": "Unlimited trend analysis and AI insights for TikTok creators",
            "active": True
        })

        print(f"✅ Product created successfully!")
        print(f"   Product ID: {product.id}")
        print(f"   Name: {product.name}")
        print(f"   Description: {product.description}")
        print()

        # 2. Create Price ($29/month)
        print("2️⃣ Creating Price ($29/month)...")
        price = client.prices.create(params={
            "product": product.id,
            "unit_amount": 2900,  # $29.00 in cents
            "currency": "usd",
            "recurring": {
                "interval": "month",
                "interval_count": 1
            },
            "active": True
        })

        print(f"✅ Price created successfully!")
        print(f"   Price ID: {price.id}")
        print(
            f"   Amount: ${price.unit_amount / 100} {price.currency.upper()}")
        print(f"   Interval: {price.recurring.interval}ly")
        print()

        # 3. Update .env file
        print("3️⃣ Updating .env file...")

        env_path = Path(__file__).parent / ".env"

        if not env_path.exists():
            print(f"⚠️  .env file not found at {env_path}")
            print(f"\n✅ Manual setup required:")
            print(f"   Add this to your .env file:")
            print(f"   STRIPE_PRICE_ID={price.id}")
            return

        # Read current .env
        with open(env_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Update STRIPE_PRICE_ID
        updated = False
        for i, line in enumerate(lines):
            if line.startswith("STRIPE_PRICE_ID="):
                lines[i] = f"STRIPE_PRICE_ID={price.id}\n"
                updated = True
                break

        # If not found, add it
        if not updated:
            lines.append(f"\nSTRIPE_PRICE_ID={price.id}\n")

        # Write back
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

        print(f"✅ .env file updated!")
        print(f"   STRIPE_PRICE_ID={price.id}")
        print()

        # 4. Summary
        print("="*80)
        print("✅ SETUP COMPLETE!")
        print("="*80)
        print()
        print("📦 Created:")
        print(f"   Product: {product.name} ({product.id})")
        print(f"   Price: ${price.unit_amount / 100}/month ({price.id})")
        print()
        print("📝 Next Steps:")
        print("   1. Restart your backend server")
        print("   2. Test subscription flow")
        print("   3. View in Stripe Dashboard:")

        if mode == "TEST":
            print(
                f"      https://dashboard.stripe.com/test/products/{product.id}")
            print()
            print("🧪 Test with card: 4242 4242 4242 4242")
        else:
            print(f"      https://dashboard.stripe.com/products/{product.id}")
            print()
            print("⚠️  LIVE MODE - Real charges will occur!")

        print()

        return True

    except StripeError as e:
        print(f"❌ Stripe Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = setup_stripe_product()
    exit(0 if result else 1)
