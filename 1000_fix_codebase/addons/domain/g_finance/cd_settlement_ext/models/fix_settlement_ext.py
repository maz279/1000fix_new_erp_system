# fix_settlement_ext — M53 W7: commission ledger + payout runs (P10-M02 / R08-M02).
#
# A08 remediation (B4, 4 Nov 2026), M53-1/-2/-3/-4/-5/-7/-12/-15, F2:
#   * a commission row comes from a referral or a marketplace order, never
#     typed; its rate is the scheme's in force (BRU-REV-10), its TDS is
#     measured from the scheme and the payee's evidenced PSR (the M52 tax
#     profile), and both are locked at accrual with the gross, rate, payee
#     and escrow flag (LP-07); state, GL link and escrow flag are guarded;
#   * a payout run is PREPARED (frozen), APPROVED from the M63 inbox by an
#     Accounting Administrator who did not prepare it (DOFA Tier 4 above the
#     CFO band), and the approval PINS the payee lines: payee, bank account
#     (number snapshot), amount. Approval happens only from "prepared", so an
#     executed run is never approved — or paid — again (BRU-REV-18);
#   * money moves only as M50 payment instructions (fix.payment.execution,
#     B1's _fix_request_payment), one per pinned payee line, each released by
#     treasury (two-person) and confirmed by an imported bank statement debit
#     (FR-REV-034/036); every payee account passes B2's
#     _fix_assert_payable_bank first. M53's own rail / BEFTN file is retired:
#     it paid without treasury and was "confirmed" by a typed reference;
#   * the run completes when every instruction is bank-confirmed; only then
#     are statements issued and the payable discharged in the GL.
from __future__ import annotations

from datetime import datetime, time, timedelta

import pytz
from odoo import api, fields, models
from odoo.addons.cd_billing_engine.models.fix_finance_approval import (
    GROUP_ACCOUNTANT,
    GROUP_ADMINISTRATOR,
    float_param,
    require_role,
)
from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions
from odoo.exceptions import AccessError, UserError

from libs.py.fix_events import publish

# Settlement GL accounts by role: (default code, label). The code is looked up
# in the company's chart; a database may override it with the system
# parameter ``cd_settlement_ext.account_code.<role>``.
# NOTE: 210100 is also the VAT Output Payable code cd_tax_engine_bd reconciles
# against; a chart that keeps TDS separate must override ``tds_payable``.
SETTLEMENT_ACCOUNTS = {
    "clearing": ("101000", "Customer Payment Clearing / Disbursement Bank"),
    "commission_revenue": ("400100", "Marketplace Commission Revenue"),
    "seller_payable": ("200200", "Marketplace Seller Payable"),
    "tds_payable": ("210100", "TDS Withheld Liability (ITA 2023 s.140)"),
    # A08 M53 roles with NO default code: the chart has no semantically
    # certain account for them, so the system parameter must name one.
    "partner_commission_expense": (None, "Partner / Referral Commission Expense"),
    "partner_payable": (None, "Partner Commission Payable"),
    "clawback_recovery": (None, "Customer Refund Clearing (clawbacks / forfeited escrow)"),
    "warranty_expense": (None, "Workmanship Warranty Expense (IAS 37)"),
    "warranty_provision": (None, "Workmanship Warranty Provision (IAS 37)"),
}

# The payout approval ladder (spec 05-04 §7 "Marketplace seller payout —
# Finance Manager"; M53 §8 "Finance Manager / CFO"): every payout is approved
# by the Accounting Administrator; above the CFO band by DOFA Tier 4. The CFO
# band default is the only CFO band 05-04 §7 states (BDT 2,000,000); the M30
# DOFA ladder overrides it when ruled.
PARAM_PAYOUT_CFO = "cd_settlement_ext.payout_cfo_limit"
DEFAULT_PAYOUT_CFO = 2000000.0
# ITA 2023 s.264/265 non-filer uplift on TDS (the engine's existing 50%).
PARAM_NON_FILER_UPLIFT = "cd_settlement_ext.tds_non_filer_uplift"
DEFAULT_NON_FILER_UPLIFT = 0.5
# Optional: the bank journal (code) treasury pays payouts from.
PARAM_PAYOUT_JOURNAL = "cd_settlement_ext.payout_journal_code"

LEDGER_GUARDED = {
    "state",
    "gl_move_id",
    "escrow_hold",
    "tds_amount",
    "psr_verified",
    "psr_slip_number",
    "commission_rate",
    "referral_id",
    "marketplace_order_id",
    "void_reason",
    "voided_by_id",
    "voided_at",
}
# LP-07: what an accrued row never changes (reversible only by contra-posting).
LEDGER_LOCKED = (
    "gross_amount",
    "commission_rate",
    "commission_amount",
    "seller_partner_id",
    "tds_amount",
    "psr_verified",
    "psr_slip_number",
    "scheme_id",
    "source_type",
    "company_id",
    "currency_id",
)


def _configured_account(env, company, role):
    """The company's configured GL account for a settlement role.

    Never guessed, never created: the former helper fell back to ANY account
    of the same type (posting commission revenue to whichever income account
    came first) or created accounts on the fly. A missing account refuses the
    posting with the code that must be configured.

    Odoo 19: account.account is shared across companies (company_ids) and its
    code is company-dependent."""
    default_code, label = SETTLEMENT_ACCOUNTS[role]
    code = (
        env["ir.config_parameter"].sudo().get_param(f"cd_settlement_ext.account_code.{role}")
        or default_code
    )
    if not code:
        raise UserError(
            "Settlement posting refused: no GL account is configured for %s in company %s. "
            "Set system parameter cd_settlement_ext.account_code.%s to the account code to use."
            % (label, company.name, role)
        )
    accounts = env["account.account"].with_company(company)
    acc = accounts.search([("code", "=", code), ("company_ids", "in", company.id)], limit=1)
    if not acc:
        raise UserError(
            "Settlement posting refused: no GL account %s (%s) in company %s. Configure it in "
            "the chart of accounts, or set system parameter "
            "cd_settlement_ext.account_code.%s to the account code to use."
            % (code, label, company.name, role)
        )
    return acc


def _configured_journal(env, company):
    """The company's general journal for settlement postings — refused, not
    created, when the company has none."""
    journal = env["account.journal"].search(
        [("type", "=", "general"), ("company_id", "=", company.id)], limit=1
    )
    if not journal:
        raise UserError(
            "Settlement posting refused: company %s has no general (miscellaneous) journal."
            % company.name
        )
    return journal


def _routing_of(bank) -> str:
    if not bank:
        return ""
    routing = bank["fix_routing_number"] if "fix_routing_number" in bank._fields else ""
    return (routing or bank.bank_id.bic or "").strip()


def _bank_details(partner) -> tuple[str, str]:
    """(account number, routing number) of the partner's first bank account,
    exactly as recorded — empty strings when absent, never a default."""
    bank = partner.bank_ids[:1]
    return (bank.acc_number or "").strip(), _routing_of(bank)


def _is_routing(routing: str) -> bool:
    """A Bangladesh BEFTN routing number: exactly 9 ASCII digits."""
    return len(routing) == 9 and routing.isascii() and routing.isdigit()


