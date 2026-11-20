# cd_marketplace — M12 (P10).
{
    "name": "1000FiX Marketplace & Seller Ecosystem",
    "summary": "M12: Marketplace & Seller Ecosystem (CD-M12-01)",
    "description": """
CD-M12-01 (P10) — Marketplace & Seller Ecosystem.
""",
    "version": "19.0.0.4.1",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Marketplace & Seller Ecosystem",
    "depends": [
        "base",
        "portal",
        "mail",
        "cd_entity_config",
        "cd_rbac_ext",
        "cd_party_master",
        "cd_service_order",
        "cd_catalogue",
        "cd_tradein",
        "cd_event_outbox",
        # A04 C4/C9: routed seller CFO, listing and dispute decisions
        # (fix.approvable.mixin, M63). Already loaded before this module
        # (cd_service_order depends on it).
        "cd_workflow_engine",
        # A04 ERP audit (20 Nov 2026) M12-F1/F3: the customer's money is an M20
        # receipt, refunded by an M20 refund (cd_billing_engine).
        "cd_billing_engine",
    ],
    "data": [
        "security/cd_marketplace_groups.xml",
        "security/fix_isolation_rules.xml",
        "security/fix_marketplace_security.xml",
        "security/ir.model.access.csv",
        "data/ir_config_parameter_data.xml",
        "data/ir_cron.xml",
        "data/ir_sequence_data.xml",
        "data/fix_marketplace_consumers.xml",
        "views/cd_marketplace_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M12-01",
    "x_module_id": "M12",
    "x_wave": "W7",
    "x_owner": "Marketplace & Seller Ecosystem",
    "x_category": "Phase10",
    "x_tier": "T10",
}
