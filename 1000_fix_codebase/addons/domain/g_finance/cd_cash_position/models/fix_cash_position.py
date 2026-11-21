# cd_cash_position — M50 Treasury, cash & banking core (P06-M04, CD-M50-01;
# A08 rebuild 2026-10-26; A08 workflow-audit remediation 2026-11-04).
#
# T06: treasury EXECUTES payment requests raised by M52 / M20 / M53 —
# through `_fix_request_payment` (a pinned draft execution) or the
# payment.requested event (registered consumer) — and publishes the bank's
# confirmation. Nothing in finance calls treasury synchronously.
#
# A08 workflow audit (M50-1 … M50-5, M50-14, M50-15, M50-18):
#   * two-person release (F1): an accountant PREPARES the instruction; an
#     Accounting Administrator who did not create, prepare or approve its
#     source RELEASES it. Above the single-releaser ceiling the amount is
#     routed through the M63 engine (fix.dofa.mixin) to a DOFA tier holder
#     who is also an Accounting Administrator, and the releaser must be a
#     different person from that approver (dual treasury authorisation,
#     BRU-TRE-12 / FR-TRE-033);
#   * the payee, bank account, amount, journal and rail are pinned (F2): a
#     change after preparation voids the preparation and the approval; after
#     release it is refused (the bank file is cut). The GL posts the amount
#     the bank file carried;
#   * a payment is bank-confirmed only by an IMPORTED bank statement DEBIT of
#     the released amount (never a typed reference, never a credit);
#   * every state / stamp / evidence field is guarded (fix.guarded.mixin);
#   * `source_posts_gl` is computed from the source model, never typed;
#   * manual instructions take a sequence key (no timestamp collisions) and a
#     duplicate instruction is refused unless a reason is recorded.
from __future__ import annotations

import base64
import csv
import hashlib
import io
import logging
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

from .treasury_common import (
    GROUP_ACCOUNTANT,
    GROUP_ADMIN,
    bank_account_of,
    float_param,
    gl_balance,
    has_token,
    post_treasury_move,
    require_role,
    treasury_account,
)

# Requesting documents that book their own payment entry when the execution
# is confirmed (treasury then posts nothing). A source model may also declare
# `_fix_posts_own_payment = True` on its class.
SELF_POSTING_SOURCES = {"fix.payment.run.line", "fix.employee.advance"}
LEGACY_PREFIX = {
    "fix.ar.invoice": "AR",
    "fix.expense.claim": "EXP",
    "fix.vendor.invoice": "AP",
}
MATCH_WINDOW_DAYS = 10
_logger = logging.getLogger(__name__)

# Configuration (ir.config_parameter). The M50 spec gives no value for the
# dual-authorisation threshold (BRU-TRE-12 "the configured value"), so the
# single-releaser ceiling defaults to 0: every release is routed for DOFA
# approval. The tier bands are the 05-04 §7 cash-commitment bands (<=50k,
# <=500k, <=2M, above), the same defaults the A06 procurement ladder uses; a
# ruled fix.dofa.ladder for fix.payment.execution overrides them.
PARAM_SINGLE_CEILING = "cd_cash_position.release_single_ceiling"
PARAM_TIER2 = "cd_cash_position.release_tier2_max"
PARAM_TIER3 = "cd_cash_position.release_tier3_max"
PARAM_TIER4 = "cd_cash_position.release_tier4_max"
DEFAULT_RELEASE_LADDER = {
    PARAM_SINGLE_CEILING: 0.0,
    PARAM_TIER2: 50000.0,
    PARAM_TIER3: 500000.0,
    PARAM_TIER4: 2000000.0,
}
# Duplicate-instruction window (M50-14): same payee account + amount +
# currency raised within this many days is a duplicate unless a reason is
# recorded. Default = the statement match window.
PARAM_DUP_DAYS = "cd_cash_position.duplicate_window_days"
# Bank charge write-off (M50-6): a debit above this is booked only by an
# Accounting Administrator who did not import the statement. Default 0: every
# charge has a second person.
PARAM_CHARGE_CEILING = "cd_cash_position.bank_charge_single_max"

# What a payment instruction is: frozen from preparation on.
INSTRUCTION_FIELDS = (
    "amount",
    "currency_id",
    "partner_id",
    "partner_bank_id",
    "payee",
    "journal_id",
    "method",
    "rail",
    "debit_account_id",
    "value_date",
    "company_id",
    # A05 I3: the GL dimensions the confirmation posts with, and the card
    # transaction a card refund reverses
    "operating_unit_id",
    "branch_id",
    "original_payment_ref",
)
# What a source document fixed (pinned at creation by _fix_request_payment).
SOURCE_PINNED_FIELDS = (
    "amount",
    "currency_id",
    "partner_id",
    "payee",
    "source_ref",
    # A05 I3 (FIN-10): the source's unit and branch are the transaction's
    "operating_unit_id",
    "branch_id",
    "original_payment_ref",
    # A05 S6: the liability the confirmation clears is the source's (the
    # seller payable, the deposits held, the recycler fee accrual) - treasury
    # never re-points it to another account
    "debit_account_id",
)
OPEN_STATES = ("pending", "prepared", "sent", "executed")

# A05 FIN-12 / FIN-25 (I3): the journal an instruction is paid from matches
# its method — cash from a cash journal, a bank transfer or cheque from an
# operating bank account, an MFS payment from the MFS wallet, a card refund
# through the card acquirer (gateway) account.
METHOD_JOURNAL_ROLES = {
    "mobile_fs": ("mfs_wallet",),
    "card": ("gateway",),
}
# bank roles a bank transfer / cheque is never paid from
NON_OPERATING_ROLES = ("mfs_wallet", "gateway", "deposit")
# A05 FIN-12: the groups that may pay out a released cash voucher
GROUP_CASHIER = "cd_front_desk.group_fd_cashier"


def is_imported(line) -> bool:
    """Bank evidence is a line of an imported statement file."""
    return bool(line and line.statement_file_hash)


class FixApprovalMatrixTreasury(models.Model):
    _inherit = "fix.approval.matrix"

    decision_domain = fields.Selection(
        selection_add=[("payment_release", "Treasury Payment Release")],
        ondelete={"payment_release": "cascade"},
    )


