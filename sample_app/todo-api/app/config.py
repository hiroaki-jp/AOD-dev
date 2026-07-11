"""環境変数の読み込みはこのモジュールに集約する(規約)。"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str


def load_settings() -> Settings:
    return Settings(
        database_url=os.environ.get(
            "DATABASE_URL", "postgresql://app:app@localhost:5432/sample_app"
        ),
    )
