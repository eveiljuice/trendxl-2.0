# TrendXL 2.0 - Supabase Migration Guide

## Обзор

Этот проект теперь использует **Supabase** вместо локальной SQLite базы данных. Supabase предоставляет:

- ✅ **PostgreSQL database** - мощная реляционная база данных
- ✅ **Row Level Security (RLS)** - встроенная безопасность на уровне строк
- ✅ **Real-time subscriptions** - подписки в реальном времени
- ✅ **Authentication** - встроенная аутентификация
- ✅ **Автоматическая генерация API** - RESTful и GraphQL API

---

## Шаг 1: Получение ключей Supabase

1. Откройте ваш проект Supabase: https://supabase.com/dashboard/project/jynidxwtbjrxmsbfpqra

2. Перейдите в **Settings** → **API**

3. Скопируйте следующие значения:
   - **Project URL**: `https://sgzlhcagtesjazvwskjw.supabase.co`
   - **anon/public key**: используется для клиентских запросов
   - **service_role key**: используется для серверных операций (держите в секрете!)

---

## Шаг 2: Применение миграции базы данных

### Вариант A: Через Supabase Dashboard (Рекомендуется)

1. Откройте **SQL Editor** в вашем проекте Supabase
2. Скопируйте содержимое файла `backend/supabase_migration.sql`
3. Вставьте SQL в редактор
4. Нажмите **Run** для выполнения миграции

### Вариант B: Через Supabase CLI

```bash
# Установите Supabase CLI (если еще не установлен)
npm install -g supabase

# Войдите в аккаунт
supabase login

# Свяжите проект
supabase link --project-ref jynidxwtbjrxmsbfpqra

# Примените миграцию
supabase db push
```

---

## Шаг 3: Обновление конфигурации

1. Откройте файл `backend/.env`

2. Обновите следующие переменные:

```env
# Supabase Configuration
SUPABASE_URL=https://sgzlhcagtesjazvwskjw.supabase.co
SUPABASE_ANON_KEY=ваш-anon-key-здесь
SUPABASE_SERVICE_ROLE_KEY=ваш-service-role-key-здесь
```

---

## Шаг 4: Установка зависимостей

Установите необходимые Python пакеты:

```bash
cd backend
pip install -r requirements.txt
```

Это установит:

- `supabase>=2.0.0` - Python клиент для Supabase
- `postgrest>=0.13.0` - Python клиент для PostgREST API

---

## Шаг 5: Структура базы данных

### Таблица: `users`

Хранит информацию о пользователях TikTok

| Поле            | Тип         | Описание                        |
| --------------- | ----------- | ------------------------------- |
| id              | UUID        | Primary key                     |
| link            | TEXT        | TikTok профиль URL (уникальный) |
| parsed_niche    | TEXT        | Определенная ниша               |
| location        | TEXT        | Локация пользователя            |
| followers       | INTEGER     | Количество подписчиков          |
| engagement_rate | DECIMAL     | Уровень вовлеченности           |
| top_posts       | JSONB       | Массив топовых постов           |
| created_at      | TIMESTAMPTZ | Дата создания                   |
| updated_at      | TIMESTAMPTZ | Дата обновления                 |

### Таблица: `trend_feed`

Хранит трендовый контент и результаты анализа

| Поле            | Тип         | Описание                          |
| --------------- | ----------- | --------------------------------- |
| id              | UUID        | Primary key                       |
| user_id         | UUID        | Foreign key → users.id            |
| trend_title     | TEXT        | Название тренда                   |
| platform        | TEXT        | Платформа (по умолчанию 'tiktok') |
| video_url       | TEXT        | URL видео                         |
| stat_metrics    | JSONB       | Метрики (views, likes, comments)  |
| relevance_score | DECIMAL     | Оценка релевантности              |
| date            | TIMESTAMPTZ | Дата тренда                       |
| created_at      | TIMESTAMPTZ | Дата создания                     |

### Таблица: `interaction_log`

Отслеживает взаимодействия пользователей с трендами

| Поле        | Тип         | Описание                               |
| ----------- | ----------- | -------------------------------------- |
| id          | UUID        | Primary key                            |
| user_id     | UUID        | Foreign key → users.id                 |
| trend_id    | UUID        | Foreign key → trend_feed.id            |
| action_type | TEXT        | Тип действия (watched/clicked/ignored) |
| timestamp   | TIMESTAMPTZ | Время действия                         |

