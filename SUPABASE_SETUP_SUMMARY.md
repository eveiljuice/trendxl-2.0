# 🎉 Supabase Migration - Итоговая инструкция

## ✅ Что было сделано

### 1. **База данных создана**

Создан SQL-файл миграции: `backend/supabase_migration.sql`

Таблицы:

- ✅ `users` - профили TikTok пользователей
- ✅ `trend_feed` - трендовый контент
- ✅ `interaction_log` - логи взаимодействий
- ✅ `niche_adapters` - адаптеры ниш

### 2. **Python клиент настроен**

- ✅ Установлены пакеты: `supabase>=2.0.0`, `postgrest>=0.13.0`
- ✅ Создан файл: `backend/supabase_client.py`
- ✅ Обновлен файл: `backend/requirements.txt`

### 3. **Конфигурация обновлена**

- ✅ Обновлен файл: `backend/config.py`
- ✅ Создан шаблон: `backend/.env.example`
- ✅ Обновлен файл: `backend/.env` (требует ваши ключи)

### 4. **Документация создана**

- ✅ `SUPABASE_MIGRATION_GUIDE.md` - полное руководство
- ✅ `SUPABASE_SETUP_SUMMARY.md` - этот файл
- ✅ `backend/test_supabase_connection.py` - тестовый скрипт

---

## 🚀 Быстрый старт (3 шага)

### Шаг 1: Получите ключи Supabase

1. Откройте ваш проект: **https://supabase.com/dashboard/project/jynidxwtbjrxmsbfpqra**

2. Перейдите в **Settings** → **API**

3. Скопируйте:
   - **Project URL**: `https://sgzlhcagtesjazvwskjw.supabase.co`
   - **anon public** ключ
   - **service_role** ключ (секретный!)

### Шаг 2: Обновите .env файл

Откройте `backend/.env` и замените:

```env
SUPABASE_URL=https://sgzlhcagtesjazvwskjw.supabase.co
SUPABASE_ANON_KEY=ваш-anon-ключ-здесь
SUPABASE_SERVICE_ROLE_KEY=ваш-service-role-ключ-здесь
```

### Шаг 3: Примените миграцию

**Вариант A - Через Dashboard (Рекомендуется)**:

1. Откройте **SQL Editor**: https://supabase.com/dashboard/project/jynidxwtbjrxmsbfpqra/sql
2. Скопируйте содержимое `backend/supabase_migration.sql`
3. Вставьте и нажмите **Run** (▶)

**Вариант B - Через CLI**:

```bash
# Установите CLI
npm install -g supabase

# Войдите
supabase login

# Свяжите проект
supabase link --project-ref jynidxwtbjrxmsbfpqra

# Примените миграцию (если используете локальные миграции)
# Скопируйте supabase_migration.sql в supabase/migrations/
# затем выполните:
supabase db push
```

---

## 🧪 Тестирование

### Тест 1: Проверка подключения

```bash
cd backend
python test_supabase_connection.py
```

Вы должны увидеть:

```
✅ Supabase client initialized successfully
✅ User inserted
✅ Trend inserted
✅ All tests passed successfully!
```

### Тест 2: Запуск сервера

```bash
cd backend
python run_server.py
```

Откройте: http://localhost:8000/docs

### Тест 3: Проверка в Dashboard

1. Откройте **Table Editor**: https://supabase.com/dashboard/project/jynidxwtbjrxmsbfpqra/editor
2. Проверьте таблицы: `users`, `trend_feed`, `interaction_log`, `niche_adapters`

---

## 📊 Структура базы данных

### Таблица: `users`

```sql
id                UUID PRIMARY KEY
link              TEXT UNIQUE (TikTok URL)
parsed_niche      TEXT
location          TEXT
followers         INTEGER
engagement_rate   DECIMAL(5,2)
top_posts         JSONB (массив постов)
created_at        TIMESTAMPTZ
updated_at        TIMESTAMPTZ
```

### Таблица: `trend_feed`

```sql
id                UUID PRIMARY KEY
user_id           UUID → users(id)
trend_title       TEXT
platform          TEXT (default: 'tiktok')
video_url         TEXT
stat_metrics      JSONB (views, likes, comments, shares)
relevance_score   DECIMAL(5,2)
date              TIMESTAMPTZ
created_at        TIMESTAMPTZ
```

### Таблица: `interaction_log`

```sql
id                UUID PRIMARY KEY
user_id           UUID → users(id)
trend_id          UUID → trend_feed(id)
action_type       TEXT (watched/clicked/ignored)
timestamp         TIMESTAMPTZ
```

### Таблица: `niche_adapters`

```sql
id                UUID PRIMARY KEY
domain            TEXT
parsed_by_gpt_summary  TEXT
topic_tags        JSONB (массив тегов)
created_at        TIMESTAMPTZ
updated_at        TIMESTAMPTZ
```

