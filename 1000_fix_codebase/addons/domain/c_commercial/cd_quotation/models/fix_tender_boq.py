# M36 tender BOQ, bid pricing and PPR 2025 contract terms (quote-to-cash,
# tender part, 13 Nov 2026).
#
# A tender carried one typed "bid price lodged" and nothing behind it: no
# bill of quantities, no price schedule, no internal approval of the price.
# Bangladesh public tenders (PPR 2025, in force 28 Sep 2025; BPPA standard
# tender documents e-PG2 / e-PG3) are priced line by line on the price
# schedule (forms e-PG2-3A goods / 3B related services): item no.,
# description, country of origin, unit, quantity, unit price and total price
# INCLUDING VAT and levies, point of delivery, delivery period required /
# offered. Now:
#
#   BOQ        fix.tender.line, imported from the procuring entity's sheet
#              (.xlsx / .csv, header matched to the STD column names) or
#              typed; editable only while the bid is a draft.
#   pricing    Price as Quotation builds a draft fix.quotation (contract) from
#              the BOQ, one line per item at the unit price EXCLUDING VAT
#              (the quotation adds VAT once), so the bid price goes through
#              the quotation's value-band approval. bid_value then follows the
#              quotation's total payable (incl. VAT) while the bid is a draft.
#   submit     refused until the quotation is approved and every BOQ line is
#              priced on it, line for line. A lodged bid's quotation is frozen
#              and is never issued as a customer quotation: the award, not a
#              quotation acceptance, creates the contract.
#   terms      tender type, validity 60-150 days (public), retention, LD,
#              performance security, NoA deadlines on the Bangladesh working
#              week (Sun-Thu) and the acceptance certificate after award.
import base64
import csv
import io
import re
from datetime import timedelta

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_quotation import dhaka_today
from .fix_quote_ops import QUOTE_TERMS
from .fix_quote_scope import EDITABLE_STATES

# Bangladesh: Friday and Saturday are the weekly holidays (Python weekday()).
BD_WEEKEND = (4, 5)

# PPR 2025 / BPPA STD defaults. The numbers the business must confirm per
# tender are entered on the tender; these only seed a new one.
PUBLIC_VALIDITY_RANGE = (60, 150)  # tender validity, days
PERFORMANCE_SECURITY_WORKING_DAYS = 7  # furnished within 7 working days of the NoA
CONTRACT_SIGNING_DAYS = 14  # contract signed within 14 days of the NoA
PERFORMANCE_SECURITY_EXTRA_DAYS = 28  # valid 28 days past completion
LD_PUBLIC_BAND = (0.03, 0.05)  # % of the contract price per day of delay
LD_PUBLIC_CAP = 10.0  # % of the contract price
RETENTION_PUBLIC = 10.0  # % of each payment after acceptance

TENDER_TYPES = [
    ("public_egp", "Public tender (e-GP, PPR 2025)"),
    ("private_rfq", "Private RFQ"),
    ("private_rfp", "Private RFP"),
]
LINE_KINDS = [("goods", "Goods (e-PG2-3A)"), ("related_service", "Related services (e-PG2-3B)")]

# Frozen once the bid is lodged (the tender documents' terms and the BOQ).
BOQ_BID_TERMS = frozenset(
    {
        "tender_type",
        "procuring_entity",
        "egp_package_no",
        "retention_pct",
        "ld_rate_pct_per_day",
        "ld_cap_pct",
        "boq_file",
        "boq_filename",
    }
)
# Frozen once the outcome is decided.
BOQ_AWARD_TERMS = frozenset({"noa_date"})
# Frozen once the acceptance certificate is recorded.
ACCEPTANCE_TERMS = frozenset(
    {"teac_certificate_no", "teac_certificate_date", "teac_accepted_value"}
)
BOQ_STAMPS = frozenset({"quotation_id", "acceptance_recorded_by", "acceptance_recorded_at"})

# Context flag: the pricing action links BOQ lines to their quotation lines.
LINKING = "fix_tender_boq_linking"

# The price schedule columns (BPPA e-PG2-3A / 3B), matched on a normalised
# header (lower case, punctuation folded to spaces).
REQUIRED_COLUMNS = ("item_no", "description", "unit", "quantity", "unit_price")
COLUMN_LABELS = {
    "item_no": "Item No.",
    "line_kind": "Type (goods / related service)",
    "description": "Description",
    "country_of_origin": "Country of Origin",
    "unit": "Unit",
    "quantity": "Quantity",
    "unit_price": "Unit Price (incl. VAT)",
    "total_price": "Total Price",
    "point_of_delivery": "Point of Delivery",
    "delivery_period_required": "Delivery Period Required",
    "delivery_period_offered": "Delivery Period Offered",
}


def add_bd_working_days(start, days, holidays=()):
    """`days` Bangladesh working days after `start`: Friday and Saturday are
    the weekend, and any date in `holidays` is skipped too."""
    current, left = start, days
    while left > 0:
        current += timedelta(days=1)
        if current.weekday() in BD_WEEKEND or current in holidays:
            continue
        left -= 1
    return current


