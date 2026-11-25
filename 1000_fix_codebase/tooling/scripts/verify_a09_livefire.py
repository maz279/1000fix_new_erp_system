#!/usr/bin/env python3
"""verify_a09_livefire.py - End-to-End Livefire Verification for Area A09
Tests all 7 People & Workforce modules:
- M21 (Core HR & Lifecycle)
- M55 (Time, Attendance & Scheduling)
- M56 (Payroll & Statutory)
- M57 (Performance & Incentives)
- M22 (Learning & Certification)
- M58 (Talent Acquisition)
- M59 (Health, Safety & Wellbeing)
"""

import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import UTC, datetime

sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://127.0.0.1:8069"
DB = "fix_dev"
ADMIN = ("admin", "admin")

PASS_COUNT = 0
FAIL_COUNT = 0


def check(name: str, ok: bool, detail: str = ""):
    global PASS_COUNT, FAIL_COUNT
    if ok:
        PASS_COUNT += 1
        print(f"  [PASS] {name}" + (f" :: {detail}" if detail else ""))
    else:
        FAIL_COUNT += 1
        print(f"  [FAIL] {name} :: {detail}")


class Client:
    def __init__(self):
        self.cookie = ""

    def _post(self, path, payload):
        req = urllib.request.Request(
            BASE + path,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                **({"Cookie": self.cookie} if self.cookie else {}),
            },
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            if "set-cookie" in r.headers:
                self.cookie = r.headers["set-cookie"].split(";")[0]
            return json.loads(r.read().decode("utf-8"))

    def login(self):
        out = self._post(
            "/web/session/authenticate",
            {"jsonrpc": "2.0", "params": {"db": DB, "login": ADMIN[0], "password": ADMIN[1]}},
        )
        return bool(out.get("result", {}).get("uid"))

    def call(self, path, params=None):
        return self._post(path, {"jsonrpc": "2.0", "params": params or {}})


