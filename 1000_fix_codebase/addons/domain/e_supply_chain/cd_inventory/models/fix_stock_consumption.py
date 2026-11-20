# cd_inventory — Barcode/QR Scan-to-Consume & Parts Consumption Engine (M15, CD-M15-01).
#
# A06 audit (2026-11-03) M15-3/-5/-6/-15: the issue checked the company-wide
# aggregate, skipped the ledger where the location held no bucket, never
# reduced van stock, took quarantined / in-transit / reserved stock, valued
# the issue at the master's standard cost, accepted -5 (adding stock) and
# 0.25 PCS, issued one serial to two jobs and a serial never received, and a
# forged `consumed` state let a "return" create stock from nothing. Now the
# issue takes UNRESTRICTED, unreserved stock from the bucket of the location
# it names (the `van` class at a van, issued by its custodian), at that
# bucket's average cost; serials are one unit, received, in stock at that
# location, and leave it on issue; the state and the cost are guarded and a
# consumed record is final. A return comes back at the cost it left with;
# a part returned as defective goes to quarantine.
from __future__ import annotations

import logging
from datetime import datetime

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

from .fix_inventory_approval import (
    CONTROLLER_GROUP,
    COST_GROUP,
    STOREKEEPER_GROUP,
    VALUED_CLASSES,
    check_location_usable,
    check_quantity,
    location_class,
    part_codes,
)
from .fix_stock_move_log import move_ctx
from .fix_valuation_suspense import suspense_account_code

_logger = logging.getLogger(__name__)

# The job models an issue can be charged to, looked up only when their addon
# is installed (no manifest dependency on the service-delivery addons).
JOB_MODELS = ("fix.service.order", "fix.workshop.job", "fix.field.order")
WORK_ORDER_MODEL = "fix.work.order"

RETURN_REASONS = [
    ("wrong_diagnosis", "Defect misdiagnosed - part not needed"),
    ("defective_new", "Part DOA / defective out of box"),
    ("customer_refusal", "Customer declined estimate"),
    ("excess_draw", "Excess van stock drawn and returned"),
]

# A06 ERP audit A28: the job states a part is issued in (the A02 bridges'
# gate, now on every issue): an approved service order in repair (or back
# from QC), a workshop job on the bench, a field job on site.
ISSUE_JOB_STATES = {
    "fix.service.order": ("approved", "in_repair", "qc_failed"),
    "fix.workshop.job": ("in_repair",),
    "fix.field.order": ("arrived", "in_progress"),
}
# A06 ERP audit A09: a part does not come back from a job that is finished:
# handed over, closed or completed (a job being cancelled still returns its
# parts, before it is closed).
RETURN_CLOSED_JOB_STATES = {
    "fix.service.order": ("delivered", "closed"),
    "fix.workshop.job": ("delivered",),
    "fix.field.order": ("completed",),
}
# Service-order settlement states that mean the job was invoiced and paid.
SETTLED_STATES = ("settled", "credit_approved")
# D3 (owner decision 20 Nov 2026): the stock type of a warranty store.
WARRANTY_STOCK_TYPE = "warranty"

# A06 final pass B4: which class of stock an issue draws (BRU-INV-01/03/04).
ISSUE_CLASSES = [
    ("owned", "Own Stock (van stock at a van)"),
    ("consignment", "Brand Consignment"),
    ("customer", "Customer Supplied"),
    ("bench", "Bench / WIP"),
    ("warranty", "Warranty Reserve"),
]


