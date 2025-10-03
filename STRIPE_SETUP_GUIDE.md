# Stripe Subscription Setup Guide

This guide will help you set up Stripe subscriptions for TrendXL 2.0.

## 📋 Prerequisites

1. Stripe account (create at https://stripe.com)
2. Supabase project configured
3. Backend and frontend running

## 🔧 Backend Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Apply Supabase Migration

Run the Stripe migration to add subscription fields to the profiles table:

```sql
-- Execute this in Supabase SQL Editor or via CLI
-- File: backend/supabase_stripe_migration.sql
```

Or use Supabase CLI:

```bash
supabase db push
```

### 3. Configure Environment Variables

Add to your `.env` file in the `backend` directory:

```env
# Stripe Configuration
STRIPE_API_KEY=sk_test_xxxxx  # Your Stripe Secret Key
STRIPE_WEBHOOK_SECRET=whsec_xxxxx  # Your Webhook Secret (optional)
STRIPE_PRICE_ID=price_xxxxx  # Your $29/month Price ID
```

### 4. Create Stripe Products and Prices

1. Go to Stripe Dashboard → Products
2. Create a new product:
   - Name: "TrendXL Pro"
   - Description: "Unlimited trend analysis and AI insights"
3. Create a recurring price:
   - Amount: $29.00
   - Billing period: Monthly
   - Currency: USD
4. Copy the Price ID (starts with `price_`) and add it to `.env`

## 🎨 Frontend Setup

### 1. Install Dependencies

```bash
npm install
```

This will install:

- `stripe` package (already in requirements.txt)
- `react-router-dom` for routing (already in package.json)

### 2. Configure Environment Variables

Add to your `.env` file in the root directory:

```env
VITE_API_URL=http://localhost:8000  # Or your backend URL
```

## 🚀 Running the Application

### 1. Start Backend

```bash
cd backend
python run_server.py
```

Or via npm script from root:

```bash
npm run backend
```

### 2. Start Frontend

```bash
npm run dev
```

### 3. Run Both Simultaneously

```bash
npm run dev:full
```

## 🧪 Testing Stripe Integration

### Test Registration Flow

1. **Register a new user**

   - Go to http://localhost:5173
   - Click "Sign Up"
   - Fill in email, username, and password
   - After registration, a Stripe customer is automatically created

2. **View Profile & Subscription**

   - Click on your profile avatar in the top right
   - Select "My Profile"
   - You should see "No Active Subscription" with a subscribe button

3. **Test Subscription Checkout**

   - Click "Subscribe Now - $29/month"
   - You'll be redirected to Stripe Checkout
   - Use test card: `4242 4242 4242 4242`
   - Any future date for expiry
   - Any 3-digit CVC

4. **View Active Subscription**

   - After successful payment, return to My Profile
   - You should see your active subscription with:
     - Status: Active
     - Price: $29/month
     - Current billing period
     - Cancel button

5. **Test Cancellation**
   - Click "Cancel Subscription"
   - Confirm cancellation
   - Subscription will be set to cancel at period end
   - You can reactivate it before the period ends

## 🔐 Stripe Test Cards

Use these test cards in Stripe Checkout:

| Card Number           | Description        |
| --------------------- | ------------------ |
| `4242 4242 4242 4242` | Successful payment |
| `4000 0000 0000 9995` | Declined card      |
| `4000 0025 0000 3155` | 3D Secure required |

## 📊 Monitoring

### Check Stripe Dashboard

1. **Customers**: See all registered users
2. **Subscriptions**: View active/canceled subscriptions
3. **Payments**: Monitor successful/failed payments
4. **Webhooks**: Track webhook events (for production)

### Check Supabase

1. **Profiles Table**: Check `stripe_customer_id` and `stripe_subscription_id` fields
2. **Auth Users**: Verify user accounts

## 🚨 Troubleshooting

### "Stripe API key not configured"

- Check that `STRIPE_API_KEY` is set in backend `.env`
- Restart the backend server

### "Stripe customer not found"

- User might have been created before Stripe integration
- Manually create a Stripe customer or re-register

### "Failed to create checkout session"

- Verify `STRIPE_PRICE_ID` is correct
- Check Stripe Dashboard that the price exists
- Ensure price is active and recurring

### Database errors

- Run the Supabase migration: `backend/supabase_stripe_migration.sql`
- Check that profiles table has Stripe columns

## 🌐 Production Deployment

### 1. Update Environment Variables

Set production values:

```env
STRIPE_API_KEY=sk_live_xxxxx  # Live key
STRIPE_WEBHOOK_SECRET=whsec_xxxxx  # Production webhook
STRIPE_PRICE_ID=price_xxxxx  # Production price ID
```

### 2. Configure Webhooks

1. Go to Stripe Dashboard → Webhooks
2. Add endpoint: `https://your-domain.com/api/v1/webhook/stripe`
3. Select events:
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
4. Copy webhook secret and add to `.env`

### 3. Enable Live Mode

Toggle to "Live mode" in Stripe Dashboard before going to production.

## 💡 Features Implemented

✅ Automatic Stripe customer creation on registration
✅ Subscription management (create, view, cancel, reactivate)
✅ Stripe Checkout integration
✅ Subscription status tracking in database
✅ User profile page with subscription info
✅ Clean UI without mock buttons

## 📝 Notes

- Customers are created automatically when users register
- Subscriptions must be created via Stripe Checkout
- Subscription data is synced between Stripe and Supabase
- Users can cancel anytime (will keep access until period end)
- Test mode is safe - no real charges

## 🔗 Useful Links

- [Stripe Dashboard](https://dashboard.stripe.com)
- [Stripe Testing](https://stripe.com/docs/testing)
- [Stripe Checkout Docs](https://stripe.com/docs/payments/checkout)
- [Stripe Subscriptions Guide](https://stripe.com/docs/billing/subscriptions/overview)
