# fix_fixed_asset — M49: the asset register and CWIP (P08-M08, A08 rebuild).
# Book depreciation is straight-line; the per-month amount comes from a PURE
# function (100% covered, DoD-03) and is posted to the GL by the depreciation
# run (fix.asset.depreciation.run), idempotent per asset, book and month.
# Every event this module publishes is published from THIS file (the event
# contracts in contracts/events list it as the publisher).
#
# A08 workflow audit (2026-11-04):
#   M49-1/2  an asset was born `active` with no capex and no acquisition entry,
#            and depreciated; `state='disposed'` was written with no disposal.
#            The state, custodian and branch are guarded: an asset becomes
#            active only through its capitalisation (CWIP, lease) or the M19
#            capitalisation seam, moves only by an acknowledged transfer, and
#            leaves only by a posted disposal.
#   M49-3    CWIP `amount` was typed. It is now the posted cost booked to the
#            category's CWIP account and linked to the project (_fix_book_cost
#            — the M52 capital-invoice hand-off), never more than the CWIP GL
#            balance.
#   M49-4    gross / life were edited after depreciation: frozen once active.
#   M49-8    the tax book compounded WDV x rate / 12 (26,200 instead of 30,000
#            at 30%): it now charges the annual written-down value, from the
#            M51 Third Schedule master, refusing a rate not yet confirmed.
#   M49-11   asset.capitalized was published on every create, even drafts: it
#            is published on capitalisation only, and the M49 events have a
#            registered consumer (consume_asset_event).
from decimal import ROUND_HALF_UP, Decimal

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish

from .fix_asset_common import (
    CLOSE_GATE,
    CLOSE_GATE_TOLERANCE,
    USER_GROUP,
    add_months,
    float_param,
    money,
    month_end,
    month_start,
    post_entry,
    require_accounts,
    require_group,
)

ACTIVE_STATES = ("active", "disposed")
# frozen once the asset is in service (BRU-FXA-10: a change needs approval and
# is prospective; until that document exists the figures do not move)
ASSET_TERMS = (
    "gross",
    "salvage",
    "life_months",
    "purchase_date",
    "depreciation_start",
    "category_id",
    "currency_id",
    "company_id",
)


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


def annual_wdv_month(opening_wdv: float, rate_percent: float, month_in_year: int, charged: float):
    """Tax (ITA 2023 Third Schedule) reducing balance on the ANNUAL written-
    down value: the year's allowance is opening WDV x rate, spread over its
    12 months; the 12th month takes the remainder (A08 M49-8). The year runs
    from the asset's first tax month; the year-of-acquisition and disposal
    rules are for the tax adviser to confirm."""
    if opening_wdv <= 0.0 or rate_percent <= 0.0:
        return 0.0
    annual = money(opening_wdv * rate_percent / 100.0)
    if month_in_year >= 11:
        return money(max(annual - charged, 0.0))
    return money(annual / 12.0)


def reducing_balance_monthly(wdv: float, rate_percent: float) -> float:
    """DEPRECATED (A08 M49-8): WDV x rate / 12 compounded monthly understates
    the annual allowance. Kept for callers outside M49; the run uses
    annual_wdv_month."""
    if wdv <= 0.0 or rate_percent <= 0.0:
        return 0.0
    return money(wdv * rate_percent / 100.0 / 12.0)


class FixJournalPostingLogAsset(models.Model):
    """The fixed-asset register as a posting source in M19's posting log."""

    _inherit = "fix.journal.posting.log"

    source = fields.Selection(
        selection_add=[("fixed_asset", "Fixed Assets (M49)")],
        ondelete={"fixed_asset": lambda recs: recs.write({"source": "api"})},
    )


