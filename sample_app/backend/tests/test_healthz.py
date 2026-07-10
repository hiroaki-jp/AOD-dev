import re

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# ISO 8601 UTC パターン(例: 2026-07-10T15:00:00+00:00 または 2026-07-10T15:00:00Z)
_ISO8601_UTC_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?"
    r"(\+00:00|Z)$"
)


def test_healthz_returns_ok() -> None:
    res = client.get("/healthz")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_healthz_timestamp_is_iso8601_utc() -> None:
    """受入基準1: レスポンスに ISO 8601 形式の UTC タイムスタンプが含まれる。"""
    res = client.get("/healthz")
    assert res.status_code == 200
    body = res.json()
    assert "timestamp" in body, "timestamp フィールドが存在しない"
    assert _ISO8601_UTC_RE.match(body["timestamp"]), (
        f"timestamp が ISO 8601 UTC 形式でない: {body['timestamp']}"
    )


def test_healthz_status_field_preserved() -> None:
    """受入基準2: 既存の status フィールドが維持されている。"""
    res = client.get("/healthz")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"
