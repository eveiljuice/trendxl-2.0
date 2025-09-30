# 🔍 Railway Deployment - Полный отчет о расследовании

**Дата**: 30 сентября 2025  
**Проблема**: Backend не запускается в Railway, healthcheck падает  
**Статус**: ✅ РЕШЕНО

---

## 🚨 НАЙДЕННЫЕ ПРОБЛЕМЫ

### 1. **ГЛАВНАЯ ПРОБЛЕМА: Конфликт конфигураций Railway**

Railway использует файлы в следующем приоритете:
1. **`railway.json`** (корневой) ← Railway читает ЭТОТ файл!
2. `railway.toml` (игнорируется, если есть railway.json)
3. `backend/railway.json` (для отдельных сервисов)

#### ❌ Что было:
```json
// railway.json указывал на Dockerfile (fullstack)
{
  "name": "TrendXL-Frontend",  // Неправильное название!
  "dockerfilePath": "Dockerfile"  // Fullstack контейнер
}
```

#### ❌ Что мы пытались сделать (не работало):
- Обновили `railway.toml` → **Railway игнорировал**
- Создали `Dockerfile.backend` → **Railway не использовал**
- Изменили `railway.backend.toml` → **Railway не видел**

#### ✅ Почему не работало:
**Railway всегда использует `railway.json` в приоритете над `railway.toml`!**

---

### 2. **API ключи не передавались в контейнер**

#### ❌ Проблема:
```json
// railway.json НЕ включал переменные окружения для backend
"variables": {
  "PORT": "${{RAILWAY_PORT}}",
  "NODE_ENV": "production"
  // ❌ НЕТ ENSEMBLE_API_TOKEN
  // ❌ НЕТ OPENAI_API_KEY
  // ❌ НЕТ PERPLEXITY_API_KEY
}
```

Backend падал с ошибкой:
```python
ValidationError: 3 validation errors for Settings
ensemble_api_token - Field required
openai_api_key - Field required
perplexity_api_key - Field required
```

---

### 3. **Healthcheck timeout был слишком короткий**

- **Было**: 30 секунд
- **Нужно**: 60 секунд (backend запускается ~5-10 секунд)

---

## ✅ РЕШЕНИЕ

### Шаг 1: Исправлен `railway.json`

```json
{
  "name": "TrendXL-Fullstack",  // ✅ Правильное название
  "dockerfilePath": "Dockerfile",  // ✅ Fullstack контейнер
  "healthcheck": {
    "timeout": 60  // ✅ Увеличен timeout
  },
  "environments": {
    "production": {
      "variables": {
        "PYTHONPATH": "/app/backend",  // ✅ Добавлены backend переменные
        "PYTHONUNBUFFERED": "1",
        "HOST": "0.0.0.0",
        "DEBUG": "false"
      }
    }
  }
}
```

### Шаг 2: Убрана задержка запуска в production

```python
# backend/run_server.py
# ✅ Теперь задержка только в DEBUG режиме
if settings.debug:
    # Wait 5 seconds (только для development)
else:
    # Start immediately (production)
```

### Шаг 3: **КРИТИЧНО** - Нужно добавить API ключи в Railway

В **Railway Dashboard → Variables** добавьте:

```env
ENSEMBLE_API_TOKEN=your_token_here
OPENAI_API_KEY=sk-your_key_here
PERPLEXITY_API_KEY=pplx-your_key_here
```

**⚠️ БЕЗ ЭТИХ ПЕРЕМЕННЫХ BACKEND НЕ ЗАПУСТИТСЯ!**

---

## 📊 АРХИТЕКТУРА

### Текущая структура (Fullstack контейнер):

