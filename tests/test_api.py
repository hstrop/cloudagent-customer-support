from fastapi.testclient import TestClient

from cloudagent.api import create_app


def test_api_health_and_chat() -> None:
    with TestClient(create_app()) as client:
        assert client.get("/health").json()["mode"] == "offline_demo"
        response = client.post("/v1/chat", json={"message": "物流一直没有更新", "session_id": "api-test"})
    assert response.status_code == 200
    assert response.json()["evidence"][0]["id"] == "delivery-001"


def test_api_rejects_invalid_session() -> None:
    with TestClient(create_app()) as client:
        response = client.post("/v1/chat", json={"message": "退款", "session_id": "bad session"})
    assert response.status_code == 400


def test_api_can_reset_session() -> None:
    with TestClient(create_app()) as client:
        client.post("/v1/chat", json={"message": "客服几点上班？", "session_id": "reset-api"})
        response = client.post("/v1/sessions/reset-api/reset")
    assert response.status_code == 200
    assert response.json()["reset"] is True
