"""TODO API エントリポイント。"""

from __future__ import annotations

from fastapi import FastAPI

from app.routers.todos import router as todos_router

app = FastAPI(title="todo-api", version="0.1.0")
app.include_router(todos_router)
