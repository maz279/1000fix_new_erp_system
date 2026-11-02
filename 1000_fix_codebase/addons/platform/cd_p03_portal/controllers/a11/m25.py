# A11 · M25 Business Intelligence — the surfaces the generic workspace
# endpoints may serve (SURFACES), the Weekly Executive Business Review
# (REPORTS) and the live executive dashboard payloads (/p03/bi/kpis,
# /p03/bi/exec). Every number is a measured read of the real service order,
# estimate and AR invoice tables — nothing here invents data.
import datetime
import logging

from odoo import http
from odoo.http import request

from ..p03_service_order_api import _require_internal

_logger = logging.getLogger(__name__)

SURFACES = {
    "fix.bi.sync.config": {
        "order": "sequence, id",
        "limit": 50,
        "actions": {"action_test_connection", "action_run_sync"},
    },
    "fix.bi.sync.log": {
        "order": "ran_at desc, id desc",
        "limit": 100,
        "actions": set(),
    },
    "fix.bi.dashboard": {
        "order": "role, name",
        "limit": 200,
        "actions": set(),
    },
    "fix.bi.distribution.schedule": {
        "order": "name",
        "limit": 200,
        "actions": set(),
    },
    "fix.bi.alert.subscription": {
        "order": "name",
        "limit": 200,
        "actions": set(),
    },
}

OPEN_ORDER_STATES = [
    "draft",
    "intake",
    "diagnostic",
    "estimate_pending",
    "estimate_sent",
    "awaiting_approval",
    "approved",
    "in_repair",
    "qc_pending",
    "qc_failed",
    "ready",
]
ISSUED_INVOICE_STATES = ["issued", "paid"]
SERVICE_TYPES = ["walk_in", "collection", "onsite", "mail_in", "corporate"]


def _companies(env):
    return env.companies.ids


def _bi_domain(env, model, extra):
    """Company-wide read domain (A08 pattern: sudo reads + explicit company)."""
    domain = list(extra)
    if "company_id" in env[model]._fields:
        domain.append(("company_id", "in", _companies(env)))
    return domain


def _week_bounds(weeks=8):
    """ISO-week (monday) starts, oldest first, ending with this week."""
    today = datetime.date.today()
    this_monday = today - datetime.timedelta(days=today.weekday())
    mondays = [this_monday - datetime.timedelta(weeks=k) for k in range(weeks - 1, -1, -1)]
    return mondays


def fields_date(value):
    """Best-effort date coercion for group results (datetime or date)."""
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    return datetime.date.today()


def weekly_exec_review(env, **params):
    """The Weekly Executive Business Review: 8 measured ISO weeks — orders
    opened and delivered, approved estimate value, issued AR invoices."""
    orders = env["fix.service.order"].sudo()
    estimates = env["fix.estimate"].sudo()
    invoices = env["fix.ar.invoice"].sudo()
    mondays = _week_bounds(int(params.get("weeks", 8)))

    def week_of(day):
        return day - datetime.timedelta(days=day.weekday())

    opened = {}
    for day_group, count in orders._read_group(
        _bi_domain(
            env,
            "fix.service.order",
            [
                ("create_date", ">=", datetime.datetime.combine(mondays[0], datetime.time.min)),
            ],
        ),
        groupby=["create_date:day"],
        aggregates=["__count"],
    ):
        opened[week_of(fields_date(day_group))] = (
            opened.get(week_of(fields_date(day_group)), 0) + count
        )

    delivered = {}
    for rec in orders.search(
        _bi_domain(
            env,
            "fix.service.order",
            [
                ("state", "in", ["delivered", "closed"]),
                ("write_date", ">=", datetime.datetime.combine(mondays[0], datetime.time.min)),
            ],
        )
    ):
        stamp = rec.write_date.date() if rec.write_date else None
        if stamp:
            delivered[week_of(stamp)] = delivered.get(week_of(stamp), 0) + 1

    approved = {}
    for rec in estimates.search(
        _bi_domain(
            env,
            "fix.estimate",
            [
                ("state", "=", "approved"),
                ("create_date", ">=", datetime.datetime.combine(mondays[0], datetime.time.min)),
            ],
        )
    ):
        stamp = rec.create_date.date() if rec.create_date else None
        if stamp:
            key = week_of(stamp)
            approved[key] = approved.get(key, 0.0) + rec.grand_total

    invoiced = {}
    for rec in invoices.search(
        _bi_domain(
            env,
            "fix.ar.invoice",
            [
                ("state", "in", ISSUED_INVOICE_STATES),
                ("invoice_date", ">=", mondays[0]),
            ],
        )
    ):
        if rec.invoice_date:
            key = week_of(rec.invoice_date)
            invoiced[key] = invoiced.get(key, 0.0) + rec.taxable_amount

    rows = []
    for monday in mondays:
        rows.append(
            {
                "week": "W%s · %s" % (monday.isocalendar()[1], monday.strftime("%d %b")),
                "orders_opened": opened.get(monday, 0),
                "orders_delivered": delivered.get(monday, 0),
                "estimates_approved": round(approved.get(monday, 0.0), 2),
                "invoiced_taxable": round(invoiced.get(monday, 0.0), 2),
            }
        )
    return {
        "title": "Weekly Executive Business Review — measured ISO weeks",
        "cols": [
            "week",
            "orders_opened",
            "orders_delivered",
            "estimates_approved",
            "invoiced_taxable",
        ],
        "labels": {
            "week": "Week",
            "orders_opened": "Orders Opened",
            "orders_delivered": "Orders Delivered",
            "estimates_approved": "Approved Estimate Value (৳)",
            "invoiced_taxable": "Invoiced Taxable (৳)",
        },
        "rows": rows,
        "notes": [
            "Approved = fix.estimate state 'approved' in the week; invoiced = AR invoices issued/paid."
        ],
    }


