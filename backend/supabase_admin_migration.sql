-- Migration: Add admin role support to profiles table
-- Date: 2025-01-02
-- Description: Adds is_admin field to track admin users with full access

-- Add is_admin column to profiles table
ALTER TABLE profiles 
ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE;

-- Create index for quick admin lookups
CREATE INDEX IF NOT EXISTS idx_profiles_is_admin ON profiles(is_admin) WHERE is_admin = TRUE;

-- Add comment explaining the field
COMMENT ON COLUMN profiles.is_admin IS 'Admin users have full access to all services without subscription limits';

-- Update RLS policy to allow admins to bypass restrictions (optional)
-- If you want admins to have special database access, uncomment below:
-- DROP POLICY IF EXISTS "Admins can read all profiles" ON profiles;
-- CREATE POLICY "Admins can read all profiles" ON profiles
--   FOR SELECT
--   USING (
--     auth.uid() = id OR 
--     (SELECT is_admin FROM profiles WHERE id = auth.uid()) = TRUE
--   );

