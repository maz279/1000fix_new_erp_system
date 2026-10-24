#!/usr/bin/env python3
"""migrations/load_inventory.py — Wave-2 M15 Inventory & Physical Count Baseline Loader (ETL-5).

Specifications:
  - Roadmap: Milestone R03-M01-T06 (R03_Field_Operations_Inventory_Offline_Engine.md)
  - Data sources:
      SRC-37: Central Warehouse SKU Catalog (Excel / CSV)
      SRC-38: Branch Spare Parts Stock Count (physical count baseline: a location
              header - branch, type, van plate, van custodian, legacy reference -
              and one count line per location x part)
  - Standards:
      MIG-02: control totals of the count sheet are checked against its lines, and the
              physical count is reconciled against what is IN THE DATABASE after the load
      MIG-03: permanent legacy_reference on every loaded row
              ('LEG:SRC37:<part_number>', 'LEG:SRC38:<location_code>',
               'LEG:SRC38:<location_code>:<part_number>')
      GV-005: STUB-M15-M19-001 suspense valuation postings (account 110999)
      GV-009: every number and status in the G2-04 reconciliation record is measured
              from the target database after the load; nothing is copied from the
              extract's own claims, and no sign-off is ever recorded by this loader
      G2-04:  inventory accuracy >= 95% at migrated locations (measured here; the gate
              stays open until the named roles sign the record)

Company / operating unit of every location and suspense row come from the location's
branch (fix_branch.company_id / operating_unit_id); the catalog's company is the legal
entity named in migrations/fixtures/wave1_reference_data.json. Nothing falls back to
"the first company" or to id 1: a location whose branch is not on the target is
REJECTED with its count lines (counted and listed), never loaded with NULL.

Re-runs are idempotent: every row is matched on its legacy reference and updated.

Target: the dedicated rehearsal database `fix_migration` (never fix_dev, DE-12);
DATABASE_URL / PG* override (migrations/target_db.py).
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from psycopg2.extensions import parse_dsn

logger = logging.getLogger(__name__)

MIGRATIONS_DIR = Path(__file__).resolve().parent
EXTRACTS_DIR = MIGRATIONS_DIR / "extracts"
FIXTURE_FILE = MIGRATIONS_DIR / "fixtures" / "wave1_reference_data.json"
SIGNOFF_DOC = (
    MIGRATIONS_DIR.parent / "docs" / "traceability" / "inventory-reconciliation-signoff.md"
)

ACCURACY_TARGET = 95.0
SUSPENSE_ACCOUNT = "110999"
STUB_REFERENCE = "STUB-M15-M19-001"
STUB_EXPIRY = "2026-11-30"
ENTRY_TYPE = "initial_count"

PASS = "PASS"  # noqa: S105 - a verdict label, not a credential
FAIL = "FAIL"
INCOMPLETE = "INCOMPLETE"

# Tables the load writes (cd_inventory ORM models); the loader never creates them.
REQUIRED_TABLES = ("fix_stock_location", "fix_spare_part", "fix_inventory_valuation_suspense")

# Synthetic SRC-38 location header (DE-12: synthetic source data, no real data on a
# workstation). (branch_code, code, name, type, van_plate, custodian_employee_code)
# VAN-HQ-01's plate was not recorded on the count sheet: it loads as NULL.
SYNTHETIC_LOCATIONS = (
    ("HQ", "CENTRAL-WH", "Central Warehouse Mirpur", "central", None, None),
    ("PC-01", "DHAN-HUB", "Dhanmondi Service Hub", "branch", None, None),
    ("PC-02", "UTT-HUB", "Uttara Service Hub", "branch", None, None),
    ("PC-03", "MIR-HUB", "Mirpur Service Hub", "branch", None, None),
    ("PC-04", "CTG-HUB", "Chattogram Agrabad Hub", "branch", None, None),
    ("PC-01", "VAN-DHAN-01", "Dhanmondi Mobile Van 1", "van", "DHAKA METRO-GA-11-2041", "E-0002"),
    ("PC-02", "VAN-UTT-01", "Uttara Mobile Van 1", "van", "DHAKA METRO-GA-11-2042", "E-0003"),
    ("PC-03", "VAN-MIR-01", "Mirpur Mobile Van 1", "van", "DHAKA METRO-GA-11-2043", "E-0004"),
    ("PC-04", "VAN-CTG-01", "Chattogram Mobile Van 1", "van", "CHATTO METRO-NA-11-0457", "E-0005"),
    ("HQ", "VAN-HQ-01", "Dhaka Rapid Van 1", "van", None, "E-0001"),
)

SIGN_OFF_ROLES = (
    "Stock Controller (Head of Supply Chain)",
    "Lead Inventory Auditor (physical blind count)",
    "System Architect (G2-04 gate owner)",
)


def _write_json(path: Path, data: Any) -> None:
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n"
    )


def generate_inventory_extracts(out_dir: Path = EXTRACTS_DIR) -> tuple[Path, Path]:
    """Generate the synthetic SRC-37 (catalog) and SRC-38 (physical count) extracts.

    Deterministic synthetic SOURCE data. `out_dir` defaults to the committed
    migrations/extracts; tests pass a tmp dir. The count sheet carries its own
    control totals (MIG-02) - never an accuracy or a reconciliation claim.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    parts_path = out_dir / "inventory_parts_extract.json"
    counts_path = out_dir / "inventory_physical_count_extract.json"

    categories = [
        ("display", "Display & Touch Screen Assembly", 3500.0, 5200.0),
        ("battery", "Lithium Battery Pack", 1200.0, 1900.0),
        ("motherboard", "Motherboard / Main PCB", 6500.0, 9800.0),
        ("camera", "Front / Rear Camera Module", 850.0, 1400.0),
        ("charging_port", "Charging Port & Sub-PCB", 450.0, 850.0),
        ("compressor", "Inverter / Rotary Compressor", 11000.0, 16500.0),
        ("motor", "Drive Motor & Pump", 2800.0, 4200.0),
        ("sensor", "Thermal / Pressure Sensor", 350.0, 650.0),
        ("fastener", "Housing, Screws & Thermal Pads", 150.0, 300.0),
    ]
    brands = ["Samsung", "Apple", "Dell", "HP", "Lenovo", "Walton", "Gree", "LG"]

    parts = []
    for i in range(1, 151):
        cat_key, cat_name, cost, price = categories[(i - 1) % len(categories)]
        brand = brands[(i - 1) % len(brands)]
        sku = f"FX-{brand[:3].upper()}-{cat_key[:3].upper()}-{1000 + i}"
        is_serialized = cat_key in ["display", "battery", "motherboard", "compressor"]
        parts.append(
            {
                "part_number": sku,
                "name": f"{brand} {cat_name} Rev-{i % 5 + 1}",
                "name_bn": f"{brand} {cat_name} (যন্ত্রাংশ {i})",
                "category": cat_key,
                "brand": brand,
                "barcode": f"880{i:010d}",
                "qr_code": f"QR-FX-{sku}",
                "is_serialized": is_serialized,
                "warranty_months": 12 if is_serialized else 6,
                "unit_cost": cost,
                "sales_price": price,
                "min_qty": 5.0,
                "max_qty": 30.0,
                "safety_stock": 3.0,
                "legacy_reference": f"LEG:SRC37:{sku}",
            }
        )
    _write_json(parts_path, parts)

    locations = [
        {
            "code": code,
            "name": name,
            "location_type": loc_type,
            "branch_code": branch_code,
            "van_plate": plate,
            "custodian_employee_code": custodian,
            "legacy_reference": f"LEG:SRC38:{code}",
        }
        for branch_code, code, name, loc_type, plate, custodian in SYNTHETIC_LOCATIONS
    ]

    lines = []
    for loc in locations:
        for idx, part in enumerate(parts):
            # hubs carry every part; vans carry the 40 fast movers
            if loc["location_type"] == "van" and idx >= 40:
                continue
            counted = (idx % 7 + 2) if loc["location_type"] != "van" else (idx % 3 + 1)
            # five lines per branch hub where the legacy book is one unit short of the count
            book_short = (
                1 if idx in (12, 34, 56, 78, 90) and loc["location_type"] == "branch" else 0
            )
            system = counted - book_short
            lines.append(
                {
                    "location_code": loc["code"],
                    "part_number": part["part_number"],
                    "physical_count": counted,
                    "system_count": system,
                    "unit_cost": part["unit_cost"],
                    "legacy_reference": f"LEG:SRC38:{loc['code']}:{part['part_number']}",
                }
            )

    payload = {
        "metadata": {
            "source_doc": "SRC-38 Physical Count Audit 2026",
            "data_classification": "SYNTHETIC",
            "audited_at": "2026-10-16T18:00:00Z",
            "sign_off_roles": list(SIGN_OFF_ROLES),
            "control_totals": {
                "locations": len(locations),
                "count_lines": len(lines),
                "physical_units": sum(line["physical_count"] for line in lines),
            },
        },
        "locations": locations,
        "lines": lines,
    }
    _write_json(counts_path, payload)
    return parts_path, counts_path


