# A04 · M09 Warranty & Claims — surfaces, report packs and KPIs over the real
# fix.warranty (55) / .claim (3) / .evidence / .product / .provision and the
# new transfer, recall and appeal models. Every cycle/latency figure is read
# from recorded timestamps; an unmeasurable ratio stays declared.
from odoo import fields, http
from odoo.http import request

from ..p03_service_order_api import _require_internal

SURFACES = {
    # fix.warranty is owned by M01 (a02 surface) — read through the merged
    # registry; not declared twice.
    # A04 workflow audit (2026-11-03) M09-11: every surface declared
    # `actions: set()`, so the only path the workspace offered was editing
    # `state`. The lifecycles are whitelisted; each method checks its own
    # role, state and segregation of duties (cd_warranty_claims).
    "fix.warranty.claim": {
        "order": "created_at desc, id desc",
        "limit": 300,
        "actions": {
            "action_assemble_workshop_evidence_pack",
            "action_refresh_amount",
            "action_submit",
            "action_mark_in_review",
            "action_propose_approve",
            "action_propose_partial",
            "action_propose_reject",
            "action_recall_approval",
            "action_close",
            "action_confirm_device_recheck",
        },
    },
    "fix.warranty.evidence": {
        "order": "id desc",
        "limit": 300,
        "actions": set(),
    },
    "fix.warranty.product": {
        "order": "name",
        "limit": 200,
        "actions": set(),
    },
    # fix.warranty.provision(.policy) are owned by M53 (a08 surface).
    "fix.warranty.transfer": {
        "order": "effective_date desc, id desc",
        "limit": 200,
        "actions": {"action_approve", "action_effect", "action_void"},
    },
    "fix.warranty.recall": {
        "order": "launched_on desc, id desc",
        "limit": 200,
        "actions": {"action_launch", "action_complete", "action_cancel"},
    },
    "fix.claim.appeal": {
        "order": "create_date desc, id desc",
        "limit": 200,
        "actions": {"action_uphold", "action_reject_appeal"},
    },
}

DECIDED = ("approved", "partially_approved", "rejected", "remitted", "closed")
RECOVERED = ("approved", "partially_approved", "remitted", "closed")


def _pack(title, cols, labels, rows, notes, totals=None, empty=None):
    return {
        "title": title,
        "cols": cols,
        "labels": labels,
        "rows": rows,
        "totals": totals,
        "notes": notes,
        "empty": empty or "No data in this basis yet.",
    }


def _claims(env):
    # A04 M09-14: read in the user's environment, so the operating-unit
    # isolation rule applies to the packs and KPIs too (it used sudo()).
    return env["fix.warranty.claim"].search([])


def _today(env):
    # A04 M09-14: the business date (Asia/Dhaka), not the host's.
    return fields.Date.context_today(env["fix.warranty.claim"])


def claim_ageing_by_brand(env, date_from=None, date_to=None, **params):
    claims = _claims(env)
    today = _today(env)
    by_brand = {}
    for claim in claims:
        brand = claim.brand_id
        row = by_brand.setdefault(
            brand.id if brand else 0,
            {
                "brand": brand.name if brand else "Unassigned",
                "claims": 0,
                "amount": 0.0,
                "age_days": [],
            },
        )
        row["claims"] += 1
        row["amount"] += claim.claim_amount or 0.0
        if claim.created_at:
            row["age_days"].append((today - claim.created_at.date()).days)
    rows = []
    for row in by_brand.values():
        ages = row["age_days"]
        rows.append(
            {
                "brand": row["brand"],
                "claims": row["claims"],
                "amount": round(row["amount"], 2),
                "avg_age_days": round(sum(ages) / len(ages), 1) if ages else 0.0,
                "oldest_days": max(ages) if ages else 0,
            }
        )
    rows.sort(key=lambda r: -r["avg_age_days"])
    return _pack(
        "Claim Ageing by Brand",
        ["brand", "claims", "amount", "avg_age_days", "oldest_days"],
        {
            "brand": "Brand",
            "claims": "Claims",
            "amount": "Claim Amount",
            "avg_age_days": "Avg Age (days)",
            "oldest_days": "Oldest (days)",
        },
        rows,
        [
            "Age is calendar days since the claim was created — open claims age, "
            "decided ones are still shown for the brand's full picture."
        ],
        totals={
            "brand": "Total",
            "claims": len(claims),
            "amount": round(sum(r["amount"] for r in rows), 2),
        }
        if rows
        else None,
        empty="No warranty claims yet.",
    )


