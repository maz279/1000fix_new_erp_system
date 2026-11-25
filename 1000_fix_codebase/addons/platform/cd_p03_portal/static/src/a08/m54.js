/** @odoo-module **/
/* A08 · Finance & Treasury — M54 Costing, Budget & FP&A.
 * One file per A08 module (merged into P03_MODULES and the screen maps by
 * p03_modules_meta.js): the registry entry, the in-workspace data screens,
 * built-in report routes, data-entry form chips and the "+ New" surface.
 * Backend: controllers/a08/m54.py (SURFACES, REPORTS, kpis) over cd_fpa. */

export const MODULE = {
  area: 'A08', code: 'M54', en: 'Costing, Budget & FP&A', title: 'M54 · Costing, Budget & FP&A',
  bn: 'ব্যয়, বাজেট ও এফপিএ', icon: '🧮',
  desc: 'Cost pools and posted allocation cycles, job costing with loaded labour, business-line, branch and customer profitability, budget versions with approval, variance, forecast and board pack.',
  kpis: [
    { l: 'Budget Variance FYTD', m: 'fpa_budget_variance_fytd' },
    { l: 'Budget Variance (Total)', m: 'budget_total_variance', prefix: '৳ ' },
    { l: 'Budgets', m: 'budgets_count' },
    { l: 'Branch League #1', m: 'fpa_branch_top' },
    { l: 'Negative-Margin Branches', m: 'fpa_negative_branches' },
    { l: 'Job Costing Coverage', m: 'fpa_job_costing_coverage' }
  ],
  groups: [
    { en: 'Costing', screens: [
      { id: 'M54-pools', en: 'Cost Pools & Elements', bn: 'ব্যয় পুল ও উপাদান', t: 'g' },
      { id: 'M54-elements', en: 'Cost Elements', bn: 'ব্যয় উপাদান', t: 'g' },
      { id: 'M54-cost-centres', en: 'Cost Centres', bn: 'ব্যয় কেন্দ্র', t: 'g' },
      { id: 'M54-allocation', en: 'Allocation Cycles', bn: 'বণ্টন চক্র', t: 'g' },
      { id: 'M54-jobs', en: 'Job / Work-Order Costing', bn: 'কাজের ব্যয়', t: 'r' },
      { id: 'M54-jobdist', en: 'Job Margin Distribution', bn: 'কাজের মার্জিন বিন্যাস', t: 'r' },
      { id: 'M54-loaded', en: 'Technician Loaded Cost', bn: 'কর্মী ব্যয়', t: 'r' },
      { id: 'M54-activity-rates', en: 'Planned Activity Rates', bn: 'পরিকল্পিত কার্য হার', t: 'g' }
    ]},
    { en: 'Profitability', screens: [
      { id: 'M54-lines', en: 'Business Lines', bn: 'ব্যবসা লাইন', t: 'g' },
      { id: 'M54-variances-bl', en: 'Business-Line Variance Explanations', bn: 'ব্যবসা লাইনের বিচ্যুতি ব্যাখ্যা', t: 'g' },
      { id: 'M54-streams', en: '14 Business-Line P&L', bn: 'ব্যবসা লাইনের লাভ-ক্ষতি', t: 'r' },
      { id: 'M54-branches', en: 'Branch Profitability', bn: 'শাখা লাভজনকতা', t: 'r' },
      { id: 'M54-customers', en: 'Customer Profitability', bn: 'গ্রাহক লাভজনকতা', t: 'r' },
      { id: 'M54-variances-branch', en: 'Branch Variance Explanations', bn: 'শাখার বিচ্যুতি ব্যাখ্যা', t: 'g' },
      { id: 'M54-unitecon', en: 'Unit Economics', bn: 'একক অর্থনীতি', t: 'r' }
    ]},
    { en: 'Budgeting', screens: [
      { id: 'M54-budgets', en: 'Operating & Capital Budgets', bn: 'বাজেট', t: 'g' },
      { id: 'M54-budget-lines', en: 'Budget Lines', bn: 'বাজেট লাইন', t: 'g' },
      { id: 'M54-workflow', en: 'Budget Workflow', bn: 'বাজেট প্রবাহ', t: 'g' },
      { id: 'M54-targets', en: 'Top-Down Targets', bn: 'শীর্ষ-নির্ধারিত লক্ষ্য', t: 'g' },
      { id: 'M54-bva', en: 'Variance Analysis', bn: 'বিচ্যুতি বিশ্লেষণ', t: 'r' },
      { id: 'M54-variances', en: 'Variance Explanations', bn: 'বিচ্যুতি ব্যাখ্যা', t: 'g' }
    ]},
    { en: 'Planning', screens: [
      { id: 'M54-rolling', en: 'Rolling Forecast', bn: 'রোলিং পূর্বাভাস', t: 'r' },
      { id: 'M54-forecasts', en: 'Forecast Versions', bn: 'পূর্বাভাস সংস্করণ', t: 'g' },
      { id: 'M54-scenario', en: 'Scenario Modelling', bn: 'পরিস্থিতি মডেল', t: 'g' },
      { id: 'M54-board', en: 'Board Pack', bn: 'বোর্ড প্যাক', t: 'r' },
      { id: 'M54-boardpacks', en: 'Board Pack Archive', bn: 'বোর্ড প্যাক সংরক্ষণ', t: 'g' }
    ]}
  ],
  reports: ['Business-Line P&L', 'Branch League Table', 'Budget vs Actual', 'Job Margin Distribution', 'Customer Profitability Deciles', 'Unit Economics per Repair', 'Rolling Forecast', 'Board Pack'],
  forms: ['Budget Version', 'Allocation Rule', 'Allocation Cycle', 'Scenario', 'Board Pack', 'Cost Element', 'Cost Centre', 'Planned Activity Rate', 'Business Line', 'Business-Line Variance Explanation', 'Branch Variance Explanation', 'Budget Target', 'Variance Explanation', 'Forecast Version'],
  cross: ['Financial Accounting & GL', 'Workshop & Depot Repair', 'Business Intelligence'],
  freg: { src: 70, sub: [
    ['1', 'Cost Model', 9, { model: 'fix.cost.pool', cols: ['code', 'name', 'pool_type', 'receiver_type', 'allocation_basis'], screens: ['M54-pools', 'M54-elements', 'M54-cost-centres', 'M54-loaded'], reports: [], forms: ['Allocation Rule', 'Cost Element', 'Cost Centre'] }],
    ['2', 'Allocation Cycles', 10, { model: 'fix.cost.allocation', cols: ['name', 'pool_id', 'date_from', 'allocated_overhead', 'state'], screens: ['M54-allocation'], reports: [], forms: ['Allocation Cycle'] }],
    ['3', 'Job & Contract Costing', 11, { model: 'fix.workshop.job', cols: ['name', 'customer_id', 'parts_total', 'labour_total', 'total_repair_cost'], screens: ['M54-jobs', 'M54-jobdist', 'M54-activity-rates'], reports: ['Job Margin Distribution'], forms: ['Planned Activity Rate'], create: 'M54-form-rate' }],
    ['4', 'Business-Line Profitability', 9, { model: 'fix.business.line', cols: ['code', 'name', 'revenue_stream_no', 'is_profit_centre'], screens: ['M54-lines', 'M54-streams', 'M54-unitecon', 'M54-variances-bl'], reports: ['Business-Line P&L', 'Unit Economics per Repair'], forms: ['Business Line', 'Business-Line Variance Explanation'] }],
    ['5', 'Branch & Channel Profitability', 8, { model: 'fix.journal.dimension', cols: ['branch_id', 'channel', 'business_line', 'cost_centre', 'move_line_id'], screens: ['M54-branches', 'M54-customers', 'M54-variances-branch'], reports: ['Branch League Table', 'Customer Profitability Deciles'], forms: ['Branch Variance Explanation'], create: 'M54-form-variance-branch' }],
    ['6', 'Budgeting', 11, { model: 'fix.budget', cols: ['name', 'budget_type', 'fiscal_year', 'planned_amount', 'state'], screens: ['M54-budgets', 'M54-budget-lines', 'M54-workflow', 'M54-targets'], reports: ['Budget vs Actual'], forms: ['Budget Version', 'Budget Target'] }],
    ['7', 'Variance & Forecast', 8, { model: 'fix.variance.explanation', cols: ['name', 'scope_type', 'date_from', 'variance', 'owner_id', 'due_date', 'state'], screens: ['M54-bva', 'M54-variances', 'M54-rolling', 'M54-forecasts', 'M54-scenario'], reports: ['Budget vs Actual', 'Rolling Forecast'], forms: ['Variance Explanation', 'Forecast Version', 'Scenario'] }],
    ['8', 'Board Pack', 4, { model: 'fix.board.pack', cols: ['name', 'date_from', 'date_to', 'issued_by', 'state'], screens: ['M54-board', 'M54-boardpacks'], reports: ['Board Pack'], forms: ['Board Pack'] }]
  ] }
};

