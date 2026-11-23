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
from .fix_tax_engine import normalize_bin, valid_bin
from .fix_tax_master import tax_account

FILING_GROUP = "cd_tax_engine_bd.group_tax_filing_approver"
MANAGER_GROUP = "account.group_account_manager"
FINANCE_USER_GROUPS = ("account.group_account_user", "account.group_account_manager")

# The figures and stamps of a return that only its own actions write
# (A08 M51-1: state, the NBR confirmation and the sub-ledger status were
# writable by an accountant, by ORM and by P03).
VAT_RETURN_GUARDED = {
    "state",
    "filed_at",
    "nbr_confirmation",
    "total_taxable",
    "output_vat",
    "input_vat",
    "opening_credit",
    "credit_used",
    "closing_credit",
    "net_payable",
    "nil_return",
    "due_date",
    "subledger_output_variance",
    "subledger_input_variance",
    "subledger_status",
    "subledger_reconciled_at",
    "subledger_notes",
    "treatment_breakdown",
    "classification_notes",
    "prepared_by_id",
    "prepared_at",
    "filed_by_id",
}


def _require_finance(env, what):
    if env.su or any(env.user.has_group(g) for g in FINANCE_USER_GROUPS):
        return
    raise UserError("%s needs the Accountant role." % what)


def _require_filer(env, preparer, what):
    """BRU-TAX-13: a return is filed by the filing approver (CFO), never by
    the person who prepared it."""
    if env.su:
        return
    if not env.user.has_group(FILING_GROUP):
        group = env.ref(FILING_GROUP, raise_if_not_found=False)
        raise UserError(
            "%s needs the %s role (BRU-TAX-13: CFO approval to file)."
            % (what, group.name if group else FILING_GROUP)
        )
    if preparer and env.user == preparer:
        raise UserError(
            "Segregation of duties: you prepared this return; another person (the filing "
            "approver) files it."
        )


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
    bin_no = normalize_bin(company.vat)
    if not re.fullmatch(r"\d{13}", bin_no) or not valid_bin(bin_no):
        raise UserError(
            "Company %s has no valid 13-digit BIN — a VAT return cannot be "
            "prepared or filed without it" % company.name
        )
    return bin_no