# --------------------------------------------------------------------------- load


def require_inventory_schema(cur) -> None:
    """The cd_inventory ORM tables (with legacy_reference) must exist - fail closed.

    The loader never creates shadow tables: a target without cd_inventory is not a
    rehearsal target (build it with tooling/scripts/build-test-db.py --db fix_migration).
    """
    cur.execute(
        "SELECT table_name FROM information_schema.columns "
        "WHERE table_schema = 'public' AND table_name = ANY(%s) "
        "AND column_name = 'legacy_reference';",
        (list(REQUIRED_TABLES),),
    )
    present = {row[0] for row in cur.fetchall()}
    missing = [t for t in REQUIRED_TABLES if t not in present]
    if missing:
        raise RuntimeError(
            f"target lacks {missing} (with legacy_reference) - install/upgrade cd_inventory "
            "on the rehearsal database before ETL-5"
        )


def resolve_catalog_company(cur, fixture_path: Path | None = None) -> int:
    """Company of the legal entity named in the reference fixture (no LIMIT 1 guess)."""
    fixture = json.loads((fixture_path or FIXTURE_FILE).read_text(encoding="utf-8"))
    entity_code = fixture["entity"]["code"]
    cur.execute("SELECT company_id FROM fix_entity WHERE code = %s;", (entity_code,))
    rows = cur.fetchall()
    if len(rows) != 1 or rows[0][0] is None:
        raise RuntimeError(
            f"legal entity {entity_code!r} not found exactly once on the target - "
            "run ETL-0 (migrations/pipeline.py) before ETL-5"
        )
    return rows[0][0]


