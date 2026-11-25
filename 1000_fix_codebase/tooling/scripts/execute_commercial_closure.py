#!/usr/bin/env python3
"""execute_commercial_closure.py — Milestone R11-M04-T02: Commercial Closure against SoW Baseline.

Standard: CO-003 / CO-003-AMD-01 / B-11 Settlement / ISO 21502:2020 §7.10
Governing finding: P12-M08-T06 / R11-M04-T02

GV-009: the previous version wrote fourteen invented change requests
("CR-01".."CR-14", each a literal "APPROVED_AND_MERGED" - in this repository
CR-01..CR-03 are counting rules, not change requests), "3,389/3,389 delivered",
four vendor settlements with invented shred certificates and savings, a
"COMMERCIAL_AND_CONTRACTUAL_CLOSURE_UNANIMOUSLY_APPROVED" verdict and three
signatures. Every status below is now computed in this run:

  AMENDMENT_ON_DISK          docs/p01-m08/SoW-F08-signed-amendment.md exists and
                             cites the contracted 3,389 / 122 baseline
  SCOPE_BASELINE_MATCHES     the latest requirements-baseline scan evidence measures
                             the same 3,389 requirements / 122 NFRs
  REQUIREMENTS_ACCEPTANCE    per-requirement acceptance recorded in the committed RTM
                             (docs/p01-m03/registers/rtm-seed.csv)
  NFR_ACCEPTANCE             no per-NFR acceptance register is committed -> UNMEASURED
  CHANGE_REQUEST_DISPOSITION every CR document under docs/ (CR-*.md) records a closed
                             disposition (approved / ratified / rejected / withdrawn)
  VENDOR_SETTLEMENTS         vendor contract terminations, final invoices and
                             retainage need commercial records -> UNMEASURED
  CONTRACT_SIGNATURES        named signatures on the amendment and closure -> UNMEASURED

Emits:
- docs/traceability/evidence/r11-m04-commercial-closure-statement.json
- docs/traceability/r11-m04-commercial-closure-statement.md

Exit: 0 PASS / 1 FAIL / 2 INCOMPLETE (a check is UNMEASURED).
"""

from __future__ import annotations

import csv
import json
import re
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = REPO_ROOT / "docs" / "traceability" / "evidence"
TRACEABILITY_DIR = REPO_ROOT / "docs" / "traceability"
DOCS_DIR = REPO_ROOT / "docs"
AMENDMENT_DOC = DOCS_DIR / "p01-m08" / "SoW-F08-signed-amendment.md"
BASELINE_EVIDENCE_DIR = REPO_ROOT / "tooling" / "requirements-baseline" / "evidence"
RTM_CSV = DOCS_DIR / "p01-m03" / "registers" / "rtm-seed.csv"

PASS, FAIL, UNMEASURED, INCOMPLETE = "PASS", "FAIL", "UNMEASURED", "INCOMPLETE"

# Contracted baseline (CO-003-AMD-01 Clause 1) - the target under test.
CONTRACT_FUNCTIONAL_REQUIREMENTS = 3389
CONTRACT_NFRS = 122

ACCEPTED_RTM_STATUSES = {"accepted", "verified", "delivered", "passed", "closed"}
CLOSED_CR_WORDS = ("APPROVED", "RATIFIED", "ACCEPTED", "REJECTED", "WITHDRAWN", "CLOSED")
OPEN_CR_WORDS = ("PROPOSED", "PENDING", "DRAFT", "OPEN", "RAISED", "UNDER REVIEW")

CR_ID_ROW = re.compile(
    r"^\|\s*\**CR id\**\s*\|\s*`?([A-Za-z0-9][A-Za-z0-9-]*)", re.IGNORECASE | re.MULTILINE
)
CR_HEADING = re.compile(r"^#\s+(CR-[A-Z0-9-]+)", re.MULTILINE)
STATUS_ROW = re.compile(r"^\|\s*\**Status\**\s*\|\s*([^|]+)\|", re.IGNORECASE | re.MULTILINE)

NFR_UNMEASURED = (
    "no per-NFR acceptance register is committed; acceptance of the 122 NFRs needs the "
    "signed acceptance records"
)
VENDOR_UNMEASURED = (
    "vendor contract terminations, final invoices, retainage release and data-destruction "
    "certificates live in commercial/finance records, none of which are committed"
)
SIGNATURE_UNMEASURED = (
    "execution of CO-003-AMD-01 and the closure sign-off are named-person acts a tool "
    "cannot observe (P01-M08 records the amendment signature as external)"
)


def make_check(check_id: str, status: str, detail: str, **measured: object) -> dict:
    return {"id": check_id, "status": status, "detail": detail, **measured}


def overall_verdict(checks: list[dict]) -> str:
    statuses = {check["status"] for check in checks}
    if not statuses:
        return INCOMPLETE
    if FAIL in statuses:
        return FAIL
    return PASS if statuses == {PASS} else INCOMPLETE


