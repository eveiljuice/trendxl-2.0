-- ============================================================================
-- ОЧИСТКА ПЕРЕД ИСПРАВЛЕНИЕМ
-- Выполни СНАЧАЛА этот скрипт, ПОТОМ основной
-- ============================================================================

-- Удалить ВСЕ старые политики
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
        RAISE NOTICE 'Dropped policy: %', r.policyname;
    END LOOP;
    
    RAISE NOTICE '✅ Все старые политики удалены';
END $$;

-- Удалить старые функции
DROP FUNCTION IF EXISTS public.record_free_trial_usage(UUID, TEXT);
DROP FUNCTION IF EXISTS public.can_use_free_trial(UUID);
DROP FUNCTION IF EXISTS public.get_free_trial_info(UUID);

DO $$
BEGIN
    RAISE NOTICE '✅ Все старые функции удалены';
    RAISE NOTICE '👉 Теперь можешь выполнить QUICK_FIX_SUPABASE_FREEMIUM.sql';
END $$;

