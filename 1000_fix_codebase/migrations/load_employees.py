#!/usr/bin/env python3
"""migrations/load_employees.py — ETL-4: Employee master loader.

Specification: docs/p04/migration-etl-specs.md (ETL-4) and MIG-06 residency routing.
Target models: hr.employee, fix.party.role, fix_event_outbox (AS-08 JML events).
Classified storage: NID routed to Z4 via libs.py.fix_residency.
Legacy reference: EMP:PAYROLL_2026:<employee_code>
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
        # Default company and operating unit
        cur.execute("SELECT id FROM res_company LIMIT 1;")
        company_id = cur.fetchone()[0]
        cur.execute("SELECT id FROM operating_unit WHERE code = 'OU1' LIMIT 1;")
        ou_row = cur.fetchone()
        operating_unit_id = ou_row[0] if ou_row else 1

        for item in data:
            emp_code = item["employee_code"]
            name = item["name"]
            name_bn = item.get("name_bn", "")
            email = item.get("email", "")
            phone = item.get("phone", "")
            branch_code = item.get("branch_code", "HQ")
            role_code = item.get("primary_role", "R-01")
            nid = item.get("nid", "").strip()
            hire_date = item.get("hire_date", "2024-01-15")
            legacy_ref = item["legacy_reference"]

            # Resolve branch_id
            cur.execute("SELECT id FROM fix_branch WHERE code = %s LIMIT 1;", (branch_code,))
            branch_row = cur.fetchone()
            branch_id = branch_row[0] if branch_row else None

            # Resolve primary_role_id from fix.role
            cur.execute("SELECT id FROM fix_role WHERE code = %s LIMIT 1;", (role_code,))
            role_row = cur.fetchone()
            role_id = role_row[0] if role_row else None

            cur.execute("SAVEPOINT employee_sp;")
            try:
                # 1. Partner & Party Role for Employee (Multi-role design rule: employee is a party)
                cur.execute(
                    "SELECT id FROM res_partner WHERE email = %s OR legacy_reference = %s;",
                    (email, f"PARTNER:{legacy_ref}")
                )
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
                        (name, name_bn, email, phone, company_id, f"PARTNER:{legacy_ref}")
                    )
                    partner_id = cur.fetchone()[0]

                # fix.party.role
                cur.execute(
                    "SELECT id FROM fix_party_role WHERE partner_id = %s AND role_type = 'employee';",
                    (partner_id,)
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
                        (partner_id, company_id)
                    )
                    party_role_id = cur.fetchone()[0]

                # 2. Resource record (resource.resource) required by hr.employee
                cur.execute(
                    """INSERT INTO resource_resource (
                           name, resource_type, company_id, tz, time_efficiency, active, create_date, write_date
                       ) VALUES (%s, 'user', %s, 'Asia/Dhaka', 100.0, true, NOW(), NOW())
                       RETURNING id;""",
                    (name, company_id)
                )
                resource_id = cur.fetchone()[0]

                # 3. Insert or update hr.employee
                cur.execute(
                    "SELECT id FROM hr_employee WHERE legacy_reference = %s OR employee_code = %s;",
                    (legacy_ref, emp_code)
                )
                existing_emp = cur.fetchone()
                if existing_emp:
                    emp_id = existing_emp[0]
                    cur.execute(
                        """UPDATE hr_employee
                           SET name = %s, name_bn = %s, work_email = %s, work_phone = %s,
                               branch_id = %s, primary_role_id = %s, party_role_id = %s,
                               partner_id = %s, legacy_reference = %s, active = true
                           WHERE id = %s;""",
                        (name, name_bn, email, phone, branch_id, role_id,
                         party_role_id, partner_id, legacy_ref, emp_id)
                    )
                else:
                    cur.execute(
                        """INSERT INTO hr_employee (
                               name, name_bn, employee_code, work_email, work_phone,
                               branch_id, primary_role_id, party_role_id, partner_id,
                               resource_id, company_id, operating_unit_id,
                               legacy_reference, active, create_date, write_date
                           ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, true, NOW(), NOW())
                           RETURNING id;""",
                        (name, name_bn, emp_code, email, phone, branch_id, role_id,
                         party_role_id, partner_id, resource_id, company_id,
                         operating_unit_id, legacy_ref)
                    )
                    emp_id = cur.fetchone()[0]

                # 4. MIG-06 Residency routing for Employee NID
                if nid:
                    residency_ref = str(uuid.uuid4())
                    z4_key = f"employee identity:{residency_ref}"
                    residency.put(z4_key, nid)

                # 5. JML Event emission to fix_event_outbox (AS-08)
                event_payload = json.dumps({
                    "event": "employee.imported",
                    "employee_id": emp_id,
                    "employee_code": emp_code,
                    "name": name,
                    "primary_role": role_code,
                    "branch_code": branch_code,
                    "hire_date": hire_date,
                    "legacy_reference": legacy_ref,
                })
                event_uuid = str(uuid.uuid4())
                cur.execute(
                    """INSERT INTO fix_event_outbox (
                           event_id, event_type, aggregate, aggregate_id, payload,
                           company_id, operating_unit_id, status, publish_attempts,
                           create_date, write_date
                       ) VALUES (%s, 'employee.imported', 'hr.employee', %s, %s, %s, %s, 'pending', 0, NOW(), NOW());""",
                    (event_uuid, str(emp_id), event_payload, company_id, operating_unit_id)
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
