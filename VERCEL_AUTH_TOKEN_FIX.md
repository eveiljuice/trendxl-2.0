# Vercel Authentication & Redis Fixes

## Проблемы, которые были исправлены

### 1. ❌ Redis Connection Error

**Ошибка в логах:**

```
Redis not available, caching disabled: Error 111 connecting to localhost:6379. Connection refused.
```

**Причина:**

- Backend пытался подключиться к `localhost:6379` по умолчанию
- В Vercel serverless окружении Redis недоступен локально
- Переменная `REDIS_URL` не была установлена

**Решение:**

- ✅ Изменён default значение `redis_url` в `backend/config.py` на пустую строку
- ✅ Добавлена проверка в `backend/services/cache_service.py`:
  - Если `REDIS_URL` не установлена или пустая → Redis отключается gracefully
  - Выводится информационное сообщение вместо ошибки
  - Приложение продолжает работать без кеша

**Файлы изменены:**

- `backend/config.py` - изменён default для `redis_url`
- `backend/services/cache_service.py` - добавлена проверка и graceful отключение

---

### 2. ❌ JWT Token Expired Error

**Ошибка в логах:**

```
HTTP Request: GET https://jynidxwtbjrxmsbfpqra.supabase.co/auth/v1/user "HTTP/2 403 Forbidden"
Token decode failed: invalid JWT: unable to parse or verify signature, token has invalid claims: token is expired
"GET /api/v1/auth/me HTTP/1.1" 401 -
```

**Причина:**

- JWT access token истёк (обычно через 1 час)
- Не было автоматического обновления токена через Supabase refresh token
- Фронтенд не обрабатывал 401 ошибки и не пытался обновить токен

**Решение:**

#### Backend (`backend/auth_service_supabase.py`):

- ✅ Улучшена обработка ошибок в `get_current_user()`
- ✅ Добавлена проверка на expired токены с понятным сообщением
- ✅ Логируются предупреждения вместо ошибок для expired токенов

#### Frontend (`src/contexts/AuthContext.tsx`):

- ✅ Добавлен обработчик `TOKEN_REFRESHED` в `onAuthStateChange`
- ✅ Добавлен обработчик `TOKEN_EXPIRED` с автоматическим refresh
- ✅ Улучшена функция `verifyToken()`:
  - Автоматически пытается обновить токен при 401 ошибке
  - Использует `supabase.auth.refreshSession()` для получения нового токена
  - Повторяет запрос с новым токеном (максимум 1 раз)
  - При неудаче очищает сессию и разлогинивает пользователя

#### API Service (`src/services/backendApi.ts`):

- ✅ Добавлен axios interceptor для обработки 401 ошибок
- ✅ Автоматически обновляет токен через Supabase при 401
- ✅ Повторяет неудачный запрос с новым токеном
- ✅ Перенаправляет на /login при неудаче refresh

**Файлы изменены:**

- `backend/auth_service_supabase.py` - улучшена обработка expired токенов
- `src/contexts/AuthContext.tsx` - добавлено автообновление токенов
- `src/services/backendApi.ts` - добавлен interceptor для 401

---

## Как это работает теперь

### JWT Token Refresh Flow

1. **Пользователь логинится:**

   - Supabase выдаёт access token (истекает через 1 час) и refresh token
   - Оба токена сохраняются в localStorage и Supabase session

2. **Access token истекает:**

   - При любом API запросе backend возвращает 401
   - Axios interceptor перехватывает 401 ошибку
   - Автоматически вызывается `supabase.auth.refreshSession()`
   - Получается новый access token
   - Повторяется исходный запрос с новым токеном

3. **Проактивный refresh (Supabase SDK):**

   - Supabase SDK автоматически обновляет токен за 5 минут до истечения
   - Срабатывает `onAuthStateChange` с событием `TOKEN_REFRESHED`
   - Новый токен сохраняется в localStorage
   - Пользователь даже не замечает обновления

4. **При неудаче refresh:**
   - Пользователь разлогинивается
   - Очищается localStorage и Supabase session
   - Редирект на страницу логина

### Redis Caching

1. **Без REDIS_URL:**

   - Кеш отключен gracefully
   - Выводится информационное сообщение в логи
   - Приложение работает нормально (просто медленнее)

2. **С REDIS_URL (optional):**
   - Можно добавить Upstash Redis или Redis Cloud
   - Кеш ускоряет повторные запросы
   - Рекомендуется для production, но не обязательно

---

## Настройка для Vercel

### Обязательные переменные окружения:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
JWT_SECRET=your-jwt-secret
STRIPE_API_KEY=sk-test-...
STRIPE_PRICE_ID=price_...
ENSEMBLE_API_TOKEN=your-ensemble-token
OPENAI_API_KEY=sk-...
PERPLEXITY_API_KEY=pplx-...
```

### Опциональные переменные:

```bash
# Redis (recommended for production, not required)
REDIS_URL=redis://default:password@redis.upstash.io:6379

# Stripe webhook (для production payments)
STRIPE_WEBHOOK_SECRET=whsec_...
```

---

## Тестирование

### Локально:

```bash
# Backend
cd backend
python run_server.py

# Frontend
npm run dev
```

### Проверка token refresh:

1. Залогиньтесь в приложение
2. Откройте DevTools → Application → Local Storage
3. Скопируйте `auth_token`
4. Подождите >1 часа или измените JWT expiration в Supabase Auth Settings
5. Попробуйте сделать API запрос
6. Токен должен автоматически обновиться без перелогина

### Проверка Redis:

1. Без `REDIS_URL` в логах должно быть:
   ```
   ℹ️ Redis caching disabled (REDIS_URL not configured)
   ```
2. Приложение работает нормально, просто без кеша

---

## Дополнительно: Настройка Redis (optional)

Для улучшения производительности можно добавить Redis:

### Вариант 1: Upstash Redis (рекомендуется для Vercel)

1. Зарегистрируйтесь на https://upstash.com
2. Создайте Redis database
3. Скопируйте `UPSTASH_REDIS_REST_URL`
4. Добавьте в Vercel Environment Variables:
   ```
   REDIS_URL=redis://default:password@your-redis.upstash.io:6379
   ```

### Вариант 2: Redis Cloud

1. Зарегистрируйтесь на https://redis.com/try-free/
2. Создайте database
3. Получите connection URL
4. Добавьте как `REDIS_URL` в Vercel

---

## Итоговые улучшения

✅ **Исправлена ошибка Redis connection refused**

- Приложение работает без Redis
- Graceful degradation вместо ошибок

✅ **Исправлена ошибка JWT token expired**

- Автоматическое обновление токенов через Supabase
- Проактивный refresh за 5 минут до истечения
- Retry при 401 ошибках
- Улучшенный UX - пользователь не замечает refresh

✅ **Улучшена обработка ошибок**

- Понятные сообщения в логах
- Корректная обработка expired tokens
- Автоматический logout при неудаче

✅ **Production-ready**

- Работает в Vercel serverless окружении
- Не требует обязательного Redis
- Полная поддержка JWT token lifecycle
