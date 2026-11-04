# fix_iot_ops — M48: streams, protocol adapters, threshold rules, downsampling,
# prescriptive actions and telemetry consent. Devices, telemetry rows, alerts and
# predictions live in fix_stream_registry.py.
import re

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

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


# A07 P0 recipe (2026-11-03) M48-2: who approves a prescriptive action. Spec
# §13 gives R05 Operations Director the approval of proactive interventions; no
# M48 role group exists yet (P1), so the DOFA tier labelled "Branch /
# Operations Manager" decides. A default the business must confirm; a
# fix.approval.matrix row (decision domain iot_prescriptive_action) can name
# another group without code.
ACTION_APPROVER_GROUP = "cd_entity_config.group_dofa_tier_2"
# M48-3: BRU-IOT-15/16 make the CTO the approver of a rule suppression. There is
# no CTO group and no DOFA tier names the CTO; the closest C-level tier (Tier 4,
# "CFO / CCO / COO") decides by default, which the business must confirm. A
# matrix row (decision domain iot_rule_suppression) can name another group.
SUPPRESSION_APPROVER_GROUP = "cd_entity_config.group_dofa_tier_4"


def _assert_authority(rec, xmlid, what):
    """The deciding user (the absent approver when a delegate decides) must
    hold the group the request was routed to: the matrix row's group when one
    names it and that group implies `xmlid` (a rule may only narrow who
    decides, A11 audit E3), otherwise `xmlid`. Superuser code is trusted."""
    if rec.env.su:
        return
    row = rec.approval_request_id.sudo().matrix_id
    coded = rec.env.ref(xmlid)
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
        ],
        ondelete={"iot_prescriptive_action": "cascade", "iot_rule_suppression": "cascade"},
    )


