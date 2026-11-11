# cd_gl_ext — the ledger's own guards (A08 remediation, B3, 4 Nov 2026).
#
# The M19 maker-checker used to live only inside its API: Odoo grants
# account.move create + post to Billing, so a Billing user posted a manual
# journal alone, an accountant posted BDT 50 M alone, a manager approved his
# own entry, and an approved entry was reset to draft, raised 1,000x and
# re-posted (A08 M19-2, probes J02-J05). 65 of 90 posted entries on fix_dev
# never touched the API. This file moves the control to the ledger:
#
#   account.move._post     a MANUAL journal entry (move_type 'entry' that no
#                          Odoo sub-ledger mechanism produced) posts only with
#                          the M19 token, i.e. through the API; control
#                          accounts refuse manual-style lines (COA-02,
#                          BRU-FIN-13); a manual entry dated in a closed
#                          period is refused, never silently re-dated.
#   account.move.button_draft
#                          a posted manual entry is never reset (BRU-FIN-12:
#                          reverse it); a superuser reset voids its approval.
#   account.move.write     `state` changes only inside _post / button_draft /
#                          button_cancel, never by a write of the field; the
#                          auto-post job posts no manual entry without the token.
#   fix.journal.approval   the routed (M63) DOFA approval of one manual entry.
#   fix.period.reopen      the only way into a closed period: a time-boxed lock
#                          exception for one named user, approved by an
#                          Accounting Administrator other than the closer.
#   account.lock_exception refused outside an approved reopen (M19-7).
#   res.company            the Global Lock Date moves back only through a
#                          reopen, and never forward past today (M19-6).
#   fix.chart.control.change
#                          the control flag of a statutory account changes
#                          only by an approved proposal (M19-8, FR-FIN-002).
import logging
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from .fix_gl_ext import (
    ACCOUNT_MANAGER,
    ACCOUNT_USER,
    MANUAL_POSTING_SOURCES,
    _chart_map_for_company,
    _log_posting,
    _move_snapshot,
    _publish_posted,
    has_fiscal_lock_token,
    has_m19_token,
    m19_context,
    m19_source,
    require_role,
)

_logger = logging.getLogger(__name__)

# Lock exceptions created by an approved reopen (or by Odoo recreating them
# when the company lock moves) carry this token.
LOCK_EXC_KEY = "fix_m19_lock_exception"
_LOCK_EXC_TOKEN = object()
# Control-flag changes applied by an approved proposal carry this token.
CONTROL_KEY = "fix_m19_control_change"
_CONTROL_TOKEN = object()
# Odoo's own status writes inside _post / button_draft / button_cancel carry
# this token; a write that changes `state` without it is refused.
STATE_KEY = "fix_m19_state_change"
_STATE_TOKEN = object()

# Manual-journal materiality bands (A08 S2 / P1-1). The spec gives no figure
# ("within the authority matrix", M19 §8 / AUT-FIN-14; decision B3), so the
# defaults are conservative: every manual journal needs at least a Tier 2
# (Finance Manager) approver; the CFO above BDT 500,000; the MD / Board above
# BDT 5,000,000. A fix.dofa.ladder ruling for fix.journal.approval overrides.
PARAM_JE_TIER2 = "cd_gl_ext.je_dofa_tier2_max"
PARAM_JE_TIER4 = "cd_gl_ext.je_dofa_tier4_max"
DEFAULT_JE_TIER2 = 500000.0
DEFAULT_JE_TIER4 = 5000000.0
# Reopen exceptions are time-boxed: at most this many days (FR-FIN-019).
PARAM_REOPEN_MAX_DAYS = "cd_gl_ext.reopen_max_days"
DEFAULT_REOPEN_MAX_DAYS = 3


def float_param(env, key, default):
    raw = env["ir.config_parameter"].sudo().get_param(key)
    if raw in (None, False, ""):
        return float(default)
    try:
        return float(raw)
    except (TypeError, ValueError):
        _logger.warning("%s is not a number (%r); using %s", key, raw, default)
        return float(default)


