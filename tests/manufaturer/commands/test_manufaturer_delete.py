import pytest

# =========================================================
# 200 — успешное удаление
# =========================================================

@pytest.mark.asyncio
async def test_delete_manufacturer_200(authorized_client):
    # 1️⃣ Создаём производителя
    create = await authorized_client.post(
        "/manufacturer",
        json={
            "name": "Delete Me",
            "description": "To be deleted"
        }
    )

    assert create.status_code == 200
    manufacturer_id = create.json()["data"]["id"]

    # 2️⃣ Удаляем
    response = await authorized_client.delete(f"/manufacturer/{manufacturer_id}")

    assert response.status_code == 200

    body = response.json()

    # Проверяем контракт API
    assert body["success"] is True
    assert body["data"]["deleted"] is True

    # 3️⃣ Проверяем, что объект реально удалён
    get_response = await authorized_client.get(f"/manufacturer/{manufacturer_id}")

    assert get_response.status_code == 404

    get_body = get_response.json()
    assert get_body["success"] is False
    assert get_body["error"]["code"] == "manufacturer_not_found"


# =========================================================
# 404 — удаление несуществующего производителя
# =========================================================

@pytest.mark.asyncio
async def test_delete_manufacturer_404_not_found(authorized_client):
    response = await authorized_client.delete("/manufacturer/999999")

    assert response.status_code == 404

    body = response.json()

    assert body["success"] is False
    assert body["error"]["code"] == "manufacturer_not_found"


# =========================================================
# Повторное удаление → 404
# =========================================================

@pytest.mark.asyncio
async def test_delete_manufacturer_second_time_404(authorized_client):
    # Создаём
    create = await authorized_client.post(
        "/manufacturer",
        json={
            "name": "Delete Twice",
            "description": "Test"
        }
    )

    manufacturer_id = create.json()["data"]["id"]

    # Первый delete
    first_delete = await authorized_client.delete(f"/manufacturer/{manufacturer_id}")
    assert first_delete.status_code == 200

    # Второй delete
    second_delete = await authorized_client.delete(f"/manufacturer/{manufacturer_id}")

    assert second_delete.status_code == 404

    body = second_delete.json()
    assert body["success"] is False
    assert body["error"]["code"] == "manufacturer_not_found"