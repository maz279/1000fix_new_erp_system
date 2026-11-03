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
    { l: 'Branch League #1', m: 'fpa_branch_top' },
    { l: 'Negative-Margin Branches', m: 'fpa_negative_branches' },
    { l: 'Job Costing Coverage', m: 'fpa_job_costing_coverage' }
  ],
  groups: [
    { en: 'Costing', screens: [
      { id: 'M54-pools', en: 'Cost Pools & Elements', bn: 'ব্যয় পুল ও উপাদান', t: 'g' },
      { id: 'M54-allocation', en: 'Allocation Cycles', bn: 'বণ্টন চক্র', t: 'c' },
      { id: 'M54-jobs', en: 'Job / Work-Order Costing', bn: 'কাজের ব্যয়', t: 'r' },
      { id: 'M54-jobdist', en: 'Job Margin Distribution', bn: 'কাজের মার্জিন বিন্যাস', t: 'r' },
      { id: 'M54-loaded', en: 'Technician Loaded Cost', bn: 'কর্মী ব্যয়', t: 'r' }
    ]},
    { en: 'Profitability', screens: [
      { id: 'M54-lines', en: 'Business Lines', bn: 'ব্যবসা লাইন', t: 'g' },
      { id: 'M54-streams', en: '14 Business-Line P&L', bn: 'ব্যবসা লাইনের লাভ-ক্ষতি', t: 'r' },
      { id: 'M54-branches', en: 'Branch Profitability', bn: 'শাখা লাভজনকতা', t: 'r' },
      { id: 'M54-customers', en: 'Customer Profitability', bn: 'গ্রাহক লাভজনকতা', t: 'r' },
      { id: 'M54-unitecon', en: 'Unit Economics', bn: 'একক অর্থনীতি', t: 'r' }
    ]},
    { en: 'Budgeting', screens: [
      { id: 'M54-budgets', en: 'Operating & Capital Budgets', bn: 'বাজেট', t: 'g' },
      { id: 'M54-workflow', en: 'Budget Workflow', bn: 'বাজেট প্রবাহ', t: 'c' },
      { id: 'M54-bva', en: 'Variance Analysis', bn: 'বিচ্যুতি বিশ্লেষণ', t: 'r' }
    ]},
    { en: 'Planning', screens: [
      { id: 'M54-rolling', en: 'Rolling Forecast', bn: 'রোলিং পূর্বাভাস', t: 'r' },
      { id: 'M54-scenario', en: 'Scenario Modelling', bn: 'পরিস্থিতি মডেল', t: 'c' },
      { id: 'M54-board', en: 'Board Pack', bn: 'বোর্ড প্যাক', t: 'r' },
      { id: 'M54-boardpacks', en: 'Board Pack Archive', bn: 'বোর্ড প্যাক সংরক্ষণ', t: 'g' }
    ]}
  ],
  reports: ['Business-Line P&L', 'Branch League Table', 'Budget vs Actual', 'Job Margin Distribution', 'Customer Profitability Deciles', 'Unit Economics per Repair', 'Rolling Forecast', 'Board Pack'],
  forms: ['Budget Version', 'Allocation Rule', 'Allocation Cycle', 'Scenario', 'Board Pack'],
  cross: ['Financial Accounting & GL', 'Workshop & Depot Repair', 'Business Intelligence'],
  freg: { src: 70, sub: [
    ['1', 'Cost Model', 9, { model: 'fix.cost.pool', cols: ['code', 'name', 'pool_type', 'receiver_type', 'allocation_basis'], screens: ['M54-pools', 'M54-loaded'] }],
    ['2', 'Allocation Cycles', 10, { model: 'fix.cost.allocation', cols: ['name', 'pool_id', 'date_from', 'allocated_overhead', 'state'], screens: ['M54-allocation'] }],
    ['3', 'Job & Contract Costing', 11, { model: 'fix.workshop.job', cols: ['name', 'customer_id', 'parts_total', 'labour_total', 'total_repair_cost'], screens: ['M54-jobs', 'M54-jobdist'] }],
    ['4', 'Business-Line Profitability', 9, { model: 'fix.business.line', cols: ['code', 'name', 'revenue_stream_no', 'is_profit_centre'], screens: ['M54-lines', 'M54-streams', 'M54-unitecon'] }],
    ['5', 'Branch & Channel Profitability', 8, { model: 'fix.journal.dimension', cols: ['branch_id', 'channel', 'business_line', 'cost_centre', 'move_line_id'], screens: ['M54-branches', 'M54-customers'] }],
    ['6', 'Budgeting', 11, { model: 'fix.budget', cols: ['name', 'budget_type', 'fiscal_year', 'planned_amount', 'state'], screens: ['M54-budgets', 'M54-workflow'] }],
    ['7', 'Variance & Forecast', 8, { model: 'fix.budget', cols: ['name', 'fiscal_year', 'planned_amount', 'actual_amount', 'variance'], screens: ['M54-bva', 'M54-rolling', 'M54-scenario'] }],
    ['8', 'Board Pack', 4, { model: 'fix.board.pack', cols: ['name', 'date_from', 'date_to', 'issued_by', 'state'], screens: ['M54-board', 'M54-boardpacks'] }]
  ] }
};

