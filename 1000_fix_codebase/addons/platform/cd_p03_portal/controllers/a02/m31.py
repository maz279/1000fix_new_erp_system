# A02 · M31 Workshop & Depot Repair — models the generic workspace screens
# may read, the workflow methods they may call (/p03/model/records,
# /p03/model/action), the module KPI payload (/p03/workshop/kpis) and the
# built-in reports (/p03/model/report). Same contract as a02/m01 + m02.
import datetime
import logging

from odoo import http
from odoo.http import request

from ..p03_service_order_api import _require_internal

_logger = logging.getLogger(__name__)

SURFACES = {
    "fix.workshop.job": {
        "order": "priority desc, create_date desc, id desc",
        "limit": 200,
        # A07 M45: the QC instrument. Retired, missing and out-of-service items are
        # not offered; the fitness gate at QC pass still judges the one named.
        "pickers": {
            "equipment_id": [("operational_status", "in", ("available", "issued"))],
            # M31 audit 14 Nov: a bench under maintenance or closed takes no job
            "bench_id": [("state", "in", ("available", "occupied"))],
        },
        # A02 audit M31-7 / P31-06: the generic action_transition is NOT
        # offered — it reached qc_failed with no NCR and no rework count. Only
        # the named actions, each carrying its own gates and side-effects.
        "actions": {
            "action_intake",
            "action_diagnostic",
            "action_wait_parts",
            "action_auto_assign_bench",
            # sub-module 3 "Bench Allocation & Queue": the job to a bench and
            # a technician, with the hand-over note (FR-WSR-011/015)
            "action_allocate_bench",
            "action_start_repair",
            "action_submit_qc",
            "action_start_burn_in",
            "action_log_thermal_crash",
            "action_pass_burn_in",
            "action_fail_burn_in",
            "action_pass_qc",
            "action_fail_qc",
            "action_deliver",
            "action_cancel",
            # A02 audit B1: the waiver is a routed request; the BER write-off
            # is requested by Confirm BER and approved from the M63 inbox, so
            # neither action_dofa_approve nor a direct grant is offered.
            "action_request_certification_waiver",
            "action_grant_certification_waiver",
            "action_propose_ber",
            "action_confirm_ber",
            "action_recall_approval",
        },
    },
    "fix.workshop.bench": {
        "order": "code",
        "limit": 100,
        "actions": {
            "action_log_daily_esd",
            "action_set_maintenance",
            "action_set_offline",
            "action_return_to_service",
        },
    },
    "fix.workshop": {
        "order": "code",
        "limit": 50,
        # A02 audit M31 step 1: receive a device from M01 on the M31 side
        "actions": {"action_receive_service_order"},
    },
    "fix.workshop.part.line": {
        "order": "id desc",
        "limit": 200,
        # Part Fitment form: a closed job takes no new parts (the model refuses
        # it), so it is not offered
        "pickers": {"job_id": [("state", "not in", ("delivered", "unrepairable", "cancelled"))]},
        # A02 audit B1: a part beyond the approved estimate is fitted after a
        # routed extra-part approval (Request Approval), decided in M63
        "actions": {
            "action_reserve",
            "action_consume_part",
            "action_release_reservation",
            "action_request_approval",
            "action_recall_approval",
        },
    },
    "fix.workshop.evidence": {
        "order": "id desc",
        "limit": 200,
        "actions": set(),
    },
    # sub-module 7 "Testing & Burn-In" (M31 audit 14 Nov 2026): the protocol
    # library (FR-WSR-031, workshop managers) and the measured test results
    # recorded against it (FR-WSR-032); a result is judged by its limits
    "fix.workshop.test.protocol": {"order": "code", "limit": 200, "actions": set()},
    "fix.workshop.test.result": {
        "order": "tested_at desc, id desc",
        "limit": 300,
        "pickers": {
            "job_id": [
                ("state", "not in", ("delivered", "unrepairable", "cancelled")),
                ("qc_passed", "=", False),
            ],
            "step_id": [("protocol_id.active", "=", True)],
            "equipment_id": [("operational_status", "in", ("available", "issued"))],
        },
        "actions": set(),
    },
}

_WIP_STATES = (
    "intake",
    "diagnostic",
    "waiting_parts",
    "in_repair",
    "burn_in",
    "qc_pending",
    "qc_failed",
)


