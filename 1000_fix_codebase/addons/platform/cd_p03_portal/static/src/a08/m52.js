/** @odoo-module **/
/* A08 · Finance & Treasury — M52 AP & Employee Expense.
 * One file per A08 module (merged into P03_MODULES and the screen maps by
 * p03_modules_meta.js): the registry entry, the in-workspace data screens,
 * built-in report routes, data-entry form chips and the "+ New" surface. */

export const MODULE = {
  area: 'A08', code: 'M52', en: 'AP & Employee Expense', title: 'M52 · AP & Employee Expense',
  bn: 'প্রদেয় ও ব্যয়', icon: '💸',
  desc: 'Vendor invoices with 3-way match, TDS/VDS at source, employee expenses & advances, payment runs.',
  kpis: [
    { l: 'Payables Open', m: 'vendor_bills_open' },
    { l: 'Match Exceptions', m: 'match_exceptions' },
    { l: 'Expense Claims Pending', m: 'expense_claims_pending' },
    { l: 'TDS MTD' }
  ],
  groups: [
    { en: 'Vendor Payables', screens: [
      { id: 'M52-bills', en: 'Vendor Bills', bn: 'বিক্রেতার বিল', t: 'g' },
      { id: 'M52-match', en: 'Match Exceptions', bn: 'মিল ব্যতিক্রম', t: 'g' },
      { id: 'M52-approval', en: 'Approval Workflow', bn: 'অনুমোদন', t: 'c' }
    ]},
    { en: 'Payments', screens: [
      { id: 'M52-runs', en: 'Payment Runs', bn: 'পেমেন্ট রান', t: 'c' },
      { id: 'M52-tds', en: 'TDS / VDS at Source', bn: 'উৎসে কর', t: 'g' },
      { id: 'M52-notes', en: 'Debit / Credit Notes', bn: 'ডেবিট নোট', t: 'g' }
    ]},
    { en: 'Employee Expense', screens: [
      { id: 'M52-claims', en: 'Expense Claims', bn: 'খরচের দাবি', t: 'g' },
      { id: 'M52-advances', en: 'Advances & Floats', bn: 'অগ্রিম', t: 'g' },
      { id: 'M52-perdiem', en: 'Per-Diem & Mileage', bn: 'ভাতা ও মাইলেজ', t: 'g' },
      { id: 'M52-policy', en: 'Expense Policy', bn: 'নীতি', t: 'g' }
    ]},
    { en: 'Analysis', screens: [
      { id: 'M52-aging', en: 'AP Ageing', bn: 'প্রদেয় বয়স', t: 'r' },
      { id: 'M52-grni', en: 'GRNI Accruals', bn: 'জিআরএনআই', t: 'r' }
    ]}
  ],
  reports: ['AP Ageing', 'TDS Deduction Register', 'Payment Run Summary', 'Expense by Category', 'GRNI Reconciliation', 'Duplicate Prevention Log'],
  forms: ['Vendor Bill', 'Expense Claim', 'Employee Advance', 'Debit Note'],
  cross: ['Procurement & Sourcing', 'Treasury & Banking', 'Tax & Regulatory (BD)'],
  freg: { src: 82, sub: [
    ['1', 'Invoice Capture', 10], ['2', 'Matching', 11], ['3', 'Approval', 8],
    ['4', 'Payable Ledger', 8], ['5', 'Payment Runs', 9], ['6', 'TDS/VDS', 9],
    ['7', 'Employee Expenses', 14], ['8', 'Advances & Cards', 8], ['9', 'GRNI', 5]
  ] }
};

/* in-workspace data screens (checked before any stock Odoo view) */
export const SCREENS = {
  'M52-bills': { kind: 'model_list', model: 'fix.vendor.invoice',
    cols: ['vendor_id','invoice_ref','invoice_date','subtotal','tds_amount','total_payable','match_state'],
    stateField: 'match_state', actions: [{m:'action_request_payment',l:'Request Payment'}] },
  'M52-match': { kind: 'model_list', model: 'fix.vendor.invoice',
    cols: ['vendor_id','invoice_ref','invoice_date','total_payable','match_state','match_detail'],
    stateField: 'match_state', domain: [['match_state','!=','matched']] },
  'M52-claims': { kind: 'model_list', model: 'fix.expense.claim',
    cols: ['employee_id','description','expense_date','amount','state'],
    stateField: 'state', actions: [{m:'action_submit',l:'Submit'},{m:'action_approve',l:'Approve'}] },
};

/* built-in report chips -> the screen that shows that report */
export const REPORT_ROUTES = {
  "M52:AP Ageing": "M52-bills",
  "M52:TDS Deduction Register": "M52-bills",
  "M52:Payment Run Summary": "M52-bills",
  "M52:Expense by Category": "M52-claims",
  "M52:GRNI Reconciliation": "M52-match",
  "M52:Duplicate Prevention Log": "M52-match",
};

/* data-entry form chips -> real model forms */
export const FORM_MODELS = {
  'M52:Vendor Bill': 'fix.vendor.invoice',
  'M52:Expense Claim': 'fix.expense.claim',
};

/* the module's "+ New" surface */
export const CREATE = {
  M52: { model: 'fix.vendor.invoice', label: 'Vendor Bill' },
};
