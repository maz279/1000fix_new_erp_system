# A03 · M10 Loyalty & Rewards — the surfaces the generic workspace endpoints
# may serve (SURFACES), the five registry report packs and the module KPI
# payload. Every figure is a measured read of fix.loyalty.*; an empty
# programme reports empty, never a demo number.
import datetime

from odoo import http
from odoo.http import request

from ..p03_service_order_api import _require_internal

SURFACES = {
    "fix.loyalty.program": {
        "order": "name",
        "limit": 100,
        "actions": set(),
    },
    "fix.loyalty.tier": {
        "order": "program_id, sequence",
        "limit": 200,
        "actions": set(),
    },
    "fix.loyalty.account": {
        "order": "points_balance desc, id desc",
        "limit": 300,
        # action_activate refuses a frozen wallet. The Tier-2 release is
        # requested here and decided from the M63 inbox; action_unfreeze is
        # the engine's apply method, so it is not offered directly (A03 R7).
        # Reconcile proves the derived balance equals the posted ledger.
        "actions": {
            "action_request_approval",
            "action_recall_approval",
            "action_suspend",
            "action_activate",
            "action_reconcile_balance",
        },
    },
    "fix.loyalty.ledger": {
        "order": "create_date desc, id desc",
        "limit": 300,
        # Without action_dofa_approve no adjustment above 500 points could
        # be approved from any screen (A03 audit). A posted line is corrected
        # by action_reverse, which raises an opposite draft line (R2).
        "actions": {
            "action_post",
            "action_request_approval",
            "action_recall_approval",
            "action_reverse",
        },
    },
    "fix.loyalty.voucher": {
        "order": "valid_from desc, id desc",
        "limit": 300,
        "actions": set(),
    },
    "fix.loyalty.campaign.hook": {
        "order": "create_date desc, id desc",
        "limit": 100,
        "actions": set(),
    },
    "fix.loyalty.referral.code": {
        "order": "create_date desc, id desc",
        "limit": 300,
        "actions": {"action_mark_converted"},
    },
    # --- added by the A03 gap-closure build -------------------
    # Each of these is bound by a workspace screen below; an
    # unservable surface is what test_a03_registry_coverage exists
    # to catch, and a surface no screen opens is dead weight it
    # also catches.
    "fix.loyalty.scheme": {
        "order": "sequence, id",
        "limit": 200,
        "actions": {
            "action_activate",
            "action_request_approval",
            "action_recall_approval",
            "action_retire",
        },
    },
    "fix.loyalty.earn.rule": {
        "order": "scheme_id, priority, id",
        "limit": 300,
        "actions": set(),
    },
    "fix.loyalty.burn.rule": {
        "order": "scheme_id, priority, id",
        "limit": 300,
        "actions": set(),
    },
    "fix.loyalty.point.type": {
        "order": "sequence, id",
        "limit": 200,
        "actions": set(),
    },
    "fix.loyalty.affiliation": {
        "order": "name",
        "limit": 200,
        "actions": set(),
    },
    "fix.loyalty.affiliation.member": {
        "order": "affiliation_id, account_id",
        "limit": 300,
        "actions": set(),
    },
    "fix.loyalty.card": {
        "order": "issued_on desc, id desc",
        "limit": 300,
        "actions": {"action_block"},
    },
}

POSTED = ("posted",)


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


def _month_key(value):
    return value.strftime("%Y-%m") if hasattr(value, "strftime") else str(value)[:7]


def _six_months():
    today = datetime.date.today()
    months = []
    for k in range(5, -1, -1):
        first = (today.replace(day=1) - datetime.timedelta(days=31 * k)).replace(day=1)
        months.append(first)
    return months


