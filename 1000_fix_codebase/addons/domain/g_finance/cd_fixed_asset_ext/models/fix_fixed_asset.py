# fix_fixed_asset — M49: the asset register and CWIP (P08-M08, A08 rebuild).
# Book depreciation is straight-line; the per-month amount comes from a PURE
# function (100% covered, DoD-03) and is posted to the GL by the depreciation
# run (fix.asset.depreciation.run), idempotent per asset, book and month.
# Every event this module publishes is published from THIS file (the event
# contracts in contracts/events list it as the publisher).
from decimal import ROUND_HALF_UP, Decimal

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

from .fix_asset_common import (
    USER_GROUP,
    money,
    month_end,
    month_start,
    post_entry,
    require_accounts,
    require_group,
)

ACTIVE_STATES = ("active", "disposed")


def straight_line_monthly(gross: Decimal, salvage: Decimal, life_months: int) -> Decimal:
    """SL depreciation per month: (gross - salvage) / life, 2dp, never
    negative. The financial path's single authority (100% covered)."""
    if life_months <= 0:
        raise ValueError("life must be positive months")
    if salvage < 0 or gross < 0:
        raise ValueError("gross and salvage cannot be negative")
    if salvage > gross:
        raise ValueError("salvage above gross")
    monthly = (gross - salvage) / Decimal(life_months)
    return monthly.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def remaining_straight_line(carrying: float, salvage: float, remaining_months: int) -> float:
    """The month's book charge after revaluation/impairment (IAS 16.50):
    the depreciable carrying amount spread over the REMAINING life; the last
    month takes the whole remainder so the asset lands exactly on salvage."""
    if remaining_months <= 0:
        return 0.0
    base = money(carrying) - money(salvage)
    if base <= 0.0:
        return 0.0
    if remaining_months == 1:
        return money(base)
    return money(base / remaining_months)


def reducing_balance_monthly(wdv: float, rate_percent: float) -> float:
    """Tax (ITA 2023 Third Schedule) reducing balance: WDV x rate / 12."""
    if wdv <= 0.0 or rate_percent <= 0.0:
        return 0.0
    return money(wdv * rate_percent / 100.0 / 12.0)


