# cd_ap_ext — retention money withheld from sub-contractors
# (FR-APE-027 P1, BRU-APE-20 H; spec M52 §10.1 entity `fix.ap.retention`).
#
# A vendor bill states a retention percentage (fix_ap_ext.retention_percent);
# the bill's posting credits `retention_payable` for the withheld amount and
# the vendor's payable — and so the payables ageing — excludes it. This model
# is the register of what is held: one row per bill, with the scheduled
# release date and the contractual condition.
#
# Release is maker-checker, never a plain write and never on request alone
# (BRU-APE-20):
#   held -> release_requested (an accountant asks)
#        -> released          (an Accounting Administrator who did not ask
#                              releases, on the scheduled date or on certified
#                              completion with the certificate reference filed)
# The release posts Dr retention payable / Cr the configured payment bank
# journal's account — the module's payment convention (M50 pays out of the
# bank journal configured in cd_ap_ext.payment_journal_code). No guessed
# account: the role fails closed naming its parameter.
from odoo import api, fields, models
from odoo.addons.cd_cash_position.models.treasury_common import require_other_person
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

from .ap_gl import ap_account, ap_journal, post_ap_move
from .fix_ap_controls import require_finance
from .fix_ap_ext import _q


class FixApRetention(models.Model):
    """Retention withheld from a sub-contractor's bill, and its release."""

    _name = "fix.ap.retention"
    _description = "AP Retention Withheld"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "release_due_date, id"

    name = fields.Char(readonly=True, copy=False, default="New", index=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", index=True)
    vendor_id = fields.Many2one(
        "res.partner", string="Sub-contractor", required=True, index=True, ondelete="restrict"
    )
    invoice_id = fields.Many2one(
        "fix.vendor.invoice",
        string="Vendor Bill",
        required=True,
        index=True,
        ondelete="restrict",
        readonly=True,
    )
    invoice_ref = fields.Char(string="Bill Reference", readonly=True, copy=False)
    contract_ref = fields.Char(
        string="Contract Reference",
        help="The sub-contract whose retention terms this withholding applies.",
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.company.currency_id
    )
    withheld_amount = fields.Monetary(
        string="Withheld", currency_field="currency_id", readonly=True, copy=False
    )
    released_amount = fields.Monetary(
        string="Released", currency_field="currency_id", readonly=True, copy=False, default=0.0
    )
    balance = fields.Monetary(
        string="Still Held",
        currency_field="currency_id",
        compute="_compute_balance",
        store=True,
    )
    release_due_date = fields.Date(
        string="Release Due",
        readonly=True,
        copy=False,
        help="BRU-APE-20: the scheduled date the retention becomes releasable.",
    )
    release_condition = fields.Selection(
        [
            ("scheduled", "Scheduled date"),
            ("certified", "Certified completion"),
        ],
        string="Release Condition",
        default="scheduled",
        required=True,
        help="Scheduled date, or certified completion recorded by the project/contract owner.",
    )
    certificate_ref = fields.Char(
        string="Completion Certificate Ref",
        help="The completion certificate that releases retention before its scheduled date "
        "(BRU-APE-20).",
    )
    state = fields.Selection(
        [
            ("held", "Held"),
            ("release_requested", "Release Requested"),
            ("released", "Released"),
        ],
        default="held",
        required=True,
        tracking=True,
        index=True,
    )
    release_requested_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    release_requested_at = fields.Datetime(readonly=True, copy=False)
    released_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    released_at = fields.Datetime(readonly=True, copy=False)
    release_move_id = fields.Many2one(
        "account.move", string="Release Entry", readonly=True, copy=False
    )
    note = fields.Text()
    age_days = fields.Integer(string="Days Past Due", compute="_compute_age")
    due_state = fields.Selection(
        [
            ("scheduled", "Scheduled"),
            ("due", "Due"),
            ("overdue", "Overdue"),
            ("released", "Released"),
        ],
        compute="_compute_age",
        string="Position",
    )

    TERMS = (
        "company_id",
        "operating_unit_id",
        "vendor_id",
        "invoice_id",
        "contract_ref",
        "currency_id",
        "withheld_amount",
        "release_due_date",
    )
    WORKFLOW = (
        "state",
        "released_amount",
        "release_requested_by_id",
        "release_requested_at",
        "released_by_id",
        "released_at",
        "release_move_id",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"name"} | set(self.TERMS) | set(self.WORKFLOW)

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(rec.state != "held" for rec in self):
            locked |= set(self.TERMS) | {"release_condition", "certificate_ref"}
        return locked

    @api.depends("withheld_amount", "released_amount")
    def _compute_balance(self):
        for rec in self:
            rec.balance = _q((rec.withheld_amount or 0.0) - (rec.released_amount or 0.0))

    @api.depends("release_due_date", "state")
    def _compute_age(self):
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.state == "released":
                rec.age_days = 0
                rec.due_state = "released"
                continue
            days = (today - rec.release_due_date).days if rec.release_due_date else 0
            rec.age_days = max(days, 0)
            if days > 0:
                rec.due_state = "overdue"
            elif days == 0:
                rec.due_state = "due"
            else:
                rec.due_state = "scheduled"

    @api.constrains("withheld_amount", "released_amount")
    def _check_amounts(self):
        for rec in self:
            if rec.withheld_amount is not None and rec.withheld_amount < 0:
                raise ValidationError(
                    "Retention %s: the withheld amount cannot be negative." % rec.name
                )
            if (rec.released_amount or 0.0) > (rec.withheld_amount or 0.0) + 1e-6:
                raise ValidationError("Retention %s: released more than was withheld." % rec.name)

    @api.model_create_multi
    def create(self, vals_list):
        # only the bill's own posting creates the withholding (it is the
        # figure the posted GL entry credits); a typed row would be a payment
        # without a bill.
        if not self.env.su:
            raise UserError(
                "Retention rows are recorded by the vendor bill's posting, never typed."
            )
        for vals in vals_list:
            if not vals.get("invoice_id"):
                raise UserError(
                    "Retention is withheld on a vendor bill: create it from the bill's posting."
                )
        recs = super().create(vals_list)
        for rec in recs:
            if rec.name in (False, "New"):
                rec._guarded().write(
                    {
                        "name": self.env["ir.sequence"].sudo().next_by_code("fix.ap.retention")
                        or "RET/New"
                    }
                )
        return recs

    def write(self, vals):
        if set(self.TERMS) & set(vals) and not self._fix_guard_open():
            raise UserError(
                "Retention %s is withheld evidence: its bill, sub-contractor and amount do not "
                "change. Release it through the approved action." % ", ".join(self.mapped("name"))
            )
        if self and not self._fix_guard_open():
            for rec in self:
                if rec.state == "released" and (
                    {"release_condition", "certificate_ref", "note"} & set(vals)
                ):
                    changed = [
                        name
                        for name in {"release_condition", "certificate_ref", "note"} & set(vals)
                        if rec._fix_guard_differs(name, vals[name], rec[name])
                    ]
                    if changed:
                        raise UserError("Retention %s is released: its record is final." % rec.name)
        return super().write(vals)

    def unlink(self):
        raise UserError(
            "Retention rows are released through the approved action, never deleted: they "
            "are the withholding evidence."
        )

    # ------------------------------------------------------------- workflow --
    def action_request_release(self):
        """The first person asks for the release; a second person approves it."""
        require_finance(self.env, "Requesting a retention release")
        for rec in self:
            if rec.state != "held":
                raise UserError("Retention %s is %s." % (rec.name, rec.state))
            if (
                rec.release_due_date
                and rec.release_due_date > fields.Date.context_today(rec)
                and (
                    rec.release_condition != "certified" or not (rec.certificate_ref or "").strip()
                )
            ):
                raise UserError(
                    "BRU-APE-20: retention %s is not due until %s and no certified "
                    "completion is recorded: it is released on the scheduled date or on "
                    "certified completion, never on request alone."
                    % (rec.name, rec.release_due_date)
                )
            rec._guarded().write(
                {
                    "state": "release_requested",
                    "release_requested_by_id": self.env.uid,
                    "release_requested_at": fields.Datetime.now(),
                }
            )
            rec.message_post(body="Release requested by %s." % self.env.user.name)
        return True

    def action_release(self):
        """An Accounting Administrator who did not ask releases the retention.
        BRU-APE-20: only on the scheduled date, or on certified completion
        with its certificate reference."""
        require_finance(self.env, "Releasing retention", manager=True)
        for rec in self:
            if rec.state != "release_requested":
                raise UserError(
                    "Retention %s is %s: request its release first." % (rec.name, rec.state)
                )
            require_other_person(
                self.env,
                rec.release_requested_by_id
                | rec.invoice_id.sudo().create_uid
                | rec.invoice_id.sudo().submitted_by,
                "Releasing retention %s" % rec.name,
            )
            today = fields.Date.context_today(rec)
            certified = rec.release_condition == "certified" and bool(
                (rec.certificate_ref or "").strip()
            )
            if rec.release_due_date and rec.release_due_date > today and not certified:
                raise UserError(
                    "BRU-APE-20: retention %s is due on %s; it is not released early without "
                    "a certified completion recorded on it." % (rec.name, rec.release_due_date)
                )
            if certified and not (rec.certificate_ref or "").strip():
                raise UserError("BRU-APE-20: certified completion needs its certificate reference.")
            amount = _q(rec.balance)
            if amount <= 0:
                raise UserError("Retention %s has no balance to release." % rec.name)
            company = rec.company_id
            partner = rec.vendor_id.commercial_partner_id
            account = ap_account(self.env, company, "retention_payable")
            journal = ap_journal(self.env, company, "payment")
            label = "Retention released %s %s" % (rec.name, partner.name)
            lines = [
                (account, label, amount, 0.0, partner),
                (journal.default_account_id, label, 0.0, amount, partner),
            ]
            move = post_ap_move(
                self.env,
                company,
                journal,
                today,
                label,
                lines,
                rec.operating_unit_id,
            )
            rec._guarded().write(
                {
                    "state": "released",
                    "released_amount": _q((rec.released_amount or 0.0) + amount),
                    "released_by_id": self.env.uid,
                    "released_at": fields.Datetime.now(),
                    "release_move_id": move.id,
                }
            )
            rec.message_post(
                body="Released BDT %.2f by %s (entry %s)." % (amount, self.env.user.name, move.name)
            )
            publish(
                self.env,
                "ap.retention_released",
                "fix.ap.retention",
                rec.id,
                {
                    "retention": rec.name,
                    "invoice": rec.invoice_ref,
                    "vendor_id": partner.id,
                    "amount": amount,
                    "move_id": move.id,
                },
            )
        return True

    def action_reject_release(self):
        """A manager sends a release request back to held (the retention stays)."""
        require_finance(self.env, "Rejecting a retention release", manager=True)
        for rec in self:
            if rec.state != "release_requested":
                raise UserError("Retention %s has no open release request." % rec.name)
            require_other_person(
                self.env, rec.release_requested_by_id, "Rejecting a retention release"
            )
            rec._guarded().write(
                {
                    "state": "held",
                    "release_requested_by_id": False,
                    "release_requested_at": False,
                }
            )
            rec.message_post(body="Release request rejected by %s." % self.env.user.name)
        return True
