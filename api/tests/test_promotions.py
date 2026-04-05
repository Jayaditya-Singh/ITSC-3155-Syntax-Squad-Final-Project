from fastapi.testclient import TestClient
from ..controllers import promotions as controller
from ..main import app
import pytest
from ..models import promotions as model
from datetime import datetime, timedelta

client = TestClient(app)

FUTURE_DATE = datetime.now() + timedelta(days=30)


@pytest.fixture
def db_session(mocker):
    return mocker.Mock()


def test_create_promotion_percent(db_session):
    promo_data = {
        "promo_code": "SAVE15",
        "discount_percent": 15.0,
        "expiration_date": FUTURE_DATE,
        "is_active": True
    }
    promo_obj = model.Promotion(**promo_data)
    result = controller.create(db_session, promo_obj)
    assert result is not None
    assert result.promo_code == "SAVE15"
    assert result.discount_percent == 15.0


def test_create_promotion_flat_amount(db_session):
    promo_data = {
        "promo_code": "5OFF",
        "discount_amount": 5.00,
        "expiration_date": FUTURE_DATE,
        "is_active": True
    }
    promo_obj = model.Promotion(**promo_data)
    result = controller.create(db_session, promo_obj)
    assert result.discount_amount == 5.00


def test_read_all_promotions(db_session):
    promos = [
        model.Promotion(id=1, promo_code="SAVE10", discount_percent=10.0,
                        expiration_date=FUTURE_DATE, is_active=True),
        model.Promotion(id=2, promo_code="FREESHIP", discount_amount=3.99,
                        expiration_date=FUTURE_DATE, is_active=True),
    ]
    db_session.query.return_value.all.return_value = promos
    result = controller.read_all(db_session)
    assert len(result) == 2


def test_read_all_promotions_empty(db_session):
    db_session.query.return_value.all.return_value = []
    result = controller.read_all(db_session)
    assert result == []


def test_read_one_promotion(db_session):
    promo = model.Promotion(id=1, promo_code="SUMMER20", discount_percent=20.0,
                            expiration_date=FUTURE_DATE, is_active=True)
    db_session.query.return_value.filter.return_value.first.return_value = promo
    result = controller.read_one(db_session, item_id=1)
    assert result.promo_code == "SUMMER20"


def test_read_one_promotion_not_found(db_session):
    from fastapi import HTTPException
    db_session.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(HTTPException) as exc:
        controller.read_one(db_session, item_id=999)
    assert exc.value.status_code == 404


def test_read_by_code(db_session):
    promo = model.Promotion(id=1, promo_code="WELCOME", discount_percent=10.0,
                            expiration_date=FUTURE_DATE, is_active=True)
    db_session.query.return_value.filter.return_value.first.return_value = promo
    result = controller.read_by_code(db_session, promo_code="WELCOME")
    assert result.promo_code == "WELCOME"


def test_read_by_code_not_found(db_session):
    from fastapi import HTTPException
    db_session.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(HTTPException) as exc:
        controller.read_by_code(db_session, promo_code="INVALID")
    assert exc.value.status_code == 404


def test_update_promotion(db_session, mocker):
    existing = model.Promotion(id=1, promo_code="OLD10", discount_percent=10.0,
                               expiration_date=FUTURE_DATE, is_active=True)
    mock_query = db_session.query.return_value.filter.return_value
    mock_query.first.return_value = existing
    update_data = mocker.Mock()
    update_data.dict.return_value = {"is_active": False}
    result = controller.update(db_session, item_id=1, request=update_data)
    assert result is not None


def test_update_promotion_not_found(db_session, mocker):
    from fastapi import HTTPException
    db_session.query.return_value.filter.return_value.first.return_value = None
    update_data = mocker.Mock()
    update_data.dict.return_value = {"is_active": False}
    with pytest.raises(HTTPException) as exc:
        controller.update(db_session, item_id=999, request=update_data)
    assert exc.value.status_code == 404


def test_delete_promotion(db_session):
    existing = model.Promotion(id=1, promo_code="SAVE15", discount_percent=15.0,
                               expiration_date=FUTURE_DATE, is_active=True)
    db_session.query.return_value.filter.return_value.first.return_value = existing
    result = controller.delete(db_session, item_id=1)
    assert result.status_code == 204


def test_delete_promotion_not_found(db_session):
    from fastapi import HTTPException
    db_session.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(HTTPException) as exc:
        controller.delete(db_session, item_id=999)
    assert exc.value.status_code == 404