class FixFixedAsset(models.Model):
    _name = "fix.fixed.asset"
    _description = "Fixed Asset"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "purchase_date desc, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Branch", tracking=True)
    name = fields.Char(required=True)
    code = fields.Char(
        string="Asset Tag", copy=False, index=True, tracking=True, help="Barcode / tag label."
    )
    category_id = fields.Many2one("fix.asset.category", string="Asset Category", tracking=True)
    category = fields.Char(
        string="Category Label",
        required=True,
        compute="_compute_category_label",
        store=True,
        readonly=False,
        precompute=True,
    )
    custodian_id = fields.Many2one("hr.employee", string="Custodian", tracking=True)
    seam_id = fields.Many2one(
        "fix.fixed.asset.seam",
        string="Capitalisation Seam (M19)",
        help="Finance posted the capitalisation event; this asset consumed it (AR-006 pair 14)",
    )
    capex_request_id = fields.Many2one("fix.capex.request", string="Capex Request", readonly=True)
    lease_id = fields.Many2one("fix.lease", string="Lease (IFRS 16)", readonly=True)
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    gross = fields.Monetary(string="Gross", currency_field="currency_id", required=True)
    salvage = fields.Monetary(string="Salvage Value", currency_field="currency_id")
    life_months = fields.Integer(string="Useful Life (Months)", required=True)
    purchase_date = fields.Date(string="Acquisition Date", required=True)
    depreciation_start = fields.Date(
        string="Depreciation Start",
        compute="_compute_depreciation_start",
        store=True,
        readonly=False,
        precompute=True,
        help="First month charged: the acquisition month by default.",
    )
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("disposed", "Disposed")],
        default="draft",
        required=True,
        tracking=True,
    )
    disposal_date = fields.Date(string="Disposal Date", readonly=True, copy=False)
    monthly_depreciation = fields.Monetary(
        string="Monthly Depreciation",
        currency_field="currency_id",
        compute="_compute_depreciation",
        store=True,
    )
    budget_reference = fields.Char(
        string="Budget Reference (Advisory)",
        help="AR-006 5.4 NOT-A-PREREQ: M49 does NOT read M54. This is a "
        "free-text advisory pointer, deliberately NOT a relation — "
        "the M49<->M54 break",
    )
    depreciation_line_ids = fields.One2many(
        "fix.asset.depreciation.line", "asset_id", string="Depreciation Lines"
    )
    transfer_ids = fields.One2many("fix.asset.transfer", "asset_id", string="Transfer History")
    revaluation_ids = fields.One2many(
        "fix.asset.revaluation", "asset_id", string="Revaluations & Impairments"
    )
    disposal_ids = fields.One2many("fix.asset.disposal", "asset_id", string="Disposals")

    cost = fields.Monetary(
        string="Cost / Revalued Amount", currency_field="currency_id", compute="_compute_book"
    )
    accumulated_depreciation = fields.Monetary(
        string="Accumulated Depreciation", currency_field="currency_id", compute="_compute_book"
    )
    impairment_total = fields.Monetary(
        string="Accumulated Impairment", currency_field="currency_id", compute="_compute_book"
    )
    book_nbv = fields.Monetary(
        string="Net Book Value", currency_field="currency_id", compute="_compute_book"
    )
    revaluation_surplus = fields.Monetary(
        string="Revaluation Surplus", currency_field="currency_id", compute="_compute_book"
    )
    tax_accumulated = fields.Monetary(
        string="Tax Depreciation to Date", currency_field="currency_id", compute="_compute_book"
    )
    tax_wdv = fields.Monetary(
        string="Tax Written-Down Value", currency_field="currency_id", compute="_compute_book"
    )
    book_months_done = fields.Integer(string="Months Depreciated", compute="_compute_book")

    _code_company_uniq = models.Constraint(
        "UNIQUE (company_id, code)", "An asset tag is unique per company."
    )

    # ------------------------------------------------------------------
    # computes
    # ------------------------------------------------------------------
    @api.depends("category_id")
    def _compute_category_label(self):
        for rec in self:
            # The label column is required: an asset entered without a
            # category (the workspace form allows it) still gets the honest
            # "Uncategorised" instead of a NOT NULL refusal.
            rec.category = (
                rec.category_id.name if rec.category_id else (rec.category or "Uncategorised")
            )

    @api.depends("purchase_date")
    def _compute_depreciation_start(self):
        for rec in self:
            if rec.purchase_date and not rec.depreciation_start:
                rec.depreciation_start = month_start(rec.purchase_date)
            elif not rec.depreciation_start:
                rec.depreciation_start = False

    @api.depends("gross", "salvage", "life_months")
    def _compute_depreciation(self):
        for rec in self:
            if rec.life_months > 0:
                try:
                    monthly = straight_line_monthly(
                        Decimal(str(rec.gross)), Decimal(str(rec.salvage or 0)), rec.life_months
                    )
                except ValueError as e:  # a user-facing refusal, not a server error
                    raise ValidationError("Asset %s: %s" % (rec.name, e)) from e
                rec.monthly_depreciation = float(monthly)
            else:
                rec.monthly_depreciation = 0.0

    @api.depends(
        "gross",
        "depreciation_line_ids.amount",
        "depreciation_line_ids.state",
        "revaluation_ids.state",
        "disposal_ids.state",
    )
    def _compute_book(self):
        for rec in self:
            pos = rec._position()
            rec.cost = pos["cost"]
            rec.accumulated_depreciation = pos["dep"]
            rec.impairment_total = pos["imp"]
            rec.book_nbv = money(pos["cost"] - pos["dep"] - pos["imp"])
            rec.revaluation_surplus = pos["surplus"]
            rec.tax_accumulated = pos["tax"]
            rec.tax_wdv = money(rec.gross - pos["tax"]) if not pos["disposed"] else 0.0
            rec.book_months_done = len(
                rec.depreciation_line_ids.filtered(
                    lambda ln: ln.book == "book" and ln.state == "posted"
                )
            )

    def _position(self, before=None):
        """Book position from POSTED events strictly before `before` (all
        posted events when None): cost (incl. revaluation), accumulated
        depreciation, net impairment, surplus and tax depreciation. A posted
        disposal before the cut-off removes the asset (all zeros)."""
        self.ensure_one()
        zero = {
            "cost": 0.0,
            "dep": 0.0,
            "imp": 0.0,
            "surplus": 0.0,
            "tax": 0.0,
            "disposed": False,
        }

        def _in(day):
            return before is None or (day and day < before)

        if self.state not in ACTIVE_STATES or not _in(self.purchase_date):
            return zero
        disposal = self.disposal_ids.filtered(lambda d: d.state == "posted")[:1]
        if disposal and _in(disposal.date):
            return dict(zero, disposed=True)
        revals = self.revaluation_ids.filtered(lambda r: r.state == "posted" and _in(r.date))
        lines = self.depreciation_line_ids.filtered(
            lambda ln: ln.state == "posted" and _in(month_end(ln.period_start))
        )
        return {
            "cost": money(self.gross + sum(revals.mapped("cost_delta"))),
            "dep": money(sum(lines.filtered(lambda ln: ln.book == "book").mapped("amount"))),
            "imp": money(sum(revals.mapped("accum_delta"))),
            "surplus": money(sum(revals.mapped("surplus_amount"))),
            "tax": money(sum(lines.filtered(lambda ln: ln.book == "tax").mapped("amount"))),
            "disposed": False,
        }

    # ------------------------------------------------------------------
    # ORM
    # ------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        Category = self.env["fix.asset.category"]
        for vals in vals_list:
            cat = Category.browse(vals["category_id"]) if vals.get("category_id") else Category
            if cat and not vals.get("life_months"):
                vals["life_months"] = cat.useful_life_months
            if cat and "salvage" not in vals and vals.get("gross"):
                vals["salvage"] = money(vals["gross"] * cat.salvage_percent / 100.0)
            if not vals.get("code"):
                vals["code"] = self.env["ir.sequence"].next_by_code("fix.fixed.asset") or False
        recs = super().create(vals_list)
        for rec in recs:
            if rec.seam_id and not rec.seam_id.consumed:
                rec.seam_id.action_mark_consumed()
            publish(
                self.env,
                "asset.capitalized",
                "fix.fixed.asset",
                rec.id,
                {"name": rec.name, "gross": float(rec.gross)},
            )
        return recs

    @api.ondelete(at_uninstall=False)
    def _unlink_only_drafts(self):
        if any(rec.state != "draft" for rec in self):
            raise UserError(self.env._("Only draft assets can be deleted — dispose of the others."))

    # ------------------------------------------------------------------
    # depreciation amounts (used by the depreciation run)
    # ------------------------------------------------------------------
    def _book_amount(self, period):
        """Book charge for `period` (IAS 16 straight-line over the remaining
        life, so revaluations/impairments re-spread automatically)."""
        self.ensure_one()
        earlier = self.depreciation_line_ids.filtered(
            lambda ln: ln.book == "book" and ln.period_start < period
        )
        pos = self._position()
        carrying = pos["cost"] - sum(earlier.mapped("amount")) - pos["imp"]
        return remaining_straight_line(
            carrying, self.salvage or 0.0, self.life_months - len(earlier)
        )

    def _tax_amount(self, period, rate_percent):
        self.ensure_one()
        earlier = self.depreciation_line_ids.filtered(
            lambda ln: ln.book == "tax" and ln.period_start < period
        )
        return reducing_balance_monthly(self.gross - sum(earlier.mapped("amount")), rate_percent)

    # ------------------------------------------------------------------
    # workflow
    # ------------------------------------------------------------------
    def action_activate(self):
        """Put a registered (draft) asset into service. Acquisition cost is
        already in the GL from the vendor bill / the M19 seam / CWIP, so
        activation posts nothing; depreciation starts in its start month."""
        require_group(self.env, USER_GROUP, "Activating an asset")
        for rec in self:
            if rec.state != "draft":
                raise UserError(self.env._("Only draft assets can be put into service."))
            if not rec.category_id:
                raise UserError(
                    self.env._("Choose the asset category of %s first.", rec.display_name)
                )
            if rec.gross <= 0:
                raise UserError(self.env._("The asset cost must be above zero."))
            rec.state = "active"

    def action_accrue_month(self):
        """Depreciate the selected asset(s) for the CURRENT month on the
        accounting book and post the GL entry (Dr depreciation expense / Cr
        accumulated depreciation). Idempotent: a second call in the same
        month is refused — one depreciation line per asset, book and month."""
        for rec in self:
            if rec.state != "active":
                raise UserError("Only ACTIVE assets accrue depreciation")
        period = month_start(fields.Date.context_today(self))
        self.env["fix.asset.depreciation.run"]._depreciate(self, period, "book")
        return True

    def _publish_depreciation(self, amount):
        """The monthly accrual M54 consumes (AR-006 4.1 pair 14): the EVENT
        carries the posted amount; M49 never reads budgets."""
        self.ensure_one()
        publish(
            self.env,
            "depreciation.accrued",
            "fix.fixed.asset",
            self.id,
            {"asset": self.name, "amount": float(amount)},
        )

    def action_dispose(self):
        """Start a disposal: a DRAFT write-off document the disposal screen
        approves (SoD) and posts with its gain/loss. Nothing changes in the
        GL until that posting."""
        disposals = self.env["fix.asset.disposal"]
        for rec in self:
            if rec.state != "active":
                raise UserError(self.env._("Only active assets can be disposed of."))
            draft = rec.disposal_ids.filtered(lambda d: d.state in ("draft", "approved"))
            disposals |= draft or disposals.create(
                {"asset_id": rec.id, "kind": "write_off", "date": fields.Date.context_today(rec)}
            )
        return {"disposal_ids": disposals.ids}

    def _mark_disposed(self, on_date):
        for rec in self:
            rec.write({"state": "disposed", "disposal_date": on_date})
            publish(self.env, "asset.disposed", "fix.fixed.asset", rec.id, {"name": rec.name})


