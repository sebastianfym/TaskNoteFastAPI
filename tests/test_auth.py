import pytest
from httpx import AsyncClient
from app import app  # Импортируйте ваше приложение FastAPI


@pytest.mark.asyncio
async def test_create_item():
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        data = {"username": "username", "password": "password"}
        response = await ac.post("/api/v1/register", json=data)
        print(response.json())
    assert response.status_code == 201
    assert response.json() == data



@pytest.mark.asyncio
async def test_read_main():
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        data = {"username": "username", "password": "password"}
        response = await ac.post("/api/v1/login", json=data)
    assert response.status_code == 200
    assert "access_token" in response.json()
