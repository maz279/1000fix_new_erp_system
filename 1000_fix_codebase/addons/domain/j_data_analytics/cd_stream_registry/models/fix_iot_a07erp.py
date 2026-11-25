# fix_iot_a07erp — A07 ERP audit (2026-11-20): M48 storage tiers, retention and
# the automations the spec requires that had no job.
#
# - D17(b) / M48-14: hourly and daily aggregates for EVERY stream (hourly kept
#   3 years, daily for ever), raw readings purged past their stream's retention
#   (30 / 90 / 365 days by signal criticality) once an hourly aggregate computed
#   after the reading arrived holds them (BRU-IOT-07, M48-11). Purge is ON by
#   default (fix_iot_ops.RETENTION_PURGE_PARAM = "0" switches it off).
# - M48-10: alert escalation by severity acknowledgement SLA (AUT-IOT-10), the
#   prediction-horizon sweep (AUT-IOT-16), rule performance (BRU-IOT-15) and the
#   adapter key rotation-due alert (AUT-IOT-21). The SLAs and limits have no
#   decided figure: each is a setting, and an unset setting does nothing.
# - M48-14: a device with streams or readings is decommissioned, never deleted.
# - M48-15/18: the module owning the asset an alert is about is recorded on it.
import logging
from datetime import timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError

from libs.py.fix_events import publish

from .fix_iot_ops import (
    IOT_ADMIN,
    IOT_OPERATOR,
    RETENTION_PURGE_DEFAULT,
    RETENTION_PURGE_PARAM,
    _dhaka_today,
    _flag,
    _param_int,
)

_logger = logging.getLogger(__name__)

HOURLY_RETENTION_PARAM = "cd_stream_registry.hourly_retention_days"
HOURLY_RETENTION_DEFAULT = 1095  # decision D17(b): hourly aggregates 3 years
ACK_SLA_PARAM = "cd_stream_registry.ack_sla_minutes_%s"  # minor / major / critical
RULE_REVIEW_ACK_PCT_PARAM = "cd_stream_registry.rule_review_ack_rate_pct"
KEY_MAX_AGE_PARAM = "cd_stream_registry.adapter_key_max_age_days"
TIERS = [("hour", "Hourly"), ("day", "Daily")]
TIER_SECONDS = {"hour": 3600, "day": 86400}
_EPOCH = fields.Datetime.to_datetime("1970-01-01 00:00:00")


def _bucket(ts, seconds):
    epoch = int((ts - _EPOCH).total_seconds())
    return _EPOCH + timedelta(seconds=epoch - epoch % seconds)


def _holders(env, xmlid):
    group = env.ref(xmlid, raise_if_not_found=False)
    if not group:
        return env["res.users"]
    return group.sudo().all_user_ids.filtered(lambda u: u.active and not u.share)


def _todo(record, users, summary):
    todo = record.env.ref("mail.mail_activity_data_todo", raise_if_not_found=False)
    for user in users:
        record.activity_schedule(
            activity_type_id=todo.id if todo else False, summary=summary[:200], user_id=user.id
        )


class FixIotTelemetryAggregate(models.Model):
    """D17(b): one hourly or daily aggregate of a stream, written by the retention
    job. It outlives the raw readings; the daily tier is never deleted."""

    _name = "fix.iot.telemetry.aggregate"
    _description = "IoT Telemetry Tier Aggregate"
    _inherit = ["fix.iot.insert.only.mixin"]
    _order = "bucket_start desc"

    stream_id = fields.Many2one(
        "fix.iot.stream", string="Stream", required=True, ondelete="restrict", index=True
    )
    company_id = fields.Many2one(
        related="stream_id.company_id", store=True, index=True, string="Company"
    )
    tier = fields.Selection(TIERS, required=True, index=True)
    bucket_start = fields.Datetime(required=True, index=True)
    value_avg = fields.Float(string="Average", required=True)
    value_min = fields.Float(string="Minimum", required=True)
    value_max = fields.Float(string="Maximum", required=True)
    points = fields.Integer(string="Raw Readings", required=True)
    max_reading_id = fields.Integer(string="Holds Readings Up To", readonly=True)

    _tier_bucket_once = models.Constraint(
        "UNIQUE (stream_id, tier, bucket_start)", "A stream writes each tier bucket once."
    )


