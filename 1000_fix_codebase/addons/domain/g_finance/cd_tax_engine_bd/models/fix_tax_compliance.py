# cd_tax_engine_bd — A08 M51 compliance records (CD-M51-01): TDS/VDS
# deduction lines, treasury challans, input VAT credit tracking, the audit
# support pack, and the argument-free preparation of the 9.1 / quarterly
# withholding returns the workspace calls.
#
# Nothing here invents a figure: deductions come from the AP sub-ledger
# (cd_ap_ext creates them on bill approval), challan numbers and dates are
# typed by the user from the bank's A-challan / e-payment receipt, and the
# returns sum the ERP's own registers.
import base64
import csv
import hashlib
import io
import json
import re
import zipfile
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

from . import return_logic
from .fix_tax_master import add_months, period_of, tax_account

TWO = Decimal("0.01")
PERIOD_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
QUARTER_RE = re.compile(r"^\d{4}-Q[1-4]$")
ITA_SECTIONS = ("89", "90", "94", "109")


def money(value):
    return float(Decimal(str(value or 0)).quantize(TWO, ROUND_HALF_UP))


def quarter_bounds(quarter):
    """[start, end] dates of a TDS-return quarter label (FY-start year):
    2026-Q1 = Jul-Sep 2026, 2026-Q2 = Oct-Dec 2026, 2026-Q3 = Jan-Mar 2027."""
    fy_start, q = int(quarter[:4]), int(quarter[-1])
    year, month = add_months(fy_start, 7, 3 * (q - 1))
    ey, em = add_months(year, month, 3)
    return date(year, month, 1), date(ey, em, 1) - timedelta(days=1)


def _journal_account(env, company, param):
    """The default account of the bank journal configured under ``param``."""
    code = env["ir.config_parameter"].sudo().get_param(param)
    journal = env["account.journal"]
    if code:
        journal = journal.search(
            [
                ("company_id", "=", company.id),
                ("code", "=", code),
                ("type", "in", ("bank", "cash")),
            ],
            limit=1,
        )
    if not journal or not journal.default_account_id:
        raise UserError(
            "No bank journal configured for this posting in %s: set system parameter %s "
            "to the code of the bank/cash journal the money leaves from. Nothing was posted."
            % (company.name, param)
        )
    return journal


def post_tax_move(
    env, company, journal, entry_date, ref, lines, operating_unit=None, source="tax_subledger"
):
    """Post a balanced entry through M19's hardened engine (dimensions, chart
    rules, posting log). lines: [(account, label, debit, credit, partner|False)]."""
    from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions

    debit = round(sum(line[2] for line in lines), 2)
    credit = round(sum(line[3] for line in lines), 2)
    if abs(debit - credit) > 0.005:
        raise UserError("Unbalanced posting refused (%.2f / %.2f)" % (debit, credit))
    ou = operating_unit or env["operating.unit"].search([("company_id", "=", company.id)], limit=1)
    move_vals = {
        "journal_id": journal.id,
        "company_id": company.id,
        "date": entry_date,
        "ref": ref,
        "move_type": "entry",
        "line_ids": [
            (
                0,
                0,
                {
                    "account_id": account.id,
                    "name": label,
                    "debit": round(dr, 2),
                    "credit": round(cr, 2),
                    "partner_id": partner.id if partner else False,
                },
            )
            for account, label, dr, cr, partner in lines
            if round(dr, 2) or round(cr, 2)
        ],
    }
    dims = (
        {i: {"operating_unit_id": ou.id} for i in range(len(move_vals["line_ids"]))} if ou else {}
    )
    move, _dims = post_with_dimensions(env, move_vals, dims, source=source)
    return move


