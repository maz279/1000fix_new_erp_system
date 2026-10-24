#!/usr/bin/env python3
"""test_clone_with_masking.py — Validation of In-Stream Sovereign Masking (NFR-086c).

Checks, each against clone_with_masking.mask_stream_chunk / process_stream:
1. 10, 13 and 17-digit Bangladesh NID numbers are replaced by masked tokens.
2. Mobile numbers (+8801... / 01...) are replaced with synthetic test numbers.
3. Personal email addresses are replaced with anonymised internal aliases.
4. MFS wallet numbers (bKash/Nagad) are replaced with masked tokens.
5. Bank account numbers are replaced with masked tokens.
6. A simulated SQL dump streamed through process_stream reaches the output
   stream with no raw PII value and no residual PII pattern match.

GV-009: every check is evaluated explicitly (no `assert`, so `python -O` cannot
skip it); the evidence status, checked types and compliance flags are computed
from the checks of this run. Exit: 0 PASS / 1 FAIL.

Emits docs/traceability/evidence/r10-m04-clone-masking-evidence.json
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from io import StringIO
from pathlib import Path

# Add tooling/dr to path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from clone_with_masking import mask_stream_chunk, process_stream

REPO_ROOT = HERE.parents[1]
EVIDENCE_DIR = REPO_ROOT / "docs" / "traceability" / "evidence"
EVIDENCE_FILE = "r10-m04-clone-masking-evidence.json"

PASS, FAIL = "PASS", "FAIL"

# (PII type, sample input, raw values that must not survive, placeholder that must appear)
MASKING_CASES: tuple[tuple[str, str, tuple[str, ...], str], ...] = (
    (
        "NID_10",
        "INSERT INTO res_partner VALUES (1, '7352849102');",
        ("7352849102",),
        "BD-NID-MASKED-",
    ),
    (
        "NID_13",
        "INSERT INTO res_partner VALUES (4, '1985269251800');",
        ("1985269251800",),
        "BD-NID-MASKED-",
    ),
    (
        "NID_17",
        "INSERT INTO res_partner VALUES (2, '19852692518000123');",
        ("19852692518000123",),
        "BD-NID-MASKED-",
    ),
    (
        "MOBILE_BD",
        "Mobile: +8801712345678 and 01898765432",
        ("+8801712345678", "01898765432"),
        "+880170000",
    ),
    (
        "EMAIL",
        "Contact: rahim.uddin@gmail.com and fatima.begum@yahoo.com",
        ("rahim.uddin@gmail.com", "fatima.begum@yahoo.com"),
        "@masked.1000fix.internal",
    ),
    ("MFS_WALLET", "Payout: bkash-01711223344", ("bkash-01711223344",), "MFS-WALLET-"),
    ("BANK_ACC", "Settlement account: 20501234567890", ("20501234567890",), "BANK-ACC-"),
)

SAMPLE_DUMP = (
    "-- PostgreSQL database dump\n",
    "SET statement_timeout = 0;\n",
    "COPY res_partner (id, name, nid_number, mobile, email, bkash_wallet) FROM stdin;\n",
    "101\tTanvir Ahmed\t19902692518000456\t+8801712345678\ttanvir.ahmed@dhakarepair.com\tbkash-01712345678\n",
    "102\tNusrat Jahan\t8492018472\t01823456789\tnusrat.jahan@gmail.com\tbkash-01823456789\n",
    "103\tKazi Nazrul\t19762692518000789\t01934567890\tnazrul.kazi@outlook.com\tbkash-01934567890\n",
    "\\.\n",
    "-- Data completed\n",
)
SAMPLE_DUMP_RAW_PII = (
    "19902692518000456",
    "8492018472",
    "19762692518000789",
    "+8801712345678",
    "01823456789",
    "01934567890",
    "tanvir.ahmed@dhakarepair.com",
    "nusrat.jahan@gmail.com",
    "nazrul.kazi@outlook.com",
    "bkash-01712345678",
)
SAMPLE_DUMP_PLACEHOLDERS = (
    "BD-NID-MASKED-",
    "+880170000",
    "@masked.1000fix.internal",
    "MFS-WALLET-",
)
SAMPLE_DUMP_EXPECTED_LINES = len(SAMPLE_DUMP)
SAMPLE_DUMP_EXPECTED_MASKED = 3  # the three COPY data rows


def _check(check_id: str, leaked: list[str], problems: list[str], detail: str) -> dict:
    problems = [f"raw value {raw!r} leaked" for raw in leaked] + problems
    return {
        "id": check_id,
        "status": FAIL if problems else PASS,
        "leaked_values": len(leaked),
        "detail": "; ".join(problems) if problems else detail,
    }


def run_masking_checks() -> list[dict]:
    """One check per PII type: raw values gone, placeholder present."""
    checks = []
    for pii_type, sample, raw_values, placeholder in MASKING_CASES:
        masked = mask_stream_chunk(sample)
        leaked = [raw for raw in raw_values if raw in masked]
        problems = (
            []
            if placeholder in masked
            else [f"placeholder {placeholder!r} missing from {masked!r}"]
        )
        checks.append(_check(pii_type, leaked, problems, f"masked to {masked!r}"))
    return checks


def run_stream_check() -> tuple[dict, dict]:
    """Stream a simulated SQL dump through process_stream; return (check, stats)."""
    output = StringIO()
    stats = process_stream(StringIO("".join(SAMPLE_DUMP)), output)
    text = output.getvalue()
    leaked = [raw for raw in SAMPLE_DUMP_RAW_PII if raw in text]
    problems = [f"placeholder {p!r} missing" for p in SAMPLE_DUMP_PLACEHOLDERS if p not in text]
    if stats["lines_processed"] != SAMPLE_DUMP_EXPECTED_LINES:
        problems.append(
            f"lines_processed {stats['lines_processed']} != {SAMPLE_DUMP_EXPECTED_LINES}"
        )
    if stats["lines_masked"] != SAMPLE_DUMP_EXPECTED_MASKED:
        problems.append(f"lines_masked {stats['lines_masked']} != {SAMPLE_DUMP_EXPECTED_MASKED}")
    if stats["residual_pii_lines"]:
        problems.append(f"{stats['residual_pii_lines']} output line(s) still match a PII pattern")
    detail = (
        f"{stats['lines_processed']} lines streamed, {stats['lines_masked']} masked, "
        f"{len(leaked)} raw PII values and {stats['residual_pii_lines']} residual PII lines in the output"
    )
    return _check("SQL_DUMP_STREAM", leaked, problems, detail), stats


def build_evidence() -> dict:
    type_checks = run_masking_checks()
    stream_check, stats = run_stream_check()
    checks = [*type_checks, stream_check]
    passed = all(c["status"] == PASS for c in checks)
    return {
        "test": "R10-M04-T02: In-Stream Sovereign Masking (NFR-086c)",
        "timestamp": datetime.now(UTC).isoformat(),
        "status": PASS if passed else FAIL,
        "lines_processed": stats["lines_processed"],
        "lines_masked": stats["lines_masked"],
        "residual_pii_lines": stats["residual_pii_lines"],
        "sovereign_pii_zero_leakage": (
            sum(c["leaked_values"] for c in checks) == 0 and stats["residual_pii_lines"] == 0
        ),
        "nfr_086c_compliant": passed,
        "checked_types": [c["id"] for c in type_checks],
        "failed_checks": [c["id"] for c in checks if c["status"] == FAIL],
        "checks": checks,
    }


def _raise_on_failures(checks: list[dict]) -> None:
    failed = [f"{c['id']}: {c['detail']}" for c in checks if c["status"] == FAIL]
    if failed:
        raise AssertionError("; ".join(failed))


def test_individual_masking_rules():
    _raise_on_failures(run_masking_checks())


def test_full_stream_sql_dump_simulation():
    _raise_on_failures([run_stream_check()[0]])


def main() -> int:
    evidence = build_evidence()
    for check in evidence["checks"]:
        print(f"[{check['status']}] {check['id']}: {check['detail']}")
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    out_file = EVIDENCE_DIR / EVIDENCE_FILE
    out_file.write_bytes((json.dumps(evidence, indent=2) + "\n").encode("utf-8"))
    print(f"NFR-086c in-stream masking: {evidence['status']}")
    print(f"Evidence recorded in {out_file}")
    return 0 if evidence["status"] == PASS else 1


if __name__ == "__main__":
    sys.exit(main())
