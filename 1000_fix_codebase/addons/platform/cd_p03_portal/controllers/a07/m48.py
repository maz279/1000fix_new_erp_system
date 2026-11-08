# A07 · M48 IoT Telemetry & Predictive — surfaces, packs and KPIs over stream
# bindings, adapters, threshold rules, alerts, health/prediction and consent.
import datetime

from odoo import fields

from ..p03_service_order_api import _company_domain

SURFACES = {
    "fix.iot.stream": {
        "order": "device_id, metric",
        "limit": 300,
        "actions": {"action_activate", "action_suspend"},
    },
    "fix.iot.adapter": {
        "order": "name",
        "limit": 100,
        "actions": {"action_enable", "action_disable"},
    },
    # A07 P0 recipe (2026-11-03) M48-3: pausing or loosening a rule is a
    # suppression request routed to an approver; tightening and resuming apply
    # at once. action_approve_suppression runs only from the approver's inbox.
    "fix.iot.rule": {
        "order": "stream_id, name",
        "limit": 300,
        "actions": {
            "action_pause",
            "action_change_threshold",
            "action_request_approval",
            "action_recall_approval",
            "action_activate",
        },
    },
    "fix.iot.alert": {
        "order": "create_date desc",
        "limit": 400,
        "actions": {"action_ack", "action_resolve"},
    },
    # M48-2: approval is requested here and decided from the approver's inbox
    # (action_approve is the engine's apply method, not a workspace button);
    # completion records the outcome on the prediction.
    "fix.iot.action": {
        "order": "scheduled_on desc, id desc",
        "limit": 300,
        "actions": {
            "action_request_approval",
            "action_recall_approval",
            "action_revise_terms",
            "action_dispatch",
            "action_done_confirmed",
            "action_done_not_confirmed",
        },
    },
    # A07 P1 (2026-11-04): a consent a non-officer records is verified by a
    # Consent Officer who did not record it; a revocation whose agreed
    # treatment is anonymisation leaves a manual task the officer closes.
    "fix.iot.consent": {
        "order": "valid_to desc, id desc",
        "limit": 300,
        "actions": {"action_revoke", "action_verify", "action_record_treatment"},
    },
    "fix.iot.device": {"order": "id desc", "limit": 400, "actions": set()},
    # A07 P1 (2026-11-04) M48-11 / probe 57: the Downsampling Policy form had
    # no surface, so it could not save. Activation is requested here and
    # decided by the CTO through a retention change.
    "fix.iot.downsample": {
        "order": "stream_id",
        "limit": 300,
        "actions": {"action_activate"},
    },
    # BRU-IOT-06: retention and downsampling changes, routed to the CTO;
    # action_apply is the engine's apply method, not a workspace button.
    "fix.iot.retention.change": {
        "order": "id desc",
        "limit": 300,
        "actions": {"action_request_approval", "action_recall_approval"},
    },
    # AUT-IOT-03: the gaps the liveness cron recorded. Read only.
    "fix.iot.gap": {"order": "detected_at desc, id desc", "limit": 400, "actions": set()},
}


def _pack(title, cols, labels, rows, notes, totals=None, empty=None):
    return {
        "title": title,
        "cols": cols,
        "labels": labels,
        "rows": rows,
        "totals": totals,
        "notes": notes,
        "empty": empty,
    }


def _now():
    # Odoo stores datetimes as naive UTC; datetime.now() is the server's local
    # clock and shifted every 24-hour window by the host's offset.
    return fields.Datetime.now()


def _telemetry_cutoff(hours=24):
    return _now() - datetime.timedelta(hours=hours)


# A07 audit (2026-11-03) M48-7: every pack and kpis() read sudo().search([]),
# so a clerk's Open Alerts counted another company's alerts he cannot see.
# Records are now SEARCHED with the caller's env, so the record rules (company
# and operating unit) apply, plus the explicit company fence; only the display
# read is sudo. A07 P1 (2026-11-04): every M48 model now carries a company
# (its own or its parent's) and a record rule; an adapter with no company is
# shared protocol configuration.
def _scope(env, model):
    return _company_domain(env, model)


def _visible(env, model, domain=(), **kw):
    """`model` records the caller may see, browsed with sudo for display."""
    Model = env[model]
    return Model.sudo().browse(Model.search(_scope(env, model) + list(domain), **kw).ids)


