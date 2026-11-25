# cd_billing_engine — Customer TDS / AIT certificates received, M20.
#
# Corporate and government customers deduct INCOME TAX at source from what
# they pay 1000 FiX (Income Tax Act 2023: s.89 supply of goods / execution of
# a contract, s.90 services), deposit it with the treasury and hand over a
# certificate of tax deducted. That tax is an advance income tax (AIT) credit
# of the company, claimed in its own return. Until the certificate is
# recorded the invoice shows a residual equal to the tax that will never
# arrive as cash, and corporate invoices age as partly unpaid.
#
# fix.tds.certificate.received is the income-tax analogue of the Mushak 6.6
# VDS certificate (fix_vds_certificate.py), and follows the same controls:
#   draft -> verified (a second person checks it against the original: SoD)
#         -> settled (the tax part of the receivable is cleared:
#                     Dr AIT receivable / Cr AR control)
#   draft | verified -> cancelled.
# State and every stamp are guarded; the certificate is frozen once verified;
# the amount never exceeds what is still open on the invoice.
#
# GL: the AIT receivable account is the role "ait_receivable"
# (cd_billing_engine.account_code.ait_receivable). It has NO default code —
# the chart decides which account carries advance income tax, so settlement
# refuses until finance names it (never a guessed account).
from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

TAX_SECTIONS = [
    ("s89", "s.89 — Supply of goods / execution of contract"),
    ("s90", "s.90 — Services"),
    ("other", "Other section"),
]

PARAM_AIT_ACCOUNT = "cd_billing_engine.account_code.ait_receivable"


