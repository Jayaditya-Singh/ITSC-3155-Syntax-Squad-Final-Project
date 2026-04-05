import pytest
from fastapi.testclient import TestClient
from ..main import app

client = TestClient(app)

BASE = "/orders"


def test_integration_create_order(sample_order_data):
    response = client.post(BASE + "/", json=sample_order_data)
    assert response.status_code == 201
    data = response.json()
    assert data["order_type"] == "Takeout"
    assert data["order_status"] == "Pending"
    assert "id" in data
    assert "tracking_number" in data
    assert data["tracking_number"] is not None


def test_integration_create_guest_order():
    response = client.post(BASE + "/", json={
        "customer_id": None,
        "order_type": "Delivery",
        "order_status": "Pending",
        "total_price": 18.00
    })
    assert response.status_code == 201
    assert response.json()["customer_id"] is None


def test_integration_create_order_default_type():
    response = client.post(BASE + "/", json={"total_price": 10.00})
    assert response.status_code == 201


def test_integration_read_all_orders():
    response = client.get(BASE + "/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_integration_read_one_order(sample_order_data):
    create_resp = client.post(BASE + "/", json=sample_order_data)
    order_id = create_resp.json()["id"]
    response = client.get(f"{BASE}/{order_id}")
    assert response.status_code == 200
    assert response.json()["id"] == order_id


def test_integration_read_one_order_not_found():
    response = client.get(f"{BASE}/99999")
    assert response.status_code == 404


def test_integration_track_order(sample_order_data):
    create_resp = client.post(BASE + "/", json=sample_order_data)
    tracking = create_resp.json()["tracking_number"]
    response = client.get(f"{BASE}/track/{tracking}")
    assert response.status_code == 200
    assert response.json()["tracking_number"] == tracking


def test_integration_track_order_invalid():
    response = client.get(f"{BASE}/track/INVALID999")
    assert response.status_code == 404


def test_integration_update_order_status(sample_order_data):
    create_resp = client.post(BASE + "/", json=sample_order_data)
    order_id = create_resp.json()["id"]
    update_resp = client.put(f"{BASE}/{order_id}", json={"order_status": "Preparing"})
    assert update_resp.status_code == 200
    assert update_resp.json()["order_status"] == "Preparing"


def test_integration_update_order_status_flow(sample_order_data):
    create_resp = client.post(BASE + "/", json=sample_order_data)
    order_id = create_resp.json()["id"]
    for status in ["Preparing", "Ready", "Out for Delivery", "Complete"]:
        resp = client.put(f"{BASE}/{order_id}", json={"order_status": status})
        assert resp.status_code == 200
        assert resp.json()["order_status"] == status


def test_integration_update_order_not_found():
    response = client.put(f"{BASE}/99999", json={"order_status": "Complete"})
    assert response.status_code == 404


def test_integration_delete_order(sample_order_data):
    create_resp = client.post(BASE + "/", json=sample_order_data)
    order_id = create_resp.json()["id"]
    delete_resp = client.delete(f"{BASE}/{order_id}")
    assert delete_resp.status_code == 204
    get_resp = client.get(f"{BASE}/{order_id}")
    assert get_resp.status_code == 404


def test_integration_delete_order_not_found():
    response = client.delete(f"{BASE}/99999")
    assert response.status_code == 404