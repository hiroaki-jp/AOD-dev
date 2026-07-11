from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import MagicMock
from uuid import UUID

from app.db import Psycopg2TodoRepository


def test_mark_todo_completed_updates_only_required_fields() -> None:
    conn = MagicMock()
    conn.__enter__.return_value = conn
    conn.__exit__.return_value = None

    cursor_cm = MagicMock()
    cursor = MagicMock()
    cursor_cm.__enter__.return_value = cursor
    cursor_cm.__exit__.return_value = None
    conn.cursor.return_value = cursor_cm

    todo_id = UUID("12345678-1234-5678-1234-567812345678")
    cursor.fetchone.return_value = (
        todo_id,
        "Test TODO",
        True,
        datetime(2024, 1, 1, tzinfo=UTC),
        datetime(2024, 1, 2, tzinfo=UTC),
    )

    repo = Psycopg2TodoRepository(conn)
    repo.mark_todo_completed(todo_id=todo_id)

    executed_sql = cursor.execute.call_args.args[0]
    assert "SET is_completed = TRUE, updated_at = now()" in executed_sql
    assert "title =" not in executed_sql
    assert "created_at =" not in executed_sql