---

## 💻 Примеры использования

### Пример 1: Вставка пользователя

```python
from backend.supabase_client import insert_user

user = await insert_user(
    link="https://tiktok.com/@username",
    parsed_niche="Fashion",
    location="NY",
    followers=25000,
    engagement_rate=5.2,
    top_posts=[
        {"id": "123", "views": 100000, "likes": 5000}
    ]
)
print(f"User ID: {user['id']}")
```

### Пример 2: Добавление тренда

```python
from backend.supabase_client import insert_trend

trend = await insert_trend(
    user_id="user-uuid-here",
    trend_title="#AIArt Challenge",
    video_url="https://tiktok.com/@user/video/456",
    stat_metrics={
        "views": 500000,
        "likes": 25000,
        "comments": 1200
    },
    relevance_score=9.0
)
```

### Пример 3: Получение трендов

```python
from backend.supabase_client import get_trends_by_user

trends = await get_trends_by_user(
    user_id="user-uuid-here",
    limit=20
)

for trend in trends:
    print(f"{trend['trend_title']}: {trend['relevance_score']}")
```

---

## 🔒 Безопасность (Row Level Security)

Миграция автоматически включает RLS на всех таблицах:

```sql
-- Включено на всех таблицах
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE trend_feed ENABLE ROW LEVEL SECURITY;
ALTER TABLE interaction_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE niche_adapters ENABLE ROW LEVEL SECURITY;
```

⚠️ **Важно**: Текущие политики разрешают всем читать/писать.
Для продакшена настройте более строгие правила!

---

## 🛠️ Устранение проблем

### Проблема: "Connection timeout"

**Решение**:

1. Откройте https://supabase.com/dashboard/project/jynidxwtbjrxmsbfpqra
2. Если проект приостановлен (paused), нажмите **Resume**
3. Подождите ~30 секунд

### Проблема: "Invalid API key"

**Решение**:

1. Проверьте `.env` файл
2. Убедитесь, что ключи скопированы полностью
3. Проверьте отсутствие лишних пробелов

### Проблема: "Table doesn't exist"

**Решение**:

1. Примените миграцию через SQL Editor
2. Проверьте в Table Editor наличие таблиц

### Проблема: "Permission denied"

**Решение**:

1. Проверьте RLS политики
2. Используйте `service_role` ключ для полного доступа

---

## 📚 Полезные ссылки

### Ваш проект

- 🏠 [Dashboard](https://supabase.com/dashboard/project/jynidxwtbjrxmsbfpqra)
- 📊 [Table Editor](https://supabase.com/dashboard/project/jynidxwtbjrxmsbfpqra/editor)
- 💻 [SQL Editor](https://supabase.com/dashboard/project/jynidxwtbjrxmsbfpqra/sql)
- 🔑 [API Settings](https://supabase.com/dashboard/project/jynidxwtbjrxmsbfpqra/settings/api)
- 📈 [Logs](https://supabase.com/dashboard/project/jynidxwtbjrxmsbfpqra/logs/explorer)

### Документация

- 📖 [Supabase Docs](https://supabase.com/docs)
- 🐍 [Python Client](https://github.com/supabase/supabase-py)
- 🔐 [Row Level Security](https://supabase.com/docs/guides/database/postgres/row-level-security)
- 🚀 [Deployment Guide](https://supabase.com/docs/guides/deployment)

---

## ✅ Чек-лист

Перед запуском проверьте:

- [ ] Получены ключи Supabase
- [ ] Обновлен файл `backend/.env`
- [ ] Применена миграция в SQL Editor
- [ ] Установлены пакеты: `pip install -r backend/requirements.txt`
- [ ] Пройдены тесты: `python backend/test_supabase_connection.py`
- [ ] Запущен сервер: `python backend/run_server.py`
- [ ] Проверен в браузере: http://localhost:8000/docs

---

## 🎯 Следующие шаги

1. **Настройте RLS политики** для продакшена
2. **Добавьте индексы** для оптимизации запросов
3. **Настройте Realtime** для live обновлений
4. **Добавьте Backup** политики
5. **Мониторинг** через Supabase Dashboard

---

## 💡 Дополнительные возможности Supabase

- 🔄 **Realtime**: Подписывайтесь на изменения в реальном времени
- 🗄️ **Storage**: Храните файлы и медиа
- 🔐 **Auth**: Встроенная аутентификация
- 📧 **Email**: Отправка email уведомлений
- 🔍 **Full-text search**: Полнотекстовый поиск
- 📊 **Analytics**: Встроенная аналитика

---

**Готово! Теперь ваше приложение использует Supabase! 🚀**

Если возникнут вопросы, обращайтесь к `SUPABASE_MIGRATION_GUIDE.md`
