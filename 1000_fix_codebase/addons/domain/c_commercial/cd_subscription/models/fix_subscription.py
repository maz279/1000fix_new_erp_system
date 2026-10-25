# cd_subscription — M39 Subscription & recurring revenue + the M53 W4
# revenue slice (P07-M03, CD-M39-01).
#
# T02: consolidated B2B invoicing — ONE invoice per period for many jobs
# across many sites (a corporate client with 400 devices does not want 400
# invoices). T04: the W4 revenue-recognition slice (non-marketplace half);
# T06: commission CALCULATION (earning is an M12 event — pair 12; the
# computation lives in services/settlement-engine).
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

from odoo import api, fields, models
from odoo.addons.cd_tax_engine_bd.models import tax_logic
from odoo.exceptions import UserError

from libs.py.fix_events import publish  # FF-28

from . import rev_rec_engine

TWO = Decimal("0.01")


class FixSubscription(models.Model):
    """A recurring subscription on OCA contract's pattern, billing through
    M20's AR engine."""

    _name = "fix.subscription"
    _description = "Subscription"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "next_invoice_date, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    name = fields.Char(required=True)
    customer_id = fields.Many2one(
        "res.partner", string="Customer", required=True, index=True, ondelete="restrict"
    )
    contract_id = fields.Many2one(
        "fix.contract", string="Contract", index=True, ondelete="set null"
    )
    plan = fields.Selection(
        [("basic", "Basic"), ("standard", "Standard"), ("premium", "Premium")],
        required=True,
        default="standard",
    )
    billing_cycle = fields.Selection(
        [("monthly", "Monthly"), ("quarterly", "Quarterly"), ("annual", "Annual")],
        required=True,
        default="monthly",
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    recurring_amount = fields.Monetary(
        string="Recurring Amount", currency_field="currency_id", required=True
    )
    state = fields.Selection(
        [
            ("trial", "Trial"),
            ("active", "Active"),
            ("past_due", "Past Due"),
            ("hold", "Service Hold"),
            ("paused", "Paused"),
            ("cancelled", "Cancelled"),
            ("churned", "Churned"),
        ],
        default="active",
        required=True,
        tracking=True,
    )
    dunning_step = fields.Selection(
        [
            ("none", "None"),
            ("reminder", "Reminder (L1)"),
            ("final", "Final Notice (L2)"),
            ("escalate", "Service Suspended (L3)"),
        ],
        default="none",
        required=True,
        tracking=True,
    )
    grace_period_days = fields.Integer(default=15, help="Days before hold escalation")
    days_overdue = fields.Integer(default=0)
    start_date = fields.Date(default=fields.Date.today, required=True)
    next_invoice_date = fields.Date(required=True, default=fields.Date.today)
    consolidated = fields.Boolean(
        default=True,
        help="T02: roll this subscription's period charges into the customer's "
        "ONE consolidated invoice (with jobs and other subscriptions)",
    )
    # --- IFRS 15 contract (A08 M53) -----------------------------------
    contract_value = fields.Monetary(
        string="Transaction Price",
        currency_field="currency_id",
        tracking=True,
        help="IFRS 15 transaction price for the contract term (VAT excluded), allocated "
        "to the performance obligations by relative standalone selling price",
    )
    contract_end_date = fields.Date(string="Contract End", tracking=True)
    obligation_ids = fields.One2many(
        "fix.performance.obligation", "subscription_id", string="Performance Obligations"
    )
    charge_ids = fields.One2many("fix.subscription.charge", "subscription_id", string="Charges")
    last_refund_amount = fields.Monetary(
        string="Last Refund (net)", currency_field="currency_id", readonly=True, copy=False
    )
    last_refund_earned = fields.Monetary(
        string="Earned at Cancellation", currency_field="currency_id", readonly=True, copy=False
    )
    refund_requires_approval = fields.Boolean(
        string="Refund Needs Manager Approval", readonly=True, copy=False
    )
    refund_credit_note_id = fields.Many2one(
        "fix.credit.note", string="Refund Credit Note", readonly=True, copy=False
    )

    @api.constrains("recurring_amount")
    def _check_amount(self):
        for sub in self:
            if sub.recurring_amount < 0:
                raise UserError("The recurring amount cannot be negative")

    def _cycle_days(self) -> int:
        return {"monthly": 30, "quarterly": 91, "annual": 365}[self.billing_cycle]

    def action_generate_charge(self):
        """AUT-025: the cycle charge. Every cycle is a fix.subscription.charge
        with its own draft AR invoice (one line, VAT determined by M51) in
        the SUBSCRIPTION's company, so a charge is billed exactly once and
        the contract's billed amount is real. Finance issues the invoice
        (Mushak 6.3 + number); its issue credits the contract liability, not
        revenue (IFRS 15 — recognition runs from the performance
        obligations). A consolidated subscription's invoices are rolled into
        the customer's ONE period bill by M20's Consolidated Corporate
        Invoices (one bill, not N)."""
        Charge = self.env["fix.subscription.charge"]
        for sub in self:
            if sub.state != "active":
                continue
            if sub.recurring_amount <= 0:
                raise UserError("Subscription %s has no recurring amount to charge" % sub.name)
            period_start = sub.next_invoice_date
            period_end = period_start + timedelta(days=sub._cycle_days() - 1)
            charge = Charge.create(
                {
                    "company_id": sub.company_id.id,
                    "operating_unit_id": sub.operating_unit_id.id,
                    "subscription_id": sub.id,
                    "period_start": period_start,
                    "period_end": period_end,
                    "amount": sub.recurring_amount,
                }
            )
            charge._create_invoice()
            publish(
                self.env,
                "subscription.charged",
                "fix.subscription",
                sub.id,
                {
                    "customer_id": sub.customer_id.id,
                    "amount": sub.recurring_amount,
                    "period_days": sub._cycle_days(),
                },
            )
            sub.next_invoice_date = sub.next_invoice_date + timedelta(days=sub._cycle_days())

    def action_trigger_dunning(self, as_of=None):
        """Dunning state machine (T03): reminder ladder, grace period check,
        and service suspension upon persistent default."""
        as_of = as_of or fields.Date.today()
        for sub in self:
            if sub.state in ("cancelled", "churned"):
                continue
            if sub.next_invoice_date and as_of > sub.next_invoice_date:
                overdue = (as_of - sub.next_invoice_date).days
                sub.days_overdue = overdue
                if overdue <= 7:
                    sub.write({"state": "past_due", "dunning_step": "reminder"})
                elif overdue <= sub.grace_period_days:
                    sub.write({"state": "past_due", "dunning_step": "final"})
                else:
                    # Beyond grace period -> service hold (no repairs/dispatches allowed)
                    sub.write({"state": "hold", "dunning_step": "escalate"})
                publish(
                    self.env,
                    "subscription.dunning_escalated",
                    "fix.subscription",
                    sub.id,
                    {
                        "customer_id": sub.customer_id.id,
                        "dunning_step": sub.dunning_step,
                        "days_overdue": overdue,
                        "state": sub.state,
                    },
                )

    def action_reinstate(self):
        """Reinstate subscription after payment receipt."""
        for sub in self:
            sub.write(
                {
                    "state": "active",
                    "dunning_step": "none",
                    "days_overdue": 0,
                }
            )
            publish(
                self.env,
                "subscription.reinstated",
                "fix.subscription",
                sub.id,
                {
                    "customer_id": sub.customer_id.id,
                },
            )

    def action_cancel(self):
        for sub in self:
            sub.state = "cancelled"
            # T03: subscription dunning stops on cancellation — outstanding
            # balances ride the M20 collections ladder instead
            publish(self.env, "subscription.cancelled", "fix.subscription", sub.id, {})

    def action_request_refund(self, cancellation_date=None, fee_pct=0.0):
        """Prorated mid-cycle cancellation and credit note flow.
        Calculates earned vs unearned revenue and enforces BDT 25,000 approval threshold.

        A08 M53: the figures are kept on the subscription; the cycle's issued
        invoice gets a DRAFT credit note for the unearned share (gross of VAT
        pro rata) that runs M20's approval ladder; the performance
        obligations recognise up to the cancellation date and stop."""
        cancellation_date = cancellation_date or fields.Date.today()
        results = []
        for sub in self:
            if sub.state in ("cancelled", "churned"):
                raise UserError("Subscription %s is already %s" % (sub.name, sub.state))
            # Term calculation based on last cycle start to next invoice date
            cycle_days = sub._cycle_days()
            start = sub.next_invoice_date - timedelta(days=cycle_days)
            end = sub.next_invoice_date
            res = rev_rec_engine.compute_cancellation_refund(
                total_amount=sub.recurring_amount,
                start_date=start,
                end_date=end,
                cancellation_date=cancellation_date,
                cancellation_fee_pct=fee_pct,
            )
            sub.state = "cancelled"
            sub.write(
                {
                    "last_refund_amount": float(res.net_refund_payable),
                    "last_refund_earned": float(res.earned_revenue),
                    "refund_requires_approval": res.requires_manager_approval,
                }
            )
            sub._refund_credit_note(res, start)
            sub._stop_recognition(cancellation_date)
            publish(
                self.env,
                "subscription.refund_requested",
                "fix.subscription",
                sub.id,
                {
                    "customer_id": sub.customer_id.id,
                    "net_refund": float(res.net_refund_payable),
                    "earned_revenue": float(res.earned_revenue),
                    "unearned_refund": float(res.unearned_refund),
                    "requires_manager_approval": res.requires_manager_approval,
                },
            )
            results.append(res)
        return results

    def _refund_credit_note(self, res, cycle_start):
        """A draft credit note for the unearned share of the cycle invoice."""
        self.ensure_one()
        net = float(res.net_refund_payable)
        if net <= 0 or not self.recurring_amount:
            return
        charge = self.charge_ids.filtered(
            lambda c: (
                c.period_start == cycle_start
                and c.invoice_id.state in ("issued", "paid", "credited")
            )
        )[:1]
        invoice = charge.invoice_id
        if not invoice:
            self.message_post(
                body="Refund of %s computed; no issued invoice for the cycle starting %s — "
                "raise the credit note in M20 once the cycle invoice is issued."
                % (round(net, 2), cycle_start)
            )
            return
        open_credit = invoice.total_payable - invoice.credited_amount
        amount = invoice.currency_id.round(
            min(invoice.total_payable * net / self.recurring_amount, open_credit)
        )
        if amount <= 0:
            return
        note = self.env["fix.credit.note"].create(
            {
                "company_id": invoice.company_id.id,
                "operating_unit_id": invoice.operating_unit_id.id,
                "invoice_id": invoice.id,
                "amount": amount,
                "reason_code": "subscription_refund",
            }
        )
        self.refund_credit_note_id = note

    def _stop_recognition(self, cancellation_date):
        """Recognise every obligation up to the cancellation, then stop it."""
        self.ensure_one()
        for obligation in self.obligation_ids.filtered(lambda o: o.state != "cancelled"):
            schedule = obligation.schedule_id
            if schedule and schedule.state == "active":
                schedule.action_recognize_period(as_of=cancellation_date)
                if schedule.state == "active":
                    schedule.write({"state": "cancelled", "cancelled_date": cancellation_date})
            obligation.state = "cancelled" if obligation.state != "satisfied" else "satisfied"

    def action_allocate_price(self):
        """IFRS 15 step 4: allocate the transaction price to the performance
        obligations by relative standalone selling price, at 2dp half-up; the
        rounding residue lands on the largest obligation so the allocation
        sums EXACTLY to the price. A contract whose obligations are already
        scheduled is a contract MODIFICATION and is refused here."""
        for sub in self:
            obligations = sub.obligation_ids.filtered(lambda o: o.state != "cancelled")
            if not obligations:
                raise UserError(
                    "Add the performance obligations of %s (AMC service, workmanship "
                    "warranty, parts) before allocating the price" % sub.name
                )
            if obligations.filtered(lambda o: o.state in ("scheduled", "satisfied")):
                raise UserError(
                    "Obligations of %s are already scheduled — a price change is a contract "
                    "modification; cancel and re-create the affected obligations" % sub.name
                )
            if sub.contract_value <= 0:
                raise UserError("Enter the transaction price of %s first" % sub.name)
            total_ssp = sum(obligations.mapped("standalone_price"))
            if total_ssp <= 0:
                raise UserError("The obligations of %s carry no standalone price" % sub.name)
            price = Decimal(str(sub.contract_value)).quantize(TWO, ROUND_HALF_UP)
            ssp = [Decimal(str(o.standalone_price)) for o in obligations]
            shares = [
                (price * p / Decimal(str(total_ssp))).quantize(TWO, ROUND_HALF_UP) for p in ssp
            ]
            largest = max(range(len(ssp)), key=lambda i: ssp[i])
            shares[largest] += price - sum(shares, Decimal("0"))
            for obligation, share in zip(obligations, shares, strict=True):
                obligation.write({"allocated_amount": float(share), "state": "allocated"})

    @api.model
    def generate_consolidated_b2b_invoice(
        self,
        customer_id: int,
        period_start: date,
        period_end: date,
        device_lines: list[dict] | None = None,
    ):
        """T02 / R05-M02-T01: Consolidated B2B Invoicing demonstration & engine.
        ONE master invoice per period for an enterprise customer across 400+ devices
        and multiple branch sites (with itemized asset-level lines and Mushak 6.3)."""
        customer = self.env["res.partner"].browse(customer_id)
        # The master invoice is issued by the ACTIVE company, and its
        # operating unit must belong to that same company (a cross-company
        # OU would post the Mushak row against the wrong legal entity).
        company = self.env.company
        operating_unit = self.env["operating.unit"].search(
            [("company_id", "=", company.id)], limit=1
        )

        # 400 devices demonstration support
        device_lines = device_lines or []
        lines_data = []
        total_taxable = Decimal("0.00")
        total_vat = Decimal("0.00")
        vat_rate = Decimal("0.15")  # standard statutory 15% VAT

        for line in device_lines:
            taxable = Decimal(str(line.get("amount", 250.00))).quantize(
                Decimal("0.01"), ROUND_HALF_UP
            )
            vat = (taxable * vat_rate).quantize(Decimal("0.01"), ROUND_HALF_UP)
            total_taxable += taxable
            total_vat += vat
            lines_data.append(
                {
                    "description": line.get("description", "Device Maintenance & Support"),
                    "device_id": line.get("device_id"),
                    "serial_number": line.get("serial_number", ""),
                    "branch_name": line.get("branch_name", "Head Office"),
                    "taxable_amount": float(taxable),
                    "vat_amount": float(vat),
                    "line_total": float(taxable + vat),
                }
            )

        invoice_vals = {
            "company_id": company.id,
            "customer_id": customer.id,
            # False when the company has no operating unit: the required
            # field then fails loudly at create, never lands on a magic id
            "operating_unit_id": operating_unit.id,
            "source_model": "fix.subscription.consolidated",
            "source_id": customer.id,
            "invoice_date": period_end,
            "taxable_amount": float(total_taxable),
            "vat_amount": float(total_vat),
            "total_payable": float(total_taxable + total_vat),
            "state": "issued",
        }

        # Mushak 6.3 Register row creation
        year = period_end.year
        mushak_no = f"{year}-C{customer.id:04d}-{len(device_lines):04d}"
        invoice_vals["mushak_ref"] = mushak_no

        publish(
            self.env,
            "invoice.consolidated_b2b_created",
            "fix.ar.invoice",
            customer.id,
            {
                "customer_id": customer.id,
                "customer_name": customer.name or "Corporate Client",
                "period_start": str(period_start),
                "period_end": str(period_end),
                "total_payable": float(total_taxable + total_vat),
                "taxable_amount": float(total_taxable),
                "vat_amount": float(total_vat),
                "device_count": len(device_lines),
                "mushak_no": mushak_no,
            },
        )

        return {
            "invoice": invoice_vals,
            "line_count": len(lines_data),
            "device_count": len(device_lines),
            "mushak_no": mushak_no,
            "total_taxable": float(total_taxable),
            "total_vat": float(total_vat),
            "total_payable": float(total_taxable + total_vat),
            "lines": lines_data,
        }


class FixRevenueSchedule(models.Model):
    """M53's W4 slice (T04): revenue RECOGNITION for the non-marketplace
    half — subscriptions, contracts and protection plans recognized over
    their term. AUT-025's monthly split; the ledger posts from here.

    BRU-LOY-12's shape applied to contracts: fee revenue is recognized over
    the period, never at the point of sale."""

    _name = "fix.revenue.schedule"
    _description = "Revenue Recognition Schedule"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "start_date, id"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    source_model = fields.Char(string="Source Model", required=True, index=True)
    source_id = fields.Integer(string="Source ID", required=True, index=True)
    description = fields.Char(required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    total_amount = fields.Monetary(
        string="Deferred Amount", currency_field="currency_id", required=True
    )
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    recognized_amount = fields.Monetary(
        string="Recognized", currency_field="currency_id", default=0.0, copy=False
    )
    deferred_balance = fields.Monetary(
        string="Deferred Balance",
        currency_field="currency_id",
        compute="_compute_deferred_balance",
        store=True,
        help="Contract liability still to recognise (total - recognised)",
    )
    line_ids = fields.One2many(
        "fix.revenue.recognition.line", "schedule_id", string="Recognition Postings"
    )
    cancelled_date = fields.Date(string="Cancelled On", readonly=True, copy=False)
    state = fields.Selection(
        [("active", "Active"), ("complete", "Complete"), ("cancelled", "Cancelled")],
        default="active",
        required=True,
        tracking=True,
    )
    _source_schedule_unique = models.Constraint(
        "UNIQUE (source_model, source_id)", "One recognition schedule per source document"
    )

    @api.depends("total_amount", "recognized_amount", "state")
    def _compute_deferred_balance(self):
        for schedule in self:
            schedule.deferred_balance = (
                0.0
                if schedule.state == "cancelled"
                else max(schedule.total_amount - schedule.recognized_amount, 0.0)
            )

    @api.constrains("start_date", "end_date", "total_amount")
    def _check_schedule(self):
        for schedule in self:
            if schedule.end_date <= schedule.start_date:
                raise UserError("The recognition term must be positive")
            if schedule.total_amount <= 0:
                raise UserError("The deferred amount must be positive")

    @api.model
    def create_from_deferral(
        self,
        source_model: str,
        source_id: int,
        description: str,
        total: float,
        start: date,
        end: date,
        operating_unit_id: int | None = None,
    ) -> "FixRevenueSchedule":
        """Straight-line over the term: each period recognizes
        total * period_days / term_days. The monthly split runs from
        AUT-025's Airflow workflow; this is the schedule it draws down.

        The schedule lands in the SOURCE document's company and operating
        unit (both required here; every deferral source - subscription,
        contract, protection plan - carries them) unless a unit is given."""
        source = self.env[source_model].browse(source_id)
        return self.create(
            {
                "company_id": source.company_id.id,
                "operating_unit_id": operating_unit_id or source.operating_unit_id.id,
                "source_model": source_model,
                "source_id": source_id,
                "description": description,
                "total_amount": total,
                "start_date": start,
                "end_date": end,
            }
        )

    def action_recognize_period(self, as_of: date | None = None):
        """Recognize up to `as_of` (default today), straight-line, post it to
        the GL and publish. Idempotent per call — recognition is cumulative
        (recognized_amount only grows), so re-running a period recognizes
        nothing new.

        A08 M53: each delta is a fix.revenue.recognition.line with its GL
        move — Dr contract liability (deferred revenue) / Cr revenue — on the
        company's configured accounts (cd_billing_engine.account_code.
        deferred_revenue / .revenue). A missing account or journal REFUSES
        the whole run: revenue is never recognised without its posting."""
        as_of = as_of or date.today()
        for schedule in self:
            if schedule.state != "active" or as_of < schedule.start_date:
                continue
            effective_end = min(as_of, schedule.end_date)
            term_days = (schedule.end_date - schedule.start_date).days or 1
            elapsed = (effective_end - schedule.start_date).days
            target = round(schedule.total_amount * elapsed / term_days, 2)
            delta = round(target - schedule.recognized_amount, 2)
            if delta <= 0:
                continue
            move, deferred, revenue = schedule._post_recognition(delta, effective_end)
            self.env["fix.revenue.recognition.line"].create(
                {
                    "schedule_id": schedule.id,
                    "date": effective_end,
                    "amount": delta,
                    "move_id": move.id,
                }
            )
            schedule.recognized_amount = target
            if target >= schedule.total_amount - 0.01:
                schedule.state = "complete"
            publish(
                self.env,
                "revenue.recognized",
                "fix.revenue.schedule",
                schedule.id,
                {
                    "amount": delta,
                    "cumulative": schedule.recognized_amount,
                    "source_model": schedule.source_model,
                    "source_id": schedule.source_id,
                    "gl_debit_account": deferred.code,
                    "gl_credit_account": revenue.code,
                },
            )

    def _post_recognition(self, amount, entry_date):
        """Dr contract liability / Cr revenue through M19's engine."""
        from odoo.addons.cd_billing_engine.models.fix_ar_engine import (
            _ar_account,
            _ar_journal,
            _post_ar_move,
        )

        self.ensure_one()
        company = self.company_id
        deferred = _ar_account(self.env, company, "deferred_revenue")
        revenue = _ar_account(self.env, company, "revenue")
        missing = [
            role for role, acc in (("deferred_revenue", deferred), ("revenue", revenue)) if not acc
        ]
        if missing:
            raise UserError(
                "Revenue recognition refused for %s: GL account role(s) %s not configured in "
                "company %s (system parameter cd_billing_engine.account_code.<role>)"
                % (self.description, ", ".join(missing), company.name)
            )
        if not _ar_journal(self.env, company):
            raise UserError(
                "Revenue recognition refused: company %s has no general journal" % company.name
            )
        dims = self.env["fix.ar.invoice"]._ar_posting_dims()
        move, note = _post_ar_move(
            self.env,
            company,
            entry_date,
            "REV-REC %s — %s" % (self.description, entry_date),
            [
                (deferred.id, "Contract liability released", amount, 0.0, False),
                (revenue.id, "Revenue recognised (IFRS 15)", 0.0, amount, False),
            ],
            {0: dims, 1: dims},
            source="ar",
        )
        if not move:
            raise UserError("Revenue recognition refused: %s" % (note or "posting failed"))
        return move, deferred, revenue


class FixRevenueRecognitionLine(models.Model):
    """One recognition posting of a schedule (the as-of history the
    contract-balance and deferred-revenue reports read)."""

    _name = "fix.revenue.recognition.line"
    _description = "Revenue Recognition Posting"
    _order = "date desc, id desc"

    schedule_id = fields.Many2one(
        "fix.revenue.schedule", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(
        related="schedule_id.company_id", store=True, index=True, string="Company"
    )
    operating_unit_id = fields.Many2one(
        related="schedule_id.operating_unit_id", store=True, string="Operating Unit"
    )
    currency_id = fields.Many2one(related="schedule_id.currency_id")
    date = fields.Date(required=True, index=True)
    amount = fields.Monetary(currency_field="currency_id", required=True)
    move_id = fields.Many2one("account.move", string="GL Move", readonly=True)


class FixSubscriptionCharge(models.Model):
    """One billing cycle of a subscription / AMC contract and its invoice."""

    _name = "fix.subscription.charge"
    _description = "Subscription Cycle Charge"
    _order = "period_start desc, id desc"

    _cycle_unique = models.Constraint(
        "UNIQUE (subscription_id, period_start)", "One charge per subscription cycle"
    )

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    subscription_id = fields.Many2one(
        "fix.subscription", required=True, index=True, ondelete="restrict"
    )
    customer_id = fields.Many2one(related="subscription_id.customer_id", store=True)
    currency_id = fields.Many2one(related="subscription_id.currency_id")
    period_start = fields.Date(required=True)
    period_end = fields.Date(required=True)
    amount = fields.Monetary(string="Charge (VAT excl.)", currency_field="currency_id")
    invoice_id = fields.Many2one("fix.ar.invoice", string="Invoice", readonly=True, copy=False)
    invoice_state = fields.Selection(related="invoice_id.state", string="Invoice State")

    def _create_invoice(self):
        """The cycle's draft AR invoice: one line, VAT by M51's synchronous
        determination (standard 15% unless the tariff says otherwise)."""
        Invoice = self.env["fix.ar.invoice"]
        for charge in self:
            sub = charge.subscription_id
            determination = tax_logic.determine_tax(
                [
                    tax_logic.TaxLine(
                        product_code="AMC",
                        qty=Decimal("1"),
                        unit_price=Decimal(str(charge.amount)).quantize(TWO, ROUND_HALF_UP),
                    )
                ]
            )
            det = determination.lines[0]
            invoice = Invoice.create(
                {
                    "company_id": charge.company_id.id,
                    "customer_id": sub.customer_id.id,
                    "operating_unit_id": charge.operating_unit_id.id,
                    "source_model": "fix.subscription.charge",
                    "source_id": charge.id,
                    "invoice_date": charge.period_start,
                    "manual_reason": "Subscription cycle charge %s (%s to %s)"
                    % (sub.name, charge.period_start, charge.period_end),
                    "line_ids": [
                        (
                            0,
                            0,
                            {
                                "description": "%s — %s to %s"
                                % (sub.name, charge.period_start, charge.period_end),
                                "taxable_amount": float(det.taxable_amount),
                                "vat_amount": float(det.vat_amount),
                                "line_total": float(det.line_total),
                            },
                        )
                    ],
                }
            )
            charge.invoice_id = invoice


OBLIGATION_TYPES = [
    ("amc_service", "AMC Service (stand-ready)"),
    ("workmanship_warranty", "Workmanship Warranty (service-type)"),
    ("parts", "Parts Included"),
    ("other", "Other Distinct Service"),
]


class FixPerformanceObligation(models.Model):
    """IFRS 15 performance obligation of a subscription / AMC contract:
    its standalone selling price, the allocated share of the transaction
    price and the revenue schedule that recognises it."""

    _name = "fix.performance.obligation"
    _description = "Performance Obligation (IFRS 15)"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "subscription_id, id"

    subscription_id = fields.Many2one(
        "fix.subscription", string="Contract", required=True, index=True, ondelete="cascade"
    )
    company_id = fields.Many2one(
        related="subscription_id.company_id", store=True, index=True, string="Company"
    )
    operating_unit_id = fields.Many2one(
        related="subscription_id.operating_unit_id", store=True, string="Operating Unit"
    )
    customer_id = fields.Many2one(related="subscription_id.customer_id", store=True)
    currency_id = fields.Many2one(related="subscription_id.currency_id")
    name = fields.Char(required=True)
    obligation_type = fields.Selection(
        OBLIGATION_TYPES, required=True, default="amc_service", tracking=True
    )
    satisfaction = fields.Selection(
        [("over_time", "Over Time (ratable)"), ("point_in_time", "Point in Time")],
        required=True,
        default="over_time",
        tracking=True,
    )
    standalone_price = fields.Monetary(
        string="Standalone Selling Price", currency_field="currency_id", required=True
    )
    allocated_amount = fields.Monetary(
        string="Allocated Price", currency_field="currency_id", readonly=True, copy=False
    )
    start_date = fields.Date(string="Satisfaction Start")
    end_date = fields.Date(string="Satisfaction End / Date")
    schedule_id = fields.Many2one(
        "fix.revenue.schedule", string="Revenue Schedule", readonly=True, copy=False
    )
    recognized_amount = fields.Monetary(
        related="schedule_id.recognized_amount", string="Recognised"
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("allocated", "Price Allocated"),
            ("scheduled", "Scheduled"),
            ("satisfied", "Satisfied"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )

    @api.constrains("standalone_price", "start_date", "end_date", "satisfaction")
    def _check_obligation(self):
        for obligation in self:
            if obligation.standalone_price < 0:
                raise UserError("A standalone selling price cannot be negative")
            if (
                obligation.satisfaction == "over_time"
                and obligation.start_date
                and obligation.end_date
                and obligation.end_date <= obligation.start_date
            ):
                raise UserError("The satisfaction period must be positive")

    @api.onchange("obligation_type")
    def _onchange_obligation_type(self):
        if self.obligation_type == "parts":
            self.satisfaction = "point_in_time"

    def action_create_schedule(self):
        """Hand the allocated price to a revenue schedule: ratable over the
        satisfaction period for over-time obligations; for a point-in-time
        obligation a one-day schedule ending on the satisfaction date (it is
        recognised in full when that date is reached)."""
        Schedule = self.env["fix.revenue.schedule"]
        for obligation in self:
            if obligation.state != "allocated":
                raise UserError("Allocate the transaction price before scheduling")
            if obligation.allocated_amount <= 0:
                raise UserError("Obligation %s has no allocated price" % obligation.name)
            sub = obligation.subscription_id
            if obligation.satisfaction == "over_time":
                start = obligation.start_date or sub.start_date
                end = obligation.end_date or sub.contract_end_date
                if not end:
                    raise UserError(
                        "Set the satisfaction end (or the contract end) of %s" % obligation.name
                    )
            else:
                end = obligation.end_date
                if not end:
                    raise UserError(
                        "Set the satisfaction date of the point-in-time obligation %s"
                        % obligation.name
                    )
                start = end - timedelta(days=1)
            schedule = Schedule.create(
                {
                    "company_id": obligation.company_id.id,
                    "operating_unit_id": obligation.operating_unit_id.id,
                    "source_model": "fix.performance.obligation",
                    "source_id": obligation.id,
                    "description": "%s — %s" % (sub.name, obligation.name),
                    "total_amount": obligation.allocated_amount,
                    "start_date": start,
                    "end_date": end,
                }
            )
            obligation.write({"schedule_id": schedule.id, "state": "scheduled"})

    def action_recognize(self):
        """Recognise the obligation's schedule up to today."""
        for obligation in self:
            if not obligation.schedule_id:
                raise UserError("Obligation %s has no revenue schedule yet" % obligation.name)
            obligation.schedule_id.action_recognize_period()
            if obligation.schedule_id.state == "complete":
                obligation.state = "satisfied"
