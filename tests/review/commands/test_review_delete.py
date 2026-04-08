"""
Интеграционные тесты для команды удаления отзыва.
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
async def test_delete_review_success_200(authorized_client):
    """Успешное удаление отзыва"""
    product = await _create_product(authorized_client, "Delete Product")
    product_id = product["id"]
    review = await _create_review(authorized_client, product_id, rating=4, text="Delete me")
    review_id = review["id"]

    response = await authorized_client.delete(f"/reviews/{review_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["deleted"] is True


@pytest.mark.asyncio
async def test_delete_review_not_found_404(authorized_client):
    """Удаление несуществующего отзыва"""
    response = await authorized_client.delete("/reviews/999999")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_review_updates_product_rating(authorized_client):
    """После удаления отзыва рейтинг товара пересчитывается"""
    product = await _create_product(authorized_client, "Delete Rating Product")
    product_id = product["id"]

    # Создаём отзыв
    review = await _create_review(authorized_client, product_id, rating=4, text="Test")
    review_id = review["id"]

    # Удаляем отзыв
    response = await authorized_client.delete(f"/reviews/{review_id}")
    assert response.status_code == 200

    # Проверяем рейтинг товара — должно быть None/0
    product_resp = await authorized_client.get(f"/product/{product_id}")
    product_data = product_resp.json()["data"]
    rating = product_data.get("rating")
    assert rating is not None
    assert rating["count"] == 0
    assert rating["value"] is None


@pytest.mark.asyncio
async def test_delete_review_then_get_404(authorized_client):
    """После удаления отзыв нельзя получить"""
    product = await _create_product(authorized_client, "Delete Then Get Product")
    product_id = product["id"]
    review = await _create_review(authorized_client, product_id, rating=4, text="Delete me")
    review_id = review["id"]

    # Удаляем
    await authorized_client.delete(f"/reviews/{review_id}")

    # Пытаемся получить
    response = await authorized_client.get(f"/reviews/{review_id}")
    assert response.status_code == 404
