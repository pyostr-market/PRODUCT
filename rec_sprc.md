# Спецификация API: Система рекомендаций товаров

**Версия:** 1.0  
**Дата:** 31 марта 2026 г.  
**Статус:** Реализовано

---
qwen --resume 6af05156-6ec9-4a8d-869c-6ce8981139af
## 1. Общие положения

Система рекомендаций товаров позволяет создавать связи между товарами различных типов и получать рекомендации для отображения в каталоге.

### 1.1 Типы связей

| Тип | Описание | Пример использования |
|-----|----------|---------------------|
| `accessory` | Аксессуары | Чехол для телефона, защитное стекло |
| `similar` | Похожие товары | Товары с аналогичными характеристиками |
| `bundle` | Комплект | Товары, продающиеся вместе |
| `upsell` | Более дорогая альтернатива | Товары премиум-сегмента |

### 1.2 Ограничения

- Связь товара с самим собой **не допускается**
- Комбинация `product_id + related_product_id + relation_type` должна быть **уникальной**
- Оба товара (product_id и related_product_id) должны существовать в системе

---

## 2. API Методы

### 2.1 Создание связи

**Метод:** `POST /product/product-relations`

**Права доступа:** Требуется permission `product:create`

#### Запрос

**Тело запроса (JSON):**

```json
{
  "product_id": 5,
  "related_product_id": 79,
  "relation_type": "accessory",
  "sort_order": 1
}
```

**Параметры:**

| Поле | Тип | Обязательное | Описание |
|------|-----|--------------|----------|
| `product_id` | integer | Да | ID основного товара |
| `related_product_id` | integer | Да | ID связанного товара |
| `relation_type` | string | Да | Тип связи (accessory, similar, bundle, upsell) |
| `sort_order` | integer | Нет | Порядок отображения (по умолчанию: 0) |

#### Ответ

**Успешный ответ (200 OK):**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "product_id": 5,
    "related_product_id": 79,
    "relation_type": "accessory",
    "sort_order": 1
  }
}
```

**Коды ошибок:**

| Код | Описание |
|-----|----------|
| 400 | Связь товара с самим собой / Один из товаров не существует |
| 401 | Неавторизованный запрос |
| 403 | Недостаточно прав |
| 409 | Связь уже существует |

---

### 2.2 Обновление связи

**Метод:** `PUT /product/product-relations/{id}`

**Права доступа:** Требуется permission `product:update`

#### Запрос

**Параметры пути:**

| Параметр | Тип | Описание |
|----------|-----|----------|
| `id` | integer | ID связи для обновления |

**Тело запроса (JSON):**

```json
{
  "relation_type": "accessory",
  "sort_order": 2
}
```

**Параметры:**

| Поле | Тип | Обязательное | Описание |
|------|-----|--------------|----------|
| `relation_type` | string | Нет | Новый тип связи |
| `sort_order` | integer | Нет | Новый порядок отображения |

#### Ответ

**Успешный ответ (200 OK):**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "product_id": 5,
    "related_product_id": 79,
    "relation_type": "accessory",
    "sort_order": 2
  }
}
```

**Коды ошибок:**

| Код | Описание |
|-----|----------|
| 401 | Неавторизованный запрос |
| 403 | Недостаточно прав |
| 404 | Связь не найдена |

---

### 2.3 Удаление связи

**Метод:** `DELETE /product/product-relations/{id}`

**Права доступа:** Требуется permission `product:delete`

#### Запрос

**Параметры пути:**

| Параметр | Тип | Описание |
|----------|-----|----------|
| `id` | integer | ID связи для удаления |

#### Ответ

**Успешный ответ (200 OK):**

```json
{
  "success": true,
  "data": {
    "deleted": true
  }
}
```

**Коды ошибок:**

| Код | Описание |
|-----|----------|
| 401 | Неавторизованный запрос |
| 403 | Недостаточно прав |
| 404 | Связь не найдена |

---

### 2.4 Получение списка связей товара

**Метод:** `GET /product/products/{product_id}/relations`

**Права доступа:** Публичный (не требует авторизации)

#### Запрос

**Параметры пути:**

| Параметр | Тип | Описание |
|----------|-----|----------|
| `product_id` | integer | ID товара |

**Query-параметры:**

| Параметр | Тип | Обязательное | Описание |
|----------|-----|--------------|----------|
| `relation_type` | string | Нет | Фильтр по типу связи |
| `page` | integer | Нет | Номер страницы (по умолчанию: 1) |
| `limit` | integer | Нет | Количество элементов (по умолчанию: 20, макс: 100) |

#### Ответ

