# 🚂 Railway Deployment - TrendXL 2.0

> Полная конфигурация для развертывания бэкенда и фронтенда на Railway

---

## 📦 Структура файлов

```
trendxl 2.0/
├── railway.backend.toml          # ✅ Backend сервис конфигурация
├── railway.frontend.toml         # ✅ Frontend сервис конфигурация
├── railway.toml                  # ⚠️  Deprecated (single-service)
│
├── Dockerfile.backend            # 🐳 Backend Docker image
├── Dockerfile.frontend           # 🐳 Frontend Docker image
│
├── RAILWAY_QUICK_START.md        # ⚡ Быстрый старт (начните с этого!)
├── RAILWAY_DEPLOYMENT_GUIDE_V2.md # 📖 Полное руководство
├── RAILWAY_DEPLOYMENT_SUMMARY.md # 📋 Сводка и архитектура
│
└── backend/                      # Python FastAPI приложение
    └── frontend/src/             # React приложение
```

---

## 🚀 С чего начать?

### Вариант 1: Быстрый старт (5 минут)

Читайте **[RAILWAY_QUICK_START.md](./RAILWAY_QUICK_START.md)**

Кратко:

1. Создайте проект на Railway
2. Добавьте backend сервис → настройте `railway.backend.toml`
3. Добавьте frontend сервис → настройте `railway.frontend.toml`
4. Готово! ✨

### Вариант 2: Полное руководство

Читайте **[RAILWAY_DEPLOYMENT_GUIDE_V2.md](./RAILWAY_DEPLOYMENT_GUIDE_V2.md)**

Включает:

- Детальные инструкции UI и CLI
- Настройка environment variables
- Service communication
- Мониторинг и логи
- Troubleshooting
- Advanced configuration

### Вариант 3: Изучить архитектуру

Читайте **[RAILWAY_DEPLOYMENT_SUMMARY.md](./RAILWAY_DEPLOYMENT_SUMMARY.md)**

Включает:

- Диаграммы архитектуры
- Детали конфигурации
- Безопасность
- Масштабирование

---

## 🎯 Два независимых сервиса

### Backend Service

- **Config**: `railway.backend.toml`
- **Dockerfile**: `Dockerfile.backend`
- **Технологии**: Python, FastAPI, Uvicorn
- **Watch**: `/backend/**`
- **Port**: Auto (Railway)
- **Health**: `/health`

### Frontend Service

- **Config**: `railway.frontend.toml`
- **Dockerfile**: `Dockerfile.frontend`
- **Технологии**: React, Vite, Nginx
- **Watch**: `/src/**`, `/public/**`
- **Port**: Auto (Railway)
- **Health**: `/health`

---

## 🔑 Необходимые переменные окружения

### Backend (обязательно)

```env
ENSEMBLE_API_TOKEN=your_token
OPENAI_API_KEY=sk-your_key
PERPLEXITY_API_KEY=pplx-your_key
```

### Frontend (обязательно)

```env
VITE_BACKEND_API_URL=https://your-backend.up.railway.app
```

---

## 📖 Документация Railway

Файлы документации в этом проекте:

| Файл                               | Описание             | Когда использовать  |
| ---------------------------------- | -------------------- | ------------------- |
| **RAILWAY_QUICK_START.md**         | Быстрый старт        | Первый деплой       |
| **RAILWAY_DEPLOYMENT_GUIDE_V2.md** | Полное руководство   | Детальная настройка |
| **RAILWAY_DEPLOYMENT_SUMMARY.md**  | Архитектура и сводка | Понимание системы   |
| **README_RAILWAY_DEPLOYMENT.md**   | Этот файл            | Навигация           |

---

## ⚡ Быстрые команды

```bash
# Railway CLI
railway login
railway init

# Backend
railway add --service backend
railway up --service backend
railway logs --service backend

# Frontend
railway add --service frontend
railway up --service frontend
railway logs --service frontend

# Переменные
railway variables set KEY="value" --service backend
railway variables --service backend
```

---

## 🐛 Частые проблемы

### ❌ Backend не запускается

**Причина**: Отсутствуют API ключи  
**Решение**: Установите `ENSEMBLE_API_TOKEN` и `OPENAI_API_KEY`

### ❌ Frontend не соединяется с Backend

**Причина**: Неправильный `VITE_BACKEND_API_URL`  
**Решение**: Проверьте URL и **пересоберите** frontend (VITE vars are build-time!)

### ❌ Пересборка не нужного сервиса

**Причина**: Изменили файлы вне watch patterns  
**Решение**: Watch patterns настроены корректно в `.toml` файлах

---

## ✅ Checklist

Перед деплоем убедитесь:

- [ ] Оба Dockerfile (`Dockerfile.backend`, `Dockerfile.frontend`) существуют
- [ ] Оба конфиг файла (`railway.backend.toml`, `railway.frontend.toml`) настроены
- [ ] API ключи готовы (Ensemble, OpenAI, Perplexity)
- [ ] Backend health check работает: `/health`
- [ ] Frontend health check работает: `/health`
- [ ] CORS настроен на backend
- [ ] Git репозиторий подключен к Railway

---

## 🌐 После деплоя

Проверьте:

1. **Backend health**: `curl https://your-backend.up.railway.app/health`
2. **Frontend health**: `curl https://your-frontend.up.railway.app/health`
3. **Frontend → Backend**: Откройте frontend, попробуйте запрос
4. **Logs**: Проверьте логи обоих сервисов

---

## 📞 Поддержка

- [Railway Docs](https://docs.railway.app)
- [Railway Discord](https://discord.gg/railway)
- [Monorepo Guide](https://docs.railway.app/guides/monorepo)
- [Config as Code](https://docs.railway.app/reference/config-as-code)

---

## 🎉 Успешного развертывания!

Следующие шаги:

1. 📖 Читайте **RAILWAY_QUICK_START.md**
2. 🚀 Разверните на Railway
3. 🧪 Протестируйте оба сервиса
4. 📊 Настройте мониторинг
5. 🔄 Настройте CI/CD

**Готово к деплою! 🚂🚀**

---

**Версия**: 2.0  
**Дата**: 2025-09-30  
**Статус**: ✅ Production Ready
