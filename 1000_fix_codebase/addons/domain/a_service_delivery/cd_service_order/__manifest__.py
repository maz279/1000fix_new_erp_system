# cd_service_order — M01 Service Request & Order Management core (P04-M03).
# The flagship module: 88 requirements, full state machine, SLA engine.
{
    "name": "1000FiX Service Order",
    "summary": "Service order/work order core with full state machine, SLA clocks, diagnostic tree, estimate/approval, QC checklist (M01-core)",
    "description": """
CD-M01-nn: Service Request & Order Management core (M01, W1 slice).

The largest single module in the programme. AS-06: state transitions declared
in one place per model (DP-01). SLA computation lives in services/ so it is
unit-testable without a database (AR-007 section 3.1).
""",
    "version": "19.0.2.3.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Service Delivery/Orders",
    "depends": [
        "base",
        "mail",
        "cd_entity_config",
        "cd_catalogue",
        "cd_party_master",
        "cd_device_registry",
        "cd_document_core",
        "cd_event_outbox",
        "cd_employee_core",
        "cd_workflow_engine",
        # A06 M15-10: a work-order part leaves the M15 ledger
        "cd_inventory",
    ],
    "data": [
        "data/fix_sla_instance_cron.xml",
        "data/fix_estimate_expiry_cron.xml",
        "security/fix_service_order_groups.xml",
        "security/fix_isolation_rules.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence.xml",
        "data/fix_fault_codes.xml",
        "data/fix_party_merge_consumers.xml",
        # A02 audit B2/B3/M01-P2: hand-back and breach consumers, the default
        # SLA policy and the abandoned-device cron.
        "data/fix_m01_handback_consumers.xml",
        "data/fix_sla_default_policy.xml",
        "data/fix_m01_lifecycle_cron.xml",
        "views/fix_service_order_views.xml",
        "views/fix_estimate_views.xml",
        "views/fix_fault_code_views.xml",
        "views/fix_sla_policy_views.xml",
        "views/fix_device_history_order_views.xml",
        "report/report_jobcard.xml",
    ],
    "installable": True,
    "application": True,
    "x_cd_id": "CD-M01-01",
    "x_module_id": "M01",
    "x_wave": "W1",
    "x_owner": "Service Delivery",
    "x_category": "A_Service_Delivery_and_Operations",
    "x_tier": "T3",
}