**Успешный ответ (200 OK):**

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "relation_id": 1,
        "id": 79,
        "name": "Silicone Case",
        "price": 29.99,
        "description": "Защитный чехол",
        "relation_type": "accessory",
        "sort_order": 1,
        "images": [
          {
            "upload_id": 1,
            "image_url": "https://cdn.example.com/products/silicone-case.jpg",
            "is_main": true,
            "ordering": 0
          }
        ]
      },
      {
        "relation_id": 2,
        "id": 80,
        "name": "Screen Protector",
        "price": 9.99,
        "description": "Защитное стекло",
        "relation_type": "accessory",
        "sort_order": 2,
        "images": [
          {
            "upload_id": 2,
            "image_url": "https://cdn.example.com/products/screen-protector.jpg",
            "is_main": true,
            "ordering": 0
          }
        ]
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 45
    }
  }
}
```

**Структура элемента:**

| Поле | Тип | Описание |
|------|-----|----------|
| `relation_id` | integer | **ID связи** (используется для удаления) |
| `id` | integer | ID рекомендованного товара |
| `name` | string | Название товара |
| `price` | float | Цена товара |
| `description` | string | Описание товара (может быть null) |
| `relation_type` | string | Тип связи |
| `sort_order` | integer | Порядок сортировки |
| `images` | array | Список изображений товара |

**Структура изображения:**

| Поле | Тип | Описание |
|------|-----|----------|
| `upload_id` | integer | ID загруженного изображения |
| `image_url` | string | Публичный URL изображения |
| `is_main` | boolean | Флаг главного изображения |
| `ordering` | integer | Порядок сортировки изображений |

**Коды ошибок:**

| Код | Описание |
|-----|----------|
| 404 | Товар не найден |

---

### 2.5 Получение рекомендаций для товара

**Метод:** `GET /product/products/{product_id}/recommendations`

**Права доступа:** Публичный (не требует авторизации)

#### Запрос

**Параметры пути:**

| Параметр | Тип | Описание |
|----------|-----|----------|
| `product_id` | integer | ID товара |

**Query-параметры:**

| Параметр | Тип | Обязательное | Описание |
|----------|-----|--------------|----------|
| `relation_type` | string | Нет | Фильтр по типу рекомендации |
| `page` | integer | Нет | Номер страницы (по умолчанию: 1) |
| `limit` | integer | Нет | Количество элементов (по умолчанию: 20, макс: 100) |

#### Ответ

**Успешный ответ (200 OK):**

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "relation_id": 1,
        "id": 79,
        "name": "Silicone Case",
        "price": 29.99,
        "description": "Защитный чехол",
        "relation_type": "accessory",
        "sort_order": 1,
        "images": [
          {
            "upload_id": 1,
            "image_url": "https://cdn.example.com/products/silicone-case.jpg",
            "is_main": true,
            "ordering": 0
          }
        ]
      },
      {
        "relation_id": 2,
        "id": 80,
        "name": "Screen Protector",
        "price": 9.99,
        "description": "Защитное стекло",
        "relation_type": "similar",
        "sort_order": 2,
        "images": []
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 12
    }
  }
}
```

**Коды ошибок:**

| Код | Описание |
|-----|----------|
| 404 | Товар не найден |

---

## 3. Примеры использования

### 3.1 Создание аксессуаров для товара

```bash
# Создаём связь "аксессуар"
curl -X POST http://api.example.com/product/product-relations \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 5,
    "related_product_id": 79,
    "relation_type": "accessory",
    "sort_order": 1
  }'
```

### 3.2 Получение всех аксессуаров для товара

```bash
curl -X GET "http://api.example.com/product/products/5/relations?relation_type=accessory"
```

**Ответ:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "relation_id": 1,
        "id": 79,
        "name": "Silicone Case",
        "price": 29.99,
        "relation_type": "accessory",
        "sort_order": 1
      }
    ],
    "pagination": { ... }
  }
}
```

### 3.3 Удаление связи

```bash
# Используем relation_id из ответа GET /relations
curl -X DELETE http://api.example.com/product/product-relations/1 \
  -H "Authorization: Bearer <token>"
```

### 3.4 Получение похожих товаров

```bash
curl -X GET "http://api.example.com/product/products/5/recommendations?relation_type=similar&limit=10"
```

### 3.5 Обновление порядка отображения

```bash
curl -X PUT http://api.example.com/product/product-relations/1 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "sort_order": 10
  }'
```

---

## 4. Структура базы данных

### Таблица: `product_relations`

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | BIGINT | Первичный ключ |
| `product_id` | BIGINT | FK на products.id |
| `related_product_id` | BIGINT | FK на products.id |
| `relation_type` | VARCHAR(50) | Тип связи |
| `sort_order` | INTEGER | Порядок сортировки |
| `created_at` | TIMESTAMP | Дата создания |
| `updated_at` | TIMESTAMP | Дата обновления |

**Уникальные ограничения:**
- `UNIQUE (product_id, related_product_id, relation_type)`

**Индексы:**
- `IX product_relations_product_id`
- `IX product_relations_related_product_id`
- `IX product_relations_relation_type`

### Таблица: `product_relation_audit_logs`

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | BIGINT | Первичный ключ |
| `relation_id` | BIGINT | ID связи |
| `action` | VARCHAR(50) | Действие (create, update, delete) |
| `old_data` | TEXT | Старые данные (JSON) |
| `new_data` | TEXT | Новые данные (JSON) |
| `user_id` | BIGINT | ID пользователя |
| `fio` | VARCHAR(255) | ФИО пользователя |
| `created_at` | TIMESTAMP | Дата записи |

---

## 5. Сценарии использования

### 5.1 Блок «Аксессуары» в карточке товара

```
GET /product/products/{id}/recommendations?relation_type=accessory
```

### 5.2 Блок «Похожие товары»

```
GET /product/products/{id}/recommendations?relation_type=similar
```

### 5.3 Блок «С этим товаром покупают» (комплекты)

```
GET /product/products/{id}/recommendations?relation_type=bundle
```

### 5.4 Блок «Более дорогие альтернативы»

```
GET /product/products/{id}/recommendations?relation_type=upsell
```

---

## 6. Примечания

1. **Сортировка:** Результаты сортируются по `sort_order` (возрастание), затем по `id`.
2. **Пагинация:** Используется offset-пагинация с параметрами `page` и `limit`.
3. **Каскадное удаление:** При удалении товара все связанные связи удаляются автоматически.
4. **Audit-логирование:** Все операции создания, обновления и удаления записываются в `product_relation_audit_logs`.