def commercial_board(env, **params):
    """CCO commercial board: pipeline definitions by revenue stream and the open
    opportunity value by stage (crm.lead). Nothing is forecast beyond what the
    pipeline records hold."""
    pipelines = env["fix.pipeline"].sudo().search([("active", "=", True)])
    leads = env["crm.lead"].sudo().search([("type", "=", "opportunity")])
    rows = []
    for pipeline in pipelines:
        stream = dict(pipeline._fields["revenue_stream"].selection).get(
            pipeline.revenue_stream, pipeline.revenue_stream
        )
        stage_count = 0
        try:
            import json as _json

            stage_count = len(_json.loads(pipeline.stages_json or "[]"))
        except Exception:
            stage_count = 0
        rows.append(
            {
                "stream": stream,
                "pipeline": pipeline.code,
                "stages": stage_count,
                "probability": pipeline.default_probability or 0.0,
                "open_opportunities": len(leads),
                "open_value": round(sum(leads.mapped("expected_revenue")), 2),
            }
        )
    return _pack(
        "CCO Commercial Board - %d pipeline(s), %d open opportunit(ies)" % (len(rows), len(leads)),
        ["stream", "pipeline", "stages", "probability", "open_opportunities", "open_value"],
        {
            "stream": "Revenue Stream",
            "pipeline": "Pipeline",
            "stages": "Stages",
            "probability": "Default Probability %",
            "open_opportunities": "Open Opportunities",
            "open_value": "Open Expected Revenue",
        },
        rows,
        [
            "Stage count comes from the pipeline's own stage definition. Open value sums "
            "expected_revenue on open CRM opportunities - it is not a forecast model."
        ],
        empty="No active pipelines.",
    )


REPORTS = {
    "weekly_exec_review": weekly_exec_review,
}

REPORTS["commercial_board"] = commercial_board


