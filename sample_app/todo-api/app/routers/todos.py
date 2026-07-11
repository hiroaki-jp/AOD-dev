"""TODO エンドポイントのルーター。"""

from __future__ import annotations

import logging
from collections.abc import Generator
from typing import Annotated
from uuid import UUID

import psycopg2
import psycopg2.extensions
from fastapi import APIRouter, Depends, HTTPException, status

from app.config import Settings, load_settings
from app.db import TodoNotFoundError, TodoRepository, get_connection, get_todo_repository
from app.models import CreateTodoRequest, Todo, TodoListResponse

router = APIRouter(prefix="/api/v1", tags=["todos"])
logger = logging.getLogger(__name__)


def get_settings() -> Settings:
    return load_settings()


def get_conn(
    settings: Annotated[Settings, Depends(get_settings)],
) -> Generator[psycopg2.extensions.connection, None, None]:
    conn = get_connection(settings)
    try:
        yield conn
    finally:
        conn.close()


ConnDep = Annotated[psycopg2.extensions.connection, Depends(get_conn)]


def get_repo(conn: ConnDep) -> TodoRepository:
    return get_todo_repository(conn)


RepoDep = Annotated[TodoRepository, Depends(get_repo)]


@router.get("/todos", response_model=TodoListResponse)
def list_todos(repo: RepoDep) -> TodoListResponse:
    """受入基準1: 保存済み TODO の一覧を items 配列で返す。"""
    try:
        items = repo.list_todos()
        return TodoListResponse(items=items)
    except psycopg2.Error as exc:
        logger.exception("Failed to list todos")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Persistence unavailable",
        ) from exc


@router.post("/todos", response_model=Todo, status_code=status.HTTP_201_CREATED)
def create_todo(body: CreateTodoRequest, repo: RepoDep) -> Todo:
    """受入基準2: 妥当な title を受け取り 201 と作成済み TODO を返す。"""
    try:
        return repo.add_todo(title=body.title)
    except psycopg2.Error as exc:
        logger.exception("Failed to add todo")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Persistence unavailable",
        ) from exc


@router.patch("/todos/{todo_id}/complete", response_model=Todo)
def complete_todo(todo_id: UUID, repo: RepoDep) -> Todo:
    """受入基準3: 既存 TODO を完了状態に更新し 200 と更新済み TODO を返す。"""
    try:
        return repo.mark_todo_completed(todo_id=todo_id)
    except TodoNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found") from exc
    except psycopg2.Error as exc:
        logger.exception("Failed to complete todo")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Persistence unavailable",
        ) from exc
