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
    { l: 'Overdue Obligations', m: 'overdue_obligations' }
  ],
  groups: [
    { en: 'VAT', screens: [
      { id: 'M51-mushak61', en: 'Mushak 6.1 (Purchases)', bn: 'মুশক ৬.১ (ক্রয়)', t: 'g' },
      { id: 'M51-mushak62', en: 'Mushak 6.2 (Sales)', bn: 'মুশক ৬.২ (বিক্রয়)', t: 'g' },
      { id: 'M51-mushak63', en: 'Mushak 6.3 Records', bn: 'মুশক ৬.৩', t: 'g' },
      { id: 'M51-vat91', en: 'VAT Return 9.1 Filing', bn: 'ভ্যাট রিটার্ন ৯.১', t: 'c' },
      { id: 'M51-challans', en: 'Challans (A-Challan)', bn: 'চালান', t: 'g' },
      { id: 'M51-input', en: 'Input Credit Tracking', bn: 'ইনপুট ক্রেডিট', t: 'g' }
    ]},
    { en: 'Withholding', screens: [
      { id: 'M51-tds', en: 'TDS Register', bn: 'টিডিএস রেজিস্টার', t: 'g' },
      { id: 'M51-vds', en: 'VDS (Mushak 6.6)', bn: 'ভিডিএস (মুশক ৬.৬)', t: 'g' },
      { id: 'M51-certs', en: 'Certificates', bn: 'সনদ', t: 'g' }
    ]},
    { en: 'Compliance', screens: [
      { id: 'M51-determination', en: 'Tax Determination Service', bn: 'কর নির্ধারণ', t: 'c' },
      { id: 'M51-mushak610', en: 'Mushak 6.10 High-Value Register', bn: 'মুশক ৬.১০ উচ্চমূল্য রেজিস্টার', t: 'r' },
      { id: 'M51-notes', en: 'Credit / Debit Note Register', bn: 'ক্রেডিট ও ডেবিট নোট রেজিস্টার', t: 'r' },
      { id: 'M51-calendar', en: 'Statutory Calendar', bn: 'বিধিবদ্ধ ক্যালেন্ডার', t: 'c' },
      { id: 'M51-audit', en: 'Audit Support Pack', bn: 'অডিট সহায়তা', t: 'r' }
    ]},
    { en: 'Master Data', screens: [
      { id: 'M51-rates', en: 'Tax Rate Master', bn: 'কর হার তালিকা', t: 'g' },
      { id: 'M51-params', en: 'Statutory Parameters', bn: 'বিধিবদ্ধ মানদণ্ড', t: 'g' },
      { id: 'M51-duerules', en: 'Statutory Calendar Rules', bn: 'বিধিবদ্ধ সময়সূচির নিয়ম', t: 'g' },
      { id: 'M51-filings', en: 'Filing Evidence', bn: 'দাখিলের প্রমাণ', t: 'g' }
    ]}
  ],
  reports: ['Mushak 9.1 Return Draft', 'VAT Reconciliation', 'TDS Annual Summary', 'VDS Deduction Register', 'Mushak 6.10 High-Value Register', 'Credit / Debit Note Register', 'Statutory Compliance Calendar'],
  forms: ['Challan', 'TDS Return', 'Input VAT Adjustment', 'Filing Evidence', 'Tax Rate'],
  cross: ['AR, Invoicing & Collections', 'AP & Employee Expense', 'Financial Accounting & GL'],
  freg: { src: 78, sub: [
    ['1', 'Determination Service', 9], ['2', 'VAT Output/Input', 12], ['3', 'Mushak Registers', 11],
    ['4', 'VAT Return 9.1', 8], ['5', 'VDS', 7], ['6', 'TDS', 12],
    ['7', 'Challans & Certificates', 7], ['8', 'High-Value Register', 4], ['9', 'Calendar & Audit', 8]
  ] }
};

