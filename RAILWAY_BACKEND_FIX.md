# 🔧 Railway Backend Fix - Устранение проблем с запуском

## ❌ Текущая проблема

Backend падает с ошибкой:
```
ValidationError: 3 validation errors for Settings
ensemble_api_token - Field required
openai_api_key - Field required  
perplexity_api_key - Field required
```

## 🔍 Причины проблемы

1. **Отсутствуют API ключи** в Railway environment variables
2. **Используется неправильный Dockerfile** (fullstack вместо standalone backend)
3. Backend пытается запустить nginx + supervisor, а нужен только FastAPI

## ✅ Решение (пошагово)

### Шаг 1: Настройка Environment Variables в Railway

Зайдите в **Railway Dashboard** → **Backend Service** → **Variables** и добавьте:

```env
# Обязательные API ключи
ENSEMBLE_API_TOKEN=ваш_токен_с_dashboard.ensembledata.com
OPENAI_API_KEY=sk-proj-ваш_ключ_с_platform.openai.com
PERPLEXITY_API_KEY=pplx-ваш_ключ_с_perplexity.ai

# Server Configuration
PORT=8000
HOST=0.0.0.0
DEBUG=False

# Redis (опционально, если нужен)
REDIS_URL=redis://localhost:6379

# CORS для frontend
CORS_ORIGINS=https://trendxl-20-frontend-production.up.railway.app
```

**⚠️ ВАЖНО:** Замените `ваш_токен`, `ваш_ключ` на реальные значения!

### Шаг 2: Настройка правильного Dockerfile в Railway

В настройках **Backend Service** в Railway:

#### Вариант A: Использовать новый Dockerfile.backend

1. **Settings** → **Deploy**
2. **Docker Path**: `Dockerfile.backend`
3. **Root Directory**: оставить пустым (корень проекта)

#### Вариант B: Использовать Railway TOML

1. В корне проекта уже есть `railway.backend.toml`
2. В Railway Settings → Deploy
3. Убедитесь что используется этот конфиг

### Шаг 3: Коммит изменений

```bash
# Закоммитим новые файлы
git add Dockerfile.backend railway.backend.toml .dockerignore.backend RAILWAY_BACKEND_FIX.md
git commit -m "Add standalone backend Dockerfile for Railway"
git push origin main
```

### Шаг 4: Redeploy Backend в Railway

1. Зайдите в Railway → Backend Service
2. Нажмите **Deploy** → **Redeploy**
3. Или просто push в GitHub (auto-deploy)

### Шаг 5: Проверка запуска

После деплоя проверьте логи:

```
✅ Успешный запуск должен показать:
🚀 Starting TrendXL 2.0 Backend Server...
📍 Host: 0.0.0.0
🔌 Port: 8000
✅ Backend loaded successfully
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Шаг 6: Тест API

```bash
# Проверка health endpoint
curl https://trendxl-20-backend-production.up.railway.app/health

# Ожидаемый ответ:
{
  "status": "healthy",
  "services": {
    "backend": true,
    "cache": false,
    "ensemble_api": true,
    "openai_api": true
  }
}
```

## 📋 Checklist

- [ ] Environment variables добавлены в Railway
- [ ] Все 3 API ключа установлены (ENSEMBLE, OPENAI, PERPLEXITY)
- [ ] Dockerfile.backend используется для сборки
- [ ] Backend успешно запустился (проверить логи)
- [ ] Health endpoint отвечает
- [ ] Frontend может подключиться к backend

## 🚨 Частые ошибки

### Ошибка 1: "Field required" для API ключей

**Причина**: Не установлены environment variables  
**Решение**: Добавить все ключи в Railway Variables (см. Шаг 1)

### Ошибка 2: Backend запускает nginx

**Причина**: Используется fullstack Dockerfile  
**Решение**: Указать `Dockerfile.backend` в Railway Settings

### Ошибка 3: "Module not found"

**Причина**: Неправильный PYTHONPATH  
**Решение**: В Dockerfile.backend уже установлен `PYTHONPATH=/app/backend`

### Ошибка 4: CORS errors от frontend

**Причина**: Frontend URL не в CORS_ORIGINS  
**Решение**: Добавить в Railway Variables:
```
CORS_ORIGINS=https://trendxl-20-frontend-production.up.railway.app
```

## 📊 Различия Dockerfile vs Dockerfile.backend

### Dockerfile (fullstack - НЕ ИСПОЛЬЗУЕМ)
```dockerfile
# Multi-stage: Frontend + Backend + Nginx
FROM node:18-alpine AS frontend-builder
FROM python:3.10-slim AS backend-builder  
FROM nginx:alpine AS production
# Запускает: nginx + supervisor + backend
```

### Dockerfile.backend (standalone - ИСПОЛЬЗУЕМ)
```dockerfile
# Single stage: Only Backend
FROM python:3.10-slim
# Запускает: только FastAPI/Uvicorn
CMD ["python", "run_server.py"]
```

## 🔗 Архитектура после исправления

```
┌─────────────────────────────────────┐
│   Railway Frontend Service          │
│   trendxl-20-frontend-production    │
│   Nginx + Static React Build        │
└──────────────┬──────────────────────┘
               │ HTTPS
               ▼
┌─────────────────────────────────────┐
│   Railway Backend Service            │
│   trendxl-20-backend-production     │
│   Python + FastAPI + Uvicorn        │
│   Environment Variables:             │
│   - ENSEMBLE_API_TOKEN              │
│   - OPENAI_API_KEY                  │
│   - PERPLEXITY_API_KEY              │
└─────────────────────────────────────┘
```

## 📝 После успешного запуска

1. Frontend автоматически подключится к backend
2. Можно тестировать анализ TikTok профилей
3. Все API запросы будут проходить через HTTPS
4. CORS настроен правильно

## 🆘 Если проблема не решена

1. **Проверьте логи** в Railway Dashboard
2. **Экспортируйте переменные** и убедитесь что они видны
3. **Пересоберите** с нуля: Settings → Delete → Deploy заново
4. **Проверьте** что используется ветка `main` в GitHub

---

**Создано**: 30 сентября 2025  
**Последнее обновление**: 30 сентября 2025

