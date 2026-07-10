"""sample_app backend エントリポイント。

FastAPI の規約サンプル: レスポンスは必ず Pydantic モデルで定義する。
"""

from __future__ import annotations

import tomllib
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel


def _load_project_version() -> str:
    pyproject_path = Path(__file__).resolve().parent.parent / "pyproject.toml"
    with pyproject_path.open("rb") as pyproject_file:
        pyproject = tomllib.load(pyproject_file)
    return str(pyproject["project"]["version"])


app = FastAPI(title="sample-app", version=_load_project_version())


class HealthResponse(BaseModel):
    status: str


class InfoResponse(BaseModel):
    name: str
    version: str


@app.get("/healthz", response_model=HealthResponse)
def healthz() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/info", response_model=InfoResponse)
def info() -> InfoResponse:
    return InfoResponse(name=app.title, version=app.version)
