# cd_front_desk_finance — the counter sale's hand-off to the books (M04 ->
# M51 VAT register, M19 GL, M15 stock). E2E2 flow 2 (11 Nov 2026).
{
    "name": "1000FiX Front Desk Finance Bridge",
    "summary": "Counter sales post to the books: Mushak 6.3 from the VAT register, GL through "
    "M19, stock out through the M15 ledger; refunds reverse all three",
    "description": """
E2E2 flow 2 (11 Nov 2026): three counter sales produced no GL entry, no stock
movement and no Mushak register row, and the M50 cash deposit then credited
the drawer cash account for takings that had never been debited to it.

This bridge closes the hand-off without changing cd_front_desk's
dependencies (it depends on none of billing, GL, tax or inventory):

- confirm: the Mushak 6.3 is issued through the VAT register service with the
  billing engine's statutory numbering and M51's determination (the AR
  invoice path); the sale is posted through M19 (Dr drawer cash / MFS or
  card clearing, Cr parts or labour revenue, Cr VAT output); a part leaves
  the M15 ledger and writes its valuation suspense row
- refund: a Mushak 6.7 against the 6.3, the mirror GL entry and the part back
  into stock (quarantine when returned defective)
- accounts come from system parameters (cd_front_desk_finance.account_code.*)
  defaulting to the accounts the estate already uses; an account that does
  not resolve never blocks the counter: the sale is left pending posting and
  a retry (button or hourly job) posts it once configured; nothing posts twice

A separate module on purpose (the cd_vehicle_dispatch / bridge lesson): the
front desk keeps its dependencies, and a server that has not installed the
bridge never loads it.
""",
    "version": "19.0.0.1.0",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Service Delivery/Front Desk",
    "depends": [
        "cd_front_desk",
        "cd_gl_ext",
        "cd_tax_engine_bd",
        "cd_billing_engine",
        "cd_inventory",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/fix_isolation_rules.xml",
        "data/fix_counter_basket_data.xml",
        "views/fix_counter_basket_views.xml",
        "data/fix_counter_posting_cron.xml",
        "views/fix_counter_sale_finance_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "x_module_id": "M04",
    "x_wave": "W1",
    "x_owner": "Service Delivery",
    "x_category": "A_Service_Delivery_and_Operations",
    "x_tier": "T3",
}