def _number(value: Any) -> float | None:
    """A non-negative quantity / cost, or None when the source value is not one."""
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number >= 0 else None


def _audit_date(meta: dict[str, Any]) -> date | None:
    raw = meta.get("audited_at")
    if not raw:
        return None
    try:
        return datetime.fromisoformat(str(raw).replace("Z", "+00:00")).date()
    except ValueError:
        return None


def _reject(rejections: list[dict], stage: str, reason: str, **keys: Any) -> None:
    rejections.append({"stage": stage, **keys, "reason": reason})


def _load_locations(cur, locations, lines, audit_day, rejections):
    """Upsert the SRC-38 location header; return (loaded {code: info}, rejected {code: reason})."""
    discrepancies: dict[str, int] = {}
    for line in lines:
        if line.get("physical_count") != line.get("system_count"):
            code = line.get("location_code")
            discrepancies[code] = discrepancies.get(code, 0) + 1

    loaded: dict[str, dict[str, Any]] = {}
    rejected: dict[str, str] = {}
    for loc in locations:
        code = (loc.get("code") or "").strip()
        ref = (loc.get("legacy_reference") or "").strip()
        loc_type = loc.get("location_type")
        branch_code = loc.get("branch_code")
        reason = None
        branch = technician_id = None
        if not code or not ref:
            reason = "location code or legacy_reference missing in the extract"
        elif code in loaded or code in rejected:
            reason = f"location {code!r} appears twice in the extract header"
        else:
            cur.execute(
                "SELECT id, company_id, operating_unit_id FROM fix_branch WHERE code = %s;",
                (branch_code,),
            )
            rows = cur.fetchall()
            if len(rows) != 1:
                reason = f"branch {branch_code!r} not found on target (fix_branch.code)"
            elif rows[0][1] is None:
                reason = f"branch {branch_code!r} has no company on target"
            else:
                branch = rows[0]
            if reason is None and loc_type == "van":
                custodian = loc.get("custodian_employee_code")
                if not custodian:
                    reason = "van location without a custodian technician in the extract"
                else:
                    cur.execute(
                        "SELECT id FROM hr_employee WHERE employee_code = %s;", (custodian,)
                    )
                    emp = cur.fetchall()
                    if len(emp) != 1:
                        reason = f"van custodian {custodian!r} not found on target (hr_employee)"
                    else:
                        technician_id = emp[0][0]
        if reason:
            if code and code not in rejected and code not in loaded:
                rejected[code] = reason
            _reject(rejections, "location", reason, legacy_reference=ref, location_code=code)
            continue

        branch_id, company_id, ou_id = branch
        values = (
            company_id,
            ou_id,
            branch_id,
            technician_id,
            loc.get("name") or code,
            loc.get("name_bn"),
            loc_type,
            loc.get("van_plate") or None,  # from the count sheet, or NULL - never invented
            audit_day,
            discrepancies.get(code, 0),
            ref,
        )
        cur.execute("SAVEPOINT inv_location;")
        try:
            cur.execute(
                "SELECT id FROM fix_stock_location "
                "WHERE legacy_reference = %s OR (code = %s AND company_id = %s) "
                "ORDER BY (legacy_reference = %s) DESC NULLS LAST, id;",
                (ref, code, company_id, ref),
            )
            existing = cur.fetchall()
            if len(existing) > 1:
                raise ValueError(
                    f"{len(existing)} target locations match {ref!r} / code {code!r}: ambiguous"
                )
            if existing:
                loc_id = existing[0][0]
                cur.execute(
                    """UPDATE fix_stock_location
                       SET company_id = %s, operating_unit_id = %s, branch_id = %s,
                           technician_id = %s, name = %s, name_bn = %s, location_type = %s,
                           is_van_stock = (%s = 'van'), is_van_location = (%s = 'van'),
                           van_plate = %s, last_audit_date = %s, audit_discrepancy_count = %s,
                           legacy_reference = %s, code = %s, active = true, write_date = NOW()
                       WHERE id = %s;""",
                    (*values[:7], loc_type, loc_type, *values[7:], code, loc_id),
                )
            else:
                cur.execute(
                    """INSERT INTO fix_stock_location (
                           company_id, operating_unit_id, branch_id, technician_id, name, name_bn,
                           location_type, is_van_stock, is_van_location, van_plate,
                           last_audit_date, audit_discrepancy_count, legacy_reference, code,
                           state, active, create_date, write_date
                       ) VALUES (%s, %s, %s, %s, %s, %s, %s, (%s = 'van'), (%s = 'van'),
                                 %s, %s, %s, %s, %s, 'active', true, NOW(), NOW())
                       RETURNING id;""",
                    (*values[:7], loc_type, loc_type, *values[7:], code),
                )
                loc_id = cur.fetchone()[0]
            cur.execute("RELEASE SAVEPOINT inv_location;")
        except Exception as exc:
            cur.execute("ROLLBACK TO SAVEPOINT inv_location;")
            rejected[code] = f"load error: {exc}"
            _reject(
                rejections, "location", rejected[code], legacy_reference=ref, location_code=code
            )
            continue
        loaded[code] = {"id": loc_id, "company_id": company_id, "operating_unit_id": ou_id}
    return loaded, rejected


