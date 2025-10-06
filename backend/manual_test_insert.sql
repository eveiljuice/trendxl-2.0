-- ============================================================================
-- РУЧНОЕ ДОБАВЛЕНИЕ ТЕСТОВОЙ ЗАПИСИ FREE TRIAL
-- Это покажет работает ли вообще запись в таблицу
-- ============================================================================

-- Шаг 1: Отключите RLS временно (для теста)
ALTER TABLE public.daily_free_analyses DISABLE ROW LEVEL SECURITY;

-- Шаг 2: Получите UUID вашего пользователя
SELECT 
    id as user_uuid,
    email
FROM auth.users
WHERE email LIKE '%timolast%'  -- Замените на часть вашего email
LIMIT 1;

-- Шаг 3: Вручную добавьте запись (ЗАМЕНИТЕ UUID на ваш из Шага 2)
INSERT INTO public.daily_free_analyses (
    user_id,
    analysis_date,
    analysis_count,
    profile_analyzed,
    last_analysis_timestamp
) VALUES (
    'PASTE_YOUR_UUID_HERE',  -- ⬅️ ВСТАВЬТЕ UUID из Шага 2
    CURRENT_DATE,
    1,
    'test_profile',
    NOW()
);

-- Шаг 4: Проверьте что запись создалась
SELECT * FROM public.daily_free_analyses;

-- Шаг 5: Протестируйте функцию с вашим UUID
SELECT 
    public.can_use_free_trial('PASTE_YOUR_UUID_HERE') as can_use_trial,
    *
FROM public.get_free_trial_info('PASTE_YOUR_UUID_HERE');

-- Должно показать:
-- can_use_trial: false (так как запись уже есть)
-- today_count: 1
-- daily_limit: 1

-- ============================================================================
-- ЕСЛИ ЭТО СРАБОТАЛО, ПРОБЛЕМА В БЕКЕНДЕ!
-- ============================================================================
-- 
-- Значит функция record_free_trial_usage НЕ ВЫЗЫВАЕТСЯ или падает с ошибкой
-- 
-- РЕШЕНИЕ:
-- 1. Проверьте что бекенд ДЕЙСТВИТЕЛЬНО вызывает функцию
-- 2. Проверьте переменные окружения в Vercel:
--    - SUPABASE_URL
--    - SUPABASE_SERVICE_KEY (не обычный KEY!)
-- 3. Посмотрите логи в Vercel Dashboard (не через CLI)
--
-- ============================================================================

-- После теста включите RLS обратно!
ALTER TABLE public.daily_free_analyses ENABLE ROW LEVEL SECURITY;

