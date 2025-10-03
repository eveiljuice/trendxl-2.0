# ✅ Railway Deployment Checklist - TrendXL 2.0

## 📋 Предварительная подготовка

### ✅ Файлы в репозитории (Готово!)

- [x] `Dockerfile.backend` - Backend Docker образ
- [x] `Dockerfile.frontend` - Frontend Docker образ
- [x] `docker-entrypoint.sh` - Nginx entrypoint скрипт
- [x] `nginx.conf` - Конфигурация Nginx (исправлен)
- [x] `.dockerignore` - Исключения для Docker build
- [x] `railway.backend.json` - Railway конфиг для backend
- [x] `railway.frontend.json` - Railway конфиг для frontend

### ✅ Документация (Готово!)

- [x] `RAILWAY_DEPLOYMENT_GUIDE.md` - Полная инструкция (EN)
- [x] `RAILWAY_QUICKSTART_RU.md` - Быстрый старт (RU)
- [x] `DOCKER_CHANGES_SUMMARY.md` - Что было изменено
- [x] `ARCHITECTURE.md` - Архитектура системы
- [x] `DEPLOYMENT_CHECKLIST.md` - Этот чеклист

---

## 🚀 Шаги деплоя на Railway

### Шаг 1: Подготовка Git репозитория

- [ ] Проверить статус Git:

  ```bash
  git status
  ```

- [ ] Добавить все изменения:

  ```bash
  git add .
  ```

- [ ] Создать коммит:

  ```bash
  git commit -m "feat: Railway deployment with optimized Docker configuration"
  ```

- [ ] Push в GitHub:
  ```bash
  git push origin main
  ```

---

### Шаг 2: Получение API ключей

- [ ] **Ensemble Data (TikTok API)** - ОБЯЗАТЕЛЬНО

  - Сайт: https://dashboard.ensembledata.com/
  - Действие: Зарегистрироваться → Скопировать API Token
  - Формат: длинная строка букв/цифр
  - Сохранить: `ENSEMBLE_API_TOKEN=_______________`

- [ ] **OpenAI API** - ОБЯЗАТЕЛЬНО

  - Сайт: https://platform.openai.com/api-keys
  - Действие: Create new secret key
  - Формат: начинается с `sk-` или `sk-proj-`
  - ⚠️ Скопировать сразу (больше не покажут!)
  - Сохранить: `OPENAI_API_KEY=_______________`

- [ ] **Perplexity API** - ОПЦИОНАЛЬНО
  - Сайт: https://www.perplexity.ai/settings/api
  - Действие: Create API key
  - Формат: начинается с `pplx-`
  - Сохранить: `PERPLEXITY_API_KEY=_______________`

---

### Шаг 3: Создание проекта на Railway

- [ ] Открыть Railway Dashboard:

  ```
  https://railway.app/dashboard
  ```

- [ ] Создать новый проект:

  - Нажать **"New Project"**
  - Выбрать **"Deploy from GitHub repo"**
  - Выбрать репозиторий `trendxl-2.0`

- [ ] Переименовать проект:
  - Кликнуть на название проекта вверху
  - Изменить на **"TrendXL 2.0"**

---

### Шаг 4: Деплой Backend сервиса

#### 4.1 Build Configuration

- [ ] Кликнуть на созданный сервис (Backend)
- [ ] Переименовать в **"TrendXL Backend"**
- [ ] Перейти в **Settings → Build**
- [ ] Настроить:
  - **Builder**: `DOCKERFILE`
  - **Dockerfile Path**: `Dockerfile.backend`
  - **Docker Build Context**: `.` (корень)

#### 4.2 Environment Variables

- [ ] Перейти в **Variables**
- [ ] Добавить переменные (нажать **"+ New Variable"** для каждой):

```bash
# API Keys (вставьте ваши реальные ключи)
ENSEMBLE_API_TOKEN=your_token_from_step2
OPENAI_API_KEY=sk-proj-your_key_from_step2
PERPLEXITY_API_KEY=pplx-your_key_from_step2

# Server Configuration
HOST=0.0.0.0
PORT=${{RAILWAY_PORT}}
DEBUG=false
ENVIRONMENT=production

# CORS (Railway автоматически подставит домен Frontend)
CORS_ORIGINS=https://${{Frontend.RAILWAY_PUBLIC_DOMAIN}}
```

- [ ] Нажать **"Save Changes"**

#### 4.3 Networking

