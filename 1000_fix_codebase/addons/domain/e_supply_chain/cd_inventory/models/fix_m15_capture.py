# cd_inventory - M15 capture pass 2 (19 Nov 2026).
#
# The 13 Nov capture audit gave every M15 sub-module page a button, but four
# pages still could not record what the spec says a person records there:
#
#   page 4 Reservations    a reservation was only a number on the on-hand row,
#                          written by M41 wave release: no record of whom the
#                          stock is held for, no priority, no expiry, no
#                          override (FR-INV-019..021, 027; BRU-INV-17..19;
#                          AUT-INV-01 "manual reservation task").
#   page 5 Issue / Return  no backorder when the part is not at hand
#                          (FR-INV-025, AUT-INV-02), and an issue could not
#                          draw the stock reserved for its own job.
#   page 7 Serial & Lot    no recall: quarantining an affected part or serial
#                          range across every location and van in one
#                          transaction, listing the jobs that already
#                          consumed it (FR-INV-040, AUT-INV-14).
#   page 3 Ownership       no per-brand consignment statement reconciled to
#                          the brand's own records (FR-INV-012, 014,
#                          AUT-INV-07).
#
# Every record below moves stock only through the ledger's own primitives
# (fix.stock.onhand._fix_reserve / _fix_unreserve, fix.stock.quarantine), so
# the movement controls (BRU-INV-07/08, bins, operating units) still apply.
import logging
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

from .fix_inventory_approval import (
    APPROVER_BRANCH_GROUP,
    CONTROLLER_GROUP,
    check_location_usable,
    check_quantity,
    inv_param,
    location_class,
)
from .fix_inventory_ops import EPS, OWNERSHIP_CLASSES
from .fix_stock_consumption import ISSUE_CLASSES

_logger = logging.getLogger(__name__)

# BRU-INV-17: warranty/SLA-bound > paid customer work > internal demand. The
# key sorts: a smaller key is the higher priority.
PRIORITIES = [
    ("1_sla", "Warranty / SLA-bound"),
    ("2_paid", "Paid customer work"),
    ("3_internal", "Internal / stock-building"),
]
SLA_CATEGORIES = ("warranty", "amc", "rework")
PARAM_RESERVATION_HOURS = "cd_inventory.reservation_validity_hours"
DEFAULT_RESERVATION_HOURS = 72.0
# BRU-INV-19: a named role overrides a reservation (spec section 13: R06
# Branch Manager approves, R17 Inventory Manager)
OVERRIDE_GROUPS = (CONTROLLER_GROUP, APPROVER_BRANCH_GROUP)
NOT_ISSUABLE_TYPES = ("quarantine", "scrap")


def _has_any_group(env, groups) -> bool:
    return env.su or any(env.user.has_group(g) for g in groups)


def _job_context(env, part, location, ref, cls, qty):
    """Resolve a job reference the way an issue does, check what the stock
    class may be used on (BRU-INV-01/03/04: at reservation as at issue,
    FR-INV-011), and rank the demand (BRU-INV-17). Returns
    (job_model, job_id, priority)."""
    probe = env["fix.stock.consumption"].new(
        {
            "service_order_ref": ref or "",
            "product_id": part.id,
            "location_id": location.id,
            "quantity": qty,
            "issue_class": cls if cls in dict(ISSUE_CLASSES) else "owned",
        }
    )
    job_model, job_id = False, 0
    if (ref or "").strip():
        job_model, job_id, _wo = probe._resolve_job()
    probe._check_class_rules(cls, job_model, job_id, env["fix.stock.lot"])
    # D3: a warranty job's stock is held in a warranty store, and only there
    probe._check_warranty_store(job_model, job_id)
    if not job_model:
        return False, 0, "3_internal"
    order = probe._job_service_order(job_model, job_id)
    if order and (
        order.order_category in SLA_CATEGORIES
        or ("sla_policy_id" in order._fields and order.sla_policy_id)
    ):
        return job_model, job_id, "1_sla"
    return job_model, job_id, "2_paid"


