{
    "name": "1000FiX Procurement Core",
    "summary": "M16 W3 slice: requisition, purchase order with ordered/received quantities, PO/receipt events (CD-M16-01)",
    "description": """
CD-M16-01: the procurement core.

- fix.requisition — internal demand, approved through the M63 engine on the
  DOFA ladder by amount (split purchases summed), requester never approves
- fix.purchase.order (+line) — the ORDERED side of the three-way match;
  approved by amount before it is sent, pinned after approval, locked after
  send (changes by versioned change order)
- fix.purchase.receipt (+line) — the posted goods receipt referencing the PO
  lines; inspection outcomes feed the accepted (matchable) quantity
- action_acknowledge() — the P05 vendor portal's PO acknowledgement surface
- Roles: Buyer, Receiver, Procurement Approver, Procurement Manager (A06 S1)
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
        "cd_workflow_engine",
    ],
    "data": [
        "security/fix_requisition_groups.xml",
        "security/fix_isolation_rules.xml",
        "security/ir.model.access.csv",
        "security/fix_requisition_rules.xml",
        "data/ir_sequence.xml",
        "data/ir_cron.xml",
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
