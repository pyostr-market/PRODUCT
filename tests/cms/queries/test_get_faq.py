"""Тесты для получения FAQ (FAQ Queries)."""

import pytest

from src.cms.api.schemas.faq_schemas import FaqReadSchema


@pytest.mark.asyncio
async def test_get_all_faq_200(authorized_client, client):
    """Тест получения всех активных FAQ."""
    # Создаём несколько FAQ
    await authorized_client.post(
        "/cms/faq/admin",
        json={"question": "Q1?", "answer": "A1", "category": "cat1"},
    )
    await authorized_client.post(
        "/cms/faq/admin",
        json={"question": "Q2?", "answer": "A2", "category": "cat1"},
    )
    await authorized_client.post(
        "/cms/faq/admin",
        json={"question": "Q3?", "answer": "A3", "category": "cat2"},
    )

    # Получаем все FAQ
    response = await client.get("/cms/faq")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["total"] == 3
    assert len(body["data"]["items"]) == 3


@pytest.mark.asyncio
async def test_get_faq_by_id_200(authorized_client, client):
    """Тест получения FAQ по ID."""
    # Создаём FAQ
    create_response = await authorized_client.post(
        "/cms/faq/admin",
        json={"question": "Test Q?", "answer": "Test A", "category": "test"},
    )
    faq_id = create_response.json()["data"]["id"]

    # Получаем FAQ по ID
    response = await client.get(f"/cms/faq/admin/{faq_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["id"] == faq_id
    assert body["data"]["question"] == "Test Q?"


@pytest.mark.asyncio
async def test_get_faq_by_id_404_not_found(authorized_client):
    """Тест получения несуществующего FAQ по ID."""
    response = await authorized_client.get("/cms/faq/admin/999999")

    assert response.status_code == 404
    body = response.json()
    assert body.get("success") is False


@pytest.mark.asyncio
async def test_search_faq_200(authorized_client, client):
    """Тест поиска FAQ по вопросу и ответу."""
    # Создаём FAQ
    await authorized_client.post(
        "/cms/faq/admin",
        json={"question": "Как оформить заказ?", "answer": "Для оформления нажмите кнопку", "category": "orders"},
    )
    await authorized_client.post(
        "/cms/faq/admin",
        json={"question": "Как вернуть товар?", "answer": "Для возврата заполните форму", "category": "returns"},
    )

    # Поиск по вопросу
    response = await client.get("/cms/faq/admin/search?q=оформить")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["total"] == 1
    assert "Как оформить заказ?" in body["data"]["items"][0]["question"]

    # Поиск по ответу
    response = await client.get("/cms/faq/admin/search?q=кнопку")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["total"] == 1

    # Поиск с пустым запросом (должны вернуться все FAQ)
    response = await client.get("/cms/faq/admin/search")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["total"] == 2


@pytest.mark.asyncio
async def test_search_faq_with_pagination(authorized_client, client):
    """Тест поиска FAQ с пагинацией."""
    # Создаём FAQ
    for i in range(10):
        await authorized_client.post(
            "/cms/faq/admin",
            json={"question": f"Вопрос {i}?", "answer": f"Ответ {i}", "category": "test"},
        )

    # Поиск с пагинацией
    response = await client.get("/cms/faq/admin/search?q=Вопрос&limit=5&offset=0")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["total"] == 10
    assert len(body["data"]["items"]) == 5


@pytest.mark.asyncio
async def test_get_all_faq_with_pagination(authorized_client, client):
    """Тест получения всех FAQ с пагинацией."""
    # Создаём FAQ
    for i in range(15):
        await authorized_client.post(
            "/cms/faq/admin",
            json={"question": f"Q{i}?", "answer": f"A{i}", "category": "cat"},
        )

    # Получаем с пагинацией
    response = await client.get("/cms/faq?limit=5&offset=0")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["total"] == 15
    assert len(body["data"]["items"]) == 5


@pytest.mark.asyncio
async def test_get_faq_by_category(authorized_client, client):
    """Тест получения FAQ по категории."""
    # Создаём FAQ в разных категориях
    await authorized_client.post(
        "/cms/faq/admin",
        json={"question": "Q1?", "answer": "A1", "category": "returns"},
    )
    await authorized_client.post(
        "/cms/faq/admin",
        json={"question": "Q2?", "answer": "A2", "category": "returns"},
    )
    await authorized_client.post(
        "/cms/faq/admin",
        json={"question": "Q3?", "answer": "A3", "category": "shipping"},
    )

    # Получаем FAQ по категории
    response = await client.get("/cms/faq?category=returns")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["total"] == 2
    assert all(f["category"] == "returns" for f in body["data"]["items"])


@pytest.mark.asyncio
async def test_get_faq_excludes_inactive(authorized_client, client):
    """Тест что неактивные FAQ не возвращаются."""
    # Создаём активный FAQ
    await authorized_client.post(
        "/cms/faq/admin",
        json={"question": "Active?", "answer": "Yes", "is_active": True},
    )
    # Создаём неактивный FAQ
    await authorized_client.post(
        "/cms/faq/admin",
        json={"question": "Inactive?", "answer": "No", "is_active": False},
    )

    # Получаем все FAQ (должен вернуться только активный)
    response = await client.get("/cms/faq")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["total"] == 1
    assert body["data"]["items"][0]["question"] == "Active?"


@pytest.mark.asyncio
async def test_get_faq_categories_200(authorized_client, client):
    """Тест получения списка категорий FAQ."""
    # Создаём FAQ в разных категориях
    await authorized_client.post(
        "/cms/faq/admin",
        json={"question": "Q1?", "answer": "A1", "category": "returns"},
    )
    await authorized_client.post(
        "/cms/faq/admin",
        json={"question": "Q2?", "answer": "A2", "category": "shipping"},
    )
    await authorized_client.post(
        "/cms/faq/admin",
        json={"question": "Q3?", "answer": "A3", "category": "returns"},
    )
    # FAQ без категории
    await authorized_client.post(
        "/cms/faq/admin",
        json={"question": "Q4?", "answer": "A4"},
    )

    # Получаем категории
    response = await client.get("/cms/faq/categories")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    categories = body["data"]["categories"]
    assert "returns" in categories
    assert "shipping" in categories
    assert len(categories) == 2  # Без None категории


@pytest.mark.asyncio
async def test_get_faq_sorted_by_order(authorized_client, client):
    """Тест сортировки FAQ по порядку."""
    # Создаём FAQ в разном порядке
    await authorized_client.post(
        "/cms/faq/admin",
        json={"question": "Q3?", "answer": "A3", "category": "cat", "order": 2},
    )
    await authorized_client.post(
        "/cms/faq/admin",
        json={"question": "Q1?", "answer": "A1", "category": "cat", "order": 0},
    )
    await authorized_client.post(
        "/cms/faq/admin",
        json={"question": "Q2?", "answer": "A2", "category": "cat", "order": 1},
    )

    # Получаем FAQ
    response = await client.get("/cms/faq?category=cat")

    assert response.status_code == 200
    body = response.json()
    questions = [f["question"] for f in body["data"]["items"]]
    assert questions == ["Q1?", "Q2?", "Q3?"]
