# A11 · M25 Business Intelligence — the surfaces the generic workspace
# endpoints may serve (SURFACES), the Weekly Executive Business Review
# (REPORTS) and the live executive dashboard payloads (/p03/bi/kpis,
# /p03/bi/exec). Every number is a measured read of the real service order,
# estimate and AR invoice tables — nothing here invents data.
#
# A11 audit E5/E6 (M25-1/-2/-3/-7): every read is the CALLER's read — the
# user's own record rules apply and every source is filtered by the caller's
# allowed companies. Only members of the explicit "BI company-wide" group get
# cross-OU company-wide tiles. "Delivered MTD" counts delivered_at/closed_at
# stamps (an edit no longer resurrects a January delivery), the
# approved-estimate tile is named what it is (Approved quotes), and the
# count tiles count records instead of carrying constants.
#
# Deep-audit fixes (Nov 2026): the AR figures include the legacy take-on
# still open on the AR control (M20's source of truth — the live estate
# carries 15.4 crore of it that the invoice-only tiles reported as 0); each
# optional metric source runs in its own savepoint so one SQL failure cannot
# blank every tile and abort the export; cockpit telemetry is written before
# the payload; money columns carry ৳ on screen and in every export; packs
# honour (or refuse) their period parameters instead of ignoring them.
import datetime
import logging

