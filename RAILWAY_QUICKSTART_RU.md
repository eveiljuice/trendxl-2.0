# 🚂 Railway - Быстрый старт для TrendXL 2.0

## 📦 Что было сделано

✅ **Оптимизированные Docker файлы:**

- `Dockerfile.backend` - Python FastAPI backend
- `Dockerfile.frontend` - React + Vite + Nginx frontend
- `docker-entrypoint.sh` - динамическая конфигурация Nginx PORT
- `nginx.conf` - исправлен, убрано дублирование
- `.dockerignore` - исключение ненужных файлов из образов

✅ **Railway конфигурации:**

- `railway.backend.json` - настройки для backend сервиса
- `railway.frontend.json` - настройки для frontend сервиса (обновлен путь к Dockerfile)

✅ **Документация:**

- `RAILWAY_DEPLOYMENT_GUIDE.md` - полная пошаговая инструкция на английском
- `RAILWAY_QUICKSTART_RU.md` - эта краткая справка на русском

---

## 🚀 Быстрый деплой (5 шагов)

### Шаг 1: Push в GitHub

```bash
git add .
git commit -m "feat: Railway deployment ready"
git push origin main
```

### Шаг 2: Создайте проект на Railway

1. Перейдите на https://railway.app/dashboard
2. **"New Project"** → **"Deploy from GitHub repo"**
3. Выберите репозиторий `trendxl-2.0`

### Шаг 3: Деплой Backend

1. Railway автоматически создаст сервис
2. **Settings** → **Build**:
   - Builder: `DOCKERFILE`
   - Dockerfile Path: `Dockerfile.backend`
3. **Variables** → добавьте API ключи:
   ```
   ENSEMBLE_API_TOKEN=your_token_here
   OPENAI_API_KEY=sk-proj-your_key_here
   PERPLEXITY_API_KEY=pplx-your_key_here
   HOST=0.0.0.0
   PORT=${{RAILWAY_PORT}}
   DEBUG=false
   ```
4. **Networking** → **Generate Domain**
5. Скопируйте Backend URL

### Шаг 4: Деплой Frontend

1. В проекте: **"+ New"** → **"GitHub Repo"** (тот же репозиторий)
2. **Settings** → **Build**:
   - Builder: `DOCKERFILE`
   - Dockerfile Path: `Dockerfile.frontend`
3. **Variables**:
   ```
   NODE_ENV=production
   VITE_APP_TITLE=TrendXL 2.0
   VITE_BACKEND_API_URL=https://${{Backend.RAILWAY_PUBLIC_DOMAIN}}
   ```
4. **Networking** → **Generate Domain**

### Шаг 5: Проверка

1. Backend health: `https://your-backend.up.railway.app/health`
2. Frontend: `https://your-frontend.up.railway.app`
3. Тест: введите TikTok профиль и запустите анализ

---

## 🔑 Где получить API ключи

### Ensemble Data (TikTok API) - **ОБЯЗАТЕЛЬНО**

- 🔗 https://dashboard.ensembledata.com/
- Регистрация → API Token
- Формат: длинная строка букв/цифр

### OpenAI API - **ОБЯЗАТЕЛЬНО**

- 🔗 https://platform.openai.com/api-keys
- Create new key
- Формат: `sk-proj-...` или `sk-...`

### Perplexity API - **ОПЦИОНАЛЬНО**

- 🔗 https://www.perplexity.ai/settings/api
- Create API key
- Формат: `pplx-...`

---

## 📂 Структура проекта

```
trendxl-2.0/
├── backend/                      # Python FastAPI backend
│   ├── main.py                  # FastAPI app
│   ├── config.py                # Настройки
│   ├── requirements.txt         # Python зависимости
│   └── run_server.py            # Запуск сервера
├── src/                         # React frontend
│   ├── components/              # UI компоненты
│   ├── services/                # API клиенты
│   │   └── backendApi.ts        # Backend API интеграция
│   └── main.tsx                 # React entry point
├── Dockerfile.backend           # ✅ Backend Docker образ
├── Dockerfile.frontend          # ✅ Frontend Docker образ
├── docker-entrypoint.sh         # ✅ Nginx entrypoint (PORT)
├── nginx.conf                   # ✅ Nginx конфигурация
├── .dockerignore                # ✅ Docker ignore file
├── railway.backend.json         # ✅ Railway backend config
├── railway.frontend.json        # ✅ Railway frontend config
├── RAILWAY_DEPLOYMENT_GUIDE.md  # 📚 Полная инструкция (EN)
└── RAILWAY_QUICKSTART_RU.md     # 📚 Эта справка (RU)
```

