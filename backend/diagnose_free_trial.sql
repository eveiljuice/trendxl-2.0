-- ============================================================================
-- ДИАГНОСТИКА FREE TRIAL СИСТЕМЫ
-- Выполните этот скрипт в Supabase SQL Editor чтобы проверить что работает
-- ============================================================================

-- 1. Проверка существования таблицы
SELECT 
    'Table exists: daily_free_analyses' as check_name,
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'daily_free_analyses'
        ) THEN '✅ YES' 
        ELSE '❌ NO - НУЖНО ВЫПОЛНИТЬ МИГРАЦИЮ!'
    END as result;

-- 2. Проверка записей в таблице
SELECT 
    'Records in daily_free_analyses' as check_name,
    CONCAT('Found: ', COUNT(*), ' records') as result
FROM public.daily_free_analyses;

-- 3. Проверка записей за сегодня
SELECT 
    'Today records' as check_name,
    CONCAT('Found: ', COUNT(*), ' records for today') as result
FROM public.daily_free_analyses
WHERE analysis_date = CURRENT_DATE;

-- 4. Показать все записи (последние 10)
SELECT 
    id,
    user_id,
    analysis_date,
    analysis_count,
    profile_analyzed,
    created_at
FROM public.daily_free_analyses
ORDER BY created_at DESC
LIMIT 10;

-- 5. Проверка существования функций
SELECT 
    routine_name as function_name,
    CASE 
        WHEN routine_name IN ('can_use_free_trial', 'record_free_trial_usage', 'get_free_trial_info') 
        THEN '✅ EXISTS' 
        ELSE '⚠️ CHECK' 
    END as status
FROM information_schema.routines
WHERE routine_schema = 'public'
AND routine_name IN ('can_use_free_trial', 'record_free_trial_usage', 'get_free_trial_info')
ORDER BY routine_name;

-- 6. Проверка RLS политик
SELECT 
    tablename,
    policyname,
    CASE 
        WHEN policyname IS NOT NULL THEN '✅ EXISTS' 
        ELSE '❌ NO POLICIES' 
    END as status
FROM pg_policies
WHERE schemaname = 'public'
AND tablename = 'daily_free_analyses';

-- 7. Тест функции can_use_free_trial для конкретного пользователя
-- ЗАМЕНИТЕ 'YOUR_USER_UUID' на реальный UUID пользователя из auth.users
DO $$
DECLARE
    test_user_id UUID;
    can_use BOOLEAN;
BEGIN
    -- Берем первого пользователя из auth.users для теста
    SELECT id INTO test_user_id FROM auth.users LIMIT 1;
    
    IF test_user_id IS NULL THEN
        RAISE NOTICE '❌ No users found in auth.users';
    ELSE
        -- Проверяем функцию
        SELECT public.can_use_free_trial(test_user_id) INTO can_use;
        RAISE NOTICE '✅ Test user: %', test_user_id;
        RAISE NOTICE '✅ can_use_free_trial returned: %', can_use;
    END IF;
END $$;

-- 8. Проверка синхронизации profiles и auth.users
SELECT 
    'Users sync check' as check_name,
    CONCAT(
        'auth.users: ', (SELECT COUNT(*) FROM auth.users),
        ' | profiles: ', (SELECT COUNT(*) FROM public.profiles),
        CASE 
            WHEN (SELECT COUNT(*) FROM auth.users) = (SELECT COUNT(*) FROM public.profiles) 
            THEN ' ✅ SYNCED' 
            ELSE ' ⚠️ NOT SYNCED' 
        END
    ) as result;

-- ============================================================================
-- РЕКОМЕНДАЦИИ ПО РЕЗУЛЬТАТАМ:
-- ============================================================================
-- 
-- ❌ Если таблица не существует:
--    → Выполните: backend/supabase_free_trial_migration.sql
--
-- ❌ Если функции не существуют:
--    → Выполните: backend/fix_free_trial_null.sql
--
-- ❌ Если нет политик RLS:
--    → Выполните: backend/supabase_free_trial_migration.sql
--
-- ⚠️ Если auth.users и profiles не синхронизированы:
--    → Выполните INSERT из fix_free_trial_null.sql (строки 104-114)
--
-- ✅ Если всё ОК но записи не создаются:
--    → Проверьте логи бекенда на наличие ошибок
--    → Проверьте что SUPABASE_SERVICE_KEY установлен
--
-- ============================================================================

