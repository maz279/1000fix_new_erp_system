# cd_data_case — M06 (P09).
{
    "name": "1000FiX Data Services & Secure Data Handling",
    "summary": "M06: Data Services & Secure Data Handling (CD-M06-01)",
    "description": """
CD-M06-01 (P09) — Data Services & Secure Data Handling.

Built on the existing estate (the layered model: compose, never
duplicate). AS-02 chatter + AS-03 company/OU on every transactional
model; AS-10 Monetary on every money field; events registered (AS-08).
""",
    "version": "19.0.2.0.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Data Services & Secure Data Handling",
    "depends": [
        "base",
        "mail",
        "cd_entity_config",
        "cd_party_master",
        "cd_device_registry",
        "cd_event_outbox",
    ],
    "data": [
        "security/fix_isolation_rules.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/cd_data_case_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M06-01",
    "x_module_id": "M06",
    "x_wave": "W6",
    "x_owner": "Data Services & Secure Data Handling",
    "x_category": "Phase9",
    "x_tier": "T9",
}