---

## 🔧 Основные технологии

**Backend:**

- Python 3.10
- FastAPI + Uvicorn
- OpenAI GPT-4o (анализ контента)
- Ensemble Data (TikTok API)
- Perplexity (Creative Center поиск)
- Redis (кэширование, опционально)

**Frontend:**

- React 18 + TypeScript
- Vite (build tool)
- Chakra UI + Tailwind CSS
- Axios (HTTP клиент)

**Инфраструктура:**

- Railway (хостинг)
- Docker (контейнеризация)
- Nginx (веб-сервер для фронтенда)

---

## ⚙️ Ключевые особенности Dockerfile

### Backend (Dockerfile.backend)

```dockerfile
# Multi-stage build не используется (single stage)
FROM python:3.10-slim-bullseye

# Оптимальные Python переменные
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Layer caching: requirements.txt сначала
COPY backend/requirements.txt ./
RUN pip install -r requirements.txt

# Код копируется после (меньше rebuilds)
COPY backend/ ./

# Non-root user для безопасности
USER trendxl

# Railway автоматически устанавливает PORT
CMD ["python", "run_server.py"]
```

**Особенности:**

- ✅ Layer caching для быстрых rebuilds
- ✅ Non-root user (безопасность)
- ✅ Health check
- ✅ Railway PORT поддержка через config.py

### Frontend (Dockerfile.frontend)

```dockerfile
# Multi-stage build для минимального размера
# Stage 1: Build
FROM node:18-alpine AS builder
RUN npm ci --include=dev
RUN npm run build

# Stage 2: Production
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
COPY docker-entrypoint.sh /docker-entrypoint.sh

# Динамический PORT через entrypoint
ENTRYPOINT ["/docker-entrypoint.sh"]
```

**Особенности:**

- ✅ Multi-stage build (финальный образ ~30MB вместо 500MB)
- ✅ Nginx для production (сжатие, кэширование, security headers)
- ✅ Динамический PORT через entrypoint script
- ✅ React Router поддержка (try_files fallback)

### Entrypoint (docker-entrypoint.sh)

```bash
#!/bin/sh
# Заменяет RAILWAY_PORT_PLACEHOLDER на реальный PORT
NGINX_PORT="${PORT:-80}"
sed -i "s/RAILWAY_PORT_PLACEHOLDER/${NGINX_PORT}/g" /etc/nginx/nginx.conf
exec nginx -g "daemon off;"
```

**Зачем нужен:**

- Nginx не может напрямую использовать переменные окружения в `listen`
- Railway динамически назначает PORT (не всегда 80)
- Entrypoint заменяет placeholder на реальный порт при старте

---

## 🐛 Troubleshooting (быстрое решение)

### ❌ Backend не стартует

```bash
# Проверьте API ключи в Railway Variables
ENSEMBLE_API_TOKEN=... (не пустой!)
OPENAI_API_KEY=sk-proj-... (начинается с sk-)
```

**Решение:** Обновите Variables → Restart deployment

### ❌ Frontend не видит Backend

```bash
# Проверьте Frontend Variables
VITE_BACKEND_API_URL=https://${{Backend.RAILWAY_PUBLIC_DOMAIN}}
```

**Решение:** После изменения VITE\_\* → **Redeploy** (не просто restart!)

### ❌ CORS ошибка

```bash
# Backend Variables
CORS_ORIGINS=https://${{Frontend.RAILWAY_PUBLIC_DOMAIN}}
```

**Решение:** Обновите → Restart Backend

### ❌ Nginx Port Binding Error

**Проверьте:**

- `docker-entrypoint.sh` существует
- В `Dockerfile.frontend` есть `ENTRYPOINT ["/docker-entrypoint.sh"]`
- Файл исполняемый: `RUN chmod +x /docker-entrypoint.sh`

**Решение:** Redeploy Frontend

### ❌ Build слишком долгий

**Нормально:**

- Frontend: 2-5 минут (npm ci + npm run build)
- Backend: 3-5 минут (pip install компилирует C-extensions)
- После первого деплоя будет быстрее (Docker layer cache)

---

## 📊 Полезные команды для дебага

### Проверка Backend

```bash
# Health check
curl https://your-backend.up.railway.app/health

# API документация
open https://your-backend.up.railway.app/docs

# Тест конкретного endpoint
curl -X POST https://your-backend.up.railway.app/api/v1/profile \
  -H "Content-Type: application/json" \
  -d '{"username": "charlidamelio"}'
```

### Проверка Frontend

