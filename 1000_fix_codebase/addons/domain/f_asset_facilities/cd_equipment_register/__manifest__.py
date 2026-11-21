# cd_equipment_register — M45 Enterprise Asset & Test Equipment (P08-M08).
{
    "name": "1000FiX Equipment & Calibration",
    "summary": "M45: test-equipment register on Odoo maintenance + the W2-deferred calibration model with due-date enforcement (CD-M45-nn)",
    "description": """
CD-M45-01 (P08-M08):

- fix.equipment — internal test equipment on Odoo maintenance (the
  maintenance.equipment link stays authoritative for work orders);
  custodian employee, branch, category
- fix.calibration — the model M31 deferred in W2 (P05-M02-T07), now
  delivered: standard reference, result, NEXT DUE; equipment with an
  OVERDUE calibration is flagged unusable — calibration blocks usage,
  not nags (ISO 9001 clause 7.1.5)
- events: equipment.calibration.recorded, equipment.calibration.overdue
- A07 P1/P2 (2026-11-04): Quality Manager / Calibration Technician /
  Equipment Custodian roles; nightly calibration and custody jobs;
  calibration profiles, as-found/as-left readings, usage decision,
  retrospective impact assessment; custody, loss and service events
""",
    "version": "19.0.0.2.1",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Inventory/Equipment",
    "depends": [
        "base",
        "mail",
        "maintenance",
        "cd_entity_config",
        # A07 P0 recipe: the write-off approval is routed by the M63 engine
        "cd_workflow_engine",
        "cd_employee_core",
        "cd_event_outbox",
    ],
    "data": [
        # A07 P1 (2026-11-04): the spec's roles, before the ACLs that name them
        "security/fix_equipment_groups.xml",
        "security/fix_isolation_rules.xml",
        "security/fix_m45_ops_rules.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence.xml",
        "data/ir_cron.xml",
        "data/m45_backfill.xml",
        "views/fix_equipment_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M45-01",
    "x_module_id": "M45",
    "x_wave": "W5",
    "x_owner": "Asset & Facilities",
    "x_category": "F_Asset_and_Facilities",
    "x_tier": "T9",
}
