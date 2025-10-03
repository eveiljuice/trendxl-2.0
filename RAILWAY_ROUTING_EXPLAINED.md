# 🚂 Railway Routing - Как это работает

## ⚠️ ВАЖНО: Роуты НЕ настраиваются в railway.toml!

**Railway автоматически обрабатывает маршрутизацию между сервисами.**

Вам **НЕ НУЖНО** настраивать роуты вручную. Railway делает это за вас! 🎉

---

## 🎯 Как работает маршрутизация на Railway

### 1. Автоматическая маршрутизация

```
Railway Project: TrendXL 2.0
│
├─ Backend Service
│  └─ Domain: https://backend-xyz.up.railway.app
│     └─ Railway автоматически назначает публичный URL
│
└─ Frontend Service
   └─ Domain: https://frontend-abc.up.railway.app
      └─ Railway автоматически назначает публичный URL
```

**Railway автоматически:**

- ✅ Создает уникальные домены для каждого сервиса
- ✅ Настраивает HTTPS и SSL сертификаты
- ✅ Обеспечивает связь между сервисами
- ✅ Назначает динамические порты через `${{RAILWAY_PORT}}`

---

## 🔗 Как связать Frontend и Backend

### Метод 1: Использование Railway переменных (РЕКОМЕНДУЕТСЯ)

**В Frontend сервисе:**

```bash
# Railway → Frontend Service → Variables
VITE_BACKEND_API_URL=https://${{Backend.RAILWAY_PUBLIC_DOMAIN}}
```

**Что происходит:**

1. Railway автоматически заменяет `${{Backend.RAILWAY_PUBLIC_DOMAIN}}` на реальный URL Backend
2. Vite использует эту переменную во время build
3. Frontend знает, куда отправлять API запросы

**В Backend сервисе:**

```bash
# Railway → Backend Service → Variables
CORS_ORIGINS=https://${{Frontend.RAILWAY_PUBLIC_DOMAIN}}
```

**Что происходит:**

1. Railway автоматически заменяет `${{Frontend.RAILWAY_PUBLIC_DOMAIN}}` на реальный URL Frontend
2. Backend разрешает CORS запросы от Frontend
3. Связь работает автоматически! ✨

---

## 📋 Правильная структура проекта на Railway

### Вариант 1: Два отдельных сервиса (РЕКОМЕНДУЕТСЯ)

```
Railway Project: TrendXL 2.0
│
├─ Service 1: Backend
│  ├─ GitHub: main branch
│  ├─ Root Directory: . (корень репозитория)
│  ├─ Dockerfile: Dockerfile.backend
│  ├─ Config: railway.backend.json
│  ├─ Variables:
│  │  ├─ ENSEMBLE_API_TOKEN=your_token
│  │  ├─ OPENAI_API_KEY=your_key
│  │  ├─ PORT=${{RAILWAY_PORT}}
│  │  └─ CORS_ORIGINS=https://${{Frontend.RAILWAY_PUBLIC_DOMAIN}}
│  └─ Domain: https://backend-xyz.up.railway.app
│
└─ Service 2: Frontend
   ├─ GitHub: main branch
   ├─ Root Directory: . (корень репозитория)
   ├─ Dockerfile: Dockerfile.frontend
   ├─ Config: railway.frontend.json
   ├─ Variables:
   │  ├─ NODE_ENV=production
   │  └─ VITE_BACKEND_API_URL=https://${{Backend.RAILWAY_PUBLIC_DOMAIN}}
   └─ Domain: https://frontend-abc.up.railway.app
```

---

## 🚀 Как задеплоить (пошагово)

### Шаг 1: Создать Backend Service

```bash
Railway Dashboard → New Project → Deploy from GitHub repo
```

1. Выбрать репозиторий `trendxl-2.0`
2. Railway создаст первый сервис
3. **Settings → Build:**

   - Builder: `DOCKERFILE`
   - Dockerfile Path: `Dockerfile.backend`
   - Docker Build Context: `.` (корень)

4. **Variables:** (добавить все переменные)

   ```bash
   ENSEMBLE_API_TOKEN=your_token_here
   OPENAI_API_KEY=sk-proj-your_key_here
   PERPLEXITY_API_KEY=pplx-your_key_here
   HOST=0.0.0.0
   PORT=${{RAILWAY_PORT}}
   DEBUG=false
   CORS_ORIGINS=https://${{Frontend.RAILWAY_PUBLIC_DOMAIN}}
   ```

5. **Networking → Generate Domain**
6. Скопировать Backend URL: `https://backend-xyz.up.railway.app`

### Шаг 2: Создать Frontend Service

```bash
Railway Project → + New → GitHub Repo (тот же репозиторий)
```

