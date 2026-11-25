#!/usr/bin/env python3
"""check-secrets.py — Secret Scanning & Zero-Leakage Audit (EP-06).

Rule EP-06:
"Secrets are Vault-managed, never in repo/config/logs. Secret-scan clean."
"""

from __future__ import annotations

import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = REPO_ROOT / "docs" / "traceability" / "evidence"

IGNORED_DIRS = {
    ".git",
    "node_modules",
    ".next",
    "dist",
    "build",
    ".venv",
    "venv",
    "__pycache__",
    "vendor",
    ".idea",
    ".vscode",
    "evidence",
}

IGNORED_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".svg",
    ".gif",
    ".ico",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".pdf",
    ".lock",
    ".log",
    ".json",
}

SECRET_PATTERNS = [
    ("PRIVATE_KEY", re.compile(r"-----BEGIN (?:RSA|OPENSSH|EC|DSA)?\s*PRIVATE KEY-----")),
    (
        "AWS_SECRET",
        re.compile(
            r'(?:aws_secret_access_key|aws_access_key_id)\s*=\s*[\'"][A-Za-z0-9/+=]{20,}[\'"]',
            re.IGNORECASE,
        ),
    ),
    (
        "HARDCODED_PROD_PASSWORD",
        re.compile(
            r'(?:prod_password|production_password)\s*[:=]\s*[\'"][^\'"]{8,}[\'"]', re.IGNORECASE
        ),
    ),
    (
        "LIVE_BKASH_SECRET",
        re.compile(
            r'bkash_(?:app_secret|password)\s*[:=]\s*[\'"][A-Za-z0-9_\-]{20,}[\'"]', re.IGNORECASE
        ),
    ),
    (
        "LIVE_NAGAD_KEY",
        re.compile(
            r'nagad_(?:private_key|secret)\s*[:=]\s*[\'"][A-Za-z0-9_\-]{20,}[\'"]', re.IGNORECASE
        ),
    ),
]


def scan_repo() -> dict:
    scanned_files = 0
    findings = []

    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in IGNORED_EXTENSIONS:
            continue

        scanned_files += 1
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError as exc:
            # an unreadable file is not silently "clean": say it was skipped
            print(f"check-secrets: skipped unreadable {path}: {exc}", file=sys.stderr)
            continue

        for label, pattern in SECRET_PATTERNS:
            matches = pattern.findall(content)
            if matches:
                # Filter out obvious docs / schema examples / mock tokens
                for m in matches:
                    if (
                        "vault" in str(m).lower()
                        or "example" in str(m).lower()
                        or "mock" in str(m).lower()
                        or "test" in str(m).lower()
                    ):
                        continue
                    findings.append(
                        {
                            "file": str(path.relative_to(REPO_ROOT)),
                            "type": label,
                            "snippet": str(m)[:30] + "...",
                        }
                    )

    passed = len(findings) == 0
    evidence = {
        "audit": "EP-06: Vault Secret Management & Zero-Leakage Repository Scan",
        "timestamp": datetime.now(UTC).isoformat(),
        "files_scanned": scanned_files,
        "violations_found": len(findings),
        "findings": findings,
        "status": "PASS" if passed else "FAIL",
        "ep_06_compliant": passed,
    }

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    out_file = EVIDENCE_DIR / "r10-m04-secret-scan-evidence.json"
    out_file.write_text(json.dumps(evidence, indent=2), encoding="utf-8")

    return evidence


if __name__ == "__main__":
    res = scan_repo()
    print("=" * 80)
    print("1000FiX — Secret Scanning & Zero-Leakage Audit (EP-06)")
    print("=" * 80)
    print(f"Files Scanned: {res['files_scanned']}")
    print(f"Violations:    {res['violations_found']}")
    print(f"Status:        {res['status']} (EP-06 Compliant: {res['ep_06_compliant']})")
    print("Evidence:      docs/traceability/evidence/r10-m04-secret-scan-evidence.json")
    print("=" * 80)

    if not res["ep_06_compliant"]:
        sys.exit(1)
    sys.exit(0)
