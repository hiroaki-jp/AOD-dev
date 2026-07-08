"""DB アクセスの規約サンプル。ORM は禁止、psycopg2 で SQL を直接書く。

- SQL は必ずプレースホルダ(%s)を使う。f-string での SQL 組み立ては禁止。
- トランザクションは `with conn:`、カーソルは `with conn.cursor() as cur:`。
"""

from __future__ import annotations

from dataclasses import dataclass

import psycopg2
import psycopg2.extensions

from app.config import Settings


@dataclass(frozen=True)
class Item:
    id: int
    name: str


def get_connection(settings: Settings) -> psycopg2.extensions.connection:
    return psycopg2.connect(settings.database_url)


def fetch_items(conn: psycopg2.extensions.connection, *, limit: int = 100) -> list[Item]:
    with conn.cursor() as cur:
        cur.execute("SELECT id, name FROM items ORDER BY id LIMIT %s", (limit,))
        return [Item(id=row[0], name=row[1]) for row in cur.fetchall()]


def insert_item(conn: psycopg2.extensions.connection, name: str) -> Item:
    with conn, conn.cursor() as cur:
        cur.execute("INSERT INTO items (name) VALUES (%s) RETURNING id", (name,))
        row = cur.fetchone()
        assert row is not None
        return Item(id=row[0], name=name)
