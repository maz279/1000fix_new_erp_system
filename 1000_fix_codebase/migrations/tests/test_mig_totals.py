"""tooling/scripts/mig-totals.py — MIG-02 verifier, file and live (--dsn) modes.

Live mode counts the migrated rows in the target database by the permanent
legacy references the Wave-1 loaders write (LIVE_COUNT_SOURCES). DB-backed cases
run against the rehearsal database after the session's pipeline run and are
skipped (with the build command) when it does not exist.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest
from psycopg2.extensions import parse_dsn

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST = REPO_ROOT / "migrations" / "extracts" / "control-totals.json"


@pytest.fixture(scope="module")
def mig_totals():
    spec = importlib.util.spec_from_file_location(
        "mig_totals", REPO_ROOT / "tooling" / "scripts" / "mig-totals.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_main(mig_totals, monkeypatch, capsys, *args: str) -> tuple[int, str]:
    monkeypatch.setattr(sys, "argv", ["mig-totals.py", *args])
    rc = mig_totals.main()
    return rc, capsys.readouterr().out


@pytest.fixture
def live_url(rehearsal_dsn, pipeline_run, monkeypatch) -> str:
    """URL form of the rehearsal DSN (mig-totals' SSRF guard); password via env."""
    params = parse_dsn(rehearsal_dsn)
    if params.get("dbname") != "fix_migration":
        pytest.skip("mig-totals live mode only accepts the fix_migration database")
    if params.get("password"):
        monkeypatch.setenv("PGPASSWORD", params["password"])
    host = params.get("host", "127.0.0.1")
    return f"postgresql://{params.get('user', 'fix')}@{host}:{params.get('port', '5432')}/fix_migration"


# ---------------------------------------------------------------- no database


def test_every_wave1_entity_has_a_live_count_source(mig_totals):
    control = json.loads(MANIFEST.read_text(encoding="utf-8"))["control_totals"]
    assert set(control) <= set(mig_totals.LIVE_COUNT_SOURCES)
    sql = mig_totals.live_count_sql("devices")
    assert sql == "SELECT count(*) FROM fix_device WHERE legacy_reference LIKE 'DEV:ASSET_SHEET:%'"
    assert "fix_attendance_record WHERE device_ref LIKE 'LEG:SIGNIN_BOOK:%'" in (
        mig_totals.live_count_sql("attendance_opening")
    )


def test_unmapped_entity_fails_closed(mig_totals, monkeypatch, capsys, tmp_path):
    manifest = tmp_path / "control-totals.json"
    manifest.write_text(json.dumps({"run": "T", "control_totals": {"inventory": 1}}), "utf-8")
    rc, out = run_main(
        mig_totals,
        monkeypatch,
        capsys,
        "--manifest",
        str(manifest),
        "--dsn",
        "postgresql://fix@127.0.0.1:5433/fix_migration",
    )
    assert rc == 1
    assert "no live-count source mapped for entity 'inventory'" in out


def test_loopback_dsn_must_be_fix_migration(mig_totals):
    for dsn in (
        "postgresql://fix@127.0.0.1:5433/fix_dev",
        "postgresql://fix@localhost:5433/fix_dev_migration",
    ):
        with pytest.raises(ValueError, match="fix_migration"):
            mig_totals.validate_dsn(dsn)
    mig_totals.validate_dsn("postgresql://fix@127.0.0.1:5433/fix_migration")


# ------------------------------------------------- live mode (rehearsal database)


def test_live_counts_match_the_loaders(mig_totals, live_url, pipeline_run):
    counts = json.loads(pipeline_run[1].read_text(encoding="utf-8"))
    live = mig_totals.query_live_counts(live_url, list(counts["accepted_records"]))
    assert live == counts["accepted_records"]
    assert live["branches"] == 6
    assert live["devices"] == 49


def test_live_with_loaded_counts_reconciles(
    mig_totals, live_url, pipeline_run, monkeypatch, capsys
):
    rc, out = run_main(
        mig_totals,
        monkeypatch,
        capsys,
        "--manifest",
        str(MANIFEST),
        "--loaded",
        str(pipeline_run[1]),
        "--dsn",
        live_url,
    )
    assert rc == 0, out
    assert "live database accepted rows + loaded-counts quarantines" in out
    assert "every control total reconciled" in out


def test_live_alone_surfaces_quarantines_as_variances(mig_totals, live_url, monkeypatch, capsys):
    rc, out = run_main(
        mig_totals, monkeypatch, capsys, "--manifest", str(MANIFEST), "--dsn", live_url
    )
    assert rc == 1
    assert "[MISMATCH] customers: control=50 loaded=49" in out
    assert "[MISMATCH] devices: control=50 loaded=49" in out
    assert "[MISMATCH] attendance_opening: control=20 loaded=0" in out
    assert "[OK] branches: control=6 loaded=6" in out


def test_live_detects_a_load_report_that_disagrees(
    mig_totals, live_url, pipeline_run, monkeypatch, capsys, tmp_path
):
    counts = json.loads(pipeline_run[1].read_text(encoding="utf-8"))
    counts["accepted_records"]["devices"] += 1  # the report claims a row the DB lacks
    tampered = tmp_path / "loaded-counts.json"
    tampered.write_text(json.dumps(counts), encoding="utf-8")
    rc, out = run_main(
        mig_totals,
        monkeypatch,
        capsys,
        "--manifest",
        str(MANIFEST),
        "--loaded",
        str(tampered),
        "--dsn",
        live_url,
    )
    assert rc == 1
    assert "[DRIFT] devices: loaded-counts accepted=50 database=49" in out
