# The cash drawer's movement ledger (FR-FRD-015, T-06, BRU-FRD-09).
#
# M04 build, 13 Nov 2026: a shift carried four running totals (payments,
# refunds, advances, field cash) and nothing said which sale, refund or
# settlement made them up, so a variance could not be traced to a movement.
# "Cash Advances" was subtracted from the expected cash, yet nothing could
# ever post one: a safe drop or a petty expense paid from the drawer left an
# unexplained shortage. Every posting now writes a ledger row (append-only:
# a correction is a new movement, T-06), and a cashier records a cash-out
# with its reason; a petty expense above the threshold and a staff advance
# need a Branch Manager who did not record it (BRU-FRD-09, BRU-FRD-11).
#
# The branch petty-cash FUND is M50's imprest (fix.imprest.*); this ledger is
# the counter drawer only.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_cash_shift import GROUP_CASHIER, GROUP_MANAGER

PETTY_LIMIT_PARAM = "cd_front_desk.petty_expense_approval_bdt"
DEFAULT_PETTY_LIMIT = 500.0
MANUAL_TYPES = ("safe_drop", "petty_expense", "staff_advance")


class FixCashMovement(models.Model):
    """One movement of cash into or out of a counter drawer."""

    _name = "fix.cash.movement"
    _description = "Cash Drawer Movement"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(compute="_compute_name", store=True, string="Movement")
    shift_id = fields.Many2one(
        "fix.cash.shift", string="Cash Shift", required=True, index=True, ondelete="restrict"
    )
    company_id = fields.Many2one(related="shift_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="shift_id.operating_unit_id", store=True, index=True
    )
    branch_id = fields.Many2one(related="shift_id.branch_id", store=True, index=True)
    currency_id = fields.Many2one(related="shift_id.currency_id")
    movement_type = fields.Selection(
        [
            ("receipt", "Cash Receipt"),
            ("refund", "Cash Refund"),
            ("field_cash", "Field Cash Handed In"),
            ("safe_drop", "Safe Drop / Transfer Out"),
            ("petty_expense", "Petty Expense Paid From Drawer"),
            ("staff_advance", "Staff Cash Advance"),
        ],
        string="Type",
        required=True,
        default="safe_drop",
    )
    direction = fields.Selection(
        [("in", "Into Drawer"), ("out", "Out of Drawer")],
        compute="_compute_direction",
        store=True,
    )
    amount = fields.Monetary(currency_field="currency_id", required=True)
    reason = fields.Char(string="Reason / Payee", help="What the cash was for, or who received it.")
    reference = fields.Char(string="Source Document", readonly=True)
    receipt_attachment_id = fields.Many2one("ir.attachment", string="Voucher / Receipt Scan")
    state = fields.Selection(
        [
            ("draft", "Recorded"),
            ("approved", "Approved"),
            ("posted", "Posted"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    recorded_by_id = fields.Many2one(
        "res.users", string="Recorded By", default=lambda self: self.env.user, readonly=True
    )
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True)
    posted_at = fields.Datetime(readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "reference",
            "recorded_by_id",
            "approved_by_id",
            "posted_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(rec.state != "draft" for rec in self):
            return locked | {
                "shift_id",
                "movement_type",
                "amount",
                "reason",
                "receipt_attachment_id",
            }
        return locked

    @api.depends("movement_type", "shift_id")
    def _compute_name(self):
        types = dict(self._fields["movement_type"].selection)
        for rec in self:
            rec.name = "%s #%s" % (types.get(rec.movement_type, ""), rec.id or "")

    @api.depends("movement_type")
    def _compute_direction(self):
        for rec in self:
            rec.direction = "in" if rec.movement_type in ("receipt", "field_cash") else "out"

    @api.constrains("amount")
    def _check_amount(self):
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError("A cash movement is a positive amount.")

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            for vals in vals_list:
                if vals.get("movement_type", "safe_drop") not in MANUAL_TYPES:
                    raise UserError(
                        "Receipts, refunds and field cash are written by the sale, refund or "
                        "settlement that moved the money, never typed."
                    )
                if not (vals.get("reason") or "").strip():
                    raise UserError("Say what the cash left the drawer for (reason / payee).")
        return super().create(vals_list)

    def write(self, vals):
        if not self._fix_guard_open():
            locked = {"shift_id", "movement_type", "amount", "reason", "receipt_attachment_id"}
            if self.filtered(lambda r: r.state != "draft") and locked & set(vals):
                raise UserError(
                    "A posted or approved cash movement is not changed: record a new movement "
                    "that corrects it (T-06)."
                )
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError("Cash movements are never deleted: cancel a draft instead (T-06).")
        return super().unlink()

    # ------------------------------------------------------------ rules

    def _fd_has(self, *groups) -> bool:
        return self.env.su or any(self.env.user.has_group(g) for g in groups)

    def _fd_petty_limit(self) -> float:
        raw = self.env["ir.config_parameter"].sudo().get_param(PETTY_LIMIT_PARAM)
        try:
            return float(raw) if raw not in (None, "", False) else DEFAULT_PETTY_LIMIT
        except ValueError:
            return DEFAULT_PETTY_LIMIT

    def _fd_needs_approval(self) -> bool:
        self.ensure_one()
        if self.movement_type == "staff_advance":
            return True
        return self.movement_type == "petty_expense" and self.amount > self._fd_petty_limit()

    # ------------------------------------------------------------ transitions

    def action_approve(self):
        """A Branch Manager who did not record the cash-out approves it."""
        if not self._fd_has(GROUP_MANAGER):
            raise UserError("Only a Branch Manager approves a cash-out.")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Movement %s is not waiting for approval." % rec.name)
            if not rec._fd_needs_approval():
                raise UserError("Movement %s needs no approval: post it." % rec.name)
            if rec.recorded_by_id == self.env.user and not self.env.su:
                raise UserError(
                    "You recorded movement %s: another Branch Manager approves it (BRU-FRD-11)."
                    % rec.name
                )
            rec._guarded().write({"state": "approved", "approved_by_id": self.env.uid})
        return True

    def action_post(self):
        """Take the cash out of the open drawer: the expected closing drops."""
        if not self._fd_has(GROUP_CASHIER, GROUP_MANAGER):
            raise UserError("Only a Front Desk Cashier posts a cash-out.")
        for rec in self:
            if rec.movement_type not in MANUAL_TYPES:
                raise UserError("Movement %s is posted by its source document." % rec.name)
            if rec.state == "draft" and rec._fd_needs_approval():
                limit = rec._fd_petty_limit()
                raise UserError(
                    "Movement %s needs a Branch Manager's approval first (%s)."
                    % (
                        rec.name,
                        "a staff advance"
                        if rec.movement_type == "staff_advance"
                        else "a petty expense above BDT %.2f, BRU-FRD-09" % limit,
                    )
                )
            if rec.state not in ("draft", "approved"):
                raise UserError("Movement %s is already %s." % (rec.name, rec.state))
            rec.shift_id._post_cash_movement("cash_advances", rec.amount, movement=rec)
        return True

    def action_cancel(self):
        for rec in self:
            if rec.state not in ("draft", "approved"):
                raise UserError(
                    "Movement %s is posted: correct it with a new movement (T-06)." % rec.name
                )
            rec._guarded().write({"state": "cancelled"})
        return True
