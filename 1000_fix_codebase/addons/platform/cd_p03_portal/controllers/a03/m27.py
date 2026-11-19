# A03 · M27 Contact Centre (16743) — surfaces, report packs and KPIs over the
# real fix.conversation / fix.conversation.turn and the fix.cc.* operations
# records. Service level, AHT, FCR and abandonment are measured from the
# recorded timestamps; delivery tracking is declared as a missing telemetry
# model rather than invented.
import datetime

from odoo import http
from odoo.http import request

from ..p03_service_order_api import _require_internal

SURFACES = {
    "fix.conversation": {
        "order": "started_at desc, id desc",
        "limit": 300,
        # Resolve runs the REQ-27.1 wrap-up and REQ-27.2 digest gates; it was
        # refused here, so agents closed calls by editing state instead. The
        # dispatch hand-off opens an on-site service order and hands it to
        # M02 (it used to raise on a non-existent 'customer_id').
        # Create Complaint hands the contact to M34; the method is added by
        # cd_cx_feedback (A03 audit M27 G6).
        # Wrap Up (M27 capture audit 2026-11-14): the Agent Desktop page's
        # capture - disposition + notes, then the same resolve gates.
        "actions": {
            "action_claim",
            "action_resolve",
            "action_wrap_up",
            "action_create_field_work_order",
            "action_create_complaint",
        },
    },
    "fix.cc.queue": {
        "order": "sequence, name",
        "limit": 100,
        "actions": set(),
    },
    "fix.cc.disposition": {
        "order": "code",
        "limit": 200,
        "actions": set(),
    },
    "fix.cc.routing.rule": {
        "order": "priority, id",
        "limit": 200,
        "actions": set(),
    },
    "fix.cc.ivr.flow": {
        "order": "name",
        "limit": 100,
        "actions": set(),
    },
    "fix.cc.outbound.list": {
        "order": "priority, id",
        "limit": 200,
        "actions": set(),
    },
    "fix.cc.notif.template": {
        "order": "name",
        "limit": 200,
        "actions": set(),
    },
    "fix.cc.qa.evaluation": {
        "order": "evaluated_at desc, id desc",
        "limit": 300,
        # A03 audit M27 G11: dispute (the scored agent) and calibration
        # (a supervisor who is not the scored agent).
        "actions": {"action_dispute", "action_send_to_calibration", "action_finalise"},
    },
    "fix.cc.wfm.shift": {
        "order": "shift_date, start_hour",
        "limit": 300,
        "actions": set(),
    },
    # --- added by the A03 gap-closure build -------------------
    # Each of these is bound by a workspace screen below; an
    # unservable surface is what test_a03_registry_coverage exists
    # to catch, and a surface no screen opens is dead weight it
    # also catches.
    "fix.notif.provider": {
        "order": "channel, sequence, id",
        "limit": 200,
        "actions": set(),
    },
    "fix.notif.delivery": {
        "order": "queued_at desc, id desc",
        "limit": 300,
        "actions": {"action_cancel", "action_mark_sent_manually", "action_send"},
    },
    # Set My Presence (FR-CCE-032): the agent's own, logged presence change.
    "fix.cc.presence.status": {
        "order": "sequence, id",
        "limit": 100,
        "actions": {"action_set_my_presence"},
    },
    # BTRC Do-Not-Disturb registry (spec 10.1: M27 owns it; read at the point
    # of send by the delivery service). It was on no screen at all.
    "fix.dnd.registry": {
        "order": "msisdn",
        "limit": 300,
        "actions": set(),
    },
    "fix.cc.capacity.profile": {
        "order": "name",
        "limit": 200,
        "actions": set(),
    },
    "fix.cc.capacity.assignment": {
        "order": "agent_id, profile_id",
        "limit": 300,
        "actions": set(),
    },
    "fix.cc.agent.state": {
        "order": "agent_id",
        "limit": 300,
        "actions": {"heartbeat"},
    },
    "fix.cc.agent.state.log": {
        "order": "from_at desc, id desc",
        "limit": 300,
        "actions": set(),
    },
    "fix.routing.workstream": {
        "order": "sequence, name",
        "limit": 200,
        "actions": {"assign_pending"},
    },
    "fix.routing.ruleset": {
        "order": "workstream_id, sequence, id",
        "limit": 300,
        "actions": set(),
    },
    "fix.routing.bullseye.ring": {
        "order": "workstream_id, sequence, id",
        "limit": 200,
        "actions": set(),
    },
    "fix.routing.workitem": {
        "order": "priority desc, created_at, id",
        "limit": 300,
        "actions": {
            "action_accept",
            "action_pick",
            "action_reject",
            "action_start_work",
            "close_and_release",
            # Supervisor only (A03 audit M27 G9).
            "action_release_capacity",
        },
    },
    "fix.cc.wfm.adherence": {
        "order": "adherence_date desc, agent_id",
        "limit": 300,
        "actions": set(),
    },
    "fix.cc.script": {
        "order": "sequence, name",
        "limit": 200,
        "actions": {"action_publish"},
    },
    "fix.cc.script.step": {
        "order": "script_id, sequence, id",
        "limit": 300,
        "actions": set(),
    },
    "fix.cc.macro": {
        "order": "name",
        "limit": 200,
        "actions": set(),
    },
    "fix.cc.knowledge.binding": {
        "order": "sequence, id",
        "limit": 200,
        "actions": set(),
    },
    "fix.cc.script.completion": {
        "order": "conversation_id, completed_at",
        "limit": 300,
        "actions": set(),
    },
    "fix.cc.qa.rubric": {
        "order": "name",
        "limit": 200,
        "actions": {"action_publish", "action_retire"},
    },
    "fix.cc.qa.criterion": {
        "order": "rubric_id, sequence, id",
        "limit": 300,
        "actions": set(),
    },
    # --- M27 capture audit pass 2 (2026-11-19) -------------------
    # The spec records the sub-module pages had no model for. Pickers are
    # server-side: these reads run sudo, so a picker offers only what the
    # record may name (internal users, an open queue, a closed contact).
    "fix.cc.callback": {
        "order": "promised_by, id",
        "limit": 300,
        "actions": {"action_mark_reached", "action_log_failed_attempt", "action_cancel"},
        "pickers": {
            "assigned_user_id": [("share", "=", False)],
            "queue_id": [("active", "=", True)],
        },
    },
    "fix.cc.voicemail": {
        "order": "received_at desc, id desc",
        "limit": 300,
        "actions": {"action_queue_as_conversation", "action_discard"},
        "pickers": {"queue_id": [("active", "=", True)]},
    },
    "fix.cc.oncall.rota": {
        "order": "start_at desc, id desc",
        "limit": 300,
        "actions": set(),
        "pickers": {"user_id": [("share", "=", False)], "queue_id": [("active", "=", True)]},
    },
    "fix.cc.contact.forecast": {
        "order": "forecast_date desc, interval_hour, channel",
        "limit": 300,
        "actions": set(),
        "pickers": {"queue_id": [("active", "=", True)]},
    },
    "fix.cc.qa.calibration": {
        "order": "session_date desc, id desc",
        "limit": 200,
        "actions": {"action_close"},
        "pickers": {
            "conversation_id": [("state", "in", ("resolved_agent", "resolved_ai"))],
            "facilitator_id": [("share", "=", False)],
            "rubric_id": [("state", "=", "published")],
        },
    },
    "fix.cc.qa.calibration.line": {
        "order": "session_id, id",
        "limit": 300,
        "actions": set(),
        "pickers": {"evaluator_id": [("share", "=", False)]},
    },
    "fix.cc.qa.coaching": {
        "order": "session_date desc, id desc",
        "limit": 300,
        "actions": {"action_acknowledge"},
        "pickers": {
            "agent_id": [("share", "=", False)],
            "coach_id": [("share", "=", False)],
        },
    },
    "fix.cc.notif.throttle": {
        "order": "purpose, channel",
        "limit": 100,
        "actions": set(),
        "pickers": {},
    },
    "fix.cc.channel.preference": {
        "order": "partner_id, category",
        "limit": 300,
        "actions": set(),
        "pickers": {"partner_id": [("active", "=", True)]},
    },
    "fix.cc.urgency.challenge": {
        "order": "raised_at desc, id desc",
        "limit": 300,
        "actions": {"action_uphold", "action_reject"},
        "pickers": {"delivery_id": [("state", "in", ("sent", "delivered", "dry_run"))]},
    },
}

