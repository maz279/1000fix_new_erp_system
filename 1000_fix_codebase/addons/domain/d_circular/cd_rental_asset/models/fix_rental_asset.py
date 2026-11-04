# fix_rental_asset — M13: rental reservation, damage, deposit (P09-M03 / R07-M03).
from __future__ import annotations

import re
from decimal import ROUND_HALF_UP, Decimal

from odoo import api, fields, models
from odoo.addons.cd_tax_engine_bd.models import tax_logic
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

# Stamp Act 1899 Sch-I Art.5 (agreement) / Art.15 (bond): an executed rental
# agreement carrying a money deposit cites its adhesive stamp serial. A Smart
# NID is 10 digits, the legacy NID 13 or 17.
_STAMP_CERT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9\-/]{3,}$")
_NID_RE = re.compile(r"^\d{10}(\d{3}|\d{7})?$")


class FixRentalReservation(models.Model):
    """Journey 8: reserve -> deliver -> active -> return -> damage_assess
    -> closed. Availability checked against overlapping reservations.
    Composes M37 rental SKUs, M03 logistics, M39 subscription billing,
    and M01 service order loaner intake (FR-SRM-063/064)."""

    _name = "fix.rental.reservation"
    _description = "Rental Reservation"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_from desc, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    branch_id = fields.Many2one(
        "fix.branch",
        string="Booking Branch",
        index=True,
        help="The branch the rental, its deposit GL postings and their COA-03 "
        "branch dimension belong to. Shared branches (no company) are selectable.",
    )
    name = fields.Char(required=True, copy=False, readonly=True, default=lambda self: "New")
    customer_id = fields.Many2one("res.partner", string="Customer", required=True, index=True)
    contract_id = fields.Many2one(
        "fix.contract",
        string="Rental Contract",
        ondelete="set null",
        domain=[("family", "=", "rental")],
    )
    rental_sku_id = fields.Many2one(
        "fix.rental.sku",
        string="Rental SKU (M37)",
        ondelete="restrict",
        index=True,
        help="M37 catalog item defining rental rates and deposit",
    )
    device_id = fields.Many2one(
        "fix.device", string="Rental Asset", ondelete="restrict", index=True
    )
    fixed_asset_id = fields.Many2one(
        "fix.fixed.asset", string="Fixed Asset (M49)", ondelete="set null"
    )
    service_order_id = fields.Many2one(
        "fix.service.order",
        string="Origin Service Order (M01)",
        ondelete="set null",
        help="FR-SRM-063/064: loaner/swap-out device for customer repair",
    )
    date_from = fields.Date(required=True, default=fields.Date.context_today)
    date_to = fields.Date(required=True, default=fields.Date.context_today)
    actual_return_date = fields.Date(string="Actual Return Date")
    duration_days = fields.Integer(
        compute="_compute_duration", store=True, string="Duration (Days)"
    )

    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    deposit_collected = fields.Monetary(
        string="Deposit Collected",
        currency_field="currency_id",
        help="Security deposit collected upfront",
    )
    deposit_refunded = fields.Monetary(
        string="Deposit Refunded",
        currency_field="currency_id",
        readonly=True,
        help="Amount refunded to customer after damage deduction",
    )
    daily_rate = fields.Monetary(string="Daily Rate", currency_field="currency_id")
    weekly_rate = fields.Monetary(string="Weekly Rate", currency_field="currency_id")
    monthly_rate = fields.Monetary(string="Monthly Rate", currency_field="currency_id")
    rental_charge = fields.Monetary(
        compute="_compute_rental_charge",
        store=True,
        string="Rental Fee",
        currency_field="currency_id",
    )
    late_fee = fields.Monetary(string="Late Return Fee", currency_field="currency_id", default=0.0)
    excess_billed = fields.Monetary(
        string="Excess Damage Billed",
        currency_field="currency_id",
        readonly=True,
        help="Charges exceeding deposit amount invoiced via M20",
    )

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("reserved", "Reserved"),
            ("delivered", "Delivered"),
            ("active", "Active"),
            ("returned", "Returned"),
            ("damage_assess", "Damage Assessment"),
            ("closed", "Closed"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    damage_ids = fields.One2many("fix.rental.damage", "reservation_id", string="Damage Records")
    damage_total = fields.Monetary(
        compute="_compute_damage", string="Damage Total", currency_field="currency_id"
    )

    delivery_consignment_id = fields.Many2one(
        "fix.consignment", string="Outbound Delivery Consignment (M03)", ondelete="set null"
    )
    return_consignment_id = fields.Many2one(
        "fix.consignment", string="Return Consignment (M03)", ondelete="set null"
    )
    subscription_id = fields.Many2one(
        "fix.subscription", string="Rental Subscription (M39)", ondelete="set null"
    )
    rental_asset_id = fields.Many2one(
        "fix.rental.asset",
        string="Fleet Asset",
        ondelete="set null",
        index=True,
        help="The serialised fleet unit on rent; availability is checked per asset",
    )
    agreement_state = fields.Selection(
        [
            ("draft", "Draft"),
            ("sent", "Signature Requested"),
            ("signed", "Signed"),
            ("declined", "Declined"),
        ],
        string="Agreement (e-sign)",
        default="draft",
        required=True,
    )
    signed_at = fields.Datetime(string="Signed At")
    signature_ref = fields.Char(string="Signature Reference")

    # ---- Journey 8 statutory & logistics capture (A05 v2.1 spec) -----------
    delivery_method = fields.Selection(
        [
            ("pickup", "Customer Pickup"),
            ("courier", "Courier (M03)"),
            ("van", "1000 FiX Van (M03)"),
            ("rider", "Rider Delivery"),
        ],
        string="Delivery Method",
        default="courier",
        help="How the asset travels to the customer (M03 executes it)",
    )
    logistics_tracking_ref = fields.Char(
        string="Logistics Tracking Ref",
        help="The M03 consignment / courier waybill reference",
    )
    stamp_duty_cert_no = fields.Char(
        string="Stamp Duty Certificate No",
        tracking=True,
        help="Adhesive stamp serial of the agreement/bond duty stamp "
        "(Stamp Act 1899 Sch-I Art.5 / Art.15)",
    )
    deposit_bond_ref = fields.Char(
        string="Deposit Bond Ref",
        help="The bonded deposit instrument reference, where the deposit is held as a bond",
    )
    signer_mobile = fields.Char(
        string="Signer Mobile",
        help="OTP-verified mobile of the signing customer (e-sign evidence)",
    )
    liability_cap_amount = fields.Monetary(
        string="Liability Cap (BDT)",
        currency_field="currency_id",
        help="Indemnity ceiling agreed in the rental agreement's special terms",
    )
    special_terms = fields.Text(
        string="Special Terms & Indemnity Clauses",
        help="Arbitration city, loss-valuation basis and any negotiated clauses",
    )
    legal_counsel_id = fields.Many2one("res.users", string="Legal Counsel (Sign-off)", index=True)
    legal_approval_date = fields.Date(string="Legal Approval Date")
    kit_id = fields.Many2one(
        "fix.rental.kit", string="Rental Kit (M13)", ondelete="set null", index=True
    )
    mushak_6_3_id = fields.Many2one(
        "fix.ar.invoice",
        string="Rental Tax Invoice (Mushak 6.3)",
        ondelete="set null",
        help="The M20 VAT invoice issued for the rental charges",
    )

    @api.depends("date_from", "date_to")
    def _compute_duration(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                days = (rec.date_to - rec.date_from).days + 1
                rec.duration_days = max(days, 1)
            else:
                rec.duration_days = 1

    @api.onchange("rental_sku_id")
    def _onchange_rental_sku(self):
        if self.rental_sku_id:
            self.daily_rate = self.rental_sku_id.daily_rate
            self.weekly_rate = self.rental_sku_id.weekly_rate
            self.monthly_rate = self.rental_sku_id.monthly_rate
            if not self.deposit_collected:
                self.deposit_collected = self.rental_sku_id.security_deposit

    @api.depends("duration_days", "daily_rate", "weekly_rate", "monthly_rate")
    def _compute_rental_charge(self):
        for rec in self:
            days = rec.duration_days or 1
            if days >= 30 and rec.monthly_rate:
                months = days // 30
                rem_days = days % 30
                rec.rental_charge = (months * rec.monthly_rate) + (
                    rem_days * (rec.daily_rate or (rec.monthly_rate / 30.0))
                )
            elif days >= 7 and rec.weekly_rate:
                weeks = days // 7
                rem_days = days % 7
                rec.rental_charge = (weeks * rec.weekly_rate) + (
                    rem_days * (rec.daily_rate or (rec.weekly_rate / 7.0))
                )
            else:
                rec.rental_charge = days * rec.daily_rate

    @api.depends("damage_ids.cost")
    def _compute_damage(self):
        for rec in self:
            rec.damage_total = sum(rec.damage_ids.mapped("cost"))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.rental.reservation") or "RENT/New"
                )
        return super().create(vals_list)

    def action_reserve(self):
        """The availability check: overlapping ACTIVE reservations for the
        same device are refused (one asset, one customer at a time)."""
        for rec in self:
            if rec.date_to < rec.date_from:
                raise UserError("Rental window is inverted")
            if rec.device_id:
                overlaps = self.search_count(
                    [
                        ("device_id", "=", rec.device_id.id),
                        ("state", "in", ("reserved", "delivered", "active")),
                        ("date_from", "<=", rec.date_to),
                        ("date_to", ">=", rec.date_from),
                        ("id", "!=", rec.id),
                    ]
                )
                if overlaps:
                    raise UserError(
                        "Rental asset %s is already reserved for the overlapping "
                        "period — availability is blocking, not advisory" % rec.device_id.name
                    )
            if rec.rental_asset_id:
                if rec.rental_asset_id.status in ("retired", "maintenance"):
                    raise UserError(
                        "Fleet asset %s is %s and cannot be reserved"
                        % (rec.rental_asset_id.name, rec.rental_asset_id.status)
                    )
                asset_overlaps = self.search_count(
                    [
                        ("rental_asset_id", "=", rec.rental_asset_id.id),
                        ("state", "in", ("reserved", "delivered", "active")),
                        ("date_from", "<=", rec.date_to),
                        ("date_to", ">=", rec.date_from),
                        ("id", "!=", rec.id),
                    ]
                )
                if asset_overlaps:
                    raise UserError(
                        "Fleet asset %s is already reserved for the overlapping "
                        "period — availability is blocking, not advisory" % rec.rental_asset_id.name
                    )
                rec.rental_asset_id.status = "reserved"
            rec.state = "reserved"
            self.env["fix.rental.deposit"]._post(
                rec, "collect", rec.deposit_collected, "Deposit collected on reservation"
            )
            publish(
                self.env,
                "rental.reserved",
                "fix.rental.reservation",
                rec.id,
                {
                    "customer": rec.customer_id.name,
                    "sku": rec.rental_sku_id.name if rec.rental_sku_id else "",
                    "from": str(rec.date_from),
                    "to": str(rec.date_to),
                    "deposit": float(rec.deposit_collected),
                },
            )

    def _logistics_operating_unit(self):
        """M03 consignments are OU-scoped (operating_unit_id is required):
        the reservation's OU, else the acting user's default OU."""
        self.ensure_one()
        ou = self.operating_unit_id or self.env.user.default_operating_unit_id
        if not ou:
            raise UserError(
                "Rental %s has no operating unit — M03 logistics cannot be dispatched" % self.name
            )
        return ou

    def action_generate_delivery_consignment(self):
        """Creates outbound delivery through M03 logistics (once per rental).
        Returns the delivery consignments of every reservation in self."""
        for rec in self:
            if rec.state != "reserved":
                raise UserError("Can only dispatch delivery for reserved rentals")
            if not rec.delivery_consignment_id:
                consignment = self.env["fix.consignment"].create(
                    {
                        "consignment_type": "delivery",
                        "scheduled_date": fields.Datetime.now(),
                        "operating_unit_id": rec._logistics_operating_unit().id,
                        "service_order_id": rec.service_order_id.id
                        if rec.service_order_id
                        else False,
                    }
                )
                rec.delivery_consignment_id = consignment.id
        return self.mapped("delivery_consignment_id")

    def action_deliver(self):
        for rec in self:
            if rec.state != "reserved":
                raise UserError("Deliver from reserved")
            rec.state = "delivered"
            if rec.rental_asset_id:
                rec.rental_asset_id.status = "out"
            publish(
                self.env,
                "rental.delivered",
                "fix.rental.reservation",
                rec.id,
                {
                    "customer": rec.customer_id.name,
                    "consignment": rec.delivery_consignment_id.name
                    if rec.delivery_consignment_id
                    else "",
                },
            )

    def action_activate(self):
        for rec in self:
            if rec.state not in ("delivered", "reserved"):
                raise UserError("Activate from delivered or reserved")
            rec.state = "active"
            publish(
                self.env,
                "rental.activated",
                "fix.rental.reservation",
                rec.id,
                {"customer": rec.customer_id.name, "start_date": str(rec.date_from)},
            )

    def action_generate_return_consignment(self):
        """Creates return collection consignment through M03 logistics (once
        per rental). Returns the return consignments of every reservation."""
        for rec in self:
            if rec.state not in ("active", "delivered"):
                raise UserError("Return consignment requires active or delivered rental")
            if not rec.return_consignment_id:
                consignment = self.env["fix.consignment"].create(
                    {
                        "consignment_type": "pickup",
                        "scheduled_date": fields.Datetime.now(),
                        "operating_unit_id": rec._logistics_operating_unit().id,
                        "service_order_id": rec.service_order_id.id
                        if rec.service_order_id
                        else False,
                    }
                )
                rec.return_consignment_id = consignment.id
        return self.mapped("return_consignment_id")

    def action_return(self):
        for rec in self:
            if rec.state != "active":
                raise UserError("Return from active")
            today = fields.Date.context_today(self)
            rec.actual_return_date = today
            # Compute late fee if returned after date_to
            if rec.date_to and today > rec.date_to:
                overdue_days = (today - rec.date_to).days
                daily = rec.daily_rate or (rec.rental_charge / max(rec.duration_days, 1))
                rec.late_fee = overdue_days * daily * 1.5  # 1.5x standard rate for overdue
            rec.state = "returned"
            if rec.rental_asset_id:
                rec.rental_asset_id.status = "maintenance"
                self.env["fix.rental.turnaround"].create(
                    {
                        "rental_asset_id": rec.rental_asset_id.id,
                        "reservation_id": rec.id,
                        "returned_on": today,
                        "grade_before": rec.rental_asset_id.condition_grade,
                    }
                )
            publish(
                self.env,
                "rental.returned",
                "fix.rental.reservation",
                rec.id,
                {
                    "customer": rec.customer_id.name,
                    "actual_return_date": str(today),
                    "late_fee": float(rec.late_fee),
                },
            )

    def action_assess_damage(self):
        """Journey 8's damage step: condition inspection and damage quantification."""
        for rec in self:
            if rec.state != "returned":
                raise UserError("Assess damage from returned")
            rec.state = "damage_assess"
            publish(
                self.env,
                "rental.damage_assessed",
                "fix.rental.reservation",
                rec.id,
                {"damage_total": float(rec.damage_total)},
            )

    def action_close(self):
        """The deposit settlement & billing closure:
        total_charges = damage_total + late_fee
        deposit_deduction = min(total_charges, deposit_collected)
        deposit_refunded = max(deposit_collected - total_charges, 0)
        excess_billed = max(total_charges - deposit_collected, 0)
        100% money path coverage guaranteed."""
        for rec in self:
            if rec.state != "damage_assess":
                raise UserError("Close from damage assessment")
            total_charges = rec.damage_total + rec.late_fee
            deduction = min(total_charges, rec.deposit_collected)
            refund = max(rec.deposit_collected - total_charges, 0.0)
            excess = max(total_charges - rec.deposit_collected, 0.0)

            rec.write({"state": "closed", "deposit_refunded": refund, "excess_billed": excess})
            ledger = self.env["fix.rental.deposit"]
            ledger._post(rec, "deduction", deduction, "Damage and late fees deducted")
            ledger._post(rec, "refund", refund, "Deposit balance refunded")
            publish(
                self.env,
                "rental.closed",
                "fix.rental.reservation",
                rec.id,
                {
                    "rental_charge": float(rec.rental_charge),
                    "deposit_collected": float(rec.deposit_collected),
                    "damage_total": float(rec.damage_total),
                    "late_fee": float(rec.late_fee),
                    "deduction": float(deduction),
                    "refund": float(refund),
                    "excess_billed": float(excess),
                },
            )

    # ------------------------------------------------------------------
    # Agreement execution (e-sign + Stamp Act 1899)
    # ------------------------------------------------------------------

    @api.constrains("agreement_state", "stamp_duty_cert_no", "deposit_collected")
    def _check_stamp_duty_on_signed_agreement(self):
        """A SIGNED agreement that carries a money deposit must cite its
        adhesive stamp serial (Stamp Act 1899 Sch-I Art.5 agreement duty /
        Art.15 bond duty). A draft may be prepared without it."""
        for rec in self:
            if (
                rec.agreement_state == "signed"
                and rec.deposit_collected
                and not (rec.stamp_duty_cert_no or "").strip()
            ):
                raise ValidationError(
                    "Rental %s: a signed agreement holding a security deposit of %.2f BDT "
                    "requires its stamp duty certificate number (Stamp Act 1899 "
                    "Sch-I Art.5/Art.15)." % (rec.name, rec.deposit_collected)
                )
            if rec.stamp_duty_cert_no and not _STAMP_CERT_RE.match(rec.stamp_duty_cert_no.strip()):
                raise ValidationError(
                    "Stamp duty certificate %r is not a valid adhesive stamp serial."
                    % rec.stamp_duty_cert_no
                )

    def action_send_agreement(self):
        """Draft -> signature requested. The customer gets the agreement for
        e-signature; nothing is binding yet."""
        for rec in self:
            if rec.agreement_state != "draft":
                raise UserError("Agreement can only be sent for signature from draft")
            if not (rec.signature_ref or "").strip() and not rec.signer_mobile:
                raise UserError(
                    "Agreement sending needs the signature reference or the signer's "
                    "OTP-verified mobile"
                )
            rec.agreement_state = "sent"

    def action_sign_agreement(self):
        """Signature requested -> signed. The stamp-duty gate is a database
        constraint, so it fires here too; signed_at is evidence."""
        for rec in self:
            if rec.agreement_state != "sent":
                raise UserError("Agreement can only be signed after it was sent")
            denial = ""
            if not (rec.signature_ref or "").strip():
                denial = "the signature reference is missing"
            elif rec.deposit_collected and not (rec.stamp_duty_cert_no or "").strip():
                denial = (
                    "a deposit-holding agreement needs its stamp duty certificate "
                    "number before signature (Stamp Act 1899 Art.5/Art.15)"
                )
            if denial:
                raise UserError("Rental %s cannot be signed: %s" % (rec.name, denial))
            rec.write({"agreement_state": "signed", "signed_at": fields.Datetime.now()})

    # ------------------------------------------------------------------
    # Mushak 6.3 — the rental charge invoice (M20 paper, M51 rates)
    # ------------------------------------------------------------------

    def action_issue_rental_invoice(self):
        """Issue the rental's Mushak 6.3 through M20: rental charge + late
        fee as taxable services at the standard 15% (M51 determination).
        Damage settled from the deposit is compensation against the
        customer's own money, never a VAT supply — it is NOT invoiced here
        (it posts to recovery income in the deposit ledger instead)."""
        Invoice = self.env["fix.ar.invoice"]
        for rec in self:
            if rec.mushak_6_3_id:
                raise UserError(
                    "Rental %s already carries invoice %s" % (rec.name, rec.mushak_6_3_id.name)
                )
            taxable = (rec.rental_charge or 0.0) + (rec.late_fee or 0.0)
            if taxable <= 0:
                raise UserError(
                    "Rental %s has no taxable charge to invoice (rental fee + late fee)" % rec.name
                )
            determination = tax_logic.determine_tax(
                [
                    tax_logic.TaxLine(
                        product_code="RENTAL",
                        qty=Decimal("1"),
                        unit_price=Decimal(str(taxable)).quantize(Decimal("0.01"), ROUND_HALF_UP),
                    )
                ]
            )
            det = determination.lines[0]
            invoice = Invoice.create(
                {
                    "company_id": rec.company_id.id,
                    "customer_id": rec.customer_id.id,
                    "branch_id": rec.branch_id.id,
                    "operating_unit_id": (
                        rec.operating_unit_id
                        or rec.branch_id.operating_unit_id
                        or self.env["operating.unit"].search(
                            [("company_id", "=", rec.company_id.id)], limit=1
                        )
                    ).id,
                    "source_model": "fix.rental.reservation",
                    "source_id": rec.id,
                    "invoice_date": fields.Date.context_today(rec),
                    "manual_reason": "Rental charges %s (%s to %s)"
                    % (rec.name, rec.date_from, rec.date_to),
                    "line_ids": [
                        (
                            0,
                            0,
                            {
                                "description": "Equipment rental %s — %s to %s"
                                % (rec.name, rec.date_from, rec.date_to),
                                "taxable_amount": float(det.taxable_amount),
                                "vat_amount": float(det.vat_amount),
                                "line_total": float(det.line_total),
                            },
                        )
                    ],
                }
            )
            rec.mushak_6_3_id = invoice.id


class FixRentalDamage(models.Model):
    """Damage assessment line on a rental return."""

    _name = "fix.rental.damage"
    _description = "Rental Damage"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.dofa.mixin"]

    # A11 audit P2 (A05 area): the loss waiver's DOFA stamp used to be given
    # by whoever pressed Approve while holding the tier. It is now a routed
    # M63 request: the raiser asks (action_request_approval), the engine
    # routes to the holders of the tier the unrecovered loss derives (minus
    # the raiser and the amount-changer), and the stamp is given from the
    # approver's inbox only. The unrecovered loss is the approval amount, so
    # a recovery booked while the request is pending withdraws it.
    _approval_domain = "rental_loss_waiver"
    _approval_routed = True

    # A05 DOFA matrix — Rental Asset Damage Dispute Waiver: the unrecovered
    # loss a waiver writes off decides the tier (SC Manager -> Regional Ops
    # Head -> Head of Customer Service -> CEO).
    _DOFA_THRESHOLDS = [
        (50000.0, "tier_1"),
        (250000.0, "tier_2"),
        (1000000.0, "tier_3"),
        (float("inf"), "tier_4"),
    ]

    def _dofa_thresholds(self):
        return self._DOFA_THRESHOLDS

    def _dofa_amount(self) -> float:
        self.ensure_one()
        return max(
            (self.cost or 0.0) - (self.recovered_amount or 0.0) - (self.waived_amount or 0.0),
            0.0,
        )

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "BDT %.2f (unrecovered rental loss)" % self._dofa_amount()

    @api.depends("cost", "recovered_amount")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    reservation_id = fields.Many2one(
        "fix.rental.reservation", required=True, ondelete="cascade", index=True
    )
    category = fields.Selection(
        [
            ("cosmetic", "Cosmetic"),
            ("functional", "Functional"),
            ("lost", "Lost/Stolen"),
            ("accessory", "Accessory Missing"),
        ],
        required=True,
        default="cosmetic",
    )
    description = fields.Text(required=True)
    incident_date = fields.Date(
        string="Incident Date", help="When the damage was discovered (post-return inspection)"
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    cost = fields.Monetary(string="Damage Cost", currency_field="currency_id", required=True)
    estimated_repair_hours = fields.Float(
        string="Estimated Repair Hours", help="Workshop hours to restore (drives M01 routing)"
    )
    service_order_id = fields.Many2one(
        "fix.service.order",
        string="Repair Order (M01)",
        ondelete="set null",
        help="Grade-D fleet damage routed to the workshop (integration spec 4.1)",
    )
    invoice_id = fields.Many2one(
        "fix.ar.invoice", string="Customer Invoice (M20)", ondelete="set null"
    )
    mushak_6_7_id = fields.Char(
        string="Mushak 6.7 Credit Note Ref",
        help="Credit note issued when an invoiced charge is walked back (VAT Act 2012)",
    )
    inspector_id = fields.Many2one("hr.employee", string="Inspector")
    evidence_url = fields.Char(string="Damage Evidence Link / S3 Ref")
    disputed = fields.Boolean(string="Disputed by Customer", default=False)
    dispute_reason = fields.Char(string="Dispute Reason")
    settlement_notes = fields.Text(string="Arbitration / Settlement Notes")
    settled = fields.Boolean(string="Recovered", default=False)
    recovered_amount = fields.Monetary(
        string="Recovered Amount", currency_field="currency_id", default=0.0
    )
    unrecovered_loss_amount = fields.Monetary(
        string="Unrecovered Loss",
        currency_field="currency_id",
        compute="_compute_unrecovered",
        store=True,
        help="Cost not recovered from the customer — the amount a waiver writes off",
    )
    waived = fields.Boolean(
        string="Waived (DOFA)",
        copy=False,
        help="The unrecovered loss was written off under a DOFA approval",
    )
    waived_amount = fields.Monetary(
        string="Waived Amount",
        currency_field="currency_id",
        copy=False,
        help="Snapshot of the unrecovered loss at waiver time — the approval's "
        "money at risk never moves after the fact",
    )

    @api.depends("cost", "recovered_amount", "waived_amount")
    def _compute_unrecovered(self):
        for rec in self:
            rec.unrecovered_loss_amount = max(
                (rec.cost or 0.0) - (rec.recovered_amount or 0.0) - (rec.waived_amount or 0.0),
                0.0,
            )

    @api.constrains("cost")
    def _check_cost(self):
        for rec in self:
            if rec.cost < 0:
                raise ValidationError("Damage cost cannot be negative")
            if rec.recovered_amount < 0:
                raise ValidationError("Recovered amount cannot be negative")
            if rec.recovered_amount + (rec.waived_amount or 0.0) > rec.cost:
                raise ValidationError(
                    "Recovered and waived amounts together cannot exceed the damage cost"
                )

    def action_waive(self):
        """Write off the unrecovered loss under DOFA. The tier is derived
        from the money at risk; the approver must hold it and must not be
        the person who raised the record (fix.dofa.mixin enforces both).
        The recovered amount is NOT touched — the waiver is its own line of
        evidence (waived_amount), so the approval's money at risk stays
        auditable after the write-off."""
        for rec in self:
            label = "damage on %s" % rec.reservation_id.name
            if rec.waived:
                raise UserError("%s is already waived" % label.capitalize())
            at_risk = rec._dofa_amount()
            if at_risk <= 0:
                raise UserError("Nothing to waive on %s: the damage is fully recovered" % label)
            rec._dofa_assert_approved("A rental-loss waiver")
            rec.write({"waived": True, "settled": True, "waived_amount": at_risk})

    def _approval_on_rejected(self, comment):
        """A11 audit P2: an inbox rejection of the waiver is evidence on the
        damage record — the loss stays recoverable."""
        for rec in self:
            rec.message_post(
                body="Loss-waiver approval rejected by %s: %s"
                % (rec.env.user.name, comment or "no comment recorded")
            )


class FixApprovalMatrixRentalDomains(models.Model):
    """A11 audit P2: lets a DoA matrix row target the routed rental
    write-off and loss-waiver approvals (SLA, escalation, policy) without
    touching any other DOFA approval."""

    _inherit = "fix.approval.matrix"

    decision_domain = fields.Selection(
        selection_add=[
            ("rental_asset_writeoff", "Rental Fleet Asset Write-Off"),
            ("rental_loss_waiver", "Rental Loss Waiver"),
        ],
        ondelete={"rental_asset_writeoff": "cascade", "rental_loss_waiver": "cascade"},
    )
