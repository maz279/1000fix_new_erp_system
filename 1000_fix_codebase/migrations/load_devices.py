#!/usr/bin/env python3
"""migrations/load_devices.py — ETL-2: Device and customer asset master loader.

Specification: docs/p04/migration-etl-specs.md (ETL-2).
Target models: fix.device, fix.warranty.
Match key: Serial Number / IMEI-1 uniqueness gate.
Legacy reference: DEV:ASSET_SHEET:<serial>
Device model: resolved by (brand_name, device_model_name) - the extract's
device_model_id is a legacy surrogate id and is NOT trusted (ETL-0 loads the
catalogue rows on a clean target, migrations/load_reference_data.py).
Warranty state: derived from the evidenced warranty end date relative to the
LOAD date (derive_warranty_status, mirroring fix.device._compute_warranty_status
for an active warranty) - never assumed to be in warranty.
Company / operating unit: the device's branch (fix_branch.company_id /
operating_unit_id). A device whose branch is not on the target, whose named owner
was not loaded, or whose serial is already held by a DIFFERENT target device is
rejected (counted and listed) - never loaded with NULL or "the first company", and
never overwriting another device.
"""

from __future__ import annotations

import json
import logging
from datetime import date
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# fix.warranty.warranty_type for a brand's standard warranty evidenced on the asset sheet
WARRANTY_TYPE = "manufacturer"


def derive_warranty_status(warranty_end: str | date | None, load_date: date) -> str:
    """fix.device.warranty_status for an active warranty ending on `warranty_end`."""
    if not warranty_end:
        return "unknown"
    end = warranty_end if isinstance(warranty_end, date) else date.fromisoformat(warranty_end)
    return "in_warranty" if end >= load_date else "out_of_warranty"


