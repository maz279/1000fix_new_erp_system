#!/usr/bin/env python3
"""migrations/load_customers.py — ETL-1: Customer master loader.

Specification: docs/p04/migration-etl-specs.md (ETL-1) and MIG-06 residency routing.
Target models: res.partner, fix.party.role, fix.identity.document.
Classified storage: NID routed to Z4 via libs.py.fix_residency.
Legacy reference: CUST:WP_STORE:<id>
"""
from __future__ import annotations

import json
import logging
import uuid
from pathlib import Path
from typing import Any

from libs.py.fix_residency import get_client as get_residency_client

logger = logging.getLogger(__name__)


def load_customers(extract_path: Path, db_conn) -> dict[str, Any]:
    """Load customers from extract with progressive dedup and Z4 residency routing."""
    data = json.loads(extract_path.read_text(encoding="utf-8"))
    loaded_count = 0
    rejected_count = 0
    rejections = []
    seen_phones: set[str] = set()

    residency = get_residency_client()

    with db_conn.cursor() as cur:
        # Get active company
        cur.execute("SELECT id FROM res_company LIMIT 1;")
        comp_row = cur.fetchone()
        company_id = comp_row[0] if comp_row else 1

        for item in data:
            name = item["name"]
            name_bn = item.get("name_bn", "")
            phone = item.get("phone", "").strip()
            email = item.get("email", "").strip().lower()
            is_company = item.get("is_company", False)
            nid = item.get("nid", "").strip()
            roles = item.get("roles", ["customer"])
            legacy_ref = item["legacy_reference"]

            # Dedup rule (ETL-1): Blocking on exact phone match
            if not phone:
                rejected_count += 1
                rejections.append({"legacy_reference": legacy_ref, "reason": "Missing required phone number"})
                continue

            if phone in seen_phones:
                # Duplicate phone within batch — quarantine / reject
                rejected_count += 1
                rejections.append({
                    "legacy_reference": legacy_ref,
                    "phone": phone,
                    "reason": "M64 dedup: exact phone match already seen in batch — quarantined for steward review"
                })
                continue
            seen_phones.add(phone)

            cur.execute("SAVEPOINT customer_sp;")
            try:
                # Check if partner already exists by legacy_reference or phone
                cur.execute(
                    "SELECT id FROM res_partner WHERE legacy_reference = %s OR phone = %s;",
                    (legacy_ref, phone)
                )
                existing = cur.fetchone()
                if existing:
                    partner_id = existing[0]
                    cur.execute(
                        """UPDATE res_partner
                           SET name = %s, name_bn = %s, email = %s, is_company = %s,
                               preferred_language = 'bn', autopost_bills = 'ask',
                               legacy_reference = %s, active = true
                           WHERE id = %s;""",
                        (name, name_bn, email, is_company, legacy_ref, partner_id)
                    )
                else:
                    cur.execute(
                        """INSERT INTO res_partner (
                               name, name_bn, phone, email, is_company, preferred_language,
                               autopost_bills, company_id, legacy_reference, active,
                               create_date, write_date
                           ) VALUES (%s, %s, %s, %s, %s, 'bn', 'ask', %s, %s, true, NOW(), NOW())
                           RETURNING id;""",
                        (name, name_bn, phone, email, is_company, company_id, legacy_ref)
                    )
                    partner_id = cur.fetchone()[0]

                # Multi-role party mapping (fix.party.role)
                for role_code in roles:
                    cur.execute(
                        "SELECT id FROM fix_party_role WHERE partner_id = %s AND role_type = %s;",
                        (partner_id, role_code)
                    )
                    if not cur.fetchone():
                        cur.execute(
                            """INSERT INTO fix_party_role (
                                   partner_id, company_id, role_type, role_status,
                                   create_date, write_date
                               ) VALUES (%s, %s, %s, 'active', NOW(), NOW());""",
                            (partner_id, company_id, role_code)
                        )

                # MIG-06 Residency routing: NID is routed to Z4 via fix_residency
                if nid:
                    residency_ref = str(uuid.uuid4())
                    z4_key = f"party identity:{residency_ref}"
                    # Store classified value in Z4
                    residency.put(z4_key, nid)

                    # Create identity document record with UUID reference (no raw NID in regional table)
                    doc_type = "nid_10" if len(nid) <= 10 else "nid_17"
                    cur.execute(
                        "SELECT id FROM fix_identity_document WHERE partner_id = %s AND document_type = %s;",
                        (partner_id, doc_type)
                    )
                    if not cur.fetchone():
                        cur.execute(
                            """INSERT INTO fix_identity_document (
                                   partner_id, document_type, residency_ref, company_id,
                                   is_primary, active, create_date, write_date
                               ) VALUES (%s, %s, %s, %s, true, true, NOW(), NOW());""",
                            (partner_id, doc_type, residency_ref, company_id)
                        )

                cur.execute("RELEASE SAVEPOINT customer_sp;")
                loaded_count += 1
            except Exception as e:
                cur.execute("ROLLBACK TO SAVEPOINT customer_sp;")
                rejected_count += 1
                rejections.append({"legacy_reference": legacy_ref, "error": str(e)})

    db_conn.commit()
    return {
        "entity": "customers",
        "total_records": len(data),
        "loaded_count": loaded_count,
        "rejected_count": rejected_count,
        "rejections": rejections,
    }
