# 🚂 Railway Deployment Guide - TrendXL 2.0

## 📋 Оглавление

1. [Предварительные требования](#предварительные-требования)
2. [Архитектура деплоя](#архитектура-деплоя)
3. [Шаг 1: Подготовка репозитория](#шаг-1-подготовка-репозитория)
4. [Шаг 2: Создание проекта на Railway](#шаг-2-создание-проекта-на-railway)
5. [Шаг 3: Деплой Backend сервиса](#шаг-3-деплой-backend-сервиса)
6. [Шаг 4: Деплой Frontend сервиса](#шаг-4-деплой-frontend-сервиса)
7. [Шаг 5: Настройка переменных окружения](#шаг-5-настройка-переменных-окружения)
8. [Шаг 6: Проверка работоспособности](#шаг-6-проверка-работоспособности)
9. [Troubleshooting](#troubleshooting)

---

## 🎯 Предварительные требования

### Аккаунты и API ключи

- ✅ Аккаунт на [Railway.app](https://railway.app)
- ✅ GitHub репозиторий с кодом проекта
- ✅ API ключ Ensemble Data (TikTok API): https://dashboard.ensembledata.com/
- ✅ API ключ OpenAI: https://platform.openai.com/api-keys
- ✅ API ключ Perplexity (опционально): https://www.perplexity.ai/settings/api

### Технические требования

- Git установлен локально
- Базовое понимание Docker
- Доступ к командной строке

---

## 🏗️ Архитектура деплоя

TrendXL 2.0 использует **микросервисную архитектуру** на Railway:

```
┌─────────────────────────────────────────────────────┐
│                  Railway Project                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────────┐      ┌──────────────────┐   │
│  │   Backend       │      │   Frontend       │   │
│  │   (FastAPI)     │◄─────┤   (Nginx)        │   │
│  │   Port: 8000    │      │   Port: 80       │   │
│  │   Dockerfile:   │      │   Dockerfile:    │   │
│  │   .backend      │      │   .frontend      │   │
│  └────────┬────────┘      └──────────────────┘   │
│           │                                        │
│           ▼                                        │
│  ┌─────────────────┐                              │
│  │   Redis         │ (опционально)                │
│  │   (Cache)       │                              │
│  └─────────────────┘                              │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Компоненты:**

- **Backend**: Python FastAPI + Uvicorn (порт 8000)
- **Frontend**: React + Vite + Nginx (порт 80, динамический)
- **Redis**: Кэширование (опционально, Railway addon)

---

## 📦 Шаг 1: Подготовка репозитория

### 1.1 Убедитесь, что все Docker файлы на месте

Проверьте наличие следующих файлов в корне проекта:

```bash
ls -la | grep -E "Dockerfile|docker-entrypoint|nginx.conf"
```

Должны быть:

- ✅ `Dockerfile.backend` - Backend Docker образ
- ✅ `Dockerfile.frontend` - Frontend Docker образ
- ✅ `docker-entrypoint.sh` - Entrypoint для Nginx с динамическим PORT
- ✅ `nginx.conf` - Конфигурация Nginx
- ✅ `railway.backend.json` - Railway конфиг для бэкенда
- ✅ `railway.frontend.json` - Railway конфиг для фронтенда

### 1.2 Коммит и Push в GitHub

```bash
# Проверьте статус
git status

# Добавьте все изменения
git add .

# Коммит
git commit -m "feat: Railway deployment configuration with optimized Dockerfiles"

# Push в удаленный репозиторий
git push origin main
```

---

## 🚀 Шаг 2: Создание проекта на Railway

### 2.1 Создайте новый проект

1. Перейдите на https://railway.app/dashboard
2. Нажмите **"New Project"**
3. Выберите **"Deploy from GitHub repo"**
4. Выберите ваш репозиторий `trendxl-2.0`
5. Railway создаст пустой проект

### 2.2 Настройте Project Settings

1. Кликните на название проекта вверху
2. Переименуйте в **"TrendXL 2.0"**
3. Выберите регион (рекомендуется US West или US East)

---

## 🔧 Шаг 3: Деплой Backend сервиса

### 3.1 Добавьте Backend Service

1. В проекте нажмите **"+ New"** → **"GitHub Repo"**
2. Выберите ваш репозиторий
3. Railway автоматически обнаружит код

### 3.2 Настройте Backend Build

1. Кликните на созданный сервис
2. Перейдите в **"Settings"** → **"Build"**
3. Настройте следующее:
   - **Builder**: `DOCKERFILE`
   - **Dockerfile Path**: `Dockerfile.backend`
   - **Docker Build Context**: `./` (корень репозитория)

### 3.3 Настройте Backend переменные окружения

Перейдите в **"Variables"** и добавьте:

**Обязательные переменные:**

```bash
# API Keys (КРИТИЧЕСКИ ВАЖНО!)
ENSEMBLE_API_TOKEN=your_ensemble_data_api_token_here
OPENAI_API_KEY=sk-proj-your_openai_api_key_here
PERPLEXITY_API_KEY=pplx-your_perplexity_api_key_here

# Server Configuration
HOST=0.0.0.0
PORT=${{RAILWAY_PORT}}
DEBUG=false
ENVIRONMENT=production

# CORS - Railway автоматически подставит домены
CORS_ORIGINS=https://${{Frontend.RAILWAY_PUBLIC_DOMAIN}},https://${{RAILWAY_PUBLIC_DOMAIN}}
```

**Опциональные переменные:**

```bash
# Redis (если используете Railway Redis addon)
REDIS_URL=${{Redis.REDIS_URL}}

# Rate Limiting
MAX_REQUESTS_PER_MINUTE=60

# Cache TTL (seconds)
CACHE_PROFILE_TTL=1800
CACHE_POSTS_TTL=900
CACHE_TRENDS_TTL=300
```

### 3.4 Настройте Backend Networking

1. Перейдите в **"Settings"** → **"Networking"**
2. Нажмите **"Generate Domain"** чтобы получить публичный URL
3. Скопируйте URL (будет нужен для Frontend)
4. Формат: `https://trendxl-20-backend-production.up.railway.app`

### 3.5 Деплой Backend

1. Railway автоматически начнет деплой
2. Следите за логами в **"Deployments"** → последний деплой → **"View Logs"**
3. Дождитесь сообщения: `✅ All API keys configured` и `Uvicorn running on`
4. Проверьте health: `https://your-backend.up.railway.app/health`

---

## 🎨 Шаг 4: Деплой Frontend сервиса

### 4.1 Добавьте Frontend Service

1. В том же проекте нажмите **"+ New"** → **"GitHub Repo"**
2. Выберите тот же репозиторий
3. Railway создаст второй сервис

### 4.2 Настройте Frontend Build

1. Кликните на новый сервис
2. Переименуйте в **"TrendXL Frontend"**
3. Перейдите в **"Settings"** → **"Build"**
4. Настройте:
   - **Builder**: `DOCKERFILE`
   - **Dockerfile Path**: `Dockerfile.frontend`
   - **Docker Build Context**: `./`

### 4.3 Настройте Frontend переменные окружения

⚠️ **ВАЖНО**: Эти переменные используются **во время сборки** Vite!

Перейдите в **"Variables"** и добавьте:

```bash
# Node.js Environment
NODE_ENV=production

# Vite Build Variables (используются во время npm run build)
VITE_APP_TITLE=TrendXL 2.0
VITE_BACKEND_API_URL=https://${{Backend.RAILWAY_PUBLIC_DOMAIN}}

# Note: Railway автоматически подставит домен Backend сервиса
```

### 4.4 Настройте Frontend Networking

1. Перейдите в **"Settings"** → **"Networking"**
2. Нажмите **"Generate Domain"**
3. Формат: `https://trendxl-20-frontend-production.up.railway.app`
4. Это будет ваш основной URL приложения!

### 4.5 Деплой Frontend

1. Railway автоматически начнет сборку
2. Следите за логами:
   - Стадия 1 (builder): `npm ci` → `npm run build` → `✅ Build completed successfully`
   - Стадия 2 (nginx): `🚀 Starting TrendXL Frontend on Railway` → `🌐 Starting Nginx server...`
3. Откройте Frontend URL в браузере

---

## ⚙️ Шаг 5: Настройка переменных окружения

### 5.1 Получите ваши API ключи

#### Ensemble Data (TikTok API)

1. Перейдите на https://dashboard.ensembledata.com/
2. Зарегистрируйтесь или войдите
3. Скопируйте API Token
4. Формат: длинная строка из букв и цифр

#### OpenAI API

1. Перейдите на https://platform.openai.com/api-keys
2. Создайте новый API key
3. Скопируйте ключ (начинается с `sk-proj-` или `sk-`)
4. ⚠️ Сохраните его - больше не сможете увидеть!

#### Perplexity API (опционально)

1. Перейдите на https://www.perplexity.ai/settings/api
2. Создайте API key
3. Формат: начинается с `pplx-`

### 5.2 Обновите переменные в Railway

1. Перейдите в Backend сервис → **"Variables"**
2. Замените placeholder'ы на реальные ключи:
   ```bash
   ENSEMBLE_API_TOKEN=<ваш реальный токен>
   OPENAI_API_KEY=sk-proj-<ваш реальный ключ>
   PERPLEXITY_API_KEY=pplx-<ваш реальный ключ>
   ```
3. Нажмите **"Save"**
4. Railway автоматически **перезапустит** Backend сервис

### 5.3 Проверьте CORS настройки

Убедитесь, что Backend знает о Frontend домене:

```bash
# В Backend Variables
CORS_ORIGINS=https://${{Frontend.RAILWAY_PUBLIC_DOMAIN}}
```

Railway автоматически подставит реальный домен.

---

## ✅ Шаг 6: Проверка работоспособности

### 6.1 Проверьте Backend Health

Откройте в браузере:

```
https://your-backend.up.railway.app/health
```

Должны увидеть:

```json
{
  "status": "healthy",
  "timestamp": "2024-...",
  "services": {
    "ensemble_api": true,
    "openai_api": true,
    "perplexity_api": true,
    "redis": true // если используется
  }
}
```

### 6.2 Проверьте Backend API Documentation

```
https://your-backend.up.railway.app/docs
```

Должна открыться интерактивная документация FastAPI (Swagger UI).

### 6.3 Проверьте Frontend

1. Откройте: `https://your-frontend.up.railway.app`
2. Должна загрузиться главная страница TrendXL
3. Откройте DevTools Console (F12)
4. Найдите сообщения:
   ```
   🔍 Environment Debug: { VITE_BACKEND_API_URL: "https://...", ... }
   🌐 Final API Base URL: https://your-backend.up.railway.app
   ```

### 6.4 Протестируйте полный флоу

1. Введите TikTok профиль (например: `@charlidamelio`)
2. Нажмите "Analyze Trends"
3. Следите за логами в Railway:
   - **Backend logs**: должны появиться запросы к TikTok API
   - **Frontend logs** (в браузере): progress updates
4. Дождитесь результатов анализа

---

## 🔧 Troubleshooting

### ❌ Проблема: Backend не стартует

**Симптомы:**

```
Error: ENSEMBLE_API_TOKEN is required
```

**Решение:**

1. Проверьте Backend Variables в Railway
2. Убедитесь, что `ENSEMBLE_API_TOKEN` установлен и не пустой
3. Перезапустите деплой: **"Deployments"** → **"Restart"**

---

### ❌ Проблема: Frontend не может достучаться до Backend

**Симптомы:**

```
❌ API Error: Network error - no response from server
🔌 Connection refused - backend not responding
```

**Решение:**

1. **Проверьте VITE_BACKEND_API_URL:**

   - Frontend Variables должны содержать: `VITE_BACKEND_API_URL=https://${{Backend.RAILWAY_PUBLIC_DOMAIN}}`
   - Railway автоматически подставляет реальный URL Backend

2. **Пересоберите Frontend:**

   - ⚠️ Vite переменные используются **во время сборки**!
   - После изменения `VITE_*` переменных нужно **Redeploy**:
   - Frontend Service → **"Deployments"** → три точки → **"Redeploy"**

3. **Проверьте Backend CORS:**

   ```bash
   # Backend Variables
   CORS_ORIGINS=https://${{Frontend.RAILWAY_PUBLIC_DOMAIN}}
   ```

4. **Проверьте что Backend работает:**
   ```bash
   curl https://your-backend.up.railway.app/health
   ```

---

### ❌ Проблема: Port Binding Error в Nginx

**Симптомы:**

```
nginx: [emerg] bind() to 0.0.0.0:80 failed
```

**Решение:**

1. **Проверьте docker-entrypoint.sh:**

   - Файл должен существовать в корне проекта
   - Должен быть исполняемым: `chmod +x docker-entrypoint.sh`

2. **Проверьте Dockerfile.frontend:**

   ```dockerfile
   COPY docker-entrypoint.sh /docker-entrypoint.sh
   RUN chmod +x /docker-entrypoint.sh
   ENTRYPOINT ["/docker-entrypoint.sh"]
   ```

3. **Redeploy Frontend:**
   - Settings → Deploy → "Redeploy"

---

### ❌ Проблема: CORS Error в браузере

**Симптомы:**

```
Access to XMLHttpRequest at 'https://backend...' from origin 'https://frontend...'
has been blocked by CORS policy
```

**Решение:**

1. **Проверьте Backend CORS настройки:**

   ```python
   # backend/main.py должен содержать:
   app.add_middleware(
       CORSMiddleware,
       allow_origins=settings.cors_origins,
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

2. **Проверьте Backend переменные:**

   ```bash
   CORS_ORIGINS=https://${{Frontend.RAILWAY_PUBLIC_DOMAIN}}
   # Или для дебага можно временно использовать:
   CORS_ORIGINS=*
   ```

3. **Перезапустите Backend** после изменения CORS настроек

---

### ❌ Проблема: Build занимает слишком много времени

**Решение:**

1. **Frontend build (npm ci):**

   - Обычно занимает 2-5 минут
   - Если больше 10 минут - check npm logs

2. **Backend build (pip install):**

   - Обычно 3-5 минут
   - `pip install` компилирует некоторые пакеты (cryptography, bcrypt)

3. **Optimization tips:**
   - Railway кэширует Docker layers
   - После первого деплоя последующие будут быстрее

---

### ❌ Проблема: API ключи не работают

**Симптомы:**

```
⚠️ ENSEMBLE_API_TOKEN appears too short
⚠️ OPENAI_API_KEY format may be invalid
```

**Решение:**

1. **Ensemble Data Token:**

   - Должен быть длинным (50+ символов)
   - Только буквы, цифры, дефисы, подчеркивания
   - Проверьте на https://dashboard.ensembledata.com/

2. **OpenAI API Key:**

   - Должен начинаться с `sk-` или `sk-proj-`
   - Минимум 20 символов
   - Проверьте на https://platform.openai.com/api-keys

3. **Perplexity API Key:**

   - Должен начинаться с `pplx-`
   - Проверьте на https://www.perplexity.ai/settings/api

4. **После обновления ключей:**
   - Restart Backend service в Railway

---

### 🔍 Проблема: Как посмотреть логи?

**Backend Logs:**

```
Railway Dashboard → Backend Service → Deployments →
Latest Deployment → View Logs
```

**Frontend Logs:**

```
Railway Dashboard → Frontend Service → Deployments →
Latest Deployment → View Logs
```

**Браузерные логи:**

```
F12 → Console tab
```

**Полезные команды для дебага:**

```bash
# Backend health check
curl https://your-backend.up.railway.app/health

# Backend API docs
open https://your-backend.up.railway.app/docs

# Frontend health check
curl https://your-frontend.up.railway.app/health

# Test CORS
curl -H "Origin: https://your-frontend.up.railway.app" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS \
     https://your-backend.up.railway.app/api/v1/analyze
```

---

## 📊 Monitoring & Maintenance

### Мониторинг в Railway

1. **Metrics:**

   - Service → "Metrics" tab
   - CPU, Memory, Network usage

2. **Deployment History:**

   - Service → "Deployments"
   - Все предыдущие деплои

3. **Build & Deploy Logs:**
   - Deployment → "View Logs"
   - Build stage и Runtime logs

### Рекомендуемые практики

1. **Используйте Railway Environment Variables** для всех секретов
2. **Включите Auto-Deploy** для автоматического деплоя при push в main
3. **Настройте Health Checks** для автоматического перезапуска
4. **Мониторьте использование ресурсов** (Railway Free Tier: 500 часов/месяц)
5. **Регулярно обновляйте dependencies** (npm audit, pip-audit)

---

## 🎉 Готово!

Теперь ваше приложение TrendXL 2.0 успешно развернуто на Railway!

**Полезные ссылки:**

- 📚 Railway Docs: https://docs.railway.app/
- 🎓 Railway Templates: https://railway.app/templates
- 💬 Railway Discord: https://discord.gg/railway
- 🐛 TrendXL Issues: https://github.com/your-repo/issues

**Frontend URL:** `https://your-frontend.up.railway.app`
**Backend URL:** `https://your-backend.up.railway.app`
**API Docs:** `https://your-backend.up.railway.app/docs`

---

## 📝 Changelog

- **2024-10-01**: Initial Railway deployment guide
- Оптимизированные Dockerfiles для Railway
- Динамическая конфигурация Nginx PORT
- Multi-stage builds для минимальных образов
- Comprehensive troubleshooting guide

---

**Автор:** TrendXL Team  
**Лицензия:** MIT