class FixWithholdingLine(models.Model):
    """One TDS or VDS deduction: who, on what base, at which effective-dated
    rate (with the ITA 2023 section / VAT service code), and where the money
    went (challan) and which certificate covers it."""

    _name = "fix.withholding.line"
    _description = "TDS / VDS Deduction"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "document_date desc, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", index=True)
    tax_kind = fields.Selection(
        [("tds", "TDS"), ("vds", "VDS")], string="Tax", required=True, index=True
    )
    partner_id = fields.Many2one(
        "res.partner", string="Deductee", required=True, index=True, ondelete="restrict"
    )
    partner_tin = fields.Char(string="Deductee TIN", size=12)
    partner_bin = fields.Char(string="Deductee BIN", size=13)
    rate_id = fields.Many2one("fix.tax.rate", string="Rate Row", required=True, ondelete="restrict")
    section = fields.Char(string="Section / Service Code", readonly=True)
    document_date = fields.Date(required=True, index=True)
    period = fields.Char(compute="_compute_period", store=True, index=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    base_amount = fields.Monetary(string="Base", currency_field="currency_id", required=True)
    rate = fields.Float(string="Statutory Rate (%)", digits=(6, 3), required=True)
    # ITA 2023: three independent defaults each raise the withholding rate by 50%
    # (s.142 proof-of-submission of return, s.143/163 no TIN, and the non-bank
    # payment rule). They are recorded separately so the certificate can state
    # which default raised the rate.
    psr_received = fields.Boolean(
        string="PSR on file",
        default=True,
        help="Proof of Submission of Return held on the document date (s.142). "
        "Missing PSR raises the rate by 50%.",
    )
    paid_by_bank = fields.Boolean(
        string="Paid through bank",
        default=True,
        help="Payment made by bank transfer/cheque. A cash payment raises the rate by 50%.",
    )
    payee_has_tin = fields.Boolean(
        string="Payee has TIN",
        compute="_compute_payee_has_tin",
        store=True,
        help="Derived from the deductee TIN (s.143/163).",
    )
    non_filer = fields.Boolean(
        string="Non-filer", help="Kept for the older rows: equivalent to missing PSR."
    )
    defaults_count = fields.Integer(
        string="Statutory defaults",
        compute="_compute_uplift",
        store=True,
        help="Number of independent defaults applied to this deduction.",
    )
    multiplier = fields.Float(
        string="Multiplier",
        digits=(6, 3),
        default=1.0,
        help="1.5 per default (PSR missing / cash payment / no TIN), per ITA 2023. "
        "Defaulted from the flags on create; a document may state a higher one.",
    )
    effective_rate = fields.Float(
        string="Effective rate (%)", digits=(6, 3), compute="_compute_uplift", store=True
    )
    expected_amount = fields.Monetary(
        string="Expected deduction",
        currency_field="currency_id",
        compute="_compute_uplift",
        store=True,
    )
    amount = fields.Monetary(string="Deducted", currency_field="currency_id", required=True)
    source_ref = fields.Char(string="Source Document", index=True)
    state = fields.Selection(
        [
            ("withheld", "Withheld"),
            ("deposited", "Deposited"),
            ("certified", "Certificate Issued"),
            ("cancelled", "Cancelled"),
        ],
        default="withheld",
        required=True,
        tracking=True,
    )
    challan_id = fields.Many2one(
        "fix.tax.challan", string="Challan", index=True, ondelete="restrict", copy=False
    )
    challan_no = fields.Char(related="challan_id.challan_no", string="Challan No")
    challan_date = fields.Date(related="challan_id.challan_date", string="Challan Date")
    certificate_id = fields.Many2one(
        "fix.withholding.certificate", string="Certificate", readonly=True, copy=False
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "multiplier" not in vals:
                defaults = 0
                if vals.get("psr_received") is False or vals.get("non_filer"):
                    defaults += 1
                if vals.get("paid_by_bank") is False:
                    defaults += 1
                if not (vals.get("partner_tin") or "").strip():
                    defaults += 1
                vals["multiplier"] = round(1.5**defaults, 3)
        return super().create(vals_list)

    @api.depends("partner_tin")
    def _compute_payee_has_tin(self):
        for line in self:
            line.payee_has_tin = bool((line.partner_tin or "").strip())

    @api.depends(
        "rate",
        "base_amount",
        "multiplier",
        "psr_received",
        "paid_by_bank",
        "partner_tin",
        "non_filer",
    )
    def _compute_uplift(self):
        """ITA 2023: each of the three defaults multiplies the statutory rate by 1.5.
        The components stay visible so the certificate and the register can state
        exactly which default applied."""
        for line in self:
            defaults = 0
            if not line.psr_received or line.non_filer:
                defaults += 1
            if not line.paid_by_bank:
                defaults += 1
            if not (line.partner_tin or "").strip():
                defaults += 1
            line.defaults_count = defaults
            line.effective_rate = round((line.rate or 0.0) * (line.multiplier or 1.0), 3)
            line.expected_amount = round((line.base_amount or 0.0) * line.effective_rate / 100.0, 2)
            shortfall = round(line.expected_amount - (line.amount or 0.0), 2)
            line.statutory_shortfall = shortfall if shortfall > 0.5 else 0.0

    statutory_shortfall = fields.Monetary(
        string="Statutory shortfall",
        currency_field="currency_id",
        compute="_compute_uplift",
        store=True,
        help="Expected deduction minus the amount actually withheld. A positive value is "
        "under-withholding the company remains liable for.",
    )

    @api.constrains("amount", "expected_amount", "multiplier", "defaults_count")
    def _check_statutory_amount(self):
        """New deductions must equal base x effective rate and may not use a multiplier
        below 1.5 per recorded default. Historical rows that breach the floor are NOT
        refused here (that would block an upgrade); they carry a statutory_shortfall and
        the register reports them for remediation."""
        for line in self:
            if line.state == "cancelled":
                continue
            if line.env.context.get("statutory_remediation"):
                continue
            minimum = round(1.5 ** (line.defaults_count or 0), 3)
            if (line.multiplier or 1.0) < minimum - 1e-6:
                continue  # legacy row: surfaced as a shortfall, fixed by the action
            if abs((line.amount or 0.0) - (line.expected_amount or 0.0)) > 0.51:
                raise ValidationError(
                    "Deducted %.2f but the statutory amount is %.2f "
                    "(rate %.3f%% x multiplier %.3f). Correct the amount or the flags."
                    % (
                        line.amount or 0.0,
                        line.expected_amount or 0.0,
                        line.effective_rate or 0.0,
                        line.multiplier or 1.0,
                    )
                )

    def action_apply_statutory_uplift(self):
        """Remediate a legacy under-withheld row: set the multiplier to the statutory
        minimum for its recorded defaults and recompute the withheld amount."""
        for line in self:
            minimum = round(1.5 ** (line.defaults_count or 0), 3)
            amount = round((line.base_amount or 0.0) * (line.rate or 0.0) * minimum / 100.0, 2)
            line.with_context(statutory_remediation=True).write(
                {"multiplier": minimum, "amount": amount}
            )

    @api.depends("document_date")
    def _compute_period(self):
        for line in self:
            line.period = period_of(line.document_date)

    @api.constrains("base_amount", "amount", "rate", "multiplier")
    def _check_amounts(self):
        for line in self:
            if line.base_amount < 0 or line.amount < 0:
                raise ValidationError("A deduction cannot be negative")
            if line.amount > line.base_amount + 0.005:
                raise ValidationError("A deduction cannot exceed its base")
            if line.multiplier < 1:
                raise ValidationError("The multiplier is at least 1")

    def _certificate_vals(self):
        """Values of the deductee certificate (extended by cd_ap_ext with
        the vendor-invoice pointer)."""
        self.ensure_one()
        partner = self.partner_id
        return {
            "company_id": self.company_id.id,
            "operating_unit_id": self.operating_unit_id.id,
            "currency_id": self.currency_id.id,
            "certificate_type": "mushak_6_6" if self.tax_kind == "vds" else "section_52_income_tax",
            "supplier_name": partner.name,
            "supplier_bin": self.partner_bin or False,
            "supplier_tin": self.partner_tin or False,
            "supplier_address": partner.contact_address or False,
            "base_amount": self.base_amount,
            "rate_percent": self.rate * self.multiplier,
            "withheld_amount": self.amount,
            "challan_no": self.challan_id.challan_no,
            "challan_date": self.challan_id.challan_date,
            "bank_branch": " / ".join(
                p for p in (self.challan_id.bank_name, self.challan_id.bank_branch) if p
            )
            or False,
        }

    def action_issue_certificate(self):
        """Issue the deductee certificate (Mushak 6.6 for VDS, the income-tax
        withholding certificate for TDS) — only once the money is deposited:
        the certificate states the challan."""
        for line in self:
            if line.state != "deposited":
                raise UserError(
                    "Deduction %s is %s — a certificate is issued after the challan deposit"
                    % (line.source_ref or line.id, line.state)
                )
            cert = self.env["fix.withholding.certificate"].create(line._certificate_vals())
            cert.action_issue()
            line.write({"certificate_id": cert.id, "state": "certified"})
        return True


class FixTaxChallan(models.Model):
    """A-challan / e-payment deposit settling VAT, TDS or VDS liabilities.
    The challan number and date come from the bank receipt (user-entered)."""

    _name = "fix.tax.challan"
    _description = "Tax Challan (A-Challan / e-Payment)"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "challan_date desc, id desc"
    _challan_no_unique = models.Constraint(
        "UNIQUE (company_id, challan_no)", "This challan number is already recorded"
    )

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", index=True)
    challan_no = fields.Char(string="Challan No", required=True, tracking=True, copy=False)
    challan_date = fields.Date(string="Deposit Date", required=True, tracking=True)
    payment_mode = fields.Selection(
        [("a_challan", "A-Challan (iBAS++)"), ("e_payment", "e-Payment (RTGS)")],
        default="a_challan",
        required=True,
    )
    tax_kind = fields.Selection(
        [("vat", "VAT (Mushak 9.1)"), ("tds", "TDS"), ("vds", "VDS")],
        string="Tax",
        required=True,
        tracking=True,
    )
    period = fields.Char(help="YYYY-MM — the withholding / VAT period the deposit settles")
    bank_name = fields.Char()
    bank_branch = fields.Char()
    economic_code = fields.Char(
        string="Economic / Revenue Code", help="As printed on the A-challan (user-entered)"
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount = fields.Monetary(string="Deposited", currency_field="currency_id", required=True)
    withholding_line_ids = fields.One2many(
        "fix.withholding.line", "challan_id", string="Deductions Settled"
    )
    vat_return_id = fields.Many2one("fix.vat.return", string="VAT Return (9.1)")
    liability_total = fields.Monetary(
        string="Liabilities Linked", currency_field="currency_id", compute="_compute_liability"
    )
    state = fields.Selection(
        [("draft", "Draft"), ("deposited", "Deposited & Posted"), ("cancelled", "Cancelled")],
        default="draft",
        required=True,
        tracking=True,
    )
    move_id = fields.Many2one("account.move", string="GL Entry", readonly=True, copy=False)

    @api.depends("tax_kind", "withholding_line_ids.amount", "vat_return_id.net_payable")
    def _compute_liability(self):
        for ch in self:
            if ch.tax_kind == "vat":
                ch.liability_total = ch.vat_return_id.net_payable
            else:
                ch.liability_total = sum(ch.withholding_line_ids.mapped("amount"))

    @api.constrains("period", "amount")
    def _check_challan(self):
        for ch in self:
            if ch.period and not PERIOD_RE.match(ch.period):
                raise ValidationError("Period must be YYYY-MM")
            if ch.amount <= 0:
                raise ValidationError("A challan deposits a positive amount")

    def action_link_open_deductions(self):
        """Link every withheld, undeposited deduction of the challan's tax and
        period (the usual monthly deposit)."""
        for ch in self:
            if ch.state != "draft" or ch.tax_kind == "vat":
                raise UserError("Only a draft TDS/VDS challan links deductions")
            if not ch.period:
                raise UserError("Set the period (YYYY-MM) the challan settles first")
            open_lines = self.env["fix.withholding.line"].search(
                [
                    ("company_id", "=", ch.company_id.id),
                    ("tax_kind", "=", ch.tax_kind),
                    ("period", "=", ch.period),
                    ("state", "=", "withheld"),
                    ("challan_id", "=", False),
                ]
            )
            if not open_lines:
                raise UserError(
                    "No undeposited %s deductions in %s" % (ch.tax_kind.upper(), ch.period)
                )
            open_lines.write({"challan_id": ch.id})
        return True

    def action_confirm_deposit(self):
        """Confirm the deposit: the challan must settle exactly the linked
        liabilities; posts Dr tax liability / Cr bank and marks the
        deductions deposited. Fails closed on any missing configuration."""
        for ch in self:
            if ch.state != "draft":
                raise UserError("Challan %s is already %s" % (ch.challan_no, ch.state))
            company = ch.company_id
            if ch.tax_kind == "vat":
                ret = ch.vat_return_id
                if not ret or ret.state not in ("prepared", "filed"):
                    raise UserError("A VAT challan settles a prepared Mushak 9.1 return")
                role, partner_lines = "vat_output", None
            else:
                lines = ch.withholding_line_ids
                if not lines:
                    raise UserError("Link the deductions this challan settles first")
                bad = lines.filtered(
                    lambda line, kind=ch.tax_kind, comp=company: (
                        line.state != "withheld" or line.tax_kind != kind or line.company_id != comp
                    )
                )
                if bad:
                    raise UserError(
                        "Only withheld, undeposited %s deductions of %s can be settled"
                        % (ch.tax_kind.upper(), company.name)
                    )
                role, partner_lines = "%s_payable" % ch.tax_kind, lines
            if abs(money(ch.amount) - money(ch.liability_total)) > 0.005:
                raise UserError(
                    "Challan amount %.2f does not equal the liabilities it settles (%.2f)"
                    % (ch.amount, ch.liability_total)
                )
            liability = tax_account(self.env, company, role)
            journal = _journal_account(self.env, company, "cd_tax_engine_bd.challan_journal_code")
            label = "%s challan %s" % (ch.tax_kind.upper(), ch.challan_no)
            move = post_tax_move(
                self.env,
                company,
                journal,
                ch.challan_date,
                label,
                [
                    (liability, label, money(ch.amount), 0.0, False),
                    (journal.default_account_id, label, 0.0, money(ch.amount), False),
                ],
                ch.operating_unit_id,
            )
            if partner_lines:
                partner_lines.write({"state": "deposited"})
            ch.write({"state": "deposited", "move_id": move.id})
            publish(
                self.env,
                "tax_challan.deposited",
                "fix.tax.challan",
                ch.id,
                {
                    "challan_no": ch.challan_no,
                    "tax_kind": ch.tax_kind,
                    "amount": money(ch.amount),
                    "period": ch.period or "",
                },
            )
        return True


class FixInputVatCredit(models.Model):
    """Input VAT on a purchase (the Mushak 6.1 side): the supplier's 6.3,
    its eligibility for credit and the 9.1 period it is claimed in."""

    _name = "fix.input.vat.credit"
    _description = "Input VAT Credit (Mushak 6.1)"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "invoice_date desc, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", index=True)
    partner_id = fields.Many2one(
        "res.partner", string="Supplier", required=True, index=True, ondelete="restrict"
    )
    supplier_bin = fields.Char(string="Supplier BIN", size=13)
    supplier_mushak_no = fields.Char(string="Supplier Mushak 6.3 No")
    supplier_enlisted = fields.Boolean(
        string="Supplier Turnover-Tax Enlisted",
        help="An enlisted (not VAT-registered) supplier's invoice does not support input credit",
    )
    invoice_date = fields.Date(required=True, index=True)
    invoice_period = fields.Char(compute="_compute_invoice_period", store=True, index=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    taxable_amount = fields.Monetary(string="Taxable Value", currency_field="currency_id")
    vat_amount = fields.Monetary(string="Input VAT", currency_field="currency_id", required=True)
    adjustment_type = fields.Selection(
        [
            ("invoice", "Purchase invoice (6.3)"),
            ("increase", "Increasing adjustment (debit note 6.8)"),
            ("decrease", "Decreasing adjustment (credit note 6.7)"),
        ],
        default="invoice",
        required=True,
        help="A decreasing adjustment REDUCES the input VAT of the period it falls in",
    )
    signed_vat = fields.Monetary(
        string="Input VAT Effect",
        currency_field="currency_id",
        compute="_compute_signed",
        store=True,
    )
    source_ref = fields.Char(string="Source Document", index=True)
    claim_period = fields.Char(
        string="Claim Period", help="YYYY-MM — the Mushak 9.1 period the credit is claimed in"
    )
    claim_deadline = fields.Char(
        string="Last Claim Period", compute="_compute_deadline", store=True
    )
    state = fields.Selection(
        [
            ("pending", "Pending Check"),
            ("eligible", "Eligible"),
            ("claimed", "Claimed in 9.1"),
            ("ineligible", "Ineligible"),
        ],
        default="pending",
        required=True,
        tracking=True,
    )
    ineligible_reason = fields.Char(readonly=True)
    vat_return_id = fields.Many2one("fix.vat.return", string="Claimed In", readonly=True)

    @api.depends("vat_amount", "adjustment_type")
    def _compute_signed(self):
        for row in self:
            row.signed_vat = (
                -row.vat_amount if row.adjustment_type == "decrease" else row.vat_amount
            )

    @api.depends("invoice_date")
    def _compute_invoice_period(self):
        for row in self:
            row.invoice_period = period_of(row.invoice_date)

    @api.depends("invoice_date", "company_id")
    def _compute_deadline(self):
        Param = self.env["fix.tax.parameter"]
        for row in self:
            if not row.invoice_date:
                row.claim_deadline = False
                continue
            try:
                window = int(
                    Param.get_value("input_credit_window_periods", row.invoice_date, row.company_id)
                )
            except UserError:
                row.claim_deadline = False
                continue
            y, m = add_months(row.invoice_date.year, row.invoice_date.month, window)
            row.claim_deadline = "%04d-%02d" % (y, m)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("claim_period") and vals.get("invoice_date"):
                vals["claim_period"] = str(vals["invoice_date"])[:7]
        return super().create(vals_list)

    @api.constrains("claim_period", "invoice_date", "vat_amount", "adjustment_type")
    def _check_claim(self):
        for row in self:
            if row.vat_amount < 0:
                raise ValidationError("Input VAT cannot be negative")
            if row.claim_period:
                if not PERIOD_RE.match(row.claim_period):
                    raise ValidationError("Claim period must be YYYY-MM")
                if row.claim_period < row.invoice_period:
                    raise ValidationError("Input VAT cannot be claimed before the invoice period")
                if row.adjustment_type == "decrease" and row.claim_period != row.invoice_period:
                    raise ValidationError(
                        "A decreasing adjustment belongs to the 9.1 of its own period"
                    )
                if row.claim_deadline and row.claim_period > row.claim_deadline:
                    raise ValidationError(
                        "Claim period %s is after the last allowed period %s (statutory "
                        "parameter input_credit_window_periods)"
                        % (row.claim_period, row.claim_deadline)
                    )

    def _ineligibility(self):
        """The reason this credit cannot be claimed, or '' when it can."""
        self.ensure_one()
        if self.adjustment_type == "decrease":
            return ""  # a decreasing adjustment is always reported, never optional
        if self.vat_amount <= 0:
            return "No input VAT on the invoice"
        if not re.fullmatch(r"\d{13}", (self.supplier_bin or "").strip()):
            return "Supplier BIN missing or not 13 digits"
        if not (self.supplier_mushak_no or "").strip():
            return "Supplier Mushak 6.3 number missing"
        if self.supplier_enlisted:
            return "Supplier is turnover-tax enlisted, not VAT-registered"
        return ""

    def action_check_eligibility(self):
        for row in self:
            if row.state == "claimed":
                raise UserError("A claimed credit is part of a 9.1 return — not re-checked")
            reason = row._ineligibility()
            row.write(
                {
                    "state": "ineligible" if reason else "eligible",
                    "ineligible_reason": reason or False,
                }
            )
        return True


class FixTaxAuditPack(models.Model):
    """Audit Support Pack: the period's statutory registers exported as CSV,
    with a manifest of SHA-256 checksums, stored as one immutable ZIP
    attachment. action_verify re-checks the stored bundle."""

    _name = "fix.tax.audit.pack"
    _description = "Tax Audit Support Pack"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_to desc, id desc"

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit")
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("generated", "Generated")],
        default="draft",
        required=True,
        tracking=True,
    )
    attachment_id = fields.Many2one("ir.attachment", string="Bundle (ZIP)", readonly=True)
    manifest = fields.Text(readonly=True)
    pack_sha256 = fields.Char(string="Bundle SHA-256", readonly=True)
    file_count = fields.Integer(readonly=True)
    generated_at = fields.Datetime(readonly=True)
    generated_by = fields.Many2one("res.users", readonly=True)
    integrity_status = fields.Selection(
        [("unchecked", "Unchecked"), ("intact", "Intact"), ("tampered", "Checksum Mismatch")],
        default="unchecked",
        readonly=True,
        tracking=True,
    )

    @api.depends("date_from", "date_to")
    def _compute_name(self):
        for pack in self:
            pack.name = "Tax audit pack %s .. %s" % (pack.date_from or "", pack.date_to or "")

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for pack in self:
            if pack.date_to < pack.date_from:
                raise ValidationError("The pack period ends before it starts")

    def _periods(self):
        """YYYY-MM keys and quarter labels the pack period touches."""
        self.ensure_one()
        months, quarters = [], []
        y, m = self.date_from.year, self.date_from.month
        while date(y, m, 1) <= self.date_to:
            months.append("%04d-%02d" % (y, m))
            q = return_logic.tds_quarter_for_date(date(y, m, 1))[0]
            if q not in quarters:
                quarters.append(q)
            y, m = add_months(y, m, 1)
        return months, quarters

    def _pack_sections(self):
        """[(file name, model, domain, field names)] — extended by cd_ap_ext."""
        self.ensure_one()
        c = [("company_id", "=", self.company_id.id)]
        rng = lambda f: [(f, ">=", self.date_from), (f, "<=", self.date_to)]  # noqa: E731
        months, quarters = self._periods()
        return [
            (
                "mushak_6_2_sales_register.csv",
                "fix.mushak.register",
                c + rng("invoice_date"),
                [
                    "mushak_no",
                    "invoice_ref",
                    "invoice_date",
                    "customer_name",
                    "customer_bin",
                    "taxable_amount",
                    "vat_amount",
                    "total_payable",
                    "posted",
                ],
            ),
            (
                "mushak_6_1_purchase_register.csv",
                "fix.input.vat.credit",
                c + rng("invoice_date"),
                [
                    "partner_id",
                    "supplier_bin",
                    "supplier_mushak_no",
                    "invoice_date",
                    "taxable_amount",
                    "vat_amount",
                    "state",
                    "claim_period",
                    "source_ref",
                ],
            ),
            (
                "mushak_9_1_returns.csv",
                "fix.vat.return",
                [*c, ("period", "in", months)],
                [
                    "period",
                    "total_taxable",
                    "output_vat",
                    "input_vat",
                    "vds_received_credit",
                    "net_payable",
                    "due_date",
                    "state",
                    "filed_at",
                    "nbr_confirmation",
                    "subledger_status",
                ],
            ),
            (
                "withholding_deductions.csv",
                "fix.withholding.line",
                c + rng("document_date"),
                [
                    "tax_kind",
                    "partner_id",
                    "partner_tin",
                    "partner_bin",
                    "section",
                    "document_date",
                    "base_amount",
                    "rate",
                    "multiplier",
                    "amount",
                    "state",
                    "challan_no",
                    "source_ref",
                ],
            ),
            (
                "tax_challans.csv",
                "fix.tax.challan",
                c + rng("challan_date"),
                [
                    "challan_no",
                    "challan_date",
                    "tax_kind",
                    "period",
                    "bank_name",
                    "economic_code",
                    "amount",
                    "state",
                    "move_id",
                ],
            ),
            (
                "withholding_returns_quarterly.csv",
                "fix.tds.return",
                [*c, ("quarter", "in", quarters)],
                [
                    "quarter",
                    "fiscal_year",
                    "total_withheld",
                    "deductor_count",
                    "due_date",
                    "state",
                    "nbr_acknowledgment",
                ],
            ),
            (
                "withholding_certificates.csv",
                "fix.withholding.certificate",
                [
                    *c,
                    ("issued_at", ">=", self.date_from),
                    ("issued_at", "<", self.date_to + timedelta(days=1)),
                ],
                [
                    "certificate_no",
                    "certificate_type",
                    "supplier_name",
                    "supplier_bin",
                    "supplier_tin",
                    "base_amount",
                    "withheld_amount",
                    "challan_no",
                    "issued_at",
                ],
            ),
            (
                "statutory_filing_evidence.csv",
                "fix.statutory.filing",
                c + rng("filed_on"),
                ["rule_id", "period_key", "filed_on", "reference"],
            ),
            (
                "tax_rate_master_snapshot.csv",
                "fix.tax.rate",
                [
                    *c,
                    ("date_from", "<=", self.date_to),
                    "|",
                    ("date_to", "=", False),
                    ("date_to", ">=", self.date_from),
                ],
                [
                    "tax_kind",
                    "code",
                    "name",
                    "section",
                    "payee_type",
                    "rate",
                    "non_filer_applies",
                    "date_from",
                    "date_to",
                    "verify_with_adviser",
                ],
            ),
        ]

    @staticmethod
    def _cell(value):
        if isinstance(value, models.BaseModel):
            return value.display_name or ""
        if value is False or value is None:
            return ""
        return str(value)

    def _csv_bytes(self, model, domain, field_names):
        Model = self.env[model]
        names = [f for f in field_names if f in Model._fields]
        buf = io.StringIO()
        writer = csv.writer(buf, lineterminator="\n")
        writer.writerow([Model._fields[f].string for f in names])
        records = Model.search(domain, order="id")
        for rec in records:
            writer.writerow([self._cell(rec[f]) for f in names])
        return buf.getvalue().encode("utf-8"), len(records)

    def action_generate(self):
        """Build the bundle: one CSV per register, a manifest.json with each
        file's SHA-256 and row count, zipped and attached to the pack."""
        for pack in self:
            if pack.state == "generated":
                raise UserError("Pack already generated — create a new pack to re-run")
            files, manifest = (
                {},
                {
                    "company": pack.company_id.name,
                    "date_from": str(pack.date_from),
                    "date_to": str(pack.date_to),
                    "files": [],
                },
            )
            for fname, model, domain, flds in pack._pack_sections():
                if model not in self.env:
                    continue
                data, count = pack._csv_bytes(model, domain, flds)
                files[fname] = data
                manifest["files"].append(
                    {"name": fname, "rows": count, "sha256": hashlib.sha256(data).hexdigest()}
                )
            manifest_bytes = json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8")
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
                for fname in sorted(files):
                    zf.writestr(fname, files[fname])
                zf.writestr("manifest.json", manifest_bytes)
            raw = buf.getvalue()
            attachment = self.env["ir.attachment"].create(
                {
                    "name": "tax-audit-pack-%s-%s.zip" % (pack.date_from, pack.date_to),
                    "type": "binary",
                    "datas": base64.b64encode(raw),
                    "mimetype": "application/zip",
                    "res_model": pack._name,
                    "res_id": pack.id,
                    "company_id": pack.company_id.id,
                }
            )
            pack.write(
                {
                    "state": "generated",
                    "attachment_id": attachment.id,
                    "manifest": manifest_bytes.decode("utf-8"),
                    "pack_sha256": hashlib.sha256(raw).hexdigest(),
                    "file_count": len(files),
                    "generated_at": fields.Datetime.now(),
                    "generated_by": self.env.user.id,
                    "integrity_status": "intact",
                }
            )
        return True

    def action_verify(self):
        """Re-read the stored bundle and check every file against the manifest."""
        for pack in self:
            if pack.state != "generated" or not pack.attachment_id:
                raise UserError("Generate the pack first")
            raw = base64.b64decode(pack.attachment_id.datas or b"")
            ok = hashlib.sha256(raw).hexdigest() == pack.pack_sha256
            if ok:
                manifest = json.loads(pack.manifest or "{}")
                with zipfile.ZipFile(io.BytesIO(raw)) as zf:
                    for entry in manifest.get("files", []):
                        data = zf.read(entry["name"])
                        if hashlib.sha256(data).hexdigest() != entry["sha256"]:
                            ok = False
                            break
            pack.integrity_status = "intact" if ok else "tampered"
        return True
