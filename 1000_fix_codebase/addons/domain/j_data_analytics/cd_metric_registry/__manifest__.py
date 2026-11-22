# cd_metric_registry (P11).
{
    "name": "1000FiX Data Platform & Governance",
    "summary": "M62: Data Platform & Governance",
    "description": "CD-M62-01 (P11).",
    "version": "19.0.0.4.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Data Platform & Governance",
    "depends": [
        "base",
        "mail",
        "hr",
        "cd_entity_config",
        "cd_event_outbox",
        "cd_workflow_engine",
        "cd_service_order",
        "cd_warranty_claims",
        # M62 capture audit 2026-11-18: an erasure request (M33) is propagated
        # through the analytical layers (fix.data.erasure).
        "cd_party_master",
    ],
    "data": [
        "security/fix_isolation_rules.xml",
        "security/fix_data_governance_groups.xml",
        "security/ir.model.access.csv",
        "data/data_platform_sequences.xml",
        "data/fix_data_event_consumers.xml",
        "data/fix_data_governance_crons.xml",
        # A11 audit A3-F01/A3-F04: the five governed definitions used to be
        # hand-made rows on two estates and absent everywhere else; they are
        # product data now (loaded as DRAFT - publication stays a governance act).
        "data/metric_definitions.xml",
        "views/cd_metric_registry_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M62-01",
    "x_module_id": "M62",
    "x_wave": "W8",
    "x_owner": "Data Platform & Governance",
    "x_category": "Phase11",
    "x_tier": "T11",
}
