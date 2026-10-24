"""
migrations/tests/test_migration_inventory.py — Wave-2 M15 inventory baseline load (ETL-5).

Verifies, against the rehearsal database `fix_migration` after the session's Wave-1
pipeline run (branches + employees the locations need):
  - the committed synthetic extract loads 150 SKUs, 10 locations and 950 count lines,
    every location with its MIG-03 legacy reference, its branch's company / operating
    unit, the van plate the extract carries (or NULL) and its custodian technician
  - the G2-04 status and every number of the generated record are DB-measured
    (independent read-back here) and the record claims no sign-off
  - a second run is idempotent (same rows, no duplicate suspense entries)
  - variant extracts: an unknown branch / unknown part / bad control total / low
    accuracy is REJECTED or FAILS - never loaded with fallback ids, never PASS

Skipped with the build command when `fix_migration` does not exist. The load writes
its extracts and record into tmp dirs: the tests never mutate the committed
migrations/extracts or docs/traceability artefacts.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import psycopg2
import pytest
from psycopg2.extras import RealDictCursor

from migrations.load_inventory import (
    FAIL,
    INCOMPLETE,
    PASS,
    generate_inventory_extracts,
    load_inventory,
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
COMMITTED_ARTEFACTS = (
    BASE_DIR / "migrations" / "extracts" / "inventory_parts_extract.json",
    BASE_DIR / "migrations" / "extracts" / "inventory_physical_count_extract.json",
    BASE_DIR / "docs" / "traceability" / "inventory-reconciliation-signoff.md",
)
FORBIDDEN_CLAIMS = re.compile(r"signed|approved|discharged|verified", re.IGNORECASE)
# variant fixtures use their own codes so they never touch the committed run's rows
TEST_PREFIX = "TST-"


def _digests() -> dict[Path, str | None]:
    return {
        p: hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
        for p in COMMITTED_ARTEFACTS
    }


def _snapshot(cur, line_refs: list[str]) -> dict[str, int]:
    cur.execute(
        "SELECT count(*), count(DISTINCT legacy_reference) FROM fix_inventory_valuation_suspense "
        "WHERE legacy_reference = ANY(%s);",
        (line_refs,),
    )
    rows, distinct = cur.fetchone()
    cur.execute(
        "SELECT count(*) FROM fix_stock_location WHERE legacy_reference LIKE 'LEG:SRC38:%';"
    )
    locations = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM fix_spare_part WHERE legacy_reference LIKE 'LEG:SRC37:%';")
    parts = cur.fetchone()[0]
    return {
        "suspense_rows": rows,
        "distinct_refs": distinct,
        "locations": locations,
        "parts": parts,
    }


@pytest.fixture(scope="module")
def inventory_run(rehearsal_dsn, pipeline_run, tmp_path_factory):
    """Run load_inventory.py once against fix_migration, outputs under a tmp dir."""
    out = tmp_path_factory.mktemp("inventory")
    before = _digests()
    cmd = [
        sys.executable,
        "migrations/load_inventory.py",
        "--extracts-dir",
        str(out / "extracts"),
        "--signoff",
        str(out / "inventory-reconciliation-signoff.md"),
    ]
    res = subprocess.run(  # noqa: S603 - fixed argv list built in-process, no shell
        cmd,
        cwd=str(BASE_DIR),
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "DATABASE_URL": rehearsal_dsn, "PYTHONIOENCODING": "utf-8"},
    )
    return res, out, before


@pytest.fixture
def load_conn(rehearsal_dsn):
    """A transactional connection (the loader uses savepoints) - closed after the test."""
    conn = psycopg2.connect(rehearsal_dsn)
    yield conn
    conn.rollback()
    conn.close()


def _cleanup_variants(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM fix_inventory_valuation_suspense WHERE legacy_reference LIKE %s;",
            (f"LEG:SRC38:{TEST_PREFIX}%",),
        )
        cur.execute(
            "DELETE FROM fix_stock_location WHERE legacy_reference LIKE %s;",
            (f"LEG:SRC38:{TEST_PREFIX}%",),
        )
        cur.execute(
            "DELETE FROM fix_spare_part WHERE legacy_reference LIKE %s;",
            (f"LEG:SRC37:{TEST_PREFIX}%",),
        )
    conn.commit()


@pytest.fixture
def variant_conn(load_conn, pipeline_run):
    _cleanup_variants(load_conn)
    yield load_conn
    load_conn.rollback()
    _cleanup_variants(load_conn)


def _variant_extracts(tmp_path: Path, *, locations, lines, control=None) -> tuple[Path, Path]:
    skus = sorted({ln["part_number"] for ln in lines if not ln["part_number"].endswith("NOPE")})
    parts = [
        {
            "part_number": sku,
            "name": f"Test part {sku}",
            "category": "sensor",
            "brand": "Walton",
            "is_serialized": False,
            "warranty_months": 6,
            "unit_cost": 100.0,
            "sales_price": 150.0,
            "min_qty": 1.0,
            "max_qty": 10.0,
            "safety_stock": 1.0,
            "legacy_reference": f"LEG:SRC37:{sku}",
        }
        for sku in skus
    ]
    for loc in locations:
        loc.setdefault("legacy_reference", f"LEG:SRC38:{loc['code']}")
    for ln in lines:
        ln.setdefault("unit_cost", 100.0)
        ln.setdefault("legacy_reference", f"LEG:SRC38:{ln['location_code']}:{ln['part_number']}")
    totals = control or {
        "locations": len(locations),
        "count_lines": len(lines),
        "physical_units": sum(ln["physical_count"] for ln in lines),
    }
    payload = {
        "metadata": {
            "data_classification": "SYNTHETIC",
            "audited_at": "2026-10-16T18:00:00Z",
            "sign_off_roles": ["Stock Controller"],
            "control_totals": totals,
        },
        "locations": locations,
        "lines": lines,
    }
    parts_path = tmp_path / "parts.json"
    counts_path = tmp_path / "counts.json"
    parts_path.write_text(json.dumps(parts), encoding="utf-8")
    counts_path.write_text(json.dumps(payload), encoding="utf-8")
    return parts_path, counts_path


def _hub(code: str, branch: str = "HQ") -> dict:
    return {"code": code, "name": f"Test {code}", "location_type": "branch", "branch_code": branch}


def _line(loc: str, sku: str, physical: int, system: int | None = None) -> dict:
    return {
        "location_code": loc,
        "part_number": sku,
        "physical_count": physical,
        "system_count": physical if system is None else system,
    }


# --------------------------------------------------------------- committed extract


def test_inventory_migration_execution(inventory_run):
    """load_inventory.py succeeds on the committed extract and writes only to its tmp dir."""
    res, out, before = inventory_run
    assert res.returncode == 0, f"Migration failed: {res.stderr}\n{res.stdout}"
    assert "Gate Criterion G2-04 Status: PASS" in res.stdout
    assert "Inventory Accuracy: 99.51%" in res.stdout
    assert (out / "extracts" / "inventory_parts_extract.json").is_file()
    assert (out / "extracts" / "inventory_physical_count_extract.json").is_file()
    assert _digests() == before, "the test run mutated committed inventory artefacts"


def test_generated_extract_matches_committed(tmp_path):
    """The committed synthetic extracts are exactly what the generator produces."""
    parts, counts = generate_inventory_extracts(tmp_path)
    for generated, committed in zip((parts, counts), COMMITTED_ARTEFACTS[:2], strict=True):
        assert json.loads(generated.read_text("utf-8")) == json.loads(committed.read_text("utf-8"))


def test_spare_parts_catalog_loaded(inventory_run, db_conn):
    with db_conn.cursor() as cur:
        cur.execute(
            "SELECT count(*), count(DISTINCT company_id) FROM fix_spare_part "
            "WHERE legacy_reference LIKE 'LEG:SRC37:FX-%';"
        )
        count, companies = cur.fetchone()
        assert (count, companies) == (150, 1)


def test_locations_carry_legacy_reference_branch_company_and_source_plate(inventory_run, db_conn):
    """MIG-03 + no fallback ids: company/OU are the branch's; plates come from the extract."""
    _, out, _ = inventory_run
    payload = json.loads(
        (out / "extracts" / "inventory_physical_count_extract.json").read_text("utf-8")
    )
    with db_conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT l.code, l.legacy_reference, l.van_plate, l.technician_id, l.location_type,
                   l.company_id, l.operating_unit_id, b.code AS branch_code,
                   b.company_id AS b_company, b.operating_unit_id AS b_ou
            FROM fix_stock_location l JOIN fix_branch b ON b.id = l.branch_id
            WHERE l.legacy_reference LIKE 'LEG:SRC38:%' AND l.code NOT LIKE 'TST-%'
        """)
        rows = {r["code"]: r for r in cur.fetchall()}
    assert len(rows) == len(payload["locations"]) == 10
    for loc in payload["locations"]:
        row = rows[loc["code"]]
        assert row["legacy_reference"] == f"LEG:SRC38:{loc['code']}"
        assert row["branch_code"] == loc["branch_code"]
        assert (row["company_id"], row["operating_unit_id"]) == (row["b_company"], row["b_ou"])
        assert row["van_plate"] == loc["van_plate"]  # None stays NULL - never invented
        if loc["location_type"] == "van":
            assert row["technician_id"], f"van {loc['code']} has no custodian"
    assert rows["VAN-HQ-01"]["van_plate"] is None
    assert not any((r["van_plate"] or "").startswith("DHK-METRO-V-") for r in rows.values())


def test_valuation_suspense_entries(inventory_run, db_conn):
    """One suspense row per count line, account 110999 / STUB-M15-M19-001, branch company."""
    with db_conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT count(*) AS cnt, count(DISTINCT s.legacy_reference) AS refs,
                   sum(s.total_valuation) AS val,
                   bool_and(s.company_id = b.company_id
                            AND s.operating_unit_id IS NOT DISTINCT FROM b.operating_unit_id)
                       AS branch_company
            FROM fix_inventory_valuation_suspense s
            JOIN fix_stock_location l
              ON s.legacy_reference LIKE l.legacy_reference || ':%'
            JOIN fix_branch b ON b.id = l.branch_id
            WHERE s.legacy_reference LIKE 'LEG:SRC38:%' AND l.code NOT LIKE 'TST-%'
              AND s.stub_reference = 'STUB-M15-M19-001' AND s.suspense_account_code = '110999'
        """)
        row = cur.fetchone()
    assert row["cnt"] == row["refs"] == 950
    assert row["val"] > 0
    assert row["branch_company"] is True


