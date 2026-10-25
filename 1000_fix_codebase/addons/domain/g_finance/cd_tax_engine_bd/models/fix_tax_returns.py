# fix.tax.return — M51 completion: return preparation + sub-ledger (P07-M04).
# The CALCULATION is pure (return_logic.py); this model carries the prepared
# returns, the sub-ledger reconciliation and the withholding certificates.
import json
import re
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any, Protocol, TypedDict, TypeVar

from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish  # FF-28

from . import return_logic

# INT-038 adapter (services/evat-adapter/src) — loaded lazily on first filing.
EVAT_ADAPTER_SRC = Path(__file__).resolve().parents[5] / "services" / "evat-adapter" / "src"

_PayloadT = TypeVar("_PayloadT")


class EvatSubmission(Protocol):
    """What filing reads of the adapter's EvatSubmissionResult (INT-038)."""

    @property
    def status(self) -> str: ...  # "ACCEPTED" | "REJECTED" | "SAVED_BATCH"
    @property
    def ack_token(self) -> str: ...
    @property
    def filed_at(self) -> str: ...
    @property
    def validation_messages(self) -> list[str]: ...


class EvatClient(Protocol[_PayloadT]):
    """The INT-038 client contract (services/evat-adapter/src/evat_client.py):
    build_payload() then submit_return(); the payload is opaque to this module."""

    def build_payload(
        self,
        *,
        taxpayer_bin: str,
        taxpayer_name: str,
        tax_period: str,
        register_totals: dict[str, tuple[Decimal, Decimal]],
        input_vat: Decimal,
        declarant_name: str,
        declarant_designation: str,
        declarant_nid: str,
    ) -> _PayloadT: ...

    def submit_return(self, payload: _PayloadT) -> EvatSubmission: ...


class VatFilingResult(TypedDict):
    """action_file_online()'s result: exactly one filing."""

    status: str
    period: str
    token: str
    submission_time: str


def _company_bin(company: Any) -> str:
    """The taxpayer BIN from company master data — never invented: a return
    filed or prepared under a placeholder BIN is a regulatory event."""
    bin_no = (company.vat or "").replace(" ", "")
    if not re.fullmatch(r"\d{13}", bin_no):
        raise UserError(
            "Company %s has no valid 13-digit BIN — a VAT return cannot be "
            "prepared or filed without it" % company.name
        )
    return bin_no


# GL accounts the VAT sub-ledger reconciles against (codes in the company's
# chart; overridable per database through ir.config_parameter).
VAT_OUTPUT_ACCOUNT_PARAM = "cd_tax_engine_bd.vat_output_account_code"
VAT_INPUT_ACCOUNT_PARAM = "cd_tax_engine_bd.vat_input_account_code"
DEFAULT_VAT_OUTPUT_ACCOUNT = "210100"  # VAT Output Payable
DEFAULT_VAT_INPUT_ACCOUNT = "110500"  # VAT Input Credit Receivable


def _period_bounds(period: str) -> tuple[date, date]:
    """[start, next_start) of a YYYY-MM VAT period."""
    year, month = int(period[:4]), int(period[5:7])
    start = date(year, month, 1)
    return start, (date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1))


