# sample_app — AOD 対象プロダクト雛形

AI DevFactory が開発する対象プロダクトのテンプレート。固定アーキテクチャ:

- Frontend: React + Vite + TypeScript(Next.js 禁止)
- Backend: Python 3.12 + FastAPI
- DB: PostgreSQL 18(ORM 禁止、psycopg2 で SQL 直書き)+ Redis

## 起動

```bash
cd sample_app
docker compose up --build
# backend:  http://localhost:8000/healthz
# frontend: http://localhost:5173
```

## 開発(ローカル)

```bash
# backend
cd backend
python -m venv venv && venv/Scripts/activate   # Windows(Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt -r requirements-dev.txt
pytest && ruff check . && mypy app tests
uvicorn app.main:app --reload

# frontend
cd frontend
npm install
npm run dev     # 開発サーバー(API は :8000 へプロキシ)
npm test        # vitest
npm run build   # 型チェック + ビルド
```

## 規約

[.github/skills/coding-conventions/SKILL.md](../.github/skills/coding-conventions/SKILL.md) を参照。
CI のテストプロファイル(smoke / standard / release)は [.github/workflows/ci.yml](../.github/workflows/ci.yml) を参照。
