import pytest
from fastapi.testclient import TestClient
from ..main import app

client = TestClient(app)

BASE = "/menuitems"


def test_integration_create_menu_item(sample_menu_item_data):
    response = client.post(BASE + "/", json=sample_menu_item_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == sample_menu_item_data["name"]
    assert float(data["price"]) == sample_menu_item_data["price"]
    assert data["calories"] == sample_menu_item_data["calories"]
    assert data["category"] == sample_menu_item_data["category"]
    assert "id" in data


def test_integration_create_menu_item_no_optional_fields():
    response = client.post(BASE + "/", json={"name": "Plain Dish", "price": 5.00})
    assert response.status_code == 201
    data = response.json()
    assert data["calories"] is None
    assert data["category"] is None


def test_integration_create_menu_item_duplicate_name(sample_menu_item_data):
    client.post(BASE + "/", json=sample_menu_item_data)
    response = client.post(BASE + "/", json=sample_menu_item_data)
    assert response.status_code == 400


def test_integration_create_menu_item_missing_price():
    response = client.post(BASE + "/", json={"name": "No Price Item"})
    assert response.status_code == 422


def test_integration_read_all_menu_items():
    response = client.get(BASE + "/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_integration_read_one_menu_item(sample_menu_item_data):
    create_resp = client.post(BASE + "/", json=sample_menu_item_data)
    item_id = create_resp.json()["id"]
    response = client.get(f"{BASE}/{item_id}")
    assert response.status_code == 200
    assert response.json()["id"] == item_id


def test_integration_read_one_menu_item_not_found():
    response = client.get(f"{BASE}/99999")
    assert response.status_code == 404


def test_integration_update_menu_item_price(sample_menu_item_data):
    create_resp = client.post(BASE + "/", json=sample_menu_item_data)
    item_id = create_resp.json()["id"]
    update_resp = client.put(f"{BASE}/{item_id}", json={"price": 14.99})
    assert update_resp.status_code == 200
    assert float(update_resp.json()["price"]) == 14.99


def test_integration_update_menu_item_not_found():
    response = client.put(f"{BASE}/99999", json={"price": 9.99})
    assert response.status_code == 404


def test_integration_delete_menu_item(sample_menu_item_data):
    create_resp = client.post(BASE + "/", json=sample_menu_item_data)
    item_id = create_resp.json()["id"]
    delete_resp = client.delete(f"{BASE}/{item_id}")
    assert delete_resp.status_code == 204
    get_resp = client.get(f"{BASE}/{item_id}")
    assert get_resp.status_code == 404


def test_integration_delete_menu_item_not_found():
    response = client.delete(f"{BASE}/99999")
    assert response.status_code == 404