/* in-workspace data screens (checked before any stock Odoo view) */
export const SCREENS = {
  // Costing
  'M54-pools': { kind: 'model_list', model: 'fix.cost.pool',
    cols: ['code','name','pool_type','receiver_type','allocation_basis','include_in_labour_rate','element_count','target_account_id','clearing_account_id','journal_id'] },
  'M54-elements': { kind: 'model_list', model: 'fix.cost.element',
    cols: ['pool_id','code','name','element_type'] },
  'M54-allocation': { kind: 'model_list', model: 'fix.cost.allocation',
    cols: ['name','pool_id','date_from','date_to','direct_cost','allocated_overhead','state','move_id'],
    stateField: 'state',
    actions: [{m:'action_compute',l:'Compute'},{m:'action_post',l:'Post'},{m:'action_reverse',l:'Reverse'},{m:'action_reset_draft',l:'Reset to Draft'}] },
  'M54-jobs': { kind: 'table_report', module: 'M54', report: 'job_costing' },
  'M54-jobdist': { kind: 'table_report', module: 'M54', report: 'job_margin_distribution' },
  'M54-loaded': { kind: 'table_report', module: 'M54', report: 'technician_loaded_cost' },
  // Profitability
  'M54-lines': { kind: 'model_list', model: 'fix.business.line',
    cols: ['code','name','revenue_stream_no','is_profit_centre'] },
  'M54-streams': { kind: 'table_report', module: 'M54', report: 'business_line_pnl' },
  'M54-branches': { kind: 'table_report', module: 'M54', report: 'branch_profitability' },
  'M54-customers': { kind: 'table_report', module: 'M54', report: 'customer_profitability' },
  'M54-unitecon': { kind: 'table_report', module: 'M54', report: 'unit_economics' },
  // Budgeting
  'M54-budgets': { kind: 'model_list', model: 'fix.budget',
    cols: ['name','version_id','budget_type','fiscal_year','planned_amount','actual_amount','variance','state'],
    stateField: 'state', actions: [{m:'action_refresh_actuals',l:'Refresh Actuals'}] },
  'M54-budget-lines': { empty: 'Budget lines are entered on their budget.', kind: 'model_list', model: 'fix.budget.line', create: false,
    cols: ['budget_id','version_id','account_id','branch_id','business_line_id','cost_centre','date_from','date_to','planned_amount','actual_amount','variance'] },
  'M54-workflow': { kind: 'model_list', model: 'fix.budget.version',
    cols: ['name','version_type','fiscal_year','date_from','date_to','planned_revenue','planned_cost','dofa_tier_required','approval_state','state','submitted_by','approved_by'],
    stateField: 'state', domain: [['version_type','in',['budget','forecast']]],
    // Approval is decided from the M63 approval inbox (CFO / Board tier), never here.
    actions: [{m:'action_load_drivers',l:'Load Drivers'},{m:'action_generate_plan',l:'Generate Plan'},{m:'action_submit',l:'Submit for Approval'},{m:'action_reject',l:'Reject',ask:'Reason for rejecting this version',kwarg:'reason'},{m:'action_reset_draft',l:'Back to Draft'},{m:'action_create_revision',l:'Create Revision'}] },
  'M54-bva': { kind: 'table_report', module: 'M54', report: 'budget_variance' },
  // Planning
  'M54-rolling': { kind: 'table_report', module: 'M54', report: 'rolling_forecast' },
  'M54-scenario': { kind: 'model_list', model: 'fix.budget.version',
    cols: ['name','fiscal_year','date_from','date_to','base_version_id','planned_revenue','planned_cost','planned_margin','state'],
    stateField: 'state', domain: [['version_type','=','scenario']],
    context: { default_version_type: 'scenario' },
    actions: [{m:'action_load_drivers',l:'Load Drivers'},{m:'action_generate_plan',l:'Generate Plan'},{m:'action_submit',l:'Submit for Approval'}] },
  'M54-board': { kind: 'table_report', module: 'M54', report: 'board_pack' },
  'M54-boardpacks': { kind: 'model_list', model: 'fix.board.pack',
    cols: ['name','date_from','date_to','assembled_by','issued_by','export_filename','state'],
    stateField: 'state', actions: [{m:'action_assemble',l:'Assemble'},{m:'action_issue',l:'Issue'}] },


  /* ===== master-data forms (batch 2) — D365 in-workspace ===== */
  'M54-form-bline': {
    kind: 'model_form',
    model: 'fix.business.line',
    title: "Business Line",
    back: 'M54-lines',
    sections: [
      { title: "Business Line", note: "A business line used as a costing dimension; postings require it where the COA rule says so.",
        fields: [
          { name: 'code', required: true, label: "Code" },
          { name: 'name', required: true, label: "Name" },
          { name: 'name_bn', label: "Name (Bengali)" },
          { name: 'sequence', label: "Sequence" },
          { name: 'revenue_stream_no', label: "Revenue Stream No." },
          { name: 'is_profit_centre', label: "Profit Centre" },
          { name: 'active', label: "Active" }
        ] }
    ]
  },
  'M54-form-budget': {
    kind: 'model_form',
    model: 'fix.budget',
    title: "Budget",
    back: 'M54-budgets',
    sections: [
      { title: "Budget", note: "A budget per business line and period; variance compares actual postings against it.",
        fields: [
          { name: 'company_id', required: true, label: "Company" },
          { name: 'name', required: true, label: "Name" },
          { name: 'budget_type', required: true, label: "Budget Type" },
          { name: 'fiscal_year', required: true, label: "Fiscal Year" },
          { name: 'currency_id', required: true, label: "Currency" },
          { name: 'state', readonly: true, label: "State (follows the version)" },
          { name: 'version_id', required: true, label: "Budget Version" },
          { name: 'date_from', label: "From" },
          { name: 'date_to', label: "To" },
          { name: 'planned_amount', readonly: true, label: "Planned (sum of the lines)" },
          { name: 'actual_amount', readonly: true, label: "Actual (posted ledger)" },
          { name: 'variance', readonly: true, label: "Variance" }
        ] }
    ],
    lines: {
      field: 'line_ids',
      title: 'Budget Lines — account, period and planned amount',
      note: 'A version is submitted only when its budgets have lines. Each line lies inside the budget window; the actual is read live from the posted ledger. The year and window are taken from the version when left blank.',
      fields: [
        { name: 'account_id', required: true, label: 'Account' },
        { name: 'date_from', required: true, label: 'From' },
        { name: 'date_to', required: true, label: 'To' },
        { name: 'planned_amount', required: true, label: 'Planned' },
        { name: 'branch_id', label: 'Branch' },
        { name: 'business_line_id', label: 'Business Line' },
        { name: 'cost_centre', label: 'Cost Centre' }
      ]
    }
  },

};

