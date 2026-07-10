"""sample_app backend エントリポイント。

FastAPI の規約サンプル: レスポンスは必ず Pydantic モデルで定義する。
"""

from __future__ import annotations

import tomllib
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel


def _find_pyproject_path(start_dir: Path) -> Path:
    for directory in (start_dir, *start_dir.parents):
        pyproject_path = directory / "pyproject.toml"
        if pyproject_path.is_file():
            return pyproject_path
    msg = "pyproject.toml was not found in parent directories"
    raise FileNotFoundError(msg)


def _load_project_version() -> str:
    pyproject_path = _find_pyproject_path(Path(__file__).resolve().parent)
    try:
        with pyproject_path.open("rb") as pyproject_file:
            pyproject = tomllib.load(pyproject_file)
        return str(pyproject["project"]["version"])
    except (OSError, tomllib.TOMLDecodeError, KeyError, TypeError) as exc:
        msg = f"Failed to load project.version from {pyproject_path}: {type(exc).__name__}: {exc}"
        raise RuntimeError(msg) from exc


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