def _load_parts(cur, parts_data, company_id, rejections) -> dict[str, int]:
    """Upsert the SRC-37 catalog; return {part_number: id} of the loaded parts."""
    part_ids: dict[str, int] = {}
    for p in parts_data:
        sku = (p.get("part_number") or "").strip()
        ref = (p.get("legacy_reference") or "").strip()
        reason = None
        if not sku or not ref or not p.get("name"):
            reason = "part_number, name or legacy_reference missing in the extract"
        elif sku in part_ids:
            reason = f"part {sku!r} appears twice in the catalog extract"
        elif _number(p.get("unit_cost")) is None:
            reason = f"unit_cost {p.get('unit_cost')!r} is not a non-negative number"
        if reason:
            _reject(rejections, "part", reason, legacy_reference=ref, part_number=sku)
            continue
        cur.execute("SAVEPOINT inv_part;")
        try:
            cur.execute(
                "SELECT id FROM fix_spare_part "
                "WHERE legacy_reference = %s OR (part_number = %s AND company_id = %s);",
                (ref, sku, company_id),
            )
            existing = cur.fetchall()
            if len(existing) > 1:
                raise ValueError(f"{len(existing)} target parts match {ref!r}: ambiguous")
            common = (
                p["name"],
                p.get("name_bn"),
                p.get("barcode"),
                p.get("qr_code"),
                p.get("category"),
                p.get("brand"),
                bool(p.get("is_serialized")),
                p.get("warranty_months"),
                p["unit_cost"],
                p.get("sales_price"),
                p.get("min_qty"),
                p.get("max_qty"),
                p.get("safety_stock"),
                ref,
            )
            if existing:
                part_id = existing[0][0]
                cur.execute(
                    """UPDATE fix_spare_part
                       SET name = %s, name_bn = %s, barcode = %s, qr_code = %s,
                           part_category = %s, device_brand = %s, is_serialized = %s,
                           warranty_months = %s, unit_cost = %s, sales_price = %s,
                           min_qty = %s, max_qty = %s, safety_stock = %s,
                           legacy_reference = %s, active = true, write_date = NOW()
                       WHERE id = %s;""",
                    (*common, part_id),
                )
            else:
                cur.execute(
                    """INSERT INTO fix_spare_part (
                           name, name_bn, barcode, qr_code, part_category, device_brand,
                           is_serialized, warranty_months, unit_cost, sales_price, min_qty,
                           max_qty, safety_stock, legacy_reference, company_id, part_number,
                           list_price, active, create_date, write_date
                       ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                 %s, %s, %s, true, NOW(), NOW())
                       RETURNING id;""",
                    (*common, company_id, sku, p.get("sales_price")),
                )
                part_id = cur.fetchone()[0]
            cur.execute("RELEASE SAVEPOINT inv_part;")
        except Exception as exc:
            cur.execute("ROLLBACK TO SAVEPOINT inv_part;")
            _reject(rejections, "part", f"load error: {exc}", legacy_reference=ref, part_number=sku)
            continue
        part_ids[sku] = part_id
    return part_ids


def _load_count_lines(cur, lines, header_codes, loc_ids, loc_rejected, part_ids, rejections):
    """Upsert one suspense row per count line (keyed on its legacy reference)."""
    loaded = 0
    qty_by_part: dict[int, float] = {}
    seen_refs: set[str] = set()
    for line in lines:
        ref = (line.get("legacy_reference") or "").strip()
        code = line.get("location_code")
        sku = line.get("part_number")
        system_qty = _number(line.get("system_count"))
        unit_cost = _number(line.get("unit_cost"))
        reason = None
        if not ref:
            reason = "count line without legacy_reference"
        elif ref in seen_refs:
            reason = "legacy_reference appears twice in the count lines"
        elif code not in header_codes:
            reason = f"location {code!r} is not in the count sheet's location header"
        elif code in loc_rejected:
            reason = f"location {code!r} rejected: {loc_rejected[code]}"
        elif sku not in part_ids:
            reason = f"part {sku!r} is not in the loaded SRC-37 catalog"
        elif system_qty is None or _number(line.get("physical_count")) is None:
            reason = "physical_count / system_count is not a non-negative number"
        elif unit_cost is None:
            reason = f"unit_cost {line.get('unit_cost')!r} is not a non-negative number"
        if ref:
            seen_refs.add(ref)
        if reason:
            _reject(
                rejections,
                "count_line",
                reason,
                legacy_reference=ref,
                location_code=code,
                part_number=sku,
            )
            continue

        loc = loc_ids[code]
        part_id = part_ids[sku]
        values = (
            loc["company_id"],
            loc["operating_unit_id"],
            part_id,
            f"VAL-INIT-{code}-{sku}",
            f"প্রারম্ভিক মজুদ গণনা - {code}",
            system_qty,
            unit_cost,
            round(system_qty * unit_cost, 2),
        )
        cur.execute("SAVEPOINT inv_line;")
        try:
            cur.execute(
                "SELECT id FROM fix_inventory_valuation_suspense "
                "WHERE legacy_reference = %s AND entry_type = %s;",
                (ref, ENTRY_TYPE),
            )
            existing = [row[0] for row in cur.fetchall()]
            if existing:
                cur.execute(
                    """UPDATE fix_inventory_valuation_suspense
                       SET company_id = %s, operating_unit_id = %s, product_id = %s,
                           name = %s, name_bn = %s, quantity = %s, unit_cost = %s,
                           total_valuation = %s, write_date = NOW()
                       WHERE id = ANY(%s);""",
                    (*values, existing),
                )
            else:
                cur.execute(
                    """INSERT INTO fix_inventory_valuation_suspense (
                           company_id, operating_unit_id, product_id, name, name_bn,
                           quantity, unit_cost, total_valuation, entry_type,
                           suspense_account_code, status, stub_reference, stub_expiry_date,
                           legacy_reference, create_date, write_date
                       ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                 'pending_gl_cutover', %s, %s, %s, NOW(), NOW());""",
                    (*values, ENTRY_TYPE, SUSPENSE_ACCOUNT, STUB_REFERENCE, STUB_EXPIRY, ref),
                )
            cur.execute("RELEASE SAVEPOINT inv_line;")
        except Exception as exc:
            cur.execute("ROLLBACK TO SAVEPOINT inv_line;")
            _reject(
                rejections,
                "count_line",
                f"load error: {exc}",
                legacy_reference=ref,
                location_code=code,
                part_number=sku,
            )
            continue
        loaded += 1
        qty_by_part[part_id] = qty_by_part.get(part_id, 0.0) + system_qty

    for part_id, total_qty in qty_by_part.items():
        cur.execute(
            "UPDATE fix_spare_part SET qty_available = %s, write_date = NOW() WHERE id = %s;",
            (total_qty, part_id),
        )
    return loaded


