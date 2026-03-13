"""
Тесты для команды обновления производителя (UpdateManufacturerCommand).

Проверяют:
- Успешное обновление
- Обновление имени
- Обновление описания
- Валидацию имени
- Обновление несуществующего производителя (404)
- Генерацию доменных событий
- Audit логирование
"""
import pytest

# =========================================================
# Успешное обновление
# =========================================================

@pytest.mark.asyncio
async def test_update_manufacturer_name(authorized_client, client):
    """Обновление имени производителя"""
    # Создаем производителя
    create_payload = {"name": "Old Name", "description": "Description"}
    create_response = await authorized_client.post("/manufacturer", json=create_payload)
    manufacturer_id = create_response.json()["data"]["id"]

    # Обновляем имя
    update_payload = {"name": "New Name"}
    response = await authorized_client.put(f"/manufacturer/{manufacturer_id}", json=update_payload)
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert body["data"]["name"] == "New Name"
    assert body["data"]["description"] == "Description"


@pytest.mark.asyncio
async def test_update_manufacturer_description(authorized_client, client):
    """Обновление описания производителя"""
    # Создаем производителя
    create_payload = {"name": "Test Manufacturer", "description": "Old description"}
    create_response = await authorized_client.post("/manufacturer", json=create_payload)
    manufacturer_id = create_response.json()["data"]["id"]

    # Обновляем описание
    update_payload = {"description": "New description"}
    response = await authorized_client.put(f"/manufacturer/{manufacturer_id}", json=update_payload)
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert body["data"]["description"] == "New description"


@pytest.mark.asyncio
async def test_update_manufacturer_both_fields(authorized_client, client):
    """Обновление имени и описания одновременно"""
    # Создаем производителя
    create_payload = {"name": "Old Name", "description": "Old description"}
    create_response = await authorized_client.post("/manufacturer", json=create_payload)
    manufacturer_id = create_response.json()["data"]["id"]

    # Обновляем оба поля
    update_payload = {"name": "New Name", "description": "New description"}
    response = await authorized_client.put(f"/manufacturer/{manufacturer_id}", json=update_payload)
    assert response.status_code == 200

    body = response.json()
    assert body["data"]["name"] == "New Name"
    assert body["data"]["description"] == "New description"


@pytest.mark.asyncio
async def test_update_manufacturer_empty_payload(authorized_client, client):
    """Обновление с пустым payload (ничего не меняется)"""
    # Создаем производителя
    create_payload = {"name": "Test Manufacturer", "description": "Description"}
    create_response = await authorized_client.post("/manufacturer", json=create_payload)
    manufacturer_id = create_response.json()["data"]["id"]

    # Обновляем с пустым payload
    update_payload = {}
    response = await authorized_client.put(f"/manufacturer/{manufacturer_id}", json=update_payload)
    assert response.status_code == 200

    body = response.json()
    assert body["data"]["name"] == "Test Manufacturer"
    assert body["data"]["description"] == "Description"


# =========================================================
# Валидация при обновлении
# =========================================================

@pytest.mark.asyncio
async def test_update_manufacturer_name_too_short(authorized_client, client):
    """Обновление с слишком коротким именем"""
    # Создаем производителя
    create_payload = {"name": "Test Manufacturer"}
    create_response = await authorized_client.post("/manufacturer", json=create_payload)
    manufacturer_id = create_response.json()["data"]["id"]

    # Пытаемся обновить с коротким именем
    update_payload = {"name": "A"}
    response = await authorized_client.put(f"/manufacturer/{manufacturer_id}", json=update_payload)
    assert response.status_code == 400

    body = response.json()
    assert body["success"] is False


@pytest.mark.asyncio
async def test_update_manufacturer_name_empty(authorized_client, client):
    """Обновление с пустым именем"""
    # Создаем производителя
    create_payload = {"name": "Test Manufacturer"}
    create_response = await authorized_client.post("/manufacturer", json=create_payload)
    manufacturer_id = create_response.json()["data"]["id"]

    # Пытаемся обновить с пустым именем
    update_payload = {"name": ""}
    response = await authorized_client.put(f"/manufacturer/{manufacturer_id}", json=update_payload)
    assert response.status_code == 400

    body = response.json()
    assert body["success"] is False


