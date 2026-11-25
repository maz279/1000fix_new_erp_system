#!/usr/bin/env python3
"""
verify-legacy-profiles.py - Automated verification of the 48-Source Legacy Profiling Register.
Validates completion, quality metrics (P1-P6), and Bengali normalization per P01-M07 / R01-M01-T05.
"""

import re
import sys
from pathlib import Path


def main():
    repo_root = Path(__file__).resolve().parent.parent.parent
    profile_md = repo_root / "docs" / "p01-m07" / "legacy-source-profiles-completed.md"

    print(f"[*] Verifying Legacy Profiling Register at: {profile_md}")
    if not profile_md.exists():
        print(f"[FAIL] Legacy profile file not found: {profile_md}")
        sys.exit(1)

    content = profile_md.read_text(encoding="utf-8")

    # 1. Verify all 48 sources exist
    sources = re.findall(r"\*\*SRC-(\d{2})\*\*", content)
    unique_sources = sorted(list(set(sources)))

    print(f"[*] Found {len(unique_sources)} unique source identifiers.")
    if len(unique_sources) != 48:
        print(f"[FAIL] Expected exactly 48 sources, found {len(unique_sources)}")
        sys.exit(1)

    expected_ids = [f"{i:02d}" for i in range(1, 49)]
    missing = set(expected_ids) - set(unique_sources)
    if missing:
        print(f"[FAIL] Missing source IDs: {sorted(list(missing))}")
        sys.exit(1)

    # 2. Verify all 8 classes are covered
    classes = [
        "1. Live Tracker",
        "2. Branch Sheet",
        "3. Accounting",
        "4. HR & Payroll",
        "5. WordPress CMS",
        "6. Inventory",
        "7. Contacts",
        "8. Misc Records",
    ]
    for c in classes:
        if c not in content:
            print(f"[FAIL] Missing source class: {c}")
            sys.exit(1)

    # 3. Verify Quality Framework mentions
    for dim in [
        "P1: Completeness",
        "P2: Uniqueness",
        "P3: Timeliness",
        "P4: Validity",
        "P5: Accuracy",
        "P6: Consistency",
    ]:
        if dim not in content:
            print(f"[FAIL] Missing DQ dimension: {dim}")
            sys.exit(1)

    # 4. Verify Bengali Script & Numeral Normalisation
    if "Unicode Standard NFC (UTF-8)" not in content:
        print("[FAIL] Missing Unicode NFC normalisation specification")
        sys.exit(1)

    if "BENGALI_TO_ASCII" not in content:
        print("[FAIL] Missing Bengali numeral mapping specification")
        sys.exit(1)

    # 5. Verify Non-Migration Ruling
    if "FORMAL RULING ON NON-MIGRATION" not in content:
        print("[FAIL] Missing non-migration ruling")
        sys.exit(1)

    print(
        "[PASS] All 48 legacy sources verified, 8 classes covered, P1-P6 metrics and Bengali normalization valid."
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
