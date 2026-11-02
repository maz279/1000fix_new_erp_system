# fix_rental_fleet — M13: the fleet, kits, deposit ledger, condition reports
# and turnaround records the workspace screens read. The reservation and its
# damage lines already live in fix_rental_asset.py; these models compose with
# them (one fleet item per reservation, one deposit event per money movement).
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .rental_gl import (
    PAYMENT_METHOD,
    post_rental_move,
    rental_account,
    tender_account,
)


class FixRentalAsset(models.Model):
    """A serialised item in the rental fleet (the Fleet Register unit)."""

    _name = "fix.rental.asset"
    _description = "Rental Fleet Asset"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.dofa.mixin"]
    _order = "name"

    # A05 DOFA matrix — Rental Fleet Asset Retirement / Write-Off: never a
    # branch decision (tier 1 is NOT permitted); Fleet Maintenance Lead from
    # BDT 50k, Head of Supply Chain from 250k, CEO & CFO above 1M.
    _DOFA_THRESHOLDS = [
        (0.0, "tier_0"),
        (250000.0, "tier_2"),
        (1000000.0, "tier_3"),
        (float("inf"), "tier_4"),
    ]

    def _dofa_thresholds(self):
        return self._DOFA_THRESHOLDS

    def _dofa_amount(self) -> float:
        """The net book value written off by retirement — never the purchase
        cost (a fully depreciated asset risks only its residual)."""
        self.ensure_one()
        return self.net_book_value or 0.0

    def _dofa_amount_label(self) -> str:
        self.ensure_one()
        return "BDT %.2f (net book value)" % self._dofa_amount()

    @api.depends("net_book_value")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    name = fields.Char(string="Asset Code", required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    rental_sku_id = fields.Many2one(
        "fix.rental.sku", string="Rental SKU", required=True, ondelete="restrict", index=True
    )
    device_id = fields.Many2one("fix.device", string="Device (M17)", ondelete="set null")
    serial_no = fields.Char(string="Serial Number")
    category = fields.Selection(
        [
            ("camera", "Camera & Lens"),
            ("laptop", "Laptop & PC"),
            ("projector", "Projector & Display"),
            ("audio", "Audio & Lighting"),
            ("tool", "Power Tool"),
            ("medical", "Medical Device"),
            ("network", "Network Equipment"),
            ("other", "Other"),
        ],
        required=True,
        default="other",
    )
    condition_grade = fields.Selection(
        [("a", "A — Like new"), ("b", "B — Good"), ("c", "C — Fair"), ("d", "D — Poor")],
        required=True,
        default="a",
    )
    battery_health_pct = fields.Integer(string="Battery Health %", default=100)
    status = fields.Selection(
        [
            ("available", "Available"),
            ("reserved", "Reserved"),
            ("out", "On Rent"),
            ("maintenance", "In Maintenance"),
            ("retired", "Retired"),
        ],
        required=True,
        default="available",
        index=True,
    )
    acquisition_date = fields.Date()
    purchase_cost = fields.Monetary(currency_field="currency_id")
    residual_value = fields.Monetary(
        string="Residual Value", currency_field="currency_id", default=0.0
    )
    useful_life_days = fields.Integer(
        string="Useful Life (Days)", default=1095, help="3-year statutory useful life under IAS 16"
    )
    daily_depreciation = fields.Monetary(
        string="Daily Depreciation (BDT)",
        currency_field="currency_id",
        compute="_compute_depreciation",
        store=True,
    )
    net_book_value = fields.Monetary(
        string="Net Book Value (BDT)",
        currency_field="currency_id",
        compute="_compute_depreciation",
        store=True,
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    accumulated_depreciation = fields.Monetary(
        string="Accumulated Depreciation (BDT)",
        currency_field="currency_id",
        compute="_compute_depreciation",
        store=True,
        help="Straight-line depreciation accrued since acquisition (IAS 16), "
        "capped at cost − residual",
    )
    reservation_ids = fields.One2many(
        "fix.rental.reservation", "rental_asset_id", string="Reservation History"
    )
    last_service_date = fields.Date(string="Last Preventive Service")
    next_service_due = fields.Date(
        string="Next Service Due",
        help="PM due date; turnaround resets it on completion",
    )
    total_repair_cost = fields.Monetary(
        string="Lifetime Repair Cost",
        currency_field="currency_id",
        help="Rolled-up workshop cost of keeping this unit in the fleet",
    )
    rental_days_total = fields.Integer(
        string="Rental Days (Lifetime)",
        compute="_compute_utilisation",
        store=True,
    )
    cumulative_revenue = fields.Monetary(
        string="Cumulative Revenue",
        currency_field="currency_id",
        compute="_compute_utilisation",
        store=True,
    )
    utilization_rate_30d = fields.Float(
        string="Utilisation % (30 days)",
        compute="_compute_utilisation",
        help="Rented days in the last 30 ÷ 30 — the fleet-health KPI's numerator",
    )
    retired_on = fields.Date()
    retirement_reason = fields.Char()
    notes = fields.Text()

    @api.depends("purchase_cost", "residual_value", "useful_life_days", "acquisition_date")
    def _compute_depreciation(self):
        today = fields.Date.context_today(self)
        for rec in self:
            cost = rec.purchase_cost or 0.0
            residual = rec.residual_value or 0.0
            life = rec.useful_life_days or 1095
            daily = (cost - residual) / float(life) if life > 0 and cost > residual else 0.0
            rec.daily_depreciation = round(daily, 2)

            if rec.acquisition_date and rec.acquisition_date <= today:
                days_in_service = (today - rec.acquisition_date).days
            else:
                days_in_service = 0

            accum_deprec = min(daily * days_in_service, max(cost - residual, 0.0))
            nbv = max(residual, cost - accum_deprec)
            rec.accumulated_depreciation = round(accum_deprec, 2)
            rec.net_book_value = round(nbv, 2)

    @api.depends(
        "reservation_ids.state",
        "reservation_ids.duration_days",
        "reservation_ids.rental_charge",
        "reservation_ids.late_fee",
        "reservation_ids.date_from",
        "reservation_ids.date_to",
    )
    def _compute_utilisation(self):
        from datetime import timedelta

        today = fields.Date.context_today(self)
        window_start = today - timedelta(days=29)
        for rec in self:
            live = rec.reservation_ids.filtered(lambda r: r.state != "cancelled")
            rec.rental_days_total = sum(live.mapped("duration_days"))
            rec.cumulative_revenue = sum(
                (r.rental_charge or 0.0) + (r.late_fee or 0.0) for r in live
            )
            rented = sum(
                max((min(r.date_to, today) - max(r.date_from, window_start)).days + 1, 0)
                for r in live
                if r.date_from
                and r.date_to
                and r.state in ("reserved", "delivered", "active")
                and r.date_from <= today
                and r.date_to >= window_start
            )
            rec.utilization_rate_30d = round(min(rented, 30) / 30.0 * 100.0, 1)

    _battery_range = models.Constraint(
        "CHECK (battery_health_pct >= 0 AND battery_health_pct <= 100)",
        "Battery health must be a percentage between 0 and 100",
    )
    _purchase_cost_positive = models.Constraint(
        "CHECK (purchase_cost >= 0)",
        "Purchase cost cannot be negative",
    )

    def action_retire(self):
        """Retire a fleet unit. A unit on rent must come back first, and the
        write-off of its net book value carries DOFA authority (the A05
        matrix forbids tier-1 retirement outright)."""
        for rec in self:
            if rec.status == "out":
                raise ValidationError("Return the asset before retiring it")
            rec._dofa_assert_approved("Fleet asset retirement")
            rec.write(
                {
                    "status": "retired",
                    "retired_on": fields.Date.context_today(self),
                }
            )

    def action_ready(self):
        for rec in self:
            if rec.status == "retired" and rec.net_book_value:
                raise UserError(
                    "%s is retired with BDT %.2f net book value — reactivation is a "
                    "reversal of a governed write-off, not a status flip"
                    % (rec.name, rec.net_book_value)
                )
            rec.status = "available"


class FixRentalKit(models.Model):
    """A kit bundles a rental SKU with its accessories and deposit."""

    _name = "fix.rental.kit"
    _description = "Rental Kit"
    _order = "name"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    rental_sku_id = fields.Many2one(
        "fix.rental.sku", string="Rental SKU", required=True, ondelete="restrict"
    )
    accessories = fields.Text(
        string="Included Accessories",
        help="One per line: what ships with the kit and must come back",
    )
    accessory_count = fields.Integer(
        compute="_compute_accessory_count", store=True, string="Accessories"
    )
    deposit = fields.Monetary(currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    active = fields.Boolean(default=True)

    @api.depends("accessories")
    def _compute_accessory_count(self):
        for rec in self:
            lines = (rec.accessories or "").splitlines()
            rec.accessory_count = len([line for line in lines if line.strip()])


class FixRentalDeposit(models.Model):
    """One money movement against a rental's security deposit."""

    _name = "fix.rental.deposit"
    _description = "Rental Deposit Movement"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    reservation_id = fields.Many2one(
        "fix.rental.reservation", required=True, ondelete="cascade", index=True
    )
    customer_id = fields.Many2one(
        related="reservation_id.customer_id", string="Customer", store=True, index=True
    )
    kind = fields.Selection(
        [
            ("collect", "Collected"),
            ("refund", "Refunded"),
            ("deduction", "Deducted"),
            ("forfeit", "Forfeited"),
        ],
        required=True,
        default="collect",
    )
    amount = fields.Monetary(required=True, currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    method = fields.Selection(
        [
            ("cash", "Cash"),
            ("bkash", "bKash"),
            ("nagad", "Nagad"),
            ("card", "Card / SSLCOMMERZ"),
            ("bank", "Bank Transfer"),
        ],
        required=True,
        default="cash",
    )
    reference = fields.Char()
    date = fields.Date(required=True, default=fields.Date.context_today)
    note = fields.Char()
    journal_entry_id = fields.Many2one(
        "account.move",
        string="GL Journal Entry",
        readonly=True,
        copy=False,
        help="Dual-entry General Ledger move behind this movement",
    )
    gl_state = fields.Selection(
        [
            ("pending", "GL Pending"),
            ("posted", "GL Posted"),
            ("refund_queued", "Refund Queued (M50)"),
            ("failed", "GL Failed"),
        ],
        string="GL State",
        default="pending",
        required=True,
        copy=False,
        tracking=True,
        help="Money movements post to the General Ledger or say why they "
        "did not — 'GL Ready' notes and silent sub-ledger rows are not "
        "an audit trail.",
    )
    gl_note = fields.Char(
        string="GL Note",
        copy=False,
        help="Why a movement carries no journal entry (legacy rows, refused postings)",
    )
    payment_execution_id = fields.Many2one(
        "fix.payment.execution",
        string="Refund Instruction (M50)",
        readonly=True,
        copy=False,
        ondelete="set null",
        help="Treasury instruction returning the customer's money — M50 posts "
        "Dr deposits held / Cr bank when the bank confirms it left",
    )
    damage_id = fields.Many2one(
        "fix.rental.damage",
        string="Offset Damage Record",
        ondelete="set null",
        index=True,
        help="The proven damage/late-fee charge this deduction settles",
    )

    _amount_positive = models.Constraint(
        "CHECK (amount >= 0)", "A deposit movement cannot be negative"
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.rental.deposit") or "DEP/New"
                )
        return super().create(vals_list)

    def _post(self, reservation, kind, amount, note="", damage=None, method="cash"):
        """One money movement against a rental deposit — sub-ledger row AND
        General Ledger, or an honest refusal.

        collect    Dr cash/bank/MFS clearing .... Cr customer deposits held
        deduction  Dr customer deposits held ..... Dr→Cr damage/late-fee recovery income
        forfeit    Dr customer deposits held ..... Cr recovery income
        refund     no GL here: an M50 payment instruction is queued; treasury
                   debits the deposits-held liability when the bank confirms
                   the money left (the estate's two-stage money rule).

        The accounts come from rental_gl (statutory chart 2-40-20-010 /
        4-90-10-010, overridable per system parameter) and the posting goes
        through M19's post_with_dimensions, so the COA-01/02/03 rules bind
        rentals exactly as they bind invoices. A missing account or booking
        branch REFUSES the movement — money is never parked on a guess."""
        if not amount:
            return self.browse()
        vals = {
            "reservation_id": reservation.id,
            "kind": kind,
            "amount": amount,
            "method": method,
            "note": note or dict(self._fields["kind"].selection).get(kind, ""),
            "damage_id": damage.id if damage else False,
        }
        rec = self.create(vals)
        if kind == "refund":
            rec._queue_refund()
        else:
            rec._post_gl()
        return rec

    def _post_gl(self):
        """Post this movement's dual-entry (collect / deduction / forfeit)."""
        for rec in self:
            if rec.journal_entry_id:
                continue  # idempotent: one movement, one journal entry
            reservation = rec.reservation_id
            company = reservation.company_id
            try:
                liability = rental_account(self.env, company, "deposit_liability")
                partner = reservation.customer_id
                if rec.kind == "collect":
                    tender = tender_account(self.env, company, rec.method)
                    lines = [
                        (
                            tender,
                            "%s: %s received" % (rec.name, rec.method),
                            rec.amount,
                            0.0,
                            partner,
                        ),
                        (liability, "%s: deposits held" % rec.name, 0.0, rec.amount, partner),
                    ]
                elif rec.kind in ("deduction", "forfeit"):
                    income = rental_account(self.env, company, "retention_income")
                    lines = [
                        (
                            liability,
                            "%s: deposits held applied" % rec.name,
                            rec.amount,
                            0.0,
                            partner,
                        ),
                        (income, "%s: %s recovery" % (rec.name, rec.kind), 0.0, rec.amount, None),
                    ]
                else:
                    raise UserError(
                        "Deposit movement %s is a %s: refunds queue with treasury, "
                        "they do not post here" % (rec.name, rec.kind)
                    )
                move = post_rental_move(
                    self.env,
                    reservation,
                    rec.date,
                    "RDEP %s — %s" % (reservation.name, rec.kind),
                    lines,
                )
                rec.write({"journal_entry_id": move.id, "gl_state": "posted", "gl_note": False})
            except UserError as exc:
                # The money moved in the real world; the ledger row must exist
                # whatever the GL configuration says. The refusal is pinned on
                # the row (gl_state=failed + the exact reason), chatter carries
                # it, and action_repost_gl posts it once the account or the
                # booking branch is configured. Never a silent skip, never a
                # lost collection.
                reason = str(exc)[:250]
                rec.write({"gl_state": "failed", "gl_note": reason})
                rec.message_post(
                    body="GL posting refused: %s — fix the configuration and press "
                    "Repost GL." % reason
                )

    def _queue_refund(self):
        """Queue the refund with M50 treasury (idempotent on this movement).
        The deposits-held liability is the account the confirmation debits,
        so the customer's money leaves the books exactly once."""
        for rec in self:
            if rec.kind != "refund":
                raise UserError("Only refunds queue a treasury instruction")
            if rec.payment_execution_id:
                continue
            reservation = rec.reservation_id
            liability = rental_account(self.env, reservation.company_id, "deposit_liability")
            journal = self.env["account.journal"].search(
                [("type", "=", "bank"), ("company_id", "=", reservation.company_id.id)], limit=1
            )
            payment = (
                self.env["fix.payment.execution"]
                .sudo()
                .create(
                    {
                        "company_id": reservation.company_id.id,
                        "operating_unit_id": (
                            reservation.operating_unit_id
                            or self.env["operating.unit"].search(
                                [("company_id", "=", reservation.company_id.id)], limit=1
                            )
                        ).id,
                        "source_model": "fix.rental.deposit",
                        "source_id": rec.id,
                        "payee": reservation.customer_id.name,
                        "partner_id": reservation.customer_id.id,
                        "amount": rec.amount,
                        "method": PAYMENT_METHOD.get(rec.method, "bank_transfer"),
                        "debit_account_id": liability.id,
                        "journal_id": journal.id,
                    }
                )
            )
            rec.write(
                {
                    "payment_execution_id": payment.id,
                    "gl_state": "refund_queued",
                    "gl_note": "Refund queued as %s — GL posts on bank confirmation (M50)"
                    % payment.name,
                }
            )

    def action_repost_gl(self):
        """Operator recovery for a movement whose posting was refused (the
        account or branch was configured after the fact)."""
        for rec in self:
            if rec.journal_entry_id:
                raise UserError(
                    "%s already carries journal entry %s" % (rec.name, rec.journal_entry_id.name)
                )
            if rec.kind == "refund":
                raise UserError("Refunds post through M50, not here")
            rec._post_gl()


class FixRentalCondition(models.Model):
    """A pre-delivery or post-return condition report for one rental."""

    _name = "fix.rental.condition"
    _description = "Rental Condition Report"
    _order = "reported_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    reservation_id = fields.Many2one(
        "fix.rental.reservation", required=True, ondelete="cascade", index=True
    )
    rental_asset_id = fields.Many2one("fix.rental.asset", string="Fleet Asset", ondelete="set null")
    report_type = fields.Selection(
        [("pre_delivery", "Pre-Delivery"), ("post_return", "Post-Return")],
        required=True,
        default="post_return",
    )
    grade = fields.Selection(
        [("a", "A"), ("b", "B"), ("c", "C"), ("d", "D")], required=True, default="a"
    )
    battery_health_pct = fields.Integer(string="Battery Health %", default=100)
    charge_cycles = fields.Integer(
        string="Charge Cycles", help="Battery cycle count read at inspection"
    )
    charger_ok = fields.Boolean(string="Charger Present", default=True)
    case_ok = fields.Boolean(string="Case / Bag Present", default=True)
    screen_ok = fields.Boolean(string="Screen Intact", default=True)
    ports_ok = fields.Boolean(string="Ports & Connectors OK", default=True)
    body_condition_rating = fields.Selection(
        [("mint", "Mint"), ("good", "Good"), ("fair", "Fair"), ("poor", "Poor")],
        string="Body Condition",
    )
    maintenance_required = fields.Boolean(
        string="Maintenance Required",
        help="The 15-point check failed something the turnaround must fix",
    )
    notes = fields.Text()
    inspector_id = fields.Many2one("hr.employee", string="Inspector")
    photos_ref = fields.Char(string="Photo Evidence Ref")
    reported_on = fields.Date(required=True, default=fields.Date.context_today)

    _battery_range = models.Constraint(
        "CHECK (battery_health_pct >= 0 AND battery_health_pct <= 100)",
        "Battery health must be a percentage between 0 and 100",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.rental.condition") or "COND/New"
                )
        return super().create(vals_list)


class FixRentalTurnaround(models.Model):
    """The clean → inspect → re-grade → ready loop after a return."""

    _name = "fix.rental.turnaround"
    _description = "Rental Turnaround"
    _order = "returned_on desc, id desc"

    name = fields.Char(required=True, default="New")
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    rental_asset_id = fields.Many2one(
        "fix.rental.asset", string="Fleet Asset", required=True, ondelete="cascade", index=True
    )
    reservation_id = fields.Many2one(
        "fix.rental.reservation", string="Reservation", ondelete="set null"
    )
    returned_on = fields.Date(required=True, default=fields.Date.context_today)
    cleaning_done = fields.Boolean()
    sensor_cleaned = fields.Boolean(string="Sensors Cleaned")
    connectors_inspected = fields.Boolean(string="Connectors Inspected")
    firmware_updated = fields.Boolean(string="Firmware Updated")
    inspection_done = fields.Boolean()
    # NIST SP 800-88 sanitization of the returned unit's storage (the
    # customer's data leaves with the device; M06's certificate is the
    # cryptographic evidence, the hash the tamper-proof fingerprint)
    data_wipe_certificate_id = fields.Many2one(
        "fix.data.wipe.certificate",
        string="Data Wipe Certificate (M06)",
        ondelete="set null",
        index=True,
        help="M06 NIST SP 800-88 wipe evidence for the returned unit",
    )
    nist_wipe_hash = fields.Char(
        string="NIST Wipe Hash (SHA-256)",
        copy=False,
        help="Verification hash of the wipe log — required before the unit "
        "re-enters the rentable fleet",
    )
    memory_card_wiped = fields.Boolean(string="Memory Card Wiped")
    internal_storage_factory_reset = fields.Boolean(string="Internal Storage Reset")
    grade_before = fields.Selection(
        [("a", "A"), ("b", "B"), ("c", "C"), ("d", "D")], string="Grade Before"
    )
    regrade = fields.Selection(
        [("a", "A"), ("b", "B"), ("c", "C"), ("d", "D")], string="Re-Graded As"
    )
    battery_health_after_pm = fields.Integer(
        string="Battery Health After PM %",
        help="Measured after cleaning/PM; the regrade must reflect it",
    )
    functional_score_pct = fields.Integer(
        string="Functional Score %",
        help="Bench functional test result after turnaround (0-100)",
    )
    technician_id = fields.Many2one("hr.employee", string="Turnaround Technician")
    ready_timestamp = fields.Datetime(
        string="Ready Timestamp",
        readonly=True,
        copy=False,
        help="When the unit was released to the fleet",
    )
    available_on = fields.Date(string="Available From")
    state = fields.Selection(
        [
            ("pending", "Pending"),
            ("cleaning", "Cleaning"),
            ("inspection", "Inspection"),
            ("ready", "Ready"),
            ("retired", "Retired"),
        ],
        required=True,
        default="pending",
    )
    notes = fields.Char()

    _battery_pm_range = models.Constraint(
        "CHECK (battery_health_after_pm >= 0 AND battery_health_after_pm <= 100 "
        "AND functional_score_pct >= 0 AND functional_score_pct <= 100)",
        "Battery health and functional score are percentages between 0 and 100",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.rental.turnaround") or "TURN/New"
                )
        return super().create(vals_list)

    def action_ready(self):
        """Release the unit back to the rentable fleet. The wipe gate: a unit
        whose storage was reset carries either M06's verified certificate or
        a recorded wipe hash — a bare 'factory reset' checkbox is not
        evidence that the previous customer's data is gone."""
        for rec in self:
            wiped = rec.internal_storage_factory_reset or rec.memory_card_wiped
            certified = (
                rec.data_wipe_certificate_id
                and rec.data_wipe_certificate_id.sanitization_status == "verified"
            )
            if wiped and not (rec.nist_wipe_hash or "").strip() and not certified:
                raise UserError(
                    "Turnaround %s: storage was wiped but carries no evidence — "
                    "attach M06's verified wipe certificate or record the SHA-256 "
                    "wipe hash before the unit re-enters the fleet (NIST SP 800-88)" % rec.name
                )
            vals = {
                "state": "ready",
                "available_on": fields.Date.context_today(self),
                "ready_timestamp": fields.Datetime.now(),
            }
            if rec.regrade:
                rec.rental_asset_id.condition_grade = rec.regrade
            rec.write(vals)
            rec.rental_asset_id.status = "available"
            rec.rental_asset_id.last_service_date = fields.Date.context_today(self)
            rec.rental_asset_id.next_service_due = fields.Date.context_today(self) + relativedelta(
                months=3
            )

    def action_retire(self):
        for rec in self:
            rec.state = "retired"
            rec.rental_asset_id.action_retire()
            if not rec.rental_asset_id.retirement_reason:
                rec.rental_asset_id.retirement_reason = rec.notes or "Retired at turnaround"
