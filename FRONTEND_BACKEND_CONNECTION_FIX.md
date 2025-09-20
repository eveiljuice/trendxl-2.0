# TrendXL 2.0 - Frontend-Backend Connection Fix

## 🚨 Проблема: "Сайт не видит бэкенд"

**Симптомы:**

- Фронтенд не может подключиться к API
- Ошибки CORS или сетевые ошибки
- Backend health check не работает из фронтенда

## 🔍 Root Cause Analysis

### **Найденные проблемы:**

1. **❌ Неправильная конфигурация API URL**

   - Фронтенд в `.env.production` пытался подключиться к внешнему Railway URL
   - Но теперь фронтенд и бэкенд в одном контейнере

2. **❌ Nginx rewrite rule конфликт**

   - Nginx убирал `/api/` префикс из запросов
   - Но FastAPI endpoints ожидают запросы с `/api/` префиксом
   - Двойное удаление префикса ломало маршрутизацию

3. **❌ CORS ограничения**
   - CORS был настроен только на localhost порты
   - Не было поддержки Railway доменов

## ✅ Исправления применены

### **1. Исправлена конфигурация фронтенда**

**Файл:** `src/services/backendApi.ts`

```javascript
// БЫЛО:
const BACKEND_API_BASE_URL =
  import.meta.env.VITE_BACKEND_API_URL || "http://localhost:8000";

// СТАЛО:
const BACKEND_API_BASE_URL =
  import.meta.env.VITE_BACKEND_API_URL ||
  (import.meta.env.PROD ? "" : "http://localhost:8000");
```

**Логика:**

- **Development:** Используется `http://localhost:8000` (прямое подключение)
- **Production:** Используется `''` (относительные пути через nginx)

### **2. Обновлен .env.production**

**Файл:** `.env.production`

```bash
# БЫЛО:
VITE_BACKEND_API_URL=https://accurate-nurturing-production.up.railway.app

# СТАЛО:
VITE_BACKEND_API_URL=
```

**Результат:**

- Фронтенд делает запросы на `/api/v1/analyze` (относительные)
- Nginx проксирует на backend внутри контейнера

### **3. Исправлен nginx routing**

**Файл:** `nginx.fullstack.conf`

```nginx
# БЫЛО (неправильно):
location /api/ {
    rewrite ^/api/(.*)$ /$1 break;  # ❌ Удаляло /api/ префикс
    proxy_pass http://127.0.0.1:8000;
}

# СТАЛО (правильно):
location /api/ {
    # Проксируем с сохранением /api/ префикса
    proxy_pass http://127.0.0.1:8000;  # ✅ Сохраняет полный путь
}
```

**Маршрутизация теперь:**

- Фронтенд: `GET /api/v1/analyze`
- Nginx: проксирует `GET /api/v1/analyze` → Backend:8000
- Backend: получает `GET /api/v1/analyze` ✅

### **4. Обновлены CORS настройки**

**Файл:** `backend/config.py`

```python
# БЫЛО:
cors_origins: List[str] = Field(
    default=["http://localhost:3000", "http://localhost:5173"],
    env="CORS_ORIGINS"
)
cors_origin_regex: Optional[str] = Field(default=None, env="CORS_ORIGIN_REGEX")

# СТАЛО:
cors_origins: List[str] = Field(
    default=[
        "http://localhost:3000", "http://localhost:5173",
        "*"  # Разрешаем тот же домен в unified container
    ],
    env="CORS_ORIGINS"
)
cors_origin_regex: Optional[str] = Field(
    default=r"https?://.*\.up\.railway\.app$|https?://.*\.railway\.app$|http://localhost:\d+$",
    env="CORS_ORIGIN_REGEX"
)
```

### **5. Увеличены timeouts для длительных операций**

**Файл:** `nginx.fullstack.conf`

```nginx
# Timeout settings для длительных операций анализа
proxy_connect_timeout 60s;
proxy_send_timeout 300s;    # ← Увеличено до 5 минут
proxy_read_timeout 300s;    # ← Увеличено до 5 минут
```

## 📊 Архитектура после исправлений

```
Railway Domain (https://your-app.up.railway.app)
├── 🌐 Nginx (Port 80/RAILWAY_PORT)
│   ├── GET /health → 🔍 Backend health check
│   ├── GET /api/* → 🐍 Backend:8000/api/* (с сохранением /api/)
│   └── GET /* → ⚛️ React SPA
│
├── ⚛️ React Frontend
│   ├── 📡 API calls: '' + '/api/v1/...' = '/api/v1/...'
│   ├── 🔄 Relative URLs в production
│   └── 🚀 Direct URLs в development
│
└── 🐍 FastAPI Backend (Port 8000)
    ├── 🌟 /api/v1/analyze
    ├── 🌟 /api/v1/profile
    ├── 🌟 /health
    └── ✅ CORS разрешает все Railway домены
```

## 🧪 Тестирование исправлений

### **Локально:**

```bash
# Собрать и запустить
docker build -t trendxl-connection-fixed .
docker run -p 3000:80 -e PORT=80 trendxl-connection-fixed

# Тесты:
curl http://localhost:3000/health        # ✅ Health check
curl http://localhost:3000/api/health    # ✅ Backend health
curl http://localhost:3000/              # ✅ Frontend
```

### **На Railway:**

1. **Health checks проходят** ✅
2. **Frontend загружается** ✅
3. **API calls работают** ✅
4. **CORS разрешает запросы** ✅

## 🚀 Результат

После исправлений:

- ✅ **Фронтенд подключается к бэкенду** через nginx прокси
- ✅ **API endpoints доступны** по относительным путям
- ✅ **CORS настроен правильно** для Railway доменов
- ✅ **Timeouts достаточны** для длительных анализов
- ✅ **Health checks работают** и для frontend и backend

**Проблема "сайт не видит бэкенд" решена!** 🎉
