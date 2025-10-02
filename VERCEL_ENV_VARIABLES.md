# 🔐 Переменные окружения для Vercel

## ⚠️ ВАЖНО: Frontend переменные должны начинаться с `VITE_`

В Vite все переменные окружения, которые должны быть доступны в браузере (frontend), **ОБЯЗАТЕЛЬНО** должны начинаться с префиксом `VITE_`.

## 📝 Список всех переменных окружения

Перейдите в настройки проекта на Vercel:
👉 https://vercel.com/shomas-projects-2d51e250/trendxl-2-0-01102025/settings/environment-variables

### 1. Frontend (Supabase для браузера) - ОБЯЗАТЕЛЬНО

Эти переменные нужны для работы аутентификации в браузере:

```
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_ANON_KEY=your-supabase-anon-key-here
```

**Где взять:**

- Откройте: https://supabase.com/dashboard/project/YOUR_PROJECT_ID/settings/api
- `VITE_SUPABASE_URL` = Project URL
- `VITE_SUPABASE_ANON_KEY` = anon / public key

### 2. Backend (Supabase для API) - ОБЯЗАТЕЛЬНО

Эти переменные нужны для Python API функций:

```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key-here
```

**Где взять:**

- `SUPABASE_SERVICE_ROLE_KEY` = service_role key (тот же раздел, что выше)

### 3. Stripe (для подписок) - ОБЯЗАТЕЛЬНО

```
STRIPE_API_KEY=sk_test_xxxxx или sk_live_xxxxx
STRIPE_PRICE_ID=price_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx (опционально)
```

**Где взять:**

- `STRIPE_API_KEY`: https://dashboard.stripe.com/apikeys
- `STRIPE_PRICE_ID`: https://dashboard.stripe.com/prices (создайте Price для $29/month)
- `STRIPE_WEBHOOK_SECRET`: https://dashboard.stripe.com/webhooks (при настройке webhook)

### 4. API Keys для функциональности

```
ENSEMBLE_API_TOKEN=your-ensemble-api-token
OPENAI_API_KEY=sk-xxxxx или sk-proj-xxxxx
PERPLEXITY_API_KEY=pplx-xxxxx (опционально)
```

**Где взять:**

- `ENSEMBLE_API_TOKEN`: https://dashboard.ensembledata.com/
- `OPENAI_API_KEY`: https://platform.openai.com/api-keys
- `PERPLEXITY_API_KEY`: https://www.perplexity.ai/settings/api

### 5. Backend URL для frontend

```
VITE_BACKEND_API_URL=https://trendxl-2-0-01102025.vercel.app
```

Это URL вашего деплоя на Vercel.

## 📋 Полный список для копирования

Скопируйте этот шаблон и замените значения на свои:

```bash
# ============= FRONTEND (обязательно с VITE_) =============
VITE_SUPABASE_URL=https://your-project-id.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGci...
VITE_BACKEND_API_URL=https://trendxl-2-0-01102025.vercel.app

# ============= BACKEND (Python API) =============
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=eyJhbGci...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...

# ============= STRIPE =============
STRIPE_API_KEY=sk_test_xxxxx
STRIPE_PRICE_ID=price_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx

# ============= API KEYS =============
ENSEMBLE_API_TOKEN=your-token
OPENAI_API_KEY=sk-xxxxx
PERPLEXITY_API_KEY=pplx-xxxxx
```

## ⚙️ Как добавить переменные в Vercel

### Способ 1: Через веб-интерфейс

1. Откройте: https://vercel.com/shomas-projects-2d51e250/trendxl-2-0-01102025/settings/environment-variables
2. Для каждой переменной:
   - Нажмите **"Add New"**
   - **Key**: введите имя переменной (например, `VITE_SUPABASE_URL`)
   - **Value**: введите значение
   - **Environments**: выберите **Production**, **Preview**, **Development**
   - Нажмите **"Save"**

### Способ 2: Через CLI (если установлен)

```bash
# Frontend
vercel env add VITE_SUPABASE_URL production
vercel env add VITE_SUPABASE_ANON_KEY production
vercel env add VITE_BACKEND_API_URL production

# Backend
vercel env add SUPABASE_URL production
vercel env add SUPABASE_ANON_KEY production
vercel env add SUPABASE_SERVICE_ROLE_KEY production

# Stripe
vercel env add STRIPE_API_KEY production
vercel env add STRIPE_PRICE_ID production

# API Keys
vercel env add ENSEMBLE_API_TOKEN production
vercel env add OPENAI_API_KEY production
```

## 🔄 После добавления переменных

1. Vercel покажет баннер "Environment Variables Updated"
2. Нажмите **"Redeploy"** для пересборки проекта с новыми переменными
3. Дождитесь завершения деплоймента (статус READY)
4. Откройте сайт и проверьте, что ошибка исчезла

## ✅ Как проверить, что всё работает

### Откройте сайт:

https://trendxl-2-0-01102025.vercel.app

### Проверьте консоль браузера (F12):

- ❌ Если видите: `"⚠️ Supabase configuration missing"` → переменные не добавлены или имеют неправильные имена
- ✅ Если ошибки нет → всё настроено правильно!

### Попробуйте зарегистрироваться:

1. Нажмите "Sign Up"
2. Введите email и пароль
3. Если всё работает → Supabase настроен правильно! 🎉

## 🐛 Troubleshooting

### Ошибка: "supabaseUrl is required"

**Причина**: Не добавлены `VITE_SUPABASE_URL` и `VITE_SUPABASE_ANON_KEY`  
**Решение**: Добавьте эти переменные с префиксом `VITE_` и пересоберите проект

### API возвращает 500

**Причина**: Не добавлены backend переменные (`SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`)  
**Решение**: Добавьте backend переменные БЕЗ префикса `VITE_`

### Stripe не работает

**Причина**: Не добавлены `STRIPE_API_KEY` или `STRIPE_PRICE_ID`  
**Решение**: Добавьте Stripe переменные

## 📚 Дополнительные ресурсы

- **Vercel Environment Variables**: https://vercel.com/docs/projects/environment-variables
- **Vite Environment Variables**: https://vitejs.dev/guide/env-and-mode.html
- **Supabase Keys**: https://supabase.com/docs/guides/api/api-keys
- **Stripe API Keys**: https://stripe.com/docs/keys

---

💡 **Совет**: Используйте разные ключи для Production и Preview окружений для безопасности!