# ============================================================ account.move
class AccountMove(models.Model):
    _inherit = "account.move"

    fix_journal_approval_id = fields.Many2one(
        "fix.journal.approval",
        string="M19 Journal Approval",
        compute="_compute_fix_journal_approval",
    )

    def _compute_fix_journal_approval(self):
        Approval = self.env["fix.journal.approval"].sudo()
        by_move = {
            a.move_id.id: a for a in Approval.search([("move_id", "in", self.ids)]) if self.ids
        }
        for move in self:
            move.fix_journal_approval_id = by_move.get(move.id, Approval.browse()).id

    # ---- what counts as a manual journal ---------------------------------
    def _fix_is_mirror_of(self, original) -> bool:
        """True when this entry exactly reverses `original` (a posted entry):
        the same accounts, partners and currencies with the opposite balance."""
        if not original or original.state != "posted":
            return False

        def totals(move, sign):
            out = {}
            for line in move.line_ids:
                key = (line.account_id.id, line.partner_id.id or 0, line.currency_id.id or 0)
                bal, cur = out.get(key, (0.0, 0.0))
                out[key] = (
                    round(bal + sign * line.balance, 2),
                    round(cur + sign * line.amount_currency, 2),
                )
            return {k: v for k, v in out.items() if v != (0.0, 0.0)}

        return totals(self.sudo(), 1) == totals(original.sudo(), -1)

    def _fix_is_manual_entry(self) -> bool:
        """A journal entry no Odoo sub-ledger mechanism produced: not an
        invoice, not a payment's or statement line's entry, not a cash-basis
        or exchange-difference entry, not a stock valuation entry, not an
        exact reversal of a posted entry."""
        self.ensure_one()
        move = self.sudo()
        if move.move_type != "entry":
            return False
        if move.origin_payment_id and move.origin_payment_id.move_id == move:
            return False
        if move.statement_line_id and move.statement_line_id.move_id == move:
            return False
        if move.tax_cash_basis_rec_id or move.tax_cash_basis_origin_move_id:
            return False
        if "stock_move_id" in move._fields and move.stock_move_id:
            return False
        if "stock_valuation_layer_ids" in move._fields and move.stock_valuation_layer_ids:
            return False
        return not (move.reversed_entry_id and move._fix_is_mirror_of(move.reversed_entry_id))

    # ---- checks -------------------------------------------------------------
    def _fix_check_control_accounts(self, source=None):
        """COA-02 / BRU-FIN-13 at the line level: a manual-style entry never
        posts on a statutory control account."""
        if source and source not in MANUAL_POSTING_SOURCES:
            return
        for move in self:
            chart_map = _chart_map_for_company(self.env, move.company_id.id)
            for line in move.line_ids:
                chart = chart_map.get(line.account_id.id)
                if chart and chart.is_control_account:
                    raise UserError(
                        "Posting refused on %s (%s): it is the control account of the %s "
                        "sub-ledger; only that sub-ledger posts to it (COA-02, BRU-FIN-13)."
                        % (
                            line.account_id.display_name,
                            chart.account_code,
                            dict(chart._fields["control_subledger"].selection).get(
                                chart.control_subledger, chart.control_subledger or "owning"
                            ),
                        )
                    )

    def _fix_check_not_in_closed_period(self):
        """A manual entry is refused in a locked period (no silent re-date);
        a user holding an approved reopen exception may post there."""
        for move in self:
            if not move.date:
                continue
            violated = move._get_violated_lock_dates(move.date, move._affect_tax_report())
            if violated:
                lock = max(d for d, _f in violated)
                raise UserError(
                    "Period closed: %s is dated %s, on or before the lock date %s. A closed "
                    "period takes no manual posting without an approved reopen (BRU-FIN-06)."
                    % (move.display_name, move.date, lock)
                )

    # ---- the status changes only through its methods -----------------------
    def _fix_state_ctx(self):
        return self.with_context(**{STATE_KEY: _STATE_TOKEN})

    def write(self, vals):
        # `state` set by a plain write skips _post altogether: no maker-checker,
        # no number, no lock check, and a posted entry goes back to draft to be
        # edited. (Odoo itself refuses an entry created posted.) Superuser code
        # is trusted, as elsewhere in this file.
        if (
            "state" in vals
            and not self.env.su
            and self.env.context.get(STATE_KEY) is not _STATE_TOKEN
            and any(move.state != vals["state"] for move in self)
        ):
            raise UserError(
                "The status of a journal entry changes only by posting, resetting or "
                "cancelling it, never by editing the status itself (BRU-FIN-11, BRU-FIN-12)."
            )
        return super().write(vals)

    def _post(self, soft=True):
        token = has_m19_token(self.env)
        source = m19_source(self.env)
        manual = self.filtered(lambda m: m._fix_is_manual_entry())
        # Superuser code that posts an entry directly is trusted, except on the
        # auto-post path: the nightly job runs as the superuser and posts
        # whatever draft a user flagged, so there only the M19 token admits.
        unapproved = manual if not self.env.su else manual.filtered(lambda m: m.auto_post != "no")
        if unapproved and not token:
            raise UserError(
                "Manual journal entries post only through the M19 maker-checker: draft the "
                "entry for review and an Accounting Administrator other than you approves it "
                "(BRU-FIN-11, FR-FIN-014). Entries: %s"
                % ", ".join(str(m.display_name or m.ref or m.id) for m in unapproved)
            )
        manual_style = manual if (not token or source in MANUAL_POSTING_SOURCES) else self.browse()
        if not self.env.su:
            # Superuser code (sub-ledger engines, seeds, crons) is trusted, as
            # the field guards trust it; the API itself still applies COA-02
            # to manual-style sources whoever calls it.
            manual_style._fix_check_control_accounts()
            manual_style._fix_check_not_in_closed_period()
        if token:
            # An approval covers what it was given for: the entry posted is the
            # entry that was approved.
            for move in self:
                approval = move.sudo().fix_journal_approval_id
                if (
                    approval
                    and approval.lines_snapshot
                    and approval.lines_snapshot != _move_snapshot(move)
                ):
                    raise UserError(
                        "Entry %s changed after its approval was requested; the approval no "
                        "longer covers it. Draft it again." % move.display_name
                    )
        # the token stays inside: what is returned carries the caller's context
        return super(AccountMove, self._fix_state_ctx())._post(soft).with_env(self.env)

    def button_draft(self):
        if not self.env.su:
            protected = self.filtered(lambda m: m.state == "posted" and m._fix_is_manual_entry())
            if protected:
                raise UserError(
                    "A posted journal entry is never modified (BRU-FIN-12): reverse %s instead."
                    % ", ".join(protected.mapped("name"))
                )
        result = super(AccountMove, self._fix_state_ctx()).button_draft()
        approvals = (
            self.env["fix.journal.approval"]
            .sudo()
            .search([("move_id", "in", self.ids), ("state", "in", ("approved", "posted"))])
        )
        for approval in approvals:
            approval._fix_void("the entry was reset to draft; its approval no longer covers it")
        return result

    def button_cancel(self):
        return super(AccountMove, self._fix_state_ctx()).button_cancel()

    # ---- the documented M19 API for sub-ledgers (B4/B5 contract) -----------
    @api.model
    def _fix_post_via_m19(
        self, move_vals, source, source_ref=None, dimension_by_line=None, template=None
    ):
        """Create and post one entry through the M19 API (posting log, COA
        rules, dimensions, journal.posted). Returns the posted move."""
        from .fix_gl_ext import post_with_dimensions

        move, _dims = post_with_dimensions(
            self.env,
            move_vals,
            dimension_by_line or {},
            source=source,
            template=template,
            source_ref=source_ref,
        )
        return move

    def _fix_m19_post(self, source, source_ref=None, dimension_by_line=None):
        """Post these DRAFT entries through the M19 API. Returns self."""
        from .fix_gl_ext import post_existing_moves

        return post_existing_moves(
            self.env,
            self,
            source=source,
            source_ref=source_ref,
            dimension_by_line=dimension_by_line,
        )


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def _create_exchange_difference_moves(self, exchange_diff_values_list):
        # Odoo's own exchange-difference entries (raised by a reconciliation)
        # are sub-ledger postings of the reconciliation, not manual journals.
        return super(
            AccountMoveLine, self.with_context(**m19_context("exchange"))
        )._create_exchange_difference_moves(exchange_diff_values_list)


