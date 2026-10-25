/** @odoo-module **/
/* A08 · Finance & Treasury — M53 Revenue Recognition & Settlement.
 * One file per A08 module (merged into P03_MODULES and the screen maps by
 * p03_modules_meta.js): the registry entry, the in-workspace data screens,
 * built-in report routes, data-entry form chips and the "+ New" surface. */

export const MODULE = {
  area: 'A08', code: 'M53', en: 'Revenue Recognition & Settlement', title: 'M53 · Revenue Recognition & Settlement',
  bn: 'রাজস্ব ও নিষ্পত্তি', icon: '📊',
  desc: 'Performance obligations, contract balances, commission ledger, seller/partner payouts, clawbacks, escrow.',
  kpis: [
    { l: 'Commission Accrued', m: 'commission_accrued_count' },
    { l: 'Payout Runs MTD', m: 'payout_runs_open' },
    { l: 'Deferred Revenue', m: 'revenue_schedules_count' },
    { l: 'Recognised MTD' }
  ],
  groups: [
    { en: 'Revenue', screens: [
      { id: 'M53-obligations', en: 'Performance Obligations', bn: 'পারফরম্যান্স বাধ্যবাধকতা', t: 'g' },
      { id: 'M53-schedules', en: 'Revenue Schedules', bn: 'রাজস্ব সূচি', t: 'g' },
      { id: 'M53-contract', en: 'Contract Assets & Liabilities', bn: 'চুক্তি সম্পদ', t: 'r' }
    ]},
    { en: 'Commission', screens: [
      { id: 'M53-ledger', en: 'Commission Ledger', bn: 'কমিশন লেজার', t: 'g' },
      { id: 'M53-schemes', en: 'Incentive Schemes', bn: 'প্রণোদনা কর্মসূচি', t: 'g' }
    ]},
    { en: 'Settlements', screens: [
      { id: 'M53-payouts', en: 'Payout Runs', bn: 'পেআউট রান', t: 'c' },
      { id: 'M53-sellers', en: 'Seller Statements', bn: 'বিক্রেতা বিবৃতি', t: 'r' },
      { id: 'M53-partners', en: 'Partner / Referral Payouts', bn: 'পার্টনার পেআউট', t: 'g' },
      { id: 'M53-escrow', en: 'Escrow & Clawbacks', bn: 'এসক্রো', t: 'g' }
    ]}
  ],
  reports: ['Deferred Revenue Bridge', 'Rev-Rec by Stream', 'Commission Accrual', 'Payout Reconciliation', 'Clawback Register'],
  forms: ['Revenue Schedule', 'Payout Run', 'Clawback', 'Commission Scheme'],
  cross: ['Subscriptions & Recurring', 'Marketplace & Sellers', 'Partner & Channel'],
  freg: { src: 74, sub: [
    ['1', 'Performance Obligations', 10], ['2', 'Allocation & SSP', 8], ['3', 'Schedules & Triggers', 12],
    ['4', 'Modifications & Reversals', 8], ['5', 'Principal vs Agent', 5], ['6', 'Commission Ledger', 8],
    ['7', 'Seller Settlement', 10], ['8', 'Partner Payouts', 7], ['9', 'Escrow & Clawbacks', 6]
  ] }
};

/* in-workspace data screens (checked before any stock Odoo view) */
export const SCREENS = {
  'M53-schedules': { kind: 'model_list', model: 'fix.revenue.schedule',
    cols: ['source_model','description','total_amount','recognized_amount','start_date','end_date','state'],
    stateField: 'state' },
  'M53-ledger': { kind: 'model_list', model: 'fix.commission.ledger',
    cols: ['name','seller_partner_id','gross_amount','commission_amount','tds_amount','net_payable','state'],
    stateField: 'state', actions: [{m:'action_post_to_gl',l:'Post Accrual to GL'}] },
  'M53-payouts': { kind: 'model_list', model: 'fix.payout.run',
    cols: ['name','period','total_gross','total_tds','total_payable','seller_count','state'],
    stateField: 'state', actions: [{m:'action_approve',l:'Approve (SoD)'},{m:'action_generate_beftn',l:'Generate BEFTN File'}] },
  'M53-sellers': { kind: 'model_list', model: 'fix.seller.statement',
    cols: ['seller_partner_id','period','gross_gmv','commission_amount','tds_withheld','net_payable','state'],
    stateField: 'state' },
};

/* built-in report chips -> the screen that shows that report */
export const REPORT_ROUTES = {
  "M53:Commission Accrual": "M53-ledger",
  "M53:Payout Reconciliation": "M53-payouts",
  "M53:Deferred Revenue Bridge": "M53-schedules",
  "M53:Rev-Rec by Stream": "M53-schedules",
  "M53:Clawback Register": "M53-sellers",
};

/* data-entry form chips -> real model forms */
export const FORM_MODELS = {
  'M53:Revenue Schedule': 'fix.revenue.schedule',
  'M53:Payout Run': 'fix.payout.run',
};

/* the module's "+ New" surface */
export const CREATE = {
  M53: { model: 'fix.payout.run', label: 'Payout Run' },
};
