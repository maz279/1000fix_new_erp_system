# fix.localisation — Entity Localisation & Nil-Return Automation (CD-M65-01 / CD-M65-02).
#
# A12 audit (2026-11-04) M65:
#   * get_vat_return_due_date crashed (ValueError) when the statutory day was
#     29/30/31 and the following month was shorter: the due date is now
#     CLAMPED to the month's last day, the way NBR treats a month-end statutory
#     day. vat_statutory_day is constrained to 0..31 (0 = unset -> the 15th).
#   * fix.nil.return.generator carried its guards only in the actions: state,
#     the measured transaction count and the statutory payloads were writable
#     directly. They are now guarded (fix.guarded.mixin) and only the actions
#     may set them.
#
# A12 finish E6/E9: a draft or retired pack's holiday moved the statutory VAT date,
# because the consumer ignored the pack lifecycle. It now reads active, loaded
# packs only. BIN and TIN have a format check and, with the VAT day and calendar
# rule, are tracked and audited; the two that move a statutory date also need a
# finance manager. A format check says nothing about whether a number is REAL.
import calendar
import json
import re
from datetime import date, timedelta

from odoo import api, fields, models
from odoo.addons.cd_entity_config.models.fix_entity import audit_event
from odoo.exceptions import UserError, ValidationError

FINANCE_MANAGER_GROUP = "account.group_account_manager"
STATUTORY_DATE_FIELDS = {"vat_statutory_day", "statutory_calendar_rule"}
STATUTORY_FIELDS = STATUTORY_DATE_FIELDS | {"bin_number", "tin_number", "incorporation_date"}


