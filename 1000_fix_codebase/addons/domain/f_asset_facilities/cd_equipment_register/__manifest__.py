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
""",
    "version": "19.0.0.1.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Inventory/Equipment",
    "depends": [
        "base",
        "mail",
        "maintenance",
        "cd_entity_config",
        "cd_employee_core",
        "cd_event_outbox",
    ],
    "data": [
        "security/fix_isolation_rules.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence.xml",
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
