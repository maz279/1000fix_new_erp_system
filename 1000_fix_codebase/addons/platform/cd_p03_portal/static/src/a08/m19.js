/** @odoo-module **/
/* A08 · Finance & Treasury — M19 Financial Accounting & GL.
 * One file per A08 module (merged into P03_MODULES and the screen maps by
 * p03_modules_meta.js): the registry entry, the in-workspace data screens,
 * built-in report routes, data-entry form chips and the "+ New" surface. */

export const MODULE = {
  area: 'A08', code: 'M19', en: 'Financial Accounting & GL', title: 'M19 · Financial Accounting & GL',
  bn: 'আর্থিক হিসাব', icon: '📒',
  desc: 'Chart of accounts, 7-dimension model, subledger posting engine, July–June close, statutory statements.',
  kpis: [
    { l: 'Revenue MTD', m: 'revenue_mtd', prefix: '৳ ' },
    { l: 'Gross Margin', m: 'gross_margin_mtd' },
    { l: 'Close Progress', m: 'open_period_closes' },
    { l: 'IC Unmatched', m: 'ic_unmatched' },
    { l: 'TB Imbalance', m: 'tb_imbalance' },
    { l: 'Journals MTD', m: 'posted_moves_mtd' },
    { l: 'Drafts in Review', m: 'draft_journals' },
    { l: 'Legacy AR Rows', m: 'legacy_ledger_rows' },
    { l: 'Legacy AR Net', m: 'legacy_ledger_net', prefix: '৳ ' },
    { l: 'Legacy AR Branches', m: 'legacy_ledger_branches' }
  ],
  groups: [
    { en: 'Record Coverage', screens: [
      { id: 'M19-chart-account', en: "Chart of Accounts", bn: "হিসাবের ছক", t: 'g' },
      { id: 'M19-fiscal-period-bridge', en: "Fiscal Period Bridge", bn: "Fiscal Period Bridge", t: 'g' },
      { id: 'M19-journal-dimension', en: "Journal Dimension", bn: "Journal Dimension", t: 'g' },
      { id: 'M19-period-close', en: "Period Close", bn: "Period Close", t: 'g' }
    ]},
    { en: 'Ledger', screens: [
      { id: 'M19-fx-revaluation', en: 'FX Revaluation (IAS 21)', bn: 'বৈদেশিক মুদ্রা পুনর্মূল্যায়ন', t: 'g' },
      { id: 'M19-coa', en: 'Chart of Accounts (Statutory Register)', bn: 'হিসাবের ছক (বিধিবদ্ধ রেজিস্টার)', t: 'g' },
      { id: 'M19-journals', en: 'Journals', bn: 'জার্নাল', t: 'g' },
      { id: 'M19-je', en: 'Journal Entry', bn: 'জার্নাল এন্ট্রি', t: 'f' },
      { id: 'M19-tb', en: 'Trial Balance', bn: 'ট্রায়াল ব্যালেন্স', t: 'r' },
      { id: 'M19-partner-ledger', en: 'Partner Ledger (GL)', bn: 'পার্টনার খতিয়ান (GL)', t: 'r' },
      { id: 'M19-partner-statement', en: 'Partner Statement Drill-down', bn: 'পার্টনার স্টেটমেন্ট', t: 'r' },
      { id: 'M19-takeon', en: 'Legacy Take-on Wizard', bn: 'লেগেসি টেক-অন উইজার্ড', t: 'c' },
      { id: 'M19-takeon-lines', en: 'Take-on Lines (audit)', bn: 'টেক-অন লাইন (অডিট)', t: 'g' },
      { id: 'M19-dimensions', en: '7-Dimension Model', bn: 'মাত্রা মডেল', t: 'g' },
      { id: 'M19-coa-loader', en: 'CoA Master Loader', bn: 'হিসাবের ছক লোডার', t: 'c' },
      { id: 'M19-coa-register', en: 'CoA Register Pack', bn: 'হিসাবের ছক রেজিস্টার প্যাক', t: 'r' },
      { id: 'M19-recurring', en: 'Recurring & Accrual Journals', bn: 'পুনরাবৃত্ত ও বকেয়া জার্নাল', t: 'g' },
      { id: 'M19-alloc-rules', en: 'Allocation Rules', bn: 'বরাদ্দ নিয়ম', t: 'g' }
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
      { id: 'M19-audit', en: 'Immutable Audit Trail', bn: 'নিরবচ্ছিন্ন অডিট', t: 'g' },
      { id: 'M19-reopens', en: 'Period Reopen Requests', bn: 'পিরিয়ড পুনরায় খোলার অনুরোধ', t: 'g' },
      { id: 'M19-control-changes', en: 'Control Account Changes', bn: 'নিয়ন্ত্রণ হিসাব পরিবর্তন', t: 'g' },
      { id: 'M19-tp-rates', en: 'Transfer-Pricing Rates', bn: 'স্থানান্তর মূল্য হার', t: 'g' }
    ]},
    { en: 'Group & Inter-Branch', bn: 'গ্রুপ ও আন্তঃশাখা', screens: [
      { id: 'M19-consol-books', en: 'Consolidation Books', bn: 'একীভূতকরণ খাতা', t: 'c' },
      { id: 'M19-eliminations', en: 'Eliminations', bn: 'বাদকরণ', t: 'g' },
      { id: 'M19-ic-txns', en: 'Inter-Company / Inter-Branch Transactions', bn: 'আন্তঃকোম্পানি ও আন্তঃশাখা লেনদেন', t: 'g' },
      { id: 'M19-ic-balances', en: 'Due-To / Due-From Balances', bn: 'প্রদেয় ও প্রাপ্য স্থিতি', t: 'r' },
      { id: 'M19-ic-rules', en: 'Inter-Company Rules', bn: 'আন্তঃকোম্পানি নিয়ম', t: 'g' }
    ]},
    { en: 'Legacy AR Ledger (201)', bn: 'লেগেসি প্রাপ্য খতিয়ান (২০১)', screens: [
      { id: 'M19-legacy-ledger', en: 'Legacy Control-Ledger Import', bn: 'লেগেসি কন্ট্রোল খতিয়ান ইম্পোর্ট', t: 'c' },
      { id: 'M19-legacy-ledger-lines', en: 'Archive Lines (audit)', bn: 'আর্কাইভ লাইন (অডিট)', t: 'g' },
      { id: 'M19-legacy-ar-recon', en: 'Legacy AR Control Recon', bn: 'লেগেসি প্রাপ্য নিয়ন্ত্রণ মিলকরণ', t: 'r' }
    ]},
    { en: 'Legacy Bank Ledgers', bn: 'লেগেসি ব্যাংক খতিয়ান', screens: [
      { id: 'M19-bank-takeon', en: 'Bank-Ledger Take-on', bn: 'ব্যাংক খতিয়ান টেক-অন', t: 'c' },
      { id: 'M19-bank-takeon-lines', en: 'Take-on Lines (audit)', bn: 'টেক-অন লাইন (অডিট)', t: 'g' }
    ]}
  ],
  reports: ['Trial Balance', 'P&L (BFRS)', 'Balance Sheet', 'Cash Flow', 'Dimensional P&L by Branch', 'Close Checklist Report', 'Close SLA Breaches', 'Due-To / Due-From Balances', 'Partner Ledger (GL)', 'Partner Statement Drill-down', 'Legacy AR Control Reconciliation'],
  forms: ['Journal Entry (manual/recurring)', 'Allocation Rule', 'Intercompany Charge', 'Recurring Journal Template', 'Nil Return Declaration', 'Legacy Partner-Ledger Take-on', 'Legacy GL Control-Ledger Import', 'Legacy Bank-Ledger Take-on'],
  cross: ['AR, Invoicing & Collections', 'AP & Employee Expense', 'Tax & Regulatory (BD)', 'Costing, Budget & FP&A'],
  freg: { src: 95, sub: [
    ['1', 'CoA & Dimensions', 12, { model: 'fix.chart.account', cols: ['account_code', 'name', 'account_type', 'is_postable', 'is_control_account'], screens: ['M19-coa', 'M19-chart-account', 'M19-dimensions', 'M19-coa-loader', 'M19-control-changes'] }],
    ['2', 'Journals', 15, { model: 'account.journal', cols: ['name', 'code', 'type', 'default_account_id', 'currency_id'], screens: ['M19-journals', 'M19-je', 'M19-partner-ledger', 'M19-partner-statement', 'M19-takeon', 'M19-takeon-lines'] }],
    ['3', 'Subledger Posting Engine', 12, { model: 'fix.journal.dimension', cols: ['move_line_id', 'branch_id', 'cost_centre', 'business_line', 'channel'], screens: ['M19-journal-dimension', 'M19-recon', 'M19-tb'] }],
    ['4', 'Fiscal Calendar & Close', 10, { model: 'fix.period.close', cols: ['period_end', 'state', 'sla_status', 'target_completion_date', 'closed_at'], screens: ['M19-close', 'M19-periods', 'M19-period-close', 'M19-close-sla', 'M19-reopens'] }],
    ['5', 'Multi-Entity & Consolidation', 9, { model: 'fix.consolidation.book', cols: ['code', 'name', 'consolidation_date', 'net_consolidated_profit', 'state'], screens: ['M19-consol-books', 'M19-eliminations', 'M19-ic-txns', 'M19-consol', 'M19-tp-rates'] }],
    ['6', 'Multi-Currency', 7, { model: 'fix.fx.revaluation', cols: ['name', 'rate_date', 'currency_id', 'net_amount', 'state'], screens: ['M19-fx-revaluation'] }],
    ['7', 'Statutory Statements', 9, { model: 'fix.financial.report.bridge', cols: ['name', 'report_type', 'date_from', 'date_to', 'is_balanced'], screens: ['M19-report-bridge', 'M19-bs', 'M19-pl', 'M19-cf'] }],
    ['8', 'Audit & Retention', 7, { model: 'fix.fiscal.period.bridge', cols: ['fiscal_year_id', 'period_close_id', 'is_locked', 'locked_at'], screens: ['M19-audit', 'M19-fiscal-period-bridge'] }],
    ['9', 'Accrual Framework', 8, { model: 'fix.journal.template', cols: ['name', 'schedule', 'next_run_date', 'auto_reverse', 'state'], screens: ['M19-recurring', 'M19-alloc-rules'] }],
    ['10', 'Controls & SoD', 6, { model: 'fix.sod.control', cols: ['code', 'name', 'role_a_id', 'role_b_id', 'conflict_action'], screens: ['M19-suspense'] }],
    ['11', 'Legacy AR Control Archive', 3, { model: 'fix.legacy.ledger.batch', cols: ['name', 'state', 'line_count', 'branch_count', 'total_net'], screens: ['M19-legacy-ledger', 'M19-legacy-ledger-lines', 'M19-legacy-ar-recon'] }],
    ['12', 'Legacy Bank-Ledger Take-on', 2, { model: 'fix.bank.takeon.batch', cols: ['name', 'state', 'bank_gl_code', 'date_from', 'date_to', 'line_count', 'branch_count', 'total_net'], screens: ['M19-bank-takeon', 'M19-bank-takeon-lines'] }]
  ] }
};

