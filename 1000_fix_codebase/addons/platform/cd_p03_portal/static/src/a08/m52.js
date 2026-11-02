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
  'M52-rpt-tds': { kind: 'table_report', module: 'M52', report: 'tds_register', title: 'TDS / VDS Deduction Register', period: false },
  'M52-rpt-runs': { kind: 'table_report', module: 'M52', report: 'payment_run_summary', title: 'Payment Run Summary', period: false },

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
          { name: 'operating_unit_id', required: true, label: 'Operating Unit' }
        ] }
    ],
    lines: {
      field: 'line_ids',
      title: 'Invoice Lines — quantity, unit price and the product claimed against the PO',
      note: 'The three-way match compares these lines (product, quantity, price) with the purchase order and the goods receipt; an unmatched bill never reaches payment.',
      fields: [
        { name: 'product_id', required: true, label: 'Product' },
        { name: 'description', required: true, label: 'Description' },
        { name: 'quantity', required: true, label: 'Quantity' },
        { name: 'unit_price', required: true, label: 'Unit Price' }
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
      { title: 'Claim Header', note: 'Submission runs the expense policy: per-line and per-day limits by category and employee grade; breaches are recorded on the claim, and only accounting can approve or pay.',
        fields: [
          { name: 'description', required: true, label: 'Description' },
          { name: 'employee_id', required: true, label: 'Employee' },
          { name: 'expense_date', required: true, label: 'Expense Date' },
          { name: 'advance_id', label: 'Settles Advance' },
          { name: 'operating_unit_id', required: true, label: 'Operating Unit' },
          { name: 'amount', label: 'Claimed Amount (no lines)' }
        ] }
    ],
    lines: {
      field: 'line_ids',
      title: 'Expense Lines — per-diem and mileage come from the rate master',
      note: 'Quantity is days (per-diem) or kilometres (mileage) or 1 for actual cost; the rate master fills the unit amount for per-diem and mileage lines, and the policy limits are checked per line and per day for the employee’s grade.',
      fields: [
        { name: 'category_id', required: true, label: 'Category' },
        { name: 'date', required: true, label: 'Date' },
        { name: 'quantity', required: true, label: 'Days / km / qty' },
        { name: 'unit_amount', label: 'Unit Amount (rate)' },
        { name: 'description', label: 'Detail' }
      ]
    }
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
          { name: 'operating_unit_id', required: true, label: 'Operating Unit' }
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
          { name: 'description', label: 'Description' }
        ] }
    ]
  },

  'M52-form-taxprofile': {
    kind: 'model_form',
    model: 'fix.vendor.tax.profile',
    title: 'Vendor Tax Profile',
    back: 'M52-taxprofile',
    sections: [
      { title: 'Tax Identity', note: 'One profile per vendor per company. The PSR proof drives the non-filer TDS multiplier; a turnover-enlisted vendor’s invoices do not support input VAT credit.',
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
      { title: 'Return-Filing Proof (PSR)', fields: [
          { name: 'psr_reference', label: 'PSR Reference' },
          { name: 'psr_valid_until', label: 'PSR Valid Until' }
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
    sections: [
      { title: "AP Approval Rule", note: "The value band and role ladder that decide who approves an AP document.",
        fields: [
          { name: 'company_id', required: true, label: "Company" },
          { name: 'name', required: true, label: "Name" },
          { name: 'level', required: true, label: "Level" },
          { name: 'currency_id', required: true, label: "Currency" },
          { name: 'amount_min', required: true, label: "Applies From (gross)" },
          { name: 'group_id', required: true, label: "Approver Group" },
          { name: 'active', label: "Active" }
        ] }
    ]
  },
  'M52-form-aprun': {
    kind: 'model_form',
    model: 'fix.payment.run',
    title: "Payment Run",
    back: 'M52-runs',
    sections: [
      { title: "Payment Run", note: "A payment run: the documents selected, the total and the bank file produced.",
        fields: [
          { name: 'company_id', required: true, label: "Company" },
          { name: 'rail', required: true, label: "Rail" },
          { name: 'payment_date', required: true, label: "Payment Date" },
          { name: 'due_by', required: true, label: "Bills Due By" },
          { name: 'currency_id', required: true, label: "Currency" },
          { name: 'state', required: true, label: "State" }
        ] }
    ]
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
  'M52:Vendor Bill': 'fix.vendor.invoice',
  'M52:Expense Claim': 'fix.expense.claim',
  'M52:Employee Advance': 'fix.employee.advance',
  'M52:Debit Note': 'fix.vendor.note',
  'M52:Vendor Tax Profile': 'fix.vendor.tax.profile',
};

export const FORM_CHIPS = {
  'M52:AP Approval Rule': 'M52-form-aprule',
  'M52:Payment Run': 'M52-form-aprun',
  'M52:Vendor Bill': 'M52-form-bill',
  'M52:Expense Claim': 'M52-form-claim',
  'M52:Employee Advance': 'M52-form-advance',
  'M52:Debit Note': 'M52-form-note',
  'M52:Vendor Tax Profile': 'M52-form-taxprofile',
  'M52:__by_model__': {
    'fix.expense.category': 'M52-form-expense-category',
    'fix.expense.grade': 'M52-form-expense-grade',
    'fix.ap.approval.rule': 'M52-form-aprule',
    'fix.payment.run': 'M52-form-aprun',
    'fix.vendor.invoice': 'M52-form-bill',
    'fix.expense.claim': 'M52-form-claim',
    'fix.employee.advance': 'M52-form-advance',
    'fix.vendor.note': 'M52-form-note',
    'fix.vendor.tax.profile': 'M52-form-taxprofile',
    'fix.expense.rate': 'M52-form-rate',
    'fix.expense.policy': 'M52-form-policy'
  },
  'M52:__by_screen__': {
    'M52-expense-category': 'M52-form-expense-category',
    'M52-expense-grade': 'M52-form-expense-grade',
    'M52-matrix': 'M52-form-aprule',
    'M52-runs': 'M52-form-aprun',
    'M52-bills': 'M52-form-bill',
    'M52-claims': 'M52-form-claim',
    'M52-advances': 'M52-form-advance',
    'M52-notes': 'M52-form-note',
    'M52-taxprofile': 'M52-form-taxprofile',
    'M52-perdiem': 'M52-form-rate',
    'M52-policy': 'M52-form-policy'
  }
};

/* the module's "+ New" surface */
export const CREATE = {
  M52: { screen: 'M52-form-bill', model: 'fix.vendor.invoice', label: 'Vendor Bill' },
};
