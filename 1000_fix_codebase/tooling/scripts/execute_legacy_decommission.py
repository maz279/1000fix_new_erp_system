#!/usr/bin/env python3
"""
execute_legacy_decommission.py — 48-Source Legacy Decommission Register (measure-only)
Milestone: R11-M02-T03 (Legacy decommissioning)
Standards: RL-006 (DCM-01..DCM-57), DA-006, NIST SP 800-88r2, IEEE 2883:2022, ISO/IEC 27001:2022 A.8.10

MEASURE-ONLY: despite its historical name this tool executes nothing. It never connects to
a legacy system, stops a host, wipes media, revokes a credential or deletes data. It reads
the T01 / T04 evidence, scans this codebase read-only and writes the register.

SOURCES_DATA below is the DECLARED retirement plan (disposition R/K/P/N, PII flag, wave,
planned sanitisation technique, declared annual run cost). Per source, the D-ladder state
is DERIVED from checks measured in this run - never declared:
- R (retire):  MIG-08 reconciliation sign-off (T01 evidence), restorable archive (T04
  evidence), negative connection test, DPO countersign (PII sources).
- P (purge):   MIG-08 sign-off (T01), purge verification, DPO countersign.
- K (retain):  annual retention review, DPO countersign (PII sources).
- N (non-system): capture / feed conversion / credential rotation evidence.
A negative connection test would have to reach the legacy host - outside this workstation
(DE-11: the local environment never reaches non-local endpoints) - and purge / rotation /
review / countersign evidence are human or production acts: each is UNMEASURED with its
reason. Upstream evidence counts only when its status is exactly PASS.
Estate checks: register completeness (48 distinct SRC-01..SRC-48, valid dispositions),
agreement of each source's name with the T01 reconciliation register, and a read-only scan
of the codebase for configuration still pointing at a retired legacy endpoint. The estate
shadow-system scan (branch endpoints) cannot be run from here -> UNMEASURED.
Run order: generate_r11_m02_reconciliations.py and verify_archive_integrity.py first.

Verdict: FAIL if any check failed, INCOMPLETE if any is UNMEASURED, else PASS.
Exit 0 PASS / 1 FAIL / 2 INCOMPLETE. Writes only the evidence JSON and its Markdown record.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = REPO_ROOT / "docs" / "traceability" / "evidence"
DOCS_DIR = REPO_ROOT / "docs" / "traceability"
EVIDENCE_NAME = "r11-m02-decommission-register.json"
MD_NAME = "r11-m02-decommission-records.md"
T01_EVIDENCE = "r11-m02-legacy-48-reconciliations.json"
T04_EVIDENCE = "r11-m02-archive-register.json"

PASS, FAIL, UNMEASURED = "PASS", "FAIL", "UNMEASURED"
INCOMPLETE = "INCOMPLETE"
VALID_DISPOSITIONS = ("R", "K", "P", "N")

# Retired legacy endpoints (declared in SOURCES_DATA) that no live configuration may still
# reference after retirement (RL-006 DCM-10).
RETIRED_ENDPOINTS = {"SRC-01": "station.1000fix.com", "SRC-02": "123.0.26.238"}
SCAN_ROOTS = ("addons", "services", "libs", "apps", "infra", "dags", "migrations", "contracts")
SCAN_SKIP_DIRS = frozenset(
    {
        "node_modules",
        "vendor",
        ".git",
        "__pycache__",
        ".venv",
        "build",
        "dist",
        ".next",
        ".dart_tool",
        "odoo-data",
        "htmlcov",
    }
)
SCAN_SUFFIXES = frozenset(
    {
        ".py",
        ".xml",
        ".yaml",
        ".yml",
        ".conf",
        ".cfg",
        ".ini",
        ".toml",
        ".json",
        ".env",
        ".sh",
        ".ps1",
        ".sql",
        ".js",
        ".ts",
        ".tsx",
        ".dart",
        ".properties",
        ".tf",
    }
)
SCAN_MAX_BYTES = 2 * 1024 * 1024

NEGATIVE_TEST_REASON = (
    "a negative connection test must reach the legacy host, which this workstation may not "
    "do (DE-11: the local environment never reaches non-local endpoints)"
)
PURGE_REASON = (
    "purge / media-destruction verification happens on the legacy estate and its certificate "
    "is not observable by this tool"
)
DPO_REASON = "a DPO countersign is a human act; no countersign is observable by this tool"
RETENTION_REVIEW_REASON = (
    "the annual retention review is a contractual / human act; no review record is "
    "observable by this tool"
)
TRANSITION_REASON = (
    "capture into an SOP, conversion to a reference feed or credential rotation in Vault "
    "is not observable from this workstation"
)
SHADOW_SCAN_REASON = (
    "the estate shadow-system scan runs against branch endpoints and the network, which this "
    "workstation cannot reach (DE-11)"
)

# Master 48 Sources with full RL-006 metadata (DECLARED plan)
SOURCES_DATA = [
    # 1. Live Trackers (2 sources - DB)
    {
        "id": "SRC-01",
        "name": "station.1000fix.com",
        "custodian": "CTO (Shafiul Alam)",
        "class": "DB",
        "disp": "R",
        "pii": True,
        "wave": "W2",
        "rfp": "Legacy web tracking portal",
        "retention": "RC-04 (Service Orders, 5 yr)",
        "cost": 180000,
        "sanit": "IEEE 2883 Cryptographic Erase + Host Terminate",
    },
    {
        "id": "SRC-02",
        "name": "123.0.26.238/orderTracking",
        "custodian": "CTO (Shafiul Alam)",
        "class": "DB",
        "disp": "R",
        "pii": True,
        "wave": "W2",
        "rfp": "Legacy SQL order tracking",
        "retention": "RC-04 (Service Orders, 5 yr)",
        "cost": 140000,
        "sanit": "IEEE 2883 Purge + VM Destroy",
    },
    # 2. Branch Service-Order Spreadsheets (24 sources - SS)
    {
        "id": "SRC-03",
        "name": "Tejgaon Central Hub Orders",
        "custodian": "Branch Ops Lead (Tariqul Islam)",
        "class": "SS",
        "disp": "R",
        "pii": True,
        "wave": "W2",
        "rfp": "Branch service spreadsheets",
        "retention": "RC-04 (Service Orders, 5 yr)",
        "cost": 25000,
        "sanit": "NIST 800-88 Clear + Share Deprovision",
    },
    {
        "id": "SRC-04",
        "name": "Dhanmondi Service Center",
        "custodian": "Branch Ops Lead (Tariqul Islam)",
        "class": "SS",
        "disp": "R",
        "pii": True,
        "wave": "W3",
        "rfp": "Branch service spreadsheets",
        "retention": "RC-04 (Service Orders, 5 yr)",
        "cost": 25000,
        "sanit": "NIST 800-88 Clear + Share Deprovision",
    },
    {
        "id": "SRC-05",
        "name": "Mirpur-10 Service Center",
        "custodian": "Branch Ops Lead (Tariqul Islam)",
        "class": "SS",
        "disp": "R",
        "pii": True,
        "wave": "W2",
        "rfp": "Branch service spreadsheets",
        "retention": "RC-04 (Service Orders, 5 yr)",
        "cost": 25000,
        "sanit": "NIST 800-88 Clear + Share Deprovision",
    },
    {
        "id": "SRC-06",
        "name": "Uttara Sector-3 Center",
        "custodian": "Branch Ops Lead (Tariqul Islam)",
        "class": "SS",
        "disp": "R",
        "pii": True,
        "wave": "W2",
        "rfp": "Branch service spreadsheets",
        "retention": "RC-04 (Service Orders, 5 yr)",
        "cost": 25000,
        "sanit": "NIST 800-88 Clear + Share Deprovision",
    },
    {
        "id": "SRC-07",
        "name": "Motijheel Commercial Branch",
        "custodian": "Branch Ops Lead (Tariqul Islam)",
        "class": "SS",
        "disp": "R",
        "pii": True,
        "wave": "W2",
        "rfp": "Branch service spreadsheets",
        "retention": "RC-04 (Service Orders, 5 yr)",
        "cost": 25000,
        "sanit": "NIST 800-88 Clear + Share Deprovision",
    },
    {
        "id": "SRC-08",
        "name": "Banani Luxury Care Point",
        "custodian": "Branch Ops Lead (Tariqul Islam)",
        "class": "SS",
        "disp": "R",
        "pii": True,
        "wave": "W2",
        "rfp": "Branch service spreadsheets",
        "retention": "RC-04 (Service Orders, 5 yr)",
        "cost": 25000,
        "sanit": "NIST 800-88 Clear + Share Deprovision",
    },
    {
        "id": "SRC-09",
        "name": "Chittagong Agrabad Center",
        "custodian": "Regional Ops Head (Nasir Uddin)",
        "class": "SS",
        "disp": "R",
        "pii": True,
        "wave": "W2",
        "rfp": "Branch service spreadsheets",
        "retention": "RC-04 (Service Orders, 5 yr)",
        "cost": 30000,
        "sanit": "NIST 800-88 Clear + Share Deprovision",
    },
    {
        "id": "SRC-10",
        "name": "Chittagong GEC Circle Center",
        "custodian": "Regional Ops Head (Nasir Uddin)",
        "class": "SS",
        "disp": "R",
        "pii": True,
        "wave": "W4",
        "rfp": "Branch service spreadsheets",
        "retention": "RC-04 (Service Orders, 5 yr)",
        "cost": 25000,
        "sanit": "NIST 800-88 Clear + Share Deprovision",
    },
    {
        "id": "SRC-11",
        "name": "Sylhet Zindabazar Branch",
        "custodian": "Regional Ops Head (Nasir Uddin)",
        "class": "SS",
        "disp": "R",
        "pii": True,
        "wave": "W3",
        "rfp": "no contractual accountability",
        "retention": "RC-04 (Service Orders, 5 yr)",
        "cost": 20000,
        "sanit": "NIST 800-88 Clear + Share Deprovision",
    },
    {
        "id": "SRC-12",
        "name": "Rajshahi Alokar More Branch",
        "custodian": "Regional Ops Head (Nasir Uddin)",
        "class": "SS",
        "disp": "R",
        "pii": True,
        "wave": "W3",
        "rfp": "no contractual accountability",
        "retention": "RC-04 (Service Orders, 5 yr)",
        "cost": 20000,
        "sanit": "NIST 800-88 Clear + Share Deprovision",
    },
    {
        "id": "SRC-13",
        "name": "Khulna KDA Avenue Branch",
        "custodian": "Regional Ops Head (Nasir Uddin)",
        "class": "SS",
        "disp": "R",
        "pii": True,
        "wave": "W5",
        "rfp": "Branch service spreadsheets",
        "retention": "RC-04 (Service Orders, 5 yr)",
        "cost": 20000,
        "sanit": "NIST 800-88 Clear + Share Deprovision",
    },
    {
        "id": "SRC-14",
        "name": "Barisal Sadar Road Branch",
        "custodian": "Regional Ops Head (Nasir Uddin)",
        "class": "SS",
        "disp": "R",
        "pii": True,
        "wave": "W5",
        "rfp": "Branch service spreadsheets",
        "retention": "RC-04 (Service Orders, 5 yr)",
        "cost": 15000,
        "sanit": "NIST 800-88 Clear + Share Deprovision",
    },
    {
        "id": "SRC-15",
        "name": "Rangpur Station Road Branch",
        "custodian": "Regional Ops Head (Nasir Uddin)",
        "class": "SS",
        "disp": "R",
        "pii": True,
        "wave": "W5",
        "rfp": "Branch service spreadsheets",
        "retention": "RC-04 (Service Orders, 5 yr)",
        "cost": 15000,
        "sanit": "NIST 800-88 Clear + Share Deprovision",
    },
    {
        "id": "SRC-16",
        "name": "Bogra Satmatha Branch",
        "custodian": "Regional Ops Head (Nasir Uddin)",
        "class": "SS",
        "disp": "R",
        "pii": True,
        "wave": "W3",
        "rfp": "Branch service spreadsheets",
        "retention": "RC-04 (Service Orders, 5 yr)",
        "cost": 15000,
        "sanit": "NIST 800-88 Clear + Share Deprovision",
    },
    {
        "id": "SRC-17",
        "name": "Comilla Kandirpar Branch",
        "custodian": "Regional Ops Head (Nasir Uddin)",
        "class": "SS",
        "disp": "R",
        "pii": True,
        "wave": "W5",
        "rfp": "no contractual accountability",
        "retention": "RC-04 (Service Orders, 5 yr)",
        "cost": 15000,
        "sanit": "NIST 800-88 Clear + Share Deprovision",
    },
    {
        "id": "SRC-18",
        "name": "Mymensingh Town Hall Branch",
        "custodian": "Regional Ops Head (Nasir Uddin)",
        "class": "SS",
        "disp": "R",
        "pii": True,
        "wave": "W3",
        "rfp": "no contractual accountability",
        "retention": "RC-04 (Service Orders, 5 yr)",
        "cost": 15000,
        "sanit": "NIST 800-88 Clear + Share Deprovision",
    },
    {
        "id": "SRC-19",
        "name": "Gazipur Chowrasta Point",
        "custodian": "Branch Ops Lead (Tariqul Islam)",
        "class": "SS",
        "disp": "R",
        "pii": True,
        "wave": "W4",
        "rfp": "Branch service spreadsheets",
        "retention": "RC-04 (Service Orders, 5 yr)",
        "cost": 20000,
        "sanit": "NIST 800-88 Clear + Share Deprovision",
    },
    {
        "id": "SRC-20",
        "name": "Narayanganj Chasara Point (bKash/Nagad Integration)",
        "custodian": "CFO (Mustafizur Rahman)",
        "class": "PORTAL",
        "disp": "K",
        "pii": False,
        "wave": "n/a",
        "rfp": "Payment counterparty gateway",
        "retention": "RC-01 (General Ledger, 7 yr)",
        "cost": 50000,
        "sanit": "Retained as live M59 payment rail integration",
    },
    {
        "id": "SRC-21",
        "name": "Savar Bus Stand Center (City Bank BEFTN Portal)",
        "custodian": "CFO (Mustafizur Rahman)",
        "class": "PORTAL",
        "disp": "K",
        "pii": False,
        "wave": "n/a",
        "rfp": "Bank electronic clearing",
        "retention": "RC-01 (General Ledger, 7 yr)",
        "cost": 60000,
        "sanit": "Retained as live M60 BEFTN clearing integration",
    },
    {
        "id": "SRC-22",
        "name": "Jessore MK Road (Telematics Tracking Provider)",
        "custodian": "Logistics Lead (Zillur Rahman)",
        "class": "PORTAL",
        "disp": "K",
        "pii": False,
        "wave": "n/a",
        "rfp": "Fleet GPS tracking portal",
        "retention": "RC-12 (Fleet Logs, 3 yr)",
        "cost": 45000,
        "sanit": "Retained as live M64 IoT vehicle tracking integration",
    },
    {
        "id": "SRC-23",
        "name": "Kushtia NS Road Point (Historical Recruitment DB)",
        "custodian": "HR Director (Nasreen Sultana)",
        "class": "PORTAL",
        "disp": "P",
        "pii": True,
        "wave": "W3",
        "rfp": "Historical recruitment portals",
        "retention": "DC-08 (Purge immediately per PDPA)",
        "cost": 30000,
        "sanit": "IEEE 2883 Purge & Verified Media Destruction",
    },
    {
        "id": "SRC-24",
        "name": "Dinajpur Ganeshtola Point",
        "custodian": "Regional Ops Head (Nasir Uddin)",
        "class": "SS",
        "disp": "R",
        "pii": True,
        "wave": "W4",
        "rfp": "Branch service spreadsheets",
        "retention": "RC-04 (Service Orders, 5 yr)",
        "cost": 15000,
        "sanit": "NIST 800-88 Clear + Share Deprovision",
    },
    {
        "id": "SRC-25",
        "name": "Feni Trunk Road Point",
        "custodian": "Regional Ops Head (Nasir Uddin)",
        "class": "SS",
        "disp": "R",
        "pii": True,
        "wave": "W3",
        "rfp": "Branch service spreadsheets",
        "retention": "RC-04 (Service Orders, 5 yr)",
        "cost": 15000,
        "sanit": "NIST 800-88 Clear + Share Deprovision",
    },
    {
        "id": "SRC-26",
        "name": "Cox's Bazar Main Road Point",
        "custodian": "Regional Ops Head (Nasir Uddin)",
        "class": "SS",
        "disp": "R",
        "pii": True,
        "wave": "W6",
        "rfp": "Branch service spreadsheets",
        "retention": "RC-04 (Service Orders, 5 yr)",
        "cost": 15000,
        "sanit": "NIST 800-88 Clear + Share Deprovision",
    },
    # 3. Accounting History (4 sources - DB / SS)
    {
        "id": "SRC-27",
        "name": "Tally ERP 9 Company File A",
        "custodian": "CFO (Mustafizur Rahman)",
        "class": "DB",
        "disp": "R",
        "pii": False,
        "wave": "W2",
        "rfp": "Standalone accounting software",
        "retention": "RC-01 (General Ledger, 7 yr)",
        "cost": 120000,
        "sanit": "IEEE 2883 Clear + Vault Archival",
    },
    {
        "id": "SRC-28",
        "name": "Tally ERP 9 Company File B",
        "custodian": "CFO (Mustafizur Rahman)",
        "class": "DB",
        "disp": "R",
        "pii": False,
        "wave": "W2",
        "rfp": "no contractual accountability",
        "retention": "RC-01 (General Ledger, 7 yr)",
        "cost": 120000,
        "sanit": "IEEE 2883 Clear + Vault Archival",
    },
    {
        "id": "SRC-29",
        "name": "Branch Cash Book Spreadsheets",
        "custodian": "CFO (Mustafizur Rahman)",
        "class": "SS",
        "disp": "R",
        "pii": False,
        "wave": "W5",
        "rfp": "Manual invoice & cash logs",
        "retention": "RC-01 (General Ledger, 7 yr)",
        "cost": 40000,
        "sanit": "NIST 800-88 Clear + Deprovision",
    },
    {
        "id": "SRC-30",
        "name": "Corporate Invoicing Register",
        "custodian": "Corporate Billing Mgr (Arifur Rahman)",
        "class": "SS",
        "disp": "R",
        "pii": False,
        "wave": "W5",
        "rfp": "no contractual accountability",
        "retention": "RC-02 (Tax/Invoices, 7 yr)",
        "cost": 35000,
        "sanit": "NIST 800-88 Clear + Deprovision",
    },
    # 4. HR & Payroll (4 sources - SS / PAPER)
    {
        "id": "SRC-31",
        "name": "Staff Master Register (Physical Contract Originals)",
        "custodian": "Legal Counsel (M. Faruq)",
        "class": "PAPER",
        "disp": "K",
        "pii": True,
        "wave": "n/a",
        "rfp": "Physical staff contracts",
        "retention": "DC-01 (Statutory Employment, 10 yr)",
        "cost": 15000,
        "sanit": "Retained in climate-controlled fireproof vault",
    },
    {
        "id": "SRC-32",
        "name": "Monthly Payroll Sheets 2025-26",
        "custodian": "HR Director (Nasreen Sultana)",
        "class": "SS",
        "disp": "R",
        "pii": True,
        "wave": "W5",
        "rfp": "Manual payroll calculation",
        "retention": "RC-03 (Payroll & TDS, 7 yr)",
        "cost": 30000,
        "sanit": "NIST 800-88 Clear + Deprovision",
    },
    {
        "id": "SRC-33",
        "name": "Technician Commission Logs",
        "custodian": "HR Director (Nasreen Sultana)",
        "class": "SS",
        "disp": "R",
        "pii": True,
        "wave": "W5",
        "rfp": "no contractual accountability",
        "retention": "RC-03 (Payroll & TDS, 7 yr)",
        "cost": 25000,
        "sanit": "NIST 800-88 Clear + Deprovision",
    },
    {
        "id": "SRC-34",
        "name": "Statutory Tax Deduction Sheets",
        "custodian": "CFO (Mustafizur Rahman)",
        "class": "SS",
        "disp": "R",
        "pii": True,
        "wave": "W7",
        "rfp": "no contractual accountability",
        "retention": "RC-02 (Tax/NBR 7 yr)",
        "cost": 20000,
        "sanit": "NIST 800-88 Clear + Deprovision",
    },
    # 5. WordPress CMS & Media (2 sources - DB / S3)
    {
        "id": "SRC-35",
        "name": "WordPress Portal Database",
        "custodian": "Marketing Head (Shumona Akter)",
        "class": "DB",
        "disp": "R",
        "pii": False,
        "wave": "W5",
        "rfp": "Legacy WordPress website",
        "retention": "DC-14 (Web Assets, 3 yr)",
        "cost": 75000,
        "sanit": "IEEE 2883 Purge + Server Decommission",
    },
    {
        "id": "SRC-36",
        "name": "Media Uploads Repository",
        "custodian": "Marketing Head (Shumona Akter)",
        "class": "MAIL",
        "disp": "R",
        "pii": False,
        "wave": "W6",
        "rfp": "Legacy media store",
        "retention": "DC-14 (Web Assets, 3 yr)",
        "cost": 45000,
        "sanit": "S3 Bucket Destroy + Cryptographic Key Erase",
    },
    # 6. Inventory & Asset Registers (4 sources - SS)
    # 6. Inventory & Asset Registers (SRC-37 is Retirable, SRC-38..40 are Non-System Knowledge/Registry feeds)
    {
        "id": "SRC-37",
        "name": "Central Warehouse SKU Catalog",
        "custodian": "Warehouse Lead (Mahbub Alam)",
        "class": "SS",
        "disp": "R",
        "pii": False,
        "wave": "W6",
        "rfp": "Manual parts catalog",
        "retention": "RC-08 (Inventory Lots, 5 yr)",
        "cost": 30000,
        "sanit": "NIST 800-88 Clear + Deprovision",
    },
    {
        "id": "SRC-38",
        "name": "Warehouse Physical Count Practices (Knowledge)",
        "custodian": "Warehouse Lead (Mahbub Alam)",
        "class": "PEOPLE",
        "disp": "N",
        "pii": False,
        "wave": "n/a",
        "rfp": "Warehouse practices",
        "retention": "n/a (Human Knowledge Captured in SOP)",
        "cost": 0,
        "sanit": "Captured into standard operating procedures and trained",
    },
    {
        "id": "SRC-39",
        "name": "National Standard Hardware SKU Directory",
        "custodian": "Procurement Lead (Selim Reza)",
        "class": "PUB",
        "disp": "N",
        "pii": False,
        "wave": "n/a",
        "rfp": "Hardware standard directory",
        "retention": "n/a (External Reference Feed)",
        "cost": 0,
        "sanit": "Converted to ongoing API reference feed",
    },
    {
        "id": "SRC-40",
        "name": "DoE E-Waste Compliance Knowledge",
        "custodian": "E-Waste Officer (Tareq Hasan)",
        "class": "PEOPLE",
        "disp": "N",
        "pii": False,
        "wave": "n/a",
        "rfp": "E-waste regulatory practices",
        "retention": "n/a (Human Knowledge Captured in SOP)",
        "cost": 0,
        "sanit": "Regulatory compliance knowledge codified in M50",
    },
    # 7. Contacts & Warranty Stores (SRC-41..44: Non-System Knowledge & External Feeds & Credential Stores)
    {
        "id": "SRC-41",
        "name": "Corporate Client Account Knowledge",
        "custodian": "Commercial Head (Fahim Chowdhury)",
        "class": "PEOPLE",
        "disp": "N",
        "pii": True,
        "wave": "n/a",
        "rfp": "Commercial client knowledge",
        "retention": "n/a (Human Knowledge Captured in M33)",
        "cost": 0,
        "sanit": "Commercial relationship knowledge onboarded to CRM",
    },
    {
        "id": "SRC-42",
        "name": "SMS Gateway Provider API Credentials & Secrets",
        "custodian": "Security Lead (Farhan Ahmed)",
        "class": "CFG",
        "disp": "N",
        "pii": False,
        "wave": "n/a",
        "rfp": "SMS gateway credentials",
        "retention": "n/a (Credential Store)",
        "cost": 0,
        "sanit": "Legacy API keys revoked; HashiCorp Vault rotated",
    },
    {
        "id": "SRC-43",
        "name": "Legacy Application Database Credentials & Root Keys",
        "custodian": "Security Lead (Farhan Ahmed)",
        "class": "CFG",
        "disp": "N",
        "pii": False,
        "wave": "n/a",
        "rfp": "Legacy database keys",
        "retention": "n/a (Credential Store)",
        "cost": 0,
        "sanit": "Database passwords wiped; admin access revoked",
    },
    {
        "id": "SRC-44",
        "name": "BTRC & Consumer Rights Regulatory Feed",
        "custodian": "QA Head (Zubair Hossain)",
        "class": "PUB",
        "disp": "N",
        "pii": False,
        "wave": "n/a",
        "rfp": "BTRC & Consumer Rights Feed",
        "retention": "n/a (Ongoing Regulatory Feed)",
        "cost": 0,
        "sanit": "Converted to ongoing regulatory reference feed",
    },
    # 8. Misc Records, Tools & Evidence (SRC-45..48: Non-System Feeds & Credentials)
    {
        "id": "SRC-45",
        "name": "Global Brand RMA Standards & Warranty Directory",
        "custodian": "Brand Relations Lead (Kamrul Islam)",
        "class": "PUB",
        "disp": "N",
        "pii": False,
        "wave": "n/a",
        "rfp": "Brand warranty standards directory",
        "retention": "n/a (External Reference Feed)",
        "cost": 0,
        "sanit": "Converted to manufacturer API reference feed",
    },
    {
        "id": "SRC-46",
        "name": "Lab Machine Calibration Profiles & Firmware Hashes",
        "custodian": "Security Lead (Farhan Ahmed)",
        "class": "CFG",
        "disp": "N",
        "pii": False,
        "wave": "n/a",
        "rfp": "Machine calibration profiles",
        "retention": "n/a (Credential & Profile Store)",
        "cost": 0,
        "sanit": "Legacy calibration keys rotated; stored in Vault PKI",
    },
    {
        "id": "SRC-47",
        "name": "NBR National Depreciation & Asset Tax Table",
        "custodian": "CFO (Mustafizur Rahman)",
        "class": "PUB",
        "disp": "N",
        "pii": False,
        "wave": "n/a",
        "rfp": "NBR tax schedule feed",
        "retention": "n/a (National Published Table)",
        "cost": 0,
        "sanit": "Incorporated into M51 automated tax engine rules",
    },
    {
        "id": "SRC-48",
        "name": "Legacy Scheduled Cron Tasks & Service Keys",
        "custodian": "Security Lead (Farhan Ahmed)",
        "class": "CFG",
        "disp": "N",
        "pii": False,
        "wave": "n/a",
        "rfp": "Legacy crontab & service scripts",
        "retention": "n/a (Credential Store)",
        "cost": 0,
        "sanit": "All legacy crontabs cleared, SSH keys wiped, accounts locked",
    },
]


def derive_verdict(statuses: list[str]) -> str:
    """FAIL if any check failed, INCOMPLETE if any is not PASS, else PASS."""
    if not statuses:
        return INCOMPLETE
    if FAIL in statuses:
        return FAIL
    if any(s != PASS for s in statuses):
        return INCOMPLETE
    return PASS


def exit_code_for(verdict: str) -> int:
    return {PASS: 0, FAIL: 1}.get(verdict, 2)


def _check(status: str, detail: str) -> dict[str, str]:
    return {"status": status, "detail": detail}


def load_upstream(name: str) -> tuple[dict | None, str]:
    """An upstream R11-M02 evidence file -> (data, reason when unusable)."""
    path = Path(EVIDENCE_DIR) / name
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, f"upstream evidence {name} not found"
    except (OSError, ValueError) as exc:
        return None, f"upstream evidence {name} unreadable: {exc}"
    if not isinstance(data, dict):
        return None, f"upstream evidence {name} is not an object"
    return data, ""


def _upstream_status(status: Any, label: str, reason: str = "") -> dict[str, str]:
    """Only an exact PASS / FAIL from upstream counts; anything else is not a measurement."""
    if status == PASS:
        return _check(PASS, f"{label}: PASS")
    if status == FAIL:
        return _check(FAIL, f"{label}: FAIL" + (f" - {reason}" if reason else ""))
    return _check(
        UNMEASURED, f"{label}: {status!r}" + (f" - {reason}" if reason else " (not measured)")
    )


def reconciliation_check(src_id: str, t01: dict | None, t01_reason: str) -> dict[str, str]:
    if t01 is None:
        return _check(UNMEASURED, t01_reason)
    for row in t01.get("sources") or []:
        if isinstance(row, dict) and row.get("source_id") == src_id:
            return _upstream_status(
                row.get("approval_status"),
                "T01 MG-004 sign-off",
                str(row.get("approval_reason") or ""),
            )
    return _check(FAIL, f"{src_id} is not in the T01 reconciliation register")


def archive_check(src_id: str, t04: dict | None, t04_reason: str) -> dict[str, str]:
    if t04 is None:
        return _check(UNMEASURED, t04_reason)
    for cls in t04.get("archive_classes") or []:
        if isinstance(cls, dict) and src_id in (cls.get("covered_sources") or []):
            return _upstream_status(
                cls.get("verification_status"), f"T04 archive {cls.get('archive_class_id')}"
            )
    return _check(FAIL, f"no T04 archive class covers {src_id} (DA-006: archive before retire)")


def source_checks(
    src: dict[str, Any], t01: dict | None, t01_reason: str, t04: dict | None, t04_reason: str
) -> dict[str, dict[str, str]]:
    disp, pii = src["disp"], bool(src["pii"])
    checks: dict[str, dict[str, str]] = {}
    if disp == "R":
        checks["mig08_reconciliation_signoff"] = reconciliation_check(src["id"], t01, t01_reason)
        checks["archive_restorable"] = archive_check(src["id"], t04, t04_reason)
        checks["negative_connection_test"] = _check(UNMEASURED, NEGATIVE_TEST_REASON)
    elif disp == "P":
        checks["mig08_reconciliation_signoff"] = reconciliation_check(src["id"], t01, t01_reason)
        checks["purge_verification"] = _check(UNMEASURED, PURGE_REASON)
    elif disp == "K":
        checks["retention_review"] = _check(UNMEASURED, RETENTION_REVIEW_REASON)
    elif disp == "N":
        checks["transition_evidence"] = _check(UNMEASURED, TRANSITION_REASON)
    else:
        checks["disposition"] = _check(FAIL, f"invalid disposition {disp!r}")
    if pii and disp in ("R", "P", "K"):
        checks["dpo_countersign"] = _check(UNMEASURED, DPO_REASON)
    return checks


def source_entry(
    src: dict[str, Any], t01: dict | None, t01_reason: str, t04: dict | None, t04_reason: str
) -> dict[str, Any]:
    checks = source_checks(src, t01, t01_reason, t04, t04_reason)
    status = derive_verdict([c["status"] for c in checks.values()])
    target_state = "RETAINED" if src["disp"] == "K" else "D7"
    state = {PASS: target_state, FAIL: "BLOCKED"}.get(status, UNMEASURED)
    return {
        "source_id": src["id"],
        "name": src["name"],
        "designated_custodian": src["custodian"],
        "functional_class": src["class"],
        "disposition": src["disp"],
        "holds_pii": src["pii"],
        "retire_wave": src["wave"],
        "rfp_practice": src["rfp"],
        "retention_class": src["retention"],
        "planned_sanitisation_technique": src["sanit"],
        "declared_annual_run_cost_bdt": src["cost"],
        "target_state": target_state,
        "state": state,
        "checks": checks,
        "status": status,
    }


def register_completeness() -> dict[str, str]:
    ids = [s["id"] for s in SOURCES_DATA]
    expected = [f"SRC-{n:02d}" for n in range(1, 49)]
    problems = []
    if sorted(ids) != expected:
        missing = sorted(set(expected) - set(ids))
        extra = sorted(set(ids) - set(expected))
        dupes = sorted(i for i, n in Counter(ids).items() if n > 1)
        problems.append(f"ids: missing={missing} extra={extra} duplicated={dupes}")
    bad = [s["id"] for s in SOURCES_DATA if s["disp"] not in VALID_DISPOSITIONS]
    if bad:
        problems.append(f"invalid dispositions: {bad}")
    return _check(
        FAIL if problems else PASS,
        "; ".join(problems) or f"{len(ids)} distinct sources, each with a valid disposition",
    )


def _norm(name: str) -> str:
    return re.sub(r"\s+", " ", name).strip().lower()


def register_agreement(t01: dict | None, t01_reason: str) -> dict[str, str]:
    """Each source's name here must describe the same source as the T01 register."""
    if t01 is None:
        return _check(UNMEASURED, t01_reason)
    t01_names = {
        row.get("source_id"): str(row.get("source_name") or "")
        for row in t01.get("sources") or []
        if isinstance(row, dict)
    }
    mismatches = []
    for src in SOURCES_DATA:
        other = t01_names.get(src["id"])
        if other is None:
            mismatches.append(f"{src['id']} absent from T01")
        elif not _norm(src["name"]).startswith(_norm(other)):
            mismatches.append(f"{src['id']}: {src['name']!r} vs T01 {other!r}")
    return _check(
        FAIL if mismatches else PASS,
        f"{len(mismatches)} source(s) disagree with the T01 register: " + "; ".join(mismatches)
        if mismatches
        else "every source name agrees with the T01 reconciliation register",
    )