RESOLVED_STATES = ("resolved_ai", "resolved_agent")
DEFAULT_SL_TARGET = 20


def _pack(title, cols, labels, rows, notes, totals=None, empty=None):
    return {
        "title": title,
        "cols": cols,
        "labels": labels,
        "rows": rows,
        "totals": totals,
        "notes": notes,
        "empty": empty or "No data in this basis yet.",
    }


def _all(env):
    return env["fix.conversation"].sudo().search([])


def _seconds(a, b):
    if not a or not b:
        return None
    return max(0, int((b - a).total_seconds()))


def queue_live(env, date_from=None, date_to=None, **params):
    convs = _all(env).filtered(lambda c: c.state in ("new", "with_ai", "with_agent"))
    by_queue = {}
    now = datetime.datetime.now()
    for c in convs:
        key = c.queue_id.name if c.queue_id else "Unrouted"
        row = by_queue.setdefault(
            key, {"queue": key, "waiting": 0, "in_progress": 0, "longest_wait_s": 0}
        )
        if c.state == "new":
            row["waiting"] += 1
            row["longest_wait_s"] = max(row["longest_wait_s"], _seconds(c.started_at, now) or 0)
        else:
            row["in_progress"] += 1
    rows = sorted(by_queue.values(), key=lambda r: -(r["waiting"] + r["in_progress"]))
    return _pack(
        "Unified Queue Board — live workload",
        ["queue", "waiting", "in_progress", "longest_wait_s"],
        {
            "queue": "Queue",
            "waiting": "Waiting",
            "in_progress": "In Progress",
            "longest_wait_s": "Longest Wait (s)",
        },
        rows,
        [
            "Waiting = state new without an agent; in progress = with_ai/with_agent. "
            "Wait is measured from the recorded started_at."
        ],
        totals={
            "queue": "Total",
            "waiting": sum(r["waiting"] for r in rows),
            "in_progress": sum(r["in_progress"] for r in rows),
        }
        if rows
        else None,
        empty="The queue is clear — no open conversations.",
    )


