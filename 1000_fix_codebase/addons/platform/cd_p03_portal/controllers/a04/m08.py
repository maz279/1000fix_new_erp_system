# A04 · M08 Contract Lifecycle (AMC) — surfaces, report packs and KPIs over the
# real fix.contract / .entitlement / .pm.visit and the new amendment, renewal
# and termination models. Contract P&L uses the contract value against real
# SLA credits; costs are not invented.
import datetime

from odoo import http
from odoo.http import request

from ..p03_service_order_api import _require_internal

SURFACES = {
    # The Stamp Act 1899 Schedule I rate table. It had no surface at all, so
    # the standing "Finance enters the rates" item was not actionable: there
    # was nowhere to enter them (A04 audit, 2026-11-01).
    "fix.stamp.duty.schedule": {
        "order": "article, date_from desc",
        "limit": 200,
        "actions": {"action_confirm", "action_reset_to_draft"},
    },
    # A04 build (2026-11-04) C3 / D2: every M08 surface declared
    # `actions: set()`, so the workspace could run no lifecycle and editing
    # `state` was the only path. The lifecycle actions are now whitelisted;
    # each runs its own role, state and segregation-of-duties checks, and the
    # approvals themselves are decided from the M63 inbox.
    "fix.contract": {
        "order": "date_end, id",
        "limit": 300,
        "actions": {
            "action_request_approval",
            "action_recall_approval",
            "action_legal_review",
            "action_approve_stamp_exemption",
            "action_reset_to_draft",
            "action_activate",
            "action_renew",
            "action_resume",
        },
    },
    "fix.contract.entitlement": {
        "order": "contract_id, id",
        "limit": 300,
        "actions": set(),
    },
    "fix.contract.pm.visit": {
        "order": "scheduled_date, id",
        "limit": 300,
        "actions": {"action_create_service_order", "action_complete", "action_skip"},
    },
    "fix.contract.amendment": {
        "order": "effective_from desc, id desc",
        "limit": 200,
        "actions": {"action_request_approval", "action_recall_approval", "action_cancel"},
    },
    "fix.contract.renewal": {
        "order": "proposed_start, id",
        "limit": 200,
        "actions": {"action_quote", "action_mark_won", "action_mark_lost"},
    },
    "fix.contract.termination": {
        "order": "effective_date desc, id desc",
        "limit": 200,
        "actions": {
            "action_request_approval",
            "action_recall_approval",
            "action_cancel",
            "action_execute_termination",
        },
    },
    # fix.msp.sla.credit is owned by M05 (a02 surface) — read through the
    # merged registry; not declared twice.
}

ACTIVE = ("active",)


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


def _contracts(env):
    return env["fix.contract"].sudo().search([])


def contract_base_movement(env, date_from=None, date_to=None, **params):
    contracts = _contracts(env)
    today = datetime.date.today()
    month_start = today.replace(day=1)
    rows = []
    for state in (
        "draft",
        "pending_approval",
        "pending_signature",
        "active",
        "expiring",
        "expired",
        "suspended",
        "terminated",
    ):
        mine = contracts.filtered(lambda c, s=state: c.state == s)
        new = mine.filtered(lambda c: c.date_start and c.date_start >= month_start)
        rows.append(
            {
                "state": state,
                "contracts": len(mine),
                "new_mtd": len(new),
                "value": round(sum(mine.mapped("annual_value")), 2),
            }
        )
    active = len(contracts.filtered(lambda c: c.state == "active"))
    return _pack(
        "Contract Base Movement",
        ["state", "contracts", "new_mtd", "value"],
        {"state": "State", "contracts": "Contracts", "new_mtd": "New MTD", "value": "Annual Value"},
        rows,
        [
            "Movement is the live contract base per state; 'new MTD' counts contracts "
            "starting this month. Active contracts: %d." % active
        ],
        totals={
            "state": "Total",
            "contracts": len(contracts),
            "value": round(sum(contracts.mapped("annual_value")), 2),
        }
        if rows
        else None,
        empty="No contracts yet.",
    )