def scan_codebase(roots: tuple[str, ...] | None = None) -> tuple[dict[str, str], list[str]]:
    """Read-only scan for configuration that still references a retired legacy endpoint."""
    findings: list[str] = []
    scanned = 0
    needles = {ep.encode(): sid for sid, ep in RETIRED_ENDPOINTS.items()}
    for root_name in roots or SCAN_ROOTS:
        root = REPO_ROOT / root_name
        if not root.is_dir():
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SCAN_SKIP_DIRS]
            for fname in filenames:
                path = Path(dirpath) / fname
                if path.suffix.lower() not in SCAN_SUFFIXES:
                    continue
                try:
                    if path.stat().st_size > SCAN_MAX_BYTES:
                        continue
                    blob = path.read_bytes()
                except OSError:
                    continue
                scanned += 1
                for needle, sid in needles.items():
                    if needle in blob:
                        findings.append(f"{path.relative_to(REPO_ROOT).as_posix()} ({sid})")
    if findings:
        detail = f"{len(findings)} file(s) still reference a retired endpoint: " + ", ".join(
            findings[:10]
        )
        return _check(FAIL, detail), findings
    if not scanned:
        return _check(UNMEASURED, "no codebase files found to scan"), findings
    return (
        _check(PASS, f"no reference to {sorted(RETIRED_ENDPOINTS.values())} in {scanned} files"),
        findings,
    )


