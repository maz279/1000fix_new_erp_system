#!/usr/bin/env python3
"""
execute-branch-rollout.py — Milestone R08-M05-T02: phased rollout record, Waves 1 to 4,
with super-user cohorts per wave (D-002 names from R01).

GV-009: the previous version wrote twelve "PASS" readiness checks per wave, invented
exam scores, a "LIVE" status, "53 achieved", "STABILIZED_HEALTHY" hypercare and a dated
sign-off without measuring any of it. Every status below is now computed in this run:

  ROLLOUT_REGISTER_TARGET  active BR-* service centres in the branch register >= 51
  ROLLOUT_WAVE_PLAN        the four wave plans cover every registered centre exactly once
  D002_ROSTER              every cohort lead is named (id + name) in the D-002 roster
  W<n>:RB-03_operating_unit  each planned centre registered, active, operating unit bound
  W<n>:RB-04_staff_roster    each planned centre has >= 1 active employee (hr_employee)
  W<n>:<other RB checks>     site inspections, training records, director approval and
                             go-live are not observable here -> UNMEASURED

Database access is a read-only session (SELECT only). An unreachable database makes
the database checks UNMEASURED, never PASS.

Produces:
- tooling/fitness/evidence/branch-rollout-evidence.json
- docs/traceability/evidence/branch-rollout-evidence.json

Exit: 0 PASS / 1 FAIL / 2 INCOMPLETE (a check is UNMEASURED).
"""

import json
import logging
import os
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
FITNESS_EVIDENCE_DIR = ROOT_DIR / "tooling" / "fitness" / "evidence"
DOCS_EVIDENCE_DIR = ROOT_DIR / "docs" / "traceability" / "evidence"
D002_ROSTER = ROOT_DIR / "docs" / "p01-m09" / "D-002-super-user-named-roster.md"

DB_HOST = os.environ.get("PGHOST", "localhost")
DB_PORT = int(os.environ.get("PGPORT", "5433"))
DB_NAME = os.environ.get("PGDATABASE", "fix_dev")
DB_USER = os.environ.get("PGUSER", "fix")
DB_PASS = os.environ.get("PGPASSWORD", "change-me-dev-only")

PASS = "PASS"  # noqa: S105 - a verdict label, not a credential
FAIL = "FAIL"
UNMEASURED = "UNMEASURED"
INCOMPLETE = "INCOMPLETE"

REQUIRED_CENTRES = 51

# Planned centres per wave (RB-51).
WAVE_PLAN = {
    1: ["BR-0001", "BR-0004", "BR-0040", "BR-0043"],
    2: [f"BR-{i:04d}" for i in [2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 52, 53]],
    3: (
        [f"BR-{i:04d}" for i in range(20, 27)]
        + [f"BR-{i:04d}" for i in range(32, 37)]
        + [f"BR-{i:04d}" for i in [41, 42]]
        + [f"BR-{i:04d}" for i in range(44, 52)]
    ),
    4: (
        [f"BR-{i:04d}" for i in range(16, 20)]
        + [f"BR-{i:04d}" for i in range(27, 32)]
        + [f"BR-{i:04d}" for i in range(37, 40)]
    ),
}

