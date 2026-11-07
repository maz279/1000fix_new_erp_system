# fix_iot_ops — M48: streams, protocol adapters, threshold rules, downsampling,
# prescriptive actions and telemetry consent. Devices, telemetry rows, alerts and
# predictions live in fix_stream_registry.py.
import hashlib
import hmac
import math
import re
import secrets
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError

from libs.py.fix_events import publish

# A07 P1 (2026-11-04) M48-10 / D7: the spec's roles (§13). Every permission
# used to come from base.group_user. The groups ship with the dev admin as a
# member only; appointing the real holders is decision B1.
IOT_OPERATOR = "cd_stream_registry.group_iot_operator"  # R13 remote support
IOT_ADMIN = "cd_stream_registry.group_iot_admin"  # R33 IT / system administrator
IOT_MANAGER = "cd_stream_registry.group_iot_manager"  # R02 CTO
IOT_CONSENT = "cd_stream_registry.group_iot_consent_officer"  # R04 CCO / R22


def _has_role(env, xmlid):
    return env.su or env.user.has_group(xmlid)


def _require_role(env, xmlid, what):
    """Refuse `what` unless the caller holds `xmlid` (superuser is trusted)."""
    if not _has_role(env, xmlid):
        group = env.ref(xmlid, raise_if_not_found=False)
        raise AccessError("%s requires the %s role." % (what, group.name if group else xmlid))


