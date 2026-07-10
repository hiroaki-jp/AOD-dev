# OpenAPI 概要 (cycle: C-0119)

version: 1.0.0
scope: TODO管理APIのcontract-first定義
paths:
  GET /todos: TODO一覧取得。200でTODO配列を返す。完了/未完了を区別できるレスポンス必須項目を含む。
  POST /todos: TODO新規追加。201で作成済みTODOを返す。必須入力不足は400、形式不正は422相当で表現。
  PATCH /todos/{todo_id}/complete: 指定TODOを完了済みに更新。200で更新後TODOを返す。存在しないIDは404、既に完了済みは409を返す。
models:
  Todo:
    id: string(uuid)
    title: string
    description: string|null
    is_completed: boolean
    created_at: string(date-time)
    updated_at: string(date-time)
  TodoCreateRequest:
    title: string
    description: string|null
  TodoCompleteResponse: Todo
error responses:
  400: 必須項目不足などのリクエスト妥当性エラー
  404: TODO未存在
  409: 完了済みTODOへの重複完了要求
breaking: 既存契約なしのため該当なし

## モジュール

- todo-api: TODOの一覧取得・新規追加・完了更新を提供するAPI境界。依存先は永続化層(リポジトリ)のみとし、内部のアプリケーション層/ドメイン層は実装側に委ねる。
- todo-storage: TODOエンティティの永続化と参照を担うDB境界。API層からのみ依存され、他モジュールへは依存しない。
