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
- A07 audit (2026-11-03) M46-2..5: the dispatch gate reads the statutory
  document register (mandatory types from an ir.config_parameter), open
  off-road records, open accidents, today's failed pre-use check and the
  driver's state and licence expiry; it runs on assignment create AND write.
  M02 dispatch is gated by it through the separate cd_vehicle_dispatch bridge
- A07 P0 recipe (2026-11-03) M46-5..10/13: workflow fields are guarded
  (fix.guarded.mixin); off-road return needs a passed re-check and a second
  person; suspension and reinstatement take a reason and a second person;
  checks no longer pass by default and are never rewritten; fuel exceptions
  are computed and held for review by someone other than the recorder;
  accident claims need a reference, the close a second person and a
  settlement, DOFA-routed above Tier 0 through the M63 engine
- A07 P1 (2026-11-04): roles (Logistics Manager; the Fleet Officer is Odoo
  fleet's officer), company/OU record rules on the ops models, four crons
  (document and licence expiry with the midnight off-road, PM due,
  telematics silence), one current document per type with its evidence
  scan, header dates read from the register, licence class matched to the
  vehicle, failed checks and accidents take the vehicle off-road, fuel hard
  rules refused at entry, insurer and evidence before a claim closes, and
  the domain events the bridge consumes
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
        # A07 P0 recipe: the M63 routed-approval engine (accident settlement)
        "cd_workflow_engine",
        "cd_employee_core",
        "cd_service_order",
        "cd_event_outbox",
    ],
    "data": [
        "security/cd_vehicle_ext_groups.xml",
        "security/fix_isolation_rules.xml",
        "security/fix_vehicle_ops_rules.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence.xml",
        "data/ir_config_parameter.xml",
        "data/ir_cron.xml",
        "data/fix_vehicle_upgrade.xml",
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
