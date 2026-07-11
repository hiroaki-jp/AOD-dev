"""TODO API の Pydantic モデル定義。"""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, field_validator


class Todo(BaseModel):
    """契約で規定された Todo リソース表現。"""

    id: UUID
    title: str
    is_completed: bool
    created_at: datetime
    updated_at: datetime


class TodoListResponse(BaseModel):
    """`GET /api/v1/todos` のレスポンス。items 包装で将来の拡張に備える。"""

    items: list[Todo]


class CreateTodoRequest(BaseModel):
    """`POST /api/v1/todos` のリクエストボディ。"""

    title: str

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("title must not be blank")
        if len(v) > 255:
            raise ValueError("title must not exceed 255 characters")
        return v
