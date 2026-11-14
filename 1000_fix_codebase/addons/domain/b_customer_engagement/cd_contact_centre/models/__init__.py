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

# A11 audit P2: approver notifications for M63 approval events (extends
# fix.notif.delivery).
from . import fix_approval_notify

# M32 capture audit: entity definitions, the action authority matrix and the
# handoff triggers. Extends fix.conversation and fix.assistant.intent (after
# fix_assistant_llm), so it imports last.
from . import fix_assistant_registers