def test_reconciliation_record_is_measured_and_claims_no_signoff(inventory_run, db_conn):
    """Every location row of the record equals an independent DB read-back; no sign-off."""
    _, out, _ = inventory_run
    content = (out / "inventory-reconciliation-signoff.md").read_text(encoding="utf-8")
    assert not FORBIDDEN_CLAIMS.search(content), FORBIDDEN_CLAIMS.findall(content)
    assert "Sign-off: PENDING - Stock Controller (Head of Supply Chain)" in content
    assert "**Measured G2-04 status: PASS**" in content
    assert "buffer" not in content and "70 units" not in content

    payload = json.loads(
        (out / "extracts" / "inventory_physical_count_extract.json").read_text("utf-8")
    )
    counted: dict[str, int] = {}
    for line in payload["lines"]:
        counted[line["location_code"]] = (
            counted.get(line["location_code"], 0) + line["physical_count"]
        )
    with db_conn.cursor() as cur:
        cur.execute("""
            SELECT split_part(legacy_reference, ':', 3) AS code, sum(quantity)
            FROM fix_inventory_valuation_suspense
            WHERE legacy_reference LIKE 'LEG:SRC38:%' AND entry_type = 'initial_count'
            GROUP BY 1
        """)
        loaded = {code: int(qty) for code, qty in cur.fetchall()}

    table = {}
    for match in re.finditer(
        r"^\| [^|]+ \| `([A-Z0-9-]+)` \| \w+ \| ([\d,]+) \| ([\d,]+) \| (-?[\d,]+) \| ([\d.]+)% \|$",
        content,
        re.MULTILINE,
    ):
        code, c, ld, var, acc = match.groups()
        table[code] = (*(int(x.replace(",", "")) for x in (c, ld, var)), float(acc))
    assert set(table) == set(counted)
    for code, (c, ld, var, _) in table.items():
        assert c == counted[code]
        assert ld == loaded[code], f"{code}: record says {ld}, database holds {loaded[code]}"
        assert var == c - ld
    total_c, total_l = sum(counted.values()), sum(loaded[c] for c in counted)
    assert f"**{total_c:,}** | **{total_l:,}** | **{total_c - total_l:,}**" in content
    assert round((1 - (total_c - total_l) / total_c) * 100, 2) == 99.51


