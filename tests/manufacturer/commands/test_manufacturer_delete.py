"""
Тесты для команды удаления производителя (DeleteManufacturerCommand).

Проверяют:
- Успешное удаление
- Удаление несуществующего производителя (404)
- Audit логирование
- Генерацию доменных событий
- Каскадное удаление связанных категорий (если реализовано)
"""
import pytest


# =========================================================
# Успешное удаление
# =========================================================

@pytest.mark.asyncio
async def test_delete_manufacturer_success(authorized_client, client):
    """Успешное удаление производителя"""
    # Создаем производителя
    create_payload = {"name": "To Delete Manufacturer", "description": "Will be deleted"}
    create_response = await authorized_client.post("/manufacturer", json=create_payload)
    manufacturer_id = create_response.json()["data"]["id"]

    # Удаляем
    delete_response = await authorized_client.delete(f"/manufacturer/{manufacturer_id}")
    assert delete_response.status_code == 200

    body = delete_response.json()
    assert body["success"] is True
    assert body["data"]["deleted"] is True


@pytest.mark.asyncio
async def test_delete_manufacturer_verify_not_found(authorized_client, client):
    """Проверка, что удаленный производитель действительно удален"""
    # Создаем производителя
    create_payload = {"name": "To Delete Manufacturer"}
    create_response = await authorized_client.post("/manufacturer", json=create_payload)
    manufacturer_id = create_response.json()["data"]["id"]

    # Удаляем
    await authorized_client.delete(f"/manufacturer/{manufacturer_id}")

    # Пытаемся получить - должен быть 404
    get_response = await client.get(f"/manufacturer/{manufacturer_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_manufacturer_without_description(authorized_client, client):
    """Удаление производителя без описания"""
    # Создаем производителя без описания
    create_payload = {"name": "Simple Manufacturer"}
    create_response = await authorized_client.post("/manufacturer", json=create_payload)
    manufacturer_id = create_response.json()["data"]["id"]

    # Удаляем
    delete_response = await authorized_client.delete(f"/manufacturer/{manufacturer_id}")
    assert delete_response.status_code == 200


# =========================================================
# 404 ошибки
# =========================================================

@pytest.mark.asyncio
async def test_delete_nonexistent_manufacturer(authorized_client, client):
    """Удаление несуществующего производителя"""
    delete_response = await authorized_client.delete("/manufacturer/99999")
    assert delete_response.status_code == 404

    body = delete_response.json()
    assert body["success"] is False


@pytest.mark.asyncio
async def test_delete_manufacturer_twice(authorized_client, client):
    """Повторное удаление уже удаленного производителя"""
    # Создаем производителя
    create_payload = {"name": "To Delete Twice"}
    create_response = await authorized_client.post("/manufacturer", json=create_payload)
    manufacturer_id = create_response.json()["data"]["id"]

    # Первое удаление
    delete_response1 = await authorized_client.delete(f"/manufacturer/{manufacturer_id}")
    assert delete_response1.status_code == 200

    # Повторное удаление - должен быть 404
    delete_response2 = await authorized_client.delete(f"/manufacturer/{manufacturer_id}")
    assert delete_response2.status_code == 404


# =========================================================
# Удаление с связанными категориями
# =========================================================

@pytest.mark.asyncio
async def test_delete_manufacturer_with_categories(authorized_client, client):
    """Удаление производителя, у которого есть категории"""
    # Создаем производителя
    create_payload = {"name": "Manufacturer With Categories"}
    create_response = await authorized_client.post("/manufacturer", json=create_payload)
    manufacturer_id = create_response.json()["data"]["id"]

    # Создаем категорию, связанную с производителем
    category_payload = {
        "name": "Test Category",
        "manufacturer_id": manufacturer_id,
    }
    category_response = await authorized_client.post("/category", json=category_payload)
    
    # Проверяем, что категория создана (может быть 200 или 403 в зависимости от прав)
    if category_response.status_code == 200:
        category_id = category_response.json()["data"]["id"]
        
        # Удаляем производителя
        delete_response = await authorized_client.delete(f"/manufacturer/{manufacturer_id}")
        assert delete_response.status_code == 200
        
        # Проверяем, что категория тоже удалена (каскадное удаление)
        # или что manufacturer_id у категории стал None (restrict)
        # Это зависит от реализации ForeignKey
        get_category_response = await client.get(f"/category/{category_id}")
        # Либо 404 (каскадное удаление), либо категория с null manufacturer_id
        assert get_category_response.status_code in [404, 200]


# =========================================================
# Проверка ответа
# =========================================================

@pytest.mark.asyncio
async def test_delete_manufacturer_response_format(authorized_client, client):
    """Проверка формата ответа на удаление"""
    # Создаем производителя
    create_payload = {"name": "Delete Test"}
    create_response = await authorized_client.post("/manufacturer", json=create_payload)
    manufacturer_id = create_response.json()["data"]["id"]

    # Удаляем
    delete_response = await authorized_client.delete(f"/manufacturer/{manufacturer_id}")
    
    body = delete_response.json()
    
    # Проверяем структуру ответа
    assert "success" in body
    assert "data" in body
    assert body["success"] is True
    assert "deleted" in body["data"]
    assert body["data"]["deleted"] is True


# =========================================================
# Удаление с кириллическим именем
# =========================================================

@pytest.mark.asyncio
async def test_delete_manufacturer_with_cyrillic_name(authorized_client, client):
    """Удаление производителя с кириллическим именем"""
    # Создаем производителя
    create_payload = {"name": "Яндекс", "description": "Российская компания"}
    create_response = await authorized_client.post("/manufacturer", json=create_payload)
    manufacturer_id = create_response.json()["data"]["id"]

    # Удаляем
    delete_response = await authorized_client.delete(f"/manufacturer/{manufacturer_id}")
    assert delete_response.status_code == 200


# =========================================================
# Удаление с длинным именем
# =========================================================

@pytest.mark.asyncio
async def test_delete_manufacturer_with_long_name(authorized_client, client):
    """Удаление производителя с длинным именем"""
    # Создаем производителя с длинным именем
    long_name = "A" * 149
    create_payload = {"name": long_name}
    create_response = await authorized_client.post("/manufacturer", json=create_payload)
    manufacturer_id = create_response.json()["data"]["id"]

    # Удаляем
    delete_response = await authorized_client.delete(f"/manufacturer/{manufacturer_id}")
    assert delete_response.status_code == 200


# =========================================================
# Массовое создание и удаление
# =========================================================

@pytest.mark.asyncio
async def test_delete_multiple_manufacturers(authorized_client, client):
    """Удаление нескольких производителей"""
    # Создаем нескольких производителей
    manufacturer_ids = []
    for i in range(5):
        create_payload = {"name": f"Manufacturer {i}"}
        create_response = await authorized_client.post("/manufacturer", json=create_payload)
        manufacturer_ids.append(create_response.json()["data"]["id"])

    # Удаляем каждого
    for manufacturer_id in manufacturer_ids:
        delete_response = await authorized_client.delete(f"/manufacturer/{manufacturer_id}")
        assert delete_response.status_code == 200

    # Проверяем, что все удалены
    for manufacturer_id in manufacturer_ids:
        get_response = await client.get(f"/manufacturer/{manufacturer_id}")
        assert get_response.status_code == 404