# --------------------------------------------------------------------------- measure


def _accuracy(counted: float, abs_variance: float) -> float | None:
    if counted <= 0:
        return None
    return round(max(0.0, 1.0 - abs_variance / counted) * 100.0, 2)


def measure_reconciliation(
    cur, parts_data: list[dict], locations: list[dict], lines: list[dict]
) -> dict[str, Any]:
    """Physical count (extract) vs what the TARGET DATABASE holds after the load.

    Nothing here comes from the loader's own bookkeeping or the extract's claims:
    loaded quantities, valuations, locations and part totals are read back by legacy
    reference. Accuracy = 1 - sum(|loaded - counted|) / sum(counted) over every count
    line of the extract (a rejected line contributes its full count as variance).
    """
    line_refs = [ln.get("legacy_reference") for ln in lines if ln.get("legacy_reference")]
    cur.execute(
        "SELECT legacy_reference, count(*), coalesce(sum(quantity), 0), "
        "coalesce(sum(total_valuation), 0) FROM fix_inventory_valuation_suspense "
        "WHERE legacy_reference = ANY(%s) AND entry_type = %s GROUP BY legacy_reference;",
        (line_refs, ENTRY_TYPE),
    )
    db_lines = {ref: (int(n), float(q), float(v)) for ref, n, q, v in cur.fetchall()}

    loc_refs = [loc.get("legacy_reference") for loc in locations if loc.get("legacy_reference")]
    cur.execute(
        """SELECT l.legacy_reference, l.code, l.location_type, l.van_plate,
                  l.company_id, l.operating_unit_id, b.code, b.name, b.company_id,
                  b.operating_unit_id
           FROM fix_stock_location l LEFT JOIN fix_branch b ON b.id = l.branch_id
           WHERE l.legacy_reference = ANY(%s);""",
        (loc_refs,),
    )
    db_locs: dict[str, list[tuple]] = {}
    for row in cur.fetchall():
        db_locs.setdefault(row[0], []).append(row)

    part_refs = [p.get("legacy_reference") for p in parts_data if p.get("legacy_reference")]
    cur.execute(
        "SELECT legacy_reference, part_number, qty_available FROM fix_spare_part "
        "WHERE legacy_reference = ANY(%s);",
        (part_refs,),
    )
    db_parts = cur.fetchall()

    header = {loc.get("code"): loc for loc in locations}
    order = [loc.get("code") for loc in locations]
    order += sorted({ln.get("location_code") for ln in lines} - set(order), key=str)

    per_location = []
    qty_by_sku: dict[str, float] = {}
    for code in order:
        loc = header.get(code, {})
        loc_lines = [ln for ln in lines if ln.get("location_code") == code]
        counted = loaded = abs_var = valuation = 0.0
        in_db = matching = 0
        for ln in loc_lines:
            physical = _number(ln.get("physical_count")) or 0.0
            n, qty, val = db_lines.get(ln.get("legacy_reference"), (0, 0.0, 0.0))
            counted += physical
            loaded += qty
            valuation += val
            abs_var += abs(qty - physical)
            in_db += 1 if n else 0
            matching += 1 if n and qty == physical else 0
            if n:
                sku = ln.get("part_number")
                qty_by_sku[sku] = qty_by_sku.get(sku, 0.0) + qty
        rows = db_locs.get(loc.get("legacy_reference"), [])
        db_row = rows[0] if len(rows) == 1 else None
        per_location.append(
            {
                "location_code": code,
                "legacy_reference": loc.get("legacy_reference"),
                "location_type": db_row[2] if db_row else loc.get("location_type"),
                "branch_code": db_row[6] if db_row else loc.get("branch_code"),
                "branch_name": db_row[7] if db_row else None,
                "in_database": db_row is not None,
                "location_rows_in_database": len(rows),
                "van_plate": db_row[3] if db_row else None,
                "company_matches_branch": bool(db_row and db_row[4] == db_row[8]),
                "operating_unit_matches_branch": bool(db_row and db_row[5] == db_row[9]),
                "lines_in_extract": len(loc_lines),
                "lines_in_database": in_db,
                "lines_matching_count": matching,
                "counted_units": counted,
                "loaded_units": loaded,
                "net_variance": counted - loaded,
                "abs_variance": abs_var,
                "accuracy_percentage": _accuracy(counted, abs_var),
                "valuation_bdt": round(valuation, 2),
            }
        )

    part_mismatches = [
        {"part_number": sku, "qty_available": float(qty or 0), "loaded_units": qty_by_sku[sku]}
        for _, sku, qty in db_parts
        if sku in qty_by_sku and float(qty or 0) != qty_by_sku[sku]
    ]
    counted = sum(loc["counted_units"] for loc in per_location)
    abs_var = sum(loc["abs_variance"] for loc in per_location)
    return {
        "locations": per_location,
        "counted_units": counted,
        "loaded_units": sum(loc["loaded_units"] for loc in per_location),
        "abs_variance": abs_var,
        "accuracy_percentage": _accuracy(counted, abs_var),
        "valuation_bdt": round(sum(loc["valuation_bdt"] for loc in per_location), 2),
        "lines_in_database": sum(1 for ref in line_refs if ref in db_lines),
        "duplicate_line_rows": sorted(ref for ref, (n, _, _) in db_lines.items() if n > 1),
        "parts_in_database": len({row[0] for row in db_parts}),
        "part_qty_mismatches": part_mismatches,
        "locations_in_database": sum(1 for loc in per_location if loc["in_database"]),
    }


