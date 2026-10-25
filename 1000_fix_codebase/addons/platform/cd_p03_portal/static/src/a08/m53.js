/** @odoo-module **/
/* A08 · Finance & Treasury — M53 Revenue Recognition & Settlement.
 * One file per A08 module (merged into P03_MODULES and the screen maps by
 * p03_modules_meta.js): the registry entry, the in-workspace data screens,
 * built-in report routes, data-entry form chips and the "+ New" surface.
 * Technician incentives are not settlement: they moved to Payroll (A09);
 * "Commission Schemes" are the seller / partner rate tables only. */

export const MODULE = {
  area: 'A08', code: 'M53', en: 'Revenue Recognition & Settlement', title: 'M53 · Revenue Recognition & Settlement',
  bn: 'রাজস্ব ও নিষ্পত্তি', icon: '📊',
  desc: 'IFRS 15 obligations and contract balances, AMC contracts, warranty provision, commission ledger, seller/partner payouts, escrow and clawbacks.',
  kpis: [
    { l: 'Commission Accrued', m: 'commission_accrued_count' },
    { l: 'Payout Runs Open', m: 'payout_runs_open' },
    { l: 'Deferred Revenue', m: 'deferred_revenue_balance' },
    { l: 'Recognised MTD', m: 'recognised_mtd' },
    { l: 'Escrow Held', m: 'escrow_held_amount' }
  ],
  groups: [
    { en: 'Revenue', screens: [
      { id: 'M53-obligations', en: 'Performance Obligations', bn: 'পারফরম্যান্স বাধ্যবাধকতা', t: 'g' },
      { id: 'M53-schedules', en: 'Revenue Schedules', bn: 'রাজস্ব সূচি', t: 'g' },
      { id: 'M53-contract', en: 'Contract Assets & Liabilities', bn: 'চুক্তি সম্পদ ও দায়', t: 'r' },
      { id: 'M53-bridge', en: 'Deferred Revenue Bridge', bn: 'বিলম্বিত রাজস্ব সমন্বয়', t: 'r' },
      { id: 'M53-warranty', en: 'Warranty Provision (IAS 37)', bn: 'ওয়ারেন্টি সঞ্চিতি (IAS 37)', t: 'g' },
      { id: 'M53-warranty-policy', en: 'Warranty Provision Policy', bn: 'ওয়ারেন্টি সঞ্চিতি নীতি', t: 'g' }
    ]},
    { en: 'Contracts', screens: [
      { id: 'M53-subscriptions', en: 'AMC & Subscription Contracts', bn: 'AMC ও সাবস্ক্রিপশন চুক্তি', t: 'g' }
    ]},
    { en: 'Commission', screens: [
      { id: 'M53-ledger', en: 'Commission Ledger', bn: 'কমিশন লেজার', t: 'g' },
      { id: 'M53-schemes', en: 'Commission Schemes', bn: 'কমিশন কর্মসূচি', t: 'g' }
    ]},
    { en: 'Settlements', screens: [
      { id: 'M53-payouts', en: 'Payout Runs', bn: 'পেআউট রান', t: 'c' },
      { id: 'M53-sellers', en: 'Seller Statements', bn: 'বিক্রেতা বিবৃতি', t: 'r' },
      { id: 'M53-partners', en: 'Partner / Referral Payouts', bn: 'পার্টনার পেআউট', t: 'g' },
      { id: 'M53-escrow', en: 'Escrow & Clawbacks', bn: 'এসক্রো ও ফেরত আদায়', t: 'g' },
      { id: 'M53-recon', en: 'Payout Reconciliation', bn: 'পেআউট সমন্বয়', t: 'g' }
    ]}
  ],
  reports: ['Deferred Revenue Bridge', 'Rev-Rec by Stream', 'Contract Assets & Liabilities', 'Commission Accrual', 'Payout Reconciliation', 'Clawback Register'],
  forms: ['Revenue Schedule', 'Payout Run', 'Clawback', 'Commission Scheme', 'Performance Obligation', 'Subscription Contract'],
  cross: ['Subscriptions & Recurring', 'Marketplace & Sellers', 'Partner & Channel'],
  freg: { src: 74, sub: [
    ['1', 'Performance Obligations', 10], ['2', 'Allocation & SSP', 8], ['3', 'Schedules & Triggers', 12],
    ['4', 'Modifications & Reversals', 8], ['5', 'Principal vs Agent', 5], ['6', 'Commission Ledger', 8],
    ['7', 'Seller Settlement', 10], ['8', 'Partner Payouts', 7], ['9', 'Escrow & Clawbacks', 6]
  ] }
};

