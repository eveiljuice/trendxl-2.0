# 🚀 Railway Quick Start - TrendXL 2.0

Быстрый деплой двух сервисов (бэкенд + фронтенд) на Railway.

---

## 📦 Что будет развернуто

- **Backend Service**: FastAPI (Python) на `Dockerfile.backend`
- **Frontend Service**: React + Nginx на `Dockerfile.frontend`

---

## ⚡ Быстрый старт через Railway UI

### 1️⃣ Создайте проект

1. Откройте [railway.app](https://railway.app)
2. **New Project** → **Deploy from GitHub repo**
3. Выберите ваш репозиторий `trendxl 2.0`

### 2️⃣ Настройте Backend Service

Railway автоматически создаст сервис. Настройте его:

1. **Откройте сервис** → **Settings**
2. **Service Name**: `backend` (переименуйте если нужно)
3. **Config as Code**: Укажите `railway.backend.toml`
4. **Variables** → Добавьте:
   ```env
   ENSEMBLE_API_TOKEN=ваш_токен
   OPENAI_API_KEY=ваш_ключ
   PERPLEXITY_API_KEY=ваш_ключ_perplexity
   ```
5. **Deploy** (Railway развернет автоматически)
6. **Скопируйте URL** бэкенда (например: `https://trendxl-backend-production.up.railway.app`)

### 3️⃣ Добавьте Frontend Service

1. **+ New Service** → **GitHub Repo** (тот же репозиторий)
2. **Service Name**: `frontend`
3. **Settings** → **Config as Code**: `railway.frontend.toml`
4. **Variables** → Добавьте:
   ```env
   VITE_BACKEND_API_URL=https://ваш-backend-url.up.railway.app
   ```
   **ИЛИ** используйте референс:
   ```env
   VITE_BACKEND_API_URL=https://${{backend.RAILWAY_PUBLIC_DOMAIN}}
   ```
5. **Deploy**

### ✅ Готово!

- **Backend**: `https://ваш-backend.up.railway.app/health`
- **Frontend**: `https://ваш-frontend.up.railway.app`

---

## 🖥️ Быстрый старт через Railway CLI

```bash
# 1. Установите CLI
npm i -g @railway/cli

# 2. Войдите
railway login

# 3. Создайте проект
railway init

# 4. Создайте Backend сервис
railway add --service backend

# Настройте backend в Railway UI:
# Settings → Config as Code → railway.backend.toml

# 5. Установите переменные backend
railway variables set ENSEMBLE_API_TOKEN="ваш_токен" --service backend
railway variables set OPENAI_API_KEY="ваш_ключ" --service backend
railway variables set PERPLEXITY_API_KEY="ваш_ключ" --service backend

# 6. Разверните backend
railway up --service backend

# 7. Создайте Frontend сервис
railway add --service frontend

# Настройте frontend в Railway UI:
# Settings → Config as Code → railway.frontend.toml

# 8. Получите URL backend
BACKEND_URL=$(railway domain --service backend)

# 9. Установите переменную frontend
railway variables set VITE_BACKEND_API_URL="https://${BACKEND_URL}" --service frontend

# 10. Разверните frontend
railway up --service frontend
```

---

## 🔧 Важные моменты

### ⚠️ VITE переменные

`VITE_*` переменные встраиваются **во время сборки**. Если вы изменили `VITE_BACKEND_API_URL`, **пересоберите фронтенд**:

```bash
railway up --service frontend
```

### 📁 Конфигурационные файлы

- `railway.backend.toml` - конфигурация бэкенда
- `railway.frontend.toml` - конфигурация фронтенда
- `railway.toml` - устаревший (только для single-service)

### 🔍 Watch Patterns

Railway автоматически пересобирает только нужный сервис:

- **Backend**: пересборка при изменениях в `/backend/**`
- **Frontend**: пересборка при изменениях в `/src/**`, `/public/**` и т.д.

---

## 🐛 Проблемы?

### Backend не запускается

```bash
# Проверьте логи
railway logs --service backend

# Проверьте переменные
railway variables --service backend

# Проверьте health endpoint
curl https://ваш-backend.up.railway.app/health
```

### Frontend не соединяется с Backend

1. Проверьте `VITE_BACKEND_API_URL`:

   ```bash
   railway variables --service frontend
   ```

2. Если изменили - пересоберите:

   ```bash
   railway up --service frontend
   ```

3. Проверьте CORS на бэкенде

---

## 📚 Полная документация

Смотрите **[RAILWAY_DEPLOYMENT_GUIDE_V2.md](./RAILWAY_DEPLOYMENT_GUIDE_V2.md)** для:

- Детальной настройки
- Troubleshooting
- Advanced конфигурация
- Мониторинг и логи

---

## ✨ Полезные команды

```bash
# Просмотр логов
railway logs --service backend --follow
railway logs --service frontend --follow

# Просмотр переменных
railway variables --service backend
railway variables --service frontend

# Обновление переменных
railway variables set KEY="value" --service backend

# Ручной деплой
railway up --service backend
railway up --service frontend

# SSH в контейнер
railway ssh --service backend

# Просмотр статуса
railway status
```

---

**Успешного деплоя! 🎉**
