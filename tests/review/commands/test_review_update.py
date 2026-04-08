"""
Интеграционные тесты для команды обновления отзыва.
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
async def test_update_review_rating_200(authorized_client):
    """Обновление рейтинга отзыва"""
    product = await _create_product(authorized_client, "Update Rating Product")
    product_id = product["id"]
    review = await _create_review(authorized_client, product_id, rating=3, text="Test")
    review_id = review["id"]

    response = await authorized_client.put(
        f"/reviews/{review_id}",
        data={
            "rating": "5",
        },
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["rating"] in ("5", "5.0")
    assert data["text"] == "Test"


@pytest.mark.asyncio
async def test_update_review_text_200(authorized_client):
    """Обновление текста отзыва"""
    product = await _create_product(authorized_client, "Update Text Product")
    product_id = product["id"]
    review = await _create_review(authorized_client, product_id, rating=4, text="Old text")
    review_id = review["id"]

    response = await authorized_client.put(
        f"/reviews/{review_id}",
        data={
            "text": "Updated text",
        },
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["text"] == "Updated text"
    assert data["rating"] in ("4", "4.0")


@pytest.mark.asyncio
async def test_update_review_both_fields_200(authorized_client):
    """Обновление и рейтинга и текста"""
    product = await _create_product(authorized_client, "Update Both Product")
    product_id = product["id"]
    review = await _create_review(authorized_client, product_id, rating=3, text="Old")
    review_id = review["id"]

    response = await authorized_client.put(
        f"/reviews/{review_id}",
        data={
            "rating": "4.5",
            "text": "New text",
        },
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["rating"] == "4.5"
    assert data["text"] == "New text"


@pytest.mark.asyncio
async def test_update_review_not_found_404(authorized_client):
    """Обновление несуществующего отзыва"""
    response = await authorized_client.put(
        "/reviews/999999",
        data={
            "rating": "4",
        },
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_review_updates_product_rating(authorized_client):
    """После обновления отзыва рейтинг товара пересчитывается"""
    product = await _create_product(authorized_client, "Update Rating Calc Product")
    product_id = product["id"]

    # Создаём отзыв с рейтингом 3
    review = await _create_review(authorized_client, product_id, rating=3, text="Test")
    review_id = review["id"]

    # Обновляем на 5
    response = await authorized_client.put(
        f"/reviews/{review_id}",
        data={
            "rating": "5",
        },
    )
    assert response.status_code == 200

    # Проверяем рейтинг товара
    product_resp = await authorized_client.get(f"/product/{product_id}")
    product_data = product_resp.json()["data"]
    rating = product_data.get("rating")
    assert rating is not None
    assert float(rating["value"]) == 5.0
    assert rating["count"] == 1


@pytest.mark.asyncio
async def test_update_review_invalid_rating(authorized_client):
    """Обновление на невалидный рейтинг"""
    product = await _create_product(authorized_client, "Update Invalid Product")
    product_id = product["id"]
    review = await _create_review(authorized_client, product_id, rating=4, text="Test")
    review_id = review["id"]

    response = await authorized_client.put(
        f"/reviews/{review_id}",
        data={
            "rating": "6",
        },
    )

    assert response.status_code == 422
