# TrendXL 2.0 - Railway Deployment Guide

## 🚀 Созданные файлы для автоматического развертывания

### Docker-файлы

- **`Dockerfile`** - Фронтенд (React/Vite + Nginx)
- **`Dockerfile.backend`** - Бэкенд (Python FastAPI)

### Railway конфигурация

- **`railway.json`** - Конфигурация фронтенда
- **`backend/railway.json`** - Конфигурация бэкенда
- **`railway.toml`** - Мульти-сервисная конфигурация проекта

### Оптимизация сборки

- **`.dockerignore`** - Исключения для фронтенда
- **`backend/.dockerignore`** - Исключения для бэкенда

## 📋 Инструкции по развертыванию

### Вариант 1: Автоматическое обнаружение через railway.toml

1. Подключите репозиторий к Railway
2. Railway автоматически обнаружит оба сервиса через `railway.toml`
3. Будут созданы два сервиса: `trendxl-frontend` и `trendxl-backend`

### Вариант 2: Отдельные сервисы через railway.json

1. **Для фронтенда**: Создайте сервис, указав корневую папку проекта
2. **Для бэкенда**: Создайте сервис, указав папку `backend/`
3. Railway использует соответствующие `railway.json` файлы

### Переменные окружения

#### Фронтенд

- `PORT` - автоматически задается Railway
- `NODE_ENV=production`

#### Бэкенд

- `PORT` - автоматически задается Railway
- `PYTHONPATH=/app`
- `PYTHONUNBUFFERED=1`
- `HOST=0.0.0.0`
- `DEBUG=false`
- `ENVIRONMENT=production`
- `LOG_LEVEL=INFO`

### Health Check Endpoints

- **Фронтенд**: `GET /health` (возвращает "ok")
- **Бэкенд**: `GET /health` (должен быть реализован в FastAPI)

## 🛠 Особенности конфигурации

1. **Мульти-стейдж сборка** - оптимизирует размер Docker-образов
2. **Nginx для фронтенда** - эффективная раздача статических файлов
3. **Health checks** - автоматическая проверка работоспособности
4. **Security** - использование non-root пользователей
5. **Port binding** - динамическое связывание портов через Railway

## 🔧 Команды для тестирования локально

```bash
# Сборка бэкенда
docker build -f Dockerfile.backend -t trendxl-backend .

# Сборка фронтенда
docker build -f Dockerfile -t trendxl-frontend .

# Запуск бэкенда
docker run -p 8000:8000 trendxl-backend

# Запуск фронтенда
docker run -p 80:80 trendxl-frontend
```

## 📝 Примечания

- Railway автоматически назначает порты через переменную `$RAILWAY_PORT`
- Все сервисы настроены на автоматический перезапуск при ошибках
- Конфигурация оптимизирована для production-окружения
