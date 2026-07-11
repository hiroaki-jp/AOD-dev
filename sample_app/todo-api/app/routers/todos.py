"""TODO エンドポイントのルーター。"""

from __future__ import annotations

from collections.abc import Generator
from typing import Annotated
from uuid import UUID

import psycopg2.extensions
from fastapi import APIRouter, Depends, HTTPException, status

from app import db as todo_db
from app.config import Settings, load_settings
from app.db import TodoNotFoundError, get_connection
from app.models import CreateTodoRequest, Todo, TodoListResponse

router = APIRouter(prefix="/api/v1", tags=["todos"])


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


@router.get("/todos", response_model=TodoListResponse)
def list_todos(conn: ConnDep) -> TodoListResponse:
    """受入基準1: 保存済み TODO の一覧を items 配列で返す。"""
    items = todo_db.list_todos(conn)
    return TodoListResponse(items=items)


@router.post("/todos", response_model=Todo, status_code=status.HTTP_201_CREATED)
def create_todo(body: CreateTodoRequest, conn: ConnDep) -> Todo:
    """受入基準2: 妥当な title を受け取り 201 と作成済み TODO を返す。"""
    return todo_db.add_todo(conn, title=body.title)


@router.patch("/todos/{todo_id}/complete", response_model=Todo)
def complete_todo(todo_id: UUID, conn: ConnDep) -> Todo:
    """受入基準3: 既存 TODO を完了状態に更新し 200 と更新済み TODO を返す。"""
    try:
        return todo_db.mark_todo_completed(conn, todo_id=todo_id)
    except TodoNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found") from exc
