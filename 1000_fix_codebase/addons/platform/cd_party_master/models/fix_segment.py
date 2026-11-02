# fix.segment — segment definitions and current membership (M33,
# FR-CPM-049/050, FR-CPM-012 note). M33 owns the DEFINITION layer; the
# dynamic evaluation engine is the M64/M35 seam (spec A3-07 interim
# capability) — membership here is governed and event-published, never
# recomputed ad hoc by consumers.
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class FixSegment(models.Model):
    """A named segment defined over party attributes; membership is explicit
    and published (segment.membership_changed), not recomputed by readers."""

    _name = "fix.segment"
    _description = "Party Segment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "code"
    # Odoo 19 constraint attribute form
    _code_unique = models.Constraint("UNIQUE (code)", "Each segment code exists once")

    code = fields.Char(string="Code", required=True)
    name = fields.Char(string="Name", required=True)
    name_bn = fields.Char(string="Name (Bengali)")
    criteria_json = fields.Text(
        string="Criteria (JSON)",
        help="Declarative criteria over party attributes. The dynamic "
        "evaluation engine is the M64/M35 seam; membership here is "
        "governed explicitly until that engine lands.",
    )
    evaluation_mode = fields.Selection(
        [("manual", "Manual (steward)"), ("scheduled", "Scheduled evaluation")],
        string="Evaluation Mode",
        default="manual",
        required=True,
    )
    active = fields.Boolean(string="Active", default=True)
    membership_ids = fields.One2many("fix.segment.membership", "segment_id", string="Members")
    member_count = fields.Integer(string="Members", compute="_compute_member_count")
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company
    )

    @api.depends("membership_ids.exited_at")
    def _compute_member_count(self):
        for segment in self:
            segment.member_count = len(segment.membership_ids.filtered(lambda m: not m.exited_at))

    def action_add_members(self, partner_ids=None):
        """Governed membership add: idempotent (an exited member is
        re-opened), each add publishes segment.membership_changed."""
        if not partner_ids:
            raise ValidationError("add_members needs partner ids")
        Membership = self.env["fix.segment.membership"]
        for segment in self:
            for partner in self.env["res.partner"].browse(partner_ids).exists():
                membership = Membership.search(
                    [("segment_id", "=", segment.id), ("partner_id", "=", partner.id)], limit=1
                )
                if membership:
                    if membership.exited_at:
                        membership.write({"exited_at": False, "entered_at": fields.Datetime.now()})
                        segment._publish(partner, True)
                else:
                    Membership.create({"segment_id": segment.id, "partner_id": partner.id})
                    segment._publish(partner, True)
        return True

    def action_remove_member(self, partner_id=None):
        if not partner_id:
            raise ValidationError("remove_member needs the partner id")
        for segment in self:
            membership = segment.membership_ids.filtered(
                lambda m, pid=partner_id: m.partner_id.id == pid and not m.exited_at
            )
            membership.write({"exited_at": fields.Datetime.now()})
            segment._publish(self.env["res.partner"].browse(partner_id), False)
        return True

    def _publish(self, partner, entered):
        from libs.py.fix_events import publish

        publish(
            self.env,
            "segment.membership_changed",
            "fix.segment",
            self.id,
            {"partner_id": partner.id, "entered": entered},
        )


class FixSegmentMembership(models.Model):
    """Current and past membership of one party in one segment."""

    _name = "fix.segment.membership"
    _description = "Segment Membership"
    _order = "segment_id, entered_at desc"
    # Odoo 19 constraint attribute form
    _segment_partner_unique = models.Constraint(
        "UNIQUE (segment_id, partner_id)", "A party is a member of a segment once"
    )

    segment_id = fields.Many2one(
        "fix.segment", string="Segment", required=True, ondelete="cascade", index=True
    )
    partner_id = fields.Many2one(
        "res.partner", string="Party", required=True, ondelete="cascade", index=True
    )
    entered_at = fields.Datetime(string="Entered At", default=fields.Datetime.now)
    exited_at = fields.Datetime(
        string="Exited At", help="Empty = current member; exits are dated, never deleted"
    )
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company
    )
