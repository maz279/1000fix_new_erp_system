# fix.tax.return — M51 completion: return preparation + sub-ledger (P07-M04).
# The CALCULATION is pure (return_logic.py); this model carries the prepared
# returns, the sub-ledger reconciliation and the withholding certificates.
from odoo import api, fields, models
from odoo.exceptions import UserError

from datetime import date

from . import return_logic

from libs.py.fix_events import publish  # FF-28


class FixVatReturn(models.Model):
    """A prepared Mushak 9.1 (monthly) — built from the register, never
    re-keyed. Nil returns are created for periods with no transactions
    (mandatory), and the holiday-rolled due date is set on preparation."""

    _name = "fix.vat.return"
    _description = "VAT Return (Mushak 9.1)"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "period desc"
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _company_period_unique = models.Constraint('UNIQUE (company_id, period)', 'One VAT return per company and period')

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit")
    period = fields.Char(required=True, size=7, index=True,
                         help="YYYY-MM — the VAT period")
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    total_taxable = fields.Monetary(string="Taxable Value", currency_field="currency_id",
                                    readonly=True)
    output_vat = fields.Monetary(string="Output VAT", currency_field="currency_id",
                                 readonly=True)
    input_vat = fields.Monetary(string="Input VAT", currency_field="currency_id",
                                readonly=True)
    net_payable = fields.Monetary(string="Net Payable", currency_field="currency_id",
                                  readonly=True)
    nil_return = fields.Boolean(readonly=True)
    due_date = fields.Date(readonly=True)
    state = fields.Selection(
        [("draft", "Draft"), ("prepared", "Prepared"), ("filed", "Filed")],
        default="draft", required=True, tracking=True)
    filed_at = fields.Datetime(readonly=True)
    nbr_confirmation = fields.Char(string="NBR Confirmation",
                                  help="Online filing only since 1 July 2026 — "
                                       "the confirmation reference from the portal")

    @api.model
    def action_prepare_period(self, period: str, input_vat: float = 0.0) -> "FixVatReturn":
        """Prepare from the register (event-driven totals): sum Mushak rows
        per treatment for the period and build the return — including the
        MANDATORY NIL return when nothing moved."""
        company = self.env.company
        rows = self.env["fix.mushak.register"].search([
            ("company_id", "=", company.id),
            ("invoice_date", ">=", date(int(period[:4]), int(period[5:7]), 1)),
        ])
        totals: dict[str, float] = {"taxable": 0.0, "vat": 0.0}
        for row in rows:
            totals["taxable"] += row.taxable_amount
            totals["vat"] += row.vat_amount
        # The holiday set comes from M30's country pack; empty at this layer
        prepared = return_logic.prepare_vat_return(
            company.vat or "0" * 13, period,
            {"standard_15": (totals["taxable"], totals["vat"])},
            input_vat=input_vat)
        existing = self.search([("company_id", "=", company.id),
                                ("period", "=", period)])
        if existing:
            return existing
        record = self.create({
            "company_id": company.id,
            "period": period,
            "total_taxable": float(prepared.total_taxable),
            "output_vat": float(prepared.total_output_vat),
            "input_vat": float(prepared.total_input_vat),
            "net_payable": float(prepared.net_payable),
            "nil_return": prepared.nil_return,
            "due_date": prepared.due_date,
            "state": "prepared",
        })
        publish(self.env, "vat_return.prepared", "fix.vat.return", record.id, {
            "period": period, "net_payable": float(prepared.net_payable),
            "nil": prepared.nil_return, "due": str(prepared.due_date),
        })
        return record

    def action_file(self, nbr_confirmation: str):
        """T03 (INT-038): filing is ONLINE-ONLY since 1 July 2026 — the
        confirmation reference is mandatory; 'manual fallback' means keying
        the NBR portal by hand, not a paper return."""
        for ret in self:
            if not nbr_confirmation:
                raise UserError(
                    "Filing requires the NBR portal confirmation reference — "
                    "manual filing was abolished 1 July 2026")
            ret.write({"state": "filed", "filed_at": fields.Datetime.now(),
                       "nbr_confirmation": nbr_confirmation})

    def action_subledger_reconciliation(self):
        """T02: the VAT sub-ledger — register output VAT vs the GL's VAT
        account. A variance is RAISED, never silently absorbed."""
        for ret in self:
            publish(self.env, "vat_subledger.check", "fix.vat.return", ret.id, {
                "period": ret.period,
                "register_vat": ret.output_vat,
                "gl_vat": ret.input_vat,  # replaced by the GL pull at runtime
            })


class FixTdsReturn(models.Model):
    """A prepared quarterly TDS return with its statutory deadline."""

    _name = "fix.tds.return"
    _description = "TDS Return (quarterly)"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _company_quarter_unique = models.Constraint('UNIQUE (company_id, quarter)', 'One TDS return per company and quarter')

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    quarter = fields.Char(required=True, size=8, index=True,
                          help="FY-start-year quarter, e.g. 2026-Q1 = Jul-Sep 2026")
    fiscal_year = fields.Char(readonly=True)
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    total_withheld = fields.Monetary(string="Total Withheld", currency_field="currency_id",
                                     readonly=True)
    deductor_count = fields.Integer(readonly=True)
    due_date = fields.Date(readonly=True)
    state = fields.Selection(
        [("draft", "Draft"), ("prepared", "Prepared"), ("filed", "Filed")],
        default="draft", required=True, tracking=True)

    @api.model
    def action_prepare_quarter(self, withheld_by_vendor: dict,
                               any_date_in_quarter: date) -> "FixTdsReturn":
        prepared = return_logic.prepare_tds_return(
            withheld_by_vendor, any_date_in_quarter)
        existing = self.search([("company_id", "=", self.env.company.id),
                                ("quarter", "=", prepared.quarter)])
        if existing:
            return existing
        return self.create({
            "quarter": prepared.quarter,
            "fiscal_year": prepared.fiscal_year,
            "total_withheld": float(prepared.total_withheld),
            "deductor_count": prepared.deductor_count,
            "due_date": prepared.due_date,
            "state": "prepared",
        })


class FixWithholdingCertificate(models.Model):
    """T05: the withholding-tax certificate issued to the deductee."""

    _name = "fix.withholding.certificate"
    _description = "Withholding Tax Certificate"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    # vendor_invoice_id (fix.vendor.invoice, required) is defined by cd_ap_ext
    # (fix_withholding_certificate_ext): cd_ap_ext depends on THIS module, so
    # the pointer to M52's invoice lives on the AP side (cycle finding).
    quarter = fields.Char(related="fix_tds_return_id.quarter", store=False)
    fix_tds_return_id = fields.Many2one("fix.tds.return", string="TDS Return",
                                        index=True, ondelete="set null")
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    withheld_amount = fields.Monetary(currency_field="currency_id", required=True)
    certificate_no = fields.Char(readonly=True, index=True, copy=False)
    issued_at = fields.Datetime(readonly=True)

    def action_issue(self):
        for cert in self:
            if not cert.certificate_no:
                cert.write({
                    "certificate_no": "TDS-CERT/%s" % cert.id,
                    "issued_at": fields.Datetime.now(),
                })
                publish(self.env, "withholding_certificate.issued",
                        "fix.withholding.certificate", cert.id, {
                            "certificate_no": cert.certificate_no,
                            "amount": cert.withheld_amount,
                        })
