# TrendXL 2.0 Backend

Полнофункциональный Python бэкенд для анализа TikTok трендов, использующий Ensemble Data API и OpenAI GPT-4.

## 🚀 Возможности

- **Анализ профилей TikTok**: Получение информации о пользователях и их постах
- **ИИ-анализ контента**: Извлечение релевантных хештегов с помощью GPT-4
- **Поиск трендов**: Поиск популярных видео по хештегам
- **Кэширование**: Оптимизированная производительность с Redis
- **Rate Limiting**: Защита от злоупотреблений API
- **Полная документация API**: Swagger/OpenAPI интеграция

## 🛠 Технологический стек

- **FastAPI**: Современный веб-фреймворк для API
- **Ensemble Data SDK**: TikTok API интеграция
- **OpenAI API**: GPT-4 для анализа контента
- **Redis**: Кэширование и производительность
- **Pydantic**: Валидация данных и сериализация
- **Uvicorn**: ASGI сервер

## 📋 Требования

- Python 3.11+
- Redis Server
- Ensemble Data API Token
- OpenAI API Key

## 🔧 Установка

### 1. Клонирование и установка зависимостей

```bash
cd backend
pip install -r requirements.txt
```

### 2. Настройка окружения

```bash
cp .env.example .env
```

Отредактируйте `.env` файл:

```env
# API Keys
ENSEMBLE_API_TOKEN=your_ensemble_data_token_here
OPENAI_API_KEY=your_openai_api_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Redis Configuration
REDIS_URL=redis://localhost:6379
```

### 3. Запуск Redis (если не установлен)

```bash
# Using Docker
docker run -d -p 6379:6379 redis:7-alpine

# Or install locally on Ubuntu/Debian
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
```

### 4. Запуск сервера

```bash
python run_server.py
```

Сервер запустится на `http://localhost:8000`

## 🐳 Docker развертывание

### Полное развертывание с Docker Compose

```bash
# Запуск всех сервисов
docker-compose up -d

# Запуск с Redis GUI (опционально)
docker-compose --profile tools up -d

# Остановка
docker-compose down
```

### Только API сервис

```bash
# Сборка образа
docker build -t trendxl-backend .

# Запуск (требует внешний Redis)
docker run -d -p 8000:8000 --env-file .env trendxl-backend
```

## 📚 API Эндпоинты

### Основные эндпоинты

- `POST /api/v1/analyze` - Полный анализ трендов профиля
- `POST /api/v1/profile` - Получение информации о профиле
- `POST /api/v1/posts` - Получение постов пользователя
- `POST /api/v1/hashtag/search` - Поиск по хештегам
- `POST /api/v1/users/search` - Поиск пользователей

### Служебные эндпоинты

- `GET /health` - Проверка здоровья сервиса
- `GET /api/v1/cache/stats` - Статистика кэша
- `POST /api/v1/cache/clear` - Очистка кэша

### Документация API

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI Schema: `http://localhost:8000/openapi.json`

## 💡 Примеры использования

### Анализ трендов профиля

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{"profile_url": "https://www.tiktok.com/@username"}'
```

### Получение профиля

```bash
curl -X POST "http://localhost:8000/api/v1/profile" \
  -H "Content-Type: application/json" \
  -d '{"username": "username"}'
```

### Поиск по хештегу

```bash
curl -X POST "http://localhost:8000/api/v1/hashtag/search" \
  -H "Content-Type: application/json" \
  -d '{
    "hashtag": "trending",
    "count": 10,
    "period": 7,
    "sorting": 1
  }'
```

## 🔍 Алгоритм анализа трендов

1. **Получение профиля**: Извлечение информации о пользователе TikTok
2. **Загрузка постов**: Получение последних 20 постов пользователя
3. **ИИ-анализ**: GPT-4 анализирует посты и извлекает 5 релевантных хештегов
4. **Поиск трендов**: Для каждого хештега ищутся популярные видео за последние 7 дней
5. **Фильтрация**: Отбираются только качественные видео (> 1000 просмотров)
6. **Ранжирование**: Результаты сортируются по популярности

## 🚦 Производительность и лимиты

### Кэширование

- **Профили**: 30 минут
- **Посты**: 15 минут
- **Тренды**: 5 минут

### Rate Limiting

- 60 запросов в минуту на IP адрес
- Можно настроить в переменных окружения

### Retry Logic

- Автоматические повторы при временных ошибках API
- Экспоненциальная задержка между попытками
- Graceful degradation при недоступности сервисов

## 🛡 Безопасность

- Валидация всех входящих данных
- Rate limiting для предотвращения злоупотреблений
- Безопасное хранение API ключей
- CORS настройка для фронтенда

## 📊 Мониторинг

### Health Check

```bash
curl http://localhost:8000/health
```

### Статистика кэша

```bash
curl http://localhost:8000/api/v1/cache/stats
```

### Логирование

- Структурированные логи в JSON формате
- Разные уровни логирования для development/production
- Отслеживание API вызовов и производительности

## 🧪 Тестирование

```bash
# Запуск тестов
pytest

# С покрытием кода
pytest --cov=.

# Тестирование конкретного модуля
pytest tests/test_ensemble_service.py
```

## 🔧 Конфигурация

Все настройки в `config.py` могут быть переопределены через переменные окружения:

- `ENSEMBLE_API_TOKEN` - токен Ensemble Data API
- `OPENAI_API_KEY` - ключ OpenAI API
- `REDIS_URL` - URL для подключения к Redis
- `MAX_REQUESTS_PER_MINUTE` - лимит запросов
- `CACHE_PROFILE_TTL` - время жизни кэша профилей (сек)

## 🐛 Отладка

### Логи

```bash
# Просмотр логов в Docker
docker-compose logs -f api

# Увеличение уровня логирования
export DEBUG=True
```

### Проблемы с Redis

```bash
# Проверка подключения к Redis
redis-cli ping

# Просмотр ключей кэша
redis-cli keys "trendxl:v2:*"
```

## 📈 Масштабирование

- Горизонтальное масштабирование с несколькими экземплярами
- Load balancer для распределения нагрузки
- Redis Cluster для высокой доступности кэша
- Monitoring и alerting с Prometheus/Grafana

## 🤝 Разработка

### Структура проекта

```
backend/
├── main.py              # FastAPI приложение
├── config.py            # Конфигурация
├── models.py            # Pydantic модели
├── utils.py             # Утилиты
├── services/            # Бизнес-логика
│   ├── ensemble_service.py
│   ├── openai_service.py
│   ├── cache_service.py
│   └── trend_analysis_service.py
├── tests/               # Тесты
└── requirements.txt     # Зависимости
```

### Добавление новых эндпоинтов

1. Определить модели в `models.py`
2. Добавить бизнес-логику в соответствующий сервис
3. Создать эндпоинт в `main.py`
4. Написать тесты

## 📄 Лицензия

MIT License - см. файл LICENSE для деталей.

## 🆘 Поддержка

При возникновении проблем:

1. Проверьте логи сервиса
2. Убедитесь в корректности API ключей
3. Проверьте доступность Redis
4. Создайте issue в репозитории
