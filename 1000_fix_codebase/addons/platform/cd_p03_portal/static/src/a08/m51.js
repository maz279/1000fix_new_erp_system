/** @odoo-module **/
/* A08 · Finance & Treasury — M51 Tax & Regulatory (BD).
 * One file per A08 module (merged into P03_MODULES and the screen maps by
 * p03_modules_meta.js): the registry entry, the in-workspace data screens,
 * built-in report routes, data-entry form chips and the "+ New" surface.
 * Backend: controllers/a08/m51.py (SURFACES, kpis, REPORTS) over
 * cd_tax_engine_bd. Rates, thresholds and due days are effective-dated
 * master data; rows seeded from secondary sources say "verify with adviser". */

export const MODULE = {
  area: 'A08', code: 'M51', en: 'Tax & Regulatory (BD)', title: 'M51 · Tax & Regulatory (BD)',
  bn: 'কর ও ভ্যাট', icon: '🏛️',
  desc: 'VAT 15%, Mushak 6.1–9.1 registers & returns, TDS/VDS, challans, Mushak 6.10, statutory calendar, audit pack.',
  kpis: [
    { l: 'Output VAT MTD', m: 'vat_collected_mtd' },
    { l: 'Latest Mushak 9.1', m: 'vat91_latest' },
    { l: 'Input Credit Open', m: 'input_credit_open' },
    { l: 'Certificates Due', m: 'certificates_due' },
    { l: 'Overdue Obligations', m: 'overdue_obligations' },
    { l: 'Withholding Undeposited', m: 'withholding_undeposited', prefix: '৳ ' },
    { l: 'Next Statutory Due', m: 'next_due' },
    { l: 'Mushak Records', m: 'mushak_records' },
    { l: 'VAT Returns', m: 'vat_returns_count' },
    { l: 'Rows Awaiting Sign-Off', m: 'signoff_pending' }
  ],
  groups: [
    { en: 'VAT', screens: [
      { id: 'M51-mushak61', en: 'Mushak 6.1 (Purchases)', bn: 'মুশক ৬.১ (ক্রয়)', t: 'g' },
      { id: 'M51-mushak62', en: 'Mushak 6.2 (Sales)', bn: 'মুশক ৬.২ (বিক্রয়)', t: 'g' },
      { id: 'M51-mushak63', en: 'Mushak 6.3 Records', bn: 'মুশক ৬.৩', t: 'g' },
      { id: 'M51-unclassified', en: 'Rows Blocking the 9.1', bn: 'শ্রেণিহীন সারি', t: 'g' },
      { id: 'M51-corrections', en: 'VAT Register Corrections', bn: 'রেজিস্টার সংশোধন', t: 'g' },
      { id: 'M51-vat91', en: 'VAT Return 9.1 Filing', bn: 'ভ্যাট রিটার্ন ৯.১', t: 'c' },
      { id: 'M51-challans', en: 'Challans (A-Challan)', bn: 'চালান', t: 'g' },
      { id: 'M51-input', en: 'Input Credit Tracking', bn: 'ইনপুট ক্রেডিট', t: 'g' }
    ]},
    { en: 'Withholding', screens: [
      { id: 'M51-tds', en: 'TDS Register', bn: 'টিডিএস রেজিস্টার', t: 'g' },
      { id: 'M51-tds-lines', en: 'TDS Deductions', bn: 'টিডিএস কর্তন', t: 'g' },
      { id: 'M51-vds', en: 'VDS (45 Services)', bn: 'ভিডিএস (মুশক ৬.৬)', t: 'g' },
      { id: 'M51-certs', en: 'Certificates', bn: 'সনদ', t: 'g' }
    ]},
    { en: 'Compliance', screens: [
      { id: 'M51-determination', en: 'Tax Determination Service', bn: 'কর নির্ধারণ', t: 'c' },
      { id: 'M51-nid', en: 'High-Value NID Capture', bn: 'মুশক ৬.১০ উচ্চমূল্য রেজিস্টার', t: 'r' },
      { id: 'M51-notes', en: 'Credit / Debit Note Register', bn: 'ক্রেডিট ও ডেবিট নোট রেজিস্টার', t: 'r' },
      { id: 'M51-calendar', en: 'Statutory Calendar', bn: 'বিধিবদ্ধ ক্যালেন্ডার', t: 'c' },
      { id: 'M51-audit', en: 'Audit Support Pack', bn: 'অডিট সহায়তা', t: 'r' }
    ]},
    { en: 'Master Data', screens: [
      { id: 'M51-signoff', en: 'Sign-Off Queue', bn: 'অনুমোদনের অপেক্ষায়', t: 'r' },
      { id: 'M51-rates', en: 'Tax Rate Master', bn: 'কর হার তালিকা', t: 'g' },
      { id: 'M51-params', en: 'Statutory Parameters', bn: 'বিধিবদ্ধ মানদণ্ড', t: 'g' },
      { id: 'M51-duerules', en: 'Statutory Calendar Rules', bn: 'বিধিবদ্ধ সময়সূচির নিয়ম', t: 'g' },
      { id: 'M51-filings', en: 'Filing Evidence', bn: 'দাখিলের প্রমাণ', t: 'g' }
    ]}
  ],
  reports: ['Mushak 9.1 Return Draft', 'VAT Reconciliation', 'TDS Annual Summary', 'VDS Deduction Register', 'Mushak 6.10 High-Value Register', 'Credit / Debit Note Register', 'Statutory Compliance Calendar'],
  forms: ['Challan', 'TDS Return', 'Input VAT Adjustment', 'Filing Evidence', 'Tax Rate', 'VAT Register Correction'],
  cross: ['AR, Invoicing & Collections', 'AP & Employee Expense', 'Financial Accounting & GL'],
  freg: { src: 78, sub: [
    ['1', 'Determination Service', 9, { model: 'fix.vat.treatment', cols: ['code', 'name', 'treatment_type', 'rate', 'active'], screens: ['M51-determination', 'M51-rates', 'M51-params', 'M51-signoff'] }],
    ['2', 'VAT Output/Input', 12, { model: 'fix.input.vat.credit', cols: ['partner_id', 'invoice_date', 'taxable_amount', 'vat_amount', 'state'], screens: ['M51-input', 'M51-mushak61'] }],
    ['3', 'Mushak Registers', 11, { model: 'fix.mushak.register', cols: ['mushak_no', 'invoice_ref', 'invoice_date', 'vat_amount', 'posted'], screens: ['M51-mushak62', 'M51-mushak63', 'M51-unclassified', 'M51-corrections', 'M51-notes'] }],
    ['4', 'VAT Return 9.1', 8, { model: 'fix.vat.return', cols: ['period', 'output_vat', 'input_vat', 'net_payable', 'state'], screens: ['M51-vat91'] }],
    ['5', 'VDS', 7, { model: 'fix.withholding.line', cols: ['document_date', 'partner_id', 'base_amount', 'amount', 'state'], screens: ['M51-vds', 'M51-tds-lines'], domain: [['tax_kind', '=', 'vds']] }],
    ['6', 'TDS', 12, { model: 'fix.tds.return', cols: ['quarter', 'fiscal_year', 'total_withheld', 'due_date', 'state'], screens: ['M51-tds'] }],
    ['7', 'Challans & Certificates', 7, { model: 'fix.tax.challan', cols: ['challan_no', 'challan_date', 'tax_kind', 'amount', 'state'], screens: ['M51-challans', 'M51-certs'] }],
    ['8', 'High-Value Register', 4, { model: 'fix.ar.receipt', cols: ['name', 'customer_id', 'receipt_date', 'amount', 'nid_captured'], screens: ['M51-nid'] }],
    ['9', 'Calendar & Audit', 8, { model: 'fix.statutory.due.rule', cols: ['obligation', 'name', 'frequency', 'due_day', 'roll_to_working_day'], screens: ['M51-calendar', 'M51-duerules', 'M51-filings', 'M51-audit'] }]
  ] }
};

