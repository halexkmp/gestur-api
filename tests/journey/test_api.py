import pytest
from httpx import AsyncClient
from app.main import app
from uuid import uuid4

@pytest.mark.asyncio
async def test_register_journey_api_unauthorized():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/journey/", json={"latitude": -3.7, "longitude": -38.5})
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_admin_list_journeys_unauthorized():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/journey/admin")
    assert response.status_code == 401
