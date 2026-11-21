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
    { l: 'Payables Open', m: 'payables_open', prefix: '৳ ' },
    { l: 'Bills To Approve', m: 'bills_to_approve' },
    { l: 'Payment Runs Open', m: 'payment_runs_open' },
    { l: 'Match Exceptions', m: 'match_exceptions' },
    { l: 'Expense Claims Pending', m: 'expense_claims_pending' },
    { l: 'TDS MTD', m: 'tds_mtd', prefix: '৳ ' },
    { l: 'Duplicate Catches YTD', m: 'duplicate_catches_ytd' }
  ],
  groups: [
    { en: 'Record Coverage', screens: [
      { id: 'M52-expense-category', en: "Expense Category", bn: "Expense Category", t: 'g' },
      { id: 'M52-expense-grade', en: "Expense Grade", bn: "Expense Grade", t: 'g' }
    ]},
    { en: 'Vendor Payables', screens: [
      { id: 'M52-bills', en: 'Vendor Bills', bn: 'বিক্রেতার বিল', t: 'g' },
      { id: 'M52-match', en: 'Match Exceptions', bn: 'মিল ব্যতিক্রম', t: 'g' },
      { id: 'M52-match-cases', en: 'Match Exception Cases', bn: 'মিল ব্যতিক্রমের কেস', t: 'g' },
      { id: 'M52-tolerances', en: 'Match Tolerances', bn: 'মিলের সহনসীমা', t: 'g' },
      { id: 'M52-approval', en: 'Approval Workflow', bn: 'অনুমোদন', t: 'g' },
      { id: 'M52-matrix', en: 'Approval Matrix', bn: 'অনুমোদন ম্যাট্রিক্স', t: 'g' },
      { id: 'M52-matrix-change', en: 'Matrix Change Requests', bn: 'ম্যাট্রিক্স পরিবর্তনের অনুরোধ', t: 'g' },
      { id: 'M52-taxprofile', en: 'Vendor Tax Profile', bn: 'বিক্রেতার কর প্রোফাইল', t: 'g' },
      { id: 'M52-disputes', en: 'Vendor Disputes', bn: 'বিক্রেতার বিরোধ', t: 'g' },
      { id: 'M52-vstatements', en: 'Vendor Statement Reconciliation', bn: 'বিক্রেতার বিবরণী মিলকরণ', t: 'g' },
      { id: 'M52-ageing-snapshots', en: 'Ageing Snapshots', bn: 'বয়স বিশ্লেষণের স্থির চিত্র', t: 'g' }
    ]},
    { en: 'Payments', screens: [
      { id: 'M52-bank-queue', en: 'Bank Accounts to Confirm', bn: 'নিশ্চিতকরণের অপেক্ষায় ব্যাংক হিসাব', t: 'g' },
      { id: 'M52-bank-changes', en: 'Payee Bank Changes', bn: 'প্রাপকের ব্যাংক পরিবর্তন', t: 'g' },
      { id: 'M52-runs', en: 'Payment Runs', bn: 'পেমেন্ট রান', t: 'g' },
      { id: 'M52-tds', en: 'TDS / VDS at Source', bn: 'উৎসে কর', t: 'g' },
      { id: 'M52-notes', en: 'Debit / Credit Notes', bn: 'ডেবিট ও ক্রেডিট নোট', t: 'g' }
    ]},
    { en: 'Employee Expense', screens: [
      { id: 'M52-claims', en: 'Expense Claims', bn: 'খরচের দাবি', t: 'g' },
      { id: 'M52-claim-lines', en: 'Claim Lines & Receipts', bn: 'দাবির লাইন ও রসিদ', t: 'g' },
      { id: 'M52-advances', en: 'Advances & Floats', bn: 'অগ্রিম', t: 'g' },
      { id: 'M52-perdiem', en: 'Per-Diem & Mileage', bn: 'ভাতা ও মাইলেজ', t: 'g' },
      { id: 'M52-policy', en: 'Expense Policy', bn: 'নীতি', t: 'g' },
      { id: 'M52-cards', en: 'Corporate & Fuel Cards', bn: 'কর্পোরেট ও জ্বালানি কার্ড', t: 'g' },
      { id: 'M52-card-lines', en: 'Card Statement Lines', bn: 'কার্ড বিবরণীর লাইন', t: 'g' }
    ]},
    { en: 'Analysis', screens: [
      { id: 'M52-aging', en: 'AP Ageing', bn: 'প্রদেয় বয়স', t: 'r' },
      { id: 'M52-grni', en: 'GRNI Accruals', bn: 'জিআরএনআই', t: 'r' },
      { id: 'M52-grni-accruals', en: 'GRNI Period-End Accruals', bn: 'জিআরএনআই মেয়াদান্ত উপচিতি', t: 'g' },
      { id: 'M52-expcat', en: 'Expense by Category', bn: 'খাত অনুযায়ী ব্যয়', t: 'r' },
      { id: 'M52-dupes', en: 'Duplicate Prevention Log', bn: 'দ্বৈত বিল প্রতিরোধ', t: 'r' }
    ]},
    /* 2026-11-09 accounts_payable report §5.4 (W3/W5): the legacy 200101
     * AP register take-on — voucher-level open items on a dedicated
     * non-reconcileable legacy control account, staged from the export
     * workbook through the governed M19 funnel. Operational screens beyond
     * the nav registry, per the M29 precedent. */
    { en: 'Legacy Take-on', screens: [
      { id: 'M52-ap-takeon', en: 'AP Register Take-on Wizard', bn: 'এপি রেজিস্টার টেক-অন উইজার্ড', t: 'g' },
      { id: 'M52-ap-takeon-lines', en: 'AP Take-on Vouchers (audit)', bn: 'টেক-অন ভাউচার (অডিট)', t: 'g' }
    ]}
  ],
  reports: ['AP Ageing', 'TDS Deduction Register', 'Payment Run Summary', 'Expense by Category', 'GRNI Reconciliation', 'Duplicate Prevention Log'],
  forms: ['Vendor Bill', 'Expense Claim', 'Employee Advance', 'Debit Note', 'Vendor Tax Profile',
    /* M52 capture audit 2026-11-17 */
    'Match Exception Case', 'Match Tolerance', 'Matrix Change Request', 'Vendor Dispute',
    'Vendor Statement Reconciliation', 'Ageing Snapshot', 'Legacy AP Register Take-on', 'Payment Run',
    'Payee Bank Change', 'Expense Policy Limit', 'Per-Diem / Mileage Rate', 'Expense Category',
    'Expense Grade', 'Card', 'Card Statement Line', 'GRNI Accrual'],
  cross: ['Procurement & Sourcing', 'Treasury & Banking', 'Tax & Regulatory (BD)'],
  freg: { src: 82, sub: [
    ['1', 'Invoice Capture', 10, { model: 'fix.vendor.invoice', cols: ['vendor_id', 'invoice_ref', 'invoice_date', 'due_date', 'total_payable'], screens: ['M52-bills', 'M52-dupes'], reports: ['Duplicate Prevention Log'], forms: ['Vendor Bill'] }],
    /* M52 capture audit 2026-11-17: every page captures the records it covers.
     * Matching works blocked bills as exception cases under approved
     * tolerances; Approval proposes matrix changes; the Payable Ledger keeps
     * disputes, vendor statement reconciliations and ageing snapshots; GRNI
     * keeps the period-end accrual; cards sit with advances. */
    ['2', 'Matching', 11, { model: 'fix.ap.match.exception', cols: ['name', 'invoice_id', 'vendor_id', 'exception_type', 'responsible_party', 'owner_id', 'due_date', 'state'], screens: ['M52-match', 'M52-match-cases', 'M52-tolerances'], reports: ['GRNI Reconciliation'], forms: ['Match Exception Case', 'Match Tolerance'], create: 'M52-form-matchcase' }],
    ['3', 'Approval', 8, { model: 'fix.vendor.invoice', cols: ['vendor_id', 'invoice_ref', 'gross_amount', 'approval_level', 'approval_state'], screens: ['M52-approval', 'M52-matrix', 'M52-matrix-change'], reports: [], forms: ['Matrix Change Request'], create: 'M52-form-matrix-change', domain: [['approval_state', '!=', 'draft']] }],
    ['4', 'Payable Ledger', 8, { model: 'fix.vendor.invoice', cols: ['vendor_id', 'invoice_ref', 'due_date', 'total_payable', 'payment_state'], screens: ['M52-aging', 'M52-notes', 'M52-disputes', 'M52-vstatements', 'M52-ageing-snapshots', 'M52-ap-takeon', 'M52-ap-takeon-lines'], reports: ['AP Ageing'], forms: ['Debit Note', 'Vendor Dispute', 'Vendor Statement Reconciliation', 'Ageing Snapshot', 'Legacy AP Register Take-on'], create: 'M52-form-note', domain: [['payment_state', '!=', 'paid']] }],
    ['5', 'Payment Runs', 9, { model: 'fix.payment.run', cols: ['name', 'rail', 'payment_date', 'total_amount', 'state'], screens: ['M52-runs', 'M52-bank-queue', 'M52-bank-changes'], reports: ['Payment Run Summary'], forms: ['Payment Run', 'Payee Bank Change'] }],
    ['6', 'TDS/VDS', 9, { model: 'fix.withholding.line', cols: ['document_date', 'tax_kind', 'partner_id', 'amount', 'state'], screens: ['M52-tds', 'M52-taxprofile'], reports: ['TDS Deduction Register'], forms: ['Vendor Tax Profile'], create: 'M52-form-taxprofile' }],
    ['7', 'Employee Expenses', 14, { model: 'fix.expense.claim', cols: ['employee_id', 'description', 'expense_date', 'amount', 'state'], screens: ['M52-claims', 'M52-claim-lines', 'M52-policy', 'M52-perdiem', 'M52-expense-category', 'M52-expense-grade', 'M52-expcat'], reports: ['Expense by Category'], forms: ['Expense Claim', 'Expense Policy Limit', 'Per-Diem / Mileage Rate', 'Expense Category', 'Expense Grade'] }],
    ['8', 'Advances & Cards', 8, { model: 'fix.employee.advance', cols: ['employee_id', 'advance_type', 'amount', 'balance', 'state'], screens: ['M52-advances', 'M52-cards', 'M52-card-lines'], reports: [], forms: ['Employee Advance', 'Supplier Advance', 'Card', 'Card Statement Line'] }],
    ['9', 'GRNI', 5, { model: 'fix.ap.grni.accrual', cols: ['name', 'period_end', 'grni_total', 'clearing_balance', 'unrecorded_estimate', 'state'], screens: ['M52-grni-accruals', 'M52-grni'], reports: ['GRNI Reconciliation'], forms: ['GRNI Accrual'], create: 'M52-form-grni' }]
  ] }
};

