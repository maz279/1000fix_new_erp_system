# fix_wms_ops_spec_flow — M41 capture pass 2, part 2 (2026-11-20): the spec
# items the owner chose to build after pass 2 (the file name sorts after
# fix_wms_ops_spec, whose models it extends).
#
#   1. Demand feed and hand-off (FR-WMS-018/027, AUT-WMS-07). An approved M15
#      transfer (or van replenishment) or return to vendor whose stock sits in a
#      warehouse that runs execution queues its lines as outbound demand. The
#      wave that picks it performs the document's OWN dispatch when it ships:
#      the transfer's stock moves staged -> in transit (the sender keeps it,
#      BRU-INV-16), the RTV posts its own ledger exit. The wave never ships that
#      stock a second time. A template whose rule is "at the cut-off" (or
#      "immediate") builds and releases its wave by itself; demand the bins
#      cannot cover stays queued with the reason, never half-waved.
#   2. Scan log (§10.1 fix.wh.task.event, §14 ownership-class segregation). Every
#      scan action records who scanned what, on which device, and whether it was
#      accepted. A REFUSED attempt is written in its own transaction, so it
#      survives the rollback of the refused action; the business rule that
#      refused it (BRU-WMS-03 class, -05 scan, -11 hazard, -12 blocked ...) is
#      kept, which is what the "attempted violations" report counts.
#   3. Substitute pick (FR-WMS-023). A short line may be filled with a part M37
#      lists as an approved alternate (fix.part.crossref), on a supervisor's
#      approval (never the requester's), and never for a transfer or RTV, which
#      move one named part.
#   4. Re-slot and consolidation proposals (FR-WMS-006/030, AUT-WMS-15). Nightly,
#      slot velocity is recomputed from 90 days of picks; fast movers outside a
#      pick face and parts split across bins get a PROPOSED move that a
#      supervisor accepts (it becomes an open move with its task) or rejects.
#   5. RF journal (T-06/T-07): the idempotency record behind /api/v1/wh/*.
import json
import logging
import re
from collections import defaultdict
from datetime import datetime, time, timedelta

from odoo import SUPERUSER_ID, api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

from .fix_inventory_approval import (
    check_location_usable,
    inv_param,
    is_whole_unit,
    location_class,
    require_supervisor,
)
from .fix_wms_ops import EPS
from .fix_wms_ops_floor import _warehouse_of
from .fix_wms_ops_spec import NO_PICK_ZONES, _seq

_logger = logging.getLogger(__name__)
DHAKA = timedelta(hours=6)  # Asia/Dhaka wall time = UTC + 6, no DST
RULE = re.compile(r"BRU-[A-Z]+-\d+|FR-WMS-\d+|T-\d+")
ACTIVE_DEMAND = ("queued", "waved")
PARAM_FAST = "cd_inventory.wms_fast_picks_90d"
PARAM_MEDIUM = "cd_inventory.wms_medium_picks_90d"
PURPOSE_SOURCES = {
    "branch_run": ("transfer", "manual"),
    "van": ("van",),
    "rtv": ("rtv",),
    "refurb": ("refurb",),
    "urgent": ("job",),
}


def _wms_warehouse(env, location):
    """The warehouse that runs execution over this M15 location, if any."""
    if not location:
        return env["fix.warehouse"]
    return (
        env["fix.warehouse"]
        .sudo()
        .search([("stock_location_id", "=", location.id), ("wms_enabled", "=", True)], limit=1)
    )


# ===================================================================== 1. feed
class FixWmsDemandFeed(models.Model):
    _inherit = "fix.wms.outbound.demand"

    state = fields.Selection(
        selection_add=[("shipped", "Shipped")], ondelete={"shipped": "set default"}
    )
    dest_location_id = fields.Many2one(required=False)
    transfer_line_id = fields.Many2one(
        "fix.stock.transfer.line", string="Transfer Line", readonly=True, copy=False, index=True
    )
    transfer_id = fields.Many2one(
        related="transfer_line_id.transfer_id", string="Transfer", store=True, index=True
    )
    rtv_id = fields.Many2one(
        "fix.stock.rtv", string="Return to Vendor", readonly=True, copy=False, index=True
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"transfer_line_id", "rtv_id"}

    @api.constrains("source_type", "dest_location_id")
    def _check_destination(self):
        for rec in self:
            if rec.source_type != "rtv" and not rec.dest_location_id:
                raise ValidationError("Demand names where it goes (a return to vendor excepted).")

    def _fix_template_for(self):
        """The warehouse's template for this demand: by purpose, then by the
        destinations it serves (FR-WMS-019). Only templates of the warehouse
        itself are applied automatically."""
        self.ensure_one()
        templates = (
            self.env["fix.wms.wave.template"]
            .sudo()
            .search([("active", "=", True), ("warehouse_id", "=", self.warehouse_id.id)])
        )
        for tpl in templates.sorted(lambda t: (t.purpose != "urgent", t.id)):
            sources = PURPOSE_SOURCES.get(tpl.purpose, ())
            urgent = tpl.purpose == "urgent" and self.priority in ("urgent", "emergency")
            if self.source_type not in sources and not urgent:
                continue
            if tpl.dest_location_ids and self.dest_location_id not in tpl.dest_location_ids:
                continue
            return tpl
        return templates.browse()

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records.filtered(lambda r: not r.template_id):
            tpl = rec._fix_template_for()
            if tpl:
                rec.sudo().write({"template_id": tpl.id})
        immediate = records.filtered(lambda r: r.template_id.release_rule == "immediate")
        for tpl in immediate.mapped("template_id"):
            tpl._fix_release_queue(quiet=True)
        return records


