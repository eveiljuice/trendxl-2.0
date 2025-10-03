# ✅ Stripe Setup Complete

## 🎉 Что настроено:

### 📦 Product:
- **Name**: TrendXL Pro
- **ID**: `prod_TA3stomDrols97`
- **Description**: Unlimited trend analysis and AI insights - Monthly subscription

### 💰 Price:
- **Price ID**: `price_1SEAUHGfnGEnyXLEwLlxed1j`
- **Amount**: $49.00 USD / month
- **Type**: Recurring subscription
- **Mode**: Test mode (для тестирования)

### 🔧 Backend Configuration:
Обновлен файл `backend/.env`:
```
STRIPE_PRICE_ID=price_1SEAUHGfnGEnyXLEwLlxed1j
```

---

## ⚠️ ВАЖНО: Test Mode vs Live Mode

Сейчас используется **Test Mode** для безопасного тестирования.

### Для тестирования:
✅ Используйте тестовые карты Stripe:
- **Успешная оплата**: `4242 4242 4242 4242`
- **CVV**: любые 3 цифры
- **Дата**: любая будущая дата
- **ZIP**: любой

### Для реальных платежей (Live Mode):
1. Перейдите в Stripe Dashboard
2. Переключитесь на **Live Mode** (toggle в правом верхнем углу)
3. Создайте новый price для Live mode:
   ```
   - Product: TrendXL Pro
   - Amount: $49.00
   - Interval: Monthly
   ```
4. Обновите `STRIPE_PRICE_ID` в `backend/.env` на Live price ID
5. Проверьте что `STRIPE_API_KEY` начинается с `sk_live_`

---

## 🧪 Как протестировать:

1. Запустите backend:
   ```bash
   cd backend
   python main.py
   ```

2. Откройте приложение и попробуйте подписаться

3. Используйте тестовую карту: `4242 4242 4242 4242`

4. Проверьте в Stripe Dashboard → Payments что платеж прошел

---

## 📚 Полезные ссылки:

- **Stripe Dashboard**: https://dashboard.stripe.com/test/dashboard
- **Test Cards**: https://stripe.com/docs/testing#cards
- **Products**: https://dashboard.stripe.com/test/products
- **Prices**: https://dashboard.stripe.com/test/prices
- **Webhooks**: https://dashboard.stripe.com/test/webhooks

---

## 🔄 Переключение на Live Mode:

Когда будете готовы принимать реальные платежи:

1. В Stripe Dashboard переключитесь на **Live Mode**
2. Создайте Live version продукта и цены
3. Обновите в `backend/.env`:
   - `STRIPE_API_KEY` на Live key (начинается с `sk_live_`)
   - `STRIPE_PRICE_ID` на Live price ID
   - `STRIPE_WEBHOOK_SECRET` на Live webhook secret

4. Настройте Live webhook:
   - URL: `https://your-domain.com/api/v1/webhooks/stripe`
   - Events: `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`

---

Теперь Stripe готов к работе! 🚀

