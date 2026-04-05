# Online Restaurant Ordering System — API

A FastAPI + SQLAlchemy REST API for an online restaurant ordering system, backed by MySQL.

---

## Setup

### Install dependencies
pip install fastapi
pip install "uvicorn[standard]"
pip install sqlalchemy
pip install pymysql
pip install pytest
pip install pytest-mock
pip install httpx
pip install cryptography

### Configure the database
Edit api/dependencies/config.py with your MySQL credentials:
    db_host = "localhost"
    db_name = "restaurant_ordering_api"
    db_port = 3306
    db_user = "root"
    db_password = "password"

### Run the server
uvicorn api.main:app --reload

### Interactive API docs
http://127.0.0.1:8000/docs