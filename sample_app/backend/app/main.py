"""sample_app backend エントリポイント。

FastAPI の規約サンプル: レスポンスは必ず Pydantic モデルで定義する。
"""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from app import APP_VERSION
from app.routers import version

app = FastAPI(title="sample-app", version=APP_VERSION)
app.include_router(version.router)


class HealthResponse(BaseModel):
    status: str


@app.get("/healthz", response_model=HealthResponse)
def healthz() -> HealthResponse:
    return HealthResponse(status="ok")
