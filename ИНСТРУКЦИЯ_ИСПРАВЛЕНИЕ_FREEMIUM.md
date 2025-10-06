# 🔥 СРОЧНОЕ ИСПРАВЛЕНИЕ: Freemium система не работает

## 🚨 Проблема
- Free trial счетчик не обновляется
- Записи не попадают в таблицу `daily_free_analyses`
- Пользователи могут делать бесконечное количество анализов

## ✅ РЕШЕНИЕ (следуй по порядку)

---

## 📝 ШАГ 1: SQL исправления в Supabase (10 минут)

### 1.1. Открой Supabase Dashboard

1. Перейди на https://supabase.com/dashboard
2. Выбери свой проект **TrendXL 2.0**
3. Открой **SQL Editor** (иконка с базой данных слева)

### 1.2. Выполни скрипт

1. Открой файл `QUICK_FIX_SUPABASE_FREEMIUM.sql` (только что создан)
2. Скопируй **ВЕСЬ** код
3. Вставь в SQL Editor
4. **ВАЖНО:** Найди строку 224:
   ```sql
   WHERE email LIKE '%timolast%'  -- ⬅️ ИЗМЕНИ НА СВОЙ EMAIL
   ```
5. Измени на часть твоего email (например `'%myemail%'`)
6. Нажми **Run** (или Ctrl+Enter)

### 1.3. Проверь результат

Должны появиться сообщения:
```
✅ Часть 1: RLS политики обновлены
✅ Часть 2: Функции PostgreSQL обновлены
✅ ВСЁ РАБОТАЕТ!
```

Если видишь `❌ Пользователь не найден` - проверь email в строке 224.

---

## 🔑 ШАГ 2: Проверь переменные в Vercel (5 минут)

### 2.1. Открой Vercel Dashboard

1. Перейди на https://vercel.com/dashboard
2. Выбери проект **trendxl-2-0**
3. Открой **Settings** → **Environment Variables**

### 2.2. Найди SUPABASE_SERVICE_KEY

**Критически важно:** Должна быть переменная **`SUPABASE_SERVICE_KEY`**

#### ❌ Если её НЕТ:

1. Вернись в **Supabase Dashboard**
2. Открой **Settings** → **API**
3. Найди секцию **Project API keys**
4. Скопируй **`service_role` (secret)** ключ ⚠️ НЕ anon key!
5. Вернись в Vercel → Add Environment Variable:
   - **Name:** `SUPABASE_SERVICE_KEY`
   - **Value:** (вставь скопированный ключ)
   - **Environment:** Production, Preview, Development (все 3!)
6. Сохрани

#### ✅ Если она ЕСТЬ:

1. Проверь что ключ длинный (~250+ символов)
2. Проверь что начинается с `eyJ...`
3. Если короткий - это ANON key, замени на SERVICE_KEY (см. выше)

### 2.3. Проверь другие переменные

Должны быть:
- ✅ `SUPABASE_URL` - https://xxx.supabase.co
- ✅ `SUPABASE_KEY` - anon public key
- ✅ `SUPABASE_SERVICE_KEY` - service role key (secret)
- ✅ `JWT_SECRET`
- ✅ `STRIPE_API_KEY`

---

## 🚀 ШАГ 3: Передеплой на Vercel (3 минуты)

### 3.1. Если ты ИЗМЕНИЛ переменные в Vercel:

```bash
# В терминале проекта
git add -A
git commit -m "fix: update environment variables"
git push origin main
```

### 3.2. Или форсируй редеплой:

1. В Vercel Dashboard → Deployments
2. Найди последний деплой
3. Нажми "..." → **Redeploy**
4. Подожди 2-3 минуты пока завершится

---

## 🧪 ШАГ 4: ТЕСТ (5 минут)

### 4.1. Ручной тест в Supabase

Открой **Supabase SQL Editor** и выполни:

```sql
-- Получи свой UUID
SELECT id, email FROM auth.users WHERE email LIKE '%твой_email%';

-- Замени UUID_СЮДА на свой UUID и выполни:
SELECT * FROM public.get_free_trial_info('UUID_СЮДА');

-- Должно вернуть:
-- can_use_today: true (или false если уже использовал)
-- today_count: 0 (или 1)
-- daily_limit: 1
-- message: "You have 1 free analysis available today"
```

### 4.2. Тест на сайте

