# cd_settlement_ext — M53 (P10).
{
    "name": "1000FiX Settlement & Payout (W7)",
    "summary": "M53: Settlement & Payout (W7) (CD-M53-03)",
    "description": """
CD-M53-03 (P10) — Settlement & Payout (W7).

A08 M53 (2026-10-26): commission schemes (seller / partner rate tables with
effective-dated TDS), partner / referral commissions paid in payout runs,
escrow holds and clawbacks, payout reconciliation, seller statement
issue/settle, and the IAS 37 workmanship-warranty provision posted to GL.
Technician incentives are Payroll (A09), not settlement.
""",
    "version": "19.0.0.2.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Settlement & Payout (W7)",
    "depends": [
        "base",
        "portal",
        "mail",
        "cd_entity_config",
        "cd_gl_ext",
        "cd_tax_engine_bd",
        "cd_event_outbox",
        "cd_billing_engine",
        "cd_service_order",
        "cd_partner",
        "cd_marketplace",
    ],
    "data": [
        "security/fix_isolation_rules.xml",
        "security/fix_settlement_ext_security.xml",
        "security/ir.model.access.csv",
        "security/fix_settlement_m53_rules.xml",
        "data/fix_settlement_m53_data.xml",
        "views/cd_settlement_ext_views.xml",
        "views/fix_settlement_m53_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M53-03",
    "x_module_id": "M53",
    "x_wave": "W7",
    "x_owner": "Settlement & Payout (W7)",
    "x_category": "Phase10",
    "x_tier": "T10",
}
