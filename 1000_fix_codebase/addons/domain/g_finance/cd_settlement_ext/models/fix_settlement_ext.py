# fix_settlement_ext — M53 W7: commission ledger + payout runs (P10-M02 / R08-M02).
from __future__ import annotations

import base64
import uuid
from decimal import Decimal

from odoo import api, fields, models
from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions
from odoo.exceptions import AccessError, UserError

from libs.py.fix_events import publish
from libs.py.payout_rail import (
    INT007PayoutRail,
    PayoutBatchRequest,
    PayoutRecipient,
    PayoutStatus,
)

# Settlement GL accounts by role: (default code, label). The code is looked up
# in the company's chart; a database may override it with the system
# parameter ``cd_settlement_ext.account_code.<role>``.
# NOTE: 210100 is also the VAT Output Payable code cd_tax_engine_bd reconciles
# against; a chart that keeps TDS separate must override ``tds_payable``.
SETTLEMENT_ACCOUNTS = {
    "clearing": ("101000", "Customer Payment Clearing / Disbursement Bank"),
    "commission_revenue": ("400100", "Marketplace Commission Revenue"),
    "seller_payable": ("200200", "Marketplace Seller Payable"),
    "tds_payable": ("210100", "TDS Withheld Liability (ITA 2023 §52)"),
}


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


def _bank_details(partner) -> tuple[str, str]:
    """(account number, routing number) of the partner's first bank account,
    exactly as recorded — empty strings when absent, never a default."""
    bank = partner.bank_ids[:1]
    return (bank.acc_number or "").strip(), (bank.bank_id.bic or "").strip()


def _is_routing(routing: str) -> bool:
    """A Bangladesh BEFTN routing number: exactly 9 ASCII digits."""
    return len(routing) == 9 and routing.isascii() and routing.isdigit()


