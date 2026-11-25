# cd_tax_engine_bd — M51 intake of the salary TDS withheld by payroll (ITA 2023
# s.86), from payroll.posted and payroll.bonus_posted (A09 workflow audit
# M56-17: payroll's events had no consumer in finance).
#
# Why a record type of its own: fix.withholding.line is a deduction at ONE
# statutory rate (rate_id is required and the amount must equal base x rate x
# the default multiplier). Salary tax is computed on the slabs per employee by
# payroll, so no fixed rate row exists for it and none is invented here.
# fix.salary.tds holds what payroll actually withheld: one row per payroll
# run and operating unit, on the payroll TDS payable account payroll credited.
#
# It feeds the existing flow:
#   * a TDS challan with tds_head = "salary" links the period's rows and, on
#     the deposit, posts Dr payroll TDS payable / Cr bank (the account the
#     payroll accrual credited, never the vendor TDS role account);
#   * the quarterly TDS return lists the quarter's rows under s.86.
# Existing challans and returns (tds_head = "general") behave as before.
from __future__ import annotations

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

from .fix_tax_compliance import _journal_account, money, post_tax_move, quarter_bounds
from .fix_tax_master import period_of


class FixSalaryTds(models.Model):
    """Income tax withheld from salaries (ITA 2023 s.86) by one payroll run in
    one operating unit, as payroll posted it."""

    _name = "fix.salary.tds"
    _description = "Salary TDS Withheld (ITA 2023 s.86)"
    _inherit = ["mail.thread"]
    _order = "document_date desc, id desc"
    _source_unique = models.Constraint(
        "UNIQUE (source_model, source_id, ou_key)",
        "A payroll run's salary TDS is taken in once per operating unit",
    )

    company_id = fields.Many2one("res.company", required=True, index=True, readonly=True)
    operating_unit_id = fields.Many2one("operating.unit", index=True, readonly=True)
    ou_key = fields.Integer(
        required=True, readonly=True, help="operating_unit_id or 0: the idempotency key"
    )
    source_model = fields.Char(required=True, readonly=True, index=True)
    source_id = fields.Integer(required=True, readonly=True, index=True)
    source_ref = fields.Char(string="Payroll Run", readonly=True)
    section = fields.Char(default="s.86", readonly=True)
    document_date = fields.Date(string="Period End", required=True, readonly=True, index=True)
    period = fields.Char(compute="_compute_period", store=True, index=True)
    currency_id = fields.Many2one("res.currency", required=True, readonly=True)
    gross = fields.Monetary(string="Gross Salaries", currency_field="currency_id", readonly=True)
    amount = fields.Monetary(
        string="Tax Withheld", currency_field="currency_id", required=True, readonly=True
    )
    move_id = fields.Many2one(
        "account.move", string="Payroll Entry", readonly=True, ondelete="restrict"
    )
    liability_account_id = fields.Many2one(
        "account.account",
        string="TDS Payable Account",
        readonly=True,
        help="The account the payroll entry credited with this tax; the challan clears it.",
    )
    state = fields.Selection(
        [("withheld", "Withheld"), ("deposited", "Deposited"), ("cancelled", "Cancelled")],
        default="withheld",
        required=True,
        readonly=True,
        tracking=True,
    )
    challan_id = fields.Many2one(
        "fix.tax.challan", string="Challan", index=True, ondelete="restrict", readonly=True
    )
    challan_no = fields.Char(related="challan_id.challan_no", string="Challan No")
    challan_date = fields.Date(related="challan_id.challan_date", string="Challan Date")

    @api.depends("document_date")
    def _compute_period(self):
        for row in self:
            row.period = period_of(row.document_date)

    @api.constrains("amount", "gross")
    def _check_amount(self):
        for row in self:
            if row.amount <= 0:
                raise ValidationError("A salary TDS row holds tax actually withheld (> 0).")
            if row.gross and row.amount > row.gross + 0.005:
                raise ValidationError("Salary TDS cannot exceed the gross salaries it came from.")

    @api.model
    def consume_payroll_posted(self, event):
        """payroll.posted {company_id, move_id, period_end, tax,
        by_operating_unit: [{operating_unit_id, branch_id, gross, tax, net}]}
        -> one row per operating unit with tax withheld (idempotent)."""
        payload = event.get("payload") or {}
        return self._intake(
            "payroll.posted",
            event.get("aggregate") or "fix.payroll.period",
            event.get("aggregate_id"),
            payload,
            payload.get("tax"),
            payload.get("period") or False,
        )

    @api.model
    def consume_payroll_bonus_posted(self, event):
        """payroll.bonus_posted {company_id, bonus_run_id, move_id, period_end,
        tax_total, by_operating_unit: [{operating_unit_id, gross, tax}]} -> one
        row per operating unit with bonus tax withheld, sourced on the bonus
        run (idempotent). Same checks as payroll.posted."""
        payload = event.get("payload") or {}
        run_id = payload.get("bonus_run_id")
        if not run_id:
            raise UserError("payroll.bonus_posted names no bonus run.")
        ref = "Bonus run %s" % run_id
        if "fix.payroll.bonus.run" in self.env:
            run = self.env["fix.payroll.bonus.run"].sudo().browse(int(run_id)).exists()
            ref = "Bonus %s" % (run.name or run_id) if run else ref
        return self._intake(
            "payroll.bonus_posted",
            "fix.payroll.bonus.run",
            int(run_id),
            payload,
            payload.get("tax_total"),
            ref,
        )

    def _intake(self, what, source_model, source_id, payload, run_tax, source_ref):
        """Check the event against the posted payroll entry, then create one row
        per operating unit with tax (idempotent on source and unit)."""
        company = self.env["res.company"].browse(payload.get("company_id")).exists()
        if not company:
            raise UserError("%s %s names no company." % (what, source_id))
        move = self.env["account.move"].sudo().browse(payload.get("move_id") or 0).exists()
        if not move or move.state != "posted" or move.company_id != company:
            raise UserError("%s %s: its journal entry is not posted." % (what, source_id))
        currency = company.currency_id
        by_ou = {}
        for row in payload.get("by_operating_unit") or []:
            key = int(row.get("operating_unit_id") or 0)
            agg = by_ou.setdefault(key, [0.0, 0.0])
            agg[0] += float(row.get("gross") or 0.0)
            agg[1] += float(row.get("tax") or 0.0)
        total = currency.round(sum(t for _g, t in by_ou.values()))
        if currency.compare_amounts(total, float(run_tax or 0.0)):
            raise UserError(
                "%s %s: the units' tax (%.2f) differs from the run's (%.2f)."
                % (what, source_id, total, float(run_tax or 0.0))
            )
        liability = (
            company.sudo().payroll_tax_payable_account_id
            if "payroll_tax_payable_account_id" in company._fields
            else self.env["account.account"]
        )
        if not currency.is_zero(total):
            booked = currency.round(
                sum(move.line_ids.filtered(lambda ln: ln.account_id == liability).mapped("credit"))
            )
            if not liability or currency.compare_amounts(booked, total):
                raise UserError(
                    "%s %s: the entry credits %.2f to the TDS payable account, not "
                    "the %.2f withheld - nothing taken in." % (what, source_id, booked, total)
                )
        made = self.browse()
        for key, (gross, tax) in sorted(by_ou.items()):
            if currency.is_zero(tax):
                continue  # no tax withheld in this unit: nothing to deposit
            existing = self.search(
                [
                    ("source_model", "=", source_model),
                    ("source_id", "=", source_id),
                    ("ou_key", "=", key),
                ],
                limit=1,
            )
            if existing:
                made |= existing
                continue
            made |= self.create(
                {
                    "company_id": company.id,
                    "operating_unit_id": key or False,
                    "ou_key": key,
                    "source_model": source_model,
                    "source_id": source_id,
                    "source_ref": source_ref,
                    "document_date": fields.Date.to_date(payload.get("period_end")),
                    "currency_id": currency.id,
                    "gross": currency.round(gross),
                    "amount": currency.round(tax),
                    "move_id": move.id,
                    "liability_account_id": liability.id,
                }
            )
        return made


