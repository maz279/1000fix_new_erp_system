"""test_clickhouse_client.py - ClickHouse HTTP client and embedded OLAP engine.

The live server is never contacted: ``urllib.request.urlopen`` is replaced by a
scripted fake (status / body / exception per call). The embedded engine runs on the
per-test sqlite file provided by ``conftest.isolated_warehouse``.
"""

from __future__ import annotations

import datetime
import hashlib
import json
import logging
import sqlite3
import tempfile
import urllib.error
import urllib.request
from typing import ClassVar

import pytest
from clickhouse_client import ClickHouseClient


class FakeResponse:
    """Minimal context-manager stand-in for an ``http.client.HTTPResponse``."""

    def __init__(self, status: int = 200, body: str = "") -> None:
        self.status = status
        self._body = body.encode("utf-8")

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *exc: object) -> bool:
        return False


class ScriptedTransport:
    """Replays one scripted response (or raises one exception) per call,
    standing in for the stdlib HTTP entry point the client uses."""

    def __init__(self, *script: FakeResponse | BaseException) -> None:
        self.script = list(script)
        self.calls: list[tuple[urllib.request.Request, float]] = []

    def __call__(self, req: urllib.request.Request, timeout: float) -> FakeResponse:
        self.calls.append((req, timeout))
        item = self.script.pop(0)
        if isinstance(item, BaseException):
            raise item
        return item


@pytest.fixture
def fake_transport(monkeypatch):
    """Patches the client's stdlib HTTP entry point with a scripted fake.

    No request leaves the process: the transport is replaced, so the
    client's ping/query calls are answered from the script."""

    def install(*script: FakeResponse | BaseException) -> ScriptedTransport:
        fake = ScriptedTransport(*script)
        monkeypatch.setattr("urllib.request.urlopen", fake)
        return fake

    return install


@pytest.fixture
def embedded():
    """A client pinned to the embedded engine (as after a failed ping)."""
    client = ClickHouseClient()
    client._is_live_server = False
    yield client
    client.close()


def _headers(req: urllib.request.Request) -> dict[str, str]:
    return dict(req.header_items())


# --------------------------------------------------------------------------- ping


def test_is_connected_true_on_http_200(fake_transport):
    fake = fake_transport(FakeResponse(200, "Ok."))
    client = ClickHouseClient(host="ch.local", port=8124)

    assert client.is_connected() is True
    assert client._is_live_server is True
    req, timeout = fake.calls[0]
    assert req.full_url == "http://ch.local:8124/ping"
    assert timeout == 1.0


def test_is_connected_false_on_non_200_status(fake_transport):
    fake_transport(FakeResponse(503, "busy"))
    client = ClickHouseClient()

    assert client.is_connected() is False
    assert client._is_live_server is False


def test_is_connected_false_and_logged_when_unreachable(fake_transport, caplog):
    caplog.set_level(logging.DEBUG, logger="clickhouse_client")
    fake_transport(urllib.error.URLError("connection refused"))
    client = ClickHouseClient()

    assert client.is_connected() is False
    assert client._is_live_server is False
    assert "ClickHouse ping failed" in caplog.text


# ----------------------------------------------------------------- HTTP execute


def test_execute_http_format_json_returns_data_rows_and_sends_credentials(fake_transport):
    body = json.dumps({"meta": [], "data": [{"cnt": 7}], "rows": 1})
    fake = fake_transport(FakeResponse(200, "Ok."), FakeResponse(200, body))
    client = ClickHouseClient(host="ch", port=9000, user="analyst", password="pw", timeout=2.5)

    rows = client.execute("  SELECT count(*) AS cnt FROM t FORMAT JSON  ")

    assert rows == [{"cnt": 7}]
    req, timeout = fake.calls[1]
    assert req.full_url == "http://ch:9000/?database=fix_analytics"
    assert req.get_method() == "POST"
    assert req.data == b"SELECT count(*) AS cnt FROM t FORMAT JSON"
    assert timeout == 2.5
    headers = _headers(req)
    assert headers["X-clickhouse-user"] == "analyst"
    assert headers["X-clickhouse-key"] == "pw"


