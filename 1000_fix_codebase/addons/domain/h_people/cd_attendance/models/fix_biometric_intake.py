# fix_biometric_intake — M55 capture: the device webhook's credential and replay
# log, and the employee's biometric consent (A09 M55-8, BRU-WFM-08, T-02/T-05).
#
#   fix.biometric.device (extended)  a per-device credential, stored only as a
#                                    SHA-256 hash and rotated by an Attendance
#                                    Supervisor; the webhook
#                                    /hooks/v1/biometric/<device> presents it
#   fix.biometric.punch.event        one row per device event id: a replayed
#                                    event is answered from the log, never
#                                    ingested twice
#   fix.biometric.consent            BRU-WFM-08 / PDPA 2026: no device punch is
#                                    ingested for an employee without their
#                                    recorded consent; they withdraw it at any
#                                    time and other capture methods stay open
import hashlib
import hmac
import secrets

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from .fix_attendance import SUPERVISOR_GROUP

# a presented credential shorter than this is refused at rotation: the hash is
# unsalted, so the secret itself must carry the entropy (32 url-safe chars ~ 190 bits)
MIN_CREDENTIAL_LENGTH = 32
HR_GROUP = "cd_hr_core.group_hr_officer"


def credential_hash(secret):
    return hashlib.sha256((secret or "").encode("utf-8")).hexdigest()


class FixBiometricDeviceCredential(models.Model):
    _name = "fix.biometric.device"
    _inherit = ["fix.biometric.device", "fix.guarded.mixin"]

    credential_hash = fields.Char(
        string="Credential Hash",
        readonly=True,
        copy=False,
        groups="base.group_system",
        help="SHA-256 of the device credential. The credential itself is never stored.",
    )
    credential_prefix = fields.Char(
        string="Credential Starts With",
        readonly=True,
        copy=False,
        help="The first characters of the current credential, to tell versions apart.",
    )
    credential_rotated_at = fields.Datetime(readonly=True, copy=False)
    credential_rotated_by_id = fields.Many2one(
        "res.users", string="Credential Rotated By", readonly=True, copy=False
    )
    punch_event_ids = fields.One2many(
        "fix.biometric.punch.event", "device_id", string="Webhook Events", readonly=True
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "credential_hash",
            "credential_prefix",
            "credential_rotated_at",
            "credential_rotated_by_id",
            "last_sync_at",
        }

    def action_rotate_credential(self, credential=None):
        """Issue a new credential for the device; the old one stops working.

        `credential`: the secret provisioned on the terminal (at least 32
        characters); when omitted a random one is generated and returned ONCE
        in the result. Only an Attendance Supervisor rotates."""
        if not (self.env.su or self.env.user.has_group(SUPERVISOR_GROUP)):
            raise AccessError("Only an Attendance Supervisor rotates a device credential.")
        self.ensure_one()
        secret = (credential or "").strip() or secrets.token_urlsafe(32)
        if len(secret) < MIN_CREDENTIAL_LENGTH:
            raise UserError(
                "A device credential has at least %d characters." % MIN_CREDENTIAL_LENGTH
            )
        self.sudo()._guarded().write(
            {
                "credential_hash": credential_hash(secret),
                "credential_prefix": secret[:6],
                "credential_rotated_at": fields.Datetime.now(),
                "credential_rotated_by_id": self.env.user.id,
            }
        )
        self.message_post(
            body="Webhook credential rotated by %s (starts %s…)." % (self.env.user.name, secret[:6])
        )
        result = {"device": self.device_id, "credential_prefix": secret[:6]}
        if not credential:
            result["credential"] = secret  # shown once, never stored
        return result

    def _fix_credential_ok(self, presented):
        """Constant-time check of a presented credential (superuser reads the hash)."""
        self.ensure_one()
        stored = self.sudo().credential_hash
        if not (stored and presented):
            return False
        return hmac.compare_digest(stored, credential_hash(presented))


class FixBiometricPunchEvent(models.Model):
    """The webhook's replay log (T-05): one row per (device, event id)."""

    _name = "fix.biometric.punch.event"
    _description = "Biometric Webhook Event"
    _inherit = ["fix.guarded.mixin"]
    _order = "id desc"

    device_id = fields.Many2one(
        "fix.biometric.device", required=True, index=True, ondelete="cascade", readonly=True
    )
    company_id = fields.Many2one("res.company", required=True, index=True, readonly=True)
    event_ref = fields.Char(string="Device Event Id", required=True, index=True, readonly=True)
    employee_id = fields.Many2one("hr.employee", readonly=True, index=True)
    punch_time = fields.Datetime(readonly=True)
    punch_type = fields.Selection(
        [("check_in", "Check-In"), ("check_out", "Check-Out")], readonly=True
    )
    state = fields.Selection(
        [("ingested", "Ingested"), ("refused", "Refused")], required=True, readonly=True
    )
    record_id = fields.Many2one("fix.attendance.record", readonly=True, ondelete="set null")
    message = fields.Char(readonly=True)

    # a refused event may be sent again once its cause is fixed (consent
    # recorded, period re-opened); an ingested one never twice
    _device_event_ingested = models.UniqueIndex(
        "(device_id, event_ref) WHERE state = 'ingested'",
        "This device event was already ingested.",
    )

    def _fix_guarded_fields(self) -> set:
        # the whole row is the webhook's record of what a device sent
        return super()._fix_guarded_fields() | {
            "device_id",
            "company_id",
            "event_ref",
            "employee_id",
            "punch_time",
            "punch_type",
            "state",
            "record_id",
            "message",
        }

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.su:
            raise AccessError("Webhook events are written by the device webhook only.")
        return super().create(vals_list)