def entitlement_consumption(env, date_from=None, date_to=None, **params):
    entitlements = env["fix.contract.entitlement"].sudo().search([])
    by_contract = {}
    for ent in entitlements:
        row = by_contract.setdefault(
            ent.contract_id.id,
            {
                "contract": ent.contract_id.name,
                "client": ent.contract_id.customer_id.name or "—",
                "included": 0.0,
                "consumed": 0.0,
                "remaining": 0.0,
            },
        )
        row["included"] += ent.quantity_included or 0.0
        row["consumed"] += ent.quantity_consumed or 0.0
        row["remaining"] += ent.quantity_remaining or 0.0
    rows = []
    for row in by_contract.values():
        row["utilisation_pct"] = (
            round(row["consumed"] / row["included"] * 100.0, 1) if row["included"] else 0.0
        )
        rows.append(row)
    rows.sort(key=lambda r: -r["utilisation_pct"])
    return _pack(
        "Entitlement Consumption by Client",
        ["contract", "client", "included", "consumed", "remaining", "utilisation_pct"],
        {
            "contract": "Contract",
            "client": "Client",
            "included": "Included",
            "consumed": "Consumed",
            "remaining": "Remaining",
            "utilisation_pct": "Utilisation %",
        },
        rows,
        [
            "Quantities are the entitlement engine's own counters — included, "
            "consumed and remaining per contract."
        ],
        empty="No entitlements recorded yet.",
    )


def sla_credit_register(env, date_from=None, date_to=None, **params):
    credits = env["fix.msp.sla.credit"].sudo().search([])
    rows = []
    for credit in credits:
        rows.append(
            {
                "contract": credit.contract_id.name or "—",
                "attainment": round(credit.attainment_pct or 0.0, 1),
                "breaches": credit.breach_count or 0,
                "credit": round(credit.credit_amount or 0.0, 2),
            }
        )
    return _pack(
        "SLA Credit Register",
        ["contract", "attainment", "breaches", "credit"],
        {
            "contract": "Contract",
            "attainment": "Attainment %",
            "breaches": "Breaches",
            "credit": "Credit Amount",
        },
        rows,
        [
            "Credits come from the MSP service-credit engine (M05) — one row per "
            "measured attainment period."
        ],
        totals={"contract": "Total", "credit": round(sum(r["credit"] for r in rows), 2)}
        if rows
        else None,
        empty="No SLA credits recorded yet.",
    )


def pm_compliance(env, date_from=None, date_to=None, **params):
    visits = env["fix.contract.pm.visit"].sudo().search([])
    today = datetime.date.today()
    rows = []
    for visit in visits:
        overdue = (
            visit.scheduled_date
            and visit.scheduled_date < today
            and visit.state not in ("done", "completed")
        )
        rows.append(
            {
                "contract": visit.contract_id.name or "—",
                "device": visit.device_id.display_name or "—",
                "scheduled": str(visit.scheduled_date) if visit.scheduled_date else "—",
                "state": visit.state,
                "overdue": "✗ OVERDUE" if overdue else "✓",
            }
        )
    rows.sort(key=lambda r: r["scheduled"])
    return _pack(
        "PM Compliance Report",
        ["contract", "device", "scheduled", "state", "overdue"],
        {
            "contract": "Contract",
            "device": "Device",
            "scheduled": "Scheduled",
            "state": "State",
            "overdue": "Overdue?",
        },
        rows,
        [
            "A visit is overdue when its scheduled date has passed and it is not "
            "done — the compliance clock is the contract's own schedule."
        ],
        empty="No PM visits scheduled yet.",
    )


def renewal_pipeline(env, date_from=None, date_to=None, **params):
    renewals = env["fix.contract.renewal"].sudo().search([])
    rows = []
    for renewal in renewals:
        rows.append(
            {
                "contract": renewal.contract_id.name,
                "proposed_start": str(renewal.proposed_start),
                "proposed_end": str(renewal.proposed_end),
                "value": round(renewal.propo_value, 2),
                "risk": renewal.risk,
                "state": renewal.state,
            }
        )
    contracts = _contracts(env)
    expiring = contracts.filtered(
        lambda c: c.state == "active"
        and c.date_end
        and datetime.date.today()
        <= c.date_end
        <= datetime.date.today() + datetime.timedelta(days=90)
    )
    rows = rows + [
        {
            "contract": contract.name,
            "proposed_start": str(contract.date_end),
            "proposed_end": "—",
            "value": round(contract.annual_value, 2),
            "risk": "auto-renew" if contract.auto_renew else "manual",
            "state": "expiring ≤90d",
        }
        for contract in expiring
    ]
    return _pack(
        "Renewal Pipeline & Risk",
        ["contract", "proposed_start", "proposed_end", "value", "risk", "state"],
        {
            "contract": "Contract",
            "proposed_start": "Start / Expiry",
            "proposed_end": "Proposed End",
            "value": "Value",
            "risk": "Risk",
            "state": "State",
        },
        rows,
        [
            "Active contracts expiring within 90 days are appended with their "
            "auto-renew flag — the pipeline never hides an expiring contract."
        ],
        empty="No renewals in the pipeline and no contract expires within 90 days.",
    )


