# TrendXL 2.0 - Fullstack Deployment Guide

## 🚀 Единый Dockerfile для Railway

Создан единый Dockerfile, который объединяет React/Vite фронтенд и Python FastAPI бэкенд в одном контейнере для упрощения развертывания на Railway.

## 📁 Созданные файлы

### Основные файлы развертывания:

- **`Dockerfile`** - Единый мульти-стейдж Docker-файл
- **`railway.toml`** - Конфигурация для Railway (один сервис)
- **`nginx.fullstack.conf`** - Nginx конфигурация с реверс-прокси
- **`supervisord.conf`** - Управление процессами
- **`start-services.sh`** - Стартовый скрипт

## 🏗 Архитектура

```
┌─────────────────┐    ┌─────────────────┐
│   Railway       │    │   Docker        │
│   Platform      │────▶│   Container     │
└─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │     Nginx       │
                       │  (Port 80/PORT) │
                       └─────────────────┘
                                │
                    ┌───────────┼───────────┐
                    ▼                       ▼
           ┌─────────────────┐    ┌─────────────────┐
           │    Frontend     │    │     Backend     │
           │   (Static)      │    │ FastAPI (8000)  │
           │   React/Vite    │    │     Python      │
           └─────────────────┘    └─────────────────┘
```

## 🔄 Как это работает

1. **Nginx** служит точкой входа на порт 80 (или $PORT от Railway)
2. **Статические файлы** (фронтенд) обслуживаются Nginx напрямую
3. **API запросы** (`/api/*`) проксируются на Python backend (порт 8000)
4. **Supervisor** управляет обоими процессами (Nginx + Python)

## 🛣 Маршрутизация

- `GET /` → Фронтенд (React SPA)
- `GET /health` → Health check endpoint
- `GET /api/*` → Python FastAPI backend
- `GET /ws/*` → WebSocket support (если нужно)

## 🚀 Развертывание на Railway

### 1. Подготовка репозитория

```bash
# Добавить все новые файлы
git add .

# Коммит изменений
git commit -m "🚀 Unified fullstack Dockerfile for Railway deployment

- Single Dockerfile for both frontend and backend
- Nginx reverse proxy configuration
- Supervisor process management
- Health checks and proper routing
- Production-ready setup"

# Отправить в репозиторий
git push origin main
```

### 2. Настройка Railway

1. Подключите репозиторий к Railway
2. Railway автоматически обнаружит `railway.toml`
3. Развертывание начнется автоматически

### 3. Переменные окружения (автоматически настроены)

- `PORT` - Устанавливается Railway
- `NODE_ENV=production`
- `PYTHONPATH=/app/backend`
- `HOST=0.0.0.0`

## 🔧 Локальное тестирование

```bash
# Сборка образа
docker build -t trendxl-fullstack .

# Запуск контейнера
docker run -p 80:80 -e PORT=80 trendxl-fullstack

# Проверка работы
curl http://localhost/health        # Health check
curl http://localhost/             # Фронтенд
curl http://localhost/api/         # API backend
```

## 🧪 Отладка

Просмотр логов в контейнере:

```bash
# Войти в контейнер
docker exec -it <container_id> sh

# Посмотреть логи supervisor
tail -f /var/log/supervisor/supervisord.log

# Логи backend
tail -f /var/log/supervisor/backend.log

# Логи nginx
tail -f /var/log/supervisor/nginx.log
```

## ✅ Преимущества единого контейнера

1. **Простота развертывания** - один сервис в Railway
2. **Быстрая связь** - нет сетевых задержек между фронтендом и бэкендом
3. **Общие ресурсы** - эффективное использование памяти
4. **Единая точка входа** - упрощенная конфигурация DNS
5. **Автоматическая маршрутизация** - Nginx обрабатывает все запросы

## 🔒 Безопасность

- ✅ Non-root пользователь для Python приложения
- ✅ Security headers в Nginx
- ✅ Rate limiting для API
- ✅ Proper CORS handling
- ✅ Health checks

## 📈 Производительность

- ✅ Gzip compression
- ✅ Static file caching
- ✅ Connection pooling
- ✅ Optimized Docker layers
- ✅ Multi-process architecture

Готов к production! 🎉
