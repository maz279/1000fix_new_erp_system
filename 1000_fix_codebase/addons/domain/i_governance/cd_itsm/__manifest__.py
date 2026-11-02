# cd_itsm — M66 (P09).
{
    "name": "1000FiX Internal IT Service Management",
    "summary": "M66: Internal IT Service Management (CD-M66-01)",
    "description": """
CD-M66-01 (P09) — Internal IT Service Management.

Built on the existing estate (the layered model: compose, never
duplicate). AS-02 chatter + AS-03 company/OU on every transactional
model; AS-10 Monetary on every money field; events registered (AS-08).
""",
    "version": "19.0.0.1.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Internal IT Service Management",
    "depends": [
        "base",
        "mail",
        "cd_entity_config",
        "cd_msp_contract",
        "cd_event_outbox",
        # fix.project (cd_ppm) is referenced by this module's models; without the
        # dependency the relation can load against a missing model (FF-46).
        "cd_ppm",
    ],
    "data": [
        "security/fix_isolation_rules.xml",
        "security/ir.model.access.csv",
        "data/itsm_catalogue_sequences.xml",
        "data/integration_sequences.xml",
        "data/itsm_ops_sequences.xml",
        "views/cd_itsm_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M66-01",
    "x_module_id": "M66",
    "x_wave": "W6",
    "x_owner": "Internal IT Service Management",
    "x_category": "Phase9",
    "x_tier": "T9",
}