/* in-workspace data screens (checked before any stock Odoo view) */
export const SCREENS = {
  // Revenue (IFRS 15)
  'M53-obligations': { kind: 'model_list', model: 'fix.performance.obligation',
    cols: ['subscription_id','name','obligation_type','satisfaction','standalone_price','allocated_amount','recognized_amount','state'],
    stateField: 'state',
    actions: [{m:'action_create_schedule',l:'Create Revenue Schedule'},{m:'action_recognize',l:'Recognise to Today'}] },
  'M53-schedules': { kind: 'model_list', model: 'fix.revenue.schedule',
    cols: ['source_model','description','total_amount','recognized_amount','deferred_balance','start_date','end_date','state'],
    stateField: 'state', actions: [{m:'action_recognize_period',l:'Recognise to Today (posts GL)'}] },
  'M53-contract': { kind: 'table_report', module: 'M53', report: 'contract_balances' },
  'M53-bridge': { kind: 'table_report', module: 'M53', report: 'deferred_revenue_bridge' },
  'M53-warranty': { kind: 'model_list', model: 'fix.warranty.provision',
    cols: ['period','revenue_in_warranty','rework_rate','cost_ratio','required_balance','opening_balance','movement','state'],
    stateField: 'state', actions: [{m:'action_compute',l:'Compute'},{m:'action_post',l:'Post to GL (SoD)'}] },
  'M53-warranty-policy': { kind: 'model_list', model: 'fix.warranty.provision.policy',
    cols: ['name','warranty_days','lookback_months','cost_ratio','date_from','date_to'] },
  // Contracts
  'M53-subscriptions': { kind: 'model_list', model: 'fix.subscription',
    cols: ['name','customer_id','plan','billing_cycle','recurring_amount','contract_value','next_invoice_date','dunning_step','state'],
    stateField: 'state',
    actions: [{m:'action_generate_charge',l:'Generate Charge'},{m:'action_trigger_dunning',l:'Run Dunning'},
      {m:'action_reinstate',l:'Reinstate'},{m:'action_allocate_price',l:'Allocate Price (IFRS 15)'},
      {m:'action_request_refund',l:'Cancel & Refund'}] },
  // Commission
  'M53-ledger': { kind: 'model_list', model: 'fix.commission.ledger',
    cols: ['name','seller_partner_id','source_type','gross_amount','commission_amount','tds_amount','net_payable','escrow_hold','state'],
    stateField: 'state', actions: [{m:'action_post_to_gl',l:'Post Accrual to GL'}] },
  'M53-schemes': { kind: 'model_list', model: 'fix.commission.scheme',
    cols: ['name','scheme_type','partner_type','seller_tier','commission_rate','tds_rate','date_from','date_to'] },
  // Settlements
  'M53-payouts': { kind: 'model_list', model: 'fix.payout.run',
    cols: ['name','period','total_gross','total_tds','total_clawback','total_payable','seller_count','rail_status','state'],
    stateField: 'state',
    actions: [{m:'action_collect_accrued',l:'Collect Accrued Commissions'},{m:'action_approve',l:'Approve (SoD)'},
      {m:'action_submit_payout',l:'Disburse via API Rail'},{m:'action_generate_beftn',l:'Generate BEFTN File'},
      {m:'action_query_status',l:'Query Bank Status'},{m:'action_confirm_bank_settlement',l:'Confirm Bank Settlement'},
      {m:'action_post_payout_to_gl',l:'Post Payout to GL'}] },
  'M53-sellers': { kind: 'model_list', model: 'fix.seller.statement',
    cols: ['name','seller_partner_id','period','gross_gmv','commission_amount','tds_withheld','clawback_amount','net_payable','state'],
    stateField: 'state',
    actions: [{m:'action_issue_statement',l:'Issue Statement'},{m:'action_settle_statement',l:'Mark Settled'}] },
  'M53-partners': { kind: 'model_list', model: 'fix.referral',
    cols: ['name','partner_id','referred_partner_id','base_amount','commission_amount','state','commission_ledger_id','payout_state'],
    stateField: 'state', domain: [['state','in',['converted','commissioned']]], create: false,
    actions: [{m:'action_accrue_commission',l:'Accrue Commission (GL)'}] },
  'M53-escrow': { kind: 'model_list', model: 'fix.settlement.adjustment',
    cols: ['name','adjustment_type','seller_partner_id','dispute_id','amount','remaining_amount','state'],
    stateField: 'state',
    actions: [{m:'action_activate',l:'Activate'},{m:'action_release',l:'Release Escrow'},
      {m:'action_forfeit',l:'Forfeit (refund customer)'},{m:'action_cancel',l:'Cancel'}] },
  'M53-recon': { kind: 'model_list', model: 'fix.payout.reconciliation',
    cols: ['name','payout_run_id','reconciliation_date','system_count','rail_count','system_amount','rail_amount','unmatched_amount','state'],
    stateField: 'state', actions: [{m:'action_run_reconciliation',l:'Run Reconciliation'}] },
};

/* built-in report chips -> the screen that shows that report */
export const REPORT_ROUTES = {
  "M53:Deferred Revenue Bridge": "M53-bridge",
  "M53:Rev-Rec by Stream": "M53-bridge",
  "M53:Contract Assets & Liabilities": "M53-contract",
  "M53:Commission Accrual": "M53-ledger",
  "M53:Payout Reconciliation": "M53-recon",
  "M53:Clawback Register": "M53-escrow",
};

/* data-entry form chips -> real model forms */
export const FORM_MODELS = {
  'M53:Revenue Schedule': 'fix.revenue.schedule',
  'M53:Payout Run': 'fix.payout.run',
  'M53:Clawback': 'fix.settlement.adjustment',
  'M53:Commission Scheme': 'fix.commission.scheme',
  'M53:Performance Obligation': 'fix.performance.obligation',
  'M53:Subscription Contract': 'fix.subscription',
};

/* the module's "+ New" surface */
export const CREATE = {
  M53: { model: 'fix.payout.run', label: 'Payout Run' },
};
