from fastapi.testclient import TestClient
from ..controllers import orders as controller
from ..main import app
import pytest
from ..models import orders as model

client = TestClient(app)


@pytest.fixture
def db_session(mocker):
    return mocker.Mock()


def test_create_order(db_session):
    order_data = {
        "customer_id": 1,
        "order_type": "Delivery",
        "order_status": "Pending",
        "total_price": 25.50,
        "tracking_number": "ABC12345"
    }
    order_obj = model.Order(**order_data)
    result = controller.create(db_session, order_obj)
    assert result is not None
    assert result.customer_id == 1
    assert result.order_type == "Delivery"


def test_create_guest_order(db_session):
    order_data = {
        "customer_id": None,
        "order_type": "Takeout",
        "order_status": "Pending",
        "total_price": 10.00,
        "tracking_number": "GUEST001"
    }
    order_obj = model.Order(**order_data)
    result = controller.create(db_session, order_obj)
    assert result is not None
    assert result.customer_id is None


def test_read_all_orders(db_session):
    orders = [
        model.Order(id=1, customer_id=1, order_type="Takeout",
                    order_status="Complete", total_price=15.00),
        model.Order(id=2, customer_id=2, order_type="Delivery",
                    order_status="Pending", total_price=30.00),
    ]
    db_session.query.return_value.all.return_value = orders
    result = controller.read_all(db_session)
    assert len(result) == 2


def test_read_all_orders_empty(db_session):
    db_session.query.return_value.all.return_value = []
    result = controller.read_all(db_session)
    assert result == []


def test_read_one_order(db_session):
    order = model.Order(id=5, customer_id=1, order_type="Takeout",
                        order_status="Preparing", total_price=22.00,
                        tracking_number="TRK00005")
    db_session.query.return_value.filter.return_value.first.return_value = order
    result = controller.read_one(db_session, item_id=5)
    assert result.id == 5
    assert result.order_status == "Preparing"


def test_read_one_order_not_found(db_session):
    from fastapi import HTTPException
    db_session.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(HTTPException) as exc:
        controller.read_one(db_session, item_id=999)
    assert exc.value.status_code == 404


def test_read_by_tracking_number(db_session):
    order = model.Order(id=1, tracking_number="ABC12345",
                        order_status="Out for Delivery", total_price=20.00)
    db_session.query.return_value.filter.return_value.first.return_value = order
    result = controller.read_by_tracking(db_session, tracking_number="ABC12345")
    assert result.tracking_number == "ABC12345"


def test_read_by_tracking_not_found(db_session):
    from fastapi import HTTPException
    db_session.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(HTTPException) as exc:
        controller.read_by_tracking(db_session, tracking_number="INVALID")
    assert exc.value.status_code == 404


def test_update_order_status(db_session, mocker):
    existing = model.Order(id=1, order_status="Pending", total_price=20.00)
    mock_query = db_session.query.return_value.filter.return_value
    mock_query.first.return_value = existing
    update_data = mocker.Mock()
    update_data.dict.return_value = {"order_status": "Complete"}
    result = controller.update(db_session, item_id=1, request=update_data)
    assert result is not None


def test_update_order_not_found(db_session, mocker):
    from fastapi import HTTPException
    db_session.query.return_value.filter.return_value.first.return_value = None
    update_data = mocker.Mock()
    update_data.dict.return_value = {"order_status": "Complete"}
    with pytest.raises(HTTPException) as exc:
        controller.update(db_session, item_id=999, request=update_data)
    assert exc.value.status_code == 404


def test_delete_order(db_session):
    existing = model.Order(id=1, order_type="Takeout", total_price=15.00)
    db_session.query.return_value.filter.return_value.first.return_value = existing
    result = controller.delete(db_session, item_id=1)
    assert result.status_code == 204


def test_delete_order_not_found(db_session):
    from fastapi import HTTPException
    db_session.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(HTTPException) as exc:
        controller.delete(db_session, item_id=999)
    assert exc.value.status_code == 404