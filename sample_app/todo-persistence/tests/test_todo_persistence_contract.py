from __future__ import annotations

import ast
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MIGRATION_SQL = PROJECT_ROOT / "migrations" / "0001_initial_todo_schema.sql"
CONTRACT_PY = PROJECT_ROOT / "repository_contract.py"


def test_受入基準_ddl_に必要な列制約とindexが含まれる() -> None:
    ddl = MIGRATION_SQL.read_text(encoding="utf-8")

    assert "CREATE TABLE IF NOT EXISTS todos" in ddl
    assert "id UUID PRIMARY KEY" in ddl
    assert "title VARCHAR(255) NOT NULL" in ddl
    assert "is_completed BOOLEAN NOT NULL DEFAULT FALSE" in ddl
    assert "created_at TIMESTAMPTZ NOT NULL DEFAULT now()" in ddl
    assert "updated_at TIMESTAMPTZ NOT NULL DEFAULT now()" in ddl

    assert "CHECK (length(trim(title)) > 0)" in ddl
    assert "CHECK (char_length(title) <= 255)" in ddl

    assert "CREATE INDEX IF NOT EXISTS idx_todos_is_completed ON todos (is_completed);" in ddl
    assert "CREATE INDEX IF NOT EXISTS idx_todos_created_at ON todos (created_at);" in ddl


def test_受入基準_repository_境界は一覧追加完了のみを契約化する() -> None:
    node = ast.parse(CONTRACT_PY.read_text(encoding="utf-8"))

    todo_repository_class = next(
        class_def
        for class_def in node.body
        if isinstance(class_def, ast.ClassDef) and class_def.name == "TodoRepository"
    )
    methods = [
        method.name
        for method in todo_repository_class.body
        if isinstance(method, ast.FunctionDef)
    ]

    assert set(methods) == {"list_todos", "add_todo", "mark_todo_completed"}
