# cd_front_desk_finance — the counter sale's hand-off to the books.
#
# E2E2 flow 2 (11 Nov 2026, copy of fix_real): fix.counter.sale.action_confirm
# wrote a state, an M63 number and the drawer total, nothing else. Three sales
# left no GL entry, no stock movement and no Mushak register row; their output
# VAT (652.18) appeared nowhere, and the M50 deposit credited the drawer cash
# account (100108) for takings never debited to it.
#
# A confirmed sale now posts three legs through the estate's own engines, as
# the system on the cashier's behalf (she holds no accounting role):
#   vat    the Mushak 6.3, written by the VAT register's issuing service
#          (fix.mushak.register._fix_issue_register_row) and numbered from the
#          billing engine's statutory per-company series — the AR invoice path.
#          The VAT is M51's determination at the Tax Rate Master's rate.
#   gl     Dr drawer cash / MFS clearing / card clearing, Cr parts or labour
#          revenue, Cr VAT output, posted through M19 (_fix_post_via_m19:
#          chart rules, dimensions, posting log); the 6.3 is marked posted
#          with it (T08).
#   stock  a part leaves the M15 ledger at its bucket's average cost and books
#          its valuation suspense row, as every other issue does.
# A refund approved from the M63 inbox reverses what was posted: a Mushak 6.7
# against the 6.3, the mirror GL entry, the part back into stock (quarantine
# when returned defective).
#
# Fail closed, never blocking (the fix.inventory.valuation.suspense
# pending_gl_cutover pattern): a leg that cannot post — an account that does
# not resolve, a location nobody named — is rolled back on its own savepoint;
# the sale stays confirmed, is marked pending with the reason, and the retry
# button or the hourly job posts it once the cause is fixed. Each leg checks
# its own link before acting and the sale row is locked while it posts, so
# nothing ever posts twice.
from __future__ import annotations

import logging
from decimal import ROUND_HALF_UP, Decimal

from odoo import api, fields, models
from odoo.addons.cd_billing_engine.models.fix_ar_engine import AR_ACCOUNTS, _ar_journal
from odoo.addons.cd_billing_engine.models.fix_billing_engine import (
    _issue_mushak_row,
    m51_determine,
)
from odoo.addons.cd_front_desk.models.fix_cash_shift import GROUP_CASHIER, GROUP_MANAGER
from odoo.addons.cd_front_desk.models.fix_workstation_ext import (
    GROUP_REFUND_APPROVER,
    REFUND_REASONS,
)
from odoo.addons.cd_inventory.models.fix_inventory_approval import (
    COST_GROUP,
    check_quantity,
    location_class,
)
from odoo.addons.cd_tax_engine_bd.models import tax_logic
from odoo.addons.cd_tax_engine_bd.models.fix_tax_engine import normalize_bin, valid_bin
from odoo.exceptions import UserError

from .fix_engine_ext import SOURCE

_logger = logging.getLogger(__name__)

CENT = Decimal("0.01")
DHAKA = "Asia/Dhaka"
WALK_IN = "Walk-in customer (counter sale)"

