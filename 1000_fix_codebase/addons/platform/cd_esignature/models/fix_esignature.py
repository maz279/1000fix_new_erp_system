# cd_esignature — M24 completion: e-signature envelopes (P06-M08-T02, CD-M24-03).
#
# The L6 qualified e-signature component is a CFO-approved external
# component (a written OSS-alternative review is a governance item); this
# module is the ENVELOPE: who signs what, in what order, with what evidence
# hash — independent of the signing provider.
import hashlib
import json

from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish  # FF-28

# A04 integration (2026-11-04): M08 activates a contract, and M36 accepts a
# quote, on a COMPLETED envelope. The envelope state, its evidence and each
# signer's signature were plain fields any internal user could write, so a
# "completed signature" could be typed. They now change only through the
# transitions below (fix.guarded.mixin); a signature is recorded by the
# provider integration, which runs as a trusted service (sudo / superuser).
ENVELOPE_GUARDED = {"state", "evidence_hash", "completed_at"}
# what the evidence hash seals: frozen once the envelope leaves draft
ENVELOPE_SEALED = {"document_id", "signer_ids"}
SIGNER_GUARDED = {"signed_at", "signature_provider"}
SIGNER_SEALED = {"envelope_id", "sequence", "partner_id"}


class FixEsignatureEnvelope(models.Model):
    """A signing envelope: a document + ordered signers + evidence."""

    _name = "fix.esignature.envelope"
    _description = "E-Signature Envelope"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "create_date desc, id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    name = fields.Char(string="Subject", required=True)
    document_id = fields.Many2one(
        "fix.document", string="Document", required=True, ondelete="restrict"
    )
    signer_ids = fields.One2many("fix.esignature.signer", "envelope_id", string="Signers")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("sent", "Sent"),
            ("partially_signed", "Partially Signed"),
            ("completed", "Completed"),
            ("declined", "Declined"),
            ("voided", "Voided"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    evidence_hash = fields.Char(
        readonly=True, help="SHA-256 over document bytes + signer list — tamper evidence"
    )
    completed_at = fields.Datetime(readonly=True)

    def _fix_guarded_fields(self) -> set:
        guarded = super()._fix_guarded_fields() | ENVELOPE_GUARDED
        if any(env.state != "draft" for env in self):
            guarded |= ENVELOPE_SEALED
        return guarded

    def _compute_evidence(self) -> str:
        payload = json.dumps(
            {
                "document": self.document_id.name or "",
                "signers": [
                    (s.signer_name, s.sequence) for s in self.signer_ids.sorted("sequence")
                ],
            },
            sort_keys=True,
        ).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def action_send(self):
        for envelope in self:
            if envelope.state != "draft":
                raise UserError("Only a draft envelope can be sent (it is %s)." % envelope.state)
            if not envelope.signer_ids:
                raise UserError("An envelope needs at least one signer")
            envelope._guarded().write(
                {"state": "sent", "evidence_hash": envelope._compute_evidence()}
            )
            publish(
                self.env,
                "envelope.sent",
                "fix.esignature.envelope",
                envelope.id,
                {"subject": envelope.name},
            )

    def action_check_complete(self):
        for envelope in self:
            if envelope.state not in ("sent", "partially_signed"):
                continue
            if envelope.signer_ids and all(s.signed_at for s in envelope.signer_ids):
                envelope._guarded().write(
                    {"state": "completed", "completed_at": fields.Datetime.now()}
                )
                publish(
                    self.env,
                    "envelope.completed",
                    "fix.esignature.envelope",
                    envelope.id,
                    {"evidence_hash": envelope.evidence_hash},
                )


class FixEsignatureSigner(models.Model):
    """One signer in an envelope's signing order."""

    _name = "fix.esignature.signer"
    _description = "E-Signature Signer"
    _inherit = ["fix.guarded.mixin"]

    envelope_id = fields.Many2one("fix.esignature.envelope", required=True, ondelete="cascade")
    sequence = fields.Integer(default=10)
    partner_id = fields.Many2one("res.partner", string="Signer", required=True, ondelete="restrict")
    signer_name = fields.Char(related="partner_id.name")
    role_label = fields.Char(
        string="Signs As", help="e.g. Customer, Branch Manager, Vendor Authorised Person"
    )
    signed_at = fields.Datetime(readonly=True)
    signature_provider = fields.Char(readonly=True, help="The L6 provider's signature reference")

    def _fix_guarded_fields(self) -> set:
        guarded = super()._fix_guarded_fields() | SIGNER_GUARDED
        if any(s.envelope_id.state != "draft" for s in self):
            guarded |= SIGNER_SEALED
        return guarded

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            ids = {vals.get("envelope_id") for vals in vals_list} - {False, None}
            if any(e.state != "draft" for e in self.env["fix.esignature.envelope"].browse(ids)):
                raise UserError("Signers are added while the envelope is a draft.")
        return super().create(vals_list)

    def unlink(self):
        if not self._fix_guard_open() and any(s.envelope_id.state != "draft" for s in self):
            raise UserError("A signer is removed while the envelope is a draft.")
        return super().unlink()

    def _esign_provider_record_signature(self, signature_ref, signed_at=None):
        """The provider integration records a completed signature (trusted
        service: called with sudo() after verifying the provider's callback),
        then the envelope re-checks completion."""
        if not self.env.su:
            raise UserError("A signature is recorded by the e-signature provider only.")
        for signer in self:
            if signer.envelope_id.state not in ("sent", "partially_signed"):
                raise UserError("Envelope %s is not out for signature." % signer.envelope_id.name)
            if signer.signed_at:
                raise UserError("%s has already signed." % (signer.signer_name or signer.id))
            signer._guarded().write(
                {
                    "signed_at": signed_at or fields.Datetime.now(),
                    "signature_provider": signature_ref,
                }
            )
        self.envelope_id.action_check_complete()
        return True

    @api.constrains("sequence")
    def _check_order(self):
        seen = set()
        for signer in self.envelope_id.signer_ids.sorted("sequence"):
            if signer.sequence in seen:
                raise UserError("Signing order sequences must be unique")
            seen.add(signer.sequence)