def control_total_problems(meta: dict[str, Any], locations: list, lines: list) -> list[str]:
    """MIG-02: the count sheet's own control totals vs its lines (extract integrity)."""
    control = meta.get("control_totals")
    if not isinstance(control, dict):
        return ["the count sheet declares no control totals"]
    actual = {
        "locations": len(locations),
        "count_lines": len(lines),
        "physical_units": sum(_number(ln.get("physical_count")) or 0.0 for ln in lines),
    }
    return [
        f"control total {key} {control.get(key)!r} != {actual[key]:g} in the extract"
        for key in actual
        if _number(control.get(key)) != float(actual[key])
    ]


def derive_gate_status(
    measured: dict[str, Any],
    rejections: list[dict],
    lines_loaded: int,
    control_problems: list[str],
) -> tuple[str, list[str]]:
    """G2-04 measured status: FAIL / INCOMPLETE / PASS, with every reason."""
    failures = list(control_problems)
    accuracy = measured["accuracy_percentage"]
    if accuracy is None:
        failures.append("no counted units - accuracy cannot be measured")
    elif accuracy < ACCURACY_TARGET:
        failures.append(f"measured accuracy {accuracy}% is below the {ACCURACY_TARGET}% target")
    if measured["duplicate_line_rows"]:
        failures.append(
            f"{len(measured['duplicate_line_rows'])} count lines have more than one suspense "
            "row in the database (non-idempotent history)"
        )
    if measured["lines_in_database"] != lines_loaded:
        failures.append(
            f"loader reported {lines_loaded} count lines loaded but the database holds "
            f"{measured['lines_in_database']}"
        )
    if measured["part_qty_mismatches"]:
        failures.append(
            f"{len(measured['part_qty_mismatches'])} parts' qty_available differs from the "
            "loaded location quantities"
        )
    for loc in measured["locations"]:
        if loc["in_database"] and not (
            loc["company_matches_branch"] and loc["operating_unit_matches_branch"]
        ):
            failures.append(
                f"location {loc['location_code']} company/operating unit differs from its branch"
            )
        if loc["location_rows_in_database"] > 1:
            failures.append(f"location {loc['location_code']} has more than one target row")
    if failures:
        return FAIL, failures
    if rejections:
        return INCOMPLETE, [
            f"{len(rejections)} extract rows rejected - pending steward disposition (MG-004)"
        ]
    return PASS, [f"measured accuracy {accuracy}% >= {ACCURACY_TARGET}%; no rejections"]


# --------------------------------------------------------------------------- record


def _qty(value: float) -> str:
    return f"{int(value):,}" if float(value).is_integer() else f"{value:,.2f}"


def _pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.2f}%"


def _target_name(db_conn) -> str:
    p = parse_dsn(db_conn.dsn)
    return f"{p.get('host', 'localhost')}:{p.get('port', '5432')}/{p.get('dbname', '')}"


