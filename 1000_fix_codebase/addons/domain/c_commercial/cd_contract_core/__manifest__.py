{
    "name": "1000FiX Contract Lifecycle",
    "summary": "M08: all contract families (AMC/RAMC/managed/rental/marketplace), entitlement drawdown, contract SLAs, renewal, PM scheduler (CD-M08-01)",
    "description": """
CD-M08-01..04: the contract engine.

- fix.contract — all five product families on one engine; e-signature
  activation through M24's kernel envelope (T07); escalation renewal (T05);
  AUT-015 expiring ladder; fix.contract.cost OWNERSHIP RESOLVED HERE
  (AR-008 section 2.2 ruling: M53/M54 consume via events, T08)
- fix.contract.entitlement — what the contract buys and the drawdown (T03);
  `entitlement_active()` is the API M01's AMC order-category gate consumes
  (BRU-SRM-03); consumption is never negative and publishes
  entitlement.consumed
- contract SLAs reference the SAME fix.sla.policy model as M01 (T04: one
  SLA concept, two scopes — not two implementations)
- fix.contract.pm.visit — the preventive schedule generated at activation
  (T06), feeding dispatch via service-order creation
- Events: contract.activated, contract.renewed, contract.expiring,
  entitlement.consumed (AS-08)
""",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Sales/Contracts",
    "depends": ["base", "mail", "product", "cd_entity_config", "cd_event_outbox",
                 "cd_party_master", "cd_device_registry", "cd_service_order",
                 "cd_esignature"],
    "data": ["security/ir.model.access.csv", "views/fix_contract_views.xml"],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M08-01",
    "x_module_id": "M08",
    "x_wave": "W4",
    "x_owner": "Commercial & Finance",
    "x_category": "C_Commercial_Pricing_and_Revenue",
    "x_tier": "T6",
}
