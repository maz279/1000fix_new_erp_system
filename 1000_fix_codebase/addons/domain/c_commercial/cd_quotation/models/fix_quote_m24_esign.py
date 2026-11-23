# fix_quote_m24_esign — M36 quotation e-signature THROUGH M24 (A10 deep audit
# 2026-11-23, D-A10-4).
#
# The registry promised "M36 quote e-sign" through the document kernel; the
# module actually signed via its own provider HMAC (esign_provider_ref), so
# quote signatures carried none of M24's evidence: no sealed bytes, no ordered
# signers, no tamper check, no completion certificate. This bridge files the
# quotation PDF as a governed document and sends it for signature through
# fix.esignature.envelope; completion (M24 verifies every signer over the
# sealed bytes) accepts the quotation with acceptance_method='esign'.
#
# The provider-HMAC path stays available for estates that run an external
# provider; this is the in-house route the registry describes.
import base64
import logging

from odoo import fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

QUOTE_DOC_TYPE = "other"  # a quotation is not a contract until accepted
REPORT_REF = "cd_quotation.action_report_fix_quotation"
SIGN_WINDOW_DAYS = 7


class FixQuotationM24Esign(models.Model):
    _inherit = "fix.quotation"

    esign_envelope_id = fields.Many2one(
        "fix.esignature.envelope",
        string="E-Signature Envelope (M24)",
        readonly=True,
        copy=False,
        ondelete="restrict",
        help="The M24 envelope this quotation is signed through: sealed bytes, "
        "ordered signers and the completion certificate.",
    )

    def _fix_quote_pdf(self) -> bytes:
        self.ensure_one()
        report = self.env["ir.actions.report"].sudo()
        pdf, _kind = report._render_qweb_pdf(REPORT_REF, self.ids)
        if not pdf:
            raise UserError("The quotation PDF could not be rendered for %s." % self.name)
        return pdf

    def _fix_file_quote_document(self):
        """File the quotation's PDF in the governed repository (once)."""
        self.ensure_one()
        Doc = self.env["fix.document"].sudo()
        existing = Doc.search(
            [
                ("res_model", "=", "fix.quotation"),
                ("res_id", "=", self.id),
                ("document_type", "=", QUOTE_DOC_TYPE),
            ],
            limit=1,
        )
        if existing:
            return existing
        return Doc.with_company(self.company_id).attach(
            name=("%s v%s.pdf" % (self.name, self.version))[:200],
            datas=base64.b64encode(self._fix_quote_pdf()),
            document_type=QUOTE_DOC_TYPE,
            res_model="fix.quotation",
            res_id=self.id,
        )

    def action_request_esignature(self):
        """Send the issued quotation for signature through M24."""
        for rec in self:
            if rec.state != "sent":
                raise UserError(
                    "Quotation %s is %s: only an ISSUED quotation is sent for signature."
                    % (rec.name, rec.state)
                )
            if rec.esign_envelope_id:
                raise UserError(
                    "Quotation %s already has envelope %s."
                    % (rec.name, rec.esign_envelope_id.name)
                )
            partner = rec.customer_id
            if not partner or not (partner.email or partner.phone):
                raise UserError(
                    "The customer of %s has no email or phone for the signing request."
                    % rec.name
                )
            if not rec.operating_unit_id:
                raise UserError("Set the operating unit on %s first." % rec.name)
            document = rec._fix_file_quote_document()
            envelope = (
                self.env["fix.esignature.envelope"]
                .with_company(rec.company_id)
                .create(
                    {
                        "name": "Quotation %s v%s" % (rec.name, rec.version),
                        "operating_unit_id": rec.operating_unit_id.id,
                        "document_id": document.id,
                        # deadline is set by action_send (guarded): the
                        # envelope's own SEND_SECONDS window applies
                        "signer_ids": [
                            (
                                0,
                                0,
                                {
                                    "partner_id": partner.id,
                                    "sequence": 10,
                                    "role_label": "Customer acceptance",
                                },
                            )
                        ],
                    }
                )
            )
            envelope.action_send()
            rec._guarded().write(
                {"esign_state": "sent", "esign_envelope_id": envelope.id}
            )
            rec.message_post(
                body="Signature requested through M24 envelope %s (document %s, evidence %s)."
                % (envelope.name, document.name, envelope.evidence_hash[:12])
            )
        return True


class FixA10QuotationConsumers(models.AbstractModel):
    """Consumers of the M24 envelope events for quotations (relay-only)."""

    _name = "fix.a10.quotation.consumers"
    _description = "A10 Quotation M24 E-Signature Consumers"

    def _quote_of(self, event, label):
        if not self.env.su:
            raise UserError("%s runs only from the event relay." % label)
        if event.get("aggregate") != "fix.esignature.envelope":
            raise UserError(
                "%s refused: the event's aggregate is %s, not the envelope."
                % (label, event.get("aggregate"))
            )
        envelope = self.env["fix.esignature.envelope"].browse(event.get("aggregate_id") or 0)
        if not envelope.exists():
            return envelope, self.env["fix.quotation"]
        quote = self.env["fix.quotation"].search(
            [("esign_envelope_id", "=", envelope.id)], limit=1
        )
        return envelope, quote

    def consume_envelope_completed(self, event: dict) -> dict:
        """The customer signed every signature over the sealed bytes: accept
        the quotation with acceptance_method='esign' and the envelope as its
        evidence. Idempotent — a replayed event on an accepted quote is a
        no-op, never a second acceptance."""
        label = "Quotation e-signature completion"
        envelope, quote = self._quote_of(event, label)
        if not quote:
            return {"skipped": 1, "reason": "no quotation carries this envelope"}
        if quote.state == "accepted":
            return {"skipped": 1, "reason": "already accepted"}
        if quote.state != "sent":
            return {"skipped": 1, "reason": "quotation is %s" % quote.state}
        ref = "M24 envelope %s — evidence %s" % (
            envelope.name,
            (envelope.evidence_hash or "")[:32],
        )
        quote.sudo()._accept("esign", ref)
        quote.message_post(
            body="Accepted by the customer's M24 e-signature (envelope %s)." % envelope.name
        )
        return {"accepted": 1, "quotation": quote.name}