def _exec_payload(env):
    """The Executive C-Suite KPI dashboard payload — all live reads."""
    orders = env["fix.service.order"].sudo()
    estimates = env["fix.estimate"].sudo()
    invoices = env["fix.ar.invoice"].sudo()
    today = datetime.date.today()
    month_start = today.replace(day=1)

    open_count = orders.search_count(
        _bi_domain(env, "fix.service.order", [("state", "in", OPEN_ORDER_STATES)])
    )
    in_repair = orders.search_count(
        _bi_domain(env, "fix.service.order", [("state", "=", "in_repair")])
    )
    delivered_mtd = orders.search_count(
        _bi_domain(
            env,
            "fix.service.order",
            [
                ("state", "in", ["delivered", "closed"]),
                ("write_date", ">=", datetime.datetime.combine(month_start, datetime.time.min)),
            ],
        )
    )
    revenue_mtd = sum(
        estimates.search(
            _bi_domain(
                env,
                "fix.estimate",
                [
                    ("state", "=", "approved"),
                    (
                        "create_date",
                        ">=",
                        datetime.datetime.combine(month_start, datetime.time.min),
                    ),
                ],
            )
        ).mapped("grand_total")
    )
    invoice_rows = invoices.search(
        _bi_domain(
            env,
            "fix.ar.invoice",
            [
                ("state", "in", ISSUED_INVOICE_STATES),
                ("invoice_date", ">=", month_start),
            ],
        )
    )
    freshness = env["fix.bi.sync.log"].sudo().freshness_minutes()

    # 12-month orders trend (real create_date counts per month)
    year_ago = (today - datetime.timedelta(days=365)).strftime("%Y-%m-01")
    trend_rows = orders._read_group(
        _bi_domain(env, "fix.service.order", [("create_date", ">=", year_ago)]),
        groupby=["create_date:month"],
        aggregates=["__count"],
    )
    trend = {}
    for day_group, count in trend_rows:
        key = fields_date(day_group).strftime("%Y-%m")
        trend[key] = trend.get(key, 0) + count
    trend_series = [{"month": k, "orders": trend[k]} for k in sorted(trend)]

    # intake channel mix (service_type) over the last 30 days
    since30 = datetime.datetime.combine(today - datetime.timedelta(days=30), datetime.time.min)
    channel_rows = orders._read_group(
        _bi_domain(env, "fix.service.order", [("create_date", ">=", since30)]),
        groupby=["service_type"],
        aggregates=["__count"],
    )
    channels = [{"key": str(k), "count": c} for k, c in channel_rows]

    # top branches by open workload
    branch_rows = orders._read_group(
        _bi_domain(env, "fix.service.order", [("state", "in", OPEN_ORDER_STATES)]),
        groupby=["branch_id"],
        aggregates=["__count"],
    )
    branches = sorted(
        ({"branch": (b[1] if isinstance(b, tuple) else str(b)), "open": c} for b, c in branch_rows),
        key=lambda d: -d["open"],
    )[:6]

    return {
        "kpis": {
            "bi_data_freshness": freshness,
            "open_orders": open_count,
            "in_repair": in_repair,
            "delivered_mtd": delivered_mtd,
            "revenue_mtd": revenue_mtd,
            "invoiced_mtd": len(invoice_rows),
            "invoiced_taxable_mtd": sum(invoice_rows.mapped("taxable_amount")),
        },
        "trend": trend_series,
        "channels": channels,
        "branches": branches,
    }


class P03BiApi(http.Controller):
    """M25 live endpoints for the workspace shell."""

    @http.route("/p03/bi/kpis", type="jsonrpc", auth="user", readonly=True)
    def bi_kpis(self, module=None, **kw):
        _require_internal(request.env)
        env = request.env
        payload = _exec_payload(env)
        fresh = payload["kpis"]["bi_data_freshness"]
        try:
            dashboards = 9 + env["fix.bi.dashboard"].sudo().search_count(
                [("company_id", "in", _companies(env))]
            )
        except Exception:
            dashboards = None
        try:
            schedules = (
                env["fix.bi.distribution.schedule"].sudo().search_count([("active", "=", True)])
            )
        except Exception:
            schedules = None
        usage = _weekly_usage(env)
        return {
            "M25": {
                "bi_data_freshness": fresh if fresh is not None else "never",
                "open_orders": payload["kpis"]["open_orders"],
                "in_repair": payload["kpis"]["in_repair"],
                "delivered_mtd": payload["kpis"]["delivered_mtd"],
                "revenue_mtd": payload["kpis"]["revenue_mtd"],
                "invoiced_mtd": payload["kpis"]["invoiced_mtd"],
                # registry KPI strip (M25 spec): measured where a model exists
                "dashboards_live": dashboards,
                # the registry's standard report library (six packs; the
                # weekly review and dataset catalog are additional surfaces)
                "standard_reports": 6,
                "weekly_manager_usage": usage,
                "load_time_p95": None,
                "scheduled_distributions": schedules,
                "spreadsheets_retired": None,
            }
        }

    @http.route("/p03/bi/exec", type="jsonrpc", auth="user", readonly=True)
    def bi_exec(self, **kw):
        _require_internal(request.env)
        return _exec_payload(request.env)

    @http.route("/p03/bi/role", type="jsonrpc", auth="user", readonly=True)
    def bi_role(self, role="ceo", **kw):
        _require_internal(request.env)
        return _role_payload(request.env, role or "ceo")


def _weekly_usage(env):
    """Distinct users who logged in during the last 7 days (res.users.log is
    the only usage telemetry the platform actually records; dashboard-level
    telemetry has no model and is never invented)."""
    try:
        since = datetime.datetime.now() - datetime.timedelta(days=7)
        rows = env["res.users.log"].sudo().search([("create_date", ">=", since)])
        return len(set(rows.mapped("create_uid").ids))
    except Exception:
        return None


