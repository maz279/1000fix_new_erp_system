#!/usr/bin/env python3
"""verify_employee_document_uploads.py - Comprehensive Physical Document Verification Suite
Verifies:
1. Physical document file upload metadata on hr.employee Tab 10 vault
2. Physical file attachment and readback on hr.employee
3. Multi-tab D365 layout & physical document upload on fix.hr.document
4. Movement evidence & handover challan uploads on fix.hr.transfer
5. Academic certificate scan upload on fix.hr.education
6. Experience release letter upload on fix.hr.experience
7. Language purity verification: 0 mixed Bengali parenthetical labels in all A09 modules
"""

import base64
import os
import re
import sys

import requests

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


def main():
    print("=====================================================================")
    print("1000FiX Module M21 Physical Document Upload & Language Purity Suite")
    print("=====================================================================")

    # 1. Authenticate
    session = requests.Session()
    auth_res = session.post(
        f"{BASE}/web/session/authenticate",
        json={"jsonrpc": "2.0", "params": {"db": DB, "login": ADMIN[0], "password": ADMIN[1]}},
    )
    uid = auth_res.json().get("result", {}).get("uid")
    check("Authenticate as admin on fix_dev", bool(uid), f"UID: {uid}")

    sample_pdf = b"%PDF-1.4\n1 0 obj\n<< /Title (1000FiX Document Vault Evidence) >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"
    sample_b64 = base64.b64encode(sample_pdf).decode("ascii")

    # 2. Verify hr.employee Tab 10 vault uploads
    print("\n--- Test Suite 1: hr.employee Document Vault File Uploads ---")
    emp_vals = {
        "doc_nid_file": sample_b64,
        "doc_nid_filename": "Rahim_Smart_NID_Scanned.pdf",
        "doc_nid_verified": True,
        "doc_tin_file": sample_b64,
        "doc_tin_filename": "Rahim_TIN_Certificate.pdf",
        "doc_tin_verified": True,
        "doc_psr_file": sample_b64,
        "doc_psr_filename": "Tax_PSR_2025_2026.pdf",
        "doc_psr_verified": True,
        "doc_appointment_file": sample_b64,
        "doc_appointment_filename": "Appointment_Letter_Lead_Tech.pdf",
        "doc_appointment_signed": True,
        "doc_service_book_file": sample_b64,
        "doc_service_book_filename": "Form7_Service_Book_Scan.pdf",
        "doc_service_book_scanned": True,
        "doc_nda_file": sample_b64,
        "doc_nda_filename": "Confidentiality_NDA_Signed.pdf",
        "doc_nda_signed": True,
        "doc_medical_file": sample_b64,
        "doc_medical_filename": "Medical_Fitness_Cert.pdf",
        "doc_medical_fit_certified": True,
        "doc_police_pcc_file": sample_b64,
        "doc_police_pcc_filename": "DMP_Police_Clearance_PCC.pdf",
        "doc_police_pcc_cleared": True,
        "doc_academic_file": sample_b64,
        "doc_academic_filename": "BTEB_Diploma_Electronics.pdf",
        "doc_nominee_nid_file": sample_b64,
        "doc_nominee_nid_filename": "Nominee_NID_Card.pdf",
    }
    emp_res = session.post(
        f"{BASE}/p03/model/write",
        json={
            "jsonrpc": "2.0",
            "params": {"model": "hr.employee", "record_id": 1, "values": emp_vals},
        },
    ).json()
    check(
        "Atomic write of 10 physical document files on hr.employee",
        emp_res.get("result", {}).get("id") == 1,
    )

    # Readback verification
    read_fields = [
        {"name": k}
        for k in [
            "doc_nid_filename",
            "doc_tin_filename",
            "doc_psr_filename",
            "doc_appointment_filename",
            "doc_service_book_filename",
            "doc_nda_filename",
            "doc_medical_filename",
            "doc_police_pcc_filename",
            "doc_academic_filename",
            "doc_nominee_nid_filename",
            "doc_nid_verified",
            "doc_police_pcc_cleared",
        ]
    ]
    emp_read = (
        session.post(
            f"{BASE}/p03/model/form",
            json={
                "jsonrpc": "2.0",
                "params": {"model": "hr.employee", "record_id": 1, "fields": read_fields},
            },
        )
        .json()
        .get("result", {})
        .get("record", {})
    )

    check(
        "Readback: NID scanned file name matches",
        emp_read.get("doc_nid_filename") == "Rahim_Smart_NID_Scanned.pdf",
    )
    check(
        "Readback: TIN certificate file name matches",
        emp_read.get("doc_tin_filename") == "Rahim_TIN_Certificate.pdf",
    )
    check(
        "Readback: Tax PSR acknowledgement matches",
        emp_read.get("doc_psr_filename") == "Tax_PSR_2025_2026.pdf",
    )
    check(
        "Readback: Appointment letter scan matches",
        emp_read.get("doc_appointment_filename") == "Appointment_Letter_Lead_Tech.pdf",
    )
    check(
        "Readback: Form 7 service book scan matches",
        emp_read.get("doc_service_book_filename") == "Form7_Service_Book_Scan.pdf",
    )
    check(
        "Readback: NDA & Code of Conduct scan matches",
        emp_read.get("doc_nda_filename") == "Confidentiality_NDA_Signed.pdf",
    )
    check(
        "Readback: Medical fitness certificate matches",
        emp_read.get("doc_medical_filename") == "Medical_Fitness_Cert.pdf",
    )
    check(
        "Readback: Police clearance certificate matches",
        emp_read.get("doc_police_pcc_filename") == "DMP_Police_Clearance_PCC.pdf",
    )
    check(
        "Readback: Academic certificate file matches",
        emp_read.get("doc_academic_filename") == "BTEB_Diploma_Electronics.pdf",
    )
    check(
        "Readback: Nominee NID file matches",
        emp_read.get("doc_nominee_nid_filename") == "Nominee_NID_Card.pdf",
    )

    # 3. Verify fix.hr.document Physical Document Upload & Metadata
    print("\n--- Test Suite 2: fix.hr.document Physical File Upload ---")
    doc_vals = {
        "employee_id": 1,
        "doc_type": "service_book",
        "reference": "SB-DHK-2026-088",
        "file_data": sample_b64,
        "file_name": "Official_Service_Book_Form7.pdf",
        "file_size": len(sample_pdf),
        "file_mimetype": "application/pdf",
        "verified": True,
        "acknowledged": True,
        "notes": "Verified against original physical register by HR Manager.",
    }
    doc_res = session.post(
        f"{BASE}/p03/model/write",
        json={
            "jsonrpc": "2.0",
            "params": {"model": "fix.hr.document", "record_id": None, "values": doc_vals},
        },
    ).json()
    new_doc_id = doc_res.get("result", {}).get("id")
    check(
        "Create fix.hr.document with physical file attachment",
        bool(new_doc_id),
        f"ID: {new_doc_id}",
    )

    doc_read = (
        session.post(
            f"{BASE}/p03/model/form",
            json={
                "jsonrpc": "2.0",
                "params": {
                    "model": "fix.hr.document",
                    "record_id": new_doc_id,
                    "fields": [
                        {"name": "file_name"},
                        {"name": "file_size"},
                        {"name": "file_mimetype"},
                        {"name": "doc_type"},
                        {"name": "verified"},
                    ],
                },
            },
        )
        .json()
        .get("result", {})
        .get("record", {})
    )
    check(
        "Readback fix.hr.document filename",
        doc_read.get("file_name") == "Official_Service_Book_Form7.pdf",
    )
    check("Readback fix.hr.document filesize", doc_read.get("file_size") == len(sample_pdf))
    check("Readback fix.hr.document mimetype", doc_read.get("file_mimetype") == "application/pdf")
    check("Readback fix.hr.document classification", doc_read.get("doc_type") == "service_book")

    # 4. Verify fix.hr.transfer Movement Evidence & Handover Challans
    print("\n--- Test Suite 3: fix.hr.transfer Movement Evidence & Challans ---")
    tr_vals = {
        "employee_id": 1,
        "movement_type": "transfer",
        "reason": "Transfer to Dhanmondi Central Lab for Tier-4 Motherboard Rework",
        "transfer_letter_file": sample_b64,
        "transfer_letter_filename": "Transfer_Order_Dhanmondi_2026.pdf",
        "handover_challan_file": sample_b64,
        "handover_challan_filename": "Tool_Kit_Return_Challan_Agrabad.pdf",
        "clearance_mrn_file": sample_b64,
        "clearance_mrn_filename": "Inventory_Clearance_MRN_Scan.pdf",
        "joining_report_file": sample_b64,
        "joining_report_filename": "Dhanmondi_Station_Joining_Report.pdf",
    }
    tr_res = session.post(
        f"{BASE}/p03/model/write",
        json={
            "jsonrpc": "2.0",
            "params": {"model": "fix.hr.transfer", "record_id": None, "values": tr_vals},
        },
    ).json()
    new_tr_id = tr_res.get("result", {}).get("id")
    check(
        "Create fix.hr.transfer with 4 movement evidence files", bool(new_tr_id), f"ID: {new_tr_id}"
    )

    tr_read = (
        session.post(
            f"{BASE}/p03/model/form",
            json={
                "jsonrpc": "2.0",
                "params": {
                    "model": "fix.hr.transfer",
                    "record_id": new_tr_id,
                    "fields": [
                        {"name": "transfer_letter_filename"},
                        {"name": "handover_challan_filename"},
                        {"name": "clearance_mrn_filename"},
                        {"name": "joining_report_filename"},
                    ],
                },
            },
        )
        .json()
        .get("result", {})
        .get("record", {})
    )
    check(
        "Readback: Transfer order filename",
        tr_read.get("transfer_letter_filename") == "Transfer_Order_Dhanmondi_2026.pdf",
    )
    check(
        "Readback: Tool kit return challan filename",
        tr_read.get("handover_challan_filename") == "Tool_Kit_Return_Challan_Agrabad.pdf",
    )
    check(
        "Readback: Inventory clearance MRN scan filename",
        tr_read.get("clearance_mrn_filename") == "Inventory_Clearance_MRN_Scan.pdf",
    )
    check(
        "Readback: Station joining report filename",
        tr_read.get("joining_report_filename") == "Dhanmondi_Station_Joining_Report.pdf",
    )

    # 5. Verify fix.hr.education Certificate Upload
    print("\n--- Test Suite 4: fix.hr.education Academic Certificate Scan ---")
    edu_vals = {
        "employee_id": 1,
        "degree_level": "bachelors",
        "degree_title": "B.Sc in Electrical & Electronic Engineering",
        "major_group": "EEE",
        "board_university": "AUST",
        "passing_year": 2020,
        "gpa_score": 3.75,
        "certificate_file": sample_b64,
        "certificate_filename": "AUST_BSc_Degree_Certificate.pdf",
    }
    edu_res = session.post(
        f"{BASE}/p03/model/write",
        json={
            "jsonrpc": "2.0",
            "params": {"model": "fix.hr.education", "record_id": None, "values": edu_vals},
        },
    ).json()
    new_edu_id = edu_res.get("result", {}).get("id")
    check(
        "Create fix.hr.education with certificate file upload",
        bool(new_edu_id),
        f"ID: {new_edu_id}",
    )

    edu_read = (
        session.post(
            f"{BASE}/p03/model/form",
            json={
                "jsonrpc": "2.0",
                "params": {
                    "model": "fix.hr.education",
                    "record_id": new_edu_id,
                    "fields": [
                        {"name": "certificate_filename"},
                        {"name": "degree_title"},
                        {"name": "gpa_score"},
                    ],
                },
            },
        )
        .json()
        .get("result", {})
        .get("record", {})
    )
    check(
        "Readback: Degree certificate filename",
        edu_read.get("certificate_filename") == "AUST_BSc_Degree_Certificate.pdf",
    )

    # 6. Verify fix.hr.experience Experience Letter Upload
    print("\n--- Test Suite 5: fix.hr.experience Experience Letter Scan ---")
    exp_vals = {
        "employee_id": 1,
        "company_name": "Samsung Electronics Bangladesh Ltd",
        "industry_type": "after_sales_service",
        "designation_held": "Senior Motherboard Specialist",
        "start_date": "2020-01-01",
        "end_date": "2023-12-31",
        "experience_letter_file": sample_b64,
        "experience_letter_filename": "Samsung_Experience_Certificate.pdf",
    }
    exp_res = session.post(
        f"{BASE}/p03/model/write",
        json={
            "jsonrpc": "2.0",
            "params": {"model": "fix.hr.experience", "record_id": None, "values": exp_vals},
        },
    ).json()
    new_exp_id = exp_res.get("result", {}).get("id")
    check(
        "Create fix.hr.experience with release letter upload", bool(new_exp_id), f"ID: {new_exp_id}"
    )

    exp_read = (
        session.post(
            f"{BASE}/p03/model/form",
            json={
                "jsonrpc": "2.0",
                "params": {
                    "model": "fix.hr.experience",
                    "record_id": new_exp_id,
                    "fields": [{"name": "experience_letter_filename"}, {"name": "company_name"}],
                },
            },
        )
        .json()
        .get("result", {})
        .get("record", {})
    )
    check(
        "Readback: Experience certificate filename",
        exp_read.get("experience_letter_filename") == "Samsung_Experience_Certificate.pdf",
    )

    # 7. Language Purity Verification
    print("\n--- Test Suite 6: Language Purity (0 Mixed Bengali Parenthetical Labels) ---")
    a09_dir = r"C:\software_project\software_project_14\1000 fix\1000fix_new_erp_system\1000_fix_codebase\addons\platform\cd_p03_portal\static\src\a09"
    bangla_in_labels = 0
    checked_files = []
    for fname in os.listdir(a09_dir):
        if fname.endswith(".js"):
            checked_files.append(fname)
            with open(os.path.join(a09_dir, fname), encoding="utf-8") as f:
                content = f.read()
            matches = re.findall(r'label:\s*["\'][^"\']*[\u0980-\u09FF][^"\']*["\']', content)
            if matches:
                bangla_in_labels += len(matches)
                print(f"  [WARN] Found mixed labels in {fname}: {matches}")

    check(
        "Audited all A09 JS modules for language purity",
        len(checked_files) >= 7,
        f"Checked: {checked_files}",
    )
    check(
        "Zero mixed Bengali parenthetical labels across all A09 modules",
        bangla_in_labels == 0,
        f"Violations: {bangla_in_labels}",
    )

    print("\n=====================================================================")
    print(f"VERIFICATION RESULTS: {PASS_COUNT} PASSED, {FAIL_COUNT} FAILED")
    print("=====================================================================")
    if FAIL_COUNT > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
