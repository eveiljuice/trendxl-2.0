#!/bin/bash
# Скрипт для деплоя TrendXL 2.0 на Vercel

echo "🚀 TrendXL 2.0 - Vercel Deployment Script"
echo "=========================================="
echo ""

# Проверка установки Vercel CLI
if ! command -v vercel &> /dev/null
then
    echo "⚠️  Vercel CLI не установлен"
    echo "Установка..."
    npm install -g vercel
fi

echo "✅ Vercel CLI установлен"
echo ""

# Проверка переменных окружения
echo "🔐 Проверка переменных окружения..."
echo ""

if [ -z "$ENSEMBLE_API_TOKEN" ]; then
    echo "⚠️  ENSEMBLE_API_TOKEN не найден"
    echo "Получите токен: https://dashboard.ensembledata.com/"
fi

if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY не найден"
    echo "Получите ключ: https://platform.openai.com/api-keys"
fi

if [ -z "$PERPLEXITY_API_KEY" ]; then
    echo "⚠️  PERPLEXITY_API_KEY не найден"
    echo "Получите ключ: https://www.perplexity.ai/settings/api"
fi

if [ -z "$JWT_SECRET_KEY" ]; then
    echo "⚠️  JWT_SECRET_KEY не найден"
    echo "Сгенерируйте: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
fi

echo ""
echo "📦 Начинаем деплой..."
echo ""

# Деплой на Vercel
vercel --prod

echo ""
echo "✅ Деплой завершен!"
echo ""
echo "📝 Следующие шаги:"
echo "1. Настройте переменные окружения: vercel env add VARIABLE_NAME"
echo "2. Переделойте проект: vercel --prod"
echo "3. Проверьте работу: https://your-project-name.vercel.app/health"
echo ""
echo "📚 Документация:"
echo "- Быстрый старт: VERCEL_QUICKSTART.md"
echo "- Полное руководство: VERCEL_DEPLOYMENT_GUIDE.md"
echo "- Checklist: VERCEL_SETUP_CHECKLIST.md"
echo ""

