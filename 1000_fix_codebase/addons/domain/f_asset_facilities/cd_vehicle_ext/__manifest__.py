# cd_vehicle_ext — M46 Fleet & Vehicle Management (P08-M08).
{
    "name": "1000FiX Fleet & Vehicles",
    "summary": "M46: fleet on Odoo fleet + the W2-deferred dispatch vehicle assignment with overlap prevention (CD-M46-nn)",
    "description": """
CD-M46-01 (P08-M08):

- fleet.vehicle EXTENSION — branch, driver (hr.employee), fitness and
  insurance expiry tracking (compliance flags)
- fix.vehicle.assignment — the W2-deferred dispatch connection
  (P05-M03-T06): a vehicle assigned to a service-order day; OVERLAPPING
  assignments for one vehicle are refused (a van cannot be in two
  places); the assignment is created from the work order's field
""",
    "version": "19.0.0.1.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Fleet",
    "depends": [
        "base",
        "mail",
        "fleet",
        "cd_entity_config",
        "cd_employee_core",
        "cd_service_order",
        "cd_event_outbox",
    ],
    "data": [
        "security/fix_isolation_rules.xml",
        "security/ir.model.access.csv",
        "views/fix_vehicle_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M46-01",
    "x_module_id": "M46",
    "x_wave": "W5",
    "x_owner": "Asset & Facilities",
    "x_category": "F_Asset_and_Facilities",
    "x_tier": "T9",
}