def render_record(result: dict[str, Any], max_rejections: int = 100) -> str:
    """Markdown G2-04 reconciliation record - every figure from `result['measured']`."""
    m = result["measured"]
    lines_x = result["count_lines"]
    locs_x = result["locations"]
    parts_x = result["parts"]
    acc = m["accuracy_percentage"]
    acc_met = acc is not None and acc >= ACCURACY_TARGET
    out = [
        "# Inventory Physical Count Reconciliation Record (G2-04)",
        "",
        "**Standard Reference**: `G2-04` Wave Gate Criterion · `MIG-02` Control Totals · "
        "`MIG-03` Legacy References · `GV-009` Measured Evidence  ",
        "**Milestone**: `R03-M01-T06` (Spare Parts & Inventory, ETL-5)  ",
        f"**Generated At**: {result['generated_at']} by `migrations/load_inventory.py`  ",
        f"**Target Database**: `{result['target_database']}`  ",
        f"**Data Classification**: {result['data_classification']}  ",
        "**Data Sources**:",
        f"- `SRC-37`: SKU catalog extract - {parts_x['extracted']} parts",
        f"- `SRC-38`: physical count extract - {locs_x['extracted']} locations, "
        f"{lines_x['extracted']} count lines (audited {result['audited_at'] or 'n/a'})",
        "",
        "Every number below is read back from the target database after the load (by legacy "
        "reference) and compared with the physical count in the SRC-38 extract. Accuracy = "
        "1 - sum(|loaded - counted|) / sum(counted) over every count line; a rejected line "
        "counts in full as variance.",
        "",
        "---",
        "",
        "## 1. Measured Reconciliation Summary",
        "",
        "| Metric | Target | Measured | Result |",
        "|---|---|---|---|",
        f"| Inventory count accuracy | >= {ACCURACY_TARGET:.1f}% | {_pct(acc)} | "
        f"{'MET' if acc_met else 'NOT MET'} |",
        f"| SKUs in database (`LEG:SRC37:*`) | {parts_x['extracted']} | "
        f"{m['parts_in_database']} | {parts_x['rejected']} rejected |",
        f"| Stock locations in database (`LEG:SRC38:<loc>`) | {locs_x['extracted']} | "
        f"{m['locations_in_database']} | {locs_x['rejected']} rejected |",
        f"| Count lines in database | {lines_x['extracted']} | {m['lines_in_database']} | "
        f"{lines_x['rejected']} rejected |",
        f"| Physical units counted (extract) | - | {_qty(m['counted_units'])} | - |",
        f"| System units loaded (database) | - | {_qty(m['loaded_units'])} | - |",
        f"| Absolute unit variance | - | {_qty(m['abs_variance'])} | - |",
        f"| Duplicate suspense rows per legacy reference | 0 | "
        f"{len(m['duplicate_line_rows'])} | - |",
        f"| Parts whose qty_available != loaded units | 0 | "
        f"{len(m['part_qty_mismatches'])} | - |",
        f"| Initial stock valuation (database) | - | BDT {m['valuation_bdt']:,.2f} | "
        f"suspense {SUSPENSE_ACCOUNT} / {STUB_REFERENCE} |",
        "",
        f"**Measured G2-04 status: {result['gate_status']}**",
        "",
    ]
    out += [f"- {reason}" for reason in result["gate_status_reasons"]]
    out += [
        "",
        "This record is generated evidence, not an approval: gate G2-04 stays open until "
        "every role in section 4 has completed its sign-off.",
        "",
        "---",
        "",
        "## 2. Location Breakdown",
        "",
        "| Branch / Hub | Location Code | Type | Counted Qty | Loaded Qty (DB) "
        "| Net Variance | Accuracy |",
        "|---|---|---|---|---|---|---|",
    ]
    for loc in m["locations"]:
        branch = loc["branch_name"] or f"{loc['branch_code']} (not on target)"
        out.append(
            f"| {branch} | `{loc['location_code']}` | {loc['location_type'] or '-'} | "
            f"{_qty(loc['counted_units'])} | {_qty(loc['loaded_units'])} | "
            f"{_qty(loc['net_variance'])} | {_pct(loc['accuracy_percentage'])} |"
        )
    out += [
        f"| **Totals** | - | - | **{_qty(m['counted_units'])}** | **{_qty(m['loaded_units'])}** "
        f"| **{_qty(m['counted_units'] - m['loaded_units'])}** | **{_pct(acc)}** |",
        "",
        "| Location Code | Lines (extract) | Lines (DB) | Lines matching count | "
        "Abs Variance | Van Plate (DB) |",
        "|---|---|---|---|---|---|",
    ]
    for loc in m["locations"]:
        out.append(
            f"| `{loc['location_code']}` | {loc['lines_in_extract']} | "
            f"{loc['lines_in_database']} | {loc['lines_matching_count']} | "
            f"{_qty(loc['abs_variance'])} | {loc['van_plate'] or '-'} |"
        )
    out += ["", "---", "", "## 3. Rejected Extract Rows", ""]
    rejections = result["rejections"]
    if not rejections:
        out.append("None - every extract row was loaded.")
    else:
        out += [
            f"{len(rejections)} rows rejected (parts {parts_x['rejected']}, locations "
            f"{locs_x['rejected']}, count lines {lines_x['rejected']}):",
            "",
            "| Stage | Legacy Reference | Reason |",
            "|---|---|---|",
        ]
        for rej in rejections[:max_rejections]:
            out.append(
                f"| {rej['stage']} | `{rej.get('legacy_reference') or '-'}` | {rej['reason']} |"
            )
        if len(rejections) > max_rejections:
            out.append(
                f"| ... | ... | {len(rejections) - max_rejections} more in the load result |"
            )
    out += [
        "",
        "---",
        "",
        "## 4. Sign-off",
        "",
        "No sign-off has been recorded. Each role must review the measured figures above:",
        "",
    ]
    out += [f"- Sign-off: PENDING - {role}" for role in result["sign_off_roles"]]
    out.append("")
    return "\n".join(out)