/* in-workspace data screens (checked before any stock Odoo view) */
export const SCREENS = {
  'M19-fx-revaluation': { kind: 'model_list', model: 'fix.fx.revaluation', stateField: 'state',
    cols: ['name', 'rate_date', 'currency_id', 'total_gain', 'total_loss', 'net_amount', 'state'],
    actions: [{ m: 'action_compute', l: 'Compute' }, { m: 'action_post', l: 'Post' }] },
  'M19-rpt-fx': { kind: 'table_report', module: 'M19', report: 'fx_revaluation', title: 'FX Revaluation', period: false },
  'M19-form-fx': {
    kind: 'model_form',
    model: 'fix.fx.revaluation',
    title: 'FX Revaluation Run',
    back: 'M19-fx-revaluation',
    status: { field: 'state', labels: { draft: 'Draft', computed: 'Computed', posted: 'Posted' } },
    sections: [
      { title: 'Run', note: 'Compute restates every open foreign-currency receivable and payable at the closing rate (IAS 21); Post writes one entry for the net unrealized gain or loss.',
        fields: [
          { name: 'rate_date', required: true, label: 'Closing Rate Date' },
          { name: 'journal_id', required: true, label: 'Journal' },
          { name: 'gain_account_id', label: 'Unrealized FX Gain Account' },
          { name: 'loss_account_id', label: 'Unrealized FX Loss Account' },
          { name: 'state', readonly: true, label: 'State' },
          { name: 'computed_by_id', readonly: true, label: 'Computed By' },
          { name: 'posted_by_id', readonly: true, label: 'Posted By (reviewer)' },
          { name: 'move_id', readonly: true, label: 'Revaluation Entry' },
          { name: 'reversal_move_id', readonly: true, label: 'Reversal Entry (next day)' }
        ] }
    ]
  },
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

  /* Partner ledger surfaces (2026-11-08 report R-2/R-11) — GL truth under
   * the AR subledger: legacy take-on lines and any posting that bypassed the
   * AR/AP engines appear here and only here. */
  'M19-partner-ledger': { kind: 'table_report', module: 'M19', report: 'partner_ledger', title: 'Partner Ledger (GL)', period: true },
  'M19-partner-statement': { kind: 'table_report', module: 'M19', report: 'partner_statement', title: 'Partner Statement Drill-down', period: true },

  /* Legacy take-on wizard (R-1b) — the guided cut-over path */
  'M19-takeon': { kind: 'model_list', model: 'fix.ledger.takeon.batch', create: true,
    cols: ['name', 'state', 'takeon_date', 'line_count', 'linked_count', 'created_count', 'gl_mapped_count', 'quarantined_count', 'total_balance'],
    stateField: 'state',
    actions: [
      { m: 'action_stage', l: '1. Stage spreadsheet' },
      { m: 'action_validate', l: '2. Validate & match' },
      { m: 'action_import', l: '3. Import parties (governed)' },
      { m: 'action_post', l: '4. Post opening entry' },
      { m: 'action_rollback', l: 'Rollback (mirror entry)' },
    ] },
  'M19-takeon-lines': { kind: 'model_list', model: 'fix.ledger.takeon.line', create: false,
    cols: ['row_no', 'raw_name', 'clean_name', 'legacy_reference', 'line_state', 'suspense_kind', 'debit', 'credit', 'balance', 'matched_partner_id', 'created_partner_id'],
    stateField: 'line_state' },

  /* Legacy GL control-ledger import (2026-11-09 AR 201 report) — the
   * archive lane: read-only per-line evidence + ONE branch-dimensioned
   * control entry. The reconciliation pack proves archive vs GL vs the
   * partner take-on (different scopes, stated not hidden). */
  'M19-legacy-ledger': { kind: 'model_list', model: 'fix.legacy.ledger.batch', create: true,
    cols: ['name', 'state', 'legacy_account_code', 'date_from', 'date_to', 'line_count', 'linked_count', 'quarantined_count', 'branch_count', 'total_debit', 'total_credit', 'total_net'],
    stateField: 'state',
    actions: [
      { m: 'action_stage', l: '1. Stage spreadsheet' },
      { m: 'action_validate', l: '2. Validate & resolve branches' },
      { m: 'action_post', l: '3. Post control entry (MIG)' },
      { m: 'action_rollback', l: 'Rollback (mirror entry)' },
    ] },
  'M19-legacy-ledger-lines': { kind: 'model_list', model: 'fix.legacy.ledger.line', create: false,
    cols: ['row_no', 'entry_date', 'journal_prefix', 'journal_entry', 'invoice_ref', 'branch_raw', 'branch_resolved_id', 'line_state', 'debit', 'credit', 'balance', 'created_by_name', 'notes'],
    stateField: 'line_state' },
  'M19-legacy-ar-recon': { kind: 'table_report', module: 'M19', report: 'legacy_ar_control', title: 'Legacy AR Control Reconciliation', period: false },
  'M19-form-legacy-ledger': {
    kind: 'model_form', model: 'fix.legacy.ledger.batch',
    title: 'Legacy GL Control-Ledger Import', back: 'M19-legacy-ledger',
    status: { field: 'state', labels: {
      draft: 'Draft', staged: 'Staged', validated: 'Validated',
      posted: 'Control Entry Posted', rolled_back: 'Rolled Back' } },
    tabs: [
      { id: 'lsrc', label: '1. Source', bn: '১. সোর্স', icon: '📄', badge: '4' },
      { id: 'lout', label: '2. Outcome', bn: '২. ফলাফল', icon: '📊', badge: '8' },
      { id: 'llog', label: '3. Decision Log', bn: '৩. সিদ্ধান্ত লগ', icon: '🗂️', badge: '1' }
    ],
    sections: [
      { tab: 'lsrc', title: 'Legacy Ledger Statement & Control Account',
        note: "Attach the legacy control-account export (Date / Journal Entry / Branch / Company / Created by / Created on / Debit / Credit / Balance — the 201 Account Receivable statement). Save, then run Stage → Validate → Post from the list's command bar. Posting lands ONE branch-dimensioned control entry on a dedicated legacy control account (never a receivable account: the lines are anonymous) through the governed M19 funnel.",
        fields: [
          { name: 'name', label: 'Import', readonly: true },
          { name: 'source_file', label: 'Legacy Ledger (.xlsx)', type: 'file' },
          { name: 'source_filename', label: 'File Name' },
          { name: 'legacy_account_code', label: 'Legacy Account Code (e.g. 100201)', required: true },
          { name: 'import_ref', label: 'Import Reference', readonly: true },
          { name: 'control_account_id', label: 'Legacy Control Account (auto-created at post)' },
          { name: 'contra_account_id', label: 'Take-on Contra Account (auto at post)' }
        ] },
      { tab: 'lout', title: 'Counts & Position',
        fields: [
          { name: 'line_count', label: 'Archive Rows', readonly: true },
          { name: 'linked_count', label: 'Branch-Resolved Rows', readonly: true },
          { name: 'quarantined_count', label: 'Quarantined Rows', readonly: true },
          { name: 'branch_count', label: 'Distinct Branches', readonly: true },
          { name: 'date_from', label: 'Value Dates From', readonly: true },
          { name: 'date_to', label: 'Value Dates To', readonly: true },
          { name: 'total_debit', label: 'Total Debit (BDT)', readonly: true },
          { name: 'total_credit', label: 'Total Credit (BDT)', readonly: true },
          { name: 'total_net', label: 'Net Legacy Position (BDT)', readonly: true },
          { name: 'posted_move_id', label: 'Control Entry', readonly: true }
        ] },
      { tab: 'llog', title: 'Audit Trail',
        fields: [
          { name: 'decision_log', label: 'Decision Log (who, when, what)', readonly: true, type: 'text' }
        ] }
    ]
  },
  /* Legacy bank-ledger take-on (2026-11-09 AB Bank capability report
   * R2 Option B / R3): row-level history onto the bank GL named in the
   * export title — the guided path the LEGACY-AB load walked. */
  'M19-bank-takeon': { kind: 'model_list', model: 'fix.bank.takeon.batch', create: true,
    cols: ['name', 'state', 'bank_gl_code', 'bank_gl_account_id', 'date_from', 'date_to', 'line_count', 'linked_count', 'quarantined_count', 'branch_count', 'total_debit', 'total_credit', 'total_net'],
    stateField: 'state',
    actions: [
      { m: 'action_stage', l: '1. Stage spreadsheet' },
      { m: 'action_validate', l: '2. Validate & resolve branches' },
      { m: 'action_post', l: '3. Post row-level history (MIG)' },
      { m: 'action_rollback', l: 'Rollback (combined mirror)' },
    ] },
  'M19-bank-takeon-lines': { kind: 'model_list', model: 'fix.bank.takeon.line', create: false,
    cols: ['row_no', 'entry_date', 'journal_entry', 'branch_raw', 'branch_resolved_id', 'line_state', 'debit', 'credit', 'balance', 'created_by_name', 'notes'],
    stateField: 'line_state' },
  'M19-form-bank-takeon': {
    kind: 'model_form', model: 'fix.bank.takeon.batch',
    title: 'Legacy Bank-Ledger Take-on', back: 'M19-bank-takeon',
    status: { field: 'state', labels: {
      draft: 'Draft', staged: 'Staged', validated: 'Validated',
      posted: 'History Posted', rolled_back: 'Rolled Back' } },
    tabs: [
      { id: 'bsrc', label: '1. Source', bn: '১. সোর্স', icon: '📄', badge: '5' },
      { id: 'bout', label: '2. Outcome', bn: '২. ফলাফল', icon: '📊', badge: '8' },
      { id: 'blog', label: '3. Decision Log', bn: '৩. সিদ্ধান্ত লগ', icon: '🗂️', badge: '1' }
    ],
    sections: [
      { tab: 'bsrc', title: 'Bank Ledger Statement & Target GL',
        note: "Attach the bank ledger export ('Ledger Statement: <GL code> <name>' title + Date / Journal Entry / Branch / Company / Created by / Created on / Debit / Credit / Balance). Save, then run Stage → Validate → Post from the list's command bar. Every source row posts as its own dated entry on the bank GL through the governed M19 funnel — bank history, never bank-statement evidence (that path stays with M50 Statements Import).",
        fields: [
          { name: 'name', label: 'Take-on', readonly: true },
          { name: 'source_file', label: 'Bank Ledger (.xlsx)', type: 'file' },
          { name: 'source_filename', label: 'File Name' },
          { name: 'bank_gl_code', label: 'Bank GL Code (captured from the title)' },
          { name: 'import_ref', label: 'Import Reference', readonly: true },
          { name: 'bank_gl_account_id', label: 'Bank GL (resolved at validate)' },
          { name: 'contra_account_id', label: 'Take-on Contra Account (auto at post)' },
          { name: 'company_id', label: 'Company' }
        ] },
      { tab: 'bout', title: 'Counts & Position',
        fields: [
          { name: 'line_count', label: 'Staged Rows', readonly: true },
          { name: 'linked_count', label: 'Branch-Resolved Rows', readonly: true },
          { name: 'quarantined_count', label: 'Quarantined Rows', readonly: true },
          { name: 'posted_count', label: 'Posted Rows', readonly: true },
          { name: 'branch_count', label: 'Distinct Branches', readonly: true },
          { name: 'date_from', label: 'Value Dates From', readonly: true },
          { name: 'date_to', label: 'Value Dates To', readonly: true },
          { name: 'total_debit', label: 'Total Debit (BDT)', readonly: true },
          { name: 'total_credit', label: 'Total Credit (BDT)', readonly: true },
          { name: 'total_net', label: 'Net Movement (BDT)', readonly: true }
        ] },
      { tab: 'blog', title: 'Audit Trail',
        fields: [
          { name: 'decision_log', label: 'Decision Log (who, when, what)', readonly: true, type: 'text' }
        ] }
    ]
  },
  'M19-form-takeon': {
    kind: 'model_form', model: 'fix.ledger.takeon.batch',
    title: 'Legacy Partner-Ledger Take-on', back: 'M19-takeon',
    status: { field: 'state', labels: {
      draft: 'Draft', staged: 'Staged', validated: 'Validated',
      imported: 'Parties Imported', posted: 'Opening Entry Posted', rolled_back: 'Rolled Back' } },
    tabs: [
      { id: 'src', label: '1. Source & Date', bn: '১. সোর্স ও তারিখ', icon: '📄', badge: '4' },
      { id: 'out', label: '2. Outcome', bn: '২. ফলাফল', icon: '📊', badge: '7' },
      { id: 'log', label: '3. Decision Log', bn: '৩. সিদ্ধান্ত লগ', icon: '🗂️', badge: '1' }
    ],
    sections: [
      { tab: 'src', title: 'Legacy Spreadsheet & Take-on Date',
        note: "Attach the legacy partner ledger (Partner / Debit / Credit / Balance columns). Save, then run Stage → Validate → Import → Post from the list's command bar. Posting goes through the governed M19 funnel with the suspense-cutover source — never raw SQL on control accounts.",
        fields: [
          { name: 'name', label: 'Take-on', readonly: true },
          { name: 'source_file', label: 'Legacy Ledger (.xlsx)', type: 'file' },
          { name: 'source_filename', label: 'File Name' },
          { name: 'import_ref', label: 'Import Reference (unique legacy keys)', required: true },
          { name: 'takeon_date', label: 'Opening Balance Date (period boundary)', required: true },
          { name: 'contra_account_id', label: 'Take-on Contra Account' }
        ] },
      { tab: 'out', title: 'Counts & Position',
        fields: [
          { name: 'line_count', label: 'Source Rows', readonly: true },
          { name: 'linked_count', label: 'Linked Existing Parties', readonly: true },
          { name: 'created_count', label: 'Created Parties', readonly: true },
          { name: 'gl_mapped_count', label: 'Internal → GL Mapped', readonly: true },
          { name: 'quarantined_count', label: 'Quarantined', readonly: true },
          { name: 'total_debit', label: 'Total Debit (BDT)', readonly: true },
          { name: 'total_credit', label: 'Total Credit (BDT)', readonly: true },
          { name: 'total_balance', label: 'Net Legacy Position (BDT)', readonly: true },
          { name: 'external_balance', label: 'Carried on Partner Accounts (BDT)', readonly: true },
          { name: 'posted_move_id', label: 'Opening Entry', readonly: true }
        ] },
      { tab: 'log', title: 'Audit Trail',
        fields: [
          { name: 'decision_log', label: 'Decision Log (who, when, what)', readonly: true, type: 'text' }
        ] }
    ]
  },

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
  /* R1 (2026-11-07): the statutory register as a report pack — feeds the
   * branded Excel/PDF/CSV exports and the send-by-email flow. */
  'M19-coa-register': { kind: 'table_report', module: 'M19', report: 'coa_register', period: false, title: 'Chart of Accounts Register' },
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

  /* Allocation rules: the model rejects a rule without targets and refuses
   * targets that do not total 100% — the D365 form edits both in one save. */
  'M19-alloc-rules': { kind: 'model_list', model: 'fix.allocation.rule', stateField: 'state',
    cols: ['name', 'journal_id', 'source_account_id', 'activated_by_id', 'last_run_date', 'run_count', 'state'],
    actions: [
      { m: 'action_activate', l: 'Activate (Accounting Administrator)' },
      { m: 'action_deactivate', l: 'Deactivate' },
      { m: 'action_run', l: 'Run Allocation' },
    ] },

  /* ============ D365 IN-WORKSPACE FORM SCREENS (M19 re-audit v2) ========
   * The registry's four data-entry chips + the allocation rule: every one
   * opens a Dynamics-365 record form inside the workspace, never an Odoo
   * dialog. Header + child lines save in ONE request (the models' own
   * constraints — targets total 100%, template must balance — apply). */
  'M19-form-alloc': {
    kind: 'model_form',
    model: 'fix.allocation.rule',
    title: 'Allocation Rule',
    back: 'M19-alloc-rules',
    status: { field: 'state', labels: { draft: 'Draft', active: 'Active' } },
    sections: [
      {
        title: 'Rule Header',
        note: 'FR-FIN-026: distributes a source account’s POSTED period movement across target accounts by fixed shares (shared rent, utilities, overhead).',
        fields: [
          { name: 'name', required: true, label: 'Rule Name' },
          { name: 'journal_id', required: true, label: 'Allocation Journal' },
          { name: 'source_account_id', required: true, label: 'Source Account to Clear' },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'state', readonly: true, label: 'Rule Status' },
          { name: 'activated_by_id', readonly: true, label: 'Activated By' },
          { name: 'last_edited_by_id', readonly: true, label: 'Content Last Edited By' }
        ]
      },
      {
        title: 'Audit Trail',
        note: 'System-maintained: the last allocation entry posted by this rule, when it ran, and how many times.',
        fields: [
          { name: 'last_run_id', readonly: true, label: 'Last Allocation Entry' },
          { name: 'last_run_date', readonly: true, label: 'Last Run Date' },
          { name: 'run_count', readonly: true, label: 'Runs to Date' }
        ]
      }
    ],
    lines: {
      field: 'line_ids',
      title: 'Allocation Targets — shares must total 100%',
      note: 'Each target receives its share of the source account movement, posted with branch / cost-centre / business-line dimensions. A rule with no targets, or targets that do not total 100%, is refused by the ledger.',
      total: { field: 'percent', label: 'Total Share %', target: 100 },
      fields: [
        { name: 'account_id', required: true, label: 'Target Account' },
        { name: 'percent', required: true, label: 'Share %' },
        { name: 'branch_id', label: 'Branch' },
        { name: 'cost_centre', label: 'Cost Centre' },
        { name: 'business_line', label: 'Business Line' }
      ]
    }
  },

  'M19-form-ic': {
    kind: 'model_form',
    model: 'fix.intercompany.transaction',
    title: 'Intercompany Charge',
    back: 'M19-ic-txns',
    status: { field: 'state', labels: { draft: 'Draft', pending_matching: 'Pending Counterparty Match', matched: 'Matched & Reconciled', settled: 'Settled', disputed: 'Disputed' } },
    sections: [
      {
        title: 'Charge Header',
        note: 'FR-FIN-026..031: one inter-company / inter-branch charge with its two real postings. The transaction reference is issued by the sequence on save.',
        fields: [
          { name: 'name', required: true, label: 'Description' },
          { name: 'reference', readonly: true, label: 'Transaction Ref (auto)' },
          { name: 'scope', readonly: true, label: 'Scope (derived)' },
          { name: 'state', readonly: true, label: 'Status' }
        ]
      },
      {
        title: 'Entities & Branches',
        note: 'Originating entity carries the due-from; the counterparty carries the due-to. Branches derive from each entity and stay editable for branch-level charges.',
        fields: [
          { name: 'source_entity_id', required: true, label: 'Originating Entity' },
          { name: 'target_entity_id', required: true, label: 'Counterparty Entity' },
          { name: 'source_branch_id', label: 'Originating Branch' },
          { name: 'target_branch_id', label: 'Counterparty Branch' },
          { name: 'rule_id', label: 'Applicable IC Rule' }
        ]
      },
      {
        title: 'Amount & Date',
        note: 'The amount must be positive (ledger rule). Posting the charge creates the originating entry and the counterparty mirror entry.',
        fields: [
          { name: 'transaction_date', required: true, label: 'Transaction Date' },
          { name: 'amount', required: true, label: 'Transaction Amount' }
        ]
      },
      {
        title: 'Matching (system)',
        note: 'Populated by “Post & Mirror” and “Match Against Ledger” — read-only here. A priced charge posts at the approved transfer-pricing rate on its date; a user of the counterparty entity, not the poster, matches it.',
        fields: [
          { name: 'mirror_invoice_ref', readonly: true, label: 'Mirror Invoice Ref' },
          { name: 'match_difference', readonly: true, label: 'Match Difference' },
          { name: 'matched_date', readonly: true, label: 'Matched Timestamp' },
          { name: 'cost_amount', readonly: true, label: 'Cost Before Markup' },
          { name: 'tp_rate_id', readonly: true, label: 'Approved TP Rate Applied' },
          { name: 'mirrored_by_id', readonly: true, label: 'Mirror Posted By' },
          { name: 'matched_by_id', readonly: true, label: 'Matched By' }
        ]
      }
    ]
  },

  'M19-form-template': {
    kind: 'model_form',
    model: 'fix.journal.template',
    title: 'Recurring Journal Template',
    back: 'M19-recurring',
    status: { field: 'state', labels: { draft: 'Draft', active: 'Active', paused: 'Paused' } },
    sections: [
      {
        title: 'Schedule',
        note: 'FR-FIN-013/016: a recurring accrual carrier. A run only fires when the next run date is due — no entry is ever invented.',
        fields: [
          { name: 'name', required: true, label: 'Template Name' },
          { name: 'journal_id', required: true, label: 'Journal' },
          { name: 'memo', label: 'Entry Reference' },
          { name: 'schedule', required: true, label: 'Recurrence' },
          { name: 'next_run_date', required: true, label: 'Next Run Date' },
          { name: 'auto_reverse', label: 'Auto-Reversing (Accrual)' },
          { name: 'state', readonly: true, label: 'Status' },
          { name: 'activated_by_id', readonly: true, label: 'Activated By' },
          { name: 'last_edited_by_id', readonly: true, label: 'Content Last Edited By' }
        ]
      },
      {
        title: 'Generation Audit',
        note: 'System-maintained: the last generated entry, when it ran, and the count of entries produced.',
        fields: [
          { name: 'last_move_id', readonly: true, label: 'Last Generated Entry' },
          { name: 'last_run_date', readonly: true, label: 'Last Run Date' },
          { name: 'run_count', readonly: true, label: 'Entries Generated' }
        ]
      }
    ],
    lines: {
      field: 'line_ids',
      title: 'Template Lines — debit must equal credit',
      note: 'The ledger refuses a template with no lines or an unbalanced template. Each generated entry copies these lines.',
      balance: { label: 'Balance (Dr − Cr)', fields: ['debit', 'credit'] },
      fields: [
        { name: 'account_id', required: true, label: 'Account' },
        { name: 'label', label: 'Line Label' },
        { name: 'debit', label: 'Debit' },
        { name: 'credit', label: 'Credit' }
      ]
    }
  },

  'M19-form-nil': {
    kind: 'model_form',
    model: 'fix.nil.return.generator',
    title: 'Nil Return Declaration',
    back: 'M19-nil-returns',
    status: { field: 'state', labels: { draft: 'Draft', verified: 'Eligibility Verified', generated: 'Nil Packs Generated', submitted: 'Submitted to NBR', acknowledged: 'NBR Acknowledged' } },
    sections: [
      {
        title: 'Declaration Scope',
        note: 'Mushak 9.1 + TDS nil packs for an entity in a tax period with no recorded transactions (typically a newly registered entity).',
        fields: [
          { name: 'entity_id', required: true, label: 'Entity' },
          { name: 'period_year', required: true, label: 'Period Year' },
          { name: 'period_month', required: true, label: 'Period Month' },
          { name: 'filing_reference', label: 'NBR Filing Reference' },
          { name: 'state', readonly: true, label: 'Status' }
        ]
      },
      {
        title: 'Measured Eligibility',
        note: 'Eligibility is counted from posted invoices, bills and P&L entries dated in the period — never assumed. The NBR acknowledgement is keyed in from the e-VAT portal; this module does not file with NBR.',
        fields: [
          { name: 'due_date', readonly: true, label: 'Statutory Due Date' },
          { name: 'transaction_count', readonly: true, label: 'Transactions Counted' },
          { name: 'eligible_for_nil_return', readonly: true, label: 'Eligible for Nil Return' },
          { name: 'is_newly_registered', readonly: true, label: 'Newly Registered (<12 Months)' }
        ]
      }
    ]
  },


  /* ===== master-data forms (batch 2) — D365 in-workspace ===== */
  'M19-form-coaload': {
    kind: 'model_form',
    model: 'fix.chart.loader',
    title: "Chart Loader",
    back: 'M19-coa-loader',
    sections: [
      { title: "Chart Loader", note: "A chart-of-accounts loader run: the source file, the mapping used and the outcome counts.",
        fields: [
          { name: 'company_id', required: true, label: "Company" },
          { name: 'state', readonly: true, label: "State" },
          { name: 'source_file', label: "Source File" }
        ] }
    ]
  },
  'M19-form-bridge': {
    kind: 'model_form',
    model: 'fix.financial.report.bridge',
    title: "Financial Report Bridge",
    back: 'M19-report-bridge',
    sections: [
      { title: "Financial Report Bridge", note: "Maps a statutory report line to the accounts that feed it.",
        fields: [
          { name: 'company_id', required: true, label: "Company" },
          { name: 'name', required: true, label: "Report Name" },
          { name: 'report_type', required: true, label: "Report Type" },
          { name: 'fiscal_year_id', label: "Fiscal Year" },
          { name: 'date_from', label: "From" },
          { name: 'date_to', label: "To" }
        ] }
    ]
  },
  'M19-form-consol': {
    kind: 'model_form',
    model: 'fix.consolidation.book',
    title: "Consolidation Book",
    back: 'M19-consol-books',
    sections: [
      { title: "Consolidation Book", note: "A consolidation book: the entities in scope and the elimination rules applied.",
        fields: [
          { name: 'name', required: true, label: "Book Name" },
          { name: 'code', required: true, label: "Code" },
          { name: 'company_id', required: true, label: "Company" },
          { name: 'currency_id', required: true, label: "Consolidation Currency" },
          { name: 'parent_entity_id', required: true, label: "Parent Entity" },
          { name: 'consolidation_date', required: true, label: "Consolidation Date" },
          { name: 'state', readonly: true, label: "Status" }
        ] }
    ]
  },
  'M19-form-icrule': {
    kind: 'model_form',
    model: 'fix.intercompany.rule',
    title: "Intercompany Rule",
    back: 'M19-ic-rules',
    tabs: [
      { id: 'rule', label: 'Rule', bn: 'নিয়ম' },
      { id: 'posting', label: 'Posting Accounts', bn: 'পোস্টিং হিসাব' },
      { id: 'pricing', label: 'Transfer Pricing', bn: 'স্থানান্তর মূল্য' }
    ],
    sections: [
      { tab: 'rule', title: "Intercompany Rule", note: "The rule that pairs an intercompany transaction with its mirror entry in the counterpart entity.",
        fields: [
          { name: 'name', required: true, label: "Rule Name" },
          { name: 'code', required: true, label: "Rule Code" },
          { name: 'company_id', required: true, label: "Company" },
          { name: 'scope', required: true, label: "Scope" },
          { name: 'source_entity_id', required: true, label: "Selling / Supplying Entity" },
          { name: 'target_entity_id', required: true, label: "Purchasing / Receiving Entity" },
          { name: 'transaction_type', required: true, label: "Transaction Category" },
          { name: 'source_branch_id', label: "Supplying Branch" },
          { name: 'target_branch_id', label: "Receiving Branch" }
        ] },
      { tab: 'posting', title: "Posting Accounts", note: "Both sides post on these; a charge under a rule with any of them missing is refused, naming what is missing. An inter-branch rule uses the supplying side's journal only.",
        fields: [
          { name: 'source_journal_id', label: "Supplying Side Journal" },
          { name: 'source_receivable_account_id', label: "Due-From Account" },
          { name: 'source_income_account_id', label: "Recharge Income Account" },
          { name: 'target_journal_id', label: "Receiving Side Journal" },
          { name: 'target_expense_account_id', label: "Recharge Expense Account" },
          { name: 'target_payable_account_id', label: "Due-To Account" }
        ] },
      { tab: 'pricing', title: "Transfer Pricing", note: "The markup a charge under this rule is priced at. It must equal an approved rate in force on the charge's date (Transfer-Pricing Rates); a markup with no approved rate is refused at posting.",
        fields: [
          { name: 'markup_percent', label: "Transfer Pricing Markup (%)" },
          { name: 'documentation_ref', label: "TP Documentation Ref" },
          { name: 'transfer_pricing_compliant', readonly: true, label: "Approved Rate in Force" }
        ] }
    ]
  },

  /* A08 finish: the screens the close, the control flag and transfer pricing
   * could not be operated without. Decisions stay in the M63 approval inbox. */
  'M19-form-period-close': {
    kind: 'model_form',
    model: 'fix.period.close',
    title: "Period Close",
    back: 'M19-period-close',
    status: { field: 'state', labels: { open: 'Open', in_progress: 'In Progress', ready_to_close: 'Ready to Close', closed: 'Closed' } },
    tabs: [
      { id: 'period', label: 'Period', bn: 'পিরিয়ড' },
      { id: 'suspense', label: 'Inventory Suspense', bn: 'ইনভেন্টরি সাসপেন্স' },
      { id: 'closure', label: 'Closure', bn: 'সমাপ্তি' }
    ],
    sections: [
      { tab: 'period', title: "Period", note: "One close per company and month-end. Save, then Generate SOP Steps; the steps are worked in the Month-End Close Console.",
        fields: [
          { name: 'period_end', required: true, label: "Period End (last day of the month)" },
          { name: 'company_id', required: true, label: "Company" },
          { name: 'operating_unit_id', label: "Operating Unit" },
          { name: 'state', readonly: true, label: "State" },
          { name: 'started_at', readonly: true, label: "Started At" },
          { name: 'target_completion_date', readonly: true, label: "Target Completion Date" },
          { name: 'sla_status', readonly: true, label: "SLA Performance" }
        ] },
      { tab: 'suspense', title: "Inventory Suspense Cutover", note: "Draft the cutover journal (Journal Entry screen) for the pending suspense, have it approved, select it here, then Reconcile. Pending suspense blocks the close.",
        fields: [
          { name: 'cutover_move_id', label: "Suspense Cutover Journal Entry" },
          { name: 'suspense_closing', readonly: true, label: "Suspense Still Pending After Reconciling" },
          { name: 'suspense_reconciled', readonly: true, label: "Suspense Reconciled" },
          { name: 'cutover_voucher_ref', readonly: true, label: "Cutover Voucher" }
        ] },
      { tab: 'closure', title: "Closure (system)", note: "Stamped by the Ready Check and by Close & Lock.",
        fields: [
          { name: 'ready_by_id', readonly: true, label: "Ready Check By" },
          { name: 'closed_by_id', readonly: true, label: "Closed By" },
          { name: 'closed_at', readonly: true, label: "Closed At" },
          { name: 'lock_date_set', readonly: true, label: "Lock Date Set" },
          { name: 'is_locked', readonly: true, label: "Ledger Locked" }
        ] }
    ]
  },
  'M19-form-reopen': {
    kind: 'model_form',
    model: 'fix.period.reopen',
    title: "Period Reopen Request",
    back: 'M19-reopens',
    status: { field: 'state', labels: { draft: 'Draft', pending: 'Awaiting Approval', approved: 'Approved (exception active)', rejected: 'Rejected', revoked: 'Revoked' } },
    sections: [
      { title: "Request", note: "One named user may post into a closed period until the end time (3 days at most). Save, then Submit; an Accounting Administrator other than the closer, the requester and that user decides it in the approval inbox. Once submitted the request is frozen.",
        fields: [
          { name: 'close_id', required: true, label: "Closed Period" },
          { name: 'user_id', required: true, label: "Posting User" },
          { name: 'end_datetime', required: true, label: "Exception Ends" },
          { name: 'reason', required: true, label: "Reason" },
          { name: 'state', readonly: true, label: "Status" }
        ] },
      { title: "Decision (system)", note: "Stamped when the request is submitted and decided.",
        fields: [
          { name: 'approval_state', readonly: true, label: "Approval" },
          { name: 'requested_by_id', readonly: true, label: "Requested By" },
          { name: 'approved_by_id', readonly: true, label: "Approved By" },
          { name: 'approved_at', readonly: true, label: "Approved At" }
        ] }
    ]
  },
  'M19-form-control-change': {
    kind: 'model_form',
    model: 'fix.chart.control.change',
    title: "Control Account Change",
    back: 'M19-control-changes',
    status: { field: 'state', labels: { draft: 'Draft', pending: 'Pending', applied: 'Applied', rejected: 'Rejected' } },
    sections: [
      { title: "Proposal", note: "The control flag of a statutory account changes only through this proposal: it applies when an Accounting Administrator other than the proposer approves it in the approval inbox. Once submitted the proposal is frozen.",
        fields: [
          { name: 'account_id', required: true, label: "Statutory Account" },
          { name: 'new_is_control', label: "Control Account" },
          { name: 'new_subledger', label: "Control Subledger" },
          { name: 'reason', required: true, label: "Reason" },
          { name: 'state', readonly: true, label: "Status" },
          { name: 'approval_state', readonly: true, label: "Approval" },
          { name: 'requested_by_id', readonly: true, label: "Proposed By" },
          { name: 'applied_by_id', readonly: true, label: "Applied By" }
        ] }
    ]
  },
  'M19-form-tp-rate': {
    kind: 'model_form',
    model: 'fix.transfer.price.rate',
    title: "Transfer-Pricing Rate",
    back: 'M19-tp-rates',
    status: { field: 'state', labels: { draft: 'Proposed', active: 'Approved & Active', retired: 'Retired' } },
    sections: [
      { title: "Rate", note: "An accountant proposes the markup of a rule for an effective period, on the transfer-pricing study it rests on; an Accounting Administrator other than the proposer approves it. The rule's own markup must then equal it. An approved rate is frozen: retire it and propose a new one.",
        fields: [
          { name: 'rule_id', required: true, label: "Inter-Company Rule" },
          { name: 'markup_percent', required: true, label: "Approved Markup (%)" },
          { name: 'date_from', required: true, label: "Effective From" },
          { name: 'date_to', label: "Effective To" },
          { name: 'study_ref', required: true, label: "Transfer-Pricing Study / Basis" },
          { name: 'state', readonly: true, label: "Status" },
          { name: 'approved_by_id', readonly: true, label: "Approved By" },
          { name: 'approved_at', readonly: true, label: "Approved At" }
        ] }
    ]
  },


  /* ===== triage coverage screens ===== */
  'M19-chart-account': { kind: 'model_list', model: 'fix.chart.account',
    /* 2026-11-07 audit R2/R6: the CODE leads the grid (D365/SAP/NetSuite/Odoo
     * convention), then name/type/subtype; company-wide statutory chart, so
     * the empty operating_unit_id column is dropped (policy: company-level
     * CoA — the field stays on the model and form). */
    cols: ['account_code', 'name', 'account_type', 'account_subtype', 'active', 'company_id'],
    actions: [
      /* R9: row actions reuse the model's own guarded method — COA-04 refuses
       * archiving an account that still carries a balance. */
      { m: 'action_archive', l: 'Archive (COA-04 zero-balance guard)' },
    ],
    links: [
      /* R3: the governance surfaces one click away — no dead ends. */
      { s: 'M19-coa-loader', l: 'Import — CoA Master Loader' },
      { s: 'M19-control-changes', l: 'Control Changes approval' },
      { s: 'M19-coa', l: 'Statutory Register (hierarchy & balances)' },
    ] },
  'M19-fiscal-period-bridge': { kind: 'model_list', model: 'fix.fiscal.period.bridge', create: false,
    cols: ['company_id', 'operating_unit_id', 'fiscal_year_id', 'period_close_id', 'is_locked', 'locked_at'],
    actions: [{ m: 'action_lock_journals', l: 'Re-apply Lock (Accounting Administrator)' }] },
  'M19-journal-dimension': { kind: 'model_list', model: 'fix.journal.dimension', create: false,
    cols: ['company_id', 'operating_unit_id', 'branch_id', 'cost_centre', 'business_line', 'project_ref', 'brand'] },
  'M19-period-close': { kind: 'model_list', model: 'fix.period.close', stateField: 'state',
    cols: ['period_end', 'state', 'company_id', 'started_at', 'cutover_move_id', 'suspense_reconciled', 'is_locked', 'closed_by_id', 'lock_date_set'],
    actions: [
      { m: 'action_generate_standard_steps', l: 'Generate SOP Steps' },
      { m: 'action_set_cutover_entry', l: 'Set Cutover Entry', ask: 'Number of the posted suspense cutover entry', kwarg: 'entry' },
      { m: 'action_reconcile_inventory_suspense', l: 'Reconcile Suspense' },
      { m: 'action_ready', l: 'Ready Check' },
      { m: 'action_close', l: 'Close & Lock (Accounting Administrator)' },
      { m: 'action_request_reopen', l: 'Request Reopen (for me)', ask: 'Why must this closed period reopen? (an exception for you, for the longest window allowed)', kwarg: 'reason' },
    ] },
  'M19-reopens': { kind: 'model_list', model: 'fix.period.reopen', stateField: 'state',
    cols: ['close_id', 'period_end', 'user_id', 'end_datetime', 'reason', 'requested_by_id', 'approval_state', 'approved_by_id', 'state'],
    actions: [
      { m: 'action_submit', l: 'Submit for Approval' },
      { m: 'action_revoke', l: 'Revoke (Accounting Administrator)' },
    ] },
  'M19-control-changes': { kind: 'model_list', model: 'fix.chart.control.change', stateField: 'state',
    cols: ['account_id', 'new_is_control', 'new_subledger', 'reason', 'requested_by_id', 'approval_state', 'applied_by_id', 'state'],
    actions: [{ m: 'action_submit', l: 'Submit for Approval' }] },
  'M19-tp-rates': { kind: 'model_list', model: 'fix.transfer.price.rate', stateField: 'state',
    cols: ['rule_id', 'markup_percent', 'date_from', 'date_to', 'study_ref', 'approved_by_id', 'approved_at', 'state'],
    actions: [
      { m: 'action_activate', l: 'Approve & Activate (Accounting Administrator)' },
      { m: 'action_retire', l: 'Retire (Accounting Administrator)' },
    ] },

  'M19-form-chart-account': {
    kind: 'model_form',
    model: 'fix.chart.account',
    title: "Chart of Accounts — Account",
    back: 'M19-chart-account',
    /* 2026-11-07 audit: the old single-section form omitted statutory_group
     * (required on the model) so + New ALWAYS failed with a NotNullViolation,
     * and hid every posting-rule field. Tabbed per the D365 multi-tab
     * standard; control-account status stays read-only here — it changes
     * only through the Control Changes approval screen (COA-02). */
    tabs: [
      { id: 'ident', label: 'Identification', bn: 'শনাক্তকরণ', icon: '🏷️', badge: '7' },
      { id: 'class', label: 'Classification', bn: 'শ্রেণিবিন্যাস', icon: '🗂️', badge: '3' },
      { id: 'ctrl', label: 'Posting & Control', bn: 'পোস্টিং ও নিয়ন্ত্রণ', icon: '🛡️', badge: '6' },
      { id: 'admin', label: 'Lifecycle & Tax', bn: 'জীবনচক্র ও কর', icon: '🗓️', badge: '4' },
      { id: 'link', label: 'Posting-Chart Link', bn: 'পোস্টিং চার্ট সংযোগ', icon: '🔗', badge: '2' }
    ],
    sections: [
      { tab: 'ident', title: 'Account Identification',
        note: "MD-035 statutory chart. The code is four blocks T-GG-SS-NNN; the T block must agree with the account type (1 asset · 2 liability · 3 equity · 4 income · 5 expense) and the code is unique per company.",
        fields: [
          { name: 'account_code', required: true, label: "Account Code" },
          { name: 'name', required: true, label: "Account Name" },
          { name: 'name_bn', label: "Account Name (Bengali) — statutory reports" },
          { name: 'company_id', required: true, label: "Company" },
          { name: 'operating_unit_id', label: "Operating Unit" },
          { name: 'currency_id', label: "Currency (statutory BDT)" },
          { name: 'active', label: "Active" }
        ] },
      { tab: 'class', title: 'Statutory Classification',
        note: "The statutory group is the mandatory reporting line (COA-05) — without it an account cannot be created. Subtype examples: current_asset, fixed_asset, receivable, payable, bank, cash, stock, tax, revenue, cogs, opex.",
        fields: [
          { name: 'account_type', required: true, label: "Account Type" },
          { name: 'account_subtype', label: "Account Subtype" },
          { name: 'statutory_group', required: true, label: "Statutory Group (COA-05)" }
        ] },
      { tab: 'ctrl', title: 'Posting Rules & Control',
        note: "COA-01: only level-4 leaf accounts (NNN > 000) may be postable. Control-account status and its subledger binding change only through the Control Changes approval screen — they are shown read-only here (COA-02).",
        fields: [
          { name: 'is_postable', label: "Postable (COA-01)" },
          { name: 'manual_entry_blocked', label: "Block Manual Entry (subledger/system postings only)" },
          { name: 'is_deprecated', label: "Deprecated (closed for new postings)" },
          { name: 'requires_dimension', label: "Required Dimensions (COA-03, semicolon separated: branch;cost_centre;business_line)" },
          { name: 'is_control_account', readonly: true, label: "Control Account" },
          { name: 'control_subledger', readonly: true, label: "Control Subledger" }
        ] },
      { tab: 'admin', title: 'Effective Window & Bangladesh VAT Tagging',
        note: "Outside the effective window the account is suspended for new postings (kept on reports). VAT-relevant accounts are tagged with the statutory register they feed, so Mushak 6.1 / 6.3 / 6.6 and TDS registers produce straight from the GL.",
        fields: [
          { name: 'active_from', label: "Active From" },
          { name: 'active_to', label: "Active To" },
          { name: 'vat_relevant', label: "VAT / Mushak Relevant" },
          { name: 'mushak_register', label: "Mushak Register" }
        ] },
      { tab: 'link', title: 'Posting-Chart Link & Balance',
        note: "The link to the Odoo posting account switches the posting rules on for this account; it is managed by the CoA Master Loader reconciliation, not typed here. The ledger balance is live from posted entries.",
        fields: [
          { name: 'odoo_account_id', readonly: true, label: "Linked Odoo Account" },
          { name: 'balance', readonly: true, label: "Statutory Balance (manual, BDT)" }
        ] }
    ]
  },

};

