import pytest
from httpx import AsyncClient
from app.main import app
import asyncio
from asgi_lifespan import LifespanManager

@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://test", transport=LifespanManager(app)) as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert "current_time" in data

@pytest.mark.asyncio
async def test_post_webhook_and_status():
    txn_data = {
        "transaction_id": "txn_test_01",
        "source_account": "user_123",
        "destination_account": "merchant_456",
        "amount": 100,
        "currency": "INR"
    }
    async with AsyncClient(app=app, base_url="http://test", transport=LifespanManager(app)) as ac:
        response = await ac.post("/v1/webhooks/transactions", json=txn_data)
        assert response.status_code == 202

        response = await ac.get(f"/v1/transactions/{txn_data['transaction_id']}")
        assert response.status_code == 200
        status_data = response.json()
        assert status_data["transaction_id"] == txn_data["transaction_id"]
        assert status_data["status"] in ("PROCESSING", "PROCESSED")

        await asyncio.sleep(35)

        response = await ac.get(f"/v1/transactions/{txn_data['transaction_id']}")
        assert response.status_code == 200
        status_data = response.json()
        assert status_data["status"] == "PROCESSED"
        assert status_data["processed_at"] is not None

@pytest.mark.asyncio
async def test_webhook_idempotency():
    txn_data = {
        "transaction_id": "txn_test_02",
        "source_account": "user_abc",
        "destination_account": "merchant_xyz",
        "amount": 500,
        "currency": "USD"
    }
    async with AsyncClient(app=app, base_url="http://test", transport=LifespanManager(app)) as ac:
        responses = await asyncio.gather(
            ac.post("/v1/webhooks/transactions", json=txn_data),
            ac.post("/v1/webhooks/transactions", json=txn_data),
            ac.post("/v1/webhooks/transactions", json=txn_data),
        )
        for r in responses:
            assert r.status_code == 202

        await asyncio.sleep(35)

        response = await ac.get(f"/v1/transactions/{txn_data['transaction_id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "PROCESSED"
