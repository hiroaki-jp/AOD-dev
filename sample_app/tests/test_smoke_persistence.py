"""スモークテスト: 追加・完了更新の結果が永続化されること。

受入基準への対応:
  2. 追加した TODO が再読み込み後も保持されること
  5. 追加・完了更新の結果が永続化され、再読み込み後も保持されること

テストプロファイル: smoke + integration (develop 向け、DATABASE_URL が必要)

DATABASE_URL 環境変数が未設定の場合はテストをスキップする。
テストデータは teardown で削除し、既存データを汚染しない。
"""

from __future__ import annotations

import os
import uuid
from collections.abc import Generator

import psycopg2
import psycopg2.extensions
import pytest

from app.config import Settings
from app.db import Psycopg2TodoRepository, get_connection


def _database_url() -> str | None:
    return os.environ.get("DATABASE_URL")


@pytest.fixture()
def db_conn() -> Generator[psycopg2.extensions.connection, None, None]:
    """テスト用 DB 接続を提供し、終了時に接続を閉じる。

    DATABASE_URL が未設定の場合はスキップ。
    接続できない場合もスキップ(CI/CD 環境でサービスが起動していない場合を想定)。
    """
    url = _database_url()
    if url is None:
        pytest.skip("DATABASE_URL が未設定のため永続化テストをスキップ")

    try:
        conn = psycopg2.connect(url)
    except psycopg2.OperationalError as exc:
        pytest.skip(f"DB に接続できないためスキップ: {exc}")

    yield conn
    conn.close()


@pytest.fixture()
def repo(
    db_conn: psycopg2.extensions.connection,
) -> Psycopg2TodoRepository:
    return Psycopg2TodoRepository(db_conn)


@pytest.fixture()
def new_conn() -> Generator[psycopg2.extensions.connection, None, None]:
    """再読み込みをシミュレートするための第 2 の DB 接続。

    同じく DATABASE_URL を使用し、再読み込み後のクライアントを模倣する。
    """
    url = _database_url()
    if url is None:  # pragma: no cover  (db_conn フィクスチャが先にスキップする)
        pytest.skip("DATABASE_URL が未設定")

    conn = psycopg2.connect(url)
    yield conn
    conn.close()


@pytest.fixture(autouse=True)
def cleanup(
    db_conn: psycopg2.extensions.connection,
) -> Generator[None, None, None]:
    """テスト終了後にテスト用タイトルプレフィックスを持つ行を削除する。"""
    yield
    with db_conn, db_conn.cursor() as cur:
        cur.execute(
            "DELETE FROM todos WHERE title LIKE %s",
            ("__smoke_test__%",),
        )


@pytest.mark.smoke
@pytest.mark.integration
def test_受入基準2_永続化_追加したtodoが再読み込み後も保持される(
    repo: Psycopg2TodoRepository,
    new_conn: psycopg2.extensions.connection,
) -> None:
    """ADD → 新しい接続で LIST → 追加した TODO が含まれること。

    「再読み込み後も保持される」= 同一 DB を新たな接続で参照したとき存在する。
    """
    title = f"__smoke_test__{uuid.uuid4()}"
    created = repo.add_todo(title=title)

    # 再読み込みをシミュレート: 別の接続・別の Repository インスタンスで取得
    reload_repo = Psycopg2TodoRepository(new_conn)
    items = reload_repo.list_todos()

    ids = [t.id for t in items]
    assert created.id in ids, "追加した TODO が新しい接続で取得できない"

    matched = next(t for t in items if t.id == created.id)
    assert matched.title == title
    assert matched.is_completed is False


@pytest.mark.smoke
@pytest.mark.integration
def test_受入基準3_永続化_完了更新が再読み込み後も保持される(
    repo: Psycopg2TodoRepository,
    new_conn: psycopg2.extensions.connection,
) -> None:
    """ADD → COMPLETE → 新しい接続で LIST → 完了状態が保持されること。"""
    title = f"__smoke_test__{uuid.uuid4()}"
    created = repo.add_todo(title=title)
    repo.mark_todo_completed(todo_id=created.id)

    reload_repo = Psycopg2TodoRepository(new_conn)
    items = reload_repo.list_todos()

    matched = next((t for t in items if t.id == created.id), None)
    assert matched is not None, "完了更新した TODO が新しい接続で取得できない"
    assert matched.is_completed is True, "完了状態が永続化されていない"


@pytest.mark.smoke
@pytest.mark.integration
def test_受入基準5_永続化_設定された_database_url_で接続できる() -> None:
    """DATABASE_URL で正常に接続できること。

    接続確立自体が最低限のスモークとして機能する。
    """
    url = _database_url()
    if url is None:
        pytest.skip("DATABASE_URL が未設定")

    settings = Settings(database_url=url)
    conn = get_connection(settings)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            row = cur.fetchone()
        assert row is not None
        assert row[0] == 1
    finally:
        conn.close()