def member_growth_tier_mix(env, date_from=None, date_to=None, **params):
    accounts = env["fix.loyalty.account"].sudo().search([])
    tiers = env["fix.loyalty.tier"].sudo().search([])
    rows = []
    for tier in tiers:
        mine = accounts.filtered(lambda a, t=tier: a.tier_id.id == t.id)
        spend = sum(mine.mapped("lifetime_spend_bdt"))
        rows.append(
            {
                "tier": tier.name,
                "members": len(mine),
                "active": len(mine.filtered(lambda a: a.state == "active")),
                "avg_balance": round(sum(mine.mapped("points_balance")) / len(mine), 1)
                if mine
                else 0.0,
                "spend": round(spend, 2),
            }
        )
    no_tier = accounts.filtered(lambda a: not a.tier_id)
    if no_tier:
        rows.append(
            {
                "tier": "No tier assigned",
                "members": len(no_tier),
                "active": len(no_tier.filtered(lambda a: a.state == "active")),
                "avg_balance": round(sum(no_tier.mapped("points_balance")) / len(no_tier), 1),
                "spend": round(sum(no_tier.mapped("lifetime_spend_bdt")), 2),
            }
        )
    totals = {
        "tier": "Total",
        "members": sum(r["members"] for r in rows),
        "active": sum(r["active"] for r in rows),
        "avg_balance": round(sum(accounts.mapped("points_balance")) / len(accounts), 1)
        if accounts
        else 0.0,
        "spend": round(sum(accounts.mapped("lifetime_spend_bdt")), 2),
    }
    return _pack(
        "Member Growth & Tier Mix",
        ["tier", "members", "active", "avg_balance", "spend"],
        {
            "tier": "Tier",
            "members": "Members",
            "active": "Active",
            "avg_balance": "Avg Points Balance",
            "spend": "Lifetime Spend",
        },
        rows,
        [
            "Members are live loyalty accounts grouped by their current tier; "
            "spend is the recorded lifetime spend, never estimated."
        ],
        totals=totals if rows else None,
        empty="No loyalty accounts yet — enrol a member from the Enrolment screen.",
    )


def earn_burn(env, date_from=None, date_to=None, **params):
    ledger = env["fix.loyalty.ledger"].sudo().search([("state", "in", POSTED)])
    buckets = {}
    for line in ledger:
        key = _month_key(line.create_date)
        row = buckets.setdefault(
            key, {"month": key, "earned": 0, "redeemed": 0, "expired": 0, "adjust": 0}
        )
        if line.transaction_type in ("accrual", "campaign_bonus", "referral_bonus"):
            row["earned"] += line.points
        elif line.transaction_type == "redemption":
            row["redeemed"] += abs(line.points)
        elif line.transaction_type == "expiration":
            row["expired"] += abs(line.points)
        else:
            row["adjust"] += line.points
    rows = [buckets[k] for k in sorted(buckets, reverse=True)[:6]]
    totals = {
        "month": "Total",
        "earned": sum(r["earned"] for r in rows),
        "redeemed": sum(r["redeemed"] for r in rows),
        "expired": sum(r["expired"] for r in rows),
        "adjust": sum(r["adjust"] for r in rows),
    }
    return _pack(
        "Points Earn / Burn Analysis — posted ledger",
        ["month", "earned", "redeemed", "expired", "adjust"],
        {
            "month": "Month",
            "earned": "Earned",
            "redeemed": "Redeemed",
            "expired": "Expired",
            "adjust": "Adjustments",
        },
        rows,
        ["Only POSTED ledger lines count; drafts and reversals are excluded."],
        totals=totals if rows else None,
        empty="No posted points movements yet.",
    )


def referral_funnel(env, date_from=None, date_to=None, **params):
    codes = env["fix.loyalty.referral.code"].sudo().search([])
    states = ["pending", "converted", "expired", "cancelled"]
    rows = []
    for state in states:
        mine = codes.filtered(lambda c, s=state: c.state == s)
        rows.append(
            {
                "state": state,
                "codes": len(mine),
                "points": sum(mine.mapped("points_awarded")),
            }
        )
    total = len(codes)
    converted = len(codes.filtered(lambda c: c.state == "converted"))
    conversion = round(converted / total * 100.0, 1) if total else 0.0
    totals = {"state": "Total", "codes": total, "points": sum(r["points"] for r in rows)}
    return _pack(
        "Referral Funnel — code lifecycle",
        ["state", "codes", "points"],
        {"state": "State", "codes": "Codes", "points": "Points Awarded"},
        rows,
        [
            "Conversion %s%% = %d converted of %d codes. Awards are recorded in "
            "points_awarded when the conversion ledger line posts." % (conversion, converted, total)
        ],
        totals=totals if rows else None,
        empty="No referral codes issued yet.",
    )


