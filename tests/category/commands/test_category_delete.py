import pytest

JPEG_BYTES = b"\xff\xd8\xff\xe0delete-image"


@pytest.mark.asyncio
async def test_delete_category_200(authorized_client, image_storage_mock):
    create = await authorized_client.post(
        "/category",
        data={
            "name": "Удаляемая категория",
            "description": "Описание",
            "orderings": "0",
        },
        files=[("images", ("delete.jpg", JPEG_BYTES, "image/jpeg"))],
    )

    assert create.status_code == 200
    category_id = create.json()["data"]["id"]

    response = await authorized_client.delete(f"/category/{category_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["deleted"] is True

    get_response = await authorized_client.get(f"/category/{category_id}")
    assert get_response.status_code == 404

    assert "categories/test-image-uuid.img" in image_storage_mock.deleted_keys


@pytest.mark.asyncio
async def test_delete_category_404_not_found(authorized_client):
    response = await authorized_client.delete("/category/999999")

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "category_not_found"