1. Railway создаст второй сервис
2. **Settings → Build:**

   - Builder: `DOCKERFILE`
   - Dockerfile Path: `Dockerfile.frontend`
   - Docker Build Context: `.`

3. **Variables:** (добавить переменные)

   ```bash
   NODE_ENV=production
   VITE_APP_TITLE=TrendXL 2.0
   VITE_BACKEND_API_URL=https://${{Backend.RAILWAY_PUBLIC_DOMAIN}}
   ```

4. **Networking → Generate Domain**
5. Скопировать Frontend URL: `https://frontend-abc.up.railway.app`

### Шаг 3: Проверить маршрутизацию

1. **Backend health check:**

   ```bash
   curl https://backend-xyz.up.railway.app/health
   ```

2. **Frontend loading:**

   ```bash
   curl https://frontend-abc.up.railway.app
   ```

3. **Check Frontend → Backend connection:**
   - Открыть Frontend в браузере
   - F12 → Console
   - Проверить: `VITE_BACKEND_API_URL` должен быть правильным
   - Ввести TikTok профиль и запустить анализ

---

## 🔍 Почему НЕ нужен railway.toml для роутинга?

### ❌ Неправильное понимание:

```toml
# ЭТО НЕ РАБОТАЕТ ТАК НА RAILWAY!
[routes]
  frontend = "/"
  backend = "/api"
```

**Почему не работает:**

- Railway не использует такую маршрутизацию
- Каждый сервис получает свой собственный домен
- Нет "корневого" домена с подпутями `/api` или `/frontend`

### ✅ Правильный подход:

```bash
# Frontend Service Variables
VITE_BACKEND_API_URL=https://${{Backend.RAILWAY_PUBLIC_DOMAIN}}

# Backend Service Variables
CORS_ORIGINS=https://${{Frontend.RAILWAY_PUBLIC_DOMAIN}}
```

**Почему работает:**

- Railway автоматически подставляет реальные домены
- Frontend отправляет запросы напрямую на Backend домен
- Backend разрешает CORS от Frontend домена
- Все работает автоматически! 🎉

---

## 📊 Схема работы маршрутизации

```
User Browser
    │
    │ 1. Открывает: https://frontend-abc.up.railway.app
    ▼
Railway Load Balancer (Frontend)
    │
    │ 2. Отдает static files (HTML, JS, CSS)
    ▼
User Browser (React App)
    │
    │ 3. JavaScript делает API запросы к:
    │    https://backend-xyz.up.railway.app/api/v1/analyze
    ▼
Railway Load Balancer (Backend)
    │
    │ 4. Проверяет CORS (Origin: frontend-abc.up.railway.app)
    │ 5. Если OK → обрабатывает запрос
    ▼
Backend (FastAPI)
    │
    │ 6. Обрабатывает запрос
    │ 7. Возвращает JSON response
    ▼
User Browser (React App)
    │
    │ 8. Отображает результаты
    ▼
User sees results! 🎉
```

---

## 🎓 Railway переменные для связи сервисов

### Доступные Railway переменные:

```bash
# Публичные домены (доступны извне)
${{Backend.RAILWAY_PUBLIC_DOMAIN}}    # backend-xyz.up.railway.app
${{Frontend.RAILWAY_PUBLIC_DOMAIN}}   # frontend-abc.up.railway.app

# Приватные домены (внутри Railway сети)
${{Backend.RAILWAY_PRIVATE_DOMAIN}}   # backend.railway.internal:8000
${{Frontend.RAILWAY_PRIVATE_DOMAIN}}  # frontend.railway.internal:80

# Динамический порт (назначается Railway)
${{RAILWAY_PORT}}                      # например: 8000, 3000, и т.д.

# Static URL (устаревший, не рекомендуется)
${{Backend.RAILWAY_STATIC_URL}}       # используйте PUBLIC_DOMAIN вместо
```

### Когда использовать что:

**Public Domain (рекомендуется):**

```bash
# Frontend → Backend (через интернет)
VITE_BACKEND_API_URL=https://${{Backend.RAILWAY_PUBLIC_DOMAIN}}

# Backend → Frontend (для CORS)
CORS_ORIGINS=https://${{Frontend.RAILWAY_PUBLIC_DOMAIN}}
```

**Private Domain (для внутренней связи):**

```bash
# Если бы у вас были дополнительные сервисы, общающиеся внутри Railway
INTERNAL_API_URL=http://${{Backend.RAILWAY_PRIVATE_DOMAIN}}
```

---

## 🔧 Файлы конфигурации для Railway

### Используемые файлы (в порядке приоритета):

