/** @odoo-module **/
/* A08 · Finance & Treasury — M51 Tax & Regulatory (BD).
 * One file per A08 module (merged into P03_MODULES and the screen maps by
 * p03_modules_meta.js): the registry entry, the in-workspace data screens,
 * built-in report routes, data-entry form chips and the "+ New" surface. */

export const MODULE = {
  area: 'A08', code: 'M51', en: 'Tax & Regulatory (BD)', title: 'M51 · Tax & Regulatory (BD)',
  bn: 'কর ও ভ্যাট', icon: '🏛️',
  desc: 'VAT 15%, Mushak 6.1–9.1 registers & returns, TDS/VDS, challans, NID capture, statutory calendar.',
  kpis: [
    { l: 'VAT Payable MTD', m: 'vat_collected_mtd' },
    { l: 'Mushak 9.1 Status', m: 'vat_returns_count' },
    { l: 'Input Credit Tracked', m: 'mushak_records' },
    { l: 'TDS Certificates Due' }
  ],
  groups: [
    { en: 'VAT', screens: [
      { id: 'M51-mushak61', en: 'Mushak 6.1 (Sales)', bn: 'মুশক ৬.১', t: 'g' },
      { id: 'M51-mushak62', en: 'Mushak 6.2 (Purchases)', bn: 'মুশক ৬.২', t: 'g' },
      { id: 'M51-mushak63', en: 'Mushak 6.3 Records', bn: 'মুশক ৬.৩', t: 'g' },
      { id: 'M51-vat91', en: 'VAT Return 9.1 Filing', bn: 'ভ্যাট রিটার্ন ৯.১', t: 'c' },
      { id: 'M51-challans', en: 'Challans (A-Challan)', bn: 'চালান', t: 'g' },
      { id: 'M51-input', en: 'Input Credit Tracking', bn: 'ইনপুট ক্রেডিট', t: 'g' }
    ]},
    { en: 'Withholding', screens: [
      { id: 'M51-tds', en: 'TDS Register', bn: 'টিডিএস রেজিস্টার', t: 'g' },
      { id: 'M51-vds', en: 'VDS (45 Services)', bn: 'ভিডিএস', t: 'g' },
      { id: 'M51-certs', en: 'Certificates', bn: 'সনদ', t: 'g' }
    ]},
    { en: 'Compliance', screens: [
      { id: 'M51-determination', en: 'Tax Determination Service', bn: 'কর নির্ধারণ', t: 'c' },
      { id: 'M51-nid', en: 'High-Value NID Capture', bn: 'এনআইডি সংগ্রহ', t: 'g' },
      { id: 'M51-calendar', en: 'Statutory Calendar', bn: 'বিধিবদ্ধ ক্যালেন্ডার', t: 'c' },
      { id: 'M51-audit', en: 'Audit Support Pack', bn: 'অডিট সহায়তা', t: 'r' }
    ]}
  ],
  reports: ['Mushak 9.1 Return Draft', 'VAT Reconciliation', 'TDS Annual Summary', 'SD & AT Liability', 'Marketplace VAT Model', 'Statutory Compliance Calendar'],
  forms: ['Mushak 6.3 Entry', 'TDS Entry', 'Challan', 'Tax Adjustment'],
  cross: ['AR, Invoicing & Collections', 'AP & Employee Expense', 'Financial Accounting & GL'],
  freg: { src: 78, sub: [
    ['1', 'Determination Service', 9], ['2', 'VAT Output/Input', 12], ['3', 'Mushak Registers', 11],
    ['4', 'VAT Return 9.1', 8], ['5', 'VDS', 7], ['6', 'TDS', 12],
    ['7', 'Challans & Certificates', 7], ['8', 'NID & Cash Controls', 4], ['9', 'Calendar & Audit', 8]
  ] }
};

/* in-workspace data screens (checked before any stock Odoo view) */
export const SCREENS = {
  'M51-mushak61': { kind: 'model_list', model: 'fix.mushak.register',
    cols: ['mushak_no','invoice_ref','invoice_date','customer_name','taxable_amount','vat_amount','posted'] },
  'M51-mushak62': { kind: 'model_list', model: 'fix.mushak.register',
    cols: ['mushak_no','invoice_ref','invoice_date','supplier_name','taxable_amount','vat_amount','posted'] },
  'M51-mushak63': { kind: 'model_list', model: 'fix.mushak.register',
    cols: ['mushak_no','invoice_ref','invoice_date','customer_name','taxable_amount','vat_amount','total_payable','posted'],
    actions: [{m:'action_mark_posted',l:'Mark GL Posted'},{m:'action_rebuild_from_events',l:'Rebuild from Events'}] },
  'M51-vat91': { kind: 'model_list', model: 'fix.vat.return',
    cols: ['period','total_taxable','output_vat','input_vat','net_payable','due_date','state','filed_at'],
    stateField: 'state', actions: [{m:'action_prepare_period',l:'Prepare Period'},{m:'action_file',l:'File Return'}] },
  'M51-tds': { kind: 'model_list', model: 'fix.tds.return',
    cols: ['quarter','fiscal_year','total_withheld','deductor_count','due_date','state','filed_at'],
    stateField: 'state', actions: [{m:'action_prepare_quarter',l:'Prepare Quarter'},{m:'action_file',l:'File'}] },
  'M51-determination': { kind: 'model_list', model: 'fix.vat.treatment',
    cols: ['code','name','treatment_type','rate','active'] },
  'M51-certs': { kind: 'model_list', model: 'fix.withholding.certificate',
    cols: ['quarter','certificate_type','supplier_name','base_amount','rate_percent','withheld_amount','state'],
    stateField: 'state', actions: [{m:'action_issue',l:'Issue Certificate'}] },
};

/* built-in report chips -> the screen that shows that report */
export const REPORT_ROUTES = {
  "M51:Mushak 9.1 Return Draft": "M51-vat91",
  "M51:VAT Reconciliation": "M51-vat91",
  "M51:TDS Annual Summary": "M51-tds",
};

/* data-entry form chips -> real model forms */
export const FORM_MODELS = {
  'M51:Mushak 6.3 Entry': 'fix.mushak.register',
  'M51:TDS Entry': 'fix.tds.return',
  'M51:Challan': 'fix.tds.return',
};

/* the module's "+ New" surface */
export const CREATE = {
  M51: { model: 'fix.mushak.register', label: 'Mushak 6.3 Entry' },
};
