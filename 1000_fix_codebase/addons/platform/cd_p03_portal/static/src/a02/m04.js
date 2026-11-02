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
    domain: [['state', '=', 'confirmed']] },

  /* ===== service data-entry forms (registry names) ===== */
  'M04-form-token': {
    kind: 'model_form',
    model: 'fix.token.queue',
    title: "Token Issue",
    back: 'M04-tokens',
    status: { field: 'state', labels: { waiting: "Waiting", called: "Called", served: "Served", abandoned: "Abandoned" } },
    tabs: [
      { id: 'token', label: '1. Token & Service', bn: '১. টোকেন ও সেবা', icon: '🎫', badge: '7' },
      { id: 'wait', label: '2. SLA Wait Time & Escalation', bn: '২. অপেক্ষার সময় ও এসকেলেশন', icon: '⏱️', badge: '5' }
    ],
    sections: [
      { tab: 'token', title: "Token Generation & Customer Classification", note: "A queue token per walk-in. Called/served timestamps are what the wait-time report measures.",
        fields: [
          { name: 'branch_id', required: true, label: "Branch Hub" },
          { name: 'token_display', label: "Token Number", readonly: true },
          { name: 'customer_id', label: "Customer" },
          { name: 'customer_phone', label: "Customer Phone (+880)" },
          { name: 'service_type', required: true, label: "Intake Channel / Stream" },
          { name: 'counter_number', label: "Assigned Service Counter" },
          { name: 'service_order_id', label: "Linked Service Order" }
        ] },
      { tab: 'wait', title: "15-Minute Wait SLA & Supervisor Escalation (FLAW-04.1)",
        fields: [
          { name: 'priority_level', label: "Queue Priority Tier" },
          { name: 'wait_seconds', label: "Elapsed Waiting Time (Seconds)", readonly: true },
          { name: 'wait_sla_breached', label: "15-Min Wait SLA Breached Alert", readonly: true },
          { name: 'supervisor_escalated', label: "Escalated to Branch Supervisor" },
          { name: 'state', required: true, label: "Token Status" }
        ] }
    ]
  },
  'M04-form-storage': {
    kind: 'model_form',
    model: 'fix.walkin.intake',
    title: "Device Storage Assignment",
    back: 'M04-intake',
    status: { field: 'state', labels: { open: "Open", handed_over: "Handed Over", converted: "Converted", abandoned: "Abandoned" } },
    tabs: [
      { id: 'intake', label: '1. Customer & Device', bn: '১. গ্রাহক ও ডিভাইস', icon: '📱', badge: '6' },
      { id: 'accessory', label: '2. Accessory Bag & Barcode', bn: '২. ব্যাগ ও বারকোড', icon: '🎒', badge: '6' },
      { id: 'condition', label: '3. Cosmetic Matrix & LCI', bn: '৩. বাহ্যিক অবস্থা ও আর্দ্রতা', icon: '🔍', badge: '5' },
      { id: 'handover', label: '4. Handover & Loaner', bn: '৪. হস্তান্তর ও লোনার ডিভাইস', icon: '🤝', badge: '5' }
    ],
    sections: [
      { tab: 'intake', title: "Walk-In Customer & Serial Verification", note: "The intake record ties the device, serial, and customer statement to a token.",
        fields: [
          { name: 'token_id', label: "Queue Token" },
          { name: 'branch_id', required: true, label: "Branch Center" },
          { name: 'customer_id', required: true, label: "Customer" },
          { name: 'customer_phone', label: "Customer Phone" },
          { name: 'device_serial_input', label: "Scanned Serial / IMEI" },
          { name: 'fault_description', required: true, label: "Reported Fault & Symptoms", type: "text" }
        ] },
      { tab: 'accessory', title: "Accessory Bagging Gate (FLAW-04.3)",
        note: "Every walk-in intake must scan a sealed accessory bag barcode before conversion to a service order.",
        fields: [
          { name: 'accessory_bag_barcode', required: true, label: "Accessory Bag Barcode (Mandatory Gate)" },
          { name: 'has_charger', label: "Power Adapter Included" },
          { name: 'has_battery', label: "Battery Included" },
          { name: 'has_cable_stylus', label: "Data Cable / Stylus / Case Included" },
          { name: 'storage_bin_code', label: "Secure Storage Bin Code" },
          { name: 'state', required: true, label: "Intake Workflow State" }
        ] },
      { tab: 'condition', title: "6-Point Cosmetic Condition Matrix & Water Ingress",
        fields: [
          { name: 'cosmetic_condition_matrix', label: "Cosmetic Condition Matrix (Scratches/Dents)", type: "text" },
          { name: 'lci_status', label: "Liquid Contact Indicator (LCI) Status" },
          { name: 'intake_photo_attachment_id', label: "Counter Intake Photo Proof" },
          { name: 'diagnostic_fee_bdt', label: "Initial Diagnostic Fee (BDT)" },
          { name: 'payment_channel', label: "Fee Payment Channel" }
        ] },
      { tab: 'handover', title: "Customer Handover Proof & Temporary Loaner Device",
        fields: [
          { name: 'handover_acknowledged', label: "Customer Handover Acknowledged" },
          { name: 'handover_method', label: "Handover Proof Method" },
          { name: 'loaner_device_id', label: "Issued Temporary Loaner Device" },
          { name: 'customer_signature_attachment_id', label: "Customer Signed Intake Receipt" },
          { name: 'service_order_id', label: "Generated Service Order Ref", readonly: true }
        ] }
    ]
  },
  'M04-form-shift': {
    kind: 'model_form',
    model: 'fix.cash.shift',
    title: "Shift Open/Close",
    back: 'M04-shifts',
    status: { field: 'state', labels: { open: "Open", closed: "Closed", reconciled: "Reconciled" } },
    tabs: [
      { id: 'shift', label: '1. Shift Context', bn: '১. শিফট তথ্য', icon: '🏢', badge: '5' },
      { id: 'blind', label: '2. Bangladesh Taka Denomination Count', bn: '২. টাকার নোট গণনা', icon: '💵', badge: '10' },
      { id: 'reconciliation', label: '3. Field Cash & Supervisor Approval', bn: '৩. ফিল্ড ক্যাশ ও অনুমোদন', icon: '✍️', badge: '6' }
    ],
    sections: [
      { tab: 'shift', title: "Cash Drawer Shift Identity & Opening Float", note: "A cash shift: the opening float is entered, closing count is blinded, and variance is computed.",
        fields: [
          { name: 'branch_id', required: true, label: "Branch Hub" },
          { name: 'shift_date', required: true, label: "Shift Date" },
          { name: 'shift_type', required: true, label: "Shift Type (Morning / Evening)" },
          { name: 'operator_id', required: true, label: "Cashier / Operator" },
          { name: 'opening_float', label: "Opening Cash Float (BDT)" }
        ] },
      { tab: 'blind', title: "Blind Physical Cash Count by BDT Note Denominations (FLAW-04.2)",
        note: "Cashier counts physical currency notes blindly without seeing system expected cash totals.",
        fields: [
          { name: 'denom_1000_count', label: "৳১,০০০ নোট সংখ্যা" },
          { name: 'denom_500_count', label: "৳৫০০ নোট সংখ্যা" },
          { name: 'denom_200_count', label: "৳২০০ নোট সংখ্যা" },
          { name: 'denom_100_count', label: "৳১০০ নোট সংখ্যা" },
          { name: 'denom_50_count', label: "৳৫০ নোট সংখ্যা" },
          { name: 'denom_20_count', label: "৳২০ নোট সংখ্যা" },
          { name: 'denom_10_count', label: "৳১০ নোট সংখ্যা" },
          { name: 'coins_amount', label: "কয়েন ও ভাংতি মোট টাকা" },
          { name: 'closing_counted', label: "Total Physical Counted (BDT)", readonly: true },
          { name: 'blind_count_submitted', label: "Blind Count Formally Submitted", readonly: true }
        ] },
      { tab: 'reconciliation', title: "M02 Field Service Cash Handover & Supervisor Variance Gate (FLAW-04.2 / HS-08)",
        note: "Variances exceeding ৳১০০ require branch supervisor cryptographic / user sign-off.",
        fields: [
          { name: 'field_cash_deposited', label: "M02 On-Site Field Cash Deposited (BDT)" },
          { name: 'mfs_settled_amount', label: "bKash / Nagad POS Settled Amount (BDT)" },
          { name: 'variance', label: "Cash Drawer Variance (BDT)", readonly: true },
          { name: 'supervisor_variance_approved_by', label: "Supervisor Variance Approved By" },
          { name: 'bank_deposit_slip_no', label: "Bank Deposit Challan / Slip No" },
          { name: 'bank_deposit_attachment_id', label: "Bank Deposit Slip Scanned PDF" },
          { name: 'state', required: true, label: "Reconciliation Status" }
        ] }
    ]
  },
  'M04-form-countersale': {
    kind: 'model_form',
    model: 'fix.counter.sale',
    title: "Counter Sale",
    back: 'M04-counter',
    status: { field: 'state', labels: { draft: "Draft", paid: "Paid", refunded: "Refunded" } },
    tabs: [
      { id: 'sale', label: '1. Sale Line & Product', bn: '১. পণ্য ও বিক্রয়', icon: '🛒', badge: '7' },
      { id: 'mushak', label: '2. Payment & Mushak 6.3', bn: '২. পেমেন্ট ও মূসক ৬.৩', icon: '🧾', badge: '6' }
    ],
    sections: [
      { tab: 'sale', title: "Over-the-Counter Retail Sale & Shift Association", note: "An over-the-counter sale tied to the shift that rang it.",
        fields: [
          { name: 'name', label: "Sale Receipt Number", readonly: true },
          { name: 'shift_id', label: "Active Cash Shift" },
          { name: 'branch_id', label: "Branch Center" },
          { name: 'customer_id', label: "Customer" },
          { name: 'product_id', required: true, label: "Sold Product / Spare Part" },
          { name: 'quantity', required: true, label: "Quantity" },
          { name: 'unit_price', required: true, label: "Unit Price (BDT)" }
        ] },
      { tab: 'mushak', title: "Mushak 6.3 VAT & Payment Capture",
        fields: [
          { name: 'payment_method', required: true, label: "Payment Channel (Cash/bKash/Card)" },
          { name: 'payment_trx_ref', label: "Gateway Transaction Reference" },
          { name: 'vat_amount', label: "Mushak 15% VAT (BDT)", readonly: true },
          { name: 'total', required: true, label: "Grand Total (BDT)" },
          { name: 'invoice_attachment_id', label: "Signed Mushak 6.3 Invoice PDF" },
          { name: 'state', required: true, label: "Transaction State" }
        ] }
    ]
  },

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


export const FORM_CHIPS = {
  'M04:Handover (ID verified)': 'M04-form-storage',
  'M04:Token Issue': 'M04-form-token',
  'M04:Device Storage Assignment': 'M04-form-storage',
  'M04:Shift Open/Close': 'M04-form-shift',
  'M04:Counter Sale': 'M04-form-countersale',
  'M04:__by_model__': {
    'fix.token.queue': 'M04-form-token',
    'fix.walkin.intake': 'M04-form-storage',
    'fix.cash.shift': 'M04-form-shift',
    'fix.counter.sale': 'M04-form-countersale',
  },
  'M04:__by_screen__': {
    'M04-tokens': 'M04-form-token',
    'M04-intake': 'M04-form-storage',
    'M04-shifts': 'M04-form-shift',
    'M04-counter': 'M04-form-countersale',
  }
};
