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
      { id: 'M54-streams', en: 'Business-Line P&L', bn: 'ব্যবসা লাইনের লাভ-ক্ষতি', t: 'r' },
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
    ['1', 'Cost Model', 9], ['2', 'Allocation Cycles', 10], ['3', 'Job & Contract Costing', 11],
    ['4', 'Business-Line Profitability', 9], ['5', 'Branch & Channel Profitability', 8], ['6', 'Budgeting', 11],
    ['7', 'Variance & Forecast', 8], ['8', 'Board Pack', 4]
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
};

/* built-in report chips -> the screen that shows that report */
export const REPORT_ROUTES = {
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

/* the module's "+ New" surface */
export const CREATE = {
  M54: { model: 'fix.budget.version', label: 'Budget Version' },
};