class FixCommissionLedger(models.Model):
    """M53 W7: commission ledger consuming commission.earned events.
    The M12<->M53 break: M53 CONSUMES events; M12 never calls M53.
    Enforces FF-91: Marketplace gross is NEVER posted to revenue!"""

    _name = "fix.commission.ledger"
    _description = "Commission Ledger Entry"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "create_date desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    branch_id = fields.Many2one("fix.branch", string="Branch")
    name = fields.Char(required=True, copy=False, readonly=True, default="New")
    seller_partner_id = fields.Many2one(
        "res.partner", string="Seller (Party)", required=True, index=True
    )
    source_ref = fields.Char(string="Source Reference")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    gross_amount = fields.Monetary(
        string="Gross Marketplace GMV", currency_field="currency_id", required=True
    )
    commission_rate = fields.Float(string="Commission Rate", default=0.10)
    commission_amount = fields.Monetary(
        string="Commission Earned (Revenue)",
        currency_field="currency_id",
        compute="_compute_commission",
        store=True,
    )
    tds_amount = fields.Monetary(
        string="TDS Withheld (ITA 2023 s.140)",
        currency_field="currency_id",
        readonly=True,
        help="Measured from the commission scheme and the payee's evidenced return-filing "
        "proof (PSR); locked at accrual.",
    )
    psr_verified = fields.Boolean(
        string="Proof of Submission of Return (PSR) Verified",
        default=False,
        readonly=True,
        tracking=True,
        help="Read from the payee's tax profile (M52 fix.vendor.tax.profile: PSR reference, "
        "validity and evidence), never ticked by hand (ITA 2023 s.264/265).",
    )
    psr_slip_number = fields.Char(
        string="PSR Acknowledgement Slip Number", readonly=True, tracking=True
    )
    net_payable = fields.Monetary(
        string="Net Payable to Seller",
        currency_field="currency_id",
        compute="_compute_net",
        store=True,
    )
    state = fields.Selection(
        [
            ("earned", "Earned"),
            ("accrued", "Accrued / Posted to GL"),
            ("paid", "Disbursed / Paid"),
            ("forfeited", "Forfeited (dispute ruling)"),
            ("void", "Voided (no source document)"),
        ],
        default="earned",
        required=True,
        tracking=True,
    )
    # A08 M53: one ledger for marketplace sellers AND channel partners —
    # both are paid through the same payout runs.
    source_type = fields.Selection(
        [("marketplace", "Marketplace Seller"), ("partner_referral", "Partner / Referral")],
        string="Payee Type",
        default="marketplace",
        required=True,
        index=True,
        tracking=True,
    )
    referral_id = fields.Many2one(
        "fix.referral", string="Referral", index=True, ondelete="restrict", copy=False
    )
    marketplace_order_id = fields.Many2one(
        "fix.marketplace.order",
        string="Marketplace Order",
        index=True,
        ondelete="restrict",
        copy=False,
        help="The commissioned M12 order the row was raised from (A08 M53-4).",
    )
    scheme_id = fields.Many2one("fix.commission.scheme", string="Commission Scheme")
    void_reason = fields.Char(string="Why Voided", readonly=True, copy=False)
    voided_by_id = fields.Many2one("res.users", string="Voided By", readonly=True, copy=False)
    voided_at = fields.Datetime(string="Voided On", readonly=True, copy=False)
    escrow_hold = fields.Boolean(
        string="Held in Escrow",
        readonly=True,
        copy=False,
        tracking=True,
        help="Held by an active escrow (open marketplace dispute): never collected into a payout",
    )

    _referral_unique = models.Constraint(
        "UNIQUE (referral_id)", "A referral earns one commission row"
    )
    _marketplace_order_unique = models.Constraint(
        "UNIQUE (marketplace_order_id)", "A marketplace order earns one commission row"
    )

    # FLAW-12.2: the statutory-style buyer dispute window. `escrow_hold` above
    # is the DISPUTE flag — it only bites once a dispute is actually raised.
    # Before this, a marketplace commission accrued and could be collected into
    # a payout the same day, so a buyer who disputed on day 2 was arguing about
    # money already disbursed (A04 audit, 2026-10-31).
    ESCROW_WINDOW_DAYS = 7

    escrow_release_date = fields.Date(
        string="Escrow Releases On",
        compute="_compute_escrow_release",
        store=True,
        help="Marketplace commissions are collectable only after the buyer "
        "dispute window has elapsed. Partner/referral commissions carry no "
        "buyer window and are released immediately.",
    )
    escrow_window_elapsed = fields.Boolean(
        string="Dispute Window Elapsed",
        compute="_compute_escrow_window_elapsed",
        search="_search_escrow_window_elapsed",
        help="True once the escrow window has passed, so the row may be paid.",
    )

    # Two fields, two computes - deliberately NOT one shared method.
    #
    # They were written as one, and Odoo warned about it: "inconsistent 'store'
    # for computed fields, accessing escrow_window_elapsed may recompute and
    # update escrow_release_date". That is not a style nit. `escrow_release_date`
    # is stored and `escrow_window_elapsed` is not, so merely READING the
    # boolean ran the shared compute and WROTE the date column - and every P03
    # list endpoint (/p03/model/records, /p03/model/form, /p03/model/report) is
    # declared `readonly=True`, where a write raises. Any A04 screen showing a
    # commission-ledger row would have hit it.
    #
    # They also have different natures: the release DATE is a fixed fact of the
    # row (accrual + 7 days), so it stores; whether the window has ELAPSED
    # depends on what day it is now, so it must never be stored - a stored copy
    # would be frozen at its last recompute and silently authorise a payout.
    @api.depends("create_date", "source_type")
    def _compute_escrow_release(self):
        for rec in self:
            if rec.source_type != "marketplace" or not rec.create_date:
                rec.escrow_release_date = False
                continue
            accrued_on = fields.Date.to_date(rec.create_date)
            rec.escrow_release_date = accrued_on + timedelta(days=rec.ESCROW_WINDOW_DAYS)

    @api.depends("create_date", "source_type")
    def _compute_escrow_window_elapsed(self):
        """Whether the buyer dispute window has passed.

        Computed from `create_date` - the accrual fact - and NOT from the
        stored `escrow_release_date`. Depending on the stored column would make
        this read a cached projection that goes stale whenever the accrual
        timestamp is corrected out of band, and a stale "window elapsed" is the
        one error that must not happen here: it authorises a payout whose
        dispute window is still open.

        context_today, not UTC today: Bangladesh is UTC+6, so for the first six
        hours of each local day UTC is still on the previous date - and on the
        1st of a month, in the previous MONTH - so a payout that was in fact due
        read as still held.
        """
        for rec in self:
            if rec.source_type != "marketplace" or not rec.create_date:
                rec.escrow_window_elapsed = True
                continue
            accrued_on = fields.Date.to_date(rec.create_date)
            release_on = accrued_on + timedelta(days=rec.ESCROW_WINDOW_DAYS)
            rec.escrow_window_elapsed = release_on <= fields.Date.context_today(rec)

    def _escrow_cutoff_utc(self):
        """The UTC instant before which an accrual's window has elapsed.

        A row is released once its LOCAL accrual date plus the window is on or
        before the local today, i.e. once
            local_date(create_date) <= context_today - ESCROW_WINDOW_DAYS
        The latest UTC instant satisfying that is local midnight at the end of
        that cutoff date, converted back to UTC. Bangladesh is UTC+6, so the
        two differ by six hours every day and by a calendar month on the 1st.
        """
        cutoff_date = fields.Date.context_today(self) - timedelta(days=self.ESCROW_WINDOW_DAYS)
        tz = pytz.timezone(self.env.user.tz or "UTC")
        local_end = tz.localize(datetime.combine(cutoff_date + timedelta(days=1), time.min))
        return local_end.astimezone(pytz.utc).replace(tzinfo=None)

    def _search_escrow_window_elapsed(self, operator, value):
        """Lets action_collect_accrued filter on the window in one query.

        Derived from `create_date`, the accrual fact - NOT from the stored
        `escrow_release_date`. Both this and `_compute_escrow_window_elapsed`
        now read the same source, so the query and the flag agree by
        construction instead of having to be kept in step.

        They did not used to. The search read the stored projection, which can
        drift if an accrual timestamp is ever corrected out of band, and a
        drifted projection in a DOMAIN selects rows for payment while their
        dispute window is still open. That hazard was patched with a second
        Python guard in `action_collect_accrued`; removing the hazard is
        better than guarding it, and it leaves exactly one enforcing layer,
        whose removal a mutation check can actually observe
        (A04 audit, 2026-11-01).
        """
        if operator not in ("=", "!="):
            raise UserError("escrow_window_elapsed supports = and != only")
        elapsed = value if operator == "=" else not value
        cutoff = self._escrow_cutoff_utc()
        if elapsed:
            return ["|", ("source_type", "!=", "marketplace"), ("create_date", "<", cutoff)]
        return [("source_type", "=", "marketplace"), ("create_date", ">=", cutoff)]

    # Four reconciliation keys required by LP-02 (IN-007 §5.1, §10.2)
    payment_id = fields.Char(string="Payment ID", copy=False, index=True)
    rail = fields.Char(string="Payment Rail", default="bKash")
    rail_transaction_id = fields.Char(string="Rail Transaction ID", copy=False, index=True)
    merchant_invoice_number = fields.Char(string="Merchant Invoice Ref", copy=False, index=True)

    gl_move_id = fields.Many2one(
        "account.move", string="General Ledger Move", readonly=True, copy=False
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | LEDGER_GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "earned" for r in self):
            locked |= set(LEDGER_LOCKED)
        return locked

    @api.depends("gross_amount", "commission_rate")
    def _compute_commission(self):
        for rec in self:
            rec.commission_amount = rec.gross_amount * rec.commission_rate

    @api.depends("gross_amount", "commission_amount", "tds_amount", "source_type")
    def _compute_net(self):
        for rec in self:
            if rec.source_type == "partner_referral":
                # A partner is owed its commission (an expense of 1000 FiX),
                # less the TDS withheld on it
                rec.net_payable = rec.commission_amount - (rec.tds_amount or 0.0)
            else:
                # Seller entitlement = Gross GMV - Commission Earned - TDS Withheld
                rec.net_payable = rec.gross_amount - rec.commission_amount - (rec.tds_amount or 0.0)

    def _payable_role(self) -> str:
        self.ensure_one()
        return "partner_payable" if self.source_type == "partner_referral" else "seller_payable"

    # ---- scheme, TDS and PSR (measured, never typed) ------------------------
    def _fix_psr(self):
        """(verified, slip) from the payee's M52 tax profile: a PSR reference
        valid today, with its evidence recorded there."""
        self.ensure_one()
        if "fix.vendor.tax.profile" not in self.env:
            return False, False
        profile = self.env["fix.vendor.tax.profile"].for_partner(
            self.seller_partner_id, self.company_id
        )
        if profile and profile.is_filer_on(fields.Date.context_today(self)):
            return True, profile.psr_reference
        return False, False

    def _fix_measure_tds(self):
        """TDS = the scheme's rate on its base, uplifted for a non-filer
        (ITA 2023 s.264/265), with the PSR read from the tax profile."""
        for rec in self:
            if not rec.scheme_id:
                # no withholding rate on the row's scheme: the figure the
                # trusted source stated stands (zero by default)
                continue
            psr, slip = rec._fix_psr()
            tds = 0.0
            if rec.scheme_id:
                tds = rec.scheme_id.tds_on(rec.commission_amount, rec.gross_amount)
                if not psr:
                    uplift = float_param(rec.env, PARAM_NON_FILER_UPLIFT, DEFAULT_NON_FILER_UPLIFT)
                    tds = round(tds * (1.0 + uplift), 2)
            rec._guarded().write(
                {"tds_amount": tds, "psr_verified": psr, "psr_slip_number": slip or False}
            )

    def _fix_scheme_in_force(self):
        """The commission scheme in force today for this row's payee."""
        self.ensure_one()
        Scheme = self.env["fix.commission.scheme"]
        today = fields.Date.context_today(self)
        if self.source_type == "partner_referral":
            return Scheme._find(
                "partner",
                today,
                self.company_id,
                partner_type=self.referral_id.partner_id.partner_type,
            )
        seller = self.marketplace_order_id.selected_quote_id.seller_id.sudo()
        tier = seller.tier if seller and "tier" in seller._fields else False
        return Scheme._find("seller", today, self.company_id, seller_tier=tier)

    def _fix_ensure_scheme(self):
        """BRU-REV-10 / M53-12: a commission accrues on the scheme in force; a
        row with no scheme took the order's rate with TDS 0 and no non-filer
        uplift. It now takes the scheme in force, or is refused until Finance
        configures one. Superuser code keeps what it stated."""
        for rec in self.filtered(lambda r: not r.scheme_id):
            scheme = rec._fix_scheme_in_force()
            if not scheme:
                if rec.env.su:
                    continue
                raise UserError(
                    "No %s commission scheme is in force today for %s: nothing accrues until "
                    "Finance configures one in M53 Commission Schemes (its rate and TDS)."
                    % (
                        "partner" if rec.source_type == "partner_referral" else "seller",
                        rec.seller_partner_id.name,
                    )
                )
            vals = {"scheme_id": scheme.id}
            if scheme.commission_rate:
                vals["commission_rate"] = scheme.commission_rate
            rec._guarded().write(vals)

    @api.model
    def _fix_scheme_rate(self, vals):
        """BRU-REV-10: the scheme in force sets the rate; a scheme rate of 0
        means the rate agreed on the source (partner / marketplace order)."""
        scheme = self.env["fix.commission.scheme"].browse(vals.get("scheme_id"))
        if scheme and scheme.commission_rate:
            vals["commission_rate"] = scheme.commission_rate
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            raise UserError(
                "Commission rows are raised from a commissioned referral (Accrue Commission) "
                "or a marketplace order (commission.earned), never typed (A08 M53-4)."
            )
        typed_tds = []
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.commission.ledger")
                    or f"COM/{fields.Date.today().year}/New"
                )
            self._fix_scheme_rate(vals)
            # trusted code (seeds, a migration) may state a figure it already has
            typed_tds.append(self.env.su and "tds_amount" in vals)
        records = super().create(vals_list)
        for rec, typed in zip(records, typed_tds, strict=True):
            if not typed:
                rec._fix_measure_tds()
        return records

    def write(self, vals):
        if not self.env.su:
            for rec in self:
                if rec.state in ("accrued", "paid", "forfeited", "void"):  # noqa: SIM102
                    # Reversible only by contra-posting per LP-07
                    if set(LEDGER_LOCKED) & set(vals):
                        raise UserError(
                            "LP-07 Violation: Accrued commission entries cannot be modified. "
                            "Use contra-posting."
                        )
        return super().write(vals)

    def _post_partner_accrual(self):
        """Partner / referral commission is 1000 FiX's EXPENSE (it is the
        principal for the referred repair): Dr commission expense / Cr
        partner payable, the payable discharged by the payout run."""
        self.ensure_one()
        company = self.company_id
        journal = _configured_journal(self.env, company)
        expense = _configured_account(self.env, company, "partner_commission_expense")
        payable = _configured_account(self.env, company, "partner_payable")
        dims = {
            "branch_id": self.branch_id.id,
            "operating_unit_id": self.operating_unit_id.id,
            "cost_centre": "CC-PAY",
        }
        move, _ = post_with_dimensions(
            self.env,
            {
                "journal_id": journal.id,
                "company_id": company.id,
                "date": fields.Date.context_today(self),
                "ref": f"COM-ACCRUAL-{self.name}",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": f"Partner commission: {self.name}",
                            "account_id": expense.id,
                            "debit": self.commission_amount,
                            "credit": 0.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": f"Partner commission payable: {self.name}",
                            "account_id": payable.id,
                            "partner_id": self.seller_partner_id.id,
                            "debit": 0.0,
                            "credit": self.commission_amount,
                        },
                    ),
                ],
            },
            {0: dims, 1: dims},
            source="settlement",
        )
        self._guarded().write({"state": "accrued", "gl_move_id": move.id})
        publish(
            self.env,
            "commission.accrued",
            "fix.commission.ledger",
            self.id,
            {
                "commission_ref": self.name,
                "seller": self.seller_partner_id.name,
                "payee_type": "partner_referral",
                "commission_amount": float(self.commission_amount),
                "move_id": move.id,
            },
        )

    def _fix_assert_source(self):
        """A08 M53-4: a row accrues only with its source document."""
        for rec in self:
            if rec.env.su:
                continue
            if rec.source_type == "partner_referral":
                ref = rec.referral_id
                if not ref or ref.state != "commissioned":
                    raise UserError(
                        "Commission %s has no commissioned referral behind it: nothing accrues."
                        % rec.name
                    )
            elif not rec.marketplace_order_id:
                raise UserError(
                    "Commission %s has no marketplace order behind it: nothing accrues." % rec.name
                )
            if rec.commission_rate <= 0:
                raise UserError(
                    "Commission %s carries no rate from its scheme or source." % rec.name
                )

    def action_post_to_gl(self):
        """Post commission accrual to GL through M19 (cd_gl_ext).
        Strictly enforces FF-91 (MS-01):
        - Marketplace gross is NEVER booked to revenue!
        - Commission Earned is credited to Revenue (400100).
        - Seller Share is credited to Liability (200200).
        - Customer Clearing / Bank is debited (101000)."""
        require_role(self.env, GROUP_ACCOUNTANT, "Accruing a commission")
        for rec in self:
            if rec.state != "earned":
                continue
            rec._fix_assert_source()
            rec._fix_ensure_scheme()
            # TDS and PSR are measured again at accrual, then locked (LP-07)
            rec._fix_measure_tds()
            if rec.source_type == "partner_referral":
                rec._post_partner_accrual()
                continue

            company = rec.company_id
            journal = _configured_journal(self.env, company)
            bank_clearing = _configured_account(self.env, company, "clearing")
            commission_rev = _configured_account(self.env, company, "commission_revenue")
            seller_payable = _configured_account(self.env, company, "seller_payable")

            gross = rec.gross_amount
            comm = rec.commission_amount
            seller_share = gross - comm

            move_vals = {
                "journal_id": journal.id,
                "company_id": company.id,
                "date": fields.Date.context_today(rec),
                "ref": f"COM-ACCRUAL-{rec.name}",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": f"Customer Receipt Clearing: {rec.name}",
                            "account_id": bank_clearing.id,
                            "debit": gross,
                            "credit": 0.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": f"Commission Revenue (FF-91): {rec.name}",
                            "account_id": commission_rev.id,
                            "debit": 0.0,
                            "credit": comm,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": f"Seller Entitlement Liability: {rec.name}",
                            "account_id": seller_payable.id,
                            "partner_id": rec.seller_partner_id.id,
                            "debit": 0.0,
                            "credit": seller_share,
                        },
                    ),
                ],
            }

            dim_by_line = {
                0: {
                    "branch_id": rec.branch_id.id,
                    "operating_unit_id": rec.operating_unit_id.id,
                    "cost_centre": "CC-MKT",
                },
                1: {
                    "branch_id": rec.branch_id.id,
                    "operating_unit_id": rec.operating_unit_id.id,
                    "cost_centre": "CC-REV",
                },
                2: {
                    "branch_id": rec.branch_id.id,
                    "operating_unit_id": rec.operating_unit_id.id,
                    "cost_centre": "CC-PAY",
                },
            }

            move, _ = post_with_dimensions(self.env, move_vals, dim_by_line, source="settlement")
            rec._guarded().write(
                {
                    "state": "accrued",
                    "gl_move_id": move.id,
                }
            )

            publish(
                self.env,
                "commission.accrued",
                "fix.commission.ledger",
                rec.id,
                {
                    "commission_ref": rec.name,
                    "seller": rec.seller_partner_id.name,
                    "gross": float(rec.gross_amount),
                    "commission_amount": float(rec.commission_amount),
                    "seller_share": float(seller_share),
                    "move_id": move.id,
                    "payment_id": rec.payment_id or "",
                    "rail": rec.rail or "",
                },
            )

    # ---- the M12 -> M53 seam --------------------------------------------------
    @api.model
    def consume_commission_earned(self, event: dict):
        """The marketplace half of commission.earned. M53-15 / M53-4: there is
        ONE consumer of the event (fix.a04.finance.consumers); two active rows
        raised two ledger rows per order. Kept as a thin door to that one path."""
        if not self.env.su:
            raise AccessError("The commission consumer runs only from the event relay.")
        if (event.get("aggregate") or "fix.marketplace.order") != "fix.marketplace.order":
            return {"skipped": event.get("aggregate")}
        return self.env["fix.a04.finance.consumers"].consume_commission_earned(
            dict(event, aggregate="fix.marketplace.order")
        )

    # ---- M53-4: the exit for rows with no source document ---------------------
    def _fix_unsourced(self):
        return self.filtered(
            lambda r: r.state == "earned"
            and not r.gl_move_id
            and not r.referral_id
            and not r.marketplace_order_id
        )

    def action_link_source(self, source_ref=""):
        """Name the source document of a row that has none: the marketplace
        order (or referral) it was earned on. The document is re-read and must
        agree on payee and amount; then the row can accrue."""
        require_role(self.env, GROUP_ACCOUNTANT, "Linking a commission to its source")
        source_ref = (source_ref or "").strip()
        if not source_ref:
            raise UserError("Name the marketplace order or referral this commission was earned on.")
        for rec in self:
            if not rec._fix_unsourced():
                raise UserError("Commission %s already has its source or left Earned." % rec.name)
            if rec.source_type == "partner_referral":
                ref = (
                    self.env["fix.referral"]
                    .sudo()
                    .search(
                        [("name", "=", source_ref), ("company_id", "=", rec.company_id.id)], limit=1
                    )
                )
                if not ref or ref.state != "commissioned":
                    raise UserError(
                        "No commissioned referral %s in %s." % (source_ref, rec.company_id.name)
                    )
                if ref.partner_id.partner_id != rec.seller_partner_id:
                    raise UserError("Referral %s pays another partner." % ref.name)
                if abs((ref.base_amount or 0.0) - rec.gross_amount) > 0.005:
                    raise UserError(
                        "Referral %s has base %.2f; this row says %.2f."
                        % (ref.name, ref.base_amount, rec.gross_amount)
                    )
                rec._guarded().write({"referral_id": ref.id, "source_ref": ref.name})
                ref._guarded().write({"commission_ledger_id": rec.id})
                continue
            order = (
                self.env["fix.marketplace.order"]
                .sudo()
                .search(
                    [("name", "=", source_ref), ("company_id", "=", rec.company_id.id)], limit=1
                )
            )
            if not order or order.state not in ("commissioned", "paid"):
                raise UserError(
                    "No commissioned marketplace order %s in %s."
                    % (source_ref, rec.company_id.name)
                )
            if order.selected_quote_id.seller_id.partner_id != rec.seller_partner_id:
                raise UserError("Order %s pays another seller." % order.name)
            awarded = order.awarded_price or order.selected_quote_id.quoted_price or 0.0
            if abs(awarded - rec.gross_amount) > 0.005:
                raise UserError(
                    "Order %s was awarded at %.2f; this row says %.2f."
                    % (order.name, awarded, rec.gross_amount)
                )
            if self.sudo().search([("marketplace_order_id", "=", order.id)], limit=1):
                raise UserError("Order %s already has its commission row." % order.name)
            vals = {"marketplace_order_id": order.id, "source_ref": order.name}
            if order.commission_rate:
                vals["commission_rate"] = order.commission_rate
            rec._guarded().write(vals)
            rec.message_post(body="Linked to order %s by %s." % (order.name, self.env.user.name))
        return True

    def action_void_unsourced(self, reason=""):
        """The Accounting Administrator closes earned rows with no source: they
        never reached the GL or a payout, so nothing is reversed."""
        require_role(self.env, GROUP_ADMINISTRATOR, "Voiding a commission row")
        if not (reason or "").strip():
            raise UserError("State why the commission row is voided.")
        for rec in self:
            if not rec._fix_unsourced():
                raise UserError(
                    "Commission %s has a source document or left Earned: it is not voided."
                    % rec.name
                )
            rec._guarded().write(
                {
                    "state": "void",
                    "void_reason": reason.strip()[:250],
                    "voided_by_id": self.env.uid,
                    "voided_at": fields.Datetime.now(),
                }
            )
            rec.message_post(body="Voided by %s: %s" % (self.env.user.name, reason.strip()[:250]))
        return True

    def action_void_all_unsourced(self, reason=""):
        """The same decision for every source-less earned row of the selected
        row's company (145 on the live copy), so it is not 145 clicks."""
        require_role(self.env, GROUP_ADMINISTRATOR, "Voiding commission rows")
        rows = self.search(
            [
                ("company_id", "in", self.mapped("company_id").ids),
                ("state", "=", "earned"),
                ("gl_move_id", "=", False),
                ("referral_id", "=", False),
                ("marketplace_order_id", "=", False),
            ]
        )
        rows.action_void_unsourced(reason)
        return {"voided": len(rows)}


