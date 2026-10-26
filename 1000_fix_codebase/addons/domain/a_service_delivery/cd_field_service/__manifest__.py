{
    "name": "1000FiX Field Service, Dispatch & Geospatial Platform",
    "version": "19.0.2.0.0",
    "category": "Service Delivery",
    "summary": "AI dispatch board, route optimization, field order tracking, accept/decline flows and geofencing",
    "author": "1000FiX Services Ltd.",
    "website": "https://1000fix.com",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
        "operating_unit",
        "cd_entity_config",
        "cd_service_order",
        "cd_document_core",
        "cd_event_outbox",
        "cd_employee_core",
        # hr.employee.operating_unit_id (read by fix.technician.location.record_ping)
        # is defined by cd_hr_core - no cycle: cd_hr_core never reaches this module
        "cd_hr_core",
        "cd_inventory",
        # M02 suggestion engine: fix.certification.dispatch_eligibility and
        # the fix.roster.slot availability check
        "cd_competency",
        "cd_attendance",
    ],
    "data": [
        "security/fix_isolation_rules.xml",
        "security/fix_field_service_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence.xml",
        # sample field orders removed from install data (R01 re-audit 2026-10-22):
        # synthetic records belong in db/seeds (DE-12/13), and they required a
        # service order that a clean install does not have (NOT NULL order_id).
        "views/fix_field_service_views.xml",
        "views/fix_field_service_menus.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "x_module_id": "M02",
    "x_cd_id": "CD-M02-01",
    "x_wave": "W2",
    "x_tier": "T2",
    "x_owner": "Service Delivery",
    "x_category": "A_Service_Delivery",
}