- [ ] Перейти в **Settings → Networking**
- [ ] Нажать **"Generate Domain"**
- [ ] Скопировать URL (формат: `https://trendxl-20-backend-*.up.railway.app`)
- [ ] Сохранить URL (понадобится для Frontend)

#### 4.4 Deploy & Verify

- [ ] Railway автоматически начнет деплой
- [ ] Перейти в **Deployments → Latest → View Logs**
- [ ] Дождаться сообщений:

  ```
  ✅ All dependencies installed
  ✅ All API keys configured
  Uvicorn running on http://0.0.0.0:8000
  ```

- [ ] Проверить health check:

  ```
  https://your-backend.up.railway.app/health
  ```

  Должен вернуть:

  ```json
  {
    "status": "healthy",
    "services": {
      "ensemble_api": true,
      "openai_api": true,
      "perplexity_api": true
    }
  }
  ```

- [ ] Проверить API документацию:
  ```
  https://your-backend.up.railway.app/docs
  ```

---

### Шаг 5: Деплой Frontend сервиса

#### 5.1 Add Frontend Service

- [ ] В проекте нажать **"+ New"**
- [ ] Выбрать **"GitHub Repo"**
- [ ] Выбрать тот же репозиторий `trendxl-2.0`
- [ ] Railway создаст второй сервис

#### 5.2 Build Configuration

- [ ] Кликнуть на новый сервис
- [ ] Переименовать в **"TrendXL Frontend"**
- [ ] Перейти в **Settings → Build**
- [ ] Настроить:
  - **Builder**: `DOCKERFILE`
  - **Dockerfile Path**: `Dockerfile.frontend`
  - **Docker Build Context**: `.`

#### 5.3 Environment Variables

⚠️ **ВАЖНО**: Эти переменные используются **во время сборки** (npm run build)!

- [ ] Перейти в **Variables**
- [ ] Добавить:

```bash
# Node Environment
NODE_ENV=production

# Vite Build Variables
VITE_APP_TITLE=TrendXL 2.0
VITE_BACKEND_API_URL=https://${{Backend.RAILWAY_PUBLIC_DOMAIN}}
```

- [ ] Нажать **"Save Changes"**

#### 5.4 Networking

- [ ] Перейти в **Settings → Networking**
- [ ] Нажать **"Generate Domain"**
- [ ] Скопировать URL (формат: `https://trendxl-20-frontend-*.up.railway.app`)
- [ ] **Это ваш основной URL приложения!** 🎉

#### 5.5 Deploy & Verify

- [ ] Railway автоматически начнет деплой
- [ ] Перейти в **Deployments → Latest → View Logs**
- [ ] Следить за логами:

  **Stage 1 (Builder):**

  ```
  npm ci
  npm run build
  ✅ Build completed successfully
  ```

  **Stage 2 (Nginx):**

  ```
  🚀 Starting TrendXL Frontend on Railway
  📡 Using PORT: xxx
  ✅ Nginx configuration updated
  🌐 Starting Nginx server...
  ```

- [ ] Проверить Frontend:

  ```
  https://your-frontend.up.railway.app
  ```

- [ ] Проверить health check:

  ```
  https://your-frontend.up.railway.app/health
  ```

  Должен вернуть: `healthy`

---

### Шаг 6: Проверка интеграции

#### 6.1 Browser Console

- [ ] Открыть Frontend в браузере
- [ ] Нажать **F12** → **Console**
- [ ] Проверить логи:
  ```
  🔍 Environment Debug: {
    VITE_BACKEND_API_URL: "https://your-backend.up.railway.app",
    PROD: true,
    MODE: "production"
  }
  🌐 Final API Base URL: https://your-backend.up.railway.app
  ```

#### 6.2 Test Full Flow

- [ ] Ввести TikTok профиль (например: `@charlidamelio`)
- [ ] Нажать **"Analyze Trends"**
- [ ] Следить за progress:

  - ✅ Loading profile...
  - ✅ Collecting videos...
  - ✅ AI analyzing content...
  - ✅ Searching for trends...

- [ ] Проверить результаты:
  - ✅ Profile stats отображаются
  - ✅ Videos grid загрузился
  - ✅ Hashtags extracted
  - ✅ Trending videos found

#### 6.3 Check Backend Logs

- [ ] Railway Dashboard → Backend Service → Deployments → View Logs
- [ ] Должны видеть:
  ```
  🚀 API Request: POST /api/v1/analyze
  ⏳ Fetching profile: @charlidamelio
  ⏳ Fetching posts...
  ⏳ Analyzing with GPT-4o...
  ✅ API Success: 200 OK
  ```

---

