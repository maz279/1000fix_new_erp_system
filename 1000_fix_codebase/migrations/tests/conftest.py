"""Shared fixtures for the Wave-1 migration rehearsal tests.

Every DB-backed test runs against the dedicated rehearsal database
(`fix_migration`, migrations/target_db.py; DATABASE_URL / PG* override) and is
SKIPPED - not failed - with the build command when that database does not exist
or its server is unreachable. Procedure: migrations/REHEARSAL.md.
"""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from pathlib import Path

import psycopg2
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
EXTRACTS_DIR = REPO_ROOT / "migrations" / "extracts"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# after the sys.path bootstrap above (E402 is waived for tests/ in pyproject.toml)
from migrations.target_db import (
    BUILD_HINT,
    RehearsalTargetError,
    database_exists,
    describe,
    resolve_dsn,
)


@pytest.fixture(scope="session")
def rehearsal_dsn() -> str:
    """DSN of the rehearsal database; skips the test when it is not available."""
    try:
        dsn = resolve_dsn()
        exists = database_exists(dsn)
    except RehearsalTargetError as exc:
        pytest.skip(f"migration rehearsal target not available: {exc}")
    if not exists:
        pytest.skip(
            f"migration rehearsal database {describe(dsn)} does not exist - build it with "
            f"`{BUILD_HINT}` and run `python migrations/pipeline.py` (migrations/REHEARSAL.md)"
        )
    return dsn


@pytest.fixture(scope="module")
def db_conn(rehearsal_dsn):
    conn = psycopg2.connect(rehearsal_dsn)
    conn.autocommit = True
    yield conn
    conn.close()


def extracts_digests() -> dict[str, str]:
    """sha256 of every committed artefact under migrations/extracts."""
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in EXTRACTS_DIR.glob("*.json")}


@pytest.fixture(scope="session")
def pipeline_run(rehearsal_dsn, tmp_path_factory):
    """Run the Wave-1 pipeline once against the rehearsal DB.

    loaded-counts.json goes to a tmp dir - the test run never rewrites the
    committed migrations/extracts artefacts. Returns (process, loaded-counts path,
    extracts digests before the run, extracts digests after it).
    """
    loaded_counts = tmp_path_factory.mktemp("pipeline") / "loaded-counts.json"
    before = extracts_digests()
    res = subprocess.run(  # noqa: S603 - fixed argv list built in-process, no shell
        [sys.executable, "migrations/pipeline.py", "--loaded-counts", str(loaded_counts)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        env={**os.environ, "DATABASE_URL": rehearsal_dsn},  # DSN via env, not argv
    )
    return res, loaded_counts, before, extracts_digests()
