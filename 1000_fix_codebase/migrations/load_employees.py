#!/usr/bin/env python3
"""migrations/load_employees.py — ETL-4: Employee master loader.

Specification: docs/p04/migration-etl-specs.md (ETL-4) and MIG-06 residency routing.
Target models: hr.employee, fix.party.role, fix_event_outbox (AS-08 JML events).
Classified storage: NID routed to Z4 via libs.py.fix_residency.
Legacy reference: EMP:PAYROLL_2026:<employee_code>
Company / operating unit: the employee's branch (fix_branch.company_id /
operating_unit_id). An employee whose branch or primary role is not on the target
is rejected (counted and listed) - never defaulted to HQ / R-01 / "the first
company", and a missing hire date stays empty (never invented).
"""

from __future__ import annotations

import json
import logging
import uuid
from pathlib import Path
from typing import Any

from libs.py.fix_residency import get_client as get_residency_client

logger = logging.getLogger(__name__)


def load_employees(extract_path: Path, db_conn) -> dict[str, Any]:
    """Load employees from extract with role resolution, Z4 residency, and JML events."""
    data = json.loads(extract_path.read_text(encoding="utf-8"))
    loaded_count = 0
    rejected_count = 0
    rejections = []

    residency = get_residency_client()

    with db_conn.cursor() as cur:
        for item in data:
            emp_code = item["employee_code"]
            name = item["name"]
            name_bn = item.get("name_bn", "")
            email = item.get("email", "")
            phone = item.get("phone", "")
            branch_code = item.get("branch_code")
            role_code = item.get("primary_role")
            nid = item.get("nid", "").strip()
            hire_date = item.get("hire_date") or None
            legacy_ref = item["legacy_reference"]

            # Branch -> company / operating unit; primary role from fix.role
            cur.execute(
                "SELECT id, company_id, operating_unit_id FROM fix_branch WHERE code = %s;",
                (branch_code,),
            )
            branch_rows = cur.fetchall()
            cur.execute("SELECT id FROM fix_role WHERE code = %s;", (role_code,))
            role_rows = cur.fetchall()
            reason = None
            if len(branch_rows) != 1:
                reason = f"branch {branch_code!r} not found on target (fix_branch.code)"
            elif len(role_rows) != 1:
                reason = f"primary role {role_code!r} not found on target (fix_role.code)"
            if reason:
                rejected_count += 1
                rejections.append({"legacy_reference": legacy_ref, "reason": reason})
                continue
            branch_id, company_id, operating_unit_id = branch_rows[0]
            role_id = role_rows[0][0]

            cur.execute("SAVEPOINT employee_sp;")
            try:
                # 1. Partner & Party Role for Employee (Multi-role design rule: employee is a party)
                cur.execute(
                    "SELECT id FROM res_partner WHERE legacy_reference = %s;",
                    (f"PARTNER:{legacy_ref}",),
                )
                partner_row = cur.fetchone()
                if not partner_row and email:
                    # the same person may already be a party (multi-role design rule)
                    cur.execute("SELECT id FROM res_partner WHERE email = %s;", (email,))
                    partner_row = cur.fetchone()
                if partner_row:
                    partner_id = partner_row[0]
                else:
                    cur.execute(
                        """INSERT INTO res_partner (
                               name, name_bn, email, phone, company_id, preferred_language,
                               autopost_bills, legacy_reference, active, create_date, write_date
                           ) VALUES (%s, %s, %s, %s, %s, 'bn', 'ask', %s, true, NOW(), NOW())
                           RETURNING id;""",
                        (name, name_bn, email, phone, company_id, f"PARTNER:{legacy_ref}"),
                    )
                    partner_id = cur.fetchone()[0]

                # fix.party.role
                cur.execute(
                    "SELECT id FROM fix_party_role WHERE partner_id = %s AND role_type = 'employee';",
                    (partner_id,),
                )
                party_role_row = cur.fetchone()
                if party_role_row:
                    party_role_id = party_role_row[0]
                else:
                    cur.execute(
                        """INSERT INTO fix_party_role (
                               partner_id, company_id, role_type, role_status,
                               create_date, write_date
                           ) VALUES (%s, %s, 'employee', 'active', NOW(), NOW())
                           RETURNING id;""",
                        (partner_id, company_id),
                    )
                    party_role_id = cur.fetchone()[0]

                # 2. Insert or update hr.employee (with its resource.resource)
                cur.execute(
                    "SELECT id, resource_id FROM hr_employee WHERE legacy_reference = %s OR employee_code = %s;",
                    (legacy_ref, emp_code),
                )
                existing_emp = cur.fetchone()
                if existing_emp:
                    emp_id, resource_id = existing_emp
                    # Re-run: keep the employee's resource, refresh it (no orphan rows)
                    cur.execute(
                        """UPDATE resource_resource
                           SET name = %s, tz = 'Asia/Dhaka', time_efficiency = 100.0,
                               active = true, write_date = NOW()
                           WHERE id = %s;""",
                        (name, resource_id),
                    )
                    cur.execute(
                        """UPDATE hr_employee
                           SET name = %s, name_bn = %s, work_email = %s, work_phone = %s,
                               branch_id = %s, company_id = %s, operating_unit_id = %s,
                               primary_role_id = %s, party_role_id = %s,
                               partner_id = %s, legacy_reference = %s, active = true
                           WHERE id = %s;""",
                        (
                            name,
                            name_bn,
                            email,
                            phone,
                            branch_id,
                            company_id,
                            operating_unit_id,
                            role_id,
                            party_role_id,
                            partner_id,
                            legacy_ref,
                            emp_id,
                        ),
                    )
                else:
                    # Resource record (resource.resource) required by hr.employee
                    cur.execute(
                        """INSERT INTO resource_resource (
                               name, resource_type, company_id, tz, time_efficiency, active,
                               create_date, write_date
                           ) VALUES (%s, 'user', %s, 'Asia/Dhaka', 100.0, true, NOW(), NOW())
                           RETURNING id;""",
                        (name, company_id),
                    )
                    resource_id = cur.fetchone()[0]
                    cur.execute(
                        """INSERT INTO hr_employee (
                               name, name_bn, employee_code, work_email, work_phone,
                               branch_id, primary_role_id, party_role_id, partner_id,
                               resource_id, company_id, operating_unit_id,
                               legacy_reference, active, create_date, write_date
                           ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, true, NOW(), NOW())
                           RETURNING id;""",
                        (
                            name,
                            name_bn,
                            emp_code,
                            email,
                            phone,
                            branch_id,
                            role_id,
                            party_role_id,
                            partner_id,
                            resource_id,
                            company_id,
                            operating_unit_id,
                            legacy_ref,
                        ),
                    )
                    emp_id = cur.fetchone()[0]

                # 3. MIG-06 Residency routing for Employee NID. The Z4 reference is kept
                # on the employee's party (fix.identity.document) so MG-007 rollback can
                # erase it, and a re-run never stores a second, orphan Z4 key.
                if nid:
                    doc_type = "nid_10" if len(nid) <= 10 else "nid_17"
                    cur.execute(
                        "SELECT id FROM fix_identity_document WHERE partner_id = %s AND document_type = %s;",
                        (partner_id, doc_type),
                    )
                    if not cur.fetchone():
                        residency_ref = str(uuid.uuid4())
                        residency.put(f"employee identity:{residency_ref}", nid)
                        cur.execute(
                            """INSERT INTO fix_identity_document (
                                   partner_id, document_type, residency_ref, company_id,
                                   is_primary, active, create_date, write_date
                               ) VALUES (%s, %s, %s, %s, true, true, NOW(), NOW());""",
                            (partner_id, doc_type, residency_ref, company_id),
                        )

                # 4. JML Event emission to fix_event_outbox (AS-08) - once per employee:
                # a re-run must not re-announce the joiner downstream
                cur.execute(
                    """SELECT 1 FROM fix_event_outbox
                       WHERE event_type = 'employee.imported' AND aggregate = 'hr.employee'
                         AND aggregate_id = %s LIMIT 1;""",
                    (str(emp_id),),
                )
                if not cur.fetchone():
                    event_payload = json.dumps(
                        {
                            "event": "employee.imported",
                            "employee_id": emp_id,
                            "employee_code": emp_code,
                            "name": name,
                            "primary_role": role_code,
                            "branch_code": branch_code,
                            "hire_date": hire_date,
                            "legacy_reference": legacy_ref,
                        }
                    )
                    event_uuid = str(uuid.uuid4())
                    cur.execute(
                        """INSERT INTO fix_event_outbox (
                               event_id, event_type, aggregate, aggregate_id, payload,
                               company_id, operating_unit_id, status, bus_target, publish_attempts,
                               create_date, write_date
                           ) VALUES (%s, 'employee.imported', 'hr.employee', %s, %s, %s, %s, 'pending', 'dual', 0, NOW(), NOW());""",
                        (event_uuid, str(emp_id), event_payload, company_id, operating_unit_id),
                    )

                cur.execute("RELEASE SAVEPOINT employee_sp;")
                loaded_count += 1
            except Exception as e:
                cur.execute("ROLLBACK TO SAVEPOINT employee_sp;")
                rejected_count += 1
                rejections.append({"legacy_reference": legacy_ref, "error": str(e)})

    db_conn.commit()
    return {
        "entity": "employees",
        "total_records": len(data),
        "loaded_count": loaded_count,
        "rejected_count": rejected_count,
        "rejections": rejections,
    }
