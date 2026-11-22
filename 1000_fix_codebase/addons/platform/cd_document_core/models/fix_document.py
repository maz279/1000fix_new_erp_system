# fix.document — the kernel document model (P03-M07-T03/T04, MV-02).
# In-degree 23: seventeen modules in W1-W2 attach documents through this.
#
# A10 remediation (2026-11-05, report §6 D2 / P1-1, findings M24-5..-9):
# the document kernel had no roles, no controlled-document workflow, no
# retention enforcement and a "sync" that invented its evidence. A plain
# internal user could release a litigation hold, expire a document inside
# retention, destroy it with no record, re-activate a superseded version and
# swap a signed document's file. The lifecycle fields are now guarded:
# they move through the actions and the daily cron only.
import hashlib
import logging

from odoo import api, fields, models
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)

RECORDS_GROUP = "cd_document_core.group_document_records"

CONTROL_STATES = [
    ("draft", "Draft"),
    ("in_review", "In Review"),
    ("approved", "Approved"),
    ("published", "Published"),
    ("superseded", "Superseded"),
]

# The file-and-classification fields that freeze once a document is held,
# sealed for signature, or published as a controlled version (M24-9: the
# help text "a legal-hold document is frozen" is finally true).
_CONTENT_FIELDS = (
    "attachment_id",
    "name",
    "name_bn",
    "description",
    "document_type",
    "retention_class_id",
    "is_residency_classified",
)

# Controlled-document lifecycle fields (M24-5): version, lineage and
# currency move only through the workflow actions.
_CONTROL_FIELDS = ("version", "previous_version_id", "superseded_by_id", "is_current")


