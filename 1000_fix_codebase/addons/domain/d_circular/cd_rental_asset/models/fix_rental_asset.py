# fix_rental_asset — M13: rental reservation, damage, deposit (P09-M03 / R07-M03).
#
# A05 workflow audit (2026-11-03), M13: every workflow and money field of the
# rental was writable by a plain user and every gate lived inside one action,
# so a clerk created a booking born 'active' on a unit already out (1,902
# overlapping pairs live), typed the agreement to 'signed', closed a rental
# with no settlement and raised the deposit after collection to refund ten
# times what was taken. Now:
#   * the workflow, money and evidence fields are guarded (fix.guarded.mixin):
#     only the transition methods write them;
#   * every state change runs _validate_transition from write(), so the
#     transition map and the evidence gates (signed agreement, condition
#     reports, damage approvals, posted deposit) hold on every path;
#   * availability (turnaround padding, SKU capacity) is a constraint on the
#     record, checked on create and on every move into an open state;
#   * the agreement is signed by the CUSTOMER with a one-time code sent to
#     their phone, and its terms freeze once it is sent;
#   * the settlement reads the posted deposit ledger, never an editable field;
#     the late fee is charged once; charges above the deposit go to M20.
from __future__ import annotations

import hashlib
import json
import re
from datetime import timedelta
from decimal import ROUND_HALF_UP, Decimal

from odoo import api, fields, models
from odoo.addons.cd_service_order.models import fix_otp_util
from odoo.addons.cd_tax_engine_bd.models import tax_logic
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

from . import rental_policy as policy

# Stamp Act 1899 Sch-I Art.5 (agreement) / Art.15 (bond): an executed rental
# agreement carrying a money deposit cites its adhesive stamp serial. A Smart
# NID is 10 digits, the legacy NID 13 or 17.
_STAMP_CERT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9\-/]{3,}$")
_NID_RE = re.compile(r"^\d{10}(\d{3}|\d{7})?$")

OPEN_STATES = ("reserved", "delivered", "active")
TRANSITIONS = {
    "draft": {"reserved", "cancelled"},
    "reserved": {"delivered", "cancelled"},
    "delivered": {"active"},
    "active": {"returned"},
    "returned": {"damage_assess"},
    "damage_assess": {"closed"},
    "closed": set(),
    "cancelled": set(),
}
# Written only by the transition methods (and the overdue cron).
_RES_GUARDED = frozenset(
    {
        "state",
        "agreement_state",
        "signed_at",
        "signature_ref",
        "agreement_sent_at",
        "agreement_terms_hash",
        "agreement_otp_digest",
        "agreement_otp_expires_at",
        "agreement_otp_attempts",
        "deposit_refunded",
        "excess_billed",
        "excess_invoice_id",
        "late_fee",
        "overdue_since",
        "actual_return_date",
        "mushak_6_3_id",
        "delivery_consignment_id",
        "return_consignment_id",
    }
)
# The agreement: what the customer signs. Frozen once it is sent for
# signature (reset it to draft to change a sent one; a signed one is final).
_AGREEMENT_TERMS = frozenset(
    {
        "customer_id",
        "contract_id",
        "rental_sku_id",
        "rental_asset_id",
        "device_id",
        "kit_id",
        "date_from",
        "date_to",
        "daily_rate",
        "weekly_rate",
        "monthly_rate",
        "deposit_collected",
        "liability_cap_amount",
        "special_terms",
        "stamp_duty_cert_no",
        "deposit_bond_ref",
        "signer_mobile",
        "currency_id",
        "ifrs16_classification",
    }
)
# Set when the booking is made; after the reservation only a missing fleet
# unit may still be assigned (an SKU-pool booking gets its unit before handover).
_SET_AT_BOOKING = frozenset(
    {"customer_id", "rental_sku_id", "device_id", "kit_id", "deposit_collected", "company_id"}
)
_FREEZE_EXEMPT_PREFIX = ("message_", "activity_", "website_message")


def _refuse(model, message):
    # A ValidationError is a UserError: callers catching either see it.
    raise ValidationError(message)


