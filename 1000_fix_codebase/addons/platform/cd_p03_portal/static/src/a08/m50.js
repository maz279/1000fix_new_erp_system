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
    { l: 'Auto-Match Rate', m: 'auto_match_rate', suffix: '%' },
    { l: 'Cash Position', m: 'cash_position' },
    { l: 'Branch Cash Uncollected', m: 'branch_cash_uncollected' },
    { l: 'Payments Awaiting Bank', m: 'payments_awaiting_bank' }
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
      { id: 'M50-recon', en: 'Auto Reconciliation', bn: 'স্বয়ংক্রিয় মিলকরণ', t: 'c' },
      { id: 'M50-reconstatements', en: 'Reconciliation Statements', bn: 'মিলকরণ বিবরণী', t: 'g' },
      { id: 'M50-recon-items', en: 'Reconciling Items', bn: 'মিলকরণের খাত', t: 'g' }
    ]},
    { en: 'Execution', screens: [
      { id: 'M50-beftn', en: 'BEFTN / RTGS Instructions', bn: 'বিইএফটিএন', t: 'g' },
      { id: 'M50-cheques', en: 'Cheque Management', bn: 'চেক', t: 'g' },
      { id: 'M50-chequebooks', en: 'Cheque Books', bn: 'চেক বই', t: 'g' },
      { id: 'M50-mfs', en: 'MFS Disbursement', bn: 'এমএফএস বিতরণ', t: 'g' },
      { id: 'M50-chequepay', en: 'Cheque Payments', bn: 'চেকে পরিশোধ', t: 'g' },
      { id: 'M50-cashpay', en: 'Cash Payments', bn: 'নগদ পরিশোধ', t: 'g' }
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
      { id: 'M50-amendments', en: 'Facility Amendments', bn: 'সুবিধা সংশোধন', t: 'g' },
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
  forms: ['Bank Statement Import', 'Payment Instruction', 'Cash Deposit', 'Imprest Top-Up', 'Rider COD Settlement', 'Cheque Book', 'Facility Amendment', 'Reconciliation Statement'],
  cross: ['Financial Accounting & GL', 'AR, Invoicing & Collections', 'AP & Employee Expense'],
  freg: { src: 88, sub: [
    ['1', 'Bank Masters', 7, { model: 'account.journal', cols: ['name', 'code', 'bank_account_id', 'currency_id', 'fix_treasury_role'], screens: ['M50-accounts'], domain: [['type', '=', 'bank']] }],
    ['2', 'Statement & Recon', 13, { model: 'fix.bank.statement.line', cols: ['date', 'journal_id', 'reference', 'amount', 'match_state'], screens: ['M50-recon', 'M50-statements', 'M50-reconstatements', 'M50-recon-items', 'M50-rpt-recon', 'M50-rpt-charges'] }],
    ['3', 'Cash Position & Consolidation', 12, { model: 'fix.cash.position', cols: ['as_of', 'bank_balance', 'petty_cash_total', 'cash_in_transit_total', 'total_position'], screens: ['M50-position', 'M50-branchcash', 'M50-rpt-position', 'M50-cit'] }],
    ['4', 'Payment Execution', 13, { model: 'fix.payment.execution', cols: ['name', 'payee', 'amount', 'method', 'state'], screens: ['M50-beftn', 'M50-mfs', 'M50-cheques', 'M50-chequebooks', 'M50-chequepay', 'M50-cashpay'] }],
    ['5', 'Gateway/MFS Settlement', 11, { model: 'fix.gateway.settlement', cols: ['provider', 'settlement_date', 'total_net', 'exception_count', 'state'], screens: ['M50-gateway', 'M50-gateway-lines', 'M50-rpt-gateway', 'M50-ridercod'] }],
    ['6', 'Forecasting', 8, { model: 'fix.cash.forecast.item', cols: ['name', 'direction', 'category', 'amount', 'frequency'], screens: ['M50-forecast', 'M50-recurring'] }],
    ['7', 'Facilities & Trade Finance', 12, { model: 'fix.bank.facility', cols: ['name', 'lender_id', 'facility_type', 'limit_amount', 'state'], screens: ['M50-facilities', 'M50-amendments', 'M50-repayments', 'M50-covenants'] }],
    ['8', 'FX', 5, { model: 'fix.fx.revaluation', cols: ['rate_date', 'currency_id', 'total_gain', 'total_loss', 'net_amount'], screens: ['M50-fx'] }],
    ['9', 'Controls', 7, { model: 'fix.imprest.count', cols: ['fund_id', 'count_date', 'counted_amount', 'variance', 'state'], screens: ['M50-petty', 'M50-petty-counts', 'M50-petty-vouchers', 'M50-petty-topups'] }]
  ] }
};

const PAYMENT_COLS = ['name','payee','amount','method','rail','journal_id','state','approval_state','prepared_by_id','sent_by_id','bank_reference','bank_confirmed','executed_at'];
/* A08 workflow audit (M50-1..4): an accountant prepares, a different
 * Accounting Administrator releases (DOFA-authorised above the ceiling via
 * the M63 inbox); the bank's IMPORTED statement debit confirms. Workflow,
 * stamp and match fields are read-only on every form below. */
const PAYMENT_ACTIONS = [
  {m:'action_prepare',l:'Prepare for Release'},
  {m:'action_request_approval',l:'Request Authorisation'},
  {m:'action_recall_approval',l:'Recall Authorisation'},
  {m:'action_release',l:'Release to Bank'},
  {m:'action_confirm_bank',l:'Confirm from Statement'},
  {m:'action_mark_failed',l:'Bank Rejected'},
  {m:'action_retry',l:'Re-queue'},
  {m:'action_cancel',l:'Cancel'}
];

/* in-workspace data screens (checked before any stock Odoo view) */
export const SCREENS = {
  // ---- Cash
  'M50-position': { kind: 'model_list', create: false, model: 'fix.cash.position',
    cols: ['as_of','bank_balance','drawer_float_total','petty_cash_total','cash_in_transit_total','pending_payments','total_position'],
    actions: [{m:'action_take_snapshot',l:'Take Snapshot'}] },
  'M50-branchcash': { kind: 'table_report', module: 'M50', report: 'branch_cash' },
  'M50-ridercod': { kind: 'model_list', model: 'fix.cod.settlement',
    cols: ['name','rider_id','settlement_date','order_count','expected_amount','remitted_amount','variance','shortage_tier','recovery_state','state'],
    stateField: 'state',
    actions: [{m:'action_load_orders',l:'Load COD Orders'},{m:'action_submit',l:'Submit'},{m:'action_approve_shortage',l:'Approve Shortage',ask:'Why is the shortage accepted? (required above the escalation threshold)',kwarg:'note'},{m:'action_settle',l:'Settle'},{m:'action_dispute',l:'Dispute',ask:'Reason for the dispute',kwarg:'reason'},{m:'action_mark_recovered',l:'Shortage Recovered',ask:'Recovery reference (HR deduction / receipt)',kwarg:'reference'}] },
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
  'M50-reconstatements': { kind: 'model_list', model: 'fix.bank.reconciliation',
    cols: ['name','journal_id','period','statement_balance','gl_balance','unmatched_net','book_items_net','difference','unexplained_count','state','prepared_by_id','reviewed_by_id'],
    stateField: 'state',
    actions: [{m:'action_prepare',l:'Prepare from Ledger'},{m:'action_submit',l:'Submit for Review'},{m:'action_review',l:'Review & Sign Off'},{m:'action_return',l:'Return to Preparer',ask:'Why is it returned?',kwarg:'reason'}] },
  'M50-recon-items': { kind: 'model_list', model: 'fix.bank.reconciliation.line', create: false,
    cols: ['reconciliation_id','kind','date','reference','amount','counts','age_days','explanation','explained_by_id','state'],
    stateField: 'kind',
    actions: [{m:'action_explain',l:'Explain Item',ask:'Explanation of this reconciling item',kwarg:'explanation'}] },
  // ---- Execution
  'M50-beftn': { kind: 'model_list', model: 'fix.payment.execution',
    cols: PAYMENT_COLS, stateField: 'state', domain: [['method','=','bank_transfer']],
    context: { default_method: 'bank_transfer' }, actions: PAYMENT_ACTIONS },
  'M50-cheques': { kind: 'model_list', model: 'fix.cheque',
    cols: ['cheque_no','direction','partner_id','amount','cheque_date','is_pdc','journal_id','state','bounce_count'],
    stateField: 'state',
    actions: [{m:'action_deposit',l:'Deposit'},{m:'action_bounce',l:'Bounced'},{m:'action_cancel',l:'Void'}] },
  'M50-chequebooks': { kind: 'model_list', model: 'fix.cheque.book',
    cols: ['name','journal_id','first_number','last_number','next_number','state'],
    stateField: 'state', actions: [{m:'action_close',l:'Close Book'}] },
  'M50-mfs': { kind: 'model_list', model: 'fix.payment.execution',
    cols: PAYMENT_COLS, stateField: 'state', domain: [['method','=','mobile_fs']],
    context: { default_method: 'mobile_fs' }, actions: PAYMENT_ACTIONS },
  'M50-chequepay': { kind: 'model_list', model: 'fix.payment.execution',
    cols: PAYMENT_COLS, stateField: 'state', domain: [['method','=','cheque']],
    context: { default_method: 'cheque' }, actions: PAYMENT_ACTIONS },
  'M50-cashpay': { kind: 'model_list', model: 'fix.payment.execution',
    cols: PAYMENT_COLS, stateField: 'state', domain: [['method','=','cash']],
    context: { default_method: 'cash' }, actions: PAYMENT_ACTIONS },
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
    cols: ['name','lender_id','facility_type','limit_amount','utilised','available','utilisation_pct','next_due_date','next_due_amount','expiry_date','expiry_ack_by_id','state'],
    stateField: 'state',
    actions: [{m:'action_generate_schedule',l:'Generate Schedule'},{m:'action_activate',l:'Activate'},{m:'action_acknowledge_expiry',l:'Acknowledge Expiry'},{m:'action_close',l:'Close'}] },
  'M50-amendments': { kind: 'model_list', model: 'fix.facility.amendment',
    cols: ['facility_id','reason','new_limit_amount','new_interest_rate','new_instalments','new_next_due_date','state','requested_by_id','approved_by_id','approved_at'],
    stateField: 'state',
    actions: [{m:'action_approve',l:'Approve & Apply'},{m:'action_reject',l:'Reject'}] },
  'M50-repayments': { kind: 'model_list', model: 'fix.facility.repayment',
    cols: ['facility_id','sequence','due_date','principal','interest','total','state','is_overdue'],
    stateField: 'state', create: false, actions: [{m:'action_pay',l:'Pay Instalment'}] },
  'M50-covenants': { kind: 'model_list', model: 'fix.facility.covenant',
    cols: ['facility_id','name','metric','operator','threshold','state','last_value','last_result','last_tested'],
    stateField: 'state',
    actions: [{m:'action_approve',l:'Approve Covenant'},{m:'action_test',l:'Run Test'}] },
  'M50-fx': { kind: 'table_report', module: 'M50', report: 'fx_holdings', period: false },
  // ---- Reports
  'M50-rpt-position': { kind: 'table_report', module: 'M50', report: 'daily_cash_position', period: false },
  'M50-rpt-recon': { kind: 'table_report', module: 'M50', report: 'bank_recon_summary' },
  'M50-rpt-gateway': { kind: 'table_report', module: 'M50', report: 'gateway_recon' },
  'M50-rpt-cod': { kind: 'table_report', module: 'M50', report: 'cod_report' },
  'M50-rpt-charges': { kind: 'table_report', module: 'M50', report: 'bank_charges' },


  /* ===== A08 master-data forms (D365 in-workspace) ===== */
  'M50-form-fund': {
    kind: 'model_form',
    model: 'fix.imprest.fund',
    title: "Imprest Fund",
    back: 'M50-petty',
    status: { field: 'state', labels: { active: "Active", suspended: "Suspended", closed: "Closed" } },
    sections: [
      { title: "Fund",
        note: "An imprest (petty cash) fund per branch and custodian; the limit caps the float and the voucher limit caps a single payment.",
        fields: [
          { name: 'name', required: true, label: "Fund Name" },
          { name: 'operating_unit_id', required: true, label: "Operating Unit" },
          { name: 'branch_id', required: true, label: "Branch" },
          { name: 'custodian_id', required: true, label: "Custodian" },
          { name: 'imprest_limit', required: true, label: "Imprest Limit" },
          { name: 'voucher_limit', label: "Voucher Limit" },
          { name: 'account_id', required: true, label: "Imprest Account" },
          { name: 'state', readonly: true, label: "State" }
        ] }
    ]
  },
  'M50-form-voucher': {
    kind: 'model_form',
    model: 'fix.imprest.voucher',
    title: "Imprest Voucher",
    back: 'M50-petty-vouchers',
    status: { field: 'state', labels: { draft: "Draft", submitted: "Submitted", approved: "Approved", posted: "Posted" } },
    sections: [
      { title: "Voucher",
        note: "A petty-cash payment against the fund; the expense account and amount post to the GL on approval.",
        fields: [
          { name: 'fund_id', required: true, label: "Fund" },
          { name: 'voucher_date', required: true, label: "Voucher Date" },
          { name: 'description', required: true, label: "Description" },
          { name: 'payee', label: "Payee" },
          { name: 'expense_account_id', required: true, label: "Expense Account" },
          { name: 'amount', required: true, label: "Amount" },
          { name: 'receipt_ref', label: "Receipt Ref" },
          { name: 'state', readonly: true, label: "State" }
        ] }
    ]
  },
  'M50-form-count': {
    kind: 'model_form',
    model: 'fix.imprest.count',
    title: "Imprest Count",
    back: 'M50-petty-counts',
    status: { field: 'state', labels: { draft: "Draft", posted: "Posted" } },
    sections: [
      { title: "Count",
        note: "A cash count on a date; the variance to the book balance is computed by the model, not typed.",
        fields: [
          { name: 'fund_id', required: true, label: "Fund" },
          { name: 'count_date', required: true, label: "Count Date" },
          { name: 'counted_by_id', readonly: true, label: "Counted By" },
          { name: 'counted_amount', required: true, label: "Counted Amount" },
          { name: 'pending_vouchers_amount', readonly: true, label: "Approved Unposted Vouchers" },
          { name: 'variance', readonly: true, label: "Variance" },
          { name: 'state', readonly: true, label: "State" }
        ] }
    ]
  },
  'M50-form-journal': {
    kind: 'model_form',
    model: 'account.journal',
    title: "Bank / Cash Account",
    back: 'M50-accounts',
    sections: [
      { title: "Account",
        note: "A bank or cash journal. The treasury fields (routing number, branch, treasury role, signatories) drive the payment files.",
        fields: [
          { name: 'name', required: true, label: "Journal Name" },
          { name: 'code', required: true, label: "Short Code" },
          { name: 'type', required: true, label: "Type" },
          { name: 'currency_id', label: "Currency" },
          { name: 'bank_acc_number', label: "Bank Account Number" },
          { name: 'bank_id', label: "Bank" },
          { name: 'fix_routing_number', label: "Routing Number" },
          { name: 'fix_branch_name', label: "Bank Branch" },
          { name: 'fix_treasury_role', label: "Treasury Role" },
          { name: 'fix_signatories', label: "Signatories" },
          { name: 'active', label: "Active" }
        ] }
    ]
  },
  'M50-form-stmtline': {
    kind: 'model_form',
    model: 'fix.bank.statement.line',
    title: "Statement Line",
    back: 'M50-recon',
    status: { field: 'match_state', labels: { unmatched: "Unmatched", matched: "Matched", exception: "Exception" } },
    sections: [
      { title: "Statement Line",
        note: "One line of an imported bank statement (lines are never typed in). Pick the ONE document it pays or receives, then Confirm Manual Match; the amount and sign must agree.",
        fields: [
          { name: 'journal_id', readonly: true, label: "Journal" },
          { name: 'date', readonly: true, label: "Value Date" },
          { name: 'amount', readonly: true, label: "Amount" },
          { name: 'reference', readonly: true, label: "Reference" },
          { name: 'narration', readonly: true, label: "Narration" },
          { name: 'matched_payment_id', label: "Payment" },
          { name: 'matched_deposit_id', label: "Cash Deposit" },
          { name: 'matched_cheque_id', label: "Cheque" },
          { name: 'matched_gateway_id', label: "Gateway Settlement" },
          { name: 'match_state', readonly: true, label: "Match State" }
        ] }
    ]
  },
  'M50-form-cheque': {
    kind: 'model_form',
    model: 'fix.cheque',
    title: "Cheque",
    back: 'M50-cheques',
    status: { field: 'state', labels: { received: "Received", deposited: "Deposited", cleared: "Cleared", bounced: "Bounced" } },
    sections: [
      { title: "Cheque",
        note: "Post-dated cheques are held (is_pdc) until their date; a bounce records the reason and increments the count.",
        fields: [
          { name: 'direction', required: true, label: "Direction" },
          { name: 'cheque_no', required: true, label: "Cheque No" },
          { name: 'operating_unit_id', required: true, label: "Operating Unit" },
          { name: 'drawee_bank', label: "Drawee Bank" },
          { name: 'partner_id', label: "Partner" },
          { name: 'payee_name', label: "Payee Name" },
          { name: 'amount', required: true, label: "Amount" },
          { name: 'cheque_date', required: true, label: "Cheque Date" },
          { name: 'received_date', required: true, label: "Received Date" },
          { name: 'is_pdc', readonly: true, label: "Post-Dated" },
          { name: 'journal_id', label: "Journal" },
          { name: 'source_ref', label: "Source Document" },
          { name: 'bounce_reason', label: "Bounce Reason" },
          { name: 'state', readonly: true, label: "State" }
        ] }
    ]
  },
  'M50-form-gateway': {
    kind: 'model_form',
    model: 'fix.gateway.settlement',
    title: "Gateway Settlement",
    back: 'M50-gateway',
    status: { field: 'state', labels: { draft: "Draft", imported: "Imported — Awaiting Bank Credit", exceptions: "Exceptions", matched: "Three-Way Matched", posted: "Posted" } },
    sections: [
      { title: "Settlement",
        note: "A provider settlement batch (gross, fee, VAT, net). Attach the provider's CSV report, save, then Import Report on the list; the report hash pins the source file that was reconciled.",
        fields: [
          { name: 'provider', required: true, label: "Provider" },
          { name: 'provider_batch_ref', label: "Batch Reference" },
          { name: 'settlement_date', required: true, label: "Settlement Date" },
          { name: 'journal_id', required: true, label: "Journal" },
          { name: 'operating_unit_id', label: "Operating Unit" },
          { name: 'report_file', type: 'binary', accept: '.csv', filename: 'report_filename', label: "Settlement Report (CSV)" },
          { name: 'total_gross', readonly: true, label: "Gross" },
          { name: 'total_fee', readonly: true, label: "Fee" },
          { name: 'total_fee_vat', readonly: true, label: "Fee VAT" },
          { name: 'total_net', readonly: true, label: "Net" },
          { name: 'state', readonly: true, label: "State" }
        ] }
    ]
  },
  'M50-form-forecast': {
    kind: 'model_form',
    model: 'fix.cash.forecast.item',
    title: "Recurring Cash Item",
    back: 'M50-recurring',
    sections: [
      { title: "Recurring Item",
        note: "A standing inflow/outflow for the rolling cash forecast: direction, category, amount and frequency.",
        fields: [
          { name: 'name', required: true, label: "Item Name" },
          { name: 'direction', required: true, label: "Direction" },
          { name: 'category', required: true, label: "Category" },
          { name: 'amount', required: true, label: "Amount" },
          { name: 'frequency', required: true, label: "Frequency" },
          { name: 'start_date', required: true, label: "Start Date" },
          { name: 'end_date', label: "End Date" },
          { name: 'active', label: "Active" }
        ] }
    ]
  },
  'M50-form-facility': {
    kind: 'model_form',
    model: 'fix.bank.facility',
    title: "Bank Facility",
    back: 'M50-facilities',
    status: { field: 'state', labels: { draft: "Draft", active: "Active", closed: "Closed" } },
    tabs: [
      { id: 'sanction', label: 'Sanction', bn: 'অনুমোদন', icon: '📄' },
      { id: 'terms', label: 'Loan Terms', bn: 'ঋণের শর্ত', icon: '📅' },
      { id: 'accounts', label: 'GL & Bank', bn: 'হিসাব ও ব্যাংক', icon: '🏦' },
      { id: 'position', label: 'Position', bn: 'অবস্থান', icon: '📊' }
    ],
    sections: [
      { tab: 'sanction', title: "Facility",
        note: "A sanctioned credit line. Once active its terms change only through an approved amendment (Facility Amendments).",
        fields: [
          { name: 'name', required: true, label: "Facility Name" },
          { name: 'lender_id', required: true, label: "Lender" },
          { name: 'facility_type', required: true, label: "Facility Type" },
          { name: 'sanction_ref', label: "Sanction Ref" },
          { name: 'sanction_date', label: "Sanction Date" },
          { name: 'expiry_date', label: "Expiry Date" },
          { name: 'limit_amount', required: true, label: "Limit Amount" },
          { name: 'operating_unit_id', label: "Operating Unit" }
        ] },
      { tab: 'terms', title: "Terms",
        note: "A term or short-term loan needs the principal, tenor and first instalment date before Generate Schedule.",
        fields: [
          { name: 'principal', label: "Disbursed Principal" },
          { name: 'interest_rate', label: "Interest Rate %" },
          { name: 'tenor_months', label: "Tenor (months)" },
          { name: 'repayment_frequency', label: "Repayment Frequency" },
          { name: 'start_date', label: "First Instalment Date" }
        ] },
      { tab: 'accounts', title: "GL & Bank",
        note: "Activation needs the liability account utilisation is read from (an overdraft or cash credit may use its bank account). Instalments are paid from the bank account.",
        fields: [
          { name: 'liability_account_id', label: "Liability Account" },
          { name: 'journal_id', label: "Bank Account" }
        ] },
      { tab: 'position', title: "Position",
        note: "Read from the posted GL and the schedule; never typed.",
        fields: [
          { name: 'utilised', readonly: true, label: "Utilised" },
          { name: 'available', readonly: true, label: "Available" },
          { name: 'next_due_date', readonly: true, label: "Next Instalment Due" },
          { name: 'next_due_amount', readonly: true, label: "Next Instalment Amount" },
          { name: 'expiry_ack_by_id', readonly: true, label: "Expiry Alert Acknowledged By" },
          { name: 'expiry_ack_at', readonly: true, label: "Expiry Alert Acknowledged On" },
          { name: 'state', readonly: true, label: "State" }
        ] }
    ]
  },
  'M50-form-amendment': {
    kind: 'model_form',
    model: 'fix.facility.amendment',
    title: "Facility Amendment",
    back: 'M50-amendments',
    status: { field: 'state', labels: { draft: "Requested", approved: "Approved & Applied", rejected: "Rejected" } },
    sections: [
      { title: "Amendment",
        note: "A change to an active facility: requested here, approved by a different Accounting Administrator, which re-schedules the unpaid instalments. Leave a value empty to keep it unchanged.",
        fields: [
          { name: 'facility_id', required: true, label: "Facility" },
          { name: 'reason', required: true, label: "Reason (lender letter / board approval)" },
          { name: 'new_limit_amount', label: "New Sanctioned Limit" },
          { name: 'new_interest_rate', label: "New Interest Rate %" },
          { name: 'new_instalments', label: "Remaining Instalments" },
          { name: 'new_next_due_date', label: "Next Due Date" },
          { name: 'requested_by_id', readonly: true, label: "Requested By" },
          { name: 'approved_by_id', readonly: true, label: "Approved By" },
          { name: 'state', readonly: true, label: "State" }
        ] }
    ]
  },
  'M50-form-chequebook': {
    kind: 'model_form',
    model: 'fix.cheque.book',
    title: "Cheque Book",
    back: 'M50-chequebooks',
    status: { field: 'state', labels: { active: "In Use", exhausted: "Exhausted", closed: "Closed" } },
    sections: [
      { title: "Cheque Book",
        note: "A numbered book of one of our bank accounts. A cheque payment is refused until its paying account has a book in use; leaves are taken in order, so no number goes unaccounted for.",
        fields: [
          { name: 'name', required: true, label: "Book Name" },
          { name: 'journal_id', required: true, label: "Bank Account" },
          { name: 'first_number', required: true, label: "First Leaf" },
          { name: 'last_number', required: true, label: "Last Leaf" },
          { name: 'number_width', label: "Number Width" },
          { name: 'operating_unit_id', label: "Operating Unit" },
          { name: 'next_number', readonly: true, label: "Next Leaf" },
          { name: 'state', readonly: true, label: "State" }
        ] }
    ]
  },
  'M50-form-cod': {
    kind: 'model_form',
    model: 'fix.cod.settlement',
    title: "Rider COD Settlement",
    back: 'M50-ridercod',
    status: { field: 'state', labels: { draft: "Draft", submitted: "Submitted", settled: "Settled", disputed: "Disputed" } },
    tabs: [
      { id: 'remittance', label: 'Remittance', bn: 'জমা', icon: '💵' },
      { id: 'shortage', label: 'Shortage & Recovery', bn: 'ঘাটতি ও আদায়', icon: '⚠️' }
    ],
    sections: [
      { tab: 'remittance', title: "Remittance",
        note: "Name the rider, save, then Load COD Orders. Record what the rider remitted and where it was received; the expected amount comes from the delivered COD orders, never typed.",
        fields: [
          { name: 'name', readonly: true, label: "Settlement Ref" },
          { name: 'rider_id', required: true, label: "Rider" },
          { name: 'operating_unit_id', required: true, label: "Operating Unit" },
          { name: 'branch_id', label: "Receiving Branch" },
          { name: 'settlement_date', required: true, label: "Settlement Date" },
          { name: 'remittance_method', required: true, label: "Remittance Method" },
          { name: 'remittance_journal_id', label: "Received Into" },
          { name: 'remitted_amount', label: "Remitted" },
          { name: 'remittance_ref', label: "Remittance Ref / TrxID" },
          { name: 'order_count', readonly: true, label: "Orders" },
          { name: 'expected_amount', readonly: true, label: "COD Expected" },
          { name: 'variance', readonly: true, label: "Variance" },
          { name: 'state', readonly: true, label: "State" }
        ] },
      { tab: 'shortage', title: "Shortage & Recovery",
        note: "A booked shortage blocks the rider from further COD until it is recovered (BRU-TRE-04) and is handed to HR / payroll on settlement.",
        fields: [
          { name: 'shortage_tier', readonly: true, label: "Shortage Tier" },
          { name: 'shortage_approved_by_id', readonly: true, label: "Shortage Approved By" },
          { name: 'shortage_approval_note', readonly: true, label: "Why It Is Accepted" },
          { name: 'dispute_reason', label: "Dispute Reason" },
          { name: 'recovery_state', readonly: true, label: "Recovery" },
          { name: 'recovery_requested_at', readonly: true, label: "Handed to HR On" },
          { name: 'recovery_ref', label: "Recovery Reference" },
          { name: 'submitted_by_id', readonly: true, label: "Submitted By" },
          { name: 'settled_by_id', readonly: true, label: "Settled By" }
        ] }
    ]
  },
  'M50-form-recon': {
    kind: 'model_form',
    model: 'fix.bank.reconciliation',
    title: "Bank Reconciliation Statement",
    back: 'M50-reconstatements',
    status: { field: 'state', labels: { draft: "Draft", submitted: "Submitted for Review", reviewed: "Reviewed" } },
    tabs: [
      { id: 'statement', label: 'Statement', bn: 'বিবরণী', icon: '🏦' },
      { id: 'figures', label: 'Reconciliation', bn: 'মিলকরণ', icon: '🧮' },
      { id: 'signoff', label: 'Sign-Off', bn: 'অনুমোদন', icon: '✍️' }
    ],
    sections: [
      { tab: 'statement', title: "Bank Statement",
        note: "One statement per bank account and period (YYYY-MM). Save, Prepare from Ledger, enter the closing balance from the bank's statement and explain the items on Reconciling Items; a different Accounting Administrator reviews it.",
        fields: [
          { name: 'journal_id', required: true, label: "Bank Account" },
          { name: 'period', required: true, label: "Period (YYYY-MM)" },
          { name: 'statement_ref', label: "Bank Statement No. / Page" },
          { name: 'statement_balance', label: "Closing Balance per Statement" },
          { name: 'difference_note', label: "Explanation of the Difference" },
          { name: 'operating_unit_id', label: "Operating Unit" }
        ] },
      { tab: 'figures', title: "Reconciliation",
        note: "Statement balance + items in the books not on the statement = adjusted bank. GL balance + statement lines not in the books = adjusted book. Computed from the ledger and the imported lines.",
        fields: [
          { name: 'gl_balance', readonly: true, label: "Balance per GL" },
          { name: 'unmatched_net', readonly: true, label: "On Statement, Not in Books" },
          { name: 'book_items_net', readonly: true, label: "In Books, Not on Statement" },
          { name: 'adjusted_bank_balance', readonly: true, label: "Adjusted Bank Balance" },
          { name: 'adjusted_book_balance', readonly: true, label: "Adjusted Book Balance" },
          { name: 'difference', readonly: true, label: "Difference" },
          { name: 'item_count', readonly: true, label: "Reconciling Items" },
          { name: 'unexplained_count', readonly: true, label: "Unexplained" }
        ] },
      { tab: 'signoff', title: "Sign-Off",
        note: "The reviewer cannot be the preparer; the figures are recomputed at review.",
        fields: [
          { name: 'prepared_by_id', readonly: true, label: "Prepared By" },
          { name: 'prepared_at', readonly: true, label: "Prepared On" },
          { name: 'reviewed_by_id', readonly: true, label: "Reviewed By" },
          { name: 'reviewed_at', readonly: true, label: "Reviewed On" },
          { name: 'return_reason', readonly: true, label: "Returned Because" },
          { name: 'state', readonly: true, label: "State" }
        ] }
    ]
  },
  'M50-form-covenant': {
    kind: 'model_form',
    model: 'fix.facility.covenant',
    title: "Facility Covenant",
    back: 'M50-covenants',
    sections: [
      { title: "Covenant",
        note: "A financial covenant on a facility: the metric, operator and threshold; last value/result come from the last test.",
        fields: [
          { name: 'facility_id', required: true, label: "Facility" },
          { name: 'name', required: true, label: "Covenant" },
          { name: 'metric', required: true, label: "Metric" },
          { name: 'operator', required: true, label: "Operator" },
          { name: 'threshold', required: true, label: "Threshold" }
        ] }
    ]
  },

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
  'M50:Rider COD Settlement': 'fix.cod.settlement',
  'M50:Cheque Book': 'fix.cheque.book',
  'M50:Facility Amendment': 'fix.facility.amendment',
  'M50:Reconciliation Statement': 'fix.bank.reconciliation',
};

