{
    "name": "1000FiX Privilege Programme, Loyalty Points & Vouchers",
    "summary": "M10 privilege programme, tier management, points ledger, vouchers & campaign hooks (CD-M10-01)",
    "description": """
CD-M10-01 (P05-M08-T01..T03):

- fix.loyalty.program — the privilege programme configuration, points earning rates,
  currency value, and expiration rules
- fix.loyalty.tier — membership tier definitions (Bronze, Silver, Gold, Platinum) with
  thresholds, bonus multipliers, and labour/part discount benefits
- fix.loyalty.account — customer loyalty account tracking balances and tier progression
- fix.loyalty.ledger — append-only points transaction ledger (earned, redeemed, adjusted, expired)
- fix.loyalty.voucher — privilege vouchers with single-use codes, discounts, and expiry
- fix.loyalty.campaign — campaign hooks integrating with cd_campaign for promo codes and bonus points
- STUB-M10-M11-001 — cross-wave redemption stub with registered expiry at R04-M02-T08
""",
    "version": "19.0.1.1.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Customer/Loyalty",
    "depends": [
        "base",
        "mail",
        "operating_unit",
        "cd_entity_config",
        "cd_party_master",
        "cd_service_order",
        "cd_event_outbox",
        "cd_campaign",
        "cd_billing_engine",
        "cd_contact_centre",
        "cd_workflow_engine",
    ],
    "data": [
        "data/fix_loyalty_gap_cron.xml",
        "security/fix_isolation_rules.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "data/fix_loyalty_cron.xml",
        "data/fix_loyalty_event_consumers.xml",
        # A03 audit W1: a merge reversal undoes the loyalty transfer.
        "data/fix_loyalty_merge_reversal.xml",
        # M10 capture pass 2: membership, wallet, batches, referral events, liability runs
        "data/fix_loyalty_capture_data.xml",
        # A02 ERP pass 2 X5-09: credit notes / cancellations take earned points back
        "data/fix_loyalty_reversal_consumers.xml",
        "views/fix_loyalty_views.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M10-01",
    "x_module_id": "M10",
    "x_wave": "W2",
    "x_owner": "Customer Engagement",
    "x_category": "B_Customer_Engagement_and_Experience",
    "x_tier": "T6",
}
