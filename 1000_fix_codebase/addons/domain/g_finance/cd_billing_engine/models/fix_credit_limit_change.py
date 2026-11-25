# fix.credit.limit.change — the approval-controlled credit limit (M33 capture
# audit pass 2, 2026-11-19; M33 FR-CPM-047, BRU-CPM-12 hard block, SOD-04).
#
# Before: fix.credit.profile.credit_limit was a plain field. Any user who
# could edit the profile (its M33 / M20 form, or the inline limit box on the
# AR credit-control table) changed a customer's limit with no approval and no
# record of who asked. The spec: "Credit limit changes require Finance
# Manager approval and are fully audited"; "Credit limit approval cannot be
# performed by the person who requested it".
#
# Now a limit changes only through an approved change request. A new profile
# starts at 0, unless the superuser (a migration, a seed) creates it.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_ar_engine import FixCreditProfile as _BaseProfile  # noqa: F401  (load order)
from .fix_finance_approval import GROUP_ADMINISTRATOR, require_role

_LIMIT_TOKEN = object()
_LIMIT_KEY = "fix_credit_limit_change"


class FixCreditProfileLimit(models.Model):
    _inherit = "fix.credit.profile"
    # the change form picks a profile: show its customer, not "fix.credit.profile,7"
    _rec_name = "customer_id"

    limit_change_ids = fields.One2many(
        "fix.credit.limit.change", "profile_id", string="Limit Changes"
    )

    def _fix_limit_open(self) -> bool:
        return self.env.su or self.env.context.get(_LIMIT_KEY) is _LIMIT_TOKEN

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_limit_open():
            for vals in vals_list:
                if float(vals.get("credit_limit") or 0.0) > 0.0:
                    raise UserError(
                        "A new credit profile starts with no limit. Raise a Credit Limit "
                        "Change for the Finance Manager to approve (BRU-CPM-12)."
                    )
        return super().create(vals_list)

    def write(self, vals):
        if "credit_limit" in vals and not self._fix_limit_open():
            new = float(vals["credit_limit"] or 0.0)
            if any(abs(new - (p.credit_limit or 0.0)) > 0.005 for p in self):
                raise UserError(
                    "A credit limit changes only through an approved Credit Limit Change "
                    "(BRU-CPM-12: Finance Manager approval, never by the requester)."
                )
        return super().write(vals)


