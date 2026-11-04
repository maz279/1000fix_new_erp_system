# m52_cost — A07 P1 (2026-11-04), report §6 P1: asset running costs reach M52.
#
# A verified facility work order, a clean fuel fill and a completed vehicle
# service each carry a cost that ended at the outbox: M52 (accounts payable &
# employee expense, cd_ap_ext) never saw it, so a vendor could bill a job
# twice, or a job no-one verified, and branch costs were invisible. Each now
# raises ONE pending cost entry per source, by company / branch, that the AP
# accountant matches to the vendor bill (fix.vendor.invoice) when it is
# entered, or rejects with a reason. The entry is not a bill and posts nothing:
# the bill keeps its own three-way match and approval matrix.
from odoo import api, fields, models
from odoo.exceptions import UserError

from .fix_bridge_exception import ACCOUNTANT, ACCOUNTING_MANAGER, event_source, require_role


class FixAssetCostEntry(models.Model):
    _name = "fix.asset.cost.entry"
    _description = "M52 Pending Asset Cost Entry"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "state, cost_date desc, id desc"

    _key_unique = models.Constraint(
        "UNIQUE (key)", "One M52 cost entry per source document (idempotent hand-off)."
    )

    name = fields.Char(required=True, readonly=True, default="New", copy=False)
    key = fields.Char(required=True, readonly=True, index=True, copy=False)
    cost_type = fields.Selection(
        [
            ("facility_work_order", "Facility Work Order (M47)"),
            ("vehicle_fuel", "Vehicle Fuel (M46)"),
            ("vehicle_service", "Vehicle Service (M46)"),
        ],
        required=True,
        readonly=True,
    )
    company_id = fields.Many2one("res.company", required=True, index=True, readonly=True)
    operating_unit_id = fields.Many2one("operating.unit", string="Cost Centre (OU)", index=True)
    branch_id = fields.Many2one("fix.branch", string="Branch", readonly=True)
    source_model = fields.Char(required=True, readonly=True)
    source_res_id = fields.Integer(required=True, readonly=True, index=True)
    source_ref = fields.Char(string="Source Document", readonly=True)
    site_id = fields.Many2one("fix.site", string="Site", readonly=True)
    vehicle_id = fields.Many2one("fleet.vehicle", string="Vehicle", readonly=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, readonly=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount = fields.Monetary(string="Cost", readonly=True)
    cost_date = fields.Date(string="Cost Date", readonly=True)
    vendor_id = fields.Many2one("res.partner", string="Vendor", readonly=True)
    invoice_ref = fields.Char(string="Vendor Invoice Ref", readonly=True)
    detail = fields.Char(readonly=True, help="Station / receipt, work type, service type")
    state = fields.Selection(
        [("pending", "Pending AP"), ("matched", "Matched to Bill"), ("rejected", "Rejected")],
        default="pending",
        required=True,
        index=True,
        tracking=True,
    )
    source_changed = fields.Boolean(
        readonly=True,
        copy=False,
        help="The source document's cost changed after AP decided this entry",
    )
    vendor_invoice_id = fields.Many2one(
        "fix.vendor.invoice", string="Vendor Bill (M52)", readonly=True, copy=False, index=True
    )
    decided_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    decided_on = fields.Datetime(readonly=True, copy=False)
    decision_note = fields.Text()
    match_invoice_id = fields.Many2one(
        "fix.vendor.invoice",
        string="Bill to Match",
        copy=False,
        help="Choose the vendor bill, then Match to Bill",
    )

    def _fix_guarded_fields(self) -> set:
        # the figures are the source document's; AP decides, it does not retype them
        guarded = super()._fix_guarded_fields() | {
            "name",
            "key",
            "cost_type",
            "company_id",
            "branch_id",
            "source_model",
            "source_res_id",
            "source_ref",
            "site_id",
            "vehicle_id",
            "currency_id",
            "amount",
            "cost_date",
            "vendor_id",
            "invoice_ref",
            "detail",
            "state",
            "source_changed",
            "vendor_invoice_id",
            "decided_by_id",
            "decided_on",
        }
        if any(rec.state != "pending" for rec in self):
            guarded |= {"decision_note", "operating_unit_id", "match_invoice_id"}
        return guarded

    def unlink(self):
        if not self.env.su:
            raise UserError("An M52 cost entry is part of the record: reject it instead.")
        return super().unlink()

    # ---- raising ----------------------------------------------------------------
    @api.model
    def _m52_queue(self, record, vals):
        key = "m52:%s:%s" % (record._name, record.id)
        Entry = self.sudo()._guarded()
        existing = Entry.search([("key", "=", key)], limit=1)
        if existing:
            figures = {k: vals[k] for k in ("amount", "vendor_id", "invoice_ref") if k in vals}
            differs = any(
                (existing[k].id if k == "vendor_id" else existing[k]) != (v or False)
                for k, v in figures.items()
            )
            if not differs:
                return existing  # a redelivery, or a re-close with the same figures
            if existing.state == "pending":
                existing.write(figures)
                existing.message_post(body="The source was closed again: figures refreshed.")
            else:
                existing.write({"source_changed": True})
                existing.message_post(
                    body="The source was closed again with different figures (%s) after AP "
                    "decided this entry: AP reviews it." % figures
                )
            return existing
        vals = dict(
            vals,
            key=key,
            source_model=record._name,
            source_res_id=record.id,
            source_ref=record.display_name,
            name=self.env["ir.sequence"].sudo().next_by_code("fix.asset.cost.entry")
            or "M52COST/New",
        )
        entry = Entry.create(vals)
        entry.message_post(
            body="Pending AP: match it to the vendor bill when it is entered, or reject it "
            "with a reason. It posts nothing."
        )
        return entry

    @api.model
    def consume_facility_work_order_closed(self, event):
        """facility.work_order_closed (M47, branch-verified) -> a cost entry."""
        order = event_source(self.env, event, "fix.facility.work.order")
        payload = event.get("payload") or {}
        cost = float(payload.get("cost") or 0.0)
        if not order or cost <= 0.0:
            return False
        site = order.site_id
        return self._m52_queue(
            order,
            {
                "cost_type": "facility_work_order",
                "company_id": int(payload.get("company_id") or order.company_id.id),
                "operating_unit_id": (
                    site.operating_unit_id or site.branch_id.operating_unit_id
                ).id,
                "branch_id": site.branch_id.id,
                "site_id": site.id,
                "amount": cost,
                "cost_date": fields.Datetime.to_datetime(payload.get("verified_at")).date()
                if payload.get("verified_at")
                else fields.Date.context_today(self),
                "vendor_id": int(payload["vendor_id"]) if payload.get("vendor_id") else False,
                "invoice_ref": payload.get("invoice_ref") or False,
                "detail": "%s / %s"
                % (payload.get("work_type") or "-", payload.get("assigned_type") or "-"),
            },
        )

    @api.model
    def _m52_vehicle_vals(self, vehicle):
        vehicle = vehicle.sudo()
        return {
            "company_id": (vehicle.company_id or self.env.company).id,
            "operating_unit_id": (
                vehicle.operating_unit_id or vehicle.branch_id.operating_unit_id
            ).id,
            "branch_id": vehicle.branch_id.id,
            "vehicle_id": vehicle.id,
        }

    @api.model
    def consume_vehicle_fuel_recorded(self, event):
        """vehicle.fuel_recorded (M46, a fill with no open exception) -> a cost entry."""
        fuel = event_source(self.env, event, "fix.vehicle.fuel")
        payload = event.get("payload") or {}
        amount = float(payload.get("amount") or 0.0)
        if not fuel or amount <= 0.0:
            return False
        vals = self._m52_vehicle_vals(fuel.vehicle_id)
        vals.update(
            {
                "cost_type": "vehicle_fuel",
                "amount": amount,
                "cost_date": fields.Date.to_date(payload.get("filled_on")) or fuel.filled_on,
                "invoice_ref": payload.get("receipt_no") or False,
                "detail": "%s L at %s, receipt %s"
                % (payload.get("litres"), fuel.station or "-", payload.get("receipt_no") or "-"),
            }
        )
        return self._m52_queue(fuel, vals)

    @api.model
    def consume_vehicle_service_completed(self, event):
        """vehicle.service_completed (M46 PM done) -> a cost entry."""
        pm = event_source(self.env, event, "fix.vehicle.pm")
        payload = event.get("payload") or {}
        cost = float(payload.get("cost") or 0.0)
        if not pm or cost <= 0.0:
            return False
        # A service done through a work order of the one work-order spine
        # (cd_asset_workorder_spine links the WO to the PM) is charged once:
        # the WO's facility.work_order_closed entry carries the vendor and the
        # invoice reference AP matches on, so the PM adds no second entry.
        WO = self.env["fix.facility.work.order"].sudo()
        if "vehicle_pm_id" in WO._fields and WO.search_count([("vehicle_pm_id", "=", pm.id)]):
            return False
        vals = self._m52_vehicle_vals(pm.vehicle_id)
        vals.update(
            {
                "cost_type": "vehicle_service",
                "amount": cost,
                "cost_date": fields.Date.to_date(payload.get("done_on")) or pm.done_on,
                "detail": "%s service at %s km"
                % (payload.get("pm_type") or "-", payload.get("odometer") or 0),
            }
        )
        return self._m52_queue(pm, vals)

    # ---- AP's decision ----------------------------------------------------------
    def action_match_bill(self, vendor_invoice_id=None):
        """Match the entry to the vendor bill that charges it. The bill is the
        same company's, not rejected, from the entry's vendor where the source
        named one, and the entries matched to it never exceed its gross."""
        require_role(self.env, [ACCOUNTANT, ACCOUNTING_MANAGER], "Matching an M52 cost entry")
        for rec in self:
            bill = (
                self.env["fix.vendor.invoice"].browse(int(vendor_invoice_id)).exists()
                if vendor_invoice_id
                else rec.match_invoice_id
            )
            if not bill:
                raise UserError("Choose the vendor bill %s is charged on." % rec.name)
            if rec.state != "pending":
                raise UserError("%s is already decided." % rec.name)
            if bill.company_id != rec.company_id:
                raise UserError("%s belongs to another company." % bill.display_name)
            if bill.approval_state == "rejected":
                raise UserError("%s is rejected: match a live bill." % bill.display_name)
            if rec.vendor_id and (
                bill.vendor_id.commercial_partner_id != rec.vendor_id.commercial_partner_id
            ):
                raise UserError(
                    "%s is from %s, but %s's vendor is %s."
                    % (bill.display_name, bill.vendor_id.name, rec.source_ref, rec.vendor_id.name)
                )
            matched = (
                self.sudo().search([("vendor_invoice_id", "=", bill.id), ("state", "=", "matched")])
                - rec
            )
            total = sum(matched.mapped("amount")) + rec.amount
            if total > (bill.gross_amount or 0.0) + 0.005:
                raise UserError(
                    "%s: the cost entries matched to %s would total %.2f, above the bill's "
                    "%.2f." % (rec.name, bill.display_name, total, bill.gross_amount or 0.0)
                )
            rec.sudo()._guarded().write(
                {
                    "state": "matched",
                    "vendor_invoice_id": bill.id,
                    "decided_by_id": self.env.uid,
                    "decided_on": fields.Datetime.now(),
                }
            )
            rec.message_post(body="Matched to vendor bill %s." % bill.display_name)
        return True

    def action_reject(self, reason=None):
        require_role(self.env, [ACCOUNTANT, ACCOUNTING_MANAGER], "Rejecting an M52 cost entry")
        for rec in self:
            if rec.state != "pending":
                raise UserError("%s is already decided." % rec.name)
            note = (reason or rec.decision_note or "").strip()
            if not note:
                raise UserError("Say why %s is rejected (Decision Note)." % rec.name)
            rec.sudo()._guarded().write(
                {
                    "state": "rejected",
                    "decision_note": note,
                    "decided_by_id": self.env.uid,
                    "decided_on": fields.Datetime.now(),
                }
            )
            rec.message_post(body="Rejected: %s" % note)
        return True
