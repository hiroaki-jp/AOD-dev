"""DB アクセス。ORM 禁止、psycopg2 で SQL を直接書く。

- SQL は必ずプレースホルダ(%s)を使う。f-string での SQL 組み立ては禁止。
- トランザクションは `with conn:`、カーソルは `with conn.cursor() as cur:`。
"""

from __future__ import annotations

import uuid as uuid_module
from typing import Protocol
from uuid import UUID

import psycopg2
import psycopg2.extensions

from app.config import Settings
from app.models import Todo


class TodoNotFoundError(Exception):
    """todo_id に対応する TODO が存在しない場合の例外。"""


class TodoRepository(Protocol):
    def list_todos(self) -> list[Todo]:
        """Persisted TODO 一覧を返す。"""

    def add_todo(self, *, title: str) -> Todo:
        """新規 TODO を永続化して返す。"""

    def mark_todo_completed(self, *, todo_id: UUID) -> Todo:
        """既存 TODO を完了状態に更新して返す。"""


def get_connection(settings: Settings) -> psycopg2.extensions.connection:
    return psycopg2.connect(settings.database_url)


class Psycopg2TodoRepository:
    def __init__(self, conn: psycopg2.extensions.connection) -> None:
        self._conn = conn

    def list_todos(self) -> list[Todo]:
        with self._conn.cursor() as cur:
            cur.execute(
                "SELECT id, title, is_completed, created_at, updated_at"
                " FROM todos ORDER BY created_at",
            )
            return [
                Todo(
                    id=row[0],
                    title=row[1],
                    is_completed=row[2],
                    created_at=row[3],
                    updated_at=row[4],
                )
                for row in cur.fetchall()
            ]

    def add_todo(self, *, title: str) -> Todo:
        new_id = uuid_module.uuid4()
        with self._conn, self._conn.cursor() as cur:
            cur.execute(
                "INSERT INTO todos (id, title)"
                " VALUES (%s, %s)"
                " RETURNING id, title, is_completed, created_at, updated_at",
                (str(new_id), title),
            )
            row = cur.fetchone()
            assert row is not None
            return Todo(
                id=row[0],
                title=row[1],
                is_completed=row[2],
                created_at=row[3],
                updated_at=row[4],
            )

    def mark_todo_completed(self, *, todo_id: UUID) -> Todo:
        with self._conn, self._conn.cursor() as cur:
            cur.execute(
                "UPDATE todos"
                " SET is_completed = TRUE, updated_at = now()"
                " WHERE id = %s"
                " RETURNING id, title, is_completed, created_at, updated_at",
                (str(todo_id),),
            )
            row = cur.fetchone()
            if row is None:
                raise TodoNotFoundError(todo_id)
            return Todo(
                id=row[0],
                title=row[1],
                is_completed=row[2],
                created_at=row[3],
                updated_at=row[4],
            )


def get_todo_repository(conn: psycopg2.extensions.connection) -> TodoRepository:
    return Psycopg2TodoRepository(conn)
