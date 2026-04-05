from fastapi.testclient import TestClient
from ..controllers import payments as controller
from ..main import app
import pytest
from ..models import payments as model

client = TestClient(app)


@pytest.fixture
def db_session(mocker):
    return mocker.Mock()


def test_create_payment_credit(db_session):
    payment_data = {
        "order_id": 1,
        "payment_type": "Credit",
        "card_last_four": "4242",
        "transaction_status": "Approved"
    }
    payment_obj = model.Payment(**payment_data)
    result = controller.create(db_session, payment_obj)
    assert result is not None
    assert result.payment_type == "Credit"
    assert result.card_last_four == "4242"
    assert result.transaction_status == "Approved"


def test_create_payment_cash(db_session):
    payment_data = {
        "order_id": 2,
        "payment_type": "Cash",
        "card_last_four": None,
        "transaction_status": "Approved"
    }
    payment_obj = model.Payment(**payment_data)
    result = controller.create(db_session, payment_obj)
    assert result.card_last_four is None


def test_read_all_payments(db_session):
    payments = [
        model.Payment(id=1, order_id=1, payment_type="Credit",
                      card_last_four="4242", transaction_status="Approved"),
        model.Payment(id=2, order_id=2, payment_type="Cash",
                      transaction_status="Approved"),
    ]
    db_session.query.return_value.all.return_value = payments
    result = controller.read_all(db_session)
    assert len(result) == 2


def test_read_all_payments_empty(db_session):
    db_session.query.return_value.all.return_value = []
    result = controller.read_all(db_session)
    assert result == []


def test_read_one_payment(db_session):
    payment = model.Payment(id=1, order_id=5, payment_type="Debit",
                            card_last_four="9999", transaction_status="Approved")
    db_session.query.return_value.filter.return_value.first.return_value = payment
    result = controller.read_one(db_session, item_id=1)
    assert result.card_last_four == "9999"


def test_read_one_payment_not_found(db_session):
    from fastapi import HTTPException
    db_session.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(HTTPException) as exc:
        controller.read_one(db_session, item_id=999)
    assert exc.value.status_code == 404


def test_read_payment_by_order(db_session):
    payment = model.Payment(id=1, order_id=7, payment_type="Credit",
                            card_last_four="1111", transaction_status="Approved")
    db_session.query.return_value.filter.return_value.first.return_value = payment
    result = controller.read_by_order(db_session, order_id=7)
    assert result.order_id == 7


def test_read_payment_by_order_not_found(db_session):
    from fastapi import HTTPException
    db_session.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(HTTPException) as exc:
        controller.read_by_order(db_session, order_id=999)
    assert exc.value.status_code == 404


def test_update_payment_status(db_session, mocker):
    existing = model.Payment(id=1, order_id=1, payment_type="Credit",
                             card_last_four="4242", transaction_status="Pending")
    mock_query = db_session.query.return_value.filter.return_value
    mock_query.first.return_value = existing
    update_data = mocker.Mock()
    update_data.dict.return_value = {"transaction_status": "Approved"}
    result = controller.update(db_session, item_id=1, request=update_data)
    assert result is not None


def test_update_payment_not_found(db_session, mocker):
    from fastapi import HTTPException
    db_session.query.return_value.filter.return_value.first.return_value = None
    update_data = mocker.Mock()
    update_data.dict.return_value = {"transaction_status": "Declined"}
    with pytest.raises(HTTPException) as exc:
        controller.update(db_session, item_id=999, request=update_data)
    assert exc.value.status_code == 404


def test_delete_payment(db_session):
    existing = model.Payment(id=1, order_id=1, payment_type="Cash",
                             transaction_status="Approved")
    db_session.query.return_value.filter.return_value.first.return_value = existing
    result = controller.delete(db_session, item_id=1)
    assert result.status_code == 204


def test_delete_payment_not_found(db_session):
    from fastapi import HTTPException
    db_session.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(HTTPException) as exc:
        controller.delete(db_session, item_id=999)
    assert exc.value.status_code == 404