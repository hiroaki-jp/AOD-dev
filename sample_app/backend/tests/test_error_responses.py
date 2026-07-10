"""エラーレスポンスが JSON 形式で返ることを検証するテスト。"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient

from app.exception_handlers import unhandled_exception_handler, validation_exception_handler
from app.main import app

# テスト専用 app: メイン app を汚染しないよう独立したインスタンスを使う
_test_app = FastAPI()
_test_app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
_test_app.add_exception_handler(Exception, unhandled_exception_handler)


@_test_app.get("/test-http-error")
def raise_http_error() -> None:
    raise HTTPException(status_code=400, detail="bad request")


@_test_app.get("/test-server-error")
def raise_server_error() -> None:
    raise RuntimeError("意図的なサーバーエラー")


@_test_app.get("/test-validation-error")
def require_int_param(value: int) -> dict[str, int]:
    return {"value": value}


# raise_server_exceptions=False にすることで 500 を例外でなくレスポンスとして受け取る
_client = TestClient(_test_app, raise_server_exceptions=False)
_main_client = TestClient(app)


def test_not_found_returns_json() -> None:
    """存在しないエンドポイントへのリクエストが JSON 形式の 404 を返すこと"""
    res = _main_client.get("/nonexistent-path")
    assert res.status_code == 404
    assert res.headers["content-type"].startswith("application/json")
    assert "detail" in res.json()


def test_http_exception_returns_json() -> None:
    """HTTPException が JSON 形式で返ること"""
    res = _client.get("/test-http-error")
    assert res.status_code == 400
    assert res.headers["content-type"].startswith("application/json")
    body = res.json()
    assert body == {"detail": "bad request"}


def test_validation_error_returns_json() -> None:
    """バリデーションエラー (422) が JSON 形式で返ること"""
    res = _client.get("/test-validation-error")  # value クエリパラメータなし
    assert res.status_code == 422
    assert res.headers["content-type"].startswith("application/json")
    body = res.json()
    assert "detail" in body


def test_unhandled_exception_returns_json() -> None:
    """未処理例外が JSON 形式の 500 を返すこと"""
    res = _client.get("/test-server-error")
    assert res.status_code == 500
    assert res.headers["content-type"].startswith("application/json")
    body = res.json()
    assert "detail" in body