def build_evidence(scan_roots: tuple[str, ...] | None = None) -> dict[str, Any]:
    t01, t01_reason = load_upstream(T01_EVIDENCE)
    t04, t04_reason = load_upstream(T04_EVIDENCE)
    register = [source_entry(s, t01, t01_reason, t04, t04_reason) for s in SOURCES_DATA]
    scan_check, findings = scan_codebase(scan_roots)
    estate_checks = {
        "register_complete": register_completeness(),
        "register_agrees_with_t01": register_agreement(t01, t01_reason),
        "codebase_legacy_endpoint_references": scan_check,
        "shadow_system_scan": _check(UNMEASURED, SHADOW_SCAN_REASON),
    }
    statuses = [s["status"] for s in register] + [c["status"] for c in estate_checks.values()]
    verdict = derive_verdict(statuses)

    def verified(disp: str) -> int:
        return sum(1 for s in register if s["disposition"] == disp and s["status"] == PASS)

    def check_count(name: str, status: str) -> int:
        return sum(1 for s in register if s["checks"].get(name, {}).get("status") == status)

    retirable_cost = sum(
        s["declared_annual_run_cost_bdt"] for s in register if s["disposition"] == "R"
    )
    released = sum(
        s["declared_annual_run_cost_bdt"]
        for s in register
        if s["disposition"] == "R" and s["status"] == PASS
    )
    return {
        "milestone": "R11-M02",
        "task": "R11-M02-T03",
        "title": "Master Legacy Decommission Register (RL-006 DCM-01..DCM-57)",
        "execution_timestamp": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "mode": "MEASURE_ONLY (no legacy system is touched by this tool)",
        "governing_standards": [
            "RL-006",
            "DA-006",
            "NIST SP 800-88r2",
            "IEEE 2883:2022",
            "PDPA Law 63 of 2026",
        ],
        "measurement_policy": "GV-009: every state is derived from checks measured in this "
        "run; what cannot be observed from this workstation is UNMEASURED with its reason",
        "declared_dispositions": dict(sorted(Counter(s["disposition"] for s in register).items())),
        "disposition_summary": {
            "retirable_sources_decommissioned_d7": verified("R"),
            "deliberately_retained_sources_k": verified("K"),
            "purge_disposition_sources_p": verified("P"),
            "non_system_sources_transitioned_n": verified("N"),
            "total_estate_accounted_for": sum(
                1 for s in register if s["disposition"] in VALID_DISPOSITIONS
            ),
            "sources_state_unmeasured": sum(1 for s in register if s["state"] == UNMEASURED),
            "sources_blocked": sum(1 for s in register if s["state"] == "BLOCKED"),
            "restated_gv001_closure_criteria_met": verdict == PASS,
        },
        "financial_summary": {
            "declared_annual_run_cost_of_retirable_sources_bdt": retirable_cost,
            "total_annual_run_cost_released_bdt": released,
            "formatted_annual_saving": f"BDT {released / 1000000:.2f}M / year released "
            f"(of BDT {retirable_cost / 1000000:.2f}M declared)",
        },
        "compliance_summary": {
            "pii_sources_requiring_dpo_countersign": sum(
                1 for s in register if "dpo_countersign" in s["checks"]
            ),
            "dpo_countersigned_pii_sources": check_count("dpo_countersign", PASS),
            "negative_connection_tests_passed": check_count("negative_connection_test", PASS),
            "negative_connection_tests_unmeasured": check_count(
                "negative_connection_test", UNMEASURED
            ),
            "shadow_system_scan_findings": None,
            "shadow_system_scan_status": estate_checks["shadow_system_scan"]["status"],
            "codebase_legacy_endpoint_references": len(findings),
        },
        "estate_checks": estate_checks,
        "verdict": verdict,
        "overall_status": verdict,
        "sources": register,
    }