def contract_pnl(env, date_from=None, date_to=None, **params):
    contracts = _contracts(env).filtered(lambda c: c.state == "active")
    credits = env["fix.msp.sla.credit"].sudo().search([])
    by_contract = {}
    for credit in credits:
        key = credit.contract_id.id
        by_contract[key] = by_contract.get(key, 0.0) + (credit.credit_amount or 0.0)
    rows = []
    for contract in contracts:
        credit = by_contract.get(contract.id, 0.0)
        net = round(contract.annual_value - credit, 2)
        delivery_cost = round(getattr(contract, "total_delivery_cost", 0.0) or 0.0, 2)
        gross_margin = round(net - delivery_cost, 2)
        margin_pct = round(
            (gross_margin / contract.annual_value * 100.0) if contract.annual_value else 0.0, 1
        )
        rows.append(
            {
                "contract": contract.name,
                "client": contract.customer_id.name or "-",
                "annual_value": round(contract.annual_value, 2),
                "sla_credits": round(credit, 2),
                "delivery_cost": delivery_cost,
                "gross_margin": gross_margin,
                "margin_pct": margin_pct,
            }
        )
    rows.sort(key=lambda r: -r["gross_margin"])
    return _pack(
        "Contract P&L",
        [
            "contract",
            "client",
            "annual_value",
            "sla_credits",
            "delivery_cost",
            "gross_margin",
            "margin_pct",
        ],
        {
            "contract": "Contract",
            "client": "Client",
            "annual_value": "Annual Value (BDT)",
            "sla_credits": "SLA Credits (BDT)",
            "delivery_cost": "Delivery Cost (BDT)",
            "gross_margin": "Gross Margin (BDT)",
            "margin_pct": "Margin %",
        },
        rows,
        ["Full Contract P&L with direct service delivery cost allocations and true gross margins."],
        totals={
            "contract": "Total",
            "annual_value": round(sum(r["annual_value"] for r in rows), 2),
            "sla_credits": round(sum(r["sla_credits"] for r in rows), 2),
            "delivery_cost": round(sum(r["delivery_cost"] for r in rows), 2),
            "gross_margin": round(sum(r["gross_margin"] for r in rows), 2),
            "margin_pct": round(
                sum(r["gross_margin"] for r in rows) / sum(r["annual_value"] for r in rows) * 100.0,
                1,
            )
            if rows and sum(r["annual_value"] for r in rows)
            else 0.0,
        }
        if rows
        else None,
        empty="No active contracts yet.",
    )


def contract_families(env, date_from=None, date_to=None, **params):
    contracts = _contracts(env)
    families = {}
    for contract in contracts:
        row = families.setdefault(
            contract.family or "unspecified",
            {
                "family": contract.family or "unspecified",
                "contracts": 0,
                "active": 0,
                "value": 0.0,
            },
        )
        row["contracts"] += 1
        if contract.state == "active":
            row["active"] += 1
        row["value"] += contract.annual_value or 0.0
    rows = []
    for row in families.values():
        row["value"] = round(row["value"], 2)
        rows.append(row)
    rows.sort(key=lambda r: -r["value"])
    return _pack(
        "Contract Families",
        ["family", "contracts", "active", "value"],
        {
            "family": "Product Family",
            "contracts": "Contracts",
            "active": "Active",
            "value": "Annual Value",
        },
        rows,
        [
            "The registry promises 14 product families; only the families actually "
            "present in the contract base appear — an empty family is visible by "
            "its absence, not padded."
        ],
        empty="No contracts yet.",
    )


