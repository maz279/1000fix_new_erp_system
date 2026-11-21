{
    "name": "1000FiX Billing Engine (AR)",
    "summary": "M20 core: auto-invoice from closed jobs (NFR-040), atomic Mushak posting, dunning, credit notes (CD-M20-01)",
    "description": """
CD-M20-01: the M20 accounts-receivable core.

- fix.ar.invoice (+line) — auto-invoicing from closed service orders; the
  invoice, lines, Mushak register row and invoice.created event commit in
  ONE transaction (P06-M02-T08); idempotent on source (one invoice per job)
- Determination is a SYNCHRONOUS call into M51 (tax_logic); nothing calls
  back (AR-006 section 4.1 pair 7); receipts arrive by consuming M50 events
  — M20 never calls M50 synchronously (pair 6)
- fix.dunning — ageing buckets + the NT-006 ladder steps
- fix.credit.note — never self-approved: <= BDT 10,000 a second Accountant,
  above it the Accounting Administrator through M63 (05-04 section 7, A08 S3)
- fix.ar.writeoff — write-offs on the same ladder, against the IFRS 9
  allowance first (A08 M20-6)
- fix.vds.certificate.received — Mushak 6.6 received from VAT withholding
  customers: settles the VDS part of the receivable and feeds the 9.1 claim
- fix.tds.certificate.received — income tax deducted at source by
  customers (ITA 2023 s.89/s.90): settles the TDS part of the receivable to
  the advance income tax (AIT) account
- Events: invoice.created, invoice.paid, credit_note.issued,
  vds_certificate.settled (AS-08)
""",
    "version": "19.0.2.7.3",
    "license": "LGPL-3",
    "author": "1000FiX Services Ltd",
    "category": "Finance/Receivables",
    "depends": [
        "base",
        "mail",
        "account",
        "product",
        "cd_entity_config",
        "cd_event_outbox",
        "cd_tax_engine_bd",
        "cd_service_order",
        "cd_gl_ext",
        # A04 report §6 C7: the warranty_claim.decided consumer needs the
        # claim master (brand code, approved amount). No cycle: the warranty
        # module's closure does not reach this one.
        "cd_warranty_claims",
        # A04 report C10: the contract billing walker needs the contract
        # master (billing schedule, billed-through service) and the period
        # model lives there. No cycle: the contract module's closure (12
        # modules) does not reach this one.
        "cd_contract_core",
        # A08 S3 / P1-1: credit notes and write-offs route through M63 (DOFA)
        "cd_workflow_engine",
        # NOT cd_cash_position: the A08 cheque.bounced AR re-open extends
        # fix.ar.receipt from cd_cash_position (models/fix_ar_cheque_bounce.py
        # there) — a dependency from here onto cash closed the module cycle
        # billing -> cash -> storefront -> billing, and Odoo's loop detector
        # skipped every module in it.
    ],
    "data": [
        "data/fix_ar_aging_cron.xml",
        "security/fix_isolation_rules.xml",
        "security/ir.model.access.csv",
        "data/ar_impairment_sequences.xml",
        "security/fix_vds_rules.xml",
        "security/fix_tds_rules.xml",
        "data/ir_sequence_data.xml",
        "data/fix_ar_cron.xml",
        "data/fix_a08_ar_data.xml",
        # A03 audit W1: party.merged consumer (re-points are logged).
        "data/fix_party_merge_consumers.xml",
        # A04 report §6 C7: warranty_claim.decided -> draft M20 OEM invoice.
        "data/fix_a04_consumers.xml",
        # A02 ERP pass 2 X5-05 (D24): warranty_claim.written_off -> AR write-off.
        "data/fix_a02r2_claim_writeoff_consumer.xml",
        # A04 report C10: the contract billing walker (switch:
        # cd_billing_engine.contract_auto_billing).
        "data/fix_a04_contract_cron.xml",
        # A04 ERP audit (20 Nov 2026, B2): termination / top-up money legs and
        # the contract service-credit job.
        "data/fix_a04_contract_money.xml",
        "views/fix_billing_engine_views.xml",
        "views/fix_ar_engine_views.xml",
        "views/fix_vds_certificate_views.xml",
        "views/fix_tds_certificate_views.xml",
        # Quote-to-cash P1 (12 Nov 2026): the one customer payment-method
        # list and the Bangladesh payment-term templates.
        "data/fix_payment_method_data.xml",
        # Commercial document standard (17 Nov 2026): the shared walk-in party.
        "data/fix_walk_in_partner.xml",
        "views/fix_payment_method_views.xml",
        # M20 second capture pass (19 Nov 2026): sequences and the daily
        # promise / plan / unbilled / collection-case jobs.
        "data/fix_ar_capture_data.xml",
    ],
    "installable": True,
    "application": False,
    "x_cd_id": "CD-M20-02",
    "x_module_id": "M20",
    "x_wave": "W3",
    "x_owner": "Commercial & Finance",
    "x_category": "G_Finance_and_Treasury",
    "x_tier": "T5",
}
