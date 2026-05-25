import pytest


@pytest.mark.asyncio
async def test_healthcheck_returns_ok(client):
    response = await client.get("/health/")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["database"] == "ok"
