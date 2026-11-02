{
    "name": "1000FiX Pricing (Rate Cards)",
    "summary": "M11 data core: tier + contract rate cards on the catalogue kernel; computation in services/pricing-engine (CD-M11-02)",
    "description": """
CD-M11-02: price books and rate cards.

- fix.rate.card — product x tier rates with the CONTRACT lane (min_tier 99 +
  contract_no); validity windows; projects to the pricing engine's
  RateCardLine (data here, execution in the L5 service — BRU-MDM-15 shape)
- Resolution order enforced by the engine: contract > tier > catalogue
- Discount governance lives in cd_quotation (the quotation lifecycle's control)
- Dynamic pricing (CD-M11-05/06) is explicitly W7 (roadmap P06-M06-T08)
""",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Sales/Pricing",
    "depends": [
        "base",
        "mail",
        "cd_entity_config",
        "cd_event_outbox",
        # fix.catalogue.item (cd_catalogue) is referenced by this module's models
        # (FF-46).
        "cd_catalogue",
    ],
    "data": [
        "security/fix_isolation_rules.xml",
        "security/ir.model.access.csv",
        "views/fix_rate_card_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M11-02",
    "x_module_id": "M11",
    "x_wave": "W3",
    "x_owner": "Commercial & Finance",
    "x_category": "C_Commercial_Pricing_and_Revenue",
    "x_tier": "T4",
}
