# fix_rental_money — A05 remediation (2026-11-20, stream S1): the rental's
# order-to-cash as cumulative billing, the deposit by value and risk, and the
# controls around both.
#
#   FIN-07 / M13-02/03/04  Billable = rental (cheapest ladder, persisted) +
#                          waiver + late fee; what is not yet invoiced is raised
#                          as a supplementary M20 invoice keyed per event
#                          (extension, return, manual issue); close is refused
#                          while billable > invoiced. An early return or a
#                          cancellation cancels a draft invoice or requests a
#                          Mushak 6.7 credit note against an issued one.
#   FIN-08 / M13-10        Cancel credits / cancels the rental invoice.
#   FIN-17 / M13-08        Rental lines credit the rental income account
#                          (400108), damage and loss the recovery account
#                          (400111) - accounts from parameters (owner D1).
#   FIN-18 / M13-09        Late and cancellation fees are M51 VAT supplies
#                          (owner D2); only genuine damage compensation is
#                          outside VAT, through a configured M51 treatment.
#   M13-19 / D8            Deposit = max(SKU/kit floor, book value x risk-tier
#                          rate); a lower deposit needs a Finance Manager's
#                          routed approval with a reason (BRU-RNT-07).
#   XC-22                  The person who took the deposit does not release it.
#   M13-20                 Hold expiry, the category minimum grade, and a row
#                          lock on the unit/SKU/device when availability is
#                          decided.
#   M13-26 / I5            rental.overdue at 1/3/7 days, rental.return_due.
#   BRU-RNT-18 / M13-29    Rentals of 12 months or more need an M53 assessment
#                          reference before activation; the IFRS 16
#                          classification is recorded by Finance, not typed.
#
# Service period for M20 deferral (stream S4): every invoice raised here has
# source_model 'fix.rental.billing'; the billing row carries the period it
# bills in service_date_from / service_date_to.
from __future__ import annotations

from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

from . import rental_policy as policy
from .rental_gl import posting_operating_unit, rental_account

FINANCE_GROUP = "cd_rental_asset.group_rental_finance"
FINANCE_MANAGER_GROUP = "account.group_account_manager"
RENTAL_FAMILY = ("rental", "credit")
COMPONENTS = ("rental_amount", "waiver_amount", "late_fee_amount")
COMPONENT_LABEL = {
    "rental_amount": "Equipment rental",
    "waiver_amount": "Damage waiver",
    "late_fee_amount": "Late return fee",
}


def _refuse(message):
    raise ValidationError(message)


def is_rental_finance(user):
    return bool(
        user.has_group(FINANCE_GROUP)
        or user.has_group(FINANCE_MANAGER_GROUP)
        or user.has_group("base.group_system")
    )


def _vat_code(env, company, kind):
    """The M51 tariff code a billing line carries, or None for M51's own
    determination (the standard rate in force). Damage and loss are
    compensation outside VAT (owner D2): they need a configured exempt or
    zero-rated treatment and are refused without one."""
    Treatment = env["fix.vat.treatment"].sudo()
    if kind in ("damage", "loss"):
        param = policy.PREFIX + "vat_treatment_code.damage"
        code = (env["ir.config_parameter"].sudo().get_param(param) or "").strip()
        if not code:
            raise UserError(
                "Damage / loss compensation cannot be invoiced: system parameter %s (the M51 "
                "tariff code of compensation outside VAT, owner decision D2) is not set." % param
            )
        row = Treatment._fix_treatment_for(code, company)
        if not row:
            raise UserError(
                "System parameter %s names M51 treatment %s, which is not active in company %s."
                % (param, code, company.name)
            )
        if row.treatment_type not in ("exempt", "zero_rated"):
            raise UserError(
                "M51 treatment %s is %s: damage compensation is outside VAT (owner decision "
                "D2), so its treatment must be exempt or zero-rated." % (code, row.treatment_type)
            )
        return code
    code = (
        env["ir.config_parameter"].sudo().get_param(policy.PREFIX + "vat_treatment_code.rental")
        or ""
    ).strip()
    if code:
        if not Treatment._fix_treatment_for(code, company):
            raise UserError("M51 treatment %s (rental lines) is not active." % code)
        return code
    return "RENTAL" if Treatment._fix_treatment_for("RENTAL", company) else None


