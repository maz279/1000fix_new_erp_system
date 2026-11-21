# ruff: noqa: I001 - import order is Odoo load order: a file that _inherits a
# model must import after the file defining it. Do not alphabetise.
# cd_contact_centre models.
from . import assistant_engine, fix_assistant_ops, fix_cc_ops, fix_contact_centre
from . import fix_notif_delivery

# S3/S4 routing: presence and capacity first, then the workstream that uses
# them, then the work item, then the queue operations that read all three.
from . import fix_cc_routing
from . import fix_cc_workstream
from . import fix_cc_workitem
from . import fix_cc_queue_ops

# Agent productivity (scripts, macros, knowledge binding) and quality
# (rubrics, bulk evaluation, intent mining). Both extend models defined
# above, so they import last.
from . import fix_cc_productivity
from . import fix_cc_quality

# S7 grounding service + translation: extends fix.assistant.intent and
# fix.conversation.turn, so it imports last.
from . import fix_assistant_llm

# A03 audit W1: open conversations follow a merged party (extends
# fix.conversation).
from . import fix_conversation_party_merge

# A02 audit B2: customer notifications for M01 events (extends
# fix.notif.delivery).
from . import fix_m01_notifications
from . import fix_a02_notifications

# A02 ERP pass 2 X5-14: M27 notices for the SLA, MSP report and M06 events
# (extends fix.notif.delivery).
from . import fix_a02r2_notifications
# A05 ERP audit XC-20: customer notifications for the M13 / M14 milestones
# (extends fix.notif.delivery, after the M01 helper it reuses).
from . import fix_a05_notifications

# A11 audit P2: approver notifications for M63 approval events (extends
# fix.notif.delivery).
from . import fix_approval_notify

# M32 capture audit: entity definitions, the action authority matrix and the
# handoff triggers. Extends fix.conversation and fix.assistant.intent (after
# fix_assistant_llm), so it imports last.
from . import fix_assistant_registers

# M27 capture audit pass 2: callbacks, voicemail, on-call rota, volume
# forecast, calibration, coaching, throttle, preference centre and urgency
# challenges. Extends fix.cc.queue and fix.notif.delivery, so it imports last.
from . import fix_cc_capture2

# M32 capture audit pass 2: intent thresholds, shadow evaluation, guard-rail
# stage and firing review, the unresolved queue. Extends fix.assistant.intent,
# .dataset, .guardrail, .ask and fix.conversation (after
# fix_assistant_registers, whose handoff stamp it reads), so it imports last.
from . import fix_assistant_capture2

# M32 capture audit pass 3: handoff signal phrases (detected before the
# classifier in intake_message) and abandoned-session logging. Overrides
# intake_message and _mark_abandoned and calls capture2's _log_unresolved, so
# it imports after fix_assistant_capture2.
from . import fix_assistant_signals