def agent_desktop(env, date_from=None, date_to=None, **params):
    convs = _all(env)
    by_agent = {}
    for c in convs.filtered(lambda x: x.agent_id):
        row = by_agent.setdefault(
            c.agent_id.id,
            {
                "agent": c.agent_id.name,
                "handled": 0,
                "active": 0,
                "resolved": 0,
            },
        )
        row["handled"] += 1
        if c.state in ("with_agent",):
            row["active"] += 1
        if c.state in RESOLVED_STATES:
            row["resolved"] += 1
    rows = []
    for row in by_agent.values():
        row["fcr_pct"] = (
            round(row["resolved"] / row["handled"] * 100.0, 1) if row["handled"] else 0.0
        )
        rows.append(row)
    rows.sort(key=lambda r: -r["handled"])
    return _pack(
        "Agent Desktop Preview — workload per agent",
        ["agent", "handled", "active", "resolved", "fcr_pct"],
        {
            "agent": "Agent",
            "handled": "Handled",
            "active": "Active Now",
            "resolved": "Resolved",
            "fcr_pct": "Resolved %",
        },
        rows,
        [
            "Read-only desktop preview: the live agent console is the CPaaS/telephony "
            "surface; this table is the Odoo-side record of its work."
        ],
        empty="No conversations have been handled by an agent yet.",
    )


