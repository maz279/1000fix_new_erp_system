# A02 · M03 Service Logistics (Pick & Drop) — models the generic workspace
# screens may read, the workflow methods they may call (/p03/model/records,
# /p03/model/action), the module KPI payload (/p03/logistics/kpis) and the
# built-in reports (/p03/model/report). Same contract as a02/m01..m31.
import logging

from odoo import fields, http
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
            # BRU-LOG-03: the second signature on a high-value dispatch
            "action_countersign_dispatch",
        },
    },
    "fix.courier.partner": {"order": "name", "limit": 100, "actions": set()},
    "fix.courier.booking": {
        "order": "booked_on desc, id desc",
        "limit": 400,
        # A02 audit M03-P2: pick-up starts the consignment's custody, and
        # delivery closes it on the courier's POD. M03 audit 2026-11-13: the
        # POD itself could not be recorded (guarded field, method not served),
        # so no courier booking could ever be marked delivered.
        "actions": {"action_pick_up", "action_record_pod", "action_deliver"},
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
    # BRU-LOG-05: who may carry restricted items (recorded by a logistics manager)
    "fix.rider.certification": {
        "order": "valid_until desc, id desc",
        "limit": 300,
        "actions": set(),
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
    # the business day in the user's time zone (Asia/Dhaka), not the server's UTC date
    today = fields.Date.context_today(env.user)

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

    # M03 audit 2026-11-13: a lost leg with a broken chain was counted twice,
    # and a seal or weight tamper hold (the headline custody exception) not at all
    custody_exceptions = Cons.search_count(
        [
            *domain,
            "|",
            "|",
            ("chain_broken", "=", True),
            ("state", "in", ("lost", "held")),
            ("seal_status", "=", "tampered_mismatch"),
        ]
    )

    # COD Today is money (BDT), not a count of settlement sheets: the cash
    # riders handed over today, in the caller's companies
    cod_today = None
    if "fix.cod.settlement" in env:
        Settlement = env["fix.cod.settlement"].sudo()
        todays = Settlement.search(
            [
                ("company_id", "in", env.companies.ids),
                ("settlement_date", "=", today),
                ("state", "!=", "disputed"),
            ]
        )
        cod_today = round(sum(todays.mapped("remitted_amount")), 2)

    round_trips = [
        ((c.delivered_at or c.write_date) - c.create_date).total_seconds() / 86400.0
        for c in delivered
        if c.create_date and (c.delivered_at or c.write_date)
    ]
    avg_round_trip = round(sum(round_trips) / len(round_trips), 1) if round_trips else None

    # rider shifts: no rider-shift model exists (P09 app scope) — honest null
    # (the tile is marked src:false — no data source — in static/src/a02/m03.js)
    return {
        "in_transit": in_transit,
        "on_time_delivery": on_time_pct,
        "custody_exceptions": custody_exceptions,
        "cod_today": cod_today,
        "avg_round_trip": avg_round_trip,
        "rider_shifts_open": None,
    }


# ---------------------------------------------------------------- reports


def _labels(model, field):
    """Selection key -> label for a report cell (rows showed raw keys)."""
    return dict(model._fields[field]._description_selection(model.env))


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
    """Custody Exception Register (spec §14: seal breaks, discrepancies,
    unexplained gaps). M03 audit 2026-11-13: it listed broken chains and lost
    legs only - a seal or weight tamper hold, the headline exception, was
    missing (the Sealing & Tamper Log showed none) - and a lost leg with a
    broken chain appeared twice. One row per consignment, every issue named."""
    Cons = _cons(env)
    types = _labels(Cons, "consignment_type")
    states = _labels(Cons, "state")
    seals = _labels(Cons, "seal_status")
    found = Cons.search(
        [
            "|",
            "|",
            "|",
            ("chain_broken", "=", True),
            ("state", "in", ("lost", "held")),
            ("seal_status", "=", "tampered_mismatch"),
            ("custody_ids.exception_reason", "!=", False),
        ],
        order="scheduled_date desc, id desc",
        limit=500,
    )
    rows = []
    for c in found:
        issues = []
        if c.seal_status == "tampered_mismatch" or c.hold_reason:
            issues.append(c.hold_reason or seals.get(c.seal_status, ""))
        if c.chain_broken:
            issues.append("Broken chain: %s" % (c.chain_problem or "out of order"))
        if c.state == "lost":
            issues.append("Reported lost: %s" % (c.exception_note or "no reason recorded"))
        notes = [s.exception_reason for s in c.custody_ids if s.exception_reason]
        if notes:
            issues.append("Scan exception: %s" % "; ".join(notes))
        rows.append(
            {
                "consignment": c.name,
                "type": types.get(c.consignment_type, c.consignment_type),
                "state": states.get(c.state, c.state),
                "seal": seals.get(c.seal_status, c.seal_status or ""),
                "variance_g": c.weight_variance_g or None,
                "issue": " | ".join(i for i in issues if i),
                "released_by": c.hold_released_by_id.name or "",
                "chain": c.custody_summary or "",
            }
        )
    return {
        "title": "Custody Exception Register",
        "cols": [
            "consignment",
            "type",
            "state",
            "seal",
            "variance_g",
            "issue",
            "released_by",
            "chain",
        ],
        "labels": {
            "consignment": "Consignment",
            "type": "Type",
            "state": "State",
            "seal": "Seal Verdict",
            "variance_g": "Weight Variance (g)",
            "issue": "Exception",
            "released_by": "Hold Released By",
            "chain": "Recorded Chain",
        },
        "rows": rows,
        "notes": [
            "Seal or weight mismatches at hub intake (the leg is held until a logistics "
            "manager releases it), broken custody chains, lost consignments and scans "
            "recorded with an exception. One row per consignment."
        ],
        "empty": "No custody exception recorded.",
    }


def _courier_performance_report(env, **params):
    """Courier performance from the real booking records. M03 audit
    2026-11-13: on-time used a fixed 3 days although each partner carries its
    contractual SLA, and 'COD not settled' summed cash on returned and
    cancelled bookings, which the courier never collected."""
    bookings = env["fix.courier.booking"].sudo().search([("company_id", "in", env.companies.ids)])
    partners = env["fix.courier.partner"].sudo().search([("company_id", "in", env.companies.ids)])
    rows = []
    for partner in partners:
        mine = bookings.filtered(lambda b, p=partner: b.partner_id.id == p.id)
        delivered = mine.filtered(lambda b: b.state == "delivered")
        returned = mine.filtered(lambda b: b.state == "returned")
        sla_days = max(1, -(-(partner.sla_delivery_hours or 48) // 24))
        on_time = delivered.filtered(
            lambda b, d=sla_days: b.delivered_on
            and b.booked_on
            and (b.delivered_on - b.booked_on).days <= d
        )
        rows.append(
            {
                "courier": partner.name,
                "sla": "%dh" % (partner.sla_delivery_hours or 48),
                "bookings": len(mine),
                "delivered": len(delivered),
                "returned": len(returned),
                "on_time_pct": round(100.0 * len(on_time) / len(delivered), 1)
                if delivered
                else None,
                "charges": round(sum(mine.mapped("charged_amount")), 2),
                "cod_open": round(
                    sum(delivered.filtered(lambda b: not b.cod_settled_on).mapped("cod_amount")),
                    2,
                ),
            }
        )
    return {
        "title": "Courier Performance - %d booking(s) across %d partner(s)"
        % (len(bookings), len(partners)),
        "cols": [
            "courier",
            "sla",
            "bookings",
            "delivered",
            "returned",
            "on_time_pct",
            "charges",
            "cod_open",
        ],
        "labels": {
            "courier": "Courier",
            "sla": "Delivery SLA",
            "bookings": "Bookings",
            "delivered": "Delivered",
            "returned": "Returned",
            "on_time_pct": "On-time %",
            "charges": "Charges (৳)",
            "cod_open": "COD Held by Courier (৳)",
        },
        "rows": rows,
        "notes": [
            "On-time = delivered within the courier's contractual SLA (booking date to "
            "delivery date, whole days). COD held is cash on delivered bookings the "
            "courier has not yet paid over (Treasury M50 courier remittance)."
        ],
        "empty": "No courier bookings yet.",
    }


def _cod_settlement_report(env, **params):
    """Rider cash hand-overs (M50 settlements). M03 audit 2026-11-13: it had
    no rider column although BRU-LOG-06 reconciles per rider, and showed raw
    state keys."""
    rows = []
    if "fix.cod.settlement" in env:
        Settlement = env["fix.cod.settlement"].sudo()
        states = _labels(Settlement, "state")
        for s in Settlement.search(
            [("company_id", "in", env.companies.ids)],
            order="settlement_date desc, id desc",
            limit=200,
        ):
            rows.append(
                {
                    "settlement": s.name or str(s.id),
                    "date": str(s.settlement_date or "")[:10],
                    "rider": s.rider_id.name or "",
                    "orders": s.order_count,
                    "expected": s.expected_amount,
                    "remitted": s.remitted_amount,
                    "variance": s.variance,
                    "state": states.get(s.state, s.state or ""),
                }
            )
    return {
        "title": "COD Settlement Report",
        "cols": [
            "settlement",
            "date",
            "rider",
            "orders",
            "expected",
            "remitted",
            "variance",
            "state",
        ],
        "labels": {
            "settlement": "Settlement",
            "date": "Date",
            "rider": "Rider",
            "orders": "COD Orders",
            "expected": "Expected (৳)",
            "remitted": "Remitted (৳)",
            "variance": "Variance (৳)",
            "state": "State",
        },
        "rows": rows,
        "notes": [
            "Each rider's cash hand-over, reconciled against the delivered cash-on-delivery "
            "orders (BRU-LOG-06: zero tolerance for an unexplained variance; a shortage "
            "needs an approval and is recovered through HR). Prepared and settled in "
            "Treasury (M50)."
        ],
        "empty": "No rider cash hand-over recorded yet.",
    }


def _reverse_volume_report(env, **params):
    """Reverse logistics: returns to vendor (FR-LOG-024) and legs returned to
    origin (FR-LOG-026). M03 audit 2026-11-13: it counted returned-to-origin
    legs only - every return to vendor was missing."""
    Cons = _cons(env)
    types = _labels(Cons, "consignment_type")
    states = _labels(Cons, "state")
    found = Cons.search(
        ["|", ("state", "=", "returned"), ("consignment_type", "=", "return_to_vendor")],
        order="scheduled_date desc, id desc",
        limit=300,
    )
    rows = [
        {
            "consignment": c.name,
            "flow": "Return to vendor"
            if c.consignment_type == "return_to_vendor"
            else "Returned to origin",
            "type": types.get(c.consignment_type, c.consignment_type),
            "state": states.get(c.state, c.state),
            "reference": c.purchase_order_id.display_name or c.service_order_id.display_name or "",
            "reason": c.exception_note or "",
            "chain": c.custody_summary or "",
        }
        for c in found
    ]
    return {
        "title": "Reverse Logistics Volume",
        "cols": ["consignment", "flow", "type", "state", "reference", "reason", "chain"],
        "labels": {
            "consignment": "Consignment",
            "flow": "Reverse Flow",
            "type": "Type",
            "state": "State",
            "reference": "Order / PO",
            "reason": "Return Reason",
            "chain": "Chain",
        },
        "rows": rows,
        "notes": ["Returns to vendor (any state) and legs returned to origin."],
        "empty": "No reverse logistics movement yet.",
    }


def _damage_claims_report(env, **params):
    """Damage & Insurance Claims (spec §14 loss and damage register). M03
    audit 2026-11-13: it listed lost consignments only, ignored the claim
    records (fix.damage.claim, with its M63 DOFA approval) and said the claims
    engine was 'a later phase'. Claims first, then lost legs with no claim."""
    Claim = env["fix.damage.claim"].sudo()
    Cons = _cons(env)
    kinds = _labels(Claim, "damage_kind")
    states = _labels(Claim, "state")
    liability = _labels(Claim, "liability")
    claims = Claim.search(
        [("company_id", "in", env.companies.ids)] if "company_id" in Claim._fields else [],
        order="claimed_on desc, id desc",
        limit=300,
    )
    rows = [
        {
            "ref": c.name,
            "consignment": c.consignment_id.name or "",
            "kind": kinds.get(c.damage_kind, c.damage_kind or ""),
            "liability": liability.get(c.liability, c.liability or ""),
            "claimed": c.claimed_amount or None,
            "approved": c.approved_amount or None,
            "settled": c.settled_amount or None,
            "state": states.get(c.state, c.state or ""),
        }
        for c in claims
    ]
    claimed = set(claims.mapped("consignment_id").ids)
    for c in Cons.search([("state", "=", "lost")], limit=200):
        if c.id in claimed:
            continue
        rows.append(
            {
                "ref": "No claim yet",
                "consignment": c.name,
                "kind": "Lost in transit",
                "liability": "",
                "claimed": None,
                "approved": None,
                "settled": None,
                "state": "Candidate: last custody %s" % (c.custody_summary or "unknown"),
            }
        )
    return {
        "title": "Damage & Insurance Claims",
        "cols": [
            "ref",
            "consignment",
            "kind",
            "liability",
            "claimed",
            "approved",
            "settled",
            "state",
        ],
        "labels": {
            "ref": "Claim",
            "consignment": "Consignment",
            "kind": "Damage Kind",
            "liability": "Liability",
            "claimed": "Claimed (৳)",
            "approved": "Approved (৳)",
            "settled": "Settled (৳)",
            "state": "State",
        },
        "rows": rows,
        "notes": [
            "Claims raised on consignments, with the payout approved in the M63 approval "
            "inbox (DOFA tier; never by the person who raised it; capped at the claim and "
            "the declared value). Lost consignments without a claim follow as candidates."
        ],
        "empty": "No damage claim and no lost consignment.",
    }


def _zone_charges_report(env, **params):
    """Distance & Zone Charging: the freight leg's own charging basis —
    origin branch → destination branch with weight and the money columns
    (M03 sweep audit 2026-11-06: the screen previously borrowed the courier
    report; this is the consignment's own charge register)."""
    Cons = _cons(env)
    groups = {}
    for c in Cons.search([], limit=400):
        key = (
            c.origin_branch_id.name or "—",
            c.dest_branch_id.name or "—",
        )
        row = groups.setdefault(
            key,
            {
                "consignments": 0,
                "chargeable_kg": 0.0,
                "base_freight": 0.0,
                "surcharge": 0.0,
                "insurance": 0.0,
            },
        )
        row["consignments"] += 1
        row["chargeable_kg"] += c.chargeable_weight_kg or 0.0
        row["base_freight"] += c.base_freight_bdt or 0.0
        row["surcharge"] += c.volumetric_surcharge_bdt or 0.0
        row["insurance"] += c.insurance_fee_bdt or 0.0
    rows = [
        {
            "origin": origin,
            "destination": destination,
            "consignments": v["consignments"],
            "chargeable_kg": round(v["chargeable_kg"], 2) or None,
            "base_freight": round(v["base_freight"], 2) or None,
            "surcharge": round(v["surcharge"], 2) or None,
            "insurance": round(v["insurance"], 2) or None,
            "total": round(v["base_freight"] + v["surcharge"] + v["insurance"], 2) or None,
        }
        for (origin, destination), v in sorted(groups.items())
    ]
    return {
        "title": "Distance & Zone Charging",
        "cols": [
            "origin",
            "destination",
            "consignments",
            "chargeable_kg",
            "base_freight",
            "surcharge",
            "insurance",
            "total",
        ],
        "labels": {
            "origin": "Origin Branch",
            "destination": "Destination Branch",
            "consignments": "Consignments",
            "chargeable_kg": "Chargeable (kg)",
            "base_freight": "Base Freight (৳)",
            "surcharge": "Volumetric Surcharge (৳)",
            "insurance": "Insurance (৳)",
            "total": "Total (৳)",
        },
        "rows": rows,
        "notes": [
            "Every leg, priced from its courier's tariff (base + per-kg) or, for an own-fleet "
            "leg, the default BDT 80 + 40/kg until a zone tariff is set; insurance is 1% of "
            "the declared value. Computed per leg - no logistics invoice is raised yet (M20)."
        ],
    }


def _manifest_register_report(env, **params):
    """Item Manifests: the dispatch manifest per consignment — packaging,
    security bag, seals, weights and declared value (M03 sweep audit
    2026-11-06: the screen previously borrowed the cycle-time report)."""
    Cons = _cons(env)
    type_labels = dict(Cons._fields["consignment_type"].selection)
    state_labels = dict(Cons._fields["state"].selection)
    pkg_labels = dict(Cons._fields["packaging_type"].selection)
    rows = []
    for c in Cons.search([], order="scheduled_date desc, id desc", limit=200):
        rows.append(
            {
                "name": c.name,
                "type": type_labels.get(c.consignment_type, c.consignment_type),
                "state": state_labels.get(c.state, c.state),
                "packaging": pkg_labels.get(c.packaging_type, c.packaging_type or "—"),
                "bag": c.security_bag_barcode or "—",
                "seal": c.outbound_seal_number or "—",
                "chargeable_kg": c.chargeable_weight_kg or None,
                "declared": c.declared_value_bdt or None,
            }
        )
    return {
        "title": "Item Manifests",
        "cols": ["name", "type", "state", "packaging", "bag", "seal", "chargeable_kg", "declared"],
        "labels": {
            "name": "Consignment No.",
            "type": "Type",
            "state": "State",
            "packaging": "Packaging",
            "bag": "Security Bag",
            "seal": "Outbound Seal",
            "chargeable_kg": "Chargeable (kg)",
            "declared": "Declared Value (৳)",
        },
        "rows": rows,
        "notes": [
            "The physical dispatch manifest fields each consignment carries; "
            "weights reconcile at hub intake (variance is flagged on the leg)."
        ],
    }


def _rider_day_report(env, **params):
    """The rider's day: assigned legs per rider per run date with the live
    state mix and carried weight. Serves Route Manifests and the Rider App
    (P09) preview (route_manifest / rider_day below)."""
    Cons = _cons(env)
    groups = {}
    for c in Cons.search([("rider_id", "!=", False)], limit=400):
        stamp = c.scheduled_date or c.create_date
        day = stamp.date() if hasattr(stamp, "date") else stamp
        key = (c.rider_id.name, day)
        row = groups.setdefault(
            key, {"jobs": 0, "open": 0, "transit": 0, "delivered": 0, "kg": 0.0, "value": 0.0}
        )
        row["jobs"] += 1
        if c.state in ("draft", "confirmed"):
            row["open"] += 1
        elif c.state in ("in_transit", "held"):
            row["transit"] += 1
        elif c.state in ("delivered", "returned"):
            row["delivered"] += 1
        row["kg"] += c.chargeable_weight_kg or 0.0
        row["value"] += c.declared_value_bdt or 0.0
    rows = [
        {
            "rider": rider,
            "day": str(day),
            "jobs": v["jobs"],
            "to_start": v["open"] or None,
            "in_progress": v["transit"] or None,
            "completed": v["delivered"] or None,
            "chargeable_kg": round(v["kg"], 2) or None,
            "declared": round(v["value"], 2) or None,
        }
        for (rider, day), v in sorted(groups.items(), key=lambda kv: (kv[0][1], kv[0][0]))
    ]
    return {
        "title": params.get("_title") or "Rider App (P09) Preview",
        "cols": [
            "rider",
            "day",
            "jobs",
            "to_start",
            "in_progress",
            "completed",
            "chargeable_kg",
            "declared",
        ],
        "labels": {
            "rider": "Rider",
            "day": "Run Date",
            "jobs": "Legs",
            "to_start": "Not Started",
            "in_progress": "In Transit / Held",
            "completed": "Delivered / Returned",
            "chargeable_kg": "Load (kg)",
            "declared": "Load Value (৳)",
        },
        "rows": rows,
        "notes": [
            params.get("_note")
            or "What P09 shows the rider at day start: assigned legs by run date with "
            "the live state mix, carried weight and value."
        ],
        "empty": "No consignment has a rider assigned.",
    }


def _route_manifest_report(env, **params):
    """Route Manifests: the same rider-day grouping, titled for the
    coordinator (there is no stored manifest record; stop sequencing and route
    optimisation are not built - FR-LOG-014)."""
    return _rider_day_report(
        env,
        _title="Route Manifests",
        _note="Each rider's legs per run date with the load carried (weight and declared "
        "value, for FR-LOG-029 load limits). Stop order is not sequenced yet.",
    )


REPORTS = {
    "cycle_time": _cycle_time_report,
    "custody_exceptions": _custody_exception_report,
    "courier_performance": _courier_performance_report,
    "cod_settlement": _cod_settlement_report,
    "reverse_volume": _reverse_volume_report,
    "damage_claims": _damage_claims_report,
    # M03 sweep audit 2026-11-06: the three screens that borrowed the nearest
    # report now have their own computed packs (D14/D17 variant fix).
    "zone_charges": _zone_charges_report,
    "manifest_register": _manifest_register_report,
    "rider_day": _rider_day_report,
    "route_manifest": _route_manifest_report,
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
