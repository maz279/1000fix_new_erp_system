#!/usr/bin/env python3
"""migrations/load_reference_data.py — ETL-0: prerequisite reference data for a clean target.

A clean install (`tooling/scripts/build-test-db.py --db fix_migration`) carries
res.company, operating unit OU1 and the fix.role catalogue (R-01..R-53), but
none of the reference rows the Wave-1 loaders resolve. This stage loads them
from the rehearsal's own inputs, so the run never depends on whatever happens
to be in a developer database:

  * fix.entity        — the legal entity every fix.branch belongs to
                        (fixture: migrations/fixtures/wave1_reference_data.json)
  * operating_unit    — every operating_unit_code named in branches_extract.json is
                        resolved; a missing one is only created when the fixture
                        names it (`operating_units: {code: name}`) - never with an
                        invented name - otherwise it is reported and ETL-3 rejects
                        the branches that need it
  * fix.brand /       — every (brand_name, device_model_name, device_type) in
    fix.device.model    devices_extract.json (the extract's device_model_id is a
                        legacy surrogate id and is NOT trusted)

Idempotent: rows are matched on their natural keys and reused, never duplicated.
No fallbacks: the target must have exactly one res.company, the entity's operating
unit is the one the fixture names, and a brand is only created with the code the
fixture gives it (a brand without one is reported, its models are not created and
ETL-2 rejects the devices that need them).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

MIGRATIONS_DIR = Path(__file__).resolve().parent
FIXTURE_FILE = MIGRATIONS_DIR / "fixtures" / "wave1_reference_data.json"

# fix.device.model.device_type selection (cd_catalogue)
DEVICE_TYPES = frozenset(
    {
        "smartphone",
        "tablet",
        "laptop",
        "desktop",
        "tv",
        "appliance_washer",
        "appliance_fridge",
        "appliance_ac",
        "appliance_microwave",
        "other",
    }
)


def map_device_type(raw: str, type_map: dict[str, str]) -> str:
    value = type_map.get(raw, raw)
    return value if value in DEVICE_TYPES else "other"


def _company(cur) -> tuple[int, int]:
    """The target's single company - a clean rehearsal install has exactly one."""
    cur.execute("SELECT id, partner_id FROM res_company ORDER BY id;")
    rows = cur.fetchall()
    if len(rows) != 1:
        raise RuntimeError(
            f"target has {len(rows)} res.company rows - ETL-0 needs exactly one "
            "(a clean fix_migration build); refusing to guess which company to use"
        )
    return rows[0][0], rows[0][1]


def _ensure_entity(cur, spec: dict[str, Any], company_id: int) -> tuple[int, bool]:
    cur.execute("SELECT id FROM fix_entity WHERE code = %s;", (spec["code"],))
    row = cur.fetchone()
    if row:
        return row[0], False
    cur.execute("SELECT id FROM res_country WHERE code = %s;", (spec["country_code"],))
    country = cur.fetchone()
    if not country:
        raise RuntimeError(f"res.country {spec['country_code']!r} missing on target")
    cur.execute("SELECT id FROM res_currency WHERE name = %s;", (spec["currency"],))
    currency = cur.fetchone()
    if not currency:
        raise RuntimeError(f"res.currency {spec['currency']!r} missing on target")
    ou_code = spec.get("operating_unit_code")
    cur.execute("SELECT id FROM operating_unit WHERE code = %s;", (ou_code,))
    ou = cur.fetchone()
    if not ou:
        raise RuntimeError(
            f"operating unit {ou_code!r} named for entity {spec['code']!r} missing on target"
        )
    cur.execute(
        """INSERT INTO fix_entity (
               code, legal_name, legal_name_bn, company_id, country_id, currency_id,
               operating_unit_id, statutory_calendar_rule, vat_statutory_day,
               branch_count, active, create_date, write_date
           ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 0, true, NOW(), NOW())
           RETURNING id;""",
        (
            spec["code"],
            spec["legal_name"],
            spec.get("legal_name_bn"),
            company_id,
            country[0],
            currency[0],
            ou[0],
            spec["statutory_calendar_rule"],
            spec.get("vat_statutory_day", 15),
        ),
    )
    return cur.fetchone()[0], True