/* built-in report chips -> the screen that shows that report */
export const REPORT_ROUTES = {
  'M54:Business-Line P&L (14)': 'M54-streams',
  "M54:Business-Line P&L": "M54-streams",
  "M54:Branch League Table": "M54-branches",
  "M54:Budget vs Actual": "M54-bva",
  "M54:Job Margin Distribution": "M54-jobdist",
  "M54:Customer Profitability Deciles": "M54-customers",
  "M54:Unit Economics per Repair": "M54-unitecon",
  "M54:Rolling Forecast": "M54-rolling",
  "M54:Board Pack": "M54-board",
};

/* data-entry form chips -> real model forms */
export const FORM_MODELS = {
  'M54:Budget Version': 'fix.budget.version',
  'M54:Allocation Rule': 'fix.cost.pool',
  'M54:Allocation Cycle': 'fix.cost.allocation',
  'M54:Scenario': 'fix.budget.version',
  'M54:Board Pack': 'fix.board.pack',
  'M54:Cost Element': 'fix.cost.element',
  'M54:Cost Centre': 'fix.cost.centre',
  'M54:Planned Activity Rate': 'fix.activity.rate',
  'M54:Business Line': 'fix.business.line',
  'M54:Business-Line Variance Explanation': 'fix.variance.explanation',
  'M54:Branch Variance Explanation': 'fix.variance.explanation',
  'M54:Budget Target': 'fix.budget.target',
  'M54:Variance Explanation': 'fix.variance.explanation',
  'M54:Forecast Version': 'fix.budget.version',
};

/* ============ D365 IN-WORKSPACE FORM SCREENS (M54 re-audit v2) ========
 * The registry's three data-entry chips (and the two extra surfaces the
 * fragment declares) open Dynamics-365 record forms in the workspace —
 * never an Odoo dialog. Scenario IS a budget version (version_type
 * scenario), so both chips open the same form with a told-through note. */
