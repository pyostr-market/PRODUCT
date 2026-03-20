# API Specification: Каталог товаров — Фильтрация и фильтры

**Версия:** 1.0  
**Дата:** 20 марта 2026  
**Модуль:** `src.catalog.product`

---

## Содержание

1. [Обзор](#обзор)
2. [GET /product/catalog/filters](#get-productcatalogfilters)
3. [GET /product](#get-product)
4. [Структуры данных](#структуры-данных)
5. [Коды ошибок](#коды-ошибок)
6. [Примеры запросов](#примеры-запросов)

---

## Обзор

Данный документ описывает два API endpoint'а для работы с фильтрацией каталога товаров:

| Endpoint | Метод | Описание |
|----------|-------|----------|
| `/product/catalog/filters` | GET | Получение доступных фильтров для категории/типа товара |
| `/product` | GET | Получение списка товаров с применением фильтров |

### Базовый URL

```
http://<host>:<port>/product
```

### Аутентификация

Оба endpoint **не требуют** аутентификации и доступны публично.

---

## GET /product/catalog/filters

Получение списка доступных фильтров (атрибутов) и их значений для указанной категории или типа товара.

### Метаданные

| Параметр | Значение |
|----------|----------|
| **Метод** | `GET` |
| **Путь** | `/product/catalog/filters` |
| **Content-Type** | `application/json` |
| **Аутентификация** | Не требуется |
| **Теги** | `Каталог`, `Фильтры` |

### Параметры запроса (Query Parameters)

| Параметр | Тип | Обязательный | Описание | Пример |
|----------|-----|--------------|----------|--------|
| `product_type_id` | `integer` | Нет | ID типа товара. **Имеет наивысший приоритет** (если указан, используется напрямую) | `5` |
| `category_id` | `integer` | Нет | ID категории для получения фильтров. Если указан, система автоматически определит `device_type_id` (с учётом иерархии категорий) | `101` |
| `device_type_id` | `integer` | Нет | Альтернативное имя для `product_type_id` (для обратной совместимости). Используется, если `product_type_id` не указан | `5` |

> **Примечание:** Если все параметры не указаны, возвращаются фильтры для **всех** товаров.

### Приоритет параметров

1. **`product_type_id`** — наивысший приоритет (если указан, используется напрямую)
2. **`device_type_id`** — используется, если `product_type_id` не указан
3. **`category_id`** — используется, если ни один из параметров типа не указан (с автоматическим определением через иерархию)

### Логика определения типа товара

1. Если указан `product_type_id` — используется он напрямую
2. Если указан `device_type_id` (и `product_type_id` не указан) — используется он
3. Если указана `category_id`:
   - Проверяется `device_type_id` указанной категории
   - Если `device_type_id = NULL`, система рекурсивно поднимается вверх по иерархии родительских категорий
   - Используется первый найденный `device_type_id`
4. Если ничего не указано — фильтры возвращаются для всех товаров

### Коды состояния HTTP

| Код | Описание |
|-----|----------|
| `200 OK` | Фильтры успешно получены |
| `400 Bad Request` | Неверный формат параметров |
| `404 Not Found` | Категория или тип товара не найдены |
| `500 Internal Server Error` | Внутренняя ошибка сервера |

### Формат ответа (200 OK)

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
      }
    ]
  },
  "message": null
}
```

### Структура ответа

| Поле | Тип | Описание |
|------|-----|----------|
| `success` | `boolean` | Флаг успешного выполнения запроса |
| `data.filters` | `array` | Массив фильтров |
| `data.filters[].name` | `string` | Имя атрибута (техническое название) |
| `data.filters[].is_filterable` | `boolean` | Флаг возможности фильтрации по этому атрибуту |
| `data.filters[].options` | `array` | Массив доступных значений атрибута |
| `data.filters[].options[].value` | `string` | Значение атрибута |
| `data.filters[].options[].count` | `integer` | Количество товаров с данным значением |
| `message` | `string|null` | Сообщение (null при успехе) |

---

## GET /product

Получение списка товаров с применением фильтрации по атрибутам, категории и названию.

### Метаданные

| Параметр | Значение |
|----------|----------|
| **Метод** | `GET` |
| **Путь** | `/product` |
| **Content-Type** | `application/json` |
| **Аутентификация** | Не требуется |
| **Теги** | `Каталог`, `Товары` |

### Параметры запроса (Query Parameters)

| Параметр | Тип | Обязательный | По умолчанию | Описание | Пример |
|----------|-----|--------------|--------------|----------|--------|
| `name` | `string` | Нет | `null` | Поиск по названию товара (частичное совпадение, регистронезависимый) | `iPhone` |
| `category_id` | `integer` | Нет | `null` | ID категории для фильтрации | `101` |
| `attributes` | `string` (JSON) | Нет | `null` | JSON-объект с атрибутами для фильтрации. **Значения передаются массивом** | `{"RAM":["8 GB","16 GB"]}` |
| `limit` | `integer` | Нет | `10` | Количество записей для возврата (макс. 100) | `20` |
| `offset` | `integer` | Нет | `0` | Смещение для пагинации | `0` |

### Формат параметра `attributes`

Параметр `attributes` передаётся как **URL-encoded JSON строка**:

```
attributes={"RAM":["8 GB","16 GB"],"Color":["Black","White"]}
```

**Структура JSON:**

```json
{
  "RAM": ["8 GB", "16 GB"],
  "Color": ["Black", "White"],
  "Storage": ["128 GB"]
}
```

**Логика фильтрации:**
- **Внутри одного атрибута:** OR (товар должен соответствовать **хотя бы одному** значению из массива)
- **Между разными атрибутами:** AND (товар должен соответствовать **всем** указанным атрибутам)

### Коды состояния HTTP

| Код | Описание |
|-----|----------|
| `200 OK` | Список товаров успешно получен |
| `400 Bad Request` | Неверный формат JSON в параметре `attributes` |
| `404 Not Found` | Категория не найдена |
| `500 Internal Server Error` | Внутренняя ошибка сервера |

### Формат ответа (200 OK)

```json
{
  "success": true,
  "data": {
    "total": 15,
    "items": [
      {
        "id": 3001,
        "name": "Смартфон X Pro",
        "description": "Флагманская модель 2026 года",
        "price": "79990.00",
        "images": [
          {
            "upload_id": 1,
            "image_url": "https://cdn.example.com/product/smartphone-x-pro.jpg",
            "is_main": true,
            "ordering": 0
          }
        ],
        "attributes": [
          {
            "id": 10,
            "name": "RAM",
            "value": "16 GB",
            "is_filterable": true
          },
          {
            "id": 11,
            "name": "Color",
            "value": "Black",
            "is_filterable": true
          }
        ],
        "category": {
          "id": 101,
          "name": "Смартфоны",
          "description": "Мобильные устройства"
        },
        "supplier": {
          "id": 210,
          "name": "ООО Поставка Плюс",
          "contact_email": "sales@supply-plus.example",
          "phone": "+7-999-123-45-67"
        }
      }
    ]
  },
  "message": null
}
```

### Структура ответа

| Поле | Тип | Описание |
|------|-----|----------|
| `success` | `boolean` | Флаг успешного выполнения запроса |
| `data.total` | `integer` | Общее количество товаров, соответствующих фильтру |
| `data.items` | `array` | Массив товаров (с учётом пагинации) |
| `data.items[].id` | `integer` | ID товара |
| `data.items[].name` | `string` | Название товара |
| `data.items[].description` | `string|null` | Описание товара |
| `data.items[].price` | `string` (decimal) | Цена товара |
| `data.items[].images` | `array` | Массив изображений товара |
| `data.items[].attributes` | `array` | Массив атрибутов товара |
| `data.items[].category` | `object|null` | Категория товара |
| `data.items[].supplier` | `object|null` | Поставщик товара |
| `message` | `string|null` | Сообщение (null при успехе) |

---

## Структуры данных

### FilterSchema

```typescript
{
  name: string;           // Имя атрибута
  is_filterable: boolean; // Флаг фильтрации
  options: FilterOptionSchema[];
}
```

### FilterOptionSchema

```typescript
{
  value: string;  // Значение атрибута
  count: number;  // Количество товаров (опционально, по умолчанию 0)
}
```

### ProductReadSchema

```typescript
{
  id: number;
  name: string;
  description: string | null;
  price: string;  // Decimal в строковом формате
  images: ProductImageReadSchema[];
  attributes: ProductAttributeReadSchema[];
  category: CategoryNestedSchema | null;
  supplier: SupplierNestedSchema | null;
}
```

### ProductAttributeReadSchema

```typescript
{
  id: number;
  name: string;
  value: string;
  is_filterable: boolean;
}
```

---

## Коды ошибок

### 400 Bad Request

**Неверный формат JSON в параметре `attributes`**

```json
{
  "success": false,
  "data": null,
  "message": "Invalid attributes JSON format",
  "details": {
    "reason": "invalid_attributes_json"
  }
}
```

### 404 Not Found

**Категория не найдена**

```json
{
  "success": false,
  "data": null,
  "message": "Категория не найдена",
  "details": null
}
```

**Тип товара не найден**

```json
{
  "success": false,
  "data": null,
  "message": "Тип товара не найден",
  "details": null
}
```

### 500 Internal Server Error

**Внутренняя ошибка сервера**

```json
{
  "success": false,
  "data": null,
  "message": "Внутренняя ошибка сервера",
  "details": {
    "error_code": "INTERNAL_ERROR"
  }
}
```

---

## Примеры запросов

### Пример 1: Получить все фильтры для категории

```bash
curl -X GET "http://localhost:8001/product/catalog/filters?category_id=101" \
  -H "Accept: application/json"
```

**Ответ:**

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
          {"value": "White", "count": 8}
        ]
      }
    ]
  }
}
```

---

### Пример 2: Получить фильтры для типа товара (через product_type_id)

```bash
curl -X GET "http://localhost:8001/product/catalog/filters?product_type_id=5" \
  -H "Accept: application/json"
```

---

### Пример 2a: Получить фильтры для типа товара (через device_type_id)

```bash
curl -X GET "http://localhost:8001/product/catalog/filters?device_type_id=5" \
  -H "Accept: application/json"
```

---

### Пример 3: Фильтрация товаров по одному атрибуту

```bash
curl -X GET "http://localhost:8001/product?category_id=101&attributes={\"RAM\":[\"8 GB\"]}" \
  -H "Accept: application/json"
```

---

### Пример 4: Фильтрация по нескольким атрибутам с множественными значениями

```bash
curl -X GET "http://localhost:8001/product?category_id=101&attributes={\"RAM\":[\"8 GB\",\"16 GB\"],\"Color\":[\"Black\",\"White\"]}" \
  -H "Accept: application/json"
```

**Логика:**
- RAM = "8 GB" **ИЛИ** "16 GB"
- **И** Color = "Black" **ИЛИ** "White"

---

### Пример 5: Комбинированный запрос с пагинацией

```bash
curl -X GET "http://localhost:8001/product?category_id=101&attributes={\"RAM\":[\"8 GB\"]}&limit=20&offset=0" \
  -H "Accept: application/json"
```

---

### Пример 6: Поиск по названию с фильтрацией

```bash
curl -X GET "http://localhost:8001/product?name=iPhone&attributes={\"Storage\":[\"128 GB\",\"256 GB\"]}&limit=10" \
  -H "Accept: application/json"
```

---

### Пример 7: URL-encoded запрос (для JavaScript fetch)

```javascript
const params = new URLSearchParams({
  category_id: '101',
  attributes: JSON.stringify({
    RAM: ['8 GB', '16 GB'],
    Color: ['Black', 'White']
  }),
  limit: '20',
  offset: '0'
});

fetch(`/product?${params.toString()}`)
  .then(res => res.json())
  .then(data => console.log(data));
```

---

## Сценарии использования

### Сценарий A: Построение UI фильтра

1. Пользователь переходит в категорию "Смартфоны" (`category_id=101`)
2. Фронтенд запрашивает фильтры: `GET /product/catalog/filters?category_id=101`
3. Получает список фильтров с вариантами значений
4. Отображает чекбоксы/селекты для каждого фильтра
5. Показывает количество товаров для каждого значения (`count`)

### Сценарий B: Применение выбранных фильтров

1. Пользователь выбирает: RAM=[8GB, 16GB], Color=[Black]
2. Фронтенд формирует запрос:
   ```
   GET /product?category_id=101&attributes={"RAM":["8 GB","16 GB"],"Color":["Black"]}
   ```
3. Получает отфильтрованный список товаров
4. Отображает товары пользователю
5. Обновляет счётчики в фильтрах (опционально)

### Сценарий C: Наследование фильтров от родительской категории

1. Категория "iPhone 15 Pro" не имеет собственного `device_type_id`
2. Родительская категория "iPhone" имеет `device_type_id=5` (Смартфоны)
3. Запрос: `GET /product/catalog/filters?category_id=<ID iPhone 15 Pro>`
4. Система автоматически определяет `device_type_id=5` через рекурсивный подъём
5. Возвращаются фильтры для типа "Смартфоны"

---

## Ограничения

| Параметр | Ограничение |
|----------|-------------|
| `limit` (максимум) | 100 записей |
| `attributes` (макс. ключей) | 20 атрибутов |
| `attributes[].value` (макс. элементов) | 50 значений на атрибут |
| `name` (макс. длина) | 200 символов |

---

## Версионирование

Текущая версия API: **v1** (подразумевается, если не указано иное).

Изменения в формате ответа или логике работы будут отражены в новой версии документа.

---

## Контакты

По вопросам и предложениям обращайтесь к команде разработки каталога.
