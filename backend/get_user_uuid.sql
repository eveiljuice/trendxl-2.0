-- Получить UUID вашего пользователя
SELECT 
    id as user_uuid,
    email,
    created_at
FROM auth.users
WHERE email = 'timolast@example.com';  -- ЗАМЕНИТЕ на ваш email если нужно

-- Или просто все пользователи
SELECT 
    id as user_uuid,
    email
FROM auth.users
ORDER BY created_at DESC;

