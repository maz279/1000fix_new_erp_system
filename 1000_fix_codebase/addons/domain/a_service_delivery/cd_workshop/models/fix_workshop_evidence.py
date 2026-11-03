# fix.workshop.evidence — Workshop Evidence Pack (CD-M31-01 / AS-01 Document Attachment API).
# Consumed by Warranty in Phase R05 (MV-02).
#
# A02 workflow audit (2026-11-03), M31-8: a release now requires the evidence
# pack (fix.workshop.job._m31_check_release_evidence), so the record that
# satisfies the gate must itself be evidence: who captured it and when are
# stamped (guarded), and the job, category and document it proves cannot be
# re-pointed after capture (a pre-repair photo relabelled as post-repair).
import logging

from odoo import api, fields, models
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)


class FixWorkshopEvidence(models.Model):
    """A governed evidence record attached to a workshop repair job.

    Strictly delegates binary storage to fix.document via cd_document_core's
    attachment API (AS-01), ensuring residency classification, retention rules,
    and audit trails are maintained centrally.
    """

    _name = "fix.workshop.evidence"
    _description = "Workshop Repair Evidence Record"
    _inherit = ["mail.thread", "mail.activity.mixin", "fix.guarded.mixin"]
    _order = "captured_at desc, id desc"

    # fixed once captured: what the evidence proves, for which job
    _FROZEN_FIELDS = frozenset({"job_id", "evidence_type", "document_id"})

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"captured_by_id", "captured_at"}

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        return locked | self._FROZEN_FIELDS if self else locked

    def write(self, vals):
        touched = self._FROZEN_FIELDS & set(vals)
        if self and touched and not self._fix_guard_open():
            changed = {
                name
                for rec in self
                for name in touched
                if rec._fix_guard_differs(name, vals[name], rec[name])
            }
            if changed:
                raise UserError(
                    "%s cannot be changed on captured evidence: capture a new record "
                    "instead." % ", ".join(sorted(self._fields[n].string for n in changed))
                )
        return super().write(vals)

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        index=True,
        default=lambda self: self.env.company,
    )
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Operating Unit",
        index=True,
    )
    job_id = fields.Many2one(
        "fix.workshop.job",
        string="Workshop Job",
        required=True,
        ondelete="cascade",
        index=True,
    )
    name = fields.Char(
        string="Evidence Title",
        required=True,
        tracking=True,
    )

    evidence_type = fields.Selection(
        [
            ("pre_repair_photo", "Pre-Repair Physical Condition Photo"),
            ("diagnostic_report", "Component Diagnostic Report & Electrical Measurements"),
            ("during_repair_photo", "During-Repair Micro-Soldering / Component Replacement"),
            ("parts_verification", "Old vs New Parts Verification Photograph"),
            ("serial_verification", "Device Serial / IMEI Barcode Scan Proof"),
            ("burn_in_log", "Thermal Chamber & Stress Test Telemetry Log"),
            ("post_repair_photo", "Post-Repair Finished Product Photograph"),
            ("test_log", "Post-Repair Functional Test Log"),
            ("technician_certification", "Technician Calibration & Competency Sign-Off"),
        ],
        string="Evidence Category",
        required=True,
        default="pre_repair_photo",
        tracking=True,
        help="Classification used by warranty claims engine (M09 / R05) to validate claims",
    )

    # AS-01: Governed Document linkage
    document_id = fields.Many2one(
        "fix.document",
        string="Governed Document",
        required=True,
        ondelete="restrict",
        index=True,
        help="The kernel document object managed by cd_document_core",
    )
    attachment_id = fields.Many2one(
        "ir.attachment",
        string="Underlying File",
        related="document_id.attachment_id",
        readonly=True,
    )
    isolation_tier = fields.Selection(
        related="document_id.isolation_tier",
        string="Isolation Tier",
        readonly=True,
    )

    captured_by_id = fields.Many2one(
        "hr.employee",
        string="Captured By",
        default=lambda self: self.env.user.employee_id,
        readonly=True,
        tracking=True,
    )
    captured_at = fields.Datetime(
        string="Timestamp",
        default=fields.Datetime.now,
        required=True,
        readonly=True,
    )
    description = fields.Text(string="Evidence Notes / Observations")

    @api.model
    def create_evidence(
        self,
        job_id: int,
        name: str,
        file_bytes: bytes,
        evidence_type: str,
        description: str = "",
        isolation_tier: str = "T1",
    ) -> "FixWorkshopEvidence":
        """Factory method to attach evidence to a workshop job using cd_document_core.

        Enforces AS-01: No local file table or custom attachment logic allowed.
        """
        job = self.env["fix.workshop.job"].browse(job_id)
        if not job.exists():
            raise UserError(f"Cannot attach evidence: Workshop job ID {job_id} does not exist.")

        # AS-01: Call the unified attachment API in cd_document_core
        doc = self.env["fix.document"].attach(
            name=name,
            datas=file_bytes,
            document_type="evidence_pack",
            res_model="fix.workshop.job",
            res_id=job.id,
            isolation_tier=isolation_tier,
        )

        # the factory stamps the capturer and the time itself (guarded fields)
        created = self._guarded().create(
            {
                "job_id": job.id,
                "name": name,
                "evidence_type": evidence_type,
                "document_id": doc.id,
                "description": description,
                "captured_by_id": self.env.user.employee_id.id
                if self.env.user.employee_id
                else False,
                "captured_at": fields.Datetime.now(),
            }
        )
        # hand back a record without the transition token
        evidence = self.browse(created.ids)

        evidence._emit_evidence_recorded(job, doc)
        return evidence

    def _emit_evidence_recorded(self, job, doc):
        """Emit workshop.evidence.recorded domain event via outbox."""
        from libs.py.fix_events import publish

        publish(
            self.env,
            "workshop.evidence.recorded",
            "fix.workshop.evidence",
            self.id,
            {
                "evidence_id": self.id,
                "job_id": job.id,
                "job_name": job.name,
                "document_id": doc.id,
                "document_name": doc.name,
                "evidence_type": self.evidence_type,
                "captured_by_id": self.captured_by_id.id if self.captured_by_id else False,
                "captured_at": str(self.captured_at),
            },
        )