# D-002 super-user cohort leads per wave: (id, name, role, course).
SUPERUSER_COHORTS = {
    1: {
        "cohort_name": "Wave 1 Pilot & Flagship Cohort (Dhaka Central, CTG, SYL)",
        "leads": [
            ("FX-00312", "Kazi Fahim Ahmed", "Lead Service Engineer", "TR-011"),
            ("FX-00318", "Tanvir Hossain", "Senior Tech Lead", "TR-012"),
            ("FX-00288", "Shamsul Huda", "Workshop Superintendent", "TR-011"),
            ("FX-00294", "Kamrul Hasan", "Master Diagnostics Tech", "TR-012"),
            ("FX-00412", "Asif Iqbal", "Field Dispatch Lead (CTG)", "TR-011"),
            ("FX-00610", "Rumana Islam", "Front Desk Supervisor", "TR-002"),
        ],
        "floor_walkers_ratio": "1 per 8 users (3 per site)",
    },
    2: {
        "cohort_name": "Wave 2 Greater Dhaka Metro Commercial Cohort",
        "leads": [
            ("FX-00201", "Nazmul Huda", "Diagnostic Specialist (Motijheel)", "TR-012"),
            ("FX-00366", "Shahriar Kabir", "Senior Estimator", "TR-011"),
            ("FX-00155", "Jahangir Alam", "Central Warehouse Manager (Gazipur)", "TR-024"),
            ("FX-00162", "Mustafizur Rahman", "Inventory Controller", "TR-024"),
            ("FX-00615", "Sharmin Sultana", "Customer Experience Specialist", "TR-002"),
            ("FX-00460", "Rashedul Islam", "Lead Field Tech", "TR-011"),
        ],
        "floor_walkers_ratio": "1 per 12 users (2 per site)",
    },
    3: {
        "cohort_name": "Wave 3 Major Regional Hubs Cohort (CTG, SYL, KHU, RAJ)",
        "leads": [
            ("FX-00405", "Mahbubur Rahman", "Regional Field Ops Manager", "TR-011"),
            ("FX-00250", "Habibur Rahman", "Branch Operations Coordinator", "TR-011"),
            ("FX-00256", "Shafiqul Islam", "Network Infrastructure Lead", "TR-002"),
            ("FX-00430", "Kazi Nurul Islam", "Regional Logistics Lead", "TR-024"),
            ("FX-00445", "Sohail Ahmed", "Regional Retail Network Ops", "TR-011"),
            ("FX-00550", "Sumona Barua", "Master Data Steward (CTG Hub)", "TR-002"),
        ],
        "floor_walkers_ratio": "1 per 14 users (2 per site)",
    },
    4: {
        "cohort_name": "Wave 4 National Frontier Completion Cohort (MYM, RAN, BAR)",
        "leads": [
            ("FX-00195", "Engr. Zakir Hossain", "Chief Operations Superintendent", "TR-011"),
            ("FX-00371", "Mizanur Rahman", "Regional Service Desk Lead", "TR-002"),
            ("FX-00380", "Enamul Haque", "Pricing & Service Kit Specialist", "TR-012"),
            ("FX-00386", "Badrul Alam", "Service Kits Regional Engineer", "TR-012"),
            ("FX-00810", "Tahmina Khatun", "Workforce Deployment Partner", "TR-002"),
            ("FX-00816", "Zahidul Islam", "HR Field Enablement Lead", "TR-002"),
        ],
        "floor_walkers_ratio": "1 per 15 users (1-2 per site)",
    },
}

# RB-51 readiness checks that need a site inspection or a named human: never measured here.
UNOBSERVABLE_READINESS = {
    "RB-01_network_power": "site inspection (dual ISP + online UPS)",
    "RB-02_hardware_terminals": "site inspection (POS printers, QR scanners)",
    "RB-03_gps_bounds": "branch GPS coordinates, which fix_branch does not store",
    "RB-05_superuser_training": "training completion / exam records (cohort leads named: D002_ROSTER)",
    "RB-06_cash_drawer": "site cash count",
    "RB-07_stock_count": "physical stock count and locked opening journals",
    "RB-08_device_custody": "site device custody audit",
    "RB-09_branding_signage": "site inspection",
    "RB-10_emergency_paper_forms": "site inspection",
    "RB-11_cctv_security": "site inspection",
    "RB-12_director_approval": "a named director's signed approval",
    "GO_LIVE": "production go-live of the centre (production event)",
}

DESIGNATED_APPROVERS = {
    "branch_operations_lead": "Habibur Rahman (FX-00250)",
    "change_lead": "Rumana Islam (FX-00610)",
    "operations_director": "Engr. Zakir Hossain (FX-00195)",
}


def make_check(check_id: str, status: str, detail: str, **measured: object) -> dict:
    return {"id": check_id, "status": status, "detail": detail, **measured}


def overall_verdict(checks: list[dict]) -> str:
    statuses = {check["status"] for check in checks}
    if not statuses:
        return UNMEASURED
    if FAIL in statuses:
        return FAIL
    return PASS if statuses == {PASS} else INCOMPLETE


