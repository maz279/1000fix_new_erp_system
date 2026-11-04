# cd_ml_services — M26: AI/ML Services (A11).
# The honest model registry for the estate's real inference engines (the
# M02 dispatch-suggestion engine, M48 predictive maintenance, the fault-code
# classifier, trade-in valuation, the M25 BI aggregator) plus the inference
# run log. Every catalog entry names its owning module and implementation
# honestly; nothing claims a neural net that does not exist.
{
    "name": "1000FiX AI/ML Services",
    "summary": "M26: AI/ML Services — model registry, real inference runs, engine wiring",
    "description": "CD-M26-01 (A11). Catalog of the estate's real, explainable"
    " inference engines with a measured inference-run log: dispatch scoring,"
    " predictive maintenance, fault-code classification, trade-in valuation,"
    " BI aggregation. Demand forecasting stays honestly 'planned' until the"
    " M15 consumption-history seam exists.",
    "version": "19.0.0.2.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Data Platform & Governance",
    "depends": [
        "base",
        "mail",
        "cd_entity_config",
        "cd_field_service",
        "cd_service_order",
        "cd_stream_registry",
        "cd_demand_plan",
        "cd_tradein",
        "cd_bi_reporting",
        "cd_workflow_engine",
    ],
    "data": [
        "security/ml_security.xml",
        "data/fix_ml_lead_scoring_data.xml",
        "security/fix_isolation_rules.xml",
        "security/ir.model.access.csv",
        "data/ml_model_catalog.xml",
        "data/ml_versions.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M26-01",
    "x_module_id": "M26",
    "x_wave": "W11",
    "x_owner": "Insights & Intelligence",
    "x_category": "A11_Insights_and_Intelligence",
    "x_tier": "T2",
}
