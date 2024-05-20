import pytest
from httpx import AsyncClient
from app import app  # Импортируйте ваше приложение FastAPI


@pytest.mark.asyncio
async def test_task():
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        data = {"username": "username", "password": "password"}
        response = await ac.post("/api/v1/login", json=data)
        access_token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

        data = {"title": "Title1", "description": "description1"}

        response = await ac.post("/api/v1/tasks/add", json=data, headers=headers)
        task_id = response.json()["id"]
        assert response.status_code == 201

        data = {"title": "Title12"}
        response = await ac.patch(f"/api/v1/tasks/{task_id}", json=data, headers=headers)
        assert response.status_code == 200
        assert response.json()["title"] == "Title12"

        response = await ac.get(f"/api/v1/tasks/all", headers=headers)
        assert response.status_code == 200
        assert len(response.json()) != 0

        response = await ac.get(f"/api/v1/tasks/my_tasks", headers=headers)
        assert response.status_code == 200
        assert len(response.json()) != 0

        response = await ac.get(f"/api/v1/tasks/task/{task_id}", headers=headers)
        assert response.status_code == 200
        assert response.json()["title"] == "Title12"

        data = {"title": "NoTitle12"}
        response = await ac.patch(f"/api/v1/tasks/{task_id}", json=data)
        assert response.status_code == 401

        response = await ac.delete(f"/api/v1/tasks/task/{task_id}", headers=headers)
        assert response.status_code == 200