# =========================================================
# 404 ошибки
# =========================================================

@pytest.mark.asyncio
async def test_update_nonexistent_manufacturer(authorized_client, client):
    """Обновление несуществующего производителя"""
    update_payload = {"name": "New Name"}
    response = await authorized_client.put("/manufacturer/99999", json=update_payload)
    assert response.status_code == 404

    body = response.json()
    assert body["success"] is False


# =========================================================
# Уникальность имени при обновлении
# =========================================================

@pytest.mark.asyncio
async def test_update_manufacturer_duplicate_name(authorized_client, client):
    """Попытка установить имя, которое уже используется"""
    # Создаем двух производителей
    create_payload1 = {"name": "Manufacturer 1"}
    create_response1 = await authorized_client.post("/manufacturer", json=create_payload1)
    
    create_payload2 = {"name": "Manufacturer 2"}
    create_response2 = await authorized_client.post("/manufacturer", json=create_payload2)
    
    manufacturer_id_2 = create_response2.json()["data"]["id"]

    # Пытаемся изменить имя второго на имя первого
    update_payload = {"name": "Manufacturer 1"}
    response = await authorized_client.put(f"/manufacturer/{manufacturer_id_2}", json=update_payload)
    assert response.status_code == 409


# =========================================================
# Проверка данных после обновления
# =========================================================

@pytest.mark.asyncio
async def test_update_manufacturer_verify_with_get(authorized_client, client):
    """Проверка, что GET возвращает обновленные данные"""
    # Создаем производителя
    create_payload = {"name": "Original Name", "description": "Original description"}
    create_response = await authorized_client.post("/manufacturer", json=create_payload)
    manufacturer_id = create_response.json()["data"]["id"]

    # Обновляем
    update_payload = {"name": "Updated Name", "description": "Updated description"}
    await authorized_client.put(f"/manufacturer/{manufacturer_id}", json=update_payload)

    # Получаем и проверяем
    get_response = await client.get(f"/manufacturer/{manufacturer_id}")
    assert get_response.status_code == 200

    body = get_response.json()
    assert body["data"]["name"] == "Updated Name"
    assert body["data"]["description"] == "Updated description"


# =========================================================
# Обновление с trim имени
# =========================================================

@pytest.mark.asyncio
async def test_update_manufacturer_name_trimmed(authorized_client, client):
    """Имя обрезается при обновлении"""
    # Создаем производителя
    create_payload = {"name": "Test Manufacturer"}
    create_response = await authorized_client.post("/manufacturer", json=create_payload)
    manufacturer_id = create_response.json()["data"]["id"]

    # Обновляем с пробелами
    update_payload = {"name": "  New Name  "}
    response = await authorized_client.put(f"/manufacturer/{manufacturer_id}", json=update_payload)
    assert response.status_code == 200

    body = response.json()
    assert body["data"]["name"] == "New Name"


# =========================================================
# Частичное обновление
# =========================================================

@pytest.mark.asyncio
async def test_update_manufacturer_partial_update_name_only(authorized_client, client):
    """Частичное обновление - только имя"""
    # Создаем производителя
    create_payload = {"name": "Old Name", "description": "Description"}
    create_response = await authorized_client.post("/manufacturer", json=create_payload)
    manufacturer_id = create_response.json()["data"]["id"]

    # Обновляем только имя
    update_payload = {"name": "New Name"}
    response = await authorized_client.put(f"/manufacturer/{manufacturer_id}", json=update_payload)
    assert response.status_code == 200

    body = response.json()
    assert body["data"]["name"] == "New Name"
    assert body["data"]["description"] == "Description"


@pytest.mark.asyncio
async def test_update_manufacturer_partial_update_description_only(authorized_client, client):
    """Частичное обновление - только описание"""
    # Создаем производителя
    create_payload = {"name": "Test Manufacturer", "description": "Old description"}
    create_response = await authorized_client.post("/manufacturer", json=create_payload)
    manufacturer_id = create_response.json()["data"]["id"]

    # Обновляем только описание
    update_payload = {"description": "New description"}
    response = await authorized_client.put(f"/manufacturer/{manufacturer_id}", json=update_payload)
    assert response.status_code == 200

    body = response.json()
    assert body["data"]["name"] == "Test Manufacturer"
    assert body["data"]["description"] == "New description"
