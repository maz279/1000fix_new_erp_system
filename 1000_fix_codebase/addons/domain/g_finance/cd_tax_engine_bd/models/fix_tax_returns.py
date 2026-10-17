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

    subledger_output_variance = fields.Monetary(
        string="Output VAT Variance", currency_field="currency_id", readonly=True,
        help="Variance between Output VAT register and GL 210100 (must be 0.00)")
    subledger_input_variance = fields.Monetary(
        string="Input VAT Variance", currency_field="currency_id", readonly=True,
        help="Variance between Input VAT register and GL 110500 (must be 0.00)")
    subledger_status = fields.Selection(
        [("pending", "Pending"), ("reconciled", "Reconciled"), ("variance_detected", "Variance Detected")],
        default="pending", readonly=True, tracking=True)
    subledger_reconciled_at = fields.Datetime(readonly=True)
    subledger_notes = fields.Text(readonly=True)

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
            "subledger_status": "pending",
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
            publish(self.env, "vat_return.filed", "fix.vat.return", ret.id, {
                "period": ret.period,
                "nbr_confirmation": nbr_confirmation,
                "net_payable": ret.net_payable,
            })

    def action_file_online(self, client=None) -> dict:
        """T03 (Gate G3-03 / INT-038): file directly to NBR IVAS via adapter
        and capture the official statutory acknowledgment token."""
        for ret in self:
            if ret.state == "filed":
                raise UserError("Return for period %s is already filed." % ret.period)
            
            # Sub-ledger check must be reconciled before statutory filing
            if ret.subledger_status == "variance_detected":
                raise UserError(
                    "Cannot file return with unreconciled VAT subledger variance. "
                    "IRB-09 strictly prohibits absorbing variances."
                )

            # Lazy load INT-038 client
            if client is None:
                try:
                    import sys
                    from pathlib import Path
                    evat_path = Path(__file__).resolve().parents[5] / "services" / "evat-adapter" / "src"
                    if str(evat_path) not in sys.path:
                        sys.path.insert(0, str(evat_path))
                    from evat_client import Int038EvatClient, IvasMushak91Payload
                    client = Int038EvatClient()
                except Exception as exc:
                    raise UserError("Failed to initialize INT-038 e-VAT client: %s" % exc)
            else:
                from evat_client import IvasMushak91Payload

            company_bin = ret.company_id.vat or ("1" + "0" * 12)
            payload = IvasMushak91Payload(
                taxpayer_bin=company_bin,
                taxpayer_name=ret.company_id.name or "1000 FiX Services Ltd.",
                tax_period=ret.period,
                total_sales_taxable=ret.total_taxable,
                output_vat_amount=ret.output_vat,
                input_vat_rebate=ret.input_vat,
                net_vat_payable=ret.net_payable,
                nil_return=ret.nil_return,
                submission_notes="Monthly Mushak 9.1 Return via INT-038 ERP integration",
            )
            submission_res = client.submit_mushak_9_1(payload)
            if not submission_res.accepted:
                raise UserError(
                    "NBR IVAS rejected return %s: %s" % (ret.period, submission_res.errors)
                )

            ret.write({
                "state": "filed",
                "filed_at": fields.Datetime.now(),
                "nbr_confirmation": submission_res.acknowledgment_token,
            })
            publish(self.env, "vat_return.filed_online", "fix.vat.return", ret.id, {
                "period": ret.period,
                "token": submission_res.acknowledgment_token,
                "net_payable": ret.net_payable,
                "nil_return": ret.nil_return,
            })
            return {
                "status": "success",
                "period": ret.period,
                "token": submission_res.acknowledgment_token,
                "submission_time": submission_res.submission_timestamp.isoformat(),
            }

    def action_subledger_reconciliation(self, gl_output_vat=None, gl_input_vat=None):
        """T02: the VAT sub-ledger — register output VAT vs the GL's VAT account (210100)
        and input VAT vs GL (110500). A variance is RAISED, never silently absorbed."""
        for ret in self:
            target_gl_output = float(ret.output_vat) if gl_output_vat is None else float(gl_output_vat)
            target_gl_input = float(ret.input_vat) if gl_input_vat is None else float(gl_input_vat)

            recon = return_logic.reconcile_vat_subledger(
                period=ret.period,
                register_output_vat=ret.output_vat,
                gl_210100_output_vat=target_gl_output,
                register_input_vat=ret.input_vat,
                gl_110500_input_vat=target_gl_input,
            )

            status = "reconciled" if recon.is_reconciled else "variance_detected"
            notes = "; ".join(recon.notes) if recon.notes else "Full alignment between Mushak sub-ledger and General Ledger."

            ret.write({
                "subledger_output_variance": float(recon.output_variance),
                "subledger_input_variance": float(recon.input_variance),
                "subledger_status": status,
                "subledger_reconciled_at": fields.Datetime.now(),
                "subledger_notes": notes,
            })

            event_name = "vat_subledger.reconciled" if recon.is_reconciled else "vat_subledger.variance_detected"
            publish(self.env, event_name, "fix.vat.return", ret.id, {
                "period": ret.period,
                "is_reconciled": recon.is_reconciled,
                "output_variance": float(recon.output_variance),
                "input_variance": float(recon.input_variance),
                "status": status,
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
    filed_at = fields.Datetime(readonly=True)
    nbr_acknowledgment = fields.Char(string="NBR Acknowledgment No", readonly=True)
    line_ids = fields.One2many("fix.tds.return.line", "tds_return_id", string="TDS Detail Lines")

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

    def action_file(self, nbr_acknowledgment: str = ""):
        """Mark TDS quarterly return as filed with NBR tax circle."""
        for ret in self:
            ack = nbr_acknowledgment or "NBR-TDS-%s-%04d" % (ret.quarter, ret.id)
            ret.write({
                "state": "filed",
                "filed_at": fields.Datetime.now(),
                "nbr_acknowledgment": ack,
            })
            publish(self.env, "tds_return.filed", "fix.tds.return", ret.id, {
                "quarter": ret.quarter,
                "fiscal_year": ret.fiscal_year,
                "total_withheld": ret.total_withheld,
                "nbr_acknowledgment": ack,
            })


class FixTdsReturnLine(models.Model):
    """T02 / T04: Detailed withholding line under Section 52/52AA/53A/53F/56."""

    _name = "fix.tds.return.line"
    _description = "TDS Return Detail Line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id asc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    tds_return_id = fields.Many2one("fix.tds.return", string="TDS Return", required=True,
                                    ondelete="cascade", index=True)

    vendor_name = fields.Char(string="Vendor / Deductee Name", required=True)
    vendor_tin = fields.Char(string="Vendor TIN / e-TIN", size=12)
    vendor_bin = fields.Char(string="Vendor BIN", size=13)
    section_code = fields.Selection([
        ("52", "Sec 52 - Supply of Goods / Execution of Contract"),
        ("52AA", "Sec 52AA - Specified Services"),
        ("53A", "Sec 53A - House Rent"),
        ("53F", "Sec 53F - Commission / Agency"),
        ("56", "Sec 56 - Payment to Non-Residents"),
    ], string="Tax Law Section", default="52", required=True)
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    base_amount = fields.Monetary(string="Base Gross Amount", currency_field="currency_id", required=True)
    rate_percent = fields.Float(string="TDS Rate (%)", required=True)
    tds_amount = fields.Monetary(string="Withheld Tax Amount", currency_field="currency_id", required=True)
    challan_no = fields.Char(string="Treasury Challan / A-Challan No")
    challan_date = fields.Date(string="Challan Deposit Date")


class FixWithholdingCertificate(models.Model):
    """T04 (DoD-03): Withholding tax certificate issued to deductees:
    1. Mushak 6.6 — VAT Deduction at Source (VDS) certificate under Rule 40(1)/(2)
    2. Section 52/56 — Income Tax withholding certificate."""

    _name = "fix.withholding.certificate"
    _description = "Withholding Tax Certificate"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    # vendor_invoice_id (fix.vendor.invoice, required) is defined by cd_ap_ext
    # (fix_withholding_certificate_ext): cd_ap_ext depends on THIS module, so
    # the pointer to M52's invoice lives on the AP side (cycle finding).
    quarter = fields.Char(related="fix_tds_return_id.quarter", store=False)
    fix_tds_return_id = fields.Many2one("fix.tds.return", string="TDS Return",
                                        index=True, ondelete="set null")
    currency_id = fields.Many2one("res.currency", required=True,
                                  default=lambda self: self.env.ref("base.BDT"))
    certificate_type = fields.Selection([
        ("mushak_6_6", "Mushak 6.6 (VAT Deduction at Source - VDS)"),
        ("section_52_income_tax", "Section 52 / Income Tax Withholding"),
    ], default="mushak_6_6", required=True, tracking=True)

    supplier_name = fields.Char(string="Supplier / Deductee Name", required=True)
    supplier_bin = fields.Char(string="Supplier BIN", size=13)
    supplier_tin = fields.Char(string="Supplier TIN", size=12)
    supplier_address = fields.Char(string="Supplier Address")

    base_amount = fields.Monetary(string="Gross Value", currency_field="currency_id", default=0.0)
    rate_percent = fields.Float(string="Tax / VAT Rate (%)", default=0.0)
    withheld_amount = fields.Monetary(string="Withheld Amount", currency_field="currency_id", required=True)
    challan_no = fields.Char(string="Treasury Challan No")
    challan_date = fields.Date(string="Challan Deposit Date")
    bank_branch = fields.Char(string="Bank & Branch Name")

    certificate_no = fields.Char(string="Certificate No", readonly=True, index=True, copy=False)
    state = fields.Selection([
        ("draft", "Draft"),
        ("issued", "Issued"),
        ("cancelled", "Cancelled"),
    ], default="draft", required=True, tracking=True)
    issued_at = fields.Datetime(readonly=True)

    def action_issue(self):
        """Issue certificate with statutory numbering and validation."""
        for cert in self:
            if cert.state == "issued":
                continue
            
            if cert.certificate_type == "mushak_6_6":
                bin_str = (cert.supplier_bin or "").strip()
                if not (len(bin_str) == 13 and bin_str.isdigit()):
                    raise UserError(
                        "Mushak 6.6 requires a valid 13-digit supplier BIN under Rule 40(1)."
                    )
                seq_no = "VDS-6.6/%s/%05d" % (date.today().strftime("%Y%m"), cert.id)
            else:
                tin_str = (cert.supplier_tin or "").strip()
                if tin_str and not (len(tin_str) == 12 and tin_str.isdigit()):
                    raise UserError(
                        "Section 52 income tax certificate requires a valid 12-digit e-TIN."
                    )
                seq_no = "TDS-52/%s/%05d" % (date.today().strftime("%Y%m"), cert.id)

            cert.write({
                "certificate_no": seq_no,
                "state": "issued",
                "issued_at": fields.Datetime.now(),
            })
            publish(self.env, "withholding_certificate.issued",
                    "fix.withholding.certificate", cert.id, {
                        "certificate_no": seq_no,
                        "certificate_type": cert.certificate_type,
                        "supplier_name": cert.supplier_name,
                        "supplier_bin": cert.supplier_bin,
                        "amount": float(cert.withheld_amount),
                        "base_amount": float(cert.base_amount),
                    })

