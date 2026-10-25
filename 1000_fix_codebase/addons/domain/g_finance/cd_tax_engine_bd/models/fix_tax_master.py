# cd_tax_engine_bd — A08 M51 statutory master data (CD-M51-01).
#
# Every Bangladesh rate, threshold and due day the finance screens use is
# EFFECTIVE-DATED master data here (A08 spec rule 3), never a constant in
# code: the company's VAT/tax adviser corrects a row without a release.
# Rows that could not be confirmed against a primary NBR text are seeded
# with verify_with_adviser=True and say so on every screen that shows them.
from datetime import date, timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from . import return_logic

TAX_KINDS = [("vat", "VAT"), ("tds", "TDS (income tax at source)"), ("vds", "VDS (VAT at source)")]
PAYEE_TYPES = [("any", "Any payee"), ("company", "Company"), ("individual", "Individual")]

PARAMETER_KEYS = [
    ("non_filer_multiplier", "Non-filer withholding multiplier (no proof of return)"),
    ("mushak610_threshold", "Mushak 6.10 high-value invoice threshold (BDT)"),
    ("input_credit_window_periods", "Input VAT claim window (tax periods after the invoice)"),
    ("rtgs_min_amount", "BD-RTGS minimum transfer (BDT)"),
]

OBLIGATIONS = [
    ("vat_91_return", "Mushak 9.1 monthly VAT return and payment"),
    ("tds_deposit", "TDS deposit (income tax withheld)"),
    ("vds_deposit", "VDS deposit (VAT withheld)"),
    ("wht_return", "Quarterly withholding tax return"),
    ("company_itr", "Company income tax return (annual)"),
]
FREQUENCIES = [("monthly", "Monthly"), ("quarterly", "Quarterly"), ("annual", "Annual")]

# Account roles shared by the AP sub-ledger (cd_ap_ext) and the challans:
# role -> (system parameter, default code or None). A role without a code
# FAILS CLOSED — a tax liability never lands on a guessed account.
TAX_ACCOUNT_ROLES = {
    "vat_output": ("cd_tax_engine_bd.vat_output_account_code", "210100"),
    "vat_input": ("cd_tax_engine_bd.vat_input_account_code", "110500"),
    # chart loader: 252000 "Tax Payable" -> 2-30-30-010 TDS payable
    "tds_payable": ("cd_tax_engine_bd.account_code.tds_payable", "252000"),
    "vds_payable": ("cd_tax_engine_bd.account_code.vds_payable", None),
}


def tax_account(env, company, role):
    """The company's GL account for a tax role — refused when unconfigured."""
    param, default = TAX_ACCOUNT_ROLES[role]
    code = env["ir.config_parameter"].sudo().get_param(param) or default
    account = env["account.account"]
    if code:
        account = (
            env["account.account"]
            .with_company(company)
            .search([("code", "=", code), ("company_ids", "in", company.id)], limit=1)
        )
    if not account:
        raise UserError(
            "No GL account for the %s role in %s: set system parameter %s to an "
            "account code of this company's chart. Nothing was posted."
            % (role, company.name, param)
        )
    return account


def period_of(day):
    """The YYYY-MM VAT/withholding period of a date."""
    return day.strftime("%Y-%m") if day else False


def add_months(year, month, n):
    """(year, month) shifted by n months."""
    idx = year * 12 + (month - 1) + n
    return idx // 12, idx % 12 + 1


class FixJournalPostingLogTax(models.Model):
    """The tax sub-ledger (challans) as a posting source in M19's posting log."""

    _inherit = "fix.journal.posting.log"

    source = fields.Selection(
        selection_add=[("tax_subledger", "Tax Sub-ledger (M51)")],
        ondelete={"tax_subledger": lambda recs: recs.write({"source": "api"})},
    )


class _EffectiveDated(models.AbstractModel):
    """Shared validity window + the adviser flag of every statutory row."""

    _name = "fix.tax.effective.mixin"
    _description = "Effective-dated statutory master row"

    date_from = fields.Date(string="Valid From", required=True, default=fields.Date.today)
    date_to = fields.Date(string="Valid To", help="Empty = open-ended")
    verify_with_adviser = fields.Boolean(
        string="Verify with Adviser",
        default=True,
        help="Seeded from secondary sources: the company's VAT/tax adviser must "
        "confirm (or correct) this row before it is relied on.",
    )
    source_note = fields.Text(string="Source / Note")

    @api.constrains("date_from", "date_to")
    def _check_window(self):
        for row in self:
            if row.date_to and row.date_to < row.date_from:
                raise ValidationError("Valid To cannot be before Valid From")

    def _overlaps(self, domain):
        """True when another row of the same key overlaps this one's window."""
        self.ensure_one()
        far = date(9999, 12, 31)
        for other in self.search([*domain, ("id", "!=", self.id)]):
            if self.date_from <= (other.date_to or far) and other.date_from <= (
                self.date_to or far
            ):
                return True
        return False

    @api.model
    def _company_first(self, domain, company, limit=1):
        """Rows for the company, else the statutory defaults (no company)."""
        Model = self.sudo()
        rows = Model.search([*domain, ("company_id", "=", company.id)], limit=limit)
        return rows or Model.search([*domain, ("company_id", "=", False)], limit=limit)

    @api.model
    def _window_domain(self, on_date):
        return [
            ("date_from", "<=", on_date),
            "|",
            ("date_to", "=", False),
            ("date_to", ">=", on_date),
        ]