/* built-in report chips -> the screen that shows that report */
export const REPORT_ROUTES = {
  'M19:FX Revaluation': 'M19-rpt-fx',
  "M19:Trial Balance": "M19-tb",
  "M19:P&L (BFRS)": "M19-pl",
  "M19:Balance Sheet": "M19-bs",
  "M19:Cash Flow": "M19-cf",
  "M19:Dimensional P&L by Branch": "M19-dimensions",
  "M19:Close Checklist Report": "M19-close",
  "M19:Close SLA Breaches": "M19-close-sla",
  "M19:Partner Ledger (GL)": "M19-partner-ledger",
  "M19:Partner Statement Drill-down": "M19-partner-statement",
  "M19:Due-To / Due-From Balances": "M19-ic-balances",
  "M19:Legacy AR Control Reconciliation": "M19-legacy-ar-recon",
};

/* data-entry form chips -> real model forms */
export const FORM_MODELS = {
  'M19:Journal Entry (manual/recurring)': 'account.move',
  'M19:Allocation Rule': 'fix.allocation.rule',
  'M19:Intercompany Charge': 'fix.intercompany.transaction',
  'M19:Recurring Journal Template': 'fix.journal.template',
  'M19:Nil Return Declaration': 'fix.nil.return.generator',
  'M19:Legacy Partner-Ledger Take-on': 'fix.ledger.takeon.batch',
  'M19:Legacy GL Control-Ledger Import': 'fix.legacy.ledger.batch',
  'M19:Legacy Bank-Ledger Take-on': 'fix.bank.takeon.batch',
};

