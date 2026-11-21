# fix_wms_ops_xcontrols — A06 Supply Chain ERP audit (20 Nov 2026), stream M41.
# The file name sorts after fix_wms_ops_spec_flow on purpose: these classes
# extend models the earlier fix_wms_* files define.
#
# BRU-WMS-01 says M41 never authors a stock quantity and a bin never holds more
# than M15's ledger. The audit found the ways it still did, and the owner's
# defaults (O1-O7) decide the fix:
#   * F01 / X16 / F22 (O1): nothing leaves the warehouse without an M15 document.
#     Typed demand becomes an M15 transfer from the warehouse at build time, job
#     demand an M15 job issue; the wave and the cross-dock hand their stock to
#     that document, which makes the only ledger movement.
#   * F07 (O2): stock already on hand (legacy, or arrived before the layout) is
#     slotted by a supervisor's opening slot load, with a reason and NO ledger
#     effect, capped at what the ledger holds outside the bins.
#   * F06: the fields that tie a zone or bin to the ledger freeze once it holds
#     stock.
#   * F09: an ordinary M15 count at a WMS location takes a loss only out of the
#     stock no bin holds (the bins are counted by floor counts).
#   * F26: the spec's inbound-arrival event.
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

from .fix_inventory_approval import check_quantity, location_class, require_supervisor
from .fix_wms_ops import (
    EPS,
    NO_PUTAWAY_ZONE_TYPES,
    SLOT_CLASSES,
    _bin_location,
    bin_class,
    check_slot_cap,
    slotted_qty,
    unslotted_qty,
)
from .fix_wms_ops_spec import _seq


def _value_differs(rec, name, value) -> bool:
    field = rec._fields[name]
    if field.type == "many2one":
        return (rec[name].id or False) != (value or False)
    return (rec[name] or False) != (value or False)


def _holds_stock(env, domain) -> bool:
    return bool(
        env["fix.wms.slot"]
        .sudo()
        .search_count([*domain, "|", ("qty", ">", EPS), ("reserved_qty", ">", EPS)])
    )