class FixTaxRate(models.Model):
    """Tax Rate Master: VAT, TDS (ITA 2023 sections) and VDS (service codes)."""

    _name = "fix.tax.rate"
    _description = "Tax Rate Master"
    _inherit = ["fix.tax.effective.mixin", "mail.thread", "mail.activity.mixin"]
    _order = "tax_kind, code, payee_type, date_from desc"

    company_id = fields.Many2one(
        "res.company",
        index=True,
        default=lambda self: self.env.company,
        help="Empty = the statutory default for every company; a company row overrides it",
    )
    operating_unit_id = fields.Many2one(
        "operating.unit", help="Statutory rates are company-wide: leave empty"
    )
    tax_kind = fields.Selection(TAX_KINDS, required=True, index=True, tracking=True)
    code = fields.Char(
        required=True,
        index=True,
        help="TDS category key (e.g. service_general) or the VAT service code (e.g. S074.00)",
    )
    name = fields.Char(string="Description", required=True)
    section = fields.Char(
        string="Statutory Section",
        help="ITA 2023 section for TDS, VAT Act / service code reference for VAT and VDS",
    )
    payee_type = fields.Selection(PAYEE_TYPES, required=True, default="any")
    rate = fields.Float(string="Rate (%)", required=True, digits=(6, 3), tracking=True)
    non_filer_applies = fields.Boolean(
        string="Non-filer Multiplier Applies",
        default=True,
        help="A payee without proof of return submission suffers this rate times "
        "the non-filer multiplier (statutory parameter)",
    )
    active = fields.Boolean(default=True)

    @api.constrains("rate", "tax_kind", "code", "payee_type", "date_from", "date_to", "company_id")
    def _check_rate(self):
        for row in self:
            if not 0 <= row.rate <= 100:
                raise ValidationError("A rate is a percentage between 0 and 100")
            if row._overlaps(
                [
                    ("company_id", "=", row.company_id.id),
                    ("tax_kind", "=", row.tax_kind),
                    ("code", "=", row.code),
                    ("payee_type", "=", row.payee_type),
                ]
            ):
                raise ValidationError(
                    "Another %s rate for %s (%s) is valid in an overlapping window — "
                    "close the old row (Valid To) first" % (row.tax_kind, row.code, row.payee_type)
                )

    @api.depends("tax_kind", "code", "rate")
    def _compute_display_name(self):
        for row in self:
            row.display_name = "%s %s — %s (%g%%)" % (
                (row.tax_kind or "").upper(),
                row.code or "",
                row.section or row.name or "",
                row.rate,
            )

    @api.model
    def find_rate(self, tax_kind, code, on_date, company=None, payee_type="any"):
        """The effective rate row, or a UserError naming what to maintain.
        A payee-type row wins over the 'any' row."""
        company = company or self.env.company
        on_date = on_date or fields.Date.context_today(self)
        base = [("tax_kind", "=", tax_kind), ("code", "=", code), *self._window_domain(on_date)]
        for ptype in dict.fromkeys([payee_type or "any", "any"]):
            row = self._company_first([*base, ("payee_type", "=", ptype)], company)
            if row:
                return self.browse(row.id)
        raise UserError(
            "No effective %s rate for %r on %s in %s — maintain it in the Tax Rate Master "
            "(never guessed on statutory money)." % (tax_kind.upper(), code, on_date, company.name)
        )


