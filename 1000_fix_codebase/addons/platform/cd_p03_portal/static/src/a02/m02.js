/** @odoo-module **/
/* A02 · Service Operations — M02 Field Service & Dispatch.
 * Backend: controllers/a02/m02.py (SURFACES, kpis, REPORTS, /p03/field/*)
 * + /p03/dispatch/map_data (the live SVG map) + the whitelisted field models.
 * Every screen renders INSIDE the shell from live data: the dispatch board
 * with the explainable suggestion engine, scoped field-order lists with the
 * full AS-06 field lifecycle on the buttons, model lists for work orders,
 * declines, geofences and telemetry, and the optimizer-backed route list.
 *
 * D365 IN-WORKSPACE FORMS (Audit M02):
 * Create Field Work Order and Emergency Reschedule (opened on an SLA Risk Board
 * row, bound to that order) render INSIDE the workspace with sticky command bars, zero modal popups,
 * 100% deterministic input IDs, matching <label for>, and real Odoo ORM persistence. */

export const MODULE = {
  area: 'A02', code: 'M02', en: 'Field Service & Dispatch', title: 'M02 · Field Service & Dispatch',
  bn: 'ফিল্ড সার্ভিস ও ডিসপ্যাচ', icon: '🚐',
  desc: 'AI dispatch board, route optimisation, technician app (24h offline), GPS tracking, field evidence & payments.',
  kpis: [
    { l: 'Jobs / Tech / Day', m: 'jobs_tech_day' },
    { l: 'Auto-Assignment', m: 'auto_assignment', suffix: '%' },
    { l: 'On-Time Arrival', m: 'on_time_arrival', suffix: '%' },
    { l: 'Travel Time Share', m: 'travel_share', suffix: '%' },
    { l: 'Unassigned > 15m', m: 'unassigned_15m' },
    { l: 'Offline Sync Health', m: 'offline_sync_health', suffix: '%' }
  ],
  groups: [
    { en: 'Record Coverage', screens: [
      { id: 'M02-technician-location', en: "Technician Location", bn: "টেকনিশিয়ান অবস্থান", t: 'g' }
    ]},
    { en: 'Dispatch Console', screens: [
      { id: 'M02-dispatch', en: 'Dispatch Board (Live)', bn: 'ডিসপ্যাচ বোর্ড', t: 'd' },
      { id: 'M02-map', en: 'Live Technician Map', bn: 'লাইভ ম্যাপ', t: 'd' },
      { id: 'M02-unassigned', en: 'Unassigned Queue', bn: 'অনির্ধারিত সারি', t: 'g' },
      { id: 'M02-redispatch', en: 'Re-Dispatch Needed', bn: 'পুনরায় ডিসপ্যাচ প্রয়োজন', t: 'g' },
      { id: 'M02-sla-risk', en: 'SLA Risk Board', bn: 'এসএলএ ঝুঁকি', t: 'g' }
    ]},
    { en: 'Work Orders', screens: [
      { id: 'M02-wo', en: 'Field Work Orders', bn: 'ফিল্ড ওয়ার্ক অর্ডার', t: 'g' },
      { id: 'M02-record', en: 'Work Order Record', bn: 'ওয়ার্ক অর্ডার নথি', t: 'g' },
      { id: 'M02-exceptions', en: 'Field Exceptions', bn: 'ফিল্ড ব্যতিক্রম', t: 'g' },
      { id: 'M02-crews', en: 'Crews & Multi-Tech Jobs', bn: 'ক্রু নিয়োগ', t: 'r' }
    ]},
    { en: 'Routing & Territories', screens: [
      { id: 'M02-zones', en: 'Zones & Geofences', bn: 'জোন ও জিওফেন্স', t: 'g' },
      { id: 'M02-routes', en: 'Route Optimisation', bn: 'রুট অপ্টিমাইজেশন', t: 'g' },
      { id: 'M02-territory', en: 'Territory Balancing', bn: 'টেরিটরি সমন্বয়', t: 'r' }
    ]},
    { en: 'Technician App (P02)', screens: [
      { id: 'M02-day', en: 'Day / Job Queue Preview', bn: 'দিনের কাজ', t: 'r' },
      { id: 'M02-offline', en: 'Offline Sync Monitor', bn: 'অফলাইন সিঙ্ক', t: 'g' },
      { id: 'M02-evidence', en: 'Field Evidence Hub', bn: 'ফিল্ড প্রমাণ', t: 'g' },
      { id: 'M02-vanstock', en: 'Van Stock Consumption', bn: 'ভ্যান স্টক', t: 'r' },
      { id: 'M02-fieldparts', en: 'Field Order Parts', bn: 'ফিল্ড অর্ডারের যন্ত্রাংশ', t: 'g' }
    ]},
    { en: 'Safety & Payments', screens: [
      { id: 'M02-loneworker', en: 'Lone-Worker Check-In', bn: 'একাকী কর্মী নিরাপত্তা', t: 'g' },
      { id: 'M02-panic', en: 'Panic Alert Log', bn: 'প্যানিক অ্যালার্ট', t: 'g' },
      { id: 'M02-collect', en: 'Collect & Hand Over', bn: 'সংগ্রহ ও নগদ হস্তান্তর', t: 'g' },
      { id: 'M02-fieldpay', en: 'On-Site Payments', bn: 'স্থানে পেমেন্ট', t: 'r' },
      { id: 'M02-cashrec', en: 'Daily Cash Reconciliation', bn: 'নগদ মিলকরণ', t: 'r' }
    ]}
  ],
  reports: ['Dispatch Performance by Zone', 'Travel-Time Analysis', 'Jobs per Technician', 'Field Exception Summary', 'Van Stock Variance', 'On-Site Payment Reconciliation', 'Technician Utilization & Travel Time', 'First-Time Fix Rate by Skill', 'Geofence Breach & Delay Log'],
  forms: ['Field Work Order', 'Field Exception Report', 'Crew Assignment', 'Route Plan', 'Emergency Reschedule Request', 'Zone Geofence', 'Dispatch Zone', 'Technician Work Order', 'Van Stock Reconciliation', 'Lone-Worker Check-In', 'Field Incident Report', 'Dispatch Decision', 'Technician Device', 'Offline Conflict Review', 'Tracking Pause', 'Failed Visit Report', 'Field Cash Reconciliation'],
  cross: ['M01 order → work order', 'M55 availability & roster', 'M22 certification gate', 'M03 logistics handover', 'M17 asset context'],
  freg: {
    src: 106,
    /* M02 capture audit (2026-11-12): nine of the twelve pages named no form,
     * so a dispatcher on Van Stock, Field Safety or Territory had no button to
     * record anything. Each page now names what captures its record - its own
     * form, the master form of the module that owns the record (van counts:
     * M15, lone-worker sessions: M59, zones: M30), or, where the record is
     * written by a workflow or the technician app, the screen whose buttons
     * write it (Dispatch Board, Record Collection, Decline). Telemetry (GPS,
     * the offline journal) and field evidence stay capture-free on purpose:
     * typing them in would fabricate tracking or a customer's sign-off.
     * `domain` stays the LAST key (the mapping guard parses it there).
     *
     * Second pass (2026-11-18): pages 1, 7, 8, 9 and 11 still captured
     * nothing a person decides. The spec names a record on each that the
     * estate never had: the dispatch decision and its override reason
     * (BRU-FSM-04), a supervisor's conflict review (AUT-FSM-06), a tracking
     * pause (BRU-FSM-05), a failed visit with site evidence (BRU-FSM-09)
     * and the technician's daily cash reconciliation (BRU-FSM-07); page 6
     * gains device enrolment (T-11). The streams stay untypeable. */
    sub: [
      ['1', 'Candidate Scoring & Assignment', 14, { model: 'fix.field.order', cols: ['name', 'zone_id', 'priority', 'scheduled_start', 'technician_id'], screens: ['M02-dispatch', 'M02-unassigned', 'M02-decisions', 'M02-exceptions'], reports: ['Field Exception Summary', 'First-Time Fix Rate by Skill'], forms: ['Dispatch Decision', 'Field Work Order'], create: 'M02-form-decision', domain: [['state', 'in', ['draft', 'pending_dispatch', 'declined']]] }],
      ['2', 'Dispatch Board', 10, { model: 'fix.field.order', cols: ['name', 'technician_id', 'state', 'sla_deadline', 'dispatched_at'], screens: ['M02-dispatch', 'M02-sla-risk', 'M02-redispatch'], reports: ['Dispatch Performance by Zone'], forms: ['Emergency Reschedule Request'], create: 'M02-form-reschedule', domain: [['state', 'in', ['dispatched', 'accepted', 'en_route', 'arrived', 'in_progress']]] }],
      ['3', 'Route Optimisation & Re-optimisation', 9, { model: 'fix.field.route', cols: ['name', 'technician_id', 'date', 'total_distance_km', 'improvement_pct'], screens: ['M02-routes'], reports: ['Travel-Time Analysis'], forms: ['Route Plan'] }],
      ['4', 'Territory / Zone / Geofence', 8, { model: 'fix.geofence', cols: ['name', 'zone_id', 'geofence_type', 'active'], screens: ['M02-zones', 'M02-territory'], reports: ['Geofence Breach & Delay Log', 'Dispatch Performance by Zone'], forms: ['Zone Geofence', 'Dispatch Zone'] }],
      ['5', 'Work-Order Lifecycle', 9, { model: 'fix.field.order', cols: ['name', 'state', 'dispatched_at', 'arrived_at', 'completed_at'], screens: ['M02-record', 'M02-wo', 'M02-crews', 'M02-exceptions'], reports: ['Jobs per Technician', 'First-Time Fix Rate by Skill'], forms: ['Field Work Order', 'Crew Assignment', 'Field Exception Report'] }],
      ['6', 'Technician Mobile App', 18, { model: 'fix.work.order', cols: ['name', 'technician_id', 'sequence', 'state', 'start_time'], screens: ['M02-day', 'M02-wo', 'M02-fieldparts', 'M02-devices'], reports: ['Technician Utilization & Travel Time', 'Jobs per Technician'], forms: ['Technician Work Order', 'Technician Device'] }],
      ['7', 'Offline Sync & Conflict Resolution', 7, { model: 'fix.offline.idempotency.ledger', cols: ['command_id', 'technician_id', 'operation', 'status', 'applied_at'], screens: ['M02-offline', 'M02-conflict-reviews', 'M02-devices'], reports: [], forms: ['Offline Conflict Review', 'Technician Device'], create: 'M02-form-conflict' }],
      ['8', 'GPS Tracking & ETA', 7, { model: 'fix.technician.location', cols: ['technician_id', 'timestamp', 'latitude', 'longitude', 'speed_kmh'], screens: ['M02-map', 'M02-technician-location', 'M02-pauses'], reports: ['Geofence Breach & Delay Log', 'Travel-Time Analysis'], forms: ['Tracking Pause'], create: 'M02-form-pause' }],
      ['9', 'Field Evidence Capture', 6, { model: 'fix.field.order', cols: ['name', 'technician_id', 'customer_signature_signer', 'customer_otp_verified', 'post_work_photo_attachment_id'], screens: ['M02-evidence', 'M02-failed-visits'], reports: ['Field Exception Summary'], forms: ['Failed Visit Report'], create: 'M02-form-failedvisit', domain: [['state', 'in', ['arrived', 'in_progress', 'completed']]] }],
      ['10', 'Van Stock', 5, { model: 'fix.stock.van.recon', cols: ['name', 'location_id', 'technician_id', 'recon_date', 'state'], screens: ['M02-vanstock', 'M02-fieldparts'], reports: ['Van Stock Variance'], forms: ['Van Stock Reconciliation'], create: 'M15-form-recon' }],
      ['11', 'On-Site Payment', 6, { model: 'fix.field.order', cols: ['name', 'onsite_collection_amount', 'onsite_payment_method', 'onsite_payment_trx_id', 'customer_otp_verified'], screens: ['M02-collect', 'M02-field-cash', 'M02-fieldpay', 'M02-cashrec'], reports: ['On-Site Payment Reconciliation'], forms: ['Field Cash Reconciliation'], create: 'M02-form-cashrecon', domain: [['onsite_payment_method', 'in', ['cash', 'bkash', 'nagad', 'sslcommerz', 'corporate_credit']]] }],
      ['12', 'Field Safety', 7, { model: 'fix.hse.loneworker', cols: ['name', 'employee_id', 'field_order_id', 'checkin_time', 'expected_end', 'state'], screens: ['M02-loneworker', 'M02-panic'], reports: [], forms: ['Lone-Worker Check-In', 'Field Incident Report'], create: 'M59-form-loneworker', domain: [['field_order_id', '!=', false]] }]
    ]
  }
};

