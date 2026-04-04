import json

import pytest


async def _create_category(authorized_client, name: str) -> int:
    response = await authorized_client.post(
        "/category",
        json={"name": name},
    )
    assert response.status_code == 200
    return response.json()["data"]["id"]


async def _create_product_with_attrs(
    authorized_client,
    *,
    name: str,
    category_id: int,
    attrs: list[dict],
) -> int:
    """Создаёт товар с произвольными атрибутами.
    
    Каждый атрибут: {"name": "...", "value": "...", "is_filterable": bool, "is_groupable": bool}
    """
    response = await authorized_client.post(
        "/product",
        data={
            "name": name,
            "price": "1000.00",
            "category_id": str(category_id),
            "attributes_json": json.dumps(attrs),
        },
    )
    assert response.status_code == 200
    return response.json()["data"]["id"]


@pytest.mark.asyncio
async def test_related_products_by_id(authorized_client, client):
    category_id = await _create_category(authorized_client, "iPhone 15 Pro")

    base_id = await _create_product_with_attrs(
        authorized_client,
        name="iPhone 15 Pro 256 Гб Красный",
        category_id=category_id,
        attrs=[
            {"name": "Память", "value": "256 Гб", "is_filterable": True, "is_groupable": True},
            {"name": "Цвет", "value": "Красный", "is_filterable": True, "is_groupable": True},
        ],
    )

    await _create_product_with_attrs(
        authorized_client,
        name="iPhone 15 Pro 256 Гб Черный",
        category_id=category_id,
        attrs=[
            {"name": "Память", "value": "256 Гб", "is_filterable": True, "is_groupable": True},
            {"name": "Цвет", "value": "Черный", "is_filterable": True, "is_groupable": True},
        ],
    )
    await _create_product_with_attrs(
        authorized_client,
        name="iPhone 15 Pro 256 Гб Зеленый",
        category_id=category_id,
        attrs=[
            {"name": "Память", "value": "256 Гб", "is_filterable": True, "is_groupable": True},
            {"name": "Цвет", "value": "Зеленый", "is_filterable": True, "is_groupable": True},
        ],
    )
    await _create_product_with_attrs(
        authorized_client,
        name="iPhone 15 Pro 512 Гб Красный",
        category_id=category_id,
        attrs=[
            {"name": "Память", "value": "512 Гб", "is_filterable": True, "is_groupable": True},
            {"name": "Цвет", "value": "Красный", "is_filterable": True, "is_groupable": True},
        ],
    )

    response = await client.get(f"/product/related/variants?product_id={base_id}")

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True

    items = body["data"]["items"]
    names = [item["name"] for item in items]

    # С новой логикой: ВСЕ groupable-атрибуты должны совпадать по значению
    # У базового товара: Память=256 Гб, Цвет=Красный
    # Только товар с обоими совпадающими атрибутами должен вернуться
    assert "iPhone 15 Pro 256 Гб Красный" in names
    # Товары с другим цветом или памятью НЕ должны возвращаться
    assert "iPhone 15 Pro 256 Гб Черный" not in names
    assert "iPhone 15 Pro 256 Гб Зеленый" not in names
    assert "iPhone 15 Pro 512 Гб Красный" not in names

    # Проверяем, что у всех товаров есть изображения с ordering
    for item in items:
        assert "images" in item
        for image in item["images"]:
            assert "ordering" in image
        # Проверяем наличие связанных данных
        assert "category" in item
        assert "supplier" in item
        # Категория должна быть заполнена
        assert item["category"] is not None
        assert item["category"]["id"] == category_id


@pytest.mark.asyncio
async def test_related_products_by_name(authorized_client, client):
    category_id = await _create_category(authorized_client, "iPhone 14 Pro")

    await _create_product_with_attrs(
        authorized_client,
        name="iPhone 14 Pro 128 Гб Синий",
        category_id=category_id,
        attrs=[
            {"name": "Память", "value": "128 Гб", "is_filterable": True, "is_groupable": True},
            {"name": "Цвет", "value": "Синий", "is_filterable": True, "is_groupable": True},
        ],
    )
    await _create_product_with_attrs(
        authorized_client,
        name="iPhone 14 Pro 128 Гб Черный",
        category_id=category_id,
        attrs=[
            {"name": "Память", "value": "128 Гб", "is_filterable": True, "is_groupable": True},
            {"name": "Цвет", "value": "Черный", "is_filterable": True, "is_groupable": True},
        ],
    )

    response = await client.get(
        "/product/related/variants?name=iPhone 14 Pro 128 Гб Синий"
    )

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    # Только товар с Память=128 Гб И Цвет=Синий
    assert body["data"]["total"] == 1
    names = [item["name"] for item in body["data"]["items"]]
    assert "iPhone 14 Pro 128 Гб Синий" in names


@pytest.mark.asyncio
async def test_related_products_400_without_lookup(client):
    response = await client.get("/product/related/variants")

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "product_related_lookup_required"


