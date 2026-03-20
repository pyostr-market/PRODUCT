# Фильтрация каталога товаров

## Обзор

Реализована система фильтрации каталога товаров по атрибутам с поддержкой:
- Получения доступных фильтров для категории/типа товара
- Фильтрации товаров по множественным значениям атрибутов

## API Endpoints

### 1. Получение фильтров для каталога

**Endpoint:** `GET /product/catalog/filters`

**Описание:** Возвращает список всех доступных фильтров (атрибутов) и их значений для указанной категории или типа товара.

**Логика работы:**
1. Если указана `category_id`, система проверяет её `device_type_id`
2. Если у категории нет `device_type_id`, смотрим на родительскую категорию (рекурсивно вверх по иерархии)
3. Получаем все атрибуты с флагом `is_filterable=true` для этого типа товара
4. Группируем уникальные значения атрибутов и возвращаем в ответе

**Параметры запроса:**
- `category_id` (int, optional) - ID категории для фильтрации
- `device_type_id` (int, optional) - ID типа товара (если category_id не указан)

**Пример запроса:**
```bash
GET /product/catalog/filters?category_id=101
```

**Пример ответа:**
```json
{
  "success": true,
  "data": {
    "filters": [
      {
        "name": "RAM",
        "is_filterable": true,
        "options": [
          {"value": "4 GB", "count": 5},
          {"value": "8 GB", "count": 10},
          {"value": "16 GB", "count": 7}
        ]
      },
      {
        "name": "Color",
        "is_filterable": true,
        "options": [
          {"value": "Black", "count": 12},
          {"value": "White", "count": 8},
          {"value": "Blue", "count": 6}
        ]
      },
      {
        "name": "Storage",
        "is_filterable": true,
        "options": [
          {"value": "64 GB", "count": 8},
          {"value": "128 GB", "count": 15},
          {"value": "256 GB", "count": 10}
        ]
      }
    ]
  }
}
```

**Структура ответа:**
- `filters` - массив фильтров
  - `name` - имя атрибута (RAM, Color, Storage и т.д.)
  - `is_filterable` - флаг возможности фильтрации
  - `options` - массив доступных значений
    - `value` - значение атрибута
    - `count` - количество товаров с этим значением (опционально)

---

### 2. Фильтрация товаров

**Endpoint:** `GET /product`

**Описание:** Возвращает список товаров с применённой фильтрацией по атрибутам.

**Параметры запроса:**
- `name` (str, optional) - Поиск по названию (частичное совпадение)
- `category_id` (int, optional) - ID категории
- `attributes` (str, optional) - JSON-объект с атрибутами для фильтрации
- `limit` (int) - Количество записей (по умолчанию 10)
- `offset` (int) - Смещение (по умолчанию 0)

**Формат attributes:**
```json
{
  "RAM": ["8 GB", "16 GB"],
  "Color": ["Black", "White"],
  "Storage": ["128 GB"]
}
```

**Важно:** Значения атрибутов передаются как **массивы**. Товар должен соответствовать **хотя бы одному** значению из массива для каждого атрибута (логика OR внутри атрибута, AND между атрибутами).

**Пример запроса:**
```bash
GET /product?category_id=101&attributes={"RAM":["8 GB","16 GB"],"Color":["Black"]}&limit=20&offset=0
```

**Пример ответа:**
```json
{
  "success": true,
  "data": {
    "total": 15,
    "items": [
      {
        "id": 3001,
        "name": "Смартфон X",
        "description": "Флагманская модель",
        "price": "59990.00",
        "images": [...],
        "attributes": [
          {"id": 10, "name": "RAM", "value": "8 GB", "is_filterable": true},
          {"id": 11, "name": "Color", "value": "Black", "is_filterable": true}
        ],
        "category": {...},
        "supplier": {...}
      },
      ...
    ]
  }
}
```

---

## Сценарии использования

### Сценарий 1: Построение фильтра в каталоге

1. Пользователь переходит в категорию "Смартфоны" (category_id=101)
2. Фронтенд делает запрос: `GET /product/catalog/filters?category_id=101`
3. Получает список всех доступных фильтров и их значений
4. Отображает фильтры в UI (чекбоксы, селекты и т.д.)

### Сценарий 2: Применение фильтров

1. Пользователь выбирает фильтры: RAM=8GB, RAM=16GB, Color=Black
2. Фронтенд делает запрос: `GET /product?category_id=101&attributes={"RAM":["8 GB","16 GB"],"Color":["Black"]}`
3. Получает отфильтрованный список товаров
4. Отображает товары пользователю

### Сценарий 3: Наследование типа товара

1. У нас есть категория "iPhone 15" (дочерняя от "iPhone")
2. У "iPhone 15" нет своего `device_type_id`
3. У родительской категории "iPhone" указан `device_type_id=5` (Смартфоны)
4. При запросе `GET /product/catalog/filters?category_id=<ID iPhone 15>` система автоматически поднимется вверх по иерархии и найдёт тип товара "Смартфоны"
5. Вернёт все фильтры для смартфонов

