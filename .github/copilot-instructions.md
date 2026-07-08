# Copilot Coding Agent への指示

このリポジトリは AI DevFactory(AOD)の対象プロダクト用リポジトリです。

## 作業範囲(厳守)

- 変更してよいのは **`sample_app/` フォルダ以下のみ**。`.github/` やリポジトリルートのファイルは変更しない。
- Issue 本文に `allowed_paths`(触ってよいファイル範囲)が指定されている場合は、その範囲から出ない。
- 範囲外の変更が必要だと判断した場合は、実装せずに PR 説明に理由を書く。

## 技術スタック(違反禁止)

- Frontend: React + Vite + TypeScript(**Next.js は禁止**)
- Backend: Python 3.12 + FastAPI
- DB: PostgreSQL。**ORM は禁止**。psycopg2 で SQL を直接書く
- コーディング規約の詳細: [.github/skills/coding-conventions/SKILL.md](skills/coding-conventions/SKILL.md) に従う

## 品質要件

- Python: 型ヒント必須。`mypy --strict` と `ruff check` / `ruff format` を通すこと
- TypeScript: `strict: true` でコンパイルが通ること
- Issue に受入基準がある場合、**各受入基準に対応するテストを必ず追加**する
- 既存テストを壊さない(`sample_app/backend` で pytest、`sample_app/frontend` で vitest)

## PR の書き方

- PR は Issue で指定されたブランチ(通常 develop)に向ける
- PR 説明に以下を含める:
  - 対応した Issue 番号と受入基準ごとの対応状況
  - **Assumptions セクション**: 不明点に対して置いた仮定をすべて列挙する(仮定を置いて進めてよいが、必ず明記する)
