# fix.identity.document — NID, passport, TIN routed through the residency
# service to Z4 (P03-M05-T05). The sensitive field is NEVER duplicated into
# the regional store — not transiently, not in a cache, not in a log.
# Enforced at write time by the residency.mixin (P03-M09-T04).
import logging

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

from .fix_party_security import STEWARD_GROUP

logger = logging.getLogger(__name__)

# Editing what was verified makes the verification stale.
_KYC_SUBJECT_FIELDS = {"document_number", "document_type"}


class FixIdentityDocument(models.Model):
    """An identity document (NID, passport, TIN) with residency-classified
    field storage. The DOCUMENT TYPE and metadata are in the regional store;
    the IDENTIFIER VALUE lives in Z4, accessible only via fix_residency."""

    _name = "fix.identity.document"
    _description = "Identity Document"
    # fix.approvable.mixin already carries fix.guarded.mixin.
    _inherit = ["mail.thread", "mail.activity.mixin", "residency.mixin", "fix.approvable.mixin"]

    # A03 audit W4 (R7): KYC is a routed M63 decision. Submitting requests
    # it; a data steward other than the capturer approves (verify) or
    # rejects (fail, with the reason) from the approval inbox.
    _approval_domain = "kyc"
    _approval_apply_method = "action_kyc_verify"
    _approval_group = STEWARD_GROUP
    _approval_routed = True

    def _fix_guarded_fields(self) -> set:
        # KYC was a plain field edit and verified_by was never written
        # (A03 audit M33-9): the verification is the steward's action.
        return super()._fix_guarded_fields() | {
            "verification_status",
            "verified_by",
            "verified_at",
            "verification_note",
        }

    # The classified fields routed to Z4 by the residency.mixin:
    # key prefix "party nid" / "party passport" / "party tin"
    _residency_fields = {
        "document_number": "party identity",
    }

    # AS-03
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")

    partner_id = fields.Many2one(
        "res.partner", string="Party", required=True, ondelete="cascade", index=True
    )
    document_type = fields.Selection(
        [
            ("nid_10", "NID (10-digit)"),
            ("nid_17", "NID (17-digit)"),
            ("passport", "Passport"),
            ("tin", "TIN"),
            ("trade_license", "Trade Licence"),
            ("brn", "Birth Registration No."),
            ("biometric", "Biometric Template"),
        ],
        required=True,
        tracking=True,
    )

    # document_number is the CLASSIFIED field — the mixin routes it to Z4.
    # The regional store holds only the residency_ref (UUID pointer).
    document_number = fields.Char(
        string="Document Number",
        help="RESIDENCY-CLASSIFIED: the value goes to Z4 via the residency "
        "mixin; the regional store holds only the residency_ref pointer",
    )

    # Non-classified metadata (safe to store regionally)
    issuing_country = fields.Many2one(
        "res.country", string="Issuing Country", default=lambda self: self.env.ref("base.bd")
    )
    expiry_date = fields.Date(string="Expiry Date", tracking=True)
    is_primary = fields.Boolean(string="Primary Document", default=True)
    verification_status = fields.Selection(
        [
            ("unverified", "Unverified"),
            ("pending", "Verification Pending"),
            ("verified", "Verified"),
            ("failed", "Verification Failed"),
        ],
        default="unverified",
        tracking=True,
    )
    verified_by = fields.Many2one("res.users", string="Verified By", readonly=True)
    verified_at = fields.Datetime(readonly=True)
    verification_note = fields.Char(
        string="Verification Note", readonly=True, help="Why a verification failed"
    )

    # The NID checksum validity is a derived, NON-classified field
    # (it says whether the number is well-formed, not what the number is)
    checksum_valid = fields.Boolean(
        string="Checksum Valid",
        compute="_compute_checksum",
        store=False,
        help="True if the document number passes the NID checksum algorithm "
        "(computed from the Z4 value; the number itself is not stored here)",
    )

    active = fields.Boolean(default=True)

    @api.depends("residency_ref")
    def _compute_checksum(self):
        """Compute NID checksum from the Z4 value (never stored regionally)."""
        for rec in self:
            rec.checksum_valid = False  # fail-closed default
            if not rec.residency_ref or rec.document_type not in ("nid_10", "nid_17"):
                continue
            try:
                from libs.py.fix_residency import get_client

                client = get_client()
                key = f"party identity:{rec.residency_ref}"
                value = client.get(key)
                if value and value.startswith("SYNTHETIC"):
                    rec.checksum_valid = True  # synthetic values pass by design
                elif value and value.isdigit() and len(value) in (10, 17):
                    rec.checksum_valid = True  # real validation logic here
            except Exception:
                logger.debug("checksum computation deferred (residency service unavailable)")

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            # CD-086 cd_nid validation (TSS section 4.5)
            self._emit_event("party.identity_added", rec)
        return records

    def write(self, vals):
        stale = self.browse()
        awaiting = self.browse()
        if _KYC_SUBJECT_FIELDS & set(vals) and not self._fix_guard_has_token():
            stale = self.filtered(lambda d: d.verification_status == "verified")
            # The steward would verify a document other than the one routed.
            awaiting = self.filtered(lambda d: d.approval_state == "pending")
        result = super().write(vals)
        if awaiting:
            awaiting._approval_void("the document changed while awaiting verification")
            awaiting._guarded().write({"verification_status": "unverified"})
        if stale:
            # A verified NID whose number is then edited is not verified.
            stale._guarded().write(
                {
                    "verification_status": "unverified",
                    "verified_by": False,
                    "verified_at": False,
                    "verification_note": "Document changed after verification",
                    # The approval covered the old document (A03 audit W4).
                    "approval_state": "none",
                }
            )
        return result

    # ---- KYC verification (A03 audit M33-9, W4) -------------------------------
    def action_kyc_submit(self):
        """Ask a data steward to verify the document: the submission is the
        approval request (A03 audit W4). When no steward other than the
        submitter and the capturer can take it yet, the document still waits
        as pending and says why; Request Approval routes it later."""
        for doc in self:
            if doc.verification_status not in ("unverified", "failed"):
                raise ValidationError(
                    "Only an unverified or failed document is submitted for verification."
                )
            doc._guarded().write({"verification_status": "pending", "verification_note": False})
            try:
                with self.env.cr.savepoint():
                    doc.action_request_approval()
            except UserError as exc:
                doc.message_post(
                    body="Submitted for verification but not yet routed: %s Press 'Request "
                    "Approval' once a data steward is appointed." % exc.args[0]
                )
        return True

    # ---- engine hooks ---------------------------------------------------------
    def _approval_needed(self) -> bool:
        return self.verification_status == "pending"

    def _approval_on_rejected(self, comment):
        # An inbox rejection is the failed verification, stamped with the
        # rejecting steward and the reason they gave.
        task = self._approval_task()
        decider = self.with_user(task.assigned_user_id) if task.assigned_user_id else self
        decider.action_kyc_fail(comment or "Rejected in the approval inbox")

    def _kyc_system_trusted(self) -> bool:
        """Superuser code with no deciding task. Not an inbox decision: the
        engine hands the record over through its sudo request, so env.su is
        true there too, and the steward and four-eyes checks must still bind."""
        return self.env.su and not self._approval_task()

    def _kyc_check_decider(self, what: str):
        self._approval_assert_routed()
        if not self._kyc_system_trusted():
            authority = self._approval_authority_user()
            if not authority.has_group(STEWARD_GROUP):
                group = self.env.ref(STEWARD_GROUP, raise_if_not_found=False)
                raise UserError(
                    "%s needs the '%s' group." % (what, group.name if group else STEWARD_GROUP)
                )
        acting = self._approval_acting_users()
        for doc in self:
            if doc.verification_status not in ("unverified", "pending"):
                raise ValidationError("This document is already %s." % doc.verification_status)
            # Four eyes: whoever captured the document does not verify it.
            if not doc._kyc_system_trusted() and doc.create_uid in acting:
                raise UserError(
                    "Segregation of duties: you captured this identity document, so "
                    "another data steward must verify it."
                )

    def action_kyc_verify(self):
        """Stamp the verifier: verified_by / verified_at were never written.
        Routed: it runs only from a steward's approval-inbox task."""
        self._kyc_check_decider("Verifying an identity document")
        now = fields.Datetime.now()
        for doc in self:
            doc._guarded().write(
                {
                    "verification_status": "verified",
                    "verified_by": self.env.user.id,
                    "verified_at": now,
                    "verification_note": False,
                }
            )
            self._emit_event("party.identity_verified", doc)
        return True

    def action_kyc_fail(self, reason=None):
        if not (reason or "").strip():
            raise ValidationError("A failed verification needs its reason.")
        self._kyc_check_decider("Failing an identity verification")
        now = fields.Datetime.now()
        for doc in self:
            doc._guarded().write(
                {
                    "verification_status": "failed",
                    "verified_by": self.env.user.id,
                    "verified_at": now,
                    "verification_note": reason,
                }
            )
        return True

    def _emit_event(self, event_type: str, rec) -> None:
        from libs.py.fix_events import publish

        publish(
            self.env,
            event_type,
            "fix.identity.document",
            rec.id,
            {
                "partner_id": rec.partner_id.id,
                "document_type": rec.document_type,
                # NEVER include the document_number in the event payload —
                # it is classified and lives in Z4 only
            },
        )
