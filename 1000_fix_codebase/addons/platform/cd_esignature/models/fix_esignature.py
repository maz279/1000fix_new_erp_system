# cd_esignature — M24 completion: e-signature envelopes (P06-M08-T02, CD-M24-03).
#
# The L6 qualified e-signature component is a CFO-approved external
# component (a written OSS-alternative review is a governance item); this
# module is the ENVELOPE: who signs what, in what order, with what evidence
# hash — independent of the signing provider.
#
# A10 remediation (2026-11-05, report §6 D1, findings M24-1/-2/-3/-9/-10):
# there was no signing method at all — signed_at was typed by whoever cared
# to, the "evidence hash" covered the document NAME, and an envelope with no
# signer completed from a draft. A signature is now an act of the signer's
# own login, in sequence, over sealed file bytes; completion re-hashes the
# bytes and refuses a swap; a completed envelope freezes itself and its
# document, and files a completion certificate.
import base64
import hashlib
import json

from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish  # FF-28

# A04 integration (2026-11-04): M08 activates a contract, and M36 accepts a
# quote, on a COMPLETED envelope. A04's C2 guard on the envelope state,
# evidence and signatures landed as part of the M24 evidence rebuild below
# (guard mixin, sealed-once-sent fields, the deadline and the completion
# certificate).
SEND_SECONDS = 3 * 24 * 3600  # default signing window: three days
# what a signer's guard seals (A04): the signature itself, and once the
# envelope has left draft, the signer's identity and place in the sequence
SIGNER_GUARDED = {"signed_at", "signature_provider"}
SIGNER_SEALED = {"envelope_id", "sequence", "partner_id"}


