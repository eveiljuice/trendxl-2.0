-- ============================================================================
-- ПРОВЕРКА: Работает ли freemium система в Supabase
-- Выполни это ПОСЛЕ основного скрипта для проверки
-- ============================================================================

-- Шаг 1: Найди свой UUID (измени email!)
SELECT 
    id as user_uuid,
    email,
    created_at
FROM auth.users
WHERE email LIKE '%timolast%'  -- ⬅️ ИЗМЕНИ НА СВОЙ EMAIL
LIMIT 1;

-- 👆 СКОПИРУЙ UUID из результата выше и вставь его ниже вместо 'YOUR_UUID_HERE'

-- ============================================================================
-- Шаг 2: Проверь функцию get_free_trial_info
-- ============================================================================

SELECT * FROM public.get_free_trial_info('YOUR_UUID_HERE');

-- ✅ Должно вернуть:
-- can_use_today: true (если не использовал сегодня) или false
-- today_count: 0 или 1
-- daily_limit: 1
-- has_subscription: false (если нет подписки)
-- message: "You have 1 free analysis available today"

-- ============================================================================
-- Шаг 3: Проверь функцию can_use_free_trial
-- ============================================================================

SELECT public.can_use_free_trial('YOUR_UUID_HERE') as can_use;

-- ✅ Должно вернуть: true (если можешь использовать) или false

-- ============================================================================
-- Шаг 4: Проверь записи в таблице
-- ============================================================================

SELECT 
    user_id,
    analysis_date,
    analysis_count,
    profile_analyzed,
    last_analysis_timestamp,
    created_at
FROM public.daily_free_analyses
WHERE user_id = 'YOUR_UUID_HERE'
ORDER BY analysis_date DESC
LIMIT 5;

-- ✅ Должно показать твои записи (если уже делал анализ)
-- Или быть пустым (если еще не делал)

-- ============================================================================
-- Шаг 5: Проверь политики RLS
-- ============================================================================

SELECT 
    schemaname,
    tablename,
    policyname,
    cmd,
    roles,
    qual,
    with_check
FROM pg_policies
WHERE tablename = 'daily_free_analyses'
ORDER BY policyname;

-- ✅ Должно показать 4 политики:
-- 1. "Allow insert for authenticated users"
-- 2. "Allow update for authenticated users"
-- 3. "Service role has full access"
-- 4. "Users can view their own analyses"

-- ============================================================================
-- Шаг 6: Проверь что функции существуют
-- ============================================================================

SELECT 
    routine_name,
    routine_type,
    data_type as return_type
FROM information_schema.routines
WHERE routine_schema = 'public'
AND routine_name IN ('can_use_free_trial', 'record_free_trial_usage', 'get_free_trial_info')
ORDER BY routine_name;

-- ✅ Должно показать все 3 функции

-- ============================================================================
-- Шаг 7: ТЕСТОВАЯ ЗАПИСЬ (опционально)
-- ============================================================================

-- ТОЛЬКО ДЛЯ ТЕСТА! Создает тестовую запись
-- РАСКОММЕНТИРУЙ если хочешь протестировать запись:

-- SELECT public.record_free_trial_usage('YOUR_UUID_HERE', 'test_profile_manual');

-- Потом проверь что запись появилась:
-- SELECT * FROM public.daily_free_analyses WHERE user_id = 'YOUR_UUID_HERE';

-- ============================================================================
-- ✅ ЕСЛИ ВСЁ РАБОТАЕТ:
-- 1. Проверь переменные в Vercel (SUPABASE_SERVICE_KEY)
-- 2. Закоммить изменения: git commit + git push
-- 3. Протестируй на сайте после деплоя
-- ============================================================================