class FixWmsTemplateAutoRelease(models.Model):
    _inherit = "fix.wms.wave.template"

    last_released_at = fields.Datetime(string="Last Auto-Release", readonly=True, copy=False)

    def _fix_cutoff_utc(self, day):
        self.ensure_one()
        hhmm = datetime.strptime((self.cutoff or "").strip(), "%H:%M").time()
        return datetime.combine(day, time(hhmm.hour, hhmm.minute)) - DHAKA

    def _fix_release_queue(self, quiet=False):
        """Build and release this template's queued demand (AUT-WMS-07). Demand
        the bins cannot cover stays queued with the reason. Run as the system:
        the supervisor who set the rule decided the release."""
        released = self.env["fix.wms.wave"]
        for tpl in self.sudo():
            demand = tpl.env["fix.wms.outbound.demand"].search(
                [("state", "=", "queued"), ("template_id", "=", tpl.id)]
            )
            try:
                with tpl.env.cr.savepoint():
                    if demand:
                        waves = tpl.env["fix.wms.wave"].browse(
                            demand.action_build_wave(skip_short=True)
                        )
                        waves.action_release()
                        released |= waves
                    tpl.write({"last_released_at": fields.Datetime.now()})
            except (UserError, ValidationError) as exc:
                if not quiet:
                    raise
                _logger.warning("M41 auto-release of %s left queued: %s", tpl.name, exc)
        return released

    @api.model
    def _cron_auto_release(self):
        now = fields.Datetime.now()
        today = (now + DHAKA).date()
        templates = self.sudo().search(
            [
                ("active", "=", True),
                ("release_rule", "in", ("cutoff", "immediate")),
                ("warehouse_id.wms_enabled", "=", True),
            ]
        )
        for tpl in templates:
            if tpl.release_rule == "cutoff":
                try:
                    due = tpl._fix_cutoff_utc(today)
                except ValueError:
                    continue
                if now < due or (tpl.last_released_at and tpl.last_released_at >= due):
                    continue
            tpl._fix_release_queue(quiet=True)


class FixStockTransferWms(models.Model):
    """An approved transfer out of a warehouse that runs execution is picked by
    a wave; its wave's shipment dispatches it (FR-WMS-018/027)."""

    _inherit = "fix.stock.transfer"

    wms_demand_ids = fields.One2many(
        "fix.wms.outbound.demand", "transfer_id", string="Warehouse Demand"
    )

    def _fix_active_demand(self):
        return self.sudo().wms_demand_ids.filtered(lambda d: d.state in ACTIVE_DEMAND)

    def _fix_queue_wms_demand(self):
        Demand = self.env["fix.wms.outbound.demand"].sudo()
        for rec in self.filtered(lambda r: r.state == "approved"):
            warehouse = _wms_warehouse(self.env, rec.from_location_id)
            if not warehouse or rec.sudo().wms_demand_ids.filtered(
                lambda d: d.state != "cancelled"
            ):
                continue
            source = "van" if rec.to_location_id.location_type == "van" else "transfer"
            Demand._guarded().create(
                [
                    {
                        "company_id": rec.company_id.id,
                        "warehouse_id": warehouse.id,
                        "source_type": source,
                        "source_ref": rec.name,
                        "part_id": line.part_id.id,
                        "qty": line.qty,
                        "dest_location_id": rec.to_location_id.id,
                        "transfer_line_id": line.id,
                    }
                    for line in rec.line_ids
                ]
            )

    def action_submit(self):
        res = super().action_submit()
        self._fix_queue_wms_demand()
        return res

    def action_approve(self):
        res = super().action_approve()
        self._fix_queue_wms_demand()
        return res

    def action_dispatch(self):
        if self.env.context.get("fix_wms_ship"):
            return self._fix_dispatch_from_wave()
        for rec in self:
            demand = rec._fix_active_demand()
            if demand.filtered(lambda d: d.state == "waved"):
                raise UserError(
                    "Transfer %s is being picked by wave %s: its shipment dispatches it "
                    "(FR-WMS-027)." % (rec.name, demand.mapped("wave_id")[:1].name)
                )
            # still only queued: a direct dispatch takes it off the warehouse queue
            # (stock in bins still refuses below, BRU-WMS-01)
            demand._guarded().write({"state": "cancelled"})
        return super().action_dispatch()

    def action_cancel(self):
        for rec in self:
            demand = rec._fix_active_demand()
            if demand.filtered(lambda d: d.state == "waved"):
                raise UserError(
                    "Transfer %s is in wave %s: cancel the wave first."
                    % (rec.name, demand.mapped("wave_id")[:1].name)
                )
            demand._guarded().write({"state": "cancelled"})
        return super().action_cancel()

    def _fix_dispatch_from_wave(self):
        """The wave picked every line to STAGED; dispatch moves it to the
        sender's IN-TRANSIT bucket at its cost (BRU-INV-16), as M15's own
        dispatch does from unrestricted."""
        Onhand = self.env["fix.stock.onhand"]
        for rec in self:
            if rec.state != "approved":
                raise UserError("Transfer %s is %s, not approved." % (rec.name, rec.state))
            check_location_usable(rec.from_location_id)
            cls = location_class(rec.from_location_id)
            for line in rec.line_ids:
                cost = Onhand._fix_move_status(
                    line.part_id, rec.from_location_id, cls, line.qty, "staged", "in_transit"
                )
                line.sudo()._guarded().write(
                    {"unit_cost": cost, "is_dispatched": True, "received_qty": line.qty}
                )
                if line.lot_id:
                    line.lot_id._fix_move("in_transit")
            rec._guarded().write(
                {
                    "state": "dispatched",
                    "dispatched_on": fields.Date.context_today(self),
                    "dispatched_by_id": self.env.context.get("fix_wms_shipper") or self.env.uid,
                }
            )
        return True