/* A08 M51-6 (BRU-TAX-22): the adviser's written confirmation, then the CFO. */
const MASTER_ACTIONS = [
  {m:'action_record_adviser_verification',l:'Record Adviser Confirmation',ask:'Reference of the adviser\'s written confirmation',kwarg:'reference'},
  {m:'action_cfo_signoff',l:'CFO Sign-Off (Row in Force)'},
  {m:'action_activate',l:'Activate Proposal (CFO)'},
  {m:'action_reject_proposal',l:'Reject Proposal'}
];
/* A08 M51-4/-8: one person asks with a reason, a different Accounting
 * Administrator applies; which duplicate is voided stays a person's decision. */
const DEDUCTION_ACTIONS = [
  {m:'action_issue_certificate',l:'Issue Certificate'},
  {m:'action_request_void',l:'Request Void (Duplicate)',ask:'Why is this deduction the wrong copy?',kwarg:'reason'},
  {m:'action_request_reopen',l:'Request Reopen',ask:'Why does this deduction go back to withheld?',kwarg:'reason'},
  {m:'action_approve_correction',l:'Apply Correction (2nd Person)'},
  {m:'action_reject_correction',l:'Reject Correction',ask:'Why is the correction rejected?',kwarg:'reason'},
  {m:'action_clear_duplicate',l:'Not a Duplicate',ask:'Why are both deductions genuine?',kwarg:'reason'}
];

