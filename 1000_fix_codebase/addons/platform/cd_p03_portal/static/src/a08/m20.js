/** @odoo-module **/
/* A08 · Finance & Treasury — M20 AR, Invoicing & Collections.
 * One file per A08 module (merged into P03_MODULES and the screen maps by
 * p03_modules_meta.js): the registry entry, the in-workspace data screens,
 * built-in report routes, data-entry form chips and the "+ New" surface. */

export const MODULE = {
  area: 'A08', code: 'M20', en: 'AR, Invoicing & Collections', title: 'M20 · AR, Invoicing & Collections',
  bn: 'প্রাপ্য ও ইনভয়েসিং', icon: '🧾',
  desc: 'Billable events from every module, Mushak 6.3 invoices, bKash/Nagad/card receipts, dunning, ageing.',
  kpis: [
    { l: 'Invoices MTD', m: 'ar_invoices_mtd' },
    { l: 'Overdue > 60d', m: 'overdue_gt_60d', prefix: '৳ ' },
    { l: 'DSO', m: 'dso', suffix: ' d' },
    { l: 'Auto-Gen %', m: 'auto_generated_pct', suffix: '%' },
    { l: 'Within 1h %', m: 'within_1h_pct', suffix: '%' },
    { l: 'Credit Notes', m: 'credit_notes_total' },
    { l: 'VDS to Claim', m: 'vds_unclaimed', prefix: '৳ ' }
  ],
  groups: [
    { en: 'Provisioning', screens: [
      { id: 'M20-ecl', en: 'IFRS 9 Impairment (ECL)', bn: 'আইএফআরএস ৯ ইসিএল', t: 'g' },
      { id: 'M20-ecl-rates', en: 'ECL Loss Rates (approved)', bn: 'ইসিএল ক্ষতির হার', t: 'g' },
      { id: 'M20-writeoffs', en: 'Write-offs', bn: 'অবলোপন', t: 'g' },
    ]},
    { en: 'Record Coverage', screens: [
      { id: 'M20-ar-dispute', en: "Ar Dispute", bn: "Ar Dispute", t: 'g' },
      { id: 'M20-ar-consolidated-bill', en: "Ar Consolidated Bill", bn: "Ar Consolidated Bill", t: 'g' },
      { id: 'M20-dunning-register', en: 'Dunning Register', bn: 'দেনা আদায় রেজিস্টার', t: 'g' }
    ]},
    { en: 'Delivery & Statements', screens: [
      { id: 'M20-deliveries', en: 'Invoice Deliveries', bn: 'ইনভয়েস বিতরণ', t: 'g' },
      { id: 'M20-statement-register', en: 'Statements of Account', bn: 'হিসাব বিবরণী', t: 'g' }
    ]},
    { en: 'Collections', screens: [
      { id: 'M20-cases', en: 'Collections Worklist', bn: 'আদায় কাজের তালিকা', t: 'g' },
      { id: 'M20-promises', en: 'Promises to Pay', bn: 'পরিশোধের প্রতিশ্রুতি', t: 'g' },
      { id: 'M20-plans', en: 'Payment Plans', bn: 'কিস্তি পরিকল্পনা', t: 'g' },
      { id: 'M20-dunning-policies', en: 'Dunning Ladders', bn: 'তাগাদার ধাপ', t: 'g' }
    ]},
    { en: 'Invoicing', screens: [
      { id: 'M20-invoices', en: 'Customer Invoices', bn: 'গ্রাহক ইনভয়েস', t: 'g' },
      { id: 'M20-invoice', en: 'Invoice (Mushak 6.3)', bn: 'মুশক ৬.৩', t: 'f' },
      { id: 'M20-events', en: 'Billable Events', bn: 'বিলযোগ্য ঘটনা', t: 'g' },
      { id: 'M20-consolidated', en: 'Consolidated Corporate Invoices', bn: 'সমন্বিত ইনভয়েস', t: 'g' },
      { id: 'M20-brand', en: 'Brand Claim Invoices', bn: 'ব্র্যান্ড ইনভয়েস', t: 'g' }
    ]},
    { en: 'Receipts', screens: [
      { id: 'M20-receipts', en: 'Receipts (All Methods)', bn: 'রিসিট', t: 'g' },
      { id: 'M20-links', en: 'Payment Links', bn: 'পেমেন্ট লিংক', t: 'g' },
      { id: 'M20-allocation', en: 'Matching & Allocation', bn: 'মিলকরণ', t: 'c' },
      { id: 'M20-vds', en: 'Customer VDS Certificates (Mushak 6.6)', bn: 'গ্রাহকের উৎসে ভ্যাট কর্তন সনদ (মুশক ৬.৬)', t: 'g' },
      { id: 'M20-tds', en: 'Customer TDS / AIT Certificates', bn: 'গ্রাহকের উৎসে আয়কর কর্তন সনদ', t: 'g' },
      { id: 'M20-closeout', en: 'Invoice Settlement Close-out', bn: 'ইনভয়েস নিষ্পত্তি সমাপন', t: 'g' },
      { id: 'M20-unapplied', en: 'Unapplied Receipts', bn: 'অপ্রয়োগকৃত রসিদ', t: 'g' },
      { id: 'M20-deposits', en: 'Deposits & Retention', bn: 'জামানত ও রিটেনশন', t: 'g' }
    ]},
    { en: 'Credit Control', screens: [
      { id: 'M20-credit', en: 'Limits, Terms & Holds', bn: 'ক্রেডিট নিয়ন্ত্রণ', t: 'g' },
      { id: 'M20-dunning', en: 'Dunning Worklist', bn: 'দেনা আদায়', t: 'c' },
      { id: 'M20-disputes', en: 'Disputes', bn: 'বিরোধ', t: 'g' },
      { id: 'M20-refunds', en: 'Credit Notes & Refunds', bn: 'ক্রেডিট নোট', t: 'g' },
      { id: 'M20-notes-register', en: 'Credit-Note Register (approval)', bn: 'ক্রেডিট নোট রেজিস্টার', t: 'g' },
      { id: 'M20-oa-refunds', en: 'Refunds of On-Account Money', bn: 'অগ্রিম অর্থ ফেরত', t: 'g' }
    ]},
    { en: 'Analysis', screens: [
      { id: 'M20-aging', en: 'AR Ageing', bn: 'বয়স্ক প্রাপ্য', t: 'r' },
      { id: 'M20-leakage', en: 'Revenue-Leakage Detection', bn: 'রাজস্ব ক্ষয়', t: 'r' },
      { id: 'M20-unbilled', en: 'Unbilled Exceptions', bn: 'বিল না হওয়া কাজ', t: 'g' },
      { id: 'M20-statements', en: 'Customer Statements', bn: 'গ্রাহক স্টেটমেন্ট', t: 'r' },
      { id: 'M20-vds-register', en: 'VDS Claim Register (Mushak 9.1)', bn: 'উৎসে ভ্যাট কর্তন দাবি রেজিস্টার (মুশক ৯.১)', t: 'r' },
      { id: 'M20-gl-recon', en: 'AR Sub-ledger to GL Reconciliation', bn: 'প্রাপ্য ও সাধারণ খতিয়ান সমন্বয়', t: 'r' }
    ]}
  ],
  reports: ['AR Ageing by Segment', 'Dunning Effectiveness', 'Payment Method Mix', 'Invoice Accuracy', 'Brand Receivable Ageing', 'Collections Productivity', 'VDS Received Register', 'AR Sub-ledger to GL Reconciliation'],
  forms: ['Invoice Request', 'Proforma Invoice', 'Consolidated Bill', 'Invoice Delivery', 'Customer Statement', 'Receipt', 'Deposit / Retention', 'Credit Note', 'Refund', 'Payment Link', 'VDS Certificate', 'TDS Certificate', 'Credit Profile', 'Dispute', 'Dunning Policy', 'Promise to Pay', 'Payment Plan', 'Collection Case', 'Write-off', 'ECL Loss Rates', 'Unbilled Exception'],
  cross: ['Financial Accounting & GL', 'Treasury & Banking', 'Tax & Regulatory (BD)'],
  /* What each page captures (capture-button audits 2026-11-13 and 2026-11-19):
   *   1, 3  nothing typed - the queue is fed by closed jobs (FR-ARB-001) and
   *         the Mushak 6.3 is rendered at issue
   *   2  "+ New AR Invoice" (the manual-invoice exception, FR-ARB-010), a
   *      consolidated corporate bill (FR-ARB-008), M36's proforma (FR-ARB-007)
   *   4  "+ New Invoice Delivery" (FR-ARB-013/014) and statements (FR-ARB-017)
   *   5  receipt, payment link, deposit / retention (FR-ARB-028)
   *   6  the customer's Mushak 6.6 VDS certificate
   *   7  the customer credit profile - limit and terms (FR-ARB-030); its form
   *      is M33's, the customer master that also surfaces it
   *   8  a dispute (FR-ARB-036), promise to pay (035), payment plan (037),
   *      collection case (034) and the dunning ladder (032)
   *   9  credit note; refund of on-account money (FR-ARB-040)
   *   10 "+ New Unbilled Exception" for delivered work the daily
   *      reconciliation does not read (FR-ARB-043) */
  freg: { src: 99, sub: [
    ['1', 'Billable-Event Intake', 12, { model: 'fix.billable.event', cols: ['event_id', 'source_type', 'customer_id', 'first_seen_at', 'state', 'attempts', 'last_error', 'invoice_id'], screens: ['M20-events'], reports: ['Invoice Accuracy'], forms: [], create: false }],
    ['2', 'Invoice Assembly', 12, { model: 'fix.ar.invoice', cols: ['name', 'customer_id', 'invoice_date', 'total_payable', 'state'], screens: ['M20-invoices', 'M20-consolidated', 'M20-brand'], reports: ['Invoice Accuracy', 'Brand Receivable Ageing'], forms: ['Invoice Request', 'Proforma Invoice', 'Consolidated Bill'] }],
    ['3', 'Mushak 6.3 Rendering', 8, { model: 'fix.ar.invoice', cols: ['name', 'mushak_id', 'generated_at', 'vat_amount', 'total_payable'], screens: ['M20-invoice'], reports: [], forms: [], create: false }],
    ['4', 'Delivery Channels', 6, { model: 'fix.ar.invoice.delivery', cols: ['name', 'invoice_id', 'channel', 'recipient', 'status', 'retry_count'], screens: ['M20-deliveries', 'M20-statement-register', 'M20-statements', 'M20-ar-consolidated-bill'], reports: [], forms: ['Invoice Delivery', 'Customer Statement', 'Consolidated Bill'], create: 'M20-form-delivery' }],
    ['5', 'Receipt Capture (8 methods)', 14, { model: 'fix.ar.receipt', cols: ['name', 'customer_id', 'receipt_date', 'method', 'amount', 'state'], screens: ['M20-receipts', 'M20-links', 'M20-deposits'], reports: ['Payment Method Mix'], forms: ['Receipt', 'Payment Link', 'Deposit / Retention'] }],
    ['6', 'Matching & Allocation', 11, { model: 'fix.ar.receipt', cols: ['name', 'customer_id', 'amount', 'allocated_amount', 'unapplied_amount'], screens: ['M20-allocation', 'M20-unapplied', 'M20-closeout', 'M20-vds', 'M20-tds', 'M20-vds-register', 'M20-gl-recon'], reports: ['VDS Received Register', 'AR Sub-ledger to GL Reconciliation'], forms: ['VDS Certificate', 'TDS Certificate'], create: 'M20-form-vds' }],
    ['7', 'Credit Control', 9, { model: 'fix.credit.profile', cols: ['customer_id', 'credit_limit', 'exposure', 'over_limit', 'credit_hold'], screens: ['M20-credit', 'M20-aging', 'M20-ecl', 'M20-ecl-rates', 'M20-writeoffs'], reports: ['AR Ageing by Segment', 'Brand Receivable Ageing'], forms: ['Credit Profile', 'Write-off', 'ECL Loss Rates'], create: 'M33-form-credit' }],
    ['8', 'Dunning & Collections', 12, { model: 'fix.dunning', cols: ['invoice_id', 'overdue_amount', 'days_overdue', 'step', 'channel', 'suppressed'], screens: ['M20-dunning', 'M20-dunning-register', 'M20-cases', 'M20-promises', 'M20-plans', 'M20-dunning-policies', 'M20-disputes', 'M20-ar-dispute'], reports: ['Dunning Effectiveness', 'Collections Productivity'], forms: ['Dispute', 'Promise to Pay', 'Payment Plan', 'Collection Case', 'Dunning Policy'], create: 'M20-form-dispute' }],
    ['9', 'Credit Notes & Refunds', 8, { model: 'fix.credit.note', cols: ['invoice_id', 'amount', 'reason_code', 'state', 'issued_at'], screens: ['M20-refunds', 'M20-notes-register', 'M20-oa-refunds'], reports: [], forms: ['Credit Note', 'Refund'], create: 'M20-form-note' }],
    ['10', 'Leakage Detection', 7, { model: 'fix.ar.unbilled.exception', cols: ['name', 'source_module', 'source_ref', 'customer_id', 'estimated_value', 'age_days', 'escalated_to', 'state'], screens: ['M20-unbilled', 'M20-leakage'], reports: ['Invoice Accuracy'], forms: ['Unbilled Exception'], create: 'M20-form-unbilled' }]
  ] }
};