def _attachment_bytes(document) -> bytes:
    # The bytes are read through sudo: they are the EVIDENCE the hash seals,
    # and every actor of the envelope (the sender, the completion checker,
    # the cron) must be able to re-hash them regardless of the attachment
    # ACL world (Odoo's base rule hides res_field attachments from plain
    # internal users — caught live when the A04 merge tightened it).
    attachment = document.sudo().attachment_id if document else False
    if attachment and attachment.datas:
        try:
            return base64.b64decode(attachment.datas)
        except Exception:
            return str(attachment.datas).encode("utf-8")
    return b""


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
            ("expired", "Expired"),
            ("voided", "Voided"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    evidence_hash = fields.Char(
        readonly=True, help="SHA-256 over document bytes + signer list — tamper evidence"
    )
    sent_at = fields.Datetime(readonly=True)
    deadline = fields.Datetime(
        readonly=True, help="Signing window; past it the envelope expires and is voided"
    )
    completed_at = fields.Datetime(readonly=True)
    decline_reason = fields.Char(readonly=True)
    void_reason = fields.Char(readonly=True)
    completion_certificate_id = fields.Many2one(
        "fix.document", string="Completion Certificate", readonly=True, ondelete="restrict"
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "evidence_hash",
            "sent_at",
            "deadline",
            "completed_at",
            "decline_reason",
            "void_reason",
            "completion_certificate_id",
        }

    def _fix_form_locked_fields(self) -> set:
        # A sent envelope is under evidence: its subject, document and signer
        # list are what was sent. Only the note fields stay editable.
        locked = super()._fix_form_locked_fields()
        if self and all(rec.state != "draft" for rec in self):
            locked |= {"name", "document_id", "operating_unit_id", "signer_ids"}
        return locked

    def write(self, vals):
        # The signers travel with the envelope: once out of draft, re-pointing
        # the envelope at another document or subject is a forgery (M24-2/-3,
        # A04's sealed-once-sent list).
        if self and not self._fix_guard_open():
            touched = {"name", "document_id", "operating_unit_id", "signer_ids"} & set(vals)
            if touched:
                for rec in self:
                    offenders = [n for n in touched if rec._fix_guard_differs(n, vals[n], rec[n])]
                    if offenders and rec.state != "draft":
                        self._fix_guard_refuse(offenders)
        return super().write(vals)

    # ------------------------------------------------------------- evidence
    def _compute_evidence(self) -> str:
        """SHA-256 over the document BYTES and the signer list (M24-3).

        The old hash covered the document's name: two files reading 'Pay
        5,000' and 'Pay 500,000' under one name sealed identically. The
        formula covers only what cannot change after send — the bytes and
        the (partner, sequence) pairs — so signing itself never moves it."""
        self.ensure_one()
        payload = json.dumps(
            {
                "document": self.document_id.name or "",
                "bytes_sha256": hashlib.sha256(_attachment_bytes(self.document_id)).hexdigest(),
                "signers": [
                    (s.partner_id.name or "", s.sequence)
                    for s in self.signer_ids.sorted("sequence")
                ],
            },
            sort_keys=True,
        ).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def _next_signer(self):
        """The signer whose turn it is: the first unsigned in sequence."""
        self.ensure_one()
        unsigned = self.signer_ids.filtered(lambda s: not s.signed_at).sorted("sequence")
        return unsigned[:1]

    def _assert_document_issuable(self):
        for rec in self:
            doc = rec.document_id
            if doc.legal_hold:
                raise UserError(
                    "'%s' is under legal hold — it cannot be sent for signature." % doc.name
                )
            if doc.is_controlled and doc.control_state != "published":
                raise UserError(
                    "'%s' is a controlled document in state '%s' — only a PUBLISHED "
                    "version may be signed (M24-5)." % (doc.name, doc.control_state)
                )
            if not doc.is_current:
                raise UserError(
                    "'%s' is a superseded version — only the CURRENT version of a "
                    "document line may be signed (M24-5)." % doc.name
                )
            if not _attachment_bytes(doc):
                raise UserError(
                    "'%s' has no file to sign — an envelope seals bytes, not a name." % doc.name
                )

    # ------------------------------------------------------------ lifecycle
    def action_send(self):
        """Seal the envelope: hash the bytes, lock the document, start the
        signing window."""
        for envelope in self:
            if envelope.state != "draft":
                raise UserError(
                    "Only a DRAFT envelope is sent — %s is %s." % (envelope.name, envelope.state)
                )
            if not envelope.signer_ids:
                raise UserError("An envelope needs at least one signer")
            envelope._assert_document_issuable()
            now = fields.Datetime.now()
            envelope._guarded().write(
                {
                    "state": "sent",
                    "evidence_hash": envelope._compute_evidence(),
                    "sent_at": now,
                    "deadline": fields.Datetime.add(now, seconds=SEND_SECONDS),
                }
            )
            envelope.document_id._guarded().write({"signature_locked": True})
            publish(
                self.env,
                "envelope.sent",
                "fix.esignature.envelope",
                envelope.id,
                {
                    "subject": envelope.name,
                    "document": envelope.document_id.name,
                    "evidence_hash": envelope.evidence_hash,
                },
            )
        return True

    def action_check_complete(self):
        """Complete only from a SENT envelope whose every signer signed, over
        the same bytes that were sealed (M24-2/-3). Files the completion
        certificate and freezes the envelope."""
        for envelope in self:
            if envelope.state not in ("sent", "partially_signed"):
                raise UserError(
                    "Completion is checked on a SENT envelope — %s is %s."
                    % (envelope.name, envelope.state)
                )
            if not envelope.signer_ids:
                raise UserError("An envelope needs at least one signer")
            if envelope.deadline and fields.Datetime.now() > envelope.deadline:
                envelope._guarded().write({"state": "expired"})
                raise UserError(
                    "The signing window for %s closed on %s — void the envelope and "
                    "send a new one." % (envelope.name, envelope.deadline)
                )
            if not all(s.signed_at for s in envelope.signer_ids):
                raise UserError(
                    "Every signer must sign before %s completes — %d of %d have."
                    % (
                        envelope.name,
                        len(envelope.signer_ids.filtered("signed_at")),
                        len(envelope.signer_ids),
                    )
                )
            if envelope._compute_evidence() != envelope.evidence_hash:
                raise UserError(
                    "The document or signer list of %s changed after it was sent — the "
                    "sealed evidence no longer matches. Void it and start again." % envelope.name
                )
            now = fields.Datetime.now()
            # the certificate files through the service env: the sender who
            # checks completion is not granted the attachment store
            certificate = (
                self.env["fix.document"]
                .sudo()
                .attach(
                    name="Signature Certificate — %s" % envelope.name,
                    datas=base64.b64encode(
                        json.dumps(
                            {
                                "envelope": envelope.name,
                                "document": envelope.document_id.name,
                                "evidence_hash": envelope.evidence_hash,
                                "signers": [
                                    {
                                        "signer": s.partner_id.name,
                                        "sequence": s.sequence,
                                        "signed_at": s.signed_at.isoformat()
                                        if s.signed_at
                                        else None,
                                        "provider": s.signature_provider,
                                        "auth_method": s.auth_method,
                                    }
                                    for s in envelope.signer_ids.sorted("sequence")
                                ],
                                "completed_at": now.isoformat(),
                            },
                            sort_keys=True,
                        ).encode("utf-8")
                    ),
                    document_type="signature_certificate",
                    res_model="fix.esignature.envelope",
                    res_id=envelope.id,
                )
            )
            envelope._guarded().write(
                {
                    "state": "completed",
                    "completed_at": now,
                    "completion_certificate_id": certificate.id,
                }
            )
            publish(
                self.env,
                "envelope.completed",
                "fix.esignature.envelope",
                envelope.id,
                {
                    "evidence_hash": envelope.evidence_hash,
                    "certificate": certificate.name,
                },
            )
            envelope.message_post(
                body="Completed — evidence %s; certificate %s filed."
                % (envelope.evidence_hash, certificate.name)
            )
        return True

    def action_void(self, reason: str = ""):
        """The sender withdraws the envelope; the document is unsealed."""
        for envelope in self:
            if envelope.state not in ("draft", "sent", "partially_signed"):
                raise UserError(
                    "Only a draft or in-flight envelope is voided — %s is %s."
                    % (envelope.name, envelope.state)
                )
            if not reason or not reason.strip():
                raise UserError(
                    "State why the envelope is voided — the void is part of the record."
                )
            was_sent = envelope.state in ("sent", "partially_signed")
            envelope._guarded().write({"state": "voided", "void_reason": reason.strip()})
            if was_sent:
                envelope.document_id._guarded().write({"signature_locked": False})
            envelope.message_post(body="Voided by %s: %s" % (self.env.user.name, reason.strip()))
        return True

    @api.model
    def cron_expire_envelopes(self):
        """Daily: in-flight envelopes past their deadline expire and unseal
        their documents (M24-10)."""
        stale = self.search(
            [
                ("state", "in", ("sent", "partially_signed")),
                ("deadline", "!=", False),
                ("deadline", "<", fields.Datetime.now()),
            ]
        )
        for envelope in stale:
            envelope._guarded().write({"state": "expired"})
            envelope.document_id._guarded().write({"signature_locked": False})
            envelope.message_post(body="Signing window closed on %s." % envelope.deadline)
        return len(stale)


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
    auth_method = fields.Char(
        readonly=True, help="How the signer authenticated (session, OTP, provider callback)"
    )

    def _fix_guarded_fields(self) -> set:
        # envelope_id is NOT here: a signer is BORN on its envelope (the
        # one2many create sets it in the user's env). Re-pointing an existing
        # signer is the forgery — that is guarded in write() below.
        # SIGNER_SEALED (A04): once the envelope has left draft, the signer's
        # identity and place in the sequence are evidence, not configuration.
        guarded = super()._fix_guarded_fields() | SIGNER_GUARDED | {"auth_method"}
        if any(s.envelope_id.state != "draft" for s in self):
            guarded |= SIGNER_SEALED
        return guarded

    def write(self, vals):
        if self and not self._fix_guard_open() and "envelope_id" in vals:
            for signer in self:
                if signer._fix_guard_differs(
                    "envelope_id", vals["envelope_id"], signer.envelope_id
                ):
                    self._fix_guard_refuse(["envelope_id"])
        return super().write(vals)

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

    @api.model_create_multi
    def create(self, vals_list):
        # A signer joins an envelope only while it is a draft: adding one to
        # a sent envelope would change the sealed evidence (M24-2, probe e17).
        if not self._fix_guard_open():
            envelopes = self.env["fix.esignature.envelope"].browse(
                {v["envelope_id"] for v in vals_list if v.get("envelope_id")}
            )
            for envelope in envelopes:
                if envelope.state != "draft":
                    raise UserError(
                        "Signers join an envelope while it is a DRAFT — %s is %s."
                        % (envelope.name, envelope.state)
                    )
        return super().create(vals_list)

    def unlink(self):
        # An unsigned signer leaves only in draft (M24-2, probe e16): deleting
        # one from a sent envelope would complete it over fewer signatures.
        if not self._fix_guard_open():
            for signer in self:
                if signer.envelope_id.state != "draft":
                    raise UserError(
                        "Signers are removed only while the envelope is a DRAFT — %s is %s."
                        % (signer.envelope_id.name, signer.envelope_id.state)
                    )
        return super().unlink()

    # ------------------------------------------------------------- signing
    def action_sign(self, provider=None):
        """The signer's own act (M24-1): only the user whose partner IS the
        signer may sign, in sequence, inside the window. The timestamps and
        the authentication evidence are stamped server-side — never typed."""
        for signer in self:
            envelope = signer.envelope_id
            if not self.env.su and self.env.user.partner_id != signer.partner_id:
                raise UserError(
                    "%s signs for themself — the signature of %s belongs to %s's own "
                    "login (A10 D1)."
                    % (signer.partner_id.name, envelope.name, signer.partner_id.name)
                )
            if envelope.state not in ("sent", "partially_signed"):
                raise UserError(
                    "Signing happens on a SENT envelope — %s is %s."
                    % (envelope.name, envelope.state)
                )
            if envelope.deadline and fields.Datetime.now() > envelope.deadline:
                raise UserError(
                    "The signing window for %s closed on %s." % (envelope.name, envelope.deadline)
                )
            if signer.signed_at:
                raise UserError(
                    "%s has already signed %s." % (signer.partner_id.name, envelope.name)
                )
            turn = envelope._next_signer()
            if turn and turn != signer:
                raise UserError(
                    "The signing order is sequential — %s signs first (position %d; %s "
                    "is at %d)."
                    % (turn.partner_id.name, turn.sequence, signer.partner_id.name, signer.sequence)
                )
            signer._guarded().write(
                {
                    "signed_at": fields.Datetime.now(),
                    "signature_provider": (provider or "internal").strip() or "internal",
                    "auth_method": "session" if not self.env.su else "provider-callback",
                }
            )
            signed = envelope.signer_ids.filtered("signed_at")
            if signed and len(signed) < len(envelope.signer_ids):
                # some, but not all: the envelope is in flight (M24-10 —
                # 'partially_signed' used to be unreachable). Completion is
                # its own explicit, hash-checked step (M24-2).
                envelope._guarded().write({"state": "partially_signed"})
            envelope.message_post(
                body="%s signed (position %d, %s)."
                % (signer.partner_id.name, signer.sequence, provider or "internal session")
            )
        return True

    def action_decline(self, reason: str = ""):
        """A signer refuses to sign: the envelope is declined with the reason
        on file and the document is unsealed."""
        for signer in self:
            envelope = signer.envelope_id
            if not self.env.su and self.env.user.partner_id != signer.partner_id:
                raise UserError(
                    "Only %s declines their own signature on %s."
                    % (signer.partner_id.name, envelope.name)
                )
            if envelope.state not in ("sent", "partially_signed"):
                raise UserError(
                    "Declining happens on a SENT envelope — %s is %s."
                    % (envelope.name, envelope.state)
                )
            if not reason or not reason.strip():
                raise UserError("State the reason — a refusal without grounds is not a record.")
            envelope._guarded().write({"state": "declined", "decline_reason": reason.strip()})
            envelope.document_id._guarded().write({"signature_locked": False})
            envelope.message_post(body="%s declined: %s" % (signer.partner_id.name, reason.strip()))
        return True
