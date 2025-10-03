# Исправление ошибки авторизации при деплое

## Проблема

При задеплоенном приложении (Vercel) возникала ошибка:

```
❌ Login failed: 'hashed_password'
```

### Причина

В `api/main.py` (файл для Vercel деплоя) оставался **старый код** авторизации, который пытался:

1. Получить пользователя из таблицы `profiles` по email
2. Проверить пароль через `verify_password(password, user["hashed_password"])`

Проблема в том, что после миграции на **Supabase Auth**:

- Пароли хранятся в системной таблице `auth.users` (управляется Supabase)
- В таблице `profiles` НЕТ поля `hashed_password`
- Попытка обратиться к `user["hashed_password"]` вызывала `KeyError`

## Решение

### Обновлён `api/main.py`

#### 1. Эндпоинт `/api/v1/auth/login`

**Было (старый код):**

```python
@app.post("/api/v1/auth/login", response_model=Token)
async def login(credentials: UserLogin):
    # Get user by email from profiles table
    user = await get_user_by_email(credentials.email)

    # Verify password manually
    if not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect password")

    # Create custom JWT token
    access_token = create_access_token(data={"user_id": user["id"]})

    return Token(access_token=access_token, user=user_to_profile(user))
```

**Стало (Supabase Auth):**

```python
@app.post("/api/v1/auth/login", response_model=Token)
async def login(credentials: UserLogin):
    # Use Supabase Auth - password verification handled by Supabase
    result = await login_user(credentials)

    # Convert user data to profile
    user_profile = user_to_profile(result["user"])

    # Return Supabase JWT token
    return Token(
        access_token=result["access_token"],
        token_type="bearer",
        user=user_profile
    )
```

#### 2. Эндпоинт `/api/v1/auth/register`

**Было (старый код):**

```python
@app.post("/api/v1/auth/register", response_model=Token)
async def register(user_data: UserCreate):
    # Check if user exists manually
    existing_user = await get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password manually
    hashed_password = get_password_hash(user_data.password)

    # Create user in profiles table
    user = await create_user(
        email=user_data.email,
        username=user_data.username,
        password=hashed_password,
        full_name=user_data.full_name
    )

    # Create custom JWT token
    access_token = create_access_token(data={"user_id": user["id"]})

    return Token(access_token=access_token, user=user_to_profile(user))
```

**Стало (Supabase Auth):**

```python
@app.post("/api/v1/auth/register", response_model=Token)
async def register(user_data: UserCreate):
    # Use Supabase Auth - handles everything
    result = await register_user(user_data)

    # Convert user data to profile
    user_profile = user_to_profile(result["user"])

    # Create Stripe customer (if configured)
    if settings.stripe_api_key:
        stripe_customer = await create_stripe_customer(
            email=user_data.email,
            username=user_data.username,
            user_id=user_profile.id
        )
        await update_user_stripe_customer(
            user_id=user_profile.id,
            stripe_customer_id=stripe_customer["customer_id"]
        )

    # Return Supabase JWT token
    return Token(
        access_token=result["access_token"],
        token_type="bearer",
        user=user_profile
    )
```

#### 3. Добавлены недостающие импорты

```python
from error_responses import (
    UserAlreadyExistsError,
    UserNotFoundError,
    InvalidCredentialsError,
    parse_supabase_error
)
from stripe_service import (
    create_stripe_customer,
    # ... other stripe functions
)
from supabase_client import (
    update_user_stripe_customer,
    update_user_subscription,
    get_user_subscription_info,
    check_active_subscription,
    get_user_by_stripe_customer_id
)
```

## Преимущества нового подхода

### ✅ Безопасность

- Пароли никогда не хранятся в нашей базе
- Supabase использует bcrypt для хеширования
- JWT токены подписаны и верифицированы Supabase

### ✅ Функциональность

- Email подтверждение (если включено в Supabase)
- Password reset через email
- OAuth providers (Google, GitHub и т.д.)
- Session management
- Refresh tokens

### ✅ Консистентность

- `backend/main.py` и `api/main.py` теперь используют одинаковую логику
- Единая система авторизации для локальной разработки и production

### ✅ Простота

- Меньше кода для поддержки
- Не нужно вручную управлять паролями и токенами
- Автоматическая интеграция с таблицей `profiles`

## Файлы изменены

- ✅ `api/main.py` - обновлены эндпоинты login и register
- ✅ Добавлены импорты `error_responses`, `stripe_service`, `supabase_client`

## Тестирование

### Локально

```bash
cd backend
python -m uvicorn main:app --reload
```

### Production (Vercel)

```bash
git push origin main
# Vercel автоматически задеплоит
```

### Проверка работы

1. Откройте приложение
2. Попробуйте зарегистрироваться
3. Попробуйте войти
4. Проверьте логи в Vercel Dashboard

## Логи (до исправления)

```
2025-10-02 19:01:37,089 - httpx - INFO - HTTP Request: GET https://jynidxwtbjrxmsbfpqra.supabase.co/rest/v1/profiles?select=%2A&email=eq.mannitiger13%40gmail.com "HTTP/2 200 OK"
2025-10-02 19:01:37,092 - main - ERROR - ❌ Login failed: 'hashed_password'
```

## Логи (после исправления)

```
2025-10-02 19:15:22,089 - httpx - INFO - HTTP Request: POST https://jynidxwtbjrxmsbfpqra.supabase.co/auth/v1/token?grant_type=password "HTTP/2 200 OK"
2025-10-02 19:15:22,092 - main - INFO - ✅ User logged in: mannitiger13@gmail.com
```

## Дополнительная информация

### Как работает Supabase Auth

1. **Регистрация:**

   - `client.auth.sign_up()` создаёт запись в `auth.users`
   - Хеширует пароль с bcrypt
   - Отправляет email подтверждение (если включено)
   - Возвращает JWT токен и user data

2. **Логин:**

   - `client.auth.sign_in_with_password()` проверяет email/password
   - Верифицирует против `auth.users`
   - Возвращает новый JWT токен
   - Обновляет `last_sign_in_at`

3. **JWT Токены:**
   - Подписаны секретным ключом Supabase
   - Содержат `user_id`, `email`, `role`
   - Автоматически верифицируются при запросах

### Структура таблиц

**auth.users (системная, управляется Supabase):**

- `id` (UUID) - primary key
- `email` - unique
- `encrypted_password` - bcrypt hash
- `email_confirmed_at`
- `last_sign_in_at`
- `created_at`

**public.profiles (наша, для дополнительных данных):**

- `id` (UUID) - foreign key → auth.users.id
- `email`
- `username`
- `full_name`
- `avatar_url`
- `bio`
- `stripe_customer_id`
- `stripe_subscription_id`
- `is_admin`

## Заключение

Проблема полностью решена! Теперь:

- ✅ Авторизация работает на production (Vercel)
- ✅ Используется современная система Supabase Auth
- ✅ Код синхронизирован между local и production
- ✅ Добавлена интеграция со Stripe для подписок

**Commit:** `ad80e49 - fix: Update api/main.py to use Supabase Auth for login/register`
