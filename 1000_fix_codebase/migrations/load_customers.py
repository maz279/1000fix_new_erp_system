#!/usr/bin/env python3
"""migrations/load_customers.py — ETL-1: Customer master loader.

Specification: docs/p04/migration-etl-specs.md (ETL-1) and MIG-06 residency routing.
Target models: res.partner, fix.party.role, fix.identity.document.
Classified storage: NID routed to Z4 via libs.py.fix_residency.
Legacy reference: CUST:WP_STORE:<id>
Company: the customer's branch (fix_branch.company_id) - a customer whose branch is
not on the target is rejected (counted and listed), never given "the first company".
M64: a phone already held by a DIFFERENT target partner is quarantined for steward
review - the loader never overwrites another partner's name or legacy reference.
"""

from __future__ import annotations

import json
import logging
import uuid
from pathlib import Path
from typing import Any

from libs.py.fix_residency import get_client as get_residency_client

logger = logging.getLogger(__name__)


class _Quarantine(Exception):
    """A record held back for data-steward review (not a load error)."""


def load_customers(extract_path: Path, db_conn) -> dict[str, Any]:
    """Load customers from extract with progressive dedup and Z4 residency routing."""
    data = json.loads(extract_path.read_text(encoding="utf-8"))
    loaded_count = 0
    rejected_count = 0
    rejections = []
    seen_phones: set[str] = set()

    residency = get_residency_client()

    with db_conn.cursor() as cur:
        branch_company: dict[str, int | None] = {}

        def resolve_company(branch_code: str) -> int | None:
            if branch_code not in branch_company:
                cur.execute("SELECT company_id FROM fix_branch WHERE code = %s;", (branch_code,))
                rows = cur.fetchall()
                branch_company[branch_code] = rows[0][0] if len(rows) == 1 else None
            return branch_company[branch_code]

        for item in data:
            name = item["name"]
            name_bn = item.get("name_bn", "")
            phone = item.get("phone", "").strip()
            email = item.get("email", "").strip().lower()
            is_company = item.get("is_company", False)
            nid = item.get("nid", "").strip()
            roles = item.get("roles", ["customer"])
            branch_code = item.get("branch_code")
            legacy_ref = item["legacy_reference"]

            # Dedup rule (ETL-1): Blocking on exact phone match
            if not phone:
                rejected_count += 1
                rejections.append(
                    {"legacy_reference": legacy_ref, "reason": "Missing required phone number"}
                )
                continue

            company_id = resolve_company(branch_code) if branch_code else None
            if company_id is None:
                rejected_count += 1
                rejections.append(
                    {
                        "legacy_reference": legacy_ref,
                        "branch_code": branch_code,
                        "reason": f"branch {branch_code!r} not found on target (fix_branch.code)",
                    }
                )
                continue

            if phone in seen_phones:
                # Duplicate phone within batch — quarantine / reject
                rejected_count += 1
                rejections.append(
                    {
                        "legacy_reference": legacy_ref,
                        "phone": phone,
                        "reason": "M64 dedup: exact phone match already seen in batch — quarantined for steward review",
                    }
                )
                continue
            seen_phones.add(phone)

            cur.execute("SAVEPOINT customer_sp;")
            try:
                # Re-run: the partner this legacy reference already created
                cur.execute(
                    "SELECT id FROM res_partner WHERE legacy_reference = %s;", (legacy_ref,)
                )
                existing = cur.fetchone()
                if not existing:
                    # M64 against the target: another partner already holds this phone
                    cur.execute(
                        "SELECT id, legacy_reference FROM res_partner WHERE phone = %s;", (phone,)
                    )
                    holder = cur.fetchone()
                    if holder:
                        raise _Quarantine(
                            f"M64 dedup: phone already held by target partner {holder[0]} "
                            f"({holder[1] or 'no legacy reference'}) - quarantined for steward review"
                        )
                if existing:
                    partner_id = existing[0]
                    cur.execute(
                        """UPDATE res_partner
                           SET name = %s, name_bn = %s, email = %s, is_company = %s,
                               preferred_language = 'bn', autopost_bills = 'ask',
                               legacy_reference = %s, active = true
                           WHERE id = %s;""",
                        (name, name_bn, email, is_company, legacy_ref, partner_id),
                    )
                else:
                    cur.execute(
                        """INSERT INTO res_partner (
                               name, name_bn, phone, email, is_company, preferred_language,
                               autopost_bills, company_id, legacy_reference, active,
                               create_date, write_date
                           ) VALUES (%s, %s, %s, %s, %s, 'bn', 'ask', %s, %s, true, NOW(), NOW())
                           RETURNING id;""",
                        (name, name_bn, phone, email, is_company, company_id, legacy_ref),
                    )
                    partner_id = cur.fetchone()[0]

                # Multi-role party mapping (fix.party.role)
                for role_code in roles:
                    cur.execute(
                        "SELECT id FROM fix_party_role WHERE partner_id = %s AND role_type = %s;",
                        (partner_id, role_code),
                    )
                    if not cur.fetchone():
                        cur.execute(
                            """INSERT INTO fix_party_role (
                                   partner_id, company_id, role_type, role_status,
                                   create_date, write_date
                               ) VALUES (%s, %s, %s, 'active', NOW(), NOW());""",
                            (partner_id, company_id, role_code),
                        )

                # MIG-06 Residency routing: NID is routed to Z4 via fix_residency
                if nid:
                    # Create identity document record with UUID reference (no raw NID in regional table)
                    doc_type = "nid_10" if len(nid) <= 10 else "nid_17"
                    cur.execute(
                        "SELECT id FROM fix_identity_document WHERE partner_id = %s AND document_type = %s;",
                        (partner_id, doc_type),
                    )
                    if not cur.fetchone():
                        # Store the classified value in Z4 only for a NEW document, so a
                        # re-run never leaves orphan Z4 keys behind (MG-007 idempotency)
                        residency_ref = str(uuid.uuid4())
                        residency.put(f"party identity:{residency_ref}", nid)
                        cur.execute(
                            """INSERT INTO fix_identity_document (
                                   partner_id, document_type, residency_ref, company_id,
                                   is_primary, active, create_date, write_date
                               ) VALUES (%s, %s, %s, %s, true, true, NOW(), NOW());""",
                            (partner_id, doc_type, residency_ref, company_id),
                        )

                cur.execute("RELEASE SAVEPOINT customer_sp;")
                loaded_count += 1
            except _Quarantine as q:
                cur.execute("ROLLBACK TO SAVEPOINT customer_sp;")
                rejected_count += 1
                rejections.append(
                    {"legacy_reference": legacy_ref, "phone": phone, "reason": str(q)}
                )
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
