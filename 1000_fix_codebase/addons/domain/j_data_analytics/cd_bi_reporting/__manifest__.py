# cd_bi_reporting — M25: Business Intelligence (A11).
# The module's own backend: the Power BI sync configuration and the
# aggregate snapshot engine that stamps BI data freshness. Executive KPIs
# are computed live by cd_p03_portal/controllers/a11/m25.py over the real
# service-order / estimate / AR-invoice tables.
{
    "name": "1000FiX Business Intelligence",
    "summary": "M25: Business Intelligence — exec dashboards, report library, sync config",
    "description": "CD-M25-01 (A11). Power BI sync configuration with an honest"
    " fail-closed external transport (operator credentials), the internal"
    " aggregate snapshot engine backing the BI Data Freshness KPI, the G8"
    " dashboard certification lifecycle (author != steward, through M63),"
    " the entitlement-re-checking distribution worker and the append-only"
    " export log (BRU-BID-11).",
    "version": "19.0.0.4.1",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Data Platform & Governance",
    "depends": [
        "base",
        "cd_entity_config",
        "cd_service_order",
        "cd_billing_engine",
        "cd_workflow_engine",
        "mail",
    ],
    "data": [
        "security/fix_isolation_rules.xml",
        "security/bi_security.xml",
        "security/ir.model.access.csv",
        "security/bi_capture_rules.xml",
        "data/bi_crons.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M25-01",
    "x_module_id": "M25",
    "x_wave": "W11",
    "x_owner": "Insights & Intelligence",
    "x_category": "A11_Insights_and_Intelligence",
    "x_tier": "T2",
}
