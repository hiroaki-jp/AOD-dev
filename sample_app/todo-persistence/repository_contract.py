from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True)
class TodoRecord:
    id: UUID
    title: str
    is_completed: bool
    created_at: datetime
    updated_at: datetime


class TodoNotFoundError(Exception):
    """todo_id に対応する TODO が存在しない場合の repository 契約例外。"""


class TodoRepository(Protocol):
    def list_todos(self) -> list[TodoRecord]:
        """Persisted TODO 一覧を返す。"""

    def add_todo(self, *, title: str) -> TodoRecord:
        """新規 TODO を永続化して返す。"""

    def mark_todo_completed(self, *, todo_id: UUID) -> TodoRecord:
        """既存 TODO を完了状態に更新して返す。

        todo_id が存在しない場合は TodoNotFoundError を送出する。
        """
