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
      { id: 'M04-counter', en: 'Counter Workstation', bn: 'কাউন্টার ওয়ার্কস্টেশন', t: 'r' },
      { id: 'M04-priority', en: 'Priority Queue Rules', bn: 'প্রায়োরিটি কিউ রুলস', t: 'g' }
    ]},
    { en: 'Device Custody', screens: [
      { id: 'M04-storage', en: 'Storage Locations', bn: 'স্টোরেজ অবস্থান', t: 'g' },
      { id: 'M04-handover', en: 'Collection & Handover', bn: 'সংগ্রহ ও হস্তান্তর', t: 'g' },
      { id: 'M04-uncollected', en: 'Uncollected Devices', bn: 'অসংগৃহীত ডিভাইস', t: 'r' }
    ]},
    { en: 'Cash & Shift', screens: [
      { id: 'M04-drawer', en: 'Cash Drawer', bn: 'ক্যাশ ড্রয়ার', t: 'g' },
      { id: 'M04-payments', en: 'Payment Capture (All Methods)', bn: 'পেমেন্ট গ্রহণ', t: 'g' },
      { id: 'M04-shift', en: 'Shift Open / Close', bn: 'শিফট খোলা/বন্ধ', t: 'r' },
      { id: 'M04-banking', en: 'Banking Deposits', bn: 'ব্যাংকিং ডিপোজিট', t: 'r' }
    ]},
    { en: 'Counter Sales', screens: [
      { id: 'M04-sales', en: 'Counter Sales (Parts/Plans)', bn: 'কাউন্টার বিক্রয়', t: 'g' },
      { id: 'M04-kiosk', en: 'Kiosk Mode', bn: 'কিয়স্ক মোড', t: 'r' }
    ]},
    { en: 'Branch Ops', screens: [
      { id: 'M04-checklists', en: 'Open/Close Checklists', bn: 'খোলা/বন্ধ চেকলিস্ট', t: 'r' },
      { id: 'M04-dashboard', en: 'Branch Ops Dashboard', bn: 'ব্রাঞ্চ অপস ড্যাশবোর্ড', t: 'r' },
      { id: 'M04-receipts', en: 'Receipt & Label Printing', bn: 'রিসিট ও লেবেল প্রিন্ট', t: 'g' }
    ]}
  ],
  reports: ['Branch Daily Cash Summary', 'Token Wait-Time Distribution', 'Uncollected Device Ageing', 'Counter Sales by Category', 'Shift Variance Register', 'Branch Comparison League'],
  /* 'Handover (ID verified)' opened a BLANK intake form; a hand-over is the
   * Complete Handover action on an existing intake (Collection & Handover).
   * 'Device Storage Assignment' was the walk-in intake form under another name. */
  forms: ['Token Issue', 'Walk-in Intake', 'Shift Open/Close', 'Counter Sale'],
  cross: ['M01 walk-in intake', 'M03 collection/delivery', 'M20 receipts', 'M47 branch infrastructure', 'M17 device custody'],
  freg: {
    src: 95,
    sub: [
      ['1', 'Token & Queue', 12, { model: 'fix.token.queue', cols: ['token_display', 'service_type', 'priority_level', 'state', 'issued_at'], screens: ['M04-queue', 'M04-priority'], reports: ['Token Wait-Time Distribution'], forms: ['Token Issue'] }],
      ['2', 'Counter Workstation', 14, { model: 'fix.walkin.intake', cols: ['customer_id', 'device_serial_input', 'symptom_category', 'state', 'intake_start'], screens: ['M04-counter'], reports: ['Token Wait-Time Distribution'], forms: ['Walk-in Intake'] }],
      ['3', 'Device Storage & Retrieval', 10, { model: 'fix.walkin.intake', cols: ['customer_id', 'device_id', 'storage_bin_code', 'state', 'service_order_id'], screens: ['M04-storage', 'M04-uncollected'], reports: ['Uncollected Device Ageing'], forms: [], create: false }],
      ['4', 'Collection & Handover', 9, { model: 'fix.walkin.intake', cols: ['customer_id', 'device_id', 'handover_method', 'handover_acknowledged_at', 'state'], screens: ['M04-handover', 'M04-uncollected'], reports: ['Uncollected Device Ageing'], forms: [], create: false, domain: [['state', 'in', ['handover_pending', 'completed']]] }],
      ['5', 'Counter Sales', 8, { model: 'fix.counter.sale', cols: ['name', 'sale_date', 'product_id', 'total', 'state'], screens: ['M04-sales', 'M04-kiosk'], reports: ['Counter Sales by Category'], forms: ['Counter Sale'] }],
      ['6', 'Cash Drawer', 12, { model: 'fix.cash.shift', cols: ['shift_date', 'opening_float', 'expected_closing', 'closing_counted', 'variance'], screens: ['M04-drawer'], reports: ['Branch Daily Cash Summary', 'Shift Variance Register'], forms: ['Shift Open/Close'] }],
      ['7', 'Payment Capture', 9, { model: 'fix.counter.sale', cols: ['name', 'customer_id', 'total', 'payment_method', 'transaction_ref'], screens: ['M04-payments', 'M04-receipts'], reports: ['Branch Daily Cash Summary'], forms: [], create: false }],
      ['8', 'Shift Operations', 10, { model: 'fix.cash.shift', cols: ['shift_date', 'shift_type', 'operator_id', 'opened_at', 'state'], screens: ['M04-shift', 'M04-checklists'], reports: ['Branch Daily Cash Summary'], forms: ['Shift Open/Close'] }],
      ['9', 'Banking & Deposits', 5, { model: 'fix.cash.deposit', cols: ['name', 'branch_id', 'business_date', 'amount', 'state'], screens: ['M04-banking'], reports: ['Shift Variance Register'], forms: [] }],
      ['10', 'Branch Admin', 6, { model: 'fix.branch', cols: ['code', 'name', 'zone_id', 'manager_id', 'phone'], screens: ['M04-dashboard', 'M04-checklists'], reports: ['Branch Comparison League'], forms: [] }]
    ]
  }
};