def exit_code(verdict: str) -> int:
    return {PASS: 0, FAIL: 1}.get(verdict, 2)


def verify_branches_in_db() -> list[tuple]:
    """Active BR-* centres with their operating unit and active-employee count (read-only)."""
    import psycopg2

    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        connect_timeout=5,
    )
    try:
        conn.set_session(readonly=True, autocommit=True)
        with conn.cursor() as cur:
            cur.execute("""
                SELECT b.code, b.name, b.name_bn, b.active, b.legacy_reference,
                       ou.code AS ou_code, ou.name AS ou_name,
                       (SELECT count(*) FROM hr_employee e
                         WHERE e.branch_id = b.id AND e.active) AS employees
                FROM fix_branch b
                LEFT JOIN operating_unit ou ON b.operating_unit_id = ou.id
                WHERE b.active = true AND b.code LIKE 'BR-%'
                ORDER BY b.code;
            """)
            return cur.fetchall()
    finally:
        conn.close()


def check_d002_roster(roster_path: Path) -> tuple[dict, int | None]:
    """Every cohort lead's id and name appear together on a D-002 roster line."""
    if not roster_path.exists():
        return make_check("D002_ROSTER", FAIL, f"{roster_path.name} missing"), None
    text = roster_path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    named_ids = set(re.findall(r"FX-\d{5}", text))
    missing = [
        f"{lead_id} {name}"
        for cohort in SUPERUSER_COHORTS.values()
        for lead_id, name, _role, _course in cohort["leads"]
        if not any(f"`{lead_id}`" in line and name in line for line in lines)
    ]
    total = sum(len(c["leads"]) for c in SUPERUSER_COHORTS.values())
    if missing:
        return make_check("D002_ROSTER", FAIL, f"leads not in the D-002 roster: {missing}"), len(
            named_ids
        )
    return make_check(
        "D002_ROSTER", PASS, f"{total}/{total} cohort leads named in {roster_path.name}"
    ), len(named_ids)


def global_db_checks(db_rows: list[tuple] | None, db_error: str | None) -> list[dict]:
    if db_rows is None:
        reason = f"branch register not reachable: {db_error}"
        return [
            make_check("ROLLOUT_REGISTER_TARGET", UNMEASURED, reason),
            make_check("ROLLOUT_WAVE_PLAN", UNMEASURED, reason),
        ]
    registered = {row[0] for row in db_rows}
    target = make_check(
        "ROLLOUT_REGISTER_TARGET",
        PASS if len(registered) >= REQUIRED_CENTRES else FAIL,
        f"{len(registered)} active BR-* centres registered (required >= {REQUIRED_CENTRES})",
        registered=len(registered),
    )
    planned = [code for codes in WAVE_PLAN.values() for code in codes]
    duplicates = sorted({c for c in planned if planned.count(c) > 1})
    unplanned = sorted(registered - set(planned))
    unregistered = sorted(set(planned) - registered)
    problems = []
    if duplicates:
        problems.append(f"in more than one wave: {duplicates}")
    if unplanned:
        problems.append(f"registered but in no wave: {unplanned}")
    if unregistered:
        problems.append(f"planned but not registered/active: {unregistered}")
    plan = make_check(
        "ROLLOUT_WAVE_PLAN",
        FAIL if problems else PASS,
        "; ".join(problems) or f"{len(planned)} planned centres == registered centres",
        planned=len(planned),
    )
    return [target, plan]


def wave_checks(wave_num: int, by_code: dict | None, db_error: str | None) -> dict:
    codes = WAVE_PLAN[wave_num]
    checks: dict[str, dict] = {}
    if by_code is None:
        reason = f"branch register not reachable: {db_error}"
        checks["RB-03_operating_unit"] = make_check("RB-03_operating_unit", UNMEASURED, reason)
        checks["RB-04_staff_roster"] = make_check("RB-04_staff_roster", UNMEASURED, reason)
    else:
        unbound = [c for c in codes if c not in by_code or not by_code[c][5]]
        checks["RB-03_operating_unit"] = make_check(
            "RB-03_operating_unit",
            FAIL if unbound else PASS,
            f"not registered / no operating unit: {unbound}"
            if unbound
            else f"{len(codes)}/{len(codes)} centres registered with an operating unit",
        )
        unstaffed = [c for c in codes if c not in by_code or not by_code[c][7]]
        checks["RB-04_staff_roster"] = make_check(
            "RB-04_staff_roster",
            FAIL if unstaffed else PASS,
            f"{len(unstaffed)}/{len(codes)} centres have no active employee: {unstaffed}"
            if unstaffed
            else f"{len(codes)}/{len(codes)} centres have active employees",
        )
    for check_id, needs in UNOBSERVABLE_READINESS.items():
        checks[check_id] = make_check(check_id, UNMEASURED, f"requires {needs}")
    return checks