---

## Архитектурные решения

### 1. Определение типа товара для категории

Используется рекурсивный SQL CTE (Common Table Expression) для подъёма по иерархии категорий:

```sql
WITH RECURSIVE category_chain AS (
    SELECT id, parent_id, device_type_id
    FROM categories
    WHERE id = :category_id
    UNION ALL
    SELECT c.id, c.parent_id, c.device_type_id
    FROM categories c
    INNER JOIN category_chain cc ON c.id = cc.parent_id
    WHERE cc.device_type_id IS NULL
)
SELECT device_type_id
FROM category_chain
WHERE device_type_id IS NOT NULL
LIMIT 1
```

### 2. Группировка уникальных значений атрибутов

SQL запрос для получения фильтров:

```sql
SELECT
    pa.name as attribute_name,
    pa.is_filterable,
    pav.value as attribute_value,
    COUNT(DISTINCT p.id) as product_count
FROM product_attribute_values pav
JOIN product_attributes pa ON pa.id = pav.attribute_id
JOIN products p ON p.id = pav.product_id
JOIN categories c ON c.id = p.category_id
WHERE pa.is_filterable = true
  AND c.device_type_id = :device_type_id
GROUP BY pa.name, pa.is_filterable, pav.value
ORDER BY pa.name, pav.value
```

### 3. Фильтрация по множественным значениям

Для поддержки множественных значений используется SQL оператор `IN` (для SQLAlchemy) или `= ANY()` (для raw SQL):

```python
# SQLAlchemy версия
ProductAttributeValue.value.in_(attr_values)

# Raw SQL версия
pav.value = ANY(:attr_values)
```

---

## Структуры данных

### DTO (Data Transfer Objects)

```python
@dataclass
class FilterOptionDTO:
    value: str
    count: int = 0

@dataclass
class FilterDTO:
    name: str
    is_filterable: bool = True
    options: list[FilterOptionDTO]

@dataclass
class CatalogFiltersDTO:
    filters: list[FilterDTO]
```

### Schema (Pydantic)

```python
class FilterOptionSchema(BaseModel):
    value: str
    count: int = 0

class FilterSchema(BaseModel):
    name: str
    is_filterable: bool = True
    options: List[FilterOptionSchema]

class CatalogFiltersResponse(BaseModel):
    filters: List[FilterSchema]
```

---

## Расширение функциональности

### Добавление нового атрибута

1. Создать атрибут через API: `POST /product/admin/attribute`
2. Указать `is_filterable=true` для возможности фильтрации
3. Атрибут автоматически появится в фильтрах для соответствующего типа товара

### Кэширование фильтров

Для оптимизации производительности можно добавить кэширование:
- Кэшировать результат `get_catalog_filters()` на 5-15 минут
- Инвалидировать кэш при изменении атрибутов или товаров

### Пагинация значений фильтров

Если у атрибута очень много значений (например, >100), можно добавить пагинацию:
- Добавить параметры `filter_limit` и `filter_offset`
- Ограничивать количество возвращаемых значений

---

## Тестирование

### Примеры запросов для тестирования

```bash
# 1. Получить все фильтры для категории
curl "http://localhost:8001/product/catalog/filters?category_id=101"

# 2. Получить фильтры для типа товара
curl "http://localhost:8001/product/catalog/filters?device_type_id=5"

# 3. Фильтрация товаров по одному атрибуту
curl "http://localhost:8001/product?category_id=101&attributes={\"RAM\":[\"8 GB\"]}"

# 4. Фильтрация товаров по нескольким атрибутам с множественными значениями
curl "http://localhost:8001/product?category_id=101&attributes={\"RAM\":[\"8 GB\",\"16 GB\"],\"Color\":[\"Black\",\"White\"]}"

# 5. Комбинированный запрос с пагинацией
curl "http://localhost:8001/product?category_id=101&attributes={\"RAM\":[\"8 GB\"]}&limit=20&offset=0"
```

---

## Миграции базы данных

Изменения в схеме БД не требуются. Используются существующие таблицы:
- `product_attributes` - атрибуты с флагом `is_filterable`
- `product_attribute_values` - значения атрибутов
- `categories` - категории с `device_type_id` и `parent_id`
- `product_types` - типы товаров

---

## Производительность

### Рекомендации

1. **Индексы:** Убедитесь, что существуют индексы:
   - `ix_product_attributes_is_filterable`
   - `ix_product_attribute_values_attribute_id`
   - `ix_product_attribute_values_value`
   - `ix_categories_device_type_id`

2. **Кэширование:** Кэшируйте результаты фильтров на 5-15 минут

3. **Оптимизация запросов:** Используйте `EXPLAIN ANALYZE` для проверки планов выполнения

4. **Ограничение количества фильтров:** Если фильтров очень много, рассмотрите пагинацию или группировку