/* In-workspace data screens over the whitelisted front-desk models. */
export const SCREENS = {
  'M04-queue': { kind: 'model_list', model: 'fix.token.queue', create: false,
    cols: ['token_display', 'counter_number', 'service_type', 'customer_id', 'state', 'issued_at', 'called_at', 'recall_count', 'served_at'],
    stateField: 'state',
    actions: [
      /* A02 audit M04-P2: calling a called or no-show token again is a
       * counted re-call; the queue actions need a front-desk role */
      { m: 'action_call', l: 'Call / Re-call Token' },
      { m: 'action_serving', l: 'Start Serving' },
      { m: 'action_complete', l: 'Complete' },
      { m: 'action_no_show', l: 'Mark No-Show' },
      { m: 'action_cancel', l: 'Cancel Token' },
      /* A02 audit M04-9: the wait SLA also runs on a 5-minute cron */
      { m: 'action_evaluate_wait_sla', l: 'Check Wait SLA' }
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
    /* A02 audit M04-2/-11: the cashier submits a BLIND count (it no longer
     * echoes the variance); a Branch Manager who did not handle the cash
     * approves a variance beyond tolerance and reconciles (BRU-FRD-11).
     * A02 audit B1: the approval is decided in the manager's M63 inbox. */
    actions: [
      { m: 'action_close_shift', l: 'Close for Counting' },
      { m: 'action_submit_blind_count', l: 'Submit Blind Count' },
      { m: 'action_confirm_closed', l: 'Confirm Count' },
      { m: 'action_request_approval', l: 'Request Variance Approval', ask: 'Explanation of the variance', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Approval Request' },
      { m: 'action_reconcile', l: 'Reconcile' }
    ] },
  'M04-payments': { kind: 'model_list', model: 'fix.counter.sale', create: false,
    cols: ['name', 'sale_date', 'branch_id', 'product_id', 'quantity', 'total', 'payment_method', 'state'],
    stateField: 'state' },
  'M04-shift': { kind: 'table_report', module: 'M04', report: 'daily_cash', period: false },
  'M04-banking': { kind: 'table_report', module: 'M04', report: 'variance_register', period: false },
  'M04-sales': { kind: 'model_list', model: 'fix.counter.sale', create: false,
    cols: ['name', 'sale_date', 'product_id', 'quantity', 'unit_price', 'total', 'payment_method', 'state', 'refund_state', 'sold_by'],
    stateField: 'state',
    /* A02 audit M04-5: a price below list and a refund need a manager who
     * did not sell; the refund leaves the drawer that is open now.
     * A02 audit B1: both are decided in the approver's M63 inbox; a refund
     * request routes itself. */
    actions: [
      { m: 'action_confirm', l: 'Confirm Sale' },
      { m: 'action_request_approval', l: 'Request Price Approval', ask: 'Why the price is below list', kwarg: 'justification' },
      { m: 'action_request_refund', l: 'Request Refund', ask: 'Reason (defective / wrong_item / customer_cancelled / duplicate / other): note', kwarg: 'reason' },
      { m: 'action_recall_approval', l: 'Recall Approval Request' }
    ] },
  'M04-kiosk': { kind: 'table_report', module: 'M04', report: 'sales_category', period: false },
  /* M04 sweep audit 2026-11-06: the checklist screen gets its own pack —
   * it previously duplicated the branch league table verbatim. */
  'M04-checklists': { kind: 'table_report', module: 'M04', report: 'shift_checklists', title: 'Open/Close Checklists', period: false },
  'M04-dashboard': { kind: 'table_report', module: 'M04', report: 'branch_league', period: false },
  'M04-receipts': { kind: 'model_list', model: 'fix.counter.sale', create: false,
    cols: ['name', 'sale_date', 'customer_id', 'product_id', 'total', 'payment_method', 'state'],
    domain: [['state', '=', 'confirmed']] },

  /* ===== service data-entry forms (registry names) ===== */
  'M04-form-token': {
    kind: 'model_form',
    model: 'fix.token.queue',
    title: "Token Issue",
    back: 'M04-queue',
    status: { field: 'state', labels: { waiting: "Waiting", called: "Called", serving: "Serving", completed: "Completed", no_show: "No Show", cancelled: "Cancelled" } },
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
          { name: 'customer_phone', label: "Customer Phone (+880)", readonly: true },
          { name: 'service_type', required: true, label: "Intake Channel / Stream" },
          { name: 'counter_number', label: "Assigned Service Counter" },
          { name: 'service_order_id', label: "Linked Service Order", readonly: true }
        ] },
      { tab: 'wait', title: "15-Minute Wait SLA & Supervisor Escalation (FLAW-04.1)",
        fields: [
          { name: 'priority_level', label: "Queue Priority Tier" },
          { name: 'wait_seconds', label: "Elapsed Waiting Time (Seconds)", readonly: true },
          { name: 'wait_sla_breached', label: "15-Min Wait SLA Breached Alert", readonly: true },
          { name: 'recall_count', label: "Times Re-called", readonly: true },
          { name: 'supervisor_escalated', label: "Escalated to Branch Supervisor", readonly: true },
          { name: 'state', label: "Token Status", readonly: true }
        ] }
    ]
  },
  'M04-form-storage': {
    kind: 'model_form',
    model: 'fix.walkin.intake',
    title: "Walk-in Intake",
    back: 'M04-storage',
    status: { field: 'state', labels: { in_progress: "In Progress", handover_pending: "Handover Pending", completed: "Completed" } },
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
          { name: 'customer_phone', label: "Customer Phone", readonly: true },
          /* BRU-FRD-12 (A02 audit M04-8): the device is identified before handover */
          { name: 'device_id', label: "Registered Device" },
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
          { name: 'state', label: "Intake Workflow State", readonly: true }
        ] },
      { tab: 'condition', title: "6-Point Cosmetic Condition Matrix & Water Ingress",
        fields: [
          { name: 'cosmetic_condition_matrix', label: "Cosmetic Condition Matrix (Scratches/Dents)", type: "text" },
          { name: 'lci_status', label: "Liquid Contact Indicator (LCI) Status" },
          { name: 'intake_photo_attachment_id', label: "Counter Intake Photo Proof" },
          { name: 'diagnostic_fee_bdt', label: "Initial Diagnostic Fee (BDT)" },
          { name: 'payment_channel', label: "Fee Payment Channel" },
          /* A02 audit M04-P2: a cash fee goes to the open drawer at hand-off;
           * a waiver is approved in a Branch Manager's M63 inbox */
          { name: 'payment_trx_ref', label: "Fee Receipt / MFS TrxID" },
          { name: 'fee_waiver_approved_by_id', label: "Fee Waiver Approved By", readonly: true },
          { name: 'diagnostic_fee_shift_id', label: "Fee Posted To Shift", readonly: true }
        ] },
      { tab: 'handover', title: "Customer Handover Proof & Temporary Loaner Device",
        fields: [
          { name: 'handover_acknowledged', label: "Customer Handover Acknowledged", readonly: true },
          { name: 'handover_method', label: "Handover Proof Method (Digital Signature)" },
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
    back: 'M04-drawer',
    status: { field: 'state', labels: { open: "Open", counting: "Counting", closed: "Closed", reconciled: "Reconciled", discrepancy: "Discrepancy" } },
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
          { name: 'field_cash_deposited', label: "M02 On-Site Field Cash Deposited (BDT)", readonly: true },
          { name: 'mfs_settled_amount', label: "bKash / Nagad POS Settled Amount (BDT)" },
          { name: 'variance', label: "Cash Drawer Variance (BDT)", readonly: true },
          /* A02 audit M04-2: stamped by Approve Variance, never typed */
          { name: 'supervisor_variance_approved_by', label: "Supervisor Variance Approved By", readonly: true },
          { name: 'variance_approved_amount', label: "Approved Variance (BDT)", readonly: true },
          { name: 'approval_state', label: "Variance Approval (M63)", readonly: true },
          { name: 'reconciled_by', label: "Reconciled By", readonly: true },
          { name: 'bank_deposit_slip_no', label: "Bank Deposit Challan / Slip No" },
          { name: 'bank_deposit_attachment_id', label: "Bank Deposit Slip Scanned PDF" },
          { name: 'state', label: "Reconciliation Status", readonly: true }
        ] }
    ]
  },
  'M04-form-countersale': {
    kind: 'model_form',
    model: 'fix.counter.sale',
    title: "Counter Sale",
    back: 'M04-sales',
    status: { field: 'state', labels: { draft: "Draft", confirmed: "Confirmed", refunded: "Refunded" } },
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
          { name: 'unit_price', required: true, label: "Unit Price (BDT)" },
          { name: 'list_price_floor', label: "List Price (BDT)", readonly: true },
          { name: 'price_override_approved_by', label: "Price Below List Approved By", readonly: true }
        ] },
      { tab: 'mushak', title: "Mushak 6.3 VAT & Payment Capture",
        fields: [
          { name: 'payment_method', required: true, label: "Payment Channel (Cash/bKash/Card)" },
          /* A02 audit M04-12: payment_trx_ref / vat_amount / invoice_attachment_id
           * never existed on the model; transaction_ref is the real field */
          { name: 'transaction_ref', label: "Gateway Transaction Reference" },
          /* A02 audit M04-P2: tender, VAT split (prices include VAT) and the
           * Mushak-6.3 number issued at confirm */
          { name: 'tendered_amount', label: "Cash Tendered (BDT)" },
          { name: 'change_due', label: "Change Due (BDT)", readonly: true },
          { name: 'mushak_63_ref', label: "NBR Mushak-6.3 Number", readonly: true },
          { name: 'vat_rate', label: "VAT Rate (%)", readonly: true },
          { name: 'amount_untaxed', label: "Net of VAT (BDT)", readonly: true },
          { name: 'vat_amount', label: "VAT (BDT)", readonly: true },
          { name: 'approval_state', label: "Approval (M63)", readonly: true },
          { name: 'total', label: "Grand Total (BDT)", readonly: true },
          { name: 'state', label: "Transaction State", readonly: true },
          { name: 'refund_state', label: "Refund Status", readonly: true },
          { name: 'refund_reason_code', label: "Refund Reason", readonly: true },
          { name: 'refund_approved_by', label: "Refund Approved By", readonly: true }
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
  'M04:Token Issue': 'M04-form-token',
  'M04:Walk-in Intake': 'M04-form-storage',
  'M04:Shift Open/Close': 'M04-form-shift',
  'M04:Counter Sale': 'M04-form-countersale',
  'M04:__by_model__': {
    'fix.token.queue': 'M04-form-token',
    'fix.walkin.intake': 'M04-form-storage',
    'fix.cash.shift': 'M04-form-shift',
    'fix.counter.sale': 'M04-form-countersale',
  },
  'M04:__by_screen__': {
    'M04-queue': 'M04-form-token',
    'M04-storage': 'M04-form-storage',
    'M04-drawer': 'M04-form-shift',
    'M04-sales': 'M04-form-countersale',
  }
};
