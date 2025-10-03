# Инструкция по применению миграции Supabase для TrendXL

## ⚠️ ВАЖНО: Эту миграцию нужно выполнить вручную!

Эта миграция создает:

1. **Таблицу `scan_history`** - для работы функции "My Trends"
2. **Таблицу `daily_free_analyses`** - для подсчета бесплатных попыток
3. **Функции для free trial** - проверка, запись и получение информации о пробных периодах

## Шаги для выполнения:

### Вариант 1: Через Supabase Dashboard (Рекомендуется)

1. Откройте [Supabase Dashboard](https://supabase.com/dashboard/project/jynidxwtbjrxmsbfpqra/editor)
2. Перейдите в **SQL Editor** (слева в меню)
3. Нажмите **New Query**
4. Скопируйте и вставьте SQL код из файла **`COMPLETE_SUPABASE_MIGRATION.sql`** (в корне проекта)
5. Нажмите **Run** или `Ctrl+Enter`

### Вариант 2: Через Supabase CLI (если установлен)

```bash
# Перейдите в директорию проекта
cd "C:\Users\ok\Desktop\timo\trendxl 2.0"

# Примените миграцию
supabase db push
```

## Проверка успешности

После выполнения миграции проверьте:

1. В Supabase Dashboard перейдите в **Table Editor**
2. Убедитесь что таблица `scan_history` появилась
3. Проверьте что у неё есть следующие столбцы:

   - id (uuid)
   - user_id (uuid)
   - username (text)
   - profile_data (jsonb)
   - scan_type (text)
   - created_at (timestamptz)
   - updated_at (timestamptz)

4. Проверьте что включен Row Level Security (RLS):
   - Откройте таблицу scan_history
   - Перейдите на вкладку **Policies**
   - Должны быть 3 политики:
     - "Users can view own scan history"
     - "Users can insert own scans"
     - "Users can delete own scans"

## Что делать если возникла ошибка

Если при выполнении SQL возникла ошибка:

1. Убедитесь что вы вошли в правильный проект Supabase
2. Проверьте что у вас есть права на создание таблиц
3. Если таблица уже существует, сначала удалите её:
   ```sql
   DROP TABLE IF EXISTS public.scan_history CASCADE;
   ```
   Затем повторите выполнение миграции

## После успешного выполнения

1. Перезагрузите приложение
2. Выполните сканирование любого TikTok профиля
3. Перейдите в раздел "My Trends" в меню
4. Вы должны увидеть сохраненное сканирование

## SQL код для копирования

```sql
-- Create scan_history table to store user's TikTok profile scans
CREATE TABLE IF NOT EXISTS public.scan_history (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  username text NOT NULL,
  profile_data jsonb NOT NULL,
  scan_type text NOT NULL DEFAULT 'free' CHECK (scan_type IN ('free', 'paid')),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_scan_history_user_id ON public.scan_history(user_id);
CREATE INDEX IF NOT EXISTS idx_scan_history_created_at ON public.scan_history(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_scan_history_username ON public.scan_history(username);

-- Enable Row Level Security
ALTER TABLE public.scan_history ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own scan history" ON public.scan_history
  FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own scans" ON public.scan_history
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own scans" ON public.scan_history
  FOR DELETE
  USING (auth.uid() = user_id);

-- Grant permissions to authenticated users
GRANT SELECT, INSERT, DELETE ON public.scan_history TO authenticated;
GRANT USAGE ON SCHEMA public TO authenticated;
```
