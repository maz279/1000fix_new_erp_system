#!/usr/bin/env python3
"""migrations/load_branches.py — ETL-3: Branch master loader.

Specification: docs/p04/migration-etl-specs.md (ETL-3).
Target model: fix.branch (table fix_branch).
Legacy reference: BR:PILOT_2026:<branch_code>
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def load_branches(extract_path: Path, db_conn) -> dict[str, Any]:
    """Load branches from extract into fix_branch table."""
    data = json.loads(extract_path.read_text(encoding="utf-8"))
    loaded_count = 0
    rejected_count = 0
    rejections = []

    with db_conn.cursor() as cur:
        # Resolve company_id and default operating_unit_id
        cur.execute("SELECT id, company_id FROM fix_entity LIMIT 1;")
        entity_row = cur.fetchone()
        entity_id = entity_row[0] if entity_row else 1
        company_id = entity_row[1] if entity_row and entity_row[1] else 1

        cur.execute("SELECT id FROM operating_unit WHERE code = 'OU1' LIMIT 1;")
        ou_row = cur.fetchone()
        default_ou_id = ou_row[0] if ou_row else 1

        for item in data:
            code = item["code"]
            name = item["name"]
            name_bn = item.get("name_bn", "")
            phone = item.get("phone", "")
            email = item.get("email", "")
            legacy_ref = item["legacy_reference"]

            try:
                # Check if already exists by legacy_reference or code
                cur.execute(
                    "SELECT id FROM fix_branch WHERE legacy_reference = %s OR code = %s;",
                    (legacy_ref, code)
                )
                existing = cur.fetchone()
                if existing:
                    cur.execute(
                        """UPDATE fix_branch
                           SET name = %s, name_bn = %s, phone = %s, email = %s,
                               legacy_reference = %s, active = true
                           WHERE id = %s;""",
                        (name, name_bn, phone, email, legacy_ref, existing[0])
                    )
                else:
                    cur.execute(
                        """INSERT INTO fix_branch (
                               code, name, name_bn, phone, email,
                               entity_id, operating_unit_id, company_id,
                               legacy_reference, active, create_date, write_date
                           ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, true, NOW(), NOW());""",
                        (code, name, name_bn, phone, email,
                         entity_id, default_ou_id, company_id, legacy_ref)
                    )
                loaded_count += 1
            except Exception as e:
                rejected_count += 1
                rejections.append({"code": code, "error": str(e)})

    db_conn.commit()
    return {
        "entity": "branches",
        "total_records": len(data),
        "loaded_count": loaded_count,
        "rejected_count": rejected_count,
        "rejections": rejections,
    }