class FixStockRtvWms(models.Model):
    _inherit = "fix.stock.rtv"

    wms_demand_ids = fields.One2many("fix.wms.outbound.demand", "rtv_id", string="Warehouse Demand")

    def _fix_active_demand(self):
        return self.sudo().wms_demand_ids.filtered(lambda d: d.state in ACTIVE_DEMAND)

    def _source_status(self):
        if self.env.context.get("fix_wms_ship"):
            return "staged"
        return super()._source_status()

    def _fix_queue_wms_demand(self):
        Demand = self.env["fix.wms.outbound.demand"].sudo()
        for rec in self.filtered(lambda r: r.state == "approved" and not r.quarantine_id):
            if rec._source_status() != "unrestricted":
                continue
            warehouse = _wms_warehouse(self.env, rec.location_id)
            if not warehouse or rec.sudo().wms_demand_ids.filtered(
                lambda d: d.state != "cancelled"
            ):
                continue
            Demand._guarded().create(
                {
                    "company_id": rec.company_id.id,
                    "warehouse_id": warehouse.id,
                    "source_type": "rtv",
                    "source_ref": rec.name,
                    "part_id": rec.part_id.id,
                    "qty": rec.qty,
                    "rtv_id": rec.id,
                }
            )

    def action_approve(self, note=None):
        res = super().action_approve(note)
        self._fix_queue_wms_demand()
        return res

    def action_ship(self):
        if not self.env.context.get("fix_wms_ship"):
            for rec in self:
                demand = rec._fix_active_demand()
                if demand.filtered(lambda d: d.state == "waved"):
                    raise UserError(
                        "RTV %s is being picked by wave %s: its shipment ships it."
                        % (rec.name, demand.mapped("wave_id")[:1].name)
                    )
                demand._guarded().write({"state": "cancelled"})
        return super().action_ship()

    def action_cancel(self):
        for rec in self:
            demand = rec._fix_active_demand()
            if demand.filtered(lambda d: d.state == "waved"):
                raise UserError("RTV %s is in a wave: cancel the wave first." % rec.name)
            demand._guarded().write({"state": "cancelled"})
        return super().action_cancel()


class FixWmsWaveHandoff(models.Model):
    _inherit = "fix.wms.wave"

    def action_ship(self):
        for rec in self:
            ready = rec.state == "staged" and rec.stage_ids.filtered(
                lambda s: s.state == "loaded" and (s.load_ref or "").strip() and s.manifest_verified
            )
            if ready:
                rec._fix_handoff()
        return super().action_ship()

    def _fix_handoff(self):
        """Lines picked for a transfer or an RTV are shipped by that document."""
        self.ensure_one()
        picked = self.line_ids.filtered(
            lambda ln: ln.state == "picked"
            and ln.demand_id
            and (ln.demand_id.transfer_line_id or ln.demand_id.rtv_id)
        )
        demands = picked.mapped("demand_id")
        for demand in demands:
            lines = picked.filtered(lambda ln, d=demand: ln.demand_id == d)
            got = round(sum(lines.mapped("picked_qty")), 4)
            if abs(got - demand.qty) > EPS:
                raise UserError(
                    "%s asks for %s of %s; wave %s picked %s. A transfer or RTV ships whole: "
                    "re-source or cancel the shortfall first."
                    % (demand.source_ref, demand.qty, demand.part_id.part_number, self.name, got)
                )
            named = demand.transfer_line_id.lot_id or demand.rtv_id.lot_id
            if named and lines.mapped("lot_id") != named:
                raise UserError(
                    "%s names serial %s; the pick scanned %s."
                    % (
                        demand.source_ref,
                        named.name,
                        ", ".join(lines.mapped("lot_id.name")) or "none",
                    )
                )
        if not demands:
            return
        picked._guarded().write({"state": "handed"})
        demands._guarded().write({"state": "shipped"})
        shipper = self.env.uid
        for transfer in demands.mapped("transfer_id"):
            open_lines = transfer.sudo().wms_demand_ids.filtered(lambda d: d.state != "cancelled")
            if all(d.state == "shipped" for d in open_lines):
                transfer.sudo().with_context(
                    fix_wms_ship=True, fix_wms_shipper=shipper
                ).action_dispatch()
        for rtv in demands.mapped("rtv_id"):
            rtv.sudo().with_context(fix_wms_ship=True).action_ship()
        publish(
            self.env,
            "wh.dispatched",
            "fix.wms.wave",
            self.id,
            {
                "wave": self.name,
                "transfers": demands.mapped("transfer_id.name"),
                "rtvs": demands.mapped("rtv_id.name"),
            },
        )

    def action_cancel(self, reason=None):
        demands = self.mapped("demand_ids").filtered(lambda d: d.state == "waved")
        res = super().action_cancel(reason)
        demands._guarded().write({"state": "queued", "wave_id": False})
        return res


class FixWmsWaveLineFlow(models.Model):
    _inherit = "fix.wms.wave.line"

    state = fields.Selection(
        selection_add=[("handed", "Shipped by its Document")],
        ondelete={"handed": "set default"},
    )
    substitute_of_id = fields.Many2one(
        "fix.wms.wave.line", string="Substitute For", readonly=True, copy=False
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"substitute_of_id"}


# ===================================================================== 2. scans
class FixWmsScanEvent(models.Model):
    """A scan-level execution record (§10.1 fix.wh.task.event). It holds no
    foreign key but its company: a refused attempt is written in a separate
    transaction, where the operative, record or device of the refused one may
    not exist yet."""

    _name = "fix.wms.scan.event"
    _description = "Warehouse Scan Event"
    _order = "occurred_at desc, id desc"

    company_id = fields.Many2one("res.company", index=True)
    occurred_at = fields.Datetime(required=True, default=fields.Datetime.now, index=True)
    user_ref = fields.Integer(string="User ID", index=True)
    user_name = fields.Char(string="Operative")
    device_code = fields.Char(string="Device")
    res_model = fields.Char(string="Record Type")
    res_id = fields.Integer(string="Record ID")
    record_name = fields.Char(string="Record")
    action = fields.Char(string="Action")
    scans = fields.Char(string="Scanned")
    accepted = fields.Boolean(index=True)
    rule = fields.Char(string="Rule", index=True)
    message = fields.Char(string="Why Refused")
    offline = fields.Boolean(string="Replayed Offline")
    idempotency_key = fields.Char(string="Idempotency Key")

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            raise AccessError("The scan log is written by the scan actions only.")
        return super().create(vals_list)

    def write(self, vals):
        raise AccessError("The scan log is append-only.")

    def unlink(self):
        raise AccessError("The scan log is append-only.")