def reimbursement_cycle(env, date_from=None, date_to=None, **params):
    claims = _claims(env).filtered(lambda c: c.submitted_at and c.decided_at)
    by_brand = {}
    for claim in claims:
        hours = (claim.decided_at - claim.submitted_at).total_seconds() / 3600.0
        row = by_brand.setdefault(
            claim.brand_id.id,
            {
                "brand": claim.brand_id.name or "—",
                "claims": 0,
                "hours": 0.0,
            },
        )
        row["claims"] += 1
        row["hours"] += hours
    rows = []
    for row in by_brand.values():
        rows.append(
            {
                "brand": row["brand"],
                "claims": row["claims"],
                "avg_hours": round(row["hours"] / row["claims"], 1),
                "avg_days": round(row["hours"] / row["claims"] / 24.0, 1),
            }
        )
    rows.sort(key=lambda r: -r["avg_days"])
    return _pack(
        "Reimbursement Cycle Time",
        ["brand", "claims", "avg_hours", "avg_days"],
        {
            "brand": "Brand",
            "claims": "Decided Claims",
            "avg_hours": "Avg Cycle (h)",
            "avg_days": "Avg Cycle (days)",
        },
        rows,
        ["Cycle = submitted_at → decided_at, averaged per brand over decided claims."],
        empty="No claim has both a submission and a decision timestamp yet.",
    )


def claim_rejection(env, date_from=None, date_to=None, **params):
    rejected = _claims(env).filtered(lambda c: c.state == "rejected")
    reasons = {}
    for claim in rejected:
        key = (claim.rejection_reason or "unspecified").strip() or "unspecified"
        reasons[key] = reasons.get(key, 0) + 1
    total = len(rejected)
    rows = []
    cumulative = 0
    for reason, count in sorted(reasons.items(), key=lambda kv: -kv[1]):
        cumulative += count
        rows.append(
            {
                "reason": reason,
                "claims": count,
                "share_pct": round(count / total * 100.0, 1) if total else 0.0,
                "cumulative_pct": round(cumulative / total * 100.0, 1) if total else 0.0,
            }
        )
    return _pack(
        "Claim Rejection Analysis",
        ["reason", "claims", "share_pct", "cumulative_pct"],
        {
            "reason": "Rejection Reason",
            "claims": "Claims",
            "share_pct": "Share %",
            "cumulative_pct": "Cumulative %",
        },
        rows,
        ["Reasons are recorded on the brand decision (rejection_reason)."],
        totals={"reason": "Total", "claims": total} if rows else None,
        empty="No rejected claims yet.",
    )


def evidence_completeness(env, date_from=None, date_to=None, **params):
    claims = _claims(env)
    rows = []
    for claim in claims:
        rows.append(
            {
                "claim": claim.claim_no,
                "state": claim.state,
                "evidence": len(claim.evidence_ids),
                "complete": "✓" if claim.evidence_complete else "✗",
                "missing": claim.missing_evidence or "—",
            }
        )
    complete = len(claims.filtered(lambda c: c.evidence_complete))
    return _pack(
        "Evidence Completeness",
        ["claim", "state", "evidence", "complete", "missing"],
        {
            "claim": "Claim",
            "state": "State",
            "evidence": "Evidence Files",
            "complete": "Complete",
            "missing": "Missing Evidence",
        },
        rows,
        [
            "Evidence completeness is the claim's own flag and file count. "
            "Complete: %d of %d claims (%.1f%%)."
            % (complete, len(claims), complete / len(claims) * 100.0 if claims else 0.0)
        ],
        empty="No warranty claims yet.",
    )


def loss_ratio(env, date_from=None, date_to=None, **params):
    claims = _claims(env)
    products = env["fix.warranty.product"].search([])
    claimed = sum(claims.mapped("claim_amount"))
    remitted = sum(claims.mapped("remittance_amount"))
    exposure = sum((p.claim_limit or 0.0) for p in products)
    rows = [
        {"metric": "Claims raised", "value": len(claims), "basis": "fix.warranty.claim"},
        {"metric": "Claim value", "value": round(claimed, 2), "basis": "claim_amount"},
        {"metric": "Remitted by brands", "value": round(remitted, 2), "basis": "remittance_amount"},
        {
            "metric": "Product claim limits (exposure)",
            "value": round(exposure, 2),
            "basis": "sum of warranty-product claim_limit",
        },
        {
            "metric": "Observed loss ratio",
            "value": round(claimed / exposure * 100.0, 1) if exposure else 0.0,
            "basis": "claim value / exposure",
        },
    ]
    return _pack(
        "Loss Ratio by Product",
        ["metric", "value", "basis"],
        {"metric": "Measure", "value": "Value", "basis": "Basis"},
        rows,
        [
            "Observed ratio = claims / the products' claim limits. Premium revenue "
            "is not linked to warranty products in the data model, so an actuarial "
            "loss ratio is a declared gap — this is the observable one."
        ],
    )