def _canon(header) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(header or "").lower()).strip()


def match_column(header):
    """The BOQ field a price-schedule header names, or None."""
    h = _canon(header)
    if not h:
        return None
    if h in ("item no", "item", "item number", "item sl no", "sl no", "serial no"):
        return "item_no"
    if h.startswith("description"):
        return "description"
    if h in ("type", "kind", "line kind", "line type", "goods or related service"):
        return "line_kind"
    if "country of origin" in h:
        return "country_of_origin"
    if h in ("unit", "unit of measurement", "unit of measure", "uom", "unit of supply"):
        return "unit"
    if h in ("qty", "quantity") or h.startswith("quantity"):
        return "quantity"
    if h.startswith("unit price"):
        return "unit_price"
    if h.startswith("total price") or h in ("total", "amount"):
        return "total_price"
    if "point of delivery" in h:
        return "point_of_delivery"
    if "delivery" in h and "required" in h:
        return "delivery_period_required"
    if "delivery" in h and "offered" in h:
        return "delivery_period_offered"
    return None


def _number(value):
    """A cell as a float; None when blank. Raises ValueError on text."""
    if value is None:
        return None
    if isinstance(value, int | float):
        return float(value)
    text = str(value).strip().replace(",", "")
    text = re.sub(r"^(bdt|tk\.?|৳)\s*", "", text, flags=re.I)
    if not text:
        return None
    return float(text)


def _kind(value, default="goods"):
    h = _canon(value)
    if not h:
        return default
    if "service" in h:
        return "related_service"
    if "good" in h:
        return "goods"
    raise ValueError(value)


def read_rows(raw: bytes, filename: str) -> list:
    """The sheet as a list of rows (lists of cell values)."""
    name = (filename or "").lower()
    if name.endswith(".csv"):
        text = raw.decode("utf-8-sig", errors="replace")
        return list(csv.reader(io.StringIO(text)))
    if name.endswith((".xlsx", ".xlsm")):
        try:
            import openpyxl
        except ImportError as exc:  # pragma: no cover - the venv ships it
            raise UserError("Excel import needs openpyxl; upload the BOQ as .csv.") from exc
        try:
            book = openpyxl.load_workbook(io.BytesIO(raw), read_only=True, data_only=True)
        except Exception as exc:
            raise UserError("The BOQ file %s is not a readable .xlsx workbook." % filename) from exc
        sheet = book.worksheets[0]
        return [list(row) for row in sheet.iter_rows(values_only=True)]
    raise UserError("The BOQ is imported from an .xlsx or .csv file; %s is neither." % filename)


def parse_boq(rows: list, default_kind="goods"):
    """(lines, errors): BOQ line values from a price schedule, or the reasons
    it cannot be read. The header row is the first of the first 25 rows that
    names every required column (title rows above it are skipped)."""
    best, best_cols = None, {}
    for idx, row in enumerate(rows[:25]):
        cols = {}
        for pos, cell in enumerate(row or []):
            key = match_column(cell)
            if key and key not in cols:
                cols[key] = pos
        if all(k in cols for k in REQUIRED_COLUMNS):
            best, best_cols = idx, cols
            break
        if len(cols) > len(best_cols):
            best_cols = cols
    if best is None:
        missing = [COLUMN_LABELS[k] for k in REQUIRED_COLUMNS if k not in best_cols]
        return [], [
            "No header row names the price-schedule columns; missing: %s. Expected the "
            "BPPA e-PG2-3A/3B headings (Item No., Description, Country of Origin, Unit, "
            "Quantity, Unit Price, Total Price, Point of Delivery, Delivery Period)."
            % ", ".join(missing)
        ]
    lines, errors = [], []

    def cell(row, key):
        pos = best_cols.get(key)
        return row[pos] if pos is not None and pos < len(row) else None

    for idx, row in enumerate(rows[best + 1 :], start=best + 2):
        row = list(row or [])
        if not any(str(v).strip() for v in row if v is not None):
            continue
        texts = {
            k: str(cell(row, k)).strip() if cell(row, k) is not None else "" for k in COLUMN_LABELS
        }
        try:
            qty = _number(cell(row, "quantity"))
        except ValueError:
            errors.append("Row %d: quantity '%s' is not a number." % (idx, texts["quantity"]))
            continue
        try:
            price = _number(cell(row, "unit_price"))
        except ValueError:
            errors.append("Row %d: unit price '%s' is not a number." % (idx, texts["unit_price"]))
            continue
        if qty is None and price is None:
            # a sub-heading or the schedule's total row
            continue
        if not texts["description"]:
            errors.append("Row %d: the description is empty." % idx)
            continue
        if qty is None or qty <= 0:
            errors.append("Row %d (%s): the quantity must be above zero." % (idx, texts["item_no"]))
            continue
        if price is not None and price < 0:
            errors.append("Row %d (%s): a unit price cannot be negative." % (idx, texts["item_no"]))
            continue
        try:
            total = _number(cell(row, "total_price"))
        except ValueError:
            total = None
        if total is not None and price and abs(total - round(qty * price, 2)) > 0.01:
            errors.append(
                "Row %d (%s): total price %.2f is not quantity x unit price (%.2f)."
                % (idx, texts["item_no"], total, qty * price)
            )
            continue
        try:
            kind = _kind(cell(row, "line_kind"), default_kind)
        except ValueError:
            errors.append(
                "Row %d: type '%s' is neither goods nor related service."
                % (idx, texts["line_kind"])
            )
            continue
        lines.append(
            {
                "item_no": texts["item_no"] or str(len(lines) + 1),
                "line_kind": kind,
                "description": texts["description"],
                "country_of_origin": texts["country_of_origin"] or False,
                "unit": texts["unit"] or False,
                "quantity": qty,
                "unit_price_incl_vat": price or 0.0,
                "point_of_delivery": texts["point_of_delivery"] or False,
                "delivery_period_required": texts["delivery_period_required"] or False,
                "delivery_period_offered": texts["delivery_period_offered"] or False,
            }
        )
    if not lines and not errors:
        errors.append("The price schedule has no item rows under its header.")
    return lines, errors


