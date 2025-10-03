# 🚀 БЫСТРЫЙ СТАРТ: Миграция Supabase

## ⚠️ ВАЖНО: Выполняйте по шагам!

### Откройте Supabase SQL Editor:

👉 https://supabase.com/dashboard/project/jynidxwtbjrxmsbfpqra/editor

---

## 📋 ШАГ 1: Создание таблицы scan_history

Скопируйте и запустите:

```sql
CREATE TABLE IF NOT EXISTS public.scan_history (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  username text NOT NULL,
  profile_data jsonb NOT NULL,
  scan_type text NOT NULL DEFAULT 'free',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_scan_history_user_id ON public.scan_history(user_id);
CREATE INDEX IF NOT EXISTS idx_scan_history_created_at ON public.scan_history(created_at DESC);

ALTER TABLE public.scan_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY IF NOT EXISTS "Users can view own scan history" ON public.scan_history
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY IF NOT EXISTS "Users can insert own scans" ON public.scan_history
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY IF NOT EXISTS "Users can delete own scans" ON public.scan_history
  FOR DELETE USING (auth.uid() = user_id);

GRANT SELECT, INSERT, DELETE ON public.scan_history TO authenticated;
```

✅ Должно выполниться успешно!

---

## 📋 ШАГ 2: Создание таблицы daily_free_analyses

Скопируйте и запустите:

```sql
CREATE TABLE IF NOT EXISTS public.daily_free_analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    analysis_date DATE NOT NULL DEFAULT CURRENT_DATE,
    analysis_count INTEGER NOT NULL DEFAULT 0,
    last_analysis_timestamp TIMESTAMPTZ DEFAULT NOW(),
    profile_analyzed TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT unique_user_date UNIQUE(user_id, analysis_date)
);

CREATE INDEX IF NOT EXISTS idx_daily_free_analyses_user_id ON public.daily_free_analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_daily_free_analyses_date ON public.daily_free_analyses(analysis_date DESC);

ALTER TABLE public.daily_free_analyses ENABLE ROW LEVEL SECURITY;

CREATE POLICY IF NOT EXISTS "Users can view their own free analyses"
    ON public.daily_free_analyses FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY IF NOT EXISTS "Users can insert their own free analyses"
    ON public.daily_free_analyses FOR INSERT WITH CHECK (auth.uid() = user_id);

GRANT ALL ON public.daily_free_analyses TO authenticated;
```

✅ Должно выполниться успешно!

---

## 📋 ШАГ 3: Создание функции can_use_free_trial

Скопируйте и запустите:

```sql
CREATE OR REPLACE FUNCTION public.can_use_free_trial(p_user_id UUID)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_today_count INTEGER;
BEGIN
    SELECT COALESCE(analysis_count, 0) INTO v_today_count
    FROM public.daily_free_analyses
    WHERE user_id = p_user_id AND analysis_date = CURRENT_DATE;

    RETURN (v_today_count < 1);
END;
$$;
```

✅ Должно выполниться успешно!

---

## 📋 ШАГ 4: Создание функции record_free_trial_usage

Скопируйте и запустите:

```sql
CREATE OR REPLACE FUNCTION public.record_free_trial_usage(
    p_user_id UUID,
    p_profile_analyzed TEXT DEFAULT NULL
)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    INSERT INTO public.daily_free_analyses (
        user_id, analysis_date, analysis_count,
        last_analysis_timestamp, profile_analyzed
    ) VALUES (
        p_user_id, CURRENT_DATE, 1, NOW(), p_profile_analyzed
    )
    ON CONFLICT (user_id, analysis_date)
    DO UPDATE SET
        analysis_count = public.daily_free_analyses.analysis_count + 1,
        last_analysis_timestamp = NOW();
END;
$$;
```

✅ Должно выполниться успешно!

---

## 📋 ШАГ 5: Создание функции get_free_trial_info

Скопируйте и запустите:

```sql
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
        public.can_use_free_trial(p_user_id) as can_use_today,
        COALESCE(today_data.analysis_count, 0)::INTEGER as today_count,
        today_data.last_analysis_timestamp as last_used,
        COALESCE(total_data.total, 0)::INTEGER as total_free_analyses
    FROM (SELECT 1) as dummy
    LEFT JOIN (
        SELECT analysis_count, last_analysis_timestamp
        FROM public.daily_free_analyses
        WHERE user_id = p_user_id AND analysis_date = CURRENT_DATE
    ) today_data ON TRUE
    LEFT JOIN (
        SELECT SUM(analysis_count)::INTEGER as total
        FROM public.daily_free_analyses
        WHERE user_id = p_user_id
    ) total_data ON TRUE;
END;
$$;
```

✅ Должно выполниться успешно!

---

## 📋 ШАГ 6: ПРОВЕРКА

Скопируйте и запустите для проверки:

```sql
SELECT
    'scan_history' as table_name,
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'scan_history'
    ) THEN '✅ EXISTS' ELSE '❌ NOT FOUND' END as status
UNION ALL
SELECT
    'daily_free_analyses' as table_name,
    CASE WHEN EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'public' AND table_name = 'daily_free_analyses'
    ) THEN '✅ EXISTS' ELSE '❌ NOT FOUND' END as status
UNION ALL
SELECT
    'can_use_free_trial()' as table_name,
    CASE WHEN EXISTS (
        SELECT 1 FROM pg_proc WHERE proname = 'can_use_free_trial'
    ) THEN '✅ EXISTS' ELSE '❌ NOT FOUND' END as status
UNION ALL
SELECT
    'get_free_trial_info()' as table_name,
    CASE WHEN EXISTS (
        SELECT 1 FROM pg_proc WHERE proname = 'get_free_trial_info'
    ) THEN '✅ EXISTS' ELSE '❌ NOT FOUND' END as status;
```

Вы должны увидеть:

```
table_name              | status
------------------------|-----------
scan_history            | ✅ EXISTS
daily_free_analyses     | ✅ EXISTS
can_use_free_trial()    | ✅ EXISTS
get_free_trial_info()   | ✅ EXISTS
```

---

## 🎉 ГОТОВО!

После успешного выполнения всех шагов:

- ✅ Ошибка 404 исчезнет
- ✅ Счетчик free scans заработает
- ✅ My Trends покажет историю
- ✅ Все функции работают

Перезагрузите приложение и проверьте!