1. Открой свой сайт (Vercel URL)
2. Войди в аккаунт
3. **Проверь счетчик** - должен показать `1/1 Free Today` (фиолетовый)
4. Введи ссылку на TikTok профиль
5. Запусти анализ
6. **После анализа** счетчик должен стать `0/1 Used Today` (оранжевый)
7. Попробуй ввести еще раз → должна появиться кнопка **Subscribe**

### 4.3. Проверь таблицу

В Supabase SQL Editor:

```sql
SELECT * FROM public.daily_free_analyses 
ORDER BY created_at DESC 
LIMIT 5;
```

Должна появиться запись с:
- `user_id` = твой UUID
- `analysis_date` = сегодняшняя дата
- `analysis_count` = 1
- `profile_analyzed` = имя профиля

---

## 🐛 TROUBLESHOOTING

### Проблема 1: "Function does not exist"

**Решение:**
1. Вернись к ШАГ 1
2. Убедись что ВСЕ 3 части скрипта выполнены
3. Проверь в SQL Editor:
   ```sql
   SELECT routine_name FROM information_schema.routines 
   WHERE routine_name IN ('can_use_free_trial', 'record_free_trial_usage', 'get_free_trial_info');
   ```
   Должны появиться все 3 функции

### Проблема 2: "RLS policy violation"

**Решение:**
1. Проверь что `SUPABASE_SERVICE_KEY` установлен в Vercel
2. Проверь логи Vercel - должно быть:
   ```
   ✅ Supabase client initialized (using SERVICE_KEY)
   ```
3. Если показывает `using ANON_KEY` → не установлен SERVICE_KEY

### Проблема 3: Таблица пустая после анализа

**Решение:**
1. Открой Vercel → Logs
2. Сделай анализ на сайте
3. Ищи в логах:
   - `🎯 Attempting to record free trial` ✅ функция вызывается
   - `❌ Failed to record free trial` ❌ есть ошибка
4. Если ошибка - проверь текст ошибки и примени исправление

### Проблема 4: Счетчик показывает неправильно

**Решение:**
1. Очисти кэш браузера (Ctrl+Shift+Delete)
2. Перезагрузи страницу
3. Выйди и войди заново
4. Проверь что бекенд вернул правильные данные:
   - Открой Developer Tools (F12)
   - Вкладка Network
   - Сделай действие
   - Найди запрос `/api/v1/free-trial/info`
   - Проверь Response

---

## ✅ КОНТРОЛЬНЫЙ СПИСОК

Перед тем как говорить "не работает", убедись:

- [ ] ✅ SQL скрипт выполнен БЕЗ ошибок в Supabase
- [ ] ✅ `SUPABASE_SERVICE_KEY` установлен в Vercel
- [ ] ✅ Vercel завершил деплой (зеленая галочка)
- [ ] ✅ Таблица `daily_free_analyses` существует
- [ ] ✅ Функции созданы (3 штуки)
- [ ] ✅ RLS политики созданы (4 штуки)
- [ ] ✅ Ручной тест в SQL Editor работает
- [ ] ✅ Логи Vercel показывают "using SERVICE_KEY"
- [ ] ✅ Кэш браузера очищен

---

## 📊 ОЖИДАЕМОЕ ПОВЕДЕНИЕ

### Новый пользователь (день 1):
1. Видит: `1/1 Free Today` (фиолетовый блок)
2. Делает анализ → успешно
3. Видит: `0/1 Used Today, Resets in 12h 30m` (оранжевый блок)
4. Пытается сделать еще → показывается **Subscribe Now**

### Тот же пользователь (день 2):
1. Видит: `1/1 Free Today` (фиолетовый блок)
2. Счетчик сбросился автоматически в 00:00 UTC

### Пользователь с подпиской:
1. Видит: `✨ Premium Active - Unlimited Scans` (зеленый блок)
2. Может делать бесконечно анализов
3. Счетчик не показывается

---

## 🆘 ЕСЛИ НИЧЕГО НЕ ПОМОГЛО

Напиши мне:
1. **Скриншот** Vercel Environment Variables (закрой секретные ключи!)
2. **Скриншот** результата SQL в Supabase:
   ```sql
   SELECT * FROM public.daily_free_analyses LIMIT 5;
   SELECT routine_name FROM information_schema.routines 
   WHERE routine_name LIKE '%free%';
   ```
3. **Лог из Vercel** после попытки анализа (Functions → Logs)
4. **Скриншот** Developer Tools → Network → `/api/v1/analyze` (Response)

---

**Время исправления:** 20-30 минут  
**Дата:** 6 октября 2025  
**Приоритет:** 🔴 CRITICAL

