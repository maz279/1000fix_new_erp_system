# M04 capture audit (18 Nov 2026): two captures the specification gives M04
# that no page could record.
#
# * Shift handover (FR-FRD-022, owned entity fix.shift.handover): the
#   outgoing shift's structured note to the incoming team, which that team
#   acknowledges. A free-text note on the day's checklist was all there was:
#   nobody was named as receiving it and nothing showed it had been read.
# * Customer rating at handover (FR-FRD-029, AUT-FRD-12): a quick 1-5 rating
#   taken at the counter when the device is released. M34's survey is raised
#   only when the order CLOSES (NT-024 deferred send), so the counter had no
#   way to record what the customer said at the counter.
import secrets
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError

from .fix_cash_shift import fill_operating_unit

HANDOVER_GROUPS = (
    "cd_front_desk.group_fd_cashier",
    "cd_front_desk.group_fd_branch_manager",
    "cd_front_desk.group_fd_queue_agent",
)
MANAGER = "cd_front_desk.group_fd_branch_manager"


class FixShiftHandover(models.Model):
    """The outgoing shift's handover note to the incoming team (FR-FRD-022)."""

    _name = "fix.shift.handover"
    _description = "Shift Handover Note"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "id desc"

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "name",
            "state",
            "handed_over_by_id",
            "handed_over_at",
            "acknowledged_by_id",
            "acknowledged_at",
        }

    name = fields.Char(string="Handover No.", readonly=True, copy=False, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit", index=True)
    from_shift_id = fields.Many2one(
        "fix.cash.shift",
        string="Outgoing Shift",
        required=True,
        index=True,
        ondelete="restrict",
        help="The shift handing over.",
    )
    branch_id = fields.Many2one(
        "fix.branch", related="from_shift_id.branch_id", store=True, string="Branch", index=True
    )
    from_operator_id = fields.Many2one(
        "hr.employee",
        related="from_shift_id.operator_id",
        store=True,
        string="Handed Over By (Shift)",
    )
    to_operator_id = fields.Many2one(
        "hr.employee",
        string="Incoming Team Member",
        required=True,
        help="Who takes over the counter; they acknowledge the note.",
    )
    to_shift_id = fields.Many2one("fix.cash.shift", string="Incoming Shift", ondelete="restrict")
    notes = fields.Text(string="Handover Notes", required=True)
    open_items = fields.Text(
        string="Open Items",
        help="What the incoming team must act on: customers waiting, devices promised, "
        "cash or stock issues.",
    )
    state = fields.Selection(
        [("handed_over", "Handed Over"), ("acknowledged", "Acknowledged")],
        default="handed_over",
        required=True,
        tracking=True,
    )
    handed_over_by_id = fields.Many2one("res.users", string="Written By", readonly=True)
    handed_over_at = fields.Datetime(string="Written At", readonly=True)
    acknowledged_by_id = fields.Many2one("res.users", string="Acknowledged By", readonly=True)
    acknowledged_at = fields.Datetime(string="Acknowledged At", readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su and not any(self.env.user.has_group(g) for g in HANDOVER_GROUPS):
            raise AccessError("Only front-desk staff write a shift handover.")
        Shift = self.env["fix.cash.shift"]
        for vals in vals_list:
            shift = Shift.browse(vals.get("from_shift_id")).exists()
            if not shift:
                raise UserError("Choose the outgoing shift this handover is from.")
            if len((vals.get("notes") or "").strip()) < 10:
                raise UserError("Write the handover notes for the incoming team (FR-FRD-022).")
            incoming = self.env["hr.employee"].browse(vals.get("to_operator_id")).exists()
            if not incoming:
                raise UserError("Name the incoming team member who takes over.")
            if incoming == shift.operator_id:
                raise UserError(
                    "A handover goes to the next team, not back to the shift's own operator."
                )
            to_shift = Shift.browse(vals.get("to_shift_id")).exists()
            if to_shift and to_shift.branch_id != shift.branch_id:
                raise UserError(
                    "The incoming shift must be at the same branch as the outgoing one."
                )
            if to_shift and to_shift == shift:
                raise UserError("The incoming shift cannot be the outgoing shift.")
            vals.update(
                {
                    "company_id": shift.company_id.id,
                    "state": "handed_over",
                    "handed_over_by_id": self.env.uid,
                    "handed_over_at": fields.Datetime.now(),
                    "acknowledged_by_id": False,
                    "acknowledged_at": False,
                    "name": self.env["ir.sequence"].sudo().next_by_code("fix.shift.handover")
                    or "New",
                }
            )
            if not vals.get("operating_unit_id"):
                vals["operating_unit_id"] = shift.operating_unit_id.id or False
        fill_operating_unit(self.env, vals_list)
        return super(FixShiftHandover, self._guarded()).create(vals_list)

    def write(self, vals):
        if not self.env.su and not self._fix_guard_has_token():
            if set(vals) & self._fix_guarded_fields():
                return super().write(vals)  # the guard refuses its own fields
            if any(rec.state == "acknowledged" for rec in self):
                raise UserError(
                    "An acknowledged handover is a record of what was handed over: it is not changed."
                )
            if any(rec.handed_over_by_id != self.env.user for rec in self):
                raise UserError(
                    "Only the person who wrote a handover may correct it before it is acknowledged."
                )
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError("A shift handover is kept as evidence and never deleted.")
        return super().unlink()

    def action_acknowledge(self):
        """The incoming team member confirms they read the handover."""
        now = fields.Datetime.now()
        for rec in self:
            if rec.state != "handed_over":
                raise UserError("Handover %s is already acknowledged." % rec.name)
            user = self.env.user
            incoming_user = rec.to_operator_id.user_id
            if rec.handed_over_by_id == user and not self.env.su:
                raise UserError(
                    "You wrote handover %s: the incoming team acknowledges it." % rec.name
                )
            # an incoming member with no login: the branch manager signs for them
            allowed = user == incoming_user if incoming_user else user.has_group(MANAGER)
            if not (allowed or self.env.su):
                raise AccessError(
                    "Handover %s is for %s: only they%s acknowledge it."
                    % (
                        rec.name,
                        rec.to_operator_id.name,
                        "" if incoming_user else " (or a Branch Manager, as they have no login)",
                    )
                )
            rec._guarded().write(
                {"state": "acknowledged", "acknowledged_by_id": user.id, "acknowledged_at": now}
            )
            rec.message_post(body="Acknowledged by %s." % user.name)
        return True


COUNTER_RATINGS = [
    ("1", "1 - Very Dissatisfied"),
    ("2", "2 - Dissatisfied"),
    ("3", "3 - Neutral"),
    ("4", "4 - Satisfied"),
    ("5", "5 - Very Satisfied"),
]


# A02 pass 2 (M04-06): how long a rating link stays open, in hours
RATING_LINK_HOURS_PARAM = "cd_front_desk.counter_rating_link_hours"
DEFAULT_RATING_LINK_HOURS = 24.0


class FixServiceOrderCounterRating(models.Model):
    """FR-FRD-029: the customer's quick rating at the counter, at handover.

    A02 pass 2 (M04-06): the rating was typed by the counter staff it rated.
    The customer now gives it themselves: the counter asks for it (Ask the
    Customer to Rate), which opens a one-time rating page for this order on
    the counter tablet or the customer's phone; the page records the
    customer's stars and comment, once. Staff cannot type or change it."""

    _inherit = "fix.service.order"

    counter_rating = fields.Selection(
        COUNTER_RATINGS, string="Customer Rating at Handover", copy=False, tracking=True
    )
    counter_feedback = fields.Char(string="Customer's Comment at Handover", copy=False)
    counter_rated_by_id = fields.Many2one(
        "res.users",
        string="Rating Asked By",
        readonly=True,
        copy=False,
        help="The staff member who handed the customer the rating page.",
    )
    counter_rated_at = fields.Datetime(string="Rating Given At", readonly=True, copy=False)
    counter_rating_token = fields.Char(
        readonly=True, copy=False, index=True, groups="base.group_system"
    )
    counter_rating_requested_at = fields.Datetime(
        string="Rating Asked At", readonly=True, copy=False
    )
    counter_rating_url = fields.Char(
        string="Customer Rating Page",
        compute="_compute_counter_rating_url",
        help="Open on the counter tablet or send to the customer's phone: the customer rates "
        "the service there, once.",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "counter_rated_by_id",
            "counter_rated_at",
            "counter_rating_token",
            "counter_rating_requested_at",
            # M04-06: the customer's own words, written only by the rating page
            "counter_rating",
            "counter_feedback",
        }

    def _compute_counter_rating_url(self):
        base = self.env["ir.config_parameter"].sudo().get_param("web.base.url") or ""
        for order in self:
            token = order.sudo().counter_rating_token
            order.counter_rating_url = (
                "%s/fix/counter-rating/%s" % (base, token)
                if token and not order.counter_rated_at
                else False
            )

    def action_request_counter_rating(self):
        """The counter asks the customer to rate: a one-time page for this
        order. Asking again replaces the earlier link."""
        for order in self:
            if order.counter_rated_at:
                raise UserError("Order %s: the customer already rated the handover." % order.name)
            if order.state not in ("ready", "delivered"):
                raise UserError(
                    "Order %s: the customer's rating is taken at handover, when the device is "
                    "ready or released." % order.name
                )
            order._guarded().sudo().write(
                {
                    "counter_rating_token": secrets.token_urlsafe(24),
                    "counter_rating_requested_at": fields.Datetime.now(),
                    "counter_rated_by_id": self.env.uid,
                }
            )
            order.message_post(
                body="%s asked the customer to rate the handover." % self.env.user.name
            )
        if len(self) == 1:
            return {"rating_url": self.counter_rating_url}
        return True

    @api.model
    def _fd_rating_link_hours(self) -> float:
        raw = self.env["ir.config_parameter"].sudo().get_param(RATING_LINK_HOURS_PARAM)
        try:
            return float(raw) if raw not in (None, False, "") else DEFAULT_RATING_LINK_HOURS
        except ValueError:
            return DEFAULT_RATING_LINK_HOURS

    @api.model
    def _fd_order_for_rating(self, token):
        """The order a live rating link belongs to, or an empty recordset."""
        token = (token or "").strip()
        if len(token) < 16:
            return self.browse()
        order = self.sudo().search([("counter_rating_token", "=", token)], limit=1)
        if not order or order.counter_rated_at or order.state not in ("ready", "delivered"):
            return self.browse()
        asked = order.counter_rating_requested_at
        if not asked or fields.Datetime.now() > asked + timedelta(
            hours=self._fd_rating_link_hours()
        ):
            return self.browse()
        return order

    @api.model
    def _fd_take_customer_rating(self, token, rating, feedback=None):
        """The rating page: the customer's stars and comment, once."""
        order = self._fd_order_for_rating(token)
        if not order:
            raise UserError("This rating link is no longer open.")
        rating = str(rating or "").strip()
        if rating not in dict(COUNTER_RATINGS):
            raise UserError("Choose from 1 to 5 stars.")
        order._guarded().write(
            {
                "counter_rating": rating,
                "counter_feedback": (feedback or "").strip()[:500] or False,
                "counter_rated_at": fields.Datetime.now(),
                "counter_rating_token": False,
            }
        )
        order.message_post(body="The customer rated the handover %s/5." % rating)
        return order
