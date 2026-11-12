/** @odoo-module **/
/* A02 · Service Operations — M01 Service Requests & Orders.
 * One file per module (merged into P03_MODULES and the screen maps by
 * p03_modules_meta.js): the registry entry, the in-workspace data screens,
 * built-in report routes, data-entry form chips and the "+ New" surface.
 *
 * Backend: controllers/a02/m01.py (SURFACES, kpis, REPORTS) plus the
 * bespoke /p03/orders/list scopes and /p03/stats in p03_service_order_api.
 * Every screen renders INSIDE the shell from live data — the order grid,
 * operations board, intake console, model lists and table reports. */

export const MODULE = {
  area: 'A02', code: 'M01', en: 'Service Requests & Orders', title: 'M01 · Service Requests & Orders',
  bn: 'সার্ভিস অর্ডার', icon: '📋',
  desc: 'Master record of every service need from 12 intake channels — lifecycle, entitlement, estimates, SLA.',
  kpis: [
    { l: 'Open Orders', m: 'open_orders' },
    { l: 'SLA At-Risk', m: 'sla_at_risk' },
    { l: 'TAT < 24h (IT)', m: 'tat_under_24h', suffix: '%' },
    { l: 'Estimate Conv.', m: 'estimate_conversion', suffix: '%' },
    { l: 'Intake < 3 min', m: 'intake_minutes' },
    { l: 'Rework Rate', m: 'rework_rate', suffix: '%' }
  ],
  groups: [
    { en: 'Intake & Channels', screens: [
      { id: 'M01-board', en: 'Order Operations Board', bn: 'অর্ডার অপারেশন্স বোর্ড', t: 'd' },
      { id: 'M01-all', en: 'All Service Orders', bn: 'সকল সার্ভিস অর্ডার', t: 'g' },
      { id: 'M01-intake', en: 'Omni-Channel Intake', bn: 'অমনি-চ্যানেল ইনটেক', t: 'c' },
      { id: 'M01-channels', en: 'Channel Performance', bn: 'চ্যানেল পারফরম্যান্স', t: 'r' },
      { id: 'M01-hotline', en: 'Hotline 16743 Queue', bn: 'হটলাইন ১৬৭৪৩ কিউ', t: 'g' }
    ]},
    { en: 'Order Lifecycle', screens: [
      { id: 'M01-order', en: 'Service Order Record', bn: 'সার্ভিস অর্ডার নথি', t: 'f' },
      { id: 'M01-types', en: 'Order Types (12)', bn: 'অর্ডার ক্যাটাগরি', t: 'r' },
      { id: 'M01-wip', en: 'WIP & Ageing Analysis', bn: 'চলমান কাজ ও এজিং', t: 'g' },
      { id: 'M01-holds', en: 'Hold Management', bn: 'হোল্ড ব্যবস্থাপনা', t: 'g' },
      { id: 'M01-rework', en: 'Rework Detection', bn: 'রিওয়ার্ক শনাক্তকরণ', t: 'g' }
    ]},
    { en: 'Diagnosis & Estimates', screens: [
      { id: 'M01-templates', en: 'Diagnostic Templates', bn: 'ডায়াগনস্টিক টেমপ্লেট', t: 'g' },
      { id: 'M01-fault', en: 'Fault & Symptom Coding', bn: 'ত্রুটি ও লক্ষণ কোডিং', t: 'g' },
      { id: 'M01-estimates', en: 'Estimates & Approvals', bn: 'অনুমান ও অনুমোদন', t: 'g' },
      { id: 'M01-thresholds', en: 'Approval Thresholds', bn: 'অনুমোদন সীমা', t: 'r' }
    ]},
    { en: 'Entitlement & SLA', screens: [
      { id: 'M01-entitle', en: 'Entitlement Evaluation', bn: 'সুবিধা ও ওয়ারেন্টি যাচাই', t: 'g' },
      { id: 'M01-sla', en: 'SLA Policies & Clocks', bn: 'এসএলএ পলিসি ও কাউন্টডাউন', t: 'g' },
      { id: 'M01-esc', en: 'Escalation Rules', bn: 'এসকেলেশন রুলস', t: 'g' },
      { id: 'M01-sla-rep', en: 'SLA Compliance Report', bn: 'এসএলএ সম্মতি রিপোর্ট', t: 'r' }
    ]},
    { en: 'Quality & Release', screens: [
      { id: 'M01-qc', en: 'QC Checkpoints', bn: 'কিউসি পরিদর্শন', t: 'g' },
      { id: 'M01-reports', en: 'Service Reports', bn: 'সার্ভিস রিপোর্ট ও প্রমাণক', t: 'g' },
      { id: 'M01-rwty', en: 'Repair Warranty Issuance', bn: 'মেরামত ওয়ারেন্টি সার্টিফিকেট', t: 'g' },
      { id: 'M01-events', en: 'Domain Events (Outbox)', bn: 'ডোমেইন ইভেন্ট (আউটবক্স)', t: 'r' }
    ]},
    { en: 'SLA Instances (S9)', bn: 'এসএলএ ইনস্ট্যান্স', screens: [
      { id: 'M01-sla-items', en: 'SLA Items & Targets', bn: 'এসএলএ আইটেম', t: 'g' },
      { id: 'M01-form-sla-item', en: 'SLA Item', bn: 'আইটেম ফর্ম', t: 'f' },
      { id: 'M01-sla-instances', en: 'Live SLA Clocks', bn: 'চলমান এসএলএ ঘড়ি', t: 'g' }
    ]}
  ],
  reports: [
    'Daily Intake by Channel', 'WIP Ageing by Branch', 'SLA Compliance & Escalations',
    'Estimate Conversion Funnel', 'Rework & Repeat-Fault Analysis', 'Order Cycle-Time (TAT) Distribution', 'Uncollected Device Register',
    'Domain Events Published'
  ],
  forms: [
    'New Service Order (12 channels, 34 fields)', 'Diagnostic Estimate Request', 'Hold / Release Reason', 'QC Checklist Inspection'
  , 'SLA Item'],
  cross: [
    'M02 Field Dispatch Handoff', 'M31 Workshop Routing', 'M09 Brand Warranty Check', 'M20 Mushak 6.3 Invoicing', 'M17 Device History'
  ],
  freg: {
    src: 128,
    sub: [
      /* Each sub-module names what implements it: its screens, the reports that
       * measure it, the forms that capture it. Twelve of the thirteen pages
       * showed two empty panels although the module ships 7 reports and 6
       * forms - every one of them is now on the sub-module it belongs to.
       * `create: false`: the page works on EXISTING orders (a slice of the
       * order book), so it offers no "+ New Service Order" - a new order is
       * not a hold, a dispatch hand-off, a delivered job or a WIP analysis.
       * `domain` stays the LAST key (the mapping guard parses it there). */
      ['1', 'Omni-Channel Intake (12 channels)', 14, { model: 'fix.service.order', cols: ['name', 'service_type', 'customer_id', 'device_id', 'create_date'], screens: ['M01-intake', 'M01-channels', 'M01-hotline'], reports: ['Daily Intake by Channel'], forms: ['New Service Order (12 channels, 34 fields)'] }],
      ['2', 'Lifecycle State Machine & Stepper', 9, { model: 'fix.service.order', cols: ['name', 'state', 'order_category', 'priority', 'technician_id'], screens: ['M01-all', 'M01-order', 'M01-types'], reports: ['Order Cycle-Time (TAT) Distribution'], forms: ['New Service Order (12 channels, 34 fields)'] }],
      ['3', 'Entitlement Evaluation & SLA Clock', 8, { model: 'fix.warranty', cols: ['device_id', 'warranty_type', 'status', 'end_date', 'verification_state'], screens: ['M01-entitle', 'M01-sla-instances'], reports: ['SLA Compliance & Escalations'], forms: [] }],
      ['4', 'Complaint & Fault Taxonomy Coding', 10, { model: 'fix.fault.code', cols: ['code', 'name', 'category', 'default_severity', 'active'], screens: ['M01-fault'], reports: ['Rework & Repeat-Fault Analysis'], forms: [] }],
      ['5', 'Diagnostic Templates & Benchmarks', 7, { model: 'fix.diagnostic.node', cols: ['code', 'name', 'parent_id', 'fault_code', 'is_terminal'], screens: ['M01-templates'], reports: [], forms: [] }],
      ['6', 'Estimate & Customer Approval Loop', 12, { model: 'fix.estimate', cols: ['order_id', 'version', 'grand_total', 'state', 'approved_at'], screens: ['M01-estimates', 'M01-thresholds'], reports: ['Estimate Conversion Funnel'], forms: ['Diagnostic Estimate Request'] }],
      ['7', 'Assignment & Field Dispatch Handoff', 6, { model: 'fix.service.order', cols: ['name', 'technician_id', 'preferred_technician_id', 'triage_verdict', 'state'], screens: ['M01-all'], reports: [], forms: [], create: false, domain: [['service_type', '=', 'onsite']] }],
      ['8', 'SLA Policy, Clock & Escalations', 13, { model: 'fix.sla.policy', cols: ['code', 'name', 'priority', 'response_hours', 'resolution_hours'], screens: ['M01-sla', 'M01-esc', 'M01-sla-rep', 'M01-sla-items'], reports: ['SLA Compliance & Escalations'], forms: ['SLA Item'] }],
      ['9', 'Customer Hold & Release Management', 5, { model: 'fix.service.order', cols: ['name', 'customer_id', 'deferred_reason', 'deferred_until', 'state'], screens: ['M01-holds'], reports: [], forms: ['Hold / Release Reason'], create: 'M01-form-hold', domain: [['is_deferred_block', '=', true]] }],
      ['10', 'QC Checkpoints & Rework Detection', 11, { model: 'fix.qc.checklist', cols: ['order_id', 'inspector_id', 'state', 'all_passed', 'checked_at'], screens: ['M01-qc', 'M01-rework'], reports: ['Rework & Repeat-Fault Analysis'], forms: ['QC Checklist Inspection'] }],
      ['11', 'Service Reports & Repair Warranty', 12, { model: 'fix.service.order', cols: ['name', 'service_warranty_days', 'service_warranty_until', 'service_warranty_issued_by', 'state'], screens: ['M01-rwty', 'M01-reports'], reports: ['Uncollected Device Register'], forms: [], create: false, domain: [['state', 'in', ['ready', 'delivered', 'closed']]] }],
      ['12', 'Operations Boards & WIP Analysis', 11, { model: 'fix.service.order', cols: ['name', 'state', 'branch_id', 'priority', 'create_date'], screens: ['M01-board', 'M01-wip'], reports: ['WIP Ageing by Branch', 'Order Cycle-Time (TAT) Distribution'], forms: [], create: false, domain: [['state', 'not in', ['delivered', 'closed', 'cancelled']]] }],
      /* 13 has no record of its own: an event is counted, not opened. It
       * pointed at the device-history list (Service Reports, which is
       * sub-module 11's); it is fed by the outbox report instead. */
      ['13', 'API & Domain Event Broadcasting', 10, { report: 'domain_events', screens: ['M01-events'], reports: ['Domain Events Published'], forms: [] }]
    ]
  }
};