class IngestRefused(UserError):
    """A gate in FixIotStream.ingest said no. `code` is what the gateway route
    answers with; the message, which may name a customer, stays in the server."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


# A generated key carries 256 bits, so a plain digest is enough: there is nothing
# to guess, and a slow hash would be paid on every reading.
MIN_ADAPTER_KEY_LENGTH = 32


def adapter_key_hash(key):
    return hashlib.sha256((key or "").encode("utf-8")).hexdigest()


def adapter_key_matches(stored, hashed):
    """Constant-time; an adapter with no stored key matches nothing."""
    return hmac.compare_digest(stored or "!", hashed or "?")


def _flag(env, param, default="0"):
    return (env["ir.config_parameter"].sudo().get_param(param) or default).strip() == "1"


# A07 P1 (2026-11-04) business switches (ir.config_parameter, safe default):
# - dwell: FR-IOT-031 "sustained for N minutes" before a rule alerts. Off by
#   default, so a breach always alerts on the first reading (nothing is held
#   back); on, a rule with duration_min > 0 alerts only once the breach has
#   lasted that long. The business confirms per estate (B5).
DWELL_PARAM = "cd_stream_registry.rule_dwell_enforced"
# - retention purge: the retention cron always rolls raw readings up into the
#   policy's aggregates and measures the compression; it DELETES raw readings
#   past the stream's retention (only where an aggregate covers them,
#   BRU-IOT-07) and aggregates past the policy's retention only when this is
#   "1". Deletion is irreversible and the retention periods on fix_dev are seed
#   defaults nobody has confirmed (B5: retention per stream).
RETENTION_PURGE_PARAM = "cd_stream_registry.retention_purge_enabled"
# A stream is silent when no reading arrived for SILENCE_FACTOR sample
# intervals, and never sooner than SILENCE_MIN_SECONDS (AUT-IOT-03). Defaults
# the business must confirm (B2); the spec gives no number.
SILENCE_FACTOR = 3
SILENCE_MIN_SECONDS = 300

# A07 audit (2026-11-03) M48-1: which streams need a telemetry consent before
# ingest. "customer" (default) exempts only devices positively identified as
# company facility / equipment sensors; "all" requires a consent on every
# stream. Any other value is treated as "all" (fail closed). Live fix_dev has
# no consent on any device, so "all" would stop every live stream on deploy:
# whether facility sensors are exempt is the business's call.
CONSENT_SCOPE_PARAM = "cd_stream_registry.consent_required_for"

# Metric tokens that reveal where a person or vehicle is (BRU-IOT-18): a
# location signal is personal data whatever the device is bound to.
_LOCATION_TOKENS = frozenset(
    {
        "gps",
        "lat",
        "lon",
        "lng",
        "latitude",
        "longitude",
        "location",
        "geo",
        "geolocation",
        "position",
        "coords",
        "heading",
    }
)


def _is_location_metric(metric):
    tokens = [t for t in re.split(r"[^a-z0-9]+", (metric or "").lower()) if t]
    return any(t in _LOCATION_TOKENS or t.startswith("gps") for t in tokens)


# scheme://user:password@host - a credential typed into a URL (M48-4).
_URL_SECRET = re.compile(r"://[^/@\s:]+:[^/@\s]+@")


# A07 P0 recipe (2026-11-03) M48-2: who approves a prescriptive action. Spec
# §13 gives R05 Operations Director the approval of proactive interventions.
# A07 P1 (2026-11-04): the Operations Director role is M47's
# (cd_facility.group_operations_director, a dependency of this module). A
# fix.approval.matrix row (decision domain iot_prescriptive_action) can name
# another group without code.
# A07 (2026-11-07): the fallback to DOFA Tier 2 was dead code, the group always
# being installed; on live nobody holds it, so no action could be approved. The
# fallback now applies when the group has no active holder in the record's company.
ACTION_APPROVER_GROUP = "cd_facility.group_operations_director"
ACTION_APPROVER_FALLBACK = "cd_entity_config.group_dofa_tier_2"
# M48-3: BRU-IOT-15/16 make the CTO the approver of a rule suppression. P0 used
# DOFA Tier 4 as a stand-in; A07 P1 (2026-11-04) points it at the spec's own
# role, the IoT Manager (CTO) group. A matrix row (decision domain
# iot_rule_suppression) can still name another group.
SUPPRESSION_APPROVER_GROUP = IOT_MANAGER
# BRU-IOT-06 / FR-IOT-025: retention, compression and aggregation changes need
# CTO approval (A07 P1).
RETENTION_APPROVER_GROUP = IOT_MANAGER


def _assert_authority(rec, xmlid, what):
    """The deciding user (the absent approver when a delegate decides) must
    hold the group the request was routed to: the matrix row's group when one
    names it and that group implies `xmlid` (a rule may only narrow who
    decides, A11 audit E3), otherwise `xmlid`. Superuser code is trusted."""
    if rec.env.su:
        return
    row = rec.approval_request_id.sudo().matrix_id
    coded = rec.env.ref(xmlid, raise_if_not_found=False)
    if not coded:
        raise UserError("%s: the approving group %s is not installed." % (what, xmlid))
    narrowed = row.approver_group_id
    group = narrowed if narrowed and coded in narrowed.sudo().all_implied_ids else coded
    if rec._approval_authority_user() not in group.sudo().all_user_ids:
        raise UserError("%s requires %s authority." % (what, group.display_name))


class FixApprovalMatrix(models.Model):
    """The M48 decisions the approval engine (M63) routes."""

    _inherit = "fix.approval.matrix"

    decision_domain = fields.Selection(
        selection_add=[
            ("iot_prescriptive_action", "IoT Prescriptive Action"),
            ("iot_rule_suppression", "IoT Alert Rule Suppression"),
            ("iot_retention_policy", "IoT Retention / Downsampling Policy Change"),
        ],
        ondelete={
            "iot_prescriptive_action": "cascade",
            "iot_rule_suppression": "cascade",
            "iot_retention_policy": "cascade",
        },
    )


# A07 (2026-11-07): what a stream reads. Telemetry belongs to a stream through
# its device AND metric, so moving either on a stream past draft re-labels every
# reading it has taken.
_STREAM_IDENTITY = frozenset({"device_id", "metric"})
_CONSENT_POLICIES = {
    "inherit": "inherit",
    "module default": "inherit",
    "required": "required",
    "consent always required": "required",
}


class FixIotStream(models.Model):
    _name = "fix.iot.stream"
    _description = "IoT Stream Binding"
    _inherit = ["mail.thread", "fix.guarded.mixin"]
    _order = "device_id, metric"

    def _fix_guarded_fields(self) -> set:
        # A07 P0 recipe (2026-11-03): a stream could be born `active` or have
        # its state written directly, skipping the activate/suspend checks.
        guarded = super()._fix_guarded_fields() | {"state", "activated_on"}
        # A07 P1 (2026-11-04) BRU-IOT-06: an existing stream's raw retention
        # changes only through an approved fix.iot.retention.change. A new
        # stream is born with its retention (an empty recordset is a create).
        return guarded | {"retention_days"} if self else guarded

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(s.state != "draft" for s in self):
            locked |= _STREAM_IDENTITY
        return locked

    name = fields.Char(required=True, default="New")
    device_id = fields.Many2one(
        "fix.iot.device", string="Device", required=True, ondelete="cascade", index=True
    )
    # A07 P1 (2026-11-04) M48-9: the stream had no company, so no record rule
    # could isolate it; it belongs to its device's company.
    company_id = fields.Many2one(
        related="device_id.company_id", string="Company", store=True, index=True
    )
    equipment_id = fields.Many2one(related="device_id.equipment_id", string="Equipment", store=True)
    site_id = fields.Many2one(related="device_id.site_id", string="Site", store=True)
    adapter_id = fields.Many2one("fix.iot.adapter", string="Protocol Adapter", ondelete="set null")
    metric = fields.Char(required=True, help="e.g. temperature, vibration, battery_pct")
    unit = fields.Char()
    sample_interval_sec = fields.Integer(string="Sample Interval (s)", default=60, required=True)
    retention_days = fields.Integer(string="Raw Retention (days)", default=90, required=True)
    # A07 P1 (2026-11-04) B5: the consent policy of THIS stream. "inherit" uses
    # the module default (CONSENT_SCOPE_PARAM, as in P0); "required" demands a
    # valid consent whatever the device is bound to. Tightening is open to the
    # stream's administrator; relaxing back needs the Consent Officer (spec §13:
    # consent policy is separated from collection configuration).
    consent_policy = fields.Selection(
        [("inherit", "Module Default"), ("required", "Consent Always Required")],
        string="Consent Policy",
        required=True,
        default="inherit",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("active", "Active"),
            ("silent", "Silent"),
            ("suspended", "Suspended"),
        ],
        required=True,
        default="draft",
    )
    activated_on = fields.Datetime(string="Activated On", readonly=True, copy=False)
    last_seen = fields.Datetime(related="device_id.last_telemetry", string="Last Seen")
    # A07 audit (2026-11-03) M48-8: this was One2many(..., "device_id"), which
    # matched the STREAM's id against telemetry.device_id and so listed another
    # device's rows. Telemetry has no stream link; a stream's readings are its
    # device's readings of its metric.
    telemetry_ids = fields.Many2many(
        "fix.iot.telemetry", compute="_compute_telemetry_ids", string="Telemetry"
    )
    rule_ids = fields.One2many("fix.iot.rule", "stream_id", string="Alert Rules")
    gap_ids = fields.One2many("fix.iot.gap", "stream_id", string="Gaps")

    _interval_positive = models.Constraint(
        "CHECK (sample_interval_sec > 0)", "The sample interval must be positive"
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.iot.stream") or "STRM/New"
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            for rec in self.filtered(lambda s: s.state != "draft"):
                changed = [
                    n
                    for n in _STREAM_IDENTITY & set(vals)
                    if rec._fix_guard_differs(n, vals[n], rec[n])
                ]
                if changed:
                    raise UserError(
                        "Stream %s is %s: its %s can no longer change, or the readings it holds "
                        "would be credited to something else. Register a new stream."
                        % (
                            rec.name,
                            dict(self._fields["state"].selection)[rec.state].lower(),
                            ", ".join(sorted(self._fields[n].string for n in changed)),
                        )
                    )
        if self and not self._fix_guard_open() and "consent_policy" in vals:
            relaxing = vals["consent_policy"] != "required" and any(
                rec._fix_guard_differs("consent_policy", vals["consent_policy"], rec.consent_policy)
                for rec in self
            )
            if relaxing:
                _require_role(self.env, IOT_CONSENT, "Relaxing a stream's consent policy")
        return super().write(vals)

    def action_set_consent_policy(self, policy=None, reason=None):
        """A07 (2026-11-07): the Consent Officer decides a stream's consent policy.
        Relaxing was refused to the Administrator, who holds the write access, and
        the officer has no write access, so nobody could. Written as the platform
        once the role is checked; the decision and why are in the chatter."""
        _require_role(self.env, IOT_CONSENT, "Changing a stream's consent policy")
        code = _CONSENT_POLICIES.get((policy or "").strip().lower())
        if not code:
            raise UserError(
                "Choose the consent policy: inherit (the module default) or required "
                "(consent always required)."
            )
        why = (reason or "").strip()
        if not why:
            raise UserError("Give the reason for changing the consent policy.")
        labels = dict(self._fields["consent_policy"].selection)
        for rec in self:
            if rec.consent_policy == code:
                raise UserError("Stream %s already uses this policy." % rec.name)
            before = rec.consent_policy
            rec.sudo()._guarded().write({"consent_policy": code})
            rec.sudo().message_post(
                body="Consent policy changed from %s to %s by %s: %s"
                % (labels[before], labels[code], self.env.user.name, why)
            )
        return True

    @api.depends("device_id", "metric")
    def _compute_telemetry_ids(self):
        Telemetry = self.env["fix.iot.telemetry"]
        for rec in self:
            rec.telemetry_ids = (
                Telemetry.search(
                    [("device_id", "=", rec.device_id.id), ("metric", "=", rec.metric)]
                )
                if rec.device_id and rec.metric
                else Telemetry
            )

    # ---- consent (BRU-IOT-03/05) ------------------------------------------
    def _fix_consent_reason(self, consents):
        """Why this stream needs a valid consent before ingest, or "" if exempt.

        `consents` are the consent records covering the device that COUNT: a
        verified grant (whatever its state now) or any revocation. A consent a
        non-officer recorded and nobody verified grants nothing yet."""
        self.ensure_one()
        if self.consent_policy == "required":
            return "the stream's own consent policy requires one"
        scope = self.env["ir.config_parameter"].sudo().get_param(CONSENT_SCOPE_PARAM) or "customer"
        device = self.device_id
        if scope != "customer":
            return "the consent policy (%s=%s) covers every stream" % (CONSENT_SCOPE_PARAM, scope)
        if device.partner_id:
            return "the device belongs to customer %s" % device.partner_id.display_name
        if device.device_type == "tracker" or _is_location_metric(self.metric):
            return "the stream carries a location signal"
        if not (device.equipment_id or device.site_id):
            # Not shown to be company equipment or a company site, so it
            # cannot claim the facility-sensor exemption.
            return "the device is bound to no company equipment or site"
        if consents:
            # Once a consent was recorded for the subject, its revocation or
            # expiry must stop collection; the exemption cannot outlive it.
            return "a consent was recorded for this device"
        return ""

    def _fix_check_consent(self):
        """A07 audit (2026-11-03) M48-1 / BRU-IOT-03: refuse ingest unless a
        valid consent covers the device. Applies to every caller, superuser
        included: consent is a data-protection rule, not a permission.
        A07 P1: the consent must be verified, and must disclose the stream's
        signal when it names its signals (BRU-IOT-05)."""
        Consent = self.env["fix.iot.consent"]
        for rec in self:
            consents = Consent._fix_for_device(rec.device_id).filtered(lambda c: c._fix_counts())
            reason = rec._fix_consent_reason(consents)
            if not reason:
                continue
            valid = consents.filtered(lambda c: c._fix_is_valid())
            if not valid:
                raise IngestRefused(
                    "consent_required",
                    "Ingest refused on stream %s: no active, verified, in-date telemetry "
                    "consent covers device %s, and one is required because %s. Record a "
                    "consent for the device, its site or its customer (a Consent Officer "
                    "verifies it) first." % (rec.name, rec.device_id.display_name, reason),
                )
            if not valid.filtered(lambda c, m=rec.metric: c._fix_permits(m)):
                raise IngestRefused(
                    "signal_not_disclosed",
                    "Ingest refused on stream %s: the consent covering device %s does not "
                    "disclose the signal '%s' (BRU-IOT-05: collecting an undisclosed signal "
                    "is a data-protection incident)."
                    % (rec.name, rec.device_id.display_name, rec.metric),
                )

    # ---- lifecycle ----------------------------------------------------------
    def _fix_check_bound(self):
        """A07 P1 (2026-11-04) BRU-IOT-02 / FR-IOT-001: a stream binds to one
        asset identity. The device must monitor M45 equipment or an M47 site."""
        for rec in self:
            device = rec.device_id
            if not (device.equipment_id or device.site_id):
                raise UserError(
                    "Stream %s cannot be activated: device %s is bound to no asset. Set its "
                    "M45 equipment or M47 site first (BRU-IOT-02)."
                    % (rec.name, device.display_name)
                )

    def action_activate(self):
        for rec in self:
            if rec.state in ("active", "silent"):
                raise UserError("Stream is already active")
            rec._fix_check_bound()
            rec._guarded().write({"state": "active", "activated_on": fields.Datetime.now()})

    def action_suspend(self):
        for rec in self:
            if rec.state not in ("active", "silent"):
                raise UserError("Suspend an active stream")
            rec._guarded().write({"state": "suspended"})

    def _fix_suspend(self, reason):
        """Suspend these streams as the platform (consent revoked or lapsed),
        and tell M05/M07/M60 (spec §12.3 telemetry.stream_suspended)."""
        for rec in self.sudo().filtered(lambda s: s.state in ("active", "silent")):
            rec.write({"state": "suspended"})
            rec.gap_ids.filtered(lambda g: g.state == "open")._fix_close(fields.Datetime.now())
            publish(
                rec.env,
                "telemetry.stream_suspended",
                "fix.iot.stream",
                rec.id,
                {
                    "stream": rec.name,
                    "device": rec.device_id.device_id,
                    "metric": rec.metric,
                    "equipment_id": rec.equipment_id.id or False,
                    "site_id": rec.site_id.id or False,
                    "reason": reason,
                },
            )

    def _fix_check_adapter(self):
        """A07 P1 (2026-11-04) M48-4 / FR-IOT-009: a disabled adapter stops
        ingest, and no reading arrives through an unauthenticated one. A07
        (2026-11-07): nor through one whose key was never rotated, whatever its
        state: the auth mode was checked, a credential never."""
        for rec in self:
            adapter = rec.adapter_id.sudo()
            if not adapter:
                continue
            if adapter.state != "enabled":
                raise IngestRefused(
                    "adapter_disabled",
                    "Ingest refused on stream %s: its protocol adapter %s is disabled."
                    % (rec.name, adapter.name),
                )
            if adapter.auth_mode == "none":
                raise IngestRefused(
                    "adapter_unauthenticated",
                    "Ingest refused on stream %s: its protocol adapter %s accepts "
                    "unauthenticated devices (auth mode None)." % (rec.name, adapter.name),
                )
            if not adapter.api_key_hash:
                raise IngestRefused(
                    "adapter_no_key",
                    "Ingest refused on stream %s: its protocol adapter %s has no key. An IoT "
                    "Administrator rotates one first." % (rec.name, adapter.name),
                )

    def ingest(self, value, timestamp=None):
        """Record one reading and evaluate the stream's active threshold rules.

        A07 P1 (2026-11-04) M48-4: only the IoT Administrator role (or the
        superuser gateway service) ingests; the adapter must be enabled and
        authenticated; `timestamp` is the source's own time stamp when the
        gateway sends one (deduplicated on device, signal and time, FR-IOT-018),
        otherwise the server stamps the reading."""
        self.ensure_one()
        _require_role(self.env, IOT_ADMIN, "Ingesting telemetry")
        if self.state not in ("active", "silent"):
            raise IngestRefused("stream_not_active", "Ingest requires an active stream")
        self._fix_check_adapter()
        self._fix_check_consent()
        try:
            value = float(value)
        except (TypeError, ValueError) as exc:
            raise IngestRefused("invalid_value", "A telemetry reading must be a number.") from exc
        if not math.isfinite(value):
            raise IngestRefused("invalid_value", "A telemetry reading must be a finite number.")
        stream = self.sudo()
        vals = {
            "company_id": stream.device_id.company_id.id,
            "operating_unit_id": stream.device_id.operating_unit_id.id,
            "device_id": stream.device_id.id,
            "metric": stream.metric,
            "value": value,
            "unit": stream.unit,
        }
        if timestamp:
            vals["timestamp"] = timestamp
        # Telemetry refuses a direct create() by a plain user (it skipped this
        # consent check and the rule engine); this service writes it after its
        # own checks. The record handed back carries no token and no sudo.
        reading = self.env["fix.iot.telemetry"].sudo()._guarded().create(vals)
        ts = reading.timestamp
        stream.device_id._fix_telemetry_received("online", ts)
        if stream.state == "silent":
            # FR-IOT-028: the gap is recorded permanently; the stream resumes.
            stream.write({"state": "active"})
            stream.gap_ids.filtered(lambda g: g.state == "open")._fix_close(ts)
        # An expired suppression ends here as well as in the daily cron, so a
        # lapsed pause or loosened threshold never hides a reading.
        stream.rule_ids._fix_lapse_suppressions()
        raised = stream.rule_ids.filtered(lambda r: r.state == "active")._fix_evaluate(
            stream, value, ts
        )
        return (
            self.env["fix.iot.telemetry"].browse(reading.id),
            self.env["fix.iot.alert"].browse(raised.ids),
        )

    # ---- liveness (AUT-IOT-03, BRU-IOT-09) ------------------------------------
    def _fix_silence_after(self):
        self.ensure_one()
        return timedelta(
            seconds=max((self.sample_interval_sec or 60) * SILENCE_FACTOR, SILENCE_MIN_SECONDS)
        )

    def _fix_latest_readings(self):
        """{(device id, metric): latest timestamp} for these streams."""
        if not self:
            return {}
        groups = (
            self.env["fix.iot.telemetry"]
            .sudo()
            ._read_group(
                [
                    ("device_id", "in", self.device_id.ids),
                    ("timestamp", "<=", fields.Datetime.now()),
                ],
                ["device_id", "metric"],
                ["timestamp:max"],
            )
        )
        return {(device.id, metric): last for device, metric, last in groups}

    @api.model
    def cron_liveness(self):
        """A07 P1 (2026-11-04) D9: a stream with no reading for its silence
        window turns `silent`, a gap is opened and the owning modules are told
        (telemetry.stream_silent); a device whose every live stream fell silent
        goes offline with an alert. Silent is never shown as a zero
        (BRU-IOT-09). Idempotent: a silent stream is not re-flagged."""
        now = fields.Datetime.now()
        streams = self.sudo().search([("state", "=", "active")])
        latest = streams._fix_latest_readings()
        silenced = self.browse()
        for stream in streams:
            last = latest.get((stream.device_id.id, stream.metric))
            since = last or stream.activated_on or stream.write_date
            if since and now - since > stream._fix_silence_after():
                stream.write({"state": "silent"})
                gap = (
                    self.env["fix.iot.gap"]
                    .sudo()
                    .create(
                        {
                            "stream_id": stream.id,
                            "gap_from": since,
                            "detected_at": now,
                            "cause": "device_silent",
                            "had_reading": bool(last),
                        }
                    )
                )
                publish(
                    stream.env,
                    "telemetry.stream_silent",
                    "fix.iot.stream",
                    stream.id,
                    {
                        "stream": stream.name,
                        "device": stream.device_id.device_id,
                        "metric": stream.metric,
                        "equipment_id": stream.equipment_id.id or False,
                        "site_id": stream.site_id.id or False,
                        "last_point": fields.Datetime.to_string(last) if last else None,
                        "gap": gap.name,
                        "cause": "device_silent",
                    },
                )
                silenced |= stream
        for device in silenced.device_id:
            live = self.sudo().search_count(
                [("device_id", "=", device.id), ("state", "=", "active")]
            )
            if not live and device.status != "offline":
                device._fix_mark_offline()
        return len(silenced)


class FixIotAdapter(models.Model):
    _name = "fix.iot.adapter"
    _description = "IoT Protocol Adapter"
    _inherit = ["fix.guarded.mixin"]
    _order = "name"

    def _fix_guarded_fields(self) -> set:
        # A07 P0 recipe (2026-11-03): the enabled/disabled flag changes only
        # through action_enable / action_disable.
        return super()._fix_guarded_fields() | {
            "state",
            "disabled_by",
            "disabled_on",
            "disable_reason",
            "api_key_hash",
            "key_rotated_by",
            "key_rotated_on",
            "credential_rotated_on",
        }

    name = fields.Char(required=True, default="New")
    # A07 P1 (2026-11-04) M48-9: an adapter may be shared protocol
    # configuration (no company) or one company's own.
    company_id = fields.Many2one("res.company", string="Company", index=True)
    protocol = fields.Selection(
        [
            ("mqtt", "MQTT"),
            ("http", "HTTPS Webhook"),
            ("modbus", "Modbus TCP"),
            ("opcua", "OPC-UA"),
            ("lorawan", "LoRaWAN"),
        ],
        required=True,
        default="mqtt",
    )
    endpoint = fields.Char(help="Broker or collector URL recorded for configuration")
    auth_mode = fields.Selection(
        [("none", "None"), ("token", "Bearer Token"), ("certificate", "Mutual TLS")],
        required=True,
        default="token",
    )
    # A07 P1 (2026-11-04) M48-4 / FR-IOT-003: where the credential lives. A
    # REFERENCE to the secret store (vault path, certificate fingerprint),
    # never the secret itself; there was no credential field at all, so a
    # secret could only sit in the free-text endpoint.
    credential_ref = fields.Char(
        string="Credential Reference",
        help="Secret-store reference or certificate fingerprint. Never the secret itself.",
    )
    credential_rotated_on = fields.Date(string="Credential Rotated On", readonly=True)
    # A07 (2026-11-07): the key POST /iot/v1/ingest checks, as a hash: the key
    # itself is shown once, by action_rotate_key, and never stored.
    api_key_hash = fields.Char(
        string="Key Hash", readonly=True, copy=False, groups=IOT_ADMIN, prefetch=False
    )
    key_set = fields.Boolean(string="Key Set", compute="_compute_key_set")
    key_rotated_by = fields.Many2one(
        "res.users", string="Key Rotated By", readonly=True, copy=False
    )
    key_rotated_on = fields.Datetime(string="Key Rotated On", readonly=True, copy=False)
    # A07 (2026-11-07): an adapter was born enabled with no credential. New ones
    # are born disabled; stored rows keep their state, and ingest refuses any
    # adapter with no key.
    state = fields.Selection(
        [("enabled", "Enabled"), ("disabled", "Disabled")], required=True, default="disabled"
    )
    disabled_by = fields.Many2one("res.users", string="Disabled By", readonly=True, copy=False)
    disabled_on = fields.Datetime(string="Disabled On", readonly=True, copy=False)
    disable_reason = fields.Char(string="Disable Reason", readonly=True, copy=False)
    stream_ids = fields.One2many("fix.iot.stream", "adapter_id", string="Streams")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.iot.adapter") or "IADP/New"
        return super().create(vals_list)

    # A07 P1 (2026-11-04) M48-4: an enabled adapter with auth_mode=none was
    # accepted, and a password could be typed into the endpoint URL.
    @api.constrains("state", "auth_mode")
    def _check_authenticated(self):
        for rec in self:
            if rec.state == "enabled" and rec.auth_mode == "none":
                raise ValidationError(
                    "Adapter %s cannot be enabled without authentication: choose Bearer "
                    "Token or Mutual TLS (FR-IOT-009 per-device authentication)." % rec.name
                )

    @api.constrains("endpoint")
    def _check_endpoint_has_no_secret(self):
        for rec in self:
            if rec.endpoint and _URL_SECRET.search(rec.endpoint):
                raise ValidationError(
                    "The endpoint of adapter %s carries a user name and password. Record the "
                    "credential in the secret store and put its reference in Credential "
                    "Reference instead." % rec.name
                )

    def _compute_key_set(self):
        for rec in self:
            rec.key_set = bool(rec.sudo().api_key_hash)

    def action_rotate_key(self, key=None):
        """Set a new key; the old one stops working at once. The key is generated
        and shown once, and only its hash is kept. `key`, when given, is one the
        Administrator made in the secret store: it is not shown back."""
        _require_role(self.env, IOT_ADMIN, "Rotating an adapter key")
        self.ensure_one()
        if self.auth_mode == "none":
            raise UserError(
                "Adapter %s accepts no authentication: choose Bearer Token or Mutual TLS first."
                % self.name
            )
        supplied = (key or "").strip()
        if supplied and len(supplied) < MIN_ADAPTER_KEY_LENGTH:
            raise UserError(
                "A key must have at least %d characters. Leave it blank to have one generated."
                % MIN_ADAPTER_KEY_LENGTH
            )
        secret = supplied or secrets.token_urlsafe(32)
        self.sudo()._guarded().write(
            {
                "api_key_hash": adapter_key_hash(secret),
                "key_rotated_by": self.env.uid,
                "key_rotated_on": fields.Datetime.now(),
                "credential_rotated_on": fields.Date.context_today(self),
            }
        )
        if supplied:
            return {"note": "The new key of adapter %s is in force." % self.name}
        return {
            "note": "New key of adapter %s, shown only now: %s" % (self.name, secret),
            "secret": secret,
        }

    def action_enable(self):
        _require_role(self.env, IOT_ADMIN, "Enabling a protocol adapter")
        for rec in self:
            if rec.state != "disabled":
                raise UserError("Enable a disabled adapter")
            if rec.auth_mode != "none" and not (rec.credential_ref or "").strip():
                raise UserError(
                    "Record the credential reference of adapter %s before enabling it." % rec.name
                )
            if not rec.sudo().api_key_hash:
                raise UserError("Rotate a key for adapter %s before enabling it." % rec.name)
            rec._guarded().write(
                {
                    "state": "enabled",
                    "disabled_by": False,
                    "disabled_on": False,
                    "disable_reason": False,
                }
            )

    def action_disable(self, reason=None):
        """A07 P1 (2026-11-04): any internal user may pull an adapter's plug
        (it only stops collection, the fail-safe direction); who did it, when
        and why is stamped, and only the IoT Administrator turns it back on."""
        if not (self.env.su or self.env.user._is_internal()):
            raise AccessError("Only internal users can disable a protocol adapter.")
        uid = self.env.uid
        for rec in self:
            if rec.state != "enabled":
                raise UserError("Disable an enabled adapter")
            rec.sudo()._guarded().write(
                {
                    "state": "disabled",
                    "disabled_by": uid,
                    "disabled_on": fields.Datetime.now(),
                    "disable_reason": (reason or "").strip() or False,
                }
            )


# A rule's terms: an existing rule's threshold moves only through
# action_change_threshold, and its operator and stream not at all (turning
# "> 5" into "< 5", or moving the rule to another stream, silences it as surely
# as a 1e9 threshold). A new rule is born with all three. A07 (2026-11-07): so
# do a huge cooldown, a long dwell and a downgraded severity silence it. They
# change through action_change_settings, on the same terms as the threshold.
_RULE_SETTINGS = ("severity", "duration_min", "cooldown_min")
_RULE_TERMS = frozenset({"threshold", "operator", "stream_id", *_RULE_SETTINGS})
_SEVERITY_RANK = {"minor": 0, "major": 1}
# The suppression proposal the requester fills in; frozen while it is pending
# approval or in force.
_RULE_PROPOSAL = frozenset({"suppression_reason", "suppression_until"})


class FixIotRule(models.Model):
    _name = "fix.iot.rule"
    _description = "IoT Threshold Alert Rule"
    # fix.approvable.mixin already sits in front of fix.guarded.mixin.
    _inherit = ["fix.approvable.mixin"]
    _order = "stream_id, name"

    # A07 P0 recipe (2026-11-03) M48-3 / BRU-IOT-15/16: any user paused a major
    # rule, or wrote its threshold to 1e9 while it stayed "active", with no
    # reason, approver or expiry, and the breaching readings then raised
    # nothing. Pausing or loosening is now a suppression: a reason and an
    # expiry, routed through the engine to someone who is neither the
    # requester nor the rule's author (spec §13 SoD). Tightening applies at
    # once. action_approve_suppression is the apply method; it runs only from
    # the approver's inbox.
    _approval_domain = "iot_rule_suppression"
    _approval_apply_method = "action_approve_suppression"
    _approval_group = SUPPRESSION_APPROVER_GROUP
    _approval_routed = True

    def _fix_guarded_fields(self) -> set:
        guarded = super()._fix_guarded_fields() | {
            "state",
            "baseline_threshold",
            "proposed_threshold",
            "proposed_severity",
            "proposed_duration_min",
            "proposed_cooldown_min",
            "baseline_severity",
            "baseline_duration_min",
            "baseline_cooldown_min",
            "suppression_kind",
            "suppression_requested_by",
            "suppressed_by",
            "suppressed_on",
            # A07 P1: the evaluator's own bookkeeping (dwell, cooldown).
            "breach_since",
            "last_alert_on",
            "cooldown_suppressed",
        }
        # An empty recordset is a rule being created (the guard's create and
        # the P03 form of a new record): it is born with its terms.
        return guarded | _RULE_TERMS if self else guarded

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(r._fix_suppression_frozen() for r in self):
            locked |= _RULE_PROPOSAL
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open():
            touched = _RULE_PROPOSAL & set(vals)
            for rec in self.filtered(lambda r: r._fix_suppression_frozen()):
                if [n for n in touched if rec._fix_guard_differs(n, vals[n], rec[n])]:
                    raise UserError(
                        "Rule %s has a suppression pending approval or in force: its reason "
                        "and expiry are frozen. Recall the request or lift the suppression "
                        "first." % rec.name
                    )
        return super().write(vals)

    name = fields.Char(required=True, default="New")
    stream_id = fields.Many2one(
        "fix.iot.stream", string="Stream", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(
        related="stream_id.company_id", string="Company", store=True, index=True
    )
    operator = fields.Selection(
        [("gt", ">"), ("gte", ">="), ("lt", "<"), ("lte", "<=")],
        required=True,
        default="gt",
    )
    threshold = fields.Float(required=True)
    severity = fields.Selection(
        [("minor", "Minor"), ("major", "Major")], required=True, default="minor"
    )
    duration_min = fields.Integer(string="For (minutes)", default=0)
    cooldown_min = fields.Integer(string="Cooldown (minutes)", default=15)
    state = fields.Selection(
        [("active", "Active"), ("paused", "Paused")], required=True, default="active"
    )
    # Suppression (BRU-IOT-16): what is asked, why, until when, by whom, and
    # who approved it. In force = suppressed_by is set.
    suppression_kind = fields.Selection(
        [("pause", "Pause"), ("loosen", "Loosened Threshold"), ("settings", "Loosened Settings")],
        string="Suppression",
        readonly=True,
        copy=False,
    )
    suppression_reason = fields.Char(string="Suppression Reason", copy=False)
    suppression_until = fields.Date(
        string="Suppressed Until",
        copy=False,
        help="The suppression ends after this day; the rule then alerts again at its "
        "pre-suppression threshold.",
    )
    proposed_threshold = fields.Float(string="Proposed Threshold", readonly=True, copy=False)
    baseline_threshold = fields.Float(
        string="Threshold Before Suppression",
        readonly=True,
        copy=False,
        help="Restored when a loosened-threshold suppression is lifted or expires.",
    )
    _SEVERITIES = [("minor", "Minor"), ("major", "Major")]
    proposed_severity = fields.Selection(
        _SEVERITIES, string="Proposed Severity", readonly=True, copy=False
    )
    proposed_duration_min = fields.Integer(
        string="Proposed Sustained For (minutes)", readonly=True, copy=False
    )
    proposed_cooldown_min = fields.Integer(
        string="Proposed Cooldown (minutes)", readonly=True, copy=False
    )
    baseline_severity = fields.Selection(
        _SEVERITIES, string="Severity Before Suppression", readonly=True, copy=False
    )
    baseline_duration_min = fields.Integer(
        string="Sustained For Before Suppression", readonly=True, copy=False
    )
    baseline_cooldown_min = fields.Integer(
        string="Cooldown Before Suppression", readonly=True, copy=False
    )
    suppression_requested_by = fields.Many2one(
        "res.users", string="Suppression Requested By", readonly=True, copy=False
    )
    suppressed_by = fields.Many2one(
        "res.users", string="Suppression Approved By", readonly=True, copy=False
    )
    suppressed_on = fields.Datetime(string="Suppression Approved On", readonly=True, copy=False)
    # A07 P1 (2026-11-04) M48-3 / FR-IOT-031/033: duration_min and
    # cooldown_min were stored and never read (20 breaches raised 20 alerts).
    breach_since = fields.Datetime(string="Breaching Since", readonly=True, copy=False)
    last_alert_on = fields.Datetime(string="Last Alert Raised", readonly=True, copy=False)
    cooldown_suppressed = fields.Integer(
        string="Breaches Held by Cooldown",
        readonly=True,
        copy=False,
        help="Breaches that raised no new alert because the cooldown after the last "
        "alert had not elapsed.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.iot.rule") or "IRUL/New"
        return super().create(vals_list)

    @api.constrains("duration_min", "cooldown_min")
    def _check_windows(self):
        for rec in self:
            if (rec.duration_min or 0) < 0 or (rec.cooldown_min or 0) < 0:
                raise ValidationError("Dwell and cooldown cannot be negative.")

    def _fix_evaluate(self, stream, value, ts):
        """Evaluate these (active) rules against one reading of `stream`.

        A07 P1 (2026-11-04) P2 depth, FR-IOT-031/033 and AUT-IOT-09:
        - dedup: while the rule's last alert is open, a further breach adds an
          occurrence to it instead of raising another;
        - cooldown: after an alert, no new one for cooldown_min minutes;
        - dwell (DWELL_PARAM): the breach must have lasted duration_min.
        A reading that no longer breaches clears the dwell clock. Runs as the
        platform: the evaluation's effects belong to no user. Returns the new
        alerts."""
        Alert = self.env["fix.iot.alert"].sudo()
        dwell = _flag(self.env, DWELL_PARAM)
        raised = Alert
        for rule in self.sudo():
            if not rule.matches(value):
                if rule.breach_since:
                    rule.write({"breach_since": False})
                continue
            since = rule.breach_since or ts
            vals = {} if rule.breach_since else {"breach_since": ts}
            if dwell and rule.duration_min and ts - since < timedelta(minutes=rule.duration_min):
                if vals:
                    rule.write(vals)
                continue
            open_alert = Alert.search(
                [("rule_id", "=", rule.id), ("state", "!=", "resolved")], order="id desc", limit=1
            )
            if open_alert:
                open_alert.write(
                    {
                        "occurrence_count": open_alert.occurrence_count + 1,
                        "last_occurrence_on": ts,
                        "last_value": value,
                    }
                )
                if vals:
                    rule.write(vals)
                continue
            if (
                rule.cooldown_min
                and rule.last_alert_on
                and ts - rule.last_alert_on < timedelta(minutes=rule.cooldown_min)
            ):
                vals["cooldown_suppressed"] = rule.cooldown_suppressed + 1
                rule.write(vals)
                continue
            alert = Alert.create(
                {
                    "company_id": stream.device_id.company_id.id,
                    "operating_unit_id": stream.device_id.operating_unit_id.id,
                    "device_id": stream.device_id.id,
                    "rule_id": rule.id,
                    "stream_id": stream.id,
                    "severity": rule.severity,
                    "trigger_value": value,
                    "last_value": value,
                    "last_occurrence_on": ts,
                    "message": "%s %s %s: reading %s %s"
                    % (
                        stream.metric,
                        dict(rule._fields["operator"].selection).get(rule.operator),
                        rule.threshold,
                        value,
                        stream.unit or "",
                    ),
                }
            )
            vals["last_alert_on"] = ts
            rule.write(vals)
            # FR-IOT-035: routed to the module owning the asset (bridge).
            publish(
                self.env,
                "iot.rule_alert_raised",
                "fix.iot.alert",
                alert.id,
                {
                    "alert": alert.name,
                    "rule": rule.name,
                    "stream": stream.name,
                    "device": stream.device_id.device_id,
                    "metric": stream.metric,
                    "equipment_id": stream.equipment_id.id or False,
                    "site_id": stream.site_id.id or False,
                    "severity": rule.severity,
                    "operator": rule.operator,
                    "threshold": rule.threshold,
                    "trigger_value": value,
                },
            )
            raised |= alert
        return raised

    @api.model
    def cron_lapse_suppressions(self):
        """A07 P1 (2026-11-04) BRU-IOT-16: a suppression ends at its expiry
        even on a stream that receives no reading (P0 lapsed it only on
        ingest). Idempotent."""
        rules = self.sudo().search([("suppressed_by", "!=", False)])
        before = len(rules)
        rules._fix_lapse_suppressions()
        return before - len(rules.filtered(lambda r: r.suppressed_by))

    def matches(self, value):
        self.ensure_one()
        if self.operator == "gt":
            return value > self.threshold
        if self.operator == "gte":
            return value >= self.threshold
        if self.operator == "lt":
            return value < self.threshold
        return value <= self.threshold

    # ---- suppression ------------------------------------------------------
    def _fix_looser(self, new, than):
        """Would threshold `new` alert on fewer readings than `than`?"""
        self.ensure_one()
        if self.operator in ("gt", "gte"):
            return new > than
        return new < than

    def _fix_suppression_in_force(self):
        self.ensure_one()
        return bool(self.suppressed_by)

    def _fix_suppression_frozen(self):
        self.ensure_one()
        return self.approval_state == "pending" or self._fix_suppression_in_force()

    def _fix_lift_vals(self):
        """Values that end any suppression and restore normal alerting."""
        self.ensure_one()
        vals = {
            "state": "active",
            "suppression_kind": False,
            "suppression_reason": False,
            "suppression_until": False,
            "proposed_threshold": 0.0,
            "baseline_threshold": 0.0,
            "suppression_requested_by": False,
            "suppressed_by": False,
            "suppressed_on": False,
            "approval_state": "none",
            **self._fix_proposal_cleared(),
            "baseline_severity": False,
            "baseline_duration_min": 0,
            "baseline_cooldown_min": 0,
        }
        if self.suppression_kind == "loosen" and self._fix_suppression_in_force():
            vals["threshold"] = self.baseline_threshold
        if self.suppression_kind == "settings" and self._fix_suppression_in_force():
            vals.update(
                {
                    "severity": self.baseline_severity,
                    "duration_min": self.baseline_duration_min,
                    "cooldown_min": self.baseline_cooldown_min,
                }
            )
        return vals

    @staticmethod
    def _fix_proposal_cleared():
        return {
            "proposed_severity": False,
            "proposed_duration_min": 0,
            "proposed_cooldown_min": 0,
        }

    def _fix_lapse_suppressions(self):
        """End every suppression on these rules whose expiry has passed. Runs
        as superuser: an expiry takes effect whoever triggers it (ingest now; a
        scheduler in P1)."""
        today = fields.Date.context_today(self)
        for rec in self.sudo():
            if (
                rec._fix_suppression_in_force()
                and rec.suppression_until
                and rec.suppression_until < today
            ):
                rec.write(rec._fix_lift_vals())

    def _fix_request_suppression(self, kind, reason=None, proposed_threshold=0.0, proposed=None):
        today = fields.Date.context_today(self)
        for rec in self:
            why = (reason or rec.suppression_reason or "").strip()
            if not why:
                raise UserError("A suppression of rule %s needs a reason." % rec.name)
            if not rec.suppression_until:
                raise UserError(
                    "A suppression of rule %s needs an expiry: set Suppressed Until first. "
                    "Indefinite suppression is not permitted." % rec.name
                )
            if rec.suppression_until < today:
                raise UserError("The suppression expiry of rule %s is in the past." % rec.name)
            if rec._fix_suppression_frozen():
                raise UserError("Rule %s already has a suppression pending or in force." % rec.name)
            if kind == "pause" and rec.state != "active":
                raise UserError("Pause an active rule")
            rec._guarded().write(
                {
                    "suppression_kind": kind,
                    "suppression_reason": why,
                    "proposed_threshold": proposed_threshold,
                    "suppression_requested_by": self.env.uid,
                    **(proposed or {}),
                }
            )
            rec.action_request_approval(justification=why)

    def _approval_needed(self) -> bool:
        return bool(self.suppression_kind) and not self._fix_suppression_in_force()

    def _fix_clear_request(self):
        """A suppression that did not come into force leaves nothing behind."""
        for rec in self.filtered(lambda r: not r._fix_suppression_in_force()):
            rec._guarded().write(
                {
                    "suppression_kind": False,
                    "proposed_threshold": 0.0,
                    "suppression_requested_by": False,
                    **rec._fix_proposal_cleared(),
                }
            )

    def _approval_on_rejected(self, comment):
        self._fix_clear_request()

    def _approval_clear_stamp(self, reason):
        # A07 (2026-11-07): a recalled or voided request kept its kind, so the rule
        # showed "Pause" for ever. The engine calls this on recall, void and reject.
        super()._approval_clear_stamp(reason)
        self._fix_clear_request()

    def action_pause(self, reason=None):
        """Request a pause: a suppression, decided from the approver's inbox."""
        self._fix_request_suppression("pause", reason)

    def action_change_threshold(self, threshold=None, reason=None):
        """Tightening applies at once; loosening is a suppression request."""
        try:
            new = float(threshold)
        except (TypeError, ValueError) as exc:
            raise UserError("Give the new threshold as a number.") from exc
        for rec in self:
            if abs(new - rec.threshold) < 1e-9:
                raise UserError("Rule %s already uses threshold %s." % (rec.name, new))
            if rec._fix_looser(new, rec.threshold):
                rec._fix_request_suppression("loosen", reason, proposed_threshold=new)
                continue
            vals = {"threshold": new}
            if rec._fix_suppression_in_force():
                if rec.suppression_kind == "loosen" and not rec._fix_looser(
                    new, rec.baseline_threshold
                ):
                    # As tight as before the suppression, or tighter: it is over.
                    vals = dict(rec._fix_lift_vals(), threshold=new)
            elif rec.approval_state == "pending":
                # The terms the approver is looking at have moved.
                rec._approval_void("the threshold was changed while the suppression was pending")
                vals.update(
                    {
                        "suppression_kind": False,
                        "proposed_threshold": 0.0,
                        "suppression_requested_by": False,
                    }
                )
            rec._guarded().write(vals)

    def _fix_settings_looser(self, proposed):
        """Would these settings alert on fewer readings, or less loudly?"""
        self.ensure_one()
        return (
            _SEVERITY_RANK[proposed["severity"]] < _SEVERITY_RANK[self.severity]
            or proposed["duration_min"] > (self.duration_min or 0)
            or proposed["cooldown_min"] > (self.cooldown_min or 0)
        )

    def _fix_parse_settings(self, severity, duration_min, cooldown_min):
        """The settings asked for, each kept as it is when left blank."""
        self.ensure_one()
        wanted = (severity or "").strip().lower() or self.severity
        if wanted not in _SEVERITY_RANK:
            raise UserError("Severity is minor or major.")
        out = {"severity": wanted}
        for name, value in (("duration_min", duration_min), ("cooldown_min", cooldown_min)):
            text = str(value).strip() if value not in (None, False) else ""
            if not text:
                out[name] = self[name] or 0
                continue
            try:
                out[name] = int(text)
            except ValueError as exc:
                raise UserError("Give the minutes as a whole number.") from exc
            if out[name] < 0:
                raise UserError("Dwell and cooldown cannot be negative.")
        return out

    def action_change_settings(
        self, severity=None, duration_min=None, cooldown_min=None, reason=None
    ):
        """Tightening applies at once; loosening is a suppression request, with a
        reason and an expiry, decided from the approver's inbox."""
        for rec in self:
            proposed = rec._fix_parse_settings(severity, duration_min, cooldown_min)
            if all(proposed[n] == (rec[n] or 0) for n in proposed):
                raise UserError("Rule %s already uses these settings." % rec.name)
            if rec._fix_suppression_frozen():
                raise UserError(
                    "Rule %s has a suppression pending approval or in force. Recall the request "
                    "or lift the suppression first." % rec.name
                )
            if rec._fix_settings_looser(proposed):
                rec._fix_request_suppression(
                    "settings",
                    reason,
                    proposed={"proposed_%s" % n: proposed[n] for n in _RULE_SETTINGS},
                )
            else:
                rec._guarded().write(proposed)
        return True

    def action_approve_suppression(self):
        """The M63 apply method: put the requested suppression in force."""
        self._approval_assert_routed()
        acting = self._approval_acting_users()
        today = fields.Date.context_today(self)
        now = fields.Datetime.now()
        for rec in self:
            if not rec.suppression_kind or rec._fix_suppression_in_force():
                raise UserError("Rule %s has no suppression request to approve." % rec.name)
            _assert_authority(rec, SUPPRESSION_APPROVER_GROUP, "Approving a rule suppression")
            if not self.env.su and acting & (rec.suppression_requested_by | rec.create_uid):
                raise UserError(
                    "The requester or the author of rule %s cannot approve its suppression."
                    % rec.name
                )
            if not rec.suppression_until or rec.suppression_until < today:
                raise UserError("The suppression of rule %s has already expired." % rec.name)
            vals = {"suppressed_by": self.env.uid, "suppressed_on": now}
            if rec.suppression_kind == "pause":
                if rec.state != "active":
                    raise UserError("Pause an active rule")
                vals["state"] = "paused"
            elif rec.suppression_kind == "settings":
                vals.update(
                    {
                        **{"baseline_%s" % n: rec[n] for n in _RULE_SETTINGS},
                        **{n: rec["proposed_%s" % n] for n in _RULE_SETTINGS},
                    }
                )
            else:
                if not rec._fix_looser(rec.proposed_threshold, rec.threshold):
                    raise UserError("The proposed threshold no longer loosens rule %s." % rec.name)
                vals.update(
                    {"baseline_threshold": rec.threshold, "threshold": rec.proposed_threshold}
                )
            rec._guarded().write(vals)

    def action_activate(self):
        """Resume a paused rule, or lift a loosened threshold: restoring alerting
        tightens, so it needs no approval."""
        for rec in self:
            if rec.state == "active" and not rec._fix_suppression_in_force():
                raise UserError("Rule %s is active with no suppression in force." % rec.name)
            if rec.approval_state == "pending":
                rec._approval_void("the rule was resumed while a suppression was pending")
            rec._guarded().write(rec._fix_lift_vals())