class FixCwipEntry(models.Model):
    """Capital work in progress: costs accumulate, then capitalise."""

    _name = "fix.cwip.entry"
    _description = "CWIP Entry"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Branch")
    name = fields.Char(required=True)
    description = fields.Text(string="Description")
    capex_request_id = fields.Many2one(
        "fix.capex.request", string="Capex Request", index=True, tracking=True
    )
    category_id = fields.Many2one("fix.asset.category", string="Asset Category", tracking=True)
    life_months = fields.Integer(string="Useful Life (Months)")
    salvage = fields.Monetary(string="Salvage Value", currency_field="currency_id")
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    amount = fields.Monetary(
        string="Accumulated Cost",
        currency_field="currency_id",
        required=True,
        tracking=True,
        help="Costs booked to the CWIP account so far (vendor bills of the project).",
    )
    state = fields.Selection(
        [("open", "Open"), ("capitalised", "Capitalised")],
        default="open",
        required=True,
        tracking=True,
    )
    asset_id = fields.Many2one("fix.fixed.asset", string="Resulting Asset", readonly=True)
    move_id = fields.Many2one(
        "account.move", string="Capitalisation Entry", readonly=True, copy=False
    )

    def _resolve_category(self, category):
        if not category:
            return self.category_id
        if isinstance(category, models.BaseModel):
            return category
        Category = self.env["fix.asset.category"]
        if isinstance(category, int):
            return Category.browse(category).exists()
        return Category.search(
            [
                ("company_id", "=", self.company_id.id),
                "|",
                ("code", "=", category),
                ("name", "=", category),
            ],
            limit=1,
        )

    def action_capitalise(self, category=None, life_months=None, salvage=None):
        """CWIP -> fixed asset: the accumulated cost becomes the gross and is
        reclassified in the GL (Dr asset account / Cr CWIP account).

        Every entry in the recordset is capitalised and the asset is
        registered to the entry's OWN company / operating unit. Missing
        posting accounts fail closed (nothing is created)."""
        require_group(self.env, USER_GROUP, "Capitalising CWIP")
        assets = self.env["fix.fixed.asset"]
        for rec in self:
            if rec.state != "open":
                raise UserError("CWIP entry already capitalised")
            if rec.amount <= 0:
                raise UserError("Nothing accumulated to capitalise")
            cat = rec._resolve_category(category)
            if not cat:
                raise UserError(self.env._("Choose the asset category of %s first.", rec.name))
            life = life_months or rec.life_months or cat.useful_life_months
            residual = salvage if salvage is not None else rec.salvage
            request = rec.capex_request_id
            if request and money(rec.amount) > money(request.amount):
                raise UserError(
                    self.env._(
                        "%s: the accumulated cost exceeds the approved capex "
                        "(%s) — raise a supplementary capex request first.",
                        rec.name,
                        request.amount,
                    )
                )
            require_accounts(
                cat, ["journal_id", "asset_account_id", "cwip_account_id"], "CWIP capitalisation"
            )
            today = fields.Date.context_today(rec)
            move = post_entry(
                rec.env,
                rec.company_id,
                cat.journal_id,
                today,
                "CWIP capitalisation: %s" % rec.name,
                [
                    (cat.asset_account_id, rec.amount, 0.0, rec.name),
                    (cat.cwip_account_id, 0.0, rec.amount, rec.name),
                ],
            )
            asset = self.env["fix.fixed.asset"].create(
                {
                    "company_id": rec.company_id.id,
                    "operating_unit_id": rec.operating_unit_id.id,
                    "name": rec.name,
                    "category_id": cat.id,
                    "gross": rec.amount,
                    "salvage": residual or 0.0,
                    "life_months": life,
                    "purchase_date": today,
                    "capex_request_id": request.id,
                    "state": "active",
                }
            )
            rec.write({"state": "capitalised", "asset_id": asset.id, "move_id": move.id})
            if request and request.state == "cwip":
                request.state = "capitalised"
            publish(
                self.env,
                "cwip.capitalised",
                "fix.cwip.entry",
                rec.id,
                {"asset": asset.name, "amount": float(rec.amount)},
            )
            assets |= asset
        return assets
