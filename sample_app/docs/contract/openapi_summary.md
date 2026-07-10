# OpenAPI 概要 (cycle: C-0415)

Version: 1.0.0. Contract-first. Existing contract changes: none in this placeholder initial design. New API surface added for TODO management.

Base path: /api/v1

Endpoints:
- GET /todos
  - summary: TODO 一覧取得
  - response 200: application/json object { items: Todo[] }
- POST /todos
  - summary: TODO 新規追加
  - request body: application/json { title: string }
  - response 201: application/json Todo
  - error 400: validation error
- PATCH /todos/{todo_id}/complete
  - summary: TODO 完了更新
  - path param todo_id: integer/UUID (implementation-specific, but stable within contract)
  - response 200: application/json Todo
  - error 404: target not found
  - error 400: validation error

Shared schema:
- Todo:
  - id: string|integer (stable identifier)
  - title: string
  - is_completed: boolean
  - created_at: string(date-time)
  - updated_at: string(date-time)

Notes:
- No edit/delete/search/sort/due date/user/auth fields.
- info.version must be kept in sync with contract revision and CI schema diff checks.
- Response shapes intentionally keep a single resource representation for list/create/complete to minimize UI coupling.

## モジュール

- module:todo-api (FastAPI) — responsibility: TODO 一覧取得・新規追加・完了更新の HTTP 契約を提供する。depends on: persistence abstraction only; no UI dependency.
- module:todo-web (React) — responsibility: TODO 一覧/追加/完了更新の画面を提供し、todo-api を呼び出して状態を同期する。depends on: todo-api contract only.
- module:todo-persistence (DB/Repository boundary) — responsibility: TODO の永続化と取得。depends on: database schema only; no HTTP/UI dependency.