# The terms of an ACTIVE downsampling policy: they change only through an
# approved fix.iot.retention.change (BRU-IOT-06).
_POLICY_TERMS = frozenset(
    {"stream_id", "raw_interval_sec", "target_interval_sec", "aggregation", "retention_days"}
)


class FixIotDownsample(models.Model):
    _name = "fix.iot.downsample"
    _description = "IoT Downsampling Policy"
    _inherit = ["fix.guarded.mixin"]
    _order = "stream_id"

    # A07 P1 (2026-11-04) M48 BRU-IOT-06/07: action_activate was a bare
    # `state = "active"`, any user changed an active policy's retention, and a
    # typed compression_pct (99999 accepted) fed the Retention Compression KPI
    # while nothing compressed anything. A policy is drafted freely; turning it
    # on and changing an active one are CTO-approved changes
    # (fix.iot.retention.change); the compression is MEASURED by the retention
    # cron from the aggregates it actually wrote.
    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "activated_on",
            "rolled_until",
            "raw_points_rolled",
            "rollup_points",
            "measured_compression_pct",
            "last_rollup_on",
        }

    def _fix_change_open(self):
        """A retention change of this policy that is awaiting approval."""
        return (
            self.env["fix.iot.retention.change"]
            .sudo()
            .search([("downsample_id", "in", self.ids), ("state", "=", "requested")])
        )

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and (any(p.state == "active" for p in self) or self._fix_change_open()):
            locked |= _POLICY_TERMS
        return locked

    def write(self, vals):
        if self and not self._fix_guard_open():
            touched = _POLICY_TERMS & set(vals)
            for rec in self.filtered(lambda p: p.state == "active"):
                if [n for n in touched if rec._fix_guard_differs(n, vals[n], rec[n])]:
                    raise UserError(
                        "Downsampling policy %s is active: its terms change only through a "
                        "retention change approved by the CTO (BRU-IOT-06)." % rec.name
                    )
            # A07 (2026-11-07): the CTO approves the terms in front of them; they
            # stayed editable after Request Activation.
            for rec in self.filtered(lambda p: p._fix_change_open()):
                if [n for n in touched if rec._fix_guard_differs(n, vals[n], rec[n])]:
                    raise UserError(
                        "Downsampling policy %s is awaiting the CTO's approval: its terms are "
                        "frozen. Recall the request to change them." % rec.name
                    )
        return super().write(vals)

    name = fields.Char(required=True, default="New")
    stream_id = fields.Many2one(
        "fix.iot.stream", string="Stream", required=True, ondelete="cascade", index=True
    )
    company_id = fields.Many2one(
        related="stream_id.company_id", string="Company", store=True, index=True
    )
    raw_interval_sec = fields.Integer(string="Raw Interval (s)", required=True, default=60)
    target_interval_sec = fields.Integer(string="Target Interval (s)", required=True, default=300)
    aggregation = fields.Selection(
        [("avg", "Average"), ("min", "Minimum"), ("max", "Maximum"), ("last", "Last Value")],
        required=True,
        default="avg",
    )
    retention_days = fields.Integer(string="Compressed Retention (days)", default=730)
    # The DESIGN reduction this policy would give (1 - raw / target). A
    # planning figure, computed, never typed and never a KPI.
    compression_pct = fields.Float(
        string="Design Reduction %", compute="_compute_design_reduction", digits=(16, 1)
    )
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active")], required=True, default="draft"
    )
    activated_on = fields.Datetime(string="Activated On", readonly=True, copy=False)
    # What the retention cron has really done (AUT-IOT-05).
    rolled_until = fields.Datetime(string="Aggregated Up To", readonly=True, copy=False)
    raw_points_rolled = fields.Integer(string="Raw Readings Aggregated", readonly=True, copy=False)
    rollup_points = fields.Integer(string="Aggregates Written", readonly=True, copy=False)
    measured_compression_pct = fields.Float(
        string="Measured Compression %",
        readonly=True,
        copy=False,
        digits=(16, 1),
        help="100 x (1 - aggregates written / raw readings aggregated), from the "
        "retention cron's own counts. Empty until it has aggregated something.",
    )
    last_rollup_on = fields.Datetime(string="Last Aggregation Run", readonly=True, copy=False)
    rollup_ids = fields.One2many("fix.iot.telemetry.rollup", "downsample_id", string="Aggregates")

    _target_ge_raw = models.Constraint(
        "CHECK (target_interval_sec >= raw_interval_sec)",
        "The target interval cannot be shorter than the raw interval",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.iot.downsample") or "IDSP/New"
                )
        return super().create(vals_list)

    @api.depends("raw_interval_sec", "target_interval_sec")
    def _compute_design_reduction(self):
        for rec in self:
            target = rec.target_interval_sec or 0
            rec.compression_pct = (
                round((1 - (rec.raw_interval_sec or 0) / target) * 100, 1) if target > 0 else 0.0
            )

    @api.constrains("retention_days", "raw_interval_sec")
    def _check_positive(self):
        for rec in self:
            if (rec.retention_days or 0) <= 0 or (rec.raw_interval_sec or 0) <= 0:
                raise ValidationError("Intervals and retention must be positive.")

    def _fix_activate(self):
        """Put the policy in force (the platform, or an approved change)."""
        for rec in self.sudo():
            if rec.state != "draft":
                raise UserError("Policy %s is already active." % rec.name)
            rec._guarded().write({"state": "active", "activated_on": fields.Datetime.now()})

    def _fix_deactivate(self):
        """Back to draft: the cron stops aggregating and purging for it, what it
        wrote stays, and its terms can be edited and sent for activation again."""
        for rec in self.sudo():
            if rec.state != "active":
                raise UserError("Policy %s is not active." % rec.name)
            rec._guarded().write({"state": "draft", "activated_on": False})

    def action_request_deactivation(self, reason=None):
        """A07 (2026-11-07): an active policy could never be switched off. Same
        approval as turning it on."""
        why = (reason or "").strip()
        if not why:
            raise UserError("Give the reason for switching the policy off.")
        Change = self.env["fix.iot.retention.change"]
        for rec in self:
            if rec.state != "active":
                raise UserError("Policy %s is not active." % rec.name)
            change = Change.create(
                {"downsample_id": rec.id, "change_type": "deactivate", "reason": why}
            )
            change.action_request_approval()
        return True

    def action_activate(self):
        """Superuser code (seeds, data loading) activates directly. Anyone else
        REQUESTS activation: a fix.iot.retention.change routed to the CTO."""
        for rec in self:
            if rec.state != "draft":
                raise UserError("Policy %s is already active." % rec.name)
        if self.env.su:
            return self._fix_activate()
        Change = self.env["fix.iot.retention.change"]
        for rec in self:
            change = Change.create(
                {
                    "downsample_id": rec.id,
                    "change_type": "activate",
                    "reason": "Activate downsampling policy %s" % rec.name,
                }
            )
            change.action_request_approval()
        return True

    # ---- retention cron (AUT-IOT-05/06, BRU-IOT-07) ---------------------------
    def _fix_bucket(self, ts):
        seconds = self.target_interval_sec
        epoch = int((ts - _EPOCH).total_seconds())
        return _EPOCH + timedelta(seconds=epoch - epoch % seconds)

    def _fix_rollup(self, now):
        """Aggregate every COMPLETE bucket since rolled_until into
        fix.iot.telemetry.rollup, and measure the compression. Idempotent: a
        bucket is written once (unique per policy and bucket start)."""
        self.ensure_one()
        stream = self.stream_id
        Telemetry = self.env["fix.iot.telemetry"].sudo()
        Rollup = self.env["fix.iot.telemetry.rollup"].sudo()
        upto = self._fix_bucket(now)  # the current bucket is not complete
        domain = [
            ("device_id", "=", stream.device_id.id),
            ("metric", "=", stream.metric),
            ("timestamp", "<", upto),
        ]
        if self.rolled_until:
            domain.append(("timestamp", ">=", self.rolled_until))
        buckets = {}
        for reading in Telemetry.search(domain, order="timestamp"):
            buckets.setdefault(self._fix_bucket(reading.timestamp), []).append(reading.value)
        existing = set(
            Rollup.search(
                [("downsample_id", "=", self.id), ("bucket_start", "in", list(buckets))]
            ).mapped("bucket_start")
        )
        agg = {
            "avg": lambda v: sum(v) / len(v),
            "min": min,
            "max": max,
            "last": lambda v: v[-1],
        }[self.aggregation]
        new = [
            {
                "downsample_id": self.id,
                "bucket_start": start,
                "bucket_seconds": self.target_interval_sec,
                "aggregation": self.aggregation,
                "value": agg(values),
                "points": len(values),
            }
            for start, values in sorted(buckets.items())
            if start not in existing
        ]
        if new:
            Rollup._guarded().create(new)
        raw = self.raw_points_rolled + sum(v["points"] for v in new)
        rolled = self.rollup_points + len(new)
        self._guarded().write(
            {
                "rolled_until": upto,
                "raw_points_rolled": raw,
                "rollup_points": rolled,
                "measured_compression_pct": round((1 - rolled / raw) * 100, 1) if raw else 0.0,
                "last_rollup_on": now,
            }
        )
        return len(new)

    @api.model
    def cron_retention(self):
        """A07 P1 (2026-11-04) D9 / AUT-IOT-05/06: aggregate every active
        policy, then - only when RETENTION_PURGE_PARAM is "1" - drop raw
        readings past their stream's retention that an aggregate already
        covers (BRU-IOT-07), and aggregates past their policy's retention.
        Raw readings of a stream with no active policy are never dropped.
        Returns {"aggregates": n, "raw_dropped": n, "aggregates_dropped": n}."""
        now = fields.Datetime.now()
        purge = _flag(self.env, RETENTION_PURGE_PARAM)
        out = {"aggregates": 0, "raw_dropped": 0, "aggregates_dropped": 0}
        for policy in self.sudo().search([("state", "=", "active")]):
            out["aggregates"] += policy._fix_rollup(now)
            if not purge:
                continue
            stream = policy.stream_id
            horizon = min(now - timedelta(days=stream.retention_days), policy.rolled_until)
            raw = (
                self.env["fix.iot.telemetry"]
                .sudo()
                .search(
                    [
                        ("device_id", "=", stream.device_id.id),
                        ("metric", "=", stream.metric),
                        ("timestamp", "<", horizon),
                    ]
                )
            )
            out["raw_dropped"] += len(raw)
            raw.unlink()
            old = policy.rollup_ids.filtered(
                lambda r, cut=now - timedelta(days=policy.retention_days): r.bucket_start < cut
            )
            out["aggregates_dropped"] += len(old)
            old.unlink()
        return out


