import pytest

JPEG_BYTES = b"\xff\xd8\xff\xe0filter-image"


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
