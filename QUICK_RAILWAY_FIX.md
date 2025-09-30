# 🚀 Быстрое исправление Railway Backend (2 минуты)

## 🔥 Проблема
Backend падает: `ValidationError - API keys required`

## ✅ Решение (3 шага)

### 1️⃣ Добавить API ключи в Railway

**Railway Dashboard → Backend Service → Variables → Add**

```env
ENSEMBLE_API_TOKEN=your_ensemble_token_here
OPENAI_API_KEY=sk-your_openai_key_here
PERPLEXITY_API_KEY=pplx-your_perplexity_key_here
PORT=8000
CORS_ORIGINS=https://trendxl-20-frontend-production.up.railway.app
```

### 2️⃣ Изменить Dockerfile в Railway

**Railway Dashboard → Backend Service → Settings → Deploy**

Найдите:
- **Docker Dockerfile Path**: измените на `Dockerfile.backend`

ИЛИ убедитесь что используется `railway.backend.toml`

### 3️⃣ Redeploy

**Railway Dashboard → Backend Service → Deployments**
- Нажмите на последний деплой
- Кнопка **Redeploy**

## ✅ Проверка

```bash
curl https://trendxl-20-backend-production.up.railway.app/health
```

Должен вернуть:
```json
{"status": "healthy", "services": {"backend": true}}
```

## 📚 Подробная инструкция

См. файл `RAILWAY_BACKEND_FIX.md`

---

**Время исправления**: ~2 минуты  
**Дата**: 30 сентября 2025

