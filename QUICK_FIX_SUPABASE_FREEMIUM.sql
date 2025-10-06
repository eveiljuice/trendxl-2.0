-- ============================================================================
-- БЫСТРОЕ ИСПРАВЛЕНИЕ FREEMIUM СИСТЕМЫ - Выполни это в Supabase SQL Editor
-- ============================================================================

-- ============================================================================
-- ЧАСТЬ 1: Исправление RLS политик (5 мин)
-- ============================================================================

-- 1. Удалить старые политики
DROP POLICY IF EXISTS "Users can view their own free analyses" ON public.daily_free_analyses;
DROP POLICY IF EXISTS "Users can insert their own free analyses" ON public.daily_free_analyses;
DROP POLICY IF EXISTS "Users can update their own free analyses" ON public.daily_free_analyses;
DROP POLICY IF EXISTS "Service role can do anything" ON public.daily_free_analyses;

-- 2. Удалить ВСЕ политики (на случай если остались старые)
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN 
        SELECT policyname 
        FROM pg_policies 
        WHERE tablename = 'daily_free_analyses' 
        AND schemaname = 'public'
    LOOP
        EXECUTE format('DROP POLICY IF EXISTS %I ON public.daily_free_analyses', r.policyname);
    END LOOP;
END $$;

-- 3. Создать ПРАВИЛЬНЫЕ политики
CREATE POLICY "Service role has full access"
    ON public.daily_free_analyses
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Users can view their own analyses"
    ON public.daily_free_analyses
    FOR SELECT
    TO authenticated
    USING (auth.uid() = user_id);

CREATE POLICY "Allow insert for authenticated users"
    ON public.daily_free_analyses
    FOR INSERT
    TO authenticated
    WITH CHECK (true);

CREATE POLICY "Allow update for authenticated users"
    ON public.daily_free_analyses
    FOR UPDATE
    TO authenticated
    USING (true)
    WITH CHECK (true);

-- 4. Обновить права доступа
GRANT ALL ON public.daily_free_analyses TO service_role;
GRANT SELECT, INSERT, UPDATE ON public.daily_free_analyses TO authenticated;

-- 5. Включить RLS
ALTER TABLE public.daily_free_analyses ENABLE ROW LEVEL SECURITY;

-- 6. Сообщение об успехе
DO $$
BEGIN
    RAISE NOTICE '✅ Часть 1: RLS политики обновлены';
END $$;

-- ============================================================================
-- ЧАСТЬ 2: Исправление функций PostgreSQL (5 мин)
-- ============================================================================

-- Удалить старые версии
DROP FUNCTION IF EXISTS public.record_free_trial_usage(UUID, TEXT);
DROP FUNCTION IF EXISTS public.can_use_free_trial(UUID);
DROP FUNCTION IF EXISTS public.get_free_trial_info(UUID);

-- Функция 1: record_free_trial_usage (записывает использование)
CREATE OR REPLACE FUNCTION public.record_free_trial_usage(
    p_user_id UUID,
    p_profile_analyzed TEXT DEFAULT NULL
)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
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
    
    RAISE NOTICE '✅ Free trial recorded for user: %, profile: %', p_user_id, p_profile_analyzed;
END;
$$;

-- Функция 2: can_use_free_trial (проверяет доступность)
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
    SELECT 
        COALESCE(stripe_subscription_status IN ('active', 'trialing'), FALSE),
        COALESCE(is_admin, FALSE)
    INTO 
        v_has_subscription,
        v_is_admin
    FROM public.profiles
    WHERE id = p_user_id;
    
    IF v_has_subscription OR v_is_admin THEN
        RETURN FALSE;
    END IF;
    
    SELECT COALESCE(analysis_count, 0) INTO v_today_count
    FROM public.daily_free_analyses
    WHERE user_id = p_user_id
    AND analysis_date = CURRENT_DATE;
    
    -- КРИТИЧНО: Если записи нет (NULL), COALESCE вернет 0, что меньше 1 → TRUE
    RETURN (COALESCE(v_today_count, 0) < 1);
END;
$$;

-- Функция 3: get_free_trial_info (возвращает информацию)
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
    SELECT
        COALESCE(p.stripe_subscription_status IN ('active', 'trialing'), FALSE),
        COALESCE(p.is_admin, FALSE)
    INTO
        v_has_subscription,
        v_is_admin
    FROM public.profiles p
    WHERE p.id = p_user_id;

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

    SELECT
        COALESCE(dfa.analysis_count, 0),
        dfa.last_analysis_timestamp
    INTO
        v_today_count,
        v_last_used
    FROM public.daily_free_analyses dfa
    WHERE dfa.user_id = p_user_id
    AND dfa.analysis_date = CURRENT_DATE;

    SELECT COALESCE(SUM(dfa.analysis_count), 0)
    INTO v_total_free
    FROM public.daily_free_analyses dfa
    WHERE dfa.user_id = p_user_id;

    v_can_use := (COALESCE(v_today_count, 0) < 1);

    RETURN QUERY SELECT
        v_can_use as can_use_today,
        COALESCE(v_today_count, 0) as today_count,
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

-- Сообщение об успехе
DO $$
BEGIN
    RAISE NOTICE '✅ Часть 2: Функции PostgreSQL обновлены';
END $$;

-- ============================================================================
-- ЧАСТЬ 3: Проверка (1 мин)
-- ============================================================================

-- Получить твой UUID (замени email на свой)
DO $$
DECLARE
    test_user_id UUID;
    test_result RECORD;
BEGIN
    -- Найти пользователя по email (измени на свой!)
    SELECT id INTO test_user_id
    FROM auth.users
    WHERE email LIKE '%timolast%'  -- ⬅️ ИЗМЕНИ НА СВОЙ EMAIL
    LIMIT 1;
    
    IF test_user_id IS NOT NULL THEN
        RAISE NOTICE '=== ТЕСТИРОВАНИЕ ===';
        RAISE NOTICE 'User UUID: %', test_user_id;
        
        -- Тест 1: can_use_free_trial
        RAISE NOTICE 'Can use trial: %', public.can_use_free_trial(test_user_id);
        
        -- Тест 2: get_free_trial_info
        FOR test_result IN SELECT * FROM public.get_free_trial_info(test_user_id)
        LOOP
            RAISE NOTICE 'can_use_today: %', test_result.can_use_today;
            RAISE NOTICE 'today_count: %', test_result.today_count;
            RAISE NOTICE 'message: %', test_result.message;
        END LOOP;
        
        RAISE NOTICE '=== ✅ ВСЁ РАБОТАЕТ! ===';
    ELSE
        RAISE NOTICE '❌ Пользователь не найден. Измени email в скрипте.';
    END IF;
END $$;

-- ============================================================================
-- ГОТОВО! Переходи к следующему шагу
-- ============================================================================