def _default_evat_client() -> EvatClient[Any]:
    """Build the INT-038 NBR e-VAT client (sandbox unless configured)."""
    if str(EVAT_ADAPTER_SRC) not in sys.path:
        sys.path.insert(0, str(EVAT_ADAPTER_SRC))
    from evat_client import (  # type: ignore[import-not-found]  # on sys.path only at runtime (above)
        Int038EvatClient,
    )

    client: EvatClient[Any] = Int038EvatClient()
    return client


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
    _company_period_unique = models.Constraint(
        "UNIQUE (company_id, period)", "One VAT return per company and period"
    )

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit")
    period = fields.Char(required=True, size=7, index=True, help="YYYY-MM — the VAT period")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    total_taxable = fields.Monetary(
        string="Taxable Value", currency_field="currency_id", readonly=True
    )
    output_vat = fields.Monetary(string="Output VAT", currency_field="currency_id", readonly=True)
    input_vat = fields.Monetary(string="Input VAT", currency_field="currency_id", readonly=True)
    net_payable = fields.Monetary(string="Net Payable", currency_field="currency_id", readonly=True)
    nil_return = fields.Boolean(readonly=True)
    due_date = fields.Date(readonly=True)
    state = fields.Selection(
        [("draft", "Draft"), ("prepared", "Prepared"), ("filed", "Filed")],
        default="draft",
        required=True,
        tracking=True,
    )
    filed_at = fields.Datetime(readonly=True)
    nbr_confirmation = fields.Char(
        string="NBR Confirmation",
        help="Online filing only since 1 July 2026 — the confirmation reference from the portal",
    )

    subledger_output_variance = fields.Monetary(
        string="Output VAT Variance",
        currency_field="currency_id",
        readonly=True,
        help="Variance between Output VAT register and GL 210100 (must be 0.00)",
    )
    subledger_input_variance = fields.Monetary(
        string="Input VAT Variance",
        currency_field="currency_id",
        readonly=True,
        help="Variance between Input VAT register and GL 110500 (must be 0.00)",
    )
    subledger_status = fields.Selection(
        [
            ("pending", "Pending"),
            ("reconciled", "Reconciled"),
            ("variance_detected", "Variance Detected"),
        ],
        default="pending",
        readonly=True,
        tracking=True,
    )
    subledger_reconciled_at = fields.Datetime(readonly=True)
    subledger_notes = fields.Text(readonly=True)
    treatment_breakdown = fields.Text(
        readonly=True,
        help="JSON {treatment: [taxable, output VAT]} summed from the Mushak register "
        "per Mushak 9.1 line. Keys starting with 'unclassified' are register rows "
        "whose treatment could not be determined; they block online filing.",
    )
    classification_notes = fields.Text(readonly=True)

    def _register_totals(self) -> dict[str, tuple[Decimal, Decimal]]:
        """The per-treatment totals the return was prepared with."""
        self.ensure_one()
        raw = json.loads(self.treatment_breakdown or "{}")
        return {k: (Decimal(str(v[0])), Decimal(str(v[1]))) for k, v in raw.items()}

    @api.model
    def action_prepare_period(self, period: str, input_vat: float | None = None) -> "FixVatReturn":
        """Prepare from the register (event-driven totals): sum Mushak rows
        per treatment for the period and build the return — including the
        MANDATORY NIL return when nothing moved.

        Treatment: each register row is classified from its own
        ``treatment_summary`` or, failing that, its effective rate
        (return_logic.classify_register_row). Rows that cannot be classified
        are summed per actual rate under ``unclassified_rate_<r>`` and noted —
        never folded into the 15% standard line.

        Input VAT: this module holds no purchase-side (Mushak 6.3 received)
        register, so the creditable input VAT must be supplied by the caller
        from the period's purchase records. It is REQUIRED — a missing figure
        is refused rather than silently filed as 0.00 (which would over-declare
        the net payable). Pass ``input_vat=0.0`` explicitly for a period with
        no creditable purchases.
        """
        company = self.env.company
        if input_vat is None:
            raise UserError(
                "Input VAT for %s must be supplied from the period's purchase "
                "Mushak 6.3 records (pass 0.0 explicitly if there were none) — "
                "it is not defaulted." % period
            )
        period_start, next_period_start = _period_bounds(period)
        # BOTH bounds: without the upper one a period's return also summed
        # every later month's Mushak rows (an over-declared Mushak 9.1).
        rows = self.env["fix.mushak.register"].search(
            [
                ("company_id", "=", company.id),
                ("invoice_date", ">=", period_start),
                ("invoice_date", "<", next_period_start),
            ]
        )
        register_totals = return_logic.aggregate_register(
            [(row.taxable_amount, row.vat_amount, row.treatment_summary or "") for row in rows]
        )
        # The holiday set comes from M30's country pack; empty at this layer
        prepared = return_logic.prepare_vat_return(
            _company_bin(company),
            period,
            register_totals,
            input_vat=Decimal(str(input_vat)),
        )
        existing: FixVatReturn = self.search(
            [("company_id", "=", company.id), ("period", "=", period)]
        )
        if existing:
            return existing
        unclassified = sorted(
            k for k in register_totals if k.startswith(return_logic.UNCLASSIFIED_PREFIX)
        )
        notes = (
            "Register rows without a determinable VAT treatment (summed per actual "
            "rate, must be classified before filing): %s" % ", ".join(unclassified)
            if unclassified
            else ""
        )
        record: FixVatReturn = self.create(
            {
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
                "treatment_breakdown": json.dumps(
                    {
                        line.treatment: [str(line.taxable_value), str(line.output_vat)]
                        for line in prepared.lines
                    },
                    sort_keys=True,
                ),
                "classification_notes": notes,
            }
        )
        publish(
            self.env,
            "vat_return.prepared",
            "fix.vat.return",
            record.id,
            {
                "period": period,
                "net_payable": float(prepared.net_payable),
                "nil": prepared.nil_return,
                "due": str(prepared.due_date),
            },
        )
        return record

    def action_file(self, nbr_confirmation: str) -> None:
        """T03 (INT-038): filing is ONLINE-ONLY since 1 July 2026 — the
        confirmation reference is mandatory; 'manual fallback' means keying
        the NBR portal by hand, not a paper return."""
        for ret in self:
            if not nbr_confirmation:
                raise UserError(
                    "Filing requires the NBR portal confirmation reference — "
                    "manual filing was abolished 1 July 2026"
                )
            ret.write(
                {
                    "state": "filed",
                    "filed_at": fields.Datetime.now(),
                    "nbr_confirmation": nbr_confirmation,
                }
            )
            publish(
                self.env,
                "vat_return.filed",
                "fix.vat.return",
                ret.id,
                {
                    "period": ret.period,
                    "nbr_confirmation": nbr_confirmation,
                    "net_payable": ret.net_payable,
                },
            )

    def action_file_online(self, client: EvatClient[Any] | None = None) -> VatFilingResult:
        """T03 (Gate G3-03 / INT-038): file directly to NBR IVAS via adapter
        and capture the official statutory acknowledgment token.

        Uses the adapter's real contract — build_payload() then
        submit_return(), whose result carries status / ack_token / filed_at.
        One return per call: the result describes exactly one filing."""
        self.ensure_one()
        ret = self
        if ret.state == "filed":
            raise UserError("Return for period %s is already filed." % ret.period)

        # Sub-ledger check must be reconciled before statutory filing
        if ret.subledger_status == "variance_detected":
            raise UserError(
                "Cannot file return with unreconciled VAT subledger variance. "
                "IRB-09 strictly prohibits absorbing variances."
            )

        taxpayer_bin = _company_bin(ret.company_id)
        register_totals = ret._register_totals()
        unclassified = sorted(
            k for k in register_totals if k.startswith(return_logic.UNCLASSIFIED_PREFIX)
        )
        if unclassified:
            raise UserError(
                "Return %s contains register supplies with no determinable VAT treatment "
                "(%s). Classify them in the register and re-prepare before filing."
                % (ret.period, ", ".join(unclassified))
            )
        line_taxable = sum((t for t, _ in register_totals.values()), Decimal("0"))
        line_vat = sum((v for _, v in register_totals.values()), Decimal("0"))
        if line_taxable.quantize(Decimal("0.01")) != Decimal(str(ret.total_taxable)).quantize(
            Decimal("0.01")
        ) or line_vat.quantize(Decimal("0.01")) != Decimal(str(ret.output_vat)).quantize(
            Decimal("0.01")
        ):
            # Previously every supply was declared on the 15% line whatever
            # its real treatment; a return without a register breakdown that
            # matches its totals cannot be filed honestly.
            raise UserError(
                "Return %s has no per-treatment breakdown matching its totals — "
                "prepare it from the Mushak register before filing." % ret.period
            )
        if client is None:
            try:
                client = _default_evat_client()
            except Exception as exc:
                raise UserError("Failed to initialize INT-038 e-VAT client: %s" % exc) from exc

        # The return is declared by a real signing officer, configured by
        # Finance; the adapter refuses a payload without one.
        icp = self.env["ir.config_parameter"].sudo()
        payload = client.build_payload(
            taxpayer_bin=taxpayer_bin,
            taxpayer_name=ret.company_id.name,
            tax_period=ret.period,
            register_totals=register_totals,
            input_vat=Decimal(str(ret.input_vat)),
            declarant_name=icp.get_param("cd_tax_engine_bd.declarant_name", ""),
            declarant_designation=icp.get_param("cd_tax_engine_bd.declarant_designation", ""),
            declarant_nid=icp.get_param("cd_tax_engine_bd.declarant_nid", ""),
        )
        try:
            submission = client.submit_return(payload)
        except (ValueError, RuntimeError) as exc:  # EvatValidationError / EvatError
            raise UserError("NBR IVAS rejected return %s: %s" % (ret.period, exc)) from exc
        if submission.status != "ACCEPTED":
            raise UserError(
                "NBR IVAS rejected return %s: %s"
                % (ret.period, "; ".join(submission.validation_messages) or submission.status)
            )

        ret.write(
            {
                "state": "filed",
                "filed_at": fields.Datetime.now(),
                "nbr_confirmation": submission.ack_token,
            }
        )
        publish(
            self.env,
            "vat_return.filed_online",
            "fix.vat.return",
            ret.id,
            {
                "period": ret.period,
                "token": submission.ack_token,
                "net_payable": ret.net_payable,
                "nil_return": ret.nil_return,
            },
        )
        return {
            "status": "success",
            "period": ret.period,
            "token": submission.ack_token,
            "submission_time": submission.filed_at,
        }

    def _vat_gl_account(self, param: str, default_code: str) -> Any:
        """The company's VAT GL account (by configured code) — refused if absent."""
        self.ensure_one()
        code = self.env["ir.config_parameter"].sudo().get_param(param) or default_code
        Account = self.env["account.account"].with_company(self.company_id)
        account = Account.search(
            [*Account._check_company_domain(self.company_id), ("code", "=", code)], limit=1
        )
        if not account:
            raise UserError(
                "VAT sub-ledger reconciliation needs GL account %s in company %s "
                "(configure it, or set system parameter %s to the right code). "
                "Without the GL side there is nothing to reconcile against."
                % (code, self.company_id.name, param)
            )
        return account

    def _gl_vat_balances(self) -> tuple[Decimal, Decimal]:
        """(output VAT, input VAT) per the GENERAL LEDGER for the return period:
        posted journal items on the VAT payable (credit-normal) and VAT
        receivable (debit-normal) accounts dated within the period."""
        self.ensure_one()
        out_acc = self._vat_gl_account(VAT_OUTPUT_ACCOUNT_PARAM, DEFAULT_VAT_OUTPUT_ACCOUNT)
        in_acc = self._vat_gl_account(VAT_INPUT_ACCOUNT_PARAM, DEFAULT_VAT_INPUT_ACCOUNT)
        start, next_start = _period_bounds(self.period)
        MoveLine = self.env["account.move.line"]
        balances: dict[int, Decimal] = {}
        for account in (out_acc, in_acc):
            lines = MoveLine.search(
                [
                    ("company_id", "=", self.company_id.id),
                    ("account_id", "=", account.id),
                    ("parent_state", "=", "posted"),
                    ("date", ">=", start),
                    ("date", "<", next_start),
                ]
            )
            balances[account.id] = sum((Decimal(str(line.balance)) for line in lines), Decimal("0"))
        return -balances[out_acc.id], balances[in_acc.id]

    def action_subledger_reconciliation(self) -> None:
        """T02: the VAT sub-ledger — register output VAT vs the GL's VAT account (210100)
        and input VAT vs GL (110500). A variance is RAISED, never silently absorbed.

        The GL side is ALWAYS read from posted account.move.line for the
        period. (Previously, called without GL figures — as the form button
        does — the return was compared with itself and always "reconciled".)
        Missing GL accounts refuse the reconciliation."""
        for ret in self:
            target_gl_output, target_gl_input = ret._gl_vat_balances()

            recon = return_logic.reconcile_vat_subledger(
                period=ret.period,
                register_output_vat=ret.output_vat,
                gl_210100_output_vat=target_gl_output,
                register_input_vat=ret.input_vat,
                gl_110500_input_vat=target_gl_input,
            )

            status = "reconciled" if recon.is_reconciled else "variance_detected"
            notes = (
                "; ".join(recon.notes)
                if recon.notes
                else "Full alignment between Mushak sub-ledger and General Ledger."
            )

            ret.write(
                {
                    "subledger_output_variance": float(recon.output_variance),
                    "subledger_input_variance": float(recon.input_variance),
                    "subledger_status": status,
                    "subledger_reconciled_at": fields.Datetime.now(),
                    "subledger_notes": notes,
                }
            )

            event_name = (
                "vat_subledger.reconciled"
                if recon.is_reconciled
                else "vat_subledger.variance_detected"
            )
            publish(
                self.env,
                event_name,
                "fix.vat.return",
                ret.id,
                {
                    "period": ret.period,
                    "is_reconciled": recon.is_reconciled,
                    "output_variance": float(recon.output_variance),
                    "input_variance": float(recon.input_variance),
                    "status": status,
                },
            )