# ------------------------------------------------------------------ accounts
# Each role reads its keys in order; the FIRST key that is set decides (a
# configured code that is not in the chart fails closed, it never falls
# through to a guess). The fallbacks are the accounts the estate already
# uses for the same money: the AR invoice's revenue and VAT output, the
# drawer account the M50 deposit credits, the channel clearing that AR
# receipts debit for bKash / Nagad / card and M50 settles to bank.
PARAM = "cd_front_desk_finance.account_code."
BILLING = "cd_billing_engine.account_code."
DRAWER_PARAM = "cd_cash_position.account_code.branch_cash"
CHANNEL_PARAM = "cd_cash_position.account_code.channel_clearing"
SHORTAGE_PARAM = "cd_cash_position.account_code.cash_shortage"
ACCOUNT_ROLES = {
    "parts_revenue": ("parts revenue", (PARAM + "parts_revenue", BILLING + "revenue")),
    "labour_revenue": ("labour / service revenue", (PARAM + "labour_revenue", BILLING + "revenue")),
    "mfs_clearing": (
        "bKash / Nagad clearing",
        (PARAM + "mfs_clearing", CHANNEL_PARAM, BILLING + "channel_mfs"),
    ),
    "card_clearing": (
        "card (POS) clearing",
        (PARAM + "card_clearing", CHANNEL_PARAM, BILLING + "channel_mfs"),
    ),
    # the drawer is the account the M50 deposit credits: one key, both sides
    "drawer_cash": (
        "drawer cash (the account the M50 deposit credits)",
        (DRAWER_PARAM, BILLING + "cash"),
    ),
    "vat_output": ("VAT output (Mushak 6.3)", (BILLING + "vat_output",)),
    # the reconciled drawer variance (fix_cash_shift_posting): the treasury's
    # "Cash shortage / over" account, where M50 already books deposit overs;
    # an overage goes to its own account once one is named
    "cash_shortage": ("cash shortage (drawer short)", (SHORTAGE_PARAM,)),
    "cash_overage": (
        "cash overage (drawer over)",
        (PARAM + "cash_overage", SHORTAGE_PARAM),
    ),
}
PAYMENT_ROLE = {
    "cash": "drawer_cash",
    "bkash": "mfs_clearing",
    "nagad": "mfs_clearing",
    # quote-to-cash P2 (13 Nov 2026): the other MFS wallets clear the same way
    "rocket": "mfs_clearing",
    "upay": "mfs_clearing",
    "card": "card_clearing",
}

POSTING_STATES = [
    ("none", "Nothing to Post"),
    ("pending", "Pending Posting"),
    ("posted", "Posted"),
    ("reversal_pending", "Refund Reversal Pending"),
    ("reversed", "Refund Reversed"),
]
STOCK_STATES = [
    ("none", "Not Evaluated"),
    ("not_required", "No Stock Item"),
    ("pending", "Pending"),
    ("issued", "Issued"),
    ("returned", "Returned"),
    ("cancelled", "Not Needed (refunded before issue)"),
]
LEG_LABELS = {
    "vat": "Mushak 6.3",
    "gl": "GL entry",
    "stock": "Stock issue",
    "vat_reverse": "Mushak 6.7",
    "gl_reverse": "Refund GL entry",
    "stock_reverse": "Stock return",
}
# A cashier, a branch manager, a refund approver or finance may ask for a
# retry: it posts nothing but what the rules already say.
RETRY_GROUPS = (
    GROUP_CASHIER,
    GROUP_MANAGER,
    GROUP_REFUND_APPROVER,
    "account.group_account_user",
    "account.group_account_manager",
)
POSTING_FIELDS = {
    "posting_state",
    "posting_note",
    "posting_attempted_at",
    "vat_taxable_amount",
    "vat_output_amount",
    "vat_treatment_summary",
    "mushak_id",
    "mushak_note_id",
    "gl_move_id",
    "gl_reversal_move_id",
    "revenue_account_id",
    "payment_account_id",
    "stock_state",
    "stock_part_id",
    "stock_ownership_class",
    "stock_unit_cost",
    "stock_lot_id",
}


def resolve_account(env, company, role):
    """(account, None) or (empty account, the reason and the key to set)."""
    label, chain = ACCOUNT_ROLES[role]
    params = env["ir.config_parameter"].sudo()
    key, code = chain[-1], ""
    for key in chain:
        code = (params.get_param(key) or "").strip()
        if code:
            break
    else:
        if key.startswith(BILLING):
            # the billing engine's own default for its role: what AR invoices use
            code = AR_ACCOUNTS[key[len(BILLING) :]][0] or ""
    Account = env["account.account"].sudo()
    if code:
        account = Account.with_company(company).search(
            [("code", "=", code), ("company_ids", "in", company.id)], limit=1
        )
        if account:
            return account, None
        why = "%s names %s, which is not an account of %s" % (key, code, company.name)
    else:
        why = "no account is configured"
    return Account, "No GL account for %s: %s. Set the system parameter %s to the account code." % (
        label,
        why,
        chain[0],
    )


def _message(exc) -> str:
    return str(exc.args[0]) if getattr(exc, "args", None) else str(exc)