/* in-workspace data screens (checked before any stock Odoo view) */
export const SCREENS = {
  'M20-ecl': { kind: 'model_list', model: 'fix.ar.impairment', stateField: 'state',
    cols: ['name', 'as_of', 'total_exposure', 'total_provision', 'existing_provision', 'movement', 'state'],
    actions: [{ m: 'action_compute', l: 'Compute' }, { m: 'action_post', l: 'Post' }] },
  'M20-rpt-ecl': { kind: 'table_report', module: 'M20', report: 'ecl_provision', title: 'IFRS 9 ECL Provision', period: false },
  'M20-form-ecl': {
    kind: 'model_form',
    model: 'fix.ar.impairment',
    title: 'AR Impairment Run (IFRS 9)',
    back: 'M20-ecl',
    status: { field: 'state', labels: { draft: 'Draft', computed: 'Computed', posted: 'Posted' } },
    sections: [
      { title: 'Run', note: 'Compute ages every open invoice against its due date and applies the loss rates of the approved set in force at the as-of date; Post (an Accounting Administrator other than the preparer) writes only the movement against the provision already booked, read from the GL, through the M19 API.',
        fields: [
          { name: 'as_of', required: true, label: 'As Of' },
          { name: 'journal_id', required: true, label: 'Journal' },
          { name: 'expense_account_id', label: 'Impairment Expense Account' },
          { name: 'provision_account_id', label: 'Provision Account' },
          { name: 'rate_set_id', readonly: true, label: 'Approved Loss Rates (at Compute)' },
          { name: 'rate_current', readonly: true, label: 'Rate current (%)' },
          { name: 'rate_1_30', readonly: true, label: 'Rate 1-30 (%)' },
          { name: 'rate_31_60', readonly: true, label: 'Rate 31-60 (%)' },
          { name: 'rate_61_90', readonly: true, label: 'Rate 61-90 (%)' },
          { name: 'rate_90_plus', readonly: true, label: 'Rate 90+ (%)' },
          { name: 'state', readonly: true, label: 'State' },
          { name: 'existing_provision', readonly: true, label: 'Provision Already Booked (from GL)' },
          { name: 'computed_by_id', readonly: true, label: 'Computed By' },
          { name: 'posted_by_id', readonly: true, label: 'Reviewed & Posted By' }
        ] }
    ]
  },
  /* M20-5: the approved loss rates a run stamps at Compute. */
  'M20-ecl-rates': { kind: 'model_list', model: 'fix.ar.ecl.rate', stateField: 'state',
    cols: ['name', 'date_from', 'date_to', 'rate_current', 'rate_1_30', 'rate_31_60', 'rate_61_90', 'rate_90_plus', 'approved_by_id', 'state'],
    actions: [
      { m: 'action_approve', l: 'Approve (second Accounting Administrator)' },
      { m: 'action_retire', l: 'Retire', ask: 'Why these rates are retired', kwarg: 'reason' }
    ] },
  'M20-form-ecl-rate': {
    kind: 'model_form',
    model: 'fix.ar.ecl.rate',
    title: 'ECL Loss Rates',
    back: 'M20-ecl-rates',
    status: { field: 'state', labels: { draft: 'Draft', approved: 'Approved', retired: 'Retired' } },
    sections: [
      { title: 'Rate Set', note: 'The IFRS 9 simplified-approach loss rate per ageing bucket, from the company\'s own loss history. An Accounting Administrator other than the preparer approves it; a run with no approved set in force at its as-of date is refused.',
        fields: [
          { name: 'name', required: true, label: 'Rate Set' },
          { name: 'date_from', required: true, label: 'Effective From' },
          { name: 'date_to', label: 'Effective To' },
          { name: 'rate_current', required: true, label: 'Rate current (%)' },
          { name: 'rate_1_30', required: true, label: 'Rate 1-30 (%)' },
          { name: 'rate_31_60', required: true, label: 'Rate 31-60 (%)' },
          { name: 'rate_61_90', required: true, label: 'Rate 61-90 (%)' },
          { name: 'rate_90_plus', required: true, label: 'Rate 90+ (%)' },
          { name: 'basis_note', required: true, type: 'text', label: 'Basis (loss history or policy)' },
          { name: 'state', readonly: true, label: 'State' },
          { name: 'approved_by_id', readonly: true, label: 'Approved By' }
        ] }
    ]
  },
  /* M20-6 / S3: a write-off is requested here with its recovery history; a
   * second Accountant approves within the direct band, the M63 inbox above it. */
  'M20-writeoffs': { kind: 'model_list', model: 'fix.ar.writeoff', stateField: 'state',
    cols: ['name', 'invoice_id', 'customer_id', 'amount', 'reason', 'allowance_amount', 'expense_amount', 'requested_by_id', 'state'],
    actions: [
      { m: 'action_submit', l: 'Request Approval' },
      { m: 'action_approve', l: 'Approve (direct band)' },
      { m: 'action_reject', l: 'Reject', ask: 'Why the write-off is rejected', kwarg: 'reason' }
    ] },
  'M20-form-writeoff': {
    kind: 'model_form',
    model: 'fix.ar.writeoff',
    title: 'Write-off',
    back: 'M20-writeoffs',
    status: { field: 'state', labels: { draft: 'Draft', requested: 'Requested', posted: 'Approved & Posted', rejected: 'Rejected' } },
    sections: [
      { title: 'Request', note: 'FR-ARB-041 / BRU-ARB-12: the open residual of an issued invoice, with the reason and the collection steps already taken. It posts against the IFRS 9 loss allowance first, only the excess to bad-debt expense, and never by the person who requested it.',
        fields: [
          { name: 'invoice_id', required: true, label: 'Invoice' },
          { name: 'reason', required: true, label: 'Reason' },
          { name: 'recovery_history', required: true, type: 'text', label: 'Recovery History' }
        ] },
      { title: 'Approval & Posting (system)',
        fields: [
          { name: 'name', readonly: true, label: 'Reference' },
          { name: 'customer_id', readonly: true, label: 'Customer' },
          { name: 'amount', readonly: true, label: 'Amount (residual at request)' },
          { name: 'allowance_amount', readonly: true, label: 'Charged to Loss Allowance' },
          { name: 'expense_amount', readonly: true, label: 'Charged to Bad-Debt Expense' },
          { name: 'requested_by_id', readonly: true, label: 'Requested By' },
          { name: 'rejected_reason', readonly: true, label: 'Rejection Reason' },
          { name: 'state', readonly: true, label: 'State' }
        ] }
    ]
  },
  /* BRU-ARB-22: money received and not applied, aged; the daily job escalates. */
  'M20-unapplied': { empty: 'No unapplied receipt: every receipt recorded is allocated to invoices.', kind: 'model_list', model: 'fix.ar.receipt', create: false,
    domain: [['state', '=', 'confirmed'], ['unapplied_amount', '>', 0]],
    cols: ['name', 'customer_id', 'receipt_date', 'method', 'amount', 'allocated_amount', 'unapplied_amount', 'unapplied_escalated_at'] },
  'M20-gl-recon': { kind: 'table_report', module: 'M20', report: 'ar_subledger_gl_recon', title: 'AR Sub-ledger to GL Reconciliation', period: false },
  'M20-invoices': { kind: 'ar_invoices' },
  'M20-invoice': { kind: 'ar_editor' },
  'M20-events': { kind: 'ar_events' },
  'M20-consolidated': { kind: 'ar_consolidated' },
  'M20-brand': { kind: 'ar_brand' },
  'M20-receipts': { kind: 'ar_receipts' },
  'M20-links': { kind: 'ar_links' },
  'M20-allocation': { kind: 'ar_allocation' },
  'M20-credit': { kind: 'ar_credit' },
  'M20-dunning': { kind: 'ar_dunning' },
  'M20-disputes': { kind: 'ar_disputes' },
  'M20-refunds': { kind: 'ar_refunds' },
  'M20-aging': { kind: 'ar_aging' },
  'M20-leakage': { kind: 'ar_leakage' },
  'M20-statements': { kind: 'ar_statements' },
  // ---- A08 additions (generic screens, controllers/a08/m20.py) ----
  'M20-vds': { kind: 'model_list', model: 'fix.vds.certificate.received',
    cols: ['name','customer_id','invoice_id','certificate_no','certificate_date','period','vds_amount','state'],
    stateField: 'state',
    actions: [{m:'action_verify',l:'Verify (checker)'},{m:'action_settle',l:'Settle against Receivable'},{m:'action_cancel',l:'Cancel'}] },
  /* Income tax deducted at source by corporate / government customers
   * (ITA 2023 s.89 supply, s.90 services): verify, then settle the TDS part
   * of the receivable to the advance income tax (AIT) account. */
  'M20-tds': { kind: 'model_list', model: 'fix.tds.certificate.received',
    empty: 'No TDS certificate recorded. When a corporate customer deducts income tax at source, record its certificate here so the invoice stops ageing as unpaid.',
    cols: ['name','customer_id','invoice_id','certificate_no','certificate_date','tax_section','tds_amount','state'],
    stateField: 'state',
    actions: [{m:'action_verify',l:'Verify (checker)'},{m:'action_settle',l:'Settle against Receivable'},{m:'action_cancel',l:'Cancel'}] },
  'M20-closeout': { empty: 'No invoice is waiting for close-out.', kind: 'model_list', model: 'fix.ar.invoice',
    cols: ['name','customer_id','invoice_date','total_payable','amount_paid','credited_amount','vds_settled_amount','tds_settled_amount','amount_residual','state'],
    domain: [['state','=','issued']], create: false,
    actions: [{m:'action_register_paid',l:'Register Paid (residual covered)'}] },
  'M20-vds-register': { kind: 'table_report', module: 'M20', report: 'vds_claim_register', title: 'VDS Received Register' },

  /* ============ THE SIX REGISTRY BUILT-IN REPORTS (v2 re-audit) ==========
   * Every chip opens its OWN computed report over controllers/a08/m20.py —
   * never the nearest list (D17). */
  'M20-rpt-segment': { kind: 'table_report', module: 'M20', report: 'ageing_by_segment', title: 'AR Ageing by Segment', period: false },
  'M20-rpt-dunning': { kind: 'table_report', module: 'M20', report: 'dunning_effectiveness', title: 'Dunning Effectiveness', period: false },
  'M20-rpt-mix': { kind: 'table_report', module: 'M20', report: 'payment_method_mix', title: 'Payment Method Mix', period: true },
  'M20-rpt-accuracy': { kind: 'table_report', module: 'M20', report: 'invoice_accuracy', title: 'Invoice Accuracy', period: true },
  'M20-rpt-brandage': { kind: 'table_report', module: 'M20', report: 'brand_receivable_ageing', title: 'Brand Receivable Ageing', period: false },
  'M20-rpt-productivity': { kind: 'table_report', module: 'M20', report: 'collections_productivity', title: 'Collections Productivity', period: true },

  /* Credit-note register with the submit → approve → issue workflow (the
   * D365 form creates the draft; the register moves it). */
  'M20-notes-register': { empty: 'Credit notes and refunds are requested from Credit Notes & Refunds; they are listed here once requested.', kind: 'model_list', model: 'fix.credit.note', stateField: 'state',
    create: false,
    cols: ['invoice_id', 'amount', 'reason_code', 'state', 'approval_state', 'issued_at', 'approved_by', 'refund_amount', 'refund_ref', 'gl_note'],
    actions: [
      { m: 'action_submit', l: 'Submit for Approval' },
      { m: 'action_approve', l: 'Approve' },
      { m: 'action_reject', l: 'Reject', ask: 'Why the credit note is rejected', kwarg: 'reason' },
      { m: 'action_rerequest', l: 'Re-request (returned by approver)', ask: 'The information the approver asked for', kwarg: 'justification' },
      { m: 'action_withdraw_to_draft', l: 'Withdraw to Draft (returned)', ask: 'Why the note is withdrawn', kwarg: 'reason' },
      { m: 'action_issue', l: 'Issue & Post to GL' },
    ] },

  /* ============ D365 IN-WORKSPACE FORM SCREENS (v2 re-audit) ============
   * The registry's five data-entry chips open real Dynamics-365 record
   * forms inside the workspace — never an Odoo dialog or a bare list. */
  'M20-form-receipt': {
    kind: 'model_form',
    model: 'fix.ar.receipt',
    title: 'Receipt',
    back: 'M20-receipts',
    status: { field: 'state', labels: { draft: 'Draft', confirmed: 'Confirmed', reversed: 'Reversed' } },
    sections: [
      {
        title: 'Receipt Capture',
        note: 'FR-ARB-024..028: the payment method comes from the one customer payment-method list (Rocket, Upay, RTGS included) and sets the tender the receipt books as; two-stage clearing. Capturing a receipt creates a DRAFT — Confirming posts Dr channel-account / Cr AR through M19. The branch dimension is required by the chart (COA-03); without one the confirm is refused rather than posted without a branch.',
        fields: [
          { name: 'customer_id', required: true, label: 'Customer' },
          { name: 'amount', required: true, label: 'Amount (BDT)' },
          { name: 'payment_method_id', required: true, label: 'Payment Method' },
          { name: 'method', readonly: true, label: 'Booked As (set by the payment method)' },
          { name: 'reference', label: 'Reference (TrxID / cheque no)' },
          { name: 'receipt_date', required: true, label: 'Receipt Date' },
          { name: 'branch_id', required: true, label: 'Collecting Branch' },
          { name: 'nid_captured', label: 'Customer NID (cash > threshold)' }
        ]
      },
      {
        title: 'Posting & Application (system)',
        note: 'Confirm from the Receipts workbook. Cash above the configured threshold requires the NID (FR-ARB-026) — the model refuses rather than posting untracked money.',
        fields: [
          { name: 'name', readonly: true, label: 'Receipt Number (auto)' },
          { name: 'state', readonly: true, label: 'Status' },
          { name: 'account_id', readonly: true, label: 'Cleared Into Account' },
          { name: 'allocated_amount', readonly: true, label: 'Allocated' },
          { name: 'unapplied_amount', readonly: true, label: 'Unapplied' },
          { name: 'gl_note', readonly: true, label: 'GL Note' }
        ]
      }
    ]
  },

  'M20-form-note': {
    kind: 'model_form',
    model: 'fix.credit.note',
    title: 'Credit Note',
    back: 'M20-notes-register',
    status: { field: 'state', labels: { draft: 'Draft', pending_approval: 'Pending Approval', approved: 'Approved', rejected: 'Rejected', issued: 'Issued' } },
    sections: [
      {
        title: 'Credit Request',
        note: 'FR-ARB-036: a credit note reverses revenue + VAT pro-rata on the original invoice. It is never approved by its raiser: up to BDT 10,000 (cumulative on the invoice) a second Accountant approves; above it the Accounting Administrator approves from the M63 inbox. Credits never exceed the invoice; the part covering money already received is refunded through treasury (M50).',
        fields: [
          { name: 'invoice_id', required: true, label: 'Original Invoice' },
          { name: 'amount', required: true, label: 'Credit Amount (BDT)' },
          { name: 'reason_code', required: true, label: 'Reason Code' },
          { name: 'operating_unit_id', required: true, label: 'Operating Unit' }
        ]
      },
      {
        title: 'Approval & Posting (system)',
        note: 'Submit → Approve → Issue from the Credit-Note Register. Issuing posts the GL mirror and updates the invoice residual.',
        fields: [
          { name: 'state', readonly: true, label: 'Status' },
          { name: 'requested_by_id', readonly: true, label: 'Submitted By' },
          { name: 'approved_by', readonly: true, label: 'Approved By' },
          { name: 'tier_basis_amount', readonly: true, label: 'Cumulative Credit (tier basis)' },
          { name: 'issued_at', readonly: true, label: 'Issued At' },
          { name: 'posted_move_id', readonly: true, label: 'GL Move' },
          { name: 'gl_note', readonly: true, label: 'GL Note' },
          { name: 'refund_amount', readonly: true, label: 'Refund of Money Received (M50)' },
          { name: 'refund_ref', readonly: true, label: 'Refund Instruction' }
        ]
      }
    ]
  },

  'M20-form-link': {
    kind: 'model_form',
    model: 'fix.ar.payment.link',
    title: 'Payment Link',
    back: 'M20-links',
    status: { field: 'state', labels: { new: 'New', used: 'Used', expired: 'Expired' } },
    sections: [
      {
        title: 'Single-Use Link',
        note: 'Links attach to ISSUED invoices only; the model refuses a draft invoice and refuses a second active link per invoice. The bKash/Nagad/SSLCommerz checkout URL is porting phase — the token lifecycle is real.',
        fields: [
          { name: 'invoice_id', required: true, label: 'Issued Invoice' },
          { name: 'expires_at', label: 'Expires At' }
        ]
      },
      {
        title: 'Token & Status (system)',
        fields: [
          { name: 'token', readonly: true, label: 'Link Token' },
          { name: 'amount', readonly: true, label: 'Amount Collected (residual at issue)' },
          { name: 'state', readonly: true, label: 'Status' },
          { name: 'used_at', readonly: true, label: 'Used At' },
          { name: 'gateway_note', readonly: true, label: 'Gateway Note' }
        ]
      }
    ]
  },

  'M20-form-vds': {
    kind: 'model_form',
    model: 'fix.vds.certificate.received',
    title: 'VDS Certificate',
    back: 'M20-vds',
    status: { field: 'state', labels: { draft: 'Draft', verified: 'Verified', settled: 'Settled against Receivable', claimed: 'Claimed in Mushak 9.1', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'certificate', label: 'Certificate', bn: 'সনদ' },
      { id: 'verification', label: 'Verification & Claim', bn: 'যাচাই ও দাবি' }
    ],
    sections: [
      {
        tab: 'certificate',
        title: 'Mushak 6.6 Certificate',
        note: 'The customer deducts VDS at source and issues a Mushak 6.6 certificate. Record it here, then Verify → Settle against the receivable → claim in the Mushak 9.1 adjustment.',
        fields: [
          { name: 'invoice_id', required: true, label: 'Original Invoice' },
          { name: 'certificate_no', required: true, label: 'Certificate No' },
          { name: 'certificate_date', required: true, label: 'Certificate Date' },
          { name: 'period', required: true, label: 'VAT Period (YYYY-MM)' },
          { name: 'vds_amount', required: true, label: 'VDS Amount (BDT)' },
          { name: 'challan_no', label: 'Challan No' },
          { name: 'challan_date', label: 'Challan Date' },
          { name: 'customer_bin', label: 'Customer BIN' },
          { name: 'note', label: 'Note', type: 'text' }
        ]
      },
      {
        tab: 'verification',
        title: 'Verification & Claim (system)',
        note: 'Verify and Settle from the VDS register; the tax return marks the certificate claimed.',
        fields: [
          { name: 'name', readonly: true, label: 'Declaration Ref (auto)' },
          { name: 'customer_id', readonly: true, label: 'Customer' },
          { name: 'invoice_vat_amount', readonly: true, label: 'Invoice VAT' },
          { name: 'state', readonly: true, label: 'Status' },
          { name: 'prepared_by_id', readonly: true, label: 'Prepared By' },
          { name: 'verified_by_id', readonly: true, label: 'Verified By' },
          { name: 'claimed_return_ref', readonly: true, label: 'Claimed in Return' }
        ]
      }
    ]
  },

  'M20-form-tds': {
    kind: 'model_form',
    model: 'fix.tds.certificate.received',
    title: 'TDS / AIT Certificate',
    back: 'M20-tds',
    status: { field: 'state', labels: { draft: 'Draft', verified: 'Verified', settled: 'Settled against Receivable', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'certificate', label: 'Certificate', bn: 'সনদ' },
      { id: 'invoice', label: 'Invoice', bn: 'ইনভয়েস' },
      { id: 'verification', label: 'Verification & Settlement', bn: 'যাচাই ও নিষ্পত্তি' }
    ],
    sections: [
      {
        tab: 'certificate',
        title: 'Certificate of Tax Deducted at Source',
        note: 'A corporate or government customer deducts income tax at source (Income Tax Act 2023 s.89 supply / contract, s.90 services) and issues a certificate. Record it here; a second person verifies it against the original; Settle then clears that part of the receivable to the advance income tax (AIT) account.',
        fields: [
          { name: 'invoice_id', required: true, label: 'Original Invoice' },
          { name: 'certificate_no', required: true, label: 'Certificate No' },
          { name: 'certificate_date', required: true, label: 'Certificate Date' },
          { name: 'tax_section', required: true, label: 'Deducted Under (section)' },
          { name: 'tds_amount', required: true, label: 'Tax Deducted (BDT)' },
          { name: 'customer_tin', label: 'Deductor e-TIN' },
          { name: 'challan_no', label: 'Treasury Challan No' },
          { name: 'challan_date', label: 'Challan Date' },
          { name: 'note', label: 'Note', type: 'text' }
        ]
      },
      {
        tab: 'invoice',
        title: 'Invoice (system)',
        note: 'The tax recorded on an invoice can never exceed what is still open on it.',
        fields: [
          { name: 'customer_id', readonly: true, label: 'Customer' },
          { name: 'invoice_total', readonly: true, label: 'Invoice Total' },
          { name: 'invoice_residual', readonly: true, label: 'Open Residual' },
          { name: 'operating_unit_id', readonly: true, label: 'Operating Unit' }
        ]
      },
      {
        tab: 'verification',
        title: 'Verification & Settlement (system)',
        note: 'Verify and Settle from the TDS register. The preparer cannot verify; settlement posts Dr AIT receivable / Cr AR.',
        fields: [
          { name: 'name', readonly: true, label: 'Reference (auto)' },
          { name: 'state', readonly: true, label: 'Status' },
          { name: 'prepared_by_id', readonly: true, label: 'Prepared By' },
          { name: 'verified_by_id', readonly: true, label: 'Verified By' },
          { name: 'verified_at', readonly: true, label: 'Verified On' },
          { name: 'settled_move_id', readonly: true, label: 'Settlement GL Move' },
          { name: 'settled_at', readonly: true, label: 'Settled On' }
        ]
      }
    ]
  },

  /* ===== triage coverage screens ===== */
  'M20-ar-dispute': { empty: 'No dispute yet. Raise one with + New Dispute when a customer contests an issued invoice.', kind: 'model_list', model: 'fix.ar.dispute', stateField: 'state',
    cols: ['name', 'state', 'invoice_id', 'amount_disputed', 'reason', 'outcome_code', 'resolution_note', 'resolved_by'],
    actions: [
      { m: 'action_resolve_upheld_credit', l: 'Resolve: Upheld (credit note)', ask: 'Resolution note', kwarg: 'note' },
      { m: 'action_resolve_partially_upheld', l: 'Resolve: Partially Upheld', ask: 'Resolution note', kwarg: 'note' },
      { m: 'action_resolve_rejected', l: 'Resolve: Rejected', ask: 'Resolution note', kwarg: 'note' },
      { m: 'action_resolve_withdrawn', l: 'Resolve: Withdrawn', ask: 'Resolution note', kwarg: 'note' },
      { m: 'action_resolve_payment_plan', l: 'Resolve: Payment Plan', ask: 'Resolution note', kwarg: 'note' }
    ] },
  /* FR-ARB-008: + New records the corporate customer and the period; Generate
   * pulls that period's issued invoices onto the bill. */
  'M20-ar-consolidated-bill': { empty: 'No consolidated bill yet. Start one with + New Consolidated Bill, then Generate it from the period\'s issued invoices.', kind: 'model_list', model: 'fix.ar.consolidated.bill', stateField: 'state',
    cols: ['bill_ref', 'customer_id', 'operating_unit_id', 'period_start', 'period_end', 'total_payable', 'state'],
    actions: [
      { m: 'action_generate', l: 'Generate (pull the period\'s issued invoices)' },
      { m: 'action_send', l: 'Mark Sent' }
    ] },
  'M20-form-consolidated': {
    kind: 'model_form',
    model: 'fix.ar.consolidated.bill',
    title: 'Consolidated Bill',
    back: 'M20-ar-consolidated-bill',
    status: { field: 'state', labels: { draft: 'Draft', generated: 'Generated', sent: 'Sent', paid: 'Paid', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Corporate Account & Period', note: 'FR-ARB-008: one bill for a corporate account\'s period. Save it as a draft, then Generate it from the list: it carries that customer\'s ISSUED invoices dated inside the period, never a draft (no number, no Mushak 6.3).',
        fields: [
          { name: 'customer_id', required: true, label: 'Corporate Customer' },
          { name: 'operating_unit_id', required: true, label: 'Operating Unit' },
          { name: 'bill_ref', required: true, label: 'Bill Reference' },
          { name: 'period_start', required: true, label: 'Period Start' },
          { name: 'period_end', required: true, label: 'Period End' }
        ] },
      { title: 'Totals (system)',
        fields: [
          { name: 'state', readonly: true, label: 'Status' },
          { name: 'total_taxable', readonly: true, label: 'Total Taxable' },
          { name: 'total_vat', readonly: true, label: 'Total VAT' },
          { name: 'total_payable', readonly: true, label: 'Total Payable' }
        ] }
    ]
  },
  /* FR-ARB-036 (P0): a dispute is logged against an issued invoice; dunning
   * then stops on the disputed amount only. Resolved from the dispute list. */
  'M20-form-dispute': {
    kind: 'model_form',
    model: 'fix.ar.dispute',
    title: 'Dispute',
    back: 'M20-ar-dispute',
    status: { field: 'state', labels: { open: 'Open', resolved: 'Resolved' } },
    sections: [
      { title: 'Disputed Invoice', note: 'The customer contests part or all of an issued invoice. Dunning stops on the disputed amount only; the rest keeps its reminders. Open disputes on an invoice never exceed what is still open on it. Another person resolves it, with an outcome code.',
        fields: [
          { name: 'invoice_id', required: true, label: 'Invoice', domain: [['state', 'in', ['issued', 'paid']]] },
          { name: 'amount_disputed', required: true, label: 'Disputed Amount (BDT)' },
          { name: 'reason', required: true, label: 'What the customer contests' }
        ] },
      { title: 'Resolution (system)',
        fields: [
          { name: 'state', readonly: true, label: 'Status' },
          { name: 'outcome_code', readonly: true, label: 'Outcome' },
          { name: 'resolution_note', readonly: true, label: 'Resolution' },
          { name: 'resolved_by', readonly: true, label: 'Resolved By' },
          { name: 'resolved_at', readonly: true, label: 'Resolved At' }
        ] }
    ]
  },
  'M20-dunning-register': { empty: 'Dunning steps are generated by the collections cycle for overdue invoices.', kind: 'model_list', model: 'fix.dunning', create: false,
    cols: ['name', 'invoice_id', 'overdue_amount', 'step', 'step_date', 'channel', 'policy_id', 'suppressed', 'suppression_reason', 'suppressed_until', 'suppression_note'],
    actions: [
      { m: 'action_suppress_payment_plan', l: 'Suppress: Payment Plan', asks: [{ label: 'Until (YYYY-MM-DD, empty = the configured days)', kwarg: 'until' }, { label: 'Note', kwarg: 'note' }] },
      { m: 'action_suppress_strategic', l: 'Suppress: Strategic Customer', asks: [{ label: 'Until (YYYY-MM-DD, empty = the configured days)', kwarg: 'until' }, { label: 'Note', kwarg: 'note' }] },
      { m: 'action_suppress_dispute', l: 'Suppress: Open Dispute', asks: [{ label: 'Until (YYYY-MM-DD, empty = until the dispute closes)', kwarg: 'until' }, { label: 'Note', kwarg: 'note' }] },
      { m: 'action_lift_suppression', l: 'Lift Suppression', ask: 'Why the suppression ends', kwarg: 'note' }
    ] },

  /* ============ M20 SECOND CAPTURE PASS (19 Nov 2026) ===================
   * The records the spec says a person captures on these pages and that had
   * no model: delivery and statements (p4), deposits (p5), the dunning
   * ladder, promises, payment plans and the collections worklist (p8),
   * refunds of on-account money (p9) and unbilled exceptions (p10). */

  /* p4 FR-ARB-013/014: one record per invoice and channel; a re-send is a Retry. */
  'M20-deliveries': { empty: 'No invoice delivery recorded. Record one with + New Invoice Delivery: the channel, who it went to, then whether it arrived.', kind: 'model_list', model: 'fix.ar.invoice.delivery', stateField: 'status',
    cols: ['name', 'invoice_id', 'customer_id', 'channel', 'recipient', 'status', 'sent_at', 'delivered_at', 'retry_count', 'failure_reason'],
    actions: [
      { m: 'action_mark_sent', l: 'Mark Sent' },
      { m: 'action_mark_delivered', l: 'Confirm Delivered' },
      { m: 'action_mark_opened', l: 'Mark Opened' },
      { m: 'action_mark_failed', l: 'Record Failure', ask: 'Why it failed (bounced, wrong number, not reachable)', kwarg: 'reason' },
      { m: 'action_retry', l: 'Retry' }
    ] },
  'M20-form-delivery': {
    kind: 'model_form',
    model: 'fix.ar.invoice.delivery',
    title: 'Invoice Delivery',
    back: 'M20-deliveries',
    status: { field: 'status', labels: { queued: 'Queued', sent: 'Sent', delivered: 'Delivered', opened: 'Opened', failed: 'Failed' } },
    sections: [
      { title: 'Delivery', note: 'FR-ARB-013: an issued invoice delivered on one channel. The recipient defaults to the customer\'s email or mobile. The invoice\'s payment link travels with it; delivering again on the same channel is a Retry on this record, never a second invoice or link (T-12).',
        fields: [
          { name: 'invoice_id', required: true, label: 'Issued Invoice' },
          { name: 'channel', required: true, label: 'Channel' },
          { name: 'recipient', label: 'Recipient (email / mobile; empty = the customer\'s)' }
        ] },
      { title: 'Confirmation (system)', note: 'FR-ARB-014: Mark Sent, Confirm Delivered, Mark Opened or Record Failure from the list. A failure is retried up to the configured count, then another channel is used.',
        fields: [
          { name: 'name', readonly: true, label: 'Reference' },
          { name: 'customer_id', readonly: true, label: 'Customer' },
          { name: 'status', readonly: true, label: 'Status' },
          { name: 'sent_at', readonly: true, label: 'Sent' },
          { name: 'delivered_at', readonly: true, label: 'Delivered' },
          { name: 'opened_at', readonly: true, label: 'Opened' },
          { name: 'retry_count', readonly: true, label: 'Retries' },
          { name: 'failure_reason', readonly: true, label: 'Failure' },
          { name: 'payment_link_id', readonly: true, label: 'Payment Link Sent' }
        ] }
    ]
  },
  /* p4 FR-ARB-017: a statement of account, frozen once generated. */
  'M20-statement-register': { empty: 'No statement requested. Request one with Customer Statement: the customer and the period, then Generate.', kind: 'model_list', model: 'fix.ar.statement', stateField: 'state',
    cols: ['name', 'customer_id', 'period_from', 'period_to', 'opening_balance', 'total_charges', 'total_credits', 'closing_balance', 'state', 'delivery_channel'],
    actions: [
      { m: 'action_generate', l: 'Generate' },
      { m: 'action_mark_delivered', l: 'Mark Delivered', ask: 'Channel: portal, email, whatsapp, sms or print', kwarg: 'channel' }
    ] },
  'M20-form-statement': {
    kind: 'model_form',
    model: 'fix.ar.statement',
    title: 'Customer Statement',
    back: 'M20-statement-register',
    status: { field: 'state', labels: { draft: 'Draft', generated: 'Generated', delivered: 'Delivered' } },
    sections: [
      { title: 'Customer & Period', note: 'FR-ARB-017: opening balance, every invoice, credit note and receipt in the period, closing balance. Generate it from the list; it is then frozen, so the statement the customer received can be reproduced.',
        fields: [
          { name: 'customer_id', required: true, label: 'Customer' },
          { name: 'period_from', required: true, label: 'Period From' },
          { name: 'period_to', required: true, label: 'Period To' }
        ] },
      { title: 'Statement (system)',
        fields: [
          { name: 'name', readonly: true, label: 'Reference' },
          { name: 'opening_balance', readonly: true, label: 'Opening Balance' },
          { name: 'total_charges', readonly: true, label: 'Invoiced' },
          { name: 'total_credits', readonly: true, label: 'Credits & Receipts' },
          { name: 'closing_balance', readonly: true, label: 'Closing Balance' },
          { name: 'line_count', readonly: true, label: 'Transactions' },
          { name: 'lines_text', readonly: true, type: 'text', label: 'Transaction Lines' },
          { name: 'generated_by', readonly: true, label: 'Generated By' },
          { name: 'delivery_channel', readonly: true, label: 'Delivered On' },
          { name: 'state', readonly: true, label: 'Status' }
        ] }
    ]
  },
  /* p5 FR-ARB-028: deposit / retention / advance money held apart. */
  'M20-deposits': { empty: 'No deposit or retention held. Record one with Deposit / Retention against the receipt that brought the money.', kind: 'model_list', model: 'fix.ar.deposit', stateField: 'state',
    cols: ['name', 'customer_id', 'deposit_type', 'receipt_id', 'amount', 'contract_id', 'release_due_at', 'state', 'applied_to_invoice_id'],
    actions: [
      { m: 'action_apply', l: 'Apply to Invoice', ask: 'Invoice number the money is applied to', kwarg: 'invoice' },
      { m: 'action_release', l: 'Release (refund)', ask: 'Why the deposit is returned', kwarg: 'reason' }
    ] },
  'M20-form-deposit': {
    kind: 'model_form',
    model: 'fix.ar.deposit',
    title: 'Deposit / Retention',
    back: 'M20-deposits',
    status: { field: 'state', labels: { held: 'Held', applied: 'Applied', released: 'Released' } },
    sections: [
      { title: 'Money Held', note: 'FR-ARB-028: part of a confirmed receipt held as a deposit, contract retention or an advance. It stops counting as unapplied (no escalation) until it is applied to an invoice or released as a refund that another person authorises.',
        fields: [
          { name: 'deposit_type', required: true, label: 'Type' },
          { name: 'receipt_id', required: true, label: 'Receipt Holding the Money' },
          { name: 'amount', required: true, label: 'Amount Held (BDT)' },
          { name: 'contract_id', label: 'Contract' },
          { name: 'reference', label: 'Agreement Reference' },
          { name: 'release_due_at', label: 'Release / Apply By' }
        ] },
      { title: 'Application (system)',
        fields: [
          { name: 'name', readonly: true, label: 'Reference' },
          { name: 'customer_id', readonly: true, label: 'Customer' },
          { name: 'state', readonly: true, label: 'Status' },
          { name: 'applied_to_invoice_id', readonly: true, label: 'Applied To' },
          { name: 'refund_id', readonly: true, label: 'Refund' }
        ] }
    ]
  },
  /* p8 FR-ARB-032: the ladder per segment or named account. */
  'M20-dunning-policies': { empty: 'No dunning ladder in force: the built-in NT-006 ladder (reminder, final notice after 7 days, collections after 14) applies. Write one with Dunning Policy.', kind: 'model_list', model: 'fix.ar.dunning.policy', stateField: 'state',
    cols: ['name', 'segment', 'first_offset_days', 'l1_channel', 'l2_days', 'l2_channel', 'l3_days', 'l3_channel', 'escalation_role', 'state', 'activated_by_id'],
    actions: [
      { m: 'action_activate', l: 'Activate (second Accounting Administrator)' },
      { m: 'action_retire', l: 'Retire', ask: 'Why the ladder is retired', kwarg: 'reason' }
    ] },
  'M20-form-dunning-policy': {
    kind: 'model_form',
    model: 'fix.ar.dunning.policy',
    title: 'Dunning Policy',
    back: 'M20-dunning-policies',
    status: { field: 'state', labels: { draft: 'Draft', active: 'Active', retired: 'Retired' } },
    tabs: [
      { id: 'policy', label: 'Policy', bn: 'নীতি' },
      { id: 'ladder', label: 'Ladder', bn: 'ধাপ' }
    ],
    sections: [
      { tab: 'policy', title: 'Who It Applies To', note: 'FR-ARB-032: a named-account ladder wins over a segment ladder, which wins over the company default (All customers). Another Accounting Administrator activates it; an active ladder is not edited, it is retired and replaced.',
        fields: [
          { name: 'name', required: true, label: 'Ladder' },
          { name: 'segment', required: true, label: 'Segment' },
          { name: 'customer_ids', label: 'Named Accounts' },
          { name: 'note', type: 'text', label: 'Why this ladder' },
          { name: 'state', readonly: true, label: 'Status' },
          { name: 'activated_by_id', readonly: true, label: 'Activated By' }
        ] },
      { tab: 'ladder', title: 'Levels', note: 'L1 goes out the given days after the due date; L2 and L3 follow after the given days at the level before. L3 opens a collection case for the role named.',
        fields: [
          { name: 'first_offset_days', required: true, label: 'L1 After (days past due)' },
          { name: 'l1_channel', required: true, label: 'L1 Channel' },
          { name: 'l1_tone', required: true, label: 'L1 Tone' },
          { name: 'l2_days', required: true, label: 'L2 After (days at L1)' },
          { name: 'l2_channel', required: true, label: 'L2 Channel' },
          { name: 'l2_tone', required: true, label: 'L2 Tone' },
          { name: 'l3_days', required: true, label: 'L3 After (days at L2)' },
          { name: 'l3_channel', required: true, label: 'L3 Channel' },
          { name: 'l3_tone', required: true, label: 'L3 Tone' },
          { name: 'escalation_role', required: true, label: 'L3 Escalates To' }
        ] }
    ]
  },
  /* p8 FR-ARB-035: a promise holds dunning until its date. */
  'M20-promises': { empty: 'No promise to pay recorded. When a customer commits to a date, record it with Promise to Pay: dunning on that invoice waits until then.', kind: 'model_list', model: 'fix.ar.promise', stateField: 'state',
    cols: ['name', 'invoice_id', 'customer_id', 'amount', 'promised_date', 'made_by', 'state', 'recorded_by', 'case_id'],
    actions: [
      { m: 'action_cancel', l: 'Cancel', ask: 'Why the promise is cancelled', kwarg: 'reason' }
    ] },
  'M20-form-promise': {
    kind: 'model_form',
    model: 'fix.ar.promise',
    title: 'Promise to Pay',
    back: 'M20-promises',
    status: { field: 'state', labels: { open: 'Open', kept: 'Kept', broken: 'Broken', cancelled: 'Cancelled' } },
    sections: [
      { title: 'The Promise', note: 'FR-ARB-035: the amount and the date the customer committed to. Dunning on the invoice waits until the date; the daily check marks it kept when the money arrives, or broken, which resumes dunning and escalates the collection case.',
        fields: [
          { name: 'invoice_id', required: true, label: 'Open Invoice' },
          { name: 'amount', required: true, label: 'Promised Amount (BDT)' },
          { name: 'promised_date', required: true, label: 'Promised Date' },
          { name: 'made_by', required: true, label: 'Promised By (customer side)' },
          { name: 'contact_channel', required: true, label: 'How It Was Made' },
          { name: 'case_id', label: 'Collection Case' },
          { name: 'note', label: 'Note' }
        ] },
      { title: 'Outcome (system)',
        fields: [
          { name: 'name', readonly: true, label: 'Reference' },
          { name: 'customer_id', readonly: true, label: 'Customer' },
          { name: 'residual_at_promise', readonly: true, label: 'Open When Promised' },
          { name: 'recorded_by', readonly: true, label: 'Recorded By' },
          { name: 'state', readonly: true, label: 'Status' },
          { name: 'kept_at', readonly: true, label: 'Kept On' },
          { name: 'broken_at', readonly: true, label: 'Broken On' }
        ] }
    ]
  },
  /* p8 FR-ARB-037: instalments, agreed by a second person. */
  'M20-plans': { empty: 'No payment plan. Propose one with Payment Plan; another Accountant agrees it.', kind: 'model_list', model: 'fix.ar.payment.plan', stateField: 'state',
    cols: ['name', 'customer_id', 'total_amount', 'paid_to_date', 'missed_count', 'state', 'approved_by_id'],
    actions: [
      { m: 'action_activate', l: 'Agree (second Accountant)' },
      { m: 'action_cancel', l: 'Cancel', ask: 'Why the plan is cancelled', kwarg: 'reason' }
    ] },
  'M20-form-plan': {
    kind: 'model_form',
    model: 'fix.ar.payment.plan',
    title: 'Payment Plan',
    back: 'M20-plans',
    status: { field: 'state', labels: { draft: 'Draft', active: 'Active', completed: 'Completed', defaulted: 'Defaulted', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'plan', label: 'Plan', bn: 'পরিকল্পনা' },
      { id: 'instalments', label: 'Instalments', bn: 'কিস্তি' }
    ],
    sections: [
      { tab: 'plan', title: 'Customer & Invoices', note: 'FR-ARB-037: the overdue invoices settled by instalments. The instalments add up to what is open on them; another Accountant agrees the plan, and dunning on those invoices then waits. A missed instalment defaults the plan, resumes dunning and escalates the collection case.',
        fields: [
          { name: 'customer_id', required: true, label: 'Customer' },
          { name: 'invoice_ids', label: 'Invoices in the Plan' },
          { name: 'reason', required: true, label: 'Why a Plan' },
          { name: 'name', readonly: true, label: 'Reference' },
          { name: 'total_amount', readonly: true, label: 'Settles (at agreement)' },
          { name: 'paid_to_date', readonly: true, label: 'Paid to Date' },
          { name: 'missed_count', readonly: true, label: 'Missed Instalments' },
          { name: 'approved_by_id', readonly: true, label: 'Agreed By' }
        ] }
    ],
    grids: [
      { field: 'line_ids', tab: 'instalments', title: 'Instalments', addLabel: '+ Add instalment',
        empty: 'No instalment yet. Add each due date and amount.',
        note: 'Due today or later; together they equal the open amount of the plan\'s invoices.',
        fields: [
          { name: 'due_date', label: 'Due Date' },
          { name: 'amount', label: 'Amount (BDT)' },
          { name: 'note', label: 'Note' }
        ] }
    ]
  },
  /* p8 FR-ARB-034: the collections worklist, highest priority first. */
  'M20-cases': { empty: 'No collection case. Cases open when dunning reaches L3, a promise breaks or a plan defaults; a collector can open one with Collection Case.', kind: 'model_list', model: 'fix.ar.collection.case', stateField: 'state',
    cols: ['name', 'customer_id', 'priority_score', 'total_overdue', 'oldest_age', 'broken_promises', 'assigned_to', 'next_action_at', 'last_contact_at', 'state', 'origin'],
    actions: [
      { m: 'action_take', l: 'Take' },
      { m: 'action_log_contact', l: 'Log Contact', asks: [{ label: 'What the customer said', kwarg: 'note' }, { label: 'Next action on (YYYY-MM-DD)', kwarg: 'next_action' }] },
      { m: 'action_refresh', l: 'Refresh Priority' },
      { m: 'action_close_paid', l: 'Close: Paid', ask: 'How it was settled', kwarg: 'note' },
      { m: 'action_close_promise', l: 'Close: Promise Recorded', ask: 'Note', kwarg: 'note' },
      { m: 'action_close_plan', l: 'Close: Payment Plan Agreed', ask: 'Note', kwarg: 'note' },
      { m: 'action_close_legal', l: 'Close: Referred to Legal', ask: 'Note', kwarg: 'note' },
      { m: 'action_close_uncollectible', l: 'Close: Uncollectible', ask: 'Note', kwarg: 'note' }
    ] },
  'M20-form-case': {
    kind: 'model_form',
    model: 'fix.ar.collection.case',
    title: 'Collection Case',
    back: 'M20-cases',
    status: { field: 'state', labels: { open: 'Open', in_progress: 'Being Worked', closed: 'Closed' } },
    sections: [
      { title: 'Case', note: 'FR-ARB-034: one open case per customer. Priority = overdue value (BDT thousands) + oldest overdue days + 50 per broken promise; the worklist is sorted by it.',
        fields: [
          { name: 'customer_id', required: true, label: 'Customer' },
          { name: 'assigned_to', label: 'Collector' },
          { name: 'next_action_at', label: 'Next Action On' },
          { name: 'note', type: 'text', label: 'Why the case is opened' }
        ] },
      { title: 'Exposure & History (system)',
        fields: [
          { name: 'name', readonly: true, label: 'Reference' },
          { name: 'priority_score', readonly: true, label: 'Priority' },
          { name: 'total_overdue', readonly: true, label: 'Overdue' },
          { name: 'overdue_count', readonly: true, label: 'Overdue Invoices' },
          { name: 'oldest_age', readonly: true, label: 'Oldest Overdue (days)' },
          { name: 'broken_promises', readonly: true, label: 'Broken Promises' },
          { name: 'last_contact_at', readonly: true, label: 'Last Contact' },
          { name: 'last_contact_note', readonly: true, label: 'Last Contact Note' },
          { name: 'origin', readonly: true, label: 'Opened By' },
          { name: 'outcome', readonly: true, label: 'Outcome' },
          { name: 'state', readonly: true, label: 'Status' }
        ] }
    ]
  },
  /* p9 FR-ARB-040: refund of on-account money. */
  'M20-oa-refunds': { empty: 'No refund of on-account money. Money already applied to an invoice is returned through a credit note; an overpayment or a released deposit is refunded here.', kind: 'model_list', model: 'fix.ar.refund', stateField: 'state',
    cols: ['name', 'customer_id', 'receipt_id', 'amount', 'method', 'reason', 'requested_by_id', 'authorised_by_id', 'payment_instruction', 'state'],
    actions: [
      { m: 'action_authorise', l: 'Authorise (another person)' },
      { m: 'action_reject', l: 'Reject', ask: 'Why the refund is rejected', kwarg: 'reason' }
    ] },
  'M20-form-refund': {
    kind: 'model_form',
    model: 'fix.ar.refund',
    title: 'Refund',
    back: 'M20-oa-refunds',
    status: { field: 'state', labels: { requested: 'Requested', authorised: 'Authorised', rejected: 'Rejected' } },
    sections: [
      { title: 'Refund Request', note: 'FR-ARB-040: money the customer has on account (an overpayment) goes back to them. Another person authorises it: an Accountant within the direct band, the Accounting Administrator above it; treasury (M50) then pays it. Cash above the threshold is refused (BRU-ARB-11).',
        fields: [
          { name: 'receipt_id', required: true, label: 'Receipt With Money on Account' },
          { name: 'amount', required: true, label: 'Refund Amount (BDT)' },
          { name: 'method', required: true, label: 'Refund Method' },
          { name: 'payee_account', label: 'Pay To (wallet / account no.)' },
          { name: 'reason', required: true, label: 'Reason' }
        ] },
      { title: 'Authorisation (system)',
        fields: [
          { name: 'name', readonly: true, label: 'Reference' },
          { name: 'customer_id', readonly: true, label: 'Customer' },
          { name: 'requested_by_id', readonly: true, label: 'Requested By' },
          { name: 'authorised_by_id', readonly: true, label: 'Authorised By' },
          { name: 'payment_instruction', readonly: true, label: 'Treasury Instruction' },
          { name: 'rejected_reason', readonly: true, label: 'Rejection Reason' },
          { name: 'state', readonly: true, label: 'Status' }
        ] }
    ]
  },
  /* p10 FR-ARB-043 / BRU-ARB-24: delivered but not invoiced. */
  'M20-unbilled': { empty: 'No delivered-but-unbilled exception. The daily reconciliation raises one for every closed job without an invoice; report other delivered work with + New Unbilled Exception.', kind: 'model_list', model: 'fix.ar.unbilled.exception', stateField: 'state',
    cols: ['name', 'source_module', 'source_ref', 'customer_id', 'delivered_at', 'estimated_value', 'age_days', 'escalated_to', 'state', 'resolution'],
    actions: [
      { m: 'action_resolve_invoiced', l: 'Resolve: Invoiced', ask: 'Number of the issued invoice that bills it', kwarg: 'invoice' },
      { m: 'action_resolve_not_billable', l: 'Resolve: Not Billable (Accounting Administrator)', ask: 'Why it is not billable', kwarg: 'note' },
      { m: 'action_resolve_duplicate', l: 'Resolve: Duplicate', ask: 'Which item it duplicates', kwarg: 'note' }
    ] },
  'M20-form-unbilled': {
    kind: 'model_form',
    model: 'fix.ar.unbilled.exception',
    title: 'Unbilled Exception',
    back: 'M20-unbilled',
    status: { field: 'state', labels: { open: 'Open', escalated: 'Escalated', resolved: 'Resolved' } },
    sections: [
      { title: 'Delivered Work Not Invoiced', note: 'FR-ARB-043: work delivered with no invoice. The daily reconciliation raises closed service orders by itself; report here what it does not read (a contract cycle, a rental period, an order). It ages and escalates to the branch manager, the Finance Manager and the CFO; "not billable" is approved by an Accounting Administrator who did not report it (BRU-ARB-01).',
        fields: [
          { name: 'source_module', required: true, label: 'Revenue Stream' },
          { name: 'source_ref', required: true, label: 'Source Document' },
          { name: 'customer_id', required: true, label: 'Customer' },
          { name: 'delivered_at', required: true, label: 'Delivered On' },
          { name: 'estimated_value', label: 'Estimated Value (BDT)' },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'note', type: 'text', label: 'Note' }
        ] },
      { title: 'Ageing & Resolution (system)',
        fields: [
          { name: 'name', readonly: true, label: 'Reference' },
          { name: 'detected_by', readonly: true, label: 'Detected By' },
          { name: 'age_days', readonly: true, label: 'Age (days)' },
          { name: 'escalated_to', readonly: true, label: 'Escalated To' },
          { name: 'state', readonly: true, label: 'Status' },
          { name: 'resolution', readonly: true, label: 'Resolution' },
          { name: 'invoice_id', readonly: true, label: 'Invoice' },
          { name: 'resolution_note', readonly: true, label: 'Resolution Note' },
          { name: 'resolved_by', readonly: true, label: 'Resolved By' }
        ] }
    ]
  },


};

