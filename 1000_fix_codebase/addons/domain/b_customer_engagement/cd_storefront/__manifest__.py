# cd_storefront — M38 (P10).
{
    "name": "1000FiX E-Commerce & Digital Storefront",
    "summary": "M38: E-Commerce & Digital Storefront (CD-M38-02)",
    "description": """
CD-M38-02 (P10) — E-Commerce & Digital Storefront.
""",
    "version": "19.0.0.2.1",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "E-Commerce & Digital Storefront",
    "depends": [
        "base",
        "portal",
        "mail",
        "cd_entity_config",
        "cd_catalogue",
        "cd_party_master",
        "cd_event_outbox",
        "cd_consignment",
        # A04 audit (2026-11-04): payment is confirmed against an M20 receipt
        # (cd_billing_engine), graded refurb stock is reserved and sold (M15
        # cd_inventory), and the refund is a routed M63 approval
        # (cd_workflow_engine). All three load before this module on fix_dev.
        "cd_billing_engine",
        "cd_inventory",
        "cd_workflow_engine",
    ],
    "data": [
        "security/cd_storefront_groups.xml",
        "security/fix_isolation_rules.xml",
        "security/fix_storefront_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/ir_cron.xml",
        "views/cd_storefront_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M38-02",
    "x_module_id": "M38",
    "x_wave": "W7",
    "x_owner": "E-Commerce & Digital Storefront",
    "x_category": "Phase10",
    "x_tier": "T10",
}