/* in-workspace data screens (checked before any stock Odoo view) */
export const SCREENS = {
  // Costing
  'M54-pools': { kind: 'model_list', model: 'fix.cost.pool',
    cols: ['code','name','pool_type','receiver_type','allocation_basis','include_in_labour_rate','element_count','target_account_id','clearing_account_id'] },
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
  'M54-workflow': { kind: 'model_list', model: 'fix.budget.version',
    cols: ['name','version_type','fiscal_year','date_from','date_to','planned_revenue','planned_cost','state','submitted_by','approved_by'],
    stateField: 'state', domain: [['version_type','in',['budget','forecast']]],
    actions: [{m:'action_submit',l:'Submit'},{m:'action_approve',l:'Approve'},{m:'action_reject',l:'Reject'},{m:'action_reset_draft',l:'Back to Draft'}] },
  'M54-bva': { kind: 'table_report', module: 'M54', report: 'budget_variance' },
  // Planning
  'M54-rolling': { kind: 'table_report', module: 'M54', report: 'rolling_forecast' },
  'M54-scenario': { kind: 'model_list', model: 'fix.budget.version',
    cols: ['name','fiscal_year','date_from','date_to','base_version_id','planned_revenue','planned_cost','planned_margin','state'],
    stateField: 'state', domain: [['version_type','=','scenario']],
    context: { default_version_type: 'scenario' },
    actions: [{m:'action_load_drivers',l:'Load Drivers'},{m:'action_generate_plan',l:'Generate Plan'},{m:'action_submit',l:'Submit'},{m:'action_approve',l:'Approve'}] },
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
          { name: 'state', required: true, label: "State" },
          { name: 'version_id', label: "Budget Version" },
          { name: 'date_from', label: "From" }
        ] }
    ]
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
    sections: [
      { title: 'Version', note: 'A budget, forecast or scenario version for one fiscal year. A scenario reads against a base version, which is what makes the what-if comparison possible.',
        fields: [
          { name: 'name', required: true, label: 'Version Name' },
          { name: 'version_type', required: true, label: 'Version Type' },
          { name: 'fiscal_year', required: true, label: 'Fiscal Year' },
          { name: 'date_from', required: true, label: 'From' },
          { name: 'date_to', required: true, label: 'To' },
          { name: 'base_version_id', label: 'Base Version (scenarios)' },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'state', required: true, label: 'State' }
        ] }
    ]
  },

  'M54-form-pool': {
    kind: 'model_form',
    model: 'fix.cost.pool',
    title: 'Cost Pool / Allocation Rule',
    back: 'M54-pools',
    sections: [
      { title: 'Cost Pool', note: 'The pool collects posted overhead and spreads it to its receivers on the chosen basis; "load into technician rate" includes it in the M54 loaded-cost rate.',
        fields: [
          { name: 'code', required: true, label: 'Pool Code' },
          { name: 'name', required: true, label: 'Pool Name' },
          { name: 'pool_type', required: true, label: 'Pool Type' },
          { name: 'receiver_type', required: true, label: 'Receiver' },
          { name: 'allocation_basis', required: true, label: 'Allocation Basis' },
          { name: 'target_account_id', label: 'Target Account' },
          { name: 'clearing_account_id', label: 'Clearing Account' },
          { name: 'include_in_labour_rate', label: 'Load Into Technician Rate' },
          { name: 'operating_unit_id', label: 'Operating Unit' }
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
          { name: 'operating_unit_id', label: 'Operating Unit' }
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
          { name: 'state', required: true, label: 'State' }
        ] }
    ]
  }
});

export const FORM_CHIPS = {
  'M54:Business Line': 'M54-form-bline',
  'M54:Budget': 'M54-form-budget',
  'M54:Budget Version': 'M54-form-version',
  'M54:Allocation Rule': 'M54-form-pool',
  'M54:Allocation Cycle': 'M54-form-allocation',
  'M54:Scenario': 'M54-form-version',
  'M54:Board Pack': 'M54-form-boardpack',
  'M54:__by_model__': {
    'fix.business.line': 'M54-form-bline',
    'fix.budget': 'M54-form-budget',
    'fix.budget.version': 'M54-form-version',
    'fix.cost.pool': 'M54-form-pool',
    'fix.cost.allocation': 'M54-form-allocation',
    'fix.board.pack': 'M54-form-boardpack'
  },
  'M54:__by_screen__': {
    'M54-lines': 'M54-form-bline',
    'M54-budgets': 'M54-form-budget',
    'M54-workflow': 'M54-form-version',
    'M54-scenario': 'M54-form-version',
    'M54-pools': 'M54-form-pool',
    'M54-allocation': 'M54-form-allocation',
    'M54-boardpacks': 'M54-form-boardpack'
  }
};

/* the module's "+ New" surface */
export const CREATE = {
  M54: { screen: 'M54-form-version', model: 'fix.budget.version', label: 'Budget Version' },
};
