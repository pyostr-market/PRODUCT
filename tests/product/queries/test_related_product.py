import json

import pytest

JPEG_BYTES = b"\xff\xd8\xff\xe0category-image"


async def _create_category(authorized_client, name: str) -> int:
    response = await authorized_client.post(
        "/category",
        data={
            "name": name,
            "orderings": "0",
        },
        files=[("images", ("test.jpg", JPEG_BYTES, "image/jpeg"))],
    )
    assert response.status_code == 200
    return response.json()["data"]["id"]


async def _create_product(
    authorized_client,
    *,
    name: str,
    category_id: int,
    memory: str,
    color: str,
) -> int:
    response = await authorized_client.post(
        "/product",
        data={
            "name": name,
            "price": "1000.00",
            "category_id": str(category_id),
            "attributes_json": json.dumps(
                [
                    {"name": "Память", "value": memory, "is_filterable": True},
                    {"name": "Цвет", "value": color, "is_filterable": True},
                ]
            ),
        },
    )
    assert response.status_code == 200
    return response.json()["data"]["id"]


@pytest.mark.asyncio
async def test_related_products_by_id(authorized_client, client):
    category_id = await _create_category(authorized_client, "iPhone 15 Pro")

    base_id = await _create_product(
        authorized_client,
        name="iPhone 15 Pro 256 Гб Красный",
        category_id=category_id,
        memory="256 Гб",
        color="Красный",
    )

    await _create_product(
        authorized_client,
        name="iPhone 15 Pro 256 Гб Черный",
        category_id=category_id,
        memory="256 Гб",
        color="Черный",
    )
    await _create_product(
        authorized_client,
        name="iPhone 15 Pro 256 Гб Зеленый",
        category_id=category_id,
        memory="256 Гб",
        color="Зеленый",
    )
    await _create_product(
        authorized_client,
        name="iPhone 15 Pro 512 Гб Красный",
        category_id=category_id,
        memory="512 Гб",
        color="Красный",
    )

    response = await client.get(f"/product/related/variants?product_id={base_id}")

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True

    items = body["data"]["items"]
    names = [item["name"] for item in items]

    assert "iPhone 15 Pro 256 Гб Черный" in names
    assert "iPhone 15 Pro 256 Гб Зеленый" in names
    assert "iPhone 15 Pro 512 Гб Красный" in names
    assert "iPhone 15 Pro 256 Гб Красный" in names
    
    # Проверяем, что у всех товаров есть изображения с ordering
    for item in items:
        assert "images" in item
        for image in item["images"]:
            assert "ordering" in image


@pytest.mark.asyncio
async def test_related_products_by_name(authorized_client, client):
    category_id = await _create_category(authorized_client, "iPhone 14 Pro")

    await _create_product(
        authorized_client,
        name="iPhone 14 Pro 128 Гб Синий",
        category_id=category_id,
        memory="128 Гб",
        color="Синий",
    )
    await _create_product(
        authorized_client,
        name="iPhone 14 Pro 128 Гб Черный",
        category_id=category_id,
        memory="128 Гб",
        color="Черный",
    )

    response = await client.get(
        "/product/related/variants?name=iPhone 14 Pro 128 Гб Синий"
    )

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True
    assert body["data"]["total"] == 2


@pytest.mark.asyncio
async def test_related_products_400_without_lookup(client):
    response = await client.get("/product/related/variants")

    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "product_related_lookup_required"
