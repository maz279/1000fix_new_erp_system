#!/usr/bin/env python3
"""execute_financial_closure.py — Milestone R11-M04-T03: Programme Financial Closure.

Standard: GV-004 / GV-008 / CO-005 / IAS 38 Intangible Assets / ISO 21502:2020 §7.7
Governing finding: P12-M08-T01 / R11-M04-T03

GV-009: the previous version wrote an invented per-phase ledger (planned and
"actual measured" person-weeks for R01..R11), a blended rate reverse-engineered
to hit a $1,630,000 envelope that no committed artefact records, an invented
IAS 38 CapEx/OpEx split, a "FAVOURABLE_VARIANCE_BUDGET_CLOSED_UNDER_CEILING"
verdict, "FINANCIAL CLOSE UNANIMOUSLY APPROVED" text and three signatures.
Every status below is now computed in this run:

  EFFORT_BASELINE_SOURCE     CO-003-AMD-01 (docs/p01-m08/SoW-F08-signed-amendment.md)
                             is on disk and states the 1,842 PW baseline and the
                             1,850 PW / 331-unit register figure
  CD_REGISTER_RECONCILIATION the planned effort in tooling/cd-register.yaml (items
                             summed in this run) equals the amendment's register
                             figure, and its header count/pw_total match its items
  ACTUAL_EFFORT_BY_PHASE     needs the timesheet / effort ledger -> UNMEASURED
  ACTUAL_SPEND_AND_VARIANCE  needs the finance general ledger -> UNMEASURED
  IAS38_CAPITALISATION_SPLIT needs ledger classification + auditor review -> UNMEASURED
  FINANCIAL_SIGN_OFF         named signatures -> UNMEASURED

Emits:
- docs/traceability/evidence/r11-m04-programme-financial-close.json
- docs/traceability/r11-m04-programme-financial-close.md

Exit: 0 PASS / 1 FAIL / 2 INCOMPLETE (a check is UNMEASURED).
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = REPO_ROOT / "docs" / "traceability" / "evidence"
TRACEABILITY_DIR = REPO_ROOT / "docs" / "traceability"
AMENDMENT_DOC = REPO_ROOT / "docs" / "p01-m08" / "SoW-F08-signed-amendment.md"
CD_REGISTER = REPO_ROOT / "tooling" / "cd-register.yaml"

PASS, FAIL, UNMEASURED, INCOMPLETE = "PASS", "FAIL", "UNMEASURED", "INCOMPLETE"

# Contract figures (CO-003-AMD-01 Clause 2, CO-003 §6.3) - the targets under test.
CONTRACT_EFFORT_PW = 1842
AMENDMENT_REGISTER_PW = 1850
AMENDMENT_REGISTER_UNITS = 331

EFFORT_UNMEASURED = (
    "actual person-weeks per phase need the timesheet / effort ledger; no effort ledger "
    "is committed to the repository"
)
SPEND_UNMEASURED = (
    "actual spend, budget envelope, blended rate, FX rate and variance need the finance "
    "general ledger / programme cost centre; none is committed to the repository"
)
IAS38_UNMEASURED = (
    "the IAS 38 CapEx/OpEx split needs ledger cost classification and auditor review; "
    "neither is available to this tool"
)
SIGN_OFF_UNMEASURED = (
    "financial close sign-off (Finance Director, CEO, Audit Committee chair) is a "
    "named-person act a tool cannot observe"
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


def effort_source_check(path: Path) -> dict:
    if not path.is_file():
        return make_check("EFFORT_BASELINE_SOURCE", FAIL, f"{path.name} not found")
    text = path.read_text(encoding="utf-8", errors="replace")
    figures = [
        f"{CONTRACT_EFFORT_PW:,}",
        f"{AMENDMENT_REGISTER_PW:,}",
        str(AMENDMENT_REGISTER_UNITS),
    ]
    missing = [fig for fig in figures if fig not in text]
    if missing:
        return make_check("EFFORT_BASELINE_SOURCE", FAIL, f"{path.name} does not state {missing}")
    return make_check(
        "EFFORT_BASELINE_SOURCE",
        PASS,
        f"{path.name} states {CONTRACT_EFFORT_PW:,} PW baseline and {AMENDMENT_REGISTER_PW:,} PW "
        f"across {AMENDMENT_REGISTER_UNITS} register units",
    )


def load_cd_register(path: Path) -> tuple[dict | None, str | None]:
    if not path.is_file():
        return None, f"{path.name} not found"
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        return None, f"{path.name} unreadable: {exc}"
    if not isinstance(data, dict) or not isinstance(data.get("items"), list):
        return None, f"{path.name} has no 'items' list"
    return data, None


def planned_pw_by_wave(items: list[dict]) -> dict[str, int]:
    waves: dict[str, int] = {}
    for item in items:
        wave = str(item.get("wave") or "<none>")
        pw = item.get("pw")
        waves[wave] = waves.get(wave, 0) + (pw if isinstance(pw, int) else 0)
    return dict(sorted(waves.items()))


def register_reconciliation_check(data: dict | None, error: str | None) -> dict:
    if data is None:
        return make_check("CD_REGISTER_RECONCILIATION", FAIL, error or "register missing")
    items = [i for i in data["items"] if isinstance(i, dict)]
    bad_pw = [i.get("id") for i in items if not isinstance(i.get("pw"), int)]
    units = len(items)
    total_pw = sum(i["pw"] for i in items if isinstance(i.get("pw"), int))
    problems = []
    if bad_pw:
        problems.append(f"{len(bad_pw)} items without an integer pw: {bad_pw[:5]}")
    if data.get("count") != units or data.get("pw_total") != total_pw:
        problems.append(
            f"header count={data.get('count')} pw_total={data.get('pw_total')} vs items "
            f"{units} / {total_pw} PW"
        )
    if total_pw != AMENDMENT_REGISTER_PW or units != AMENDMENT_REGISTER_UNITS:
        problems.append(
            f"register carries {total_pw} PW across {units} units vs CO-003-AMD-01 "
            f"{AMENDMENT_REGISTER_PW} PW / {AMENDMENT_REGISTER_UNITS} units "
            f"(delta {total_pw - AMENDMENT_REGISTER_PW:+d} PW, "
            f"{units - AMENDMENT_REGISTER_UNITS:+d} units) - unreconciled to the contract"
        )
    detail = (
        "; ".join(problems)
        if problems
        else f"register items sum to {total_pw} PW across {units} units = CO-003-AMD-01"
    )
    return make_check(
        "CD_REGISTER_RECONCILIATION",
        FAIL if problems else PASS,
        detail,
        register_units=units,
        register_planned_pw=total_pw,
        contract_baseline_pw=CONTRACT_EFFORT_PW,
        amendment_register_pw=AMENDMENT_REGISTER_PW,
        amendment_register_units=AMENDMENT_REGISTER_UNITS,
    )


def compute_financial_closure(
    *, amendment_doc: Path = AMENDMENT_DOC, cd_register: Path = CD_REGISTER
) -> dict:
    data, error = load_cd_register(cd_register)
    items = [i for i in (data or {}).get("items", []) if isinstance(i, dict)]
    checks = [
        effort_source_check(amendment_doc),
        register_reconciliation_check(data, error),
        make_check("ACTUAL_EFFORT_BY_PHASE", UNMEASURED, EFFORT_UNMEASURED),
        make_check("ACTUAL_SPEND_AND_VARIANCE", UNMEASURED, SPEND_UNMEASURED),
        make_check("IAS38_CAPITALISATION_SPLIT", UNMEASURED, IAS38_UNMEASURED),
        make_check("FINANCIAL_SIGN_OFF", UNMEASURED, SIGN_OFF_UNMEASURED),
    ]
    return {
        "$schema": "1000fix-erp/financial-closure/2",
        "standard": "GV-004 / GV-008 / CO-005 / IAS 38 Intangible Assets",
        "milestone": "R11-M04",
        "task": "R11-M04-T03",
        "closure_timestamp": datetime.now(UTC).isoformat(),
        "planned_effort": {
            "contract_baseline_pw": CONTRACT_EFFORT_PW,
            "register_planned_pw": sum(planned_pw_by_wave(items).values()) if items else None,
            "register_units": len(items) if items else None,
            "register_planned_pw_by_wave": planned_pw_by_wave(items) if items else {},
        },
        "actuals": {
            "actual_effort_pw": None,
            "actual_spend": None,
            "status": UNMEASURED,
            "detail": SPEND_UNMEASURED,
        },
        "checks": checks,
        "summary": {
            "checks_passed": sum(1 for c in checks if c["status"] == PASS),
            "checks_failed": sum(1 for c in checks if c["status"] == FAIL),
            "checks_unmeasured": sum(1 for c in checks if c["status"] == UNMEASURED),
            "financial_verdict": overall_verdict(checks),
        },
    }


def render_markdown(report: dict) -> str:
    planned = report["planned_effort"]
    lines = [
        "# Programme Financial Close Statement — Milestone R11-M04-T03",
        "## 1000FiX ERP System v2.0 · GV-008 / IAS 38",
        "",
        "Generated by `tooling/scripts/execute_financial_closure.py` at "
        f"{report['closure_timestamp']}. Every status below is computed in that run.",
        "",
        f"**Financial verdict: {report['summary']['financial_verdict']}**",
        "",
        "| Item | Value |",
        "|---|---|",
        f"| Contract effort baseline (CO-003-AMD-01) | {planned['contract_baseline_pw']:,} PW |",
        f"| Planned effort in `cd-register.yaml` (summed) | {planned['register_planned_pw']} PW "
        f"across {planned['register_units']} units |",
        f"| Actual effort / spend | {report['actuals']['status']} |",
        "",
        "## Checks",
        "",
        "| Check | Status | Detail |",
        "|---|:---:|---|",
    ]
    lines += [f"| `{c['id']}` | {c['status']} | {c['detail']} |" for c in report["checks"]]
    lines += [
        "",
        "## Planned effort by wave (cd-register.yaml)",
        "",
        "| Wave | Planned PW |",
        "|---|---:|",
    ]
    lines += [f"| {w} | {pw} |" for w, pw in planned["register_planned_pw_by_wave"].items()]
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    print("=" * 76)
    print("1000FiX ERP — Task R11-M04-T03: Programme Financial Closure")
    print("=" * 76)
    report = compute_financial_closure()
    for check in report["checks"]:
        print(f"  [{check['status']}] {check['id']}: {check['detail']}")

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    json_path = EVIDENCE_DIR / "r11-m04-programme-financial-close.json"
    json_path.write_bytes((json.dumps(report, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
    TRACEABILITY_DIR.mkdir(parents=True, exist_ok=True)
    md_path = TRACEABILITY_DIR / "r11-m04-programme-financial-close.md"
    md_path.write_bytes(render_markdown(report).encode("utf-8"))

    print(f"\nFinancial verdict: {report['summary']['financial_verdict']}")
    print(f"[OK] Financial close evidence JSON written: {json_path}")
    print(f"[OK] Financial close statement written: {md_path}")
    return exit_code(report["summary"]["financial_verdict"])


if __name__ == "__main__":
    raise SystemExit(main())