from odoo import http
from odoo.exceptions import AccessError, UserError
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
        # E7/M25-10: the log is append-only — no row action at all.
        "order": "ran_at desc, id desc",
        "limit": 100,
        "actions": set(),
    },
    "fix.bi.dashboard": {
        # G8: the lifecycle — review entry, certification through M63, and
        # retirement. There is no direct "certify" click: activation runs
        # only from an approved request in the approver's inbox.
        "order": "role, name",
        "limit": 200,
        # M25 pass 2: the steward's verification (BRU-BID-10) before the request
        "actions": {
            "action_submit_review",
            "action_steward_verify",
            "action_request_approval",
            "action_retire",
        },
    },
    "fix.bi.distribution.schedule": {
        "order": "name",
        "limit": 200,
        "actions": {"action_send_now"},
    },
    "fix.bi.alert.subscription": {
        "order": "name",
        "limit": 200,
        "actions": set(),
    },
    # FR-BID-034: the spreadsheet-retirement register. The lifecycle moves
    # only through these actions; the model refuses typed state changes.
    "fix.bi.manual.pack": {
        "order": "state, name",
        "limit": 200,
        "actions": {
            "action_start_parallel_run",
            "action_reconcile_matched",
            "action_reconcile_discrepancy",
            "action_retire",
        },
    },
    # M25 second capture pass (19 Nov 2026): the records the spec names for
    # each page. Lifecycle fields move only through these actions.
    "fix.bi.annotation": {"order": "create_date desc, id desc", "limit": 200, "actions": set()},
    "fix.bi.report.definition": {
        "order": "report_key",
        "limit": 200,
        "actions": {"action_certify", "action_retire", "action_generate_run"},
    },
    "fix.bi.report.run": {
        "order": "generated_at desc, id desc",
        "limit": 200,
        "actions": {"action_flag_restatement"},
    },
    "fix.bi.exploration": {
        "order": "write_date desc, id desc",
        "limit": 200,
        "actions": {"action_run", "action_share", "action_promote"},
    },
    "fix.bi.alert.instance": {
        "order": "raised_at desc, id desc",
        "limit": 200,
        "actions": {"action_acknowledge", "action_close"},
    },
    "fix.bi.embedded.surface": {
        "order": "host_module, host_screen",
        "limit": 200,
        "actions": {"action_activate", "action_retire"},
        # an internal audience is an internal group, never a portal one
        "pickers": {"audience_group_id": [("share", "=", False)]},
    },
    "fix.bi.content.usage": {"order": "viewed_at desc, id desc", "limit": 200, "actions": set()},
    # E6/BRU-BID-11: the export audit trail (append-only, no actions).
    "fix.bi.export.log": {
        "order": "ran_at desc, id desc",
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


def _has_bi_group(env, xmlid):
    """Membership of a cd_bi_reporting group (True for the superuser). The
    portal does not depend on that module, so resolve by xmlid through the
    user's own group set — has_group traverses implications, so a BI Finance
    Reader (whose group implies the company-wide one) counts for both gates;
    the old `env.user in group.user_ids` missed every implied member."""
    if env.su:
        return True
    return env.user.has_group(xmlid)


def _is_company_wide(env):
    """E6: the explicit executive charter — cross-OU reads INSIDE the
    allowed companies. Everyone else reads under their own record rules."""
    return _has_bi_group(env, "cd_bi_reporting.group_bi_company_wide")


def _read(env, model):
    """E6: the handle every M25 read goes through. Company-wide readers get
    sudo + an explicit company filter (their charter); everyone else gets
    the caller's env, so the OU/company record rules apply (BRU-BID-02)."""
    if _is_company_wide(env):
        return env[model].sudo()
    return env[model]


def _bi_domain(env, model, extra):
    """The read domain: the caller's allowed companies, explicitly."""
    domain = list(extra)
    if "company_id" in env[model]._fields:
        domain.append(("company_id", "in", _companies(env)))
    return domain


def _require_finance_reader(env):
    """E6 (M25-2): finance figures are not for every internal user."""
    if not _has_bi_group(env, "cd_bi_reporting.group_bi_finance"):
        raise UserError(
            "The finance pack is reserved for BI Finance Readers (M25) — AR "
            "outstanding, overdue and collections figures are not served to "
            "your account."
        )


def _require_company_wide(env):
    """E6 (M25-2): the executive pack crosses operating units — that is the
    company-wide group's explicit charter, nobody else's."""
    if not _is_company_wide(env):
        raise UserError(
            "The executive pack is reserved for BI Company-Wide Readers "
            "(M25). Your dashboards stay scoped to your own record rules."
        )


def _delivered_extra(start):
    """E5 (M25-3): delivered in the window by its OWN stamp — delivered_at
    or closed_at — never write_date (an edit must not resurrect a January
    delivery into this month's count)."""
    return [
        ("state", "in", ["delivered", "closed"]),
        "|",
        ("delivered_at", ">=", start),
        ("closed_at", ">=", start),
    ]


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
    opened and delivered (by delivery stamp, E5), approved estimate value,
    issued AR invoices."""
    orders = _read(env, "fix.service.order")
    estimates = _read(env, "fix.estimate")
    invoices = _read(env, "fix.ar.invoice")
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

    # E5 (M25-3): a delivery is counted in the week the order was DELIVERED
    # or CLOSED (its own stamp) — never in the week somebody edited it.
    delivered = {}
    for rec in orders.search(
        _bi_domain(
            env,
            "fix.service.order",
            _delivered_extra(datetime.datetime.combine(mondays[0], datetime.time.min)),
        )
    ):
        stamp = rec.delivered_at or rec.closed_at
        if stamp:
            stamp = stamp.date() if isinstance(stamp, datetime.datetime) else stamp
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
            # A1-F03: the estimate buckets are keyed by the week the estimate
            # was CREATED (fix.estimate has no approval-date stamp to bucket
            # by) — the note says created, not approved.
            "Estimate value counts APPROVED estimates in the week they were created "
            "(fix.estimate carries no approval-date stamp); invoiced counts customer "
            "invoices issued or paid.",
            "Delivered counts orders by the date they were delivered or closed; a later edit "
            "does not move them.",
        ],
        "kinds": {"estimates_approved": "monetary", "invoiced_taxable": "monetary"},
    }


def commercial_board(env, **params):
    """CCO commercial board: pipeline definitions by revenue stream and the open
    opportunity value by stage (crm.lead). Nothing is forecast beyond what the
    pipeline records hold."""
    pipelines = _read(env, "fix.pipeline").search([("active", "=", True)])
    # A1-F13: the lead totals are PER PIPELINE (crm.lead.pipeline_id), not the
    # company-wide search repeated on every row. A build without that relation
    # drops the two columns rather than inventing a per-pipeline split.
    leads = _read(env, "crm.lead")
    per_pipeline = "pipeline_id" in leads._fields
    if per_pipeline:
        leads = leads.search(_bi_domain(env, "crm.lead", [("type", "=", "opportunity")]))
    else:
        leads = leads.browse()
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
        mine = (
            leads.filtered(lambda lead, p=pipeline: lead.pipeline_id.id == p.id)
            if per_pipeline
            else leads
        )
        rows.append(
            {
                "stream": stream,
                "pipeline": pipeline.code,
                "stages": stage_count,
                "probability": pipeline.default_probability or 0.0,
                "open_opportunities": len(mine) if per_pipeline else None,
                "open_value": round(sum(mine.mapped("expected_revenue")), 2)
                if per_pipeline
                else None,
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
            "open_value": "Open Expected Revenue (৳)",
        },
        rows,
        [
            "Stage count comes from the pipeline's own stage definition. Open value sums "
            "expected_revenue on THIS pipeline's open CRM opportunities (leads without a "
            "pipeline are counted nowhere) - it is not a forecast model."
        ],
        empty="No active pipelines.",
        kinds={"open_value": "monetary"},
    )


REPORTS = {
    "weekly_exec_review": weekly_exec_review,
}

REPORTS["commercial_board"] = commercial_board


def _exec_payload(env):
    """The Executive C-Suite KPI dashboard payload — all live reads, each
    under the caller's scope (or the company-wide charter when granted)."""
    orders = _read(env, "fix.service.order")
    estimates = _read(env, "fix.estimate")
    invoices = _read(env, "fix.ar.invoice")
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
            _delivered_extra(datetime.datetime.combine(month_start, datetime.time.min)),
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
    freshness = env["fix.bi.sync.log"].freshness_minutes()

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
    # A1-F02: the group value is the branch record (or a False group for
    # unassigned orders) — resolve the DISPLAY NAME in one lookup instead of
    # letting the raw ORM repr ("fix.branch(281,)") reach the CEO board.
    branch_ids = {b.id for b, _count in branch_rows if b}
    branch_names = {
        b.id: b.display_name for b in _read(env, "fix.branch").browse(sorted(branch_ids)) if b
    }
    branches = sorted(
        (
            {"branch": branch_names.get(b.id, "Unassigned") if b else "Unassigned", "open": c}
            for b, c in branch_rows
        ),
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
        # A3-F03: while a data entity is flagged degraded the executive board
        # says so too, not just the role cockpits
        "notes": _quality_incident_notes(env),
    }


class P03BiApi(http.Controller):
    """M25 live endpoints for the workspace shell."""

    @http.route("/p03/bi/kpis", type="jsonrpc", auth="user", readonly=True)
    def bi_kpis(self, module=None, **kw):
        _require_internal(request.env)
        env = request.env
        payload = _exec_payload(env)
        fresh = payload["kpis"]["bi_data_freshness"]
        # A1-F01: each optional KPI probe runs in its own savepoint and a
        # failure is logged — one broken source withholds only ITS tile.
        try:
            with env.cr.savepoint():
                # A1-F03: "live" counts what a reader can actually open — a
                # CERTIFIED dashboard (drafts are the author's workspace and
                # retired ones left the audience; BRU-BID-06).
                dashboards = _read(env, "fix.bi.dashboard").search_count(
                    _bi_domain(env, "fix.bi.dashboard", [("state", "=", "certified")])
                )
        except Exception as exc:
            _logger.warning("M25 metric dashboards_live unavailable: %s", exc)
            dashboards = None
        try:
            with env.cr.savepoint():
                schedules = _read(env, "fix.bi.distribution.schedule").search_count(
                    _bi_domain(env, "fix.bi.distribution.schedule", [("active", "=", True)])
                )
        except Exception as exc:
            _logger.warning("M25 metric scheduled_distributions unavailable: %s", exc)
            schedules = None
        usage = _weekly_usage(env)
        # KPI-094: packs retired from the spreadsheet-retirement register
        # (FR-BID-034); None - withheld - when the register is unreadable.
        try:
            with env.cr.savepoint():
                retired = _read(env, "fix.bi.manual.pack").search_count(
                    _bi_domain(env, "fix.bi.manual.pack", [("state", "=", "retired")])
                )
        except Exception as exc:
            _logger.warning("M25 metric spreadsheets_retired unavailable: %s", exc)
            retired = None
        return {
            "M25": {
                "bi_data_freshness": fresh if fresh is not None else "never",
                "open_orders": payload["kpis"]["open_orders"],
                "in_repair": payload["kpis"]["in_repair"],
                "delivered_mtd": payload["kpis"]["delivered_mtd"],
                # A1-F03: the key keeps its historical name for compatibility,
                # but what it holds is the value of APPROVED QUOTES — the
                # companion key says so.
                "revenue_mtd": payload["kpis"]["revenue_mtd"],
                "approved_quotes_mtd": payload["kpis"]["revenue_mtd"],
                "invoiced_mtd": payload["kpis"]["invoiced_mtd"],
                # registry KPI strip (M25 spec): MEASURED counts (E5/M25-7 —
                # the old `9 +` and constant `6` are gone).
                "dashboards_live": dashboards,
                # A1-F03: the canonical library (STANDARD_REPORTS, 6) — not
                # len(REPORTS), which counts self-listing catalogues too.
                "standard_reports": len(STANDARD_REPORTS),
                "weekly_manager_usage": usage,
                "load_time_p95": None,
                "scheduled_distributions": schedules,
                "spreadsheets_retired": retired,
            }
        }

    @http.route("/p03/bi/exec", type="jsonrpc", auth="user", readonly=True)
    def bi_exec(self, **kw):
        _require_internal(request.env)
        # E6 (M25-2): the executive payload carries company-wide money
        # figures — that read belongs to the company-wide group's charter.
        _require_company_wide(request.env)
        return _exec_payload(request.env)

    # not readonly: a view writes its usage row (FR-BID-033)
    @http.route("/p03/bi/role", type="jsonrpc", auth="user")
    def bi_role(self, role="ceo", **kw):
        _require_internal(request.env)
        role = role or "ceo"
        if role == "cfo":
            # E6 (M25-2): the CFO dashboard is the finance pack with a
            # different layout — same entitlement.
            _require_finance_reader(request.env)
        elif role == "all":
            _require_company_wide(request.env)
        # FR-BID-033 + A1-F05: the view is logged BEFORE the payload is
        # computed — a failing metric source used to abort the transaction
        # and silently destroy the telemetry row with it.
        try:
            agent = request.httprequest.headers.get("User-Agent")
        except Exception:
            agent = None
        if "fix.bi.content.usage" in request.env:
            logged = request.env["fix.bi.content.usage"]._log_view(
                "role_dashboard", "M25:%s" % role, agent
            )
            if not logged:
                _logger.warning(
                    "M25 usage telemetry not written for role %s (see _log_view)", role
                )
        payload = _role_payload(request.env, role)
        payload["notes"] = (
            payload["notes"]
            + _annotation_notes(request.env, role)
            + _quality_incident_notes(request.env)
        )
        return payload

    @http.route("/p03/bi/embed/token", type="jsonrpc", auth="user")
    def bi_embed_token(self, surface_id=None, record_ref=None, **kw):
        """AUT-BID-16: a short-lived, scope-bound, single-use embed token."""
        # sudo reads the placement only; the viewer is still env.user, and
        # _issue_token checks THEM against the surface's audience
        surface = (
            request.env["fix.bi.embedded.surface"].sudo().browse(int(surface_id or 0)).exists()
        )
        if not surface:
            return {"error": "Unknown embedded surface"}
        try:
            return surface._issue_token(record_ref=record_ref)
        except (UserError, AccessError) as exc:
            return {"error": str(exc.args[0] if exc.args else exc)}


def _annotation_notes(env, role):
    """FR-BID-009: the owners' explanations shown to the cockpit's audience."""
    try:
        rows = env["fix.bi.annotation"]._for_role(role)
    except Exception:
        return []
    return [
        "%s (%s%s, %s): %s%s"
        % (
            a.name,
            a.period,
            (" · %s" % a.metric_key) if a.metric_key else "",
            a.author_id.name,
            a.text_en,
            (" / %s" % a.text_bn) if a.text_bn else "",
        )
        for a in rows
    ]


def _quality_incident_notes(env):
    """A3-F03 (the M62 half of the degraded-surface rule): while any data
    entity is flagged degraded, every cockpit says so — a figure from an
    affected source may be wrong and the reader is told before they read a
    tile. The model is optional (M62 not installed → no note, never an
    error), and the read sits in its own savepoint."""
    if "fix.data.entity" not in env:
        return []
    try:
        with env.cr.savepoint():
            degraded = _read(env, "fix.data.entity").search(
                _bi_domain(env, "fix.data.entity", [("degraded", "=", True)]), limit=20
            )
            if not degraded:
                return []
            return [
                "Data quality incident open on %s — figures from that source may be affected."
                % ", ".join(degraded.mapped("name"))
            ]
    except Exception as exc:
        _logger.warning("M25 quality incident note unavailable: %s", exc)
        return []


def _weekly_usage(env):
    """Distinct users who viewed BI content in the last 7 days
    (fix.bi.content.usage — the module's own telemetry, FR-BID-033). A1-F03:
    the old basis counted res.users.log (any login, BI or not); the tile is
    named manager usage of BI, so 0 is honest when nobody used BI. E6: read
    through _read within the caller's companies, so a caller who may not read
    the log at all has the tile WITHHELD (None → '—') instead of a sudo
    count of a source they cannot see (M25 K07)."""
    try:
        with env.cr.savepoint():
            since = datetime.datetime.now() - datetime.timedelta(days=7)
            rows = _read(env, "fix.bi.content.usage").search(
                _bi_domain(env, "fix.bi.content.usage", [("viewed_at", ">=", since)])
            )
            return len(set(rows.mapped("user_id").ids))
    except Exception as exc:
        _logger.warning("M25 metric weekly_manager_usage unavailable: %s", exc)
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


def _to_date(value, label="date_to"):
    """A1-F04: period parameters arrive as strings (the run generator stamps
    str(date)); coerce once, refusing garbage loudly."""
    if value in (None, ""):
        return None
    if isinstance(value, datetime.datetime):
        return value.date()
    if isinstance(value, datetime.date):
        return value
    try:
        return datetime.date.fromisoformat(str(value)[:10])
    except ValueError as exc:
        raise UserError("%s must be a date (YYYY-MM-DD), not %r." % (label, value)) from exc


def _resolve_period(date_from, date_to):
    """A1-F04: the period an MTD pack actually applies. The window is
    month-to-date ENDING at date_to (default today); a date_from that is not
    the first of that month is refused — before, a run could be stamped with
    a period the pack silently never applied."""
    end = _to_date(date_to) or datetime.date.today()
    month_start = end.replace(day=1)
    start = _to_date(date_from, "date_from")
    if start is not None and start != month_start:
        raise UserError(
            "This pack is measured month-to-date; date_from must be the first of "
            "the month (use %s for the month of %s, or leave date_from empty)."
            % (month_start, end)
        )
    return end


def _takeon_ar_totals(env, as_of=None):
    """The legacy take-on still open on the AR control, summed over the
    caller's companies — the SAME source of truth M20 reads (its
    takeon_ar_opening, which reads the GL as superuser: WE gate who sees the
    result). Returns (outstanding, overdue_60d) or (None, None) when the
    caller holds no finance entitlement or the helper is unavailable
    (D-L01/A1-F07: the live estate carries 15.4 crore of migrated open
    receivables the invoice-only tiles reported as 0)."""
    if not (_has_bi_group(env, "cd_bi_reporting.group_bi_finance") or _is_company_wide(env)):
        return None, None
    try:
        with env.cr.savepoint():
            from odoo.addons.cd_billing_engine.models.fix_ar_engine import takeon_ar_opening

            outstanding = overdue = 0.0
            for company in env["res.company"].browse(_companies(env)):
                for opening in takeon_ar_opening(env, company, as_of=as_of).values():
                    residual = opening["residual"] or 0.0
                    outstanding += residual
                    # the SAME basis M20's ageing and ECL run use
                    # (fix_ar_impairment.action_compute): days past the
                    # take-on's OWN date; >60 is past the d31_60 bucket.
                    if opening["date"] and (as_of - opening["date"]).days > 60:
                        overdue += residual
            return outstanding, overdue
    except Exception as exc:
        _logger.warning("M25 metric ar_outstanding_takeon unavailable: %s", exc)
        return None, None


def _gl_ar_balance(env):
    """A1-F07: the receivable control balance per the GENERAL LEDGER — the
    Σ balance of posted move lines on receivable accounts (asset_receivable)
    in the caller's companies, read as the CALLER through _read (their
    record rules; never a raw sudo — a caller who may not read the GL gets
    None and the pack says 'GL not readable by your account')."""
    try:
        with env.cr.savepoint():
            groups = _read(env, "account.move.line")._read_group(
                [
                    ("company_id", "in", _companies(env)),
                    ("parent_state", "=", "posted"),
                    ("account_id.account_type", "=", "asset_receivable"),
                ],
                [],
                ["balance:sum"],
            )
            return round(sum(g[0] or 0.0 for g in groups), 2)
    except Exception as exc:
        _logger.warning("M25 metric gl_ar_balance unavailable: %s", exc)
        return None


def _metrics(env, as_of=None):
    """The measured metric bank every role dashboard and pack reads from.
    E6: every read is the caller's read (record rules apply) filtered by the
    caller's companies; a source the caller may not read withholds its tile
    instead of leaking through sudo.

    A1-F04: `as_of` (default today) anchors the month-to-date windows, so a
    pack generated for a past month reports that month; snapshot counts (open
    orders, headcount, dunning...) stay CURRENT and the pack notes say so.
    A1-F01: every optional source runs in its own savepoint and a failure is
    logged — one broken source withholds only its own tiles, never the
    transaction."""
    today = as_of or datetime.date.today()
    month_start = today.replace(day=1)
    day_end = datetime.datetime.combine(today, datetime.time.max)
    orders = _read(env, "fix.service.order")
    estimates = _read(env, "fix.estimate")
    invoices = _read(env, "fix.ar.invoice")
    receipts = _read(env, "fix.ar.receipt")
    m = {}
    m["open_orders"] = orders.search_count(
        _bi_domain(env, "fix.service.order", [("state", "in", OPEN_ORDER_STATES)])
    )
    m["in_repair"] = orders.search_count(
        _bi_domain(env, "fix.service.order", [("state", "=", "in_repair")])
    )
    delivered_dom = _delivered_extra(datetime.datetime.combine(month_start, datetime.time.min))
    # as-of: the delivery stamp must also fall ON or BEFORE the as-of day (an
    # order closed without a delivered_at stamp is never excluded by it)
    delivered_dom += ["|", ("delivered_at", "=", False), ("delivered_at", "<=", day_end)]
    m["delivered_mtd"] = orders.search_count(_bi_domain(env, "fix.service.order", delivered_dom))
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
                    ("create_date", "<=", day_end),
                ],
            )
        ).mapped("grand_total")
    )
    inv_mtd = invoices.search(
        _bi_domain(
            env,
            "fix.ar.invoice",
            [
                ("state", "in", ISSUED_INVOICE_STATES),
                ("invoice_date", ">=", month_start),
                ("invoice_date", "<=", today),
            ],
        )
    )
    m["invoiced_mtd"] = len(inv_mtd)
    m["invoiced_taxable_mtd"] = sum(inv_mtd.mapped("taxable_amount"))
    # D-L01/A1-F07: the AR tiles (ALL of them — the legs and the totals) are
    # finance figures gated on the BI finance / company-wide entitlement; an
    # unentitled caller gets None ('—'), never a partial AR that pretends the
    # migrated take-on does not exist.
    if _has_bi_group(env, "cd_bi_reporting.group_bi_finance") or _is_company_wide(env):
        open_inv = invoices.search(
            _bi_domain(env, "fix.ar.invoice", [("state", "=", "issued")])
        ).filtered(lambda i: i.amount_residual > 0.005)
        m["ar_outstanding_invoices"] = sum(open_inv.mapped("amount_residual"))
        m["overdue_gt_60d_invoices"] = sum(
            i.amount_residual
            for i in open_inv
            if (today - i.invoice_date).days - i._payment_terms_days() > 60
        )
        # the migrated open receivables (M20's take-on) join the AR figures —
        # the SAME source of truth M20 reads, aged on the SAME basis
        takeon_open, takeon_overdue = _takeon_ar_totals(env, as_of=today)
        m["ar_outstanding_takeon"] = takeon_open
        m["overdue_gt_60d_takeon"] = takeon_overdue
        if takeon_open is None:
            # the helper is unavailable: the tile's stated basis is
            # "invoices + take-on", so showing the invoice half alone would
            # understate the AR — withhold instead (logged above)
            m["ar_outstanding"] = m["overdue_gt_60d"] = None
        else:
            m["ar_outstanding"] = m["ar_outstanding_invoices"] + takeon_open
            m["overdue_gt_60d"] = m["overdue_gt_60d_invoices"] + takeon_overdue
    else:
        for key in (
            "ar_outstanding_invoices",
            "overdue_gt_60d_invoices",
            "ar_outstanding_takeon",
            "overdue_gt_60d_takeon",
            "ar_outstanding",
            "overdue_gt_60d",
        ):
            m[key] = None
    m["collected_mtd"] = sum(
        receipts.search(
            _bi_domain(
                env,
                "fix.ar.receipt",
                [
                    ("state", "=", "confirmed"),
                    ("receipt_date", ">=", month_start),
                    ("receipt_date", "<=", today),
                ],
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
        with env.cr.savepoint():
            Complaints = _read(env, "fix.complaint")
            m["complaints_open"] = Complaints.search_count(
                _bi_domain(
                    env,
                    "fix.complaint",
                    [("state", "not in", ("closed", "resolved", "rejected", "cancelled"))],
                )
            )
            m["complaints_total"] = Complaints.search_count(_bi_domain(env, "fix.complaint", []))
    except Exception as exc:
        _logger.warning("M25 metric complaints_open/complaints_total unavailable: %s", exc)
        m["complaints_open"] = m["complaints_total"] = None
    try:
        with env.cr.savepoint():
            m["ncr_open"] = _read(env, "fix.ncr").search_count(
                _bi_domain(
                    env,
                    "fix.ncr",
                    [("state", "not in", ("closed", "verified", "rejected", "cancelled"))],
                )
            )
    except Exception as exc:
        _logger.warning("M25 metric ncr_open unavailable: %s", exc)
        m["ncr_open"] = None
    try:
        with env.cr.savepoint():
            Lead = _read(env, "crm.lead")
            # company filter explicit: a lead with no company shows nowhere
            # rather than on every company's board (K05).
            lead_dom = _bi_domain(
                env, "crm.lead", [("type", "=", "opportunity"), ("active", "=", True)]
            )
            m["leads_open"] = Lead.search_count(lead_dom)
            m["pipeline_value"] = sum(Lead.search(lead_dom).mapped("expected_revenue"))
    except Exception as exc:
        _logger.warning("M25 metric leads_open/pipeline_value unavailable: %s", exc)
        m["leads_open"] = m["pipeline_value"] = None
    try:
        with env.cr.savepoint():
            m["loyalty_members"] = _read(env, "fix.loyalty.account").search_count(
                _bi_domain(env, "fix.loyalty.account", [])
            )
    except Exception as exc:
        _logger.warning("M25 metric loyalty_members unavailable: %s", exc)
        m["loyalty_members"] = None
    try:
        with env.cr.savepoint():
            m["employees_active"] = _read(env, "hr.employee").search_count(
                _bi_domain(env, "hr.employee", [("active", "=", True)])
            )
            m["present_today"] = _read(env, "hr.attendance").search_count(
                [
                    ("check_in", ">=", datetime.datetime.combine(today, datetime.time.min)),
                    ("employee_id.company_id", "in", _companies(env)),
                ]
            )
    except Exception as exc:
        _logger.warning("M25 metric employees_active/present_today unavailable: %s", exc)
        m["employees_active"] = m["present_today"] = None
    try:
        with env.cr.savepoint():
            m["requisitions_open"] = _read(env, "fix.requisition").search_count(
                _bi_domain(env, "fix.requisition", [("state", "in", ("draft", "approved"))])
            )
    except Exception as exc:
        _logger.warning("M25 metric requisitions_open unavailable: %s", exc)
        m["requisitions_open"] = None
    try:
        with env.cr.savepoint():
            m["dunning_active"] = _read(env, "fix.dunning").search_count(
                [
                    ("invoice_id.state", "=", "issued"),
                    ("invoice_id.company_id", "in", _companies(env)),
                ]
            )
    except Exception as exc:
        _logger.warning("M25 metric dunning_active unavailable: %s", exc)
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
                    # E5 (M25-3): named what it measures — the value of
                    # approved quotes, NOT booked revenue.
                    _k("Approved Quotes MTD", m["revenue_mtd"], money=True),
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
                    _k("Approved Quotes MTD", m["revenue_mtd"], money=True),
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
            "Each view of this cockpit is logged with its device class (FR-BID-033); "
            "p95 load time has no measurement yet and is never invented.",
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
    # E6 (M25-2): company-wide figures are the company-wide group's charter.
    _require_company_wide(env)
    m = _metrics(env)
    rows = [
        {
            "metric": "Approved quotes MTD (estimate value)",
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
            "basis": "orders with a delivered_at/closed_at stamp this month",
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
    orders = _read(env, "fix.service.order")
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
                _delivered_extra(datetime.datetime.combine(month_start, datetime.time.min)),
            ),
            groupby=["branch_id"],
            aggregates=["__count"],
        )
    }
    invoices = _read(env, "fix.ar.invoice")
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
    orders = _read(env, "fix.service.order")
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
            "basis": "delivered_at/closed_at stamped this month",
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
    # E6 (M25-2): AR outstanding, overdue and collections are finance-reader
    # figures — the pack (screen AND export) is gated, and every export is
    # logged by the download route (BRU-BID-11).
    _require_finance_reader(env)
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
        saved = _read(env, "fix.bi.dashboard").search(_bi_domain(env, "fix.bi.dashboard", []))
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
    for cfg in _read(env, "fix.bi.sync.config").search(
        _bi_domain(env, "fix.bi.sync.config", []), order="sequence, id"
    ):
        last = _read(env, "fix.bi.sync.log").search(
            [("config_id", "=", cfg.id), ("status", "=", "success")],
            order="ran_at desc",
            limit=1,
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


# The standard report library (FR-BID-011): every canonical pack, who it is
# for and who may open it. Entitlements mirror the on-screen gates
# (_require_company_wide / _require_finance_reader) - not a second policy.
STANDARD_REPORTS = (
    ("executive_pack", "Executive Pack", "CEO, board", "BI Company-Wide Reader"),
    ("branch_league", "Branch League", "COO, branch managers", "Internal user (own scope)"),
    ("service_kpi_pack", "Service KPI Pack", "Service heads", "Internal user (own scope)"),
    ("finance_pack", "Finance Pack", "CFO, finance", "BI Finance Reader"),
    ("people_pack", "People Pack", "HR", "Internal user (own scope)"),
    (
        "weekly_exec_review",
        "Weekly Executive Review",
        "Executive team",
        "Internal user (own scope)",
    ),
)


def report_library(env, date_from=None, date_to=None, **params):
    """Standard Report Library: each canonical pack with its audience, the
    entitlement that opens it, the distributions scheduled for it and how
    often it left the system in the last 30 days (export log). Measured, not
    declared: a pack nobody schedules or exports shows zeros."""
    since = datetime.datetime.now() - datetime.timedelta(days=30)
    schedules = _read(env, "fix.bi.distribution.schedule")
    try:
        exports = _read(env, "fix.bi.export.log")
        exports.check_access("read")
    except Exception:
        exports = None  # the export audit is a steward/operator read
    try:
        defs = {
            d.report_key: d
            for d in _read(env, "fix.bi.report.definition").search(
                _bi_domain(env, "fix.bi.report.definition", [])
            )
        }
    except Exception:
        defs = {}
    states = {"draft": "Draft", "certified": "Certified", "retired": "Retired"}
    rows = []
    for key, title, audience, entitlement in STANDARD_REPORTS:
        pack = "M25:%s" % key
        definition = defs.get(pack)
        scheduled = schedules.search_count(
            _bi_domain(
                env,
                "fix.bi.distribution.schedule",
                [("report_key", "=", pack), ("active", "=", True)],
            )
        )
        if exports is not None:
            used = exports.search_count([("pack", "=", pack), ("ran_at", ">=", since)])
            last = exports.search([("pack", "=", pack)], limit=1, order="ran_at desc")
            last_txt = last.ran_at.strftime("%Y-%m-%d %H:%M") if last else "—"
        else:
            used, last_txt = "—", "—"
        rows.append(
            {
                "report": title,
                "key": pack,
                "audience": audience,
                "entitlement": entitlement,
                "owner": definition.business_owner_id.name if definition else "Not registered",
                "certification": states.get(definition.certification_state) if definition else "—",
                "schedules": scheduled,
                "exports_30d": used,
                "last_export": last_txt,
            }
        )
    return _pack(
        "Standard Report Library — every canonical pack and its use",
        [
            "report",
            "key",
            "audience",
            "entitlement",
            "owner",
            "certification",
            "schedules",
            "exports_30d",
            "last_export",
        ],
        {
            "report": "Report",
            "key": "Report Key",
            "audience": "Audience",
            "entitlement": "Who May Open It",
            "owner": "Business Owner",
            "certification": "Certification",
            "schedules": "Active Schedules",
            "exports_30d": "Exports (30 days)",
            "last_export": "Last Export",
        },
        rows,
        [
            "Each pack is computed live from the transaction tables; open it from its chip. "
            "+ New Report Definition registers a pack's business owner and definition for "
            "a steward to certify (FR-BID-011); Generate Run stamps a reproducible run. "
            "To receive one by e-mail on a cadence, add a Distribution Schedule.",
            "Exports are read from the append-only export log (BRU-BID-11); a user who may "
            "not read that log sees '—'.",
        ],
    )


REPORTS.update(
    {
        "report_library": report_library,
        "executive_pack": executive_pack,
        "branch_league": branch_league,
        "service_kpi_pack": service_kpi_pack,
        "finance_pack": finance_pack,
        "people_pack": people_pack,
        "export_catalog": export_catalog,
        "dataset_catalog": dataset_catalog,
    }
)