/* in-workspace data screens (checked before any stock Odoo view) */
export const SCREENS = {
  'M51-mushak61': { kind: 'model_list', model: 'fix.input.vat.credit',
    cols: ['invoice_date','partner_id','supplier_bin','supplier_mushak_no','adjustment_type','taxable_amount','vat_amount','claim_period','state'] },
  'M51-mushak62': { kind: 'model_list', model: 'fix.mushak.register', create: false,
    cols: ['mushak_no','invoice_ref','invoice_date','customer_name','customer_bin','taxable_amount','vat_amount','total_payable','posted'] },
  'M51-mushak63': { kind: 'model_list', model: 'fix.mushak.register', create: false,
    cols: ['mushak_no','invoice_ref','invoice_date','customer_name','taxable_amount','vat_amount','total_payable','posted'],
    actions: [{m:'action_mark_posted',l:'Mark GL Posted'},{m:'action_rebuild_from_events',l:'Rebuild from Events'}] },
  'M51-vat91': { kind: 'model_list', model: 'fix.vat.return',
    cols: ['period','total_taxable','output_vat','input_vat','vds_received_credit','net_payable','net_payable_after_vds','due_date','subledger_status','state','filed_at','nbr_confirmation'],
    stateField: 'state',
    actions: [{m:'action_prepare',l:'Prepare from Registers'},{m:'action_subledger_reconciliation',l:'Reconcile Sub-Ledger'},{m:'action_file_online',l:'File Online (NBR)'}] },
  'M51-challans': { kind: 'model_list', model: 'fix.tax.challan',
    cols: ['challan_no','challan_date','tax_kind','period','bank_name','economic_code','amount','liability_total','state'],
    stateField: 'state',
    actions: [{m:'action_link_open_deductions',l:'Link Open Deductions'},{m:'action_confirm_deposit',l:'Confirm Deposit & Post'}] },
  'M51-input': { kind: 'model_list', model: 'fix.input.vat.credit',
    cols: ['partner_id','supplier_mushak_no','invoice_date','vat_amount','signed_vat','claim_period','claim_deadline','ineligible_reason','vat_return_id','state'],
    stateField: 'state', actions: [{m:'action_check_eligibility',l:'Check Eligibility'}] },
  'M51-tds': { kind: 'model_list', model: 'fix.tds.return',
    cols: ['quarter','fiscal_year','total_withheld','deductor_count','due_date','state','filed_at','nbr_acknowledgment'],
    stateField: 'state', actions: [{m:'action_prepare',l:'Prepare from Deductions'},{m:'action_file',l:'Record NBR Filing'}] },
  'M51-vds': { kind: 'model_list', model: 'fix.withholding.line', create: false,
    cols: ['document_date','partner_id','partner_bin','section','base_amount','rate','amount','source_ref','challan_no','certificate_id','state'],
    stateField: 'state', domain: [['tax_kind','=','vds']],
    actions: [{m:'action_issue_certificate',l:'Issue Mushak 6.6'}] },
  'M51-certs': { kind: 'model_list', model: 'fix.withholding.certificate', create: false,
    cols: ['certificate_no','certificate_type','supplier_name','base_amount','rate_percent','withheld_amount','challan_no','state'],
    stateField: 'state', actions: [{m:'action_issue',l:'Issue Certificate'}] },
  'M51-determination': { kind: 'model_list', model: 'fix.vat.treatment',
    cols: ['code','name','treatment_type','rate','active'] },
  'M51-mushak610': { kind: 'table_report', module: 'M51', report: 'mushak_610' },
  'M51-notes': { kind: 'table_report', module: 'M51', report: 'note_register' },
  'M51-calendar': { kind: 'table_report', module: 'M51', report: 'statutory_calendar' },
  'M51-audit': { kind: 'model_list', model: 'fix.tax.audit.pack',
    cols: ['name','date_from','date_to','file_count','pack_sha256','attachment_id','integrity_status','state'],
    stateField: 'state', actions: [{m:'action_generate',l:'Generate Pack'},{m:'action_verify',l:'Verify Checksums'}] },
  'M51-rates': { kind: 'model_list', model: 'fix.tax.rate',
    cols: ['tax_kind','code','name','section','payee_type','rate','non_filer_applies','date_from','date_to','verify_with_adviser'] },
  'M51-params': { kind: 'model_list', model: 'fix.tax.parameter',
    cols: ['key','value','date_from','date_to','verify_with_adviser'] },
  'M51-duerules': { kind: 'model_list', model: 'fix.statutory.due.rule',
    cols: ['obligation','name','frequency','due_day','month_offset','roll_to_working_day','date_from','date_to','verify_with_adviser'] },
  'M51-filings': { kind: 'model_list', model: 'fix.statutory.filing',
    cols: ['rule_id','period_key','filed_on','reference'] },
};

/* built-in report chips -> the screen that shows that report */
export const REPORT_ROUTES = {
  "M51:Mushak 9.1 Return Draft": "M51-vat91",
  "M51:VAT Reconciliation": "M51-vat91",
  "M51:TDS Annual Summary": "M51-tds",
  "M51:VDS Deduction Register": "M51-vds",
  "M51:Mushak 6.10 High-Value Register": "M51-mushak610",
  "M51:Credit / Debit Note Register": "M51-notes",
  "M51:Statutory Compliance Calendar": "M51-calendar",
};

/* data-entry form chips -> real model forms */
export const FORM_MODELS = {
  'M51:Challan': 'fix.tax.challan',
  'M51:TDS Return': 'fix.tds.return',
  'M51:Input VAT Adjustment': 'fix.input.vat.credit',
  'M51:Filing Evidence': 'fix.statutory.filing',
  'M51:Tax Rate': 'fix.tax.rate',
};

/* the module's "+ New" surface */
export const CREATE = {
  M51: { model: 'fix.tax.challan', label: 'Challan' },
};