def test_execute_http_omits_credential_headers_when_blank(fake_transport):
    fake = fake_transport(FakeResponse(200, "Ok."), FakeResponse(200, "Ok."))
    client = ClickHouseClient(user="", password="")

    assert client.execute("CREATE DATABASE IF NOT EXISTS fix_analytics") == 1
    headers = _headers(fake.calls[1][0])
    assert "X-clickhouse-user" not in headers
    assert "X-clickhouse-key" not in headers


def test_execute_http_default_user_without_password_sends_user_only(fake_transport):
    fake = fake_transport(FakeResponse(200, "Ok."), FakeResponse(200, ""))
    client = ClickHouseClient()

    assert client.execute("INSERT INTO t VALUES (1)") == 0  # empty body -> 0
    headers = _headers(fake.calls[1][0])
    assert headers["X-clickhouse-user"] == "default"
    assert "X-clickhouse-key" not in headers


def test_execute_http_non_json_body_for_format_json_returns_1(fake_transport, caplog):
    caplog.set_level(logging.DEBUG, logger="clickhouse_client")
    fake_transport(FakeResponse(200, "Ok."), FakeResponse(200, "Code: 62. Syntax error"))
    client = ClickHouseClient()

    assert client.execute("SELECT 1 FORMAT JSON") == 1
    assert "not JSON" in caplog.text


def test_execute_http_json_each_row_returns_every_row(fake_transport):
    """Regression: FORMAT JSONEachRow (NDJSON) was parsed as one JSON document,
    returning 1 (multi-row) or [] (single row) instead of the rows."""
    fake_transport(FakeResponse(200, "Ok."), FakeResponse(200, '{"k":1}\n{"k":2}\n'))
    client = ClickHouseClient()

    assert client.execute("SELECT k FROM t FORMAT JSONEachRow") == [{"k": 1}, {"k": 2}]


def test_execute_http_failure_falls_back_to_embedded_and_labels_it(fake_transport, caplog):
    fake_transport(FakeResponse(200, "Ok."), urllib.error.URLError("reset by peer"))
    client = ClickHouseClient()

    assert client.execute("SELECT 42 AS answer") == [{"answer": 42}]
    # GV-009: the fallback is loud - an ERROR carrying mode=sqlite-fallback -
    # and the client's mode labels every subsequent result as SQLite data.
    assert "mode=sqlite-fallback" in caplog.text
    assert "NOT ClickHouse data" in caplog.text
    assert client.mode == "sqlite-fallback"
    client.close()


def test_execute_http_failure_raises_when_fallback_disabled(fake_transport):
    fake_transport(FakeResponse(200, "Ok."), urllib.error.URLError("reset by peer"))
    client = ClickHouseClient(use_fallback_if_unreachable=False)

    with pytest.raises(urllib.error.URLError, match="reset by peer"):
        client.execute("SELECT 1")
    assert client._fallback_db is None  # the embedded engine was never touched


def test_execute_pings_only_once(fake_transport):
    fake = fake_transport(urllib.error.URLError("down"))
    client = ClickHouseClient()

    assert client.execute("SELECT 1 AS a") == [{"a": 1}]
    assert client.execute("SELECT 2 AS a") == [{"a": 2}]
    assert len(fake.calls) == 1  # unreachable result is cached
    assert client.mode == "sqlite-fallback"
    client.close()


def test_live_results_are_labelled_clickhouse(fake_transport):
    body = json.dumps({"meta": [], "data": [{"cnt": 7}], "rows": 1})
    fake_transport(FakeResponse(200, "Ok."), FakeResponse(200, body))
    client = ClickHouseClient()

    assert client.execute("SELECT count(*) AS cnt FROM t FORMAT JSON") == [{"cnt": 7}]
    assert client.mode == "clickhouse"
    assert client._fallback_db is None


# --------------------------------------------------------------------- inserts


def test_insert_rows_empty_is_noop_without_ping(fake_transport):
    fake = fake_transport()
    client = ClickHouseClient()

    assert client.insert_rows("fix_analytics.t", []) == 0
    assert fake.calls == []
    assert client._is_live_server is None