class AccountPartialReconcile(models.Model):
    _inherit = "account.partial.reconcile"

    def _create_tax_cash_basis_moves(self):
        return super(
            AccountPartialReconcile, self.with_context(**m19_context("exchange"))
        )._create_tax_cash_basis_moves()


# ==================================================== lock exceptions / lock
class AccountLockException(models.Model):
    _inherit = "account.lock_exception"

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su and self.env.context.get(LOCK_EXC_KEY) is not _LOCK_EXC_TOKEN:
            raise UserError(
                "A closed period is reopened only through an approved period reopen "
                "(fix.period.reopen): one named user, an end date, and an Accounting "
                "Administrator other than the closer (BRU-FIN-06)."
            )
        for vals in vals_list:
            if self.env.context.get(LOCK_EXC_KEY) is _LOCK_EXC_TOKEN and not self.env.context.get(  # noqa: SIM102
                "fix_m19_recreate"
            ):
                if not vals.get("user_id") or not vals.get("end_datetime"):
                    raise UserError("A reopen exception names one user and an end date.")
        return super().create(vals_list)

    def _recreate(self):
        # Odoo re-issues active exceptions when a lock date moves; those were
        # approved already.
        return super(
            AccountLockException,
            self.with_context(**{LOCK_EXC_KEY: _LOCK_EXC_TOKEN, "fix_m19_recreate": True}),
        )._recreate()