class FixTenderLine(models.Model):
    """One item of the tender's bill of quantities / price schedule (BPPA
    e-PG2-3A goods, 3B related services). Prices include VAT and levies."""

    _name = "fix.tender.line"
    _description = "Tender BOQ / Price Schedule Line"
    _order = "tender_id, sequence, id"

    tender_id = fields.Many2one("fix.tender", required=True, ondelete="cascade", index=True)
    company_id = fields.Many2one(related="tender_id.company_id", store=True, index=True)
    operating_unit_id = fields.Many2one(
        related="tender_id.operating_unit_id", store=True, index=True
    )
    currency_id = fields.Many2one(related="tender_id.currency_id")
    sequence = fields.Integer(default=10)
    item_no = fields.Char(string="Item No.", required=True)
    line_kind = fields.Selection(LINE_KINDS, string="Type", required=True, default="goods")
    description = fields.Char(required=True)
    product_id = fields.Many2one("product.product", string="Our Item / Service")
    country_of_origin = fields.Char()
    unit = fields.Char()
    quantity = fields.Float(default=1.0, digits="Product Unit of Measure")
    unit_price_incl_vat = fields.Monetary(
        string="Unit Price (incl. VAT)",
        currency_field="currency_id",
        help="The bid price per unit as the price schedule states it: including VAT and "
        "all levies (BPPA STD).",
    )
    total_price = fields.Monetary(
        string="Total Price (incl. VAT)",
        currency_field="currency_id",
        compute="_compute_total",
        store=True,
    )
    point_of_delivery = fields.Char()
    delivery_period_required = fields.Char(string="Delivery Period Required")
    delivery_period_offered = fields.Char(string="Delivery Period Offered")
    quotation_line_id = fields.Many2one(
        "fix.quotation.line",
        string="Priced On",
        readonly=True,
        ondelete="set null",
        copy=False,
        help="The quotation line that prices this item (Price as Quotation).",
    )

    @api.depends("quantity", "unit_price_incl_vat")
    def _compute_total(self):
        for line in self:
            line.total_price = round((line.quantity or 0.0) * (line.unit_price_incl_vat or 0.0), 2)

    @api.constrains("quantity", "unit_price_incl_vat")
    def _check_numbers(self):
        for line in self:
            if (line.quantity or 0.0) < 0 or (line.unit_price_incl_vat or 0.0) < 0:
                raise ValidationError(
                    "BOQ item %s cannot have a negative quantity or price." % line.item_no
                )

    def _assert_tender_open(self, tenders):
        if self.env.su:
            return
        lodged = tenders.filtered(lambda t: t.state != "draft")
        if lodged:
            raise UserError(
                "The BOQ of tender %s is frozen: the bid is %s." % (lodged[0].name, lodged[0].state)
            )

    @api.model_create_multi
    def create(self, vals_list):
        ids = [v["tender_id"] for v in vals_list if v.get("tender_id")]
        self._assert_tender_open(self.env["fix.tender"].browse(ids).exists())
        if not self.env.context.get(LINKING) and not self.env.su:
            for vals in vals_list:
                vals.pop("quotation_line_id", None)
        return super().create(vals_list)

    def write(self, vals):
        self._assert_tender_open(self.mapped("tender_id"))
        if "tender_id" in vals and any(line.tender_id.id != vals["tender_id"] for line in self):
            raise UserError("A BOQ line never moves to another tender.")
        if "quotation_line_id" in vals and not (self.env.context.get(LINKING) or self.env.su):
            raise UserError("A BOQ line is linked to its quotation line by Price as Quotation.")
        return super().write(vals)

    def unlink(self):
        self._assert_tender_open(self.mapped("tender_id"))
        return super().unlink()

    def _ex_vat_price(self, vat_rate) -> float:
        self.ensure_one()
        return round((self.unit_price_incl_vat or 0.0) / (1.0 + (vat_rate or 0.0) / 100.0), 2)


