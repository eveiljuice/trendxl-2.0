-- Migration: Create scan_history table for My Trends feature
-- Description: Creates table to store user's trend analysis history
-- Created: 2025-10-03

-- ============================================================================
-- Table: scan_history
-- Description: Stores complete analysis results for "My Trends" feature
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.scan_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  username TEXT NOT NULL,
  profile_data JSONB NOT NULL,
  scan_type TEXT NOT NULL DEFAULT 'free' CHECK (scan_type IN ('free', 'paid')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for scan_history
CREATE INDEX IF NOT EXISTS idx_scan_history_user_id ON public.scan_history(user_id);
CREATE INDEX IF NOT EXISTS idx_scan_history_username ON public.scan_history(username);
CREATE INDEX IF NOT EXISTS idx_scan_history_created_at ON public.scan_history(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_scan_history_user_date ON public.scan_history(user_id, created_at DESC);

-- Enable Row Level Security
ALTER TABLE public.scan_history ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- RLS Policies for scan_history
-- ============================================================================

-- Drop old policies if they exist
DROP POLICY IF EXISTS "Users can view own scan history" ON public.scan_history;
DROP POLICY IF EXISTS "Users can insert own scans" ON public.scan_history;
DROP POLICY IF EXISTS "Users can delete own scans" ON public.scan_history;
DROP POLICY IF EXISTS "Users can update own scans" ON public.scan_history;

-- Policy: Users can view their own scan history
CREATE POLICY "Users can view own scan history"
  ON public.scan_history
  FOR SELECT
  USING (auth.uid() = user_id);

-- Policy: Users can insert their own scans
CREATE POLICY "Users can insert own scans"
  ON public.scan_history
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

-- Policy: Users can delete their own scans
CREATE POLICY "Users can delete own scans"
  ON public.scan_history
  FOR DELETE
  USING (auth.uid() = user_id);

-- Policy: Users can update their own scans
CREATE POLICY "Users can update own scans"
  ON public.scan_history
  FOR UPDATE
  USING (auth.uid() = user_id);

-- ============================================================================
-- Grants
-- ============================================================================

-- Grant permissions to authenticated users
GRANT ALL ON public.scan_history TO authenticated;

-- Grant permissions to service role
GRANT ALL ON public.scan_history TO service_role;

-- ============================================================================
-- Trigger for updated_at
-- ============================================================================

-- Function to update updated_at timestamp (reuse if exists)
CREATE OR REPLACE FUNCTION update_scan_history_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for scan_history table
DROP TRIGGER IF EXISTS update_scan_history_timestamp ON public.scan_history;
CREATE TRIGGER update_scan_history_timestamp
    BEFORE UPDATE ON public.scan_history
    FOR EACH ROW
    EXECUTE FUNCTION update_scan_history_updated_at();

-- ============================================================================
-- Comments
-- ============================================================================

COMMENT ON TABLE public.scan_history IS 'Stores user scan history with complete analysis data for My Trends feature';
COMMENT ON COLUMN public.scan_history.user_id IS 'Reference to auth.users - user who performed the scan';
COMMENT ON COLUMN public.scan_history.username IS 'TikTok username that was analyzed';
COMMENT ON COLUMN public.scan_history.profile_data IS 'Complete analysis data: profile, trends, hashtags, posts, tokenUsage';
COMMENT ON COLUMN public.scan_history.scan_type IS 'Type of scan: free (daily trial) or paid (subscription)';
COMMENT ON COLUMN public.scan_history.created_at IS 'When the scan was created';
COMMENT ON COLUMN public.scan_history.updated_at IS 'When the scan was last updated';

-- ============================================================================
-- Success Message
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '✅ scan_history table created successfully!';
    RAISE NOTICE '✅ All indexes and RLS policies applied!';
    RAISE NOTICE '✅ Grants configured for authenticated and service_role!';
    RAISE NOTICE '';
    RAISE NOTICE '📊 You can now use the My Trends feature!';
END $$;
