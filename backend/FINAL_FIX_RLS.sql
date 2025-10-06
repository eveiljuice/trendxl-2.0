-- ============================================================================
-- КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ RLS ДЛЯ FREE TRIAL СИСТЕМЫ
-- Проблема: RLS блокирует запись через backend с SERVICE KEY
-- Решение: Обновить политики + добавить политику для service_role
-- ============================================================================

-- Шаг 1: Удалить старые политики
DROP POLICY IF EXISTS "Users can view their own free analyses" ON public.daily_free_analyses;
DROP POLICY IF EXISTS "Users can insert their own free analyses" ON public.daily_free_analyses;
DROP POLICY IF EXISTS "Users can update their own free analyses" ON public.daily_free_analyses;
DROP POLICY IF EXISTS "Service role can do anything" ON public.daily_free_analyses;

-- Шаг 2: Создать ПРАВИЛЬНЫЕ политики

-- Политика для service_role (backend с SERVICE_KEY) - ПОЛНЫЙ ДОСТУП
CREATE POLICY "Service role has full access"
    ON public.daily_free_analyses
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Политика для authenticated пользователей - только свои данные
CREATE POLICY "Users can view their own analyses"
    ON public.daily_free_analyses
    FOR SELECT
    TO authenticated
    USING (auth.uid() = user_id);

-- Политика для INSERT через функции (с SECURITY DEFINER)
CREATE POLICY "Allow insert for authenticated users"
    ON public.daily_free_analyses
    FOR INSERT
    TO authenticated
    WITH CHECK (true);  -- Проверка идет в функции

-- Политика для UPDATE через функции (с SECURITY DEFINER)
CREATE POLICY "Allow update for authenticated users"
    ON public.daily_free_analyses
    FOR UPDATE
    TO authenticated
    USING (true)  -- Проверка идет в функции
    WITH CHECK (true);

-- Шаг 3: Обновить GRANTS
GRANT ALL ON public.daily_free_analyses TO service_role;
GRANT SELECT, INSERT, UPDATE ON public.daily_free_analyses TO authenticated;

-- Шаг 4: Убедиться что RLS включен
ALTER TABLE public.daily_free_analyses ENABLE ROW LEVEL SECURITY;

-- Шаг 5: УДАЛИТЬ старые функции (если существуют с другой сигнатурой)
DROP FUNCTION IF EXISTS public.record_free_trial_usage(UUID, TEXT);
DROP FUNCTION IF EXISTS public.can_use_free_trial(UUID);
DROP FUNCTION IF EXISTS public.get_free_trial_info(UUID);

-- Шаг 6: Создать функцию record_free_trial_usage с правильной сигнатурой
CREATE OR REPLACE FUNCTION public.record_free_trial_usage(
    p_user_id UUID,
    p_profile_analyzed TEXT DEFAULT NULL
)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER  -- Выполняется с правами владельца функции
SET search_path = public  -- Явно указываем search_path
AS $$
BEGIN
    -- Вставить или обновить запись за сегодня
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
    
    -- Логируем для отладки
    RAISE NOTICE 'Free trial recorded for user: %, profile: %', p_user_id, p_profile_analyzed;
END;
$$;

-- Шаг 7: Создать can_use_free_trial для корректной работы
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
    
    -- Admin или подписка = неограниченный доступ
    IF v_has_subscription OR v_is_admin THEN
        RETURN FALSE;  -- Не используют free trial
    END IF;
    
    -- Проверяем использование за сегодня
    SELECT COALESCE(analysis_count, 0) INTO v_today_count
    FROM public.daily_free_analyses
    WHERE user_id = p_user_id
    AND analysis_date = CURRENT_DATE;
    
    -- Можно использовать если меньше 1
    RETURN (v_today_count < 1);
END;
$$;

-- Шаг 8: Создать get_free_trial_info с новой сигнатурой
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

    -- Получаем данные о free trial
    SELECT
        COALESCE(dfa.analysis_count, 0),
        dfa.last_analysis_timestamp
    INTO
        v_today_count,
        v_last_used
    FROM public.daily_free_analyses dfa
    WHERE dfa.user_id = p_user_id
    AND dfa.analysis_date = CURRENT_DATE;

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

-- Шаг 9: Проверка что все работает
DO $$
BEGIN
    RAISE NOTICE '✅ RLS policies updated successfully';
    RAISE NOTICE '✅ Functions updated with SECURITY DEFINER';
    RAISE NOTICE '✅ Service role has full access';
    RAISE NOTICE '✅ Authenticated users can use functions';
END $$;

-- Комментарии
COMMENT ON POLICY "Service role has full access" ON public.daily_free_analyses 
    IS 'Backend with SERVICE_KEY can bypass RLS for all operations';
    
COMMENT ON POLICY "Users can view their own analyses" ON public.daily_free_analyses 
    IS 'Users can only view their own free trial records';
    
COMMENT ON POLICY "Allow insert for authenticated users" ON public.daily_free_analyses 
    IS 'Allow insert through SECURITY DEFINER functions';
    
COMMENT ON POLICY "Allow update for authenticated users" ON public.daily_free_analyses 
    IS 'Allow update through SECURITY DEFINER functions';

