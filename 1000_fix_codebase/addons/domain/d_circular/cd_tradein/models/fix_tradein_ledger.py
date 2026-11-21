# fix_tradein_ledger — M14: the refurbished-stock valued ledger, the resale
# price approval, markdowns, the sale and the return of a refurbished unit.
#
# A05 ERP audit (20 Nov 2026), owner decisions D1/D2/D3/D6/D7:
#   M14-01/03, FIN-02/03: the payout posted Dr Bank Suspense / Cr Bank and the
#       TDS was a register line with no liability. The device is now booked
#       into stock AT PURCHASE: Dr refurbished stock (gross) / Cr seller
#       payable 200101 (net) / Cr TDS payable 200905; the TDS is recorded on
#       that posted entry (M51 _fix_record_deductions) and treasury clears the
#       payable (debit_account_id) when the money leaves.
#   M14-02, FIN-04: refurbished stock never reached the GL. Each unit now has
#       a ledger (fix.refurb.ledger): capitalised at payout, refurbishment
#       (M31 parts + labour, typed step costs only once approved) absorbed at
#       Resale Ready, NRV write-downs, write-off, harvest relief, Dr COGS /
#       Cr stock at each sale and its reversal on a return.
#   M14-08, FIN-19: a warranty provision by grade (parameters) at each sale,
#       released at warranty expiry or when the unit comes back.
#   M14-13, FIN-23, D6: the listing price is approved four-eyes by a pricing
#       manager who did not propose it; never below landed cost unless an
#       approved markdown says so (M14-25 NRV + markdown).
#   M14-04/05/15: a unit is sold only through these paths, every sale re-asks
#       the wipe gate, NEIR and price, and a return is held, not restocked.
# Every account is a system parameter that FAILS CLOSED (D1); every posting
# goes through the M19 posting API with the trade-in's operating unit and
# branch as its dimensions, and is idempotent on its ledger key.
from __future__ import annotations

import logging
from decimal import ROUND_HALF_UP, Decimal
from types import SimpleNamespace

from odoo import api, fields, models
from odoo.addons.cd_billing_engine.models.fix_ar_engine import _ar_journal
from odoo.addons.cd_gl_ext.models.fix_gl_ext import post_with_dimensions
from odoo.addons.cd_tax_engine_bd.models.fix_tax_master import tax_account
from odoo.exceptions import AccessError, UserError

from .fix_tradein import _EPS, _param, _param_float
from .fix_tradein_ops import _assert_role

_logger = logging.getLogger(__name__)

DHAKA = "Asia/Dhaka"
CENT = Decimal("0.01")
SOURCE = "tradein_subledger"

GROUP_PRICING_MANAGER = "cd_tradein.group_refurb_pricing_manager"
GROUP_STOCK_CONTROLLER = "cd_wms_structure.group_inventory_controller"
GROUP_REFURB_SUPERVISOR = "cd_tradein.group_refurb_supervisor"
# M14-30: what a unit cost and earns is read by costing and finance only
COST_GROUPS = "cd_wms_structure.group_stock_cost_viewer,account.group_account_user"

# D1: role -> label. The code of each is system parameter
# cd_tradein.account_code.<role>; unset or unknown REFUSES the posting.
ACCOUNT_ROLES = {
    "refurb_stock": "Stock of Inventory - Refurbished",
    "seller_payable": "Account Payable (trade-in seller payable)",
    "tds_payable": "Tax Payable (TDS withheld from the seller)",
    "cogs": "Cost of Goods Sold - Direct Sales",
    "writeoff": "Write Off Inventory",
    "warranty_provision": "Provision For Warranty cost",
    "warranty_expense": "Warranty Cost Expense",
    # D10(a): the NEW contra-cost "Refurbishment Cost Absorbed" (proposed
    # 600008) - seeded by the lead's deploy data, fails closed while unset
    "refurb_absorption": "Refurbishment cost absorbed into refurbished stock",
    # D10(b): 400101 Direct Sales Income - every refurbished resale invoice
    # (counter, marketplace) credits it, never the service revenue default
    "resale_revenue": "Direct Sales Income (refurbished resale revenue)",
}
PARAM_PROVISION_PCT = "cd_tradein.warranty_provision_pct.%s"  # D7/D11: a 2 / b 3 / c 5 / d 7
PARAM_WARRANTY_MONTHS_GRADE = "cd_tradein.resale_warranty_months.%s"


def account_param(role):
    return "cd_tradein.account_code.%s" % role


def tradein_account(env, company, role):
    """The company's GL account for an M14 role. Refuses, never guesses."""
    key = account_param(role)
    code = (env["ir.config_parameter"].sudo().get_param(key) or "").strip()
    label = ACCOUNT_ROLES[role]
    if not code:
        raise UserError(
            "M14 posting refused: no GL account is configured for %s. Set system parameter "
            "%s to its account code. Nothing was posted." % (label, key)
        )
    account = (
        env["account.account"]
        .sudo()
        .with_company(company)
        .search([("code", "=", code), ("company_ids", "in", company.id)], limit=1)
    )
    if not account:
        raise UserError(
            "M14 posting refused: system parameter %s names %s (%s), which is not an account "
            "of %s. Nothing was posted." % (key, code, label, company.name)
        )
    if role == "tds_payable":
        # the challan deposit (M51) debits ITS TDS payable: the trade-in must
        # credit the same account or the deposit never clears what we withheld
        m51 = tax_account(env(su=True), company, "tds_payable")
        if m51 != account:
            raise UserError(
                "M14 posting refused: %s names %s, but the M51 TDS payable account the challan "
                "deposit clears is %s (cd_tax_engine_bd.account_code.tds_payable). They must "
                "be the same account." % (key, account.code, m51.code)
            )
    return account


def dhaka_today(record):
    """The business day in Bangladesh (Odoo runs in UTC)."""
    return fields.Date.context_today(record.with_context(tz=DHAKA))


