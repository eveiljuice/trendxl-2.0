# 🚂 Railway Setup - Краткая инструкция

## ⚠️ ВАЖНО: Роуты настраивать НЕ НУЖНО!

**Railway автоматически обрабатывает всю маршрутизацию между сервисами.**

---

## 🎯 Что нужно сделать (3 простых шага)

### Шаг 1: Создать Backend сервис

1. Railway Dashboard → **New Project** → Deploy from GitHub repo
2. Выбрать `trendxl-2.0`
3. **Settings → Build:**
   - Dockerfile Path: `Dockerfile.backend`
4. **Variables:**
   ```bash
   ENSEMBLE_API_TOKEN=your_token
   OPENAI_API_KEY=sk-proj-your_key
   PERPLEXITY_API_KEY=pplx-your_key
   HOST=0.0.0.0
   PORT=${{RAILWAY_PORT}}
   CORS_ORIGINS=https://${{Frontend.RAILWAY_PUBLIC_DOMAIN}}
   ```
5. **Networking** → Generate Domain

### Шаг 2: Создать Frontend сервис

1. В том же проекте: **+ New** → GitHub Repo (тот же)
2. **Settings → Build:**
   - Dockerfile Path: `Dockerfile.frontend`
3. **Variables:**
   ```bash
   NODE_ENV=production
   VITE_BACKEND_API_URL=https://${{Backend.RAILWAY_PUBLIC_DOMAIN}}
   ```
4. **Networking** → Generate Domain

### Шаг 3: Готово! ✅

Railway автоматически:

- ✅ Связал Frontend и Backend
- ✅ Настроил HTTPS
- ✅ Назначил порты
- ✅ Настроил CORS

---

## 🔗 Как работает связь?

```
Frontend (https://frontend-abc.up.railway.app)
    │
    │ VITE_BACKEND_API_URL=https://backend-xyz.up.railway.app
    ▼
Backend (https://backend-xyz.up.railway.app)
    │
    │ CORS_ORIGINS=https://frontend-abc.up.railway.app
    ▼
External APIs (TikTok, OpenAI, Perplexity)
```

**Railway автоматически подставляет реальные URL вместо переменных!**

---

## 📁 Файлы конфигурации (уже готовы!)

- ✅ `Dockerfile.backend` - Backend Docker образ
- ✅ `Dockerfile.frontend` - Frontend Docker образ
- ✅ `railway.backend.json` - Backend конфигурация
- ✅ `railway.frontend.json` - Frontend конфигурация
- ✅ `docker-entrypoint.sh` - Nginx entrypoint
- ✅ `nginx.conf` - Nginx конфигурация

**Все уже настроено! Просто следуйте 3 шагам выше.**

---

## 📚 Подробная документация

- 📖 [RAILWAY_ROUTING_EXPLAINED.md](./RAILWAY_ROUTING_EXPLAINED.md) - **КАК работает маршрутизация**
- 🚀 [RAILWAY_QUICKSTART_RU.md](./RAILWAY_QUICKSTART_RU.md) - Быстрый старт
- 📋 [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md) - Полный чеклист

---

**Версия:** TrendXL 2.0  
**Дата:** 1 октября 2025
