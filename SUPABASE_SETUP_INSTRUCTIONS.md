# 🚀 Инструкции по настройке Supabase

## ✅ Что уже сделано

### Backend

- ✅ Создан `auth_service_supabase.py` для аутентификации через Supabase Auth
- ✅ Создан `supabase_client.py` с функциями для работы с БД
- ✅ Обновлен `main.py` - все endpoints используют Supabase
- ✅ Удалены `database.py`, `auth_service.py` и локальные `.db` файлы
- ✅ Настроены переменные окружения в `backend/.env`

### Frontend

- ✅ Установлен `@supabase/supabase-js`
- ✅ Создан `src/lib/supabase.ts`
- ✅ Обновлен `AuthContext` для работы с Supabase
- ✅ Настроены переменные окружения в `.env.local`

### SQL Миграции

- ✅ `backend/supabase_migration.sql` - основные таблицы
- ✅ `backend/supabase_token_usage_migration.sql` - профили и token usage

## 📋 Что нужно сделать вручную

### Шаг 1: Активировать проект Supabase (если на паузе)

1. Откройте: https://supabase.com/dashboard/project/jynidxwtbjrxmsbfpqra
2. Если проект на паузе, нажмите **"Resume project"**
3. Дождитесь полной активации (может занять 1-2 минуты)

### Шаг 2: Применить миграции

#### Миграция 1: Профили и Token Usage

1. Откройте SQL Editor:
   https://supabase.com/dashboard/project/jynidxwtbjrxmsbfpqra/sql

2. Нажмите **"New query"**

3. Скопируйте и вставьте содержимое файла:

   ```
   backend/supabase_token_usage_migration.sql
   ```

4. Нажмите **Run** ▶ (или Ctrl+Enter)

5. Убедитесь, что миграция выполнена без ошибок

#### Миграция 2: Таблицы для анализа (Users, Trends, etc.)

1. Создайте новый запрос (New query)

2. Скопируйте и вставьте содержимое файла:

   ```
   backend/supabase_migration.sql
   ```

3. Нажмите **Run** ▶

4. Проверьте результат

### Шаг 3: Проверить таблицы

Откройте Table Editor:
https://supabase.com/dashboard/project/jynidxwtbjrxmsbfpqra/editor

Должны быть созданы следующие таблицы:

#### Auth & Profiles

- ✅ `profiles` - расширенные профили пользователей
- ✅ `token_usage` - отслеживание использования токенов

#### Analysis Data

- ✅ `users` - пользователи TikTok для анализа
- ✅ `trend_feed` - найденные тренды
- ✅ `interaction_log` - логи взаимодействий
- ✅ `niche_adapters` - адаптеры для ниш

### Шаг 4: Проверить Row Level Security (RLS)

Для каждой таблицы:

1. Откройте Table Editor → Выберите таблицу
2. Перейдите на вкладку **"RLS"**
3. Убедитесь, что политики включены:

#### profiles

- ✅ "Public profiles are viewable by everyone" (SELECT)
- ✅ "Users can insert their own profile" (INSERT)
- ✅ "Users can update own profile" (UPDATE)

#### token_usage

- ✅ "Users can view their own token usage" (SELECT)
- ✅ "Anyone can insert token usage" (INSERT)

#### users, trend_feed, interaction_log, niche_adapters

- ✅ "Users can view their own data" (SELECT)
- ✅ "Users can insert their own data" (INSERT)
- ✅ "Users can update their own data" (UPDATE)
- ✅ "Users can delete their own data" (DELETE)

### Шаг 5: Проверить триггеры

1. Откройте SQL Editor
2. Выполните запрос:
   ```sql
   SELECT trigger_name, event_object_table, action_statement
   FROM information_schema.triggers
   WHERE trigger_schema = 'public';
   ```

Должны быть созданы:

- ✅ `on_auth_user_created` на `auth.users` → вызывает `handle_new_user()`
- ✅ `update_*_updated_at` на каждой таблице с `updated_at`

### Шаг 6: Настроить Email Templates (опционально)

1. Откройте: https://supabase.com/dashboard/project/jynidxwtbjrxmsbfpqra/auth/templates
2. Настройте шаблоны для:
   - Confirm signup
   - Reset password
   - Magic link
   - Change email

### Шаг 7: Запустить приложение

#### Backend

```bash
cd backend
python main.py
```

Вы должны увидеть:

```
✅ Supabase client initialized successfully
🚀 TrendXL 2.0 Backend starting up...
```

#### Frontend

```bash
npm run dev
```

Откройте: http://localhost:5173

### Шаг 8: Протестировать

#### Тест 1: Регистрация