class FixTenderBoq(models.Model):
    _inherit = "fix.tender"

    # ---- header (PPR 2025) -------------------------------------------------
    tender_type = fields.Selection(TENDER_TYPES, required=True, default="public_egp", tracking=True)
    procuring_entity = fields.Char(
        string="Procuring Entity (office)",
        help="The procuring entity's office as the tender notice names it (the contract "
        "party is the linked partner).",
    )
    egp_package_no = fields.Char(string="e-GP Package No.")
    retention_pct = fields.Float(
        string="Retention (%)",
        default=RETENTION_PUBLIC,
        help="Withheld from each payment after the acceptance committee's acceptance.",
    )
    ld_rate_pct_per_day = fields.Float(
        string="Liquidated Damages (% per day)",
        default=0.05,
        digits=(5, 3),
        help="Of the contract price per day of delay; PPR 2025 STDs use 0.03-0.05%.",
    )
    ld_cap_pct = fields.Float(
        string="LD Cap (%)", default=LD_PUBLIC_CAP, help="Of the contract price."
    )
    performance_security_pct = fields.Float(default=10.0)
    ppr_warnings = fields.Text(
        string="PPR 2025 Checks",
        compute="_compute_ppr_warnings",
        help="Terms outside the usual PPR 2025 / STD values: confirm them against the "
        "tender documents.",
    )
    # ---- BOQ ---------------------------------------------------------------
    boq_line_ids = fields.One2many("fix.tender.line", "tender_id", string="BOQ / Price Schedule")
    boq_file = fields.Binary(
        string="BOQ File (.xlsx / .csv)",
        attachment=True,
        copy=False,
        help="The procuring entity's price schedule; Import BOQ reads it.",
    )
    boq_filename = fields.Char(string="BOQ File Name", copy=False)
    boq_total = fields.Monetary(
        string="BOQ Total (incl. VAT)",
        currency_field="currency_id",
        compute="_compute_boq_totals",
        store=True,
    )
    boq_line_count = fields.Integer(string="BOQ Items", compute="_compute_boq_totals", store=True)
    boq_unpriced_count = fields.Integer(
        string="Unpriced Items", compute="_compute_boq_totals", store=True
    )
    # ---- pricing through a quotation --------------------------------------
    quotation_id = fields.Many2one(
        "fix.quotation",
        string="Pricing Quotation",
        readonly=True,
        copy=False,
        index=True,
        ondelete="restrict",
        help="The quotation that prices the BOQ and carries the internal price approval.",
    )
    quotation_state = fields.Selection(related="quotation_id.state", string="Quotation State")
    bid_value = fields.Monetary(
        compute="_compute_bid_value",
        store=True,
        readonly=False,
        help="Our submitted price incl. VAT. With a pricing quotation it is the quotation's "
        "total payable (incl. VAT), kept in step while the bid is a draft; frozen once the "
        "bid is submitted.",
    )
    # ---- NoA and its deadlines ---------------------------------------------
    noa_date = fields.Date(string="NoA Date", copy=False, tracking=True)
    performance_security_due = fields.Date(
        string="Performance Security Due",
        compute="_compute_noa_deadlines",
        help="7 working days after the NoA (Sun-Thu week; national holidays skipped).",
    )
    contract_signing_due = fields.Date(
        string="Contract Signing Due",
        compute="_compute_noa_deadlines",
        help="14 days after the NoA.",
    )
    performance_security_valid_until = fields.Date(
        string="Performance Security Valid Until",
        compute="_compute_noa_deadlines",
        help="28 days past the contract's completion.",
    )
    # ---- acceptance (after the award) --------------------------------------
    teac_certificate_no = fields.Char(string="Acceptance Certificate No.", copy=False)
    teac_certificate_date = fields.Date(string="Acceptance Certificate Date", copy=False)
    teac_accepted_value = fields.Monetary(
        string="Accepted Value", currency_field="currency_id", copy=False
    )
    acceptance_recorded_by = fields.Many2one("res.users", readonly=True, copy=False)
    acceptance_recorded_at = fields.Datetime(readonly=True, copy=False)
    retention_amount = fields.Monetary(
        string="Retention (BDT)",
        currency_field="currency_id",
        compute="_compute_retention",
        store=True,
    )

    # ---- computes ----------------------------------------------------------
    @api.depends("boq_line_ids.total_price", "boq_line_ids.unit_price_incl_vat")
    def _compute_boq_totals(self):
        for rec in self:
            lines = rec.boq_line_ids
            rec.boq_total = round(sum(lines.mapped("total_price")), 2)
            rec.boq_line_count = len(lines)
            rec.boq_unpriced_count = len(
                lines.filtered(lambda r: (r.unit_price_incl_vat or 0) <= 0)
            )

    @api.depends("quotation_id", "quotation_id.amount_total")
    def _compute_bid_value(self):
        # Only a draft bid follows its quotation; a lodged bid keeps the price
        # it was lodged at. Without a quotation the typed value stays.
        for rec in self:
            if rec.quotation_id and rec.state == "draft":
                rec.bid_value = rec.quotation_id.amount_total

    @api.depends("noa_date", "contract_months", "converted_res_id")
    def _compute_noa_deadlines(self):
        for rec in self:
            noa = rec.noa_date
            if not noa:
                rec.performance_security_due = False
                rec.contract_signing_due = False
                rec.performance_security_valid_until = False
                continue
            holidays = rec._bd_holidays(noa, noa + timedelta(days=60))
            rec.performance_security_due = add_bd_working_days(
                noa, PERFORMANCE_SECURITY_WORKING_DAYS, holidays
            )
            rec.contract_signing_due = noa + timedelta(days=CONTRACT_SIGNING_DAYS)
            end = rec._contract_end()
            if not end:
                end = noa + relativedelta(months=rec.contract_months or 12)
            rec.performance_security_valid_until = end + timedelta(
                days=PERFORMANCE_SECURITY_EXTRA_DAYS
            )

    @api.depends("teac_accepted_value", "retention_pct")
    def _compute_retention(self):
        for rec in self:
            rec.retention_amount = round(
                (rec.teac_accepted_value or 0.0) * (rec.retention_pct or 0.0) / 100.0, 2
            )

    @api.depends(
        "tender_type",
        "bid_validity_days",
        "ld_rate_pct_per_day",
        "ld_cap_pct",
        "retention_pct",
        "performance_security_pct",
    )
    def _compute_ppr_warnings(self):
        for rec in self:
            notes = []
            if rec.tender_type == "public_egp":
                low, high = LD_PUBLIC_BAND
                rate = rec.ld_rate_pct_per_day or 0.0
                if rate and not low - 1e-9 <= rate <= high + 1e-9:
                    notes.append(
                        "LD %.3f%% per day is outside the usual %.2f-%.2f%% band."
                        % (rate, low, high)
                    )
                if (rec.ld_cap_pct or 0.0) > LD_PUBLIC_CAP + 1e-9:
                    notes.append("An LD cap above %.0f%% is unusual." % LD_PUBLIC_CAP)
                if abs((rec.retention_pct or 0.0) - RETENTION_PUBLIC) > 1e-9:
                    notes.append("Retention is usually %.0f%%." % RETENTION_PUBLIC)
                if abs((rec.performance_security_pct or 0.0) - 10.0) > 1e-9:
                    notes.append("The STDs ask a 10% performance security.")
                if not rec.bid_validity_days:
                    notes.append("State the tender validity (60-150 days).")
            rec.ppr_warnings = "\n".join(notes) or False

    # ---- helpers -----------------------------------------------------------
    def _bd_holidays(self, date_from, date_to) -> set:
        """National holidays from the certified country pack (rows a pack
        loaded into a working calendar), as dates."""
        Holiday = self.env.get("fix.working.calendar.holiday")
        if Holiday is None or "pack_line_id" not in Holiday._fields:
            return set()
        days = set()
        rows = Holiday.sudo().search(
            [
                ("pack_line_id", "!=", False),
                ("date_from", "<=", date_to),
                ("date_to", ">=", date_from),
            ]
        )
        for row in rows:
            day = row.date_from
            while day <= row.date_to:
                days.add(day)
                day += timedelta(days=1)
        return days

    def _contract_end(self):
        self.ensure_one()
        model, res_id = self.converted_res_model, self.converted_res_id
        if not (model and res_id) or model not in self.env:
            return False
        contract = self.env[model].sudo().browse(res_id).exists()
        if contract and "date_end" in contract._fields:
            return contract.date_end or False
        return False

    # ---- validation --------------------------------------------------------
    @api.constrains("tender_type", "bid_validity_days")
    def _check_validity_days(self):
        low, high = PUBLIC_VALIDITY_RANGE
        for rec in self:
            days = rec.bid_validity_days or 0
            if days < 0:
                raise ValidationError("The tender validity cannot be negative.")
            if rec.tender_type == "public_egp" and days and not low <= days <= high:
                raise ValidationError(
                    "A public tender's validity is %d to %d days (PPR 2025); %d was entered."
                    % (low, high, days)
                )

    @api.constrains("retention_pct", "ld_rate_pct_per_day", "ld_cap_pct")
    def _check_contract_terms(self):
        for rec in self:
            if not 0.0 <= (rec.retention_pct or 0.0) <= 100.0:
                raise ValidationError("Retention is between 0 and 100% of each payment.")
            if not 0.0 <= (rec.ld_rate_pct_per_day or 0.0) <= 1.0:
                raise ValidationError(
                    "Liquidated damages are a daily rate between 0 and 1% of the contract price."
                )
            if not 0.0 <= (rec.ld_cap_pct or 0.0) <= 100.0:
                raise ValidationError("The LD cap is between 0 and 100% of the contract price.")
            if (rec.ld_rate_pct_per_day or 0.0) > 0.0 and not rec.ld_cap_pct:
                raise ValidationError("Liquidated damages need a cap (PPR 2025 STDs: 10%).")

    @api.constrains("noa_date", "teac_certificate_date", "teac_accepted_value")
    def _check_dates(self):
        for rec in self:
            today = dhaka_today(rec)
            if rec.noa_date and rec.noa_date > today:
                raise ValidationError("The Notification of Award cannot be dated in the future.")
            if rec.teac_certificate_date and rec.teac_certificate_date > today:
                raise ValidationError("An acceptance certificate cannot be dated in the future.")
            if (rec.teac_accepted_value or 0.0) < 0:
                raise ValidationError("The accepted value cannot be negative.")

    # ---- guard -------------------------------------------------------------
    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | BOQ_STAMPS

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(t.state != "draft" for t in self):
            locked |= BOQ_BID_TERMS | {"boq_line_ids"}
        if self and any(t.state in ("no_bid", "won", "lost", "cancelled") for t in self):
            locked |= BOQ_AWARD_TERMS
        if self and any(t.acceptance_recorded_at or t.state != "won" for t in self):
            locked |= ACCEPTANCE_TERMS
        if self and any(t.quotation_id for t in self):
            locked.add("bid_value")
        return locked

    def write(self, vals):
        if not self._fix_guard_open():
            for terms, frozen_in, why in (
                (BOQ_BID_TERMS, lambda t: t.state != "draft", "the bid has been lodged"),
                (
                    BOQ_AWARD_TERMS,
                    lambda t: t.state in ("no_bid", "won", "lost", "cancelled"),
                    "it is decided",
                ),
                (
                    ACCEPTANCE_TERMS,
                    lambda t: bool(t.acceptance_recorded_at),
                    "the acceptance is recorded",
                ),
            ):
                touched = terms & set(vals)
                if not touched:
                    continue
                hit = self.filtered(
                    lambda t, f=frozen_in, n=touched: f(t)
                    and any(t._fix_guard_differs(k, vals[k], t[k]) for k in n)
                )
                if hit:
                    raise UserError(
                        "Tender %s cannot change: %s (%s)." % (hit[0].name, why, hit[0].state)
                    )
            if "bid_value" in vals:
                hit = self.filtered(
                    lambda t: t.quotation_id
                    and t.state == "draft"
                    and abs((vals["bid_value"] or 0.0) - (t.quotation_id.amount_total or 0.0))
                    > 0.005
                )
                if hit:
                    raise UserError(
                        "Tender %s is priced by quotation %s: the bid price is its total "
                        "payable (BDT %.2f), changed on the quotation."
                        % (hit[0].name, hit[0].quotation_id.name, hit[0].quotation_id.amount_total)
                    )
        return super().write(vals)

    # ---- BOQ import --------------------------------------------------------
    def _boq_source(self, attachment_id=None):
        """(bytes, filename) of the BOQ to import: the named attachment of
        this tender, else the BOQ file on the form, else the newest .xlsx /
        .csv attached to the tender."""
        self.ensure_one()
        Attachment = self.env["ir.attachment"]
        if attachment_id:
            att = Attachment.browse(int(attachment_id)).exists()
            if not att or att.res_model != self._name or att.res_id != self.id:
                raise UserError("That file is not attached to tender %s." % self.name)
            return base64.b64decode(att.datas or b""), att.name
        if self.boq_file:
            return base64.b64decode(self.boq_file), self.boq_filename or "boq.xlsx"
        atts = Attachment.search(
            [("res_model", "=", self._name), ("res_id", "=", self.id)], order="id desc"
        ).filtered(lambda a: (a.name or "").lower().endswith((".xlsx", ".xlsm", ".csv")))
        if not atts:
            raise UserError(
                "Upload the price schedule (.xlsx or .csv) in the BOQ File field, or attach "
                "it to tender %s, then import it." % self.name
            )
        return base64.b64decode(atts[0].datas or b""), atts[0].name

    def action_import_boq(self, attachment_id=None):
        """Replace the draft BOQ with the price schedule's rows."""
        for rec in self:
            if rec.state != "draft":
                raise UserError(
                    "The BOQ of tender %s is frozen: the bid is %s." % (rec.name, rec.state)
                )
            raw, filename = rec._boq_source(attachment_id)
            lines, errors = parse_boq(read_rows(raw, filename))
            if errors:
                shown = errors[:20]
                more = len(errors) - len(shown)
                raise UserError(
                    "BOQ %s was not imported:\n%s%s"
                    % (filename, "\n".join(shown), "\n(and %d more)" % more if more else "")
                )
            rec.boq_line_ids.unlink()
            self.env["fix.tender.line"].create(
                [
                    dict(vals, tender_id=rec.id, sequence=(i + 1) * 10)
                    for i, vals in enumerate(lines)
                ]
            )
            rec.message_post(
                body="BOQ imported from %s: %d item(s), BDT %.2f incl. VAT."
                % (filename, len(lines), rec.boq_total)
            )
        return True

    # ---- pricing through a quotation --------------------------------------
    def _quotation_header(self) -> dict:
        self.ensure_one()
        valid_until = self.due_date + timedelta(days=self.bid_validity_days or 0)
        return {
            "customer_id": self.client_id.id,
            "quote_type": "contract",
            "contract_family": self.contract_family or "managed",
            "contract_months": self.contract_months or 12,
            "operating_unit_id": self.operating_unit_id.id,
            "currency_id": self.currency_id.id,
            "company_id": self.company_id.id,
            "valid_until": valid_until,
        }

    def action_price_as_quotation(self):
        """Price the BOQ on a draft contract quotation (one line per item,
        unit price excluding VAT), so the price takes the quotation's
        value-band approval. Re-running it re-prices the same quotation while
        that is a draft or approved (a change sends it back for approval)."""
        Quote = self.env["fix.quotation"]
        Line = self.env["fix.quotation.line"]
        for rec in self:
            if rec.state != "draft":
                raise UserError(
                    "Tender %s is %s: its bid is already priced." % (rec.name, rec.state)
                )
            problems = []
            if not rec.client_id:
                problems.append("Link the procuring entity (the quotation's customer).")
            if not rec.operating_unit_id:
                problems.append("Set the operating unit.")
            if not rec.boq_line_ids:
                problems.append("Import or enter the BOQ first.")
            unpriced = rec.boq_line_ids.filtered(
                lambda r: (r.unit_price_incl_vat or 0.0) <= 0.0 or (r.quantity or 0.0) <= 0.0
            )
            if unpriced:
                problems.append(
                    "Price every BOQ item (unit price incl. VAT and quantity): %s."
                    % ", ".join(unpriced.mapped("item_no")[:10])
                )
            if problems:
                raise UserError("Tender %s: %s" % (rec.name, " ".join(problems)))
            quote = rec.quotation_id
            header = rec._quotation_header()
            if quote:
                if quote.state not in EDITABLE_STATES:
                    raise UserError(
                        "Quotation %s is %s and cannot be re-priced." % (quote.name, quote.state)
                    )
                quote.write({k: v for k, v in header.items() if k != "company_id"})
                quote.line_ids.unlink()
            else:
                header["delivery_terms"] = (
                    "As the tender's price schedule: point of delivery and delivery period "
                    "per BOQ item."
                )
                quote = Quote.create(header)
                rec._guarded().write({"quotation_id": quote.id})
            vat = quote.vat_rate or 0.0
            boq = rec.boq_line_ids.sorted(lambda r: (r.sequence, r.id))
            created = Line.create(
                [
                    {
                        "quotation_id": quote.id,
                        "sequence": (i + 1) * 10,
                        "line_type": "goods" if src.line_kind == "goods" else "service",
                        "product_id": src.product_id.id or False,
                        "description": ("Item %s: %s" % (src.item_no, src.description))[:250],
                        "quantity": src.quantity,
                        "unit_price": src._ex_vat_price(vat),
                    }
                    for i, src in enumerate(boq)
                ]
            )
            for src, line in zip(boq, created, strict=True):
                src.with_context(**{LINKING: True}).write({"quotation_line_id": line.id})
            rec.message_post(
                body="Priced on quotation %s: %d line(s), BDT %.2f excl. VAT, BDT %.2f incl. VAT."
                % (quote.name, len(created), quote.value, quote.amount_total)
            )
        return True

    def _pricing_problems(self) -> list:
        """Why the BOQ is not priced, line for line, on an approved quotation."""
        self.ensure_one()
        quote = self.quotation_id.sudo()
        problems = []
        if quote.state not in ("approved", "sent", "accepted"):
            problems.append(
                "Its pricing quotation %s is %s: the price needs the internal approval first."
                % (quote.name, quote.state)
            )
        vat = quote.vat_rate or 0.0
        linked = self.env["fix.quotation.line"]
        for line in self.boq_line_ids:
            ql = line.quotation_line_id.sudo()
            if (line.unit_price_incl_vat or 0.0) <= 0.0:
                problems.append("BOQ item %s has no price." % line.item_no)
                continue
            if (
                not ql
                or ql.quotation_id != quote
                or abs((ql.quantity or 0.0) - (line.quantity or 0.0)) > 1e-6
                or abs((ql.unit_price or 0.0) - line._ex_vat_price(vat)) > 0.005
                or (ql.discount_pct or 0.0)
            ):
                problems.append(
                    "BOQ item %s is not priced as the BOQ states on quotation %s: re-run "
                    "Price as Quotation." % (line.item_no, quote.name)
                )
                continue
            linked |= ql
        extra = quote._scope_lines() - linked
        if extra:
            problems.append(
                "Quotation %s prices %d line(s) the BOQ does not list." % (quote.name, len(extra))
            )
        if (quote.discount_amount or 0.0) > 0.005:
            problems.append(
                "Quotation %s has an overall discount the price schedule does not show: put "
                "the price into the BOQ unit prices instead." % quote.name
            )
        return problems

    def action_submit(self):
        for rec in self:
            if rec.state != "draft":
                continue  # the base refusal applies
            problems = []
            if rec.tender_type == "public_egp" and not rec.bid_validity_days:
                problems.append("State the tender validity (60-150 days, PPR 2025).")
            if rec.boq_line_ids and not rec.quotation_id:
                problems.append("Price the BOQ as a quotation and have it approved.")
            if rec.quotation_id:
                problems += rec._pricing_problems()
                total = rec.quotation_id.sudo().amount_total or 0.0
                if abs((rec.bid_value or 0.0) - total) > 0.005:
                    problems.append(
                        "The bid price BDT %.2f differs from the quotation total BDT %.2f."
                        % (rec.bid_value or 0.0, total)
                    )
            if problems:
                raise UserError(
                    "Tender %s cannot be submitted: %s" % (rec.name, " ".join(problems))
                )
        return super().action_submit()

    # ---- acceptance certificate -------------------------------------------
    def action_record_acceptance(self):
        """Record the procuring entity's acceptance certificate (staged on
        the form): retention then runs on the accepted value."""
        today = dhaka_today(self)
        for rec in self:
            if rec.state != "won":
                raise UserError(
                    "Only an awarded (won) tender has an acceptance; %s is %s."
                    % (rec.name, rec.state)
                )
            if rec.acceptance_recorded_at:
                raise UserError("Tender %s already has its acceptance recorded." % rec.name)
            problems = []
            if not (rec.teac_certificate_no or "").strip():
                problems.append("Record the acceptance certificate number.")
            if not rec.teac_certificate_date:
                problems.append("Record the acceptance certificate date.")
            elif rec.teac_certificate_date > today or (
                rec.award_date and rec.teac_certificate_date < rec.award_date
            ):
                problems.append("The certificate date must fall between the award and today.")
            value = rec.teac_accepted_value or 0.0
            if value <= 0.0:
                problems.append("Record the accepted value.")
            elif value > (rec.contract_value or 0.0) + 0.005:
                problems.append(
                    "The accepted value BDT %.2f exceeds the contract value BDT %.2f (with "
                    "approved variations)." % (value, rec.contract_value or 0.0)
                )
            if problems:
                raise UserError("Tender %s: %s" % (rec.name, " ".join(problems)))
            rec._guarded().write(
                {
                    "acceptance_recorded_by": self.env.user.id,
                    "acceptance_recorded_at": fields.Datetime.now(),
                }
            )
            rec.message_post(
                body="Acceptance certificate %s of %s recorded: BDT %.2f accepted, retention "
                "%.1f%% = BDT %.2f."
                % (
                    rec.teac_certificate_no,
                    rec.teac_certificate_date,
                    value,
                    rec.retention_pct or 0.0,
                    rec.retention_amount,
                )
            )
        return True


