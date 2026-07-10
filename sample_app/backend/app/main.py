"""sample_app backend エントリポイント。

FastAPI の規約サンプル: レスポンスは必ず Pydantic モデルで定義する。
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel

from app.exception_handlers import unhandled_exception_handler, validation_exception_handler

app = FastAPI(title="sample-app", version="0.1.0")

app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(Exception, unhandled_exception_handler)


class HealthResponse(BaseModel):
    status: str


@app.get("/healthz", response_model=HealthResponse)
def healthz() -> HealthResponse:
    return HealthResponse(status="ok")