/* In-workspace data screens. fs_board/fs_list are the bespoke dispatch
 * surfaces; model_list rides the whitelisted generic reader; table_report
 * calls the module REPORTS. */
export const SCREENS = {
  'M02-dispatch': { kind: 'fs_board' },
  'M02-map': { kind: 'fs_map' },
  /* M46: the vehicle an order travels in was taken off the road. Open the order
   * and choose another vehicle (the flag clears), or wait for the van to return. */
  'M02-redispatch': { kind: 'model_list', model: 'fix.field.order', create: false,
    note: 'The vehicle these orders travel in was taken off the road. Open the order and choose another vehicle on its Dispatch & Zone tab, or reschedule it after the van returns. The flag clears on its own either way.',
    domain: [['redispatch_required', '=', true]],
    stateField: 'state',
    cols: ['name', 'order_id', 'technician_id', 'scheduled_start', 'state', 'vehicle_id', 'redispatch_required', 'redispatch_offroad_id', 'redispatch_reason', 'redispatch_flagged_at'] },
  'M02-unassigned': { kind: 'model_list', model: 'fix.field.order', create: false,
    cols: ['name', 'order_id', 'zone_id', 'priority', 'scheduled_start', 'state', 'technician_id', 'vehicle_id', 'redispatch_required'],
    domain: [['state', 'in', ['draft', 'pending_dispatch', 'declined']]],
    stateField: 'state',
    /* A02 audit M02-13: the actions the dispatch board does not offer.
     * The server checks who may run each one (dispatcher / assigned technician). */
    /* `states` mirror the model's own guards (bidirectional audit 2026-11-13):
     * a button shows as available only where the server accepts it. */
    actions: [
      /* A09 M22-F3: decided in the Certification Override Approver's inbox,
       * never by the dispatcher who asks. */
      { m: 'action_request_certification_waiver', l: 'Request Certification Waiver', ask: 'Technician employee id, then the reason', kwarg: 'waiver', states: ['draft', 'pending_dispatch', 'declined'] },
      { m: 'action_cancel', l: 'Cancel (dispatcher)', ask: 'Reason for the cancellation', kwarg: 'reason', states: ['draft', 'pending_dispatch', 'declined'] }
    ] },
  'M02-sla-risk': { kind: 'model_list', model: 'fix.field.order', create: false,
    cols: ['name', 'order_id', 'zone_id', 'priority', 'sla_deadline', 'scheduled_start', 'state', 'technician_id'],
    domain: [['state', 'in', ['pending_dispatch', 'dispatched', 'accepted', 'en_route', 'arrived', 'in_progress']], ['sla_deadline', '!=', false]] },
  'M02-wo': { kind: 'model_list', model: 'fix.work.order',
    cols: ['name', 'order_id', 'technician_id', 'sequence', 'state', 'start_time', 'end_time', 'duration_hours'],
    stateField: 'state',
    /* A pending slot had no way to get its technician: action_assign (the
     * dispatcher-only path, which also sets it Assigned) was on no button. */
    actions: [
      { m: 'action_assign', l: 'Assign Technician (dispatcher)', ask: 'Technician employee id', kwarg: 'technician_id', states: ['pending', 'assigned'] },
      { m: 'action_request_certification_waiver', l: 'Request Certification Waiver', ask: 'Technician employee id, then the reason', kwarg: 'waiver', states: ['pending', 'assigned'] }
    ] },
  'M02-record': { kind: 'model_list', model: 'fix.field.order', create: false,
    cols: ['name', 'order_id', 'technician_id', 'zone_id', 'scheduled_start', 'state',
      'dispatched_at', 'arrived_at', 'actual_travel_minutes', 'on_time_arrival', 'completed_at', 'onsite_payment_state',
      'vehicle_id', 'vehicle_driver_id', 'redispatch_required'],
    stateField: 'state',
    /* A02 audit M02-13: decline, cancel and the cash hand-over had no button.
     * An arrival carries the technician's position (M02-8); completion needs
     * the customer's sign-off, a post-work photo and the work summary (M02-2),
     * captured through the technician app's evidence channel. */
    actions: [
      /* A02 ERP audit X-17: the field service report */
      { m: 'p03_print_document', print: 'a4', l: 'Print Field Service Report', states: ['completed'] },
      { m: 'action_decline', l: 'Decline', ask: 'Reason for declining the job', kwarg: 'reason', states: ['dispatched'] },
      { m: 'action_arrive', l: 'Mark Arrival', ask: 'Your position: latitude, longitude (e.g. 23.8103, 90.4125)', kwarg: 'position', states: ['en_route'] },
      { m: 'action_record_collection', l: 'Record Collection', ask: 'Method amount [TrxID], e.g. bkash 1500 8N7A6B5C or cash 900', kwarg: 'payment', states: ['arrived', 'in_progress'] },
      /* A02 ERP audit M02-F1: the technician declares the hand-over; a cashier
       * of the service order's branch (not the technician, not the declarer)
       * accepts it into that branch's open drawer. */
      { m: 'action_handover_field_cash', l: 'Hand Over Cash (declare)', states: ['completed'] },
      { m: 'action_accept_field_cash', l: 'Accept Field Cash (cashier)', states: ['completed'] },
      { m: 'action_reassign', l: 'Reassign (dispatcher)', ask: 'New technician employee id, then the reason', kwarg: 'reassignment', states: ['dispatched', 'accepted', 'en_route'] },
      { m: 'action_waive_geofence', l: 'Waive Geofence (dispatcher)', ask: 'Reason for waiving the arrival geofence', kwarg: 'reason', states: ['dispatched', 'accepted', 'en_route'] },
      /* A02 ERP audit M02-F3: the fence, zone and service order are frozen once
       * dispatched; only a dispatcher moves the arrival fence, with a reason. */
      { m: 'action_set_geofence', l: 'Set Geofence (dispatcher)', ask: 'Geofence id (0 = the zone\'s fences), then the reason', kwarg: 'change', states: ['dispatched', 'accepted', 'en_route'] },
      { m: 'action_cancel', l: 'Cancel (dispatcher)', ask: 'Reason for the cancellation', kwarg: 'reason', states: ['draft', 'pending_dispatch', 'declined', 'dispatched', 'accepted', 'en_route', 'arrived', 'in_progress'] }
    ] },
  /* A decline is recorded by Decline on the field order (Work Order Record),
   * which checks the order is dispatched to the decliner; the model refuses
   * any other create, so this list's "+ New" could only fail on Save. */
  'M02-exceptions': { kind: 'model_list', model: 'fix.field.decline.log', create: false,
    cols: ['name', 'field_order_id', 'technician_id', 'reason', 'decline_date', 'notes'],
    empty: 'No field exception recorded. An exception is recorded when the assigned technician declines a field order (Decline on Work Order Record, or the technician app), with a coded reason: it cannot be typed in here.' },
  'M02-crews': { kind: 'table_report', module: 'M02', report: 'crews',
    title: 'Crews & Multi-Tech Jobs', period: false },
  'M02-zones': { kind: 'model_list', model: 'fix.geofence',
    cols: ['name', 'zone_id', 'geofence_type', 'active'] },
  /* The route's three workflow methods were whitelisted but on no button, so
   * a plan stayed "Draft Itinerary" for good (bidirectional audit 2026-11-13). */
  'M02-routes': { kind: 'model_list', model: 'fix.field.route',
    cols: ['name', 'technician_id', 'date', 'order_count', 'total_distance_km', 'total_duration_hours', 'improvement_pct', 'route_state'],
    stateField: 'route_state',
    actions: [
      { m: 'action_optimize_route', l: 'Optimise Route', states: ['draft', 'optimized'] },
      { m: 'action_start_route', l: 'Start Route', states: ['draft', 'optimized'] },
      { m: 'action_complete_route', l: 'Complete Route', states: ['in_progress'] }
    ] },
  'M02-territory': { kind: 'table_report', module: 'M02', report: 'zone_workload', title: 'Territory Workload Balance', period: false },

  /* ============ TECHNICIAN APP (P02) + SAFETY & PAYMENTS (registry v2) ====
   * The eight registry screens that had no surface. Each renders from a real
   * model or a measured report; the two safety screens state their honest
   * absence (no safety-event store yet — the P02 app stream is the source). */
  'M02-day': { kind: 'table_report', module: 'M02', report: 'day_queue', title: 'Day / Job Queue Preview', period: false },
  'M02-offline': { kind: 'model_list', model: 'fix.offline.idempotency.ledger', create: false,
    cols: ['command_id', 'technician_id', 'device_id', 'model', 'operation', 'status', 'review_state', 'conflict_reason', 'client_created_at', 'applied_at'],
    stateField: 'status',
    empty: 'No offline command received yet. The technician app writes one entry per action it replays after working offline, with its result and any conflict: the journal is audit evidence and cannot be typed in. A rejected or conflicted entry is reviewed with + New Conflict Review.' },
  /* Field evidence is the signature, photos and job sheet linked to a FIELD
   * order by the technician app's evidence channel (bound to the assigned
   * technician). This list used to read fix.workshop.evidence - M31's bench
   * repair evidence, which needs a workshop job and holds no field visit. */
  'M02-evidence': { kind: 'model_list', model: 'fix.field.order', create: false,
    cols: ['name', 'technician_id', 'state', 'customer_otp_verified', 'customer_signature_signer', 'customer_signature_attachment_id', 'pre_work_photo_attachment_id', 'post_work_photo_attachment_id', 'field_job_sheet_attachment_id'],
    domain: [['state', 'in', ['arrived', 'in_progress', 'completed']]],
    stateField: 'state',
    empty: 'No field order has reached the customer site yet. Evidence (customer signature or OTP, before and after photos) is captured on site by the assigned technician in the technician app and linked to the order here; completion is refused without it.' },
  'M02-fieldparts': { kind: 'model_list', model: 'fix.field.order.part', create: false,
    cols: ['field_order_id', 'product_id', 'quantity', 'lot_serial_number', 'state', 'consumed_by_id', 'consumed_at'],
    stateField: 'state',
    note: 'Parts are fitted from the technician app on site; a fitted line is frozen (A02 audit M02-P2).' },
  'M02-vanstock': { kind: 'table_report', module: 'M02', report: 'van_stock', title: 'Van Stock Consumption', period: false },
  /* These two said "no safety-event store exists yet". fix.hse.loneworker
   * (M59) exists: the field-order slice of its sessions is listed here, and
   * "+ New" opens M59's check-in form (a dispatcher opens a session for the
   * technician on the order that sent them; the model checks that). */
  'M02-loneworker': { kind: 'model_list', model: 'fix.hse.loneworker', stateField: 'state',
    cols: ['name', 'employee_id', 'field_order_id', 'opened_by_id', 'checkin_time', 'expected_end', 'buddy_id', 'state'],
    domain: [['field_order_id', '!=', false]],
    actions: [{ m: 'action_checkout', l: 'Check Out', states: ['checked_in', 'missed', 'escalated'] }, { m: 'action_escalate', l: 'Escalate', states: ['checked_in', 'missed'] }],
    empty: 'No lone-worker session is open on a field order. A dispatcher opens one with + New for the technician on the order that sent them; the technician checks out, and a missed check-out escalates to the emergency contact.' },
  /* The technician app's panic button arrives as a 'panic_sos' command in the
   * offline journal; it is listed from there, never typed in. */
  'M02-panic': { kind: 'model_list', model: 'fix.offline.idempotency.ledger', create: false,
    cols: ['command_id', 'technician_id', 'device_id', 'status', 'client_created_at', 'applied_at'],
    domain: [['operation', '=', 'panic_sos']],
    stateField: 'status',
    empty: 'No panic alert received. A panic alert is sent from the technician app and lands here with the technician and the time; it cannot be typed in.' },
  /* On-site collection: Record Collection while on site, Hand Over Cash to an
   * open branch shift after completion. The On-Site Payment page had only two
   * reports, so the buttons that write a collection were on no page of it. */
  'M02-collect': { kind: 'model_list', model: 'fix.field.order', create: false,
    cols: ['name', 'order_id', 'technician_id', 'state', 'onsite_collection_amount', 'onsite_payment_method', 'onsite_payment_trx_id', 'onsite_payment_state', 'cash_declared_by_id', 'cash_shift_id', 'cash_accepted_by_id'],
    domain: [['state', 'in', ['arrived', 'in_progress', 'completed']]],
    stateField: 'state',
    actions: [
      { m: 'action_record_collection', l: 'Record Collection', ask: 'Method amount [TrxID], e.g. bkash 1500 8N7A6B5C or cash 900', kwarg: 'payment', states: ['arrived', 'in_progress'] },
      { m: 'action_handover_field_cash', l: 'Hand Over Cash (declare)', states: ['completed'] },
      { m: 'action_accept_field_cash', l: 'Accept Field Cash (cashier)', states: ['completed'] }
    ],
    empty: 'No field order is on site or completed. A collection is recorded while the technician is on site (arrived or working). After completion the technician declares the cash handed over, and a cashier of the service order\'s branch accepts it into that branch\'s open drawer.' },
  'M02-fieldpay': { kind: 'table_report', module: 'M02', report: 'field_payments', title: 'On-Site Payments', period: false },
  'M02-cashrec': { kind: 'table_report', module: 'M02', report: 'cash_recon', title: 'Daily Cash Reconciliation', period: false },

  /* ============ THE SIX REGISTRY BUILT-IN REPORTS (v2 forensic audit) =====
   * Every chip opens its OWN computed report over controllers/a02/m02.py. */
  'M02-rpt-dispatch': { kind: 'table_report', module: 'M02', report: 'dispatch_performance',
    title: 'Dispatch Performance by Zone', period: false },
  'M02-rpt-travel': { kind: 'table_report', module: 'M02', report: 'travel_time', title: 'Travel-Time Analysis', period: false },
  'M02-rpt-jobs': { kind: 'table_report', module: 'M02', report: 'jobs_per_technician', title: 'Jobs per Technician', period: false },
  'M02-rpt-exceptions': { kind: 'table_report', module: 'M02', report: 'field_exceptions', title: 'Field Exception Summary', period: false },
  'M02-rpt-vanstock': { kind: 'table_report', module: 'M02', report: 'van_stock', title: 'Van Stock Variance', period: false },
  'M02-rpt-pay': { kind: 'table_report', module: 'M02', report: 'field_payments', title: 'On-Site Payment Reconciliation', period: false },

  /* ============ DEDICATED ANALYTICAL SURFACES (kept, secondary) ========== */
  'M02-rpt-utilization': { kind: 'table_report', module: 'M02', report: 'technician_utilization', title: 'Technician Utilization & Travel Time', period: true },
  'M02-rpt-ftfr': { kind: 'table_report', module: 'M02', report: 'ftfr_by_skill', title: 'First-Time Fix Rate by Skill', period: true },
  'M02-rpt-geofence': { kind: 'table_report', module: 'M02', report: 'geofence_delays', title: 'Geofence Breach & Delay Log', period: false },

  /* ============ D365 IN-WORKSPACE FORM SCREENS (Audit M02) ============
   * Canonical Microsoft Dynamics 365 field forms with zero modal popups,
   * sticky command bars, sectioned enterprise cards, and WCAG 2.1 AA labels. */
  'M02-form-zone': {
    kind: 'model_form',
    model: 'fix.geofence',
    title: 'Zone Geofence',
    back: 'M02-zones',
    tabs: [
      { id: 'boundary', label: '1. Territory & Zone', bn: '১. অঞ্চল ও জোন', icon: '🗺️', badge: '4' },
      { id: 'geometry', label: '2. Fence Geometry', bn: '২. সীমানার জ্যামিতি', icon: '📐', badge: '1' }
    ],
    sections: [
      { tab: 'boundary', title: 'Geofence Territory Identity', note: 'A geofence bounds a dispatch zone: the geometry an arrival is tested against, and the zone it belongs to. The fence register is Platform Admin master data: only a Platform Admin can save one.',
        fields: [
          { name: 'name', required: true, label: 'Geofence Name' },
          { name: 'geofence_type', required: true, label: 'Geofence Type' },
          { name: 'zone_id', required: true, label: 'Dispatch Zone' },
          { name: 'active', label: 'Active' }
        ] },
      /* It said "GeoJSON": real GeoJSON fails the model's check, which reads
       * the two shapes below (fix.geofence._check_geometry). */
      { tab: 'geometry', title: 'Fence Geometry',
        note: 'A circle: {"lat": 23.7937, "lng": 90.4066, "radius_m": 500} (radius up to 100,000 m). A polygon: {"points": [[23.79, 90.40], [23.80, 90.41], [23.78, 90.42]]}, at least three latitude, longitude points. An unreadable fence refuses every arrival.',
        fields: [
          { name: 'geometry_json', required: true, type: 'text', label: 'Geometry (JSON)' }
        ] }
    ]
  },

  'M02-form-workorder': {
    kind: 'model_form',
    model: 'fix.work.order',
    title: 'Work Order',
    back: 'M02-wo',
    status: { field: 'state' },
    tabs: [
      { id: 'assignment', label: '1. Slot & Technician', bn: '১. স্লট ও টেকনিশিয়ান', icon: '👷', badge: '6' },
      { id: 'execution', label: '2. Execution Notes', bn: '২. কাজের বিবরণ', icon: '📝', badge: '1' }
    ],
    sections: [
      { tab: 'assignment', title: 'Work Order Slot & Schedule', note: 'One technician-slot on a service order: the assigned technician, the sequence on the job, the planned window and the parts consumed.',
        fields: [
          { name: 'order_id', required: true, label: 'Service Order' },
          { name: 'technician_id', label: 'Technician' },
          { name: 'sequence', label: 'Sequence' },
          { name: 'start_time', label: 'Start Time' },
          { name: 'end_time', label: 'End Time' },
          { name: 'state', label: 'State', readonly: true }
        ] },
      { tab: 'execution', title: 'Execution Notes & Directives', fields: [{ name: 'notes', type: 'text', label: 'Notes' }] }
    ]
  },

  'M02-form-wo': {
    kind: 'model_form',
    model: 'fix.field.order',
    title: 'Field Work Order',
    back: 'M02-record',
    status: { field: 'state' },
    tabs: [
      { id: 'dispatch', label: '1. Dispatch & Zone', bn: '১. ডিসপ্যাচ ও জোন', icon: '🚐', badge: '15' },
      { id: 'schedule', label: '2. Technician & SLA', bn: '২. টেকনিশিয়ান ও সময়সূচি', icon: '⏱️', badge: '6' },
      { id: 'gps', label: '3. Site GPS & Anti-Spoof', bn: '৩. জিপিএস ও অবস্থান যাচাই', icon: '📍', badge: '8' },
      { id: 'settlement', label: '4. On-Site COD & MFS', bn: '৪. অন-সাইট পেমেন্ট ও নগদ', icon: '💳', badge: '6' },
      { id: 'safety', label: '5. Lone-Worker & Evidence', bn: '৫. নিরাপত্তা ও প্রমাণক', icon: '🛡️', badge: '8' }
    ],
    sections: [
      {
        tab: 'dispatch',
        title: 'Service Order & Territory Classification',
        note: 'Select originating customer service order, dispatch territory zone, and SLA priority level. Once the order is dispatched these three are frozen: a dispatcher moves the arrival fence with Set Geofence.',
        fields: [
          { name: 'name', label: 'Field Order Ref', readonly: true },
          { name: 'order_id', required: true, label: 'Customer Service Order' },
          { name: 'priority', required: true, label: 'SLA Priority Level' },
          { name: 'zone_id', required: true, label: 'Dispatch Territory Zone' },
          { name: 'geofence_id', label: 'Geofence Boundary' }
        ]
      },
      {
        tab: 'dispatch',
        title: 'Vehicle',
        note: 'The vehicle this order travels in, and who drives it (empty = the vehicle\'s assigned driver). Dispatch runs the fleet gate on them: an uninsured or off-road vehicle, or a driver whose licence has expired, is refused, and the refusal says why.',
        fields: [
          { name: 'vehicle_id', label: 'Vehicle' },
          { name: 'vehicle_driver_id', label: 'Vehicle Driver' },
          { name: 'vehicle_assignment_id', label: 'Vehicle Booking', readonly: true }
        ]
      },
      {
        tab: 'dispatch',
        title: 'Re-Dispatch',
        note: 'Set by the fleet when the vehicle is taken off the road, and cleared when it returns or you choose another vehicle.',
        fields: [
          { name: 'redispatch_required', label: 'Re-Dispatch Required', readonly: true },
          { name: 'redispatch_offroad_id', label: 'Vehicle Off-Road Record', readonly: true },
          { name: 'redispatch_reason', label: 'Why', readonly: true, type: 'text' },
          { name: 'redispatch_flagged_at', label: 'Flagged At', readonly: true },
          { name: 'redispatch_cleared_at', label: 'Cleared At', readonly: true },
          { name: 'redispatch_cleared_by_id', label: 'Cleared By', readonly: true },
          { name: 'redispatch_clear_note', label: 'How It Was Cleared', readonly: true, type: 'text' }
        ]
      },
      {
        tab: 'schedule',
        title: 'Technician Assignment & Appointment Windows',
        note: 'The technician is assigned by Dispatch (the dispatch board or Reassign); the SLA deadline is derived from the service order and its policy.',
        fields: [
          { name: 'technician_id', label: 'Assigned Field Technician', readonly: true },
          { name: 'scheduled_start', required: true, label: 'Scheduled Start Window' },
          { name: 'scheduled_end', label: 'Scheduled End Window' },
          { name: 'sla_deadline', label: 'Guaranteed SLA Deadline', readonly: true },
          { name: 'on_time_arrival', label: 'Arrived Within SLA Window', readonly: true },
          { name: 'arrived_at', label: 'Arrived At', readonly: true }
        ]
      },
      {
        tab: 'gps',
        title: 'Customer Site Location, Haversine Distance & GNSS Anti-Spoofing (FLAW-02.2)',
        note: 'Mock GPS locations are hard-blocked at arrival check-in, and a geofenced arrival must be inside the fence. Both are set by the device and the arrival action, never on this form.',
        fields: [
          { name: 'customer_address', label: 'Service Site Address', type: 'text' },
          { name: 'latitude', label: 'Site GPS Latitude' },
          { name: 'longitude', label: 'Site GPS Longitude' },
          { name: 'is_mock_location', label: 'Mock GPS Detected (Hard Block)', readonly: true },
          { name: 'gnss_hdop', label: 'GNSS HDOP Precision', readonly: true },
          { name: 'travel_time_est_minutes', label: 'Est. Travel Time (min)' },
          { name: 'distance_km', label: 'Estimated Distance (km)' },
          { name: 'notes', label: 'Site Access & Dispatch Instructions', type: 'text' }
        ]
      },
      {
        tab: 'settlement',
        title: 'On-Site Payment Collection & M04 Cash Handover (FLAW-02.3 / HS-08)',
        note: 'Recorded with Record Collection on the Work Order Record screen. Cash is declared handed over by the technician and accepted into the branch drawer by a cashier of the service order\'s branch; the field order never marks the service order settled itself.',
        fields: [
          { name: 'onsite_collection_amount', label: 'On-Site Collection Amount (BDT)', readonly: true },
          { name: 'onsite_payment_method', label: 'On-Site Payment Channel', readonly: true },
          { name: 'onsite_payment_trx_id', label: 'MFS / POS Gateway TrxID', readonly: true },
          { name: 'onsite_payment_state', label: 'On-Site Payment Status', readonly: true },
          { name: 'cash_declared_by_id', label: 'Hand-over Declared By', readonly: true },
          { name: 'cash_declared_at', label: 'Hand-over Declared At', readonly: true },
          { name: 'cash_shift_id', label: 'Accepted Into Branch Cash Shift (M04)', readonly: true },
          { name: 'cash_accepted_by_id', label: 'Accepted By (Cashier)', readonly: true },
          { name: 'cash_handed_over_at', label: 'Accepted Into Drawer At', readonly: true }
        ]
      },
      {
        tab: 'safety',
        title: 'Lone-Worker Safety Check-In & Field Evidence Pack',
        note: 'Completion needs the customer sign-off (verified OTP or signature), a post-work photo and the work summary. The signature and photos come from the technician app.',
        fields: [
          /* M59 FR-HSE-025 / AUT-HSE-17: live hazards reported at this customer's premises */
          { name: 'hse_site_hazard_note', label: 'Customer Site Hazards (M59)', readonly: true, type: 'text' },
          { name: 'lone_worker_checkin_at', label: 'Last Safety Heartbeat At', readonly: true },
          { name: 'work_summary', label: 'On-Site Work Summary', type: 'text' },
          { name: 'customer_otp_verified', label: 'Customer OTP Verified', readonly: true },
          { name: 'customer_signature_attachment_id', label: 'Customer Signature', readonly: true },
          { name: 'customer_signature_signer', label: 'Signed By', readonly: true },
          { name: 'pre_work_photo_attachment_id', label: 'Pre-Work Site / Nameplate Photo', readonly: true },
          { name: 'post_work_photo_attachment_id', label: 'Post-Work Completion Photo', readonly: true },
          { name: 'field_job_sheet_attachment_id', label: 'Signed Field Job Sheet PDF' }
        ]
      }
    ]
  },

  /* Opens on an EXISTING order only: a row of the SLA Risk Board (FORM_CHIPS
   * __by_screen__), which has no + New, so the form is always bound to the
   * selected field order and never creates one. */
  'M02-form-reschedule': {
    kind: 'model_form',
    model: 'fix.field.order',
    title: 'Emergency Reschedule Request',
    back: 'M02-sla-risk',
    /* From the chip or the Dispatch Board page it first asks which order (a
     * reschedule never creates a field order); from an SLA Risk row it opens
     * on that order directly. */
    newLabel: 'Reschedule a Field Order',
    pickRecord: {
      label: 'Step 1 of 2: choose the field order to reschedule',
      note: 'Field orders still to be attended. A completed or cancelled order cannot be rescheduled.',
      search: 'Search field order / service order',
      choose: 'Reschedule this order',
      cols: ['name', 'order_id', 'technician_id', 'zone_id', 'scheduled_start', 'sla_deadline', 'state'],
      domain: [['state', 'in', ['draft', 'pending_dispatch', 'declined', 'dispatched', 'accepted', 'en_route']]],
      empty: 'There is no field order waiting to be attended, so there is nothing to reschedule.'
    },
    status: { field: 'state' },
    tabs: [
      { id: 'target', label: '1. Order & Territory', bn: '১. অর্ডার ও অঞ্চল', icon: '📋', badge: '4' },
      { id: 'windows', label: '2. Rescheduled Window', bn: '২. নতুন সময়সূচি', icon: '📅', badge: '3' },
      { id: 'reason', label: '3. Justification & Evidence', bn: '৩. কারণ ও প্রমাণক', icon: '📝', badge: '4' }
    ],
    sections: [
      {
        tab: 'target',
        title: 'Service Order & Territory Classification',
        note: 'The at-risk field order selected on the SLA Risk Board. Its service order stays as it is; the territory and priority may be re-allocated with the new window.',
        fields: [
          { name: 'order_id', label: 'Service Order', readonly: true },
          { name: 'zone_id', required: true, label: 'Dispatch Territory Zone' },
          { name: 'technician_id', label: 'Assigned Field Technician', readonly: true },
          { name: 'priority', label: 'Escalated SLA Priority' }
        ]
      },
      {
        tab: 'windows',
        title: 'Emergency Reschedule Appointment Windows',
        note: 'Specify the rescheduled customer arrival window. The SLA deadline is not moved by a reschedule (A02 audit M02-7).',
        fields: [
          { name: 'scheduled_start', required: true, label: 'New Scheduled Start Window' },
          { name: 'scheduled_end', label: 'New Scheduled End Window' },
          { name: 'sla_deadline', label: 'SLA Resolution Deadline', readonly: true }
        ]
      },
      {
        tab: 'reason',
        title: 'Emergency Justification & Customer Agreement',
        note: 'Document customer agreement, weather conditions, vehicle breakdown, or force majeure.',
        fields: [
          { name: 'decline_reason', label: 'Last Decline Reason', readonly: true },
          { name: 'decline_notes', label: 'Last Decline Notes', type: 'text', readonly: true },
          { name: 'notes', label: 'Safety, Route & Access Instructions', type: 'text' },
          { name: 'field_job_sheet_attachment_id', label: 'Reschedule Confirmation Attachment' }
        ]
      }
    ]
  },

  /* Registry form #2 — Field Exception Report (the coded decline record that
   * feeds the Field Exception Summary report). */
  'M02-form-exception': {
    kind: 'model_form',
    model: 'fix.field.decline.log',
    title: 'Field Exception Report',
    back: 'M02-exceptions',
    create: false, pick: 'A field exception is written by Decline on the field order: open one from Field Exceptions to add notes.',
    tabs: [
      { id: 'source', label: '1. Exception Source', bn: '১. ব্যতিক্রম উৎস', icon: '⚠️', badge: '3' },
      { id: 'resolution', label: '2. Coded Reason & Notes', bn: '২. কারণ ও মন্তব্য', icon: '📎', badge: '2' }
    ],
    sections: [
      {
        tab: 'source',
        title: 'Exception Source & Technician',
        note: 'Written by Decline on the field order; read-only here.',
        fields: [
          { name: 'field_order_id', label: 'Field Order', readonly: true },
          { name: 'technician_id', label: 'Technician', readonly: true },
          { name: 'decline_date', label: 'Exception Date', readonly: true }
        ]
      },
      {
        tab: 'resolution',
        title: 'Coded Reason & Notes',
        note: 'Every decline/exception carries a coded reason so the Field Exception Summary report can group them.',
        fields: [
          { name: 'reason', label: 'Reason Code', readonly: true },
          { name: 'notes', label: 'Notes', type: 'text' }
        ]
      }
    ]
  },

  /* Registry form #4 — Route Plan (the day's optimised route per technician). */
  'M02-form-route': {
    kind: 'model_form',
    model: 'fix.field.route',
    title: 'Route Plan',
    back: 'M02-routes',
    status: { field: 'route_state' },
    tabs: [
      { id: 'plan', label: '1. Route & Stops', bn: '১. রুট ও স্টপ', icon: '🗺️', badge: '8' },
      { id: 'metrics', label: '2. Optimisation Metrics', bn: '২. অপ্টিমাইজেশন ফলাফল', icon: '📊', badge: '5' }
    ],
    sections: [
      {
        tab: 'plan',
        title: 'Route Schedule, Technician & Stops',
        /* The stops were not on the form, and Optimise refuses a route of
         * fewer than two orders: a plan made here could never leave Draft. */
        note: 'The reference is numbered on save. Add field orders as stops, the technician\'s own or ones not yet dispatched (two or more, each with a site position), give the depot\'s position, then Optimise Route on the Route Optimisation list, Start it and Complete it there. Changing the stops or the depot clears the optimised order.',
        fields: [
          { name: 'name', label: 'Route Reference', readonly: true },
          { name: 'technician_id', required: true, label: 'Technician' },
          { name: 'date', required: true, label: 'Route Date' },
          { name: 'field_order_ids', label: 'Stops (field orders)', domain: [['state', 'in', ['draft', 'pending_dispatch', 'dispatched', 'accepted', 'en_route']]] },
          { name: 'depot_location', label: 'Starting Depot / Hub' },
          /* A02 ERP audit M02-F11: the route starts from its own depot position */
          { name: 'depot_latitude', label: 'Depot Latitude' },
          { name: 'depot_longitude', label: 'Depot Longitude' },
          { name: 'notes', type: 'text', label: 'Route Notes' }
        ]
      },
      {
        tab: 'metrics',
        title: 'Measured Route Optimisation Outcome',
        note: 'Build the plan from the Route Optimisation screen (action_optimize_route), then start and complete it here.',
        fields: [
          { name: 'order_count', label: 'Stops', readonly: true },
          { name: 'total_distance_km', label: 'Total Distance (km)', readonly: true },
          { name: 'total_duration_hours', label: 'Total Duration (h)', readonly: true },
          { name: 'improvement_pct', label: 'Optimisation Gain %', readonly: true },
          { name: 'stop_plan', type: 'text', label: 'Optimised Stop Order', readonly: true }
        ]
      }
    ]
  },

  /* ===== triage coverage screens ===== */
  /* A GPS ping is the technician app's telemetry, anti-spoof checked: typing one
   * here, or editing a ping's coordinates, fabricates tracking (2026-11-12). */
  'M02-technician-location': { kind: 'model_list', model: 'fix.technician.location', create: false,
    cols: ['name', 'company_id', 'operating_unit_id', 'name_bn', 'technician_id', 'latitude', 'longitude', 'is_mock_location', 'gnss_hdop'],
    empty: 'No GPS ping received yet. Pings arrive from the technician mobile app while a technician is on duty; they are tracking evidence and cannot be typed in. A break or the end of duty is recorded with + New Tracking Pause: no position is kept while it runs.' },

  'M02-form-technician-location': {
    kind: 'model_form',
    model: 'fix.technician.location',
    title: "Technician Location",
    back: 'M02-technician-location',
    create: false, pick: 'A GPS ping comes from the technician mobile app: open one from Technician Locations.',
    tabs: [
      { id: 'ping', label: '1. GPS Coordinates', bn: '১. জিপিএস স্থানাঙ্ক', icon: '📡', badge: '7' },
      { id: 'telemetry', label: '2. Anti-Spoof & Device Health', bn: '২. অ্যান্টি-স্পুফ ও টেলিমেট্রি', icon: '🛡️', badge: '4' }
    ],
    sections: [
      { tab: 'ping', title: "Technician GPS Ping Identity", note: "Every field here is the model's real field; the workflow rules live on the model and are not bypassed by this form.",
        fields: [
          { name: 'name', label: "Ping Reference", readonly: true },
          { name: 'name_bn', label: "Ping Reference (Bengali)", readonly: true },
          { name: 'company_id', label: "Company", readonly: true },
          { name: 'operating_unit_id', label: "Operating Unit", readonly: true },
          { name: 'technician_id', label: "Technician", readonly: true },
          { name: 'latitude', label: "Latitude", readonly: true },
          { name: 'longitude', label: "Longitude", readonly: true }
        ] },
      { tab: 'telemetry', title: "GNSS Anti-Spoofing & Mobile Telemetry (FLAW-02.2)",
        fields: [
          { name: 'is_mock_location', label: "Mock Location Flagged", readonly: true },
          { name: 'gnss_hdop', label: "GNSS HDOP Precision", readonly: true },
          { name: 'speed_kmh', label: "Speed (km/h)", readonly: true },
          { name: 'battery_pct', label: "Device Battery (%)", readonly: true }
        ] }
    ]
  },

  /* ============ CAPTURE REGISTERS (second capture pass, 2026-11-18) =====
   * Each list below is the record one sub-module page now captures. The
   * model checks who may write it; the lists only show and call it. */
  'M02-decisions': { kind: 'model_list', title: 'Dispatch Decisions', title_bn: 'ডিসপ্যাচ সিদ্ধান্ত', model: 'fix.dispatch.decision',
    cols: ['name', 'field_order_id', 'technician_id', 'recommended_technician_id', 'selected_rank', 'is_override', 'override_reason', 'decided_by_id', 'decided_at'],
    empty: 'No dispatch decided here yet. + New Dispatch Decision sends a waiting field order to a technician and keeps what the engine ranked first; sending anyone else needs the override reason (BRU-FSM-04).' },
  'M02-devices': { kind: 'model_list', title: 'Technician Devices', title_bn: 'টেকনিশিয়ান ডিভাইস', model: 'fix.technician.device', stateField: 'state',
    cols: ['device_uid', 'employee_id', 'platform', 'device_model', 'app_version', 'state', 'enrolled_at', 'last_sync_at', 'revoke_reason', 'revoked_at'],
    actions: [
      { m: 'action_revoke', l: 'Revoke Device (dispatcher)', ask: 'Reason (lost, stolen, departed, replaced or compromised), then any notes', kwarg: 'revoke', states: ['enrolled'] }
    ],
    empty: 'No device enrolled. A dispatcher enrols each technician phone with + New Technician Device; a revoked phone can no longer sync (T-11).' },
  'M02-conflict-reviews': { kind: 'model_list', title: 'Conflict Reviews', title_bn: 'দ্বন্দ্ব পর্যালোচনা', model: 'fix.offline.conflict.review',
    cols: ['name', 'ledger_id', 'technician_id', 'operation', 'entry_status', 'decision', 'reviewed_by_id', 'reviewed_at'],
    empty: 'No conflict reviewed yet. A rejected or conflicted replay in the offline journal is reviewed with + New Conflict Review, by someone other than the technician who sent it.' },
  'M02-pauses': { kind: 'model_list', title: 'Tracking Pauses', title_bn: 'ট্র্যাকিং বিরতি', model: 'fix.tracking.pause', stateField: 'state',
    cols: ['name', 'employee_id', 'reason', 'started_at', 'planned_end', 'ended_at', 'state'],
    actions: [{ m: 'action_end', l: 'End Pause', states: ['active'] }],
    empty: 'No tracking pause. A technician (or a dispatcher for them) records a break or the end of duty with + New Tracking Pause; no position is stored while it runs (BRU-FSM-05).' },
  'M02-failed-visits': { kind: 'model_list', title: 'Failed Visits', title_bn: 'ব্যর্থ ভিজিট', model: 'fix.field.visit.exception',
    cols: ['name', 'field_order_id', 'technician_id', 'exception_type', 'follow_up', 'distance_from_site_m', 'recorded_at'],
    empty: 'No failed visit. The technician sent to the site records one with + New Failed Visit Report, with a photo and the position it was taken at (BRU-FSM-09); the order returns to the dispatch queue.' },
  'M02-field-cash': { kind: 'model_list', title: 'Field Cash Reconciliation', title_bn: 'ফিল্ড নগদ মিলকরণ', model: 'fix.field.cash.recon', stateField: 'state',
    cols: ['name', 'employee_id', 'recon_date', 'order_count', 'cash_collected', 'cash_handed_over', 'cash_outstanding', 'counted_amount', 'variance', 'state', 'confirmed_by_id'],
    actions: [
      { m: 'action_submit', l: 'Submit Count', states: ['draft'] },
      { m: 'action_confirm', l: 'Confirm (dispatcher / finance)', states: ['submitted'] }
    ],
    empty: 'No field cash day reconciled. + New Field Cash Reconciliation takes one technician\'s day: the cash their completed jobs collected and what reached a branch shift come from the jobs; the technician counts what they still hold, and someone else confirms (BRU-FSM-07).' },

  'M02-form-decision': {
    kind: 'model_form',
    model: 'fix.dispatch.decision',
    title: 'Dispatch Decision',
    back: 'M02-decisions',
    tabs: [
      { id: 'send', label: '1. Order & Technician', bn: '১. অর্ডার ও টেকনিশিয়ান', icon: '🚐', badge: '2' },
      { id: 'override', label: '2. Override Reason', bn: '২. ব্যতিক্রমের কারণ', icon: '📝', badge: '2' },
      { id: 'engine', label: '3. What The Engine Ranked', bn: '৩. সুপারিশ', icon: '📊', badge: '6' }
    ],
    sections: [
      { tab: 'send', title: 'Order To Dispatch',
        note: 'Saving dispatches the order to this technician, through the same checks as the dispatch board: availability (M55), certification (M22) and the vehicle gate (M46). The decision cannot be edited afterwards.',
        fields: [
          { name: 'field_order_id', required: true, label: 'Field Order (waiting for dispatch)', domain: [['state', 'in', ['draft', 'pending_dispatch', 'declined']]] },
          { name: 'technician_id', required: true, label: 'Technician To Send' }
        ] },
      { tab: 'override', title: 'Override Reason (BRU-FSM-04)',
        note: 'Needed only when the technician is not the engine\'s first choice: the save is refused without it, and the reason feeds the assignment model.',
        fields: [
          { name: 'override_reason', label: 'Override Reason' },
          { name: 'override_notes', type: 'text', label: 'Override Notes (required for Other)' }
        ] },
      { tab: 'engine', title: 'Recommendation At The Time Of The Decision',
        note: 'Filled on save from the suggestion engine\'s ranking.',
        fields: [
          { name: 'name', label: 'Reference', readonly: true },
          { name: 'recommended_technician_id', label: 'Recommended Technician', readonly: true },
          { name: 'recommended_score', label: 'Recommended Score', readonly: true },
          { name: 'selected_rank', label: 'Rank Of Technician Sent', readonly: true },
          { name: 'is_override', label: 'Overrode The Recommendation', readonly: true },
          { name: 'explanation', type: 'text', label: 'Why The Engine Recommended', readonly: true }
        ] }
    ]
  },

  'M02-form-device': {
    kind: 'model_form',
    model: 'fix.technician.device',
    title: 'Technician Device',
    back: 'M02-devices',
    status: { field: 'state' },
    sections: [
      { title: 'Device Enrolment (FR-FSM-064, T-11)',
        note: 'Enrolled by a dispatcher. The Device ID is the one the technician app shows under Settings; it is sent with every sync. A lost or replaced phone is revoked on the Technician Devices list and the new one enrolled as a new device.',
        fields: [
          { name: 'employee_id', required: true, label: 'Technician' },
          { name: 'device_uid', required: true, label: 'Device ID' },
          { name: 'platform', required: true, label: 'Platform' },
          { name: 'device_model', label: 'Handset Model' },
          { name: 'app_version', label: 'App Version' },
          { name: 'state', label: 'Status', readonly: true },
          { name: 'last_sync_at', label: 'Last Sync', readonly: true }
        ] }
    ]
  },

  'M02-form-conflict': {
    kind: 'model_form',
    model: 'fix.offline.conflict.review',
    title: 'Offline Conflict Review',
    back: 'M02-conflict-reviews',
    sections: [
      { title: 'Journal Entry Reviewed (AUT-FSM-06)',
        note: 'Only a replay the server rejected or applied with a conflict. The journal entry itself is evidence and does not change; this review records what was done about it. The technician who sent the command does not review it.',
        fields: [
          { name: 'ledger_id', required: true, label: 'Journal Entry', domain: [['status', 'in', ['rejected', 'conflict_applied']]] },
          { name: 'decision', required: true, label: 'Decision' },
          { name: 'notes', required: true, type: 'text', label: 'What Was Done' },
          { name: 'technician_id', label: 'Technician', readonly: true },
          { name: 'operation', label: 'Command', readonly: true },
          { name: 'conflict_reason', type: 'text', label: 'Conflict / Rejection Reason', readonly: true }
        ] }
    ]
  },

  'M02-form-pause': {
    kind: 'model_form',
    model: 'fix.tracking.pause',
    title: 'Tracking Pause',
    back: 'M02-pauses',
    sections: [
      { title: 'Break Or End Of Duty (BRU-FSM-05)',
        note: 'No position is stored from the start until the end (at most 14 hours), and the app shows that tracking is paused. A pause starts now or later: positions already recorded stay. End it early with End Pause.',
        fields: [
          { name: 'employee_id', required: true, label: 'Technician' },
          { name: 'reason', required: true, label: 'Reason' },
          { name: 'started_at', required: true, label: 'From' },
          { name: 'planned_end', required: true, label: 'Until' }
        ] }
    ]
  },

  'M02-form-failedvisit': {
    kind: 'model_form',
    model: 'fix.field.visit.exception',
    title: 'Failed Visit Report',
    back: 'M02-failed-visits',
    tabs: [
      { id: 'visit', label: '1. Visit & Outcome', bn: '১. ভিজিট ও ফলাফল', icon: '🚪', badge: '4' },
      { id: 'evidence', label: '2. Site Evidence', bn: '২. সাইটের প্রমাণ', icon: '📷', badge: '4' }
    ],
    sections: [
      { tab: 'visit', title: 'What Happened At The Site (FR-FSM-037/038)',
        note: 'Recorded by the technician the order was sent to, on the way or at the site. Saving returns the order to the dispatch queue for the follow-up; it cannot be edited afterwards.',
        fields: [
          { name: 'field_order_id', required: true, label: 'Field Order', domain: [['state', 'in', ['en_route', 'arrived', 'in_progress']]] },
          { name: 'exception_type', required: true, label: 'What Happened' },
          { name: 'reason', required: true, type: 'text', label: 'Details' },
          { name: 'follow_up', required: true, label: 'Follow-Up' }
        ] },
      { tab: 'evidence', title: 'Geotagged Evidence (BRU-FSM-09)',
        note: 'A photo taken at the customer\'s site, and the position it was taken at: within 1 km of the site on the order, or the save is refused.',
        fields: [
          { name: 'evidence_photo', required: true, type: 'binary', filename: 'evidence_photo_name', label: 'Site Photo' },
          { name: 'evidence_photo_name', label: 'Photo File Name' },
          { name: 'latitude', required: true, label: 'Latitude' },
          { name: 'longitude', required: true, label: 'Longitude' }
        ] }
    ]
  },

  'M02-form-cashrecon': {
    kind: 'model_form',
    model: 'fix.field.cash.recon',
    title: 'Field Cash Reconciliation',
    back: 'M02-field-cash',
    status: { field: 'state' },
    tabs: [
      { id: 'day', label: '1. Technician & Count', bn: '১. টেকনিশিয়ান ও গণনা', icon: '💵', badge: '4' },
      { id: 'jobs', label: '2. From The Jobs', bn: '২. কাজের হিসাব', icon: '📋', badge: '6' }
    ],
    sections: [
      { tab: 'day', title: 'The Technician\'s Day (FR-FSM-056)',
        note: 'One record per technician per day. Count the cash still held; a difference from the jobs needs an explanation. Submit Count and Confirm are on the Field Cash list, and the confirmer is not the technician or whoever submitted.',
        fields: [
          { name: 'employee_id', required: true, label: 'Technician' },
          { name: 'recon_date', required: true, label: 'Day' },
          { name: 'counted_amount', label: 'Cash In Hand (Counted, BDT)' },
          { name: 'variance_reason', type: 'text', label: 'Variance Explanation' }
        ] },
      { tab: 'jobs', title: 'Measured From The Day\'s Completed Cash Jobs',
        note: 'Taken from the field orders, never typed.',
        fields: [
          { name: 'order_count', label: 'Cash Jobs', readonly: true },
          { name: 'cash_collected', label: 'Cash Collected', readonly: true },
          { name: 'cash_handed_over', label: 'Handed To A Branch Shift', readonly: true },
          { name: 'cash_outstanding', label: 'Still With The Technician', readonly: true },
          { name: 'variance', label: 'Variance', readonly: true },
          { name: 'order_refs', type: 'text', label: 'Jobs Counted', readonly: true }
        ] }
    ]
  },

};

