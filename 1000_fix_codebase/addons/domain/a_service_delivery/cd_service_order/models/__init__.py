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
    fix_work_order,
)

# S9 SLA instance engine: extends fix.sla.policy, so it imports after the
# module that defines it.
from . import fix_sla_instance
