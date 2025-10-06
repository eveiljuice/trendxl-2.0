-- ============================================================================
-- ИСПРАВЛЕНИЕ: can_use_free_trial возвращает NULL для новых пользователей
-- Проблема: Новый пользователь не может сделать ПЕРВЫЙ анализ
-- Решение: Возвращать TRUE если записи нет (новый пользователь)
-- ============================================================================

-- Шаг 1: Исправить can_use_free_trial
CREATE OR REPLACE FUNCTION public.can_use_free_trial(p_user_id UUID)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_today_count INTEGER;
    v_has_subscription BOOLEAN;
    v_is_admin BOOLEAN;
BEGIN
    -- Проверяем подписку и admin статус
    SELECT 
        COALESCE(stripe_subscription_status IN ('active', 'trialing'), FALSE),
        COALESCE(is_admin, FALSE)
    INTO 
        v_has_subscription,
        v_is_admin
    FROM public.profiles
    WHERE id = p_user_id;
    
    -- Admin или подписка = неограниченный доступ (не используют free trial)
    IF v_has_subscription OR v_is_admin THEN
        RETURN FALSE;
    END IF;
    
    -- Проверяем использование за сегодня
    SELECT COALESCE(analysis_count, 0) INTO v_today_count
    FROM public.daily_free_analyses
    WHERE user_id = p_user_id
    AND analysis_date = CURRENT_DATE;
    
    -- КРИТИЧНО: Если v_today_count NULL (нет записи), значит новый пользователь
    -- NULL означает что SELECT ничего не нашел, COALESCE превратит в 0
    -- 0 < 1 = TRUE → пользователь может использовать free trial
    RETURN (COALESCE(v_today_count, 0) < 1);
END;
$$;

-- Шаг 2: Исправить get_free_trial_info
CREATE OR REPLACE FUNCTION public.get_free_trial_info(p_user_id UUID)
RETURNS TABLE (
    can_use_today BOOLEAN,
    today_count INTEGER,
    last_used TIMESTAMPTZ,
    total_free_analyses INTEGER,
    has_subscription BOOLEAN,
    is_admin BOOLEAN,
    daily_limit INTEGER,
    message TEXT
)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_can_use BOOLEAN;
    v_today_count INTEGER;
    v_last_used TIMESTAMPTZ;
    v_total_free INTEGER;
    v_has_subscription BOOLEAN;
    v_is_admin BOOLEAN;
BEGIN
    -- Получаем статус подписки и admin
    SELECT
        COALESCE(p.stripe_subscription_status IN ('active', 'trialing'), FALSE),
        COALESCE(p.is_admin, FALSE)
    INTO
        v_has_subscription,
        v_is_admin
    FROM public.profiles p
    WHERE p.id = p_user_id;

    -- Если подписка или admin - неограниченный доступ
    IF v_has_subscription OR v_is_admin THEN
        RETURN QUERY SELECT
            FALSE as can_use_today,
            0 as today_count,
            NULL::TIMESTAMPTZ as last_used,
            0 as total_free_analyses,
            TRUE as has_subscription,
            v_is_admin as is_admin,
            1 as daily_limit,
            'You have unlimited access' as message;
        RETURN;
    END IF;

    -- Получаем данные о free trial (может быть NULL если новый пользователь)
    SELECT
        COALESCE(dfa.analysis_count, 0),  -- Если NULL (нет записи) → 0
        dfa.last_analysis_timestamp
    INTO
        v_today_count,
        v_last_used
    FROM public.daily_free_analyses dfa
    WHERE dfa.user_id = p_user_id
    AND dfa.analysis_date = CURRENT_DATE;

    -- КРИТИЧНО: Если v_today_count NULL, это новый пользователь
    -- Устанавливаем значения по умолчанию
    v_today_count := COALESCE(v_today_count, 0);

    -- Общее количество использований
    SELECT COALESCE(SUM(dfa.analysis_count), 0)
    INTO v_total_free
    FROM public.daily_free_analyses dfa
    WHERE dfa.user_id = p_user_id;

    -- Проверяем можно ли использовать сегодня
    v_can_use := (v_today_count < 1);

    RETURN QUERY SELECT
        v_can_use as can_use_today,
        v_today_count as today_count,
        v_last_used as last_used,
        v_total_free as total_free_analyses,
        FALSE as has_subscription,
        v_is_admin as is_admin,
        1 as daily_limit,
        CASE
            WHEN v_can_use THEN 'You have 1 free analysis available today'
            ELSE 'You''ve used your free daily analysis. Subscribe for unlimited access!'
        END as message;
END;
$$;

-- Шаг 3: Тестирование
DO $$
DECLARE
    test_user_id UUID;
    test_result RECORD;
BEGIN
    -- Получаем ID нового пользователя (или создаем тестового)
    SELECT id INTO test_user_id
    FROM auth.users
    WHERE email = 'timolastcommit@example.com'
    LIMIT 1;
    
    IF test_user_id IS NOT NULL THEN
        -- Тест 1: Проверяем can_use_free_trial
        RAISE NOTICE '=== TEST 1: can_use_free_trial ===';
        RAISE NOTICE 'User ID: %', test_user_id;
        RAISE NOTICE 'Can use trial: %', public.can_use_free_trial(test_user_id);
        
        -- Тест 2: Проверяем get_free_trial_info
        RAISE NOTICE '=== TEST 2: get_free_trial_info ===';
        FOR test_result IN 
            SELECT * FROM public.get_free_trial_info(test_user_id)
        LOOP
            RAISE NOTICE 'can_use_today: %', test_result.can_use_today;
            RAISE NOTICE 'today_count: %', test_result.today_count;
            RAISE NOTICE 'total_free_analyses: %', test_result.total_free_analyses;
            RAISE NOTICE 'has_subscription: %', test_result.has_subscription;
            RAISE NOTICE 'message: %', test_result.message;
        END LOOP;
    ELSE
        RAISE NOTICE 'User not found. Please replace email in script.';
    END IF;
    
    RAISE NOTICE '=== ✅ Functions updated successfully ===';
END $$;

-- Комментарии
COMMENT ON FUNCTION public.can_use_free_trial IS 'Returns TRUE for new users (no record in daily_free_analyses), FALSE if used today or has subscription';
COMMENT ON FUNCTION public.get_free_trial_info IS 'Returns complete free trial info, handling NULL values for new users correctly';

