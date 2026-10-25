# cd_tax_engine_bd — A08 M51 (CD-M51-01): the argument-free preparation of
# the Mushak 9.1 and the quarterly withholding return that the workspace
# calls, built from the registers (output), the tracked input credits, the
# VDS certificates received and the TDS deduction lines. Loaded after
# fix_tax_returns (these classes extend its models).
import json
import re
from datetime import date, timedelta
from decimal import Decimal

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

from . import return_logic
from .fix_tax_compliance import (
    ITA_SECTIONS,
    PERIOD_RE,
    QUARTER_RE,
    money,
    post_tax_move,
    quarter_bounds,
)
from .fix_tax_master import add_months, tax_account


class FixVatReturnA08(models.Model):
    """Argument-free preparation of the 9.1 the workspace calls, with input
    credit from the tracked purchase credits and VDS credit (6.6 received)."""

    _inherit = "fix.vat.return"

    input_credit_ids = fields.One2many(
        "fix.input.vat.credit", "vat_return_id", string="Input Credits Claimed"
    )
    vds_received_credit = fields.Monetary(
        string="VDS Credit (6.6 received)",
        currency_field="currency_id",
        readonly=True,
        help="VAT customers deducted at source, evidenced by Mushak 6.6 received",
    )
    net_payable_after_vds = fields.Monetary(
        string="Net Payable after VDS", currency_field="currency_id", readonly=True
    )
    challan_ids = fields.One2many("fix.tax.challan", "vat_return_id", string="Challans")
    vds_certificate_ids = fields.Char(
        readonly=True, help="JSON ids of the Mushak 6.6 received this return claims"
    )
    vds_claim_move_id = fields.Many2one(
        "account.move", string="VDS Claim Entry", readonly=True, copy=False
    )

    @api.constrains("period")
    def _check_period_format(self):
        for ret in self:
            if not PERIOD_RE.match(ret.period or ""):
                raise ValidationError("The VAT period is YYYY-MM")

    def _vds_certificates(self):
        """Mushak 6.6 received (cd_billing_engine) claimable in this period:
        settled, not yet claimed. Empty when that model is not installed."""
        self.ensure_one()
        model = "fix.vds.certificate.received"
        if model not in self.env:
            return None
        Cert = self.env[model]
        if hasattr(Cert, "claimable_for_period"):
            return Cert.claimable_for_period(self.period, self.company_id)
        return Cert.search(
            [
                ("company_id", "=", self.company_id.id),
                ("period", "=", self.period),
                ("state", "=", "settled"),
            ]
        )

    def _vds_claim_lines(self):
        """The certificates this prepared return claims (ids stored on preparation)."""
        self.ensure_one()
        model = "fix.vds.certificate.received"
        ids = json.loads(self.vds_certificate_ids or "[]")
        if model not in self.env or not ids:
            return None
        return self.env[model].browse(ids).exists().filtered(lambda c: c.state == "settled")

    def _vds_claim_accounts(self):
        """(VAT payable, VDS receivable, journal) for the claim entry — refused
        when unconfigured, BEFORE anything is filed."""
        self.ensure_one()
        company = self.company_id
        vat_payable = tax_account(self.env, company, "vat_output")
        param = "cd_billing_engine.account_code.vds_receivable"
        code = self.env["ir.config_parameter"].sudo().get_param(param) or "132000"
        receivable = self.env["account.account"].search(
            [("code", "=", code), ("company_ids", "in", company.id)], limit=1
        )
        if not receivable:
            raise UserError(
                "No VDS receivable account %s in %s (system parameter %s) — the VDS "
                "credit cannot be cleared; nothing was filed." % (code, company.name, param)
            )
        journal = self.env["account.journal"].search(
            [("company_id", "=", company.id), ("type", "=", "general")], limit=1
        )
        if not journal:
            raise UserError("No general journal in %s for the VDS claim entry" % company.name)
        return vat_payable, receivable, journal

    def _claim_vds_on_filing(self, accounts):
        """On filing: Dr VAT payable / Cr VDS receivable, and mark the 6.6
        certificates claimed against this return (claimed exactly once)."""
        self.ensure_one()
        certs = self._vds_claim_lines()
        if not certs:
            return
        amount = money(sum(certs.mapped("vds_amount")))
        vat_payable, receivable, journal = accounts
        label = "VDS 6.6 claimed in Mushak 9.1 %s" % self.period
        move = post_tax_move(
            self.env,
            self.company_id,
            journal,
            fields.Date.context_today(self),
            label,
            [(vat_payable, label, amount, 0.0, False), (receivable, label, 0.0, amount, False)],
            self.operating_unit_id,
        )
        certs.action_mark_claimed("Mushak 9.1 %s (%s)" % (self.period, self.nbr_confirmation or ""))
        self.vds_claim_move_id = move.id

    def action_file(self, nbr_confirmation: str):
        accounts = {r.id: r._vds_claim_accounts() for r in self if r._vds_claim_lines()}
        res = super().action_file(nbr_confirmation)
        for ret in self.filtered(lambda r: r.id in accounts):
            ret._claim_vds_on_filing(accounts[ret.id])
        return res

    def action_file_online(self, client=None):
        accounts = self._vds_claim_accounts() if self._vds_claim_lines() else None
        res = super().action_file_online(client=client)
        if accounts:
            self._claim_vds_on_filing(accounts)
        return res

    def action_prepare(self):
        """(Re)prepare this period's 9.1 from the Mushak register (output), the
        eligible input credits whose claim period is this period (input) and
        the VDS certificates received. Refused once filed."""
        for ret in self:
            if ret.state == "filed":
                raise UserError("Return %s is filed — it cannot be re-prepared" % ret.period)
            company = ret.company_id
            start, nxt = (
                date(int(ret.period[:4]), int(ret.period[5:7]), 1),
                date(*add_months(int(ret.period[:4]), int(ret.period[5:7]), 1), 1),
            )
            rows = self.env["fix.mushak.register"].search(
                [
                    ("company_id", "=", company.id),
                    ("invoice_date", ">=", start),
                    ("invoice_date", "<", nxt),
                ]
            )
            register_totals = return_logic.aggregate_register(
                [(r.taxable_amount, r.vat_amount, r.treatment_summary or "") for r in rows]
            )
            credits = ret.input_credit_ids | self.env["fix.input.vat.credit"].search(
                [
                    ("company_id", "=", company.id),
                    ("state", "=", "eligible"),
                    ("claim_period", "=", ret.period),
                ]
            )
            input_vat = Decimal(str(money(sum(credits.mapped("signed_vat")))))
            prepared = return_logic.prepare_vat_return(
                ret._company_bin_checked(), ret.period, register_totals, input_vat=input_vat
            )
            due = self.env["fix.statutory.due.rule"].due_date_for(
                "vat_91_return", nxt - timedelta(days=1), company
            )
            certs = ret._vds_certificates()
            vds = money(sum(certs.mapped("vds_amount"))) if certs else 0.0
            unclassified = sorted(
                k for k in register_totals if k.startswith(return_logic.UNCLASSIFIED_PREFIX)
            )
            ret.write(
                {
                    "total_taxable": float(prepared.total_taxable),
                    "output_vat": float(prepared.total_output_vat),
                    "input_vat": float(prepared.total_input_vat),
                    "net_payable": float(prepared.net_payable),
                    "vds_received_credit": vds,
                    "vds_certificate_ids": json.dumps(certs.ids if certs else []),
                    "net_payable_after_vds": money(float(prepared.net_payable) - vds),
                    "nil_return": prepared.nil_return and not vds,
                    "due_date": due or prepared.due_date,
                    "state": "prepared",
                    "subledger_status": "pending",
                    "subledger_notes": False,
                    "treatment_breakdown": json.dumps(
                        {
                            line.treatment: [str(line.taxable_value), str(line.output_vat)]
                            for line in prepared.lines
                        },
                        sort_keys=True,
                    ),
                    "classification_notes": (
                        "Register rows without a determinable VAT treatment (must be "
                        "classified before filing): %s" % ", ".join(unclassified)
                    )
                    if unclassified
                    else False,
                }
            )
            (ret.input_credit_ids - credits).write({"state": "eligible", "vat_return_id": False})
            credits.write({"state": "claimed", "vat_return_id": ret.id})
            publish(
                self.env,
                "vat_return.prepared",
                "fix.vat.return",
                ret.id,
                {"period": ret.period, "net_payable": float(prepared.net_payable), "vds": vds},
            )
        return True

    def _company_bin_checked(self):
        from .fix_tax_returns import _company_bin

        return _company_bin(self.company_id)