def test_second_run_is_idempotent(inventory_run, load_conn):
    """Re-loading the same extract changes nothing: same rows, no duplicate suspense entries."""
    _, out, _ = inventory_run
    parts = out / "extracts" / "inventory_parts_extract.json"
    counts = out / "extracts" / "inventory_physical_count_extract.json"
    refs = [ln["legacy_reference"] for ln in json.loads(counts.read_text("utf-8"))["lines"]]
    with load_conn.cursor() as cur:
        first = _snapshot(cur, refs)
    load_conn.rollback()
    result = load_inventory(parts, counts, load_conn, signoff_path=None)
    with load_conn.cursor() as cur:
        second = _snapshot(cur, refs)
    assert first == second
    assert second["suspense_rows"] == second["distinct_refs"] == 950
    assert result["gate_status"] == PASS
    assert result["measured"]["duplicate_line_rows"] == []
    assert result["count_lines"] == {"extracted": 950, "loaded": 950, "rejected": 0}


# --------------------------------------------------------------- variant extracts


def test_unknown_branch_and_unknown_part_are_rejected_and_fail(variant_conn, tmp_path):
    """A location whose branch is missing and a line with an unknown part are rejected,
    counted and listed; the large book/count gap makes the measured status FAIL."""
    locations = [_hub("TST-HUB-01"), _hub("TST-HUB-99", branch="NO-SUCH-BRANCH")]
    lines = [
        _line("TST-HUB-01", "TST-P-0001", 10, 4),
        _line("TST-HUB-01", "TST-P-0002", 10),
        _line("TST-HUB-01", "TST-P-NOPE", 5),  # not in the catalog
        _line("TST-HUB-99", "TST-P-0001", 7),  # branch not on target
    ]
    parts, counts = _variant_extracts(tmp_path, locations=locations, lines=lines)
    record = tmp_path / "record.md"
    result = load_inventory(parts, counts, variant_conn, signoff_path=record)

    assert result["gate_status"] == FAIL
    assert result["locations"] == {"extracted": 2, "loaded": 1, "rejected": 1}
    assert result["count_lines"] == {"extracted": 4, "loaded": 2, "rejected": 2}
    reasons = {r["legacy_reference"]: r["reason"] for r in result["rejections"]}
    assert "branch 'NO-SUCH-BRANCH' not found" in reasons["LEG:SRC38:TST-HUB-99"]
    assert "not in the loaded SRC-37 catalog" in reasons["LEG:SRC38:TST-HUB-01:TST-P-NOPE"]
    assert "location 'TST-HUB-99' rejected" in reasons["LEG:SRC38:TST-HUB-99:TST-P-0001"]
    # counted 32, loaded 4 + 10 = 14 -> accuracy 1 - 18/32
    assert result["measured"]["counted_units"] == 32
    assert result["measured"]["loaded_units"] == 14
    assert result["accuracy_percentage"] == 43.75

    with variant_conn.cursor() as cur:
        cur.execute("SELECT count(*) FROM fix_stock_location WHERE code = 'TST-HUB-99';")
        assert cur.fetchone()[0] == 0, "a location with an unknown branch must not be loaded"
        cur.execute(
            "SELECT count(*) FROM fix_inventory_valuation_suspense WHERE legacy_reference = ANY(%s);",
            (["LEG:SRC38:TST-HUB-99:TST-P-0001", "LEG:SRC38:TST-HUB-01:TST-P-NOPE"],),
        )
        assert cur.fetchone()[0] == 0
    content = record.read_text(encoding="utf-8")
    assert "**Measured G2-04 status: FAIL**" in content
    assert "43.75%" in content and "NOT MET" in content
    assert "branch 'NO-SUCH-BRANCH' not found" in content
    assert not FORBIDDEN_CLAIMS.search(content)