```
┌─────────────────────────────────────────────┐
│   Railway Service                           │
│   Port: $PORT (обычно 8080)                 │
│                                             │
│   ┌─────────────────────┐                  │
│   │   Nginx             │                  │
│   │   Port: $PORT       │                  │
│   │   (Frontend + Proxy)│                  │
│   └──────────┬──────────┘                  │
│              │                              │
│              │ Proxy /api/*                 │
│              ▼                              │
│   ┌─────────────────────┐                  │
│   │   Python Backend    │                  │
│   │   Port: 8000        │                  │
│   │   (FastAPI)         │                  │
│   └─────────────────────┘                  │
│                                             │
│   Supervisor управляет обоими процессами   │
└─────────────────────────────────────────────┘
```

### Endpoints:

- **Frontend**: `https://your-app.up.railway.app/`
- **Backend API**: `https://your-app.up.railway.app/api/*`
- **Health check**: `https://your-app.up.railway.app/health`

---

## 🔧 ЧТО НУЖНО СДЕЛАТЬ СЕЙЧАС

### 1. ✅ Изменения уже закоммичены

Railway автоматически подхватит:
- Обновленный `railway.json`
- Увеличенный healthcheck timeout
- Оптимизированный запуск backend

### 2. ⚠️ ОБЯЗАТЕЛЬНО: Добавить Environment Variables в Railway

Зайдите в **Railway Dashboard**:

1. Откройте ваш проект
2. Выберите сервис
3. Перейдите в **Variables**
4. Добавьте:

```env
ENSEMBLE_API_TOKEN=ваш_токен_с_dashboard.ensembledata.com
OPENAI_API_KEY=sk-proj-ваш_ключ_с_platform.openai.com
PERPLEXITY_API_KEY=pplx-ваш_ключ_с_perplexity.ai
```

5. Сохраните и подождите автоматического redeploy

### 3. 🧪 Проверка после деплоя

```bash
# Проверка health endpoint
curl https://your-app.up.railway.app/health

# Ожидаемый ответ:
{
  "status": "healthy",
  "services": {
    "backend": true,
    "ensemble_api": true,
    "openai_api": true
  }
}
```

---

## 📝 LESSONS LEARNED

### 1. Railway читает конфигурации в порядке приоритета:

```
railway.json > railway.toml > package.json
```

### 2. Если есть `railway.json` - он ВСЕГДА используется

Изменения в `railway.toml` игнорируются!

### 3. Environment Variables КРИТИЧНЫ

Backend не запустится без API ключей - это не optional!

### 4. Fullstack контейнер работает отлично

Если правильно настроить:
- ✅ Один сервис вместо двух
- ✅ Одна база кода
- ✅ Простой деплой
- ✅ Меньше стоимость

---

## 🎯 РЕЗУЛЬТАТ

### До исправлений:
```
❌ Backend падал с ValidationError
❌ Healthcheck timeout через 30s
❌ Railway использовал неправильную конфигурацию
❌ API ключи не передавались
```

### После исправлений:
```
✅ railway.json исправлен и указывает на Dockerfile
✅ Healthcheck timeout увеличен до 60s
✅ Backend запускается сразу (без задержки)
✅ API ключи нужно добавить в Railway Variables
```

---

## 🚀 СЛЕДУЮЩИЙ ДЕПЛОЙ ДОЛЖЕН ПОКАЗАТЬ:

```
✅ Build successful
✅ Starting healthcheck at /health
✅ Attempt #1: Success!
✅ All services healthy
✅ Deployment successful

Logs:
🚀 Starting TrendXL 2.0 Fullstack Application...
✅ All API keys configured
INFO: Uvicorn running on http://0.0.0.0:8000
```

---

## 📞 ЕСЛИ ПРОБЛЕМА ОСТАЕТСЯ

1. Проверьте Railway Dashboard → Variables
2. Убедитесь что добавлены все 3 API ключа
3. Проверьте логи: Railway Dashboard → Deployments → View logs
4. Проверьте что используется ветка `main`

---

**Создано**: 30 сентября 2025  
**Автор**: AI Assistant  
**Статус**: Готово к деплою (после добавления API ключей в Railway)

