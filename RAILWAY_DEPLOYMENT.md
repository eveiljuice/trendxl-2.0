# 🚀 TrendXL 2.0 - Railway Deployment Guide

Полное руководство по развертыванию TrendXL 2.0 на Railway с отдельными сервисами для backend и frontend.

## 📋 Предварительные требования

1. **Аккаунт Railway** - зарегистрируйтесь на [railway.app](https://railway.app)
2. **API ключи:**
   - Ensemble Data API Token - [dashboard.ensembledata.com](https://dashboard.ensembledata.com/)
   - OpenAI API Key - [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
3. **GitHub репозиторий** с кодом TrendXL 2.0

## 🏗️ Архитектура деплоя

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │     Redis       │
│  (React/Nginx)  │────│  (FastAPI)      │────│   (Railway)     │
│  Port: 80       │    │  Port: 8000     │    │   Port: 6379    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 Шаг 1: Подготовка проекта

### 1.1 Коммит изменений в GitHub

```bash
git add .
git commit -m "feat: Railway deployment configuration"
git push origin main
```

### 1.2 Проверка файлов конфигурации

Убедитесь, что созданы следующие файлы:

- ✅ `railway.json` (корневой, для frontend)
- ✅ `Dockerfile` (корневой, для frontend)  
- ✅ `nginx.conf` (конфигурация Nginx)
- ✅ `backend/railway.json` (для backend)
- ✅ `backend/Dockerfile` (уже существует)
- ✅ `backend/.env.production` (шаблон переменных)
- ✅ `.env.production` (шаблон для frontend)

## 🚀 Шаг 2: Деплой Backend (FastAPI)

### 2.1 Создание Backend сервиса

1. Перейдите на [railway.app](https://railway.app)
2. Нажмите **"New Project"**
3. Выберите **"Deploy from GitHub repo"**
4. Выберите ваш репозиторий `trendxl-2.0`
5. Railway автоматически обнаружит несколько сервисов

### 2.2 Настройка Backend сервиса

1. Выберите сервис с **Python/FastAPI** (должен определиться автоматически по `backend/Dockerfile`)
2. Перейдите в **Settings → Environment**
3. Установите **Root Directory**: `backend`
4. Добавьте переменные окружения:

```env
ENSEMBLE_API_TOKEN=your_actual_ensemble_token
OPENAI_API_KEY=your_actual_openai_key
DEBUG=false
HOST=0.0.0.0
PORT=$PORT
PYTHONPATH=/app
PYTHONUNBUFFERED=1
```

### 2.3 Добавление Redis

1. В проекте нажмите **"+ New"**
2. Выберите **"Database"** → **"Add Redis"**
3. Railway автоматически создаст переменные:
   - `REDIS_URL`
   - `REDIS_PRIVATE_URL` (используйте эту для внутренних подключений)

### 2.4 Обновление CORS для Backend

После деплоя backend получит домен вида `https://backend-production-xxx.up.railway.app`

Добавьте переменную окружения:
```env
CORS_ORIGINS=["https://your-frontend-domain.railway.app"]
```

## 🎨 Шаг 3: Деплой Frontend (React)

### 3.1 Создание Frontend сервиса

1. В том же проекте нажмите **"+ New"** → **"GitHub Repo"**
2. Выберите тот же репозиторий
3. Railway создаст второй сервис

### 3.2 Настройка Frontend сервиса

1. Перейдите в **Settings → Environment**
2. Установите **Root Directory**: `.` (корень проекта)
3. Добавьте переменную окружения:

```env
VITE_BACKEND_API_URL=https://your-backend-domain.railway.app
```

### 3.3 Настройка Build Command

В **Settings → Build**:
- **Build Command**: `npm run build`
- **Start Command**: автоматически (Nginx)

## 🔗 Шаг 4: Связывание сервисов

### 4.1 Получение доменов

После деплоя оба сервиса получат домены:
- Backend: `https://backend-production-xxx.up.railway.app`
- Frontend: `https://frontend-production-xxx.up.railway.app`

### 4.2 Обновление CORS

1. Перейдите в Backend сервис
2. В **Variables** обновите `CORS_ORIGINS`:

```json
["https://your-actual-frontend-domain.railway.app", "https://*.railway.app"]
```

### 4.3 Обновление Frontend API URL

1. Перейдите в Frontend сервис  
2. Обновите `VITE_BACKEND_API_URL`:

```env
VITE_BACKEND_API_URL=https://your-actual-backend-domain.railway.app
```

## ✅ Шаг 5: Тестирование

### 5.1 Проверка Backend

```bash
curl https://your-backend-domain.railway.app/health
```

Ожидаемый ответ:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "services": {
    "ensemble_api": "available",
    "openai_api": "available", 
    "redis_cache": "available"
  }
}
```

### 5.2 Проверка Frontend

Откройте `https://your-frontend-domain.railway.app`

Должна загрузиться страница TrendXL 2.0 с формой ввода TikTok профиля.

### 5.3 Проверка интеграции

1. Введите TikTok профиль (например: `@zachking`)
2. Нажмите "Analyze Profile"
3. Должен появиться анализ профиля и трендов

## 🛠️ Шаг 6: Настройка доменов (опционально)

### 6.1 Custom Domain для Frontend

1. В Frontend сервисе перейдите в **Settings → Networking**
2. Нажмите **"Custom Domain"**
3. Добавьте ваш домен (например: `trendxl.yourdomain.com`)
4. Настройте DNS записи согласно инструкциям Railway

### 6.2 Custom Domain для Backend  

1. В Backend сервисе перейдите в **Settings → Networking**
2. Добавьте API домен (например: `api.yourdomain.com`)
3. Обновите `VITE_BACKEND_API_URL` во Frontend

## 📊 Мониторинг и логи

### 6.1 Просмотр логов

```bash
# В Railway Dashboard
# Backend сервис → Deployments → View Logs
# Frontend сервис → Deployments → View Logs
```

### 6.2 Мониторинг ресурсов

Railway предоставляет метрики:
- CPU Usage
- Memory Usage  
- Network Traffic
- Request Count

### 6.3 Health Checks

Backend включает автоматические health checks:
- `/health` - общее состояние
- `/api/v1/cache/stats` - статистика кэша

## 🔧 Troubleshooting

### Проблема: Backend не запускается

**Решение:**
1. Проверьте логи в Railway Dashboard
2. Убедитесь что `ENSEMBLE_API_TOKEN` и `OPENAI_API_KEY` корректны
3. Проверьте что `PORT=$PORT` установлен

### Проблема: CORS ошибки

**Решение:**
1. Убедитесь что Frontend домен добавлен в `CORS_ORIGINS`
2. Проверьте формат: `["https://domain.railway.app"]`
3. Перезапустите Backend сервис

### Проблема: Frontend не подключается к Backend

**Решение:**
1. Проверьте `VITE_BACKEND_API_URL` в Frontend
2. Убедитесь что Backend домен доступен
3. Проверьте Network tab в браузере

### Проблема: Redis подключение

**Решение:**
1. Убедитесь что Redis сервис запущен
2. Используйте `REDIS_PRIVATE_URL` вместо `REDIS_URL`
3. Проверьте логи Backend на ошибки Redis

## 💰 Стоимость

### Railway Pricing (примерно):

- **Hobby Plan** (бесплатно): $5 кредитов/месяц
  - Backend: ~$3-4/месяц
  - Frontend: ~$1-2/месяц  
  - Redis: ~$1/месяц

- **Developer Plan** ($20/месяц): $20 кредитов
  - Достаточно для production использования

## 🚀 Production Tips

### 1. Оптимизация производительности

```env
# Backend
MAX_REQUESTS_PER_MINUTE=120
CACHE_PROFILE_TTL=3600
CACHE_POSTS_TTL=1800
CACHE_TRENDS_TTL=600
```

### 2. Мониторинг

Настройте уведомления в Railway для:
- Высокое использование CPU/Memory
- Ошибки деплоя
- Downtime

### 3. Backup

Railway автоматически создает backups, но рекомендуется:
- Регулярные коммиты в GitHub
- Экспорт данных Redis (если критично)

## 📞 Поддержка

- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **Railway Discord**: [railway.app/discord](https://railway.app/discord)
- **TrendXL Issues**: [GitHub Issues](https://github.com/your-username/trendxl-2.0/issues)

---

## ✅ Checklist деплоя

- [ ] Создан аккаунт Railway
- [ ] Получены API ключи (Ensemble + OpenAI)
- [ ] Код запушен в GitHub
- [ ] Backend сервис создан и настроен
- [ ] Redis добавлен и подключен
- [ ] Frontend сервис создан и настроен
- [ ] CORS настроен правильно
- [ ] Домены связаны между сервисами
- [ ] Health checks проходят
- [ ] Интеграция работает end-to-end
- [ ] (Опционально) Custom домены настроены

**🎉 Поздравляем! TrendXL 2.0 успешно развернут на Railway!**
