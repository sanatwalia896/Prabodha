from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


def test_register_returns_user_response() -> None:
    client = TestClient(app)
    username = f"sam-{uuid4().hex[:8]}"
    response = client.post(
        "/api/v1/auth/register",
        json={"username": username, "password": "password123"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["username"] == username
    assert body["settings"] == {}
    assert body["created_at"] is not None


def test_login_returns_bearer_token() -> None:
    client = TestClient(app)
    username = f"sam-{uuid4().hex[:8]}"
    client.post(
        "/api/v1/auth/register",
        json={"username": username, "password": "password123"},
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": "password123"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert len(body["access_token"]) > 20