def _scan_vals(records, action, scans, accepted, exc=None):
    env = records.env
    ctx = env.context
    message = ""
    if exc is not None:
        message = str(getattr(exc, "args", [exc])[0] if getattr(exc, "args", None) else exc)
    match = RULE.search(message)
    rule = match.group(0) if match else ""
    if not rule and message.startswith(("Scanned bin", "Scanned item")):
        rule = "BRU-WMS-05"  # every put-away and pick is confirmed by bin and item scan
    if not rule and not accepted:
        rule = "refused"
    rec = records[:1]
    return {
        "company_id": (rec.company_id.id if "company_id" in rec._fields else False)
        or env.company.id,
        "user_ref": env.uid,
        "user_name": env.user.name,
        "device_code": ctx.get("fix_scan_device") or False,
        "res_model": records._name,
        "res_id": rec.id or 0,
        "record_name": rec.display_name if rec else False,
        "action": action,
        "scans": " ".join(str(s) for s in scans if s not in (None, False, "")) or False,
        "accepted": accepted,
        "rule": rule or False,
        "message": message[:250] or False,
        "offline": bool(ctx.get("fix_scan_offline")),
        "idempotency_key": ctx.get("fix_scan_key") or False,
    }


def _scan_logged(records, action, scans, call):
    """Run a scan action and log it; a refusal is logged in its own transaction
    (it must survive the rollback of the action it refused)."""
    env = records.env
    if env.su or env.context.get("fix_scan_logging"):
        return call(records)
    try:
        result = call(records.with_context(fix_scan_logging=True))
    except (UserError, ValidationError, AccessError) as exc:
        vals = _scan_vals(records, action, scans, False, exc)
        try:
            with env.registry.cursor() as cr:
                api.Environment(cr, SUPERUSER_ID, {})["fix.wms.scan.event"].create(vals)
        except Exception:  # never let the log hide the refusal itself
            _logger.exception("M41 scan log: could not record a refused scan")
        raise
    env["fix.wms.scan.event"].sudo().create(_scan_vals(records, action, scans, True))
    return result


class FixWmsPutawayScan(models.Model):
    _inherit = "fix.wms.putaway"

    def action_complete(self, bin_code=None, item_code=None):
        if len(self) != 1:
            return all(rec.action_complete(bin_code, item_code) for rec in self) or True
        return _scan_logged(
            self,
            "put-away",
            [bin_code, item_code],
            lambda r: super(FixWmsPutawayScan, r).action_complete(bin_code, item_code),
        )


class FixWmsWaveLineScanLog(models.Model):
    _inherit = "fix.wms.wave.line"

    def action_scan_pick(self, bin_code=None, item_code=None, serial=None):
        if len(self) != 1:
            return all(rec.action_scan_pick(bin_code, item_code, serial) for rec in self) or True
        return _scan_logged(
            self,
            "pick",
            [bin_code, item_code, serial],
            lambda r: super(FixWmsWaveLineScanLog, r).action_scan_pick(bin_code, item_code, serial),
        )

    def action_scan_short_pick(self, bin_code=None, item_code=None, found_qty=None, serial=None):
        if len(self) != 1:
            return (
                all(
                    rec.action_scan_short_pick(bin_code, item_code, found_qty, serial)
                    for rec in self
                )
                or True
            )
        return _scan_logged(
            self,
            "short pick",
            [bin_code, item_code, "found=%s" % found_qty, serial],
            lambda r: super(FixWmsWaveLineScanLog, r).action_scan_short_pick(
                bin_code, item_code, found_qty, serial
            ),
        )


class FixWmsMoveScanLog(models.Model):
    _inherit = "fix.wms.move"

    def action_confirm(self, from_code=None, to_code=None, item_code=None):
        if len(self) != 1:
            return all(rec.action_confirm(from_code, to_code, item_code) for rec in self) or True
        return _scan_logged(
            self,
            "move",
            [from_code, to_code, item_code],
            lambda r: super(FixWmsMoveScanLog, r).action_confirm(from_code, to_code, item_code),
        )


class FixWmsTaskScanLog(models.Model):
    _inherit = "fix.wms.task"

    def action_done(self, scan=None, bin_scan=None, item_scan=None):
        if len(self) != 1:
            return all(rec.action_done(scan, bin_scan, item_scan) for rec in self) or True
        return _scan_logged(
            self,
            "task %s" % (self.task_type or ""),
            [scan, bin_scan, item_scan],
            lambda r: super(FixWmsTaskScanLog, r).action_done(scan, bin_scan, item_scan),
        )


class FixWmsCrossdockScanLog(models.Model):
    _inherit = "fix.wms.crossdock"

    def action_confirm(self, item_code=None):
        if len(self) != 1:
            return all(rec.action_confirm(item_code) for rec in self) or True
        return _scan_logged(
            self,
            "cross-dock",
            [item_code],
            lambda r: super(FixWmsCrossdockScanLog, r).action_confirm(item_code),
        )


class FixWmsHandlingUnitScanLog(models.Model):
    _inherit = "fix.wms.handling.unit"

    def action_store(self, bin_code=None):
        if len(self) != 1:
            return all(rec.action_store(bin_code) for rec in self) or True
        return _scan_logged(
            self,
            "store handling unit",
            [bin_code],
            lambda r: super(FixWmsHandlingUnitScanLog, r).action_store(bin_code),
        )


# ===================================================================== 3. substitution
def _catalogue_item(env, part):
    product = part.sudo().product_id
    if not product:
        return env["fix.catalogue.item"]
    return (
        env["fix.catalogue.item"]
        .sudo()
        .search([("product_tmpl_id", "=", product.product_tmpl_id.id)], limit=1)
    )


