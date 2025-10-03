-- ============================================================================
-- ШАГ 2: ДОБАВИТЬ ПОЛИТИКИ (после создания таблиц)
-- ============================================================================
-- Выполните ТОЛЬКО после успешного выполнения MINIMAL_TABLES_ONLY.sql

-- Удаляем старые политики (если есть)
DROP POLICY IF EXISTS "Users can view own scan history" ON public.scan_history;
DROP POLICY IF EXISTS "Users can insert own scans" ON public.scan_history;
DROP POLICY IF EXISTS "Users can delete own scans" ON public.scan_history;
DROP POLICY IF EXISTS "Users can view their own free analyses" ON public.daily_free_analyses;
DROP POLICY IF EXISTS "Users can insert their own free analyses" ON public.daily_free_analyses;
DROP POLICY IF EXISTS "Users can update their own free analyses" ON public.daily_free_analyses;

-- Создаем политики для scan_history
CREATE POLICY "Users can view own scan history" ON public.scan_history
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own scans" ON public.scan_history
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own scans" ON public.scan_history
  FOR DELETE USING (auth.uid() = user_id);

-- Создаем политики для daily_free_analyses
CREATE POLICY "Users can view their own free analyses"
    ON public.daily_free_analyses FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own free analyses"
    ON public.daily_free_analyses FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own free analyses"
    ON public.daily_free_analyses FOR UPDATE USING (auth.uid() = user_id);