Object.assign(SCREENS, {
  'M54-form-version': {
    kind: 'model_form',
    model: 'fix.budget.version',
    title: 'Budget Version',
    back: 'M54-workflow',
    status: { field: 'state', labels: {
      draft: 'Draft', submitted: 'Submitted', approved: 'Approved',
      rejected: 'Rejected', superseded: 'Superseded' } },
    tabs: [
      { id: 'version', label: 'Version', bn: 'সংস্করণ' },
      { id: 'plan', label: 'Driver Plan', bn: 'চালক পরিকল্পনা' },
      { id: 'approval', label: 'Approval', bn: 'অনুমোদন' }
    ],
    sections: [
      { tab: 'version', title: 'Version', note: 'A budget, forecast or scenario version for one fiscal year. A scenario reads against a base version, which is what makes the what-if comparison possible. Plan it line by line on its budgets, or from drivers on the Driver Plan tab.',
        fields: [
          { name: 'name', required: true, label: 'Version Name' },
          { name: 'version_type', required: true, label: 'Version Type' },
          { name: 'fiscal_year', required: true, label: 'Fiscal Year' },
          { name: 'date_from', required: true, label: 'From' },
          { name: 'date_to', required: true, label: 'To' },
          { name: 'base_version_id', label: 'Base Version (scenarios)' },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'state', readonly: true, label: 'State' },
          { name: 'revision_of_id', readonly: true, label: 'Revision Of' }
        ] },
      { tab: 'plan', title: 'Driver Plan', note: 'Generate Plan turns the scenario drivers below into monthly budget lines on these four accounts. Load Drivers measures the base values over the window (default: the twelve months before the version starts); only the scenario value is yours to change.',
        fields: [
          { name: 'revenue_account_id', label: 'Revenue Account' },
          { name: 'parts_account_id', label: 'Parts Cost Account' },
          { name: 'labour_account_id', label: 'Labour Cost Account' },
          { name: 'overhead_account_id', label: 'Overhead Account' },
          { name: 'base_date_from', label: 'Drivers Measured From' },
          { name: 'base_date_to', label: 'Drivers Measured To' },
          { name: 'planned_revenue', readonly: true, label: 'Planned Revenue' },
          { name: 'planned_cost', readonly: true, label: 'Planned Cost' },
          { name: 'planned_margin', readonly: true, label: 'Planned Margin' }
        ] },
      { tab: 'approval', title: 'Approval (system)', note: 'Submit routes the version to the DOFA tier of its planned total; the decision is taken in the M63 approval inbox.',
        fields: [
          { name: 'dofa_tier_required', readonly: true, label: 'Approval Tier (from the planned total)' },
          { name: 'approval_state', readonly: true, label: 'Approval' },
          { name: 'submitted_by', readonly: true, label: 'Submitted By' },
          { name: 'approved_by', readonly: true, label: 'Approved By' },
          { name: 'rejection_reason', readonly: true, label: 'Rejection Reason' }
        ] }
    ],
    lines: {
      field: 'driver_ids',
      title: 'Scenario Drivers',
      note: 'Press Load Drivers on the list to fill these from the ledger, then change the scenario values. The base value is measured, not typed.',
      fields: [
        { name: 'driver_key', required: true, label: 'Driver' },
        { name: 'base_value', readonly: true, label: 'Base (Actuals)' },
        { name: 'scenario_value', label: 'Scenario Value' }
      ]
    }
  },

  /* A new scenario from the Scenario Modelling grid: the same record, typed
   * as a scenario so it lands on that grid and not on the budget workflow. */
  'M54-form-scenario': {
    kind: 'model_form',
    model: 'fix.budget.version',
    title: 'Scenario',
    back: 'M54-scenario',
    status: { field: 'state', labels: {
      draft: 'Draft', submitted: 'Submitted', approved: 'Approved',
      rejected: 'Rejected', superseded: 'Superseded' } },
    tabs: [
      { id: 'version', label: 'Scenario', bn: 'পরিস্থিতি' },
      { id: 'plan', label: 'Driver Plan', bn: 'চালক পরিকল্পনা' }
    ],
    sections: [
      { tab: 'version', title: 'Scenario', note: 'A what-if on one fiscal year, read against its base version. It never replaces an approved budget.',
        fields: [
          { name: 'name', required: true, label: 'Scenario Name' },
          { name: 'version_type', readonly: true, value: 'scenario', label: 'Version Type' },
          { name: 'fiscal_year', required: true, label: 'Fiscal Year' },
          { name: 'date_from', required: true, label: 'From' },
          { name: 'date_to', required: true, label: 'To' },
          { name: 'base_version_id', label: 'Compared With' },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'state', readonly: true, label: 'State' }
        ] },
      { tab: 'plan', title: 'Driver Plan', note: 'Generate Plan turns the scenario drivers below into monthly budget lines on these four accounts. Load Drivers measures the base values over the window (default: the twelve months before the scenario starts); only the scenario value is yours to change.',
        fields: [
          { name: 'revenue_account_id', label: 'Revenue Account' },
          { name: 'parts_account_id', label: 'Parts Cost Account' },
          { name: 'labour_account_id', label: 'Labour Cost Account' },
          { name: 'overhead_account_id', label: 'Overhead Account' },
          { name: 'base_date_from', label: 'Drivers Measured From' },
          { name: 'base_date_to', label: 'Drivers Measured To' },
          { name: 'planned_revenue', readonly: true, label: 'Planned Revenue' },
          { name: 'planned_cost', readonly: true, label: 'Planned Cost' },
          { name: 'planned_margin', readonly: true, label: 'Planned Margin' }
        ] }
    ],
    lines: {
      field: 'driver_ids',
      title: 'Scenario Drivers',
      note: 'Press Load Drivers on the list to fill these from the ledger, then change the scenario values. The base value is measured, not typed.',
      fields: [
        { name: 'driver_key', required: true, label: 'Driver' },
        { name: 'base_value', readonly: true, label: 'Base (Actuals)' },
        { name: 'scenario_value', label: 'Scenario Value' }
      ]
    }
  },

  'M54-form-pool': {
    kind: 'model_form',
    model: 'fix.cost.pool',
    title: 'Cost Pool / Allocation Rule',
    back: 'M54-pools',
    sections: [
      { title: 'Cost Pool', note: 'The pool collects posted overhead and spreads it to its receivers on the chosen basis; "load into technician rate" includes it in the M54 loaded-cost rate. It gathers nothing until the Cost Elements screen names the GL accounts it collects.',
        fields: [
          { name: 'code', required: true, label: 'Pool Code' },
          { name: 'name', required: true, label: 'Pool Name' },
          { name: 'pool_type', required: true, label: 'Pool Type' },
          { name: 'receiver_type', required: true, label: 'Receiver' },
          { name: 'allocation_basis', required: true, label: 'Allocation Basis' },
          { name: 'target_account_id', label: 'Absorbed Overhead Account (Dr)' },
          { name: 'clearing_account_id', label: 'Pool Clearing Account (Cr)' },
          { name: 'journal_id', label: 'Allocation Journal' },
          { name: 'include_in_labour_rate', label: 'Load Into Technician Rate' },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'element_count', readonly: true, label: 'Cost Elements' }
        ] }
    ],
    lines: {
      field: 'share_ids',
      title: 'Fixed Shares — only for the Fixed Shares basis',
      note: 'Each share names a branch or a business line, as the Receiver says; together they must total 100% when the cycle computes.',
      total: { field: 'percent', label: 'Total Share %', target: 100 },
      fields: [
        { name: 'branch_id', label: 'Branch' },
        { name: 'business_line_id', label: 'Business Line' },
        { name: 'percent', required: true, label: 'Share %' }
      ]
    }
  },

  'M54-form-element': {
    kind: 'model_form',
    model: 'fix.cost.element',
    title: 'Cost Element',
    back: 'M54-elements',
    sections: [
      { title: 'Cost Element', note: 'A named group of GL accounts inside a pool: their posted balances are what the pool gathers. An account sits in one element of one active pool only, so no cost is gathered twice.',
        fields: [
          { name: 'pool_id', required: true, label: 'Cost Pool' },
          { name: 'code', required: true, label: 'Code' },
          { name: 'name', required: true, label: 'Name' },
          { name: 'element_type', required: true, label: 'Element Type' },
          { name: 'account_ids', label: 'GL Accounts' }
        ] }
    ]
  },

  'M54-form-allocation': {
    kind: 'model_form',
    model: 'fix.cost.allocation',
    title: 'Allocation Cycle',
    back: 'M54-allocation',
    sections: [
      { title: 'Allocation Cycle', note: 'One execution of a pool over a period: direct cost plus the allocated overhead, posted to the receivers\' accounts.',
        fields: [
          { name: 'name', required: true, label: 'Cycle Name' },
          { name: 'pool_id', required: true, label: 'Cost Pool' },
          { name: 'date_from', label: 'From' },
          { name: 'date_to', label: 'To' },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'state', readonly: true, label: 'State' },
          { name: 'computed_by', readonly: true, label: 'Computed By' },
          { name: 'posted_by', readonly: true, label: 'Posted By (reviewer)' }
        ] }
    ]
  },

  'M54-form-boardpack': {
    kind: 'model_form',
    model: 'fix.board.pack',
    title: 'Board Pack',
    back: 'M54-boardpacks',
    status: { field: 'state', labels: {
      draft: 'Draft', assembled: 'Assembled', issued: 'Issued' } },
    sections: [
      { title: 'Board Pack', note: 'Assembling snapshots the period\'s management reports; issuing freezes the pack as the record of what the board saw.',
        fields: [
          { name: 'name', required: true, label: 'Pack Name' },
          { name: 'date_from', required: true, label: 'From' },
          { name: 'date_to', required: true, label: 'To' },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'state', readonly: true, label: 'State' },
          { name: 'assembled_by', readonly: true, label: 'Assembled By' },
          { name: 'issued_by', readonly: true, label: 'Issued By' }
        ] }
    ]
  }
});