1. **railway.backend.json** - Backend сервис конфигурация

   ```json
   {
     "$schema": "https://railway.app/railway.schema.json",
     "name": "TrendXL Backend API",
     "build": {
       "builder": "DOCKERFILE",
       "dockerfilePath": "Dockerfile.backend"
     }
   }
   ```

2. **railway.frontend.json** - Frontend сервис конфигурация
   ```json
   {
     "$schema": "https://railway.app/railway.schema.json",
     "name": "TrendXL Frontend",
     "build": {
       "builder": "DOCKERFILE",
       "dockerfilePath": "Dockerfile.frontend"
     }
   }
   ```

### НЕ используемые файлы:

- ❌ `railway.toml` - устаревший, не используется для multi-service
- ❌ `railway.json` - если есть специфичные для сервисов файлы

---

## ✅ Checklist правильной настройки

### Backend Service:

- [ ] Dockerfile Path: `Dockerfile.backend`
- [ ] Variables: API ключи установлены
- [ ] Variables: `PORT=${{RAILWAY_PORT}}`
- [ ] Variables: `CORS_ORIGINS=https://${{Frontend.RAILWAY_PUBLIC_DOMAIN}}`
- [ ] Domain: сгенерирован и скопирован
- [ ] Health check: `/health` работает

### Frontend Service:

- [ ] Dockerfile Path: `Dockerfile.frontend`
- [ ] Variables: `NODE_ENV=production`
- [ ] Variables: `VITE_BACKEND_API_URL=https://${{Backend.RAILWAY_PUBLIC_DOMAIN}}`
- [ ] Domain: сгенерирован
- [ ] Открывается в браузере
- [ ] Console: `VITE_BACKEND_API_URL` правильный

### Integration:

- [ ] Frontend может делать запросы к Backend
- [ ] CORS работает (нет ошибок в Console)
- [ ] Полный флоу анализа работает

---

## 🐛 Troubleshooting маршрутизации

### Проблема 1: Frontend не видит Backend

**Симптомы:**

```
❌ API Error: Network error - no response from server
ERR_NAME_NOT_RESOLVED
```

**Решение:**

1. Проверить `VITE_BACKEND_API_URL` в Frontend Variables
2. Убедиться что URL правильный: `https://${{Backend.RAILWAY_PUBLIC_DOMAIN}}`
3. **Redeploy** Frontend (не просто Restart!) - Vite переменные используются во время build

### Проблема 2: CORS ошибка

**Симптомы:**

```
Access to XMLHttpRequest has been blocked by CORS policy
```

**Решение:**

1. Проверить `CORS_ORIGINS` в Backend Variables
2. Убедиться что URL правильный: `https://${{Frontend.RAILWAY_PUBLIC_DOMAIN}}`
3. Restart Backend

### Проблема 3: Неправильный домен в переменных

**Симптомы:**

```
VITE_BACKEND_API_URL=https://${{Backend.RAILWAY_PUBLIC_DOMAIN}}
# Не заменяется на реальный URL
```

**Решение:**

1. Убедиться что имя Backend сервиса - **"Backend"** (с большой буквы)
2. Или использовать фактическое имя: `${{TrendXL-Backend.RAILWAY_PUBLIC_DOMAIN}}`
3. Redeploy Frontend

---

## 📚 Дополнительные ресурсы

**Официальная документация Railway:**

- 🚂 [Railway Docs - Deployment](https://docs.railway.app/deploy/deployments)
- 🔗 [Railway Docs - Variables](https://docs.railway.app/deploy/variables)
- 🌐 [Railway Docs - Networking](https://docs.railway.app/deploy/networking)

**Документация TrendXL:**

- 📖 [RAILWAY_DEPLOYMENT_GUIDE.md](./RAILWAY_DEPLOYMENT_GUIDE.md) - Полная инструкция
- 🚀 [RAILWAY_QUICKSTART_RU.md](./RAILWAY_QUICKSTART_RU.md) - Быстрый старт
- 🏗️ [ARCHITECTURE.md](./ARCHITECTURE.md) - Архитектура проекта

---

## 💡 Ключевые выводы

1. **Railway автоматически обрабатывает маршрутизацию** - вам не нужно ничего настраивать вручную

2. **Используйте Railway переменные** типа `${{Backend.RAILWAY_PUBLIC_DOMAIN}}` для связи сервисов

3. **Создавайте отдельные сервисы** для Frontend и Backend через Railway UI

4. **railway.toml НЕ используется для роутинга** - только для базовой конфигурации отдельного сервиса

5. **Файлы railway.backend.json и railway.frontend.json** уже настроены правильно

6. **VITE\_\* переменные** нужны **во время build**, поэтому после изменения нужен **Redeploy**

---

**Версия:** TrendXL 2.0  
**Дата:** 1 октября 2025  
**Статус:** ✅ Production Ready
