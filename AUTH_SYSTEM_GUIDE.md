# 🔐 Система Аутентификации TrendXL 2.0

## Обзор

Реализована полноценная система регистрации/авторизации пользователей с использованием:

- **Backend**: FastAPI + SQLite + JWT токены
- **Frontend**: React + Chakra UI v3 + Context API
- **Безопасность**: Bcrypt для хеширования паролей, JWT для сессий

## 🏗️ Архитектура

### Backend (Python)

#### 1. База данных (`backend/database.py`)

- SQLite база данных (`trendxl_users.db`)
- Таблица `users` с полями:
  - id, email, username, hashed_password
  - full_name, avatar_url, bio
  - created_at, last_login, is_active

#### 2. Сервис аутентификации (`backend/auth_service.py`)

- Модели Pydantic для валидации данных
- Хеширование паролей с bcrypt
- Создание и верификация JWT токенов
- Токены действуют 7 дней

#### 3. API Endpoints (`backend/main.py`)

- `POST /api/v1/auth/register` - Регистрация
- `POST /api/v1/auth/login` - Вход
- `GET /api/v1/auth/me` - Получить текущего пользователя
- `PUT /api/v1/auth/profile` - Обновить профиль

### Frontend (React + TypeScript)

#### 1. Контекст аутентификации (`src/contexts/AuthContext.tsx`)

```typescript
const { user, token, login, register, logout, isAuthenticated } = useAuth();
```

#### 2. Компоненты

- `AuthModal.tsx` - Модальное окно входа/регистрации
- `UserProfileDropdown.tsx` - Выпадающее меню профиля
- `App.tsx` - Интеграция проверки аутентификации

## 🚀 Использование

### Запуск Backend

```bash
cd backend
python main.py
```

Backend будет доступен на `http://localhost:8000`

### Запуск Frontend

```bash
npm run dev
```

Frontend будет доступен на `http://localhost:5173`

## 📋 Логика работы

### 1. Первое посещение

- Пользователь видит форму ввода TikTok профиля
- При нажатии "Discover Trends" появляется модальное окно аутентификации

### 2. Регистрация

- Email (обязательно)
- Username (минимум 3 символа)
- Password (минимум 6 символов)
- Full Name (опционально)

После успешной регистрации:

- Создается JWT токен
- Токен сохраняется в localStorage
- Пользователь автоматически авторизован

### 3. Вход

- Email
- Password

После успешного входа:

- Создается новый JWT токен
- Обновляется last_login
- Пользователь перенаправляется на главную

### 4. Работа с приложением

- В шапке отображается профиль пользователя
- Доступ к "Discover Trends" без дополнительных проверок
- Токен автоматически проверяется при каждой загрузке страницы

### 5. Выход

- Токен удаляется из localStorage
- Пользователь возвращается на главную страницу

## 🔒 Безопасность

### Backend

1. **Пароли**: Хешируются с помощью bcrypt (никогда не хранятся в открытом виде)
2. **JWT**: Подписываются секретным ключом (SECRET_KEY в `auth_service.py`)
3. **Токены**: Имеют срок действия (7 дней по умолчанию)
4. **Валидация**: Все входные данные проверяются через Pydantic

### Frontend

1. **Токены**: Хранятся в localStorage (доступ только с того же домена)
2. **Автоматическая проверка**: При загрузке страницы проверяется валидность токена
3. **Защищенные маршруты**: Модальное окно перед доступом к функционалу

## ⚙️ Настройка

### Изменить SECRET_KEY (ВАЖНО!)

В продакшене обязательно измените секретный ключ в `backend/auth_service.py`:

```python
# ВАЖНО: В продакшене используйте переменную окружения!
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
```

### Изменить время жизни токена

В `backend/auth_service.py`:

```python
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 дней
```

### Настроить API URL

В `src/contexts/AuthContext.tsx`:

```typescript
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
```

Или создайте файл `.env` в корне проекта:

```env
VITE_API_URL=http://your-backend-url.com
```

## 📝 API Примеры

### Регистрация

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "johndoe",
    "password": "secret123",
    "full_name": "John Doe"
  }'
```

Ответ:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "full_name": "John Doe",
    "created_at": "2025-09-30T12:00:00"
  }
}
```

### Вход

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secret123"
  }'
```

### Получить текущего пользователя

```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 🐛 Отладка

### Backend не запускается

```bash
# Проверьте установку зависимостей
cd backend
pip install -r requirements.txt

# Проверьте порт
netstat -an | findstr :8000
```

### Frontend не подключается к Backend

1. Проверьте, что backend запущен на `http://localhost:8000`
2. Проверьте CORS настройки в `backend/main.py`
3. Откройте DevTools → Network и проверьте запросы

### Токен не сохраняется

1. Откройте DevTools → Application → Local Storage
2. Проверьте наличие ключа `auth_token`
3. Проверьте консоль на ошибки

### База данных

```bash
# Посмотреть содержимое базы данных
cd backend
sqlite3 trendxl_users.db
sqlite> SELECT * FROM users;
sqlite> .quit
```

## 🎨 Кастомизация UI

### Изменить цвета модального окна

В `src/components/AuthModal.tsx`:

```typescript
// Фон модального окна
bg = "white"; // Измените на нужный цвет

// Кнопки
bg = "black"; // Основной цвет кнопок
```

### Изменить стиль профиля

В `src/components/UserProfileDropdown.tsx` можно настроить:

- Размер аватара
- Цвета текста
- Стиль выпадающего меню

## 📦 Структура файлов

```
backend/
├── auth_service.py      # JWT, bcrypt, модели
├── database.py          # SQLite, CRUD операции
├── main.py              # API endpoints
└── trendxl_users.db     # База данных (создается автоматически)

src/
├── contexts/
│   └── AuthContext.tsx  # React контекст аутентификации
├── components/
│   ├── AuthModal.tsx    # Форма входа/регистрации
│   └── UserProfileDropdown.tsx  # Меню профиля
├── App.tsx              # Интеграция проверки аутентификации
└── main.tsx             # AuthProvider wrapper
```

## ✅ Что реализовано

- [x] Регистрация пользователей
- [x] Вход в систему
- [x] JWT токены с автоматическим обновлением
- [x] Хеширование паролей с bcrypt
- [x] SQLite база данных
- [x] Модальное окно входа/регистрации
- [x] Выпадающее меню профиля
- [x] Проверка аутентификации перед "Discover Trends"
- [x] Сохранение сессии в localStorage
- [x] Автоматическая валидация токена
- [x] Обновление профиля (API готово)

## 🚧 TODO (Будущие улучшения)

- [ ] Страница профиля пользователя
- [ ] Сброс пароля через email
- [ ] OAuth (Google, GitHub)
- [ ] Сохранение избранных трендов
- [ ] История анализов пользователя
- [ ] Настройки уведомлений
- [ ] Загрузка аватара
- [ ] Двухфакторная аутентификация

## 🤝 Поддержка

Если возникли проблемы:

1. Проверьте логи backend в консоли
2. Проверьте DevTools Console в браузере
3. Убедитесь, что все зависимости установлены
4. Проверьте, что порты 8000 и 5173 свободны

---

**Важно**: В продакшене обязательно:

1. Измените SECRET_KEY на случайный ключ
2. Используйте HTTPS
3. Настройте правильные CORS origins
4. Используйте PostgreSQL вместо SQLite для production
5. Добавьте rate limiting для API