/* ============ M54 SUB-MODULE CAPTURE AUDIT (2026-11-17) ===============
 * Pages 3 (Job & Contract Costing) and 5 (Branch & Channel Profitability)
 * captured nothing, page 7 offered "+ New" Budget on the variance page, and
 * four spec records had no screen at all: the cost centre with its owner
 * (FR-FPA-001), the approved planned activity rate (FR-FPA-012/013,
 * BRU-FPA-16), the top-down budget target (FR-FPA-029) and the owner
 * variance explanation (FR-FPA-037, BRU-FPA-12). Backend: cd_fpa
 * models/fix_fpa_capture.py. */
const VARIANCE_COLS = ['name','scope_type','budget_line_id','branch_id','business_line_id','date_from','date_to','planned','actual','variance','variance_pct','owner_id','due_date','state'];
const VARIANCE_ACTIONS = [
  {m:'action_remeasure',l:'Re-measure'},
  {m:'action_submit',l:'Submit Explanation'},
  {m:'action_accept',l:'Accept'},
  {m:'action_return',l:'Return to Owner',ask:'What must the owner add or correct?',kwarg:'reason'}
];
const VARIANCE_STATUS = { field: 'state', labels: {
  open: 'Awaiting Explanation', submitted: 'Submitted', accepted: 'Accepted', returned: 'Returned' } };
const VARIANCE_TABS = [
  { id: 'variance', label: 'Variance', bn: 'বিচ্যুতি' },
  { id: 'explain', label: 'Explanation', bn: 'ব্যাখ্যা' },
  { id: 'review', label: 'Review', bn: 'পর্যালোচনা' }
];