# GL accounts the VAT sub-ledger reconciles against (codes in the company's
# chart; overridable per database through ir.config_parameter).
# The account roles live in fix_tax_master.TAX_ACCOUNT_ROLES (vat_output /
# vat_input): the AP posting and this reconciliation read the same ones. A08
# M51-8: the input-VAT role has NO default code any more — 110500 is "Work in
# Progress" in the loaded chart.
VAT_OUTPUT_ACCOUNT_PARAM = "cd_tax_engine_bd.vat_output_account_code"
VAT_INPUT_ACCOUNT_PARAM = "cd_tax_engine_bd.vat_input_account_code"
DEFAULT_VAT_OUTPUT_ACCOUNT = "210100"  # VAT Output Payable


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
    _inherit = ["fix.guarded.mixin", "mail.thread", "mail.activity.mixin"]
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
    opening_credit = fields.Monetary(
        string="Opening Input Credit",
        currency_field="currency_id",
        readonly=True,
        help="Input VAT credit carried in from the previous filed return for this company "
        "(FR-TAX-018/029). A first period opens at 0.00.",
    )
    credit_used = fields.Monetary(
        string="Credit Used",
        currency_field="currency_id",
        readonly=True,
        help="Opening credit consumed against this period's output VAT: "
        "min(opening credit, max(0, output - input)).",
    )
    closing_credit = fields.Monetary(
        string="Closing Input Credit",
        currency_field="currency_id",
        readonly=True,
        help="Input VAT credit carried forward to the next period: the unused opening "
        "credit plus any excess of input VAT over output VAT (FR-TAX-018/029).",
    )
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
        help="Variance between the Output VAT register and the configured VAT output GL "
        "account (cd_tax_engine_bd.vat_output_account_code; must be 0.00)",
    )
    subledger_input_variance = fields.Monetary(
        string="Input VAT Variance",
        currency_field="currency_id",
        readonly=True,
        help="Variance between the Input VAT register and the configured VAT input GL "
        "account (cd_tax_engine_bd.vat_input_account_code; must be 0.00)",
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
    prepared_by_id = fields.Many2one("res.users", string="Prepared By", readonly=True, copy=False)
    prepared_at = fields.Datetime(string="Prepared On", readonly=True, copy=False)
    filed_by_id = fields.Many2one("res.users", string="Filed By", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | VAT_RETURN_GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= {"period", "company_id", "operating_unit_id", "currency_id"}
        return locked

    def _register_totals(self) -> dict[str, tuple[Decimal, Decimal]]:
        """The per-treatment totals the return was prepared with."""
        self.ensure_one()
        raw = json.loads(self.treatment_breakdown or "{}")
        return {k: (Decimal(str(v[0])), Decimal(str(v[1]))) for k, v in raw.items()}

    @api.model
    def _previous_filed_return(self, company, period):
        """The latest FILED return of this company before `period` — the
        return whose closing input credit this period opens with. It is the
        tie-out (FR-TAX-018/029, AC-26): the opening balance must agree to
        the last filed Mushak 9.1, never to a book balance."""
        return self.sudo().search(
            [
                ("company_id", "=", company.id),
                ("state", "=", "filed"),
                ("period", "<", period),
            ],
            order="period desc",
            limit=1,
        )

    @api.model
    def _opening_input_credit(self, company, period) -> Decimal:
        """Opening input VAT credit for a period: the previous filed return's
        closing credit, or zero for a company's first period."""
        previous = self._previous_filed_return(company, period)
        return Decimal(str(previous.closing_credit or 0.0)).quantize(Decimal("0.01"))

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

        Input-credit ledger (FR-TAX-018/029): the previous FILED return's
        closing credit is carried in automatically; this period consumes it
        against output VAT and stores the remainder as ``closing_credit`` so
        net payable is never negative.
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
        opening_credit = self._opening_input_credit(company, period)
        prepared = return_logic.prepare_vat_return(
            _company_bin(company),
            period,
            register_totals,
            input_vat=Decimal(str(input_vat)),
            opening_credit=opening_credit,
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
        _require_finance(self.env, "Preparing a VAT return")
        record: FixVatReturn = self._guarded().create(
            {
                "prepared_by_id": self.env.uid,
                "prepared_at": fields.Datetime.now(),
                "company_id": company.id,
                "period": period,
                "total_taxable": float(prepared.total_taxable),
                "output_vat": float(prepared.total_output_vat),
                "input_vat": float(prepared.total_input_vat),
                "opening_credit": float(prepared.opening_credit),
                "credit_used": float(prepared.credit_used),
                "closing_credit": float(prepared.closing_credit),
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
        return record.with_env(self.env)

    def _fix_assert_credit_continuity(self) -> None:
        """FR-TAX-018/029, AC-26: the opening input credit of a filed period
        must be exactly the closing credit of the previous filed return for
        the same company. This is the tie-out that prevents silent credit
        loss (or silent double-use): a tampered or stale opening balance is
        refused, naming both figures. A company's FIRST filed period is
        exempt because there is nothing to carry in."""
        for ret in self:
            previous = ret._previous_filed_return(ret.company_id, ret.period)
            if not previous:
                continue
            opening = Decimal(str(ret.opening_credit or 0.0)).quantize(Decimal("0.01"))
            closing = Decimal(str(previous.closing_credit or 0.0)).quantize(Decimal("0.01"))
            if abs(opening - closing) > Decimal("0.005"):
                raise UserError(
                    "Return %s opens with an input credit of %.2f, but the previous filed "
                    "return %s closes with %.2f. The difference (%.2f) would be lost or "
                    "double-used: re-prepare this return from the filed return before "
                    "filing (FR-TAX-018/029, BRU-TAX-06, AC-26)."
                    % (
                        ret.period,
                        opening,
                        previous.period,
                        closing,
                        opening - closing,
                    )
                )

    def _fix_assert_fileable(self):
        """BRU-TAX-12/13 (A08 M51-1): only a PREPARED return whose sub-ledger
        reconciles — recomputed now, by the system, against the posted GL —
        and whose every supply is classified, filed by the filing approver
        who did not prepare it."""
        for ret in self:
            if ret.state == "filed":
                raise UserError("Return for period %s is already filed." % ret.period)
            if ret.state != "prepared":
                raise UserError(
                    "Return %s is %s: prepare it from the registers before filing."
                    % (ret.period, ret.state)
                )
            _require_filer(ret.env, ret.prepared_by_id, "Filing the Mushak 9.1")
            ret._fix_assert_credit_continuity()
            _company_bin(ret.company_id)
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
            # The register is re-read at filing (BRU-TAX-12): rows written
            # after the last Prepare — Mushak 6.7/6.8 notes, event-driven
            # adoptions — change the period's declaration without touching
            # the stored snapshot or (for GL-less writes) the GL, so the
            # preparation snapshot alone can never prove fileability.
            start, next_start = _period_bounds(ret.period)
            live_rows = self.env["fix.mushak.register"].search(
                [
                    ("company_id", "=", ret.company_id.id),
                    ("invoice_date", ">=", start),
                    ("invoice_date", "<", next_start),
                ]
            )
            live_totals = return_logic.aggregate_register(
                [(r.taxable_amount, r.vat_amount, r.treatment_summary or "") for r in live_rows]
            )
            live_unclassified = sorted(
                k for k in live_totals if k.startswith(return_logic.UNCLASSIFIED_PREFIX)
            )
            if live_unclassified:
                raise UserError(
                    "The Mushak register for %s now holds supplies with no determinable "
                    "VAT treatment (%s) — classify them and re-prepare before filing."
                    % (ret.period, ", ".join(live_unclassified))
                )
            live_taxable = sum((t for t, _ in live_totals.values()), Decimal("0"))
            live_vat = sum((v for _, v in live_totals.values()), Decimal("0"))
            if live_taxable.quantize(Decimal("0.01")) != line_taxable.quantize(
                Decimal("0.01")
            ) or live_vat.quantize(Decimal("0.01")) != line_vat.quantize(Decimal("0.01")):
                raise UserError(
                    "The Mushak register for %s changed after this return was prepared — "
                    "re-prepare it from the register before filing." % ret.period
                )
            ret.sudo().action_subledger_reconciliation()
            if ret.subledger_status != "reconciled":
                raise UserError(
                    "Cannot file return %s: the VAT sub-ledger does not reconcile to the GL "
                    "(%s). IRB-09 strictly prohibits absorbing variances."
                    % (ret.period, ret.subledger_notes or ret.subledger_status)
                )

    def action_file(self, nbr_confirmation: str = "") -> None:
        """T03 (INT-038): filing is ONLINE-ONLY since 1 July 2026. A typed
        confirmation is not a verified submission (A08 M51-1: a never-
        prepared return was filed on "TYPED-12345"): users file through
        action_file_online, whose acknowledgement comes from NBR IVAS. This
        entry point remains for trusted system code (an adapter callback
        carrying the IVAS token) and applies the same gate."""
        if not self.env.su:
            raise UserError(
                "The Mushak 9.1 is filed online through NBR IVAS (File Online): the "
                "acknowledgement is the one IVAS returns. A typed confirmation is not "
                "accepted."
            )
        for ret in self:
            if not nbr_confirmation:
                raise UserError(
                    "Filing requires the NBR portal confirmation reference — "
                    "manual filing was abolished 1 July 2026"
                )
            ret._fix_assert_fileable()
            ret._guarded().write(
                {
                    "state": "filed",
                    "filed_at": fields.Datetime.now(),
                    "nbr_confirmation": nbr_confirmation,
                    "filed_by_id": self.env.uid,
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
        # A08 M51-1: prepared, reconciled (recomputed now), filer != preparer
        ret._fix_assert_fileable()

        taxpayer_bin = _company_bin(ret.company_id)
        register_totals = ret._register_totals()
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

        if not (submission.ack_token or "").strip():
            raise UserError("NBR IVAS accepted return %s without an acknowledgement" % ret.period)
        ret._guarded().write(
            {
                "state": "filed",
                "filed_at": fields.Datetime.now(),
                "nbr_confirmation": submission.ack_token,
                "filed_by_id": self.env.uid,
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
        # The same account roles the AP / AR postings use (A08 M51-8): the
        # input-VAT role has no default, so an unconfigured chart refuses here.
        out_acc = tax_account(self.env, self.company_id, "vat_output")
        in_acc = tax_account(self.env, self.company_id, "vat_input")
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

    def _gl_vat_account_codes(self) -> tuple[str | None, str | None]:
        """The codes of the VAT output / input accounts the GL side is read
        from, for the variance message (fix_real: 200902 / 200901). The GL
        read (_gl_vat_balances) is what refuses an unconfigured role; a code
        that cannot be resolved here is left unnamed, never invented."""
        self.ensure_one()
        codes = []
        for role in ("vat_output", "vat_input"):
            try:
                account = tax_account(self.env, self.company_id, role)
            except UserError:
                codes.append(None)
                continue
            codes.append(account.with_company(self.company_id).code or None)
        return codes[0], codes[1]

    def action_subledger_reconciliation(self) -> None:
        """T02: the VAT sub-ledger — register output VAT vs the configured VAT output
        account and input VAT vs the configured VAT input account (fix_real: 200902 /
        200901); the variance message names those accounts. A variance is RAISED,
        never silently absorbed.

        The GL side is ALWAYS read from posted account.move.line for the
        period. (Previously, called without GL figures — as the form button
        does — the return was compared with itself and always "reconciled".)
        Missing GL accounts refuse the reconciliation."""
        _require_finance(self.env, "Reconciling the VAT sub-ledger")
        for ret in self:
            if ret.state == "draft":
                raise UserError("Prepare return %s before reconciling it" % ret.period)
            target_gl_output, target_gl_input = ret.sudo()._gl_vat_balances()
            out_code, in_code = ret.sudo()._gl_vat_account_codes()

            recon = return_logic.reconcile_vat_subledger(
                period=ret.period,
                register_output_vat=ret.output_vat,
                gl_210100_output_vat=target_gl_output,
                register_input_vat=ret.input_vat,
                gl_110500_input_vat=target_gl_input,
                output_account_code=out_code,
                input_account_code=in_code,
            )

            status = "reconciled" if recon.is_reconciled else "variance_detected"
            notes = (
                "; ".join(recon.notes)
                if recon.notes
                else "Full alignment between Mushak sub-ledger and General Ledger."
            )

            ret._guarded().write(
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
    _inherit = ["fix.guarded.mixin", "mail.thread", "mail.activity.mixin"]
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
    prepared_by_id = fields.Many2one("res.users", string="Prepared By", readonly=True, copy=False)
    filed_by_id = fields.Many2one("res.users", string="Filed By", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        # A08 M51-1 (W11/W12): state and the computed totals move only by the
        # return's actions.
        return super()._fix_guarded_fields() | {
            "state",
            "filed_at",
            "fiscal_year",
            "total_withheld",
            "deductor_count",
            "due_date",
            "prepared_by_id",
            "filed_by_id",
        }

    def write(self, vals):
        if self and not self._fix_guard_open():
            filed = self.filtered(lambda r: r.state == "filed")
            moving = {k for k in vals if not k.startswith(("message_", "activity_"))}
            if filed and any(
                r._fix_guard_differs(n, vals[n], r[n])
                for r in filed
                for n in moving
                if n in r._fields
            ):
                raise UserError("TDS return %s is filed and cannot change" % filed[:1].quarter)
        return super().write(vals)

    @api.model
    def action_prepare_quarter(
        self, withheld_by_vendor: dict[str, Decimal], any_date_in_quarter: date
    ) -> "FixTdsReturn":
        _require_finance(self.env, "Preparing a TDS return")
        prepared = return_logic.prepare_tds_return(withheld_by_vendor, any_date_in_quarter)
        existing: FixTdsReturn = self.search(
            [("company_id", "=", self.env.company.id), ("quarter", "=", prepared.quarter)]
        )
        if existing:
            return existing
        record: FixTdsReturn = self._guarded().create(
            {
                "quarter": prepared.quarter,
                "fiscal_year": prepared.fiscal_year,
                "total_withheld": float(prepared.total_withheld),
                "deductor_count": prepared.deductor_count,
                "due_date": prepared.due_date,
                "state": "prepared",
                "prepared_by_id": self.env.uid,
            }
        )
        return record.with_env(self.env)

    def action_file(self, nbr_acknowledgment: str = "") -> None:
        """Mark the TDS quarterly return as filed with the NBR tax circle.

        Requires the REAL acknowledgment number NBR issued — passed in, or
        entered on the return's ``nbr_acknowledgment`` field before pressing
        the button. (Previously a missing acknowledgment was replaced by a
        self-minted ``NBR-TDS-<quarter>-<id>``, recording a filing NBR never
        acknowledged.) A08 M51-1: only a PREPARED return whose every
        deduction is deposited by challan, filed by the filing approver who
        did not prepare it."""
        for ret in self:
            ack = (nbr_acknowledgment or ret.nbr_acknowledgment or "").strip()
            if not ack:
                raise UserError(
                    "Enter the NBR acknowledgment number for TDS return %s before "
                    "marking it filed — it cannot be generated locally." % ret.quarter
                )
            if ret.state == "filed":
                raise UserError("TDS return %s is already filed." % ret.quarter)
            if ret.state != "prepared":
                raise UserError(
                    "TDS return %s is %s: prepare it from the deductions before filing."
                    % (ret.quarter, ret.state)
                )
            _require_filer(ret.env, ret.prepared_by_id, "Filing the TDS return")
            undeposited = ret.line_ids.filtered(
                lambda ln: (
                    not ln.challan_no
                    or (
                        "withholding_line_id" in ln._fields
                        and ln.withholding_line_id
                        and ln.withholding_line_id.state not in ("deposited", "certified")
                    )
                )
            )
            if undeposited:
                raise UserError(
                    "TDS return %s reports %d deduction(s) not yet deposited by challan: "
                    "deposit them, re-prepare, then file." % (ret.quarter, len(undeposited))
                )
            ret._guarded().write(
                {
                    "state": "filed",
                    "filed_at": fields.Datetime.now(),
                    "nbr_acknowledgment": ack,
                    "filed_by_id": self.env.uid,
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
    _inherit = ["fix.guarded.mixin", "mail.thread", "mail.activity.mixin"]
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
    source_model = fields.Char(
        string="Source Model",
        readonly=True,
        help="The model of the payment the certified deduction was withheld from "
        "(fix.vendor.invoice for AP; another payment source such as an A05 trade-in payout).",
    )
    source_ref = fields.Char(string="Source Document", readonly=True)

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
    withholding_line_ids = fields.One2many(
        "fix.withholding.line", "certificate_id", string="Deductions Certified", readonly=True
    )

    # ---------------------------------------------------------------- guard --
    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "certificate_no", "issued_at"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= {n for n, f in self._fields.items() if f.store}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            # A08 M51-4 (W03): a free-standing Mushak 6.6 was issued with no
            # deduction, no challan, base 0 and BIN 0000000000000.
            raise UserError(
                "A withholding certificate is issued from the deduction its challan "
                "deposited (Issue Certificate on the deduction), never created by hand."
            )
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            issued = self.filtered(lambda c: c.state != "draft")
            moving = {k for k in vals if not k.startswith(("message_", "activity_"))}
            if issued and any(
                c._fix_guard_differs(n, vals[n], c[n])
                for c in issued
                for n in moving
                if n in c._fields
            ):
                raise UserError(
                    "Certificate %s is %s: an issued certificate is never edited (W08)."
                    % (issued[:1].certificate_no, issued[:1].state)
                )
        return super().write(vals)

    def action_issue(self) -> None:
        """Issue certificate with statutory numbering and validation — only
        for the deductions it certifies, each deposited by a verified challan
        (A08 M51-4)."""
        for cert in self:
            if cert.state == "issued":
                continue
            lines = cert.sudo().withholding_line_ids
            if not lines:
                raise UserError(
                    "Certificate %s certifies no deduction: it is issued from a deposited "
                    "deduction only." % (cert.certificate_no or cert.id)
                )
            for line in lines:
                challan = line.challan_id
                if (
                    line.state not in ("deposited", "certified")
                    or not challan
                    or challan.state != "deposited"
                    or not challan.verified_by_id
                    or challan.challan_no != cert.challan_no
                ):
                    raise UserError(
                        "Deduction %s is not deposited by the verified challan %s"
                        % (line.source_ref or line.id, cert.challan_no or "-")
                    )

            if cert.certificate_type == "mushak_6_6":
                bin_str = (cert.supplier_bin or "").strip()
                if not valid_bin(bin_str):
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

            cert._guarded().write(
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