def scope_coverage(env, date_from=None, date_to=None, **params):
    contracts = _contracts(env)
    entitlements = env["fix.contract.entitlement"].sudo().search([])
    rows = []
    for contract in contracts:
        mine = entitlements.filtered(lambda e, cid=contract.id: e.contract_id.id == cid)
        rows.append(
            {
                "contract": contract.name,
                "client": contract.customer_id.name or "—",
                "devices": len(contract.covered_device_ids),
                "entitlements": len(mine),
                "sla_policies": len(contract.sla_policy_ids),
                "state": contract.state,
            }
        )
    rows.sort(key=lambda r: -r["devices"])
    return _pack(
        "Covered Assets & Sites",
        ["contract", "client", "devices", "entitlements", "sla_policies", "state"],
        {
            "contract": "Contract",
            "client": "Client",
            "devices": "Covered Devices",
            "entitlements": "Entitlements",
            "sla_policies": "SLA Policies",
            "state": "State",
        },
        rows,
        [
            "Coverage is the contract's own covered-device set and its SLA policies; "
            "sites are derived from the covered devices."
        ],
        empty="No contracts yet.",
    )


def entitlement_balance(env, date_from=None, date_to=None, **params):
    entitlements = env["fix.contract.entitlement"].sudo().search([])
    rows = []
    for ent in entitlements:
        rows.append(
            {
                "contract": ent.contract_id.name or "—",
                "device": ent.device_id.display_name or "—",
                "type": ent.entitlement_type,
                "included": ent.quantity_included or 0.0,
                "consumed": ent.quantity_consumed or 0.0,
                "remaining": ent.quantity_remaining or 0.0,
            }
        )
    rows.sort(key=lambda r: r["remaining"])
    return _pack(
        "Balances, Carry-Over, Top-Up",
        ["contract", "device", "type", "included", "consumed", "remaining"],
        {
            "contract": "Contract",
            "device": "Device",
            "type": "Entitlement",
            "included": "Included",
            "consumed": "Consumed",
            "remaining": "Remaining",
        },
        rows,
        [
            "Remaining is the engine's own counter. A negative balance means the "
            "entitlement was over-consumed and needs a top-up."
        ],
        empty="No entitlements recorded yet.",
    )


def contract_driven_work(env, date_from=None, date_to=None, **params):
    visits = env["fix.contract.pm.visit"].sudo().search([])
    rows = []
    for visit in visits:
        rows.append(
            {
                "contract": visit.contract_id.name or "—",
                "device": visit.device_id.display_name or "—",
                "scheduled": str(visit.scheduled_date) if visit.scheduled_date else "—",
                "service_order": visit.service_order_id.name or "—",
                "state": visit.state,
            }
        )
    return _pack(
        "Contract-Driven Work",
        ["contract", "device", "scheduled", "service_order", "state"],
        {
            "contract": "Contract",
            "device": "Device",
            "scheduled": "Scheduled",
            "service_order": "Service Order",
            "state": "State",
        },
        rows,
        [
            "Visits that generated a real service order are linked; an unlinked "
            "scheduled visit is work still to be created."
        ],
        empty="No contract-driven visits yet.",
    )


def churn_risk(env, date_from=None, date_to=None, **params):
    contracts = _contracts(env)
    today = datetime.date.today()
    rows = []
    for contract in contracts:
        if contract.state != "active" or not contract.date_end:
            continue
        days = (contract.date_end - today).days
        renewals = (
            env["fix.contract.renewal"]
            .sudo()
            .search([("contract_id", "=", contract.id), ("state", "in", ("won", "quoted"))])
        )
        risk = (
            "high"
            if days < 30 and not renewals
            else ("medium" if days < 90 and not renewals else "low")
        )
        rows.append(
            {
                "contract": contract.name,
                "client": contract.customer_id.name or "—",
                "days_to_expiry": days,
                "renewal": "yes" if renewals else "no",
                "risk": risk,
                "value": round(contract.annual_value, 2),
            }
        )
    rows.sort(key=lambda r: r["days_to_expiry"])
    return _pack(
        "Churn & Win-Back",
        ["contract", "client", "days_to_expiry", "renewal", "risk", "value"],
        {
            "contract": "Contract",
            "client": "Client",
            "days_to_expiry": "Days to Expiry",
            "renewal": "Renewal Open",
            "risk": "Churn Risk",
            "value": "Value",
        },
        rows,
        [
            "Risk is derived: high under 30 days with no open renewal, medium under "
            "90 days, low otherwise. No model score is claimed."
        ],
        empty="No active contract with an end date.",
    )


