/** @odoo-module **/
/* A08 · Finance & Treasury — M19 Financial Accounting & GL.
 * One file per A08 module (merged into P03_MODULES and the screen maps by
 * p03_modules_meta.js): the registry entry, the in-workspace data screens,
 * built-in report routes, data-entry form chips and the "+ New" surface. */

export const MODULE = {
  area: 'A08', code: 'M19', en: 'Financial Accounting & GL', title: 'M19 · Financial Accounting & GL',
  bn: 'আর্থিক হিসাব', icon: '💰',
  desc: 'Chart of accounts, 7-dimension model, subledger posting engine, July–June close, statutory statements.',
  kpis: [
    { l: 'Revenue MTD', m: 'revenue_mtd' },
    { l: 'Gross Margin', m: 'gross_margin_mtd' },
    { l: 'Close Progress', m: 'open_period_closes' },
    { l: 'IC Unmatched', m: 'ic_unmatched' },
    { l: 'TB Imbalance', m: 'tb_imbalance' },
    { l: 'Journals MTD', m: 'posted_moves_mtd' },
    { l: 'Drafts in Review', m: 'draft_journals' }
  ],
  groups: [
    { en: 'Ledger', screens: [
      { id: 'M19-coa', en: 'Chart of Accounts', bn: 'হিসাবের ছক', t: 'g' },
      { id: 'M19-journals', en: 'Journals', bn: 'জার্নাল', t: 'g' },
      { id: 'M19-je', en: 'Journal Entry', bn: 'জার্নাল এন্ট্রি', t: 'f' },
      { id: 'M19-tb', en: 'Trial Balance', bn: 'ট্রায়াল ব্যালেন্স', t: 'r' },
      { id: 'M19-dimensions', en: '7-Dimension Model', bn: 'মাত্রা মডেল', t: 'g' },
      { id: 'M19-coa-loader', en: 'CoA Master Loader', bn: 'হিসাবের ছক লোডার', t: 'c' },
      { id: 'M19-recurring', en: 'Recurring & Accrual Journals', bn: 'পুনরাবৃত্ত ও বকেয়া জার্নাল', t: 'g' }
    ]},
    { en: 'Close', screens: [
      { id: 'M19-close', en: 'Month-End Close Console', bn: 'মাসিক ক্লোজ', t: 'c' },
      { id: 'M19-periods', en: 'Periods & Locks', bn: 'পিরিয়ড', t: 'g' },
      { id: 'M19-close-sla', en: 'Close SLA Breaches', bn: 'ক্লোজ SLA লঙ্ঘন', t: 'r' },
      { id: 'M19-report-bridge', en: 'Statutory Report Bridge', bn: 'বিধিবদ্ধ প্রতিবেদন সেতু', t: 'g' },
      { id: 'M19-nil-returns', en: 'Nil-Return Packs', bn: 'শূন্য রিটার্ন প্যাক', t: 'g' }
    ]},
    { en: 'Statements', screens: [
      { id: 'M19-bs', en: 'Balance Sheet', bn: 'উত্তরপত্র', t: 'r' },
      { id: 'M19-pl', en: 'Profit & Loss', bn: 'লাভ-ক্ষতি', t: 'r' },
      { id: 'M19-cf', en: 'Cash Flow', bn: 'নগদ প্রবাহ', t: 'r' },
      { id: 'M19-consol', en: 'Consolidation', bn: 'সমন্বয়', t: 'r' }
    ]},
    { en: 'Controls', screens: [
      { id: 'M19-suspense', en: 'Suspense & Control Accounts', bn: 'সাসপেন্স', t: 'g' },
      { id: 'M19-recon', en: 'Subledger vs Control', bn: 'উপ-খতিয়ান মিলকরণ', t: 'c' },
      { id: 'M19-audit', en: 'Immutable Audit Trail', bn: 'নিরবচ্ছিন্ন অডিট', t: 'g' }
    ]},
    { en: 'Group & Inter-Branch', bn: 'গ্রুপ ও আন্তঃশাখা', screens: [
      { id: 'M19-consol-books', en: 'Consolidation Books', bn: 'একীভূতকরণ খাতা', t: 'c' },
      { id: 'M19-eliminations', en: 'Eliminations', bn: 'বাদকরণ', t: 'g' },
      { id: 'M19-ic-txns', en: 'Inter-Company / Inter-Branch Transactions', bn: 'আন্তঃকোম্পানি ও আন্তঃশাখা লেনদেন', t: 'g' },
      { id: 'M19-ic-balances', en: 'Due-To / Due-From Balances', bn: 'প্রদেয় ও প্রাপ্য স্থিতি', t: 'r' },
      { id: 'M19-ic-rules', en: 'Inter-Company Rules', bn: 'আন্তঃকোম্পানি নিয়ম', t: 'g' }
    ]}
  ],
  reports: ['Trial Balance', 'P&L (BFRS)', 'Balance Sheet', 'Cash Flow', 'Dimensional P&L by Branch', 'Close Checklist Report', 'Close SLA Breaches', 'Due-To / Due-From Balances'],
  forms: ['Journal Entry (manual/recurring)', 'Allocation Rule', 'Intercompany Charge', 'Recurring Journal Template', 'Nil Return Declaration'],
  cross: ['AR, Invoicing & Collections', 'AP & Employee Expense', 'Tax & Regulatory (BD)', 'Costing, Budget & FP&A'],
  freg: { src: 91, sub: [
    ['1', 'CoA & Dimensions', 12], ['2', 'Journals', 11], ['3', 'Subledger Posting Engine', 12],
    ['4', 'Fiscal Calendar & Close', 10], ['5', 'Multi-Entity & Consolidation', 9], ['6', 'Multi-Currency', 7],
    ['7', 'Statutory Statements', 9], ['8', 'Audit & Retention', 7], ['9', 'Accrual Framework', 8], ['10', 'Controls & SoD', 6]
  ] }
};

