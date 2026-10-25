/** @odoo-module **/
/* A08 · Finance & Treasury — M50 Treasury & Banking.
 * One file per A08 module (merged into P03_MODULES and the screen maps by
 * p03_modules_meta.js): the registry entry, the in-workspace data screens,
 * built-in report routes, data-entry form chips and the "+ New" surface.
 * Backend: controllers/a08/m50.py (SURFACES, REPORTS, kpis) over the
 * cd_cash_position models. */

export const MODULE = {
  area: 'A08', code: 'M50', en: 'Treasury & Banking', title: 'M50 · Treasury & Banking',
  bn: 'কোষাগার ও ব্যাংক', icon: '🏦',
  desc: 'Bank reconciliation, branch cash consolidation, rider COD, gateway/MFS settlement, BEFTN/RTGS execution.',
  kpis: [
    { l: 'Recon Exceptions', m: 'unreconciled_bank_lines' },
    { l: 'Auto-Match Rate', m: 'auto_match_rate' },
    { l: 'Cash Position', m: 'cash_position' },
    { l: 'Branch Cash Uncollected', m: 'branch_cash_uncollected' }
  ],
  groups: [
    { en: 'Cash', screens: [
      { id: 'M50-position', en: 'Consolidated Cash Position', bn: 'নগদ অবস্থান', t: 'd' },
      { id: 'M50-branchcash', en: 'Branch Cash Consolidation', bn: 'শাখা নগদ', t: 'r' },
      { id: 'M50-ridercod', en: 'Rider COD Settlement', bn: 'রাইডার সিওডি', t: 'c' },
      { id: 'M50-petty', en: 'Petty Cash (Imprest)', bn: 'খরচি নগদ', t: 'g' },
      { id: 'M50-petty-vouchers', en: 'Petty Cash Vouchers', bn: 'খরচি নগদ ভাউচার', t: 'g' },
      { id: 'M50-petty-topups', en: 'Imprest Top-Ups', bn: 'খরচি নগদ পূরণ', t: 'g' },
      { id: 'M50-petty-counts', en: 'Petty Cash Counts', bn: 'খরচি নগদ গণনা', t: 'g' }
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
      { id: 'M50-gateway-lines', en: 'Settlement Exceptions', bn: 'সেটেলমেন্ট ব্যতিক্রম', t: 'g' },
      { id: 'M50-cit', en: 'Cash-in-Transit', bn: 'নগদ পরিবহন', t: 'g' }
    ]},
    { en: 'Planning', screens: [
      { id: 'M50-forecast', en: 'Cash-Flow Forecast', bn: 'নগদ প্রবাহ পূর্বাভাস', t: 'r' },
      { id: 'M50-recurring', en: 'Recurring Cash Items', bn: 'পুনরাবৃত্ত নগদ খাত', t: 'g' },
      { id: 'M50-facilities', en: 'Facilities & Covenants', bn: 'সুবিধা ও চুক্তি', t: 'g' },
      { id: 'M50-repayments', en: 'Loan Repayment Schedule', bn: 'ঋণ পরিশোধ সূচি', t: 'g' },
      { id: 'M50-covenants', en: 'Covenant Tests', bn: 'চুক্তি শর্ত পরীক্ষা', t: 'g' },
      { id: 'M50-fx', en: 'FX Holdings', bn: 'বৈদেশিক মুদ্রা', t: 'r' }
    ]},
    { en: 'Reports', screens: [
      { id: 'M50-rpt-position', en: 'Daily Cash Position', bn: 'দৈনিক নগদ অবস্থান', t: 'r' },
      { id: 'M50-rpt-recon', en: 'Bank Reconciliation Summary', bn: 'ব্যাংক মিলকরণ সারসংক্ষেপ', t: 'r' },
      { id: 'M50-rpt-gateway', en: 'Gateway Settlement Reconciliation', bn: 'গেটওয়ে সেটেলমেন্ট মিলকরণ', t: 'r' },
      { id: 'M50-rpt-cod', en: 'COD Settlement Report', bn: 'সিওডি সেটেলমেন্ট প্রতিবেদন', t: 'r' },
      { id: 'M50-rpt-charges', en: 'Bank Charges Analysis', bn: 'ব্যাংক চার্জ বিশ্লেষণ', t: 'r' }
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

const PAYMENT_COLS = ['name','payee','amount','method','rail','journal_id','state','bank_reference','bank_confirmed','executed_at'];
const PAYMENT_ACTIONS = [
  {m:'action_release',l:'Release to Bank'},
  {m:'action_confirm_bank',l:'Confirm Bank Debit'},
  {m:'action_mark_failed',l:'Bank Rejected'},
  {m:'action_retry',l:'Re-queue'}
];

/* in-workspace data screens (checked before any stock Odoo view) */
export const SCREENS = {
  // ---- Cash
  'M50-position': { kind: 'model_list', model: 'fix.cash.position',
    cols: ['as_of','bank_balance','drawer_float_total','petty_cash_total','cash_in_transit_total','pending_payments','total_position'],
    actions: [{m:'action_take_snapshot',l:'Take Snapshot'}] },
  'M50-branchcash': { kind: 'table_report', module: 'M50', report: 'branch_cash' },
  'M50-ridercod': { kind: 'model_list', model: 'fix.cod.settlement',
    cols: ['name','rider_id','settlement_date','order_count','expected_amount','remitted_amount','variance','state'],
    stateField: 'state',
    actions: [{m:'action_load_orders',l:'Load COD Orders'},{m:'action_submit',l:'Submit'},{m:'action_settle',l:'Settle'},{m:'action_dispute',l:'Dispute'}] },
  'M50-petty': { kind: 'model_list', model: 'fix.imprest.fund',
    cols: ['name','branch_id','custodian_id','imprest_limit','book_balance','pending_vouchers','replenish_amount','state'],
    stateField: 'state', actions: [{m:'action_request_topup',l:'Request Top-Up'}] },
  'M50-petty-vouchers': { kind: 'model_list', model: 'fix.imprest.voucher',
    cols: ['name','fund_id','voucher_date','description','amount','receipt_ref','state'],
    stateField: 'state',
    actions: [{m:'action_submit',l:'Submit'},{m:'action_approve',l:'Approve'},{m:'action_post',l:'Pay & Post'},{m:'action_reject',l:'Reject'}] },
  'M50-petty-topups': { kind: 'model_list', model: 'fix.imprest.topup',
    cols: ['name','fund_id','amount','journal_id','topup_date','state','approved_by_id'],
    stateField: 'state',
    actions: [{m:'action_approve',l:'Approve'},{m:'action_pay',l:'Pay from Bank'},{m:'action_reject',l:'Reject'}] },
  'M50-petty-counts': { kind: 'model_list', model: 'fix.imprest.count',
    cols: ['fund_id','count_date','counted_amount','book_balance','variance','state'],
    stateField: 'state',
    actions: [{m:'action_reconcile',l:'Reconcile'},{m:'action_book_variance',l:'Book Variance'}] },
  // ---- Banking
  'M50-accounts': { kind: 'model_list', model: 'account.journal',
    cols: ['name','code','bank_id','bank_acc_number','fix_branch_name','fix_routing_number','fix_account_type','fix_treasury_role','currency_id','fix_gl_balance','fix_unmatched_lines'],
    domain: [['type','=','bank']], context: { default_type: 'bank' } },
  'M50-statements': { kind: 'model_list', model: 'fix.bank.statement.import',
    cols: ['journal_id','filename','format_type','state','imported_count','create_date'],
    stateField: 'state', actions: [{m:'action_import',l:'Import'}] },
  'M50-recon': { kind: 'model_list', model: 'fix.bank.statement.line',
    cols: ['date','journal_id','reference','narration','amount','match_state','matched_kind','matched_invoice_ref'],
    stateField: 'match_state',
    actions: [{m:'auto_match',l:'Auto-Match'},{m:'action_confirm_manual_match',l:'Confirm Manual Match'},{m:'action_post_bank_charge',l:'Book as Bank Charge'}] },
  // ---- Execution
  'M50-beftn': { kind: 'model_list', model: 'fix.payment.execution',
    cols: PAYMENT_COLS, stateField: 'state', domain: [['method','=','bank_transfer']],
    context: { default_method: 'bank_transfer' }, actions: PAYMENT_ACTIONS },
  'M50-cheques': { kind: 'model_list', model: 'fix.cheque',
    cols: ['cheque_no','direction','partner_id','amount','cheque_date','is_pdc','journal_id','state','bounce_count'],
    stateField: 'state',
    actions: [{m:'action_deposit',l:'Deposit'},{m:'action_bounce',l:'Bounced'},{m:'action_cancel',l:'Void'}] },
  'M50-mfs': { kind: 'model_list', model: 'fix.payment.execution',
    cols: PAYMENT_COLS, stateField: 'state', domain: [['method','=','mobile_fs']],
    context: { default_method: 'mobile_fs' }, actions: PAYMENT_ACTIONS },
  // ---- Settlement
  'M50-gateway': { kind: 'model_list', model: 'fix.gateway.settlement',
    cols: ['name','provider','settlement_date','line_count','total_gross','total_fee','total_fee_vat','total_net','exception_count','bank_matched','state'],
    stateField: 'state',
    actions: [{m:'action_import_report',l:'Import Report'},{m:'action_match',l:'Re-run Match'},{m:'action_post',l:'Post'}] },
  'M50-gateway-lines': { kind: 'model_list', model: 'fix.gateway.settlement.line',
    cols: ['batch_id','provider','trx_id','txn_date','gross','fee','net','receipt_name','receipt_amount','match_state'],
    stateField: 'match_state', domain: [['match_state','!=','matched']], create: false },
  'M50-cit': { kind: 'model_list', model: 'fix.cash.deposit',
    cols: ['name','branch_id','business_date','journal_id','amount','slip_no','state','credited_amount','variance_amount'],
    stateField: 'state',
    actions: [{m:'action_dispatch',l:'Dispatch to Bank'},{m:'action_resolve_variance',l:'Book Variance'},{m:'action_cancel',l:'Cancel'}] },
  // ---- Planning
  'M50-forecast': { kind: 'table_report', module: 'M50', report: 'cash_forecast', period: false },
  'M50-recurring': { kind: 'model_list', model: 'fix.cash.forecast.item',
    cols: ['name','direction','category','amount','frequency','start_date','end_date'] },
  'M50-facilities': { kind: 'model_list', model: 'fix.bank.facility',
    cols: ['name','lender_id','facility_type','limit_amount','utilised','available','utilisation_pct','next_due_date','next_due_amount','state'],
    stateField: 'state',
    actions: [{m:'action_activate',l:'Activate'},{m:'action_generate_schedule',l:'Generate Schedule'},{m:'action_close',l:'Close'}] },
  'M50-repayments': { kind: 'model_list', model: 'fix.facility.repayment',
    cols: ['facility_id','sequence','due_date','principal','interest','total','state','is_overdue'],
    stateField: 'state', create: false, actions: [{m:'action_pay',l:'Pay Instalment'}] },
  'M50-covenants': { kind: 'model_list', model: 'fix.facility.covenant',
    cols: ['facility_id','name','metric','operator','threshold','last_value','last_result','last_tested'],
    actions: [{m:'action_test',l:'Run Test'}] },
  'M50-fx': { kind: 'table_report', module: 'M50', report: 'fx_holdings', period: false },
  // ---- Reports
  'M50-rpt-position': { kind: 'table_report', module: 'M50', report: 'daily_cash_position', period: false },
  'M50-rpt-recon': { kind: 'table_report', module: 'M50', report: 'bank_recon_summary' },
  'M50-rpt-gateway': { kind: 'table_report', module: 'M50', report: 'gateway_recon' },
  'M50-rpt-cod': { kind: 'table_report', module: 'M50', report: 'cod_report' },
  'M50-rpt-charges': { kind: 'table_report', module: 'M50', report: 'bank_charges' },
};

/* built-in report chips -> the screen that shows that report */
export const REPORT_ROUTES = {
  "M50:Daily Cash Position": "M50-rpt-position",
  "M50:Bank Reconciliation Summary": "M50-rpt-recon",
  "M50:Gateway Settlement Reconciliation": "M50-rpt-gateway",
  "M50:COD Settlement Report": "M50-rpt-cod",
  "M50:13-Week Cash Forecast": "M50-forecast",
  "M50:Bank Charges Analysis": "M50-rpt-charges",
};

/* data-entry form chips -> real model forms */
export const FORM_MODELS = {
  'M50:Bank Statement Import': 'fix.bank.statement.import',
  'M50:Payment Instruction': 'fix.payment.execution',
  'M50:Cash Deposit': 'fix.cash.deposit',
  'M50:Imprest Top-Up': 'fix.imprest.topup',
};

/* the module's "+ New" surface */
export const CREATE = {
  M50: { model: 'fix.payment.execution', label: 'Payment Instruction' },
};
