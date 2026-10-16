#!/usr/bin/env python3
"""migrations/extracts_generator.py — Generate Wave-1 Migration Source Extracts.

Conforms to docs/p04/migration-etl-specs.md (ETL-1..ETL-4) and
docs/p04/migration-mig-standards.md (MIG-01..MIG-08).
Emits extracts and control-totals.json with sha256 checksums.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

EXTRACTS_DIR = Path(__file__).resolve().parent / "extracts"


def compute_sha256(file_path: Path) -> str:
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def generate_branches() -> list[dict]:
    # Exactly 6 branches: 5 pilot service centres + Dhaka HQ (ETL-3)
    return [
        {
            "code": "HQ",
            "name": "Dhaka Central HQ & Service Hub",
            "name_bn": "ঢাকা প্রধান কার্যালয় ও সার্ভিস সেন্টার",
            "phone": "8801700000001",
            "email": "hq.service@1000fix.com",
            "operating_unit_code": "OU1",
            "legacy_reference": "BR:PILOT_2026:HQ",
        },
        {
            "code": "PC-01",
            "name": "Dhanmondi Service Centre",
            "name_bn": "ধানমন্ডি সার্ভিস সেন্টার",
            "phone": "8801700000002",
            "email": "dhanmondi@1000fix.com",
            "operating_unit_code": "OU1",
            "legacy_reference": "BR:PILOT_2026:PC01",
        },
        {
            "code": "PC-02",
            "name": "Uttara Service Centre",
            "name_bn": "উত্তরা সার্ভিস সেন্টার",
            "phone": "8801700000003",
            "email": "uttara@1000fix.com",
            "operating_unit_code": "OU1",
            "legacy_reference": "BR:PILOT_2026:PC02",
        },
        {
            "code": "PC-03",
            "name": "Mirpur Service Centre",
            "name_bn": "মিরপুর সার্ভিস সেন্টার",
            "phone": "8801700000004",
            "email": "mirpur@1000fix.com",
            "operating_unit_code": "OU1",
            "legacy_reference": "BR:PILOT_2026:PC03",
        },
        {
            "code": "PC-04",
            "name": "Chattogram Agrabad Service Centre",
            "name_bn": "চট্টগ্রাম আগ্রাবাদ সার্ভিস সেন্টার",
            "phone": "8801700000005",
            "email": "agrabad@1000fix.com",
            "operating_unit_code": "OU1",
            "legacy_reference": "BR:PILOT_2026:PC04",
        },
        {
            "code": "PC-05",
            "name": "Sylhet Zindabazar Service Centre",
            "name_bn": "সিলেট জিন্দাবাজার সার্ভিস সেন্টার",
            "phone": "8801700000006",
            "email": "sylhet@1000fix.com",
            "operating_unit_code": "OU1",
            "legacy_reference": "BR:PILOT_2026:PC05",
        },
    ]


def generate_customers() -> list[dict]:
    # 50 customers with progressive matching and classified NID fields (ETL-1)
    # Includes 1 exact duplicate phone test case for hard dedup rejection
    first_names = [
        ("Rahim", "রহিম"), ("Karim", "করিম"), ("Fatima", "ফাতিমা"), ("Ayesha", "আয়েশা"),
        ("Tanvir", "তানভীর"), ("Nusrat", "নুসরাত"), ("Kamal", "কামাল"), ("Salma", "সালমা"),
        ("Hasan", "হাসান"), ("Rina", "রিনা"), ("Mahmud", "মাহমুদ"), ("Shirin", "শিরীন"),
        ("Habib", "হাবিব"), ("Farhana", "ফারহানা"), ("Zahid", "জাহিদ"), ("Tasnim", "তাসনিম"),
        ("Ashik", "আশিক"), ("Sadia", "সাদিয়া"), ("Faisal", "ফয়সাল"), ("Nazma", "নাজমা"),
        ("Tariq", "তারিক"), ("Sabina", "সাবিনা"), ("Jamil", "জামিল"), ("Rubina", "রুবিনা"),
        ("Enamul", "এনামুল")
    ]
    last_names = [
        ("Ahmed", "আহমেদ"), ("Chowdhury", "চৌধুরী"), ("Hossain", "হোসেন"), ("Khan", "খান"),
        ("Rahman", "রহমান"), ("Islam", "ইসলাম"), ("Uddin", "উদ্দিন"), ("Sultana", "সুলতানা"),
        ("Begum", "বেগম"), ("Haque", "হক")
    ]
    branches = ["HQ", "PC-01", "PC-02", "PC-03", "PC-04", "PC-05"]

    customers = []
    for i in range(1, 51):
        fn_en, fn_bn = first_names[(i - 1) % len(first_names)]
        ln_en, ln_bn = last_names[(i - 1) % len(last_names)]
        name_en = f"{fn_en} {ln_en}"
        name_bn = f"{fn_bn} {ln_bn}"
        phone = f"880171{i:06d}"
        email = f"customer.{i:03d}@example.com"
        nid = f"1990{i:06d}123"
        branch = branches[(i - 1) % len(branches)]
        roles = ["customer"]
        if i % 5 == 0:
            roles.append("seller")
        is_company = (i % 10 == 0)

        # Test case: customer 50 has duplicate phone of customer 49 to test dedup rejection
        if i == 50:
            phone = "880171000049"  # Exact duplicate of customer 49
            name_en = "Rahim Duplicate Phone"
            name_bn = "রহিম ডুপ্লিকেট ফোন"

        customers.append({
            "source_id": f"WP-{1000 + i}",
            "name": name_en,
            "name_bn": name_bn,
            "phone": phone,
            "email": email,
            "is_company": is_company,
            "nid": nid,
            "roles": roles,
            "branch_code": branch,
            "legacy_reference": f"CUST:WP_STORE:{1000 + i}",
        })
    return customers


def generate_devices() -> list[dict]:
    # 50 devices with serial/IMEI uniqueness gate (ETL-2)
    # Includes 1 duplicate serial test case to test MDM review flagging
    device_models = [
        (6, "Reno 11", "Oppo", "mobile"),
        (7, "Narzo 70", "Realme", "mobile"),
        (8, "iPhone 13", "Apple", "mobile"),
        (9, "Redmi 13C", "Xiaomi", "mobile"),
        (10, "Galaxy S24", "Samsung", "mobile"),
    ]
    branches = ["HQ", "PC-01", "PC-02", "PC-03", "PC-04", "PC-05"]

    devices = []
    for i in range(1, 51):
        model_id, model_name, brand, dev_type = device_models[(i - 1) % len(device_models)]
        cust_id = 1000 + ((i - 1) % 49 + 1)  # point to valid customer 1..49
        serial = f"SN-{brand[:3].upper()}-{2026000 + i}"
        imei_1 = f"358901{i:09d}"
        imei_2 = f"358902{i:09d}"
        branch = branches[(i - 1) % len(branches)]

        # Duplicate serial edge case for device 50
        if i == 50:
            serial = "SN-APP-2026001"  # duplicate of device 1

        devices.append({
            "source_id": f"DEV-AST-{2000 + i}",
            "serial_number": serial,
            "imei_1": imei_1,
            "imei_2": imei_2,
            "device_model_id": model_id,
            "device_model_name": model_name,
            "brand_name": brand,
            "device_type": dev_type,
            "customer_legacy_ref": f"CUST:WP_STORE:{cust_id}",
            "branch_code": branch,
            "purchase_date": "2025-06-15",
            "warranty_start": "2025-06-15",
            "warranty_end": "2026-06-15",
            "legacy_reference": f"DEV:ASSET_SHEET:{serial}",
        })
    return devices


def generate_employees() -> list[dict]:
    # 20 employees with JML event emission and role mapping (ETL-4)
    roles = ["R-01", "R-14", "R-23", "R-08", "R-15", "R-19", "R-04", "R-27"]
    branches = ["HQ", "PC-01", "PC-02", "PC-03", "PC-04", "PC-05"]
    emp_names = [
        ("Shahidul Alam", "শহিদুল আলম"), ("Tahmina Begum", "তাহমিনা বেগম"),
        ("Monirul Islam", "মনিরুল ইসলাম"), ("Sharmin Akter", "শারমিন আক্তার"),
        ("Ariful Haque", "আরিফুল হক"), ("Khadija Khatun", "খাদিজা খাতুন"),
        ("Mustafizur Rahman", "মুস্তাফিজুর রহমান"), ("Shamima Nasrin", "শামীমা নাসরিন"),
        ("Golam Kibria", "গোলাম কিবরিয়া"), ("Ruksana Parveen", "রুকসানা পারভীন"),
        ("Imran Hossain", "ইমরান হোসেন"), ("Sabrina Yesmin", "সাবরিনা ইয়াসমিন"),
        ("Nazrul Islam", "নজরুল ইসলাম"), ("Farida Yasmin", "ফরিদা ইয়াসমিন"),
        ("Al Amin Sheikh", "আল আমিন শেখ"), ("Suraiya Akter", "সুরাইয়া আক্তার"),
        ("Mahbubur Rashid", "মাহবুবুর রশীদ"), ("Hasina Momtaz", "হাসিনা মমতাজ"),
        ("Delwar Hossain", "দেলোয়ার হোসেন"), ("Bilkis Banu", "বিলকিস বানু")
    ]

    employees = []
    for i in range(1, 21):
        name_en, name_bn = emp_names[i - 1]
        code = f"E-{i:04d}"
        role = roles[(i - 1) % len(roles)]
        branch = branches[(i - 1) % len(branches)]
        nid = f"1985{i:06d}789"
        email = f"employee.{i:03d}@1000fix.com"
        phone = f"880181{i:06d}"

        employees.append({
            "employee_code": code,
            "name": name_en,
            "name_bn": name_bn,
            "email": email,
            "phone": phone,
            "branch_code": branch,
            "primary_role": role,
            "nid": nid,
            "hire_date": "2024-01-15",
            "legacy_reference": f"EMP:PAYROLL_2026:{code}",
        })
    return employees


def main() -> None:
    EXTRACTS_DIR.mkdir(parents=True, exist_ok=True)

    branches = generate_branches()
    customers = generate_customers()
    devices = generate_devices()
    employees = generate_employees()

    b_path = EXTRACTS_DIR / "branches_extract.json"
    c_path = EXTRACTS_DIR / "customers_extract.json"
    d_path = EXTRACTS_DIR / "devices_extract.json"
    e_path = EXTRACTS_DIR / "employees_extract.json"

    b_path.write_text(json.dumps(branches, indent=2, ensure_ascii=False), encoding="utf-8")
    c_path.write_text(json.dumps(customers, indent=2, ensure_ascii=False), encoding="utf-8")
    d_path.write_text(json.dumps(devices, indent=2, ensure_ascii=False), encoding="utf-8")
    e_path.write_text(json.dumps(employees, indent=2, ensure_ascii=False), encoding="utf-8")

    checksums = {
        "branches": compute_sha256(b_path),
        "customers": compute_sha256(c_path),
        "devices": compute_sha256(d_path),
        "employees": compute_sha256(e_path),
    }

    manifest = {
        "run": "WAVE1_REHEARSAL_20261016",
        "extracted_at": datetime.now(timezone.utc).isoformat(),
        "control_totals": {
            "branches": len(branches),
            "customers": len(customers),
            "devices": len(devices),
            "employees": len(employees),
        },
        "checksums": checksums,
        "value_totals": {
            "branches": 0,
            "customers": 0,
            "devices": 0,
            "employees": 0,
        },
    }

    ctrl_path = EXTRACTS_DIR / "control-totals.json"
    ctrl_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Generated extracts in {EXTRACTS_DIR}:")
    print(f"  branches: {len(branches)} (sha256: {checksums['branches'][:12]}...)")
    print(f"  customers: {len(customers)} (sha256: {checksums['customers'][:12]}...)")
    print(f"  devices: {len(devices)} (sha256: {checksums['devices'][:12]}...)")
    print(f"  employees: {len(employees)} (sha256: {checksums['employees'][:12]}...)")
    print(f"Control totals written to: {ctrl_path}")


if __name__ == "__main__":
    main()
