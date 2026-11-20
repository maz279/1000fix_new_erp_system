{
    "name": "1000FiX Supplier Performance Reviews & CARs",
    "summary": "M42 performance review cycle by segment and corrective action requests tracked to verified closure (CD-M42-03)",
    "description": """
CD-M42-03 (M42 spec §5.5):

- fix.supplier.review — scheduled reviews by segment cadence (strategic
  quarterly, preferred half-yearly, approved annually) with minuted
  outcomes, linked to the computed scorecard (FR-SRM2-030)
- fix.supplier.car — corrective action requests tracked to verified
  closure; the raiser cannot verify; overdue CARs escalate (FR-SRM2-031);
  the M42 -> M23 NCR stub rides as a reference until M23 lands

The scorecard figures stay COMPUTED from M16/M41 facts by
fix.supplier.scorecard (cd_cx_feedback, pair-10 consumer, T-04/T-05).
""",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Purchase/Supplier Relationship",
    "depends": ["base", "mail", "cd_entity_config", "cd_event_outbox",
                 "cd_vendor_ext", "cd_cx_feedback"],
    "data": [
        "security/ir.model.access.csv",
        "data/fix_supplier_scorecard_data.xml",
        "views/fix_supplier_scorecard_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M42-03",
    "x_module_id": "M42",
    "x_wave": "W4",
    "x_owner": "Supply Chain",
    "x_category": "E_Supply_Chain_and_Inventory",
    "x_tier": "T9",
}
