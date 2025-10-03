# 🚀 Развертывание TrendXL 2.0 на Railway

## 📋 Обзор

Этот проект состоит из двух сервисов:

- **Frontend**: React + Vite + Nginx (порт 80)
- **Backend**: Python FastAPI + Uvicorn (порт динамический)

## 🏗️ Архитектура

```
┌─────────────────┐         ┌─────────────────┐
│   Frontend      │────────▶│    Backend      │
│  React + Vite   │  HTTP   │  FastAPI + DB   │
│  Nginx:80       │         │  Uvicorn:$PORT  │
└─────────────────┘         └─────────────────┘
```

## 📦 Шаг 1: Подготовка проекта

### Проверьте наличие файлов:

- ✅ `Dockerfile` (в корне для фронтенда)
- ✅ `backend/Dockerfile` (для бекенда)
- ✅ `.dockerignore` (в корне)
- ✅ `backend/.dockerignore`

## 🌐 Шаг 2: Создание проекта на Railway

### 1. Создайте новый проект

```bash
# Перейдите на https://railway.app
# Создайте новый проект через GitHub репозиторий
```

### 2. Добавьте Backend сервис

#### В настройках сервиса:

- **Name**: `trendxl-backend`
- **Root Directory**: `backend`
- **Dockerfile Path**: `backend/Dockerfile`

#### Переменные окружения (Settings → Variables):

```bash
# Обязательные
ENSEMBLE_API_TOKEN=your_ensemble_token_here
OPENAI_API_KEY=your_openai_key_here

# Опциональные (Railway предоставит автоматически)
PORT=8000
HOST=0.0.0.0
DEBUG=false
ENVIRONMENT=production

# Redis (если нужен)
REDIS_URL=redis://redis:6379

# Database
DATABASE_URL=sqlite:///data/trendxl.db
USER_DATABASE_URL=sqlite:///data/trendxl_users.db

# JWT
SECRET_KEY=your_long_random_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200
```

#### Генерация доменного имени:

1. В разделе **Settings → Networking**
2. Нажмите **Generate Domain**
3. Скопируйте URL (например: `trendxl-backend-production.up.railway.app`)

### 3. Добавьте Frontend сервис

#### В настройках сервиса:

- **Name**: `trendxl-frontend`
- **Root Directory**: `/` (корень проекта)
- **Dockerfile Path**: `Dockerfile`

#### Переменные окружения:

```bash
# URL бекенда (полученный на предыдущем шаге)
VITE_API_URL=https://trendxl-backend-production.up.railway.app

# Или если используете одинаковый домен с разными путями
VITE_API_URL=/api
```

#### Генерация доменного имени:

1. В разделе **Settings → Networking**
2. Нажмите **Generate Domain**
3. Ваш frontend будет доступен по этому URL

### 4. (Опционально) Добавьте Redis

Если ваше приложение использует Redis для кэширования:

1. В Railway нажмите **+ New** → **Database** → **Add Redis**
2. Railway автоматически создаст `REDIS_URL`
3. Обновите переменную `REDIS_URL` в backend сервисе через Reference:
   ```
   ${{Redis.REDIS_URL}}
   ```

## 🔧 Шаг 3: Настройка окружения

### Backend Environment Variables

Полный список переменных для backend:

```bash
# API Keys (ОБЯЗАТЕЛЬНО)
ENSEMBLE_API_TOKEN=your_token
OPENAI_API_KEY=sk-xxx
PERPLEXITY_API_KEY=pplx-xxx  # опционально

# Server Configuration
PORT=8000
HOST=0.0.0.0
DEBUG=false
ENVIRONMENT=production
LOG_LEVEL=info

# CORS
ALLOWED_ORIGINS=https://your-frontend-domain.railway.app,https://your-custom-domain.com

# Database
DATABASE_URL=sqlite:///data/trendxl.db
USER_DATABASE_URL=sqlite:///data/trendxl_users.db

# Authentication
SECRET_KEY=your-super-secret-jwt-key-min-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# Redis (опционально)
REDIS_URL=redis://redis:6379
CACHE_TTL=3600

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60
```