/* in-workspace data screens (checked before any stock Odoo view) */
export const SCREENS = {
  'M19-coa': { kind: 'coa' },
  'M19-journals': { kind: 'journals' },
  'M19-je': { kind: 'je_editor' },
  'M19-tb': { kind: 'statement', report: 'trial_balance' },
  'M19-dimensions': { kind: 'dimensions' },
  'M19-close': { kind: 'close' },
  'M19-periods': { kind: 'periods' },
  'M19-bs': { kind: 'statement', report: 'balance_sheet' },
  'M19-pl': { kind: 'statement', report: 'pnl' },
  'M19-cf': { kind: 'statement', report: 'cash_flow' },
  'M19-consol': { kind: 'statement', report: 'consolidated' },
  'M19-suspense': { kind: 'suspense' },
  'M19-recon': { kind: 'recon' },
  'M19-audit': { kind: 'audit' },

  /* A08 additions — generic screens over the real models (controllers/a08/m19.py) */
  'M19-coa-loader': { kind: 'model_list', model: 'fix.chart.loader', stateField: 'state',
    cols: ['company_id', 'loaded_at', 'account_count', 'postable_count', 'linked_count',
      'reconciled_at', 'recon_discrepancy', 'unmapped_ledger_count', 'state'],
    actions: [
      { m: 'action_load_from_csv', l: 'Load MD-035 Chart' },
      { m: 'action_link_odoo_accounts', l: 'Link to Ledger Accounts' },
      { m: 'action_reconcile_chart', l: 'Reconcile with Ledger' },
    ] },
  'M19-recurring': { kind: 'model_list', model: 'fix.journal.template', stateField: 'state',
    cols: ['name', 'journal_id', 'schedule', 'next_run_date', 'auto_reverse', 'run_count',
      'last_run_date', 'last_move_id', 'activated_by_id', 'state'],
    actions: [
      { m: 'action_activate', l: 'Activate' },
      { m: 'action_generate_entry', l: 'Generate Due Entry' },
      { m: 'action_pause', l: 'Pause' },
    ] },
  'M19-close-sla': { kind: 'table_report', module: 'M19', report: 'close_sla', period: false },
  'M19-report-bridge': { kind: 'model_list', model: 'fix.financial.report.bridge',
    cols: ['name', 'report_type', 'fiscal_year_id', 'date_from', 'date_to', 'generated_at',
      'line_count', 'headline_amount', 'is_balanced'],
    actions: [{ m: 'action_generate_report', l: 'Generate from Ledger' }] },
  'M19-nil-returns': { kind: 'model_list', model: 'fix.nil.return.generator', stateField: 'state',
    cols: ['name', 'entity_id', 'period_year', 'period_month', 'due_date', 'transaction_count',
      'eligible_for_nil_return', 'filing_reference', 'state'],
    actions: [
      { m: 'action_verify_eligibility', l: 'Verify Eligibility' },
      { m: 'action_generate_nil_packs', l: 'Generate Nil Packs' },
      { m: 'action_submit_to_nbr', l: 'Record NBR Acknowledgement' },
    ] },
  'M19-consol-books': { kind: 'model_list', model: 'fix.consolidation.book', stateField: 'state',
    cols: ['code', 'name', 'parent_entity_id', 'consolidation_date', 'total_subsidiary_revenue',
      'total_eliminations', 'net_consolidated_profit', 'consolidated_assets',
      'consolidated_liabilities', 'run_by_id', 'state'],
    actions: [
      { m: 'action_run_consolidation', l: 'Run Consolidation' },
      { m: 'action_generate_eliminations', l: 'Generate Eliminations' },
      { m: 'action_close', l: 'Close Book' },
    ] },
  'M19-eliminations': { kind: 'model_list', model: 'fix.elimination.entry', create: false,
    cols: ['book_id', 'name', 'elimination_type', 'from_entity_id', 'to_entity_id', 'amount',
      'reference'] },
  'M19-ic-txns': { kind: 'model_list', model: 'fix.intercompany.transaction', stateField: 'state',
    cols: ['reference', 'name', 'scope', 'source_entity_id', 'target_entity_id',
      'source_branch_id', 'target_branch_id', 'transaction_date', 'amount',
      'mirror_invoice_ref', 'match_difference', 'state'],
    actions: [
      { m: 'action_generate_mirror', l: 'Post & Mirror' },
      { m: 'action_match', l: 'Match Against Ledger' },
      { m: 'action_mark_settled', l: 'Mark Settled' },
    ] },
  'M19-ic-balances': { kind: 'table_report', module: 'M19', report: 'ic_balances' },
  'M19-ic-rules': { kind: 'model_list', model: 'fix.intercompany.rule',
    cols: ['code', 'name', 'scope', 'source_entity_id', 'target_entity_id', 'transaction_type',
      'markup_percent', 'transfer_pricing_compliant', 'active'] },
};

/* built-in report chips -> the screen that shows that report */
export const REPORT_ROUTES = {
  "M19:Trial Balance": "M19-tb",
  "M19:P&L (BFRS)": "M19-pl",
  "M19:Balance Sheet": "M19-bs",
  "M19:Cash Flow": "M19-cf",
  "M19:Dimensional P&L by Branch": "M19-dimensions",
  "M19:Close Checklist Report": "M19-close",
  "M19:Close SLA Breaches": "M19-close-sla",
  "M19:Due-To / Due-From Balances": "M19-ic-balances",
};

/* data-entry form chips -> real model forms */
export const FORM_MODELS = {
  'M19:Journal Entry (manual/recurring)': 'account.move',
  'M19:Allocation Rule': 'fix.allocation.rule',
  'M19:Intercompany Charge': 'fix.intercompany.transaction',
  'M19:Recurring Journal Template': 'fix.journal.template',
  'M19:Nil Return Declaration': 'fix.nil.return.generator',
};

/* the module's "+ New" surface */
export const CREATE = {
  M19: { model: 'account.move', label: 'Journal Entry' },
};