class FixIotStream(models.Model):
    _name = "fix.iot.stream"
    _description = "IoT Stream Binding"
    _inherit = ["fix.guarded.mixin"]
    _order = "device_id, metric"

    def _fix_guarded_fields(self) -> set:
        # A07 P0 recipe (2026-11-03): a stream could be born `active` or have
        # its state written directly, skipping the activate/suspend checks.
        return super()._fix_guarded_fields() | {"state"}

    name = fields.Char(required=True, default="New")
    device_id = fields.Many2one(
        "fix.iot.device", string="Device", required=True, ondelete="cascade", index=True
    )
    equipment_id = fields.Many2one(related="device_id.equipment_id", string="Equipment", store=True)
    site_id = fields.Many2one(related="device_id.site_id", string="Site", store=True)
    adapter_id = fields.Many2one("fix.iot.adapter", string="Protocol Adapter", ondelete="set null")
    metric = fields.Char(required=True, help="e.g. temperature, vibration, battery_pct")
    unit = fields.Char()
    sample_interval_sec = fields.Integer(string="Sample Interval (s)", default=60, required=True)
    retention_days = fields.Integer(string="Raw Retention (days)", default=90, required=True)
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active"), ("suspended", "Suspended")],
        required=True,
        default="draft",
    )
    last_seen = fields.Datetime(related="device_id.last_telemetry", string="Last Seen")
    # A07 audit (2026-11-03) M48-8: this was One2many(..., "device_id"), which
    # matched the STREAM's id against telemetry.device_id and so listed another
    # device's rows. Telemetry has no stream link; a stream's readings are its
    # device's readings of its metric.
    telemetry_ids = fields.Many2many(
        "fix.iot.telemetry", compute="_compute_telemetry_ids", string="Telemetry"
    )
    rule_ids = fields.One2many("fix.iot.rule", "stream_id", string="Alert Rules")

    _interval_positive = models.Constraint(
        "CHECK (sample_interval_sec > 0)", "The sample interval must be positive"
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.iot.stream") or "STRM/New"
        return super().create(vals_list)

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

    def _fix_consent_reason(self, consents):
        """Why this stream needs a valid consent before ingest, or "" if exempt.

        `consents` are the consent records (any state) covering the device."""
        self.ensure_one()
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
        included: consent is a data-protection rule, not a permission."""
        Consent = self.env["fix.iot.consent"]
        for rec in self:
            consents = Consent._fix_for_device(rec.device_id)
            reason = rec._fix_consent_reason(consents)
            if reason and not consents.filtered(lambda c: c._fix_is_valid()):
                raise UserError(
                    "Ingest refused on stream %s: no active, in-date telemetry consent covers "
                    "device %s, and one is required because %s. Record a consent for the "
                    "device, its site or its customer first."
                    % (rec.name, rec.device_id.display_name, reason)
                )

    def action_activate(self):
        for rec in self:
            if rec.state == "active":
                raise UserError("Stream is already active")
            rec._guarded().write({"state": "active"})

    def action_suspend(self):
        for rec in self:
            if rec.state != "active":
                raise UserError("Suspend an active stream")
            rec._guarded().write({"state": "suspended"})

    def ingest(self, value):
        """Record one reading and evaluate the stream's active threshold rules."""
        self.ensure_one()
        if self.state != "active":
            raise UserError("Ingest requires an active stream")
        self._fix_check_consent()
        # Telemetry refuses a direct create() by a plain user (it skipped this
        # consent check and the rule engine), so ingest writes through the
        # guard token; the record handed back carries no token.
        telemetry = (
            self.env["fix.iot.telemetry"]
            ._guarded()
            .create(
                {
                    "company_id": self.device_id.company_id.id,
                    "operating_unit_id": self.device_id.operating_unit_id.id,
                    "device_id": self.device_id.id,
                    "timestamp": fields.Datetime.now(),
                    "metric": self.metric,
                    "value": value,
                    "unit": self.unit,
                }
            )
        )
        telemetry = self.env["fix.iot.telemetry"].browse(telemetry.id)
        # last_seen reads live from the device; action_telemetry_received
        # stamps it.
        self.device_id.action_telemetry_received("online")
        raised = self.env["fix.iot.alert"]
        # An expired suppression ends here, before evaluation, so a lapsed
        # pause or loosened threshold never hides a reading (BRU-IOT-16:
        # suppression is never indefinite, and no cron exists yet).
        self.rule_ids._fix_lapse_suppressions()
        for rule in self.rule_ids.filtered(lambda r: r.state == "active"):
            if rule.matches(value):
                raised |= self.env["fix.iot.alert"].create(
                    {
                        "device_id": self.device_id.id,
                        "severity": rule.severity,
                        "message": "%s %s %s: reading %s %s"
                        % (
                            self.metric,
                            dict(rule._fields["operator"].selection).get(rule.operator),
                            rule.threshold,
                            value,
                            self.unit or "",
                        ),
                    }
                )
        return telemetry, raised


class FixIotAdapter(models.Model):
    _name = "fix.iot.adapter"
    _description = "IoT Protocol Adapter"
    _inherit = ["fix.guarded.mixin"]
    _order = "name"

    def _fix_guarded_fields(self) -> set:
        # A07 P0 recipe (2026-11-03): the enabled/disabled flag changes only
        # through action_enable / action_disable.
        return super()._fix_guarded_fields() | {"state"}

    name = fields.Char(required=True, default="New")
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
    state = fields.Selection(
        [("enabled", "Enabled"), ("disabled", "Disabled")], required=True, default="enabled"
    )
    stream_ids = fields.One2many("fix.iot.stream", "adapter_id", string="Streams")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.iot.adapter") or "IADP/New"
        return super().create(vals_list)

    def action_enable(self):
        for rec in self:
            if rec.state != "disabled":
                raise UserError("Enable a disabled adapter")
            rec._guarded().write({"state": "enabled"})

    def action_disable(self):
        for rec in self:
            if rec.state != "enabled":
                raise UserError("Disable an enabled adapter")
            rec._guarded().write({"state": "disabled"})


# A rule's terms: an existing rule's threshold moves only through
# action_change_threshold, and its operator and stream not at all (turning
# "> 5" into "< 5", or moving the rule to another stream, silences it as surely
# as a 1e9 threshold). A new rule is born with all three.
_RULE_TERMS = frozenset({"threshold", "operator", "stream_id"})
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
            "suppression_kind",
            "suppression_requested_by",
            "suppressed_by",
            "suppressed_on",
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
        [("pause", "Pause"), ("loosen", "Loosened Threshold")],
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
    suppression_requested_by = fields.Many2one(
        "res.users", string="Suppression Requested By", readonly=True, copy=False
    )
    suppressed_by = fields.Many2one(
        "res.users", string="Suppression Approved By", readonly=True, copy=False
    )
    suppressed_on = fields.Datetime(string="Suppression Approved On", readonly=True, copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.iot.rule") or "IRUL/New"
        return super().create(vals_list)

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
        }
        if self.suppression_kind == "loosen" and self._fix_suppression_in_force():
            vals["threshold"] = self.baseline_threshold
        return vals

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

    def _fix_request_suppression(self, kind, reason=None, proposed_threshold=0.0):
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
                }
            )
            rec.action_request_approval(justification=why)

    def _approval_needed(self) -> bool:
        return bool(self.suppression_kind) and not self._fix_suppression_in_force()

    def _approval_on_rejected(self, comment):
        for rec in self.filtered(lambda r: not r._fix_suppression_in_force()):
            rec._guarded().write(
                {
                    "suppression_kind": False,
                    "proposed_threshold": 0.0,
                    "suppression_requested_by": False,
                }
            )

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


