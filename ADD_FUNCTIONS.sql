-- ============================================================================
-- ШАГ 3: ДОБАВИТЬ ФУНКЦИИ (после создания таблиц и политик)
-- ============================================================================
-- Выполните ТОЛЬКО после успешного выполнения предыдущих шагов

-- Функция 1: can_use_free_trial
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

-- Функция 2: record_free_trial_usage
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

-- Функция 3: get_free_trial_info
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

-- Комментарии
COMMENT ON FUNCTION public.can_use_free_trial IS 'Check if user can use free trial today';
COMMENT ON FUNCTION public.record_free_trial_usage IS 'Record free trial usage';
COMMENT ON FUNCTION public.get_free_trial_info IS 'Get user free trial info';