Object.assign(SCREENS, {
  'M54-cost-centres': { kind: 'model_list', model: 'fix.cost.centre',
    cols: ['code','name','parent_id','branch_id','owner_id','centre_type','date_from','date_to','active'] },
  'M54-activity-rates': { kind: 'model_list', model: 'fix.activity.rate',
    cols: ['name','activity_type','branch_id','planned_rate','measured_rate','effective_from','effective_to','state','submitted_by','approved_by'],
    stateField: 'state',
    actions: [
      {m:'action_measure',l:'Measure Actual Rate'},
      {m:'action_submit',l:'Submit for Approval'},
      {m:'action_approve',l:'Approve'},
      {m:'action_reject',l:'Reject',ask:'Reason for rejecting this rate',kwarg:'reason'}
    ] },
  'M54-targets': { kind: 'model_list', model: 'fix.budget.target',
    cols: ['name','version_id','scope_type','branch_id','business_line_id','cost_centre_id','target_type','target_amount','plan_amount','departure','departure_pct','state','issued_by'],
    stateField: 'state',
    actions: [
      {m:'action_issue',l:'Issue to Preparers'},
      {m:'action_withdraw',l:'Withdraw',ask:'Reason for withdrawing this target',kwarg:'reason'}
    ] },
  'M54-variances': { kind: 'model_list', model: 'fix.variance.explanation',
    cols: VARIANCE_COLS, stateField: 'state', actions: VARIANCE_ACTIONS },
  'M54-variances-branch': { kind: 'model_list', model: 'fix.variance.explanation',
    cols: ['name','branch_id','date_from','date_to','planned','actual','variance','variance_pct','owner_id','due_date','state'],
    domain: [['scope_type','=','branch']], stateField: 'state', actions: VARIANCE_ACTIONS },
  'M54-variances-bl': { kind: 'model_list', model: 'fix.variance.explanation',
    cols: ['name','business_line_id','date_from','date_to','planned','actual','variance','variance_pct','owner_id','due_date','state'],
    domain: [['scope_type','=','business_line']], stateField: 'state', actions: VARIANCE_ACTIONS },
  'M54-forecasts': { kind: 'model_list', model: 'fix.budget.version',
    cols: ['name','fiscal_year','date_from','date_to','planned_revenue','planned_cost','planned_margin','approval_state','state','submitted_by','approved_by'],
    stateField: 'state', domain: [['version_type','=','forecast']],
    context: { default_version_type: 'forecast' },
    actions: [{m:'action_load_drivers',l:'Load Drivers'},{m:'action_generate_plan',l:'Generate Plan'},{m:'action_submit',l:'Submit for Approval'},{m:'action_create_revision',l:'Create Revision'}] },

  'M54-form-centre': {
    kind: 'model_form',
    model: 'fix.cost.centre',
    title: 'Cost Centre',
    back: 'M54-cost-centres',
    sections: [
      { title: 'Cost Centre', note: 'The code is the one written on budget lines and journal dimensions. The owner is accountable for the centre budget and explains its variances (BRU-FPA-12).',
        fields: [
          { name: 'code', required: true, label: 'Code' },
          { name: 'name', required: true, label: 'Name' },
          { name: 'name_bn', label: 'Name (Bengali)' },
          { name: 'parent_id', label: 'Parent Cost Centre' },
          { name: 'branch_id', label: 'Branch' },
          { name: 'owner_id', required: true, label: 'Owner' },
          { name: 'centre_type', required: true, label: 'Allocation Behaviour' },
          { name: 'date_from', label: 'Active From' },
          { name: 'date_to', label: 'Active To' },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'note', label: 'What It Covers' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },

  'M54-form-rate': {
    kind: 'model_form',
    model: 'fix.activity.rate',
    title: 'Planned Activity Rate',
    back: 'M54-activity-rates',
    status: { field: 'state', labels: {
      draft: 'Draft', submitted: 'Submitted', approved: 'Approved', rejected: 'Rejected', superseded: 'Superseded' } },
    tabs: [
      { id: 'rate', label: 'Rate', bn: 'হার' },
      { id: 'compare', label: 'Compare With Actuals', bn: 'প্রকৃতের সাথে তুলনা' },
      { id: 'approval', label: 'Approval', bn: 'অনুমোদন' }
    ],
    sections: [
      { tab: 'rate', title: 'Planned Rate', note: 'The fully loaded cost of one unit of activity. Once approved, job costing applies it to every work-order hour of the branch from the effective date, so the same hour costs the same on every job (BRU-FPA-16). A branch without its own rate uses the all-branch rate.',
        fields: [
          { name: 'activity_type', required: true, label: 'Activity' },
          { name: 'branch_id', label: 'Branch (blank: all branches)' },
          { name: 'planned_rate', required: true, label: 'Planned Rate per Unit' },
          { name: 'currency_id', required: true, label: 'Currency' },
          { name: 'effective_from', required: true, label: 'Effective From' },
          { name: 'effective_to', label: 'Effective To' },
          { name: 'basis', required: true, label: 'Composition (salary, benefits, tools, vehicle, training, non-productive time)' },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'name', readonly: true, label: 'Reference' }
        ] },
      { tab: 'compare', title: 'Actual Loaded Rate', note: 'Measure Actual Rate on the list reads payroll, loaded overhead and productive work-order hours over this window (default: the twelve months before the rate takes effect).',
        fields: [
          { name: 'measure_from', label: 'Compare From' },
          { name: 'measure_to', label: 'Compare To' },
          { name: 'measured_rate', readonly: true, label: 'Actual Loaded Rate' },
          { name: 'measured_hours', readonly: true, label: 'Productive Hours Measured' }
        ] },
      { tab: 'approval', title: 'Approval (system)', note: 'An Accounting Administrator who neither prepared nor submitted the rate approves it. Approving closes the rate it replaces the day before; an approved rate is never edited.',
        fields: [
          { name: 'state', readonly: true, label: 'State' },
          { name: 'submitted_by', readonly: true, label: 'Submitted By' },
          { name: 'approved_by', readonly: true, label: 'Approved By' },
          { name: 'approved_at', readonly: true, label: 'Approved At' },
          { name: 'rejection_reason', readonly: true, label: 'Rejection Reason' },
          { name: 'superseded_by_id', readonly: true, label: 'Replaced By' }
        ] }
    ]
  },

  'M54-form-target': {
    kind: 'model_form',
    model: 'fix.budget.target',
    title: 'Budget Target',
    back: 'M54-targets',
    status: { field: 'state', labels: { draft: 'Draft', issued: 'Issued', withdrawn: 'Withdrawn' } },
    sections: [
      { title: 'Top-Down Target', note: 'Set by an Accounting Administrator (the CFO) for a draft budget or forecast version, for the whole company or one branch, business line or cost centre. The plan is read against it live; submitting the version records the departures.',
        fields: [
          { name: 'version_id', required: true, label: 'Budget Version' },
          { name: 'scope_type', required: true, label: 'Target For' },
          { name: 'branch_id', label: 'Branch' },
          { name: 'business_line_id', label: 'Business Line' },
          { name: 'cost_centre_id', label: 'Cost Centre' },
          { name: 'target_type', required: true, label: 'Target Measure' },
          { name: 'target_amount', required: true, label: 'Target' },
          { name: 'note', label: 'Guidance to Preparers' },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'plan_amount', readonly: true, label: 'Planned in the Version' },
          { name: 'departure', readonly: true, label: 'Plan minus Target' },
          { name: 'departure_pct', readonly: true, label: 'Departure %' },
          { name: 'issued_by', readonly: true, label: 'Issued By' }
        ] }
    ]
  },

  'M54-form-variance': {
    kind: 'model_form',
    model: 'fix.variance.explanation',
    title: 'Variance Explanation',
    back: 'M54-variances',
    status: VARIANCE_STATUS,
    tabs: VARIANCE_TABS,
    sections: [
      { tab: 'variance', title: 'Variance', note: 'Pick what the variance is of and the period. Saving measures budget, actual and variance from the approved budget and the posted ledger; the monthly job raises these itself for every line above the threshold.',
        fields: [
          { name: 'scope_type', required: true, label: 'Variance Of' },
          { name: 'budget_line_id', label: 'Budget Line (approved version)' },
          { name: 'branch_id', label: 'Branch' },
          { name: 'business_line_id', label: 'Business Line' },
          { name: 'date_from', required: true, label: 'Period From' },
          { name: 'date_to', required: true, label: 'Period To' },
          { name: 'cost_centre_id', label: 'Cost Centre' },
          { name: 'owner_id', label: 'Accountable Owner (blank: the cost-centre owner or the budget preparer)' },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'version_id', readonly: true, label: 'Approved Version' },
          { name: 'planned', readonly: true, label: 'Budget (measured)' },
          { name: 'actual', readonly: true, label: 'Actual from the GL (measured)' },
          { name: 'variance', readonly: true, label: 'Variance (favourable +)' },
          { name: 'variance_pct', readonly: true, label: 'Variance %' },
          { name: 'breached', readonly: true, label: 'Above Threshold' },
          { name: 'due_date', readonly: true, label: 'Explain By (3 working days)' }
        ] },
      { tab: 'explain', title: 'Owner Explanation', note: 'Written by the accountable owner only, then submitted for review. The figures on the Variance tab are measured from the approved budget and the posted ledger, never typed.',
        fields: [
          { name: 'root_cause', label: 'Root Cause' },
          { name: 'explanation', label: 'Explanation' },
          { name: 'action_committed', label: 'Action Committed' }
        ] },
      { tab: 'review', title: 'Review (system)', note: 'An Accounting Administrator who is neither the owner nor the submitter accepts the explanation or returns it with a reason.',
        fields: [
          { name: 'state', readonly: true, label: 'Status' },
          { name: 'submitted_by', readonly: true, label: 'Submitted By' },
          { name: 'submitted_at', readonly: true, label: 'Submitted At' },
          { name: 'accepted_by', readonly: true, label: 'Accepted By' },
          { name: 'return_reason', readonly: true, label: 'Returned Because' },
          { name: 'threshold_amount', readonly: true, label: 'Threshold Amount' },
          { name: 'threshold_pct', readonly: true, label: 'Threshold %' }
        ] }
    ]
  },

  'M54-form-variance-branch': {
    kind: 'model_form',
    model: 'fix.variance.explanation',
    title: 'Branch Variance Explanation',
    back: 'M54-variances-branch',
    status: VARIANCE_STATUS,
    tabs: VARIANCE_TABS,
    sections: [
      { tab: 'variance', title: 'Variance', note: 'The branch result against every approved budget line coded to the branch, for the period. The branch manager or cost-centre owner explains it.',
        fields: [
          { name: 'scope_type', readonly: true, value: 'branch', label: 'Variance Of' },
          { name: 'branch_id', required: true, label: 'Branch' },
          { name: 'date_from', required: true, label: 'Period From' },
          { name: 'date_to', required: true, label: 'Period To' },
          { name: 'cost_centre_id', label: 'Cost Centre' },
          { name: 'owner_id', label: 'Accountable Owner (blank: the cost-centre owner or the budget preparer)' },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'version_id', readonly: true, label: 'Approved Version' },
          { name: 'planned', readonly: true, label: 'Budget (measured)' },
          { name: 'actual', readonly: true, label: 'Actual from the GL (measured)' },
          { name: 'variance', readonly: true, label: 'Variance (favourable +)' },
          { name: 'variance_pct', readonly: true, label: 'Variance %' },
          { name: 'breached', readonly: true, label: 'Above Threshold' },
          { name: 'due_date', readonly: true, label: 'Explain By (3 working days)' }
        ] },
      { tab: 'explain', title: 'Owner Explanation', note: 'Written by the accountable owner only, then submitted for review. The figures on the Variance tab are measured from the approved budget and the posted ledger, never typed.',
        fields: [
          { name: 'root_cause', label: 'Root Cause' },
          { name: 'explanation', label: 'Explanation' },
          { name: 'action_committed', label: 'Action Committed' }
        ] },
      { tab: 'review', title: 'Review (system)', note: 'An Accounting Administrator who is neither the owner nor the submitter accepts the explanation or returns it with a reason.',
        fields: [
          { name: 'state', readonly: true, label: 'Status' },
          { name: 'submitted_by', readonly: true, label: 'Submitted By' },
          { name: 'submitted_at', readonly: true, label: 'Submitted At' },
          { name: 'accepted_by', readonly: true, label: 'Accepted By' },
          { name: 'return_reason', readonly: true, label: 'Returned Because' },
          { name: 'threshold_amount', readonly: true, label: 'Threshold Amount' },
          { name: 'threshold_pct', readonly: true, label: 'Threshold %' }
        ] }
    ]
  },

  'M54-form-variance-bl': {
    kind: 'model_form',
    model: 'fix.variance.explanation',
    title: 'Business-Line Variance Explanation',
    back: 'M54-variances-bl',
    status: VARIANCE_STATUS,
    tabs: VARIANCE_TABS,
    sections: [
      { tab: 'variance', title: 'Variance', note: 'The business-line result against every approved budget line coded to the line, for the period.',
        fields: [
          { name: 'scope_type', readonly: true, value: 'business_line', label: 'Variance Of' },
          { name: 'business_line_id', required: true, label: 'Business Line' },
          { name: 'date_from', required: true, label: 'Period From' },
          { name: 'date_to', required: true, label: 'Period To' },
          { name: 'cost_centre_id', label: 'Cost Centre' },
          { name: 'owner_id', label: 'Accountable Owner (blank: the cost-centre owner or the budget preparer)' },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'version_id', readonly: true, label: 'Approved Version' },
          { name: 'planned', readonly: true, label: 'Budget (measured)' },
          { name: 'actual', readonly: true, label: 'Actual from the GL (measured)' },
          { name: 'variance', readonly: true, label: 'Variance (favourable +)' },
          { name: 'variance_pct', readonly: true, label: 'Variance %' },
          { name: 'breached', readonly: true, label: 'Above Threshold' },
          { name: 'due_date', readonly: true, label: 'Explain By (3 working days)' }
        ] },
      { tab: 'explain', title: 'Owner Explanation', note: 'Written by the accountable owner only, then submitted for review. The figures on the Variance tab are measured from the approved budget and the posted ledger, never typed.',
        fields: [
          { name: 'root_cause', label: 'Root Cause' },
          { name: 'explanation', label: 'Explanation' },
          { name: 'action_committed', label: 'Action Committed' }
        ] },
      { tab: 'review', title: 'Review (system)', note: 'An Accounting Administrator who is neither the owner nor the submitter accepts the explanation or returns it with a reason.',
        fields: [
          { name: 'state', readonly: true, label: 'Status' },
          { name: 'submitted_by', readonly: true, label: 'Submitted By' },
          { name: 'submitted_at', readonly: true, label: 'Submitted At' },
          { name: 'accepted_by', readonly: true, label: 'Accepted By' },
          { name: 'return_reason', readonly: true, label: 'Returned Because' },
          { name: 'threshold_amount', readonly: true, label: 'Threshold Amount' },
          { name: 'threshold_pct', readonly: true, label: 'Threshold %' }
        ] }
    ]
  },

  /* A forecast is a budget version typed forecast: the same record and
   * workflow, captured from the Variance & Forecast page. */
  'M54-form-forecast': {
    kind: 'model_form',
    model: 'fix.budget.version',
    title: 'Forecast Version',
    back: 'M54-forecasts',
    status: { field: 'state', labels: {
      draft: 'Draft', submitted: 'Submitted', approved: 'Approved',
      rejected: 'Rejected', superseded: 'Superseded' } },
    tabs: [
      { id: 'version', label: 'Forecast', bn: 'পূর্বাভাস' },
      { id: 'plan', label: 'Driver Plan', bn: 'চালক পরিকল্পনা' }
    ],
    sections: [
      { tab: 'version', title: 'Forecast', note: 'A driver-based forecast of the result for one fiscal year. Once approved it is the forecast the variance and rolling views read; a re-forecast is a revision, and the approved one is kept.',
        fields: [
          { name: 'name', required: true, label: 'Forecast Name' },
          { name: 'version_type', readonly: true, value: 'forecast', label: 'Version Type' },
          { name: 'fiscal_year', required: true, label: 'Fiscal Year' },
          { name: 'date_from', required: true, label: 'From' },
          { name: 'date_to', required: true, label: 'To' },
          { name: 'base_version_id', label: 'Compared With' },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'state', readonly: true, label: 'State' }
        ] },
      { tab: 'plan', title: 'Driver Plan', note: 'Generate Plan turns the drivers below into monthly lines on these four accounts. Load Drivers measures the base values from the ledger; only the forecast value is yours to change.',
        fields: [
          { name: 'revenue_account_id', label: 'Revenue Account' },
          { name: 'parts_account_id', label: 'Parts Cost Account' },
          { name: 'labour_account_id', label: 'Labour Cost Account' },
          { name: 'overhead_account_id', label: 'Overhead Account' },
          { name: 'base_date_from', label: 'Drivers Measured From' },
          { name: 'base_date_to', label: 'Drivers Measured To' },
          { name: 'planned_revenue', readonly: true, label: 'Planned Revenue' },
          { name: 'planned_cost', readonly: true, label: 'Planned Cost' },
          { name: 'planned_margin', readonly: true, label: 'Planned Margin' }
        ] }
    ],
    lines: {
      field: 'driver_ids',
      title: 'Forecast Drivers',
      note: 'Press Load Drivers on the list to fill these from the ledger, then change the forecast values. The base value is measured, not typed.',
      fields: [
        { name: 'driver_key', required: true, label: 'Driver' },
        { name: 'base_value', readonly: true, label: 'Base (Actuals)' },
        { name: 'scenario_value', label: 'Forecast Value' }
      ]
    }
  }
});