def agent_states(env, date_from=None, date_to=None, **params):
    today = datetime.date.today()
    shifts = env["fix.cc.wfm.shift"].sudo().search([("shift_date", "=", today)])
    rows = []
    for shift in shifts:
        active = _all(env).filtered(
            lambda c, uid=shift.agent_id.id: c.agent_id.id == uid and c.state == "with_agent"
        )
        rows.append(
            {
                "agent": shift.agent_id.name,
                "queue": shift.queue_id.name or "—",
                "shift": "%02d:00–%02d:00" % (shift.start_hour, shift.end_hour),
                "shift_state": shift.state,
                "active_conversations": len(active),
                "availability": "On a contact" if active else "Available",
            }
        )
    return _pack(
        "Agent States & Wrap-Up — today's roster",
        ["agent", "queue", "shift", "shift_state", "active_conversations", "availability"],
        {
            "agent": "Agent",
            "queue": "Queue",
            "shift": "Shift",
            "shift_state": "Roster State",
            "active_conversations": "Active Contacts",
            "availability": "Availability",
        },
        rows,
        [
            "Availability is derived from today's WFM shift and the agent's active "
            "conversations — no separate presence feed exists."
        ],
        empty="No shifts rostered for today.",
    )


def voice_summary(env, date_from=None, date_to=None, **params):
    convs = _all(env).filtered(lambda c: c.channel == "voice")
    rows = [
        {"metric": "Voice conversations", "value": len(convs), "basis": "channel=voice"},
        {
            "metric": "AI resolved",
            "value": len(convs.filtered(lambda c: c.state == "resolved_ai")),
            "basis": "state=resolved_ai",
        },
        {
            "metric": "Handed off to agent",
            "value": len(convs.filtered(lambda c: c.state == "with_agent")),
            "basis": "state=with_agent",
        },
        {
            "metric": "Abandoned",
            "value": len(convs.filtered(lambda c: c.state == "abandoned")),
            "basis": "state=abandoned",
        },
    ]
    ivr = env["fix.cc.ivr.flow"].sudo().search([("channel", "=", "voice"), ("active", "=", True)])
    rows.append(
        {
            "metric": "Active IVR flows",
            "value": len(ivr),
            "basis": ", ".join(ivr.mapped("name")) or "none configured",
        }
    )
    return _pack(
        "Voice & IVR Flows — hotline 16743",
        ["metric", "value", "basis"],
        {"metric": "Measure", "value": "Value", "basis": "Basis"},
        rows,
        [
            "Voice KPIs are counted from the conversation records; IVR flow versions "
            "are configuration (telephony execution is the CPaaS porting phase)."
        ],
    )


def digital_summary(env, date_from=None, date_to=None, **params):
    convs = _all(env).filtered(lambda c: c.channel != "voice")
    channels = {}
    for c in convs:
        row = channels.setdefault(
            c.channel, {"channel": c.channel, "conversations": 0, "resolved": 0, "ai_resolved": 0}
        )
        row["conversations"] += 1
        if c.state in RESOLVED_STATES:
            row["resolved"] += 1
        if c.state == "resolved_ai":
            row["ai_resolved"] += 1
    rows = []
    for row in channels.values():
        row["resolution_pct"] = (
            round(row["resolved"] / row["conversations"] * 100.0, 1)
            if row["conversations"]
            else 0.0
        )
        rows.append(row)
    rows.sort(key=lambda r: -r["conversations"])
    return _pack(
        "WhatsApp / Chat / Email / Social — digital channels",
        ["channel", "conversations", "resolved", "resolution_pct", "ai_resolved"],
        {
            "channel": "Channel",
            "conversations": "Conversations",
            "resolved": "Resolved",
            "resolution_pct": "Resolution %",
            "ai_resolved": "Resolved by AI",
        },
        rows,
        ["Resolution counts both agent- and AI-resolved conversations."],
        empty="No digital-channel conversations yet.",
    )


def notification_delivery(env, date_from=None, date_to=None, **params):
    configs = env["fix.notification.config"].sudo().search([])
    rows = []
    for cfg in configs:
        rows.append(
            {
                "channel": cfg.channel,
                "consent_class": cfg.consent_class,
                "frequency_cap": cfg.frequency_cap,
                "send_window": cfg.send_window,
                "stale_discard_hours": cfg.stale_discard_hours,
            }
        )
    return _pack(
        "Delivery Tracking & Retry — notification policy",
        ["channel", "consent_class", "frequency_cap", "send_window", "stale_discard_hours"],
        {
            "channel": "Channel",
            "consent_class": "Consent Class",
            "frequency_cap": "Frequency Cap",
            "send_window": "Send Window",
            "stale_discard_hours": "Stale Discard (h)",
        },
        rows,
        [
            "The estate has NO per-message delivery log model — this screen shows the "
            "enforced policy (caps, windows, stale discard) and does not pretend to "
            "report delivery receipts. Delivery telemetry is a declared gap."
        ],
        empty="No notification configuration exists yet.",
    )