ROLE_TITLES = {
    "ceo": "CEO Cockpit",
    "coo": "COO / Ops Board (Live)",
    "cfo": "CFO Dashboard",
    "cco": "CCO Commercial",
    "service": "Service Analytics",
    "finance": "Finance Analytics",
    "people": "People Analytics",
    "quality": "Quality Analytics",
    "all": "Executive C-Suite KPI Dashboard",
}


def _metrics(env):
    """The measured metric bank every role dashboard and pack reads from."""
    today = datetime.date.today()
    month_start = today.replace(day=1)
    orders = env["fix.service.order"].sudo()
    estimates = env["fix.estimate"].sudo()
    invoices = env["fix.ar.invoice"].sudo()
    receipts = env["fix.ar.receipt"].sudo()
    m = {}
    m["open_orders"] = orders.search_count(
        _bi_domain(env, "fix.service.order", [("state", "in", OPEN_ORDER_STATES)])
    )
    m["in_repair"] = orders.search_count(
        _bi_domain(env, "fix.service.order", [("state", "=", "in_repair")])
    )
    m["delivered_mtd"] = orders.search_count(
        _bi_domain(
            env,
            "fix.service.order",
            [
                ("state", "in", ["delivered", "closed"]),
                ("write_date", ">=", datetime.datetime.combine(month_start, datetime.time.min)),
            ],
        )
    )
    m["revenue_mtd"] = sum(
        estimates.search(
            _bi_domain(
                env,
                "fix.estimate",
                [
                    ("state", "=", "approved"),
                    (
                        "create_date",
                        ">=",
                        datetime.datetime.combine(month_start, datetime.time.min),
                    ),
                ],
            )
        ).mapped("grand_total")
    )
    inv_mtd = invoices.search(
        _bi_domain(
            env,
            "fix.ar.invoice",
            [("state", "in", ISSUED_INVOICE_STATES), ("invoice_date", ">=", month_start)],
        )
    )
    m["invoiced_mtd"] = len(inv_mtd)
    m["invoiced_taxable_mtd"] = sum(inv_mtd.mapped("taxable_amount"))
    open_inv = invoices.search(
        _bi_domain(env, "fix.ar.invoice", [("state", "=", "issued")])
    ).filtered(lambda i: i.amount_residual > 0.005)
    m["ar_outstanding"] = sum(open_inv.mapped("amount_residual"))
    m["overdue_gt_60d"] = sum(
        i.amount_residual
        for i in open_inv
        if (today - i.invoice_date).days - i._payment_terms_days() > 60
    )
    m["collected_mtd"] = sum(
        receipts.search(
            _bi_domain(
                env,
                "fix.ar.receipt",
                [("state", "=", "confirmed"), ("receipt_date", ">=", month_start)],
            )
        ).mapped("amount")
    )
    m["sla_overdue"] = orders.search_count(
        _bi_domain(
            env,
            "fix.service.order",
            [
                ("state", "in", OPEN_ORDER_STATES),
                ("sla_resolution_deadline", "<", datetime.datetime.now()),
            ],
        )
    )
    m["qc_failed"] = orders.search_count(
        _bi_domain(env, "fix.service.order", [("state", "=", "qc_failed")])
    )
    m["estimates_awaiting"] = estimates.search_count(
        _bi_domain(env, "fix.estimate", [("state", "=", "sent")])
    )
    try:
        m["complaints_open"] = (
            env["fix.complaint"]
            .sudo()
            .search_count([("state", "not in", ("closed", "resolved", "rejected", "cancelled"))])
        )
        m["complaints_total"] = env["fix.complaint"].sudo().search_count([])
    except Exception:
        m["complaints_open"] = m["complaints_total"] = None
    try:
        m["ncr_open"] = (
            env["fix.ncr"]
            .sudo()
            .search_count([("state", "not in", ("closed", "verified", "rejected", "cancelled"))])
        )
    except Exception:
        m["ncr_open"] = None
    try:
        Lead = env["crm.lead"].sudo()
        m["leads_open"] = Lead.search_count([("type", "=", "opportunity"), ("active", "=", True)])
        m["pipeline_value"] = sum(
            Lead.search([("type", "=", "opportunity"), ("active", "=", True)]).mapped(
                "expected_revenue"
            )
        )
    except Exception:
        m["leads_open"] = m["pipeline_value"] = None
    try:
        m["loyalty_members"] = env["fix.loyalty.account"].sudo().search_count([])
    except Exception:
        m["loyalty_members"] = None
    try:
        m["employees_active"] = env["hr.employee"].sudo().search_count([("active", "=", True)])
        m["present_today"] = (
            env["hr.attendance"]
            .sudo()
            .search_count([("check_in", ">=", datetime.datetime.combine(today, datetime.time.min))])
        )
    except Exception:
        m["employees_active"] = m["present_today"] = None
    try:
        m["requisitions_open"] = (
            env["fix.requisition"].sudo().search_count([("state", "in", ("draft", "approved"))])
        )
    except Exception:
        m["requisitions_open"] = None
    try:
        m["dunning_active"] = (
            env["fix.dunning"].sudo().search_count([("invoice_id.state", "=", "issued")])
        )
    except Exception:
        m["dunning_active"] = None
    return {k: (round(v, 2) if isinstance(v, float) else v) for k, v in m.items()}