1. Откройте приложение
2. Нажмите "Sign Up"
3. Заполните форму:
   - Email: test@example.com
   - Username: testuser
   - Password: password123
4. Нажмите "Register"

**Проверка в Supabase:**

- Откройте: https://supabase.com/dashboard/project/jynidxwtbjrxmsbfpqra/auth/users
- Должен появиться новый пользователь
- Откройте Table Editor → profiles
- Должен быть создан профиль для этого пользователя (через триггер)

#### Тест 2: Авторизация

1. Выйдите из системы (Logout)
2. Нажмите "Sign In"
3. Введите:
   - Email: test@example.com
   - Password: password123
4. Нажмите "Login"

**Ожидаемый результат:**

- ✅ Успешный вход
- ✅ Токен сохранен в localStorage
- ✅ Отображается профиль пользователя

#### Тест 3: Анализ профиля

1. Введите TikTok профиль: `@charlidamelio`
2. Нажмите "Analyze"
3. Дождитесь результатов

**Проверка в Supabase:**

- Откройте Table Editor → token_usage
- Должна появиться новая запись с:
  - user_id (ваш UUID)
  - openai_tokens
  - perplexity_tokens
  - total_cost_estimate
  - profile_analyzed: "charlidamelio"

#### Тест 4: Token Usage

1. В приложении откройте профиль пользователя
2. Перейдите в раздел "Token Usage"

**Ожидаемый результат:**

- ✅ Отображается статистика использования
- ✅ Количество анализов
- ✅ Использованные токены
- ✅ Стоимость

## 🔧 Troubleshooting

### Ошибка: "Connection timeout"

**Причина:** Проект Supabase на паузе или не отвечает

**Решение:**

1. Откройте: https://supabase.com/dashboard/project/jynidxwtbjrxmsbfpqra
2. Нажмите "Resume project"
3. Дождитесь активации
4. Повторите попытку

### Ошибка: "Invalid or expired token"

**Причина:** Токен не валиден или истек

**Решение:**

1. Очистите localStorage в браузере:
   ```javascript
   localStorage.clear();
   ```
2. Перезагрузите страницу
3. Войдите снова

### Ошибка: "RLS policy violation"

**Причина:** Не настроены или отключены RLS политики

**Решение:**

1. Проверьте, что RLS включен для таблицы
2. Проверьте, что политики созданы правильно
3. Пересоздайте политики из миграционного файла

### Ошибка: "SUPABASE_URL not set"

**Причина:** Не настроены переменные окружения

**Решение Backend:**

1. Проверьте `backend/.env`:
   ```env
   SUPABASE_URL=https://jynidxwtbjrxmsbfpqra.supabase.co
   SUPABASE_ANON_KEY=your_anon_key
   ```
2. Перезапустите backend

**Решение Frontend:**

1. Проверьте `.env.local`:
   ```env
   VITE_SUPABASE_URL=https://jynidxwtbjrxmsbfpqra.supabase.co
   VITE_SUPABASE_ANON_KEY=your_anon_key
   ```
2. Перезапустите frontend: `npm run dev`

### Ошибка: "Failed to record token usage"

**Причина:** Таблица token_usage не создана или нет прав

**Решение:**

1. Проверьте, что таблица существует в Table Editor
2. Проверьте RLS политики для token_usage
3. Убедитесь, что политика "Anyone can insert token usage" включена

## 📚 Полезные ссылки

### Supabase Dashboard

- **Main**: https://supabase.com/dashboard/project/jynidxwtbjrxmsbfpqra
- **SQL Editor**: https://supabase.com/dashboard/project/jynidxwtbjrxmsbfpqra/sql
- **Table Editor**: https://supabase.com/dashboard/project/jynidxwtbjrxmsbfpqra/editor
- **Authentication**: https://supabase.com/dashboard/project/jynidxwtbjrxmsbfpqra/auth/users
- **API Settings**: https://supabase.com/dashboard/project/jynidxwtbjrxmsbfpqra/settings/api

### Документация

- [Supabase Auth Guide](https://supabase.com/docs/guides/auth)
- [Row Level Security](https://supabase.com/docs/guides/auth/row-level-security)
- [JavaScript Client](https://supabase.com/docs/reference/javascript/introduction)
- [Python Client](https://supabase.com/docs/reference/python/introduction)

## ✨ Готово!

После выполнения всех шагов ваше приложение будет полностью работать с Supabase:

- ✅ Регистрация и авторизация через Supabase Auth
- ✅ JWT токены управляются Supabase
- ✅ Все данные хранятся в Supabase PostgreSQL
- ✅ Row Level Security защищает данные
- ✅ Автоматическое создание профилей через триггеры
- ✅ Отслеживание использования токенов

Локальная SQLite база данных больше не используется! 🎉
