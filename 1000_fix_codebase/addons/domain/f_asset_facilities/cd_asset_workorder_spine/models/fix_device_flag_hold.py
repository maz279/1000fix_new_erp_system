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
#
# A07 operability (2026-11-07): the hold told the branch not to hand the device
# back and nothing stopped them. The hand-over itself now refuses.
#
# A07 ERP audit (2026-11-20), M17 stream S1:
# - M17-01: an order opened (or re-pointed) AFTER the flag got no hold and read
#   "not held". The order itself now raises the hold at once (key
#   "intake@<order>"), with the branch activity and a warning on the order, and
#   the stored flag reads the device's own flag as well as the holds.
# - M17-22 / D12(b): an "ownership disputed" flag holds the order the same way
#   (hold flag "disputed"), and its clearance clears only its own holds.
# - M17-09: a scrapped device is not serviced: no new order is opened on it.
# - M17-07: a courtesy loaner and a swap device come from 1000FiX's stock and
#   are handable; the swap hands the device to the customer through an M17
#   ownership transfer (and so out of company stock).
# - M17-14: the order's progress is the device's custody state.
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
# M17-07: where a loaner and a swap unit may come from.
LOANER_POPULATIONS = ("rental_pool", "refurbishment_stock")
SWAP_POPULATIONS = ("refurbishment_stock",)
# M17-14: the order's state as the device's custody state.
ORDER_CUSTODY = {
    "intake": "under_service",
    "diagnostic": "under_service",
    "estimate_pending": "under_service",
    "estimate_sent": "under_service",
    "awaiting_approval": "under_service",
    "approved": "under_service",
    "in_repair": "under_service",
    "qc_pending": "under_service",
    "qc_failed": "under_service",
    "ready": "awaiting_collection",
    "delivered": "with_owner",
}


