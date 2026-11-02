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
    ]},
    { en: 'Record Coverage', screens: [
      { id: 'M20-ar-dispute', en: "Ar Dispute", bn: "Ar Dispute", t: 'g' },
      { id: 'M20-ar-consolidated-bill', en: "Ar Consolidated Bill", bn: "Ar Consolidated Bill", t: 'g' },
      { id: 'M20-dunning-register', en: 'Dunning Register', bn: 'দেনা আদায় রেজিস্টার', t: 'g' }
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
      { id: 'M20-closeout', en: 'Invoice Settlement Close-out', bn: 'ইনভয়েস নিষ্পত্তি সমাপন', t: 'g' }
    ]},
    { en: 'Credit Control', screens: [
      { id: 'M20-credit', en: 'Limits, Terms & Holds', bn: 'ক্রেডিট নিয়ন্ত্রণ', t: 'g' },
      { id: 'M20-dunning', en: 'Dunning Worklist', bn: 'দেনা আদায়', t: 'c' },
      { id: 'M20-disputes', en: 'Disputes', bn: 'বিরোধ', t: 'g' },
      { id: 'M20-refunds', en: 'Credit Notes & Refunds', bn: 'ক্রেডিট নোট', t: 'g' },
      { id: 'M20-notes-register', en: 'Credit-Note Register (approval)', bn: 'ক্রেডিট নোট রেজিস্টার', t: 'g' }
    ]},
    { en: 'Analysis', screens: [
      { id: 'M20-aging', en: 'AR Ageing', bn: 'বয়স্ক প্রাপ্য', t: 'r' },
      { id: 'M20-leakage', en: 'Revenue-Leakage Detection', bn: 'রাজস্ব ক্ষয়', t: 'r' },
      { id: 'M20-statements', en: 'Customer Statements', bn: 'গ্রাহক স্টেটমেন্ট', t: 'r' },
      { id: 'M20-vds-register', en: 'VDS Claim Register (Mushak 9.1)', bn: 'উৎসে ভ্যাট কর্তন দাবি রেজিস্টার (মুশক ৯.১)', t: 'r' }
    ]}
  ],
  reports: ['AR Ageing by Segment', 'Dunning Effectiveness', 'Payment Method Mix', 'Invoice Accuracy', 'Brand Receivable Ageing', 'Collections Productivity', 'VDS Received Register'],
  forms: ['Invoice Request', 'Receipt', 'Credit Note', 'Refund', 'Payment Link', 'VDS Certificate'],
  cross: ['Financial Accounting & GL', 'Treasury & Banking', 'Tax & Regulatory (BD)'],
  freg: { src: 99, sub: [
    ['1', 'Billable-Event Intake', 12], ['2', 'Invoice Assembly', 12], ['3', 'Mushak 6.3 Rendering', 8],
    ['4', 'Delivery Channels', 6], ['5', 'Receipt Capture (8 methods)', 14], ['6', 'Matching & Allocation', 11],
    ['7', 'Credit Control', 9], ['8', 'Dunning & Collections', 12], ['9', 'Credit Notes & Refunds', 8], ['10', 'Leakage Detection', 7]
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
      { title: 'Run', note: 'Compute ages every open invoice against its due date and applies the bucket loss rate; Post writes only the movement against the provision already booked.',
        fields: [
          { name: 'as_of', required: true, label: 'As Of' },
          { name: 'journal_id', required: true, label: 'Journal' },
          { name: 'expense_account_id', label: 'Impairment Expense Account' },
          { name: 'provision_account_id', label: 'Provision Account' },
          { name: 'rate_current', label: 'Rate current (%)' },
          { name: 'rate_1_30', label: 'Rate 1-30 (%)' },
          { name: 'rate_31_60', label: 'Rate 31-60 (%)' },
          { name: 'rate_61_90', label: 'Rate 61-90 (%)' },
          { name: 'rate_90_plus', label: 'Rate 90+ (%)' },
          { name: 'state', required: true, label: 'State' }
        ] }
    ]
  },
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
  'M20-closeout': { kind: 'model_list', model: 'fix.ar.invoice',
    cols: ['name','customer_id','invoice_date','total_payable','amount_paid','credited_amount','vds_settled_amount','amount_residual','state'],
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
  'M20-notes-register': { kind: 'model_list', model: 'fix.credit.note', stateField: 'state',
    create: false,
    cols: ['invoice_id', 'amount', 'reason_code', 'state', 'issued_at', 'approved_by', 'gl_note'],
    actions: [
      { m: 'action_submit', l: 'Submit for Approval' },
      { m: 'action_approve', l: 'Approve' },
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
        note: 'FR-ARB-024..028: eight tenders, two-stage clearing. Capturing a receipt creates a DRAFT — Confirming posts Dr channel-account / Cr AR through M19. The branch dimension is required by the chart (COA-03); without one the confirm is refused rather than posted without a branch.',
        fields: [
          { name: 'customer_id', required: true, label: 'Customer' },
          { name: 'amount', required: true, label: 'Amount (BDT)' },
          { name: 'method', required: true, label: 'Tender Method' },
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
    title: 'Credit Note / Refund',
    back: 'M20-notes-register',
    status: { field: 'state', labels: { draft: 'Draft', pending_approval: 'Pending Approval', approved: 'Approved', rejected: 'Rejected', issued: 'Issued' } },
    sections: [
      {
        title: 'Credit Request',
        note: 'FR-ARB-036: a credit note reverses revenue + VAT pro-rata on the original invoice. Above BDT 25,000 a manager approves before issue.',
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
          { name: 'approved_by', readonly: true, label: 'Approved By' },
          { name: 'issued_at', readonly: true, label: 'Issued At' },
          { name: 'posted_move_id', readonly: true, label: 'GL Move' },
          { name: 'gl_note', readonly: true, label: 'GL Note' }
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
          { name: 'amount', readonly: true, label: 'Invoice Amount' },
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
    sections: [
      {
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
        title: 'Verification & Claim (system)',
        note: 'Verify and Settle from the VDS register; the tax return marks the certificate claimed.',
        fields: [
          { name: 'name', readonly: true, label: 'Declaration Ref (auto)' },
          { name: 'customer_id', readonly: true, label: 'Customer' },
          { name: 'invoice_vat_amount', readonly: true, label: 'Invoice VAT' },
          { name: 'state', readonly: true, label: 'Status' },
          { name: 'claimed_return_ref', readonly: true, label: 'Claimed in Return' }
        ]
      }
    ]
  },

  /* ===== triage coverage screens ===== */
  'M20-ar-dispute': { kind: 'model_list', model: 'fix.ar.dispute', stateField: 'state', create: false,
    cols: ['state', 'company_id', 'operating_unit_id', 'invoice_id', 'amount_disputed', 'reason', 'resolution_note'] },
  'M20-ar-consolidated-bill': { kind: 'model_list', model: 'fix.ar.consolidated.bill', stateField: 'state', create: false,
    cols: ['state', 'company_id', 'operating_unit_id', 'customer_id', 'currency_id', 'bill_ref', 'period_start'] },
  'M20-dunning-register': { kind: 'model_list', model: 'fix.dunning', create: false,
    cols: ['company_id', 'operating_unit_id', 'invoice_id', 'overdue_amount', 'step', 'step_date', 'suppressed'] },


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
};

/* data-entry form chips -> real model forms */
export const FORM_MODELS = {
  'M20:Invoice Request': 'fix.ar.invoice',
  'M20:Credit Note': 'fix.credit.note',
  'M20:Refund': 'fix.credit.note',
  'M20:Receipt': 'fix.ar.receipt',
  'M20:Payment Link': 'fix.ar.payment.link',
  'M20:VDS Certificate': 'fix.vds.certificate.received',
};

/* the registry chips + every grid's + New / Open full record resolve to the
 * in-workspace D365 form for its model. */
export const FORM_CHIPS = {
  'M20:Receipt': 'M20-form-receipt',
  'M20:Credit Note': 'M20-form-note',
  'M20:Refund': 'M20-form-note',
  'M20:Payment Link': 'M20-form-link',
  'M20:VDS Certificate': 'M20-form-vds',
  'M20:__by_model__': {
    'fix.ar.impairment': 'M20-form-ecl',

    'fix.ar.receipt': 'M20-form-receipt',
    'fix.credit.note': 'M20-form-note',
    'fix.ar.payment.link': 'M20-form-link',
    'fix.vds.certificate.received': 'M20-form-vds'
  },
  'M20:__by_screen__': {
    'M20-ecl': 'M20-form-ecl',

    'M20-vds': 'M20-form-vds',
    'M20-notes-register': 'M20-form-note'
  }
};

/* the module's "+ New" surface */
export const CREATE = {
  M20: { model: 'fix.ar.invoice', label: 'AR Invoice' },
};