def voucher_usage_fraud(env, date_from=None, date_to=None, **params):
    vouchers = env["fix.loyalty.voucher"].sudo().search([])
    states = ["draft", "active", "redeemed", "expired", "cancelled"]
    rows = []
    for state in states:
        mine = vouchers.filtered(lambda v, s=state: v.state == s)
        rows.append(
            {
                "state": state,
                "vouchers": len(mine),
                "value": round(sum(mine.mapped("discount_value")), 2),
            }
        )
    same_day = 0
    for v in vouchers.filtered(lambda v: v.state == "redeemed" and v.redeemed_at):
        issued = v.create_date.date() if v.create_date else None
        if issued and v.redeemed_at.date() == issued:
            same_day += 1
    # duplicate redemption signal: same partner redeeming more than one voucher
    by_partner = {}
    for v in vouchers.filtered(lambda v: v.state == "redeemed"):
        by_partner[v.partner_id.id] = by_partner.get(v.partner_id.id, 0) + 1
    multi = [pid for pid, n in by_partner.items() if n > 1]
    # The totals row must total the columns. The fraud signals are different
    # measures, so they go in the notes with their measured values instead of
    # being printed under "Vouchers"/"Face Value" (report_check caught the
    # mismatch: totals said 0 vouchers against 3 rows).
    totals = {
        "state": "Total",
        "vouchers": sum(r["vouchers"] for r in rows),
        "value": round(sum(r["value"] for r in rows), 2),
    }
    return _pack(
        "Voucher Usage & Fraud — lifecycle plus exception signals",
        ["state", "vouchers", "value"],
        {"state": "State", "vouchers": "Vouchers", "value": "Face Value"},
        rows,
        [
            "Fraud signals measured from the records: %d voucher(s) redeemed on their "
            "issue day, and %d partner(s) with more than one redemption." % (same_day, len(multi)),
            "Exception signals are measured from the records: vouchers redeemed on "
            "their issue day and partners with more than one redemption. There is no "
            "black-box fraud score.",
        ],
        totals=totals if rows else None,
        empty="No vouchers issued yet.",
    )


def _program_liability(env):
    accounts = env["fix.loyalty.account"].sudo().search([])
    out = {}
    for acc in accounts:
        program = acc.program_id
        row = out.setdefault(
            program.id if program else 0,
            {
                "program": program.name if program else "No programme",
                "rate": program.bdt_per_point if program else 0.0,
                # IFRS 15: the liability is carried net of the breakage
                # Finance expects. The rate is the programme's
                # expected_breakage_pct, default 0 = the gross figure this
                # report always showed (A03 audit, open finance decision).
                "expected_breakage": program.breakage_rate() if program else 0.0,
                "accounts": 0,
                "outstanding": 0,
                "expired": 0,
                "earned": 0,
            },
        )
        row["accounts"] += 1
        row["outstanding"] += max(0, acc.points_balance)
        row["earned"] += acc.lifetime_points_earned
        row["expired"] += max(
            0, acc.lifetime_points_earned - acc.lifetime_points_redeemed - acc.points_balance
        )
    for row in out.values():
        row["gross_liability"] = round(row["outstanding"] * row["rate"], 2)
        row["liability"] = round(row["gross_liability"] * (1.0 - row["expected_breakage"]), 2)
        row["expected_breakage_pct"] = round(row["expected_breakage"] * 100.0, 2)
        row["breakage_pct"] = (
            round(row["expired"] / row["earned"] * 100.0, 1) if row["earned"] else 0.0
        )
    return out


