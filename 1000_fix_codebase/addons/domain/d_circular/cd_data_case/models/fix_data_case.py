# fix_data_case — M06: data recovery, wipe certificates (P09-M05).
# The most residency-sensitive module: recovered data lives ONLY in Z4.
from odoo import api, fields, models
from odoo.exceptions import AccessDenied, UserError
from odoo.http import request

from libs.py.fix_events import publish

WIPE_METHODS = [
    ("nist_800_88", "NIST SP 800-88 (Clear)"),
    ("nist_800_88_purge", "NIST SP 800-88 (Purge)"),
    ("cryptographic_erase", "Cryptographic Erase"),
    ("physical_destruction", "Physical Destruction"),
]


class FixZ4AccessAudit(models.Model):
    """SC-002 / SC-007: Per-read immutable audit log on every Z4 access.
    Statutory Bangladesh sovereign data access record. Append-only."""

    _name = "fix.z4.access.audit"
    _description = "Z4 Sovereign Data Per-Read Access Audit Log"
    _order = "access_time desc"

    case_id = fields.Many2one(
        "fix.data.recovery.case",
        string="Data Recovery Case",
        required=True,
        ondelete="cascade",
        readonly=True,
        index=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        related="case_id.company_id",
        store=True,
        readonly=True,
        index=True,
    )
    operating_unit_id = fields.Many2one(
        "operating.unit",
        string="Operating Unit",
        related="case_id.operating_unit_id",
        store=True,
        readonly=True,
    )
    user_id = fields.Many2one(
        "res.users",
        string="Accessor",
        required=True,
        default=lambda self: self.env.user,
        readonly=True,
    )
    user_name = fields.Char(string="Accessor Name", readonly=True)
    access_time = fields.Datetime(
        string="Access Timestamp", default=fields.Datetime.now, readonly=True, index=True
    )
    access_type = fields.Selection(
        [
            ("metadata_read", "Metadata Read"),
            ("file_list_read", "Recovered File List Read"),
            ("file_download", "Recovered Data Download"),
            ("preview_read", "Media File Preview"),
            ("export", "Customer Handover Export"),
        ],
        string="Access Type",
        required=True,
        readonly=True,
    )
    purpose = fields.Char(string="Statutory Justification / Purpose", required=True, readonly=True)
    ip_address = fields.Char(string="Client IP Address", readonly=True)
    step_up_verified = fields.Boolean(string="Step-Up 2FA Verified", default=True, readonly=True)
    sha256_audit_hash = fields.Char(string="Audit Entry SHA-256 Hash", readonly=True)

    @api.model_create_multi
    def create(self, vals_list):
        import hashlib
        import time

        for vals in vals_list:
            if not vals.get("user_name"):
                user = self.env["res.users"].browse(vals.get("user_id", self.env.uid))
                vals["user_name"] = user.name or "Technician"
            seed = (
                f"{vals.get('case_id')}-{vals.get('user_id')}-"
                f"{vals.get('access_type')}-{vals.get('purpose')}-"
                f"{vals.get('ip_address')}-{time.time()}"
            )
            vals["sha256_audit_hash"] = hashlib.sha256(seed.encode()).hexdigest()
        return super().create(vals_list)

    def write(self, vals):
        raise UserError(
            "SC-002: fix.z4.access.audit is an immutable statutory sovereign log. "
            "Modifications are strictly prohibited."
        )

    def unlink(self):
        raise UserError(
            "SC-002: fix.z4.access.audit is an immutable statutory sovereign log. "
            "Deletion is strictly prohibited."
        )


