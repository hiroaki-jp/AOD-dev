---
name: coding-conventions
description: 対象プロダクト(sample_app)のコーディング規約。Python/FastAPI/psycopg2 と React/TypeScript の書き方、テスト規約、PR 規約を定める。
---

# コーディング規約(sample_app)

## Python(backend)

- Python 3.12。すべての関数・メソッドに型ヒントを付け、`mypy --strict` を通す。
- lint/format は ruff(設定は `sample_app/backend/pyproject.toml`)。
- **ORM 禁止**。DB アクセスは psycopg2 で SQL を直接書く:
  - SQL は必ずプレースホルダ(`%s`)を使う。文字列結合・f-string での SQL 組み立ては禁止(SQL インジェクション防止)。
  - 接続・トランザクションの持ち方は `app/db.py` のサンプルに従う(`with conn:` でトランザクション、`with conn.cursor() as cur:` でカーソル)。
- FastAPI:
  - リクエスト/レスポンスは必ず Pydantic モデルで定義する(dict を直接返さない)。
  - ルーターは機能単位で分割し `app/routers/` に置く。
  - 環境変数の読み込みは設定モジュールに集約する(ハンドラ内で `os.environ` を直接読まない)。
- 例外: 想定内のエラーは `HTTPException` に変換。裸の `except Exception: pass` は禁止。

## TypeScript / React(frontend)

- **Next.js 禁止**。Vite + React + TypeScript(`strict: true`)。
- 関数コンポーネント + フックのみ(クラスコンポーネント禁止)。
- API 呼び出しは `src/api/` に集約し、レスポンス型を定義する(`any` 禁止)。
- 状態は最小限に。サーバー状態とローカル UI 状態を混ぜない。

## テスト

- backend: pytest。`sample_app/backend/tests/` に置く。
  - ユニットテスト(マーカーなし): 外部依存なしで動くこと。
  - DB 等が必要な統合テストには `@pytest.mark.integration` を付ける。
  - E2E には `@pytest.mark.e2e` を付ける。
- frontend: vitest。テストは対象ファイルの隣に `*.test.ts(x)` で置く。
- 受入基準 1 項目につき最低 1 テスト。テスト名は受入基準がわかる日本語または説明的な英語にする。

## 命名・構成

- Python: モジュール/関数 snake_case、クラス PascalCase、定数 UPPER_SNAKE。
- TypeScript: 変数/関数 camelCase、コンポーネント/型 PascalCase、ファイルはコンポーネント名に一致。
- マジックナンバーは定数化。コメントは「なぜ」を書く(「何をしているか」の逐語コメントは書かない)。

## コミット・PR

- 1 PR = 1 Issue。無関係なリファクタリングを混ぜない。
- PR 説明に受入基準への対応状況と Assumptions セクション(置いた仮定の列挙)を必ず含める。
