from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_info_returns_name_and_version() -> None:
    res = client.get("/info")
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("application/json")
    assert res.json() == {"name": app.title, "version": app.version}
