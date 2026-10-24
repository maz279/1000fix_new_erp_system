"""migrations/target_db.py — the ONE place the rehearsal resolves its target database.

The Wave-1 rehearsal loads a dedicated, clean database (`fix_migration`) and
never the shared dev database (DE-12; mig-totals refuses loopback DSNs that
are not `fix_migration`). Build it with
`python tooling/scripts/build-test-db.py --db fix_migration` (migrations/REHEARSAL.md).

Resolution order (first hit wins):
  1. an explicit DSN argument (`--dsn` on the CLIs)
  2. DATABASE_URL
  3. PGHOST / PGPORT / PGUSER / PGPASSWORD / PGDATABASE, falling back to
     infra/odoo-conf/local.resolved.conf (generated, REPO-15: db_host/db_port/
     db_user/db_password)
     and to the database `fix_migration`.
"""

from __future__ import annotations

import configparser
import os
from pathlib import Path

import psycopg2
from psycopg2.extensions import make_dsn, parse_dsn

REPO_ROOT = Path(__file__).resolve().parent.parent
RUNTIME_CONF = REPO_ROOT / "infra" / "odoo-conf" / "local.resolved.conf"

DEFAULT_DB = "fix_migration"
# The rehearsal never writes these, whatever the environment says (DE-12).
REFUSED_DBS = frozenset({"fix_dev", "postgres", "template0", "template1"})
BUILD_HINT = "python tooling/scripts/build-test-db.py --db fix_migration"


class RehearsalTargetError(RuntimeError):
    """The resolved target is refused or not reachable/built."""


def _runtime_conf() -> dict[str, str]:
    conf = configparser.ConfigParser(interpolation=None)
    conf.read(RUNTIME_CONF, encoding="utf-8")
    return dict(conf["options"]) if conf.has_section("options") else {}


def resolve_dsn(dsn: str | None = None) -> str:
    """Return the libpq DSN of the rehearsal target (never fix_dev)."""
    if dsn or os.environ.get("DATABASE_URL"):
        resolved = dsn or os.environ["DATABASE_URL"]
    else:
        opts = _runtime_conf()
        params = {
            "host": os.environ.get("PGHOST", opts.get("db_host", "127.0.0.1")),
            "port": os.environ.get("PGPORT", opts.get("db_port", "5433")),
            "user": os.environ.get("PGUSER", opts.get("db_user", "fix")),
            "dbname": os.environ.get("PGDATABASE", DEFAULT_DB),
        }
        password = os.environ.get("PGPASSWORD", opts.get("db_password", ""))
        if password:
            params["password"] = password
        resolved = make_dsn(**params)
    name = database_name(resolved)
    if name in REFUSED_DBS:
        raise RehearsalTargetError(
            f"refusing rehearsal target database {name!r}: the Wave-1 rehearsal loads "
            f"its own clean database ({DEFAULT_DB!r}), never the shared dev database (DE-12)"
        )
    return resolved


def database_name(dsn: str) -> str:
    return parse_dsn(dsn).get("dbname", "")


def describe(dsn: str) -> str:
    """host:port/dbname without credentials (safe to print)."""
    p = parse_dsn(dsn)
    return f"{p.get('host', 'localhost')}:{p.get('port', '5432')}/{p.get('dbname', '')}"


def database_exists(dsn: str) -> bool:
    """True when the target database exists on its server.

    Raises RehearsalTargetError when the server itself is unreachable.
    """
    params = parse_dsn(dsn)
    name = params.pop("dbname", "")
    try:
        conn = psycopg2.connect(dbname="postgres", **params)
    except psycopg2.OperationalError as exc:
        raise RehearsalTargetError(
            f"database server for {describe(dsn)} unreachable: {str(exc).strip()}"
        ) from exc
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (name,))
            return cur.fetchone() is not None
    finally:
        conn.close()


def connect(dsn: str | None = None):
    """Connect to the rehearsal target with a clear error when it is not built."""
    resolved = resolve_dsn(dsn)
    if not database_exists(resolved):
        raise RehearsalTargetError(
            f"rehearsal database {describe(resolved)} does not exist - build it first: "
            f"{BUILD_HINT}"
        )
    return psycopg2.connect(resolved)
