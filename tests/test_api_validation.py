"""HTTP validation regression tests for the numeric-rule API."""
from fastapi.testclient import TestClient
from agents.api import app

client = TestClient(app)


def payload(**updates):
    result = {
        "task_id": "TASK-1",
        "target_identifier": "SAMPLE-1",
        "primary_metric": 10,
        "secondary_metric": 2,
    }
    result.update(updates)
    return result


def test_api_valid_numeric_request():
    response = client.post("/api/audit", json=payload())
    assert response.status_code == 200
    result = response.json()
    assert result["task_id"] == "TASK-1"
    assert result["total_alerts"] == 0


def test_api_rejects_non_finite_metrics():
    for metric in ("NaN", "Infinity", "-Infinity"):
        response = client.post("/api/audit", json=payload(primary_metric=metric))
        assert response.status_code == 422


def test_api_rejects_obvious_identifiers_without_server_error():
    response = client.post("/api/audit", json=payload(target_identifier="MRN-123456"))
    assert response.status_code == 400
    assert "Input contains" in response.json()["detail"]
