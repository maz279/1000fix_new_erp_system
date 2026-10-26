/** @odoo-module **/
/* A02 · Service Operations — M02 Field Service & Dispatch.
 * Backend: controllers/a02/m02.py (SURFACES, kpis, REPORTS, /p03/field/*)
 * + /p03/dispatch/map_data (the live SVG map) + the whitelisted field models.
 * Every screen renders INSIDE the shell from live data: the dispatch board
 * with the explainable suggestion engine, scoped field-order lists with the
 * full AS-06 field lifecycle on the buttons, model lists for work orders,
 * declines, geofences and telemetry, and the optimizer-backed route list. */

export const MODULE = {
  area: 'A02', code: 'M02', en: 'Field Service & Dispatch', title: 'M02 · Field Service & Dispatch',
  bn: 'ফিল্ড সার্ভিস ও ডিসপ্যাচ', icon: '🚐',
  desc: 'AI dispatch board, route optimisation, technician app (24h offline), GPS tracking, field evidence & payments.',
  kpis: [
    { l: 'Jobs / Tech / Day', m: 'jobs_tech_day' },
    { l: 'Auto-Assignment', m: 'auto_assignment' },
    { l: 'On-Time Arrival', m: 'on_time_arrival' },
    { l: 'Travel Time Share', m: 'travel_share' },
    { l: 'Unassigned > 15m', m: 'unassigned_15m' },
    { l: 'Offline Sync Health', m: 'offline_sync_health' }
  ],
  groups: [
    { en: 'Dispatch Console', screens: [
      { id: 'M02-dispatch', en: 'Dispatch Board (Live AI)', bn: 'লাইভ এআই ডিসপ্যাচ বোর্ড', t: 'd' },
      { id: 'M02-map', en: 'Live Technician GPS Map', bn: 'লাইভ টেকনিশিয়ান ম্যাপ', t: 'd' },
      { id: 'M02-unassigned', en: 'Unassigned Jobs Queue', bn: 'অনির্ধারিত কাজের সারি', t: 'g' },
      { id: 'M02-sla-risk', en: 'SLA Risk & Escalation Board', bn: 'এসএলএ ঝুঁকি বোর্ড', t: 'g' }
    ]},
    { en: 'Work Orders', screens: [
      { id: 'M02-wo', en: 'Field Work Orders', bn: 'ফিল্ড ওয়ার্ক অর্ডার', t: 'g' },
      { id: 'M02-record', en: 'Work Order Record View', bn: 'ওয়ার্ক অর্ডার নথি', t: 'f' },
      { id: 'M02-exceptions', en: 'Field Job Exceptions', bn: 'ফিল্ড ব্যতিক্রম', t: 'g' },
      { id: 'M02-crews', en: 'Multi-Tech Crews', bn: 'ক্রু নিয়োগ', t: 'g' }
    ]},
    { en: 'Routing & Territories', screens: [
      { id: 'M02-zones', en: 'Territory Zones & Geofences', bn: 'জোন ও জিওফেন্স', t: 'g' },
      { id: 'M02-routes', en: 'Route Optimization Engine', bn: 'রুট অপ্টিমাইজেশন', t: 'c' },
      { id: 'M02-territory', en: 'Territory Workload Balance', bn: 'টেরিটরি ব্যালেন্স', t: 'r' }
    ]}
  ],
  reports: ['Technician Utilization & Travel Time', 'First-Time Fix Rate by Skill', 'Geofence Breach & Delay Log', 'Field Payment Reconciliation'],
  forms: ['Create Field Work Order', 'Technician Dispatch Override', 'Emergency Reschedule Request'],
  cross: ['M01 Service Orders', 'M15 Truck-Stock Inventory', 'M21 Skill Matrix', 'M20 Mobile Invoicing'],
  freg: {
    src: 112,
    sub: [
      ['1', 'Automated Dispatch & Optimization', 12],
      ['2', 'Real-time GPS Tracking & ETA', 8],
      ['3', 'Mobile Work Order Execution', 10],
      ['4', 'Field Parts Consumption & Truck Stock', 9],
      ['5', 'Customer Signoff & Digital Evidence', 8],
      ['6', 'Field Payment & bKash / Cash Collection', 7]
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
  'M02-wo': { kind: 'model_list', model: 'fix.work.order', create: false,
    cols: ['name', 'order_id', 'technician_id', 'sequence', 'state', 'start_time', 'end_time', 'duration_hours'],
    stateField: 'state' },
  'M02-record': { kind: 'model_list', model: 'fix.field.order', create: false,
    cols: ['name', 'order_id', 'technician_id', 'zone_id', 'scheduled_start', 'state',
      'dispatched_at', 'arrived_at', 'actual_travel_minutes', 'on_time_arrival', 'completed_at'],
    stateField: 'state' },
  'M02-exceptions': { kind: 'model_list', model: 'fix.field.decline.log', create: false,
    cols: ['name', 'field_order_id', 'technician_id', 'reason', 'decline_date', 'notes'] },
  'M02-crews': { kind: 'fs_crews' },
  'M02-zones': { kind: 'model_list', model: 'fix.geofence', create: false,
    cols: ['name', 'zone_id', 'geofence_type', 'active'] },
  'M02-routes': { kind: 'model_list', model: 'fix.field.route',
    cols: ['name', 'technician_id', 'date', 'order_count', 'total_distance_km', 'total_duration_hours', 'improvement_pct', 'route_state'],
    stateField: 'route_state' },
  'M02-territory': { kind: 'table_report', module: 'M02', report: 'zone_workload', period: false }
};

/* built-in report chips -> the screen that shows that report */
export const REPORT_ROUTES = {
  "M02:Technician Utilization & Travel Time": "M02-territory",
  "M02:First-Time Fix Rate by Skill": "M02-wo",
  "M02:Geofence Breach & Delay Log": "M02-exceptions",
  "M02:Field Payment Reconciliation": "M02-record"
};

/* data-entry form chips: field work orders are created from the M01 service
 * order (bridge action) — the honest path until a bespoke in-shell intake
 * form lands with the mobile phase. */
export const FORM_MODELS = {};

/* the module's "+ New" surface: no generic create — dispatch flows start
 * from the service order hand-over or the dispatch board. */
export const CREATE = {};