class FixCreditLimitChange(models.Model):
    """A request to change one customer's credit limit, decided by a
    Finance Manager who did not raise it."""

    _name = "fix.credit.limit.change"
    _description = "Credit Limit Change"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "current_limit",
            "decided_by",
            "decided_at",
            "decision_note",
            "applied_at",
        }

    name = fields.Char(string="Reference", compute="_compute_name", store=True)
    profile_id = fields.Many2one(
        "fix.credit.profile",
        string="Credit Profile",
        required=True,
        index=True,
        ondelete="restrict",
    )
    customer_id = fields.Many2one(
        related="profile_id.customer_id", store=True, string="Customer", index=True
    )
    company_id = fields.Many2one(related="profile_id.company_id", store=True, index=True)
    currency_id = fields.Many2one(related="profile_id.currency_id")
    current_limit = fields.Monetary(
        string="Limit When Requested", currency_field="currency_id", readonly=True
    )
    proposed_limit = fields.Monetary(
        string="Proposed Limit", currency_field="currency_id", required=True
    )
    reason = fields.Text(string="Why", required=True)
    state = fields.Selection(
        [
            ("submitted", "Awaiting Finance Manager"),
            ("approved", "Approved and Applied"),
            ("rejected", "Rejected"),
            ("cancelled", "Withdrawn"),
        ],
        string="State",
        default="submitted",
        required=True,
        tracking=True,
    )
    requested_by = fields.Many2one(
        "res.users", string="Requested By", default=lambda self: self.env.user, readonly=True
    )
    decided_by = fields.Many2one("res.users", string="Decided By", readonly=True)
    decided_at = fields.Datetime(string="Decided At", readonly=True)
    decision_note = fields.Char(string="Decision Note", readonly=True)
    applied_at = fields.Datetime(string="Applied At", readonly=True)

    @api.depends("customer_id", "proposed_limit")
    def _compute_name(self):
        for rec in self:
            rec.name = "CLC/%s/%s" % (rec.id or "new", rec.customer_id.display_name or "")

    @api.model_create_multi
    def create(self, vals_list):
        Profile = self.env["fix.credit.profile"]
        for vals in vals_list:
            # M20-F7: profile reads are finance-only now, but the ladder is
            # raised by any internal user (its own ACL) — the snapshot the
            # audit trail needs is taken as the trusted service, so a
            # non-finance requester can still raise the change the Finance
            # Manager decides.
            profile = Profile.sudo().browse(vals.get("profile_id"))
            if not profile.exists():
                raise ValidationError("Choose the credit profile to change.")
            vals["current_limit"] = profile.credit_limit
            if not self.env.su:
                vals["requested_by"] = self.env.uid
            if self.search_count([("profile_id", "=", profile.id), ("state", "=", "submitted")]):
                raise UserError(
                    "%s already has a limit change awaiting decision."
                    % profile.customer_id.display_name
                )
        records = super(FixCreditLimitChange, self._guarded()).create(vals_list)
        # hand back the records WITHOUT the transition token create used
        return self.browse(records.ids)

    def write(self, vals):
        moving = {"profile_id", "proposed_limit", "reason"} & set(vals)
        if moving and not self._fix_guard_open() and any(r.state != "submitted" for r in self):
            raise UserError("A decided limit change is a record; raise a new one.")
        return super().write(vals)

    @api.constrains("proposed_limit")
    def _check_limit(self):
        for rec in self:
            if rec.proposed_limit < 0:
                raise ValidationError("A credit limit cannot be negative.")
            if rec.state == "submitted" and abs(rec.proposed_limit - rec.current_limit) < 0.005:
                raise ValidationError("The proposed limit is the limit already in force.")

    def _decide(self, approve: bool, note):
        require_role(
            self.env,
            GROUP_ADMINISTRATOR,
            "Deciding a credit limit change",
        )
        now = fields.Datetime.now()
        for rec in self:
            if rec.state != "submitted":
                raise UserError("%s is already %s." % (rec.name, rec.state))
            if not self.env.su and rec.requested_by == self.env.user:
                raise UserError(
                    "Segregation of duties (SOD-04): you requested this change; another "
                    "Finance Manager decides it."
                )
            # SOD-08 (M20 §13 / M20-F8): whoever CREATED the customer record
            # never decides its credit limit — the maker-checker pair the
            # spec names beyond the requester. The creator stamp is the
            # partner's own create_uid (the M33 master's), read on the live
            # profile link, and trusted code (su) is exempt as everywhere.
            creator = rec.profile_id.customer_id.create_uid
            if not self.env.su and creator and creator == self.env.user:
                raise UserError(
                    "Segregation of duties (SOD-08): you created the customer record %s; "
                    "another Finance Manager decides its credit limit."
                    % rec.profile_id.customer_id.display_name
                )
            vals = {
                "state": "approved" if approve else "rejected",
                "decided_by": self.env.user.id,
                "decided_at": now,
                "decision_note": (note or "").strip() or False,
            }
            if approve:
                if abs(rec.profile_id.credit_limit - rec.current_limit) > 0.005:
                    raise UserError(
                        "The limit changed since this was requested (now %.2f). Reject "
                        "it and raise a new one." % rec.profile_id.credit_limit
                    )
                rec.profile_id.with_context(**{_LIMIT_KEY: _LIMIT_TOKEN}).write(
                    {"credit_limit": rec.proposed_limit}
                )
                vals["applied_at"] = now
                rec.profile_id.message_post(
                    body="Credit limit %.2f -> %.2f (requested by %s, approved by %s): %s"
                    % (
                        rec.current_limit,
                        rec.proposed_limit,
                        rec.requested_by.name,
                        self.env.user.name,
                        rec.reason,
                    )
                )
            rec._guarded().write(vals)
        return True

    def action_approve(self, note=None):
        return self._decide(True, note)

    def action_reject(self, note=None):
        if not (note or "").strip():
            raise ValidationError("Say why the change is rejected.")
        return self._decide(False, note)

    def action_cancel(self):
        for rec in self:
            if rec.state != "submitted":
                raise UserError("Only a change awaiting decision is withdrawn.")
            if not self.env.su and rec.requested_by != self.env.user:
                raise UserError("Only the requester withdraws a limit change.")
            rec._guarded().write({"state": "cancelled"})
        return True
