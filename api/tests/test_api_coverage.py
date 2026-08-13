"""Integration coverage for the API blueprints (evaluations, reports,
submissions edges, auth validation)."""

import pytest
from src.app import create_app
from src.database import engine, Base
from src.blueprints.auth import _reset_rate_limits


@pytest.fixture
def client():
    app = create_app()
    with app.test_client() as c:
        yield c


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(engine)
    _reset_rate_limits()
    yield
    Base.metadata.drop_all(engine)
    _reset_rate_limits()


def _auth(client, email="u@example.com", password="password123"):
    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    return resp.get_json()["data"]["access_token"]


def _submit(client, token, code="def f(x):\n    return x\n", language="python"):
    resp = client.post(
        "/api/v1/submissions",
        json={"code": code, "language": language},
        headers={"Authorization": f"Bearer {token}"},
    )
    return resp.get_json()["data"]["id"]


# ---- Evaluations ----

def test_run_evaluation_success(client):
    token = _auth(client)
    sid = _submit(client, token)
    resp = client.post(f"/api/v1/evaluations/{sid}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert data["overall_score"] is not None
    assert data["analysis_status"] == "ok"


def test_run_evaluation_idempotent(client):
    token = _auth(client)
    sid = _submit(client, token)
    client.post(f"/api/v1/evaluations/{sid}", headers={"Authorization": f"Bearer {token}"})
    resp = client.post(f"/api/v1/evaluations/{sid}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.get_json()["data"]["message"] == "Analysis already completed"


def test_run_evaluation_syntax_error(client):
    token = _auth(client)
    sid = _submit(client, token, code="def broken(:\n    pass")
    resp = client.post(f"/api/v1/evaluations/{sid}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 422
    assert resp.get_json()["error_type"] == "syntax_error"


def test_run_evaluation_type_error(client):
    token = _auth(client)
    sid = _submit(client, token, code="function add(a: number, b: number) { return a+b; }\nadd('x', 2);", language="typescript")
    resp = client.post(f"/api/v1/evaluations/{sid}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 422
    assert resp.get_json()["error_type"] == "type_error"


def test_get_evaluation(client):
    token = _auth(client)
    sid = _submit(client, token)
    client.post(f"/api/v1/evaluations/{sid}", headers={"Authorization": f"Bearer {token}"})
    resp = client.get(f"/api/v1/evaluations/{sid}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.get_json()["data"]["submission_id"] == sid


def test_get_evaluation_not_found(client):
    token = _auth(client)
    resp = client.get("/api/v1/evaluations/9999", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 404


def test_evaluation_unauthorized(client):
    resp = client.post("/api/v1/evaluations/1")
    assert resp.status_code == 401


# ---- Reports ----

def test_export_jsonl(client):
    token = _auth(client)
    sid = _submit(client, token)
    client.post(f"/api/v1/evaluations/{sid}", headers={"Authorization": f"Bearer {token}"})
    resp = client.get(
        f"/api/v1/reports/{sid}/export?format=jsonl",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.headers["Content-Type"].startswith("application/x-jsonl")
    assert "report_" in resp.headers.get("Content-Disposition", "")


def test_export_markdown(client):
    token = _auth(client)
    sid = _submit(client, token)
    client.post(f"/api/v1/evaluations/{sid}", headers={"Authorization": f"Bearer {token}"})
    resp = client.get(
        f"/api/v1/reports/{sid}/export",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.headers["Content-Type"].startswith("text/markdown")
    assert "# Code Review Report" in resp.get_data(as_text=True)


def test_export_not_found(client):
    token = _auth(client)
    resp = client.get(f"/api/v1/reports/9999/export", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 404


def test_export_unauthorized(client):
    resp = client.get("/api/v1/reports/1/export")
    assert resp.status_code == 401


# ---- Submissions edges ----

def test_create_submission_empty_code(client):
    token = _auth(client)
    resp = client.post("/api/v1/submissions", json={"code": "", "language": "python"}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 400
    assert resp.get_json()["error_type"] == "validation_error"


def test_create_submission_unsupported_language(client):
    token = _auth(client)
    resp = client.post("/api/v1/submissions", json={"code": "x=1", "language": "rust"}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 400
    assert resp.get_json()["error_type"] == "unsupported_language"


def test_get_specific_submission(client):
    token = _auth(client)
    sid = _submit(client, token)
    resp = client.get(f"/api/v1/submissions/{sid}", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.get_json()["data"]["id"] == sid


def test_get_submission_not_found(client):
    token = _auth(client)
    resp = client.get("/api/v1/submissions/9999", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 404


def test_list_submissions_empty(client):
    token = _auth(client)
    resp = client.get("/api/v1/submissions", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200


# ---- Auth validation ----

def test_register_bad_email(client):
    resp = client.post("/api/v1/auth/register", json={"email": "notanemail", "password": "password123"})
    assert resp.status_code == 400
    assert resp.get_json()["error_type"] == "validation_error"


def test_register_short_password(client):
    resp = client.post("/api/v1/auth/register", json={"email": "a@b.com", "password": "short"})
    assert resp.status_code == 400


def test_register_missing_fields(client):
    resp = client.post("/api/v1/auth/register", json={"email": "a@b.com"})
    assert resp.status_code == 400


def test_login_validation_bad_email(client):
    resp = client.post("/api/v1/auth/login", json={"email": "bad", "password": "password123"})
    assert resp.status_code == 400


def test_register_rate_limit(client):
    # Rate limit is per client IP; use unique emails so only the limit applies.
    statuses = []
    for i in range(25):
        r = client.post(
            "/api/v1/auth/register",
            json={"email": f"rl{i}@example.com", "password": "password123"},
        )
        statuses.append(r.status_code)
    assert 429 in statuses
    assert all(s in (201, 400, 409, 429) for s in statuses)