class FixTaxParameter(models.Model):
    """Statutory scalar parameters (thresholds, multipliers, windows)."""

    _name = "fix.tax.parameter"
    _description = "Statutory Parameter"
    _inherit = ["fix.tax.effective.mixin", "mail.thread", "mail.activity.mixin"]
    _order = "key, date_from desc"

    company_id = fields.Many2one(
        "res.company",
        index=True,
        default=lambda self: self.env.company,
        help="Empty = the statutory default for every company; a company row overrides it",
    )
    operating_unit_id = fields.Many2one(
        "operating.unit", help="Statutory parameters are company-wide: leave empty"
    )
    key = fields.Selection(PARAMETER_KEYS, required=True, index=True)
    value = fields.Float(required=True, digits=(16, 3), tracking=True)

    @api.depends("key", "value")
    def _compute_display_name(self):
        labels = dict(PARAMETER_KEYS)
        for row in self:
            row.display_name = "%s = %g" % (labels.get(row.key, row.key or ""), row.value)

    @api.constrains("key", "value", "date_from", "date_to", "company_id")
    def _check_parameter(self):
        for row in self:
            if row.value < 0:
                raise ValidationError("A statutory parameter cannot be negative")
            if row._overlaps([("company_id", "=", row.company_id.id), ("key", "=", row.key)]):
                raise ValidationError(
                    "Parameter %s already has a row valid in an overlapping window" % row.key
                )

    @api.model
    def get_value(self, key, on_date=None, company=None):
        company = company or self.env.company
        on_date = on_date or fields.Date.context_today(self)
        row = self._company_first([("key", "=", key), *self._window_domain(on_date)], company)
        if not row:
            raise UserError(
                "Statutory parameter %r has no row valid on %s for %s — maintain it "
                "under Tax Rate Master > Statutory Parameters." % (key, on_date, company.name)
            )
        return row.value


