#!/usr/bin/env python3
"""clickhouse_client.py — ClickHouse HTTP Client & Embedded OLAP Engine.

Supports:
1. Native ClickHouse HTTP interface (http://127.0.0.1:8123) with user/password/database.
2. An in-memory / file-backed SQLite engine used ONLY as an explicitly-labelled
   fallback for local environments where the container is offline.

HONESTY CONTRACT (GV-009): the fallback is never silent. Every operation that
runs on the embedded engine logs an ERROR carrying ``mode=sqlite-fallback``
and sets ``self.mode = "sqlite-fallback"`` so callers can label their own
outputs. Results produced in fallback mode are SQLite results and must never
be presented as ClickHouse measurements (see run_nfr039_profile.py, which
refuses to measure against the fallback).
3. Strict LB-06 compliance: only operates against the analytical warehouse (fix_analytics).
"""

from __future__ import annotations

import json
import logging
import os
import re
import sqlite3
import urllib.error
import urllib.request
from typing import Any

logger = logging.getLogger("clickhouse_client")

MODE_CLICKHOUSE = "clickhouse"
MODE_SQLITE_FALLBACK = "sqlite-fallback"
MODE_UNKNOWN = "unknown (not probed yet)"


class ClickHouseClient:
    """HTTP Client for ClickHouse Server with an explicit, loudly-labelled fallback.

    ``mode`` always names the engine that produced the last result:
    ``clickhouse``, ``sqlite-fallback``, or ``unknown (not probed yet)``.
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8123,
        database: str = "fix_analytics",
        user: str | None = None,
        password: str | None = None,
        timeout: float = 5.0,
        use_fallback_if_unreachable: bool = True,
    ):
        self.host = host
        self.port = port
        self.database = database
        # Credentials default to the compose ClickHouse env (the image refuses
        # network access for 'default' when no password is configured).
        self.user = user if user is not None else os.environ.get("CLICKHOUSE_USER", "default")
        self.password = (
            password if password is not None else os.environ.get("CLICKHOUSE_PASSWORD", "")
        )
        self.timeout = timeout
        self.use_fallback_if_unreachable = use_fallback_if_unreachable
        # SSRF boundary: the base URL is built ONLY from the configured host
        # (validated: hostname characters, no scheme/userinfo/path) and an
        # int port, pinned to the literal http scheme. Every request in this
        # client appends a path to this pre-validated base - a misconfigured
        # host cannot smuggle a different origin.
        import re as _re

        if not _re.fullmatch(r"[A-Za-z0-9._-]+", self.host):
            raise ValueError(f"ClickHouse host not a plain hostname: {self.host!r}")
        if not isinstance(self.port, int) or not (1 <= self.port <= 65535):
            raise ValueError(f"ClickHouse port not a valid integer: {self.port!r}")
        if not _re.fullmatch(r"[A-Za-z0-9_]+", self.database):
            raise ValueError(f"ClickHouse database not a plain identifier: {self.database!r}")
        self.base_url = f"http://{self.host}:{self.port}"
        self._is_live_server: bool | None = None
        self._mode: str = MODE_UNKNOWN
        self._fallback_db: sqlite3.Connection | None = None

    @property
    def mode(self) -> str:
        """The engine that produced the most recent result (never a guess)."""
        return self._mode

    def _mark_fallback(self, operation: str, detail: str) -> None:
        """Labels this client as running on the fallback and says so, loudly."""
        self._mode = MODE_SQLITE_FALLBACK
        logger.error(
            "mode=sqlite-fallback: %s ran on the EMBEDDED SQLite engine, not ClickHouse "
            "(this result is NOT ClickHouse data): %s",
            operation,
            detail,
        )

    def is_connected(self) -> bool:
        """Checks if the live ClickHouse HTTP server is reachable."""
        try:
            req = urllib.request.Request(f"{self.base_url}/ping")  # noqa: S310 - fixed http:// scheme on config host/port
            with urllib.request.urlopen(req, timeout=1.0) as resp:  # noqa: S310 - fixed http:// scheme on config host/port
                if resp.status == 200:
                    self._is_live_server = True
                    self._mode = MODE_CLICKHOUSE
                    return True
        except Exception as exc:
            logger.debug("ClickHouse ping failed, using embedded mode: %s", exc)
        self._is_live_server = False
        return False

    def _get_fallback_conn(self) -> sqlite3.Connection:
        if self._fallback_db is None:
            import tempfile

            db_path = os.environ.get(
                "CLICKHOUSE_EMBEDDED_PATH",
                os.path.join(tempfile.gettempdir(), "1000fix_analytics_embedded.db"),
            )
            self._fallback_db = sqlite3.connect(db_path, check_same_thread=False)
            self._fallback_db.row_factory = sqlite3.Row
            # Register ClickHouse compatibility functions in SQLite
            self._fallback_db.create_function(
                "toYYYYMM", 1, lambda val: int(str(val)[:7].replace("-", "")) if val else 0
            )
            self._fallback_db.create_function(
                "toDate", 1, lambda val: str(val)[:10] if val else None
            )
            self._fallback_db.create_function(
                "md5",
                1,
                lambda val: __import__("hashlib").md5(str(val).encode()).hexdigest() if val else "",
            )
        return self._fallback_db

    def close(self) -> None:
        """Closes the embedded engine connection (reopened lazily on next use)."""
        if self._fallback_db is not None:
            self._fallback_db.close()
            self._fallback_db = None

    def execute(
        self, query: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]] | int:
        """Executes a DDL, DML, or query statement against ClickHouse or embedded engine.

        The result of a fallback execution is SQLite data: ``self.mode`` reports
        ``sqlite-fallback`` and an ERROR is logged — never silently presented as
        ClickHouse output.
        """
        query_clean = query.strip()
        if self._is_live_server is None:
            self.is_connected()

        if self._is_live_server:
            try:
                result = self._execute_http(query_clean)
                self._mode = MODE_CLICKHOUSE
                return result
            except Exception as e:
                logger.error(
                    "ClickHouse HTTP execute failed: %s.",
                    e,
                )
                if not self.use_fallback_if_unreachable:
                    raise

        self._mark_fallback("execute", query_clean[:120])
        return self._execute_embedded(query_clean, params)

    def _execute_http(self, query: str) -> list[dict[str, Any]] | int:
        """Executes a query via ClickHouse HTTP endpoint."""
        url = f"{self.base_url}/?database={self.database}"
        data = query.encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST")  # noqa: S310 - fixed http:// scheme on config host/port
        if self.user:
            req.add_header("X-ClickHouse-User", self.user)
        if self.password:
            req.add_header("X-ClickHouse-Key", self.password)

        with urllib.request.urlopen(req, timeout=self.timeout) as resp:  # noqa: S310 - fixed http:// scheme on config host/port
            content = resp.read().decode("utf-8").strip()
            if not content:
                return 0
            # Try parsing JSON if requested
            q_upper = query.upper()
            if "FORMAT JSON" in q_upper:
                try:
                    if "FORMAT JSONEACHROW" in q_upper:
                        # JSONEachRow is newline-delimited: one JSON object per row
                        return [json.loads(line) for line in content.splitlines()]
                    parsed = json.loads(content)
                    return parsed.get("data", [])
                except Exception as exc:
                    logger.debug("ClickHouse response is not JSON: %s", exc)
            return 1

    def insert_rows(self, table: str, rows: list[dict[str, Any]]) -> int:
        """Inserts multiple rows formatted as dictionaries.

        A fallback insert lands in the embedded SQLite file: ``self.mode``
        reports ``sqlite-fallback`` and an ERROR is logged.
        """
        if not rows:
            return 0

        if self._is_live_server is None:
            self.is_connected()

        if self._is_live_server:
            # http.client with the pre-validated host/port (no URL string
            # construction): auth headers were previously missing here, so a
            # password-protected ClickHouse silently fell back to SQLite.
            import http.client

            clean_table = table.split(".")[-1]
            if not re.fullmatch(r"[A-Za-z0-9_]+", clean_table):
                raise ValueError(f"table name not a plain identifier: {table!r}")
            try:
                conn = http.client.HTTPConnection(self.host, self.port, timeout=self.timeout)
                try:
                    headers = {"Content-Type": "text/plain; charset=utf-8"}
                    if self.user:
                        headers["X-ClickHouse-User"] = self.user
                    if self.password:
                        headers["X-ClickHouse-Key"] = self.password
                    path = (
                        f"/?database={self.database}"
                        f"&query=INSERT%20INTO%20{clean_table}%20FORMAT%20JSONEachRow"
                    )
                    body = "\n".join(json.dumps(r, default=str) for r in rows).encode("utf-8")
                    conn.request("POST", path, body=body, headers=headers)
                    resp = conn.getresponse()
                    resp.read()
                    if resp.status == 200:
                        self._mode = MODE_CLICKHOUSE
                        return len(rows)
                    logger.error("HTTP insert into %s returned %d.", clean_table, resp.status)
                finally:
                    conn.close()
            except Exception as e:
                logger.error("HTTP insert into %s failed: %s.", table, e)
                if not self.use_fallback_if_unreachable:
                    raise

        self._mark_fallback("insert_rows", f"{len(rows)} rows into {table}")
        # Embedded insert
        clean_table = table.split(".")[-1]
        conn = self._get_fallback_conn()
        cols = list(rows[0].keys())
        placeholders = ", ".join(["?"] * len(cols))
        col_names = ", ".join([f'"{c}"' for c in cols])
        insert_sql = f'INSERT OR REPLACE INTO "{clean_table}" ({col_names}) VALUES ({placeholders})'  # noqa: S608 - quoted identifiers from warehouse rows; values bound via ? params

        # Ensure table columns exist
        self._ensure_embedded_table(clean_table, rows[0])

        val_rows = [[r.get(c) for c in cols] for r in rows]
        with conn:
            conn.executemany(insert_sql, val_rows)
        return len(rows)

    def _ensure_embedded_table(self, table: str, sample_row: dict[str, Any]):
        """Creates table in SQLite with types deduced from sample row if not existing."""
        conn = self._get_fallback_conn()
        col_defs = []
        for k, v in sample_row.items():
            if isinstance(v, int):
                col_defs.append(f'"{k}" INTEGER')
            elif isinstance(v, float):
                col_defs.append(f'"{k}" REAL')
            else:
                col_defs.append(f'"{k}" TEXT')
        ddl = f'CREATE TABLE IF NOT EXISTS "{table}" ({", ".join(col_defs)})'
        with conn:
            conn.execute(ddl)

    def _execute_embedded(
        self, query: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]] | int:
        """Translates ClickHouse DDL/DML into SQLite compatible operations."""
        conn = self._get_fallback_conn()
        # Strip database qualifier e.g. fix_analytics. or default.
        query = re.sub(rf"\b{self.database}\.", "", query, flags=re.IGNORECASE)
        query = re.sub(r"\bdefault\.", "", query, flags=re.IGNORECASE)
        q_upper = query.upper()

        # Database creation no-op
        if q_upper.startswith("CREATE DATABASE"):
            return 1

        # Handle ClickHouse DDL translation: strip ENGINE, ORDER BY, PARTITION BY, TTL
        if q_upper.startswith("CREATE TABLE"):
            # Clean ClickHouse engine and partition clauses after the closing parenthesis
            ch_ddl = re.sub(r"\)\s*ENGINE\s*=.*", ")", query, flags=re.DOTALL | re.IGNORECASE)
            # Map ClickHouse data types to SQLite
            type_mappings = [
                (r"\bUInt64\b", "INTEGER"),
                (r"\bUInt32\b", "INTEGER"),
                (r"\bInt32\b", "INTEGER"),
                (r"\bInt64\b", "INTEGER"),
                (r"\bUInt8\b", "INTEGER"),
                (r"\bFloat64\b", "REAL"),
                (r"\bFloat32\b", "REAL"),
                (r"\bDecimal\(.*?\)", "REAL"),
                (r"\bString\b", "TEXT"),
                (r"\bFixedString\(.*?\)", "TEXT"),
                (r"\bDate\b", "TEXT"),
                (r"\bDateTime\b", "TEXT"),
                (r"\bNullable\((.*?)\)", r"\1"),
                (r"\bLowCardinality\((.*?)\)", r"\1"),
            ]
            for pat, repl in type_mappings:
                ch_ddl = re.sub(pat, repl, ch_ddl, flags=re.IGNORECASE)
            ch_ddl = ch_ddl.strip().rstrip(";")
            with conn:
                conn.execute(ch_ddl)
            return 1

        # ClickHouse TRUNCATE has no SQLite equivalent: emulate it with DELETE
        truncate = re.match(
            r"TRUNCATE\s+TABLE\s+(IF\s+EXISTS\s+)?\"?(\w+)\"?\s*;?$", query, flags=re.IGNORECASE
        )
        if truncate:
            if_exists, table = truncate.groups()
            exists = conn.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?", (table,)
            ).fetchone()
            if if_exists and not exists:
                return 0
            with conn:
                return conn.execute(f'DELETE FROM "{table}"').rowcount  # noqa: S608 - \w+ identifier, quoted

        # Query execution
        # Strip ClickHouse specific FORMAT JSON / FORMAT JSONEachRow
        clean_select = re.sub(
            r"FORMAT\s+JSON(EachRow)?\s*;?$", "", query, flags=re.IGNORECASE
        ).strip()
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(clean_select, params)
            else:
                cursor.execute(clean_select)
            result: list[dict[str, Any]] | int = cursor.rowcount
            if cursor.description:
                cols = [d[0] for d in cursor.description]
                result = [dict(zip(cols, row, strict=False)) for row in cursor.fetchall()]
            # sqlite3 (legacy transaction mode) opens an implicit transaction for
            # INSERT/UPDATE/DELETE. Commit it: left open, the write is lost when the
            # connection closes and its RESERVED lock makes every other client of the
            # same file fail with "database is locked".
            if conn.in_transaction:
                conn.commit()
        except Exception as e:
            logger.debug(f"Embedded query error on: {clean_select} -> {e}")
            if conn.in_transaction:
                conn.rollback()
            raise
        return result