class FixTaxChallanSalary(models.Model):
    """A TDS challan depositing salary TDS (tds_head = salary)."""

    _inherit = "fix.tax.challan"

    tds_head = fields.Selection(
        [("general", "Withholding on payments"), ("salary", "Salary (ITA 2023 s.86)")],
        string="TDS Head",
        default="general",
        help="Salary TDS is deposited on its own challan and clears the payroll TDS payable "
        "account; every other deduction stays on a general challan.",
    )
    salary_tds_ids = fields.One2many("fix.salary.tds", "challan_id", string="Salary TDS Settled")

    @api.depends(
        "tax_kind",
        "tds_head",
        "withholding_line_ids.amount",
        "vat_return_id.net_payable",
        "salary_tds_ids.amount",
    )
    def _compute_liability(self):
        super()._compute_liability()
        for ch in self:
            if ch.tax_kind == "tds" and ch.tds_head == "salary":
                ch.liability_total = sum(ch.salary_tds_ids.mapped("amount"))

    @api.constrains("tds_head", "tax_kind", "withholding_line_ids")
    def _check_salary_head(self):
        for ch in self:
            if ch.tds_head == "salary" and (ch.tax_kind != "tds" or ch.withholding_line_ids):
                raise ValidationError(
                    "A salary TDS challan is a TDS challan settling salary TDS only."
                )

    def action_link_open_deductions(self):
        salary = self.filtered(lambda ch: ch.tds_head == "salary")
        salary.check_access("write")
        for ch in salary:
            if ch.state != "draft" or ch.tax_kind != "tds":
                raise UserError("Only a draft salary TDS challan links salary TDS")
            if not ch.period:
                raise UserError("Set the period (YYYY-MM) the challan settles first")
            rows = (
                self.env["fix.salary.tds"]
                .sudo()
                .search(
                    [
                        ("company_id", "=", ch.company_id.id),
                        ("period", "=", ch.period),
                        ("state", "=", "withheld"),
                        ("challan_id", "=", False),
                    ]
                )
            )
            if not rows:
                raise UserError("No undeposited salary TDS in %s" % ch.period)
            rows.write({"challan_id": ch.id})
        rest = self - salary
        if rest:
            return super(FixTaxChallanSalary, rest).action_link_open_deductions()
        return True

    def action_confirm_deposit(self):
        salary = self.filtered(lambda ch: ch.tds_head == "salary")
        salary.check_access("write")
        for ch in salary:
            if ch.state != "draft":
                raise UserError("Challan %s is already %s" % (ch.challan_no, ch.state))
            company = ch.company_id
            rows = ch.sudo().salary_tds_ids
            if ch.withholding_line_ids or ch.tax_kind != "tds":
                raise UserError("A salary TDS challan settles salary TDS only")
            if not rows:
                raise UserError("Link the salary TDS this challan settles first")
            if rows.filtered(lambda r, comp=company: r.state != "withheld" or r.company_id != comp):
                raise UserError(
                    "Only withheld, undeposited salary TDS of %s can be settled" % company.name
                )
            if abs(money(ch.amount) - money(ch.liability_total)) > 0.005:
                raise UserError(
                    "Challan amount %.2f does not equal the salary TDS it settles (%.2f)"
                    % (ch.amount, ch.liability_total)
                )
            liability = rows.mapped("liability_account_id")
            if len(liability) != 1 or rows.filtered(lambda r: not r.liability_account_id):
                raise UserError(
                    "The salary TDS rows of challan %s do not name one payroll TDS payable "
                    "account. Nothing was posted." % ch.challan_no
                )
            journal = _journal_account(self.env, company, "cd_tax_engine_bd.challan_journal_code")
            label = "Salary TDS challan %s" % ch.challan_no
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
            rows.write({"state": "deposited"})
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
        rest = self - salary
        if rest:
            return super(FixTaxChallanSalary, rest).action_confirm_deposit()
        return True


