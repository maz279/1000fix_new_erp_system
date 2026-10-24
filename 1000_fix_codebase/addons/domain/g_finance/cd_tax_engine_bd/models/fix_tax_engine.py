# cd_tax_engine_bd — M51-core VAT determination & Mushak 6.3 (P06-M02, MV-03).
#
# Register names the modules CD-M51-01..05 at W4; MV-03 moved determination
# and Mushak issuance INTO W3 (roadmap P06-M02). This module is that W3
# slice: determination + TDS (tax_logic.py, pure) + the event-driven Mushak
# register + the statutory QWeb invoice. VAT RETURNS and filing stay W4
# (roadmap backlog entry).
#
# Call direction (AR-006 section 4.1): M20 and M52 CALL this module's
# determination synchronously; NOTHING calls M20 back — the register is
# populated by CONSUMING invoice.created events (T04), so M51 can rebuild
# the VAT register from the event stream without M20's cooperation.
from decimal import Decimal
from typing import Any

from odoo import api, fields, models
from odoo.exceptions import ValidationError

from libs.py.fix_events import publish  # FF-28

from . import tax_logic


class FixVatTreatment(models.Model):
    """A tariff-backed treatment row: product/HS code -> treatment + rate.

    Data source: M30's country pack (fix.country.pack), NOT M65 (T06 —
    closes the +5-wave dependency violation). Rows here are the cached
    projection the pack publishes."""

    _name = "fix.vat.treatment"
    _description = "VAT Treatment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _code_unique = models.Constraint("UNIQUE (code)", "VAT treatment code must be unique")

    code = fields.Char(string="Tariff Code", required=True)
    name = fields.Char(string="Treatment", required=True)
    treatment_type = fields.Selection(
        [(t, t) for t in tax_logic.VALID_TREATMENTS],
        string="Treatment Type",
        required=True,
        default="standard_15",
    )
    rate = fields.Float(
        string="Rate (%)",
        default=15.0,
        help="AS-10 does not apply to rates — a percentage, not money",
    )
    truncated_base = fields.Float(
        string="Truncated Fixed Base",
        help="For truncated treatments: the fixed VAT base amount per period",
    )
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    active = fields.Boolean(default=True)

    @api.constrains("treatment_type", "rate", "truncated_base")
    def _check_treatment(self) -> None:
        for row in self:
            rate = Decimal(str(row.rate))
            if row.treatment_type == "standard_15" and rate != tax_logic.STANDARD_RATE:
                raise ValidationError("standard_15 must carry the 15% rate")
            # the determination engine refuses an unscheduled reduced rate —
            # the tariff row must not be able to hold one either
            if row.treatment_type == "reduced" and rate not in tax_logic.REDUCED_RATES:
                raise ValidationError(
                    f"reduced rate {row.rate:g}% is not a scheduled rate (5 / 7.5 / 10)"
                )
            if row.treatment_type in ("zero_rated", "exempt", "truncated") and rate != 0:
                raise ValidationError(f"{row.treatment_type} carries no ad-valorem rate")
            if row.treatment_type == "truncated" and row.truncated_base <= 0:
                raise ValidationError("truncated treatments need a positive fixed base")


