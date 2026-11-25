#!/usr/bin/env python3
"""
Verify Technical Debt Register & Code TODO Tree
Milestone: R09-M04 - Task: R09-M04-T02
Standard: BE-009 / P11-M08-T01
"""

import json
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEBT_REGISTER_PATH = REPO_ROOT / "docs" / "debt" / "BE-009-technical-debt-register.json"
EVIDENCE_PATH = (
    REPO_ROOT / "docs" / "traceability" / "evidence" / "r09-m04-debt-burndown-evidence.json"
)
ADDONS_PATH = REPO_ROOT / "addons"


def verify_debt_register():
    print(f"[*] Verifying BE-009 Debt Register at: {DEBT_REGISTER_PATH}")
    if not DEBT_REGISTER_PATH.is_file():
        raise FileNotFoundError(f"Debt register not found: {DEBT_REGISTER_PATH}")

    with open(DEBT_REGISTER_PATH, encoding="utf-8") as f:
        data = json.load(f)

    items = data.get("items", [])
    if len(items) != 15:
        raise ValueError(f"Expected 15 canonical debt items (DBT-001..DBT-015), found {len(items)}")

    expected_ids = [f"DBT-{i:03d}" for i in range(1, 16)]
    found_ids = [item.get("id") for item in items]
    if found_ids != expected_ids:
        raise ValueError(f"Debt item IDs mismatch: expected {expected_ids}, got {found_ids}")

    for item in items:
        debt_id = item.get("id")
        title = item.get("title")
        owner = item.get("owner")
        disposition = item.get("disposition")
        resolution = item.get("resolution")

        if not (debt_id and title and owner and disposition and resolution):
            raise ValueError(f"Incomplete debt item {debt_id}: {item}")
        if disposition not in ("repaid", "resolved"):
            raise ValueError(f"Debt item {debt_id} not resolved/repaid: status={disposition}")

    print("[+] All 15 canonical debt items (DBT-001..DBT-015) validated as repaid/resolved.")
    return data


def scan_codebase_todos():
    print(f"[*] Scanning codebase for unowned TODO/FIXME comment markers in: {ADDONS_PATH}")
    # Match comments containing TODO/FIXME/XXX
    comment_pattern = re.compile(r"(?:#|//|/\*|\*|<!--)\s*.*\b(TODO|FIXME|XXX)\b", re.IGNORECASE)
    owned_pattern = re.compile(r"\b(TODO|FIXME|XXX)\(([a-zA-Z0-9_\-\.\/ ]+)\):?", re.IGNORECASE)
    unowned_pattern = re.compile(r"\b(TODO|FIXME|XXX)\b(?!\([a-zA-Z0-9_\-\.\/ ]+\))", re.IGNORECASE)

    unowned_findings = []
    owned_findings = []

    for root, dirs, files in os.walk(ADDONS_PATH):
        # Skip pycache and hidden dirs
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]
        for file in files:
            if not file.endswith((".py", ".js", ".ts", ".xml", ".json", ".yaml", ".yml", ".md")):
                continue
            filepath = Path(root) / file
            try:
                content = filepath.read_text(encoding="utf-8", errors="ignore")
                for line_no, line in enumerate(content.splitlines(), start=1):
                    # Check if line contains a comment with TODO/FIXME/XXX
                    if comment_pattern.search(line):
                        # Check if owned
                        owned_match = owned_pattern.search(line)
                        if owned_match:
                            owned_findings.append(
                                {
                                    "file": str(filepath.relative_to(REPO_ROOT)),
                                    "line": line_no,
                                    "type": owned_match.group(1).upper(),
                                    "owner": owned_match.group(2).strip(),
                                    "text": line.strip(),
                                }
                            )
                        else:
                            unowned_match = unowned_pattern.search(line)
                            if unowned_match:
                                unowned_findings.append(
                                    {
                                        "file": str(filepath.relative_to(REPO_ROOT)),
                                        "line": line_no,
                                        "type": unowned_match.group(1).upper(),
                                        "text": line.strip(),
                                    }
                                )
            except Exception as e:
                print(f"[!] Warning reading {filepath}: {e}")

    print(
        f"[+] Scan completed: {len(unowned_findings)} unowned TODOs, {len(owned_findings)} owned TODOs."
    )
    return unowned_findings, owned_findings


def main():
    debt_data = verify_debt_register()
    unowned_todos, owned_todos = scan_codebase_todos()

    is_clean = len(unowned_todos) == 0

    evidence = {
        "$schema": "1000fix-erp/evidence/1",
        "milestone": "R09-M04",
        "task": "R09-M04-T02",
        "title": "Technical Debt Burn-Down & Todo Tree Register Verification",
        "standard": "BE-009 / P11-M08-T01",
        "timestamp": "2026-10-20T21:18:00Z",
        "register_summary": debt_data["summary"],
        "items_count": len(debt_data["items"]),
        "unowned_todos_count": len(unowned_todos),
        "owned_todos_count": len(owned_todos),
        "unowned_todos": unowned_todos,
        "owned_todos": owned_todos,
        "status": "PASS" if is_clean else "FAIL",
    }

    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(EVIDENCE_PATH, "w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2)

    print(f"[+] Evidence emitted to: {EVIDENCE_PATH}")
    if not is_clean:
        print(f"[!] FAILED: Found {len(unowned_todos)} unowned TODOs!")
        sys.exit(1)
    else:
        print("[+] SUCCESS: Debt burn-down fully verified with 0 unowned TODOs.")


if __name__ == "__main__":
    main()
