import pytest

from src.catalog.category.api.schemas.schemas import CategoryReadSchema

JPEG_1 = b"\xff\xd8\xff\xe0get-image-1"
JPEG_2 = b"\xff\xd8\xff\xe0get-image-2"
JPEG_BYTES = b"\xff\xd8\xff\xe0test-image"


@pytest.mark.asyncio
async def test_get_category_200(authorized_client, client):
    create = await authorized_client.post(
        "/category",
        data={
            "name": "Категория для get",
            "description": "Описание",
            "orderings": ["2", "1"],
        },
        files=[
            ("images", ("get2.jpg", JPEG_2, "image/jpeg")),
            ("images", ("get1.jpg", JPEG_1, "image/jpeg")),
        ],
    )
    assert create.status_code == 200

    # Проверяем, что изображения созданы с правильным ordering
    create_images = create.json()["data"]["images"]
    assert len(create_images) == 2
    # Первое изображение (get2.jpg) имеет ordering=2, второе (get1.jpg) имеет ordering=1

    category_id = create.json()["data"]["id"]

    response = await client.get(f"/category/{category_id}")
    assert response.status_code == 200

    body = response.json()
    category = CategoryReadSchema(**body["data"])

    assert category.id == category_id
    assert category.name == "Категория для get"
    # Изображения сортируются по ordering (возрастание), поэтому сначала идёт ordering=1, потом ordering=2
    assert [image.ordering for image in category.images] == [1, 2]
    # Первое изображение в ответе (с ordering=1) - это get1.jpg (второй файл)
    assert category.images[0].image_url == "https://test-s3.local/categories/test-image-2.img"
    # Второе изображение в ответе (с ordering=2) - это get2.jpg (первый файл)
    assert category.images[1].image_url == "https://test-s3.local/categories/test-image-1.img"
    
    # Проверяем, что связанные данные возвращаются (даже если null)
    assert "parent" in body["data"]
    assert "manufacturer" in body["data"]


@pytest.mark.asyncio
async def test_get_category_200_with_parent(authorized_client, client):
    """Проверка получения категории с родительской категорией."""
    # Создаём родительскую категорию
    parent_resp = await authorized_client.post(
        "/category",
        data={"name": "Parent Category", "orderings": "0"},
        files=[("images", ("test.jpg", JPEG_BYTES, "image/jpeg"))],
    )
    assert parent_resp.status_code == 200, f"Parent category create failed: {parent_resp.json()}"
    parent_id = parent_resp.json()["data"]["id"]
    
    # Создаём дочернюю категорию
    child_resp = await authorized_client.post(
        "/category",
        data={"name": "Child Category", "orderings": "0", "parent_id": str(parent_id)},
        files=[("images", ("test.jpg", JPEG_BYTES, "image/jpeg"))],
    )
    assert child_resp.status_code == 200, f"Child category create failed: {child_resp.json()}"
    child_id = child_resp.json()["data"]["id"]

    response = await client.get(f"/category/{child_id}")
    assert response.status_code == 200

    body = response.json()
    
    # Проверяем, что родительская категория вернулась как вложенный объект
    assert body["data"]["parent"] is not None
    assert body["data"]["parent"]["id"] == parent_id
    assert body["data"]["parent"]["name"] == "Parent Category"


@pytest.mark.asyncio
async def test_get_category_200_with_manufacturer(authorized_client, client):
    """Проверка получения категории с производителем."""
    # Создаём производителя
    manuf_resp = await authorized_client.post(
        "/manufacturer",
        json={"name": "Test Manufacturer", "description": "Test Desc"},
    )
    assert manuf_resp.status_code == 200, f"Manufacturer create failed: {manuf_resp.json()}"
    manufacturer_id = manuf_resp.json()["data"]["id"]
    
    # Создаём категорию с производителем
    cat_resp = await authorized_client.post(
        "/category",
        data={"name": "Category with Manufacturer", "orderings": "0", "manufacturer_id": str(manufacturer_id)},
        files=[("images", ("test.jpg", JPEG_BYTES, "image/jpeg"))],
    )
    assert cat_resp.status_code == 200, f"Category create failed: {cat_resp.json()}"
    category_id = cat_resp.json()["data"]["id"]

    response = await client.get(f"/category/{category_id}")
    assert response.status_code == 200

    body = response.json()
    
    # Проверяем, что производитель вернулся как вложенный объект
    assert body["data"]["manufacturer"] is not None
    assert body["data"]["manufacturer"]["id"] == manufacturer_id
    assert body["data"]["manufacturer"]["name"] == "Test Manufacturer"
    assert body["data"]["manufacturer"]["description"] == "Test Desc"


@pytest.mark.asyncio
async def test_get_category_404_not_found(client):
    response = await client.get("/category/999999")

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "category_not_found"
