# M08 contract lifecycle operations: amendments, renewals and terminations on
# top of fix.contract / fix.contract.entitlement / fix.contract.pm.visit.
#
# A04 build (2026-11-04) C2-C8: all three were data shells. An amendment was
# 'approved' and 'applied' by typing its state and never changed the contract
# (a live +150k amendment sat unapplied); a renewal 'won' created nothing; a
# termination's DOFA tier was a free choice (BDT 5M stored as Tier 1), its
# approval had no group or SoD, and the penalty was raised 0 -> 5M after
# approval and still executed. Each now has a real lifecycle: states move by
# actions, the money is pinned by the DOFA mixin, and the approvals are
# routed through the M63 inbox.
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish

from .fix_contract import (
    CONTRACT_VALUE_DOFA_THRESHOLDS,
    IN_FORCE,
    MANAGER,
    OFFICER,
    require_role,
)

# A04 build (2026-11-04): BUSINESS DEFAULT TO CONFIRM (§7). The termination
# ladder the module already stated on its own Selection: Commercial Director
# (estate Tier 3) below BDT 500k, CFO (Tier 4) below 2M, the MD / Board
# (Tier 5) from 2M. The amount is what the termination gives up: the
# unexpired contract value plus the penalty or break fee.
TERMINATION_DOFA_THRESHOLDS = [
    (500000.0, "tier_3"),
    (2000000.0, "tier_4"),
    (float("inf"), "tier_5"),
]


class FixApprovalMatrixContract(models.Model):
    """M08 decision domains on the DoA register (A04 build, 2026-11-04)."""

    _inherit = "fix.approval.matrix"

    decision_domain = fields.Selection(
        selection_add=[
            ("contract_value", "Contract Value Approval"),
            ("contract_amendment", "Contract Amendment"),
            ("contract_termination", "Contract Suspension / Termination"),
        ],
        ondelete=dict.fromkeys(
            ("contract_value", "contract_amendment", "contract_termination"), "cascade"
        ),
    )


def _states_label(model, state):
    return dict(model._fields["state"].selection).get(state, state)


AMENDMENT_TERM_FIELDS = frozenset(
    {"contract_id", "kind", "delta_value", "new_date_end", "effective_from", "currency_id"}
)


