-- Migration: Add Free Trial System (1 free analysis per day)
-- Description: Allows new users to test the product with 1 free analysis per day
-- Created: 2025-10-03

-- ============================================================================
-- Table: daily_free_analyses
-- Description: Tracks daily free analysis usage for users
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.daily_free_analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    analysis_date DATE DEFAULT CURRENT_DATE,
    analysis_count INTEGER DEFAULT 0,
    last_analysis_timestamp TIMESTAMPTZ DEFAULT NOW(),
    profile_analyzed TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, analysis_date)
);

-- Create indexes for daily_free_analyses table
CREATE INDEX IF NOT EXISTS idx_daily_free_analyses_user_id ON public.daily_free_analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_daily_free_analyses_date ON public.daily_free_analyses(analysis_date DESC);
CREATE INDEX IF NOT EXISTS idx_daily_free_analyses_user_date ON public.daily_free_analyses(user_id, analysis_date);

-- Enable RLS
ALTER TABLE public.daily_free_analyses ENABLE ROW LEVEL SECURITY;

-- Policies for daily_free_analyses
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

-- ============================================================================
-- Function: Check if user can use free trial
-- ============================================================================
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

-- ============================================================================
-- Function: Record free trial usage
-- ============================================================================
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

-- ============================================================================
-- Function: Get user's free trial info
-- ============================================================================
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

-- ============================================================================
-- Function: Cleanup old free trial records (older than 90 days)
-- ============================================================================
CREATE OR REPLACE FUNCTION public.cleanup_old_free_trial_records()
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM public.daily_free_analyses
    WHERE analysis_date < CURRENT_DATE - INTERVAL '90 days';
END;
$$;

-- Comments
COMMENT ON TABLE public.daily_free_analyses IS 'Tracks daily free analysis usage for users without subscriptions';
COMMENT ON FUNCTION public.can_use_free_trial IS 'Check if user can use their daily free trial (1 analysis per day)';
COMMENT ON FUNCTION public.record_free_trial_usage IS 'Record a free trial analysis usage';
COMMENT ON FUNCTION public.get_free_trial_info IS 'Get detailed information about user free trial usage';
COMMENT ON FUNCTION public.cleanup_old_free_trial_records IS 'Cleanup free trial records older than 90 days';

