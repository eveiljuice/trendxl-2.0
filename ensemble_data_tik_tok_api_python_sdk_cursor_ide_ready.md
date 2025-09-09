# EnsembleData TikTok API — Python SDK (Cursor IDE Ready)

> Готовая документация в формате Markdown для Cursor IDE по TikTok-эндпоинтам EnsembleData на Python. Содержит установку, инициализацию клиента, примеры кода, обработку пагинации/ошибок и обзор возвращаемых данных. Все примеры используют официальный SDK `ensembledata`.

---

## 1) Установка и быстрый старт

```bash
pip install ensembledata
```

```python
from ensembledata.api import EDClient

client = EDClient("API_TOKEN")  # храните токен в переменных окружения!

# Пробный вызов — инфо о пользователе по username
res = client.tiktok.user_info_from_username(username="zachking")
print(res.data.keys())           # dict с полезной нагрузкой
print(res.units_charged)         # биллинговые юниты за запрос
```

**Структура ответа SDK**:

- `res.data` — словарь (JSON) с данными эндпоинта.
- `res.units_charged` — количество списанных юнитов.
- Поля пагинации: `nextCursor`, иногда `nextPageToken` (если доступны для эндпоинта).

**Совет по токену**: `API_TOKEN` лучше прокидывать через переменные окружения и не коммитить в репозиторий.

---

## 2) Ошибки и таймауты

```python
from ensembledata.api import EDClient, EDError

client = EDClient("API_TOKEN")
try:
    res = client.tiktok.user_info_from_username(username="daviddobrik")
except EDError as e:
    # Обрабатывайте коды/типы ошибок по e / e.args
    print("API error:", e)
```

Если какого‑то метода/параметра нет в SDK, используйте низкоуровневый вызов:

```python
res = client.request("/tt/hashtag/posts", params={"name": "magic", "cursor": 0})
```

А для дополнительных параметров — `extra_params` там, где метод уже есть:

```python
res = client.tiktok.keyword_search(keyword="tesla", period="180", extra_params={"country": "US"})
```

---

## 3) Пагинация (cursor, page\_token) — паттерн

```python
def iter_cursor(fetch, *, max_loops=100):
    cursor = None
    loops = 0
    while loops < max_loops:
        res = fetch(cursor)
        data = res.data
        yield data
        cursor = data.get("nextCursor") if isinstance(data, dict) else None
        if not cursor:
            break
        loops += 1

# Пример использования с Keyword Search
for chunk in iter_cursor(lambda c: client.tiktok.keyword_search(keyword="tesla", cursor=c)):
    posts = chunk["data"]
    ...
```

---

## 4) Эндпоинты TikTok (Python SDK)

Ниже — сигнатуры и минимальные примеры. Параметры в snake\_case, как в SDK.

### 4.1 Пользователи (User Info)

**По username**

```python
res = client.tiktok.user_info_from_username(username="daviddobrik")
user = res.data["user"]
stats = res.data["stats"]
```

**По secuid**

```python
res = client.tiktok.user_info_from_secuid(sec_uid="MS4wLjABAAA...")
user = res.data["user"]  # поля могут отличаться от user_info_from_username
```

> Где взять `secUid`? В ответах других эндпоинтов (автор поста, post info и т. п.).

---

### 4.2 Подписчики и подписки (Followers / Followings)

**Последние 5000 подписчиков пользователя**

```python
res = client.tiktok.user_followers(
    id="6784819479778378757",        # user id
    sec_uid="MS4wLjABAAAAQ45..."      # secondary user id
)
followers = res.data["followers"]
next_cursor = res.data.get("nextCursor")
```

**Кого пользователь читает (followings)**

```python
res = client.tiktok.user_followings(
    id="6784819479778378757",
    sec_uid="MS4wLjABAAAAQ45..."
)
followings = res.data["followings"]
next_cursor = res.data.get("nextCursor")
next_page_token = res.data.get("nextPageToken")

# Следующие страницы
if next_cursor and next_page_token:
    res = client.tiktok.user_followings(
        id="6784819479778378757",
        sec_uid="MS4wLjABAAAAQ45...",
        cursor=next_cursor,
        page_token=next_page_token,
    )
```

