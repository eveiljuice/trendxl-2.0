# 🐳 Docker Quick Start для TrendXL 2.0

## 🎯 Быстрый старт

### Локальная разработка с Docker

#### 1. Backend (FastAPI)

```bash
# Перейдите в директорию backend
cd backend

# Создайте .env файл с необходимыми переменными
cat > .env << EOL
ENSEMBLE_API_TOKEN=your_token_here
OPENAI_API_KEY=your_key_here
PERPLEXITY_API_KEY=your_key_here
PORT=8000
HOST=0.0.0.0
DEBUG=true
ENVIRONMENT=development
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200
EOL

# Соберите Docker образ
docker build -t trendxl-backend .

# Запустите контейнер
docker run -p 8000:8000 --env-file .env trendxl-backend

# Проверьте работу
curl http://localhost:8000/health
# Откройте API документацию: http://localhost:8000/docs
```

#### 2. Frontend (React + Vite)

```bash
# Вернитесь в корень проекта
cd ..

# Создайте .env файл (опционально)
echo "VITE_API_URL=http://localhost:8000" > .env

# Соберите Docker образ
docker build -t trendxl-frontend .

# Запустите контейнер
docker run -p 80:80 trendxl-frontend

# Проверьте работу
curl http://localhost/health
# Откройте в браузере: http://localhost
```

## 🔧 Полезные команды

### Просмотр логов

```bash
# Backend логи
docker logs -f [container_id]

# Frontend логи
docker logs -f [container_id]
```

### Остановка контейнеров

```bash
# Показать запущенные контейнеры
docker ps

# Остановить контейнер
docker stop [container_id]

# Остановить все контейнеры
docker stop $(docker ps -q)
```

### Очистка

```bash
# Удалить остановленные контейнеры
docker container prune

# Удалить неиспользуемые образы
docker image prune

# Полная очистка
docker system prune -a
```

## 🚀 Railway Deployment

### Структура проекта на Railway:

```
Railway Project: TrendXL 2.0
├── Service 1: Backend
│   ├── Root Directory: backend
│   ├── Dockerfile: backend/Dockerfile
│   └── Environment Variables: [См. RAILWAY_DEPLOYMENT.md]
│
└── Service 2: Frontend
    ├── Root Directory: /
    ├── Dockerfile: Dockerfile
    └── Environment Variables: VITE_API_URL
```

### Деплой через Railway Dashboard:

1. **Создайте проект**: [New Project] → [Deploy from GitHub repo]
2. **Добавьте Backend сервис**:
   - Settings → Root Directory: `backend`
   - Settings → Variables: Добавьте все переменные окружения
   - Settings → Networking → Generate Domain
3. **Добавьте Frontend сервис**:
   - Settings → Root Directory: `/`
   - Settings → Variables: `VITE_API_URL=<backend-url>`
   - Settings → Networking → Generate Domain

### Деплой через Railway CLI:

```bash
# Установите Railway CLI
npm install -g @railway/cli

# Войдите в аккаунт
railway login

# Создайте проект
railway init

# Деплой backend
cd backend
railway up

# Деплой frontend (из корня)
cd ..
railway up
```

## 📋 Checklist перед деплоем

### Backend

- [ ] Все зависимости в `requirements.txt`
- [ ] API ключи в переменных окружения
- [ ] `DEBUG=false` для production
- [ ] `SECRET_KEY` сгенерирован
- [ ] CORS настроен для frontend домена
- [ ] Health endpoint работает

### Frontend

- [ ] `VITE_API_URL` указывает на backend
- [ ] Build завершается успешно
- [ ] Nginx конфигурация правильная
- [ ] SPA роутинг работает
- [ ] Статические файлы доступны

## 🧪 Тестирование

### Backend endpoints

```bash
# Health check
curl https://your-backend.railway.app/health

# API documentation
open https://your-backend.railway.app/docs

# Test authentication
curl -X POST https://your-backend.railway.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"Test123!"}'
```

### Frontend

```bash
# Health check
curl https://your-frontend.railway.app/health

# Open in browser
open https://your-frontend.railway.app
```

## 🐛 Troubleshooting

### Backend не отвечает

1. Проверьте логи: Railway Dashboard → Backend Service → Logs
2. Проверьте переменные окружения
3. Проверьте health endpoint
4. Убедитесь что используется `$PORT` переменная

### Frontend показывает пустую страницу

1. Проверьте Nginx логи
2. Проверьте что build прошел успешно
3. Проверьте статические файлы в `/usr/share/nginx/html`
4. Проверьте консоль браузера на ошибки

### CORS ошибки

1. Добавьте frontend URL в `ALLOWED_ORIGINS` backend
2. Формат: `https://your-frontend.railway.app` (без слеша в конце)
3. Перезапустите backend сервис

## 📚 Дополнительные ресурсы

- [Полная инструкция по деплою](./RAILWAY_DEPLOYMENT.md)
- [Railway Documentation](https://docs.railway.app)
- [Docker Documentation](https://docs.docker.com)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Vite Documentation](https://vitejs.dev)

---

**Готовы к деплою?** Следуйте инструкциям в [RAILWAY_DEPLOYMENT.md](./RAILWAY_DEPLOYMENT.md)