def _k(ln, v, **extra):
    row = {"l": ln, "v": v}
    row.update(extra)
    return row


def _role_payload(env, role):
    """Role dashboards (FR-BI role cockpit): each KPI is a measured read;
    money tiles declare the currency so the shell formats them."""
    m = _metrics(env)
    title = ROLE_TITLES.get(role, "Executive C-Suite KPI Dashboard")
    groups = []

    if role in ("ceo", "all"):
        groups.append(
            {
                "title": "Company Performance",
                "kpis": [
                    _k("Revenue MTD (approved)", m["revenue_mtd"], money=True),
                    _k("Delivered MTD", m["delivered_mtd"]),
                    _k("Invoices Issued MTD", m["invoiced_mtd"]),
                    _k("Open Orders", m["open_orders"]),
                    _k("Open Complaints", m["complaints_open"]),
                ],
            }
        )
        groups.append(
            {
                "title": "Commercial",
                "kpis": [
                    _k("Open Opportunities", m["leads_open"]),
                    _k("Pipeline Value", m["pipeline_value"], money=True),
                    _k("Loyalty Members", m["loyalty_members"]),
                ],
            }
        )
    if role in ("coo", "all"):
        groups.append(
            {
                "title": "Operations",
                "kpis": [
                    _k("Open Orders", m["open_orders"]),
                    _k("In Repair Now", m["in_repair"]),
                    _k("SLA Overdue", m["sla_overdue"]),
                    _k("QC Failed", m["qc_failed"]),
                    _k("Delivered MTD", m["delivered_mtd"]),
                ],
            }
        )
    if role in ("cfo", "all"):
        groups.append(
            {
                "title": "Finance",
                "kpis": [
                    _k("Invoiced Taxable MTD", m["invoiced_taxable_mtd"], money=True),
                    _k("Collected MTD", m["collected_mtd"], money=True),
                    _k("AR Outstanding", m["ar_outstanding"], money=True),
                    _k("Overdue > 60d", m["overdue_gt_60d"], money=True),
                ],
            }
        )
    if role in ("cco", "all"):
        groups.append(
            {
                "title": "Commercial",
                "kpis": [
                    _k("Open Opportunities", m["leads_open"]),
                    _k("Pipeline Value", m["pipeline_value"], money=True),
                    _k("Loyalty Members", m["loyalty_members"]),
                    _k("Open Complaints", m["complaints_open"]),
                ],
            }
        )
    if role == "service":
        groups.append(
            {
                "title": "Service Performance",
                "kpis": [
                    _k("Open Orders", m["open_orders"]),
                    _k("In Repair Now", m["in_repair"]),
                    _k("SLA Overdue", m["sla_overdue"]),
                    _k("QC Failed", m["qc_failed"]),
                    _k("Estimates Awaiting Approval", m["estimates_awaiting"]),
                ],
            }
        )
    if role == "finance":
        groups.append(
            {
                "title": "Receivables",
                "kpis": [
                    _k("AR Outstanding", m["ar_outstanding"], money=True),
                    _k("Overdue > 60d", m["overdue_gt_60d"], money=True),
                    _k("Collected MTD", m["collected_mtd"], money=True),
                    _k("Active Dunning Rows", m["dunning_active"]),
                ],
            }
        )
        groups.append(
            {
                "title": "Billing",
                "kpis": [
                    _k("Invoiced Taxable MTD", m["invoiced_taxable_mtd"], money=True),
                    _k("Revenue MTD (approved)", m["revenue_mtd"], money=True),
                ],
            }
        )
    if role == "people":
        groups.append(
            {
                "title": "Workforce",
                "kpis": [
                    _k("Active Employees", m["employees_active"]),
                    _k("Checked In Today", m["present_today"]),
                    _k("Open Requisitions", m["requisitions_open"]),
                ],
            }
        )
    if role == "quality":
        groups.append(
            {
                "title": "Quality",
                "kpis": [
                    _k("Open Complaints", m["complaints_open"]),
                    _k("Total Complaints", m["complaints_total"]),
                    _k("Open NCRs", m["ncr_open"]),
                    _k("QC Failed Orders", m["qc_failed"]),
                ],
            }
        )
    return {
        "role": role,
        "title": title,
        "as_of": str(datetime.date.today()),
        "groups": groups,
        "notes": [
            "Every tile is a live read of the operational tables (orders, estimates, "
            "AR, complaints, NCRs, CRM, HR). A tile with no readable source stays '—'.",
            "Dashboard-level usage telemetry and p95 load time have no model yet — they "
            "are never invented.",
        ],
    }