def preference_summary(env, date_from=None, date_to=None, **params):
    configs = env["fix.notification.config"].sudo().search([])
    rows = []
    for cfg in configs:
        rows.append(
            {
                "channel": cfg.channel,
                "consent_class": cfg.consent_class,
                "combined_cap": cfg.combined_cap_non_transactional,
                "sms_route": cfg.sms_route or "—",
                "name": cfg.name,
            }
        )
    return _pack(
        "Consent & DND — channels, consent classes and caps",
        ["channel", "consent_class", "combined_cap", "sms_route", "name"],
        {
            "channel": "Channel",
            "consent_class": "Consent Class",
            "combined_cap": "Non-transactional Combined Cap",
            "sms_route": "SMS Route",
            "name": "Configuration",
        },
        rows,
        [
            "Per-customer DND preferences are applied by the notification engine against "
            "these channel policies; a customer-level preference register is a declared gap."
        ],
        empty="No consent policy configured yet.",
    )


def channel_mix(env, date_from=None, date_to=None, **params):
    convs = _all(env)
    channels = {}
    for c in convs:
        row = channels.setdefault(
            c.channel, {"channel": c.channel, "conversations": 0, "resolved": 0, "ai": 0}
        )
        row["conversations"] += 1
        if c.state in RESOLVED_STATES:
            row["resolved"] += 1
        if c.state == "resolved_ai":
            row["ai"] += 1
    total = len(convs)
    rows = []
    for row in channels.values():
        row["share_pct"] = round(row["conversations"] / total * 100.0, 1) if total else 0.0
        row["ai_pct"] = (
            round(row["ai"] / row["conversations"] * 100.0, 1) if row["conversations"] else 0.0
        )
        rows.append(row)
    rows.sort(key=lambda r: -r["conversations"])
    return _pack(
        "Channel Mix & Volumes",
        ["channel", "conversations", "share_pct", "resolved", "ai_pct"],
        {
            "channel": "Channel",
            "conversations": "Conversations",
            "share_pct": "Share %",
            "resolved": "Resolved",
            "ai_pct": "AI-Resolved %",
        },
        rows,
        [
            "Volumes are the recorded conversations per channel; share is of all "
            "conversations in the basis."
        ],
        totals={
            "channel": "Total",
            "conversations": total,
            "share_pct": 100.0,
            "resolved": sum(r["resolved"] for r in rows),
        }
        if rows
        else None,
        empty="No conversations recorded yet.",
    )


def service_level_by_interval(env, date_from=None, date_to=None, **params):
    convs = _all(env).filtered(lambda c: c.queued_at and c.answered_at)
    buckets = {}
    for c in convs:
        hour = c.queued_at.hour
        row = buckets.setdefault(hour, {"hour": "%02d:00" % hour, "offered": 0, "within_target": 0})
        row["offered"] += 1
        target = c.queue_id.target_answer_seconds or DEFAULT_SL_TARGET
        wait = _seconds(c.queued_at, c.answered_at) or 0
        if wait <= target:
            row["within_target"] += 1
    rows = []
    for hour in sorted(buckets):
        row = buckets[hour]
        row["sl_pct"] = (
            round(row["within_target"] / row["offered"] * 100.0, 1) if row["offered"] else 0.0
        )
        rows.append(row)
    total_offered = sum(r["offered"] for r in rows)
    total_within = sum(r["within_target"] for r in rows)
    return _pack(
        "Service Level by Interval — answered within the queue target",
        ["hour", "offered", "within_target", "sl_pct"],
        {
            "hour": "Queue Hour",
            "offered": "Offered",
            "within_target": "Within Target",
            "sl_pct": "Service Level %",
        },
        rows,
        [
            "Offered = conversations with both queued_at and answered_at. Target is the "
            "queue's own target_answer_seconds (default 20s → the 80/20 measure)."
        ],
        totals={
            "hour": "Total",
            "offered": total_offered,
            "within_target": total_within,
            "sl_pct": round(total_within / total_offered * 100.0, 1) if total_offered else 0.0,
        }
        if rows
        else None,
        empty="No answered conversations with queue timestamps yet.",
    )