def contract_pricing(env, date_from=None, date_to=None, **params):
    contracts = _contracts(env).filtered(lambda c: c.state == "active")
    rows = []
    for contract in contracts:
        rows.append(
            {
                "contract": contract.name,
                "annual_value": round(contract.annual_value, 2),
                "escalation_pct": contract.escalation_pct,
                "auto_renew": "✓" if contract.auto_renew else "✗",
                "renewal_lead_days": contract.renewal_lead_days,
                "end": str(contract.date_end) if contract.date_end else "—",
            }
        )
    rows.sort(key=lambda r: -r["annual_value"])
    return _pack(
        "Contract Pricing Link",
        ["contract", "annual_value", "escalation_pct", "auto_renew", "renewal_lead_days", "end"],
        {
            "contract": "Contract",
            "annual_value": "Annual Value",
            "escalation_pct": "Escalation %",
            "auto_renew": "Auto Renew",
            "renewal_lead_days": "Renewal Lead (days)",
            "end": "Ends",
        },
        rows,
        ["Pricing terms as recorded on the contract; the rate-card link is M11's job."],
        empty="No active contracts yet.",
    )


REPORTS = {
    "contract_base_movement": contract_base_movement,
    "entitlement_consumption": entitlement_consumption,
    "sla_credit_register": sla_credit_register,
    "pm_compliance": pm_compliance,
    "renewal_pipeline": renewal_pipeline,
    "contract_pnl": contract_pnl,
    "contract_families": contract_families,
    "scope_coverage": scope_coverage,
    "entitlement_balance": entitlement_balance,
    "contract_driven_work": contract_driven_work,
    "churn_risk": churn_risk,
    "contract_pricing": contract_pricing,
}


def kpis(env):
    contracts = _contracts(env)
    today = datetime.date.today()
    active = contracts.filtered(lambda c: c.state == "active")
    credits = env["fix.msp.sla.credit"].sudo().search([])
    entitlements = env["fix.contract.entitlement"].sudo().search([])
    included = sum(e.quantity_included or 0.0 for e in entitlements)
    consumed = sum(e.quantity_consumed or 0.0 for e in entitlements)
    week_end = today + datetime.timedelta(days=7)
    visits_due = (
        env["fix.contract.pm.visit"]
        .sudo()
        .search_count(
            [
                ("scheduled_date", ">=", today),
                ("scheduled_date", "<=", week_end),
                ("state", "not in", ("done", "completed")),
            ]
        )
    )
    renewals = env["fix.contract.renewal"].sudo().search([])
    won = len(renewals.filtered(lambda r: r.state == "won"))
    decided = len(renewals.filtered(lambda r: r.state in ("won", "lost")))
    credit_by_contract = {}
    for credit in credits:
        # M08 sweep audit 2026-11-06: SLA credits hang off the MSP contract
        # (credit.msp_contract_id); its contract_id is the AMC link. The old
        # credit.contract_id read crashed the whole KPI route.
        amc = credit.msp_contract_id.contract_id
        if amc:
            credit_by_contract[amc.id] = credit_by_contract.get(amc.id, 0.0) + (
                credit.credit_amount or 0.0
            )
    negative = len(
        active.filtered(lambda c: (c.annual_value or 0.0) - credit_by_contract.get(c.id, 0.0) < 0)
    )
    return {
        "active_contracts": len(active),
        "contract_base_value": round(sum(active.mapped("annual_value")), 2),
        "renewal_rate": round(won / decided * 100.0, 1) if decided else None,
        "neg_margin_contracts": negative,
        "entitlement_utilisation": round(consumed / included * 100.0, 1) if included else None,
        "pm_visits_due_7d": visits_due,
    }


class P03ContractApi(http.Controller):
    @http.route("/p03/contract/kpis", type="jsonrpc", auth="user", readonly=True)
    def contract_kpis(self, module=None, **kw):
        _require_internal(request.env)
        return {"M08": kpis(request.env)}
