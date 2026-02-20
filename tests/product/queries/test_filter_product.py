import pytest


@pytest.mark.asyncio
async def test_filter_product_list_200(authorized_client, client):
    names = ["Product A", "Product B", "Product C"]

    for name in names:
        r = await authorized_client.post(
            "/product/",
            data={
                "name": name,
                "price": "100.00",
            },
        )
        assert r.status_code == 200

    response = await client.get("/product/")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] >= 3
    assert len(data["items"]) >= 3


@pytest.mark.asyncio
async def test_filter_product_by_name(authorized_client, client):
    await authorized_client.post("/product/", data={"name": "Filter iPhone", "price": "1.00"})
    await authorized_client.post("/product/", data={"name": "Filter Samsung", "price": "1.00"})
    await authorized_client.post("/product/", data={"name": "Other Item", "price": "1.00"})

    response = await client.get("/product/?name=Filter")

    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 2
    names = [item["name"] for item in data["items"]]

    assert "Filter iPhone" in names
    assert "Filter Samsung" in names
    assert "Other Item" not in names
