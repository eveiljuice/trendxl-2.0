-- Migration: Add Stripe fields to profiles table
-- This migration adds Stripe customer and subscription tracking to user profiles

-- Add Stripe fields to profiles table
ALTER TABLE profiles
ADD COLUMN IF NOT EXISTS stripe_customer_id TEXT,
ADD COLUMN IF NOT EXISTS stripe_subscription_id TEXT,
ADD COLUMN IF NOT EXISTS stripe_subscription_status TEXT,
ADD COLUMN IF NOT EXISTS subscription_start_date TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS subscription_end_date TIMESTAMPTZ;

-- Create index for faster lookups by Stripe customer ID
CREATE INDEX IF NOT EXISTS idx_profiles_stripe_customer_id ON profiles(stripe_customer_id);
CREATE INDEX IF NOT EXISTS idx_profiles_stripe_subscription_id ON profiles(stripe_subscription_id);

-- Add comment to table
COMMENT ON COLUMN profiles.stripe_customer_id IS 'Stripe customer ID for billing';
COMMENT ON COLUMN profiles.stripe_subscription_id IS 'Current Stripe subscription ID';
COMMENT ON COLUMN profiles.stripe_subscription_status IS 'Current subscription status (active, canceled, incomplete, etc.)';
COMMENT ON COLUMN profiles.subscription_start_date IS 'When the current subscription started';
COMMENT ON COLUMN profiles.subscription_end_date IS 'When the current subscription ends or ended';