def ex_vat(env, company, gross, day):
    """The taxable value whose M51-determined VAT makes `gross` (D2: resale
    at standard VAT on the full price), never a hard-coded rate."""
    Line = env["fix.ar.invoice.line"].sudo()
    frame = SimpleNamespace(invoice_date=day, company_id=company)
    product = env["product.product"]
    treatment = env["fix.vat.treatment"]

    def total_of(taxable):
        det = Line._fix_determined(frame, float(taxable), product, treatment)
        total = Decimal(str(det.taxable_amount)) + Decimal(str(det.vat_amount))
        return total.quantize(CENT, ROUND_HALF_UP), det

    target = Decimal(str(gross or 0.0)).quantize(CENT, ROUND_HALF_UP)
    if target <= 0:
        return 0.0
    _total, probe = total_of(target)
    rate = Decimal(str(probe.rate or 0))
    net = (target * 100 / (100 + rate)).quantize(CENT, ROUND_HALF_UP)
    for cand in (net, net - CENT, net + CENT):
        if cand >= 0 and total_of(cand)[0] == target:
            return float(cand)
    return float(net)


def post_tradein_move(tradein, ref, lines, date=None):
    """Post a balanced M14 entry through M19. `lines` is
    [(account, label, debit, credit, partner|None)]. The dimensions are the
    trade-in's operating unit and branch (never the company's first OU)."""
    env = tradein.sudo().env
    tradein = tradein.sudo()
    company = tradein.company_id
    lines = [ln for ln in lines if round(ln[2], 2) or round(ln[3], 2)]
    if not lines:
        return env["account.move"]
    if round(sum(ln[2] for ln in lines) - sum(ln[3] for ln in lines), 2) != 0:
        raise UserError("M14 posting %s is not balanced." % ref)
    journal = _ar_journal(env, company)
    if not journal:
        raise UserError(
            "M14 posting refused: company %s has no general (miscellaneous) journal." % company.name
        )
    ou = tradein.operating_unit_id
    if not ou:
        raise UserError(
            "M14 posting refused: trade-in %s has no operating unit (the OU is fixed at intake "
            "and is the posting's dimension)." % tradein.name
        )
    branch = tradein.branch_id
    dims = env["fix.ar.invoice"]._ar_posting_dims(branch.id if branch else False)
    dims["operating_unit_id"] = ou.id
    move, _dims = post_with_dimensions(
        env,
        {
            "journal_id": journal.id,
            "company_id": company.id,
            "date": date or dhaka_today(tradein),
            "ref": ref,
            "line_ids": [
                (
                    0,
                    0,
                    {
                        "name": label,
                        "account_id": account.id,
                        "partner_id": partner.id if partner else False,
                        "debit": round(debit, 2),
                        "credit": round(credit, 2),
                    },
                )
                for account, label, debit, credit, partner in lines
            ],
        },
        {idx: dims for idx in range(len(lines))},
        source=SOURCE,
        source_ref=ref,
    )
    return move


class FixJournalPostingLogTradein(models.Model):
    """The trade-in sub-ledger as an M19 posting source (automated: a line
    with no dimension the chart needs takes the company default)."""

    _inherit = "fix.journal.posting.log"

    source = fields.Selection(
        selection_add=[(SOURCE, "Trade-In & Refurbished Stock Sub-ledger (M14)")],
        ondelete={SOURCE: lambda recs: recs.write({"source": "api"})},
    )


# =========================================================================== ledger
LEDGER_KINDS = [
    ("acquisition", "Bought in (payout)"),
    ("transfer_in", "Transferred in (company-owned)"),
    ("refurb_cost", "Refurbishment absorbed"),
    ("nrv_writedown", "NRV write-down (markdown)"),
    ("writeoff", "Write-off"),
    ("harvest", "Parts harvested to M15"),
    ("cogs", "Cost of sale"),
    ("cogs_reversal", "Returned by the buyer"),
    ("warranty_provision", "Warranty provision"),
    ("warranty_release", "Warranty provision released"),
]


