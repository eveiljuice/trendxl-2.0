# 📸 Руководство по извлечению изображений из TikTok постов

## Обзор

В TrendXL 2.0 реализована комплексная система извлечения изображений из TikTok постов с использованием EnsembleData TikTok API. Система поддерживает как видео-посты (thumbnail изображения), так и image-посты (карусели изображений).

## 🔧 Backend изменения

### Модели данных

Обновлены модели в `backend/models.py`:

```python
class TikTokPost(BaseModel):
    # ... существующие поля ...
    cover_image_url: str = ""
    images: List[str] = Field(default_factory=list, description="Additional images from the post")

class TrendVideo(BaseModel):
    # ... существующие поля ...
    cover_image_url: str = ""
    images: List[str] = Field(default_factory=list, description="Additional images from the post")
```

### Сервис извлечения

В `backend/services/ensemble_service.py` реализована комплексная система извлечения:

#### 1. Извлечение основного изображения (cover_image_url)

```python
cover_image_url = (
    # Primary sources - high quality covers
    safe_get_nested(video_info, ['cover', 'url_list', 0]) or
    safe_get_nested(video_info, ['origin_cover', 'url_list', 0]) or
    # Dynamic covers - animated thumbnails
    safe_get_nested(video_info, ['dynamic_cover', 'url_list', 0]) or
    # AI-generated covers
    safe_get_nested(video_info, ['ai_cover', 'url_list', 0]) or
    # Fallbacks...
)
```

#### 2. Извлечение дополнительных изображений

```python
# Image posts (карусели)
image_post_info = safe_get_nested(post_data, ['image_post_info']) or {}
if image_post_info:
    images_data = safe_get_nested(image_post_info, ['images']) or []
    for img_data in images_data[:5]:
        img_url = safe_get_nested(img_data, ['image_url', 'url_list', 0])
        # ...

# Alternative video thumbnails
alt_covers = [
    safe_get_nested(video_info, ['cover', 'url_list', i]) for i in range(3, 6)
]
```

## 🎨 Frontend изменения

### TypeScript типы

Обновлены интерфейсы в `src/types/index.ts`:

```typescript
export interface TikTokPost {
  // ... существующие поля ...
  cover_image_url: string;
  images: string[]; // Дополнительные изображения
}

export interface TrendVideo {
  // ... существующие поля ...
  cover_image_url: string;
  images: string[]; // Дополнительные изображения
}
```

### Компоненты

#### TrendCard.tsx

Добавлена поддержка мультиизображений:

- **Навигационные точки**: Переключение между изображениями
- **Счетчик изображений**: Показывает текущее/общее количество
- **Автоматическое переключение**: При ошибке загрузки основного изображения

```tsx
// Навигационные точки
{
  hasMultipleImages && (
    <div className="absolute top-3 right-3 flex space-x-1">
      {allImages.map((_, index) => (
        <button onClick={(e) => handleImageChange(index, e)}>
          {/* ... */}
        </button>
      ))}
    </div>
  );
}

// Счетчик
{
  hasMultipleImages && (
    <div className="absolute top-3 left-3 bg-black/70 text-white text-xs px-2 py-1 rounded-full">
      {selectedImageIndex + 1}/{allImages.length}
    </div>
  );
}
```

#### VideoModal.tsx

Добавлена галерея дополнительных изображений:

```tsx
{
  /* Additional Images Gallery */
}
{
  trend.images && trend.images.length > 0 && (
    <div className="mt-3 flex space-x-2 overflow-x-auto pb-2">
      {trend.images.slice(0, 5).map((imageUrl, index) => (
        <img
          src={imageUrl}
          onClick={() => window.open(imageUrl, "_blank")}
          className="w-16 h-16 object-cover hover:scale-110 transition-transform cursor-pointer"
        />
      ))}
    </div>
  );
}
```

## 📊 Источники изображений

### 1. Видео-посты

- `video.cover.url_list[0-2]` - Основные обложки
- `video.origin_cover.url_list[0-2]` - Оригинальные обложки
- `video.dynamic_cover.url_list[0-1]` - Анимированные превью
- `video.ai_cover.url_list[0-1]` - AI-сгенерированные обложки

### 2. Image-посты (карусели)

- `image_post_info.images[].image_url.url_list[0]` - Основные изображения
- `image_post_info.images[].display_image.url_list[0]` - Отображаемые изображения
- `image_post_info.images[].thumbnail.url_list[0]` - Миниатюры

### 3. Дополнительные источники

- `video.cover_hd.url_list[0]` - HD обложки
- `video.cover_medium.url_list[0]` - Средние обложки
- `video.cover_thumb.url_list[0]` - Миниатюры

## 🔄 Fallback механизм

Система использует множественные fallback для обеспечения максимальной доступности изображений:

1. **Основное изображение**: 10+ источников с приоритетом качества
2. **URL валидация**: Проверка формата и протокола
3. **Ограничение длины**: URL обрезаются до 500 символов
4. **Дедупликация**: Удаление дублирующихся изображений

## 🧪 Тестирование

Запустите тест для проверки функциональности:

```bash
python test_image_extraction.py
```

Тест проверяет:

- ✅ Извлечение cover_image_url
- ✅ Извлечение дополнительных изображений
- ✅ Поддержку image-постов
- ✅ Валидацию URL
- ✅ Работу с хештег-поиском

## 📱 Пользовательский интерфейс

### Карточки видео

- Основное изображение отображается как превью
- Навигационные точки для переключения между изображениями
- Счетчик изображений в левом верхнем углу
- Плавные анимации переходов

### Модальное окно

- Основное изображение в полном размере
- Горизонтальная галерея дополнительных изображений
- Клик по изображению открывает в новой вкладке
- Индикатор количества изображений

## 🔧 Настройка

### Переменные окружения

```bash
ENSEMBLE_API_TOKEN=your_api_token_here
```

### Ограничения

- Максимум 5 дополнительных изображений на пост
- URL изображений ограничены 500 символами
- Таймаут загрузки изображений: 10 секунд

## 🚀 Развертывание

1. Убедитесь, что все зависимости установлены
2. Установите ENSEMBLE_API_TOKEN
3. Перезапустите backend сервис
4. Пересоберите frontend (если используете production build)

## 📈 Производительность

- Изображения загружаются асинхронно
- Используется lazy loading для дополнительных изображений
- Кэширование на уровне браузера
- Оптимизированные размеры превью

## 🐛 Устранение неполадок

### Изображения не загружаются

1. Проверьте CORS настройки
2. Убедитесь в валидности API токена
3. Проверьте сетевые ограничения

### Медленная загрузка

1. Проверьте скорость интернет-соединения
2. Убедитесь в доступности CDN TikTok
3. Рассмотрите использование прокси для изображений

---

_Документация обновлена: $(date)_
