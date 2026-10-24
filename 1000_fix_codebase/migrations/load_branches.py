#!/usr/bin/env python3
"""migrations/load_branches.py — ETL-3: Branch master loader.

Specification: docs/p04/migration-etl-specs.md (ETL-3).
Target model: fix.branch (table fix_branch).
Legacy reference: BR:PILOT_2026:<branch_code>
Prerequisites: fix.entity + the operating units named in the extract (ETL-0).
The legal entity is the one the reference fixture names (entity.code); a branch
whose operating unit is missing on the target, or that names none, is rejected
(counted and listed) - never defaulted to OU1.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

FIXTURE_FILE = Path(__file__).resolve().parent / "fixtures" / "wave1_reference_data.json"


def load_branches(extract_path: Path, db_conn, fixture_path: Path | None = None) -> dict[str, Any]:
    """Load branches from extract into fix_branch table."""
    data = json.loads(extract_path.read_text(encoding="utf-8"))
    fixture = json.loads((fixture_path or FIXTURE_FILE).read_text(encoding="utf-8"))
    entity_code = fixture["entity"]["code"]
    loaded_count = 0
    rejected_count = 0
    rejections = []

    with db_conn.cursor() as cur:
        # Resolve the legal entity (and its company) by the fixture's entity code. On a
        # clean target it is created by ETL-0 (migrations/load_reference_data.py) - never
        # "the first entity" and never surrogate id 1.
        cur.execute("SELECT id, company_id FROM fix_entity WHERE code = %s;", (entity_code,))
        entity_row = cur.fetchone()
        if not entity_row:
            raise RuntimeError(
                f"fix_entity {entity_code!r} missing on target - run ETL-0 reference data "
                "(migrations/load_reference_data.py) before ETL-3"
            )
        entity_id, company_id = entity_row

        ou_ids: dict[str, int | None] = {}

        def resolve_ou(ou_code: str) -> int | None:
            if ou_code not in ou_ids:
                cur.execute("SELECT id FROM operating_unit WHERE code = %s LIMIT 1;", (ou_code,))
                row = cur.fetchone()
                ou_ids[ou_code] = row[0] if row else None
            return ou_ids[ou_code]

        for item in data:
            code = item["code"]
            name = item["name"]
            name_bn = item.get("name_bn", "")
            phone = item.get("phone", "")
            email = item.get("email", "")
            legacy_ref = item["legacy_reference"]
            ou_code = item.get("operating_unit_code")

            cur.execute("SAVEPOINT branch_sp;")
            try:
                if not ou_code:
                    raise ValueError("no operating_unit_code in the extract")
                ou_id = resolve_ou(ou_code)
                if ou_id is None:
                    raise ValueError(f"operating unit {ou_code!r} not found on target")
                # Check if already exists by legacy_reference or code
                cur.execute(
                    "SELECT id FROM fix_branch WHERE legacy_reference = %s OR code = %s;",
                    (legacy_ref, code),
                )
                existing = cur.fetchone()
                if existing:
                    cur.execute(
                        """UPDATE fix_branch
                           SET name = %s, name_bn = %s, phone = %s, email = %s,
                               operating_unit_id = %s, legacy_reference = %s, active = true
                           WHERE id = %s;""",
                        (name, name_bn, phone, email, ou_id, legacy_ref, existing[0]),
                    )
                else:
                    cur.execute(
                        """INSERT INTO fix_branch (
                               code, name, name_bn, phone, email,
                               entity_id, operating_unit_id, company_id,
                               legacy_reference, active, create_date, write_date
                           ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, true, NOW(), NOW());""",
                        (
                            code,
                            name,
                            name_bn,
                            phone,
                            email,
                            entity_id,
                            ou_id,
                            company_id,
                            legacy_ref,
                        ),
                    )
                cur.execute("RELEASE SAVEPOINT branch_sp;")
                loaded_count += 1
            except Exception as e:
                cur.execute("ROLLBACK TO SAVEPOINT branch_sp;")
                rejected_count += 1
                rejections.append({"legacy_reference": legacy_ref, "code": code, "error": str(e)})

    db_conn.commit()
    return {
        "entity": "branches",
        "total_records": len(data),
        "loaded_count": loaded_count,
        "rejected_count": rejected_count,
        "rejections": rejections,
    }