class FixRentalReservation(models.Model):
    """Journey 8: reserve -> deliver -> active -> return -> damage_assess
    -> closed (or draft/reserved -> cancelled). Availability is a constraint
    on the record. Composes M37 rental SKUs, M03 logistics, M39 subscription
    billing, and M01 service order loaner intake (FR-SRM-063/064).

    Settlement (Gate G6-4): deposit_deduction from the posted ledger,
    deposit_refunded = collected - deducted, excess_billed to M20."""

    _name = "fix.rental.reservation"
    _description = "Rental Reservation"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
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
    actual_return_date = fields.Date(string="Actual Return Date", readonly=True, copy=False)
    duration_days = fields.Integer(
        compute="_compute_duration", store=True, string="Duration (Days)"
    )

    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    deposit_collected = fields.Monetary(
        string="Deposit Collected",
        currency_field="currency_id",
        help="The security deposit agreed and taken at reservation. Fixed once the "
        "booking is made: what was actually collected is the deposit ledger.",
    )
    deposit_refunded = fields.Monetary(
        string="Deposit Refunded",
        currency_field="currency_id",
        readonly=True,
        copy=False,
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
    late_fee = fields.Monetary(
        string="Late Return Fee",
        currency_field="currency_id",
        default=0.0,
        readonly=True,
        copy=False,
        help="Computed from the dates (grace period, multiplier: system parameters) by "
        "the return and the overdue job. Charged once: on the Mushak 6.3 or from the "
        "deposit, per cd_rental_asset.late_fee_settlement.",
    )
    excess_billed = fields.Monetary(
        string="Excess Damage Billed",
        currency_field="currency_id",
        readonly=True,
        copy=False,
        help="Charges exceeding deposit amount invoiced via M20",
    )
    excess_invoice_id = fields.Many2one(
        "fix.ar.invoice",
        string="Excess Charges Invoice (M20)",
        readonly=True,
        copy=False,
        ondelete="restrict",
        help="The M20 invoice raised at close for charges above the deposit",
    )
    overdue_since = fields.Date(
        string="Overdue Since",
        readonly=True,
        copy=False,
        help="First day past the due date plus grace, set by the overdue job",
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
        readonly=True,
        copy=False,
    )
    damage_ids = fields.One2many("fix.rental.damage", "reservation_id", string="Damage Records")
    damage_total = fields.Monetary(
        compute="_compute_damage", string="Damage Total", currency_field="currency_id"
    )
    condition_ids = fields.One2many(
        "fix.rental.condition", "reservation_id", string="Condition Reports"
    )
    deposit_ids = fields.One2many("fix.rental.deposit", "reservation_id", string="Deposit Ledger")

    delivery_consignment_id = fields.Many2one(
        "fix.consignment",
        string="Outbound Delivery Consignment (M03)",
        ondelete="set null",
        readonly=True,
        copy=False,
    )
    return_consignment_id = fields.Many2one(
        "fix.consignment",
        string="Return Consignment (M03)",
        ondelete="set null",
        readonly=True,
        copy=False,
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
        readonly=True,
        copy=False,
    )
    signed_at = fields.Datetime(string="Signed At", readonly=True, copy=False)
    signature_ref = fields.Char(
        string="Signature Reference",
        readonly=True,
        copy=False,
        help="System evidence token of the customer's one-time-code signature: the "
        "signer's masked mobile and a digest of the terms they signed.",
    )
    agreement_sent_at = fields.Datetime(readonly=True, copy=False)
    agreement_terms_hash = fields.Char(
        string="Signed Terms Digest",
        readonly=True,
        copy=False,
        help="SHA-256 of the commercial terms sent for signature",
    )
    agreement_otp_digest = fields.Char(readonly=True, copy=False, groups="base.group_system")
    agreement_otp_expires_at = fields.Datetime(readonly=True, copy=False)
    agreement_otp_attempts = fields.Integer(readonly=True, copy=False)

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
        help="The customer's mobile the signing code is sent to (else the customer's own)",
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
        readonly=True,
        copy=False,
        help="The M20 VAT invoice issued for the rental charges",
    )
    # ---- IFRS 16 lessor data (A05 P2) -----------------------------------------
    ifrs16_classification = fields.Selection(
        [("operating", "Operating Lease"), ("finance", "Finance Lease")],
        string="IFRS 16 Lessor Classification",
        default="operating",
        required=True,
        help="IFRS 16.61-66: a short equipment rental that does not transfer the "
        "asset's risks and rewards is an operating lease (income straight-line).",
    )
    lease_income_per_day = fields.Monetary(
        string="Lease Income per Day (IFRS 16.81)",
        currency_field="currency_id",
        compute="_compute_lease_income",
        help="Straight-line operating-lease income: rental fee ÷ rental days",
    )

    # ---- workspace step inputs (M13 capture audit, 2026-11-13) --------------
    # Not stored: they carry what the counter or support desk types to the
    # workflow method that records it (action_reserve, action_report_fault).
    # The deposit ledger row and the rental's history are the records.
    deposit_method = fields.Selection(
        [
            ("cash", "Cash"),
            ("bkash", "bKash"),
            ("nagad", "Nagad"),
            ("card", "Card / SSLCOMMERZ"),
            ("bank", "Bank Transfer"),
        ],
        string="Deposit Taken By",
        store=False,
    )
    deposit_reference = fields.Char(string="MFS / Bank / Receipt Reference", store=False)
    fault_report = fields.Text(string="Fault Reported", store=False)

    # ------------------------------------------------------------------
    # computes
    # ------------------------------------------------------------------
    @api.depends("date_from", "date_to")
    def _compute_duration(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                days = (rec.date_to - rec.date_from).days + 1
                rec.duration_days = max(days, 1)
            else:
                rec.duration_days = 1

    @api.depends("rental_charge", "duration_days")
    def _compute_lease_income(self):
        for rec in self:
            rec.lease_income_per_day = (rec.rental_charge or 0.0) / max(rec.duration_days or 1, 1)

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

    # ------------------------------------------------------------------
    # the guard: guarded fields, frozen terms, frozen closed rentals
    # ------------------------------------------------------------------
    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | _RES_GUARDED

    def _fix_guard_refuse(self, names):
        try:
            super()._fix_guard_refuse(names)
        except UserError as exc:
            _refuse(self, str(exc))

    def _frozen_fields(self) -> set:
        """Fields this record no longer accepts a change to (beyond the guard)."""
        self.ensure_one()
        if self.state in ("closed", "cancelled"):
            return {
                name
                for name, field in self._fields.items()
                if field.store and not name.startswith(_FREEZE_EXEMPT_PREFIX)
            }
        frozen = set()
        if self.agreement_state in ("sent", "signed"):
            frozen |= _AGREEMENT_TERMS
        if self.state != "draft":
            frozen |= _SET_AT_BOOKING
            if self.rental_asset_id or self.state != "reserved":
                frozen.add("rental_asset_id")
        return frozen

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        for rec in self:
            locked |= rec._frozen_fields()
        return locked

    def _fix_refuse_frozen(self, vals):
        for rec in self:
            frozen = rec._frozen_fields() & set(vals)
            changed = [n for n in frozen if rec._fix_guard_differs(n, vals[n], rec[n])]
            if not changed:
                continue
            labels = ", ".join(sorted(self._fields[n].string or n for n in changed))
            if rec.state in ("closed", "cancelled"):
                why = "the rental is %s and its record is final" % rec.state
            elif rec.agreement_state in ("sent", "signed") and set(changed) & _AGREEMENT_TERMS:
                why = (
                    "they are terms of the agreement the customer %s; reset the "
                    "agreement to draft (if not yet signed) to change them"
                    % ("signed" if rec.agreement_state == "signed" else "was sent to sign")
                )
            else:
                why = "they are fixed once the booking is made"
            _refuse(self, "Rental %s: %s cannot change: %s." % (rec.name, labels, why))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.rental.reservation") or "RENT/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            # The guard first: a forged state is refused as a forgery, not as
            # a bad transition.
            guarded = self._fix_guarded_fields() & set(vals)
            changed = {
                n for rec in self for n in guarded if rec._fix_guard_differs(n, vals[n], rec[n])
            }
            if changed:
                self._fix_guard_refuse(changed)
            self._fix_refuse_frozen(vals)
        if "state" in vals and (not self.env.su or self._fix_guard_has_token()):
            # Every transition a user can reach runs the map and its gates;
            # a superuser's raw write (data repair, fixtures) is trusted.
            for rec in self:
                rec._validate_transition(vals["state"])
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            live = self.filtered(lambda r: r.state != "draft" or r.deposit_ids)
            if live:
                _refuse(
                    self,
                    "Rental %s has left draft or carries deposit movements; cancel it "
                    "instead of deleting it." % live[0].name,
                )
        return super().unlink()

    # ------------------------------------------------------------------
    # availability: a constraint, so every path (create born 'active',
    # write(state), a moved date or unit) runs it
    # ------------------------------------------------------------------
    @api.constrains(
        "state", "date_from", "date_to", "rental_asset_id", "device_id", "rental_sku_id"
    )
    def _check_availability(self):
        """One unit, one customer per period - blocking, not advisory.

        A fleet asset is also blocked for the turnaround padding after each
        booking; an SKU-pool booking (no unit yet) may not exceed the SKU's
        rentable fleet. Searched as superuser: an overlapping booking in
        another operating unit still occupies the unit."""
        self.filtered(lambda r: r.state in OPEN_STATES)._assert_available()

    def _assert_available(self):
        """Raise unless each booking may hold its unit for its window (as if
        it were open: the gates call it before the state moves)."""
        pad = timedelta(days=policy.param_int(self.env, "turnaround_padding_days", 1))
        Res = self.sudo()
        for rec in self:
            if not (rec.date_from and rec.date_to):
                continue
            if rec.date_to < rec.date_from:
                _refuse(self, "Rental window is inverted")
            if rec.device_id:
                overlaps = Res.search_count(
                    [
                        ("device_id", "=", rec.device_id.id),
                        ("state", "in", OPEN_STATES),
                        ("date_from", "<=", rec.date_to),
                        ("date_to", ">=", rec.date_from),
                        ("id", "!=", rec.id),
                    ]
                )
                if overlaps:
                    _refuse(
                        self,
                        "Rental asset %s is already reserved for the overlapping period — "
                        "availability is blocking, not advisory" % rec.device_id.display_name,
                    )
            if rec.rental_asset_id:
                asset_overlaps = Res.search_count(
                    [
                        ("rental_asset_id", "=", rec.rental_asset_id.id),
                        ("state", "in", OPEN_STATES),
                        ("date_from", "<=", rec.date_to + pad),
                        ("date_to", ">=", rec.date_from - pad),
                        ("id", "!=", rec.id),
                    ]
                )
                if asset_overlaps:
                    _refuse(
                        self,
                        "Fleet asset %s is already reserved for the overlapping period "
                        "(including %d turnaround day(s)) — availability is blocking, "
                        "not advisory" % (rec.rental_asset_id.name, pad.days),
                    )
            if rec.rental_sku_id and not rec.device_id:
                capacity = (
                    self.env["fix.rental.asset"]
                    .sudo()
                    .search_count(
                        [
                            ("rental_sku_id", "=", rec.rental_sku_id.id),
                            ("status", "not in", ("retired", "lost")),
                        ]
                    )
                )
                demand = (
                    Res.search_count(
                        [
                            ("rental_sku_id", "=", rec.rental_sku_id.id),
                            ("device_id", "=", False),
                            ("state", "in", OPEN_STATES),
                            ("date_from", "<=", rec.date_to + pad),
                            ("date_to", ">=", rec.date_from - pad),
                            ("id", "!=", rec.id),
                        ]
                    )
                    + 1
                )
                if demand > capacity:
                    _refuse(
                        self,
                        "Rental SKU %s has %d rentable fleet unit(s) and %d overlapping "
                        "booking(s) — the pool is fully booked for this period"
                        % (rec.rental_sku_id.display_name, capacity, demand),
                    )

    # ------------------------------------------------------------------
    # transitions and their gates
    # ------------------------------------------------------------------
    def _validate_transition(self, new_state):
        self.ensure_one()
        old = self.state
        if new_state == old:
            return
        allowed = TRANSITIONS.get(old, set())
        if new_state not in allowed:
            _refuse(
                self,
                "Invalid rental transition for %s: %s -> %s. Allowed from '%s': %s"
                % (self.name, old, new_state, old, ", ".join(sorted(allowed)) or "(final state)"),
            )
        gate = getattr(self, "_gate_%s" % new_state, None)
        if gate:
            gate()

    def _require_signed(self, step):
        if self.agreement_state != "signed":
            _refuse(
                self,
                "Rental %s cannot be %s: the customer has not signed the agreement "
                "(it is '%s'). Send it for signature and enter the customer's code."
                % (self.name, step, self.agreement_state),
            )

    def _return_inspection_required(self):
        return bool(
            policy.param_on(self.env, "require_return_inspection", True)
            or (self.rental_sku_id and self.rental_sku_id.requires_inspection_return)
        )

    def _require_condition_report(self, report_type, step):
        if not self.condition_ids.filtered(lambda c: c.report_type == report_type):
            label = dict(self.env["fix.rental.condition"]._fields["report_type"].selection)[
                report_type
            ]
            _refuse(
                self,
                "Rental %s cannot be %s without a %s condition report — the handover "
                "evidence of the unit's state." % (self.name, step, label.lower()),
            )

    def _unposted_collections(self):
        return self.deposit_ids.filtered(lambda d: d.kind == "collect" and d.gl_state != "posted")

    def _gate_reserved(self):
        if self.date_to < self.date_from:
            _refuse(self, "Rental window is inverted")
        self._assert_available()
        if not (self.rental_asset_id or self.device_id or self.rental_sku_id):
            _refuse(
                self,
                "Rental %s names no fleet asset, device or rental SKU: there is nothing "
                "to check availability against." % self.name,
            )
        asset = self.rental_asset_id
        if asset and asset.status in ("retired", "maintenance"):
            _refuse(
                self, "Fleet asset %s is %s and cannot be reserved" % (asset.name, asset.status)
            )
        sku = self.rental_sku_id
        if sku and sku.max_rental_days and self.duration_days > sku.max_rental_days:
            _refuse(
                self,
                "Rental SKU %s allows at most %d rental days; %s is %d days."
                % (sku.display_name, sku.max_rental_days, self.name, self.duration_days),
            )
        if policy.param_on(self.env, "enforce_sku_deposit", True):
            required = max(
                (sku.security_deposit or 0.0) if sku else 0.0,
                (self.kit_id.deposit or 0.0) if self.kit_id else 0.0,
            )
            if (self.deposit_collected or 0.0) + 0.005 < required:
                _refuse(
                    self,
                    "Rental %s carries a deposit of %.2f; the SKU/kit requires at least "
                    "%.2f (cd_rental_asset.enforce_sku_deposit)."
                    % (self.name, self.deposit_collected or 0.0, required),
                )

    def _gate_delivered(self):
        self._require_signed("handed over")
        if not (self.rental_asset_id or self.device_id):
            _refuse(
                self,
                "Rental %s has no fleet unit assigned: assign one before handover." % self.name,
            )
        asset = self.rental_asset_id
        if asset and asset.status not in ("available", "reserved"):
            _refuse(
                self, "Fleet asset %s is %s, not ready for handover." % (asset.name, asset.status)
            )
        self._require_condition_report("pre_delivery", "handed over")

    def _gate_active(self):
        self._require_signed("activated")

    def _gate_damage_assess(self):
        if self._return_inspection_required():
            self._require_condition_report("post_return", "assessed")

    def _gate_closed(self):
        self._require_signed("closed")
        if self._return_inspection_required():
            self._require_condition_report("post_return", "closed")
        disputed = self.damage_ids.filtered("disputed")
        if disputed:
            _refuse(
                self,
                "Rental %s is held: %d damage charge(s) are disputed by the customer. The "
                "dispute is resolved by the charge approval." % (self.name, len(disputed)),
            )
        if policy.param_on(self.env, "damage_charge_requires_approval", True):
            for dmg in self.damage_ids:
                denial = dmg._charge_denial()
                if denial:
                    _refuse(self, "Rental %s cannot be closed: %s" % (self.name, denial))
        unposted = self._unposted_collections()
        if unposted:
            _refuse(
                self,
                "Rental %s cannot be settled: deposit movement %s is not posted to the "
                "General Ledger (%s). Repost it first — a refund is paid only from money "
                "the ledger holds." % (self.name, unposted[0].name, unposted[0].gl_state),
            )

    def _gate_cancelled(self):
        unposted = self._unposted_collections()
        if unposted:
            _refuse(
                self,
                "Rental %s cannot be cancelled: deposit movement %s is not posted to the "
                "General Ledger (%s). Repost it first, so the refund returns money the "
                "ledger holds." % (self.name, unposted[0].name, unposted[0].gl_state),
            )

    # ------------------------------------------------------------------
    # lifecycle actions
    # ------------------------------------------------------------------
    def _ledger_balance(self):
        """Deposit held per the POSTED ledger: posted collections less every
        deduction, forfeit and queued/posted refund."""
        self.ensure_one()
        rows = self.deposit_ids
        collected = sum(r.amount for r in rows if r.kind == "collect" and r.gl_state == "posted")
        out = sum(r.amount for r in rows if r.kind in ("deduction", "forfeit", "refund"))
        return round(collected - out, 2)

    def _set_asset_status(self, status):
        for rec in self.filtered("rental_asset_id"):
            rec.rental_asset_id._guarded().write({"status": status})

    def action_reserve(self, method=None, reference=None):
        """Draft -> reserved; the deposit is taken and posted.

        `method` is the tender the counter took the deposit in (cash, bKash,
        Nagad, card, bank) and `reference` its MFS/bank/receipt reference:
        the tender decides the GL clearing account it is posted to and how
        M50 refunds it. Without one the deposit is cash, as before.

        Availability (the search_count of overlapping open bookings, the
        'already reserved' refusal — blocking, not advisory — the turnaround
        padding and the SKU capacity) is the _check_availability constraint:
        it runs here and on every other path into an open state."""
        method = method or "cash"
        tenders = dict(self.env["fix.rental.deposit"]._fields["method"].selection)
        if method not in tenders:
            raise UserError(
                "Unknown deposit tender %r: choose one of %s."
                % (method, ", ".join(tenders.values()))
            )
        reference = (reference or "").strip() or None
        for rec in self:
            if rec.state != "draft":
                raise UserError("Reserve from draft: %s is %s" % (rec.name, rec.state))
            if method != "cash" and rec.deposit_collected and not reference:
                raise UserError(
                    "Rental %s: a deposit taken by %s needs its transaction reference, so "
                    "treasury can match and later refund it." % (rec.name, tenders[method])
                )
            rec._guarded().write({"state": "reserved"})
            if rec.rental_asset_id.status == "available":
                rec._set_asset_status("reserved")
            self.env["fix.rental.deposit"]._post(
                rec,
                "collect",
                rec.deposit_collected,
                "Deposit collected on reservation",
                method=method,
                reference=reference,
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
        return True

    def action_report_fault(self, fault=None):
        """FR-RNT-027 (first step): a customer reports a fault on a unit that
        is out on rent. The report is written to the rental's history with
        who took it and when, and a to-do with the swap/support deadline
        (system parameter cd_rental_asset.swap_sla_hours, default 24) goes to
        whoever booked the rental. The swap itself is not modelled yet."""
        text = (fault or "").strip()
        if not text:
            raise UserError("Describe the fault the customer reported.")
        hours = policy.param_int(self.env, "swap_sla_hours", 24)
        for rec in self:
            if rec.state not in ("delivered", "active"):
                raise UserError(
                    "Rental %s is %s: a fault is reported on a unit that is out on rent."
                    % (rec.name, rec.state)
                )
            due = fields.Datetime.context_timestamp(
                rec, fields.Datetime.now() + timedelta(hours=hours)
            ).date()
            rec.message_post(
                body="Fault reported on %s by %s: %s"
                % (
                    rec.rental_asset_id.name or rec.device_id.display_name or "the unit",
                    self.env.user.name,
                    text,
                )
            )
            rec.activity_schedule(
                "mail.mail_activity_data_todo",
                date_deadline=due,
                summary="In-rental fault on %s: support or swap within %d h" % (rec.name, hours),
                note=text,
                user_id=rec.create_uid.id or self.env.uid,
            )
        return True

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
                rec._guarded().write({"delivery_consignment_id": consignment.id})
        return self.mapped("delivery_consignment_id")

    def action_deliver(self):
        """Reserved -> delivered: needs the customer's signed agreement, a unit
        and a pre-delivery condition report (gates in _validate_transition)."""
        for rec in self:
            if rec.state != "reserved":
                raise UserError("Deliver from reserved")
            rec._guarded().write({"state": "delivered"})
            rec._set_asset_status("out")
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
        return True

    def action_activate(self):
        for rec in self:
            if rec.state != "delivered":
                raise UserError("Activate from delivered: the unit must be handed over first")
            rec._guarded().write({"state": "active"})
            publish(
                self.env,
                "rental.activated",
                "fix.rental.reservation",
                rec.id,
                {"customer": rec.customer_id.name, "start_date": str(rec.date_from)},
            )
        return True

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
                rec._guarded().write({"return_consignment_id": consignment.id})
        return self.mapped("return_consignment_id")

    def _late_fee_on(self, on_date):
        """The late fee for a return on `on_date`: overdue days beyond the
        grace period at the multiplier x the daily rate. A single figure,
        recomputed (never accumulated), so it is charged once."""
        self.ensure_one()
        if not (self.date_to and on_date):
            return 0.0
        grace = policy.param_int(self.env, "late_fee_grace_days", 0)
        late_days = (on_date - self.date_to).days - grace
        if late_days <= 0:
            return 0.0
        daily = self.daily_rate or (self.rental_charge / max(self.duration_days, 1))
        multiplier = policy.param_float(self.env, "late_fee_multiplier", 1.5)
        return round(late_days * daily * multiplier, 2)

    def action_return(self):
        for rec in self:
            if rec.state != "active":
                raise UserError("Return from active")
            today = fields.Date.context_today(self)
            fee = rec._late_fee_on(today)
            rec._guarded().write(
                {"state": "returned", "actual_return_date": today, "late_fee": fee}
            )
            if rec.rental_asset_id:
                rec._set_asset_status("maintenance")
                self.env["fix.rental.turnaround"]._guarded().create(
                    {
                        "rental_asset_id": rec.rental_asset_id.id,
                        "reservation_id": rec.id,
                        "company_id": rec.company_id.id,
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
        return True

    def action_assess_damage(self):
        """Journey 8's damage step: condition inspection and damage quantification."""
        for rec in self:
            if rec.state != "returned":
                raise UserError("Assess damage from returned")
            rec._guarded().write({"state": "damage_assess"})
            publish(
                self.env,
                "rental.damage_assessed",
                "fix.rental.reservation",
                rec.id,
                {"damage_total": float(rec.damage_total)},
            )
        return True

    def action_close(self):
        """The deposit settlement & billing closure, from the POSTED ledger:
        held              = posted collections (never deposit_collected)
        charges           = approved damage (cost - waived) [+ late fee when
                            cd_rental_asset.late_fee_settlement = deposit]
        deposit_deduction = min(charges, held), one ledger row per damage line
        deposit_refunded  = held - deposit_deduction (queued to M50)
        excess_billed     = charges - deposit_deduction, invoiced through M20."""
        Ledger = self.env["fix.rental.deposit"]
        for rec in self:
            if rec.state != "damage_assess":
                raise UserError("Close from damage assessment")
            rec._guarded().write({"state": "closed"})
            held = rec._ledger_balance()
            remaining = held
            deduction = 0.0
            charges = 0.0
            for dmg in rec.damage_ids.sorted("id"):
                # M13 capture pass 2: what the line charges the customer, after a
                # loss waiver AND the elected damage waiver (FR-RNT-036)
                charge = dmg._chargeable()
                charges += charge
                take = min(charge, remaining)
                if take > 0:
                    Ledger._post(rec, "deduction", take, "Damage charge: %s" % dmg.description, dmg)
                    remaining -= take
                    deduction += take
            late = rec.late_fee if policy.late_fee_mode(self.env) == "deposit" else 0.0
            charges += late or 0.0
            take = min(late or 0.0, remaining)
            if take > 0:
                Ledger._post(rec, "deduction", take, "Late return fee")
                remaining -= take
                deduction += take
            refund = round(max(remaining, 0.0), 2)
            excess = round(max(charges - deduction, 0.0), 2)
            rec._guarded().write({"deposit_refunded": refund, "excess_billed": excess})
            Ledger._post(rec, "refund", refund, "Deposit balance refunded")
            if excess > 0:
                rec._hand_off_excess(excess)
            publish(
                self.env,
                "rental.closed",
                "fix.rental.reservation",
                rec.id,
                {
                    "rental_charge": float(rec.rental_charge),
                    "deposit_collected": float(held),
                    "damage_total": float(rec.damage_total),
                    "late_fee": float(rec.late_fee),
                    "deduction": float(deduction),
                    "refund": float(refund),
                    "excess_billed": float(excess),
                },
            )
        return True

    def action_cancel(self):
        """Draft/reserved -> cancelled: the unit is freed and the posted
        deposit refunded through M50, less the cancellation fee (system
        parameter cd_rental_asset.cancellation_fee_pct, default 0)."""
        Ledger = self.env["fix.rental.deposit"]
        for rec in self:
            if rec.state not in ("draft", "reserved"):
                raise UserError(
                    "Rental %s is %s: only a draft or reserved rental is cancelled; a "
                    "delivered one comes back through Return." % (rec.name, rec.state)
                )
            rec._guarded().write({"state": "cancelled"})
            asset = rec.rental_asset_id
            if asset and asset.status == "reserved":
                still = self.sudo().search_count(
                    [
                        ("rental_asset_id", "=", asset.id),
                        ("state", "in", OPEN_STATES),
                        ("id", "!=", rec.id),
                    ]
                )
                if not still:
                    rec._set_asset_status("available")
            held = rec._ledger_balance()
            pct = min(policy.param_float(self.env, "cancellation_fee_pct", 0.0), 100.0)
            fee = round(held * max(pct, 0.0) / 100.0, 2)
            if fee > 0:
                Ledger._post(rec, "forfeit", fee, "Cancellation fee (%.1f%%)" % pct)
            refund = round(held - fee, 2)
            rec._guarded().write({"deposit_refunded": max(refund, 0.0)})
            Ledger._post(rec, "refund", refund, "Deposit refunded on cancellation")
            rec.message_post(
                body="Rental cancelled; deposit refund %.2f queued, fee %.2f." % (refund, fee)
            )
        return True

    def _hand_off_excess(self, amount):
        """Charges above the deposit become an M20 invoice (draft): finance
        issues it. Damage compensation is not a VAT supply, so the line
        carries no VAT. Through M20's own manual-invoice service, as the
        system: a rental clerk holds no accounting rights."""
        self.ensure_one()
        Invoice = self.env["fix.ar.invoice"].sudo()
        ou = (
            self.operating_unit_id
            or (self.branch_id and self.branch_id.operating_unit_id)
            or self.env["operating.unit"]
            .sudo()
            .search([("company_id", "=", self.company_id.id)], limit=1)
        )
        invoice = Invoice.create_manual_invoice(
            {
                "company_id": self.company_id.id,
                "customer_id": self.customer_id.id,
                "branch_id": self.branch_id.id,
                "operating_unit_id": ou.id,
                "currency_id": self.currency_id.id,
                "invoice_date": fields.Date.context_today(self),
            },
            [
                {
                    "description": "Rental %s: charges above the security deposit "
                    "(damage compensation, outside the scope of VAT)" % self.name,
                    "taxable_amount": float(amount),
                    "vat_amount": 0.0,
                    "line_total": float(amount),
                }
            ],
            "Rental %s: charges above the deposit" % self.name,
        )
        self._guarded().write({"excess_invoice_id": invoice.id})
        self.damage_ids.filtered(lambda d: not d.invoice_id)._guarded().write(
            {"invoice_id": invoice.id}
        )
        self.message_post(
            body="Charges of %.2f above the deposit handed to M20 as draft invoice %s."
            % (amount, invoice.display_name)
        )
        return invoice

    # ------------------------------------------------------------------
    # the overdue job (A05 E12)
    # ------------------------------------------------------------------
    @api.model
    def cron_rental_overdue(self):
        """Daily: open rentals past their due date plus grace get their late
        fee accrued to date (recomputed, never added, so a re-run changes
        nothing) and, once, a chatter note and a to-do for the booker."""
        today = fields.Date.context_today(self)
        grace = policy.param_int(self.env, "late_fee_grace_days", 0)
        overdue = self.sudo().search(
            [
                ("state", "in", ("delivered", "active")),
                ("date_to", "<", today - timedelta(days=grace)),
            ]
        )
        for rec in overdue:
            vals = {}
            fee = rec._late_fee_on(today)
            if abs(fee - (rec.late_fee or 0.0)) > 0.005:
                vals["late_fee"] = fee
            first = not rec.overdue_since
            if first:
                vals["overdue_since"] = rec.date_to + timedelta(days=grace + 1)
            if vals:
                rec._guarded().write(vals)
            if first:
                rec.message_post(
                    body="Rental is overdue since %s; late fee accrued to date %.2f."
                    % (rec.overdue_since, rec.late_fee)
                )
                rec.activity_schedule(
                    "mail.mail_activity_data_todo",
                    summary="Overdue rental %s: recover the unit" % rec.name,
                    user_id=rec.create_uid.id or self.env.uid,
                )
        return len(overdue)

    # ------------------------------------------------------------------
    # Agreement execution (customer e-sign by one-time code + Stamp Act 1899)
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

    def _terms_digest(self):
        self.ensure_one()
        terms = {}
        for name in sorted(_AGREEMENT_TERMS):
            value = self[name]
            if isinstance(value, models.BaseModel):
                value = value.ids
            terms[name] = value if isinstance(value, int | float | list) else str(value or "")
        return hashlib.sha256(json.dumps(terms, sort_keys=True).encode()).hexdigest()

    def _signer_phone(self):
        self.ensure_one()
        typed = re.sub(r"\D", "", self.signer_mobile or "")
        if typed.startswith("880"):
            typed = typed[2:]
        if re.fullmatch(r"01[3-9]\d{8}", typed):
            return typed
        return fix_otp_util.bd_mobile(self.customer_id)

    def action_send_agreement(self):
        """Draft -> signature requested: a one-time code goes to the
        CUSTOMER's phone and the terms are pinned. The staff member never
        sees the code; the customer reads it back to sign."""
        for rec in self:
            if rec.state in ("closed", "cancelled"):
                raise UserError("Rental %s is %s." % (rec.name, rec.state))
            if rec.agreement_state not in ("draft", "declined"):
                raise UserError("Agreement can only be sent for signature from draft")
            if rec.deposit_collected and not (rec.stamp_duty_cert_no or "").strip():
                raise UserError(
                    "Rental %s: a deposit-holding agreement needs its stamp duty "
                    "certificate number before it is sent (Stamp Act 1899 Art.5/Art.15)" % rec.name
                )
            phone = rec._signer_phone()
            if not phone:
                raise UserError(
                    "Agreement sending needs the customer's Bangladesh mobile number: the "
                    "signing code is sent there."
                )
            code = fix_otp_util.issue_code()
            fix_otp_util.dispatch_otp(phone, code, fix_otp_util.OTP_TTL_SECONDS)
            now = fields.Datetime.now()
            rec.sudo()._guarded().write(
                {
                    "agreement_state": "sent",
                    "agreement_sent_at": now,
                    "agreement_terms_hash": rec._terms_digest(),
                    "agreement_otp_digest": fix_otp_util.digest(
                        self.env, "rental_agreement", rec.id, code
                    ),
                    "agreement_otp_expires_at": now
                    + timedelta(seconds=fix_otp_util.OTP_TTL_SECONDS),
                    "agreement_otp_attempts": 0,
                }
            )
            rec.message_post(
                body="Agreement sent for signature; code sent to %s." % fix_otp_util.mask(phone)
            )
        return True

    def action_sign_agreement(self, code=None, otp=None):
        """Signature requested -> signed, on the customer's code. A wrong
        code is counted and returned (a raise would roll the counter back);
        five misses burn it. The stamp-duty gate is a constraint too."""
        code = (code or otp or "").strip()
        result = {"verified": True}
        for rec in self:
            if rec.agreement_state != "sent":
                raise UserError("Agreement can only be signed after it was sent")
            if not code:
                raise UserError(
                    "Enter the code the customer received: the agreement is signed by "
                    "the customer, not by staff."
                )
            stored = rec.sudo().agreement_otp_digest
            if not stored or not rec.agreement_otp_expires_at:
                raise UserError("Send the agreement for signature again: no code is pending.")
            if fields.Datetime.now() > rec.agreement_otp_expires_at:
                raise UserError("The signing code has expired. Send the agreement again.")
            if rec._terms_digest() != rec.agreement_terms_hash:
                raise UserError("The terms changed after the agreement was sent. Send it again.")
            if not fix_otp_util.matches(self.env, "rental_agreement", rec.id, code, stored):
                attempts = rec.agreement_otp_attempts + 1
                burnt = attempts >= fix_otp_util.OTP_MAX_ATTEMPTS
                rec.sudo()._guarded().write(
                    {
                        "agreement_otp_attempts": attempts,
                        "agreement_otp_digest": False if burnt else stored,
                    }
                )
                rec.message_post(
                    body="Wrong signing code entered by %s (attempt %d)%s."
                    % (self.env.user.name, attempts, "; the code is burnt" if burnt else "")
                )
                result = {
                    "verified": False,
                    "error": "That signing code is not correct."
                    + (" Too many attempts: send the agreement again." if burnt else ""),
                }
                continue
            phone = rec._signer_phone()
            now = fields.Datetime.now()
            token = hashlib.sha256(
                ("%s|%s|%s|%s" % (rec.id, phone, rec.agreement_terms_hash, now)).encode()
            ).hexdigest()[:24]
            rec.sudo()._guarded().write(
                {
                    "agreement_state": "signed",
                    "signed_at": now,
                    "signature_ref": "OTP:%s:%s" % (fix_otp_util.mask(phone), token),
                    "agreement_otp_digest": False,
                }
            )
            rec.message_post(
                body="Agreement signed by the customer (code to %s)." % (fix_otp_util.mask(phone))
            )
        return result

    def action_reset_agreement(self):
        """A sent (not yet signed) or declined agreement back to draft, so its
        terms can be corrected and sent again. A signed agreement is final."""
        for rec in self:
            if rec.agreement_state not in ("sent", "declined"):
                raise UserError(
                    "Only a sent or declined agreement goes back to draft; a signed "
                    "agreement is final."
                )
            if rec.state in ("closed", "cancelled"):
                raise UserError("Rental %s is %s." % (rec.name, rec.state))
            rec.sudo()._guarded().write(
                {
                    "agreement_state": "draft",
                    "agreement_otp_digest": False,
                    "agreement_otp_expires_at": False,
                    "agreement_terms_hash": False,
                }
            )
        return True

    # ------------------------------------------------------------------
    # Mushak 6.3 — the rental charge invoice (M20 paper, M51 rates)
    # ------------------------------------------------------------------

    def action_issue_rental_invoice(self):
        """Issue the rental's Mushak 6.3 through M20: the rental charge, plus
        the late fee when it is billed on the invoice (late_fee_settlement =
        invoice, the default; otherwise it was taken from the deposit and is
        not invoiced again). Damage settled from the deposit is compensation
        against the customer's own money, never a VAT supply — it is NOT
        invoiced here (it posts to recovery income in the deposit ledger)."""
        Invoice = self.env["fix.ar.invoice"].sudo()
        late_on_invoice = policy.late_fee_mode(self.env) == "invoice"
        for rec in self:
            if rec.state in ("draft", "cancelled"):
                raise UserError("Rental %s is %s: nothing was rented." % (rec.name, rec.state))
            if rec.mushak_6_3_id or Invoice.search_count(
                [("source_model", "=", "fix.rental.reservation"), ("source_id", "=", rec.id)]
            ):
                raise UserError("Rental %s already carries its rental invoice" % rec.name)
            taxable = (rec.rental_charge or 0.0) + (
                (rec.late_fee or 0.0) if late_on_invoice else 0.0
            )
            if taxable <= 0:
                raise UserError(
                    "Rental %s has no taxable charge to invoice (rental fee + late fee)" % rec.name
                )
            # A08 M51-5: the rate comes from the statutory master, never from code
            determination = self.env["fix.vat.treatment"]._fix_determine_tax(
                [
                    tax_logic.TaxLine(
                        product_code="RENTAL",
                        qty=Decimal("1"),
                        unit_price=Decimal(str(taxable)).quantize(Decimal("0.01"), ROUND_HALF_UP),
                    )
                ],
                on_date=fields.Date.context_today(rec),
                company=rec.company_id,
            )
            det = determination.lines[0]
            lines = [
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
            ]
            # M13 capture pass 2 (FR-RNT-036/037): the elected damage waiver is
            # its own chargeable line, at the plan's % of the gross rental
            waiver_fee = getattr(rec, "waiver_fee", 0.0) or 0.0
            if waiver_fee > 0:
                wdet = (
                    self.env["fix.vat.treatment"]
                    ._fix_determine_tax(
                        [
                            tax_logic.TaxLine(
                                product_code="RENTAL",
                                qty=Decimal("1"),
                                unit_price=Decimal(str(waiver_fee)).quantize(
                                    Decimal("0.01"), ROUND_HALF_UP
                                ),
                            )
                        ],
                        on_date=fields.Date.context_today(rec),
                        company=rec.company_id,
                    )
                    .lines[0]
                )
                lines.append(
                    (
                        0,
                        0,
                        {
                            "description": "Damage waiver %s (%s)"
                            % (rec.waiver_plan_id.name, rec.name),
                            "taxable_amount": float(wdet.taxable_amount),
                            "vat_amount": float(wdet.vat_amount),
                            "line_total": float(wdet.line_total),
                        },
                    )
                )
            invoice = Invoice.create(
                {
                    "company_id": rec.company_id.id,
                    "customer_id": rec.customer_id.id,
                    "branch_id": rec.branch_id.id,
                    "operating_unit_id": (
                        rec.operating_unit_id
                        or rec.branch_id.operating_unit_id
                        or self.env["operating.unit"]
                        .sudo()
                        .search([("company_id", "=", rec.company_id.id)], limit=1)
                    ).id,
                    "source_model": "fix.rental.reservation",
                    "source_id": rec.id,
                    "invoice_date": fields.Date.context_today(rec),
                    "manual_reason": "Rental charges %s (%s to %s)"
                    % (rec.name, rec.date_from, rec.date_to),
                    "line_ids": lines,
                }
            )
            rec._guarded().write({"mushak_6_3_id": invoice.id})
        return True


# Fields of a damage line written only by the settlement, the waiver and the
# charge approval.
_DMG_GUARDED = frozenset(
    {
        "waived",
        "waived_amount",
        "recovered_amount",
        "settled",
        "unrecovered_loss_amount",
        "invoice_id",
        "mushak_6_7_id",
        "charge_approval_id",
        "dispute_resolved_by_id",
        "dispute_resolved_at",
    }
)
# What may still be written on a damage line of a closed or cancelled rental.
_DMG_AFTER_CLOSE = frozenset({"dofa_justification", "settlement_notes"})


class FixRentalDamage(models.Model):
    """Damage assessment line on a rental return.

    Two approvals, both routed through M63 (A05 E5/E11):
      * the CHARGE against the customer (fix.rental.charge.approval), tiered
        on the cost charged, required before close; a disputed line holds the
        close until that approval resolves the dispute;
      * the WAIVER of an unrecovered loss (this record's own DOFA), tiered on
        cost - recovered (from the deposit ledger) - waived."""

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

    @api.depends("cost", "recovered_amount", "waived_amount")
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
        "fix.ar.invoice",
        string="Customer Invoice (M20)",
        ondelete="set null",
        readonly=True,
        copy=False,
    )
    mushak_6_7_id = fields.Char(
        string="Mushak 6.7 Credit Note Ref",
        readonly=True,
        copy=False,
        help="Credit note issued when an invoiced charge is walked back (VAT Act 2012)",
    )
    inspector_id = fields.Many2one("hr.employee", string="Inspector")
    evidence_url = fields.Char(string="Damage Evidence Link / S3 Ref")
    disputed = fields.Boolean(
        string="Disputed by Customer",
        default=False,
        help="A customer's dispute holds the close. Raising it is open to staff; it is "
        "cleared only by the approval of the charge.",
    )
    dispute_reason = fields.Char(string="Dispute Reason")
    dispute_resolved_by_id = fields.Many2one(
        "res.users", string="Dispute Resolved By", readonly=True, copy=False
    )
    dispute_resolved_at = fields.Datetime(readonly=True, copy=False)
    settlement_notes = fields.Text(string="Arbitration / Settlement Notes")
    deposit_ids = fields.One2many("fix.rental.deposit", "damage_id", string="Deposit Recoveries")
    recovered_amount = fields.Monetary(
        string="Recovered Amount",
        currency_field="currency_id",
        compute="_compute_recovered",
        store=True,
        help="Recovered from the customer's deposit: the deduction movements of the "
        "deposit ledger linked to this line. Never typed.",
    )
    settled = fields.Boolean(
        string="Recovered",
        compute="_compute_unrecovered",
        store=True,
        help="Nothing left unrecovered: recovered from the deposit or waived under DOFA",
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
        readonly=True,
        help="The unrecovered loss was written off under a DOFA approval",
    )
    waived_amount = fields.Monetary(
        string="Waived Amount",
        currency_field="currency_id",
        copy=False,
        readonly=True,
        help="Snapshot of the unrecovered loss at waiver time — the approval's "
        "money at risk never moves after the fact",
    )
    charge_approval_id = fields.Many2one(
        "fix.rental.charge.approval",
        string="Charge Approval",
        readonly=True,
        copy=False,
        ondelete="set null",
    )
    charge_approval_state = fields.Selection(
        related="charge_approval_id.approval_state", string="Charge Approval State"
    )

    @api.depends("deposit_ids.amount", "deposit_ids.kind")
    def _compute_recovered(self):
        for rec in self:
            rec.recovered_amount = sum(
                d.amount for d in rec.deposit_ids if d.kind in ("deduction", "forfeit")
            )

    @api.depends("cost", "recovered_amount", "waived_amount")
    def _compute_unrecovered(self):
        for rec in self:
            rec.unrecovered_loss_amount = max(
                (rec.cost or 0.0) - (rec.recovered_amount or 0.0) - (rec.waived_amount or 0.0),
                0.0,
            )
            rec.settled = rec.unrecovered_loss_amount <= 0.005

    @api.constrains("cost")
    def _check_cost(self):
        for rec in self:
            if rec.cost < 0:
                raise ValidationError("Damage cost cannot be negative")
            if rec.recovered_amount < 0:
                raise ValidationError("Recovered amount cannot be negative")
            if rec.recovered_amount + (rec.waived_amount or 0.0) > rec.cost + 0.005:
                raise ValidationError(
                    "Recovered and waived amounts together cannot exceed the damage cost"
                )

    # ---- guard ---------------------------------------------------------
    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | _DMG_GUARDED

    def _fix_guard_refuse(self, names):
        try:
            super()._fix_guard_refuse(names)
        except UserError as exc:
            _refuse(self, str(exc))

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self:
            locked.add("reservation_id")
            if any(r.disputed for r in self):
                locked.add("disputed")
            if any(r.reservation_id.state in ("closed", "cancelled") for r in self):
                locked |= {
                    n
                    for n, f in self._fields.items()
                    if f.store and n not in _DMG_AFTER_CLOSE and not n.startswith("message_")
                }
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            Res = self.env["fix.rental.reservation"]
            for vals in vals_list:
                res = Res.browse(vals.get("reservation_id")).exists()
                if res and res.state not in ("returned", "damage_assess"):
                    _refuse(
                        self,
                        "Damage is assessed on a returned unit: rental %s is %s."
                        % (res.name, res.state),
                    )
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self:
                if "reservation_id" in vals and rec._fix_guard_differs(
                    "reservation_id", vals["reservation_id"], rec.reservation_id
                ):
                    _refuse(self, "A damage line stays on the rental it was assessed on.")
                if "disputed" in vals and rec.disputed and not vals["disputed"]:
                    _refuse(
                        self,
                        "The customer's dispute on %s is resolved by the approval of the "
                        "charge (Request Charge Approval), not by unticking it."
                        % rec.reservation_id.name,
                    )
                if rec.reservation_id.state in ("closed", "cancelled"):
                    changed = [
                        n
                        for n in set(vals) - _DMG_AFTER_CLOSE
                        if n in self._fields
                        and self._fields[n].store
                        and not n.startswith("message_")
                        and rec._fix_guard_differs(n, vals[n], rec[n])
                    ]
                    if changed:
                        _refuse(
                            self,
                            "Rental %s is %s: its damage record (%s) is final."
                            % (
                                rec.reservation_id.name,
                                rec.reservation_id.state,
                                ", ".join(sorted(changed)),
                            ),
                        )
        before = {rec.id: (rec.cost, rec.disputed) for rec in self}
        result = super().write(vals)
        for rec in self:
            cost, disputed = before[rec.id]
            moved = abs((rec.cost or 0.0) - (cost or 0.0)) > 0.005
            raised = rec.disputed and not disputed
            if (moved or raised) and rec.charge_approval_id:
                rec._void_charge_approval(
                    "the damage cost changed" if moved else "the customer disputed the charge"
                )
        return result

    # ---- the charge approval ----------------------------------------------
    def _chargeable(self):
        self.ensure_one()
        return round(max((self.cost or 0.0) - (self.waived_amount or 0.0), 0.0), 2)

    def _charge_denial(self):
        """'' when the charge this line puts on the customer is approved."""
        self.ensure_one()
        charge = self._chargeable()
        if charge <= 0:
            return ""
        approval = self.charge_approval_id
        label = "the damage charge of %.2f (%s)" % (charge, (self.description or "")[:40])
        if not approval or approval.approval_state != "approved" or not approval.dofa_approved:
            return (
                "%s has no granted charge approval — request it; the approver decides it " % (label)
                + "from the M63 inbox."
            )
        if abs(approval.amount - charge) > 0.005:
            return "%s differs from the %.2f that was approved; request it again." % (
                label,
                approval.amount,
            )
        try:
            approval._dofa_assert_approved("The damage charge")
        except UserError as exc:
            return str(exc)
        return ""

    def _void_charge_approval(self, reason):
        for rec in self.filtered("charge_approval_id"):
            approval = rec.charge_approval_id.sudo()
            if approval.approval_state in ("pending", "approved") or approval.dofa_approved:
                approval._approval_void(reason)
            rec.message_post(body="Charge approval withdrawn: %s." % reason)

    def action_request_charge_approval(self, justification=None):
        """Route the charge against the customer to the DOFA holder of its
        tier (M63). The inspector who assessed it, the requester and whoever
        last moved the amount never decide it."""
        Approval = self.env["fix.rental.charge.approval"]
        for rec in self:
            if rec.reservation_id.state not in ("returned", "damage_assess"):
                raise UserError(
                    "A damage charge is approved during damage assessment (rental %s is %s)."
                    % (rec.reservation_id.name, rec.reservation_id.state)
                )
            charge = rec._chargeable()
            if charge <= 0:
                raise UserError("Nothing to approve: the damage line charges nothing.")
            current = rec.charge_approval_id
            if (
                current
                and current.approval_state in ("pending", "approved")
                and abs(current.amount - charge) <= 0.005
            ):
                raise UserError(
                    "The charge on %s is already %s."
                    % (rec.reservation_id.name, current.approval_state)
                )
            if current:
                rec._void_charge_approval("a new charge approval was requested")
            # the guard token stays on the create: the request is raised clean
            approval = Approval.browse(
                Approval._guarded()
                .create(
                    {"damage_id": rec.id, "amount": charge, "dofa_justification": justification}
                )
                .id
            )
            rec._guarded().write({"charge_approval_id": approval.id})
            approval.action_request_approval(justification=justification)
        return True

    def action_recall_charge_approval(self):
        for rec in self:
            if not rec.charge_approval_id:
                raise UserError("No charge approval to recall.")
            rec.charge_approval_id.action_recall_approval()
        return True

    def action_raise_dispute(self, reason=None):
        """Record the customer's dispute: the close is held, and any charge
        approval is withdrawn (the approver decides the disputed charge)."""
        for rec in self:
            if rec.reservation_id.state in ("closed", "cancelled"):
                raise UserError(
                    "Rental %s is %s." % (rec.reservation_id.name, rec.reservation_id.state)
                )
            vals = {"disputed": True}
            if reason:
                vals["dispute_reason"] = reason
            rec.write(vals)
        return True

    def _on_charge_approved(self, approver):
        """Called by the granted charge approval: a disputed charge is
        resolved by that decision."""
        for rec in self.filtered("disputed"):
            rec._guarded().write(
                {
                    "disputed": False,
                    "dispute_resolved_by_id": approver.id,
                    "dispute_resolved_at": fields.Datetime.now(),
                }
            )
            rec.message_post(
                body="Dispute resolved by the approval of the charge (%s)." % approver.name
            )

    # ---- the waiver ----------------------------------------------------
    def action_waive(self):
        """Write off the unrecovered loss under DOFA. The tier is derived
        from the money at risk (cost less what the deposit ledger recovered
        and what was waived); the approval is routed through M63 and must
        not be the creator's. The recovered amount is NOT touched — the
        waiver is its own line of evidence (waived_amount)."""
        for rec in self:
            label = "damage on %s" % rec.reservation_id.name
            if rec.waived:
                raise UserError("%s is already waived" % label.capitalize())
            if rec.invoice_id:
                raise UserError(
                    "The loss on %s was invoiced to the customer (%s): walk it back with an "
                    "M20 credit note (Mushak 6.7), not a waiver."
                    % (label, rec.invoice_id.display_name)
                )
            at_risk = rec._dofa_amount()
            if at_risk <= 0:
                raise UserError("Nothing to waive on %s: the damage is fully recovered" % label)
            rec._dofa_assert_approved("A rental-loss waiver")
            rec._guarded().write({"waived": True, "settled": True, "waived_amount": at_risk})

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
