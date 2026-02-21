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

    category_id = create.json()["data"]["id"]

    response = await client.get(f"/category/{category_id}")
    assert response.status_code == 200

    body = response.json()
    category = CategoryReadSchema(**body["data"])

    assert category.id == category_id
    assert category.name == "Категория для get"
    assert category.images[0].image_url == "https://test-s3.local/categories/test-image-uuid.img"
    assert [image.ordering for image in category.images] == [1, 2]


@pytest.mark.asyncio
async def test_get_category_404_not_found(client):
    response = await client.get("/category/999999")

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "category_not_found"
