{
    "name": "1000FiX General Ledger Extension",
    "summary": "M19 core: branch/OU posting dimensions, 5-day period close, fixed-asset seam, suspense reconciliation, journal events (CD-M19-01)",
    "description": """
CD-M19-01: the M19 financial core on Odoo account + OCA account-financial-tools.

Owns:
- fix.journal.dimension — branch/cost-centre/OU on every posting (AS-03)
- fix.period.close (+line) — the 5-day month-end close process (CD-M19-05)
- fix.fixed.asset.seam — the capitalisation interface M49 extends (Phase 8)
- post_with_dimensions() — atomic post + dimensions + journal.posted event (AS-08)

The Bangladesh chart of accounts loads from the MD-* finance and statutory
content set (master data, AF-09-gated — loader lands with the content).
Suspense reconciliation (AR-006 §5.4) is enforced at close: the W2 inventory
suspense balance must be zero before a period can close.
""",
    "version": "19.0.2.5.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Finance/Accounting",
    "depends": [
        "base",
        "mail",
        "account",
        "cd_entity_config",
        "cd_event_outbox",
        "account_fiscal_year",
        # A08 S2/P1-1: manual journals, period reopens and control-flag changes
        # are routed approvals (M63 engine, DOFA tiers).
        "cd_workflow_engine",
    ],
    "data": [
        "security/fix_isolation_rules.xml",
        "security/ir.model.access.csv",
        "security/fix_gl_capture_security.xml",
        "data/fx_revaluation_sequences.xml",
        "views/fix_gl_ext_views.xml",
        "views/fix_gl_engine_views.xml",
        "data/fix_gl_cron.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M19-01",
    "x_module_id": "M19",
    "x_wave": "W3",
    "x_owner": "Commercial & Finance",
    "x_category": "G_Finance_and_Treasury",
    "x_tier": "T4",
}
