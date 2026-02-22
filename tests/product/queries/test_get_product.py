import pytest

from src.catalog.product.api.schemas.schemas import ProductReadSchema


@pytest.mark.asyncio
async def test_get_product_200(authorized_client, client):
    create = await authorized_client.post(
        "/product",
        data={
            "name": "Товар для получения",
            "price": "777.77",
        },
    )
    assert create.status_code == 200
    product_id = create.json()["data"]["id"]

    response = await client.get(f"/product/{product_id}")

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True

    product = ProductReadSchema(**body["data"])
    assert product.id == product_id
    assert product.name == "Товар для получения"


@pytest.mark.asyncio
async def test_get_product_200_with_images(authorized_client, client):
    """Получение товара с изображениями и проверкой ordering."""
    create = await authorized_client.post(
        "/product",
        data={
            "name": "Товар с изображениями",
            "price": "999.99",
            "image_is_main": ["true", "false"],
            "image_ordering": ["0", "1"],
        },
        files=[
            ("images", ("img1.jpg", b"\xff\xd8\xff\xe0test1", "image/jpeg")),
            ("images", ("img2.jpg", b"\xff\xd8\xff\xe0test2", "image/jpeg")),
        ],
    )
    assert create.status_code == 200
    
    product_id = create.json()["data"]["id"]

    response = await client.get(f"/product/{product_id}")

    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True

    product = ProductReadSchema(**body["data"])
    assert product.id == product_id
    assert len(product.images) == 2
    assert product.images[0].ordering == 0
    assert product.images[1].ordering == 1
    assert product.images[0].is_main is True


@pytest.mark.asyncio
async def test_get_product_404(client):
    response = await client.get("/product/999999")

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "product_not_found"