class FixEntityLocalisation(models.Model):
    """Extension to fix.entity providing Bangladesh tax localisation, statutory calendars, and address rules."""

    _inherit = "fix.entity"

    bin_number = fields.Char(
        string="Business Identification No (BIN / VAT)",
        size=16,
        tracking=True,
        help="13-digit statutory VAT registration number under VAT & SD Act 2012",
    )
    tin_number = fields.Char(
        string="Taxpayer Identification No (TIN)",
        size=16,
        tracking=True,
        help="12-digit e-TIN under Income Tax Act 2023",
    )
    vat_statutory_day = fields.Integer(
        string="VAT Due Day of Month",
        default=15,
        tracking=True,
        help="Statutory submission day (default 15th per Mushak rules); a day "
        "beyond the month's length clamps to the month's last day",
    )

    _vat_day_range = models.Constraint(
        "CHECK (vat_statutory_day IS NULL OR vat_statutory_day BETWEEN 0 AND 31)",
        "The VAT statutory day must be a day of the longest month (0 = unset, the 15th applies)",
    )

    @api.constrains("vat_statutory_day")
    def _check_vat_statutory_day(self):
        # Python-level first so the refusal is a form error, never a raw
        # database CHECK violation on the wire.
        for rec in self:
            if rec.vat_statutory_day and not 1 <= rec.vat_statutory_day <= 31:
                raise ValidationError(
                    "The VAT statutory day must be a real day of the longest "
                    "month (1-31; 0 or empty falls back to the statutory 15th)."
                )

    statutory_calendar_rule = fields.Selection(
        [
            ("mushak_next_working_day", "Mushak 15th or Next Working Day (BD Weekend Rollover)"),
            ("strict_calendar_day", "Strict Calendar Day (No Rollover)"),
        ],
        string="Tax Calendar Rule",
        default="mushak_next_working_day",
        required=True,
        tracking=True,
    )

    @api.constrains("bin_number", "tin_number")
    def _check_registration_format(self):
        for rec in self:
            if rec.bin_number and not re.fullmatch(r"\d{13}", rec.bin_number):
                raise ValidationError("A BIN is 13 digits (VAT & SD Act 2012).")
            if rec.tin_number and not re.fullmatch(r"\d{12}", rec.tin_number):
                raise ValidationError("An e-TIN is 12 digits (Income Tax Act 2023).")

    def write(self, vals):
        touched = STATUTORY_FIELDS & set(vals)
        before = {rec.id: {n: rec[n] for n in touched} for rec in self} if touched else {}
        date_moved = (
            STATUTORY_DATE_FIELDS & touched
            and not self.env.su
            and any(rec[n] != vals[n] for rec in self for n in STATUTORY_DATE_FIELDS & touched)
        )
        if date_moved and not self.env.user.has_group(FINANCE_MANAGER_GROUP):
            raise UserError(
                "The VAT due day and calendar rule move a statutory date, so changing "
                "them needs a finance manager as well as a Platform Admin."
            )
        result = super().write(vals)
        for rec in self:
            moved = [n for n in touched if rec[n] != before[rec.id][n]]
            if moved:
                audit_event(
                    rec.env,
                    "entity.statutory_changed",
                    "fix.entity,%d" % rec.id,
                    "%s changed by %s" % (", ".join(sorted(moved)), rec.env.user.name),
                )
        return result

    # No default: an assumed incorporation date would make every entity look
    # "newly registered" (nil-return eligibility reads it).
    incorporation_date = fields.Date(string="Incorporation / Registration Date")

    def get_vat_return_due_date(self, period_year: int, period_month: int) -> date:
        """Calculate exact VAT return due date for given month.
        Under VAT & SD Act 2012, submission is due by 15th of subsequent month.
        If 15th falls on Friday (weekday 4) or Saturday (weekday 5) in Bangladesh,
        it automatically rolls over to the next working Sunday or next business day."""
        self.ensure_one()
        # Next month calculation
        if period_month == 12:
            sub_year = period_year + 1
            sub_month = 1
        else:
            sub_year = period_year
            sub_month = period_month + 1

        # M65 lc_03: clamp the statutory day to the month's last day (a 31st
        # due day still lands in a 30-day month - as NBR treats month-end).
        due = date(
            sub_year,
            sub_month,
            min(self.vat_statutory_day or 15, calendar.monthrange(sub_year, sub_month)[1]),
        )

        if self.statutory_calendar_rule == "mushak_next_working_day":
            # In Python weekday(): Monday is 0, Tuesday 1, Wednesday 2, Thursday 3, Friday 4, Saturday 5, Sunday 6
            # Bangladesh weekend: Friday (4) and Saturday (5)
            while due.weekday() in (4, 5):  # Friday or Saturday
                due += timedelta(days=1)

            # Holidays from certified packs that are active and loaded: a draft,
            # uncertified or retired pack moves no statutory date (A12 finish E6).
            def holiday_on(day):
                return self.env["fix.country.pack.line"].search(
                    [
                        ("pack_id.kind", "=", "holidays"),
                        ("pack_id.state", "=", "active"),
                        ("pack_id.loaded_at", "!=", False),
                        ("date_value", "=", day),
                    ]
                )

            while holiday_on(due) or due.weekday() in (4, 5):
                due += timedelta(days=1)

        return due

    def get_tds_quarter_due_date(self, quarter: int, fiscal_year_end: int) -> date:
        """Returns statutory filing date for TDS returns per NBR Income Tax Act 2023.
        Quarter 1 (Jul-Sep): Oct 15
        Quarter 2 (Oct-Dec): Jan 15 (next year)
        Quarter 3 (Jan-Mar): Apr 15
        Quarter 4 (Apr-Jun): Jul 15
        """
        self.ensure_one()
        due_map = {
            1: (fiscal_year_end - 1, 10, 15),
            2: (fiscal_year_end, 1, 15),
            3: (fiscal_year_end, 4, 15),
            4: (fiscal_year_end, 7, 15),
        }
        if quarter not in due_map:
            raise ValidationError(f"Invalid TDS quarter {quarter}. Must be 1, 2, 3, or 4.")

        y, m, d = due_map[quarter]
        due = date(y, m, d)
        while due.weekday() in (4, 5):  # Rollover Friday/Saturday
            due += timedelta(days=1)
        return due

    def validate_bd_address(self, address_dict: dict) -> bool:
        """Validate 4-tier Bangladesh address structure: division, district, upazila, postcode."""
        required_keys = ["division", "district", "postcode"]
        for k in required_keys:
            if not address_dict.get(k):
                raise ValidationError(f"Missing mandatory address component: {k}")
        # Verify 4-digit numeric postal code
        postcode = str(address_dict.get("postcode", "")).strip()
        if not (postcode.isdigit() and len(postcode) == 4):
            raise ValidationError(f"Bangladesh postal code must be exactly 4 digits: '{postcode}'")
        return True


def _previous_month(today):
    return (today.year - 1, 12) if today.month == 1 else (today.year, today.month - 1)