def _jobs(env):
    return env["fix.workshop.job"].sudo().with_context(lang="en_US")


def kpis(env):
    """The M31 module-tile KPI row (registry-canonical metrics)."""
    Job = _jobs(env)
    domain = [("company_id", "in", env.companies.ids)]
    now = datetime.datetime.now()

    on_bench = Job.search_count([*domain, ("bench_id", "!=", False), ("state", "in", _WIP_STATES)])
    completed = Job.search([*domain, ("state", "=", "delivered")], limit=500)
    passed_first = sum(1 for j in completed if not j.is_rework and j.rework_count == 0)
    first_pass_yield = round(100.0 * passed_first / len(completed), 1) if completed else None

    l3_waiting = Job.search(
        [
            *domain,
            ("repair_level", "=", "l3"),
            ("state", "in", ("intake", "diagnostic", "waiting_parts")),
        ],
        limit=200,
    )
    l3_over_48h = sum(
        1 for j in l3_waiting if j.create_date and (now - j.create_date).total_seconds() > 48 * 3600
    )

    durations_days = [
        (j.completed_at - j.create_date).total_seconds() / 86400.0
        for j in completed
        if j.completed_at and j.create_date
    ]
    avg_bench_days = round(sum(durations_days) / len(durations_days), 1) if durations_days else None

    lines_with_serial = (
        env["fix.workshop.part.line"].sudo().search_count([("lot_serial_number", "!=", False)])
    )
    lines_total = env["fix.workshop.part.line"].sudo().search_count([])
    parts_fitment = round(100.0 * lines_with_serial / lines_total, 1) if lines_total else None

    internal_rework = Job.search_count([*domain, ("is_rework", "=", True)])

    return {
        "on_bench": on_bench,
        "first_pass_yield": first_pass_yield,
        "l3_queue_48h": l3_over_48h,
        "avg_bench_days": avg_bench_days,
        "parts_fitment": parts_fitment,
        "internal_rework": internal_rework,
    }


# ---------------------------------------------------------------- reports


def _bench_utilisation_report(env, **params):
    Workshop = env["fix.workshop"].sudo()
    rows = []
    for w in Workshop.search([]):
        rows.append(
            {
                "workshop": w.name,
                "type": w.workshop_type,
                "benches": w.bench_count,
                "available": w.available_bench_count,
                "utilisation_pct": w.bench_utilization,
                "active_jobs": w.active_job_count,
            }
        )
    return {
        "title": "Bench Utilisation by Workshop",
        "cols": ["workshop", "type", "benches", "available", "utilisation_pct", "active_jobs"],
        "labels": {
            "workshop": "Workshop",
            "type": "Type",
            "benches": "Benches",
            "available": "Available",
            "utilisation_pct": "Utilisation %",
            "active_jobs": "Active Jobs",
        },
        "rows": rows,
        "notes": ["Live reads of the workshop/bench masters with their stored computes."],
    }


def _cycle_time_report(env, **params):
    """Repair Cycle Time by Level: draft→completed days per L1/L2/L3."""
    Job = _jobs(env)
    rows = []
    for level in ("l1", "l2", "l3"):
        done = Job.search([("repair_level", "=", level), ("state", "=", "delivered")], limit=300)
        durations = [
            (j.completed_at - j.create_date).total_seconds() / 86400.0
            for j in done
            if j.completed_at and j.create_date
        ]
        rows.append(
            {
                "level": level.upper(),
                "delivered": len(done),
                "avg_days": round(sum(durations) / len(durations), 1) if durations else None,
                "max_days": round(max(durations), 1) if durations else None,
            }
        )
    return {
        "title": "Repair Cycle Time by Level",
        "cols": ["level", "delivered", "avg_days", "max_days"],
        "labels": {
            "level": "Repair Level",
            "delivered": "Delivered Jobs",
            "avg_days": "Avg Days",
            "max_days": "Max Days",
        },
        "rows": rows,
        "notes": [
            "Cycle time runs from the creation of the repair job to its completion; "
            "only delivered jobs are counted."
        ],
    }