class FixPaymentExecution(models.Model):
    """The execution side of the payment-request seam.

    pending (draft) -> prepared (accountant; DOFA routed above the ceiling)
    -> sent (released by a second person; bank file cut) -> executed
    (imported statement debit; GL posted) | failed (bank rejection / bounce)
    | cancelled."""

    _name = "fix.payment.execution"
    _description = "Payment Execution"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.dofa.mixin"]
    _order = "id desc"
    _approval_domain = "payment_release"
    _approval_routed = True
    _request_key_unique = models.Constraint(
        "UNIQUE (source_model, source_id)",
        "A payment request is executed exactly once — DI-04 idempotency",
    )

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    branch_id = fields.Many2one(
        "fix.branch",
        string="Branch",
        index=True,
        help="The source document's branch: the confirmation posts with it (and with this "
        "instruction's operating unit, the branch's own).",
    )
    name = fields.Char(string="Instruction Ref", readonly=True, copy=False, index=True)
    source_model = fields.Char(string="Source Model", required=True, index=True)
    source_id = fields.Integer(string="Source ID", required=True, index=True)
    source_ref = fields.Char(string="Source Reference", readonly=True, copy=False)
    source_pinned = fields.Boolean(
        string="Pinned to Source",
        readonly=True,
        copy=False,
        help="Raised by a source document: payee, amount and currency are the source's.",
    )
    source_approved_by_id = fields.Many2one(
        "res.users",
        string="Source Approved By",
        readonly=True,
        copy=False,
        help="Who approved the requesting document. They never authorise or release it.",
    )
    payee = fields.Char(string="Payee", required=True)
    partner_id = fields.Many2one("res.partner", string="Payee Partner", index=True)
    partner_bank_id = fields.Many2one(
        "res.partner.bank",
        string="Payee Account / Wallet",
        help="The payee's bank account (BEFTN/RTGS/NPSB) or MFS wallet",
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount = fields.Monetary(string="Amount", currency_field="currency_id", required=True)
    method = fields.Selection(
        [
            ("bank_transfer", "Bank Transfer"),
            ("cheque", "Cheque"),
            ("cash", "Cash"),
            ("mobile_fs", "bKash/Nagad Merchant Pay"),
            # A05 FIN-25: a card deposit is refunded to the card it came from
            ("card", "Card Refund (to the original card)"),
        ],
        default="bank_transfer",
        required=True,
    )
    original_payment_ref = fields.Char(
        string="Original Card Transaction",
        help="Card refunds: the acquirer reference (RRN / approval code) of the card payment "
        "this refund reverses. The refund goes back to that card, never to a bank account.",
    )
    rail = fields.Selection(
        [("beftn", "BEFTN"), ("rtgs", "RTGS"), ("npsb", "NPSB"), ("cheque", "Cheque")],
        string="Rail",
        help="Clearing rail (bank transfers: BEFTN / RTGS / NPSB)",
    )
    source_posts_gl = fields.Boolean(
        string="Source Posts GL",
        compute="_compute_source_posts_gl",
        store=True,
        readonly=True,
        help="The requesting document books its own payment entry when this execution is "
        "confirmed (AP payment runs, employee advances) — treasury then posts nothing, so the "
        "bank is never credited twice. Derived from the source model; never set by hand.",
    )
    journal_id = fields.Many2one(
        "account.journal",
        string="Paid From",
        domain="[('type', 'in', ('bank', 'cash')), ('company_id', '=', company_id)]",
        help="The company bank/cash account the money leaves from",
    )
    debit_account_id = fields.Many2one(
        "account.account",
        string="Debit Account",
        help="Liability cleared by this payment (e.g. AP control). Empty: the configured "
        "outgoing-payments clearing account.",
    )
    value_date = fields.Date(string="Value Date", default=fields.Date.context_today)
    state = fields.Selection(
        [
            ("pending", "Draft"),
            ("prepared", "Prepared — Awaiting Release"),
            ("sent", "Sent — Awaiting Bank Confirmation"),
            ("executed", "Executed"),
            ("failed", "Failed"),
            ("cancelled", "Cancelled"),
        ],
        default="pending",
        required=True,
        tracking=True,
    )
    prepared_by_id = fields.Many2one("res.users", string="Prepared By", readonly=True, copy=False)
    prepared_at = fields.Datetime(readonly=True, copy=False)
    sent_at = fields.Datetime(readonly=True, copy=False)
    sent_by_id = fields.Many2one("res.users", string="Released By", readonly=True, copy=False)
    executed_at = fields.Datetime(readonly=True, copy=False)
    # the instruction as the bank file carried it (F2)
    released_amount = fields.Monetary(
        string="Released Amount", currency_field="currency_id", readonly=True, copy=False
    )
    released_partner_bank_id = fields.Many2one(
        "res.partner.bank", string="Released To Account", readonly=True, copy=False
    )
    released_acc_number = fields.Char(string="Released Account No", readonly=True, copy=False)
    released_journal_id = fields.Many2one(
        "account.journal", string="Released From", readonly=True, copy=False
    )
    bank_reference = fields.Char(
        string="Bank Reference",
        tracking=True,
        copy=False,
        help="The bank's / wallet's trx id; used to find the imported statement debit",
    )
    statement_line_id = fields.Many2one(
        "fix.bank.statement.line", string="Bank Statement Line", readonly=True, copy=False
    )
    confirmation_source = fields.Selection(
        [
            ("statement", "Bank Statement Match"),
            ("payroll_return", "Imported Payroll Bank-Return File"),
            ("bank_reference", "Bank Reference Recorded (legacy)"),
            ("caller_asserted", "Caller-Asserted (No Bank Evidence)"),
            # A05 FIN-12: cash paid out across the counter on a cash voucher
            ("cash_voucher", "Cash Voucher Paid Out"),
        ],
        readonly=True,
        copy=False,
    )
    # A05 FIN-12: the cash voucher of a cash-method instruction
    cash_voucher_no = fields.Char(string="Cash Voucher No", readonly=True, copy=False, index=True)
    cash_paid_by_id = fields.Many2one(
        "res.users", string="Cash Paid Out By", readonly=True, copy=False
    )
    cash_paid_at = fields.Datetime(string="Cash Paid Out At", readonly=True, copy=False)
    cash_received_by = fields.Char(
        string="Cash Received By",
        readonly=True,
        copy=False,
        help="Who signed the cash voucher for the money (name / ID as on the voucher).",
    )
    bank_confirmed = fields.Boolean(
        compute="_compute_bank_confirmed", store=True, string="Bank Confirmed"
    )
    failure_reason = fields.Char(string="Failure Reason", tracking=True, copy=False)
    duplicate_reason = fields.Char(
        string="Not a Duplicate Because",
        copy=False,
        help="Required to prepare an instruction that repeats another open instruction "
        "(same payee account, amount and currency within the duplicate window).",
    )
    instruction_attachment_id = fields.Many2one(
        "ir.attachment", string="Instruction File", readonly=True, copy=False
    )
    move_id = fields.Many2one("account.move", string="GL Entry", readonly=True, copy=False)
    reversal_move_id = fields.Many2one(
        "account.move", string="Reversal Entry", readonly=True, copy=False
    )
    gl_note = fields.Char(string="GL Note", readonly=True, copy=False)

    # ------------------------------------------------------------ guards
    _TREASURY_GUARDED = frozenset(
        {
            "state",
            "prepared_by_id",
            "prepared_at",
            "sent_at",
            "sent_by_id",
            "executed_at",
            "released_amount",
            "released_partner_bank_id",
            "released_acc_number",
            "released_journal_id",
            "statement_line_id",
            "confirmation_source",
            "instruction_attachment_id",
            "move_id",
            "reversal_move_id",
            "gl_note",
            "source_posts_gl",
            "source_pinned",
            "source_approved_by_id",
            "source_ref",
            "name",
            "cash_voucher_no",
            "cash_paid_by_id",
            "cash_paid_at",
            "cash_received_by",
        }
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | self._TREASURY_GUARDED

    def unlink(self):
        # T-14 immutable audit: once an instruction has been prepared, sent,
        # executed or failed, it carries the approvals, the releaser and the
        # bank's confirmation — evidence never erased. Cancel instead.
        if not (self.env.su or self._fix_guard_has_token()):
            locked = self.filtered(lambda p: p.state != "pending")
            if locked:
                raise UserError(
                    "Payment instructions that left draft are evidence and are never "
                    "deleted (%s). Cancel the instruction through the workflow instead."
                    % ", ".join(locked.mapped("name")[:3])
                )
        return super().unlink()

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(p.state not in ("pending",) for p in self):
            locked |= set(INSTRUCTION_FIELDS)
        if self and any(p.source_pinned for p in self):
            locked |= set(SOURCE_PINNED_FIELDS)
        return locked

    # ------------------------------------------------------------ computes
    @api.depends("source_model")
    def _compute_source_posts_gl(self):
        for pay in self:
            model = pay.source_model or ""
            declared = model in self.env and getattr(
                type(self.env[model]), "_fix_posts_own_payment", False
            )
            pay.source_posts_gl = model in SELF_POSTING_SOURCES or bool(declared)

    @api.depends(
        "state",
        "confirmation_source",
        "statement_line_id",
        "statement_line_id.amount",
        "statement_line_id.statement_file_hash",
    )
    def _compute_bank_confirmed(self):
        for pay in self:
            line = pay.statement_line_id
            pay.bank_confirmed = bool(
                pay.state == "executed"
                and (
                    # an imported statement debit, or the imported payroll
                    # bank-return file (F1's payroll evidence source)
                    (is_imported(line) and line.amount < 0)
                    or pay.confirmation_source == "payroll_return"
                    # A05 FIN-12: cash never reaches a bank statement; the
                    # cashier's voucher is its evidence
                    or pay.confirmation_source == "cash_voucher"
                )
            )

    @api.constrains("branch_id", "operating_unit_id")
    def _check_branch_unit(self):
        """A05 I3: the branch posts in its own unit (M19's journal dimension
        refuses anything else, at confirmation — too late)."""
        for pay in self:
            if (
                pay.branch_id
                and pay.branch_id.operating_unit_id
                and pay.branch_id.operating_unit_id != pay.operating_unit_id
            ):
                raise ValidationError(
                    "%s: branch %s belongs to %s, not to %s."
                    % (
                        pay.name or "This instruction",
                        pay.branch_id.name,
                        pay.branch_id.operating_unit_id.name,
                        pay.operating_unit_id.name,
                    )
                )

    @api.constrains("amount")
    def _check_amount(self):
        for pay in self:
            if pay.amount < 0:
                raise ValidationError("A payment amount cannot be negative.")

    @api.constrains("partner_id", "partner_bank_id")
    def _check_bank_owner(self):
        """The money goes only to the payee's own account or wallet."""
        for pay in self:
            bank_owner = pay.partner_bank_id.partner_id.commercial_partner_id
            if bank_owner and pay.partner_id and bank_owner != pay.partner_id.commercial_partner_id:
                raise ValidationError(
                    "%s pays %s: the account or wallet %s belongs to %s."
                    % (
                        pay.name or "This instruction",
                        pay.partner_id.display_name,
                        pay.partner_bank_id.acc_number,
                        bank_owner.display_name,
                    )
                )

    # ------------------------------------------------------------ DOFA
    def _dofa_thresholds(self):
        env = self.env
        ceiling = float_param(
            env, PARAM_SINGLE_CEILING, DEFAULT_RELEASE_LADDER[PARAM_SINGLE_CEILING]
        )
        bands = [(max(ceiling, 0.0), "tier_0")]
        for key, tier in (
            (PARAM_TIER2, "tier_2"),
            (PARAM_TIER3, "tier_3"),
            (PARAM_TIER4, "tier_4"),
        ):
            bound = float_param(env, key, DEFAULT_RELEASE_LADDER[key])
            if bound > bands[-1][0]:
                bands.append((bound, tier))
        bands.append((float("inf"), "tier_5"))
        return bands

    def _dofa_amount(self) -> float:
        self.ensure_one()
        amount = self.amount or 0.0
        company = self.company_id or self.env.company
        if self.currency_id and company.currency_id and self.currency_id != company.currency_id:
            amount = self.currency_id._convert(
                amount, company.currency_id, company, self.value_date or fields.Date.today()
            )
        return amount

    @api.depends("amount", "currency_id")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    def _approval_pinned_fields(self) -> set:
        return super()._approval_pinned_fields() | {
            "partner_bank_id",
            "payee",
            "journal_id",
            "method",
            "rail",
        }

    def _fix_conflicted_users(self):
        """Who never authorises or releases this instruction."""
        self.ensure_one()
        rec = self.sudo()
        return (
            rec.create_uid
            | rec.prepared_by_id
            | rec.source_approved_by_id
            | rec.approval_amount_changed_by_id
        ).sudo()

    def _approval_excluded(self):
        return (super()._approval_excluded() | self._fix_conflicted_users()).sudo()

    def _approval_holders(self, group):
        """Treasury authorisers: the DOFA tier holders who are also
        Accounting Administrators."""
        users = super()._approval_holders(group)
        return users.filtered(lambda u: u.has_group(GROUP_ADMIN))

    def action_dofa_approve(self):
        """The M63 apply method: only from the approver's inbox task, by an
        Accounting Administrator holding the tier, outside the conflicted set."""
        self._approval_assert_routed()
        for rec in self:
            if rec.state != "prepared":
                raise UserError("%s is not prepared for release." % rec.name)
            if not self.env.su:
                deciders = self.env.user | rec._approval_task().on_behalf_of_id
                if not all(u.has_group(GROUP_ADMIN) for u in deciders):
                    raise UserError(
                        "Authorising a payment needs the Accounting Administrator role."
                    )
                clash = deciders & rec._fix_conflicted_users()
                if clash:
                    raise UserError(
                        "Segregation of duties: %s created, prepared or approved the source of "
                        "%s and cannot authorise it." % (", ".join(clash.mapped("name")), rec.name)
                    )
        return super().action_dofa_approve()

    def _approval_on_rejected(self, comment):
        for rec in self.sudo():
            if rec.state == "prepared":
                rec._fix_unprepare("authorisation rejected: %s" % (comment or "no reason"))
        return super()._approval_on_rejected(comment)

    # ------------------------------------------------------------ create / write
    def _fix_manual_key(self) -> int:
        raw = self.env["ir.sequence"].sudo().next_by_code("fix.payment.execution.manual")
        try:
            return int(raw)
        except (TypeError, ValueError) as exc:
            raise UserError(
                "The manual payment instruction key sequence (fix.payment.execution.manual) "
                "is missing."
            ) from exc

    @api.model_create_multi
    def create(self, vals_list):
        trusted = self.env.su or self._fix_guard_has_token()
        if not trusted:
            # The guard's own create check, on what the USER sent (before the
            # system adds the sequence name and the manual key below).
            guarded = self._fix_guarded_fields()
            empty = self.browse()
            for vals in vals_list:
                keys = guarded & set(vals)
                if not keys:
                    continue
                defaults = self.default_get(list(keys))
                changed = [
                    n
                    for n in keys
                    if empty._fix_guard_differs(
                        n,
                        vals[n],
                        empty._fields[n].convert_to_record(
                            empty._fields[n].convert_to_cache(defaults.get(n), empty), empty
                        ),
                    )
                ]
                if changed:
                    self._fix_guard_refuse(changed)
        for vals in vals_list:
            # computed from the source model; a caller's value is ignored
            vals.pop("source_posts_gl", None)
            if not trusted:
                if vals.get("source_model") not in (None, False, "", "manual"):
                    raise UserError(
                        "A payment instruction for %s is raised by its source document "
                        "(_fix_request_payment), not typed in treasury." % vals["source_model"]
                    )
                vals.pop("name", None)
                vals["source_model"] = "manual"
                vals["source_id"] = self._fix_manual_key()
            elif not vals.get("source_model") or (
                vals.get("source_model") == "manual" and not vals.get("source_id")
            ):
                vals["source_model"] = "manual"
                vals["source_id"] = self._fix_manual_key()
            if not vals.get("name"):
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.payment.execution") or "PEX"
                )
            company = (
                self.env["res.company"].browse(vals.get("company_id"))
                if vals.get("company_id")
                else self.env.company
            )
            if not vals.get("operating_unit_id") and vals.get("branch_id"):
                # A05 I3: a branch posts in its own unit
                vals["operating_unit_id"] = (
                    self.env["fix.branch"].sudo().browse(vals["branch_id"]).operating_unit_id.id
                )
            if not vals.get("operating_unit_id"):
                # the form's OU picker can arrive empty; treasury executes
                # company-wide — fall back to the company's first OU
                vals["operating_unit_id"] = (
                    self.env["operating.unit"]
                    .sudo()
                    .search([("company_id", "=", company.id)], limit=1)
                    .id
                )
        if trusted:
            return super().create(vals_list)
        # user-sent guarded values were refused above; the name and manual
        # key are the system's own
        return super(FixPaymentExecution, self._guarded()).create(vals_list).with_env(self.env)

    def write(self, vals):
        if self and not self._fix_guard_has_token():
            if not self.env.su and {"source_model", "source_id"} & set(vals):
                for pay in self:
                    if vals.get("source_model", pay.source_model) != pay.source_model or int(
                        vals.get("source_id", pay.source_id) or 0
                    ) != (pay.source_id or 0):
                        raise UserError(
                            "The source of %s is fixed: it is the document that asked for "
                            "the payment." % pay.name
                        )
            touched = set(INSTRUCTION_FIELDS) & set(vals)
            unprepare = self.browse()
            for pay in self:
                changed = [f for f in touched if pay._fix_guard_differs(f, vals[f], pay[f])]
                if not changed:
                    continue
                # F1 freeze: a SENT instruction is what the bank was told.
                # Escapes: the superuser relay consumer, the payroll
                # treasury consumer's in-process token (it completes the
                # instruction from the imported bank file), and the FIRST
                # naming of the paying wallet on a payroll MFS execution
                # that left with none configured — treasury records which
                # wallet the provider paid from, before Confirm Bank.
                first_wallet = (
                    changed == ["journal_id"]
                    and pay.payroll_released
                    and not pay.journal_id
                    and self.env.user.has_group(GROUP_ACCOUNTANT)
                )
                if (
                    pay.state not in ("pending", "prepared")
                    and not self.env.su
                    and not first_wallet
                    and not self.env.context.get("fix_payroll_treasury")
                ):
                    raise UserError(
                        "%s is %s: its payee, account, amount and rail are what the bank was "
                        "instructed to pay and cannot change (%s). Cancel it and raise a new "
                        "instruction."
                        % (
                            pay.name,
                            dict(self._fields["state"].selection)[pay.state],
                            ", ".join(changed),
                        )
                    )
                if pay.source_pinned and not self.env.su:
                    pinned = set(changed) & set(SOURCE_PINNED_FIELDS)
                    if "partner_bank_id" in changed and pay.partner_bank_id:
                        pinned.add("partner_bank_id")
                    if pinned:
                        raise UserError(
                            "%s pays what %s approved: %s cannot change in treasury."
                            % (pay.name, pay.source_model, ", ".join(sorted(pinned)))
                        )
                if pay.state == "prepared":
                    unprepare |= pay
            result = super().write(vals)
            for pay in unprepare:
                pay._fix_unprepare(
                    "the instruction changed after preparation (%s)" % ", ".join(sorted(touched))
                )
            return result
        return super().write(vals)

    def _fix_unprepare(self, reason):
        """Withdraw preparation and authorisation: the terms they covered moved."""
        for pay in self:
            if pay.approval_state in ("pending", "approved") or pay.dofa_approved:
                pay._approval_void(reason)
                if pay.dofa_approved:
                    pay._dofa_void_approval(reason)
            pay._guarded().write(
                {"state": "pending", "prepared_by_id": False, "prepared_at": False}
            )
            pay.message_post(body="Preparation withdrawn: %s." % reason)

    # ------------------------------------------------------------ requests
    @api.model
    def _fix_request_payment(
        self,
        source_model,
        source_id,
        payee_partner,
        bank_account,
        amount,
        currency,
        ref,
        approved_by,
        **options,
    ):
        """THE way another module asks treasury to pay (B2 payment runs, B4
        payout runs, the payment.requested consumer). Creates a DRAFT
        execution pinned to this payee, bank account, amount and currency;
        idempotent on (source_model, source_id) — a replay with other terms
        is refused. Treasury prepares, authorises and releases it.

        options: method, rail, journal_id, value_date, debit_account_id,
        company_id, operating_unit_id, payee (label)."""
        if not source_model or source_model == "manual" or not source_id:
            raise UserError("A payment request names its source document.")
        Partner = self.env["res.partner"].sudo()
        partner = (
            Partner.browse(int(payee_partner))
            if isinstance(payee_partner, int)
            else (payee_partner.sudo() if payee_partner else Partner)
        )
        Bank = self.env["res.partner.bank"].sudo()
        bank = (
            Bank.browse(int(bank_account))
            if isinstance(bank_account, int)
            else (bank_account.sudo() if bank_account else Bank)
        )
        Currency = self.env["res.currency"].sudo()
        if isinstance(currency, str):
            cur = Currency.search([("name", "=", currency)], limit=1)
        elif isinstance(currency, int):
            cur = Currency.browse(currency)
        else:
            cur = currency.sudo() if currency else Currency
        cur = cur or self.env.ref("base.BDT")
        Users = self.env["res.users"].sudo()
        approver = (
            Users.browse(int(approved_by))
            if isinstance(approved_by, int)
            else (approved_by.sudo() if approved_by else Users)
        )
        amount = round(float(amount or 0.0), 2)
        if amount <= 0:
            raise UserError(
                "A payment request carries a positive amount (%s/%s)." % (source_model, source_id)
            )
        if not partner and not options.get("payee"):
            raise UserError(
                "A payment request names its payee (%s/%s)." % (source_model, source_id)
            )
        source = None
        if source_model in self.env:
            source = self.env[source_model].sudo().browse(int(source_id)).exists()
            if not source:
                raise UserError("%s %s does not exist: nothing to pay." % (source_model, source_id))
        Exec = self.sudo()
        existing = Exec.search(
            [("source_model", "=", source_model), ("source_id", "=", int(source_id))], limit=1
        )
        if existing:
            if (
                abs(existing.amount - amount) > 0.005
                or (partner and existing.partner_id != partner)
                or (bank and existing.partner_bank_id and existing.partner_bank_id != bank)
                or existing.currency_id != cur
            ):
                raise UserError(
                    "%s/%s was already requested as %s on different terms; a replay pays "
                    "once, on the terms first approved." % (source_model, source_id, existing.name)
                )
            return self.browse(existing.id)
        company = (
            self.env["res.company"].browse(options.get("company_id"))
            if options.get("company_id")
            else (
                source.company_id
                if source is not None and "company_id" in source._fields and source.company_id
                else self.env.company
            )
        )
        ou_id, branch, dims_note = self._fix_request_dimensions(
            source_model, source_id, source, company, options
        )
        if not ou_id:
            raise UserError("%s/%s carries no operating unit." % (source_model, source_id))
        method = options.get("method") or "bank_transfer"
        if method == "card" and not (options.get("original_payment_ref") or "").strip():
            raise UserError(
                "%s/%s: a card refund names the card payment it reverses "
                "(original_payment_ref) — it goes back to that card, not to a bank account."
                % (source_model, source_id)
            )
        vals = {
            "company_id": company.id,
            "operating_unit_id": ou_id,
            "source_model": source_model,
            "source_id": int(source_id),
            "source_ref": ref or "%s/%s" % (source_model, source_id),
            "source_pinned": True,
            "source_approved_by_id": approver.id or False,
            "payee": options.get("payee") or partner.display_name,
            "partner_id": partner.id or False,
            "partner_bank_id": bank.id or False,
            "currency_id": cur.id,
            "amount": amount,
            "method": method,
            "branch_id": branch.id or False,
        }
        for key in ("rail", "journal_id", "value_date", "debit_account_id", "original_payment_ref"):
            if options.get(key):
                vals[key] = options[key]
        # A05 FIN-12 / FIN-25: the journal matches the method. A caller's
        # journal of the wrong kind (the first bank journal for a cash refund)
        # is replaced by the one journal of the right kind, else left empty
        # for treasury to choose — never guessed among several.
        journal_note = False
        given = self.env["account.journal"].sudo().browse(vals.get("journal_id") or [])
        if not self._fix_journal_fits(given, method):
            matching = self._fix_matching_journal(
                company, method, self.env["operating.unit"].browse(ou_id)
            )
            vals["journal_id"] = matching.id or False
            if given:
                journal_note = "%s is not a %s journal: %s" % (
                    given.display_name,
                    dict(self._fields["method"].selection)[method],
                    "pre-filled %s instead" % matching.display_name
                    if matching
                    else "treasury chooses the paying journal",
                )
        pay = Exec._guarded().create(vals)
        pay.message_post(
            body="Requested by %s (%s)%s. Treasury prepares, authorises and releases it; "
            "nothing is paid before %s confirms it."
            % (
                ref or source_model,
                source_model,
                " — approved by %s" % approver.name if approver else "",
                "the cashier's voucher" if method == "cash" else "an imported bank statement",
            )
        )
        for note in (dims_note, journal_note):
            if note:
                pay.message_post(body=note)
        return self.browse(pay.id)

    @api.model
    def _fix_request_dimensions(self, source_model, source_id, source, company, options):
        """A05 FIN-10 / I3: (operating unit id, branch, note) of a requested
        payment. The branch is the caller's (option branch_id) or the source
        document's own branch_id; the unit is the caller's, else the source's,
        else the branch's — the company's first unit only when none of them
        knows one. A branch named by the caller that sits in another unit is
        refused; a source branch that does so is not carried (the caller's
        unit wins, as before) and the instruction says why."""
        Branch = self.env["fix.branch"].sudo()
        raw_branch = options.get("branch_id")
        if not raw_branch:
            explicit = Branch
        elif isinstance(raw_branch, int):
            explicit = Branch.browse(raw_branch).exists()
        else:
            explicit = raw_branch.sudo()
        inferred = Branch
        if (
            not explicit
            and source is not None
            and "branch_id" in source._fields
            and source.branch_id
            and source.branch_id._name == "fix.branch"
        ):
            inferred = source.branch_id.sudo()
        branch = explicit or inferred
        ou_option = options.get("operating_unit_id")
        if ou_option and not isinstance(ou_option, int):
            ou_option = ou_option.id
        ou_id = ou_option or (
            source.operating_unit_id.id
            if source is not None and "operating_unit_id" in source._fields
            else False
        )
        note = False
        branch_ou = branch.operating_unit_id if branch else self.env["operating.unit"]
        if branch and branch.company_id and branch.company_id != company:
            raise UserError(
                "%s/%s: branch %s belongs to another company."
                % (source_model, source_id, branch.name)
            )
        if not ou_id:
            ou_id = branch_ou.id
        elif branch_ou and branch_ou.id != ou_id:
            if explicit:
                raise UserError(
                    "%s/%s: branch %s belongs to %s, not to the operating unit the payment "
                    "names. A posting carries the branch's own unit."
                    % (source_model, source_id, branch.name, branch_ou.name)
                )
            note = (
                "Source branch %s (unit %s) is not in this instruction's unit: the confirmation "
                "posts on the unit only." % (branch.name, branch_ou.name)
            )
            branch = Branch
        if not ou_id:
            ou_id = (
                self.env["operating.unit"]
                .sudo()
                .search([("company_id", "=", company.id)], limit=1)
                .id
            )
        return ou_id, branch, note

    @api.model
    def _fix_journal_fits(self, journal, method) -> bool:
        """Is `journal` the kind `method` is paid from?"""
        if not journal:
            return False
        if method == "cash":
            # a cash journal that pays money out — not the cheque-in-hand
            # staging journal (fix_real: CIH, the only 'cash' journal)
            return journal.type == "cash" and not self._fix_is_cheque_in_hand(journal)
        if journal.type != "bank":
            return False
        role = journal.fix_treasury_role or journal.fix_account_type or False
        if method in METHOD_JOURNAL_ROLES:
            return role in METHOD_JOURNAL_ROLES[method]
        return role not in NON_OPERATING_ROLES

    @api.model
    def _fix_is_cheque_in_hand(self, journal) -> bool:
        cih = treasury_account(
            self.env, journal.company_id or self.env.company, "cheque_in_hand", required=False
        )
        return bool(cih and journal.sudo().default_account_id == cih)

    @api.model
    def _fix_matching_journal(self, company, method, operating_unit=None):
        """The ONE journal of the company that `method` is paid from (in the
        payment's unit when journals carry one), else none: treasury picks
        among several, the system never guesses."""
        journals = (
            self.env["account.journal"]
            .sudo()
            .search(
                [
                    ("company_id", "=", company.id),
                    ("type", "=", "cash" if method == "cash" else "bank"),
                ]
            )
            .filtered(lambda j: self._fix_journal_fits(j, method))
        )
        if len(journals) > 1 and operating_unit and "operating_unit_id" in journals._fields:
            in_unit = journals.filtered(lambda j: j.operating_unit_id == operating_unit)
            journals = in_unit or journals
        if len(journals) > 1 and method in ("bank_transfer", "cheque"):
            operating = journals.filtered(lambda j: j.fix_treasury_role == "operating")
            journals = operating if len(operating) == 1 else journals
        return journals if len(journals) == 1 else self.env["account.journal"]

    # payment.requested producers -> (partner, bank, amount, currency, approver, ou, ref)
    def _resolve_expense_claim(self, claim, payload):
        employee = claim.employee_id.sudo()
        partner = employee.work_contact_id or employee.user_id.partner_id
        bank = self.env["res.partner.bank"]
        if "primary_bank_account_id" in employee._fields:
            bank = employee.primary_bank_account_id
        if claim.state not in ("approved", "paid"):
            raise UserError(
                "Expense claim %s is %s, not approved." % (claim.display_name, claim.state)
            )
        return {
            "source_model": claim._name,
            "source_id": claim.id,
            "partner": partner,
            "bank": bank,
            "amount": claim.amount,
            "currency": claim.currency_id,
            "approver": claim.approved_by if "approved_by" in claim._fields else False,
            "ref": payload.get("invoice_ref") or "EXP/%s" % claim.id,
            "options": {"payee": "employee:%s %s" % (employee.id, employee.name)},
        }

    def _resolve_advance_excess(self, adv, payload):
        """An advance settled by claims above it pays the employee the excess.
        The advance's own disbursement already uses (fix.employee.advance,
        id), so the excess is its own source key."""
        claims = adv.claim_ids.filtered(lambda c: c.state in ("approved", "paid"))
        excess = round(sum(claims.mapped("amount")) - adv.amount, 2)
        if excess <= 0.005:
            raise UserError("Advance %s has no excess to pay." % adv.display_name)
        employee = adv.employee_id.sudo()
        partner = employee.work_contact_id or employee.user_id.partner_id
        bank = self.env["res.partner.bank"]
        if "primary_bank_account_id" in employee._fields:
            bank = employee.primary_bank_account_id
        return {
            "source_model": "fix.employee.advance.excess",
            "source_id": adv.id,
            "partner": partner,
            "bank": bank,
            "amount": excess,
            "currency": adv.currency_id,
            "approver": adv.approved_by,
            "ref": payload.get("invoice_ref") or "%s/EXCESS" % adv.name,
            "options": {
                "payee": "employee:%s %s" % (employee.id, employee.name),
                "company_id": adv.company_id.id,
                "operating_unit_id": adv.operating_unit_id.id,
            },
        }

    def _resolve_vendor_invoice(self, inv, payload):
        partner = inv.vendor_id.commercial_partner_id
        banks = partner.bank_ids
        approver = False
        for name in ("approved_by", "approved_by_id", "dofa_approved_by"):
            if name in inv._fields and inv[name]:
                approver = inv[name]
                break
        return {
            "source_model": inv._name,
            "source_id": inv.id,
            "partner": partner,
            "bank": banks if len(banks) == 1 else self.env["res.partner.bank"],
            "amount": inv.total_payable,
            "currency": inv.currency_id,
            "approver": approver,
            "ref": payload.get("invoice_ref") or inv.display_name,
            "options": {"method": "cash"} if inv.payment_channel == "non_bank" else {},
        }

    def _payment_resolvers(self):
        """The documents that may request a payment, each with the resolver
        that re-reads its payee, bank, amount and approver. A module that adds
        a payable document extends this (cd_ap_ext: the supplier advance)."""
        return {
            "fix.expense.claim": self._resolve_expense_claim,
            "fix.employee.advance": self._resolve_advance_excess,
            "fix.vendor.invoice": self._resolve_vendor_invoice,
        }

    @api.model
    def consume_payment_requested(self, event: dict) -> FixPaymentExecution:
        """Registered consumer of payment.requested (fix.event.consumer).

        Runs only from the event relay. The payload is a pointer, not the
        terms: the payee, bank account and amount are re-read from the
        requesting document, a payload amount that differs is refused, and
        the result is a pinned DRAFT execution (idempotent — DI-04)."""
        if not self.env.su:
            raise AccessError(
                "payment.requested is consumed by the event relay only; treasury users raise "
                "manual instructions on the form."
            )
        payload = event.get("payload") or {}
        model = event.get("aggregate") or ""
        try:
            res_id = int(event.get("aggregate_id") or 0)
        except (TypeError, ValueError):
            res_id = 0
        resolvers = self._payment_resolvers()
        if model not in resolvers or model not in self.env:
            raise UserError("payment.requested from %s is not a known payment source." % model)
        source = self.env[model].sudo().browse(res_id).exists()
        if not source:
            raise UserError("payment.requested %s/%s: no such document." % (model, res_id))
        terms = resolvers[model](source, payload)
        if (
            payload.get("amount") is not None
            and abs(float(payload.get("amount") or 0.0) - terms["amount"]) > 0.005
        ):
            raise UserError(
                "payment.requested %s/%s says %s but the document says %s: refused."
                % (model, res_id, payload.get("amount"), terms["amount"])
            )
        return self._fix_request_payment(
            terms["source_model"],
            terms["source_id"],
            terms["partner"],
            terms["bank"],
            terms["amount"],
            terms["currency"],
            terms["ref"],
            terms["approver"],
            **terms["options"],
        )

    # ------------------------------------------------------------ preparation
    def _check_releasable(self):
        self.ensure_one()
        if self.amount <= 0:
            raise UserError("%s has no amount to pay." % self.name)
        bank_account_of(self.journal_id)
        if self.journal_id.company_id != self.company_id:
            raise UserError("The paying bank account belongs to another company.")
        if self.method == "cash" and self.journal_id.type != "cash":
            raise UserError("A cash payment is paid from a cash journal.")
        if (
            self.method in ("bank_transfer", "mobile_fs", "cheque", "card")
            and self.journal_id.type != "bank"
        ):
            raise UserError("A %s is paid from a bank journal." % self.method)
        if self.method == "card":
            # A05 FIN-25: back to the card it came from, through the acquirer
            if not self._fix_journal_fits(self.journal_id, "card"):
                raise UserError(
                    "%s is a card refund: it is paid through the card acquirer (gateway) "
                    "account, not %s." % (self.name, self.journal_id.display_name)
                )
            if not (self.original_payment_ref or "").strip():
                raise UserError(
                    "%s is a card refund: record the original card transaction it reverses."
                    % self.name
                )
        if self.method == "bank_transfer":
            if self.rail not in ("beftn", "rtgs", "npsb"):
                raise UserError("Select the bank rail (BEFTN / RTGS / NPSB) for %s." % self.name)
            acct = self.partner_bank_id
            if not acct or not acct.acc_number:
                raise UserError("%s needs the payee's bank account." % self.name)
            if self.rail in ("beftn", "rtgs") and not acct.fix_routing_number:
                raise UserError(
                    "%s: the payee account %s has no routing number (BEFTN/RTGS need it)."
                    % (self.name, acct.acc_number)
                )
            if self.rail == "rtgs":
                minimum = float_param(self.env, "cd_cash_position.rtgs_min_amount", 0.0)
                if minimum and self.amount < minimum:
                    raise UserError(
                        "RTGS is for amounts of at least %s (system parameter "
                        "cd_cash_position.rtgs_min_amount); use BEFTN." % minimum
                    )
        if self.method == "mobile_fs" and not (
            self.partner_bank_id and self.partner_bank_id.acc_number
        ):
            raise UserError("%s needs the payee's MFS wallet number." % self.name)

    def _fix_duplicates(self):
        """Other open instructions to the same account (or payee) for the same
        amount and currency inside the duplicate window (M50-14)."""
        self.ensure_one()
        days = int(float_param(self.env, PARAM_DUP_DAYS, MATCH_WINDOW_DAYS))
        since = fields.Datetime.now() - timedelta(days=max(days, 0))
        domain = [
            ("id", "!=", self.id),
            ("company_id", "=", self.company_id.id),
            ("currency_id", "=", self.currency_id.id),
            ("state", "in", OPEN_STATES),
            ("create_date", ">=", since),
        ]
        if self.partner_bank_id:
            domain.append(("partner_bank_id", "=", self.partner_bank_id.id))
        elif self.partner_id:
            domain.append(("partner_id", "=", self.partner_id.id))
        else:
            domain.append(("payee", "=ilike", (self.payee or "").strip()))
        return self.sudo().search(domain).filtered(lambda p: abs(p.amount - self.amount) < 0.005)

    def _fix_check_duplicate(self):
        for pay in self:
            dups = pay._fix_duplicates()
            if dups and not (pay.duplicate_reason or "").strip():
                raise UserError(
                    "%s repeats %s (same payee account, amount %.2f and currency within %s "
                    "days). Record why it is not a duplicate payment before preparing it."
                    % (
                        pay.name,
                        ", ".join(dups.mapped("name")),
                        pay.amount,
                        int(float_param(self.env, PARAM_DUP_DAYS, MATCH_WINDOW_DAYS)),
                    )
                )

    def action_prepare(self, justification=None):
        """An accountant checks the instruction and readies it for release.
        Above the single-releaser ceiling the authorisation is requested from
        the M63 engine at once."""
        require_role(self.env, GROUP_ACCOUNTANT, "Preparing a payment instruction")
        for pay in self:
            if pay.state != "pending":
                raise UserError(
                    "%s is %s: only a draft instruction is prepared." % (pay.name, pay.state)
                )
            pay._check_releasable()
            pay._fix_check_duplicate()
            pay._guarded().write(
                {
                    "state": "prepared",
                    "prepared_by_id": self.env.uid,
                    "prepared_at": fields.Datetime.now(),
                }
            )
            if pay._approval_needed():
                text = (justification or pay.dofa_justification or "").strip()
                if not text and pay.source_pinned:
                    text = "Pays %s approved by %s." % (
                        pay.source_ref or pay.source_model,
                        pay.source_approved_by_id.name or "its source workflow",
                    )
                if not text and pay._dofa_tier_rank(
                    pay._dofa_current_tier()
                ) >= pay._dofa_tier_rank("tier_2"):
                    raise UserError(
                        "%s needs a written justification for its %s authorisation."
                        % (pay.name, pay._dofa_current_tier())
                    )
                pay.action_request_approval(justification=text or None)
            pay.message_post(body="Prepared for release by %s." % self.env.user.name)
        return True

    def action_request_approval(self, justification=None):
        for pay in self:
            if pay.state != "prepared":
                raise UserError("Prepare %s before asking for its authorisation." % pay.name)
        return super().action_request_approval(justification=justification)

    def action_cancel(self):
        require_role(self.env, GROUP_ACCOUNTANT, "Cancelling a payment instruction")
        for pay in self:
            if pay.state not in ("pending", "prepared", "failed"):
                raise UserError("%s was released to the bank: it is not cancelled." % pay.name)
            if pay.approval_state in ("pending", "approved") or pay.dofa_approved:
                pay._approval_void("the instruction was cancelled")
            pay._guarded().write({"state": "cancelled"})
        return True

    # ------------------------------------------------------------ release
    def _fix_assert_releaser(self):
        """F1: a named Accounting Administrator who is not the creator,
        preparer, the source's approver or the DOFA approver."""
        self.ensure_one()
        user = self.env.user
        if user._is_superuser() or not user.has_group(GROUP_ADMIN):
            raise UserError(
                "Releasing payment %s needs a named Accounting Administrator; the release "
                "is the second signature on the instruction." % self.name
            )
        clash = user & (self._fix_conflicted_users() | self.sudo().dofa_approved_by)
        if clash:
            raise UserError(
                "Segregation of duties: %s created, prepared, approved or authorised %s and "
                "cannot also release it." % (user.name, self.name)
            )

    def _fix_assert_payable_bank(self):
        """B2 contract (cd_ap_ext): an unconfirmed or recently changed payee
        account is not paid. Called whenever the contract is installed."""
        Bank = self.env["res.partner.bank"]
        check = getattr(Bank, "_fix_assert_payable_bank", None)
        for pay in self:
            if pay.partner_bank_id and callable(check):
                check(pay.partner_bank_id)

    def _fix_assert_period_open(self):
        """BRU-TRE-15: no release into a locked (closed) M19 period."""
        for pay in self:
            company = pay.company_id
            day = pay.value_date or fields.Date.context_today(pay)
            locks = [
                company[f]
                for f in ("fiscalyear_lock_date", "hard_lock_date")
                if f in company._fields and company[f]
            ]
            lock = max(locks) if locks else None
            if lock and day <= lock:
                raise UserError(
                    "%s is dated %s, inside a closed accounting period (locked to %s)."
                    % (pay.name, day, lock)
                )

    def _instruction_csv(self) -> str:
        """A neutral instruction file. Bank-specific BEFTN/RTGS layouts differ
        per bank and are NOT verified — the treasury team uploads this to the
        bank portal or maps it to the bank's own template."""
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(
            [
                "instruction_ref",
                "value_date",
                "rail",
                "debit_account",
                "payee",
                "payee_account",
                "routing_number",
                "amount",
                "currency",
            ]
        )
        for pay in self:
            writer.writerow(
                [
                    pay.name,
                    pay.value_date or fields.Date.context_today(pay),
                    pay.rail or pay.method,
                    pay.journal_id.bank_acc_number or pay.journal_id.code,
                    pay.partner_bank_id.acc_holder_name or pay.payee,
                    pay.partner_bank_id.acc_number
                    or (pay.original_payment_ref if pay.method == "card" else "")
                    or "",
                    pay.partner_bank_id.fix_routing_number or "",
                    "%.2f" % pay.amount,
                    pay.currency_id.name,
                ]
            )
        return buf.getvalue()

    def action_release(self):
        """The second signature: release the prepared (and, above the ceiling,
        authorised) instruction to the bank. Pins what the bank file carries."""
        for pay in self:
            if pay.state != "prepared":
                raise UserError(
                    "%s is '%s': an instruction is prepared (and authorised when its "
                    "amount requires) before it is released." % (pay.name, pay.state)
                )
            pay._fix_assert_releaser()
            pay._check_releasable()
            if pay._approval_needed():
                if pay.approval_state != "approved":
                    raise UserError(
                        "%s (%s) needs DOFA %s approval through the M63 inbox before release "
                        "(above the single-releaser ceiling)."
                        % (pay.name, pay._dofa_amount_label(), pay._dofa_current_tier())
                    )
                pay._dofa_assert_approved("Releasing payment %s" % pay.name)
            pay._fix_assert_payable_bank()
            pay._fix_assert_period_open()
            pay._fix_check_duplicate()
            vals = {
                "state": "sent",
                "sent_at": fields.Datetime.now(),
                "sent_by_id": self.env.uid,
                "released_amount": pay.amount,
                "released_partner_bank_id": pay.partner_bank_id.id or False,
                "released_acc_number": pay.partner_bank_id.acc_number or False,
                "released_journal_id": pay.journal_id.id,
            }
            if pay.method in ("bank_transfer", "mobile_fs", "card"):
                attachment = (
                    self.env["ir.attachment"]
                    .sudo()
                    .create(
                        {
                            "name": "%s.csv" % (pay.name or "instruction").replace("/", "-"),
                            "raw": pay._instruction_csv().encode("utf-8"),
                            "mimetype": "text/csv",
                            "res_model": pay._name,
                            "res_id": pay.id,
                        }
                    )
                )
                vals["instruction_attachment_id"] = attachment.id
            if pay.method == "cheque":
                vals["bank_reference"] = pay._fix_issue_cheque()
            pay._guarded().write(vals)
            pay.message_post(body="Instruction released — awaiting the bank's statement debit.")
        return True

    def _fix_issue_cheque(self):
        """An issued cheque takes the next leaf of the paying account's active
        cheque book (BRU-TRE-17)."""
        self.ensure_one()
        Cheque = self.env["fix.cheque"].sudo()
        existing = Cheque.search([("payment_execution_id", "=", self.id)], limit=1)
        if existing and existing.state not in ("cancelled", "bounced"):
            return existing.cheque_no
        book = self.env["fix.cheque.book"].sudo()._fix_active_book(self.journal_id)
        number = book._fix_take_leaf()
        Cheque._guarded().create(
            {
                "company_id": self.company_id.id,
                "operating_unit_id": self.operating_unit_id.id,
                "direction": "issued",
                "cheque_no": number,
                "drawee_bank": self.journal_id.bank_id.name or self.journal_id.name,
                "cheque_book_id": book.id,
                "partner_id": self.partner_id.id,
                "payee_name": self.payee,
                "amount": self.amount,
                "currency_id": self.currency_id.id,
                "cheque_date": self.value_date or fields.Date.context_today(self),
                "journal_id": self.journal_id.id,
                "payment_execution_id": self.id,
            }
        )
        return number

    # ------------------------------------------------------------- confirmation
    def _fix_assert_evidence(self, line):
        """An outgoing payment is confirmed only by an imported statement
        DEBIT of the released amount, on the paying account, imported by
        someone other than the releaser."""
        self.ensure_one()
        if not is_imported(line):
            raise UserError(
                "Statement line %s was not imported from a bank statement file: it is not "
                "bank evidence." % (line.reference or line.id)
            )
        if line.amount >= 0:
            raise UserError(
                "A bank CREDIT (%s) never confirms the outgoing payment %s."
                % (line.amount, self.name)
            )
        released = self.released_amount or self.amount
        if abs(abs(line.amount) - released) > 0.005:
            raise UserError(
                "The bank debited %s but %s was released for %s."
                % (abs(line.amount), self.name, released)
            )
        journal = self.released_journal_id or self.journal_id
        if line.journal_id and journal and line.journal_id != journal:
            raise UserError("The statement line is on another bank account than %s." % self.name)
        if self.sent_by_id and line.sudo().create_uid == self.sent_by_id:
            raise UserError(
                "Segregation of duties: the statement confirming %s was imported by its "
                "releaser %s." % (self.name, self.sent_by_id.name)
            )

    def _confirm_executed(self, source, statement_line=None, reference=None, entry_date=None):
        """The bank confirmed the debit: post Dr liability / Cr bank for the
        RELEASED amount and publish payment.executed (exactly once).

        Evidence rule (F1): a typed reference confirms nothing. The debit is
        evidenced either by an IMPORTED statement line (source='statement',
        checked by _fix_assert_evidence) or — the one narrow exception — by
        the payroll bank-return FILE (source='payroll_return'): the relay-side
        payroll consumer confirms only from a hash-verified return import
        (fix.payroll.bank.return), which is imported bank evidence of the
        debit, so the F1 rule holds; the exception is restricted to
        payroll-released instructions confirmed by the superuser relay."""
        self.ensure_one()
        if self.state != "sent":
            raise UserError(
                "%s is '%s': only a sent payment is confirmed." % (self.name, self.state)
            )
        if source == "payroll_return":
            trusted = self.env.su or self.env.user.has_group(GROUP_ACCOUNTANT)
            if not (self.payroll_released and trusted and (reference or "").strip()):
                raise UserError(
                    "The payroll return confirmation runs only from the imported return "
                    "file's reference, on a payroll-released instruction."
                )
        elif source != "statement" or not statement_line:
            raise UserError("A payment is confirmed only by an imported bank statement debit.")
        else:
            self._fix_assert_evidence(statement_line)
            entry_date = statement_line.date
        if source != "payroll_return" and (
            abs(self.amount - self.released_amount) > 0.005
            or self.partner_bank_id != self.released_partner_bank_id
        ):
            raise UserError(
                "%s no longer matches the instruction released to the bank." % self.name
            )
        # (payroll_return excepted: the return's failed-item netting legally
        # rewrote the amount between release and confirmation; the file's own
        # netting validated it)
        bank = bank_account_of(self.released_journal_id or self.journal_id)
        move = self.env["account.move"]
        note = False
        # statement: the bank debited the released amount; payroll_return:
        # the netted amount the return file leaves the bank owing
        amount = (
            self.released_amount if source == "statement" else (self.amount or self.released_amount)
        )
        if self.source_posts_gl:
            note = "Payment entry booked by the requesting document (%s)" % self.source_model
        else:
            debit = self.debit_account_id or treasury_account(
                self.env, self.company_id, "outgoing_clearing"
            )
            move = post_treasury_move(
                self.env,
                self.company_id,
                entry_date or fields.Date.context_today(self),
                "PAY %s — %s" % (self.name, self.payee),
                [
                    (debit, "Payment %s" % self.name, amount, 0.0, self.partner_id),
                    (bank, "Paid %s" % self.payee, 0.0, amount, self.partner_id),
                ],
                source="treasury",
                # A05 FIN-10 / I3: the payment's unit and the source's branch
                **self._fix_posting_dims(),
            )
        executed_vals = {
            "state": "executed",
            "executed_at": fields.Datetime.now(),
            "confirmation_source": source,
            "bank_reference": reference or self.bank_reference,
            "move_id": move.id,
            "gl_note": note,
        }
        if statement_line:
            executed_vals["statement_line_id"] = statement_line.id
        self._guarded().write(executed_vals)
        self._publish_executed()

    def _publish_executed(self):
        publish(
            self.env,
            "payment.executed",
            "fix.payment.execution",
            self.id,
            {
                "source_model": self.source_model,
                "source_id": self.source_id,
                "amount": self.released_amount or self.amount,
                "method": self.method,
            },
        )

    def _fix_posting_dims(self):
        """A05 FIN-10 / I3: the dimensions treasury's entry for this payment
        carries — its operating unit and the source document's branch."""
        self.ensure_one()
        return {
            "branch": self.branch_id or None,
            "operating_unit": self.operating_unit_id or None,
        }

    def action_pay_cash_voucher(self, received_by=None):
        """A05 FIN-12: the confirmation path of a CASH instruction. Cash never
        reaches a bank statement, so a released cash instruction is a cash
        voucher on its cash journal: a named cashier / treasury user — not the
        requester, the source's approver or the releaser — hands the money
        over, and that hand-over posts Dr the instruction's debit account /
        Cr the cash journal's account, with the payment's unit and branch.
        Exactly once (the state moves to executed in the same transaction)."""
        user = self.env.user
        if user._is_superuser() or not any(
            user.has_group(g) for g in (GROUP_ACCOUNTANT, GROUP_ADMIN, GROUP_CASHIER)
        ):
            raise UserError(
                "Paying out a cash voucher needs a named cashier or treasury user; the "
                "hand-over is a person's signature."
            )
        for pay in self:
            # the cashier reads the instruction (base read + unit rule); the
            # journal, accounts and stamps are read as the system
            rec = pay.sudo()
            if rec.method != "cash":
                raise UserError(
                    "%s is a %s: only a cash instruction is paid on a cash voucher."
                    % (rec.name, dict(self._fields["method"].selection)[rec.method])
                )
            if rec.state != "sent":
                raise UserError(
                    "%s is '%s': a cash voucher is paid out only after the instruction is "
                    "prepared and released." % (rec.name, rec.state)
                )
            journal = rec.released_journal_id or rec.journal_id
            if journal.type != "cash" or self._fix_is_cheque_in_hand(journal):
                raise UserError(
                    "%s is not paid from a cash journal (cheques in hand are not cash to pay "
                    "out)." % rec.name
                )
            clash = user & (rec.create_uid | rec.source_approved_by_id | rec.sent_by_id)
            if clash:
                raise UserError(
                    "Segregation of duties: %s requested, approved or released %s and cannot "
                    "also pay its cash out." % (user.name, pay.name)
                )
            if abs(rec.amount - rec.released_amount) > 0.005:
                raise UserError(
                    "%s no longer matches the instruction that was released." % pay.name
                )
            today = fields.Date.context_today(pay.with_context(tz="Asia/Dhaka"))
            move = self.env["account.move"]
            note = False
            if rec.source_posts_gl:
                note = "Payment entry booked by the requesting document (%s)" % rec.source_model
            else:
                debit = rec.debit_account_id or treasury_account(
                    rec.env, rec.company_id, "outgoing_clearing"
                )
                move = post_treasury_move(
                    rec.env,
                    rec.company_id,
                    today,
                    "CASH %s — %s" % (rec.name, rec.payee),
                    [
                        (debit, "Payment %s" % rec.name, rec.released_amount, 0.0, rec.partner_id),
                        (
                            bank_account_of(journal),
                            "Cash paid %s" % rec.payee,
                            0.0,
                            rec.released_amount,
                            rec.partner_id,
                        ),
                    ],
                    source="treasury",
                    **rec._fix_posting_dims(),
                )
            voucher = (
                self.env["ir.sequence"].sudo().next_by_code("fix.payment.cash.voucher")
                or "CPV/%s" % rec.id
            )
            rec._guarded().write(
                {
                    "state": "executed",
                    "executed_at": fields.Datetime.now(),
                    "confirmation_source": "cash_voucher",
                    "cash_voucher_no": voucher,
                    "cash_paid_by_id": user.id,
                    "cash_paid_at": fields.Datetime.now(),
                    "cash_received_by": (received_by or "").strip() or rec.payee,
                    "bank_reference": voucher,
                    "move_id": move.id,
                    "gl_note": note,
                }
            )
            rec.message_post(
                body="Cash voucher %s paid out by %s to %s."
                % (voucher, user.name, rec.cash_received_by)
            )
            rec._publish_executed()
        return True

    def action_confirm_bank(self):
        """Confirm from the bank's reference: it must identify an IMPORTED
        statement debit of the released amount on the paying account. A typed
        reference with no such line confirms nothing."""
        Line = self.env["fix.bank.statement.line"]
        for pay in self:
            if pay.state != "sent":
                raise UserError("%s is not awaiting the bank's confirmation." % pay.name)
            refs = [r for r in ((pay.bank_reference or "").strip(), pay.name) if r]
            journal = pay.released_journal_id or pay.journal_id
            candidates = Line.search(
                [
                    ("company_id", "=", pay.company_id.id),
                    ("match_state", "=", "unmatched"),
                    ("statement_file_hash", "!=", False),
                    ("amount", "<", 0),
                    ("journal_id", "in", (journal.id, False)),
                ]
            ).filtered(
                lambda ln, p=pay, refs=refs: (
                    abs(abs(ln.amount) - p.released_amount) < 0.005
                    and any(has_token(ln._text(), r) for r in refs)
                )
            )
            if len(candidates) != 1:
                raise UserError(
                    "No single imported bank statement debit of %.2f quotes %s: import the "
                    "bank statement first — a typed reference is not bank evidence."
                    % (pay.released_amount, " / ".join(refs))
                )
            candidates._fix_match_document("matched_payment_id", pay, "manual")
        return True

    def action_mark_failed(self):
        require_role(self.env, GROUP_ACCOUNTANT, "Recording a bank rejection")
        for pay in self:
            if pay.state != "sent":
                raise UserError("Only a sent payment can be rejected by the bank.")
            if not (pay.failure_reason or "").strip():
                raise UserError("Record the bank's rejection reason on %s first." % pay.name)
            pay._guarded().write({"state": "failed"})
            pay._publish_failed(pay.failure_reason)
        return True

    def _publish_failed(self, reason):
        publish(
            self.env,
            "payment.failed",
            "fix.payment.execution",
            self.id,
            {"source_model": self.source_model, "source_id": self.source_id, "reason": reason},
        )

    def _fix_return_after_clearing(self, reason):
        """The bank took the money back after confirming it (a cleared cheque
        returned): reverse treasury's entry and re-open the payment."""
        for pay in self:
            if pay.state != "executed":
                continue
            reversal = self.env["account.move"]
            if pay.move_id and not pay.reversal_move_id:
                lines = [
                    (ln.account_id, "Return of %s" % pay.name, ln.credit, ln.debit, ln.partner_id)
                    for ln in pay.move_id.line_ids
                ]
                reversal = post_treasury_move(
                    self.env,
                    pay.company_id,
                    fields.Date.context_today(pay),
                    "RETURN %s — %s" % (pay.name, reason),
                    lines,
                    source="treasury",
                    **pay._fix_posting_dims(),
                )
            pay._guarded().write(
                {
                    "state": "failed",
                    "failure_reason": reason,
                    "reversal_move_id": reversal.id or pay.reversal_move_id.id,
                    "gl_note": (
                        "Returned after clearing; the requesting document must reverse its "
                        "own payment entry (%s)" % pay.source_model
                    )
                    if pay.source_posts_gl
                    else pay.gl_note,
                }
            )
            pay.message_post(body="Returned by the bank after clearing: %s." % reason)
            pay._publish_failed(reason)

    def action_retry(self):
        require_role(self.env, GROUP_ACCOUNTANT, "Re-queueing a payment")
        for pay in self:
            if pay.state != "failed":
                raise UserError("Only a failed payment is re-queued.")
            if pay.approval_state in ("pending", "approved") or pay.dofa_approved:
                pay._approval_void("the payment failed and was re-queued")
            pay._guarded().write(
                {
                    "state": "pending",
                    "sent_at": False,
                    "sent_by_id": False,
                    "prepared_by_id": False,
                    "prepared_at": False,
                    "instruction_attachment_id": False,
                    "released_amount": 0.0,
                    "released_partner_bank_id": False,
                    "released_acc_number": False,
                    "released_journal_id": False,
                    "statement_line_id": False,
                    "confirmation_source": False,
                    "move_id": False,
                }
            )
        return True

    def action_execute(self) -> None:
        """LEGACY direct execution for trusted service code only (sudo):
        marks the payment executed WITHOUT bank evidence — "caller-asserted",
        un-bank-confirmed, no GL — so it stays on the reconciliation
        exceptions until an imported statement debit confirms it. Refused to
        every user (it was callable by JSON-RPC: M50-15)."""
        if not self.env.su:
            raise AccessError(
                "action_execute is a legacy service call; treasury releases a payment and the "
                "imported bank statement confirms it."
            )
        for payment in self:
            if payment.state != "pending":
                raise UserError("Only pending payments execute")
            payment._guarded().write(
                {
                    "state": "executed",
                    "executed_at": fields.Datetime.now(),
                    "confirmation_source": "caller_asserted",
                    "gl_note": "Not posted: executed by the caller without bank evidence",
                }
            )
            payment._publish_executed()


class FixBankStatementImport(models.Model):
    """One uploaded bank statement file (CSV, MT940 or XLSX)."""

    _name = "fix.bank.statement.import"
    _description = "Bank Statement Import"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit", index=True)
    journal_id = fields.Many2one(
        "account.journal",
        string="Bank Account",
        required=True,
        domain="[('type', '=', 'bank'), ('company_id', '=', company_id)]",
    )
    file = fields.Binary(string="Statement File", attachment=True)
    filename = fields.Char(string="File Name")
    format_type = fields.Selection(
        [("auto", "Auto-Detect"), ("csv", "CSV"), ("mt940", "MT940"), ("xlsx", "XLSX (Excel)")],
        default="auto",
        required=True,
        string="Format",
    )
    state = fields.Selection(
        [("draft", "Draft"), ("imported", "Imported"), ("duplicate", "Duplicate File")],
        default="draft",
        required=True,
        tracking=True,
    )
    imported_count = fields.Integer(string="Lines Imported", readonly=True)
    file_hash = fields.Char(string="File Hash", readonly=True)
    line_ids = fields.One2many("fix.bank.statement.line", "import_id", string="Lines")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"state", "imported_count", "file_hash"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "draft" for r in self):
            locked |= {"file", "journal_id", "format_type", "company_id"}
        return locked

    def write(self, vals):
        if self and not (self.env.su or self._fix_guard_has_token()):
            frozen = {"file", "journal_id", "format_type", "company_id"} & set(vals)
            if frozen and any(r.state != "draft" for r in self):
                raise UserError("An imported statement file is evidence and cannot change.")
        return super().write(vals)

    @staticmethod
    def _xlsx_to_csv(raw: bytes) -> str:
        """Re-read an Excel statement into the CSV contract the parser
        already understands (Date, Reference, Description, Credit, Debit).
        Bangladeshi banks issue XLSX portals exports far more often than
        camt feeds — this keeps one parsing pipeline (G12, report R11)."""
        import csv as _csv
        import io as _io
        import zipfile

        try:
            import openpyxl
        except ImportError:
            raise UserError("openpyxl is not available on this server.") from None
        if not zipfile.is_zipfile(_io.BytesIO(raw)):
            raise UserError("The XLSX file is not a valid Excel workbook.")
        workbook = openpyxl.load_workbook(_io.BytesIO(raw), read_only=True, data_only=True)
        sheet = workbook.worksheets[0]
        rows = [list(r) for r in sheet.iter_rows(values_only=True)]
        workbook.close()

        def _norm(text):
            return str(text or "").strip().lower().replace(" ", "").replace(".", "")

        header_idx, colmap = None, {}
        for idx, row in enumerate(rows[:10]):
            labels = {_norm(c): pos for pos, c in enumerate(row or [])}
            if any(k in labels for k in ("date", "valuedate", "trxdate")):
                header_idx = idx
                for key, variants in (
                    ("date", ("date", "valuedate", "trxdate", "transactiondate")),
                    ("ref", ("reference", "ref", "refno", "chequeno", "trnid", "trxid")),
                    ("narration", ("description", "narration", "particulars", "remarks")),
                    ("credit", ("credit", "deposit", "inflow", "cr")),
                    ("debit", ("debit", "withdrawal", "outflow", "dr")),
                    ("amount", ("amount", "netamount")),
                ):
                    for variant in variants:
                        if variant in labels:
                            colmap[key] = labels[variant]
                            break
                break
        if header_idx is None or "date" not in colmap:
            raise UserError(
                "No date column found in the XLSX header — expected Date/Value Date "
                "plus Credit/Debit (or Amount) columns."
            )

        def _cell(row, key):
            pos = colmap.get(key)
            if pos is None or pos >= len(row) or row[pos] is None:
                return ""
            return str(row[pos]).strip()

        buf = _io.StringIO()
        writer = _csv.writer(buf)
        writer.writerow(["Date", "Reference", "Description", "Credit", "Debit"])
        for row in rows[header_idx + 1 :]:
            if not any(c is not None and str(c).strip() for c in row):
                continue
            first = _cell(row, "date")
            if not first or first.lower().startswith("total"):
                continue
            writer.writerow(
                [
                    first,
                    _cell(row, "ref"),
                    _cell(row, "narration"),
                    _cell(row, "credit"),
                    _cell(row, "debit"),
                ]
            )
        return buf.getvalue()

    def action_import(self):
        require_role(self.env, GROUP_ACCOUNTANT, "Importing a bank statement")
        for rec in self:
            if rec.state != "draft":
                raise UserError("This statement file was already processed.")
            if not rec.file:
                raise UserError("Attach the statement file first (CSV, MT940 or XLSX).")
            raw = base64.b64decode(rec.file)
            content = raw.decode("utf-8-sig", errors="replace")
            file_hash = None
            effective_format = rec.format_type
            if rec.format_type == "xlsx" or raw[:2] == b"PK":
                content = self._xlsx_to_csv(raw)
                file_hash = hashlib.sha256(raw).hexdigest()
                effective_format = "csv"
            result = (
                self.env["fix.bank.statement.line"]
                .with_company(rec.company_id)
                ._guarded()
                .import_bank_feed(
                    content,
                    format_type=effective_format,
                    journal_id=rec.journal_id.id,
                    import_id=rec.id,
                    file_hash=file_hash,
                )
            )
            rec._guarded().write(
                {
                    "state": "duplicate" if result["status"] == "duplicate_file" else "imported",
                    "imported_count": result["imported"],
                    "file_hash": result["file_hash"],
                }
            )
        return True


