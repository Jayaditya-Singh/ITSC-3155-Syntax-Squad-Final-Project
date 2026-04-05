from fastapi.testclient import TestClient
from ..controllers import menu_items as controller
from ..main import app
import pytest
from ..models import menu_items as model

client = TestClient(app)


@pytest.fixture
def db_session(mocker):
    return mocker.Mock()


def test_create_menu_item(db_session):
    item_data = {
        "name": "Margherita Pizza",
        "price": 12.99,
        "calories": 800,
        "category": "Pizza"
    }
    item_obj = model.MenuItem(**item_data)
    result = controller.create(db_session, item_obj)
    assert result is not None
    assert result.name == "Margherita Pizza"
    assert result.price == 12.99
    assert result.calories == 800
    assert result.category == "Pizza"


def test_create_menu_item_no_optional_fields(db_session):
    item_data = {"name": "House Burger", "price": 9.99}
    item_obj = model.MenuItem(**item_data)
    result = controller.create(db_session, item_obj)
    assert result is not None
    assert result.calories is None
    assert result.category is None


def test_read_all_menu_items(db_session):
    items = [
        model.MenuItem(id=1, name="Pasta", price=11.00, category="Pasta"),
        model.MenuItem(id=2, name="Salad", price=7.50, category="Salads"),
    ]
    db_session.query.return_value.all.return_value = items
    result = controller.read_all(db_session)
    assert len(result) == 2
    assert result[0].name == "Pasta"


def test_read_all_menu_items_empty(db_session):
    db_session.query.return_value.all.return_value = []
    result = controller.read_all(db_session)
    assert result == []


def test_read_one_menu_item(db_session):
    item = model.MenuItem(id=3, name="Tiramisu", price=6.50, category="Desserts")
    db_session.query.return_value.filter.return_value.first.return_value = item
    result = controller.read_one(db_session, item_id=3)
    assert result.name == "Tiramisu"


def test_read_one_menu_item_not_found(db_session):
    from fastapi import HTTPException
    db_session.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(HTTPException) as exc:
        controller.read_one(db_session, item_id=999)
    assert exc.value.status_code == 404


def test_update_menu_item(db_session, mocker):
    existing = model.MenuItem(id=1, name="Old Name", price=5.00)
    mock_query = db_session.query.return_value.filter.return_value
    mock_query.first.return_value = existing
    update_data = mocker.Mock()
    update_data.dict.return_value = {"price": 6.50}
    result = controller.update(db_session, item_id=1, request=update_data)
    assert result is not None


def test_update_menu_item_not_found(db_session, mocker):
    from fastapi import HTTPException
    db_session.query.return_value.filter.return_value.first.return_value = None
    update_data = mocker.Mock()
    update_data.dict.return_value = {"price": 9.99}
    with pytest.raises(HTTPException) as exc:
        controller.update(db_session, item_id=999, request=update_data)
    assert exc.value.status_code == 404


def test_delete_menu_item(db_session):
    existing = model.MenuItem(id=1, name="Soup", price=4.50)
    db_session.query.return_value.filter.return_value.first.return_value = existing
    result = controller.delete(db_session, item_id=1)
    assert result.status_code == 204


def test_delete_menu_item_not_found(db_session):
    from fastapi import HTTPException
    db_session.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(HTTPException) as exc:
        controller.delete(db_session, item_id=999)
    assert exc.value.status_code == 404