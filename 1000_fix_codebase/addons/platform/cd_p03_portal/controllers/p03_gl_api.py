# P03 GL API — the read/write endpoints behind the M19 in-workspace screens.
#
# Every screen of M19 (Chart of Accounts, Journals, Journal Entry, the five
# statements, the close console, periods, dimensions, suspense, subledger
# reconciliation and the audit trail) is fed from here — all values are live
# reads of the real Odoo models through the pure statement computations in
# cd_gl_ext. Write paths (JE draft/approve, close steps, locks, template and
# allocation runs) call the SAME model methods the Odoo forms use, so the
# SoD and COA-rule enforcement applies identically.
#
# Internal-user only (NVR-22). Read endpoints are readonly; nothing is
# fabricated — absent models/fields come back as None and the workspace keeps
# its honest placeholder.
import datetime
import logging

from odoo import http
from odoo.addons.cd_gl_ext.models.coa_logic import account_level
from odoo.addons.cd_gl_ext.models.fix_fiscal_year_ext import (
    compute_balance_sheet,
    compute_cash_flow,
    compute_consolidated,
    compute_pnl,
    compute_trial_balance,
)
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.http import request

from .p03_service_order_api import _require_internal, _user_error

_logger = logging.getLogger(__name__)


def _fy_window(today=None):
    """The Bangladesh fiscal year (July-June) containing today."""
    today = today or datetime.date.today()
    start = (
        datetime.date(today.year, 7, 1) if today.month >= 7 else datetime.date(today.year - 1, 7, 1)
    )
    return start, datetime.date(start.year + 1, 6, 30)


FINANCE_READ_GROUPS = (
    "account.group_account_readonly",
    "account.group_account_invoice",
    "account.group_account_user",
    "account.group_account_manager",
)


def _require_finance(env):
    """The ledger screens read as the system (balances across journals), so
    the caller must hold a finance role first (A08: a plain internal user used
    to read every posted entry, close and posting-log row here)."""
    _require_internal(env)
    if not env.su and not any(env.user.has_group(g) for g in FINANCE_READ_GROUPS):
        raise AccessError("The general ledger screens need a finance (accounting) role.")


def _parse_date(value, fallback):
    if not value:
        return fallback
    return datetime.date.fromisoformat(str(value)[:10])