class FixBiometricConsent(models.Model):
    """BRU-WFM-08 / T-02: specific consent to biometric processing, given by
    the employee (confirmed by their own login, or recorded by HR against
    their signed consent) and withdrawn by them at any time. HR prepares the
    consent record; plain users have no write on the model (RAP X-02): the
    employee's Give / Withdraw actions apply their own decision."""

    _name = "fix.biometric.consent"
    _description = "Biometric Processing Consent (PDPA)"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "id desc"

    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    employee_id = fields.Many2one("hr.employee", required=True, index=True)
    consent_file = fields.Binary(string="Signed Consent", attachment=True, copy=False)
    consent_file_name = fields.Char(copy=False)
    notice_version = fields.Char(
        string="Consent Notice Version", help="The consent notice the employee was shown."
    )
    state = fields.Selection(
        [("draft", "Draft"), ("given", "Given"), ("withdrawn", "Withdrawn")],
        default="draft",
        required=True,
        readonly=True,
        tracking=True,
        index=True,
    )
    given_by_id = fields.Many2one("res.users", string="Recorded By", readonly=True)
    given_at = fields.Datetime(readonly=True)
    withdrawn_by_id = fields.Many2one("res.users", string="Withdrawn By", readonly=True)
    withdrawn_at = fields.Datetime(readonly=True)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "given_by_id",
            "given_at",
            "withdrawn_by_id",
            "withdrawn_at",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        if self and self.state != "draft":
            locked |= {"employee_id", "company_id", "consent_file", "notice_version"}
        return locked

    @api.constrains("employee_id", "state")
    def _check_one_given(self):
        for rec in self.filtered(lambda r: r.state == "given"):
            if self.sudo().search_count(
                [
                    ("id", "!=", rec.id),
                    ("employee_id", "=", rec.employee_id.id),
                    ("state", "=", "given"),
                ]
            ):
                raise ValidationError(
                    "%s already has a given biometric consent." % rec.employee_id.name
                )

    def write(self, vals):
        if (
            self
            and not self._fix_guard_open()
            and {"employee_id", "company_id", "consent_file", "notice_version"} & set(vals)
            and self.filtered(lambda r: r.state != "draft")
        ):
            raise UserError("A given consent is not edited: withdraw it and record a new one.")
        return super().write(vals)

    @api.model
    def _fix_has_consent(self, employee, day=None):
        return bool(
            self.sudo().search_count([("employee_id", "=", employee.id), ("state", "=", "given")])
        )

    def _fix_assert_own_or_hr(self, verb):
        for rec in self:
            if rec.employee_id.sudo().user_id == self.env.user:
                continue
            if self.env.su or self.env.user.has_group(HR_GROUP):
                continue
            raise AccessError(
                "Biometric consent is %s by the employee, or by HR from their signed consent "
                "- never by the attendance roles that run the devices." % verb
            )

    def action_give(self):
        self._fix_assert_own_or_hr("given")
        for rec in self:
            if rec.state != "draft":
                raise UserError("Only a draft consent is given.")
            own = rec.employee_id.sudo().user_id == self.env.user
            if not own and not rec.consent_file:
                raise UserError("HR records a consent only against the employee's signed consent.")
            # RAP X-02: no plain-user write on the model; the employee's own
            # decision is applied as superuser once the check above passed
            rec.sudo()._guarded().write(
                {
                    "state": "given",
                    "given_by_id": self.env.user.id,
                    "given_at": fields.Datetime.now(),
                }
            )
        return True

    def action_withdraw(self):
        self._fix_assert_own_or_hr("withdrawn")
        for rec in self:
            if rec.state != "given":
                raise UserError("Only a given consent is withdrawn.")
            rec.sudo()._guarded().write(
                {
                    "state": "withdrawn",
                    "withdrawn_by_id": self.env.user.id,
                    "withdrawn_at": fields.Datetime.now(),
                }
            )
            rec.sudo().message_post(
                body="Consent withdrawn by %s: no further device punches are ingested."
                % self.env.user.name
            )
        return True