def main():
    print("=====================================================================")
    print("A09 Livefire Verification Suite (M21, M55, M56, M57, M22, M58, M59)")
    print("=====================================================================")

    client = Client()
    # Wait for Odoo to be ready
    for _attempt in range(15):
        try:
            if client.login():
                print(f"[OK] Authenticated as admin on {DB} at {datetime.now(UTC).isoformat()}\n")
                break
        except Exception:
            time.sleep(2)
    else:
        print("[ERROR] Cannot authenticate to Odoo.")
        return 1

    # 1. Test KPI endpoint for each module
    print("--- 1. Testing /p03/people/kpis across all 7 modules ---")
    for mod in ["M21", "M55", "M56", "M57", "M22", "M58", "M59"]:
        kpis_resp = client.call("/p03/people/kpis", {"module": mod})
        mod_kpi = kpis_resp.get("result", {}).get(mod, {})
        check(f"{mod} KPIs live", bool(mod_kpi), f"metrics: {list(mod_kpi.keys())}")

    # 2. Test Model Records for each module
    tests = [
        (
            "M21",
            "hr.employee",
            ["name", "employee_code", "position_id", "operating_unit_id"],
            "headcount_movement",
        ),
        (
            "M21",
            "fix.employment.contract",
            ["employee_id", "contract_type", "joining_date", "basic_monthly", "state"],
            "attrition_analysis",
        ),
        (
            "M55",
            "fix.attendance.record",
            ["employee_id", "check_in", "check_out", "source", "approval_state"],
            "attendance_summary",
        ),
        (
            "M55",
            "fix.leave.request",
            ["employee_id", "leave_type_id", "date_from", "date_to", "days", "state"],
            "leave_utilisation",
        ),
        (
            "M55",
            "fix.biometric.device",
            ["name", "device_id", "model_type", "branch_id", "ip_address", "active"],
            "overtime_analysis",
        ),
        (
            "M56",
            "fix.payroll.period",
            [
                "name",
                "period_start",
                "period_end",
                "slip_count",
                "gross_total",
                "net_total",
                "state",
            ],
            "salary_register",
        ),
        (
            "M56",
            "fix.payslip",
            ["period_id", "employee_id", "basic", "taxpayer_category"],
            "tax_deduction_summary",
        ),
        (
            "M57",
            "fix.performance.goal",
            ["name", "employee_id", "period", "weight", "state"],
            "rating_distribution",
        ),
        (
            "M57",
            "fix.performance.scorecard",
            ["employee_id", "period", "first_time_fix", "csat", "score"],
            "technician_scorecards",
        ),
        ("M22", "fix.competency", ["code", "name", "device_type"], "certification_coverage"),
        (
            "M22",
            "fix.certification",
            ["employee_id", "competency_id", "issued_on", "expires_on", "status"],
            "expiry_forecast",
        ),
        (
            "M58",
            "fix.job.requisition",
            ["name", "department_id", "position_id", "openings", "state"],
            "funnel_conversion",
        ),
        (
            "M58",
            "fix.candidate",
            ["name", "email", "phone", "requisition_id", "state"],
            "time_to_fill",
        ),
        (
            "M59",
            "fix.hse.hazard",
            ["name", "hazard_type", "likelihood", "severity", "risk_score", "state"],
            "incident_statistics",
        ),
        (
            "M59",
            "fix.hazardous.substance.register",
            ["name", "un_number", "storage_location", "current_stock_litres", "state"],
            "statutory_compliance",
        ),
        (
            "M59",
            "fix.ppe.register",
            ["name", "item_type", "regulatory_standard", "stock_quantity", "state"],
            "drill_coverage",
        ),
    ]

    print("\n--- 2. Testing /p03/model/records across A09 Modules ---")
    for mod_code, model, cols, _ in tests:
        res = client.call("/p03/model/records", {"model": model, "cols": cols})
        r_data = res.get("result", {})
        err = res.get("error")
        if err:
            check(f"{mod_code} · {model} records", False, f"Server error: {err}")
        else:
            rows = r_data.get("rows", [])
            labels = r_data.get("labels", {})
            # /p03/model/records drops unknown columns silently; a column
            # with no label is one the screen will not render.
            missing = [c for c in cols if c not in labels]
            check(
                f"{mod_code} · {model} records",
                not missing,
                f"{len(rows)} live rows, {len(labels)} labels"
                + (f", dropped columns: {', '.join(missing)}" if missing else ""),
            )

    print(
        "\n--- 3. Testing /p03/model/report with Date Range Parameters (D365 Interactive Filters) ---"
    )
    date_from = "2026-01-01"
    date_to = "2026-12-31"
    tested_reports = set()
    for mod_code, _, _, report_name in tests:
        if (mod_code, report_name) in tested_reports:
            continue
        tested_reports.add((mod_code, report_name))
        res = client.call(
            "/p03/model/report",
            {"module": mod_code, "report": report_name, "date_from": date_from, "date_to": date_to},
        )
        r_data = res.get("result", {})
        err = res.get("error")
        if err or r_data.get("error"):
            check(
                f"{mod_code} · report '{report_name}' (date filtered)",
                False,
                f"Error: {err or r_data.get('error')}",
            )
        else:
            rep_title = r_data.get("title", "")
            rep_rows = r_data.get("rows", [])
            rep_cols = r_data.get("cols", [])
            check(
                f"{mod_code} · report '{report_name}'",
                True,
                f"'{rep_title}', {len(rep_rows)} rows, cols: {rep_cols}",
            )

    print("\n--- 4. Testing /p03/model/form for D365 In-Workspace Forms (with Field Metas) ---")
    form_models = [
        (
            "M21",
            "hr.employee",
            [{"name": "name"}, {"name": "employee_code"}, {"name": "work_email"}],
        ),
        (
            "M21",
            "fix.employment.contract",
            [{"name": "employee_id"}, {"name": "contract_type"}, {"name": "joining_date"}],
        ),
        (
            "M55",
            "fix.leave.request",
            [{"name": "employee_id"}, {"name": "leave_type_id"}, {"name": "days"}],
        ),
        (
            "M56",
            "fix.payroll.structure",
            [{"name": "name"}, {"name": "grade"}, {"name": "basic_pct"}],
        ),
        (
            "M57",
            "fix.performance.goal",
            [{"name": "name"}, {"name": "employee_id"}, {"name": "period"}, {"name": "weight"}],
        ),
        (
            "M22",
            "fix.certification",
            [{"name": "employee_id"}, {"name": "competency_id"}, {"name": "issued_on"}],
        ),
        (
            "M58",
            "fix.job.requisition",
            [{"name": "name"}, {"name": "department_id"}, {"name": "openings"}],
        ),
        (
            "M59",
            "fix.hazardous.substance.register",
            [{"name": "name"}, {"name": "un_number"}, {"name": "storage_location"}],
        ),
        (
            "M59",
            "fix.hse.hazard",
            [{"name": "name"}, {"name": "hazard_type"}, {"name": "likelihood"}],
        ),
    ]
    for mod_code, model, fields in form_models:
        res = client.call("/p03/model/form", {"model": model, "fields": fields, "record_id": False})
        r_data = res.get("result", {})
        err = res.get("error")
        if err or r_data.get("error"):
            check(
                f"{mod_code} · {model} form metadata", False, f"Error: {err or r_data.get('error')}"
            )
        else:
            out_fields = r_data.get("fields", [])
            check(
                f"{mod_code} · {model} form metadata",
                len(out_fields) > 0,
                f"{len(out_fields)} fields parsed with choices/types",
            )

    print("\n=====================================================================")
    print(f"A09 Livefire Result: {PASS_COUNT} PASSED, {FAIL_COUNT} FAILED")
    print("=====================================================================")
    return 0 if FAIL_COUNT == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