def aht_fcr(env, date_from=None, date_to=None, **params):
    convs = _all(env).filtered(lambda c: c.answered_at)
    by_disp = {}
    for c in convs:
        key = c.disposition_id.code if c.disposition_id else "—"
        row = by_disp.setdefault(
            key,
            {
                "disposition": key,
                "handled": 0,
                "handle_seconds": 0.0,
                "with_handle": 0,
                "wait_seconds": 0.0,
                "with_wait": 0,
                "fcr": 0,
            },
        )
        row["handled"] += 1
        handle = _seconds(c.answered_at, c.ended_at)
        if handle is not None:
            row["handle_seconds"] += handle
            row["with_handle"] += 1
        wait = _seconds(c.queued_at, c.answered_at)
        if wait is not None:
            row["wait_seconds"] += wait
            row["with_wait"] += 1
        if c.fcr:
            row["fcr"] += 1
    rows = []
    for row in by_disp.values():
        rows.append(
            {
                "disposition": row["disposition"],
                "handled": row["handled"],
                "aht_s": round(row["handle_seconds"] / row["with_handle"], 1)
                if row["with_handle"]
                else 0.0,
                "avg_wait_s": round(row["wait_seconds"] / row["with_wait"], 1)
                if row["with_wait"]
                else 0.0,
                "fcr_pct": round(row["fcr"] / row["handled"] * 100.0, 1) if row["handled"] else 0.0,
            }
        )
    rows.sort(key=lambda r: -r["handled"])
    totals = {
        "disposition": "Total",
        "handled": sum(r["handled"] for r in rows),
        "aht_s": round(
            sum(r["aht_s"] * r["handled"] for r in rows) / max(1, sum(r["handled"] for r in rows)),
            1,
        ),
        "fcr_pct": round(
            sum(r["fcr_pct"] * r["handled"] for r in rows)
            / max(1, sum(r["handled"] for r in rows)),
            1,
        ),
    }
    return _pack(
        "AHT & FCR by Disposition",
        ["disposition", "handled", "aht_s", "avg_wait_s", "fcr_pct"],
        {
            "disposition": "Disposition",
            "handled": "Handled",
            "aht_s": "AHT (s)",
            "avg_wait_s": "Avg Wait (s)",
            "fcr_pct": "FCR %",
        },
        rows,
        [
            "AHT = answered_at → ended_at; wait = queued_at → answered_at. FCR is the "
            "recorded disposition outcome, not a guess."
        ],
        totals=totals if rows else None,
        empty="No answered conversations yet.",
    )


def qa_distribution(env, date_from=None, date_to=None, **params):
    evals = env["fix.cc.qa.evaluation"].sudo().search([])
    by_agent = {}
    for ev in evals:
        row = by_agent.setdefault(
            ev.agent_id.id,
            {
                "agent": ev.agent_id.name,
                "evaluations": 0,
                "score_sum": 0,
                "below_80": 0,
            },
        )
        row["evaluations"] += 1
        row["score_sum"] += ev.score
        if ev.score < 80:
            row["below_80"] += 1
    rows = []
    for row in by_agent.values():
        row["avg_score"] = (
            round(row["score_sum"] / row["evaluations"], 1) if row["evaluations"] else 0.0
        )
        rows.append({k: row[k] for k in ("agent", "evaluations", "avg_score", "below_80")})
    rows.sort(key=lambda r: -r["avg_score"])
    return _pack(
        "QA Score Distribution",
        ["agent", "evaluations", "avg_score", "below_80"],
        {
            "agent": "Agent",
            "evaluations": "Evaluations",
            "avg_score": "Avg Score",
            "below_80": "Evaluations < 80",
        },
        rows,
        [
            "Scores are the recorded QA evaluations (0–100); the 80 threshold is the "
            "coaching trigger."
        ],
        totals={
            "agent": "Total",
            "evaluations": sum(r["evaluations"] for r in rows),
            "avg_score": round(
                sum(r["avg_score"] * r["evaluations"] for r in rows)
                / max(1, sum(r["evaluations"] for r in rows)),
                1,
            ),
            "below_80": sum(r["below_80"] for r in rows),
        }
        if rows
        else None,
        empty="No QA evaluations recorded yet.",
    )