/* in-workspace data screens (checked before any stock Odoo view) */
export const SCREENS = {
  'M52-bills': { kind: 'model_list', model: 'fix.vendor.invoice',
    cols: ['vendor_id','invoice_ref','invoice_date','due_date','gross_amount','tds_amount','vds_amount','advance_applied','total_payable','tds_category_review','match_state','approval_state','payment_state'],
    stateField: 'approval_state',
    actions: [{m:'action_submit_approval',l:'Submit for Approval'},{m:'action_confirm_tds_category',l:'Confirm Defaulted TDS Category'},{m:'action_request_payment',l:'Request Payment'},{m:'action_fix_print',l:'🖨 Print Vendor Bill (PDF)'}] },
  'M52-match': { kind: 'model_list', model: 'fix.vendor.invoice', create: false,
    cols: ['vendor_id','invoice_ref','invoice_date','total_payable','match_state','match_detail','open_match_case_id'],
    stateField: 'match_state', domain: [['match_state','in',['unmatched','blocked']]],
    actions: [{m:'action_open_match_case',l:'Open Exception Case'}] },
  'M52-approval': { kind: 'model_list', model: 'fix.vendor.invoice', create: false,
    cols: ['vendor_id','invoice_ref','invoice_date','gross_amount','approval_level','approval_levels_required','submitted_by','approval_state'],
    stateField: 'approval_state', domain: [['approval_state','!=','draft']],
    actions: [{m:'action_approve',l:'Approve Level'},{m:'action_reject',l:'Reject'},{m:'action_reset_draft',l:'Reset to Draft'}] },
  'M52-matrix': { empty: 'The approval matrix changes only through an approved rule change (Approval Matrix Changes).', kind: 'model_list', model: 'fix.ap.approval.rule', create: false,
    cols: ['level','name','amount_min','group_id','active'] },
  'M52-matrix-change': { kind: 'model_list', model: 'fix.ap.approval.rule.change',
    cols: ['rule_id','name','level','amount_min','group_id','active','reason','proposed_by_id','decided_by_id','state'],
    stateField: 'state',
    actions: [{m:'action_apply',l:'Confirm & Apply'},{m:'action_reject',l:'Reject'}] },
  'M52-bank-queue': { kind: 'model_list', model: 'fix.payee.bank.change',
    cols: ['name','partner_id','partner_bank_id','acc_number','bank_id','routing_number','verification_ref','verified_by_id','evidence_names','proposed_by_id','state'],
    stateField: 'state', domain: [['state','in',['draft','proposed']]],
    actions: [{m:'action_propose',l:'Propose (call-back recorded)'},{m:'action_confirm',l:'Confirm (second person)'},{m:'action_reject',l:'Reject',ask:'Why is this bank change rejected?',kwarg:'reason'}] },
  'M52-bank-changes': { kind: 'model_list', model: 'fix.payee.bank.change',
    cols: ['name','partner_id','acc_number','verification_ref','proposed_by_id','confirmed_by_id','confirmed_at','reject_reason','state'],
    stateField: 'state' },
  'M52-taxprofile': { kind: 'model_list', model: 'fix.vendor.tax.profile',
    cols: ['partner_id','tin','bin','taxpayer_type','psr_reference','psr_valid_until','psr_valid','turnover_enlisted'] },
  'M52-runs': { kind: 'model_list', model: 'fix.payment.run',
    cols: ['name','rail','payment_date','due_by','bill_count','total_tds','total_vds','total_amount','prepared_by','approved_by','state'],
    stateField: 'state',
    actions: [{m:'action_propose',l:'Build Proposal'},{m:'action_submit',l:'Submit'},{m:'action_approve',l:'Approve'},{m:'action_release',l:'Release to Bank'},{m:'action_sync_bank_status',l:'Read Bank Status'},{m:'action_cancel',l:'Cancel'}] },
  'M52-tds': { empty: 'Withholding lines are calculated when a vendor bill is approved; they are not typed in.', kind: 'model_list', model: 'fix.withholding.line', create: false,
    cols: ['document_date','tax_kind','partner_id','section','base_amount','rate','multiplier','amount','source_ref','challan_no','state'],
    stateField: 'state', actions: [{m:'action_issue_certificate',l:'Issue Certificate'}] },
  'M52-notes': { kind: 'model_list', model: 'fix.vendor.note',
    cols: ['name','vendor_id','note_type','mushak_ref','note_date','amount','vat_amount','tds_amount','signed_total','state'],
    stateField: 'state', actions: [{m:'action_approve',l:'Approve & Post'},{m:'action_cancel',l:'Cancel'}] },
  'M52-claims': { kind: 'model_list', model: 'fix.expense.claim',
    cols: ['employee_id','description','expense_date','amount','advance_id','payment_failure','state'],
    stateField: 'state', actions: [{m:'action_submit',l:'Submit'},{m:'action_manager_approve',l:'Line Manager Approve'},{m:'action_approve',l:'Finance Approve'},{m:'action_reject',l:'Reject'}] },
  'M52-advances': { kind: 'model_list', model: 'fix.employee.advance',
    cols: ['name','employee_id','advance_type','purpose','amount','settled_amount','recovered_amount','balance','recovery_state','state'],
    stateField: 'state',
    actions: [{m:'action_approve',l:'Approve'},{m:'action_confirm_disbursement',l:'Confirm Disbursement'},{m:'action_sync_disbursement',l:'Read Bank Status'},{m:'action_settle',l:'Settle Against Claims'},{m:'action_record_recovery',l:'Recover Balance'},
      {m:'action_confirm_payroll_recovery',l:'Confirm Payroll Deduction',asks:[{label:'Amount payroll deducted',kwarg:'amount',number:true},{label:'Payslip or payroll run reference',kwarg:'reference'}]},
      {m:'action_cancel',l:'Cancel',ask:'Why is this advance cancelled?',kwarg:'reason'}] },
  'M52-claim-lines': { empty: 'Claim lines are entered on their expense claim.', kind: 'model_list', model: 'fix.expense.claim.line', create: false,
    cols: ['claim_id','category_id','date','description','cost_centre','quantity','unit_amount','amount','receipt_names'] },
  'M52-perdiem': { kind: 'model_list', model: 'fix.expense.rate',
    cols: ['rate_type','grade_id','location','vehicle','rate','date_from','date_to'] },
  'M52-policy': { kind: 'model_list', model: 'fix.expense.policy',
    cols: ['category_id','grade_id','limit_per_line','limit_per_day','receipt_required_above','blocked'] },
  'M52-aging': { kind: 'table_report', module: 'M52', report: 'ap_ageing', period: false },
  'M52-grni': { kind: 'table_report', module: 'M52', report: 'grni_accruals', period: false },
  'M52-expcat': { kind: 'table_report', module: 'M52', report: 'expense_by_category' },
  'M52-dupes': { kind: 'table_report', module: 'M52', report: 'duplicate_bills', period: false },
  'M52-rpt-tds': { kind: 'table_report', module: 'M52', report: 'tds_register', title: 'TDS / VDS Deduction Register', period: false },
  'M52-rpt-runs': { kind: 'table_report', module: 'M52', report: 'payment_run_summary', title: 'Payment Run Summary', period: false },

  /* Legacy AP register take-on (accounts_payable report 2026-11-09 §5.4) —
   * the 200101 open-items register (297 vouchers) staged, validated and
   * posted at GL level; the companion lane to M19's partner-ledger take-on
   * and the legacy AR control archive. */
  'M52-ap-takeon': { kind: 'model_list', model: 'fix.ap.takeon.batch', create: true,
    cols: ['name', 'state', 'takeon_date', 'line_count', 'ready_count', 'quarantined_count', 'posted_count', 'total_open', 'posted_move_id'],
    stateField: 'state',
    actions: [
      { m: 'action_stage', l: '1. Stage register spreadsheet' },
      { m: 'action_validate', l: '2. Validate & crosswalk branches' },
      { m: 'action_post', l: '3. Post opening entry' },
      { m: 'action_rollback', l: 'Rollback (mirror entry)' },
    ] },
  'M52-ap-takeon-lines': { empty: 'Take-on lines are imported from the legacy payables file staged on its batch; they are not typed in.', kind: 'model_list', model: 'fix.ap.takeon.line', create: false,
    cols: ['row_no', 'legacy_ref', 'source_ref_note', 'legacy_date', 'legacy_branch', 'branch_id', 'legacy_created_by', 'legacy_created_on', 'debit', 'credit', 'balance', 'line_state'],
    stateField: 'line_state' },
  'M52-form-ap-takeon': {
    kind: 'model_form', model: 'fix.ap.takeon.batch',
    title: 'Legacy AP Register Take-on', back: 'M52-ap-takeon',
    status: { field: 'state', labels: {
      draft: 'Draft', staged: 'Staged', validated: 'Validated',
      posted: 'Opening Entry Posted', rolled_back: 'Rolled Back' } },
    tabs: [
      { id: 'src', label: '1. Source & Date', bn: '১. সোর্স ও তারিখ', icon: '📄', badge: '5' },
      { id: 'out', label: '2. Outcome', bn: '২. ফলাফল', icon: '📊', badge: '6' },
      { id: 'log', label: '3. Decision Log', bn: '৩. সিদ্ধান্ত লগ', icon: '🗂️', badge: '1' }
    ],
    sections: [
      { tab: 'src', title: 'Legacy Register & Cut-over Date',
        note: "Attach the legacy AP ledger statement (Date / Journal Entry / Branch / Company / Created by / Created on / Debit / Credit / Balance — the 200101 Account Payable open-items register). Save, then run Stage → Validate → Post from the list's command bar. Posting writes one voucher-level credit entry on a dedicated non-reconcileable legacy control account through the governed M19 funnel — the register's debits ARE payables, and the live payable control stays owned by the partner take-on (no double count).",
        fields: [
          { name: 'name', label: 'Take-on', readonly: true },
          { name: 'source_file', label: 'Legacy AP Register (.xlsx)', type: 'file' },
          { name: 'source_filename', label: 'File Name' },
          { name: 'import_ref', label: 'Import Reference', required: true },
          { name: 'legacy_account_code', label: 'Source Ledger Account Code', required: true },
          { name: 'takeon_date', label: 'Cut-over Date (period boundary)', required: true },
          { name: 'control_account_id', label: 'Posting Target Account (default: dedicated legacy control)' },
          { name: 'contra_account_id', label: 'Take-on Contra Account' }
        ] },
      { tab: 'out', title: 'Counts & Open Position',
        fields: [
          { name: 'line_count', label: 'Register Rows', readonly: true },
          { name: 'ready_count', label: 'Ready To Post', readonly: true },
          { name: 'quarantined_count', label: 'Quarantined (identity/zero/duplicate)', readonly: true },
          { name: 'posted_count', label: 'Posted Vouchers', readonly: true },
          { name: 'total_open', label: 'Net Open Position', readonly: true },
          { name: 'posted_move_id', label: 'Opening Entry', readonly: true }
        ] },
      { tab: 'log', title: 'Decision Log',
        fields: [
          { name: 'decision_log', label: 'Staging / Validation / Posting Log', type: 'text', readonly: true }
        ] }
    ]
  },

  /* ============ D365 IN-WORKSPACE FORM SCREENS (M52 re-audit v2) ========
   * Every data-entry chip opens a Dynamics-365 record form inside the
   * workspace — never an Odoo dialog. Header + child lines save in ONE
   * request; the models' own constraints (3-way match block, duplicate
   * refusal, policy checks) apply server-side. */
  'M52-form-bill': {
    kind: 'model_form',
    model: 'fix.vendor.invoice',
    title: 'Vendor Bill',
    back: 'M52-bills',
    status: { field: 'approval_state', labels: {
      draft: 'Draft', to_approve: 'To Approve', approved: 'Approved', rejected: 'Rejected' } },
    sections: [
      { title: 'Bill Header', note: 'A PO bill is BLOCKED until the three-way match clears (PO vs receipt vs invoice); a non-PO service bill is controlled by the approval matrix instead. A vendor+reference that matches a live bill is refused at submission.',
        fields: [
          { name: 'invoice_ref', required: true, label: 'Vendor Invoice Ref' },
          { name: 'vendor_id', required: true, label: 'Vendor' },
          { name: 'bill_type', required: true, label: 'Bill Type' },
          { name: 'requisition_id', label: 'Purchase Order' },
          { name: 'invoice_date', required: true, label: 'Invoice Date' },
          { name: 'payment_term_days', label: 'Payment Terms (days)' },
          { name: 'supplier_mushak_no', label: 'Supplier Mushak 6.3 No' },
          { name: 'vat_amount', label: 'Input VAT (6.3)' },
          { name: 'vds_rate_id', label: 'VDS Service Code (empty: the vendor default, or no VDS)' },
          { name: 'payment_channel', required: true, label: 'Payment Channel' },
          { name: 'operating_unit_id', required: true, label: 'Operating Unit' }
        ] }
    ],
    lines: {
      field: 'line_ids',
      title: 'Invoice Lines — quantity, unit price and the product claimed against the PO',
      note: 'The three-way match compares these lines (product, quantity, price) with the purchase order and the goods receipt; an unmatched bill never reaches payment. TDS comes from the category’s rate in the M51 master; an exemption counts only with the certificate on the vendor’s tax profile.',
      fields: [
        { name: 'product_id', required: true, label: 'Product' },
        { name: 'description', required: true, label: 'Description' },
        { name: 'quantity', required: true, label: 'Quantity' },
        { name: 'unit_price', required: true, label: 'Unit Price' },
        { name: 'tds_category', label: 'TDS Category' },
        { name: 'tds_category_assumed', label: 'Category Defaulted (review)', readonly: true },
        { name: 'tds_exempt', label: 'TDS Exempt' },
        { name: 'cwip_id', label: 'CWIP Project (capital purchase)' }
      ]
    }
  },

  'M52-form-claim': {
    kind: 'model_form',
    model: 'fix.expense.claim',
    title: 'Expense Claim',
    back: 'M52-claims',
    status: { field: 'state', labels: {
      draft: 'Draft', submitted: 'Submitted', approved: 'Approved', paid: 'Paid', rejected: 'Rejected' } },
    sections: [
      { title: 'Claim Header', note: 'A claim is its lines: submission runs the expense policy (limits by category and grade, receipts, a receipt claimed once). The line manager approves, then accounting; claims in a 30-day window are summed for the manager threshold.',
        fields: [
          { name: 'description', required: true, label: 'Description' },
          { name: 'employee_id', required: true, label: 'Employee' },
          { name: 'expense_date', required: true, label: 'Expense Date' },
          { name: 'advance_id', label: 'Settles Advance' },
          { name: 'operating_unit_id', required: true, label: 'Operating Unit' },
          { name: 'amount', readonly: true, label: 'Claimed Amount (sum of the lines)' }
        ] }
    ],
    lines: {
      field: 'line_ids',
      title: 'Expense Lines — per-diem and mileage come from the rate master',
      note: 'Quantity is days (per-diem) or kilometres (mileage) or 1 for actual cost; the rate master fills the unit amount for per-diem and mileage lines, and the policy limits are checked per line and per day for the employee’s grade. Every line names its cost centre. Save, then attach each receipt on Claim Lines & Receipts: above the policy’s amount a claim does not submit without one.',
      fields: [
        { name: 'category_id', required: true, label: 'Category' },
        { name: 'date', required: true, label: 'Date' },
        { name: 'quantity', required: true, label: 'Days / km / qty' },
        { name: 'unit_amount', label: 'Unit Amount (rate)' },
        { name: 'cost_centre', required: true, label: 'Cost Centre' },
        { name: 'location', label: 'Per-Diem Location' },
        { name: 'vehicle', label: 'Vehicle' },
        { name: 'description', label: 'Detail' }
      ]
    }
  },

  'M52-form-claim-line': {
    kind: 'model_form',
    model: 'fix.expense.claim.line',
    title: 'Claim Line & Receipt',
    back: 'M52-claim-lines',
    sections: [
      { title: 'Expense Line', note: 'The lines of a submitted claim no longer change. A receipt is reimbursed once: the same file on another live claim is refused at submission.',
        fields: [
          { name: 'claim_id', readonly: true, label: 'Claim' },
          { name: 'category_id', required: true, label: 'Category' },
          { name: 'date', required: true, label: 'Date' },
          { name: 'quantity', required: true, label: 'Days / km / qty' },
          { name: 'unit_amount', label: 'Unit Amount (rate)' },
          { name: 'amount', readonly: true, label: 'Amount' },
          { name: 'cost_centre', required: true, label: 'Cost Centre' },
          { name: 'location', label: 'Per-Diem Location' },
          { name: 'vehicle', label: 'Vehicle' },
          { name: 'description', label: 'Detail' }
        ] },
      { title: 'Receipt',
        fields: [
          { name: 'receipt_file', type: 'binary', filename: 'receipt_filename', accept: '.pdf,.jpg,.jpeg,.png', label: 'Upload Receipt' },
          { name: 'receipt_filename', label: 'Receipt File Name' },
          { name: 'receipt_names', readonly: true, label: 'Receipts Attached' }
        ] }
    ]
  },

  'M52-form-bank-change': {
    kind: 'model_form',
    model: 'fix.payee.bank.change',
    title: 'Payee Bank Change',
    back: 'M52-bank-queue',
    status: { field: 'state', labels: { draft: 'Draft', proposed: 'Proposed', confirmed: 'Confirmed', rejected: 'Rejected' } },
    tabs: [
      { id: 'account', label: 'Account', bn: 'হিসাব', icon: '🏦' },
      { id: 'callback', label: 'Call-Back Evidence', bn: 'কল-ব্যাক প্রমাণ', icon: '📞' },
      { id: 'decision', label: 'Decision', bn: 'সিদ্ধান্ত', icon: '✅' }
    ],
    sections: [
      { tab: 'account', title: 'Account', note: 'An account is not payable until a second person confirms it. Unconfirmed accounts queue here by themselves; complete the call-back on the row, or raise a new or changed account with + New. An M42 supplier’s account changes through the supplier bank-detail change request instead.',
        fields: [
          { name: 'partner_id', required: true, label: 'Payee' },
          { name: 'partner_bank_id', label: 'Account To Confirm / Change (empty: a new account)' },
          { name: 'acc_number', required: true, label: 'Account / Wallet Number' },
          { name: 'bank_id', label: 'Bank' },
          { name: 'routing_number', label: 'BEFTN Routing Number' },
          { name: 'acc_holder_name', label: 'Account Holder' }
        ] },
      { tab: 'callback', title: 'Call-Back Evidence', note: 'Who was called, on which independently known number, when, and what they confirmed. Required to propose. The confirming accounting manager is someone other than the proposer, the caller and the last person to change the account.',
        fields: [
          { name: 'verification_ref', type: 'text', required: true, label: 'Call-Back Verification' },
          { name: 'verified_by_id', label: 'Call-Back Made By' },
          { name: 'evidence_file', type: 'binary', filename: 'evidence_filename', label: 'Upload Evidence' },
          { name: 'evidence_filename', label: 'Evidence File Name' },
          { name: 'evidence_names', readonly: true, label: 'Evidence Attached' }
        ] },
      { tab: 'decision', title: 'Decision',
        fields: [
          { name: 'proposed_by_id', readonly: true, label: 'Proposed By' },
          { name: 'proposed_at', readonly: true, label: 'Proposed On' },
          { name: 'confirmed_by_id', readonly: true, label: 'Confirmed By' },
          { name: 'confirmed_at', readonly: true, label: 'Confirmed On' },
          { name: 'reject_reason', readonly: true, label: 'Rejected Because' },
          { name: 'result_bank_id', readonly: true, label: 'Confirmed Account' },
          { name: 'state', readonly: true, label: 'State' }
        ] }
    ]
  },

  'M52-form-matrix-change': {
    kind: 'model_form',
    model: 'fix.ap.approval.rule.change',
    title: 'Matrix Change Request',
    back: 'M52-matrix-change',
    status: { field: 'state', labels: { proposed: 'Proposed', applied: 'Applied', rejected: 'Rejected' } },
    sections: [
      { title: 'Proposed Row', note: 'Saving proposes the change; another accounting manager confirms it, and only that writes the matrix. Name the row to change, or leave Matrix Row empty to add one. For an existing row, what you leave empty stays as it is.',
        fields: [
          { name: 'rule_id', label: 'Matrix Row (empty: a new row)' },
          { name: 'name', label: 'New Name' },
          { name: 'level', label: 'New Level' },
          { name: 'amount_min', label: 'New Applies From (gross)' },
          { name: 'group_id', label: 'New Approver Group' },
          { name: 'active', label: 'Row Active' },
          { name: 'reason', type: 'text', required: true, label: 'Reason' }
        ] },
      { title: 'Decision',
        fields: [
          { name: 'proposed_by_id', readonly: true, label: 'Proposed By' },
          { name: 'decided_by_id', readonly: true, label: 'Decided By' },
          { name: 'decided_at', readonly: true, label: 'Decided On' },
          { name: 'state', readonly: true, label: 'State' }
        ] }
    ]
  },

  'M52-form-advance': {
    kind: 'model_form',
    model: 'fix.employee.advance',
    title: 'Employee Advance',
    back: 'M52-advances',
    status: { field: 'state', labels: {
      draft: 'Draft', approved: 'Approved', disbursed: 'Disbursed', settled: 'Settled', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Advance / Float', note: 'Draft → approved → disbursed → settled. Approved claims raised against the advance settle it; an unspent balance is recovered by cash refund or payroll deduction.',
        fields: [
          { name: 'employee_id', required: true, label: 'Employee' },
          { name: 'advance_type', required: true, label: 'Type' },
          { name: 'purpose', required: true, label: 'Purpose' },
          { name: 'amount', required: true, label: 'Amount' },
          { name: 'request_date', required: true, label: 'Request Date' },
          { name: 'settle_by', label: 'Settle By' },
          { name: 'recovery_method', label: 'Recovery Method' },
          { name: 'operating_unit_id', required: true, label: 'Operating Unit' },
          { name: 'recovery_state', readonly: true, label: 'Recovery' },
          { name: 'recovery_requested_amount', readonly: true, label: 'Payroll Deduction Requested' },
          { name: 'cancel_reason', readonly: true, label: 'Cancelled Because' }
        ] }
    ]
  },

  'M52-form-note': {
    kind: 'model_form',
    model: 'fix.vendor.note',
    title: 'Debit / Credit Note',
    back: 'M52-notes',
    status: { field: 'state', labels: {
      draft: 'Draft', approved: 'Approved & Posted', applied: 'Netted in Payment Run', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Vendor Note (Mushak 6.7 / 6.8)', note: 'A credit note (6.7) reduces the payable; a debit note (6.8) increases it. The reference number is printed on the vendor note.',
        fields: [
          { name: 'invoice_id', required: true, label: 'Bill' },
          { name: 'note_type', required: true, label: 'Note Type' },
          { name: 'mushak_ref', label: 'Mushak 6.7 / 6.8 No' },
          { name: 'note_date', required: true, label: 'Note Date' },
          { name: 'reason', required: true, label: 'Reason' },
          { name: 'amount', required: true, label: 'Value (excl. VAT)' },
          { name: 'vat_amount', label: 'VAT' },
          { name: 'description', label: 'Description' },
          { name: 'source_ref', label: 'Return Document (RTV)', readonly: true },
          { name: 'return_qty', label: 'Returned Quantity', readonly: true },
          { name: 'tds_amount', label: 'TDS Reversed', readonly: true },
          { name: 'signed_total', label: 'Effect on Payable', readonly: true }
        ] }
    ]
  },

  'M52-form-taxprofile': {
    kind: 'model_form',
    model: 'fix.vendor.tax.profile',
    title: 'Vendor Tax Profile',
    back: 'M52-taxprofile',
    tabs: [
      { id: 'identity', label: 'Tax Identity', bn: 'কর পরিচিতি' },
      { id: 'psr', label: 'Return-Filing Proof (PSR)', bn: 'রিটার্ন দাখিলের প্রমাণ' },
      { id: 'exempt', label: 'TDS Exemption', bn: 'টিডিএস অব্যাহতি' }
    ],
    sections: [
      { tab: 'identity', title: 'Tax Identity', note: 'One profile per vendor per company. The PSR proof drives the non-filer TDS multiplier; a turnover-enlisted vendor’s invoices do not support input VAT credit.',
        fields: [
          { name: 'partner_id', required: true, label: 'Vendor' },
          { name: 'tin', label: 'TIN (e-TIN)' },
          { name: 'bin', label: 'BIN' },
          { name: 'taxpayer_type', required: true, label: 'Taxpayer Type' },
          { name: 'default_tds_category', label: 'Default TDS Category' },
          { name: 'default_vds_rate_id', label: 'Default VDS Service Code' },
          { name: 'vds_exempt', label: 'VDS Not Applicable' },
          { name: 'turnover_enlisted', label: 'Turnover-Tax Enlisted' }
        ] },
      { tab: 'psr', title: 'Return-Filing Proof (PSR)', note: 'The vendor counts as a filer only with a TIN, the reference, an expiry not yet passed and the proof attached.',
        fields: [
          { name: 'psr_reference', label: 'PSR Reference' },
          { name: 'psr_valid_until', label: 'PSR Valid Until' },
          { name: 'psr_evidence_file', type: 'binary', filename: 'psr_evidence_filename', label: 'Upload PSR Proof' },
          { name: 'psr_evidence_filename', label: 'PSR File Name' },
          { name: 'psr_evidence_names', readonly: true, label: 'PSR Proof Attached' },
          { name: 'psr_valid', readonly: true, label: 'PSR Valid Today' }
        ] },
      { tab: 'exempt', title: 'TDS Exemption Certificate', note: 'A bill line ticked TDS Exempt counts only with the certificate number, its expiry and the file here, valid on the invoice date.',
        fields: [
          { name: 'tds_exempt_certificate_ref', label: 'TDS Exemption Certificate No' },
          { name: 'tds_exempt_valid_until', label: 'Exemption Valid Until' },
          { name: 'tds_exempt_file', type: 'binary', filename: 'tds_exempt_filename', label: 'Upload Exemption Certificate' },
          { name: 'tds_exempt_filename', label: 'Certificate File Name' },
          { name: 'tds_exempt_names', readonly: true, label: 'Certificate Attached' }
        ] }
    ]
  },

  'M52-form-rate': {
    kind: 'model_form',
    model: 'fix.expense.rate',
    title: 'Per-Diem / Mileage Rate',
    back: 'M52-perdiem',
    sections: [
      { title: 'Rate', note: 'Effective-dated per-diem and mileage rates by grade, location and vehicle; claims are computed from the rate valid on the expense date.',
        fields: [
          { name: 'rate_type', required: true, label: 'Rate Type' },
          { name: 'grade_id', label: 'Grade (empty = all)' },
          { name: 'location', label: 'Location' },
          { name: 'vehicle', label: 'Vehicle' },
          { name: 'rate', required: true, label: 'Rate' },
          { name: 'date_from', required: true, label: 'Valid From' },
          { name: 'date_to', label: 'Valid To' }
        ] }
    ]
  },

  'M52-form-policy': {
    kind: 'model_form',
    model: 'fix.expense.policy',
    title: 'Expense Policy Limit',
    back: 'M52-policy',
    sections: [
      { title: 'Policy', note: '0 = no limit. A category can be blocked outright; above the receipt threshold a receipt attachment is required. A grade-specific row beats the all-grades row.',
        fields: [
          { name: 'category_id', required: true, label: 'Category' },
          { name: 'grade_id', label: 'Grade (empty = all)' },
          { name: 'limit_per_line', label: 'Limit per Expense' },
          { name: 'limit_per_day', label: 'Limit per Day' },
          { name: 'receipt_required_above', label: 'Receipt Required Above' },
          { name: 'blocked', label: 'Not Reimbursable' }
        ] }
    ]
  },


  /* ===== master-data forms (batch 2) — D365 in-workspace ===== */
  'M52-form-aprule': {
    kind: 'model_form',
    model: 'fix.ap.approval.rule',
    title: "AP Approval Rule",
    back: 'M52-matrix',
    create: false, pick: 'An approval rule changes only through an approved rule change: open one from Approval Matrix.',
    sections: [
      { title: "AP Approval Rule", note: "The value band and role ladder that decide who approves a vendor bill. Read-only here: a matrix row changes through a matrix change request proposed by one accounting manager and confirmed by another (A08 M52-12).",
        fields: [
          { name: 'company_id', readonly: true, label: "Company" },
          { name: 'name', readonly: true, label: "Name" },
          { name: 'level', readonly: true, label: "Level" },
          { name: 'currency_id', readonly: true, label: "Currency" },
          { name: 'amount_min', readonly: true, label: "Applies From (gross)" },
          { name: 'group_id', readonly: true, label: "Approver Group" },
          { name: 'active', readonly: true, label: "Active" }
        ] }
    ]
  },
  'M52-form-aprun': {
    kind: 'model_form',
    model: 'fix.payment.run',
    title: "Payment Run",
    back: 'M52-runs',
    sections: [
      { title: "Payment Run", note: "Propose, submit, approve and release are actions (three different people prepare, approve and release). The approval pins each line's payee account, amount and bills; a later change voids it.",
        fields: [
          { name: 'company_id', required: true, label: "Company" },
          { name: 'rail', required: true, label: "Rail" },
          { name: 'payment_date', required: true, label: "Payment Date" },
          { name: 'due_by', required: true, label: "Bills Due By" },
          { name: 'currency_id', required: true, label: "Currency" },
          { name: 'state', readonly: true, label: "State" }
        ] }
    ],
    lines: {
      field: 'line_ids',
      title: 'Payees in this run',
      note: 'Build Proposal fills these. A payee with no confirmed bank account is Skipped with its reason and stays in the pool for the next run: confirm the account under Bank Accounts to Confirm.',
      readonlyGrid: true,
      fields: [
        { name: 'partner_id', readonly: true, label: 'Payee' },
        { name: 'bank_account_id', readonly: true, label: 'Bank Account' },
        { name: 'gross_amount', readonly: true, label: 'Bills Gross' },
        { name: 'tds_amount', readonly: true, label: 'TDS' },
        { name: 'amount', readonly: true, label: 'To Pay' },
        { name: 'state', readonly: true, label: 'State' },
        { name: 'skip_reason', readonly: true, label: 'Why Skipped' }
      ]
    }
  },


  /* ===== triage coverage screens ===== */
  'M52-expense-category': { kind: 'model_list', model: 'fix.expense.category',
    cols: ['name', 'code', 'active', 'company_id', 'operating_unit_id', 'line_type', 'account_id'] },
  'M52-expense-grade': { kind: 'model_list', model: 'fix.expense.grade',
    cols: ['name', 'active', 'company_id', 'operating_unit_id', 'sequence'] },

  'M52-form-expense-category': {
    kind: 'model_form',
    model: 'fix.expense.category',
    title: "Expense Category",
    back: 'M52-expense-category',
    sections: [
      { title: "Expense Category", note: "Opened from the module's own record set. Every field here is the model's real field; the workflow rules live on the model and are not bypassed by this form.",
        fields: [
          { name: 'name', required: true, label: "Name" },
          { name: 'code', required: true, label: "Code" },
          { name: 'company_id', required: true, label: "Company" },
          { name: 'line_type', required: true, label: "Line Type" },
          { name: 'active', label: "Active" },
          { name: 'operating_unit_id', label: "Operating Unit" },
          { name: 'account_id', label: "Expense Account" }
        ] }
    ]
  },
  'M52-form-expense-grade': {
    kind: 'model_form',
    model: 'fix.expense.grade',
    title: "Expense Grade",
    back: 'M52-expense-grade',
    sections: [
      { title: "Expense Grade", note: "Opened from the module's own record set. Every field here is the model's real field; the workflow rules live on the model and are not bypassed by this form.",
        fields: [
          { name: 'name', required: true, label: "Name" },
          { name: 'company_id', required: true, label: "Company" },
          { name: 'active', label: "Active" },
          { name: 'operating_unit_id', label: "Operating Unit" },
          { name: 'sequence', label: "Sequence" }
        ] }
    ]
  },

  /* ============ M52 capture audit (2026-11-17) ============ */
  'M52-match-cases': { kind: 'model_list', model: 'fix.ap.match.exception',
    cols: ['name','invoice_id','vendor_id','purchase_order_id','exception_type','responsible_party','owner_id','due_date','age_days','bill_match_state','resolution_code','state'],
    stateField: 'state',
    empty: 'No match exception case. A case is opened for every blocked purchase-order bill (Open Exception Case on Match Exceptions, or the daily check).',
    actions: [{m:'action_resolve',l:'Resolve (cause fixed)',states:['open']}] },
  'M52-tolerances': { kind: 'model_list', model: 'fix.ap.match.tolerance',
    cols: ['name','category_id','amount_from','qty_pct','price_pct','price_abs','effective_from','requested_by_id','approved_by_id','state'],
    stateField: 'state',
    empty: 'No match tolerance: purchase-order bills match exactly (quantity) and to 0.01 (price).',
    actions: [{m:'action_submit',l:'Submit',states:['draft']},{m:'action_approve',l:'Approve (second person)',states:['submitted']},{m:'action_reject',l:'Reject',states:['submitted']}] },
  'M52-disputes': { kind: 'model_list', model: 'fix.ap.dispute',
    cols: ['name','invoice_id','vendor_id','disputed_amount','reason_code','owner_id','raised_by_id','outcome','note_id','state'],
    stateField: 'state',
    actions: [{m:'action_resolve',l:'Resolve (second person)',states:['open']},{m:'action_withdraw',l:'Withdraw',states:['open']}] },
  'M52-vstatements': { kind: 'model_list', model: 'fix.ap.vendor.statement',
    cols: ['name','partner_id','statement_date','statement_balance','ledger_balance','difference','open_bill_count','prepared_by_id','signed_by_id','state'],
    stateField: 'state',
    actions: [{m:'action_compare',l:'Compare with Ledger',states:['draft','compared']},{m:'action_sign_off',l:'Sign Off (second person)',states:['compared']}] },
  'M52-ageing-snapshots': { kind: 'model_list', model: 'fix.ap.ageing.snapshot',
    cols: ['name','as_of','note','current','d1_30','d31_60','d61_90','d90','total','vendor_count','taken_by_id','taken_at'],
    empty: 'No ageing snapshot kept yet. Take one at each period close: it is never changed afterwards.' },
  'M52-grni-accruals': { kind: 'model_list', model: 'fix.ap.grni.accrual',
    cols: ['name','period_end','line_count','grni_total','clearing_balance','unrecorded_estimate','computed_by_id','confirmed_by_id','state'],
    stateField: 'state',
    actions: [{m:'action_compute',l:'Compute from Receipts',states:['draft','computed']},{m:'action_confirm',l:'Confirm (second person)',states:['computed']}] },
  'M52-cards': { kind: 'model_list', model: 'fix.expense.card',
    cols: ['name','card_type','issuer','last_digits','holder_id','monthly_limit','valid_to','unexplained_count','active'] },
  'M52-card-lines': { kind: 'model_list', model: 'fix.expense.card.transaction',
    cols: ['card_id','holder_id','txn_date','merchant','amount','statement_ref','category_id','cost_centre','approved_by_id','state'],
    stateField: 'state',
    actions: [{m:'action_explain',l:'Explained (receipt + coding)',states:['unexplained','explained']},{m:'action_approve',l:'Approve (finance)',states:['explained']},{m:'action_dispute',l:'Dispute with Issuer',states:['unexplained','explained']},{m:'action_reopen',l:'Reopen',states:['explained','disputed']}] },

  'M52-form-matchcase': {
    kind: 'model_form', model: 'fix.ap.match.exception',
    title: 'Match Exception Case', back: 'M52-match-cases',
    status: { field: 'state', labels: { open: 'Open', resolved: 'Resolved' } },
    tabs: [
      { id: 'case', label: 'Case', bn: 'কেস', icon: '🧾' },
      { id: 'work', label: 'Work & Resolution', bn: 'কাজ ও সমাধান', icon: '🛠️' }
    ],
    sections: [
      { tab: 'case', title: 'Blocked Bill', note: 'A blocked purchase-order bill stays recorded as a liability; only its payment is stopped. The case names who must fix the cause (the buyer for a price, the receiver for a receipt, the vendor for the bill) and by when.',
        fields: [
          { name: 'name', readonly: true, label: 'Case' },
          { name: 'invoice_id', required: true, label: 'Bill' },
          { name: 'vendor_id', readonly: true, label: 'Vendor' },
          { name: 'purchase_order_id', readonly: true, label: 'Purchase Order' },
          { name: 'bill_match_state', readonly: true, label: 'Bill Match Now' },
          { name: 'variance_detail', readonly: true, type: 'text', label: 'Variance When Opened' },
          { name: 'exception_type', required: true, label: 'Exception Type' },
          { name: 'responsible_party', required: true, label: 'Responsible Party' },
          { name: 'owner_id', required: true, label: 'Owner' },
          { name: 'due_date', required: true, label: 'Resolve By' }
        ] },
      { tab: 'work', title: 'Work & Resolution', note: 'The case closes only when its cause is fixed: the receipt is posted, the PO corrected, the bill corrected or credited, or the bill rejected. The match itself is never overridden.',
        fields: [
          { name: 'action_note', type: 'text', label: 'Actions Taken' },
          { name: 'resolution_code', label: 'Resolution' },
          { name: 'resolution_note', type: 'text', label: 'Resolution Note' },
          { name: 'age_days', readonly: true, label: 'Age (days)' },
          { name: 'resolved_by_id', readonly: true, label: 'Resolved By' },
          { name: 'resolved_at', readonly: true, label: 'Resolved On' }
        ] }
    ]
  },
  'M52-form-tolerance': {
    kind: 'model_form', model: 'fix.ap.match.tolerance',
    title: 'Match Tolerance', back: 'M52-tolerances',
    status: { field: 'state', labels: { draft: 'Draft', submitted: 'Awaiting Approval', active: 'Active', superseded: 'Superseded', rejected: 'Rejected' } },
    tabs: [
      { id: 'scope', label: 'Scope & Limits', bn: 'পরিধি ও সীমা', icon: '📏' },
      { id: 'decision', label: 'Decision', bn: 'সিদ্ধান্ত', icon: '✅' }
    ],
    sections: [
      { tab: 'scope', title: 'Where It Applies and How Far', note: 'The most specific active row applies: the product\u2019s own category (or a parent) beats all categories, then the highest value band the bill reaches. With both a percentage and an amount on price, the smaller allowance applies. Approved by an Accounting Administrator other than the requester; a change is a new row that replaces this one.',
        fields: [
          { name: 'category_id', label: 'Product Category (empty: all)' },
          { name: 'amount_from', label: 'Bills From (gross)' },
          { name: 'qty_pct', label: 'Quantity Over Receipt (%)' },
          { name: 'price_pct', label: 'Unit Price Over PO (%)' },
          { name: 'price_abs', label: 'Unit Price Over PO (amount per unit)' },
          { name: 'effective_from', required: true, label: 'Effective From' },
          { name: 'reason', type: 'text', required: true, label: 'Reason' }
        ] },
      { tab: 'decision', title: 'Decision',
        fields: [
          { name: 'supersedes_id', readonly: true, label: 'Replaces' },
          { name: 'requested_by_id', readonly: true, label: 'Requested By' },
          { name: 'requested_at', readonly: true, label: 'Requested On' },
          { name: 'approved_by_id', readonly: true, label: 'Decided By' },
          { name: 'approved_at', readonly: true, label: 'Decided On' }
        ] }
    ]
  },
  'M52-form-dispute': {
    kind: 'model_form', model: 'fix.ap.dispute',
    title: 'Vendor Dispute', back: 'M52-disputes',
    status: { field: 'state', labels: { open: 'Open: Payment Held', resolved: 'Resolved', withdrawn: 'Withdrawn' } },
    tabs: [
      { id: 'dispute', label: 'Dispute', bn: 'বিরোধ', icon: '⚖️' },
      { id: 'outcome', label: 'Outcome', bn: 'ফলাফল', icon: '✅' }
    ],
    sections: [
      { tab: 'dispute', title: 'What Is Disputed', note: 'While the dispute is open the bill is held from payment runs and payment requests. Payment status is per bill, so the whole bill waits for the dispute to close.',
        fields: [
          { name: 'name', readonly: true, label: 'Dispute' },
          { name: 'invoice_id', required: true, label: 'Bill' },
          { name: 'vendor_id', readonly: true, label: 'Vendor' },
          { name: 'bill_payable', readonly: true, label: 'Bill Payable' },
          { name: 'disputed_amount', required: true, label: 'Disputed Amount' },
          { name: 'reason_code', required: true, label: 'Reason' },
          { name: 'description', type: 'text', required: true, label: 'Description' },
          { name: 'vendor_ref', label: 'Vendor\u2019s Reference' },
          { name: 'owner_id', required: true, label: 'Owner' }
        ] },
      { tab: 'outcome', title: 'Outcome', note: 'Resolved by someone other than the person who raised it. An upheld dispute is settled by the vendor\u2019s credit note on the same bill, approved.',
        fields: [
          { name: 'outcome', label: 'Outcome' },
          { name: 'note_id', label: 'Vendor Credit Note' },
          { name: 'resolution_note', type: 'text', label: 'How It Was Settled' },
          { name: 'raised_by_id', readonly: true, label: 'Raised By' },
          { name: 'raised_at', readonly: true, label: 'Raised On' },
          { name: 'resolved_by_id', readonly: true, label: 'Closed By' },
          { name: 'resolved_at', readonly: true, label: 'Closed On' }
        ] }
    ]
  },
  'M52-form-vstatement': {
    kind: 'model_form', model: 'fix.ap.vendor.statement',
    title: 'Vendor Statement Reconciliation', back: 'M52-vstatements',
    status: { field: 'state', labels: { draft: 'Draft', compared: 'Compared', signed: 'Signed Off' } },
    sections: [
      { title: 'Vendor\u2019s Statement', note: 'Enter the balance the vendor\u2019s statement says we owe and attach it, then Compare with Ledger: our balance is the approved, unpaid bills to that date, net of notes not yet netted, plus any legacy opening balance. A difference is explained item by item; another person signs off.',
        fields: [
          { name: 'name', readonly: true, label: 'Reconciliation' },
          { name: 'partner_id', required: true, label: 'Vendor' },
          { name: 'statement_date', required: true, label: 'Statement Date' },
          { name: 'statement_balance', required: true, label: 'Balance on the Vendor\u2019s Statement' },
          { name: 'statement_file', type: 'binary', filename: 'statement_filename', accept: '.pdf,.xlsx,.xls,.csv,.jpg,.jpeg,.png', label: 'Upload Statement' },
          { name: 'statement_filename', label: 'File Name' }
        ] },
      { title: 'Comparison',
        fields: [
          { name: 'ledger_balance', readonly: true, label: 'Our Ledger Balance' },
          { name: 'open_bill_count', readonly: true, label: 'Open Bills on Our Ledger' },
          { name: 'difference', readonly: true, label: 'Difference' },
          { name: 'reconciling_items', type: 'text', label: 'Reconciling Items' },
          { name: 'prepared_by_id', readonly: true, label: 'Compared By' },
          { name: 'signed_by_id', readonly: true, label: 'Signed Off By' }
        ] }
    ]
  },
  'M52-form-snapshot': {
    kind: 'model_form', model: 'fix.ap.ageing.snapshot',
    title: 'Ageing Snapshot', back: 'M52-ageing-snapshots',
    sections: [
      { title: 'Payables Ageing Kept at a Date', note: 'Saving takes the snapshot: the AP Ageing as of the date, vendor by vendor, frozen. It is never edited or deleted, so the period-close figure can always be shown again.',
        fields: [
          { name: 'as_of', required: true, label: 'As Of' },
          { name: 'note', label: 'Purpose (e.g. the close it belongs to)' },
          { name: 'name', readonly: true, label: 'Snapshot' },
          { name: 'total', readonly: true, label: 'Total Open' },
          { name: 'vendor_count', readonly: true, label: 'Vendors' },
          { name: 'taken_by_id', readonly: true, label: 'Taken By' },
          { name: 'taken_at', readonly: true, label: 'Taken On' },
          { name: 'basis', readonly: true, label: 'Opening Balances' }
        ] }
    ],
    lines: {
      field: 'line_ids', title: 'Vendors', readonlyGrid: true,
      fields: [
        { name: 'label', readonly: true, label: 'Vendor' },
        { name: 'current', readonly: true, label: 'Not Due' },
        { name: 'd1_30', readonly: true, label: '1-30' },
        { name: 'd31_60', readonly: true, label: '31-60' },
        { name: 'd61_90', readonly: true, label: '61-90' },
        { name: 'd90', readonly: true, label: '90+' },
        { name: 'total', readonly: true, label: 'Total' }
      ]
    }
  },
  'M52-form-grni': {
    kind: 'model_form', model: 'fix.ap.grni.accrual',
    title: 'GRNI Accrual', back: 'M52-grni-accruals',
    status: { field: 'state', labels: { draft: 'Draft', computed: 'Computed', confirmed: 'Confirmed' } },
    tabs: [
      { id: 'period', label: 'Period & Figures', bn: 'মেয়াদ ও অঙ্ক', icon: '📅' },
      { id: 'unrecorded', label: 'Unrecorded Liability', bn: 'অনিবন্ধিত দায়', icon: '📝' }
    ],
    sections: [
      { tab: 'period', title: 'Received Not Invoiced at the Period End', note: 'Save, then Compute from Receipts: every goods receipt not yet billed, at the purchase-order price, kept line by line, beside the balance of the GRNI clearing account. An Accounting Administrator other than the person who computed it confirms it; confirmed, it is kept as it was.',
        fields: [
          { name: 'name', readonly: true, label: 'Accrual' },
          { name: 'period_end', required: true, label: 'Period End' },
          { name: 'line_count', readonly: true, label: 'Receipt Lines' },
          { name: 'grni_total', readonly: true, label: 'Received Not Invoiced' },
          { name: 'clearing_balance', readonly: true, label: 'GRNI Clearing Account Balance' },
          { name: 'clearing_note', readonly: true, label: 'Clearing Account' },
          { name: 'computed_by_id', readonly: true, label: 'Computed By' },
          { name: 'confirmed_by_id', readonly: true, label: 'Confirmed By' }
        ] },
      { tab: 'unrecorded', title: 'Estimated Unrecorded Liability', note: 'Costs received with no bill and no purchase order (utilities, rent, couriers...). Give the basis of any estimate.',
        fields: [
          { name: 'unrecorded_estimate', label: 'Estimate' },
          { name: 'unrecorded_basis', type: 'text', label: 'Basis of the Estimate' }
        ] }
    ],
    lines: {
      field: 'line_ids', title: 'Receipts not yet billed', readonlyGrid: true,
      fields: [
        { name: 'order_ref', readonly: true, label: 'PO' },
        { name: 'vendor_id', readonly: true, label: 'Vendor' },
        { name: 'product_id', readonly: true, label: 'Product' },
        { name: 'open_qty', readonly: true, label: 'Not Invoiced' },
        { name: 'unit_price', readonly: true, label: 'PO Price' },
        { name: 'accrual', readonly: true, label: 'Accrual' },
        { name: 'received_on', readonly: true, label: 'Last Receipt' }
      ]
    }
  },
  'M52-form-card': {
    kind: 'model_form', model: 'fix.expense.card',
    title: 'Corporate / Fuel Card', back: 'M52-cards',
    sections: [
      { title: 'Card', note: 'Only the last four digits are kept. Spend on the card is explained line by line from the issuer\u2019s statement (Card Statement Lines); it is never also claimed for reimbursement.',
        fields: [
          { name: 'card_type', required: true, label: 'Card Type' },
          { name: 'issuer', required: true, label: 'Issuer (bank / fuel company)' },
          { name: 'last_digits', required: true, label: 'Last 4 Digits' },
          { name: 'holder_id', required: true, label: 'Cardholder' },
          { name: 'monthly_limit', label: 'Monthly Limit' },
          { name: 'valid_to', label: 'Expires' },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'active', label: 'Active' },
          { name: 'unexplained_count', readonly: true, label: 'Unexplained Lines' }
        ] }
    ]
  },
  'M52-form-cardline': {
    kind: 'model_form', model: 'fix.expense.card.transaction',
    title: 'Card Statement Line', back: 'M52-card-lines',
    status: { field: 'state', labels: { unexplained: 'Unexplained', explained: 'Explained', approved: 'Approved', disputed: 'Disputed with Issuer' } },
    tabs: [
      { id: 'line', label: 'Statement Line', bn: 'বিবরণীর লাইন', icon: '💳' },
      { id: 'explain', label: 'Explanation', bn: 'ব্যাখ্যা', icon: '🧾' }
    ],
    sections: [
      { tab: 'line', title: 'As the Issuer Printed It', note: 'Recorded once per statement reference and never changed.',
        fields: [
          { name: 'card_id', required: true, label: 'Card' },
          { name: 'holder_id', readonly: true, label: 'Cardholder' },
          { name: 'txn_date', required: true, label: 'Transaction Date' },
          { name: 'merchant', required: true, label: 'Merchant' },
          { name: 'amount', required: true, label: 'Amount' },
          { name: 'statement_ref', required: true, label: 'Statement Reference' }
        ] },
      { tab: 'explain', title: 'Explanation', note: 'The category, the cost centre or job, and the receipt. Finance approves, never the cardholder.',
        fields: [
          { name: 'category_id', label: 'Expense Category' },
          { name: 'cost_centre', label: 'Cost Centre / Job' },
          { name: 'purpose', label: 'Purpose' },
          { name: 'receipt_file', type: 'binary', filename: 'receipt_filename', accept: '.pdf,.jpg,.jpeg,.png', label: 'Upload Receipt' },
          { name: 'receipt_filename', label: 'Receipt File Name' },
          { name: 'approved_by_id', readonly: true, label: 'Approved By' },
          { name: 'approved_at', readonly: true, label: 'Approved On' }
        ] }
    ]
  },

};