PAYOUT_GUARDED = {
    "state",
    "prepared_by_id",
    "prepared_at",
    "approved_by_id",
    "approved_date",
    "sod_verified",
    "approved_total",
    "approved_commission_ids",
    "line_ids",
    "gl_move_id",
    "idempotency_key",
    "rail_status",
    "rail_batch_id",
    "bank_confirmation_ref",
    "bank_confirmed_by_id",
    "bank_confirmed_at",
    "beftn_file",
    "beftn_filename",
}
# Frozen once the run is prepared: the approval covers exactly these rows.
PAYOUT_LOCKED = ("commission_ids", "clawback_ids", "company_id", "period", "currency_id")


class FixPayoutRun(models.Model):
    """Payout run: money to 500-2,000 sellers and partners.

    draft (collect) -> prepared (frozen; routed to M63) -> approved (pinned
    payee lines) -> executing (one M50 instruction per payee) -> executed
    (every instruction bank-confirmed; statements issued; payable
    discharged). Preparer != approver != releaser (M50)."""

    _name = "fix.payout.run"
    _description = "Payout Run / পরিশোধ চক্র"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.finance.dofa.mixin"]
    _order = "period desc, id desc"
    _approval_domain = "payout_run"
    _fin_direct_param = None
    _fin_cfo_param = PARAM_PAYOUT_CFO
    _fin_cfo_default = DEFAULT_PAYOUT_CFO
    _fin_what = "Payout run"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True, copy=False, default="New")
    period = fields.Char(string="Settlement Period", required=True, index=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    total_payable = fields.Monetary(
        compute="_compute_total",
        string="Total Net Payable",
        currency_field="currency_id",
        store=True,
    )
    total_tds = fields.Monetary(
        compute="_compute_total",
        string="Total Statutory TDS Withheld",
        currency_field="currency_id",
        store=True,
    )
    total_gross = fields.Monetary(
        compute="_compute_total", string="Total Gross GMV", currency_field="currency_id", store=True
    )
    seller_count = fields.Integer(compute="_compute_total", string="Seller Count", store=True)

    state = fields.Selection(
        [
            ("draft", "Draft / খসড়া"),
            ("prepared", "Prepared — Awaiting Approval / প্রস্তুত"),
            ("approved", "Approved (SoD Verified) / অনুমোদিত"),
            ("executing", "Released to Treasury (M50) / চলমান"),
            ("file_generated", "BEFTN File Generated (legacy) / ফাইল তৈরি"),
            ("executed", "Executed / সমাপ্ত"),
            ("cancelled", "Cancelled / বাতিল"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )

    # Segregation of Duties fields
    prepared_by_id = fields.Many2one("res.users", string="Prepared By", readonly=True, copy=False)
    prepared_at = fields.Datetime(string="Prepared On", readonly=True, copy=False)
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True, copy=False)
    approved_date = fields.Datetime(string="Approved Date", readonly=True, copy=False)
    sod_verified = fields.Boolean(string="SoD Verified", readonly=True, default=False, copy=False)
    approved_total = fields.Monetary(
        string="Approved Net Total",
        currency_field="currency_id",
        readonly=True,
        copy=False,
        help="The net the approver signed off (F2): a different total is not paid.",
    )
    approved_commission_ids = fields.Many2many(
        "fix.commission.ledger",
        "fix_payout_run_approved_commission_rel",
        "run_id",
        "commission_id",
        string="Approved Commissions",
        readonly=True,
        copy=False,
    )
    line_ids = fields.One2many(
        "fix.payout.run.line", "run_id", string="Pinned Payee Lines", readonly=True
    )

    commission_ids = fields.Many2many("fix.commission.ledger", string="Commissions")
    clawback_ids = fields.Many2many(
        "fix.settlement.adjustment",
        "fix_payout_run_clawback_rel",
        "run_id",
        "adjustment_id",
        string="Clawbacks to Recover",
        domain=[("adjustment_type", "=", "clawback"), ("state", "=", "active")],
    )
    recovery_ids = fields.One2many(
        "fix.settlement.recovery", "payout_run_id", string="Clawbacks Recovered"
    )
    total_clawback = fields.Monetary(
        compute="_compute_total",
        string="Clawback Deducted",
        currency_field="currency_id",
        store=True,
    )

    # Kept for the run's history: the INT-007 / BEFTN fields of runs paid
    # before the M50 seam (read-only, no longer written).
    idempotency_key = fields.Char(string="Idempotency Key (7-Day TTL)", copy=False, readonly=True)
    rail_type = fields.Selection(
        [
            ("api", "Direct API (Mobile Money / Bank Gateway)"),
            ("beftn", "BEFTN Standard Batch File (128-byte)"),
            ("m50", "Treasury (M50 payment instructions)"),
        ],
        string="Disbursement Rail",
        default="m50",
        required=True,
    )
    rail_status = fields.Selection(
        [
            ("draft", "Not Submitted"),
            ("executing", "Executing"),
            ("confirmed", "Confirmed"),
            ("unknown", "Unknown (Timed Out)"),
            ("pending_bank_confirmation", "Pending Bank Confirmation"),
            ("file_generated", "BEFTN File Generated (Not Confirmed)"),
            ("failed", "Failed"),
        ],
        string="Rail Confirmation Status",
        default="draft",
        tracking=True,
    )
    rail_batch_id = fields.Char(string="Rail Batch Reference", readonly=True, copy=False)
    bank_confirmation_ref = fields.Char(
        string="Bank Settlement Reference",
        copy=False,
        readonly=True,
        help="Legacy: the bank reference recorded on runs paid before the M50 seam.",
    )
    bank_confirmed_by_id = fields.Many2one(
        "res.users", string="Bank Confirmation Recorded By", readonly=True, copy=False
    )
    bank_confirmed_at = fields.Datetime(string="Bank Confirmation Recorded At", readonly=True)
    beftn_file = fields.Binary(string="BEFTN Batch File Content", readonly=True)
    beftn_filename = fields.Char(string="BEFTN Filename", readonly=True)

    gl_move_id = fields.Many2one(
        "account.move", string="GL Disbursement Entry", readonly=True, copy=False
    )
    statement_ids = fields.One2many(
        "fix.seller.statement", "payout_run_id", string="Seller Statements"
    )
    reconciliation_ids = fields.One2many(
        "fix.payout.reconciliation", "payout_run_id", string="Reconciliation Runs"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | PAYOUT_GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "draft" for r in self):
            locked |= set(PAYOUT_LOCKED)
        return locked

    def write(self, vals):
        if not self._fix_guard_open():
            touched = set(PAYOUT_LOCKED) & set(vals)
            if touched and self.filtered(lambda r: r.state != "draft"):
                raise UserError(
                    "Payout run %s is prepared: its commissions and clawbacks are fixed — the "
                    "approval covers exactly them (F2). Cancel it and prepare a new run."
                    % ", ".join(self.mapped("name"))
                )
        return super().write(vals)

    @api.depends(
        "commission_ids.net_payable",
        "commission_ids.tds_amount",
        "commission_ids.gross_amount",
        "clawback_ids.remaining_amount",
        "recovery_ids.amount",
        "state",
    )
    def _compute_total(self):
        for rec in self:
            rec.total_clawback = sum(
                amount for pairs in rec._clawback_deductions().values() for _a, amount in pairs
            )
            rec.total_payable = sum(rec.commission_ids.mapped("net_payable")) - rec.total_clawback
            rec.total_tds = sum(rec.commission_ids.mapped("tds_amount"))
            rec.total_gross = sum(rec.commission_ids.mapped("gross_amount"))
            rec.seller_count = len(rec.commission_ids.mapped("seller_partner_id"))

    def _clawback_deductions(self) -> dict:
        """{payee: [(clawback, amount)]} deducted in this run. An executed
        run reports what it recovered; an open run projects each payee's
        open clawbacks against that payee's net in the run (never more)."""
        self.ensure_one()
        out: dict = {}
        if self.state == "executed":
            for line in self.recovery_ids:
                out.setdefault(line.adjustment_id.seller_partner_id, []).append(
                    (line.adjustment_id, line.amount)
                )
            return out
        for payee in self.commission_ids.mapped("seller_partner_id"):
            available = sum(
                self.commission_ids.filtered(lambda c, p=payee: c.seller_partner_id == p).mapped(
                    "net_payable"
                )
            )
            for claw in self.clawback_ids.filtered(
                lambda a, p=payee: a.seller_partner_id == p and a.state == "active"
            ).sorted("id"):
                take = round(min(available, claw.remaining_amount), 2)
                if take <= 0:
                    continue
                out.setdefault(payee, []).append((claw, take))
                available -= take
        return out

    def _fix_held_payees(self, partners):
        """Payees whose M12 seller record carries a payout hold (dispute,
        quality investigation, KYC; FR-REV-035). Read softly: the field is
        the marketplace's."""
        if "fix.marketplace.seller" not in self.env:
            return self.env["res.partner"]
        Seller = self.env["fix.marketplace.seller"].sudo()
        if "payout_hold" not in Seller._fields or not partners:
            return self.env["res.partner"]
        held = Seller.search(
            [("payout_hold", "=", True), ("partner_id", "in", partners.commercial_partner_id.ids)]
        )
        return held.mapped("partner_id")

    def action_collect_accrued(self):
        """Fill a draft run with every accrued commission (sellers AND
        partners) not held in escrow and not already in another open run,
        plus the payees' open clawbacks."""
        Ledger = self.env["fix.commission.ledger"]
        for run in self:
            if run.state != "draft":
                raise UserError("Commissions are collected into a draft payout run only")
            busy = self.search(
                [
                    ("id", "!=", run.id),
                    ("state", "not in", ("executed", "cancelled")),
                    ("company_id", "=", run.company_id.id),
                ]
            ).mapped("commission_ids")
            rows = Ledger.search(
                [
                    ("company_id", "=", run.company_id.id),
                    ("state", "=", "accrued"),
                    ("gl_move_id", "!=", False),
                    ("escrow_hold", "=", False),
                    # FLAW-12.2: the buyer dispute window must have elapsed.
                    ("escrow_window_elapsed", "=", True),
                    ("id", "not in", busy.ids),
                ]
            )
            # FR-REV-035: a seller on payout hold is skipped (paid once released)
            held = self._fix_held_payees(rows.mapped("seller_partner_id"))
            if held:
                rows = rows.filtered(
                    lambda r, h=held: r.seller_partner_id.commercial_partner_id not in h
                )
            # No Python re-confirm here, deliberately. The domain above and
            # `escrow_window_elapsed` are both derived from `create_date`, so
            # they cannot disagree, and a second guard would only make the
            # first one's removal invisible to a mutation check. One enforcing
            # layer, and it is tested (A04 audit, 2026-11-01).
            if not rows and not run.commission_ids:
                raise UserError(
                    "No accrued commissions are free to pay — accrue commissions to the GL first"
                )
            run.commission_ids = [(6, 0, (run.commission_ids | rows).ids)]
            claws = self.env["fix.settlement.adjustment"].search(
                [
                    ("company_id", "=", run.company_id.id),
                    ("adjustment_type", "=", "clawback"),
                    ("state", "=", "active"),
                    ("seller_partner_id", "in", run.commission_ids.mapped("seller_partner_id").ids),
                ]
            )
            run.clawback_ids = [(6, 0, claws.ids)]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.payout.run")
                    or f"PAY/{fields.Date.today().year}/New"
                )
        return super().create(vals_list)

    # ---- the ladder -----------------------------------------------------------
    def _dofa_amount(self) -> float:
        self.ensure_one()
        if self.state not in ("draft", "prepared") and self.approved_total:
            return self.approved_total
        return self.total_payable

    @api.depends("total_payable", "approved_total", "state")
    def _compute_dofa_tier_required(self):
        return super()._compute_dofa_tier_required()

    def _fin_requester(self):
        return self.prepared_by_id

    def _fin_extra_conflicts(self):
        """SOD-06 / BRU-REV-23: a payee may not approve their own payout, nor
        anyone who changed a payee's bank account since it was confirmed."""
        self.ensure_one()
        users = self.env["res.users"]
        payees = self.commission_ids.mapped("seller_partner_id").commercial_partner_id
        users |= self.env["res.users"].sudo().search([("partner_id", "in", payees.ids)])
        for bank in payees.bank_ids.sudo():
            if "fix_changed_by_id" in bank._fields:
                users |= bank.fix_changed_by_id
        return users

    def _fix_check_rows(self):
        self.ensure_one()
        if not self.commission_ids:
            raise UserError("No commissions attached to this payout run.")
        held = self.commission_ids.filtered("escrow_hold")
        if held:
            raise UserError(
                "Payout run %s carries commissions held in escrow (%s) — remove them or "
                "release the escrow first." % (self.name, ", ".join(held.mapped("name")))
            )
        unposted = self.commission_ids.filtered(lambda c: c.state != "accrued" or not c.gl_move_id)
        if unposted:
            raise UserError(
                "Payout run %s carries commissions never accrued to the GL (%s): the discharge "
                "would debit a payable that was never credited."
                % (self.name, ", ".join(unposted.mapped("name")))
            )
        held = self._fix_held_payees(self.commission_ids.mapped("seller_partner_id"))
        if held:
            raise UserError(
                "Payout run %s pays %s, on payout hold (FR-REV-035): remove them or release "
                "the hold first." % (self.name, ", ".join(held.mapped("name")))
            )
        foreign = self.commission_ids.filtered(lambda c: c.company_id != self.company_id)
        if foreign:
            raise UserError("Payouts cannot cross legal entities (BRU-REV-24).")
        other = self.search(
            [
                ("id", "!=", self.id),
                ("state", "not in", ("draft", "cancelled")),
                ("commission_ids", "in", self.commission_ids.ids),
            ],
            limit=1,
        )
        if other:
            raise UserError(
                "Commissions of %s are already in payout run %s: a commission is paid once "
                "(BRU-REV-18)." % (self.name, other.name)
            )

    def action_prepare(self):
        """The preparer freezes the run and asks for its approval (M63)."""
        require_role(self.env, GROUP_ACCOUNTANT, "Preparing a payout run")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft payout run is prepared (%s)" % rec.state)
            rec._fix_check_rows()
            rec._guarded().write(
                {
                    "state": "prepared",
                    "prepared_by_id": self.env.uid,
                    "prepared_at": fields.Datetime.now(),
                }
            )
            rec._fin_route(
                "Payout run %s (%s): %d payee(s), net BDT %.2f"
                % (rec.name, rec.period, rec.seller_count, rec.total_payable)
            )
        return True

    def action_approve(self):
        """Approval comes from the Accounting Administrator's (above the CFO
        band, the CFO's) M63 inbox task: a direct call is refused by the
        routing guard. Superuser code is trusted."""
        return self.action_dofa_approve()

    def _fin_before_approve(self):
        self.ensure_one()
        if self.state != "prepared":
            raise UserError(
                "Payout run %s is %s: a run is approved once, from prepared — an approved or "
                "executed run is never approved (or paid) again (BRU-REV-18)."
                % (self.name, self.state)
            )
        self._fix_check_rows()

    def _fix_payee_lines(self):
        """[(payee, bank, net, tds, gross, commissions)] per payee, after clawbacks."""
        self.ensure_one()
        deductions = self._clawback_deductions()
        out = []
        for payee in self.commission_ids.mapped("seller_partner_id"):
            rows = self.commission_ids.filtered(lambda c, p=payee: c.seller_partner_id == p)
            net = sum(rows.mapped("net_payable")) - sum(
                amount for _c, amount in deductions.get(payee, [])
            )
            out.append(
                (
                    payee,
                    payee.bank_ids[:1],
                    round(net, 2),
                    round(sum(rows.mapped("tds_amount")), 2),
                    round(sum(rows.mapped("gross_amount")), 2),
                    rows,
                )
            )
        return out

    def _fin_after_approve(self):
        """Pin what is paid (F2): one line per payee with the bank account and
        its number as they stand at approval, and the run's net total."""
        self.ensure_one()
        run = self.sudo()
        Line = self.env["fix.payout.run.line"].sudo()
        for payee, bank, net, tds, gross, rows in run._fix_payee_lines():
            Line.create(
                {
                    "run_id": run.id,
                    "partner_id": payee.id,
                    "partner_bank_id": bank.id or False,
                    "acc_number": (bank.acc_number or "").strip() or False,
                    "routing_number": _routing_of(bank) or False,
                    "amount": max(net, 0.0),
                    "tds_amount": tds,
                    "gross_amount": gross,
                    "commission_ids": [(6, 0, rows.ids)],
                }
            )
        run._guarded().write(
            {
                "state": "approved",
                "approved_by_id": self.env.uid,
                "approved_date": fields.Datetime.now(),
                "sod_verified": True,
                "approved_total": run.total_payable,
                "approved_commission_ids": [(6, 0, run.commission_ids.ids)],
            }
        )
        publish(
            self.env,
            "payout.approved",
            "fix.payout.run",
            run.id,
            {
                "payout_run": run.name,
                "total_payable": float(run.total_payable),
                "total_tds": float(run.total_tds),
                "seller_count": run.seller_count,
                "approved_by": self.env.user.name,
            },
        )

    def _fix_assert_pinned(self):
        """What is paid is what was approved: the commission set, the total
        and each payee's account number."""
        self.ensure_one()
        if set(self.commission_ids.ids) != set(self.approved_commission_ids.ids):
            raise UserError(
                "Payout run %s carries other commissions than were approved: approval voided — "
                "nothing is paid." % self.name
            )
        if abs(self.total_payable - self.approved_total) > 0.005:
            raise UserError(
                "Payout run %s now totals %.2f; %.2f was approved. Nothing is paid."
                % (self.name, self.total_payable, self.approved_total)
            )
        for line in self.line_ids.filtered(lambda ln: ln.amount > 0.005):
            if not line.partner_bank_id:
                raise UserError(
                    "No payee bank account for %s: nothing is paid (a confirmed account is "
                    "recorded first, under M52's dual control)." % line.partner_id.name
                )
            bank = line.partner_bank_id.sudo().exists()
            if not bank:
                raise UserError(
                    "The approved account of %s no longer exists: nothing is paid."
                    % line.partner_id.name
                )
            if (bank.acc_number or "").strip() != (line.acc_number or ""):
                raise UserError(
                    "The bank account of %s changed after approval (%s approved): the "
                    "approval covered the account it was given for (F2)."
                    % (line.partner_id.name, line.acc_number)
                )
            if bank.partner_id.commercial_partner_id != line.partner_id.commercial_partner_id:
                raise UserError(
                    "The approved account no longer belongs to %s." % line.partner_id.name
                )

    def _fix_active_lines(self):
        """The payee lines still to be paid or paid (not replaced or dropped)."""
        self.ensure_one()
        return self.line_ids.filtered(lambda ln: not ln.superseded)

    def _payout_journal(self):
        code = self.env["ir.config_parameter"].sudo().get_param(PARAM_PAYOUT_JOURNAL)
        if not code:
            return self.env["account.journal"]
        return (
            self.env["account.journal"]
            .sudo()
            .search(
                [
                    ("code", "=", code),
                    ("company_id", "=", self.company_id.id),
                    ("type", "=", "bank"),
                ],
                limit=1,
            )
        )

    def action_request_payments(self):
        """Release the approved run to treasury (FR-REV-034): one M50 payment
        instruction per pinned payee line, after B2's payee-account gate.
        Treasury prepares, releases (two-person) and confirms from the bank
        statement; nothing is paid here."""
        require_role(self.env, GROUP_ACCOUNTANT, "Releasing a payout run to treasury")
        Execution = self.env["fix.payment.execution"]
        Bank = self.env["res.partner.bank"]
        if not hasattr(Execution, "_fix_request_payment"):
            raise UserError("Treasury's payment-request service (M50) is not installed.")
        if not hasattr(Bank, "_fix_assert_payable_bank"):
            raise UserError("The payee bank-account control (M52) is not installed.")
        for run in self:
            if run.state != "approved":
                raise UserError(
                    "Payout run %s is %s: only an approved run is released to treasury."
                    % (run.name, run.state)
                )
            run._fin_assert_approved()
            run._fix_assert_pinned()
            for line in run.line_ids.filtered(lambda ln: ln.amount > 0.005):
                Bank._fix_assert_payable_bank(line.partner_bank_id)
                run._fix_request_line_payment(line)
            run._guarded().write(
                {"state": "executing", "rail_type": "m50", "rail_status": "executing"}
            )
            run.message_post(
                body="Released to treasury: %d payment instruction(s), net BDT %.2f."
                % (len(run.line_ids.filtered("payment_execution_id")), run.approved_total)
            )
            run._fix_sync_payments()
        return True

    def _fix_request_line_payment(self, line):
        """One M50 instruction for one pinned payee line."""
        self.ensure_one()
        options = {
            "company_id": self.company_id.id,
            "operating_unit_id": self.operating_unit_id.id or False,
            "method": "bank_transfer",
            "rail": "beftn",
        }
        journal = self._payout_journal()
        if journal:
            options["journal_id"] = journal.id
        pay = self.env["fix.payment.execution"]._fix_request_payment(
            "fix.payout.run.line",
            line.id,
            line.partner_id,
            line.partner_bank_id,
            line.amount,
            self.currency_id,
            "%s / %s" % (self.name, line.partner_id.name),
            self.approved_by_id,
            **options,
        )
        line.sudo().write({"payment_execution_id": pay.id})
        return pay

    # ---- M53-1: an instruction treasury could not pay -------------------------
    def _fix_unpaid_lines(self):
        """Active lines whose instruction the bank rejected or treasury cancelled."""
        self.ensure_one()
        return self._fix_active_lines().filtered(
            lambda ln: ln.amount > 0.005
            and ln.payment_execution_id.sudo().state in ("failed", "cancelled")
        )

    def action_rerequest_unpaid(self):
        """Ask treasury again for the rejected or cancelled payee lines, on the
        terms approved: same payee, account and amount. A failed instruction is
        re-queued; a cancelled one is final in M50, so its line is replaced by
        an identical pinned line with a new instruction."""
        require_role(self.env, GROUP_ACCOUNTANT, "Re-requesting a payout payment")
        Bank = self.env["res.partner.bank"]
        for run in self:
            if run.state != "executing":
                raise UserError(
                    "Payout run %s is %s, not released to treasury." % (run.name, run.state)
                )
            lines = run._fix_unpaid_lines()
            if not lines:
                raise UserError("Payout run %s has no rejected or cancelled payment." % run.name)
            for line in lines:
                bank = line.partner_bank_id.sudo().exists()
                if not bank or (bank.acc_number or "").strip() != (line.acc_number or ""):
                    raise UserError(
                        "The bank account of %s changed after approval: drop this payee from the "
                        "run and pay them in a new, newly approved run." % line.partner_id.name
                    )
                Bank._fix_assert_payable_bank(bank)
                pay = line.payment_execution_id.sudo()
                if pay.state == "failed":
                    pay.with_env(self.env).action_retry()
                    continue
                twin = (
                    self.env["fix.payout.run.line"]
                    .sudo()
                    .create(
                        {
                            "run_id": run.id,
                            "partner_id": line.partner_id.id,
                            "partner_bank_id": line.partner_bank_id.id,
                            "acc_number": line.acc_number,
                            "routing_number": line.routing_number,
                            "amount": line.amount,
                            "tds_amount": line.tds_amount,
                            "gross_amount": line.gross_amount,
                            "commission_ids": [(6, 0, line.commission_ids.ids)],
                        }
                    )
                )
                line.sudo().write(
                    {"superseded": True, "superseded_reason": "Cancelled instruction re-requested"}
                )
                run._fix_request_line_payment(twin)
            run._guarded().write({"rail_status": "executing"})
            run.message_post(
                body="%s re-requested %d unpaid payment(s) from treasury."
                % (self.env.user.name, len(lines))
            )
        return True

    def action_drop_unpaid(self, reason=""):
        """Close the run without the payees treasury could not pay: their
        commissions return to Accrued, free for a new, newly approved run. The
        Accounting Administrator decides, not whoever prepared the run."""
        require_role(self.env, GROUP_ADMINISTRATOR, "Dropping a payee from a payout run")
        if not (reason or "").strip():
            raise UserError("State why the payee is dropped from the run.")
        for run in self:
            if run.state != "executing":
                raise UserError(
                    "Payout run %s is %s, not released to treasury." % (run.name, run.state)
                )
            if not self.env.su and run.prepared_by_id == self.env.user:
                raise UserError(
                    "Segregation of duties: you prepared %s; another Accounting Administrator "
                    "decides this." % run.name
                )
            lines = run._fix_unpaid_lines()
            if not lines:
                raise UserError("Payout run %s has no rejected or cancelled payment." % run.name)
            dropped = lines.mapped("commission_ids")
            lines.sudo().write({"superseded": True, "superseded_reason": reason.strip()[:250]})
            # the run first, so a cancel's status sync sees only who is still paid
            run._guarded().write(
                {
                    "commission_ids": [(3, c.id) for c in dropped],
                    "approved_commission_ids": [(3, c.id) for c in dropped],
                    "rail_status": "executing",
                }
            )
            for pay in (
                lines.mapped("payment_execution_id").sudo().filtered(lambda p: p.state == "failed")
            ):
                pay.with_env(self.env).action_cancel()
            run.message_post(
                body="%s dropped %s from the run: %s. Their commissions stay accrued for a new run."
                % (
                    self.env.user.name,
                    ", ".join(lines.mapped("partner_id.name")),
                    reason.strip()[:250],
                )
            )
            if run._fix_active_lines():
                run._fix_sync_payments()
            else:
                run._guarded().write({"state": "cancelled", "rail_status": "failed"})
        return True

    def action_open_reconciliation(self):
        """M53-14: open (or re-run) this run's payout reconciliation."""
        require_role(self.env, GROUP_ACCOUNTANT, "Reconciling a payout run")
        Rec = self.env["fix.payout.reconciliation"]
        out = Rec
        for run in self:
            rec = run.reconciliation_ids.filtered(lambda r: r.state != "resolved")[
                :1
            ] or Rec.create({"company_id": run.company_id.id, "payout_run_id": run.id})
            rec.action_run_reconciliation()
            out |= rec
        return {"reconciliation": out[:1].name, "state": out[:1].state}

    # Old entry points: the run no longer pays by itself.
    def action_execute(self):
        return self.action_request_payments()

    def action_submit_payout(self, simulate_timeout=False, rail_instance=None):
        return self.action_request_payments()

    def action_generate_beftn(self, rail_instance=None):
        return self.action_request_payments()

    def action_query_status(self, rail_instance=None):
        """Read the M50 instructions' outcome (bank statement confirmations)."""
        return self._fix_sync_payments()

    def action_confirm_bank_settlement(self, bank_reference: str = ""):
        raise UserError(
            "A payout is confirmed by treasury from the imported bank statement (M50), never "
            "by a typed reference (A08 M53-3)."
        )

    def _fix_sync_payments(self):
        """Complete the run once every instruction is bank-confirmed."""
        for run in self.sudo():
            if run.state != "executing":
                continue
            lines = run._fix_active_lines().filtered(lambda ln: ln.amount > 0.005)
            # per disbursement (M53-1): each payee is discharged in the GL when
            # the bank confirms THAT payment, not when the last one clears
            for line in lines.filtered(
                lambda ln: ln.payment_execution_id.state == "executed" and not ln.gl_move_id
            ):
                run._fix_post_line_discharge(line)
            states = [ln.payment_execution_id.state for ln in lines]
            if any(s in ("failed", "cancelled") for s in states):
                run._guarded().write({"rail_status": "failed"})
            if lines and all(s == "executed" for s in states):
                run._guarded().write({"rail_status": "confirmed"})
                run._finalize_payout_execution()
            elif not lines and (run._fix_active_lines() or not run.line_ids):
                # nothing to pay (a clawback consumed every net), not "all dropped"
                run._guarded().write({"rail_status": "confirmed"})
                run._finalize_payout_execution()
        return True

    def _fix_post_line_discharge(self, line):
        """Discharge one payee line: Dr each payable role, Cr clawback recovery,
        Cr TDS, Cr the bank treasury paid from. The commissions are paid now."""
        self.ensure_one()
        run = self.sudo()
        company = run.company_id
        rows = line.commission_ids
        by_role: dict[str, float] = {}
        for c in rows:
            role = c._payable_role()
            by_role[role] = by_role.get(role, 0.0) + c.net_payable + (c.tds_amount or 0.0)
        labels = {
            "seller_payable": "Discharge Seller Liability",
            "partner_payable": "Discharge Partner Commission Liability",
        }
        entries = []
        dims = []
        for role, amount in sorted(by_role.items(), key=lambda kv: kv[0] != "seller_payable"):
            entries.append(
                {
                    "name": "%s: %s" % (labels[role], run.name),
                    "account_id": _configured_account(self.env, company, role).id,
                    "partner_id": line.partner_id.id,
                    "debit": round(amount, 2),
                    "credit": 0.0,
                }
            )
            dims.append("CC-PAY")
        clawback = round(sum(a for _c, a in run._clawback_deductions().get(line.partner_id, [])), 2)
        if clawback > 0.005:
            entries.append(
                {
                    "name": "Clawbacks recovered: %s" % run.name,
                    "account_id": _configured_account(self.env, company, "clawback_recovery").id,
                    "debit": 0.0,
                    "credit": clawback,
                }
            )
            dims.append("CC-PAY")
        tds = round(sum(c.tds_amount or 0.0 for c in rows), 2)
        if tds > 0.005:
            entries.append(
                {
                    "name": "Statutory TDS Withheld (ITA 2023 s.140): %s" % run.name,
                    "account_id": _configured_account(self.env, company, "tds_payable").id,
                    "debit": 0.0,
                    "credit": tds,
                }
            )
            dims.append("CC-TAX")
        if line.amount > 0.005:
            pay = line.payment_execution_id.sudo()
            journal = pay and (
                (pay["released_journal_id"] if "released_journal_id" in pay._fields else False)
                or pay.journal_id
            )
            account = (journal.default_account_id if journal else False) or _configured_account(
                self.env, company, "clearing"
            )
            entries.append(
                {
                    "name": "Net Disbursed Funds via treasury: %s" % run.name,
                    "account_id": account.id,
                    "debit": 0.0,
                    "credit": round(line.amount, 2),
                }
            )
            dims.append("CC-TREAS")
        move, _ = post_with_dimensions(
            self.env,
            {
                "journal_id": _configured_journal(self.env, company).id,
                "company_id": company.id,
                "date": fields.Date.context_today(run),
                "ref": "PAYOUT-DISCHARGE-%s-%s" % (run.name, line.id),
                "line_ids": [(0, 0, vals) for vals in entries],
            },
            {
                i: {"operating_unit_id": run.operating_unit_id.id, "cost_centre": cc}
                for i, cc in enumerate(dims)
            },
            source="settlement",
        )
        line.sudo().write({"gl_move_id": move.id})
        if not run.gl_move_id:
            run._guarded().write({"gl_move_id": move.id})
        rows._guarded().write({"state": "paid"})
        return move

    def _finalize_payout_execution(self):
        """Finalize executed payout run: mark paid, generate bilingual statements, and post to GL."""
        self.ensure_one()
        run = self.sudo()
        if run.state == "executed":
            return
        # freeze the clawback recoveries BEFORE the run turns executed
        deductions = run._clawback_deductions()
        Recovery = self.env["fix.settlement.recovery"].sudo()
        for _payee, pairs in deductions.items():
            for claw, amount in pairs:
                Recovery.create(
                    {"adjustment_id": claw.id, "payout_run_id": run.id, "amount": amount}
                )
                if claw.remaining_amount <= 0.005:
                    claw._guarded().write({"state": "recovered"})
        run._guarded().write({"state": "executed"})
        run.commission_ids._guarded().write({"state": "paid"})

        # Generate bilingual statements for each seller (born draft, issued
        # by the system now that the money has moved)
        stmt_model = self.env["fix.seller.statement"].sudo()
        statements = stmt_model
        lines = run._fix_active_lines()
        for line in lines:
            comms = line.commission_ids
            clawback_tot = sum(amt for _c, amt in deductions.get(line.partner_id, []))
            statements |= stmt_model._guarded().create(
                {
                    "company_id": run.company_id.id,
                    "operating_unit_id": run.operating_unit_id.id,
                    "seller_partner_id": line.partner_id.id,
                    "payee_type": comms[:1].source_type or "marketplace",
                    "period": run.period,
                    "gross_gmv": sum(comms.mapped("gross_amount")),
                    "commission_amount": sum(comms.mapped("commission_amount")),
                    "tds_withheld": sum(c.tds_amount or 0.0 for c in comms),
                    "clawback_amount": clawback_tot,
                    "payout_run_id": run.id,
                }
            )
        statements.action_issue_statement()

        # Post payout execution to General Ledger
        run.action_post_payout_to_gl()

        publish(
            self.env,
            "payout.executed",
            "fix.payout.run",
            run.id,
            {
                "payout_run": run.name,
                "rail_type": run.rail_type,
                "rail_status": run.rail_status,
                "sellers_paid": len(lines),
                "total_disbursed": float(run.total_payable),
                "tds_withheld": float(run.total_tds),
            },
        )

    def _fix_disbursement_lines(self):
        """[(bank account, amount)] the disbursement credits: the GL account of
        each M50 instruction's paying bank journal (the clearing role when an
        instruction carries none, e.g. a legacy run)."""
        self.ensure_one()
        by_account: dict = {}
        fallback = None
        for line in self.line_ids.filtered(lambda ln: ln.amount > 0.005):
            pay = line.payment_execution_id.sudo()
            journal = pay and (
                (pay["released_journal_id"] if "released_journal_id" in pay._fields else False)
                or pay.journal_id
            )
            account = journal.default_account_id if journal else False
            if not account:
                fallback = fallback or _configured_account(self.env, self.company_id, "clearing")
                account = fallback
            by_account[account] = by_account.get(account, 0.0) + line.amount
        if not by_account and self.total_payable > 0.005:
            by_account[_configured_account(self.env, self.company_id, "clearing")] = (
                self.total_payable
            )
        return by_account

    def action_post_payout_to_gl(self):
        """Post payout discharge and statutory TDS withholding to General Ledger through M19.

        Only an EXECUTED run (bank-confirmed) is discharged, once. Each payee
        type clears its own payable (sellers 200200, partners the configured
        partner payable); clawbacks recovered in the run credit the
        customer-refund clearing account they reimburse; the net credits the
        bank account treasury paid from (M50 books nothing for a payout line,
        so the bank is credited once).

        A run paid through M50 discharges per payee line as each payment is
        confirmed (M53-1); this settles any line not yet posted (a payee whose
        net a clawback consumed). The aggregate entry below is only for runs
        paid before the pinned lines existed."""
        for rec in self:
            lines = rec._fix_active_lines()
            if lines and rec.state == "executed":
                for line in lines.filtered(lambda ln: not ln.gl_move_id):
                    rec._fix_post_line_discharge(line)
                continue
            if rec.gl_move_id:
                continue
            if rec.state != "executed":
                raise UserError(
                    "Payout %s is %s — only a confirmed (executed) payout is discharged in the GL"
                    % (rec.name, rec.state)
                )

            company = rec.company_id
            journal = _configured_journal(self.env, company)
            tds_payable = _configured_account(self.env, company, "tds_payable")

            by_role: dict[str, float] = {}
            for c in rec.commission_ids:
                role = c._payable_role()
                by_role[role] = by_role.get(role, 0.0) + c.net_payable + (c.tds_amount or 0.0)
            tds_withheld = rec.total_tds
            labels = {
                "seller_payable": "Discharge Seller Liability",
                "partner_payable": "Discharge Partner Commission Liability",
            }
            debit_lines = [
                (
                    0,
                    0,
                    {
                        "name": f"{labels[role]}: {rec.name}",
                        "account_id": _configured_account(self.env, company, role).id,
                        "debit": amount,
                        "credit": 0.0,
                    },
                )
                for role, amount in sorted(
                    by_role.items(), key=lambda kv: kv[0] != "seller_payable"
                )
            ]
            clawback_lines = []
            if rec.total_clawback > 0.005:
                recovery_acc = _configured_account(self.env, company, "clawback_recovery")
                clawback_lines.append(
                    (
                        0,
                        0,
                        {
                            "name": f"Clawbacks recovered: {rec.name}",
                            "account_id": recovery_acc.id,
                            "debit": 0.0,
                            "credit": rec.total_clawback,
                        },
                    )
                )
            tds_lines = []
            if tds_withheld > 0.005:
                tds_lines.append(
                    (
                        0,
                        0,
                        {
                            "name": f"Statutory TDS Withheld (ITA 2023 s.140): {rec.name}",
                            "account_id": tds_payable.id,
                            "debit": 0.0,
                            "credit": tds_withheld,
                        },
                    )
                )
            bank_lines = [
                (
                    0,
                    0,
                    {
                        "name": f"Net Disbursed Funds via treasury: {rec.name}",
                        "account_id": account.id,
                        "debit": 0.0,
                        "credit": round(amount, 2),
                    },
                )
                for account, amount in rec._fix_disbursement_lines().items()
            ]

            move_vals = {
                "journal_id": journal.id,
                "company_id": company.id,
                "date": fields.Date.context_today(rec),
                "ref": f"PAYOUT-DISCHARGE-{rec.name}",
                "line_ids": debit_lines + clawback_lines + tds_lines + bank_lines,
            }

            n_pay = len(debit_lines) + len(clawback_lines)
            dim_by_line = {
                i: {"operating_unit_id": rec.operating_unit_id.id, "cost_centre": "CC-PAY"}
                for i in range(n_pay)
            }
            for i in range(n_pay, n_pay + len(tds_lines)):
                dim_by_line[i] = {
                    "operating_unit_id": rec.operating_unit_id.id,
                    "cost_centre": "CC-TAX",
                }
            for i in range(n_pay + len(tds_lines), n_pay + len(tds_lines) + len(bank_lines)):
                dim_by_line[i] = {
                    "operating_unit_id": rec.operating_unit_id.id,
                    "cost_centre": "CC-TREAS",
                }

            move, _ = post_with_dimensions(self.env, move_vals, dim_by_line, source="settlement")
            rec._guarded().write({"gl_move_id": move.id})

    def action_cancel(self):
        """Abandon a run that has not been released to treasury."""
        require_role(self.env, GROUP_ACCOUNTANT, "Cancelling a payout run")
        for run in self:
            if run.state not in ("draft", "prepared", "approved"):
                raise UserError(
                    "Payout run %s was released to treasury: it is not cancelled here." % run.name
                )
            run._fin_void("the payout run was cancelled")
            run._guarded().write({"state": "cancelled"})
        return True


class FixPayoutRunLine(models.Model):
    """One payee of an approved payout run, pinned at approval (F2): the
    account and its number, the amount. The M50 instruction pays this line,
    once (fix.payment.execution is unique per source)."""

    _name = "fix.payout.run.line"
    _description = "Payout Run Payee Line (pinned)"
    _order = "run_id, id"
    # M50 posts nothing for this source: the payout run books the discharge.
    _fix_posts_own_payment = True

    run_id = fields.Many2one("fix.payout.run", required=True, ondelete="restrict", index=True)
    company_id = fields.Many2one(related="run_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(related="run_id.operating_unit_id", store=True)
    currency_id = fields.Many2one(related="run_id.currency_id")
    partner_id = fields.Many2one("res.partner", string="Payee", required=True, readonly=True)
    partner_bank_id = fields.Many2one("res.partner.bank", string="Approved Account", readonly=True)
    acc_number = fields.Char(string="Approved Account No", readonly=True)
    routing_number = fields.Char(string="Approved Routing No", readonly=True)
    amount = fields.Monetary(string="Net Paid", currency_field="currency_id", readonly=True)
    tds_amount = fields.Monetary(string="TDS", currency_field="currency_id", readonly=True)
    gross_amount = fields.Monetary(string="Gross", currency_field="currency_id", readonly=True)
    commission_ids = fields.Many2many(
        "fix.commission.ledger",
        "fix_payout_run_line_commission_rel",
        "line_id",
        "commission_id",
        string="Commissions",
        readonly=True,
    )
    payment_execution_id = fields.Many2one(
        "fix.payment.execution", string="Treasury Instruction", readonly=True
    )
    payment_state = fields.Selection(related="payment_execution_id.state", string="Payment")
    gl_move_id = fields.Many2one("account.move", string="GL Discharge", readonly=True, copy=False)
    superseded = fields.Boolean(
        string="Replaced / Dropped",
        readonly=True,
        copy=False,
        help="This line no longer pays: its cancelled instruction was re-requested on a new "
        "line, or the payee was dropped from the run (M53-1).",
    )
    superseded_reason = fields.Char(string="Why Replaced / Dropped", readonly=True, copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            raise UserError("Payee lines are pinned by the payout approval, never typed.")
        return super().create(vals_list)

    def write(self, vals):
        if not self.env.su:
            raise UserError("A pinned payee line is never edited (F2).")
        allowed = {"payment_execution_id", "gl_move_id", "superseded", "superseded_reason"}
        if set(vals) - allowed and self.filtered("payment_execution_id"):
            raise UserError("A payee line released to treasury is never edited (F2).")
        return super().write(vals)


class FixPaymentExecutionPayout(models.Model):
    """The M50 instruction of a payout line reports its outcome to the run."""

    _inherit = "fix.payment.execution"

    def write(self, vals):
        result = super().write(vals)
        if "state" in vals:
            lines = self.sudo().filtered(lambda p: p.source_model == "fix.payout.run.line")
            if lines:
                runs = (
                    self.env["fix.payout.run.line"]
                    .sudo()
                    .browse(lines.mapped("source_id"))
                    .exists()
                    .mapped("run_id")
                )
                runs._fix_sync_payments()
        return result


__all__ = ["GROUP_ADMINISTRATOR"]
