import pytest
from httpx import AsyncClient
from app.main import app
from uuid import uuid4

@pytest.mark.asyncio
async def test_create_loan_unauthorized():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/loans/", json={})
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_get_loan_unauthorized():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f"/loans/{uuid4()}")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_list_loans_unauthorized():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/loans/")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_update_loan_unauthorized():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.put(f"/loans/{uuid4()}", json={})
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_list_installments_unauthorized():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(f"/loans/{uuid4()}/installments")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_pay_installment_unauthorized():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(f"/loan-installments/{uuid4()}/pay", json={})
    assert response.status_code == 401
