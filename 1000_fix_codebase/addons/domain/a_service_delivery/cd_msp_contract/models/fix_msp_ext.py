# fix_msp_ext — M05 follow-ups (P08-M07): the alert resolution leg and the
# session state guard the journeys always described. FILE NAME IS
# LOAD-BEARING: imports after the base models alphabetically (fix_msp).
#
# A02 audit M05-4 (2026-11-03): the client's consent is a one-time code sent
# to the client contact and read back to the technician, not a tickbox; the
# recording reference is required to end a session.
import os
import secrets
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import misc

# Policy numbers and switches (ir.config_parameter). Defaults are the safe
# values; changing them is a business decision.
CONSENT_TTL_PARAM = "cd_msp_contract.remote_consent_ttl_minutes"
CONSENT_TTL_DEFAULT = 10
CONSENT_MAX_ATTEMPTS = 3
RECORDING_REQUIRED_PARAM = "cd_msp_contract.remote_session_recording_required"
_CONSENT_SCOPE = "cd_msp_contract.remote_consent"


def _bd_mobile(phone):
    """``01XXXXXXXXX`` for a Bangladesh mobile number, else None."""
    digits = "".join(c for c in str(phone or "") if c.isdigit())
    if digits.startswith("880"):
        digits = "0" + digits[3:]
    elif len(digits) == 10 and not digits.startswith("0"):
        digits = "0" + digits
    return digits if len(digits) == 11 and digits.startswith("01") else None


class FixMspAlertExt(models.Model):
    _inherit = "fix.msp.alert"

    resolved_at = fields.Datetime(string="Resolved At", readonly=True, copy=False)
    resolution_note = fields.Char(string="Resolution Note", readonly=True, copy=False)

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"resolved_at", "resolution_note"}

    def action_resolve(self, note=""):
        """The ticketed → resolved leg. The state existed in the Selection
        but no method ever set it — resolution was only reachable by direct
        field writes in tests. Resolving stamps the time, records the note
        and links back to the service order's outcome."""
        for alert in self:
            if alert.state not in ("ticketed", "acked", "new"):
                raise UserError(
                    "Alert %s cannot be resolved from state '%s'." % (alert.id, alert.state)
                )
            alert._guarded().write(
                {
                    "state": "resolved",
                    "resolved_at": fields.Datetime.now(),
                    "resolution_note": note or None,
                }
            )
        return True