class FixIotDownsample(models.Model):
    _name = "fix.iot.downsample"
    _description = "IoT Downsampling Policy"
    _order = "stream_id"

    name = fields.Char(required=True, default="New")
    stream_id = fields.Many2one(
        "fix.iot.stream", string="Stream", required=True, ondelete="cascade", index=True
    )
    raw_interval_sec = fields.Integer(string="Raw Interval (s)", required=True, default=60)
    target_interval_sec = fields.Integer(string="Target Interval (s)", required=True, default=300)
    aggregation = fields.Selection(
        [("avg", "Average"), ("min", "Minimum"), ("max", "Maximum"), ("last", "Last Value")],
        required=True,
        default="avg",
    )
    retention_days = fields.Integer(string="Compressed Retention (days)", default=730)
    compression_pct = fields.Float(string="Compression %", default=80.0)
    state = fields.Selection(
        [("draft", "Draft"), ("active", "Active")], required=True, default="draft"
    )

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

    def action_activate(self):
        for rec in self:
            rec.state = "active"


# What an approval covers: changing one voids it (approved) or is refused
# (dispatched and later).
_ACTION_PINNED = frozenset({"action_type", "priority", "prediction_id"})
# Also frozen once the action is done or cancelled.
_ACTION_CLOSED = _ACTION_PINNED | {"technician_id", "scheduled_on"}
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
        }

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(a.state in ("dispatched", "done", "cancelled") for a in self):
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
                if rec.state in ("dispatched", "done", "cancelled"):
                    raise UserError(
                        "Action %s is %s: its %s can no longer change."
                        % (
                            rec.name,
                            dict(self._fields["state"].selection)[rec.state].lower(),
                            ", ".join(self._fields[n].string for n in changed),
                        )
                    )
                if rec.state == "approved" or rec.approval_state == "pending":
                    void[rec.id] = changed
        result = super().write(vals)
        for rec in self.filtered(lambda r: r.id in void):
            # The approval covered the old terms: withdraw it and send the
            # action back to proposed, so it is approved again as changed.
            rec._approval_void(
                "%s changed after approval was given or requested"
                % ", ".join(self._fields[n].string for n in void[rec.id])
            )
            if rec.state == "approved":
                rec._guarded().write(
                    {"state": "proposed", "approved_by": False, "approved_on": False}
                )
        return result

    name = fields.Char(required=True, default="New")
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

    def _approval_needed(self) -> bool:
        return self.state == "proposed"

    def action_request_approval(self, justification=None):
        self._fix_check_approvable()
        return super().action_request_approval(justification=justification)

    def action_approve(self):
        """The M63 apply method. Reached only from the approver's inbox task,
        in the approver's environment; the proposer and the requester never
        decide it (the engine does not route to them, and this re-checks)."""
        self._approval_assert_routed()
        acting = self._approval_acting_users()
        self._fix_check_approvable()
        for rec in self:
            _assert_authority(rec, ACTION_APPROVER_GROUP, "Approving a prescriptive action")
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
        for rec in self:
            if rec.state != "approved":
                raise UserError("Dispatch an approved action")
            if not rec.technician_id:
                raise UserError("Assign a technician before dispatching action %s." % rec.name)
            rec._guarded().write({"state": "dispatched", "dispatched_on": fields.Datetime.now()})

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
        now = fields.Datetime.now()
        for rec in self:
            if rec.state != "dispatched":
                raise UserError("Complete a dispatched action")
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

    def action_done_confirmed(self, note=None):
        return self.action_done(outcome="confirmed", note=note)

    def action_done_not_confirmed(self, note=None):
        return self.action_done(outcome="not_confirmed", note=note)


