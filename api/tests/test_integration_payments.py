import pytest
from fastapi.testclient import TestClient
from ..main import app

client = TestClient(app)

BASE = "/payments"


def test_integration_create_payment_credit(sample_payment_data):
    response = client.post(BASE + "/", json=sample_payment_data)
    assert response.status_code == 201
    data = response.json()
    assert data["payment_type"] == "Credit"
    assert data["card_last_four"] == "4242"
    assert data["transaction_status"] == "Approved"
    assert "id" in data


def test_integration_create_payment_cash():
    response = client.post(BASE + "/", json={
        "order_id": 2,
        "payment_type": "Cash",
        "transaction_status": "Approved"
    })
    assert response.status_code == 201
    assert response.json()["card_last_four"] is None


def test_integration_create_payment_missing_order_id():
    response = client.post(BASE + "/", json={
        "payment_type": "Credit",
        "card_last_four": "1234",
        "transaction_status": "Approved"
    })
    assert response.status_code == 422


def test_integration_read_all_payments():
    response = client.get(BASE + "/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_integration_read_one_payment(sample_payment_data):
    create_resp = client.post(BASE + "/", json=sample_payment_data)
    payment_id = create_resp.json()["id"]
    response = client.get(f"{BASE}/{payment_id}")
    assert response.status_code == 200
    assert response.json()["id"] == payment_id


def test_integration_read_one_payment_not_found():
    response = client.get(f"{BASE}/99999")
    assert response.status_code == 404


def test_integration_read_payment_by_order(sample_payment_data):
    client.post(BASE + "/", json=sample_payment_data)
    response = client.get(f"{BASE}/order/{sample_payment_data['order_id']}")
    assert response.status_code == 200
    assert response.json()["order_id"] == sample_payment_data["order_id"]


def test_integration_read_payment_by_order_not_found():
    response = client.get(f"{BASE}/order/99999")
    assert response.status_code == 404


def test_integration_update_payment_status(sample_payment_data):
    create_resp = client.post(BASE + "/", json={
        **sample_payment_data,
        "transaction_status": "Pending"
    })
    payment_id = create_resp.json()["id"]
    update_resp = client.put(f"{BASE}/{payment_id}",
                             json={"transaction_status": "Approved"})
    assert update_resp.status_code == 200
    assert update_resp.json()["transaction_status"] == "Approved"


def test_integration_update_payment_declined(sample_payment_data):
    create_resp = client.post(BASE + "/", json={
        **sample_payment_data,
        "transaction_status": "Pending"
    })
    payment_id = create_resp.json()["id"]
    update_resp = client.put(f"{BASE}/{payment_id}",
                             json={"transaction_status": "Declined"})
    assert update_resp.status_code == 200
    assert update_resp.json()["transaction_status"] == "Declined"


def test_integration_update_payment_not_found():
    response = client.put(f"{BASE}/99999", json={"transaction_status": "Approved"})
    assert response.status_code == 404


def test_integration_delete_payment(sample_payment_data):
    create_resp = client.post(BASE + "/", json=sample_payment_data)
    payment_id = create_resp.json()["id"]
    delete_resp = client.delete(f"{BASE}/{payment_id}")
    assert delete_resp.status_code == 204
    get_resp = client.get(f"{BASE}/{payment_id}")
    assert get_resp.status_code == 404