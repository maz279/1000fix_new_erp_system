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
    { l: 'Revenue Schedules', m: 'revenue_schedules_count' },
    { l: 'Escrow Held', m: 'escrow_held_amount' }
  ],
  groups: [
    { en: 'Revenue', screens: [
      { id: 'M53-obligations', en: 'Performance Obligations', bn: 'পারফরম্যান্স বাধ্যবাধকতা', t: 'g' },
      { id: 'M53-schedules', en: 'Revenue Schedules', bn: 'রাজস্ব সূচি', t: 'g' },
      { id: 'M53-schedules-held', en: 'Held Revenue Schedules (needs a decision)', bn: 'আটকে রাখা রাজস্ব সূচি', t: 'g' },
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
      { id: 'M53-ledger-unsourced', en: 'Commissions with No Source (needs a decision)', bn: 'উৎসবিহীন কমিশন', t: 'g' },
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
  forms: ['Revenue Schedule', 'Payout Run', 'Clawback', 'Commission Scheme', 'Performance Obligation', 'Subscription Contract', 'Payout Reconciliation'],
  cross: ['Subscriptions & Recurring', 'Marketplace & Sellers', 'Partner & Channel'],
  freg: { src: 74, sub: [
    ['1', 'Performance Obligations', 10, { model: 'fix.performance.obligation', cols: ['name', 'obligation_type', 'satisfaction', 'standalone_price', 'state'], screens: ['M53-obligations'] }],
    ['2', 'Allocation & SSP', 8, { model: 'fix.performance.obligation', cols: ['subscription_id', 'name', 'standalone_price', 'allocated_amount', 'state'], screens: ['M53-obligations', 'M53-contract'] }],
    ['3', 'Schedules & Triggers', 12, { model: 'fix.revenue.schedule', cols: ['description', 'total_amount', 'recognized_amount', 'deferred_balance', 'state'], screens: ['M53-schedules', 'M53-bridge'] }],
    ['4', 'Modifications & Reversals', 8, { model: 'fix.subscription', cols: ['name', 'customer_id', 'contract_value', 'last_refund_amount', 'state'], screens: ['M53-subscriptions'] }],
    ['5', 'Principal vs Agent', 5, { model: 'fix.commission.ledger', cols: ['name', 'seller_partner_id', 'gross_amount', 'commission_amount', 'state'], screens: ['M53-ledger'], domain: [['source_type', '=', 'marketplace']] }],
    ['6', 'Commission Ledger', 8, { model: 'fix.commission.ledger', cols: ['seller_partner_id', 'commission_amount', 'tds_amount', 'net_payable', 'state'], screens: ['M53-ledger', 'M53-schemes'] }],
    ['7', 'Seller Settlement', 10, { model: 'fix.seller.statement', cols: ['seller_partner_id', 'period', 'gross_gmv', 'net_payable', 'state'], screens: ['M53-sellers', 'M53-payouts', 'M53-recon'] }],
    ['8', 'Partner Payouts', 7, { model: 'fix.referral', cols: ['name', 'partner_id', 'referred_partner_id', 'commission_amount', 'state'], screens: ['M53-partners'], domain: [['state', 'in', ['converted', 'commissioned']]] }],
    ['9', 'Escrow & Clawbacks', 6, { model: 'fix.settlement.adjustment', cols: ['adjustment_type', 'seller_partner_id', 'amount', 'remaining_amount', 'state'], screens: ['M53-escrow'] }]
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
    stateField: 'state', actions: [{m:'action_recognize_period',l:'Recognise to Today (posts GL)'},
      {m:'action_request_cfo_approval',l:'Request CFO Approval (manual schedule)'}] },
  /* M53-6: schedules with no contract and no CFO approval post nothing; a person
   * cancels them, or reopens them as a manual schedule for the CFO. */
  'M53-schedules-held': { kind: 'model_list', model: 'fix.revenue.schedule', create: false,
    domain: [['state', '=', 'held']],
    cols: ['source_model','source_id','description','total_amount','recognized_amount','start_date','end_date','hold_reason','state'],
    stateField: 'state', actions: [{m:'action_cancel_held',l:'Cancel (no contract)',ask:'Why this schedule is cancelled',kwarg:'reason'},
      {m:'action_reopen_as_manual',l:'Reopen as Manual Schedule (for the CFO)'}] },
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
      {m:'action_generate_revrec_schedule',l:'Generate Revenue Schedule'},
      {m:'action_request_contract_value',l:'Request Transaction Price',asks:[{label:'Transaction price (BDT, VAT excluded)',kwarg:'contract_value',number:true},{label:'Where it comes from (the contract)',kwarg:'reason'}]},
      {m:'action_approve_contract_value',l:'Approve Transaction Price (second person)'},
      {m:'action_request_refund',l:'Cancel & Refund'}] },
  // Commission
  'M53-ledger': { kind: 'model_list', model: 'fix.commission.ledger',
    cols: ['name','seller_partner_id','source_type','gross_amount','commission_amount','tds_amount','net_payable','escrow_hold','state'],
    stateField: 'state', actions: [{m:'action_post_to_gl',l:'Post Accrual to GL'}] },
  /* M53-4: an earned row with no order or referral never accrues; this is its exit. */
  'M53-ledger-unsourced': { kind: 'model_list', model: 'fix.commission.ledger', create: false,
    domain: [['state','=','earned'],['marketplace_order_id','=',false],['referral_id','=',false]],
    cols: ['name','seller_partner_id','source_type','gross_amount','commission_amount','create_date','state'],
    stateField: 'state',
    actions: [{m:'action_link_source',l:'Link to its Order / Referral',ask:'Marketplace order or referral number',kwarg:'source_ref'},
      {m:'action_void_unsourced',l:'Void (Accounting Administrator)',ask:'Why this row is voided',kwarg:'reason'},
      {m:'action_void_all_unsourced',l:'Void All with No Source (Accounting Administrator)',ask:'Why every source-less row of this company is voided',kwarg:'reason'}] },
  'M53-schemes': { kind: 'model_list', model: 'fix.commission.scheme',
    cols: ['name','scheme_type','partner_type','seller_tier','commission_rate','tds_rate','date_from','date_to'] },
  // Settlements
  'M53-payouts': { kind: 'model_list', model: 'fix.payout.run',
    cols: ['name','period','total_gross','total_tds','total_clawback','total_payable','seller_count','rail_status','state'],
    stateField: 'state',
    // A08 F2: approval comes from the M63 inbox; money moves only as M50
    // payment instructions, confirmed by treasury from the bank statement.
    actions: [{m:'action_collect_accrued',l:'Collect Accrued Commissions'},
      {m:'action_prepare',l:'Prepare & Request Approval'},
      {m:'action_request_payments',l:'Release to Treasury (M50)'},
      {m:'action_query_status',l:'Refresh Payment Status'},
      {m:'action_rerequest_unpaid',l:'Re-request Rejected Payments'},
      {m:'action_drop_unpaid',l:'Drop Unpaid Payees (Accounting Administrator)',ask:'Why these payees leave the run',kwarg:'reason'},
      {m:'action_open_reconciliation',l:'Reconcile to Bank'},
      {m:'action_cancel',l:'Cancel'}] },
  'M53-sellers': { kind: 'model_list', model: 'fix.seller.statement',
    cols: ['name','seller_partner_id','period','gross_gmv','commission_amount','tds_withheld','clawback_amount','net_payable','withholding_cert_ref','tds_challan_id','state'],
    stateField: 'state',
    actions: [{m:'action_issue_statement',l:'Issue Statement'},{m:'action_settle_statement',l:'Mark Settled'},
      {m:'action_attach_challan',l:'Attach TDS Challan (issues the certificate)',ask:'Deposited, verified TDS challan number',kwarg:'challan_no'}] },
  'M53-partners': { kind: 'model_list', model: 'fix.referral',
    cols: ['name','partner_id','referred_partner_id','base_amount','commission_amount','state','commission_ledger_id','payout_state'],
    stateField: 'state', domain: [['state','in',['submitted','converted','commissioned']]], create: false,
    /* Convert: the Referral Manager (cd_partner.group_fix_referral_manager). */
    actions: [{m:'action_convert',l:'Convert from Paid Invoice',ask:'The referred customer\'s paid invoice number (empty = the one picked on the form)',kwarg:'invoice'},
      {m:'action_earn_commission',l:'Earn Commission'},
      {m:'action_accrue_commission',l:'Accrue Commission (GL)'}] },
  'M53-escrow': { kind: 'model_list', model: 'fix.settlement.adjustment',
    cols: ['name','adjustment_type','seller_partner_id','dispute_id','amount','remaining_amount','state'],
    stateField: 'state',
    actions: [{m:'action_activate',l:'Activate'},{m:'action_release',l:'Release Escrow'},
      {m:'action_forfeit',l:'Forfeit (refund customer)'},{m:'action_cancel',l:'Cancel'}] },
  'M53-recon': { kind: 'model_list', model: 'fix.payout.reconciliation',
    cols: ['name','payout_run_id','reconciliation_date','system_count','rail_count','system_amount','rail_amount','unmatched_amount','state'],
    stateField: 'state', actions: [{m:'action_run_reconciliation',l:'Run Reconciliation'},
      {m:'action_investigate',l:'Investigate Break',ask:'What is being checked',kwarg:'note'},
      {m:'action_resolve_break',l:'Resolve Break (Accounting Administrator)',ask:'What explains the break',kwarg:'note'}] },


  /* ===== A08 master-data forms (D365 in-workspace) ===== */
  'M53-form-obligation': {
    kind: 'model_form',
    model: 'fix.performance.obligation',
    title: "Performance Obligation",
    back: 'M53-obligations',
    status: { field: 'state', labels: { draft: "Draft", active: "Active", fulfilled: "Fulfilled" } },
    sections: [
      { title: "Obligation",
        note: "One distinct promise inside a subscription; the standalone price decides how the contract value is allocated across obligations.",
        fields: [
          { name: 'subscription_id', required: true, label: "Subscription" },
          { name: 'name', required: true, label: "Obligation" },
          { name: 'obligation_type', required: true, label: "Type" },
          { name: 'satisfaction', required: true, label: "Satisfaction Method" },
          { name: 'standalone_price', required: true, label: "Standalone Price" },
          { name: 'allocated_amount', readonly: true, label: "Allocated Amount (price allocation)" },
          { name: 'start_date', label: "Start" },
          { name: 'end_date', label: "End" },
          { name: 'state', readonly: true, label: "State" }
        ] }
    ]
  },
  'M53-form-provision': {
    kind: 'model_form',
    model: 'fix.warranty.provision',
    title: "Warranty Provision",
    back: 'M53-warranty',
    status: { field: 'state', labels: { draft: "Draft", computed: "Computed", posted: "Posted" } },
    sections: [
      { title: "Provision",
        note: "Required balance = revenue in warranty x measured rework rate x cost ratio over the lookback window. Opening balance and movement are recorded, not typed.",
        fields: [
          { name: 'period', required: true, label: "Period (YYYY-MM)" },
          { name: 'period_end', readonly: true, label: "Period End" },
          { name: 'policy_id', readonly: true, label: "Policy (computed)" },
          { name: 'cost_ratio', readonly: true, label: "Cost Ratio (computed)" },
          { name: 'opening_balance', readonly: true, label: "Opening Balance (computed)" },
          { name: 'state', readonly: true, label: "State" }
        ] },
      { title: "Note",
        fields: [
          { name: 'note', type: 'text', readonly: true, label: "Note (from the computation)" }
        ] }
    ]
  },
  'M53-form-policy': {
    kind: 'model_form',
    model: 'fix.warranty.provision.policy',
    title: "Warranty Policy",
    back: 'M53-warranty-policy',
    sections: [
      { title: "Policy",
        note: "The policy fixes the warranty window, the lookback months and the cost ratio the provision engine applies.",
        fields: [
          { name: 'name', required: true, label: "Policy Name" },
          { name: 'warranty_days', required: true, label: "Warranty Days" },
          { name: 'lookback_months', required: true, label: "Lookback (months)" },
          { name: 'cost_ratio', required: true, label: "Cost Ratio" },
          { name: 'date_from', required: true, label: "From" },
          { name: 'date_to', label: "To" },
          { name: 'active', label: "Active" }
        ] }
    ]
  },
  'M53-form-subscription': {
    kind: 'model_form',
    model: 'fix.subscription',
    title: "Subscription",
    back: 'M53-subscriptions',
    status: { field: 'state', labels: { draft: "Draft", active: "Active", suspended: "Suspended", closed: "Closed" } },
    sections: [
      { title: "Subscription",
        note: "A recurring contract: plan, billing cycle, amount and the next invoice date. The state, dunning ladder and refund figures change only through the lifecycle actions; a mid-term price or plan change goes through an approved proration.",
        fields: [
          { name: 'name', required: true, label: "Subscription" },
          { name: 'customer_id', required: true, label: "Customer" },
          { name: 'contract_id', label: "Contract" },
          { name: 'plan', required: true, label: "Plan" },
          { name: 'billing_cycle', required: true, label: "Billing Cycle" },
          { name: 'recurring_amount', required: true, label: "Recurring Amount" },
          { name: 'start_date', required: true, label: "Start Date" },
          { name: 'next_invoice_date', required: true, label: "Next Invoice" },
          { name: 'grace_period_days', label: "Grace Period (days)" },
          { name: 'consolidated', label: "Consolidated Billing" },
          { name: 'contract_value', label: "Transaction Price (at creation; then Request Transaction Price)" },
          { name: 'contract_end_date', label: "Contract End" },
          { name: 'pending_contract_value', readonly: true, label: "Requested Transaction Price" },
          { name: 'state', readonly: true, label: "State" }
        ] }
    ]
  },
  'M53-form-ledger': {
    kind: 'model_form',
    model: 'fix.commission.ledger',
    title: "Commission Ledger",
    back: 'M53-ledger',
    status: { field: 'state', labels: { draft: "Draft", approved: "Approved", paid: "Paid" } },
    sections: [
      { title: "Commission",
        note: "One commission earning per seller and source. Commission amount and TDS are computed from the gross and the scheme rate.",
        fields: [
          { name: 'seller_partner_id', readonly: true, label: "Seller" },
          { name: 'name', readonly: true, label: "Reference" },
          { name: 'source_type', readonly: true, label: "Source Type" },
          { name: 'source_ref', readonly: true, label: "Source Reference" },
          { name: 'gross_amount', readonly: true, label: "Gross Amount" },
          { name: 'commission_rate', readonly: true, label: "Commission Rate (scheme)" },
          { name: 'tds_amount', readonly: true, label: "TDS (scheme + PSR)" },
          { name: 'psr_verified', readonly: true, label: "PSR on File (M52 tax profile)" },
          { name: 'escrow_hold', readonly: true, label: "Escrow Hold" },
          { name: 'state', readonly: true, label: "State" }
        ] }
    ]
  },
  'M53-form-statement': {
    kind: 'model_form',
    model: 'fix.seller.statement',
    title: "Seller Statement",
    back: 'M53-sellers',
    status: { field: 'state', labels: { draft: "Draft", issued: "Issued", settled: "Settled" } },
    sections: [
      { title: "Statement",
        note: "A period statement for one seller. GMV, commission, TDS and the net payable are computed; the withholding certificate reference is required by statute.",
        fields: [
          { name: 'seller_partner_id', required: true, label: "Seller" },
          { name: 'name', readonly: true, label: "Statement" },
          { name: 'period', required: true, label: "Period (YYYY-MM)" },
          { name: 'date_issued', readonly: true, label: "Issued On" },
          { name: 'gross_gmv', required: true, label: "Gross GMV" },
          { name: 'commission_amount', required: true, label: "Commission" },
          { name: 'tds_withheld', required: true, label: "TDS Withheld" },
          { name: 'platform_fee', label: "Platform Fee" },
          { name: 'clawback_amount', label: "Clawback" },
          { name: 'net_payable', readonly: true, label: "Net Payable (computed)" },
          { name: 'withholding_cert_ref', readonly: true, label: "Withholding Certificate (on the TDS challan)" },
          { name: 'tds_challan_id', readonly: true, label: "TDS Challan" },
          { name: 'state', readonly: true, label: "State" }
        ] }
    ]
  },

};

/* built-in report chips -> the screen that shows that report */
export const REPORT_ROUTES = {
  "M53:Deferred Revenue Bridge": "M53-bridge",
  "M53:Rev-Rec by Stream": "M53-rpt-streams",
  "M53:Contract Assets & Liabilities": "M53-contract",
  "M53:Commission Accrual": "M53-rpt-comacc",
  "M53:Payout Reconciliation": "M53-rpt-payrecon",
  "M53:Clawback Register": "M53-rpt-clawback",
};

/* report screens (each chip opens its OWN computed pack) */
Object.assign(SCREENS, {
  'M53-rpt-streams': { kind: 'table_report', module: 'M53', report: 'rev_rec_by_stream', title: 'Revenue Recognition by Stream', period: false },
  'M53-rpt-comacc': { kind: 'table_report', module: 'M53', report: 'commission_accrual', title: 'Commission Accrual', period: false },
  'M53-rpt-payrecon': { kind: 'table_report', module: 'M53', report: 'payout_reconciliation', title: 'Payout Reconciliation', period: false },
  'M53-rpt-clawback': { kind: 'table_report', module: 'M53', report: 'clawback_register', title: 'Clawback & Escrow Register', period: false }
});

/* data-entry form chips -> real model forms (the registry's four) */
export const FORM_MODELS = {
  'M53:Revenue Schedule': 'fix.revenue.schedule',
  'M53:Payout Run': 'fix.payout.run',
  'M53:Clawback': 'fix.settlement.adjustment',
  'M53:Commission Scheme': 'fix.commission.scheme',
  'M53:Payout Reconciliation': 'fix.payout.reconciliation',
  'M53:Performance Obligation': 'fix.performance.obligation',
  'M53:Subscription Contract': 'fix.subscription',
};

/* ============ D365 IN-WORKSPACE FORM SCREENS (M53 re-audit v2) ======== */
Object.assign(SCREENS, {
  'M53-form-schedule': {
    kind: 'model_form',
    model: 'fix.revenue.schedule',
    title: 'Revenue Schedule',
    back: 'M53-schedules',
    sections: [
      { title: 'Schedule', note: 'The contracted amount is recognised over the schedule window; the recognised amount and deferred balance are maintained by the recognition engine. A manually created schedule names its contract, a reason and evidence, and recognises nothing until the CFO approves it through the M63 inbox (BRU-REV-01).',
        fields: [
          { name: 'description', required: true, label: 'Description' },
          { name: 'start_date', required: true, label: 'Start Date' },
          { name: 'end_date', required: true, label: 'End Date' },
          { name: 'total_amount', required: true, label: 'Contracted Amount' },
          { name: 'operating_unit_id', required: true, label: 'Operating Unit' },
          { name: 'contract_id', label: 'Contract (manual schedule)' },
          { name: 'subscription_id', label: 'Subscription Contract (manual schedule)' },
          { name: 'manual_reason', label: 'Reason (manual schedule)', type: 'text' },
          { name: 'evidence_ref', label: 'Evidence Reference' },
          { name: 'state', readonly: true, label: 'State' },
          { name: 'hold_reason', readonly: true, label: 'Why Held' },
          { name: 'recognized_amount', readonly: true, label: 'Recognised (posted lines)' }
        ] }
    ]
  },

  'M53-form-payoutrun': {
    kind: 'model_form',
    model: 'fix.payout.run',
    title: 'Payout Run',
    back: 'M53-payouts',
    status: { field: 'state', labels: {
      draft: 'Draft', prepared: 'Prepared — Awaiting Approval', approved: 'Approved (SoD Verified)',
      executing: 'Released to Treasury', file_generated: 'BEFTN File Generated (legacy)',
      executed: 'Executed', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Payout Run', note: 'The run aggregates the period\'s commission ledger into seller payouts with TDS withheld; it is prepared, approved from the M63 inbox, and paid only as M50 payment instructions that treasury releases and the bank statement confirms.',
        fields: [
          { name: 'period', required: true, label: 'Settlement Period (YYYY-MM)' },
          { name: 'state', readonly: true, label: 'State' }
        ] }
    ]
  },

  'M53-form-clawback': {
    kind: 'model_form',
    model: 'fix.settlement.adjustment',
    title: 'Clawback / Escrow',
    back: 'M53-escrow',
    status: { field: 'state', labels: {
      draft: 'Draft', active: 'Held / Open', released: 'Released to Payee',
      forfeited: 'Forfeited (refunded)', recovered: 'Recovered', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Adjustment', note: 'An escrow hold freezes the listed commissions while a dispute is open (a raised dispute holds its own order\'s commissions automatically; the amount is what they would pay). A clawback recovers a stated amount from future payouts.',
        fields: [
          { name: 'adjustment_type', required: true, label: 'Type' },
          { name: 'seller_partner_id', required: true, label: 'Seller / Partner' },
          { name: 'dispute_id', label: 'Marketplace Dispute (escrow)' },
          { name: 'commission_ids', label: 'Commissions to Hold (escrow)' },
          { name: 'amount', label: 'Amount (clawback; an escrow computes it)' },
          { name: 'reason', required: true, type: 'text', label: 'Reason' },
          { name: 'requested_by_id', readonly: true, label: 'Requested By' },
          { name: 'decided_by_id', readonly: true, label: 'Decided By' },
          { name: 'state', readonly: true, label: 'State' }
        ] }
    ]
  },

  /* M53-4: pick the referred customer's paid invoice, then Convert. */
  'M53-form-referral': {
    kind: 'model_form',
    model: 'fix.referral',
    title: 'Partner Referral',
    back: 'M53-partners',
    status: { field: 'state', labels: { submitted: 'Submitted', converted: 'Converted', commissioned: 'Commissioned' } },
    sections: [
      { title: 'Conversion', note: 'A referral converts on the referred customer\'s PAID invoice: the base is read from it, never typed. Converting needs the Referral Manager; finance then earns and accrues the commission.',
        fields: [
          { name: 'name', readonly: true, label: 'Referral' },
          { name: 'partner_id', readonly: true, label: 'Referring Partner' },
          { name: 'referred_partner_id', readonly: true, label: 'Referred Customer' },
          { name: 'convert_invoice_id', label: 'Paid Invoice to Convert From' },
          { name: 'invoice_id', readonly: true, label: 'Invoice Converted From' },
          { name: 'base_amount', readonly: true, label: 'Referred Revenue (from the invoice)' },
          { name: 'commission_amount', readonly: true, label: 'Commission Earned' },
          { name: 'commission_ledger_id', readonly: true, label: 'Commission Ledger Entry' },
          { name: 'state', readonly: true, label: 'State' }
        ] }
    ]
  },

  /* M53-14: reconcile a released run to what the bank statement confirmed. */
  'M53-form-recon': {
    kind: 'model_form',
    model: 'fix.payout.reconciliation',
    title: 'Payout Reconciliation',
    back: 'M53-recon',
    status: { field: 'state', labels: { draft: 'Not Run', balanced: 'Balanced', break_detected: 'Break Detected', investigating: 'Investigating', resolved: 'Resolved' } },
    tabs: [
      { id: 'run', label: 'Run', bn: 'চালনা' },
      { id: 'figures', label: 'Figures', bn: 'অঙ্ক' }
    ],
    sections: [
      { tab: 'run', title: 'Reconciliation', note: 'Pick the payout run, save, then Run Reconciliation: the disbursed side is read from the M50 instructions the bank statement confirmed, never typed. A break is investigated and resolved by an Accounting Administrator who did not run it.',
        fields: [
          { name: 'payout_run_id', required: true, label: 'Payout Run' },
          { name: 'rail_name', readonly: true, label: 'Rail' },
          { name: 'reconciliation_date', label: 'Reconciliation Date' },
          { name: 'state', readonly: true, label: 'State' },
          { name: 'break_notes', readonly: true, type: 'text', label: 'Break Notes' },
          { name: 'ran_by_id', readonly: true, label: 'Last Run By' },
          { name: 'resolved_by_id', readonly: true, label: 'Resolved By' }
        ] },
      { tab: 'figures', title: 'Count and Amount', note: 'Compared separately (FF-94).',
        fields: [
          { name: 'system_count', readonly: true, label: 'System Payees' },
          { name: 'rail_count', readonly: true, label: 'Bank-Confirmed Payees' },
          { name: 'count_matched', readonly: true, label: 'Counts Match' },
          { name: 'system_amount', readonly: true, label: 'System Amount' },
          { name: 'rail_amount', readonly: true, label: 'Bank-Confirmed Amount' },
          { name: 'amount_matched', readonly: true, label: 'Amounts Match' },
          { name: 'unmatched_count', readonly: true, label: 'Unmatched Payees' },
          { name: 'unmatched_amount', readonly: true, label: 'Unmatched Amount' },
          { name: 'aged_unmatched_count', readonly: true, label: 'Unmatched Aged > 30 Days' }
        ] }
    ]
  },

  'M53-form-scheme': {
    kind: 'model_form',
    model: 'fix.commission.scheme',
    title: 'Commission Scheme',
    back: 'M53-schemes',
    sections: [
      { title: 'Scheme', note: 'Effective-dated commission rates by partner type and seller tier; the TDS rate withholds at source per ITA 2023.',
        fields: [
          { name: 'name', required: true, label: 'Scheme Name' },
          { name: 'scheme_type', required: true, label: 'Scheme Type' },
          { name: 'partner_type', required: true, label: 'Partner Type' },
          { name: 'seller_tier', label: 'Seller Tier (empty = all)' },
          { name: 'commission_rate', required: true, label: 'Commission Rate (0-1)' },
          { name: 'tds_rate', label: 'TDS Rate (0-1)' },
          { name: 'tds_base', label: 'TDS Base' },
          { name: 'date_from', required: true, label: 'Effective From' },
          { name: 'date_to', label: 'Effective To' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  }
});

export const FORM_CHIPS = {
  'M53:Performance Obligation': 'M53-form-obligation',
  'M53:Warranty Provision': 'M53-form-provision',
  'M53:Warranty Policy': 'M53-form-policy',
  'M53:Subscription': 'M53-form-subscription',
  'M53:Commission Ledger': 'M53-form-ledger',
  'M53:Seller Statement': 'M53-form-statement',
  'M53:Revenue Schedule': 'M53-form-schedule',
  'M53:Payout Run': 'M53-form-payoutrun',
  'M53:Clawback': 'M53-form-clawback',
  'M53:Commission Scheme': 'M53-form-scheme',
  'M53:Payout Reconciliation': 'M53-form-recon',
  'M53:__by_model__': {
    'fix.referral': 'M53-form-referral',
    'fix.payout.reconciliation': 'M53-form-recon',
    'fix.performance.obligation': 'M53-form-obligation',
    'fix.warranty.provision': 'M53-form-provision',
    'fix.warranty.provision.policy': 'M53-form-policy',
    'fix.subscription': 'M53-form-subscription',
    'fix.commission.ledger': 'M53-form-ledger',
    'fix.seller.statement': 'M53-form-statement',
    'fix.revenue.schedule': 'M53-form-schedule',
    'fix.payout.run': 'M53-form-payoutrun',
    'fix.settlement.adjustment': 'M53-form-clawback',
    'fix.commission.scheme': 'M53-form-scheme'
  },
  'M53:__by_screen__': {
    'M53-obligations': 'M53-form-obligation',
    'M53-warranty': 'M53-form-provision',
    'M53-warranty-policy': 'M53-form-policy',
    'M53-subscriptions': 'M53-form-subscription',
    'M53-ledger': 'M53-form-ledger',
    'M53-sellers': 'M53-form-statement',
    'M53-schedules': 'M53-form-schedule',
    'M53-payouts': 'M53-form-payoutrun',
    'M53-escrow': 'M53-form-clawback',
    'M53-schemes': 'M53-form-scheme',
    'M53-partners': 'M53-form-referral',
    'M53-recon': 'M53-form-recon',
    'M53-schedules-held': 'M53-form-schedule'
  }
};

/* the module's "+ New" surface */
export const CREATE = {
  M53: { model: 'fix.payout.run', label: 'Payout Run' },
};