def _approved_alternate(env, part, substitute):
    """The M37 cross-reference that lets `substitute` replace `part`: one way
    from the part, or two way in either order (FR-CAT-030)."""
    a, b = _catalogue_item(env, part), _catalogue_item(env, substitute)
    if not a or not b:
        return env["fix.part.crossref"]
    Xref = env["fix.part.crossref"].sudo()
    forward = Xref.search(
        [("active", "=", True), ("part_item_id", "=", a.id), ("alt_item_id", "=", b.id)], limit=1
    )
    if forward:
        return forward
    return Xref.search(
        [
            ("active", "=", True),
            ("part_item_id", "=", b.id),
            ("alt_item_id", "=", a.id),
            ("direction", "=", "two_way"),
        ],
        limit=1,
    )


class FixWmsSubstitution(models.Model):
    """FR-WMS-023: a short pick line filled with an approved alternate part."""

    _name = "fix.wms.substitution"
    _description = "Pick Substitution"
    _order = "create_date desc, id desc"
    _inherit = ["fix.guarded.mixin"]

    name = fields.Char(required=True, default="New", copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    wave_line_id = fields.Many2one(
        "fix.wms.wave.line", string="Short Pick Line", required=True, ondelete="restrict"
    )
    wave_id = fields.Many2one(related="wave_line_id.wave_id", string="Wave", store=True)
    part_id = fields.Many2one(related="wave_line_id.part_id", string="Part Asked For", store=True)
    substitute_part_id = fields.Many2one(
        "fix.spare.part", string="Substitute Part", required=True, ondelete="restrict"
    )
    bin_id = fields.Many2one(
        "fix.warehouse.bin", string="Pick the Substitute From", required=True, ondelete="restrict"
    )
    qty = fields.Float(string="Quantity", readonly=True)
    crossref_id = fields.Many2one(
        "fix.part.crossref", string="M37 Approval", readonly=True, copy=False
    )
    reason = fields.Char(string="Why")
    state = fields.Selection(
        [("requested", "Requested"), ("approved", "Approved"), ("rejected", "Rejected")],
        required=True,
        default="requested",
    )
    requested_by_id = fields.Many2one(
        "res.users", string="Requested By", readonly=True, default=lambda self: self.env.user
    )
    decided_by_id = fields.Many2one("res.users", string="Decided By", readonly=True, copy=False)
    new_line_id = fields.Many2one(
        "fix.wms.wave.line", string="Substitute Pick Line", readonly=True, copy=False
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "qty",
            "crossref_id",
            "state",
            "requested_by_id",
            "decided_by_id",
            "new_line_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.id:
            locked |= {"wave_line_id", "substitute_part_id", "bin_id", "reason"}
        return locked

    def _fix_check(self):
        Slot = self.env["fix.wms.slot"].sudo()
        for rec in self:
            line = rec.wave_line_id
            if line.state != "short" or line.wave_id.state != "picking":
                raise UserError("Substitute only for a short line of a wave being picked.")
            demand = line.demand_id
            if demand.transfer_line_id or demand.rtv_id:
                raise UserError(
                    "%s moves one named part (%s): it is not substituted."
                    % (demand.source_ref, line.part_id.part_number)
                )
            sub = rec.substitute_part_id
            if sub == line.part_id:
                raise UserError("A substitute is another part.")
            xref = _approved_alternate(rec.env, line.part_id, sub)
            if not xref:
                raise UserError(
                    "M37 lists %s as no approved alternate of %s (FR-CAT-030)."
                    % (sub.part_number, line.part_id.part_number)
                )
            if xref.device_model_ids:
                raise UserError(
                    "That alternate is valid only on certain device models: substitute it at "
                    "the job, not in a wave."
                )
            if _warehouse_of(rec.bin_id) != line.wave_id.warehouse_id:
                raise UserError("Bin %s is in another warehouse." % rec.bin_id.name)
            slot = Slot._slot_for(sub, rec.bin_id)
            free = round((slot.qty or 0.0) - (slot.reserved_qty or 0.0), 4) if slot else 0.0
            if not slot or free + EPS < rec.qty:
                raise UserError(
                    "Bin %s holds %s of %s free; the shortfall is %s."
                    % (rec.bin_id.name, free, sub.part_number, rec.qty)
                )
            slot._check_pickable()
            rec._guarded().write({"crossref_id": xref.id})

    @api.model_create_multi
    def create(self, vals_list):
        Line = self.env["fix.wms.wave.line"]
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = _seq(self.env, "fix.wms.substitution", "SUB/New")
            line = Line.browse(vals.get("wave_line_id") or 0)
            vals["qty"] = round((line.qty or 0.0) - (line.picked_qty or 0.0), 4)
        records = super(FixWmsSubstitution, self._guarded()).create(vals_list)
        records = records.with_env(self.env)
        records._fix_check()
        return records

    def action_approve(self):
        require_supervisor(self.env, "approve a substitute part")
        Onhand = self.env["fix.stock.onhand"]
        Task = self.env["fix.wms.task"].sudo()
        for rec in self:
            if rec.state != "requested":
                raise UserError("Substitution %s is %s." % (rec.name, rec.state))
            if rec.requested_by_id == self.env.user and not self.env.su:
                raise AccessError(
                    "You asked for substitution %s: another supervisor approves it." % rec.name
                )
            rec._fix_check()
            line, wave = rec.wave_line_id, rec.wave_line_id.wave_id
            _warehouse, location = wave._wave_location()
            cls = location_class(location)
            slot = self.env["fix.wms.slot"]._slot_for(rec.substitute_part_id, rec.bin_id)
            Onhand._fix_reserve(rec.substitute_part_id, location, cls, rec.qty, wave.name)
            slot._guarded().write({"reserved_qty": round((slot.reserved_qty or 0.0) + rec.qty, 4)})
            new = (
                self.env["fix.wms.wave.line"]
                ._guarded()
                .create(
                    {
                        "wave_id": wave.id,
                        "part_id": rec.substitute_part_id.id,
                        "bin_id": rec.bin_id.id,
                        "qty": rec.qty,
                        "reserved_qty": rec.qty,
                        "source_type": line.source_type,
                        "source_ref": line.source_ref,
                        "dest_location_id": line.dest_location_id.id or False,
                        "priority": line.priority,
                        "demand_id": line.demand_id.id or False,
                        "substitute_of_id": line.id,
                    }
                )
            )
            Task.create(
                {
                    "company_id": wave.company_id.id,
                    "task_type": "pick",
                    "ref": "%s (substitute)" % wave.name,
                    "wave_line_id": new.id,
                    "part_id": rec.substitute_part_id.id,
                    "bin_id": rec.bin_id.id,
                    "qty": rec.qty,
                }
            )
            if (line.picked_qty or 0.0) > EPS:
                line._guarded().write({"qty": line.picked_qty, "state": "picked"})
            else:
                line._guarded().write({"state": "cancelled"})
            rec._guarded().write(
                {"state": "approved", "decided_by_id": self.env.user.id, "new_line_id": new.id}
            )
            publish(
                self.env,
                "wh.substituted",
                "fix.wms.substitution",
                rec.id,
                {
                    "wave": wave.name,
                    "part_id": line.part_id.id,
                    "substitute_id": rec.substitute_part_id.id,
                    "qty": rec.qty,
                    "crossref_id": rec.crossref_id.id,
                },
            )
        return True

    def action_reject(self):
        require_supervisor(self.env, "reject a substitute part")
        for rec in self:
            if rec.state != "requested":
                raise UserError("Substitution %s is %s." % (rec.name, rec.state))
            rec._guarded().write({"state": "rejected", "decided_by_id": self.env.user.id})
        return True


# ===================================================================== 4. proposals
class FixWmsSlotProposal(models.Model):
    """FR-WMS-006/030: a re-slot or consolidation move the system proposes and
    a supervisor decides. Nothing moves until the accepted move is confirmed
    by scan on the floor."""

    _name = "fix.wms.slot.proposal"
    _description = "Re-Slot / Consolidation Proposal"
    _order = "create_date desc, id desc"
    _inherit = ["fix.guarded.mixin"]

    name = fields.Char(required=True, default="New", copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    warehouse_id = fields.Many2one("fix.warehouse", required=True, ondelete="cascade")
    kind = fields.Selection(
        [
            ("reslot", "Re-slot a fast mover to a pick face"),
            ("consolidate", "Consolidate a split part"),
        ],
        required=True,
    )
    part_id = fields.Many2one(
        "fix.spare.part", string="Spare Part", required=True, ondelete="cascade"
    )
    from_bin_id = fields.Many2one(
        "fix.warehouse.bin", string="From Bin", required=True, ondelete="cascade"
    )
    to_bin_id = fields.Many2one(
        "fix.warehouse.bin", string="To Bin", required=True, ondelete="cascade"
    )
    qty = fields.Float(string="Quantity", required=True)
    picks_90d = fields.Integer(string="Picks (90 days)")
    reason = fields.Char(string="Why")
    state = fields.Selection(
        [("proposed", "Proposed"), ("accepted", "Accepted"), ("rejected", "Rejected")],
        required=True,
        default="proposed",
    )
    decided_by_id = fields.Many2one("res.users", string="Decided By", readonly=True, copy=False)
    move_id = fields.Many2one("fix.wms.move", string="Move", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "decided_by_id", "move_id"}

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            raise AccessError("Proposals are made by the nightly slotting run.")
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = _seq(self.env, "fix.wms.slot.proposal", "PROP/New")
        return super().create(vals_list)

    def action_accept(self):
        require_supervisor(self.env, "accept a slotting proposal")
        Move = self.env["fix.wms.move"]
        for rec in self:
            if rec.state != "proposed":
                raise UserError("Proposal %s is %s." % (rec.name, rec.state))
            slot = self.env["fix.wms.slot"]._slot_for(rec.part_id, rec.from_bin_id)
            free = round((slot.qty or 0.0) - (slot.reserved_qty or 0.0), 4) if slot else 0.0
            qty = min(rec.qty, free)
            if is_whole_unit(rec.part_id):
                qty = float(int(qty + EPS))
            if qty <= EPS:
                raise UserError(
                    "Bin %s no longer holds free %s: reject the proposal."
                    % (rec.from_bin_id.name, rec.part_id.part_number)
                )
            move = Move.create(
                {
                    "company_id": rec.company_id.id,
                    "move_type": rec.kind,
                    "reason_code": rec.kind,
                    "part_id": rec.part_id.id,
                    "from_bin_id": rec.from_bin_id.id,
                    "to_bin_id": rec.to_bin_id.id,
                    "qty": qty,
                    "note": rec.name,
                }
            )
            rec._guarded().write(
                {"state": "accepted", "decided_by_id": self.env.user.id, "move_id": move.id}
            )
        return True

    def action_reject(self):
        require_supervisor(self.env, "reject a slotting proposal")
        for rec in self:
            if rec.state != "proposed":
                raise UserError("Proposal %s is %s." % (rec.name, rec.state))
            rec._guarded().write({"state": "rejected", "decided_by_id": self.env.user.id})
        return True

    @api.model
    def _cron_propose(self):
        for warehouse in self.env["fix.warehouse"].sudo().search([("wms_enabled", "=", True)]):
            warehouse._fix_propose_slotting()


class FixWarehouseSlotting(models.Model):
    _inherit = "fix.warehouse"

    def action_propose_slotting(self):
        """Run the nightly slotting proposals now (a supervisor)."""
        require_supervisor(self.env, "run the slotting proposals")
        made = 0
        for rec in self:
            if not rec.wms_enabled:
                raise UserError("Warehouse %s does not run warehouse execution." % rec.name)
            made += len(rec.sudo()._fix_propose_slotting())
        return {"warning": "%d proposal(s) made" % made} if not made else True

    def _fix_propose_slotting(self):
        """Velocity from 90 days of picks, then the proposals (AUT-WMS-15)."""
        self.ensure_one()
        env = self.env(su=True)
        Slot = env["fix.wms.slot"]
        Line = env["fix.wms.wave.line"]
        Proposal = env["fix.wms.slot.proposal"]
        Putaway = env["fix.wms.putaway"]
        since = fields.Datetime.now() - timedelta(days=90)
        fast = inv_param(env, PARAM_FAST, 20.0)
        medium = inv_param(env, PARAM_MEDIUM, 5.0)
        slots = Slot.search([("bin_id.zone_id.warehouse_id", "=", self.id), ("qty", ">", 0)])
        picks = {}
        for slot in slots:
            count = Line.search_count(
                [
                    ("part_id", "=", slot.part_id.id),
                    ("bin_id", "=", slot.bin_id.id),
                    ("picked_at", ">=", since),
                    ("state", "in", ("picked", "handed")),
                ]
            )
            picks[slot.id] = count
            band = "fast" if count >= fast else ("medium" if count >= medium else "slow")
            if slot.velocity != band:
                slot.write({"velocity": band})
        busy = Proposal.search([("warehouse_id", "=", self.id), ("state", "=", "proposed")])
        open_moves = env["fix.wms.move"].search(
            [("state", "=", "open"), ("from_bin_id.zone_id.warehouse_id", "=", self.id)]
        )
        taken = {(p.part_id.id, p.from_bin_id.id) for p in busy} | {
            (m.part_id.id, m.from_bin_id.id) for m in open_moves
        }
        made = Proposal.browse()

        def free_of(slot):
            qty = round((slot.qty or 0.0) - (slot.reserved_qty or 0.0), 4)
            return float(int(qty + EPS)) if is_whole_unit(slot.part_id) else qty

        bins = env["fix.warehouse.bin"].search(
            [("zone_id.warehouse_id", "=", self.id)], order="pick_sequence, id"
        )
        faces = bins.filtered(
            lambda b: b.is_pick_face
            and not b._fix_is_blocked()
            and b.zone_id.zone_type not in NO_PICK_ZONES
        )
        for slot in slots.filtered(lambda s: s.velocity == "fast" and not s.bin_id.is_pick_face):
            qty = free_of(slot)
            if qty <= EPS or (slot.part_id.id, slot.bin_id.id) in taken:
                continue
            cls = slot.bin_id.ownership_class or "any"
            for face in faces:
                if Slot.search_count([("bin_id", "=", face.id), ("qty", ">", 0)]):
                    continue
                if Putaway._fix_bin_refusal(face, slot.part_id, qty, cls, bins.browse()):
                    continue
                made |= Proposal.create(
                    {
                        "company_id": self.company_id.id,
                        "warehouse_id": self.id,
                        "kind": "reslot",
                        "part_id": slot.part_id.id,
                        "from_bin_id": slot.bin_id.id,
                        "to_bin_id": face.id,
                        "qty": qty,
                        "picks_90d": picks.get(slot.id, 0),
                        "reason": "%d picks in 90 days, outside a pick face"
                        % picks.get(slot.id, 0),
                    }
                )
                taken.add((slot.part_id.id, slot.bin_id.id))
                break
        by_part = defaultdict(lambda: Slot.browse())
        for slot in slots:
            by_part[slot.part_id.id] |= slot
        for group in by_part.values():
            if len(group) < 2:
                continue
            ordered = group.sorted(lambda s: (-(s.qty or 0.0), s.id))
            target = ordered[0]
            for slot in ordered[1:]:
                qty = free_of(slot)
                if qty <= EPS or (slot.part_id.id, slot.bin_id.id) in taken:
                    continue
                if (slot.bin_id.ownership_class or "any") != (
                    target.bin_id.ownership_class or "any"
                ):
                    continue
                cls = slot.bin_id.ownership_class or "any"
                if Putaway._fix_bin_refusal(target.bin_id, slot.part_id, qty, cls, bins.browse()):
                    continue
                made |= Proposal.create(
                    {
                        "company_id": self.company_id.id,
                        "warehouse_id": self.id,
                        "kind": "consolidate",
                        "part_id": slot.part_id.id,
                        "from_bin_id": slot.bin_id.id,
                        "to_bin_id": target.bin_id.id,
                        "qty": qty,
                        "picks_90d": picks.get(slot.id, 0),
                        "reason": "%s is split across %d bins"
                        % (slot.part_id.part_number, len(group)),
                    }
                )
                taken.add((slot.part_id.id, slot.bin_id.id))
        return made


# ===================================================================== 5. RF journal
class FixWmsRfJournal(models.Model):
    """T-06/T-07: one row per (device, idempotency key). Replaying a key returns
    the stored outcome; the action never runs twice."""

    _name = "fix.wms.rf.journal"
    _description = "RF Confirmation Journal"
    _order = "processed_at desc, id desc"

    device_id = fields.Many2one("fix.wms.device", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="device_id.company_id", store=True, index=True)
    key = fields.Char(string="Idempotency Key", required=True)
    task_id = fields.Many2one("fix.wms.task", ondelete="set null")
    op = fields.Char(string="Operation", required=True)
    payload = fields.Text()
    ok = fields.Boolean()
    result = fields.Text()
    offline = fields.Boolean(string="Offline Replay")
    user_id = fields.Many2one("res.users", string="Operative")
    processed_at = fields.Datetime(required=True, default=fields.Datetime.now)

    _key_unique = models.Constraint(
        "UNIQUE (device_id, key)", "An idempotency key is used once per device"
    )

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            raise AccessError("The RF journal is written by the RF API only.")
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.su:
            raise AccessError("The RF journal is append-only.")
        return super().write(vals)


class FixWmsDeviceRf(models.Model):
    """The RF API's logic (the controller only authenticates and routes)."""

    _inherit = "fix.wms.device"

    @api.model
    def _rf_resolve(self, device_code):
        """The device the caller holds, and the caller as its operative (T-15)."""
        code = (device_code or "").strip()
        device = self.sudo().search([("device_code", "=", code)], limit=1)
        if not device:
            raise AccessError("Unknown RF device %r." % code)
        if device.state != "active":
            raise AccessError("RF device %s is deactivated (T-15)." % device.device_code)
        employee = (
            self.env["hr.employee"]
            .sudo()
            .search(
                [("user_id", "=", self.env.uid), ("company_id", "in", self.env.companies.ids)],
                limit=1,
            )
        )
        if not employee:
            raise AccessError("You have no employee record: the RF app is an operative's.")
        if device.operative_id and device.operative_id != employee:
            raise AccessError(
                "RF device %s is issued to %s." % (device.device_code, device.operative_id.name)
            )
        device._guarded().write({"last_seen_at": fields.Datetime.now()})
        # every action below runs as the operative, under their rules
        return device.with_env(self.env), employee

    def _rf_task_payload(self, task):
        part, bin_record = task.part_id.sudo(), task.bin_id.sudo()
        return {
            "id": task.id,
            "name": task.name,
            "type": task.task_type,
            "state": task.state,
            "ref": task.ref or "",
            "part": part.part_number or "",
            "part_name": part.name or "",
            "part_name_bn": part.name_bn or "",
            "bin": bin_record.name or "",
            "bin_barcode": bin_record.barcode or "",
            "qty": task.qty,
            "equipment": task.equipment_required or "",
            "walk_order": task.pick_sequence,
            "standard_seconds": task.time_standard_sec,
        }

    def _rf_next(self, employee, limit=4):
        """The operative's current task and the next three (T-06): assigned to
        them first, then open tasks of their warehouse and zones."""
        self.ensure_one()
        Task = self.env["fix.wms.task"]
        mine = Task.search(
            [("state", "=", "assigned"), ("assignee_id", "=", employee.id)],
            order="pick_sequence, id",
            limit=limit,
        )
        rest = limit - len(mine)
        open_tasks = Task.browse()
        if rest > 0:
            profile = (
                self.env["fix.wms.operative"]
                .sudo()
                .search(
                    [("employee_id", "=", employee.id), ("warehouse_id", "=", self.warehouse_id.id)]
                )
            )
            domain = [
                ("state", "=", "open"),
                ("bin_id.zone_id.warehouse_id", "=", self.warehouse_id.id),
            ]
            if profile.zone_ids:
                domain.append(("bin_id.zone_id", "in", profile.zone_ids.ids))
            open_tasks = Task.search(domain, order="pick_sequence, id", limit=rest)
        return [self._rf_task_payload(t) for t in mine | open_tasks]

    def _rf_run(self, key, op, task_id, payload, offline=False):
        """Run one RF operation once per (device, key) (T-07)."""
        self.ensure_one()
        key = (key or "").strip()
        if not key:
            raise UserError("Every RF confirmation carries an idempotency key (T-07).")
        Journal = self.env["fix.wms.rf.journal"].sudo()
        seen = Journal.search([("device_id", "=", self.id), ("key", "=", key)], limit=1)
        if seen:
            return {"ok": seen.ok, "replayed": True, **json.loads(seen.result or "{}")}
        task = self.env["fix.wms.task"].browse(int(task_id or 0)).exists()
        ctx = {
            "fix_scan_device": self.device_code,
            "fix_scan_key": key,
            "fix_scan_offline": offline,
        }
        try:
            with self.env.cr.savepoint():
                if not task:
                    raise UserError("Task %s does not exist." % task_id)
                result = self._rf_apply(task.with_context(**ctx), op, payload or {})
            ok = True
        except (UserError, ValidationError, AccessError) as exc:
            ok, result = False, {"error": str(exc.args[0] if exc.args else exc)}
        Journal.create(
            {
                "device_id": self.id,
                "key": key,
                "task_id": task.id or False,
                "op": op,
                "payload": json.dumps(payload or {}, default=str),
                "ok": ok,
                "result": json.dumps(result, default=str),
                "offline": offline,
                "user_id": self.env.uid,
            }
        )
        return {"ok": ok, "replayed": False, **result}

    def _rf_apply(self, task, op, payload):
        if task.bin_id and _warehouse_of(task.bin_id.sudo()) != self.warehouse_id:
            raise AccessError("Task %s is another warehouse's (T-13)." % task.name)
        if op == "claim":
            task.action_claim()
        elif op == "confirm":
            scans = payload.get("scans") or []
            task.action_done(scan=" ".join(str(s) for s in scans))
        elif op == "exception":
            self._rf_exception(task, payload)
        else:
            raise UserError("Unknown RF operation %r." % op)
        return {"task": self._rf_task_payload(task)}

    def _rf_exception(self, task, payload):
        """Short pick, full or blocked bin, damaged item (FR-WMS-024/015/034)."""
        kind = payload.get("kind")
        if task.state != "assigned" or task.assignee_id.user_id != self.env.user:
            raise UserError("Report an exception on your own assigned task.")
        if kind == "short" and task.wave_line_id:
            task.wave_line_id.action_scan_short_pick(
                bin_code=payload.get("bin_code"),
                item_code=payload.get("item_code"),
                found_qty=payload.get("found_qty"),
                serial=payload.get("serial"),
            )
        elif kind in ("full_bin", "blocked_bin", "damaged_item") and task.putaway_id:
            task.putaway_id.action_report_exception(cause=kind, note=payload.get("note"))
        elif kind == "blocked_bin" and task.bin_id:
            task.bin_id.action_block(payload.get("note") or "Blocked, reported from the RF device")
        else:
            raise UserError("Exception %r does not apply to a %s task." % (kind, task.task_type))
