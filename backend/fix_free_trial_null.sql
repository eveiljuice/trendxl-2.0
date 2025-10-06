-- Fix для проблемы can_use_free_trial возвращающей NULL
-- Проблема: функция может возвращать NULL если профиль пользователя не найден

-- 1. Обновленная функция can_use_free_trial с правильной обработкой NULL
CREATE OR REPLACE FUNCTION public.can_use_free_trial(p_user_id UUID)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_today_count INTEGER;
    v_has_subscription BOOLEAN;
    v_user_exists BOOLEAN;
BEGIN
    -- Check if user exists in profiles table
    SELECT EXISTS(
        SELECT 1 FROM public.profiles WHERE id = p_user_id
    ) INTO v_user_exists;
    
    -- If user doesn't exist in profiles, check auth.users
    IF NOT v_user_exists THEN
        SELECT EXISTS(
            SELECT 1 FROM auth.users WHERE id = p_user_id
        ) INTO v_user_exists;
        
        -- If user exists in auth but not in profiles, they can use free trial
        IF v_user_exists THEN
            RETURN TRUE;
        ELSE
            -- User doesn't exist at all
            RETURN FALSE;
        END IF;
    END IF;
    
    -- Check if user has active subscription
    SELECT 
        CASE 
            WHEN stripe_subscription_status IN ('active', 'trialing') THEN TRUE
            ELSE FALSE
        END INTO v_has_subscription
    FROM public.profiles
    WHERE id = p_user_id;
    
    -- If no subscription status found, default to FALSE
    v_has_subscription := COALESCE(v_has_subscription, FALSE);
    
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
    RETURN (COALESCE(v_today_count, 0) < 1);
END;
$$;

-- 2. Обновленная функция get_free_trial_info для правильной обработки NULL
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
        COALESCE(public.can_use_free_trial(p_user_id), TRUE) as can_use_today,
        COALESCE(dfa_today.analysis_count, 0)::INTEGER as today_count,
        dfa_today.last_analysis_timestamp as last_used,
        COALESCE(dfa_total.total_count, 0)::INTEGER as total_free_analyses
    FROM 
        (SELECT 1) as dummy
    LEFT JOIN (
        SELECT analysis_count, last_analysis_timestamp
        FROM public.daily_free_analyses
        WHERE user_id = p_user_id
        AND analysis_date = CURRENT_DATE
    ) dfa_today ON TRUE
    LEFT JOIN (
        SELECT SUM(analysis_count)::INTEGER as total_count
        FROM public.daily_free_analyses
        WHERE user_id = p_user_id
    ) dfa_total ON TRUE;
END;
$$;

-- 3. Проверка что таблица profiles синхронизирована с auth.users
-- Если пользователь есть в auth.users но нет в profiles, создаем запись

INSERT INTO public.profiles (id, email, username, created_at, updated_at)
SELECT 
    au.id,
    au.email,
    COALESCE(au.raw_user_meta_data->>'username', SPLIT_PART(au.email, '@', 1)) as username,
    au.created_at,
    NOW() as updated_at
FROM auth.users au
LEFT JOIN public.profiles p ON p.id = au.id
WHERE p.id IS NULL
ON CONFLICT (id) DO NOTHING;

-- Comments
COMMENT ON FUNCTION public.can_use_free_trial IS 'Check if user can use their daily free trial (1 analysis per day) - Returns boolean, never NULL';
COMMENT ON FUNCTION public.get_free_trial_info IS 'Get detailed information about user free trial usage - Handles NULL values properly';

