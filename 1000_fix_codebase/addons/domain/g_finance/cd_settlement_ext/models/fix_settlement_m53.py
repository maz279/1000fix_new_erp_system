# fix_settlement_m53 — A08 M53 settlement depth (2026-10-26):
#
#   * fix.commission.scheme       — seller / partner commission rate tables
#                                   (effective-dated; TDS rate and base)
#   * fix.referral (inherited)    — partner / referral commissions accrued
#                                   into the commission ledger and paid in
#                                   payout runs
#   * fix.settlement.adjustment   — escrow holds (open marketplace disputes)
#                                   and clawbacks against future payouts
#   * fix.settlement.recovery     — what each payout run recovered
#   * fix.warranty.provision(.policy) — IAS 37 workmanship-warranty
#                                   provision per period, posted to the GL
#
# Technician incentives are NOT here: they moved to Payroll (A09).
#
# A08 remediation (B4), M53-4/-7/-11: a referral is converted from the
# referred customer's PAID invoice (the base is never typed) and accrued only
# with that evidence; the escrow flag and every adjustment / provision state,
# figure and stamp is guarded (escrow is lifted only by its release, a
# provision posts only the figures its computation produced).
import re
from datetime import date, timedelta

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.addons.cd_billing_engine.models.fix_finance_approval import (
    GROUP_ACCOUNTANT,
    float_param,
    require_role,
)
from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions
from odoo.addons.cd_partner.models.fix_partner import EARNING_STATES
from odoo.addons.cd_partner.models.fix_partner_capture import attribution_days
from odoo.addons.cd_partner.models.fix_partner_ops import payout_account
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

from .fix_settlement_ext import (
    DEFAULT_NON_FILER_UPLIFT,
    PARAM_NON_FILER_UPLIFT,
    _configured_account,
    _configured_journal,
)

PERIOD_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
OPEN_DISPUTE_STATES = ("raised", "investigating", "arbitration", "escalated")

PARTNER_TYPES = [
    ("referral", "Referral Partner"),
    ("reseller", "Reseller"),
    ("franchise", "Franchise"),
    ("alliance", "Strategic Alliance"),
]
SELLER_TIERS = [
    ("unrated", "Unrated (No Measured Performance Yet)"),
    ("platinum", "Platinum Seller (Top 5%)"),
    ("gold", "Gold Seller (Standard Qualified)"),
    ("silver", "Silver Seller (Probationary)"),
    ("at_risk", "At-Risk (Dispute Hold)"),
]


def _is_manager(env) -> bool:
    return env.user.has_group("account.group_account_manager") or env.user.has_group(
        "base.group_system"
    )


def _post_settlement_move(env, company, entry_date, ref, lines):
    """Post a balanced move [(account, name, debit, credit, partner)] through
    M19's engine with the AR posting dimensions. Refuses on missing config."""
    journal = _configured_journal(env, company)
    dims = env["fix.ar.invoice"]._ar_posting_dims()
    move, _ = post_with_dimensions(
        env,
        {
            "journal_id": journal.id,
            "company_id": company.id,
            "date": entry_date,
            "ref": ref,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "account_id": acc.id,
                        "name": name,
                        "debit": debit,
                        "credit": credit,
                        "partner_id": partner or False,
                    },
                )
                for acc, name, debit, credit, partner in lines
            ],
        },
        dict.fromkeys(range(len(lines)), dims),
        source="settlement",
    )
    return move