class FixCommissionLedger(models.Model):
    """M53 W7: commission ledger consuming commission.earned events.
    The M12<->M53 break: M53 CONSUMES events; M12 never calls M53.
    Enforces FF-91: Marketplace gross is NEVER posted to revenue!"""

    _name = "fix.commission.ledger"
    _description = "Commission Ledger Entry"
    _inherit = ["mail.thread", "mail.activity.mixin"]
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
    tds_amount = fields.Monetary(string="TDS Withheld (ITA 2023 §52)", currency_field="currency_id")
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
        ],
        default="earned",
        required=True,
        tracking=True,
    )

    # Four reconciliation keys required by LP-02 (IN-007 §5.1, §10.2)
    payment_id = fields.Char(string="Payment ID", copy=False, index=True)
    rail = fields.Char(string="Payment Rail", default="bKash")
    rail_transaction_id = fields.Char(string="Rail Transaction ID", copy=False, index=True)
    merchant_invoice_number = fields.Char(string="Merchant Invoice Ref", copy=False, index=True)

    gl_move_id = fields.Many2one(
        "account.move", string="General Ledger Move", readonly=True, copy=False
    )

    @api.depends("gross_amount", "commission_rate")
    def _compute_commission(self):
        for rec in self:
            rec.commission_amount = rec.gross_amount * rec.commission_rate

    @api.depends("gross_amount", "commission_amount", "tds_amount")
    def _compute_net(self):
        for rec in self:
            # Seller entitlement = Gross GMV - Commission Earned - TDS Withheld
            rec.net_payable = rec.gross_amount - rec.commission_amount - (rec.tds_amount or 0.0)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.commission.ledger")
                    or f"COM/{fields.Date.today().year}/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        for rec in self:
            if rec.state in ("accrued", "paid") and not self.env.su:
                # Reversible only by contra-posting per LP-07
                restricted_fields = {
                    "gross_amount",
                    "commission_rate",
                    "commission_amount",
                    "seller_partner_id",
                }
                if any(f in vals for f in restricted_fields):
                    raise UserError(
                        "LP-07 Violation: Accrued commission entries cannot be modified. Use contra-posting."
                    )
        return super().write(vals)

    def action_post_to_gl(self):
        """Post commission accrual to GL through M19 (cd_gl_ext).
        Strictly enforces FF-91 (MS-01):
        - Marketplace gross is NEVER booked to revenue!
        - Commission Earned is credited to Revenue (400100).
        - Seller Share is credited to Liability (200200).
        - Customer Clearing / Bank is debited (101000)."""
        for rec in self:
            if rec.state != "earned":
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

            move, _ = post_with_dimensions(self.env, move_vals, dim_by_line)
            rec.write(
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


class FixPayoutRun(models.Model):
    """Payout run: money to 500-2,000 sellers.
    Enforces two-person Segregation of Duties (SoD) gate, INT-007 multi-rail dispatch,
    7-day idempotency, first-class unknown state (FF-85), and BEFTN fallback."""

    _name = "fix.payout.run"
    _description = "Payout Run / পরিশোধ চক্র"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "period desc, id desc"

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
            ("approved", "Approved (SoD Verified) / অনুমোদিত"),
            ("executing", "Executing / চলমান"),
            ("file_generated", "BEFTN File Generated (Unconfirmed) / ফাইল তৈরি"),
            ("executed", "Executed / সমাপ্ত"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )

    # Segregation of Duties fields
    prepared_by_id = fields.Many2one(
        "res.users", string="Prepared By", default=lambda self: self.env.user, readonly=True
    )
    approved_by_id = fields.Many2one("res.users", string="Approved By", readonly=True)
    approved_date = fields.Datetime(string="Approved Date", readonly=True)
    sod_verified = fields.Boolean(string="SoD Verified", readonly=True, default=False)

    commission_ids = fields.Many2many("fix.commission.ledger", string="Commissions")

    # INT-007 Payout Rail Integration Fields
    idempotency_key = fields.Char(string="Idempotency Key (7-Day TTL)", copy=False, readonly=True)
    rail_type = fields.Selection(
        [
            ("api", "Direct API (Mobile Money / Bank Gateway)"),
            ("beftn", "BEFTN Standard Batch File (128-byte)"),
        ],
        string="Disbursement Rail",
        default="api",
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
        tracking=True,
        help="The reference the BANK issued for this disbursement (BEFTN settlement / "
        "bank statement reference), entered by a finance manager. Required to "
        "confirm a payout that has no confirmed rail response.",
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

    @api.depends(
        "commission_ids.net_payable", "commission_ids.tds_amount", "commission_ids.gross_amount"
    )
    def _compute_total(self):
        for rec in self:
            rec.total_payable = sum(rec.commission_ids.mapped("net_payable"))
            rec.total_tds = sum(rec.commission_ids.mapped("tds_amount"))
            rec.total_gross = sum(rec.commission_ids.mapped("gross_amount"))
            rec.seller_count = len(rec.commission_ids.mapped("seller_partner_id"))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.payout.run")
                    or f"PAY/{fields.Date.today().year}/New"
                )
        return super().create(vals_list)

    def action_approve(self):
        """Two-person Segregation of Duties (SoD) gate.
        Rule 1: Preparer cannot approve their own payout run.
        Rule 2: Approver must possess financial managerial authority."""
        for rec in self:
            if not rec.commission_ids:
                raise UserError("No commissions attached to this payout run.")
            if rec.prepared_by_id and self.env.user.id == rec.prepared_by_id.id:
                raise UserError("SoD Violation: Preparer cannot approve their own payout run.")
            if not (
                self.env.user.has_group("account.group_account_manager")
                or self.env.user.has_group("base.group_system")
            ):
                raise AccessError("SoD Violation: Only Finance Managers can approve payout runs.")

            rec.write(
                {
                    "state": "approved",
                    "approved_by_id": self.env.user.id,
                    "approved_date": fields.Datetime.now(),
                    "sod_verified": True,
                }
            )
            publish(
                self.env,
                "payout.approved",
                "fix.payout.run",
                rec.id,
                {
                    "payout_run": rec.name,
                    "total_payable": float(rec.total_payable),
                    "total_tds": float(rec.total_tds),
                    "seller_count": rec.seller_count,
                    "approved_by": self.env.user.name,
                },
            )

    def action_execute(self):
        """Execute payout run (alias for action_submit_payout)."""
        for rec in self:
            if rec.state != "approved":
                raise UserError("Approve before executing")
        return self.action_submit_payout()

    def _check_bank_details(self) -> None:
        """Refuse the payout unless EVERY party has real bank details: the
        paying company (originating account) and each seller (beneficiary).

        Nothing is ever defaulted — the former fallbacks paid a seller with
        no account into a placeholder account through the sponsor routing
        number, and the rail's BEFTN header carried a library-default
        originating routing. All gaps are listed in one named error."""
        self.ensure_one()
        problems = []
        parties = [("company", self.company_id.partner_id, self.company_id.name)] + [
            ("seller", seller, seller.name)
            for seller in self.commission_ids.mapped("seller_partner_id")
        ]
        for role, partner, name in parties:
            acc_num, routing = _bank_details(partner)
            if not acc_num:
                problems.append("%s %s: no bank account" % (role, name))
            elif not _is_routing(routing):
                problems.append(
                    "%s %s: routing %r is not a 9-digit BEFTN routing number"
                    % (role, name, routing)
                )
        if problems:
            raise UserError(
                "Payout %s refused — bank details missing or invalid for: %s"
                % (self.name, "; ".join(problems))
            )

    def _default_rail(self) -> INT007PayoutRail:
        """The INT-007 rail originating from the company's OWN bank account."""
        company = self.company_id
        return INT007PayoutRail(
            originating_routing=_bank_details(company.partner_id)[1],
            company_name=company.name,
            company_id=company.company_registry or company.vat or str(company.id),
        )

    def _prepare_payout_recipients(self) -> list[PayoutRecipient]:
        self.ensure_one()
        self._check_bank_details()
        # Aggregate net payable per seller
        seller_totals: dict[models.Model, dict] = {}
        for c in self.commission_ids:
            seller = c.seller_partner_id
            if seller not in seller_totals:
                seller_totals[seller] = {
                    "net_payable": Decimal("0.00"),
                    "gross": Decimal("0.00"),
                    "tds": Decimal("0.00"),
                    "comm": Decimal("0.00"),
                }
            seller_totals[seller]["net_payable"] += Decimal(str(c.net_payable))
            seller_totals[seller]["gross"] += Decimal(str(c.gross_amount))
            seller_totals[seller]["tds"] += Decimal(str(c.tds_amount or 0.0))
            seller_totals[seller]["comm"] += Decimal(str(c.commission_amount))

        recipients = []
        for seller, amounts in seller_totals.items():
            acc_num, routing = _bank_details(seller)  # validated: never invented
            recipients.append(
                PayoutRecipient(
                    seller_ref=f"SLR-{seller.id:04d}",
                    seller_name=seller.name,
                    account_number=acc_num,
                    routing_number=routing,
                    amount_bdt=amounts["net_payable"],
                    disbursement_ref=f"DISB-{self.name}-{seller.id}",
                )
            )
        return recipients

    def action_submit_payout(self, simulate_timeout=False, rail_instance=None):
        """Submit payout batch to INT-007 seller payout rail with 7-day idempotency."""
        for rec in self:
            if rec.state != "approved":
                raise UserError(
                    "Payout run must be SoD-approved before dispatching to payout rail."
                )

            if not rec.idempotency_key:
                rec.idempotency_key = f"IDEMP-{rec.name}-{uuid.uuid4().hex[:12]}"

            recipients = rec._prepare_payout_recipients()
            req = PayoutBatchRequest(
                batch_ref=rec.name,
                period=rec.period,
                recipients=tuple(recipients),
                idempotency_key=rec.idempotency_key,
                total_amount=Decimal(str(rec.total_payable)),
                recipient_count=len(recipients),
            )

            rail = rail_instance or rec._default_rail()
            result = rail.submit_payout_batch(
                req, rail_type="api", simulate_timeout=simulate_timeout
            )

            rec.write(
                {
                    "rail_batch_id": result.rail_batch_id,
                    "rail_status": result.status.value,
                }
            )

            if result.status == PayoutStatus.CONFIRMED:
                rec._finalize_payout_execution()
            elif result.status == PayoutStatus.UNKNOWN:
                rec.state = "executing"
                # IN-007 §3.4: Customer/seller sees 'We are confirming payment', not 'failed'

    def action_query_status(self, rail_instance=None):
        """Read-back query resolving UNKNOWN state (IN-007 §5.4, FF-85).

        Only a REAL bank response may resolve the run. A rail exposes that as
        ``query_bank_status(batch_ref, rail_batch_id)`` returning an object
        with ``status`` (PayoutStatus) and ``bank_reference``. The INT-007
        library rail has no such bank query — its ``read_back_status`` takes
        the outcome from the CALLER (this method used to pass CONFIRMED and so
        finalised every timed-out payout as paid). Without a bank response the
        run stays ``pending_bank_confirmation`` until a finance manager
        records the bank's reference (action_confirm_bank_settlement)."""
        for rec in self:
            if not rec.rail_batch_id:
                raise UserError("No rail batch reference recorded to query.")

            rail = rail_instance or rec._default_rail()
            query = getattr(rail, "query_bank_status", None)
            response = query(rec.name, rec.rail_batch_id) if query else None
            status = getattr(response, "status", None)
            bank_ref = (getattr(response, "bank_reference", "") or "").strip()

            if status == PayoutStatus.CONFIRMED and bank_ref:
                rec.write({"rail_status": "confirmed", "bank_confirmation_ref": bank_ref})
                rec._finalize_payout_execution()
            elif status == PayoutStatus.FAILED:
                rec.rail_status = "failed"
            else:
                if rec.rail_status != "failed":
                    rec.rail_status = "pending_bank_confirmation"
                rec.message_post(
                    body="Read-back: no bank response available for rail batch %s — payout "
                    "remains pending bank confirmation (not marked paid)." % rec.rail_batch_id
                )

    def action_generate_beftn(self, rail_instance=None):
        """Generate the BEFTN standard 128-byte batch file (fallback rail).

        Generating the file disburses nothing: the file still has to be
        uploaded to the sponsor bank and settled through BEFTN. The run moves
        to ``file_generated`` — commissions stay unpaid and no disbursement is
        posted to the GL until a finance manager records the bank's settlement
        reference (action_confirm_bank_settlement). It previously marked the
        payout confirmed, commissions paid and posted the GL discharge."""
        for rec in self:
            if rec.state != "approved":
                raise UserError("Approve payout run before generating BEFTN fallback file.")

            if not rec.idempotency_key:
                rec.idempotency_key = f"IDEMP-BEFTN-{rec.name}-{uuid.uuid4().hex[:12]}"

            recipients = rec._prepare_payout_recipients()
            req = PayoutBatchRequest(
                batch_ref=rec.name,
                period=rec.period,
                recipients=tuple(recipients),
                idempotency_key=rec.idempotency_key,
                total_amount=Decimal(str(rec.total_payable)),
                recipient_count=len(recipients),
            )

            rail = rail_instance or rec._default_rail()
            result = rail.generate_beftn_fallback_batch(req)

            file_bytes = result.beftn_raw.encode("ascii")
            rec.write(
                {
                    "state": "file_generated",
                    "rail_type": "beftn",
                    "rail_status": "file_generated",
                    "rail_batch_id": result.rail_batch_id,
                    "beftn_file": base64.b64encode(file_bytes),
                    "beftn_filename": f"BEFTN_{rec.name.replace('/', '_')}.txt",
                }
            )

    def action_confirm_bank_settlement(self, bank_reference: str = ""):
        """Record the BANK's confirmation of a disbursement and finalise the run.

        The only route to ``executed`` for a payout without a confirmed rail
        response (BEFTN file runs, timed-out / pending API runs). Requires the
        bank-issued settlement reference — passed in, or entered on the run's
        ``bank_confirmation_ref`` field — and a finance manager."""
        if not (
            self.env.user.has_group("account.group_account_manager")
            or self.env.user.has_group("base.group_system")
        ):
            raise AccessError("Only Finance Managers can confirm a bank settlement.")
        for rec in self:
            if rec.state not in ("executing", "file_generated"):
                raise UserError(
                    "Payout %s is not awaiting bank confirmation (state: %s)."
                    % (rec.name, rec.state)
                )
            if rec.rail_status == "failed":
                raise UserError(
                    "The rail reported payout %s as FAILED; it cannot be confirmed." % rec.name
                )
            ref = (bank_reference or rec.bank_confirmation_ref or "").strip()
            if not ref:
                raise UserError(
                    "Enter the bank's settlement reference for payout %s before confirming "
                    "it — a disbursement is never confirmed without the bank's evidence." % rec.name
                )
            rec.write(
                {
                    "bank_confirmation_ref": ref,
                    "bank_confirmed_by_id": self.env.user.id,
                    "bank_confirmed_at": fields.Datetime.now(),
                    "rail_status": "confirmed",
                }
            )
            rec._finalize_payout_execution()

    def _finalize_payout_execution(self):
        """Finalize executed payout run: mark paid, generate bilingual statements, and post to GL."""
        self.ensure_one()
        self.state = "executed"
        self.commission_ids.write({"state": "paid"})

        # Generate bilingual statements for each seller
        stmt_model = self.env["fix.seller.statement"]
        seller_groups: dict[models.Model, list] = {}
        for c in self.commission_ids:
            seller_groups.setdefault(c.seller_partner_id, []).append(c)

        for seq, (seller, comms) in enumerate(seller_groups.items(), start=1):
            gross_tot = sum(c.gross_amount for c in comms)
            comm_tot = sum(c.commission_amount for c in comms)
            tds_tot = sum(c.tds_amount or 0.0 for c in comms)
            net_tot = sum(c.net_payable for c in comms)
            cert_ref = f"NBR-TDS52-{fields.Date.today().year}-{seller.id:04d}-{seq:04d}"

            stmt_model.create(
                {
                    "company_id": self.company_id.id,
                    "operating_unit_id": self.operating_unit_id.id,
                    "seller_partner_id": seller.id,
                    "period": self.period,
                    "gross_gmv": gross_tot,
                    "commission_amount": comm_tot,
                    "tds_withheld": tds_tot,
                    "net_payable": net_tot,
                    "withholding_cert_ref": cert_ref,
                    "payout_run_id": self.id,
                    "state": "issued",
                }
            )

        # Post payout execution to General Ledger
        self.action_post_payout_to_gl()

        publish(
            self.env,
            "payout.executed",
            "fix.payout.run",
            self.id,
            {
                "payout_run": self.name,
                "rail_type": self.rail_type,
                "rail_status": self.rail_status,
                "sellers_paid": len(seller_groups),
                "total_disbursed": float(self.total_payable),
                "tds_withheld": float(self.total_tds),
            },
        )

    def action_post_payout_to_gl(self):
        """Post payout discharge and statutory TDS withholding to General Ledger through M19."""
        for rec in self:
            if rec.gl_move_id:
                continue

            company = rec.company_id
            journal = _configured_journal(self.env, company)
            # Account codes per SETTLEMENT_ACCOUNTS: seller payable 200200,
            # TDS 210100 (ITA 2023 §52), disbursement bank 101000.
            seller_payable = _configured_account(self.env, company, "seller_payable")
            tds_payable = _configured_account(self.env, company, "tds_payable")
            disbursement_bank = _configured_account(self.env, company, "clearing")

            total_seller_liability = rec.total_payable + rec.total_tds
            net_disbursed = rec.total_payable
            tds_withheld = rec.total_tds

            move_vals = {
                "journal_id": journal.id,
                "company_id": company.id,
                "date": fields.Date.context_today(rec),
                "ref": f"PAYOUT-DISCHARGE-{rec.name}",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": f"Discharge Seller Liability: {rec.name}",
                            "account_id": seller_payable.id,
                            "debit": total_seller_liability,
                            "credit": 0.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": f"Statutory TDS Withheld (ITA 2023 §52): {rec.name}",
                            "account_id": tds_payable.id,
                            "debit": 0.0,
                            "credit": tds_withheld,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": f"Net Disbursed Funds via {rec.rail_type}: {rec.name}",
                            "account_id": disbursement_bank.id,
                            "debit": 0.0,
                            "credit": net_disbursed,
                        },
                    ),
                ],
            }

            dim_by_line = {
                0: {"operating_unit_id": rec.operating_unit_id.id, "cost_centre": "CC-PAY"},
                1: {"operating_unit_id": rec.operating_unit_id.id, "cost_centre": "CC-TAX"},
                2: {"operating_unit_id": rec.operating_unit_id.id, "cost_centre": "CC-TREAS"},
            }

            move, _ = post_with_dimensions(self.env, move_vals, dim_by_line)
            rec.gl_move_id = move.id