def points_liability(env, date_from=None, date_to=None, **params):
    data = _program_liability(env)
    rows = [
        {
            "program": r["program"],
            "accounts": r["accounts"],
            "outstanding": r["outstanding"],
            "rate": r["rate"],
            "gross_liability": r["gross_liability"],
            "expected_breakage_pct": r["expected_breakage_pct"],
            "liability": r["liability"],
            "breakage_pct": r["breakage_pct"],
        }
        for r in data.values()
    ]
    rows.sort(key=lambda r: -r["liability"])
    totals = {
        "program": "Total",
        "accounts": sum(r["accounts"] for r in rows),
        "outstanding": sum(r["outstanding"] for r in rows),
        "gross_liability": round(sum(r["gross_liability"] for r in rows), 2),
        "liability": round(sum(r["liability"] for r in rows), 2),
        "breakage_pct": round(sum(r["breakage_pct"] for r in rows) / len(rows), 1) if rows else 0.0,
    }
    return _pack(
        "Liability & Breakage (IFRS 15) — outstanding points valued per programme",
        [
            "program",
            "accounts",
            "outstanding",
            "rate",
            "gross_liability",
            "expected_breakage_pct",
            "liability",
            "breakage_pct",
        ],
        {
            "program": "Programme",
            "accounts": "Accounts",
            "outstanding": "Outstanding Points",
            "rate": "BDT per Point",
            "gross_liability": "Gross Liability",
            "expected_breakage_pct": "Expected Breakage %",
            "liability": "Points Liability (net)",
            "breakage_pct": "Realised Breakage %",
        },
        rows,
        [
            "Gross liability = outstanding points × the programme's own BDT-per-point rate. "
            "Points liability = gross × (1 − expected breakage), the IFRS 15 contract "
            "liability net of the points Finance expects never to be redeemed.",
            "Expected breakage is the programme's 'Expected Breakage %' setting; 0 until "
            "Finance rules on it, so the liability is then the full gross figure.",
            "Realised breakage = points earned but neither redeemed nor still outstanding, "
            "over lifetime earned.",
        ],
        totals=totals if rows else None,
        empty="No loyalty accounts yet — liability is zero until members enrol.",
    )


def programme_profitability(env, date_from=None, date_to=None, **params):
    data = _program_liability(env)
    accounts = env["fix.loyalty.account"].sudo().search([])
    spend_by_program = {}
    for acc in accounts:
        key = acc.program_id.id if acc.program_id else 0
        spend_by_program[key] = spend_by_program.get(key, 0.0) + acc.lifetime_spend_bdt
    ledger = (
        env["fix.loyalty.ledger"]
        .sudo()
        .search([("state", "in", POSTED), ("transaction_type", "=", "redemption")])
    )
    redeemed_by_program = {}
    for line in ledger:
        program = line.account_id.program_id
        key = program.id if program else 0
        redeemed_by_program[key] = redeemed_by_program.get(key, 0) + abs(line.points)
    rows = []
    for key, r in data.items():
        redeemed_pts = redeemed_by_program.get(key, 0)
        cost = round(redeemed_pts * r["rate"], 2)
        spend = round(spend_by_program.get(key, 0.0), 2)
        rows.append(
            {
                "program": r["program"],
                "spend": spend,
                "redeemed_cost": cost,
                "liability": r["liability"],
                "cost_pct": round((cost + r["liability"]) / spend * 100.0, 2) if spend else 0.0,
            }
        )
    rows.sort(key=lambda r: -r["spend"])
    totals = {
        "program": "Total",
        "spend": round(sum(r["spend"] for r in rows), 2),
        "redeemed_cost": round(sum(r["redeemed_cost"] for r in rows), 2),
        "liability": round(sum(r["liability"] for r in rows), 2),
        "cost_pct": round(
            (sum(r["redeemed_cost"] for r in rows) + sum(r["liability"] for r in rows))
            / sum(r["spend"] for r in rows)
            * 100.0,
            2,
        )
        if sum(r["spend"] for r in rows)
        else 0.0,
    }
    return _pack(
        "Programme Profitability — spend, redeemed cost and outstanding liability",
        ["program", "spend", "redeemed_cost", "liability", "cost_pct"],
        {
            "program": "Programme",
            "spend": "Lifetime Spend",
            "redeemed_cost": "Redeemed Points Cost",
            "liability": "Outstanding Liability",
            "cost_pct": "Programme Cost %",
        },
        rows,
        [
            "Cost % = (redeemed cost + outstanding liability) / lifetime spend. "
            "Spend is the recorded spend on the accounts, not a revenue estimate."
        ],
        totals=totals if rows else None,
        empty="No programme spend yet.",
    )