/* built-in report chips -> the computed report screen (D17) */
export const REPORT_ROUTES = {
  'M20:IFRS 9 ECL Provision': 'M20-rpt-ecl',
  "M20:AR Ageing by Segment": "M20-rpt-segment",
  "M20:Dunning Effectiveness": "M20-rpt-dunning",
  "M20:Payment Method Mix": "M20-rpt-mix",
  "M20:Invoice Accuracy": "M20-rpt-accuracy",
  "M20:Brand Receivable Ageing": "M20-rpt-brandage",
  "M20:Collections Productivity": "M20-rpt-productivity",
  "M20:VDS Received Register": "M20-vds-register",
  "M20:AR Sub-ledger to GL Reconciliation": "M20-gl-recon",
};

/* data-entry form chips -> real model forms */
export const FORM_MODELS = {
  'M20:Invoice Request': 'fix.ar.invoice',
  'M20:Credit Note': 'fix.credit.note',
  'M20:Refund': 'fix.ar.refund',
  'M20:Receipt': 'fix.ar.receipt',
  'M20:Payment Link': 'fix.ar.payment.link',
  'M20:VDS Certificate': 'fix.vds.certificate.received',
  'M20:TDS Certificate': 'fix.tds.certificate.received',
  'M20:Write-off': 'fix.ar.writeoff',
  'M20:ECL Loss Rates': 'fix.ar.ecl.rate',
  'M20:Consolidated Bill': 'fix.ar.consolidated.bill',
  'M20:Dispute': 'fix.ar.dispute',
  'M20:Credit Profile': 'fix.credit.profile',
  'M20:Proforma Invoice': 'fix.sales.proforma',
  'M20:Invoice Delivery': 'fix.ar.invoice.delivery',
  'M20:Customer Statement': 'fix.ar.statement',
  'M20:Deposit / Retention': 'fix.ar.deposit',
  'M20:Dunning Policy': 'fix.ar.dunning.policy',
  'M20:Promise to Pay': 'fix.ar.promise',
  'M20:Payment Plan': 'fix.ar.payment.plan',
  'M20:Collection Case': 'fix.ar.collection.case',
  'M20:Unbilled Exception': 'fix.ar.unbilled.exception',
};