class _FakeHTTPConn:
    """Scripted http.client.HTTPConnection for the SSRF-safe insert path."""

    calls: ClassVar[list[tuple[str, str, bytes, dict]]] = []
    next_status: ClassVar[int] = 200
    raise_error: ClassVar[bool] = False

    def __init__(self, host, port, timeout=None):
        self.host, self.port = host, port

    def request(self, method, path, body=None, headers=None):
        _FakeHTTPConn.calls.append((method, path, body or b"", dict(headers or {})))

    def getresponse(self):
        if _FakeHTTPConn.raise_error:
            raise OSError("connection refused")
        resp = type("R", (), {"status": _FakeHTTPConn.next_status, "read": lambda s: b"Ok."})()
        return resp

    def close(self):
        pass


def _install_http(monkeypatch, status=200, raise_error=False):
    _FakeHTTPConn.calls = []
    _FakeHTTPConn.next_status = status
    _FakeHTTPConn.raise_error = raise_error
    monkeypatch.setattr("http.client.HTTPConnection", _FakeHTTPConn)
    return _FakeHTTPConn


def test_insert_rows_http_posts_json_each_row(fake_transport, monkeypatch):
    fake = _install_http(monkeypatch)
    fake_transport(FakeResponse(200, "Ok."))  # the ping still uses urlopen
    client = ClickHouseClient()
    rows = [{"k": 1, "d": datetime.date(2025, 6, 1)}, {"k": 2, "d": datetime.date(2025, 6, 2)}]

    assert client.insert_rows("fix_analytics.t", rows) == 2
    method, path, body, headers = fake.calls[0]
    assert method == "POST"
    assert path.startswith("/?database=fix_analytics")
    assert "INSERT%20INTO%20t%20FORMAT%20JSONEachRow" in path  # table is identifier-split
    lines = [json.loads(line) for line in body.decode("utf-8").splitlines()]
    assert lines == [{"k": 1, "d": "2025-06-01"}, {"k": 2, "d": "2025-06-02"}]
    assert headers["X-ClickHouse-User"] == "default"  # auth present (R01 fix)
    assert client._fallback_db is None


def test_insert_rows_http_non_200_lands_in_embedded_and_is_labelled(fake_transport, caplog):
    fake_transport(FakeResponse(200, "Ok."), FakeResponse(202, ""))
    client = ClickHouseClient()

    assert client.insert_rows("fix_analytics.t", [{"k": 1}]) == 1
    assert "mode=sqlite-fallback" in caplog.text
    assert client.mode == "sqlite-fallback"
    client._is_live_server = False
    assert client.execute("SELECT k FROM t") == [{"k": 1}]
    client.close()


def test_insert_rows_http_error_falls_back_to_embedded(fake_transport, monkeypatch, caplog):
    _install_http(monkeypatch, raise_error=True)
    fake_transport(FakeResponse(200, "Ok."))
    client = ClickHouseClient()

    assert client.insert_rows("t", [{"k": 5, "v": "x"}]) == 1
    assert "HTTP insert into t failed" in caplog.text
    assert client.mode == "sqlite-fallback"
    client._is_live_server = False
    assert client.execute("SELECT k, v FROM t") == [{"k": 5, "v": "x"}]
    client.close()


def test_insert_rows_http_error_raises_when_fallback_disabled(fake_transport, monkeypatch):
    _install_http(monkeypatch, raise_error=True)
    fake_transport(FakeResponse(200, "Ok."))
    client = ClickHouseClient(use_fallback_if_unreachable=False)

    with pytest.raises(OSError):
        client.insert_rows("t", [{"k": 1}])
    assert client._fallback_db is None


def test_insert_rows_embedded_infers_column_types(embedded):
    rows = [{"i": 1, "f": 1.5, "s": "x", "n": None}, {"i": 2, "f": 2.5, "s": "y", "n": None}]

    assert embedded.insert_rows("fix_analytics.typed", rows) == 2
    info = embedded.execute("PRAGMA table_info(typed)")
    assert {c["name"]: c["type"] for c in info} == {
        "i": "INTEGER",
        "f": "REAL",
        "s": "TEXT",
        "n": "TEXT",
    }
    assert embedded.execute("SELECT i, f, s FROM typed ORDER BY i") == [
        {"i": 1, "f": 1.5, "s": "x"},
        {"i": 2, "f": 2.5, "s": "y"},
    ]


