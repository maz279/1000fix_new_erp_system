# cd_ap_ext — payee bank accounts under dual control (A08 S1, M52-1, BRU-APE-09).
#
# A08 audit (2026-11-04), M52-1: after a payment run was approved, the run
# line's bank account was re-pointed to an accomplice, or the vendor's own
# account number was edited by any Contact-Creation user, and the release
# paid it. The bank account is the highest-risk field in payables (spec M52
# §2 "second").
#
# Here every res.partner.bank carries a CONFIRMATION that only the system
# sets: a second person confirms a proposed account (fix.payee.bank.change,
# or for an M42 supplier the A06 fix.supplier.bank.change) after an
# out-of-band call-back that is recorded (reference, who called, when). Any
# later change of a payment field (number, bank, holder, routing, owner)
# withdraws the confirmation by itself. _fix_assert_payable_bank() is the one
# gate every payment path calls (M52 runs here, M50 releases and M53 payout
# runs through the B1/B4 contracts); it refuses an unconfirmed account, an
# account changed since its confirmation, and one inside the configurable
# cooling-off period after confirmation.
import hashlib
from datetime import timedelta

from odoo import api, fields, models
from odoo.addons.cd_fixed_asset_ext.models.fix_asset_common import (
    attach_upload,
    attachment_names,
)
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

# Hours after a confirmation before the first payment may leave (BRU-APE-09).
# Default 0 = payable as soon as confirmed; a business decision (A08 report §7, B4).
PARAM_COOLING_OFF = "cd_ap_ext.bank_cooling_off_hours"

# The fields that decide where money goes: a change of any of them is a new
# payee account, whatever the record id says.
PAYMENT_FIELDS = (
    "acc_number",
    "bank_id",
    "partner_id",
    "acc_holder_name",
    "allow_out_payment",
    "fix_routing_number",
)
CONFIRM_FIELDS = (
    "fix_confirmed",
    "fix_confirmed_by_id",
    "fix_confirmed_at",
    "fix_verification_ref",
    "fix_verified_by_id",
    "fix_bank_change_id",
    "fix_confirmed_fingerprint",
    "fix_changed_at",
    "fix_changed_by_id",
)

_CONFIRM_KEY = "fix_payee_bank_confirmation"
_CONFIRM_TOKEN = object()

GROUP_ACCOUNTANT = "account.group_account_user"
GROUP_MANAGER = "account.group_account_manager"


def _norm(value):
    return "".join(ch for ch in str(value or "") if ch.isalnum()).upper()


def float_param(env, key, default):
    raw = env["ir.config_parameter"].sudo().get_param(key)
    if raw in (None, False, ""):
        return float(default)
    try:
        return float(raw)
    except (TypeError, ValueError):
        return float(default)


