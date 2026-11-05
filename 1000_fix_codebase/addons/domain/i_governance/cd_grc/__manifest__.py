# cd_grc — M60 (P09).
{
    "name": "1000FiX Governance, Risk & Compliance",
    "summary": "M60: Governance, Risk & Compliance (CD-M60-01)",
    "description": """
CD-M60-01 (P09) — Governance, Risk & Compliance.

Built on the existing estate (the layered model: compose, never
duplicate). AS-02 chatter + AS-03 company/OU on every transactional
model; AS-10 Monetary on every money field; events registered (AS-08).
""",
    "version": "19.0.0.1.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Governance, Risk & Compliance",
    "depends": [
        "base",
        "mail",
        "hr",
        "cd_entity_config",
        "cd_event_outbox",
        "cd_document_core",
        "cd_rbac_ext",
        # A10 P1-5: above-appetite residual acceptance routes through the M63
        # approval engine (fix.approvable.mixin / fix.approval.matrix), and a
        # failed control test raises an NCR + CAPA in the QMS journey.
        "cd_workflow_engine",
        "cd_qms_process",
    ],
    "data": [
        "security/fix_isolation_rules.xml",
        "security/fix_grc_groups.xml",
        "security/fix_grc_whistle_rules.xml",
        "security/ir.model.access.csv",
        "data/grc_ops_sequences.xml",
        "data/fix_grc_handoff_consumers.xml",
        "data/fix_grc_event_consumers.xml",
        "data/fix_grc_crons.xml",
        "views/cd_grc_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M60-01",
    "x_module_id": "M60",
    "x_wave": "W6",
    "x_owner": "Governance, Risk & Compliance",
    "x_category": "Phase9",
    "x_tier": "T9",
}