def _ensure_operating_units(
    cur, codes: list[str], names: dict[str, str], company_id: int, company_partner_id: int
) -> tuple[int, list[str]]:
    """Resolve the extract's OU codes; create only the ones the fixture names."""
    created = 0
    missing = []
    for code in codes:
        cur.execute("SELECT id FROM operating_unit WHERE code = %s;", (code,))
        if cur.fetchone():
            continue
        if not names.get(code):
            missing.append(code)  # ETL-3 rejects the branches that reference it
            continue
        cur.execute(
            """INSERT INTO operating_unit (code, name, company_id, partner_id, active,
                                           create_date, write_date)
               VALUES (%s, %s, %s, %s, true, NOW(), NOW());""",
            (code, names[code], company_id, company_partner_id),
        )
        created += 1
    return created, missing


def _ensure_catalogue(
    cur, devices: list[dict[str, Any]], fixture: dict[str, Any], company_id: int
) -> tuple[int, int, int, list[str]]:
    brand_codes: dict[str, str] = fixture.get("brand_codes", {})
    type_map: dict[str, str] = fixture.get("device_type_map", {})
    brands_created = models_created = 0
    brand_ids: dict[str, int] = {}
    brands_without_code: list[str] = []
    model_keys = sorted(
        {
            (d.get("brand_name", ""), d.get("device_model_name", ""), d.get("device_type", ""))
            for d in devices
            if d.get("brand_name") and d.get("device_model_name")
        }
    )
    for brand, model, raw_type in model_keys:
        if brand in brands_without_code:
            continue
        if brand not in brand_ids:
            cur.execute("SELECT id FROM fix_brand WHERE name = %s;", (brand,))
            row = cur.fetchone()
            if row:
                brand_ids[brand] = row[0]
            elif not brand_codes.get(brand):
                brands_without_code.append(brand)  # never an invented code
                continue
            else:
                code = brand_codes[brand]
                cur.execute(
                    """INSERT INTO fix_brand (name, code, active, authorised, model_count,
                                              create_date, write_date)
                       VALUES (%s, %s, true, false, 0, NOW(), NOW()) RETURNING id;""",
                    (brand, code),
                )
                brand_ids[brand] = cur.fetchone()[0]
                brands_created += 1
        cur.execute(
            "SELECT id FROM fix_device_model WHERE brand_id = %s AND name = %s;",
            (brand_ids[brand], model),
        )
        if cur.fetchone():
            continue
        cur.execute(
            """INSERT INTO fix_device_model (
                   company_id, brand_id, name, device_type, discontinued, parts_available,
                   active, create_date, write_date
               ) VALUES (%s, %s, %s, %s, false, true, true, NOW(), NOW());""",
            (company_id, brand_ids[brand], model, map_device_type(raw_type, type_map)),
        )
        models_created += 1
    return len(model_keys), brands_created, models_created, brands_without_code


def load_reference_data(
    extracts_dir: Path, db_conn, fixture_path: Path | None = None
) -> dict[str, Any]:
    """Ensure the prerequisite reference rows exist on the target; commit."""
    fixture = json.loads((fixture_path or FIXTURE_FILE).read_text(encoding="utf-8"))
    branches = json.loads((extracts_dir / "branches_extract.json").read_text(encoding="utf-8"))
    devices = json.loads((extracts_dir / "devices_extract.json").read_text(encoding="utf-8"))
    ou_codes = sorted({b["operating_unit_code"] for b in branches if b.get("operating_unit_code")})

    with db_conn.cursor() as cur:
        company_id, company_partner_id = _company(cur)
        entity_id, entity_created = _ensure_entity(cur, fixture["entity"], company_id)
        ous_created, ous_missing = _ensure_operating_units(
            cur, ou_codes, fixture.get("operating_units", {}), company_id, company_partner_id
        )
        models_total, brands_created, models_created, brands_without_code = _ensure_catalogue(
            cur, devices, fixture, company_id
        )
    db_conn.commit()
    return {
        "entity": "reference_data",
        "company_id": company_id,
        "entity_id": entity_id,
        "entity_created": entity_created,
        "operating_units": len(ou_codes),
        "operating_units_created": ous_created,
        "operating_units_missing": ous_missing,
        "device_models": models_total,
        "brands_created": brands_created,
        "device_models_created": models_created,
        "brands_without_code": brands_without_code,
    }