/* in-workspace data screens (checked before any stock Odoo view) */
export const SCREENS = {
  'M51-rpt-sdat': { kind: 'table_report', module: 'M51', report: 'sd_at_liability',
    title: 'SD & AT Liability', period: false },

  'M51-mushak61': { kind: 'model_list', model: 'fix.input.vat.credit', create: false,
    cols: ['invoice_date','partner_id','supplier_bin','supplier_mushak_no','adjustment_type','taxable_amount','vat_amount','claim_period','state'] },
  'M51-mushak62': { kind: 'model_list', model: 'fix.mushak.register', create: false,
    cols: ['mushak_no','invoice_ref','invoice_date','customer_name','customer_bin','taxable_amount','vat_amount','total_payable','vat_line','rate_flagged','posted'] },
  'M51-mushak63': { kind: 'model_list', model: 'fix.mushak.register', create: false,
    cols: ['mushak_no','row_type','invoice_ref','invoice_date','customer_name','taxable_amount','vat_amount','total_payable','vat_line','rate_flagged','original_id','posted'] },
  'M51-unclassified': { kind: 'model_list', model: 'fix.mushak.register', create: false,
    cols: ['mushak_no','invoice_ref','invoice_date','supplier_bin','customer_name','taxable_amount','vat_amount','vat_line','posted'],
    domain: [['vat_line','=like','unclassified%']] },
  'M51-corrections': { kind: 'model_list', model: 'fix.mushak.correction',
    cols: ['register_id','current_line','correction_type','treatment','taxable_amount','vat_amount','reason','requested_by_id','state','decided_by_id','note_id','rejection_reason'],
    stateField: 'state',
    actions: [{m:'action_approve',l:'Approve & Apply (2nd Person)'},{m:'action_reject',l:'Reject',ask:'Why is it rejected?',kwarg:'reason'}] },
  'M51-vat91': { kind: 'model_list', model: 'fix.vat.return',
    cols: ['period','total_taxable','output_vat','input_vat','vds_received_credit','net_payable','net_payable_after_vds','due_date','subledger_status','classification_notes','state','filed_at','nbr_confirmation'],
    stateField: 'state',
    actions: [{m:'action_prepare',l:'Prepare from Registers'},{m:'action_subledger_reconciliation',l:'Reconcile Sub-Ledger'},{m:'action_file_online',l:'File Online (NBR)'}] },
  'M51-challans': { kind: 'model_list', model: 'fix.tax.challan',
    cols: ['challan_no','challan_date','tax_kind','period','bank_name','economic_code','amount','liability_total','verified_by_id','state'],
    stateField: 'state',
    actions: [{m:'action_link_open_deductions',l:'Link Open Deductions'},{m:'action_record_verification',l:'Record Receipt Verification'},{m:'action_confirm_deposit',l:'Confirm Deposit & Post'}] },
  'M51-input': { kind: 'model_list', model: 'fix.input.vat.credit',
    cols: ['partner_id','supplier_mushak_no','invoice_date','vat_amount','signed_vat','claim_period','claim_deadline','ineligible_reason','vat_return_id','state'],
    stateField: 'state', actions: [{m:'action_check_eligibility',l:'Check Eligibility'}] },
  'M51-tds': { kind: 'model_list', model: 'fix.tds.return',
    cols: ['quarter','fiscal_year','total_withheld','deductor_count','due_date','state','filed_at','nbr_acknowledgment'],
    stateField: 'state', actions: [{m:'action_prepare',l:'Prepare from Deductions'},{m:'action_file',l:'Record NBR Filing'}] },
  'M51-tds-lines': { kind: 'model_list', model: 'fix.withholding.line', create: false,
    cols: ['document_date','partner_id','partner_bin','section','base_amount','rate','multiplier','amount','statutory_shortfall','rate_flagged','source_ref','challan_no','certificate_id','duplicate_refs','correction_kind','correction_state','correction_reason','state'],
    stateField: 'state', domain: [['tax_kind','=','tds']],
    actions: [{m:'action_apply_statutory_uplift',l:'Apply Statutory Uplift'}, ...DEDUCTION_ACTIONS] },
  'M51-vds': { kind: 'model_list', model: 'fix.withholding.line', create: false,
    cols: ['document_date','partner_id','partner_bin','section','base_amount','rate','multiplier','amount','statutory_shortfall','rate_flagged','source_ref','challan_no','certificate_id','duplicate_refs','correction_kind','correction_state','correction_reason','state'],
    stateField: 'state', domain: [['tax_kind','=','vds']],
    actions: DEDUCTION_ACTIONS },
  'M51-certs': { kind: 'model_list', model: 'fix.withholding.certificate', create: false,
    cols: ['certificate_no','certificate_type','supplier_name','base_amount','rate_percent','withheld_amount','challan_no','state'],
    stateField: 'state' },
  'M51-determination': { kind: 'model_list', model: 'fix.vat.treatment',
    cols: ['code','name','treatment_type','rate','active','signoff_state','adviser_reference','cfo_signed_by_id','state'],
    stateField: 'state', actions: MASTER_ACTIONS },
  'M51-signoff': { kind: 'table_report', module: 'M51', report: 'signoff_queue', title: 'Statutory Master Sign-Off Queue', period: false },
  'M51-nid': { kind: 'table_report', module: 'M51', report: 'mushak_610' },
  'M51-notes': { kind: 'table_report', module: 'M51', report: 'note_register' },
  'M51-calendar': { kind: 'table_report', module: 'M51', report: 'statutory_calendar' },
  'M51-audit': { kind: 'model_list', model: 'fix.tax.audit.pack',
    cols: ['name','date_from','date_to','file_count','pack_sha256','attachment_id','integrity_status','state'],
    stateField: 'state', actions: [{m:'action_generate',l:'Generate Pack'},{m:'action_verify',l:'Verify Checksums'}] },
  'M51-rates': { kind: 'model_list', model: 'fix.tax.rate',
    cols: ['tax_kind','code','name','section','payee_type','rate','non_filer_applies','date_from','date_to','signoff_state','adviser_reference','cfo_signed_by_id','state'],
    stateField: 'state', actions: MASTER_ACTIONS },
  'M51-params': { kind: 'model_list', model: 'fix.tax.parameter',
    cols: ['key','value','date_from','date_to','signoff_state','adviser_reference','cfo_signed_by_id','state'],
    stateField: 'state', actions: MASTER_ACTIONS },
  'M51-duerules': { kind: 'model_list', model: 'fix.statutory.due.rule',
    cols: ['obligation','name','frequency','due_day','month_offset','roll_to_working_day','date_from','date_to','signoff_state','adviser_reference','cfo_signed_by_id','state'],
    stateField: 'state', actions: MASTER_ACTIONS },
  'M51-filings': { kind: 'model_list', model: 'fix.statutory.filing',
    cols: ['rule_id','period_key','filed_on','reference'] },


  /* ===== A08 master-data forms (D365 in-workspace) ===== */
  'M51-form-vatreturn': {
    kind: 'model_form',
    model: 'fix.vat.return',
    title: "VAT Return (Mushak 9.1)",
    back: 'M51-vat91',
    status: { field: 'state', labels: { draft: "Draft", filed: "Filed", accepted: "Accepted" } },
    sections: [
      { title: "Return",
        note: "One return per period. Output/input VAT, net payable and the VDS credit are computed from the registers; the sub-ledger status is recomputed against the GL; it is filed online by the filing approver, never by its preparer.",
        fields: [
          { name: 'period', required: true, label: "Period (YYYY-MM)" },
          { name: 'due_date', readonly: true, label: "Due Date" },
          { name: 'nil_return', readonly: true, label: "Nil Return" },
          { name: 'subledger_status', readonly: true, label: "Sub-ledger" },
          { name: 'prepared_by_id', readonly: true, label: "Prepared By" },
          { name: 'nbr_confirmation', readonly: true, label: "NBR Confirmation (IVAS)" },
          { name: 'state', readonly: true, label: "State" }
        ] }
    ]
  },
  'M51-form-treatment': {
    kind: 'model_form',
    model: 'fix.vat.treatment',
    title: "VAT Treatment",
    back: 'M51-determination',
    sections: [
      { title: "Treatment",
        note: "The treatment decides how a transaction line is taxed (standard, exempt, zero-rated, truncated base).",
        fields: [
          { name: 'code', required: true, label: "Treatment Code" },
          { name: 'name', required: true, label: "Treatment Name" },
          { name: 'treatment_type', required: true, label: "Treatment Type" },
          { name: 'rate', label: "Rate %" },
          { name: 'truncated_base', label: "Truncated Base %" },
          { name: 'adviser_reference_input', label: "Adviser Confirmation (to record)" },
          { name: 'state', readonly: true, label: "Status" },
          { name: 'active', label: "Active" }
        ] }
    ]
  },
  'M51-form-audit': {
    kind: 'model_form',
    model: 'fix.tax.audit.pack',
    title: "Tax Audit Pack",
    back: 'M51-audit',
    status: { field: 'state', labels: { draft: "Draft", generated: "Generated", submitted: "Submitted" } },
    sections: [
      { title: "Audit Pack",
        note: "A generated evidence pack for a date range: file count, SHA-256 of the pack and the integrity status of the manifest.",
        fields: [
          { name: 'date_from', required: true, label: "From" },
          { name: 'date_to', required: true, label: "To" },
          { name: 'integrity_status', readonly: true, label: "Integrity (vs seal)" },
          { name: 'state', readonly: true, label: "State" }
        ] }
    ]
  },
  'M51-form-tparam': {
    kind: 'model_form',
    model: 'fix.tax.parameter',
    title: "Tax Parameter",
    back: 'M51-params',
    sections: [
      { title: "Parameter",
        note: "A dated statutory parameter (rate, threshold, rebate). The adviser-verification flag records whether it was confirmed externally.",
        fields: [
          { name: 'key', required: true, label: "Parameter Key" },
          { name: 'value', required: true, label: "Value" },
          { name: 'date_from', required: true, label: "From" },
          { name: 'date_to', label: "To" },
          { name: 'verify_with_adviser', readonly: true, label: "Verify With Adviser" },
          { name: 'adviser_reference_input', label: "Adviser Confirmation (to record)" },
          { name: 'state', readonly: true, label: "Status" },
          { name: 'source_note', label: "Source Note" }
        ] }
    ]
  },
  'M51-form-duerule': {
    kind: 'model_form',
    model: 'fix.statutory.due.rule',
    title: "Statutory Due Rule",
    back: 'M51-duerules',
    sections: [
      { title: "Due Rule",
        note: "Computes the due date of a recurring statutory obligation from the period end, the due day and the month offset.",
        fields: [
          { name: 'name', required: true, label: "Rule Name" },
          { name: 'obligation', required: true, label: "Obligation" },
          { name: 'authority', label: "Authority" },
          { name: 'frequency', required: true, label: "Frequency" },
          { name: 'due_day', required: true, label: "Due Day" },
          { name: 'month_offset', required: true, label: "Month Offset" },
          { name: 'roll_to_working_day', label: "Roll to Working Day" },
          { name: 'date_from', required: true, label: "Valid From" },
          { name: 'adviser_reference_input', label: "Adviser Confirmation (to record)" },
          { name: 'state', readonly: true, label: "Status" },
          { name: 'active', label: "Active" }
        ] }
    ]
  },

};

