"""Comprehensive Verification Suite for M21 Transfer & Promotion 8-Tab Dynamics 365 Standard.
Tests:
1. 8-Tab Form Structure & Language Purity (zero mixed Bengali in English labels).
2. Atomic multi-tab record write (/p03/model/write) covering all 60+ parameters.
3. Full readback and data integrity assertions (/p03/model/form).
4. Multi-tier workflow state transitions (recommend -> tech_eval -> hr_audit -> finance_approve -> approve -> clear_handover -> apply).
5. Automatic employee master (hr.employee) synchronization upon apply.
"""

import base64
import datetime
import sys

import requests

sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:8069"
DB = "fix_dev"
ADMIN = ("admin", "admin")

PASS_COUNT = 0
FAIL_COUNT = 0


def check(name: str, ok: bool, detail: str = ""):
    global PASS_COUNT, FAIL_COUNT
    if ok:
        PASS_COUNT += 1
        print(f"  [PASS] {name}" + (f" :: {detail}" if detail else ""))
    else:
        FAIL_COUNT += 1
        print(f"  [FAIL] {name} :: {detail}")


def main():
    print("=====================================================================")
    print("1000FiX Module M21 Transfer & Promotion Enterprise Suite (8-Tab D365)")
    print("=====================================================================")

    session = requests.Session()

    # 1. Authenticate
    auth_res = session.post(
        f"{BASE_URL}/web/session/authenticate",
        json={"jsonrpc": "2.0", "params": {"db": DB, "login": ADMIN[0], "password": ADMIN[1]}},
    )
    uid = auth_res.json().get("result", {}).get("uid")
    check("Authenticate as admin on fix_dev", bool(uid), f"UID: {uid}")

    # 2. Check Static Definition of M21-form-transfer in m21.js
    m21_js_path = r"c:\software_project\software_project_14\1000 fix\1000fix_new_erp_system\1000_fix_codebase\addons\platform\cd_p03_portal\static\src\a09\m21.js"
    with open(m21_js_path, encoding="utf-8") as f:
        m21_js_content = f.read()

    # Find M21-form-transfer in m21.js
    form_start = m21_js_content.find("'M21-form-transfer': {")
    form_end = m21_js_content.find("'M21-form-exit': {")
    assert form_start != -1 and form_end != -1, "M21-form-transfer block not found in m21.js"
    transfer_block = m21_js_content[form_start:form_end]

    expected_tabs = [
        "movement",
        "organization",
        "compensation",
        "technical",
        "handover",
        "logistics",
        "approval",
        "vault",
    ]
    for tid in expected_tabs:
        check(
            f"Dynamics 365 Tab '{tid}' defined in M21-form-transfer",
            f"id: '{tid}'" in transfer_block,
        )

    # Check for strict language integrity: No Bengali mixed in English labels
    import re

    labels = re.findall(r"label:\s*'([^']*)'", transfer_block)
    mixed_labels = []
    for lbl in labels:
        for ch in lbl:
            if "\u0980" <= ch <= "\u09ff":
                mixed_labels.append(lbl)
                break
    check(
        "Language Integrity: 100% pure English labels (no mixed Bengali)",
        len(mixed_labels) == 0,
        f"Found: {mixed_labels}",
    )

    # 3. Retrieve existing master records
    emp_list = (
        session.post(
            f"{BASE_URL}/p03/model/records",
            json={"jsonrpc": "2.0", "params": {"model": "hr.employee", "limit": 5}},
        )
        .json()
        .get("result", {})
        .get("rows", [])
    )
    check("Fetch employees from /p03/model/records", len(emp_list) > 0, f"Count: {len(emp_list)}")
    test_emp = emp_list[0]
    test_emp_id = test_emp["id"]

    branch_list = (
        session.post(
            f"{BASE_URL}/p03/model/records",
            json={"jsonrpc": "2.0", "params": {"model": "operating.unit", "limit": 10}},
        )
        .json()
        .get("result", {})
        .get("rows", [])
    )
    from_branch_id = branch_list[0]["id"] if len(branch_list) > 0 else 1
    to_branch_id = branch_list[1]["id"] if len(branch_list) > 1 else from_branch_id

    pos_list = (
        session.post(
            f"{BASE_URL}/p03/model/records",
            json={"jsonrpc": "2.0", "params": {"model": "fix.org.position", "limit": 10}},
        )
        .json()
        .get("result", {})
        .get("rows", [])
    )
    from_pos_id = pos_list[0]["id"] if len(pos_list) > 0 else 1
    to_pos_id = pos_list[1]["id"] if len(pos_list) > 1 else from_pos_id

    # 4. Create Full 8-Tab Movement Record
    print("\n--- Test Suite 1: Full 8-Tab Movement Write & Persistence ---")
    sample_pdf = b"%PDF-1.4\n1 0 obj\n<< /Title (1000FiX Movement Order Scan) >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"
    sample_b64 = base64.b64encode(sample_pdf).decode("ascii")
    today_str = datetime.date.today().isoformat()

    tr_vals = {
        # Tab 1: Scope
        "employee_id": test_emp_id,
        "movement_type": "promotion",
        "movement_category": "technical_promotion",
        "movement_nature": "permanent",
        "requisition_date": today_str,
        "release_date": today_str,
        "effective_date": today_str,
        "reason": "Promoted to L3 Senior Board Diagnostic Specialist and Posted to Agrabad Workshop Hub",
        # Tab 2: Org Realignment
        "from_operating_unit_id": from_branch_id,
        "to_operating_unit_id": to_branch_id,
        "from_position_id": from_pos_id,
        "to_position_id": to_pos_id,
        "from_job_title": "Junior Repair Technician",
        "to_job_title": "Senior Logic Board Repair Specialist",
        "from_grade_band": "L2",
        "to_grade_band": "L3",
        # Tab 3: Compensation
        "current_basic": 22000.0,
        "proposed_basic": 29000.0,
        "basic_increment_pct": 31.81,
        "current_gross": 38000.0,
        "proposed_gross": 52000.0,
        "proposed_house_rent": 14500.0,
        "proposed_medical": 2900.0,
        "proposed_conveyance": 3000.0,
        "proposed_skill_allowance": 2600.0,
        "to_tax_location": "dhaka_chittagong",
        "effective_payroll_month": "2026-11",
        # Tab 4: Technical & OEM Badges
        "from_repair_tier": "tier2_component",
        "to_repair_tier": "tier3_board",
        "oem_brand_authorizations": "Apple Authorized Technician, Samsung Care+ Master Level",
        "target_workbench_id": "AGR-WB-04",
        "esd_certified": True,
        "bga_license": True,
        "target_dispatch_zone": "Chittagong Central Commercial Hub",
        "technical_assessment_score": 94.5,
        "nda_confirmed": True,
        # Tab 5: Handover & Custody Clearance
        "open_jobs_audited": True,
        "open_jobs_transferred_count": 2,
        "open_jobs_reassignment_ref": "RMA-DOCKET-2026-9041",
        "toolkit_custody_ref": "TOOL-CUSTODY-8819",
        "toolkit_returned": True,
        "toolkit_challan_no": "CHL-TK-2026-0042",
        "spare_parts_reconciled": True,
        "spare_parts_variance_value": 0.0,
        "clearance_mrn_no": "MRN-2026-0812",
        "storekeeper_cleared": True,
        "imprest_cash_settled": True,
        # Tab 6: Relocation & Transit Leave
        "transfer_grant": 15000.0,
        "luggage_allowance": 8000.0,
        "travel_allowance": 4500.0,
        "transit_leave_days": 4,
        "transit_start_date": today_str,
        "transit_end_date": today_str,
        "shifting_vendor": "Bengal Movers Logistics Ltd.",
        "temporary_stay_provided": True,
        "destination_joining_date": today_str,
        # Tab 8: Scanned Vault Attachments
        "transfer_letter_file": sample_b64,
        "transfer_letter_filename": "Official_Transfer_Order_2026.pdf",
        "handover_challan_file": sample_b64,
        "handover_challan_filename": "Tool_Kit_Return_Challan_Agrabad.pdf",
        "clearance_mrn_file": sample_b64,
        "clearance_mrn_filename": "Spare_Parts_Clearance_MRN.pdf",
        "joining_report_file": sample_b64,
        "joining_report_filename": "Agrabad_Station_Joining_Report.pdf",
        "service_book_endorsement_file": sample_b64,
        "service_book_endorsement_filename": "Form7_Endorsement_Page_Scan.pdf",
        "contract_addendum_file": sample_b64,
        "contract_addendum_filename": "Employment_Contract_Addendum.pdf",
        "open_jobs_docket_file": sample_b64,
        "open_jobs_docket_filename": "RMA_Job_Reassignment_Docket.pdf",
    }

    write_res = session.post(
        f"{BASE_URL}/p03/model/write",
        json={
            "jsonrpc": "2.0",
            "params": {"model": "fix.hr.transfer", "record_id": None, "values": tr_vals},
        },
    ).json()
    transfer_id = write_res.get("result", {}).get("id")
    check(
        "Atomic write of 60+ parameters on fix.hr.transfer", bool(transfer_id), f"ID: {transfer_id}"
    )

    # 5. Readback and Verify Full Field Integrity
    read_fields = [
        {"name": k}
        for k in [
            "name",
            "employee_id",
            "movement_category",
            "movement_nature",
            "to_operating_unit_id",
            "to_position_id",
            "to_grade_band",
            "proposed_gross",
            "proposed_basic",
            "to_repair_tier",
            "oem_brand_authorizations",
            "esd_certified",
            "bga_license",
            "open_jobs_audited",
            "toolkit_returned",
            "storekeeper_cleared",
            "transit_leave_days",
            "transfer_letter_filename",
            "handover_challan_filename",
            "service_book_endorsement_filename",
            "state",
        ]
    ]
    read_res = (
        session.post(
            f"{BASE_URL}/p03/model/form",
            json={
                "jsonrpc": "2.0",
                "params": {
                    "model": "fix.hr.transfer",
                    "record_id": transfer_id,
                    "fields": read_fields,
                },
            },
        )
        .json()
        .get("result", {})
        .get("record", {})
    )

    check(
        "Readback: Movement Category matches",
        read_res.get("movement_category") == "technical_promotion",
    )
    check("Readback: Target Grade Band matches L3", read_res.get("to_grade_band") == "L3")
    check(
        "Readback: Assigned Repair Tier matches tier3_board",
        read_res.get("to_repair_tier") == "tier3_board",
    )
    check("Readback: Proposed Gross matches 52,000", read_res.get("proposed_gross") == 52000.0)
    check("Readback: Proposed Basic matches 29,000", read_res.get("proposed_basic") == 29000.0)
    check("Readback: Open jobs audited flag is True", read_res.get("open_jobs_audited") is True)
    check("Readback: Tool kit returned flag is True", read_res.get("toolkit_returned") is True)
    check(
        "Readback: Storekeeper clearance flag is True", read_res.get("storekeeper_cleared") is True
    )
    check("Readback: Paid transit leave days matches 4", read_res.get("transit_leave_days") == 4)
    check(
        "Readback: Transfer letter filename matches",
        read_res.get("transfer_letter_filename") == "Official_Transfer_Order_2026.pdf",
    )
    check(
        "Readback: Service book endorsement filename matches",
        read_res.get("service_book_endorsement_filename") == "Form7_Endorsement_Page_Scan.pdf",
    )

    # 6. Multi-Tier Workflow State Transitions
    print("\n--- Test Suite 2: Multi-Tier Workflow Authorization Actions ---")
    actions_to_test = [
        ("action_recommend", "recommended", "Recommending Origin Manager"),
        ("action_concur", "concurred", "Destination Manager Concurrence"),
        ("action_tech_eval", "tech_evaluated", "Technical Board Evaluation"),
        ("action_hr_audit", "hr_audited", "HR Compliance & Legal Audit"),
        ("action_finance_approve", "finance_approved", "Finance & Budget Clearance"),
        ("action_approve", "approved", "Executive Management Signoff"),
        ("action_clear_handover", "handover_cleared", "Storekeeper Handover Clearance"),
        ("action_apply", "applied", "Automated Employee Master Sync"),
    ]

    for act_method, expected_state, desc in actions_to_test:
        act_res = session.post(
            f"{BASE_URL}/p03/model/action",
            json={
                "jsonrpc": "2.0",
                "params": {
                    "model": "fix.hr.transfer",
                    "ids": [transfer_id],
                    "method": act_method,
                    "kwargs": {},
                },
            },
        ).json()
        is_ok = act_res.get("result", {}).get("success") is True

        # Verify state in DB
        state_check = (
            session.post(
                f"{BASE_URL}/p03/model/form",
                json={
                    "jsonrpc": "2.0",
                    "params": {
                        "model": "fix.hr.transfer",
                        "record_id": transfer_id,
                        "fields": [{"name": "state"}],
                    },
                },
            )
            .json()
            .get("result", {})
            .get("record", {})
            .get("state")
        )

        check(
            f"Workflow Action: {act_method} ({desc})",
            is_ok and state_check == expected_state,
            f"State: {state_check}",
        )

    # 7. Verify Auto-Synchronization to hr.employee Master
    print("\n--- Test Suite 3: Employee Master (hr.employee) Auto-Synchronization ---")
    emp_read = (
        session.post(
            f"{BASE_URL}/p03/model/form",
            json={
                "jsonrpc": "2.0",
                "params": {
                    "model": "hr.employee",
                    "record_id": test_emp_id,
                    "fields": [
                        {"name": "repair_tier"},
                        {"name": "job_band"},
                        {"name": "wage"},
                        {"name": "basic_wage"},
                        {"name": "operating_unit_id"},
                        {"name": "position_id"},
                    ],
                },
            },
        )
        .json()
        .get("result", {})
        .get("record", {})
    )

    def get_id(val):
        return val.get("id") if isinstance(val, dict) else val

    check(
        "Employee Master: repair_tier updated to l3_component",
        emp_read.get("repair_tier") == "l3_component",
        f"Actual: {emp_read.get('repair_tier')}",
    )
    check(
        "Employee Master: job_band updated to band_4 (Senior Tech L3)",
        emp_read.get("job_band") == "band_4",
        f"Actual: {emp_read.get('job_band')}",
    )
    check(
        "Employee Master: wage updated to 52,000",
        emp_read.get("wage") == 52000.0,
        f"Actual: {emp_read.get('wage')}",
    )
    check(
        "Employee Master: basic_wage updated to 29,000",
        emp_read.get("basic_wage") == 29000.0,
        f"Actual: {emp_read.get('basic_wage')}",
    )
    check(
        "Employee Master: operating_unit_id updated to destination branch",
        get_id(emp_read.get("operating_unit_id")) == to_branch_id,
        f"Actual: {emp_read.get('operating_unit_id')}",
    )
    check(
        "Employee Master: position_id updated to destination position",
        get_id(emp_read.get("position_id")) == to_pos_id,
        f"Actual: {emp_read.get('position_id')}",
    )

    print("\n=====================================================================")
    print(f"VERIFICATION SUMMARY: {PASS_COUNT} PASSED, {FAIL_COUNT} FAILED")
    print("=====================================================================")
    return FAIL_COUNT == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
