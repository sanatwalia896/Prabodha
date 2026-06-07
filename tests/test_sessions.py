from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from app.main import app


def test_start_session_returns_session_payload() -> None:
    client = TestClient(app)
    user_id = str(uuid4())
    response = client.post(
        "/api/v1/sessions",
        json={"user_id": user_id, "label": "Deep Work"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["label"] == "Deep Work"
    UUID(body["session_id"])


def test_stop_session_returns_closed_session() -> None:
    client = TestClient(app)
    user_id = str(uuid4())
    session_response = client.post(
        "/api/v1/sessions",
        json={"user_id": user_id, "label": "Deep Work"},
    )
    session_id = session_response.json()["session_id"]
    client.post(
        "/api/v1/events/score",
        json={"session_id": session_id, "score": 91.0, "level": "DEEP"},
    )
    response = client.post(f"/api/v1/sessions/{session_id}/stop")

    assert response.status_code == 200
    body = response.json()
    assert body["end_time"] is not None
    assert body["overall_score"] == 91.0
