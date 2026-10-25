/** @odoo-module **/
/* A08 · Finance & Treasury — M52 AP & Employee Expense.
 * One file per A08 module (merged into P03_MODULES and the screen maps by
 * p03_modules_meta.js): the registry entry, the in-workspace data screens,
 * built-in report routes, data-entry form chips and the "+ New" surface.
 * Backend: controllers/a08/m52.py (SURFACES, kpis, REPORTS) over cd_ap_ext. */

export const MODULE = {
  area: 'A08', code: 'M52', en: 'AP & Employee Expense', title: 'M52 · AP & Employee Expense',
  bn: 'প্রদেয় ও ব্যয়', icon: '💸',
  desc: 'Vendor bills with 3-way match and an approval matrix, TDS/VDS at source, payment runs, employee expenses & advances.',
  kpis: [
    { l: 'Payables Open', m: 'vendor_bills_open' },
    { l: 'Bills To Approve', m: 'bills_to_approve' },
    { l: 'Match Exceptions', m: 'match_exceptions' },
    { l: 'Expense Claims Pending', m: 'expense_claims_pending' },
    { l: 'TDS MTD', m: 'tds_mtd' }
  ],
  groups: [
    { en: 'Vendor Payables', screens: [
      { id: 'M52-bills', en: 'Vendor Bills', bn: 'বিক্রেতার বিল', t: 'g' },
      { id: 'M52-match', en: 'Match Exceptions', bn: 'মিল ব্যতিক্রম', t: 'g' },
      { id: 'M52-approval', en: 'Approval Workflow', bn: 'অনুমোদন', t: 'c' },
      { id: 'M52-matrix', en: 'Approval Matrix', bn: 'অনুমোদন ম্যাট্রিক্স', t: 'g' },
      { id: 'M52-taxprofile', en: 'Vendor Tax Profile', bn: 'বিক্রেতার কর প্রোফাইল', t: 'g' }
    ]},
    { en: 'Payments', screens: [
      { id: 'M52-runs', en: 'Payment Runs', bn: 'পেমেন্ট রান', t: 'c' },
      { id: 'M52-tds', en: 'TDS / VDS at Source', bn: 'উৎসে কর', t: 'g' },
      { id: 'M52-notes', en: 'Debit / Credit Notes', bn: 'ডেবিট ও ক্রেডিট নোট', t: 'g' }
    ]},
    { en: 'Employee Expense', screens: [
      { id: 'M52-claims', en: 'Expense Claims', bn: 'খরচের দাবি', t: 'g' },
      { id: 'M52-advances', en: 'Advances & Floats', bn: 'অগ্রিম', t: 'g' },
      { id: 'M52-perdiem', en: 'Per-Diem & Mileage', bn: 'ভাতা ও মাইলেজ', t: 'g' },
      { id: 'M52-policy', en: 'Expense Policy', bn: 'নীতি', t: 'g' }
    ]},
    { en: 'Analysis', screens: [
      { id: 'M52-aging', en: 'AP Ageing', bn: 'প্রদেয় বয়স', t: 'r' },
      { id: 'M52-grni', en: 'GRNI Accruals', bn: 'জিআরএনআই', t: 'r' },
      { id: 'M52-expcat', en: 'Expense by Category', bn: 'খাত অনুযায়ী ব্যয়', t: 'r' },
      { id: 'M52-dupes', en: 'Duplicate Prevention Log', bn: 'দ্বৈত বিল প্রতিরোধ', t: 'r' }
    ]}
  ],
  reports: ['AP Ageing', 'TDS Deduction Register', 'Payment Run Summary', 'Expense by Category', 'GRNI Reconciliation', 'Duplicate Prevention Log'],
  forms: ['Vendor Bill', 'Expense Claim', 'Employee Advance', 'Debit Note', 'Vendor Tax Profile'],
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
    cols: ['vendor_id','invoice_ref','invoice_date','due_date','gross_amount','tds_amount','vds_amount','total_payable','match_state','approval_state','payment_state'],
    stateField: 'approval_state',
    actions: [{m:'action_submit_approval',l:'Submit for Approval'},{m:'action_request_payment',l:'Request Payment'}] },
  'M52-match': { kind: 'model_list', model: 'fix.vendor.invoice',
    cols: ['vendor_id','invoice_ref','invoice_date','total_payable','match_state','match_detail'],
    stateField: 'match_state', domain: [['match_state','in',['unmatched','blocked']]] },
  'M52-approval': { kind: 'model_list', model: 'fix.vendor.invoice',
    cols: ['vendor_id','invoice_ref','invoice_date','gross_amount','approval_level','approval_levels_required','submitted_by','approval_state'],
    stateField: 'approval_state', domain: [['approval_state','!=','draft']],
    actions: [{m:'action_approve',l:'Approve Level'},{m:'action_reject',l:'Reject'},{m:'action_reset_draft',l:'Reset to Draft'}] },
  'M52-matrix': { kind: 'model_list', model: 'fix.ap.approval.rule',
    cols: ['level','name','amount_min','group_id','active'] },
  'M52-taxprofile': { kind: 'model_list', model: 'fix.vendor.tax.profile',
    cols: ['partner_id','tin','bin','taxpayer_type','psr_reference','psr_valid_until','psr_valid','turnover_enlisted'] },
  'M52-runs': { kind: 'model_list', model: 'fix.payment.run',
    cols: ['name','rail','payment_date','due_by','bill_count','total_tds','total_vds','total_amount','prepared_by','approved_by','state'],
    stateField: 'state',
    actions: [{m:'action_propose',l:'Build Proposal'},{m:'action_submit',l:'Submit'},{m:'action_approve',l:'Approve'},{m:'action_release',l:'Release to Bank'},{m:'action_sync_bank_status',l:'Read Bank Status'},{m:'action_cancel',l:'Cancel'}] },
  'M52-tds': { kind: 'model_list', model: 'fix.withholding.line', create: false,
    cols: ['document_date','tax_kind','partner_id','section','base_amount','rate','multiplier','amount','source_ref','challan_no','state'],
    stateField: 'state', actions: [{m:'action_issue_certificate',l:'Issue Certificate'}] },
  'M52-notes': { kind: 'model_list', model: 'fix.vendor.note',
    cols: ['name','vendor_id','note_type','mushak_ref','note_date','amount','vat_amount','signed_total','state'],
    stateField: 'state', actions: [{m:'action_approve',l:'Approve & Post'},{m:'action_cancel',l:'Cancel'}] },
  'M52-claims': { kind: 'model_list', model: 'fix.expense.claim',
    cols: ['employee_id','description','expense_date','amount','advance_id','state'],
    stateField: 'state', actions: [{m:'action_submit',l:'Submit'},{m:'action_approve',l:'Approve'},{m:'action_reject',l:'Reject'}] },
  'M52-advances': { kind: 'model_list', model: 'fix.employee.advance',
    cols: ['name','employee_id','advance_type','purpose','amount','settled_amount','recovered_amount','balance','state'],
    stateField: 'state',
    actions: [{m:'action_approve',l:'Approve'},{m:'action_confirm_disbursement',l:'Confirm Disbursement'},{m:'action_settle',l:'Settle Against Claims'},{m:'action_record_recovery',l:'Recover Balance'}] },
  'M52-perdiem': { kind: 'model_list', model: 'fix.expense.rate',
    cols: ['rate_type','grade_id','location','vehicle','rate','date_from','date_to'] },
  'M52-policy': { kind: 'model_list', model: 'fix.expense.policy',
    cols: ['category_id','grade_id','limit_per_line','limit_per_day','receipt_required_above','blocked'] },
  'M52-aging': { kind: 'table_report', module: 'M52', report: 'ap_ageing', period: false },
  'M52-grni': { kind: 'table_report', module: 'M52', report: 'grni_accruals', period: false },
  'M52-expcat': { kind: 'table_report', module: 'M52', report: 'expense_by_category' },
  'M52-dupes': { kind: 'table_report', module: 'M52', report: 'duplicate_bills', period: false },
};

/* built-in report chips -> the screen that shows that report */
export const REPORT_ROUTES = {
  "M52:AP Ageing": "M52-aging",
  "M52:TDS Deduction Register": "M52-tds",
  "M52:Payment Run Summary": "M52-runs",
  "M52:Expense by Category": "M52-expcat",
  "M52:GRNI Reconciliation": "M52-grni",
  "M52:Duplicate Prevention Log": "M52-dupes",
};

/* data-entry form chips -> real model forms */
export const FORM_MODELS = {
  'M52:Vendor Bill': 'fix.vendor.invoice',
  'M52:Expense Claim': 'fix.expense.claim',
  'M52:Employee Advance': 'fix.employee.advance',
  'M52:Debit Note': 'fix.vendor.note',
  'M52:Vendor Tax Profile': 'fix.vendor.tax.profile',
};

/* the module's "+ New" surface */
export const CREATE = {
  M52: { model: 'fix.vendor.invoice', label: 'Vendor Bill' },
};
