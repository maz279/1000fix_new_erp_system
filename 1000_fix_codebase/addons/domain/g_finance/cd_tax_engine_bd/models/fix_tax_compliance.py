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
from .fix_tax_master import (
    MANAGER_GROUP,
    add_months,
    float_param,
    period_of,
    tax_account,
    tax_alert,
)

TWO = Decimal("0.01")
FINANCE_USER_GROUPS = ("account.group_account_user", "account.group_account_manager")
RATIO_TOLERANCE_PARAM = "cd_tax_engine_bd.input_vat_ratio_tolerance"
RATIO_TOLERANCE_DEFAULT = 1.0  # BDT: per-line rounding on the supplier's 6.3
# BRU-TAX-10 says "the statutory window" and gives no number: 0 reminds from the
# day of the deposit. The adviser's figure goes here.
CERTIFICATE_WINDOW_PARAM = "cd_tax_engine_bd.certificate_window_days"


def require_finance(env, what):
    if env.su or any(env.user.has_group(g) for g in FINANCE_USER_GROUPS):
        return
    raise UserError("%s needs the Accountant role." % what)


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
    Move = env["account.move"]
    if hasattr(Move, "_fix_post_via_m19"):  # B3's documented M19 API
        return Move._fix_post_via_m19(move_vals, source, source_ref=ref, dimension_by_line=dims)
    move, _dims = post_with_dimensions(env, move_vals, dims, source=source)
    return move