class FixQuotationTenderLock(models.Model):
    """A quotation that prices a lodged bid is the bid: it is frozen, and it
    is never issued to the customer as a quotation (the award, not a
    quotation acceptance, makes the contract; issuing it would let one
    tender become two contracts)."""

    _inherit = "fix.quotation"

    def _tenders_priced(self, lodged_only=False):
        domain = [("quotation_id", "in", self.ids)]
        if lodged_only:
            domain.append(("state", "in", ("submitted", "won")))
        return self.env["fix.tender"].sudo().search(domain) if self.ids else self.env["fix.tender"]

    def write(self, vals):
        if not self._fix_guard_open():
            touched = (QUOTE_TERMS | {"line_ids"}) & set(vals)
            if touched:
                lodged = self._tenders_priced(lodged_only=True)
                if lodged:
                    changed = "line_ids" in touched or any(
                        q._fix_guard_differs(n, vals[n], q[n])
                        for q in self.filtered(lambda r: r in lodged.quotation_id)
                        for n in touched
                    )
                    if changed:
                        raise UserError(
                            "Quotation %s prices the bid lodged on tender %s and cannot change."
                            % (lodged[0].quotation_id.name, lodged[0].name)
                        )
        return super().write(vals)

    def action_send(self):
        tenders = self._tenders_priced()
        if tenders:
            raise UserError(
                "Quotation %s prices tender %s: the bid is lodged by submitting the tender, "
                "and the award creates the contract. It is not issued to the customer."
                % (tenders[0].quotation_id.name, tenders[0].name)
            )
        return super().action_send()


class FixQuotationLineTenderLock(models.Model):
    _inherit = "fix.quotation.line"

    @api.model
    def _assert_editable(self, quotations):
        super()._assert_editable(quotations)
        if quotations:
            lodged = quotations._tenders_priced(lodged_only=True)
            if lodged:
                raise UserError(
                    "Quotation %s prices the bid lodged on tender %s: its lines are frozen."
                    % (lodged[0].quotation_id.name, lodged[0].name)
                )