class ResPartnerBankPayable(models.Model):
    _inherit = "res.partner.bank"

    fix_confirmed = fields.Boolean(
        string="Payee Account Confirmed",
        readonly=True,
        copy=False,
        help="Set by the system only, when a second person confirms the account after a "
        "recorded call-back. Any change of the number, bank, holder, routing or owner "
        "clears it: the account is then unpayable until confirmed again.",
    )
    fix_confirmed_by_id = fields.Many2one(
        "res.users", string="Confirmed By", readonly=True, copy=False
    )
    fix_confirmed_at = fields.Datetime(string="Confirmed On", readonly=True, copy=False)
    fix_verification_ref = fields.Char(string="Call-Back Verification", readonly=True, copy=False)
    fix_verified_by_id = fields.Many2one(
        "res.users", string="Call-Back Made By", readonly=True, copy=False
    )
    fix_bank_change_id = fields.Many2one(
        "fix.payee.bank.change", string="Confirming Change", readonly=True, copy=False
    )
    fix_confirmed_fingerprint = fields.Char(readonly=True, copy=False)
    fix_changed_at = fields.Datetime(string="Payment Details Changed On", readonly=True, copy=False)
    fix_changed_by_id = fields.Many2one(
        "res.users", string="Payment Details Changed By", readonly=True, copy=False
    )

    # ------------------------------------------------------------ helpers --
    def _fix_fingerprint(self):
        self.ensure_one()
        parts = [
            _norm(self.acc_number),
            str(self.bank_id.id or ""),
            str(self.partner_id.commercial_partner_id.id or ""),
            _norm(self.acc_holder_name),
            _norm(self["fix_routing_number"] if "fix_routing_number" in self._fields else ""),
        ]
        return hashlib.sha256("|".join(parts).encode()).hexdigest()

    def _fix_confirm_open(self):
        return self.env.context.get(_CONFIRM_KEY) is _CONFIRM_TOKEN

    def _fix_confirming(self):
        return self.with_context(**{_CONFIRM_KEY: _CONFIRM_TOKEN})

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_confirm_open():
            for vals in vals_list:
                touched = [f for f in CONFIRM_FIELDS if vals.get(f)]
                if touched:
                    raise UserError(
                        "A payee account is confirmed only by a second person through a "
                        "bank-detail change (call-back recorded): %s cannot be set directly."
                        % ", ".join(touched)
                    )
        now = fields.Datetime.now()
        for vals in vals_list:
            vals.setdefault("fix_changed_at", now)
            vals.setdefault("fix_changed_by_id", self.env.uid)
        return super().create(vals_list)

    def write(self, vals):
        if not self._fix_confirm_open():
            touched = [f for f in CONFIRM_FIELDS if f in vals]
            if touched:
                raise UserError(
                    "A payee account is confirmed only by a second person through a "
                    "bank-detail change (call-back recorded): %s cannot be written directly."
                    % ", ".join(touched)
                )
            payment = [f for f in PAYMENT_FIELDS if f in vals and f in self._fields]
            if payment:
                before = {rec.id: rec._fix_fingerprint() for rec in self}
                result = super().write(vals)
                moved = self.filtered(lambda r: r._fix_fingerprint() != before[r.id])
                if moved:
                    # A changed account is a new payee: the confirmation lapses.
                    super(ResPartnerBankPayable, moved).write(
                        {
                            "fix_confirmed": False,
                            "fix_changed_at": fields.Datetime.now(),
                            "fix_changed_by_id": self.env.uid,
                        }
                    )
                    for rec in moved:
                        publish(
                            self.env,
                            "payee_bank.changed",
                            "res.partner.bank",
                            rec.id,
                            {"partner_id": rec.partner_id.id, "changed_by": self.env.uid},
                        )
                return result
        return super().write(vals)

    def _fix_mark_confirmed(self, verification_ref, verified_by, change=None):
        """System only: record the second person's confirmation."""
        if not (self._fix_confirm_open() or self.env.su):
            raise UserError("A payee account is confirmed through a bank-detail change only.")
        for rec in self:
            rec._fix_confirming().sudo().write(
                {
                    "fix_confirmed": True,
                    "fix_confirmed_by_id": self.env.uid,
                    "fix_confirmed_at": fields.Datetime.now(),
                    "fix_verification_ref": verification_ref,
                    "fix_verified_by_id": verified_by.id if verified_by else False,
                    "fix_bank_change_id": change.id if change else False,
                    "fix_confirmed_fingerprint": rec._fix_fingerprint(),
                }
            )
        return True

    def _fix_supplier_confirmation(self):
        """The A06 M42 supplier bank-change confirmed THIS account as it stands
        now (cd_vendor_portal loads after cd_ap_ext, so it is read by name)."""
        self.ensure_one()
        if "fix.supplier.bank.change" not in self.env:
            return False
        change = (
            self.env["fix.supplier.bank.change"]
            .sudo()
            .search(
                [("partner_bank_id", "=", self.id), ("state", "=", "confirmed")],
                order="confirmed_at desc, id desc",
                limit=1,
            )
        )
        if not change or _norm(change.acc_number) != _norm(self.acc_number):
            return False
        if (
            self.fix_changed_at
            and change.confirmed_at
            and change.confirmed_at < self.fix_changed_at
        ):
            return False
        return change

    def _fix_is_confirmed(self):
        """Confirmed as it stands now, here or through the M42 supplier change."""
        self.ensure_one()
        bank = self.sudo()
        if bank.fix_confirmed and bank.fix_confirmed_fingerprint == bank._fix_fingerprint():
            return True
        return bool(bank._fix_supplier_confirmation())

    def _fix_payable_problem(self):
        """Why this account cannot be paid now, or False."""
        self.ensure_one()
        bank = self.sudo()
        if not bank.acc_number:
            return "the payee account has no account number"
        confirmed_at = None
        if bank.fix_confirmed and bank.fix_confirmed_fingerprint == bank._fix_fingerprint():
            confirmed_at = bank.fix_confirmed_at
        else:
            change = bank._fix_supplier_confirmation()
            if change:
                confirmed_at = change.confirmed_at
        if not confirmed_at:
            if (
                bank.fix_confirmed_at
                and bank.fix_changed_at
                and bank.fix_changed_at > bank.fix_confirmed_at
            ):
                return (
                    "payee account %s was changed after its confirmation; a second person must "
                    "verify it again (BRU-APE-09)" % bank.acc_number
                )
            return (
                "payee account %s is not confirmed: a bank-detail change must be verified by "
                "call-back and confirmed by a second person (BRU-APE-09)" % bank.acc_number
            )
        hours = float_param(self.env, PARAM_COOLING_OFF, 0.0)
        if hours > 0 and confirmed_at + timedelta(hours=hours) > fields.Datetime.now():
            return (
                "payee account %s was confirmed on %s; the %.0f-hour cooling-off period (%s) "
                "has not passed" % (bank.acc_number, confirmed_at, hours, PARAM_COOLING_OFF)
            )
        return False

    @api.model
    def _fix_assert_payable_bank(self, bank):
        """The payment gate (B1/B4 contract): refuse an unconfirmed account, an
        account changed since its confirmation, or one still cooling off."""
        bank = bank if isinstance(bank, models.BaseModel) else self.browse(bank)
        if not bank or len(bank) != 1:
            raise UserError("No payee bank account: nothing can be paid.")
        problem = bank._fix_payable_problem()
        if problem:
            raise UserError("Payment blocked: %s." % problem)
        return True


