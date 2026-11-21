# cd_storefront_finance — the storefront order's hand-off to the books (M38 ->
# M20 AR, M51 VAT register, M19 GL, M15 stock). E2E3 flow 4 (12 Nov 2026).
{
    "name": "1000FiX Storefront Finance Bridge",
    "summary": "Storefront orders post to the books: an M20 invoice with its Mushak 6.3 and GL, "
    "the receipt applied, stock out on dispatch; returns restock and are refunded by an M20 "
    "credit note",
    "description": """
E2E3 flow 4 (12 Nov 2026, E3-08): a paid, delivered and refunded storefront
order produced no invoice, no Mushak 6.3, no revenue, no output VAT, no
stock-out and no restock; its M20 receipt sat unapplied as a customer credit,
and the refund's native out_refund debited revenue never credited and wrote a
6.7 with no 6.3, outside the M20 sub-ledger.

This bridge closes the hand-off through the estate's own engines:

- at the tax point (payment confirmed; dispatch for cash on delivery) an M20
  fix.ar.invoice is raised and issued through the billing engine's source API
  (_fix_ar_invoice_from_source): number, Mushak 6.3, GL through M19. Its lines
  are the order's, at the order's VAT-inclusive prices, split by M51
- the M20 receipt that proved the payment is applied to the invoice; a
  gateway-proved payment is captured as an M20 receipt on the channel clearing
- cash on delivery (G2): on the verified delivery the courier's cash is an M20
  cod receipt (Dr COD clearing / Cr AR) applied to the invoice, which M50's
  rider COD settlement clears against cash or bank; a branch pickup is a cash
  receipt. An unresolved clearing account leaves the order pending
- on dispatch each part leaves the M15 ledger and books its valuation
  suspense row
- a return restocks when it is received and inspected (quarantine unless
  grade A); the approved refund is an M20 credit note against the invoice
  (6.7, GL mirror, M50 refund instruction), and issuing it completes the
  return. A cancelled paid order is credited the same way
- storefront revenue: cd_storefront_finance.account_code.revenue, defaulting
  to the billing engine's revenue role. An account or a store that does not
  resolve never blocks the storefront: the order is left pending with the
  reason, and a retry (button or hourly job) posts it once; nothing posts twice

A separate module on purpose (the counter-sale bridge's lesson): cd_storefront
keeps its dependencies, and a server without the bridge never loads it.
""",
    "version": "19.0.0.1.1",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "E-Commerce & Digital Storefront",
    "depends": [
        "cd_storefront",
        "cd_billing_engine",
        "cd_inventory",
        "cd_tax_engine_bd",
        "cd_gl_ext",
        # A04 ERP M38-F2: the order_cancelled consumer row (fix.event.consumer)
        "cd_event_outbox",
    ],
    "data": [
        "data/fix_storefront_posting_cron.xml",
        "data/fix_storefront_consumers.xml",
        "views/fix_storefront_finance_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "x_module_id": "M38",
    "x_wave": "W7",
    "x_owner": "E-Commerce & Digital Storefront",
    "x_category": "Phase10",
    "x_tier": "T10",
}
