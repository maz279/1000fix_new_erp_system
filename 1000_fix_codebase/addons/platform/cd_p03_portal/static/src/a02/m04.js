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
    /* A02 ERP audit M04-F17: shortages and overages add up, never net */
    { l: 'Cash Variance Today', m: 'cash_variance_today' },
    { l: 'Shifts Open', m: 'shifts_open' },
    { l: 'Counter Sales MTD', m: 'counter_sales_mtd' }
  ],
  groups: [
    { en: 'Queue & Token', screens: [
      { id: 'M04-queue', en: 'Token & Waiting Display', bn: 'টোকেন ও অপেক্ষার ডিসপ্লে', t: 'd' },
      { id: 'M04-counter', en: 'Counter Workstation', bn: 'কাউন্টার ওয়ার্কস্টেশন', t: 'r' },
      { id: 'M04-priority', en: 'Priority Queue Rules', bn: 'প্রায়োরিটি কিউ রুলস', t: 'g' },
      { id: 'M04-counters', en: 'Service Counters', bn: 'সার্ভিস কাউন্টার', t: 'g' }
    ]},
    { en: 'Device Custody', screens: [
      { id: 'M04-storage', en: 'Devices in Custody', bn: 'হেফাজতে থাকা ডিভাইস', t: 'g' },
      { id: 'M04-locations', en: 'Storage Locations', bn: 'স্টোরেজ অবস্থান', t: 'g' },
      { id: 'M04-collection', en: 'Ready for Collection', bn: 'সংগ্রহের জন্য প্রস্তুত', t: 'g' },
      { id: 'M04-handover', en: 'Intake Hand-off', bn: 'ইনটেক হস্তান্তর', t: 'g' },
      { id: 'M04-uncollected', en: 'Uncollected Devices', bn: 'অসংগৃহীত ডিভাইস', t: 'r' }
    ]},
    { en: 'Cash & Shift', screens: [
      { id: 'M04-drawer', en: 'Cash Drawer', bn: 'ক্যাশ ড্রয়ার', t: 'g' },
      { id: 'M04-movements', en: 'Drawer Movements', bn: 'ড্রয়ার লেনদেন', t: 'g' },
      { id: 'M04-payments', en: 'Payment Capture (All Methods)', bn: 'পেমেন্ট গ্রহণ', t: 'g' },
      { id: 'M04-idchecks', en: 'High-Value Cash ID Checks', bn: 'উচ্চমূল্যের নগদ পরিচয় যাচাই', t: 'g' },
      { id: 'M04-shift', en: 'Shift Open / Close', bn: 'শিফট খোলা/বন্ধ', t: 'r' },
      { id: 'M04-handovers', en: 'Shift Handovers', bn: 'শিফট হস্তান্তর', t: 'g' },
      { id: 'M04-banking', en: 'Banking Deposits', bn: 'ব্যাংকিং ডিপোজিট', t: 'r' },
      { id: 'M04-deposits', en: 'Deposits Recorded', bn: 'জমাকৃত ডিপোজিট', t: 'g' }
    ]},
    { en: 'Counter Sales', screens: [
      { id: 'M04-sales', en: 'Counter Sales (Parts/Plans)', bn: 'কাউন্টার বিক্রয়', t: 'g' },
      { id: 'M04-baskets', en: 'Multi-Item Baskets', bn: 'একাধিক পণ্যের বাস্কেট', t: 'g' },
      { id: 'M04-kiosk', en: 'Kiosk Mode', bn: 'কিয়স্ক মোড', t: 'r' }
    ]},
    { en: 'Branch Ops', screens: [
      { id: 'M04-checklists', en: 'Open/Close Checklists', bn: 'খোলা/বন্ধ চেকলিস্ট', t: 'g' },
      { id: 'M04-dashboard', en: 'Branch Ops Dashboard', bn: 'ব্রাঞ্চ অপস ড্যাশবোর্ড', t: 'r' },
      { id: 'M04-announcements', en: 'Branch Announcements', bn: 'শাখা ঘোষণা', t: 'g' },
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
  /* M04 build 2026-11-13: counters and priority rules, storage locations,
   * the drawer movement ledger, ID-checked device release and announcements. */
  /* M04 capture audit (18 Nov 2026): every page had a "+ New", but four
   * captures the specification gives M04 had no record. Payment Capture could
   * not record the customer's NID and consent for cash above the high-value
   * threshold (FR-FRD-019 P0, BRU-FRD-04/13), and the counter never enforced
   * it; Shift Operations had no handover the incoming team acknowledges
   * (FR-FRD-022, fix.shift.handover); Collection & Handover could not take
   * the customer's rating at the counter (FR-FRD-029); Banking & Deposits
   * captured a deposit it then never listed (test_m04_capture_gaps). */
  forms: ['Token Issue', 'Service Counter', 'Queue Priority Rule', 'Walk-in Intake',
    'Intake Receipt Acknowledgement', 'Device Storage Assignment', 'Storage Location',
    'Handover (ID verified)', 'Shift Open/Close', 'Drawer Cash-Out', 'Petty Cash Voucher',
    'Counter Sale', 'Counter Basket', 'Counter Payment', 'Cash Deposit', 'Opening / Closing Checklist',
    'Branch Announcement', 'High-Value Cash ID Check', 'Shift Handover', 'Customer Rating at Handover'],
  cross: ['M01 walk-in intake', 'M03 collection/delivery', 'M20 receipts', 'M47 branch infrastructure', 'M17 device custody'],
  freg: {
    src: 95,
    sub: [
      ['1', 'Token & Queue', 12, { model: 'fix.token.queue', cols: ['token_display', 'service_type', 'priority_level', 'state', 'issued_at'], screens: ['M04-queue', 'M04-priority', 'M04-counters'], reports: ['Token Wait-Time Distribution'], forms: ['Token Issue', 'Queue Priority Rule', 'Service Counter'] }],
      ['2', 'Counter Workstation', 14, { model: 'fix.walkin.intake', cols: ['customer_id', 'device_serial_input', 'symptom_category', 'state', 'intake_start'], screens: ['M04-counter', 'M04-handover'], reports: ['Token Wait-Time Distribution'], forms: ['Walk-in Intake', 'Intake Receipt Acknowledgement'], create: 'M04-form-storage' }],
      /* 3 FR-FRD-011: the shelf / bin of a device already in custody */
      ['3', 'Device Storage & Retrieval', 10, { model: 'fix.walkin.intake', cols: ['customer_id', 'device_id', 'storage_location_id', 'state', 'service_order_id'], screens: ['M04-storage', 'M04-shelved', 'M04-locations', 'M04-uncollected'], reports: ['Uncollected Device Ageing'], forms: ['Device Storage Assignment', 'Service Order Shelf', 'Storage Location'], create: 'M04-form-storage-assign' }],
      /* 4 FR-FRD-010 / BRU-FRD-05: a ready device released to its collector,
       * whose identity is checked (the intake hand-off is Counter Workstation's) */
      ['4', 'Collection & Handover', 9, { model: 'fix.service.order', cols: ['name', 'customer_id', 'recipient_name', 'collector_is_customer', 'collector_id_verified_by', 'delivery_otp_verified', 'state'], screens: ['M04-collection', 'M04-uncollected'], reports: ['Uncollected Device Ageing'], forms: ['Handover (ID verified)', 'Customer Rating at Handover'], create: 'M04-form-release', domain: [['state', 'in', ['ready', 'delivered']]] }],
      ['5', 'Counter Sales', 8, { model: 'fix.counter.sale', cols: ['name', 'sale_date', 'product_id', 'total', 'state'], screens: ['M04-sales', 'M04-baskets', 'M04-kiosk'], reports: ['Counter Sales by Category'], forms: ['Counter Sale', 'Counter Basket'] }],
      ['6', 'Cash Drawer', 12, { model: 'fix.cash.shift', cols: ['shift_date', 'opening_float', 'expected_closing', 'closing_counted', 'variance'], screens: ['M04-drawer', 'M04-movements', 'M04-books'], reports: ['Branch Daily Cash Summary', 'Shift Variance Register', 'Front-Desk Money Not Yet in the Books'], forms: ['Shift Open/Close', 'Drawer Cash-Out', 'Petty Cash Voucher'] }],
      /* 7 FR-FRD-016: the method, reference and tender of a rung-up sale */
      ['7', 'Payment Capture', 9, { model: 'fix.counter.sale', cols: ['name', 'customer_id', 'total', 'payment_method', 'transaction_ref'], screens: ['M04-payments', 'M04-idchecks', 'M04-receipts', 'M04-books'], reports: ['Branch Daily Cash Summary', 'Front-Desk Money Not Yet in the Books'], forms: ['Counter Payment', 'High-Value Cash ID Check'], create: 'M04-form-payment' }],
      /* 8 FR-FRD-014/022: the outgoing shift hands over to the incoming team,
       * who acknowledge it (the drawer itself is Cash Drawer's) */
      ['8', 'Shift Operations', 10, { model: 'fix.shift.handover', cols: ['name', 'branch_id', 'from_shift_id', 'to_operator_id', 'state', 'handed_over_at', 'acknowledged_by_id'], screens: ['M04-handovers', 'M04-shift', 'M04-shift-close', 'M04-checklists'], reports: ['Branch Daily Cash Summary'], forms: ['Shift Handover', 'Shift Open/Close', 'Opening / Closing Checklist'], create: 'M04-form-shift-handover' }],
      /* 9 FR-FRD-018: M04 records the deposit (M50's form, M50 reconciles it) */
      ['9', 'Banking & Deposits', 5, { model: 'fix.cash.deposit', cols: ['name', 'branch_id', 'business_date', 'amount', 'state'], screens: ['M04-deposits', 'M04-banking'], reports: ['Shift Variance Register'], forms: ['Cash Deposit'], create: 'M50-form-deposit' }],
      /* 10 FR-FRD-020/022/024: the branch's daily checklists and handover
       * notes. The branch itself is M30's configuration (spec section 3.2). */
      ['10', 'Branch Admin', 6, { model: 'fix.branch.checklist', cols: ['name', 'branch_id', 'checklist_type', 'checklist_date', 'open_item_count', 'state', 'completed_by_id'], screens: ['M04-checklists', 'M04-announcements', 'M04-dashboard'], reports: ['Branch Comparison League'], forms: ['Opening / Closing Checklist', 'Branch Announcement'] }]
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
      /* A02 ERP audit M04-F12: the next waiting customer by priority lane,
       * then issue time (BRU-FRD-07); press it on any token of the branch */
      { m: 'action_call_next', l: 'Call Next by Priority' },
      { m: 'action_call', l: 'Call / Re-call Token' },
      { m: 'action_serving', l: 'Start Serving' },
      { m: 'action_complete', l: 'Complete' },
      { m: 'action_no_show', l: 'Mark No-Show' },
      { m: 'action_cancel', l: 'Cancel Token' },
      /* A02 audit M04-9: the wait SLA also runs on a 5-minute cron */
      { m: 'action_evaluate_wait_sla', l: 'Check Wait SLA' }
    ] },
  'M04-counter': { kind: 'table_report', module: 'M04', report: 'wait_distribution', period: false },
  /* M04 build 2026-11-13: the RULES (BRU-FRD-07). This screen listed the
   * waiting tokens under the rules' name; those are on Token & Waiting Display. */
  'M04-priority': { kind: 'model_list', model: 'fix.queue.priority.rule',
    cols: ['sequence', 'name', 'branch_id', 'corporate_only', 'partner_category_id', 'loyalty_tier_name', 'service_type', 'priority_level', 'active'],
    empty: 'No priority rule yet: every token stays in the lane the agent picks. Add a rule with + New.' },
  'M04-counters': { kind: 'model_list', model: 'fix.queue.counter',
    cols: ['branch_id', 'number', 'label', 'can_intake', 'can_collect', 'can_pay', 'can_enquiry', 'can_corporate', 'can_technical', 'agent_id', 'active'],
    empty: 'No counter is set up yet. Add each branch counter and what it serves with + New.',
    /* A02 ERP audit M04-F12 (BRU-FRD-07): today's waiting tokens the counter
     * serves, highest priority lane first, then first issued */
    actions: [{ m: 'action_call_next', l: 'Call Next Customer' }] },
  'M04-storage': { kind: 'model_list', model: 'fix.walkin.intake', create: false,
    cols: ['customer_id', 'device_serial_input', 'storage_location_id', 'fault_description', 'state', 'intake_start', 'intake_duration_seconds', 'service_order_id'],
    stateField: 'state',
    actions: [{ m: 'action_submit_for_handover', l: 'Submit for Handover' }] },
  'M04-handover': { kind: 'model_list', model: 'fix.walkin.intake', create: false,
    cols: ['customer_id', 'device_id', 'state', 'handover_method', 'handover_acknowledged', 'handover_acknowledged_at', 'service_order_id'],
    domain: [['state', 'in', ['handover_pending', 'completed']]],
    stateField: 'state',
    actions: [{ m: 'action_complete_handover', l: 'Complete Handover' }] },
  /* A02 pass 2 M04-05: the service orders on a shelf at the branch */
  'M04-shelved': { kind: 'model_list', model: 'fix.service.order', create: false,
    title: 'Devices on the Shelves',
    cols: ['name', 'customer_id', 'device_id', 'branch_id', 'storage_location_id', 'state'],
    domain: [['storage_location_id', '!=', false], ['state', 'not in', ['delivered', 'closed', 'cancelled']]],
    stateField: 'state',
    empty: 'No service order is on a shelf. The intake\'s shelf passes to its order at the hand-off; Service Order Shelf puts a Ready device on one.' },
  'M04-locations': { kind: 'model_list', model: 'fix.storage.location',
    cols: ['branch_id', 'code', 'zone', 'shelf', 'bin', 'secure', 'occupied', 'occupied_by_id', 'occupied_by_order_id', 'active'],
    empty: 'No storage location is registered yet. Add the shelves and bins of each branch with + New.' },
  /* FR-FRD-010: ready devices; the release needs the customer's OTP and, for
   * a third-party collector, an identity check (BRU-FRD-05) */
  'M04-collection': { kind: 'model_list', model: 'fix.service.order', create: false,
    cols: ['name', 'customer_id', 'device_id', 'branch_id', 'storage_location_id', 'recipient_name', 'collector_is_customer', 'delivery_otp_verified', 'collector_id_verified_by', 'state'],
    domain: [['state', '=', 'ready']],
    stateField: 'state',
    empty: 'No device is ready for collection.',
    actions: [
      { m: 'action_send_delivery_otp', l: 'Send Handover OTP', states: ['ready'] },
      { m: 'action_verify_delivery_otp', l: 'Verify Handover OTP', states: ['ready'], ask: 'Code from the customer\'s phone', kwarg: 'code' },
      { m: 'action_verify_collector_id', l: 'Verify Collector ID', states: ['ready'] },
      { m: 'action_deliver', l: 'Release Device', states: ['ready'] },
      /* A02 pass 2 M04-06: the customer rates on their own page (tablet / phone) */
      { m: 'action_request_counter_rating', l: 'Ask the Customer to Rate', states: ['ready', 'delivered'] }
    ] },
  'M04-uncollected': { kind: 'table_report', module: 'M04', report: 'uncollected_ageing', period: false },
  /* a drawer starts with a counted float (FR-FRD-014): "+ New" opens a shift */
  'M04-drawer': { kind: 'model_list', model: 'fix.cash.shift',
    cols: ['shift_date', 'shift_type', 'branch_id', 'operator_id', 'opening_float', 'proposed_float', 'cash_payments', 'cash_refunds', 'cash_advances', 'expected_closing', 'closing_counted', 'variance', 'variance_posting_state', 'state'],
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
      { m: 'action_reconcile', l: 'Reconcile' },
      /* A02 pass 2 M04-03: a float other than the last close's cash needs a
       * Branch Manager who does not run the drawer */
      { m: 'action_approve_opening_float', l: 'Approve Opening Float', states: ['open'] },
      /* A02 pass 2 X5-20: the variance posts when the count is confirmed */
      { m: 'action_retry_variance_posting', l: 'Retry Variance GL Posting', states: ['closed', 'reconciled', 'discrepancy'] }
    ] },
  /* FR-FRD-015: every movement of the drawer; cash-outs are recorded here */
  'M04-movements': { kind: 'model_list', model: 'fix.cash.movement',
    cols: ['name', 'shift_id', 'branch_id', 'movement_type', 'direction', 'amount', 'reason', 'employee_id', 'reference', 'state', 'posting_state', 'recorded_by_id', 'approved_by_id', 'posted_at'],
    stateField: 'state',
    empty: 'No drawer movement yet. Sales, refunds and settlements write theirs; a cash-out is recorded with + New.',
    actions: [
      { m: 'action_approve', l: 'Approve Cash-Out', states: ['draft'] },
      { m: 'action_post', l: 'Post Cash-Out', states: ['draft', 'approved'] },
      { m: 'action_cancel', l: 'Cancel', states: ['draft', 'approved'] },
      /* A02 pass 2 X5-20: a cash-out whose account did not resolve is pending */
      { m: 'action_retry_posting', l: 'Retry GL Posting', states: ['posted'] }
    ] },
  'M04-payments': { kind: 'model_list', model: 'fix.counter.sale', create: false,
    cols: ['name', 'sale_date', 'branch_id', 'product_id', 'quantity', 'total', 'payment_method', 'transaction_ref', 'tendered_amount', 'state'],
    stateField: 'state',
    /* the payment is taken on the Counter Payment form; confirming puts cash
     * in the open drawer and issues the Mushak-6.3 number (FR-FRD-016) */
    actions: [{ m: 'action_confirm', l: 'Confirm Payment & Issue Receipt', states: ['draft'] }] },
  'M04-shift': { kind: 'table_report', module: 'M04', report: 'daily_cash', period: false },
  /* A02 pass 2 X5-20: what the counter took that the books still owe, and why */
  'M04-books': { kind: 'table_report', module: 'M04', report: 'books_pending', period: false },
  /* FR-FRD-018: the branch deposits M04 records with M50's form; M50
   * dispatches and reconciles them (Cash-in-Transit) */
  'M04-deposits': { kind: 'model_list', model: 'fix.cash.deposit',
    cols: ['name', 'branch_id', 'business_date', 'amount', 'slip_no', 'state', 'credited_amount', 'variance_amount'],
    stateField: 'state',
    empty: 'No deposit recorded yet. Record each banking with + New; M50 dispatches and reconciles it.' },
  /* FR-FRD-022: what the outgoing shift handed over, and who acknowledged it */
  'M04-handovers': { kind: 'model_list', model: 'fix.shift.handover',
    cols: ['name', 'branch_id', 'from_shift_id', 'from_operator_id', 'to_operator_id', 'state', 'handed_over_by_id', 'handed_over_at', 'acknowledged_by_id', 'acknowledged_at'],
    stateField: 'state',
    empty: 'No handover yet. The outgoing shift writes one with + New; the incoming team member acknowledges it here.',
    actions: [{ m: 'action_acknowledge', l: 'I Have Read This Handover', states: ['handed_over'] }] },
  /* FR-FRD-019 / BRU-FRD-04: the NID and consent behind each high-value cash
   * receipt. A check is evidence: never edited, never deleted. */
  'M04-idchecks': { kind: 'model_list', model: 'fix.cash.id.check',
    cols: ['name', 'branch_id', 'sale_id', 'basket_id', 'partner_id', 'amount', 'threshold', 'nid_last4', 'notice_version_id', 'recorded_by_id', 'recorded_at'],
    empty: 'No high-value cash receipt yet. A cash sale or basket above the threshold is confirmed only after its ID check is recorded with + New.' },
  'M04-banking': { kind: 'table_report', module: 'M04', report: 'variance_register', period: false },
  /* a sale is rung up at the counter (FR-FRD-012): "+ New" opens Counter Sale */
  'M04-sales': { kind: 'model_list', model: 'fix.counter.sale',
    cols: ['name', 'sale_date', 'product_id', 'quantity', 'unit_price', 'total', 'payment_method', 'state', 'refund_state', 'posting_state', 'sold_by'],
    stateField: 'state',
    /* A02 audit M04-5: a price below list and a refund need a manager who
     * did not sell; the refund leaves the drawer that is open now.
     * A02 audit B1: both are decided in the approver's M63 inbox; a refund
     * request routes itself. */
    actions: [
      { m: 'action_confirm', l: 'Confirm Sale' },
      { m: 'action_request_approval', l: 'Request Price Approval', ask: 'Why the price is below list', kwarg: 'justification' },
      { m: 'action_request_refund', l: 'Request Refund', ask: 'Reason (defective / wrong_item / customer_cancelled / duplicate / other): note', kwarg: 'reason' },
      { m: 'action_recall_approval', l: 'Recall Approval Request' },
      /* BRU-FRD-10: a protection plan / membership is sold once its terms are accepted */
      { m: 'action_accept_terms', l: 'Customer Accepted the Terms', states: ['draft'] },
      /* A02 ERP audit X-17: the customer's receipt (statutory Mushak 6.3 once posted) */
      { m: 'action_print_receipt', l: 'Print Receipt (A4)', states: ['confirmed', 'refunded'] },
      { m: 'action_print_receipt_80', l: 'Print Receipt (80 mm)', states: ['confirmed', 'refunded'] },
      /* A02 pass 2 X5-20: a sale / refund whose posting is pending */
      { m: 'action_retry_posting', l: 'Retry Posting to Books', states: ['confirmed', 'refunded'] }
    ] },
  'M04-kiosk': { kind: 'table_report', module: 'M04', report: 'sales_category', period: false },
  /* quote-to-cash 2026-11-13: a customer buying several items pays once.
   * Confirming raises one counter sale per item (each posted, priced and
   * approved as a single sale); any refusal confirms none. */
  'M04-baskets': { kind: 'model_list', model: 'fix.counter.basket',
    cols: ['name', 'branch_id', 'customer_id', 'payment_method_id', 'transaction_ref', 'total', 'change_due', 'state'],
    stateField: 'state',
    empty: 'No basket yet. + New rings up several items for one customer and one payment.',
    actions: [{ m: 'action_confirm', l: 'Confirm Basket & Issue Receipts', states: ['draft'] }] },
  /* M04 sub-module audit 2026-11-13: the checklists are RECORDED
   * (fix.branch.checklist, FR-FRD-020/024). The per-shift cash-close pack that
   * stood in for them keeps its own name under Shift Operations. */
  'M04-checklists': { kind: 'model_list', model: 'fix.branch.checklist',
    cols: ['name', 'branch_id', 'checklist_type', 'checklist_date', 'open_item_count', 'state', 'completed_by_id', 'completed_at'],
    stateField: 'state',
    empty: 'No checklist recorded yet. Start the day with + New: the opening checklist comes with its items.',
    actions: [{ m: 'action_complete', l: 'Sign Off Checklist', states: ['draft'] }] },
  'M04-shift-close': { kind: 'table_report', module: 'M04', report: 'shift_checklists', title: 'Shift Cash-Close Status', period: false },
  'M04-announcements': { kind: 'model_list', model: 'fix.branch.announcement',
    cols: ['name', 'kind', 'valid_from', 'valid_until', 'state', 'published_by_id', 'ack_count', 'is_current'],
    stateField: 'state',
    empty: 'No announcement yet. A Branch Manager drafts one with + New and publishes it.',
    actions: [
      { m: 'action_publish', l: 'Publish', states: ['draft'] },
      { m: 'action_acknowledge', l: 'I Have Read This', states: ['published'] },
      { m: 'action_withdraw', l: 'Withdraw', states: ['published'] }
    ] },
  'M04-dashboard': { kind: 'table_report', module: 'M04', report: 'branch_league', period: false },
  'M04-receipts': { kind: 'model_list', model: 'fix.counter.sale', create: false,
    cols: ['name', 'sale_date', 'customer_id', 'product_id', 'total', 'payment_method', 'state'],
    domain: [['state', '=', 'confirmed']],
    stateField: 'state',
    actions: [
      { m: 'action_print_receipt', l: 'Print Receipt (A4)' },
      { m: 'action_print_receipt_80', l: 'Print Receipt (80 mm)' }
    ] },

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
          { name: 'counter_id', label: "Assigned Service Counter" },
          { name: 'service_order_id', label: "Linked Service Order", readonly: true }
        ] },
      { tab: 'wait', title: "15-Minute Wait SLA & Supervisor Escalation (FLAW-04.1)",
        fields: [
          { name: 'priority_level', label: "Queue Priority Tier" },
          { name: 'priority_rule_id', label: "Placed By Priority Rule", readonly: true },
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
      { id: 'shift', label: '1. Shift Context', bn: '১. শিফট তথ্য', icon: '🏢', badge: '8' },
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
          /* A02 pass 2 M04-03: left empty, the drawer opens with what the last
           * close left; a different float needs a Branch Manager's approval */
          { name: 'opening_float', label: "Opening Cash Float (BDT) — empty: the last close's cash" },
          { name: 'proposed_float', label: "Proposed Float (last close less deposits)", readonly: true },
          { name: 'float_variance', label: "Float Difference (BDT)", readonly: true },
          { name: 'float_approved_by_id', label: "Float Difference Approved By", readonly: true }
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
          /* A02 pass 2 M04-04: posted when the count is confirmed */
          { name: 'variance_posting_state', label: "Variance in GL", readonly: true },
          { name: 'variance_move_id', label: "Variance GL Entry", readonly: true },
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
          /* A02 ERP audit X-04: the statutory Mushak 6.3 and the VAT the books
           * hold come from the posting (cd_front_desk_finance: VAT register
           * number, M51 product rate). The counter's own reference and flat-rate
           * split are labelled for what they are: internal and an estimate. */
          { name: 'mushak_no', label: "NBR Mushak 6.3 No. (statutory)", readonly: true },
          { name: 'posting_state', label: "Posted to Books", readonly: true },
          { name: 'vat_taxable_amount', label: "Taxable Value per Mushak 6.3 (BDT)", readonly: true },
          { name: 'vat_output_amount', label: "VAT per Mushak 6.3 (BDT)", readonly: true },
          { name: 'vat_treatment_summary', label: "VAT Treatment (M51)", readonly: true },
          { name: 'mushak_63_ref', label: "Counter Receipt Ref (internal, not the NBR number)", readonly: true },
          { name: 'vat_rate', label: "Counter VAT Rate (estimate, %)", readonly: true },
          { name: 'amount_untaxed', label: "Net of VAT (estimate, BDT)", readonly: true },
          { name: 'vat_amount', label: "VAT (estimate, BDT)", readonly: true },
          /* BRU-FRD-10 */
          { name: 'terms_required', label: "Terms Acceptance Required", readonly: true },
          { name: 'terms_accepted_partner_id', label: "Terms Accepted By (Customer)", readonly: true },
          { name: 'terms_accepted_at', label: "Terms Accepted At", readonly: true },
          { name: 'approval_state', label: "Approval (M63)", readonly: true },
          { name: 'total', label: "Grand Total (BDT)", readonly: true },
          { name: 'state', label: "Transaction State", readonly: true },
          { name: 'refund_state', label: "Refund Status", readonly: true },
          { name: 'refund_reason_code', label: "Refund Reason", readonly: true },
          { name: 'refund_approved_by', label: "Refund Approved By", readonly: true }
        ] }
    ]
  },

  'M04-form-basket': {
    kind: 'model_form',
    model: 'fix.counter.basket',
    title: 'Counter Basket',
    newLabel: 'Ring Up a Basket',
    back: 'M04-baskets',
    status: { field: 'state', labels: { draft: 'Draft', confirmed: 'Confirmed' } },
    lines: {
      field: 'line_ids',
      tab: 'items',
      title: 'Items',
      note: 'One line per item. Leave the unit price empty to charge the list price; a price below list needs a manager approval on its counter sale.',
      fields: [
        { name: 'product_id', label: 'Item', required: true },
        { name: 'quantity', label: 'Qty' },
        { name: 'unit_price', label: 'Unit Price (BDT)' },
        { name: 'subtotal', label: 'Amount (BDT)', readonly: true }
      ]
    },
    /* A02 pass 2 X5-19: the counter sales the basket raised (each one's
     * Mushak 6.3 and posting), read-only */
    grids: [
      {
        field: 'sale_ids', tab: 'sales', title: 'Counter Sales Raised', readonlyGrid: true,
        empty: 'No counter sale yet: confirming the basket raises one per item.',
        fields: [
          { name: 'name', label: 'Sale', readonly: true },
          { name: 'product_id', label: 'Item', readonly: true },
          { name: 'quantity', label: 'Qty', readonly: true },
          { name: 'total', label: 'Amount (BDT)', readonly: true },
          { name: 'state', label: 'Status', readonly: true },
          { name: 'posting_state', label: 'Books', readonly: true }
        ]
      }
    ],
    tabs: [
      { id: 'items', label: '1. Customer & Items', bn: '১. গ্রাহক ও পণ্য', icon: '🛒', badge: '4' },
      { id: 'pay', label: '2. Payment', bn: '২. পেমেন্ট', icon: '💳', badge: '6' },
      { id: 'sales', label: '3. Counter Sales Raised', bn: '৩. বিক্রয় রসিদ', icon: '🧾' }
    ],
    sections: [
      { tab: 'items', title: 'Customer & Branch', note: 'The branch decides the operating unit and, for cash, the open drawer.',
        fields: [
          { name: 'name', label: 'Basket No.', readonly: true },
          { name: 'branch_id', label: 'Branch', required: true },
          { name: 'customer_id', label: 'Customer' }
        ] },
      { tab: 'pay', title: 'One Payment for the Whole Basket', note: 'bKash, Nagad, Rocket, Upay and card need the TrxID / slip number. A cash basket above the high-value threshold (BDT 50,000) needs its High-Value Cash ID Check before it is confirmed.',
        fields: [
          /* the tenders a counter sale confirms (cash, the four wallets, card POS) */
          { name: 'payment_method_id', label: 'Paid By', required: true, domain: [['for_counter', '=', true], ['receipt_method', '!=', 'cheque']] },
          { name: 'transaction_ref', label: 'TrxID / Card Slip No.' },
          { name: 'tendered_amount', label: 'Cash Tendered (BDT)' },
          { name: 'total', label: 'Total (BDT)', readonly: true },
          { name: 'change_due', label: 'Change Due (BDT)', readonly: true },
          { name: 'state', label: 'Status', readonly: true }
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
        note: 'Choose the registered location that holds the device, so it is found in seconds at collection. A location holds one device, and a device is in one location (BRU-FRD-06). A retained charger, battery or cable goes in a sealed, barcoded accessory bag.',
        fields: [
          { name: 'storage_location_id', required: true, label: 'Storage Location (free bins of this branch)' },
          { name: 'storage_bin_code', label: 'Bin Code', readonly: true },
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
    title: 'Intake Receipt Acknowledgement',
    newLabel: 'Record Intake Receipt Proof',
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
        note: 'Cash, card, bKash, Nagad or bank transfer. A non-cash payment needs its TrxID or card slip number; cash needs the amount tendered. Then press Confirm Payment & Issue Receipt on Payment Capture: cash joins the open drawer and the Mushak-6.3 number is issued. Cash above the high-value threshold (BDT 50,000) is confirmed only after its High-Value Cash ID Check.',
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

  /* ===== M04 build 2026-11-13: the five capabilities the spec gave M04
   * that had no record behind them ===== */

  /* FR-FRD-007/027: a branch counter and what it serves */
  'M04-form-counter': {
    kind: 'model_form',
    model: 'fix.queue.counter',
    title: 'Service Counter',
    newLabel: 'Add a Service Counter',
    back: 'M04-counters',
    sections: [
      { title: 'Counter & What It Serves',
        note: 'A token is routed only to a counter that serves its service type (FR-FRD-007). Setting up counters needs a Branch Manager.',
        fields: [
          { name: 'branch_id', required: true, label: 'Branch' },
          { name: 'number', required: true, label: 'Counter No.' },
          { name: 'label', label: 'Counter Name (shown on the display)' },
          { name: 'can_intake', label: 'Serves Device Drop-off / Intake' },
          { name: 'can_collect', label: 'Serves Collection / Pick-up' },
          { name: 'can_pay', label: 'Serves Payment' },
          { name: 'can_enquiry', label: 'Serves Enquiry' },
          { name: 'can_corporate', label: 'Corporate Accounts Desk' },
          { name: 'can_technical', label: 'Technical Desk' },
          { name: 'agent_id', label: 'Staffed By' },
          { name: 'active', label: 'Open' }
        ] }
    ]
  },

  /* BRU-FRD-07: who goes into which priority lane, automatically */
  'M04-form-priority-rule': {
    kind: 'model_form',
    model: 'fix.queue.priority.rule',
    title: 'Queue Priority Rule',
    newLabel: 'Add a Priority Rule',
    back: 'M04-priority',
    sections: [
      { title: 'When a Token Matches, Place It In',
        note: 'Checked in sequence order when a token is issued; the first rule that matches places the token, and a rule only ever raises the lane the agent chose. Leave the branch empty to apply everywhere. A loyalty tier is matched by its exact name (e.g. Gold).',
        fields: [
          { name: 'name', required: true, label: 'Rule Name' },
          { name: 'sequence', label: 'Order Checked' },
          { name: 'branch_id', label: 'Branch (empty = all branches)' },
          { name: 'corporate_only', label: 'Customer is a Company / Corporate Account' },
          { name: 'partner_category_id', label: 'Customer Tag (e.g. Senior Citizen)' },
          { name: 'loyalty_tier_name', label: 'Loyalty Tier Name (e.g. Gold, Diamond)' },
          { name: 'service_type', label: 'Service Type (empty = any)' },
          { name: 'priority_level', required: true, label: 'Place In Lane' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },

  /* FR-FRD-011 / T-09: a shelf or bin that holds one device */
  'M04-form-location': {
    kind: 'model_form',
    model: 'fix.storage.location',
    title: 'Storage Location',
    newLabel: 'Register a Storage Location',
    back: 'M04-locations',
    sections: [
      { title: 'Shelf / Bin',
        note: 'Register each place a customer device can be stored, with the code printed on its label. A location holds one device at a time and is free again when the intake leaves custody.',
        fields: [
          { name: 'branch_id', required: true, label: 'Branch' },
          { name: 'code', required: true, label: 'Location Code (as on the label)' },
          { name: 'zone', label: 'Zone / Room' },
          { name: 'shelf', label: 'Shelf' },
          { name: 'bin', label: 'Bin' },
          { name: 'secure', label: 'Lockable Secure Cabinet' },
          { name: 'active', label: 'In Use' },
          { name: 'occupied', label: 'Occupied Now', readonly: true },
          { name: 'occupied_by_id', label: 'Holds the Device of Intake', readonly: true }
        ] }
    ]
  },

  /* FR-FRD-015 / BRU-FRD-09: cash leaving the drawer, with its reason */
  'M04-form-movement': {
    kind: 'model_form',
    model: 'fix.cash.movement',
    title: 'Drawer Cash-Out',
    newLabel: 'Record Cash-Out',
    back: 'M04-movements',
    status: { field: 'state', labels: { draft: 'Recorded', approved: 'Approved', posted: 'Posted', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Cash Leaving the Drawer',
        note: 'Record cash taken out of an OPEN drawer: a safe drop, a small expense paid from the till or a staff advance. Post Cash-Out on Drawer Movements lowers the expected closing and books it (A02 pass 2, D2): a petty expense to the expense account of its category, a staff advance to the advance account of the staff member, a safe drop to Cash in Safe, each against drawer cash. A staff advance, and a petty expense above BDT 500, need a Branch Manager who did not record it. Sales, refunds and settlements write their own movements. Expenses from the branch petty-cash fund are M50 imprest vouchers.',
        fields: [
          { name: 'shift_id', required: true, label: 'Open Cash Shift' },
          { name: 'movement_type', required: true, label: 'Kind of Cash-Out' },
          { name: 'amount', required: true, label: 'Amount (BDT)' },
          { name: 'reason', required: true, label: 'Reason / Payee' },
          { name: 'expense_category', label: 'Expense Category (petty expense)' },
          { name: 'employee_id', label: 'Staff Member (staff advance)' },
          { name: 'receipt_attachment_id', label: 'Voucher / Receipt Scan' },
          { name: 'state', label: 'Status', readonly: true },
          { name: 'recorded_by_id', label: 'Recorded By', readonly: true },
          { name: 'approved_by_id', label: 'Approved By', readonly: true },
          { name: 'posted_at', label: 'Posted At', readonly: true },
          { name: 'posting_state', label: 'In GL', readonly: true },
          { name: 'move_id', label: 'GL Entry', readonly: true },
          { name: 'debit_account_id', label: 'Booked To', readonly: true },
          { name: 'posting_note', label: 'Why Not Posted Yet', readonly: true }
        ] }
    ]
  },

  /* A02 pass 2 M04-05 (FR-FRD-011 / BRU-FRD-06): where a service order's
   * device waits at the branch. Required before Ready once the branch has
   * registered its shelves; freed at delivery or cancellation. */
  'M04-form-shelf': {
    kind: 'model_form',
    model: 'fix.service.order',
    title: 'Service Order Shelf',
    newLabel: 'Put a Device on a Shelf',
    back: 'M04-shelved',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the service order whose device is at the branch',
      note: 'Open orders; an order already on a shelf can be moved to another.',
      search: 'Search order / customer / serial',
      choose: 'Shelve this device',
      cols: ['name', 'customer_id', 'device_id', 'branch_id', 'storage_location_id', 'state'],
      domain: [['state', 'not in', ['delivered', 'closed', 'cancelled']], ['service_type', '!=', 'onsite']],
      empty: 'No open order has its device at a branch.'
    },
    sections: [
      { title: 'Step 2 of 2: The Shelf',
        note: 'A location holds one device, and a device is in one location (BRU-FRD-06). It is freed when the device is delivered or the order is cancelled.',
        fields: [
          { name: 'storage_location_id', required: true, label: 'Storage Location', domain: [['occupied', '=', false]] },
          { name: 'name', label: 'Service Order', readonly: true },
          { name: 'customer_id', label: 'Customer', readonly: true },
          { name: 'device_id', label: 'Device', readonly: true },
          { name: 'branch_id', label: 'Branch', readonly: true },
          { name: 'state', label: 'Order State', readonly: true }
        ] }
    ]
  },

  /* FR-FRD-010 / BRU-FRD-05: a ready device released to the person collecting */
  'M04-form-release': {
    kind: 'model_form',
    model: 'fix.service.order',
    title: 'Handover (ID verified)',
    newLabel: 'Release Device to Collector',
    back: 'M04-collection',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the ready order being collected',
      note: 'Service orders that are Ready for collection.',
      search: 'Search order / customer / serial',
      choose: 'Release this device',
      cols: ['name', 'customer_id', 'device_id', 'branch_id', 'state'],
      domain: [['state', '=', 'ready']],
      empty: 'No device is ready for collection.'
    },
    sections: [
      { title: 'Step 2 of 2: Who Is Collecting',
        note: 'If the customer collects in person, the handover OTP from their phone is the identity check. If someone else collects, untick the box and record their relation, the ID document seen (only its last 4 digits, BRU-FRD-14) and the customer\'s authority letter. Then on Ready for Collection: Send and Verify Handover OTP, Verify Collector ID, and Release Device. The release also needs the signed delivery report.',
        fields: [
          { name: 'recipient_name', required: true, label: 'Collector\'s Full Name' },
          { name: 'collector_is_customer', label: 'Customer Collects in Person' },
          { name: 'collector_relation', label: 'Relation to Customer' },
          { name: 'collector_id_type', label: 'ID Document Seen' },
          { name: 'collector_id_last4', label: 'ID No. (last 4 digits only)' },
          { name: 'collector_authority_attachment_id', label: 'Customer\'s Authority Letter' },
          { name: 'service_report_attachment_id', label: 'Signed Delivery Report' },
          { name: 'name', label: 'Service Order', readonly: true },
          { name: 'customer_id', label: 'Customer', readonly: true },
          { name: 'device_id', label: 'Device', readonly: true },
          { name: 'delivery_otp_verified', label: 'Handover OTP Verified', readonly: true },
          { name: 'collector_id_verified_by', label: 'Collector ID Checked By', readonly: true },
          { name: 'collector_id_verified_at', label: 'Collector ID Checked At', readonly: true },
          { name: 'state', label: 'Order State', readonly: true }
        ] }
    ]
  },

  /* FR-FRD-031: a notice, target or procedure change for the counters */
  'M04-form-announcement': {
    kind: 'model_form',
    model: 'fix.branch.announcement',
    title: 'Branch Announcement',
    newLabel: 'Draft an Announcement',
    back: 'M04-announcements',
    status: { field: 'state', labels: { draft: 'Draft', published: 'Published', withdrawn: 'Withdrawn' } },
    sections: [
      { title: 'Announcement',
        note: 'A Branch Manager publishes it from Branch Announcements; counter staff mark it read there. A published announcement is not rewritten: withdraw it and publish a new one.',
        fields: [
          { name: 'name', required: true, label: 'Title' },
          { name: 'kind', required: true, label: 'Kind' },
          { name: 'body', required: true, label: 'Message', type: 'text' },
          { name: 'branch_ids', label: 'Branches (empty = all)' },
          { name: 'valid_from', required: true, label: 'Show From' },
          { name: 'valid_until', label: 'Show Until' },
          { name: 'state', label: 'Status', readonly: true },
          { name: 'published_by_id', label: 'Published By', readonly: true },
          { name: 'ack_count', label: 'Read By (count)', readonly: true }
        ] }
    ]
  },

  /* ===== M04 capture audit 2026-11-18 ===== */

  /* 7 Payment Capture (FR-FRD-019 P0, BRU-FRD-04/13/14): cash above the
   * high-value threshold is confirmed only after this check. The consent is
   * recorded against the notice shown BEFORE the NID is written, and the NID
   * goes to the resident store: the check keeps its last 4 digits only. */
  'M04-form-idcheck': {
    kind: 'model_form',
    model: 'fix.cash.id.check',
    title: 'High-Value Cash ID Check',
    newLabel: 'Record High-Value Cash ID Check',
    back: 'M04-idchecks',
    tabs: [
      { id: 'what', label: '1. Sale & Customer', bn: '১. বিক্রয় ও গ্রাহক', icon: '💵', badge: '3' },
      { id: 'notice', label: '2. Notice & Consent', bn: '২. নোটিশ ও সম্মতি', icon: '📜', badge: '2' },
      { id: 'nid', label: '3. Customer NID', bn: '৩. গ্রাহকের এনআইডি', icon: '🪪', badge: '2' }
    ],
    sections: [
      { tab: 'what', title: 'The Cash Receipt Being Checked',
        note: 'A cash sale or basket above the high-value threshold (M51 statutory parameter, BDT 50,000 today) is confirmed only after this check. Choose the draft sale, or the basket for a multi-item sale.',
        fields: [
          { name: 'sale_id', label: 'Counter Sale (draft, cash)', domain: [['state', '=', 'draft'], ['payment_method', '=', 'cash'], ['basket_id', '=', false]] },
          { name: 'basket_id', label: 'Counter Basket (draft)', domain: [['state', '=', 'draft']] },
          { name: 'partner_id', required: true, label: 'Customer Paying' },
          { name: 'name', label: 'Check No.', readonly: true },
          { name: 'amount', label: 'Cash Received (BDT)', readonly: true },
          { name: 'threshold', label: 'Threshold in Force (BDT)', readonly: true }
        ] },
      { tab: 'notice', title: 'PDPA Transparency Notice (BRU-FRD-13)',
        note: 'Show the customer the notice in force (Bengali and English) and tell them why the NID is needed: the law requires it for cash above the threshold. Tick the box only after they have seen it and agreed. Their consent is recorded against this notice version before the NID is written.',
        fields: [
          { name: 'notice_version_id', required: true, label: 'Notice Version Shown', domain: [['active', '=', true]] },
          { name: 'notice_presented', required: true, label: 'Notice Shown and Customer Agreed' },
          { name: 'consent_id', label: 'Consent Recorded', readonly: true }
        ] },
      { tab: 'nid', title: 'National ID (BRU-FRD-14)',
        note: 'Type the NID from the card, or choose the NID already on file for this customer. The number goes to the Bangladesh-resident store only; this check keeps its last 4 digits. It is never printed beyond the statutory receipt.',
        fields: [
          { name: 'nid_number', label: 'Customer NID (10 or 17 digits)' },
          { name: 'identity_document_id', label: 'Or: NID Already on File', domain: [['document_type', 'in', ['nid_10', 'nid_17']], ['active', '=', true]] },
          { name: 'nid_last4', label: 'NID (last 4 digits)', readonly: true },
          { name: 'recorded_by_id', label: 'Checked By', readonly: true },
          { name: 'recorded_at', label: 'Checked At', readonly: true }
        ] }
    ]
  },

  /* 8 Shift Operations (FR-FRD-022): the outgoing shift's structured note */
  'M04-form-shift-handover': {
    kind: 'model_form',
    model: 'fix.shift.handover',
    title: 'Shift Handover',
    newLabel: 'Write Shift Handover',
    back: 'M04-handovers',
    status: { field: 'state', labels: { handed_over: 'Handed Over', acknowledged: 'Acknowledged' } },
    sections: [
      { title: 'From the Outgoing Shift to the Incoming Team',
        note: 'Write what the next team must know: customers waiting or promised a call, devices due back, cash or stock issues, equipment faults. The incoming team member acknowledges it on Shift Handovers; once acknowledged it is kept as written.',
        fields: [
          { name: 'from_shift_id', required: true, label: 'Outgoing Cash Shift' },
          { name: 'to_operator_id', required: true, label: 'Incoming Team Member' },
          { name: 'to_shift_id', label: 'Incoming Cash Shift (if opened)' },
          { name: 'notes', required: true, label: 'Handover Notes', type: 'text' },
          { name: 'open_items', label: 'Open Items to Act On', type: 'text' },
          { name: 'name', label: 'Handover No.', readonly: true },
          { name: 'branch_id', label: 'Branch', readonly: true },
          { name: 'state', label: 'Status', readonly: true },
          { name: 'handed_over_by_id', label: 'Written By', readonly: true },
          { name: 'acknowledged_by_id', label: 'Acknowledged By', readonly: true },
          { name: 'acknowledged_at', label: 'Acknowledged At', readonly: true }
        ] }
    ]
  },

  /* 4 Collection & Handover (FR-FRD-029, AUT-FRD-12): the customer's quick
   * rating at the counter. M34's survey is sent only when the order closes. */
  'M04-form-rating': {
    kind: 'model_form',
    model: 'fix.service.order',
    title: 'Customer Rating at Handover',
    newLabel: 'Take Customer Rating',
    back: 'M04-collection',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the order being handed over',
      note: 'Orders ready for collection or just released that the customer has not rated yet.',
      search: 'Search order / customer',
      choose: 'Take the rating for this order',
      cols: ['name', 'customer_id', 'device_id', 'branch_id', 'state'],
      domain: [['state', 'in', ['ready', 'delivered']], ['counter_rated_at', '=', false]],
      empty: 'No order is being handed over.'
    },
    sections: [
      { title: 'Step 2 of 2: How Was Today\'s Service?',
        note: 'The customer rates the service themselves (A02 pass 2, M04-06): use Ask the Customer to Rate on Collection & Handover, then open the Customer Rating Page below on the counter tablet or send it to the customer\'s phone. The page takes the stars and a comment once; staff cannot type or change a rating. The fuller survey still goes to the customer when the order closes (M34).',
        fields: [
          { name: 'counter_rating_url', label: 'Customer Rating Page (open on the tablet / phone)', readonly: true },
          { name: 'counter_rating', label: 'Customer Rating (1 to 5)', readonly: true },
          { name: 'counter_feedback', label: 'Customer\'s Comment', readonly: true },
          { name: 'name', label: 'Service Order', readonly: true },
          { name: 'customer_id', label: 'Customer', readonly: true },
          { name: 'counter_rated_by_id', label: 'Rating Asked By', readonly: true },
          { name: 'counter_rating_requested_at', label: 'Rating Asked At', readonly: true },
          { name: 'counter_rated_at', label: 'Rating Given At', readonly: true },
          { name: 'state', label: 'Order State', readonly: true }
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
  'M04:Intake Receipt Acknowledgement': 'M04-form-handover',
  'M04:Handover (ID verified)': 'M04-form-release',
  'M04:Service Counter': 'M04-form-counter',
  'M04:Queue Priority Rule': 'M04-form-priority-rule',
  'M04:Storage Location': 'M04-form-location',
  'M04:Service Order Shelf': 'M04-form-shelf',
  'M04:Drawer Cash-Out': 'M04-form-movement',
  /* the branch petty-cash fund is M50's imprest: M04 records with its form */
  'M04:Petty Cash Voucher': 'M50-form-voucher',
  'M04:Branch Announcement': 'M04-form-announcement',
  'M04:Shift Open/Close': 'M04-form-shift',
  'M04:Counter Sale': 'M04-form-countersale',
  'M04:Counter Basket': 'M04-form-basket',
  'M04:Counter Payment': 'M04-form-payment',
  /* the deposit is M50's record: M04 records it with M50's own form */
  'M04:Cash Deposit': 'M50-form-deposit',
  'M04:Opening / Closing Checklist': 'M04-form-checklist',
  'M04:High-Value Cash ID Check': 'M04-form-idcheck',
  'M04:Shift Handover': 'M04-form-shift-handover',
  'M04:Customer Rating at Handover': 'M04-form-rating',
  'M04:__by_model__': {
    'fix.token.queue': 'M04-form-token',
    'fix.walkin.intake': 'M04-form-storage',
    'fix.cash.shift': 'M04-form-shift',
    'fix.counter.sale': 'M04-form-countersale',
    'fix.counter.basket': 'M04-form-basket',
    'fix.branch.checklist': 'M04-form-checklist',
    'fix.queue.counter': 'M04-form-counter',
    'fix.queue.priority.rule': 'M04-form-priority-rule',
    'fix.storage.location': 'M04-form-location',
    'fix.cash.movement': 'M04-form-movement',
    'fix.branch.announcement': 'M04-form-announcement',
    'fix.cash.id.check': 'M04-form-idcheck',
    'fix.shift.handover': 'M04-form-shift-handover',
  },
  'M04:__by_screen__': {
    'M04-queue': 'M04-form-token',
    'M04-storage': 'M04-form-storage',
    'M04-drawer': 'M04-form-shift',
    'M04-sales': 'M04-form-countersale',
    'M04-baskets': 'M04-form-basket',
    'M04-checklists': 'M04-form-checklist',
    'M04-counters': 'M04-form-counter',
    'M04-priority': 'M04-form-priority-rule',
    'M04-locations': 'M04-form-location',
    'M04-movements': 'M04-form-movement',
    'M04-announcements': 'M04-form-announcement',
    'M04-idchecks': 'M04-form-idcheck',
    'M04-handovers': 'M04-form-shift-handover',
    'M04-deposits': 'M50-form-deposit',
  }
};
