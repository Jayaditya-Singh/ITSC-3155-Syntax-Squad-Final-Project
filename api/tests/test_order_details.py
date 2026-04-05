from fastapi.testclient import TestClient
from ..controllers import order_details as controller
from ..main import app
import pytest
from ..models import order_details as model

client = TestClient(app)


@pytest.fixture
def db_session(mocker):
    return mocker.Mock()


def test_create_order_detail(db_session):
    detail_data = {
        "order_id": 1,
        "menu_item_id": 3,
        "amount": 2,
        "unit_price": 12.99
    }
    detail_obj = model.OrderDetail(**detail_data)
    result = controller.create(db_session, detail_obj)
    assert result is not None
    assert result.order_id == 1
    assert result.menu_item_id == 3
    assert result.amount == 2
    assert result.unit_price == 12.99


def test_read_all_order_details(db_session):
    details = [
        model.OrderDetail(id=1, order_id=1, menu_item_id=1, amount=2, unit_price=10.00),
        model.OrderDetail(id=2, order_id=1, menu_item_id=2, amount=1, unit_price=5.00),
    ]
    db_session.query.return_value.all.return_value = details
    result = controller.read_all(db_session)
    assert len(result) == 2


def test_read_all_order_details_empty(db_session):
    db_session.query.return_value.all.return_value = []
    result = controller.read_all(db_session)
    assert result == []


def test_read_one_order_detail(db_session):
    detail = model.OrderDetail(id=1, order_id=1, menu_item_id=2, amount=2, unit_price=9.99)
    db_session.query.return_value.filter.return_value.first.return_value = detail
    result = controller.read_one(db_session, item_id=1)
    assert result.menu_item_id == 2


def test_read_one_order_detail_not_found(db_session):
    from fastapi import HTTPException
    db_session.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(HTTPException) as exc:
        controller.read_one(db_session, item_id=999)
    assert exc.value.status_code == 404


def test_update_order_detail(db_session, mocker):
    existing = model.OrderDetail(id=1, order_id=1, menu_item_id=1, amount=1, unit_price=5.00)
    mock_query = db_session.query.return_value.filter.return_value
    mock_query.first.return_value = existing
    update_data = mocker.Mock()
    update_data.dict.return_value = {"amount": 3}
    result = controller.update(db_session, item_id=1, request=update_data)
    assert result is not None


def test_update_order_detail_not_found(db_session, mocker):
    from fastapi import HTTPException
    db_session.query.return_value.filter.return_value.first.return_value = None
    update_data = mocker.Mock()
    update_data.dict.return_value = {"amount": 2}
    with pytest.raises(HTTPException) as exc:
        controller.update(db_session, item_id=999, request=update_data)
    assert exc.value.status_code == 404


def test_delete_order_detail(db_session):
    existing = model.OrderDetail(id=1, order_id=1, menu_item_id=1, amount=1, unit_price=5.00)
    db_session.query.return_value.filter.return_value.first.return_value = existing
    result = controller.delete(db_session, item_id=1)
    assert result.status_code == 204


def test_delete_order_detail_not_found(db_session):
    from fastapi import HTTPException
    db_session.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(HTTPException) as exc:
        controller.delete(db_session, item_id=999)
    assert exc.value.status_code == 404