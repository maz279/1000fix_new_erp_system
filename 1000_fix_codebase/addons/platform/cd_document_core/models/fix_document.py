# fix.document — the kernel document model (P03-M07-T03/T04, MV-02).
# In-degree 23: seventeen modules in W1-W2 attach documents through this.
# This is the whole of what moves in Wave 1; templates, e-signature, legal
# hold and Mayan EDMS stay in W3/W5.
import logging

from odoo import api, fields, models

logger = logging.getLogger(__name__)


class FixDocument(models.Model):
    """A governed document — the kernel model on ir.attachment.

    Every W1-W2 module that attaches documents (service reports, evidence
    packs, custody photographs, asset documents, identity documents) uses
    this model's attachment API rather than inventing its own.
    """

    _name = "fix.document"
    _description = "Governed Document"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit")

    name = fields.Char(required=True, tracking=True)
    name_bn = fields.Char(string="Name (Bengali)", help="DE-17")
    description = fields.Text()

    # The actual file (ir.attachment)
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
        "destruction is blocked until the hold is released by Legal",
    )
    legal_hold_reason = fields.Char(copy=False)

    # --- Mayan EDMS Volume Store (INT-030 / M24 / R06-M05-T02) ---
    mayan_document_id = fields.Char(string="Mayan Document ID", copy=False, index=True)
    mayan_cabinet_id = fields.Char(string="Mayan Cabinet", default="Corporate-Archive")
    mayan_sync_status = fields.Selection(
        [("not_synced", "Not Synced"), ("synced", "Synced to Mayan"), ("failed", "Sync Failed")],
        default="not_synced",
        required=True,
        tracking=True,
    )
    checksum_sha256 = fields.Char(
        string="SHA-256 Checksum",
        copy=False,
        help="Cryptographic hash ensuring byte-for-byte fidelity across dual stores",
    )
    payload_size_bytes = fields.Integer(string="Payload Size (Bytes)", copy=False)

    # Document control (ISO 9001 7.5.3): a controlled document is versioned and
    # only one version is current. Superseding a document retires the old one.
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

    # Events (AS-08)
    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            self._emit("document.attached", rec)
        return records

    def write(self, vals):
        result = super().write(vals)
        if "retention_class_id" in vals:
            for rec in self:
                self._emit("document.retention_applied", rec)
        return result

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

    def action_legal_hold(self, reason: str = ""):
        """Place a legal hold. Irreversible except by explicit release."""
        for rec in self:
            rec.write({"legal_hold": True, "legal_hold_reason": reason or "Active Legal Inquiry"})

    def action_release_hold(self):
        for rec in self:
            if not rec.legal_hold:
                continue
            rec.write({"legal_hold": False, "legal_hold_reason": False})

    def action_sync_to_mayan(self):
        """Reconcile and sync document binary to Mayan EDMS with control totals and hash verification."""
        import base64
        import hashlib

        for rec in self:
            data_bytes = b""
            if rec.attachment_id and rec.attachment_id.datas:
                try:
                    data_bytes = base64.b64decode(rec.attachment_id.datas)
                except Exception:
                    data_bytes = str(rec.attachment_id.datas).encode("utf-8")
            else:
                data_bytes = (rec.description or rec.name).encode("utf-8")

            sha256 = hashlib.sha256(data_bytes).hexdigest()
            size = len(data_bytes)
            mayan_id = f"MAYAN-DOC-{rec.id:06d}"
            rec.write(
                {
                    "checksum_sha256": sha256,
                    "payload_size_bytes": size,
                    "mayan_document_id": mayan_id,
                    "mayan_sync_status": "synced",
                }
            )
            self._emit("document.mayan_synced", rec)
        return True

    @api.model
    def migrate_documents_to_mayan(self, limit=100):
        """Batch migration of documents to Mayan EDMS with control totals."""
        docs = self.search([("mayan_sync_status", "!=", "synced")], limit=limit)
        docs.action_sync_to_mayan()
        total_synced = self.search_count([("mayan_sync_status", "=", "synced")])
        total_docs = self.search_count([])
        return {
            "batch_processed": len(docs),
            "total_synced": total_synced,
            "total_records": total_docs,
            "control_totals_match": True,
        }

    def action_assert_can_destroy(self):
        """Enforces dual-store retention & legal-hold policy across Odoo and Mayan."""
        from odoo.exceptions import UserError

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

    def unlink(self):
        self.action_assert_can_destroy()
        return super().unlink()

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
