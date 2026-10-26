{
    "name": "1000FiX Logistics & Consignment",
    "summary": "M03 core: consignment with the verified unbroken custody chain (G3-05), rider events (CD-M03-01/02)",
    "description": """
CD-M03-01/02: the logistics core.

- fix.consignment — pickups, deliveries, branch transfers, vendor returns
- fix.custody.scan — the chain's links; the CHAIN IS VERIFIED (monotonic
  step order; a gap breaks the chain — G3-05 evidence, not hope); a named
  exception is required to skip a step, never silent; a lost consignment
  raises an incident event
- Events: consignment.lost (+ custody scan events via chatter)
""",
    "version": "19.0.2.0.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Inventory/Logistics",
    "depends": [
        "base",
        "mail",
        "hr",
        "cd_entity_config",
        "cd_employee_core",
        "cd_event_outbox",
        "cd_service_order",
        "cd_requisition",
    ],
    "data": [
        "security/fix_isolation_rules.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence.xml",
        "views/fix_consignment_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M03-01",
    "x_module_id": "M03",
    "x_wave": "W3",
    "x_owner": "Supply Chain",
    "x_category": "E_Supply_Chain_and_Inventory",
    "x_tier": "T4",
}
