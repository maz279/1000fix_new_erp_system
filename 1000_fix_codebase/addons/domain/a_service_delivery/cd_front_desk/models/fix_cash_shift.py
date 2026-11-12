# fix.cash.shift — cash drawer and shift control (P04-M02-T04).
# AS-10: money is Monetary with explicit currency. Reconciles to M19 in Phase 6.
#
# A02 audit (M04-1/-2/-3/-4/-6/-7/-10/-11): every drawer total, the count, the
# state and the variance sign-off were plain writable fields. A cashier zeroed
# BDT 3,000 of takings, typed her own count, signed off her own -4,000
# variance and wrote "reconciled" on an open drawer; sales kept posting into a
# reconciled shift. The drawer is now driven only by its transitions:
#   open --close--> counting --blind count--> counting (counted)
#        --confirm--> closed --[variance approval]--> reconcile
# and the movements (takings, refunds, field cash) are posted only by the
# counter-sale, refund and field-settlement methods, onto an OPEN shift.
#
# A02 audit B1 (P1): the variance approval is a routed M63 request. The
# cashier requests it once the count is in; the engine routes it to a Branch
# Manager who did not handle the drawer, and action_approve_variance runs
# only from that manager's inbox, pinned to the variance it saw.
import logging

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

logger = logging.getLogger(__name__)

# The variance a branch may close without a manager's sign-off. A policy
# number, not a control: the default is the BDT 100 the model always used.
TOLERANCE_PARAM = "cd_front_desk.variance_tolerance_bdt"
DEFAULT_TOLERANCE = 100.0
# BRU-FRD-01 scope: "branch" (one live shift per branch, the rule as written)
# or "operator" (one per branch and cashier, for multi-counter branches).
OPEN_SHIFT_SCOPE_PARAM = "cd_front_desk.open_shift_scope"
# A shift is "not closed" until its count is confirmed.
LIVE_STATES = ("open", "counting")
FINAL_STATES = ("reconciled", "discrepancy")

GROUP_CASHIER = "cd_front_desk.group_fd_cashier"
GROUP_MANAGER = "cd_front_desk.group_fd_branch_manager"

DENOMINATIONS = (
    ("denom_1000_count", 1000.0),
    ("denom_500_count", 500.0),
    ("denom_200_count", 200.0),
    ("denom_100_count", 100.0),
    ("denom_50_count", 50.0),
    ("denom_20_count", 20.0),
    ("denom_10_count", 10.0),
)


# drawer total -> its ledger type, for the movements the system posts
SYSTEM_TYPE_FOR = {
    "cash_payments": "receipt",
    "cash_refunds": "refund",
    "field_cash_deposited": "field_cash",
}


def default_operating_unit(env, vals):
    """The operating unit of a front-desk record that was saved without one:
    its cash shift's, else its branch's, else the user's default.

    The field is required on the token, the intake and the shift, and none of
    the M04 workspace forms asks for it (the branch decides it), so a token, an
    intake or a shift opened from the workspace could never be saved (M04
    sub-module audit, 13 Nov 2026). Returns an id, or False."""
    if vals.get("shift_id"):
        shift = env["fix.cash.shift"].browse(vals["shift_id"]).exists()
        if shift and shift.operating_unit_id:
            return shift.operating_unit_id.id
    if vals.get("branch_id"):
        branch = env["fix.branch"].browse(vals["branch_id"]).exists()
        if branch and "operating_unit_id" in branch._fields and branch.operating_unit_id:
            return branch.operating_unit_id.id
    user_ou = getattr(env.user, "default_operating_unit_id", False)
    return user_ou.id if user_ou else False


def fill_operating_unit(env, vals_list):
    for vals in vals_list:
        if not vals.get("operating_unit_id"):
            ou = default_operating_unit(env, vals)
            if ou:
                vals["operating_unit_id"] = ou


class FixApprovalMatrixFrontDesk(models.Model):
    _inherit = "fix.approval.matrix"

    # A02 audit B1: the M04 approvals routed through M63
    decision_domain = fields.Selection(
        selection_add=[
            ("cash_variance", "Cash Drawer Variance"),
            ("counter_refund", "Counter-Sale Refund"),
            ("price_override", "Counter Price Below List"),
            ("diagnostic_fee_waiver", "Diagnostic Fee Waiver"),
        ],
        ondelete={
            "cash_variance": "cascade",
            "counter_refund": "cascade",
            "price_override": "cascade",
            "diagnostic_fee_waiver": "cascade",
        },
    )


