# DB スキーマ概要 (cycle: C-0415)

Migration version: 0001_initial_todo_schema.sql

Table: todos
- id UUID PRIMARY KEY
- title VARCHAR(255) NOT NULL
- is_completed BOOLEAN NOT NULL DEFAULT FALSE
- created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
- updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()

Constraints:
- PRIMARY KEY (id)
- CHECK (length(trim(title)) > 0)
- CHECK (char_length(title) <= 255)

Indexes:
- CREATE INDEX idx_todos_is_completed ON todos (is_completed)
- CREATE INDEX idx_todos_created_at ON todos (created_at)

Design notes:
- Single-user, no user_id column.
- No soft delete, no version column, no history table in this initial contract.
- Updates for completion should modify is_completed and updated_at only.
- ORM definitions are out of scope; emit raw DDL only.

## 横断的な留意事項

- API error responses must be machine-detectable and suitable for UI notifications; use a consistent error envelope across validation and not-found cases.
- Maintain logging for request validation failures and persistence errors at minimum; logs should include request correlation if available, but no auth context is required.
- Frontend should optimistically avoid extra flows; after successful create/complete, refresh list state from API response or refetch GET /todos.
- Contract-first rule: OpenAPI is the source of truth; generated FastAPI schema must be diffed in CI and changes classified as breaking/non-breaking.
- Keep snake_case in DB, JSON field names may use snake_case as well to reduce translation overhead across FastAPI/React boundary.
- Since this is a placeholder initial design, there are no existing contract changes; all items are additive only.