def recall_coverage(env, date_from=None, date_to=None, **params):
    recalls = env["fix.warranty.recall"].search([])
    rows = []
    for recall in recalls:
        coverage = (
            round(recall.covered_units / recall.affected_units * 100.0, 1)
            if recall.affected_units
            else 0.0
        )
        rows.append(
            {
                "recall": recall.name,
                "brand": recall.brand_id.name or "—",
                "affected": recall.affected_units,
                "covered": recall.covered_units,
                "coverage_pct": coverage,
                "state": recall.state,
            }
        )
    rows.sort(key=lambda r: r["coverage_pct"])
    return _pack(
        "Recall Coverage Report",
        ["recall", "brand", "affected", "covered", "coverage_pct", "state"],
        {
            "recall": "Recall",
            "brand": "Brand",
            "affected": "Affected Units",
            "covered": "Covered Units",
            "coverage_pct": "Coverage %",
            "state": "State",
        },
        rows,
        [
            "Coverage is the units actually contacted/serviced over the affected "
            "population recorded on the campaign."
        ],
        empty="No recall campaigns yet.",
    )


def warranty_validation(env, date_from=None, date_to=None, **params):
    warranties = env["fix.warranty"].search([])
    today = _today(env)
    rows = []
    for warranty in warranties:
        days_left = (warranty.end_date - today).days if warranty.end_date else None
        rows.append(
            {
                "warranty": warranty.device_id.display_name or "—",
                "type": warranty.warranty_type,
                "status": warranty.status,
                "start": str(warranty.start_date) if warranty.start_date else "—",
                "end": str(warranty.end_date) if warranty.end_date else "—",
                "days_left": days_left if days_left is not None else "—",
            }
        )
    rows.sort(key=lambda r: r["days_left"] if isinstance(r["days_left"], int) else 99999)
    return _pack(
        "Manufacturer Validation",
        ["warranty", "type", "status", "start", "end", "days_left"],
        {
            "warranty": "Device / Warranty",
            "type": "Type",
            "status": "Status",
            "start": "Start",
            "end": "End",
            "days_left": "Days Left",
        },
        rows,
        [
            "Manufacturer validation = the recorded warranty window and status per "
            "device. A negative days-left is an expired coverage."
        ],
        empty="No warranties registered yet.",
    )


def warranty_repairs(env, date_from=None, date_to=None, **params):
    claims = _claims(env)
    rows = []
    for claim in claims:
        order = claim.service_order_id
        rows.append(
            {
                "claim": claim.claim_no,
                "order": order.name if order else "—",
                "state": claim.state,
                "amount": round(claim.claim_amount or 0.0, 2),
                "remitted": round(claim.remittance_amount or 0.0, 2),
            }
        )
    return _pack(
        "Repair Warranty & Rework",
        ["claim", "order", "state", "amount", "remitted"],
        {
            "claim": "Claim",
            "order": "Service Order",
            "state": "State",
            "amount": "Claim Amount",
            "remitted": "Remitted",
        },
        rows,
        [
            "A claim is a warranty repair that the brand must reimburse; the order "
            "link is the rework record."
        ],
        empty="No warranty claims yet.",
    )


def brand_claim_stats(env, date_from=None, date_to=None, **params):
    claims = _claims(env)
    by_brand = {}
    for claim in claims:
        row = by_brand.setdefault(
            claim.brand_id.id,
            {
                "brand": claim.brand_id.name or "—",
                "claims": 0,
                "approved": 0,
                "rejected": 0,
                "remitted": 0.0,
                "claimed": 0.0,
            },
        )
        row["claims"] += 1
        if claim.state in RECOVERED and claim.approved_amount:
            row["approved"] += 1
        if claim.state == "rejected":
            row["rejected"] += 1
        row["remitted"] += claim.remittance_amount or 0.0
        row["claimed"] += claim.claim_amount or 0.0
    rows = []
    for row in by_brand.values():
        decided = row["approved"] + row["rejected"]
        rows.append(
            {
                "brand": row["brand"],
                "claims": row["claims"],
                "approval_pct": round(row["approved"] / decided * 100.0, 1) if decided else 0.0,
                "rejected": row["rejected"],
                "claimed": round(row["claimed"], 2),
                "remitted": round(row["remitted"], 2),
            }
        )
    rows.sort(key=lambda r: -r["claims"])
    return _pack(
        "Brand Rules & Claim Formats — per-brand outcomes",
        ["brand", "claims", "approval_pct", "rejected", "claimed", "remitted"],
        {
            "brand": "Brand",
            "claims": "Claims",
            "approval_pct": "Approval %",
            "rejected": "Rejected",
            "claimed": "Claimed",
            "remitted": "Remitted",
        },
        rows,
        [
            "Per-brand outcome rates are measured from the claim states; the brand "
            "submission FORMAT is not modelled (declared gap)."
        ],
        empty="No warranty claims yet.",
    )


