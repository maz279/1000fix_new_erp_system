# ruff: noqa: I001 - import order is Odoo load order: a file that _inherits a
# model must import after the file defining it. Do not alphabetise.
# cd_service_order — M01 Service Order Management (P04-M03)
from . import (
    fix_device_history_ext,
    fix_estimate,
    fix_fault_code,
    fix_qc_checklist,
    fix_service_order,
    fix_service_order_fault,
    fix_sla_policy,
    fix_so_approval,
    fix_work_order,
    fix_work_order_part_m15,
)

# S9 SLA instance engine: extends fix.sla.policy, so it imports after the
# module that defines it.
from . import fix_sla_instance

# A03 audit M33-5: party.merged consumers; extends fix.service.order and
# fix.device, so it imports after them.
from . import fix_party_merge_consumer

# A02 audit B2 / M01-P2: hand-back consumers and the abandoned-device cron;
# extends fix.service.order, so it imports after it.
from . import fix_service_order_handback

# D-11: the close gate refuses billed estimate parts that never left stock;
# extends fix.service.order, so it imports after it.
from . import fix_service_order_parts_gate

# G12: the billed-part-not-fitted exemption (routed M63 approval); extends
# fix.service.order and the D-11 gate above, so it imports after them.
from . import fix_so_part_exemption

# M01 capture audit (2026-11-17): the SLA escalation matrix; extends
# fix.sla.policy and fix.sla.kpi.instance (and its breach cron) and calls
# fix.service.order._fix_branch_users, so it imports after all of them.
from . import fix_sla_escalation
