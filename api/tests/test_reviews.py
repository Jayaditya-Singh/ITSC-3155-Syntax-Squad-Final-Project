from fastapi.testclient import TestClient
from ..controllers import reviews as controller
from ..main import app
import pytest
from ..models import reviews as model

client = TestClient(app)


@pytest.fixture
def db_session(mocker):
    return mocker.Mock()


def test_create_review_full(db_session):
    review_data = {
        "customer_id": 1,
        "order_id": 10,
        "review_text": "Great food and fast delivery!",
        "score": 5
    }
    review_obj = model.Review(**review_data)
    result = controller.create(db_session, review_obj)
    assert result is not None
    assert result.score == 5
    assert result.review_text == "Great food and fast delivery!"


def test_create_review_guest(db_session):
    review_data = {
        "customer_id": None,
        "order_id": 11,
        "review_text": "Decent, but a bit slow.",
        "score": 3
    }
    review_obj = model.Review(**review_data)
    result = controller.create(db_session, review_obj)
    assert result.customer_id is None


def test_create_review_no_text(db_session):
    review_data = {"customer_id": 2, "order_id": 12, "score": 4}
    review_obj = model.Review(**review_data)
    result = controller.create(db_session, review_obj)
    assert result.score == 4
    assert result.review_text is None


def test_read_all_reviews(db_session):
    reviews = [
        model.Review(id=1, customer_id=1, order_id=1, review_text="Excellent!", score=5),
        model.Review(id=2, customer_id=2, order_id=2, review_text="Average.", score=3),
    ]
    db_session.query.return_value.all.return_value = reviews
    result = controller.read_all(db_session)
    assert len(result) == 2


def test_read_all_reviews_empty(db_session):
    db_session.query.return_value.all.return_value = []
    result = controller.read_all(db_session)
    assert result == []


def test_read_one_review(db_session):
    review = model.Review(id=1, customer_id=1, order_id=5,
                          review_text="Loved it!", score=5)
    db_session.query.return_value.filter.return_value.first.return_value = review
    result = controller.read_one(db_session, item_id=1)
    assert result.score == 5


def test_read_one_review_not_found(db_session):
    from fastapi import HTTPException
    db_session.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(HTTPException) as exc:
        controller.read_one(db_session, item_id=999)
    assert exc.value.status_code == 404


def test_update_review(db_session, mocker):
    existing = model.Review(id=1, customer_id=1, order_id=1,
                            review_text="OK", score=3)
    mock_query = db_session.query.return_value.filter.return_value
    mock_query.first.return_value = existing
    update_data = mocker.Mock()
    update_data.dict.return_value = {"score": 5}
    result = controller.update(db_session, item_id=1, request=update_data)
    assert result is not None


def test_update_review_not_found(db_session, mocker):
    from fastapi import HTTPException
    db_session.query.return_value.filter.return_value.first.return_value = None
    update_data = mocker.Mock()
    update_data.dict.return_value = {"score": 2}
    with pytest.raises(HTTPException) as exc:
        controller.update(db_session, item_id=999, request=update_data)
    assert exc.value.status_code == 404


def test_delete_review(db_session):
    existing = model.Review(id=1, customer_id=1, order_id=1, score=4)
    db_session.query.return_value.filter.return_value.first.return_value = existing
    result = controller.delete(db_session, item_id=1)
    assert result.status_code == 204


def test_delete_review_not_found(db_session):
    from fastapi import HTTPException
    db_session.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(HTTPException) as exc:
        controller.delete(db_session, item_id=999)
    assert exc.value.status_code == 404