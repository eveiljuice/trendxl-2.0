# 🔑 Админ-аккаунт - Быстрый старт

## Что это дает?

✅ **Полный доступ ко всем сервисам без подписки**  
✅ **Неограниченное использование всех API**  
✅ **Никаких проверок лимитов**

## Установка за 3 шага

### Шаг 1: Примените миграцию в Supabase

1. Откройте [Supabase SQL Editor](https://supabase.com/dashboard/project/jynidxwtbjrxmsbfpqra/sql/new)
2. Скопируйте и выполните этот SQL:

```sql
-- Add is_admin column to profiles table
ALTER TABLE profiles
ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE;

-- Create index for quick admin lookups
CREATE INDEX IF NOT EXISTS idx_profiles_is_admin ON profiles(is_admin) WHERE is_admin = TRUE;

-- Add comment explaining the field
COMMENT ON COLUMN profiles.is_admin IS 'Admin users have full access to all services without subscription limits';
```

3. Нажмите **RUN** ✅

### Шаг 2: Зарегистрируйте аккаунты

Если еще не зарегистрированы:

- Зайдите на сайт
- Создайте аккаунты для вас и партнера

### Шаг 3: Установите админ-статус

**Вариант A: Через Python скрипт (Быстрее)**

```bash
cd backend
python set_admin.py your-email@example.com
python set_admin.py partner-email@example.com
```

**Вариант B: Через Supabase SQL Editor**

```sql
UPDATE profiles
SET is_admin = TRUE
WHERE email IN ('your-email@example.com', 'partner-email@example.com');

-- Проверка
SELECT email, username, is_admin FROM profiles WHERE is_admin = TRUE;
```

## ✅ Готово!

Теперь вы и ваш партнер можете:

- Использовать все функции без подписки
- Не беспокоиться о лимитах
- Иметь полный доступ к API

## Проверка

1. Залогиньтесь на сайте
2. Попробуйте использовать trend analysis
3. Проверьте логи бэкенда - должно появиться:
   ```
   🔑 Admin user <username> bypassing subscription check
   ```

## Безопасность

⚠️ **ВАЖНО**: Замените email-адреса в `backend/.env`:

```env
ADMIN_EMAILS=your-real-email@example.com,partner-real-email@example.com
```

## Удаление админ-статуса

Если нужно убрать админ-права:

```bash
python set_admin.py email@example.com --remove
```

---

**Нужна помощь?** См. полную документацию: `ADMIN_SETUP.md`
