/** @odoo-module **/
/* A08 · Finance & Treasury — M49 Fixed Assets & Capex.
 * One file per A08 module (merged into P03_MODULES and the screen maps by
 * p03_modules_meta.js): the registry entry, the in-workspace data screens,
 * built-in report routes, data-entry form chips and the "+ New" surface.
 * Backend: cd_fixed_asset_ext; reports + KPIs in controllers/a08/m49.py. */

export const MODULE = {
  area: 'A08', code: 'M49', en: 'Fixed Assets & Capex', title: 'M49 · Fixed Assets & Capex',
  bn: 'স্থায়ী সম্পদ ও ক্যাপেক্স', icon: '🏗️',
  desc: 'Capex requests to retirement — CWIP, dual-book depreciation (accounting + tax Third Schedule), verification, IFRS 16 leases.',
  kpis: [
    { l: 'Gross Block', m: 'm49_gross_block' },
    { l: 'NBV', m: 'm49_nbv' },
    { l: 'CWIP Open', m: 'm49_cwip_open' },
    { l: 'Depreciation MTD', m: 'm49_dep_mtd' },
    { l: 'Lease Liability', m: 'm49_lease_liability' }
  ],
  groups: [
    { en: 'Capex', screens: [
      { id: 'M49-requests', en: 'Capex Requests', bn: 'ক্যাপেক্স অনুরোধ', t: 'g' },
      { id: 'M49-budget', en: 'Capital Budget', bn: 'মূলধনী বাজেট', t: 'g' },
      { id: 'M49-capex-budget', en: 'Capex vs Budget', bn: 'ক্যাপেক্স বনাম বাজেট', t: 'r' }
    ]},
    { en: 'Register', screens: [
      { id: 'M49-register', en: 'Asset Register', bn: 'সম্পদ রেজিস্টার', t: 'g' },
      { id: 'M49-cwip', en: 'CWIP Tracking', bn: 'সিডব্লিউআইপি', t: 'g' },
      { id: 'M49-transfer', en: 'Transfers & Custodians', bn: 'স্থানান্তর', t: 'g' },
      { id: 'M49-categories', en: 'Asset Categories', bn: 'সম্পদের শ্রেণি', t: 'g' }
    ]},
    { en: 'Depreciation', screens: [
      { id: 'M49-dep', en: 'Dual-Book Depreciation', bn: 'দ্বৈত অবচয়', t: 'c' },
      { id: 'M49-dualbook', en: 'Book vs Tax Depreciation', bn: 'হিসাব বনাম কর অবচয়', t: 'r' },
      { id: 'M49-schedules', en: 'Schedules & Movements', bn: 'সূচি', t: 'r' },
      { id: 'M49-nbv', en: 'NBV by Category', bn: 'শ্রেণিভিত্তিক নিট মূল্য', t: 'r' },
      { id: 'M49-taxrates', en: 'Tax Depreciation Rates', bn: 'কর অবচয়ের হার', t: 'g' }
    ]},
    { en: 'Lifecycle', screens: [
      { id: 'M49-impairment', en: 'Revaluation & Impairment', bn: 'পুনর্মূল্যায়ন', t: 'g' },
      { id: 'M49-disposal', en: 'Disposal & Write-Off', bn: 'নিষ্পত্তি', t: 'g' },
      { id: 'M49-disposal-gl', en: 'Disposal Gains/Losses', bn: 'নিষ্পত্তির লাভ/ক্ষতি', t: 'r' },
      { id: 'M49-verify', en: 'Physical Verification', bn: 'শারীরিক যাচাই', t: 'c' },
      { id: 'M49-verify-results', en: 'Verification Results', bn: 'যাচাইয়ের ফলাফল', t: 'g' }
    ]},
    { en: 'Leases (IFRS 16)', screens: [
      { id: 'M49-leases', en: 'Lease Contracts', bn: 'ইজারা চুক্তি', t: 'g' },
      { id: 'M49-lease-schedule', en: 'Lease Schedules', bn: 'ইজারা সূচি', t: 'g' },
      { id: 'M49-lease-summary', en: 'Lease Summary', bn: 'ইজারা সারসংক্ষেপ', t: 'r' }
    ]}
  ],
  reports: ['Fixed Asset Movement Schedule', 'Depreciation (Dual Book)', 'NBV by Category', 'Capex vs Budget', 'Disposal Gains/Losses', 'IFRS 16 Lease Summary'],
  forms: ['Capex Request', 'Asset Capitalisation', 'Transfer', 'Disposal', 'Revaluation / Impairment', 'Lease Contract'],
  cross: ['Financial Accounting & GL', 'Enterprise Assets & Test Equipment', 'Fleet & Vehicles'],
  freg: { src: 66, sub: [
    ['1', 'Capex & Approval', 9], ['2', 'Register & Capitalisation', 11], ['3', 'Componentisation', 5],
    ['4', 'Dual-Book Depreciation', 12], ['5', 'Revaluation & Impairment', 7], ['6', 'Transfers & Custody', 6],
    ['7', 'Verification & Tagging', 7], ['8', 'Disposal', 9]
  ] }
};