def execute_rollout() -> dict:
    logger.info("Recording Milestone R08-M05 phased national rollout (measure-only)...")
    try:
        db_rows, db_error = verify_branches_in_db(), None
    except Exception as exc:  # any driver/connection failure: the register is not observable
        db_rows, db_error = None, f"{type(exc).__name__}: {str(exc).strip()}"
    by_code = {row[0]: row for row in db_rows} if db_rows is not None else None

    roster_check, roster_ids = check_d002_roster(D002_ROSTER)
    global_checks = [*global_db_checks(db_rows, db_error), roster_check]
    checks = list(global_checks)
    wave_results = {}
    for wave_num, cohort in SUPERUSER_COHORTS.items():
        readiness = wave_checks(wave_num, by_code, db_error)
        codes = WAVE_PLAN[wave_num]
        wave_results[f"wave_{wave_num}"] = {
            "wave": wave_num,
            "cohort_name": cohort["cohort_name"],
            "branches_planned": len(codes),
            "branches_verified_in_db": (
                sum(1 for c in codes if c in by_code) if by_code is not None else None
            ),
            "floor_walkers_ratio": cohort["floor_walkers_ratio"],
            "super_user_leads": [
                {"id": i, "name": n, "role": r, "course": c} for i, n, r, c in cohort["leads"]
            ],
            "readiness_checks": readiness,
            "status": overall_verdict(list(readiness.values())),
        }
        checks += [dict(c, id=f"W{wave_num}:{c['id']}") for c in readiness.values()]

    verdict = overall_verdict(checks)
    evidence_payload = {
        "milestone": "R08-M05",
        "task": "R08-M05-T02",
        "tool": "tooling/scripts/execute-branch-rollout.py",
        "timestamp": datetime.now(UTC).isoformat(),
        "verdict": verdict,
        "branch_register": f"{DB_HOST}:{DB_PORT}/{DB_NAME}",
        "total_service_centres_registered": len(db_rows) if db_rows is not None else None,
        "total_service_centres_live": None,
        "required_centres_target": REQUIRED_CENTRES,
        "super_user_training_model": "D-002 Option C Phased Model",
        "d002_roster_named_ids": roster_ids,
        "governance_runbook": "docs/runbooks/RB-51-branch-rollout-runbook.md",
        "summary": {
            s.lower(): sum(1 for c in checks if c["status"] == s) for s in (PASS, FAIL, UNMEASURED)
        },
        "checks": global_checks,
        "waves": wave_results,
        "rollout_blockers": [c["id"] for c in checks if c["status"] == FAIL],
        "hypercare_status": UNMEASURED,
        "signoff": {"status": UNMEASURED, "designated_approvers": DESIGNATED_APPROVERS},
    }

    FITNESS_EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(evidence_payload, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    fit_file = FITNESS_EVIDENCE_DIR / "branch-rollout-evidence.json"
    docs_file = DOCS_EVIDENCE_DIR / "branch-rollout-evidence.json"
    fit_file.write_bytes(payload)
    docs_file.write_bytes(payload)

    for check in checks:
        logger.info("[%s] %s: %s", check["status"], check["id"], check["detail"])
    logger.info("Rollout evidence written to %s and %s", fit_file, docs_file)
    print(
        f"Rollout record verdict: {verdict} "
        f"({len(evidence_payload['rollout_blockers'])} failing checks)"
    )
    return evidence_payload


if __name__ == "__main__":
    sys.exit(exit_code(execute_rollout()["verdict"]))