class FixRentalBilling(models.Model):
    """One chargeable event of a rental handed to M20 as an invoice (or a
    credit). The invoice source: one invoice per row, keyed per event, so a
    second invoice for the same rental is a supplementary one and never
    collides with the first."""

    _name = "fix.rental.billing"
    _description = "Rental Billing Event"
    _inherit = ["fix.guarded.mixin"]
    _order = "reservation_id, id"
    # stream S4 (FIN-14 / M13-17): the rental hire is earned over its period;
    # M20 defers the lines that carry service_period_start / _end
    _fix_defer_revenue = True

    name = fields.Char(required=True, readonly=True)
    reservation_id = fields.Many2one(
        "fix.rental.reservation", required=True, index=True, ondelete="restrict", readonly=True
    )
    company_id = fields.Many2one(related="reservation_id.company_id", store=True, index=True)
    customer_id = fields.Many2one(related="reservation_id.customer_id", store=True)
    currency_id = fields.Many2one(related="reservation_id.currency_id")
    operating_unit_id = fields.Many2one("operating.unit", readonly=True, index=True)
    branch_id = fields.Many2one("fix.branch", readonly=True)
    kind = fields.Selection(
        [
            ("rental", "Rental Charges"),
            ("credit", "Rental Credit"),
            ("cancellation", "Cancellation Fee"),
            ("damage", "Damage above the Deposit"),
            ("loss", "Loss of the Unit"),
        ],
        required=True,
        readonly=True,
    )
    key = fields.Char(required=True, readonly=True, help="The event this row bills, per rental")
    extension_id = fields.Many2one("fix.rental.extension", readonly=True, ondelete="set null")
    service_date_from = fields.Date(
        readonly=True, help="First day of the service this row bills (M20 deferral, stream S4)"
    )
    service_date_to = fields.Date(
        readonly=True, help="Last day of the service this row bills (M20 deferral, stream S4)"
    )
    rental_amount = fields.Monetary(currency_field="currency_id", readonly=True)
    waiver_amount = fields.Monetary(currency_field="currency_id", readonly=True)
    late_fee_amount = fields.Monetary(currency_field="currency_id", readonly=True)
    fee_amount = fields.Monetary(
        string="Fee / Compensation", currency_field="currency_id", readonly=True
    )
    taxable_amount = fields.Monetary(currency_field="currency_id", readonly=True)
    invoice_id = fields.Many2one("fix.ar.invoice", readonly=True, ondelete="set null")
    credit_note_id = fields.Many2one("fix.credit.note", readonly=True, ondelete="set null")
    state = fields.Selection(
        [("invoiced", "Invoiced"), ("credit", "Credit Requested"), ("cancelled", "Cancelled")],
        default="invoiced",
        required=True,
        readonly=True,
    )

    _key_unique = models.Constraint(
        "UNIQUE (reservation_id, key)", "A rental bills each event once."
    )

    _BILLING_GUARDED = frozenset(
        {
            "name",
            "reservation_id",
            "operating_unit_id",
            "branch_id",
            "kind",
            "key",
            "extension_id",
            "service_date_from",
            "service_date_to",
            "rental_amount",
            "waiver_amount",
            "late_fee_amount",
            "fee_amount",
            "taxable_amount",
            "invoice_id",
            "credit_note_id",
            "state",
        }
    )

    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | self._BILLING_GUARDED

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            _refuse("A rental billing event is raised by the rental, never typed.")
        return super().create(vals_list)

    def unlink(self):
        if not self.env.su:
            _refuse("A rental billing event is evidence of what was billed: it is kept.")
        return super().unlink()

    def _effective(self):
        """Rows still counting towards what the customer was billed: not
        cancelled here, their invoice not cancelled in M20, their credit
        note not rejected."""
        return self.filtered(
            lambda r: r.state != "cancelled"
            and not (r.invoice_id and r.invoice_id.sudo().state == "cancelled")
            and not (r.credit_note_id and r.credit_note_id.sudo().state == "rejected")
        )