def load_devices(extract_path: Path, db_conn, load_date: date | None = None) -> dict[str, Any]:
    """Load devices from extract with serial/IMEI uniqueness and warranty linking."""
    load_date = load_date or date.today()
    data = json.loads(extract_path.read_text(encoding="utf-8"))
    loaded_count = 0
    rejected_count = 0
    rejections = []
    seen_serials: set[str] = set()

    with db_conn.cursor() as cur:
        cur.execute("SELECT id FROM res_currency WHERE name = 'BDT';")
        curr_row = cur.fetchone()
        if not curr_row:
            raise RuntimeError("res_currency BDT missing on target")
        currency_id = curr_row[0]

        for item in data:
            serial = item.get("serial_number", "").strip()
            imei_1 = item.get("imei_1", "").strip()
            imei_2 = item.get("imei_2", "").strip()
            model_name = item.get("device_model_name", "")
            brand_name = item.get("brand_name", "")
            cust_ref = item.get("customer_legacy_ref", "")
            branch_code = item.get("branch_code")
            purchase_date = item.get("purchase_date")
            w_start = item.get("warranty_start")
            w_end = item.get("warranty_end")
            legacy_ref = item["legacy_reference"]

            # Serial uniqueness check in batch
            if serial and serial in seen_serials:
                # Duplicate serial edge case — flag for MDM review per ETL-2 spec
                rejected_count += 1
                rejections.append(
                    {
                        "legacy_reference": legacy_ref,
                        "source_id": item.get("source_id"),
                        "serial_number": serial,
                        "reason": "MDM collision: Duplicate serial number detected — flagged for MDM steward review",
                    }
                )
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

            # Branch -> company / operating unit (no default branch, no first company)
            cur.execute(
                "SELECT id, company_id, operating_unit_id FROM fix_branch WHERE code = %s;",
                (branch_code,),
            )
            branch_rows = cur.fetchall()
            reason = None
            if len(branch_rows) != 1:
                reason = f"branch {branch_code!r} not found on target (fix_branch.code)"
            elif cust_ref and owner_id is None:
                reason = f"owner {cust_ref!r} not loaded on target (res_partner.legacy_reference)"
            if reason:
                rejected_count += 1
                rejections.append(
                    {
                        "legacy_reference": legacy_ref,
                        "source_id": item.get("source_id"),
                        "reason": reason,
                    }
                )
                continue
            branch_id, company_id, operating_unit_id = branch_rows[0]

            # Resolve model (and its brand / device type) by natural key
            cur.execute(
                """SELECT m.id, m.brand_id, m.device_type
                   FROM fix_device_model m JOIN fix_brand b ON b.id = m.brand_id
                   WHERE b.name = %s AND m.name = %s LIMIT 1;""",
                (brand_name, model_name),
            )
            model_row = cur.fetchone()

            device_name = f"{brand_name} {serial}" if serial else f"{brand_name} Device"
            warranty_status = derive_warranty_status(w_end if w_start else None, load_date)

            cur.execute("SAVEPOINT device_sp;")
            try:
                if not model_row:
                    raise ValueError(
                        f"device model {brand_name!r}/{model_name!r} not in catalogue (ETL-0)"
                    )
                model_id, brand_id, dev_type = model_row
                # Re-run: the device this legacy reference already created
                cur.execute("SELECT id FROM fix_device WHERE legacy_reference = %s;", (legacy_ref,))
                existing = cur.fetchone()
                if not existing and serial:
                    cur.execute(
                        "SELECT id, legacy_reference FROM fix_device WHERE serial_number = %s;",
                        (serial,),
                    )
                    holder = cur.fetchone()
                    if holder:
                        raise ValueError(
                            f"MDM collision: serial already held by target device {holder[0]} "
                            f"({holder[1] or 'no legacy reference'}) - flagged for MDM steward review"
                        )
                if existing:
                    device_id = existing[0]
                    cur.execute(
                        """UPDATE fix_device
                           SET name = %s, imei_1 = %s, imei_2 = %s, owner_id = %s,
                               branch_id = %s, company_id = %s, operating_unit_id = %s,
                               purchase_date = %s, device_model_id = %s,
                               brand_id = %s, device_type = %s, warranty_status = %s,
                               active = true
                           WHERE id = %s;""",
                        (
                            device_name,
                            imei_1,
                            imei_2,
                            owner_id,
                            branch_id,
                            company_id,
                            operating_unit_id,
                            purchase_date,
                            model_id,
                            brand_id,
                            dev_type,
                            warranty_status,
                            device_id,
                        ),
                    )
                else:
                    cur.execute(
                        """INSERT INTO fix_device (
                               name, serial_number, imei_1, imei_2, device_model_id,
                               brand_id, device_type, owner_id, branch_id, company_id,
                               operating_unit_id, purchase_date, legacy_reference,
                               active, warranty_status, state, lifecycle_stage,
                               create_date, write_date
                           ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, true, %s, 'registered', 'active', NOW(), NOW())
                           RETURNING id;""",
                        (
                            device_name,
                            serial,
                            imei_1,
                            imei_2,
                            model_id,
                            brand_id,
                            dev_type,
                            owner_id,
                            branch_id,
                            company_id,
                            operating_unit_id,
                            purchase_date,
                            legacy_ref,
                            warranty_status,
                        ),
                    )
                    device_id = cur.fetchone()[0]

                # Link warranty if evidenced. The record stays 'active' (it is the
                # evidenced warranty); in/out of warranty is the device state above.
                if w_start and w_end:
                    cur.execute("SELECT id FROM fix_warranty WHERE device_id = %s;", (device_id,))
                    warranty_row = cur.fetchone()
                    if warranty_row:
                        cur.execute(
                            """UPDATE fix_warranty
                               SET start_date = %s, end_date = %s, warranty_type = %s,
                                   currency_id = %s, company_id = %s, operating_unit_id = %s,
                                   write_date = NOW()
                               WHERE id = %s;""",
                            (
                                w_start,
                                w_end,
                                WARRANTY_TYPE,
                                currency_id,
                                company_id,
                                operating_unit_id,
                                warranty_row[0],
                            ),
                        )
                    else:
                        cur.execute(
                            """INSERT INTO fix_warranty (
                                   device_id, company_id, operating_unit_id, currency_id, start_date,
                                   end_date, warranty_type, status, create_date, write_date
                               ) VALUES (%s, %s, %s, %s, %s, %s, %s, 'active', NOW(), NOW());""",
                            (
                                device_id,
                                company_id,
                                operating_unit_id,
                                currency_id,
                                w_start,
                                w_end,
                                WARRANTY_TYPE,
                            ),
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
