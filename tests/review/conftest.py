"""Fixtures для тестов модуля отзывов."""

import pytest_asyncio


@pytest_asyncio.fixture
async def test_product_for_reviews(authorized_client):
    """Создаёт тестовый товар для отзывов."""
    response = await authorized_client.post(
        "/product",
        data={
            "name": "Товар для отзывов",
            "description": "Тестовый товар для проверки отзывов",
            "price": "5000.00",
        },
    )
    assert response.status_code == 200
    yield response.json()["data"]
