from fastapi.testclient import TestClient
from ..controllers import customers as controller
from ..main import app
import pytest
from ..models import customers as model

client = TestClient(app)


@pytest.fixture
def db_session(mocker):
    return mocker.Mock()


def test_create_customer(db_session):
    customer_data = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "phone": "704-555-0100",
        "address": "123 Main St, Charlotte, NC"
    }
    customer_obj = model.Customer(**customer_data)
    result = controller.create(db_session, customer_obj)
    assert result is not None
    assert result.name == "Jane Doe"
    assert result.email == "jane@example.com"


def test_create_customer_minimal(db_session):
    customer_data = {"name": "Guest User", "email": "guest@example.com"}
    customer_obj = model.Customer(**customer_data)
    result = controller.create(db_session, customer_obj)
    assert result is not None
    assert result.phone is None
    assert result.address is None


def test_read_all_customers(db_session):
    customers = [
        model.Customer(id=1, name="Alice", email="alice@example.com"),
        model.Customer(id=2, name="Bob", email="bob@example.com"),
    ]
    db_session.query.return_value.all.return_value = customers
    result = controller.read_all(db_session)
    assert len(result) == 2
    assert result[0].name == "Alice"


def test_read_all_customers_empty(db_session):
    db_session.query.return_value.all.return_value = []
    result = controller.read_all(db_session)
    assert result == []


def test_read_one_customer(db_session):
    customer = model.Customer(id=1, name="Alice", email="alice@example.com")
    db_session.query.return_value.filter.return_value.first.return_value = customer
    result = controller.read_one(db_session, item_id=1)
    assert result.id == 1
    assert result.name == "Alice"


def test_read_one_customer_not_found(db_session):
    from fastapi import HTTPException
    db_session.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(HTTPException) as exc:
        controller.read_one(db_session, item_id=999)
    assert exc.value.status_code == 404


def test_update_customer(db_session, mocker):
    existing = model.Customer(id=1, name="Alice", email="alice@example.com")
    mock_query = db_session.query.return_value.filter.return_value
    mock_query.first.return_value = existing
    update_data = mocker.Mock()
    update_data.dict.return_value = {"phone": "999-000-1234"}
    result = controller.update(db_session, item_id=1, request=update_data)
    assert result is not None


def test_update_customer_not_found(db_session, mocker):
    from fastapi import HTTPException
    db_session.query.return_value.filter.return_value.first.return_value = None
    update_data = mocker.Mock()
    update_data.dict.return_value = {"phone": "999-000-1234"}
    with pytest.raises(HTTPException) as exc:
        controller.update(db_session, item_id=999, request=update_data)
    assert exc.value.status_code == 404


def test_delete_customer(db_session):
    existing = model.Customer(id=1, name="Alice", email="alice@example.com")
    db_session.query.return_value.filter.return_value.first.return_value = existing
    result = controller.delete(db_session, item_id=1)
    assert result.status_code == 204


def test_delete_customer_not_found(db_session):
    from fastapi import HTTPException
    db_session.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(HTTPException) as exc:
        controller.delete(db_session, item_id=999)
    assert exc.value.status_code == 404