# 🚀 Railway Services Setup - TrendXL 2.0

## 📋 Обзор конфигураций

TrendXL 2.0 настроен для развертывания в виде **двух отдельных сервисов** на Railway:

1. **Frontend Service** - React + Vite + Nginx 
2. **Backend Service** - Python FastAPI

---

## 📁 Структура Railway конфигураций:

```
trendxl-2.0/
├── 🎨 FRONTEND CONFIGS:
│   ├── railway.frontend.json     # Frontend service config
│   ├── Dockerfile               # React + Nginx container  
│   ├── .dockerignore.frontend   # Frontend build optimization
│   └── nginx.default.conf.template
│
├── 🚀 BACKEND CONFIGS:
│   ├── railway.json             # Main backend config (root)
│   ├── railway.backend.json     # Alternative backend config
│   ├── Dockerfile.backend       # Python container
│   ├── .dockerignore.backend    # Backend build optimization  
│   └── backend/
│       ├── railway.json         # Local backend config
│       └── Dockerfile           # Local Python container
│
└── 📚 DOCUMENTATION:
    └── RAILWAY_SERVICES_SETUP.md  # This file
```

---

## 🛠️ Настройка Railway Services:

### **1. Frontend Service Setup**

**В Railway Dashboard:**

1. **Create New Service** → **From GitHub Repository**
2. **Service Name**: `TrendXL Frontend` 
3. **Settings → Build:**
   ```
   Builder: Dockerfile
   Dockerfile Path: Dockerfile
   Root Directory: . (project root)
   ```
4. **Settings → Environment Variables:**
   ```bash
   NODE_ENV=production
   VITE_APP_TITLE=TrendXL 2.0  
   VITE_BACKEND_URL=https://${{Backend.RAILWAY_PUBLIC_DOMAIN}}
   ```
5. **Settings → Networking:**
   ```
   Port: 80
   Public Domain: Enable
   ```

**Или используйте `railway.frontend.json`:**
```bash
railway up --config railway.frontend.json
```

---

### **2. Backend Service Setup**

**В Railway Dashboard:**

1. **Create New Service** → **From GitHub Repository** 
2. **Service Name**: `TrendXL Backend API`
3. **Settings → Build:**
   ```
   Builder: Dockerfile
   Dockerfile Path: Dockerfile.backend
   Root Directory: . (project root)
   ```
4. **Settings → Environment Variables:**
   ```bash
   PYTHONPATH=/app
   PYTHONUNBUFFERED=1
   HOST=0.0.0.0
   PORT=${{RAILWAY_PORT}}
   DEBUG=false
   ENVIRONMENT=production
   
   # API Keys (добавьте ваши ключи):
   ENSEMBLE_API_TOKEN=your_ensemble_token
   OPENAI_API_KEY=your_openai_key  
   PERPLEXITY_API_KEY=your_perplexity_key
   ```
5. **Settings → Networking:**
   ```
   Port: 8000
   Public Domain: Enable
   Private Domain: Enable
   ```

**Или используйте конфигурационные файлы:**
```bash
# Вариант 1: Основной config
railway up --config railway.json

# Вариант 2: Альтернативный config  
railway up --config railway.backend.json

# Вариант 3: Из папки backend
cd backend && railway up
```

---

## 🔗 Связывание сервисов:

### **Frontend → Backend связь:**
```bash
# В Frontend Service environment:
VITE_BACKEND_URL=https://${{Backend.RAILWAY_PUBLIC_DOMAIN}}
VITE_API_BASE_URL=${{Backend.RAILWAY_PRIVATE_DOMAIN}}
```

### **Backend → Frontend связь:**
```bash  
# В Backend Service environment:
CORS_ORIGINS=https://${{Frontend.RAILWAY_PUBLIC_DOMAIN}},http://localhost:5173
FRONTEND_URL=${{Frontend.RAILWAY_PUBLIC_DOMAIN}}
```

---

## 📊 Конфигурации по файлам:

| Файл | Назначение | Dockerfile | Сервис |
|------|------------|------------|--------|
| `railway.frontend.json` | Frontend service | `Dockerfile` | React + Nginx |
| `railway.json` | Backend service (main) | `Dockerfile.backend` | Python API |
| `railway.backend.json` | Backend service (alt) | `Dockerfile.backend` | Python API |
| `backend/railway.json` | Backend local deploy | `Dockerfile` | Python API |

---

## 🚦 Проверка развертывания:

### **Frontend Service должен показать:**
```
✅ Build: Dockerfile 
✅ FROM node:18-alpine AS frontend-builder
✅ FROM nginx:alpine AS frontend  
✅ Container started on port 80
✅ Health check: GET / → 200 OK
```

### **Backend Service должен показать:**
```  
✅ Build: Dockerfile.backend
✅ FROM python:3.10-slim-bullseye
✅ Python 3.10.x installed
✅ Container started on port 8000  
✅ Health check: GET /health → 200 OK
```

---

## 🔧 Устранение неполадок:

### **❌ Frontend показывает ошибку "python not found"**
→ **Проблема**: Railway использует `Dockerfile.backend` вместо `Dockerfile`
→ **Решение**: Проверьте `dockerfilePath` в настройках Frontend сервиса

### **❌ Backend показывает ошибки Node.js/npm**  
→ **Проблема**: Railway использует `Dockerfile` вместо `Dockerfile.backend`
→ **Решение**: Обновите `dockerfilePath` в настройках Backend сервиса

### **❌ CORS ошибки между Frontend и Backend**
→ **Решение**: Проверьте переменные `VITE_BACKEND_URL` и `CORS_ORIGINS`

### **❌ API ключи не работают**
→ **Решение**: Убедитесь, что все API токены добавлены в Backend environment

---

## 📋 Checklist развертывания:

### Frontend Service:
- [ ] Service Name: `TrendXL Frontend`
- [ ] Dockerfile Path: `Dockerfile` 
- [ ] Environment: `NODE_ENV=production`
- [ ] Environment: `VITE_BACKEND_URL` настроен
- [ ] Port: 80
- [ ] Public Domain: Enabled

### Backend Service:  
- [ ] Service Name: `TrendXL Backend API`
- [ ] Dockerfile Path: `Dockerfile.backend`
- [ ] Environment: Python variables настроены
- [ ] Environment: API ключи добавлены
- [ ] Port: 8000 
- [ ] Public + Private Domain: Enabled

### Cross-Service:
- [ ] Frontend может достучаться до Backend API
- [ ] CORS настроен правильно
- [ ] Health checks работают
- [ ] Логи не показывают ошибок

---

## 📞 Помощь:

Если развертывание не работает:

1. **Проверьте логи сборки** - правильный ли Dockerfile используется?
2. **Проверьте environment variables** - все ли переменные настроены?
3. **Проверьте health checks** - отвечают ли эндпоинты?
4. **Проверьте cross-service связь** - могут ли сервисы общаться?

Railway логи покажут точную причину проблем с развертыванием.
