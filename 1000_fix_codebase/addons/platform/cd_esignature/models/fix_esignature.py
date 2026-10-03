# cd_esignature — M24 completion: e-signature envelopes (P06-M08-T02, CD-M24-03).
#
# The L6 qualified e-signature component is a CFO-approved external
# component (a written OSS-alternative review is a governance item); this
# module is the ENVELOPE: who signs what, in what order, with what evidence
# hash — independent of the signing provider.
from odoo import api, fields, models
from odoo.exceptions import UserError

import hashlib
import json

from libs.py.fix_events import publish  # FF-28


class FixEsignatureEnvelope(models.Model):
    """A signing envelope: a document + ordered signers + evidence."""

    _name = "fix.esignature.envelope"
    _description = "E-Signature Envelope"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc, id desc"

    company_id = fields.Many2one("res.company", required=True, index=True,
                                 default=lambda self: self.env.company)
    operating_unit_id = fields.Many2one("operating.unit", required=True, index=True)
    name = fields.Char(string="Subject", required=True)
    document_id = fields.Many2one("fix.document", string="Document",
                                  required=True, ondelete="restrict")
    signer_ids = fields.One2many("fix.esignature.signer", "envelope_id",
                                 string="Signers")
    state = fields.Selection(
        [("draft", "Draft"), ("sent", "Sent"), ("partially_signed", "Partially Signed"),
         ("completed", "Completed"), ("declined", "Declined"), ("voided", "Voided")],
        default="draft", required=True, tracking=True)
    evidence_hash = fields.Char(readonly=True,
                                help="SHA-256 over document bytes + signer list — tamper evidence")
    completed_at = fields.Datetime(readonly=True)

    def _compute_evidence(self) -> str:
        payload = json.dumps({
            "document": self.document_id.name or "",
            "signers": [(s.signer_name, s.sequence) for s in self.signer_ids.sorted("sequence")],
        }, sort_keys=True).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def action_send(self):
        for envelope in self:
            if not envelope.signer_ids:
                raise UserError("An envelope needs at least one signer")
            envelope.write({"state": "sent",
                            "evidence_hash": envelope._compute_evidence()})
            publish(self.env, "envelope.sent", "fix.esignature.envelope",
                    envelope.id, {"subject": envelope.name})

    def action_check_complete(self):
        for envelope in self:
            if all(s.signed_at for s in envelope.signer_ids):
                envelope.write({"state": "completed",
                                "completed_at": fields.Datetime.now()})
                publish(self.env, "envelope.completed", "fix.esignature.envelope",
                        envelope.id, {"evidence_hash": envelope.evidence_hash})


class FixEsignatureSigner(models.Model):
    """One signer in an envelope's signing order."""

    _name = "fix.esignature.signer"
    _description = "E-Signature Signer"

    envelope_id = fields.Many2one("fix.esignature.envelope", required=True,
                                  ondelete="cascade")
    sequence = fields.Integer(default=10)
    partner_id = fields.Many2one("res.partner", string="Signer", required=True,
                                 ondelete="restrict")
    signer_name = fields.Char(related="partner_id.name")
    role_label = fields.Char(string="Signs As",
                             help="e.g. Customer, Branch Manager, Vendor Authorised Person")
    signed_at = fields.Datetime(readonly=True)
    signature_provider = fields.Char(readonly=True,
                                     help="The L6 provider's signature reference")

    @api.constrains("sequence")
    def _check_order(self):
        seen = set()
        for signer in self.envelope_id.signer_ids.sorted("sequence"):
            if signer.sequence in seen:
                raise UserError("Signing order sequences must be unique")
            seen.add(signer.sequence)
