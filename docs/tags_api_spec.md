# Спецификация API для тегов товаров (Product Tags)

## Обзор

Данный документ описывает новые API методы для управления тегами товаров. Теги позволяют добавлять метки к товарам (например, "популярный", "новинка", "распродажа" и т.д.).

### Структура данных

#### Tag (Тег)

| Поле | Тип | Описание |
|------|-----|----------|
| `tag_id` | integer | Уникальный идентификатор тега |
| `name` | string | Название тега (уникальное, макс. 100 символов) |
| `description` | string \| null | Описание тега (макс. 500 символов) |

#### ProductTag (Связь товара с тегом)

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | integer | Уникальный идентификатор связи |
| `product_id` | integer | ID товара |
| `tag_id` | integer | ID тега |
| `tag` | Tag | Объект тега (вложенный) |

---

## API методы

### 1. Создать тег

Создаёт новый тег в системе.

**Endpoint:** `POST /product/tags`

**Request Body:**
```json
{
  "name": "популярный",
  "description": "Популярные товары"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "tag_id": 1,
    "name": "популярный",
    "description": "Популярные товары"
  }
}
```

**Ошибки:**
- `409 Conflict` — тег с таким именем уже существует
- `422 Unprocessable Entity` — невалидные входные данные

---

### 2. Получить все теги

Возвращает список всех тегов с пагинацией.

**Endpoint:** `GET /product/tags`

**Query Parameters:**

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `limit` | integer | 100 | Количество записей (макс. 1000) |
| `offset` | integer | 0 | Смещение для пагинации |

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "total": 5,
    "items": [
      {
        "tag_id": 1,
        "name": "популярный",
        "description": "Популярные товары"
      },
      {
        "tag_id": 2,
        "name": "новинка",
        "description": "Новые поступления"
      }
    ]
  }
}
```

---

### 3. Получить тег по ID

Возвращает информацию о конкретном теге.

**Endpoint:** `GET /product/tags/{tag_id}`

**Path Parameters:**

| Параметр | Тип | Описание |
|----------|-----|----------|
| `tag_id` | integer | ID тега |

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "tag_id": 1,
    "name": "популярный",
    "description": "Популярные товары"
  }
}
```

**Ошибки:**
- `404 Not Found` — тег не найден

---

### 4. Обновить тег

Обновляет данные существующего тега.

**Endpoint:** `PUT /product/tags/{tag_id}`

**Path Parameters:**

| Параметр | Тип | Описание |
|----------|-----|----------|
| `tag_id` | integer | ID тега |

**Request Body:**
```json
{
  "name": "хит продаж",
  "description": "Самые продаваемые товары"
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "tag_id": 1,
    "name": "хит продаж",
    "description": "Самые продаваемые товары"
  }
}
```

**Ошибки:**
- `404 Not Found` — тег не найден
- `409 Conflict` — новое имя тега уже занято другим тегом

---

### 5. Удалить тег

Удаляет тег из системы. Все связи товаров с этим тегом также будут удалены (CASCADE).

**Endpoint:** `DELETE /product/tags/{tag_id}`

**Path Parameters:**

| Параметр | Тип | Описание |
|----------|-----|----------|
| `tag_id` | integer | ID тега |

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Тег удален"
}
```

**Ошибки:**
- `404 Not Found` — тег не найден

---

### 6. Добавить тег к товару

Создаёт связь между товаром и тегом.

**Endpoint:** `POST /product/tags/product-tags`

**Request Body:**
```json
{
  "product_id": 123,
  "tag_id": 1
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "product_id": 123,
    "tag_id": 1,
    "tag": {
      "tag_id": 1,
      "name": "популярный",
      "description": "Популярные товары"
    }
  }
}
```

**Ошибки:**
- `400 Bad Request` — связь уже существует
- `404 Not Found` — товар или тег не найдены

---

### 7. Удалить тег у товара

Удаляет связь между товаром и тегом.

**Endpoint:** `DELETE /product/tags/product-tags/{product_id}/{tag_id}`

**Path Parameters:**

| Параметр | Тип | Описание |
|----------|-----|----------|
| `product_id` | integer | ID товара |
| `tag_id` | integer | ID тега |

**Response (200 OK):**
```json
{
  "status": "success",
  "message": "Тег удален из товара"
}
```

**Ошибки:**
- `404 Not Found` — связь не найдена

---

### 8. Получить все теги товара

Возвращает все теги, связанные с конкретным товаром.

**Endpoint:** `GET /product/tags/product-tags/{product_id}`

**Path Parameters:**

| Параметр | Тип | Описание |
|----------|-----|----------|
| `product_id` | integer | ID товара |

**Query Parameters:**

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `limit` | integer | 100 | Количество записей |
| `offset` | integer | 0 | Смещение для пагинации |

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "total": 2,
    "items": [
      {
        "id": 1,
        "product_id": 123,
        "tag_id": 1,
        "tag": {
          "tag_id": 1,
          "name": "популярный",
          "description": "Популярные товары"
        }
      },
      {
        "id": 2,
        "product_id": 123,
        "tag_id": 2,
        "tag": {
          "tag_id": 2,
          "name": "новинка",
          "description": "Новые поступления"
        }
      }
    ]
  }
}
```

