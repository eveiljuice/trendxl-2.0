-- ============================================================================
-- ПРОСТАЯ ПРОВЕРКА FREE TRIAL (выполняйте по одному запросу)
-- ============================================================================

-- ЗАПРОС 1: Проверка таблицы
SELECT 
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'daily_free_analyses'
        ) THEN '✅ Таблица СУЩЕСТВУЕТ' 
        ELSE '❌ Таблица НЕ СУЩЕСТВУЕТ - нужна миграция!'
    END as result;

-- ЗАПРОС 2: Сколько записей в таблице
SELECT COUNT(*) as total_records FROM public.daily_free_analyses;

-- ЗАПРОС 3: Записи за сегодня
SELECT 
    user_id,
    analysis_count,
    profile_analyzed,
    created_at
FROM public.daily_free_analyses
WHERE analysis_date = CURRENT_DATE;

-- ЗАПРОС 4: Проверка функций
SELECT routine_name 
FROM information_schema.routines
WHERE routine_schema = 'public'
AND routine_name IN ('can_use_free_trial', 'record_free_trial_usage', 'get_free_trial_info');

-- ЗАПРОС 5: Тест функции для вашего пользователя
-- ЗАМЕНИТЕ 'YOUR_USER_UUID' на ваш UUID из консоли браузера
SELECT 
    public.can_use_free_trial('YOUR_USER_UUID') as can_use,
    * 
FROM public.get_free_trial_info('YOUR_USER_UUID');

