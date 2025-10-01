# PowerShell скрипт для деплоя TrendXL 2.0 на Vercel

Write-Host "🚀 TrendXL 2.0 - Vercel Deployment Script" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Проверка установки Vercel CLI
Write-Host "🔍 Проверка Vercel CLI..." -ForegroundColor Yellow

try {
    $vercelVersion = vercel --version 2>$null
    Write-Host "✅ Vercel CLI установлен (версия: $vercelVersion)" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Vercel CLI не установлен" -ForegroundColor Red
    Write-Host "Установка..." -ForegroundColor Yellow
    npm install -g vercel
}

Write-Host ""

# Проверка переменных окружения
Write-Host "🔐 Проверка переменных окружения..." -ForegroundColor Yellow
Write-Host ""

$envVarsNeeded = @()

if (-not $env:ENSEMBLE_API_TOKEN) {
    Write-Host "⚠️  ENSEMBLE_API_TOKEN не найден" -ForegroundColor Red
    Write-Host "   Получите токен: https://dashboard.ensembledata.com/" -ForegroundColor Gray
    $envVarsNeeded += "ENSEMBLE_API_TOKEN"
}

if (-not $env:OPENAI_API_KEY) {
    Write-Host "⚠️  OPENAI_API_KEY не найден" -ForegroundColor Red
    Write-Host "   Получите ключ: https://platform.openai.com/api-keys" -ForegroundColor Gray
    $envVarsNeeded += "OPENAI_API_KEY"
}

if (-not $env:PERPLEXITY_API_KEY) {
    Write-Host "⚠️  PERPLEXITY_API_KEY не найден" -ForegroundColor Red
    Write-Host "   Получите ключ: https://www.perplexity.ai/settings/api" -ForegroundColor Gray
    $envVarsNeeded += "PERPLEXITY_API_KEY"
}

if (-not $env:JWT_SECRET_KEY) {
    Write-Host "⚠️  JWT_SECRET_KEY не найден" -ForegroundColor Red
    Write-Host "   Сгенерируйте: python -c `"import secrets; print(secrets.token_urlsafe(32))`"" -ForegroundColor Gray
    $envVarsNeeded += "JWT_SECRET_KEY"
}

if ($envVarsNeeded.Count -gt 0) {
    Write-Host ""
    Write-Host "⚠️  Обнаружено $($envVarsNeeded.Count) отсутствующих переменных окружения" -ForegroundColor Yellow
    Write-Host "   Вы сможете добавить их после первого деплоя через:" -ForegroundColor Gray
    Write-Host "   vercel env add VARIABLE_NAME" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "📦 Начинаем деплой..." -ForegroundColor Yellow
Write-Host ""

# Деплой на Vercel
try {
    vercel --prod
    
    Write-Host ""
    Write-Host "✅ Деплой завершен!" -ForegroundColor Green
    Write-Host ""
    
    if ($envVarsNeeded.Count -gt 0) {
        Write-Host "📝 Следующие шаги:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "1. Настройте переменные окружения:" -ForegroundColor White
        foreach ($var in $envVarsNeeded) {
            Write-Host "   vercel env add $var" -ForegroundColor Cyan
        }
        Write-Host ""
        Write-Host "2. Переделойте проект:" -ForegroundColor White
        Write-Host "   vercel --prod" -ForegroundColor Cyan
        Write-Host ""
    }
    
    Write-Host "3. Проверьте работу:" -ForegroundColor White
    Write-Host "   https://your-project-name.vercel.app/health" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📚 Документация:" -ForegroundColor Yellow
    Write-Host "   - Быстрый старт: VERCEL_QUICKSTART.md" -ForegroundColor Gray
    Write-Host "   - Полное руководство: VERCEL_DEPLOYMENT_GUIDE.md" -ForegroundColor Gray
    Write-Host "   - Checklist: VERCEL_SETUP_CHECKLIST.md" -ForegroundColor Gray
    Write-Host ""
    
} catch {
    Write-Host ""
    Write-Host "❌ Ошибка при деплое: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "🔧 Попробуйте:" -ForegroundColor Yellow
    Write-Host "1. Выполните вход: vercel login" -ForegroundColor Cyan
    Write-Host "2. Повторите деплой: vercel --prod" -ForegroundColor Cyan
    Write-Host "3. Проверьте документацию: VERCEL_QUICKSTART.md" -ForegroundColor Cyan
    Write-Host ""
}

