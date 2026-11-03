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
    { l: 'Revenue MTD', m: 'revenue_mtd', prefix: '৳ ' },
    { l: 'Gross Margin', m: 'gross_margin_mtd' },
    { l: 'Close Progress', m: 'open_period_closes' },
    { l: 'IC Unmatched', m: 'ic_unmatched' },
    { l: 'TB Imbalance', m: 'tb_imbalance' },
    { l: 'Journals MTD', m: 'posted_moves_mtd' },
    { l: 'Drafts in Review', m: 'draft_journals' }
  ],
  groups: [
    { en: 'Record Coverage', screens: [
      { id: 'M19-chart-account', en: "Chart Account", bn: "Chart Account", t: 'g' },
      { id: 'M19-fiscal-period-bridge', en: "Fiscal Period Bridge", bn: "Fiscal Period Bridge", t: 'g' },
      { id: 'M19-journal-dimension', en: "Journal Dimension", bn: "Journal Dimension", t: 'g' },
      { id: 'M19-period-close', en: "Period Close", bn: "Period Close", t: 'g' }
    ]},
    { en: 'Ledger', screens: [
      { id: 'M19-fx-revaluation', en: 'FX Revaluation (IAS 21)', bn: 'বৈদেশিক মুদ্রা পুনর্মূল্যায়ন', t: 'g' },
      { id: 'M19-coa', en: 'Chart of Accounts', bn: 'হিসাবের ছক', t: 'g' },
      { id: 'M19-journals', en: 'Journals', bn: 'জার্নাল', t: 'g' },
      { id: 'M19-je', en: 'Journal Entry', bn: 'জার্নাল এন্ট্রি', t: 'f' },
      { id: 'M19-tb', en: 'Trial Balance', bn: 'ট্রায়াল ব্যালেন্স', t: 'r' },
      { id: 'M19-dimensions', en: '7-Dimension Model', bn: 'মাত্রা মডেল', t: 'g' },
      { id: 'M19-coa-loader', en: 'CoA Master Loader', bn: 'হিসাবের ছক লোডার', t: 'c' },
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
    ['1', 'CoA & Dimensions', 12, { model: 'fix.chart.account', cols: ['account_code', 'name', 'account_type', 'is_postable', 'is_control_account'], screens: ['M19-coa', 'M19-chart-account', 'M19-dimensions', 'M19-coa-loader'] }],
    ['2', 'Journals', 11, { model: 'account.journal', cols: ['name', 'code', 'type', 'default_account_id', 'currency_id'], screens: ['M19-journals', 'M19-je'] }],
    ['3', 'Subledger Posting Engine', 12, { model: 'fix.journal.dimension', cols: ['move_line_id', 'branch_id', 'cost_centre', 'business_line', 'channel'], screens: ['M19-journal-dimension', 'M19-recon', 'M19-tb'] }],
    ['4', 'Fiscal Calendar & Close', 10, { model: 'fix.period.close', cols: ['period_end', 'state', 'sla_status', 'target_completion_date', 'closed_at'], screens: ['M19-close', 'M19-periods', 'M19-period-close', 'M19-close-sla'] }],
    ['5', 'Multi-Entity & Consolidation', 9, { model: 'fix.consolidation.book', cols: ['code', 'name', 'consolidation_date', 'net_consolidated_profit', 'state'], screens: ['M19-consol-books', 'M19-eliminations', 'M19-ic-txns', 'M19-consol'] }],
    ['6', 'Multi-Currency', 7, { model: 'fix.fx.revaluation', cols: ['name', 'rate_date', 'currency_id', 'net_amount', 'state'], screens: ['M19-fx-revaluation'] }],
    ['7', 'Statutory Statements', 9, { model: 'fix.financial.report.bridge', cols: ['name', 'report_type', 'date_from', 'date_to', 'is_balanced'], screens: ['M19-report-bridge', 'M19-bs', 'M19-pl', 'M19-cf'] }],
    ['8', 'Audit & Retention', 7, { model: 'fix.fiscal.period.bridge', cols: ['fiscal_year_id', 'period_close_id', 'is_locked', 'locked_at'], screens: ['M19-audit', 'M19-fiscal-period-bridge'] }],
    ['9', 'Accrual Framework', 8, { model: 'fix.journal.template', cols: ['name', 'schedule', 'next_run_date', 'auto_reverse', 'state'], screens: ['M19-recurring', 'M19-alloc-rules'] }],
    ['10', 'Controls & SoD', 6, { model: 'fix.sod.control', cols: ['code', 'name', 'role_a_id', 'role_b_id', 'conflict_action'], screens: ['M19-suspense'] }]
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
          { name: 'state', required: true, label: 'State' }
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

  /* Allocation rules: the model rejects a rule without targets and refuses
   * targets that do not total 100% — the D365 form edits both in one save. */
  'M19-alloc-rules': { kind: 'model_list', model: 'fix.allocation.rule', stateField: 'state',
    cols: ['name', 'journal_id', 'source_account_id', 'last_run_date', 'run_count', 'state'],
    actions: [{ m: 'action_run', l: 'Run Allocation' }] },

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
          { name: 'state', label: 'Rule Status' }
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
        note: 'Populated by “Post & Mirror” and “Match Against Ledger” — read-only here.',
        fields: [
          { name: 'mirror_invoice_ref', readonly: true, label: 'Mirror Invoice Ref' },
          { name: 'match_difference', readonly: true, label: 'Match Difference' },
          { name: 'matched_date', readonly: true, label: 'Matched Timestamp' }
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
          { name: 'state', label: 'Status' }
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
          { name: 'state', required: true, label: "State" },
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
          { name: 'state', label: "Status" }
        ] }
    ]
  },
  'M19-form-icrule': {
    kind: 'model_form',
    model: 'fix.intercompany.rule',
    title: "Intercompany Rule",
    back: 'M19-ic-rules',
    sections: [
      { title: "Intercompany Rule", note: "The rule that pairs an intercompany transaction with its mirror entry in the counterpart entity.",
        fields: [
          { name: 'name', required: true, label: "Rule Name" },
          { name: 'code', required: true, label: "Rule Code" },
          { name: 'company_id', required: true, label: "Company" },
          { name: 'scope', required: true, label: "Scope" },
          { name: 'source_entity_id', required: true, label: "Selling / Supplying Entity" },
          { name: 'target_entity_id', required: true, label: "Purchasing / Receiving Entity" },
          { name: 'transaction_type', required: true, label: "Transaction Category" },
          { name: 'source_branch_id', label: "Supplying Branch" }
        ] }
    ]
  },


  /* ===== triage coverage screens ===== */
  'M19-chart-account': { kind: 'model_list', model: 'fix.chart.account',
    cols: ['name', 'active', 'company_id', 'operating_unit_id', 'account_code', 'account_type', 'account_subtype'] },
  'M19-fiscal-period-bridge': { kind: 'model_list', model: 'fix.fiscal.period.bridge', create: false,
    cols: ['company_id', 'operating_unit_id', 'fiscal_year_id', 'period_close_id', 'is_locked'] },
  'M19-journal-dimension': { kind: 'model_list', model: 'fix.journal.dimension', create: false,
    cols: ['company_id', 'operating_unit_id', 'branch_id', 'cost_centre', 'business_line', 'project_ref', 'brand'] },
  'M19-period-close': { kind: 'model_list', model: 'fix.period.close', stateField: 'state', create: false,
    cols: ['state', 'company_id', 'operating_unit_id', 'period_end', 'started_at', 'currency_id', 'suspense_opening'] },

  'M19-form-chart-account': {
    kind: 'model_form',
    model: 'fix.chart.account',
    title: "Chart Account",
    back: 'M19-chart-account',
    sections: [
      { title: "Chart Account", note: "Opened from the module's own record set. Every field here is the model's real field; the workflow rules live on the model and are not bypassed by this form.",
        fields: [
          { name: 'name', required: true, label: "Account Name" },
          { name: 'company_id', required: true, label: "Company" },
          { name: 'account_code', required: true, label: "Account Code" },
          { name: 'account_type', required: true, label: "Account Type" },
          { name: 'active', label: "Active" },
          { name: 'operating_unit_id', label: "Operating Unit" },
          { name: 'account_subtype', label: "Account Subtype" }
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
  'M19:__by_model__': {
    'fix.fx.revaluation': 'M19-form-fx',
    'fix.chart.account': 'M19-form-chart-account',
    'fix.chart.loader': 'M19-form-coaload',
    'fix.financial.report.bridge': 'M19-form-bridge',
    'fix.consolidation.book': 'M19-form-consol',
    'fix.intercompany.rule': 'M19-form-icrule',
    'fix.allocation.rule': 'M19-form-alloc',
    'fix.intercompany.transaction': 'M19-form-ic',
    'fix.journal.template': 'M19-form-template',
    'fix.nil.return.generator': 'M19-form-nil'
  },
  'M19:__by_screen__': {
    'M19-fx-revaluation': 'M19-form-fx',
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
  M19: { model: 'account.move', label: 'Journal Entry' },
};
