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

---

## Project Structure

The CRUD methods for each table are defined in the `api/controllers/` folder — each table has its own controller file that handles create, read, update, and delete logic.

The `api/routers/` folder pulls those controller methods in and exposes them as API endpoints, which is what shows up in the Swagger UI.