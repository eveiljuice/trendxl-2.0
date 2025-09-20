# TrendXL 2.0 - Debug CORS Issue

## 🚨 Актуальная проблема

**Ошибка:**
```
Access to XMLHttpRequest at 'https://accurate-nurturing-production.up.railway.app/health' 
from origin 'https://trendxl-20-production-df03.up.railway.app' 
has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

## 🔍 Диагностика

### **Проблема:** Фронтенд все еще использует старый URL!

- **Ожидаемо:** Фронтенд должен делать запросы к `/health` (относительный путь)
- **Реально:** Фронтенд делает запросы к `https://accurate-nurturing-production.up.railway.app/health`
- **Причина:** Переменные окружения не обновились в production сборке

## ✅ Исправления применены

### **1. Принудительное использование относительных путей**

**Файл:** `src/services/backendApi.ts`
```javascript
// Теперь принудительно используем пустую строку в production
const BACKEND_API_BASE_URL = import.meta.env.PROD 
  ? '' // В production ВСЕГДА используем относительные пути
  : (import.meta.env.VITE_BACKEND_API_URL || 'http://localhost:8000');
```

### **2. Добавлена отладка**

Теперь в консоли браузера будет видно:
```javascript
console.log('🔍 Environment Debug:', {
  VITE_BACKEND_API_URL: import.meta.env.VITE_BACKEND_API_URL,
  PROD: import.meta.env.PROD,
  DEV: import.meta.env.DEV,
  MODE: import.meta.env.MODE
});

console.log('🌐 Final API Base URL:', BACKEND_API_BASE_URL);

console.log('🚀 API Request:', {
  method: 'GET',
  url: '/health',
  baseURL: '',
  fullURL: '/health'  // ← Должно быть именно так!
});
```

### **3. Создан основной .env файл**

**Файл:** `.env`
```bash
# Принудительно используем пустую строку для относительных путей
VITE_BACKEND_API_URL=
```

### **4. Обновлен Dockerfile для очистки кеша**

```dockerfile
# Убедимся что используется правильный .env файл
COPY .env .env

# Очистим кеш и соберем заново с правильными переменными  
RUN npm run build
```

## 🧪 Что произойдет после развертывания

### **1. Переменные окружения в браузере:**
```
VITE_BACKEND_API_URL: ""
PROD: true
DEV: false
MODE: "production"
```

### **2. Финальный API Base URL:**
```
Final API Base URL: ""
```

### **3. API запросы:**
```
🚀 API Request: {
  method: 'GET',
  url: '/health',
  baseURL: '',
  fullURL: '/health'
}
```

### **4. Сетевые запросы в браузере:**
- **Было:** `GET https://accurate-nurturing-production.up.railway.app/health`
- **Стало:** `GET https://trendxl-20-production-df03.up.railway.app/health`

### **5. Nginx обработка:**
```
Запрос: GET /health
Nginx: location /health → proxy_pass http://127.0.0.1:8000/health
Backend: получает GET /health ✅
```

## 📋 Проверка после развертывания

1. **Открыть Console в браузере**
2. **Найти отладочные сообщения:**
   - `🔍 Environment Debug`
   - `🌐 Final API Base URL`
   - `🚀 API Request`

3. **Проверить Network tab:**
   - Запросы должны идти на `/health`, `/api/v1/...`
   - Не должно быть запросов к `accurate-nurturing-production.up.railway.app`

## 🚀 Ожидаемый результат

После развертывания:
- ✅ **Фронтенд использует относительные пути**
- ✅ **Все API запросы через nginx прокси**  
- ✅ **CORS ошибки исчезают**
- ✅ **Backend доступен через /api/ routes**

## 🔧 Если проблема остается

Если после развертывания проблема не решена:

1. **Проверить консоль браузера** - найти отладочные сообщения
2. **Проверить Network tab** - куда идут запросы
3. **Очистить кеш браузера** - Ctrl+Shift+R
4. **Проверить что Railway пересобрал** приложение с новым кодом

Railway должен автоматически пересобрать с исправлениями! 🎯
