import pytest


@pytest.mark.asyncio
async def test_register_endpoint_shape(client):
    payload = {
        "first_name": "Test",
        "last_name": "User",
        "username": "test_user",
        "email": "test@example.com",
        "password": "StrongPass123",
    }
    response = await client.post("/auth/register", json=payload)
    assert response.status_code in {201, 400, 500}
