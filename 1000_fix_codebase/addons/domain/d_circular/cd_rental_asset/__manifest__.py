# cd_rental_asset — M13 (P09).
{
    "name": "1000FiX Rental & Equipment-as-a-Service",
    "summary": "M13: Rental & Equipment-as-a-Service (CD-M13-01)",
    "description": """
CD-M13-01 (P09) — Rental & Equipment-as-a-Service.

Built on the existing estate (the layered model: compose, never
duplicate). AS-02 chatter + AS-03 company/OU on every transactional
model; AS-10 Monetary on every money field; events registered (AS-08).
""",
    "version": "19.0.0.2.2",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Rental & Equipment-as-a-Service",
    "depends": [
        "base",
        "mail",
        "account",
        "cd_entity_config",
        "cd_catalogue",
        "cd_party_master",
        "cd_device_registry",
        "cd_contract_core",
        "cd_fixed_asset_ext",
        "cd_consignment",
        "cd_subscription",
        "cd_service_order",
        "cd_event_outbox",
        # money path: deposit GL (M19), invoicing (M20), VAT (M51), refunds (M50)
        "cd_gl_ext",
        "cd_billing_engine",
        "cd_tax_engine_bd",
        "cd_cash_position",
        # customer-data wipe evidence on turnaround (M06)
        "cd_data_case",
        "cd_workflow_engine",
        # condition photographs are filed as M24 documents (capture pass 2)
        "cd_document_core",
    ],
    "data": [
        "security/rental_groups.xml",
        "security/fix_isolation_rules.xml",
        "security/ir.model.access.csv",
        "security/fix_rental_charge_rules.xml",
        "security/fix_rental_a05_rules.xml",
        "data/ir_sequence.xml",
        "data/ir_cron.xml",
        "data/rental_event_consumers.xml",
        "views/cd_rental_asset_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M13-01",
    "x_module_id": "M13",
    "x_wave": "W6",
    "x_owner": "Rental & Equipment-as-a-Service",
    "x_category": "Phase9",
    "x_tier": "T9",
}
