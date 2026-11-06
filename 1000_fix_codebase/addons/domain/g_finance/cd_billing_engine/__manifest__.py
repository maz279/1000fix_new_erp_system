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
- Events: invoice.created, invoice.paid, credit_note.issued,
  vds_certificate.settled (AS-08)
""",
    "version": "19.0.2.2.0",
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
        # A08 S3 / P1-1: credit notes and write-offs route through M63 (DOFA)
        "cd_workflow_engine",
        # A08 B1 -> B4: a returned customer cheque (fix.cheque) re-opens its AR
        "cd_cash_position",
    ],
    "data": [
        "security/fix_isolation_rules.xml",
        "security/ir.model.access.csv",
        "data/ar_impairment_sequences.xml",
        "security/fix_vds_rules.xml",
        "data/ir_sequence_data.xml",
        "data/fix_ar_cron.xml",
        "data/fix_a08_ar_data.xml",
        # A03 audit W1: party.merged consumer (re-points are logged).
        "data/fix_party_merge_consumers.xml",
        "views/fix_billing_engine_views.xml",
        "views/fix_ar_engine_views.xml",
        "views/fix_vds_certificate_views.xml",
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