def _device_flags(device):
    """The hold-worthy flags a device carries now: (flag, reason, who, when)."""
    flags = []
    if device.state == "lost":
        flags.append(
            (
                device.lost_flag_type or "lost",
                device.lost_reason,
                device.lost_flagged_by_id,
                device.lost_flagged_at,
            )
        )
    if device.ownership_disputed:
        flags.append(
            (
                "disputed",
                device.dispute_reason,
                device.dispute_flagged_by_id,
                device.dispute_flagged_at,
            )
        )
    return flags


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

    @api.model
    def _raise_holds(self, device, orders, key, flag, reason, who, when):
        """One hold per (order, key) with the branch activity and a warning on
        the order. Idempotent."""
        Hold = self.sudo()._guarded()
        ident = ", ".join(
            "%s %s" % (label, value)
            for label, value in (
                ("serial", device.serial_number),
                ("IMEI", device.imei_1),
                ("IMEI 2", device.imei_2),
            )
            if value
        )
        what = "under an ownership dispute" if flag == "disputed" else "reported %s" % flag
        created = Hold.browse()
        for order in orders:
            if Hold.search_count([("order_id", "=", order.id), ("flag_event_id", "=", key)]):
                continue
            text = (
                "Device %s%s is %s since %s (raised by %s): %s. Do not hand it back "
                "or release it from order %s until the flag is cleared in M17 by a Branch "
                "Manager; check the claimant's identity first. The order's state is unchanged."
                % (
                    device.display_name,
                    " (%s)" % ident if ident else "",
                    what,
                    when or fields.Datetime.now(),
                    who.name or "the system",
                    reason or "-",
                    order.name,
                )
            )
            hold = Hold.create(
                {
                    "name": "%s / %s" % (order.name, device.display_name),
                    "order_id": order.id,
                    "device_id": device.id,
                    "flag": flag,
                    "flag_event_id": key,
                    "reason": reason,
                    "flagged_by_id": who.id or False,
                    "flagged_at": when or fields.Datetime.now(),
                }
            )
            user = self._hold_assignee(order)
            if user:
                activity = order.sudo().activity_schedule(
                    "mail.mail_activity_data_todo",
                    user_id=user.id,
                    summary="Device %s: do not hand back" % what,
                    note=text,
                )
                hold.write({"activity_id": activity.id})
            order.sudo().message_post(body=text)
            created |= hold
        return created

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
        if not device:
            return False
        flag = payload.get("flag") or "lost"
        if flag == "disputed":
            if not device.ownership_disputed:
                return False
            who, when = device.dispute_flagged_by_id, device.dispute_flagged_at
            reason = payload.get("reason") or device.dispute_reason
        else:
            if device.state != "lost":
                return False
            who, when = device.lost_flagged_by_id, device.lost_flagged_at
            reason = payload.get("reason") or device.lost_reason
        key = event.get("event_id") or "%s@%s@%s" % (device.id, flag, when)
        orders = (
            self.env["fix.service.order"]
            .sudo()
            .search([("device_id", "=", device.id), ("state", "not in", SO_CLOSED)])
        )
        self._raise_holds(device, orders, key, flag, reason, who, when)
        return True

    @api.model
    def consume_device_flag_cleared(self, event):
        """device.flag_cleared -> the clearance on each open hold of the device
        (who, when, why; the activity is marked done). Idempotent: only open
        holds are touched, and a hold of a newer flag stays open. A cleared
        dispute clears dispute holds only, and a cleared lost flag only its own."""
        payload = event.get("payload") or {}
        device = (
            self.env["fix.device"]
            .sudo()
            .browse(payload.get("device_id") or event.get("aggregate_id"))
            .exists()
        )
        if not device:
            return False
        disputed = payload.get("flag") == "disputed"
        holds = self.sudo().search([("device_id", "=", device.id), ("state", "=", "open")])
        holds = holds.filtered(lambda h: (h.flag == "disputed") == disputed)
        if disputed:
            if device.ownership_disputed and device.dispute_flagged_at:
                holds = holds.filtered(
                    lambda h: h.flagged_at and h.flagged_at < device.dispute_flagged_at
                )
            fallback_who, when = device.dispute_cleared_by_id, device.dispute_cleared_at
        else:
            if device.state == "lost" and device.lost_flagged_at:
                # flagged again since: only the holds of the earlier flag are cleared
                holds = holds.filtered(
                    lambda h: h.flagged_at and h.flagged_at < device.lost_flagged_at
                )
            fallback_who, when = device.lost_cleared_by_id, device.lost_cleared_at
        who = (
            self.env["res.users"].sudo().browse(payload.get("cleared_by") or 0).exists()
            or fallback_who
        )
        when = when or fields.Datetime.now()
        reason = payload.get("reason") or "-"
        for hold in holds:
            text = "%s flag of %s cleared in M17 by %s on %s: %s. Order %s may proceed." % (
                "Ownership-dispute" if disputed else "Lost/stolen",
                device.display_name,
                who.name or "the system",
                when,
                reason,
                hold.order_id.name,
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
        help="M17 has this order's device flagged lost or stolen, or its ownership "
        "disputed: it is not handed back until a Branch Manager clears the flag.",
    )

    @api.depends(
        "state", "device_hold_ids.state", "device_id.state", "device_id.ownership_disputed"
    )
    def _compute_device_flag_hold(self):
        # M17-01: the device's own flag counts too (the hold waits for the
        # relay) - but only for an order still open: a delivered, closed or
        # cancelled order is history and is not "held" by a later flag.
        for rec in self:
            device = rec.sudo().device_id
            flagged = device.state == "lost" or bool(device.ownership_disputed)
            rec.device_flag_hold = any(h.state == "open" for h in rec.device_hold_ids) or (
                flagged and rec.state not in SO_CLOSED
            )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"device_flag_hold"}

    def _validate_transition(self, new_state: str) -> None:
        # every way to Delivered passes here (write -> _validate_transition)
        if new_state == "delivered" and self.state != "delivered":
            self._assert_device_not_held()
        return super()._validate_transition(new_state)

    def _assert_device_not_held(self) -> None:
        """BRU-AST-09 (H): no release while the flag stands. The device's own
        state decides as well as the hold: the hold waits for the event relay.
        It binds service code too: a hard block on a device reported stolen or
        under an ownership dispute has no trusted path."""
        self.ensure_one()
        device = self.sudo().device_id
        holds = self.sudo().device_hold_ids.filtered(lambda h: h.state == "open")
        hold = holds.filtered(lambda h: h.flag != "disputed")[:1]
        if device.state == "lost" or hold:
            raise UserError(
                "Order %s cannot be handed over: its device %s is reported lost or stolen (%s). "
                "A Branch Manager must clear the flag in the Device Registry first."
                % (self.name, device.display_name, device.lost_reason or hold.reason or "-")
            )
        dispute = holds.filtered(lambda h: h.flag == "disputed")[:1]
        if device.ownership_disputed or dispute:
            raise UserError(
                "Order %s cannot be handed over: the ownership of %s is disputed (%s). A "
                "Branch Manager must clear the dispute in the Device Registry first."
                % (self.name, device.display_name, device.dispute_reason or dispute.reason or "-")
            )

    # ------------------------------------------------- M17-01/07/09 at intake
    def _a07_check_order_devices(self, vals):
        """M17-09: no order on a scrapped device. M17-07: a loaner is
        1000FiX's rental-pool or refurbishment stock and handable."""
        Device = self.env["fix.device"].sudo()
        if vals.get("device_id"):
            device = Device.browse(vals["device_id"]).exists()
            if device.state == "scrapped":
                raise UserError(
                    "%s is scrapped: it is not serviced. A scrapped identity presented again "
                    "is a fraud signal; refer it to the Branch Manager." % device.display_name
                )
        if vals.get("loan_device_id"):
            loaner = Device.browse(vals["loan_device_id"]).exists()
            if loaner:
                loaner.assert_population(LOANER_POPULATIONS, "be lent as a courtesy loaner")

    def _a07_hold_flagged_devices(self):
        """M17-01: an order opened on (or moved to) a flagged device is held at
        once, with the branch activity and the warning on the order."""
        Hold = self.env["fix.service.order.device.hold"].sudo()
        for order in self.sudo().filtered(lambda o: o.device_id and o.state not in SO_CLOSED):
            device = order.device_id
            for flag, reason, who, when in _device_flags(device):
                key = "intake@%s@%s@%s" % (order.id, flag, when)
                Hold._raise_holds(device, order, key, flag, reason, who, when)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._a07_check_order_devices(vals)
        orders = super().create(vals_list)
        orders._a07_hold_flagged_devices()
        return orders

    def write(self, vals):
        if vals.get("device_id") or vals.get("loan_device_id"):
            self._a07_check_order_devices(vals)
        closing = (
            self.filtered(lambda o: o.state != "closed")
            if vals.get("state") == "closed"
            else self.browse()
        )
        result = super().write(vals)
        if vals.get("device_id"):
            self._a07_hold_flagged_devices()
        if closing:
            self.env["fix.maintenance.demand"].sudo()._spine_order_closed(closing)
        return result

    def _on_state_change(self, new_state: str, old_state: str) -> None:
        super()._on_state_change(new_state, old_state)
        # M17-14: the order's progress is where the device is.
        custody = ORDER_CUSTODY.get(new_state)
        device = self.sudo().device_id
        if new_state == "cancelled" and device.custody_state == "under_service":
            custody = "awaiting_collection"
        if custody and device:
            device._a07_set_custody(
                custody,
                party=self.customer_id if custody == "with_owner" else None,
                branch=self.branch_id if custody != "with_owner" else None,
                reference=self.name,
            )

    def action_swap_device(self, replacement_device_id, reason="unrepairable", grade="grade_a"):
        """M17-07: the swap unit is 1000FiX's refurbishment stock and handable;
        it passes to the order's customer through M17's ownership transfer
        (which takes it out of company stock), not by a field on the order."""
        self.ensure_one()
        replacement = self.env["fix.device"].sudo().browse(replacement_device_id).exists()
        if replacement:
            replacement.assert_population(SWAP_POPULATIONS, "be swapped to a customer")
        result = super().action_swap_device(replacement_device_id, reason=reason, grade=grade)
        customer = self.sudo().customer_id
        if replacement and customer and replacement.owner_id != customer:
            replacement.action_transfer_ownership(
                new_owner_id=customer.id,
                transfer_type="return",
                reason="Asset swap on service order %s (%s)" % (self.name, reason),
                channel="system",
            )
        return result
