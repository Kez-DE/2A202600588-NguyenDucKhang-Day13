from fastapi.testclient import TestClient

from app.main import app


def test_chat_returns_and_propagates_correlation_id() -> None:
    client = TestClient(app)
    response = client.post(
        "/chat",
        headers={"x-request-id": "req-test1234"},
        json={
            "user_id": "u_test",
            "session_id": "s_test",
            "feature": "qa",
            "message": "Explain why metrics traces and logs work together",
        },
    )

    assert response.status_code == 200
    assert response.json()["correlation_id"] == "req-test1234"
    assert response.headers["x-request-id"] == "req-test1234"
    assert response.headers["x-response-time-ms"].isdigit()


def test_dashboard_contains_required_panels() -> None:
    client = TestClient(app)
    response = client.get("/dashboard")

    assert response.status_code == 200
    html = response.text
    for label in [
        "Latency P50 / P95 / P99",
        "Traffic",
        "Error Rate & Breakdown",
        "Cost Over Time",
        "Tokens In / Out",
        "Quality Proxy",
    ]:
        assert label in html
