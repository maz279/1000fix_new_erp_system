# cd_partner — M40 (P10).
{
    "name": "1000FiX Partner, Channel & Franchise",
    "summary": "M40: Partner, Channel & Franchise (CD-M40-01)",
    "description": """
CD-M40-01 (P10) — Partner, Channel & Franchise.
""",
    "version": "19.0.0.3.1",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Partner, Channel & Franchise",
    "depends": [
        "base",
        "portal",
        "mail",
        "cd_entity_config",
        "cd_rbac_ext",
        "cd_party_master",
        "cd_contract_core",
        "cd_event_outbox",
        # A04 audit (2026-11-04): the rebate payout is a routed M63 approval.
        # cd_workflow_engine already loads before this module on fix_dev
        # (through cd_party_master).
        "cd_workflow_engine",
        # M40-comarketing (12 Nov 2026): co-marketing partners on fix.campaign
        # and the MDF's campaign key.
        "cd_campaign",
        # A04 ERP audit (20 Nov 2026) M40-F1/F2/F16: royalties, the franchise
        # fee and reseller draws are billed as M20 invoices; the reseller price
        # is M11's. Neither module's closure reaches cd_partner (no cycle).
        "cd_billing_engine",
        "cd_rate_card",
    ],
    "data": [
        "security/cd_partner_groups.xml",
        "security/fix_isolation_rules.xml",
        "security/fix_partner_security.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/ir_cron.xml",
        # A03 audit W1: party.merged consumer (re-points are logged).
        "data/fix_party_merge_consumers.xml",
        # A04 ERP audit (20 Nov 2026): escalation / payout consumers, jobs
        "data/fix_partner_a04erp_data.xml",
        "security/fix_partner_a04erp_rules.xml",
        "views/cd_partner_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M40-01",
    "x_module_id": "M40",
    "x_wave": "W7",
    "x_owner": "Partner, Channel & Franchise",
    "x_category": "Phase10",
    "x_tier": "T10",
}