class FixTdsReturnSalary(models.Model):
    """The quarterly TDS return also lists the quarter's salary TDS (s.86)."""

    _inherit = "fix.tds.return"

    def action_prepare(self):
        res = super().action_prepare()
        # in-process prepare token: the A08 M51-1 line gate allows builds
        # only from Prepare (this extension IS Prepare's salary leg)
        Line = self.env["fix.tds.return.line"].with_context(fix_tds_return_prepare=True)
        for ret in self:
            start, end = quarter_bounds(ret.quarter)
            rows = (
                self.env["fix.salary.tds"]
                .sudo()
                .search(
                    [
                        ("company_id", "=", ret.company_id.id),
                        ("document_date", ">=", start),
                        ("document_date", "<=", end),
                        ("state", "!=", "cancelled"),
                    ],
                    order="document_date, id",
                )
            )
            if not rows:
                continue
            Line.create(
                [
                    {
                        "tds_return_id": ret.id,
                        "company_id": ret.company_id.id,
                        "operating_unit_id": row.operating_unit_id.id,
                        "salary_tds_id": row.id,
                        "vendor_name": "Salaried employees %s - %s"
                        % (row.source_ref or "", row.operating_unit_id.name or ret.company_id.name),
                        "section_code": "86",
                        "base_amount": row.gross,
                        "rate_percent": round(row.amount * 100.0 / row.gross, 3)
                        if row.gross
                        else 0.0,
                        "tds_amount": row.amount,
                        "challan_no": row.challan_id.challan_no or False,
                        "challan_date": row.challan_id.challan_date or False,
                    }
                    for row in rows
                ]
            )
            ret._guarded().write(
                {"total_withheld": money(ret.total_withheld + sum(rows.mapped("amount")))}
            )
        return res


class FixTdsReturnLineSalary(models.Model):
    _inherit = "fix.tds.return.line"

    salary_tds_id = fields.Many2one("fix.salary.tds", string="Salary TDS", ondelete="set null")
    section_code = fields.Selection(
        selection_add=[("86", "ITA 2023 s.86 - Salary")],
        ondelete={"86": "set default"},
    )
