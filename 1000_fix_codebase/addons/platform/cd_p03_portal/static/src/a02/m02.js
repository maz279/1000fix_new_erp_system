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
 * Create Field Work Order, Technician Dispatch Override, and Emergency Reschedule
 * render INSIDE the workspace with sticky command bars, zero modal popups,
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
      { id: 'M02-sla-risk', en: 'SLA Risk Board', bn: 'এসএলএ ঝুঁকি', t: 'g' }
    ]},
    { en: 'Work Orders', screens: [
      { id: 'M02-wo', en: 'Field Work Orders', bn: 'ফিল্ড ওয়ার্ক অর্ডার', t: 'g' },
      { id: 'M02-record', en: 'Work Order Record', bn: 'ওয়ার্ক অর্ডার নথি', t: 'f' },
      { id: 'M02-exceptions', en: 'Field Exceptions', bn: 'ফিল্ড ব্যতিক্রম', t: 'g' },
      { id: 'M02-crews', en: 'Crews & Multi-Tech Jobs', bn: 'ক্রু নিয়োগ', t: 'g' }
    ]},
    { en: 'Routing & Territories', screens: [
      { id: 'M02-zones', en: 'Zones & Geofences', bn: 'জোন ও জিওফেন্স', t: 'g' },
      { id: 'M02-routes', en: 'Route Optimisation', bn: 'রুট অপ্টিমাইজেশন', t: 'c' },
      { id: 'M02-territory', en: 'Territory Balancing', bn: 'টেরিটরি সমন্বয়', t: 'r' }
    ]},
    { en: 'Technician App (P02)', screens: [
      { id: 'M02-day', en: 'Day / Job Queue Preview', bn: 'দিনের কাজ', t: 'd' },
      { id: 'M02-offline', en: 'Offline Sync Monitor', bn: 'অফলাইন সিঙ্ক', t: 'g' },
      { id: 'M02-evidence', en: 'Field Evidence Hub', bn: 'ফিল্ড প্রমাণ', t: 'g' },
      { id: 'M02-vanstock', en: 'Van Stock Consumption', bn: 'ভ্যান স্টক', t: 'g' }
    ]},
    { en: 'Safety & Payments', screens: [
      { id: 'M02-loneworker', en: 'Lone-Worker Check-In', bn: 'একাকী কর্মী নিরাপত্তা', t: 'g' },
      { id: 'M02-panic', en: 'Panic Alert Log', bn: 'প্যানিক অ্যালার্ট', t: 'g' },
      { id: 'M02-fieldpay', en: 'On-Site Payments', bn: 'স্থানে পেমেন্ট', t: 'g' },
      { id: 'M02-cashrec', en: 'Daily Cash Reconciliation', bn: 'নগদ মিলকরণ', t: 'c' }
    ]}
  ],
  reports: ['Dispatch Performance by Zone', 'Travel-Time Analysis', 'Jobs per Technician', 'Field Exception Summary', 'Van Stock Variance', 'On-Site Payment Reconciliation', 'Technician Utilization & Travel Time', 'First-Time Fix Rate by Skill', 'Geofence Breach & Delay Log'],
  forms: ['Field Work Order', 'Field Exception Report', 'Crew Assignment', 'Route Plan'],
  cross: ['M01 order → work order', 'M55 availability & roster', 'M22 certification gate', 'M03 logistics handover', 'M17 asset context'],
  freg: {
    src: 106,
    sub: [
      ['1', 'Candidate Scoring & Assignment', 14, { model: 'fix.field.order', cols: ['name', 'zone_id', 'priority', 'scheduled_start', 'technician_id'], screens: ['M02-unassigned', 'M02-exceptions'], domain: [['state', 'in', ['draft', 'pending_dispatch', 'declined']]] }],
      ['2', 'Dispatch Board', 10, { model: 'fix.field.order', cols: ['name', 'technician_id', 'state', 'sla_deadline', 'dispatched_at'], screens: ['M02-dispatch', 'M02-sla-risk'], domain: [['state', 'in', ['dispatched', 'accepted', 'en_route', 'arrived', 'in_progress']]] }],
      ['3', 'Route Optimisation & Re-optimisation', 9, { model: 'fix.field.route', cols: ['name', 'technician_id', 'date', 'total_distance_km', 'improvement_pct'], screens: ['M02-routes'] }],
      ['4', 'Territory / Zone / Geofence', 8, { model: 'fix.geofence', cols: ['name', 'zone_id', 'geofence_type', 'active'], screens: ['M02-zones', 'M02-territory'] }],
      ['5', 'Work-Order Lifecycle', 9, { model: 'fix.field.order', cols: ['name', 'state', 'dispatched_at', 'arrived_at', 'completed_at'], screens: ['M02-record', 'M02-wo', 'M02-crews'] }],
      ['6', 'Technician Mobile App', 18, { model: 'fix.work.order', cols: ['name', 'technician_id', 'sequence', 'state', 'start_time'], screens: ['M02-day', 'M02-wo'] }],
      ['7', 'Offline Sync & Conflict Resolution', 7, { model: 'fix.offline.idempotency.ledger', cols: ['command_id', 'technician_id', 'operation', 'status', 'applied_at'], screens: ['M02-offline'] }],
      ['8', 'GPS Tracking & ETA', 7, { model: 'fix.technician.location', cols: ['technician_id', 'timestamp', 'latitude', 'longitude', 'speed_kmh'], screens: ['M02-map', 'M02-technician-location'] }],
      ['9', 'Field Evidence Capture', 6, { model: 'fix.workshop.evidence', cols: ['name', 'job_id', 'evidence_type', 'captured_by_id', 'captured_at'], screens: ['M02-evidence'] }],
      ['10', 'Van Stock', 5, { model: 'fix.stock.van.recon', cols: ['name', 'technician_id', 'recon_date', 'variance', 'state'], screens: ['M02-vanstock'] }],
      ['11', 'On-Site Payment', 6, { model: 'fix.field.order', cols: ['name', 'onsite_collection_amount', 'onsite_payment_method', 'onsite_payment_trx_id', 'customer_otp_verified'], screens: ['M02-fieldpay', 'M02-cashrec'], domain: [['onsite_payment_method', 'in', ['cash', 'bkash', 'nagad', 'sslcommerz', 'corporate_credit']]] }],
      ['12', 'Field Safety', 7, { model: 'fix.hse.loneworker', cols: ['name', 'employee_id', 'checkin_time', 'expected_end', 'state'], screens: ['M02-loneworker', 'M02-panic'] }]
    ]
  }
};