_EPOCH = fields.Datetime.to_datetime("1970-01-01 00:00:00")


# What an approval covers: changing one voids it (approved) or is refused
# (dispatched and later).
_ACTION_PINNED = frozenset({"action_type", "priority", "prediction_id"})
# Also frozen once the action is done or cancelled.
_ACTION_CLOSED = _ACTION_PINNED | {"technician_id", "scheduled_on", "outcome_evidence_ref"}
# action_done outcome -> the prediction's recorded outcome.
_ACTION_OUTCOME = {"confirmed": "confirmed", "not_confirmed": "false_alarm"}


class FixIotPrescriptiveAction(models.Model):
    _name = "fix.iot.action"
    _description = "Prescriptive Maintenance Action"
    # fix.approvable.mixin already sits in front of fix.guarded.mixin.
    _inherit = ["fix.approvable.mixin"]
    _order = "scheduled_on desc, id desc"

    # A07 P0 recipe (2026-11-03) M48-2: action_approve was a bare state flip.
    # The proposer approved his own action, any user approved anyone's, a
    # `replace` on a healthy prediction was approved, the approved terms could
    # be swapped afterwards, and create / write / the P03 form set any state.
    # Approval is now routed through the engine (no amount: the operations-
    # manager tier decides), the engine excludes the proposer and requester,
    # and action_approve runs only from the approver's inbox.
    _approval_domain = "iot_prescriptive_action"
    _approval_apply_method = "action_approve"
    _approval_group = ACTION_APPROVER_GROUP
    _approval_routed = True

    def _fix_live_approver_group(self):
        group = self.env.ref(ACTION_APPROVER_GROUP, raise_if_not_found=False)
        if not group:
            return ACTION_APPROVER_FALLBACK
        companies = self.company_id or self.env.company
        held = group.sudo().all_user_ids.filtered(
            lambda u: u.active and not u.share and companies & u.company_ids
        )
        return ACTION_APPROVER_GROUP if held else ACTION_APPROVER_FALLBACK

    def _approval_group_xmlid(self):
        # A request stays with the group it was routed to: appointing a Director
        # meanwhile must not leave the Tier 2 approver holding a task they are
        # refused on. Empty set: asked before any record exists.
        routed = self.filtered(lambda a: a.approval_state == "pending").mapped(
            "approval_routed_group"
        )
        return routed[0] if routed and routed[0] else self._fix_live_approver_group()

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "state",
            "approved_by",
            "approved_on",
            "dispatched_on",
            "completed_by",
            "completed_on",
            "outcome",
            "outcome_note",
            "revision_note",
            "approval_routed_group",
            "cancelled_by",
            "cancelled_on",
            "cancel_reason",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(a.state in ("approved", "dispatched", "done", "cancelled") for a in self):
            locked |= _ACTION_PINNED
        if self and any(a.state in ("done", "cancelled") for a in self):
            locked |= _ACTION_CLOSED
        return locked

    def write(self, vals):
        void = {}
        if self and not self._fix_guard_open():
            for rec in self:
                frozen = _ACTION_CLOSED if rec.state in ("done", "cancelled") else _ACTION_PINNED
                changed = sorted(
                    n for n in frozen & set(vals) if rec._fix_guard_differs(n, vals[n], rec[n])
                )
                if not changed:
                    if (
                        rec.state == "dispatched"
                        and "technician_id" in vals
                        and not vals["technician_id"]
                    ):
                        raise UserError(
                            "Action %s is dispatched: its technician cannot be cleared." % rec.name
                        )
                    continue
                # A07 P1 (2026-11-04) M48-12: an approved action's terms are
                # refused, not silently voided; Revise Terms (with a reason)
                # sends it back to proposed for a fresh approval.
                if rec.state in ("approved", "dispatched", "done", "cancelled"):
                    raise UserError(
                        "Action %s is %s: its %s can no longer change.%s"
                        % (
                            rec.name,
                            dict(self._fields["state"].selection)[rec.state].lower(),
                            ", ".join(self._fields[n].string for n in changed),
                            " Use Revise Terms to withdraw the approval first."
                            if rec.state == "approved"
                            else "",
                        )
                    )
                if rec.approval_state == "pending":
                    void[rec.id] = changed
        result = super().write(vals)
        for rec in self.filtered(lambda r: r.id in void):
            # The approval covered the old terms: withdraw it and send the
            # action back to proposed, so it is approved again as changed.
            rec._approval_void(
                "%s changed while approval was requested"
                % ", ".join(self._fields[n].string for n in void[rec.id])
            )
        return result

    def action_revise_terms(self, reason=None):
        """Withdraw an approval so the action's terms can change; it returns to
        proposed and is approved again as changed (M48-12). IoT operator, with
        a reason; the withdrawal is stamped."""
        _require_role(self.env, IOT_OPERATOR, "Revising an approved action")
        why = (reason or "").strip()
        if not why:
            raise UserError("Give the reason for revising the approved action.")
        for rec in self:
            if rec.state != "approved":
                raise UserError(
                    "Only an approved action is revised (%s is %s)." % (rec.name, rec.state)
                )
            rec._approval_void("terms revised: %s" % why)
            rec._guarded().write(
                {
                    "state": "proposed",
                    "approved_by": False,
                    "approved_on": False,
                    "revision_note": "%s (%s, %s)"
                    % (why, self.env.user.name, fields.Date.context_today(self)),
                }
            )
        return True

    def action_cancel(self, reason=None):
        """A07 (2026-11-07): `cancelled` had no writer. A proposed or approved
        action is called off with a reason, and any open request or approval goes
        with it. Once dispatched the work is with the order: complete it instead."""
        _require_role(self.env, IOT_OPERATOR, "Cancelling a prescriptive action")
        why = (reason or "").strip()
        if not why:
            raise UserError("Give the reason for cancelling the action.")
        for rec in self:
            if rec.state not in ("proposed", "approved"):
                raise UserError(
                    "Only a proposed or approved action is cancelled (%s is %s)."
                    % (rec.name, rec.state)
                )
            rec._approval_void("action cancelled: %s" % why)
            rec._guarded().write(
                {
                    "state": "cancelled",
                    "cancelled_by": self.env.uid,
                    "cancelled_on": fields.Datetime.now(),
                    "cancel_reason": why,
                }
            )
        return True

    name = fields.Char(required=True, default="New")
    revision_note = fields.Char(string="Last Terms Revision", readonly=True, copy=False)
    approval_routed_group = fields.Char(string="Approval Routed To", readonly=True, copy=False)
    cancelled_by = fields.Many2one("res.users", string="Cancelled By", readonly=True, copy=False)
    cancelled_on = fields.Datetime(string="Cancelled On", readonly=True, copy=False)
    cancel_reason = fields.Char(string="Why Cancelled", readonly=True, copy=False)
    prediction_id = fields.Many2one(
        "fix.predictive.maintenance",
        string="Prediction",
        required=True,
        ondelete="cascade",
        index=True,
    )
    equipment_id = fields.Many2one(
        related="prediction_id.equipment_id", string="Equipment", store=True
    )
    # A07 P1 (2026-11-04) M48-9: scoped through its prediction's company.
    company_id = fields.Many2one(
        related="prediction_id.company_id", string="Company", store=True, index=True
    )
    action_type = fields.Selection(
        [
            ("inspect", "Inspect"),
            ("replace", "Replace"),
            ("calibrate", "Calibrate"),
            ("dispatch", "Dispatch Technician"),
            ("reduce_load", "Reduce Load"),
        ],
        required=True,
        default="inspect",
    )
    priority = fields.Selection(
        [("low", "Low"), ("medium", "Medium"), ("high", "High")],
        required=True,
        default="medium",
    )
    technician_id = fields.Many2one("hr.employee", string="Technician")
    scheduled_on = fields.Date(required=True, default=fields.Date.context_today)
    state = fields.Selection(
        [
            ("proposed", "Proposed"),
            ("approved", "Approved"),
            ("dispatched", "Dispatched"),
            ("done", "Done"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        default="proposed",
    )
    notes = fields.Char()
    approved_by = fields.Many2one("res.users", string="Approved By", readonly=True, copy=False)
    approved_on = fields.Datetime(string="Approved On", readonly=True, copy=False)
    dispatched_on = fields.Datetime(string="Dispatched On", readonly=True, copy=False)
    completed_by = fields.Many2one("res.users", string="Completed By", readonly=True, copy=False)
    completed_on = fields.Datetime(string="Completed On", readonly=True, copy=False)
    outcome = fields.Selection(
        [("confirmed", "Failure Confirmed"), ("not_confirmed", "Failure Not Confirmed")],
        string="Outcome",
        readonly=True,
        copy=False,
    )
    outcome_note = fields.Text(string="Outcome Note", readonly=True, copy=False)
    # A07 P1 (2026-11-04) P2 "outcome with evidence" (spec fix.prediction.outcome
    # evidence_ref / related_service_order_id): what proves the finding - the
    # job card, photo set or service order reference. Required to complete.
    outcome_evidence_ref = fields.Char(
        string="Outcome Evidence",
        copy=False,
        help="Job card, service order or photo-set reference proving what the "
        "intervention found. Required before completion.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.iot.action") or "IACT/New"
        return super().create(vals_list)

    def _fix_check_approvable(self):
        for rec in self:
            if rec.state != "proposed":
                raise UserError("Approve a proposed action")
            if rec.prediction_id.prediction == "healthy":
                raise UserError(
                    "Action %s is on prediction %s, which predicts a healthy asset: there is "
                    "no failure to intervene on." % (rec.name, rec.prediction_id.name)
                )
            # A07 (2026-11-07): the first finding stands, and two interventions
            # cannot race to record it.
            prediction = rec.prediction_id.sudo()
            if prediction.outcome != "pending":
                raise UserError(
                    "Prediction %s already has its outcome: a re-assessment records a new "
                    "prediction." % prediction.name
                )
            busy = prediction.action_ids.filtered(
                lambda a, r=rec: a != r
                and (a.state in ("approved", "dispatched") or a.approval_state == "pending")
            )
            if busy:
                raise UserError(
                    "Prediction %s already has action %s under way: cancel it first."
                    % (prediction.name, busy[0].name)
                )
            # A07 P1 (2026-11-04) BRU-IOT-10 / FR-IOT-040: an intervention
            # applies the prediction, so its model must be a published M26 one.
            rec.prediction_id._fix_assert_published_model("Approving action %s" % rec.name)

    def _approval_needed(self) -> bool:
        return self.state == "proposed"

    def action_request_approval(self, justification=None):
        self._fix_check_approvable()
        for rec in self:
            rec._guarded().write({"approval_routed_group": rec._fix_live_approver_group()})
        return super().action_request_approval(justification=justification)

    def action_approve(self):
        """The M63 apply method. Reached only from the approver's inbox task,
        in the approver's environment; the proposer and the requester never
        decide it (the engine does not route to them, and this re-checks)."""
        self._approval_assert_routed()
        acting = self._approval_acting_users()
        self._fix_check_approvable()
        for rec in self:
            _assert_authority(rec, rec._approval_group_xmlid(), "Approving a prescriptive action")
            requester = rec.approval_request_id.sudo().requested_by_id
            if not self.env.su and acting & (rec.create_uid | requester):
                raise UserError(
                    "The proposer or the requester of action %s cannot approve it." % rec.name
                )
            rec._guarded().write(
                {
                    "state": "approved",
                    "approved_by": self.env.uid,
                    "approved_on": fields.Datetime.now(),
                }
            )

    def action_dispatch(self):
        """A07 P1 (2026-11-04): dispatch is the IoT operator's (spec R13), and
        it hands the work to the owning module. M48 never acts on the asset
        (BRU-IOT-12): iot.action_dispatched carries what the M01/M02 order
        needs, and the bridge creates it."""
        _require_role(self.env, IOT_OPERATOR, "Dispatching a prescriptive action")
        for rec in self:
            if rec.state != "approved":
                raise UserError("Dispatch an approved action")
            if not rec.technician_id:
                raise UserError("Assign a technician before dispatching action %s." % rec.name)
            rec._guarded().write({"state": "dispatched", "dispatched_on": fields.Datetime.now()})
            prediction = rec.prediction_id.sudo()
            publish(
                rec.env,
                "iot.action_dispatched",
                "fix.iot.action",
                rec.id,
                {
                    "action": rec.name,
                    "action_type": rec.action_type,
                    "priority": rec.priority,
                    "scheduled_on": fields.Date.to_string(rec.scheduled_on),
                    "technician_id": rec.technician_id.id,
                    "equipment_id": prediction.equipment_id.id,
                    "equipment_code": prediction.equipment_id.code or "",
                    "company_id": prediction.company_id.id,
                    "operating_unit_id": prediction.operating_unit_id.id or False,
                    "prediction": prediction.name,
                    "predicted": prediction.prediction,
                    "days_to_failure": prediction.estimated_days_to_failure,
                    "model": prediction.model_name or "",
                    "approved_by": rec.approved_by.id or False,
                    "notes": rec.notes or "",
                },
            )

    def action_done(self, outcome=None, note=None):
        """Complete the intervention and record what it found on the
        prediction (FR-IOT-044 / BRU-IOT-14): the failure was confirmed or not,
        with a note. The prediction's outcome changes only here."""
        if outcome not in _ACTION_OUTCOME:
            raise UserError(
                "Record the outcome: was the predicted failure confirmed or not confirmed?"
            )
        note = (note or "").strip()
        if not note:
            raise UserError("Describe what the intervention found.")
        _require_role(self.env, IOT_OPERATOR, "Completing a prescriptive action")
        now = fields.Datetime.now()
        for rec in self:
            if rec.state != "dispatched":
                raise UserError("Complete a dispatched action")
            blockers = rec._fix_completion_blockers()
            if blockers:
                raise UserError(
                    "Action %s cannot be completed yet: %s." % (rec.name, "; ".join(blockers))
                )
            # A07 P1 (2026-11-04) P2: the outcome needs evidence, and spec §13
            # SoD - the person whose intervention is evaluated does not record
            # its outcome.
            if not (rec.outcome_evidence_ref or "").strip():
                raise UserError(
                    "Record the outcome evidence of action %s (job card, service order or "
                    "photo-set reference) before completing it." % rec.name
                )
            if not self.env.su and rec.technician_id.user_id == self.env.user:
                raise UserError(
                    "The technician who performed action %s cannot record its outcome." % rec.name
                )
            rec._guarded().write(
                {
                    "state": "done",
                    "completed_by": self.env.uid,
                    "completed_on": now,
                    "outcome": outcome,
                    "outcome_note": note,
                }
            )
            rec.prediction_id._fix_record_outcome(_ACTION_OUTCOME[outcome], note, rec)
            publish(
                rec.env,
                "iot.intervention_outcome_recorded",
                "fix.iot.action",
                rec.id,
                {
                    "action": rec.name,
                    "prediction": rec.prediction_id.sudo().name,
                    "model": rec.prediction_id.sudo().model_name or "",
                    "outcome": outcome,
                    "prediction_outcome": _ACTION_OUTCOME[outcome],
                    "evidence_ref": rec.outcome_evidence_ref,
                    "intervention_performed": True,
                },
            )

    def _fix_completion_blockers(self):
        """Why the intervention is not over. The spine bridge names the order it
        routed: M48 itself never acts on the asset (BRU-IOT-12)."""
        return []

    def action_done_confirmed(self, note=None):
        return self.action_done(outcome="confirmed", note=note)

    def action_done_not_confirmed(self, note=None):
        return self.action_done(outcome="not_confirmed", note=note)


# What a revoked consent may still have changed: nothing but its notes.
_CONSENT_TERMS = frozenset(
    {"subject_type", "device_id", "site_id", "partner_id", "purpose", "granted_on", "valid_to"}
)
# What a verification covers: changing any of it sends the consent back to
# pending verification (A07 P1).
_CONSENT_GRANT = _CONSENT_TERMS | {
    "signal_groups_permitted",
    "disclosure_document_id",
    "granted_by",
    "evidence_ref",
    "revocation_treatment",
}
_CONSENT_SUBJECT = {"device": "device_id", "site": "site_id", "customer": "partner_id"}


def _signal_tokens(text):
    return [t for t in re.split(r"[\s,;]+", (text or "").lower()) if t]


class FixIotConsent(models.Model):
    _name = "fix.iot.consent"
    _description = "IoT Telemetry Consent"
    _inherit = ["fix.guarded.mixin"]
    _order = "valid_to desc, id desc"

    def _fix_guarded_fields(self) -> set:
        # A07 audit (2026-11-03) M48-1: a plain write or the P03 form set a
        # revoked consent back to active, and nothing recorded who revoked it.
        # Only action_revoke changes these. A07 P1 adds the verification and
        # the revocation treatment record.
        return super()._fix_guarded_fields() | {
            "state",
            "revoked_by",
            "revoked_at",
            "verification",
            "verified_by",
            "verified_on",
            "revocation_evidence_ref",
            "treatment_state",
            "treatment_note",
            "readings_treated",
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(c.state == "revoked" for c in self):
            locked |= _CONSENT_GRANT
        return locked

    def _fix_attach_disclosure(self, content, filename):
        self.ensure_one()
        return self.env["ir.attachment"].create(
            {
                "name": (filename or "").strip() or "Disclosure of %s" % self.name,
                "datas": content,
                "res_model": self._name,
                "res_id": self.id,
            }
        )

    def write(self, vals):
        content = vals.pop("disclosure_file", None)
        filename = vals.pop("disclosure_filename", None)
        if content:
            for rec in self:
                # Through the write below, so a changed grant goes back for
                # verification, and a revoked one refuses it.
                rec.write(
                    {
                        **vals,
                        "disclosure_document_id": rec._fix_attach_disclosure(content, filename).id,
                    }
                )
            return True
        if not vals:
            return True
        # Revocation is final for everyone, superuser code included: a
        # withdrawn consent is never reinstated; a new grant is a new record.
        if (
            "state" in vals
            and vals["state"] != "revoked"
            and any(c.state == "revoked" for c in self)
        ):
            raise UserError(
                "A revoked telemetry consent cannot be reactivated. Record a new consent."
            )
        reverify = self.browse()
        if self and not self._fix_guard_open():
            touched = _CONSENT_GRANT & set(vals)
            for rec in self:
                changed = [n for n in touched if rec._fix_guard_differs(n, vals[n], rec[n])]
                if changed and rec.state == "revoked":
                    raise UserError(
                        "Consent %s is revoked: its terms (%s) are frozen."
                        % (
                            rec.name,
                            ", ".join(self._fields[n].string or n for n in sorted(changed)),
                        )
                    )
                if changed and rec.verification == "verified":
                    reverify |= rec
        result = super().write(vals)
        if reverify:
            # The verifier vouched for the old terms, not these.
            reverify._guarded().write(
                {"verification": "pending", "verified_by": False, "verified_on": False}
            )
        return result

    name = fields.Char(required=True, default="New")
    # A07 P1 (2026-11-04) M48-9: consents had no company and no record rule.
    company_id = fields.Many2one(
        "res.company", required=True, index=True, default=lambda self: self.env.company
    )
    subject_type = fields.Selection(
        [("device", "Device"), ("site", "Site"), ("customer", "Customer")],
        required=True,
        default="device",
    )
    device_id = fields.Many2one("fix.iot.device", string="Device", ondelete="set null")
    site_id = fields.Many2one("fix.site", string="Site", ondelete="set null")
    partner_id = fields.Many2one("res.partner", string="Customer")
    purpose = fields.Selection(
        [
            ("service", "Service Delivery"),
            ("analytics", "Analytics"),
            ("safety", "Safety Monitoring"),
        ],
        required=True,
        default="service",
    )
    granted_on = fields.Date(required=True, default=fields.Date.context_today)
    valid_to = fields.Date()
    state = fields.Selection(
        [("active", "Active"), ("revoked", "Revoked")], required=True, default="active"
    )
    # A07 P1 (2026-11-04) M48-1 / FR-IOT-005 / BRU-IOT-05: the grant record
    # had only free-text notes - no disclosure, no grantor, no signal scope.
    disclosure_document_id = fields.Many2one(
        "ir.attachment",
        string="Disclosure Given",
        ondelete="restrict",
        help="The disclosure / consent form the data subject was shown and signed.",
    )
    # A07 (2026-11-07): the form offered a picker over every attachment, listing
    # other records' file names. It now takes the file itself, staged here and
    # turned into an attachment of this consent on save.
    disclosure_file = fields.Binary(string="Disclosure File", store=False)
    disclosure_filename = fields.Char(string="Disclosure File Name", store=False)
    disclosure_name = fields.Char(
        string="Disclosure On File", related="disclosure_document_id.name"
    )
    granted_by = fields.Char(
        string="Granted By",
        help="The person who gave the consent (the data subject or their agent).",
    )
    signal_groups_permitted = fields.Char(
        string="Signals Permitted",
        help="Metrics (or metric prefixes) the consent discloses, comma separated, e.g. "
        "'temperature, vibration'. Ingest refuses any other signal. Empty means the "
        "consent names no signal limit.",
    )
    evidence_ref = fields.Char(
        string="Grant Evidence",
        help="Where the signed consent is filed (document number, e-sign id).",
    )
    # Spec §13 SoD: consent policy (R04 CCO / R22 account manager) is separate
    # from collection configuration. A consent a non-officer records is
    # `pending` and grants nothing until a Consent Officer who did not record
    # it verifies it. Superuser code and officers record verified consents.
    # The default is evaluated per caller; when this column was added on
    # upgrade it was evaluated as the superuser, so consents recorded before
    # A07 P1 are carried over as verified (they were all seeded by the admin).
    verification = fields.Selection(
        [("pending", "Pending Verification"), ("verified", "Verified")],
        string="Verification",
        required=True,
        default=lambda self: "verified" if _has_role(self.env, IOT_CONSENT) else "pending",
    )
    verified_by = fields.Many2one("res.users", string="Verified By", readonly=True, copy=False)
    verified_on = fields.Datetime(string="Verified On", readonly=True, copy=False)
    # FR-IOT-006 / AUT-IOT-02: the treatment agreed at grant, applied at revoke.
    revocation_treatment = fields.Selection(
        [
            ("retain", "Retain"),
            ("anonymise", "Anonymise"),
            ("delete", "Delete"),
        ],
        string="Treatment on Revocation",
        required=True,
        default="retain",
        help="Agreed with the data subject at grant: what happens to the readings "
        "already held when the consent is withdrawn.",
    )
    revoked_by = fields.Many2one("res.users", string="Revoked By", readonly=True)
    revoked_at = fields.Datetime(string="Revoked At", readonly=True)
    # Kept for the P0 screens and tests: the same moment.
    revoked_on = fields.Datetime(related="revoked_at", string="Revoked On")
    revocation_evidence_ref = fields.Char(string="Withdrawal Evidence", readonly=True, copy=False)
    treatment_state = fields.Selection(
        [("applied", "Applied"), ("manual", "Manual Task Open")],
        string="Treatment",
        readonly=True,
        copy=False,
    )
    treatment_note = fields.Text(string="Treatment Record", readonly=True, copy=False)
    readings_treated = fields.Integer(string="Readings Treated", readonly=True, copy=False)
    notes = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.iot.consent") or "ICNS/New"
        uploads = [
            (v.pop("disclosure_file", None), v.pop("disclosure_filename", None)) for v in vals_list
        ]
        records = super().create(vals_list)
        for rec, (content, filename) in zip(records, uploads, strict=True):
            if content:
                rec._guarded().write(
                    {"disclosure_document_id": rec._fix_attach_disclosure(content, filename).id}
                )
        officer = _has_role(self.env, IOT_CONSENT)
        for rec in records.filtered(lambda c: c.verification == "verified" and officer):
            # A07 (2026-11-07): an officer's consent was verified by being recorded,
            # with no evidence at all. It needs what action_verify needs; without
            # it the consent waits, and grants nothing, like anyone else's.
            if not self.env.su and rec._fix_evidence_problem():
                rec._guarded().write({"verification": "pending"})
                continue
            rec._guarded().write(
                {"verified_by": self.env.uid, "verified_on": fields.Datetime.now()}
            )
        return records

    # A07 audit (2026-11-03) M48-1: a customer consent naming no customer and a
    # device consent naming no device were accepted, and so was a validity
    # window that ends before it starts. Such a record consents for nobody.
    @api.constrains("subject_type", "device_id", "site_id", "partner_id")
    def _check_subject(self):
        for rec in self:
            field = _CONSENT_SUBJECT.get(rec.subject_type)
            if field and not rec[field]:
                raise ValidationError(
                    "A %s consent must name its %s."
                    % (
                        dict(self._fields["subject_type"].selection).get(rec.subject_type),
                        self._fields[field].string.lower(),
                    )
                )

    @api.constrains("granted_on", "valid_to")
    def _check_dates(self):
        for rec in self:
            if rec.valid_to and rec.granted_on and rec.valid_to < rec.granted_on:
                raise ValidationError("A consent cannot be valid to a date before it was granted.")

    def _fix_counts(self):
        """Does this consent bear on ingest? A verified grant does, whatever
        its state now; so does any withdrawal, verified or not (a withdrawal
        is always honoured). An unverified grant grants nothing."""
        self.ensure_one()
        return self.state == "revoked" or self.verification == "verified"

    def _fix_is_valid(self, day=None):
        """Active, verified and in date: granted_on <= day <= valid_to
        (open-ended when valid_to is empty)."""
        self.ensure_one()
        day = day or fields.Date.context_today(self)
        return (
            self.state == "active"
            and self.verification == "verified"
            and bool(self.granted_on)
            and self.granted_on <= day
            and (not self.valid_to or day <= self.valid_to)
        )

    def _fix_permits(self, metric):
        """BRU-IOT-05: is `metric` among the disclosed signals?"""
        self.ensure_one()
        tokens = _signal_tokens(self.signal_groups_permitted)
        if not tokens:
            return True
        metric = (metric or "").lower()
        return any(metric == t or metric.startswith(t + "_") for t in tokens)

    def _fix_covers(self, device):
        """Does this consent's subject include `device`?"""
        self.ensure_one()
        if self.subject_type == "device":
            return self.device_id == device
        if self.subject_type == "site":
            return bool(device.site_id) and self.site_id == device.site_id
        if self.subject_type == "customer":
            return (
                bool(device.partner_id)
                and self.partner_id == device.partner_id
                and (not self.device_id or self.device_id == device)
            )
        return False

    @api.model
    def _fix_for_device(self, device):
        """Every consent (any state) whose subject covers `device`. Read with
        sudo: the ingest check must see consents the caller cannot."""
        domain = [("device_id", "=", device.id)]
        if device.site_id:
            domain = ["|", ("site_id", "=", device.site_id.id), *domain]
        if device.partner_id:
            domain = ["|", ("partner_id", "=", device.partner_id.id), *domain]
        return self.sudo().search(domain).filtered(lambda c: c._fix_covers(device))

    def _fix_covered_streams(self):
        Device = self.env["fix.iot.device"].sudo()
        devices = Device
        for rec in self:
            if rec.subject_type == "device":
                candidates = rec.device_id.sudo()
            elif rec.subject_type == "site" and rec.site_id:
                candidates = Device.search([("site_id", "=", rec.site_id.id)])
            elif rec.subject_type == "customer" and rec.partner_id:
                candidates = rec.device_id.sudo() or Device.search(
                    [("partner_id", "=", rec.partner_id.id)]
                )
            else:
                candidates = Device
            devices |= candidates.filtered(rec._fix_covers)
        return self.env["fix.iot.stream"].sudo().search([("device_id", "in", devices.ids)])

    def _fix_unconsented(self, streams):
        """The streams among `streams`, in any state, no valid consent covers."""
        return streams.filtered(
            lambda s: not self._fix_for_device(s.device_id).filtered(lambda c: c._fix_is_valid())
        )

    def _fix_uncovered(self, streams):
        """The live streams among `streams` no valid consent covers any more."""
        return self._fix_unconsented(streams).filtered(lambda s: s.state in ("active", "silent"))

    def _fix_held_readings(self, streams):
        Telemetry = self.env["fix.iot.telemetry"].sudo()
        readings = Telemetry
        for stream in streams:
            readings |= Telemetry.search(
                [("device_id", "=", stream.device_id.id), ("metric", "=", stream.metric)]
            )
        return readings

    def _fix_drop_aggregates(self, streams):
        """The aggregates of `streams` are the subject's readings summed up, and
        they outlive the raw ones: they go with them. Returns how many."""
        rollups = (
            self.env["fix.iot.telemetry.rollup"].sudo().search([("stream_id", "in", streams.ids)])
        )
        count = len(rollups)
        rollups.unlink()
        return count

    def _fix_evidence_problem(self):
        """What is missing for this consent to be verified, or ""."""
        self.ensure_one()
        if not (self.disclosure_document_id or (self.evidence_ref or "").strip()):
            return (
                "Consent %s has no evidence: attach the disclosure given or record where "
                "the signed consent is filed." % self.name
            )
        if not (self.granted_by or "").strip():
            return "Record who granted consent %s." % self.name
        if not _signal_tokens(self.signal_groups_permitted):
            return "Consent %s names no signal: list the signals it discloses (BRU-IOT-05)." % (
                self.name
            )
        return ""

    def action_verify(self):
        """A07 P1 (2026-11-04): a Consent Officer who did not record the
        consent verifies it against its evidence (spec §13 SoD)."""
        _require_role(self.env, IOT_CONSENT, "Verifying a telemetry consent")
        for rec in self:
            if rec.state != "active" or rec.verification != "pending":
                raise UserError("Verify an active consent that is pending verification.")
            if not self.env.su and rec.create_uid == self.env.user:
                raise UserError("The person who recorded consent %s cannot verify it." % rec.name)
            problem = rec._fix_evidence_problem()
            if problem:
                raise UserError(problem)
            rec._guarded().write(
                {
                    "verification": "verified",
                    "verified_by": self.env.uid,
                    "verified_on": fields.Datetime.now(),
                }
            )

    def action_revoke(self, evidence_ref=None):
        """A07 audit (2026-11-03) M48-1 / AUT-IOT-02: revoking used only to flip
        the state; the device kept streaming. It stamps who/when and suspends
        every stream it covered that no other valid consent covers.

        A07 P1 (2026-11-04) FR-IOT-006: it then applies the treatment agreed at
        grant to the readings already held on those streams - retain (recorded
        as such), delete (removed, and counted), or anonymise (a task for the
        Consent Officer, AUT-IOT-02, who runs it: action_record_treatment) - and
        publishes telemetry.consent_revoked with the evidence. Anyone may record a
        withdrawal: stopping collection is fail-safe.

        A07 (2026-11-07): the treatment covers every stream no other valid consent
        covers, suspended ones too: suspended first, a revocation treated nothing
        and recorded "applied"."""
        now = fields.Datetime.now()
        for rec in self:
            if rec.state != "active":
                raise UserError("Revoke an active consent")
            rec._guarded().write(
                {
                    "state": "revoked",
                    "revoked_by": self.env.uid,
                    "revoked_at": now,
                    "revocation_evidence_ref": (evidence_ref or "").strip() or False,
                }
            )
        for rec in self:
            covered = rec._fix_covered_streams()
            stopped = rec._fix_uncovered(covered)
            stopped._fix_suspend("consent %s revoked" % rec.name)
            rec._fix_apply_treatment(rec._fix_unconsented(covered), stopped)

    def _fix_apply_treatment(self, streams, stopped):
        self.ensure_one()
        readings = self._fix_held_readings(streams)
        treatment = self.revocation_treatment
        if treatment == "delete":
            count = len(readings)
            readings.unlink()
            dropped = self._fix_drop_aggregates(streams)
            vals = {
                "treatment_state": "applied",
                "readings_treated": count,
                "treatment_note": "%d reading(s) and %d aggregate(s) of %d stream(s) deleted on "
                "revocation." % (count, dropped, len(streams)),
            }
        elif treatment == "anonymise":
            vals = {
                "treatment_state": "manual",
                "readings_treated": 0,
                "treatment_note": "Anonymisation of %d reading(s) of %d stream(s) awaits the "
                "Consent Officer." % (len(readings), len(streams)),
            }
        else:
            vals = {
                "treatment_state": "applied",
                "readings_treated": 0,
                "treatment_note": "%d reading(s) of %d stream(s) retained as agreed at grant."
                % (len(readings), len(streams)),
            }
        self.sudo()._guarded().write(vals)
        publish(
            self.env,
            "telemetry.consent_revoked",
            "fix.iot.consent",
            self.id,
            {
                "consent": self.name,
                "subject_type": self.subject_type,
                "device_id": self.device_id.id or False,
                "site_id": self.site_id.id or False,
                "partner_id": self.partner_id.id or False,
                "treatment": treatment,
                "treatment_state": vals["treatment_state"],
                "readings_treated": vals["readings_treated"],
                "streams_suspended": stopped.mapped("name"),
                "evidence_ref": self.revocation_evidence_ref or "",
            },
        )

    def action_record_treatment(self, note=None):
        """A07 (2026-11-07): this closed the task on a typed note with 0 readings
        treated, and every reading untouched. It now does the work: readings of
        the streams no valid consent covers lose their device and exact time, a
        location series and the aggregates are deleted, and the count is the
        count of what happened."""
        _require_role(self.env, IOT_CONSENT, "Anonymising a consent's readings")
        note = (note or "").strip()
        if not note:
            raise UserError("Add a note for the record: why, and under what authority.")
        for rec in self:
            if rec.treatment_state != "manual":
                raise UserError("Consent %s has no open treatment task." % rec.name)
            streams = rec._fix_unconsented(rec._fix_covered_streams())
            anonymised, deleted = rec._fix_held_readings(streams)._fix_anonymise()
            dropped = rec._fix_drop_aggregates(streams)
            rec._guarded().write(
                {
                    "treatment_state": "applied",
                    "readings_treated": anonymised + deleted,
                    "treatment_note": "%s\n%d reading(s) anonymised, %d location reading(s) and "
                    "%d aggregate(s) deleted by %s: %s"
                    % (
                        rec.treatment_note or "",
                        anonymised,
                        deleted,
                        dropped,
                        self.env.user.name,
                        note,
                    ),
                }
            )

    @api.model
    def cron_consent_expiry(self):
        """A07 P1 (2026-11-04) D9: a consent that lapsed (valid_to passed)
        stops collection at midnight, not only at the next ingest attempt:
        every live stream it covered that no other valid consent covers - and
        that needs one - is suspended. Idempotent: a suspended stream is not
        touched again."""
        today = fields.Date.context_today(self)
        lapsed = self.sudo().search(
            [("state", "=", "active"), ("valid_to", "!=", False), ("valid_to", "<", today)]
        )
        suspended = self.env["fix.iot.stream"]
        for rec in lapsed:
            for stream in rec._fix_uncovered(rec._fix_covered_streams()):
                counting = rec._fix_for_device(stream.device_id).filtered(lambda c: c._fix_counts())
                if stream._fix_consent_reason(counting):
                    stream._fix_suspend("consent %s expired on %s" % (rec.name, rec.valid_to))
                    suspended |= stream
        return len(suspended)


# ---------------------------------------------------------------------------
# A07 P1 (2026-11-04) BRU-IOT-06 / FR-IOT-025: retention governance.
# ---------------------------------------------------------------------------
class FixIotRetentionChange(models.Model):
    """A request to change a stream's raw retention or a downsampling
    policy's retention, or to put a policy in force. Routed through the M63
    engine to the CTO (IoT Manager), never decided by its requester or
    creator, and applied only from the approver's inbox."""

    _name = "fix.iot.retention.change"
    _description = "IoT Retention Policy Change"
    _inherit = ["mail.thread", "fix.approvable.mixin"]
    _order = "id desc"

    _approval_domain = "iot_retention_policy"
    _approval_apply_method = "action_apply"
    _approval_group = RETENTION_APPROVER_GROUP
    _approval_routed = True

    def _fix_guarded_fields(self) -> set:
        guarded = super()._fix_guarded_fields() | {
            "state",
            "current_days",
            "requested_by",
            "applied_by",
            "applied_on",
        }
        # Once requested, the terms are what the approver is looking at.
        if self and any(r.state != "draft" for r in self):
            guarded |= {"stream_id", "downsample_id", "change_type", "proposed_days", "reason"}
        return guarded

    name = fields.Char(required=True, default="New", copy=False)
    company_id = fields.Many2one(
        "res.company", compute="_compute_company", store=True, index=True, string="Company"
    )
    operating_unit_id = fields.Many2one(
        "operating.unit",
        compute="_compute_company",
        store=True,
        index=True,
        string="Operating Unit",
    )
    change_type = fields.Selection(
        [
            ("retention", "Retention Change"),
            ("activate", "Policy Activation"),
            ("deactivate", "Policy Deactivation"),
        ],
        required=True,
        default="retention",
    )
    stream_id = fields.Many2one(
        "fix.iot.stream", string="Stream (raw retention)", ondelete="cascade"
    )
    downsample_id = fields.Many2one(
        "fix.iot.downsample", string="Downsampling Policy", ondelete="cascade"
    )
    current_days = fields.Integer(string="Current Retention (days)", readonly=True)
    proposed_days = fields.Integer(string="Proposed Retention (days)")
    reason = fields.Char(required=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("requested", "Awaiting CTO Approval"),
            ("applied", "Applied"),
            ("rejected", "Rejected"),
        ],
        required=True,
        default="draft",
    )
    requested_by = fields.Many2one("res.users", string="Requested By", readonly=True, copy=False)
    applied_by = fields.Many2one("res.users", string="Approved By", readonly=True, copy=False)
    applied_on = fields.Datetime(string="Applied On", readonly=True, copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].next_by_code("fix.iot.retention.change") or "IRET/New"
                )
        return super().create(vals_list)

    @api.depends(
        "stream_id.company_id",
        "downsample_id.company_id",
        "stream_id.device_id.operating_unit_id",
        "downsample_id.stream_id.device_id.operating_unit_id",
    )
    def _compute_company(self):
        for rec in self:
            rec.company_id = rec.downsample_id.company_id or rec.stream_id.company_id
            stream = rec.stream_id or rec.downsample_id.stream_id
            rec.operating_unit_id = stream.device_id.operating_unit_id

    @api.constrains("change_type", "stream_id", "downsample_id", "proposed_days")
    def _check_target(self):
        for rec in self:
            if bool(rec.stream_id) == bool(rec.downsample_id):
                raise ValidationError(
                    "A retention change names exactly one target: a stream or a policy."
                )
            if rec.change_type in ("activate", "deactivate") and not rec.downsample_id:
                raise ValidationError("Only a downsampling policy is activated or switched off.")
            if rec.change_type == "retention" and (rec.proposed_days or 0) <= 0:
                raise ValidationError("The proposed retention must be a positive number of days.")

    def _fix_target(self):
        self.ensure_one()
        return self.downsample_id or self.stream_id

    def _approval_needed(self) -> bool:
        return self.state in ("draft", "requested") and self.approval_state != "approved"

    def action_request_approval(self, justification=None):
        for rec in self:
            if rec.state != "draft":
                raise UserError("Request approval of a draft change.")
            target = rec._fix_target().sudo()
            # A07 (2026-11-07): each press of Request Activation opened another
            # request for the same policy.
            field = "downsample_id" if rec.downsample_id else "stream_id"
            if self.sudo().search_count([(field, "=", target.id), ("state", "=", "requested")]):
                raise UserError(
                    "%s already has a change awaiting the CTO's approval. Recall it first."
                    % target.name
                )
            if rec.change_type == "activate" and target.state != "draft":
                raise UserError("Policy %s is already active." % target.name)
            if rec.change_type == "deactivate" and target.state != "active":
                raise UserError("Policy %s is not active." % target.name)
            if rec.change_type == "retention" and rec.proposed_days == target.retention_days:
                raise UserError(
                    "%s already keeps %s days: nothing to change."
                    % (target.name, rec.proposed_days)
                )
        result = super().action_request_approval(
            justification=justification or "; ".join(self.mapped("reason"))
        )
        for rec in self:
            rec._guarded().write(
                {
                    "state": "requested",
                    "requested_by": self.env.uid,
                    "current_days": rec._fix_target().sudo().retention_days,
                }
            )
        return result

    def action_recall_approval(self):
        result = super().action_recall_approval()
        self._guarded().write({"state": "draft"})
        return result

    def _approval_on_rejected(self, comment):
        self._guarded().write({"state": "rejected"})

    def action_apply(self):
        """The M63 apply method: make the approved change."""
        self._approval_assert_routed()
        acting = self._approval_acting_users()
        for rec in self:
            if rec.state != "requested":
                raise UserError("Change %s is not awaiting approval." % rec.name)
            _assert_authority(rec, RETENTION_APPROVER_GROUP, "Approving a retention change")
            if not self.env.su and acting & (rec.requested_by | rec.create_uid):
                raise UserError(
                    "The requester or the author of change %s cannot approve it." % rec.name
                )
            target = rec._fix_target().sudo()
            if rec.change_type == "activate":
                target._fix_activate()
            elif rec.change_type == "deactivate":
                target._fix_deactivate()
            else:
                target._guarded().write({"retention_days": rec.proposed_days})
            rec._guarded().write(
                {
                    "state": "applied",
                    "applied_by": self.env.uid,
                    "applied_on": fields.Datetime.now(),
                }
            )
            publish(
                rec.env,
                "telemetry.retention_policy_changed",
                rec._name,
                rec.id,
                {
                    "change": rec.name,
                    "change_type": rec.change_type,
                    "target_model": target._name,
                    "target": target.name,
                    "from_days": rec.current_days,
                    "to_days": rec.proposed_days if rec.change_type == "retention" else None,
                    "approved_by": self.env.uid,
                },
            )


class _InsertOnlyMixin(models.AbstractModel):
    """A07 P1 (2026-11-04) P2 item 4: platform records (gaps, aggregates) are
    written by the crons and the ingest service; users never edit or delete
    them."""

    _name = "fix.iot.insert.only.mixin"
    _description = "IoT platform record (insert-only for users)"
    _inherit = ["fix.guarded.mixin"]

    @api.model_create_multi
    def create(self, vals_list):
        if not self._fix_guard_open():
            raise AccessError("%s records are written by the platform only." % self._description)
        return super().create(vals_list)

    def write(self, vals):
        if self and not self._fix_guard_open():
            raise AccessError("%s records cannot be edited." % self._description)
        return super().write(vals)

    def unlink(self):
        if self and not self.env.su:
            raise AccessError("%s records cannot be deleted." % self._description)
        return super().unlink()


class FixIotGap(models.Model):
    """FR-IOT-028 / AUT-IOT-03: a recorded absence of readings."""

    _name = "fix.iot.gap"
    _description = "IoT Telemetry Gap"
    _inherit = ["fix.iot.insert.only.mixin"]
    _order = "detected_at desc, id desc"

    name = fields.Char(required=True, default="New", readonly=True)
    stream_id = fields.Many2one(
        "fix.iot.stream", string="Stream", required=True, ondelete="cascade", index=True
    )
    device_id = fields.Many2one(related="stream_id.device_id", store=True, string="Device")
    company_id = fields.Many2one(
        related="stream_id.company_id", store=True, index=True, string="Company"
    )
    gap_from = fields.Datetime(string="Silent Since", required=True, readonly=True)
    gap_to = fields.Datetime(string="Resumed At", readonly=True)
    detected_at = fields.Datetime(string="Detected At", required=True, readonly=True)
    cause = fields.Selection(
        [
            ("device_silent", "Device Silent"),
            ("connectivity", "Connectivity Loss"),
            ("platform", "Platform Failure"),
            ("shed", "Shed Under Back-Pressure"),
        ],
        required=True,
        default="device_silent",
        readonly=True,
    )
    had_reading = fields.Boolean(
        string="Stream Had Readings",
        readonly=True,
        help="False when the stream never received a reading since activation.",
    )
    points_expected = fields.Integer(string="Readings Missed", readonly=True)
    state = fields.Selection(
        [("open", "Open"), ("closed", "Closed")], default="open", required=True, readonly=True
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"].sudo().next_by_code("fix.iot.gap") or "IGAP/New"
                )
        return super().create(vals_list)

    def _fix_close(self, at):
        for gap in self.sudo():
            interval = max(gap.stream_id.sample_interval_sec or 60, 1)
            missed = max(int((at - gap.gap_from).total_seconds() // interval) - 1, 0)
            gap.write({"gap_to": at, "state": "closed", "points_expected": missed})


class FixIotTelemetryRollup(models.Model):
    """FR-IOT-023 / BRU-IOT-07: one downsampled bucket written by the
    retention cron; it outlives the raw readings it summarises."""

    _name = "fix.iot.telemetry.rollup"
    _description = "IoT Telemetry Aggregate"
    _inherit = ["fix.iot.insert.only.mixin"]
    _order = "bucket_start desc"

    downsample_id = fields.Many2one(
        "fix.iot.downsample", string="Policy", required=True, ondelete="cascade", index=True
    )
    stream_id = fields.Many2one(related="downsample_id.stream_id", store=True, string="Stream")
    company_id = fields.Many2one(
        related="downsample_id.company_id", store=True, index=True, string="Company"
    )
    bucket_start = fields.Datetime(required=True, index=True)
    bucket_seconds = fields.Integer(required=True)
    aggregation = fields.Char(required=True)
    value = fields.Float(required=True)
    points = fields.Integer(string="Raw Readings", required=True)

    _bucket_unique = models.Constraint(
        "UNIQUE (downsample_id, bucket_start)", "A policy writes each bucket once."
    )
