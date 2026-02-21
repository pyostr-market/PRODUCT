import pytest

from src.catalog.suppliers.api.schemas.schemas import SupplierReadSchema


@pytest.mark.asyncio
async def test_filter_supplier_list_200(authorized_client, client):
    names = ["Apple", "Samsung", "Xiaomi"]

    for name in names:
        r = await authorized_client.post(
            "/supplier",
            json={"name": name},
        )
        assert r.status_code == 200

    response = await client.get("/supplier")
    assert response.status_code == 200

    body = response.json()
    assert body["success"] is True

    data = body["data"]
    assert data["total"] >= 3
    assert len(data["items"]) >= 3

    for item in data["items"]:
        SupplierReadSchema(**item)


@pytest.mark.asyncio
async def test_filter_supplier_by_name(authorized_client, client):
    await authorized_client.post("/supplier", json={"name": "FilterApple"})
    await authorized_client.post("/supplier", json={"name": "FilterSamsung"})
    await authorized_client.post("/supplier", json={"name": "OtherBrand"})

    response = await client.get("/supplier?name=Filter")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 2

    names = [item["name"] for item in data["items"]]

    assert "FilterApple" in names
    assert "FilterSamsung" in names
    assert "OtherBrand" not in names


@pytest.mark.asyncio
async def test_filter_supplier_limit(authorized_client, client):
    for i in range(5):
        await authorized_client.post(
            "/supplier",
            json={"name": f"LimitTest{i}"},
        )

    response = await client.get("/supplier?limit=2")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_filter_supplier_offset(authorized_client, client):
    for i in range(5):
        await authorized_client.post(
            "/supplier",
            json={"name": f"OffsetTest{i}"},
        )

    response = await client.get("/supplier?limit=2&offset=2")
    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_filter_supplier_empty(client):
    response = await client.get("/supplier?name=NoSuchBrand")

    assert response.status_code == 200

    body = response.json()
    data = body["data"]

    assert data["total"] == 0
    assert data["items"] == []
