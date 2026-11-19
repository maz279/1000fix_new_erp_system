{
    "name": "1000FiX Warehouse Structure",
    "summary": "M41 W3 slice: warehouses, zones (quarantine non-reservable per BRU-INV-08), bins (CD-M41-01)",
    "description": """
CD-M41-01: the warehouse structure.

- fix.warehouse — central + depot warehouses on branches/OUs
- fix.warehouse.zone — typed zones; quarantine and inspection zones are
  NON-RESERVABLE (the BRU-INV-08 rule carried by the structure)
- fix.warehouse.bin — scannable leaf storage

Inbound/outbound operations (CD-M41-02/03) land with Phase 5's inventory
completion; this slice gives consignments and procurement destinations.
""",
    "version": "19.0.1.1.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Inventory/Warehouse",
    "depends": [
        "base",
        "mail",
        "cd_entity_config",
        "cd_requisition",
    ],
    "data": [
        "security/fix_isolation_rules.xml",
        "security/fix_wms_groups.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence.xml",
        "views/fix_wms_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M41-01",
    "x_module_id": "M41",
    "x_wave": "W3",
    "x_owner": "Supply Chain",
    "x_category": "E_Supply_Chain_and_Inventory",
    "x_tier": "T4",
}
