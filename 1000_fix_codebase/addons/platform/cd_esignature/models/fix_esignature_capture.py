# cd_esignature — M24 capture audit, second pass (19 Nov 2026).
#
# Page 5 (E-Signature) could send an envelope and let a signer sign with
# their own login, but the spec names two more things a person records:
#
#   fix.esignature.wet.signature  FR-DMS-026 (wet-signature scan), scope 12:
#       a customer or vendor without a login signs on paper at the counter;
#       a member of staff witnesses it and files the scan, and the signer's
#       place in the envelope is stamped with that evidence, in sequence.
#   action_verify                 FR-DMS-033, BRU-DMS-16: re-check a signed
#       envelope on demand, years later, from its own sealed evidence.
#
# BRU-DMS-17: the assurance level comes from the document's class
# (fix.document.class.signature_assurance_level) and is never downgraded by
# the requester: a class that needs a qualified signature accepts only the
# provider's, never a session click or a scan.
import base64
import hashlib
import json

from odoo import api, fields, models
from odoo.exceptions import UserError

from . import fix_esignature  # noqa: F401  (the base loads first)


def _required_level(envelope):
    cls = envelope.document_id.sudo().class_id
    return cls.signature_assurance_level if cls else False


class FixDocumentSignatureScan(models.Model):
    _inherit = "fix.document"

    document_type = fields.Selection(
        selection_add=[("signature_scan", "Wet-Ink Signature Scan")],
        ondelete={"signature_scan": "set default"},
    )


class FixEsignatureEnvelopeVerify(models.Model):
    _inherit = "fix.esignature.envelope"

    verified_at = fields.Datetime(readonly=True, copy=False)
    verified_by_id = fields.Many2one("res.users", readonly=True, copy=False)
    verification_result = fields.Selection(
        [("intact", "Intact"), ("broken", "Broken")], readonly=True, copy=False
    )
    verification_note = fields.Text(readonly=True, copy=False)
    assurance_level = fields.Selection(
        related="document_id.class_id.signature_assurance_level", string="Required Assurance"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "verified_at",
            "verified_by_id",
            "verification_result",
            "verification_note",
        }

    def action_verify(self):
        """FR-DMS-033: recompute the sealed evidence from the document bytes
        and the signer list, and read the completion certificate back. Any
        user may verify; the result is stamped on the envelope."""
        for envelope in self:
            if envelope.state not in ("sent", "partially_signed", "completed"):
                raise UserError(
                    "Only a sealed envelope (sent or completed) has evidence to verify — %s is %s."
                    % (envelope.name, envelope.state)
                )
            problems = []
            if envelope.sudo()._compute_evidence() != envelope.evidence_hash:
                problems.append("the document bytes or the signer list no longer match the seal")
            if envelope.state == "completed":
                cert = envelope.sudo().completion_certificate_id
                if not cert:
                    problems.append("the completion certificate is missing")
                else:
                    try:
                        raw = base64.b64decode(cert.attachment_id.datas or b"")
                        data = json.loads(raw.decode("utf-8"))
                    except Exception:
                        data = {}
                    if data.get("evidence_hash") != envelope.evidence_hash:
                        problems.append("the completion certificate does not carry the sealed hash")
                    signed = {
                        (s.get("signer"), s.get("sequence"))
                        for s in data.get("signers", [])
                        if s.get("signed_at")
                    }
                    expected = {(s.partner_id.name, s.sequence) for s in envelope.signer_ids}
                    if signed != expected:
                        problems.append("the certificate's signers differ from the envelope's")
                unsigned = envelope.signer_ids.filtered(lambda s: not s.signed_at)
                if unsigned:
                    problems.append("%d signer(s) carry no signature" % len(unsigned))
            ok = not problems
            envelope._guarded().write(
                {
                    "verified_at": fields.Datetime.now(),
                    "verified_by_id": self.env.uid,
                    "verification_result": "intact" if ok else "broken",
                    "verification_note": "Evidence %s matches; certificate consistent."
                    % envelope.evidence_hash
                    if ok
                    else "; ".join(problems),
                }
            )
            envelope.message_post(
                body="Verified by %s: %s"
                % (self.env.user.name, "INTACT" if ok else "BROKEN — " + "; ".join(problems))
            )
        return True


class FixEsignatureSignerAssurance(models.Model):
    _inherit = "fix.esignature.signer"

    def action_sign(self, provider=None):
        """BRU-DMS-17: a class that requires a qualified signature accepts only
        the provider's callback (which arrives as the service user), never a
        session click."""
        if not self.env.su:
            for signer in self:
                if _required_level(signer.envelope_id) == "qualified":
                    raise UserError(
                        "The class of '%s' requires a provider-backed qualified signature; it is "
                        "signed through the provider, not with a session click (BRU-DMS-17)."
                        % signer.envelope_id.document_id.name
                    )
        return super().action_sign(provider=provider)