# ------------------------------------------------------------- embedded engine


def test_embedded_db_path_honours_env(embedded, isolated_warehouse):
    embedded.execute("SELECT 1")
    assert isolated_warehouse.db_path.exists()


def test_embedded_db_default_path_is_in_tempdir(monkeypatch, tmp_path):
    monkeypatch.delenv("CLICKHOUSE_EMBEDDED_PATH")
    monkeypatch.setattr(tempfile, "gettempdir", lambda: str(tmp_path))
    client = ClickHouseClient()
    client._is_live_server = False

    client.execute("SELECT 1")
    assert (tmp_path / "1000fix_analytics_embedded.db").exists()
    client.close()


def test_embedded_clickhouse_compat_functions(embedded):
    rows = embedded.execute(
        "SELECT toYYYYMM('2025-06-15') AS ym, toYYYYMM(NULL) AS ym_null, "
        "toDate('2025-06-15 10:30:00') AS d, toDate(NULL) AS d_null, "
        "md5('abc') AS h, md5(NULL) AS h_null"
    )
    assert rows == [
        {
            "ym": 202506,
            "ym_null": 0,
            "d": "2025-06-15",
            "d_null": None,
            "h": hashlib.md5(b"abc", usedforsecurity=False).hexdigest(),
            "h_null": "",
        }
    ]


def test_embedded_create_database_is_noop(embedded):
    assert embedded.execute("CREATE DATABASE IF NOT EXISTS fix_analytics;") == 1
    assert embedded.execute("SELECT name FROM sqlite_master") == []


def test_embedded_create_table_translates_clickhouse_ddl(embedded):
    ddl = """
    CREATE TABLE IF NOT EXISTS fix_analytics.ch_types (
        a UInt64, b UInt32, c Int32, d Int64, e UInt8,
        f Float64, g Float32, h Decimal(12, 2),
        i String, j FixedString(3), k Date, l DateTime,
        m Nullable(String), n LowCardinality(String)
    ) ENGINE = MergeTree()
    PARTITION BY toYYYYMM(k)
    ORDER BY (a, k);
    """
    assert embedded.execute(ddl) == 1
    info = embedded.execute("PRAGMA table_info(ch_types)")
    assert [(c["name"], c["type"]) for c in info] == [
        ("a", "INTEGER"),
        ("b", "INTEGER"),
        ("c", "INTEGER"),
        ("d", "INTEGER"),
        ("e", "INTEGER"),
        ("f", "REAL"),
        ("g", "REAL"),
        ("h", "REAL"),
        ("i", "TEXT"),
        ("j", "TEXT"),
        ("k", "TEXT"),
        ("l", "TEXT"),
        ("m", "TEXT"),
        ("n", "TEXT"),
    ]


def test_embedded_query_strips_qualifiers_format_and_binds_params(embedded):
    embedded.insert_rows("t", [{"k": 1, "v": "a"}, {"k": 2, "v": "b"}])

    assert embedded.execute("SELECT count(*) AS n FROM fix_analytics.t") == [{"n": 2}]
    assert embedded.execute("SELECT count(*) AS n FROM default.t") == [{"n": 2}]
    assert embedded.execute("SELECT v FROM t WHERE k = :k FORMAT JSON", {"k": 2}) == [{"v": "b"}]
    assert embedded.execute("SELECT v FROM t ORDER BY k FORMAT JSONEachRow;") == [
        {"v": "a"},
        {"v": "b"},
    ]


def test_embedded_dml_returns_rowcount(embedded):
    embedded.insert_rows("t", [{"k": 1, "v": "a"}, {"k": 2, "v": "b"}, {"k": 3, "v": "c"}])

    assert embedded.execute("UPDATE t SET v = 'z' WHERE k >= 2") == 2
    assert embedded.execute("DELETE FROM t WHERE k = 1") == 1
    assert embedded.execute("SELECT k, v FROM t ORDER BY k") == [
        {"k": 2, "v": "z"},
        {"k": 3, "v": "z"},
    ]