---

### 4.3 Посты пользователя (User Posts / Liked Posts)

> **Внимание:** методы для постов пользователя находятся на верхнем уровне клиента.

**Посты по username**

```python
res = client.tiktok_user_posts_from_username(
    username="zachking",
    depth=1,                    # 1 блок = 10 постов
)
posts = res.data["data"]
next_cursor = res.data.get("nextCursor")

# Получить следующую порцию с учётом курсора
if next_cursor is not None:
    res = client.tiktok_user_posts_from_username(
        username="zachking",
        depth=1,
        cursor=next_cursor,
    )
```

Поддерживает также:

- `oldest_createtime=<unix_ts>` — остановиться на постах старше указанной даты (нужно фильтровать на своей стороне хвост последнего чанка).
- `alternative_method=True` — альтернативный способ сбора (может давать доп. поля, напр. `cla_info`).

**Посты по secuid**

```python
res = client.tiktok_user_posts_from_secuid(
    sec_uid="MS4wLjABAAAA...",
    depth=1,
)
```

**Понравившиеся посты пользователя (если публичны)**

```python
res = client.tiktok_user_liked_posts(sec_uid="MS4wLjABAAAA...")
liked = res.data["liked_posts"]
next_cursor = res.data.get("nextCursor")
```

---

### 4.4 Поиск пользователей (User Search)

```python
res = client.tiktok.user_search(keyword="tesla")
users = res.data["users"]
next_cursor = res.data.get("nextCursor")

# Следующая страница
if next_cursor:
    res = client.tiktok.user_search(keyword="tesla", cursor=next_cursor)
```

---

### 4.5 Информация о постах (Post Info / Multi Post Info)

**Post Info по URL**

```python
res = client.tiktok.post_info(url="https://www.tiktok.com/@user/video/7286900345836424479")
post = res.data[0]
```

**Multi Post Info по списку aweme\_ids (до 100 за раз)**

```python
res = client.tiktok.multi_post_info(aweme_ids=[
    "6950314200000000000",
    "6950314200000000001",
    "6950314200000000002",
])
posts = res.data
```

---

### 4.6 Комментарии и ответы (Comments / Replies)

**Комментарии к посту**

```python
res = client.tiktok.post_comments(aweme_id="7411198650782731563")
comments = res.data["comments"]
next_cursor = res.data.get("nextCursor")

# Дочитать остальные страницы
while next_cursor is not None:
    res = client.tiktok.post_comments(aweme_id="7411198650782731563", cursor=next_cursor)
    comments += res.data["comments"]
    next_cursor = res.data.get("nextCursor")
```

**Ответы на конкретный комментарий**

```python
res = client.tiktok.post_comment_replies(
    aweme_id="7411198650782731563",
    comment_id="7411205662439736097",
)
replies = res.data["comments"]
```

---

### 4.7 Мониторинг хэштегов (Hashtag Search / Full Hashtag Search)

**Частичный поиск по хэштегу (курсорная пагинация)**

```python
res = client.tiktok.hashtag_search(hashtag="magic", cursor=0)
posts = res.data["data"]
next_cursor = res.data.get("nextCursor")
```

**Полный обход хэштега (автокурсор)**

```python
# Можно ограничивать глубину и давность
res = client.tiktok.full_hashtag_search(
    hashtag="magic",
    max_cursor=2_000,  # необязательный лимит курсора
    days=30            # фильтр по давности
)
all_posts = res.data["data"]
```

> `Full Hashtag Search` может выполняться долго — поднимайте таймауты, если идёте напрямую HTTP.

---

### 4.8 Мониторинг ключевых слов (Keyword Search / Full Keyword Search)

**Keyword Search**

