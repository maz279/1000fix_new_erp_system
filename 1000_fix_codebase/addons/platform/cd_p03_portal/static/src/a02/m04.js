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
      { id: 'M04-checklists', en: 'Open/Close Checklists', bn: 'খোলা/বন্ধ চেকলিস্ট', t: 'g' },
      { id: 'M04-dashboard', en: 'Branch Ops Dashboard', bn: 'ব্রাঞ্চ অপস ড্যাশবোর্ড', t: 'r' },
      { id: 'M04-receipts', en: 'Receipt & Label Printing', bn: 'রিসিট ও লেবেল প্রিন্ট', t: 'g' }
    ]}
  ],
  reports: ['Branch Daily Cash Summary', 'Token Wait-Time Distribution', 'Uncollected Device Ageing', 'Counter Sales by Category', 'Shift Variance Register', 'Branch Comparison League'],
  /* 'Handover (ID verified)' opened a BLANK intake form; a hand-over is the
   * Complete Handover action on an existing intake (Collection & Handover).
   * 'Device Storage Assignment' was the walk-in intake form under another name. */
  /* M04 sub-module audit (13 Nov 2026): only 2 of the 10 sub-module pages
   * offered a capture button (Counter Workstation, Shift Operations). Every
   * M04 list said `create: false`, so fregCreate offered nothing on the token,
   * drawer and sales pages although their forms existed; the custody,
   * hand-over and payment pages had no form at all; the registry's
   * 'Device Storage Assignment' and 'Handover (ID verified)' forms had been
   * dropped without a replacement; and Branch Admin listed M30's branch
   * master. Each page now captures its own record (test_m04_submodule_capture). */
  forms: ['Token Issue', 'Walk-in Intake', 'Device Storage Assignment', 'Handover (ID verified)',
    'Shift Open/Close', 'Counter Sale', 'Counter Payment', 'Cash Deposit', 'Opening / Closing Checklist'],
  cross: ['M01 walk-in intake', 'M03 collection/delivery', 'M20 receipts', 'M47 branch infrastructure', 'M17 device custody'],
  freg: {
    src: 95,
    sub: [
      ['1', 'Token & Queue', 12, { model: 'fix.token.queue', cols: ['token_display', 'service_type', 'priority_level', 'state', 'issued_at'], screens: ['M04-queue', 'M04-priority'], reports: ['Token Wait-Time Distribution'], forms: ['Token Issue'] }],
      ['2', 'Counter Workstation', 14, { model: 'fix.walkin.intake', cols: ['customer_id', 'device_serial_input', 'symptom_category', 'state', 'intake_start'], screens: ['M04-counter'], reports: ['Token Wait-Time Distribution'], forms: ['Walk-in Intake'] }],
      /* 3 FR-FRD-011: the shelf / bin of a device already in custody */
      ['3', 'Device Storage & Retrieval', 10, { model: 'fix.walkin.intake', cols: ['customer_id', 'device_id', 'storage_bin_code', 'state', 'service_order_id'], screens: ['M04-storage', 'M04-uncollected'], reports: ['Uncollected Device Ageing'], forms: ['Device Storage Assignment'], create: 'M04-form-storage-assign' }],
      /* 4 BRU-FRD-05: the customer's signed acknowledgement of an intake */
      ['4', 'Collection & Handover', 9, { model: 'fix.walkin.intake', cols: ['customer_id', 'device_id', 'handover_method', 'handover_acknowledged_at', 'state'], screens: ['M04-handover', 'M04-uncollected'], reports: ['Uncollected Device Ageing'], forms: ['Handover (ID verified)'], create: 'M04-form-handover', domain: [['state', 'in', ['handover_pending', 'completed']]] }],
      ['5', 'Counter Sales', 8, { model: 'fix.counter.sale', cols: ['name', 'sale_date', 'product_id', 'total', 'state'], screens: ['M04-sales', 'M04-kiosk'], reports: ['Counter Sales by Category'], forms: ['Counter Sale'] }],
      ['6', 'Cash Drawer', 12, { model: 'fix.cash.shift', cols: ['shift_date', 'opening_float', 'expected_closing', 'closing_counted', 'variance'], screens: ['M04-drawer'], reports: ['Branch Daily Cash Summary', 'Shift Variance Register'], forms: ['Shift Open/Close'] }],
      /* 7 FR-FRD-016: the method, reference and tender of a rung-up sale */
      ['7', 'Payment Capture', 9, { model: 'fix.counter.sale', cols: ['name', 'customer_id', 'total', 'payment_method', 'transaction_ref'], screens: ['M04-payments', 'M04-receipts'], reports: ['Branch Daily Cash Summary'], forms: ['Counter Payment'], create: 'M04-form-payment' }],
      ['8', 'Shift Operations', 10, { model: 'fix.cash.shift', cols: ['shift_date', 'shift_type', 'operator_id', 'opened_at', 'state'], screens: ['M04-shift', 'M04-shift-close', 'M04-checklists'], reports: ['Branch Daily Cash Summary'], forms: ['Shift Open/Close', 'Opening / Closing Checklist'] }],
      /* 9 FR-FRD-018: M04 records the deposit (M50's form, M50 reconciles it) */
      ['9', 'Banking & Deposits', 5, { model: 'fix.cash.deposit', cols: ['name', 'branch_id', 'business_date', 'amount', 'state'], screens: ['M04-banking'], reports: ['Shift Variance Register'], forms: ['Cash Deposit'], create: 'M50-form-deposit' }],
      /* 10 FR-FRD-020/022/024: the branch's daily checklists and handover
       * notes. The branch itself is M30's configuration (spec section 3.2). */
      ['10', 'Branch Admin', 6, { model: 'fix.branch.checklist', cols: ['name', 'branch_id', 'checklist_type', 'checklist_date', 'open_item_count', 'state', 'completed_by_id'], screens: ['M04-checklists', 'M04-dashboard'], reports: ['Branch Comparison League'], forms: ['Opening / Closing Checklist'] }]
    ]
  }
};