class FixDocument(models.Model):
    """A governed document — the kernel model on ir.attachment.

    Every W1-W2 module that attaches documents (service reports, evidence
    packs, custody photographs, assets, identity documents) uses this model's
    attachment API rather than inventing its own.

    A document is either operational (born current, `is_controlled=False`)
    or controlled (born draft: an author writes it, a Document Controller
    who is not the author approves it through M63, publishing supersedes the
    previous version — ISO 9001 7.5.3).
    """

    _name = "fix.document"
    _description = "Governed Document"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.approvable.mixin"]
    _order = "create_date desc"

    # M63: a controlled document is approved by a Document Controller, never
    # its own author (BRU-DMS-10). No DOFA tier — the deciding group is fixed.
    _approval_apply_method = "action_approve"
    _approval_group = "cd_document_core.group_document_controller"
    _approval_routed = True

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit")

    name = fields.Char(required=True, tracking=True)
    name_bn = fields.Char(string="Name (Bengali)", help="DE-17")
    description = fields.Text()

    # The actual file (ir.attachment)
    # A person's upload on the workspace form: the file becomes the attachment below.
    upload_file = fields.Binary(string="File", store=False)
    upload_filename = fields.Char(string="File Name", store=False)
    attachment_id = fields.Many2one(
        "ir.attachment",
        string="Attachment",
        required=True,
        ondelete="restrict",
        index=True,
        help="The underlying file — stored in the object store (D-028 Ceph)",
    )

    # Retention (loaded as content per LG-009, not as a M60 dependency)
    retention_class_id = fields.Many2one(
        "fix.retention.class",
        string="Retention Class",
        help="Determines how long this document is kept and what happens at expiry",
    )
    retention_expires = fields.Date(
        string="Retention Expires", compute="_compute_retention", store=True
    )

    # Document classification
    document_type = fields.Selection(
        [
            ("service_report", "Service Report"),
            ("evidence_pack", "Evidence Pack"),
            ("custody_photo", "Custody Photograph"),
            ("identity_document", "Identity Document"),
            ("asset_document", "Asset Document"),
            ("warranty_card", "Warranty Card"),
            ("invoice", "Invoice"),
            ("contract", "Contract"),
            ("signature_certificate", "Signature Certificate"),
            ("destruction_certificate", "Destruction Certificate"),
            ("other", "Other"),
        ],
        required=True,
        default="other",
        tracking=True,
    )

    # Residency classification (AS-14): some documents contain S3 data
    is_residency_classified = fields.Boolean(
        default=False,
        tracking=True,
        help="If True, the document contains residency-classified data and is "
        "stored in Z4 via the residency service (FF-09)",
    )

    # Link to any record (polymorphic)
    res_model = fields.Char(string="Linked Model", index=True)
    res_id = fields.Integer(string="Linked Record ID", index=True)

    # Access control
    isolation_tier = fields.Selection(
        [
            ("T1", "T1 — Internal"),
            ("T2", "T2 — Branch-scoped"),
            ("T3", "T3 — Role-scoped"),
            ("T5", "T5 — Residency-classified"),
        ],
        default="T1",
        required=True,
        help="The minimum isolation tier required to read this document",
    )

    active = fields.Boolean(default=True, tracking=True)

    # --- M24 completion (P06-M08-T01): templates + legal hold ---
    template_id = fields.Many2one(
        "fix.document.template",
        string="Generated From",
        readonly=True,
        index=True,
        help="The template this document was generated from (the template engine, CD-M24-05)",
    )
    legal_hold = fields.Boolean(
        default=False,
        tracking=True,
        copy=False,
        help="A legal-hold document is frozen: retention cannot expire it and "
        "destruction is blocked until the hold is released by Records/Legal "
        "with the matter reference on file",
    )
    legal_hold_reason = fields.Char(copy=False)
    # Sealed by the e-signature envelope at send (cd_esignature): the file a
    # signature covers can never be swapped afterwards. The flag lives here
    # because cd_esignature depends on this module, not the other way round.
    signature_locked = fields.Boolean(
        copy=False,
        tracking=True,
        help="An e-signature envelope has been sent over this document: its "
        "file and classification are frozen",
    )

    # --- Mayan EDMS Volume Store (INT-030 / M24 / R06-M05-T02) ---
    mayan_document_id = fields.Char(string="Mayan Document ID", copy=False, index=True)
    mayan_cabinet_id = fields.Char(string="Mayan Cabinet", default="Corporate-Archive")
    mayan_sync_status = fields.Selection(
        [("not_synced", "Not Synced"), ("synced", "Synced to Mayan"), ("failed", "Sync Failed")],
        default="not_synced",
        required=True,
        tracking=True,
    )
    # Server-computed integrity fingerprint over the attachment bytes. It was
    # a typed field anyone could set (M24-8): now it is derived, so a swap is
    # visible and nothing can claim an integrity it did not compute.
    checksum_sha256 = fields.Char(
        string="SHA-256 Checksum",
        compute="_compute_integrity",
        store=True,
        help="Cryptographic hash of the attachment bytes, computed by the server",
    )
    payload_size_bytes = fields.Integer(
        string="Payload Size (Bytes)", compute="_compute_integrity", store=True
    )

    # --- Controlled documents (ISO 9001 7.5.3, M24-5 / P1-1) ---
    is_controlled = fields.Boolean(
        default=False,
        tracking=True,
        help="A controlled document (policy, procedure, form) moves through "
        "draft → review → approval (a Document Controller, never the author) "
        "→ publication; publishing supersedes the previous version.",
    )
    control_state = fields.Selection(
        CONTROL_STATES,
        default="draft",
        required=True,
        tracking=True,
        copy=False,
    )
    version = fields.Char(default="1.0", required=True, tracking=True)
    is_current = fields.Boolean(
        default=True,
        tracking=True,
        help="Only the current version may be issued; superseded versions stay readable.",
    )
    previous_version_id = fields.Many2one(
        "fix.document",
        string="Supersedes",
        ondelete="set null",
        copy=False,
    )
    superseded_by_id = fields.Many2one(
        "fix.document",
        string="Superseded by",
        ondelete="set null",
        copy=False,
    )
    approved_by_id = fields.Many2one("res.users", string="Approved By", copy=False, readonly=True)
    approved_on = fields.Date(copy=False, readonly=True)
    published_on = fields.Date(copy=False, readonly=True)

    state = fields.Selection(
        [
            ("active", "Active"),
            ("expired", "Retention Expired"),
            ("pending_destruction", "Pending Destruction"),
            ("destroyed", "Destroyed"),
        ],
        default="active",
        required=True,
        tracking=True,
    )

    # ------------------------------------------------------------------ guard
    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "legal_hold",
            "legal_hold_reason",
            "signature_locked",
            "control_state",
            "is_current",
            "superseded_by_id",
            "mayan_document_id",
            "mayan_sync_status",
        }

    def _record_locked(self) -> bool:
        """Content freezes once the record is held, sealed for signature or
        published as a controlled version (M24-9)."""
        self.ensure_one()
        return bool(
            self.legal_hold
            or self.signature_locked
            or (self.is_controlled and self.control_state in ("published", "superseded"))
        )

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and all(rec._record_locked() for rec in self):
            locked |= {n for n in _CONTENT_FIELDS if n in self._fields}
        return locked

    def write(self, vals):
        # Record-level freezes the mixin cannot express (they depend on the
        # record's own state, not the model): content fields under hold or
        # signature seal, lifecycle fields of a controlled line.
        if self and not self._fix_guard_open():
            touched = (set(_CONTENT_FIELDS) | set(_CONTROL_FIELDS)) & set(vals)
            if touched:
                for rec in self:
                    offenders = [n for n in touched if rec._fix_guard_differs(n, vals[n], rec[n])]
                    if offenders and rec._record_locked():
                        self._fix_guard_refuse(offenders)
        result = super().write(vals)
        if "retention_class_id" in vals:
            for rec in self:
                self._emit("document.retention_applied", rec)
        return result

    @api.model_create_multi
    def create(self, vals_list):
        # The integrity fingerprint is server-computed; a caller-typed value
        # never reaches the record (it would be refused as a guarded compute).
        for vals in vals_list:
            vals.pop("checksum_sha256", None)
            vals.pop("payload_size_bytes", None)
            upload = vals.pop("upload_file", None)
            filename = vals.pop("upload_filename", None)
            if upload and not vals.get("attachment_id"):
                vals.setdefault("name", filename or "Document")
                vals["attachment_id"] = (
                    self.env["ir.attachment"]
                    .create(
                        {
                            "name": filename or vals["name"],
                            "datas": upload,
                            "res_model": "fix.document",
                        }
                    )
                    .id
                )
        records = super().create(vals_list)
        for rec in records:
            self._emit("document.attached", rec)
        return records

    @api.depends("attachment_id", "attachment_id.datas")
    def _compute_integrity(self):
        import base64

        for rec in self:
            raw = b""
            if rec.attachment_id and rec.attachment_id.datas:
                try:
                    raw = base64.b64decode(rec.attachment_id.datas)
                except Exception:
                    raw = str(rec.attachment_id.datas).encode("utf-8")
            rec.checksum_sha256 = hashlib.sha256(raw).hexdigest() if raw else False
            rec.payload_size_bytes = len(raw)

    @api.depends("retention_class_id", "create_date", "legal_hold")
    def _compute_retention(self):
        from datetime import date, timedelta

        for rec in self:
            if rec.legal_hold:
                # A legal hold freezes the clock: no expiry while held.
                rec.retention_expires = False
                continue
            if rec.retention_class_id and rec.retention_class_id.retention_years:
                base = rec.create_date.date() if rec.create_date else date.today()
                rec.retention_expires = base + timedelta(
                    days=365 * rec.retention_class_id.retention_years
                )
            else:
                rec.retention_expires = False

    # --------------------------------------------------- controlled documents
    def action_submit_review(self, justification=None):
        """The author sends their draft for approval (draft → in_review).

        The request routes through M63 to a Document Controller; the engine
        never routes it to the requester or the record's creator."""
        for rec in self:
            if not rec.is_controlled:
                raise UserError(
                    "%s is not a controlled document; there is nothing to review." % rec.name
                )
            if rec.control_state != "draft":
                raise UserError(
                    "Only a DRAFT controlled document goes to review — %s is %s."
                    % (rec.name, rec.control_state)
                )
            rec._guarded().write({"control_state": "in_review"})
            rec.action_request_approval(justification=justification)
            rec.message_post(body="Submitted for approval: %s" % (justification or "(no note)"))
        return True

    def action_approve(self):
        """The M63 apply method: a Document Controller (never the author)
        approves a document in review. Called by the approval engine from the
        approver's inbox; a direct press is refused."""
        self._approval_assert_routed()
        trusted = self.env.su and not self._approval_task()
        authority = self._approval_authority_user()
        acting = self._approval_acting_users()
        for rec in self:
            if rec.control_state != "in_review":
                raise UserError(
                    "Approval lands on a document IN REVIEW — %s is %s."
                    % (rec.name, rec.control_state)
                )
            if not trusted:
                if not authority.has_group("cd_document_core.group_document_controller"):
                    raise UserError(
                        "A controlled document is approved by a Document Controller, "
                        "which %s is not." % authority.name
                    )
                if acting & (rec.create_uid | rec.sudo().approved_by_id):
                    raise UserError(
                        "Segregation of duties: the author never approves their own "
                        "document (BRU-DMS-10)."
                    )
            rec._guarded().write(
                {
                    "control_state": "approved",
                    "approved_by_id": self.env.user.id,
                    "approved_on": fields.Date.context_today(rec),
                }
            )
            rec.message_post(body="Approved by %s." % self.env.user.name)
        return True

    def action_publish(self):
        """Issue the approved version: it becomes the current one and every
        published version of the same line is superseded (M24-5 — v2 must
        retire v1; two currents can no longer exist)."""
        for rec in self:
            if not rec.is_controlled:
                raise UserError("%s is not a controlled document." % rec.name)
            if rec.control_state != "approved":
                raise UserError(
                    "Publishing follows approval — %s is %s." % (rec.name, rec.control_state)
                )
            today = fields.Date.context_today(rec)
            rec._guarded().write(
                {"control_state": "published", "is_current": True, "published_on": today}
            )
            line = self.search(
                [
                    ("id", "!=", rec.id),
                    ("name", "=", rec.name),
                    ("is_controlled", "=", True),
                    ("control_state", "=", "published"),
                ]
            )
            if rec.previous_version_id:
                line |= rec.previous_version_id
            for old in line - rec:
                old._guarded().write(
                    {
                        "control_state": "superseded",
                        "is_current": False,
                        "superseded_by_id": rec.id,
                    }
                )
                old.message_post(body="Superseded by version %s." % rec.version)
            rec.message_post(body="Version %s published by %s." % (rec.version, self.env.user.name))
        return True

    def action_new_revision(self, version=None):
        """The author starts the next version: a new DRAFT of the same line.
        The published version stays current until the new one is published."""
        drafts = self.env["fix.document"]
        for rec in self:
            if not rec.is_controlled or rec.control_state != "published" or not rec.is_current:
                raise UserError(
                    "A new revision starts from the PUBLISHED, CURRENT version of a "
                    "controlled line — %s is %s." % (rec.name, rec.control_state)
                )
            next_version = version or rec._next_version()
            # The draft does not claim currency: the published version stays
            # THE current one until the revision is published. is_current is
            # guarded, so the draft is created through the transition token.
            draft = rec._guarded().create(
                {
                    "name": rec.name,
                    "name_bn": rec.name_bn,
                    "document_type": rec.document_type,
                    "attachment_id": rec.attachment_id.id,
                    "retention_class_id": rec.retention_class_id.id,
                    "isolation_tier": rec.isolation_tier,
                    "is_controlled": True,
                    "version": next_version,
                    "is_current": False,
                    "previous_version_id": rec.id,
                }
            )
            drafts |= draft.with_env(self.env)
            rec.message_post(body="Revision %s started." % next_version)
        return {
            "reporter": "Draft created",
            "note": "%d draft revision(s): %s"
            % (len(drafts), ", ".join("%s v%s" % (d.name, d.version) for d in drafts)),
        }

    def _next_version(self):
        try:
            return "%.1f" % (
                (float(self.version or "1") + 0.1) if "." in (self.version or "") else 1.1
            )
        except ValueError:
            return "next"

    # ---------------------------------------------------------- legal hold
    def _require_records_officer(self, why):
        if self.env.su or self.env.user.has_group(RECORDS_GROUP):
            return
        raise UserError(
            "Only a Records Officer (Legal/Records) may %s. Appoint the group "
            "%s first (A10 D2)." % (why, RECORDS_GROUP)
        )

    def action_legal_hold(self, matter_ref: str = ""):
        """Records/Legal places a hold with the matter reference on file
        (M24-6). The hold and its reason are stamped, never typed."""
        self._require_records_officer("place a legal hold")
        Hold = self.env["fix.legal.hold"].sudo()
        for rec in self:
            if not matter_ref or not matter_ref.strip():
                raise UserError(
                    "State the matter reference (case, notice or inquiry) the hold on "
                    "'%s' answers to." % rec.name
                )
            if rec.legal_hold:
                raise UserError("'%s' is already on hold." % rec.name)
            rec._guarded().write({"legal_hold": True, "legal_hold_reason": matter_ref.strip()})
            Hold.create(
                {
                    "document_id": rec.id,
                    "matter_ref": matter_ref.strip(),
                    "placed_by_id": self.env.user.id,
                    "placed_on": fields.Date.context_today(rec),
                }
            )
            rec.message_post(
                body="Legal hold placed (%s) by %s." % (matter_ref, self.env.user.name)
            )
        return True

    def action_release_hold(self, reason: str = ""):
        """Only Records/Legal releases a hold, and only with a recorded
        reason (M24-6: any-user release was the disposal bypass)."""
        self._require_records_officer("release a legal hold")
        if not reason or not reason.strip():
            raise UserError("State why the hold is released — the release is part of the record.")
        Hold = self.env["fix.legal.hold"].sudo()
        for rec in self:
            if not rec.legal_hold:
                continue
            open_holds = Hold.search([("document_id", "=", rec.id), ("state", "=", "held")])
            if not open_holds:
                raise UserError(
                    "'%s' shows a hold flag with no hold on the register — resolve the "
                    "register first." % rec.name
                )
            rec._guarded().write({"legal_hold": False, "legal_hold_reason": False})
            open_holds.write(
                {
                    "released_by_id": self.env.user.id,
                    "released_on": fields.Date.context_today(rec),
                    "release_reason": reason.strip(),
                    "state": "released",
                }
            )
            rec.message_post(
                body="Legal hold released by %s: %s" % (self.env.user.name, reason.strip())
            )
        return True

    # ---------------------------------------------------------- retention
    @api.model
    def cron_retention_enforcement(self):
        """The daily retention sweep (M24-7). Eligibility is computed by the
        system — never typed: a document whose class has elapsed, that is not
        under legal hold and is still active becomes EXPIRED and its review is
        announced. Destruction stays a Records decision on the register."""
        today = fields.Date.today()
        docs = self.search(
            [
                ("state", "=", "active"),
                ("legal_hold", "=", False),
                ("retention_expires", "!=", False),
                ("retention_expires", "<=", today),
            ]
        )
        for rec in docs:
            rec._guarded().write({"state": "expired"})
            self._emit("document.retention_due", rec)
            rec.message_post(
                body="Retention elapsed on %s (class %s): review for disposal."
                % (rec.retention_expires, rec.retention_class_id.name or "—")
            )
        return len(docs)

    def consume_document_retention_due(self, env_from_relay):
        """In-Odoo consumer for document.retention_due (relay-only): keeps a
        visible trace on the document thread. External consumers (Mayan, BI)
        read the transactional outbox."""
        if not self.env.su:
            raise UserError("The retention consumer runs from the event relay only.")
        doc = self.browse(int(env_from_relay.get("aggregate_id") or 0)).exists()
        if doc:
            doc.message_post(body="Retention review announced by the retention sweep.")
        return True

    def action_assert_can_destroy(self):
        """Enforces dual-store retention & legal-hold policy across Odoo and Mayan."""
        for rec in self:
            if rec.legal_hold:
                raise UserError(
                    f"Document '{rec.name}' is under active legal hold ('{rec.legal_hold_reason or 'Legal Notice'}'). "
                    "Destruction is strictly blocked across both Odoo kernel and Mayan EDMS volume store."
                )
            if rec.state not in ("expired", "pending_destruction"):
                raise UserError(
                    f"Document '{rec.name}' has not reached retention expiry. "
                    "Premature destruction violates M24 compliance."
                )
        return True

    def action_dispose(self, method: str = "secure_wipe"):
        """Defensible disposal (M24-7): a Records Officer disposes an expired
        document — a permanent disposal record and a destruction certificate
        are created, the file is wiped and only then may the row be removed."""
        import base64

        self._require_records_officer("dispose of a document")
        Disposal = self.env["fix.disposal.record"].sudo()
        for rec in self:
            rec.action_assert_can_destroy()
            # A10 deep audit (2026-11-22, A2-F04): seal WHAT is being destroyed
            # BEFORE the bytes go — the surviving row's checksum recomputes to
            # False after the wipe, so the register and the certificate are the
            # only places the destroyed payload's fingerprint lives.
            sealed_hash = rec.checksum_sha256 or ""
            raw = rec.attachment_id.sudo().datas if rec.attachment_id else False
            sealed_size = len(base64.b64decode(raw)) if raw else 0
            # the certificate files through the service env: a Records Officer
            # decides the disposal, but the attachment store is not theirs
            certificate = self.sudo().attach(
                name="Destruction Certificate — %s" % rec.name,
                datas=base64.b64encode(
                    (
                        "Disposed %s — %s\nPayload sha256 %s (%d bytes)."
                        % (fields.Datetime.now(), method, sealed_hash or "—", sealed_size)
                    ).encode("utf-8")
                ),
                document_type="destruction_certificate",
                res_model="fix.document",
                res_id=rec.id,
            )
            disposal = Disposal.create(
                {
                    "name": "DISPOSAL/%s" % rec.name,
                    "document_id": rec.id,
                    "method": method,
                    "certificate_doc_id": certificate.id,
                    "performed_by_id": self.env.user.id,
                    "payload_sha256": sealed_hash,
                    "payload_size": sealed_size,
                }
            )
            if rec.attachment_id:
                rec.attachment_id.sudo().write({"datas": False})
            rec._guarded().write({"state": "destroyed", "active": False})
            rec.message_post(
                body="Disposed by %s (%s); disposal register %s, certificate attached."
                % (self.env.user.name, method, disposal.name)
            )
        return True

    def unlink(self):
        # The register is permanent (M24-7): a document leaves the system only
        # through a disposal with its record and certificate already on file —
        # and a destroyed row stays, because it anchors its disposal record.
        for rec in self:
            if rec.state == "destroyed":
                raise UserError(
                    "'%s' is destroyed: its row anchors the permanent disposal register." % rec.name
                )
            rec.action_assert_can_destroy()
            if (
                not self.env["fix.disposal.record"]
                .sudo()
                .search_count([("document_id", "=", rec.id)])
            ):
                raise UserError(
                    "'%s' may be removed only through a recorded disposal (action_dispose) — "
                    "a bare delete leaves no register entry." % rec.name
                )
        return super().unlink()

    # ---------------------------------------------------------- Mayan EDMS
    def _mayan_config(self):
        url = self.env["ir.config_parameter"].sudo().get_param("mayan_edms.base_url", "").strip()
        token = self.env["ir.config_parameter"].sudo().get_param("mayan_edms.token", "").strip()
        return url, token

    def action_sync_to_mayan(self):
        """Sync the document binary to Mayan EDMS (M24-8 honesty).

        The old action called no Mayan API, invented an id and reported
        'synced'. Now: no configured endpoint → refusal, status stays
        not_synced; a configured endpoint must ACKNOWLEDGE the upload before
        the record says synced."""
        import base64

        import requests

        url, token = self._mayan_config()
        if not url or not token:
            for rec in self:
                rec.message_post(
                    body="Mayan sync refused: no endpoint configured "
                    "(ir.config_parameter mayan_edms.base_url / mayan_edms.token)."
                )
            raise UserError(
                "Mayan EDMS is not configured, so no document may be reported as "
                "synced. Set mayan_edms.base_url and mayan_edms.token first (M24-8)."
            )
        results = []
        for rec in self:
            raw = base64.b64decode(rec.attachment_id.datas or b"") if rec.attachment_id else b""
            if not raw:
                rec._guarded().write({"mayan_sync_status": "failed"})
                results.append(False)
                continue
            try:
                response = requests.post(
                    "%s/api/v4/documents/" % url.rstrip("/"),
                    headers={"Authorization": "Token %s" % token},
                    files={"file": (rec.name, raw)},
                    timeout=15,
                )
                payload = (
                    response.json()
                    if response.headers.get("content-type", "").startswith("application/json")
                    else {}
                )
                remote_id = str(payload.get("id") or "")
            except Exception as exc:  # network errors are honest failures
                logger.warning("Mayan sync failed for %s: %s", rec.name, exc)
                remote_id = ""
            if remote_id:
                rec._guarded().write(
                    {"mayan_document_id": remote_id, "mayan_sync_status": "synced"}
                )
                self._emit("document.mayan_synced", rec)
                results.append(True)
            else:
                rec._guarded().write({"mayan_sync_status": "failed"})
                results.append(False)
        if not all(results):
            raise UserError(
                "Mayan did not acknowledge %d of %d document(s); those stay "
                "marked failed — a document is never 'synced' without a remote "
                "acknowledgement." % (results.count(False), len(results))
            )
        return True

    @api.model
    def migrate_documents_to_mayan(self, limit=100):
        """Batch migration to Mayan EDMS with honest control totals
        (M24-8: the old method hard-coded control_totals_match: True)."""
        docs = self.search([("mayan_sync_status", "!=", "synced")], limit=limit)
        ok = 0
        failed = []
        for rec in docs:
            try:
                with self.env.cr.savepoint():
                    rec.action_sync_to_mayan()
                ok += 1
            except UserError:
                failed.append(rec.name)
        return {
            "batch_processed": len(docs),
            "synced_this_batch": ok,
            "failed_this_batch": len(failed),
            "total_synced": self.search_count([("mayan_sync_status", "=", "synced")]),
            "total_records": self.search_count([]),
            "control_totals_match": ok + len(failed) == len(docs),
        }

    # The attachment API (P03-M07-T06) — consumed by every W1-W2 module
    @api.model
    def attach(
        self,
        name: str,
        datas: bytes,
        document_type: str,
        res_model: str = "",
        res_id: int = 0,
        retention_class_id: int | None = None,
        isolation_tier: str = "T1",
    ) -> "FixDocument":
        """The one API for attaching documents.

        Every W1-W2 module calls this instead of creating ir.attachment
        directly. Without this, seventeen ad-hoc implementations emerge and
        Wave 3 becomes a migration of them all.
        """
        attachment = self.env["ir.attachment"].create(
            {
                "name": name,
                "datas": datas,
                "res_model": "fix.document",
            }
        )
        return self.create(
            {
                "name": name,
                "attachment_id": attachment.id,
                "document_type": document_type,
                "res_model": res_model,
                "res_id": res_id,
                "retention_class_id": retention_class_id,
                "isolation_tier": isolation_tier,
            }
        )

    def _emit(self, event_type: str, rec) -> None:
        from libs.py.fix_events import publish

        publish(
            self.env,
            event_type,
            "fix.document",
            rec.id,
            {
                "name": rec.name,
                "document_type": rec.document_type,
                "is_residency_classified": rec.is_residency_classified,
            },
        )