### Шаг 7: Финальная проверка

- [ ] **Backend Health**: ✅ Работает
- [ ] **Frontend Loading**: ✅ Работает
- [ ] **API Communication**: ✅ Работает
- [ ] **CORS**: ✅ Нет ошибок
- [ ] **Full Analysis Flow**: ✅ Работает
- [ ] **Logs**: ✅ Нет критических ошибок

---

## 🐛 Troubleshooting

### ❌ Backend не стартует

**Проверить:**

```bash
# Railway → Backend → Variables
ENSEMBLE_API_TOKEN не пустой?
OPENAI_API_KEY начинается с sk-?
```

**Решение:**

1. Обновить Variables с реальными ключами
2. Backend → Deployments → три точки → **"Restart"**

---

### ❌ Frontend не видит Backend

**Проверить:**

```bash
# Railway → Frontend → Variables
VITE_BACKEND_API_URL=${{Backend.RAILWAY_PUBLIC_DOMAIN}}
```

**Решение:**

1. ⚠️ После изменения VITE\_\* нужен **Redeploy**, не Restart!
2. Frontend → Deployments → три точки → **"Redeploy"**
3. Причина: Vite переменные используются во время build

---

### ❌ CORS ошибка в браузере

**Проверить:**

```bash
# Railway → Backend → Variables
CORS_ORIGINS=https://${{Frontend.RAILWAY_PUBLIC_DOMAIN}}
```

**Решение:**

1. Обновить CORS_ORIGINS
2. Backend → Deployments → **"Restart"**

---

### ❌ Nginx Port Binding Error

**Проверить:**

- docker-entrypoint.sh существует ✅
- Dockerfile.frontend копирует его ✅
- ENTRYPOINT указан правильно ✅

**Решение:**

1. Frontend → Deployments → **"Redeploy"**
2. Check Logs для деталей

---

## 📊 Финальный результат

После выполнения всех шагов:

```
✅ Backend Service
   URL: https://your-backend.up.railway.app
   Health: https://your-backend.up.railway.app/health
   Docs: https://your-backend.up.railway.app/docs

✅ Frontend Service
   URL: https://your-frontend.up.railway.app
   Health: https://your-frontend.up.railway.app/health

✅ Integration
   Frontend → Backend: Working
   External APIs: Connected
   Full Analysis: Functional
```

---

## 🎓 Рекомендации после деплоя

### 1. Auto-Deploy

- [ ] Backend → Settings → **Auto-Deploy: ON**
- [ ] Frontend → Settings → **Auto-Deploy: ON**
- Теперь каждый push в main будет автоматически деплоиться

### 2. Custom Domain (опционально)

- [ ] Settings → Networking → **Custom Domain**
- [ ] Добавить CNAME запись в DNS:
  ```
  your-domain.com → CNAME → your-app.up.railway.app
  ```

### 3. Redis Cache (опционально)

- [ ] Railway Project → **"+ New"** → **"Database"** → **"Redis"**
- [ ] Backend Variables → добавить:
  ```
  REDIS_URL=${{Redis.REDIS_URL}}
  ```

### 4. Monitoring

- [ ] Регулярно проверять **Metrics** в Railway Dashboard
- [ ] Следить за использованием Free Tier (500 часов/месяц)
- [ ] Настроить alerts для критических ошибок

---

## 📚 Дополнительные ресурсы

**Документация:**

- 📖 [RAILWAY_DEPLOYMENT_GUIDE.md](./RAILWAY_DEPLOYMENT_GUIDE.md) - Полная инструкция
- 🚀 [RAILWAY_QUICKSTART_RU.md](./RAILWAY_QUICKSTART_RU.md) - Быстрый старт
- 🏗️ [ARCHITECTURE.md](./ARCHITECTURE.md) - Архитектура
- 📝 [DOCKER_CHANGES_SUMMARY.md](./DOCKER_CHANGES_SUMMARY.md) - Что изменено

**Support:**

- 💬 Railway Discord: https://discord.gg/railway
- 📧 Railway Support: support@railway.app
- 🐛 GitHub Issues: создайте issue в репозитории

---

## ✨ Поздравляем!

Ваше приложение **TrendXL 2.0** успешно развернуто на Railway! 🎉

**Основной URL:** https://your-frontend.up.railway.app

Поделитесь с друзьями и начните анализировать TikTok тренды! 🚀

---

**Дата:** 1 октября 2025  
**Версия:** TrendXL 2.0  
**Платформа:** Railway.app  
**Статус:** ✅ Production Ready