/* In-workspace data screens. so_list/so_board/so_intake are the bespoke
 * order surfaces (/p03/orders/list scopes + /p03/stats); model_list uses the
 * generic whitelisted reader (/p03/model/records + /p03/model/action);
 * table_report calls the module's REPORTS (/p03/model/report). */
/* A02 audit M01-P2: the whitelisted order actions that had no button (a
 * chargeable order could not be delivered from the workspace: no OTP button).
 * Shown on the order lists per row, filtered by the row's state; `asks`
 * prompts for each server argument in turn, `kw` adds fixed arguments. The
 * server decides: roles, segregation of duties and gates apply there. */
const SO_OPEN = ['draft', 'intake', 'diagnostic', 'estimate_pending', 'estimate_sent',
  'awaiting_approval', 'approved', 'in_repair', 'qc_pending', 'qc_failed', 'ready'];
const SO_PRICED = ['approved', 'in_repair', 'qc_pending', 'qc_failed', 'ready', 'delivered'];
/* the server refuses a hold on a finished order (ready, delivered, closed, cancelled) */
const SO_HOLDABLE = SO_OPEN.filter((s) => s !== 'ready');
const SO_ACTIONS = [
  { id: 'send_otp', m: 'action_send_delivery_otp', l: 'Send Delivery OTP', states: ['ready'] },
  { id: 'verify_otp', m: 'action_verify_delivery_otp', l: 'Verify Delivery OTP', states: ['ready'],
    asks: [{ kwarg: 'otp', label: 'Handover code the customer read out' }] },
  { id: 'settle_counter', m: 'action_mark_settled', l: 'Record Counter Payment', states: SO_PRICED,
    kw: { source: 'counter' },
    asks: [{ kwarg: 'amount_bdt', label: 'Amount received (BDT)', number: true },
      { kwarg: 'reference', label: 'Cash receipt / MFS transaction reference' }] },
  { id: 'settle_m20', m: 'action_mark_settled', l: 'Settle from M20 Receipt', states: SO_PRICED,
    kw: { source: 'm20_receipt' }, asks: [{ kwarg: 'reference', label: 'Confirmed M20 receipt number' }] },
  { id: 'verify_settlement', m: 'action_verify_settlement', l: 'Verify Settlement', states: SO_PRICED },
  { id: 'goodwill', m: 'action_request_goodwill', l: 'Request Goodwill (approver inbox)', states: SO_OPEN,
    asks: [{ kwarg: 'reason', label: 'Reason for the goodwill repair' }] },
  { id: 'rework', m: 'action_request_rework_approval', l: 'Request Zero-Charge Rework', states: SO_OPEN,
    asks: [{ kwarg: 'reason', label: 'Why the rework is free of charge' }] },
  { id: 'category', m: 'action_change_category', l: 'Change Category',
    states: ['draft', 'intake', 'diagnostic', 'estimate_pending'],
    asks: [{ kwarg: 'category', label: 'New category: standard, warranty, amc, rework, rental, refurbishment, recycling or goodwill' },
      { kwarg: 'reason', label: 'Reason for the re-classification' }] },
  { id: 'priority', m: 'action_override_priority', l: 'Override Priority', states: SO_OPEN,
    asks: [{ kwarg: 'priority', label: 'New priority: normal, high, urgent or emergency' },
      { kwarg: 'reason', label: 'Justification for the override' }] },
  { id: 'field_order', m: 'action_create_field_order', l: 'Create Field Order',
    states: ['intake', 'diagnostic', 'approved', 'in_repair'] },
  { id: 'workshop_job', m: 'action_create_workshop_job', l: 'Create Workshop Job',
    states: ['intake', 'diagnostic', 'approved', 'in_repair'] },
  /* a hold is captured on its form: it was typed as a reason CODE into a
   * browser prompt, and the resume date could not be given at all */
  { id: 'defer', m: 'action_defer_order', l: 'Defer / Hold (supervisor)', states: SO_HOLDABLE,
    form: 'M01-form-hold' },
  { id: 'unrepairable', m: 'action_mark_unrepairable', l: 'Mark Unrepairable',
    states: ['diagnostic', 'in_repair', 'qc_pending', 'qc_failed'],
    asks: [{ kwarg: 'reason', label: 'Why the device cannot be repaired' }] },
  { id: 'cancel', m: 'action_cancel', l: 'Cancel Order', states: SO_OPEN,
    asks: [{ kwarg: 'reason', label: 'Reason: customer_declined, estimate_declined, duplicate, unrepairable, customer_unreachable, abandoned, or other: <note>' }] },
  { id: 'comeback', m: 'action_reopen_comeback', l: 'Open Comeback (repair warranty)', states: ['delivered', 'closed'],
    asks: [{ kwarg: 'reason', label: 'The problem the customer came back with' }] }
];

