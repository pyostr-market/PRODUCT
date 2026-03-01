import json

import pytest


@pytest.mark.asyncio
async def test_delete_category_200(authorized_client, image_storage_mock):
    # Загружаем изображение
    with open("static/img/test.jpg", "rb") as f:
        image_data = f.read()

    upload_response = await authorized_client.post(
        "/upload/",
        data={"folder": "categories"},
        files={"file": ("delete.jpg", image_data, "image/jpeg")},
    )
    assert upload_response.status_code == 200
    upload_id = upload_response.json()["data"]["upload_id"]

    # Создаём категорию
    create = await authorized_client.post(
        "/category",
        data={
            "name": "Удаляемая категория",
            "description": "Описание",
            "images_json": json.dumps([{"upload_id": upload_id, "ordering": 0}]),
        },
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

    # Проверяем, что изображение было удалено из S3
    assert len(image_storage_mock.deleted_keys) > 0


@pytest.mark.asyncio
async def test_delete_category_404_not_found(authorized_client):
    response = await authorized_client.delete("/category/999999")

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "category_not_found"