def _stream_readings(env, streams, since=None):
    """{(device id, metric): (count, latest timestamp)} of the readings of
    `streams` dated in [since, now]. A reading belongs to a stream through its
    device AND metric (telemetry has no stream link): counting per device
    credited every stream of a device with all of the device's readings."""
    if not streams:
        return {}
    domain = [("device_id", "in", streams.device_id.ids), ("timestamp", "<=", _now())]
    if since:
        domain.append(("timestamp", ">=", since))
    groups = env["fix.iot.telemetry"]._read_group(
        domain, ["device_id", "metric"], ["__count", "timestamp:max"]
    )
    return {(device.id, metric): (count, last) for device, metric, count, last in groups}


def _key(stream):
    return (stream.device_id.id, stream.metric)


def pipeline_health(env, date_from=None, date_to=None, **params):
    cutoff = _telemetry_cutoff(24)
    visible_streams = _visible(env, "fix.iot.stream")
    counts = _stream_readings(env, visible_streams, cutoff)
    latest_by_stream = _stream_readings(env, visible_streams)
    open_alerts = {}
    for alert in _visible(env, "fix.iot.alert", [("state", "!=", "resolved")]):
        open_alerts[alert.device_id.id] = open_alerts.get(alert.device_id.id, 0) + 1
    rows = []
    for adapter in _visible(env, "fix.iot.adapter"):
        streams = adapter.stream_ids & visible_streams
        devices = streams.mapped("device_id")
        readings = sum(counts.get(_key(s), (0, None))[0] for s in streams)
        latest = max(
            (latest_by_stream[_key(s)][1] for s in streams if _key(s) in latest_by_stream),
            default=None,
        )
        rows.append(
            {
                "adapter": adapter.name,
                "protocol": dict(adapter._fields["protocol"].selection).get(adapter.protocol),
                "state": dict(adapter._fields["state"].selection).get(adapter.state),
                "streams": len(streams),
                "active_streams": len(streams.filtered(lambda s: s.state == "active")),
                "readings_24h": readings,
                "last_seen": str(latest)[:19] if latest else "—",
                "open_alerts": sum(open_alerts.get(d.id, 0) for d in devices),
            }
        )
    rows.sort(key=lambda r: r["adapter"])
    return _pack(
        "Pipeline Observability — adapters, streams and ingest in the last 24 hours",
        [
            "adapter",
            "protocol",
            "state",
            "streams",
            "active_streams",
            "readings_24h",
            "last_seen",
            "open_alerts",
        ],
        {
            "adapter": "Adapter",
            "protocol": "Protocol",
            "state": "State",
            "streams": "Streams",
            "active_streams": "Active",
            "readings_24h": "Readings 24h",
            "last_seen": "Last Seen",
            "open_alerts": "Open Alerts",
        },
        rows,
        [
            "Readings are counted per stream (device and metric) from the telemetry table; "
            "'last seen' is the latest reading of the adapter's streams."
        ],
        totals={
            "adapter": "Total",
            "streams": sum(r["streams"] for r in rows),
            "active_streams": sum(r["active_streams"] for r in rows),
            "readings_24h": sum(r["readings_24h"] for r in rows),
            "open_alerts": sum(r["open_alerts"] for r in rows),
        },
        empty="No protocol adapters configured.",
    )


def asset_health(env, date_from=None, date_to=None, **params):
    cutoff = _telemetry_cutoff(24)
    devices = _visible(env, "fix.iot.device")
    open_alerts = {}
    for alert in _visible(env, "fix.iot.alert", [("state", "!=", "resolved")]):
        open_alerts[alert.device_id.id] = open_alerts.get(alert.device_id.id, 0) + 1
    telemetry_counts = {
        device.id: count
        for device, count in env["fix.iot.telemetry"]._read_group(
            [
                ("device_id", "in", devices.ids),
                ("timestamp", ">=", cutoff),
                ("timestamp", "<=", _now()),
            ],
            ["device_id"],
            ["__count"],
        )
    }
    rows = []
    for device in devices:
        alerts = open_alerts.get(device.id, 0)
        readings = telemetry_counts.get(device.id, 0)
        score = 100 - min(alerts * 12, 60)
        if device.status == "degraded":
            score -= 15
        elif device.status == "offline":
            score -= 30
        if readings == 0:
            score -= 20
        score = max(min(score, 100), 0)
        band = "Healthy" if score >= 80 else ("Watch" if score >= 55 else "At Risk")
        rows.append(
            {
                "device": device.name,
                "identifier": device.device_id,
                "equipment": device.equipment_id.name if device.equipment_id else "—",
                "site": device.site_id.name if device.site_id else "—",
                "status": dict(device._fields["status"].selection).get(device.status),
                "readings_24h": readings,
                "open_alerts": alerts,
                "score": score,
                "band": band,
            }
        )
    rows.sort(key=lambda r: r["score"])
    at_risk = len([r for r in rows if r["band"] == "At Risk"])
    return _pack(
        "Asset Health Scoring — device condition from alerts, status and ingestion",
        [
            "device",
            "identifier",
            "equipment",
            "site",
            "status",
            "readings_24h",
            "open_alerts",
            "score",
            "band",
        ],
        {
            "device": "Device",
            "identifier": "Identifier",
            "equipment": "Equipment",
            "site": "Site",
            "status": "Status",
            "readings_24h": "Readings 24h",
            "open_alerts": "Open Alerts",
            "score": "Health Score",
            "band": "Band",
        },
        rows,
        [
            "The score is a transparent rule: 100 minus 12 per open alert (cap 60), "
            "minus 15 degraded / 30 offline, minus 20 when no reading arrived in 24h. "
            "%d device(s) are in the At Risk band." % at_risk
        ],
        empty="No IoT devices registered.",
    )