# ============================================================ page 4
class FixStockReservation(models.Model):
    """Stock held against a job (FR-INV-019..021, 027)."""

    _name = "fix.stock.reservation"
    _description = "Stock Reservation"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "priority, expires_at, id"

    name = fields.Char(required=True, copy=False, default="New", index=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one(
        "operating.unit", related="location_id.operating_unit_id", store=True
    )
    part_id = fields.Many2one(
        "fix.spare.part", string="Spare Part", required=True, index=True, ondelete="restrict"
    )
    location_id = fields.Many2one(
        "fix.stock.location", string="Location", required=True, index=True, ondelete="restrict"
    )
    reserve_class = fields.Selection(
        ISSUE_CLASSES,
        string="Reserve From Class",
        required=True,
        default="owned",
        help="Brand consignment is reserved only for a warranty job for that brand, "
        "customer-supplied only for that customer's job (FR-INV-011).",
    )
    booked_class = fields.Selection(
        OWNERSHIP_CLASSES, string="Ledger Class", readonly=True, copy=False
    )
    qty = fields.Float(string="Quantity", required=True, default=1.0)
    qty_consumed = fields.Float(string="Issued", readonly=True, copy=False)
    qty_open = fields.Float(string="Still Held", compute="_compute_open", store=True)
    service_order_ref = fields.Char(
        string="Job Reference",
        index=True,
        help="The service order, workshop job or field order the stock is held for. Empty: "
        "internal or stock-building demand (lowest priority).",
    )
    job_model = fields.Char(readonly=True, copy=False)
    job_res_id = fields.Integer(readonly=True, copy=False)
    priority = fields.Selection(
        PRIORITIES, readonly=True, copy=False, index=True, help="BRU-INV-17, from the job."
    )
    expires_at = fields.Datetime(string="Expires", readonly=True, copy=False)
    requested_by_id = fields.Many2one(
        "res.users", string="Requested By", readonly=True, default=lambda self: self.env.user
    )
    reserved_at = fields.Datetime(readonly=True, copy=False)
    displaces_id = fields.Many2one(
        "fix.stock.reservation",
        string="Emergency Override Of",
        domain=[("state", "=", "active")],
        copy=False,
        help="BRU-INV-19: an active reservation of the same stock this one takes over. "
        "Needs an Inventory Controller or Branch Manager and a reason.",
    )
    override_reason = fields.Char(string="Override Reason", copy=False)
    override_by_id = fields.Many2one("res.users", string="Overridden By", readonly=True)
    displaced_by_id = fields.Many2one(
        "fix.stock.reservation", string="Displaced By", readonly=True, copy=False
    )
    release_reason = fields.Char(readonly=True, copy=False)
    released_at = fields.Datetime(readonly=True, copy=False)
    notes = fields.Char()
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Held"),
            ("consumed", "Issued"),
            ("released", "Released"),
            ("expired", "Expired"),
            ("overridden", "Displaced"),
        ],
        default="draft",
        required=True,
        index=True,
        tracking=True,
    )

    _qty_positive = models.Constraint("CHECK (qty > 0)", "A reservation holds a positive quantity")

    _DOC_FIELDS = (
        "part_id",
        "location_id",
        "reserve_class",
        "qty",
        "service_order_ref",
        "displaces_id",
        "override_reason",
        "company_id",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "booked_class",
            "qty_consumed",
            "job_model",
            "job_res_id",
            "priority",
            "expires_at",
            "requested_by_id",
            "reserved_at",
            "override_by_id",
            "displaced_by_id",
            "release_reason",
            "released_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state not in (False, "draft"):
            locked |= set(self._DOC_FIELDS)
        return locked

    @api.depends("qty", "qty_consumed", "state")
    def _compute_open(self):
        for rec in self:
            rec.qty_open = (
                round((rec.qty or 0.0) - (rec.qty_consumed or 0.0), 4)
                if rec.state == "active"
                else 0.0
            )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.stock.reservation")
                    or "RSV/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            frozen = [k for k in self._DOC_FIELDS if k in vals]
            if frozen and any(
                rec.state != "draft" and rec._fix_guard_differs(k, vals[k], rec[k])
                for rec in self
                for k in frozen
            ):
                raise UserError(
                    "A held reservation is fixed: release it and reserve again rather than "
                    "changing its part, location, quantity or job."
                )
        return super().write(vals)

    # -------------------------------------------------------------- helpers
    def _notify(self, body):
        for rec in self:
            partners = rec.requested_by_id.partner_id
            rec.sudo().message_post(
                body=body,
                partner_ids=partners.ids,
                subtype_xmlid="mail.mt_comment",
            )

    def _release_open(self, state, reason, displaced_by=None):
        """Return the still-held quantity to available stock."""
        Onhand = self.env["fix.stock.onhand"]
        for rec in self:
            if rec.state != "active":
                raise UserError("%s is not held: nothing to release." % rec.name)
            open_qty = round(rec.qty - rec.qty_consumed, 4)
            if open_qty > EPS:
                # A06 ERP audit A05: a reservation whose stock already left the
                # ledger (a loss posted before the count rule) is closed on the
                # record with what the ledger still held, never left stuck
                row = Onhand._bucket(rec.part_id, rec.location_id, rec.booked_class)
                held = min(open_qty, row.reserved if row else 0.0)
                if held > EPS:
                    Onhand._fix_unreserve(
                        rec.part_id, rec.location_id, rec.booked_class, held, rec.name
                    )
                if held + EPS < open_qty:
                    reason = "%s (only %s of %s was still held on the ledger)" % (
                        reason,
                        round(held, 4),
                        open_qty,
                    )
            vals = {
                "state": state,
                "release_reason": reason,
                "released_at": fields.Datetime.now(),
            }
            if displaced_by:
                vals["displaced_by_id"] = displaced_by.id
            rec.sudo()._guarded().write(vals)
            publish(
                self.env,
                "stock.reservation_released",
                "fix.stock.reservation",
                rec.id,
                {
                    "reservation": rec.name,
                    "part_number": rec.part_id.part_number,
                    "location_code": rec.location_id.code,
                    "quantity": open_qty,
                    "reason": state,
                    "service_order_ref": rec.service_order_ref or "",
                },
            )

    def _bumpable(self, needed, priority, cls):
        """BRU-INV-17 computed rule: lower-priority holds on the same stock that
        together free `needed`, lowest priority and newest first; empty when
        they cannot cover it."""
        self.ensure_one()
        others = self.sudo().search(
            [
                ("state", "=", "active"),
                ("part_id", "=", self.part_id.id),
                ("location_id", "=", self.location_id.id),
                ("booked_class", "=", cls),
                ("priority", ">", priority),
                ("id", "!=", self.id),
            ],
            order="priority desc, reserved_at desc, id desc",
        )
        chosen = self.browse()
        freed = 0.0
        for other in others:
            if freed + EPS >= needed:
                break
            chosen |= other
            freed += other.qty - other.qty_consumed
        return chosen if freed + EPS >= needed else self.browse()

    # -------------------------------------------------------------- actions
    def action_reserve(self):
        """Hold the stock: class rule, priority, then the ledger reservation."""
        Onhand = self.env["fix.stock.onhand"]
        for rec in self:
            if rec.state != "draft":
                raise UserError("%s is already %s." % (rec.name, rec.state))
            part, location = rec.part_id, rec.location_id
            check_quantity(part, rec.qty, "reservation")
            check_location_usable(location, self.env)
            if location.location_type in NOT_ISSUABLE_TYPES:
                raise UserError(
                    "%s is a %s location: its stock cannot be reserved (BRU-INV-08)."
                    % (location.code, location.location_type)
                )
            if part.state == "obsolete":
                raise UserError("%s is obsolete and cannot be reserved." % part.part_number)
            cls = location_class(location, rec.reserve_class or "owned")
            job_model, job_id, priority = _job_context(
                self.env, part, location, rec.service_order_ref, cls, rec.qty
            )
            displaced = rec.displaces_id
            if displaced:
                if not _has_any_group(self.env, OVERRIDE_GROUPS):
                    raise AccessError(
                        "Only an Inventory Controller or a Branch Manager overrides another "
                        "job's reservation (BRU-INV-19)."
                    )
                if len((rec.override_reason or "").strip()) < 10:
                    raise UserError(
                        "Record why this job takes another job's reserved stock (at least a "
                        "sentence): the override is reported (BRU-INV-19)."
                    )
                if displaced == rec or displaced.state != "active":
                    raise UserError("%s is not an active reservation." % displaced.name)
                if (displaced.part_id, displaced.location_id, displaced.booked_class) != (
                    part,
                    location,
                    cls,
                ):
                    raise UserError(
                        "%s holds other stock (%s at %s): an override takes the same part "
                        "from the same location and class."
                        % (
                            displaced.name,
                            displaced.part_id.part_number,
                            displaced.location_id.code,
                        )
                    )
                displaced._release_open(
                    "overridden",
                    "Emergency override by %s for %s: %s"
                    % (self.env.user.name, rec.service_order_ref or rec.name, rec.override_reason),
                    displaced_by=rec,
                )
                displaced._notify(
                    "Your reservation %s was overridden by %s for job %s. Reason: %s"
                    % (displaced.name, rec.name, rec.service_order_ref or "-", rec.override_reason)
                )
            bucket = Onhand._bucket(part, location, cls)
            available = (bucket.qty - bucket.reserved) if bucket else 0.0
            if rec.qty > available + EPS:
                bumped = rec._bumpable(rec.qty - available, priority, cls)
                if not bumped:
                    raise UserError(
                        "Only %s of %s is available at %s and no lower-priority reservation "
                        "can give way. Raise a backorder, or an Inventory Controller or Branch "
                        "Manager may override a reservation with a reason (BRU-INV-19)."
                        % (round(max(available, 0.0), 4), part.part_number, location.code)
                    )
                for other in bumped:
                    other._release_open(
                        "overridden",
                        "Priority rule (BRU-INV-17): %s (%s) ranks above it"
                        % (rec.service_order_ref or rec.name, dict(PRIORITIES)[priority]),
                        displaced_by=rec,
                    )
                    other._notify(
                        "Your reservation %s gave way to %s, a higher-priority job "
                        "(BRU-INV-17). Reserve again or raise a backorder." % (other.name, rec.name)
                    )
            Onhand._fix_reserve(part, location, cls, rec.qty, rec.name)
            hours = inv_param(self.env, PARAM_RESERVATION_HOURS, DEFAULT_RESERVATION_HOURS)
            now = fields.Datetime.now()
            rec.sudo()._guarded().write(
                {
                    "state": "active",
                    "booked_class": cls,
                    "job_model": job_model or False,
                    "job_res_id": job_id,
                    "priority": priority,
                    "reserved_at": now,
                    "expires_at": now + timedelta(hours=hours or DEFAULT_RESERVATION_HOURS),
                    "override_by_id": self.env.user.id if displaced else False,
                }
            )
            publish(
                self.env,
                "stock.reserved",
                "fix.stock.reservation",
                rec.id,
                {
                    "reservation": rec.name,
                    "part_number": part.part_number,
                    "location_code": location.code,
                    "quantity": rec.qty,
                    "ownership_class": cls,
                    "priority": priority,
                    "service_order_ref": rec.service_order_ref or "",
                    "override_of": displaced.name or "",
                },
            )
        return True

    def action_release(self, note=None):
        """The requester (or an Inventory Controller) gives the stock back."""
        for rec in self:
            if rec.requested_by_id != self.env.user and not _has_any_group(
                self.env, OVERRIDE_GROUPS
            ):
                raise AccessError(
                    "Only %s, who reserved it, or an Inventory Controller releases %s."
                    % (rec.requested_by_id.name, rec.name)
                )
            rec._release_open("released", note or "Released by %s" % self.env.user.name)
        return True

    @api.model
    def _cron_expire(self):
        """BRU-INV-18 / FR-INV-021: a hold not issued in time returns to stock
        and the requester is told."""
        due = self.search([("state", "=", "active"), ("expires_at", "<", fields.Datetime.now())])
        done = 0
        for rec in due:
            # A06 ERP audit A05: one reservation that cannot be released never
            # stops the sweep for the others
            try:
                with self.env.cr.savepoint():
                    rec._release_open("expired", "Not issued before %s" % rec.expires_at)
                    rec._notify(
                        "Reservation %s of %s at %s expired unissued and went back to stock "
                        "(BRU-INV-18)." % (rec.name, rec.part_id.part_number, rec.location_id.code)
                    )
                done += 1
            except Exception:
                _logger.exception("reservation %s could not be expired", rec.name)
        return done

    def _fix_consume(self, qty, consumption):
        """An issue draws its own reservation: unreserve exactly what it takes
        so the issue's unreserved-stock check finds it."""
        self.ensure_one()
        if self.state != "active":
            raise UserError("Reservation %s is %s, not held." % (self.name, self.state))
        open_qty = round(self.qty - self.qty_consumed, 4)
        if qty > open_qty + EPS:
            raise UserError(
                "Reservation %s holds %s; this issue takes %s." % (self.name, open_qty, qty)
            )
        self.env["fix.stock.onhand"]._fix_unreserve(
            self.part_id, self.location_id, self.booked_class, qty, consumption.name
        )
        consumed = round(self.qty_consumed + qty, 4)
        vals = {"qty_consumed": consumed}
        if consumed + EPS >= self.qty:
            vals["state"] = "consumed"
        self.sudo()._guarded().write(vals)


class FixStockConsumptionReservation(models.Model):
    """FR-INV-022: an issue takes the stock reserved for its job."""

    _inherit = "fix.stock.consumption"

    reservation_id = fields.Many2one(
        "fix.stock.reservation",
        string="From Reservation",
        domain=[("state", "=", "active")],
        copy=False,
        help="Issue the stock held for this job. Same part, location and class.",
    )

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state not in (False, "draft"):
            locked |= {"reservation_id"}
        return locked

    def write(self, vals):
        if (
            self
            and "reservation_id" in vals
            and not self._fix_guard_open()
            and any(
                rec.state != "draft"
                and rec._fix_guard_differs(
                    "reservation_id", vals["reservation_id"], rec.reservation_id
                )
                for rec in self
            )
        ):
            raise UserError("An issued part is final: its reservation cannot change.")
        return super().write(vals)

    def action_scan_and_consume(self) -> dict:
        reservation = self.reservation_id
        if reservation and self.state == "draft":
            cls = location_class(self.location_id, self.issue_class or "owned")
            if (reservation.part_id, reservation.location_id, reservation.booked_class) != (
                self.product_id,
                self.location_id,
                cls,
            ):
                raise UserError(
                    "Reservation %s holds %s at %s (%s): this issue is for other stock."
                    % (
                        reservation.name,
                        reservation.part_id.part_number,
                        reservation.location_id.code,
                        reservation.booked_class,
                    )
                )
            held_for = (reservation.service_order_ref or "").strip()
            if held_for and held_for != (self.service_order_ref or "").strip():
                raise UserError(
                    "Reservation %s is held for job %s, not %s: another job's stock is taken "
                    "only by an override (BRU-INV-19)."
                    % (reservation.name, held_for, self.service_order_ref)
                )
            reservation._fix_consume(self.quantity, self)
        return super().action_scan_and_consume()


# ============================================================ page 5
class FixStockBackorder(models.Model):
    """FR-INV-025 / AUT-INV-02: the part is not at hand; the backorder finds
    it in the network (a transfer) or buys it (an M16 requisition) and holds
    the job's parts-wait until the stock is reserved for it."""

    _name = "fix.stock.backorder"
    _description = "Stock Backorder"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "create_date desc, id desc"

    name = fields.Char(required=True, copy=False, default="New", index=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one(
        "operating.unit", related="location_id.operating_unit_id", store=True
    )
    part_id = fields.Many2one(
        "fix.spare.part", string="Spare Part", required=True, index=True, ondelete="restrict"
    )
    location_id = fields.Many2one(
        "fix.stock.location",
        string="Needed At",
        required=True,
        index=True,
        ondelete="restrict",
    )
    qty = fields.Float(string="Quantity", required=True, default=1.0)
    service_order_ref = fields.Char(string="Job Reference", index=True)
    needed_by = fields.Date(string="Needed By")
    notes = fields.Char()
    source_location_id = fields.Many2one(
        "fix.stock.location",
        string="Network Source",
        compute="_compute_source",
        help="The location holding the most available stock of this part (AUT-INV-02).",
    )
    source_available = fields.Float(string="Available There", compute="_compute_source")
    transfer_id = fields.Many2one("fix.stock.transfer", readonly=True, copy=False)
    requisition_id = fields.Many2one("fix.requisition", readonly=True, copy=False)
    reservation_id = fields.Many2one("fix.stock.reservation", readonly=True, copy=False)
    raised_by_id = fields.Many2one(
        "res.users", string="Raised By", readonly=True, default=lambda self: self.env.user
    )
    cancel_reason = fields.Char(readonly=True, copy=False)
    state = fields.Selection(
        [
            ("open", "Open (parts wait)"),
            ("transfer", "Transfer Raised"),
            ("requisition", "Requisition Raised"),
            ("fulfilled", "Fulfilled"),
            ("cancelled", "Cancelled"),
        ],
        default="open",
        required=True,
        index=True,
        tracking=True,
    )

    _qty_positive = models.Constraint("CHECK (qty > 0)", "A backorder is for a positive quantity")

    _DOC_FIELDS = ("part_id", "location_id", "qty", "service_order_ref", "company_id")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "transfer_id",
            "requisition_id",
            "reservation_id",
            "raised_by_id",
            "cancel_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.id:
            locked |= set(self._DOC_FIELDS)
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open():
            frozen = [k for k in self._DOC_FIELDS if k in vals]
            if frozen and any(
                rec._fix_guard_differs(k, vals[k], rec[k]) for rec in self for k in frozen
            ):
                raise UserError("A backorder is fixed once raised: cancel it and raise a new one.")
        return super().write(vals)

    @api.model
    def _available(self, part, location):
        rows = (
            self.env["fix.stock.onhand"]
            .sudo()
            .search(
                [
                    ("part_id", "=", part.id),
                    ("location_id", "=", location.id),
                    ("stock_status", "=", "unrestricted"),
                    ("ownership_class", "in", ("owned", "van")),
                ]
            )
        )
        return round(sum(r.qty - r.reserved for r in rows), 4)

    @api.depends("part_id", "location_id", "qty")
    def _compute_source(self):
        Onhand = self.env["fix.stock.onhand"].sudo()
        for rec in self:
            rec.source_location_id = False
            rec.source_available = 0.0
            if not rec.part_id:
                continue
            totals = {}
            for row in Onhand.search(
                [
                    ("part_id", "=", rec.part_id.id),
                    ("stock_status", "=", "unrestricted"),
                    ("ownership_class", "in", ("owned", "van")),
                    ("location_id", "!=", rec.location_id.id or 0),
                    ("location_id.location_type", "not in", NOT_ISSUABLE_TYPES),
                    ("location_id.state", "=", "active"),
                    ("company_id", "=", rec.company_id.id or self.env.company.id),
                ]
            ):
                free = row.qty - row.reserved
                if free > EPS:
                    totals[row.location_id] = totals.get(row.location_id, 0.0) + free
            if totals:
                best = max(totals, key=lambda loc: (totals[loc], -loc.id))
                rec.source_location_id = best
                rec.source_available = round(totals[best], 4)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.stock.backorder") or "BKO/New"
                )
        records = super().create(vals_list)
        for rec in records:
            check_quantity(rec.part_id, rec.qty, "backorder")
            check_location_usable(rec.location_id, self.env)
            if rec.service_order_ref:
                # a backorder that names a job names a real one
                _job_context(
                    self.env, rec.part_id, rec.location_id, rec.service_order_ref, "owned", rec.qty
                )
            here = self._available(rec.part_id, rec.location_id)
            if here + EPS >= rec.qty:
                raise UserError(
                    "%s of %s is available at %s: reserve it instead of backordering "
                    "(FR-INV-025)." % (here, rec.part_id.part_number, rec.location_id.code)
                )
            publish(
                self.env,
                "stock.stockout",
                "fix.stock.backorder",
                rec.id,
                {
                    "backorder": rec.name,
                    "part_number": rec.part_id.part_number,
                    "location_code": rec.location_id.code,
                    "unmet_quantity": round(rec.qty - max(here, 0.0), 4),
                    "service_order_ref": rec.service_order_ref or "",
                },
            )
        return records

    def _require_open(self):
        for rec in self:
            if rec.state != "open":
                raise UserError("%s is %s: it is no longer open." % (rec.name, rec.state))

    def action_raise_transfer(self):
        """Pull the part from the network source (FR-INV-054 lifecycle)."""
        self._require_open()
        for rec in self:
            source = rec.source_location_id
            if not source or rec.source_available + EPS < rec.qty:
                raise UserError(
                    "No location holds %s available of %s: raise a requisition instead."
                    % (rec.qty, rec.part_id.part_number)
                )
            transfer = self.env["fix.stock.transfer"].create(
                {
                    "from_location_id": source.id,
                    "to_location_id": rec.location_id.id,
                    "operating_unit_id": rec.location_id.operating_unit_id.id or False,
                    "line_ids": [(0, 0, {"part_id": rec.part_id.id, "qty": rec.qty})],
                }
            )
            rec.sudo()._guarded().write({"state": "transfer", "transfer_id": transfer.id})
            rec.sudo().message_post(
                body="Transfer %s raised from %s (%s available there)."
                % (transfer.name, source.code, rec.source_available)
            )
        return True

    def action_raise_requisition(self):
        """Buy it (M16) - only when the network cannot supply it, so a branch
        does not buy what another holds (spec section 7.2)."""
        self._require_open()
        Employee = self.env["hr.employee"].sudo()
        for rec in self:
            if rec.source_location_id and rec.source_available + EPS >= rec.qty:
                raise UserError(
                    "%s holds %s available of %s: raise a transfer, not a purchase."
                    % (rec.source_location_id.code, rec.source_available, rec.part_id.part_number)
                )
            if "fix.requisition" not in self.env:
                raise UserError("M16 requisitions are not installed.")
            if rec.part_id.state != "active":
                raise UserError(
                    "%s is %s: it is not bought again."
                    % (rec.part_id.part_number, rec.part_id.state)
                )
            requester = Employee.search([("user_id", "=", self.env.uid)], limit=1)
            if not requester:
                raise UserError(
                    "You have no employee record to raise a requisition in the name of."
                )
            location = rec.location_id
            part = rec.part_id.sudo()
            requisition = (
                self.env["fix.requisition"]
                .sudo()
                .create(
                    {
                        "company_id": rec.company_id.id,
                        "operating_unit_id": location.operating_unit_id.id or False,
                        "branch_id": location.branch_id.id or False,
                        "requested_by": requester.id,
                        "product_id": part.product_id.id or False,
                        "qty": rec.qty,
                        "description": "Backorder %s: %s %s of %s for %s at %s"
                        % (
                            rec.name,
                            rec.qty,
                            part.uom or "PCS",
                            part.part_number,
                            rec.service_order_ref or "stock",
                            location.code,
                        ),
                        "estimate_amount": round(
                            rec.qty * (part.average_cost or part.unit_cost or 0.0), 2
                        ),
                        "urgency": "urgent",
                    }
                )
            )
            rec.sudo()._guarded().write({"state": "requisition", "requisition_id": requisition.id})
        return True

    def action_fulfil(self):
        """The stock has arrived: hold it for the job and end the parts wait."""
        for rec in self:
            if rec.state not in ("open", "transfer", "requisition"):
                raise UserError("%s is %s." % (rec.name, rec.state))
            here = self._available(rec.part_id, rec.location_id)
            if here + EPS < rec.qty:
                raise UserError(
                    "Only %s of %s is available at %s: the backorder stays open."
                    % (max(here, 0.0), rec.part_id.part_number, rec.location_id.code)
                )
            reservation = self.env["fix.stock.reservation"]
            if rec.service_order_ref:
                reservation = reservation.create(
                    {
                        "part_id": rec.part_id.id,
                        "location_id": rec.location_id.id,
                        "qty": rec.qty,
                        "service_order_ref": rec.service_order_ref,
                        "notes": "From backorder %s" % rec.name,
                    }
                )
                reservation.action_reserve()
            rec.sudo()._guarded().write(
                {"state": "fulfilled", "reservation_id": reservation.id or False}
            )
        return True

    def action_cancel(self, note=None):
        for rec in self:
            if rec.state in ("fulfilled", "cancelled"):
                raise UserError("%s is %s." % (rec.name, rec.state))
            if not (note or "").strip():
                raise UserError("Give the reason the backorder is cancelled.")
            rec.sudo()._guarded().write({"state": "cancelled", "cancel_reason": note})
        return True


# ============================================================ page 7
RECALL_REASONS = [
    ("recall", "Brand / supplier recall"),
    ("defect", "Batch defect"),
    ("counterfeit", "Counterfeit / grey-market suspicion"),
]
QUARANTINE_REASON = {"recall": "defective", "defect": "defective", "counterfeit": "suspect"}


class FixStockRecall(models.Model):
    """FR-INV-040 / AUT-INV-14: find and quarantine every affected unit across
    all locations and vans in one transaction, and list the jobs already
    consuming it."""

    _name = "fix.stock.recall"
    _description = "Stock Recall"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "create_date desc, id desc"

    name = fields.Char(required=True, copy=False, default="New", index=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    part_id = fields.Many2one(
        "fix.spare.part", string="Spare Part", required=True, index=True, ondelete="restrict"
    )
    scope = fields.Selection(
        [("all", "Every unit of the part"), ("serials", "Named serials / lots")],
        required=True,
        default="all",
    )
    lot_ids = fields.Many2many(
        "fix.stock.lot",
        "fix_stock_recall_lot_rel",
        "recall_id",
        "lot_id",
        string="Serials / Lots",
    )
    reason = fields.Selection(RECALL_REASONS, required=True, default="recall")
    reference = fields.Char(string="Bulletin / Notice Reference")
    notes = fields.Text()
    declared_by_id = fields.Many2one(
        "res.users", string="Declared By", readonly=True, default=lambda self: self.env.user
    )
    executed_by_id = fields.Many2one("res.users", string="Executed By", readonly=True)
    executed_at = fields.Datetime(readonly=True)
    quarantine_ids = fields.Many2many(
        "fix.stock.quarantine",
        "fix_stock_recall_quarantine_rel",
        "recall_id",
        "quarantine_id",
        string="Quarantines Raised",
        readonly=True,
    )
    affected_consumption_ids = fields.Many2many(
        "fix.stock.consumption",
        "fix_stock_recall_consumption_rel",
        "recall_id",
        "consumption_id",
        string="Jobs Already Consuming It",
        readonly=True,
    )
    qty_quarantined = fields.Float(string="Quarantined", readonly=True)
    qty_not_reached = fields.Float(
        string="Not Reached",
        readonly=True,
        help="Units the sweep could not quarantine (reserved by a wave pick, in warehouse "
        "bins, in transit or issued): the worklist below names them.",
    )
    worklist = fields.Text(string="Manual Sweep Worklist", readonly=True)
    state = fields.Selection(
        [("draft", "Draft"), ("executed", "Executed"), ("cancelled", "Cancelled")],
        default="draft",
        required=True,
        index=True,
        tracking=True,
    )

    _DOC_FIELDS = ("part_id", "scope", "lot_ids", "reason", "company_id")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "declared_by_id",
            "executed_by_id",
            "executed_at",
            "quarantine_ids",
            "affected_consumption_ids",
            "qty_quarantined",
            "qty_not_reached",
            "worklist",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state not in (False, "draft"):
            locked |= set(self._DOC_FIELDS)
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open():
            frozen = [k for k in self._DOC_FIELDS if k in vals]
            if frozen and any(
                rec.state != "draft" and rec._fix_guard_differs(k, vals[k], rec[k])
                for rec in self
                for k in frozen
            ):
                raise UserError("An executed recall is a record: it cannot be edited.")
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.stock.recall") or "RCL/New"
                )
        return super().create(vals_list)

    @api.constrains("scope", "lot_ids", "part_id")
    def _check_lots(self):
        for rec in self:
            if rec.scope == "serials" and not rec.lot_ids:
                raise ValidationError("Name the serials or lots the recall covers.")
            wrong = rec.lot_ids - rec.lot_ids.filtered_domain([("part_id", "=", rec.part_id.id)])
            if wrong:
                raise ValidationError(
                    "%s are not serials of %s."
                    % (", ".join(wrong.mapped("name")), rec.part_id.part_number)
                )

    def _target_lots(self):
        self.ensure_one()
        if self.scope == "serials":
            return self.lot_ids
        if self.part_id.is_serialized:
            return self.env["fix.stock.lot"].sudo().search([("part_id", "=", self.part_id.id)])
        return self.env["fix.stock.lot"]

    def _quarantine(self, vals, missed, label):
        """One quarantine; a refusal (bins, inactive location) goes on the
        worklist instead of stopping the sweep."""
        Quarantine = self.env["fix.stock.quarantine"].sudo()
        try:
            with self.env.cr.savepoint():
                return Quarantine.create(vals)
        except (UserError, ValidationError, AccessError) as exc:
            missed.append("%s: %s" % (label, exc.args[0] if exc.args else exc))
            return Quarantine.browse()

    def action_execute(self):
        if not _has_any_group(self.env, (CONTROLLER_GROUP,)):
            raise AccessError("Only an Inventory Controller executes a stock recall.")
        Onhand = self.env["fix.stock.onhand"].sudo()
        Reservation = self.env["fix.stock.reservation"].sudo()
        today = fields.Date.context_today(self)
        for rec in self:
            if rec.state != "draft":
                raise UserError("%s is already %s." % (rec.name, rec.state))
            part = rec.part_id
            reason = QUARANTINE_REASON[rec.reason]
            note = "Recall %s%s" % (rec.name, (" (%s)" % rec.reference) if rec.reference else "")
            raised = self.env["fix.stock.quarantine"]
            missed = []
            quarantined = 0.0
            not_reached = 0.0
            lots = rec._target_lots()
            # a held reservation would let recalled stock be issued: release it
            held = Reservation.search([("state", "=", "active"), ("part_id", "=", part.id)])
            if rec.scope == "serials":
                held = held.filtered_domain([("location_id", "in", lots.location_id.ids)])
            for res in held:
                res._release_open("released", "Recalled by %s" % rec.name)
                res._notify(
                    "Reservation %s was released: %s is recalled (%s)."
                    % (res.name, part.part_number, rec.name)
                )
            if lots or part.is_serialized:
                for lot in lots:
                    if lot.status != "in_stock":
                        not_reached += lot.qty or 1.0
                        missed.append(
                            "%s: %s at %s"
                            % (
                                lot.name,
                                dict(lot._fields["status"].selection).get(lot.status),
                                lot.location_id.code or "-",
                            )
                        )
                        continue
                    bucket = Onhand.search(
                        [
                            ("part_id", "=", part.id),
                            ("location_id", "=", lot.location_id.id),
                            ("stock_status", "=", "unrestricted"),
                        ],
                        order="ownership_class",
                    ).filtered(lambda r, need=(lot.qty or 1.0): r.qty - r.reserved >= need - EPS)[
                        :1
                    ]
                    if not bucket:
                        not_reached += lot.qty or 1.0
                        missed.append(
                            "%s at %s: reserved by a pick" % (lot.name, lot.location_id.code)
                        )
                        continue
                    q = rec._quarantine(
                        {
                            "part_id": part.id,
                            "location_id": lot.location_id.id,
                            "ownership_class": bucket.ownership_class,
                            "lot_id": lot.id,
                            "qty": lot.qty or 1.0,
                            "reason": reason,
                            "quarantined_on": today,
                            "notes": note,
                        },
                        missed,
                        "%s at %s" % (lot.name, lot.location_id.code),
                    )
                    if q:
                        raised |= q
                        quarantined += q.qty
                    else:
                        not_reached += lot.qty or 1.0
            else:
                for row in Onhand.search([("part_id", "=", part.id)]):
                    if row.stock_status == "quarantine":
                        continue
                    if row.stock_status != "unrestricted":
                        not_reached += row.qty
                        missed.append(
                            "%s %s at %s: %s"
                            % (row.qty, row.ownership_class, row.location_id.code, row.stock_status)
                        )
                        continue
                    if row.reserved > EPS:
                        not_reached += row.reserved
                        missed.append(
                            "%s at %s: reserved by a wave pick"
                            % (row.reserved, row.location_id.code)
                        )
                    free = round(row.qty - row.reserved, 4)
                    if free <= EPS:
                        continue
                    q = rec._quarantine(
                        {
                            "part_id": part.id,
                            "location_id": row.location_id.id,
                            "ownership_class": row.ownership_class,
                            "qty": free,
                            "reason": reason,
                            "quarantined_on": today,
                            "notes": note,
                        },
                        missed,
                        "%s %s at %s" % (free, row.ownership_class, row.location_id.code),
                    )
                    if q:
                        raised |= q
                        quarantined += free
                    else:
                        not_reached += free
            consumed = (
                self.env["fix.stock.consumption"]
                .sudo()
                .search(
                    [("product_id", "=", part.id), ("state", "=", "consumed")]
                    + ([("lot_id", "in", lots.ids)] if rec.scope == "serials" else [])
                )
            )
            rec.sudo()._guarded().write(
                {
                    "state": "executed",
                    "executed_by_id": self.env.user.id,
                    "executed_at": fields.Datetime.now(),
                    "quarantine_ids": [(6, 0, raised.ids)],
                    "affected_consumption_ids": [(6, 0, consumed.ids)],
                    "qty_quarantined": round(quarantined, 4),
                    "qty_not_reached": round(not_reached, 4),
                    "worklist": "\n".join(missed) or False,
                }
            )
            publish(
                self.env,
                "stock.quarantined",
                "fix.stock.recall",
                rec.id,
                {
                    "recall": rec.name,
                    "part_number": part.part_number,
                    "reason": rec.reason,
                    "quantity": round(quarantined, 4),
                    "not_reached": round(not_reached, 4),
                    "jobs_affected": len(consumed),
                },
            )
        return True

    def action_cancel(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError(
                    "%s is %s: an executed recall is released quarantine by quarantine."
                    % (rec.name, rec.state)
                )
            rec.sudo()._guarded().write({"state": "cancelled"})
        return True


# ============================================================ page 3
class FixConsignmentReconciliation(models.Model):
    """FR-INV-012 / 014 / AUT-INV-07: the per-brand consignment statement,
    reconciled to the brand's own figures and acknowledged by the brand."""

    _name = "fix.consignment.reconciliation"
    _description = "Brand Consignment Reconciliation"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "as_at desc, id desc"

    name = fields.Char(required=True, copy=False, default="New", index=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    brand_id = fields.Many2one("fix.brand", string="Brand", required=True, index=True)
    period_start = fields.Date(
        string="Period From",
        required=True,
        default=lambda self: fields.Date.context_today(self).replace(day=1),
    )
    as_at = fields.Date(string="Statement As At", readonly=True, copy=False)
    previous_id = fields.Many2one(
        "fix.consignment.reconciliation", string="Previous Statement", readonly=True, copy=False
    )
    line_ids = fields.One2many(
        "fix.consignment.reconciliation.line", "reconciliation_id", string="Parts"
    )
    opening_qty = fields.Float(string="Opening", compute="_compute_totals", store=True)
    received_qty = fields.Float(string="Received", compute="_compute_totals", store=True)
    consumed_qty = fields.Float(
        string="Consumed on Warranty", compute="_compute_totals", store=True
    )
    damaged_qty = fields.Float(
        string="Damaged / Written Off", compute="_compute_totals", store=True
    )
    other_qty = fields.Float(string="Other Movements", compute="_compute_totals", store=True)
    closing_qty = fields.Float(string="Closing (ledger)", compute="_compute_totals", store=True)
    brand_qty = fields.Float(string="Closing (brand)", compute="_compute_totals", store=True)
    variance_qty = fields.Float(string="Variance", compute="_compute_totals", store=True)
    statement_ref = fields.Char(string="Brand Statement Reference")
    brand_acknowledged_by = fields.Char(string="Acknowledged By (brand)")
    brand_acknowledged_on = fields.Date(string="Brand Acknowledged On")
    variance_note = fields.Text(string="Variance Explanation")
    prepared_by_id = fields.Many2one("res.users", string="Prepared By", readonly=True)
    recorded_by_id = fields.Many2one(
        "res.users", string="Acknowledgement Recorded By", readonly=True
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("computed", "Computed"),
            ("submitted", "Sent to Brand"),
            ("acknowledged", "Acknowledged"),
        ],
        default="draft",
        required=True,
        index=True,
        tracking=True,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "as_at",
            "previous_id",
            "prepared_by_id",
            "recorded_by_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state not in (False, "draft"):
            locked |= {"brand_id", "period_start", "company_id"}
        if len(self) == 1 and self.state == "acknowledged":
            locked |= {
                "statement_ref",
                "brand_acknowledged_by",
                "brand_acknowledged_on",
                "variance_note",
            }
        return locked

    @api.depends(
        "line_ids.opening_qty",
        "line_ids.received_qty",
        "line_ids.consumed_qty",
        "line_ids.damaged_qty",
        "line_ids.other_qty",
        "line_ids.closing_qty",
        "line_ids.brand_qty",
    )
    def _compute_totals(self):
        for rec in self:
            lines = rec.line_ids
            for name in (
                "opening_qty",
                "received_qty",
                "consumed_qty",
                "damaged_qty",
                "other_qty",
                "closing_qty",
                "brand_qty",
            ):
                rec[name] = round(sum(lines.mapped(name)), 4)
            rec.variance_qty = round(rec.brand_qty - rec.closing_qty, 4)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.consignment.reconciliation")
                    or "CSR/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self:
                if rec.state != "draft" and any(
                    k in vals and rec._fix_guard_differs(k, vals[k], rec[k])
                    for k in ("brand_id", "period_start", "company_id")
                ):
                    raise UserError(
                        "Recompute a new statement rather than changing its brand or period."
                    )
                if rec.state == "acknowledged" and any(
                    k in vals and rec._fix_guard_differs(k, vals[k], rec[k])
                    for k in (
                        "statement_ref",
                        "brand_acknowledged_by",
                        "brand_acknowledged_on",
                        "variance_note",
                    )
                ):
                    raise UserError("An acknowledged statement is final.")
        return super().write(vals)

    def _brand_parts(self):
        self.ensure_one()
        name = (self.brand_id.name or "").strip()
        Part = self.env["fix.spare.part"].sudo().with_context(active_test=False)
        domain = [("brand_id", "=", self.brand_id.id)]
        if name:
            domain = ["|", ("brand_id", "=", self.brand_id.id), ("device_brand", "=ilike", name)]
        return Part.search([*domain, ("company_id", "in", [self.company_id.id, False])])

    def action_compute(self):
        """The statement from the ledger: closing now, what came in and what
        went on warranty jobs since the period began, the opening carried from
        the brand's previous acknowledged statement."""
        for rec in self:
            if rec.state not in ("draft", "computed"):
                raise UserError("%s was sent to the brand: it is not recomputed." % rec.name)
            today = fields.Date.context_today(rec)
            if rec.period_start > today:
                raise UserError("The period cannot start in the future.")
            parts = rec._brand_parts()
            start = fields.Datetime.to_datetime(rec.period_start)
            previous = self.sudo().search(
                [
                    ("brand_id", "=", rec.brand_id.id),
                    ("company_id", "=", rec.company_id.id),
                    ("state", "=", "acknowledged"),
                    ("id", "!=", rec.id),
                ],
                order="as_at desc, id desc",
                limit=1,
            )
            if previous and rec.period_start <= previous.as_at:
                # the opening carries from that statement: an overlapping
                # period would count its receipts and issues twice
                raise UserError(
                    "%s already covers %s up to %s: start this period after it."
                    % (previous.name, rec.brand_id.name, previous.as_at)
                )
            carried = {line.part_id.id: line.closing_qty for line in previous.line_ids}
            Onhand = self.env["fix.stock.onhand"].sudo()
            closing, received, consumed, damaged = {}, {}, {}, {}
            for row in Onhand.search(
                [
                    ("part_id", "in", parts.ids),
                    ("ownership_class", "=", "consignment"),
                    ("company_id", "=", rec.company_id.id),
                ]
            ):
                closing[row.part_id.id] = closing.get(row.part_id.id, 0.0) + row.qty
            for line in (
                self.env["fix.stock.receipt.line"]
                .sudo()
                .search(
                    [
                        ("part_id", "in", parts.ids),
                        ("is_posted", "=", True),
                        ("receipt_id.ownership_class", "=", "consignment"),
                        ("receipt_id.posted_at", ">=", start),
                        ("receipt_id.company_id", "=", rec.company_id.id),
                    ]
                )
            ):
                received[line.part_id.id] = received.get(line.part_id.id, 0.0) + line.qty_accepted
            for issue in (
                self.env["fix.stock.consumption"]
                .sudo()
                .search(
                    [
                        ("product_id", "in", parts.ids),
                        ("state", "=", "consumed"),
                        ("ownership_class", "=", "consignment"),
                        ("consumed_at", ">=", start),
                        ("company_id", "=", rec.company_id.id),
                    ]
                )
            ):
                consumed[issue.product_id.id] = (
                    consumed.get(issue.product_id.id, 0.0) + issue.quantity
                )
            for q in (
                self.env["fix.stock.quarantine"]
                .sudo()
                .search(
                    [
                        ("part_id", "in", parts.ids),
                        ("state", "=", "scrapped"),
                        ("ownership_class", "=", "consignment"),
                        ("scrapped_at", ">=", start),
                        ("company_id", "=", rec.company_id.id),
                    ]
                )
            ):
                damaged[q.part_id.id] = damaged.get(q.part_id.id, 0.0) + q.qty
            ids = set(closing) | set(received) | set(consumed) | set(damaged) | set(carried)
            lines = []
            for pid in sorted(ids):
                close = round(closing.get(pid, 0.0), 4)
                rcv = round(received.get(pid, 0.0), 4)
                cns = round(consumed.get(pid, 0.0), 4)
                dmg = round(damaged.get(pid, 0.0), 4)
                if pid in carried:
                    opening = round(carried[pid], 4)
                else:
                    opening = round(close - rcv + cns + dmg, 4)
                lines.append(
                    (
                        0,
                        0,
                        {
                            "part_id": pid,
                            "opening_qty": opening,
                            "received_qty": rcv,
                            "consumed_qty": cns,
                            "damaged_qty": dmg,
                            "other_qty": round(close - opening - rcv + cns + dmg, 4),
                            "closing_qty": close,
                            "brand_qty": close,
                        },
                    )
                )
            rec.line_ids.sudo().unlink()
            rec.sudo()._guarded().write(
                {
                    "line_ids": lines,
                    "as_at": today,
                    "previous_id": previous.id or False,
                    "state": "computed",
                    "prepared_by_id": self.env.user.id,
                }
            )
        return True

    def action_submit(self):
        for rec in self:
            if rec.state != "computed":
                raise UserError("Compute %s before sending it to the brand." % rec.name)
            rec.sudo()._guarded().write({"state": "submitted"})
        return True

    def action_acknowledge(self):
        """Record the brand's acknowledgement (two persons: not the preparer)."""
        if not _has_any_group(self.env, (CONTROLLER_GROUP,)):
            raise AccessError("Only an Inventory Controller records a brand's acknowledgement.")
        for rec in self:
            if rec.state != "submitted":
                raise UserError("%s has not been sent to the brand." % rec.name)
            if rec.prepared_by_id == self.env.user and not self.env.su:
                raise UserError(
                    "%s prepared %s: a second person records the brand's acknowledgement."
                    % (self.env.user.name, rec.name)
                )
            missing = [
                label
                for name, label in (
                    ("statement_ref", "the brand's statement reference"),
                    ("brand_acknowledged_by", "who acknowledged it for the brand"),
                    ("brand_acknowledged_on", "the acknowledgement date"),
                )
                if not rec[name]
            ]
            if missing:
                raise UserError("Record %s." % ", ".join(missing))
            if abs(rec.variance_qty) > EPS and len((rec.variance_note or "").strip()) < 10:
                raise UserError(
                    "The brand's figures differ from the ledger by %s: explain the variance."
                    % rec.variance_qty
                )
            rec.sudo()._guarded().write(
                {"state": "acknowledged", "recorded_by_id": self.env.user.id}
            )
            publish(
                self.env,
                "stock.consignment_reconciled",
                "fix.consignment.reconciliation",
                rec.id,
                {
                    "statement": rec.name,
                    "brand": rec.brand_id.name,
                    "as_at": str(rec.as_at),
                    "closing_ledger": rec.closing_qty,
                    "closing_brand": rec.brand_qty,
                    "variance": rec.variance_qty,
                },
            )
        return True


class FixConsignmentReconciliationLine(models.Model):
    _name = "fix.consignment.reconciliation.line"
    _description = "Brand Consignment Reconciliation Line"
    _inherit = ["fix.guarded.mixin"]
    _order = "reconciliation_id, part_id"

    reconciliation_id = fields.Many2one(
        "fix.consignment.reconciliation", required=True, ondelete="cascade", index=True
    )
    part_id = fields.Many2one("fix.spare.part", string="Spare Part", required=True)
    opening_qty = fields.Float(string="Opening", readonly=True)
    received_qty = fields.Float(string="Received", readonly=True)
    consumed_qty = fields.Float(string="Consumed", readonly=True)
    damaged_qty = fields.Float(string="Damaged", readonly=True)
    other_qty = fields.Float(
        string="Other",
        readonly=True,
        help="Returns to the brand, transfers out, count adjustments.",
    )
    closing_qty = fields.Float(string="Closing (ledger)", readonly=True)
    brand_qty = fields.Float(string="Closing (brand)")
    variance_qty = fields.Float(string="Variance", compute="_compute_variance", store=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "reconciliation_id",
            "part_id",
            "opening_qty",
            "received_qty",
            "consumed_qty",
            "damaged_qty",
            "other_qty",
            "closing_qty",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self[:1].reconciliation_id.state == "acknowledged":
            locked |= {"brand_qty"}
        return locked

    @api.depends("brand_qty", "closing_qty")
    def _compute_variance(self):
        for line in self:
            line.variance_qty = round(line.brand_qty - line.closing_qty, 4)

    def write(self, vals):
        if (
            self
            and "brand_qty" in vals
            and not self._fix_guard_open()
            and any(line.reconciliation_id.state not in ("computed", "submitted") for line in self)
        ):
            raise UserError("The brand's figures are entered on a computed or sent statement only.")
        return super().write(vals)