def claim_reconciliation(env, date_from=None, date_to=None, **params):
    claims = _claims(env).filtered(lambda c: c.state in RECOVERED and c.approved_amount)
    rows = []
    for claim in claims:
        # reconciled against what the OEM APPROVED (a partial approval is not
        # a short payment)
        claimed = claim.approved_amount or 0.0
        remitted = claim.remittance_amount or 0.0
        rows.append(
            {
                "claim": claim.claim_no,
                "brand": claim.brand_id.name or "—",
                "claimed": round(claimed, 2),
                "remitted": round(remitted, 2),
                "difference": round(remitted - claimed, 2),
                "state": claim.state,
            }
        )
    rows.sort(key=lambda r: r["difference"])
    return _pack(
        "Brand Reconciliation",
        ["claim", "brand", "claimed", "remitted", "difference", "state"],
        {
            "claim": "Claim",
            "brand": "Brand",
            "claimed": "Approved",
            "remitted": "Remitted",
            "difference": "Remitted − Approved",
            "state": "State",
        },
        rows,
        [
            "A negative difference is a brand short-payment to chase; zero means the "
            "claim reconciled."
        ],
        empty="No approved or remitted claims yet.",
    )


def warranty_fraud(env, date_from=None, date_to=None, **params):
    claims = _claims(env)
    by_device = {}
    for claim in claims:
        if claim.device_id:
            by_device[claim.device_id.id] = by_device.get(claim.device_id.id, 0) + 1
    repeat = [d for d, n in by_device.items() if n > 1]
    no_evidence = claims.filtered(lambda c: not c.evidence_complete)
    same_day = 0
    for claim in claims:
        if (
            claim.created_at
            and claim.job_completed_at
            and claim.created_at.date() == claim.job_completed_at.date()
        ):
            same_day += 1
    rows = [
        {
            "signal": "Devices with more than one claim",
            "count": len(repeat),
            "detail": "Repeat claims on the same device are the primary fraud signal.",
        },
        {
            "signal": "Claims without complete evidence",
            "count": len(no_evidence),
            "detail": "Evidence is mandatory before brand submission.",
        },
        {
            "signal": "Claims raised the same day the job completed",
            "count": same_day,
            "detail": "Same-day submission can indicate fabricated failures; review.",
        },
    ]
    return _pack(
        "Fraud Detection — measured exception signals",
        ["signal", "count", "detail"],
        {"signal": "Signal", "count": "Open Count", "detail": "Why it matters"},
        rows,
        ["Signals are computed from live claim records — no opaque risk score is " "claimed."],
    )


REPORTS = {
    "claim_ageing_by_brand": claim_ageing_by_brand,
    "reimbursement_cycle": reimbursement_cycle,
    "claim_rejection": claim_rejection,
    "evidence_completeness": evidence_completeness,
    "loss_ratio": loss_ratio,
    "recall_coverage": recall_coverage,
    "warranty_validation": warranty_validation,
    "warranty_repairs": warranty_repairs,
    "brand_claim_stats": brand_claim_stats,
    "claim_reconciliation": claim_reconciliation,
    "warranty_fraud": warranty_fraud,
}


def kpis(env):
    claims = _claims(env)
    today = _today(env)
    month_start = today.replace(day=1)
    mtd = claims.filtered(lambda c: c.created_at and c.created_at.date() >= month_start)
    decided = claims.filtered(lambda c: c.state in DECIDED)
    approved = claims.filtered(lambda c: c.state in RECOVERED and c.approved_amount)
    with_both = claims.filtered(lambda c: c.submitted_at and c.decided_at)
    cycle_days = [(c.decided_at - c.submitted_at).total_seconds() / 86400.0 for c in with_both]
    leakage = sum(
        (c.approved_amount or 0.0) - (c.remittance_amount or 0.0)
        for c in approved
        if c.remittance_amount
    )
    under_72h = claims.filtered(
        lambda c: c.submission_latency_hours is not None and c.submission_latency_hours <= 72
    )
    appeals = env["fix.claim.appeal"].search([("decision", "=", "pending")])
    return {
        "claims_submitted_mtd": len(mtd.filtered(lambda c: c.state != "draft")),
        "first_submission_approval": round(len(approved) / len(decided) * 100.0, 1)
        if decided
        else None,
        "reimbursement_days": round(sum(cycle_days) / len(cycle_days), 1) if cycle_days else None,
        "revenue_leakage": round(leakage, 2),
        "claims_under_72h": round(len(under_72h) / len(claims) * 100.0, 1) if claims else None,
        "appeals_open": len(appeals),
    }


class P03WarrantyApi(http.Controller):
    @http.route("/p03/warranty/kpis", type="jsonrpc", auth="user", readonly=True)
    def warranty_kpis(self, module=None, **kw):
        _require_internal(request.env)
        return {"M09": kpis(request.env)}