class FixWithholdingLine(models.Model):
    """One TDS or VDS deduction: who, on what base, at which effective-dated
    rate (with the ITA 2023 section / VAT service code), and where the money
    went (challan) and which certificate covers it."""

    _name = "fix.withholding.line"
    _description = "TDS / VDS Deduction"
    _inherit = ["fix.guarded.mixin", "mail.thread", "mail.activity.mixin"]
    _order = "document_date desc, id desc"
    _rec_name = "source_ref"

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
    # A08 M51-7 (W07): both evidence flags default to the UNFAVOURABLE value —
    # a deduction that states no PSR / bank evidence suffers the uplift.
    psr_received = fields.Boolean(
        string="PSR on file",
        default=False,
        help="Proof of Submission of Return held on the document date (s.142). "
        "Missing PSR raises the rate by 50%.",
    )
    paid_by_bank = fields.Boolean(
        string="Paid through bank",
        default=False,
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
    source_model = fields.Char(
        string="Source Model",
        index=True,
        help="The model of the payment the deduction was withheld from (fix.vendor.invoice "
        "for AP bills; e.g. a trade-in payout for A05). Empty = an AP vendor bill.",
    )
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
    move_id = fields.Many2one(
        "account.move",
        string="Liability Entry",
        readonly=True,
        copy=False,
        index=True,
        help="The posted GL entry that credits the TDS / VDS payable for this deduction "
        "(the vendor bill's posting).",
    )
    rate_flagged = fields.Boolean(
        string="Rate Unconfirmed",
        compute="_compute_rate_flagged",
        help="The rate row this deduction cites is not signed off by the adviser and the CFO.",
    )
    duplicate_refs = fields.Char(
        string="Duplicate Of",
        compute="_compute_duplicate_refs",
        help="Other live deductions of the same tax, payee and bill.",
    )
    duplicate_cleared_by_id = fields.Many2one(
        "res.users", string="Not a Duplicate, Per", readonly=True, copy=False
    )
    duplicate_cleared_reason = fields.Char(
        string="Why It Is Not a Duplicate", readonly=True, copy=False
    )
    # A08 M51-4/-8: the only way out of a phantom "certified" state, and the only
    # way a duplicate deduction stops counting: one person asks with a reason, a
    # different Accounting Administrator applies it.
    correction_kind = fields.Selection(
        [("void", "Void this Duplicate"), ("reopen", "Reopen as Withheld")],
        string="Correction",
        readonly=True,
        copy=False,
        tracking=True,
    )
    correction_state = fields.Selection(
        [("requested", "Requested"), ("applied", "Applied"), ("rejected", "Rejected")],
        readonly=True,
        copy=False,
        tracking=True,
    )
    correction_reason = fields.Char(readonly=True, copy=False, tracking=True)
    correction_requested_by_id = fields.Many2one(
        "res.users", string="Correction Requested By", readonly=True, copy=False
    )
    correction_decided_by_id = fields.Many2one(
        "res.users", string="Correction Decided By", readonly=True, copy=False
    )
    correction_decided_at = fields.Datetime(readonly=True, copy=False)

    # ---------------------------------------------------------------- guard --
    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "certificate_id",
            "move_id",
            "duplicate_cleared_by_id",
            "duplicate_cleared_reason",
            "correction_kind",
            "correction_state",
            "correction_reason",
            "correction_requested_by_id",
            "correction_decided_by_id",
            "correction_decided_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "withheld":
            locked |= {n for n, f in self._fields.items() if f.store}
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        Rate = self.env["fix.tax.rate"].sudo()
        for vals in vals_list:
            rate = Rate.browse(vals["rate_id"]) if vals.get("rate_id") else Rate
            if rate and "rate" not in vals:
                vals["rate"] = rate.rate
            if rate and not vals.get("section"):
                vals["section"] = rate.section
            uplifted = vals.get("tax_kind") != "vds" and (not rate or rate.non_filer_applies)
            if "multiplier" not in vals and not uplifted:
                vals["multiplier"] = 1.0
            if "multiplier" not in vals:
                defaults = 0
                if not vals.get("psr_received", False) or vals.get("non_filer"):
                    defaults += 1
                if not vals.get("paid_by_bank", False):
                    defaults += 1
                if not (vals.get("partner_tin") or "").strip():
                    defaults += 1
                vals["multiplier"] = round(1.5**defaults, 3)
        if not self._fix_guard_open():
            # A08 M51-8: a deduction is the tax side of a posted liability.
            raise UserError(
                "A TDS / VDS deduction is recorded with the GL entry that posts its "
                "liability (the approved vendor bill), through "
                "fix.withholding.line._fix_record_deductions(vals, move) — never typed."
            )
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            done = self.filtered(lambda line: line.state != "withheld")
            moving = {k for k in vals if not k.startswith(("message_", "activity_"))}
            if done and moving:
                changed = {
                    name
                    for line in done
                    for name in moving
                    if name in line._fields
                    and line._fix_guard_differs(name, vals[name], line[name])
                }
                if changed:
                    raise UserError(
                        "Deduction %s is %s: a deposited or certified deduction is never "
                        "edited." % (done[:1].source_ref or done[:1].id, done[:1].state)
                    )
        return super().write(vals)

    @api.model
    def _fix_record_deductions(self, vals_list, move):
        """CONTRACT (B5 -> B2, A08 M51-8): record the TDS / VDS deductions of a
        POSTED liability entry (the approved vendor bill's posting). The entry
        must credit the configured TDS / VDS payable account with at least the
        deductions recorded against it, so no deduction exists without its GL
        liability. Returns the lines in the caller's environment."""
        if not move or move.state != "posted":
            raise UserError("Deductions are recorded against a POSTED GL entry")
        vals_list = [dict(vals, move_id=move.id) for vals in vals_list]
        lines = self._guarded().create(vals_list)
        return self.browse(lines.ids)

    @api.constrains("move_id", "amount", "tax_kind", "state")
    def _check_gl_liability(self):
        for move in self.mapped("move_id"):
            lines = self.sudo().search([("move_id", "=", move.id), ("state", "!=", "cancelled")])
            if move.state != "posted":
                raise ValidationError("The liability entry %s is not posted" % move.name)
            for kind in set(lines.mapped("tax_kind")):
                account = tax_account(self.env, move.company_id, "%s_payable" % kind)
                credited = sum(
                    move.sudo()
                    .line_ids.filtered(lambda ml, a=account: ml.account_id == a)
                    .mapped("credit")
                )
                owed = sum(lines.filtered(lambda ln, k=kind: ln.tax_kind == k).mapped("amount"))
                if money(owed) > money(credited) + 0.01:
                    raise ValidationError(
                        "%s deductions of %.2f exceed the %.2f the entry %s credits to %s: "
                        "every deduction posts its liability to the GL."
                        % (kind.upper(), owed, credited, move.name, account.display_name)
                    )

    @api.constrains("rate", "rate_id")
    def _check_rate_row(self):
        for line in self:
            row = line.rate_id.sudo()
            if row and abs((line.rate or 0.0) - row.rate) > 0.0005:
                raise ValidationError(
                    "The deduction cites rate row %s (%g%%) but withholds at %g%%: the "
                    "rate comes from the Tax Rate Master." % (row.display_name, row.rate, line.rate)
                )

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
        "tax_kind",
        "rate_id.non_filer_applies",
    )
    def _compute_uplift(self):
        """ITA 2023: each of the three defaults multiplies the statutory rate by 1.5.
        The components stay visible so the certificate and the register can state
        exactly which default applied. The uplift is an INCOME-TAX rule: a VDS
        (VAT at source) line, or a rate row the master marks non_filer_applies =
        False, carries no default (and so no multiplier floor)."""
        for line in self:
            defaults = 0
            if line.tax_kind == "vds" or (
                line.rate_id and not line.rate_id.sudo().non_filer_applies
            ):
                line.defaults_count = 0
                line.effective_rate = round((line.rate or 0.0) * (line.multiplier or 1.0), 3)
                line.expected_amount = round(
                    (line.base_amount or 0.0) * line.effective_rate / 100.0, 2
                )
                shortfall = round(line.expected_amount - (line.amount or 0.0), 2)
                line.statutory_shortfall = shortfall if shortfall > 0.5 else 0.0
                continue
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
        """A deduction equals base x effective rate, and its multiplier is never
        below 1.5 per recorded default (A08 M51-7, W06: a new no-TIN row at x1.0
        used to pass as a "legacy row"; the context bypass is gone too).
        Constraints run when these fields are written, so historical rows are
        re-checked only when edited; action_apply_statutory_uplift brings one
        to the statutory minimum."""
        for line in self:
            if line.state == "cancelled":
                continue
            minimum = round(1.5 ** (line.defaults_count or 0), 3)
            if (line.multiplier or 1.0) < minimum - 1e-6:
                raise ValidationError(
                    "Multiplier %.3f is below the statutory %.3f for %d default(s) (missing "
                    "PSR / cash payment / no TIN, ITA 2023): the deduction would "
                    "under-withhold." % (line.multiplier or 1.0, minimum, line.defaults_count)
                )
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
        require_finance(self.env, "Applying the statutory uplift")
        for line in self:
            if line.state != "withheld":
                raise UserError("Only an undeposited deduction is remediated")
            minimum = round(1.5 ** (line.defaults_count or 0), 3)
            amount = round((line.base_amount or 0.0) * (line.rate or 0.0) * minimum / 100.0, 2)
            line.write({"multiplier": minimum, "amount": amount})

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
            # the payment the certificate covers: an AP bill or another source
            # (A05 trade-in payouts) — the certificate is never free-standing
            "source_model": self.source_model or False,
            "source_ref": self.source_ref or False,
            "challan_no": self.challan_id.challan_no,
            "challan_date": self.challan_id.challan_date,
            "bank_branch": " / ".join(
                p for p in (self.challan_id.bank_name, self.challan_id.bank_branch) if p
            )
            or False,
        }

    def _compute_rate_flagged(self):
        for line in self:
            row = line.rate_id.sudo()
            line.rate_flagged = bool(row) and row.signoff_state != "signed"

    # ------------------------------------------------- duplicates and corrections --
    @staticmethod
    def _fix_bill_key(source_ref):
        """The bill a deduction was withheld from, however its source was written:
        one series says 'ACME-1180', its duplicate says 'Bill ACME-1180'."""
        return re.sub(r"^bill\s+", "", (source_ref or "").strip(), flags=re.I).upper()

    def _fix_duplicates(self):
        """Other live deductions of the same tax, payee and bill. Which one is
        right is a person's decision; this only says there are two."""
        self.ensure_one()
        key = self._fix_bill_key(self.source_ref)
        if not key or self.duplicate_cleared_by_id or self.state == "cancelled":
            return self.browse()
        others = self.sudo().search(
            [
                ("id", "!=", self.id),
                ("company_id", "=", self.company_id.id),
                ("tax_kind", "=", self.tax_kind),
                ("partner_id", "=", self.partner_id.id),
                ("state", "!=", "cancelled"),
                ("duplicate_cleared_by_id", "=", False),
            ]
        )
        return others.filtered(lambda o, k=key: self._fix_bill_key(o.source_ref) == k)

    def _compute_duplicate_refs(self):
        for line in self:
            dups = line._fix_duplicates() if line.id else line.browse()
            line.duplicate_refs = ", ".join(
                "#%s %.2f (%s)" % (d.id, d.amount, d.state) for d in dups
            )

    def _fix_refuse_void(self):
        self.ensure_one()
        if self.state == "cancelled":
            raise UserError("Deduction #%s is already void." % self.id)
        if self.certificate_id or self.challan_id:
            raise UserError(
                "Deduction #%s has a %s: it is not voided."
                % (self.id, "certificate" if self.certificate_id else "challan")
            )
        if self.move_id:
            raise UserError(
                "Deduction #%s carries the liability of %s: reverse that entry at its bill; it "
                "is not voided here." % (self.id, self.move_id.display_name)
            )
        if not self._fix_duplicates():
            raise UserError(
                "Deduction #%s is not a duplicate: only a duplicate is voided. A wrong deduction "
                "is corrected at its bill." % self.id
            )
        filed = (
            self.env["fix.tds.return.line"]
            .sudo()
            .search_count(
                [("withholding_line_id", "=", self.id), ("tds_return_id.state", "=", "filed")]
            )
        )
        if filed:
            raise UserError("Deduction #%s is on a filed TDS return." % self.id)

    def _fix_refuse_reopen(self):
        self.ensure_one()
        if self.state not in ("certified", "deposited"):
            raise UserError("Only a deduction marked deposited or certified is reopened.")
        if self.certificate_id or self.challan_id:
            raise UserError(
                "Deduction #%s has a %s: its state is real and it is not reopened."
                % (self.id, "certificate" if self.certificate_id else "challan")
            )

    def _fix_request_correction(self, kind, reason):
        require_finance(self.env, "Requesting a correction of a deduction")
        why = (reason or "").strip()
        if not why:
            raise UserError("State the reason for the correction.")
        for line in self:
            if line.correction_state == "requested":
                raise UserError("Deduction #%s already has a correction waiting." % line.id)
            (line._fix_refuse_void if kind == "void" else line._fix_refuse_reopen)()
            line._guarded().write(
                {
                    "correction_kind": kind,
                    "correction_state": "requested",
                    "correction_reason": why,
                    "correction_requested_by_id": self.env.uid,
                    "correction_decided_by_id": False,
                    "correction_decided_at": False,
                }
            )
        return True

    def action_request_void(self, reason=None):
        """Ask to void this deduction as the duplicate of another."""
        return self._fix_request_correction("void", reason)

    def action_request_reopen(self, reason=None):
        """Ask to put back to withheld a deduction marked deposited or certified
        with neither challan nor certificate behind it."""
        return self._fix_request_correction("reopen", reason)

    def _fix_require_second_person(self, what):
        if not self.env.su and not self.env.user.has_group(MANAGER_GROUP):
            raise UserError("%s needs the Accounting Administrator role." % what)
        for line in self:
            if not self.env.su and self.env.user in (
                line.correction_requested_by_id | line.create_uid
            ):
                raise UserError(
                    "Segregation of duties: %s must be done by someone other than who recorded "
                    "deduction #%s or asked for this." % (what, line.id)
                )

    def action_approve_correction(self):
        """The second person applies the requested void or reopen, re-checked now."""
        self._fix_require_second_person("Applying a deduction correction")
        for line in self:
            if line.correction_state != "requested":
                raise UserError("Deduction #%s has no correction waiting." % line.id)
            void = line.correction_kind == "void"
            (line._fix_refuse_void if void else line._fix_refuse_reopen)()
            line._guarded().write(
                {
                    "state": "cancelled" if void else "withheld",
                    "correction_state": "applied",
                    "correction_decided_by_id": self.env.uid,
                    "correction_decided_at": fields.Datetime.now(),
                }
            )
            line.message_post(
                body="%s by %s, requested by %s: %s"
                % (
                    "Voided as a duplicate" if void else "Reopened as withheld",
                    self.env.user.name,
                    line.correction_requested_by_id.name,
                    line.correction_reason,
                )
            )
        return True

    def action_reject_correction(self, reason=None):
        self._fix_require_second_person("Rejecting a deduction correction")
        why = (reason or "").strip()
        if not why:
            raise UserError("State why the correction is rejected.")
        for line in self:
            if line.correction_state != "requested":
                raise UserError("Deduction #%s has no correction waiting." % line.id)
            line._guarded().write(
                {
                    "correction_state": "rejected",
                    "correction_decided_by_id": self.env.uid,
                    "correction_decided_at": fields.Datetime.now(),
                }
            )
            line.message_post(body="Correction rejected by %s: %s" % (self.env.user.name, why))
        return True

    def action_clear_duplicate(self, reason=None):
        """An Accounting Administrator who did not record it says the second
        deduction on this bill is genuine (two sections on one bill, say)."""
        self._fix_require_second_person("Clearing a duplicate flag")
        why = (reason or "").strip()
        if not why:
            raise UserError("State why this is not a duplicate.")
        for line in self:
            if not line._fix_duplicates():
                raise UserError("Deduction #%s is not flagged as a duplicate." % line.id)
            line._guarded().write(
                {"duplicate_cleared_by_id": self.env.uid, "duplicate_cleared_reason": why}
            )
        return True

    @api.model
    def _cron_certificate_window(self):
        """BRU-TAX-10 / AUT-TAX-09 (ir.cron, daily): a deduction deposited by challan
        with no certificate past the window is a to-do for the Accounting
        Administrators. Issues nothing, posts nothing."""
        window = int(float_param(self.env, CERTIFICATE_WINDOW_PARAM, 0))
        today = fields.Date.context_today(self)
        due = self.sudo().search([("state", "=", "deposited"), ("certificate_id", "=", False)])
        count = 0
        for line in due.filtered(
            lambda ln: ln.challan_id.challan_date
            and (today - ln.challan_id.challan_date).days >= window
        ):
            count += len(
                tax_alert(
                    line,
                    line.company_id,
                    "Withholding certificate due",
                    "Deduction #%s (%s, %.2f) was deposited by challan %s on %s; its certificate "
                    "is not issued."
                    % (
                        line.id,
                        line.partner_id.display_name,
                        line.amount,
                        line.challan_no,
                        line.challan_date,
                    ),
                    [MANAGER_GROUP],
                )
            )
        return count

    def action_issue_certificate(self):
        """Issue the deductee certificate (Mushak 6.6 for VDS, the income-tax
        withholding certificate for TDS) — only once the money is deposited:
        the certificate states the challan. A08 M51-4: a certificate exists
        only through this action, for a deduction its verified challan paid."""
        require_finance(self.env, "Issuing a withholding certificate")
        for line in self:
            if line.state != "deposited":
                raise UserError(
                    "Deduction %s is %s — a certificate is issued after the challan deposit"
                    % (line.source_ref or line.id, line.state)
                )
            challan = line.challan_id
            if not challan or challan.state != "deposited" or not challan.verified_by_id:
                raise UserError(
                    "Deduction %s has no deposited, verified challan — no certificate"
                    % (line.source_ref or line.id)
                )
            cert = (
                self.env["fix.withholding.certificate"]._guarded().create(line._certificate_vals())
            )
            line._guarded().write({"certificate_id": cert.id})
            cert.action_issue()
            line._guarded().write({"state": "certified"})
        return True


