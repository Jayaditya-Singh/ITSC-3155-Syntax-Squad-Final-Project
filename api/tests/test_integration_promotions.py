import pytest
from fastapi.testclient import TestClient
from ..main import app
from datetime import datetime, timedelta

client = TestClient(app)

BASE = "/promotions"

FUTURE = (datetime.now() + timedelta(days=30)).isoformat()


def test_integration_create_promotion_percent(sample_promotion_data):
    response = client.post(BASE + "/", json=sample_promotion_data)
    assert response.status_code == 201
    data = response.json()
    assert data["promo_code"] == sample_promotion_data["promo_code"]  # ← use fixture value
    assert float(data["discount_percent"]) == 15.0
    assert data["is_active"] is True


def test_integration_create_promotion_flat_amount():
    response = client.post(BASE + "/", json={
        "promo_code": "5OFF",
        "discount_amount": 5.00,
        "expiration_date": FUTURE,
        "is_active": True
    })
    assert response.status_code == 201
    assert float(response.json()["discount_amount"]) == 5.00


def test_integration_create_promotion_duplicate_code(sample_promotion_data):
    client.post(BASE + "/", json=sample_promotion_data)
    response = client.post(BASE + "/", json=sample_promotion_data)
    assert response.status_code == 400


def test_integration_create_promotion_missing_expiration():
    response = client.post(BASE + "/", json={
        "promo_code": "NOEXP",
        "discount_percent": 10.0
    })
    assert response.status_code == 422


def test_integration_read_all_promotions():
    response = client.get(BASE + "/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_integration_read_by_code(sample_promotion_data):
    client.post(BASE + "/", json=sample_promotion_data)
    promo_code = sample_promotion_data["promo_code"]  # ← use fixture value
    response = client.get(f"{BASE}/code/{promo_code}")
    assert response.status_code == 200
    assert response.json()["promo_code"] == promo_code


def test_integration_read_by_code_invalid():
    response = client.get(f"{BASE}/code/DOESNOTEXIST")
    assert response.status_code == 404


def test_integration_read_one_promotion(sample_promotion_data):
    create_resp = client.post(BASE + "/", json=sample_promotion_data)
    promo_id = create_resp.json()["id"]
    response = client.get(f"{BASE}/{promo_id}")
    assert response.status_code == 200
    assert response.json()["id"] == promo_id


def test_integration_read_one_promotion_not_found():
    response = client.get(f"{BASE}/99999")
    assert response.status_code == 404


def test_integration_deactivate_promotion(sample_promotion_data):
    create_resp = client.post(BASE + "/", json=sample_promotion_data)
    promo_id = create_resp.json()["id"]
    update_resp = client.put(f"{BASE}/{promo_id}", json={"is_active": False})
    assert update_resp.status_code == 200
    assert update_resp.json()["is_active"] is False


def test_integration_update_promotion_not_found():
    response = client.put(f"{BASE}/99999", json={"is_active": False})
    assert response.status_code == 404


def test_integration_delete_promotion(sample_promotion_data):
    create_resp = client.post(BASE + "/", json=sample_promotion_data)
    promo_id = create_resp.json()["id"]
    delete_resp = client.delete(f"{BASE}/{promo_id}")
    assert delete_resp.status_code == 204
    get_resp = client.get(f"{BASE}/{promo_id}")
    assert get_resp.status_code == 404