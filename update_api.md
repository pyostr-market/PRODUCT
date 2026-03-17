# Изменения API: Перенос типа устройства с товара на категорию

## Обзор изменений

Тип устройства (device type) был перенесён с уровня товара (`Product`) на уровень категории (`Category`). Это изменение делает архитектуру более гибкой и правильной с точки зрения доменной модели — все товары в одной категории теперь имеют один тип устройства.

---

## Изменения в базе данных

### Таблица `categories`

**Добавлено:**
- `device_type_id` (BigInteger, nullable) — внешний ключ на таблицу `product_types`

**Индексы:**
- `ix_categories_device_type_id` — индекс для ускорения поиска по типу устройства

### Таблица `products`

**Удалено:**
- `product_type_id` (BigInteger) — внешний ключ на таблицу `product_types`
- `ix_products_product_type_id` — индекс

### Таблица `product_types`

**Добавлено:**
- Relationship `categories` — обратная связь с категориями

---

## Изменения в API категорий

### Категория (Category)

#### `POST /api/v1/categories/admin/category` — Создание категории

**Изменения в запросе:**
- **Добавлено поле:** `device_type_id` (integer, nullable) — ID типа устройства для категории

**Пример запроса:**
```json
{
  "name": "Смартфоны",
  "description": "Мобильные устройства",
  "parent_id": null,
  "manufacturer_id": 1,
  "device_type_id": 5,
  "image": {
    "upload_id": 123
  }
}
```

**Изменения в ответе:**
- **Добавлено поле:** `device_type` — объект типа устройства
  - `id` (integer) — ID типа устройства
  - `name` (string) — Название типа
  - `parent_id` (integer, nullable) — ID родительского типа

**Пример ответа:**
```json
{
  "success": true,
  "data": {
    "id": 10,
    "name": "Смартфоны",
    "description": "Мобильные устройства",
    "image": {
      "upload_id": 123,
      "image_url": "https://..."
    },
    "parent": null,
    "manufacturer": {
      "id": 1,
      "name": "Samsung"
    },
    "device_type": {
      "id": 5,
      "name": "Мобильные устройства",
      "parent_id": null
    }
  }
}
```

---

#### `PUT /api/v1/categories/admin/category/{category_id}` — Обновление категории

**Изменения в запросе:**
- **Добавлено поле:** `device_type_id` (integer, nullable) — ID типа устройства для категории

**Пример запроса:**
```json
{
  "name": "Смартфоны Pro",
  "device_type_id": 5
}
```

**Изменения в ответе:**
- **Добавлено поле:** `device_type` в ответе (см. выше)

---

#### `GET /api/v1/categories/admin/category/{category_id}` — Получение категории

**Изменения в ответе:**
- **Добавлено поле:** `device_type` — объект типа устройства

**Пример ответа:**
```json
{
  "success": true,
  "data": {
    "id": 10,
    "name": "Смартфоны",
    "description": "Мобильные устройства",
    "device_type": {
      "id": 5,
      "name": "Мобильные устройства",
      "parent_id": null
    }
  }
}
```

---

#### `GET /api/v1/categories/admin/categories` — Список категорий

**Изменения в ответе:**
- **Добавлено поле:** `device_type` в каждом элементе списка

---

#### `GET /api/v1/categories/admin/categories/tree` — Дерево категорий

**Изменения в ответе:**
- **Добавлено поле:** `device_type` в каждом элементе дерева

---

## Изменения в API товаров

### Товар (Product)

#### `POST /api/v1/products/admin/product` — Создание товара

**Изменения в запросе:**
- **Удалено поле:** `product_type_id` (integer, nullable)

**Пример запроса:**
```json
{
  "name": "iPhone 15 Pro",
  "description": "Флагманский смартфон",
  "price": 99999.00,
  "category_id": 10,
  "supplier_id": 1,
  "images": [
    {
      "upload_id": 123,
      "is_main": true,
      "ordering": 0
    }
  ],
  "attributes": [
    {
      "name": "Цвет",
      "value": "Titanium Black",
      "is_filterable": true
    }
  ]
}
```

**Изменения в ответе:**
- **Удалено поле:** `product_type` из ответа

**Пример ответа:**
```json
{
  "success": true,
  "data": {
    "id": 100,
    "name": "iPhone 15 Pro",
    "description": "Флагманский смартфон",
    "price": 99999.00,
    "images": [...],
    "attributes": [...],
    "category": {
      "id": 10,
      "name": "Смартфоны",
      "description": "Мобильные устройства",
      "device_type": {
        "id": 5,
        "name": "Мобильные устройства"
      }
    },
    "supplier": {
      "id": 1,
      "name": "Apple Inc."
    }
  }
}
```

