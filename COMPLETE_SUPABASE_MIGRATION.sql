-- ============================================================================
-- COMPLETE SUPABASE MIGRATION for TrendXL 2.0
-- ============================================================================
-- This migration creates all necessary tables and functions for:
-- 1. Scan History (My Trends feature)
-- 2. Free Trial System (1 free scan per day)
-- ============================================================================

-- ============================================================================
-- PART 1: SCAN HISTORY TABLE
-- ============================================================================

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view own scan history" ON public.scan_history;
DROP POLICY IF EXISTS "Users can insert own scans" ON public.scan_history;
DROP POLICY IF EXISTS "Users can delete own scans" ON public.scan_history;

-- Create scan_history table
CREATE TABLE IF NOT EXISTS public.scan_history (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  username text NOT NULL,
  profile_data jsonb NOT NULL,
  scan_type text NOT NULL DEFAULT 'free' CHECK (scan_type IN ('free', 'paid')),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

-- Drop existing indexes if they exist and recreate
DROP INDEX IF EXISTS public.idx_scan_history_user_id;
DROP INDEX IF EXISTS public.idx_scan_history_created_at;
DROP INDEX IF EXISTS public.idx_scan_history_username;

-- Create indexes for faster lookups
CREATE INDEX idx_scan_history_user_id ON public.scan_history(user_id);
CREATE INDEX idx_scan_history_created_at ON public.scan_history(created_at DESC);
CREATE INDEX idx_scan_history_username ON public.scan_history(username);

-- Enable Row Level Security
ALTER TABLE public.scan_history ENABLE ROW LEVEL SECURITY;

-- Create RLS Policies
CREATE POLICY "Users can view own scan history" ON public.scan_history
  FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own scans" ON public.scan_history
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own scans" ON public.scan_history
  FOR DELETE
  USING (auth.uid() = user_id);

-- Grant permissions to authenticated users
GRANT SELECT, INSERT, DELETE ON public.scan_history TO authenticated;
GRANT USAGE ON SCHEMA public TO authenticated;

-- Add comments
COMMENT ON TABLE public.scan_history IS 'Stores history of TikTok profile scans performed by users';

-- ============================================================================
-- PART 2: FREE TRIAL SYSTEM
-- ============================================================================

-- Drop existing policies
DROP POLICY IF EXISTS "Users can view their own free analyses" ON public.daily_free_analyses;
DROP POLICY IF EXISTS "Users can insert their own free analyses" ON public.daily_free_analyses;
DROP POLICY IF EXISTS "Users can update their own free analyses" ON public.daily_free_analyses;

-- Create daily_free_analyses table
CREATE TABLE IF NOT EXISTS public.daily_free_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    analysis_date DATE DEFAULT CURRENT_DATE,
    analysis_count INTEGER DEFAULT 0,
    last_analysis_timestamp TIMESTAMPTZ DEFAULT NOW(),
    profile_analyzed TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, analysis_date)
);

-- Drop existing indexes if they exist and recreate
DROP INDEX IF EXISTS public.idx_daily_free_analyses_user_id;
DROP INDEX IF EXISTS public.idx_daily_free_analyses_date;
DROP INDEX IF EXISTS public.idx_daily_free_analyses_user_date;

-- Create indexes
CREATE INDEX idx_daily_free_analyses_user_id ON public.daily_free_analyses(user_id);
CREATE INDEX idx_daily_free_analyses_date ON public.daily_free_analyses(analysis_date DESC);
CREATE INDEX idx_daily_free_analyses_user_date ON public.daily_free_analyses(user_id, analysis_date);

-- Enable RLS
ALTER TABLE public.daily_free_analyses ENABLE ROW LEVEL SECURITY;

-- Create RLS Policies
CREATE POLICY "Users can view their own free analyses"
    ON public.daily_free_analyses FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own free analyses"
    ON public.daily_free_analyses FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own free analyses"
    ON public.daily_free_analyses FOR UPDATE
    USING (auth.uid() = user_id);

-- Grant permissions
GRANT ALL ON public.daily_free_analyses TO authenticated;
GRANT ALL ON public.daily_free_analyses TO service_role;

-- Add comments
COMMENT ON TABLE public.daily_free_analyses IS 'Tracks daily free analysis usage for users without subscriptions';

-- ============================================================================
-- PART 3: FREE TRIAL FUNCTIONS
-- ============================================================================

-- Function: Check if user can use free trial
CREATE OR REPLACE FUNCTION public.can_use_free_trial(p_user_id UUID)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_today_count INTEGER;
    v_has_subscription BOOLEAN;
