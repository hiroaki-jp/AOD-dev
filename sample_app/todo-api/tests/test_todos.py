"""TODO API エンドポイントのスモークテスト。"""

from __future__ import annotations

from collections.abc import Generator
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch
from uuid import UUID

import psycopg2
import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.db import TodoNotFoundError
from app.main import app
from app.models import Todo
from app.routers.todos import get_repo

SAMPLE_ID = UUID("12345678-1234-5678-1234-567812345678")
SAMPLE_TODO = Todo(
    id=SAMPLE_ID,
    title="Test TODO",
    is_completed=False,
    created_at=datetime(2024, 1, 1, tzinfo=UTC),
    updated_at=datetime(2024, 1, 1, tzinfo=UTC),
)
COMPLETED_TODO = Todo(
    id=SAMPLE_ID,
    title="Test TODO",
    is_completed=True,
    created_at=datetime(2024, 1, 1, tzinfo=UTC),
    updated_at=datetime(2024, 1, 2, tzinfo=UTC),
)


@pytest.fixture(autouse=True)
def override_repo() -> Generator[MagicMock, None, None]:
    """各テストで repository を差し替え、外部依存を排除する。"""
    mock_repo = MagicMock()

    def mock_get_repo() -> MagicMock:
        return mock_repo

    app.dependency_overrides[get_repo] = mock_get_repo
    yield mock_repo
    app.dependency_overrides.clear()


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


# ---- 受入基準1: GET /api/v1/todos が items 配列を返す ----


def test_受入基準1_一覧取得が_items_配列を返す(
    client: TestClient,
    override_repo: MagicMock,
) -> None:
    override_repo.list_todos.return_value = [SAMPLE_TODO]
    res = client.get("/api/v1/todos")

    assert res.status_code == status.HTTP_200_OK
    body = res.json()
    assert "items" in body
    assert isinstance(body["items"], list)
    override_repo.list_todos.assert_called_once_with()


def test_受入基準1_一覧取得が_todo_の内容を返す(
    client: TestClient,
    override_repo: MagicMock,
) -> None:
    override_repo.list_todos.return_value = [SAMPLE_TODO]
    res = client.get("/api/v1/todos")

    items = res.json()["items"]
    assert len(items) == 1
    assert items[0]["title"] == "Test TODO"
    assert items[0]["is_completed"] is False


def test_受入基準1_一覧取得_空の場合は空配列(
    client: TestClient,
    override_repo: MagicMock,
) -> None:
    override_repo.list_todos.return_value = []
    res = client.get("/api/v1/todos")

    assert res.status_code == status.HTTP_200_OK
    assert res.json() == {"items": []}


# ---- 受入基準2: POST /api/v1/todos が 201 と作成済み TODO を返す ----


def test_受入基準2_todo追加が_201と作成済みtodoを返す(
    client: TestClient,
    override_repo: MagicMock,
) -> None:
    override_repo.add_todo.return_value = SAMPLE_TODO
    res = client.post("/api/v1/todos", json={"title": "Test TODO"})

    assert res.status_code == status.HTTP_201_CREATED
    body = res.json()
    assert body["title"] == "Test TODO"
    assert body["is_completed"] is False
    assert "id" in body
    override_repo.add_todo.assert_called_once_with(title="Test TODO")


def test_受入基準4_todo追加_空タイトルは_400(client: TestClient) -> None:
    res = client.post("/api/v1/todos", json={"title": "   "})
    assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_受入基準4_todo追加_titleなしは_422(client: TestClient) -> None:
    res = client.post("/api/v1/todos", json={})
    assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_受入基準4_todo追加_255文字超タイトルは_422(client: TestClient) -> None:
    res = client.post("/api/v1/todos", json={"title": "a" * 256})
    assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# ---- 受入基準3: PATCH /api/v1/todos/{id}/complete が 200 と更新済み TODO を返す ----


def test_受入基準3_完了更新が_200と更新済みtodoを返す(
    client: TestClient,
    override_repo: MagicMock,
) -> None:
    override_repo.mark_todo_completed.return_value = COMPLETED_TODO
    res = client.patch(f"/api/v1/todos/{SAMPLE_ID}/complete")

    assert res.status_code == status.HTTP_200_OK
    body = res.json()
    assert body["is_completed"] is True
    assert body["id"] == str(SAMPLE_ID)
    override_repo.mark_todo_completed.assert_called_once_with(todo_id=SAMPLE_ID)


def test_受入基準4_完了更新_存在しないtodoは_404(
    client: TestClient,
    override_repo: MagicMock,
) -> None:
    unknown_id = UUID("00000000-0000-0000-0000-000000000000")
    override_repo.mark_todo_completed.side_effect = TodoNotFoundError(unknown_id)
    res = client.patch(f"/api/v1/todos/{unknown_id}/complete")

    assert res.status_code == status.HTTP_404_NOT_FOUND


# ---- 受入基準5: レスポンス形状が契約の Todo / { items: Todo[] } に一致する ----


def test_受入基準5_レスポンス形状がtodo契約に一致する(
    client: TestClient,
    override_repo: MagicMock,
) -> None:
    override_repo.list_todos.return_value = [SAMPLE_TODO]
    res = client.get("/api/v1/todos")

    item = res.json()["items"][0]
    assert set(item.keys()) == {"id", "title", "is_completed", "created_at", "updated_at"}


def test_受入基準5_post_レスポンス形状がtodo契約に一致する(
    client: TestClient,
    override_repo: MagicMock,
) -> None:
    override_repo.add_todo.return_value = SAMPLE_TODO
    res = client.post("/api/v1/todos", json={"title": "Test TODO"})

    body = res.json()
    assert set(body.keys()) == {"id", "title", "is_completed", "created_at", "updated_at"}


def test_受入基準5_patch_レスポンス形状がtodo契約に一致する(
    client: TestClient,
    override_repo: MagicMock,
) -> None:
    override_repo.mark_todo_completed.return_value = COMPLETED_TODO
    res = client.patch(f"/api/v1/todos/{SAMPLE_ID}/complete")

    body = res.json()
    assert set(body.keys()) == {"id", "title", "is_completed", "created_at", "updated_at"}


def test_post_永続化失敗時は_503とログを返す(
    client: TestClient,
    override_repo: MagicMock,
) -> None:
    override_repo.add_todo.side_effect = psycopg2.Error("db failure")

    with patch("app.routers.todos.logger") as logger_mock:
        res = client.post("/api/v1/todos", json={"title": "Test TODO"})

    assert res.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert res.json()["detail"] == "Persistence unavailable"
    logger_mock.exception.assert_called_once_with("Failed to add todo")


def test_get_永続化失敗時は_503とログを返す(
    client: TestClient,
    override_repo: MagicMock,
) -> None:
    override_repo.list_todos.side_effect = psycopg2.Error("db failure")

    with patch("app.routers.todos.logger") as logger_mock:
        res = client.get("/api/v1/todos")

    assert res.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert res.json()["detail"] == "Persistence unavailable"
    logger_mock.exception.assert_called_once_with("Failed to list todos")


def test_patch_永続化失敗時は_503とログを返す(
    client: TestClient,
    override_repo: MagicMock,
) -> None:
    override_repo.mark_todo_completed.side_effect = psycopg2.Error("db failure")

    with patch("app.routers.todos.logger") as logger_mock:
        res = client.patch(f"/api/v1/todos/{SAMPLE_ID}/complete")

    assert res.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert res.json()["detail"] == "Persistence unavailable"
    logger_mock.exception.assert_called_once_with("Failed to complete todo")
