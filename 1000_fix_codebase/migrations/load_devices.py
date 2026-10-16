#!/usr/bin/env python3
"""migrations/load_devices.py — ETL-2: Device and customer asset master loader.

Specification: docs/p04/migration-etl-specs.md (ETL-2).
Target models: fix.device, fix.warranty.
Match key: Serial Number / IMEI-1 uniqueness gate.
Legacy reference: DEV:ASSET_SHEET:<serial>
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def load_devices(extract_path: Path, db_conn) -> dict[str, Any]:
    """Load devices from extract with serial/IMEI uniqueness and warranty linking."""
    data = json.loads(extract_path.read_text(encoding="utf-8"))
    loaded_count = 0
    rejected_count = 0
    rejections = []
    seen_serials: set[str] = set()

    with db_conn.cursor() as cur:
        # Default company and operating unit
        cur.execute("SELECT id FROM res_company LIMIT 1;")
        company_id = cur.fetchone()[0]
        cur.execute("SELECT id FROM operating_unit WHERE code = 'OU1' LIMIT 1;")
        ou_row = cur.fetchone()
        operating_unit_id = ou_row[0] if ou_row else 1
        cur.execute("SELECT id FROM res_currency WHERE name = 'BDT' LIMIT 1;")
        curr_row = cur.fetchone()
        currency_id = curr_row[0] if curr_row else 55

        for item in data:
            serial = item.get("serial_number", "").strip()
            imei_1 = item.get("imei_1", "").strip()
            imei_2 = item.get("imei_2", "").strip()
            model_id = item.get("device_model_id", 6)
            brand_name = item.get("brand_name", "")
            dev_type = item.get("device_type", "mobile")
            cust_ref = item.get("customer_legacy_ref", "")
            branch_code = item.get("branch_code", "HQ")
            purchase_date = item.get("purchase_date")
            w_start = item.get("warranty_start")
            w_end = item.get("warranty_end")
            legacy_ref = item["legacy_reference"]

            # Serial uniqueness check in batch
            if serial and serial in seen_serials:
                # Duplicate serial edge case — flag for MDM review per ETL-2 spec
                rejected_count += 1
                rejections.append({
                    "legacy_reference": legacy_ref,
                    "serial_number": serial,
                    "reason": "MDM collision: Duplicate serial number detected — flagged for MDM steward review"
                })
                continue
            if serial:
                seen_serials.add(serial)

            # Resolve owner_id from customer legacy reference
            owner_id = None
            if cust_ref:
                cur.execute("SELECT id FROM res_partner WHERE legacy_reference = %s;", (cust_ref,))
                owner_row = cur.fetchone()
                if owner_row:
                    owner_id = owner_row[0]

            # Resolve branch_id from branch code
            cur.execute("SELECT id FROM fix_branch WHERE code = %s LIMIT 1;", (branch_code,))
            branch_row = cur.fetchone()
            branch_id = branch_row[0] if branch_row else None

            # Resolve brand_id from model
            cur.execute("SELECT brand_id FROM fix_device_model WHERE id = %s;", (model_id,))
            brand_row = cur.fetchone()
            brand_id = brand_row[0] if brand_row else None

            device_name = f"{brand_name} {serial}" if serial else f"{brand_name} Device"

            cur.execute("SAVEPOINT device_sp;")
            try:
                # Check if device already exists by legacy_reference or serial_number
                cur.execute(
                    "SELECT id FROM fix_device WHERE legacy_reference = %s OR (serial_number = %s AND serial_number != '');",
                    (legacy_ref, serial)
                )
                existing = cur.fetchone()
                if existing:
                    device_id = existing[0]
                    cur.execute(
                        """UPDATE fix_device
                           SET name = %s, imei_1 = %s, imei_2 = %s, owner_id = %s,
                               branch_id = %s, purchase_date = %s, active = true
                           WHERE id = %s;""",
                        (device_name, imei_1, imei_2, owner_id, branch_id, purchase_date, device_id)
                    )
                else:
                    cur.execute(
                        """INSERT INTO fix_device (
                               name, serial_number, imei_1, imei_2, device_model_id,
                               brand_id, device_type, owner_id, branch_id, company_id,
                               operating_unit_id, purchase_date, legacy_reference,
                               active, warranty_status, state, create_date, write_date
                           ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, true, 'in_warranty', 'registered', NOW(), NOW())
                           RETURNING id;""",
                        (device_name, serial, imei_1, imei_2, model_id, brand_id, dev_type,
                         owner_id, branch_id, company_id, operating_unit_id, purchase_date, legacy_ref)
                    )
                    device_id = cur.fetchone()[0]

                # Link warranty if evidenced
                if w_start and w_end:
                    cur.execute("SELECT id FROM fix_warranty WHERE device_id = %s;", (device_id,))
                    if not cur.fetchone():
                        cur.execute(
                            """INSERT INTO fix_warranty (
                                   device_id, company_id, operating_unit_id, currency_id, start_date,
                                   end_date, warranty_type, status, create_date, write_date
                               ) VALUES (%s, %s, %s, %s, %s, %s, 'brand_standard', 'active', NOW(), NOW());""",
                            (device_id, company_id, operating_unit_id, currency_id, w_start, w_end)
                        )

                cur.execute("RELEASE SAVEPOINT device_sp;")
                loaded_count += 1
            except Exception as e:
                cur.execute("ROLLBACK TO SAVEPOINT device_sp;")
                rejected_count += 1
                rejections.append({"legacy_reference": legacy_ref, "error": str(e)})

    db_conn.commit()
    return {
        "entity": "devices",
        "total_records": len(data),
        "loaded_count": loaded_count,
        "rejected_count": rejected_count,
        "rejections": rejections,
    }
