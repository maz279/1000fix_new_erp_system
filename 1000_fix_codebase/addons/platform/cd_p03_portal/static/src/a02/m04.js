/** @odoo-module **/
/* A02 · Service Operations — M04 Branch & Front-Desk.
 * This fragment REPLACES the base-file M04 block, which described a
 * logistics module (manifests/transit/couriers — wrong content; registry
 * drift measured 2026-10-26: zero id overlap with the canonical registry).
 * The structure below is the CANONICAL registry M04: 5 groups, 15 screens,
 * 6 KPIs, 6 reports, freg 95 functions in 10 subs.
 *
 * Backend: controllers/a02/m04.py (SURFACES, kpis, 6 REPORTS) over the
 * cd_front_desk models — token queue, walk-in intake, cash shifts and the
 * new counter sales — plus the branch order book for custody views. */

export const MODULE = {
  area: 'A02', code: 'M04', en: 'Branch & Front-Desk', title: 'M04 · Branch & Front-Desk',
  bn: 'ব্রাঞ্চ ও ফ্রন্ট ডেস্ক', icon: '🏢',
  desc: 'Counter operations at 51+ centres — token queue, device custody, cash drawer, shift close, counter sales.',
  kpis: [
    { l: 'Tokens Today', m: 'tokens_today' },
    { l: 'Avg Wait', m: 'avg_wait_min' },
    { l: 'Uncollected > 7d', m: 'uncollected_7d' },
    { l: 'Cash Variance Today', m: 'cash_variance_today' },
    { l: 'Shifts Open', m: 'shifts_open' },
    { l: 'Counter Sales MTD', m: 'counter_sales_mtd' }
  ],
  groups: [
    { en: 'Queue & Token', screens: [
      { id: 'M04-queue', en: 'Token & Waiting Display', bn: 'টোকেন ও অপেক্ষার ডিসপ্লে', t: 'd' },
      { id: 'M04-counter', en: 'Counter Workstation', bn: 'কাউন্টার ওয়ার্কস্টেশন', t: 'c' },
      { id: 'M04-priority', en: 'Priority Queue Rules', bn: 'প্রায়োরিটি কিউ রুলস', t: 'g' }
    ]},
    { en: 'Device Custody', screens: [
      { id: 'M04-storage', en: 'Storage Locations', bn: 'স্টোরেজ অবস্থান', t: 'g' },
      { id: 'M04-handover', en: 'Collection & Handover', bn: 'সংগ্রহ ও হস্তান্তর', t: 'g' },
      { id: 'M04-uncollected', en: 'Uncollected Devices', bn: 'অসংগৃহীত ডিভাইস', t: 'g' }
    ]},
    { en: 'Cash & Shift', screens: [
      { id: 'M04-drawer', en: 'Cash Drawer', bn: 'ক্যাশ ড্রয়ার', t: 'g' },
      { id: 'M04-payments', en: 'Payment Capture (All Methods)', bn: 'পেমেন্ট গ্রহণ', t: 'g' },
      { id: 'M04-shift', en: 'Shift Open / Close', bn: 'শিফট খোলা/বন্ধ', t: 'c' },
      { id: 'M04-banking', en: 'Banking Deposits', bn: 'ব্যাংকিং ডিপোজিট', t: 'g' }
    ]},
    { en: 'Counter Sales', screens: [
      { id: 'M04-sales', en: 'Counter Sales (Parts/Plans)', bn: 'কাউন্টার বিক্রয়', t: 'g' },
      { id: 'M04-kiosk', en: 'Kiosk Mode', bn: 'কিয়স্ক মোড', t: 'd' }
    ]},
    { en: 'Branch Ops', screens: [
      { id: 'M04-checklists', en: 'Open/Close Checklists', bn: 'খোলা/বন্ধ চেকলিস্ট', t: 'g' },
      { id: 'M04-dashboard', en: 'Branch Ops Dashboard', bn: 'ব্রাঞ্চ অপস ড্যাশবোর্ড', t: 'd' },
      { id: 'M04-receipts', en: 'Receipt & Label Printing', bn: 'রিসিট ও লেবেল প্রিন্ট', t: 'g' }
    ]}
  ],
  reports: ['Branch Daily Cash Summary', 'Token Wait-Time Distribution', 'Uncollected Device Ageing', 'Counter Sales by Category', 'Shift Variance Register', 'Branch Comparison League'],
  forms: ['Token Issue', 'Device Storage Assignment', 'Shift Open/Close', 'Counter Sale', 'Handover (ID verified)'],
  cross: ['M01 walk-in intake', 'M03 collection/delivery', 'M20 receipts', 'M47 branch infrastructure', 'M17 device custody'],
  freg: {
    src: 95,
    sub: [
      ['1', 'Token & Queue', 12],
      ['2', 'Counter Workstation', 14],
      ['3', 'Device Storage & Retrieval', 10],
      ['4', 'Collection & Handover', 9],
      ['5', 'Counter Sales', 8],
      ['6', 'Cash Drawer', 12],
      ['7', 'Payment Capture', 9],
      ['8', 'Shift Operations', 10],
      ['9', 'Banking & Deposits', 5],
      ['10', 'Branch Admin', 6]
    ]
  }
};