class FixEsignatureWetSignature(models.Model):
    """A paper signature, witnessed and scanned, standing in for one signer's
    turn in an envelope. It is evidence: it is never edited or deleted."""

    _name = "fix.esignature.wet.signature"
    _description = "Wet-Ink Signature (scanned)"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    name = fields.Char(default="/", readonly=True, copy=False)
    envelope_id = fields.Many2one(
        "fix.esignature.envelope", required=True, ondelete="restrict", index=True
    )
    company_id = fields.Many2one(related="envelope_id.company_id", store=True, index=True)
    signer_id = fields.Many2one(
        "fix.esignature.signer", string="Signer", required=True, ondelete="restrict"
    )
    signed_on = fields.Date(
        string="Signed On (ink)", required=True, default=fields.Date.context_today
    )
    scan_file = fields.Binary(string="Scanned Signed Page", store=False)
    scan_filename = fields.Char(store=False)
    scan_document_id = fields.Many2one(
        "fix.document", string="Filed Scan", readonly=True, ondelete="restrict"
    )
    witnessed_by_id = fields.Many2one("res.users", string="Witnessed By", readonly=True)
    identity_checked = fields.Char(
        string="Identity Checked Against",
        required=True,
        help="The ID the witness saw (NID, passport, trade licence) — not its number.",
    )
    note = fields.Text()

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"scan_document_id", "witnessed_by_id"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self:
            locked |= {
                "envelope_id",
                "signer_id",
                "signed_on",
                "scan_file",
                "identity_checked",
                "note",
            }
        return locked

    @api.model_create_multi
    def create(self, vals_list):
        scans = [(v.pop("scan_file", None), v.pop("scan_filename", None)) for v in vals_list]
        for vals, (data, _fname) in zip(vals_list, scans, strict=True):
            if not data:
                raise UserError(
                    "Upload the scanned signed page: a wet signature is evidenced by its scan."
                )
            vals["witnessed_by_id"] = self.env.uid
        records = super(FixEsignatureWetSignature, self._guarded()).create(vals_list)
        for rec, (data, fname) in zip(records, scans, strict=True):
            rec._stamp(data, fname)
        return records.with_env(self.env)

    def _stamp(self, data, fname):
        self.ensure_one()
        signer = self.signer_id
        envelope = self.envelope_id
        if signer.envelope_id != envelope:
            raise UserError("%s is not a signer of %s." % (signer.partner_id.name, envelope.name))
        if envelope.state not in ("sent", "partially_signed"):
            raise UserError(
                "A signature is recorded on a SENT envelope — %s is %s."
                % (envelope.name, envelope.state)
            )
        if envelope.deadline and fields.Datetime.now() > envelope.deadline:
            raise UserError(
                "The signing window for %s closed on %s." % (envelope.name, envelope.deadline)
            )
        if signer.signed_at:
            raise UserError("%s has already signed %s." % (signer.partner_id.name, envelope.name))
        if _required_level(envelope) == "qualified":
            raise UserError(
                "The class of '%s' requires a provider-backed qualified signature; a scanned wet "
                "signature is a lower assurance level (BRU-DMS-17)." % envelope.document_id.name
            )
        if not self.env.su and self.env.user.partner_id == signer.partner_id:
            raise UserError("A wet signature is witnessed by someone other than the signer.")
        turn = envelope._next_signer()
        if turn and turn != signer:
            raise UserError(
                "The signing order is sequential — %s signs first (position %d)."
                % (turn.partner_id.name, turn.sequence)
            )
        scan = (
            self.env["fix.document"]
            .sudo()
            .attach(
                name=fname
                or "Wet-ink signature — %s — %s" % (envelope.name, signer.partner_id.name),
                datas=data,
                document_type="signature_scan",
                res_model="fix.esignature.envelope",
                res_id=envelope.id,
            )
        )
        name = "WET-%05d" % self.id
        self.sudo()._guarded().write({"scan_document_id": scan.id, "name": name})
        signer._guarded().write(
            {
                "signed_at": fields.Datetime.now(),
                "signature_provider": "wet-ink:%s sha256:%s"
                % (name, hashlib.sha256(base64.b64decode(data)).hexdigest()[:16]),
                "auth_method": "wet_ink_scan (witness %s, ID %s)"
                % (self.env.user.name, self.identity_checked),
            }
        )
        signed = envelope.signer_ids.filtered("signed_at")
        if signed and len(signed) < len(envelope.signer_ids):
            envelope._guarded().write({"state": "partially_signed"})
        envelope.message_post(
            body="%s signed in ink on %s, witnessed by %s; scan %s filed."
            % (signer.partner_id.name, self.signed_on, self.env.user.name, scan.name)
        )

    def write(self, vals):
        if not self._fix_guard_open():
            # a guarded field gets the guard's own refusal (the A10 control
            # suite reads it); anything else is still evidence, never edited
            touched = self._fix_guarded_fields() & set(vals)
            if touched:
                super().write({k: vals[k] for k in touched})  # refuses any change
            raise UserError("A recorded wet signature is evidence: it is never edited.")
        return super().write(vals)

    def unlink(self):
        if not self.env.su:
            raise UserError("A recorded wet signature is evidence: it is never deleted.")
        return super().unlink()
