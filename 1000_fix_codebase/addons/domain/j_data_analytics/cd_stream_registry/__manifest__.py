# cd_stream_registry (P11).
{
    "name": "1000FiX IoT Telemetry & Predictive Maintenance",
    "summary": "M48: IoT Telemetry & Predictive Maintenance",
    "description": "CD-M48-01 (P11).",
    "version": "19.0.0.2.1",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "IoT Telemetry & Predictive Maintenance",
    "depends": [
        "base",
        "mail",
        "cd_entity_config",
        "cd_equipment_register",
        "cd_facility",
        "cd_event_outbox",
        # A07 P0 recipe: prescriptive-action and rule-suppression approvals are
        # routed through the M63 engine (fix.approvable.mixin).
        "cd_workflow_engine",
        # M48 capture audit (2026-11-17): a prescriptive action names the parts it
        # likely needs (FR-IOT-042); stock is read at run time when installed.
        "product",
    ],
    "data": [
        # A07 P1 (2026-11-04): the spec's roles, their ACLs, the company fence
        # on the six un-ruled models, and the scheduler.
        "security/fix_iot_groups.xml",
        "security/fix_isolation_rules.xml",
        "security/fix_iot_scope_rules.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence.xml",
        "data/ir_cron.xml",
        "views/cd_stream_registry_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M48-01",
    "x_module_id": "M48",
    "x_wave": "W8",
    "x_owner": "IoT Telemetry & Predictive Maintenance",
    "x_category": "Phase11",
    "x_tier": "T11",
}
