# A07 · M48 IoT Telemetry & Predictive — surfaces, packs and KPIs over stream
# bindings, adapters, threshold rules, alerts, health/prediction and consent.
import datetime

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
    "fix.iot.rule": {
        "order": "stream_id, name",
        "limit": 300,
        "actions": {"action_pause", "action_activate"},
    },
    "fix.iot.alert": {
        "order": "create_date desc",
        "limit": 400,
        "actions": {"action_ack", "action_resolve"},
    },
    "fix.iot.action": {
        "order": "scheduled_on desc, id desc",
        "limit": 300,
        "actions": {"action_approve", "action_dispatch", "action_done"},
    },
    "fix.iot.consent": {
        "order": "valid_to desc, id desc",
        "limit": 300,
        "actions": {"action_revoke"},
    },
    "fix.iot.device": {"order": "id desc", "limit": 400, "actions": set()},
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
    return datetime.datetime.now()


def _telemetry_cutoff(hours=24):
    return _now() - datetime.timedelta(hours=hours)


def pipeline_health(env, date_from=None, date_to=None, **params):
    Adapter = env["fix.iot.adapter"].sudo()
    Telemetry = env["fix.iot.telemetry"].sudo()
    Alert = env["fix.iot.alert"].sudo()
    cutoff = _telemetry_cutoff(24)
    counts = {
        r["device_id"][0]: r["device_id_count"]
        for r in Telemetry.read_group([("timestamp", ">=", cutoff)], ["device_id"], ["device_id"])
        if r["device_id"]
    }
    last_seen = {}
    for device in env["fix.iot.device"].sudo().search([]):
        last_seen[device.id] = device.last_telemetry
    open_alerts = {}
    for alert in Alert.search([("state", "!=", "resolved")]):
        open_alerts[alert.device_id.id] = open_alerts.get(alert.device_id.id, 0) + 1
    rows = []
    for adapter in Adapter.search([]):
        streams = adapter.stream_ids
        devices = streams.mapped("device_id")
        readings = sum(counts.get(d.id, 0) for d in devices)
        latest = max((last_seen.get(d.id) for d in devices if last_seen.get(d.id)), default=None)
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
            "Readings are counted from the telemetry table; 'last seen' is the device's "
            "recorded telemetry timestamp."
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
    Device = env["fix.iot.device"].sudo()
    Alert = env["fix.iot.alert"].sudo()
    cutoff = _telemetry_cutoff(24)
    open_alerts = {}
    for alert in Alert.search([("state", "!=", "resolved")]):
        open_alerts[alert.device_id.id] = open_alerts.get(alert.device_id.id, 0) + 1
    telemetry_counts = {
        r["device_id"][0]: r["device_id_count"]
        for r in env["fix.iot.telemetry"]
        .sudo()
        .read_group([("timestamp", ">=", cutoff)], ["device_id"], ["device_id"])
        if r["device_id"]
    }
    rows = []
    for device in Device.search([]):
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
    rows = []
    for prediction in env["fix.predictive.maintenance"].sudo().search([]):
        days = prediction.estimated_days_to_failure
        if days <= 7:
            band, action = "Imminent", "Schedule intervention now"
        elif days <= 30:
            band, action = "Short", "Plan within the month"
        elif days <= 90:
            band, action = "Medium", "Add to the next PM cycle"
        else:
            band, action = "Long", "Monitor only"
        rows.append(
            {
                "equipment": prediction.equipment_id.name,
                "prediction": dict(prediction._fields["prediction"].selection).get(
                    prediction.prediction
                ),
                "confidence": round((prediction.confidence or 0.0) * 100, 1),
                "days": days,
                "band": band,
                "model": prediction.model_name or "—",
                "recommended": action,
            }
        )
    rows.sort(key=lambda r: r["days"])
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
            "recommended timing are derived from it, not re-estimated here."
        ],
        empty="No predictions recorded.",
    )


def telemetry_coverage(env, date_from=None, date_to=None, **params):
    cutoff = _telemetry_cutoff(24)
    counts = {
        r["device_id"][0]: r["device_id_count"]
        for r in env["fix.iot.telemetry"]
        .sudo()
        .read_group([("timestamp", ">=", cutoff)], ["device_id"], ["device_id"])
        if r["device_id"]
    }
    rows = []
    for stream in env["fix.iot.stream"].sudo().search([]):
        expected = 86400 // max(stream.sample_interval_sec or 60, 1)
        actual = counts.get(stream.device_id.id, 0)
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
    rows = []
    for stream in env["fix.iot.stream"].sudo().search([]):
        last = stream.device_id.last_telemetry
        lag = int((now - last).total_seconds()) if last else None
        gaps = "No data" if lag is None else ("Fresh" if lag <= 3600 else "Stale")
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
    rows.sort(key=lambda r: str(r["lag_sec"] or 0), reverse=True)
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
        ["Fresh = a reading within the last hour; Stale = older; No data = never seen."],
        empty="No stream bindings configured.",
    )


def alert_storm(env, date_from=None, date_to=None, **params):
    cutoff = _telemetry_cutoff(24)
    rows = []
    for device in env["fix.iot.device"].sudo().search([]):
        alerts = env["fix.iot.alert"].sudo().search([("device_id", "=", device.id)])
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
    for prediction in env["fix.predictive.maintenance"].sudo().search([]):
        rows.append(
            {
                "equipment": prediction.equipment_id.name,
                "prediction": dict(prediction._fields["prediction"].selection).get(
                    prediction.prediction
                ),
                "confidence": round((prediction.confidence or 0.0) * 100, 1),
                "days": prediction.estimated_days_to_failure,
                "outcome": dict(prediction._fields["outcome"].selection).get(prediction.outcome),
                "work_order": prediction.work_order_created,
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
    streams = env["fix.iot.stream"].sudo().search([])
    telemetry = env["fix.iot.telemetry"].sudo()
    alerts = env["fix.iot.alert"].sudo().search([])
    predictions = env["fix.predictive.maintenance"].sudo().search([])
    actions = env["fix.iot.action"].sudo().search([])
    policies = env["fix.iot.downsample"].sudo().search([("state", "=", "active")])
    cutoff = _telemetry_cutoff(24)
    readings = telemetry.search_count([("timestamp", ">=", cutoff)])
    confirmed = len(predictions.filtered(lambda p: p.outcome == "confirmed"))
    false_alarm = len(predictions.filtered(lambda p: p.outcome == "false_alarm"))
    compression = sum(policies.mapped("compression_pct"))
    return {
        "streams_ingesting": len(streams.filtered(lambda s: s.state == "active")),
        "ingest_rate_per_hour": round(readings / 24.0, 1),
        "open_alerts": len(alerts.filtered(lambda a: a.state != "resolved")),
        "prediction_precision": (
            round(confirmed / (confirmed + false_alarm) * 100, 1)
            if (confirmed + false_alarm)
            else 0.0
        ),
        "prescriptive_actions": len(actions),
        "retention_compression": (round(compression / len(policies), 1) if policies else 0.0),
    }