class ResCompany(models.Model):
    _inherit = "res.company"

    def write(self, vals):
        if (
            "fiscalyear_lock_date" in vals
            and not self.env.su
            and not has_fiscal_lock_token(self.env)
        ):
            new = (
                fields.Date.to_date(vals["fiscalyear_lock_date"])
                if vals["fiscalyear_lock_date"]
                else None
            )
            today = fields.Date.context_today(self)
            for company in self:
                current = company.fiscalyear_lock_date
                if current and (not new or new < current):
                    raise UserError(
                        "The Global Lock Date of %s moves back only through an approved period "
                        "reopen (BRU-FIN-06)." % company.name
                    )
                if new and new >= today:
                    raise UserError(
                        "The Global Lock Date cannot be set to %s: a period is locked after it "
                        "ends (today is %s)." % (new, today)
                    )
        return super().write(vals)


# ========================================================= journal approval
JE_APPROVAL_STATES = [
    ("draft", "Draft"),
    ("pending", "Awaiting Approval"),
    ("posted", "Approved & Posted"),
    ("rejected", "Rejected"),
    ("voided", "Voided"),
]


class FixJournalApproval(models.Model):
    """The routed approval of one manual journal entry (A08 S2, P1-1).

    The preparer drafts the entry; this record routes it through M63 to the
    DOFA tier of its amount, restricted to Accounting Administrators, minus
    the preparer and anyone who edited the entry. The approver's decision
    posts the entry with the M19 token. The snapshot of date, journal and
    lines is what the approval covers: a changed entry is refused."""

    _name = "fix.journal.approval"
    _description = "Manual Journal Approval"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.dofa.mixin"]
    _order = "id desc"
    _approval_domain = "journal_entry"
    _approval_routed = True
    _approval_apply_method = "action_dofa_approve"
    _move_unique = models.Constraint("UNIQUE (move_id)", "One approval per journal entry")

    name = fields.Char(compute="_compute_name", store=True)
    move_id = fields.Many2one(
        "account.move", string="Journal Entry", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    currency_id = fields.Many2one(related="company_id.currency_id")
    amount = fields.Monetary(
        string="Entry Amount",
        currency_field="currency_id",
        compute="_compute_amount",
        store=True,
        help="Total debits in the company currency — the amount the DOFA tier is derived from.",
    )
    source = fields.Char(default="manual", readonly=True)
    reason = fields.Char(string="Reason / Narrative")
    state = fields.Selection(JE_APPROVAL_STATES, default="draft", required=True, tracking=True)
    lines_snapshot = fields.Text(readonly=True, copy=False)
    log_id = fields.Many2one("fix.journal.posting.log", readonly=True, ondelete="set null")
    requested_by_id = fields.Many2one("res.users", string="Prepared By", readonly=True)
    posted_by_id = fields.Many2one("res.users", string="Approved & Posted By", readonly=True)
    posted_at = fields.Datetime(readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "lines_snapshot",
            "log_id",
            "requested_by_id",
            "posted_by_id",
            "posted_at",
            "move_id",
            "company_id",
            "source",
        }

    @api.depends("move_id.name", "move_id.ref")
    def _compute_name(self):
        for rec in self:
            move = rec.move_id.sudo()
            rec.name = "JE approval %s" % (
                move.name if move.name and move.name != "/" else move.ref or move.id
            )

    @api.depends("move_id.line_ids.debit")
    def _compute_amount(self):
        for rec in self:
            rec.amount = round(sum(rec.move_id.sudo().line_ids.mapped("debit")), 2)

    @api.depends("amount")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    # ---- DOFA ---------------------------------------------------------------
    def _dofa_amount(self) -> float:
        self.ensure_one()
        return round(sum(self.move_id.sudo().line_ids.mapped("debit")), 2)

    def _dofa_thresholds(self):
        return [
            (float_param(self.env, PARAM_JE_TIER2, DEFAULT_JE_TIER2), "tier_2"),
            (float_param(self.env, PARAM_JE_TIER4, DEFAULT_JE_TIER4), "tier_4"),
            (float("inf"), "tier_5"),
        ]

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "manual journal %s of BDT %.2f" % (
            self.move_id.sudo().display_name,
            self._dofa_amount(),
        )

    def _fix_conflicted_users(self):
        """Preparer, requester, and whoever created or edited the entry."""
        self.ensure_one()
        rec = self.sudo()
        users = (
            rec.create_uid
            | rec.requested_by_id
            | rec.move_id.create_uid
            | rec.move_id.line_ids.mapped("create_uid")
            | rec.move_id.line_ids.mapped("write_uid")
            | rec.approval_request_id.requested_by_id
        )
        if rec.id:
            # a re-routed entry: whoever requested it in an earlier round too
            users |= (
                self.env["fix.approval.request"]
                .sudo()
                .search([("res_model", "=", self._name), ("res_id", "=", rec.id)])
                .mapped("requested_by_id")
            )
        return users.filtered(lambda u: not u._is_superuser())

    def _approval_excluded(self):
        return (super()._approval_excluded() | self._fix_conflicted_users()).sudo()

    def _approval_holders(self, group):
        users = super()._approval_holders(group)
        return users.filtered(lambda u: u.has_group(ACCOUNT_MANAGER))

    # ---- lifecycle ----------------------------------------------------------
    def action_request_approval(self, justification=None):
        for rec in self:
            if rec.state not in ("draft", "rejected", "voided"):
                raise UserError("%s is already %s." % (rec.display_name, rec.state))
            if rec.move_id.state != "draft":
                raise UserError("Only a draft entry is routed for approval.")
            rec._guarded().write(
                {
                    "state": "pending",
                    "lines_snapshot": _move_snapshot(rec.move_id),
                    "requested_by_id": self.env.uid,
                }
            )
        return super().action_request_approval(justification=justification)

    def _fix_assert_decider(self):
        self.ensure_one()
        if self.env.su:
            return
        if not self.env.user.has_group(ACCOUNT_MANAGER):
            raise AccessError("Only an Accounting Administrator approves journal entries.")
        task = self._approval_task()
        deciders = self.env.user | task.on_behalf_of_id
        clash = deciders & self._fix_conflicted_users()
        if clash:
            raise UserError(
                "Segregation of duties (BRU-FIN-11): %s prepared or edited %s and cannot "
                "approve it, at any value."
                % (", ".join(clash.mapped("name")), self.move_id.display_name)
            )

    def action_dofa_approve(self):
        """The engine's apply method (routed: only from the approver's inbox
        task). Checks, stamps, then posts the entry."""
        self._approval_assert_routed()
        for rec in self:
            rec._fix_assert_decider()
            if rec.state != "pending":
                raise UserError("%s is not awaiting approval." % rec.display_name)
            if rec.lines_snapshot != _move_snapshot(rec.move_id):
                raise UserError(
                    "Entry %s changed after it was routed for approval; the preparer must route it "
                    "again." % rec.move_id.display_name
                )
        result = super().action_dofa_approve()
        for rec in self:
            rec._fix_post_approved()
        return result

    def _fix_post_approved(self, system=False):
        """Post the approved entry with the M19 token and close the log row."""
        for rec in self:
            move = rec.move_id
            if move.state != "draft":
                raise UserError("%s is not a draft entry." % move.display_name)
            if system and rec.state == "draft":
                rec._guarded().write({"lines_snapshot": _move_snapshot(move)})
            move.with_context(**m19_context(rec.source or "manual"))._post(soft=False)
            rec._guarded().write(
                {
                    "state": "posted",
                    "posted_by_id": self.env.uid,
                    "posted_at": fields.Datetime.now(),
                }
            )
            if rec.log_id:
                rec.log_id.with_context(force_edit=True).sudo().write(
                    {
                        "state": "posted",
                        "posted_by": self.env.uid,
                        "posted_at": fields.Datetime.now(),
                        "move_name": move.name or rec.log_id.move_name,
                        "amount": move.amount_total,
                    }
                )
            else:
                _log_posting(self.env, move, rec.source or "manual", rec.requested_by_id.id, None)
            _publish_posted(self.env, move, rec.source or "manual")
            rec.message_post(
                body="Journal entry %s approved and posted by %s." % (move.name, self.env.user.name)
            )

    def _approval_on_rejected(self, comment):
        for rec in self.sudo():
            rec._guarded().write({"state": "rejected"})
        return super()._approval_on_rejected(comment)

    def _fix_void(self, reason):
        for rec in self.sudo():
            if rec.dofa_approved or rec.approval_state in ("pending", "approved"):
                rec._dofa_void_approval(reason)
            rec._guarded().write({"state": "voided", "lines_snapshot": False})
            rec.message_post(body="Approval voided: %s" % reason)


# ============================================================ period reopen
REOPEN_STATES = [
    ("draft", "Draft"),
    ("pending", "Awaiting Approval"),
    ("approved", "Approved (exception active)"),
    ("rejected", "Rejected"),
    ("revoked", "Revoked"),
]


class FixPeriodReopen(models.Model):
    """A governed, time-boxed reopen of a closed period (BRU-FIN-06,
    FR-FIN-019, AUT-FIN-13): one named user may post into the period until
    the end date, through an Odoo lock exception created only when an
    Accounting Administrator other than the closer, the requester and the
    beneficiary approves it (routed through M63)."""

    _name = "fix.period.reopen"
    _description = "Period Reopen Request"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.approvable.mixin"]
    _order = "id desc"
    _approval_domain = "period_reopen"
    _approval_group = ACCOUNT_MANAGER
    _approval_routed = True
    _approval_apply_method = "action_approve"

    close_id = fields.Many2one("fix.period.close", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="close_id.company_id", store=True, index=True)
    period_end = fields.Date(related="close_id.period_end", store=True)
    user_id = fields.Many2one(
        "res.users", string="Posting User", required=True, help="The one user the exception admits."
    )
    reason = fields.Text(required=True)
    end_datetime = fields.Datetime(string="Exception Ends", required=True)
    state = fields.Selection(REOPEN_STATES, default="draft", required=True, tracking=True)
    requested_by_id = fields.Many2one("res.users", readonly=True)
    approved_by_id = fields.Many2one("res.users", readonly=True)
    approved_at = fields.Datetime(readonly=True)
    lock_exception_id = fields.Many2one(
        "account.lock_exception", readonly=True, ondelete="set null"
    )

    _TERMS = ("close_id", "user_id", "end_datetime", "reason")

    @api.depends("period_end", "user_id")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = "Reopen %s for %s" % (
                rec.period_end or "",
                rec.user_id.sudo().name or "",
            )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "requested_by_id",
            "approved_by_id",
            "approved_at",
            "lock_exception_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(rec.state != "draft" for rec in self):
            locked |= set(self._TERMS)
        return locked

    def write(self, vals):
        if (
            set(self._TERMS) & set(vals)
            and not self._fix_guard_open()
            and any(rec.state != "draft" for rec in self)
        ):
            raise UserError("A submitted reopen request is frozen; raise a new one.")
        return super().write(vals)

    def _approval_pinned_fields(self) -> set:
        return super()._approval_pinned_fields() | {"close_id", "user_id", "end_datetime", "reason"}

    def _fix_conflicted_users(self):
        self.ensure_one()
        rec = self.sudo()
        return (
            rec.create_uid
            | rec.requested_by_id
            | rec.user_id
            | rec.close_id.closed_by_id
            | rec.approval_request_id.requested_by_id
        )

    def _approval_excluded(self):
        return (super()._approval_excluded() | self._fix_conflicted_users()).sudo()

    @api.constrains("end_datetime")
    def _check_end(self):
        max_days = float_param(self.env, PARAM_REOPEN_MAX_DAYS, DEFAULT_REOPEN_MAX_DAYS)
        for rec in self:
            if rec.state != "draft":
                continue
            if rec.end_datetime <= fields.Datetime.now():
                raise ValidationError("A reopen ends in the future.")
            if rec.end_datetime > fields.Datetime.now() + timedelta(days=max_days):
                raise ValidationError(
                    "A reopen lasts at most %d day(s) (%s)." % (max_days, PARAM_REOPEN_MAX_DAYS)
                )

    def action_submit(self):
        require_role(self.env, ACCOUNT_USER, "Requesting a period reopen")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft reopen request is submitted.")
            if rec.close_id.state != "closed":
                raise UserError("Only a closed period is reopened.")
            if not (rec.reason or "").strip():
                raise UserError("A reopen states its reason.")
            rec._guarded().write({"state": "pending", "requested_by_id": self.env.uid})
            rec.action_request_approval(justification=rec.reason)
        return True

    def action_approve(self):
        self._approval_assert_routed()
        for rec in self:
            if not self.env.su:
                if not self.env.user.has_group(ACCOUNT_MANAGER):
                    raise AccessError("A reopen is approved by an Accounting Administrator.")
                task = rec._approval_task()
                clash = (self.env.user | task.on_behalf_of_id) & rec._fix_conflicted_users()
                if clash:
                    raise UserError(
                        "Segregation of duties: %s closed the period, requested the reopen or "
                        "would post under it, and cannot approve it."
                        % ", ".join(clash.mapped("name"))
                    )
            if rec.state != "pending":
                raise UserError("The reopen request is not awaiting approval.")
            if rec.end_datetime <= fields.Datetime.now():
                raise UserError("The requested reopen window has already ended.")
            close = rec.close_id
            period_start = close.period_end.replace(day=1)
            exception = (
                self.env["account.lock_exception"]
                .sudo()
                .with_context(**{LOCK_EXC_KEY: _LOCK_EXC_TOKEN})
                .create(
                    {
                        "company_id": close.company_id.id,
                        "user_id": rec.user_id.id,
                        "end_datetime": rec.end_datetime,
                        "reason": "Reopen %s of %s: %s" % (rec.id, close.period_end, rec.reason),
                        "fiscalyear_lock_date": period_start - timedelta(days=1),
                    }
                )
            )
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": self.env.uid,
                    "approved_at": fields.Datetime.now(),
                    "lock_exception_id": exception.id,
                }
            )
            close.message_post(
                body="Period %s reopened for %s until %s by %s (requested by %s): %s"
                % (
                    close.period_end,
                    rec.user_id.name,
                    rec.end_datetime,
                    self.env.user.name,
                    rec.requested_by_id.name,
                    rec.reason,
                )
            )
        return True

    def _approval_on_rejected(self, comment):
        for rec in self.sudo():
            rec._guarded().write({"state": "rejected"})
        return super()._approval_on_rejected(comment)

    def action_revoke(self):
        require_role(self.env, ACCOUNT_MANAGER, "Revoking a period reopen")
        for rec in self:
            if rec.state != "approved":
                raise UserError("Only an approved reopen is revoked.")
            if rec.lock_exception_id:
                rec.lock_exception_id.sudo().action_revoke()
            rec._guarded().write({"state": "revoked"})
        return True