# ---------------------------------------------------------------------------
# The registry's report library. Every pack is a live measured read; the
# shared metric bank is defined once in _metrics so the packs cannot drift.
# ---------------------------------------------------------------------------


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


def executive_pack(env, date_from=None, date_to=None, **params):
    m = _metrics(env)
    rows = [
        {
            "metric": "Revenue MTD (approved estimates)",
            "value": m["revenue_mtd"],
            "basis": "fix.estimate state=approved, created this month",
        },
        {
            "metric": "Invoices issued MTD",
            "value": m["invoiced_mtd"],
            "basis": "fix.ar.invoice issued/paid, invoice_date this month",
        },
        {
            "metric": "Invoiced taxable MTD",
            "value": m["invoiced_taxable_mtd"],
            "basis": "sum(taxable_amount) of the same invoices",
        },
        {
            "metric": "Collected MTD",
            "value": m["collected_mtd"],
            "basis": "fix.ar.receipt state=confirmed, this month",
        },
        {
            "metric": "AR outstanding",
            "value": m["ar_outstanding"],
            "basis": "issued invoices with residual > 0",
        },
        {
            "metric": "Overdue > 60 days",
            "value": m["overdue_gt_60d"],
            "basis": "residual past the customer's own credit terms",
        },
        {
            "metric": "Open orders",
            "value": m["open_orders"],
            "basis": "service orders in a non-terminal state",
        },
        {
            "metric": "Delivered MTD",
            "value": m["delivered_mtd"],
            "basis": "orders reaching delivered/closed this month",
        },
        {
            "metric": "Open complaints",
            "value": m["complaints_open"],
            "basis": "fix.complaint in a non-terminal state",
        },
    ]
    return _pack(
        "Executive Pack — measured company metrics",
        ["metric", "value", "basis"],
        {"metric": "Metric", "value": "Value", "basis": "Basis"},
        rows,
        [
            "One row per executive figure; the basis column is the exact query the "
            "number comes from, so nothing is accepted on trust."
        ],
    )


