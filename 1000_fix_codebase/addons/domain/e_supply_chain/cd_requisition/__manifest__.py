{
    "name": "1000FiX Procurement Core",
    "summary": "M16 W3 slice: requisition, purchase order with ordered/received quantities, PO/receipt events (CD-M16-01)",
    "description": """
CD-M16-01: the procurement core.

- fix.requisition — internal demand with the 05-04 authority matrix
- fix.purchase.order (+line) — the ORDERED side of the three-way match;
  action_record_receipt() publishes goods.received events that M52 consumes
- action_acknowledge() — the P05 vendor portal's PO acknowledgement surface
- Events: po.issued, po.acknowledged, goods.received (AS-08)

RFQ sourcing events (CD-M16-03) land with the vendor-portal completion.
""",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Inventory/Purchasing",
    "depends": [
        "base",
        "mail",
        "product",
        "hr",
        "cd_entity_config",
        "cd_employee_core",
        "cd_event_outbox",
    ],
    "data": [
        "security/fix_isolation_rules.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence.xml",
        "views/fix_requisition_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M16-01",
    "x_module_id": "M16",
    "x_wave": "W3",
    "x_owner": "Supply Chain",
    "x_category": "E_Supply_Chain_and_Inventory",
    "x_tier": "T4",
}