class FixStatutoryDueRule(models.Model):
    """Due-day master of the statutory calendar."""

    _name = "fix.statutory.due.rule"
    _description = "Statutory Due-Date Rule"
    _inherit = ["fix.tax.effective.mixin", "mail.thread", "mail.activity.mixin"]
    _order = "obligation, date_from desc"

    company_id = fields.Many2one(
        "res.company",
        index=True,
        default=lambda self: self.env.company,
        help="Empty = the statutory default for every company; a company row overrides it",
    )
    operating_unit_id = fields.Many2one("operating.unit", help="Company-wide: leave empty")
    obligation = fields.Selection(OBLIGATIONS, required=True, index=True)
    name = fields.Char(required=True)
    authority = fields.Char(
        default="NBR",
        help="Collecting authority — configurable (the 2025 NBR split is still being implemented)",
    )
    frequency = fields.Selection(FREQUENCIES, required=True)
    due_day = fields.Integer(string="Due Day of Month", required=True)
    month_offset = fields.Integer(
        string="Months After Period End",
        required=True,
        default=1,
        help="1 = the month after the period (monthly/quarterly); for annual rules the "
        "months after the fiscal year end (30 June)",
    )
    roll_to_working_day = fields.Boolean(
        string="Roll to Next Working Day",
        default=True,
        help="A due date on a Friday/Saturday or fixed public holiday moves forward",
    )
    active = fields.Boolean(default=True)

    @api.constrains("due_day", "month_offset", "obligation", "date_from", "date_to", "company_id")
    def _check_rule(self):
        for rule in self:
            if not 1 <= rule.due_day <= 31:
                raise ValidationError("The due day is a day of the month (1-31)")
            if rule.month_offset < 0:
                raise ValidationError("Months after period end cannot be negative")
            if rule._overlaps(
                [("company_id", "=", rule.company_id.id), ("obligation", "=", rule.obligation)]
            ):
                raise ValidationError(
                    "Obligation %s already has a rule valid in an overlapping window"
                    % rule.obligation
                )

    # ------------------------------------------------------------ periods --
    @staticmethod
    def _period_ends(frequency, date_from, date_to, lookback_months):
        """Every period END (a date) from lookback_months before date_from up to
        date_to: month ends, quarter ends (Sep/Dec/Mar/Jun) or 30 June."""
        y, m = add_months(date_from.year, date_from.month, -lookback_months)
        ends = []
        while date(y, m, 1) <= date_to:
            ny, nm = add_months(y, m, 1)
            end = date(ny, nm, 1) - timedelta(days=1)
            if (
                frequency == "monthly"
                or (frequency == "quarterly" and m in (3, 6, 9, 12))
                or (frequency == "annual" and m == 6)
            ):
                ends.append(end)
            y, m = ny, nm
        return ends

    def _due_for_period_end(self, period_end):
        self.ensure_one()
        y, m = add_months(period_end.year, period_end.month, self.month_offset)
        ny, nm = add_months(y, m, 1)
        last_day = (date(ny, nm, 1) - timedelta(days=1)).day
        due = date(y, m, min(self.due_day, last_day))
        if self.roll_to_working_day:
            due = return_logic.next_working_day(due, set())
        return due

    @staticmethod
    def period_key(frequency, period_end):
        """The register key of a period: YYYY-MM, the TDS-return quarter label
        (FY-start year, e.g. 2026-Q1 = Jul-Sep 2026) or FY2027."""
        if frequency == "monthly":
            return period_end.strftime("%Y-%m")
        quarter, fiscal_year = return_logic.tds_quarter_for_date(period_end)
        return quarter if frequency == "quarterly" else fiscal_year

    @api.model
    def due_date_for(self, obligation, period_end, company=None):
        """The master-data due date of an obligation for the period ending
        period_end, or None when no rule is maintained."""
        company = company or self.env.company
        rule = self._company_first(
            [("obligation", "=", obligation), *self._window_domain(period_end)], company
        )
        return rule._due_for_period_end(period_end) if rule else None

    @api.model
    def calendar(self, date_from, date_to, company=None):
        """The statutory calendar: one row per obligation whose computed due
        date falls in [date_from, date_to], with its status from the ERP's own
        records (returns, withholding deposits) or recorded filing evidence."""
        company = company or self.env.company
        today = fields.Date.context_today(self)
        rows = []
        own = self.sudo().search([("company_id", "=", company.id)])
        defaults = self.sudo().search(
            [("company_id", "=", False), ("obligation", "not in", own.mapped("obligation"))]
        )
        for rule in own | defaults:
            lookback = (rule.month_offset or 0) + 13
            for end in self._period_ends(rule.frequency, date_from, date_to, lookback):
                if not (rule.date_from <= end and (not rule.date_to or end <= rule.date_to)):
                    continue
                due = rule._due_for_period_end(end)
                if not date_from <= due <= date_to:
                    continue
                key = self.period_key(rule.frequency, end)
                status, detail = rule._status(key, company)
                if status not in ("done", "nothing_due"):
                    status = "overdue" if due < today else "due"
                rows.append(
                    {
                        "rule": rule,
                        "period": key,
                        "period_end": end,
                        "due_date": due,
                        "status": status,
                        "detail": detail,
                    }
                )
        rows.sort(key=lambda r: (r["due_date"], r["rule"].obligation))
        return rows

    def _status(self, key, company):
        """(status, detail) for one period: done / nothing_due / open."""
        self.ensure_one()
        env = self.env
        evidence = env["fix.statutory.filing"].search(
            [("rule_id", "=", self.id), ("period_key", "=", key), ("company_id", "=", company.id)],
            limit=1,
        )
        if evidence:
            return "done", "Filed %s, ref %s" % (evidence.filed_on, evidence.reference)
        if self.obligation == "vat_91_return":
            ret = env["fix.vat.return"].search(
                [("company_id", "=", company.id), ("period", "=", key)], limit=1
            )
            if ret.state == "filed":
                return "done", "Filed, NBR ref %s" % (ret.nbr_confirmation or "-")
            return "open", ("Return %s" % ret.state) if ret else "No return prepared"
        if self.obligation == "wht_return":
            ret = env["fix.tds.return"].search(
                [("company_id", "=", company.id), ("quarter", "=", key)], limit=1
            )
            if ret.state == "filed":
                return "done", "Filed, NBR ack %s" % (ret.nbr_acknowledgment or "-")
            return "open", ("Return %s" % ret.state) if ret else "No return prepared"
        if self.obligation in ("tds_deposit", "vds_deposit"):
            kind = "tds" if self.obligation == "tds_deposit" else "vds"
            lines = env["fix.withholding.line"].search(
                [
                    ("company_id", "=", company.id),
                    ("tax_kind", "=", kind),
                    ("period", "=", key),
                    ("state", "!=", "cancelled"),
                ]
            )
            if not lines:
                return "nothing_due", "Nothing withheld in the period"
            open_lines = lines.filtered(lambda line: line.state == "withheld")
            if not open_lines:
                return "done", "All %d deduction(s) deposited by challan" % len(lines)
            return "open", "BDT %s withheld, not yet deposited (%d line(s))" % (
                "{:,.2f}".format(sum(open_lines.mapped("amount"))),
                len(open_lines),
            )
        return "open", "Record the filing evidence when done"


class FixStatutoryFiling(models.Model):
    """Evidence that a statutory obligation was met (any calendar rule)."""

    _name = "fix.statutory.filing"
    _description = "Statutory Filing Evidence"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "filed_on desc, id desc"
    _rule_period_unique = models.Constraint(
        "UNIQUE (company_id, rule_id, period_key)",
        "Evidence for this obligation and period already exists",
    )

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit")
    rule_id = fields.Many2one(
        "fix.statutory.due.rule", string="Obligation", required=True, ondelete="restrict"
    )
    period_key = fields.Char(
        string="Period",
        required=True,
        help="YYYY-MM (monthly), 2026-Q1 (quarter, FY-start year) or FY2027 (annual)",
    )
    filed_on = fields.Date(required=True, default=fields.Date.context_today)
    reference = fields.Char(string="Acknowledgement / Reference", required=True)
    note = fields.Text()
    attachment_ids = fields.Many2many("ir.attachment", string="Evidence Files")
