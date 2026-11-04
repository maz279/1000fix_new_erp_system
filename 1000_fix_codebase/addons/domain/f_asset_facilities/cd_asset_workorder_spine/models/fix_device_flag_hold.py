# fix_device_flag_hold — A07 P1 wiring round 2 (2026-11-04): an M17
# lost/stolen flag reaches the M01 counter.
#
# BRU-AST-09 / FF-48: M17 published device.flagged and device.flag_cleared
# and no service order heard of them, so a phone reported stolen while it sat
# in repair was handed back at the counter to whoever held the ticket. Now
# every open service order of the device gets ONE hold per flag (this model,
# keyed on the flag event) with an activity for its branch (the branch
# manager, else a device branch manager, else whoever raised the order), and
# the clearance is recorded on the hold: who cleared it, when and why, and
# the activity is marked done. The order's state is never touched, and
# nobody types a hold: only the two consumers write it.
from odoo import api, fields, models
from odoo.exceptions import UserError

SO_CLOSED = ("delivered", "closed", "cancelled")
DEVICE_BRANCH_MANAGER = "cd_device_registry.group_device_branch_manager"
HOLD_SYSTEM_FIELDS = {
    "name",
    "order_id",
    "device_id",
    "flag",
    "flag_event_id",
    "reason",
    "flagged_by_id",
    "flagged_at",
    "state",
    "cleared_by_id",
    "cleared_at",
    "clear_reason",
    "activity_id",
}


