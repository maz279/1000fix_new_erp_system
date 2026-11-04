# fix_compensation_proposal — M57: the compensation-proposal cycle
# (BRU-PIC-17, FR-PIC-038..040).
#
# A09 workflow audit M57 §1.2 row 17 and §2 "Compensation proposal vs budget":
# there was no proposal model; a salary changed only by editing a contract.
# Now a merit or raise proposal is:
#   1. proposed by the employee's LINE MANAGER (from the closed review, or for
#      a direct report), with a justification, inside the pay band;
#   2. reviewed by a Performance Calibrator who is neither the manager nor the
#      employee (calibration may adjust the figure, again inside the band);
#   3. approved by the Compensation Manager through a routed M63 request
#      (fix.people.approval.mixin): never the proposer, the calibrator, the
#      record's creator or the employee.
# The approval applies the raise as a new contract VERSION
# (fix.employment.contract.action_new_version): the active contract's terms
# stay frozen, and the draft version goes through M21's legal sign-off and
# activation like any other. The figure, the contract and the effective date
# are pinned from the proposal on: nothing is typed after it is raised.
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError

from libs.py.fix_events import publish

from .fix_performance import CALIBRATOR, COMPENSATION, require_group

OPEN_STATES = ("submitted", "calibrated")


class FixCompensationProposal(models.Model):
    _name = "fix.compensation.proposal"
    _description = "Compensation Proposal"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.people.approval.mixin"]
    _order = "id desc"

    _approval_domain = "hr_compensation"
    _approval_apply_method = "action_approve"
    _approval_group = COMPENSATION

    name = fields.Char(required=True, default="New", readonly=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", required=True, index=True)
    contract_id = fields.Many2one(
        "fix.employment.contract", string="Active Contract", required=True, ondelete="restrict"
    )
    review_id = fields.Many2one(
        "fix.performance.review", string="Review Cycle", ondelete="set null"
    )
    proposal_type = fields.Selection(
        [("merit", "Merit Increase"), ("raise", "Salary Raise"), ("market", "Market Adjustment")],
        required=True,
        default="merit",
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    current_basic = fields.Monetary(
        string="Current Basic",
        currency_field="currency_id",
        readonly=True,
        groups="%s,%s,hr.group_hr_user" % (COMPENSATION, CALIBRATOR),
    )
    proposed_basic = fields.Monetary(
        string="Proposed Basic",
        currency_field="currency_id",
        readonly=True,
        groups="%s,%s,hr.group_hr_user" % (COMPENSATION, CALIBRATOR),
    )
    increase_pct = fields.Float(
        string="Increase %",
        compute="_compute_increase",
        digits=(5, 2),
        groups="%s,%s,hr.group_hr_user" % (COMPENSATION, CALIBRATOR),
    )
    effective_date = fields.Date(string="Effective From", required=True, readonly=True)
    justification = fields.Text(required=True, readonly=True)
    state = fields.Selection(
        [
            ("submitted", "Awaiting Calibration"),
            ("calibrated", "Awaiting Compensation Approval"),
            ("approved", "Approved (New Contract Version)"),
            ("returned", "Returned by Calibration"),
            ("rejected", "Rejected"),
            ("withdrawn", "Withdrawn"),
        ],
        default="submitted",
        required=True,
        tracking=True,
        index=True,
    )
    proposed_by_id = fields.Many2one("res.users", string="Proposed By", readonly=True)
    proposed_at = fields.Datetime(string="Proposed At", readonly=True)
    calibrated_by_id = fields.Many2one("res.users", string="Calibrated By", readonly=True)
    calibrated_at = fields.Datetime(string="Calibrated At", readonly=True)
    calibration_note = fields.Text(string="Calibration Note", readonly=True)
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True)
    approved_at = fields.Datetime(string="Approved At", readonly=True)
    new_contract_id = fields.Many2one(
        "fix.employment.contract", string="New Contract Version", readonly=True
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    _PINNED = frozenset(
        {
            "name",
            "company_id",
            "employee_id",
            "contract_id",
            "review_id",
            "proposal_type",
            "currency_id",
            "current_basic",
            "proposed_basic",
            "effective_date",
            "justification",
        }
    )

    def _fix_guarded_fields(self) -> set:
        return (
            super()._fix_guarded_fields()
            | self._PINNED
            | {
                "state",
                "proposed_by_id",
                "proposed_at",
                "calibrated_by_id",
                "calibrated_at",
                "calibration_note",
                "approved_by_id",
                "approved_at",
                "new_contract_id",
            }
        )

    @api.depends("current_basic", "proposed_basic")
    def _compute_increase(self):
        for rec in self:
            cur = rec.current_basic or 0.0
            rec.increase_pct = round((rec.proposed_basic - cur) / cur * 100.0, 2) if cur else 0.0

    # ---- approval declarations ---------------------------------------------
    def _approval_amount(self) -> float:
        rec = self.sudo()
        return float((rec.proposed_basic or 0.0) - (rec.current_basic or 0.0))

    def _approval_preparers(self):
        return self.mapped("proposed_by_id") | self.mapped("calibrated_by_id")

    def _approval_needed(self) -> bool:
        return self.state == "calibrated"

    def _approval_on_rejected(self, comment):
        for rec in self:
            rec._guarded().write({"state": "rejected"})
            rec.message_post(body="Compensation proposal rejected: %s" % (comment or ""))

    # ---- creation: only by the line manager's proposal -------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            raise UserError(
                "A compensation proposal is raised by the employee's line manager "
                "(Propose Compensation on the review), not typed."
            )
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.compensation.proposal")
                    or "CMP/New"
                )
        return super().create(vals_list)

    def unlink(self):
        if not self.env.su:
            raise UserError("A compensation proposal is evidence; it is not deleted.")
        return super().unlink()

    # ---- checks ----------------------------------------------------------------------
    @api.model
    def _fix_band_check(self, contract, basic):
        """I7 on the proposed figure: the contract's gross with the new basic
        must sit inside the grade's band."""
        contract = contract.sudo()
        gross = contract._fix_contract_gross() - (contract.basic_monthly or 0.0) + basic
        self.env["fix.compensation.band"]._fix_check_amount(
            contract._fix_contract_grade(),
            gross,
            company=contract.company_id,
            what="The proposed monthly gross",
        )

    @api.model
    def _fix_parse_amount_note(self, text):
        """'<amount> <note>' or '<note>' (the workspace prompt's one string)."""
        text = str(text or "").strip()
        head, _sep, tail = text.partition(" ")
        try:
            return float(head.replace(",", "")), tail.strip()
        except ValueError:
            return None, text

    @api.model
    def _fix_propose(
        self,
        employee,
        proposed_basic,
        justification,
        proposal_type="merit",
        effective_date=None,
        review=None,
    ):
        """The line manager raises a proposal for a direct report."""
        employee = employee.sudo()
        user = self.env.user
        if not self.env.su:
            manager = employee.parent_id
            if not manager or manager.user_id != user:
                raise AccessError(
                    "A compensation proposal for %s is raised by their line manager."
                    % employee.name
                )
            if employee.user_id == user:
                raise UserError("You cannot propose your own pay.")
        justification = (justification or "").strip()
        if not justification:
            raise UserError("Justify the proposal (performance, market data, role change).")
        try:
            proposed_basic = float(proposed_basic or 0.0)
        except (TypeError, ValueError):
            raise UserError("The proposed basic is a monthly amount in BDT.") from None
        Contract = self.env["fix.employment.contract"].sudo()
        contract = Contract.search(
            [("employee_id", "=", employee.id), ("state", "=", "active")], limit=1
        )
        if not contract:
            raise UserError("%s has no active contract to change." % employee.name)
        if proposed_basic <= (contract.basic_monthly or 0.0):
            raise UserError(
                "The proposal raises the basic: %.2f is not above the current %.2f."
                % (proposed_basic, contract.basic_monthly or 0.0)
            )
        if self.sudo().search_count(
            [("employee_id", "=", employee.id), ("state", "in", OPEN_STATES)]
        ):
            raise UserError("%s already has an open compensation proposal." % employee.name)
        self._fix_band_check(contract, proposed_basic)
        effective = fields.Date.to_date(effective_date) if effective_date else None
        effective = effective or fields.Date.context_today(self)
        if effective < fields.Date.context_today(self):
            raise UserError("A raise takes effect from today or later, never backdated.")
        rec = (
            self.sudo()
            ._guarded()
            .create(
                {
                    "company_id": contract.company_id.id,
                    "employee_id": employee.id,
                    "contract_id": contract.id,
                    "review_id": review.id if review else False,
                    "proposal_type": proposal_type or "merit",
                    "currency_id": contract.currency_id.id or self.env.ref("base.BDT").id,
                    "current_basic": contract.basic_monthly,
                    "proposed_basic": proposed_basic,
                    "effective_date": effective,
                    "justification": justification,
                    "state": "submitted",
                    "proposed_by_id": user.id,
                    "proposed_at": fields.Datetime.now(),
                }
            )
        )
        calibrators = (
            self.env.ref(CALIBRATOR)
            .sudo()
            .all_user_ids.filtered(
                lambda u: u.active and not u.share and u not in (user | employee.user_id)
            )
        )
        for cal in calibrators[:5]:
            rec.activity_schedule(
                "mail.mail_activity_data_todo",
                summary="Calibrate %s" % rec.name,
                note="Compensation proposal for %s awaits calibration." % employee.name,
                user_id=cal.id,
            )
        return rec.with_env(self.env)

    # ---- transitions -------------------------------------------------------------------
    def _fix_assert_calibrator(self):
        require_group(self.env, CALIBRATOR, "Calibrating a compensation proposal")
        for rec in self:
            if self.env.su:
                continue
            if self.env.user in (rec.proposed_by_id | rec.employee_id.sudo().user_id):
                raise UserError("The proposer and the employee do not calibrate a proposal.")

    def action_calibration_review(self, calibration=None, note=None):
        """The calibrator confirms (or adjusts, inside the band) the figure and
        routes the proposal to the Compensation Manager. ``calibration`` is the
        workspace prompt: '<adjusted basic> <note>' or '<note>'."""
        self._fix_assert_calibrator()
        amount, text = self._fix_parse_amount_note(calibration)
        text = (note or text or "").strip()
        if not text:
            raise UserError("Record the calibration note.")
        for rec in self:
            if rec.state != "submitted":
                raise UserError("%s is not awaiting calibration." % rec.name)
            vals = {
                "state": "calibrated",
                "calibrated_by_id": self.env.user.id,
                "calibrated_at": fields.Datetime.now(),
                "calibration_note": text,
            }
            if amount is not None:
                if amount <= (rec.sudo().current_basic or 0.0):
                    raise UserError("A calibrated figure still raises the basic.")
                self._fix_band_check(rec.contract_id, amount)
                vals["proposed_basic"] = amount
            rec._guarded().write(vals)
            rec.activity_unlink(["mail.mail_activity_data_todo"])
        return self.action_request_approval()

    def action_calibration_return(self, note=None):
        self._fix_assert_calibrator()
        note = (note or "").strip()
        if not note:
            raise UserError("Say why the proposal is returned to the manager.")
        for rec in self:
            if rec.state != "submitted":
                raise UserError("%s is not awaiting calibration." % rec.name)
            rec._guarded().write(
                {
                    "state": "returned",
                    "calibrated_by_id": self.env.user.id,
                    "calibrated_at": fields.Datetime.now(),
                    "calibration_note": note,
                }
            )
            rec.activity_unlink(["mail.mail_activity_data_todo"])
        return True

    def action_withdraw(self):
        """The proposer withdraws an open proposal. Narrow: the line manager
        holds no write access to M57 records (RAP X-02)."""
        self.check_access("read")
        for rec in self.sudo():
            if not self.env.su and rec.proposed_by_id != self.env.user:
                raise AccessError("Only the manager who proposed %s withdraws it." % rec.name)
            if rec.state not in OPEN_STATES:
                raise UserError("%s is no longer open." % rec.name)
            if rec.approval_state == "pending":
                rec._approval_void("the manager withdrew the proposal")
            rec._guarded().write({"state": "withdrawn"})
        return True

    def action_approve(self):
        """The Compensation Manager's routed decision: the raise becomes a new
        contract version, inside the band, from the pinned figure."""
        self._approval_assert_routed()
        self._people_assert_not_conflicted()
        for rec in self:
            if rec.state != "calibrated":
                raise UserError("%s is not awaiting approval." % rec.name)
            pinned = rec.sudo()
            contract = pinned.contract_id
            if contract.state != "active":
                raise UserError(
                    "%s is no longer the active contract; propose again." % contract.name
                )
            if abs((contract.basic_monthly or 0.0) - (pinned.current_basic or 0.0)) > 0.005:
                raise UserError(
                    "The contract's basic changed since the proposal (%.2f, proposed against "
                    "%.2f); propose again." % (contract.basic_monthly, pinned.current_basic)
                )
            self._fix_band_check(contract, pinned.proposed_basic)
            # The approver is not necessarily an HR Officer: the routed
            # decision is the authority, so the version is opened as superuser.
            out = contract.sudo().action_new_version(effective_date=pinned.effective_date)
            version = self.env["fix.employment.contract"].sudo().browse(out["res_id"])
            version._guarded().write({"basic_monthly": pinned.proposed_basic})
            decider = rec._people_decider()
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": decider.id,
                    "approved_at": fields.Datetime.now(),
                    "new_contract_id": version.id,
                }
            )
            publish(
                self.env,
                "compensation.proposal.approved",
                "fix.compensation.proposal",
                rec.id,
                {
                    "employee_id": rec.employee_id.id,
                    "contract_id": contract.id,
                    "new_contract_id": version.id,
                    "effective_date": str(pinned.effective_date),
                },
            )
        return True
