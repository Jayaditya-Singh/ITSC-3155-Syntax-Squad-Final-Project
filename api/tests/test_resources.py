from fastapi.testclient import TestClient
from ..controllers import resources as controller
from ..main import app
import pytest
from ..models import resources as model

client = TestClient(app)


@pytest.fixture
def db_session(mocker):
    return mocker.Mock()


def test_create_resource(db_session):
    resource_data = {"name": "Flour", "amount": 500.0, "unit": "grams"}
    resource_obj = model.Resource(**resource_data)
    result = controller.create(db_session, resource_obj)
    assert result is not None
    assert result.name == "Flour"
    assert result.amount == 500.0
    assert result.unit == "grams"


def test_read_all_resources(db_session):
    resources = [
        model.Resource(id=1, name="Flour", amount=500.0, unit="grams"),
        model.Resource(id=2, name="Sugar", amount=200.0, unit="grams"),
    ]
    db_session.query.return_value.all.return_value = resources
    result = controller.read_all(db_session)
    assert len(result) == 2


def test_read_all_resources_empty(db_session):
    db_session.query.return_value.all.return_value = []
    result = controller.read_all(db_session)
    assert result == []


def test_read_one_resource(db_session):
    resource = model.Resource(id=1, name="Butter", amount=250.0, unit="grams")
    db_session.query.return_value.filter.return_value.first.return_value = resource
    result = controller.read_one(db_session, item_id=1)
    assert result.name == "Butter"


def test_read_one_resource_not_found(db_session):
    from fastapi import HTTPException
    db_session.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(HTTPException) as exc:
        controller.read_one(db_session, item_id=999)
    assert exc.value.status_code == 404


def test_update_resource(db_session, mocker):
    existing = model.Resource(id=1, name="Flour", amount=500.0, unit="grams")
    mock_query = db_session.query.return_value.filter.return_value
    mock_query.first.return_value = existing
    update_data = mocker.Mock()
    update_data.dict.return_value = {"amount": 750.0}
    result = controller.update(db_session, item_id=1, request=update_data)
    assert result is not None


def test_update_resource_not_found(db_session, mocker):
    from fastapi import HTTPException
    db_session.query.return_value.filter.return_value.first.return_value = None
    update_data = mocker.Mock()
    update_data.dict.return_value = {"amount": 100.0}
    with pytest.raises(HTTPException) as exc:
        controller.update(db_session, item_id=999, request=update_data)
    assert exc.value.status_code == 404


def test_delete_resource(db_session):
    existing = model.Resource(id=1, name="Salt", amount=100.0, unit="grams")
    db_session.query.return_value.filter.return_value.first.return_value = existing
    result = controller.delete(db_session, item_id=1)
    assert result.status_code == 204


def test_delete_resource_not_found(db_session):
    from fastapi import HTTPException
    db_session.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(HTTPException) as exc:
        controller.delete(db_session, item_id=999)
    assert exc.value.status_code == 404