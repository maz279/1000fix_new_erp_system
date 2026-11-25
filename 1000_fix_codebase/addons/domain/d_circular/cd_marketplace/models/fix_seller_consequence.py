# M12 seller consequences (13 Nov 2026, M12 capture audit).
#
# Sub-module 7 "Performance Consequences" had nothing to record: the tier
# ladder (Measure & Rank moves a seller to at-risk) was the only consequence,
# and probation, suspension and the appeal against them (M12 spec FR-MKP-053
# to 055, seller lifecycle s.8.1, BRU-MKP-11 / -18) had no store.
#
#   * fix.seller.consequence - a formal warning, a probation with its
#     remediation plan and review date, or a suspension, imposed by a
#     Marketplace Operator with its trigger and reason:
#       draft -> active (imposed) -> appealed -> active (appeal dismissed)
#                                             -> lifted (appeal upheld)
#                active -> lifted (remediation verified) / expired (its end date)
#                draft  -> cancelled
#     Lifting it or deciding its appeal is done by an operator other than the
#     one who imposed it (BRU-MKP-18). Its terms are pinned once imposed.
#   * While a suspension is in force (active or under appeal) the seller does
#     not transact: no quote is accepted or awarded and no listing goes live
#     (submit / resume); imposing it pauses the seller's active listings
#     (BRU-MKP-11).
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_marketplace import OPERATOR_GROUP, _assert_role, _seller_users
from .fix_seller_standard import dhaka_today

CONSEQUENCE_TYPES = [
    ("warning", "Formal Warning"),
    ("probation", "Probation (remediation plan)"),
    ("suspension", "Suspension (transacting blocked)"),
]
TRIGGERS = [
    ("score", "Score below threshold"),
    ("dispute", "Upheld dispute"),
    ("counterfeit", "Counterfeit / non-genuine part finding"),
    ("evidence", "Evidence non-compliance"),
    ("fraud", "Fraud or off-platform dealing"),
    ("lapse", "Registration or document lapse"),
    ("other", "Other policy breach"),
]
CONSEQUENCE_STATES = [
    ("draft", "Draft"),
    ("active", "In Force"),
    ("appealed", "Under Appeal"),
    ("lifted", "Lifted"),
    ("expired", "Expired"),
    ("cancelled", "Cancelled"),
]
# A consequence in these states binds the seller (an appeal does not lift it).
IN_FORCE_STATES = ("active", "appealed")
_TERMS = {
    "seller_id",
    "consequence_type",
    "trigger",
    "reason",
    "remediation_plan",
    "review_date",
    "effective_from",
    "effective_to",
}


