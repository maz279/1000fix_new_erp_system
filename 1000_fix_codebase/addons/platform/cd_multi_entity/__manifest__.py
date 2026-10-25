# cd_multi_entity — Milestone R10-M01 (M65 Multi-Entity, Multi-Country & Localisation).
# Manifest conforms to AR-007 section 3.2: 1000FiX mandatory keys present.
{
    "name": "1000FiX Multi-Entity, Multi-Country & Consolidation",
    "summary": "M65 Multi-Company Consolidation, Inter-Company Rules, BD Country Pack & Statutory Calendars",
    "description": """
M65 Multi-Entity, Multi-Country & Localisation — the enterprise consolidation module.

Owns:
- fix.consolidation.book (Group multi-company financial consolidation)
- fix.consolidation.line (Consolidated line items with currency translation)
- fix.elimination.entry (Automated inter-company revenue/expense/receivable eliminations)
- fix.intercompany.rule (Inter-company transfer pricing and transaction rules)
- fix.intercompany.transaction (Matched inter-company settlements and mirror entries)
- fix.entity.localisation (BD address formats, BIN/TIN, Mushak statutory calendar)
- fix.nil.return.generator (Statutory nil-return automation for newly registered entities)
- Concrete Bangladesh country-pack loader on M30's fix.country.pack interface

CD items: CD-M65-01, CD-M65-02, CD-M65-03 per tooling/cd-register.yaml.
    """,
    "version": "19.0.1.1.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "website": "https://1000fix.com",
    "category": "Platform/Administration",
    "depends": [
        "base",
        "mail",
        "operating_unit",
        "account",
        "cd_entity_config",
        "cd_gl_ext",
    ],
    "data": [
        "security/fix_isolation_rules.xml",
        "security/cd_multi_entity_security.xml",
        "security/ir.model.access.csv",
        "data/res_lang_bn_bd.xml",
        "data/ir_sequence_data.xml",
        "views/fix_consolidation_views.xml",
        "views/fix_intercompany_views.xml",
        "views/fix_localisation_views.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
    # --- 1000FiX mandatory keys (AR-007 section 3.2, FF-16 validated) --------
    "x_cd_id": "CD-M65-03",
    "x_module_id": "M65",
    "x_wave": "W9",
    "x_owner": "Platform",
    "x_category": "K_Platform_and_Technology",
    "x_tier": "T12",
}
