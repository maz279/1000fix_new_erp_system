# A02 · M03 Service Logistics (Pick & Drop) — models the generic workspace
# screens may read, the workflow methods they may call (/p03/model/records,
# /p03/model/action), the module KPI payload (/p03/logistics/kpis) and the
# built-in reports (/p03/model/report). Same contract as a02/m01..m31.
import datetime
import logging

from odoo import http
from odoo.http import request

from ..p03_service_order_api import _require_internal

_logger = logging.getLogger(__name__)

SURFACES = {
    "fix.consignment": {
        "order": "scheduled_date desc, id desc",
        "limit": 200,
        "actions": {
            "action_confirm",
            "action_start_transit",
            "action_generate_otp",
            "action_verify_pod",
            "action_deliver",
            "action_return",
            "action_report_lost",
        },
    },
    "fix.custody.scan": {
        "order": "scanned_at desc, id desc",
        "limit": 300,
        "actions": set(),
    },
}


def _cons(env):
    return env["fix.consignment"].sudo().with_context(lang="en_US")


def kpis(env):
    """The M03 module-tile KPI row (registry-canonical metrics)."""
    Cons = _cons(env)
    domain = [("company_id", "in", env.companies.ids)]
    today = datetime.date.today()

    in_transit = Cons.search_count([*domain, ("state", "=", "in_transit")])

    delivered = Cons.search([*domain, ("state", "=", "delivered")], limit=500)
    on_time = sum(
        1
        for c in delivered
        if c.scheduled_date and c.write_date and c.write_date <= c.scheduled_date
    )
    # on-time = closed by the scheduled date (schedule = promised window end)
    on_time_pct = round(100.0 * on_time / len(delivered), 1) if delivered else None

    custody_exceptions = Cons.search_count(
        [*domain, ("chain_broken", "=", True)]
    ) + Cons.search_count([*domain, ("state", "=", "lost")])

    cod_today = None
    if "fix.cod.settlement" in env:
        Settlement = env["fix.cod.settlement"].sudo()
        cod_today = Settlement.search_count([("settlement_date", "=", today)])

    round_trips = [
        (c.write_date - c.create_date).total_seconds() / 86400.0
        for c in delivered
        if c.create_date and c.write_date
    ]
    avg_round_trip = round(sum(round_trips) / len(round_trips), 1) if round_trips else None

    # rider shifts: no rider-shift model exists (P09 app scope) — honest null
    return {
        "in_transit": in_transit,
        "on_time_delivery": on_time_pct,
        "custody_exceptions": custody_exceptions,
        "cod_today": cod_today,
        "avg_round_trip": avg_round_trip,
        "rider_shifts_open": None,
    }


# ---------------------------------------------------------------- reports


def _cycle_time_report(env, **params):
    Cons = _cons(env)
    rows = []
    for ctype in ("pickup", "delivery", "branch_transfer", "return_to_vendor"):
        done = Cons.search(
            [("consignment_type", "=", ctype), ("state", "in", ("delivered", "returned"))],
            limit=300,
        )
        spans = [
            (c.write_date - c.create_date).total_seconds() / 86400.0
            for c in done
            if c.create_date and c.write_date
        ]
        rows.append(
            {
                "type": ctype.replace("_", " ").title(),
                "closed": len(done),
                "avg_days": round(sum(spans) / len(spans), 1) if spans else None,
                "max_days": round(max(spans), 1) if spans else None,
            }
        )
    return {
        "title": "Consignment Cycle Time",
        "cols": ["type", "closed", "avg_days", "max_days"],
        "labels": {
            "type": "Consignment Type",
            "closed": "Closed",
            "avg_days": "Avg Days",
            "max_days": "Max Days",
        },
        "rows": rows,
        "notes": ["Creation → close, delivered/returned consignments only."],
    }


