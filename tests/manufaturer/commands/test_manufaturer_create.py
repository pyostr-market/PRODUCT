import pytest

from src.catalog.manufacturer.api.schemas.schemas import ManufacturerReadSchema


@pytest.mark.asyncio
async def test_create_manufacturer_200(authorized_client):
    response = await authorized_client.post(
        "/manufacturer/",
        json={
            "name": "Apple название",
            "description": "Apple описание"
        }
    )

    # 1️⃣ HTTP
    assert response.status_code == 200

    # 2️⃣ Контракт API
    body = response.json()
    assert body["success"] is True
    assert "data" in body
    assert "error" not in body

    # 3️⃣ Валидация схемы
    manufacturer = ManufacturerReadSchema(**body["data"])

    # 4️⃣ Бизнес-проверки
    assert manufacturer.name == "Apple название"
    assert manufacturer.description == "Apple описание"
    assert isinstance(manufacturer.id, int)

@pytest.mark.asyncio
async def test_create_manufacturer_409_already_exists(authorized_client):
    payload = {
        "name": "Samsung",
        "description": "Test description"
    }

    # Создаём первый раз
    first = await authorized_client.post("/manufacturer/", json=payload)
    assert first.status_code == 200

    # Пытаемся создать повторно
    response = await authorized_client.post("/manufacturer/", json=payload)

    # 1️⃣ HTTP
    assert response.status_code == 409

    # 2️⃣ Контракт API
    body = response.json()
    assert body["success"] is False
    assert "error" in body
    assert "data" not in body

    error = body["error"]

    # 3️⃣ Проверка структуры ошибки
    assert error["code"] == "manufacturer_already_exist"
    assert isinstance(error["message"], str)
    assert isinstance(error["details"], dict)

@pytest.mark.asyncio
async def test_create_manufacturer_400_name_too_short(authorized_client):
    response = await authorized_client.post(
        "/manufacturer/",
        json={
            "name": "A",  # слишком короткое
            "description": "Test"
        }
    )

    # 1️⃣ HTTP
    assert response.status_code == 400

    # 2️⃣ Контракт API
    body = response.json()
    assert body["success"] is False
    assert "error" in body
    assert "data" not in body

    error = body["error"]

    # 3️⃣ Проверяем доменную ошибку
    assert error["code"] == "manufacturer_name_too_short"
    assert isinstance(error["message"], str)
    assert isinstance(error["details"], dict)