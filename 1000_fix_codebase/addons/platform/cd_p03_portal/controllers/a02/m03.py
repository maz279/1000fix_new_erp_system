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
        # A02 audit M03-4: action_deliver is the internal delivery gate (it
        # needs a verified POD); the workspace closes a leg through the POD
        # code or the hub receipt, never by calling it directly.
        "actions": {
            "action_confirm",
            "action_start_transit",
            "action_verify_hub_intake",
            # A02 audit M03-P2: the weight half of the hub intake (one prompt each)
            "action_record_receive_weight",
            "action_out_for_delivery",
            "action_generate_otp",
            "action_verify_pod",
            "action_confirm_receipt",
            "action_return",
            "action_report_lost",
            "action_release_hold",
        },
    },
    "fix.courier.partner": {"order": "name", "limit": 100, "actions": set()},
    "fix.courier.booking": {
        "order": "booked_on desc, id desc",
        "limit": 400,
        # A02 audit M03-P2: pick-up starts the consignment's custody, and
        # delivery closes it on the courier's POD.
        "actions": {"action_pick_up", "action_deliver"},
    },
    "fix.damage.claim": {
        "order": "claimed_on desc, id desc",
        "limit": 300,
        # A02 audit B1: the payout is approved from the M63 inbox; the claim
        # handler requests (or recalls) the approval, never presses Approve.
        "actions": {
            "action_request_approval",
            "action_recall_approval",
            "action_reject",
            "action_settle",
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
    # A02 audit M03-13: the stamped delivery moment, not write_date (any later
    # edit moved it); rows delivered before the stamp existed fall back.
    on_time = sum(
        1
        for c in delivered
        if c.scheduled_date
        and (c.delivered_at or c.write_date)
        and (c.delivered_at or c.write_date) <= c.scheduled_date
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
        ((c.delivered_at or c.write_date) - c.create_date).total_seconds() / 86400.0
        for c in delivered
        if c.create_date and (c.delivered_at or c.write_date)
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


def _closed_at(consignment):
    """When a consignment closed, from its own stamps (A02 audit M03-P2: the
    report read write_date, which any later edit moved): the delivery
    stamp, or the server-stamped 'returned' custody scan."""
    if consignment.state == "delivered":
        return consignment.delivered_at
    returned = consignment.custody_ids.filtered(lambda s: s.step == "returned")
    return max(returned.mapped("scanned_at")) if returned else None


def _cycle_time_report(env, **params):
    Cons = _cons(env)
    rows = []
    for ctype in ("pickup", "delivery", "branch_transfer", "return_to_vendor"):
        done = Cons.search(
            [("consignment_type", "=", ctype), ("state", "in", ("delivered", "returned"))],
            limit=300,
        )
        spans = [
            (_closed_at(c) - c.create_date).total_seconds() / 86400.0
            for c in done
            if c.create_date and _closed_at(c)
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
        "notes": [
            "Creation → close, delivered/returned consignments only. Close is the "
            "delivery stamp or the returned custody scan; legs closed before those "
            "stamps existed are left out."
        ],
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
    """Courier performance from the real booking records: volume, on-time
    delivery, COD exposure and charges per partner."""
    bookings = env["fix.courier.booking"].sudo().search([])
    partners = env["fix.courier.partner"].sudo().search([])
    rows = []
    for partner in partners:
        mine = bookings.filtered(lambda b, p=partner: b.partner_id.id == p.id)
        delivered = mine.filtered(lambda b: b.state == "delivered")
        returned = mine.filtered(lambda b: b.state == "returned")
        closed = delivered | returned
        on_time = delivered.filtered(
            lambda b: b.delivered_on and b.booked_on and (b.delivered_on - b.booked_on).days <= 3
        )
        rows.append(
            {
                "courier": partner.name,
                "bookings": len(mine),
                "delivered": len(delivered),
                "returned": len(returned),
                "on_time_pct": round(100.0 * len(on_time) / len(closed), 1) if closed else None,
                "charges": round(sum(mine.mapped("charged_amount")), 2),
                "cod_open": round(
                    sum(mine.filtered(lambda b: not b.cod_settled_on).mapped("cod_amount")), 2
                ),
            }
        )
    return {
        "title": "Courier Performance - %d booking(s) across %d partner(s)"
        % (len(bookings), len(partners)),
        "cols": [
            "courier",
            "bookings",
            "delivered",
            "returned",
            "on_time_pct",
            "charges",
            "cod_open",
        ],
        "labels": {
            "courier": "Courier",
            "bookings": "Bookings",
            "delivered": "Delivered",
            "returned": "Returned",
            "on_time_pct": "On-time %",
            "charges": "Charges",
            "cod_open": "COD not settled",
        },
        "rows": rows,
        "notes": [
            "On-time = delivered within 3 days of booking, measured from the booking "
            "and delivery dates. COD not settled is cash the partner still holds."
        ],
        "empty": "No courier bookings yet.",
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