/* built-in report chips -> the screen that shows that report */
export const REPORT_ROUTES = {
  'M51:SD & AT Liability': 'M51-rpt-sdat',
  'M51:Marketplace VAT Model': 'M51-determination',
  "M51:Mushak 9.1 Return Draft": "M51-rpt-vatdraft",
  "M51:VAT Reconciliation": "M51-rpt-vatrecon",
  "M51:TDS Annual Summary": "M51-rpt-tdsannual",
  "M51:VDS Deduction Register": "M51-rpt-vds",
  "M51:Mushak 6.10 High-Value Register": "M51-mushak610",
  "M51:Credit / Debit Note Register": "M51-notes",
  "M51:Statutory Compliance Calendar": "M51-calendar",
};

/* report screens (each chip opens its OWN computed pack) */
Object.assign(SCREENS, {
  'M51-rpt-vatdraft': { kind: 'table_report', module: 'M51', report: 'vat_return_draft', title: 'Mushak 9.1 Return Draft', period: false },
  'M51-rpt-vatrecon': { kind: 'table_report', module: 'M51', report: 'vat_reconciliation', title: 'VAT Reconciliation', period: false },
  'M51-rpt-tdsannual': { kind: 'table_report', module: 'M51', report: 'tds_annual_summary', title: 'TDS Annual Summary', period: false },
  'M51-rpt-vds': { kind: 'table_report', module: 'M51', report: 'vds_deduction_register', title: 'VDS Deduction Register', period: false },
  'M51-mushak610': { kind: 'table_report', module: 'M51', report: 'mushak_610', title: 'Mushak 6.10 High-Value Register', period: true }
});

