"""
Интеграционные тесты для запросов получения отзывов.
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


# =========================================================
# GET /reviews/{review_id}
# =========================================================

class TestGetReview:

    @pytest.mark.asyncio
    async def test_get_review_success_200(self, authorized_client):
        """Получение отзыва по ID"""
        product = await _create_product(authorized_client, "Product For Review")
        product_id = product["id"]
        review = await _create_review(
            authorized_client, product_id, rating=4.5, text="Great product!"
        )
        review_id = review["id"]

        response = await authorized_client.get(f"/reviews/{review_id}")

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True

        data = body["data"]
        assert data["id"] == review_id
        assert data["product_id"] == product_id
        assert data["rating"] in ("4.5",)
        assert data["text"] == "Great product!"
        assert data["user_id"] == 1
        assert "username" in data

    @pytest.mark.asyncio
    async def test_get_review_not_found_404(self, authorized_client):
        """Получение несуществующего отзыва"""
        response = await authorized_client.get("/reviews/999999")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_review_with_no_text(self, authorized_client):
        """Получение отзыва без текста (только рейтинг)"""
        product = await _create_product(authorized_client, "Product No Text")
        product_id = product["id"]
        review = await _create_review(authorized_client, product_id, rating=5, text=None)

        response = await authorized_client.get(f"/reviews/{review['id']}")

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["text"] is None or data["text"] == ""
        assert data["rating"] in ("5", "5.0")


# =========================================================
# GET /reviews/product/{product_id}
# =========================================================

class TestGetReviewsByProduct:

    @pytest.mark.asyncio
    async def test_get_reviews_empty_200(self, authorized_client):
        """Получение отзывов для товара без отзывов"""
        product = await _create_product(authorized_client, "Product No Reviews")
        product_id = product["id"]

        response = await authorized_client.get(f"/reviews/product/{product_id}")

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True

        data = body["data"]
        assert data["total"] == 0
        assert data["items"] == []
        assert data["average_rating"] is None

    @pytest.mark.asyncio
    async def test_get_reviews_with_data_200(self, authorized_client):
        """Получение отзывов для товара с отзывами"""
        product = await _create_product(authorized_client, "Product With Reviews")
        product_id = product["id"]

        await _create_review(authorized_client, product_id, rating=5, text="Excellent")

        response = await authorized_client.get(f"/reviews/product/{product_id}")

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True

        data = body["data"]
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["text"] == "Excellent"

    @pytest.mark.asyncio
    async def test_get_reviews_average_rating(self, authorized_client):
        """Проверка среднего рейтинга"""
        product = await _create_product(authorized_client, "Product For Average")
        product_id = product["id"]

        # Один отзыв с рейтингом 4 → average = 4.0
        await _create_review(authorized_client, product_id, rating=4)

        response = await authorized_client.get(f"/reviews/product/{product_id}")

        assert response.status_code == 200
        data = response.json()["data"]

        assert data["average_rating"] == pytest.approx(4.0, abs=0.01)

    @pytest.mark.asyncio
    async def test_get_reviews_different_products(self, authorized_client):
        """Отзывы для разных товаров не пересекаются"""
        # Создаём два товара
        resp1 = await authorized_client.post(
            "/product",
            data={"name": "Product A", "price": "100.00"},
        )
        product_a_id = resp1.json()["data"]["id"]

        resp2 = await authorized_client.post(
            "/product",
            data={"name": "Product B", "price": "200.00"},
        )
        product_b_id = resp2.json()["data"]["id"]

        # Создаём отзывы (от одного пользователя — по одному на товар)
        await _create_review(authorized_client, product_a_id, rating=5, text="Review for A")
        # Для B нужен другой пользователь, но мы просто проверим что A не содержит B

        # Проверяем отзывы для A
        resp_a = await authorized_client.get(f"/reviews/product/{product_a_id}")
        data_a = resp_a.json()["data"]
        assert data_a["total"] == 1
        assert data_a["items"][0]["text"] == "Review for A"

        # Проверяем отзывы для B (пусто)
        resp_b = await authorized_client.get(f"/reviews/product/{product_b_id}")
        data_b = resp_b.json()["data"]
        assert data_b["total"] == 0
