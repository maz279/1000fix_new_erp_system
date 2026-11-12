# Branch announcements to counter staff (FR-FRD-031).
#
# M04 build, 13 Nov 2026: there was no way to publish a notice, target or
# procedure change to the counters; it travelled by phone and chat and nobody
# could say who had read it. An announcement is drafted, published by a
# Branch Manager to chosen branches (or all), shown while it is valid, and
# each counter user acknowledges it once.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

GROUP_MANAGER = "cd_front_desk.group_fd_branch_manager"


class FixBranchAnnouncement(models.Model):
    _name = "fix.branch.announcement"
    _description = "Branch Announcement"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "published_at desc, id desc"

    name = fields.Char(string="Title", required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    body = fields.Text(string="Message", required=True)
    kind = fields.Selection(
        [
            ("notice", "Notice"),
            ("target", "Target"),
            ("procedure", "Procedure Change"),
            ("emergency", "Emergency / Escalation"),
        ],
        string="Kind",
        default="notice",
        required=True,
    )
    branch_ids = fields.Many2many(
        "fix.branch", string="Branches", help="Leave empty to publish to every branch."
    )
    valid_from = fields.Date(string="Show From", default=fields.Date.context_today, required=True)
    valid_until = fields.Date(string="Show Until")
    state = fields.Selection(
        [("draft", "Draft"), ("published", "Published"), ("withdrawn", "Withdrawn")],
        default="draft",
        required=True,
        tracking=True,
    )
    published_by_id = fields.Many2one("res.users", string="Published By", readonly=True)
    published_at = fields.Datetime(readonly=True)
    ack_user_ids = fields.Many2many(
        "res.users",
        "fix_branch_announcement_ack_rel",
        "announcement_id",
        "user_id",
        string="Acknowledged By",
        readonly=True,
    )
    ack_count = fields.Integer(compute="_compute_ack", string="Acknowledged")
    is_current = fields.Boolean(
        compute="_compute_current", search="_search_current", string="Showing Now"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "published_by_id",
            "published_at",
            "ack_user_ids",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(rec.state != "draft" for rec in self):
            return locked | {"name", "body", "kind", "branch_ids", "valid_from"}
        return locked

    @api.depends("ack_user_ids")
    def _compute_ack(self):
        for rec in self:
            rec.ack_count = len(rec.ack_user_ids)

    def _compute_current(self):
        today = fields.Date.context_today(self)
        for rec in self:
            rec.is_current = (
                rec.state == "published"
                and rec.valid_from <= today
                and (not rec.valid_until or rec.valid_until >= today)
            )

    def _search_current(self, operator, value):
        today = fields.Date.context_today(self)
        domain = [
            ("state", "=", "published"),
            ("valid_from", "<=", today),
            "|",
            ("valid_until", "=", False),
            ("valid_until", ">=", today),
        ]
        # Odoo 19 hands a boolean filter over as `in` / `not in` a set
        if operator in ("in", "not in"):
            positive = (True in value) == (operator == "in")
        else:
            positive = (operator == "=" and bool(value)) or (operator == "!=" and not value)
        return domain if positive else ["!", *domain]

    @api.constrains("valid_from", "valid_until")
    def _check_dates(self):
        for rec in self:
            if rec.valid_until and rec.valid_until < rec.valid_from:
                raise ValidationError("An announcement cannot end before it starts.")

    def write(self, vals):
        if not self._fix_guard_open():
            frozen = {"name", "body", "kind", "branch_ids", "valid_from"} & set(vals)
            if frozen and self.filtered(lambda r: r.state != "draft"):
                raise UserError(
                    "A published announcement is not rewritten: withdraw it and publish a new one."
                )
        return super().write(vals)

    def action_publish(self):
        if not (self.env.su or self.env.user.has_group(GROUP_MANAGER)):
            raise UserError("Only a Branch Manager publishes an announcement.")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Announcement '%s' is already %s." % (rec.name, rec.state))
            rec._guarded().write(
                {
                    "state": "published",
                    "published_by_id": self.env.uid,
                    "published_at": fields.Datetime.now(),
                }
            )
        return True

    def action_withdraw(self):
        if not (self.env.su or self.env.user.has_group(GROUP_MANAGER)):
            raise UserError("Only a Branch Manager withdraws an announcement.")
        for rec in self:
            if rec.state != "published":
                raise UserError("Announcement '%s' is not published." % rec.name)
            rec._guarded().write({"state": "withdrawn"})
        return True

    def action_acknowledge(self):
        """The current user has read it (once; acknowledging again is a no-op)."""
        for rec in self:
            if not rec.is_current:
                raise UserError("Announcement '%s' is not showing now." % rec.name)
            if self.env.user not in rec.ack_user_ids:
                rec.sudo()._guarded().write({"ack_user_ids": [(4, self.env.uid)]})
        return True