class FixCounterSalePosting(models.Model):
    _inherit = "fix.counter.sale"

    posting_state = fields.Selection(
        POSTING_STATES,
        string="Books",
        default="none",
        required=True,
        readonly=True,
        copy=False,
        index=True,
        help="Whether the sale (and its refund) reached the VAT register, the GL and the "
        "stock ledger. Pending: something could not post yet — see the note; the hourly job "
        "and Retry Posting post it once the cause is fixed.",
    )
    posting_note = fields.Text(string="Posting Note", readonly=True, copy=False)
    posting_attempted_at = fields.Datetime(string="Last Posting Run", readonly=True, copy=False)
    vat_taxable_amount = fields.Float(
        string="Mushak 6.3 Taxable Value (BDT)", readonly=True, copy=False
    )
    vat_output_amount = fields.Float(string="Mushak 6.3 VAT (BDT)", readonly=True, copy=False)
    vat_treatment_summary = fields.Char(string="VAT Treatment", readonly=True, copy=False)
    mushak_id = fields.Many2one(
        "fix.mushak.register",
        string="Mushak 6.3",
        readonly=True,
        copy=False,
        index=True,
        ondelete="restrict",
        help="The statutory VAT register row of this sale (the AR invoice path).",
    )
    mushak_no = fields.Char(related="mushak_id.mushak_no", string="Mushak 6.3 No.")
    mushak_note_id = fields.Many2one(
        "fix.mushak.register",
        string="Mushak 6.7 (Refund)",
        readonly=True,
        copy=False,
        ondelete="restrict",
    )
    gl_move_id = fields.Many2one(
        "account.move", string="Sale GL Entry", readonly=True, copy=False, index=True
    )
    gl_reversal_move_id = fields.Many2one(
        "account.move", string="Refund GL Entry", readonly=True, copy=False
    )
    revenue_account_id = fields.Many2one(
        "account.account", string="Revenue Account", readonly=True, copy=False
    )
    payment_account_id = fields.Many2one(
        "account.account",
        string="Payment Account",
        readonly=True,
        copy=False,
        help="Drawer cash, MFS clearing or card clearing — the account the sale debited.",
    )
    stock_state = fields.Selection(
        STOCK_STATES, string="Stock", default="none", required=True, readonly=True, copy=False
    )
    stock_location_id = fields.Many2one(
        "fix.stock.location",
        string="Issue From Location",
        copy=False,
        index=True,
        help="The M15 location the part leaves. Empty: the branch's counter stock location, "
        "else the one branch location holding the part.",
    )
    stock_part_id = fields.Many2one(
        "fix.spare.part", string="Spare Part", readonly=True, copy=False
    )
    stock_ownership_class = fields.Char(string="Issued From Class", readonly=True, copy=False)
    stock_unit_cost = fields.Float(
        string="Issue Unit Cost (BDT)", readonly=True, copy=False, groups=COST_GROUP
    )
    stock_lot_id = fields.Many2one(
        "fix.stock.lot", string="Issued Serial", readonly=True, copy=False
    )

    def _fix_guarded_fields(self) -> set:
        # the posting outcome is the system's: nobody types it
        return super()._fix_guarded_fields() | POSTING_FIELDS

    def write(self, vals):
        moving = {"stock_location_id", "serial_or_warranty_ref"} & set(vals)
        if moving and not self.env.su:
            for sale in self:
                done = sale.stock_state in ("issued", "returned", "cancelled")
                if (done or sale.state == "refunded") and any(
                    sale._fix_guard_differs(k, vals[k], sale[k]) for k in moving
                ):
                    raise UserError(
                        "Sale %s: its stock is already %s; the issue location and serial can "
                        "no longer change."
                        % (sale.name, dict(STOCK_STATES)[sale.stock_state].lower())
                    )
        return super().write(vals)

    @api.ondelete(at_uninstall=False)
    def _unlink_except_in_the_books(self):
        for sale in self:
            if sale.mushak_id or sale.gl_move_id or sale.stock_state in ("issued", "returned"):
                raise UserError(
                    "Counter sale %s is in the books (Mushak 6.3, GL or stock): it is refunded, "
                    "never deleted." % sale.name
                )

    # ------------------------------------------------------------ transitions
    def action_confirm(self):
        result = super().action_confirm()
        self._cdff_post()
        return result

    def action_approve_refund(self):
        result = super().action_approve_refund()
        self._cdff_post()
        return result

    def action_retry_posting(self):
        """Post whatever the sale still owes the books (idempotent)."""
        if not (self.env.su or any(self.env.user.has_group(g) for g in RETRY_GROUPS)):
            raise UserError("Only front-desk or finance staff may retry a counter sale's posting.")
        self._cdff_post()
        return True

    @api.model
    def _cron_retry_counter_postings(self, limit=200):
        """Hourly: post every sale still pending, oldest attempt first. A sale
        confirmed before this bridge was installed is posted the same way."""
        sales = self.sudo().search(
            [
                ("state", "!=", "draft"),
                ("posting_state", "in", ("none", "pending", "reversal_pending")),
            ],
            order="posting_attempted_at asc, id asc",
            limit=limit,
        )
        sales._cdff_post()
        return len(sales)

    # ---------------------------------------------------------------- engine
    def _cdff_post(self):
        for sale in self:
            if sale.state != "draft":
                sale._cdff_post_one()

    def _cdff_todo(self):
        """The legs the sale still owes, in order."""
        self.ensure_one()
        money = self.total > 0.005
        legs = []
        if self.state == "confirmed":
            if money and not self.mushak_id:
                legs.append("vat")
            if money and not self.gl_move_id:
                legs.append("gl")
            if self.stock_state in ("none", "pending"):
                legs.append("stock")
        elif self.state == "refunded":
            if self.mushak_id and not self.mushak_note_id:
                legs.append("vat_reverse")
            if self.gl_move_id and not self.gl_reversal_move_id:
                legs.append("gl_reverse")
            if self.stock_state == "issued":
                legs.append("stock_reverse")
        return legs

    def _cdff_post_one(self):
        """Run every leg the sale owes on its own savepoint, as the system on
        behalf of the acting user (env.uid stays the cashier / approver)."""
        self.ensure_one()
        sale = self.sudo().with_company(self.company_id)
        self.env.flush_all()
        # one runner per sale: a concurrent retry waits, then finds nothing to do
        self.env.cr.execute("SELECT id FROM fix_counter_sale WHERE id = %s FOR UPDATE", [sale.id])
        sale.invalidate_recordset()
        if sale.state == "refunded" and sale.stock_state in ("none", "pending"):
            # refunded before the part ever left the ledger: nothing to move
            sale._guarded().write({"stock_state": "cancelled"})
        problems = []
        for leg in sale._cdff_todo():
            try:
                with self.env.cr.savepoint():
                    getattr(sale, "_cdff_leg_%s" % leg)()
            except Exception as exc:
                if not isinstance(exc, UserError | ValueError):
                    _logger.exception("counter sale %s: %s leg failed", sale.name, leg)
                problems.append("%s: %s" % (LEG_LABELS[leg], _message(exc)))
                if leg == "stock" and sale.stock_state == "none":
                    sale._guarded().write({"stock_state": "pending"})
        sale._cdff_record(problems)

    def _cdff_record(self, problems):
        self.ensure_one()
        owed = self._cdff_todo()
        if self.state == "confirmed":
            new = "pending" if owed else "posted"
        elif self.state == "refunded":
            new = "reversal_pending" if owed else "reversed"
        else:
            new = "none"
        note = "\n".join(problems) or False
        changed = (new, note or False) != (self.posting_state, self.posting_note or False)
        self._guarded().write(
            {
                "posting_state": new,
                "posting_note": note,
                "posting_attempted_at": fields.Datetime.now(),
            }
        )
        if changed:
            label = dict(POSTING_STATES)[new]
            body = "Books: %s." % label if not note else "Books: %s — %s" % (label, note)
            self.message_post(body=body)

    # ------------------------------------------------------------- helpers
    def _cdff_day(self, stamp=None):
        """The Bangladesh calendar day of a counter event (UTC+6 frame)."""
        tz = self.company_id.partner_id.tz or DHAKA
        return fields.Date.context_today(
            self.with_context(tz=tz), timestamp=stamp or fields.Datetime.now()
        )

    def _cdff_branch(self):
        return self.branch_id or self.shift_id.branch_id

    def _cdff_vat_figures(self):
        """(taxable, VAT, treatment line) of the VAT-inclusive counter total.

        The rate and treatment are M51's (Tax Rate Master + tariff row of the
        product); the taxable value is the one whose determined VAT makes the
        total exactly — the cash taken. When no taxable value does (an
        inclusive total the 2-decimal rounding skips), the split is the
        inclusive one, within a paisa of the determination. Fixed once."""
        self.ensure_one()
        if self.vat_treatment_summary:
            return self.vat_taxable_amount, self.vat_output_amount, self.vat_treatment_summary
        total = Decimal(str(self.total)).quantize(CENT, ROUND_HALF_UP)
        product = self.product_id
        code = product.default_code or "CS-%s" % product.id
        day = self._cdff_day(self.confirmed_at)

        def determine(taxable):
            line = tax_logic.TaxLine(product_code=code, qty=Decimal(1), unit_price=taxable)
            return m51_determine(self.env, [line], on_date=day, company=self.company_id)

        probe = determine(total).lines[0]
        if probe.treatment == "truncated":
            raise UserError(
                "%s is a truncated-base supply: its VAT is not a rate on the counter price. "
                "Raise its Mushak 6.3 through billing." % product.display_name
            )
        rate = Decimal(str(probe.rate))
        net = (total * 100 / (100 + rate)).quantize(CENT, ROUND_HALF_UP)
        chosen = None
        for taxable in (net, net - CENT, net + CENT):
            if taxable < 0:
                continue
            found = determine(taxable)
            if found.total_payable == total:
                chosen = (taxable, found.total_vat, found.lines[0])
                break
        if chosen is None:
            chosen = (net, total - net, determine(net).lines[0])
        taxable, vat, line = chosen
        summary = "%s: %s @ %s%%" % (
            line.product_code,
            line.treatment,
            format(Decimal(str(line.rate)).normalize(), "f"),
        )
        self._guarded().write(
            {
                "vat_taxable_amount": float(taxable),
                "vat_output_amount": float(vat),
                "vat_treatment_summary": summary,
            }
        )
        return float(taxable), float(vat), summary

    def _cdff_post_move(self, day, ref, lines, source_ref):
        """Post one balanced entry through M19 (chart rules, dimensions,
        posting log, journal.posted). lines: [(account, label, debit, credit)]."""
        company = self.company_id
        journal = _ar_journal(self.env, company)
        if not journal:
            raise UserError("No general journal in %s to post counter sales to." % company.name)
        kept = [ln for ln in lines if round(ln[2], 2) or round(ln[3], 2)]
        dims = self.env["fix.ar.invoice"]._ar_posting_dims(self._cdff_branch().id)
        move_vals = {
            "journal_id": journal.id,
            "company_id": company.id,
            "date": day,
            "ref": ref,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "account_id": account.id,
                        "name": label,
                        "debit": round(debit, 2),
                        "credit": round(credit, 2),
                    },
                )
                for account, label, debit, credit in kept
            ],
        }
        return self.env["account.move"]._fix_post_via_m19(
            move_vals,
            SOURCE,
            source_ref=source_ref,
            dimension_by_line={i: dict(dims) for i in range(len(kept))},
        )

    # ------------------------------------------------------------ forward legs
    def _cdff_leg_vat(self):
        """The Mushak 6.3, as the AR invoice issues it."""
        taxable, vat, summary = self._cdff_vat_figures()
        company = self.company_id
        Invoice = self.env["fix.ar.invoice"].sudo()
        day = self._cdff_day(self.confirmed_at)
        partner = self.customer_id.commercial_partner_id
        buyer_bin = normalize_bin(partner.vat) if partner else ""
        row = _issue_mushak_row(
            self.env,
            {
                "operating_unit_id": self.operating_unit_id.id,
                "company_id": company.id,
                "mushak_no": Invoice._next_mushak_no(company, day),
                "invoice_ref": self.name,
                "invoice_date": day,
                "supplier_name": company.name,
                "supplier_bin": Invoice._company_bin(company),
                "customer_name": partner.name or WALK_IN,
                "customer_bin": buyer_bin if valid_bin(buyer_bin) else False,
                "taxable_amount": taxable,
                "vat_amount": vat,
                "total_payable": self.total,
                "treatment_summary": summary,
            },
        )
        self._guarded().write({"mushak_id": row.id})

    def _cdff_leg_gl(self):
        if not self.mushak_id:
            raise UserError("The sale is posted with its Mushak 6.3, which is not issued yet.")
        _taxable, vat, _summary = self._cdff_vat_figures()
        company = self.company_id
        revenue_role = "labour_revenue" if self.product_id.type == "service" else "parts_revenue"
        pay, pay_why = resolve_account(self.env, company, PAYMENT_ROLE[self.payment_method])
        revenue, revenue_why = resolve_account(self.env, company, revenue_role)
        vat_account, vat_why = (
            resolve_account(self.env, company, "vat_output") if vat > 0.005 else (None, None)
        )
        missing = [why for why in (pay_why, revenue_why, vat_why) if why]
        if missing:
            raise UserError(" ".join(missing))
        method = dict(self._fields["payment_method"].selection)[self.payment_method]
        label = "Counter sale %s" % self.name
        mushak_no = self.mushak_id.mushak_no
        move = self._cdff_post_move(
            self.mushak_id.invoice_date,
            "%s — %s (Mushak %s)" % (label, method, mushak_no),
            [
                (pay, "%s — %s" % (label, method), self.total, 0.0),
                (
                    revenue,
                    "%s — %s" % (label, ACCOUNT_ROLES[revenue_role][0]),
                    0.0,
                    round(self.total - vat, 2),
                ),
                (vat_account, "VAT output (Mushak %s)" % mushak_no, 0.0, vat),
            ],
            self.name,
        )
        self._guarded().write(
            {"gl_move_id": move.id, "payment_account_id": pay.id, "revenue_account_id": revenue.id}
        )
        # T08: the register row is marked posted only with its GL entry
        self.mushak_id._fix_mark_posted(move)

    def _cdff_part(self):
        company = self.company_id
        return (
            self.env["fix.spare.part"]
            .sudo()
            .search(
                [
                    ("product_id", "=", self.product_id.id),
                    ("company_id", "in", [company.id, False]),
                ],
                limit=1,
            )
        )

    def _cdff_issue_location(self, part):
        """The sale's location, else the branch's counter location, else the
        ONE location of the branch holding enough of the part. Never a guess."""
        if self.stock_location_id:
            return self.stock_location_id
        branch = self._cdff_branch()
        if branch.counter_stock_location_id:
            return branch.counter_stock_location_id
        rows = (
            self.env["fix.stock.onhand"]
            .sudo()
            .search(
                [
                    ("part_id", "=", part.id),
                    ("location_id.branch_id", "=", branch.id),
                    ("location_id.location_type", "in", ("branch", "central")),
                    ("ownership_class", "=", "owned"),
                    ("stock_status", "=", "unrestricted"),
                ]
            )
            .filtered(lambda r: (r.qty or 0.0) - (r.reserved or 0.0) + 1e-9 >= self.quantity)
        )
        if len(rows.location_id) == 1:
            return rows.location_id
        where = ", ".join(rows.location_id.mapped("code")) or "none"
        raise UserError(
            "%s locations of %s hold %s of %s (%s): set the sale's Issue From Location (or the "
            "branch's Counter Stock Location) and retry."
            % (
                "Several" if rows else "No",
                branch.display_name or "the branch",
                self.quantity,
                part.part_number,
                where,
            )
        )

    def _cdff_leg_stock(self):
        """The part leaves the M15 ledger like any issue: unrestricted,
        unreserved stock of the location at its average cost, bins respected,
        a serial in stock there, and the valuation suspense row booked."""
        part = self._cdff_part()
        if not part:
            self._guarded().write({"stock_state": "not_required"})
            return
        location = self._cdff_issue_location(part)
        if location.location_type in ("quarantine", "scrap"):
            raise UserError(
                "%s is a %s location: its stock is not sold."
                % (location.code, location.location_type)
            )
        qty = self.quantity
        check_quantity(part, qty, "counter sale quantity")
        cls = location_class(location, "owned")
        lot = self.env["fix.stock.lot"]
        if part.is_serialized:
            serial = (self.serial_or_warranty_ref or "").strip()
            if not serial:
                raise UserError(
                    "%s is serialized: enter the serial sold (Part Serial) and retry."
                    % part.part_number
                )
            if abs(qty - 1.0) > 1e-9:
                raise UserError(
                    "%s is serialized: one sale line sells one serial." % part.part_number
                )
            lot = lot._fix_find(part, serial)
            if not lot or lot.status != "in_stock" or lot.location_id != location:
                raise UserError(
                    "Serial %s of %s is not in stock at %s."
                    % (serial, part.part_number, location.code)
                )
        Onhand = self.env["fix.stock.onhand"]
        bucket = Onhand._bucket(part, location, cls)
        available = ((bucket.qty or 0.0) - (bucket.reserved or 0.0)) if bucket else 0.0
        if available + 1e-9 < qty:
            raise UserError(
                "Only %s of %s is available at %s for a sale of %s."
                % (round(available, 4), part.part_number, location.code, qty)
            )
        cost = bucket.unit_cost or 0.0
        Onhand._fix_check_bins(part, location, qty)
        Onhand._apply(part, location, cls, -qty)
        if lot:
            lot._fix_move("issued", qty=0.0)
        self.env["fix.inventory.valuation.suspense"]._fix_post(
            SOURCE, part, -qty, cost, self.name, location=location, ownership=cls
        )
        self._guarded().write(
            {
                "stock_state": "issued",
                "stock_location_id": location.id,
                "stock_part_id": part.id,
                "stock_ownership_class": cls,
                "stock_unit_cost": cost,
                "stock_lot_id": lot.id or False,
            }
        )

    # ------------------------------------------------------------ refund legs
    def _cdff_refund_day(self):
        return self._cdff_day(self.refund_approved_at)

    def _cdff_leg_vat_reverse(self):
        """The Mushak 6.7 against the sale's 6.3 (M51's correction service)."""
        row = self.mushak_id
        reason = dict(REFUND_REASONS).get(self.refund_reason_code) or "refund"
        note = self.env["fix.mushak.register"]._fix_issue_note(
            row,
            "credit_note",
            row.taxable_amount,
            row.vat_amount,
            "Counter refund of %s (%s)" % (self.name, reason),
            ref="%s/REFUND" % self.name,
            on_date=self._cdff_refund_day(),
        )
        self._guarded().write({"mushak_note_id": note.id})

    def _cdff_leg_gl_reverse(self):
        """The mirror of the sale's entry: the drawer (or clearing) pays the
        refund back, revenue and VAT output are reversed."""
        if self.mushak_id and not self.mushak_note_id:
            raise UserError("The refund is posted with its Mushak 6.7, which is not issued yet.")
        original = self.gl_move_id
        move = self._cdff_post_move(
            self._cdff_refund_day(),
            "Refund of counter sale %s (%s)" % (self.name, original.name),
            [
                (
                    line.account_id,
                    "Refund of %s — %s" % (self.name, line.name or ""),
                    line.credit,
                    line.debit,
                )
                for line in original.line_ids
            ],
            "%s/REFUND" % self.name,
        )
        self._guarded().write({"gl_reversal_move_id": move.id})
        if self.mushak_note_id:
            self.mushak_note_id._fix_mark_posted(move)

    def _cdff_leg_stock_reverse(self):
        """The part comes back to the location it left, at the cost it left
        with; returned defective, it goes to quarantine (BRU-INV-08)."""
        part, location = self.stock_part_id, self.stock_location_id
        cls = self.stock_ownership_class or location_class(location, "owned")
        cost = self.stock_unit_cost
        qty = self.quantity
        defective = self.refund_reason_code == "defective"
        self.env["fix.stock.onhand"]._apply(
            part, location, cls, qty, cost, status="quarantine" if defective else "unrestricted"
        )
        lot = self.stock_lot_id
        if lot:
            lot._fix_move("quarantined" if defective else "in_stock", location, 1.0)
        if defective:
            self.env["fix.stock.quarantine"].sudo()._guarded().with_context(
                fix_quarantine_in_place=True
            ).create(
                {
                    "part_id": part.id,
                    "location_id": location.id,
                    "company_id": self.company_id.id,
                    "ownership_class": cls,
                    "lot_id": lot.id or False,
                    "qty": qty,
                    "reason": "defective",
                    "notes": "Returned defective on counter refund %s" % self.name,
                    "source_ref": self.name,
                }
            )
        self.env["fix.inventory.valuation.suspense"]._fix_post(
            SOURCE, part, qty, cost, "%s/REFUND" % self.name, location=location, ownership=cls
        )
        self._guarded().write({"stock_state": "returned"})