class FixBankStatementLine(models.Model):
    """A bank statement line awaiting reconciliation (T07)."""

    _name = "fix.bank.statement.line"
    _description = "Bank Statement Line"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "date desc, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Operating Unit",
        index=True,
        help="Empty = company-wide bank account",
    )
    journal_id = fields.Many2one(
        "account.journal", string="Bank Account", index=True, domain="[('type', '=', 'bank')]"
    )
    import_id = fields.Many2one("fix.bank.statement.import", string="Import", index=True)
    date = fields.Date(required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount = fields.Monetary(currency_field="currency_id", required=True)
    reference = fields.Char(string="Bank Reference", index=True)
    narration = fields.Char()
    match_state = fields.Selection(
        [("unmatched", "Unmatched"), ("auto", "Auto-Matched"), ("manual", "Manually Matched")],
        default="unmatched",
        required=True,
    )
    matched_payment_id = fields.Many2one("fix.payment.execution", string="Matched Payment")
    matched_deposit_id = fields.Many2one("fix.cash.deposit", string="Matched Cash Deposit")
    matched_cheque_id = fields.Many2one("fix.cheque", string="Matched Cheque")
    matched_gateway_id = fields.Many2one("fix.gateway.settlement", string="Matched Settlement")
    matched_invoice_ref = fields.Char(string="Matched Invoice")
    matched_kind = fields.Selection(
        [
            ("payment", "Outgoing Payment"),
            ("deposit", "Branch Cash Deposit"),
            ("cheque", "Cheque"),
            ("gateway", "Gateway / MFS Settlement"),
            ("charge", "Bank Charge"),
        ],
        string="Matched To",
        readonly=True,
    )
    matched_by_id = fields.Many2one("res.users", string="Matched By", readonly=True, copy=False)
    is_bank_charge = fields.Boolean(string="Bank Charge", readonly=True)
    charge_move_id = fields.Many2one("account.move", string="Charge Entry", readonly=True)
    statement_sequence = fields.Char(string="Statement Sequence", index=True)
    statement_file_hash = fields.Char(string="Statement File Hash", index=True)

    _MATCH_DOCS = (
        "matched_payment_id",
        "matched_deposit_id",
        "matched_cheque_id",
        "matched_gateway_id",
    )
    _EVIDENCE = (
        "amount",
        "date",
        "reference",
        "narration",
        "journal_id",
        "currency_id",
        "company_id",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "match_state",
            "matched_kind",
            "matched_invoice_ref",
            "matched_by_id",
            "is_bank_charge",
            "charge_move_id",
            "statement_sequence",
            "statement_file_hash",
            "import_id",
        }

    def unlink(self):
        # T-14 immutable audit: an imported statement line is the bank's own
        # record of a movement — the evidence every reconciliation and
        # confirmation decision stands on. It is never deleted; a bad import
        # is corrected by importing the bank's corrected statement.
        if not (self.env.su or self._fix_guard_has_token()):
            raise UserError(
                "Bank statement lines are the bank's evidence of a movement and are "
                "never deleted. Reconcile, flag or re-import the corrected statement."
            )
        return super().unlink()

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self:
            if any(is_imported(ln) or ln.match_state != "unmatched" for ln in self):
                locked |= set(self._EVIDENCE)
            if any(ln.match_state != "unmatched" for ln in self):
                locked |= set(self._MATCH_DOCS)
        return locked

    @api.constrains("match_state", "matched_kind", *_MATCH_DOCS, "charge_move_id")
    def _check_matched_to_something(self):
        """A line leaves the unmatched list only paired with a real document
        (or booked as a charge): never cleared to nothing (M50-6)."""
        for ln in self:
            if ln.match_state == "unmatched":
                continue
            has_doc = any(ln[f] for f in self._MATCH_DOCS) or (
                ln.matched_kind == "charge" and ln.charge_move_id
            )
            if not (ln.matched_kind and has_doc):
                raise ValidationError(
                    "Statement line %s cannot be marked matched without the document it "
                    "matches." % (ln.reference or ln.id)
                )

    @api.model_create_multi
    def create(self, vals_list):
        if not (self.env.su or self._fix_guard_has_token()):
            raise UserError(
                "Statement lines come only from an imported bank statement file (Statements "
                "Import). A hand-typed line is not bank evidence."
            )
        return super().create(vals_list)

    def write(self, vals):
        if self and not (self.env.su or self._fix_guard_has_token()):
            evidence = set(self._EVIDENCE) & set(vals)
            docs = set(self._MATCH_DOCS) & set(vals)
            for ln in self:
                if evidence and (is_imported(ln) or ln.match_state != "unmatched"):
                    changed = [f for f in evidence if ln._fix_guard_differs(f, vals[f], ln[f])]
                    if changed:
                        raise UserError(
                            "Statement line %s is bank evidence: %s cannot change."
                            % (ln.reference or ln.id, ", ".join(sorted(changed)))
                        )
                if docs and ln.match_state != "unmatched":
                    changed = [f for f in docs if ln._fix_guard_differs(f, vals[f], ln[f])]
                    if changed:
                        raise UserError(
                            "Statement line %s is matched: its document cannot change."
                            % (ln.reference or ln.id)
                        )
        return super().write(vals)

    @api.model
    def import_bank_feed(
        self,
        file_content: str,
        format_type: str = "auto",
        journal_id=None,
        import_id=None,
        file_hash: str | None = None,
    ) -> dict:
        """INT-006: Ingest electronic bank statement feed with deduplication
        and sequence audit. Reached through fix.bank.statement.import
        (action_import) or trusted service code — never typed in by RPC.
        ``file_hash`` lets the caller hash the ORIGINAL file bytes (an XLSX
        re-read as CSV must still dedup against the workbook it came from)."""
        if not (self.env.su or self._fix_guard_has_token()):
            raise AccessError("Bank statements are imported from a statement file record.")
        file_hash = file_hash or hashlib.sha256(file_content.encode("utf-8")).hexdigest()

        existing = self.sudo().search([("statement_file_hash", "=", file_hash)], limit=1)
        if existing:
            return {"imported": 0, "status": "duplicate_file", "file_hash": file_hash}

        common = {
            "company_id": self.env.company.id,
            "statement_file_hash": file_hash,
            "journal_id": journal_id or False,
            "import_id": import_id or False,
        }
        lines_to_create = []
        try:
            from services.reconciliation.src.bank_feed_parser import parse_bank_feed

            parsed = parse_bank_feed(file_content, format_type=format_type)
            for item in parsed.lines:
                lines_to_create.append(
                    dict(
                        common,
                        date=item.date,
                        amount=float(item.amount),
                        reference=item.reference,
                        narration=item.narration,
                        statement_sequence=parsed.sequence_number,
                    )
                )
        except Exception:
            # discard anything the parser produced before it failed — the
            # fallback re-reads the whole file (no duplicated lines)
            lines_to_create = []
            reader = csv.DictReader(io.StringIO(file_content))
            for row in reader:
                dt_str = row.get("Date") or row.get("date")
                amt_str = (
                    row.get("Amount")
                    or row.get("amount")
                    or row.get("Credit")
                    or row.get("credit", "0")
                )
                if dt_str and amt_str:
                    lines_to_create.append(
                        dict(
                            common,
                            date=dt_str,
                            amount=float(amt_str),
                            reference=row.get("Reference") or row.get("reference") or "",
                            narration=row.get("Description") or row.get("narration") or "",
                        )
                    )

        if lines_to_create:
            self._guarded().create(lines_to_create)

        return {"imported": len(lines_to_create), "status": "success", "file_hash": file_hash}

    # ------------------------------------------------------------------ matching

    def _text(self):
        return "%s %s" % (self.reference or "", self.narration or "")

    def _in_window(self, start_date):
        if not start_date:
            return True
        return (
            start_date - timedelta(days=1)
            <= self.date
            <= start_date + timedelta(days=MATCH_WINDOW_DAYS)
        )

    def _payment_candidates(self, taken):
        """Outgoing payments this DEBIT line can confirm: same company /
        currency, the released amount to the paisa, sent (or executed by a
        legacy caller without bank evidence), not released by the importer."""
        if self.amount >= 0 or not is_imported(self):
            return self.env["fix.payment.execution"]
        payments = self.env["fix.payment.execution"].search(
            [
                ("company_id", "=", self.company_id.id),
                ("currency_id", "=", self.currency_id.id),
                "|",
                ("state", "=", "sent"),
                "&",
                ("state", "=", "executed"),
                ("statement_line_id", "=", False),
            ]
        )
        importer = self.sudo().create_uid

        def fits(p):
            released = p.released_amount if p.state == "sent" else p.amount
            journal = p.released_journal_id or p.journal_id
            return (
                p.id not in taken
                and p.method != "cheque"  # cheques confirm through their clearing
                and abs(abs(self.amount) - released) < 0.005
                and (not self.journal_id or not journal or journal == self.journal_id)
                and not (p.state == "sent" and p.sent_by_id and p.sent_by_id == importer)
            )

        return payments.filtered(fits)

    def _match_payment(self, taken):
        text = self._text()
        candidates = self._payment_candidates(taken)
        if not candidates:
            return False
        by_ref = candidates.filtered(
            lambda p: (
                has_token(text, p.name)
                or has_token(text, p.bank_reference)
                or (
                    LEGACY_PREFIX.get(p.source_model)
                    and has_token(text, "%s/%s" % (LEGACY_PREFIX[p.source_model], p.source_id))
                )
            )
        )
        chosen = by_ref if len(by_ref) == 1 else False
        if not chosen and not by_ref:
            # rule 2: payee named on the line + amount + date window, unique only
            by_payee = candidates.filtered(
                lambda p: (
                    p.payee
                    and p.payee.upper() in text.upper()
                    and self._in_window(p.sent_at.date() if p.sent_at else None)
                )
            )
            chosen = by_payee if len(by_payee) == 1 else False
        if not chosen:
            return False
        ref = chosen.name
        if LEGACY_PREFIX.get(chosen.source_model):
            legacy = "%s/%s" % (LEGACY_PREFIX[chosen.source_model], chosen.source_id)
            ref = legacy if has_token(text, legacy) else ref
        if chosen.state == "sent":
            chosen._confirm_executed("statement", statement_line=self, reference=self.reference)
        else:
            chosen._guarded().write({"statement_line_id": self.id})
        return {
            "matched_payment_id": chosen.id,
            "matched_invoice_ref": ref or str(chosen.source_id),
            "matched_kind": "payment",
        }

    def _match_deposit(self):
        if self.amount <= 0 or not is_imported(self):
            return False
        deposits = self.env["fix.cash.deposit"].search(
            [
                ("company_id", "=", self.company_id.id),
                ("state", "=", "in_transit"),
                ("dispatch_move_id", "!=", False),
            ]
        )
        text = self._text()
        # The deposit slip number identifies the deposit; the bank's credited
        # amount is then taken as evidence — a short / over credit becomes a
        # variance on the deposit (never silently absorbed).
        hits = deposits.filtered(
            lambda d: (
                (not self.journal_id or d.journal_id == self.journal_id)
                and has_token(text, d.slip_no or d.name)
            )
        )
        if len(hits) != 1:
            return False
        hits._credit_from_statement(self)
        return {
            "matched_deposit_id": hits.id,
            "matched_invoice_ref": hits.name,
            "matched_kind": "deposit",
        }

    def _match_cheque(self):
        if not is_imported(self):
            return False
        cheques = self.env["fix.cheque"].search(
            [
                ("company_id", "=", self.company_id.id),
                ("state", "in", ("deposited", "issued")),
            ]
        )
        text = self._text()
        hits = cheques.filtered(
            lambda c: (
                abs(abs(self.amount) - c.amount) < 0.005
                and ((c.direction == "received") == (self.amount > 0))
                and has_token(text, c.cheque_no)
            )
        )
        if len(hits) != 1:
            return False
        hits._clear_from_statement(self)
        return {
            "matched_cheque_id": hits.id,
            "matched_invoice_ref": hits.cheque_no,
            "matched_kind": "cheque",
        }

    def _match_gateway(self):
        if self.amount <= 0 or not is_imported(self):
            return False
        batches = self.env["fix.gateway.settlement"].search(
            [
                ("company_id", "=", self.company_id.id),
                ("state", "in", ("imported", "matched", "exceptions")),
                ("statement_line_id", "=", False),
            ]
        )
        text = self._text()
        hits = batches.filtered(
            lambda b: (
                abs(b.total_net - self.amount) < 0.005
                and (not self.journal_id or b.journal_id == self.journal_id)
                and self.date >= (b.settlement_date or self.date) - timedelta(days=1)
                and (
                    has_token(text, b.name)
                    or has_token(text, b.provider_batch_ref)
                    or b.provider_label() in text.upper()
                )
            )
        )
        if len(hits) != 1:
            return False
        hits._guarded().write({"statement_line_id": self.id})
        hits._recompute_match()
        return {
            "matched_gateway_id": hits.id,
            "matched_invoice_ref": hits.name,
            "matched_kind": "gateway",
        }

    @api.model
    def auto_match(self) -> int:
        """T07: the in-Odoo half of reconciliation. An IMPORTED line matches
        ONE document only when the amount agrees to the paisa AND a whole-token
        reference (or, for payments, a unique payee + date-window candidate)
        identifies it; anything ambiguous stays unmatched for a human."""
        require_role(self.env, GROUP_ACCOUNTANT, "Running the statement auto-match")
        matched = 0
        pending = self.search(
            [
                ("match_state", "=", "unmatched"),
                ("statement_file_hash", "!=", False),
                ("company_id", "in", self.env.companies.ids),
            ]
        )
        taken: set[int] = set()
        for line in pending:
            try:
                # one line that cannot take its match (an account not
                # configured, a closed period) must not stop the others
                with self.env.cr.savepoint():
                    vals = (
                        line._match_payment(taken)
                        or line._match_deposit()
                        or line._match_cheque()
                        or line._match_gateway()
                    )
            except (UserError, ValidationError) as exc:
                self.env.invalidate_all(flush=False)
                _logger.warning("auto-match skipped statement line %s: %s", line.id, exc)
                continue
            if vals:
                if vals.get("matched_payment_id"):
                    taken.add(vals["matched_payment_id"])
                vals["match_state"] = "auto"
                line._guarded().write(vals)
                matched += 1
        return matched

    @api.model
    def _fix_reconciliation_blockers(self, company, date_to):
        """BRU-TRE-19 / FR-TRE-012 gate for M19 period close: the imported
        bank statement lines of `company` dated on or before `date_to` that
        are still unmatched (nothing explains them). M19 refuses the close
        while this returns anything."""
        return self.sudo().search(
            [
                ("company_id", "=", company.id),
                ("statement_file_hash", "!=", False),
                ("match_state", "=", "unmatched"),
                ("date", "<=", date_to),
            ]
        )

    @api.model
    def _cron_auto_match(self):
        """Scheduled auto-match, company by company (ir.cron)."""
        total = 0
        for company in self.env["res.company"].sudo().search([]):
            total += (
                self.sudo()
                .with_company(company)
                .with_context(allowed_company_ids=[company.id])
                .auto_match()
            )
        return total

    def _fix_match_document(self, field, doc, how):
        """Pair this imported line with ONE document and let the document
        take the bank's evidence. Sign, amount and SoD are checked here."""
        self.ensure_one()
        if self.match_state != "unmatched":
            raise UserError("This line is already matched.")
        if not is_imported(self):
            raise UserError(
                "Statement line %s was typed, not imported: it is not bank evidence."
                % (self.reference or self.id)
            )
        if field == "matched_payment_id":
            if not self.env.su and doc.sent_by_id == self.env.user:
                raise UserError(
                    "Segregation of duties: %s released %s and cannot also confirm it."
                    % (self.env.user.name, doc.name)
                )
            if doc.state == "sent":
                doc._confirm_executed("statement", statement_line=self, reference=self.reference)
            elif doc.state == "executed" and not doc.statement_line_id:
                doc._fix_assert_evidence(self)
                doc._guarded().write({"statement_line_id": self.id})
            else:
                raise UserError("%s is not awaiting a bank confirmation." % doc.name)
            kind = "payment"
        elif field == "matched_deposit_id":
            if abs(self.amount - doc.amount) > 0.005:
                raise UserError(
                    "Amounts differ (line %s vs deposit %s): a manual match needs the same "
                    "amount; a short credit is matched by its slip number."
                    % (self.amount, doc.amount)
                )
            doc._credit_from_statement(self)
            kind = "deposit"
        elif field == "matched_cheque_id":
            if abs(abs(self.amount) - doc.amount) > 0.005:
                raise UserError(
                    "Amounts differ (line %s vs cheque %s)." % (self.amount, doc.amount)
                )
            if (doc.direction == "received") != (self.amount > 0):
                raise UserError(
                    "The statement line's sign does not fit a %s cheque." % doc.direction
                )
            doc._clear_from_statement(self)
            kind = "cheque"
        else:
            if self.amount <= 0 or abs(self.amount - doc.total_net) > 0.005:
                raise UserError(
                    "A settlement is matched to a bank CREDIT of its net total (%s)."
                    % doc.total_net
                )
            doc._guarded().write({"statement_line_id": self.id})
            doc._recompute_match()
            kind = "gateway"
        self._guarded().write(
            {
                field: doc.id,
                "match_state": how,
                "matched_kind": kind,
                "matched_invoice_ref": doc.display_name,
                "matched_by_id": self.env.uid,
            }
        )

    def action_confirm_manual_match(self):
        """A human paired the line with a document on the form: the amount and
        sign rules apply, then the document takes the bank's evidence."""
        require_role(self.env, GROUP_ACCOUNTANT, "Matching a bank statement line")
        for line in self:
            if line.match_state != "unmatched":
                raise UserError("This line is already matched.")
            picked = [f for f in self._MATCH_DOCS if line[f]]
            if len(picked) != 1:
                raise UserError("Pick exactly one document to match this line to.")
            doc = line[picked[0]]
            amount = (
                doc.total_net
                if picked[0] == "matched_gateway_id"
                else (doc.released_amount or doc.amount)
                if picked[0] == "matched_payment_id"
                else doc.amount
            )
            if abs(abs(line.amount) - amount) > 0.005:
                raise UserError(
                    "Amounts differ (line %s vs document %s): a match needs the same amount."
                    % (line.amount, amount)
                )
            line._fix_match_document(picked[0], doc, "manual")
        return True

    def action_post_bank_charge(self):
        """A debit line the bank charged (fees, excise duty, SMS charges):
        post Dr bank charges / Cr bank and close the line. Above the
        single-person ceiling it is booked by an Accounting Administrator who
        did not import the statement."""
        require_role(self.env, GROUP_ACCOUNTANT, "Booking a bank charge")
        ceiling = float_param(self.env, PARAM_CHARGE_CEILING, 0.0)
        for line in self:
            if line.match_state != "unmatched" or line.amount >= 0:
                raise UserError("Only an unmatched debit line is booked as a bank charge.")
            if not is_imported(line):
                raise UserError("Only an imported statement line is booked as a bank charge.")
            amount = abs(line.amount)
            if amount > ceiling + 0.005 and not self.env.su:
                if not self.env.user.has_group(GROUP_ADMIN):
                    raise UserError(
                        "A bank charge of %.2f is above the %.2f single-person ceiling "
                        "(%s): an Accounting Administrator books it."
                        % (amount, ceiling, PARAM_CHARGE_CEILING)
                    )
                if line.sudo().create_uid == self.env.user:
                    raise UserError(
                        "Segregation of duties: the person who imported the statement does not "
                        "also write its debits off as bank charges."
                    )
            bank = bank_account_of(line.journal_id)
            expense = treasury_account(self.env, line.company_id, "bank_charges")
            move = post_treasury_move(
                self.env,
                line.company_id,
                line.date,
                "BANK CHARGE %s %s" % (line.reference or "", line.narration or ""),
                [
                    (expense, line.narration or "Bank charge", amount, 0.0, None),
                    (bank, line.narration or "Bank charge", 0.0, amount, None),
                ],
                source="treasury",
            )
            line._guarded().write(
                {
                    "is_bank_charge": True,
                    "charge_move_id": move.id,
                    "match_state": "manual",
                    "matched_kind": "charge",
                    "matched_by_id": self.env.uid,
                }
            )
        return True


class FixCashPosition(models.Model):
    """Cash position snapshot across bank (posted GL), branch drawers (M04
    cash shifts), petty cash and cash-in-transit, less payments released or
    queued but not yet confirmed by the bank."""

    _name = "fix.cash.position"
    _description = "Cash Position Snapshot"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "as_of desc, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    as_of = fields.Datetime(default=fields.Datetime.now, required=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    bank_balance = fields.Monetary(
        string="Bank",
        currency_field="currency_id",
        compute="_compute_position",
        store=True,
        help="Posted GL balance of the company's bank journals' accounts at the snapshot time",
    )
    drawer_float_total = fields.Monetary(
        string="Branch Drawers",
        currency_field="currency_id",
        compute="_compute_drawers",
        store=True,
    )
    petty_cash_total = fields.Monetary(
        string="Petty Cash", currency_field="currency_id", compute="_compute_position", store=True
    )
    cash_in_transit_total = fields.Monetary(
        string="Cash-in-Transit",
        currency_field="currency_id",
        compute="_compute_position",
        store=True,
    )
    pending_payments = fields.Monetary(
        string="Pending Payments",
        currency_field="currency_id",
        compute="_compute_position",
        store=True,
        help="Payments queued, prepared or sent but not yet confirmed by the bank",
    )
    total_position = fields.Monetary(
        string="Total Position", currency_field="currency_id", compute="_compute_total", store=True
    )

    @api.depends(
        "bank_balance",
        "drawer_float_total",
        "petty_cash_total",
        "cash_in_transit_total",
        "pending_payments",
    )
    def _compute_total(self) -> None:
        for snap in self:
            snap.total_position = (
                snap.bank_balance
                + snap.drawer_float_total
                + snap.petty_cash_total
                + snap.cash_in_transit_total
                - snap.pending_payments
            )

    @api.depends("company_id", "as_of")
    def _compute_position(self) -> None:
        for snap in self:
            company = snap.company_id
            journals = self.env["account.journal"].search(
                [("type", "=", "bank"), ("company_id", "=", company.id)]
            )
            accounts = journals.mapped("default_account_id")
            as_of_date = (snap.as_of or fields.Datetime.now()).date()
            snap.bank_balance = gl_balance(self.env, accounts, company, date_to=as_of_date)
            funds = self.env["fix.imprest.fund"].search(
                [("company_id", "=", company.id), ("state", "=", "active")]
            )
            snap.petty_cash_total = sum(funds.mapped("book_balance"))
            snap.cash_in_transit_total = sum(
                self.env["fix.cash.deposit"]
                .search([("company_id", "=", company.id), ("state", "=", "in_transit")])
                .mapped("amount")
            )
            snap.pending_payments = sum(
                self.env["fix.payment.execution"]
                .search(
                    [
                        ("company_id", "=", company.id),
                        ("state", "in", ("pending", "prepared", "sent")),
                    ]
                )
                .mapped("amount")
            )

    # Without any dependency Odoo never computes a stored field, so every
    # snapshot carried drawer_float_total = 0. The snapshot's own company and
    # timestamp drive it: computed at creation, re-taken when as_of moves.
    @api.depends("company_id", "as_of")
    def _compute_drawers(self) -> None:
        """Open M04 cash shifts carry their expected closing as float — only
        the snapshot's OWN company's drawers (the search was company-blind,
        so one entity's position counted every other entity's cash)."""
        for snap in self:
            shifts = self.env["fix.cash.shift"].search(
                [("state", "in", ("open", "counting")), ("company_id", "=", snap.company_id.id)]
            )
            snap.drawer_float_total = sum(shifts.mapped("expected_closing"))

    def action_take_snapshot(self):
        """Take a fresh snapshot for each selected snapshot's company."""
        created = self.browse()
        for company in self.mapped("company_id") or self.env.company:
            created |= self.create({"company_id": company.id, "as_of": fields.Datetime.now()})
        return {"snapshot_ids": created.ids}
