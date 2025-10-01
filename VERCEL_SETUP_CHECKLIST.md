# ✅ Vercel Setup Checklist

## Перед деплоем

- [ ] **Git репозиторий создан** и проект закоммичен
- [ ] **Vercel CLI установлен**: `npm install -g vercel`
- [ ] **Вход выполнен**: `vercel login`

## API ключи получены

- [ ] **Ensemble Data API Token** от https://dashboard.ensembledata.com/
- [ ] **OpenAI API Key** от https://platform.openai.com/api-keys
- [ ] **Perplexity API Key** от https://www.perplexity.ai/settings/api
- [ ] **JWT Secret Key** сгенерирован: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- [ ] **Redis URL** (опционально) от https://upstash.com/ или https://redis.com/

## Файлы конфигурации

- [x] `vercel.json` - конфигурация Vercel
- [x] `.vercelignore` - исключаемые файлы
- [x] `api/index.py` - serverless function entry point
- [x] `api/requirements.txt` - Python зависимости для API
- [x] `backend/vercel_adapter.py` - адаптер FastAPI → Vercel
- [x] `package.json` - обновлен с `vercel-build` скриптом
- [x] `backend/requirements.txt` - добавлен `mangum`

## Первый деплой

- [ ] **Выполнен первый деплой**: `vercel`
- [ ] **Получен deployment URL**: `https://your-project-name.vercel.app`

## Переменные окружения настроены

Через CLI:

```bash
vercel env add ENSEMBLE_API_TOKEN
vercel env add OPENAI_API_KEY
vercel env add PERPLEXITY_API_KEY
vercel env add JWT_SECRET_KEY
vercel env add REDIS_URL
```

Или через Dashboard:

- [ ] Settings → Environment Variables
- [ ] Добавлены все обязательные переменные
- [ ] Выбраны окружения: Production, Preview, Development

## Production деплой

- [ ] **Выполнен production деплой**: `vercel --prod`
- [ ] **Обновлен VITE_BACKEND_API_URL** в `vercel.json` с реальным URL

## Тестирование

- [ ] **Frontend открывается**: https://your-project-name.vercel.app
- [ ] **Health check работает**: https://your-project-name.vercel.app/health
  ```json
  {"status": "healthy", "services": {...}}
  ```
- [ ] **API status работает**: https://your-project-name.vercel.app/api/v1/status
- [ ] **Анализ профиля работает** (тест с реальным TikTok профилем)
- [ ] **Логи проверены**: `vercel logs` или через Dashboard

## CORS настроен

Если есть CORS ошибки:

- [ ] Добавлена переменная `CORS_ORIGINS`:
  ```bash
  vercel env add CORS_ORIGINS
  # Значение: ["https://your-project-name.vercel.app"]
  ```
- [ ] Переделоен проект: `vercel --prod`

## База данных (если нужна)

⚠️ **SQLite не работает на Vercel** (read-only filesystem)

Выберите альтернативу:

- [ ] **Vercel Postgres**: `vercel postgres create`
- [ ] **Supabase PostgreSQL**: https://supabase.com
- [ ] **PlanetScale MySQL**: https://planetscale.com
- [ ] Обновлен `backend/database.py` для использования выбранной БД
- [ ] Добавлена `DATABASE_URL` в переменные окружения

## Оптимизация

- [ ] **Vercel Analytics подключен**:
  ```bash
  npm install @vercel/analytics
  ```
  В `src/main.tsx`:
  ```typescript
  import { inject } from "@vercel/analytics";
  inject();
  ```
- [ ] **Мониторинг настроен**: Settings → Notifications
- [ ] **Custom domain подключен** (опционально): Settings → Domains

## Git Integration (рекомендуется)

- [ ] **Репозиторий подключен** через Vercel Dashboard
- [ ] **Автодеплой включен** для main/master ветки
- [ ] **Preview deployments включены** для pull requests

## Документация

- [ ] Прочитан `VERCEL_QUICKSTART.md`
- [ ] Прочитан `VERCEL_DEPLOYMENT_GUIDE.md`
- [ ] Команда ознакомлена с `.env.vercel.example`

## Финальная проверка

- [ ] ✅ Сайт работает корректно
- [ ] ✅ Все API эндпоинты отвечают
- [ ] ✅ Анализ профилей работает
- [ ] ✅ Логи не содержат критичных ошибок
- [ ] ✅ Performance приемлемый

---

## 🎉 Готово!

Если все пункты отмечены ✅, ваш проект успешно развернут на Vercel!

### Полезные команды:

```bash
# Просмотр логов
vercel logs

# Просмотр информации о проекте
vercel inspect

# Список deployments
vercel ls

# Открыть проект в браузере
vercel open

# Список переменных окружения
vercel env ls

# Production деплой
vercel --prod
```

---

## ⚠️ Известные ограничения

### Vercel Free Tier (Hobby):

- ⏱️ Function timeout: **10 секунд** (может быть недостаточно для анализа)
- 💾 Memory: 1024 MB
- 📦 Deployment size: 100 MB

### Vercel Pro ($20/мес):

- ⏱️ Function timeout: **60 секунд** (настроено в `vercel.json`)
- 💾 Memory: 3008 MB
- 📦 Deployment size: 500 MB

**Рекомендация**:

- Для полного функционала используйте **Vercel Pro**
- Или рассмотрите **Railway** (см. `RAILWAY_DEPLOYMENT.md`)

---

## 📞 Поддержка

- Vercel Docs: https://vercel.com/docs
- Vercel Support: https://vercel.com/support
- GitHub Issues: (ваш репозиторий)
