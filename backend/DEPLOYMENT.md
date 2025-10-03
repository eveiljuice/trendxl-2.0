# TrendXL 2.0 Backend - Руководство по развертыванию

## 🚀 Быстрый старт

### 1. Подготовка окружения

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
```

### 2. Настройка API ключей

Отредактируйте `.env` файл:

```env
ENSEMBLE_API_TOKEN=your_token_here
OPENAI_API_KEY=your_key_here
```

### 3. Запуск Redis

```bash
# Docker (рекомендуется)
docker run -d --name trendxl-redis -p 6379:6379 redis:7-alpine

# Или локально
sudo systemctl start redis-server
```

### 4. Запуск сервера

```bash
# Linux/Mac
./start.sh

# Windows
python run_server.py

# Или напрямую
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 🐳 Docker развертывание

### Полное развертывание

```bash
# Сборка и запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f api

# Остановка
docker-compose down
```

### Только API

```bash
docker build -t trendxl-backend .
docker run -d -p 8000:8000 --env-file .env trendxl-backend
```

## 🌐 Production развертывание

### Nginx конфигурация

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Systemd сервис

```ini
[Unit]
Description=TrendXL 2.0 Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/trendxl-backend
Environment=PATH=/opt/trendxl-backend/venv/bin
ExecStart=/opt/trendxl-backend/venv/bin/python run_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

### SSL с Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 📊 Мониторинг

### Health checks

```bash
# Базовая проверка
curl http://localhost:8000/health

# Статистика кэша
curl http://localhost:8000/api/v1/cache/stats
```

### Prometheus мониторинг

Добавьте в `requirements.txt`:

```
prometheus-fastapi-instrumentator>=6.0.0
```

## 🛡 Безопасность

### Файрвол

```bash
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Переменные окружения в production

```bash
export ENSEMBLE_API_TOKEN="prod_token"
export OPENAI_API_KEY="prod_key"
export DEBUG="false"
export REDIS_URL="redis://prod-redis:6379"
```

## 🔧 Настройки производительности

### Uvicorn workers

```bash
uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000
```

### Redis persistence

```bash
redis-server --save 900 1 --save 300 10 --save 60 10000
```

## 📈 Масштабирование

### Load Balancer

```nginx
upstream trendxl_backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    location / {
        proxy_pass http://trendxl_backend;
    }
}
```

### Redis Cluster

```bash
# Master-slave setup
redis-server --port 6379 --daemonize yes
redis-server --port 6380 --slaveof 127.0.0.1 6379 --daemonize yes
```

## 🐛 Отладка

### Логи

```bash
# Docker logs
docker-compose logs -f api

# Системные логи
journalctl -u trendxl-backend -f

# Логи приложения
tail -f /var/log/trendxl/app.log
```

### Профилирование

```python
# Добавьте в код для профилирования
import cProfile
cProfile.run('your_function()')
```

## 🔄 Обновление

### Обновление кода

```bash
git pull
pip install -r requirements.txt
sudo systemctl restart trendxl-backend
```

### Миграция данных

```bash
# Backup Redis
redis-cli --rdb dump.rdb

# Restore
redis-cli --pipe < dump.rdb
```

## 🆘 Устранение неполадок

### Проблемы с Redis

```bash
# Проверка подключения
redis-cli ping

# Очистка кэша
redis-cli flushall

# Просмотр логов
redis-cli monitor
```

### Проблемы с API

```bash
# Проверка эндпоинтов
curl -v http://localhost:8000/health

# Тест Ensemble API
curl -X POST http://localhost:8000/api/v1/profile \
  -H "Content-Type: application/json" \
  -d '{"username": "test"}'
```

### Производительность

```bash
# Мониторинг ресурсов
htop
iostat -x 1
netstat -an | grep 8000

# Профилирование Redis
redis-cli --latency
redis-cli info memory
```