/* ============ D365 IN-WORKSPACE FORM SCREENS (M50 re-audit v2) ========
 * The registry's four data-entry chips open Dynamics-365 record forms in
 * the workspace — never an Odoo dialog. Merged into SCREENS (the meta
 * merger reads that export). */
Object.assign(SCREENS, {
  'M50-form-import': {
    kind: 'model_form',
    model: 'fix.bank.statement.import',
    title: 'Bank Statement Import',
    back: 'M50-statements',
    status: { field: 'state', labels: {
      draft: 'Draft', imported: 'Imported', duplicate: 'Duplicate File' } },
    sections: [
      { title: 'Statement Import', note: 'Pick the bank journal and format and attach the bank\'s CSV or MT940 file; save, then Import on the list. The import creates the statement lines, the only evidence that confirms a payment.',
        fields: [
          { name: 'journal_id', required: true, label: 'Bank Journal' },
          { name: 'format_type', required: true, label: 'Format' },
          { name: 'file', type: 'binary', accept: '.csv,.txt,.sta,.mt940,.940', filename: 'filename', label: 'Statement File' },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'imported_count', readonly: true, label: 'Lines Imported' },
          { name: 'state', readonly: true, label: 'State' }
        ] }
    ]
  },

  'M50-form-instruction': {
    kind: 'model_form',
    model: 'fix.payment.execution',
    title: 'Payment Instruction',
    back: 'M50-beftn',
    status: { field: 'state', labels: {
      pending: 'Draft', prepared: 'Prepared — Awaiting Release', sent: 'Released to Bank',
      executed: 'Confirmed by Bank', failed: 'Failed', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'instruction', label: 'Instruction', bn: 'নির্দেশনা', icon: '🧾' },
      { id: 'evidence', label: 'Bank & Justification', bn: 'ব্যাংক ও যৌক্তিকতা', icon: '🏦' },
      { id: 'authorisation', label: 'Authorisation', bn: 'অনুমোদন', icon: '✍️' }
    ],
    sections: [
      { tab: 'instruction', title: 'Instruction', note: 'Payment runs release their lines here as individual instructions on the chosen rail; a manual instruction records the same data for one-off payments.',
        fields: [
          { name: 'payee', required: true, label: 'Payee' },
          { name: 'partner_id', label: 'Payee Partner' },
          { name: 'partner_bank_id', label: 'Payee Bank Account' },
          { name: 'amount', required: true, label: 'Amount' },
          { name: 'method', required: true, label: 'Method' },
          { name: 'rail', label: 'Rail' },
          { name: 'journal_id', label: 'Paid From' },
          { name: 'value_date', label: 'Value Date' },
          { name: 'operating_unit_id', required: true, label: 'Operating Unit' }
        ] },
      { tab: 'evidence', title: 'Bank & Justification', note: 'The bank reference helps find the imported statement debit; it confirms nothing by itself.',
        fields: [
          { name: 'bank_reference', label: 'Bank Reference' },
          { name: 'failure_reason', label: 'Bank Rejection Reason' },
          { name: 'duplicate_reason', label: 'Not a Duplicate Because' },
          { name: 'dofa_justification', label: 'Authorisation Justification' }
        ] },
      { tab: 'authorisation', title: 'Authorisation', note: 'An accountant prepares, a different Accounting Administrator releases, an imported bank debit confirms.',
        fields: [
          { name: 'approval_state', readonly: true, label: 'Authorisation' },
          { name: 'prepared_by_id', readonly: true, label: 'Prepared By' },
          { name: 'sent_by_id', readonly: true, label: 'Released By' },
          { name: 'state', readonly: true, label: 'State' }
        ] }
    ]
  },

  'M50-form-deposit': {
    kind: 'model_form',
    model: 'fix.cash.deposit',
    title: 'Cash Deposit',
    back: 'M50-cit',
    status: { field: 'state', labels: {
      recorded: 'Recorded', in_transit: 'In Transit', deposited: 'Deposited',
      confirmed: 'Confirmed by Bank' } },
    sections: [
      { title: 'Cash-in-Transit', note: 'The branch cash day is deposited under a slip number; carrier tracks who moved the cash.',
        fields: [
          { name: 'branch_id', required: true, label: 'Branch' },
          { name: 'business_date', required: true, label: 'Cash Day' },
          { name: 'journal_id', required: true, label: 'Bank Journal' },
          { name: 'amount', required: true, label: 'Amount' },
          { name: 'slip_no', label: 'Deposit Slip No' },
          { name: 'carrier', label: 'Carrier' },
          { name: 'operating_unit_id', required: true, label: 'Operating Unit' },
          { name: 'variance_reason', label: 'Variance Explanation' },
          { name: 'state', readonly: true, label: 'State' }
        ] }
    ]
  },

  'M50-form-topup': {
    kind: 'model_form',
    model: 'fix.imprest.topup',
    title: 'Imprest Top-Up',
    back: 'M50-petty-topups',
    status: { field: 'state', labels: {
      draft: 'Draft', approved: 'Approved', disbursed: 'Disbursed' } },
    sections: [
      { title: 'Top-Up', note: 'Replenishes the petty-cash (imprest) fund back to its limit; the fund is selected and the amount is drawn from the bank journal.',
        fields: [
          { name: 'fund_id', required: true, label: 'Imprest Fund' },
          { name: 'amount', required: true, label: 'Amount' },
          { name: 'journal_id', required: true, label: 'Bank Journal' },
          { name: 'topup_date', required: true, label: 'Top-Up Date' },
          { name: 'state', readonly: true, label: 'State' }
        ] }
    ]
  }
});

