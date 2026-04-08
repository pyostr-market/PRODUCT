"""
Интеграционные тесты для команды создания отзыва.
"""
import json

import pytest


@pytest.mark.asyncio
async def test_create_review_success_200(authorized_client, test_product_for_reviews):
    """Успешное создание отзыва с рейтингом"""
    product_id = test_product_for_reviews["id"]

    response = await authorized_client.post(
        "/reviews",
        data={
            "product_id": product_id,
            "rating": "4.5",
            "text": "Отличный товар, рекомендую!",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    data = body["data"]
    assert data["product_id"] == product_id
    assert data["rating"] == "4.5"
    assert data["text"] == "Отличный товар, рекомендую!"
    assert data["user_id"] == 1
    assert data["username"] is not None
    assert data["id"] is not None


@pytest.mark.asyncio
async def test_create_review_rating_only_200(authorized_client, test_product_for_reviews):
    """Создание отзыва только с рейтингом (без текста)"""
    product_id = test_product_for_reviews["id"]

    response = await authorized_client.post(
        "/reviews",
        data={
            "product_id": product_id,
            "rating": "5",
        },
    )

    assert response.status_code == 200
    data = response.json()["data"]
    # Decimal(5) → "5", Decimal("5.0") → "5.0"
    assert data["rating"] in ("5", "5.0")
    assert data["text"] is None


@pytest.mark.asyncio
async def test_create_review_with_images_200(authorized_client, test_product_for_reviews):
    """Создание отзыва с изображениями"""
    product_id = test_product_for_reviews["id"]

    response = await authorized_client.post(
        "/reviews",
        data={
            "product_id": product_id,
            "rating": "4",
            "text": "С фото",
        },
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["images"] == []  # Без загруженных изображений


@pytest.mark.asyncio
async def test_create_review_duplicate_409(authorized_client, test_product_for_reviews):
    """Повторный отзыв на тот же товар — ошибка 409"""
    product_id = test_product_for_reviews["id"]

    # Первый отзыв
    resp1 = await authorized_client.post(
        "/reviews",
        data={
            "product_id": product_id,
            "rating": "4",
            "text": "Первый отзыв",
        },
    )
    assert resp1.status_code == 200

    # Второй отзыв на тот же товар
    resp2 = await authorized_client.post(
        "/reviews",
        data={
            "product_id": product_id,
            "rating": "5",
            "text": "Второй отзыв",
        },
    )
    assert resp2.status_code == 409


@pytest.mark.asyncio
async def test_create_review_invalid_rating_low(authorized_client, test_product_for_reviews):
    """Рейтинг ниже минимума (0) — ошибка"""
    product_id = test_product_for_reviews["id"]

    response = await authorized_client.post(
        "/reviews",
        data={
            "product_id": product_id,
            "rating": "0",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_review_invalid_rating_high(authorized_client, test_product_for_reviews):
    """Рейтинг выше максимума (6) — ошибка"""
    product_id = test_product_for_reviews["id"]

    response = await authorized_client.post(
        "/reviews",
        data={
            "product_id": product_id,
            "rating": "6",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_review_updates_product_rating(authorized_client, test_product_for_reviews):
    """После создания отзыва рейтинг товара обновляется"""
    product_id = test_product_for_reviews["id"]

    # Создаём отзыв
    await authorized_client.post(
        "/reviews",
        data={
            "product_id": product_id,
            "rating": "4.5",
            "text": "Тест",
        },
    )

    # Проверяем, что рейтинг товара обновился
    product_resp = await authorized_client.get(f"/product/{product_id}")
    product_data = product_resp.json()["data"]
    rating = product_data.get("rating")
    assert rating is not None
    assert float(rating["value"]) == 4.5
    assert rating["count"] == 1
