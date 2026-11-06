# cd_billing_engine — Customer VDS certificates (Mushak 6.6 received), M20.
#
# Corporate and government customers are VAT withholding entities: they pay
# 1000 FiX the invoice LESS the VAT they deduct at source (VDS), deposit it
# with the treasury and hand over a Mushak 6.6 certificate. Until that
# certificate is recorded the invoice shows a residual equal to the VDS that
# will never arrive as cash.
#
# fix.vds.certificate.received records each certificate against the invoice:
#   draft -> verified (a second person checks it: SoD) -> settled (the VDS
#   part of the receivable is cleared: Dr VDS receivable / Cr AR) ->
#   claimed (the M51 Mushak 9.1 return took it as a VDS adjustment).
#
# CONTRACT FOR THE TAX SIDE (M51 / Mushak 9.1): read the certificates with
#   state = "settled" and period = "<YYYY-MM>" (the VAT period in which the
#   certificate is claimed), amount = vds_amount, the invoice in invoice_id,
#   certificate_no / certificate_date / customer_bin / challan_no for the
#   9.1 note; after filing call action_mark_claimed(return_ref) so a
#   certificate is never claimed twice. claimable_for_period() returns them.
#
# A08 remediation (B4, M20-2/-3/-13): state and every stamp are guarded
# (a preparer rewrote prepared_by_id and verified his own certificate; a
# draft was written "settled" with no GL); the certificate is frozen once
# verified (100 verified, 1,500 settled); "claimed" is recorded only for a
# FILED Mushak 9.1 return (fix.vat.return) that lists the certificate — a
# typed reference claims nothing.
import json
import re

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

PERIOD_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


