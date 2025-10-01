# 🚀 TrendXL 2.0 - Vercel Deployment

Быстрый гайд по развертыванию TrendXL 2.0 на Vercel.

## 📚 Документация

- **⚡ Быстрый старт**: [`VERCEL_QUICKSTART.md`](VERCEL_QUICKSTART.md) - 5 шагов до деплоя
- **📖 Полное руководство**: [`VERCEL_DEPLOYMENT_GUIDE.md`](VERCEL_DEPLOYMENT_GUIDE.md) - детальная документация
- **✅ Checklist**: [`VERCEL_SETUP_CHECKLIST.md`](VERCEL_SETUP_CHECKLIST.md) - проверочный список
- **🔧 Пример ENV**: [`.env.vercel.example`](.env.vercel.example) - переменные окружения

## ⚡ Быстрый старт

### 1. Установка и вход

```bash
npm install -g vercel
vercel login
```

### 2. Настройка переменных окружения

Получите API ключи:

- **Ensemble Data**: https://dashboard.ensembledata.com/
- **OpenAI**: https://platform.openai.com/api-keys
- **Perplexity**: https://www.perplexity.ai/settings/api
- **Redis** (опционально): https://upstash.com/

Сгенерируйте JWT Secret:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Деплой

```bash
cd "C:\Users\ok\Desktop\timo\trendxl 2.0"
vercel --prod
```

### 4. Добавьте переменные окружения

```bash
vercel env add ENSEMBLE_API_TOKEN
vercel env add OPENAI_API_KEY
vercel env add PERPLEXITY_API_KEY
vercel env add JWT_SECRET_KEY
```

### 5. Переделойте

```bash
vercel --prod
```

## ✅ Проверка

Откройте: `https://your-project-name.vercel.app`

Проверьте health: `https://your-project-name.vercel.app/health`

## 📁 Структура проекта

```
trendxl 2.0/
├── api/
│   ├── index.py              # Serverless function entry
│   └── requirements.txt      # Python deps for API
├── backend/
│   ├── main.py               # FastAPI app
│   └── vercel_adapter.py     # Vercel adapter
├── src/                      # React frontend
├── vercel.json               # Vercel config
└── .vercelignore            # Ignore files
```

## ⚙️ Конфигурация

### vercel.json

Настроены:

- ✅ Static site build (Vite)
- ✅ Python serverless functions
- ✅ API routing `/api/*` → backend
- ✅ Health check `/health` → backend
- ✅ Frontend routing `/*` → React app
- ✅ Function timeout: 60s (Pro plan)
- ✅ Memory: 1024 MB

### Переменные окружения

Обязательные:

- `ENSEMBLE_API_TOKEN`
- `OPENAI_API_KEY`
- `PERPLEXITY_API_KEY`
- `JWT_SECRET_KEY`

Опциональные:

- `REDIS_URL` (для кэширования)
- `DATABASE_URL` (PostgreSQL/MySQL)

## ⚠️ Важно

### Ограничения Vercel

**Free Tier (Hobby):**

- ⏱️ Function timeout: 10 секунд
- ⚠️ Может быть недостаточно для полного анализа профиля

**Pro Tier ($20/мес):**

- ⏱️ Function timeout: 60 секунд ✅
- 💾 Memory: 3008 MB
- Рекомендуется для production

### База данных

⚠️ **SQLite не работает на Vercel** (read-only filesystem)

Используйте:

- Vercel Postgres: `vercel postgres create`
- Supabase: https://supabase.com
- PlanetScale: https://planetscale.com

## 🔧 Основные команды

```bash
# Production deploy
vercel --prod

# Preview deploy
vercel

# Logs
vercel logs

# Environment variables
vercel env ls
vercel env add VARIABLE_NAME
vercel env rm VARIABLE_NAME

# Project info
vercel inspect

# Open dashboard
vercel open
```

## 🐛 Troubleshooting

### Backend не отвечает (502)

```bash
# Проверьте логи
vercel logs

# Проверьте переменные
vercel env ls
```

### Timeout на анализе

- Используйте Vercel Pro (60s timeout)
- Или переключитесь на Railway

### CORS ошибки

```bash
vercel env add CORS_ORIGINS
# Значение: ["https://your-project.vercel.app"]
vercel --prod
```

## 📊 Мониторинг

- **Logs**: `vercel logs` или Dashboard → Functions → Logs
- **Analytics**: https://vercel.com/analytics
- **Notifications**: Settings → Notifications

## 🌐 Custom Domain

1. Settings → Domains
2. Добавьте ваш домен
3. Настройте DNS записи
4. Обновите `CORS_ORIGINS` с новым доменом

## 🔄 Git Integration

Рекомендуется для CI/CD:

1. Dashboard → Import Project
2. Подключите Git репозиторий
3. Автодеплой при push в `main`
4. Preview deployments для PR

## 📚 Дополнительно

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Python Runtime](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [FastAPI on Vercel](https://vercel.com/guides/deploying-fastapi-with-vercel)
- [Mangum Documentation](https://mangum.io/)

## 🚂 Альтернативы

Если Vercel не подходит:

- **Railway** (рекомендуется): см. `RAILWAY_DEPLOYMENT.md`
- **Render**: бесплатный tier
- **Fly.io**: Docker support

---

**Вопросы?** Проверьте полную документацию в `VERCEL_DEPLOYMENT_GUIDE.md`

**Успешного деплоя! 🎉**
