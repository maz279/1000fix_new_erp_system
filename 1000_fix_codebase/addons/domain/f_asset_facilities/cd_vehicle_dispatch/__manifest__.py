# cd_vehicle_dispatch — M46 -> M02 dispatch bridge (A07 audit 2026-11-03, M46-1).
{
    "name": "1000FiX Fleet Dispatch Bridge",
    "summary": "M46 -> M02 dispatch bridge: a field order names its vehicle and driver, and "
    "dispatch runs the M46 dispatch gate and books the day's vehicle assignment",
    "description": """
A07 audit M46-1: the M46 dispatch gate was not connected to dispatch. This
bridge adds a vehicle and a driver to fix.field.order; action_dispatch (and a
later change of van, driver, technician or day on a live order) asserts the
vehicle dispatchable and creates or refreshes the day's fix.vehicle.assignment.

A separate module on purpose: cd_vehicle_ext stays independent of M02, and a
server whose database has not installed this bridge never loads it, so the
fix.field.order extension cannot break M02 before it is deliberately installed.
""",
    "version": "19.0.0.1.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Fleet",
    "depends": [
        "cd_vehicle_ext",
        "cd_field_service",
    ],
    "data": [
        "data/ir_config_parameter.xml",
        "views/fix_field_order_vehicle_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "x_module_id": "M46",
    "x_wave": "W5",
    "x_owner": "Asset & Facilities",
    "x_category": "F_Asset_and_Facilities",
    "x_tier": "T9",
}
