{
    "name": "1000FiX Supplier Profile & Commercial Terms",
    "summary": "M42 supplier profile over the party, segmentation, compliance documents, bank-change control, agreements and governed prices (CD-M42-01)",
    "description": """
CD-M42-01 (M42 Supplier Relationship & Performance, spec §5.1-§5.4):

- fix.supplier.profile — the supplier role over an M33 party: the twelve
  classes (FR-SRM2-002), segment, risk tier, supplied categories (T-12: one
  profile per party per legal entity); suspend/block with a recorded reason
- fix.supplier.segment.review — governed segment / risk-tier change; the
  proposer cannot approve (SoD)
- fix.supplier.document — the compliance register with daily idempotent
  expiry (T-07) and evidence hashing (T-11)
- fix.supplier.bank.change — documented verification + second-person
  approval, prior value hashed, immutable once decided (FR-SRM2-018, T-06)
- fix.supplier.agreement / .price.list / .price.change — agreements with
  expiry warning (FR-SRM2-026), agreed prices, and price-change governance
  (FR-SRM2-023)

Access follows spec §13 through six function groups (Viewer, Procurement
Officer, Quality Manager, Procurement Manager, Finance Manager, CFO);
segregation of duties is enforced in the models on top of them.

Each model behind a P03 workspace form declares `_p03_capture`; the P03
portal discovers it through the registry (no platform -> domain dependency).
""",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Purchase/Supplier Relationship",
    "depends": ["base", "mail", "product", "cd_entity_config", "cd_rbac_ext", "cd_event_outbox"],
    "data": [
        "security/fix_vendor_ext_security.xml",
        "security/ir.model.access.csv",
        "data/fix_vendor_ext_cron.xml",
        "views/fix_vendor_ext_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M42-01",
    "x_module_id": "M42",
    "x_wave": "W4",
    "x_owner": "Supply Chain",
    "x_category": "E_Supply_Chain_and_Inventory",
    "x_tier": "T9",
}