export const SCREENS = {
  'M01-board': { kind: 'so_board' },
  'M01-all': { kind: 'so_list', scope: 'all', actions: SO_ACTIONS,
    create: { screen: 'M01-form-order', label: 'New Service Order' } },
  'M01-intake': { kind: 'so_intake' },
  'M01-channels': { kind: 'table_report', module: 'M01', report: 'channel_intake', period: true },
  'M01-hotline': { kind: 'model_list', model: 'fix.token.queue', create: false,
    cols: ['token_display', 'counter_number', 'service_type', 'customer_id', 'state', 'create_date'],
    stateField: 'state' },
  /* The RECORD of an order, not a second "new order" form: with no order it
   * opened blank, a twin of M01-form-order under another name. */
  'M01-order': { kind: 'model_form', model: 'fix.service.order',
    title: 'Service Order Record', back: 'M01-all',
    create: false, pick: 'Open an order from All Service Orders to see its record. A new order starts with + New Service Order.',
    status: { field: 'state' },
    tabs: [
      { id: 'intake', label: '1. Customer & Intake', bn: '১. গ্রাহক ও গ্রহণ', icon: '👤', badge: '9' },
      { id: 'device', label: '2. Device & Custody', bn: '২. ডিভাইস ও কাস্টডি', icon: '📱', badge: '9' },
      { id: 'triage', label: '3. Fault & Triage', bn: '৩. ত্রুটি ও ট্রায়াজ', icon: '🔍', badge: '8' },
      { id: 'sla', label: '4. SLA & Deferred Hold', bn: '৪. এসএলএ ও হোল্ড', icon: '⏱️', badge: '8' },
      { id: 'commercial', label: '5. Settlement & Warranty', bn: '৫. নিষ্পত্তি ও ওয়ারেন্টি', icon: '💳', badge: '7' },
      { id: 'release', label: '6. Release & Evidence Vault', bn: '৬. হস্তান্তর ও প্রমাণক', icon: '🔐', badge: '6' }
    ],
    sections: [
      { tab: 'intake', title: 'Customer & Omni-Channel Intake (12 Channels)', fields: [
        { name: 'name', label: 'Order Reference', readonly: true },
        { name: 'customer_id', required: true, label: 'Customer' },
        { name: 'customer_phone', label: 'Customer Phone (+880)', readonly: true },
        { name: 'branch_id', required: true, label: 'Service Center / Branch' },
        { name: 'service_type', required: true, label: 'Intake Channel (12 Streams)' },
        { name: 'order_category', required: true, label: 'Commercial Classification (set at intake; Change Category after)' },
        { name: 'priority', required: true, label: 'SLA Priority (set at intake; Override Priority after)' },
        { name: 'technician_id', label: 'Assigned Technician' },
        { name: 'promised_delivery_date', label: 'Promised Delivery Date & Time' },
      ]},
      { tab: 'device', title: 'Device Identification & Physical Custody Matrix',
        /* the order needs a REGISTERED device and this list offers only those: on a new
         * estate it is empty, and nothing said where devices come from (rehearsal, 12 Nov) */
        note: 'Only registered devices are listed. A new device is registered first under M17 Device & Asset Registry (+ Asset); if its model is missing, add the model on the brand under M37 Product & Service Catalogue (Brands).',
        fields: [
        { name: 'device_id', required: true, label: 'Registered Device' },
        { name: 'device_serial', label: 'Device Serial Number (S/N)', readonly: true },
        { name: 'passcode_type', label: 'Device Lock / Auth Type' },
        { name: 'passcode_value', label: 'Diagnostic Passcode / PIN' },
        { name: 'lci_tripped', label: 'Liquid Contact Indicator (LCI) Tripped' },
        { name: 'accessory_bag_barcode', label: 'Accessory Bag Barcode' },
        { name: 'sim_memory_removed', label: 'SIM & Memory Card Returned at Counter' },
        { name: 'cosmetic_condition_notes', label: '6-Point Cosmetic Condition Matrix', type: 'text' },
        { name: 'intake_photo_attachment_id', label: 'Intake Condition Photo Pack' },
      ]},
      { tab: 'triage', title: 'Fault Coding, Reproducibility & Triage Verdict', fields: [
        { name: 'catalog_item_id', label: 'Service Catalogue Item' },
        { name: 'symptom_reproducibility', label: 'Symptom Reproducibility' },
        { name: 'triage_verdict', label: 'Initial Triage Verdict' },
        { name: 'diagnostic_engineer_id', label: 'Diagnostic Engineer' },
        { name: 'is_rework', label: 'Rework Flag (same device + fault, 30 days)', readonly: true },
        { name: 'rework_of_id', label: 'Original Service Order (if rework)', readonly: true },
        { name: 'fault_description', required: true, label: 'Customer Reported Fault & Symptoms', type: 'text' },
        { name: 'diagnostic_notes', label: 'Bench / Technical Diagnostic Notes', type: 'text' },
      ]},
      { tab: 'sla', title: 'SLA Countdown & Deferred Hold Governance (FLAW-01.3)',
        note: 'SLA clock automatically pauses when awaiting customer estimate approval or when placed on deferred hold.',
        fields: [
          { name: 'sla_resolution_deadline', label: 'SLA Resolution Deadline', readonly: true },
          { name: 'sla_clock_paused', label: 'SLA Clock Paused', readonly: true },
          { name: 'sla_paused_at', label: 'SLA Paused Since', readonly: true },
          { name: 'sla_total_paused_minutes', label: 'Cumulative Paused SLA (Minutes)', readonly: true },
          { name: 'is_deferred_block', label: 'Order on Deferred Hold (Defer / Resume)', readonly: true },
          { name: 'deferred_reason', label: 'Deferred Hold Reason (set by Defer)', readonly: true },
          { name: 'deferred_until', label: 'Deferred Resumption Date' },
          { name: 'deferred_notes', label: 'Hold Justification Notes', type: 'text' },
        ]},
      { tab: 'commercial', title: 'Financial Settlement Gate & Repair Warranty (FLAW-01.1)',
        note: 'Chargeable orders with approved estimates cannot transition to Delivered while Settlement State is Unpaid.',
        fields: [
          { name: 'state', label: 'Workflow State', readonly: true },
          { name: 'payment_settlement_state', label: 'Financial Settlement Status', readonly: true },
          { name: 'invoice_ref', label: 'Receipt / Transaction Reference', readonly: true },
          { name: 'settlement_source', label: 'Settlement Source', readonly: true },
          { name: 'settlement_verified', label: 'Settlement Verified', readonly: true },
          { name: 'amount_settled_bdt', label: 'Amount Settled (BDT)', readonly: true },
          { name: 'service_warranty_days', label: 'Repair Warranty Period (Days)' },
          { name: 'service_warranty_until', label: 'Repair Warranty Valid Until', readonly: true },
          { name: 'currency_id', label: 'Currency', readonly: true },
        ]},
      { tab: 'release', title: 'Customer Release, OTP Handover & Signed Report', fields: [
        { name: 'delivery_otp_verified', label: 'Customer Release OTP Verified', readonly: true },
        { name: 'recipient_name', label: 'Collecting Recipient Full Name' },
        { name: 'recipient_nid_phone', label: 'Recipient Phone / NID Verification' },
        { name: 'service_report_attachment_id', label: 'Signed Service Report / Job Card PDF' },
        { name: 'intake_completed_at', label: 'Intake Completed At', readonly: true },
        { name: 'delivered_at', label: 'Delivered Timestamp', readonly: true },
        { name: 'delivery_otp_verified_by', label: 'Handover OTP Checked By', readonly: true },
      ]}
    ] },
  'M01-types': { kind: 'table_report', module: 'M01', report: 'type_matrix', period: false },
  'M01-wip': { kind: 'so_list', scope: 'wip', actions: SO_ACTIONS },
  /* `create`: the list of holds is also where one is placed */
  'M01-holds': { kind: 'so_list', scope: 'holds', actions: SO_ACTIONS,
    create: { screen: 'M01-form-hold', label: 'Place Order on Hold' } },
  'M01-rework': { kind: 'so_list', scope: 'rework', actions: SO_ACTIONS },
  'M01-templates': { kind: 'model_list', model: 'fix.diagnostic.node', create: false,
    cols: ['code', 'name', 'parent_id', 'is_terminal', 'fault_code', 'recommended_action'] },
  'M01-fault': { kind: 'model_list', model: 'fix.fault.code', create: false,
    cols: ['code', 'name', 'category', 'default_severity', 'active'] },
  'M01-estimates': { kind: 'model_list', model: 'fix.estimate',
    cols: ['order_id', 'version', 'parts_total', 'labour_total', 'grand_total', 'state', 'customer_approval_ref', 'manager_approval_uid'],
    stateField: 'state',
    /* A02 audit M01-4/M01-9: approval moves only through these actions; the
     * customer's approval is a code sent to their phone or a signed estimate. */
    actions: [
      { m: 'action_send', l: 'Send to Customer' },
      { m: 'action_send_customer_otp', l: 'Send Approval Code' },
      { m: 'action_verify_customer_otp', l: 'Verify Approval Code', ask: 'Code the customer read out', kwarg: 'otp' },
      { m: 'action_record_signed_approval', l: 'Record Signed Approval' },
      /* A02 audit B1: the BRU-SRM-08 key is given from the branch manager's M63 inbox */
      { m: 'action_request_manager_key', l: 'Request Manager Key', ask: 'Why the second key is needed', kwarg: 'justification' },
      { m: 'action_approve', l: 'Approve' },
      { m: 'action_reject', l: 'Reject' },
      { m: 'action_revise', l: 'Revise' }
    ] },
  'M01-thresholds': { kind: 'table_report', module: 'M01', report: 'approval_thresholds', period: false },
  'M01-entitle': { kind: 'model_list', model: 'fix.warranty', create: false,
    cols: ['device_id', 'warranty_type', 'status', 'start_date', 'end_date', 'verification_state'],
    stateField: 'status',
    /* A02 audit M01-W1: pending cover becomes active only when a Warranty
     * Officer (not the registrar) verifies its proof. */
    actions: [
      /* A02 audit B1: verification is decided from the Warranty Officer's M63 inbox */
      { m: 'action_request_approval', l: 'Request Verification', ask: 'What proof is attached', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Request' },
      { m: 'action_void', l: 'Void', ask: 'Reason for voiding', kwarg: 'reason' }
    ] },
  'M01-sla': { kind: 'model_list', model: 'fix.sla.policy', create: false,
    cols: ['code', 'service_type', 'priority', 'response_hours', 'resolution_hours', 'active'] },
  'M01-esc': { kind: 'model_list', model: 'fix.sla.policy', create: false,
    cols: ['code', 'service_type', 'priority', 'resolution_hours', 'escalation_template_id', 'active'] },
  'M01-sla-rep': { kind: 'table_report', module: 'M01', report: 'sla_compliance', period: false },
  'M01-qc': { kind: 'model_list', model: 'fix.qc.checklist',
    cols: ['order_id', 'inspector_id', 'state', 'all_passed', 'checked_at'],
    stateField: 'state',
    /* A02 audit M01-6: passed only by completing it, as a QC Inspector who
     * neither repaired nor completed the repair. */
    actions: [{ m: 'action_complete', l: 'Complete Inspection' }] },
  'M01-reports': { kind: 'model_list', model: 'fix.device.history', create: false,
    cols: ['event_type', 'description', 'device_id', 'service_order_id', 'create_date'],
    domain: [['event_type', 'in', ['service_order', 'qc', 'warranty', 'repair']]] },
  'M01-rwty': { kind: 'so_list', scope: 'rwty', actions: SO_ACTIONS },

  /* ============ D365 IN-WORKSPACE FORM SCREENS (forensic audit D-M01) ============
   * Service Order Record, Estimate, QC, and Hold/Release render INSIDE the
   * workspace as canonical Dynamics 365 full-page forms over real Odoo models. */
  'M01-form-order': { kind: 'model_form', model: 'fix.service.order',
    title: 'New Service Order', back: 'M01-all',
    status: { field: 'state' },
    tabs: [
      { id: 'intake', label: '1. Customer & Intake', bn: '১. গ্রাহক ও গ্রহণ', icon: '👤', badge: '9' },
      { id: 'device', label: '2. Device & Custody', bn: '২. ডিভাইস ও কাস্টডি', icon: '📱', badge: '9' },
      { id: 'triage', label: '3. Fault & Triage', bn: '৩. ত্রুটি ও ট্রায়াজ', icon: '🔍', badge: '8' },
      { id: 'sla', label: '4. SLA & Deferred Hold', bn: '৪. এসএলএ ও হোল্ড', icon: '⏱️', badge: '8' },
      { id: 'commercial', label: '5. Settlement & Warranty', bn: '৫. নিষ্পত্তি ও ওয়ারেন্টি', icon: '💳', badge: '7' },
      { id: 'release', label: '6. Release & Evidence Vault', bn: '৬. হস্তান্তর ও প্রমাণক', icon: '🔐', badge: '6' }
    ],
    sections: [
      { tab: 'intake', title: 'Customer & Omni-Channel Intake (12 Channels)', fields: [
        { name: 'name', label: 'Order Reference', readonly: true },
        { name: 'customer_id', required: true, label: 'Customer' },
        { name: 'customer_phone', label: 'Customer Phone (+880)', readonly: true },
        { name: 'branch_id', required: true, label: 'Service Center / Branch' },
        { name: 'service_type', required: true, label: 'Intake Channel (12 Streams)' },
        { name: 'order_category', required: true, label: 'Commercial Classification (set at intake; Change Category after)' },
        { name: 'priority', required: true, label: 'SLA Priority (set at intake; Override Priority after)' },
        { name: 'technician_id', label: 'Assigned Technician' },
        { name: 'promised_delivery_date', label: 'Promised Delivery Date & Time' },
      ]},
      { tab: 'device', title: 'Device Identification & Physical Custody Matrix',
        /* the order needs a REGISTERED device and this list offers only those: on a new
         * estate it is empty, and nothing said where devices come from (rehearsal, 12 Nov) */
        note: 'Only registered devices are listed. A new device is registered first under M17 Device & Asset Registry (+ Asset); if its model is missing, add the model on the brand under M37 Product & Service Catalogue (Brands).',
        fields: [
        { name: 'device_id', required: true, label: 'Registered Device' },
        { name: 'device_serial', label: 'Device Serial Number (S/N)', readonly: true },
        { name: 'passcode_type', label: 'Device Lock / Auth Type' },
        { name: 'passcode_value', label: 'Diagnostic Passcode / PIN' },
        { name: 'lci_tripped', label: 'Liquid Contact Indicator (LCI) Tripped' },
        { name: 'accessory_bag_barcode', label: 'Accessory Bag Barcode' },
        { name: 'sim_memory_removed', label: 'SIM & Memory Card Returned at Counter' },
        { name: 'cosmetic_condition_notes', label: '6-Point Cosmetic Condition Matrix', type: 'text' },
        { name: 'intake_photo_attachment_id', label: 'Intake Condition Photo Pack' },
      ]},
      { tab: 'triage', title: 'Fault Coding, Reproducibility & Triage Verdict', fields: [
        { name: 'catalog_item_id', label: 'Service Catalogue Item' },
        { name: 'symptom_reproducibility', label: 'Symptom Reproducibility' },
        { name: 'triage_verdict', label: 'Initial Triage Verdict' },
        { name: 'diagnostic_engineer_id', label: 'Diagnostic Engineer' },
        { name: 'is_rework', label: 'Rework Flag (same device + fault, 30 days)', readonly: true },
        { name: 'rework_of_id', label: 'Original Service Order (if rework)', readonly: true },
        { name: 'fault_description', required: true, label: 'Customer Reported Fault & Symptoms', type: 'text' },
        { name: 'diagnostic_notes', label: 'Bench / Technical Diagnostic Notes', type: 'text' },
      ]},
      { tab: 'sla', title: 'SLA Countdown & Deferred Hold Governance (FLAW-01.3)',
        note: 'SLA clock automatically pauses when awaiting customer estimate approval or when placed on deferred hold.',
        fields: [
          { name: 'sla_resolution_deadline', label: 'SLA Resolution Deadline', readonly: true },
          { name: 'sla_clock_paused', label: 'SLA Clock Paused', readonly: true },
          { name: 'sla_paused_at', label: 'SLA Paused Since', readonly: true },
          { name: 'sla_total_paused_minutes', label: 'Cumulative Paused SLA (Minutes)', readonly: true },
          { name: 'is_deferred_block', label: 'Order on Deferred Hold (Defer / Resume)', readonly: true },
          { name: 'deferred_reason', label: 'Deferred Hold Reason (set by Defer)', readonly: true },
          { name: 'deferred_until', label: 'Deferred Resumption Date' },
          { name: 'deferred_notes', label: 'Hold Justification Notes', type: 'text' },
        ]},
      { tab: 'commercial', title: 'Financial Settlement Gate & Repair Warranty (FLAW-01.1)',
        note: 'Chargeable orders with approved estimates cannot transition to Delivered while Settlement State is Unpaid.',
        fields: [
          { name: 'state', label: 'Workflow State', readonly: true },
          { name: 'payment_settlement_state', label: 'Financial Settlement Status', readonly: true },
          { name: 'invoice_ref', label: 'Receipt / Transaction Reference', readonly: true },
          { name: 'settlement_source', label: 'Settlement Source', readonly: true },
          { name: 'settlement_verified', label: 'Settlement Verified', readonly: true },
          { name: 'amount_settled_bdt', label: 'Amount Settled (BDT)', readonly: true },
          { name: 'service_warranty_days', label: 'Repair Warranty Period (Days)' },
          { name: 'service_warranty_until', label: 'Repair Warranty Valid Until', readonly: true },
          { name: 'currency_id', label: 'Currency', readonly: true },
        ]},
      { tab: 'release', title: 'Customer Release, OTP Handover & Signed Report', fields: [
        { name: 'delivery_otp_verified', label: 'Customer Release OTP Verified', readonly: true },
        { name: 'recipient_name', label: 'Collecting Recipient Full Name' },
        { name: 'recipient_nid_phone', label: 'Recipient Phone / NID Verification' },
        { name: 'service_report_attachment_id', label: 'Signed Service Report / Job Card PDF' },
        { name: 'intake_completed_at', label: 'Intake Completed At', readonly: true },
        { name: 'delivered_at', label: 'Delivered Timestamp', readonly: true },
        { name: 'delivery_otp_verified_by', label: 'Handover OTP Checked By', readonly: true },
      ]}
    ] },

  /* The Hold / Release form. A hold is placed on an EXISTING order, so the
   * form first asks which (pickRecord), then captures the reason, the resume
   * date and the justification, and its button runs action_defer_order
   * (saveAction): that pauses the SLA clock and is a Service Supervisor's
   * decision - a plain write cannot do it, the hold fields are guarded.
   * Before 2026-11-12 this form opened blank with no customer or device (Save
   * could only fail), then redirected to a list that offered nothing to enter. */
  'M01-form-hold': { kind: 'model_form', model: 'fix.service.order',
    title: 'Hold / Release Reason', back: 'M01-holds',
    newLabel: 'Place Order on Hold',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the order to place on hold',
      note: 'Open orders that are not on hold. A finished order (ready, delivered, closed, cancelled) cannot be held.',
      search: 'Search order / customer / serial',
      choose: 'Hold this order',
      cols: ['name', 'customer_id', 'device_id', 'branch_id', 'state'],
      domain: [['is_deferred_block', '=', false], ['state', 'not in', ['ready', 'delivered', 'closed', 'cancelled']]],
      empty: 'There is no open service order to place on hold. A hold is placed on an existing order: create the order first.',
      emptyNew: true
    },
    saveAction: {
      method: 'action_defer_order', label: 'Place on Hold', done: 'Order placed on hold: its SLA clock is paused',
      kwargs: { reason: 'deferred_reason', resume_date: 'deferred_until', notes: 'deferred_notes' }
    },
    tabs: [
      { id: 'hold', label: '1. Hold & SLA Pause', bn: '১. হোল্ড ও এসএলএ বিরতি', icon: '⏸️', badge: '7' },
      { id: 'target', label: '2. Order Context', bn: '২. অর্ডার তথ্য', icon: '📋', badge: '5' }
    ],
    sections: [
      { tab: 'hold', title: 'Step 2 of 2: Hold Reason, Resume Date & Justification',
        note: 'Placing or lifting a hold needs the Service Supervisor role. A held order pauses its SLA clock until it is resumed from Hold Management (FR-SRM-088).',
        fields: [
          /* readonly for the generic write (the field is guarded); an INPUT
           * here because saveAction carries it to action_defer_order */
          { name: 'deferred_reason', label: 'Hold Reason', required: true, readonly: true },
          { name: 'deferred_until', label: 'Resume On (expected date)' },
          { name: 'deferred_notes', label: 'Hold Justification Notes', type: 'text' },
          { name: 'is_deferred_block', label: 'Order on Hold Now', readonly: true },
          { name: 'sla_clock_paused', label: 'SLA Clock Paused', readonly: true },
          { name: 'sla_paused_at', label: 'SLA Paused Since', readonly: true },
          { name: 'sla_total_paused_minutes', label: 'Total Paused Minutes', readonly: true },
        ]},
      { tab: 'target', title: 'Service Order', fields: [
        { name: 'name', label: 'Order Reference', readonly: true },
        { name: 'customer_id', label: 'Customer', readonly: true },
        { name: 'branch_id', label: 'Service Center / Branch', readonly: true },
        { name: 'state', label: 'Current State', readonly: true },
        { name: 'sla_resolution_deadline', label: 'SLA Resolution Deadline', readonly: true },
      ]}
    ] },

  'M01-form-estimate': { kind: 'model_form', model: 'fix.estimate',
    title: 'Diagnostic Estimate Request', back: 'M01-estimates',
    status: { field: 'state' },
    /* The lines ARE the estimate: the totals below are computed from them and
     * the model refuses to send an estimate that has none. This form showed
     * the totals and no lines, so an estimate raised in M01 could never be
     * sent (2026-11-12). Same grid as M36's estimate form. */
    lines: { field: 'line_ids', title: 'Estimate Lines (Parts, Labour, Diagnostic Fee)',
      note: 'A line left without a type is a Part and without a quantity is 1. Each line is quoted at or above its list price; a lower price is a discount, which the DOFA tiers approve.',
      /* no `defaults`: a starter row carrying values is SENT on save, and a
       * row with no description is refused - a header could not be saved alone */
      fields: [
        { name: 'line_type', label: 'Type', required: true },
        { name: 'product_id', label: 'Product' },
        { name: 'description', label: 'Description', required: true },
        { name: 'quantity', label: 'Qty', required: true },
        { name: 'unit_price', label: 'Unit Price', required: true },
        { name: 'line_total', label: 'Total', readonly: true },
      ] },
    tabs: [
      { id: 'scope', label: '1. Estimate Scope', bn: '১. প্রাক্কলন পরিধি', icon: '📄', badge: '5' },
      { id: 'pricing', label: '2. Commercials & VAT', bn: '২. মূল্য ও ভ্যাট', icon: '💰', badge: '7' },
      { id: 'dofa', label: '3. DOFA & Customer Approval', bn: '৩. অনুমোদন ও প্রমাণক', icon: '✅', badge: '5' }
    ],
    sections: [
      { tab: 'scope', title: 'Estimate Header & Diagnostic Findings', fields: [
        { name: 'order_id', label: 'Service Order' },  // optional for a pre-sales estimate; the server requires an order or an opportunity (A03 W8)
        { name: 'version', label: 'Estimate Revision', readonly: true },
        { name: 'state', label: 'Estimate Status', readonly: true },
        { name: 'expiry_date', label: 'Valid Until' },
        { name: 'diagnostic_notes', label: 'Diagnostic Breakdown & Parts Scope', type: 'text' },
      ]},
      { tab: 'pricing', title: 'Commercial Breakdown & 15% Mushak VAT', fields: [
        { name: 'parts_total', label: 'Parts Total (BDT)', readonly: true },
        { name: 'labour_total', label: 'Labour Total (BDT)', readonly: true },
        { name: 'diagnostic_total', label: 'Diagnostic Fee Total (BDT)', readonly: true },
        { name: 'discount', label: 'Discount Amount (BDT)' },
        { name: 'discount_pct', label: 'Discount (%)', readonly: true },
        { name: 'vat_amount', label: 'VAT 15% (BDT)', readonly: true },
        { name: 'grand_total', label: 'Grand Total (BDT)', readonly: true },
      ]},
      { tab: 'dofa', title: '5-Tier DOFA Governance & Customer Approval (BRU-SRM-07)',
        fields: [
          { name: 'dofa_tier_required', label: 'DOFA Approval Tier Required', readonly: true },
          { name: 'dofa_approved_by', label: 'DOFA Approver', readonly: true },
          { name: 'customer_approval_ref', label: 'Customer Approval Ref (OTP / Signed)', readonly: true },
          { name: 'customer_approval_method', label: 'Customer Approval Method', readonly: true },
          { name: 'manager_approval_uid', label: 'Manager Approval User', readonly: true },
          { name: 'signed_estimate_attachment_id', label: 'Signed Estimate / Customer Approval PDF' },
        ]},
    ] },

  'M01-form-qc': { kind: 'model_form', model: 'fix.qc.checklist',
    title: 'QC Checklist Inspection', back: 'M01-qc',
    status: { field: 'state' },
    lines: { field: 'item_ids', title: 'Checklist Items', readonlyGrid: true,
      note: 'Written from the stages above when the inspection is completed.',
      fields: [
        { name: 'name', label: 'Item', readonly: true },
        { name: 'passed', label: 'Passed', readonly: true },
        { name: 'notes', label: 'Notes', readonly: true },
      ] },
    tabs: [
      { id: 'inspection', label: '1. 4-Stage QC Gates', bn: '১. ৪-ধাপ কিউসি যাচাই', icon: '🛡️', badge: '8' },
      { id: 'evidence', label: '2. Findings & Evidence', bn: '২. পর্যবেক্ষণ ও প্রমাণক', icon: '📎', badge: '3' }
    ],
    sections: [
      { tab: 'inspection', title: 'ISO 9001 4-Stage Quality Control Checkpoints', fields: [
        { name: 'order_id', required: true, label: 'Service Order' },
        { name: 'inspector_id', label: 'QC Inspector (stamped on completion)', readonly: true },
        { name: 'visual_inspection_passed', label: 'Stage 1: Cosmetic & Visual Fitment Passed' },
        { name: 'functional_test_passed', label: 'Stage 2: Full Functional Diagnostic Passed' },
        { name: 'safety_electrical_passed', label: 'Stage 3: Electrical & Thermal Safety Passed' },
        { name: 'cleaning_sanitization_passed', label: 'Stage 4: Device Sanitization & Packaging Passed' },
        { name: 'all_passed', label: 'All QC Checkpoints Passed', readonly: true },
        { name: 'state', label: 'QC Status', readonly: true },
      ]},
      { tab: 'evidence', title: 'Inspector Findings & Calibration Evidence',
        note: 'An order leaves QC only through a recorded inspection (FR-SRM release gate); a failed checklist routes the order to rework.',
        fields: [
          { name: 'checked_at', label: 'Inspected Timestamp', readonly: true },
          { name: 'notes', label: 'QC Inspection Findings / Failed Checkpoints', type: 'text' },
          { name: 'test_report_attachment_id', label: 'QC Test Report / Calibration Printout' },
        ]},
    ] },

  /* ============ BUILT-IN REPORTS as computed table_reports (audit D-M01) ============
   * The backend REPORTS functions already existed in controllers/a02/m01.py —
   * these screens finally surface them; previously the chips routed to the
   * nearest LIST (Uncollected → warranty list, TAT → WIP list). */
  'M01-rpt-wipage': { kind: 'table_report', module: 'M01', report: 'wip_ageing', title: 'WIP Ageing by Branch', period: true },
  'M01-rpt-estfunnel': { kind: 'table_report', module: 'M01', report: 'estimate_funnel', title: 'Estimate Conversion Funnel', period: true },
  'M01-rpt-rework': { kind: 'table_report', module: 'M01', report: 'rework_analysis', title: 'Rework & Repeat-Fault Analysis', period: true },
  'M01-rpt-tat': { kind: 'table_report', module: 'M01', report: 'tat_distribution', title: 'Order Cycle-Time (TAT) Distribution', period: true },
  'M01-rpt-uncollected': { kind: 'table_report', module: 'M01', report: 'uncollected_register', title: 'Uncollected Device Register', period: false },
  /* what M01 has put on the transactional outbox, per event type (counts only) */
  'M01-events': { kind: 'table_report', module: 'M01', report: 'domain_events', title: 'Domain Events Published (Outbox)', period: false },
  /* ==================================================================
   * A03 GAP-CLOSURE BUILD - new surfaces for this module
   * Every cols list was validated against the model's real fields
   * before generation: /p03/model/records drops unknown columns
   * silently, so a typo would read as missing data rather than as
   * a bug.
   * ================================================================== */
  'M01-sla-items': { kind: 'model_list', model: 'fix.sla.item', create: true,
    cols: ['policy_id', 'sequence', 'name', 'kpi_code', 'target_hours', 'calendar_id', 'pausable', 'warn_at_pct', 'active'],
    note: 'Pause/resume and work hours are configurable at item level as well as policy level, so priorities can run against different calendars.' },
  'M01-form-sla-item': {
    kind: 'model_form', model: 'fix.sla.item',
    title: 'SLA Item', back: 'M01-sla-items',
    status: { field: 'active', labels: { true: 'Active', false: 'Inactive' } },
    tabs: [
      { id: 'target', label: '1. Target', bn: '১. লক্ষ্য', icon: '🎯' },
      { id: 'clock', label: '2. Clock & Calendar', bn: '২. ঘড়ি ও ক্যালেন্ডার', icon: '🕒' }
    ],
    sections: [
      {
        tab: 'target',
        title: 'The Promise',
        fields: [
        { name: 'policy_id', label: 'Policy', required: true },
        { name: 'name', label: 'Item', required: true },
        { name: 'kpi_code', label: 'KPI Code', required: true },
        { name: 'target_hours', label: 'Target (business hours)', required: true },
        { name: 'sequence', label: 'Order' },
        { name: 'active', label: 'Active' }
        ]
      },
      {
        tab: 'clock',
        title: 'Calendar & Pause Rules',
        note: 'Configurable at item level as well as policy level, so priorities can run against different calendars. An empty calendar everywhere means all-day-every-day, which is the documented default.',
        fields: [
        { name: 'calendar_id', label: 'Business Hours' },
        { name: 'pausable', label: 'Pausable' },
        { name: 'warn_at_pct', label: 'Warn At % Of Target' }
        ]
      }
    ]
  },
  'M01-sla-instances': { kind: 'model_list', model: 'fix.sla.kpi.instance', create: false,
    cols: ['started_at', 'display_label', 'res_model', 'res_id', 'kpi_code', 'state', 'target_at', 'elapsed_pause_minutes', 'series_index'],
    stateField: 'state',
    actions: [
      /* A02 audit B3: Service Supervisor only (enforced by the model) */
      { m: 'pause', l: 'Pause (supervisor)', ask: 'Reason for the pause', kwarg: 'reason' },
      { m: 'resume', l: 'Resume (supervisor)' },
      { m: 'succeed', l: 'Succeed (supervisor)' }
    ],
    /* An SLA clock is EVIDENCE: it starts by itself and its fields are guarded
     * (A02 audit B3), so this list has no "+ New" - and it says so, instead of
     * an empty grid under a form chip that promised data entry (2026-11-12). */
    empty: 'No SLA clock is running. A clock starts by itself when a service order is received, a call is queued or a complaint is logged: it is audit evidence and cannot be typed in. When one is listed, select it to Pause (with a reason), Resume or mark it Succeeded (Service Supervisor). Targets are set under SLA Items & Targets.',
    note: 'A resume cancels the instance and creates a new one, so these are an append-only series per record rather than a mutable row.' },
  'M01-form-sla-instance': {
    kind: 'model_form', model: 'fix.sla.kpi.instance',
    title: 'SLA KPI Instance', back: 'M01-sla-instances',
    /* every field is read-only: the clock engine starts an instance, nobody types one */
    create: false, pick: 'An SLA clock is started by its order, never typed in: open one from Live SLA Clocks.',
    status: { field: 'state', labels: { in_progress: 'In progress', paused: 'Paused', succeeded: 'Succeeded', breached: 'Breached', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'clock', label: '1. The Clock', bn: '১. ঘড়ি', icon: '🕒' },
      { id: 'holds', label: '2. Holds', bn: '২. বিরতি', icon: '⏸️' },
      { id: 'series', label: '3. Instance Series', bn: '৩. ইনস্ট্যান্স ধারা', icon: '🔗' }
    ],
    sections: [
      {
        tab: 'clock',
        title: 'What Is Promised, Against What Calendar',
        /* A02 audit B3: an instance is the clock's evidence; it moves only through its actions */
        note: 'The calendar is STAMPED at creation: a later edit does not retroactively move this instance\'s target.',
        fields: [
        { name: 'display_label', label: 'Instance', readonly: true },
        { name: 'res_model', label: 'Record Model', readonly: true },
        { name: 'res_id', label: 'Record ID', readonly: true },
        { name: 'partner_id', label: 'Customer', readonly: true },
        { name: 'policy_id', label: 'Policy', readonly: true },
        { name: 'item_id', label: 'SLA Item', readonly: true },
        { name: 'kpi_code', label: 'KPI', readonly: true },
        { name: 'calendar_id', label: 'Business Hours Used', readonly: true },
        { name: 'target_hours', label: 'Target (hours)', readonly: true },
        { name: 'started_at', label: 'Started', readonly: true },
        { name: 'target_at', label: 'Deadline', readonly: true },
        { name: 'warn_at', label: 'Warn At', readonly: true }
        ]
      },
      {
        tab: 'holds',
        title: 'Pause And Elapsed Time',
        note: 'Whether hold time counts depends on whether the pause and the resume fell inside working hours — a pause at 18:00 lifted at 09:00 spans fifteen clock hours and, on a 9-to-6 calendar, zero business minutes.',
        fields: [
        { name: 'state', label: 'State', readonly: true },
        { name: 'paused_at', label: 'Paused At', readonly: true },
        { name: 'pause_reason', label: 'Pause Reason', readonly: true },
        { name: 'elapsed_pause_minutes', label: 'Elapsed Time (min)', readonly: true },
        { name: 'succeeded_at', label: 'Succeeded At', readonly: true },
        { name: 'breached_at', label: 'Breached At', readonly: true },
        { name: 'warned_at', label: 'Warned At', readonly: true }
        ]
      },
      {
        tab: 'series',
        title: 'The Append-Only Series',
        note: 'A resume does not restart this timer: it cancels the instance and creates a new one. The chain is how many times a record was held, and for how long — which is what a disputed SLA claim turns on.',
        fields: [
        { name: 'series_index', label: 'Position In Series', readonly: true },
        { name: 'supersedes_id', label: 'Supersedes', readonly: true },
        { name: 'superseded_by_id', label: 'Superseded By', readonly: true },
        { name: 'cancelled_reason', label: 'Cancellation Reason', readonly: true }
        ]
      }
    ]
  },
};