class FixNilReturnGenerator(models.Model):
    """Statutory nil-return packs (Mushak 9.1 + TDS) for an entity and tax
    period WITHOUT any recorded transactions - typically a newly registered
    entity, which must file from its month of registration.

    Eligibility is measured, never assumed: "Verify" counts the entity
    company's posted invoices, bills and P&L entries dated in the period.
    The NBR acknowledgement is keyed in from the e-VAT portal; this module
    does not file with NBR."""

    _name = "fix.nil.return.generator"
    _description = "Statutory Nil-Return Generator"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "period_year desc, period_month desc, id desc"

    def _fix_guarded_fields(self) -> set:
        # M65 nr_01: the state machine, the MEASURED count and the statutory
        # payloads are evidence - the actions set them, nobody types them.
        # filing_reference stays open: the officer keys NBR's slip number.
        return super()._fix_guarded_fields() | {
            "state",
            "transaction_count",
            "transactions_counted_at",
            "mushak_9_1_nil_payload",
            "tds_nil_payload",
        }

    # move types that are supplies/purchases whatever accounts they touch
    INVOICE_MOVE_TYPES = (
        "out_invoice",
        "out_refund",
        "in_invoice",
        "in_refund",
        "out_receipt",
        "in_receipt",
    )
    PL_ACCOUNT_TYPES = (
        "income",
        "income_other",
        "expense",
        "expense_other",
        "expense_depreciation",
        "expense_direct_cost",
    )

    name = fields.Char(
        string="Declaration Reference",
        required=True,
        copy=False,
        default=lambda self: self.env["ir.sequence"].next_by_code("fix.nil.return") or "/",
    )
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    entity_id = fields.Many2one("fix.entity", string="Entity", required=True, tracking=True)
    period_year = fields.Integer(
        string="Period Year",
        required=True,
        default=lambda self: _previous_month(fields.Date.context_today(self))[0],
    )
    period_month = fields.Integer(
        string="Period Month",
        required=True,
        default=lambda self: _previous_month(fields.Date.context_today(self))[1],
    )
    due_date = fields.Date(
        string="Statutory Filing Due Date", compute="_compute_due_date", store=True
    )

    is_newly_registered = fields.Boolean(
        string="Newly Registered (<12 Months)", compute="_compute_eligibility", store=True
    )
    transaction_count = fields.Integer(
        string="Transaction Count in Period",
        readonly=True,
        copy=False,
        help="Posted sales/purchase documents and P&L entries of the entity's company "
        "dated in the tax period, counted by Verify Eligibility",
    )
    transactions_counted_at = fields.Datetime(
        string="Transactions Counted At", readonly=True, copy=False
    )
    eligible_for_nil_return = fields.Boolean(
        string="Eligible for Nil Return", compute="_compute_eligibility", store=True
    )

    mushak_9_1_nil_payload = fields.Text(
        string="Mushak 9.1 Nil Return Payload (JSON)", readonly=True
    )
    tds_nil_payload = fields.Text(string="TDS Nil Statement Payload (JSON)", readonly=True)
    filing_reference = fields.Char(string="NBR Acknowledgement Slip No", tracking=True)

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("verified", "Eligibility Verified"),
            ("generated", "Nil Packs Generated"),
            ("submitted", "Submitted to NBR"),
            ("acknowledged", "NBR Acknowledged"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )

    @api.constrains("period_month", "period_year")
    def _check_period(self):
        for rec in self:
            if not 1 <= rec.period_month <= 12:
                raise ValidationError("Period month must be between 1 and 12.")
            if rec.period_year < 2000:
                raise ValidationError("Period year is not valid.")

    @api.depends("entity_id", "period_year", "period_month")
    def _compute_due_date(self):
        for rec in self:
            if rec.entity_id and rec.period_year and 1 <= rec.period_month <= 12:
                rec.due_date = rec.entity_id.get_vat_return_due_date(
                    rec.period_year, rec.period_month
                )
            else:
                rec.due_date = False

    @api.depends(
        "entity_id.incorporation_date",
        "transaction_count",
        "transactions_counted_at",
        "period_year",
        "period_month",
    )
    def _compute_eligibility(self):
        for rec in self:
            inc_date = rec.entity_id.incorporation_date
            if not inc_date or not rec.period_year or not 1 <= rec.period_month <= 12:
                rec.is_newly_registered = False
            else:
                # registered in the period's month or within the 12 months before it
                period_start = date(rec.period_year, rec.period_month, 1)
                inc_month = date(inc_date.year, inc_date.month, 1)
                rec.is_newly_registered = 0 <= (period_start - inc_month).days <= 365
            # Eligible only once the period has actually been counted.
            rec.eligible_for_nil_return = bool(
                rec.entity_id and rec.transactions_counted_at and rec.transaction_count == 0
            )

    def _period_bounds(self):
        start = date(self.period_year, self.period_month, 1)
        nxt = (
            date(self.period_year + 1, 1, 1)
            if self.period_month == 12
            else date(self.period_year, self.period_month + 1, 1)
        )
        return start, nxt - timedelta(days=1)

    def _count_period_transactions(self) -> int:
        """Posted moves of the entity's company dated in the period that are
        sales/purchase documents or touch a P&L account."""
        self.ensure_one()
        start, end = self._period_bounds()
        company = self.entity_id.company_id
        # sudo: eligibility is a statutory fact about the entity's books,
        # counted whatever journals the compliance officer can open.
        return (
            self.env["account.move"]
            .sudo()
            .search_count(
                [
                    ("company_id", "=", company.id),
                    ("state", "=", "posted"),
                    ("date", ">=", start),
                    ("date", "<=", end),
                    "|",
                    ("move_type", "in", self.INVOICE_MOVE_TYPES),
                    ("line_ids.account_id.account_type", "in", self.PL_ACCOUNT_TYPES),
                ]
            )
        )

    def action_verify_eligibility(self):
        """Count the period's real transactions; refuse when there are any."""
        self.ensure_one()
        if self.state not in ("draft", "verified"):
            raise UserError("Eligibility can only be re-verified before the packs are generated.")
        count = self._count_period_transactions()
        if count:
            raise ValidationError(
                f"Entity {self.entity_id.code} has {count} recorded transactions in "
                f"{self.period_year}-{self.period_month:02d}. A standard Mushak 9.1 "
                "transaction return is required instead of a nil return."
            )
        self._guarded().write(
            {
                "transaction_count": 0,
                "transactions_counted_at": fields.Datetime.now(),
                "state": "verified",
            }
        )
        return True

    def action_generate_nil_packs(self):
        """Generate the Mushak 9.1 nil return and TDS nil statement payloads
        for a VERIFIED declaration."""
        self.ensure_one()
        if self.state != "verified":
            raise ValidationError("Nil return must be verified prior to generation.")

        # Statutory identifiers must be the entity's real registrations: a
        # placeholder BIN/TIN in a filing pack would misidentify the taxpayer.
        missing = [
            label
            for label, value in (
                ("BIN", self.entity_id.bin_number),
                ("TIN", self.entity_id.tin_number),
            )
            if not value
        ]
        if missing:
            raise UserError(
                f"Entity {self.entity_id.code} has no registered {' / '.join(missing)}. "
                "Record the NBR registration numbers on the entity before generating "
                "nil-return packs."
            )

        mushak_payload = {
            "mushak_form": "9.1",
            "statutory_act": "Value Added Tax and Supplementary Duty Act 2012",
            "entity_code": self.entity_id.code,
            "entity_name": self.entity_id.legal_name,
            "bin": self.entity_id.bin_number,
            "tax_period": f"{self.period_year}-{self.period_month:02d}",
            "submission_type": "NIL",
            "part_3_supplies": {"total_sales_value": 0.0, "vat_payable": 0.0, "sd_payable": 0.0},
            "part_4_purchases": {"total_purchase_value": 0.0, "rebate_claimable": 0.0},
            "part_5_net_tax": {"net_payable": 0.0},
            "declaration": {
                "officer_name": self.env.user.name,
                "is_zero_liability_certified": True,
                "timestamp_utc": fields.Datetime.now().isoformat(),
            },
        }
        tds_payload = {
            "form": "TDS_MONTHLY_NIL",
            "statutory_act": "Income Tax Act 2023 (Bangladesh)",
            "entity_code": self.entity_id.code,
            "tin": self.entity_id.tin_number,
            "tax_period": f"{self.period_year}-{self.period_month:02d}",
            "withholding_count": 0,
            "total_tds_deducted": 0.0,
            "total_deposited_treasury": 0.0,
            "is_nil_declaration": True,
        }
        self._guarded().write(
            {
                "mushak_9_1_nil_payload": json.dumps(mushak_payload, indent=2),
                "tds_nil_payload": json.dumps(tds_payload, indent=2),
                "state": "generated",
            }
        )
        return True

    def action_submit_to_nbr(self):
        """Record the NBR acknowledgement for a nil return filed on the e-VAT portal.

        There is no NBR e-filing integration in this module: the compliance
        officer files the generated packs on the NBR portal and enters the
        acknowledgement slip number NBR issued in ``filing_reference``. This
        action refuses until the packs exist and that real slip number is
        present."""
        self.ensure_one()
        if self.state != "generated" or not self.mushak_9_1_nil_payload:
            raise UserError("Generate the nil-return packs before recording the NBR filing.")
        ack_ref = (self.filing_reference or "").strip()
        if not ack_ref:
            raise UserError(
                "Enter the NBR acknowledgement slip number issued by the e-VAT portal "
                "before recording this nil return as acknowledged. This system does not "
                "file with NBR and cannot generate an acknowledgement itself."
            )
        self._guarded().write({"filing_reference": ack_ref, "state": "acknowledged"})
        return True
