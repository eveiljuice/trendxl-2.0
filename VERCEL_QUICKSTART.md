# ⚡ Быстрый старт: Деплой на Vercel

## 🚀 5 шагов до деплоя

### 1. Установите Vercel CLI

```bash
npm install -g vercel
```

### 2. Войдите в Vercel

```bash
vercel login
```

### 3. Настройте переменные окружения

Создайте файл `.env` в корне проекта (или настройте через Vercel Dashboard):

```bash
# Обязательные переменные
ENSEMBLE_API_TOKEN=your-token-here
OPENAI_API_KEY=sk-your-key-here
PERPLEXITY_API_KEY=pplx-your-key-here
JWT_SECRET_KEY=your-secret-key-32-chars-min

# Опционально (для кэширования)
REDIS_URL=redis://your-redis-url
```

**Где получить API ключи:**

- Ensemble Data: https://dashboard.ensembledata.com/
- OpenAI: https://platform.openai.com/api-keys
- Perplexity: https://www.perplexity.ai/settings/api
- Redis: https://upstash.com/ (бесплатный tier)

**Сгенерировать JWT Secret:**

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Деплой на Vercel

```bash
cd "C:\Users\ok\Desktop\timo\trendxl 2.0"
vercel --prod
```

Следуйте инструкциям CLI:

1. Set up and deploy? → **Yes**
2. Which scope? → Выберите свой аккаунт
3. Link to existing project? → **No**
4. Project name? → **trendxl** (или свое название)
5. Directory? → **./** (текущая директория)
6. Override settings? → **No**

### 5. Настройте переменные окружения в Vercel

После первого деплоя:

```bash
vercel env add ENSEMBLE_API_TOKEN
vercel env add OPENAI_API_KEY
vercel env add PERPLEXITY_API_KEY
vercel env add JWT_SECRET_KEY
vercel env add REDIS_URL
```

Для каждой переменной:

1. Введите значение
2. Выберите окружения: **Production**, **Preview**, **Development**

Или через веб-интерфейс:

1. Откройте https://vercel.com/dashboard
2. Выберите проект **trendxl**
3. Settings → Environment Variables
4. Добавьте все переменные

### 6. Переделойте проект

После добавления переменных окружения:

```bash
vercel --prod
```

---

## ✅ Проверка работы

### Откройте ваш сайт:

```
https://trendxl.vercel.app  (или ваше имя проекта)
```

### Проверьте backend:

```
https://trendxl.vercel.app/health
```

Должен вернуть:

```json
{
  "status": "healthy",
  "services": { ... }
}
```

### Проверьте API:

```
https://trendxl.vercel.app/api/v1/status
```

---

## 🔧 Основные команды

```bash
# Production деплой
vercel --prod

# Preview деплой (для тестирования)
vercel

# Просмотр логов
vercel logs

# Список переменных окружения
vercel env ls

# Удалить deployment
vercel remove [deployment-url]

# Открыть проект в браузере
vercel open
```

---

## 📊 Автоматический деплой через Git

### Настройка GitHub/GitLab/Bitbucket:

1. Перейдите на https://vercel.com/dashboard
2. Нажмите **"Import Project"**
3. Подключите Git репозиторий
4. Vercel автоматически деплоит:
   - **main/master ветка** → Production
   - **другие ветки** → Preview deployments

### Преимущества:

- ✅ Автоматический деплой при push
- ✅ Preview deployments для каждого PR
- ✅ Rollback к любой версии
- ✅ Автоматическое тестирование

---

## ⚠️ Важные ограничения Vercel

### Free Tier (Hobby):

- ⏱️ **Function timeout**: 10 секунд
- 💾 **Memory**: 1024 MB
- 📦 **Deployment size**: 100 MB
- 🔄 **Executions**: 100 GB-Hrs

### Pro Tier ($20/месяц):

- ⏱️ **Function timeout**: 60 секунд (настроено в `vercel.json`)
- 💾 **Memory**: 3008 MB
- 📦 **Deployment size**: 500 MB
- 🔄 **Executions**: 1000 GB-Hrs

**Рекомендация**:

- Для полного функционала TrendXL рекомендуется **Pro план**
- Анализ TikTok профиля может занимать 30-60 секунд
- Free tier подходит для демо и тестирования

---

## 🐛 Troubleshooting

### Проблема: Backend не отвечает (502)

**Решение:**

1. Проверьте логи: `vercel logs`
2. Убедитесь, что все переменные окружения установлены
3. Проверьте, что `mangum` в `requirements.txt`

### Проблема: Timeout на анализе

**Решение:**

- Используйте Vercel Pro для 60-секундного таймаута
- Или переключитесь на Railway (см. `RAILWAY_DEPLOYMENT.md`)

### Проблема: CORS ошибки

**Решение:**
Добавьте переменную окружения:

```bash
vercel env add CORS_ORIGINS
# Значение: ["https://trendxl.vercel.app"]
```

### Проблема: Database не работает

**Решение:**
SQLite не работает на Vercel (read-only filesystem).
Используйте:

- Vercel Postgres: `vercel postgres create`
- Supabase: https://supabase.com
- PlanetScale: https://planetscale.com

---

## 📚 Дополнительная документация

- 📖 Полное руководство: `VERCEL_DEPLOYMENT_GUIDE.md`
- 🔧 Пример переменных: `.env.vercel.example`
- 🚂 Альтернатива (Railway): `RAILWAY_DEPLOYMENT.md`

---

## 🎯 Следующие шаги

1. ✅ Деплой выполнен
2. 🔐 Настроены переменные окружения
3. 🌐 Настроен custom domain (опционально)
4. 📊 Включена аналитика: https://vercel.com/analytics
5. 🔔 Настроены уведомления об ошибках

---

**Готово! Ваше приложение запущено на Vercel! 🎉**

Вопросы? Проверьте:

- Vercel Docs: https://vercel.com/docs
- Vercel Support: https://vercel.com/support
