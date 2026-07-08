from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_version_returns_current_version() -> None:
    res = client.get("/version")
    assert res.status_code == 200
    assert res.json() == {"version": "0.1.0"}