/* in-workspace data screens (checked before any stock Odoo view) */
export const SCREENS = {
  // Capex
  'M49-requests': { kind: 'model_list', model: 'fix.capex.request',
    cols: ['name','title','request_date','operating_unit_id','budget_id','amount','requested_by_id','state'],
    stateField: 'state', actions: [{m:'action_submit',l:'Submit'},{m:'action_approve',l:'Approve'},
      {m:'action_reject',l:'Reject'},{m:'action_create_cwip',l:'Open CWIP Project'}] },
  'M49-budget': { kind: 'model_list', model: 'fix.capex.budget',
    cols: ['name','fiscal_year','date_from','date_to','operating_unit_id','amount','committed_amount','actual_amount','available_amount','state'],
    stateField: 'state', actions: [{m:'action_approve',l:'Approve'},{m:'action_close',l:'Close'}] },
  'M49-capex-budget': { kind: 'table_report', module: 'M49', report: 'capex_vs_budget' },
  // Register
  'M49-register': { kind: 'model_list', model: 'fix.fixed.asset',
    cols: ['code','name','category','operating_unit_id','custodian_id','purchase_date','gross','monthly_depreciation','book_nbv','state'],
    stateField: 'state', actions: [{m:'action_activate',l:'Put into Service'},{m:'action_accrue_month',l:'Accrue Month'},{m:'action_dispose',l:'Dispose'}] },
  'M49-cwip': { kind: 'model_list', model: 'fix.cwip.entry',
    cols: ['name','capex_request_id','category_id','operating_unit_id','amount','state','asset_id'],
    stateField: 'state', actions: [{m:'action_capitalise',l:'Capitalise'}] },
  'M49-transfer': { kind: 'model_list', model: 'fix.asset.transfer',
    cols: ['name','asset_id','date','from_operating_unit_id','operating_unit_id','from_custodian_id','to_custodian_id','state'],
    stateField: 'state', actions: [{m:'action_confirm',l:'Confirm Transfer'},{m:'action_cancel',l:'Cancel'}] },
  'M49-categories': { kind: 'model_list', model: 'fix.asset.category',
    cols: ['code','name','useful_life_months','salvage_percent','tax_rate_code','journal_id','asset_account_id','expense_account_id'] },
  // Depreciation
  'M49-dep': { kind: 'model_list', model: 'fix.asset.depreciation.run',
    cols: ['name','book','period_start','operating_unit_id','asset_count','total_amount','state'],
    stateField: 'state', actions: [{m:'action_compute',l:'Compute'},{m:'action_post',l:'Post'}] },
  'M49-dualbook': { kind: 'table_report', module: 'M49', report: 'dual_book' },
  'M49-schedules': { kind: 'table_report', module: 'M49', report: 'movement_schedule' },
  'M49-nbv': { kind: 'table_report', module: 'M49', report: 'nbv_by_category' },
  'M49-taxrates': { kind: 'model_list', model: 'fix.asset.tax.rate',
    cols: ['code','name','rate_percent','date_from','date_to','legal_reference','verified'] },
  // Lifecycle
  'M49-impairment': { kind: 'model_list', model: 'fix.asset.revaluation',
    cols: ['name','asset_id','kind','date','new_value','carrying_amount','surplus_amount','pl_amount','state'],
    stateField: 'state', actions: [{m:'action_post',l:'Approve & Post'},{m:'action_cancel',l:'Cancel'}] },
  'M49-disposal': { kind: 'model_list', model: 'fix.asset.disposal',
    cols: ['name','asset_id','kind','date','proceeds','nbv','gain_loss','state'],
    stateField: 'state', actions: [{m:'action_approve',l:'Approve'},{m:'action_post',l:'Post'},{m:'action_cancel',l:'Cancel'}] },
  'M49-disposal-gl': { kind: 'table_report', module: 'M49', report: 'disposal_gains' },
  'M49-verify': { kind: 'model_list', model: 'fix.asset.verification.campaign',
    cols: ['name','date','operating_unit_id','expected_count','found_count','misplaced_count','missing_count','unregistered_count','state'],
    stateField: 'state', actions: [{m:'action_start',l:'Start Count'},{m:'action_close',l:'Close Campaign'}] },
  'M49-verify-results': { kind: 'model_list', model: 'fix.asset.verification.line',
    cols: ['campaign_id','asset_id','asset_code','operating_unit_id','scanned_tag','scanned_operating_unit_id','result'],
    stateField: 'result', create: false,
    actions: [{m:'action_mark_found',l:'Mark Found'},{m:'action_mark_missing',l:'Mark Missing'}] },
  // Leases (IFRS 16)
  'M49-leases': { kind: 'model_list', model: 'fix.lease',
    cols: ['reference','name','operating_unit_id','commencement_date','term_months','payment_amount','ibr_percent','liability_balance','state'],
    stateField: 'state', actions: [{m:'action_activate',l:'Activate (Commence)'},{m:'action_post_due',l:'Post Due Months'}] },
  'M49-lease-schedule': { kind: 'model_list', model: 'fix.lease.schedule.line',
    cols: ['lease_id','sequence','period_start','opening','payment','interest','principal','closing','depreciation','state'],
    stateField: 'state', create: false, actions: [{m:'action_post',l:'Post Month'}] },
  'M49-lease-summary': { kind: 'table_report', module: 'M49', report: 'lease_summary' },
};

/* built-in report chips -> the screen that shows that report */
export const REPORT_ROUTES = {
  "M49:Fixed Asset Movement Schedule": "M49-schedules",
  "M49:Depreciation (Dual Book)": "M49-dualbook",
  "M49:NBV by Category": "M49-nbv",
  "M49:Capex vs Budget": "M49-capex-budget",
  "M49:Disposal Gains/Losses": "M49-disposal-gl",
  "M49:IFRS 16 Lease Summary": "M49-lease-summary",
};

/* data-entry form chips -> real model forms */
export const FORM_MODELS = {
  'M49:Capex Request': 'fix.capex.request',
  'M49:Asset Capitalisation': 'fix.fixed.asset',
  'M49:Transfer': 'fix.asset.transfer',
  'M49:Disposal': 'fix.asset.disposal',
  'M49:Revaluation / Impairment': 'fix.asset.revaluation',
  'M49:Lease Contract': 'fix.lease',
};

/* the module's "+ New" surface */
export const CREATE = {
  M49: { model: 'fix.fixed.asset', label: 'Fixed Asset' },
};