```python
res = client.tiktok.keyword_search(
    keyword="tesla",
    period="180",      # 0, 1, 7, 30, 90, 180 (дней)
    # необязательные параметры:
    # country="US",     # ISO 3166-1 alpha-2
    # sorting="1",      # 0 — релевантность, 1 — по лайкам
)
posts = res.data["data"]
next_cursor = res.data.get("nextCursor")
```

**Full Keyword Search (автокурсор)**

```python
res = client.tiktok.full_keyword_search(keyword="tesla", period="180")
all_posts = res.data["data"]
```

> `Full Keyword Search` тоже может выполняться долго (много внутренних запросов).

---

### 4.9 Музыка (Music Search / Music Posts / Music Details)

**Поиск музыки по ключевому слову**

```python
res = client.tiktok.music_search(
    keyword="classical",
    sorting="0",     # 0 relevance, 1 most used, 2 most recent, 3 shortest, 4 longest
    filter_by="0",   # 0 все, 1 только музыка, 2 только авторы/креаторы музыки
)
music = res.data["music"]
next_cursor = res.data.get("nextCursor")
```

**Посты по музыке (music\_id)**

```python
res = client.tiktok.music_posts(music_id="7063948643480488709")
posts = res.data["aweme_list"]
next_cursor = res.data.get("nextCursor")
```

**Детали музыки**

```python
res = client.tiktok.music_details(music_id="7063948643480488709")
usage_count = res.data["user_count"]
```

---

## 5) Полезные заметки и best‑practices

- **Pinned-посты**: в выдаче User Posts они идут первыми — фильтруйте `post["is_top"]` при анализе новизны.
- **Дата/время**: многие методы возвращают timestamps в Unix — приводите к TZ и фильтруйте после последнего чанка.
- **Страны и сортировка** в Keyword Search могут влиять на состав выдачи, но не гарантируют 100% фильтра по стране.
- **Лайкнутые посты** часто приватны — будьте готовы к пустой/ограниченной выдаче.
- **Биллинг**: следите за `res.units_charged` и суммарным количеством внутренних запросов (особенно в Full‑поисках).
- **Устойчивость**: оборачивайте запросы в retry с backoff, особенно при длинных Full‑обходах.

---

## 6) Частые рецепты (copy‑paste)

**A. Собрать все посты по хэштегу за последние N дней (с ограничением глубины)**

```python
from ensembledata.api import EDClient
client = EDClient("API_TOKEN")

res = client.tiktok.full_hashtag_search(
    hashtag="magic",
    days=30,
    max_cursor=2_000,
)
posts = res.data["data"]
```

**B. Пройтись по всем страницам Keyword Search вручную**

```python
posts = []
cursor = None
while True:
    res = client.tiktok.keyword_search(keyword="tesla", period="180", cursor=cursor)
    posts.extend(res.data["data"])  # добавляем текущую порцию
    cursor = res.data.get("nextCursor")
    if cursor is None:
        break
```

**C. Получить 50 постов пользователя, минуя pinned**

```python
res = client.tiktok_user_posts_from_username(username="zachking", depth=5)
posts = [p for p in res.data["data"] if not p.get("is_top")]  # depth=5 -> ~50 постов
```

**D. Комментарии и все ответы к первому комменту**

```python
post_id = "7411198650782731563"
comments = client.tiktok.post_comments(aweme_id=post_id).data["comments"]
if comments:
    first = comments[0]
    replies = client.tiktok.post_comment_replies(
        aweme_id=post_id, comment_id=first["cid"]
    ).data["comments"]
```

---

## 7) Отладка и инспекция ответов

```python
import json

res = client.tiktok.post_info(url="https://www.tiktok.com/@user/video/7286900345836424479")
print(json.dumps(res.data, ensure_ascii=False, indent=2))
```

Если нужен отсутствующий параметр:

```python
res = client.tiktok.keyword_search(
    keyword="tesla", period="180", extra_params={"country": "US"}
)
```

---

## 8) Чек‑лист интегратора

-

---

### Готово

Этого достаточно, чтобы в Cursor IDE сразу подключить `ensembledata` и собрать TikTok‑потоки: пользователи, посты, комменты, хэштеги/ключевые слова и музыка.

