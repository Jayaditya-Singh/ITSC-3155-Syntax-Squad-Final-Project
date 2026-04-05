from fastapi.testclient import TestClient
from ..controllers import recipes as controller
from ..main import app
import pytest
from ..models import recipes as model

client = TestClient(app)


@pytest.fixture
def db_session(mocker):
    return mocker.Mock()


def test_create_recipe(db_session):
    recipe_data = {"menu_item_id": 1, "resource_id": 2, "amount": 150.0}
    recipe_obj = model.Recipe(**recipe_data)
    result = controller.create(db_session, recipe_obj)
    assert result is not None
    assert result.menu_item_id == 1
    assert result.resource_id == 2
    assert result.amount == 150.0


def test_read_all_recipes(db_session):
    recipes = [
        model.Recipe(id=1, menu_item_id=1, resource_id=1, amount=200.0),
        model.Recipe(id=2, menu_item_id=1, resource_id=2, amount=50.0),
    ]
    db_session.query.return_value.all.return_value = recipes
    result = controller.read_all(db_session)
    assert len(result) == 2


def test_read_all_recipes_empty(db_session):
    db_session.query.return_value.all.return_value = []
    result = controller.read_all(db_session)
    assert result == []


def test_read_one_recipe(db_session):
    recipe = model.Recipe(id=1, menu_item_id=1, resource_id=1, amount=200.0)
    db_session.query.return_value.filter.return_value.first.return_value = recipe
    result = controller.read_one(db_session, item_id=1)
    assert result.menu_item_id == 1


def test_read_one_recipe_not_found(db_session):
    from fastapi import HTTPException
    db_session.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(HTTPException) as exc:
        controller.read_one(db_session, item_id=999)
    assert exc.value.status_code == 404


def test_update_recipe(db_session, mocker):
    existing = model.Recipe(id=1, menu_item_id=1, resource_id=1, amount=100.0)
    mock_query = db_session.query.return_value.filter.return_value
    mock_query.first.return_value = existing
    update_data = mocker.Mock()
    update_data.dict.return_value = {"amount": 250.0}
    result = controller.update(db_session, item_id=1, request=update_data)
    assert result is not None


def test_update_recipe_not_found(db_session, mocker):
    from fastapi import HTTPException
    db_session.query.return_value.filter.return_value.first.return_value = None
    update_data = mocker.Mock()
    update_data.dict.return_value = {"amount": 100.0}
    with pytest.raises(HTTPException) as exc:
        controller.update(db_session, item_id=999, request=update_data)
    assert exc.value.status_code == 404


def test_delete_recipe(db_session):
    existing = model.Recipe(id=1, menu_item_id=1, resource_id=1, amount=100.0)
    db_session.query.return_value.filter.return_value.first.return_value = existing
    result = controller.delete(db_session, item_id=1)
    assert result.status_code == 204


def test_delete_recipe_not_found(db_session):
    from fastapi import HTTPException
    db_session.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(HTTPException) as exc:
        controller.delete(db_session, item_id=999)
    assert exc.value.status_code == 404