def exit_code(verdict: str) -> int:
    return {PASS: 0, FAIL: 1}.get(verdict, 2)


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix() if path.is_relative_to(root) else path.as_posix()


def amendment_check(path: Path) -> dict:
    if not path.is_file():
        return make_check("AMENDMENT_ON_DISK", FAIL, f"{path.name} not found")
    text = path.read_text(encoding="utf-8", errors="replace")
    wanted = {f"{CONTRACT_FUNCTIONAL_REQUIREMENTS:,}": "requirements", f"{CONTRACT_NFRS}": "NFRs"}
    missing = [f"{fig} {what}" for fig, what in wanted.items() if fig not in text]
    if missing:
        return make_check("AMENDMENT_ON_DISK", FAIL, f"{path.name} does not cite {missing}")
    return make_check(
        "AMENDMENT_ON_DISK",
        PASS,
        f"{path.name} on disk and cites {CONTRACT_FUNCTIONAL_REQUIREMENTS:,} requirements / "
        f"{CONTRACT_NFRS} NFRs (an on-disk amendment is not proof of execution)",
    )


def latest_baseline_evidence(directory: Path) -> Path | None:
    files = sorted(directory.glob("requirements-baseline-*.json")) if directory.is_dir() else []
    return files[-1] if files else None


def scope_baseline_check(directory: Path) -> dict:
    path = latest_baseline_evidence(directory)
    if path is None:
        return make_check(
            "SCOPE_BASELINE_MATCHES",
            UNMEASURED,
            "no requirements-baseline scan evidence found; run "
            "tooling/requirements-baseline/scan-requirements.ps1",
        )
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        population = data["denominator"]["population"]
        nfrs = data["nfr"]["unique"]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return make_check("SCOPE_BASELINE_MATCHES", FAIL, f"{path.name} unreadable: {exc!r}")
    ok = population == CONTRACT_FUNCTIONAL_REQUIREMENTS and nfrs == CONTRACT_NFRS
    return make_check(
        "SCOPE_BASELINE_MATCHES",
        PASS if ok else FAIL,
        f"{path.name} measured {population} requirements / {nfrs} NFRs vs contracted "
        f"{CONTRACT_FUNCTIONAL_REQUIREMENTS} / {CONTRACT_NFRS}",
        measured_requirements=population,
        measured_nfrs=nfrs,
        scan_ran_at=data.get("ranAtUtc"),
    )


def requirements_acceptance_check(rtm_path: Path) -> dict:
    if not rtm_path.is_file():
        return make_check(
            "REQUIREMENTS_ACCEPTANCE",
            UNMEASURED,
            f"{rtm_path.name} not found; no per-requirement acceptance record to read",
        )
    with rtm_path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    statuses: dict[str, int] = {}
    for row in rows:
        status = (row.get("status") or "").strip().lower() or "<blank>"
        statuses[status] = statuses.get(status, 0) + 1
    accepted = sum(n for s, n in statuses.items() if s in ACCEPTED_RTM_STATUSES)
    untracked = CONTRACT_FUNCTIONAL_REQUIREMENTS - len(rows)
    detail = (
        f"{rtm_path.name}: {accepted} of {len(rows)} rows record acceptance "
        f"(statuses {dict(sorted(statuses.items()))}); {max(untracked, 0)} of the "
        f"{CONTRACT_FUNCTIONAL_REQUIREMENTS:,} contracted requirements are not in the RTM"
    )
    if accepted < len(rows):
        status = FAIL
    elif untracked > 0:
        status = UNMEASURED
    else:
        status = PASS
    return make_check(
        "REQUIREMENTS_ACCEPTANCE",
        status,
        detail,
        rtm_rows=len(rows),
        rtm_rows_accepted=accepted,
        rtm_status_counts=dict(sorted(statuses.items())),
    )


def classify_cr_status(text: str | None) -> str:
    if text is None:
        return "NO_RECORDED_DISPOSITION"
    upper = text.upper()
    if any(word in upper for word in OPEN_CR_WORDS):
        return "OPEN"
    if any(word in upper for word in CLOSED_CR_WORDS):
        return "DISPOSITIONED"
    return "UNRECOGNISED_STATUS"