/* In-workspace data screens over the whitelisted front-desk models. */
export const SCREENS = {
  /* a token is issued at the counter (FR-FRD-001): "+ New" opens Token Issue */
  'M04-queue': { kind: 'model_list', model: 'fix.token.queue',
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
  /* a drawer starts with a counted float (FR-FRD-014): "+ New" opens a shift */
  'M04-drawer': { kind: 'model_list', model: 'fix.cash.shift',
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
    cols: ['name', 'sale_date', 'branch_id', 'product_id', 'quantity', 'total', 'payment_method', 'transaction_ref', 'tendered_amount', 'state'],
    stateField: 'state',
    /* the payment is taken on the Counter Payment form; confirming puts cash
     * in the open drawer and issues the Mushak-6.3 number (FR-FRD-016) */
    actions: [{ m: 'action_confirm', l: 'Confirm Payment & Issue Receipt', states: ['draft'] }] },
  'M04-shift': { kind: 'table_report', module: 'M04', report: 'daily_cash', period: false },
  'M04-banking': { kind: 'table_report', module: 'M04', report: 'variance_register', period: false },
  /* a sale is rung up at the counter (FR-FRD-012): "+ New" opens Counter Sale */
  'M04-sales': { kind: 'model_list', model: 'fix.counter.sale',
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
  /* M04 sub-module audit 2026-11-13: the checklists are RECORDED
   * (fix.branch.checklist, FR-FRD-020/024). The per-shift cash-close pack that
   * stood in for them keeps its own name under Shift Operations. */
  'M04-checklists': { kind: 'model_list', model: 'fix.branch.checklist',
    cols: ['name', 'branch_id', 'checklist_type', 'checklist_date', 'open_item_count', 'state', 'completed_by_id', 'completed_at'],
    stateField: 'state',
    empty: 'No checklist recorded yet. Start the day with + New: the opening checklist comes with its items.',
    actions: [{ m: 'action_complete', l: 'Sign Off Checklist', states: ['draft'] }] },
  'M04-shift-close': { kind: 'table_report', module: 'M04', report: 'shift_checklists', title: 'Shift Cash-Close Status', period: false },
  'M04-dashboard': { kind: 'table_report', module: 'M04', report: 'branch_league', period: false },
  'M04-receipts': { kind: 'model_list', model: 'fix.counter.sale', create: false,
    cols: ['name', 'sale_date', 'customer_id', 'product_id', 'total', 'payment_method', 'state'],
    domain: [['state', '=', 'confirmed']] },

  /* ===== service data-entry forms (registry names) ===== */
  'M04-form-token': {
    kind: 'model_form',
    model: 'fix.token.queue',
    title: "Token Issue",
    newLabel: 'Issue Queue Token',
    back: 'M04-queue',
    status: { field: 'state', labels: { waiting: "Waiting", called: "Called", serving: "Serving", completed: "Completed", no_show: "No Show", cancelled: "Cancelled" } },
    tabs: [
      { id: 'token', label: '1. Token & Service', bn: '১. টোকেন ও সেবা', icon: '🎫', badge: '8' },
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
          /* FR-FRD-032: the reason for the visit, so the counter is ready */
          { name: 'notes', label: "Reason for Visit" },
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
    newLabel: 'Open a Cash Shift',
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

  /* ===== forms on a record already at the counter (pickRecord) =====
   * M04 sub-module audit 2026-11-13: custody, hand-over and payment are
   * captured on an EXISTING intake or sale, so each form first asks which. */

  /* 3 Device Storage & Retrieval (FR-FRD-011). Registry form 'Device Storage
   * Assignment': it used to open a blank intake under that name. */
  'M04-form-storage-assign': {
    kind: 'model_form',
    model: 'fix.walkin.intake',
    title: 'Device Storage Assignment',
    newLabel: 'Assign Storage Bin',
    back: 'M04-storage',
    status: { field: 'state', labels: { in_progress: "In Progress", handover_pending: "Handover Pending", completed: "Completed" } },
    pickRecord: {
      label: 'Step 1 of 2: choose the device in branch custody',
      note: 'Walk-in intakes whose device is still at the counter (in progress or waiting for hand-over).',
      search: 'Search customer / serial / bin',
      choose: 'Assign a bin to this device',
      cols: ['customer_id', 'device_id', 'device_serial_input', 'storage_bin_code', 'state'],
      domain: [['state', 'in', ['in_progress', 'handover_pending']]],
      empty: 'No device is in branch custody. A device enters custody with a walk-in intake (Counter Workstation).'
    },
    sections: [
      { title: 'Step 2 of 2: Storage Shelf / Bin',
        note: 'Record where the device sits so it is found in seconds at collection. A retained charger, battery or cable goes in a sealed, barcoded accessory bag.',
        fields: [
          { name: 'storage_bin_code', required: true, label: 'Storage Shelf / Bin Code' },
          { name: 'accessory_bag_barcode', label: 'Accessory Bag Barcode' },
          { name: 'customer_id', label: 'Customer', readonly: true },
          { name: 'device_id', label: 'Device', readonly: true },
          { name: 'device_serial_input', label: 'Scanned Serial / IMEI', readonly: true },
          { name: 'state', label: 'Intake State', readonly: true }
        ] }
    ]
  },

  /* 4 Collection & Handover (BRU-FRD-05). Registry form 'Handover (ID
   * verified)': it used to open a blank intake. The proof is written here;
   * Complete Handover on the list checks it and creates the service order. */
  'M04-form-handover': {
    kind: 'model_form',
    model: 'fix.walkin.intake',
    title: 'Handover (ID verified)',
    newLabel: 'Record Handover Proof',
    back: 'M04-handover',
    status: { field: 'state', labels: { in_progress: "In Progress", handover_pending: "Handover Pending", completed: "Completed" } },
    pickRecord: {
      label: 'Step 1 of 2: choose the intake the customer is acknowledging',
      note: 'Intakes not yet handed over. A completed hand-over is frozen.',
      search: 'Search customer / serial',
      choose: 'Record proof for this intake',
      cols: ['customer_id', 'device_id', 'device_serial_input', 'handover_method', 'state'],
      domain: [['state', 'in', ['in_progress', 'handover_pending']]],
      empty: 'No intake is waiting for hand-over. Start one with a walk-in intake (Counter Workstation).'
    },
    sections: [
      { title: "Step 2 of 2: Customer's Signed Acknowledgement",
        note: 'Choose Digital Signature and attach the receipt the customer signed. Then submit the intake for hand-over (Storage Locations) and press Complete Handover on Collection & Handover: it checks this proof, the device and the accessory bag, posts a cash diagnostic fee to the open shift and creates the service order. OTP and staff-witness acknowledgements are not accepted yet.',
        fields: [
          { name: 'handover_method', required: true, label: 'Acknowledgement Method' },
          { name: 'customer_signature_attachment_id', required: true, label: 'Customer Signed Intake Receipt' },
          { name: 'loaner_device_id', label: 'Temporary Loaner Device Issued' },
          { name: 'accessory_bag_barcode', label: 'Accessory Bag Barcode' },
          { name: 'customer_id', label: 'Customer', readonly: true },
          { name: 'device_id', label: 'Device', readonly: true },
          { name: 'handover_acknowledged', label: 'Hand-over Completed', readonly: true },
          { name: 'service_order_id', label: 'Service Order Created', readonly: true },
          { name: 'state', label: 'Intake State', readonly: true }
        ] }
    ]
  },

  /* 7 Payment Capture (FR-FRD-016): the method, reference and tender of a
   * draft sale. Confirm Payment & Issue Receipt on the list then applies the
   * rules (TrxID for non-cash, tender covers the total, open shift for cash). */
  'M04-form-payment': {
    kind: 'model_form',
    model: 'fix.counter.sale',
    title: 'Counter Payment',
    newLabel: 'Take Counter Payment',
    back: 'M04-payments',
    status: { field: 'state', labels: { draft: "Draft", confirmed: "Confirmed", refunded: "Refunded" } },
    pickRecord: {
      label: 'Step 1 of 2: choose the counter sale being paid',
      note: 'Draft counter sales. A confirmed sale is already paid and has its Mushak-6.3 number.',
      search: 'Search sale no. / customer / product',
      choose: 'Take payment for this sale',
      cols: ['name', 'customer_id', 'product_id', 'total', 'payment_method', 'state'],
      domain: [['state', '=', 'draft']],
      empty: 'No counter sale is waiting for payment. Ring the sale up first (Counter Sales).'
    },
    sections: [
      { title: 'Step 2 of 2: Payment Method, Reference & Tender',
        note: 'Cash, card, bKash, Nagad or bank transfer. A non-cash payment needs its TrxID or card slip number; cash needs the amount tendered. Then press Confirm Payment & Issue Receipt on Payment Capture: cash joins the open drawer and the Mushak-6.3 number is issued.',
        fields: [
          { name: 'payment_method', required: true, label: 'Payment Method' },
          { name: 'transaction_ref', label: 'TrxID / Card Slip No.' },
          { name: 'tendered_amount', label: 'Cash Tendered (BDT)' },
          { name: 'change_due', label: 'Change Due (BDT)', readonly: true },
          { name: 'total', label: 'Amount Due (BDT)', readonly: true },
          { name: 'name', label: 'Sale No.', readonly: true },
          { name: 'customer_id', label: 'Customer' },
          { name: 'product_id', label: 'Product', readonly: true },
          { name: 'state', label: 'Sale State', readonly: true }
        ] }
    ]
  },

  /* 10 Branch Admin / 8 Shift Operations (FR-FRD-020/022/024): a new
   * checklist comes with the items its type requires; tick each one or say
   * why not, then Sign Off Checklist on the list. */
  'M04-form-checklist': {
    kind: 'model_form',
    model: 'fix.branch.checklist',
    title: 'Opening / Closing Checklist',
    newLabel: 'Start Opening / Closing Checklist',
    back: 'M04-checklists',
    status: { field: 'state', labels: { draft: "In Progress", completed: "Completed" } },
    lines: { field: 'line_ids', title: 'Checklist Items',
      note: 'Saved with the items the checklist type requires (safety, equipment, stock, cash and staffing at opening; cash, device custody, orders and security at closing). Tick each item or write why it is not done; add a line for anything else.',
      fields: [
        { name: 'area', label: 'Area' },
        { name: 'name', label: 'Item', required: true },
        { name: 'done', label: 'Done' },
        { name: 'note', label: 'Note / Why Not Done' }
      ] },
    sections: [
      { title: 'Branch, Day & Handover Notes',
        note: 'One opening and one closing checklist per branch per day. Signing off stamps who and when, and freezes the checklist.',
        fields: [
          { name: 'branch_id', required: true, label: 'Branch' },
          { name: 'checklist_type', required: true, label: 'Opening or Closing' },
          { name: 'checklist_date', required: true, label: 'Business Day' },
          { name: 'handover_notes', label: 'Handover Notes for the Next Shift', type: 'text' },
          { name: 'open_item_count', label: 'Items Not Done', readonly: true },
          { name: 'state', label: 'Status', readonly: true },
          { name: 'completed_by_id', label: 'Signed Off By', readonly: true },
          { name: 'completed_at', label: 'Signed Off At', readonly: true }
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

/* every M04 form chip is a declared in-workspace form (FORM_CHIPS) */
export const FORM_MODELS = {};

/* the module's "+ New" surface: no generic create — counter work starts
 * from the token issue or the walk-in intake. */
export const CREATE = {};


export const FORM_CHIPS = {
  'M04:Token Issue': 'M04-form-token',
  'M04:Walk-in Intake': 'M04-form-storage',
  'M04:Device Storage Assignment': 'M04-form-storage-assign',
  'M04:Handover (ID verified)': 'M04-form-handover',
  'M04:Shift Open/Close': 'M04-form-shift',
  'M04:Counter Sale': 'M04-form-countersale',
  'M04:Counter Payment': 'M04-form-payment',
  /* the deposit is M50's record: M04 records it with M50's own form */
  'M04:Cash Deposit': 'M50-form-deposit',
  'M04:Opening / Closing Checklist': 'M04-form-checklist',
  'M04:__by_model__': {
    'fix.token.queue': 'M04-form-token',
    'fix.walkin.intake': 'M04-form-storage',
    'fix.cash.shift': 'M04-form-shift',
    'fix.counter.sale': 'M04-form-countersale',
    'fix.branch.checklist': 'M04-form-checklist',
  },
  'M04:__by_screen__': {
    'M04-queue': 'M04-form-token',
    'M04-storage': 'M04-form-storage',
    'M04-drawer': 'M04-form-shift',
    'M04-sales': 'M04-form-countersale',
    'M04-checklists': 'M04-form-checklist',
  }
};
