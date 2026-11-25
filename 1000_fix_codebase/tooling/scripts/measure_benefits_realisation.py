#!/usr/bin/env python3
"""measure_benefits_realisation.py — Milestone R11-M04-T01: Benefits Measurement against BM-002.

Standard: BM-002 .. BM-005 / ISO 21502:2020 §7.13 / ISO/IEC/IEEE 15939:2017
Governing finding: P12-M08-T01 / R11-M04-T01

GV-009: the previous version wrote eight invented KPI rows ("measured" actuals
such as 73.8% automation and BDT 81.22M monthly revenue, each "EXCEEDED"), two
"PROMISE_FULFILLED" literals, a "BENEFITS_REALISATION_SUBSTANTIATED_AND_VERIFIED"
verdict and three executive signatures. Its KPI ids did not even match the
committed register (KPI-010 there is "Walk-in intake time", not revenue). Every
status below is now computed in this run:

  BM002_REGISTER_INTEGRITY  services/bi-warehouse/kpi-register.json loads, its row
                            count equals total_registered and the BM-002
                            reconciliation count, and every KPI id is unique
  PROMISE_AUTOMATION_70     the 70% automation promise maps to a registered KPI
                            (baseline/target read from the register); its
                            production actual -> UNMEASURED
  PROMISE_REVENUE_GROWTH_87 no registered KPI carries the revenue-growth promise;
                            it needs the finance revenue ledger -> UNMEASURED
  KPI_PRODUCTION_ACTUALS    actuals for every registered KPI come from the BI
                            warehouse fact tables on production, which never
                            reach a workstation (DE-12) -> UNMEASURED
  BENEFITS_SIGN_OFF         named executive sign-off -> UNMEASURED

Emits:
- docs/traceability/evidence/r11-m04-benefits-realisation-report.json
- docs/traceability/r11-m04-benefits-realisation-report.md

Exit: 0 PASS / 1 FAIL / 2 INCOMPLETE (a check is UNMEASURED).
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_DIR = REPO_ROOT / "docs" / "traceability" / "evidence"
TRACEABILITY_DIR = REPO_ROOT / "docs" / "traceability"
KPI_REGISTER = REPO_ROOT / "services" / "bi-warehouse" / "kpi-register.json"

PASS, FAIL, UNMEASURED, INCOMPLETE = "PASS", "FAIL", "UNMEASURED", "INCOMPLETE"

# Business-case promises (the targets under test, not measurements).
AUTOMATION_PROMISE_PCT = 70.0
REVENUE_GROWTH_PROMISE_PCT = 87.0
AUTOMATION_KPI_NAME_HINT = "automation of routine work"

# Baseline values in the register that are not a recorded measurement.
NON_NUMERIC_BASELINES = {"unmeasured", "n/a", "unknown", "untracked", "manual", "baseline", ""}

ACTUALS_UNMEASURED = (
    "production actuals come from the BI warehouse fact tables (fact_service_orders, "
    "fact_invoices, ...) on the production read-replica; production data never reaches "
    "a workstation (DE-12), so no actual can be measured here"
)
REVENUE_UNMEASURED = (
    "no KPI in kpi-register.json carries the 87% revenue-growth promise; measuring it "
    "requires the audited finance revenue ledger for the baseline and current periods"
)
SIGN_OFF_UNMEASURED = (
    "executive sign-off (CFO, CEO, Programme Director) is a human act a tool cannot observe"
)
REQUIRED_SIGNATORY_ROLES = (
    "Chief Financial Officer (CFO)",
    "Chief Executive Officer (CEO)",
    "Programme Director",
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


def load_register(path: Path) -> tuple[dict | None, str | None]:
    if not path.is_file():
        return None, f"{path.name} not found"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return None, f"{path.name} unreadable: {exc}"
    if not isinstance(data, dict) or not isinstance(data.get("register"), list):
        return None, f"{path.name} has no 'register' list"
    return data, None


def register_integrity_check(data: dict | None, error: str | None) -> dict:
    if data is None:
        return make_check("BM002_REGISTER_INTEGRITY", FAIL, error or "register missing")
    rows = data["register"]
    ids = [row.get("kpi") for row in rows if isinstance(row, dict)]
    declared = data.get("total_registered")
    reconciled = (data.get("reconciliation_bm002") or {}).get("registered_count")
    duplicates = sorted({kpi for kpi in ids if ids.count(kpi) > 1 and kpi})
    problems = []
    if len(ids) != len(rows) or None in ids:
        problems.append("rows without a 'kpi' id")
    if declared != len(rows):
        problems.append(f"total_registered={declared} but {len(rows)} rows")
    if reconciled != len(rows):
        problems.append(f"reconciliation_bm002.registered_count={reconciled} but {len(rows)} rows")
    if duplicates:
        problems.append(f"duplicate ids {duplicates}")
    detail = (
        f"{len(rows)} registered KPIs; " + "; ".join(problems)
        if problems
        else f"{len(rows)} registered KPIs = total_registered = BM-002 reconciliation count; ids unique"
    )
    return make_check(
        "BM002_REGISTER_INTEGRITY",
        FAIL if problems else PASS,
        detail,
        registered_rows=len(rows),
        declared_total=declared,
        reconciliation_count=reconciled,
    )


def has_recorded_baseline(row: dict) -> bool:
    return str(row.get("baseline", "")).strip().lower() not in NON_NUMERIC_BASELINES


def find_automation_kpi(rows: list[dict]) -> dict | None:
    for row in rows:
        if AUTOMATION_KPI_NAME_HINT in str(row.get("name", "")).lower():
            return row
    return None


def promise_checks(rows: list[dict]) -> list[dict]:
    automation = find_automation_kpi(rows)
    if automation is None:
        auto_check = make_check(
            "PROMISE_AUTOMATION_70",
            FAIL,
            f"no registered KPI named '*{AUTOMATION_KPI_NAME_HINT}*' carries the "
            f"{AUTOMATION_PROMISE_PCT:g}% automation promise",
            promised_pct=AUTOMATION_PROMISE_PCT,
        )
    else:
        auto_check = make_check(
            "PROMISE_AUTOMATION_70",
            UNMEASURED,
            f"{automation['kpi']} '{automation.get('name')}' (register baseline "
            f"{automation.get('baseline')}, W4 target {automation.get('w4_target')}); "
            + ACTUALS_UNMEASURED,
            promised_pct=AUTOMATION_PROMISE_PCT,
            register_kpi=automation["kpi"],
            register_baseline=automation.get("baseline"),
            register_w4_target=automation.get("w4_target"),
            register_w8_target=automation.get("w8_target"),
            measured_actual=None,
        )
    revenue_check = make_check(
        "PROMISE_REVENUE_GROWTH_87",
        UNMEASURED,
        REVENUE_UNMEASURED,
        promised_growth_pct=REVENUE_GROWTH_PROMISE_PCT,
        measured_actual=None,
    )
    return [auto_check, revenue_check]


def kpi_rows(rows: list[dict]) -> list[dict]:
    return [
        {
            "kpi_id": row.get("kpi"),
            "name": row.get("name"),
            "family": row.get("family"),
            "register_baseline": row.get("baseline"),
            "baseline_recorded": has_recorded_baseline(row),
            "w4_target": row.get("w4_target"),
            "w8_target": row.get("w8_target"),
            "source": row.get("source"),
            "measured_production_actual": None,
            "status": UNMEASURED,
        }
        for row in rows
        if isinstance(row, dict)
    ]


def measure_benefits(register_path: Path = KPI_REGISTER) -> dict:
    data, error = load_register(register_path)
    rows = [row for row in (data or {}).get("register", []) if isinstance(row, dict)]
    metrics = kpi_rows(rows)
    with_baseline = sum(1 for m in metrics if m["baseline_recorded"])
    checks = [register_integrity_check(data, error), *promise_checks(rows)]
    checks.append(
        make_check(
            "KPI_PRODUCTION_ACTUALS",
            UNMEASURED,
            f"0 of {len(metrics)} registered KPIs have a measured production actual; "
            + ACTUALS_UNMEASURED,
            kpis_registered=len(metrics),
            kpis_with_recorded_baseline=with_baseline,
            kpis_with_measured_actual=0,
        )
    )
    checks.append(make_check("BENEFITS_SIGN_OFF", UNMEASURED, SIGN_OFF_UNMEASURED))
    verdict = overall_verdict(checks)
    return {
        "$schema": "1000fix-erp/benefits-realisation/2",
        "standard": "BM-002 .. BM-005 / ISO 21502:2020 §7.13 / MSP 5th Ed",
        "milestone": "R11-M04",
        "task": "R11-M04-T01",
        "measurement_timestamp": datetime.now(UTC).isoformat(),
        "baseline_source": register_path.relative_to(REPO_ROOT).as_posix()
        if register_path.is_relative_to(REPO_ROOT)
        else register_path.as_posix(),
        "summary": {
            "kpis_registered": len(metrics),
            "kpis_with_recorded_baseline": with_baseline,
            "kpis_with_measured_actual": 0,
            "checks_passed": sum(1 for c in checks if c["status"] == PASS),
            "checks_failed": sum(1 for c in checks if c["status"] == FAIL),
            "checks_unmeasured": sum(1 for c in checks if c["status"] == UNMEASURED),
        },
        "checks": checks,
        "metrics": metrics,
        "sign_off": {
            "status": UNMEASURED,
            "required_roles": list(REQUIRED_SIGNATORY_ROLES),
            "detail": SIGN_OFF_UNMEASURED,
        },
        "executive_verdict": verdict,
    }


def render_markdown(report: dict) -> str:
    s = report["summary"]
    lines = [
        "# Benefits Realisation Report — Milestone R11-M04-T01",
        "## 1000FiX ERP System v2.0 · BM-002..BM-005",
        "",
        "Generated by `tooling/scripts/measure_benefits_realisation.py` "
        f"at {report['measurement_timestamp']}. Every status below is computed in that run.",
        "",
        "| Item | Value |",
        "|---|---|",
        f"| **Baseline source** | `{report['baseline_source']}` |",
        f"| **Registered KPIs** | {s['kpis_registered']} |",
        f"| **KPIs with a recorded pre-programme baseline** | {s['kpis_with_recorded_baseline']} |",
        f"| **KPIs with a measured production actual** | {s['kpis_with_measured_actual']} |",
        f"| **Executive verdict** | **{report['executive_verdict']}** |",
        "",
        "## Checks",
        "",
        "| Check | Status | Detail |",
        "|---|:---:|---|",
    ]
    lines += [f"| `{c['id']}` | {c['status']} | {c['detail']} |" for c in report["checks"]]
    lines += [
        "",
        "## Registered KPIs (baselines and targets from the register; actuals not measured)",
        "",
        "| KPI | Name | Register baseline | W4 target | W8 target | Actual | Status |",
        "|---|---|:---:|:---:|:---:|:---:|:---:|",
    ]
    lines += [
        f"| {m['kpi_id']} | {m['name']} | {m['register_baseline']} | {m['w4_target']} | "
        f"{m['w8_target']} | — | {m['status']} |"
        for m in report["metrics"]
    ]
    lines += [
        "",
        "## Sign-off",
        "",
        f"Status: **{report['sign_off']['status']}** — {report['sign_off']['detail']}. "
        f"Required roles: {', '.join(report['sign_off']['required_roles'])}.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    print("=" * 76)
    print("1000FiX ERP — Task R11-M04-T01: Benefits Realisation Measurement")
    print("=" * 76)
    report = measure_benefits()
    for check in report["checks"]:
        print(f"  [{check['status']}] {check['id']}: {check['detail']}")

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    json_path = EVIDENCE_DIR / "r11-m04-benefits-realisation-report.json"
    json_path.write_bytes((json.dumps(report, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
    TRACEABILITY_DIR.mkdir(parents=True, exist_ok=True)
    md_path = TRACEABILITY_DIR / "r11-m04-benefits-realisation-report.md"
    md_path.write_bytes(render_markdown(report).encode("utf-8"))

    print(f"\nExecutive verdict: {report['executive_verdict']}")
    print(f"[OK] Benefits evidence JSON written: {json_path}")
    print(f"[OK] Benefits realisation report written: {md_path}")
    return exit_code(report["executive_verdict"])


if __name__ == "__main__":
    raise SystemExit(main())
