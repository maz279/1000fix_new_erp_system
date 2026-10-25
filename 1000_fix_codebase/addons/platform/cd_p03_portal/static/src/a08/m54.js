/** @odoo-module **/
/* A08 · Finance & Treasury — M54 Costing, Budget & FP&A.
 * One file per A08 module (merged into P03_MODULES and the screen maps by
 * p03_modules_meta.js): the registry entry, the in-workspace data screens,
 * built-in report routes, data-entry form chips and the "+ New" surface. */

export const MODULE = {
  area: 'A08', code: 'M54', en: 'Costing, Budget & FP&A', title: 'M54 · Costing, Budget & FP&A',
  bn: 'ব্যয়, বাজেট ও এফপিএ', icon: '🧮',
  desc: 'Allocation cycles, job & contract costing, 14-stream business-line profitability, branch league, budgets.',
  kpis: [
    { l: 'Budget Variance', m: 'budget_total_variance' },
    { l: 'Branch League #1' },
    { l: 'Negative-Margin Branches' },
    { l: 'Job Costing Coverage' }
  ],
  groups: [
    { en: 'Costing', screens: [
      { id: 'M54-pools', en: 'Cost Pools & Elements', bn: 'ব্যয় পুল', t: 'g' },
      { id: 'M54-allocation', en: 'Allocation Cycles', bn: 'বণ্টন চক্র', t: 'c' },
      { id: 'M54-jobs', en: 'Job / Work-Order Costing', bn: 'কাজের ব্যয়', t: 'r' },
      { id: 'M54-loaded', en: 'Technician Loaded Cost', bn: 'কর্মী ব্যয়', t: 'r' }
    ]},
    { en: 'Profitability', screens: [
      { id: 'M54-streams', en: '14 Business-Line P&L', bn: '১৪ ব্যবসার লাভ', t: 'r' },
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
      { id: 'M54-board', en: 'Board Pack', bn: 'বোর্ড প্যাক', t: 'r' }
    ]}
  ],
  reports: ['Business-Line P&L (14)', 'Branch League Table', 'Budget vs Actual', 'Job Margin Distribution', 'Customer Profitability Deciles', 'Unit Economics per Repair'],
  forms: ['Budget Version', 'Allocation Rule', 'Scenario'],
  cross: ['Financial Accounting & GL', 'Workshop & Depot Repair', 'Business Intelligence'],
  freg: { src: 70, sub: [
    ['1', 'Cost Model', 9], ['2', 'Allocation Cycles', 10], ['3', 'Job & Contract Costing', 11],
    ['4', 'Business-Line Profitability', 9], ['5', 'Branch & Channel Profitability', 8], ['6', 'Budgeting', 11],
    ['7', 'Variance & Forecast', 8], ['8', 'Board Pack', 4]
  ] }
};

/* in-workspace data screens (checked before any stock Odoo view) */
export const SCREENS = {
  'M54-budgets': { kind: 'model_list', model: 'fix.budget',
    cols: ['name','fiscal_year','planned_amount','actual_amount','variance','state'],
    stateField: 'state' },
  'M54-allocation': { kind: 'model_list', model: 'fix.cost.allocation',
    cols: ['name','direct_cost','allocated_overhead','total_cost'] },
};

/* built-in report chips -> the screen that shows that report */
export const REPORT_ROUTES = {
  "M54:Budget vs Actual": "M54-budgets",
};

/* data-entry form chips -> real model forms */
export const FORM_MODELS = {
  'M54:Budget Version': 'fix.budget',
  'M54:Allocation Rule': 'fix.cost.allocation',
};

/* the module's "+ New" surface */
export const CREATE = {
  M54: { model: 'fix.budget', label: 'Budget' },
};