# ---------------------------------------------------------------------------
# Commission schemes (rate tables)
# ---------------------------------------------------------------------------
class FixCommissionScheme(models.Model):
    """An effective-dated commission rate table line for marketplace sellers
    or channel partners. The TDS rate is statutory master data: the seeded
    value carries a "verify with the tax adviser" note and is edited here,
    never in code."""

    _name = "fix.commission.scheme"
    _description = "Commission Scheme"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "scheme_type, date_from desc, id desc"

    name = fields.Char(required=True, tracking=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    active = fields.Boolean(default=True)
    scheme_type = fields.Selection(
        [("seller", "Marketplace Seller"), ("partner", "Partner / Referral")],
        string="Payee Type",
        required=True,
        default="partner",
        tracking=True,
    )
    partner_type = fields.Selection(
        PARTNER_TYPES, string="Partner Type", help="Empty = every partner type"
    )
    seller_tier = fields.Selection(SELLER_TIERS, string="Seller Tier", help="Empty = every tier")
    commission_rate = fields.Float(
        string="Commission Rate",
        digits=(5, 4),
        tracking=True,
        help="0-1. Zero = the rate agreed on the partner / marketplace order applies",
    )
    tds_rate = fields.Float(string="TDS Rate", digits=(5, 4), tracking=True, help="0-1")
    tds_base = fields.Selection(
        [("commission", "On the Commission"), ("gross", "On the Gross Amount")],
        string="TDS Base",
        required=True,
        default="commission",
    )
    tds_reference = fields.Char(
        string="Statutory Reference", help="Act / section / SRO the TDS rate comes from"
    )
    date_from = fields.Date(string="Effective From", required=True, tracking=True)
    date_to = fields.Date(string="Effective To", tracking=True)
    note = fields.Text(string="Notes")

    @api.constrains(
        "commission_rate",
        "tds_rate",
        "date_from",
        "date_to",
        "scheme_type",
        "partner_type",
        "seller_tier",
        "company_id",
        "active",
    )
    def _check_scheme(self):
        for scheme in self:
            if not (0 <= scheme.commission_rate <= 1 and 0 <= scheme.tds_rate <= 1):
                raise ValidationError("Commission and TDS rates are fractions between 0 and 1")
            if scheme.date_to and scheme.date_to < scheme.date_from:
                raise ValidationError("A scheme cannot end before it starts")
            if not scheme.active:
                continue
            for other in self.search(
                [
                    ("id", "!=", scheme.id),
                    ("company_id", "=", scheme.company_id.id),
                    ("scheme_type", "=", scheme.scheme_type),
                    ("partner_type", "=", scheme.partner_type),
                    ("seller_tier", "=", scheme.seller_tier),
                ]
            ):
                end_a = scheme.date_to or date.max
                end_b = other.date_to or date.max
                if scheme.date_from <= end_b and other.date_from <= end_a:
                    raise ValidationError(
                        "Scheme %s overlaps %s for the same payee type — end the old scheme "
                        "before the new one starts" % (scheme.name, other.name)
                    )

    @api.model
    def _find(self, scheme_type, on_date, company, partner_type=False, seller_tier=False):
        """The scheme in force on a date: the specific line (partner type /
        tier) wins over the generic one."""
        base = [
            ("company_id", "=", company.id),
            ("scheme_type", "=", scheme_type),
            ("date_from", "<=", on_date),
            "|",
            ("date_to", "=", False),
            ("date_to", ">=", on_date),
        ]
        key = "partner_type" if scheme_type == "partner" else "seller_tier"
        value = partner_type if scheme_type == "partner" else seller_tier
        if value:
            specific = self.search([*base, (key, "=", value)], limit=1)
            if specific:
                return specific
        return self.search([*base, (key, "=", False)], limit=1)

    def tds_on(self, commission, gross) -> float:
        self.ensure_one()
        base = commission if self.tds_base == "commission" else gross
        return round((base or 0.0) * self.tds_rate, 2)


# ---------------------------------------------------------------------------
# Partner / referral payouts
# ---------------------------------------------------------------------------
class FixReferral(models.Model):
    """Finance side of a commissioned referral: the commission is accrued
    into the M53 commission ledger (Dr expense / Cr partner payable) and
    paid in the next payout run."""

    _inherit = "fix.referral"

    commission_ledger_id = fields.Many2one(
        "fix.commission.ledger", string="Commission Ledger Entry", readonly=True, copy=False
    )
    payout_state = fields.Selection(
        related="commission_ledger_id.state", string="Payout State", readonly=True
    )
    invoice_id = fields.Many2one(
        "fix.ar.invoice",
        string="Referred Customer's Invoice",
        readonly=True,
        copy=False,
        index=True,
        help="The paid M20 invoice of the referred customer the commission base comes from.",
    )
    convert_invoice_id = fields.Many2one(
        "fix.ar.invoice",
        string="Invoice to Convert From",
        copy=False,
        help="Pick the referred customer's paid invoice, then Convert: the base is read from it.",
    )
    converted_by_id = fields.Many2one("res.users", string="Converted By", readonly=True, copy=False)
    converted_at = fields.Datetime(string="Converted On", readonly=True, copy=False)

    _invoice_unique = models.Constraint(
        "UNIQUE (invoice_id)", "An invoice evidences one referral conversion"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "commission_ledger_id",
            "invoice_id",
            "converted_by_id",
            "converted_at",
        }

    def _fix_referral_evidence(self, evidence=None):
        """The base is the referred customer's PAID invoice (revenue, VAT
        excluded), in the referral's company; each invoice is used once."""
        self.ensure_one()
        invoice = evidence or self.convert_invoice_id
        if isinstance(invoice, str):
            # the number typed at the Convert prompt, in the referral's company
            invoice = (
                self.env["fix.ar.invoice"]
                .sudo()
                .search(
                    [("name", "=", invoice.strip()), ("company_id", "=", self.company_id.id)],
                    limit=1,
                )
            )
        elif isinstance(invoice, int):
            invoice = self.env["fix.ar.invoice"].browse(invoice)
        invoice = invoice.sudo().exists() if invoice else self.env["fix.ar.invoice"]
        if not invoice:
            raise UserError(
                "Referral %s is converted from the referred customer's paid invoice: name the "
                "invoice (the base is never typed)." % self.name
            )
        if not self.referred_partner_id:
            raise UserError("Referral %s names no referred customer." % self.name)
        if (
            invoice.customer_id.commercial_partner_id
            != self.referred_partner_id.commercial_partner_id
        ):
            raise UserError(
                "Invoice %s is not the referred customer's (%s)."
                % (invoice.name, self.referred_partner_id.name)
            )
        if invoice.company_id != self.company_id:
            raise UserError("Invoice %s belongs to another company." % invoice.name)
        if invoice.state != "paid":
            raise UserError(
                "Invoice %s is %s: a referral converts on the referred customer's PAID invoice."
                % (invoice.name, invoice.state)
            )
        # A04 ERP audit M40-F7 (FR-PCM-024, BRU-PCM-05): only revenue raised
        # from the referral date, inside the attribution window, is the
        # referral's. An invoice of 1 Mar 2025 paid a referral of 20 Nov 2026.
        # The window opens on the referral's business day. M20 dates an
        # invoice by the UTC calendar (fields.Date.today) while the referral
        # day is Asia/Dhaka, so an invoice raised minutes after a referral
        # made between 00:00 and 06:00 Dhaka carries the previous date; the
        # referral's own UTC day is accepted as its start too.
        created = fields.Date.to_date(self.create_date) if self.create_date else None
        start = min(d for d in (self.referred_on, created) if d)
        days = attribution_days(self.env)
        if not invoice.invoice_date or not (
            start <= invoice.invoice_date <= start + timedelta(days=days)
        ):
            raise UserError(
                "Invoice %s is dated %s, outside referral %s's attribution window (%s to %s, "
                "%d days): it is not the referral's revenue (BRU-PCM-05)."
                % (
                    invoice.name,
                    invoice.invoice_date,
                    self.name,
                    start,
                    start + timedelta(days=days),
                    days,
                )
            )
        return {
            "base_amount": invoice.taxable_amount,
            "invoice_id": invoice.id,
            "converted_by_id": self.env.uid,
            "converted_at": fields.Datetime.now(),
        }

    def action_accrue_commission(self):
        require_role(self.env, GROUP_ACCOUNTANT, "Accruing a referral commission")
        Scheme = self.env["fix.commission.scheme"]
        Ledger = self.env["fix.commission.ledger"]
        today = fields.Date.context_today(self)
        for ref in self:
            if ref.state != "commissioned":
                raise UserError("Referral %s has not earned its commission yet" % ref.name)
            # the one commission.earned consumer may have raised the row already:
            # finance accrues THAT row (UNIQUE referral_id allows no second one)
            existing = ref.commission_ledger_id or Ledger.sudo().search(
                [("referral_id", "=", ref.id)], limit=1
            )
            if existing and existing.state != "earned":
                raise UserError("Referral %s is already in the commission ledger" % ref.name)
            if not self.env.su:
                if not ref.invoice_id or ref.invoice_id.sudo().state != "paid":
                    raise UserError(
                        "Referral %s carries no paid invoice of the referred customer: nothing "
                        "accrues (A08 M53-4)." % ref.name
                    )
                if abs(ref.base_amount - ref.invoice_id.sudo().taxable_amount) > 0.005:
                    raise UserError(
                        "Referral %s base %.2f is not its invoice's %.2f."
                        % (ref.name, ref.base_amount, ref.invoice_id.sudo().taxable_amount)
                    )
            partner = ref.partner_id
            # A04 ERP audit M40-F9: nothing accrues to a partner out of good
            # standing (a suspended partner's referral waits for reinstatement).
            if partner.state not in EARNING_STATES:
                raise UserError(
                    "Partner %s is %s: no commission accrues (BRU-PCM-01)."
                    % (partner.name, partner.state)
                )
            # A04 ERP audit M40-F6: ONE rate - the one the commission was
            # earned at (frozen on the referral). A scheme's rate no longer
            # overrides it (the GL posted 3% of a referral earned at 50%); the
            # scheme supplies the TDS.
            rate = ref.commission_rate or partner.commission_rate
            if not 0 < rate <= 1:
                raise UserError(
                    "Partner %s has no valid agreed commission rate (%s)" % (partner.name, rate)
                )
            scheme = Scheme._find(
                "partner", today, ref.company_id, partner_type=partner.partner_type
            )
            if not scheme:
                raise UserError(
                    "No partner commission scheme is in force on %s for %s partners — "
                    "configure M53 Commission Schemes (TDS rate) first"
                    % (today, partner.partner_type)
                )
            if existing:
                existing.sudo()._guarded().write(
                    {
                        "scheme_id": scheme.id,
                        "gross_amount": ref.base_amount,
                        "commission_rate": rate,
                        "rail": "BEFTN",
                    }
                )
                ledger = existing.with_env(self.env)
            else:
                ledger = Ledger._guarded().create(
                    {
                        "company_id": ref.company_id.id,
                        "operating_unit_id": ref.operating_unit_id.id,
                        "source_type": "partner_referral",
                        "seller_partner_id": partner.partner_id.id,
                        "source_ref": ref.name,
                        "referral_id": ref.id,
                        "scheme_id": scheme.id,
                        "gross_amount": ref.base_amount,
                        "commission_rate": rate,
                        "rail": "BEFTN",
                    }
                )
            ref.sudo()._guarded().write({"commission_ledger_id": ledger.id})
            ledger.with_env(self.env).action_post_to_gl()


class FixCommissionLedgerReferralRate(models.Model):
    """A04 ERP audit M40-F6: a partner referral row carries the rate its
    referral was earned at. The ledger's scheme step replaced it with the
    scheme's rate (fix_settlement_ext._fix_scheme_rate / _fix_ensure_scheme),
    so the GL accrued a different commission from the one the partner was
    told it earned. For referral rows the scheme now supplies the TDS only."""

    _inherit = "fix.commission.ledger"

    @api.model
    def _fix_scheme_rate(self, vals):
        if vals.get("source_type") == "partner_referral" and vals.get("referral_id"):
            rate = self.env["fix.referral"].sudo().browse(vals["referral_id"]).commission_rate
            if rate:
                vals["commission_rate"] = rate
                return vals
        return super()._fix_scheme_rate(vals)

    def _fix_ensure_scheme(self):
        earned = {
            rec.id: rec.referral_id.commission_rate
            for rec in self
            if rec.source_type == "partner_referral" and rec.referral_id.commission_rate
        }
        result = super()._fix_ensure_scheme()
        for rec in self.filtered(lambda r: r.id in earned):
            if abs(rec.commission_rate - earned[rec.id]) > 1e-9:
                rec._guarded().write({"commission_rate": earned[rec.id]})
        return result


class FixPartnerPayoutConsumers(models.AbstractModel):
    """A04 ERP audit M40-F3/F13: an approved rebate or MDF claim is ACCRUED
    (Dr expense / Cr partner payable / Cr TDS withheld) and its NET is raised
    as a pending M50 instruction that clears the partner payable. The rebate
    hand-off raised the instruction with no debit account, no accrual and no
    TDS; an MDF claim was "paid" by a typed reference. Every account is
    configured (cd_settlement_ext.account_code.<role>) - unset, the hand-off
    is refused and dead-letters visibly (and the approval itself refuses)."""

    _inherit = "fix.a04.finance.consumers"

    def _partner_tds(self, partner, company, amount):
        """The partner scheme's TDS on the payout, uplifted for a non-filer."""
        scheme = self.env["fix.commission.scheme"]._find(
            "partner",
            fields.Date.context_today(self),
            company,
            partner_type=partner.partner_type,
        )
        if not scheme:
            raise UserError(
                "No partner commission scheme is in force for %s partners in %s: its TDS rate "
                "decides the withholding - configure M53 Commission Schemes first."
                % (partner.partner_type, company.name)
            )
        tds = scheme.tds_on(amount, amount)
        filer = False
        if "fix.vendor.tax.profile" in self.env:
            profile = self.env["fix.vendor.tax.profile"].for_partner(partner.partner_id, company)
            filer = bool(profile and profile.is_filer_on(fields.Date.context_today(self)))
        if tds and not filer:
            uplift = float_param(self.env, PARAM_NON_FILER_UPLIFT, DEFAULT_NON_FILER_UPLIFT)
            tds = round(tds * (1.0 + uplift), 2)
        return round(tds, 2), scheme

    def _partner_payout(self, source, partner, amount, expense_role, label):
        Execution = self.env["fix.payment.execution"].sudo()
        existing = Execution.search(
            [("source_model", "=", source._name), ("source_id", "=", source.id)], limit=1
        )
        if existing:
            return {"model": existing._name, "id": existing.id, "created": False}
        company = partner.company_id
        party = partner.partner_id
        expense = payout_account(self.env, company, expense_role)
        payable = payout_account(self.env, company, "partner_payable")
        tds_account = payout_account(self.env, company, "tds_payable")
        tds, scheme = self._partner_tds(partner, company, amount)
        net = round(amount - tds, 2)
        if net <= 0.005:
            raise UserError("%s refused: nothing is left to pay after TDS." % label)
        ou = self.env["fix.finance.handback"]._handback_ou(company, partner.operating_unit_id)
        dims = {"operating_unit_id": ou.id, "cost_centre": "CC-PAY"}
        lines = [
            (
                0,
                0,
                {
                    "account_id": expense.id,
                    "name": "%s: %s" % (label, source.display_name),
                    "debit": amount,
                    "credit": 0.0,
                },
            ),
            (
                0,
                0,
                {
                    "account_id": payable.id,
                    "name": "%s payable: %s" % (label, source.display_name),
                    "partner_id": party.id,
                    "debit": 0.0,
                    "credit": net,
                },
            ),
        ]
        if tds > 0.005:
            lines.append(
                (
                    0,
                    0,
                    {
                        "account_id": tds_account.id,
                        "name": "TDS withheld (%s, %.2f%%): %s"
                        % (
                            scheme.tds_reference or scheme.name,
                            scheme.tds_rate * 100,
                            source.display_name,
                        ),
                        "partner_id": party.id,
                        "debit": 0.0,
                        "credit": tds,
                    },
                )
            )
        move, _dims = post_with_dimensions(
            self.env,
            {
                "journal_id": _configured_journal(self.env, company).id,
                "company_id": company.id,
                "date": fields.Date.context_today(self),
                "ref": "%s %s" % (label, source.display_name),
                "line_ids": lines,
            },
            dict.fromkeys(range(len(lines)), dims),
            source="settlement",
        )
        pay = Execution.create(
            {
                "company_id": company.id,
                "operating_unit_id": ou.id,
                "payee": party.name,
                "partner_id": party.id,
                "amount": net,
                "method": "bank_transfer",
                "source_model": source._name,
                "source_id": source.id,
                "debit_account_id": payable.id,
            }
        )
        pay.message_post(
            body="Raised by the %s hand-off of %s: BDT %.2f accrued (%s), TDS %.2f withheld, "
            "net %.2f payable to %s. Nothing is paid until treasury releases it and the bank "
            "confirms it." % (label, source.display_name, amount, move.name, tds, net, party.name)
        )
        self.env["fix.finance.handback"]._handback_note(
            source,
            "Finance hand-back (%s):" % label,
            "accrued in %s (BDT %.2f, TDS %.2f); pending treasury payout %s of BDT %.2f."
            % (move.name, amount, tds, pay.name, net),
        )
        return {"model": pay._name, "id": pay.id, "created": True, "move_id": move.id}

    @api.model
    def consume_partner_rebate_approved(self, event: dict) -> dict:
        """partner.rebate_approved -> accrual + a PENDING M50 payout of the net."""
        self._a04_assert_relay()
        label = "Rebate hand-off"
        rebate, payload = self._a04_source(event, "fix.partner.rebate", label)
        if rebate.state != "approved":
            raise UserError(
                "%s refused: rebate %s is %s, not approved." % (label, rebate.name, rebate.state)
            )
        amount = rebate.amount or 0.0
        self.env["fix.finance.handback"]._handback_check_amount(label, payload, "amount", amount)
        if amount <= 0.005:
            raise UserError("%s refused: rebate %s has no amount." % (label, rebate.name))
        partner = rebate.partner_id
        if not partner or not partner.partner_id:
            raise UserError(
                "%s refused: rebate %s has no channel partner to pay." % (label, rebate.name)
            )
        role = "partner_mdf_expense" if rebate.kind == "mdf" else "partner_rebate_payout"
        return self._partner_payout(rebate, partner, amount, role, "Partner rebate")

    @api.model
    def consume_partner_mdf_claim_approved(self, event: dict) -> dict:
        """partner.mdf_claim_approved -> accrual + a PENDING M50 payout of the net."""
        self._a04_assert_relay()
        label = "MDF hand-off"
        claim, payload = self._a04_source(event, "fix.mdf.claim", label)
        if claim.state != "approved":
            raise UserError(
                "%s refused: claim %s is %s, not approved." % (label, claim.name, claim.state)
            )
        amount = claim.amount or 0.0
        self.env["fix.finance.handback"]._handback_check_amount(label, payload, "amount", amount)
        if amount <= 0.005:
            raise UserError("%s refused: claim %s has no amount." % (label, claim.name))
        partner = claim.fund_id.partner_id
        return self._partner_payout(claim, partner, amount, "partner_mdf_expense", "Partner MDF")


# ---------------------------------------------------------------------------
# Escrow & clawbacks
# ---------------------------------------------------------------------------
class FixSettlementAdjustment(models.Model):
    """Escrow: commissions of a seller frozen while a marketplace dispute is
    open (never collected into a payout). Clawback: an amount owed BACK by a
    seller/partner, recovered from their future payouts."""

    _name = "fix.settlement.adjustment"
    _description = "Settlement Escrow / Clawback"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "id desc"

    ADJ_LOCKED = ("adjustment_type", "seller_partner_id", "commission_ids", "amount", "company_id")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "requested_by_id",
            "decided_by_id",
            "decided_at",
            "move_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "draft" for r in self):
            locked |= set(self.ADJ_LOCKED)
        return locked

    def write(self, vals):
        if not self._fix_guard_open():
            touched = set(self.ADJ_LOCKED) & set(vals)
            if touched and self.filtered(lambda r: r.state != "draft"):
                raise UserError(
                    "An active escrow / clawback is fixed; cancel it and raise a new one."
                )
        return super().write(vals)

    name = fields.Char(string="Reference", default="New", readonly=True, copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    adjustment_type = fields.Selection(
        [
            ("escrow", "Escrow Hold (open dispute)"),
            ("clawback", "Clawback (recover from future payouts)"),
        ],
        string="Type",
        required=True,
        default="escrow",
        tracking=True,
    )
    seller_partner_id = fields.Many2one(
        "res.partner", string="Seller / Partner", required=True, index=True, tracking=True
    )
    dispute_id = fields.Many2one(
        "fix.marketplace.dispute", string="Marketplace Dispute", index=True, tracking=True
    )
    commission_ids = fields.Many2many(
        "fix.commission.ledger",
        "fix_settlement_adjustment_commission_rel",
        "adjustment_id",
        "commission_id",
        string="Commissions Held",
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount = fields.Monetary(currency_field="currency_id", tracking=True)
    recovery_ids = fields.One2many("fix.settlement.recovery", "adjustment_id", string="Recoveries")
    recovered_amount = fields.Monetary(
        currency_field="currency_id", compute="_compute_recovered", store=True
    )
    remaining_amount = fields.Monetary(
        currency_field="currency_id", compute="_compute_recovered", store=True
    )
    reason = fields.Text(required=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Held / Open"),
            ("released", "Released to Payee"),
            ("forfeited", "Forfeited (refunded)"),
            ("recovered", "Recovered"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
        index=True,
    )
    requested_by_id = fields.Many2one(
        "res.users", string="Requested By", default=lambda self: self.env.user, readonly=True
    )
    decided_by_id = fields.Many2one("res.users", string="Decided By", readonly=True, copy=False)
    decided_at = fields.Datetime(string="Decided On", readonly=True, copy=False)
    move_id = fields.Many2one("account.move", string="GL Move", readonly=True, copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.settlement.adjustment") or "ADJ/New"
                )
        return super().create(vals_list)

    @api.depends("amount", "recovery_ids.amount")
    def _compute_recovered(self):
        for rec in self:
            rec.recovered_amount = sum(rec.recovery_ids.mapped("amount"))
            rec.remaining_amount = max(rec.amount - rec.recovered_amount, 0.0)

    @api.onchange("dispute_id")
    def _onchange_dispute(self):
        if self.dispute_id and self.dispute_id.seller_id.partner_id:
            self.seller_partner_id = self.dispute_id.seller_id.partner_id

    def _stamp(self, state):
        self._guarded().write(
            {"state": state, "decided_by_id": self.env.user.id, "decided_at": fields.Datetime.now()}
        )

    def action_activate(self):
        """Escrow: freeze the listed (unpaid) commissions. Clawback: open the
        claim — a finance manager other than the requester approves it, as it
        reduces what a payee is paid."""
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft adjustment can be activated")
            if rec.adjustment_type == "escrow":
                rows = rec.commission_ids
                if not rows:
                    raise UserError("List the commissions to hold in escrow")
                if rows.filtered(lambda c, r=rec: c.seller_partner_id != r.seller_partner_id):
                    raise UserError(
                        "Every held commission must belong to %s" % rec.seller_partner_id.name
                    )
                if rows.filtered(lambda c: c.state not in ("earned", "accrued")):
                    raise UserError("Only unpaid (earned / accrued) commissions can be held")
                in_flight = self.env["fix.payout.run"].search(
                    [("commission_ids", "in", rows.ids), ("state", "!=", "draft")]
                )
                if in_flight:
                    raise UserError(
                        "Commissions are already in approved payout run(s) %s"
                        % ", ".join(in_flight.mapped("name"))
                    )
                rows.sudo()._guarded().write({"escrow_hold": True})
                rec._guarded().write({"amount": sum(rows.mapped("net_payable"))})
                rec._stamp("active")
            else:
                if rec.amount <= 0:
                    raise UserError("A clawback needs a positive amount")
                if not _is_manager(self.env):
                    raise AccessError("Only a finance manager can approve a clawback")
                if rec.requested_by_id == self.env.user:
                    raise AccessError(
                        "Segregation of duties: the requester cannot approve clawback %s" % rec.name
                    )
                rec._stamp("active")
            payload = {"ref": rec.name, "payee": rec.seller_partner_id.name, "amount": rec.amount}
            # one literal event type per branch, so the event contracts derive
            if rec.adjustment_type == "escrow":
                publish(
                    self.env,
                    "settlement.escrow_opened",
                    "fix.settlement.adjustment",
                    rec.id,
                    payload,
                )
            else:
                publish(
                    self.env,
                    "settlement.clawback_opened",
                    "fix.settlement.adjustment",
                    rec.id,
                    payload,
                )

    # ---- M53-7: a dispute raises its own escrow -------------------------------
    @api.model
    def _fix_escrow_for_dispute(self, dispute):
        """Hold the commissions of the disputed order, once per dispute. Rows
        already in a released payout run cannot be held and are reported on the
        dispute for finance; with nothing unpaid there is nothing to hold."""
        self = self.sudo()
        existing = self.search(
            [
                ("dispute_id", "=", dispute.id),
                ("adjustment_type", "=", "escrow"),
                ("state", "in", ("draft", "active")),
            ],
            limit=1,
        )
        if existing:
            return existing
        order = dispute.order_id
        rows = (
            self.env["fix.commission.ledger"]
            .sudo()
            .search(
                [("marketplace_order_id", "=", order.id), ("state", "in", ("earned", "accrued"))]
            )
        )
        in_flight = (
            self.env["fix.payout.run"]
            .sudo()
            .search([("commission_ids", "in", rows.ids), ("state", "!=", "draft")])
        )
        free = rows - in_flight.mapped("commission_ids")
        if not free:
            if rows:
                dispute.message_post(
                    body="Escrow not raised: the order's commissions are already in payout run(s) "
                    "%s. Finance decides." % ", ".join(in_flight.mapped("name"))
                )
            return self.browse()
        seller = free[:1].seller_partner_id
        adjustment = self.create(
            {
                "company_id": order.company_id.id,
                "operating_unit_id": order.operating_unit_id.id or False,
                "adjustment_type": "escrow",
                "seller_partner_id": seller.id,
                "dispute_id": dispute.id,
                "commission_ids": [
                    (6, 0, free.filtered(lambda c, s=seller: c.seller_partner_id == s).ids)
                ],
                "reason": "Automatic hold: dispute %s was raised on order %s."
                % (dispute.name, order.name),
            }
        )
        adjustment.action_activate()
        return adjustment

    @api.model
    def consume_dispute_raised(self, event: dict) -> dict:
        """R8 consumer of marketplace.dispute_raised: the disputed amount stops
        at once, without anyone having to remember to raise the escrow. The
        payload is a claim: the dispute is re-read and must still be open."""
        if not self.env.su:
            raise AccessError("The escrow consumer runs only from the event relay.")
        try:
            dispute_id = int(event.get("aggregate_id") or 0)
        except (TypeError, ValueError):
            dispute_id = 0
        dispute = self.env["fix.marketplace.dispute"].sudo().browse(dispute_id).exists()
        if not dispute:
            raise UserError("Escrow refused: there is no marketplace dispute #%s." % dispute_id)
        if dispute.state not in OPEN_DISPUTE_STATES:
            return {"skipped": "dispute %s is %s" % (dispute.name, dispute.state)}
        adjustment = self._fix_escrow_for_dispute(dispute)
        return {"model": self._name, "id": adjustment.id or False, "created": bool(adjustment)}

    def action_release(self):
        """Release an escrow back into payouts once its dispute is resolved
        (a second person decides: segregation of duties)."""
        for rec in self:
            if rec.adjustment_type != "escrow" or rec.state != "active":
                raise UserError("Only an active escrow can be released")
            if rec.dispute_id and rec.dispute_id.state in OPEN_DISPUTE_STATES:
                raise UserError(
                    "Dispute %s is still open — the escrow stays until it is resolved"
                    % rec.dispute_id.name
                )
            if rec.requested_by_id == self.env.user:
                raise AccessError(
                    "Segregation of duties: the requester cannot release escrow %s" % rec.name
                )
            rec.commission_ids.sudo()._guarded().write({"escrow_hold": False})
            rec._stamp("released")

    def action_forfeit(self):
        """The dispute was ruled for the customer: the held commissions are
        never paid. The seller liability they carried is moved to the
        customer-refund clearing account (Dr seller payable / Cr refund
        clearing). Finance manager, not the requester."""
        for rec in self:
            if rec.adjustment_type != "escrow" or rec.state != "active":
                raise UserError("Only an active escrow can be forfeited")
            if not _is_manager(self.env):
                raise AccessError("Only a finance manager can forfeit an escrow")
            if rec.requested_by_id == self.env.user:
                raise AccessError(
                    "Segregation of duties: the requester cannot forfeit escrow %s" % rec.name
                )
            move = False
            posted = rec.commission_ids.filtered(lambda c: c.state == "accrued")
            liability = sum(c.net_payable + (c.tds_amount or 0.0) for c in posted)
            if liability > 0.005:
                company = rec.company_id
                role = posted[:1]._payable_role()
                move = _post_settlement_move(
                    self.env,
                    company,
                    fields.Date.context_today(rec),
                    "ESCROW-FORFEIT-%s" % rec.name,
                    [
                        (
                            _configured_account(self.env, company, role),
                            "Forfeited payee liability %s" % rec.name,
                            liability,
                            0.0,
                            rec.seller_partner_id.id,
                        ),
                        (
                            _configured_account(self.env, company, "clawback_recovery"),
                            "Customer refund clearing %s" % rec.name,
                            0.0,
                            liability,
                            False,
                        ),
                    ],
                )
            rec.commission_ids.sudo()._guarded().write({"state": "forfeited", "escrow_hold": False})
            rec._guarded().write({"move_id": move.id if move else False})
            rec._stamp("forfeited")

    def action_cancel(self):
        for rec in self:
            if rec.state == "draft":
                rec._guarded().write({"state": "cancelled"})
                continue
            if rec.adjustment_type == "clawback" and rec.state == "active" and not rec.recovery_ids:
                if not _is_manager(self.env):
                    raise AccessError("Only a finance manager can cancel an open clawback")
                rec._stamp("cancelled")
                continue
            raise UserError("%s cannot be cancelled in state %s" % (rec.name, rec.state))


class FixSettlementRecovery(models.Model):
    """The part of a clawback a payout run deducted."""

    _name = "fix.settlement.recovery"
    _description = "Clawback Recovery"
    _order = "id desc"

    adjustment_id = fields.Many2one(
        "fix.settlement.adjustment", required=True, ondelete="restrict", index=True
    )
    payout_run_id = fields.Many2one(
        "fix.payout.run", required=True, ondelete="restrict", index=True
    )
    company_id = fields.Many2one(related="adjustment_id.company_id", store=True, index=True)
    currency_id = fields.Many2one(related="adjustment_id.currency_id")
    amount = fields.Monetary(currency_field="currency_id", required=True)


# ---------------------------------------------------------------------------
# IAS 37 workmanship warranty provision
# ---------------------------------------------------------------------------
class FixWarrantyProvisionPolicy(models.Model):
    """The estimate behind the workmanship-warranty provision: the warranty
    period the company gives on repairs, the claim-history window and the
    average cost of a rework as a share of the original repair revenue.
    Effective-dated master data, set by finance — nothing is seeded."""

    _name = "fix.warranty.provision.policy"
    _description = "Warranty Provision Policy (IAS 37)"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_from desc, id desc"

    name = fields.Char(required=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    active = fields.Boolean(default=True)
    warranty_days = fields.Integer(
        string="Workmanship Warranty (days)", required=True, tracking=True
    )
    lookback_months = fields.Integer(
        string="Claim History Window (months)", required=True, default=12, tracking=True
    )
    cost_ratio = fields.Float(
        string="Rework Cost Ratio",
        digits=(5, 4),
        required=True,
        tracking=True,
        help="Average cost of one rework as a fraction of the original repair revenue (0-1)",
    )
    date_from = fields.Date(string="Effective From", required=True)
    date_to = fields.Date(string="Effective To")
    note = fields.Text(string="Basis of Estimate")

    @api.constrains("warranty_days", "lookback_months", "cost_ratio", "date_from", "date_to")
    def _check_policy(self):
        for policy in self:
            if policy.warranty_days <= 0 or policy.lookback_months <= 0:
                raise ValidationError("Warranty days and the history window must be positive")
            if not 0 <= policy.cost_ratio <= 1:
                raise ValidationError("The rework cost ratio is a fraction between 0 and 1")
            if policy.date_to and policy.date_to < policy.date_from:
                raise ValidationError("A policy cannot end before it starts")

    @api.model
    def _find(self, company, on_date):
        return self.search(
            [
                ("company_id", "=", company.id),
                ("date_from", "<=", on_date),
                "|",
                ("date_to", "=", False),
                ("date_to", ">=", on_date),
            ],
            limit=1,
        )


class FixWarrantyProvision(models.Model):
    """The period-end workmanship-warranty provision (IAS 37, assurance-type
    warranty): required balance = repair revenue still inside the warranty
    window x historical rework rate x rework cost ratio. The movement against
    the last posted balance is booked (increase: Dr warranty expense / Cr
    provision; release on expiry: the reverse)."""

    _name = "fix.warranty.provision"
    _description = "Warranty Provision (IAS 37)"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "period desc, id desc"

    PROVISION_FIGURES = (
        "policy_id",
        "revenue_in_warranty",
        "lookback_orders",
        "lookback_reworks",
        "rework_rate",
        "cost_ratio",
        "required_balance",
        "opening_balance",
        "movement",
    )

    def _fix_guarded_fields(self) -> set:
        # A08 M53-11: the figures are measured, the stamps are evidence
        return (
            super()._fix_guarded_fields()
            | set(self.PROVISION_FIGURES)
            | {
                "state",
                "move_id",
                "computed_by_id",
                "computed_at",
                "posted_by_id",
                "note",
            }
        )

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "draft" for r in self):
            locked |= {"period", "company_id"}
        return locked

    def write(self, vals):
        if not self._fix_guard_open() and {"period", "company_id"} & set(vals):  # noqa: SIM102
            if self.filtered(lambda r: r.state != "draft"):
                raise UserError("A computed provision keeps its period; open a new one.")
        return super().write(vals)

    _period_unique = models.Constraint(
        "UNIQUE (company_id, period)", "One warranty provision per company per period"
    )

    name = fields.Char(compute="_compute_name", store=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    currency_id = fields.Many2one(related="company_id.currency_id")
    period = fields.Char(string="Period (YYYY-MM)", required=True, index=True)
    period_end = fields.Date(compute="_compute_period_end", store=True)
    policy_id = fields.Many2one("fix.warranty.provision.policy", string="Policy", readonly=True)
    revenue_in_warranty = fields.Monetary(
        string="Repair Revenue in Warranty", currency_field="currency_id", readonly=True
    )
    lookback_orders = fields.Integer(string="Invoiced Repairs (history)", readonly=True)
    lookback_reworks = fields.Integer(string="Reworks (history)", readonly=True)
    rework_rate = fields.Float(string="Rework Rate", digits=(5, 4), readonly=True)
    cost_ratio = fields.Float(string="Rework Cost Ratio", digits=(5, 4), readonly=True)
    required_balance = fields.Monetary(
        string="Required Provision", currency_field="currency_id", readonly=True
    )
    opening_balance = fields.Monetary(
        string="Last Posted Provision", currency_field="currency_id", readonly=True
    )
    movement = fields.Monetary(string="Movement", currency_field="currency_id", readonly=True)
    move_id = fields.Many2one("account.move", string="GL Move", readonly=True, copy=False)
    computed_by_id = fields.Many2one("res.users", string="Computed By", readonly=True)
    computed_at = fields.Datetime(string="Computed On", readonly=True)
    posted_by_id = fields.Many2one("res.users", string="Posted By", readonly=True)
    note = fields.Text(readonly=True)
    state = fields.Selection(
        [("draft", "Draft"), ("computed", "Computed"), ("posted", "Posted")],
        default="draft",
        required=True,
        tracking=True,
    )

    @api.depends("period")
    def _compute_name(self):
        for rec in self:
            rec.name = "WP/%s" % (rec.period or "")

    @api.depends("period")
    def _compute_period_end(self):
        for rec in self:
            if rec.period and PERIOD_RE.match(rec.period):
                y, m = (int(x) for x in rec.period.split("-"))
                rec.period_end = date(y, m, 1) + relativedelta(months=1) - timedelta(days=1)
            else:
                rec.period_end = False

    @api.constrains("period")
    def _check_period(self):
        for rec in self:
            if not PERIOD_RE.match(rec.period or ""):
                raise ValidationError("The period must be written YYYY-MM (e.g. 2026-10)")

    def _fix_measure(self):
        """The provision figures measured from posted data (no side effect)."""
        self.ensure_one()
        Invoice = self.env["fix.ar.invoice"].sudo()
        Order = self.env["fix.service.order"].sudo()
        rec = self
        end = rec.period_end
        policy = self.env["fix.warranty.provision.policy"]._find(rec.company_id, end)
        if not policy:
            raise UserError(
                "No warranty provision policy is in force on %s — set the warranty "
                "period and rework cost ratio first" % end
            )
        repair = [
            ("company_id", "=", rec.company_id.id),
            ("source_model", "=", "fix.service.order"),
            ("state", "in", ("issued", "paid", "credited")),
        ]
        in_warranty = Invoice.search(
            [
                *repair,
                ("invoice_date", ">", end - timedelta(days=policy.warranty_days)),
                ("invoice_date", "<=", end),
            ]
        )
        window_start = end - relativedelta(months=policy.lookback_months)
        history = Invoice.search_count(
            [*repair, ("invoice_date", ">", window_start), ("invoice_date", "<=", end)]
        )
        reworks = Order.search_count(
            [
                ("company_id", "=", rec.company_id.id),
                ("is_rework", "=", True),
                ("create_date", ">", fields.Datetime.to_datetime(window_start)),
                ("create_date", "<", fields.Datetime.to_datetime(end + timedelta(days=1))),
            ]
        )
        rate = min(reworks / history, 1.0) if history else 0.0
        revenue = sum(in_warranty.mapped("taxable_amount"))
        required = round(revenue * rate * policy.cost_ratio, 2)
        last = self.search(
            [
                ("company_id", "=", rec.company_id.id),
                ("state", "=", "posted"),
                ("period", "<", rec.period),
            ],
            order="period desc",
            limit=1,
        )
        opening = last.required_balance if last else 0.0
        notes = []
        if not history:
            notes.append("No invoiced repairs in the history window: rework rate 0.")
        return {
            "policy_id": policy.id,
            "revenue_in_warranty": revenue,
            "lookback_orders": history,
            "lookback_reworks": reworks,
            "rework_rate": rate,
            "cost_ratio": policy.cost_ratio,
            "required_balance": required,
            "opening_balance": opening,
            "movement": round(required - opening, 2),
            "note": " ".join(notes) or False,
        }

    def action_compute(self):
        """Measure the provision from posted data: AR repair invoices and
        the rework orders flagged by M01 (BRU-SRM-06)."""
        require_role(self.env, GROUP_ACCOUNTANT, "Computing the warranty provision")
        for rec in self:
            if rec.state == "posted":
                raise UserError("Provision %s is posted" % rec.name)
            vals = rec._fix_measure()
            vals.update(
                {
                    "computed_by_id": self.env.user.id,
                    "computed_at": fields.Datetime.now(),
                    "state": "computed",
                }
            )
            rec._guarded().write(vals)

    def action_post(self):
        """Book the movement (finance manager, not the person who computed)."""
        for rec in self:
            if rec.state != "computed":
                raise UserError("Compute provision %s before posting it" % rec.name)
            if not _is_manager(self.env):
                raise AccessError("Only a finance manager can post the warranty provision")
            if self.env.user in (rec.computed_by_id | rec.create_uid) and not self.env.su:
                raise AccessError(
                    "Segregation of duties: %s computed %s and cannot post it"
                    % (self.env.user.name, rec.name)
                )
            # what posts is what the data says now, never a figure carried
            # over from a write
            measured = rec._fix_measure()
            if (
                abs(measured["movement"] - rec.movement) > 0.005
                or abs(measured["required_balance"] - rec.required_balance) > 0.005
            ):
                raise UserError(
                    "Provision %s no longer matches its data (movement %.2f now %.2f): compute "
                    "it again before posting." % (rec.name, rec.movement, measured["movement"])
                )
            later = self.search(
                [
                    ("company_id", "=", rec.company_id.id),
                    ("state", "=", "posted"),
                    ("period", ">", rec.period),
                ],
                limit=1,
            )
            if later:
                raise UserError(
                    "A later period (%s) is already posted — post periods in order" % later.period
                )
            move = False
            amount = abs(rec.movement)
            if amount > 0.005:
                company = rec.company_id
                expense = _configured_account(self.env, company, "warranty_expense")
                provision = _configured_account(self.env, company, "warranty_provision")
                if rec.movement > 0:
                    lines = [
                        (expense, "Warranty provision charge %s" % rec.period, amount, 0.0, False),
                        (provision, "Warranty provision %s" % rec.period, 0.0, amount, False),
                    ]
                else:
                    lines = [
                        (
                            provision,
                            "Warranty provision release %s" % rec.period,
                            amount,
                            0.0,
                            False,
                        ),
                        (expense, "Warranty provision release %s" % rec.period, 0.0, amount, False),
                    ]
                move = _post_settlement_move(
                    self.env, company, rec.period_end, "WARRANTY-PROV-%s" % rec.period, lines
                )
            rec._guarded().write(
                {
                    "state": "posted",
                    "move_id": move.id if move else False,
                    "posted_by_id": self.env.user.id,
                }
            )