class FixTdsCertificateReceived(models.Model):
    """A certificate of income tax deducted at source by a customer."""

    _name = "fix.tds.certificate.received"
    _description = "Customer TDS / AIT Certificate (income tax deducted at source)"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "certificate_date desc, id desc"

    _certificate_unique = models.Constraint(
        "UNIQUE (company_id, customer_id, certificate_no)",
        "This customer's TDS certificate number is already recorded",
    )

    name = fields.Char(string="Reference", default="New", readonly=True, copy=False, index=True)
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit", index=True)
    invoice_id = fields.Many2one(
        "fix.ar.invoice",
        string="Invoice (Mushak 6.3)",
        required=True,
        index=True,
        ondelete="restrict",
        tracking=True,
        domain="[('state', '=', 'issued'), ('company_id', '=', company_id)]",
    )
    customer_id = fields.Many2one(
        related="invoice_id.customer_id", store=True, index=True, string="Customer"
    )
    currency_id = fields.Many2one(related="invoice_id.currency_id")
    invoice_total = fields.Monetary(
        related="invoice_id.total_payable", string="Invoice Total", currency_field="currency_id"
    )
    invoice_residual = fields.Monetary(
        related="invoice_id.amount_residual",
        string="Invoice Open Residual",
        currency_field="currency_id",
    )
    customer_tin = fields.Char(
        string="Deductor e-TIN",
        help="The customer's 12-digit e-TIN as printed on the certificate",
    )
    certificate_no = fields.Char(string="Certificate No", required=True, tracking=True)
    certificate_date = fields.Date(string="Certificate Date", required=True, tracking=True)
    tax_section = fields.Selection(
        TAX_SECTIONS,
        string="Deducted Under",
        required=True,
        default="s90",
        tracking=True,
        help="Income Tax Act 2023 section the customer deducted under",
    )
    tds_amount = fields.Monetary(
        string="Tax Deducted (BDT)", currency_field="currency_id", required=True, tracking=True
    )
    challan_no = fields.Char(string="Treasury Challan No")
    challan_date = fields.Date(string="Challan Date")
    note = fields.Text(string="Notes")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("verified", "Verified"),
            ("settled", "Settled against Receivable"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        required=True,
        tracking=True,
        index=True,
    )
    prepared_by_id = fields.Many2one(
        "res.users", string="Prepared By", default=lambda self: self.env.user, readonly=True
    )
    verified_by_id = fields.Many2one("res.users", string="Verified By", readonly=True, copy=False)
    verified_at = fields.Datetime(string="Verified On", readonly=True, copy=False)
    settled_move_id = fields.Many2one(
        "account.move", string="Settlement GL Move", readonly=True, copy=False
    )
    settled_at = fields.Datetime(string="Settled On", readonly=True, copy=False)

    TDS_GUARDED = {
        "state",
        "prepared_by_id",
        "verified_by_id",
        "verified_at",
        "settled_move_id",
        "settled_at",
    }
    # Frozen once a second person has verified the certificate.
    TDS_LOCKED = (
        "invoice_id",
        "tds_amount",
        "certificate_no",
        "certificate_date",
        "tax_section",
        "company_id",
        "customer_tin",
        "challan_no",
        "challan_date",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | self.TDS_GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "draft" for r in self):
            locked |= set(self.TDS_LOCKED)
        return locked

    # ------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            invoice = self.env["fix.ar.invoice"].browse(vals.get("invoice_id"))
            if invoice:
                vals.setdefault("company_id", invoice.company_id.id)
                vals.setdefault("operating_unit_id", invoice.operating_unit_id.id)
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.tds.certificate.received")
                    or "TDS/New"
                )
        return super().create(vals_list)

    def _pending_on_invoice(self) -> float:
        """TDS recorded on this certificate's invoice and not yet settled
        (this certificate included): what the open residual must cover."""
        self.ensure_one()
        pending = self.invoice_id.tds_certificate_ids.filtered(
            lambda c: c.state in ("draft", "verified")
        )
        return sum(pending.mapped("tds_amount"))

    @api.constrains("tds_amount", "invoice_id", "state")
    def _check_certificate(self):
        for cert in self:
            if cert.tds_amount <= 0:
                raise ValidationError("The tax deducted must be positive")
            if cert.state not in ("draft", "verified"):
                continue
            residual = cert.invoice_id.amount_residual
            pending = cert._pending_on_invoice()
            if pending > residual + 0.005:
                raise ValidationError(
                    "TDS recorded on invoice %s (%s, this certificate included) would exceed its "
                    "open residual (%s): tax deducted at source clears only what the customer "
                    "still owes." % (cert.invoice_id.name, round(pending, 2), round(residual, 2))
                )

    def write(self, vals):
        if not self._fix_guard_open() and set(self.TDS_LOCKED) & set(vals):
            for cert in self:
                if cert.state != "draft":
                    raise UserError(
                        "Certificate %s is %s — its amount, invoice, number and section are "
                        "locked once verified (cancel it and record it again)"
                        % (cert.name, cert.state)
                    )
        return super().write(vals)

    # ------------------------------------------------------------------
    def action_verify(self):
        """Checker step: a second person confirms the certificate against
        the original (segregation of duties — the preparer cannot verify)."""
        for cert in self:
            if cert.state != "draft":
                raise UserError("Only draft certificates can be verified")
            if self.env.user in (cert.prepared_by_id | cert.create_uid):
                raise AccessError(
                    "Segregation of duties: %s prepared certificate %s and cannot verify it"
                    % (self.env.user.name, cert.name)
                )
            cert._guarded().write(
                {
                    "state": "verified",
                    "verified_by_id": self.env.user.id,
                    "verified_at": fields.Datetime.now(),
                }
            )

    @api.model
    def _ait_account(self, company):
        """The AIT receivable account, or a refusal naming the parameter."""
        from .fix_ar_engine import _ar_account

        account = _ar_account(self.env, company, "ait_receivable")
        if not account:
            code = self.env["ir.config_parameter"].sudo().get_param(PARAM_AIT_ACCOUNT)
            raise UserError(
                "Settle refused: no advance income tax (AIT) receivable account for %s. "
                "Set the system parameter %s to the code of the chart account that carries "
                "income tax deducted at source by customers%s. Refusing rather than guessing "
                "an account."
                % (
                    company.name,
                    PARAM_AIT_ACCOUNT,
                    " (the configured code %r is not in this company's chart)" % code
                    if code
                    else "",
                )
            )
        return account

    def action_settle(self):
        """Clear the tax part of the receivable: Dr AIT receivable / Cr AR
        (the customer's control line). Refuses — never skips — when an
        account or the journal is missing. A fully covered invoice is closed
        as paid with the certificate as evidence."""
        from .fix_ar_engine import _ar_account

        for cert in self:
            if cert.state != "verified":
                raise UserError("Verify certificate %s before settling it" % cert.name)
            invoice = cert.invoice_id
            if invoice.state != "issued":
                raise UserError(
                    "Invoice %s is %s — TDS can only settle an open (issued) receivable"
                    % (invoice.name, invoice.state)
                )
            if cert.tds_amount > invoice.amount_residual + 0.005:
                raise UserError(
                    "TDS %s exceeds the open residual %s of invoice %s"
                    % (cert.tds_amount, invoice.amount_residual, invoice.name)
                )
            company = invoice.company_id
            ait_acc = cert._ait_account(company)
            ar_acc = _ar_account(cert.env, company, "ar")
            if not ar_acc:
                raise UserError(
                    "Settle refused: no AR control account for %s "
                    "(cd_billing_engine.account_code.ar)" % company.name
                )
            move = invoice._post_reversal_gl(
                "TDS %s (%s) — INV %s" % (cert.certificate_no, cert.tax_section, invoice.name),
                [("ait_receivable", ait_acc, cert.tds_amount, invoice.customer_id.id)],
                [("ar", ar_acc, cert.tds_amount, invoice.customer_id.id)],
            )
            cert._guarded().write(
                {
                    "state": "settled",
                    "settled_move_id": move.id,
                    "settled_at": fields.Datetime.now(),
                }
            )
            if invoice.amount_residual <= 0.005:
                invoice._mark_paid()

    def action_cancel(self):
        for cert in self:
            if cert.state not in ("draft", "verified"):
                raise UserError(
                    "Certificate %s is %s — a settled certificate is reversed by finance "
                    "through a GL correction, not cancelled" % (cert.name, cert.state)
                )
            cert._guarded().write({"state": "cancelled"})