def _custody_exception_report(env, **params):
    Cons = _cons(env)
    rows = [
        {
            "consignment": c.name,
            "type": c.consignment_type,
            "state": c.state,
            "issue": "broken chain" if c.chain_broken else "reported lost",
            "chain": c.custody_summary or "",
        }
        for c in Cons.search([("chain_broken", "=", True)])
    ]
    rows += [
        {
            "consignment": c.name,
            "type": c.consignment_type,
            "state": c.state,
            "issue": "reported lost",
            "chain": c.custody_summary or "",
        }
        for c in Cons.search([("state", "=", "lost")])
    ]
    return {
        "title": "Custody Exception Register",
        "cols": ["consignment", "type", "state", "issue", "chain"],
        "labels": {
            "consignment": "Consignment",
            "type": "Type",
            "state": "State",
            "issue": "Issue",
            "chain": "Recorded Chain",
        },
        "rows": rows,
        "notes": ["Broken chains (out-of-order scans) and lost consignments — live."],
    }


def _courier_performance_report(env, **params):
    return {
        "title": "Courier Performance (Pathao/RedX/Steadfast)",
        "cols": ["courier", "bookings"],
        "labels": {"courier": "Courier Partner", "bookings": "Bookings"},
        "rows": [],
        "notes": [
            "No courier partner master exists yet — the courier integration "
            "(partner accounts, bookings, rate cards) is a later phase; this "
            "report lights up with it."
        ],
    }


def _cod_settlement_report(env, **params):
    rows = []
    if "fix.cod.settlement" in env:
        Settlement = env["fix.cod.settlement"].sudo()
        for s in Settlement.search([], order="id desc", limit=100):
            rows.append(
                {
                    "settlement": s.name or str(s.id),
                    "state": s.state or "",
                    "expected": s.expected_amount,
                    "remitted": s.remitted_amount,
                    "variance": s.variance,
                    "date": str(s.settlement_date or "")[:10],
                }
            )
    return {
        "title": "COD Settlement Report",
        "cols": ["settlement", "state", "expected", "remitted", "variance", "date"],
        "labels": {
            "settlement": "Settlement",
            "state": "State",
            "expected": "Expected",
            "remitted": "Remitted",
            "variance": "Variance",
            "date": "Date",
        },
        "rows": rows,
        "notes": [
            "COD settlements live in the M50 treasury engine (fix.cod.settlement); "
            "the M03 collection model arrives with the rider-app phase."
        ],
    }


def _reverse_volume_report(env, **params):
    Cons = _cons(env)
    returned = Cons.search([("state", "=", "returned")], limit=200)
    rows = [
        {"consignment": c.name, "type": c.consignment_type, "chain": c.custody_summary or ""}
        for c in returned
    ]
    return {
        "title": "Reverse Logistics Volume",
        "cols": ["consignment", "type", "chain"],
        "labels": {"consignment": "Consignment", "type": "Type", "chain": "Chain"},
        "rows": rows,
        "notes": ["Returned consignments (reverse logistics legs), live."],
    }


def _damage_claims_report(env, **params):
    Cons = _cons(env)
    lost = Cons.search([("state", "=", "lost")], limit=200)
    rows = [
        {
            "consignment": c.name,
            "last_known": c.custody_summary or "",
            "rider": c.rider_id.name or "",
        }
        for c in lost
    ]
    return {
        "title": "Damage & Insurance Claims",
        "cols": ["consignment", "last_known", "rider"],
        "labels": {
            "consignment": "Consignment",
            "last_known": "Last Known Custody",
            "rider": "Rider",
        },
        "rows": rows,
        "notes": [
            "Lost consignments are the claim candidates; the insurance-claims "
            "engine (valuation, adjuster flow) is a later phase."
        ],
    }


REPORTS = {
    "cycle_time": _cycle_time_report,
    "custody_exceptions": _custody_exception_report,
    "courier_performance": _courier_performance_report,
    "cod_settlement": _cod_settlement_report,
    "reverse_volume": _reverse_volume_report,
    "damage_claims": _damage_claims_report,
}


class P03M03Controller(http.Controller):
    @http.route("/p03/logistics/kpis", type="jsonrpc", auth="user", readonly=True)
    def logistics_kpis(self, **kw):
        _require_internal(request.env)
        try:
            return {"M03": kpis(request.env)}
        except Exception:
            _logger.exception("p03 logistics_kpis failed")
            return {"error": "KPI computation failed"}