/* Built-in report chips -> dedicated in-workspace table_report screen */
export const REPORT_ROUTES = {
  "M02:Dispatch Performance by Zone": "M02-rpt-dispatch",
  "M02:Travel-Time Analysis": "M02-rpt-travel",
  "M02:Jobs per Technician": "M02-rpt-jobs",
  "M02:Field Exception Summary": "M02-rpt-exceptions",
  "M02:Van Stock Variance": "M02-rpt-vanstock",
  "M02:On-Site Payment Reconciliation": "M02-rpt-pay",
  "M02:Technician Utilization & Travel Time": "M02-rpt-utilization",
  "M02:First-Time Fix Rate by Skill": "M02-rpt-ftfr",
  "M02:Geofence Breach & Delay Log": "M02-rpt-geofence"
};

/* Data-entry form chips: the registry's four forms, each a D365 in-workspace
 * model_form screen (zero modal popups). Labelled with the registry names —
 * the older prototype chip labels were drift (v2 forensic audit). */
/* 'Crew Assignment' opened the FIELD order form, which has no crew field: a
 * crew is two or more technician work orders on one service order (the Crews
 * report measures exactly that), so it adds a technician work order.
 * Records another module masters open THAT module's form (M38 does the same
 * for promotions): van counts M15, lone-worker sessions M59, zones M30. */
