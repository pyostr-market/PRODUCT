import pytest

from src.catalog.category.api.schemas.schemas import CategoryReadSchema

JPEG_1 = b"\xff\xd8\xff\xe0get-image-1"
JPEG_2 = b"\xff\xd8\xff\xe0get-image-2"


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


@pytest.mark.asyncio
async def test_get_category_404_not_found(client):
    response = await client.get("/category/999999")

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "category_not_found"