/* data-entry form chips -> real model forms */
export const FORM_MODELS = {
  'M51:Challan': 'fix.tax.challan',
  'M51:TDS Return': 'fix.tds.return',
  'M51:Input VAT Adjustment': 'fix.input.vat.credit',
  'M51:Filing Evidence': 'fix.statutory.filing',
  'M51:Tax Rate': 'fix.tax.rate',
  'M51:VAT Register Correction': 'fix.mushak.correction',
};

/* ============ D365 IN-WORKSPACE FORM SCREENS (M51 re-audit v2) ======== */
Object.assign(SCREENS, {
  'M51-form-challan': {
    kind: 'model_form',
    model: 'fix.tax.challan',
    title: 'Challan',
    back: 'M51-challans',
    sections: [
      { title: 'A-Challan Deposit', note: 'The deposit challan settles a withholding or VAT period; the liability total links it to the return it pays.',
        fields: [
          { name: 'challan_no', required: true, label: 'Challan No' },
          { name: 'challan_date', required: true, label: 'Deposit Date' },
          { name: 'tax_kind', required: true, label: 'Tax Kind' },
          { name: 'period', label: 'Period (YYYY-MM)' },
          { name: 'payment_mode', required: true, label: 'Payment Mode' },
          { name: 'amount', required: true, label: 'Deposited' },
          { name: 'economic_code', label: 'Economic Code' },
          { name: 'bank_name', label: 'Bank' },
          { name: 'bank_branch', label: 'Branch' },
          { name: 'vat_return_id', label: 'VAT Return (9.1)' },
          { name: 'receipt_reference', label: 'iBAS++ / Bank Confirmation (verifier)' },
          { name: 'verified_by_id', readonly: true, label: 'Verified By' },
          { name: 'state', readonly: true, label: 'State' }
        ] }
    ]
  },

  'M51-form-tdsreturn': {
    kind: 'model_form',
    model: 'fix.tds.return',
    title: 'TDS Return',
    back: 'M51-tds',
    status: { field: 'state', labels: { draft: 'Draft', prepared: 'Prepared', filed: 'Filed' } },
    sections: [
      { title: 'Quarterly Return', note: 'The return summarises the quarter\'s withholding; the fiscal year and due date compute from the quarter.',
        fields: [
          { name: 'quarter', required: true, label: 'Quarter' },
          { name: 'total_withheld', readonly: true, label: 'Total Withheld' },
          { name: 'prepared_by_id', readonly: true, label: 'Prepared By' },
          { name: 'state', readonly: true, label: 'State' },
          { name: 'nbr_acknowledgment', label: 'NBR Acknowledgement (filing approver)' }
        ] }
    ]
  },

  'M51-form-inputcredit': {
    kind: 'model_form',
    model: 'fix.input.vat.credit',
    title: 'Input VAT Adjustment',
    back: 'M51-input',
    sections: [
      { title: 'Input Credit', note: 'Records a supplier Mushak 6.3 input credit or its adjustment (increase / decrease); enlisted suppliers do not support credit.',
        fields: [
          { name: 'partner_id', required: true, label: 'Supplier' },
          { name: 'supplier_mushak_no', label: 'Supplier Mushak 6.3 No' },
          { name: 'supplier_bin', label: 'Supplier BIN' },
          { name: 'invoice_date', required: true, label: 'Invoice Date' },
          { name: 'taxable_amount', label: 'Taxable Value' },
          { name: 'vat_amount', required: true, label: 'Input VAT' },
          { name: 'adjustment_type', required: true, label: 'Adjustment Type' },
          { name: 'original_credit_id', label: 'Original Invoice Credit (6.7 / 6.8)' },
          { name: 'source_ref', label: 'Source Document' },
          { name: 'supplier_enlisted', label: 'Turnover-Enlisted' }
        ] }
    ]
  },

  'M51-form-filing': {
    kind: 'model_form',
    model: 'fix.statutory.filing',
    title: 'Filing Evidence',
    back: 'M51-filings',
    sections: [
      { title: 'Filing', note: 'Evidence that a statutory obligation was met: the calendar rule it discharges and the acknowledgement reference.',
        fields: [
          { name: 'rule_id', label: 'Calendar Rule' },
          { name: 'period_key', required: true, label: 'Period' },
          { name: 'filed_on', required: true, label: 'Filed On' },
          { name: 'reference', required: true, label: 'Acknowledgement / Reference' }
        ] }
    ]
  },

  'M51-form-rate': {
    kind: 'model_form',
    model: 'fix.tax.rate',
    title: 'Tax Rate',
    back: 'M51-rates',
    sections: [
      { title: 'Rate Master', note: 'Effective-dated statutory rate by kind and section; non-filer multiplier applies where marked.',
        fields: [
          { name: 'tax_kind', required: true, label: 'Tax Kind' },
          { name: 'code', label: 'Code' },
          { name: 'name', required: true, label: 'Description' },
          { name: 'section', label: 'ITA Section / Service Code' },
          { name: 'rate', required: true, label: 'Rate (%)' },
          { name: 'payee_type', required: true, label: 'Payee Type' },
          { name: 'non_filer_applies', label: 'Non-Filer Multiplier Applies' },
          { name: 'date_from', required: true, label: 'Valid From' },
          { name: 'date_to', label: 'Valid To' },
          { name: 'adviser_reference_input', label: 'Adviser Confirmation (to record)' },
          { name: 'signoff_state', readonly: true, label: 'Sign-Off' },
          { name: 'state', readonly: true, label: 'Status' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },

  'M51-form-correction': {
    kind: 'model_form',
    model: 'fix.mushak.correction',
    title: 'VAT Register Correction',
    back: 'M51-corrections',
    status: { field: 'state', labels: { draft: 'Requested', approved: 'Approved & Applied', rejected: 'Rejected' } },
    sections: [
      { title: 'Correction', note: 'An issued row is never edited. Classify a row the 9.1 cannot read (its amounts must fit the treatment at the rate in force), or issue a Mushak 6.7 / 6.8 note in an open period. A different Accounting Administrator decides. No BIN is typed here: a note carries the company\'s own. Re-prepare the return afterwards.',
        fields: [
          { name: 'register_id', required: true, label: 'Register Row' },
          { name: 'current_line', readonly: true, label: '9.1 Line Now' },
          { name: 'correction_type', required: true, label: 'Correction' },
          { name: 'treatment', label: 'Treatment' },
          { name: 'reduced_rate', label: 'Scheduled Reduced Rate (%)' },
          { name: 'taxable_amount', label: 'Note Taxable Value' },
          { name: 'vat_amount', label: 'Note VAT' },
          { name: 'note_date', label: 'Note Date' },
          { name: 'reason', required: true, label: 'Reason' },
          { name: 'requested_by_id', readonly: true, label: 'Requested By' },
          { name: 'decided_by_id', readonly: true, label: 'Decided By' },
          { name: 'note_id', readonly: true, label: 'Note Issued' },
          { name: 'state', readonly: true, label: 'State' }
        ] }
    ]
  }
});

export const FORM_CHIPS = {
  'M51:Mushak 6.3 Entry': 'M51-form-vatreturn',
  'M51:TDS Entry': 'M51-form-tdsreturn',
  'M51:Tax Adjustment': 'M51-form-inputcredit',
  'M51:VAT Return (Mushak 9.1)': 'M51-form-vatreturn',
  'M51:VAT Treatment': 'M51-form-treatment',
  'M51:Tax Audit Pack': 'M51-form-audit',
  'M51:Tax Parameter': 'M51-form-tparam',
  'M51:Statutory Due Rule': 'M51-form-duerule',
  'M51:Challan': 'M51-form-challan',
  'M51:TDS Return': 'M51-form-tdsreturn',
  'M51:Input VAT Adjustment': 'M51-form-inputcredit',
  'M51:Filing Evidence': 'M51-form-filing',
  'M51:Tax Rate': 'M51-form-rate',
  'M51:VAT Register Correction': 'M51-form-correction',
  'M51:__by_model__': {
    'fix.vat.return': 'M51-form-vatreturn',
    'fix.vat.treatment': 'M51-form-treatment',
    'fix.tax.audit.pack': 'M51-form-audit',
    'fix.tax.parameter': 'M51-form-tparam',
    'fix.statutory.due.rule': 'M51-form-duerule',
    'fix.tax.challan': 'M51-form-challan',
    'fix.tds.return': 'M51-form-tdsreturn',
    'fix.input.vat.credit': 'M51-form-inputcredit',
    'fix.statutory.filing': 'M51-form-filing',
    'fix.tax.rate': 'M51-form-rate',
    'fix.mushak.correction': 'M51-form-correction'
  },
  'M51:__by_screen__': {
    'M51-vat91': 'M51-form-vatreturn',
    'M51-determination': 'M51-form-treatment',
    'M51-audit': 'M51-form-audit',
    'M51-params': 'M51-form-tparam',
    'M51-duerules': 'M51-form-duerule',
    'M51-challans': 'M51-form-challan',
    'M51-tds': 'M51-form-tdsreturn',
    'M51-input': 'M51-form-inputcredit',
    'M51-filings': 'M51-form-filing',
    'M51-rates': 'M51-form-rate',
    'M51-corrections': 'M51-form-correction'
  }
};

/* the module's "+ New" surface */
export const CREATE = {
  M51: { screen: 'M51-form-challan', model: 'fix.tax.challan', label: 'Challan' },
};
