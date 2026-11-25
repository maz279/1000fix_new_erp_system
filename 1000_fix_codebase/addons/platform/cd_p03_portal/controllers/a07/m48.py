# A07 · M48 IoT Telemetry & Predictive — surfaces, packs and KPIs over stream
# bindings, adapters, threshold rules, alerts, health/prediction and consent.
import datetime

from odoo import fields

from ..p03_service_order_api import _company_domain
from .writable import WRITABLE

SURFACES = {
    "fix.iot.stream": {
        "order": "device_id, metric",
        "limit": 300,
        "actions": {
            "action_activate",
            "action_suspend",
            "action_set_consent_policy",
            # M48 capture audit (2026-11-17) FR-IOT-008.
            "action_decommission",
        },
        "pickers": {"signal_id": [("active", "=", True)]},
    },
    "fix.iot.adapter": {
        "order": "name",
        "limit": 100,
        "actions": {"action_enable", "action_disable", "action_rotate_key"},
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
            "action_change_settings",
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
            "action_cancel",
            "action_dispatch",
            "action_done_confirmed",
            "action_done_not_confirmed",
            # A07 ERP audit (2026-11-20) M48-09
            "action_done_prevented",
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
    # M48 capture audit (2026-11-17): a device is decommissioned, never deleted
    # (FR-IOT-008), and reports through a registered gateway (FR-IOT-002).
    "fix.iot.device": {
        "order": "id desc",
        "limit": 400,
        # A07 ERP audit (2026-11-20) M48-01: a bound device is re-bound by the
        # Consent Officer, with a reason.
        "actions": {"action_decommission", "action_change_binding"},
        "pickers": {
            "gateway_id": [("device_type", "=", "gateway"), ("decommissioned", "=", False)]
        },
    },
    # FR-IOT-004 signal definitions; FR-IOT-007 criticality assessments and the
    # health index they drive (FR-IOT-037/038, AUT-IOT-11).
    "fix.iot.signal": {"order": "code", "limit": 300, "actions": set()},
    "fix.iot.monitoring.scope": {
        "order": "review_due, id desc",
        "limit": 300,
        "actions": {"action_score_now"},
    },
    "fix.iot.health": {"order": "computed_at desc, id desc", "limit": 400, "actions": set()},
    # FR-IOT-012: a file export goes through the live ingest gates.
    "fix.iot.file.batch": {
        "order": "id desc",
        "limit": 200,
        "actions": {"action_process"},
        "pickers": {"adapter_id": [("state", "=", "enabled")]},
    },
    # FR-IOT-032 / BRU-IOT-16: bounded suppression with an approver.
    "fix.iot.maintenance.window": {
        "order": "date_from desc, id desc",
        "limit": 300,
        "actions": {"action_request", "action_approve", "action_cancel"},
        "pickers": {"device_id": [("decommissioned", "=", False)]},
    },
    # FR-IOT-042: the parts grid of a prescriptive action.
    "fix.iot.action.part": {"order": "id", "limit": 400, "actions": set()},
    # A07 P1 (2026-11-04) M48-11 / probe 57: the Downsampling Policy form had
    # no surface, so it could not save. Activation is requested here and
    # decided by the CTO through a retention change.
    "fix.iot.downsample": {
        "order": "stream_id",
        "limit": 300,
        "actions": {"action_activate", "action_request_deactivation"},
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
    # A07 (2026-11-07): the readings and aggregates had no screen, so an officer
    # could not see what a consent's treatment was about. Read only, as the caller:
    # readings can be personal data.
    "fix.iot.telemetry": {
        "order": "timestamp desc",
        "limit": 300,
        "actions": set(),
        "rules": True,
    },
    "fix.iot.telemetry.rollup": {
        "order": "bucket_start desc",
        "limit": 300,
        "actions": set(),
        "rules": True,
    },
    # A07 ERP audit (2026-11-20) D17(b): the hourly and daily tiers. Read only.
    "fix.iot.telemetry.aggregate": {
        "order": "bucket_start desc",
        "limit": 300,
        "actions": set(),
        "rules": True,
    },
}


# A surface added by the A07 ERP audit is served once writable.py (generated
# from the workspace forms) lists it; until it is regenerated the package
# would refuse to load (a07/__init__.py reads WRITABLE[model] for each).
for _new in ("fix.iot.telemetry.aggregate",):
    if _new not in WRITABLE:
        SURFACES.pop(_new)


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


# A07 ERP audit (2026-11-20) M48-17: every pack took date_from / date_to and
# ignored them. A period is now the Dhaka business days asked for: from 00:00
# Dhaka of date_from to 00:00 Dhaka after date_to, as naive UTC (Dhaka is UTC+6
# all year). With no period, the window stays the last 24 hours.
DHAKA_OFFSET = datetime.timedelta(hours=6)


def _window(date_from=None, date_to=None, hours=24):
    """(start, end, label) in naive UTC."""
    now = _now()
    if not date_from and not date_to:
        return now - datetime.timedelta(hours=hours), now, "the last %d hours" % hours
    start_day = fields.Date.to_date(date_from) if date_from else None
    end_day = fields.Date.to_date(date_to) if date_to else None
    start = (
        datetime.datetime.combine(start_day, datetime.time.min) - DHAKA_OFFSET
        if start_day
        else now - datetime.timedelta(hours=hours)
    )
    end = (
        datetime.datetime.combine(end_day + datetime.timedelta(days=1), datetime.time.min)
        - DHAKA_OFFSET
        if end_day
        else now
    )
    end = min(end, now)
    return start, end, "%s to %s (Dhaka days)" % (start_day or "-", end_day or "today")


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


def _stream_readings(env, streams, since=None, until=None):
    """{(device id, metric): (count, latest timestamp)} of the readings of
    `streams` dated in [since, until or now]. A reading belongs to a stream
    through its device AND metric (telemetry has no stream link): counting per
    device credited every stream of a device with all of the device's readings."""
    if not streams:
        return {}
    domain = [("device_id", "in", streams.device_id.ids), ("timestamp", "<=", until or _now())]
    if since:
        domain.append(("timestamp", ">=", since))
    groups = env["fix.iot.telemetry"]._read_group(
        domain, ["device_id", "metric"], ["__count", "timestamp:max"]
    )
    return {(device.id, metric): (count, last) for device, metric, count, last in groups}


def _key(stream):
    return (stream.device_id.id, stream.metric)


def _label(rec, field):
    return dict(rec._fields[field].selection).get(rec[field]) or "—"


def pipeline_health(env, date_from=None, date_to=None, **params):
    start, end, period = _window(date_from, date_to)
    visible_streams = _visible(env, "fix.iot.stream")
    counts = _stream_readings(env, visible_streams, start, end)
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
        "Pipeline Observability — adapters, streams and ingest over %s" % period,
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
            "readings_24h": "Readings in Period",
            "last_seen": "Last Seen",
            "open_alerts": "Open Alerts",
        },
        rows,
        [
            "Readings are counted per stream (device and metric) from the telemetry table over "
            "%s; 'last seen' is the latest reading of the adapter's streams." % period
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


def _device_asset(device):
    for name in ("equipment_id", "site_id", "vehicle_id", "customer_device_id"):
        if name in device._fields and device[name]:
            return device[name].display_name
    return "—"


def asset_health(env, date_from=None, date_to=None, **params):
    """A07 ERP audit (2026-11-20) M48-13: the pack recomputed its own score with
    three bands and disagreed with the stored index. It now shows the latest
    fix.iot.health row of each live device (the four bands of the index), and
    the worst band per asset."""
    devices = _visible(env, "fix.iot.device", [("decommissioned", "=", False)])
    Health = env["fix.iot.health"]
    latest = {}
    for row in _visible(env, "fix.iot.health", [("device_id", "in", devices.ids)]):
        prev = latest.get(row.device_id.id)
        if not prev or (row.computed_at, row.id) > (prev.computed_at, prev.id):
            latest[row.device_id.id] = row
    rank = {"healthy": 0, "watch": 1, "degraded": 2, "critical": 3}
    rows = []
    worst = {}
    for device in devices:
        row = latest.get(device.id)
        asset = _device_asset(device)
        band = row.band if row else None
        if band and rank[band] > rank.get(worst.get(asset), -1):
            worst[asset] = band
        rows.append(
            {
                "device": device.name,
                "identifier": device.device_id,
                "asset": asset,
                "status": dict(device._fields["status"].selection).get(device.status),
                "score": row.index_value if row else "—",
                "band": dict(Health._fields["band"].selection).get(band) if band else "Not scored",
                "trend": dict(Health._fields["trend"].selection).get(row.trend) if row else "—",
                "scored_at": str(row.computed_at)[:19] if row else "—",
                "factors": row.factors if row else "—",
            }
        )
    rows.sort(key=lambda r: (r["score"] == "—", r["score"] if r["score"] != "—" else 0))
    at_risk = len([a for a, b in worst.items() if b in ("degraded", "critical")])
    return _pack(
        "Asset Health Scoring — the stored health index of each device",
        [
            "device",
            "identifier",
            "asset",
            "status",
            "score",
            "band",
            "trend",
            "scored_at",
            "factors",
        ],
        {
            "device": "Device",
            "identifier": "Identifier",
            "asset": "Asset",
            "status": "Status",
            "score": "Health Index",
            "band": "Band",
            "trend": "Trend",
            "scored_at": "Scored At",
            "factors": "Contributing Factors",
        },
        rows,
        [
            "The index is the one scoring stores (Health Index History): open alerts, device "
            "status, readings in 24 hours, repairs in 90 days and asset age. %d asset(s) are "
            "degraded or critical. Decommissioned devices are not listed." % at_risk
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
            "equipment": prediction.asset_label or "—",
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
            "equipment": "Asset",
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
    start, end, period = _window(date_from, date_to)
    seconds = max(int((end - start).total_seconds()), 1)
    streams = _visible(env, "fix.iot.stream")
    live = {s.id for s in streams if s.state in ("active", "silent")}
    # A07 audit (2026-11-03) M48-7: counted per DEVICE, so a temperature stream
    # with 0 readings showed 100% on its device's vibration readings.
    counts = _stream_readings(env, streams, start, end)
    rows = []
    low = 0
    for stream in streams:
        expected = seconds // max(stream.sample_interval_sec or 60, 1)
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
        if stream.id in live and coverage < 80:
            low += 1
    rows.sort(key=lambda r: r["coverage"])
    return _pack(
        "Telemetry Coverage — expected vs received readings over %s" % period,
        ["stream", "device", "metric", "interval", "expected", "readings", "coverage", "state"],
        {
            "stream": "Stream",
            "device": "Device",
            "metric": "Metric",
            "interval": "Interval (s)",
            "expected": "Expected",
            "readings": "Received",
            "coverage": "Coverage %",
            "state": "State",
        },
        rows,
        [
            "Coverage compares received readings with the period / sample interval; "
            "%d live stream(s) are below 80%%. Draft and suspended streams are listed but "
            "not counted: they are not meant to be sending." % low
        ],
        empty="No stream bindings configured.",
    )


def stream_quality(env, date_from=None, date_to=None, **params):
    now = _now()
    streams = _visible(env, "fix.iot.stream")
    latest = _stream_readings(env, streams)
    policies = {
        p.stream_id.id: p
        for p in env["fix.iot.downsample"]
        .sudo()
        .search([("stream_id", "in", streams.ids), ("state", "=", "active")])
    }
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
        policy = policies.get(stream.id)
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
    start, end, period = _window(date_from, date_to)
    devices = _visible(env, "fix.iot.device")
    # M48-17: one search for all devices' alerts (it was one per device).
    alerts = _visible(env, "fix.iot.alert", [("device_id", "in", devices.ids)])
    by_device = {}
    for alert in alerts:
        by_device.setdefault(alert.device_id.id, []).append(alert)
    rows = []
    for device in devices:
        mine = by_device.get(device.id, [])
        recent = [a for a in mine if a.create_date and start <= a.create_date <= end]
        rows.append(
            {
                "device": device.name,
                "severity_critical": len([a for a in recent if a.severity == "critical"]),
                "severity_major": len([a for a in recent if a.severity == "major"]),
                "severity_minor": len([a for a in recent if a.severity == "minor"]),
                "open": len([a for a in mine if a.state != "resolved"]),
                "resolved": len([a for a in mine if a.state == "resolved"]),
                "total": len(mine),
                "last_alert": str(max((a.create_date for a in mine), default="—"))[:19],
            }
        )
    rows.sort(key=lambda r: (-r["severity_critical"], -r["severity_major"], -r["severity_minor"]))
    storm = len(
        [r for r in rows if r["severity_critical"] + r["severity_major"] + r["severity_minor"] >= 5]
    )
    return _pack(
        "Alert Storm Analysis — alert volume per device over %s" % period,
        [
            "device",
            "severity_critical",
            "severity_major",
            "severity_minor",
            "open",
            "resolved",
            "total",
            "last_alert",
        ],
        {
            "device": "Device",
            "severity_critical": "Critical",
            "severity_major": "Major",
            "severity_minor": "Minor",
            "open": "Open",
            "resolved": "Resolved",
            "total": "Total",
            "last_alert": "Last Alert",
        },
        rows,
        ["%d device(s) raised five or more alerts over %s." % (storm, period)],
        totals={
            "device": "Total",
            "severity_critical": sum(r["severity_critical"] for r in rows),
            "severity_major": sum(r["severity_major"] for r in rows),
            "severity_minor": sum(r["severity_minor"] for r in rows),
            "open": sum(r["open"] for r in rows),
            "resolved": sum(r["resolved"] for r in rows),
            "total": sum(r["total"] for r in rows),
        },
        empty="No devices registered.",
    )


# M48-09: a failure the intervention prevented is a true positive (spec §15).
TRUE_POSITIVE = ("confirmed", "prevented")


def _precision(predictions):
    tp = len(predictions.filtered(lambda p: p.outcome in TRUE_POSITIVE))
    fp = len(predictions.filtered(lambda p: p.outcome == "false_alarm"))
    return (round(tp / (tp + fp) * 100, 1) if (tp + fp) else None), tp, fp


def _in_window(domain, field, date_from, date_to):
    if date_from or date_to:
        start, end, _period = _window(date_from, date_to)
        return [*list(domain), (field, ">=", start), (field, "<", end)]
    return list(domain)


def prediction_outcomes(env, date_from=None, date_to=None, **params):
    rows = []
    predictions = _visible(
        env,
        "fix.predictive.maintenance",
        _in_window([], "create_date", date_from, date_to),
    )
    for prediction in predictions:
        rows.append(
            {
                "equipment": prediction.asset_label or "—",
                "prediction": dict(prediction._fields["prediction"].selection).get(
                    prediction.prediction
                ),
                "confidence": round((prediction.confidence or 0.0) * 100, 1),
                "days": prediction.estimated_days_to_failure,
                "outcome": dict(prediction._fields["outcome"].selection).get(prediction.outcome),
                "source": _label(prediction, "score_source"),
                # presentation-ready: a raw boolean renders as the literal
                # "false" in the grid cell
                "work_order": "Yes" if prediction.work_order_created else "—",
                "model": prediction.model_name or "—",
            }
        )
    rows.sort(key=lambda r: (r["outcome"] or "", -r["confidence"]))
    precision, tp, fp = _precision(predictions)
    return _pack(
        "Prediction Outcome Tracking",
        [
            "equipment",
            "prediction",
            "confidence",
            "days",
            "outcome",
            "source",
            "work_order",
            "model",
        ],
        {
            "equipment": "Asset",
            "prediction": "Prediction",
            "confidence": "Confidence %",
            "days": "Days to Failure",
            "outcome": "Verified Outcome",
            "source": "Score Source",
            "work_order": "WO Requested",
            "model": "Model",
        },
        rows,
        [
            "Precision = (confirmed + prevented) / (confirmed + prevented + false alarm); "
            "unknown is excluded; %s."
            % ("%.1f%%" % precision if precision is not None else "no verified outcome yet")
        ],
        totals={"equipment": "Confirmed + Prevented", "prediction": tp},
        empty="No predictions recorded.",
    )


def precision_by_model(env, date_from=None, date_to=None, **params):
    """M48-17: precision per model per month of the outcome (spec §14)."""
    predictions = _visible(
        env,
        "fix.predictive.maintenance",
        _in_window(
            [("outcome", "in", ("confirmed", "prevented", "false_alarm", "unknown"))],
            "outcome_recorded_on",
            date_from,
            date_to,
        ),
    )
    groups = {}
    for pred in predictions:
        when = pred.outcome_recorded_on or pred.create_date
        month = (when + DHAKA_OFFSET).strftime("%Y-%m") if when else "—"
        groups.setdefault((pred.model_name or "—", month), pred.browse())
        groups[(pred.model_name or "—", month)] |= pred
    rows = []
    for (model, month), preds in sorted(groups.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        precision, tp, fp = _precision(preds)
        rows.append(
            {
                "model": model,
                "month": month,
                "confirmed": len(preds.filtered(lambda p: p.outcome == "confirmed")),
                "prevented": len(preds.filtered(lambda p: p.outcome == "prevented")),
                "false_alarm": fp,
                "unknown": len(preds.filtered(lambda p: p.outcome == "unknown")),
                "precision": precision if precision is not None else "—",
            }
        )
    return _pack(
        "Prediction Precision by Model and Month",
        ["model", "month", "confirmed", "prevented", "false_alarm", "unknown", "precision"],
        {
            "model": "Model",
            "month": "Month (Dhaka)",
            "confirmed": "Confirmed",
            "prevented": "Prevented",
            "false_alarm": "False Alarm",
            "unknown": "Unknown (excluded)",
            "precision": "Precision %",
        },
        rows,
        ["The month of the recorded outcome. Unknown outcomes are excluded from precision."],
        empty="No prediction has a recorded outcome yet.",
    )


def alert_acknowledgement(env, date_from=None, date_to=None, **params):
    """M48-17: mean time to acknowledge and % acknowledged within the severity
    SLA (cd_stream_registry.ack_sla_minutes_<severity>; '—' when unset)."""
    start, end, period = _window(date_from, date_to, hours=24 * 30)
    alerts = _visible(
        env, "fix.iot.alert", [("create_date", ">=", start), ("create_date", "<", end)]
    )
    Param = env["ir.config_parameter"].sudo()
    rows = []
    for severity, label in alerts._fields["severity"].selection:
        mine = alerts.filtered(lambda a, s=severity: a.severity == s)
        acked = mine.filtered(lambda a: a.acked_on and a.create_date)
        minutes = [(a.acked_on - a.create_date).total_seconds() / 60 for a in acked]
        try:
            sla = int(Param.get_param("cd_stream_registry.ack_sla_minutes_%s" % severity) or 0)
        except ValueError:
            sla = 0
        within = len([m for m in minutes if sla and m <= sla])
        rows.append(
            {
                "severity": label,
                "raised": len(mine),
                "acknowledged": len(acked),
                "mtta_min": round(sum(minutes) / len(minutes), 1) if minutes else "—",
                "sla_min": sla or "—",
                "within_sla_pct": round(within / len(mine) * 100, 1) if (sla and mine) else "—",
                "escalated": len(mine.filtered(lambda a: a.escalation_level > 0)),
            }
        )
    return _pack(
        "Alert Acknowledgement — MTTA and SLA over %s" % period,
        [
            "severity",
            "raised",
            "acknowledged",
            "mtta_min",
            "sla_min",
            "within_sla_pct",
            "escalated",
        ],
        {
            "severity": "Severity",
            "raised": "Raised",
            "acknowledged": "Acknowledged",
            "mtta_min": "MTTA (min)",
            "sla_min": "SLA (min)",
            "within_sla_pct": "Within SLA %",
            "escalated": "Escalated",
        },
        rows,
        [
            "MTTA = mean of acknowledged-at minus raised-at. Within SLA counts alerts "
            "acknowledged inside their severity's SLA over all alerts raised."
        ],
    )


def intervention_register(env, date_from=None, date_to=None, **params):
    """M48-17: the proactive intervention register (spec §14)."""
    actions = _visible(env, "fix.iot.action", _in_window([], "create_date", date_from, date_to))
    rows = []
    for action in actions:
        rows.append(
            {
                "action": action.name,
                "asset": action.prediction_id.asset_label or "—",
                "type": _label(action, "action_type"),
                "preventive": "Yes" if action.preventive_request else "—",
                "scheduled": str(action.scheduled_on or "—"),
                "approved_by": action.approved_by.name or "—",
                "state": _label(action, "state"),
                "outcome": _label(action, "outcome") if action.outcome else "—",
            }
        )
    done = len(actions.filtered(lambda a: a.state == "done"))
    return _pack(
        "Proactive Intervention Register",
        ["action", "asset", "type", "preventive", "scheduled", "approved_by", "state", "outcome"],
        {
            "action": "Action",
            "asset": "Asset",
            "type": "Type",
            "preventive": "Preventive WO Request",
            "scheduled": "Scheduled",
            "approved_by": "Approved By",
            "state": "State",
            "outcome": "Outcome",
        },
        rows,
        [
            "%d proposed, %d approved, %d dispatched, %d done, %d cancelled."
            % tuple(
                len(actions.filtered(lambda a, s=s: a.state == s))
                for s in ("proposed", "approved", "dispatched", "done", "cancelled")
            )
        ],
        totals={"action": "Done", "asset": done},
        empty="No prescriptive action recorded.",
    )


def consent_register(env, date_from=None, date_to=None, **params):
    """M48-17: the telemetry consent register (spec §14)."""
    consents = _visible(env, "fix.iot.consent", _in_window([], "create_date", date_from, date_to))
    rows = []
    for consent in consents:
        subject = consent.device_id or consent.site_id or consent.partner_id
        rows.append(
            {
                "consent": consent.name,
                "subject": "%s: %s"
                % (_label(consent, "subject_type"), subject.display_name or "—"),
                "purpose": _label(consent, "purpose"),
                "signals": consent.signal_groups_permitted or "—",
                "proactive": "Yes" if consent.proactive_service else "—",
                "valid": "%s to %s" % (consent.granted_on or "—", consent.valid_to or "open"),
                "verification": _label(consent, "verification"),
                "state": _label(consent, "state"),
                "treatment": _label(consent, "treatment_state") if consent.treatment_state else "—",
            }
        )
    return _pack(
        "Telemetry Consent Register",
        [
            "consent",
            "subject",
            "purpose",
            "signals",
            "proactive",
            "valid",
            "verification",
            "state",
            "treatment",
        ],
        {
            "consent": "Consent",
            "subject": "Subject",
            "purpose": "Purpose",
            "signals": "Signals Permitted",
            "proactive": "Proactive Service",
            "valid": "Valid",
            "verification": "Verification",
            "state": "State",
            "treatment": "Revocation Treatment",
        },
        rows,
        [
            "A pending consent grants nothing until a Consent Officer who did not record it verifies it."
        ],
        empty="No telemetry consent recorded.",
    )


REPORTS = {
    "pipeline_health": pipeline_health,
    "asset_health": asset_health,
    "rul_estimation": rul_estimation,
    "telemetry_coverage": telemetry_coverage,
    "stream_quality": stream_quality,
    "alert_storm": alert_storm,
    "prediction_outcomes": prediction_outcomes,
    "precision_by_model": precision_by_model,
    "alert_acknowledgement": alert_acknowledgement,
    "intervention_register": intervention_register,
    "consent_register": consent_register,
}


def kpis(env):
    streams = _visible(env, "fix.iot.stream", [("state", "=", "active")])
    alerts = _visible(env, "fix.iot.alert", [("state", "!=", "resolved")])
    predictions = _visible(env, "fix.predictive.maintenance")
    # M48-17: a cancelled action is not a prescriptive action taken.
    actions = _visible(env, "fix.iot.action", [("state", "!=", "cancelled")])
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
    precision, _tp, _fp = _precision(predictions)
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
        "prediction_precision": precision,
        "prescriptive_actions": len(actions),
        "retention_compression": (
            round(sum(measured.mapped("measured_compression_pct")) / len(measured), 1)
            if measured
            else None
        ),
    }
