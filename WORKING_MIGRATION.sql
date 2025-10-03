-- ============================================================================
-- TrendXL 2.0 Complete Database Migration
-- ============================================================================
-- Run this ONCE in Supabase SQL Editor to create all tables and functions
-- https://supabase.com/dashboard/project/jynidxwtbjrxmsbfpqra/editor
-- ============================================================================

-- STEP 1: Create Tables
-- ============================================================================

-- Create scan_history table
CREATE TABLE IF NOT EXISTS public.scan_history (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  username text NOT NULL,
  profile_data jsonb NOT NULL,
  scan_type text NOT NULL DEFAULT 'free',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

-- Create indexes for scan_history
CREATE INDEX IF NOT EXISTS idx_scan_history_user_id ON public.scan_history(user_id);
CREATE INDEX IF NOT EXISTS idx_scan_history_created_at ON public.scan_history(created_at DESC);

-- Enable RLS for scan_history
ALTER TABLE public.scan_history ENABLE ROW LEVEL SECURITY;

-- Grant permissions for scan_history
GRANT ALL ON public.scan_history TO authenticated;
GRANT ALL ON public.scan_history TO service_role;

-- Create daily_free_analyses table
CREATE TABLE IF NOT EXISTS public.daily_free_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    analysis_date DATE NOT NULL DEFAULT CURRENT_DATE,
    analysis_count INTEGER NOT NULL DEFAULT 0,
    last_analysis_timestamp TIMESTAMPTZ DEFAULT NOW(),
    profile_analyzed TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_user_date UNIQUE(user_id, analysis_date)
);

-- Create indexes for daily_free_analyses
CREATE INDEX IF NOT EXISTS idx_daily_free_analyses_user_id ON public.daily_free_analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_daily_free_analyses_date ON public.daily_free_analyses(analysis_date DESC);

-- Enable RLS for daily_free_analyses
ALTER TABLE public.daily_free_analyses ENABLE ROW LEVEL SECURITY;

-- Grant permissions for daily_free_analyses
GRANT ALL ON public.daily_free_analyses TO authenticated;
GRANT ALL ON public.daily_free_analyses TO service_role;

-- ============================================================================
-- STEP 2: Create RLS Policies
-- ============================================================================

-- Drop old policies if they exist (to avoid errors on re-run)
DROP POLICY IF EXISTS "Users can view own scan history" ON public.scan_history;
DROP POLICY IF EXISTS "Users can insert own scans" ON public.scan_history;
DROP POLICY IF EXISTS "Users can delete own scans" ON public.scan_history;
DROP POLICY IF EXISTS "Users can view their own free analyses" ON public.daily_free_analyses;
DROP POLICY IF EXISTS "Users can insert their own free analyses" ON public.daily_free_analyses;
DROP POLICY IF EXISTS "Users can update their own free analyses" ON public.daily_free_analyses;

-- Create policies for scan_history
CREATE POLICY "Users can view own scan history" ON public.scan_history
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own scans" ON public.scan_history
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own scans" ON public.scan_history
  FOR DELETE USING (auth.uid() = user_id);

-- Create policies for daily_free_analyses
CREATE POLICY "Users can view their own free analyses"
    ON public.daily_free_analyses FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own free analyses"
    ON public.daily_free_analyses FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own free analyses"
    ON public.daily_free_analyses FOR UPDATE USING (auth.uid() = user_id);

-- ============================================================================
-- STEP 3: Create Functions
-- ============================================================================

-- Function: can_use_free_trial
CREATE OR REPLACE FUNCTION public.can_use_free_trial(p_user_id UUID)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_today_count INTEGER;
BEGIN
    SELECT COALESCE(analysis_count, 0) INTO v_today_count
    FROM public.daily_free_analyses
    WHERE user_id = p_user_id AND analysis_date = CURRENT_DATE;
    
    RETURN (v_today_count < 1);
END;
$$;

-- Function: record_free_trial_usage
CREATE OR REPLACE FUNCTION public.record_free_trial_usage(
    p_user_id UUID,
    p_profile_analyzed TEXT DEFAULT NULL
)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    INSERT INTO public.daily_free_analyses (
        user_id, analysis_date, analysis_count, 
        last_analysis_timestamp, profile_analyzed
    ) VALUES (
        p_user_id, CURRENT_DATE, 1, NOW(), p_profile_analyzed
    )
    ON CONFLICT (user_id, analysis_date)
    DO UPDATE SET
        analysis_count = daily_free_analyses.analysis_count + 1,
        last_analysis_timestamp = NOW(),
        profile_analyzed = COALESCE(EXCLUDED.profile_analyzed, daily_free_analyses.profile_analyzed);
END;
$$;

-- Function: get_free_trial_info
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
        COALESCE(today_data.analysis_count, 0)::INTEGER as today_count,
        today_data.last_analysis_timestamp as last_used,
        COALESCE(total_data.total, 0)::INTEGER as total_free_analyses
    FROM (SELECT 1) as dummy
    LEFT JOIN (
        SELECT analysis_count, last_analysis_timestamp
        FROM public.daily_free_analyses
        WHERE user_id = p_user_id AND analysis_date = CURRENT_DATE
    ) today_data ON TRUE
    LEFT JOIN (
        SELECT SUM(analysis_count)::INTEGER as total
        FROM public.daily_free_analyses
        WHERE user_id = p_user_id
    ) total_data ON TRUE;
END;
$$;

-- ============================================================================
-- Migration Complete!
-- ============================================================================
-- You can now:
-- 1. Use the free trial system (1 scan per day)
-- 2. Save and view scan history in My Trends
-- 3. Track user scanning activity
-- ============================================================================