class FixContractAmendment(models.Model):
    _name = "fix.contract.amendment"
    _description = "Contract Amendment"
    _inherit = ["mail.thread", "fix.dofa.mixin"]
    _order = "effective_from desc, id desc"

    # Routed through M63: a priced change under the contract-value DOFA
    # ladder on the size of the change; a change with no money (scope) is
    # decided by a Contract Manager.
    _approval_domain = "contract_amendment"
    _approval_apply_method = "action_dofa_approve"
    _approval_group = MANAGER
    _approval_routed = True

    name = fields.Char(required=True)
    contract_id = fields.Many2one("fix.contract", required=True, ondelete="cascade", index=True)
    kind = fields.Selection(
        [("pricing", "Pricing change"), ("scope", "Scope change"), ("term", "Term change")],
        required=True,
        default="scope",
    )
    delta_value = fields.Monetary(currency_field="currency_id")
    new_date_end = fields.Date(
        string="New Term End", help="Term change: the contract's new end date."
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    effective_from = fields.Date(required=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Awaiting Approval"),
            ("approved", "Approved"),
            ("applied", "Applied"),
            ("rejected", "Rejected"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="draft",
        readonly=True,
        tracking=True,
    )
    note = fields.Char()
    # The version trail: what the contract read before and after.
    version_no = fields.Integer(string="Contract Version", readonly=True, copy=False)
    value_before = fields.Monetary(currency_field="currency_id", readonly=True, copy=False)
    value_after = fields.Monetary(currency_field="currency_id", readonly=True, copy=False)
    date_end_before = fields.Date(readonly=True, copy=False)
    applied_by = fields.Many2one("res.users", readonly=True, copy=False)
    applied_on = fields.Datetime(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "version_no",
            "value_before",
            "value_after",
            "date_end_before",
            "applied_by",
            "applied_on",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if len(self) == 1 and self.state != "draft":
            locked |= AMENDMENT_TERM_FIELDS | {"name", "note"}
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open():
            frozen = set(vals) & (AMENDMENT_TERM_FIELDS | {"name", "note"})
            for rec in self.filtered(lambda r: r.state != "draft"):
                if any(rec._fix_guard_differs(n, vals[n], rec[n]) for n in frozen):
                    raise UserError(
                        "Amendment %s is %s: its terms are fixed. Cancel it and raise a new one."
                        % (rec.name, _states_label(rec, rec.state))
                    )
        return super().write(vals)

    # ---- DOFA ---------------------------------------------------------------
    def _dofa_amount(self) -> float:
        """The value the amendment moves: the price change, or the value of
        the term added or removed. A scope change carries no amount."""
        self.ensure_one()
        if self.kind == "pricing":
            return abs(self.delta_value or 0.0)
        if self.kind == "term" and self.new_date_end and self.contract_id.date_end:
            days = abs((self.new_date_end - self.contract_id.date_end).days)
            return round((self.contract_id.annual_value or 0.0) * days / 365.0, 2)
        return 0.0

    def _dofa_thresholds(self):
        return CONTRACT_VALUE_DOFA_THRESHOLDS

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "BDT %.2f (%s amendment of %s)" % (
            self._dofa_amount(),
            self.kind,
            self.contract_id.code,
        )

    @api.depends("kind", "delta_value", "new_date_end", "contract_id.date_end")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    def _approval_needed(self) -> bool:
        # every amendment is decided: priced ones by DOFA, scope by a manager
        return True

    def _approval_tier(self):
        tier = self._dofa_current_tier()
        return tier if tier != "tier_0" else False

    # ---- lifecycle ------------------------------------------------------------
    def _amendment_require_state(self, allowed, what):
        for rec in self:
            if rec.state not in allowed:
                raise UserError(
                    "Amendment %s cannot %s: it is %s."
                    % (rec.name, what, _states_label(rec, rec.state))
                )

    def _amendment_validate(self):
        for rec in self:
            contract = rec.contract_id
            if contract.state not in IN_FORCE:
                raise UserError(
                    "Contract %s is not in force: a draft contract is edited, a closed "
                    "one is not amended." % contract.code
                )
            if contract.billed_through_date and rec.effective_from <= contract.billed_through_date:
                raise UserError(
                    "Contract %s is billed through %s: an amendment cannot take effect "
                    "inside a billed period (from %s at the earliest)."
                    % (
                        contract.code,
                        contract.billed_through_date,
                        contract.billed_through_date + timedelta(days=1),
                    )
                )
            if rec.kind == "pricing":
                if not rec.delta_value:
                    raise UserError("A pricing amendment needs a value change.")
                if (contract.annual_value or 0.0) + rec.delta_value <= 0:
                    raise UserError(
                        "Amendment %s would leave contract %s with no value: terminate "
                        "the contract instead." % (rec.name, contract.code)
                    )
            if rec.kind == "term":
                if not rec.new_date_end or rec.new_date_end <= contract.date_start:
                    raise UserError("A term amendment needs a new end date after the start.")
                if rec.new_date_end == contract.date_end:
                    raise UserError("The new end date is the current one.")

    def action_request_approval(self, justification=None):
        require_role(self.env, OFFICER, "Submitting an amendment")
        self._amendment_require_state(("draft",), "be submitted")
        today = fields.Date.context_today(self)
        for rec in self:
            if not self.env.su and rec.effective_from < today:
                raise UserError(
                    "Amendment %s is backdated (%s): an amendment takes effect from today "
                    "or later." % (rec.name, rec.effective_from)
                )
        self._amendment_validate()
        result = super().action_request_approval(justification=justification)
        self._guarded().write({"state": "submitted"})
        return result

    def action_dofa_approve(self):
        """Run by the deciding M63 task in the approver's env. Approved,
        the amendment applies at once when it is effective, else on its
        effective date (cron_apply_due_amendments)."""
        self._approval_assert_routed()
        self._amendment_require_state(("submitted",), "be approved")
        for rec in self:
            if rec._dofa_current_tier() == "tier_0":
                # a scope change: the Contract Manager decides, not the raiser
                if not (self.env.su or self.env.user.has_group(MANAGER)):
                    raise UserError("A scope amendment is approved by a Contract Manager.")
                if not self.env.su and rec.create_uid in rec._approval_acting_users():
                    raise UserError(
                        "Segregation of duties: you raised amendment %s, so another "
                        "Contract Manager must approve it." % rec.name
                    )
            else:
                super(FixContractAmendment, rec.sudo()).action_dofa_approve()
        self.sudo()._guarded().write({"state": "approved"})
        today = fields.Date.context_today(self)
        self.sudo().filtered(lambda r: r.effective_from <= today)._amendment_apply()
        return True

    def _approval_on_rejected(self, comment):
        self.sudo().filtered(lambda r: r.state == "submitted")._guarded().write(
            {"state": "rejected"}
        )
        return super()._approval_on_rejected(comment)

    def action_recall_approval(self):
        result = super().action_recall_approval()
        self.filtered(lambda r: r.state == "submitted")._guarded().write({"state": "draft"})
        return result

    def action_cancel(self):
        require_role(self.env, OFFICER, "Cancelling an amendment")
        self._amendment_require_state(("draft", "submitted", "approved"), "be cancelled")
        for rec in self:
            rec._approval_void("the amendment was cancelled")
            rec.sudo()._guarded().write({"state": "cancelled", "approval_state": "none"})
        return True

    def _amendment_assert_approved(self):
        for rec in self:
            if rec._dofa_current_tier() == "tier_0":
                if rec.state != "approved":
                    raise UserError("Amendment %s is not approved." % rec.name)
            else:
                rec._dofa_assert_approved("Amendment %s" % rec.name)

    def _amendment_apply(self):
        """Write the approved change onto the contract and version it.
        Service code: called by the approval, the daily cron, or trusted
        callers; the approval (or superuser trust) is the authority."""
        for rec in self:
            if rec.state == "applied":
                continue
            if not self.env.su:
                rec._amendment_require_state(("approved",), "be applied")
                rec._amendment_assert_approved()
            rec._amendment_validate()
            contract = rec.contract_id.sudo()
            version = (contract.amendment_version or 0) + 1
            before, end_before = contract.annual_value, contract.date_end
            vals = {"amendment_version": version}
            if rec.kind == "pricing":
                after = round(before + rec.delta_value, 2)
                vals["annual_value"] = after
                if contract.dofa_approved:
                    # the amendment's own approval now covers the contract value
                    vals["dofa_approved_amount"] = max(after, contract.dofa_approved_amount or 0.0)
                    vals["dofa_approved_tier"] = max(
                        contract.dofa_approved_tier or "tier_0",
                        contract._dofa_tier_for_amount(after),
                    )
            elif rec.kind == "term":
                vals["date_end"] = rec.new_date_end
            contract._guarded().write(vals)
            rec.sudo()._guarded().write(
                {
                    "state": "applied",
                    "version_no": version,
                    "value_before": before,
                    "value_after": contract.annual_value,
                    "date_end_before": end_before,
                    "applied_by": self.env.user.id,
                    "applied_on": fields.Datetime.now(),
                }
            )
            contract.message_post(
                body="Amendment %s applied (version %d): value %.2f -> %.2f, end %s -> %s."
                % (rec.name, version, before, contract.annual_value, end_before, contract.date_end)
            )
            publish(
                self.env,
                "contract.amended",
                "fix.contract",
                contract.id,
                {
                    "code": contract.code,
                    "amendment_id": rec.id,
                    "kind": rec.kind,
                    "version": version,
                    "value_before": float(before or 0.0),
                    "value_after": float(contract.annual_value or 0.0),
                    "effective_from": str(rec.effective_from),
                },
            )
            if rec.kind == "pricing":
                publish(
                    self.env,
                    "contract.price_revised",
                    "fix.contract",
                    contract.id,
                    {
                        "code": contract.code,
                        "old_annual_value": before,
                        "new_annual_value": contract.annual_value,
                        "reason": rec.note or rec.name,
                    },
                )
        return True

    @api.model
    def cron_apply_due_amendments(self):
        """Daily, idempotent: approved amendments whose effective date has
        come are applied. Returns the number applied."""
        today = fields.Date.context_today(self)
        due = self.sudo().search([("state", "=", "approved"), ("effective_from", "<=", today)])
        applied = 0
        for rec in due:
            try:
                with self.env.cr.savepoint():
                    rec._amendment_apply()
                    applied += 1
            except UserError as exc:
                rec.message_post(body="Could not apply on its effective date: %s" % exc)
        return applied


class FixContractRenewal(models.Model):
    """A renewal quote. Won, it drafts the next term (A04 build, M08-10)."""

    _name = "fix.contract.renewal"
    _description = "Contract Renewal"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "proposed_start, id"

    name = fields.Char(required=True)
    contract_id = fields.Many2one("fix.contract", required=True, ondelete="cascade", index=True)
    proposed_start = fields.Date(required=True)
    proposed_end = fields.Date(required=True)
    propo_value = fields.Monetary(currency_field="currency_id", string="Proposed Value")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    risk = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")],
        required=True,
        default="medium",
    )
    state = fields.Selection(
        [("draft", "Draft"), ("quoted", "Quoted"), ("won", "Won"), ("lost", "Lost")],
        required=True,
        default="draft",
        readonly=True,
        tracking=True,
    )
    renewal_contract_id = fields.Many2one(
        "fix.contract", string="Next Term", readonly=True, copy=False, ondelete="set null"
    )

    _QUOTE_FIELDS = frozenset(
        {"contract_id", "proposed_start", "proposed_end", "propo_value", "currency_id"}
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "renewal_contract_id"}

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if len(self) == 1 and self.state != "draft":
            locked |= self._QUOTE_FIELDS
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open():
            frozen = set(vals) & self._QUOTE_FIELDS
            for rec in self.filtered(lambda r: r.state != "draft"):
                if any(rec._fix_guard_differs(n, vals[n], rec[n]) for n in frozen):
                    raise UserError(
                        "Renewal quote %s has been issued: its terms are fixed." % rec.name
                    )
        return super().write(vals)

    def _renewal_check(self):
        for rec in self:
            contract = rec.contract_id
            if contract.state not in (*IN_FORCE, "expired"):
                raise UserError(
                    "Contract %s cannot be renewed: it is %s." % (contract.code, contract.state)
                )
            if rec.proposed_end <= rec.proposed_start:
                raise UserError("The proposed term must end after it starts.")
            if rec.proposed_start <= contract.date_start:
                raise UserError("The renewal must start after the current term starts.")
            if (rec.propo_value or 0.0) <= 0:
                raise UserError("A renewal quote needs a proposed value.")

    def action_quote(self):
        require_role(self.env, OFFICER, "Issuing a renewal quote")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft renewal can be quoted.")
        self._renewal_check()
        self.sudo()._guarded().write({"state": "quoted"})
        return True

    def action_mark_won(self):
        """The customer accepted: the next term is drafted (it is approved,
        signed and activated like any contract). The current term keeps its
        cover until it ends."""
        require_role(self.env, OFFICER, "Recording a won renewal")
        for rec in self:
            if rec.state != "quoted":
                raise UserError("Only a quoted renewal can be won (it is %s)." % rec.state)
        self._renewal_check()
        for rec in self:
            term = rec.contract_id._fix_create_renewal_term(
                date_start=rec.proposed_start,
                date_end=rec.proposed_end,
                value=rec.propo_value,
                name=rec.name,
            )
            rec.sudo()._guarded().write({"state": "won", "renewal_contract_id": term.id})
        return True

    def action_mark_lost(self):
        require_role(self.env, OFFICER, "Recording a lost renewal")
        for rec in self:
            if rec.state not in ("draft", "quoted"):
                raise UserError("Only an open renewal can be lost.")
        self.sudo()._guarded().write({"state": "lost"})
        return True


TERMINATION_TERM_FIELDS = frozenset(
    {"contract_id", "kind", "reason", "effective_date", "penalty_amount", "currency_id"}
)


class FixContractTermination(models.Model):
    _name = "fix.contract.termination"
    _description = "Contract Suspension / Termination"
    _inherit = ["mail.thread", "fix.dofa.mixin"]
    _order = "effective_date desc, id desc"

    _approval_domain = "contract_termination"
    _approval_apply_method = "action_dofa_approve"
    _approval_routed = True

    name = fields.Char(required=True)
    contract_id = fields.Many2one("fix.contract", required=True, ondelete="cascade", index=True)
    kind = fields.Selection(
        [("suspension", "Suspension"), ("termination", "Termination")],
        required=True,
        default="termination",
    )
    reason = fields.Char(required=True)
    effective_date = fields.Date(required=True)
    notice_required_days = fields.Integer(
        compute="_compute_notice", store=True, help="From the contract template's notice period."
    )
    notice_ok = fields.Boolean(
        string="Notice Period Satisfied",
        compute="_compute_notice",
        store=True,
        help="Computed: the effective date is at least the template's notice "
        "period after the notice was raised. A termination that does not "
        "honour it cannot execute (a suspension may be immediate).",
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    penalty_amount = fields.Monetary(
        string="Termination Penalty / Break Fee", currency_field="currency_id", default=0.0
    )
    # A04 build (M08-6): the tier was a free Selection (default Tier 1); it is
    # now the DOFA tier derived from the amount. A tier sent by a caller is
    # ignored, not stored. Kept under its old name for the screens.
    dofa_tier = fields.Selection(
        related="dofa_tier_required", string="Required DOFA Tier", readonly=True
    )
    dofa_approver_id = fields.Many2one(
        related="dofa_approved_by", string="DOFA Approver (legacy name)", readonly=True
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Awaiting Approval"),
            ("approved", "Approved"),
            ("effective", "Effective"),
            ("rejected", "Rejected"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="draft",
        readonly=True,
        tracking=True,
    )
    executed_by = fields.Many2one("res.users", readonly=True, copy=False)
    executed_on = fields.Datetime(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "executed_by", "executed_on"}

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if len(self) == 1 and self.state != "draft":
            locked |= TERMINATION_TERM_FIELDS | {"name"}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals.pop("dofa_tier", None)  # derived, never chosen
        return super().create(vals_list)

    def write(self, vals):
        vals.pop("dofa_tier", None)
        if self and not self._fix_guard_open():
            frozen = set(vals) & (TERMINATION_TERM_FIELDS | {"name"})
            for rec in self.filtered(lambda r: r.state != "draft"):
                if any(rec._fix_guard_differs(n, vals[n], rec[n]) for n in frozen):
                    raise UserError(
                        "Notice %s is %s: its terms (contract, date, penalty) are fixed. "
                        "Cancel it and raise a new one." % (rec.name, _states_label(rec, rec.state))
                    )
        return super().write(vals)

    @api.depends("effective_date", "contract_id.template_id.notice_period_days", "create_date")
    def _compute_notice(self):
        for rec in self:
            days = rec.contract_id.template_id.notice_period_days or 0
            raised = (rec.create_date or fields.Datetime.now()).date()
            rec.notice_required_days = days
            rec.notice_ok = bool(rec.effective_date and (rec.effective_date - raised).days >= days)

    # ---- DOFA: what the termination gives up --------------------------------------
    def _unexpired_value(self) -> float:
        self.ensure_one()
        contract = self.contract_id
        if (
            not (contract.date_end and self.effective_date)
            or self.effective_date > contract.date_end
        ):
            return 0.0
        days = (contract.date_end - self.effective_date).days + 1
        return round((contract.annual_value or 0.0) * days / 365.0, 2)

    def _dofa_amount(self) -> float:
        self.ensure_one()
        return round(self._unexpired_value() + abs(self.penalty_amount or 0.0), 2)

    def _dofa_thresholds(self):
        return TERMINATION_DOFA_THRESHOLDS

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "BDT %.2f (unexpired value %.2f + penalty %.2f on %s)" % (
            self._dofa_amount(),
            self._unexpired_value(),
            abs(self.penalty_amount or 0.0),
            self.contract_id.code,
        )

    @api.depends(
        "penalty_amount", "effective_date", "contract_id.annual_value", "contract_id.date_end"
    )
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    # ---- lifecycle ------------------------------------------------------------------
    def _termination_require_state(self, allowed, what):
        for rec in self:
            if rec.state not in allowed:
                raise UserError(
                    "Notice %s cannot %s: it is %s."
                    % (rec.name, what, _states_label(rec, rec.state))
                )

    def _termination_check_contract(self):
        for rec in self:
            allowed = IN_FORCE if rec.kind == "suspension" else (*IN_FORCE, "suspended")
            if rec.contract_id.state not in allowed:
                raise UserError(
                    "Contract %s is %s: it cannot be %s."
                    % (
                        rec.contract_id.code,
                        rec.contract_id.state,
                        "suspended" if rec.kind == "suspension" else "terminated",
                    )
                )

    def action_request_approval(self, justification=None):
        require_role(self.env, OFFICER, "Submitting a termination or suspension")
        self._termination_require_state(("draft",), "be submitted")
        self._termination_check_contract()
        today = fields.Date.context_today(self)
        for rec in self:
            if not self.env.su and rec.effective_date < today:
                raise UserError(
                    "Notice %s is backdated (%s): a termination takes effect from today "
                    "or later." % (rec.name, rec.effective_date)
                )
            if (rec.penalty_amount or 0.0) < 0:
                raise UserError("A penalty cannot be negative.")
        result = super().action_request_approval(justification=justification)
        self._guarded().write({"state": "submitted"})
        return result

    def action_dofa_approve(self):
        """Run by the deciding M63 task: the DOFA tier holder (not the
        raiser) approves, the amount is pinned."""
        self._approval_assert_routed()
        self._termination_require_state(("submitted",), "be approved")
        result = super(FixContractTermination, self.sudo()).action_dofa_approve()
        self.sudo()._guarded().write({"state": "approved"})
        return result

    def _approval_on_rejected(self, comment):
        self.sudo().filtered(lambda r: r.state == "submitted")._guarded().write(
            {"state": "rejected"}
        )
        return super()._approval_on_rejected(comment)

    def action_recall_approval(self):
        result = super().action_recall_approval()
        self.filtered(lambda r: r.state == "submitted")._guarded().write({"state": "draft"})
        return result

    def action_cancel(self):
        require_role(self.env, OFFICER, "Cancelling a termination notice")
        self._termination_require_state(("draft", "submitted", "approved"), "be cancelled")
        for rec in self:
            rec._approval_void("the notice was cancelled")
            rec.sudo()._guarded().write({"state": "cancelled", "approval_state": "none"})
        return True

    def action_execute_termination(self):
        """Enact the approved termination / suspension on the contract, on or
        after its effective date (Contract Manager; the daily job runs it on
        the date). The approval must still cover the amount."""
        require_role(self.env, MANAGER, "Executing a termination")
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.state != "approved":
                raise UserError(
                    "Termination requires DOFA approval prior to execution "
                    "(DOFA governance control)."
                )
            rec._dofa_assert_approved("Termination %s" % rec.name)
            if rec.effective_date > today:
                raise UserError(
                    "Notice %s takes effect on %s; it executes on that date."
                    % (rec.name, rec.effective_date)
                )
            if rec.kind == "termination" and not rec.notice_ok:
                raise UserError(
                    "Notice %s does not honour the %d-day notice period of the contract."
                    % (rec.name, rec.notice_required_days)
                )
            rec._termination_check_contract()
            rec.sudo()._guarded().write(
                {
                    "state": "effective",
                    "executed_by": self.env.user.id,
                    "executed_on": fields.Datetime.now(),
                }
            )
            new_state = "terminated" if rec.kind == "termination" else "suspended"
            rec.contract_id.sudo()._guarded().write({"state": new_state})
            publish(
                self.env,
                "contract.terminated",
                "fix.contract.termination",
                rec.id,
                {
                    "contract_id": rec.contract_id.id,
                    "kind": rec.kind,
                    "effective_date": str(rec.effective_date),
                    "penalty_amount": float(rec.penalty_amount or 0.0),
                },
            )
        return True

    @api.model
    def cron_execute_due_terminations(self):
        """Daily, idempotent: approved notices whose effective date has come
        are executed. Returns the number executed."""
        today = fields.Date.context_today(self)
        due = self.sudo().search([("state", "=", "approved"), ("effective_date", "<=", today)])
        done = 0
        for rec in due:
            try:
                with self.env.cr.savepoint():
                    rec.action_execute_termination()
                    done += 1
            except (UserError, ValueError) as exc:
                rec.message_post(body="Could not execute on its effective date: %s" % exc)
        return done
