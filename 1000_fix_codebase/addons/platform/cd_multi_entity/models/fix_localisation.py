# fix.localisation — Entity Localisation & Nil-Return Automation (CD-M65-01 / CD-M65-02).
import json
from datetime import date, timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class FixEntityLocalisation(models.Model):
    """Extension to fix.entity providing Bangladesh tax localisation, statutory calendars, and address rules."""

    _inherit = "fix.entity"

    bin_number = fields.Char(
        string="Business Identification No (BIN / VAT)",
        size=16,
        help="13-digit statutory VAT registration number under VAT & SD Act 2012",
    )
    tin_number = fields.Char(
        string="Taxpayer Identification No (TIN)",
        size=16,
        help="12-digit e-TIN under Income Tax Act 2023",
    )
    vat_statutory_day = fields.Integer(
        string="VAT Due Day of Month",
        default=15,
        help="Statutory submission day (default 15th per Mushak rules)",
    )
    statutory_calendar_rule = fields.Selection(
        [
            ("mushak_next_working_day", "Mushak 15th or Next Working Day (BD Weekend Rollover)"),
            ("strict_calendar_day", "Strict Calendar Day (No Rollover)"),
        ],
        string="Tax Calendar Rule",
        default="mushak_next_working_day",
        required=True,
    )

    incorporation_date = fields.Date(
        string="Incorporation / Registration Date", default=fields.Date.context_today
    )

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

        due = date(sub_year, sub_month, self.vat_statutory_day or 15)

        if self.statutory_calendar_rule == "mushak_next_working_day":
            # In Python weekday(): Monday is 0, Tuesday 1, Wednesday 2, Thursday 3, Friday 4, Saturday 5, Sunday 6
            # Bangladesh weekend: Friday (4) and Saturday (5)
            while due.weekday() in (4, 5):  # Friday or Saturday
                due += timedelta(days=1)

            # Check gazetted holidays from country pack lines if available
            holidays = self.env["fix.country.pack.line"].search(
                [
                    ("pack_id.kind", "=", "holidays"),
                    ("date_value", "=", due),
                ]
            )
            while holidays or due.weekday() in (4, 5):
                due += timedelta(days=1)
                holidays = self.env["fix.country.pack.line"].search(
                    [
                        ("pack_id.kind", "=", "holidays"),
                        ("date_value", "=", due),
                    ]
                )

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


class FixNilReturnGenerator(models.Model):
    """Automates statutory Nil-Return generation for newly registered entities (R10-M01-T04).
    Section 0.7.4 item 2: Mandatory nil return for newly registered entities with no transactions
    from the month of registration."""

    _name = "fix.nil.return.generator"
    _description = "Statutory Nil-Return Generator"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "period_year desc, period_month desc, id desc"

    name = fields.Char(
        string="Declaration Reference",
        required=True,
        default=lambda self: self.env["ir.sequence"].next_by_code("fix.nil.return")
        or "NIL-RET-2026",
    )
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    entity_id = fields.Many2one("fix.entity", string="Entity", required=True, tracking=True)
    period_year = fields.Integer(string="Period Year", required=True, default=2026)
    period_month = fields.Integer(string="Period Month", required=True, default=6)
    due_date = fields.Date(
        string="Statutory Filing Due Date", compute="_compute_due_date", store=True
    )

    is_newly_registered = fields.Boolean(
        string="Newly Registered (<12 Months)", compute="_compute_eligibility", store=True
    )
    transaction_count = fields.Integer(
        string="Transaction Count in Period",
        default=0,
        help="Total sales and purchase invoices recorded in the tax period",
    )
    eligible_for_nil_return = fields.Boolean(
        string="Eligible for Nil Return", compute="_compute_eligibility", store=True
    )

    mushak_9_1_nil_payload = fields.Text(string="Mushak 9.1 Nil Return Payload (JSON)")
    tds_nil_payload = fields.Text(string="TDS Nil Statement Payload (JSON)")
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

    @api.depends("entity_id", "period_year", "period_month")
    def _compute_due_date(self):
        for rec in self:
            if rec.entity_id and rec.period_year and rec.period_month:
                rec.due_date = rec.entity_id.get_vat_return_due_date(
                    rec.period_year, rec.period_month
                )
            else:
                rec.due_date = False

    @api.depends("entity_id", "transaction_count", "period_year", "period_month")
    def _compute_eligibility(self):
        for rec in self:
            if not rec.entity_id:
                rec.is_newly_registered = False
                rec.eligible_for_nil_return = False
                continue

            # Check if incorporated in current or preceding fiscal year
            inc_date = rec.entity_id.incorporation_date or fields.Date.context_today(rec)
            period_date = date(rec.period_year, rec.period_month, 1)
            days_since = (period_date - inc_date).days
            is_new = 0 <= days_since <= 365

            rec.is_newly_registered = is_new
            # Eligible if 0 transactions
            rec.eligible_for_nil_return = rec.transaction_count == 0

    def action_verify_eligibility(self):
        """Verify statutory criteria for Nil-Return submission."""
        self.ensure_one()
        self._compute_eligibility()
        if not self.eligible_for_nil_return:
            raise ValidationError(
                f"Entity {self.entity_id.code} has {self.transaction_count} recorded transactions. "
                "Standard Mushak 9.1 transaction return required instead of Nil Return."
            )
        self.state = "verified"
        return True

    def action_generate_nil_packs(self):
        """Generate official NBR Mushak 9.1 Nil Return and TDS Nil Statement schemas."""
        self.ensure_one()
        if self.state not in ("verified", "draft"):
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

        # Mushak 9.1 Zero Return Schema
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

        # TDS Nil Return Schema
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

        self.write(
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
        action refuses until that real slip number is present. (It previously
        minted ``NBR-ACK-<entity>-<period>-NIL`` itself and marked the return
        acknowledged without anything being filed.)
        """
        self.ensure_one()
        if not self.mushak_9_1_nil_payload:
            self.action_generate_nil_packs()
        ack_ref = (self.filing_reference or "").strip()
        if not ack_ref:
            raise UserError(
                "Enter the NBR acknowledgement slip number issued by the e-VAT portal "
                "before recording this nil return as acknowledged. This system does not "
                "file with NBR and cannot generate an acknowledgement itself."
            )
        self.write(
            {
                "filing_reference": ack_ref,
                "state": "acknowledged",
            }
        )
        return True