/* the registry chips + every grid's + New / Open full record resolve to the
 * in-workspace D365 form for its model. */
export const FORM_CHIPS = {
  'M20:Receipt': 'M20-form-receipt',
  'M20:Credit Note': 'M20-form-note',
  'M20:Refund': 'M20-form-refund',
  'M20:Payment Link': 'M20-form-link',
  'M20:VDS Certificate': 'M20-form-vds',
  'M20:TDS Certificate': 'M20-form-tds',
  'M20:Write-off': 'M20-form-writeoff',
  'M20:ECL Loss Rates': 'M20-form-ecl-rate',
  'M20:Consolidated Bill': 'M20-form-consolidated',
  'M20:Dispute': 'M20-form-dispute',
  'M20:Credit Profile': 'M33-form-credit',
  'M20:Proforma Invoice': 'M36-form-proforma',
  'M20:Invoice Delivery': 'M20-form-delivery',
  'M20:Customer Statement': 'M20-form-statement',
  'M20:Deposit / Retention': 'M20-form-deposit',
  'M20:Dunning Policy': 'M20-form-dunning-policy',
  'M20:Promise to Pay': 'M20-form-promise',
  'M20:Payment Plan': 'M20-form-plan',
  'M20:Collection Case': 'M20-form-case',
  'M20:Unbilled Exception': 'M20-form-unbilled',
  'M20:__by_model__': {
    'fix.ar.consolidated.bill': 'M20-form-consolidated',
    'fix.ar.dispute': 'M20-form-dispute',
    'fix.ar.impairment': 'M20-form-ecl',
    'fix.ar.ecl.rate': 'M20-form-ecl-rate',
    'fix.ar.writeoff': 'M20-form-writeoff',

    'fix.ar.receipt': 'M20-form-receipt',
    'fix.credit.note': 'M20-form-note',
    'fix.ar.payment.link': 'M20-form-link',
    'fix.vds.certificate.received': 'M20-form-vds',
    'fix.tds.certificate.received': 'M20-form-tds',
    'fix.ar.invoice.delivery': 'M20-form-delivery',
    'fix.ar.statement': 'M20-form-statement',
    'fix.ar.deposit': 'M20-form-deposit',
    'fix.ar.dunning.policy': 'M20-form-dunning-policy',
    'fix.ar.promise': 'M20-form-promise',
    'fix.ar.payment.plan': 'M20-form-plan',
    'fix.ar.collection.case': 'M20-form-case',
    'fix.ar.refund': 'M20-form-refund',
    'fix.ar.unbilled.exception': 'M20-form-unbilled'
  },
  'M20:__by_screen__': {
    'M20-ecl': 'M20-form-ecl',
    'M20-ecl-rates': 'M20-form-ecl-rate',
    'M20-writeoffs': 'M20-form-writeoff',
    'M20-vds': 'M20-form-vds',
    'M20-tds': 'M20-form-tds',
    'M20-notes-register': 'M20-form-note',
    'M20-ar-dispute': 'M20-form-dispute',
    'M20-ar-consolidated-bill': 'M20-form-consolidated',
    'M20-deliveries': 'M20-form-delivery',
    'M20-statement-register': 'M20-form-statement',
    'M20-deposits': 'M20-form-deposit',
    'M20-dunning-policies': 'M20-form-dunning-policy',
    'M20-promises': 'M20-form-promise',
    'M20-plans': 'M20-form-plan',
    'M20-cases': 'M20-form-case',
    'M20-oa-refunds': 'M20-form-refund',
    'M20-unbilled': 'M20-form-unbilled'
  }
};

/* the module's "+ New" surface */
export const CREATE = {
  M20: { model: 'fix.ar.invoice', label: 'AR Invoice' },
};