class FixFixedAsset(models.Model):
    _name = "fix.fixed.asset"
    _description = "Fixed Asset"
    _inherit = ["fix.guarded.mixin", "mail.thread", "mail.activity.mixin"]
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
    cwip_id = fields.Many2one("fix.cwip.entry", string="CWIP Project", readonly=True, copy=False)
    lease_id = fields.Many2one("fix.lease", string="Lease (IFRS 16)", readonly=True)
    acquisition_move_id = fields.Many2one(
        "account.move", string="Acquisition Entry", readonly=True, copy=False
    )
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
    # guard
    # ------------------------------------------------------------------
    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "disposal_date",
            "capex_request_id",
            "cwip_id",
            "lease_id",
            "acquisition_move_id",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields() | {"custodian_id", "operating_unit_id"}
        if self and self.state != "draft":
            locked |= set(ASSET_TERMS) | {"seam_id"}
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open():
            # BRU-FXA-09 (M49-12): custodian and branch move only through an
            # acknowledged transfer; M49-4: the cost basis is frozen in service
            for rec in self:
                moved = [
                    n
                    for n in ("custodian_id", "operating_unit_id")
                    if n in vals and rec._fix_guard_differs(n, vals[n], rec[n])
                ]
                if moved and rec.state != "draft":
                    raise UserError(
                        self.env._(
                            "%s: the custodian and branch change only through an asset "
                            "transfer, acknowledged by the receiver.",
                            rec.display_name,
                        )
                    )
                frozen = [
                    n
                    for n in (*ASSET_TERMS, "seam_id")
                    if n in vals and rec._fix_guard_differs(n, vals[n], rec[n])
                ]
                if frozen and rec.state != "draft":
                    raise UserError(
                        self.env._(
                            "%s is in service: its cost, life and category are frozen (%s). "
                            "A revaluation / impairment changes the carrying amount.",
                            rec.display_name,
                            ", ".join(frozen),
                        )
                    )
        return super().write(vals)

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
        return super().create(vals_list)

    @api.ondelete(at_uninstall=False)
    def _unlink_only_drafts(self):
        if any(rec.state != "draft" for rec in self):
            raise UserError(self.env._("Only draft assets can be deleted — dispose of the others."))

    # ------------------------------------------------------------------
    # depreciation amounts (used by the depreciation run)
    # ------------------------------------------------------------------
    def _posted_lines(self, book, before=None):
        self.ensure_one()
        return self.depreciation_line_ids.filtered(
            lambda ln: (
                ln.book == book
                and ln.state == "posted"
                and (before is None or ln.period_start < before)
            )
        )

    def _book_amount(self, period):
        """Book charge for `period` (IAS 16 straight-line over the remaining
        life, so revaluations/impairments re-spread automatically). Only
        POSTED months count as charged (A08 M49-7: an abandoned computed run
        no longer holds a month)."""
        self.ensure_one()
        earlier = self._posted_lines("book", period)
        pos = self._position()
        carrying = pos["cost"] - sum(earlier.mapped("amount")) - pos["imp"]
        return remaining_straight_line(
            carrying, self.salvage or 0.0, self.life_months - len(earlier)
        )

    def _tax_amount(self, period, rate_percent):
        """Annual written-down value (A08 M49-8): the allowance of each tax
        year (12 months from the first tax month) is the year's opening WDV x
        rate, spread over its months."""
        self.ensure_one()
        start = month_start(self.depreciation_start or self.purchase_date)
        months_since = (period.year - start.year) * 12 + period.month - start.month
        if months_since < 0:
            return 0.0
        year_start = add_months(start, (months_since // 12) * 12)
        before_year = sum(self._posted_lines("tax", year_start).mapped("amount"))
        in_year = sum(
            self._posted_lines("tax", period)
            .filtered(lambda ln: ln.period_start >= year_start)
            .mapped("amount")
        )
        amount = annual_wdv_month(
            money(self.gross - before_year), rate_percent, months_since % 12, in_year
        )
        remaining = money(self.gross - before_year - in_year)
        return money(min(amount, max(remaining, 0.0)))

    # ------------------------------------------------------------------
    # workflow
    # ------------------------------------------------------------------
    def _fix_activate_from_source(self, move=None):
        """Put the asset in service from its capitalisation (system)."""
        for rec in self:
            rec._guarded().write(
                {"state": "active", "acquisition_move_id": move.id if move else False}
            )
            rec._publish_capitalized(move)

    def action_activate(self):
        """Put a registered (draft) asset into service. BRU-FXA-01 (A08
        M49-2): only from its source — the M19 capitalisation seam whose
        posted journal item carries the cost on the category's asset account.
        CWIP and lease assets come into service through their capitalisation."""
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
            seam = rec.seam_id.sudo()
            line = seam.move_line_id
            if not seam or seam.consumed:
                raise UserError(
                    self.env._(
                        "%s has no source: an asset is put into service from its approved "
                        "capex (CWIP capitalisation), its lease, or an unconsumed M19 "
                        "capitalisation seam (BRU-FXA-01).",
                        rec.display_name,
                    )
                )
            if (
                line.parent_state != "posted"
                or line.account_id != rec.category_id.asset_account_id
                or abs(money(line.balance) - money(rec.gross)) > 0.005
            ):
                raise UserError(
                    self.env._(
                        "The seam of %s does not carry its cost: a posted debit of %s on the "
                        "category's asset account is required.",
                        rec.display_name,
                        rec.gross,
                    )
                )
            seam.action_mark_consumed()
            rec._fix_activate_from_source(line.move_id)

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

    def _publish_capitalized(self, move=None):
        self.ensure_one()
        publish(
            self.env,
            "asset.capitalized",
            "fix.fixed.asset",
            self.id,
            {
                "name": self.name,
                "gross": float(self.gross),
                "move_id": move.id if move else False,
                "cwip_id": self.cwip_id.id or False,
                "lease_id": self.lease_id.id or False,
            },
        )

    def _publish_depreciation(self, amount, move=None):
        """The monthly accrual M54 consumes (AR-006 4.1 pair 14): the EVENT
        carries the posted amount; M49 never reads budgets."""
        self.ensure_one()
        publish(
            self.env,
            "depreciation.accrued",
            "fix.fixed.asset",
            self.id,
            {"asset": self.name, "amount": float(amount), "move_id": move.id if move else False},
        )

    def action_dispose(self):
        """Start a disposal: a DRAFT write-off document the disposal screen
        routes for approval and posts with its gain/loss. Nothing changes in
        the GL until that posting."""
        disposals = self.env["fix.asset.disposal"]
        for rec in self:
            if rec.state != "active":
                raise UserError(self.env._("Only active assets can be disposed of."))
            draft = rec.disposal_ids.filtered(
                lambda d: d.state in ("draft", "submitted", "approved")
            )
            disposals |= draft or disposals.create(
                {"asset_id": rec.id, "kind": "write_off", "date": fields.Date.context_today(rec)}
            )
        return {"disposal_ids": disposals.ids}

    def _mark_disposed(self, on_date, move=None):
        for rec in self:
            rec._guarded().write({"state": "disposed", "disposal_date": on_date})
            publish(
                self.env,
                "asset.disposed",
                "fix.fixed.asset",
                rec.id,
                {"name": rec.name, "move_id": move.id if move else False},
            )

    @api.model
    def consume_asset_event(self, event):
        """The registered consumer of asset.capitalized, depreciation.accrued
        and asset.disposed (A08 M49-11; BRU-FXA-02 "no register change
        without a ledger consequence"): an event whose journal entry is
        missing or not posted is flagged on the asset for Finance."""
        payload = event.get("payload") or {}
        asset = self.sudo().browse(event.get("aggregate_id") or 0).exists()
        if not asset:
            return False
        move = self.env["account.move"].sudo().browse(payload.get("move_id") or 0).exists()
        if move and move.state == "posted":
            return True
        asset.message_post(
            body=self.env._(
                "Register event %s has no posted journal entry: the register and the GL "
                "disagree (BRU-FXA-02). Reconcile before the period closes.",
                event.get("event_type") or "?",
            )
        )
        return False

    @api.model
    def _fix_register_gl_reconciliation(self, company=None):
        """BRU-FXA-03 (A08 M49-10): the register against its control accounts,
        per category — cost vs the asset account, accumulated depreciation and
        impairment vs the accumulated account, open CWIP vs the CWIP account.
        Returns rows with the variance; a close checklist reads it."""
        company = company or self.env.company
        MoveLine = self.env["account.move.line"].sudo()

        def gl(account):
            if not account:
                return 0.0
            lines = MoveLine.search(
                [
                    ("company_id", "=", company.id),
                    ("account_id", "=", account.id),
                    ("parent_state", "=", "posted"),
                ]
            )
            return money(sum(lines.mapped("balance")))

        rows = []
        categories = self.env["fix.asset.category"].sudo().search([("company_id", "=", company.id)])
        assets = self.sudo().search([("company_id", "=", company.id), ("state", "=", "active")])
        cwips = (
            self.env["fix.cwip.entry"]
            .sudo()
            .search([("company_id", "=", company.id), ("state", "=", "open")])
        )
        seen = set()
        for cat in categories:
            for label, field in (
                ("cost", "asset_account_id"),
                ("accumulated", "accumulated_account_id"),
                ("cwip", "cwip_account_id"),
            ):
                account = cat[field]
                if not account or (account.id, label) in seen:
                    continue
                seen.add((account.id, label))
                # an account shared by several categories is compared once, in total
                sharing = categories.filtered(lambda k, f=field, a=account: k[f] == a)
                mine = assets.filtered(lambda a, ks=sharing: a.category_id in ks)
                if label == "cost":
                    register = sum(mine.mapped("cost"))
                elif label == "accumulated":
                    register = -sum(mine.mapped("accumulated_depreciation")) - sum(
                        mine.mapped("impairment_total")
                    )
                else:
                    register = sum(
                        cwips.filtered(lambda w, ks=sharing: w.category_id in ks).mapped("amount")
                    )
                ledger = gl(account)
                rows.append(
                    {
                        "category": cat.display_name,
                        "line": label,
                        "account": account.display_name,
                        "register": money(register),
                        "gl": ledger,
                        "variance": money(register - ledger),
                    }
                )
        return rows


class FixPeriodCloseRegister(models.Model):
    """BRU-FXA-03 (A08 M49-10): the register reconciles to its control accounts
    before the period closes. The reconciliation was a report nobody had to read."""

    _inherit = "fix.period.close"

    def _fix_check_register_reconciled(self):
        self.ensure_one()
        env = self.env
        if not float_param(env, CLOSE_GATE):
            return True
        tolerance = float_param(env, CLOSE_GATE_TOLERANCE)
        rows = env["fix.fixed.asset"].sudo()._fix_register_gl_reconciliation(self.company_id)
        off = [row for row in rows if abs(row["variance"]) > tolerance]
        if off:
            raise UserError(
                "The fixed-asset register does not agree with the ledger (BRU-FXA-03), so "
                "period %s does not close. Reconcile on Register to GL Reconciliation:\n%s"
                % (
                    self.period_end,
                    "\n".join(
                        "%s, %s (%s): register %.2f, ledger %.2f, variance %.2f"
                        % (
                            row["category"],
                            row["line"],
                            row["account"],
                            row["register"],
                            row["gl"],
                            row["variance"],
                        )
                        for row in off[:10]
                    ),
                )
            )
        return True

    def action_close(self):
        for close in self:
            close._fix_check_register_reconciled()
        return super().action_close()


class FixCwipEntry(models.Model):
    """Capital work in progress: posted costs accumulate, then capitalise."""

    _name = "fix.cwip.entry"
    _description = "CWIP Entry"
    _inherit = ["fix.guarded.mixin", "mail.thread", "mail.activity.mixin"]
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
    cost_line_ids = fields.Many2many(
        "account.move.line",
        "fix_cwip_entry_cost_line_rel",
        "cwip_id",
        "move_line_id",
        string="Booked Costs",
        readonly=True,
        copy=False,
        help="Posted journal items on the CWIP account (M52 capital invoices, receipts) "
        "booked to this project",
    )
    amount = fields.Monetary(
        string="Accumulated Cost",
        currency_field="currency_id",
        compute="_compute_amount",
        store=True,
        tracking=True,
        help="Posted costs booked to the CWIP account for this project (never typed).",
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

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "asset_id",
            "move_id",
            "cost_line_ids",
            "amount",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields() | {"amount"}
        if self and self.state != "open":
            locked |= {n for n, f in self._fields.items() if f.store}
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open():
            done = self.filtered(lambda r: r.state != "open")
            moving = {k for k in vals if not k.startswith(("message_", "activity_"))}
            if done and any(
                r._fix_guard_differs(n, vals[n], r[n])
                for r in done
                for n in moving
                if n in r._fields
            ):
                raise UserError(self.env._("A capitalised CWIP project is closed."))
            if "capex_request_id" in vals:
                booked = self.filtered("cost_line_ids")
                if any(
                    r._fix_guard_differs(
                        "capex_request_id", vals["capex_request_id"], r.capex_request_id
                    )
                    for r in booked
                ):
                    raise UserError(
                        self.env._("Costs are booked to this project: its capex is fixed.")
                    )
        return super().write(vals)

    @api.depends("cost_line_ids.balance", "cost_line_ids.parent_state")
    def _compute_amount(self):
        for rec in self:
            lines = rec.cost_line_ids.filtered(lambda ln: ln.parent_state == "posted")
            rec.amount = money(sum(lines.mapped("balance")))

    def _fix_cwip_account(self):
        """The account a capital invoice debits for this project (M52 hand-off)."""
        self.ensure_one()
        account = self.category_id.cwip_account_id
        if not account:
            raise UserError(
                self.env._(
                    "Configure the CWIP account of category %s first.",
                    self.category_id.display_name or "-",
                )
            )
        return account

    def _fix_book_cost(self, move_lines):
        """CONTRACT (B5 -> B2, A08 M49-3): book POSTED journal items on the
        project's CWIP account (an approved M52 capital invoice's line, a
        goods receipt) to this project. Each item is booked once."""
        self.ensure_one()
        if self.state != "open":
            raise UserError(self.env._("%s is already capitalised.", self.name))
        account = self._fix_cwip_account()
        lines = move_lines.sudo()
        for line in lines:
            if line.parent_state != "posted":
                raise UserError(self.env._("%s is not posted.", line.move_id.display_name))
            if line.account_id != account or line.company_id != self.company_id:
                raise UserError(
                    self.env._("%s is not on the CWIP account of %s.", line.display_name, self.name)
                )
        taken = self.sudo().search(
            [("id", "!=", self.id), ("cost_line_ids", "in", lines.ids)], limit=1
        )
        if taken:
            raise UserError(self.env._("These costs are already booked to %s.", taken.name))
        already = lines.filtered(lambda ln: ln in self.cost_line_ids)
        if already:
            # booked-once applies to the SAME project too (B5 contract): an
            # (4, id) relink of an already-linked line is a silent no-op
            # otherwise, and the double booking went unrefused
            raise UserError(self.env._("These costs are already booked to %s.", self.name))
        self._guarded().write({"cost_line_ids": [(4, ln.id) for ln in lines]})
        return True

    def _unbooked_cwip_entries(self):
        """Posted entries on the project's CWIP account not yet booked to any
        project: what the person can name when booking cost."""
        self.ensure_one()
        lines = (
            self.env["account.move.line"]
            .sudo()
            .search(
                [
                    ("company_id", "=", self.company_id.id),
                    ("account_id", "=", self._fix_cwip_account().id),
                    ("parent_state", "=", "posted"),
                    ("balance", ">", 0),
                ]
            )
        )
        booked = self.sudo().search([("cost_line_ids", "in", lines.ids)]).mapped("cost_line_ids")
        return (lines - booked).mapped("move_id")

    def action_book_posted_cost(self, move_ids=None, entries=None):
        """Book the CWIP-account lines of posted entries to the project: by id
        (the M52 hand-off) or by entry number (`entries`, comma separated, the
        workspace's Book Posted Cost)."""
        require_group(self.env, USER_GROUP, "Booking CWIP cost")
        names = [n.strip() for n in (entries or "").split(",") if n.strip()]
        for rec in self:
            Move = self.env["account.move"].sudo()
            moves = Move.browse(move_ids or [])
            if names:
                moves |= Move.search(
                    [("company_id", "=", rec.company_id.id), ("name", "in", names)]
                )
            account = rec._fix_cwip_account()
            lines = moves.line_ids.filtered(lambda ln, a=account: ln.account_id == a)
            if not lines:
                waiting = rec._unbooked_cwip_entries().mapped("name")
                raise UserError(
                    self.env._(
                        "No posted CWIP cost in the entries given. Posted entries on the CWIP "
                        "account not yet booked to a project: %s",
                        ", ".join(waiting[:20]) or "none",
                    )
                )
            rec._fix_book_cost(lines)
        return True

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

    def _cwip_gl_balance(self, account):
        self.ensure_one()
        lines = (
            self.env["account.move.line"]
            .sudo()
            .search(
                [
                    ("company_id", "=", self.company_id.id),
                    ("account_id", "=", account.id),
                    ("parent_state", "=", "posted"),
                ]
            )
        )
        return money(sum(lines.mapped("balance")))

    def action_capitalise(self, category=None, life_months=None, salvage=None):
        """CWIP -> fixed asset: the booked cost becomes the gross and is
        reclassified in the GL (Dr asset account / Cr CWIP account).

        A08 M49-2/3: only for an APPROVED capex request (DOFA stamp in force),
        for the POSTED cost booked to the project, never above the approved
        capex nor above what the CWIP account holds. The asset is registered
        active to the entry's own company / operating unit; missing posting
        accounts fail closed (nothing is created)."""
        require_group(self.env, USER_GROUP, "Capitalising CWIP")
        assets = self.env["fix.fixed.asset"]
        for rec in self:
            if rec.state != "open":
                raise UserError("CWIP entry already capitalised")
            request = rec.capex_request_id
            if not request:
                raise UserError(
                    self.env._(
                        "%s has no capex request: capitalisation needs an approved capex "
                        "(BRU-FXA-01).",
                        rec.name,
                    )
                )
            request.sudo()._fix_assert_approved("Capitalising %s" % rec.name)
            if rec.amount <= 0:
                raise UserError("Nothing accumulated to capitalise")
            cat = rec._resolve_category(category)
            if not cat:
                raise UserError(self.env._("Choose the asset category of %s first.", rec.name))
            life = life_months or rec.life_months or cat.useful_life_months
            residual = salvage if salvage is not None else rec.salvage
            if money(rec.amount) > money(request.amount):
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
            if set(rec.cost_line_ids.mapped("account_id").ids) - {cat.cwip_account_id.id}:
                raise UserError(
                    self.env._("The costs of %s sit on another CWIP account.", rec.name)
                )
            balance = rec._cwip_gl_balance(cat.cwip_account_id)
            if money(rec.amount) > balance + 0.005:
                raise UserError(
                    self.env._(
                        "%s: capitalising %s would take the CWIP account below zero (it holds %s).",
                        rec.name,
                        rec.amount,
                        balance,
                    )
                )
            # FR-FXA-014/016: one asset, or one per recorded component (each
            # with its own category, life and residual), the cost allocated
            # by the components' approved shares
            parts = rec._capitalisation_parts(cat, life, residual or 0.0)
            for part in parts:
                require_accounts(part["category"], ["asset_account_id"], "CWIP capitalisation")
            today = fields.Date.context_today(rec)
            move = post_entry(
                rec.env,
                rec.company_id,
                cat.journal_id,
                today,
                "CWIP capitalisation: %s" % rec.name,
                [(p["category"].asset_account_id, p["gross"], 0.0, p["name"]) for p in parts]
                + [(cat.cwip_account_id, 0.0, rec.amount, rec.name)],
                rec.operating_unit_id,
            )
            created = self.env["fix.fixed.asset"]
            for part in parts:
                created |= (
                    self.env["fix.fixed.asset"]
                    ._guarded()
                    .create(
                        dict(
                            {
                                "company_id": rec.company_id.id,
                                "operating_unit_id": rec.operating_unit_id.id,
                                "name": part["name"],
                                "category_id": part["category"].id,
                                "gross": part["gross"],
                                "salvage": part["salvage"],
                                "life_months": part["life"],
                                "purchase_date": today,
                                "capex_request_id": request.id,
                                "cwip_id": rec.id,
                            },
                            **part.get("asset_vals", {}),
                        )
                    )
                )
            rec._guarded().write(
                {"state": "capitalised", "asset_id": created[:1].id, "move_id": move.id}
            )
            if request.state in ("approved", "cwip"):
                request.sudo()._guarded().write({"state": "capitalised"})
            for asset in created:
                asset._fix_activate_from_source(move)
            rec._after_capitalise(created)
            assets |= created.with_env(self.env)
        return assets

    def _capitalisation_parts(self, category, life, residual):
        """What the project capitalises into: one asset carrying the whole
        cost. cd_fixed_asset_ext's components (fix_asset_capture) split it."""
        self.ensure_one()
        return [
            {
                "name": self.name,
                "category": category,
                "gross": self.amount,
                "salvage": residual,
                "life": life,
            }
        ]

    def _after_capitalise(self, assets):
        """Hook: the assets the project was capitalised into."""
        return None