def branch_league(env, date_from=None, date_to=None, **params):
    today = datetime.date.today()
    month_start = today.replace(day=1)
    orders = env["fix.service.order"].sudo()
    groups = orders._read_group(
        _bi_domain(env, "fix.service.order", []),
        groupby=["branch_id"],
        aggregates=["__count"],
    )
    open_groups = {
        b.id if b else 0: c
        for b, c in orders._read_group(
            _bi_domain(env, "fix.service.order", [("state", "in", OPEN_ORDER_STATES)]),
            groupby=["branch_id"],
            aggregates=["__count"],
        )
    }
    repair_groups = {
        b.id if b else 0: c
        for b, c in orders._read_group(
            _bi_domain(env, "fix.service.order", [("state", "=", "in_repair")]),
            groupby=["branch_id"],
            aggregates=["__count"],
        )
    }
    delivered_groups = {
        b.id if b else 0: c
        for b, c in orders._read_group(
            _bi_domain(
                env,
                "fix.service.order",
                [
                    ("state", "in", ["delivered", "closed"]),
                    ("write_date", ">=", datetime.datetime.combine(month_start, datetime.time.min)),
                ],
            ),
            groupby=["branch_id"],
            aggregates=["__count"],
        )
    }
    invoices = env["fix.ar.invoice"].sudo()
    invoiced_groups = {}
    for branch, total in invoices._read_group(
        _bi_domain(
            env,
            "fix.ar.invoice",
            [
                ("state", "in", ISSUED_INVOICE_STATES),
                ("invoice_date", ">=", month_start),
            ],
        ),
        groupby=["branch_id"],
        aggregates=["taxable_amount:sum"],
    ):
        invoiced_groups[branch.id if branch else 0] = total or 0.0
    rows = []
    for branch, total in groups:
        key = branch.id if branch else 0
        rows.append(
            {
                "branch": branch.name if branch else "Unassigned",
                "orders": total,
                "open": open_groups.get(key, 0),
                "in_repair": repair_groups.get(key, 0),
                "delivered_mtd": delivered_groups.get(key, 0),
                "invoiced_mtd": round(invoiced_groups.get(key, 0.0), 2),
            }
        )
    rows.sort(key=lambda r: (-r["invoiced_mtd"], -r["open"], r["branch"]))
    totals = {
        "branch": "Total",
        "orders": sum(r["orders"] for r in rows),
        "open": sum(r["open"] for r in rows),
        "in_repair": sum(r["in_repair"] for r in rows),
        "delivered_mtd": sum(r["delivered_mtd"] for r in rows),
        "invoiced_mtd": round(sum(r["invoiced_mtd"] for r in rows), 2),
    }
    return _pack(
        "Branch League — orders, workload and invoiced value",
        ["branch", "orders", "open", "in_repair", "delivered_mtd", "invoiced_mtd"],
        {
            "branch": "Branch",
            "orders": "Orders (all time)",
            "open": "Open Now",
            "in_repair": "In Repair",
            "delivered_mtd": "Delivered MTD",
            "invoiced_mtd": "Invoiced Taxable MTD",
        },
        rows,
        [
            "League order: invoiced taxable value this month, then open workload. "
            "Branch is the owning branch on the order/invoice."
        ],
        totals=totals if rows else None,
    )


def service_kpi_pack(env, date_from=None, date_to=None, **params):
    m = _metrics(env)
    orders = env["fix.service.order"].sudo()
    state_rows = orders._read_group(
        _bi_domain(env, "fix.service.order", []),
        groupby=["state"],
        aggregates=["__count"],
    )
    rows = [
        {"metric": "Open orders", "value": m["open_orders"], "basis": "non-terminal states"},
        {"metric": "In repair", "value": m["in_repair"], "basis": "state=in_repair"},
        {
            "metric": "SLA overdue",
            "value": m["sla_overdue"],
            "basis": "open orders past sla_resolution_deadline",
        },
        {"metric": "QC failed", "value": m["qc_failed"], "basis": "state=qc_failed"},
        {
            "metric": "Estimates awaiting approval",
            "value": m["estimates_awaiting"],
            "basis": "fix.estimate state=sent",
        },
        {
            "metric": "Delivered MTD",
            "value": m["delivered_mtd"],
            "basis": "delivered/closed this month",
        },
    ]
    for state, count in sorted(state_rows, key=lambda r: -r[1]):
        rows.append(
            {"metric": "Orders in %s" % state, "value": count, "basis": "state distribution"}
        )
    return _pack(
        "Service KPI Pack — operations measures and state distribution",
        ["metric", "value", "basis"],
        {"metric": "Measure", "value": "Value", "basis": "Basis"},
        rows,
        [
            "SLA overdue uses the order's own resolution deadline; QC failed is the "
            "rework queue, not a quality score."
        ],
    )


def finance_pack(env, date_from=None, date_to=None, **params):
    m = _metrics(env)
    rows = [
        {
            "metric": "Invoiced taxable MTD",
            "value": m["invoiced_taxable_mtd"],
            "basis": "AR invoices issued/paid this month",
        },
        {
            "metric": "Invoices issued MTD",
            "value": m["invoiced_mtd"],
            "basis": "count of the same invoices",
        },
        {
            "metric": "Collected MTD",
            "value": m["collected_mtd"],
            "basis": "confirmed receipts this month",
        },
        {
            "metric": "AR outstanding",
            "value": m["ar_outstanding"],
            "basis": "issued invoices with residual",
        },
        {
            "metric": "Overdue > 60d",
            "value": m["overdue_gt_60d"],
            "basis": "residual past customer terms",
        },
        {
            "metric": "Active dunning rows",
            "value": m["dunning_active"],
            "basis": "fix.dunning on issued invoices",
        },
    ]
    return _pack(
        "Finance Pack — billing and receivables",
        ["metric", "value", "basis"],
        {"metric": "Measure", "value": "Value", "basis": "Basis"},
        rows,
        ["All values are live AR reads shared with M20 (one source of truth)."],
    )