class FixTdsReturn(models.Model):
    """A prepared quarterly TDS return with its statutory deadline."""

    _name = "fix.tds.return"
    _description = "TDS Return (quarterly)"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _company_quarter_unique = models.Constraint(
        "UNIQUE (company_id, quarter)", "One TDS return per company and quarter"
    )

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    quarter = fields.Char(
        required=True, size=8, index=True, help="FY-start-year quarter, e.g. 2026-Q1 = Jul-Sep 2026"
    )
    fiscal_year = fields.Char(readonly=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    total_withheld = fields.Monetary(
        string="Total Withheld", currency_field="currency_id", readonly=True
    )
    deductor_count = fields.Integer(readonly=True)
    due_date = fields.Date(readonly=True)
    state = fields.Selection(
        [("draft", "Draft"), ("prepared", "Prepared"), ("filed", "Filed")],
        default="draft",
        required=True,
        tracking=True,
    )
    filed_at = fields.Datetime(readonly=True)
    nbr_acknowledgment = fields.Char(
        string="NBR Acknowledgment No",
        copy=False,
        help="The acknowledgment number NBR issued for this quarter's return — "
        "entered by the user after filing; required to mark the return filed.",
    )
    line_ids = fields.One2many("fix.tds.return.line", "tds_return_id", string="TDS Detail Lines")

    @api.model
    def action_prepare_quarter(
        self, withheld_by_vendor: dict[str, Decimal], any_date_in_quarter: date
    ) -> "FixTdsReturn":
        prepared = return_logic.prepare_tds_return(withheld_by_vendor, any_date_in_quarter)
        existing: FixTdsReturn = self.search(
            [("company_id", "=", self.env.company.id), ("quarter", "=", prepared.quarter)]
        )
        if existing:
            return existing
        record: FixTdsReturn = self.create(
            {
                "quarter": prepared.quarter,
                "fiscal_year": prepared.fiscal_year,
                "total_withheld": float(prepared.total_withheld),
                "deductor_count": prepared.deductor_count,
                "due_date": prepared.due_date,
                "state": "prepared",
            }
        )
        return record

    def action_file(self, nbr_acknowledgment: str = "") -> None:
        """Mark the TDS quarterly return as filed with the NBR tax circle.

        Requires the REAL acknowledgment number NBR issued — passed in, or
        entered on the return's ``nbr_acknowledgment`` field before pressing
        the button. (Previously a missing acknowledgment was replaced by a
        self-minted ``NBR-TDS-<quarter>-<id>``, recording a filing NBR never
        acknowledged.)"""
        for ret in self:
            ack = (nbr_acknowledgment or ret.nbr_acknowledgment or "").strip()
            if not ack:
                raise UserError(
                    "Enter the NBR acknowledgment number for TDS return %s before "
                    "marking it filed — it cannot be generated locally." % ret.quarter
                )
            if ret.state == "filed":
                raise UserError("TDS return %s is already filed." % ret.quarter)
            ret.write(
                {
                    "state": "filed",
                    "filed_at": fields.Datetime.now(),
                    "nbr_acknowledgment": ack,
                }
            )
            publish(
                self.env,
                "tds_return.filed",
                "fix.tds.return",
                ret.id,
                {
                    "quarter": ret.quarter,
                    "fiscal_year": ret.fiscal_year,
                    "total_withheld": ret.total_withheld,
                    "nbr_acknowledgment": ack,
                },
            )


class FixTdsReturnLine(models.Model):
    """T02 / T04: Detailed withholding line under Section 52/52AA/53A/53F/56."""

    _name = "fix.tds.return.line"
    _description = "TDS Return Detail Line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id asc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    tds_return_id = fields.Many2one(
        "fix.tds.return", string="TDS Return", required=True, ondelete="cascade", index=True
    )

    vendor_name = fields.Char(string="Vendor / Deductee Name", required=True)
    vendor_tin = fields.Char(string="Vendor TIN / e-TIN", size=12)
    vendor_bin = fields.Char(string="Vendor BIN", size=13)
    section_code = fields.Selection(
        [
            ("52", "Sec 52 - Supply of Goods / Execution of Contract"),
            ("52AA", "Sec 52AA - Specified Services"),
            ("53A", "Sec 53A - House Rent"),
            ("53F", "Sec 53F - Commission / Agency"),
            ("56", "Sec 56 - Payment to Non-Residents"),
        ],
        string="Tax Law Section",
        default="52",
        required=True,
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    base_amount = fields.Monetary(
        string="Base Gross Amount", currency_field="currency_id", required=True
    )
    rate_percent = fields.Float(string="TDS Rate (%)", required=True)
    tds_amount = fields.Monetary(
        string="Withheld Tax Amount", currency_field="currency_id", required=True
    )
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

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    # vendor_invoice_id (fix.vendor.invoice, required) is defined by cd_ap_ext
    # (fix_withholding_certificate_ext): cd_ap_ext depends on THIS module, so
    # the pointer to M52's invoice lives on the AP side (cycle finding).
    quarter = fields.Char(related="fix_tds_return_id.quarter", store=False)
    fix_tds_return_id = fields.Many2one(
        "fix.tds.return", string="TDS Return", index=True, ondelete="set null"
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    certificate_type = fields.Selection(
        [
            ("mushak_6_6", "Mushak 6.6 (VAT Deduction at Source - VDS)"),
            ("section_52_income_tax", "Section 52 / Income Tax Withholding"),
        ],
        default="mushak_6_6",
        required=True,
        tracking=True,
    )

    supplier_name = fields.Char(string="Supplier / Deductee Name", required=True)
    supplier_bin = fields.Char(string="Supplier BIN", size=13)
    supplier_tin = fields.Char(string="Supplier TIN", size=12)
    supplier_address = fields.Char(string="Supplier Address")

    base_amount = fields.Monetary(string="Gross Value", currency_field="currency_id", default=0.0)
    rate_percent = fields.Float(string="Tax / VAT Rate (%)", default=0.0)
    withheld_amount = fields.Monetary(
        string="Withheld Amount", currency_field="currency_id", required=True
    )
    challan_no = fields.Char(string="Treasury Challan No")
    challan_date = fields.Date(string="Challan Deposit Date")
    bank_branch = fields.Char(string="Bank & Branch Name")

    certificate_no = fields.Char(string="Certificate No", readonly=True, index=True, copy=False)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("issued", "Issued"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    issued_at = fields.Datetime(readonly=True)

    def action_issue(self) -> None:
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

            cert.write(
                {
                    "certificate_no": seq_no,
                    "state": "issued",
                    "issued_at": fields.Datetime.now(),
                }
            )
            publish(
                self.env,
                "withholding_certificate.issued",
                "fix.withholding.certificate",
                cert.id,
                {
                    "certificate_no": seq_no,
                    "certificate_type": cert.certificate_type,
                    "supplier_name": cert.supplier_name,
                    "supplier_bin": cert.supplier_bin,
                    "amount": float(cert.withheld_amount),
                    "base_amount": float(cert.base_amount),
                },
            )