class FixPayeeBankChange(models.Model):
    """A proposed payee bank account (or a change of one) for a payee that is
    not an M42 supplier: employees, landlords, one-off vendors. Two people: the
    proposer records the call-back, a different accounting manager confirms."""

    _name = "fix.payee.bank.change"
    _description = "Payee Bank-Detail Change"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(required=True, default="New", copy=False, readonly=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    partner_id = fields.Many2one("res.partner", string="Payee", required=True, index=True)
    partner_bank_id = fields.Many2one(
        "res.partner.bank",
        string="Account To Confirm / Change",
        help="Empty: a new account is created on confirmation.",
    )
    acc_number = fields.Char(string="Account / Wallet Number", required=True)
    bank_id = fields.Many2one("res.bank", string="Bank")
    routing_number = fields.Char(string="BEFTN Routing Number")
    acc_holder_name = fields.Char(string="Account Holder")
    verification_ref = fields.Char(
        string="Call-Back Verification",
        help="Who was called, on which independently known number, when, and what they "
        "confirmed. Required to propose.",
    )
    verified_by_id = fields.Many2one(
        "res.users", string="Call-Back Made By", default=lambda self: self.env.user
    )
    evidence_attachment_ids = fields.Many2many("ir.attachment", string="Evidence")
    # A08 S1: the workspace form uploads the call-back evidence here
    evidence_file = fields.Binary(
        string="Upload Evidence",
        compute="_compute_evidence_file",
        inverse="_inverse_evidence_file",
        attachment=False,
    )
    evidence_filename = fields.Char(string="Evidence File Name", copy=False)
    evidence_names = fields.Char(string="Evidence Attached", compute="_compute_evidence_names")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("proposed", "Proposed"),
            ("confirmed", "Confirmed"),
            ("rejected", "Rejected"),
        ],
        required=True,
        default="draft",
        tracking=True,
    )
    proposed_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    proposed_at = fields.Datetime(readonly=True, copy=False)
    confirmed_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    confirmed_at = fields.Datetime(readonly=True, copy=False)
    reject_reason = fields.Char(readonly=True, copy=False)
    result_bank_id = fields.Many2one(
        "res.partner.bank", string="Confirmed Account", readonly=True, copy=False
    )

    TERMS = (
        "partner_id",
        "partner_bank_id",
        "acc_number",
        "bank_id",
        "routing_number",
        "acc_holder_name",
        "verification_ref",
        "verified_by_id",
        "company_id",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "proposed_by_id",
            "proposed_at",
            "confirmed_by_id",
            "confirmed_at",
            "reject_reason",
            "result_bank_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "draft" for r in self):
            locked |= set(self.TERMS) | {"evidence_file", "evidence_filename"}
        return locked

    def _compute_evidence_file(self):
        for rec in self:
            rec.evidence_file = False

    def _inverse_evidence_file(self):
        for rec in self:
            attach_upload(
                rec,
                "evidence_attachment_ids",
                rec.evidence_file,
                rec.evidence_filename,
                "Call-back evidence %s" % rec.name,
            )

    @api.depends("evidence_attachment_ids")
    def _compute_evidence_names(self):
        for rec in self:
            rec.evidence_names = attachment_names(rec.evidence_attachment_ids)

    @api.model
    def _cron_open_confirmation_queue(self):
        """A08 S1: the queue of accounts awaiting a second person. Every payee
        account that is not confirmed as it stands gets one open DRAFT change,
        carrying its current details, for a person to complete with the
        call-back. Moves no money and confirms nothing. Left out: the company's
        own bank accounts (not payees), M42 suppliers (their change request is
        fix.supplier.bank.change) and accounts with a change already open."""
        Bank = self.env["res.partner.bank"].sudo()
        own = self.env["res.company"].sudo().search([]).mapped("partner_id")
        opened = self.browse()
        for bank in Bank.search([("acc_number", "!=", False)]):
            payee = bank.partner_id
            if not payee or payee.commercial_partner_id in own or bank._fix_is_confirmed():
                continue
            if self._is_supplier(payee):
                continue
            if self.sudo().search_count(
                [("partner_bank_id", "=", bank.id), ("state", "in", ("draft", "proposed"))]
            ):
                continue
            company = bank.company_id or payee.company_id or self.env.company
            opened |= self.sudo().create(
                {
                    "company_id": company.id,
                    "partner_id": payee.id,
                    "partner_bank_id": bank.id,
                    "acc_number": bank.acc_number,
                    "bank_id": bank.bank_id.id or False,
                    "routing_number": bank["fix_routing_number"] or False
                    if "fix_routing_number" in bank._fields
                    else False,
                    "acc_holder_name": bank.acc_holder_name or False,
                    "verified_by_id": False,
                }
            )
        return opened

    @api.constrains("routing_number")
    def _check_routing(self):
        for rec in self:
            if rec.routing_number and not (
                rec.routing_number.strip().isdigit() and len(rec.routing_number.strip()) == 9
            ):
                raise ValidationError("A BEFTN routing number is 9 digits.")

    @api.constrains("partner_id", "partner_bank_id")
    def _check_account_owner(self):
        for rec in self:
            bank = rec.partner_bank_id.sudo()
            if bank and (
                bank.partner_id.commercial_partner_id != rec.partner_id.commercial_partner_id
            ):
                raise ValidationError("The account to change belongs to another payee.")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.payee.bank.change")
                    or "PBANK/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        if (
            set(self.TERMS) & set(vals)
            and not self._fix_guard_open()
            and self.filtered(lambda r: r.state != "draft")
        ):
            raise UserError("A proposed bank-detail change is fixed; reject it and propose again.")
        return super().write(vals)

    def _is_supplier(self, partner):
        if "fix.supplier" not in self.env:
            return False
        commercial = partner.commercial_partner_id
        return bool(
            self.env["fix.supplier"]
            .sudo()
            .search_count([("partner_id", "in", (partner | commercial).ids)])
        )

    def action_propose(self):
        if not (
            self.env.su
            or self.env.user.has_group(GROUP_ACCOUNTANT)
            or self.env.user.has_group(GROUP_MANAGER)
        ):
            raise UserError("Proposing a payee bank account needs an accounting role.")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft bank-detail change is proposed (%s)." % rec.state)
            if not (rec.verification_ref or "").strip():
                raise UserError(
                    "Record the call-back verification (who was called, on which known number, "
                    "when) before proposing %s." % rec.name
                )
            if rec._is_supplier(rec.partner_id):
                raise UserError(
                    "%s is an M42 supplier: its bank details change through the supplier "
                    "bank-detail change request." % rec.partner_id.display_name
                )
            rec._guarded().write(
                {
                    "state": "proposed",
                    "proposed_by_id": self.env.uid,
                    "proposed_at": fields.Datetime.now(),
                    # a queue row opened by the job names nobody yet
                    "verified_by_id": rec.verified_by_id.id or self.env.uid,
                }
            )
            rec.message_post(body="Payee bank-detail change %s proposed." % rec.name)
        return True

    def action_confirm(self):
        """A different accounting manager confirms: the account is written (or
        created) and marked confirmed with the call-back on record."""
        if not (self.env.su or self.env.user.has_group(GROUP_MANAGER)):
            raise UserError("A payee bank account is confirmed by an accounting manager.")
        Bank = self.env["res.partner.bank"].sudo()
        for rec in self:
            if rec.state != "proposed":
                raise UserError(
                    "Confirm a proposed bank change (%s is %s)." % (rec.name, rec.state)
                )
            conflicted = rec.proposed_by_id | rec.create_uid | rec.verified_by_id
            if rec.partner_bank_id:
                conflicted |= rec.partner_bank_id.sudo().fix_changed_by_id
            if self.env.user in conflicted:
                raise UserError(
                    "Segregation of duties (BRU-APE-09): you proposed, verified or changed this "
                    "bank account; another person confirms it."
                )
            if (
                self.env.user.partner_id.commercial_partner_id
                == rec.partner_id.commercial_partner_id
            ):
                raise UserError("A payee cannot confirm their own bank account.")
            vals = {
                "acc_number": rec.acc_number,
                "bank_id": rec.bank_id.id or False,
                "acc_holder_name": rec.acc_holder_name or False,
            }
            if "fix_routing_number" in Bank._fields:
                vals["fix_routing_number"] = rec.routing_number or False
            # Written under the confirmation token: the confirmer does not
            # become the account's "changer" (that is the proposer's change).
            account = rec.partner_bank_id.sudo()
            if not account:
                account = Bank.search(
                    [
                        ("partner_id", "=", rec.partner_id.id),
                        ("acc_number", "=", rec.acc_number),
                    ],
                    limit=1,
                )
            if account:
                account._fix_confirming().write(
                    dict(
                        vals,
                        fix_changed_at=fields.Datetime.now(),
                        fix_changed_by_id=rec.proposed_by_id.id,
                    )
                )
            else:
                account = Bank._fix_confirming().create(
                    dict(
                        vals,
                        partner_id=rec.partner_id.id,
                        fix_changed_by_id=rec.proposed_by_id.id,
                    )
                )
            account._fix_confirming()._fix_mark_confirmed(
                rec.verification_ref, rec.verified_by_id, change=rec
            )
            rec._guarded().write(
                {
                    "state": "confirmed",
                    "confirmed_by_id": self.env.uid,
                    "confirmed_at": fields.Datetime.now(),
                    "result_bank_id": account.id,
                }
            )
            rec.message_post(body="Payee bank-detail change %s confirmed." % rec.name)
            publish(
                self.env,
                "payee_bank.confirmed",
                "res.partner.bank",
                account.id,
                {"change": rec.name, "confirmed_by": self.env.uid, "partner_id": rec.partner_id.id},
            )
        return True

    def action_reject(self, reason=None):
        if not (self.env.su or self.env.user.has_group(GROUP_MANAGER)):
            raise UserError("A payee bank-detail change is rejected by an accounting manager.")
        for rec in self:
            if rec.state not in ("draft", "proposed"):
                raise UserError("Bank change %s is %s." % (rec.name, rec.state))
            if not (reason or "").strip():
                raise UserError("State why bank change %s is rejected." % rec.name)
            rec._guarded().write({"state": "rejected", "reject_reason": reason.strip()})
        return True