---

## Изменения в существующих API

### Получение товара (GET /product/{product_id})

В ответ при получении товара теперь дополнительно включается поле `tags`:

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "id": 123,
    "name": "iPhone 15 Pro",
    "description": "Смартфон Apple iPhone 15 Pro 256GB",
    "price": 99999.00,
    "images": [...],
    "attributes": [...],
    "tags": [
      {
        "tag_id": 1,
        "name": "популярный",
        "description": "Популярные товары"
      },
      {
        "tag_id": 3,
        "name": "премиум",
        "description": "Премиальные товары"
      }
    ],
    "category": {...},
    "supplier": {...}
  }
}
```

### Список товаров (GET /product)

В ответе при получении списка товаров каждый элемент также содержит поле `tags`:

```json
{
  "status": "success",
  "data": {
    "total": 100,
    "items": [
      {
        "id": 123,
        "name": "iPhone 15 Pro",
        "price": 99999.00,
        "tags": [
          {"tag_id": 1, "name": "популярный", "description": null}
        ],
        "images": [...],
        "attributes": [...]
      }
    ]
  }
}
```

---

## Примеры использования

### 1. Создание тегов и привязка к товару

```bash
# Создаём теги
curl -X POST http://localhost:8001/product/tags \
  -H "Content-Type: application/json" \
  -d '{"name": "популярный", "description": "Популярные товары"}'

curl -X POST http://localhost:8001/product/tags \
  -H "Content-Type: application/json" \
  -d '{"name": "новинка"}'

# Привязываем теги к товару
curl -X POST http://localhost:8001/product/tags/product-tags \
  -H "Content-Type: application/json" \
  -d '{"product_id": 123, "tag_id": 1}'

curl -X POST http://localhost:8001/product/tags/product-tags \
  -H "Content-Type: application/json" \
  -d '{"product_id": 123, "tag_id": 2}'
```

### 2. Получение товара с тегами

```bash
curl http://localhost:8001/product/123
```

Ответ будет содержать массив тегов:
```json
{
  "tags": [
    {"tag_id": 1, "name": "популярный", "description": "Популярные товары"},
    {"tag_id": 2, "name": "новинка", "description": null}
  ]
}
```

### 3. Получение всех тегов товара

```bash
curl http://localhost:8001/product/tags/product-tags/123
```

---

## Ограничения и валидация

| Правило | Описание |
|---------|----------|
| Уникальность имени тега | Поле `name` должно быть уникальным (регистрозависимое) |
| Длина имени тега | Максимум 100 символов |
| Длина описания тега | Максимум 500 символов |
| Уникальность связи | Один тег может быть привязан к товару только один раз |
| Каскадное удаление | При удалении тега все его связи с товарами удаляются автоматически |
| Каскадное удаление | При удалении товара все его связи с тегами удаляются автоматически |

---

## Схема базы данных

### Таблица `tags`

| Колонка | Тип | Ограничения |
|---------|-----|-------------|
| `id` | BigInteger | PRIMARY KEY, AUTOINCREMENT |
| `name` | VARCHAR(100) | NOT NULL, UNIQUE |
| `description` | VARCHAR(500) | NULL |
| `created_at` | DateTime | NOT NULL |
| `updated_at` | DateTime | NOT NULL |

**Индексы:**
- `ix_tags_name` на `name` (UNIQUE)

### Таблица `product_tags`

| Колонка | Тип | Ограничения |
|---------|-----|-------------|
| `id` | BigInteger | PRIMARY KEY, AUTOINCREMENT |
| `product_id` | BigInteger | NOT NULL, FK → products.id (CASCADE DELETE) |
| `tag_id` | BigInteger | NOT NULL, FK → tags.id (CASCADE DELETE) |
| `created_at` | DateTime | NOT NULL |
| `updated_at` | DateTime | NOT NULL |

**Индексы:**
- `ix_product_tags_product_id` на `product_id`
- `ix_product_tags_tag_id` на `tag_id`

**Уникальные ограничения:**
- `uq_product_tags_unique` на `(product_id, tag_id)`

---

## Миграция

Для создания таблиц выполните:

```bash
alembic upgrade head
```

Миграция: `alembic/versions/1a2b3c4d5e6f_add_tags_and_product_tags.py`