# What a revoked consent may still have changed: nothing but its notes.
_CONSENT_TERMS = frozenset(
    {"subject_type", "device_id", "site_id", "partner_id", "purpose", "granted_on", "valid_to"}
)
_CONSENT_SUBJECT = {"device": "device_id", "site": "site_id", "customer": "partner_id"}


class FixIotConsent(models.Model):
    _name = "fix.iot.consent"
    _description = "IoT Telemetry Consent"
    _inherit = ["fix.guarded.mixin"]
    _order = "valid_to desc, id desc"

    def _fix_guarded_fields(self) -> set:
        # A07 audit (2026-11-03) M48-1: a plain write or the P03 form set a
        # revoked consent back to active, and nothing recorded who revoked it.
        # Only action_revoke changes these.
        return super()._fix_guarded_fields() | {"state", "revoked_by", "revoked_on"}

    def _fix_form_locked_fields(self) -> set:
        locked = set(super()._fix_form_locked_fields())
        if self and any(c.state == "revoked" for c in self):
            locked |= _CONSENT_TERMS
        return locked

    def write(self, vals):
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
        if self and not self._fix_guard_open():
            touched = _CONSENT_TERMS & set(vals)
            for rec in self.filtered(lambda c: c.state == "revoked"):
                changed = [n for n in touched if rec._fix_guard_differs(n, vals[n], rec[n])]
                if changed:
                    raise UserError(
                        "Consent %s is revoked: its terms (%s) are frozen."
                        % (
                            rec.name,
                            ", ".join(self._fields[n].string or n for n in sorted(changed)),
                        )
                    )
        return super().write(vals)

    name = fields.Char(required=True, default="New")
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
    revoked_by = fields.Many2one("res.users", string="Revoked By", readonly=True)
    revoked_on = fields.Datetime(string="Revoked On", readonly=True)
    notes = fields.Char()

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code("fix.iot.consent") or "ICNS/New"
        return super().create(vals_list)

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

    def _fix_is_valid(self, day=None):
        """Active and in date: granted_on <= day <= valid_to (open-ended when
        valid_to is empty)."""
        self.ensure_one()
        day = day or fields.Date.context_today(self)
        return (
            self.state == "active"
            and bool(self.granted_on)
            and self.granted_on <= day
            and (not self.valid_to or day <= self.valid_to)
        )

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

    def action_revoke(self):
        """A07 audit (2026-11-03) M48-1 / AUT-IOT-02: revoking used only to flip
        the state; the device kept streaming. Now it stamps who/when and
        suspends every stream it covered that no other valid consent covers."""
        now = fields.Datetime.now()
        for rec in self:
            if rec.state != "active":
                raise UserError("Revoke an active consent")
            rec._guarded().write(
                {"state": "revoked", "revoked_by": self.env.uid, "revoked_on": now}
            )
        for stream in self._fix_covered_streams().filtered(lambda s: s.state == "active"):
            consents = self._fix_for_device(stream.device_id)
            if not consents.filtered(lambda c: c._fix_is_valid()):
                # sudo: the revocation must take effect whatever the revoker's
                # rights on the stream.
                stream.sudo().state = "suspended"
