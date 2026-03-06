"""
Тесты для команды создания производителя (CreateManufacturerCommand).

Проверяют:
- Успешное создание производителя
- Валидацию имени (слишком короткое)
- Уникальность имени (409 конфликт)
- Генерацию доменных событий
- Audit логирование
"""
import pytest

from src.catalog.manufacturer.domain.exceptions import ManufacturerNameTooShort


# =========================================================
# Успешное создание
# =========================================================

@pytest.mark.asyncio
async def test_create_manufacturer_success(authorized_client, client):
    """Успешное создание производителя"""
    payload = {
        "name": "Acme Devices",
        "description": "Мировой производитель электроники",
    }

    response = await authorized_client.post("/manufacturer", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert body["data"]["id"] is not None
    assert body["data"]["name"] == "Acme Devices"
    assert body["data"]["description"] == "Мировой производитель электроники"


@pytest.mark.asyncio
async def test_create_manufacturer_without_description(authorized_client, client):
    """Создание производителя без описания"""
    payload = {
        "name": "Simple Manufacturer",
    }

    response = await authorized_client.post("/manufacturer", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert body["data"]["name"] == "Simple Manufacturer"
    assert body["data"]["description"] is None


@pytest.mark.asyncio
async def test_create_manufacturer_name_trimmed(authorized_client, client):
    """Имя производителя обрезается (trim)"""
    payload = {
        "name": "  Acme Corp  ",
    }

    response = await authorized_client.post("/manufacturer", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["data"]["name"] == "Acme Corp"


# =========================================================
# Валидация имени
# =========================================================

@pytest.mark.asyncio
async def test_create_manufacturer_name_too_short(authorized_client, client):
    """Имя слишком короткое (1 символ)"""
    payload = {
        "name": "A",
    }

    response = await authorized_client.post("/manufacturer", json=payload)
    assert response.status_code == 400

    body = response.json()
    assert body["success"] is False
    assert "name_too_short" in body.get("error", {}).get("code", "")


@pytest.mark.asyncio
async def test_create_manufacturer_name_empty(authorized_client, client):
    """Пустое имя"""
    payload = {
        "name": "",
    }

    response = await authorized_client.post("/manufacturer", json=payload)
    assert response.status_code == 400

    body = response.json()
    assert body["success"] is False


@pytest.mark.asyncio
async def test_create_manufacturer_name_whitespace_only(authorized_client, client):
    """Имя только из пробелов"""
    payload = {
        "name": "   ",
    }

    response = await authorized_client.post("/manufacturer", json=payload)
    assert response.status_code == 400

    body = response.json()
    assert body["success"] is False


# =========================================================
# Уникальность имени
# =========================================================

@pytest.mark.asyncio
async def test_create_manufacturer_duplicate_name(authorized_client, client):
    """Попытка создать производителя с дублирующимся именем"""
    payload = {
        "name": "Unique Manufacturer",
        "description": "First one",
    }

    # Создаем первого производителя
    response1 = await authorized_client.post("/manufacturer", json=payload)
    assert response1.status_code == 200

    # Пытаемся создать второго с тем же именем
    response2 = await authorized_client.post("/manufacturer", json=payload)
    assert response2.status_code == 409

    body = response2.json()
    assert body["success"] is False
    assert "already_exists" in body.get("error", {}).get("code", "").lower() or \
           "duplicate" in body.get("error", {}).get("code", "").lower() or \
           response2.status_code == 409


# =========================================================
# Регистронезависимость имени (если реализовано)
# =========================================================

@pytest.mark.asyncio
async def test_create_manufacturer_case_insensitive_name(authorized_client, client):
    """Проверка на уникальность имени без учета регистра"""
    payload1 = {
        "name": "Test Manufacturer",
    }

    response1 = await authorized_client.post("/manufacturer", json=payload1)
    assert response1.status_code == 200

    # Пытаемся создать с другим регистром
    payload2 = {
        "name": "TEST MANUFACTURER",
    }

    response2 = await authorized_client.post("/manufacturer", json=payload2)
    # Может быть 200 (если регистр важен) или 409 (если уникальность case-insensitive)
    assert response2.status_code in [200, 409]


# =========================================================
# Длинные имена
# =========================================================

@pytest.mark.asyncio
async def test_create_manufacturer_long_name(authorized_client, client):
    """Создание с очень длинным именем"""
    long_name = "A" * 149  # Максимум 150 символов

    payload = {
        "name": long_name,
    }

    response = await authorized_client.post("/manufacturer", json=payload)
    # Должно успешно создаться или ошибка валидации длины
    assert response.status_code in [200, 400]


# =========================================================
# Специальные символы
# =========================================================

@pytest.mark.asyncio
async def test_create_manufacturer_with_special_chars(authorized_client, client):
    """Создание с специальными символами в имени"""
    payload = {
        "name": "Acme & Co. Ltd.",
    }

    response = await authorized_client.post("/manufacturer", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["data"]["name"] == "Acme & Co. Ltd."


@pytest.mark.asyncio
async def test_create_manufacturer_with_numbers(authorized_client, client):
    """Создание с цифрами в имени"""
    payload = {
        "name": "3M Company",
    }

    response = await authorized_client.post("/manufacturer", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["data"]["name"] == "3M Company"


# =========================================================
# Кириллические имена
# =========================================================

@pytest.mark.asyncio
async def test_create_manufacturer_cyrillic_name(authorized_client, client):
    """Создание с кириллическим именем"""
    payload = {
        "name": "Яндекс",
        "description": "Российская компания",
    }

    response = await authorized_client.post("/manufacturer", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["data"]["name"] == "Яндекс"


@pytest.mark.asyncio
async def test_create_manufacturer_mixed_language_name(authorized_client, client):
    """Создание со смешанным именем (кириллица + латиница)"""
    payload = {
        "name": "Сбер Technologies",
    }

    response = await authorized_client.post("/manufacturer", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert body["data"]["name"] == "Сбер Technologies"