export const FORM_CHIPS = {
  'M02:Field Work Order': 'M02-form-wo',
  'M02:Field Exception Report': 'M02-form-exception',
  'M02:Crew Assignment': 'M02-form-workorder',
  'M02:Technician Work Order': 'M02-form-workorder',
  'M02:Route Plan': 'M02-form-route',
  'M02:Emergency Reschedule Request': 'M02-form-reschedule',
  'M02:Zone Geofence': 'M02-form-zone',
  'M02:Dispatch Zone': 'M30-form-zone',
  'M02:Van Stock Reconciliation': 'M15-form-recon',
  'M02:Lone-Worker Check-In': 'M59-form-loneworker',
  /* FR-FSM-059: an accident, hazard or abuse in the field goes to M59 */
  'M02:Field Incident Report': 'M59-form-incident',
  /* second capture pass (2026-11-18): the six capture registers */
  'M02:Dispatch Decision': 'M02-form-decision',
  'M02:Technician Device': 'M02-form-device',
  'M02:Offline Conflict Review': 'M02-form-conflict',
  'M02:Tracking Pause': 'M02-form-pause',
  'M02:Failed Visit Report': 'M02-form-failedvisit',
  'M02:Field Cash Reconciliation': 'M02-form-cashrecon',
  'M02:__by_model__': {
    'fix.geofence': 'M02-form-zone',
    'fix.technician.location': 'M02-form-technician-location',
    'fix.field.order': 'M02-form-wo',
    'fix.field.decline.log': 'M02-form-exception',
    'fix.field.route': 'M02-form-route',
    'fix.work.order': 'M02-form-workorder',
    'fix.stock.van.recon': 'M15-form-recon',
    'fix.hse.loneworker': 'M59-form-loneworker',
    'fix.dispatch.decision': 'M02-form-decision',
    'fix.technician.device': 'M02-form-device',
    'fix.offline.conflict.review': 'M02-form-conflict',
    'fix.tracking.pause': 'M02-form-pause',
    'fix.field.visit.exception': 'M02-form-failedvisit',
    'fix.field.cash.recon': 'M02-form-cashrecon'
  },
  'M02:__by_screen__': {
    'M02-wo': 'M02-form-workorder',
    'M02-zones': 'M02-form-zone',
    'M02-record': 'M02-form-wo',
    'M02-exceptions': 'M02-form-exception',
    'M02-routes': 'M02-form-route',
    'M02-sla-risk': 'M02-form-reschedule',
    'M02-loneworker': 'M59-form-loneworker',
    'M02-decisions': 'M02-form-decision',
    'M02-devices': 'M02-form-device',
    'M02-conflict-reviews': 'M02-form-conflict',
    'M02-pauses': 'M02-form-pause',
    'M02-failed-visits': 'M02-form-failedvisit',
    'M02-field-cash': 'M02-form-cashrecon'
  }
};

