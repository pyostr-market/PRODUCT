"""
Интеграционные тесты для audit логов отзывов.
"""
import pytest


async def _create_product(client, name="Test Product"):
    """Хелпер для создания товара."""
    response = await client.post(
        "/product",
        data={"name": name, "price": "100.00"},
    )
    assert response.status_code == 200
    return response.json()["data"]


async def _create_review(client, product_id, rating=4, text="Test review"):
    """Хелпер для создания отзыва."""
    response = await client.post(
        "/reviews",
        data={
            "product_id": product_id,
            "rating": str(rating),
            "text": text,
        },
    )
    assert response.status_code == 200
    return response.json()["data"]


@pytest.mark.asyncio
async def test_review_audit_logs_200(authorized_client):
    """Проверка audit логов для отзывов"""
    product = await _create_product(authorized_client, "Audit Product")
    product_id = product["id"]

    # Создаём отзыв
    review = await _create_review(authorized_client, product_id, rating=4, text="Test")
    review_id = review["id"]

    # Обновляем отзыв
    await authorized_client.put(
        f"/reviews/{review_id}",
        data={
            "rating": "5",
            "text": "Updated",
        },
    )

    # Запрашиваем audit логи
    response = await authorized_client.get(f"/reviews/admin/audit?review_id={review_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    data = body["data"]
    assert data["total"] >= 2
    assert len(data["items"]) >= 2

    actions = [item["action"] for item in data["items"]]
    assert "create" in actions
    assert "update" in actions


@pytest.mark.asyncio
async def test_review_audit_logs_after_delete(authorized_client):
    """Audit логи после удаления отзыва"""
    product = await _create_product(authorized_client, "Audit Delete Product")
    product_id = product["id"]

    review = await _create_review(authorized_client, product_id, rating=4, text="Test")
    review_id = review["id"]

    # Удаляем отзыв
    await authorized_client.delete(f"/reviews/{review_id}")

    # Запрашиваем audit логи — после удаления review_id становится NULL (SET NULL)
    # Поэтому фильтруем по user_id
    response = await authorized_client.get(f"/reviews/admin/audit?user_id=1")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    data = body["data"]
    assert data["total"] >= 2

    actions = [item["action"] for item in data["items"]]
    assert "create" in actions
    assert "delete" in actions


@pytest.mark.asyncio
async def test_review_audit_logs_filter_by_action(authorized_client):
    """Фильтрация audit логов по action"""
    product = await _create_product(authorized_client, "Audit Filter Product")
    product_id = product["id"]

    review = await _create_review(authorized_client, product_id, rating=4, text="Test")
    review_id = review["id"]

    # Фильтруем по action=create
    response = await authorized_client.get(
        f"/reviews/admin/audit?review_id={review_id}&action=create"
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total"] == 1
    assert data["items"][0]["action"] == "create"


@pytest.mark.asyncio
async def test_review_audit_logs_filter_by_user(authorized_client):
    """Фильтрация audit логов по user_id"""
    product = await _create_product(authorized_client, "Audit User Product")
    product_id = product["id"]

    await _create_review(authorized_client, product_id, rating=4, text="Test")

    response = await authorized_client.get(
        f"/reviews/admin/audit?user_id=1"
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total"] >= 1
    assert all(item["user_id"] == 1 for item in data["items"])


@pytest.mark.asyncio
async def test_review_audit_logs_contains_data(authorized_client):
    """Audit логи содержат old_data и new_data"""
    product = await _create_product(authorized_client, "Audit Data Product")
    product_id = product["id"]

    review = await _create_review(authorized_client, product_id, rating=3, text="Old")
    review_id = review["id"]

    # Обновляем
    await authorized_client.put(
        f"/reviews/{review_id}",
        data={
            "rating": "5",
            "text": "New",
        },
    )

    # Получаем audit логи
    response = await authorized_client.get(
        f"/reviews/admin/audit?review_id={review_id}&action=update"
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total"] >= 1

    update_log = data["items"][0]
    assert update_log["action"] == "update"
    assert update_log["old_data"] is not None
    assert update_log["new_data"] is not None
    assert update_log["old_data"]["rating"] in ("3", "3.0")
    assert update_log["new_data"]["rating"] in ("5", "5.0")