export const FORM_CHIPS = {
  'M50:Imprest Fund': 'M50-form-fund',
  'M50:Imprest Voucher': 'M50-form-voucher',
  'M50:Imprest Count': 'M50-form-count',
  'M50:Bank / Cash Account': 'M50-form-journal',
  'M50:Statement Line': 'M50-form-stmtline',
  'M50:Cheque': 'M50-form-cheque',
  'M50:Gateway Settlement': 'M50-form-gateway',
  'M50:Recurring Cash Item': 'M50-form-forecast',
  'M50:Bank Facility': 'M50-form-facility',
  'M50:Facility Covenant': 'M50-form-covenant',
  'M50:Bank Statement Import': 'M50-form-import',
  'M50:Payment Instruction': 'M50-form-instruction',
  'M50:Cash Deposit': 'M50-form-deposit',
  'M50:Imprest Top-Up': 'M50-form-topup',
  'M50:Rider COD Settlement': 'M50-form-cod',
  'M50:Cheque Book': 'M50-form-chequebook',
  'M50:Facility Amendment': 'M50-form-amendment',
  'M50:Reconciliation Statement': 'M50-form-recon',
  'M50:__by_model__': {
    'fix.imprest.fund': 'M50-form-fund',
    'fix.imprest.voucher': 'M50-form-voucher',
    'fix.imprest.count': 'M50-form-count',
    'account.journal': 'M50-form-journal',
    'fix.bank.statement.line': 'M50-form-stmtline',
    'fix.cheque': 'M50-form-cheque',
    'fix.gateway.settlement': 'M50-form-gateway',
    'fix.cash.forecast.item': 'M50-form-forecast',
    'fix.bank.facility': 'M50-form-facility',
    'fix.facility.covenant': 'M50-form-covenant',
    'fix.bank.statement.import': 'M50-form-import',
    'fix.payment.execution': 'M50-form-instruction',
    'fix.cash.deposit': 'M50-form-deposit',
    'fix.imprest.topup': 'M50-form-topup',
    'fix.cod.settlement': 'M50-form-cod',
    'fix.cheque.book': 'M50-form-chequebook',
    'fix.facility.amendment': 'M50-form-amendment',
    'fix.bank.reconciliation': 'M50-form-recon'
  },
  'M50:__by_screen__': {
    'M50-petty': 'M50-form-fund',
    'M50-petty-vouchers': 'M50-form-voucher',
    'M50-petty-counts': 'M50-form-count',
    'M50-accounts': 'M50-form-journal',
    'M50-recon': 'M50-form-stmtline',
    'M50-cheques': 'M50-form-cheque',
    'M50-gateway': 'M50-form-gateway',
    'M50-recurring': 'M50-form-forecast',
    'M50-facilities': 'M50-form-facility',
    'M50-covenants': 'M50-form-covenant',
    'M50-statements': 'M50-form-import',
    'M50-beftn': 'M50-form-instruction',
    'M50-mfs': 'M50-form-instruction',
    'M50-cit': 'M50-form-deposit',
    'M50-petty-topups': 'M50-form-topup',
    'M50-ridercod': 'M50-form-cod',
    'M50-chequebooks': 'M50-form-chequebook',
    'M50-amendments': 'M50-form-amendment',
    'M50-reconstatements': 'M50-form-recon',
    'M50-chequepay': 'M50-form-instruction',
    'M50-cashpay': 'M50-form-instruction'
  }
};

/* the module's "+ New" surface */
export const CREATE = {
  M50: { screen: 'M50-form-instruction', model: 'fix.payment.execution', label: 'Payment Instruction' },
};
