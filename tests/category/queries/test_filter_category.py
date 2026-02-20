import pytest


@pytest.mark.asyncio
async def test_filter_category_list_200(authorized_client, client):
    names = ["Категория A", "Категория B", "Категория C"]

    for name in names:
        r = await authorized_client.post(
            "/category/",
            json={
                "name": name,
                "images": [
                    {
                        "image": "filter-image",
                        "image_name": "test.jpg",
                        "ordering": 0,
                    }
                ],
            },
        )
        assert r.status_code == 200

    response = await client.get("/category/")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] >= 3
    assert len(data["items"]) >= 3


@pytest.mark.asyncio
async def test_filter_category_by_name(authorized_client, client):
    payload = {"images": [{"image": "i", "image_name": "test.jpg", "ordering": 0}]}
    await authorized_client.post("/category/", json={"name": "FilterBooks", **payload})
    await authorized_client.post("/category/", json={"name": "FilterPhones", **payload})
    await authorized_client.post("/category/", json={"name": "Other", **payload})

    response = await client.get("/category/?name=Filter")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 2

    names = [item["name"] for item in data["items"]]

    assert "FilterBooks" in names
    assert "FilterPhones" in names
    assert "Other" not in names
