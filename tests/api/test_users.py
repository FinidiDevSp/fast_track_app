import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    r = await client.get("/api/v1/health")
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_create_and_list_users(client: AsyncClient):
    payload = {"email": "alice@example.com", "full_name": "Alice"}
    r = await client.post("/api/v1/users", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == payload["email"]
    assert data["full_name"] == payload["full_name"]
    assert "id" in data

    r2 = await client.get("/api/v1/users")
    assert r2.status_code == 200
    users = r2.json()
    assert any(u["email"] == "alice@example.com" for u in users)
    users = r2.json()
    assert any(u["email"] == "alice@example.com" for u in users)