class FixDataRecoveryCase(models.Model):
    """Journey 11: data recovery case -> custody -> recovery -> handover ->
    purge certificate. ALL recovered data routes to Z4 (SC-007, FF-09)."""

    _name = "fix.data.recovery.case"
    _description = "Data Recovery Case"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True, copy=False, readonly=True, default=lambda self: "New")
    customer_id = fields.Many2one("res.partner", string="Customer", required=True, index=True)
    device_id = fields.Many2one("fix.device", string="Device", ondelete="set null")
    media_type = fields.Selection(
        [
            ("hdd", "HDD"),
            ("ssd", "SSD"),
            ("usb", "USB Drive"),
            ("sd_card", "SD Card"),
            ("phone", "Phone Storage"),
            ("other", "Other"),
        ],
        required=True,
        default="hdd",
    )
    state = fields.Selection(
        [
            ("new", "New"),
            ("custody", "In Custody"),
            ("recovering", "Recovering"),
            ("recovered", "Recovered"),
            ("handover", "Handover"),
            ("purged", "Purged"),
            ("closed", "Closed"),
            ("unrecoverable", "Unrecoverable"),
        ],
        default="new",
        required=True,
        tracking=True,
    )
    custody_chain = fields.Text(
        string="Chain of Custody Log", help="Every hand-off logged: who, when, where (append-only)"
    )
    residency_zone = fields.Selection(
        [("z4", "Z4 (Residency-Classified)"), ("pending", "Pending Routing")],
        default="pending",
        required=True,
        help="SC-007: recovered customer data lives ONLY in Z4",
    )
    purge_certificate_id = fields.Many2one(
        "fix.data.wipe.certificate",
        string="Purge Certificate",
        ondelete="set null",
        help="The wipe operator's verified certificate; required to purge",
    )
    audit_ids = fields.One2many(
        "fix.z4.access.audit", "case_id", string="Z4 Access Audits", readonly=True
    )
    audit_count = fields.Integer(
        string="Total Access Reads", compute="_compute_audit_count", readonly=True
    )

    @api.depends("audit_ids")
    def _compute_audit_count(self):
        for rec in self:
            rec.audit_count = len(rec.audit_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = (
                self.env["ir.sequence"].next_by_code("fix.data.recovery.case") or "DRC/New"
            )
        return super().create(vals_list)

    def action_take_custody(self, handler):
        """The chain of custody begins: every hand-off is logged."""
        for rec in self:
            timestamp = fields.Datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            entry = f"{timestamp}: custody taken by {handler}"
            rec.custody_chain = (rec.custody_chain or "") + "\n" + entry
            rec.state = "custody"
            publish(
                self.env,
                "data_case.custody_taken",
                "fix.data.recovery.case",
                rec.id,
                {"case": rec.name, "handler": handler},
            )

    def action_log_custody_transfer(self, handler, role="Technician", location="Z4 Lab", notes=""):
        """Structured hand-off in chain of custody."""
        for rec in self:
            timestamp = fields.Datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            note_str = f" - {notes}" if notes else ""
            entry = f"{timestamp}: [Custody Transfer] Handed to {handler} ({role}) at {location}{note_str}"
            rec.custody_chain = (rec.custody_chain or "") + "\n" + entry
            publish(
                self.env,
                "data_case.custody_transferred",
                "fix.data.recovery.case",
                rec.id,
                {"case": rec.name, "handler": handler, "location": location},
            )

    def action_start_recovery(self):
        for rec in self:
            if rec.state != "custody":
                raise UserError("Recovery starts from custody")
            if rec.residency_zone != "z4":
                raise UserError(
                    "SC-007: recovered data must be routed to Z4 BEFORE "
                    "recovery starts. Not transiently, not in a cache."
                )
            rec.state = "recovering"

    def action_recovered(self):
        for rec in self:
            rec.state = "recovered"
            publish(
                self.env,
                "data_case.recovered",
                "fix.data.recovery.case",
                rec.id,
                {"case": rec.name},
            )

    def action_access_recovered_data(
        self,
        step_up_token,
        access_type="file_list_read",
        purpose="Technician File List Inspection",
        ip_address="127.0.0.1",
    ):
        """SC-002: Step-up authentication and per-read access logging for Z4 sovereign data.
        Validates 2FA step-up token and writes an immutable audit log entry."""
        self.ensure_one()
        if self.residency_zone != "z4":
            raise UserError("SC-007: Recovered data exists strictly within Z4 sovereign residency.")
        if self.state not in ("recovering", "recovered", "handover"):
            raise UserError(f"Cannot access recovered data while case is in '{self.state}' state.")

        # Step-up authentication (2FA/TOTP): the ACCESSOR's own auth_totp code,
        # verified cryptographically. There are no fixed bypass tokens and every
        # failure mode is a refusal (fail closed).
        code = str(step_up_token or "").strip()
        if len(code) == 6 and code.isdigit():
            denial = self._step_up_denial(int(code))
        else:
            denial = "a 6-digit authenticator code is required"
        if denial:
            raise UserError(
                "Access Denied: Valid step-up authentication (2FA/TOTP) required "
                f"to access Z4 recovered data (SC-002 / SC-007): {denial}."
            )

        # Per-read immutable audit log
        audit = self.env["fix.z4.access.audit"].create(
            {
                "case_id": self.id,
                "user_id": self.env.uid,
                "access_type": access_type,
                "purpose": purpose,
                "ip_address": ip_address,
                "step_up_verified": True,
            }
        )

        publish(
            self.env,
            "data_case.z4_accessed",
            "fix.data.recovery.case",
            self.id,
            {"case": self.name, "audit_id": audit.id, "access_type": access_type},
        )

        # The recovered files ARE the case's stored attachments: the listing
        # reports what is on record (an empty list when nothing is stored),
        # never invented file names or sizes.
        # read with the accessor's own rights (they just passed step-up)
        attachments = self.env["ir.attachment"].search(
            [("res_model", "=", self._name), ("res_id", "=", self.id)], order="id"
        )
        return {
            "status": "granted",
            "audit_hash": audit.sha256_audit_hash,
            "case": self.name,
            "access_type": access_type,
            "files": [
                {"filename": att.name, "size_bytes": att.file_size, "zone": self.residency_zone}
                for att in attachments
            ],
        }

    def _step_up_denial(self, code):
        """Verify a 6-digit TOTP `code` for the acting user through Odoo's
        auth_totp (`_check_credentials` type "totp": the user's own secret,
        rate-limited, replay-protected). Returns None when verified, else the
        reason for refusing. Fails closed when auth_totp is unavailable, the
        user has no TOTP enrolled, or there is no interactive request."""
        user = self.env.user
        if "totp_enabled" not in user._fields:
            return "two-factor authentication (auth_totp) is not available"
        if not user.sudo().totp_enabled:
            return "the accessor has no authenticator (TOTP) enrolled"
        if not request:
            return "step-up verification requires an interactive session"
        try:
            user._check_credentials({"type": "totp", "token": code}, {"interactive": True})
        except AccessDenied as exc:
            return str(exc) or "the authenticator code was not accepted"
        return None

    def action_handover(self, handler):
        for rec in self:
            if rec.state != "recovered":
                raise UserError("Handover from recovered")
            timestamp = fields.Datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            entry = f"{timestamp}: handed over by {handler}"
            rec.custody_chain = (rec.custody_chain or "") + "\n" + entry
            rec.state = "handover"

    def action_purge(self, certificate=None):
        """Close the case on the wipe operator's VERIFIED fix.data.wipe.certificate
        (its evidence - sector count, method, tool log - is entered by the
        operator and hash-verified there). Nothing is certified here: a case
        without a verified certificate cannot be marked purged. The statutory
        processing record is preserved even after the data is destroyed
        (NFR-095: the certificate is statutory_record_retained)."""
        for rec in self:
            if rec.state != "handover":
                raise UserError("Purge from handover")
            cert = certificate or rec.purge_certificate_id
            if not cert:
                raise UserError(
                    "Purge needs the wipe operator's fix.data.wipe.certificate "
                    "(sector count, method and wipe-tool log)"
                )
            if cert.sanitization_status != "verified":
                raise UserError(
                    "Wipe certificate %s is '%s': only a VERIFIED certificate "
                    "closes a purge" % (cert.name, cert.sanitization_status)
                )
            if not cert.statutory_record_retained:
                raise UserError("NFR-095: the purge certificate must be statutorily retained")
            rec.write({"state": "purged", "purge_certificate_id": cert.id})
            publish(
                self.env,
                "data_case.purged",
                "fix.data.recovery.case",
                rec.id,
                {"certificate": cert.name, "verification_hash": cert.verification_hash},
            )


class FixDataWipeCertificate(models.Model):
    """The secure data-wipe and destruction certificate (P09-M05-T02).
    Consumed by M14 trade-in and M18 e-waste."""

    _name = "fix.data.wipe.certificate"
    _description = "Data Wipe Certificate"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    operating_unit_id = fields.Many2one("operating.unit", string="Operating Unit")
    name = fields.Char(required=True, copy=False, readonly=True, default=lambda self: "New")
    device_id = fields.Many2one("fix.device", string="Device", ondelete="set null")
    serial_number = fields.Char(string="Storage Media Serial Number")
    technician_id = fields.Many2one(
        "res.users", string="Certifying Technician", default=lambda self: self.env.user
    )
    # Operator inputs: nothing defaults to a plausible-looking wipe result.
    method = fields.Selection(WIPE_METHODS, required=True)
    sector_count = fields.Integer(
        string="Total Overwritten Sectors",
        help="As reported by the wipe tool (not applicable to physical destruction)",
    )
    duration_seconds = fields.Integer(string="Sanitization Duration (s)")
    tool_name = fields.Char(string="Wipe Tool / Version")
    wipe_log_attachment_id = fields.Many2one(
        "ir.attachment",
        string="Wipe Tool Output / Log",
        ondelete="restrict",
        help="The wipe tool's report (or destruction evidence) the certificate attests to",
    )
    sanitization_status = fields.Selection(
        [
            ("pending_verification", "Pending Verification"),
            ("verified", "Pass - Evidence Verified"),
            ("failed", "Sanitization Incomplete"),
        ],
        default="pending_verification",
        required=True,
        readonly=True,
        tracking=True,
    )
    verified_by_id = fields.Many2one("res.users", string="Verified By", readonly=True)
    verified_at = fields.Datetime(readonly=True)
    statutory_record_retained = fields.Boolean(
        string="Statutory Processing Record Retained",
        default=True,
        readonly=True,
        help="NFR-095: Preserved permanently in statutory archive even post-purge",
    )
    certified_by = fields.Char(string="Certified By")
    certified_at = fields.Datetime(default=fields.Datetime.now, readonly=True)
    verification_hash = fields.Char(
        compute="_compute_verification_hash",
        store=True,
        readonly=True,
        help="SHA-256 over the wipe evidence (tool log content, method, sector "
        "count, media serial): anyone holding the log can re-derive it. Empty "
        "until evidence is attached.",
    )

    _EVIDENCE_FIELDS = (
        "method",
        "sector_count",
        "serial_number",
        "wipe_log_attachment_id",
        "tool_name",
        "duration_seconds",
    )

    def _evidence_digest(self) -> str:
        """sha256 over the actual evidence; '' when there is no log."""
        import hashlib

        self.ensure_one()
        log = self.wipe_log_attachment_id
        if not log:
            return ""
        digest = hashlib.sha256()
        digest.update(log.sudo().raw or b"")
        for part in (self.method, self.sector_count, self.serial_number):
            digest.update(b"|" + str(part or "").encode())
        return digest.hexdigest()

    @api.depends("wipe_log_attachment_id", "method", "sector_count", "serial_number")
    def _compute_verification_hash(self):
        for rec in self:
            rec.verification_hash = rec._evidence_digest() or False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = (
                self.env["ir.sequence"].next_by_code("fix.data.wipe.certificate") or "DWC/New"
            )
            if not vals.get("certified_by"):
                vals["certified_by"] = self.env.user.name or False
            # a certificate is never BORN verified: verification checks evidence
            vals.pop("sanitization_status", None)
        records = super().create(vals_list)
        # fix the evidence hash NOW (not lazily at first read): a log edited
        # between attachment and verification is then detected as tampering
        records.mapped("verification_hash")
        return records

    def write(self, vals):
        evidence_change = any(f in vals for f in self._EVIDENCE_FIELDS)
        if evidence_change:
            for rec in self:
                if rec.sanitization_status == "verified":
                    raise UserError(
                        "Certificate %s is verified: its wipe evidence is frozen" % rec.name
                    )
        res = super().write(vals)
        if evidence_change:
            self.mapped("verification_hash")
        return res

    def _evidence_gaps(self) -> list[str]:
        self.ensure_one()
        gaps = []
        if not self.method:
            gaps.append("wipe method")
        if self.method != "physical_destruction" and self.sector_count <= 0:
            gaps.append("overwritten sector count from the wipe tool")
        if not self.wipe_log_attachment_id:
            gaps.append("wipe tool output / log attachment")
        elif not self.wipe_log_attachment_id.sudo().raw:
            gaps.append("a non-empty wipe tool log")
        return gaps

    def action_verify(self):
        """Verify the certificate against the operator's evidence. Refuses
        (fail closed) when any evidence is missing; the hash is re-derived
        from the stored log content."""
        for rec in self:
            if rec.sanitization_status != "pending_verification":
                raise UserError(
                    "Only a pending certificate can be verified (%s is '%s')"
                    % (rec.name, rec.sanitization_status)
                )
            gaps = rec._evidence_gaps()
            if gaps:
                raise UserError(
                    "Certificate %s cannot be verified - missing: %s" % (rec.name, ", ".join(gaps))
                )
            if rec.verification_hash != rec._evidence_digest():
                raise UserError("Certificate %s: evidence hash mismatch" % rec.name)
            super(FixDataWipeCertificate, rec).write(
                {
                    "sanitization_status": "verified",
                    "verified_by_id": self.env.uid,
                    "verified_at": fields.Datetime.now(),
                }
            )
        return True

    def action_mark_failed(self):
        for rec in self:
            if rec.sanitization_status == "verified":
                raise UserError("A verified certificate cannot be failed")
            super(FixDataWipeCertificate, rec).write({"sanitization_status": "failed"})
        return True

    def unlink(self):
        for rec in self:
            if rec.statutory_record_retained:
                raise UserError(
                    "NFR-095: Data Wipe Certificates are permanent statutory processing "
                    "records and cannot be deleted."
                )
        return super().unlink()
