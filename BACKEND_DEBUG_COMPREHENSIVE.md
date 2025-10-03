# TrendXL 2.0 - Comprehensive Backend Debug

## 🔍 Comprehensive Debugging System

Добавлена полная система отладки для диагностики проблем с backend соединением.

## 🛠 Debug Features Добавлены

### **1. Frontend API Debug (Browser Console)**

После развертывания в консоли браузера будет:

```javascript
🔍 Environment Debug: {
  VITE_BACKEND_API_URL: "",
  PROD: true,
  MODE: "production"
}

🌐 Final API Base URL: ""

🚀 API Request: {
  method: 'GET',
  url: '/health',
  baseURL: '',
  fullURL: '/health',
  timestamp: '2024-01-09T12:00:00.000Z'
}

// При успешном ответе:
✅ API Success: {
  status: 200,
  statusText: 'OK',
  url: '/health',
  data: ['status', 'services'],
  timestamp: '2024-01-09T12:00:00.100Z'
}

// При ошибке:
❌ API Error: {
  message: 'Network Error',
  url: '/health',
  method: 'get',
  status: 502,
  statusText: 'Bad Gateway',
  responseData: {...},
  timestamp: '2024-01-09T12:00:00.100Z'
}

// Специальные типы ошибок:
🔌 Connection refused - backend not responding
🌐 Bad Gateway - nginx cannot reach backend  
🚫 Service Unavailable - backend service down
🌐 Network error - no response from server
```

### **2. Nginx Debug Features**

#### **Debug Endpoints:**
- `GET /nginx-status` → Returns `"nginx_running"` (тест nginx без backend)
- `GET /health` → Проксирует на backend, fallback возвращает `"nginx_ok_backend_down"`

#### **Debug Headers:**
```http
X-Proxy-Status: nginx-to-backend
X-Backend-Port: 8000
X-Debug-Info: nginx-ok-backend-unavailable
```

#### **API Error Responses:**
```json
// 502 Bad Gateway
{
  "error": "Backend not responding",
  "nginx_status": "ok", 
  "backend_port": 8000,
  "debug": "check if python process running"
}

// 503 Service Unavailable  
{
  "error": "Backend service unavailable",
  "nginx_status": "ok",
  "backend_port": 8000, 
  "debug": "backend overloaded or starting"
}

// 504 Gateway Timeout
{
  "error": "Backend timeout",
  "nginx_status": "ok",
  "backend_port": 8000,
  "debug": "backend taking too long to respond"
}
```

#### **Enhanced Logging:**
- `/var/log/nginx/health.log` - Health check requests
- `/var/log/nginx/api.log` - API requests  
- `/var/log/nginx/api_error.log` - API errors

### **3. Startup Debug (Railway Logs)**

В Railway logs будет видно:

```bash
🚀 Starting TrendXL 2.0 Fullstack Application...
📋 Configuration:
   - Frontend Port: 80
   - Backend Port: 8000
   - Python Path: /app/backend
   - Virtual Env: /app/venv

🔍 Environment Variables:
PORT=80
PYTHONPATH=/app/backend
VIRTUAL_ENV=/app/venv

🔧 Processing Nginx configuration...
   Original config preview: [10 lines]
   Updated config preview: [10 lines]
✅ Nginx configuration updated with PORT=80

📁 Creating directories...
✅ Permissions set

🧪 Testing Nginx configuration...
✅ nginx: configuration file test is successful

🔍 Testing backend availability...
   Testing Python imports...
Python executable: /app/venv/bin/python
Python path: ['/app/backend', '/app/venv/lib/python3.10/site-packages', ...]
✅ Backend dependencies OK in venv

🔧 Checking supervisor configuration...
   Supervisor config preview: [20 lines]

🔌 Testing if port 8000 is available...
✅ Port 8000 is available

🎯 Starting services with Supervisor...
   Starting supervisor daemon...
   Supervisor will start:
   - nginx (port 80/PORT)
   - backend (port 8000)

# Через 10 секунд автоматически:
📊 Service Status Check (after 10 seconds):
   Nginx processes: [процессы nginx или ❌ No nginx processes found]
   Python processes: [процессы python или ❌ No python processes found]
   Port usage: [порты 80/8000 или ❌ No processes listening]
   
   Testing internal connectivity:
   - Backend health: 200 (или failed)
   - Nginx status: 200 (или failed)
```

### **4. Supervisor Debug**

#### **Enhanced Logging:**
- `/var/log/supervisor/supervisord.log` - Supervisor daemon (debug level)
- `/var/log/supervisor/backend.log` - Python backend stdout
- `/var/log/supervisor/backend_error.log` - Python backend stderr
- `/var/log/supervisor/nginx.log` - Nginx stdout  
- `/var/log/supervisor/nginx_error.log` - Nginx stderr

#### **Process Monitoring:**
- Automatic process restart on failure
- 3 retry attempts for each service
- Priority startup (backend first, nginx second)

## 🧪 Диагностика проблем

### **После развертывания проверить:**

#### **1. В браузере (F12 → Console):**
```javascript
// Должно показать пустую baseURL:
🌐 Final API Base URL: ""

// Запросы должны идти на относительные пути:
🚀 API Request: { fullURL: '/health' }

// Ошибки покажут точный тип проблемы:
❌ API Error: { status: 502, message: "..." }
```

#### **2. В Network tab браузера:**
- Запросы к `/health`, `/nginx-status`, `/api/*`
- Response headers должны содержать `X-Proxy-Status`

#### **3. Прямые URL тесты:**
```bash
# Тест только nginx (без backend):
curl https://your-app.railway.app/nginx-status
# Ожидается: "nginx_running"

# Тест health check:  
curl https://your-app.railway.app/health
# Успех: JSON от backend
# Fallback: "nginx_ok_backend_down"

# Тест API:
curl https://your-app.railway.app/api/v1/cache/stats
# Успех: JSON от backend  
# Ошибка: JSON с debug info
```

## 🎯 Возможные сценарии после развертывания

### **Сценарий 1: Nginx работает, Backend не работает**
```
/nginx-status → 200 "nginx_running" ✅
/health → 200 "nginx_ok_backend_down" ⚠️  
/api/* → 502 JSON error ❌

Диагностика: Python процесс не запускается
```

### **Сценарий 2: Оба сервиса работают**
```
/nginx-status → 200 "nginx_running" ✅
/health → 200 JSON from backend ✅
/api/* → 200 JSON from backend ✅

Статус: Все работает! 🎉
```

### **Сценарий 3: Ничего не работает**
```
Все запросы → Network error или 500

Диагностика: Контейнер не стартует или падает
```

После развертывания с этой отладкой мы точно поймем где проблема! 🔍