class FixIotStreamTiers(models.Model):
    _inherit = "fix.iot.stream"

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"tier_rolled_until", "tier_dirty_from"}

    tier_rolled_until = fields.Datetime(string="Tiers Aggregated Up To", readonly=True, copy=False)
    tier_dirty_from = fields.Datetime(string="Tiers Recompute From", readonly=True, copy=False)

    def _fix_rollup_tiers(self, now):
        """Write the complete hourly and daily buckets since the last run. A late
        reading re-opens its buckets (M48-11): recomputed from the raw readings
        while all are held, merged into the stored aggregate once some were
        purged. Returns the aggregates written."""
        self.ensure_one()
        Telemetry = self.env["fix.iot.telemetry"].sudo()
        Agg = self.env["fix.iot.telemetry.aggregate"].sudo()
        upto = _bucket(now, TIER_SECONDS["hour"])
        day_open = _bucket(now, TIER_SECONDS["day"])
        start = self.tier_rolled_until
        if self.tier_dirty_from and start:
            start = min(start, self.tier_dirty_from)
        domain = [
            ("device_id", "=", self.device_id.id),
            ("metric", "=", self.metric),
            ("timestamp", "<", upto),
        ]
        if start:
            # a daily bucket spans earlier hours: start the day at its beginning
            domain.append(("timestamp", ">=", _bucket(start, TIER_SECONDS["day"])))
        readings = {"hour": {}, "day": {}}
        for reading in Telemetry.search(domain, order="timestamp"):
            for tier, seconds in TIER_SECONDS.items():
                readings[tier].setdefault(_bucket(reading.timestamp, seconds), []).append(reading)
        written = 0
        for tier, buckets in readings.items():
            done = {
                a.bucket_start: a
                for a in Agg.search(
                    [
                        ("stream_id", "=", self.id),
                        ("tier", "=", tier),
                        ("bucket_start", "in", list(buckets)),
                    ]
                )
            }
            rows = []
            for begin, held in sorted(buckets.items()):
                if tier == "day" and begin >= day_open:
                    continue  # today is not complete
                values = [r.value for r in held]
                stored = done.get(begin)
                if stored:
                    late = [r for r in held if r.id > (stored.max_reading_id or 0)]
                    if not late:
                        continue
                    if len(values) < stored.points + len(late):
                        # raw partly purged: merge the late readings in
                        extra = [r.value for r in late]
                        points = stored.points + len(extra)
                        vals = {
                            "value_avg": (stored.value_avg * stored.points + sum(extra)) / points,
                            "value_min": min([stored.value_min, *extra]),
                            "value_max": max([stored.value_max, *extra]),
                            "points": points,
                        }
                    else:
                        vals = None
                    stored.unlink()
                else:
                    vals = None
                if vals is None:
                    vals = {
                        "value_avg": sum(values) / len(values),
                        "value_min": min(values),
                        "value_max": max(values),
                        "points": len(values),
                    }
                rows.append(
                    dict(
                        vals,
                        stream_id=self.id,
                        tier=tier,
                        bucket_start=begin,
                        max_reading_id=max(
                            [r.id for r in held] + [stored.max_reading_id or 0 if stored else 0]
                        ),
                    )
                )
            if rows:
                Agg._guarded().create(rows)
                written += len(rows)
        self._guarded().write({"tier_rolled_until": upto, "tier_dirty_from": False})
        return written

    def _fix_purge_raw(self, now):
        """Raw readings past the stream's retention that an hourly aggregate
        already holds (BRU-IOT-07, M48-11)."""
        self.ensure_one()
        horizon = now - timedelta(days=max(self.retention_days or 0, 1))
        if self.tier_rolled_until:
            horizon = min(horizon, self.tier_rolled_until)
        raw = (
            self.env["fix.iot.telemetry"]
            .sudo()
            .search(
                [
                    ("device_id", "=", self.device_id.id),
                    ("metric", "=", self.metric),
                    ("timestamp", "<", horizon),
                ]
            )
        )
        if not raw:
            return 0
        hours = {
            a.bucket_start: a.max_reading_id
            for a in self.env["fix.iot.telemetry.aggregate"]
            .sudo()
            .search(
                [
                    ("stream_id", "=", self.id),
                    ("tier", "=", "hour"),
                    ("bucket_start", "<", horizon),
                ]
            )
        }
        drop = raw.filtered(lambda r: r.id <= (hours.get(_bucket(r.timestamp, 3600)) or 0))
        count = len(drop)
        drop.unlink()
        return count


