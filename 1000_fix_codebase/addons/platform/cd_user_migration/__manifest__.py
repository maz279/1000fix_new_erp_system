# cd_user_migration — real-user take-on (2026-11-09).
{
    "name": "1000FiX User Migration Take-On",
    "summary": "Legacy org traceability + default warehouse on the employee master for the real-user cut-over",
    "description": """
Added for the 2026-11-09 real-user migration (user.xlsx / employee.xlsx /
warehouse.xlsx take-on onto fix_real):

- hr.employee.legacy_login — the legacy system login this employee maps to
- hr.employee.legacy_branch_name — the legacy branch label verbatim (the
  legacy taxonomy is brand+location; the new fix.branch is geographic)
- hr.employee.legacy_operating_unit — the legacy product/service line
  (RMA, Xiaomi, Dell AIO ...); the new operating.unit is geographic, so the
  legacy dimension is preserved verbatim for the crosswalk and later FP&A
  modelling
- hr.employee.default_warehouse_id — the legacy login's default warehouse
  (user.xlsx "Default Warehouse"), resolved through the warehouse crosswalk

The module owns no models, views or ACLs of its own: it only extends the
employee master so the migration has referential homes that survive re-runs.
""",
    "version": "19.0.0.1.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Human Resources",
    "depends": [
        "hr",
        "cd_hr_core",
        "cd_wms_structure",
    ],
}