class FixVdsCertificateReceived(models.Model):
    """A Mushak 6.6 VDS certificate received from a customer."""

    _name = "fix.vds.certificate.received"
    _description = "Customer VDS Certificate (Mushak 6.6 received)"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "certificate_date desc, id desc"

    _certificate_unique = models.Constraint(
        "UNIQUE (company_id, customer_id, certificate_no)",
        "This customer's VDS certificate number is already recorded",
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
        domain="[('state', 'in', ('issued', 'paid')), ('company_id', '=', company_id)]",
    )
    customer_id = fields.Many2one(
        related="invoice_id.customer_id", store=True, index=True, string="Customer"
    )
    currency_id = fields.Many2one(related="invoice_id.currency_id")
    invoice_vat_amount = fields.Monetary(
        related="invoice_id.vat_amount", string="Invoice VAT", currency_field="currency_id"
    )
    customer_bin = fields.Char(
        string="Withholding Entity BIN", help="The customer's BIN as printed on the certificate"
    )
    certificate_no = fields.Char(string="Certificate No", required=True, tracking=True)
    certificate_date = fields.Date(string="Certificate Date", required=True, tracking=True)
    period = fields.Char(
        string="VAT Period (YYYY-MM)",
        required=True,
        index=True,
        tracking=True,
        help="The Mushak 9.1 period in which the VDS is claimed (defaults to the "
        "certificate month)",
    )
    vds_amount = fields.Monetary(
        string="VDS Amount", currency_field="currency_id", required=True, tracking=True
    )
    challan_no = fields.Char(string="Treasury Challan No")
    challan_date = fields.Date(string="Challan Date")
    note = fields.Text(string="Notes")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("verified", "Verified"),
            ("settled", "Settled against Receivable"),
            ("claimed", "Claimed in Mushak 9.1"),
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
    claimed_return_ref = fields.Char(string="Mushak 9.1 Return Ref", readonly=True, copy=False)
    claimed_return_id = fields.Many2one(
        "fix.vat.return", string="Mushak 9.1 Return", readonly=True, copy=False
    )
    claimed_at = fields.Datetime(string="Claimed On", readonly=True, copy=False)

    VDS_GUARDED = {
        "state",
        "prepared_by_id",
        "verified_by_id",
        "verified_at",
        "settled_move_id",
        "settled_at",
        "claimed_return_ref",
        "claimed_return_id",
        "claimed_at",
    }
    # Frozen once a second person has verified the certificate.
    VDS_LOCKED = (
        "invoice_id",
        "vds_amount",
        "certificate_no",
        "certificate_date",
        "period",
        "company_id",
        "customer_bin",
        "challan_no",
        "challan_date",
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | self.VDS_GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and any(r.state != "draft" for r in self):
            locked |= set(self.VDS_LOCKED)
        return locked

    # ------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            invoice = self.env["fix.ar.invoice"].browse(vals.get("invoice_id"))
            if invoice:
                vals.setdefault("company_id", invoice.company_id.id)
                vals.setdefault("operating_unit_id", invoice.operating_unit_id.id)
                if not vals.get("customer_bin"):
                    vals["customer_bin"] = invoice.customer_id.vat or False
            if not vals.get("period") and vals.get("certificate_date"):
                vals["period"] = fields.Date.to_date(vals["certificate_date"]).strftime("%Y-%m")
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.vds.certificate.received")
                    or "VDS/New"
                )
        return super().create(vals_list)

    @api.onchange("certificate_date")
    def _onchange_certificate_date(self):
        if self.certificate_date and not self.period:
            self.period = self.certificate_date.strftime("%Y-%m")

    @api.constrains("period", "vds_amount", "invoice_id", "state")
    def _check_certificate(self):
        for cert in self:
            if not PERIOD_RE.match(cert.period or ""):
                raise ValidationError("The VAT period must be written YYYY-MM (e.g. 2026-10)")
            if cert.vds_amount <= 0:
                raise ValidationError("The VDS amount must be positive")
            if cert.state == "cancelled":
                continue
            others = cert.invoice_id.vds_certificate_ids.filtered(
                lambda c, cert=cert: c != cert and c.state != "cancelled"
            )
            certified = sum(others.mapped("vds_amount")) + cert.vds_amount
            if certified > cert.invoice_id.vat_amount + 0.005:
                raise ValidationError(
                    "VDS certified on invoice %s (%s) would exceed the invoice VAT (%s): "
                    "VAT deducted at source can never exceed the VAT charged."
                    % (cert.invoice_id.name, round(certified, 2), cert.invoice_id.vat_amount)
                )

    def write(self, vals):
        if not self._fix_guard_open() and set(self.VDS_LOCKED) & set(vals):
            for cert in self:
                if cert.state != "draft":
                    raise UserError(
                        "Certificate %s is %s — its amount, invoice, number and period are "
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

    def action_settle(self):
        """Clear the VDS part of the receivable: Dr VDS receivable / Cr AR
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
                    "Invoice %s is %s — VDS can only settle an open (issued) receivable"
                    % (invoice.name, invoice.state)
                )
            if cert.vds_amount > invoice.amount_residual + 0.005:
                raise UserError(
                    "VDS %s exceeds the open residual %s of invoice %s"
                    % (cert.vds_amount, invoice.amount_residual, invoice.name)
                )
            company = invoice.company_id
            vds_acc = _ar_account(cert.env, company, "vds_receivable")
            ar_acc = _ar_account(cert.env, company, "ar")
            move = invoice._post_reversal_gl(
                "VDS 6.6 %s — INV %s (%s)" % (cert.certificate_no, invoice.name, cert.period),
                [("vds_receivable", vds_acc, cert.vds_amount, invoice.customer_id.id)],
                [("ar", ar_acc, cert.vds_amount, invoice.customer_id.id)],
            )
            cert._guarded().write(
                {
                    "state": "settled",
                    "settled_move_id": move.id,
                    "settled_at": fields.Datetime.now(),
                }
            )
            publish(
                cert.env,
                "vds_certificate.settled",
                "fix.vds.certificate.received",
                cert.id,
                {
                    "certificate_no": cert.certificate_no,
                    "invoice": invoice.name,
                    "period": cert.period,
                    "vds_amount": cert.vds_amount,
                },
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

    def _filed_return(self):
        """The FILED Mushak 9.1 return of the certificate's period that took
        it as a VDS adjustment (its preparation lists the certificate)."""
        self.ensure_one()
        if "fix.vat.return" not in self.env:
            return self.env["res.users"].browse()
        returns = (
            self.env["fix.vat.return"]
            .sudo()
            .search(
                [
                    ("company_id", "=", self.company_id.id),
                    ("period", "=", self.period),
                    ("state", "=", "filed"),
                ]
            )
        )
        for ret in returns:
            raw = ret.vds_certificate_ids if "vds_certificate_ids" in ret._fields else None
            try:
                ids = json.loads(raw or "[]")
            except (TypeError, ValueError):
                ids = []
            if self.id in ids:
                return ret
        return returns.browse()

    def action_mark_claimed(self, return_ref=""):
        """Called by the Mushak 9.1 preparation once the VDS is taken as an
        adjustment, so a certificate is claimed exactly once. The claim is
        recorded only against a filed fix.vat.return that lists this
        certificate (A08 M20-13: any typed reference used to do)."""
        ref = (return_ref or "").strip()
        if not ref:
            raise UserError("The Mushak 9.1 return reference is required to mark a claim")
        for cert in self:
            if cert.state != "settled":
                raise UserError(
                    "Only settled certificates can be claimed (%s is %s)" % (cert.name, cert.state)
                )
            vat_return = cert._filed_return()
            if not vat_return:
                raise UserError(
                    "Certificate %s is claimed by filing the Mushak 9.1 return of %s that "
                    "includes it (M51); no filed return lists it." % (cert.name, cert.period)
                )
            cert._guarded().write(
                {
                    "state": "claimed",
                    "claimed_return_ref": ref,
                    "claimed_return_id": vat_return.id,
                    "claimed_at": fields.Datetime.now(),
                }
            )

    @api.model
    def claimable_for_period(self, period, company=None):
        """Settled, not yet claimed certificates of a VAT period."""
        company = company or self.env.company
        return self.search(
            [("company_id", "=", company.id), ("period", "=", period), ("state", "=", "settled")]
        )