class FixIotDownsampleTiers(models.Model):
    _inherit = "fix.iot.downsample"

    @api.model
    def cron_retention(self):
        """The policy aggregation (fix_iot_ops), then the D17(b) tiers of every
        stream and the raw purge. Returns the counts."""
        out = super().cron_retention()
        now = fields.Datetime.now()
        purge = _flag(self.env, RETENTION_PURGE_PARAM, RETENTION_PURGE_DEFAULT)
        out.update({"tier_aggregates": 0, "tier_raw_dropped": 0, "hourly_dropped": 0})
        for stream in self.env["fix.iot.stream"].sudo().search([("state", "!=", "draft")]):
            try:
                with self.env.cr.savepoint():
                    out["tier_aggregates"] += stream._fix_rollup_tiers(now)
                    if purge:
                        out["tier_raw_dropped"] += stream._fix_purge_raw(now)
            except Exception:
                _logger.exception("M48 tier aggregation failed for stream %s", stream.name)
        if purge:
            keep = _param_int(self.env, HOURLY_RETENTION_PARAM, HOURLY_RETENTION_DEFAULT)
            old = (
                self.env["fix.iot.telemetry.aggregate"]
                .sudo()
                .search(
                    [
                        ("tier", "=", "hour"),
                        ("bucket_start", "<", now - timedelta(days=max(keep, 1))),
                    ]
                )
            )
            out["hourly_dropped"] = len(old)
            old.unlink()
        return out


class FixIotDeviceA07Erp(models.Model):
    _inherit = "fix.iot.device"

    def _fix_owner_module(self):
        """The module that owns the asset (spec §3.2: M48 measures, the owner acts)."""
        self.ensure_one()
        if self.equipment_id:
            return "M45"
        if self.site_id:
            return "M47"
        return "M48"

    def unlink(self):
        """M48-14: deleting a device took its streams, readings and aggregates
        with it. A device that ever streamed is decommissioned instead."""
        if not self.env.su:
            used = self.env["fix.iot.stream"].sudo().search_count(
                [("device_id", "in", self.ids)], limit=1
            ) or self.env["fix.iot.telemetry"].sudo().search_count(
                [("device_id", "in", self.ids)], limit=1
            )
            if used:
                raise UserError(
                    "A device with streams or readings is decommissioned, not deleted: its "
                    "history and aggregates are kept (FR-IOT-008)."
                )
        return super().unlink()