/* In-workspace data screens. fs_board/fs_list are the bespoke dispatch
 * surfaces; model_list rides the whitelisted generic reader; table_report
 * calls the module REPORTS. */
export const SCREENS = {
  'M02-dispatch': { kind: 'fs_board' },
  'M02-map': { kind: 'fs_map' },
  'M02-unassigned': { kind: 'model_list', model: 'fix.field.order', create: false,
    cols: ['name', 'order_id', 'zone_id', 'priority', 'scheduled_start', 'state', 'technician_id'],
    domain: [['state', 'in', ['draft', 'pending_dispatch', 'declined']]],
    stateField: 'state' },
  'M02-sla-risk': { kind: 'model_list', model: 'fix.field.order', create: false,
    cols: ['name', 'order_id', 'zone_id', 'priority', 'sla_deadline', 'scheduled_start', 'state', 'technician_id'],
    domain: [['state', 'in', ['pending_dispatch', 'dispatched', 'accepted', 'en_route', 'arrived', 'in_progress']], ['sla_deadline', '!=', false]] },
  'M02-wo': { kind: 'model_list', model: 'fix.work.order',
    cols: ['name', 'order_id', 'technician_id', 'sequence', 'state', 'start_time', 'end_time', 'duration_hours'],
    stateField: 'state' },
  'M02-record': { kind: 'model_list', model: 'fix.field.order', create: false,
    cols: ['name', 'order_id', 'technician_id', 'zone_id', 'scheduled_start', 'state',
      'dispatched_at', 'arrived_at', 'actual_travel_minutes', 'on_time_arrival', 'completed_at'],
    stateField: 'state' },
  'M02-exceptions': { kind: 'model_list', model: 'fix.field.decline.log',
    cols: ['name', 'field_order_id', 'technician_id', 'reason', 'decline_date', 'notes'] },
  'M02-crews': { kind: 'table_report', module: 'M02', report: 'crews',
    title: 'Crews & Multi-Tech Jobs', period: false },
  'M02-zones': { kind: 'model_list', model: 'fix.geofence',
    cols: ['name', 'zone_id', 'geofence_type', 'active'] },
  'M02-routes': { kind: 'model_list', model: 'fix.field.route',
    cols: ['name', 'technician_id', 'date', 'order_count', 'total_distance_km', 'total_duration_hours', 'improvement_pct', 'route_state'],
    stateField: 'route_state' },
  'M02-territory': { kind: 'table_report', module: 'M02', report: 'zone_workload', title: 'Territory Workload Balance', period: false },

  /* ============ TECHNICIAN APP (P02) + SAFETY & PAYMENTS (registry v2) ====
   * The eight registry screens that had no surface. Each renders from a real
   * model or a measured report; the two safety screens state their honest
   * absence (no safety-event store yet — the P02 app stream is the source). */
  'M02-day': { kind: 'table_report', module: 'M02', report: 'day_queue', title: 'Day / Job Queue Preview', period: false },
  'M02-offline': { kind: 'model_list', model: 'fix.offline.idempotency.ledger', create: false,
    cols: ['command_id', 'technician_id', 'device_id', 'model', 'operation', 'status', 'conflict_reason', 'client_created_at', 'applied_at'],
    stateField: 'status' },
  'M02-evidence': { kind: 'model_list', model: 'fix.workshop.evidence', create: false,
    cols: ['name', 'job_id', 'evidence_type', 'captured_by_id', 'captured_at', 'description'],
    stateField: 'evidence_type' },
  'M02-vanstock': { kind: 'table_report', module: 'M02', report: 'van_stock', title: 'Van Stock Consumption', period: false },
  'M02-loneworker': { kind: 'table_report', module: 'M02', report: 'lone_worker', title: 'Lone-Worker Check-In', period: false },
  'M02-panic': { kind: 'table_report', module: 'M02', report: 'panic_alerts', title: 'Panic Alert Log', period: false },
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
      { id: 'geometry', label: '2. GeoJSON Polygon', bn: '২. জিওজেসন বহুভুজ', icon: '📐', badge: '1' }
    ],
    sections: [
      { tab: 'boundary', title: 'Geofence Territory Identity', note: 'A geofence bounds a dispatch zone: the geometry the P02 app tests a technician position against, and the zone it belongs to.',
        fields: [
          { name: 'name', required: true, label: 'Geofence Name' },
          { name: 'geofence_type', required: true, label: 'Geofence Type' },
          { name: 'zone_id', required: true, label: 'Dispatch Zone' },
          { name: 'active', label: 'Active' }
        ] },
      { tab: 'geometry', title: 'GeoJSON Polygon Coordinates',
        fields: [
          { name: 'geometry_json', required: true, type: 'text', label: 'Geometry (GeoJSON)' }
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
          { name: 'state', required: true, label: 'State' }
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
      { id: 'dispatch', label: '1. Dispatch & Zone', bn: '১. ডিসপ্যাচ ও জোন', icon: '🚐', badge: '6' },
      { id: 'schedule', label: '2. Technician & SLA', bn: '২. টেকনিশিয়ান ও সময়সূচি', icon: '⏱️', badge: '6' },
      { id: 'gps', label: '3. Site GPS & Anti-Spoof', bn: '৩. জিপিএস ও অবস্থান যাচাই', icon: '📍', badge: '8' },
      { id: 'settlement', label: '4. On-Site COD & MFS', bn: '৪. অন-সাইট পেমেন্ট ও নগদ', icon: '💳', badge: '6' },
      { id: 'safety', label: '5. Lone-Worker & Evidence', bn: '৫. নিরাপত্তা ও প্রমাণক', icon: '🛡️', badge: '5' }
    ],
    sections: [
      {
        tab: 'dispatch',
        title: 'Service Order & Territory Classification',
        note: 'Select originating customer service order, dispatch territory zone, and SLA priority level.',
        fields: [
          { name: 'name', label: 'Field Order Ref', readonly: true },
          { name: 'order_id', required: true, label: 'Customer Service Order' },
          { name: 'priority', required: true, label: 'SLA Priority Level' },
          { name: 'zone_id', required: true, label: 'Dispatch Territory Zone' },
          { name: 'geofence_id', label: 'Geofence Boundary' },
          { name: 'van_stock_verified', label: 'Van Stock Pre-Trip Verified (FLAW-02.1)' }
        ]
      },
      {
        tab: 'schedule',
        title: 'Technician Assignment & Appointment Windows',
        note: 'Assign a qualified field engineer and specify the customer service arrival window.',
        fields: [
          { name: 'technician_id', label: 'Assigned Field Technician' },
          { name: 'helper_technician_id', label: 'Crew Helper / Co-Technician' },
          { name: 'scheduled_start', required: true, label: 'Scheduled Start Window' },
          { name: 'scheduled_end', label: 'Scheduled End Window' },
          { name: 'sla_deadline', label: 'Guaranteed SLA Deadline' },
          { name: 'on_time_arrival', label: 'Arrived Within SLA Window', readonly: true }
        ]
      },
      {
        tab: 'gps',
        title: 'Customer Site Location, Haversine Distance & GNSS Anti-Spoofing (FLAW-02.2)',
        note: 'Mock GPS locations are hard-blocked at arrival check-in. GNSS HDOP measures satellite fix precision.',
        fields: [
          { name: 'customer_address', label: 'Service Site Address', type: 'text' },
          { name: 'latitude', label: 'Site GPS Latitude' },
          { name: 'longitude', label: 'Site GPS Longitude' },
          { name: 'is_mock_location', label: 'Mock GPS Detected (Hard Block)' },
          { name: 'gnss_hdop', label: 'GNSS HDOP Precision' },
          { name: 'travel_time_est_minutes', label: 'Est. Travel Time (min)' },
          { name: 'distance_km', label: 'Estimated Distance (km)' },
          { name: 'notes', label: 'Site Access & Dispatch Instructions', type: 'text' }
        ]
      },
      {
        tab: 'settlement',
        title: 'On-Site Payment Collection & M04 Cash Handover (FLAW-02.3 / HS-08)',
        note: 'bKash/Nagad/Rocket/Upay collections require a verified Gateway TrxID before job completion.',
        fields: [
          { name: 'onsite_collection_amount', label: 'On-Site Collection Amount (BDT)' },
          { name: 'onsite_payment_method', label: 'On-Site Payment Channel' },
          { name: 'onsite_payment_trx_id', label: 'MFS / POS Gateway TrxID' },
          { name: 'cash_shift_id', label: 'Handed Over to Branch Cash Shift (M04)' },
          { name: 'cash_handed_over_at', label: 'Cash Handover Timestamp', readonly: true },
          { name: 'customer_signature_captured', label: 'Customer Digital Signature Captured' }
        ]
      },
      {
        tab: 'safety',
        title: 'Lone-Worker Safety Check-In & Field Evidence Pack',
        fields: [
          { name: 'safety_checkin_status', label: 'Lone-Worker Safety Status' },
          { name: 'last_safety_ping_at', label: 'Last Safety Heartbeat At' },
          { name: 'pre_work_photo_attachment_id', label: 'Pre-Work Site / Nameplate Photo' },
          { name: 'post_work_photo_attachment_id', label: 'Post-Work Completion Photo' },
          { name: 'signed_job_sheet_attachment_id', label: 'Signed Field Job Sheet PDF' }
        ]
      }
    ]
  },

  'M02-form-override': {
    kind: 'model_form',
    model: 'fix.field.decline.log',
    title: 'Technician Dispatch Override',
    back: 'M02-exceptions',
    tabs: [
      { id: 'target', label: '1. Order & Technician', bn: '১. অর্ডার ও টেকনিশিয়ান', icon: '👷', badge: '4' },
      { id: 'justification', label: '2. Override & Evidence', bn: '২. অনুমোদন ও প্রমাণক', icon: '🔐', badge: '4' }
    ],
    sections: [
      {
        tab: 'target',
        title: 'Field Order & Technician Assignment',
        note: 'Select the active field work order requiring supervisor override and specify the technician.',
        fields: [
          { name: 'field_order_id', required: true, label: 'Field Work Order Target' },
          { name: 'technician_id', required: true, label: 'Declining / Overridden Technician' },
          { name: 'replacement_technician_id', label: 'Replacement Field Technician' },
          { name: 'decline_date', label: 'Override Effective Timestamp' }
        ]
      },
      {
        tab: 'justification',
        title: 'Override Reason & Supervisor Authorization',
        note: 'Record supervisor operational justification and reassignment instructions.',
        fields: [
          { name: 'reason', required: true, label: 'Override Reason Code' },
          { name: 'supervisor_approved', label: 'Supervisor Override Approved' },
          { name: 'notes', required: true, label: 'Supervisor Justification / Reassignment Directives', type: 'text' },
          { name: 'evidence_attachment_id', label: 'Supporting Exception Photo / Document' }
        ]
      }
    ]
  },

  'M02-form-reschedule': {
    kind: 'model_form',
    model: 'fix.field.order',
    title: 'Emergency Reschedule Request',
    back: 'M02-record',
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
        note: 'Select the customer service order for emergency reschedule and appointment reallocation.',
        fields: [
          { name: 'order_id', required: true, label: 'Service Order Target' },
          { name: 'zone_id', required: true, label: 'Dispatch Territory Zone' },
          { name: 'technician_id', label: 'Reassigned Field Technician' },
          { name: 'priority', label: 'Escalated SLA Priority' }
        ]
      },
      {
        tab: 'windows',
        title: 'Emergency Reschedule Appointment Windows',
        note: 'Specify the rescheduled customer arrival window and adjusted SLA deadline.',
        fields: [
          { name: 'scheduled_start', required: true, label: 'New Scheduled Start Window' },
          { name: 'scheduled_end', label: 'New Scheduled End Window' },
          { name: 'sla_deadline', label: 'Adjusted SLA Resolution Deadline' }
        ]
      },
      {
        tab: 'reason',
        title: 'Emergency Justification & Customer Agreement',
        note: 'Document customer agreement, weather conditions, vehicle breakdown, or force majeure.',
        fields: [
          { name: 'decline_reason', label: 'Incident Trigger / Reschedule Cause' },
          { name: 'decline_notes', label: 'Customer Confirmation & Delay Justification', type: 'text' },
          { name: 'notes', label: 'Safety, Route & Access Instructions', type: 'text' },
          { name: 'signed_job_sheet_attachment_id', label: 'Reschedule Confirmation Attachment' }
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
    tabs: [
      { id: 'source', label: '1. Exception Source', bn: '১. ব্যতিক্রম উৎস', icon: '⚠️', badge: '4' },
      { id: 'resolution', label: '2. Coded Reason & Evidence', bn: '২. কারণ ও প্রমাণক', icon: '📎', badge: '5' }
    ],
    sections: [
      {
        tab: 'source',
        title: 'Exception Source & Technician',
        fields: [
          { name: 'field_order_id', required: true, label: 'Field Order' },
          { name: 'technician_id', required: true, label: 'Technician' },
          { name: 'replacement_technician_id', label: 'Replacement Technician' },
          { name: 'decline_date', required: true, label: 'Exception Date' }
        ]
      },
      {
        tab: 'resolution',
        title: 'Coded Reason, Supervisor Review & Evidence',
        note: 'Every decline/exception carries a coded reason so the Field Exception Summary report can group them.',
        fields: [
          { name: 'decline_reason', label: 'Reason Code (from the field order)' },
          { name: 'reason', label: 'Reason (free text)' },
          { name: 'supervisor_approved', label: 'Supervisor Reviewed' },
          { name: 'notes', label: 'Notes', type: 'text' },
          { name: 'evidence_attachment_id', label: 'Exception Photo / Evidence Attachment' }
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
      { id: 'plan', label: '1. Route Header', bn: '১. রুট তথ্য', icon: '🗺️', badge: '3' },
      { id: 'metrics', label: '2. Optimisation Metrics', bn: '২. অপ্টিমাইজেশন ফলাফল', icon: '📊', badge: '4' }
    ],
    sections: [
      {
        tab: 'plan',
        title: 'Route Schedule & Technician',
        fields: [
          { name: 'name', required: true, label: 'Route Reference' },
          { name: 'technician_id', required: true, label: 'Technician' },
          { name: 'date', required: true, label: 'Route Date' }
        ]
      },
      {
        tab: 'metrics',
        title: 'Measured Route Optimisation Outcome',
        note: 'Build the plan from the Route Optimisation screen (action_optimize_route), then start and complete it here.',
        fields: [
          { name: 'order_count', label: 'Stops' },
          { name: 'total_distance_km', label: 'Total Distance (km)' },
          { name: 'total_duration_hours', label: 'Total Duration (h)' },
          { name: 'improvement_pct', label: 'Optimisation Gain %' }
        ]
      }
    ]
  },

  /* ===== triage coverage screens ===== */
  'M02-technician-location': { kind: 'model_list', model: 'fix.technician.location',
    cols: ['name', 'company_id', 'operating_unit_id', 'name_bn', 'technician_id', 'latitude', 'longitude', 'is_mock_location', 'gnss_hdop'] },

  'M02-form-technician-location': {
    kind: 'model_form',
    model: 'fix.technician.location',
    title: "Technician Location",
    back: 'M02-technician-location',
    tabs: [
      { id: 'ping', label: '1. GPS Coordinates', bn: '১. জিপিএস স্থানাঙ্ক', icon: '📡', badge: '7' },
      { id: 'telemetry', label: '2. Anti-Spoof & Device Health', bn: '২. অ্যান্টি-স্পুফ ও টেলিমেট্রি', icon: '🛡️', badge: '4' }
    ],
    sections: [
      { tab: 'ping', title: "Technician GPS Ping Identity", note: "Every field here is the model's real field; the workflow rules live on the model and are not bypassed by this form.",
        fields: [
          { name: 'name', required: true, label: "Ping Reference" },
          { name: 'name_bn', label: "Ping Reference (Bengali)" },
          { name: 'company_id', required: true, label: "Company" },
          { name: 'operating_unit_id', required: true, label: "Operating Unit" },
          { name: 'technician_id', required: true, label: "Technician" },
          { name: 'latitude', required: true, label: "Latitude" },
          { name: 'longitude', required: true, label: "Longitude" }
        ] },
      { tab: 'telemetry', title: "GNSS Anti-Spoofing & Mobile Telemetry (FLAW-02.2)",
        fields: [
          { name: 'is_mock_location', label: "Mock Location Flagged" },
          { name: 'gnss_hdop', label: "GNSS HDOP Precision" },
          { name: 'speed_kmh', label: "Speed (km/h)" },
          { name: 'battery_level', label: "Device Battery (%)" }
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
export const FORM_CHIPS = {
  'M02:Field Work Order': 'M02-form-wo',
  'M02:Field Exception Report': 'M02-form-exception',
  'M02:Crew Assignment': 'M02-form-wo',
  'M02:Route Plan': 'M02-form-route',
  'M02:Field Work Order (work order)': 'M02-form-workorder',
  'M02:Zone Geofence': 'M02-form-zone',
  'M02:__by_model__': {
    'fix.geofence': 'M02-form-zone',
    'fix.technician.location': 'M02-form-technician-location',
    'fix.field.order': 'M02-form-wo',
    'fix.field.decline.log': 'M02-form-exception',
    'fix.field.route': 'M02-form-route',
    'fix.work.order': 'M02-form-workorder'
  },
  'M02:__by_screen__': {
    'M02-wo': 'M02-form-workorder',
    'M02-zones': 'M02-form-zone',
    'M02-record': 'M02-form-wo',
    'M02-exceptions': 'M02-form-exception',
    'M02-routes': 'M02-form-route'
  }
};

export const FORM_MODELS = {
  'M02:Field Work Order': 'fix.field.order',
  'M02:Field Exception Report': 'fix.field.decline.log',
  'M02:Crew Assignment': 'fix.field.order',
  'M02:Route Plan': 'fix.field.route'
};

/* The module's "+ New" surface: opens the canonical Dynamics 365 Create Field Work Order form */
export const CREATE = {
  M02: { screen: 'M02-form-wo', model: 'fix.field.order', label: 'Field Work Order' }
};