def load_inventory(
    parts_path: Path,
    counts_path: Path,
    db_conn,
    signoff_path: Path | None = SIGNOFF_DOC,
    fixture_path: Path | None = None,
) -> dict[str, Any]:
    """Load the SRC-37 catalog and SRC-38 count baseline, measure, write the G2-04 record.

    `signoff_path` defaults to the committed docs/traceability record; tests pass a tmp
    path (None skips the record).
    """
    parts_data = json.loads(parts_path.read_text(encoding="utf-8"))
    payload = json.loads(counts_path.read_text(encoding="utf-8"))
    meta = payload.get("metadata") or {}
    locations = payload.get("locations") or []
    lines = payload.get("lines") or []
    rejections: list[dict[str, Any]] = []

    with db_conn.cursor() as cur:
        require_inventory_schema(cur)
        catalog_company = resolve_catalog_company(cur, fixture_path)
        loc_ids, loc_rejected = _load_locations(
            cur, locations, lines, _audit_date(meta), rejections
        )
        part_ids = _load_parts(cur, parts_data, catalog_company, rejections)
        header_codes = {loc.get("code") for loc in locations}
        lines_loaded = _load_count_lines(
            cur, lines, header_codes, loc_ids, loc_rejected, part_ids, rejections
        )
    db_conn.commit()

    with db_conn.cursor() as cur:
        measured = measure_reconciliation(cur, parts_data, locations, lines)
    control_problems = control_total_problems(meta, locations, lines)
    gate_status, reasons = derive_gate_status(measured, rejections, lines_loaded, control_problems)

    def stage(name: str, extracted: int, loaded: int) -> dict[str, int]:
        rejected = sum(1 for r in rejections if r["stage"] == name)
        return {"extracted": extracted, "loaded": loaded, "rejected": rejected}

    result: dict[str, Any] = {
        "entity": "inventory_physical_baseline",
        "generated_at": datetime.now(UTC).isoformat(),
        "target_database": _target_name(db_conn),
        "data_classification": meta.get("data_classification", "UNDECLARED"),
        "audited_at": meta.get("audited_at"),
        "parts": stage("part", len(parts_data), len(part_ids)),
        "locations": stage("location", len(locations), len(loc_ids)),
        "count_lines": stage("count_line", len(lines), lines_loaded),
        "rejected_count": len(rejections),
        "rejections": rejections,
        "measured": measured,
        "total_physical_units_counted": measured["counted_units"],
        "total_units_loaded": measured["loaded_units"],
        "accuracy_percentage": measured["accuracy_percentage"],
        "total_valuation_bdt": measured["valuation_bdt"],
        "suspense_account": SUSPENSE_ACCOUNT,
        "stub_reference": STUB_REFERENCE,
        "gate_criterion": "G2-04",
        "gate_status": gate_status,
        "gate_status_reasons": reasons,
        "sign_off_roles": list(meta.get("sign_off_roles") or SIGN_OFF_ROLES),
        "sign_off_status": "PENDING",
    }
    if signoff_path is not None:
        signoff_path.parent.mkdir(parents=True, exist_ok=True)
        signoff_path.write_text(render_record(result), encoding="utf-8", newline="\n")
    return result


def exit_code(gate_status: str) -> int:
    return {PASS: 0, FAIL: 1}.get(gate_status, 2)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Wave-2 M15 inventory baseline load (ETL-5)")
    parser.add_argument(
        "--extracts-dir",
        type=Path,
        default=EXTRACTS_DIR,
        help="where the SRC-37/SRC-38 extracts live (default: migrations/extracts)",
    )
    parser.add_argument(
        "--no-generate",
        action="store_true",
        help="load the extracts already in --extracts-dir instead of regenerating the "
        "synthetic ones",
    )
    parser.add_argument(
        "--signoff",
        type=Path,
        default=SIGNOFF_DOC,
        help="G2-04 reconciliation record path (default: docs/traceability/...)",
    )
    args = parser.parse_args(argv)
    # Target: the dedicated rehearsal database fix_migration (never fix_dev, DE-12);
    # DATABASE_URL / PG* override - resolved in migrations/target_db.py.
    repo_root = str(MIGRATIONS_DIR.parent)
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from migrations.target_db import connect

    if args.no_generate:
        parts_path = args.extracts_dir / "inventory_parts_extract.json"
        counts_path = args.extracts_dir / "inventory_physical_count_extract.json"
    else:
        parts_path, counts_path = generate_inventory_extracts(args.extracts_dir)
    conn = connect()
    try:
        result = load_inventory(parts_path, counts_path, conn, args.signoff)
    finally:
        conn.close()
    summary = {k: v for k, v in result.items() if k not in ("measured", "rejections")}
    print("=" * 70)
    print("Wave-2 M15 Inventory Physical Count Migration & Reconciliation")
    print("=" * 70)
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    for rej in result["rejections"][:20]:
        print(f"  REJECTED {rej['stage']}: {rej.get('legacy_reference')} - {rej['reason']}")
    print("=" * 70)
    print(f"Gate Criterion G2-04 Status: {result['gate_status']}")
    print(f"Inventory Accuracy: {_pct(result['accuracy_percentage'])} (Target >= 95.0%)")
    print(f"Reconciliation record: {args.signoff} (sign-off PENDING)")
    return exit_code(result["gate_status"])


if __name__ == "__main__":
    sys.exit(main())