def rul_estimation(env, date_from=None, date_to=None, **params):
    keyed = []
    for prediction in _visible(env, "fix.predictive.maintenance"):
        days = prediction.estimated_days_to_failure
        # A07 audit (2026-11-03) M48-6: days defaults to 0 ("imminent"), so a
        # HEALTHY prediction with no RUL entered was banded Imminent / "Schedule
        # intervention now". A healthy score with no RUL is not an estimate.
        estimated = bool(days) or prediction.prediction != "healthy"
        if not estimated:
            band, action = "Not estimated", "Monitor only (healthy, no RUL recorded)"
        elif days <= 7:
            band, action = "Imminent", "Schedule intervention now"
        elif days <= 30:
            band, action = "Short", "Plan within the month"
        elif days <= 90:
            band, action = "Medium", "Add to the next PM cycle"
        else:
            band, action = "Long", "Monitor only"
        row = {
            "equipment": prediction.equipment_id.name,
            "prediction": dict(prediction._fields["prediction"].selection).get(
                prediction.prediction
            ),
            "confidence": round((prediction.confidence or 0.0) * 100, 1),
            "days": days if estimated else "—",
            "band": band,
            "model": prediction.model_name or "—",
            "recommended": action,
        }
        keyed.append(((not estimated, days), row))
    keyed.sort(key=lambda kr: kr[0])
    rows = [row for _key_, row in keyed]
    return _pack(
        "RUL Estimation — remaining useful life from the recorded predictions",
        ["equipment", "prediction", "confidence", "days", "band", "model", "recommended"],
        {
            "equipment": "Equipment",
            "prediction": "Prediction",
            "confidence": "Confidence %",
            "days": "Days to Failure",
            "band": "RUL Band",
            "model": "Model",
            "recommended": "Recommended Timing",
        },
        rows,
        [
            "Days-to-failure is the value recorded on the prediction; the band and the "
            "recommended timing are derived from it, not re-estimated here. A healthy "
            "prediction with no days recorded is shown as Not estimated."
        ],
        empty="No predictions recorded.",
    )


def telemetry_coverage(env, date_from=None, date_to=None, **params):
    cutoff = _telemetry_cutoff(24)
    streams = _visible(env, "fix.iot.stream")
    # A07 audit (2026-11-03) M48-7: counted per DEVICE, so a temperature stream
    # with 0 readings showed 100% on its device's vibration readings.
    counts = _stream_readings(env, streams, cutoff)
    rows = []
    for stream in streams:
        expected = 86400 // max(stream.sample_interval_sec or 60, 1)
        actual = counts.get(_key(stream), (0, None))[0]
        coverage = round(min(actual / expected, 1.0) * 100, 1) if expected else 0.0
        rows.append(
            {
                "stream": stream.name,
                "device": stream.device_id.name,
                "metric": stream.metric,
                "interval": stream.sample_interval_sec,
                "expected": expected,
                "readings": actual,
                "coverage": coverage,
                "state": dict(stream._fields["state"].selection).get(stream.state),
            }
        )
    rows.sort(key=lambda r: r["coverage"])
    low = len([r for r in rows if r["coverage"] < 80])
    return _pack(
        "Telemetry Coverage — expected vs received readings over 24 hours",
        ["stream", "device", "metric", "interval", "expected", "readings", "coverage", "state"],
        {
            "stream": "Stream",
            "device": "Device",
            "metric": "Metric",
            "interval": "Interval (s)",
            "expected": "Expected 24h",
            "readings": "Received 24h",
            "coverage": "Coverage %",
            "state": "State",
        },
        rows,
        [
            "Coverage compares received readings with 86400 / sample interval; "
            "%d stream(s) are below 80%%." % low
        ],
        empty="No stream bindings configured.",
    )


