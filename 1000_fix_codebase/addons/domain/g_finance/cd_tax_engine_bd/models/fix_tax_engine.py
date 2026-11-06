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
#
# A08 workflow audit (2026-11-04):
#   M51-2  an accountant edited the VAT of an issued Mushak 6.3 (3,000 -> 0,
#          the 9.1 followed), typed register rows with BIN 0000000000000 and
#          flagged rows "posted" with no GL entry. The register is now written
#          only by the issuing services below (billing engine, native invoice
#          posting, the invoice.created consumer); an issued row is never
#          edited — a correction is a Mushak 6.7 / 6.8 note row; `posted`
#          needs the posted GL entry.
#   M51-5  sales VAT came from a constant (15%) whatever the master said;
#          fix.vat.treatment was read by nothing. _fix_determine_tax() reads
#          the effective-dated master and the tariff treatment.
#   M51-9  posted native account.move sales invoices never reached the
#          register: _fix_register_from_invoice(move) registers them, and the
#          9.1 preparation sweeps the period's posted invoices through it.
import re
from decimal import Decimal
from typing import Any

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from libs.py.fix_events import publish  # FF-28

from . import tax_logic

BIN_RE = re.compile(r"^\d{13}$")
FINANCE_GROUPS = (
    "account.group_account_invoice",
    "account.group_account_user",
    "account.group_account_manager",
)
NATIVE_MUSHAK_SEQUENCE = "cd_tax_engine_bd.mushak_native"


def valid_bin(value) -> bool:
    """A real 13-digit BIN: digits only, never all one digit (0000000000000
    is the placeholder the seed rows carried, not a registration)."""
    value = (value or "").strip()
    return bool(BIN_RE.match(value)) and len(set(value)) > 1


class FixVatTreatment(models.Model):
    """A tariff-backed treatment row: product/HS code -> treatment + rate.

    Data source: M30's country pack (fix.country.pack), NOT M65 (T06 —
    closes the +5-wave dependency violation). Rows here are the cached
    projection the pack publishes. A08 M51-5/M51-6: the determination reads
    the ACTIVE row of a code; a change is a proposal a second manager
    activates (fix.tax.master.approval.mixin)."""

    _name = "fix.vat.treatment"
    _description = "VAT Treatment"
    _inherit = ["fix.tax.master.approval.mixin", "mail.thread", "mail.activity.mixin"]

    code = fields.Char(string="Tariff Code", required=True, index=True)
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
        help="Reduced treatments: the scheduled rate. A standard treatment carries the "
        "standard rate in force in the Tax Rate Master, which is what the determination uses.",
    )
    truncated_base = fields.Float(
        string="Truncated Fixed Base",
        help="For truncated treatments: the fixed VAT base amount per period",
    )
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    active = fields.Boolean(default=True)

    def _fix_master_key_domain(self):
        return [("company_id", "=", self.company_id.id), ("code", "=", self.code)]

    @api.constrains("code", "company_id", "state")
    def _check_code_unique(self):
        for row in self.filtered(lambda r: r.state == "active"):
            if self.search_count(
                [*row._fix_master_key_domain(), ("state", "=", "active"), ("id", "!=", row.id)]
            ):
                raise ValidationError("VAT treatment code %s already has an active row" % row.code)

    @api.constrains("treatment_type", "rate", "truncated_base")
    def _check_treatment(self) -> None:
        Rate = self.env["fix.tax.rate"]
        for row in self:
            rate = Decimal(str(row.rate))
            rates = Rate._fix_vat_rates(fields.Date.context_today(row), row.company_id)
            if row.treatment_type == "standard_15" and rate != rates.standard:
                raise ValidationError(
                    "A standard treatment carries the standard rate in force (%s%%)"
                    % rates.standard
                )
            # the determination refuses an unscheduled reduced rate — the
            # tariff row must not be able to hold one either
            if row.treatment_type == "reduced" and rate not in rates.reduced:
                raise ValidationError(
                    "reduced rate %g%% is not a scheduled rate in the Tax Rate Master (%s)"
                    % (row.rate, " / ".join("%g" % r for r in sorted(rates.reduced)) or "none")
                )
            if row.treatment_type in ("zero_rated", "exempt", "truncated") and rate != 0:
                raise ValidationError(f"{row.treatment_type} carries no ad-valorem rate")
            if row.treatment_type == "truncated" and row.truncated_base <= 0:
                raise ValidationError("truncated treatments need a positive fixed base")

    @api.model
    def _fix_treatment_for(self, code, company):
        if not code:
            return self.browse()
        return self.sudo().search(
            [
                ("code", "=", code),
                ("state", "=", "active"),
                ("active", "=", True),
                ("company_id", "=", company.id),
            ],
            limit=1,
        )

    @api.model
    def _fix_determine_tax(self, lines, on_date=None, company=None):
        """THE sales VAT determination (A08 M51-5): the effective-dated Tax
        Rate Master gives the standard and reduced rates in force on the
        supply date, and an active tariff row (by HS code, else product code)
        gives a line its treatment. M20 (billing), subscriptions and rentals
        call this instead of tax_logic.determine_tax(lines)."""
        company = company or self.env.company
        on_date = on_date or fields.Date.context_today(self)
        rates = self.env["fix.tax.rate"]._fix_vat_rates(on_date, company)
        determined = []
        for line in lines:
            if not line.treatment:
                row = self._fix_treatment_for(line.hs_code, company) or self._fix_treatment_for(
                    line.product_code, company
                )
                if row:
                    line = tax_logic.TaxLine(
                        product_code=line.product_code,
                        qty=line.qty,
                        unit_price=line.unit_price,
                        discount=line.discount,
                        hs_code=line.hs_code,
                        treatment=row.treatment_type,
                        rate_override=(
                            Decimal(str(row.rate)) if row.treatment_type == "reduced" else None
                        ),
                    )
            determined.append(line)
        return tax_logic.determine_tax(determined, rates)


