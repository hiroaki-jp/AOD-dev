# DB スキーマ概要 (cycle: C-0119)

migration_version: 0001
schema:
  table todo_items
    - id uuid primary key
    - title varchar(255) not null
    - description text null
    - is_completed boolean not null default false
    - created_at timestamptz not null default now()
    - updated_at timestamptz not null default now()
constraints:
  - check (char_length(title) > 0)
indexes:
  - idx_todo_items_is_completed on (is_completed)
notes:
  - ORM前提ではなく生DDLで管理
  - 既存テーブルなしの新規追加のみ

## 横断的な留意事項

- APIのエラー応答はJSONで統一し、少なくとも code / message / details を返すこと。
- TODO一覧はテスト容易性のため、デフォルトで安定した並び順(created_at ASC, id ASC)を採用すること。
- 監査・ログ用に、各書き込み系APIはリクエスト結果(成功/失敗)を構造化ログ出力可能な形にすること。
- 認証・認可は別途未定義のため、現段階では契約に含めない。後続タスクで追加する場合はbreaking判定に注意すること。
- 返却するTODOの必須フィールドは id/title/is_completed/created_at/updated_at とし、description は任意(nullable)とする。
