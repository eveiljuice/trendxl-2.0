# 🚨 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ RLS (Row Level Security)

## 🔍 ДИАГНОЗ ПРОБЛЕМЫ

**Симптомы:**
- ✅ Тестовая запись добавляется в `daily_free_analyses`
- ❌ В аккаунте `timolast@example.com` НЕ РАБОТАЕТ ввод ссылки
- ❌ В новых аккаунтах после парсинга НЕ РАБОТАЕТ повторный ввод

**Корень проблемы:**
1. **RLS политики слишком строгие** - блокируют запись через backend с SERVICE_KEY
2. **Backend использует неправильный ключ** - ANON_KEY вместо SERVICE_KEY
3. **Функции без явного search_path** - могут не работать корректно

---

## ✅ РЕШЕНИЕ (ПОШАГОВОЕ)

### Шаг 1: Проверьте переменные окружения в Vercel

1. Откройте **Vercel Dashboard** → ваш проект → **Settings** → **Environment Variables**

2. Проверьте наличие `SUPABASE_SERVICE_KEY`:

   ```bash
   SUPABASE_SERVICE_KEY=eyJ... (очень длинный ключ, ~250+ символов)
   ```

3. **Если НЕТ `SUPABASE_SERVICE_KEY`:**
   - Откройте **Supabase Dashboard** → Settings → API
   - Скопируйте **`service_role` key (secret)** (НЕ anon key!)
   - Добавьте в Vercel как `SUPABASE_SERVICE_KEY`
   - ⚠️ **ВАЖНО:** Это секретный ключ, держите в тайне!

4. **Если есть, но называется по-другому:**
   - Допустимые имена: `SUPABASE_SERVICE_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_KEY`
   - Backend теперь проверяет ВСЕ варианты (исправлено в коде)

### Шаг 2: Примените SQL исправления в Supabase

1. Откройте **Supabase Dashboard** → **SQL Editor**

2. Скопируйте содержимое файла `backend/FINAL_FIX_RLS.sql`

3. Вставьте в SQL Editor и нажмите **Run**

4. **Что делает этот скрипт:**
   - ✅ Удаляет старые RLS политики
   - ✅ Создает новые политики с правильным доступом
   - ✅ Добавляет политику для `service_role` (полный доступ)
   - ✅ Обновляет функции с `SECURITY DEFINER` и `search_path`
   - ✅ Исправляет `can_use_free_trial`, `record_free_trial_usage`, `get_free_trial_info`

5. Проверьте результат (должно быть):
   ```
   ✅ RLS policies updated successfully
   ✅ Functions updated with SECURITY DEFINER
   ✅ Service role has full access
   ✅ Authenticated users can use functions
   ```

### Шаг 3: Отправьте обновленный код

Код уже обновлен и готов к коммиту:

```bash
git add -A
git commit -m "fix: Критическое исправление RLS для free trial системы"
git push origin main
```

---

## 🔧 ЧТО БЫЛО ИСПРАВЛЕНО

### 1. Backend (`backend/supabase_client.py`)

**ДО:**
```python
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
SUPABASE_KEY = SUPABASE_SERVICE_KEY if SUPABASE_SERVICE_KEY else os.getenv("SUPABASE_ANON_KEY", "")
```

**ПОСЛЕ:**
```python
SUPABASE_SERVICE_KEY = (
    os.getenv("SUPABASE_SERVICE_KEY") or 
    os.getenv("SUPABASE_SERVICE_ROLE_KEY") or
    os.getenv("SUPABASE_KEY") or
    os.getenv("SUPABASE_ANON_KEY") or
    ""
)
SUPABASE_KEY = SUPABASE_SERVICE_KEY
```

✅ Теперь проверяет ВСЕ возможные названия переменной
✅ Логирует какой ключ используется (SERVICE_KEY или ANON_KEY)

### 2. RLS Политики (SQL)

**ДО:**
```sql
CREATE POLICY "Users can insert their own free analyses"
    ON public.daily_free_analyses FOR INSERT
    WITH CHECK (auth.uid() = user_id);  -- ❌ Блокирует backend!
```

**ПОСЛЕ:**
```sql
CREATE POLICY "Service role has full access"
    ON public.daily_free_analyses
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);  -- ✅ Backend имеет ПОЛНЫЙ доступ!

CREATE POLICY "Allow insert for authenticated users"
    ON public.daily_free_analyses
    FOR INSERT
    TO authenticated
    WITH CHECK (true);  -- ✅ Проверка в функции, не в политике
```

### 3. Функции (SQL)

**ДО:**
```sql
CREATE OR REPLACE FUNCTION public.record_free_trial_usage(...)
SECURITY DEFINER
AS $$
BEGIN
    INSERT INTO public.daily_free_analyses ...
END;
$$;
```

