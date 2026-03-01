import pytest

JPEG_BYTES = b"\xff\xd8\xff\xe0test-image"


@pytest.mark.asyncio
async def test_filter_category_list_200(authorized_client, client):
    names = ["Категория A", "Категория B", "Категория C"]

    for name in names:
        r = await authorized_client.post(
            "/category",
            data={
                "name": name,
                "orderings": "0",
            },
            files=[("images", ("test.jpg", JPEG_BYTES, "image/jpeg"))],
        )
        assert r.status_code == 200

    response = await client.get("/category")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] >= 3
    assert len(data["items"]) >= 3
    
    # Проверяем наличие связанных данных (могут быть null)
    for item in data["items"]:
        assert "parent" in item
        assert "manufacturer" in item


@pytest.mark.asyncio
async def test_filter_category_by_name(authorized_client, client):
    async def create(name: str):
        await authorized_client.post(
            "/category",
            data={"name": name, "orderings": "0"},
            files=[("images", ("test.jpg", JPEG_BYTES, "image/jpeg"))],
        )

    await create("FilterBooks")
    await create("FilterPhones")
    await create("Other")

    response = await client.get("/category?name=Filter")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 2

    names = [item["name"] for item in data["items"]]

    assert "FilterBooks" in names
    assert "FilterPhones" in names
    assert "Other" not in names


@pytest.mark.asyncio
async def test_filter_category_with_parent(authorized_client, client):
    """Фильтрация категорий с проверкой связанных родительских категорий."""
    # Создаём родительскую категорию
    parent_resp = await authorized_client.post(
        "/category",
        data={"name": "Filter Parent", "orderings": "0"},
        files=[("images", ("test.jpg", JPEG_BYTES, "image/jpeg"))],
    )
    assert parent_resp.status_code == 200
    parent_id = parent_resp.json()["data"]["id"]
    
    # Создаём дочернюю категорию
    child_resp = await authorized_client.post(
        "/category",
        data={"name": "Filter Child", "orderings": "0", "parent_id": str(parent_id)},
        files=[("images", ("test.jpg", JPEG_BYTES, "image/jpeg"))],
    )
    assert child_resp.status_code == 200

    response = await client.get("/category?name=Filter Child")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 1
    category = data["items"][0]

    # Проверяем, что родительская категория вернулась как вложенный объект
    assert category["parent"] is not None
    assert category["parent"]["id"] == parent_id
    assert category["parent"]["name"] == "Filter Parent"