REPORTS = {
    "queue_live": queue_live,
    "agent_desktop": agent_desktop,
    "agent_states": agent_states,
    "voice_summary": voice_summary,
    "digital_summary": digital_summary,
    "notification_delivery": notification_delivery,
    "preference_summary": preference_summary,
    "channel_mix": channel_mix,
    "service_level_by_interval": service_level_by_interval,
    "aht_fcr": aht_fcr,
    "qa_distribution": qa_distribution,
}


def _delivery_rate(env):
    """Delivered / attempted as a percentage, or None when nothing was sent."""
    Delivery = env.get("fix.notif.delivery")
    if Delivery is None:
        return None
    attempted = Delivery.sudo().search_count([("state", "in", ("sent", "delivered", "failed"))])
    if not attempted:
        return None
    delivered = Delivery.sudo().search_count([("state", "=", "delivered")])
    return round(delivered / attempted * 100.0, 1)


def kpis(env):
    convs = _all(env)
    today = datetime.date.today()
    today_convs = convs.filtered(lambda c: c.started_at and c.started_at.date() == today)
    answered = convs.filtered(lambda c: c.queued_at and c.answered_at)
    within = 0
    for c in answered:
        target = c.queue_id.target_answer_seconds or DEFAULT_SL_TARGET
        if (_seconds(c.queued_at, c.answered_at) or 0) <= target:
            within += 1
    handled = convs.filtered(lambda c: c.answered_at and c.ended_at)
    aht_values = [_seconds(c.answered_at, c.ended_at) or 0 for c in handled]
    abandoned = len(convs.filtered(lambda c: c.state == "abandoned"))
    whatsapp = len(convs.filtered(lambda c: c.channel == "whatsapp"))
    # FCR over the answered contacts, the same basis as the AHT/FCR report
    fcr = len(answered.filtered(lambda c: c.fcr)) if answered else 0
    return {
        "conversations_today": len(today_convs),
        # Registry tile keys (static/src/a03/m27.js), from the conversation
        # log. Rates and averages are None while their denominator is empty
        # (no answered / no logged contact); the two counts read 0.
        "service_level_pct": round(within / len(answered) * 100.0, 1) if answered else None,
        "avg_handle_time_sec": round(sum(aht_values) / len(aht_values), 1) if aht_values else None,
        "fcr_rate": round(fcr / len(answered) * 100.0, 1) if answered else None,
        "abandonment_rate": round(abandoned / len(convs) * 100.0, 1) if convs else None,
        # in progress on the hotline (voice) right now: with the AI or an agent
        "active_calls": len(
            convs.filtered(lambda c: c.channel == "voice" and c.state in ("with_ai", "with_agent"))
        ),
        # waiting in a queue on any channel (the Queue Board's "waiting")
        "queued_contacts": len(convs.filtered(lambda c: c.state == "new")),
        "whatsapp_share": round(whatsapp / len(convs) * 100.0, 1) if convs else None,
        # Closed: fix.notif.delivery (S1) is the delivery log this tile was
        # waiting for. Delivered over ATTEMPTED, so a suppressed message --
        # one that consent or the BTRC window stopped -- is in neither the
        # numerator nor the denominator. Counting a correctly-withheld
        # message as a delivery failure would punish the gate for working.
        "notification_delivery": _delivery_rate(env),
    }


class P03CcApi(http.Controller):
    @http.route("/p03/cc/kpis", type="jsonrpc", auth="user", readonly=True)
    def cc_kpis(self, module=None, **kw):
        _require_internal(request.env)
        return {"M27": kpis(request.env)}