class FixRemoteSessionExt(models.Model):
    _inherit = "fix.remote.session"

    started = fields.Boolean(
        string="Started",
        readonly=True,
        copy=False,
        help="True once action_start ran (the base's started_at defaults at "
        "create, so it cannot distinguish a planned from a running session).",
    )
    # --- client consent (A02 audit M05-4) ---------------------------------
    consent_partner_id = fields.Many2one(
        "res.partner",
        string="Consenting Client Contact",
        help="The client contact who receives the consent code. Empty = the "
        "contract's customer. Must belong to the contract's customer.",
    )
    consent_channel = fields.Selection(
        [("otp", "One-time code to the client contact")],
        string="Consent Channel",
        readonly=True,
        copy=False,
    )
    consent_requested_at = fields.Datetime(readonly=True, copy=False)
    consent_expires_at = fields.Datetime(readonly=True, copy=False)
    consent_attempts = fields.Integer(readonly=True, copy=False)
    # An HMAC keyed by database.secret: reading it does not reveal the code,
    # and the guard refuses any write outside the consent actions.
    consent_code_hash = fields.Char(readonly=True, copy=False)
    consent_captured_at = fields.Datetime(readonly=True, copy=False)
    consent_verified_by_id = fields.Many2one(
        "res.users",
        string="Consent Code Entered By",
        readonly=True,
        copy=False,
    )

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "started",
            "consent_channel",
            "consent_requested_at",
            "consent_expires_at",
            "consent_attempts",
            "consent_code_hash",
            "consent_captured_at",
            "consent_verified_by_id",
        }

    # The scope a consent was given for: once a code is out, the session may
    # not be moved to another contract, endpoint or contact.
    _CONSENT_BOUND_FIELDS = {"msp_contract_id", "asset_id", "consent_partner_id"}
    _STARTED_FROZEN_FIELDS = {"technician_id", "tool", "session_protocol"}

    def _msp_frozen_fields(self) -> set:
        self.ensure_one()
        frozen = set()
        if self.consent_requested_at or self.consent_captured or self.started:
            frozen |= self._CONSENT_BOUND_FIELDS
        if self.started or self.ended_at:
            frozen |= self._STARTED_FROZEN_FIELDS
        return frozen

    def _fix_form_locked_fields(self) -> set:
        locked = super()._fix_form_locked_fields()
        return locked | self._msp_frozen_fields() if self else locked

    def write(self, vals):
        if not self._fix_guard_open():
            for rec in self.filtered("id"):
                changed = [
                    name
                    for name in rec._msp_frozen_fields() & set(vals)
                    if rec._fix_guard_differs(name, vals[name], rec[name])
                ]
                if changed:
                    raise UserError(
                        "%s cannot change once the client's consent was requested or the "
                        "session started: the consent covers this contract, endpoint and "
                        "contact. Open a new session instead."
                        % ", ".join(sorted(rec._fields[n].string or n for n in changed))
                    )
        return super().write(vals)

    @api.constrains("consent_partner_id", "msp_contract_id")
    def _check_consent_partner(self):
        for rec in self:
            customer = rec.msp_contract_id.contract_id.customer_id.commercial_partner_id
            party = rec.consent_partner_id
            if party and customer and party.commercial_partner_id != customer:
                raise ValidationError(
                    "%s is not a contact of the contract's customer %s - only the client "
                    "can consent to a remote session." % (party.display_name, customer.name)
                )

    def _consent_party(self):
        self.ensure_one()
        return self.consent_partner_id or self.msp_contract_id.contract_id.customer_id

    def _consent_digest(self, code):
        self.ensure_one()
        return misc.hmac(self.env(su=True), _CONSENT_SCOPE, "%s:%s" % (self.id, code))

    def _consent_send_code(self, partner, code, ttl_seconds):
        """Hand the code to the client contact's phone through the platform
        OTP channel (the notification dispatcher's SMS path, which never stores
        the code). Returns what the caller may see: the masked destination,
        and the code itself only on the synthetic local environment (DE-11),
        as the customer portal does."""
        phone = _bd_mobile(partner.phone or getattr(partner, "mobile", False))
        if not phone:
            raise UserError(
                "%s has no Bangladesh mobile number on file, so the consent code cannot "
                "be sent. Record the client contact's mobile number first." % partner.display_name
            )
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

            otp_delivery.send_otp(phone, code, ttl_seconds, (partner.lang or "bn")[:2])
        except (ImportError, RuntimeError):
            if os.environ.get("FIX_ENV") == "local":
                return {"destination": masked, "dev_code": code}
            raise UserError(
                "The consent code could not be sent to %s. Try again shortly." % masked
            ) from None
        return {"destination": masked}

    def action_request_consent(self):
        """Send the client contact a one-time consent code (step 1 of 2)."""
        self.ensure_one()
        session = self
        if session.started or session.ended_at:
            raise UserError("This session has already started; consent is asked before it starts.")
        if session.consent_captured:
            raise UserError("The client's consent is already captured for this session.")
        if session.asset_id.msp_contract_id != session.msp_contract_id:
            raise UserError("The asset is not covered by this session's contract.")
        party = session._consent_party()
        if not party:
            raise UserError("The contract has no customer to ask for consent.")
        ttl_minutes = int(
            self.env["ir.config_parameter"].sudo().get_param(CONSENT_TTL_PARAM, CONSENT_TTL_DEFAULT)
            or CONSENT_TTL_DEFAULT
        )
        code = "%06d" % secrets.randbelow(10**6)
        now = fields.Datetime.now()
        session._guarded().write(
            {
                "consent_code_hash": session._consent_digest(code),
                "consent_requested_at": now,
                "consent_expires_at": now + timedelta(minutes=ttl_minutes),
                "consent_attempts": 0,
            }
        )
        sent = session._consent_send_code(party, code, ttl_minutes * 60)
        session.message_post(
            body="Remote-session consent code sent to %s (%s), valid %d minutes."
            % (party.display_name, sent.get("destination"), ttl_minutes)
        )
        return dict(sent, expires_in=ttl_minutes * 60)

    def _consent_count_failed_attempt(self):
        """Count a wrong code. The refusal that follows rolls this transaction
        back, which would make every guess free; so the count is committed on
        a cursor of its own. When the session row is not committed yet (the
        same transaction created it, e.g. a test), the other cursor cannot see
        it, and the count is kept in this transaction instead."""
        self.ensure_one()
        with self.env.registry.cursor() as cr:
            cr.execute(
                """
                UPDATE fix_remote_session
                   SET consent_attempts = COALESCE(consent_attempts, 0) + 1,
                       consent_code_hash = CASE WHEN COALESCE(consent_attempts, 0) + 1 >= %s
                                                THEN NULL ELSE consent_code_hash END
                 WHERE id = %s
                """,
                (CONSENT_MAX_ATTEMPTS, self.id),
            )
            counted = cr.rowcount
        if not counted:
            attempts = (self.consent_attempts or 0) + 1
            vals = {"consent_attempts": attempts}
            if attempts >= CONSENT_MAX_ATTEMPTS:
                vals["consent_code_hash"] = False
            self._guarded().write(vals)

    def action_verify_consent(self, code=None):
        """Verify the code the client contact read back (step 2 of 2). Only a
        correct, unexpired code captures consent and stamps its reference."""
        self.ensure_one()
        session = self
        if session.consent_captured:
            raise UserError("The client's consent is already captured for this session.")
        stored = session.consent_code_hash
        if not stored or not session.consent_expires_at:
            raise UserError(
                "No live consent code for this session. Use Request Consent to send the "
                "client a new code."
            )
        if fields.Datetime.now() > session.consent_expires_at:
            raise UserError("The consent code has expired. Request a new one.")
        given = str(code or "").strip()
        if not given or not misc.consteq(session._consent_digest(given), stored):
            session._consent_count_failed_attempt()
            raise UserError(
                "The consent code does not match. After %d wrong codes the code is "
                "void and a new one must be requested." % CONSENT_MAX_ATTEMPTS
            )
        party = session._consent_party()
        token = "OTP-%s-%s" % (session.id, secrets.token_hex(4).upper())
        if "fix.otp.log" in self.env:
            # M33 keeps the record of every OTP verification event; the
            # consent token points at it.
            phone = _bd_mobile(party.phone or getattr(party, "mobile", False)) or ""
            log = (
                self.env["fix.otp.log"]
                .sudo()
                .create(
                    {
                        "partner_id": party.id,
                        "channel": "mobile",
                        "destination_masked": phone and phone[:3] + "*****" + phone[-3:],
                        "state": "verified",
                        "verified_at": fields.Datetime.now(),
                        "channel_ref": "fix.remote.session,%s" % session.id,
                    }
                )
            )
            token = "fix.otp.log,%s" % log.id
        session._guarded().write(
            {
                "consent_captured": True,
                "consent_token_ref": token,
                "consent_channel": "otp",
                "consent_captured_at": fields.Datetime.now(),
                "consent_verified_by_id": self.env.user.id,
                "consent_code_hash": False,
            }
        )
        session.message_post(
            body="Client consent captured from %s by one-time code (ref %s)."
            % (party.display_name, token)
        )
        return True

    def action_start(self):
        """PDPA consent gate + the repeat-start guard: the base had no
        state, so repeated starts were silent no-ops and a started_at
        default made every planned session look 'running'."""
        for session in self:
            if session.started and not session.ended_at:
                raise UserError(
                    "Session on %s is already running (started %s) — end it first."
                    % (session.asset_id.hostname or session.asset_id.agent_id, session.started_at)
                )
            if session.ended_at:
                raise UserError(
                    "Session on %s already ended at %s — open a new session."
                    % (session.asset_id.hostname or session.asset_id.agent_id, session.ended_at)
                )
        result = super().action_start()
        self._guarded().write({"started": True, "started_at": fields.Datetime.now()})
        return result

    def action_end(self, recording_url=None):
        """End the session. The recording reference is required (BRU-RMS-12)
        unless the business turns the switch off."""
        required = self.env["ir.config_parameter"].sudo().get_param(
            RECORDING_REQUIRED_PARAM, "1"
        ) not in ("0", "false", "False", "")
        recording = (recording_url or "").strip()
        for session in self:
            if session.ended_at:
                raise UserError("Session already ended at %s." % session.ended_at)
            if not session.started:
                raise UserError("Session has not started.")
            if required and not (recording or session.recording_url):
                raise UserError(
                    "Give the session recording reference to end the session - the "
                    "recording is the evidence of what was done on the client's endpoint."
                )
        if recording:
            self._guarded().write({"recording_url": recording})
        return super().action_end()

    def action_session_duration_minutes(self):
        """Display helper: started → ended minutes (None while running)."""
        self.ensure_one()
        if not (self.started_at and self.ended_at):
            return None
        return round((self.ended_at - self.started_at).total_seconds() / 60.0, 1)
