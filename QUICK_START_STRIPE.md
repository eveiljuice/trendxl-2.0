# 🚀 Quick Start - Stripe Subscription

## ✅ Что уже готово:

- ✅ Stripe продукт "TrendXL Pro" создан
- ✅ Цена $29/месяц настроена
- ✅ Backend код интегрирован
- ✅ Frontend с My Profile готов
- ✅ .env файл обновлен
- ✅ Все зависимости установлены

## ⚡ Осталось 2 шага:

### Шаг 1: Применить SQL миграцию (1 минута)

Откройте: https://supabase.com/dashboard/project/jynidxwtbjrxmsbfpqra/sql/new

Вставьте и выполните:

```sql
ALTER TABLE profiles
ADD COLUMN IF NOT EXISTS stripe_customer_id TEXT,
ADD COLUMN IF NOT EXISTS stripe_subscription_id TEXT,
ADD COLUMN IF NOT EXISTS stripe_subscription_status TEXT,
ADD COLUMN IF NOT EXISTS subscription_start_date TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS subscription_end_date TIMESTAMPTZ;

CREATE INDEX IF NOT EXISTS idx_profiles_stripe_customer_id ON profiles(stripe_customer_id);
CREATE INDEX IF NOT EXISTS idx_profiles_stripe_subscription_id ON profiles(stripe_subscription_id);
```

### Шаг 2: Запустить и протестировать

```bash
npm run dev:full
```

Затем:

1. Откройте http://localhost:5173
2. Зарегистрируйте нового пользователя
3. Кликните на аватар → "My Profile"
4. Нажмите "Subscribe Now - $29/month"
5. Используйте карту: `4242 4242 4242 4242`
6. Готово! 🎉

---

## 📦 Созданные Stripe объекты:

- **Product ID**: `prod_TA3stomDrols97`
- **Price ID**: `price_1SDjkdGfnGEnyXLEIIX4TIUc` (уже в .env)
- **Payment Link**: https://buy.stripe.com/test_28EeVd998c3w4DzdlKefC00

## 🎯 Тестовые карты:

| Номер карты           | Результат    |
| --------------------- | ------------ |
| `4242 4242 4242 4242` | Успех ✅     |
| `4000 0000 0000 9995` | Отклонена ❌ |
| `4000 0025 0000 3155` | 3D Secure 🔐 |

## 🔗 Ссылки:

- [Stripe Dashboard](https://dashboard.stripe.com/test/dashboard)
- [Supabase SQL Editor](https://supabase.com/dashboard/project/jynidxwtbjrxmsbfpqra/sql/new)
- Payment Link: https://buy.stripe.com/test_28EeVd998c3w4DzdlKefC00

---

**Все настроено через Stripe MCP! Просто примените миграцию и начните тестировать.**