def people_pack(env, date_from=None, date_to=None, **params):
    m = _metrics(env)
    rows = [
        {
            "metric": "Active employees",
            "value": m["employees_active"],
            "basis": "hr.employee active",
        },
        {
            "metric": "Checked in today",
            "value": m["present_today"],
            "basis": "hr.attendance check_in today",
        },
        {
            "metric": "Open requisitions",
            "value": m["requisitions_open"],
            "basis": "fix.requisition draft/approved",
        },
    ]
    return _pack(
        "People Pack — workforce presence and hiring demand",
        ["metric", "value", "basis"],
        {"metric": "Measure", "value": "Value", "basis": "Basis"},
        rows,
        [
            "Presence is the HR attendance record, not a badge feed; requisitions are "
            "the demand signal from M16."
        ],
    )


def export_catalog(env, date_from=None, date_to=None, **params):
    """The 'any dashboard → export' promise: every M25 pack with its live API
    and the formats the platform can actually deliver (CSV from the workspace
    button; JSON from the same endpoint)."""
    rows = []
    for key in (
        "executive_pack",
        "branch_league",
        "service_kpi_pack",
        "finance_pack",
        "people_pack",
        "weekly_exec_review",
    ):
        rows.append(
            {
                "report": key,
                "endpoint": "/p03/model/report (module=M25, report=%s)" % key,
                "formats": "CSV · JSON",
                "dashboards": "CEO · COO · CFO · CCO · Service · Finance · People · Quality",
            }
        )
    try:
        saved = env["fix.bi.dashboard"].sudo().search([("company_id", "in", _companies(env))])
        for d in saved:
            rows.append(
                {
                    "report": d.name,
                    "endpoint": "/p03/bi/role (role=%s)" % d.role,
                    "formats": "CSV · JSON",
                    "dashboards": "Saved dashboard (%s)" % d.role,
                }
            )
    except Exception:
        # Saved dashboards are an optional extra on this list; a failure to
        # read them must not hide the packs above, but it must not be silent.
        _logger.warning("BI export list: saved dashboards unavailable", exc_info=True)
    return _pack(
        "Any dashboard → export — every pack and its live endpoint",
        ["report", "endpoint", "formats", "dashboards"],
        {
            "report": "Report / Dashboard",
            "endpoint": "Live Endpoint",
            "formats": "Formats",
            "dashboards": "Used By",
        },
        rows,
        [
            "CSV is produced by the stable /p03/model/report payload; the workspace "
            "Export button downloads it. PDF/XLSX rendering is a print-template phase."
        ],
    )


def dataset_catalog(env, date_from=None, date_to=None, **params):
    """Certified datasets = the BI sync configurations that define a scope,
    with their measured freshness. Configuration only; nothing is invented."""
    rows = []
    for cfg in (
        env["fix.bi.sync.config"]
        .sudo()
        .search([("company_id", "in", _companies(env))], order="sequence, id")
    ):
        last = (
            env["fix.bi.sync.log"]
            .sudo()
            .search(
                [("config_id", "=", cfg.id), ("status", "=", "success")],
                order="ran_at desc",
                limit=1,
            )
        )
        rows.append(
            {
                "dataset": cfg.dataset_scope or "(scope not set)",
                "config": cfg.name,
                "frequency": cfg.sync_frequency or "",
                "enabled": "✓" if cfg.enabled else "✗",
                "last_success": last.ran_at.strftime("%Y-%m-%d %H:%M") if last.ran_at else "—",
            }
        )
    return _pack(
        "Certified Datasets — sync configurations and measured freshness",
        ["dataset", "config", "frequency", "enabled", "last_success"],
        {
            "dataset": "Dataset Scope",
            "config": "Configuration",
            "frequency": "Frequency",
            "enabled": "Enabled",
            "last_success": "Last Successful Snapshot",
        },
        rows,
        [
            "A dataset is certified when its sync configuration exists and its snapshot "
            "engine has run; freshness is the newest successful run."
        ],
        empty="No BI sync configuration exists yet.",
    )


REPORTS.update(
    {
        "executive_pack": executive_pack,
        "branch_league": branch_league,
        "service_kpi_pack": service_kpi_pack,
        "finance_pack": finance_pack,
        "people_pack": people_pack,
        "export_catalog": export_catalog,
        "dataset_catalog": dataset_catalog,
    }
)