def test_embedded_query_error_is_logged_and_raised(embedded, caplog):
    caplog.set_level(logging.DEBUG, logger="clickhouse_client")

    with pytest.raises(sqlite3.OperationalError, match="no such table"):
        embedded.execute("SELECT * FROM missing_table")
    assert "Embedded query error on: SELECT * FROM missing_table" in caplog.text
    assert embedded._fallback_db.in_transaction is False


def test_embedded_failed_dml_rolls_back_and_releases_lock(embedded):
    """Regression: a DML statement failing inside its implicit transaction left that
    transaction (and its RESERVED lock) open on the shared file."""
    embedded.execute("CREATE TABLE pk (id INTEGER PRIMARY KEY, v TEXT)")
    embedded.execute("INSERT INTO pk VALUES (1, 'a')")

    with pytest.raises(sqlite3.IntegrityError):
        embedded.execute("INSERT INTO pk VALUES (1, 'dup')")
    assert embedded._fallback_db.in_transaction is False

    other = ClickHouseClient()
    other._is_live_server = False
    other._get_fallback_conn().execute("PRAGMA busy_timeout = 200")
    assert other.execute("INSERT INTO pk VALUES (2, 'b')") == 1
    other.close()
    assert embedded.execute("SELECT id, v FROM pk ORDER BY id") == [
        {"id": 1, "v": "a"},
        {"id": 2, "v": "b"},
    ]


def test_regression_embedded_dml_is_committed_for_other_clients(isolated_warehouse):
    """Regression for 'sqlite3.OperationalError: database is locked'.

    execute() ran INSERT/UPDATE/DELETE inside sqlite3's implicit (legacy-mode)
    transaction and never committed: the writing client kept a RESERVED lock, so
    any other client of the same file failed with "database is locked" on its next
    write, other clients could not see the row, and the row was lost on close.
    """
    writer = ClickHouseClient()
    writer._is_live_server = False
    writer.insert_rows("shared", [{"k": 1}])
    assert writer.execute("INSERT INTO shared (k) VALUES (2)") == 1
    assert writer._fallback_db.in_transaction is False

    reader = ClickHouseClient()
    reader._is_live_server = False
    reader._get_fallback_conn().execute("PRAGMA busy_timeout = 200")  # fail fast
    assert reader.execute("SELECT count(*) AS n FROM shared") == [{"n": 2}]
    assert reader.insert_rows("shared", [{"k": 3}]) == 1  # no "database is locked"

    writer.close()
    reader.close()
    fresh = ClickHouseClient()
    fresh._is_live_server = False
    assert fresh.execute("SELECT k FROM shared ORDER BY k") == [{"k": 1}, {"k": 2}, {"k": 3}]
    fresh.close()


def test_embedded_truncate_translates_to_delete(embedded):
    embedded.insert_rows("fix_analytics.t", [{"k": 1}, {"k": 2}])

    assert embedded.execute("TRUNCATE TABLE IF EXISTS fix_analytics.t") == 2
    assert embedded.execute("SELECT count(*) AS n FROM t") == [{"n": 0}]
    embedded.insert_rows("t", [{"k": 3}])
    assert embedded.execute('TRUNCATE TABLE "t";') == 1
    assert embedded.execute("SELECT count(*) AS n FROM t") == [{"n": 0}]  # schema kept


def test_embedded_truncate_if_exists_on_missing_table_is_noop(embedded):
    assert embedded.execute("TRUNCATE TABLE IF EXISTS fix_analytics.never_created") == 0


def test_embedded_truncate_without_if_exists_on_missing_table_raises(embedded):
    with pytest.raises(sqlite3.OperationalError, match="no such table"):
        embedded.execute("TRUNCATE TABLE never_created")


def test_close_releases_connection_and_reopens_lazily(embedded):
    embedded.insert_rows("t", [{"k": 1}])
    conn = embedded._fallback_db

    embedded.close()
    assert embedded._fallback_db is None
    with pytest.raises(sqlite3.ProgrammingError):
        conn.execute("SELECT 1")
    embedded.close()  # idempotent
    assert embedded.execute("SELECT k FROM t") == [{"k": 1}]  # reopened, data persisted
