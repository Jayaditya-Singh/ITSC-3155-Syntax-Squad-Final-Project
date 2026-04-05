import pytest
from fastapi.testclient import TestClient
from ..main import app

client = TestClient(app)

BASE = "/reviews"


def test_integration_create_review(sample_review_data):
    response = client.post(BASE + "/", json=sample_review_data)
    assert response.status_code == 201
    data = response.json()
    assert data["score"] == 5
    assert data["review_text"] == "Great food, fast delivery!"
    assert "id" in data


def test_integration_create_review_min_score():
    response = client.post(BASE + "/", json={
        "order_id": 2,
        "review_text": "Terrible experience.",
        "score": 1
    })
    assert response.status_code == 201
    assert response.json()["score"] == 1


def test_integration_create_review_score_only():
    response = client.post(BASE + "/", json={"order_id": 3, "score": 4})
    assert response.status_code == 201
    assert response.json()["review_text"] is None


def test_integration_create_review_invalid_score_too_high():
    response = client.post(BASE + "/", json={
        "order_id": 4,
        "score": 6
    })
    assert response.status_code == 422


def test_integration_create_review_invalid_score_too_low():
    response = client.post(BASE + "/", json={
        "order_id": 5,
        "score": 0
    })
    assert response.status_code == 422


def test_integration_create_review_missing_score():
    response = client.post(BASE + "/", json={
        "order_id": 6,
        "review_text": "No score provided"
    })
    assert response.status_code == 422


def test_integration_read_all_reviews():
    response = client.get(BASE + "/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_integration_read_one_review(sample_review_data):
    create_resp = client.post(BASE + "/", json=sample_review_data)
    review_id = create_resp.json()["id"]
    response = client.get(f"{BASE}/{review_id}")
    assert response.status_code == 200
    assert response.json()["id"] == review_id


def test_integration_read_one_review_not_found():
    response = client.get(f"{BASE}/99999")
    assert response.status_code == 404


def test_integration_update_review(sample_review_data):
    create_resp = client.post(BASE + "/", json=sample_review_data)
    review_id = create_resp.json()["id"]
    update_resp = client.put(f"{BASE}/{review_id}", json={
        "review_text": "Updated: even better than expected!",
        "score": 5
    })
    assert update_resp.status_code == 200
    assert update_resp.json()["review_text"] == "Updated: even better than expected!"


def test_integration_update_review_invalid_score(sample_review_data):
    create_resp = client.post(BASE + "/", json=sample_review_data)
    review_id = create_resp.json()["id"]
    update_resp = client.put(f"{BASE}/{review_id}", json={"score": 10})
    assert update_resp.status_code == 422


def test_integration_update_review_not_found():
    response = client.put(f"{BASE}/99999", json={"score": 3})
    assert response.status_code == 404


def test_integration_delete_review(sample_review_data):
    create_resp = client.post(BASE + "/", json=sample_review_data)
    review_id = create_resp.json()["id"]
    delete_resp = client.delete(f"{BASE}/{review_id}")
    assert delete_resp.status_code == 204
    get_resp = client.get(f"{BASE}/{review_id}")
    assert get_resp.status_code == 404


def test_integration_delete_review_not_found():
    response = client.delete(f"{BASE}/99999")
    assert response.status_code == 404