# fix_data_case_secure — A02 audit P1/P2 for M06 (2026-11-04): the lab steps
# the audit found missing or typed, as server-side transitions.
#
#   * Z4 through named staff (M06-P2): each case names its technician and its
#     Z4 custodian; only they work the recovered data (start, attempts,
#     imaging, recovered, handover, the step-up read);
#   * imaging as a step (M06-P2): the source and image SHA-256 are recorded by
#     an action, verified by a second person who recomputes the image hash,
#     then frozen; a case is marked recovered only on a verified image. The
#     hash was a free-text field the P03 form could write;
#   * handover to a verified recipient (M06-P2): a recipient of the customer,
#     a one-time code or the recipient's ID number, a signed receipt attached
#     to the case, and the target drive's serial confirmed. It took free text;
#   * retention (B4): a handover starts the retention clock; a daily job
#     purges a case past its retention ONLY on a verified wipe certificate for
#     its media (the P0 gate inside action_purge), and otherwise flags it.
#   * M06 sub-module capture (2026-11-13): the recovered-data inventory
#     (files and GB, FR-DTS-006) was a pair of plain fields nothing wrote, so
#     the inventory page could only list zeros; it is recorded by the case's
#     staff (action_record_inventory) and frozen at handover. The handover
#     needed a receipt attached to the case, which the workspace could not
#     upload: the handover now takes the signed receipt file itself.
#
# FILE NAME IS LOAD-BEARING: sorts after fix_data_case_ext.
import base64
import binascii
import logging
import os
import re
import secrets
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError
from odoo.tools import misc

from .fix_data_case import (
    GROUP_OPERATOR,
    GROUP_Z4_CUSTODIAN,
    _norm_serial,
    _require_role,
)
from .fix_data_case_ext import _param_on, _resolve_user

_logger = logging.getLogger(__name__)

# Switches and policy numbers (ir.config_parameter); defaults are the safe
# values. The retention window and automatic purge are a business decision
# (A02 report §7.7): unset, a case is flagged at 30 days and never purged
# automatically.
RETENTION_DAYS_PARAM = "cd_data_case.retention_days"
RETENTION_DAYS_DEFAULT = 30
AUTO_PURGE_PARAM = "cd_data_case.retention_auto_purge"
IMAGE_REQUIRED_PARAM = "cd_data_case.recovery_requires_verified_image"
IMAGE_SECOND_PERSON_PARAM = "cd_data_case.image_verification_second_person"
HANDOVER_TTL_MINUTES = 10
HANDOVER_MAX_ATTEMPTS = 3
_HANDOVER_SCOPE = "cd_data_case.handover_otp"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _sha256(value) -> str:
    """A SHA-256 hex digest in canonical form, or '' if it is not one."""
    text = "".join(str(value or "").split()).lower()
    return text if _SHA256.match(text) else ""


def _bd_mobile(phone):
    digits = "".join(c for c in str(phone or "") if c.isdigit())
    if digits.startswith("880"):
        digits = "0" + digits[3:]
    elif len(digits) == 10 and not digits.startswith("0"):
        digits = "0" + digits
    return digits if len(digits) == 11 and digits.startswith("01") else None


class FixApprovalMatrixDataCase(models.Model):
    """The M06 decision domain the M63 rule book can address (A02 audit B1)."""

    _inherit = "fix.approval.matrix"

    decision_domain = fields.Selection(
        selection_add=[("data_quote_requote", "Data Recovery Re-quote Price Increase")],
        ondelete={"data_quote_requote": "cascade"},
    )