class FixMushakRegister(models.Model):
    """The VAT register — one row per Mushak 6.3 issued (T04), plus the
    Mushak 6.7 (credit) and 6.8 (debit) note rows that correct it.

    POPULATED BY CONSUMING invoice.created — never by calling M20 back
    (AR-006 section 4.1 pair 7). The register write is ATOMIC with the GL
    posting in the billing engine (T08): same transaction, or neither."""

    _name = "fix.mushak.register"
    _description = "Mushak 6.3 VAT Register"
    _inherit = ["fix.guarded.mixin", "mail.thread", "mail.activity.mixin"]
    _order = "invoice_date desc, id desc"
    # Odoo 19 dropped the legacy constraint tuple list;
    # models.Constraint attributes (migrated by tooling/scripts/migrate-sql-constraints.py)
    _mushak_no_company_unique = models.Constraint(
        "UNIQUE (mushak_no, company_id)", "Mushak number already used in this company"
    )
    _source_move_unique = models.Constraint(
        "UNIQUE (source_move_id)", "This invoice is already in the Mushak register"
    )

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    row_type = fields.Selection(
        [
            ("invoice", "Mushak 6.3 (tax invoice)"),
            ("credit_note", "Mushak 6.7 (credit note)"),
            ("debit_note", "Mushak 6.8 (debit note)"),
        ],
        string="Form",
        required=True,
        default="invoice",
        index=True,
    )
    original_id = fields.Many2one(
        "fix.mushak.register",
        string="Original Mushak 6.3",
        index=True,
        ondelete="restrict",
        help="The issued 6.3 a credit / debit note corrects",
    )
    reason = fields.Char(string="Note Reason")
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
    source_move_id = fields.Many2one(
        "account.move",
        string="Source Invoice (native)",
        readonly=True,
        copy=False,
        index=True,
        ondelete="restrict",
        help="The posted account.move sales invoice / credit note this row registers",
    )
    move_id = fields.Many2one(
        "account.move",
        string="GL Entry",
        readonly=True,
        copy=False,
        help="The posted journal entry of the supply (the `posted` flag needs it)",
    )
    posted = fields.Boolean(
        default=False, readonly=True, help="True once the GL posting committed (atomic pair)"
    )

    # ---------------------------------------------------------------- guard --
    def _fix_guarded_fields(self) -> set:
        # every stored business field: an issued row is evidence
        return super()._fix_guarded_fields() | {
            n
            for n, f in self._fields.items()
            if f.store
            and f.type not in ("one2many", "many2many")
            and not n.startswith(("message_", "activity_"))
            and n not in ("id", "create_uid", "create_date", "write_uid", "write_date")
        }

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            raise UserError(
                "Mushak register rows are issued by the invoicing services (the billing "
                "engine, a posted sales invoice, the invoice.created consumer), never typed. "
                "A correction is a Mushak 6.7 / 6.8 note against the issued row."
            )
        return super().create(vals_list)

    def write(self, vals):
        if vals.get("posted") and not vals.get("move_id"):
            # T08 / A08 M51-2: `posted` means the GL entry exists — even for
            # trusted code. The billing engine's posting is found from its invoice.
            for row in self:
                move = row._fix_resolve_gl_move()
                if not move:
                    raise UserError(
                        "Mushak %s cannot be marked posted: no posted GL entry carries its "
                        "supply." % row.mushak_no
                    )
                super(FixMushakRegister, row).write(dict(vals, move_id=move.id))
            return True
        return super().write(vals)

    @api.ondelete(at_uninstall=False)
    def _unlink_never(self):
        if not self.env.su:
            raise UserError("An issued Mushak register row is never deleted.")

    # ---------------------------------------------------------- constraints --
    @api.constrains("supplier_bin", "customer_bin")
    def _check_bins(self) -> None:
        for row in self:
            if not valid_bin(row.supplier_bin):
                raise ValidationError(
                    "Supplier BIN must be a real 13-digit BIN (not %r)" % (row.supplier_bin or "")
                )
            if row.customer_bin and not valid_bin(row.customer_bin):
                raise ValidationError("Customer BIN must be a real 13-digit BIN when present")

    @api.constrains("row_type", "taxable_amount", "vat_amount", "original_id")
    def _check_note(self):
        for row in self:
            if row.row_type == "credit_note":
                if row.taxable_amount > 0.005 or row.vat_amount > 0.005:
                    raise ValidationError("A Mushak 6.7 credit note carries negative amounts")
            elif row.taxable_amount < -0.005 or row.vat_amount < -0.005:
                raise ValidationError("A Mushak 6.3 / 6.8 row carries non-negative amounts")
            if row.row_type == "invoice" and row.original_id:
                raise ValidationError("A Mushak 6.3 corrects nothing")
            if row.original_id and row.original_id.row_type != "invoice":
                raise ValidationError("A note corrects an issued Mushak 6.3, not another note")

    # ---------------------------------------------------------- services ----
    @api.model
    def _fix_issue_register_row(self, vals):
        """The ONE way the issuing services write a register row (billing
        engine, subscriptions, rentals): validated like any row, written as
        the system. Returns the row in the caller's environment."""
        row = self.sudo().create(dict(vals))
        return self.browse(row.id)

    @api.model
    def _fix_issue_note(self, original, kind, taxable, vat, reason, ref=None, on_date=None):
        """A Mushak 6.7 (kind 'credit_note', amounts reduce) or 6.8 ('debit_note')
        against an issued 6.3 — the only correction of a register row."""
        if kind not in ("credit_note", "debit_note"):
            raise UserError("A register correction is a credit (6.7) or debit (6.8) note")
        if not (reason or "").strip():
            raise UserError("State why the Mushak 6.3 is corrected")
        original = original.sudo()
        if original.row_type != "invoice":
            raise UserError("A note corrects an issued Mushak 6.3")
        sign = -1 if kind == "credit_note" else 1
        taxable, vat = sign * abs(taxable or 0.0), sign * abs(vat or 0.0)
        company = original.company_id
        on_date = on_date or fields.Date.context_today(self)
        return self._fix_issue_register_row(
            {
                "company_id": company.id,
                "operating_unit_id": original.operating_unit_id.id,
                "row_type": kind,
                "original_id": original.id,
                "reason": reason.strip(),
                "mushak_no": self._fix_next_native_mushak_no(company, on_date),
                "invoice_ref": ref or "%s/%s" % (kind.upper(), original.mushak_no),
                "invoice_date": on_date,
                "supplier_name": original.supplier_name,
                "supplier_bin": original.supplier_bin,
                "customer_name": original.customer_name,
                "customer_bin": original.customer_bin or False,
                "currency_id": original.currency_id.id,
                "taxable_amount": taxable,
                "vat_amount": vat,
                "total_payable": taxable + vat,
                "treatment_summary": original.treatment_summary or "",
            }
        )

    @api.model
    def _fix_next_native_mushak_no(self, company, on_date=None):
        """The company's Mushak serial: the billing engine's per-company
        fiscal-year sequence when M20 is installed, else this module's."""
        on_date = on_date or fields.Date.context_today(self)
        if "fix.ar.invoice" in self.env and hasattr(self.env["fix.ar.invoice"], "_next_mushak_no"):
            return self.env["fix.ar.invoice"].sudo()._next_mushak_no(company, on_date)
        number = self.env["ir.sequence"].sudo().next_by_code(NATIVE_MUSHAK_SEQUENCE, on_date)
        if not number:
            raise UserError("The Mushak numbering sequence is missing — upgrade cd_tax_engine_bd.")
        return number

    @api.model
    def _fix_company_bin(self, company):
        bin_no = (company.vat or "").replace(" ", "")
        if not valid_bin(bin_no):
            raise UserError(
                "Company %s has no valid 13-digit BIN — a Mushak 6.3 cannot be issued "
                "without the supplier BIN" % company.name
            )
        return bin_no

    @api.model
    def _fix_treatment_summary(self, move):
        """Per-line '<code>: <treatment> @ <rate>%' from the invoice's taxes,
        read against the master; a line whose rate identifies no treatment is
        left out, so the 9.1 flags the row as unclassified (never guessed)."""
        rates = self.env["fix.tax.rate"]._fix_vat_rates(
            move.invoice_date or move.date, move.company_id
        )
        out = []
        for line in move.invoice_line_ids.filtered(lambda ln: ln.display_type == "product"):
            pct = sum(t.amount for t in line.tax_ids if t.amount_type == "percent")
            code = line.product_id.default_code or "LINE%s" % line.id
            if Decimal(str(pct)) == rates.standard:
                out.append("%s: standard_15 @ %g%%" % (code, pct))
            elif Decimal(str(pct)) in rates.reduced:
                out.append("%s: reduced @ %g%%" % (code, pct))
        return "\n".join(out)

    @api.model
    def _fix_register_from_invoice(self, move):
        """CONTRACT (B5 -> B4, A08 M51-9): register a POSTED native sales
        invoice (out_invoice -> Mushak 6.3) or credit note (out_refund ->
        Mushak 6.7) in the VAT register. Idempotent per move. Returns the row."""
        move.ensure_one()
        move = move.sudo()
        if move.move_type not in ("out_invoice", "out_refund"):
            raise UserError("%s is not a sales invoice or credit note" % move.display_name)
        if move.state != "posted":
            raise UserError("%s is not posted — only a posted invoice is registered" % move.name)
        existing = self.sudo().search([("source_move_id", "=", move.id)], limit=1)
        if existing:
            return self.browse(existing.id)
        company = move.company_id
        partner = move.partner_id.commercial_partner_id
        customer_bin = (partner.vat or "").replace(" ", "")
        refund = move.move_type == "out_refund"
        original = self.browse()
        if refund and move.reversed_entry_id:
            original = self.sudo().search(
                [("source_move_id", "=", move.reversed_entry_id.id), ("row_type", "=", "invoice")],
                limit=1,
            )
        ou = move["operating_unit_id"] if "operating_unit_id" in move._fields else False
        ou = ou or self.env["operating.unit"].sudo().search(
            [("company_id", "=", company.id)], limit=1
        )
        if not ou:
            raise UserError("Company %s has no operating unit for its register" % company.name)
        on_date = move.invoice_date or move.date
        return self._fix_issue_register_row(
            {
                "company_id": company.id,
                "operating_unit_id": ou.id,
                "row_type": "credit_note" if refund else "invoice",
                "original_id": original.id or False,
                "reason": ("Credit note %s" % move.name) if refund else False,
                "mushak_no": self._fix_next_native_mushak_no(company, on_date),
                "invoice_ref": move.name,
                "invoice_date": on_date,
                "supplier_name": company.name,
                "supplier_bin": self._fix_company_bin(company),
                "customer_name": partner.name or move.partner_id.display_name or "-",
                "customer_bin": customer_bin if valid_bin(customer_bin) else False,
                "currency_id": company.currency_id.id,
                "taxable_amount": move.amount_untaxed_signed,
                "vat_amount": move.amount_tax_signed,
                "total_payable": move.amount_total_signed,
                "treatment_summary": self._fix_treatment_summary(move),
                "source_move_id": move.id,
                "move_id": move.id,
                "posted": True,
            }
        )

    @api.model
    def _fix_register_period_invoices(self, company, date_from, date_before):
        """Register every posted native sales invoice / credit note of the
        period not yet in the register (the 9.1 preparation calls this)."""
        moves = (
            self.env["account.move"]
            .sudo()
            .search(
                [
                    ("company_id", "=", company.id),
                    ("move_type", "in", ("out_invoice", "out_refund")),
                    ("state", "=", "posted"),
                    ("invoice_date", ">=", date_from),
                    ("invoice_date", "<", date_before),
                ],
                order="invoice_date, id",
            )
        )
        done = set(
            self.sudo().search([("source_move_id", "in", moves.ids)]).mapped("source_move_id").ids
        )
        rows = self.browse()
        for move in moves.filtered(lambda m: m.id not in done):
            rows |= self._fix_register_from_invoice(move)
        return rows

    def _fix_resolve_gl_move(self):
        """The posted GL entry of the row's supply: its own, the native
        invoice, or the billing engine's posting of the AR invoice."""
        self.ensure_one()
        row = self.sudo()
        for move in (row.move_id, row.source_move_id):
            if move and move.state == "posted":
                return move
        if "fix.ar.invoice" in self.env:
            Invoice = self.env["fix.ar.invoice"].sudo()
            if "mushak_id" in Invoice._fields and "posted_move_id" in Invoice._fields:
                inv = Invoice.search([("mushak_id", "=", row.id)], limit=1)
                if inv.posted_move_id and inv.posted_move_id.state == "posted":
                    return inv.posted_move_id
        return self.env["account.move"]

    def _fix_mark_posted(self, move):
        """T08: the GL posting of the supply committed — mark the row posted
        and publish its registration. The move must be posted."""
        for row in self:
            if not move or move.state != "posted":
                raise UserError("Mushak %s: the GL entry is not posted" % row.mushak_no)
            row.sudo().write({"posted": True, "move_id": move.id})
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
        return True

    def action_mark_posted(self) -> None:
        """Mark a row posted ONLY when its supply's posted GL entry is found
        (A08 M51-2/M04: no flag without a ledger consequence)."""
        if not self.env.su and not any(self.env.user.has_group(g) for g in FINANCE_GROUPS):
            raise UserError("Marking a Mushak row posted needs a finance role.")
        for row in self:
            move = row._fix_resolve_gl_move()
            if not move:
                raise UserError(
                    "Mushak %s has no posted GL entry: it is marked posted by the invoice "
                    "posting itself, never by hand." % row.mushak_no
                )
            row._fix_mark_posted(move)

    @api.model
    def consume_invoice_created(self, event: dict[str, Any]) -> "FixMushakRegister":
        """T04 consumer: create the register row from an invoice.created
        event. Idempotent on source_event_id (DI-05) — a replayed event
        updates nothing. The relay runs it as the system."""
        Register = self.sudo()
        payload = event.get("payload", {})
        event_id = event.get("event_id")
        if not event_id:
            # searching source_event_id = False would match every row the
            # billing engine wrote directly and silently drop the event
            raise ValidationError("invoice.created event without event_id cannot be consumed")
        existing = Register.search([("source_event_id", "=", event_id)])
        if existing:
            return existing
        # The billing engine writes the row in the SAME transaction as the
        # event (T08); a rebuild/replay meets that row by its Mushak number.
        # Adopt it instead of colliding with the (mushak_no, company) key.
        same_number = Register.search(
            [("mushak_no", "=", payload["mushak_no"]), ("company_id", "=", self.env.company.id)],
            limit=1,
        )
        if same_number:
            if not same_number.source_event_id:
                same_number.source_event_id = event_id
            return same_number
        return Register.create(
            {
                "mushak_no": payload["mushak_no"],
                "invoice_ref": payload["invoice_ref"],
                "invoice_date": payload["invoice_date"],
                "supplier_name": payload["supplier_name"],
                "supplier_bin": payload["supplier_bin"],
                "customer_name": payload["customer_name"],
                "customer_bin": payload.get("customer_bin") or False,
                "taxable_amount": payload["taxable_amount"],
                "vat_amount": payload["vat_amount"],
                "total_payable": payload["total_payable"],
                "treatment_summary": payload.get("treatment_summary", ""),
                "source_event_id": event_id,
                "operating_unit_id": payload.get("operating_unit_id"),
            }
        )

    def action_rebuild_from_events(self, from_timestamp: str | None = None) -> int:
        """T04 proof: the register rebuilds from the event stream alone —
        without M20's cooperation. Consumes replayed invoice.created. An
        engine operation for accounting managers, not a workspace button."""
        if not self.env.su and not self.env.user.has_group("account.group_account_manager"):
            raise UserError(
                "Rebuilding the Mushak register needs the Accounting Administrator role."
            )
        from libs.py.fix_events import replay_from_timestamp

        count = 0
        for event in replay_from_timestamp(
            self.env, from_timestamp or "1970-01-01", event_type="invoice.created"
        ):
            self.consume_invoice_created(event)
            count += 1
        return count