class FixSellerConsequence(models.Model):
    _name = "fix.seller.consequence"
    _description = "Seller Consequence"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "effective_from desc, id desc"

    name = fields.Char(string="Reference", default="New", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", related="seller_id.company_id", store=True, index=True, readonly=True
    )
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Operating Unit",
        related="seller_id.operating_unit_id",
        store=True,
        readonly=True,
    )
    seller_id = fields.Many2one(
        "fix.marketplace.seller", required=True, ondelete="restrict", index=True, tracking=True
    )
    consequence_type = fields.Selection(
        CONSEQUENCE_TYPES, string="Consequence", required=True, tracking=True
    )
    trigger = fields.Selection(TRIGGERS, required=True, tracking=True)
    reason = fields.Text(string="Reason and Evidence", required=True, tracking=True)
    remediation_plan = fields.Text(
        string="Remediation Plan", help="Required for a probation: what the seller must do."
    )
    review_date = fields.Date(
        string="Review Date", help="Required for a probation: when the remediation is reviewed."
    )
    effective_from = fields.Date(
        required=True, default=lambda self: dhaka_today(self), tracking=True
    )
    effective_to = fields.Date(
        string="Effective To", tracking=True, help="Empty: in force until lifted."
    )
    state = fields.Selection(
        CONSEQUENCE_STATES,
        required=True,
        default="draft",
        readonly=True,
        tracking=True,
        copy=False,
    )
    imposed_by_id = fields.Many2one("res.users", string="Imposed By", readonly=True, copy=False)
    imposed_at = fields.Datetime(string="Imposed At", readonly=True, copy=False)
    appeal_reason = fields.Text(string="Seller's Appeal", readonly=True, copy=False)
    appealed_at = fields.Datetime(string="Appealed At", readonly=True, copy=False)
    decided_by_id = fields.Many2one(
        "res.users", string="Lifted / Appeal Decided By", readonly=True, copy=False
    )
    decided_at = fields.Datetime(string="Decided At", readonly=True, copy=False)
    decision_note = fields.Text(string="Decision Note", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "imposed_by_id",
            "imposed_at",
            "appeal_reason",
            "appealed_at",
            "decided_by_id",
            "decided_at",
            "decision_note",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.id and self.state != "draft":
            locked |= _TERMS
        return locked

    @api.depends("name", "seller_id.name", "consequence_type")
    def _compute_display_name(self):
        types = dict(CONSEQUENCE_TYPES)
        for rec in self:
            rec.display_name = "%s — %s (%s)" % (
                rec.name or "New",
                rec.seller_id.name or "?",
                types.get(rec.consequence_type, "?"),
            )

    @api.constrains("effective_from", "effective_to")
    def _check_dates(self):
        for rec in self:
            if rec.effective_to and rec.effective_from and rec.effective_to < rec.effective_from:
                raise ValidationError("A consequence ends on or after the day it starts.")

    @api.model_create_multi
    def create(self, vals_list):
        _assert_role(self.env, OPERATOR_GROUP, "Recording a seller consequence")
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.seller.consequence")
                    or "SCQ/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self.filtered(lambda r: r.state != "draft"):
                changed = [
                    n for n in _TERMS & set(vals) if rec._fix_guard_differs(n, vals[n], rec[n])
                ]
                if changed:
                    raise UserError(
                        "Consequence %s is %s: its %s are pinned to what was imposed."
                        % (
                            rec.name,
                            dict(CONSEQUENCE_STATES)[rec.state],
                            ", ".join(sorted(changed)),
                        )
                    )
        return super().write(vals)

    # ---- helpers ----------------------------------------------------------
    def _assert_not_imposer(self, what):
        """BRU-MKP-18: the operator who imposed it does not lift it or decide
        its appeal; nor does anyone who acts for the seller."""
        for rec in self:
            if self.env.su:
                continue
            if self.env.user in (rec.imposed_by_id | rec.create_uid | _seller_users(rec.seller_id)):
                raise UserError(
                    "Segregation of duties: whoever recorded or imposed %s, or acts for the "
                    "seller, does not %s it (BRU-MKP-18)." % (rec.name, what)
                )

    def _decide(self, state, note):
        self._guarded().write(
            {
                "state": state,
                "decided_by_id": self.env.uid,
                "decided_at": fields.Datetime.now(),
                "decision_note": note,
            }
        )

    # ---- lifecycle --------------------------------------------------------
    def action_impose(self):
        _assert_role(self.env, OPERATOR_GROUP, "Imposing a seller consequence")
        today = dhaka_today(self)
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft consequence is imposed.")
            if rec.consequence_type == "probation" and not (
                (rec.remediation_plan or "").strip() and rec.review_date
            ):
                raise UserError(
                    "A probation carries its remediation plan and review date (FR-MKP-054)."
                )
            if rec.review_date and rec.review_date < today:
                raise UserError("The review date of %s has already passed." % rec.name)
            if rec.effective_to and rec.effective_to < today:
                raise UserError("%s would end before it starts to bind." % rec.name)
            rec._guarded().write(
                {
                    "state": "active",
                    "imposed_by_id": self.env.uid,
                    "imposed_at": fields.Datetime.now(),
                }
            )
            if rec.consequence_type == "suspension":
                listings = (
                    self.env["fix.marketplace.listing"]
                    .sudo()
                    .search([("seller_id", "=", rec.seller_id.id), ("state", "=", "active")])
                )
                listings._guarded().write({"state": "paused"})
                for listing in listings:
                    listing.message_post(body="Paused: seller suspended (%s)." % rec.name)
            rec.seller_id.message_post(
                body="%s imposed (%s): %s"
                % (dict(CONSEQUENCE_TYPES)[rec.consequence_type], rec.name, rec.reason)
            )
        return True

    def action_appeal(self, reason=None):
        _assert_role(self.env, OPERATOR_GROUP, "Recording a seller's appeal")
        if not (reason or "").strip():
            raise UserError("Record the seller's grounds of appeal.")
        for rec in self:
            if rec.state != "active":
                raise UserError("Only a consequence in force is appealed.")
            rec._guarded().write(
                {
                    "state": "appealed",
                    "appeal_reason": reason.strip(),
                    "appealed_at": fields.Datetime.now(),
                }
            )
        return True

    def action_uphold_appeal(self, note=None):
        _assert_role(self.env, OPERATOR_GROUP, "Deciding a seller's appeal")
        if not (note or "").strip():
            raise UserError("Give the reason the appeal is upheld.")
        for rec in self:
            if rec.state != "appealed":
                raise UserError("Only a consequence under appeal is decided.")
            rec._assert_not_imposer("decide the appeal against")
            rec._decide("lifted", note.strip())
        return True

    def action_dismiss_appeal(self, note=None):
        _assert_role(self.env, OPERATOR_GROUP, "Deciding a seller's appeal")
        if not (note or "").strip():
            raise UserError("Give the reason the appeal is dismissed.")
        for rec in self:
            if rec.state != "appealed":
                raise UserError("Only a consequence under appeal is decided.")
            rec._assert_not_imposer("decide the appeal against")
            rec._decide("active", note.strip())
        return True

    def action_lift(self, note=None):
        _assert_role(self.env, OPERATOR_GROUP, "Lifting a seller consequence")
        if not (note or "").strip():
            raise UserError("Record how the remediation was verified.")
        for rec in self:
            if rec.state != "active":
                raise UserError("Only a consequence in force is lifted.")
            rec._assert_not_imposer("lift")
            rec._decide("lifted", note.strip())
        return True

    def action_cancel(self):
        _assert_role(self.env, OPERATOR_GROUP, "Cancelling a seller consequence")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft consequence is cancelled; lift one in force.")
            rec._guarded().write({"state": "cancelled"})
        return True

    @api.model
    def cron_expire_consequences(self):
        """Daily: a consequence in force past its end date expires."""
        today = dhaka_today(self)
        lapsed = self.sudo().search(
            [
                ("state", "in", IN_FORCE_STATES),
                ("effective_to", "!=", False),
                ("effective_to", "<", today),
            ]
        )
        for rec in lapsed:
            rec._guarded().write({"state": "expired"})
            rec.message_post(body="Expired on %s." % rec.effective_to)
        return len(lapsed)


class FixMarketplaceSellerConsequence(models.Model):
    _inherit = "fix.marketplace.seller"

    consequence_ids = fields.One2many(
        "fix.seller.consequence", "seller_id", string="Consequences", readonly=True
    )

    def _active_suspension(self):
        """The suspension binding this seller today, if any."""
        self.ensure_one()
        today = dhaka_today(self)
        return (
            self.env["fix.seller.consequence"]
            .sudo()
            .search(
                [
                    ("seller_id", "=", self.id),
                    ("consequence_type", "=", "suspension"),
                    ("state", "in", IN_FORCE_STATES),
                    ("effective_from", "<=", today),
                    "|",
                    ("effective_to", "=", False),
                    ("effective_to", ">=", today),
                ],
                limit=1,
            )
        )

    def _assert_not_suspended(self, what):
        for seller in self:
            suspension = seller._active_suspension()
            if suspension:
                raise UserError(
                    "%s is suspended (%s): %s is refused until the suspension is lifted."
                    % (seller.name, suspension.name, what)
                )