/* In-workspace data screens over the whitelisted front-desk models. */
export const SCREENS = {
  'M04-queue': { kind: 'model_list', model: 'fix.token.queue', create: false,
    cols: ['token_display', 'counter_number', 'service_type', 'customer_id', 'state', 'issued_at', 'called_at', 'served_at'],
    stateField: 'state',
    actions: [
      { m: 'action_call', l: 'Call Token' },
      { m: 'action_serving', l: 'Start Serving' },
      { m: 'action_complete', l: 'Complete' },
      { m: 'action_no_show', l: 'Mark No-Show' }
    ] },
  'M04-counter': { kind: 'table_report', module: 'M04', report: 'wait_distribution', period: false },
  'M04-priority': { kind: 'model_list', model: 'fix.token.queue', create: false,
    cols: ['token_display', 'service_type', 'state', 'issued_at'],
    domain: [['state', '=', 'waiting']] },
  'M04-storage': { kind: 'model_list', model: 'fix.walkin.intake', create: false,
    cols: ['customer_id', 'device_serial_input', 'fault_description', 'state', 'intake_start', 'intake_duration_seconds', 'service_order_id'],
    stateField: 'state',
    actions: [{ m: 'action_submit_for_handover', l: 'Submit for Handover' }] },
  'M04-handover': { kind: 'model_list', model: 'fix.walkin.intake', create: false,
    cols: ['customer_id', 'device_id', 'state', 'handover_method', 'handover_acknowledged', 'handover_acknowledged_at', 'service_order_id'],
    domain: [['state', 'in', ['handover_pending', 'completed']]],
    stateField: 'state',
    actions: [{ m: 'action_complete_handover', l: 'Complete Handover' }] },
  'M04-uncollected': { kind: 'table_report', module: 'M04', report: 'uncollected_ageing', period: false },
  'M04-drawer': { kind: 'model_list', model: 'fix.cash.shift', create: false,
    cols: ['shift_date', 'shift_type', 'branch_id', 'operator_id', 'opening_float', 'cash_payments', 'cash_refunds', 'expected_closing', 'closing_counted', 'variance', 'state'],
    stateField: 'state',
    actions: [
      { m: 'action_close_shift', l: 'Close for Counting' },
      { m: 'action_confirm_closed', l: 'Confirm Count' },
      { m: 'action_reconcile', l: 'Reconcile' }
    ] },
  'M04-payments': { kind: 'model_list', model: 'fix.counter.sale', create: false,
    cols: ['name', 'sale_date', 'branch_id', 'product_id', 'quantity', 'total', 'payment_method', 'state'],
    stateField: 'state' },
  'M04-shift': { kind: 'table_report', module: 'M04', report: 'daily_cash', period: false },
  'M04-banking': { kind: 'table_report', module: 'M04', report: 'variance_register', period: false },
  'M04-sales': { kind: 'model_list', model: 'fix.counter.sale', create: false,
    cols: ['name', 'sale_date', 'product_id', 'quantity', 'unit_price', 'total', 'payment_method', 'state', 'sold_by'],
    stateField: 'state',
    actions: [
      { m: 'action_confirm', l: 'Confirm Sale' },
      { m: 'action_refund', l: 'Refund' }
    ] },
  'M04-kiosk': { kind: 'table_report', module: 'M04', report: 'sales_category', period: false },
  'M04-checklists': { kind: 'table_report', module: 'M04', report: 'branch_league', period: false },
  'M04-dashboard': { kind: 'table_report', module: 'M04', report: 'branch_league', period: false },
  'M04-receipts': { kind: 'model_list', model: 'fix.counter.sale', create: false,
    cols: ['name', 'sale_date', 'customer_id', 'product_id', 'total', 'payment_method', 'state'],
    domain: [['state', '=', 'confirmed']] }
};

/* built-in report chips -> the screen that shows that report */
export const REPORT_ROUTES = {
  "M04:Branch Daily Cash Summary": "M04-shift",
  "M04:Token Wait-Time Distribution": "M04-counter",
  "M04:Uncollected Device Ageing": "M04-uncollected",
  "M04:Counter Sales by Category": "M04-kiosk",
  "M04:Shift Variance Register": "M04-banking",
  "M04:Branch Comparison League": "M04-dashboard"
};

/* data-entry form chips: tokens and intakes are created by the counter
 * flows; the honest toast covers the rest until their engines land. */
export const FORM_MODELS = {};

/* the module's "+ New" surface: no generic create — counter work starts
 * from the token issue or the walk-in intake. */
export const CREATE = {};