### Таблица: `niche_adapters`

Хранит анализ контента по нишам и теги тем

| Поле                  | Тип         | Описание         |
| --------------------- | ----------- | ---------------- |
| id                    | UUID        | Primary key      |
| domain                | TEXT        | Домен/ниша       |
| parsed_by_gpt_summary | TEXT        | Резюме от GPT    |
| topic_tags            | JSONB       | Массив тегов тем |
| created_at            | TIMESTAMPTZ | Дата создания    |
| updated_at            | TIMESTAMPTZ | Дата обновления  |

---

## Шаг 6: Использование в коде

### Пример: Вставка пользователя

```python
from backend.supabase_client import insert_user

# Вставить нового пользователя
user = await insert_user(
    link="https://tiktok.com/@username",
    parsed_niche="Tech Reviews",
    location="US",
    followers=10000,
    engagement_rate=4.5,
    top_posts=[{"id": "123", "views": 50000}]
)
```

### Пример: Получение трендов

```python
from backend.supabase_client import get_trends_by_user

# Получить тренды для пользователя
trends = await get_trends_by_user(user_id="uuid-here", limit=20)
```

### Пример: Логирование взаимодействий

```python
from backend.supabase_client import insert_interaction

# Залогировать взаимодействие
interaction = await insert_interaction(
    user_id="uuid-here",
    trend_id="uuid-here",
    action_type="watched"
)
```

---

## Шаг 7: Row Level Security (RLS)

Миграция автоматически настраивает RLS политики:

- ✅ **Users**: все могут просматривать, вставлять и обновлять
- ✅ **TrendFeed**: все могут просматривать, вставлять и обновлять
- ✅ **InteractionLog**: все могут просматривать и вставлять
- ✅ **NicheAdapters**: все могут просматривать, вставлять и обновлять

⚠️ **Примечание**: В продакшене вы должны ограничить политики для большей безопасности.

---

## Шаг 8: Тестирование

Запустите приложение и проверьте подключение:

```bash
cd backend
python run_server.py
```

Или используйте Playwright для автоматического тестирования:

```bash
# Установите Playwright (если еще не установлен)
pip install playwright
playwright install

# Запустите тесты
pytest tests/
```

---

## Шаг 9: Мониторинг и отладка

### Проверка подключения

В логах приложения вы должны увидеть:

```
✅ Supabase client initialized successfully
```

### Просмотр данных

1. Откройте **Table Editor** в Supabase Dashboard
2. Выберите таблицу для просмотра данных
3. Используйте фильтры для поиска

### Просмотр логов

1. Откройте **Logs** в Supabase Dashboard
2. Выберите тип логов (API, Database, Auth)
3. Фильтруйте по времени и уровню

---

## Миграция существующих данных (Опционально)

Если у вас есть данные в локальной SQLite базе:

```bash
# 1. Экспортируйте данные из SQLite
sqlite3 backend/trendxl_users.db .dump > old_data.sql

# 2. Конвертируйте SQLite SQL в PostgreSQL (вручную или используйте инструменты)
# 3. Импортируйте в Supabase через SQL Editor
```

---

## Полезные ссылки

- 📚 [Supabase Docs](https://supabase.com/docs)
- 📚 [Supabase Python Client](https://github.com/supabase/supabase-py)
- 📚 [PostgreSQL Docs](https://www.postgresql.org/docs/)
- 🔑 [Your Project Dashboard](https://supabase.com/dashboard/project/jynidxwtbjrxmsbfpqra)
- 🎯 [API Docs](https://supabase.com/dashboard/project/jynidxwtbjrxmsbfpqra/api)

---

## Устранение неполадок

### Проблема: "Connection terminated due to connection timeout"

**Решение**: Ваш проект Supabase может быть приостановлен (паузed). Откройте dashboard и разбудите проект.

### Проблема: "Invalid API key"

**Решение**: Убедитесь, что вы скопировали правильный ключ из Settings → API.

### Проблема: "Row Level Security policy violation"

**Решение**: Проверьте RLS политики в Table Editor → Policies.

---

## Следующие шаги

1. ✅ Примените миграцию базы данных
2. ✅ Обновите переменные окружения
3. ✅ Установите зависимости
4. ✅ Протестируйте приложение
5. 🚀 Разверните на продакшен

Удачи! 🎉
