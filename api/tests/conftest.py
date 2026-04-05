import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from ..main import app
from ..dependencies.database import Base, get_db

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def sample_customer_data():
    return {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "phone": "704-555-0100",
        "address": "123 Main St, Charlotte, NC"
    }


@pytest.fixture
def sample_menu_item_data():
    return {
        "name": "Margherita Pizza",
        "price": 12.99,
        "calories": 800,
        "category": "Pizza"
    }


@pytest.fixture
def sample_resource_data():
    return {
        "name": "Mozzarella",
        "amount": 500.0,
        "unit": "grams"
    }


@pytest.fixture
def sample_recipe_data():
    return {
        "menu_item_id": 1,
        "resource_id": 1,
        "amount": 150.0
    }


@pytest.fixture
def sample_promotion_data():
    return {
        "promo_code": "SAVE15",
        "discount_percent": 15.0,
        "discount_amount": None,
        "expiration_date": (datetime.now() + timedelta(days=30)).isoformat(),
        "is_active": True
    }


@pytest.fixture
def sample_order_data():
    return {
        "customer_id": None,
        "promotion_id": None,
        "order_type": "Takeout",
        "order_status": "Pending",
        "total_price": 25.98
    }


@pytest.fixture
def sample_order_detail_data():
    return {
        "order_id": 1,
        "menu_item_id": 1,
        "amount": 2,
        "unit_price": 12.99
    }


@pytest.fixture
def sample_payment_data():
    return {
        "order_id": 1,
        "payment_type": "Credit",
        "card_last_four": "4242",
        "transaction_status": "Approved"
    }


@pytest.fixture
def sample_review_data():
    return {
        "customer_id": None,
        "order_id": 1,
        "review_text": "Great food, fast delivery!",
        "score": 5
    }