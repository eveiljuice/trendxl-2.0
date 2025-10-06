# 🚨 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Таблицы пустые - записи не создаются

## 🔍 ДИАГНОЗ

Таблицы `daily_free_analyses` и `scan_history` **ПУСТЫЕ** → функции НЕ ЗАПИСЫВАЮТ данные.

## ✅ РЕШЕНИЕ (выполните по порядку)

### Шаг 1: Ручной тест записи в Supabase

1. Откройте **Supabase Dashboard** → **SQL Editor**
2. Скопируйте содержимое файла `backend/manual_test_insert.sql`
3. Выполняйте команды **ПО ОЧЕРЕДИ**:

   **A. Отключите RLS:**

   ```sql
   ALTER TABLE public.daily_free_analyses DISABLE ROW LEVEL SECURITY;
   ```

   **B. Получите ваш UUID:**

   ```sql
   SELECT id, email FROM auth.users WHERE email LIKE '%timolast%';
   ```

   → Скопируйте UUID

   **C. Вставьте запись вручную:**

   ```sql
   INSERT INTO public.daily_free_analyses (
       user_id, analysis_date, analysis_count, profile_analyzed
   ) VALUES (
       'ВАШ_UUID_СЮДА',
       CURRENT_DATE,
       1,
       'test_profile'
   );
   ```

   **D. Проверьте:**

   ```sql
   SELECT * FROM public.daily_free_analyses;
   ```

4. **Если запись появилась** → проблема в бекенде (функция не вызывается)
5. **Если не появилась** → проблема с правами доступа

### Шаг 2: Проверьте переменные в Vercel

1. Откройте **Vercel Dashboard** → ваш проект → **Settings** → **Environment Variables**

2. Проверьте наличие:

   ```
   ✅ SUPABASE_URL=https://...supabase.co
   ✅ SUPABASE_KEY=eyJ... (публичный ключ)
   ✅ SUPABASE_SERVICE_KEY=eyJ... (service role ключ - ДЛИННЫЙ!)
   ✅ JWT_SECRET=...
   ```

3. **КРИТИЧЕСКИ ВАЖНО:** Убедитесь что есть именно `SUPABASE_SERVICE_KEY`!
   - Это НЕ тот же ключ что `SUPABASE_KEY`
   - Найдите его в Supabase: Settings → API → `service_role` key (secret)

### Шаг 3: Проверьте логи в Vercel Dashboard

1. Откройте **Vercel Dashboard** → ваш проект → **Logs**
2. Выполните анализ на сайте
3. Ищите в логах:
   - `✅ Recorded free trial usage` → функция работает
   - `❌ Failed to record free trial usage` → ошибка
   - `record_free_trial_usage` → любые упоминания

### Шаг 4: Исправление на бекенде (если нужно)

Если функция НЕ вызывается, проверьте `backend/supabase_client.py`:

```python
async def record_free_trial_usage(user_id: str, profile_analyzed: Optional[str] = None) -> bool:
    try:
        client = get_supabase()  # ⬅️ Должен использовать SERVICE_KEY!

        # Добавьте отладочный лог
        logger.info(f"🎯 Attempting to record free trial for user: {user_id}")

        # Call the database function
        response = client.rpc('record_free_trial_usage', {
            'p_user_id': user_id,
            'p_profile_analyzed': profile_analyzed
        }).execute()

        logger.info(f"✅ Recorded free trial usage for user {user_id}")
        logger.info(f"📊 Response: {response}")  # ⬅️ Добавьте это
        return True

    except Exception as e:
        logger.error(f"❌ Failed to record free trial usage: {e}")
        logger.error(f"❌ Error details: {type(e).__name__}: {str(e)}")
        raise Exception(f"Failed to record free trial usage: {str(e)}") from e
```

### Шаг 5: Проверьте `get_supabase()` использует SERVICE_KEY

В файле где определена `get_supabase()`:

```python
def get_supabase():
    # ДОЛЖЕН ИСПОЛЬЗОВАТЬ SERVICE_KEY для функций с SECURITY DEFINER!
    return create_client(
        supabase_url=settings.supabase_url,
        supabase_key=settings.supabase_service_key  # ⬅️ НЕ supabase_key!
    )
```

## 🔄 БЫСТРОЕ ВРЕМЕННОЕ РЕШЕНИЕ

Если ничего не помогает, используйте **прямую запись** вместо RPC:

```python
async def record_free_trial_usage(user_id: str, profile_analyzed: Optional[str] = None) -> bool:
    try:
        client = get_supabase()

        # Сначала проверяем есть ли запись за сегодня
        existing = client.table('daily_free_analyses').select('*').eq(
            'user_id', user_id
        ).eq('analysis_date', 'today()').execute()

        if existing.data:
            # Обновляем счетчик
            client.table('daily_free_analyses').update({
                'analysis_count': existing.data[0]['analysis_count'] + 1,
                'last_analysis_timestamp': 'now()',
                'profile_analyzed': profile_analyzed
            }).eq('id', existing.data[0]['id']).execute()
        else:
            # Создаем новую запись
            client.table('daily_free_analyses').insert({
                'user_id': user_id,
                'analysis_count': 1,
                'profile_analyzed': profile_analyzed
            }).execute()

        logger.info(f"✅ Recorded free trial usage for user {user_id}")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to record free trial usage: {e}")
        raise
```

## 📋 Чеклист проверки

- [ ] Таблица `daily_free_analyses` существует
- [ ] RLS временно отключен для теста
- [ ] Ручная запись проходит успешно
- [ ] `SUPABASE_SERVICE_KEY` установлен в Vercel
- [ ] Функция `record_free_trial_usage` вызывается на бекенде
- [ ] Логи показывают успешную запись
- [ ] После исправления: RLS включен обратно

## 🎯 ОЖИДАЕМЫЙ РЕЗУЛЬТАТ

После исправления:

1. Пользователь делает анализ
2. В таблице появляется запись с `analysis_count = 1`
3. Повторный анализ показывает модальное окно подписки
4. На следующий день (00:00 UTC) попытка восстанавливается

---

**Время исправления:** 15-30 минут  
**Критичность:** 🔴 CRITICAL  
**Дата:** 6 октября 2025