def stream_quality(env, date_from=None, date_to=None, **params):
    now = _now()
    streams = _visible(env, "fix.iot.stream")
    latest = _stream_readings(env, streams)
    rows = []
    for stream in streams:
        # The stream's own latest reading, not the device's: a silent metric
        # on a chatty device is not fresh.
        last = latest.get(_key(stream), (0, None))[1]
        lag = int((now - last).total_seconds()) if last else None
        gaps = "No data" if lag is None else ("Fresh" if lag <= 3600 else "Stale")
        if stream.state == "silent":
            # A07 P1: the liveness cron opened a gap (BRU-IOT-09).
            gaps = "Silent (gap open)"
        policy = (
            env["fix.iot.downsample"]
            .sudo()
            .search([("stream_id", "=", stream.id), ("state", "=", "active")], limit=1)
        )
        rows.append(
            {
                "stream": stream.name,
                "device": stream.device_id.name,
                "adapter": stream.adapter_id.name if stream.adapter_id else "—",
                "rules": len(stream.rule_ids),
                "last_seen": str(last)[:19] if last else "—",
                "lag_sec": lag if lag is not None else "—",
                "quality": gaps,
                "downsample": policy.name if policy else "—",
            }
        )
    # Worst first: never seen, then the longest lag. (The lag was sorted as a
    # string, so "900" ranked above "86400".)
    rows.sort(key=lambda r: (r["lag_sec"] != "—", -(r["lag_sec"] if r["lag_sec"] != "—" else 0)))
    return _pack(
        "Stream Quality Report — freshness, rules and downsampling per stream",
        ["stream", "device", "adapter", "rules", "last_seen", "lag_sec", "quality", "downsample"],
        {
            "stream": "Stream",
            "device": "Device",
            "adapter": "Adapter",
            "rules": "Alert Rules",
            "last_seen": "Last Seen",
            "lag_sec": "Lag (s)",
            "quality": "Quality",
            "downsample": "Downsampling Policy",
        },
        rows,
        [
            "Fresh = a reading within the last hour; Stale = older; No data = never seen; "
            "Silent = the liveness check found no reading within the stream's silence window "
            "and recorded a gap."
        ],
        empty="No stream bindings configured.",
    )


def alert_storm(env, date_from=None, date_to=None, **params):
    cutoff = _telemetry_cutoff(24)
    rows = []
    for device in _visible(env, "fix.iot.device"):
        alerts = _visible(env, "fix.iot.alert", [("device_id", "=", device.id)])
        recent = alerts.filtered(lambda a: a.create_date and a.create_date >= cutoff)
        rows.append(
            {
                "device": device.name,
                "severity_major": len(recent.filtered(lambda a: a.severity == "major")),
                "severity_minor": len(recent.filtered(lambda a: a.severity == "minor")),
                "open": len(alerts.filtered(lambda a: a.state != "resolved")),
                "resolved": len(alerts.filtered(lambda a: a.state == "resolved")),
                "total": len(alerts),
                "last_alert": str(max(alerts.mapped("create_date"), default="—"))[:19],
            }
        )
    rows.sort(key=lambda r: (-r["severity_major"], -r["severity_minor"]))
    storm = len([r for r in rows if r["severity_major"] + r["severity_minor"] >= 5])
    return _pack(
        "Alert Storm Analysis — 24-hour alert volume per device",
        ["device", "severity_major", "severity_minor", "open", "resolved", "total", "last_alert"],
        {
            "device": "Device",
            "severity_major": "Major 24h",
            "severity_minor": "Minor 24h",
            "open": "Open",
            "resolved": "Resolved",
            "total": "Total",
            "last_alert": "Last Alert",
        },
        rows,
        ["%d device(s) raised five or more alerts in 24 hours." % storm],
        totals={
            "device": "Total",
            "severity_major": sum(r["severity_major"] for r in rows),
            "severity_minor": sum(r["severity_minor"] for r in rows),
            "open": sum(r["open"] for r in rows),
            "resolved": sum(r["resolved"] for r in rows),
            "total": sum(r["total"] for r in rows),
        },
        empty="No devices registered.",
    )


