import pytest


@pytest.mark.asyncio
async def test_filter_product_list_200(authorized_client, client):
    names = ["Product A", "Product B", "Product C"]

    for name in names:
        r = await authorized_client.post(
            "/product",
            data={
                "name": name,
                "price": "100.00",
            },
        )
        assert r.status_code == 200

    response = await client.get("/product")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] >= 3
    assert len(data["items"]) >= 3
    
    # Проверяем, что у товаров есть изображения с ordering
    for item in data["items"]:
        assert "images" in item
        for image in item["images"]:
            assert "ordering" in image


@pytest.mark.asyncio
async def test_filter_product_by_name(authorized_client, client):
    await authorized_client.post("/product", data={"name": "Filter iPhone", "price": "1.00"})
    await authorized_client.post("/product", data={"name": "Filter Samsung", "price": "1.00"})
    await authorized_client.post("/product", data={"name": "Other Item", "price": "1.00"})

    response = await client.get("/product?name=Filter")

    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 2
    names = [item["name"] for item in data["items"]]

    assert "Filter iPhone" in names
    assert "Filter Samsung" in names
    assert "Other Item" not in names


@pytest.mark.asyncio
async def test_filter_product_with_images_and_ordering(authorized_client, client):
    """Фильтрация товаров с изображениями и проверкой ordering."""
    await authorized_client.post(
        "/product",
        data={
            "name": "Product with images",
            "price": "999.00",
            "image_is_main": ["true", "false"],
            "image_ordering": ["0", "1"],
        },
        files=[
            ("images", ("img1.jpg", b"\xff\xd8\xff\xe0test1", "image/jpeg")),
            ("images", ("img2.jpg", b"\xff\xd8\xff\xe0test2", "image/jpeg")),
        ],
    )

    response = await client.get("/product?name=Product")

    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] >= 1
    product = data["items"][0]
    
    assert len(product["images"]) == 2
    assert product["images"][0]["ordering"] == 0
    assert product["images"][1]["ordering"] == 1
    assert product["images"][0]["is_main"] is True