class FixRentalDepositReduction(models.Model):
    """BRU-RNT-07 / owner D8: a deposit below the computed one. A Finance
    Manager (Accounting Administrator) who did not ask decides it from the
    M63 inbox; the approval pins the booking, the computed deposit and the
    reduced one, and any change voids it."""

    _name = "fix.rental.deposit.reduction"
    _description = "Rental Deposit Reduction"
    _inherit = ["mail.thread", "fix.approvable.mixin"]
    _order = "id desc"

    _approval_domain = "rental_deposit_reduction"
    _approval_group = FINANCE_MANAGER_GROUP
    _approval_routed = True
    _approval_apply_method = "_reduction_approve"

    name = fields.Char(required=True, default="New", readonly=True, copy=False)
    reservation_id = fields.Many2one(
        "fix.rental.reservation",
        string="Booking",
        required=True,
        index=True,
        ondelete="cascade",
        domain=[("state", "=", "draft")],
    )
    company_id = fields.Many2one(related="reservation_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(related="reservation_id.operating_unit_id", store=True)
    customer_id = fields.Many2one(related="reservation_id.customer_id", store=True)
    currency_id = fields.Many2one(related="reservation_id.currency_id")
    required_amount = fields.Monetary(
        string="Computed Deposit", currency_field="currency_id", readonly=True, copy=False
    )
    reduced_amount = fields.Monetary(
        string="Deposit Asked For", currency_field="currency_id", required=True
    )
    reason = fields.Text(required=True)
    decided_by = fields.Many2one("res.users", readonly=True, copy=False)
    decided_on = fields.Datetime(readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | {
            "required_amount",
            "decided_by",
            "decided_on",
        }

    def _approval_pinned_fields(self) -> set:
        return super()._approval_pinned_fields() | {
            "reservation_id",
            "required_amount",
            "reduced_amount",
        }

    def _approval_amount(self) -> float:
        self.ensure_one()
        return round(max((self.required_amount or 0.0) - (self.reduced_amount or 0.0), 0.0), 2)

    @api.model_create_multi
    def create(self, vals_list):
        Res = self.env["fix.rental.reservation"]
        for vals in vals_list:
            res = Res.browse(vals.get("reservation_id")).exists()
            if res and res.state != "draft":
                _refuse(
                    "A deposit reduction is decided before the booking is confirmed: %s is %s."
                    % (res.name, res.state)
                )
            vals["name"] = (
                self.env["ir.sequence"].sudo().next_by_code("fix.rental.deposit.reduction")
                or "RNT-DEPRED/New"
            )
        recs = super().create(vals_list)
        for rec in recs:
            rec._guarded().write({"required_amount": rec.reservation_id._deposit_required()})
            rec._check_reduction()
        return recs

    def write(self, vals):
        res = super().write(vals)
        if "reduced_amount" in vals or "reservation_id" in vals:
            for rec in self:
                rec._guarded().write({"required_amount": rec.reservation_id._deposit_required()})
                rec._check_reduction()
        return res

    def _check_reduction(self):
        for rec in self:
            if not (rec.reason or "").strip():
                _refuse("Say why the deposit is reduced (BRU-RNT-07).")
            if rec.reduced_amount < 0:
                _refuse("A deposit cannot be negative.")
            if rec.reduced_amount + 0.005 >= rec.required_amount:
                _refuse(
                    "%.2f is not below the computed deposit of %.2f: no reduction is needed."
                    % (rec.reduced_amount, rec.required_amount)
                )

    def _approval_needed(self) -> bool:
        return True

    def _reduction_approve(self):
        self._approval_assert_routed()
        for rec in self:
            authority = rec._approval_authority_user()
            if not self.env.su and not authority.has_group(FINANCE_MANAGER_GROUP):
                raise UserError("A deposit reduction is approved by a Finance Manager.")
            conflicted = (rec.create_uid | rec.approval_request_id.sudo().requested_by_id).sudo()
            if not self.env.su and (rec._approval_acting_users() & conflicted):
                raise UserError(
                    "Segregation of duties: you asked for this deposit reduction; another "
                    "Finance Manager decides it."
                )
            if abs(rec.reservation_id._deposit_required() - rec.required_amount) > 0.005:
                raise UserError(
                    "The computed deposit moved since the reduction was asked for; ask again."
                )
            rec._guarded().write({"decided_by": self.env.uid, "decided_on": fields.Datetime.now()})
        return True

    def _covers(self, reservation):
        """True when this granted reduction covers the booking's deposit."""
        self.ensure_one()
        return (
            self.approval_state == "approved"
            and self.reservation_id == reservation
            and abs(self.required_amount - reservation._deposit_required()) <= 0.005
            and (reservation.deposit_collected or 0.0) + 0.005 >= (self.reduced_amount or 0.0)
        )


class FixRentalDeposit(models.Model):
    _inherit = "fix.rental.deposit"

    # stream S4 (I3): treasury reads the source's branch for its dimensions
    branch_id = fields.Many2one(
        related="reservation_id.branch_id", store=True, string="Booking Branch"
    )


class FixRentalReservation(models.Model):
    _inherit = "fix.rental.reservation"

    billing_ids = fields.One2many("fix.rental.billing", "reservation_id", string="Billing")
    deposit_reduction_ids = fields.One2many(
        "fix.rental.deposit.reduction", "reservation_id", string="Deposit Reductions"
    )
    deposit_required = fields.Monetary(
        string="Deposit Required",
        currency_field="currency_id",
        compute="_compute_deposit_required",
        compute_sudo=True,
        help="Owner decision D8: the SKU / kit floor, or the unit's book value x the "
        "customer's risk-tier rate, whichever is higher. A lower deposit needs an approved "
        "deposit reduction.",
    )
    billable_total = fields.Monetary(
        currency_field="currency_id", compute="_compute_billing", compute_sudo=True
    )
    invoiced_total = fields.Monetary(
        currency_field="currency_id", compute="_compute_billing", compute_sudo=True
    )
    unbilled_amount = fields.Monetary(
        currency_field="currency_id", compute="_compute_billing", compute_sudo=True
    )
    hold_expires_at = fields.Datetime(
        string="Hold Expires",
        readonly=True,
        copy=False,
        help="AUT-RNT-02: a reserved booking not handed over by then is released",
    )
    overdue_notified_days = fields.Integer(readonly=True, copy=False)
    return_due_notified = fields.Boolean(readonly=True, copy=False)
    lease_assessment_required = fields.Boolean(
        string="M53 Lease Assessment Required",
        compute="_compute_lease_assessment_required",
        store=True,
        help="BRU-RNT-18: a rental of twelve months or more is assessed by M53 before it "
        "is activated",
    )
    m53_assessment_ref = fields.Char(string="M53 Lease Assessment Ref", readonly=True, copy=False)
    m53_assessed_by = fields.Many2one("res.users", readonly=True, copy=False)
    late_fee_retained = fields.Monetary(
        string="Late Fee Retained by Extensions",
        currency_field="currency_id",
        readonly=True,
        copy=False,
        help="A05 M13-02: the late fee accrued before a retroactive extension moved the "
        "return date; it stays charged (BRU-RNT-12)",
    )

    def _late_fee_on(self, on_date):
        self.ensure_one()
        return round((self.late_fee_retained or 0.0) + super()._late_fee_on(on_date), 2)

    def _fix_guarded_fields(self) -> set:
        return set(super()._fix_guarded_fields()) | {
            "late_fee_retained",
            "hold_expires_at",
            "overdue_notified_days",
            "return_due_notified",
            "m53_assessment_ref",
            "m53_assessed_by",
            # M13-29: the lessor classification is M53's, recorded by Finance
            "ifrs16_classification",
        }

    # ------------------------------------------------------------------
    # BRU-RNT-18 / M13-29
    # ------------------------------------------------------------------
    @api.depends("date_from", "date_to", "duration_days")
    def _compute_lease_assessment_required(self):
        threshold = policy.param_int(self.env, "lease_assessment_days", 365)
        for rec in self:
            rec.lease_assessment_required = (
                bool(threshold) and (rec.duration_days or 0) >= threshold
            )

    def action_record_lease_assessment(self, reference=None, classification=None):
        """Finance records M53's lease-classification assessment (reference
        and IFRS 16 classification) on a long rental before it is activated."""
        if not is_rental_finance(self.env.user):
            raise UserError("The M53 lease assessment is recorded by Finance.")
        reference = (reference or "").strip()
        if not reference:
            raise UserError("Give the M53 lease assessment reference.")
        classification = classification or "operating"
        if classification not in ("operating", "finance"):
            raise UserError("The classification is an operating or a finance lease.")
        for rec in self:
            if rec.state in ("closed", "cancelled"):
                raise UserError("Rental %s is %s." % (rec.name, rec.state))
            rec._guarded().write(
                {
                    "m53_assessment_ref": reference,
                    "m53_assessed_by": self.env.uid,
                    "ifrs16_classification": classification,
                }
            )
            rec.message_post(
                body="M53 lease assessment %s recorded (%s lease) by %s."
                % (reference, classification, self.env.user.name)
            )
        return True

    def _gate_active(self):
        super()._gate_active()
        if self.lease_assessment_required and not (self.m53_assessment_ref or "").strip():
            _refuse(
                "Rental %s runs %d days: a rental of twelve months or more is activated only "
                "after its M53 lease-classification assessment is recorded (BRU-RNT-18)."
                % (self.name, self.duration_days)
            )

    # ------------------------------------------------------------------
    # owner D8 — the deposit
    # ------------------------------------------------------------------
    def _deposit_tier(self):
        self.ensure_one()
        profile = (
            self.env["fix.rental.exposure"]
            .sudo()
            .search(
                [
                    ("partner_id", "=", self.customer_id.commercial_partner_id.id),
                    ("company_id", "=", self.company_id.id),
                ],
                limit=1,
            )
        )
        return profile.risk_tier or "standard"

    def _deposit_book_value(self):
        self.ensure_one()
        asset = self.rental_asset_id.sudo()
        if asset:
            return asset._book_value()
        if self.rental_sku_id:
            units = (
                self.env["fix.rental.asset"]
                .sudo()
                .search(
                    [
                        ("rental_sku_id", "=", self.rental_sku_id.id),
                        ("status", "not in", ("retired", "lost")),
                    ]
                )
            )
            return max([u._book_value() for u in units] or [0.0])
        return 0.0

    def _deposit_floor(self):
        self.ensure_one()
        sku = self.rental_sku_id.sudo()
        floor = (sku.security_deposit or 0.0) if sku and sku.deposit_basis != "none" else 0.0
        return max(floor, (self.kit_id.sudo().deposit or 0.0) if self.kit_id else 0.0)

    def _deposit_required(self):
        self.ensure_one()
        rate = policy.deposit_rate_pct(self.env, self._deposit_tier())
        by_value = round(self._deposit_book_value() * rate / 100.0, 2)
        return round(max(self._deposit_floor(), by_value), 2)

    def _compute_deposit_required(self):
        for rec in self:
            rec.deposit_required = rec._deposit_required()

    @api.model_create_multi
    def create(self, vals_list):
        recs = super().create(vals_list)
        for rec, vals in zip(recs, vals_list, strict=True):
            if "deposit_collected" not in vals and rec.state == "draft":
                rec.sudo().write({"deposit_collected": rec._deposit_required()})
        return recs

    def _deposit_denial(self):
        self.ensure_one()
        required = self._deposit_required()
        if (self.deposit_collected or 0.0) + 0.005 >= required:
            return ""
        if any(r._covers(self) for r in self.deposit_reduction_ids):
            return ""
        return (
            "Rental %s carries a deposit of %.2f; the required deposit is %.2f (the SKU / kit "
            "floor, or the unit's book value x the %s risk-tier rate, owner decision D8). A "
            "lower deposit needs a Finance Manager's approved deposit reduction with its "
            "reason (BRU-RNT-07)."
            % (self.name, self.deposit_collected or 0.0, required, self._deposit_tier())
        )

    # ------------------------------------------------------------------
    # gates (A05 M13-20 / FIN-09 / D8)
    # ------------------------------------------------------------------
    def _assert_unit_grade(self, unit):
        unit = unit.sudo()
        minimum = policy.min_dispatch_grade(self.env, unit.category)
        if policy.grade_below(unit.condition_grade, minimum):
            _refuse(
                "Unit %s is grade %s, below the %s minimum of grade %s: it is not allocated to "
                "a rental (BRU-RNT-14)."
                % (unit.name, (unit.condition_grade or "").upper(), unit.category, minimum.upper())
            )

    def _lock_capacity(self):
        """A row lock on what availability is decided against (the unit, the
        device, the SKU pool), so two counters confirming the last unit at
        once are serialised: the second waits, then fails on the first's
        update and is retried against the committed booking (M13-20)."""
        cr = self.env.cr
        statements = {
            "asset": "UPDATE fix_rental_asset SET write_date = write_date WHERE id = %s",
            "device": "UPDATE fix_device SET write_date = write_date WHERE id = %s",
            "sku": "UPDATE fix_rental_sku SET write_date = write_date WHERE id = %s",
        }
        for rec in self:
            for key, rid in (
                ("asset", rec.rental_asset_id.id),
                ("device", rec.device_id.id),
                ("sku", rec.rental_sku_id.id),
            ):
                if rid:
                    cr.execute(statements[key], (rid,))

    def _assert_available(self):
        self._lock_capacity()
        return super()._assert_available()

    def _gate_reserved(self):
        super()._gate_reserved()
        if not self.branch_id:
            _refuse(
                "Rental %s names no booking branch: the deposit posts to the branch and its "
                "operating unit (FIN-09)." % self.name
            )
        posting_operating_unit(self)
        if not self.rental_sku_id:
            _refuse(
                "Rental %s names no rental SKU: the tariff and the deposit floor come from the "
                "SKU (M13-01)." % self.name
            )
        if (self.tariff_breakdown or "").startswith("UNPRICED"):
            _refuse(
                "Rental SKU %s cannot price %d day(s): %s. Ask the catalogue officer for the "
                "missing rate (FR-RNT-035)."
                % (self.rental_sku_id.display_name, self.billable_days, self.tariff_breakdown)
            )
        if self.rental_asset_id:
            self._assert_unit_grade(self.rental_asset_id)
        denial = self._deposit_denial()
        if denial:
            _refuse(denial)

    def _gate_delivered(self):
        super()._gate_delivered()
        if self.rental_asset_id:
            self._assert_unit_grade(self.rental_asset_id)

    def write(self, vals):
        if "rental_asset_id" in vals and vals["rental_asset_id"] and not self._fix_guard_open():
            unit = self.env["fix.rental.asset"].browse(vals["rental_asset_id"]).exists()
            for rec in self:
                if unit and unit != rec.rental_asset_id:
                    rec._assert_unit_grade(unit)
        return super().write(vals)

    # ------------------------------------------------------------------
    # cumulative billing
    # ------------------------------------------------------------------
    def _billable_components(self):
        self.ensure_one()
        if self.state == "cancelled":
            return dict.fromkeys(COMPONENTS, 0.0)
        return {
            "rental_amount": round(self.rental_charge or 0.0, 2),
            "waiver_amount": round(self.waiver_fee or 0.0, 2),
            "late_fee_amount": round(self.late_fee or 0.0, 2),
        }

    def _billed_components(self):
        self.ensure_one()
        rows = self.sudo().billing_ids.filtered(lambda r: r.kind in RENTAL_FAMILY)._effective()
        return {c: round(sum(rows.mapped(c)), 2) for c in COMPONENTS}

    @api.depends(
        "billing_ids.state",
        "rental_charge",
        "waiver_fee",
        "late_fee",
        "state",
    )
    def _compute_billing(self):
        for rec in self:
            billable = rec._billable_components()
            billed = rec._billed_components()
            rec.billable_total = round(sum(billable.values()), 2)
            rec.invoiced_total = round(sum(billed.values()), 2)
            rec.unbilled_amount = round(rec.billable_total - rec.invoiced_total, 2)

    def _service_period(self):
        self.ensure_one()
        end = self.date_to
        if self.actual_return_date:
            end = self.actual_return_date
        return self.date_from, end

    def _raise_invoice(self, row, lines, reason, account):
        """The M20 draft invoice of a billing row (Finance issues it: number,
        Mushak 6.3, GL). Its source is the row, so each event is its own
        invoice and a replay returns the same one."""
        Invoice = self.env["fix.ar.invoice"].sudo()
        invoice = Invoice._fix_ar_invoice_from_source(
            row.sudo(),
            self.customer_id,
            lines,
            reason,
            credit_account=account,
            operating_unit=row.operating_unit_id,
            branch=row.branch_id,
            invoice_date=policy.dhaka_today(self.env),
            issue=False,
        )
        row._guarded().write({"invoice_id": invoice.id})
        if not self.mushak_6_3_id and row.kind == "rental":
            self._guarded().write({"mushak_6_3_id": invoice.id})
        return invoice

    def _new_row(self, kind, key, vals):
        self.ensure_one()
        ou = posting_operating_unit(self)
        base = {
            "name": "%s/%s" % (self.name, key),
            "reservation_id": self.id,
            "kind": kind,
            "key": key,
            "operating_unit_id": ou.id,
            "branch_id": self.branch_id.id,
        }
        base.update(vals)
        Billing = self.env["fix.rental.billing"].sudo()
        return Billing.browse(Billing._guarded().create(base).id)

    def _unique_key(self, prefix):
        self.ensure_one()
        taken = set(self.sudo().billing_ids.mapped("key"))
        n = 1
        while "%s-%d" % (prefix, n) in taken:
            n += 1
        return "%s-%d" % (prefix, n)

    def _cancel_draft_rental_invoices(self, reason):
        rows = self.sudo().billing_ids.filtered(
            lambda r: r.kind in RENTAL_FAMILY
            and r.state == "invoiced"
            and r.invoice_id
            and r.invoice_id.state == "draft"
        )
        for row in rows:
            row.invoice_id.sudo().action_cancel(reason)
            row._guarded().write({"state": "cancelled"})
        return rows

    def _request_rental_credit(self, negatives, reason):
        """A negative difference on an ISSUED rental invoice: a Mushak 6.7
        credit note is requested (M20 routes its approval)."""
        self.ensure_one()
        taxable = round(-sum(negatives.values()), 2)
        rows = (
            self.sudo()
            .billing_ids.filtered(
                lambda r: r.kind == "rental"
                and r.state == "invoiced"
                and r.invoice_id.state in ("issued", "paid")
            )
            ._effective()
        )
        for row in rows.sorted("id", reverse=True):
            invoice = row.invoice_id.sudo()
            ratio = (
                (invoice.total_payable / invoice.taxable_amount) if invoice.taxable_amount else 1
            )
            credit_amount = round(taxable * ratio, 2)
            open_credit = sum(
                invoice.credit_note_ids.filtered(
                    lambda n: n.state in ("pending_approval", "approved", "issued")
                ).mapped("amount")
            )
            if credit_amount > invoice.total_payable - open_credit + 0.005:
                continue
            credit_row = self._new_row(
                "credit",
                self._unique_key("credit"),
                dict(
                    {c: -v for c, v in negatives.items()},
                    taxable_amount=-taxable,
                    service_date_from=row.service_date_from,
                    service_date_to=row.service_date_to,
                    state="credit",
                ),
            )
            note = (
                self.env["fix.credit.note"]
                .sudo()
                ._fix_request_credit(invoice, credit_amount, "return", note=reason)
            )
            credit_row._guarded().write({"credit_note_id": note.id})
            self.message_post(
                body="Credit note of %.2f requested on %s: %s."
                % (credit_amount, invoice.display_name, reason)
            )
            return credit_row
        raise UserError(
            "Rental %s: the charges fell by %.2f but no issued rental invoice can carry the "
            "credit note. Finance corrects the invoices first." % (self.name, taxable)
        )

    def _bill_rental(self, key=None, extension=None, reason=None):
        """Bring what is invoiced up (or down) to what is billable. Positive
        differences become one supplementary invoice keyed `key`; negative
        ones cancel a draft invoice (and re-bill) or request a credit note."""
        self.ensure_one()
        reason = reason or "Rental charges %s" % self.name
        for _attempt in range(3):
            billable = self._billable_components()
            billed = self._billed_components()
            deltas = {c: round(billable[c] - billed[c], 2) for c in COMPONENTS}
            negatives = {c: v for c, v in deltas.items() if v < -0.005}
            if not negatives:
                break
            if self._cancel_draft_rental_invoices("Rental %s re-billed: %s" % (self.name, reason)):
                continue
            self._request_rental_credit(negatives, reason)
            break
        billable = self._billable_components()
        billed = self._billed_components()
        positives = {
            c: round(billable[c] - billed[c], 2)
            for c in COMPONENTS
            if billable[c] - billed[c] > 0.005
        }
        if not positives:
            return self.env["fix.rental.billing"]
        key = key or self._unique_key("issue")
        existing = self.sudo().billing_ids.filtered(lambda r: r.key == key)
        if existing:
            key = self._unique_key(key)
        if extension:
            start = extension.old_date_to + timedelta(days=1)
            end = extension.new_date_to
        else:
            start, end = self._service_period()
        row = self._new_row(
            "rental",
            key,
            dict(
                positives,
                taxable_amount=round(sum(positives.values()), 2),
                extension_id=extension.id if extension else False,
                service_date_from=start,
                service_date_to=end,
            ),
        )
        company = self.company_id
        code = _vat_code(self.env, company, "rental")
        with_period = "service_period_start" in self.env["fix.ar.invoice.line"]._fields
        lines = []
        for comp, amount in positives.items():
            label = COMPONENT_LABEL[comp]
            if comp == "rental_amount":
                label = "%s %s, %s to %s (%s)" % (
                    label,
                    self.name,
                    start,
                    end,
                    self.tariff_breakdown or "",
                )
            elif comp == "waiver_amount":
                label = "%s %s (%s)" % (label, self.waiver_plan_id.name or "", self.name)
            else:
                label = "%s %s (returned %s, due %s)" % (
                    label,
                    self.name,
                    self.actual_return_date or "-",
                    self.date_to,
                )
            line = {"description": label[:250], "taxable_amount": amount}
            if code:
                line["vat_treatment_code"] = code
            if comp != "late_fee_amount" and with_period and start and end and end >= start:
                # stream S4 (FIN-14): earned over the hire, deferred and
                # released by day; the late fee is recognised at issue
                line["service_period_start"] = start
                line["service_period_end"] = end
            lines.append(line)
        self._raise_invoice(row, lines, reason, rental_account(self.env, company, "rental_income"))
        return row

    def _bill_compensation(self, kind, key, amount, description, damage_lines=None):
        """Damage above the deposit, or a lost unit's valuation above it: an
        M20 invoice outside VAT (owner D2) crediting recovery income."""
        self.ensure_one()
        amount = round(amount or 0.0, 2)
        if amount <= 0:
            return self.env["fix.rental.billing"]
        existing = self.sudo().billing_ids.filtered(lambda r: r.key == key)
        if existing:
            return existing
        company = self.company_id
        code = _vat_code(self.env, company, kind)
        row = self._new_row(
            kind,
            key,
            {
                "fee_amount": amount,
                "taxable_amount": amount,
                "service_date_from": self.date_from,
                "service_date_to": self.actual_return_date or self.date_to,
            },
        )
        invoice = self._raise_invoice(
            row,
            [
                {
                    "description": description[:250],
                    "taxable_amount": amount,
                    "vat_treatment_code": code,
                }
            ],
            description,
            rental_account(self.env, company, "recovery_income"),
        )
        if damage_lines:
            damage_lines._guarded().write({"invoice_id": invoice.id})
        return row

    def _bill_cancellation_fee(self, fee, pct):
        self.ensure_one()
        fee = round(fee or 0.0, 2)
        if fee <= 0:
            return self.env["fix.rental.billing"]
        company = self.company_id
        code = _vat_code(self.env, company, "cancellation")
        row = self._new_row(
            "cancellation",
            "cancel",
            {
                "fee_amount": fee,
                "taxable_amount": fee,
                "service_date_from": self.date_from,
                "service_date_to": self.date_from,
            },
        )
        line = {
            "description": "Cancellation fee %s (%.1f%% of the deposit)" % (self.name, pct),
            "taxable_amount": fee,
        }
        if code:
            line["vat_treatment_code"] = code
        self._raise_invoice(
            row,
            [line],
            "Cancellation of rental %s" % self.name,
            rental_account(self.env, company, "rental_income"),
        )
        return row

    def action_issue_rental_invoice(self):
        """Raise the rental's charges not yet invoiced (rental, waiver, late
        fee) as an M20 draft invoice - the first one, or a supplementary
        one. Refused when everything billable is already invoiced."""
        for rec in self:
            if rec.state in ("draft", "cancelled"):
                raise UserError("Rental %s is %s: nothing was rented." % (rec.name, rec.state))
            billable, billed = rec._unbilled()
            if abs(billable - billed) <= 0.005:
                raise UserError(
                    "Rental %s: everything billable (%.2f) is already invoiced."
                    % (rec.name, billable)
                )
            rec._bill_rental(
                reason="Rental charges %s (%s to %s)" % (rec.name, rec.date_from, rec.date_to)
            )
        return True

    def _unbilled(self):
        """(billable, invoiced) read fresh: an invoice cancelled in M20 since
        the last read counts at once."""
        self.ensure_one()
        billable = round(sum(self._billable_components().values()), 2)
        billed = round(sum(self._billed_components().values()), 2)
        return billable, billed

    def _gate_closed(self):
        super()._gate_closed()
        billable, billed = self._unbilled()
        if billable - billed > 0.005:
            _refuse(
                "Rental %s cannot be closed: %.2f of its charges (rental, waiver, late fee: "
                "billable %.2f, invoiced %.2f) is not invoiced. Issue the rental invoice first "
                "(FIN-07)." % (self.name, billable - billed, billable, billed)
            )

    # ------------------------------------------------------------------
    # XC-22: the deposit is released by someone other than who took it
    # ------------------------------------------------------------------
    def _deposit_collector(self):
        self.ensure_one()
        return self.sudo().deposit_ids.filtered(lambda d: d.kind == "collect").mapped("create_uid")

    def _assert_release_sod(self, step):
        if self.env.su:
            return
        for rec in self:
            if self.env.user in rec._deposit_collector():
                raise UserError(
                    "Segregation of duties: you took the deposit on %s; another person %s it "
                    "and releases the deposit (XC-22)." % (rec.name, step)
                )

    # ------------------------------------------------------------------
    # crons: hold expiry (AUT-RNT-02), overdue (M13-26), return due (I5)
    # ------------------------------------------------------------------
    def _set_hold_expiry(self):
        hours = policy.param_int(self.env, "hold_grace_hours", 24)
        import pytz

        tz = pytz.timezone("Asia/Dhaka")
        for rec in self.filtered("date_from"):
            start_end = (
                tz.localize(fields.Datetime.to_datetime(rec.date_from) + timedelta(days=1))
                .astimezone(pytz.UTC)
                .replace(tzinfo=None)
            )
            rec._guarded().write({"hold_expires_at": start_end + timedelta(hours=hours)})

    @api.model
    def cron_rental_hold_expiry(self):
        """AUT-RNT-02: a reserved booking whose hold expired without the unit
        being handed over is released (cancelled, the deposit refunded less
        any cancellation fee) and the coordinator alerted - never silently
        retained."""
        now = fields.Datetime.now()
        expired = self.sudo().search(
            [
                ("state", "=", "reserved"),
                ("hold_expires_at", "!=", False),
                ("hold_expires_at", "<", now),
            ]
        )
        for rec in expired:
            try:
                with self.env.cr.savepoint():
                    rec.with_context(rental_cancel_reason="hold expired").action_cancel()
            except UserError as exc:
                rec.message_post(
                    body="Hold expired but the booking could not be released: %s" % exc
                )
                rec.activity_schedule(
                    "mail.mail_activity_data_todo",
                    summary="Hold of %s expired: release it by hand" % rec.name,
                    user_id=rec.create_uid.id or self.env.uid,
                )
                continue
            rec.message_post(body="Hold expired on %s: booking released." % rec.hold_expires_at)
            rec.activity_schedule(
                "mail.mail_activity_data_todo",
                summary="Hold of %s expired and was released" % rec.name,
                user_id=rec.create_uid.id or self.env.uid,
            )
        return len(expired)

    def _escalate_overdue(self, today):
        """M13-26: at each configured overdue milestone (1 / 3 / 7 days) the
        customer notification event rental.overdue is published once and the
        booker is escalated."""
        milestones = policy.int_list(self.env, "overdue_reminder_days", "1,3,7")
        for rec in self:
            if not rec.overdue_since:
                continue
            days = (today - rec.date_to).days
            due = [m for m in milestones if m <= days and m > (rec.overdue_notified_days or 0)]
            if not due:
                continue
            reached = max(due)
            rec._guarded().write({"overdue_notified_days": reached})
            publish(
                self.env,
                "rental.overdue",
                "fix.rental.reservation",
                rec.id,
                {
                    "reservation_id": rec.id,
                    "partner_id": rec.customer_id.id,
                    "days_overdue": int(days),
                },
            )
            rec.activity_schedule(
                "mail.mail_activity_data_todo",
                summary="Rental %s is %d day(s) overdue: escalate recovery" % (rec.name, days),
                user_id=rec.create_uid.id or self.env.uid,
            )

    @api.model
    def cron_rental_overdue(self):
        count = super().cron_rental_overdue()
        today = policy.dhaka_today(self.env)
        grace = policy.param_int(self.env, "late_fee_grace_days", 0)
        overdue = self.sudo().search(
            [
                ("state", "in", ("delivered", "active")),
                ("date_to", "<", today - timedelta(days=grace)),
            ]
        )
        overdue._escalate_overdue(today)
        return count

    @api.model
    def cron_rental_return_due(self):
        """I5: rental.return_due once per rental, the configured number of
        days (default 1, i.e. T-24h) before the unit is due back."""
        today = policy.dhaka_today(self.env)
        notice = policy.param_int(self.env, "return_due_notice_days", 1)
        due = self.sudo().search(
            [
                ("state", "in", ("delivered", "active")),
                ("return_due_notified", "=", False),
                ("date_to", ">=", today),
                ("date_to", "<=", today + timedelta(days=notice)),
            ]
        )
        for rec in due:
            publish(
                self.env,
                "rental.return_due",
                "fix.rental.reservation",
                rec.id,
                {
                    "reservation_id": rec.id,
                    "partner_id": rec.customer_id.id,
                    "due_at": str(rec.date_to),
                },
            )
            rec._guarded().write({"return_due_notified": True})
        return len(due)


class FixRentalWaiverPlan(models.Model):
    """XC-07: a damage-waiver plan is Rental Finance's product: configured,
    published and retired by Finance (the ACL gives everyone else read), and
    published by a person other than whoever configured it."""

    _inherit = "fix.rental.waiver.plan"

    def _require_finance(self, what):
        if not self.env.su and not is_rental_finance(self.env.user):
            raise AccessError("%s is Rental Finance's decision (XC-07)." % what)

    @api.model_create_multi
    def create(self, vals_list):
        self._require_finance("Configuring a damage-waiver plan")
        return super().create(vals_list)

    def write(self, vals):
        if not self._fix_guard_open():
            self._require_finance("Changing a damage-waiver plan")
        return super().write(vals)

    def action_publish(self):
        self._require_finance("Publishing a damage-waiver plan")
        return super().action_publish()

    def action_retire(self):
        self._require_finance("Retiring a damage-waiver plan")
        return super().action_retire()
