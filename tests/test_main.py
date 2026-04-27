import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# Отдельная тестовая БД в памяти
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def register_and_login(username="igor", password="secret123"):
    client.post("/auth/register", json={
        "username": username,
        "email": f"{username}@test.com",
        "password": password,
    })
    res = client.post("/auth/login", json={"username": username, "password": password})
    return res.json()["access_token"]


# ── Auth ──────────────────────────────────────────────
def test_register():
    res = client.post("/auth/register", json={
        "username": "igor",
        "email": "igor@test.com",
        "password": "secret123",
    })
    assert res.status_code == 201
    assert res.json()["username"] == "igor"


def test_register_duplicate():
    client.post("/auth/register", json={"username": "igor", "email": "igor@test.com", "password": "secret"})
    res = client.post("/auth/register", json={"username": "igor", "email": "other@test.com", "password": "secret"})
    assert res.status_code == 400


def test_login():
    token = register_and_login()
    assert token is not None


def test_login_wrong_password():
    register_and_login()
    res = client.post("/auth/login", json={"username": "igor", "password": "wrongpass"})
    assert res.status_code == 401


# ── Tasks ─────────────────────────────────────────────
def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def test_create_task():
    token = register_and_login()
    res = client.post("/tasks/", json={"title": "Выучить FastAPI", "priority": "high"}, headers=auth_headers(token))
    assert res.status_code == 201
    assert res.json()["title"] == "Выучить FastAPI"


def test_get_tasks():
    token = register_and_login()
    client.post("/tasks/", json={"title": "Задача 1"}, headers=auth_headers(token))
    client.post("/tasks/", json={"title": "Задача 2"}, headers=auth_headers(token))
    res = client.get("/tasks/", headers=auth_headers(token))
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_filter_by_status():
    token = register_and_login()
    client.post("/tasks/", json={"title": "Задача"}, headers=auth_headers(token))
    res = client.get("/tasks/?status=pending", headers=auth_headers(token))
    assert res.status_code == 200
    assert all(t["status"] == "pending" for t in res.json())


def test_update_task():
    token = register_and_login()
    task = client.post("/tasks/", json={"title": "Старый заголовок"}, headers=auth_headers(token)).json()
    res = client.put(f"/tasks/{task['id']}", json={"title": "Новый заголовок", "status": "done"}, headers=auth_headers(token))
    assert res.status_code == 200
    assert res.json()["status"] == "done"


def test_delete_task():
    token = register_and_login()
    task = client.post("/tasks/", json={"title": "Удалить меня"}, headers=auth_headers(token)).json()
    res = client.delete(f"/tasks/{task['id']}", headers=auth_headers(token))
    assert res.status_code == 204


def test_cannot_access_other_users_task():
    token1 = register_and_login("user1", "pass1")
    token2 = register_and_login("user2", "pass2")
    task = client.post("/tasks/", json={"title": "Приватная задача"}, headers=auth_headers(token1)).json()
    res = client.get(f"/tasks/{task['id']}", headers=auth_headers(token2))
    assert res.status_code == 404


def test_unauthorized_access():
    res = client.get("/tasks/")
    assert res.status_code == 401
