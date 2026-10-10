from app.app import create_app


VALID_PAYLOAD = {
    "age": 35, "job": "technician", "marital": "married", "education": "secondary",
    "default": "no", "balance": 1200, "housing": "yes", "loan": "no",
    "contact": "cellular", "day": 15, "month": "may", "campaign": 1,
    "pdays": -1, "previous": 0, "poutcome": "unknown",
}


def test_health_endpoint():
    client = create_app({"TESTING": True}).test_client()
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_api_rejects_duration():
    client = create_app({"TESTING": True}).test_client()
    response = client.post("/api/score", json={**VALID_PAYLOAD, "duration": 90})
    assert response.status_code == 422
    assert "leakage" in " ".join(response.get_json()["errors"]).lower()


def test_api_rejects_missing_field():
    client = create_app({"TESTING": True}).test_client()
    payload = VALID_PAYLOAD.copy()
    payload.pop("age")
    response = client.post("/api/score", json=payload)
    assert response.status_code == 422


def test_api_scores_valid_payload():
    client = create_app({"TESTING": True}).test_client()
    response = client.post("/api/score", json=VALID_PAYLOAD)
    body = response.get_json()
    assert response.status_code == 200
    assert 0 <= body["probability"] <= 1
    assert body["priority_label"] in {"ưu tiên liên hệ", "chưa ưu tiên"}


def test_api_rejects_extra_field():
    client = create_app({"TESTING": True}).test_client()
    response = client.post("/api/score", json={**VALID_PAYLOAD, "customer_id": "abc"})
    assert response.status_code == 422


def test_api_rejects_invalid_category():
    client = create_app({"TESTING": True}).test_client()
    response = client.post("/api/score", json={**VALID_PAYLOAD, "job": "astronaut"})
    assert response.status_code == 422


def test_api_rejects_out_of_range_number():
    client = create_app({"TESTING": True}).test_client()
    response = client.post("/api/score", json={**VALID_PAYLOAD, "age": 500})
    assert response.status_code == 422
