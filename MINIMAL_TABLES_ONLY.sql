-- ============================================================================
-- ШАБЛОН 1: ТОЛЬКО ТАБЛИЦЫ (без функций и политик)
-- ============================================================================
-- Скопируйте и запустите ТОЛЬКО ЭТО:

-- Таблица 1: scan_history
CREATE TABLE IF NOT EXISTS public.scan_history (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  username text NOT NULL,
  profile_data jsonb NOT NULL,
  scan_type text NOT NULL DEFAULT 'free',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

-- Таблица 2: daily_free_analyses
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

-- Индексы
CREATE INDEX IF NOT EXISTS idx_scan_history_user_id ON public.scan_history(user_id);
CREATE INDEX IF NOT EXISTS idx_scan_history_created_at ON public.scan_history(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_daily_free_analyses_user_id ON public.daily_free_analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_daily_free_analyses_date ON public.daily_free_analyses(analysis_date DESC);

-- Включаем RLS
ALTER TABLE public.scan_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.daily_free_analyses ENABLE ROW LEVEL SECURITY;

-- Права доступа
GRANT ALL ON public.scan_history TO authenticated;
GRANT ALL ON public.daily_free_analyses TO authenticated;
GRANT ALL ON public.scan_history TO service_role;
GRANT ALL ON public.daily_free_analyses TO service_role;

