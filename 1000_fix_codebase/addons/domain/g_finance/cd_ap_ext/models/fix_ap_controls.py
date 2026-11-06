# cd_ap_ext — shared A08 M52 controls: configuration keys, the one-payment-
# per-bill lock, and dual control of the AP approval matrix.
#
# A08 audit (2026-11-04):
#   M52-4  a bill's payment_state written back to not_paid let a second run
#          pay it again (2 executions, 18,000 for a 9,000 bill). The lock
#          below is a row per bill payment with a UNIQUE index over the open
#          and paid rows: whatever a field says, the database refuses a
#          second live payment of the same bill (BRU-APE-10).
#   M52-12 one accounting manager re-pointed level 2 of the matrix to
#          base.group_user with no approval. Matrix rows now change only
#          through a change request confirmed by a second manager.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

GROUP_BILLING = "account.group_account_invoice"
GROUP_ACCOUNTANT = "account.group_account_user"
GROUP_MANAGER = "account.group_account_manager"
FINANCE_GROUPS = (GROUP_ACCOUNTANT, GROUP_MANAGER)

# --- configuration keys (documented defaults) -------------------------------
# Expense claims above this need an accounting manager (spec M52 §13 / module
# default since CD-M52-01: BDT 25,000).
PARAM_CLAIM_MANAGER_THRESHOLD = "cd_ap_ext.claim_manager_threshold"
DEFAULT_CLAIM_MANAGER_THRESHOLD = 25000.0
# Split-claim detection: an employee's live claims dated inside this rolling
# window are summed for the threshold (0 = off). Default 30 days, the same
# window A06 uses for split purchases (cd_requisition.split_window_days).
PARAM_CLAIM_SPLIT_DAYS = "cd_ap_ext.claim_split_window_days"
DEFAULT_CLAIM_SPLIT_DAYS = 30
# The claimant's line manager (hr.employee.parent_id with a login) approves
# before finance (spec M52 §8.2). "0" switches the step off.
PARAM_CLAIM_MANAGER_STEP = "cd_ap_ext.claim_line_manager_step"
# A higher matrix level's approver may sign a lower level (managers act on
# level 1) — one user still signs one level only. "0" switches it off.
PARAM_HIGHER_SIGNS_LOWER = "cd_ap_ext.higher_level_may_approve_lower"
# BRU-APE-16: every expense line names its cost centre at submission. "0" switches
# the refusal off (the posting then falls back to the default cost centre).
PARAM_CLAIM_REQUIRE_COST_CENTRE = "cd_ap_ext.claim_require_cost_centre"


def float_param(env, key, default):
    raw = env["ir.config_parameter"].sudo().get_param(key)
    if raw in (None, False, ""):
        return float(default)
    try:
        return float(raw)
    except (TypeError, ValueError):
        return float(default)


def bool_param(env, key, default=True):
    raw = env["ir.config_parameter"].sudo().get_param(key)
    if raw in (None, False, ""):
        return default
    return str(raw).strip().lower() not in ("0", "false", "no", "off")


def is_finance(env, user=None):
    user = user or env.user
    return any(user.has_group(g) for g in FINANCE_GROUPS)


def require_finance(env, what, manager=False):
    if env.su:
        return
    groups = (GROUP_MANAGER,) if manager else FINANCE_GROUPS
    if not any(env.user.has_group(g) for g in groups):
        raise UserError(
            "%s needs the %s role."
            % (what, "Accounting Administrator" if manager else "Accountant")
        )


