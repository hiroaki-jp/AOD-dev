"""sample_app backend エントリポイント。

FastAPI の規約サンプル: レスポンスは必ず Pydantic モデルで定義する。
"""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="sample-app", version="0.1.0")


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime


@app.get("/healthz", response_model=HealthResponse)
def healthz() -> HealthResponse:
    return HealthResponse(status="ok", timestamp=datetime.now(UTC))
