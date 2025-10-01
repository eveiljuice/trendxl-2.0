# 🔧 Исправление Vercel Deployment

## Проблема

1. ❌ Vercel подключен к репозиторию `ShomaEasy/trendxl-2.0`
2. ✅ Ваш код находится в `eveiljuice/trendxl-2.0`
3. ❌ Python backend не деплоится на Vercel

## Решение

### Шаг 1: Переподключите проект к правильному репозиторию

1. Откройте: https://vercel.com/shomas-projects-2d51e250/trendxl-2-0/settings/git
2. Нажмите **"Disconnect"** от текущего репозитория
3. Нажмите **"Connect Git Repository"**
4. Выберите репозиторий: `eveiljuice/trendxl-2.0`
5. Сохраните изменения

### Шаг 2: Настройте переменные окружения

Откройте: https://vercel.com/shomas-projects-2d51e250/trendxl-2-0/settings/environment-variables

Добавьте следующие переменные для **Production, Preview, Development**:

```bash
ENSEMBLE_API_TOKEN=<ваш-токен-из-backend/.env>
OPENAI_API_KEY=<ваш-ключ-из-backend/.env>
PERPLEXITY_API_KEY=<ваш-ключ-из-backend/.env>
JWT_SECRET_KEY=<сгенерированный-секрет>
REDIS_URL=redis://localhost:6379
DEBUG=false
CORS_ORIGINS=["https://trendxl-2-0.vercel.app","http://localhost:3000","http://localhost:5173"]
```

⚠️ **Где взять значения:**
- Откройте файл `backend/.env` в вашем проекте
- Скопируйте оттуда значения `ENSEMBLE_API_TOKEN`, `OPENAI_API_KEY`, `PERPLEXITY_API_KEY`
- Для `JWT_SECRET_KEY` используйте уже сгенерированный ключ

⚠️ **Важно:** После добавления переменных окружения, проект нужно переделоить!

### Шаг 3: Переделойте проект

После настройки переменных окружения:

1. Откройте: https://vercel.com/shomas-projects-2d51e250/trendxl-2-0
2. Нажмите на последний deployment
3. Нажмите меню ⋮ (три точки)
4. Выберите **"Redeploy"**
5. Включите опцию **"Use existing Build Cache"** = OFF (чтобы пересобрать все заново)
6. Нажмите **"Redeploy"**

### Шаг 4: Проверьте работу

После переделоймента проверьте:

#### 1. Frontend

https://trendxl-2-0.vercel.app

Должна открыться главная страница

#### 2. Health Check

https://trendxl-2-0.vercel.app/health

Ожидаемый ответ:

```json
{
  "status": "healthy",
  "timestamp": "...",
  "services": {...}
}
```

#### 3. API Status

https://trendxl-2-0.vercel.app/api/v1/status

Должен вернуть информацию о сервисах

#### 4. Проверка в консоли браузера

Откройте DevTools (F12) на странице https://trendxl-2-0.vercel.app

В консоли должно быть:

```
🌐 Final API Base URL:
```

(пустая строка означает использование относительных путей - это правильно!)

---

## Если все еще не работает

### Проблема: Backend не отвечает

**Причина:** Python serverless function не была построена

**Решение:**

1. Проверьте что файл `api/index.py` существует в репозитории
2. Проверьте что `api/requirements.txt` содержит `mangum>=0.17.0`
3. Проверьте логи build в Vercel Dashboard
4. Должна быть строка о сборке Python функции

### Проблема: CORS ошибки

**Причина:** Backend не разрешает запросы с фронтенда

**Решение:**

Проверьте переменную окружения `CORS_ORIGINS`:

```bash
CORS_ORIGINS=["https://trendxl-2-0.vercel.app"]
```

### Проблема: 502 Bad Gateway

**Причина:** Python функция не запускается

**Решение:**

1. Проверьте логи функции:
   - Dashboard → Deployments → Functions → Logs
2. Проверьте что все переменные окружения установлены
3. Убедитесь что `mangum` установлен

---

## Альтернативное решение: Создать новый проект

Если переподключение не работает, создайте новый проект:

1. Откройте: https://vercel.com/new
2. Импортируйте `eveiljuice/trendxl-2.0`
3. Настройте переменные окружения (см. Шаг 2)
4. Деплой

---

## Быстрая проверка

```bash
# Проверка frontend
curl https://trendxl-2-0.vercel.app

# Проверка health
curl https://trendxl-2-0.vercel.app/health

# Проверка API
curl https://trendxl-2-0.vercel.app/api/v1/status
```

---

## Контакты

- Vercel Dashboard: https://vercel.com/dashboard
- Vercel Support: https://vercel.com/support
- Документация: `VERCEL_QUICKSTART.md`
