# 🚀 Advanced Creative Center Discovery с AI-агентом

Эта расширенная архитектура реализует сложный AI-агент для поиска хэштегов в TikTok Creative Center с пошаговой навигацией и интеграцией с Ensemble Data.

## 🏗️ Архитектура системы

### Расширенная архитектура (новая):

1. **🌍 Определение географии пользователя**

   - Автоматическое определение из профиля или явное указание
   - Маппинг стран к кодам Creative Center

2. **📂 Маппинг ниши к категориям**

   - Интеллектуальный маппинг пользовательских ниш к категориям TikTok
   - Поддержка 17+ категорий Creative Center

3. **🤖 Пошаговая навигация AI-агента**

   - Заход на конкретную географию в Creative Center
   - Выбор релевантной индустрии для ниши пользователя
   - Анализ ~50 хэштегов в категории

4. **🎯 Интеллектуальная фильтрация**

   - Отбор топ-5 хэштегов по релевантности + метрикам
   - Взвешенная система оценки (релевантность + рост + производительность)

5. **📊 Интеграция с Ensemble Data**
   - Поиск трендовых видео для каждого отобранного хэштега
   - Качественная фильтрация и сортировка результатов
   - Анализ релевантности контента с GPT-4 Vision

### Упрощенная архитектура (legacy):

- Простой запрос к Perplexity для поиска хэштегов по нише

## 🔌 API Эндпоинты

### 1. Полный анализ Creative Center + Ensemble (рекомендуемый)

```http
POST /api/v1/analyze-creative-center
Content-Type: application/json

{
  "profile_url": "@username",
  "country": "US",
  "language": "en",
  "hashtag_limit": 5,
  "videos_per_hashtag": 3,
  "auto_detect_geo": true
}
```

**Ответ:**

```json
{
  "profile": {
    "username": "username",
    "niche_category": "Tech Reviews",
    "...": "..."
  },
  "creative_center_hashtags": [
    {
      "name": "techreview",
      "url": "https://ads.tiktok.com/business/creativecenter/...",
      "volume": 123456,
      "growth": 0.37,
      "score": 82.5,
      "relevance_score": 9.1
    }
  ],
  "trends": [
    {
      "id": "video123",
      "caption": "Latest tech review...",
      "views": 500000,
      "likes": 25000,
      "hashtag": "techreview",
      "relevance_score": 0.95
    }
  ],
  "analysis_summary": "Found 12 high-quality trending videos...",
  "metadata": {
    "creative_center_category": "Technology",
    "total_cc_hashtags_analyzed": 47,
    "navigation_successful": true,
    "analysis_method": "Creative Center + Ensemble Data integration"
  }
}
```

### 2. Только поиск хэштегов Creative Center

```http
POST /api/v1/creative-center/hashtags
Content-Type: application/json

{
  "niche": "Tech Reviews",
  "country": "US",
  "language": "en",
  "limit": 10,
  "auto_detect_geo": false,
  "profile_data": null
}
```

**Ответ:**

```json
{
  "niche": "Tech Reviews",
  "country": "US",
  "language": "en",
  "category": "Technology",
  "total_found": 47,
  "hashtags": [
    {
      "name": "techreview",
      "url": "https://ads.tiktok.com/business/creativecenter/...",
      "volume": 123456,
      "growth": 0.37,
      "score": 82.5
    }
  ]
}
```

## 💻 Frontend использование

### Полный анализ (рекомендуемый подход):

```typescript
import { analyzeCreativeCenterComplete } from "./services/backendApi";

// Полный анализ Creative Center + Ensemble с прогрессом
const result = await analyzeCreativeCenterComplete(
  "@username",
  "US",
  "en",
  5, // hashtag limit
  3, // videos per hashtag
  true, // auto detect geo
  (stage, message, percentage) => {
    console.log(`${stage}: ${message} (${percentage}%)`);
    // Обновить UI прогресс-бар
  }
);

console.log("Анализ завершен:", {
  profile: result.profile.username,
  hashtags: result.creative_center_hashtags.length,
  videos: result.trends.length,
  category: result.metadata.creative_center_category,
});
```

### Только поиск хэштегов:

```typescript
import { discoverCreativeCenterHashtags } from "./services/backendApi";

// Поиск с автоопределением географии
const profile = await getTikTokProfile("username");
const hashtagsResult = await discoverCreativeCenterHashtags(
  profile.niche_category || "Tech Reviews",
  "US",
  "en",
  10,
  true, // auto detect geo
  profile // profile data for geo detection
);

console.log("Creative Center хэштеги:", hashtagsResult.hashtags);
console.log("Использованная категория:", hashtagsResult.category);
console.log("Всего найдено:", hashtagsResult.total_found);
```

## Интеграция с анализом трендов

```typescript
// 1. Получаем профиль и его нишу
const profile = await getTikTokProfile("username");

// 2. Находим Creative Center хэштеги для ниши
const creativeCenterHashtags = await discoverCreativeCenterHashtags(
  profile.niche_category,
  "US",
  "en",
  10
);

// 3. Используем найденные хэштеги для поиска трендовых видео
const trendingVideos = await Promise.all(
  creativeCenterHashtags.hashtags.map((hashtag) =>
    searchHashtagPosts(hashtag.name, 5, 7, 1)
  )
);

console.log("Трендовые видео по Creative Center хэштегам:", trendingVideos);
```

## Параметры

- **niche**: Ниша контента (например: "Tech Reviews", "Fashion Style", "Food Recipes")
- **country**: Код страны для региональных трендов (US, GB, DE, etc.)
- **language**: Языковой код (en, de, fr, etc.)
- **limit**: Максимальное количество хэштегов (1-25)

## Примеры ниш

- "Tech Reviews" - технологические обзоры
- "Fashion Style" - мода и стиль
- "Food Recipes" - рецепты и кулинария
- "Fitness Training" - фитнес и тренировки
- "Comedy Skits" - комедийные скетчи
- "Beauty Tips" - советы по красоте
- "Travel Vlogs" - путешествия
- "Gaming Content" - игровой контент

## Требования

- ✅ **Perplexity API Key** в `backend/.env`
- ✅ **OpenAI API Key** для анализа профилей
- ✅ **Ensemble API Token** для TikTok данных

## Обработка ошибок

```typescript
try {
  const result = await discoverCreativeCenterHashtags("Tech Reviews");
  console.log("Успешно:", result.hashtags);
} catch (error) {
  if (error.message.includes("Perplexity API key")) {
    console.error("Не настроен API ключ Perplexity");
  } else if (error.message.includes("Creative Center discovery failed")) {
    console.error("Временная ошибка поиска, попробуйте позже");
  } else {
    console.error("Общая ошибка:", error.message);
  }
}
```

## Интеграция с UI

Рекомендуется добавить кнопку "Discover Creative Center Hashtags" в интерфейс анализа трендов, которая:

1. Использует нишу из анализа профиля
2. Показывает прогресс поиска (AI-агент может работать 30-60 секунд)
3. Отображает найденные хэштеги с метриками
4. Позволяет выбрать хэштеги для дальнейшего анализа трендов

---

_Эта функция значительно улучшает качество поиска релевантных хэштегов, используя актуальные данные TikTok Creative Center через AI-агента._