class FixTdsReturnA08(models.Model):
    """Quarterly withholding return prepared from the TDS deduction lines."""

    _inherit = "fix.tds.return"

    @api.constrains("quarter")
    def _check_quarter_format(self):
        for ret in self:
            if not QUARTER_RE.match(ret.quarter or ""):
                raise ValidationError(
                    "The quarter label is the fiscal-year start year and quarter, e.g. "
                    "2026-Q1 for Jul-Sep 2026"
                )

    def action_prepare(self):
        """Rebuild the return's detail lines from the quarter's TDS deductions."""
        for ret in self:
            if ret.state == "filed":
                raise UserError("TDS return %s is filed" % ret.quarter)
            start, end = quarter_bounds(ret.quarter)
            deductions = self.env["fix.withholding.line"].search(
                [
                    ("company_id", "=", ret.company_id.id),
                    ("tax_kind", "=", "tds"),
                    ("document_date", ">=", start),
                    ("document_date", "<=", end),
                    ("state", "!=", "cancelled"),
                ]
            )
            ret.line_ids.unlink()
            vals = []
            for d in deductions:
                m = re.search(r"s\.?\s*(\d+)", d.section or "")
                section = m.group(1) if m and m.group(1) in ITA_SECTIONS else "other"
                vals.append(
                    {
                        "tds_return_id": ret.id,
                        "company_id": ret.company_id.id,
                        "operating_unit_id": d.operating_unit_id.id,
                        "withholding_line_id": d.id,
                        "vendor_name": d.partner_id.name,
                        "vendor_tin": d.partner_tin or False,
                        "vendor_bin": d.partner_bin or False,
                        "section_code": section,
                        "base_amount": d.base_amount,
                        "rate_percent": d.rate * d.multiplier,
                        "tds_amount": d.amount,
                        "challan_no": d.challan_id.challan_no or False,
                        "challan_date": d.challan_id.challan_date or False,
                    }
                )
            self.env["fix.tds.return.line"].create(vals)
            due = self.env["fix.statutory.due.rule"].due_date_for(
                "wht_return", end, ret.company_id
            ) or return_logic.tds_return_due_date(ret.quarter)
            ret.write(
                {
                    "fiscal_year": return_logic.tds_quarter_for_date(start)[1],
                    "total_withheld": money(sum(deductions.mapped("amount"))),
                    "deductor_count": len(deductions.mapped("partner_id")),
                    "due_date": due,
                    "state": "prepared",
                }
            )
        return True


class FixTdsReturnLineA08(models.Model):
    _inherit = "fix.tds.return.line"

    withholding_line_id = fields.Many2one(
        "fix.withholding.line", string="Deduction", ondelete="set null"
    )
    section_code = fields.Selection(
        selection_add=[
            ("89", "ITA 2023 s.89 - Contractors / suppliers"),
            ("90", "ITA 2023 s.90 - Services"),
            ("94", "ITA 2023 s.94 - Commission"),
            ("109", "ITA 2023 s.109 - Rent"),
            ("other", "Other section"),
        ],
        ondelete={
            "89": "set default",
            "90": "set default",
            "94": "set default",
            "109": "set default",
            "other": "set default",
        },
    )