**ПОСЛЕ:**
```sql
CREATE OR REPLACE FUNCTION public.record_free_trial_usage(...)
SECURITY DEFINER
SET search_path = public  -- ✅ Явно указываем схему
AS $$
BEGIN
    INSERT INTO public.daily_free_analyses ...
    RAISE NOTICE 'Free trial recorded for user: %', p_user_id;  -- ✅ Логирование
END;
$$;
```

---

## 🧪 ТЕСТИРОВАНИЕ

### 1. Проверка в Supabase SQL Editor

```sql
-- 1. Проверьте политики
SELECT schemaname, tablename, policyname, cmd, roles
FROM pg_policies
WHERE tablename = 'daily_free_analyses';

-- Должно показать:
-- - Service role has full access
-- - Users can view their own analyses
-- - Allow insert for authenticated users
-- - Allow update for authenticated users

-- 2. Проверьте функции существуют
SELECT routine_name, routine_type
FROM information_schema.routines
WHERE routine_schema = 'public'
AND routine_name IN ('can_use_free_trial', 'record_free_trial_usage', 'get_free_trial_info');

-- Должно показать все 3 функции

-- 3. Протестируйте запись (замените UUID)
SELECT public.record_free_trial_usage('ВАШ_UUID_СЮДА', 'test_profile');

-- 4. Проверьте данные появились
SELECT * FROM public.daily_free_analyses ORDER BY created_at DESC LIMIT 5;
```

### 2. Проверка на сайте

1. **Откройте сайт** (после деплоя Vercel)
2. **Войдите** в аккаунт `timolast@example.com`
3. **Введите ссылку** на TikTok профиль
4. **После анализа** счетчик должен показать `0/1`
5. **Попробуйте ввести еще раз** - должна появиться кнопка Subscribe

### 3. Проверка логов Vercel

1. Откройте **Vercel Dashboard** → Logs
2. Выполните анализ на сайте
3. Ищите в логах:
   ```
   ✅ Supabase client initialized successfully (using SERVICE_KEY)
   ✅ Recorded free trial usage for user ...
   ```

---

## 📊 ОЖИДАЕМОЕ ПОВЕДЕНИЕ

### Новый пользователь (без подписки):
1. ✅ Видит счетчик: `1/1 Free Today` (фиолетовый блок)
2. ✅ Может ввести ссылку и запустить анализ
3. ✅ После анализа счетчик меняется: `0/1 Used Today` (оранжевый блок)
4. ✅ Поле ввода **БЛОКИРУЕТСЯ**
5. ✅ Кнопка меняется на "Subscribe for Unlimited Access"
6. ✅ Показывается таймер: "Resets in Xh Ym"

### Пользователь с подпиской:
1. ✅ Видит: "✨ Premium Active - Unlimited Scans" (зеленый блок)
2. ✅ Может делать неограниченное количество анализов
3. ✅ Счетчик не показывается

### Admin пользователь:
1. ✅ Видит: "✨ Premium Active - Unlimited Scans" (зеленый блок)
2. ✅ Может делать неограниченное количество анализов
3. ✅ Счетчик не показывается

---

## 🚨 TROUBLESHOOTING

### Проблема: "Supabase client initialized (using ANON_KEY)"

**Решение:**
1. `SUPABASE_SERVICE_KEY` НЕ установлен в Vercel
2. Добавьте переменную в Vercel Environment Variables
3. Передеплойте проект

### Проблема: "INSERT violation of RLS policy"

**Решение:**
1. SQL скрипт `FINAL_FIX_RLS.sql` НЕ применен
2. Примените скрипт в Supabase SQL Editor
3. Проверьте что политики созданы

### Проблема: "Function does not exist"

**Решение:**
1. Функции не созданы или удалены
2. Примените `backend/supabase_free_trial_migration.sql`
3. Затем примените `backend/FINAL_FIX_RLS.sql`

### Проблема: Счетчик не обновляется

**Решение:**
1. Backend не записывает в таблицу
2. Проверьте логи Vercel на ошибки
3. Проверьте что `SUPABASE_SERVICE_KEY` правильный
4. Запустите диагностику SQL в Supabase

---

## ✅ КОНТРОЛЬНЫЙ СПИСОК

Перед тестированием убедитесь:

- [ ] `SUPABASE_SERVICE_KEY` установлен в Vercel
- [ ] SQL скрипт `FINAL_FIX_RLS.sql` применен в Supabase
- [ ] Код закоммичен и отправлен в GitHub
- [ ] Vercel завершил деплой (проверьте статус)
- [ ] Таблица `daily_free_analyses` существует
- [ ] RLS включен на таблице
- [ ] Функции существуют (`can_use_free_trial`, `record_free_trial_usage`, `get_free_trial_info`)
- [ ] Политики созданы (4 политики)

---

**Дата:** 6 октября 2025  
**Приоритет:** 🔴 CRITICAL  
**Время на исправление:** 10-15 минут