class FixCashShift(models.Model):
    """A cash-drawer shift with opening/closing balances and reconciliation."""

    _name = "fix.cash.shift"
    _description = "Cash Shift"
    # fix.approvable.mixin brings fix.guarded.mixin with it (A02 audit B1)
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.approvable.mixin"]
    _order = "shift_date desc, branch_id"

    _approval_domain = "cash_variance"
    _approval_apply_method = "action_approve_variance"
    _approval_group = GROUP_MANAGER
    _approval_routed = True

    @api.model_create_multi
    def create(self, vals_list):
        # the branch decides the unit: the Shift Open/Close form never asks
        fill_operating_unit(self.env, vals_list)
        return super().create(vals_list)

    def _fix_guarded_fields(self) -> set:
        # A02 audit M04-1/-2/-3: the drawer totals, the count, the sign-off
        # and the state change only through the transitions below.
        return super()._fix_guarded_fields() | {
            "state",
            "cash_payments",
            "cash_refunds",
            "cash_advances",
            "field_cash_deposited",
            "closing_counted",
            "expected_closing",
            "variance",
            "blind_count_submitted",
            "counted_by",
            "counted_at",
            "supervisor_variance_approved_by",
            "variance_approved_amount",
            "variance_approved_at",
            "reconciled_by",
            "reconciled_at",
            "closed_at",
            "opened_at",
        }

    # What the shift was opened with: frozen once the drawer leaves "open"
    # (a lowered float after the count hides a shortage).
    _FROZEN_AFTER_OPEN = frozenset(
        {
            "company_id",
            "operating_unit_id",
            "branch_id",
            "shift_date",
            "operator_id",
            "currency_id",
            "opening_float",
        }
    )
    # What the count was made of: frozen once the count is confirmed. Bank
    # deposit details and notes stay editable, because banking follows close.
    _FROZEN_AFTER_CLOSE = _FROZEN_AFTER_OPEN | frozenset(
        {"shift_type", "coins_amount", "mfs_settled_amount", *(n for n, _v in DENOMINATIONS)}
    )

    # The float is declared when the shift is opened and is the base of the
    # expected closing: lowered while the drawer is open, it hides exactly the
    # cash taken since. Only superuser data repair corrects a mistyped float.
    _FROZEN_WHEN_OPEN = frozenset({"opening_float"})

    def _fix_frozen_fields(self) -> frozenset:
        if self.state == "open":
            return self._FROZEN_WHEN_OPEN
        if self.state == "counting":
            return self._FROZEN_AFTER_OPEN
        return self._FROZEN_AFTER_CLOSE

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if not self:
            return locked
        return locked | set().union(*(rec._fix_frozen_fields() for rec in self))

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)

    branch_id = fields.Many2one("fix.branch", string="Branch", required=True)
    shift_date = fields.Date(default=fields.Date.today, required=True)
    shift_type = fields.Selection(
        [
            ("morning", "Morning"),
            ("afternoon", "Afternoon"),
            ("evening", "Evening"),
            ("full_day", "Full Day"),
        ],
        required=True,
        default="full_day",
    )
    operator_id = fields.Many2one("hr.employee", string="Shift Operator", required=True)

    state = fields.Selection(
        [
            ("open", "Open"),
            ("counting", "Counting"),
            ("closed", "Closed"),
            ("reconciled", "Reconciled"),
            ("discrepancy", "Discrepancy"),
        ],
        default="open",
        required=True,
        tracking=True,
    )

    # AS-10: all cash amounts are Monetary with explicit currency
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    opening_float = fields.Monetary(
        string="Opening Float", currency_field="currency_id", required=True, tracking=True
    )
    closing_counted = fields.Monetary(
        string="Closing Counted", currency_field="currency_id", readonly=True, tracking=True
    )
    expected_closing = fields.Monetary(
        string="Expected Closing",
        currency_field="currency_id",
        compute="_compute_expected",
        store=True,
    )
    variance = fields.Monetary(
        string="Variance", currency_field="currency_id", compute="_compute_expected", store=True
    )

    opened_at = fields.Datetime(default=fields.Datetime.now, readonly=True)
    closed_at = fields.Datetime(readonly=True)

    # Transaction summary — posted by the source documents, never typed.
    cash_payments = fields.Monetary(
        string="Cash Payments", currency_field="currency_id", readonly=True, tracking=True
    )
    cash_refunds = fields.Monetary(
        string="Cash Refunds", currency_field="currency_id", readonly=True, tracking=True
    )
    cash_advances = fields.Monetary(
        string="Cash Advances", currency_field="currency_id", readonly=True, tracking=True
    )

    # --- A02 Enterprise Data Capture, Blind Denomination Count & HS-08 Field Cash Bridge (FLAW-04.2) ---
    blind_count_submitted = fields.Boolean(
        string="Blind Denomination Count Submitted",
        default=False,
        readonly=True,
        tracking=True,
        help="FLAW-04.2: True when cashier submits physical Bangladesh Taka denomination counts before viewing expected balance.",
    )
    counted_by = fields.Many2one("res.users", string="Counted By", readonly=True)
    counted_at = fields.Datetime(string="Counted At", readonly=True)
    denom_1000_count = fields.Integer(string="৳1000 Notes Count", default=0)
    denom_500_count = fields.Integer(string="৳500 Notes Count", default=0)
    denom_200_count = fields.Integer(string="৳200 Notes Count", default=0)
    denom_100_count = fields.Integer(string="৳100 Notes Count", default=0)
    denom_50_count = fields.Integer(string="৳50 Notes Count", default=0)
    denom_20_count = fields.Integer(string="৳20 Notes Count", default=0)
    denom_10_count = fields.Integer(string="৳10 Notes Count", default=0)
    coins_amount = fields.Monetary(
        string="Coins & Small Change (BDT)", currency_field="currency_id", default=0.0
    )
    field_cash_deposited = fields.Monetary(
        string="Field Engineer COD Handover (BDT)",
        currency_field="currency_id",
        default=0.0,
        readonly=True,
        tracking=True,
        help="HS-08: Physical cash handed over by M02 Field Engineers into the branch drawer.",
    )
    mfs_settled_amount = fields.Monetary(
        string="MFS & Card Batch Total (bKash/Nagad/POS)",
        currency_field="currency_id",
        default=0.0,
    )
    bank_deposit_slip_no = fields.Char(
        string="Treasury Bank Deposit Slip Ref",
        tracking=True,
    )
    bank_deposit_attachment_id = fields.Many2one(
        "ir.attachment",
        string="Stamped Bank Deposit Slip Scan",
    )
    supervisor_variance_approved_by = fields.Many2one(
        "res.users",
        string="Supervisor Variance Sign-off",
        readonly=True,
        tracking=True,
        help="The Branch Manager who approved the counted variance. Stamped by "
        "Approve Variance; voided by a recount.",
    )
    variance_approved_amount = fields.Monetary(
        string="Approved Variance",
        currency_field="currency_id",
        readonly=True,
        tracking=True,
        help="The variance the manager approved. Reconcile refuses any other figure.",
    )
    variance_approved_at = fields.Datetime(string="Variance Approved At", readonly=True)

    reconciliation_notes = fields.Text()
    reconciled_by = fields.Many2one("res.users", readonly=True)
    reconciled_at = fields.Datetime(readonly=True)

    @api.depends(
        "opening_float",
        "cash_payments",
        "cash_refunds",
        "cash_advances",
        "field_cash_deposited",
        "closing_counted",
        "blind_count_submitted",
        "state",
    )
    def _compute_expected(self):
        for rec in self:
            rec.expected_closing = (
                rec.opening_float
                + rec.cash_payments
                + rec.field_cash_deposited
                - rec.cash_refunds
                - rec.cash_advances
            )
            # The variance exists once there is a count. A count of 0.00 IS a
            # count — an empty drawer — so it must not read as "no variance".
            # While the cashier is still counting (no count submitted) it stays
            # 0: showing counted - expected then would reveal the expected
            # figure and defeat the blind count (A02 audit M04-11).
            counted = rec.blind_count_submitted or rec.state in ("closed", *FINAL_STATES)
            rec.variance = rec.closing_counted - rec.expected_closing if counted else 0.0

    # ------------------------------------------------------------ constraints

    @api.constrains("state", "branch_id", "operator_id", "company_id")
    def _check_one_live_shift(self):
        """BRU-FRD-01 (A02 audit M04-10): a branch cannot open a new shift
        while a prior one is not closed."""
        scope = self.env["ir.config_parameter"].sudo().get_param(OPEN_SHIFT_SCOPE_PARAM, "branch")
        for rec in self.filtered(lambda s: s.state in LIVE_STATES):
            domain = [
                ("id", "!=", rec.id),
                ("company_id", "=", rec.company_id.id),
                ("branch_id", "=", rec.branch_id.id),
                ("state", "in", LIVE_STATES),
            ]
            if scope == "operator":
                domain.append(("operator_id", "=", rec.operator_id.id))
            other = self.sudo().search(domain, limit=1)
            if other:
                raise ValidationError(
                    "Branch %s already has a shift that is not closed (shift #%s, %s). "
                    "Count and close it before opening another (BRU-FRD-01)."
                    % (rec.branch_id.display_name, other.id, other.operator_id.name or "")
                )

    def write(self, vals):
        """A02 audit M04-4: a counted shift's float and denominations, and a
        reconciled shift's figures, are frozen. Superuser data repair aside,
        nothing rewrites them."""
        if not self.env.su:
            for rec in self:
                frozen = rec._fix_frozen_fields() & set(vals)
                changed = [n for n in frozen if rec._fix_guard_differs(n, vals[n], rec[n])]
                if changed:
                    labels = ", ".join(sorted(rec._fields[n].string or n for n in changed))
                    raise UserError(
                        "Shift #%s is %s: %s can no longer be changed."
                        % (rec.id, dict(rec._fields["state"].selection)[rec.state], labels)
                    )
        return super().write(vals)

    # ------------------------------------------------------------ roles

    def _fd_tolerance(self) -> float:
        raw = self.env["ir.config_parameter"].sudo().get_param(TOLERANCE_PARAM)
        try:
            return float(raw) if raw not in (None, False, "") else DEFAULT_TOLERANCE
        except ValueError:
            return DEFAULT_TOLERANCE

    def _fd_require_group(self, xmlid, role, action):
        """The acting user must hold `role`. Superuser code is trusted."""
        if self.env.su or self.env.user.has_group(xmlid):
            return
        raise UserError(
            "Only a %s may %s. If no one holds this role yet, ask the administrator "
            "to appoint one." % (role, action)
        )

    def _fd_require_cashier(self, action):
        if self.env.su or self.env.user.has_group(GROUP_CASHIER):
            return
        self._fd_require_group(GROUP_MANAGER, "Front Desk Cashier or Branch Manager", action)

    def _fd_cash_handlers(self):
        """The users who handled this drawer: its cashier and its counter."""
        self.ensure_one()
        users = self.operator_id.user_id | self.counted_by
        if not self.operator_id.user_id:
            users |= self.create_uid
        return users

    def _fd_require_independent(self, action):
        """BRU-FRD-11 (A02 audit M04-6): the person who handled the cash
        cannot approve or reconcile it."""
        if self.env.su:
            return
        for rec in self:
            if self.env.user in rec._fd_cash_handlers():
                raise UserError(
                    "You handled the cash on shift #%s, so you cannot %s it. Another "
                    "Branch Manager must do this (BRU-FRD-11)." % (rec.id, action)
                )

    # ------------------------------------------------------------ routing

    def _approval_amount(self) -> float:
        return abs(self.variance or 0.0) if len(self) == 1 else 0.0

    def _approval_needed(self) -> bool:
        """A counted variance beyond tolerance that no approval covers yet."""
        self.ensure_one()
        if self.state not in ("counting", "closed") or not self.blind_count_submitted:
            return False
        if abs(self.variance) <= self._fd_tolerance():
            return False
        approved = self.supervisor_variance_approved_by and (
            abs(self.variance_approved_amount - self.variance) <= 0.005
        )
        return not approved

    def _approval_excluded(self):
        """BRU-FRD-11: whoever handled the cash never receives the task."""
        return super()._approval_excluded() | self._fd_cash_handlers().sudo()

    # ------------------------------------------------------------ movements

    def _post_cash_movement(self, field, amount, reference=None, movement=None):
        """Post a drawer movement. The only writer of the drawer totals: the
        counter sale, its refund and the M02 field-cash settlement call it,
        after their own checks. A movement lands only on an OPEN shift —
        a counted or reconciled drawer does not move (A02 audit M04-4).

        Every posting is also a row of the drawer's ledger (fix.cash.movement,
        FR-FRD-015): ``reference`` names the source document. A cash-out the
        cashier recorded passes its own ``movement``, which is marked posted
        instead of a new row being written."""
        if field not in ("cash_payments", "cash_refunds", "cash_advances", "field_cash_deposited"):
            raise UserError("Unknown drawer movement %s." % field)
        Movement = self.env["fix.cash.movement"].sudo()._guarded()
        for rec in self:
            if rec.state != "open":
                raise UserError(
                    "Shift #%s is %s: cash can be posted only to an open shift."
                    % (rec.id, dict(rec._fields["state"].selection)[rec.state])
                )
            # sudo: the posting is the consequence of a transition the caller
            # already authorised (a refund approver need not be a cashier);
            # the acting user stays the author of the tracked change.
            rec.sudo()._guarded().write({field: (rec[field] or 0.0) + amount})
            now = fields.Datetime.now()
            if movement:
                movement.sudo()._guarded().write({"state": "posted", "posted_at": now})
            elif field in SYSTEM_TYPE_FOR:
                Movement.create(
                    {
                        "shift_id": rec.id,
                        "movement_type": SYSTEM_TYPE_FOR[field],
                        "amount": abs(amount),
                        "reference": reference or "",
                        "state": "posted",
                        "posted_at": now,
                        "recorded_by_id": self.env.uid,
                    }
                )

    def _post_field_cash(self, amount, reference=None):
        """HS-08: M02 field COD handed over into this drawer (see
        cd_field_service action_handover_field_cash)."""
        if amount <= 0:
            raise UserError("Field cash handed over must be a positive amount.")
        self._post_cash_movement("field_cash_deposited", amount, reference=reference)

    @api.model
    def _fd_open_shift_for(self, branch, company=None):
        """The branch's open shift, or an empty recordset."""
        return self.sudo().search(
            [
                ("branch_id", "=", branch.id),
                ("company_id", "=", (company or self.env.company).id),
                ("state", "=", "open"),
            ],
            order="id desc",
            limit=1,
        )

    # ------------------------------------------------------------ transitions

    def action_close_shift(self):
        self._fd_require_cashier("close a cash shift")
        for rec in self:
            if rec.state != "open":
                raise ValidationError("Only open shifts can be closed.")
            rec._guarded().write({"state": "counting"})

    def action_submit_blind_count(self):
        """FLAW-04.2 (A02 audit M04-11): the count comes only from the physical
        BDT denominations. It does not reveal the expected figure or the
        variance — a count that is told it is short gets recounted until it
        isn't. A recount voids any variance approval."""
        self._fd_require_cashier("submit a cash count")
        for rec in self:
            if rec.state not in ("open", "counting"):
                raise ValidationError(
                    "Blind cash count can only be submitted on an open or counting shift."
                )
            denom_total = sum((rec[name] or 0) * value for name, value in DENOMINATIONS) + (
                rec.coins_amount or 0.0
            )
            if rec.supervisor_variance_approved_by:
                rec.message_post(
                    body="Recount submitted: the variance approval by %s is void."
                    % rec.supervisor_variance_approved_by.name
                )
            if rec.approval_state in ("pending", "approved"):
                # A02 audit B1: the request covered the previous count
                rec._approval_void("a recount was submitted")
            rec._guarded().write(
                {
                    "state": "counting",
                    "closing_counted": denom_total,
                    "blind_count_submitted": True,
                    "counted_by": self.env.uid,
                    "counted_at": fields.Datetime.now(),
                    "supervisor_variance_approved_by": False,
                    "variance_approved_amount": 0.0,
                    "variance_approved_at": False,
                }
            )
        return True

    def action_confirm_closed(self):
        """Confirming the count closes the shift (variance frozen); reconcile
        then stamps the outcome. BRU-FRD-02: no close without a count."""
        self._fd_require_cashier("confirm a cash count")
        for rec in self:
            if rec.state != "counting":
                raise UserError(
                    "Only shifts in counting can be confirmed closed (current: %s)." % rec.state
                )
            if not rec.blind_count_submitted:
                raise UserError(
                    "Submit the blind denomination count before closing shift #%s "
                    "(BRU-FRD-02)." % rec.id
                )
            rec._guarded().write({"state": "closed", "closed_at": fields.Datetime.now()})

    def action_approve_variance(self):
        """A02 audit M04-2: a variance beyond tolerance is approved by a Branch
        Manager who did not handle the cash. The approval is stamped from the
        acting user and pinned to the variance it saw. A02 audit B1: it runs
        only from the manager's M63 inbox (Request Approval routes it)."""
        self._approval_assert_routed()
        self._fd_require_group(GROUP_MANAGER, "Branch Manager", "approve a cash variance")
        self._fd_require_independent("approve the variance of")
        tolerance = self._fd_tolerance()
        for rec in self:
            if rec.state not in ("counting", "closed") or not rec.blind_count_submitted:
                raise UserError(
                    "Shift #%s has no submitted count to approve. The cashier submits "
                    "the blind count first." % rec.id
                )
            if abs(rec.variance) <= tolerance:
                raise UserError(
                    "The variance on shift #%s (BDT %.2f) is within the BDT %.2f "
                    "tolerance and needs no approval." % (rec.id, rec.variance, tolerance)
                )
            rec._guarded().write(
                {
                    "supervisor_variance_approved_by": self.env.uid,
                    "variance_approved_amount": rec.variance,
                    "variance_approved_at": fields.Datetime.now(),
                }
            )
            rec.message_post(
                body="Variance of BDT %.2f approved by %s." % (rec.variance, self.env.user.name)
            )
        return True

    def action_reconcile(self):
        """Complete the reconciliation (T07: end-of-shift report, Bengali-first).

        A02 audit M04-2/-6/-7: only a counted shift reconciles; the reconciler
        is a Branch Manager who did not handle the cash (BRU-FRD-11); a
        variance beyond tolerance needs an approval of exactly that variance
        (BRU-FRD-03), so a total shortage cannot land in "discrepancy" unseen."""
        self._fd_require_group(GROUP_MANAGER, "Branch Manager", "reconcile a cash shift")
        self._fd_require_independent("reconcile")
        tolerance = self._fd_tolerance()
        for rec in self:
            if rec.state not in ("counting", "closed"):
                raise ValidationError("Only a shift being counted can be reconciled.")
            if not rec.blind_count_submitted:
                raise UserError(
                    "Shift #%s has no count. The cashier submits the blind denomination "
                    "count before the shift can be reconciled (BRU-FRD-02)." % rec.id
                )
            if abs(rec.variance) > tolerance:
                approved = rec.supervisor_variance_approved_by
                if not approved or abs(rec.variance_approved_amount - rec.variance) > 0.005:
                    raise ValidationError(
                        f"FLAW-04.2 Blind Cash Count Gate: Variance of BDT {rec.variance:.2f} "
                        f"exceeds BDT {tolerance:.2f}. A Branch Manager must approve this "
                        "variance before reconciliation."
                    )
            now = fields.Datetime.now()
            rec._guarded().write(
                {
                    "closed_at": rec.closed_at or now,
                    "state": "reconciled" if abs(rec.variance) < 0.01 else "discrepancy",
                    "reconciled_by": self.env.uid,
                    "reconciled_at": now,
                }
            )
            # A02 audit B2: a literal publish() so FF-48 sees the event
            publish(
                self.env,
                "shift.closed",
                "fix.cash.shift",
                rec.id,
                {
                    "shift_id": rec.id,
                    "branch": rec.branch_id.name,
                    "variance": rec.variance,
                    "currency": rec.currency_id.name,
                },
            )
