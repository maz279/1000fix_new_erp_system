{
    "name": "1000FiX Supplier Risk",
    "summary": "M42 six-dimension supplier risk assessment with single-source control (CD-M42-04)",
    "description": """
CD-M42-04 (M42 spec §5.6, FR-SRM2-033):

- fix.supplier.risk — financial, operational, geographic, compliance,
  counterfeit and continuity ratings roll up to an overall tier that sets
  the re-assessment date; approval (not by the assessor) moves the
  profile's risk tier; a critical single-source dependency needs a named
  qualified alternate or a documented exception
""",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Purchase/Supplier Relationship",
    "depends": ["base", "mail", "cd_entity_config", "cd_event_outbox",
                 "cd_vendor_ext"],
    "data": [
        "security/ir.model.access.csv",
        "views/fix_supplier_risk_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M42-04",
    "x_module_id": "M42",
    "x_wave": "W4",
    "x_owner": "Supply Chain",
    "x_category": "E_Supply_Chain_and_Inventory",
    "x_tier": "T9",
}
