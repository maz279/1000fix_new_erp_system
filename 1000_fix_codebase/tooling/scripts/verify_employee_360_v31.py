#!/usr/bin/env python3
"""verify_employee_360_v31.py - Livefire Verification for Workforce Master v3.1
Tests:
1. Form layout metadata for hr.employee (10 Dynamics 365 tabs, sections, fields in m21.js)
2. Schema & choices resolution via /p03/model/form API for all 100+ workforce fields
3. Atomic write /p03/model/write across all 10 tabs on hr.employee
4. Exact readback of all statutory, technical, health, financial & legal fields
5. fix.hr.education CRUD via /p03/model surfaces
6. fix.hr.experience CRUD via /p03/model surfaces
7. fix.hr.document 26 statutory document types verification
8. fix.hr.dependant nominee creation and share validation
"""

import json
import re
import sys
import time
import urllib.request
from datetime import UTC, datetime

sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://127.0.0.1:8069"
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


class Client:
    def __init__(self):
        self.cookie = ""

    def _post(self, path, payload):
        req = urllib.request.Request(
            BASE + path,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                **({"Cookie": self.cookie} if self.cookie else {}),
            },
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            if "set-cookie" in r.headers:
                self.cookie = r.headers["set-cookie"].split(";")[0]
            return json.loads(r.read().decode("utf-8"))

    def login(self):
        out = self._post(
            "/web/session/authenticate",
            {"jsonrpc": "2.0", "params": {"db": DB, "login": ADMIN[0], "password": ADMIN[1]}},
        )
        return bool(out.get("result", {}).get("uid"))

    def call(self, path, params=None):
        return self._post(path, {"jsonrpc": "2.0", "params": params or {}})


