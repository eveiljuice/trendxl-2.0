# 🚀 Руководство по деплою TrendXL 2.0 на Vercel

## 📋 Оглавление

1. [Подготовка проекта](#подготовка-проекта)
2. [Настройка Vercel](#настройка-vercel)
3. [Переменные окружения](#переменные-окружения)
4. [Деплой](#деплой)
5. [Проверка работы](#проверка-работы)
6. [Troubleshooting](#troubleshooting)

---

## 🔧 Подготовка проекта

Проект уже подготовлен к деплою на Vercel со следующими файлами:

### Созданные файлы:

1. **`vercel.json`** - основной конфигурационный файл для Vercel
2. **`.vercelignore`** - файлы, которые не нужно загружать на Vercel
3. **`api/index.py`** - точка входа для Python backend как Serverless Function
4. **`backend/vercel_adapter.py`** - адаптер для FastAPI → Vercel Serverless

### Структура проекта:

```
trendxl 2.0/
├── api/
│   └── index.py              # Serverless function entry point
├── backend/
│   ├── main.py               # FastAPI приложение
│   ├── vercel_adapter.py     # Vercel адаптер
│   └── requirements.txt      # Python зависимости (с mangum)
├── src/                      # React frontend
├── vercel.json               # Конфигурация Vercel
├── .vercelignore            # Игнорируемые файлы
└── package.json             # Node.js зависимости
```

---

## 🌐 Настройка Vercel

### Шаг 1: Установка Vercel CLI (опционально)

```bash
npm install -g vercel
```

### Шаг 2: Вход в Vercel

```bash
vercel login
```

### Шаг 3: Подключение репозитория

#### Вариант A: Через веб-интерфейс (рекомендуется)

1. Перейдите на [vercel.com](https://vercel.com)
2. Нажмите **"Add New Project"**
3. Импортируйте ваш Git репозиторий (GitHub/GitLab/Bitbucket)
4. Vercel автоматически определит настройки

#### Вариант B: Через CLI

```bash
cd "C:\Users\ok\Desktop\timo\trendxl 2.0"
vercel
```

Следуйте инструкциям CLI для первоначальной настройки.

---

## 🔐 Переменные окружения

### Обязательные переменные:

Настройте следующие переменные в Vercel Dashboard → Settings → Environment Variables:

#### 1. **Ensemble Data API**

```
ENSEMBLE_API_TOKEN=your-ensemble-api-token
```

Получить: https://dashboard.ensembledata.com/

#### 2. **OpenAI API**

```
OPENAI_API_KEY=sk-your-openai-api-key
```

Получить: https://platform.openai.com/api-keys

#### 3. **Perplexity API**

```
PERPLEXITY_API_KEY=pplx-your-perplexity-key
```

Получить: https://www.perplexity.ai/settings/api

#### 4. **JWT Secret**

```
JWT_SECRET_KEY=your-random-secret-key-min-32-chars
```

Генерация:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### 5. **Redis URL** (опционально для кэширования)

```
REDIS_URL=redis://your-redis-url
```

Можно использовать:

- [Upstash Redis](https://upstash.com/) (бесплатный tier)
- [Redis Cloud](https://redis.com/try-free/)

### Настройка через CLI:

```bash
vercel env add ENSEMBLE_API_TOKEN
vercel env add OPENAI_API_KEY
vercel env add PERPLEXITY_API_KEY
vercel env add JWT_SECRET_KEY
vercel env add REDIS_URL
```

### Настройка через Web UI:

1. Откройте проект на [vercel.com](https://vercel.com)
2. Settings → Environment Variables
3. Добавьте каждую переменную с указанными выше именами
4. Выберите окружения: **Production**, **Preview**, **Development**

---

## 🚀 Деплой

### Автоматический деплой (рекомендуется)

После подключения Git репозитория, Vercel автоматически деплоит при каждом push в ветку:

- **main/master** → Production
- **другие ветки** → Preview deployments

### Ручной деплой через CLI

```bash
# Production deploy
vercel --prod

# Preview deploy
vercel
```

### Build команды (настроено в vercel.json):

- **Frontend Build**: `npm run vercel-build` (компилирует Vite → dist/)
- **Backend**: автоматически обрабатывается через `@vercel/python`

---

## ✅ Проверка работы

После успешного деплоя:

### 1. Проверьте основной URL:

```
https://your-project-name.vercel.app
```

### 2. Проверьте Backend Health:

```
https://your-project-name.vercel.app/health
```

Ожидаемый ответ:

```json
{
  "status": "healthy",
  "timestamp": "2024-...",
  "services": {
    "cache": "healthy",
    "api": "healthy"
  }
}
```

### 3. Проверьте API эндпоинты:

```
https://your-project-name.vercel.app/api/v1/status
```

### 4. Тест функциональности:

- Откройте фронтенд
- Попробуйте проанализировать TikTok профиль
- Проверьте логи в Vercel Dashboard → Deployment → Function Logs

---

## 🔧 Troubleshooting

### Проблема 1: Backend не отвечает (502/503)

**Причина**: Python serverless function не запускается

**Решение**:

1. Проверьте логи: Vercel Dashboard → Functions → Logs
2. Убедитесь, что `mangum` установлен в `requirements.txt`
3. Проверьте, что все переменные окружения установлены

### Проблема 2: CORS ошибки

**Причина**: Backend не разрешает запросы с фронтенда

**Решение**:
Обновите `backend/config.py`:

```python
cors_origins: List[str] = Field(
    default=[
        "https://your-project-name.vercel.app",
        "http://localhost:3000",
        "http://localhost:5173"
    ],
    env="CORS_ORIGINS"
)
```

Или установите переменную окружения:

```bash
vercel env add CORS_ORIGINS
# Значение: ["https://your-project-name.vercel.app"]
```

### Проблема 3: Timeout на анализе

**Причина**: Vercel Serverless Functions имеют лимит времени выполнения

- **Hobby plan**: 10 секунд
- **Pro plan**: 60 секунд

**Решение**:

1. Используйте Pro план для полного функционала
2. Оптимизируйте запросы (уже реализовано кэширование)
3. Рассмотрите использование [Vercel Edge Functions](https://vercel.com/docs/functions/edge-functions) для определенных эндпоинтов

### Проблема 4: Database не работает

**Причина**: SQLite не поддерживается в Vercel Serverless (read-only filesystem)

**Решение**:
Используйте внешнюю базу данных:

#### Вариант A: Vercel Postgres (рекомендуется)

```bash
vercel postgres create
```

#### Вариант B: Supabase (PostgreSQL)

1. Создайте проект на [supabase.com](https://supabase.com)
2. Получите Database URL
3. Добавьте в Vercel:

```bash
vercel env add DATABASE_URL
```

#### Вариант C: PlanetScale (MySQL)

1. Создайте базу на [planetscale.com](https://planetscale.com)
2. Получите Connection String
3. Добавьте в Vercel

Затем обновите `backend/database.py` для использования PostgreSQL/MySQL вместо SQLite.

### Проблема 5: Размер deployment слишком большой

**Причина**: Vercel имеет лимит на размер deployment

**Решение**:

1. Убедитесь, что `.vercelignore` корректен
2. Исключите `node_modules`, `dist`, `.git`
3. Оптимизируйте frontend bundle size:

```bash
npm run build -- --report
```

---

## 📊 Мониторинг и Логи

### Просмотр логов:

```bash
vercel logs
```

Или через Dashboard:

- Vercel Dashboard → Project → Deployments → Function Logs

### Настройка алертов:

1. Settings → Notifications
2. Включите уведомления для:
   - Deployment failures
   - Function errors
   - Performance issues

---

## 🎯 Оптимизация для Production

### 1. Включите Vercel Analytics:

```bash
npm install @vercel/analytics
```

В `src/main.tsx`:

```typescript
import { inject } from "@vercel/analytics";
inject();
```

### 2. Настройте кэширование:

В `vercel.json` добавьте:

```json
{
  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ]
}
```

### 3. Оптимизация холодных стартов:

Vercel Serverless Functions могут иметь "холодный старт" (cold start).

**Решение**:

- Используйте Vercel Pro для меньших холодных стартов
- Оптимизируйте импорты в Python:

  ```python
  # Вместо:
  from backend.main import app

  # Используйте:
  import sys
  sys.modules['backend'] = __import__('backend')
  from backend.main import app
  ```

---

## 📝 Checklist перед деплоем

- [ ] Создан Git репозиторий
- [ ] Файлы `vercel.json` и `.vercelignore` присутствуют
- [ ] `mangum` добавлен в `requirements.txt`
- [ ] Все переменные окружения настроены в Vercel
- [ ] Frontend API URL обновлен для production
- [ ] CORS настроен для Vercel домена
- [ ] Проект подключен к Vercel
- [ ] Выполнен первый деплой
- [ ] Протестированы основные функции
- [ ] Настроены алерты и мониторинг

---

## 🔗 Полезные ссылки

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Python Runtime](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [Vercel CLI Reference](https://vercel.com/docs/cli)
- [FastAPI on Vercel Guide](https://vercel.com/guides/deploying-fastapi-with-vercel)
- [Mangum Documentation](https://mangum.io/)

---

## 💡 Альтернативы Vercel

Если Vercel не подходит (например, из-за лимитов Serverless), рассмотрите:

1. **Railway** - уже настроено в проекте, см. `RAILWAY_DEPLOYMENT.md`
2. **Render** - бесплатный tier для fullstack приложений
3. **Fly.io** - бесплатный tier для Docker приложений
4. **Heroku** - классический PaaS (платный)

---

## 📧 Поддержка

При возникновении проблем:

1. Проверьте логи Vercel
2. Просмотрите документацию Vercel
3. Проверьте переменные окружения
4. Убедитесь, что все API ключи валидны

---

**Успешного деплоя! 🚀**
