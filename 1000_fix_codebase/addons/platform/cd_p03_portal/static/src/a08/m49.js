/** @odoo-module **/
/* A08 · Finance & Treasury — M49 Fixed Assets & Capex.
 * One file per A08 module (merged into P03_MODULES and the screen maps by
 * p03_modules_meta.js): the registry entry, the in-workspace data screens,
 * built-in report routes, data-entry form chips and the "+ New" surface. */

export const MODULE = {
  area: 'A08', code: 'M49', en: 'Fixed Assets & Capex', title: 'M49 · Fixed Assets & Capex',
  bn: 'স্থায়ী সম্পদ ও ক্যাপেক্স', icon: '🏗️',
  desc: 'Capex requests to retirement — CWIP, dual-book depreciation (accounting + tax Third Schedule), verification.',
  kpis: [
    { l: 'Gross Block', m: 'assets_gross_block' },
    { l: 'CWIP', m: 'cwip_open_count' },
    { l: 'NBV' },
    { l: 'Depreciation Run' }
  ],
  groups: [
    { en: 'Capex', screens: [
      { id: 'M49-requests', en: 'Capex Requests', bn: 'ক্যাপেক্স অনুরোধ', t: 'g' },
      { id: 'M49-budget', en: 'Capital Budget', bn: 'মূলধনী বাজেট', t: 'g' }
    ]},
    { en: 'Register', screens: [
      { id: 'M49-register', en: 'Asset Register', bn: 'সম্পদ রেজিস্টার', t: 'g' },
      { id: 'M49-cwip', en: 'CWIP Tracking', bn: 'সিডব্লিউআইপি', t: 'g' },
      { id: 'M49-transfer', en: 'Transfers & Custodians', bn: 'স্থানান্তর', t: 'g' }
    ]},
    { en: 'Depreciation', screens: [
      { id: 'M49-dep', en: 'Dual-Book Depreciation', bn: 'দ্বৈত অবচয়', t: 'c' },
      { id: 'M49-schedules', en: 'Schedules & Movements', bn: 'সূচি', t: 'r' }
    ]},
    { en: 'Lifecycle', screens: [
      { id: 'M49-impairment', en: 'Revaluation & Impairment', bn: 'পুনর্মূল্যায়ন', t: 'g' },
      { id: 'M49-disposal', en: 'Disposal & Write-Off', bn: 'নিষ্পত্তি', t: 'g' },
      { id: 'M49-verify', en: 'Physical Verification', bn: 'শারীরিক যাচাই', t: 'c' }
    ]}
  ],
  reports: ['Fixed Asset Movement Schedule', 'Depreciation (Dual Book)', 'NBV by Category', 'Capex vs Budget', 'Disposal Gains/Losses'],
  forms: ['Capex Request', 'Asset Capitalisation', 'Transfer', 'Disposal'],
  cross: ['Financial Accounting & GL', 'Enterprise Assets & Test Equipment', 'Fleet & Vehicles'],
  freg: { src: 66, sub: [
    ['1', 'Capex & Approval', 9], ['2', 'Register & Capitalisation', 11], ['3', 'Componentisation', 5],
    ['4', 'Dual-Book Depreciation', 12], ['5', 'Revaluation & Impairment', 7], ['6', 'Transfers & Custody', 6],
    ['7', 'Verification & Tagging', 7], ['8', 'Disposal', 9]
  ] }
};

/* in-workspace data screens (checked before any stock Odoo view) */
export const SCREENS = {
  'M49-register': { kind: 'model_list', model: 'fix.fixed.asset',
    cols: ['name','category','gross','salvage','life_months','purchase_date','monthly_depreciation','state'],
    stateField: 'state', actions: [{m:'action_accrue_month',l:'Accrue Month'},{m:'action_dispose',l:'Dispose'}] },
  'M49-cwip': { kind: 'model_list', model: 'fix.cwip.entry',
    cols: ['name','amount','state','asset_id'],
    stateField: 'state', actions: [{m:'action_capitalise',l:'Capitalise'}] },
};

/* built-in report chips -> the screen that shows that report */
export const REPORT_ROUTES = {
  "M49:Fixed Asset Movement Schedule": "M49-register",
  "M49:Depreciation (Dual Book)": "M49-register",
  "M49:NBV by Category": "M49-register",
  "M49:Capex vs Budget": "M49-cwip",
  "M49:Disposal Gains/Losses": "M49-register",
};

/* data-entry form chips -> real model forms */
export const FORM_MODELS = {
  'M49:Asset Capitalisation': 'fix.fixed.asset',
};

/* the module's "+ New" surface */
export const CREATE = {
  M49: { model: 'fix.fixed.asset', label: 'Fixed Asset' },
};
