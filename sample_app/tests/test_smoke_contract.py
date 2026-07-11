"""スモークテスト: API 契約とフロントエンドの利用方法の一致を確認する。

受入基準への対応:
  1. GET / POST / PATCH の API 契約と画面側の利用方法が一致していること
  3. 不正入力と未存在 TODO のエラー応答が期待どおりであること

テストプロファイル: smoke (develop 向け、DB 不要)

フロントエンド(src/api/todos.ts)が期待するインターフェース:
  - GET  /api/v1/todos               → { items: Todo[] }
  - POST /api/v1/todos               → Todo  (body: { title })
  - PATCH /api/v1/todos/{id}/complete → Todo

Todo フィールド: id, title, is_completed, created_at, updated_at
"""

from __future__ import annotations

from collections.abc import Generator
from datetime import UTC, datetime
from unittest.mock import MagicMock
from uuid import UUID

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.db import TodoNotFoundError
from app.main import app
from app.models import Todo
from app.routers.todos import get_repo

# 契約で定義された Todo フィールドセット (openapi_summary.md / TypeScript Todo 型に一致)
_TODO_FIELDS = {"id", "title", "is_completed", "created_at", "updated_at"}

SAMPLE_ID = UUID("12345678-1234-5678-1234-567812345678")
SAMPLE_TODO = Todo(
    id=SAMPLE_ID,
    title="Buy groceries",
    is_completed=False,
    created_at=datetime(2024, 1, 1, tzinfo=UTC),
    updated_at=datetime(2024, 1, 1, tzinfo=UTC),
)
COMPLETED_TODO = Todo(
    id=SAMPLE_ID,
    title="Buy groceries",
    is_completed=True,
    created_at=datetime(2024, 1, 1, tzinfo=UTC),
    updated_at=datetime(2024, 1, 2, tzinfo=UTC),
)


@pytest.fixture(autouse=True)
def mock_repo() -> Generator[MagicMock, None, None]:
    """各テストで TodoRepository を差し替えて外部依存を排除する。"""
    repo = MagicMock()

    def _get_repo() -> MagicMock:
        return repo

    app.dependency_overrides[get_repo] = _get_repo
    yield repo
    app.dependency_overrides.clear()


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


# ---- 受入基準1: GET /api/v1/todos が frontend の listTodos() と一致する ----


@pytest.mark.smoke
def test_受入基準1_契約_get_todos_returns_items_wrapper(
    client: TestClient, mock_repo: MagicMock
) -> None:
    """GET /api/v1/todos のレスポンスが { items: [] } 形式であること。

    frontend: listTodos() → res.json() → { items: Todo[] }
    """
    mock_repo.list_todos.return_value = []

    res = client.get("/api/v1/todos")

    assert res.status_code == status.HTTP_200_OK
    body = res.json()
    assert "items" in body
    assert isinstance(body["items"], list)


@pytest.mark.smoke
def test_受入基準1_契約_get_todos_todo_shape_matches_frontend_type(
    client: TestClient, mock_repo: MagicMock
) -> None:
    """GET /api/v1/todos の各 Todo フィールドが TypeScript の Todo 型と一致すること。

    frontend Todo type: { id, title, is_completed, created_at, updated_at }
    """
    mock_repo.list_todos.return_value = [SAMPLE_TODO]

    res = client.get("/api/v1/todos")

    items = res.json()["items"]
    assert len(items) == 1
    assert set(items[0].keys()) == _TODO_FIELDS
    assert items[0]["title"] == "Buy groceries"
    assert items[0]["is_completed"] is False


# ---- 受入基準1: POST /api/v1/todos が frontend の createTodo() と一致する ----


@pytest.mark.smoke
def test_受入基準2_契約_post_todos_accepts_title_body_and_returns_201(
    client: TestClient, mock_repo: MagicMock
) -> None:
    """POST /api/v1/todos が { title } ボディを受け取り 201 と Todo を返すこと。

    frontend: createTodo(title) → POST { title } → res.json() as Todo
    """
    mock_repo.add_todo.return_value = SAMPLE_TODO

    res = client.post("/api/v1/todos", json={"title": "Buy groceries"})

    assert res.status_code == status.HTTP_201_CREATED
    body = res.json()
    assert set(body.keys()) == _TODO_FIELDS
    assert body["title"] == "Buy groceries"
    assert body["is_completed"] is False
    mock_repo.add_todo.assert_called_once_with(title="Buy groceries")


# ---- 受入基準1: PATCH /api/v1/todos/{id}/complete が frontend の completeTodo() と一致する ----


@pytest.mark.smoke
def test_受入基準3_契約_patch_complete_returns_200_with_todo_shape(
    client: TestClient, mock_repo: MagicMock
) -> None:
    """PATCH /api/v1/todos/{id}/complete が 200 と完了済み Todo を返すこと。

    frontend: completeTodo(id) → PATCH /api/v1/todos/{id}/complete → res.json() as Todo
    """
    mock_repo.mark_todo_completed.return_value = COMPLETED_TODO

    res = client.patch(f"/api/v1/todos/{SAMPLE_ID}/complete")

    assert res.status_code == status.HTTP_200_OK
    body = res.json()
    assert set(body.keys()) == _TODO_FIELDS
    assert body["is_completed"] is True
    mock_repo.mark_todo_completed.assert_called_once_with(todo_id=SAMPLE_ID)


# ---- 受入基準3: 不正入力と未存在 TODO のエラー応答 ----


@pytest.mark.smoke
def test_受入基準4_契約_empty_title_returns_422(client: TestClient) -> None:
    """空白タイトルの POST は 422 Unprocessable Entity を返すこと。"""
    res = client.post("/api/v1/todos", json={"title": "   "})
    assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.smoke
def test_受入基準4_契約_title_absent_returns_422(client: TestClient) -> None:
    """title フィールドなしの POST は 422 Unprocessable Entity を返すこと。"""
    res = client.post("/api/v1/todos", json={})
    assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.smoke
def test_受入基準4_契約_title_too_long_returns_422(client: TestClient) -> None:
    """255 文字超タイトルの POST は 422 Unprocessable Entity を返すこと。"""
    res = client.post("/api/v1/todos", json={"title": "a" * 256})
    assert res.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.smoke
def test_受入基準4_契約_nonexistent_todo_complete_returns_404(
    client: TestClient, mock_repo: MagicMock
) -> None:
    """存在しない todo_id への PATCH は 404 Not Found を返すこと。"""
    unknown_id = UUID("00000000-0000-0000-0000-000000000000")
    mock_repo.mark_todo_completed.side_effect = TodoNotFoundError(unknown_id)

    res = client.patch(f"/api/v1/todos/{unknown_id}/complete")

    assert res.status_code == status.HTTP_404_NOT_FOUND