class FixTaxChallan(models.Model):
    """A-challan / e-payment deposit settling VAT, TDS or VDS liabilities.
    The challan number and date come from the bank receipt (user-entered)."""

    _name = "fix.tax.challan"
    _description = "Tax Challan (A-Challan / e-Payment)"
    _inherit = ["fix.guarded.mixin", "mail.thread", "mail.activity.mixin"]
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
    # A08 M51-11: the challan number was typed and never checked. The deposit
    # is confirmed only after a second person records the verification of the
    # receipt (iBAS++ / bank e-payment confirmation reference).
    verification_ref = fields.Char(
        string="Receipt Verification",
        readonly=True,
        copy=False,
        help="Reference of the iBAS++ / bank confirmation the challan was verified against",
    )
    verified_by_id = fields.Many2one("res.users", string="Verified By", readonly=True, copy=False)
    verified_at = fields.Datetime(string="Verified On", readonly=True, copy=False)
    receipt_reference = fields.Char(
        string="iBAS++ / Bank Confirmation",
        copy=False,
        help="The confirmation reference of the receipt, recorded by the verifier",
    )

    _VERIFIED_TERMS = frozenset(
        {
            "challan_no",
            "challan_date",
            "amount",
            "tax_kind",
            "period",
            "vat_return_id",
            "payment_mode",
            "bank_name",
            "bank_branch",
            "economic_code",
        }
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "move_id",
            "verification_ref",
            "verified_by_id",
            "verified_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= {n for n, f in self._fields.items() if f.store}
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open():
            moving = {k for k in vals if not k.startswith(("message_", "activity_"))}
            done = self.filtered(lambda ch: ch.state != "draft")
            if done and any(
                ch._fix_guard_differs(n, vals[n], ch[n])
                for ch in done
                for n in moving
                if n in ch._fields
            ):
                raise UserError(
                    "Challan %s is %s and cannot change" % (done[:1].challan_no, done[:1].state)
                )
            verified = (self - done).filtered("verified_by_id")
            if verified and moving & self._VERIFIED_TERMS:
                # the verification covered the terms it was given for
                res = super().write(vals)
                verified._guarded().write(
                    {"verification_ref": False, "verified_by_id": False, "verified_at": False}
                )
                return res
        return super().write(vals)

    @api.depends("tax_kind", "withholding_line_ids.amount", "vat_return_id.net_payable_after_vds")
    def _compute_liability(self):
        for ch in self:
            if ch.tax_kind == "vat":
                # A08 M51-11: the VDS customers deducted is already deposited
                # on the company's behalf; the challan settles what remains.
                ch.liability_total = ch.vat_return_id.net_payable_after_vds
            else:
                ch.liability_total = sum(ch.withholding_line_ids.mapped("amount"))

    def action_record_verification(self, reference=None):
        """Second person: record that the challan number, date and amount were
        verified against the iBAS++ / bank e-payment confirmation."""
        require_finance(self.env, "Verifying a challan")
        for ch in self:
            ref = (reference or ch.receipt_reference or "").strip()
            if not ref:
                raise UserError(
                    "State the iBAS++ / bank confirmation reference the challan matches."
                )
            if ch.state != "draft":
                raise UserError("Challan %s is already %s" % (ch.challan_no, ch.state))
            if not self.env.su and self.env.user == ch.create_uid:
                raise UserError(
                    "Segregation of duties: challan %s was recorded by you; another "
                    "accountant verifies it against the receipt." % ch.challan_no
                )
            ch._guarded().write(
                {
                    "verification_ref": ref,
                    "verified_by_id": self.env.uid,
                    "verified_at": fields.Datetime.now(),
                }
            )
        return True

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
        require_finance(self.env, "Linking deductions to a challan")
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
            ch._fix_refuse_duplicates(open_lines)
            open_lines.write({"challan_id": ch.id})
        return True

    def _fix_refuse_duplicates(self, lines):
        """A challan does not settle both copies of a deduction (M51-8). Which one
        is voided is a person's decision on the Deductions screen."""
        dups = lines.filtered(lambda line: line._fix_duplicates())
        if dups:
            raise UserError(
                "%d deduction(s) in this set are duplicates of another on the same bill (%s). "
                "Void the wrong one, or clear the flag, on the Deductions screen first."
                % (len(dups), ", ".join("#%s %s" % (d.id, d.source_ref) for d in dups[:6]))
            )

    def action_confirm_deposit(self):
        """Confirm the deposit: the challan must settle exactly the linked
        liabilities; posts Dr tax liability / Cr bank and marks the
        deductions deposited. Fails closed on any missing configuration."""
        require_finance(self.env, "Confirming a challan deposit")
        for ch in self:
            if ch.state != "draft":
                raise UserError("Challan %s is already %s" % (ch.challan_no, ch.state))
            if not ch.verified_by_id:
                raise UserError(
                    "Challan %s is not verified against the iBAS++ / bank receipt yet"
                    % ch.challan_no
                )
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
                ch._fix_refuse_duplicates(lines)
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
                partner_lines._guarded().write({"state": "deposited"})
            ch._guarded().write({"state": "deposited", "move_id": move.id})
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
    _inherit = ["fix.guarded.mixin", "mail.thread", "mail.activity.mixin"]
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
    original_credit_id = fields.Many2one(
        "fix.input.vat.credit",
        string="Original Invoice Credit",
        index=True,
        ondelete="restrict",
        help="For a debit / credit note (6.8 / 6.7): the credit of the supplier 6.3 it adjusts",
    )
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

    # Fields whose change makes an eligibility verdict stale.
    _BUSINESS_FIELDS = frozenset(
        {
            "partner_id",
            "supplier_bin",
            "supplier_mushak_no",
            "supplier_enlisted",
            "invoice_date",
            "taxable_amount",
            "vat_amount",
            "adjustment_type",
            "original_credit_id",
            "currency_id",
            "company_id",
            "claim_period",
        }
    )

    def _fix_guarded_fields(self) -> set:
        # A08 M51-3: eligibility is set by action_check_eligibility only.
        return super()._fix_guarded_fields() | {"state", "ineligible_reason", "vat_return_id"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state == "claimed":
            locked |= set(self._BUSINESS_FIELDS)
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("claim_period") and vals.get("invoice_date"):
                vals["claim_period"] = str(vals["invoice_date"])[:7]
        return super().create(vals_list)

    def write(self, vals):
        business = set(vals) & self._BUSINESS_FIELDS
        if self and business and not self._fix_guard_open():
            claimed = self.filtered(lambda r: r.state == "claimed")
            if claimed and any(
                r._fix_guard_differs(n, vals[n], r[n]) for r in claimed for n in business
            ):
                raise UserError(
                    "Input credit %s is claimed in the Mushak 9.1 %s: it is frozen (a "
                    "correction is a 6.7 / 6.8 adjustment)."
                    % (
                        claimed[:1].supplier_mushak_no or claimed[:1].id,
                        claimed[:1].vat_return_id.period,
                    )
                )
            # a verdict on other terms is stale: back to Pending Check
            checked = self.filtered(
                lambda r: (
                    r.state in ("eligible", "ineligible")
                    and any(r._fix_guard_differs(n, vals[n], r[n]) for n in business)
                )
            )
            res = super().write(vals)
            if checked:
                checked._guarded().write({"state": "pending", "ineligible_reason": False})
            return res
        return super().write(vals)

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
        """The reason this credit cannot be claimed, or '' when it can
        (VAT & SD Act 2012 s.46; A08 M51-3)."""
        self.ensure_one()
        if self.adjustment_type == "decrease":
            return ""  # a decreasing adjustment is always reported, never optional
        if self.vat_amount <= 0:
            return "No input VAT on the invoice"
        bin_no = (self.supplier_bin or "").strip()
        if not re.fullmatch(r"\d{13}", bin_no) or len(set(bin_no)) < 2:
            return "Supplier BIN missing or not a real 13-digit BIN"
        if not (self.supplier_mushak_no or "").strip():
            return "Supplier Mushak 6.3 number missing"
        if self.supplier_enlisted:
            return "Supplier is turnover-tax enlisted, not VAT-registered"
        if self.adjustment_type == "increase":
            original = self.original_credit_id
            if not original:
                return "Debit note (6.8) not linked to the supplier 6.3 credit it adjusts"
            if original.state not in ("eligible", "claimed"):
                return "The original invoice credit is not eligible (%s)" % (
                    original.ineligible_reason or original.state
                )
        reason = self._ratio_problem()
        if reason:
            return reason
        if self.adjustment_type == "invoice":
            dup = self._duplicate_of()
            if dup:
                return "Supplier Mushak 6.3 %s (BIN %s) is already recorded on credit %s" % (
                    self.supplier_mushak_no,
                    self.supplier_bin,
                    dup.source_ref or dup.id,
                )
        return ""

    def _ratio_problem(self):
        """The VAT must be the taxable value at a VAT rate in force (Tax Rate
        Master), within the rounding tolerance."""
        self.ensure_one()
        if (self.taxable_amount or 0.0) <= 0.0:
            return "Taxable value missing: the VAT cannot be checked against a scheduled rate"
        rates = self.env["fix.tax.rate"]._fix_vat_rates(self.invoice_date, self.company_id)
        tolerance = float_param(self.env, RATIO_TOLERANCE_PARAM, RATIO_TOLERANCE_DEFAULT)
        for rate in {rates.standard, *rates.reduced}:
            if abs(self.vat_amount - self.taxable_amount * float(rate) / 100.0) <= tolerance:
                return ""
        return "VAT %.2f on taxable %.2f (%.2f%%) matches no VAT rate in force" % (
            self.vat_amount,
            self.taxable_amount,
            self.vat_amount * 100.0 / self.taxable_amount,
        )

    def _duplicate_of(self):
        """Another credit for the same supplier 6.3 (BIN + number) that is
        eligible, claimed, or pending and recorded earlier: a supplier 6.3
        is claimed once."""
        self.ensure_one()
        others = self.sudo().search(
            [
                ("id", "!=", self.id),
                ("company_id", "=", self.company_id.id),
                ("adjustment_type", "=", "invoice"),
                ("supplier_bin", "=", (self.supplier_bin or "").strip()),
                ("supplier_mushak_no", "=", (self.supplier_mushak_no or "").strip()),
            ]
        )
        return others.filtered(
            lambda o: (
                o.state in ("eligible", "claimed") or (o.state == "pending" and o.id < self.id)
            )
        )[:1]

    def action_check_eligibility(self):
        require_finance(self.env, "Checking input VAT eligibility")
        for row in self.sorted("id"):
            if row.state == "claimed":
                raise UserError("A claimed credit is part of a 9.1 return — not re-checked")
            reason = row._ineligibility()
            row._guarded().write(
                {
                    "state": "ineligible" if reason else "eligible",
                    "ineligible_reason": reason or False,
                }
            )
        return True

    @api.model
    def _fix_propose_vat_input_reclass(self, company=None, wip_code="110500", create_draft=False):
        """A08 M51-8 data correction — a PROPOSAL, never posted here.

        AP posted input VAT to 110500 "Work in Progress" (the old default code
        of the vat_input role collided with the chart). This finds the input
        VAT lines the AP sub-ledger posted on that account (label "Input VAT
        ...") and proposes ONE re-class: Dr the configured input-VAT account /
        Cr 110500 for their total. With create_draft=True it creates the entry
        as a DRAFT journal entry for a second person to review and post.
        Refused when cd_tax_engine_bd.vat_input_account_code is not set."""
        company = company or self.env.company
        target = tax_account(self.env, company, "vat_input")
        wip = (
            self.env["account.account"]
            .sudo()
            .search([("code", "=", wip_code), ("company_ids", "in", company.id)], limit=1)
        )
        if not wip:
            raise UserError("No account %s in %s" % (wip_code, company.name))
        if wip == target:
            raise UserError("The configured input-VAT account is %s itself" % wip_code)
        lines = (
            self.env["account.move.line"]
            .sudo()
            .search(
                [
                    ("company_id", "=", company.id),
                    ("account_id", "=", wip.id),
                    ("parent_state", "=", "posted"),
                    ("name", "=like", "Input VAT %"),
                ],
                order="date, id",
            )
        )
        total = money(sum(lines.mapped("balance")))
        debit, credit = (total, 0.0) if total > 0 else (0.0, -total)
        entry = [
            {
                "account": target.code,
                "label": "Re-class AP input VAT from %s" % wip_code,
                "debit": debit,
                "credit": credit,
            },
            {
                "account": wip.code,
                "label": "Re-class AP input VAT to %s" % target.code,
                "debit": credit,
                "credit": debit,
            },
        ]
        result = {
            "company": company.name,
            "source_lines": [
                {
                    "move": ln.move_id.name,
                    "date": str(ln.date),
                    "label": ln.name,
                    "partner": ln.partner_id.display_name or "",
                    "amount": money(ln.balance),
                }
                for ln in lines
            ],
            "total": total,
            "entry": entry,
            "move_id": False,
        }
        if create_draft and total:
            journal = (
                self.env["account.journal"]
                .sudo()
                .search([("company_id", "=", company.id), ("type", "=", "general")], limit=1)
            )
            if not journal:
                raise UserError("No general journal in %s for the re-class" % company.name)
            move = (
                self.env["account.move"]
                .sudo()
                .create(
                    {
                        "move_type": "entry",
                        "company_id": company.id,
                        "journal_id": journal.id,
                        "date": fields.Date.context_today(self),
                        "ref": "A08 M51-8 re-class of AP input VAT from %s" % wip_code,
                        "line_ids": [
                            (
                                0,
                                0,
                                {
                                    "account_id": acc.id,
                                    "name": row["label"],
                                    "debit": row["debit"],
                                    "credit": row["credit"],
                                },
                            )
                            for acc, row in zip((target, wip), entry, strict=True)
                        ],
                    }
                )
            )
            result["move_id"] = move.id
        return result


class FixTaxAuditPack(models.Model):
    """Audit Support Pack: the period's statutory registers exported as CSV,
    with a manifest of SHA-256 checksums, stored as one immutable ZIP
    attachment. action_verify re-checks the stored bundle."""

    _name = "fix.tax.audit.pack"
    _description = "Tax Audit Support Pack"
    _inherit = ["fix.guarded.mixin", "mail.thread", "mail.activity.mixin"]
    _order = "date_to desc, id desc"

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "attachment_id",
            "manifest",
            "pack_sha256",
            "file_count",
            "generated_at",
            "generated_by",
            "integrity_status",
        }

    def write(self, vals):
        if self and not self._fix_guard_open():
            sealed = self.filtered(lambda p: p.state == "generated")
            if sealed and {"date_from", "date_to", "company_id"} & set(vals):
                raise UserError("A generated audit pack is sealed; create a new pack to re-run")
        return super().write(vals)

    seal_id = fields.Many2one(
        "fix.tax.audit.pack.seal", string="Seal", compute="_compute_seal", compute_sudo=True
    )

    def _compute_seal(self):
        Seal = self.env["fix.tax.audit.pack.seal"].sudo()
        for pack in self:
            pack.seal_id = Seal.search([("pack_id", "=", pack.id)], order="id", limit=1)

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
        file's SHA-256 and row count, zipped and attached to the pack. The
        hashes are sealed in an append-only record OUTSIDE the pack (A08
        M51-10), which verification reads."""
        require_finance(self.env, "Generating a tax audit pack")
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
            digest = hashlib.sha256(raw).hexdigest()
            manifest_text = manifest_bytes.decode("utf-8")
            pack._guarded().write(
                {
                    "state": "generated",
                    "attachment_id": attachment.id,
                    "manifest": manifest_text,
                    "pack_sha256": digest,
                    "file_count": len(files),
                    "generated_at": fields.Datetime.now(),
                    "generated_by": self.env.user.id,
                    "integrity_status": "intact",
                }
            )
            self.env["fix.tax.audit.pack.seal"].sudo().create(
                {
                    "pack_id": pack.id,
                    "company_id": pack.company_id.id,
                    "pack_sha256": digest,
                    "manifest": manifest_text,
                    "attachment_id": attachment.id,
                    "sealed_by": self.env.uid,
                }
            )
        return True

    def action_verify(self):
        """Re-read the stored bundle and check it against the SEAL — the hash
        and manifest recorded outside the pack at generation (a re-hashed pack
        record or a replaced bundle reads tampered)."""
        require_finance(self.env, "Verifying a tax audit pack")
        for pack in self:
            seal = pack.sudo().seal_id
            if pack.state != "generated" or not seal:
                raise UserError("Generate the pack first")
            attachment = seal.attachment_id.sudo()
            raw = base64.b64decode(attachment.datas or b"") if attachment else b""
            ok = (
                bool(raw)
                and hashlib.sha256(raw).hexdigest() == seal.pack_sha256
                and pack.pack_sha256 == seal.pack_sha256
                and pack.attachment_id == seal.attachment_id
            )
            if ok:
                try:
                    manifest = json.loads(seal.manifest or "{}")
                    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
                        for entry in manifest.get("files", []):
                            data = zf.read(entry["name"])
                            if hashlib.sha256(data).hexdigest() != entry["sha256"]:
                                ok = False
                                break
                except (zipfile.BadZipFile, KeyError, ValueError):
                    ok = False
            pack._guarded().write({"integrity_status": "intact" if ok else "tampered"})
        return True


class FixTaxAuditPackSeal(models.Model):
    """The append-only seal of a generated audit pack (A08 M51-10): the
    bundle hash and manifest live HERE, outside the pack an accountant can
    edit. Created by the system at generation; never written or deleted."""

    _name = "fix.tax.audit.pack.seal"
    _description = "Tax Audit Pack Seal"
    _order = "id desc"

    pack_id = fields.Many2one("fix.tax.audit.pack", required=True, index=True, ondelete="restrict")
    company_id = fields.Many2one("res.company", required=True, index=True)
    pack_sha256 = fields.Char(string="Bundle SHA-256", required=True)
    manifest = fields.Text(required=True)
    attachment_id = fields.Many2one("ir.attachment", string="Bundle", ondelete="restrict")
    sealed_by = fields.Many2one("res.users", required=True)
    sealed_at = fields.Datetime(required=True, default=fields.Datetime.now)

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            raise UserError("An audit pack seal is written by the pack generation only.")
        return super().create(vals_list)

    def write(self, vals):
        raise UserError("An audit pack seal is append-only.")

    def unlink(self):
        raise UserError("An audit pack seal is append-only.")
