"""バージョン情報エンドポイント。"""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app import APP_VERSION

router = APIRouter()


class VersionResponse(BaseModel):
    version: str


@router.get("/version", response_model=VersionResponse)
def get_version() -> VersionResponse:
    return VersionResponse(version=APP_VERSION)