class FixStockConsumption(models.Model):
    """Real-time parts consumption on repair jobs via barcode / QR scanning."""

    _name = "fix.stock.consumption"
    _description = "Job Parts Consumption"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]

    company_id = fields.Many2one(
        "res.company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Operating Unit",
        index=True,
    )
    name = fields.Char(
        string="Consumption Reference",
        required=True,
        copy=False,
        default="New",
        index=True,
    )
    name_bn = fields.Char(string="ব্যবহারের রেফারেন্স (বাংলা)", help="Bengali reference per DoD-08")

    service_order_ref = fields.Char(string="Service Order Reference", required=True, index=True)
    work_order_ref = fields.Char(string="Work Order Reference", index=True)
    # A06 M15-10: the job the reference resolved to when the part was issued
    job_model = fields.Char(string="Job Model", readonly=True, copy=False)
    job_res_id = fields.Integer(string="Job ID", readonly=True, copy=False)
    work_order_res_id = fields.Integer(string="Work Order ID", readonly=True, copy=False)

    product_id = fields.Many2one("fix.spare.part", string="Spare Part", required=True, index=True)
    location_id = fields.Many2one(
        "fix.stock.location", string="Deduction Location / Van", required=True, index=True
    )
    technician_id = fields.Many2one(
        "hr.employee", string="Consuming Technician", required=True, index=True
    )
    ownership_class = fields.Selection(
        [
            ("owned", "Owned Stock"),
            ("consignment", "Supplier Consignment"),
            ("customer", "Customer Property"),
            ("van", "Van Stock"),
            ("bench", "Bench / WIP"),
            ("warranty", "Warranty Reserve"),
        ],
        string="Issued From Class",
        readonly=True,
        copy=False,
    )
    issue_class = fields.Selection(
        ISSUE_CLASSES,
        string="Issue From Class",
        default="owned",
        required=True,
        help="Which stock class the issue draws. Brand consignment goes only on a warranty "
        "job for that brand (BRU-INV-01, no override); customer-supplied only on that "
        "customer's job (BRU-INV-04).",
    )
    job_customer_id = fields.Many2one(
        "res.partner",
        string="Customer-Supplied For",
        readonly=True,
        copy=False,
        help="The customer whose own part this issue consumed (BRU-INV-04).",
    )
    lot_id = fields.Many2one(
        "fix.stock.lot", string="Issued Serial / Lot", readonly=True, copy=False
    )

    quantity = fields.Float(string="Consumed Quantity", default=1.0, required=True)
    serial_number = fields.Char(string="Part Serial Number / IMEI")
    scanned_code = fields.Char(string="Raw Scanned Barcode/QR", required=True)

    state = fields.Selection(
        [
            ("draft", "Draft Scan"),
            ("consumed", "Consumed on Job"),
            ("returned", "Returned to Location"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )

    consumed_at = fields.Datetime(string="Consumption Timestamp")
    unit_cost = fields.Float(string="Unit Valuation Cost (BDT)", default=0.0, groups=COST_GROUP)
    total_cost = fields.Float(
        string="Total Valuation Cost (BDT)",
        compute="_compute_total_cost",
        store=True,
        groups=COST_GROUP,
    )

    return_reason = fields.Selection(RETURN_REASONS, string="Return Reason")
    return_notes = fields.Text(string="Return Notes")
    returned_at = fields.Datetime(string="Return Timestamp")
    # A06 ERP audit X19 / D4: stock that carries no cost leaves only on an
    # Inventory Controller's approval (its value is unknown, not nil)
    zero_cost_approved_by_id = fields.Many2one(
        "res.users", string="Uncosted Issue Approved By", readonly=True, copy=False
    )
    zero_cost_approved_at = fields.Datetime(
        string="Uncosted Issue Approved On", readonly=True, copy=False
    )

    # what an issue fixes: the job, the part, the place and the quantity
    _ISSUE_FIELDS = (
        "service_order_ref",
        "work_order_ref",
        "product_id",
        "location_id",
        "technician_id",
        "issue_class",
        "quantity",
        "serial_number",
        "scanned_code",
        "company_id",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "consumed_at",
            "unit_cost",
            "ownership_class",
            "job_customer_id",
            "lot_id",
            "return_reason",
            "returned_at",
            "job_model",
            "job_res_id",
            "work_order_res_id",
            "zero_cost_approved_by_id",
            "zero_cost_approved_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if len(self) == 1 and self.state not in (False, "draft"):
            locked |= set(self._ISSUE_FIELDS) | {"return_notes"}
        return locked

    @api.depends("quantity", "unit_cost")
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = rec.quantity * rec.unit_cost

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.stock.consumption")
                    or f"CNS-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                )
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            frozen = {k: vals[k] for k in (*self._ISSUE_FIELDS, "return_notes") if k in vals}
            issued = self.filtered(lambda r: r.state not in (False, "draft"))
            if frozen and any(
                rec._fix_guard_differs(k, v, rec[k]) for rec in issued for k, v in frozen.items()
            ):
                raise UserError(
                    "An issued part is final: its job, part, location, quantity and cost "
                    "cannot change. Return it and issue again."
                )
        return super().write(vals)

    # ---------------------------------------------------------------- checks
    def _resolve_job(self):
        """A06 M15-10: the job reference must name a real job of this company
        (service order, workshop job or field order, whichever addons are
        installed). Returns (model, id, work_order_id); refuses a reference
        that resolves to nothing."""
        self.ensure_one()
        installed = [m for m in JOB_MODELS if m in self.env]
        if not installed:
            return False, 0, 0
        ref = (self.service_order_ref or "").strip()
        found = (False, 0)
        for model in installed:
            Model = self.env[model].sudo()
            domain = [("name", "=", ref)]
            if "company_id" in Model._fields:
                domain.append(("company_id", "in", [self.company_id.id, False]))
            job = Model.search(domain, limit=1) if ref else Model.browse()
            if job:
                found = (model, job.id)
                break
        if not found[0]:
            raise UserError(
                "Job reference %r matches no service order, workshop job or field order: "
                "a part is issued only to a real job (FR-INV-022)." % ref
            )
        work_order_id = 0
        wo_ref = (self.work_order_ref or "").strip()
        if wo_ref and WORK_ORDER_MODEL in self.env:
            work_order = self.env[WORK_ORDER_MODEL].sudo().search([("name", "=", wo_ref)], limit=1)
            if not work_order:
                raise UserError("Work order reference %r matches no work order." % wo_ref)
            work_order_id = work_order.id
        return found[0], found[1], work_order_id

    def _job_service_order(self, job_model, job_id):
        """The service order behind the job (a field order and a workshop job
        both hang off one): it says whose job it is and whether it is warranty."""
        self.ensure_one()
        if not job_model:
            return self.env["res.partner"].browse()
        job = self.env[job_model].sudo().browse(job_id)
        return job if job_model == "fix.service.order" else job.order_id.sudo()

    def _check_class_rules(self, cls, job_model, job_id, lot):
        """BRU-INV-01/03/04: what each class of stock may be used on. These are
        hard blocks: there is no override at any authority level. Returns the
        customer a customer-supplied part was consumed for."""
        self.ensure_one()
        part = self.product_id
        order = self._job_service_order(job_model, job_id)
        category = order.order_category if order else False
        customer = self.env["res.partner"]
        if cls == "consignment":
            device_brand = order.device_id.sudo().brand_id if order else False
            master = part.sudo()
            if master.brand_id and device_brand:
                # A06 ERP audit A30: the governed brand master decides; the
                # legacy brand text only where the part has no governed brand
                same = master.brand_id == device_brand
            else:
                brand = (device_brand.name or "").strip().lower() if device_brand else ""
                own = (master.device_brand or "").strip().lower()
                same = bool(own) and own == brand
            if category != "warranty" or not same:
                raise UserError(
                    "Brand consignment stock of %s goes only on a warranty job for %s's own "
                    "product (BRU-INV-01). No authority can override this."
                    % (part.part_number, part.device_brand or "its brand")
                )
        elif cls == "customer":
            customer = order.customer_id.commercial_partner_id if order else customer
            if not customer:
                raise UserError(
                    "A customer-supplied part goes only on that customer's job (BRU-INV-04): "
                    "%s has no customer." % (self.service_order_ref or "this job")
                )
            held = sum(
                self.env["fix.stock.receipt.line"]
                .sudo()
                .search(
                    [
                        ("part_id", "=", part.id),
                        ("is_posted", "=", True),
                        ("receipt_id.ownership_class", "=", "customer"),
                        ("receipt_id.location_id", "=", self.location_id.id),
                        ("receipt_id.partner_id", "child_of", customer.id),
                    ]
                )
                .mapped("qty_accepted")
            )
            used = sum(
                self.sudo()
                .search(
                    [
                        ("product_id", "=", part.id),
                        ("location_id", "=", self.location_id.id),
                        ("job_customer_id", "=", customer.id),
                        ("state", "=", "consumed"),
                    ]
                )
                .mapped("quantity")
            )
            if self.quantity > held - used + 1e-9:
                raise UserError(
                    "%s holds %s of its own %s here; this job would use %s. A customer-supplied "
                    "part goes only on that customer's job (BRU-INV-04)."
                    % (customer.name, round(held - used, 4), part.part_number, self.quantity)
                )
        # BRU-INV-03. There is no refurbished class in the ledger: M14 books a
        # harvested part as owned stock, so only a serial can be traced to it.
        if lot and category == "warranty":
            harvested = (
                self.env["fix.stock.receipt"]
                .sudo()
                .search_count(
                    [("name", "=", lot.source_ref), ("source_model", "=", "fix.tradein.harvest")]
                )
            )
            if harvested:
                raise UserError(
                    "Serial %s was harvested from a trade-in: refurbished or harvested parts "
                    "never go on warranty work (BRU-INV-03)." % lot.name
                )
        return customer

    def _check_issue(self):
        """Every rule an issue must satisfy before stock moves."""
        self.ensure_one()
        part = self.product_id
        if not part:
            raise ValidationError("No valid spare part assigned to consumption.")
        # BRU-CAT-10 / B16: a discontinued part is run down (it stays serviceable
        # for what it covers; buying more is refused at the requisition and PO);
        # an obsolete one is out of service.
        if part.state == "obsolete":
            raise UserError("%s is obsolete and cannot be issued to a job." % part.part_number)
        check_quantity(part, self.quantity, "issue quantity")
        # FR-INV-022: the scan confirms the issue, so it must read this part
        # (or the serial being issued), not any text
        code = (self.scanned_code or "").strip()
        if code not in part_codes(part) and not (
            part.is_serialized and code == (self.serial_number or "").strip()
        ):
            raise UserError(
                "Scanned code %r is not %s: scan the part's barcode, QR code or part number."
                % (code, part.part_number)
            )
        location = self.location_id
        check_location_usable(location, self.env)
        if location.location_type in ("quarantine", "scrap"):
            raise UserError(
                "%s is a %s location: stock there is not issuable."
                % (location.code, location.location_type)
            )
        if location.location_type == "van":
            if self.technician_id != location.technician_id:
                raise UserError(
                    "Van %s is in the custody of %s: %s cannot draw from it (FR-INV-028)."
                    % (
                        location.code,
                        location.technician_id.name or "nobody",
                        self.technician_id.name,
                    )
                )
            # M15-14: the custodian himself, not a name typed by someone else
            if (
                not self.env.su
                and self.technician_id.user_id != self.env.user
                and not self.env.user.has_group(CONTROLLER_GROUP)
            ):
                raise UserError(
                    "Van %s is in the custody of %s: only that technician (or an Inventory "
                    "Controller) issues from it (FR-INV-028)."
                    % (location.code, location.technician_id.name)
                )
        # BRU-INV-12 / M15-8: the variance blocks the TECHNICIAN's next issue,
        # wherever it is drawn from, as well as the van it arose on
        hold = (
            self.env["fix.stock.van.recon"]
            .sudo()
            .search(
                [
                    ("state", "=", "discrepancy"),
                    "|",
                    ("location_id", "=", location.id),
                    ("technician_id", "=", self.technician_id.id),
                ],
                limit=1,
            )
        )
        if hold:
            raise UserError(
                "Van %s has an unresolved stock discrepancy (%s): issues to %s are held until "
                "an Inventory Controller resolves it (BRU-INV-12)."
                % (hold.location_id.code, hold.name, hold.technician_id.name or "its technician")
            )
        if part.is_serialized:
            if not self.serial_number:
                raise ValidationError(
                    f"Part {part.part_number} is serialized. Serial number is mandatory."
                )
            if abs(self.quantity - 1.0) > 1e-9:
                raise UserError(
                    "%s is serialized: one issue takes one serial (one unit), not %s."
                    % (part.part_number, self.quantity)
                )
            lot = self.env["fix.stock.lot"]._fix_find(part, self.serial_number)
            if not lot:
                raise UserError(
                    "Serial %s of %s was never received: it cannot be issued (BRU-INV-14). "
                    "Quarantine the unit and report it." % (self.serial_number, part.part_number)
                )
            if lot.status != "in_stock" or lot.location_id != location or (lot.qty or 0.0) < 1.0:
                raise UserError(
                    "Serial %s is %s at %s, not in stock at %s: it cannot be issued again."
                    % (
                        lot.name,
                        dict(lot._fields["status"].selection).get(lot.status),
                        lot.location_id.code or "-",
                        location.code,
                    )
                )
            return lot
        return self.env["fix.stock.lot"]

    def _check_job_state(self, job_model, job_id):
        """A06 ERP audit A28: a part is issued only to a job that is live
        work (the gate the A02 bridges applied, now on the direct issue too)."""
        self.ensure_one()
        states = ISSUE_JOB_STATES.get(job_model)
        if not states or self.env.su:
            # trusted service code (the A02 bridges) applies its own job gate
            return
        job = self.env[job_model].sudo().browse(job_id)
        if job.state not in states:
            raise UserError(
                "Parts are issued to %s only while it is %s; it is %s."
                % (job.display_name, " / ".join(states), job.state)
            )

    @api.model
    def _job_is_warranty(self, order) -> bool:
        """D3: a warranty job is a service order of the warranty category."""
        return bool(order) and order.order_category == "warranty"

    @api.model
    def _store_is_warranty(self, location) -> bool:
        return (location.sudo().stock_type or False) == WARRANTY_STOCK_TYPE

    def _check_warranty_store(self, job_model, job_id):
        """D3 (owner decision 20 Nov 2026) / A19: brand warranty parts are
        company-owned stock kept in warranty stores. A warranty job draws only
        from a warranty store, any other job never does."""
        self.ensure_one()
        if not job_model:
            return
        order = self._job_service_order(job_model, job_id)
        warranty_job = self._job_is_warranty(order)
        warranty_store = self._store_is_warranty(self.location_id)
        if warranty_job and not warranty_store:
            raise UserError(
                "%s is a warranty job: its parts come only from a warranty store, and %s is "
                "not one (D3)." % (order.name, self.location_id.code)
            )
        if warranty_store and not warranty_job:
            raise UserError(
                "%s is a warranty store: its parts go only on warranty jobs, and %s is not "
                "one (D3)." % (self.location_id.code, order.name or self.service_order_ref)
            )

    def action_approve_zero_cost(self, note=None):
        """X19 / D4: an Inventory Controller (not the technician who issues
        it) lets an issue of uncosted stock go ahead."""
        if not self.env.su and not self.env.user.has_group(CONTROLLER_GROUP):
            raise AccessError("Only an Inventory Controller approves the issue of uncosted stock.")
        for rec in self:
            if rec.state != "draft":
                raise UserError("%s is no longer a draft issue." % rec.name)
            if not self.env.su and self.env.user in (rec.create_uid | rec.technician_id.user_id):
                raise UserError(
                    "Segregation of duties: you raised or issue %s, so another Inventory "
                    "Controller approves it." % rec.name
                )
            rec.sudo()._guarded().write(
                {
                    "zero_cost_approved_by_id": self.env.user.id,
                    "zero_cost_approved_at": fields.Datetime.now(),
                }
            )
            if note:
                rec.sudo().message_post(body="Uncosted issue approved: %s" % note)
        return True

    def action_scan_and_consume(self) -> dict:
        """Atomic scan-to-consume: deducts the location bucket, values the
        issue at the bucket's average cost, books the suspense entry and
        emits the outbox event."""
        self.ensure_one()
        if self.state != "draft":
            raise UserError("Only draft scans can be confirmed for consumption.")
        lot = self._check_issue()
        job_model, job_id, work_order_id = self._resolve_job()
        self._check_job_state(job_model, job_id)
        self._check_warranty_store(job_model, job_id)
        part = self.product_id
        cls = location_class(self.location_id, self.issue_class or "owned")
        customer = self._check_class_rules(cls, job_model, job_id, lot)
        Onhand = self.env["fix.stock.onhand"].with_context(**move_ctx(self))
        bucket = Onhand._bucket(part, self.location_id, cls)
        available = (bucket.qty - bucket.reserved) if bucket else 0.0
        if available + 1e-9 < self.quantity:
            raise UserError(
                f"Insufficient stock for {part.part_number} at {self.location_id.code}: "
                f"{round(available, 4)} available, {self.quantity} requested."
            )
        cost = bucket.unit_cost or 0.0
        if cls in VALUED_CLASSES and cost <= 1e-9 and not self.zero_cost_approved_by_id:
            raise UserError(
                "%s at %s carries no cost: its value is unknown, so an Inventory Controller "
                "approves the issue first (D4) - or Finance prices the stock."
                % (part.part_number, self.location_id.code)
            )
        Onhand._fix_check_bins(part, self.location_id, self.quantity)
        Onhand._apply(part, self.location_id, cls, -self.quantity)
        if lot:
            lot._fix_move("issued", qty=0.0)

        now_utc = fields.Datetime.now()
        # as sudo: a technician holds no rights on the guarded cost
        self.sudo()._guarded().write(
            {
                "state": "consumed",
                "consumed_at": now_utc,
                "unit_cost": cost,
                "ownership_class": cls,
                "job_customer_id": customer.id or False,
                "lot_id": lot.id or False,
                "job_model": job_model,
                "job_res_id": job_id,
                "work_order_res_id": work_order_id,
            }
        )

        # Post GV-005 suspense valuation entry (M15 -> M19 stub). Consignment and
        # customer stock is held, never valued (BRU-INV-02): it books nothing.
        Suspense = self.env["fix.inventory.valuation.suspense"].sudo()
        suspense_entry = Suspense.browse()
        if cls in VALUED_CLASSES:
            suspense_entry = Suspense.create(
                {
                    "company_id": self.company_id.id,
                    "operating_unit_id": self.location_id.operating_unit_id.id or False,
                    "consumption_id": self.id,
                    "product_id": part.id,
                    "quantity": self.quantity,
                    "unit_cost": cost,
                    "total_valuation": self.quantity * cost,
                    "entry_type": "consumption",
                    "source_ref": self.name,
                    "suspense_account_code": suspense_account_code(self.env),
                    "status": "pending_gl_cutover",
                }
            )

        # Emit M15 outbox event: stock.consumed
        event_payload = {
            "consumption_id": self.id,
            "consumption_ref": self.name,
            "service_order_ref": self.service_order_ref,
            "work_order_ref": self.work_order_ref or "",
            "part_id": part.id,
            "part_number": part.part_number,
            "quantity": self.quantity,
            "ownership_class": cls,
            "location_id": self.location_id.id,
            "location_code": self.location_id.code,
            "technician_id": self.technician_id.id,
            "serial_number": self.serial_number or "",
            "scanned_code": self.scanned_code,
            "consumed_at": str(now_utc),
            "suspense_entry_id": suspense_entry.id or None,
        }

        # A06 ERP audit A33: the event the ledger promises is published inside
        # the issue's transaction; a failed publish fails the issue
        publish(self.env, "stock.consumed", "fix.stock.consumption", self.id, event_payload)

        return {
            "status": "consumed",
            "consumption_ref": self.name,
            "remaining_qty": part.qty_available,
            "valuation_entry": suspense_entry.name or None,
        }

    def _check_return_allowed(self):
        """A06 ERP audit A09: a part comes back only from a job that is not
        finished (handed over, closed, completed, or settled), and only into
        the store's hands: a storekeeper or Inventory Controller of the
        issuing location, or the van's own custodian. A job being cancelled
        returns its parts (trusted service code is exempt from the role)."""
        self.ensure_one()
        job_model, job_id = self.job_model, self.job_res_id
        if job_model and job_model in self.env and job_id:
            job = self.env[job_model].sudo().browse(job_id).exists()
            closed = RETURN_CLOSED_JOB_STATES.get(job_model, ())
            order = self._job_service_order(job_model, job_id) if job else None
            settled = bool(
                order
                and "payment_settlement_state" in order._fields
                and order.payment_settlement_state in SETTLED_STATES
                and order.state in ("ready", "delivered", "closed")
            )
            if job and (job.state in closed or settled):
                raise UserError(
                    "%s is %s: a part does not come back from a finished job (its cost is on "
                    "the customer's bill). Book it as a new receipt or a count, with a reason."
                    % (job.display_name, "settled" if settled else job.state)
                )
        if self.env.su:
            return
        user = self.env.user
        location = self.location_id
        custodian = location.location_type == "van" and location.technician_id.user_id == user
        if not (custodian or user.has_group(STOREKEEPER_GROUP) or user.has_group(CONTROLLER_GROUP)):
            raise AccessError(
                "A part is returned into %s by its store (a storekeeper or Inventory "
                "Controller) or, at a van, by its custodian." % location.code
            )

    def action_return_part(self, reason: str | None = None, notes: str = "") -> dict:
        """Atomic part return at the cost it was issued at. A part returned
        as defective (DOA) goes to quarantine, not back to available stock."""
        self.ensure_one()
        if self.state != "consumed":
            raise UserError("Only consumed parts can be returned to inventory.")
        if reason not in dict(RETURN_REASONS):
            raise UserError(
                "Give the return reason: %s." % ", ".join(k for k, _l in RETURN_REASONS)
            )
        self._check_return_allowed()
        part = self.product_id
        check_location_usable(self.location_id, self.env)
        cls = self.ownership_class or location_class(self.location_id)
        defective = reason == "defective_new"
        cost = self.sudo().unit_cost
        Onhand = self.env["fix.stock.onhand"].with_context(**move_ctx(self))
        Onhand._apply(
            part,
            self.location_id,
            cls,
            self.quantity,
            cost,
            status="quarantine" if defective else "unrestricted",
        )
        lot = self.lot_id
        if lot:
            lot._fix_move("quarantined" if defective else "in_stock", self.location_id, 1.0)
        quarantine = self.env["fix.stock.quarantine"]
        if defective:
            quarantine = (
                quarantine.sudo()
                ._guarded()
                .with_context(fix_quarantine_in_place=True)
                .create(
                    {
                        "part_id": part.id,
                        "location_id": self.location_id.id,
                        "company_id": self.company_id.id,
                        "ownership_class": cls,
                        "lot_id": lot.id or False,
                        "qty": self.quantity,
                        "reason": "defective",
                        "notes": "Returned as defective from %s" % self.name,
                        "source_ref": self.name,
                    }
                )
            )

        now_utc = fields.Datetime.now()
        self.sudo()._guarded().write(
            {
                "state": "returned",
                "return_reason": reason,
                "returned_at": now_utc,
            }
        )
        if notes:
            self.sudo()._guarded().write({"return_notes": notes})

        # Post reverse suspense valuation entry, at the ISSUE cost (the issue of
        # a non-valued class booked nothing, so neither does its return)
        Suspense = self.env["fix.inventory.valuation.suspense"].sudo()
        suspense_entry = Suspense.browse()
        if cls in VALUED_CLASSES:
            suspense_entry = Suspense.create(
                {
                    "company_id": self.company_id.id,
                    "operating_unit_id": self.location_id.operating_unit_id.id or False,
                    "consumption_id": self.id,
                    "product_id": part.id,
                    "quantity": -self.quantity,
                    "unit_cost": cost,
                    "total_valuation": -(self.quantity * cost),
                    "entry_type": "return",
                    "source_ref": self.name,
                    "suspense_account_code": suspense_account_code(self.env),
                    "status": "pending_gl_cutover",
                }
            )

        # Emit M15 outbox event: stock.returned
        event_payload = {
            "consumption_id": self.id,
            "consumption_ref": self.name,
            "service_order_ref": self.service_order_ref,
            "part_id": part.id,
            "part_number": part.part_number,
            "quantity": self.quantity,
            "location_id": self.location_id.id,
            "return_reason": reason,
            "returned_at": str(now_utc),
            "suspense_entry_id": suspense_entry.id or None,
        }

        publish(self.env, "stock.returned", "fix.stock.consumption", self.id, event_payload)

        return {
            "status": "returned",
            "consumption_ref": self.name,
            "restored_qty": part.qty_available,
            "quarantine": quarantine.name or None,
        }
