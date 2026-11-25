{
    "name": "1000FiX Subscription & Revenue",
    "summary": "M39 subscriptions + M53 W4 revenue slice: consolidated B2B invoicing, cycle charges, straight-line recognition (CD-M39-01)",
    "description": """
CD-M39-01 + M53's W4 slice (P07-M03):

- fix.subscription — recurring subscriptions with cycle charges (AUT-025)
  and CONSOLIDATED B2B invoicing (T02: one invoice, many jobs, many sites —
  a corporate client with 400 devices does not want 400 invoices);
  subscription dunning rides M20's collections ladder (T03)
- fix.revenue.schedule — the W4 revenue-recognition slice (T04):
  straight-line over the term; fee revenue recognized over the period,
  never at the point of sale; cumulative idempotent drawdown
- Commission CALCULATION consumes services/settlement-engine (T06/T07,
  pair 12: earning is an M12 event — M12 must not call M53)
- A08 M53 (IFRS 15): fix.subscription.charge (one invoice per cycle,
  billed to the contract liability), fix.performance.obligation (SSP
  allocation of the transaction price, schedule per obligation) and
  fix.revenue.recognition.line (each recognition posted Dr contract
  liability / Cr revenue)
- Events: subscription.charged/cancelled, revenue.recognized (AS-08)
""",
    "version": "19.0.1.4.3",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Sales/Subscriptions",
    "depends": [
        "base",
        "mail",
        "cd_entity_config",
        "cd_event_outbox",
        "cd_party_master",
        "cd_contract_core",
        "cd_billing_engine",
        "cd_tax_engine_bd",
        "cd_gl_ext",
        # A08 BRU-REV-01: manual schedules route to the CFO through M63
        "cd_workflow_engine",
    ],
    "data": [
        "security/cd_subscription_groups.xml",
        "security/fix_isolation_rules.xml",
        "security/ir.model.access.csv",
        "security/fix_revenue_rules.xml",
        "data/ir_cron.xml",
        "data/fix_revenue_cron.xml",
        "data/fix_subscription_quote_consumer.xml",
        # M53 capture audit: SSP and contract modification
        "data/fix_revenue_capture_data.xml",
        # M39 capture audit: lifecycle requests that take effect on their date
        "data/fix_m39_capture_cron.xml",
        # A02 ERP audit M05-F4: an MSP device uplift becomes a price change
        "data/fix_msp_uplift_consumer.xml",
        # A04 ERP M39-F4: autopay success -> M20 receipt
        "data/fix_autopay_receipt_consumer.xml",
        # A04 ERP round 2 M39-F17/F11: usage, service gate, contract activation
        "data/fix_a04_r2_consumers.xml",
        "views/fix_subscription_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M39-01",
    "x_module_id": "M39",
    "x_wave": "W4",
    "x_owner": "Commercial & Finance",
    "x_category": "C_Commercial_Pricing_and_Revenue",
    "x_tier": "T6",
}