### Frontend Environment Variables

```bash
# Backend API URL
VITE_API_URL=https://your-backend-domain.railway.app

# Или относительный путь если используете nginx proxy
VITE_API_URL=/api
```

## 🚦 Шаг 4: Деплой

### Автоматический деплой

Railway автоматически задеплоит при push в GitHub:

```bash
git add .
git commit -m "Deploy to Railway"
git push origin main
```

### Мониторинг деплоя

1. Откройте Railway Dashboard
2. Перейдите в нужный сервис
3. Вкладка **Deployments** покажет статус
4. Вкладка **Logs** покажет логи сборки и запуска

### Проверка здоровья сервисов

**Backend Health Check:**

```bash
curl https://your-backend-domain.railway.app/health
```

**Frontend Health Check:**

```bash
curl https://your-frontend-domain.railway.app/health
```

## 🔍 Отладка

### Просмотр логов

```bash
# В Railway Dashboard
Services → [Ваш сервис] → Logs
```

### Распространенные проблемы

#### Backend не запускается

- ✅ Проверьте, что все API ключи установлены
- ✅ Проверьте логи на ошибки импорта
- ✅ Убедитесь что `requirements.txt` содержит все зависимости

#### Frontend показывает ошибку CORS

- ✅ Добавьте frontend URL в `ALLOWED_ORIGINS` backend
- ✅ Проверьте что `VITE_API_URL` указывает на правильный backend URL
- ✅ Убедитесь что backend отвечает на запросы

#### 502 Bad Gateway

- ✅ Убедитесь что сервис полностью запустился (проверьте логи)
- ✅ Проверьте health endpoint
- ✅ Проверьте что порт указан правильно (используйте `$PORT` для Railway)

## 📊 Масштабирование

### Вертикальное масштабирование

Railway автоматически предоставляет ресурсы на основе плана:

- **Hobby**: 512 MB RAM, 1 vCPU
- **Pro**: До 8GB RAM, 8 vCPU

### Горизонтальное масштабирование

Для большего трафика рассмотрите:

- Использование внешней PostgreSQL базы данных вместо SQLite
- Настройку Redis для кэширования
- Увеличение количества uvicorn workers в backend

## 🔐 Безопасность

### Checklist

- [ ] Все API ключи установлены через переменные окружения
- [ ] `DEBUG=false` в production
- [ ] `SECRET_KEY` сгенерирован (минимум 32 символа)
- [ ] CORS настроен правильно (только нужные домены)
- [ ] `.env` файлы в `.dockerignore`
- [ ] Sensitive данные не в git репозитории

### Генерация SECRET_KEY

```python
import secrets
print(secrets.token_urlsafe(32))
```

## 📱 Custom Domain (опционально)

1. В Railway Dashboard → Service → Settings → Networking
2. Нажмите **Custom Domain**
3. Добавьте ваш домен
4. Настройте DNS записи как показано Railway
5. Обновите `ALLOWED_ORIGINS` в backend

## 💡 Полезные команды

### Локальное тестирование Docker

**Backend:**

```bash
cd backend
docker build -t trendxl-backend .
docker run -p 8000:8000 --env-file .env trendxl-backend
```

**Frontend:**

```bash
docker build -t trendxl-frontend .
docker run -p 80:80 trendxl-frontend
```

### Проверка переменных окружения

```bash
# В Railway CLI
railway variables

# Установка переменной
railway variables set KEY=VALUE
```

## 📞 Поддержка

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- GitHub Issues: [ваш репозиторий]/issues

## 🎉 Готово!

После успешного деплоя ваше приложение будет доступно по адресам:

- **Frontend**: `https://your-frontend-domain.railway.app`
- **Backend**: `https://your-backend-domain.railway.app`
- **API Docs**: `https://your-backend-domain.railway.app/docs`

---

**Версия**: 2.0  
**Дата обновления**: October 2024  
**Автор**: TrendXL Team