class FixDataRecoveryCaseSecure(models.Model):
    _inherit = "fix.data.recovery.case"

    # ---- named Z4 staff ----------------------------------------------------
    assigned_technician_id = fields.Many2one(
        "res.users", string="Assigned Technician", readonly=True, copy=False, tracking=True
    )
    z4_custodian_id = fields.Many2one(
        "res.users", string="Assigned Z4 Custodian", readonly=True, copy=False, tracking=True
    )
    # ---- imaging -----------------------------------------------------------
    image_source_sha256 = fields.Char(string="Source Media SHA-256", readonly=True, copy=False)
    image_tool = fields.Char(string="Imaging Tool / Write-Blocker", readonly=True, copy=False)
    imaged_at = fields.Datetime(string="Imaged At", readonly=True, copy=False)
    imaged_by_id = fields.Many2one("res.users", string="Imaged By", readonly=True, copy=False)
    image_verified_at = fields.Datetime(string="Image Verified At", readonly=True, copy=False)
    image_verified_by_id = fields.Many2one(
        "res.users", string="Image Verified By", readonly=True, copy=False
    )
    image_verify_method = fields.Selection(
        [
            ("second_person", "Second Person Recomputed the Hash"),
            ("recomputed", "Hash Recomputed by the Imager"),
        ],
        string="Image Verification",
        readonly=True,
        copy=False,
    )
    image_matches_source = fields.Boolean(
        compute="_compute_image_matches_source",
        string="Image Hash Equals Source Hash",
        help="False on a damaged drive whose image skipped unreadable sectors",
    )
    # ---- handover ----------------------------------------------------------
    handover_recipient_id = fields.Many2one(
        "res.partner",
        string="Handover Recipient",
        help="The customer, or a contact of the customer, who collects the recovered data",
    )
    target_serial_confirmed_at = fields.Datetime(
        string="Target Drive Serial Confirmed At", readonly=True, copy=False
    )
    handover_code_hash = fields.Char(readonly=True, copy=False)
    handover_code_expires_at = fields.Datetime(readonly=True, copy=False)
    handover_code_attempts = fields.Integer(readonly=True, copy=False)
    handover_verification_method = fields.Selection(
        [("otp", "One-Time Code to the Recipient"), ("national_id", "Recipient's ID Number")],
        string="Recipient Verified By",
        readonly=True,
        copy=False,
    )
    handover_verification_ref = fields.Char(
        string="Verification Reference", readonly=True, copy=False
    )
    handover_receipt_attachment_id = fields.Many2one(
        "ir.attachment", string="Signed Handover Receipt", readonly=True, copy=False
    )
    # The workspace's upload for that receipt: never stored here. The file goes
    # to action_handover, which files it as an attachment ON the case.
    handover_receipt_file = fields.Binary(string="Signed Handover Receipt (file)", store=False)
    handover_receipt_filename = fields.Char(string="Receipt File Name", store=False)
    handover_at = fields.Datetime(string="Handed Over At", readonly=True, copy=False)
    handover_by_id = fields.Many2one(
        "res.users", string="Handed Over By", readonly=True, copy=False
    )
    # ---- retention ---------------------------------------------------------
    retention_until = fields.Date(
        string="Retain Recovered Data Until", readonly=True, copy=False, index=True
    )
    retention_flagged_at = fields.Datetime(
        string="Retention Overdue Flagged At", readonly=True, copy=False
    )

    _SECURE_GUARDED = {
        "assigned_technician_id",
        "z4_custodian_id",
        "image_source_sha256",
        "image_sha256_hash",
        "image_tool",
        "imaged_at",
        "imaged_by_id",
        "image_verified_at",
        "image_verified_by_id",
        "image_verify_method",
        "target_serial_confirmed_at",
        "handover_code_hash",
        "handover_code_expires_at",
        "handover_code_attempts",
        "handover_verification_method",
        "handover_verification_ref",
        "handover_receipt_attachment_id",
        "handover_at",
        "handover_by_id",
        "retention_until",
        "retention_flagged_at",
        # recorded by action_record_inventory only
        "recovered_files_count",
        "recovered_volume_gb",
    }

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | self._SECURE_GUARDED

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self[:1].target_serial_confirmed_at or self[:1].state in (
            "handover",
            "purged",
            "closed",
        ):
            locked |= {"encrypted_target_serial", "handover_recipient_id"}
        return locked

    def write(self, vals):
        if not self._fix_guard_open():
            for rec in self.filtered("id"):
                frozen = rec._fix_form_locked_fields() & {
                    "encrypted_target_serial",
                    "handover_recipient_id",
                }
                changed = [
                    n for n in frozen & set(vals) if rec._fix_guard_differs(n, vals[n], rec[n])
                ]
                if changed:
                    raise UserError(
                        "Case %s: the handover target drive and recipient are fixed once the "
                        "target serial is confirmed or the data handed over." % rec.name
                    )
            if "handover_recipient_id" in vals:
                # a code sent to one recipient does not hand over to another
                pending = self.filtered(lambda r: r.handover_code_hash)
                if pending:
                    pending._guarded().write(
                        {"handover_code_hash": False, "handover_code_expires_at": False}
                    )
        return super().write(vals)

    @api.depends("image_source_sha256", "image_sha256_hash")
    def _compute_image_matches_source(self):
        for rec in self:
            rec.image_matches_source = bool(
                rec.image_sha256_hash and rec.image_sha256_hash == rec.image_source_sha256
            )

    # ---- Z4 named staff ----------------------------------------------------
    def action_assign_staff(self, technician=None, custodian=None):
        """Name the case's technician and Z4 custodian (A02 audit M06-P2:
        any internal user read case PII; Z4 is for named, case-assigned
        staff). The technician holds the operator role, the custodian the Z4
        Custodian role. Once recovery started, only a Z4 custodian re-assigns."""
        for rec in self:
            _require_role(
                self.env, GROUP_OPERATOR, "Data Recovery Operator", "Assigning case staff"
            )
            if rec.state in ("purged", "closed", "unrecoverable"):
                raise UserError("Case %s is %s: no one is assigned to it." % (rec.name, rec.state))
            if rec.state not in ("new", "custody") and (
                rec.assigned_technician_id or rec.z4_custodian_id
            ):
                _require_role(
                    self.env,
                    GROUP_Z4_CUSTODIAN,
                    "Z4 Custodian",
                    "Re-assigning the staff of a case in recovery",
                )
            tech = _resolve_user(self.env, technician) if technician else rec.assigned_technician_id
            cust = _resolve_user(self.env, custodian) if custodian else rec.z4_custodian_id
            if technician and not tech:
                raise UserError("No user '%s' to assign as technician." % technician)
            if custodian and not cust:
                raise UserError("No user '%s' to assign as Z4 custodian." % custodian)
            if tech and not tech.has_group(GROUP_OPERATOR):
                raise UserError("%s does not hold the Data Recovery Operator role." % tech.name)
            if cust and not cust.has_group(GROUP_Z4_CUSTODIAN):
                raise UserError("%s does not hold the Z4 Custodian role." % cust.name)
            if not (tech or cust):
                raise UserError("Name the technician and / or the Z4 custodian.")
            rec._guarded().write(
                {"assigned_technician_id": tech.id or False, "z4_custodian_id": cust.id or False}
            )
            rec._custody_log(
                "z4_assigned",
                "[Z4 assignment] technician %s, custodian %s"
                % (tech.name or "-", cust.name or "-"),
            )
        return True

    def action_assign_me(self):
        """Workspace button: the acting operator becomes the case technician."""
        return self.action_assign_staff(technician=self.env.user)

    def _z4_staff(self):
        self.ensure_one()
        return self.assigned_technician_id | self.z4_custodian_id

    def _z4_assert_assigned(self, what):
        """Refuse a Z4 action by anyone but the case's named staff."""
        if self.env.su:
            return
        for rec in self:
            staff = rec._z4_staff()
            if not staff:
                raise AccessError(
                    "%s on case %s needs named Z4 staff: assign the technician and the Z4 "
                    "custodian first (Assign Staff)." % (what, rec.name)
                )
            if self.env.user not in staff:
                raise AccessError(
                    "%s on case %s is for its assigned staff (%s) only."
                    % (what, rec.name, ", ".join(staff.mapped("name")))
                )

    # ---- imaging -----------------------------------------------------------
    def action_record_image(self, source_hash=None, image_hash=None, hashes=None, tool=None):
        """Record the forensic image: the source media's SHA-256 and the
        image's. ``hashes`` takes both in one string (the workspace prompt)."""
        if hashes and not (source_hash or image_hash):
            parts = [p for p in re.split(r"[\s,;]+", str(hashes)) if p]
            source_hash = parts[0] if parts else ""
            image_hash = parts[1] if len(parts) > 1 else parts[0] if parts else ""
        source, image = _sha256(source_hash), _sha256(image_hash)
        for rec in self:
            if rec.state not in ("custody", "recovering"):
                raise UserError(
                    "Case %s is imaged while it is held for recovery (it is '%s')."
                    % (rec.name, rec.state)
                )
            rec._z4_assert_assigned("Recording the forensic image")
            if rec.image_verified_at:
                raise UserError("Case %s: the image is verified and its hash is frozen." % rec.name)
            if not (source and image):
                raise UserError(
                    "Give both the source media SHA-256 and the image SHA-256 (64 hex digits each)."
                )
            rec._guarded().write(
                {
                    "image_source_sha256": source,
                    "image_sha256_hash": image,
                    "image_tool": (tool or "").strip() or rec.write_blocker_serial or False,
                    "imaged_at": fields.Datetime.now(),
                    "imaged_by_id": self.env.uid,
                }
            )
            rec._custody_log("imaged", "forensic image recorded (sha256 %s)" % image)
        return True

    def action_verify_image(self, recomputed_hash=None):
        """Verify the image: the verifier recomputes the image hash, which must
        equal the recorded one. A second person by default."""
        given = _sha256(recomputed_hash)
        second = _param_on(self.env, IMAGE_SECOND_PERSON_PARAM, True)
        for rec in self:
            _require_role(self.env, GROUP_OPERATOR, "Data Recovery Operator", "Verifying an image")
            if not rec.image_sha256_hash:
                raise UserError("Case %s has no recorded image to verify." % rec.name)
            if rec.image_verified_at:
                raise UserError("Case %s: the image is already verified." % rec.name)
            same = self.env.user == rec.imaged_by_id
            if second and same and not self.env.su:
                raise UserError(
                    "Segregation of duties: %s took the image of case %s, so a second person "
                    "verifies it." % (self.env.user.name, rec.name)
                )
            if not given:
                raise UserError("Give the image SHA-256 you recomputed (64 hex digits).")
            if given != rec.image_sha256_hash:
                raise UserError(
                    "Case %s: the recomputed hash does not match the recorded image hash; the "
                    "image is not verified. Re-image the media." % rec.name
                )
            rec._guarded().write(
                {
                    "image_verified_at": fields.Datetime.now(),
                    "image_verified_by_id": self.env.uid,
                    "image_verify_method": "recomputed" if same else "second_person",
                }
            )
            rec._custody_log("image_verified", "forensic image verified (hash recomputed)")
        return True

    def _assert_verified_image(self):
        if not _param_on(self.env, IMAGE_REQUIRED_PARAM, True):
            return
        for rec in self:
            if not rec.image_verified_at:
                raise UserError(
                    "Case %s: recovery is worked from a verified forensic image. Record the "
                    "image and have it verified first." % rec.name
                )

    # ---- handover ----------------------------------------------------------
    def _handover_recipient_check(self):
        self.ensure_one()
        recipient = self.handover_recipient_id
        if not recipient:
            raise UserError(
                "Case %s: name the handover recipient (the customer or one of its contacts)."
                % self.name
            )
        customer = self.customer_id.commercial_partner_id
        if recipient.commercial_partner_id != customer:
            raise UserError(
                "%s is not the customer %s or one of its contacts: the recovered data goes "
                "only to the customer." % (recipient.display_name, self.customer_id.name)
            )
        return recipient

    def action_confirm_target_serial(self, serial=None):
        """Read the serial off the target drive the data was written to; it must
        be the encrypted target drive recorded on the case."""
        for rec in self:
            if rec.state != "recovered":
                raise UserError("The target drive is confirmed at handover (case %s)." % rec.name)
            rec._z4_assert_assigned("Confirming the handover target drive")
            recorded = _norm_serial(rec.encrypted_target_serial)
            if not recorded:
                raise UserError(
                    "Case %s: record the encrypted target drive serial on the case first."
                    % rec.name
                )
            if _norm_serial(serial) != recorded:
                raise UserError(
                    "Case %s: serial %s is not the recorded target drive %s."
                    % (rec.name, serial or "(none)", rec.encrypted_target_serial)
                )
            rec._guarded().write({"target_serial_confirmed_at": fields.Datetime.now()})
        return True

    def _handover_digest(self, code):
        self.ensure_one()
        return misc.hmac(self.env(su=True), _HANDOVER_SCOPE, "%s:%s" % (self.id, code))

    def action_request_handover_otp(self):
        """Send the recipient a one-time handover code (to their mobile)."""
        self.ensure_one()
        rec = self
        if rec.state != "recovered":
            raise UserError("A handover code is sent when the data is ready (case %s)." % rec.name)
        rec._z4_assert_assigned("Sending the handover code")
        recipient = rec._handover_recipient_check()
        phone = _bd_mobile(recipient.phone or getattr(recipient, "mobile", False))
        if not phone:
            raise UserError(
                "%s has no Bangladesh mobile number on file; verify the recipient's ID number "
                "instead." % recipient.display_name
            )
        code = "%06d" % secrets.randbelow(10**6)
        rec._guarded().write(
            {
                "handover_code_hash": rec._handover_digest(code),
                "handover_code_expires_at": fields.Datetime.now()
                + timedelta(minutes=HANDOVER_TTL_MINUTES),
                "handover_code_attempts": 0,
            }
        )
        sent = rec._handover_send_code(recipient, phone, code)
        rec.message_post(
            body="Handover code sent to %s (%s)." % (recipient.display_name, sent["destination"])
        )
        return dict(sent, expires_in=HANDOVER_TTL_MINUTES * 60)

    def _handover_send_code(self, recipient, phone, code):
        """Hand the code to the recipient's phone through the platform OTP
        channel, which never stores it. The code itself is returned only on
        the synthetic local environment (DE-11)."""
        masked = phone[:3] + "*****" + phone[-3:]
        try:
            installed = (
                self.env["ir.module.module"]
                .sudo()
                .search_count([("name", "=", "cd_customer_portal"), ("state", "=", "installed")])
            )
            if not installed:
                raise RuntimeError("no OTP channel installed")
            from odoo.addons.cd_customer_portal.controllers import otp_delivery

            otp_delivery.send_otp(
                phone, code, HANDOVER_TTL_MINUTES * 60, (recipient.lang or "bn")[:2]
            )
        except (ImportError, RuntimeError):
            if os.environ.get("FIX_ENV") == "local":
                return {"destination": masked, "dev_code": code}
            raise UserError("The handover code could not be sent to %s." % masked) from None
        return {"destination": masked}

    def _handover_count_failed_code(self):
        """A wrong code is counted on its own cursor: the refusal that follows
        rolls this transaction back, which would make every guess free."""
        self.ensure_one()
        with self.env.registry.cursor() as cr:
            cr.execute(
                """
                UPDATE fix_data_recovery_case
                   SET handover_code_attempts = COALESCE(handover_code_attempts, 0) + 1,
                       handover_code_hash = CASE
                           WHEN COALESCE(handover_code_attempts, 0) + 1 >= %s THEN NULL
                           ELSE handover_code_hash END
                 WHERE id = %s
                """,
                (HANDOVER_MAX_ATTEMPTS, self.id),
            )
            counted = cr.rowcount
        if not counted:
            attempts = (self.handover_code_attempts or 0) + 1
            vals = {"handover_code_attempts": attempts}
            if attempts >= HANDOVER_MAX_ATTEMPTS:
                vals["handover_code_hash"] = False
            self._guarded().write(vals)

    def _handover_verify(self, verification):
        """('otp' | 'national_id', masked reference) for a verified recipient."""
        self.ensure_one()
        given = "".join(str(verification or "").split())
        recipient = self.handover_recipient_id
        if self.handover_code_hash and len(given) == 6 and given.isdigit():
            if fields.Datetime.now() > (self.handover_code_expires_at or fields.Datetime.now()):
                raise UserError("The handover code has expired. Send a new one.")
            if not misc.consteq(self._handover_digest(given), self.handover_code_hash):
                self._handover_count_failed_code()
                raise UserError(
                    "The handover code does not match. After %d wrong codes it is void."
                    % HANDOVER_MAX_ATTEMPTS
                )
            return "otp", "OTP to %s" % (recipient.display_name,)
        digits = "".join(c for c in given if c.isalnum()).upper()
        # The recipient's KYC-verified identity documents (M33): an ID number
        # typed by staff proves nothing unless it matches one already verified.
        docs = (
            self.env["fix.identity.document"]
            .sudo()
            .search(
                [
                    ("partner_id", "=", recipient.id),
                    ("verification_status", "=", "verified"),
                    ("document_type", "in", ("nid_10", "nid_17", "passport")),
                ]
            )
        )
        # read(): the number is residency-classified; the mixin fetches it from
        # Z4 for this request only (FF-09), never into the regional cache.
        on_file = {
            "".join(c for c in str(row.get("document_number") or "") if c.isalnum()).upper()
            for row in docs.read(["document_number"])
        } - {""}
        if not on_file:
            raise UserError(
                "Verify the recipient: give the one-time handover code (Send Handover Code), or "
                "the recipient's ID number when a verified ID is on file (none is on file for "
                "%s)." % recipient.display_name
            )
        if len(digits) < 8 or digits not in on_file:
            raise UserError(
                "The ID number does not match %s's verified ID on file." % recipient.display_name
            )
        return "national_id", "ID ****%s" % digits[-4:]

    def _handover_receipt(self, receipt_attachment_id=None):
        self.ensure_one()
        if receipt_attachment_id:
            return self._customer_artefact(receipt_attachment_id)
        Attachment = self.env["ir.attachment"].sudo()
        for att in Attachment.search(
            [
                ("res_model", "=", self._name),
                ("res_id", "=", self.id),
                ("name", "ilike", "receipt"),
            ],
            order="id desc",
        ):
            if att.raw:
                return att
        raise UserError(
            "Case %s: attach the handover receipt the recipient signed (a file named "
            "'receipt...') to the case." % self.name
        )

    def _file_handover_receipt(self, data, filename=None):
        """File the signed receipt the workspace uploaded as an attachment on
        this case. It is created inside the handover's transaction, so a
        refused handover leaves no receipt behind."""
        self.ensure_one()
        try:
            raw = base64.b64decode(data, validate=True)
        except (binascii.Error, ValueError, TypeError):
            raise UserError("The receipt file could not be read: upload it again.") from None
        if not raw:
            raise UserError("The receipt file is empty: upload the signed receipt.")
        name = (filename or "").strip() or "Signed handover receipt"
        return self.env["ir.attachment"].create(
            {"name": name, "raw": raw, "res_model": self._name, "res_id": self.id}
        )

    def action_record_inventory(self, files_count=None, volume_gb=None):
        """Record what was recovered (FR-DTS-006): how many files and how much
        data. Counts and size only - file names and content never enter the
        ERP. By the case's named staff, while the case is in recovery or
        recovered; frozen once the data is handed over."""
        try:
            files = int(files_count)
            volume = float(volume_gb)
        except (TypeError, ValueError):
            raise UserError(
                "Give the number of recovered files and the recovered volume in GB."
            ) from None
        if files < 0 or volume < 0:
            raise UserError("The recovered file count and volume cannot be negative.")
        for rec in self:
            if rec.state not in ("recovering", "recovered"):
                raise UserError(
                    "Case %s: the recovered-data inventory is recorded during recovery or once "
                    "the data is recovered, before handover (the case is '%s')."
                    % (rec.name, rec.state)
                )
            rec._z4_assert_assigned("Recording the recovered-data inventory")
            rec._guarded().write({"recovered_files_count": files, "recovered_volume_gb": volume})
            rec.message_post(
                body="Recovered-data inventory recorded by %s: %d files, %.2f GB."
                % (self.env.user.name, files, volume)
            )
        return True

    def action_handover(
        self,
        handler=None,
        verification=None,
        receipt_attachment_id=None,
        receipt_file=None,
        receipt_filename=None,
    ):
        """Hand the recovered data to a VERIFIED recipient, against a signed
        receipt, on the confirmed target drive (A02 audit M06-P2). The receipt
        is an attachment on the case, or the signed file itself (``receipt_file``,
        base64), which is then filed on the case."""
        retention_days = int(
            self.env["ir.config_parameter"].sudo().get_param(RETENTION_DAYS_PARAM)
            or RETENTION_DAYS_DEFAULT
        )
        for rec in self:
            if rec.state != "recovered":
                raise UserError("Handover from recovered")
            rec._z4_assert_assigned("Handing over recovered data")
            recipient = rec._handover_recipient_check()
            if not rec.target_serial_confirmed_at:
                raise UserError(
                    "Case %s: confirm the target drive serial before handover." % rec.name
                )
            method, ref = rec._handover_verify(verification)
            if receipt_file and not receipt_attachment_id:
                receipt = rec._file_handover_receipt(receipt_file, receipt_filename)
            else:
                receipt = rec._handover_receipt(receipt_attachment_id)
            who = (handler or "").strip() or self.env.user.name
            rec._custody_log(
                "handover",
                "handed over by %s to %s (verified by %s, receipt %s, target %s)"
                % (who, recipient.display_name, ref, receipt.name, rec.encrypted_target_serial),
            )
            rec._guarded().write(
                {
                    "state": "handover",
                    "handover_verification_method": method,
                    "handover_verification_ref": ref,
                    "handover_receipt_attachment_id": receipt.id,
                    "handover_at": fields.Datetime.now(),
                    "handover_by_id": self.env.uid,
                    "handover_code_hash": False,
                    "retention_until": fields.Date.context_today(self)
                    + timedelta(days=max(retention_days, 0)),
                }
            )
        return True

    # ---- B4: retention ------------------------------------------------------
    @api.model
    def cron_retention_purge(self):
        """Cases past their retention date: purge on a verified wipe
        certificate for the case's own media when automatic purge is on;
        otherwise (or with no such certificate) flag the case once for its
        staff. Never purges without the certificate: action_purge keeps the
        P0 gate (verified, unchanged log, bound to this serial, one case)."""
        auto = _param_on(self.env, AUTO_PURGE_PARAM, False)
        today = fields.Date.context_today(self)
        # Cases handed over before the retention clock existed get one, from
        # their last change, so they are not retained forever.
        days = int(
            self.env["ir.config_parameter"].sudo().get_param(RETENTION_DAYS_PARAM)
            or RETENTION_DAYS_DEFAULT
        )
        for legacy in self.sudo().search(
            [("state", "=", "handover"), ("retention_until", "=", False)]
        ):
            start = (legacy.handover_at or legacy.write_date or fields.Datetime.now()).date()
            legacy._guarded().write({"retention_until": start + timedelta(days=max(days, 0))})
        due = self.sudo().search(
            [
                ("state", "=", "handover"),
                ("retention_until", "!=", False),
                ("retention_until", "<=", today),
            ]
        )
        purged = 0
        for case in due:
            try:
                with self.env.cr.savepoint():
                    reason = "automatic purge is off"
                    if auto:
                        try:
                            cert = case._purge_certificate(None)
                            reason = cert._fix_certify_denial(case.media_serial_number)
                        except UserError as exc:
                            cert, reason = None, str(exc)
                        if cert and not reason:
                            case.action_purge(cert)
                            purged += 1
                            continue
                    case._retention_flag(reason)
            except Exception:
                _logger.exception("M06 retention purge failed for case %s", case.id)
        return purged

    def _retention_flag(self, reason):
        for case in self.filtered(lambda c: not c.retention_flagged_at):
            case._guarded().write({"retention_flagged_at": fields.Datetime.now()})
            note = (
                "Retention ended on %s: purge the recovered data with a verified wipe "
                "certificate for media %s (%s)."
                % (case.retention_until, case.media_serial_number, reason)
            )
            case.message_post(body=note)
            user = case.assigned_technician_id or case.z4_custodian_id or case.create_uid
            if user and user.active and not user.share:
                case.activity_schedule(
                    "mail.mail_activity_data_todo",
                    summary="Retention ended: purge case %s" % case.name,
                    note=note,
                    user_id=user.id,
                )