BEGIN
    -- Check if user has active subscription
    SELECT 
        CASE 
            WHEN stripe_subscription_status IN ('active', 'trialing') THEN TRUE
            ELSE FALSE
        END INTO v_has_subscription
    FROM public.profiles
    WHERE id = p_user_id;
    
    -- If user has subscription, they don't need free trial
    IF v_has_subscription THEN
        RETURN FALSE;
    END IF;
    
    -- Check today's free analysis count
    SELECT COALESCE(analysis_count, 0) INTO v_today_count
    FROM public.daily_free_analyses
    WHERE user_id = p_user_id
    AND analysis_date = CURRENT_DATE;
    
    -- User can use free trial if they haven't used it today (< 1)
    RETURN (v_today_count < 1);
END;
$$;

COMMENT ON FUNCTION public.can_use_free_trial IS 'Check if user can use their daily free trial (1 analysis per day)';

-- Function: Record free trial usage
CREATE OR REPLACE FUNCTION public.record_free_trial_usage(
    p_user_id UUID,
    p_profile_analyzed TEXT DEFAULT NULL
)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    -- Insert or update today's record
    INSERT INTO public.daily_free_analyses (
        user_id,
        analysis_date,
        analysis_count,
        last_analysis_timestamp,
        profile_analyzed
    ) VALUES (
        p_user_id,
        CURRENT_DATE,
        1,
        NOW(),
        p_profile_analyzed
    )
    ON CONFLICT (user_id, analysis_date)
    DO UPDATE SET
        analysis_count = daily_free_analyses.analysis_count + 1,
        last_analysis_timestamp = NOW(),
        profile_analyzed = COALESCE(EXCLUDED.profile_analyzed, daily_free_analyses.profile_analyzed);
END;
$$;

COMMENT ON FUNCTION public.record_free_trial_usage IS 'Record a free trial analysis usage';

-- Function: Get user's free trial info
CREATE OR REPLACE FUNCTION public.get_free_trial_info(p_user_id UUID)
RETURNS TABLE (
    can_use_today BOOLEAN,
    today_count INTEGER,
    last_used TIMESTAMPTZ,
    total_free_analyses INTEGER
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        public.can_use_free_trial(p_user_id) as can_use_today,
        COALESCE(dfa_today.analysis_count, 0) as today_count,
        dfa_today.last_analysis_timestamp as last_used,
        COALESCE(dfa_total.total_count, 0) as total_free_analyses
    FROM 
        (SELECT 1) as dummy
    LEFT JOIN (
        SELECT analysis_count, last_analysis_timestamp
        FROM public.daily_free_analyses
        WHERE user_id = p_user_id
        AND analysis_date = CURRENT_DATE
    ) dfa_today ON TRUE
    LEFT JOIN (
        SELECT SUM(analysis_count) as total_count
        FROM public.daily_free_analyses
        WHERE user_id = p_user_id
    ) dfa_total ON TRUE;
END;
$$;

COMMENT ON FUNCTION public.get_free_trial_info IS 'Get detailed information about user free trial usage';

-- Function: Cleanup old free trial records (older than 90 days)
CREATE OR REPLACE FUNCTION public.cleanup_old_free_trial_records()
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM public.daily_free_analyses
    WHERE analysis_date < CURRENT_DATE - INTERVAL '90 days';
END;
$$;

COMMENT ON FUNCTION public.cleanup_old_free_trial_records IS 'Cleanup free trial records older than 90 days';

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- Show created tables
DO $$
BEGIN
    RAISE NOTICE '✅ Migration completed successfully!';
    RAISE NOTICE '';
    RAISE NOTICE 'Created tables:';
    RAISE NOTICE '  - scan_history (for My Trends feature)';
    RAISE NOTICE '  - daily_free_analyses (for free trial tracking)';
    RAISE NOTICE '';
    RAISE NOTICE 'Created functions:';
    RAISE NOTICE '  - can_use_free_trial()';
    RAISE NOTICE '  - record_free_trial_usage()';
    RAISE NOTICE '  - get_free_trial_info()';
    RAISE NOTICE '  - cleanup_old_free_trial_records()';
    RAISE NOTICE '';
    RAISE NOTICE 'All policies and indexes have been created!';
END $$;

-- Verify tables exist
SELECT 
    'scan_history' as table_name,
    COUNT(*) as policy_count
FROM pg_policies 
WHERE tablename = 'scan_history'
UNION ALL
SELECT 
    'daily_free_analyses' as table_name,
    COUNT(*) as policy_count
FROM pg_policies 
WHERE tablename = 'daily_free_analyses';