def prediction_outcomes(env, date_from=None, date_to=None, **params):
    rows = []
    for prediction in _visible(env, "fix.predictive.maintenance"):
        rows.append(
            {
                "equipment": prediction.equipment_id.name,
                "prediction": dict(prediction._fields["prediction"].selection).get(
                    prediction.prediction
                ),
                "confidence": round((prediction.confidence or 0.0) * 100, 1),
                "days": prediction.estimated_days_to_failure,
                "outcome": dict(prediction._fields["outcome"].selection).get(prediction.outcome),
                # presentation-ready: a raw boolean renders as the literal
                # "false" in the grid cell
                "work_order": "Yes" if prediction.work_order_created else "—",
                "model": prediction.model_name or "—",
            }
        )
    rows.sort(key=lambda r: (r["outcome"], -r["confidence"]))
    confirmed = len([r for r in rows if r["outcome"] == "Failure Confirmed"])
    false_alarm = len([r for r in rows if r["outcome"] == "False Alarm"])
    precision = (
        round(confirmed / (confirmed + false_alarm) * 100, 1) if (confirmed + false_alarm) else None
    )
    return _pack(
        "Prediction Outcome Tracking",
        ["equipment", "prediction", "confidence", "days", "outcome", "work_order", "model"],
        {
            "equipment": "Equipment",
            "prediction": "Prediction",
            "confidence": "Confidence %",
            "days": "Days to Failure",
            "outcome": "Verified Outcome",
            "work_order": "WO Created",
            "model": "Model",
        },
        rows,
        [
            "Precision = confirmed / (confirmed + false alarm); %s."
            % ("%.1f%%" % precision if precision is not None else "no verified outcome yet")
        ],
        totals={"equipment": "Confirmed", "prediction": confirmed},
        empty="No predictions recorded.",
    )


REPORTS = {
    "pipeline_health": pipeline_health,
    "asset_health": asset_health,
    "rul_estimation": rul_estimation,
    "telemetry_coverage": telemetry_coverage,
    "stream_quality": stream_quality,
    "alert_storm": alert_storm,
    "prediction_outcomes": prediction_outcomes,
}


def kpis(env):
    streams = _visible(env, "fix.iot.stream", [("state", "=", "active")])
    alerts = _visible(env, "fix.iot.alert", [("state", "!=", "resolved")])
    predictions = _visible(env, "fix.predictive.maintenance")
    actions = _visible(env, "fix.iot.action")
    policies = _visible(env, "fix.iot.downsample", [("state", "=", "active")])
    cutoff = _telemetry_cutoff(24)
    devices = _visible(env, "fix.iot.device")
    # Readings dated in [now - 24 h, now]: a future-dated row is not "recent".
    readings = env["fix.iot.telemetry"].search_count(
        [
            ("device_id", "in", devices.ids),
            ("timestamp", ">=", cutoff),
            ("timestamp", "<=", _now()),
        ]
    )
    recent = _stream_readings(env, streams, cutoff)
    confirmed = len(predictions.filtered(lambda p: p.outcome == "confirmed"))
    false_alarm = len(predictions.filtered(lambda p: p.outcome == "false_alarm"))
    # A07 P1 (2026-11-04) M48-7 / probe 55: this averaged a TYPED
    # compression_pct (99999 accepted). It is now the compression the
    # retention cron measured from the aggregates it actually wrote; None
    # (shown as "-") until a policy has aggregated anything.
    measured = policies.filtered(lambda p: p.raw_points_rolled > 0)
    return {
        # A07 audit (2026-11-03) M48-7: this counted state=active, so it read 9
        # while no reading had arrived for 6 days. Now: active streams with at
        # least one reading of their own in the last 24 hours.
        "streams_ingesting": len([s for s in streams if _key(s) in recent]),
        "ingest_rate_per_hour": round(readings / 24.0, 1),
        "open_alerts": len(alerts),
        # None (shown as "—") when nothing is verified: 0.0 read as 0% precision.
        "prediction_precision": (
            round(confirmed / (confirmed + false_alarm) * 100, 1)
            if (confirmed + false_alarm)
            else None
        ),
        "prescriptive_actions": len(actions),
        "retention_compression": (
            round(sum(measured.mapped("measured_compression_pct")) / len(measured), 1)
            if measured
            else None
        ),
    }