/* built-in report chips -> the screen that shows that report */
export const REPORT_ROUTES = {
  "M01:Daily Intake by Channel": "M01-channels",
  "M01:WIP Ageing by Branch": "M01-rpt-wipage",
  "M01:SLA Compliance & Escalations": "M01-sla-rep",
  "M01:Estimate Conversion Funnel": "M01-rpt-estfunnel",
  "M01:Rework & Repeat-Fault Analysis": "M01-rpt-rework",
  "M01:Order Cycle-Time (TAT) Distribution": "M01-rpt-tat",
  "M01:Uncollected Device Register": "M01-rpt-uncollected",
  "M01:Domain Events Published": "M01-events"
};

/* data-entry form chips: M01 data-entry chips open real in-workspace D365 model_form
 * screens over fix.service.order, fix.estimate, and fix.qc.checklist. */
export const FORM_CHIPS = {
  'M01:SLA Item': 'M01-form-sla-item',
  'M01:Service Order (12 channels, 34 fields)': 'M01-form-order',
  'M01:Estimate Request': 'M01-form-estimate',
  'M01:QC Checklist Result': 'M01-form-qc',
  'M01:New Service Order (12 channels, 34 fields)': 'M01-form-order',
  'M01:New Service Order': 'M01-form-order',
  'M01:Diagnostic Estimate Request': 'M01-form-estimate',
  'M01:Hold / Release Reason': 'M01-form-hold',
  'M01:QC Checklist Inspection': 'M01-form-qc',
  /* the row of a HOLD list is the hold: it opens the Hold / Release form for
   * that order (the sub-module page; M01-holds itself opens the order record) */
  'M01:__by_screen__': {
    'M01-holds': 'M01-form-hold'
  },
  'M01:__by_model__': {
    'fix.sla.item': 'M01-form-sla-item',
    'fix.sla.kpi.instance': 'M01-form-sla-instance',
    'fix.service.order': 'M01-form-order',
    'fix.estimate': 'M01-form-estimate',
    'fix.qc.checklist': 'M01-form-qc'
  }
};

export const FORM_MODELS = {
  'M01:SLA Item': 'fix.sla.item',
  'M01:Service Order (12 channels, 34 fields)': 'fix.service.order',
  'M01:Estimate Request': 'fix.estimate',
  'M01:QC Checklist Result': 'fix.qc.checklist',
  'M01:New Service Order (12 channels, 34 fields)': 'fix.service.order',
  'M01:New Service Order': 'fix.service.order',
  'M01:Diagnostic Estimate Request': 'fix.estimate',
  'M01:Hold / Release Reason': 'fix.service.order',
  'M01:QC Checklist Inspection': 'fix.qc.checklist'
};

/* the module's "+ New" surface: opens the canonical Dynamics 365 Service Order Record form */
export const CREATE = {
  M01: { screen: 'M01-form-order', model: 'fix.service.order', label: 'New Service Order' }
};