```bash
# Health check
curl https://your-frontend.up.railway.app/health

# Проверка Nginx headers
curl -I https://your-frontend.up.railway.app
```

### Проверка CORS

```bash
curl -H "Origin: https://your-frontend.up.railway.app" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS \
     https://your-backend.up.railway.app/api/v1/analyze
```

### Локальная проверка Docker образов

```bash
# Build Backend локально
docker build -f Dockerfile.backend -t trendxl-backend .
docker run -p 8000:8000 -e PORT=8000 trendxl-backend

# Build Frontend локально
docker build -f Dockerfile.frontend -t trendxl-frontend .
docker run -p 3000:80 -e PORT=80 trendxl-frontend
```

---

## 🎓 Рекомендации для Railway

### 1. Environment Variables

- ✅ **Используйте Railway Variables** для всех секретов (не .env файлы)
- ✅ **VITE\_\* переменные** нужны **во время build**, не runtime
- ✅ **Railway переменные** типа `${{Backend.RAILWAY_PUBLIC_DOMAIN}}` автоматически подставляются

### 2. Auto-Deploy

- ✅ Включите Auto-Deploy для автоматического деплоя при push
- Settings → Deploy → Auto-Deploy: **ON**

### 3. Health Checks

- ✅ Backend: `/health` endpoint
- ✅ Frontend: `/health` endpoint (возвращает "healthy")
- Railway автоматически проверяет и перезапускает при сбоях

### 4. Мониторинг

- 📊 Railway Dashboard → Service → **Metrics**
- CPU, Memory, Network usage в реальном времени
- Free Tier: 500 часов/месяц (примерно 3 сервиса 24/7)

### 5. Logs

- 📝 Deployments → Latest → **View Logs**
- Build logs + Runtime logs
- Поиск по логам: Ctrl+F

---

## 💡 Дополнительные возможности

### Redis Cache (опционально)

```bash
# В Railway проекте:
+ New → Database → Redis

# Backend Variables:
REDIS_URL=${{Redis.REDIS_URL}}
```

### Custom Domain

```bash
# Settings → Networking → Custom Domain
your-domain.com → CNAME → your-app.up.railway.app
```

### Environment Variables (расширенные)

```bash
# Backend
LOG_LEVEL=INFO
MAX_REQUESTS_PER_MINUTE=60
CACHE_PROFILE_TTL=1800
CACHE_POSTS_TTL=900

# Frontend
VITE_APP_VERSION=2.0.0
VITE_GA_TRACKING_ID=UA-XXXXX-Y  # Google Analytics
```

---

## 📚 Дополнительные ресурсы

**Документация:**

- 📖 [RAILWAY_DEPLOYMENT_GUIDE.md](./RAILWAY_DEPLOYMENT_GUIDE.md) - полная пошаговая инструкция
- 🚂 [Railway Official Docs](https://docs.railway.app/)
- 🐳 [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

**API Документация:**

- 🎯 [Ensemble Data (TikTok API)](https://docs.ensembledata.com/)
- 🤖 [OpenAI API](https://platform.openai.com/docs)
- 🔍 [Perplexity API](https://docs.perplexity.ai/)

**Поддержка:**

- 💬 Railway Discord: https://discord.gg/railway
- 🐛 GitHub Issues: создайте issue в вашем репозитории
- 📧 Railway Support: support@railway.app

---

## ✅ Checklist перед деплоем

- [ ] Все изменения закоммичены в Git
- [ ] Push в main ветку
- [ ] API ключи получены (Ensemble, OpenAI, Perplexity)
- [ ] Railway аккаунт создан
- [ ] GitHub репозиторий подключен к Railway
- [ ] Backend сервис настроен (Dockerfile, Variables, Domain)
- [ ] Frontend сервис настроен (Dockerfile, Variables, Domain)
- [ ] Health checks работают (Backend, Frontend)
- [ ] CORS настроен правильно
- [ ] Тестовый анализ профиля выполнен успешно

---

## 🎉 Успешный деплой!

После выполнения всех шагов у вас будет:

- ✅ Backend API: `https://your-backend.up.railway.app`
- ✅ Frontend App: `https://your-frontend.up.railway.app`
- ✅ API Docs: `https://your-backend.up.railway.app/docs`
- ✅ Auto-deploy при push в GitHub
- ✅ Мониторинг и логи в Railway Dashboard
- ✅ Production-ready setup с security best practices

**Поздравляем! 🎊**

---

**Дата создания:** 1 октября 2025  
**Версия:** TrendXL 2.0  
**Платформа:** Railway.app  
**Автор:** TrendXL Team