/* built-in report chips -> the screen that shows that report */
export const REPORT_ROUTES = {
  "M52:AP Ageing": "M52-aging",
  "M52:TDS Deduction Register": "M52-rpt-tds",
  "M52:Payment Run Summary": "M52-rpt-runs",
  "M52:Expense by Category": "M52-expcat",
  "M52:GRNI Reconciliation": "M52-grni",
  "M52:Duplicate Prevention Log": "M52-dupes",
};

/* data-entry form chips -> real model forms */
export const FORM_MODELS = {
  'M52:Match Exception Case': 'fix.ap.match.exception',
  'M52:Match Tolerance': 'fix.ap.match.tolerance',
  'M52:Matrix Change Request': 'fix.ap.approval.rule.change',
  'M52:Vendor Dispute': 'fix.ap.dispute',
  'M52:Vendor Statement Reconciliation': 'fix.ap.vendor.statement',
  'M52:Ageing Snapshot': 'fix.ap.ageing.snapshot',
  'M52:Legacy AP Register Take-on': 'fix.ap.takeon.batch',
  'M52:Payment Run': 'fix.payment.run',
  'M52:Payee Bank Change': 'fix.payee.bank.change',
  'M52:Expense Policy Limit': 'fix.expense.policy',
  'M52:Per-Diem / Mileage Rate': 'fix.expense.rate',
  'M52:Expense Category': 'fix.expense.category',
  'M52:Expense Grade': 'fix.expense.grade',
  'M52:Card': 'fix.expense.card',
  'M52:Card Statement Line': 'fix.expense.card.transaction',
  'M52:GRNI Accrual': 'fix.ap.grni.accrual',
  'M52:Vendor Bill': 'fix.vendor.invoice',
  'M52:Expense Claim': 'fix.expense.claim',
  'M52:Employee Advance': 'fix.employee.advance',
  'M52:Debit Note': 'fix.vendor.note',
  'M52:Vendor Tax Profile': 'fix.vendor.tax.profile',
};

