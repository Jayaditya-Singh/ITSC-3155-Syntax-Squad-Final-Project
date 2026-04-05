import pytest
from fastapi.testclient import TestClient
from ..main import app

client = TestClient(app)

BASE = "/customers"


def test_integration_create_customer(sample_customer_data):
    response = client.post(BASE + "/", json=sample_customer_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == sample_customer_data["name"]
    assert data["email"] == sample_customer_data["email"]
    assert "id" in data


def test_integration_create_customer_duplicate_email(sample_customer_data):
    client.post(BASE + "/", json=sample_customer_data)
    response = client.post(BASE + "/", json=sample_customer_data)
    assert response.status_code == 400


def test_integration_create_customer_missing_required_field():
    response = client.post(BASE + "/", json={"name": "No Email"})
    assert response.status_code == 422


def test_integration_read_all_customers():
    response = client.get(BASE + "/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_integration_read_one_customer(sample_customer_data):
    create_resp = client.post(BASE + "/", json=sample_customer_data)
    customer_id = create_resp.json()["id"]
    response = client.get(f"{BASE}/{customer_id}")
    assert response.status_code == 200
    assert response.json()["id"] == customer_id


def test_integration_read_one_customer_not_found():
    response = client.get(f"{BASE}/99999")
    assert response.status_code == 404


def test_integration_update_customer(sample_customer_data):
    create_resp = client.post(BASE + "/", json=sample_customer_data)
    customer_id = create_resp.json()["id"]
    update_resp = client.put(f"{BASE}/{customer_id}", json={"phone": "999-888-7777"})
    assert update_resp.status_code == 200
    assert update_resp.json()["phone"] == "999-888-7777"


def test_integration_update_customer_not_found():
    response = client.put(f"{BASE}/99999", json={"phone": "000-000-0000"})
    assert response.status_code == 404


def test_integration_delete_customer(sample_customer_data):
    create_resp = client.post(BASE + "/", json=sample_customer_data)
    customer_id = create_resp.json()["id"]
    delete_resp = client.delete(f"{BASE}/{customer_id}")
    assert delete_resp.status_code == 204
    get_resp = client.get(f"{BASE}/{customer_id}")
    assert get_resp.status_code == 404


def test_integration_delete_customer_not_found():
    response = client.delete(f"{BASE}/99999")
    assert response.status_code == 404