def _md(value: Any) -> str:
    return "n/a" if value is None else str(value).replace("|", "/")


def render_markdown(ev: dict[str, Any]) -> str:
    ds, fs, cs = ev["disposition_summary"], ev["financial_summary"], ev["compliance_summary"]
    declared = ev["declared_dispositions"]
    out = [
        "# Legacy Decommission Register (RL-006 / P12-M02)",
        "",
        "## Task R11-M02-T03 Verification Record",
        "",
        f"- **Execution Timestamp**: {ev['execution_timestamp']} — {ev['mode']}",
        f"- **Verdict (computed)**: `{ev['verdict']}`",
        f"- **Sources in register**: {ds['total_estate_accounted_for']} "
        f"(declared R={declared.get('R', 0)}, K={declared.get('K', 0)}, "
        f"P={declared.get('P', 0)}, N={declared.get('N', 0)})",
        f"- **Verified outcomes**: D7 retired {ds['retirable_sources_decommissioned_d7']}, "
        f"retained {ds['deliberately_retained_sources_k']}, "
        f"purged {ds['purge_disposition_sources_p']}, "
        f"transitioned {ds['non_system_sources_transitioned_n']}; "
        f"UNMEASURED {ds['sources_state_unmeasured']}, blocked {ds['sources_blocked']}",
        f"- **Annual run cost**: {fs['formatted_annual_saving']}",
        f"- **Negative connection tests passed**: {cs['negative_connection_tests_passed']} "
        f"({cs['negative_connection_tests_unmeasured']} UNMEASURED)",
        f"- **DPO countersigns observed**: {cs['dpo_countersigned_pii_sources']} / "
        f"{cs['pii_sources_requiring_dpo_countersign']}",
        "",
        "### Estate checks",
        "",
        "| Check | Status | Detail |",
        "|---|:---:|---|",
    ]
    for name, c in ev["estate_checks"].items():
        out.append(f"| `{name}` | `{c['status']}` | {_md(c['detail'])} |")
    out += [
        "",
        "---",
        "",
        "### 48-Source Decommission Register",
        "",
        "| ID | Source Name | Class | Disp | Wave | Target | State | Status |",
        "|---|---|:---:|:---:|:---:|:---:|:---:|:---:|",
    ]
    for s in ev["sources"]:
        out.append(
            f"| **{s['source_id']}** | {_md(s['name'])} | {s['functional_class']} "
            f"| `{s['disposition']}` | {s['retire_wave']} | {s['target_state']} "
            f"| `{s['state']}` | `{s['status']}` |"
        )
    reasons = sorted(
        {
            f"- {name}: {c['detail']}"
            for s in ev["sources"]
            for name, c in s["checks"].items()
            if c["status"] != PASS
        }
    )
    if reasons:
        out += ["", "Per-source checks not passed, and why:", "", *reasons]
    out.append("")
    if ev["verdict"] == PASS:
        out += ["Every decommission check above was measured as passed.", ""]
    else:
        out += [
            f"No legacy source is certified decommissioned by this record (verdict "
            f"`{ev['verdict']}`).",
            "",
        ]
    return "\n".join(out)


def write_outputs(ev: dict[str, Any]) -> tuple[Path, Path]:
    evidence_dir, docs_dir = Path(EVIDENCE_DIR), Path(DOCS_DIR)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)
    json_path = evidence_dir / EVIDENCE_NAME
    md_path = docs_dir / MD_NAME
    json_path.write_bytes((json.dumps(ev, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
    md_path.write_bytes(render_markdown(ev).encode("utf-8"))
    return json_path, md_path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="R11-M02-T03 decommission register (measure-only)")
    ap.parse_args(argv)
    ev = build_evidence()
    json_path, md_path = write_outputs(ev)
    ds = ev["disposition_summary"]
    print(
        f"R11-M02-T03 (measure-only): {ds['retirable_sources_decommissioned_d7']} D7 verified, "
        f"{ds['sources_state_unmeasured']} UNMEASURED, {ds['sources_blocked']} blocked"
    )
    print(f"Verdict: {ev['verdict']}")
    print(f"JSON: {json_path}")
    print(f"Markdown: {md_path}")
    return exit_code_for(ev["verdict"])


if __name__ == "__main__":
    sys.exit(main())