export const FORM_CHIPS = {
  'M52:AP Approval Rule': 'M52-form-aprule',
  'M52:Matrix Change Request': 'M52-form-matrix-change',
  'M52:Payee Bank Change': 'M52-form-bank-change',
  'M52:Payment Run': 'M52-form-aprun',
  'M52:Vendor Bill': 'M52-form-bill',
  'M52:Expense Claim': 'M52-form-claim',
  'M52:Employee Advance': 'M52-form-advance',
  'M52:Debit Note': 'M52-form-note',
  'M52:Vendor Tax Profile': 'M52-form-taxprofile',
  'M52:Match Exception Case': 'M52-form-matchcase',
  'M52:Match Tolerance': 'M52-form-tolerance',
  'M52:Vendor Dispute': 'M52-form-dispute',
  'M52:Vendor Statement Reconciliation': 'M52-form-vstatement',
  'M52:Ageing Snapshot': 'M52-form-snapshot',
  'M52:Legacy AP Register Take-on': 'M52-form-ap-takeon',
  'M52:Expense Policy Limit': 'M52-form-policy',
  'M52:Per-Diem / Mileage Rate': 'M52-form-rate',
  'M52:Expense Category': 'M52-form-expense-category',
  'M52:Expense Grade': 'M52-form-expense-grade',
  'M52:Card': 'M52-form-card',
  'M52:Card Statement Line': 'M52-form-cardline',
  'M52:GRNI Accrual': 'M52-form-grni',
  /* M16 owns the supplier advance; M52 pays it and takes it back on the bill */
  'M52:Supplier Advance': 'M16-form-advance',
  'M52:__by_model__': {
    'fix.expense.category': 'M52-form-expense-category',
    'fix.expense.grade': 'M52-form-expense-grade',
    'fix.ap.approval.rule': 'M52-form-aprule',
    'fix.ap.approval.rule.change': 'M52-form-matrix-change',
    'fix.payee.bank.change': 'M52-form-bank-change',
    'fix.expense.claim.line': 'M52-form-claim-line',
    'fix.payment.run': 'M52-form-aprun',
    'fix.vendor.invoice': 'M52-form-bill',
    'fix.expense.claim': 'M52-form-claim',
    'fix.employee.advance': 'M52-form-advance',
    'fix.vendor.note': 'M52-form-note',
    'fix.vendor.tax.profile': 'M52-form-taxprofile',
    'fix.expense.rate': 'M52-form-rate',
    'fix.expense.policy': 'M52-form-policy',
    'fix.ap.takeon.batch': 'M52-form-ap-takeon',
    'fix.ap.match.exception': 'M52-form-matchcase',
    'fix.ap.match.tolerance': 'M52-form-tolerance',
    'fix.ap.dispute': 'M52-form-dispute',
    'fix.ap.vendor.statement': 'M52-form-vstatement',
    'fix.ap.ageing.snapshot': 'M52-form-snapshot',
    'fix.ap.grni.accrual': 'M52-form-grni',
    'fix.expense.card': 'M52-form-card',
    'fix.expense.card.transaction': 'M52-form-cardline'
  },
  'M52:__by_screen__': {
    'M52-expense-category': 'M52-form-expense-category',
    'M52-expense-grade': 'M52-form-expense-grade',
    'M52-matrix': 'M52-form-aprule',
    'M52-matrix-change': 'M52-form-matrix-change',
    'M52-bank-queue': 'M52-form-bank-change',
    'M52-bank-changes': 'M52-form-bank-change',
    'M52-claim-lines': 'M52-form-claim-line',
    'M52-runs': 'M52-form-aprun',
    'M52-bills': 'M52-form-bill',
    'M52-claims': 'M52-form-claim',
    'M52-advances': 'M52-form-advance',
    'M52-notes': 'M52-form-note',
    'M52-taxprofile': 'M52-form-taxprofile',
    'M52-perdiem': 'M52-form-rate',
    'M52-policy': 'M52-form-policy',
    'M52-ap-takeon': 'M52-form-ap-takeon',
    'M52-match-cases': 'M52-form-matchcase',
    'M52-tolerances': 'M52-form-tolerance',
    'M52-disputes': 'M52-form-dispute',
    'M52-vstatements': 'M52-form-vstatement',
    'M52-ageing-snapshots': 'M52-form-snapshot',
    'M52-grni-accruals': 'M52-form-grni',
    'M52-cards': 'M52-form-card',
    'M52-card-lines': 'M52-form-cardline'
  }
};

/* the module's "+ New" surface */
export const CREATE = {
  M52: { screen: 'M52-form-bill', model: 'fix.vendor.invoice', label: 'Vendor Bill' },
};