class FixServiceOrderDeviceHold(models.Model):
    _name = "fix.service.order.device.hold"
    _description = "Service Order Hold: Device Reported Lost / Stolen (M17)"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "state, id desc"

    _order_flag_once = models.Constraint(
        "UNIQUE (order_id, flag_event_id)", "One hold per service order and device flag."
    )

    name = fields.Char(required=True, readonly=True)
    order_id = fields.Many2one(
        "fix.service.order",
        string="Service Order",
        required=True,
        readonly=True,
        index=True,
        ondelete="cascade",
    )
    device_id = fields.Many2one(
        "fix.device",
        string="Device (M17)",
        required=True,
        readonly=True,
        index=True,
        ondelete="restrict",
    )
    company_id = fields.Many2one(related="order_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="order_id.operating_unit_id", store=True, index=True
    )
    branch_id = fields.Many2one(related="order_id.branch_id", string="Branch")
    flag = fields.Char(readonly=True, default="lost")
    flag_event_id = fields.Char(
        string="Flag Event", required=True, readonly=True, index=True, help="The idempotency key."
    )
    reason = fields.Text(string="Reported", readonly=True)
    flagged_by_id = fields.Many2one("res.users", string="Flagged By", readonly=True)
    flagged_at = fields.Datetime(readonly=True)
    state = fields.Selection(
        [("open", "Device Reported Lost / Stolen"), ("cleared", "Flag Cleared")],
        default="open",
        required=True,
        readonly=True,
        index=True,
        tracking=True,
    )
    cleared_by_id = fields.Many2one("res.users", string="Cleared By", readonly=True)
    cleared_at = fields.Datetime(readonly=True)
    clear_reason = fields.Text(readonly=True)
    activity_id = fields.Many2one("mail.activity", readonly=True, ondelete="set null")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | HOLD_SYSTEM_FIELDS

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            raise UserError("A device hold is raised from an M17 lost/stolen flag only.")
        return super().create(vals_list)

    def unlink(self):
        if not self.env.su:
            raise UserError("A device hold is part of the order's record: it is cleared in M17.")
        return super().unlink()

    # ------------------------------------------------------------ helpers
    @api.model
    def _hold_assignee(self, order):
        """Who acts for the branch: its manager, else a device branch manager
        of the company, else whoever raised the order. Never the superuser."""
        order = order.sudo()
        candidates = order.branch_id.manager_id
        group = self.env.ref(DEVICE_BRANCH_MANAGER, raise_if_not_found=False)
        if group:
            candidates |= (
                group.sudo()
                .all_user_ids.filtered(lambda u: order.company_id in u.company_ids)
                .sorted("id")
            )
        candidates |= order.create_uid
        for user in candidates:
            if user.active and user._is_internal() and not user._is_superuser():
                return user
        return self.env["res.users"]

    # ------------------------------------------------------------ consumers
    @api.model
    def consume_device_flagged(self, event):
        """device.flagged -> each open service order of the device: one hold
        and one activity for its branch. Idempotent per (order, flag event).
        A flag already cleared before the event was relayed raises nothing."""
        payload = event.get("payload") or {}
        device = (
            self.env["fix.device"]
            .sudo()
            .browse(payload.get("device_id") or event.get("aggregate_id"))
            .exists()
        )
        if not device or device.state != "lost":
            return False
        key = event.get("event_id") or "%s@%s" % (device.id, device.lost_flagged_at)
        orders = (
            self.env["fix.service.order"]
            .sudo()
            .search([("device_id", "=", device.id), ("state", "not in", SO_CLOSED)])
        )
        Hold = self.sudo()._guarded()
        who = device.lost_flagged_by_id
        ident = ", ".join(
            "%s %s" % (label, value)
            for label, value in (
                ("serial", device.serial_number),
                ("IMEI", device.imei_1),
                ("IMEI 2", device.imei_2),
            )
            if value
        )
        for order in orders:
            if Hold.search_count([("order_id", "=", order.id), ("flag_event_id", "=", key)]):
                continue
            text = (
                "Device %s%s was reported lost/stolen on %s by %s: %s. Do not hand it back "
                "or release it from order %s until the flag is cleared in M17 by a Branch "
                "Manager; check the claimant's identity first. The order's state is unchanged."
                % (
                    device.display_name,
                    " (%s)" % ident if ident else "",
                    device.lost_flagged_at or fields.Datetime.now(),
                    who.name or "the system",
                    payload.get("reason") or device.lost_reason or "-",
                    order.name,
                )
            )
            hold = Hold.create(
                {
                    "name": "%s / %s" % (order.name, device.display_name),
                    "order_id": order.id,
                    "device_id": device.id,
                    "flag": payload.get("flag") or "lost",
                    "flag_event_id": key,
                    "reason": payload.get("reason") or device.lost_reason,
                    "flagged_by_id": who.id or False,
                    "flagged_at": device.lost_flagged_at or fields.Datetime.now(),
                }
            )
            user = self._hold_assignee(order)
            if user:
                activity = order.sudo().activity_schedule(
                    "mail.mail_activity_data_todo",
                    user_id=user.id,
                    summary="Device reported lost/stolen: do not hand back",
                    note=text,
                )
                hold.write({"activity_id": activity.id})
            order.sudo().message_post(body=text)
        return True

    @api.model
    def consume_device_flag_cleared(self, event):
        """device.flag_cleared -> the clearance on each open hold of the device
        (who, when, why; the activity is marked done). Idempotent: only open
        holds are touched, and a hold of a newer flag stays open."""
        payload = event.get("payload") or {}
        device = (
            self.env["fix.device"]
            .sudo()
            .browse(payload.get("device_id") or event.get("aggregate_id"))
            .exists()
        )
        if not device:
            return False
        holds = self.sudo().search([("device_id", "=", device.id), ("state", "=", "open")])
        if device.state == "lost" and device.lost_flagged_at:
            # flagged again since: only the holds of the earlier flag are cleared
            holds = holds.filtered(lambda h: h.flagged_at and h.flagged_at < device.lost_flagged_at)
        who = (
            self.env["res.users"].sudo().browse(payload.get("cleared_by") or 0).exists()
            or device.lost_cleared_by_id
        )
        when = device.lost_cleared_at or fields.Datetime.now()
        reason = payload.get("reason") or "-"
        for hold in holds:
            text = (
                "Lost/stolen flag of %s cleared in M17 by %s on %s: %s. Order %s may proceed."
                % (
                    device.display_name,
                    who.name or "the system",
                    when,
                    reason,
                    hold.order_id.name,
                )
            )
            hold._guarded().write(
                {
                    "state": "cleared",
                    "cleared_by_id": who.id or False,
                    "cleared_at": when,
                    "clear_reason": reason,
                }
            )
            activity = hold.activity_id.sudo().exists()
            if activity:
                activity.action_feedback(feedback=text)
            hold.order_id.sudo().message_post(body=text)
        return True


class FixServiceOrderDeviceFlag(models.Model):
    _inherit = "fix.service.order"

    device_hold_ids = fields.One2many(
        "fix.service.order.device.hold", "order_id", string="Device Holds (M17)", readonly=True
    )
    device_flag_hold = fields.Boolean(
        string="Device Reported Lost / Stolen",
        compute="_compute_device_flag_hold",
        store=True,
        index=True,
        help="M17 has this order's device flagged lost or stolen: it is not handed back "
        "until a Branch Manager clears the flag.",
    )

    @api.depends("device_hold_ids.state")
    def _compute_device_flag_hold(self):
        for rec in self:
            rec.device_flag_hold = any(h.state == "open" for h in rec.device_hold_ids)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"device_flag_hold"}