# ===================================================================== demand
class FixWmsDemandDocuments(models.Model):
    """F01 / O1: every outbound demand leaves through an M15 document."""

    _inherit = "fix.wms.outbound.demand"

    state = fields.Selection(
        selection_add=[("crossdocked", "Cross-Docked")], ondelete={"crossdocked": "set default"}
    )
    ownership_class = fields.Selection(
        SLOT_CLASSES,
        string="Ownership Class",
        required=True,
        default="owned",
        help="F03: the class the demand takes. A transfer or RTV moves owned stock; a job "
        "issue may draw another class (a warranty job draws warranty stock).",
    )
    technician_id = fields.Many2one(
        "hr.employee",
        string="Technician (job demand)",
        ondelete="restrict",
        help="The technician the M15 job issue is made to.",
    )
    consumption_id = fields.Many2one(
        "fix.stock.consumption", string="M15 Job Issue", readonly=True, copy=False, index=True
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"consumption_id"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.id and self.state != "queued":
            locked |= {"ownership_class", "technician_id"}
        return locked

    @api.constrains("source_type", "rtv_id", "technician_id", "ownership_class")
    def _check_document_source(self):
        for rec in self:
            if rec.source_type == "rtv" and not rec.rtv_id:
                raise ValidationError(
                    "Return-to-vendor demand comes from an approved M15 RTV; it is never typed "
                    "(BRU-WMS-01)."
                )
            if rec.source_type == "job" and not rec.technician_id:
                raise ValidationError(
                    "Job demand names the technician the part is issued to: it leaves as an "
                    "M15 job issue (BRU-WMS-01)."
                )
            if rec.source_type != "job" and (rec.ownership_class or "owned") != "owned":
                raise ValidationError(
                    "A transfer or a return to vendor moves owned stock; only a job issue "
                    "draws another class."
                )

    def _fix_document(self):
        """The M15 document that ships this demand's stock, if it has one."""
        self.ensure_one()
        rec = self.sudo()
        return rec.transfer_line_id.transfer_id or rec.rtv_id or rec.consumption_id

    def _fix_prepare_documents(self):
        """O1: give every demand its M15 document before it is waved. Returns
        the demand whose document is not ready yet (it stays queued, the reason
        in its note)."""
        waiting = self.browse()
        for rec in self:
            doc = rec.sudo()
            note = False
            if doc.rtv_id:
                if doc.rtv_id.state != "approved":
                    note = "RTV %s is %s" % (doc.rtv_id.name, doc.rtv_id.state)
            elif doc.transfer_line_id:
                transfer = doc.transfer_line_id.transfer_id
                if transfer.state != "approved":
                    note = "Transfer %s awaits its approval (%s)" % (transfer.name, transfer.state)
            elif doc.consumption_id:
                if doc.consumption_id.state != "draft":
                    note = "Job issue %s is %s" % (
                        doc.consumption_id.name,
                        doc.consumption_id.state,
                    )
            elif rec.source_type == "job":
                rec._fix_raise_issue()
            else:
                transfer = rec._fix_raise_transfer()
                if transfer.state != "approved":
                    note = "Transfer %s raised for it awaits its approval" % transfer.name
            if note:
                waiting |= rec
                rec._guarded().write({"short_note": note})
        return waiting

    def _fix_raise_transfer(self):
        """Manual, van, refurbishment or unlinked transfer demand: an M15
        transfer from the warehouse to the destination, raised (and submitted)
        in the builder's name, so he never approves it."""
        self.ensure_one()
        location = self.warehouse_id.sudo().stock_location_id
        transfer = (
            self.env["fix.stock.transfer"]
            .sudo()
            .create(
                {
                    "company_id": location.company_id.id or self.company_id.id,
                    "operating_unit_id": location.operating_unit_id.id
                    or self.warehouse_id.sudo().operating_unit_id.id
                    or False,
                    "from_location_id": location.id,
                    "to_location_id": self.dest_location_id.id,
                    "line_ids": [(0, 0, {"part_id": self.part_id.id, "qty": self.qty})],
                }
            )
        )
        # linked BEFORE the submit, so the approval queues no second demand
        self._guarded().write({"transfer_line_id": transfer.line_ids[:1].id})
        transfer.action_submit()
        return transfer

    def _fix_raise_issue(self):
        """Job demand: a draft M15 job issue (job + store + part), consumed when
        the stock ships. The job reference must name a real job now."""
        self.ensure_one()
        location = self.warehouse_id.sudo().stock_location_id
        issue = (
            self.env["fix.stock.consumption"]
            .sudo()
            .create(
                {
                    "company_id": location.company_id.id or self.company_id.id,
                    "operating_unit_id": location.operating_unit_id.id or False,
                    "service_order_ref": self.source_ref,
                    "product_id": self.part_id.id,
                    "location_id": location.id,
                    "technician_id": self.technician_id.id,
                    "quantity": self.qty,
                    "issue_class": self.ownership_class or "owned",
                    "scanned_code": self.part_id.part_number,
                }
            )
        )
        issue._resolve_job()
        self._guarded().write({"consumption_id": issue.id})
        return issue

    def _fix_ship_documents(self, lines=None):
        """The demand's stock is STAGED at the warehouse; its document ships it.
        A transfer dispatches once every one of its lines is shipped (F11)."""
        lines = lines if lines is not None else self.env["fix.wms.wave.line"]
        shipper = self.env.uid
        for rec in self.filtered(lambda d: d.sudo().consumption_id):
            rec._fix_consume_from_staged(lines.filtered(lambda ln, d=rec: ln.demand_id == d))
        for transfer in self.sudo().mapped("transfer_id"):
            demands = transfer.wms_demand_ids
            shipped = all(
                any(d.state == "shipped" for d in demands if d.transfer_line_id == line)
                for line in transfer.line_ids
            )
            if shipped:
                transfer.with_context(fix_wms_ship=True, fix_wms_shipper=shipper).action_dispatch()
        for rtv in self.sudo().mapped("rtv_id"):
            rtv.with_context(fix_wms_ship=True).action_ship()

    def _fix_consume_from_staged(self, lines):
        self.ensure_one()
        issue = self.sudo().consumption_id
        if issue.state != "draft":
            raise UserError(
                "Job issue %s is %s: it cannot be consumed." % (issue.name, issue.state)
            )
        location = self.warehouse_id.sudo().stock_location_id
        cls = location_class(location, self.ownership_class or "owned")
        self.env["fix.stock.onhand"]._fix_move_status(
            self.part_id, location, cls, self.qty, "staged", "unrestricted"
        )
        lot = lines.mapped("lot_id")[:1]
        if lot:
            lot._fix_move("in_stock")
            issue.write({"serial_number": lot.name})
        issue.action_scan_and_consume()

    def action_cancel(self):
        """F11: one line of a document is never dropped on its own: the
        document (transfer or RTV) is cancelled, which cancels its demand. A job
        demand's draft issue is cancelled with it."""
        for rec in self:
            doc = rec.sudo()
            if doc.transfer_line_id or doc.rtv_id:
                raise UserError(
                    "%s is a line of %s: cancel (or dispatch) that document instead; one line "
                    "of it is never dropped on its own." % (rec.name, rec._fix_document().name)
                )
        issues = self.sudo().mapped("consumption_id").filtered(lambda c: c.state == "draft")
        res = super().action_cancel()
        issues._guarded().write({"state": "cancelled"})
        return res


# ===================================================================== opening load
class FixWmsSlotLoad(models.Model):
    """O2 / F07 / spec section 16.4: the bin-level opening positions. Stock M15
    already holds at a WMS location (the legacy take-on, or stock that arrived
    before the layout) is put into bins by a Warehouse Supervisor, with a
    reason. It has NO ledger effect: it only says which bin holds stock M15
    holds outside the bins, never more than that (BRU-WMS-01)."""

    _name = "fix.wms.slot.load"
    _description = "Opening Slot Load"
    _order = "create_date desc, id desc"
    _inherit = ["fix.guarded.mixin"]

    name = fields.Char(required=True, default="New", copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    warehouse_id = fields.Many2one("fix.warehouse", required=True, ondelete="restrict")
    bin_id = fields.Many2one("fix.warehouse.bin", string="Bin", required=True, ondelete="restrict")
    part_id = fields.Many2one(
        "fix.spare.part", string="Spare Part", required=True, ondelete="restrict"
    )
    qty = fields.Float(string="Quantity Found in the Bin", required=True)
    reason = fields.Char(string="Reason / Count Reference", required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("loaded", "Slotted"), ("cancelled", "Cancelled")],
        required=True,
        default="draft",
    )
    loaded_by_id = fields.Many2one("res.users", string="Slotted By", readonly=True, copy=False)
    loaded_at = fields.Datetime(string="Slotted On", readonly=True, copy=False)

    _qty_positive = models.Constraint(
        "CHECK (qty > 0)", "An opening load slots a positive quantity"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "loaded_by_id", "loaded_at"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.id and self.state != "draft":
            locked |= {"warehouse_id", "bin_id", "part_id", "qty", "reason"}
        return locked

    @api.constrains("bin_id", "warehouse_id")
    def _check_bin(self):
        for rec in self:
            if rec.bin_id.zone_id.warehouse_id != rec.warehouse_id:
                raise ValidationError(
                    "Bin %s is not in %s." % (rec.bin_id.name, rec.warehouse_id.name)
                )

    @api.model_create_multi
    def create(self, vals_list):
        require_supervisor(self.env, "load opening bin positions")
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = _seq(self.env, "fix.wms.slot.load", "SLOAD/New")
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            require_supervisor(self.env, "change an opening slot load")
            if self.filtered(lambda r: r.state != "draft"):
                raise UserError("A slotted or cancelled opening load is final.")
        return super().write(vals)

    def action_load(self):
        """Slot the quantity into the bin. No M15 movement: the cap is what the
        ledger holds of the bin's class outside every bin of the location."""
        require_supervisor(self.env, "load opening bin positions")
        Slot = self.env["fix.wms.slot"]
        for rec in self:
            if rec.state != "draft":
                raise UserError("Opening load %s is already %s." % (rec.name, rec.state))
            if not (rec.reason or "").strip():
                raise UserError("Record why (the count) the bin holds this stock.")
            if not rec.warehouse_id.wms_enabled:
                raise UserError(
                    "Warehouse %s does not run warehouse execution." % rec.warehouse_id.name
                )
            check_quantity(rec.part_id, rec.qty, "opening quantity")
            location = _bin_location(rec.bin_id)
            zone = rec.bin_id.zone_id
            if zone.zone_type in NO_PUTAWAY_ZONE_TYPES:
                raise UserError(
                    "Bin %s is in the %s zone: unrestricted stock is not slotted there."
                    % (rec.bin_id.name, zone.zone_type)
                )
            if (rec.part_id.storage_class or "general") == "hazardous" and (
                rec.bin_id.storage_class != "hazardous"
            ):
                raise UserError(
                    "%s is hazardous: it goes only into a hazardous-class bin (BRU-WMS-11)."
                    % rec.part_id.part_number
                )
            if rec.part_id.is_serialized:
                raise UserError(
                    "%s is serialized: slot its serials by put-away (BRU-WMS-10)."
                    % rec.part_id.part_number
                )
            check_slot_cap(
                self.env,
                rec.part_id,
                location,
                bin_class(rec.bin_id),
                rec.qty,
                "Opening load %s" % rec.name,
            )
            slot = Slot._slot_for(rec.part_id, rec.bin_id, create=True)
            slot._check_pickable()
            slot._guarded().write(
                {
                    "qty": round((slot.qty or 0.0) + rec.qty, 4),
                    "last_slotted_on": fields.Date.context_today(self),
                }
            )
            rec._guarded().write(
                {
                    "state": "loaded",
                    "loaded_by_id": self.env.user.id,
                    "loaded_at": fields.Datetime.now(),
                }
            )
        return True

    def action_cancel(self):
        require_supervisor(self.env, "cancel an opening slot load")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Opening load %s is already %s." % (rec.name, rec.state))
            rec._guarded().write({"state": "cancelled"})
        return True


# ===================================================================== M15 hooks
class FixStockOnhandSlotClass(models.Model):
    _inherit = "fix.stock.onhand"

    @api.model
    def _fix_check_bins(self, part, location, qty, ownership=None):
        """M15's bin rule, per ownership class when the caller names it (F03):
        a class's movement takes only that class's stock outside the bins."""
        res = super()._fix_check_bins(part, location, qty)
        if ownership:
            slot_cls = "owned" if ownership == "van" else ownership
            if slotted_qty(self.env, part, location, slot_cls) > EPS:
                free = unslotted_qty(self.env, part, location, slot_cls)
                if qty > free + EPS:
                    raise UserError(
                        "%s %s of %s at %s is in warehouse bins; only %s is outside them "
                        "(BRU-WMS-01)."
                        % (
                            slotted_qty(self.env, part, location, slot_cls),
                            slot_cls,
                            part.part_number,
                            location.code,
                            max(free, 0.0),
                        )
                    )
        return res


class FixStockCountWmsSlots(models.Model):
    """F09: the M41 side of an ordinary M15 count at a location a warehouse
    breaks down into bins (M15's own model stays M15's: this wraps its apply).
    A count LOSS comes only out of the stock no bin holds; the bins are counted
    by floor counts, whose lines carry their floor count and are exempt."""

    _inherit = "fix.stock.count"

    def _post_count(self):
        Onhand = self.env["fix.stock.onhand"]
        for rec in self:
            for line in rec.line_ids.filtered(lambda ln: not ln.floor_count_id):
                delta = round(line._line_delta(), 4)
                if delta < -EPS:
                    Onhand._fix_check_bins(
                        line.part_id,
                        rec.location_id,
                        -delta,
                        ownership=line.ownership_class or location_class(rec.location_id),
                    )
        return super()._post_count()


# ===================================================================== structure (F06)
class FixWarehouseZoneLedger(models.Model):
    _inherit = "fix.warehouse.zone"

    _LEDGER_TIES = ("warehouse_id", "zone_type", "ownership_class")

    def write(self, vals):
        tied = [k for k in self._LEDGER_TIES if k in vals]
        if self and tied and not self.env.su:
            changing = self.filtered(lambda r: any(_value_differs(r, k, vals[k]) for k in tied))
            if changing and _holds_stock(self.env, [("bin_id.zone_id", "in", changing.ids)]):
                raise UserError(
                    "Zone %s holds stock in its bins: its warehouse, type and ownership class "
                    "are frozen until the bins are empty (BRU-WMS-01)." % changing[0].name
                )
        return super().write(vals)


class FixWarehouseBinLedger(models.Model):
    _inherit = "fix.warehouse.bin"

    _LEDGER_TIES = ("zone_id", "ownership_class", "storage_class")

    def write(self, vals):
        tied = [k for k in self._LEDGER_TIES if k in vals]
        if self and tied and not self.env.su:
            changing = self.filtered(lambda r: any(_value_differs(r, k, vals[k]) for k in tied))
            if changing and _holds_stock(self.env, [("bin_id", "in", changing.ids)]):
                raise UserError(
                    "Bin %s holds stock: its zone, ownership class and storage class are "
                    "frozen until it is empty (BRU-WMS-01)." % changing[0].name
                )
        return super().write(vals)


# ===================================================================== events (F26)
class FixWmsDockArrival(models.Model):
    _inherit = "fix.wms.dock"

    def action_check_in(self):
        res = super().action_check_in()
        for rec in self.filtered(lambda d: d.dock_type == "inbound"):
            publish(
                self.env,
                "wh.inbound_arrived",
                "fix.wms.dock",
                rec.id,
                {
                    "appointment": rec.name,
                    "dock": rec.dock_no,
                    "receipt": rec.receipt_id.name or None,
                },
            )
        return res
