"""
List all Stripe products and prices in your account
"""
from stripe import StripeClient, StripeError
from config import settings


def list_stripe_products():
    """List all products and their prices"""

    print("\n" + "="*80)
    print("📦 STRIPE PRODUCTS & PRICES")
    print("="*80 + "\n")

    try:
        client = StripeClient(settings.stripe_api_key)

        # List all products
        products = client.products.list(params={"limit": 100, "active": True})

        if not products.data:
            print("❌ No products found in your Stripe account!")
            print("\n💡 To create a product and price:")
            print("   1. Go to https://dashboard.stripe.com/products")
            print("   2. Click 'Add product'")
            print("   3. Name: 'TrendXL Pro'")
            print("   4. Add price: $29/month recurring")
            print("   5. Copy the Price ID and update backend/.env")
            return

        print(f"Found {len(products.data)} product(s):\n")

        for i, product in enumerate(products.data, 1):
            print(f"{'='*80}")
            print(f"Product #{i}: {product.name}")
            print(f"{'='*80}")
            print(f"📦 Product ID: {product.id}")
            print(f"✅ Active: {product.active}")

            if hasattr(product, 'description') and product.description:
                print(f"📝 Description: {product.description}")

            # Get prices for this product
            print(f"\n💰 Prices for this product:")
            prices = client.prices.list(
                params={"product": product.id, "limit": 100})

            if not prices.data:
                print("   ⚠️  No prices found for this product")
            else:
                for j, price in enumerate(prices.data, 1):
                    print(f"\n   Price #{j}:")
                    print(f"   🆔 Price ID: {price.id}")
                    print(f"   ✅ Active: {price.active}")
                    print(
                        f"   💵 Amount: {(price.unit_amount or 0) / 100} {price.currency.upper()}")

                    if price.recurring:
                        print(f"   🔄 Type: Recurring")
                        print(f"   📅 Interval: {price.recurring.interval}")
                        print(
                            f"   🔢 Interval Count: {price.recurring.interval_count}")
                    else:
                        print(f"   🔄 Type: One-time")

                    # Highlight if this is the configured price
                    if price.id == settings.stripe_price_id:
                        print(f"   ⭐ THIS IS YOUR CONFIGURED PRICE")

            print()

        # Show summary
        print(f"{'='*80}")
        print("📋 SUMMARY")
        print(f"{'='*80}")
        print(f"Total Products: {len(products.data)}")

        # Find active recurring prices
        all_prices = []
        for product in products.data:
            prices = client.prices.list(
                params={"product": product.id, "active": True})
            for price in prices.data:
                if price.recurring:
                    all_prices.append({
                        "id": price.id,
                        "product": product.name,
                        "amount": (price.unit_amount or 0) / 100,
                        "currency": price.currency,
                        "interval": price.recurring.interval
                    })

        if all_prices:
            print(f"\n🔄 Active Recurring Prices ({len(all_prices)}):")
            for p in all_prices:
                print(f"   • {p['id']}")
                print(f"     Product: {p['product']}")
                print(
                    f"     Price: ${p['amount']} {p['currency'].upper()}/{p['interval']}")
                print()

        # Check if configured price is valid
        print(f"{'='*80}")
        print("🔍 CURRENT CONFIGURATION")
        print(f"{'='*80}")
        print(f"Configured Price ID: {settings.stripe_price_id}")

        # Check if it exists
        found = False
        for product in products.data:
            prices = client.prices.list(params={"product": product.id})
            for price in prices.data:
                if price.id == settings.stripe_price_id:
                    found = True
                    print(f"✅ Price found and exists!")
                    print(f"   Product: {product.name}")
                    print(f"   Active: {price.active}")
                    break
            if found:
                break

        if not found:
            print(f"❌ Configured price ID does not exist!")
            print(f"\n💡 Action Required:")
            print(f"   1. Choose a price ID from the list above, OR")
            print(f"   2. Create a new product at https://dashboard.stripe.com/products")
            print(f"   3. Update STRIPE_PRICE_ID in backend/.env")

            if all_prices:
                print(f"\n📝 Suggested: Use this price ID:")
                print(f"   STRIPE_PRICE_ID={all_prices[0]['id']}")

    except StripeError as e:
        print(f"❌ Stripe API Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    list_stripe_products()