class FixMushakRegister(models.Model):
    """The VAT register — one row per Mushak 6.3 issued (T04).

    POPULATED BY CONSUMING invoice.created — never by calling M20 back
    (AR-006 section 4.1 pair 7). The register write is ATOMIC with the GL
    posting in the billing engine (T08): same transaction, or neither."""

    _name = "fix.mushak.register"
    _description = "Mushak 6.3 VAT Register"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "invoice_date desc, id desc"
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _mushak_no_company_unique = models.Constraint(
        "UNIQUE (mushak_no, company_id)", "Mushak number already used in this company"
    )

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    mushak_no = fields.Char(
        string="Mushak 6.3 No.", required=True, index=True, copy=False, readonly=True
    )
    invoice_ref = fields.Char(
        string="Invoice Reference",
        required=True,
        index=True,
        help="The invoice.created event's source reference",
    )
    invoice_date = fields.Date(string="Invoice Date", required=True)
    # Supplier identity (statutory content of the form)
    supplier_name = fields.Char(required=True)
    supplier_bin = fields.Char(
        string="Supplier BIN",
        required=True,
        size=13,
        help="Business Identification Number — 13 digits",
    )
    customer_name = fields.Char(required=True)
    customer_bin = fields.Char(
        string="Customer BIN", size=13, help="Buyer BIN where the buyer is registered"
    )
    currency_id = fields.Many2one(
        "res.currency", required=True, default=lambda self: self.env.ref("base.BDT")
    )
    taxable_amount = fields.Monetary(
        string="Taxable Value", currency_field="currency_id", required=True
    )
    vat_amount = fields.Monetary(string="VAT", currency_field="currency_id", required=True)
    total_payable = fields.Monetary(
        string="Total Payable", currency_field="currency_id", required=True
    )
    treatment_summary = fields.Text(
        readonly=True, help="Per-line treatments, from the determination"
    )
    source_event_id = fields.Char(
        string="Source Event",
        index=True,
        readonly=True,
        help="invoice.created event_id — replay key",
    )
    posted = fields.Boolean(
        default=False, readonly=True, help="True once the GL posting committed (atomic pair)"
    )

    @api.constrains("supplier_bin", "customer_bin")
    def _check_bins(self) -> None:
        import re

        for row in self:
            if not re.fullmatch(r"\d{13}", row.supplier_bin or ""):
                raise ValidationError("Supplier BIN must be exactly 13 digits")
            if row.customer_bin and not re.fullmatch(r"\d{13}", row.customer_bin or ""):
                raise ValidationError("Customer BIN must be 13 digits when present")

    @api.model
    def consume_invoice_created(self, event: dict[str, Any]) -> "FixMushakRegister":
        """T04 consumer: create the register row from an invoice.created
        event. Idempotent on source_event_id (DI-05) — a replayed event
        updates nothing."""
        payload = event.get("payload", {})
        event_id = event.get("event_id")
        if not event_id:
            # searching source_event_id = False would match every row the
            # billing engine wrote directly and silently drop the event
            raise ValidationError("invoice.created event without event_id cannot be consumed")
        existing: FixMushakRegister = self.search([("source_event_id", "=", event_id)])
        if existing:
            return existing
        # The billing engine writes the row in the SAME transaction as the
        # event (T08); a rebuild/replay meets that row by its Mushak number.
        # Adopt it instead of colliding with the (mushak_no, company) key.
        same_number: FixMushakRegister = self.search(
            [("mushak_no", "=", payload["mushak_no"]), ("company_id", "=", self.env.company.id)],
            limit=1,
        )
        if same_number:
            if not same_number.source_event_id:
                same_number.source_event_id = event_id
            return same_number
        created: FixMushakRegister = self.create(
            {
                "mushak_no": payload["mushak_no"],
                "invoice_ref": payload["invoice_ref"],
                "invoice_date": payload["invoice_date"],
                "supplier_name": payload["supplier_name"],
                "supplier_bin": payload["supplier_bin"],
                "customer_name": payload["customer_name"],
                "customer_bin": payload.get("customer_bin", ""),
                "taxable_amount": payload["taxable_amount"],
                "vat_amount": payload["vat_amount"],
                "total_payable": payload["total_payable"],
                "treatment_summary": payload.get("treatment_summary", ""),
                "source_event_id": event_id,
                "operating_unit_id": payload.get("operating_unit_id"),
            }
        )
        return created

    def action_mark_posted(self) -> None:
        """T08: called in the SAME transaction as the GL posting by the
        billing engine — invoice-to-GL atomic with the register write."""
        self.write({"posted": True})
        for row in self:
            publish(
                self.env,
                "mushak.registered",
                "fix.mushak.register",
                row.id,
                {
                    "mushak_no": row.mushak_no,
                    "vat_amount": row.vat_amount,
                    "invoice_date": str(row.invoice_date),
                },
            )

    def action_rebuild_from_events(self, from_timestamp: str | None = None) -> int:
        """T04 proof: the register rebuilds from the event stream alone —
        without M20's cooperation. Consumes replayed invoice.created."""
        from libs.py.fix_events import replay_from_timestamp

        count = 0
        for event in replay_from_timestamp(
            self.env, from_timestamp or "1970-01-01", event_type="invoice.created"
        ):
            self.consume_invoice_created(event)
            count += 1
        return count