def _rework_loop_report(env, **params):
    Job = _jobs(env)
    reworks = Job.search([("is_rework", "=", True)], limit=300)
    by_reason = {}
    for j in reworks:
        by_reason[j.rework_reason or "unspecified"] = (
            by_reason.get(j.rework_reason or "unspecified", 0) + 1
        )
    rows = [
        {"reason": reason, "jobs": count}
        for reason, count in sorted(by_reason.items(), key=lambda kv: -kv[1])
    ]
    return {
        "title": "Internal Rework Loop Analysis",
        "cols": ["reason", "jobs"],
        "labels": {"reason": "Rework Reason", "jobs": "Jobs"},
        "rows": rows,
        "notes": [
            "A rework loop is a job sent back to repair after failing its quality check; "
            "counts are live."
        ],
    }


def _cost_report(env, **params):
    Job = _jobs(env)
    rows = []
    for level in ("l1", "l2", "l3"):
        done = Job.search(
            [("repair_level", "=", level), ("state", "in", ("ready", "delivered"))], limit=300
        )
        if not done:
            rows.append(
                {
                    "level": level.upper(),
                    "jobs": 0,
                    "avg_parts": None,
                    "avg_labour": None,
                    "avg_total": None,
                }
            )
            continue
        n = len(done)
        rows.append(
            {
                "level": level.upper(),
                "jobs": n,
                "avg_parts": round(sum(done.mapped("parts_total")) / n, 2),
                "avg_labour": round(sum(done.mapped("labour_total")) / n, 2),
                "avg_total": round(sum(done.mapped("total_repair_cost")) / n, 2),
            }
        )
    return {
        "title": "Workshop Cost per Repair (BDT)",
        "cols": ["level", "jobs", "avg_parts", "avg_labour", "avg_total"],
        "labels": {
            "level": "Level",
            "jobs": "Jobs",
            "avg_parts": "Avg Parts",
            "avg_labour": "Avg Labour",
            "avg_total": "Avg Total",
        },
        "rows": rows,
        "notes": [
            "Parts from consumed part lines; labour is the recorded workshop figure (no rate card yet)."
        ],
    }


def _genealogy_report(env, **params):
    Line = env["fix.workshop.part.line"].sudo()
    lines = Line.search([("lot_serial_number", "!=", False)], order="id desc", limit=200)
    rows = [
        {
            "job": ln.job_id.name,
            "part": ln.part_number or (ln.product_id.display_name or ""),
            "qty": ln.quantity,
            "lot_serial": ln.lot_serial_number,
        }
        for ln in lines
    ]
    return {
        "title": "Parts Genealogy Trace",
        "cols": ["job", "part", "qty", "lot_serial"],
        "labels": {"job": "Job", "part": "Part", "qty": "Qty", "lot_serial": "Lot / Serial"},
        "rows": rows,
        "notes": ["Part lines carrying a lot/serial — the genealogy the swap recorded."],
    }


def _burnin_report(env, **params):
    Job = _jobs(env)
    tested = Job.search([("burn_in_started_at", "!=", False)], limit=300)
    passed = sum(1 for j in tested if j.burn_in_passed)
    rows = [
        {"measure": "Burn-in started", "value": len(tested)},
        {"measure": "Burn-in passed", "value": passed},
        {"measure": "Failed after burn-in", "value": len(tested) - passed},
        {
            "measure": "Pass rate %",
            "value": round(100.0 * passed / len(tested), 1) if tested else None,
        },
    ]
    return {
        "title": "Burn-In Failure Report",
        "cols": ["measure", "value"],
        "labels": {"measure": "Measure", "value": "Jobs"},
        "rows": rows,
        "notes": ["L2/L3 jobs are burn-in gated before QC — these are the recorded outcomes."],
    }


REPORTS = {
    "bench_utilisation": _bench_utilisation_report,
    "cycle_time": _cycle_time_report,
    "rework_loops": _rework_loop_report,
    "cost_per_repair": _cost_report,
    "parts_genealogy": _genealogy_report,
    "burn_in": _burnin_report,
}


class P03M31Controller(http.Controller):
    @http.route("/p03/workshop/kpis", type="jsonrpc", auth="user", readonly=True)
    def workshop_kpis(self, **kw):
        _require_internal(request.env)
        try:
            return {"M31": kpis(request.env)}
        except Exception:
            _logger.exception("p03 workshop_kpis failed")
            return {"error": "KPI computation failed"}
