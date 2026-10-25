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
    { l: 'Overdue > 60d', m: 'overdue_gt_60d' },
    { l: 'DSO', m: 'dso' },
    { l: 'Auto-Gen %', m: 'auto_generated_pct' },
    { l: 'Within 1h %', m: 'within_1h_pct' },
    { l: 'Credit Notes', m: 'credit_notes_total' },
    { l: 'VDS to Claim', m: 'vds_unclaimed' }
  ],
  groups: [
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
      { id: 'M20-refunds', en: 'Credit Notes & Refunds', bn: 'ক্রেডিট নোট', t: 'g' }
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
  'M20-vds-register': { kind: 'table_report', module: 'M20', report: 'vds_claim_register' },
};

/* built-in report chips -> the screen that shows that report */
export const REPORT_ROUTES = {
  "M20:AR Ageing by Segment": "M20-aging",
  "M20:Dunning Effectiveness": "M20-dunning",
  "M20:Payment Method Mix": "M20-receipts",
  "M20:Invoice Accuracy": "M20-refunds",
  "M20:Brand Receivable Ageing": "M20-brand",
  "M20:Collections Productivity": "M20-dunning",
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

/* the module's "+ New" surface */
export const CREATE = {
  M20: { model: 'fix.ar.invoice', label: 'AR Invoice' },
};