class FixRefurbLedger(models.Model):
    """One movement of a refurbished unit's value (M14-02). System-written:
    each row is the posting it records, keyed so a re-run never posts twice."""

    _name = "fix.refurb.ledger"
    _description = "Refurbished Stock Ledger Line"
    _inherit = ["fix.guarded.mixin"]
    _order = "id"

    name = fields.Char(required=True, readonly=True)
    tradein_id = fields.Many2one(
        "fix.tradein.request", required=True, index=True, ondelete="restrict", readonly=True
    )
    company_id = fields.Many2one("res.company", required=True, index=True, readonly=True)
    operating_unit_id = fields.Many2one("operating.unit", index=True, readonly=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, readonly=True, default=lambda self: self.env.ref("base.BDT")
    )
    kind = fields.Selection(LEDGER_KINDS, required=True, readonly=True, index=True)
    key = fields.Char(required=True, readonly=True, index=True)
    amount = fields.Monetary(currency_field="currency_id", readonly=True)
    stock_effect = fields.Monetary(
        currency_field="currency_id",
        readonly=True,
        help="What the movement did to the unit's refurbished-stock value (+ in, - out).",
    )
    sale_no = fields.Integer(readonly=True)
    cycle = fields.Integer(readonly=True)
    move_id = fields.Many2one("account.move", string="Journal Entry", readonly=True)
    note = fields.Char(readonly=True)

    _key_unique = models.Constraint(
        "UNIQUE (tradein_id, key)", "A ledger movement is posted once (idempotent key)."
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {n for n, f in self._fields.items() if f.store}

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            raise AccessError("The refurbished-stock ledger is written by its postings only.")
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            raise AccessError("A refurbished-stock ledger line is never edited.")
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError("A refurbished-stock ledger line is evidence and is not deleted.")
        return super().unlink()


# =========================================================================== markdown
class FixRefurbMarkdown(models.Model):
    """M14-25 / FR-TRF-029 / BRU-TRF-18 / D6: a listing price below the unit's
    landed cost, or any price cut of a listed unit, is a markdown a pricing
    manager who did not ask for it approves. The approval reprices the unit and
    writes the stock down to its net realisable value (Dr 500905 / Cr stock)."""

    _name = "fix.refurb.markdown"
    _description = "Refurbished Unit Markdown"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    _INPUTS = frozenset({"tradein_id", "new_price", "reason", "company_id"})

    name = fields.Char(required=True, default="New", copy=False)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    tradein_id = fields.Many2one(
        "fix.tradein.request", string="Unit (Trade-In)", required=True, index=True
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    current_price = fields.Monetary(
        string="Price Before", currency_field="currency_id", readonly=True, copy=False
    )
    new_price = fields.Monetary(
        string="New Price (VAT inclusive)", currency_field="currency_id", required=True
    )
    reason = fields.Text(required=True)
    landed_cost = fields.Monetary(
        string="Landed Cost",
        currency_field="currency_id",
        readonly=True,
        copy=False,
        groups=COST_GROUPS,
    )
    nrv_writedown = fields.Monetary(
        string="NRV Write-down",
        currency_field="currency_id",
        readonly=True,
        copy=False,
        groups=COST_GROUPS,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("pending", "Approval Pending"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        default="draft",
        required=True,
        readonly=True,
        tracking=True,
    )
    requested_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    approved_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    approved_at = fields.Datetime(readonly=True, copy=False)

    _price_positive = models.Constraint("CHECK (new_price > 0)", "A markdown price is positive")

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "current_price",
            "landed_cost",
            "nrv_writedown",
            "requested_by_id",
            "approved_by_id",
            "approved_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(r.state != "draft" for r in self):
            locked |= self._INPUTS
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.refurb.markdown") or "RMD/New"
                )
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self.filtered(lambda r: r.state != "draft"):
                names = [
                    n
                    for n in self._INPUTS & set(vals)
                    if rec._fix_guard_differs(n, vals[n], rec[n])
                ]
                if names:
                    raise UserError("Markdown %s is %s: it is final." % (rec.name, rec.state))
        return super().write(vals)

    def action_request(self):
        for rec in self:
            if rec.state not in ("draft", "rejected"):
                raise UserError("Markdown %s is %s." % (rec.name, rec.state))
            tradein = rec.tradein_id.sudo()
            if tradein.state not in ("graded", "resale_ready"):
                raise UserError(
                    "Trade-in %s is %s: a markdown prices a graded or listed unit."
                    % (tradein.name, tradein.state)
                )
            if not (rec.reason or "").strip():
                raise UserError("Markdown %s: state why the price comes down." % rec.name)
            rec.sudo()._guarded().write(
                {
                    "state": "pending",
                    "requested_by_id": self.env.uid,
                    "current_price": tradein.listing_price or tradein.resale_value,
                    "landed_cost": tradein._tradein_landed_cost(),
                }
            )
        return True

    def action_approve(self):
        _assert_role(self.env, GROUP_PRICING_MANAGER, "Approving a markdown")
        for rec in self:
            if rec.state != "pending":
                raise UserError(
                    "Markdown %s is %s: only a pending one is approved." % (rec.name, rec.state)
                )
            if not self.env.su and self.env.user in (rec.requested_by_id | rec.create_uid):
                raise UserError(
                    "Segregation of duties: a markdown you asked for is approved by another "
                    "pricing manager (D6)."
                )
            tradein = rec.tradein_id.sudo()
            writedown = tradein._tradein_apply_markdown(rec)
            rec.sudo()._guarded().write(
                {
                    "state": "approved",
                    "approved_by_id": self.env.uid,
                    "approved_at": fields.Datetime.now(),
                    "nrv_writedown": writedown,
                }
            )
        return True

    def action_reject(self):
        _assert_role(self.env, GROUP_PRICING_MANAGER, "Rejecting a markdown")
        for rec in self:
            if rec.state != "pending":
                raise UserError("Markdown %s is %s." % (rec.name, rec.state))
            rec._guarded().write({"state": "rejected"})
        return True


# =========================================================================== request
class FixTradeinRequestLedger(models.Model):
    _inherit = "fix.tradein.request"

    ledger_ids = fields.One2many(
        "fix.refurb.ledger",
        "tradein_id",
        string="Refurbished Stock Ledger",
        readonly=True,
        groups=COST_GROUPS,
    )
    carrying_cost = fields.Monetary(
        string="Carrying Cost (Ledger)",
        currency_field="currency_id",
        compute="_compute_carrying_cost",
        store=True,
        groups=COST_GROUPS,
        help="The unit's value on the refurbished-stock ledger (what the GL carries).",
    )
    acquisition_move_id = fields.Many2one(
        "account.move", string="Purchase Entry", readonly=True, copy=False
    )
    # D6: the listing price, approved four-eyes
    listing_price = fields.Monetary(
        string="Approved Listing Price",
        currency_field="currency_id",
        readonly=True,
        copy=False,
        help="The VAT-inclusive price the unit is sold at, approved by a pricing manager who "
        "did not propose it; lowered only by an approved markdown.",
    )
    listing_price_state = fields.Selection(
        [("none", "Not Requested"), ("pending", "Approval Pending"), ("approved", "Approved")],
        string="Listing Price Approval",
        default="none",
        required=True,
        readonly=True,
        copy=False,
    )
    listing_price_proposed = fields.Monetary(
        string="Proposed Listing Price", currency_field="currency_id", readonly=True, copy=False
    )
    listing_price_proposed_by_id = fields.Many2one(
        "res.users", string="Price Proposed By", readonly=True, copy=False
    )
    listing_price_approved_by_id = fields.Many2one(
        "res.users", string="Price Approved By", readonly=True, copy=False
    )
    listing_price_approved_at = fields.Datetime(readonly=True, copy=False)
    resale_value_set_by_id = fields.Many2one(
        "res.users", string="Suggested Price Entered By", readonly=True, copy=False
    )
    sale_count = fields.Integer(string="Times Sold", readonly=True, copy=False)
    sale_invoice_id = fields.Many2one(
        "fix.ar.invoice", string="Last Sale Invoice (M20)", readonly=True, copy=False
    )
    markdown_ids = fields.One2many("fix.refurb.markdown", "tradein_id", string="Markdowns")
    # I4 (S2 -> S5): the buyer disclosure / warranty card text (BRU-TRF-15)
    buyer_disclosure_html = fields.Html(
        string="Buyer Disclosure",
        compute="_compute_buyer_disclosure",
        sanitize=True,
        help="Generated from the record: grade, battery, defects, repairs, warranty, wipe "
        "certificate and provenance. Required at Resale Ready.",
    )

    @api.depends("ledger_ids.stock_effect")
    def _compute_carrying_cost(self):
        for rec in self:
            rec.carrying_cost = round(sum(rec.sudo().ledger_ids.mapped("stock_effect")), 2)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "acquisition_move_id",
            "listing_price",
            "listing_price_state",
            "listing_price_proposed",
            "listing_price_proposed_by_id",
            "listing_price_approved_by_id",
            "listing_price_approved_at",
            "resale_value_set_by_id",
            "sale_count",
            "sale_invoice_id",
        }

    def write(self, vals):
        result = super().write(vals)
        if "resale_value" in vals and not self.env.context.get("fix_tradein_price_stamp"):
            for rec in self:
                stamp = {"resale_value_set_by_id": self.env.uid}
                # D6: a new suggested price voids a price approval in flight
                if (
                    rec.listing_price_state == "pending"
                    and abs((rec.listing_price_proposed or 0.0) - (rec.resale_value or 0.0)) > _EPS
                ):
                    stamp.update(
                        listing_price_state="none",
                        listing_price_proposed=0.0,
                        listing_price_proposed_by_id=False,
                    )
                rec.sudo().with_context(fix_tradein_price_stamp=True)._guarded().write(stamp)
        return result

    # ------------------------------------------------------------- ledger core
    def _ledger_row(self, key):
        self.ensure_one()
        return (
            self.env["fix.refurb.ledger"]
            .sudo()
            .search([("tradein_id", "=", self.id), ("key", "=", key)], limit=1)
        )

    def _ledger_carrying(self) -> float:
        self.ensure_one()
        rows = self.env["fix.refurb.ledger"].sudo().search([("tradein_id", "=", self.id)])
        return round(sum(rows.mapped("stock_effect")), 2)

    def _ledger_post(self, kind, key, amount, stock_effect, lines, note, sale_no=0):
        """Post `lines` and record the movement, once per key."""
        self.ensure_one()
        row = self._ledger_row(key)
        if row:
            return row
        rec = self.sudo()
        move = post_tradein_move(rec, "%s %s" % (rec.name, note), lines) if lines else False
        row = (
            self.env["fix.refurb.ledger"]
            .sudo()
            ._guarded()
            .create(
                {
                    "name": "%s / %s" % (rec.name, key),
                    "tradein_id": rec.id,
                    "company_id": rec.company_id.id,
                    "operating_unit_id": rec.operating_unit_id.id or False,
                    "currency_id": rec.currency_id.id,
                    "kind": kind,
                    "key": key,
                    "amount": round(amount, 2),
                    "stock_effect": round(stock_effect, 2),
                    "sale_no": sale_no,
                    "cycle": rec.refurb_cycle,
                    "move_id": move.id if move else False,
                    "note": note[:250],
                }
            )
        )
        return self.env["fix.refurb.ledger"].sudo().browse(row.id)

    def _acct(self, role):
        self.ensure_one()
        return tradein_account(self.env, self.company_id, role)

    def _tradein_capitalised(self) -> bool:
        self.ensure_one()
        rows = (
            self.env["fix.refurb.ledger"]
            .sudo()
            .search_count(
                [("tradein_id", "=", self.id), ("kind", "in", ("acquisition", "transfer_in"))]
            )
        )
        return bool(rows)

    # ------------------------------------------------------- D3: the purchase
    def _tradein_post_acquisition(self):
        """Dr refurbished stock (gross) / Cr seller payable (net) / Cr TDS
        payable (withheld), and the TDS on that posted entry (M51)."""
        self.ensure_one()
        rec = self.sudo()
        gross = round(rec.graded_value or 0.0, 2)
        tds = round(rec.tds_amount if rec.tds_applicable else 0.0, 2)
        net = round(gross - tds, 2)
        stock = rec._acct("refurb_stock")
        payable = rec._acct("seller_payable")
        lines = [
            (
                stock,
                "Trade-in %s: %s bought in" % (rec.name, rec.device_id.name or "device"),
                gross,
                0.0,
                None,
            ),
            (payable, "Trade-in %s: payable to the seller" % rec.name, 0.0, net, rec.customer_id),
        ]
        if tds > _EPS:
            lines.append(
                (
                    rec._acct("tds_payable"),
                    "Trade-in %s: TDS withheld" % rec.name,
                    0.0,
                    tds,
                    rec.customer_id,
                )
            )
        row = rec._ledger_post("acquisition", "acquisition", gross, gross, lines, "purchase")
        if row.move_id and rec.acquisition_move_id != row.move_id:
            rec._guarded().write({"acquisition_move_id": row.move_id.id})
        return row

    # ------------------------------------------------- refurbishment absorption
    def _tradein_refurb_cost_now(self) -> float:
        """The refurbishment cost of the unit: M31 job parts (issued from M15),
        clocked labour and consumables, plus approved typed step costs."""
        self.ensure_one()
        rec = self.sudo()
        job = rec.workshop_job_id
        # the legacy direct costs (guarded: written only by the system)
        total = (rec.parts_cost or 0.0) + (rec.labour_cost or 0.0)
        if job:
            total += (job.parts_total or 0.0) + (getattr(job, "labour_cost", 0.0) or 0.0)
            consumables = getattr(job, "_m31_consumables_cost", None)
            if consumables:
                total += consumables() or 0.0
        total += sum(
            rec.refurbishment_ids.filtered(lambda s: s.cost_approved_by_id).mapped("total_cost")
        )
        return round(total, 2)

    def _tradein_landed_cost(self) -> float:
        """Acquisition + refurbishment: what the unit cost to make sellable
        (the ledger's carrying cost plus refurbishment not yet absorbed)."""
        self.ensure_one()
        rec = self.sudo()
        refurb = rec._tradein_refurb_cost_now()
        if not rec._tradein_capitalised():
            acquisition = rec.graded_value or rec.accepted_offer_value or rec.offered_value or 0.0
            return round(acquisition + refurb, 2)
        absorbed = sum(rec.ledger_ids.filtered(lambda r: r.kind == "refurb_cost").mapped("amount"))
        return round(rec._ledger_carrying() + max(refurb - absorbed, 0.0), 2)

    def _tradein_absorb_refurb(self):
        """Capitalise the refurbishment cost not yet in stock (Dr stock / Cr
        refurbishment absorbed); idempotent per refurbishment cycle."""
        self.ensure_one()
        rec = self.sudo()
        absorbed = sum(rec.ledger_ids.filtered(lambda r: r.kind == "refurb_cost").mapped("amount"))
        amount = round(rec._tradein_refurb_cost_now() - absorbed, 2)
        if amount <= _EPS:
            return self.env["fix.refurb.ledger"]
        lines = [
            (
                rec._acct("refurb_stock"),
                "Trade-in %s: refurbishment capitalised" % rec.name,
                amount,
                0.0,
                None,
            ),
            (
                rec._acct("refurb_absorption"),
                "Trade-in %s: refurbishment absorbed" % rec.name,
                0.0,
                amount,
                None,
            ),
        ]
        return rec._ledger_post(
            "refurb_cost", "refurb:c%d" % rec.refurb_cycle, amount, amount, lines, "refurbishment"
        )

    # ------------------------------------------------------- D6: the price
    def action_request_listing_price(self):
        """Propose the suggested price as the listing price (D6)."""
        for rec in self:
            if rec.state not in ("graded", "resale_ready") or rec.written_off:
                raise UserError(
                    "Trade-in %s is %s: a listing price is proposed for a graded unit."
                    % (rec.name, rec.state)
                )
            if (rec.resale_value or 0.0) <= 0:
                raise UserError("Enter the suggested resale price first.")
            if rec.listing_price_state == "approved":
                raise UserError(
                    "Trade-in %s already has an approved listing price: a lower price is a "
                    "markdown." % rec.name
                )
            rec._guarded().write(
                {
                    "listing_price_state": "pending",
                    "listing_price_proposed": rec.resale_value,
                    "listing_price_proposed_by_id": self.env.uid,
                }
            )
        return True

    def action_approve_listing_price(self):
        """A pricing manager who neither proposed nor entered the price
        approves it; never below landed cost without an approved markdown."""
        _assert_role(self.env, GROUP_PRICING_MANAGER, "Approving a listing price")
        for rec in self:
            if rec.listing_price_state != "pending":
                raise UserError("Trade-in %s has no listing price awaiting approval." % rec.name)
            if not self.env.su and self.env.user in (
                rec.listing_price_proposed_by_id | rec.resale_value_set_by_id
            ):
                raise UserError(
                    "Segregation of duties: the listing price is approved by a pricing manager "
                    "who did not propose or enter it (D6)."
                )
            price = rec.listing_price_proposed
            if abs(price - (rec.resale_value or 0.0)) > _EPS:
                raise UserError(
                    "The suggested price changed after it was proposed: propose it again."
                )
            landed = rec._tradein_landed_cost()
            net = ex_vat(self.env, rec.company_id, price, dhaka_today(rec))
            if net + _EPS < landed:
                raise UserError(
                    "Trade-in %s: BDT %.2f (BDT %.2f before VAT) is below the landed cost of "
                    "BDT %.2f. A price below cost is an approved markdown (D6)."
                    % (rec.name, price, net, landed)
                )
            rec._guarded().write(
                {
                    "listing_price": price,
                    "listing_price_state": "approved",
                    "listing_price_approved_by_id": self.env.uid,
                    "listing_price_approved_at": fields.Datetime.now(),
                }
            )
        return True

    def _tradein_apply_markdown(self, markdown) -> float:
        """Reprice the unit to the markdown's price and write the stock down to
        its net realisable value. Returns the write-down posted."""
        self.ensure_one()
        rec = self.sudo()
        price = markdown.new_price
        vals = {
            "listing_price": price,
            "listing_price_state": "approved",
            "listing_price_proposed": price,
            "listing_price_proposed_by_id": markdown.requested_by_id.id,
            "listing_price_approved_by_id": self.env.uid,
            "listing_price_approved_at": fields.Datetime.now(),
        }
        rec._guarded().write(vals)
        rec.with_context(fix_tradein_price_stamp=True).write({"resale_value": price})
        stock = rec.graded_stock_id
        if stock and stock.state in ("in_stock", "reserved"):
            stock._guarded().write({"resale_price": price})
        writedown = 0.0
        if rec._tradein_capitalised():
            nrv = ex_vat(self.env, rec.company_id, price, dhaka_today(rec))
            carrying = rec._ledger_carrying()
            writedown = round(carrying - nrv, 2)
            if writedown > _EPS:
                lines = [
                    (
                        rec._acct("writeoff"),
                        "Trade-in %s: NRV write-down (%s)" % (rec.name, markdown.name),
                        writedown,
                        0.0,
                        None,
                    ),
                    (
                        rec._acct("refurb_stock"),
                        "Trade-in %s: NRV write-down" % rec.name,
                        0.0,
                        writedown,
                        None,
                    ),
                ]
                rec._ledger_post(
                    "nrv_writedown",
                    "markdown:%d" % markdown.id,
                    writedown,
                    -writedown,
                    lines,
                    "markdown %s" % markdown.name,
                )
                if stock:
                    refurb_part = min(stock.refurbishment_cost or 0.0, writedown)
                    stock._guarded().write(
                        {
                            "refurbishment_cost": (stock.refurbishment_cost or 0.0) - refurb_part,
                            "acquisition_cost": max(
                                (stock.acquisition_cost or 0.0) - (writedown - refurb_part), 0.0
                            ),
                        }
                    )
            else:
                writedown = 0.0
        rec.message_post(
            body="Markdown %s approved: listing price BDT %.2f%s."
            % (
                markdown.name,
                price,
                ("; stock written down by BDT %.2f" % writedown) if writedown else "",
            )
        )
        return writedown

    @api.model
    def cron_refurb_nrv_review(self):
        """M14-25: a listed unit whose price before VAT no longer covers its
        carrying cost is flagged for a markdown (the write-down follows the
        approved markdown, never a typed figure)."""
        units = self.sudo().search([("state", "=", "resale_ready"), ("listing_price", ">", 0)])
        flagged = 0
        for rec in units:
            nrv = ex_vat(self.env, rec.company_id, rec.listing_price, dhaka_today(rec))
            carrying = rec._ledger_carrying()
            if carrying - nrv > _EPS:
                rec.activity_schedule(
                    "mail.mail_activity_data_todo",
                    summary="NRV below cost: raise a markdown",
                    note="Listing price BDT %.2f (BDT %.2f before VAT) is below the carrying cost "
                    "of BDT %.2f." % (rec.listing_price, nrv, carrying),
                    user_id=(rec.listing_price_approved_by_id or rec.create_uid).id,
                )
                flagged += 1
        return flagged

    # ------------------------------------------------- sale gates and posting
    def _tradein_sale_denial(self, stock) -> str:
        self.ensure_one()
        rec = self.sudo()
        if rec.written_off:
            return "trade-in %s is written off (parts only)" % rec.name
        if rec.state != "resale_ready":
            return "trade-in %s is %s, not resale-ready" % (rec.name, rec.state)
        denial = rec._wipe_gate_denial(rec.wipe_certificate_id, rec.device_id)
        if denial:
            return "Journey 9 wipe gate: %s" % denial
        denial = rec._provenance_denial()
        if denial:
            return "provenance / NEIR re-check: %s" % denial
        if rec.listing_price_state != "approved" or rec.listing_price <= 0:
            return "its listing price is not approved"
        if abs((stock.resale_price or 0.0) - rec.listing_price) > _EPS:
            return "its price BDT %.2f is not the approved listing price BDT %.2f" % (
                stock.resale_price,
                rec.listing_price,
            )
        if not rec._tradein_capitalised():
            return "the unit is not on the refurbished-stock ledger (the seller payout books it)"
        return ""

    def _provision_pct(self) -> float:
        self.ensure_one()
        grade = (self.grade or "").lower()
        if grade == "e":
            return 0.0
        key = PARAM_PROVISION_PCT % grade
        raw = (_param(self.env, key, "") or "").strip()
        try:
            return float(raw)
        except ValueError:
            raise UserError(
                "Sale refused: no warranty provision rate is set for grade %s. Set system "
                "parameter %s (D7/D11: A 2%%, B 3%%, C 5%%, D 7%%)." % (grade.upper() or "?", key)
            ) from None

    def _tradein_on_sold(self, stock):
        """The unit has left stock: Dr COGS / Cr refurbished stock at its
        carrying cost, and the grade's warranty provision on the ex-VAT price."""
        self.ensure_one()
        rec = self.sudo()
        sale_no = (rec.sale_count or 0) + 1
        carrying = rec._ledger_carrying()
        lines = [
            (
                rec._acct("cogs"),
                "Trade-in %s: cost of %s sold" % (rec.name, stock.name),
                carrying,
                0.0,
                None,
            ),
            (
                rec._acct("refurb_stock"),
                "Trade-in %s: %s out of stock" % (rec.name, stock.name),
                0.0,
                carrying,
                None,
            ),
        ]
        rec._ledger_post(
            "cogs", "cogs:s%d" % sale_no, carrying, -carrying, lines, "sale %d" % sale_no, sale_no
        )
        pct = rec._provision_pct()
        if pct > 0:
            base = ex_vat(self.env, rec.company_id, stock.resale_price, dhaka_today(rec))
            amount = round(base * pct / 100.0, 2)
            lines = [
                (
                    rec._acct("warranty_expense"),
                    "Trade-in %s: warranty provision %.2f%%" % (rec.name, pct),
                    amount,
                    0.0,
                    None,
                ),
                (
                    rec._acct("warranty_provision"),
                    "Trade-in %s: warranty provision" % rec.name,
                    0.0,
                    amount,
                    None,
                ),
            ]
            rec._ledger_post(
                "warranty_provision",
                "provision:s%d" % sale_no,
                amount,
                0.0,
                lines,
                "warranty provision, sale %d" % sale_no,
                sale_no,
            )
        rec._guarded().write({"sale_count": sale_no, "state": "closed"})
        rec.message_post(
            body="Sold as %s (sale %d): cost of sale BDT %.2f." % (stock.name, sale_no, carrying)
        )

    def _tradein_release_provision(self, sale_no, why):
        self.ensure_one()
        rec = self.sudo()
        provision = rec._ledger_row("provision:s%d" % sale_no)
        if not provision or rec._ledger_row("provision_release:s%d" % sale_no):
            return False
        amount = provision.amount
        lines = [
            (
                rec._acct("warranty_provision"),
                "Trade-in %s: provision released (%s)" % (rec.name, why),
                amount,
                0.0,
                None,
            ),
            (
                rec._acct("warranty_expense"),
                "Trade-in %s: provision released" % rec.name,
                0.0,
                amount,
                None,
            ),
        ]
        return rec._ledger_post(
            "warranty_release",
            "provision_release:s%d" % sale_no,
            amount,
            0.0,
            lines,
            "warranty provision released, sale %d (%s)" % (sale_no, why),
            sale_no,
        )

    def _tradein_on_returned(self, stock, reason=None):
        """M14-05: the buyer brought the unit back. Its cost comes back into
        stock, the first warranty closes (its provision released), an M14
        return is on record, and the unit is held for a new wipe, QA and grade."""
        self.ensure_one()
        rec = self.sudo()
        sale_no = rec.sale_count or 0
        cogs = rec._ledger_row("cogs:s%d" % sale_no)
        if cogs:
            amount = cogs.amount
            lines = [
                (
                    rec._acct("refurb_stock"),
                    "Trade-in %s: %s returned" % (rec.name, stock.name),
                    amount,
                    0.0,
                    None,
                ),
                (
                    rec._acct("cogs"),
                    "Trade-in %s: cost of sale reversed" % rec.name,
                    0.0,
                    amount,
                    None,
                ),
            ]
            rec._ledger_post(
                "cogs_reversal",
                "cogs_reversal:s%d" % sale_no,
                amount,
                amount,
                lines,
                "return of sale %d" % sale_no,
                sale_no,
            )
        Return = self.env["fix.refurb.return"].sudo()
        ret = Return.browse(self.env.context.get("refurb_return_id") or 0).exists()
        if not ret:
            ret = Return._guarded().create(
                {
                    "tradein_id": rec.id,
                    "company_id": rec.company_id.id,
                    "reason": "other",
                    "description": reason or "Returned by the buyer",
                    "state": "received",
                    "within_terms": True,
                    "received_by_id": self.env.uid,
                    "received_at": fields.Datetime.now(),
                }
            )
        warranties = (
            self.env["fix.tradein.warranty"]
            .sudo()
            .search(
                [
                    ("tradein_id", "=", rec.id),
                    ("state", "=", "active"),
                    ("sale_no", "in", (0, sale_no)),
                ]
            )
        )
        warranties._guarded().write({"state": "returned"})
        for w in warranties.filtered("device_warranty_id"):
            cover = w.device_warranty_id
            if "end_date" in cover._fields:
                cover.write({"end_date": dhaka_today(rec)})
        rec._tradein_release_provision(sale_no, "unit returned")
        if rec.wipe_certificate_id:
            # M14-05: the certificate of the sold life is spent; a new wipe follows
            rec._guarded().write({"spent_wipe_certificate_ids": [(4, rec.wipe_certificate_id.id)]})
        rec._guarded().write(
            {
                "state": "collected",
                "refurb_cycle": (rec.refurb_cycle or 0) + 1,
                "last_returned_at": fields.Datetime.now(),
                "wipe_certificate_id": False,
                "grade": False,
                "listing_price_state": "none",
                "listing_price_proposed": 0.0,
                "listing_price_proposed_by_id": False,
                "listing_price_approved_by_id": False,
                "listing_price_approved_at": False,
            }
        )
        rec.message_post(
            body="%s returned by the buyer (%s, return %s): held for a new data wipe, QA and "
            "grade before it is stocked again." % (stock.name, reason or "no reason", ret.name)
        )
        return ret

    # -------------------------------------------------- counter sale (M20)
    def _tradein_invoice_sale(self, stock, buyer, source, reason):
        """The AR invoice of a refurbished sale (M20), at the approved price,
        VAT inclusive, the VAT determined by M51 (D2: standard VAT on the full
        price). Idempotent per source document."""
        self.ensure_one()
        rec = self.sudo()
        day = dhaka_today(rec)
        taxable = ex_vat(self.env, rec.company_id, stock.resale_price, day)
        invoice = (
            self.env["fix.ar.invoice"]
            .sudo()
            ._fix_ar_invoice_from_source(
                source,
                buyer,
                [
                    {
                        "description": "Refurbished %s, grade %s (%s)"
                        % (
                            rec.device_model_id.name or rec.device_id.name or "device",
                            (rec.grade or "").upper(),
                            stock.name,
                        ),
                        "taxable_amount": taxable,
                    }
                ],
                reason,
                # D10(b): refurbished resale revenue, never the M20 service
                # revenue default (fails closed while the parameter is unset)
                credit_account=tradein_account(self.env, rec.company_id, "resale_revenue"),
                operating_unit=rec.operating_unit_id,
                branch=rec.branch_id or None,
                invoice_date=day,
                issue=True,
            )
        )
        rec._guarded().write({"sale_invoice_id": invoice.id})
        return invoice

    def action_counter_sell(self, buyer_id=None):
        """M14-15: a walk-in sale of a listed unit. An Inventory Controller
        sells it to a named buyer; the M20 invoice carries the M51 VAT."""
        if not (
            self.env.su
            or self.env.user.has_group(GROUP_STOCK_CONTROLLER)
            or self.env.user.has_group(GROUP_REFURB_SUPERVISOR)
        ):
            raise AccessError(
                "A counter sale of a refurbished unit is made by an Inventory Controller."
            )
        try:
            buyer = self.env["res.partner"].sudo().browse(int(buyer_id or 0)).exists()
        except (TypeError, ValueError):
            buyer = self.env["res.partner"]
        if not buyer:
            raise UserError("Name the buyer of the refurbished unit.")
        invoices = self.env["fix.ar.invoice"]
        for rec in self:
            stock = rec.sudo().graded_stock_id
            if not stock or stock.state != "in_stock":
                raise UserError(
                    "Trade-in %s has no unit on the shelf to sell (%s)."
                    % (rec.name, stock.state if stock else "not stocked")
                )
            stock._fix_assert_saleable("Counter sale of %s" % stock.name)
            invoice = rec._tradein_invoice_sale(
                stock, buyer, stock, "Counter sale of refurbished unit %s" % stock.name
            )
            stock.sudo().action_sell()
            invoices |= invoice
        return invoices.ids

    # ------------------------------------------- I1: M13 retirement -> intake
    @api.model
    def consume_rental_asset_retired(self, event):
        """I1 consumer of rental.asset_retired: a retired rental unit routed to
        resale becomes a COMPANY-OWNED trade-in intake (source
        rental_retirement, no seller payout). Superuser only (the relay); one
        intake per asset; the payload is re-read from the asset when M13 is
        installed. The unit then goes through the wipe gate, refurbishment,
        QA, grading and price approval like any other."""
        if not self.env.su:
            raise AccessError("Rental retirements are consumed only by the event relay.")
        payload = event.get("payload") or {}
        if (payload.get("route") or "") != "resale":
            return {"created": False, "reason": "route %s is not resale" % payload.get("route")}
        try:
            asset_id = int(payload.get("asset_id") or event.get("aggregate_id") or 0)
        except (TypeError, ValueError):
            asset_id = 0
        if not asset_id:
            raise UserError("Rental retirement intake refused: the event names no asset.")
        existing = self.sudo().search([("rental_asset_id", "=", asset_id)], limit=1)
        if existing:
            return {"model": self._name, "id": existing.id, "created": False}
        Asset = self.env.get("fix.rental.asset")
        asset = Asset.sudo().browse(asset_id).exists() if Asset is not None else None
        if Asset is not None:
            if not asset:
                raise UserError("Rental retirement intake refused: no rental asset #%s." % asset_id)
            if asset.status != "retired":
                raise UserError(
                    "Rental retirement intake refused: %s is %s, not retired."
                    % (asset.name, asset.status)
                )
        device_id = (asset.device_id.id if asset else False) or payload.get("device_id") or False
        company_id = (
            asset.company_id.id if asset and "company_id" in asset._fields else False
        ) or (payload.get("company_id") or event.get("company_id"))
        ou_id = payload.get("operating_unit_id") or (
            asset.operating_unit_id.id if asset and "operating_unit_id" in asset._fields else False
        )
        if not (device_id and company_id and ou_id):
            raise UserError(
                "Rental retirement intake refused: the device, company and operating unit of "
                "the retired asset are all needed."
            )
        company = self.env["res.company"].browse(int(company_id))
        try:
            book_value = round(float(payload.get("book_value") or 0.0), 2)
        except (TypeError, ValueError):
            book_value = 0.0
        vals = {
            "company_id": company.id,
            "customer_id": company.partner_id.id,
            "device_id": int(device_id),
            "operating_unit_id": int(ou_id),
            "offered_value": 0.0,
            "source": "rental_retirement",
            "rental_asset_id": asset_id,
            "intake_channel": "corporate",
        }
        if payload.get("branch_id"):
            vals["branch_id"] = int(payload["branch_id"])
        rec = self.sudo()._guarded().create(vals)
        rec = self.sudo().browse(rec.id)
        rec._guarded().write(
            {
                "state": "collected",
                "graded_value": book_value,
                "accepted_offer_value": book_value,
                "accepted_at": fields.Datetime.now(),
                "hold_until": dhaka_today(rec),
                "hold_released": True,
            }
        )
        # the unit's carrying value is its book value, transferred into the
        # refurbished stock by M13's retirement posting (no seller, no payout)
        rec._ledger_post(
            "transfer_in",
            "transfer_in",
            book_value,
            book_value,
            [],
            "transferred from rental asset #%s at book value" % asset_id,
        )
        rec.message_post(
            body="Company-owned intake from retired rental asset #%s (book value BDT %.2f): no "
            "seller payout. The wipe gate, refurbishment, QA and grading apply."
            % (asset_id, book_value)
        )
        return {"model": self._name, "id": rec.id, "created": True}

    # -------------------------------------------------- I4: buyer disclosure
    @api.depends(
        "grade",
        "battery_health_pct",
        "declared_faults",
        "refurbishment_ids.state",
        "wipe_certificate_id",
        "provenance_ids.state",
        "provenance_ids.btrc_neir_status",
    )
    def _compute_buyer_disclosure(self):
        from markupsafe import escape

        for rec in self:
            t = rec.sudo()
            if not (t.grade and t.wipe_certificate_id):
                rec.buyer_disclosure_html = False
                continue
            qa = t._qa_latest()
            cert = t._grade_certificate()
            cycle = t.refurb_cycle
            steps = t.refurbishment_ids.filtered(
                lambda s, c=cycle: s.state == "done" and s.step != "intake" and s.cycle == c
            )
            repairs = (
                ", ".join(
                    "%s%s"
                    % (
                        dict(s._fields["step"].selection).get(s.step, s.step),
                        (": %s" % s.notes) if s.notes else "",
                    )
                    for s in steps
                )
                or "none recorded"
            )
            prov = t._provenance_current()
            months = t._warranty_months()
            rows = [
                ("Device", t.device_model_id.name or t.device_id.name or ""),
                (
                    "Grade",
                    (t.grade or "").upper()
                    + (" (%s)" % t.refurb_grade_id.name if t.refurb_grade_id else ""),
                ),
                ("Battery health", "%d%%" % (t.battery_health_pct or 0)),
                (
                    "Defects disclosed",
                    (cert.notes if cert and cert.notes else "")
                    or t.declared_faults
                    or "none recorded",
                ),
                ("Repairs carried out", repairs),
                (
                    "QA result",
                    "%s (%s of %s tests passed)" % (qa.name, qa.tests_passed, qa.tests_total)
                    if qa
                    else "none",
                ),
                ("Warranty", "%d months from the sale" % months),
                ("Data wipe certificate", t.wipe_certificate_id.name or ""),
                (
                    "Provenance",
                    "screen %s cleared %s, NEIR %s"
                    % (prov.name, prov.checked_on, prov.btrc_neir_status)
                    if prov
                    else "no current screen",
                ),
            ]
            body = "".join(
                "<tr><th>%s</th><td>%s</td></tr>" % (escape(k), escape(v)) for k, v in rows
            )
            rec.buyer_disclosure_html = (
                '<table class="fix-buyer-disclosure"><tbody>%s</tbody></table>' % body
            )

    def _warranty_months(self) -> int:
        self.ensure_one()
        grade = (self.grade or "").lower()
        per_grade = _param(self.env, PARAM_WARRANTY_MONTHS_GRADE % grade, "") if grade else ""
        try:
            months = int(float(per_grade)) if per_grade else 0
        except ValueError:
            months = 0
        return months or int(_param_float(self.env, "cd_tradein.resale_warranty_months", 6)) or 6

    # ------------------------------------------------------ warranty expiry
    @api.model
    def cron_refurb_warranty_expiry(self):
        """M14-32: a refurbished warranty past its end date expires, and its
        unused provision is released (D7)."""
        today = dhaka_today(self)
        due = (
            self.env["fix.tradein.warranty"]
            .sudo()
            .search([("state", "=", "active"), ("end_date", "!=", False), ("end_date", "<", today)])
        )
        for w in due:
            w._guarded().write({"state": "expired"})
            if w.sale_no:
                w.tradein_id._tradein_release_provision(w.sale_no, "warranty expired")
        return len(due)


# =========================================================================== stock
class FixGradedStockTradein(models.Model):
    """The trade-in side of a graded unit's sale gates and its ledger."""

    _inherit = "fix.graded.stock"

    def _tradein(self):
        self.ensure_one()
        return self.env["fix.tradein.request"].sudo().browse(self.tradein_id or 0).exists()

    def _fix_sale_denial(self) -> str:
        denial = super()._fix_sale_denial()
        if denial:
            return denial
        tradein = self._tradein()
        if not tradein:
            return ""
        return tradein._tradein_sale_denial(self)

    def _fix_cogs_relieved(self) -> float:
        tradein = self._tradein()
        if not tradein:
            return super()._fix_cogs_relieved()
        row = tradein._ledger_row("cogs:s%d" % (tradein.sale_count or 0))
        return row.amount if row else 0.0

    def action_sell(self):
        result = super().action_sell()
        for rec in self:
            tradein = rec._tradein()
            if tradein:
                tradein._tradein_on_sold(rec)
        return result

    def action_receive_return(self, reason=None):
        result = super().action_receive_return(reason=reason)
        for rec in self:
            tradein = rec._tradein()
            if tradein:
                tradein._tradein_on_returned(rec, reason)
        return result
