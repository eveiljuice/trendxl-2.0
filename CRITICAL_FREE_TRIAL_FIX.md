# 🚨 КРИТИЧЕСКАЯ ПРОБЛЕМА: Free Trial не работает

## ❌ Симптомы

Пользователь может делать НЕОГРАНИЧЕННОЕ количество анализов, хотя должен быть лимит 1 в день.

## 🔍 Диагностика

### Шаг 1: Проверьте БД в Supabase

1. Откройте **Supabase Dashboard** → **SQL Editor**
2. Скопируйте и выполните содержимое файла `backend/diagnose_free_trial.sql`
3. Посмотрите результаты:

**Что проверяет скрипт:**
- ✅ Существует ли таблица `daily_free_analyses`
- ✅ Есть ли записи в таблице
- ✅ Существуют ли функции (`can_use_free_trial`, `record_free_trial_usage`, `get_free_trial_info`)
- ✅ Настроены ли RLS политики
- ✅ Синхронизированы ли `auth.users` и `profiles`

### Шаг 2: Исправление на основе диагностики

#### Проблема 1: Таблица не существует
```
❌ Table exists: daily_free_analyses -> NO
```

**Решение:**
1. Откройте **Supabase Dashboard** → **SQL Editor**
2. Выполните файл `backend/supabase_free_trial_migration.sql`

#### Проблема 2: Функции не существуют
```
❌ Functions: can_use_free_trial -> NOT FOUND
```

**Решение:**
1. Выполните файл `backend/fix_free_trial_null.sql` в SQL Editor

#### Проблема 3: RLS политики отсутствуют
```
❌ NO POLICIES found for daily_free_analyses
```

**Решение:**
1. Выполните секцию с политиками из `backend/supabase_free_trial_migration.sql` (строки 26-42)

#### Проблема 4: Нет записей в таблице
```
✅ Таблица есть, функции есть, но записей нет
```

**Возможные причины:**

**A. Проблема с RLS политиками**

Функция `record_free_trial_usage` выполняется с `SECURITY DEFINER`, но если политики настроены неправильно, запись может не проходить.

**Решение:**
```sql
-- Временно отключите RLS для теста
ALTER TABLE public.daily_free_analyses DISABLE ROW LEVEL SECURITY;

-- Попробуйте записать вручную
INSERT INTO public.daily_free_analyses (user_id, analysis_date, analysis_count, profile_analyzed)
VALUES ('YOUR_USER_UUID', CURRENT_DATE, 1, 'test_profile');

-- Если запись прошла, проблема в RLS политиках
-- Включите RLS обратно
ALTER TABLE public.daily_free_analyses ENABLE ROW LEVEL SECURITY;

-- Пересоздайте политики правильно
```

**B. Проблема с SUPABASE_SERVICE_KEY**

Если бекенд использует `SUPABASE_KEY` вместо `SUPABASE_SERVICE_KEY`, функция может не иметь прав на запись.

**Проверьте в Vercel:**
1. Vercel Dashboard → Settings → Environment Variables
2. Убедитесь что есть `SUPABASE_SERVICE_KEY` (не только `SUPABASE_KEY`)
3. Проверьте что используется именно service key (начинается с `eyJ...` и ДЛИННЫЙ)

**C. Функция не вызывается на бекенде**

**Проверьте логи Vercel:**
```bash
vercel logs --prod
```

Ищите строки:
- `✅ Recorded free trial usage for user ...` - функция сработала
- `❌ Failed to record free trial usage` - ошибка при записи

## 🔨 БЫСТРОЕ РЕШЕНИЕ (если всё остальное не помогло)

### Вариант 1: Упрощенная запись напрямую (без RPC)

Измените `backend/supabase_client.py`:

```python
async def record_free_trial_usage(user_id: str, profile_analyzed: Optional[str] = None) -> bool:
    try:
        client = get_supabase()
        
        # Прямая запись в таблицу (не через RPC)
        data = {
            'user_id': user_id,
            'analysis_date': 'CURRENT_DATE',  # Supabase заменит на текущую дату
            'analysis_count': 1,
            'profile_analyzed': profile_analyzed
        }
        
        # Upsert: если запись есть - обновляем count, если нет - создаем
        response = client.table('daily_free_analyses').upsert(
            data,
            on_conflict='user_id,analysis_date'
        ).execute()
        
        logger.info(f"✅ Recorded free trial usage for user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to record free trial usage: {e}")
        raise Exception(f"Failed to record free trial usage: {str(e)}") from e
```

**НО:** Это не сработает с `on_conflict` в Python клиенте Supabase. Лучше оставить RPC и исправить причину.

### Вариант 2: Полный сброс и пересоздание

```sql
-- 1. Удалить всё
DROP TABLE IF EXISTS public.daily_free_analyses CASCADE;
DROP FUNCTION IF EXISTS public.can_use_free_trial CASCADE;
DROP FUNCTION IF EXISTS public.record_free_trial_usage CASCADE;
DROP FUNCTION IF EXISTS public.get_free_trial_info CASCADE;

-- 2. Создать заново
-- Выполните backend/supabase_free_trial_migration.sql
-- Затем backend/fix_free_trial_null.sql
```

## ✅ Проверка исправления

После применения исправлений:

1. **В браузере:**
   - Откройте консоль
   - Выполните анализ
   - Должно появиться:
   ```
   🎁 Free trial AVAILABLE: 0/1 used today
   ✅ Free trial check passed, proceeding with analysis
   ```
   - После анализа:
   ```
   🎁 Free trial AVAILABLE: 1/1 used today
   ```

2. **В Supabase:**
   ```sql
   SELECT * FROM public.daily_free_analyses 
   WHERE analysis_date = CURRENT_DATE;
   ```
   - Должна быть запись с `analysis_count = 1`

3. **Попробуйте снова:**
   - Введите ссылку
   - Нажмите кнопку
   - Должно показать модальное окно подписки

## 📞 Если проблема всё еще не решена

Отправьте результаты диагностики:
1. Результат выполнения `backend/diagnose_free_trial.sql`
2. Логи Vercel: `vercel logs --prod | grep "free trial"`
3. Скриншот консоли браузера после попытки анализа

---

**Дата:** 6 октября 2025  
**Критичность:** 🔴 HIGH - Позволяет обходить лимиты