export const FORM_CHIPS = {
  'M54:Business Line': 'M54-form-bline',
  'M54:Budget': 'M54-form-budget',
  'M54:Budget Version': 'M54-form-version',
  'M54:Allocation Rule': 'M54-form-pool',
  'M54:Allocation Cycle': 'M54-form-allocation',
  'M54:Scenario': 'M54-form-scenario',
  'M54:Board Pack': 'M54-form-boardpack',
  'M54:Cost Element': 'M54-form-element',
  'M54:Cost Centre': 'M54-form-centre',
  'M54:Planned Activity Rate': 'M54-form-rate',
  'M54:Business-Line Variance Explanation': 'M54-form-variance-bl',
  'M54:Branch Variance Explanation': 'M54-form-variance-branch',
  'M54:Budget Target': 'M54-form-target',
  'M54:Variance Explanation': 'M54-form-variance',
  'M54:Forecast Version': 'M54-form-forecast',
  'M54:__by_model__': {
    'fix.business.line': 'M54-form-bline',
    'fix.budget': 'M54-form-budget',
    'fix.budget.version': 'M54-form-version',
    'fix.cost.element': 'M54-form-element',
    'fix.cost.pool': 'M54-form-pool',
    'fix.cost.allocation': 'M54-form-allocation',
    'fix.board.pack': 'M54-form-boardpack',
    'fix.cost.centre': 'M54-form-centre',
    'fix.activity.rate': 'M54-form-rate',
    'fix.budget.target': 'M54-form-target',
    'fix.variance.explanation': 'M54-form-variance'
  },
  'M54:__by_screen__': {
    'M54-lines': 'M54-form-bline',
    'M54-budgets': 'M54-form-budget',
    'M54-workflow': 'M54-form-version',
    'M54-scenario': 'M54-form-scenario',
    'M54-elements': 'M54-form-element',
    'M54-pools': 'M54-form-pool',
    'M54-allocation': 'M54-form-allocation',
    'M54-boardpacks': 'M54-form-boardpack',
    'M54-cost-centres': 'M54-form-centre',
    'M54-activity-rates': 'M54-form-rate',
    'M54-targets': 'M54-form-target',
    'M54-variances': 'M54-form-variance',
    'M54-variances-branch': 'M54-form-variance-branch',
    'M54-variances-bl': 'M54-form-variance-bl',
    'M54-forecasts': 'M54-form-forecast'
  }
};

/* the module's "+ New" surface */
export const CREATE = {
  M54: { screen: 'M54-form-version', model: 'fix.budget.version', label: 'Budget Version' },
};