def parse_cr_document(path: Path, root: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    id_match = CR_ID_ROW.search(text) or CR_HEADING.search(text)
    status_match = STATUS_ROW.search(text)
    raw_status = (
        status_match.group(1).replace("*", "").replace("`", "").strip() if status_match else None
    )
    return {
        "cr_id": id_match.group(1).strip() if id_match else path.stem,
        "document": rel(path, root),
        "recorded_status": raw_status,
        "disposition": classify_cr_status(raw_status),
    }


def change_request_check(docs_dir: Path, root: Path) -> tuple[dict, list[dict]]:
    paths = sorted(docs_dir.rglob("CR-*.md")) if docs_dir.is_dir() else []
    items = [parse_cr_document(p, root) for p in paths]
    if not items:
        return (
            make_check(
                "CHANGE_REQUEST_DISPOSITION", UNMEASURED, "no CR-*.md documents under docs/"
            ),
            items,
        )
    not_closed = [i for i in items if i["disposition"] != "DISPOSITIONED"]
    detail = (
        f"{len(items) - len(not_closed)} of {len(items)} CR documents record a closed disposition"
    )
    if not_closed:
        detail += "; not closed: " + ", ".join(
            f"{i['cr_id']} ({i['disposition']})" for i in not_closed
        )
    return (
        make_check(
            "CHANGE_REQUEST_DISPOSITION",
            FAIL if not_closed else PASS,
            detail,
            change_requests_found=len(items),
            change_requests_dispositioned=len(items) - len(not_closed),
        ),
        items,
    )


def audit_commercial_closure(
    *,
    root: Path = REPO_ROOT,
    docs_dir: Path = DOCS_DIR,
    amendment_doc: Path = AMENDMENT_DOC,
    baseline_dir: Path = BASELINE_EVIDENCE_DIR,
    rtm_csv: Path = RTM_CSV,
) -> dict:
    cr_check, cr_items = change_request_check(docs_dir, root)
    checks = [
        amendment_check(amendment_doc),
        scope_baseline_check(baseline_dir),
        requirements_acceptance_check(rtm_csv),
        make_check("NFR_ACCEPTANCE", UNMEASURED, NFR_UNMEASURED),
        cr_check,
        make_check("VENDOR_SETTLEMENTS", UNMEASURED, VENDOR_UNMEASURED),
        make_check("CONTRACT_SIGNATURES", UNMEASURED, SIGNATURE_UNMEASURED),
    ]
    return {
        "$schema": "1000fix-erp/commercial-closure/2",
        "standard": "CO-003 / CO-003-AMD-01 / B-11 Settlement / ISO 21502:2020 §7.10",
        "milestone": "R11-M04",
        "task": "R11-M04-T02",
        "closure_timestamp": datetime.now(UTC).isoformat(),
        "contracted_baseline": {
            "functional_requirements": CONTRACT_FUNCTIONAL_REQUIREMENTS,
            "nfrs": CONTRACT_NFRS,
            "source": rel(amendment_doc, root),
        },
        "checks": checks,
        "change_requests": {
            "total_found": len(cr_items),
            "dispositioned": sum(1 for i in cr_items if i["disposition"] == "DISPOSITIONED"),
            "not_dispositioned": sum(1 for i in cr_items if i["disposition"] != "DISPOSITIONED"),
            "items": cr_items,
        },
        "summary": {
            "checks_passed": sum(1 for c in checks if c["status"] == PASS),
            "checks_failed": sum(1 for c in checks if c["status"] == FAIL),
            "checks_unmeasured": sum(1 for c in checks if c["status"] == UNMEASURED),
        },
        "commercial_verdict": overall_verdict(checks),
    }


def render_markdown(report: dict) -> str:
    lines = [
        "# Commercial Closure Statement — Milestone R11-M04-T02",
        "## 1000FiX ERP System v2.0 · CO-003 / CO-003-AMD-01",
        "",
        "Generated by `tooling/scripts/execute_commercial_closure.py` at "
        f"{report['closure_timestamp']}. Every status below is computed in that run.",
        "",
        f"**Commercial verdict: {report['commercial_verdict']}**",
        "",
        "## Checks",
        "",
        "| Check | Status | Detail |",
        "|---|:---:|---|",
    ]
    lines += [f"| `{c['id']}` | {c['status']} | {c['detail']} |" for c in report["checks"]]
    lines += [
        "",
        "## Change requests found under docs/",
        "",
        "| CR | Document | Recorded status | Disposition |",
        "|---|---|---|:---:|",
    ]
    lines += [
        f"| {i['cr_id']} | `{i['document']}` | {i['recorded_status'] or '—'} | {i['disposition']} |"
        for i in report["change_requests"]["items"]
    ]
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    print("=" * 76)
    print("1000FiX ERP — Task R11-M04-T02: Commercial Closure against SoW Baseline")
    print("=" * 76)
    report = audit_commercial_closure()
    for check in report["checks"]:
        print(f"  [{check['status']}] {check['id']}: {check['detail']}")

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    json_path = EVIDENCE_DIR / "r11-m04-commercial-closure-statement.json"
    json_path.write_bytes((json.dumps(report, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
    TRACEABILITY_DIR.mkdir(parents=True, exist_ok=True)
    md_path = TRACEABILITY_DIR / "r11-m04-commercial-closure-statement.md"
    md_path.write_bytes(render_markdown(report).encode("utf-8"))

    print(f"\nCommercial verdict: {report['commercial_verdict']}")
    print(f"[OK] Commercial evidence JSON written: {json_path}")
    print(f"[OK] Commercial closure statement written: {md_path}")
    return exit_code(report["commercial_verdict"])


if __name__ == "__main__":
    raise SystemExit(main())