class FixIotAlertA07Erp(models.Model):
    _inherit = "fix.iot.alert"

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records.sudo():
            if not rec.routed_to_module and rec.device_id:
                rec._guarded().write({"routed_to_module": rec.device_id._fix_owner_module()})
        return records

    @api.model
    def _fix_ack_sla(self, severity):
        return _param_int(self.env, ACK_SLA_PARAM % severity)

    @api.model
    def cron_escalate(self):
        """AUT-IOT-10: an alert not acknowledged within its severity's SLA
        (setting cd_stream_registry.ack_sla_minutes_<severity>) escalates one
        level per elapsed SLA and asset.alert_escalated tells the owning role.
        A severity with no SLA set is not escalated. Idempotent per level."""
        now = fields.Datetime.now()
        escalated = 0
        for alert in self.sudo().search([("state", "=", "new")]):
            sla = self._fix_ack_sla(alert.severity)
            if sla <= 0 or not alert.create_date:
                continue
            level = int((now - alert.create_date).total_seconds() // (sla * 60))
            if level <= alert.escalation_level:
                continue
            alert._guarded().write({"escalation_level": level, "escalated_on": now})
            publish(
                alert.env,
                "asset.alert_escalated",
                "fix.iot.alert",
                alert.id,
                {
                    "alert": alert.name,
                    "level": level,
                    "severity": alert.severity,
                    "owner_module": alert.routed_to_module or "M48",
                    "elapsed_minutes": int((now - alert.create_date).total_seconds() // 60),
                },
            )
            escalated += 1
        return escalated


class FixIotRulePerformance(models.Model):
    _inherit = "fix.iot.rule"

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {
            "alerts_30d",
            "ack_rate_30d",
            "review_flagged_on",
        }

    alerts_30d = fields.Integer(string="Alerts (30 days)", readonly=True, copy=False)
    ack_rate_30d = fields.Float(string="Acknowledged % (30 days)", readonly=True, copy=False)
    review_flagged_on = fields.Date(string="Flagged for Review", readonly=True, copy=False)

    @api.model
    def cron_rule_performance(self):
        """BRU-IOT-15: measure each rule's alerts and acknowledgement rate over 30
        days. With cd_stream_registry.rule_review_ack_rate_pct set, a rule whose
        alerts are acknowledged less often than that is flagged for the IoT
        Administrators' review (once per day flagged)."""
        since = fields.Datetime.now() - timedelta(days=30)
        floor = _param_int(self.env, RULE_REVIEW_ACK_PCT_PARAM)
        today = _dhaka_today(self.env)
        Alert = self.env["fix.iot.alert"].sudo()
        flagged = 0
        for rule in self.sudo().search([]):
            alerts = Alert.search([("rule_id", "=", rule.id), ("create_date", ">=", since)])
            acked = alerts.filtered(lambda a: a.acked_on)
            rate = round(len(acked) / len(alerts) * 100, 1) if alerts else 0.0
            vals = {"alerts_30d": len(alerts), "ack_rate_30d": rate}
            if floor and alerts and rate < floor and rule.review_flagged_on != today:
                vals["review_flagged_on"] = today
                stream = rule.stream_id
                stream.message_post(
                    body="Rule %s: %d alert(s) in 30 days, %.1f%% acknowledged (below %d%%): "
                    "review it (BRU-IOT-15)." % (rule.name, len(alerts), rate, floor)
                )
                flagged += 1
            rule._guarded().write(vals)
        return flagged


class FixIotAdapterRotation(models.Model):
    _inherit = ["fix.iot.adapter", "mail.thread", "mail.activity.mixin"]
    _name = "fix.iot.adapter"

    def _fix_guarded_fields(self) -> set:
        return super()._fix_guarded_fields() | {"rotation_flagged_for"}

    rotation_flagged_for = fields.Datetime(
        string="Rotation Reminder For Key Of", readonly=True, copy=False
    )

    @api.model
    def cron_rotation_due(self):
        """AUT-IOT-21: an enabled adapter whose key is older than
        cd_stream_registry.adapter_key_max_age_days gets a rotation task for the
        IoT Administrators, once per key. Never revokes anything itself."""
        days = _param_int(self.env, KEY_MAX_AGE_PARAM)
        if days <= 0:
            return 0
        cut = fields.Datetime.now() - timedelta(days=days)
        admins = _holders(self.env, IOT_ADMIN)
        due = 0
        for adapter in self.sudo().search([("state", "=", "enabled")]):
            rotated = adapter.key_rotated_on
            if not rotated or rotated > cut or adapter.rotation_flagged_for == rotated:
                continue
            _todo(
                adapter, admins, "Rotate the key of adapter %s (set %s)" % (adapter.name, rotated)
            )
            adapter._guarded().write({"rotation_flagged_for": rotated})
            due += 1
        return due


class FixPredictionHorizon(models.Model):
    _inherit = ["fix.predictive.maintenance"]
    _name = "fix.predictive.maintenance"

    @api.model
    def cron_horizon_sweep(self):
        """AUT-IOT-16: a prediction whose horizon passed with no outcome and no
        action under way is flagged once to the IoT Operators, who record its
        outcome (confirmed, false alarm or unknown - excluded from precision)."""
        today = _dhaka_today(self.env)
        operators = _holders(self.env, IOT_OPERATOR)
        flagged = 0
        for pred in self.sudo().search(
            [
                ("outcome", "=", "pending"),
                ("prediction", "!=", "healthy"),
                ("horizon_flagged", "=", False),
            ]
        ):
            if not pred.horizon_end or pred.horizon_end >= today:
                continue
            if pred.action_ids.filtered(
                lambda a: a.state in ("approved", "dispatched") or a.approval_state == "pending"
            ):
                continue
            _todo(
                pred,
                operators,
                "Record the outcome of prediction %s: its horizon ended %s"
                % (pred.name, pred.horizon_end),
            )
            pred._guarded().write({"horizon_flagged": True})
            flagged += 1
        return flagged