def test_a_rejected_line_keeps_an_accurate_load_off_pass(variant_conn, tmp_path):
    """Accuracy above target but one rejected line -> INCOMPLETE (pending disposition)."""
    locations = [_hub("TST-HUB-02")]
    lines = [_line("TST-HUB-02", f"TST-P-{i:04d}", 10) for i in range(1, 21)]
    lines.append(_line("TST-HUB-02", "TST-P-NOPE", 1))
    parts, counts = _variant_extracts(tmp_path, locations=locations, lines=lines)
    result = load_inventory(parts, counts, variant_conn, signoff_path=None)
    assert result["accuracy_percentage"] == round((1 - 1 / 201) * 100, 2)
    assert result["gate_status"] == INCOMPLETE
    assert result["rejected_count"] == 1


def test_van_without_resolvable_custodian_is_rejected(variant_conn, tmp_path):
    van = {
        "code": "TST-VAN-01",
        "name": "Test van",
        "location_type": "van",
        "branch_code": "HQ",
        "van_plate": "TEST PLATE 1",
        "custodian_employee_code": "NO-SUCH-EMP",
    }
    lines = [_line("TST-VAN-01", "TST-P-0001", 3)]
    parts, counts = _variant_extracts(tmp_path, locations=[van], lines=lines)
    result = load_inventory(parts, counts, variant_conn, signoff_path=None)
    assert result["gate_status"] == FAIL  # its only line is rejected -> 0% accuracy
    assert result["locations"]["rejected"] == 1
    assert "custodian 'NO-SUCH-EMP' not found" in result["rejections"][0]["reason"]