class P03GlApiController(http.Controller):
    """M19 in-workspace screen data."""

    # ------------------------------------------------------------------ CoA

    @http.route("/p03/gl/coa", type="jsonrpc", auth="user", readonly=True)
    def gl_coa(self, **kw):
        _require_finance(request.env)
        env = request.env
        company = env.company
        chart = (
            env["fix.chart.account"]
            .sudo()
            .with_context(active_test=False)
            .search([("company_id", "=", company.id)], order="account_code")
        )
        # live ledger balances for every MAPPED statutory account
        odoo_ids = chart.mapped("odoo_account_id").ids
        balances = {}
        if odoo_ids:
            groups = (
                env["account.move.line"]
                .sudo()
                ._read_group(
                    [
                        ("company_id", "=", company.id),
                        ("parent_state", "=", "posted"),
                        ("account_id", "in", odoo_ids),
                    ],
                    ["account_id"],
                    ["balance:sum"],
                )
            )
            balances = {account.id: round(balance or 0.0, 2) for account, balance in groups}
        rows = []
        for acc in chart:
            rows.append(
                {
                    "id": acc.id,
                    "code": acc.account_code,
                    "name": acc.name,
                    "level": account_level(acc.account_code),
                    "type": acc.account_type,
                    "subtype": acc.account_subtype or "",
                    "postable": acc.is_postable,
                    "control": acc.is_control_account,
                    "control_subledger": acc.control_subledger or "",
                    "requires_dimension": acc.requires_dimension or "",
                    "statutory_group": acc.statutory_group or "",
                    "active": acc.active,
                    "deprecated": acc.is_deprecated,
                    "manual_balance": round(acc.balance or 0.0, 2),
                    "ledger_balance": balances.get(acc.odoo_account_id.id)
                    if acc.odoo_account_id
                    else None,
                    "odoo_account": (
                        {
                            "id": acc.odoo_account_id.id,
                            "code": acc.odoo_account_id.code,
                            "name": acc.odoo_account_id.name,
                        }
                        if acc.odoo_account_id
                        else None
                    ),
                }
            )
        return {
            "company": company.name,
            "count": len(rows),
            "mapped": len([r for r in rows if r["odoo_account"]]),
            # R4 (2026-11-07): summary strip inputs — postable / control /
            # deprecated / unlinked counts, computed on the same read.
            "postable": len([r for r in rows if r["postable"]]),
            "control": len([r for r in rows if r["control"]]),
            "deprecated": len([r for r in rows if r.get("deprecated")]),
            "unlinked": len([r for r in rows if not r["odoo_account"]]),
            "rows": rows,
        }

    # ------------------------------------------------------------- journals

    @http.route("/p03/gl/accounts", type="jsonrpc", auth="user", readonly=True)
    def gl_accounts(self, **kw):
        """The company's Odoo accounts for the JE editor's account picker."""
        _require_finance(request.env)
        env = request.env
        accounts = (
            env["account.account"]
            .sudo()
            .search([("company_ids", "in", env.company.id)], order="code")
        )
        branches = (
            env["fix.branch"].sudo().search([]).mapped(lambda b: {"id": b.id, "name": b.name})
        )
        return {
            "rows": accounts.mapped(
                lambda a: {
                    "id": a.id,
                    "code": a.code or "",
                    "name": a.name or "",
                    "type": a.account_type or "",
                }
            ),
            "branches": branches,
        }

    @http.route("/p03/gl/journals", type="jsonrpc", auth="user", readonly=True)
    def gl_journals(
        self,
        state=None,
        search=None,
        date_from=None,
        date_to=None,
        account_code=None,
        limit=60,
        **kw,
    ):
        _require_finance(request.env)
        env = request.env
        domain = [("company_id", "=", env.company.id)]
        if state:
            domain.append(("state", "=", state))
        if search:
            domain.append(("name", "ilike", search))
        if date_from:
            domain.append(("date", ">=", _parse_date(date_from, None)))
        if date_to:
            domain.append(("date", "<=", _parse_date(date_to, None)))
        if account_code:
            # statement drill-down: entries touching one account
            domain.append(("line_ids.account_id.code", "=", account_code))
        moves = env["account.move"].sudo().search(domain, order="date desc, id desc", limit=limit)
        rows = moves.mapped(
            lambda m: {
                "id": m.id,
                "name": m.name or "",
                "ref": m.ref or "",
                "date": str(m.date),
                "journal": m.journal_id.code or m.journal_id.name,
                "journal_name": m.journal_id.name,
                "partner": m.partner_id.name or "",
                "amount": round(m.amount_total or 0.0, 2),
                "currency": m.currency_id.name,
                "state": m.state,
                "move_type": m.move_type,
            }
        )
        journals = (
            env["account.journal"]
            .sudo()
            .search([("company_id", "=", env.company.id)])
            .mapped(lambda j: {"id": j.id, "code": j.code, "name": j.name, "type": j.type})
        )
        return {"rows": rows, "count": len(rows), "journals": journals}

    # -------------------------------------------------------------- one JE

    @http.route("/p03/gl/je", type="jsonrpc", auth="user", readonly=True)
    def gl_je(self, move_id=None, **kw):
        _require_finance(request.env)
        env = request.env
        move = env["account.move"].sudo().browse(int(move_id)).exists()
        if not move or move.company_id not in env.companies:
            return {"success": False, "error": "Journal entry not found"}
        dims = (
            env["fix.journal.dimension"].sudo().search([("move_line_id", "in", move.line_ids.ids)])
        )
        dim_by_line = {d.move_line_id.id: d for d in dims}
        log = env["fix.journal.posting.log"].sudo().search([("move_id", "=", move.id)], limit=1)
        return {
            "success": True,
            **self._je_review(env, move),
            "move": {
                "id": move.id,
                "name": move.name or "",
                "ref": move.ref or "",
                "date": str(move.date),
                "journal": move.journal_id.name,
                "state": move.state,
                "amount": round(move.amount_total or 0.0, 2),
                "currency": move.currency_id.name,
                "company": move.company_id.name,
            },
            "lines": [
                {
                    "id": line.id,
                    "account": "%s %s" % (line.account_id.code or "", line.account_id.name or ""),
                    "label": line.name or "",
                    "debit": round(line.debit or 0.0, 2),
                    "credit": round(line.credit or 0.0, 2),
                    "dimension": (
                        {
                            "branch": dim.branch_id.name or "",
                            "cost_centre": dim.cost_centre or "",
                            "business_line": dim.business_line or "",
                            "project": dim.project_ref or "",
                            "brand": dim.brand or "",
                            "channel": dim.channel or "",
                        }
                        if (dim := dim_by_line.get(line.id))
                        else None
                    ),
                }
                for line in move.line_ids
            ],
            "log": (
                {
                    "source": log.source,
                    "state": log.state,
                    "requested_by": log.requested_by.name or "",
                    "posted_by": log.posted_by.name or "",
                    "posted_at": str(log.posted_at or ""),
                }
                if log
                else None
            ),
        }

    def _je_review(self, env, move):
        """Where a draft stands in its review and what THIS user may do with it,
        so the entry screen offers only the buttons the server will honour. The
        models re-check everything; this only decides what is shown."""
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import _move_snapshot

        move = move.sudo()
        approval = env["fix.journal.approval"].sudo().search([("move_id", "=", move.id)], limit=1)
        request = approval.approval_request_id
        tasks = (
            request.task_ids.filtered(lambda t: t.state == "pending")
            if request
            else env["fix.workflow.task"].sudo()
        )
        rejection = (
            env["fix.approval.history"]
            .sudo()
            .search(
                [
                    ("res_model", "=", approval._name),
                    ("res_id", "=", approval.id),
                    ("event", "=", "rejected"),
                ],
                order="id desc",
                limit=1,
            )
            if approval
            else None
        )
        is_draft = move.state == "draft"
        manual = is_draft and move._fix_is_manual_entry()
        accountant = env.su or env.user.has_group("account.group_account_user")
        manager = env.su or env.user.has_group("account.group_account_manager")
        stale = approval.state == "pending" and approval.lines_snapshot != _move_snapshot(move)
        routable = not approval or approval.state in ("rejected", "voided") or stale
        preparer = env.uid in (move.create_uid | approval.requested_by_id).ids
        states = dict(approval._fields["state"].selection)
        return {
            "approval": (
                {
                    "id": approval.id,
                    "state": approval.state,
                    "state_label": states.get(approval.state, approval.state),
                    "tier": approval.dofa_tier_required or "",
                    "reason": approval.reason or "",
                    "requested_by": approval.requested_by_id.name or "",
                    "pending_with": tasks.mapped("assigned_user_id.name"),
                    "rejection": (rejection.comment or "") if rejection else "",
                    "changed_since_routed": bool(stale),
                }
                if approval
                else None
            ),
            "actions": {
                "approve": bool(
                    is_draft
                    and manager
                    and not stale
                    and tasks.filtered(lambda t: t.assigned_user_id.id == env.uid)
                ),
                "route": bool(manual and accountant and routable),
                "discard": bool(manual and accountant and (preparer or manager)),
            },
        }

    # ---------------------------------------------------------- statements

    @http.route("/p03/gl/statements", type="jsonrpc", auth="user", readonly=True)
    def gl_statements(self, report="trial_balance", date_from=None, date_to=None, **kw):
        _require_finance(request.env)
        env = request.env
        fy_from, fy_to = _fy_window()
        date_from = _parse_date(date_from, fy_from)
        date_to = _parse_date(date_to, fy_to)
        company = env.company
        if report == "trial_balance":
            data = compute_trial_balance(env, company, date_from, date_to)
        elif report == "pnl":
            data = compute_pnl(env, company, date_from, date_to)
        elif report == "balance_sheet":
            data = compute_balance_sheet(env, company, date_to)
        elif report == "cash_flow":
            data = compute_cash_flow(env, company, date_from, date_to)
        elif report == "consolidated":
            data = compute_consolidated(env, date_from, date_to, "pnl")
        else:
            return {"success": False, "error": "Unknown report: %s" % report}
        data["success"] = True
        return data

    # ------------------------------------------------------------ dimensions

    @http.route("/p03/gl/dimensions", type="jsonrpc", auth="user", readonly=True)
    def gl_dimensions(self, limit=80, **kw):
        _require_finance(request.env)
        env = request.env
        dims = (
            env["fix.journal.dimension"]
            .sudo()
            .search([("company_id", "in", env.companies.ids)], order="id desc", limit=limit)
        )
        rows = dims.mapped(
            lambda d: {
                "id": d.id,
                "move": d.move_line_id.move_id.name or "",
                "date": str(d.move_line_id.move_id.date),
                "account": "%s %s"
                % (d.move_line_id.account_id.code or "", d.move_line_id.account_id.name or ""),
                "ou": d.operating_unit_id.name or "",
                "branch": d.branch_id.name or "",
                "cost_centre": d.cost_centre or "",
                "business_line": d.business_line or "",
                "project": d.project_ref or "",
                "brand": d.brand or "",
                "channel": d.channel or "",
            }
        )
        counts = {}
        for field in (
            "branch_id",
            "cost_centre",
            "business_line",
            "brand",
            "channel",
            "project_ref",
        ):
            try:
                groups = (
                    env["fix.journal.dimension"]
                    .sudo()
                    ._read_group(
                        [(field, "!=", False), ("company_id", "in", env.companies.ids)],
                        [field],
                        ["__count"],
                    )
                )
                counts[field] = len(groups)
            except Exception:
                counts[field] = None
        return {"rows": rows, "count": len(rows), "distinct": counts}

    # ---------------------------------------------------------------- close

    @http.route("/p03/gl/close", type="jsonrpc", auth="user", readonly=True)
    def gl_close(self, close_id=None, **kw):
        """The close console. A finance role reads every close. A step owner
        outside finance (the stock manager owns the subledger cut-off, M19-5)
        reads only the steps they own, and no ledger figure, so the step they
        must complete can actually be found."""
        _require_internal(request.env)
        env = request.env
        finance = env.su or any(env.user.has_group(g) for g in FINANCE_READ_GROUPS)
        domain = [("company_id", "in", env.companies.ids)]
        if close_id:
            domain.append(("id", "=", int(close_id)))
        closes = env["fix.period.close"].sudo().search(domain, order="period_end desc")
        my_groups = env.user.sudo().all_group_ids
        if not finance:
            closes = closes.filtered(
                lambda c: c.line_ids.filtered(lambda s: s.owner_group_id in my_groups)
            )
            if not closes:
                raise AccessError(
                    "The close console needs a finance (accounting) role or a close step you own."
                )

        def steps(close):
            lines = close.line_ids
            if not finance:
                lines = lines.filtered(lambda s: s.owner_group_id in my_groups)
            return lines.mapped(
                lambda s: {
                    "id": s.id,
                    "sequence": s.sequence,
                    "name": s.name,
                    "owner": s.owner_role or "",
                    "target_day": s.target_day,
                    "blocking": s.blocking,
                    "state": s.state,
                    "evidence": s.evidence_ref or "",
                }
            )

        def row(close):
            out = {
                "id": close.id,
                "period_end": str(close.period_end),
                "state": close.state,
                "sla_status": close.sla_status,
                "target_completion": str(close.target_completion_date or ""),
                "closed_at": str(close.closed_at or ""),
                "duration_days": close.close_duration_days,
                "steps": steps(close),
            }
            if finance:
                pending_count, pending_value = close._fix_suspense_pending()
                out.update(
                    {
                        "suspense_opening": round(close.suspense_opening or 0.0, 2),
                        "suspense_closing": round(close.suspense_closing or 0.0, 2),
                        "suspense_reconciled": close.suspense_reconciled,
                        "cutover_ref": close.cutover_voucher_ref or "",
                        "cutover_entry": close.cutover_move_id.name or "",
                        # what the ready check reads; suspense_closing stays 0
                        # until a reconciliation has run
                        "suspense_pending_count": pending_count,
                        "suspense_pending_value": pending_value,
                    }
                )
            else:
                out.update(
                    {
                        "suspense_opening": None,
                        "suspense_closing": None,
                        "suspense_reconciled": None,
                        "cutover_ref": "",
                        "cutover_entry": "",
                        "suspense_pending_count": None,
                        "suspense_pending_value": None,
                    }
                )
            return out

        return {
            "closes": [row(close) for close in closes],
            "limited": not finance,
            "next_period_end": (
                str(env["fix.period.close"].sudo()._fix_next_period_end()) if finance else ""
            ),
        }

    @http.route("/p03/gl/close/action", type="jsonrpc", auth="user", readonly=False)
    def gl_close_action(
        self,
        close_id=None,
        action=None,
        step_id=None,
        evidence=None,
        state=None,
        period_end=None,
        entry=None,
        **kw,
    ):
        _require_internal(request.env)
        env = request.env
        try:
            # savepoint: a refused action (UserError) must leave nothing behind
            with env.cr.savepoint():
                return self._close_action(
                    env, close_id, action, step_id, evidence, state, period_end, entry
                )
        except UserError as exc:
            return {"success": False, "error": str(exc)}

    def _close_action(
        self, env, close_id, action, step_id, evidence, state, period_end=None, entry=None
    ):
        try:
            if action == "start_period":
                close = env["fix.period.close"].action_start_period(period_end)
                return {
                    "success": True,
                    "message": "Close for %s started with its 10 SOP steps" % close.period_end,
                    "close_id": close.id,
                }
            if action == "set_cutover":
                env["fix.period.close"].browse(int(close_id)).action_set_cutover_entry(entry)
                return {"success": True, "message": "Cutover entry set: %s" % entry}
            if action == "generate_steps":
                close = env["fix.period.close"].browse(int(close_id))
                close.action_generate_standard_steps()
                return {"success": True, "message": "10 SOP SP-020 close steps generated"}
            if action == "mark_done":
                step = env["fix.period.close.line"].browse(int(step_id))
                step.action_mark_done(evidence or "")
                return {
                    "success": True,
                    "message": "Step marked done on evidence: %s" % (evidence or ""),
                }
            if action == "set_state":
                step = env["fix.period.close.line"].browse(int(step_id))
                step.action_set_state(state)
                return {"success": True, "message": "Step state set to %s" % state}
            if action == "ready":
                env["fix.period.close"].browse(int(close_id)).action_ready()
                return {"success": True, "message": "Close is ready"}
            if action == "close":
                env["fix.period.close"].browse(int(close_id)).action_close()
                return {"success": True, "message": "Period closed"}
            if action == "reconcile_suspense":
                result = (
                    env["fix.period.close"]
                    .browse(int(close_id))
                    .action_reconcile_inventory_suspense()
                )
                return {
                    "success": True,
                    "message": "Suspense reconciliation: %s" % result.get("status"),
                    "result": result,
                }
            return {"success": False, "error": "Unknown close action"}
        except UserError as exc:
            return {"success": False, "error": str(exc)}
        except Exception as exc:
            return {"success": False, "error": _user_error(exc)}

    # -------------------------------------------------------------- periods

    @http.route("/p03/gl/periods", type="jsonrpc", auth="user", readonly=True)
    def gl_periods(self, **kw):
        _require_finance(request.env)
        env = request.env
        closes = (
            env["fix.period.close"]
            .sudo()
            .search([("company_id", "in", env.companies.ids)], order="period_end desc")
        )
        bridges = (
            env["fix.fiscal.period.bridge"].sudo().search([("period_close_id", "in", closes.ids)])
        )
        bridge_by_close = {b.period_close_id.id: b for b in bridges}
        company = env.company.sudo()
        rows = closes.mapped(
            lambda c: {
                "id": c.id,
                "period_end": str(c.period_end),
                "state": c.state,
                # read from the company lock date, never from a tick (M19-16)
                "locked": bool(c.is_locked),
                "locked_at": str(bridge_by_close[c.id].locked_at)
                if bridge_by_close.get(c.id)
                else "",
                "fiscal_year": bridge_by_close[c.id].fiscal_year_id.name or ""
                if bridge_by_close.get(c.id)
                else "",
                "step_progress": "%d/%d"
                % (len(c.line_ids.filtered(lambda s: s.state == "done")), len(c.line_ids)),
            }
        )
        return {
            "rows": rows,
            "company_lock_date": str(company.fiscalyear_lock_date or ""),
        }

    @http.route("/p03/gl/periods/lock", type="jsonrpc", auth="user", readonly=False)
    def gl_periods_lock(self, close_id=None, **kw):
        """Re-apply the company lock of a CLOSED, ended period. Accounting
        Administrator only, and as the caller: the bridge used to be created
        and locked as superuser for any internal user (A08 M19-6, P10)."""
        _require_internal(request.env)
        env = request.env
        try:
            with env.cr.savepoint():
                if not env.su and not env.user.has_group("account.group_account_manager"):
                    raise UserError("Locking the ledger needs the Accounting Administrator role.")
                close = env["fix.period.close"].browse(int(close_id)).exists()
                if not close:
                    raise UserError("Period close not found")
                bridge = env["fix.fiscal.period.bridge"].search(
                    [("period_close_id", "=", close.id)], limit=1
                )
                if not bridge:
                    bridge = env["fix.fiscal.period.bridge"].create(
                        {"company_id": close.company_id.id, "period_close_id": close.id}
                    )
                result = bridge.action_lock_journals()
            return {
                "success": True,
                "message": "Journals locked to %s" % result["lock_date"],
                "result": result,
            }
        except (UserError, AccessError) as exc:
            return {"success": False, "error": str(exc)}

    # ------------------------------------------------------------- suspense

    @http.route("/p03/gl/suspense", type="jsonrpc", auth="user", readonly=True)
    def gl_suspense(self, **kw):
        _require_finance(request.env)
        env = request.env
        company = env.company
        # W2 inventory suspense: entries still pending their GL cutover
        pending = (
            env["fix.inventory.valuation.suspense"]
            .sudo()
            .search([("status", "=", "pending_gl_cutover"), ("company_id", "=", company.id)])
        )
        by_code = {}
        for entry in pending:
            by_code.setdefault(entry.suspense_account_code, []).append(entry)
        inventory = [
            {
                "code": code,
                "count": len(entries),
                "valuation": round(sum(e.total_valuation for e in entries), 2),
            }
            for code, entries in sorted(by_code.items())
        ]
        # GL suspense/clearing statutory accounts that are mapped: live balances
        statutory = (
            env["fix.chart.account"]
            .sudo()
            .search(
                [
                    ("company_id", "=", company.id),
                    ("odoo_account_id", "!=", False),
                    "|",
                    ("name", "ilike", "suspense"),
                    ("name", "ilike", "clearing"),
                ]
            )
        )
        accounts = []
        for acc in statutory:
            groups = (
                env["account.move.line"]
                .sudo()
                ._read_group(
                    [
                        ("company_id", "=", company.id),
                        ("parent_state", "=", "posted"),
                        ("account_id", "=", acc.odoo_account_id.id),
                    ],
                    [],
                    ["balance:sum"],
                )
            )
            accounts.append(
                {
                    "code": acc.account_code,
                    "name": acc.name,
                    "odoo_code": acc.odoo_account_id.code,
                    "balance": round(sum(g[0] or 0.0 for g in groups), 2),
                }
            )
        return {
            "inventory_pending": inventory,
            "inventory_total": round(sum(p.total_valuation for p in pending), 2),
            "gl_suspense_accounts": accounts,
        }

    # ---------------------------------------------------------------- recon

    @http.route("/p03/gl/recon", type="jsonrpc", auth="user", readonly=True)
    def gl_recon(self, **kw):
        _require_finance(request.env)
        env = request.env
        company = env.company

        def gl_balance(odoo_account):
            if not odoo_account:
                return None
            groups = (
                env["account.move.line"]
                .sudo()
                ._read_group(
                    [
                        ("company_id", "=", company.id),
                        ("parent_state", "=", "posted"),
                        ("account_id", "=", odoo_account.id),
                    ],
                    [],
                    ["balance:sum"],
                )
            )
            return round(sum(g[0] or 0.0 for g in groups), 2)

        def control_for(subledger, name_like=None):
            domain = [
                ("company_id", "=", company.id),
                ("odoo_account_id", "!=", False),
                ("control_subledger", "=", subledger),
            ]
            if name_like:
                domain = [
                    ("company_id", "=", company.id),
                    ("odoo_account_id", "!=", False),
                    ("name", "ilike", name_like),
                ]
            return env["fix.chart.account"].sudo().search(domain, limit=1)

        rows = []

        def add_row(label, control, subledger_total):
            if not control:
                rows.append(
                    {
                        "label": label,
                        "control": None,
                        "subledger": None,
                        "variance": None,
                        "status": "not_configured",
                    }
                )
                return
            gl = gl_balance(control.odoo_account_id)
            variance = None if gl is None else round(gl - subledger_total, 2)
            rows.append(
                {
                    "label": label,
                    "account": "%s %s" % (control.account_code, control.name),
                    "odoo_code": control.odoo_account_id.code,
                    "control": gl,
                    "subledger": round(subledger_total, 2),
                    "variance": variance,
                    "status": (
                        "matched" if variance is not None and abs(variance) < 0.01 else "variance"
                    ),
                }
            )

        try:
            ar_open = sum(
                env["fix.ar.invoice"]
                .sudo()
                .search([("state", "in", ("draft", "issued")), ("company_id", "=", company.id)])
                .mapped("total_payable")
            )
            add_row("AR — Trade receivables", control_for("receivable"), ar_open)
        except Exception:
            _logger.debug("subledger recon row skipped: AR trade receivables", exc_info=True)
        try:
            ap_open = sum(
                env["fix.vendor.invoice"]
                .sudo()
                .search([("company_id", "=", company.id)])
                .mapped("total_payable")
            )
            add_row("AP — Trade payables", control_for("payable"), ap_open)
        except Exception:
            _logger.debug("subledger recon row skipped: AP trade payables", exc_info=True)
        try:
            vat_output = sum(
                env["fix.mushak.register"]
                .sudo()
                .search([("company_id", "=", company.id)])
                .mapped("vat_amount")
            )
            add_row(
                "VAT output — Mushak 6.3", control_for("tax", "VAT payable - output"), vat_output
            )
        except Exception:
            _logger.debug("subledger recon row skipped: VAT output", exc_info=True)
        try:
            commission = sum(
                env["fix.commission.ledger"]
                .sudo()
                .search([("state", "=", "accrued"), ("company_id", "=", company.id)])
                .mapped("commission_amount")
            )
            add_row(
                "Commission clearing — accrued",
                control_for(None, "seller payable") or control_for(None, "commission"),
                commission,
            )
        except Exception:
            _logger.debug("subledger recon row skipped: commission clearing", exc_info=True)
        return {"rows": rows, "company": company.name}

    # ---------------------------------------------------------------- audit

    @http.route("/p03/gl/audit", type="jsonrpc", auth="user", readonly=True)
    def gl_audit(self, limit=40, **kw):
        _require_finance(request.env)
        env = request.env
        logs = (
            env["fix.journal.posting.log"]
            .sudo()
            .search([("company_id", "in", env.companies.ids)], order="id desc", limit=limit)
        )
        events = (
            env["fix.event.outbox"]
            .sudo()
            .search(
                [("event_type", "in", ("journal.posted", "period.closed", "coa.loaded"))],
                order="id desc",
                limit=limit,
            )
        )
        return {
            "logs": logs.mapped(
                lambda lg: {
                    "id": lg.id,
                    "entry": lg.move_name or lg.move_id.name or "",
                    "source": lg.source,
                    "state": lg.state,
                    "amount": round(lg.amount or 0.0, 2),
                    "requested_by": lg.requested_by.name or "",
                    "posted_by": lg.posted_by.name or "",
                    "posted_at": str(lg.posted_at or ""),
                }
            ),
            "events": events.mapped(
                lambda e: {
                    "id": e.id,
                    "type": e.event_type,
                    "aggregate": "%s/%s" % (e.aggregate, e.aggregate_id),
                    "payload": e.payload,
                    "at": str(e.create_date or ""),
                }
            ),
            "note": "The posting log is immutable (FR-FIN-042): rows can be appended, never edited or deleted.",
        }

    # ------------------------------------------------------------ templates

    @http.route("/p03/gl/templates", type="jsonrpc", auth="user", readonly=True)
    def gl_templates(self, **kw):
        _require_finance(request.env)
        env = request.env
        templates = (
            env["fix.journal.template"]
            .sudo()
            .search([("company_id", "in", env.companies.ids)], order="name")
        )
        return {
            "rows": templates.mapped(
                lambda t: {
                    "id": t.id,
                    "name": t.name,
                    "journal": t.journal_id.name,
                    "schedule": t.schedule,
                    "next_run_date": str(t.next_run_date),
                    "auto_reverse": t.auto_reverse,
                    "state": t.state,
                    "run_count": t.run_count,
                    "last_entry": t.last_move_id.name or "",
                    "lines": len(t.line_ids),
                }
            )
        }

    @http.route("/p03/gl/templates/generate", type="jsonrpc", auth="user", readonly=False)
    def gl_templates_generate(self, template_id=None, **kw):
        _require_internal(request.env)
        template = request.env["fix.journal.template"].browse(int(template_id))
        try:
            with request.env.cr.savepoint():
                template.action_generate_entry()
            return {"success": True, "message": "Entry generated for %s" % template.name}
        except UserError as exc:
            return {"success": False, "error": str(exc)}

    @http.route("/p03/gl/templates/create", type="jsonrpc", auth="user", readonly=False)
    def gl_templates_create(
        self,
        name=None,
        schedule="monthly",
        next_run_date=None,
        auto_reverse=False,
        ref=None,
        lines=None,
        **kw,
    ):
        """Save the workspace JE editor's lines as a recurring template (the
        accrual framework's carrier — FR-FIN-013/016). The template starts
        DRAFT: activating it (and the first run) happens from its form or the
        cron, never silently."""
        _require_internal(request.env)
        env = request.env
        if not env.su and not env.user.has_group("account.group_account_user"):
            return {
                "success": False,
                "error": "Saving a recurring journal template needs the Accountant role.",
            }
        try:
            lines = lines or []
            if len(lines) < 2:
                return {"success": False, "error": "A template needs at least two lines"}
            journal = (
                env["account.journal"]
                .sudo()
                .search([("type", "=", "general"), ("company_id", "=", env.company.id)], limit=1)
            )
            if not journal:
                return {"success": False, "error": "No general journal configured"}
            line_vals = []
            for line in lines:
                line_vals.append(
                    (
                        0,
                        0,
                        {
                            "account_id": int(line.get("account_id")),
                            "label": line.get("label") or "",
                            "debit": round(float(line.get("debit") or 0.0), 2),
                            "credit": round(float(line.get("credit") or 0.0), 2),
                            "cost_centre": line.get("cost_centre") or False,
                            "business_line": line.get("business_line") or False,
                        },
                    )
                )
            with env.cr.savepoint():
                template = env["fix.journal.template"].create(
                    {
                        "name": name or ref or "Workspace accrual template",
                        "journal_id": journal.id,
                        "company_id": env.company.id,
                        "memo": ref or "",
                        "schedule": schedule
                        if schedule in ("monthly", "quarterly", "yearly")
                        else "monthly",
                        "next_run_date": _parse_date(next_run_date, datetime.date.today()),
                        "auto_reverse": bool(auto_reverse),
                        "line_ids": line_vals,
                    }
                )
            return {
                "success": True,
                "message": "Template '%s' saved as DRAFT — activate it from its form"
                % template.name,
                "template_id": template.id,
            }
        except (UserError, AccessError) as exc:
            return {"success": False, "error": str(exc)}
        except Exception as exc:
            return {"success": False, "error": _user_error(exc)}

    # ----------------------------------------------------------- allocations

    @http.route("/p03/gl/allocations", type="jsonrpc", auth="user", readonly=True)
    def gl_allocations(self, **kw):
        _require_finance(request.env)
        env = request.env
        rules = (
            env["fix.allocation.rule"]
            .sudo()
            .search([("company_id", "in", env.companies.ids)], order="name")
        )
        return {
            "rows": rules.mapped(
                lambda r: {
                    "id": r.id,
                    "name": r.name,
                    "source": "%s %s"
                    % (r.source_account_id.code or "", r.source_account_id.name or ""),
                    "state": r.state,
                    "run_count": r.run_count,
                    "last_run": str(r.last_run_date or ""),
                    "targets": r.line_ids.mapped(
                        lambda ln: {
                            "account": "%s %s"
                            % (ln.account_id.code or "", ln.account_id.name or ""),
                            "percent": ln.percent,
                            "branch": ln.branch_id.name or "",
                            "cost_centre": ln.cost_centre or "",
                        }
                    ),
                }
            )
        }

    @http.route("/p03/gl/allocations/run", type="jsonrpc", auth="user", readonly=False)
    def gl_allocations_run(self, rule_id=None, date_from=None, date_to=None, **kw):
        _require_internal(request.env)
        rule = request.env["fix.allocation.rule"].browse(int(rule_id))
        try:
            with request.env.cr.savepoint():
                rule.action_run(_parse_date(date_from, None), _parse_date(date_to, None))
            return {"success": True, "message": "Allocation posted for %s" % rule.name}
        except UserError as exc:
            return {"success": False, "error": str(exc)}

    # ------------------------------------------------- JE create / approve

    @http.route("/p03/gl/je/create", type="jsonrpc", auth="user", readonly=False)
    def gl_je_create(self, lines=None, date=None, ref=None, journal_id=None, **kw):
        """Create a journal entry from the workspace editor. The entry is
        created as a DRAFT and queued for review (FR-FIN-014/015): the maker
        never posts directly; a checker approves via /p03/gl/je/approve."""
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import create_journal_entry_draft

        _require_internal(request.env)
        env = request.env
        try:
            lines = lines or []
            if len(lines) < 2:
                return {"success": False, "error": "A journal entry needs at least two lines"}
            journal = (
                env["account.journal"].browse(int(journal_id))
                if journal_id
                else env["account.journal"]
                .sudo()
                .search([("type", "=", "general"), ("company_id", "=", env.company.id)], limit=1)
            )
            if not journal:
                return {"success": False, "error": "No general journal configured for the company"}
            line_vals = []
            dimension_by_line = {}
            for idx, line in enumerate(lines):
                account = env["account.account"].sudo().browse(int(line.get("account_id")))
                if not account.exists():
                    return {"success": False, "error": "Unknown account on line %d" % (idx + 1)}
                line_vals.append(
                    (
                        0,
                        0,
                        {
                            "account_id": account.id,
                            "name": line.get("label") or ref or "Manual entry",
                            "debit": round(float(line.get("debit") or 0.0), 2),
                            "credit": round(float(line.get("credit") or 0.0), 2),
                        },
                    )
                )
                dims = {
                    "branch_id": line.get("branch_id") or False,
                    "cost_centre": line.get("cost_centre") or False,
                    "business_line": line.get("business_line") or False,
                    "project_ref": line.get("project") or False,
                    "brand": line.get("brand") or False,
                    "channel": line.get("channel") or False,
                }
                if any(dims.values()):
                    dimension_by_line[idx] = dims
            debit = round(sum(li[2]["debit"] for li in line_vals), 2)
            credit = round(sum(li[2]["credit"] for li in line_vals), 2)
            if debit != credit:
                return {
                    "success": False,
                    "error": "Entry is not balanced: debit %.2f vs credit %.2f" % (debit, credit),
                }
            reason = (kw.get("reason") or ref or "").strip()
            if not reason:
                return {
                    "success": False,
                    "error": "State the reason / narrative of the manual journal (BRU-FIN-16).",
                }
            move_vals = {
                "journal_id": journal.id,
                "company_id": env.company.id,
                "date": _parse_date(date, datetime.date.today()),
                "ref": ref or "",
                "line_ids": line_vals,
            }
            # savepoint: a COA-rule refusal must not leave the created move
            # behind — the exception is caught for the JSON response, which
            # means the transaction would otherwise commit the half-entry.
            with env.cr.savepoint():
                move, log = create_journal_entry_draft(
                    env, move_vals, dimension_by_line, source="manual", reason=reason
                )
            return {
                "success": True,
                "message": "Draft %s created — routed for approval (SoD)" % (move.name or ""),
                "move_id": move.id,
                "log_id": log.id,
            }
        except (UserError, AccessError) as exc:
            return {"success": False, "error": str(exc)}
        except Exception as exc:
            return {"success": False, "error": _user_error(exc)}

    @http.route("/p03/gl/je/approve", type="jsonrpc", auth="user", readonly=False)
    def gl_je_approve(self, move_id=None, **kw):
        """Checker step: approve and post a drafted entry. SoD is enforced in
        Python (approver != requester, accounting manager group) — the UI
        cannot bypass it. Dimensions were attached when the draft was
        created."""
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import approve_journal_entry

        _require_internal(request.env)
        env = request.env
        try:
            move = env["account.move"].browse(int(move_id)).exists()
            if not move:
                return {"success": False, "error": "Journal entry not found"}
            with env.cr.savepoint():
                posted, _dims = approve_journal_entry(env, move)
            return {"success": True, "message": "%s posted" % (posted.name or "")}
        except (UserError, AccessError) as exc:
            return {"success": False, "error": str(exc)}

    @http.route("/p03/gl/je/route", type="jsonrpc", auth="user", readonly=False)
    def gl_je_route(self, move_id=None, reason=None, **kw):
        """Maker step for a draft with no live approval: never routed, rejected,
        voided, or edited since it was routed (M19-2, S2)."""
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import route_journal_entry

        _require_internal(request.env)
        env = request.env
        try:
            move = env["account.move"].browse(int(move_id)).exists()
            if not move:
                return {"success": False, "error": "Journal entry not found"}
            with env.cr.savepoint():
                approval = route_journal_entry(env, move, reason)
            return {
                "success": True,
                "message": "Routed for approval (%s)" % (approval.dofa_tier_required or ""),
            }
        except (UserError, AccessError, ValidationError) as exc:
            return {"success": False, "error": str(exc)}

    @http.route("/p03/gl/je/discard", type="jsonrpc", auth="user", readonly=False)
    def gl_je_discard(self, move_id=None, reason=None, **kw):
        """Cancel a draft that will not be posted; it stays on record."""
        from odoo.addons.cd_gl_ext.models.fix_gl_ext import discard_journal_entry

        _require_internal(request.env)
        env = request.env
        try:
            move = env["account.move"].browse(int(move_id)).exists()
            if not move:
                return {"success": False, "error": "Journal entry not found"}
            with env.cr.savepoint():
                discard_journal_entry(env, move, reason)
            return {"success": True, "message": "Draft discarded"}
        except (UserError, AccessError, ValidationError) as exc:
            return {"success": False, "error": str(exc)}