export const FORM_MODELS = {
  'M02:Field Work Order': 'fix.field.order',
  'M02:Field Exception Report': 'fix.field.decline.log',
  'M02:Crew Assignment': 'fix.work.order',
  'M02:Technician Work Order': 'fix.work.order',
  'M02:Route Plan': 'fix.field.route',
  'M02:Emergency Reschedule Request': 'fix.field.order',
  'M02:Zone Geofence': 'fix.geofence',
  'M02:Dispatch Zone': 'fix.zone',
  'M02:Van Stock Reconciliation': 'fix.stock.van.recon',
  'M02:Lone-Worker Check-In': 'fix.hse.loneworker',
  'M02:Field Incident Report': 'fix.hse.incident',
  'M02:Dispatch Decision': 'fix.dispatch.decision',
  'M02:Technician Device': 'fix.technician.device',
  'M02:Offline Conflict Review': 'fix.offline.conflict.review',
  'M02:Tracking Pause': 'fix.tracking.pause',
  'M02:Failed Visit Report': 'fix.field.visit.exception',
  'M02:Field Cash Reconciliation': 'fix.field.cash.recon'
};

/* The module's "+ New" surface: opens the canonical Dynamics 365 Create Field Work Order form */
export const CREATE = {
  M02: { screen: 'M02-form-wo', model: 'fix.field.order', label: 'Field Work Order' }
};
