# fix.sod.mitigation — the SoD exception (FR-SEC-024, BRU-SEC-07).
#
# "Permit a time-boxed, CFO- or CTO-approved exception with a mitigating
# control, and present all live exceptions on a standing quarterly report."
# A grant that creates a conflicting combination passes only while an
# APPROVED exception for that user and control is inside its validity window.
# The approver holds the SoD Exception Approver group (the CFO / CTO
# appointment, shipped empty), is not the grantee and not the requester; the
# window is at most `cd_rbac_ext.sod_exception_max_days` days (default 92,
# one quarter: the FR-SEC-024 report cycle). State, approver and decision time
# are guarded; the pinned terms cannot change once approved.
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

MAX_DAYS_KEY = "cd_rbac_ext.sod_exception_max_days"
MAX_DAYS_DEFAULT = 92
APPROVER_GROUP = "cd_rbac_ext.group_fix_sod_exception_approver"


class FixSodMitigation(models.Model):
    _name = "fix.sod.mitigation"
    _description = "SoD Exception (Mitigating Control)"
    _inherit = ["fix.guarded.mixin", "mail.thread"]
    _order = "valid_until desc, id desc"

    name = fields.Char(required=True, default="New", copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    control_id = fields.Many2one(
        "fix.sod.control", string="SoD Control", required=True, index=True, ondelete="cascade"
    )
    user_id = fields.Many2one(
        "res.users", string="Grantee", required=True, index=True, ondelete="cascade"
    )
    mitigating_control = fields.Text(
        required=True,
        help="The compensating control that runs while the exception lasts "
        "(e.g. weekly independent review of every payment the user released).",
    )
    reason = fields.Text(required=True)
    valid_from = fields.Date(required=True, default=fields.Date.context_today)
    valid_until = fields.Date(required=True)
    requested_by_id = fields.Many2one(
        "res.users", string="Requested By", default=lambda self: self.env.user, readonly=True
    )
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True)
    decided_on = fields.Datetime(readonly=True)
    state = fields.Selection(
        [
            ("draft", "Requested"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("revoked", "Revoked"),
        ],
        required=True,
        default="draft",
        tracking=True,
    )
    is_live = fields.Boolean(compute="_compute_is_live", string="Live")

    _PINNED = ("control_id", "user_id", "valid_from", "valid_until", "mitigating_control")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "approved_by_id",
            "decided_on",
            "requested_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= set(self._PINNED) | {"reason", "company_id"}
        return locked

    @api.depends("state", "valid_from", "valid_until")
    def _compute_is_live(self):
        # M29-D2: the Dhaka calendar, not the UTC date the sudo/cron env
        # would give (the 884ddf8f bug class): between 00:00 and 06:00 Dhaka
        # an exception whose window just ended was still waiving blocks.
        from .fix_access_ops import local_today

        today = local_today(self)
        for rec in self:
            rec.is_live = bool(
                rec.state == "approved"
                and rec.valid_from
                and rec.valid_until
                and rec.valid_from <= today <= rec.valid_until
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.sod.mitigation") or "SODX/New"
                )
            if not self.env.su:
                vals["requested_by_id"] = self.env.user.id
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.su and not self._fix_guard_has_token():
            if not self.env.user.has_group("base.group_system"):
                for rec in self:
                    if rec.requested_by_id != self.env.user:
                        raise UserError("Only the requester can edit SoD exception %s." % rec.name)
            pinned = set(self._PINNED) | {"reason", "company_id"}
            for rec in self:
                if rec.state != "draft" and pinned & set(vals):
                    changed = [
                        n for n in pinned & set(vals) if rec._fix_guard_differs(n, vals[n], rec[n])
                    ]
                    if changed:
                        raise UserError(
                            "SoD exception %s is %s: its terms (%s) cannot change. Request a "
                            "new exception." % (rec.name, rec.state, ", ".join(sorted(changed)))
                        )
        return super().write(vals)

    @api.constrains("valid_from", "valid_until")
    def _check_window(self):
        max_days = self._fix_max_days()
        for rec in self:
            if rec.valid_until < rec.valid_from:
                raise ValidationError("An SoD exception must end on or after its start date.")
            if (rec.valid_until - rec.valid_from).days > max_days:
                raise ValidationError(
                    "An SoD exception is time-boxed to at most %d days (%s); request a new one "
                    "at the next review." % (max_days, MAX_DAYS_KEY)
                )

    @api.model
    def _fix_max_days(self):
        raw = self.env["ir.config_parameter"].sudo().get_param(MAX_DAYS_KEY)
        try:
            value = int(raw) if raw else MAX_DAYS_DEFAULT
        except (TypeError, ValueError):
            value = MAX_DAYS_DEFAULT
        return max(1, value)

    @api.model
    def _fix_valid_for(self, control, user):
        """Approved exceptions covering `user` × `control` today."""
        # M29-D2: Dhaka-calendar window (this runs inside sudo grant paths
        # where context_today would fall back to the UTC date).
        from .fix_access_ops import local_today

        today = local_today(self)
        return self.sudo().search(
            [
                ("control_id", "=", control.id),
                ("user_id", "=", user.id),
                ("state", "=", "approved"),
                ("valid_from", "<=", today),
                ("valid_until", ">=", today),
                ("approved_by_id", "!=", user.id),
            ],
            order="valid_until desc",
        )

    def _fix_assert_approver(self):
        approver = self.env.user
        if not approver.has_group(APPROVER_GROUP):
            raise AccessError(
                "Only an SoD Exception Approver (the CFO / CTO appointment, FR-SEC-024) can "
                "decide an SoD exception."
            )
        for rec in self:
            if approver == rec.user_id:
                raise UserError("The grantee cannot approve their own SoD exception.")
            if approver == rec.requested_by_id:
                raise UserError("The requester cannot approve the SoD exception they requested.")

    def action_approve(self):
        self._fix_assert_approver()
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.state != "draft":
                raise UserError("Approve a requested SoD exception")
            if rec.valid_until < today:
                raise UserError("This SoD exception has already expired; request a new one.")
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": self.env.user.id,
                    "decided_on": fields.Datetime.now(),
                }
            )
            self.env["fix.sod.control"]._fix_log_sod_event(
                rec.user_id,
                "exception",
                "%s approved for %s until %s" % (rec.name, rec.control_id.code, rec.valid_until),
            )

    def action_reject(self):
        self._fix_assert_approver()
        for rec in self:
            if rec.state != "draft":
                raise UserError("Reject a requested SoD exception")
            rec._guarded().write(
                {
                    "state": "rejected",
                    "approved_by_id": self.env.user.id,
                    "decided_on": fields.Datetime.now(),
                }
            )

    def action_revoke(self):
        """Ends an approved exception early. The conflict it covered then shows as
        unmitigated on the violation report until the access is removed."""
        if not (
            self.env.user.has_group(APPROVER_GROUP) or self.env.user.has_group("base.group_system")
        ):
            raise AccessError("Only an SoD Exception Approver or an administrator can revoke.")
        for rec in self:
            if rec.state != "approved":
                raise UserError("Only an approved SoD exception can be revoked")
            rec._guarded().write({"state": "revoked", "decided_on": fields.Datetime.now()})