def redemption_rules(env, date_from=None, date_to=None, **params):
    programs = env["fix.loyalty.program"].sudo().search([])
    rows = []
    for p in programs:
        rows.append(
            {
                "program": p.name,
                "points_per_bdt": p.points_per_bdt,
                "bdt_per_point": p.bdt_per_point,
                "min_redeem": p.min_points_to_redeem,
                "expiry_months": p.expiry_months,
                "active": "✓" if p.active else "✗",
            }
        )
    return _pack(
        "Redemption Rules — earn and burn configuration per programme",
        ["program", "points_per_bdt", "bdt_per_point", "min_redeem", "expiry_months", "active"],
        {
            "program": "Programme",
            "points_per_bdt": "Points per BDT",
            "bdt_per_point": "BDT per Point",
            "min_redeem": "Min Points to Redeem",
            "expiry_months": "Expiry (months)",
            "active": "Active",
        },
        rows,
        ["These are the live programme settings used by accrual and redemption."],
        empty="No loyalty programme configured yet.",
    )


def fraud_controls(env, date_from=None, date_to=None, **params):
    accounts = env["fix.loyalty.account"].sudo().search([])
    by_partner = {}
    for acc in accounts:
        by_partner[acc.partner_id.id] = by_partner.get(acc.partner_id.id, 0) + 1
    duplicate_accounts = [pid for pid, n in by_partner.items() if n > 1]
    vouchers = env["fix.loyalty.voucher"].sudo().search([("state", "=", "redeemed")])
    same_day = vouchers.filtered(
        lambda v: v.redeemed_at and v.create_date and v.redeemed_at.date() == v.create_date.date()
    )
    adjustments = (
        env["fix.loyalty.ledger"]
        .sudo()
        .search([("transaction_type", "=", "adjustment"), ("state", "in", POSTED)])
    )
    unexplained = adjustments.filtered(lambda ln: not (ln.notes or "").strip())
    rows = [
        {
            "signal": "Partner with multiple loyalty accounts",
            "count": len(duplicate_accounts),
            "detail": "Account uniqueness per partner is the control.",
        },
        {
            "signal": "Voucher redeemed on its issue day",
            "count": len(same_day),
            "detail": "Bulk same-day redemption — review the campaign distribution.",
        },
        {
            "signal": "Posted adjustment without a narration",
            "count": len(unexplained),
            "detail": "Every manual adjustment must carry its reason.",
        },
    ]
    return _pack(
        "Fraud Controls — measured exception signals",
        ["signal", "count", "detail"],
        {"signal": "Signal", "count": "Open Count", "detail": "Why it matters"},
        rows,
        [
            "Signals are computed from live records; there is no opaque risk score. "
            "Zero means the sampled control currently has no exceptions."
        ],
    )


REPORTS = {
    "member_growth_tier_mix": member_growth_tier_mix,
    "earn_burn": earn_burn,
    "referral_funnel": referral_funnel,
    "voucher_usage_fraud": voucher_usage_fraud,
    "points_liability": points_liability,
    "programme_profitability": programme_profitability,
    "redemption_rules": redemption_rules,
    "fraud_controls": fraud_controls,
}


def kpis(env):
    accounts = env["fix.loyalty.account"].sudo().search([])
    data = _program_liability(env)
    today = datetime.date.today()
    month_start = today.replace(day=1)
    ledger = (
        env["fix.loyalty.ledger"]
        .sudo()
        .search(
            [
                ("state", "in", POSTED),
                ("transaction_type", "=", "redemption"),
                ("create_date", ">=", datetime.datetime.combine(month_start, datetime.time.min)),
            ]
        )
    )
    redeemed = sum(abs(p) for p in ledger.mapped("points"))
    referrals = env["fix.loyalty.referral.code"].sudo().search([("state", "=", "converted")])
    upgrades = accounts.filtered(
        lambda a: a.tier_upgraded_date and a.tier_upgraded_date >= month_start
    )
    earned_total = sum(accounts.mapped("lifetime_points_earned"))
    expired_total = sum(
        max(0, a.lifetime_points_earned - a.lifetime_points_redeemed - a.points_balance)
        for a in accounts
    )
    return {
        "members": len(accounts),
        "points_liability": round(sum(r["liability"] for r in data.values()), 2),
        "redemption_mtd": redeemed,
        "referral_conversions": len(referrals),
        "breakage": round(expired_total / earned_total * 100.0, 1) if earned_total else None,
        "tier_upgrades_mtd": len(upgrades),
    }


class P03LoyaltyApi(http.Controller):
    @http.route("/p03/loyalty/kpis", type="jsonrpc", auth="user", readonly=True)
    def loyalty_kpis(self, module=None, **kw):
        _require_internal(request.env)
        return {"M10": kpis(request.env)}
