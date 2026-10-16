#!/usr/bin/env python3
"""seed-p02-technician-data.py — Seed diagnostic tree nodes, van stock parts and work orders for P02."""
import json

import psycopg2


def seed():
    conn = psycopg2.connect('dbname=fix_dev user=fix password=change-me-dev-only host=127.0.0.1 port=5433')
    cur = conn.cursor()

    print("--- 1. Seed Diagnostic Nodes ---")
    cur.execute("SELECT count(*) FROM fix_diagnostic_node")
    count = cur.fetchone()[0]
    if count == 0:
        # Diagnostic trees: 4 Root Categories with terminal fault codes
        trees = [
            # Root 1: Power
            {
                "code": "DIAG-PWR",
                "name": "ডিভাইস চালু হচ্ছে না (Device does not power on)",
                "children": [
                    {"code": "DIAG-PWR-BAT", "name": "ব্যাটারি ভোল্টেজ ৩.২V এর নিচে (Battery voltage < 3.2V)", "fault_code": "FAULT-BAT-DEAD", "action": "Replace battery cell assembly and test charging current."},
                    {"code": "DIAG-PWR-PMIC", "name": "চার্জিং আইসি অতিরিক্ত গরম (PMIC overheating)", "fault_code": "FAULT-PMIC-SHORT", "action": "Replace PMIC BGA chip and verify VDD rails."},
                    {"code": "DIAG-PWR-FUSE", "name": "ইনপুট ফিউজ বিচ্ছিন্ন (Blown protection fuse)", "fault_code": "FAULT-FUSE-OPEN", "action": "Replace SMD protection fuse and test reverse polarity diode."}
                ]
            },
            # Root 2: Display
            {
                "code": "DIAG-DISP",
                "name": "ডিসপ্লে কালো বা ফ্লিকার করছে (Display blank or flickering)",
                "children": [
                    {"code": "DIAG-DISP-FLEX", "name": "ডিসপ্লে রিবন ক্যাবল ঢিলা বা ক্ষতিগ্রস্ত (FPC flex damaged)", "fault_code": "FAULT-FPC-REPLACE", "action": "Reseat or replace display FPC ribbon connector."},
                    {"code": "DIAG-DISP-OLED", "name": "ডিসপ্লে গ্লাস ভাঙা / টাচ অচল (Cracked OLED / touch fail)", "fault_code": "FAULT-OLED-ASSEMBLY", "action": "Replace display module with genuine OEM assembly."}
                ]
            },
            # Root 3: Audio
            {
                "code": "DIAG-AUDIO",
                "name": "স্পিকার বা মাইকে শব্দ নেই (Speaker/Mic failure)",
                "children": [
                    {"code": "DIAG-AUDIO-MESH", "name": "স্পিকার জালে ধুলোবালি জমা (Acoustic mesh clogged)", "fault_code": "FAULT-MESH-CLEAN", "action": "Ultrasonic cleaning of acoustic mesh and chamber."},
                    {"code": "DIAG-AUDIO-COIL", "name": "স্পিকার ভয়েস কয়েল নষ্ট (Speaker voice coil open)", "fault_code": "FAULT-SPK-REPLACE", "action": "Replace dynamic loudspeaker transducer."}
                ]
            },
            # Root 4: Thermal
            {
                "code": "DIAG-THRM",
                "name": "ডিভাইস অতিরিক্ত গরম হচ্ছে (Device overheating)",
                "children": [
                    {"code": "DIAG-THRM-PASTE", "name": "থার্মাল পেস্ট শুকিয়ে গেছে (Thermal paste dried)", "fault_code": "FAULT-PASTE-DRY", "action": "Clean heatsink and apply high-conductivity thermal paste."},
                    {"code": "DIAG-THRM-FAN", "name": "কুলিং ফ্যান অচল বা জাম (Cooling fan seized)", "fault_code": "FAULT-FAN-SEIZED", "action": "Replace centrifugal cooling fan assembly."}
                ]
            }
        ]

        for tree in trees:
            cur.execute("""
                INSERT INTO fix_diagnostic_node (name, code, company_id, active, create_date, write_date, create_uid, write_uid)
                VALUES (%s, %s, 1, true, NOW(), NOW(), 1, 1)
                RETURNING id
            """, (tree["name"], tree["code"]))
            root_id = cur.fetchone()[0]

            for child in tree["children"]:
                cur.execute("""
                    INSERT INTO fix_diagnostic_node (name, code, parent_id, fault_code, recommended_action, company_id, active, create_date, write_date, create_uid, write_uid)
                    VALUES (%s, %s, %s, %s, %s, 1, true, NOW(), NOW(), 1, 1)
                """, (child["name"], child["code"], root_id, child["fault_code"], child["action"]))
        print("Inserted diagnostic decision trees successfully!")
    else:
        print(f"Diagnostic nodes already exist: {count}")

    print("\n--- 2. Ensure Sample Van Stock Parts with Barcodes ---")
    van_parts = [
        ("PART-BAT-S24", "Samsung Galaxy S24 Battery OEM", 2500.0, "8806091234567"),
        ("PART-DISP-A55", "Xiaomi Galaxy A55 Display Assembly", 4200.0, "8806092345678"),
        ("PART-FPC-IP15", "USB-C FPC Charging Ribbon Cable", 850.0, "8806093456789"),
        ("PART-SPK-GEN", "High-Fidelity Micro Loudspeaker", 650.0, "8806094567890"),
        ("PART-FAN-HP15", "HP Laptop Heatsink & Cooling Fan Module", 1800.0, "8806095678901"),
    ]
    for code, name, price, barcode in van_parts:
        cur.execute("SELECT id FROM product_template WHERE default_code = %s", (code,))
        row = cur.fetchone()
        if not row:
            name_json = json.dumps({"en_US": name, "bn_BD": name})
            cur.execute("""
                INSERT INTO product_template (name, default_code, list_price, type, service_tracking, active, uom_id, categ_id, company_id, create_date, write_date, create_uid, write_uid)
                VALUES (%s::jsonb, %s, %s, 'consu', 'no', true, 1, 2, 1, NOW(), NOW(), 1, 1)
                RETURNING id
            """, (name_json, code, price))
            tmpl_id = cur.fetchone()[0]
            cur.execute("""
                INSERT INTO product_product (product_tmpl_id, default_code, barcode, active, create_date, write_date, create_uid, write_uid)
                VALUES (%s, %s, %s, true, NOW(), NOW(), 1, 1)
                RETURNING id
            """, (tmpl_id, code, barcode))
            prod_id = cur.fetchone()[0]
            print(f"Created part {code} (ID {prod_id})")
        else:
            print(f"Part {code} already exists")

    print("\n--- 3. Ensure Assigned Work Orders for Abigail Peterson (Technician ID 6) ---")
    cur.execute("SELECT id, name, order_id, state FROM fix_work_order WHERE technician_id = 6")
    wos = cur.fetchall()
    print(f"Existing work orders for tech 6: {len(wos)}")
    if len(wos) < 3:
        cur.execute("SELECT id, name FROM fix_service_order WHERE id in (869, 871, 872, 873)")
        so_list = cur.fetchall()
        for so_id, so_name in so_list:
            cur.execute("SELECT id FROM fix_work_order WHERE order_id = %s", (so_id,))
            if not cur.fetchone():
                cur.execute("""
                    INSERT INTO fix_work_order (order_id, sequence, technician_id, state, company_id, create_date, write_date, create_uid, write_uid)
                    VALUES (%s, 10, 6, 'assigned', 1, NOW(), NOW(), 1, 1)
                    RETURNING id
                """, (so_id,))
                wo_id = cur.fetchone()[0]
                cur.execute("UPDATE fix_work_order SET name = %s WHERE id = %s", (f"{so_name}/W10", wo_id))
                cur.execute("UPDATE fix_service_order SET technician_id = 6 WHERE id = %s", (so_id,))
                print(f"Created work order {so_name}/W10 (ID {wo_id}) for Tech 6")

    conn.commit()
    conn.close()
    print("P02 Technician Data Seed Complete!")

if __name__ == "__main__":
    seed()