---

#### `PUT /api/v1/products/admin/product/{product_id}` — Обновление товара

**Изменения в запросе:**
- **Удалено поле:** `product_type_id` (integer, nullable)

**Пример запроса:**
```json
{
  "name": "iPhone 15 Pro Max",
  "price": 119999.00,
  "category_id": 10
}
```

**Изменения в ответе:**
- **Удалено поле:** `product_type` из ответа

---

#### `GET /api/v1/products/admin/product/{product_id}` — Получение товара

**Изменения в ответе:**
- **Удалено поле:** `product_type` из ответа
- Тип устройства теперь доступен через `category.device_type`

---

#### `GET /api/v1/products/admin/products` — Список товаров

**Изменения в запросе:**
- **Удалён параметр фильтра:** `product_type_id`

**Изменения в ответе:**
- **Удалено поле:** `product_type` из каждого элемента списка

---

#### `GET /api/v1/products/admin/catalog/export` — Экспорт каталога

**Изменения в ответе:**
- **Удалено поле:** `product_type` из каждого элемента экспорта

---

## Миграция данных

### Перенос существующих данных

Если в системе уже есть товары с заполненным `product_type_id`, необходимо выполнить миграцию данных:

```sql
-- Перенос product_type_id из товаров в категории
UPDATE categories c
SET device_type_id = (
    SELECT p.product_type_id 
    FROM products p 
    WHERE p.category_id = c.id 
    AND p.product_type_id IS NOT NULL 
    LIMIT 1
)
WHERE EXISTS (
    SELECT 1 FROM products p 
    WHERE p.category_id = c.id 
    AND p.product_type_id IS NOT NULL
);
```

**Важно:** Если в одной категории находятся товары с разными `product_type_id`, будет выбран первый попавшийся. Рекомендуется проверить данные перед миграцией.

### Проверка данных перед миграцией

```sql
-- Поиск категорий с товарами, имеющими разные product_type_id
SELECT 
    c.id AS category_id,
    c.name AS category_name,
    COUNT(DISTINCT p.product_type_id) AS different_types
FROM categories c
JOIN products p ON p.category_id = c.id
WHERE p.product_type_id IS NOT NULL
GROUP BY c.id, c.name
HAVING COUNT(DISTINCT p.product_type_id) > 1;
```

---

## Обратная совместимость

### Breaking Changes

1. **API товаров:**
   - Удалён параметр `product_type_id` из запросов создания/обновления товара
   - Удалено поле `product_type` из ответов API товаров
   - Удалён параметр фильтрации `product_type_id` из списка товаров

2. **API категорий:**
   - Добавлен параметр `device_type_id` в запросы создания/обновления категории
   - Добавлено поле `device_type` в ответы API категорий

### Рекомендации по обновлению

1. **Клиентские приложения:**
   - Обновите формы создания/редактирования товаров — уберите выбор типа устройства
   - Обновите формы создания/редактирования категорий — добавьте выбор типа устройства
   - Обновите отображение товаров — тип устройства теперь берётся из категории

2. **Интеграции:**
   - Обновите API-клиенты для работы с новой структурой ответов
   - Пересмотрите логику фильтрации товаров — используйте категорию вместо типа устройства

---

## Применение миграции

### Upgrade (применение изменений)

```bash
alembic upgrade head
```

### Downgrade (откат изменений)

```bash
alembic downgrade ba0dcf155658
```

---

## Чек-лист обновления

- [ ] Применить миграцию БД
- [ ] Перенести данные из `products.product_type_id` в `categories.device_type_id`
- [ ] Обновить фронтенд (формы товаров и категорий)
- [ ] Обновить API-клиенты
- [ ] Обновить документацию
- [ ] Протестировать создание/обновление категорий
- [ ] Протестировать создание/обновление товаров
- [ ] Проверить отображение типа устройства в товарах

---

## Архитектурные преимущества

1. **Согласованность данных:** Все товары в одной категории теперь имеют один тип устройства
2. **Упрощение модели товара:** Товар больше не содержит избыточных данных
3. **Гибкость управления:** Изменение типа устройства для категории автоматически применяется ко всем товарам
4. **Упрощение фильтрации:** Фильтрация по типу устройства теперь выполняется через категорию