@pytest.mark.asyncio
async def test_related_products_all_groupable_must_match(authorized_client, client):
    """
    Тест проверяет, что ВСЕ groupable-атрибуты должны совпадать по значению.
    
    Сценарий:
    - Базовый товар: Серия=series 9 (groupable), Цвет=золотой (groupable)
    - Товар 1: Серия=series 9 (groupable), Цвет=розовый (groupable) — НЕ совпадает по цвету
    - Товар 2: Серия=series 9 (groupable), Цвет=золотой (groupable) — совпадает полностью
    - Товар 3: Серия=ultra (groupable), Цвет=золотой (groupable) — НЕ совпадает по серии
    
    Ожидаем: только базовый товар и Товар 2
    """
    category_id = await _create_category(authorized_client, "Apple Watch")

    base_id = await _create_product_with_attrs(
        authorized_client,
        name="Watch Series 9 Золотой",
        category_id=category_id,
        attrs=[
            {"name": "Серия", "value": "series 9", "is_filterable": True, "is_groupable": True},
            {"name": "Цвет", "value": "золотой", "is_filterable": True, "is_groupable": True},
            {"name": "Размер", "value": "41 мм", "is_filterable": True, "is_groupable": False},
        ],
    )

    # Товар 1: совпадает серия, но не цвет
    await _create_product_with_attrs(
        authorized_client,
        name="Watch Series 9 Розовый",
        category_id=category_id,
        attrs=[
            {"name": "Серия", "value": "series 9", "is_filterable": True, "is_groupable": True},
            {"name": "Цвет", "value": "розовый", "is_filterable": True, "is_groupable": True},
            {"name": "Размер", "value": "41 мм", "is_filterable": True, "is_groupable": False},
        ],
    )

    # Товар 2: совпадает полностью
    await _create_product_with_attrs(
        authorized_client,
        name="Watch Series 9 Золотой Полный",
        category_id=category_id,
        attrs=[
            {"name": "Серия", "value": "series 9", "is_filterable": True, "is_groupable": True},
            {"name": "Цвет", "value": "золотой", "is_filterable": True, "is_groupable": True},
            {"name": "Размер", "value": "45 мм", "is_filterable": True, "is_groupable": False},
        ],
    )

    # Товар 3: совпадает цвет, но не серия
    await _create_product_with_attrs(
        authorized_client,
        name="Watch Ultra Золотой",
        category_id=category_id,
        attrs=[
            {"name": "Серия", "value": "ultra", "is_filterable": True, "is_groupable": True},
            {"name": "Цвет", "value": "золотой", "is_filterable": True, "is_groupable": True},
            {"name": "Размер", "value": "49 мм", "is_filterable": True, "is_groupable": False},
        ],
    )

    response = await client.get(f"/product/related/variants?product_id={base_id}")

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True

    items = body["data"]["items"]
    names = [item["name"] for item in items]

    # Должны вернуться: базовый товар и Товар 2 (полное совпадение groupable)
    assert "Watch Series 9 Золотой" in names
    assert "Watch Series 9 Золотой Полный" in names
    # НЕ должны вернуться: Товар 1 и Товар 3
    assert "Watch Series 9 Розовый" not in names
    assert "Watch Ultra Золотой" not in names


@pytest.mark.asyncio
async def test_related_products_ignores_non_groupable_attrs(authorized_client, client):
    """
    Тест проверяет, что non-groupable атрибуты НЕ влияют на фильтрацию.
    
    Сценарий:
    - Базовый товар: Цвет=красный (groupable), Размер=41 (non-groupable)
    - Товар 1: Цвет=красный (groupable), Размер=45 (non-groupable) — должен вернуться
    - Товар 2: Цвет=синий (groupable), Размер=41 (non-groupable) — НЕ должен вернуться
    """
    category_id = await _create_category(authorized_client, "Samsung Watch")

    base_id = await _create_product_with_attrs(
        authorized_client,
        name="Samsung Watch Красный 41",
        category_id=category_id,
        attrs=[
            {"name": "Цвет", "value": "красный", "is_filterable": True, "is_groupable": True},
            {"name": "Размер", "value": "41", "is_filterable": True, "is_groupable": False},
        ],
    )

    # Товар 1: совпадает цвет, отличается размер (non-groupable) — должен вернуться
    await _create_product_with_attrs(
        authorized_client,
        name="Samsung Watch Красный 45",
        category_id=category_id,
        attrs=[
            {"name": "Цвет", "value": "красный", "is_filterable": True, "is_groupable": True},
            {"name": "Размер", "value": "45", "is_filterable": True, "is_groupable": False},
        ],
    )

    # Товар 2: отличается цвет, совпадает размер — НЕ должен вернуться
    await _create_product_with_attrs(
        authorized_client,
        name="Samsung Watch Синий 41",
        category_id=category_id,
        attrs=[
            {"name": "Цвет", "value": "синий", "is_filterable": True, "is_groupable": True},
            {"name": "Размер", "value": "41", "is_filterable": True, "is_groupable": False},
        ],
    )

    response = await client.get(f"/product/related/variants?product_id={base_id}")

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True

    items = body["data"]["items"]
    names = [item["name"] for item in items]

    assert "Samsung Watch Красный 41" in names
    assert "Samsung Watch Красный 45" in names
    assert "Samsung Watch Синий 41" not in names
