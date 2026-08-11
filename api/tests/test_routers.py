"""Tests for API blueprints."""

import pytest
from src.app import create_app
from src.database import engine, Base


@pytest.fixture
def app():
    app = create_app()
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


def test_register(client):
    resp = client.post("/api/v1/auth/register", json={
        "email": "new@example.com",
        "password": "securepass123",
    })
    assert resp.status_code == 201
    assert resp.get_json()["status"] == "ok"
    assert resp.get_json()["data"]["email"] == "new@example.com"


def test_register_duplicate(client):
    client.post("/api/v1/auth/register", json={
        "email": "dup@example.com",
        "password": "securepass123",
    })
    resp = client.post("/api/v1/auth/register", json={
        "email": "dup@example.com",
        "password": "securepass123",
    })
    assert resp.status_code == 409
    assert resp.get_json()["status"] == "error"
    assert resp.get_json()["error_type"] == "conflict"


def test_login(client):
    client.post("/api/v1/auth/register", json={
        "email": "login@example.com",
        "password": "securepass123",
    })
    resp = client.post("/api/v1/auth/login", json={
        "email": "login@example.com",
        "password": "securepass123",
    })
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"
    assert "access_token" in resp.get_json()["data"]


def test_login_invalid(client):
    client.post("/api/v1/auth/register", json={
        "email": "valid@example.com",
        "password": "securepass123",
    })
    resp = client.post("/api/v1/auth/login", json={
        "email": "valid@example.com",
        "password": "wrongpassword",
    })
    assert resp.status_code == 401
    assert resp.get_json()["status"] == "error"
    assert resp.get_json()["error_type"] == "invalid_credentials"


def test_create_submission(client):
    client.post("/api/v1/auth/register", json={
        "email": "sub@example.com",
        "password": "securepass123",
    })
    login = client.post("/api/v1/auth/login", json={
        "email": "sub@example.com",
        "password": "securepass123",
    })
    token = login.get_json()["data"]["access_token"]

    resp = client.post("/api/v1/submissions", json={
        "code": "def hello(): return 'world'",
        "language": "python",
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 201
    assert resp.get_json()["data"]["language"] == "python"


def test_list_submissions(client):
    client.post("/api/v1/auth/register", json={
        "email": "list@example.com",
        "password": "securepass123",
    })
    login = client.post("/api/v1/auth/login", json={
        "email": "list@example.com",
        "password": "securepass123",
    })
    token = login.get_json()["data"]["access_token"]

    client.post("/api/v1/submissions", json={
        "code": "x = 1",
        "language": "python",
    }, headers={"Authorization": f"Bearer {token}"})

    resp = client.get("/api/v1/submissions", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert len(resp.get_json()) >= 1


def test_unauthorized_access(client):
    resp = client.get("/api/v1/submissions")
    assert resp.status_code == 401


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"