/* every registry form chip -> its in-workspace D365 screen; grid + New and
 * Open-full-record resolve through the model map. */
export const FORM_CHIPS = {
  'M19:Chart Loader': 'M19-form-coaload',
  'M19:Financial Report Bridge': 'M19-form-bridge',
  'M19:Consolidation Book': 'M19-form-consol',
  'M19:Intercompany Rule': 'M19-form-icrule',
  'M19:Allocation Rule': 'M19-form-alloc',
  'M19:Intercompany Charge': 'M19-form-ic',
  'M19:Recurring Journal Template': 'M19-form-template',
  'M19:Nil Return Declaration': 'M19-form-nil',
  // the three cut-over chips used to fall through to the Journal Entry editor
  'M19:Legacy Partner-Ledger Take-on': 'M19-form-takeon',
  'M19:Legacy GL Control-Ledger Import': 'M19-form-legacy-ledger',
  'M19:Legacy Bank-Ledger Take-on': 'M19-form-bank-takeon',
  'M19:__by_model__': {
    'fix.period.close': 'M19-form-period-close',
    'fix.period.reopen': 'M19-form-reopen',
    'fix.chart.control.change': 'M19-form-control-change',
    'fix.transfer.price.rate': 'M19-form-tp-rate',
    'fix.fx.revaluation': 'M19-form-fx',
    'fix.chart.account': 'M19-form-chart-account',
    'fix.chart.loader': 'M19-form-coaload',
    'fix.financial.report.bridge': 'M19-form-bridge',
    'fix.consolidation.book': 'M19-form-consol',
    'fix.intercompany.rule': 'M19-form-icrule',
    'fix.allocation.rule': 'M19-form-alloc',
    'fix.intercompany.transaction': 'M19-form-ic',
    'fix.journal.template': 'M19-form-template',
    'fix.nil.return.generator': 'M19-form-nil',
    'fix.ledger.takeon.batch': 'M19-form-takeon',
    'fix.legacy.ledger.batch': 'M19-form-legacy-ledger',
    'fix.bank.takeon.batch': 'M19-form-bank-takeon'
  },
  'M19:__by_screen__': {
    'M19-period-close': 'M19-form-period-close',
    'M19-reopens': 'M19-form-reopen',
    'M19-control-changes': 'M19-form-control-change',
    'M19-tp-rates': 'M19-form-tp-rate',
    'M19-fx-revaluation': 'M19-form-fx',
    'M19-takeon': 'M19-form-takeon',
    'M19-legacy-ledger': 'M19-form-legacy-ledger',
    'M19-bank-takeon': 'M19-form-bank-takeon',
    'M19-chart-account': 'M19-form-chart-account',
    'M19-coa-loader': 'M19-form-coaload',
    'M19-report-bridge': 'M19-form-bridge',
    'M19-consol-books': 'M19-form-consol',
    'M19-ic-rules': 'M19-form-icrule',
    'M19-alloc-rules': 'M19-form-alloc',
    'M19-ic-txns': 'M19-form-ic',
    'M19-recurring': 'M19-form-template',
    'M19-nil-returns': 'M19-form-nil'
  }
};

/* the module's "+ New" surface */
export const CREATE = {
  // The JE editor (M19-je) is the create path for journal entries - without
  // the screen the button fell through to the recurring-template form.
  M19: { screen: 'M19-je', model: 'account.move', label: 'Journal Entry' },
};