# ===================================================== control-flag change
class FixChartAccount(models.Model):
    _inherit = "fix.chart.account"

    def write(self, vals):
        flags = {"is_control_account", "control_subledger"} & set(vals)
        if flags and not self.env.su and self.env.context.get(CONTROL_KEY) is not _CONTROL_TOKEN:
            for acc in self:
                for name in flags:
                    new = vals[name] or False
                    if (acc[name] or False) != new:
                        raise UserError(
                            "The control flag of %s changes only through an approved control "
                            "change (fix.chart.control.change, FR-FIN-002)." % acc.account_code
                        )
        return super().write(vals)


class FixChartControlChange(models.Model):
    """A proposal to change a statutory account's control-account flag,
    applied when an Accounting Administrator other than the proposer approves
    it (routed through M63)."""

    _name = "fix.chart.control.change"
    _description = "Control Account Flag Change"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.approvable.mixin"]
    _order = "id desc"
    _approval_domain = "chart_control_change"
    _approval_group = ACCOUNT_MANAGER
    _approval_routed = True
    _approval_apply_method = "action_apply"

    account_id = fields.Many2one("fix.chart.account", required=True, ondelete="cascade")
    company_id = fields.Many2one(related="account_id.company_id", store=True)
    new_is_control = fields.Boolean(string="Control Account")
    new_subledger = fields.Selection(
        [
            ("receivable", "Accounts Receivable"),
            ("payable", "Accounts Payable"),
            ("stock", "Inventory Stock"),
            ("fixed_asset", "Fixed Assets"),
            ("tax", "Statutory Tax & VAT"),
        ],
        string="Control Subledger",
    )
    reason = fields.Text(required=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("pending", "Pending"),
            ("applied", "Applied"),
            ("rejected", "Rejected"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    requested_by_id = fields.Many2one("res.users", readonly=True)
    applied_by_id = fields.Many2one("res.users", readonly=True)

    _TERMS = ("account_id", "new_is_control", "new_subledger", "reason")

    @api.depends("account_id")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = "Control change %s" % (rec.account_id.sudo().account_code or "")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "requested_by_id", "applied_by_id"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if any(rec.state != "draft" for rec in self):
            locked |= set(self._TERMS)
        return locked

    def write(self, vals):
        if (
            set(self._TERMS) & set(vals)
            and not self._fix_guard_open()
            and any(rec.state != "draft" for rec in self)
        ):
            raise UserError("A submitted control change is frozen; propose a new one.")
        return super().write(vals)

    def _approval_pinned_fields(self) -> set:
        return super()._approval_pinned_fields() | {"account_id", "new_is_control", "new_subledger"}

    def _approval_excluded(self):
        return (super()._approval_excluded() | self.sudo().requested_by_id).sudo()

    def action_submit(self):
        require_role(self.env, ACCOUNT_USER, "Proposing a control-account change")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft proposal is submitted.")
            rec._guarded().write({"state": "pending", "requested_by_id": self.env.uid})
            rec.action_request_approval(justification=rec.reason)
        return True

    def action_apply(self):
        self._approval_assert_routed()
        for rec in self:
            if not self.env.su:
                if not self.env.user.has_group(ACCOUNT_MANAGER):
                    raise AccessError(
                        "A control-account change is approved by an Accounting Administrator."
                    )
                if self.env.user in (rec.create_uid | rec.requested_by_id):
                    raise UserError(
                        "Segregation of duties: the proposer cannot approve the change."
                    )
            if rec.state != "pending":
                raise UserError("The proposal is not awaiting approval.")
            rec.account_id.sudo().with_context(**{CONTROL_KEY: _CONTROL_TOKEN}).write(
                {
                    "is_control_account": rec.new_is_control,
                    "control_subledger": rec.new_subledger if rec.new_is_control else False,
                }
            )
            rec._guarded().write({"state": "applied", "applied_by_id": self.env.uid})
        return True

    def _approval_on_rejected(self, comment):
        for rec in self.sudo():
            rec._guarded().write({"state": "rejected"})
        return super()._approval_on_rejected(comment)


def control_change_context():
    """For the statutory chart loader's governed master-file reload."""
    return {CONTROL_KEY: _CONTROL_TOKEN}