class FixApBillPayment(models.Model):
    """One live payment of one bill (BRU-APE-10): the unique index makes a
    second open or paid payment of the same bill impossible."""

    _name = "fix.ap.bill.payment"
    _description = "AP Bill Payment Lock"
    _order = "id desc"

    _one_live_payment_per_bill = models.UniqueIndex(
        "(bill_id) WHERE state IN ('open', 'paid')",
        "This bill is already in flight or paid: it cannot be paid again (BRU-APE-10).",
    )

    company_id = fields.Many2one("res.company", required=True, index=True)
    bill_id = fields.Many2one(
        "fix.vendor.invoice", required=True, index=True, ondelete="restrict", readonly=True
    )
    run_line_id = fields.Many2one(
        "fix.payment.run.line", index=True, ondelete="set null", readonly=True
    )
    execution_id = fields.Many2one("fix.payment.execution", readonly=True)
    amount = fields.Float(readonly=True)
    state = fields.Selection(
        [("open", "In Flight"), ("paid", "Paid"), ("failed", "Failed / Returned")],
        required=True,
        default="open",
        index=True,
        readonly=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            raise UserError("Bill payment locks are written by the payment run only.")
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.su:
            raise UserError("Bill payment locks are written by the payment run only.")
        return super().write(vals)

    def unlink(self):
        raise UserError("Bill payment locks are evidence and cannot be deleted.")


class FixApApprovalRuleChange(models.Model):
    """A proposed change of one row of the AP approval matrix (M52-12): a
    manager proposes, a DIFFERENT manager confirms, and only the confirmation
    writes the matrix."""

    _name = "fix.ap.approval.rule.change"
    _description = "AP Approval Matrix Change"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    rule_id = fields.Many2one(
        "fix.ap.approval.rule",
        string="Matrix Row",
        help="Empty: the change adds a new row.",
        ondelete="cascade",
    )
    name = fields.Char(string="New Name")
    level = fields.Integer(string="New Level")
    amount_min = fields.Float(string="New Applies From (gross)")
    group_id = fields.Many2one("res.groups", string="New Approver Group")
    active = fields.Boolean(string="Row Active", default=True)
    reason = fields.Text(required=True)
    state = fields.Selection(
        [("proposed", "Proposed"), ("applied", "Applied"), ("rejected", "Rejected")],
        default="proposed",
        required=True,
        tracking=True,
    )
    proposed_by_id = fields.Many2one(
        "res.users", readonly=True, copy=False, default=lambda self: self.env.user
    )
    decided_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    decided_at = fields.Datetime(readonly=True, copy=False)

    TERMS = ("rule_id", "name", "level", "amount_min", "group_id", "active", "reason")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "decided_by_id",
            "decided_at",
            "proposed_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        # a change is fixed once proposed: it is created proposed
        locked = super()._fix_form_locked_fields()
        if self:
            locked |= set(self.TERMS)
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        require_finance(self.env, "Proposing an AP approval-matrix change", manager=True)
        Rule = self.env["fix.ap.approval.rule"].sudo()
        for vals in vals_list:
            vals.pop("proposed_by_id", None)
            if vals.get("rule_id"):
                # a change states the whole row: what is not changed is copied
                # (the workspace form omits what the person left empty)
                rule = Rule.browse(vals["rule_id"])
                vals.setdefault("company_id", rule.company_id.id)
                vals["name"] = vals.get("name") or rule.name
                vals["level"] = vals.get("level") or rule.level
                vals["group_id"] = vals.get("group_id") or rule.group_id.id
                vals.setdefault("amount_min", rule.amount_min)
                vals.setdefault("active", rule.active)
            elif not (vals.get("name") and vals.get("level") and vals.get("group_id")):
                raise ValidationError("A new matrix row needs a name, a level and a group.")
            # refused at the proposal, not after a second person has read it
            Rule._fix_assert_matrix_group(self.env["res.groups"].browse(vals["group_id"]))
        return super(FixApApprovalRuleChange, self._guarded()).create(
            [dict(v, proposed_by_id=self.env.uid) for v in vals_list]
        )

    def write(self, vals):
        if set(self.TERMS) & set(vals) and not self._fix_guard_open():
            raise UserError("A proposed matrix change is fixed; reject it and propose again.")
        return super().write(vals)

    def action_apply(self):
        require_finance(self.env, "Confirming an AP approval-matrix change", manager=True)
        Rule = self.env["fix.ap.approval.rule"].sudo()._fix_matrix_writing()
        for change in self:
            if change.state != "proposed":
                raise UserError("Only a proposed matrix change is confirmed.")
            if self.env.user in (change.proposed_by_id | change.create_uid):
                raise UserError(
                    "Segregation of duties: the proposer of a matrix change cannot confirm it."
                )
            vals = {
                "active": change.active,
                "name": change.name,
                "level": change.level,
                "group_id": change.group_id.id,
                "amount_min": change.amount_min,
            }
            if change.rule_id:
                Rule.browse(change.rule_id.id).write(vals)
            else:
                if not (change.name and change.level and change.group_id):
                    raise ValidationError("A new matrix row needs a name, a level and a group.")
                Rule.create(dict(vals, company_id=change.company_id.id))
            change._guarded().write(
                {
                    "state": "applied",
                    "decided_by_id": self.env.uid,
                    "decided_at": fields.Datetime.now(),
                }
            )
        return True

    def action_reject(self):
        require_finance(self.env, "Rejecting an AP approval-matrix change", manager=True)
        for change in self:
            if change.state != "proposed":
                raise UserError("Only a proposed matrix change is rejected.")
            change._guarded().write(
                {
                    "state": "rejected",
                    "decided_by_id": self.env.uid,
                    "decided_at": fields.Datetime.now(),
                }
            )
        return True