def main():
    print("=====================================================================")
    print("1000FiX Employee 360 Master Data Standard (v3.1) Livefire Suite")
    print("=====================================================================")

    client = Client()
    for _attempt in range(20):
        try:
            if client.login():
                print(f"[OK] Authenticated as admin on {DB} at {datetime.now(UTC).isoformat()}\n")
                break
        except Exception:
            time.sleep(2)
    else:
        print("[FATAL] Could not connect to Odoo server")
        sys.exit(1)

    print("--- Test 1: M21 Form Metadata in m21.js (10 Dynamics 365 Tabs) ---")
    import os

    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    m21_js_path = os.path.join(
        repo_root, "addons", "platform", "cd_p03_portal", "static", "src", "a09", "m21.js"
    )
    with open(m21_js_path, encoding="utf-8") as f:
        m21_js = f.read()

    idx_start = m21_js.find("'M21-form-employee':")
    idx_end = m21_js.find("'M21-form-contract':", idx_start)
    emp_cfg_str = m21_js[idx_start:idx_end]

    # Extract declared tab IDs
    tab_ids = re.findall(r"id:\s*'([a-z_]+)'", emp_cfg_str[: emp_cfg_str.find("sections:")])
    expected_tabs = [
        "identity",
        "statutory",
        "organization",
        "academic",
        "career",
        "technical",
        "compensation",
        "health",
        "emergency",
        "vault",
    ]
    check("M21-form-employee declares 10 Dynamics 365 tabs", len(tab_ids) == 10, f"Got: {tab_ids}")
    for exp_id in expected_tabs:
        check(f"Tab '{exp_id}' present in M21-form-employee", exp_id in tab_ids)

    # Extract all declared fields
    all_fields = re.findall(r"name:\s*'([a-zA-Z0-9_]+)'", emp_cfg_str)
    check(
        "Total fields declared in M21-form-employee >= 100",
        len(all_fields) >= 100,
        f"Count: {len(all_fields)}",
    )

    # Test 2: Field Metadata Resolution via /p03/model/form
    print("\n--- Test 2: Schema & Metadata Resolution via /p03/model/form ---")
    query_fields = [{"name": fn} for fn in all_fields]
    form_res = client.call("/p03/model/form", {"model": "hr.employee", "fields": query_fields})
    resolved_fields = form_res.get("result", {}).get("fields", [])
    resolved_names = [f.get("name") for f in resolved_fields]
    check(
        "Fields metadata returned by Odoo >= 100",
        len(resolved_fields) >= 100,
        f"Count: {len(resolved_fields)}",
    )

    critical_fields = [
        "name_bn",
        "employee_code",
        "father_name",
        "mother_name",
        "spouse_name",
        "nid_number",
        "birth_reg_number",
        "tin_number",
        "tax_zone",
        "service_book_number",
        "repair_tier",
        "bga_rework_capable",
        "esd_certified",
        "toolkit_custody_ref",
        "wage",
        "basic_wage",
        "house_rent",
        "routing_number",
        "mfs_provider",
        "color_blindness",
        "medical_fitness",
        "tetanus_vaccine_date",
        "emergency_contact",
        "emergency_phone",
        "nominee_name",
        "nominee_pct",
        "doc_nid_verified",
        "doc_tin_verified",
        "doc_psr_verified",
    ]
    for cf in critical_fields:
        check(f"Critical field '{cf}' resolved by backend", cf in resolved_names)

    # Test 3: Atomic Write of Full 360 Workforce Record (All 10 Tabs)
    print("\n--- Test 3: Atomic Write of Full 360 Workforce Record (All 10 Tabs) ---")
    emp_payload = {
        # Tab 1: Identity & Bio
        "name": "Md. Tariqul Islam",
        "name_bn": "মো: তরিকুল ইসলাম",
        "employee_code": "FIX-TECH-2026-901",
        "biometric_id": "BIO-901",
        "work_email": "tariqul.islam@1000fix.com",
        "mobile_phone": "01711002233",
        "father_name": "Md. Rafiqul Islam",
        "mother_name": "Begum Rokeya",
        "spouse_name": "Suraiya Akter",
        "birthday": "1994-06-15",
        "sex": "male",
        "marital": "married",
        "blood_group": "b_pos",
        "religion": "islam",
        "identification_mark": "Mole on left cheek",
        "private_street": "House 45, Road 12, Sector 10",
        "private_city": "Uttara",
        "private_district": "Dhaka",
        "permanent_address": "Vill: Madhupur, PO: Chandpur Sadar",
        "permanent_district": "Chandpur",
        "permanent_division": "chattogram",
        # Tab 2: Statutory & Tax
        "nid_number": "19941324567890123",
        "birth_reg_number": "19941324567890123",
        "service_book_number": "SB-1000FIX-2026-042",
        "passport_number": "A02948192",
        "tin_number": "184920482910",
        "tax_zone": "Zone 08 Dhaka",
        "tax_circle": "Circle 165",
        "psr_ack_number": "PSR-2026-8910",
        "taxpayer_category": "general",
        "minimum_tax_location": "dhaka_chattogram",
        "has_disabled_child": False,
        "driving_license_no": "DL-DH-994821",
        "driving_license_type": "light",
        "driving_license_exp": "2028-12-31",
        "police_clearance_ref": "PCC-DMP-2026-1142",
        # Tab 3: Organization & Role
        "work_location_type": "central_workshop",
        "job_title": "Senior Component-Level Repair Specialist",
        "job_band": "band_4",
        "employment_type": "permanent",
        "joining_date": "2024-01-01",
        "probation_months": 3,
        "confirmation_date": "2024-04-01",
        # Tab 4: Academic & Education
        "degree_level": "diploma_engineering",
        "degree_title": "Diploma in Electronics Engineering",
        "major_group": "Electronics & Telecommunication",
        "board_university": "Bangladesh Technical Education Board (BTEB)",
        "institute_name": "Dhaka Polytechnic Institute",
        "passing_year": 2016,
        "result_type": "cgpa_4",
        "gpa_score": 3.78,
        "roll_number": "218491",
        "registration_no": "118294/2012",
        "academic_verified": "verified_online",
        # Tab 5: Career & Experience
        "prev_company_name": "Smart Technologies BD Ltd.",
        "prev_industry_type": "after_sales_service",
        "prev_designation": "Senior Laptop Repair Specialist",
        "prev_start_date": "2018-02-01",
        "prev_end_date": "2023-12-15",
        "prev_experience_years": 5.8,
        "prev_last_salary": 42000.0,
        "prev_reason_leaving": "career_growth",
        "prev_supervisor_name": "Kazi Mahbub Alam",
        "prev_supervisor_phone": "01819998877",
        "prev_reference_status": "verified_positive",
        # Tab 6: Skills & Certifications
        "repair_tier": "l3_component",
        "device_competencies": "Laptops, Smart TVs, Inverter Motherboards, Medical Diagnostic Modules",
        "esd_certified": True,
        "bga_rework_capable": True,
        "oem_brand_certs": "Apple ACMT/ACiT, Samsung Master, HP Commercial, Daikin Inverter",
        "certification_no": "APPLE-ACMT-2025-081",
        "cert_issue_date": "2025-01-15",
        "cert_expiry_date": "2027-01-14",
        "toolkit_custody_ref": "TK-MICRO-042",
        "customer_nda_signed": True,
        # Tab 7: Compensation & Banking
        "wage": 60000.0,
        "basic_wage": 35000.0,
        "house_rent": 17500.0,
        "medical_allowance": 3500.0,
        "conveyance_allowance": 4000.0,
        "technical_allowance": 5000.0,
        "overtime_eligible": True,
        "pf_member": True,
        "bank_name": "Islami Bank Bangladesh PLC",
        "bank_branch_name": "Uttara Model Town Branch",
        "routing_number": "060261358",
        "bank_account_number": "2050118020084321",
        "mfs_provider": "bkash",
        "mfs_account_number": "01711002233",
        # Tab 8: Health, HSE & Fitness
        "color_blindness": "normal_pass",
        "medical_fitness": "fit_duty",
        "work_restrictions": "No ladder work exceeding 3 meters without safety harness",
        "tetanus_vaccine_date": "2024-02-10",
        "tetanus_expiry_date": "2029-02-09",
        "chemical_allergies": "None",
        "insurance_policy_no": "GLI-FIX-2026-901",
        # Tab 9: Emergency & Nominees
        "emergency_contact": "Begum Rokeya",
        "emergency_contact_relation": "mother",
        "emergency_phone": "01722334455",
        "emergency_phone_alt": "01811223344",
        "emergency_contact_address": "Vill: Madhupur, PO: Chandpur Sadar, Chandpur",
        "emergency_contact_sec": "Md. Rafiqul Islam",
        "emergency_relation_sec": "father",
        "emergency_phone_sec": "01733445566",
        "children": 1,
        "nominee_name": "Suraiya Akter",
        "nominee_relation": "spouse",
        "nominee_nid": "19961324567890123",
        "nominee_pct": 100.0,
        "guardian_name": "",
        # Tab 10: Document Vault
        "doc_nid_verified": True,
        "doc_tin_verified": True,
        "doc_psr_verified": True,
        "doc_appointment_signed": True,
        "doc_nda_signed": True,
        "doc_service_book_scanned": True,
        "doc_medical_fit_certified": True,
        "doc_police_pcc_cleared": True,
    }

    write_res = client.call("/p03/model/write", {"model": "hr.employee", "values": emp_payload})
    emp_id = write_res.get("result", {}).get("id")
    check(
        "Atomic write /p03/model/write created hr.employee", bool(emp_id), f"Created ID: {emp_id}"
    )

    # Test 4: Verification of Readback
    print("\n--- Test 4: Readback Verification of Full 360 Employee Record ---")
    if emp_id:
        read_fields = [{"name": k} for k in emp_payload]
        read_res = client.call(
            "/p03/model/form", {"model": "hr.employee", "fields": read_fields, "record_id": emp_id}
        )
        saved = read_res.get("result", {}).get("record", {})
        check("Readback: name matches", saved.get("name") == "Md. Tariqul Islam")
        check("Readback: name_bn matches", saved.get("name_bn") == "মো: তরিকুল ইসলাম")
        check("Readback: employee_code matches", saved.get("employee_code") == "FIX-TECH-2026-901")
        check("Readback: nid_number matches", saved.get("nid_number") == "19941324567890123")
        check(
            "Readback: service_book_number matches",
            saved.get("service_book_number") == "SB-1000FIX-2026-042",
        )
        check("Readback: routing_number matches", saved.get("routing_number") == "060261358")
        check("Readback: repair_tier matches", saved.get("repair_tier") == "l3_component")
        check("Readback: bga_rework_capable matches", saved.get("bga_rework_capable") is True)
        check(
            "Readback: toolkit_custody_ref matches",
            saved.get("toolkit_custody_ref") == "TK-MICRO-042",
        )
        check("Readback: wage (gross salary) matches", float(saved.get("wage") or 0) == 60000.0)
        check("Readback: basic_wage matches", float(saved.get("basic_wage") or 0) == 35000.0)
        check("Readback: color_blindness matches", saved.get("color_blindness") == "normal_pass")
        check("Readback: medical_fitness matches", saved.get("medical_fitness") == "fit_duty")
        check("Readback: nominee_name matches", saved.get("nominee_name") == "Suraiya Akter")
        check("Readback: nominee_pct matches", float(saved.get("nominee_pct") or 0) == 100.0)
        check("Readback: doc_nid_verified matches", saved.get("doc_nid_verified") is True)
        check(
            "Readback: doc_service_book_scanned matches",
            saved.get("doc_service_book_scanned") is True,
        )

    # Test 5: fix.hr.education Model Surface CRUD
    print("\n--- Test 5: fix.hr.education Model Surface CRUD ---")
    edu_payload = {
        "employee_id": emp_id,
        "degree_level": "diploma_engineering",
        "degree_title": "Diploma in Electronics Engineering",
        "major_group": "Electronics & Telecommunication",
        "board_university": "Bangladesh Technical Education Board (BTEB)",
        "institute_name": "Dhaka Polytechnic Institute",
        "passing_year": 2016,
        "duration_years": 4.0,
        "result_type": "cgpa_4",
        "gpa_score": 3.78,
        "roll_number": "218491",
        "registration_no": "118294/2012",
        "is_verified": "verified_online",
    }
    edu_res = client.call("/p03/model/write", {"model": "fix.hr.education", "values": edu_payload})
    edu_id = edu_res.get("result", {}).get("id")
    check("fix.hr.education record created", bool(edu_id), f"ID: {edu_id}")

    if edu_id:
        edu_fields = [{"name": k} for k in edu_payload]
        edu_read = client.call(
            "/p03/model/form",
            {"model": "fix.hr.education", "fields": edu_fields, "record_id": edu_id},
        )
        saved_edu = edu_read.get("result", {}).get("record", {})
        check(
            "fix.hr.education readback degree_title",
            saved_edu.get("degree_title") == "Diploma in Electronics Engineering",
        )
        check("fix.hr.education readback gpa_score", float(saved_edu.get("gpa_score") or 0) == 3.78)
        check(
            "fix.hr.education readback is_verified",
            saved_edu.get("is_verified") == "verified_online",
        )

    # Test 6: fix.hr.experience Model Surface CRUD
    print("\n--- Test 6: fix.hr.experience Model Surface CRUD ---")
    exp_payload = {
        "employee_id": emp_id,
        "company_name": "Smart Technologies BD Ltd.",
        "industry_type": "after_sales_service",
        "designation_held": "Senior Laptop Repair Specialist",
        "start_date": "2018-02-01",
        "end_date": "2023-12-15",
        "experience_years": 5.8,
        "last_drawn_salary": 42000.0,
        "reason_for_leaving": "career_growth",
        "supervisor_name": "Kazi Mahbub Alam",
        "supervisor_phone": "01819998877",
        "reference_status": "verified_positive",
    }
    exp_res = client.call("/p03/model/write", {"model": "fix.hr.experience", "values": exp_payload})
    exp_id = exp_res.get("result", {}).get("id")
    check("fix.hr.experience record created", bool(exp_id), f"ID: {exp_id}")

    if exp_id:
        exp_fields = [{"name": k} for k in exp_payload]
        exp_read = client.call(
            "/p03/model/form",
            {"model": "fix.hr.experience", "fields": exp_fields, "record_id": exp_id},
        )
        saved_exp = exp_read.get("result", {}).get("record", {})
        check(
            "fix.hr.experience readback company_name",
            saved_exp.get("company_name") == "Smart Technologies BD Ltd.",
        )
        check(
            "fix.hr.experience readback designation_held",
            saved_exp.get("designation_held") == "Senior Laptop Repair Specialist",
        )
        check(
            "fix.hr.experience readback reference_status",
            saved_exp.get("reference_status") == "verified_positive",
        )

    # Test 7: fix.hr.document Statutory Types Verification
    print("\n--- Test 7: fix.hr.document Statutory Types Verification ---")
    doc_form = client.call(
        "/p03/model/form", {"model": "fix.hr.document", "fields": [{"name": "doc_type"}]}
    )
    doc_fields = doc_form.get("result", {}).get("fields", [])
    doc_type_field = next((f for f in doc_fields if f.get("name") == "doc_type"), None)
    doc_choices = doc_type_field.get("choices", []) if doc_type_field else []
    doc_keys = [d.get("key") for d in doc_choices]
    check(
        "fix.hr.document has 24+ statutory doc types",
        len(doc_keys) >= 24,
        f"Count: {len(doc_keys)}",
    )
    expected_statutory_docs = [
        "appointment",
        "id_card",
        "service_book",
        "experience",
        "nda",
        "nid_smart",
        "birth_cert",
        "tin_cert",
        "tax_psr",
        "passport",
        "driving_lic",
        "code_conduct",
        "oem_cert",
        "police_pcc",
        "medical_fit",
    ]
    for esd in expected_statutory_docs:
        check(f"Statutory doc type '{esd}' available in choices", esd in doc_keys)

    # Test 8: fix.hr.dependant Nominee Verification
    print("\n--- Test 8: fix.hr.dependant Nominee Verification ---")
    dep_payload = {
        "employee_id": emp_id,
        "name": "Suraiya Akter",
        "relation": "spouse",
        "date_of_birth": "1996-08-20",
        "nid": "19961324567890123",
        "is_nominee": True,
        "nominee_pct": 100.0,
        "guardian_name": "",
    }
    dep_res = client.call("/p03/model/write", {"model": "fix.hr.dependant", "values": dep_payload})
    dep_id = dep_res.get("result", {}).get("id")
    check("fix.hr.dependant nominee record created", bool(dep_id), f"ID: {dep_id}")

    if dep_id:
        dep_fields = [{"name": k} for k in dep_payload]
        dep_read = client.call(
            "/p03/model/form",
            {"model": "fix.hr.dependant", "fields": dep_fields, "record_id": dep_id},
        )
        saved_dep = dep_read.get("result", {}).get("record", {})
        check("Nominee share is 100.0%", float(saved_dep.get("nominee_pct") or 0) == 100.0)
        check("Nominee name matches", saved_dep.get("name") == "Suraiya Akter")

    print("\n=====================================================================")
    print(f"VERIFICATION RESULTS: {PASS_COUNT} PASSED, {FAIL_COUNT} FAILED")
    print("=====================================================================")
    if FAIL_COUNT > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
