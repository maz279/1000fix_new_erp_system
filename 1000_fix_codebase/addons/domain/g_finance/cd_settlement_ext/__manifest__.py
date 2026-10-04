# cd_settlement_ext — M53 (P10).
{
    "name": "1000FiX Settlement & Payout (W7)",
    "summary": "M53: Settlement & Payout (W7) (CD-M53-03)",
    "description": """
CD-M53-03 (P10) — Settlement & Payout (W7).
""",
    "version": "19.0.0.1.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Settlement & Payout (W7)",
    "depends": ["base", "mail", "cd_entity_config", "cd_gl_ext", "cd_tax_engine_bd", "cd_event_outbox"],
    "data": ["security/ir.model.access.csv", "views/cd_settlement_ext_views.xml"],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M53-03",
    "x_module_id": "M53",
    "x_wave": "W7",
    "x_owner": "Settlement & Payout (W7)",
    "x_category": "Phase10",
    "x_tier": "T10",
}
