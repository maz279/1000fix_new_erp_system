/** @odoo-module **/
/* A08 · Finance & Treasury — M50 Treasury & Banking.
 * One file per A08 module (merged into P03_MODULES and the screen maps by
 * p03_modules_meta.js): the registry entry, the in-workspace data screens,
 * built-in report routes, data-entry form chips and the "+ New" surface. */

export const MODULE = {
  area: 'A08', code: 'M50', en: 'Treasury & Banking', title: 'M50 · Treasury & Banking',
  bn: 'কোষাগার ও ব্যাংক', icon: '🏦',
  desc: 'Bank reconciliation, branch cash consolidation, rider COD, gateway/MFS settlement, BEFTN/RTGS execution.',
  kpis: [
    { l: 'Recon Exceptions', m: 'unreconciled_bank_lines' },
    { l: 'Auto-Match Rate', m: 'auto_match_rate' },
    { l: 'Cash Position' },
    { l: 'Branch Cash Uncollected' }
  ],
  groups: [
    { en: 'Cash', screens: [
      { id: 'M50-position', en: 'Consolidated Cash Position', bn: 'নগদ অবস্থান', t: 'd' },
      { id: 'M50-branchcash', en: 'Branch Cash Consolidation', bn: 'শাখা নগদ', t: 'c' },
      { id: 'M50-ridercod', en: 'Rider COD Settlement', bn: 'রাইডার সিওডি', t: 'c' },
      { id: 'M50-petty', en: 'Petty Cash (Imprest)', bn: 'খরচি নগদ', t: 'g' }
    ]},
    { en: 'Banking', screens: [
      { id: 'M50-accounts', en: 'Bank Account Master', bn: 'ব্যাংক হিসাব', t: 'g' },
      { id: 'M50-statements', en: 'Statements Import', bn: 'স্টেটমেন্ট', t: 'g' },
      { id: 'M50-recon', en: 'Auto Reconciliation', bn: 'স্বয়ংক্রিয় মিলকরণ', t: 'c' }
    ]},
    { en: 'Execution', screens: [
      { id: 'M50-beftn', en: 'BEFTN / RTGS Instructions', bn: 'বিইএফটিএন', t: 'g' },
      { id: 'M50-cheques', en: 'Cheque Management', bn: 'চেক', t: 'g' },
      { id: 'M50-mfs', en: 'MFS Disbursement', bn: 'এমএফএস বিতরণ', t: 'g' }
    ]},
    { en: 'Settlement', screens: [
      { id: 'M50-gateway', en: 'Gateway / MFS Settlement', bn: 'গেটওয়ে সেটেলমেন্ট', t: 'c' },
      { id: 'M50-cit', en: 'Cash-in-Transit', bn: 'নগদ পরিবহন', t: 'g' }
    ]},
    { en: 'Planning', screens: [
      { id: 'M50-forecast', en: 'Cash-Flow Forecast', bn: 'নগদ প্রবাহ পূর্বাভাস', t: 'r' },
      { id: 'M50-facilities', en: 'Facilities & Covenants', bn: 'সুবিধা ও চুক্তি', t: 'g' },
      { id: 'M50-fx', en: 'FX Holdings', bn: 'বৈদেশিক মুদ্রা', t: 'g' }
    ]}
  ],
  reports: ['Daily Cash Position', 'Bank Reconciliation Summary', 'Gateway Settlement Reconciliation', 'COD Settlement Report', '13-Week Cash Forecast', 'Bank Charges Analysis'],
  forms: ['Bank Statement Import', 'Payment Instruction', 'Cash Deposit', 'Imprest Top-Up'],
  cross: ['Financial Accounting & GL', 'AR, Invoicing & Collections', 'AP & Employee Expense'],
  freg: { src: 88, sub: [
    ['1', 'Bank Masters', 7], ['2', 'Statement & Recon', 13], ['3', 'Cash Position & Consolidation', 12],
    ['4', 'Payment Execution', 13], ['5', 'Gateway/MFS Settlement', 11], ['6', 'Forecasting', 8],
    ['7', 'Facilities & Trade Finance', 12], ['8', 'FX', 5], ['9', 'Controls', 7]
  ] }
};

/* in-workspace data screens (checked before any stock Odoo view) */
export const SCREENS = {
  'M50-position': { kind: 'model_list', model: 'fix.cash.position',
    cols: ['as_of','bank_balance','drawer_float_total','pending_payments','total_position'] },
  'M50-statements': { kind: 'model_list', model: 'fix.bank.statement.line',
    cols: ['date','reference','narration','amount','match_state','matched_invoice_ref'],
    stateField: 'match_state' },
  'M50-recon': { kind: 'model_list', model: 'fix.bank.statement.line',
    cols: ['date','reference','narration','amount','match_state','matched_invoice_ref'],
    stateField: 'match_state', domain: [['match_state','=','unmatched']],
    actions: [{m:'auto_match',l:'Auto-Match'}] },
  'M50-beftn': { kind: 'model_list', model: 'fix.payment.execution',
    cols: ['source_model','source_id','payee','amount','method','state','executed_at'],
    stateField: 'state', actions: [{m:'action_execute',l:'Execute'}] },
  'M50-mfs': { kind: 'model_list', model: 'fix.payment.execution',
    cols: ['source_model','source_id','payee','amount','method','state','executed_at'],
    stateField: 'state', domain: [['method','!=','beftn']], actions: [{m:'action_execute',l:'Execute'}] },
};

/* built-in report chips -> the screen that shows that report */
export const REPORT_ROUTES = {
  "M50:Daily Cash Position": "M50-position",
  "M50:Bank Reconciliation Summary": "M50-recon",
  "M50:Gateway Settlement Reconciliation": "M50-mfs",
  "M50:COD Settlement Report": "M50-mfs",
};

/* data-entry form chips -> real model forms */
export const FORM_MODELS = {
  'M50:Bank Statement Import': 'fix.bank.statement.line',
  'M50:Payment Instruction': 'fix.payment.execution',
};

/* the module's "+ New" surface */
export const CREATE = {
  M50: { model: 'fix.payment.execution', label: 'Payment Instruction' },
};