def test_control_total_mismatch_fails(variant_conn, tmp_path):
    locations = [_hub("TST-HUB-03")]
    lines = [_line("TST-HUB-03", "TST-P-0001", 5)]
    control = {"locations": 1, "count_lines": 2, "physical_units": 5}
    parts, counts = _variant_extracts(tmp_path, locations=locations, lines=lines, control=control)
    result = load_inventory(parts, counts, variant_conn, signoff_path=None)
    assert result["gate_status"] == FAIL
    assert any("control total count_lines" in r for r in result["gate_status_reasons"])


def test_variant_rerun_is_idempotent(variant_conn, tmp_path):
    locations = [_hub("TST-HUB-04")]
    lines = [_line("TST-HUB-04", f"TST-P-{i:04d}", 2 + i) for i in range(1, 6)]
    parts, counts = _variant_extracts(tmp_path, locations=locations, lines=lines)
    refs = [ln["legacy_reference"] for ln in lines]
    first = load_inventory(parts, counts, variant_conn, signoff_path=None)
    with variant_conn.cursor() as cur:
        snap1 = _snapshot(cur, refs)
    second = load_inventory(parts, counts, variant_conn, signoff_path=None)
    with variant_conn.cursor() as cur:
        snap2 = _snapshot(cur, refs)
    assert snap1 == snap2 and snap2["suspense_rows"] == 5
    assert first["gate_status"] == second["gate_status"] == PASS
    assert first["measured"]["loaded_units"] == second["measured"]["loaded_units"] == 25
