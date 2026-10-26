/** @odoo-module **/
/* A02 · Service Operations — M03 Service Logistics (Pick & Drop).
 * This fragment REPLACES the base-file M03 block, which described a
 * walk-in branch-repair module — wrong content entirely (registry drift
 * measured 2026-10-26: zero id overlap with the canonical registry M03).
 * The structure below is the CANONICAL registry M03: 5 groups, 16 screens,
 * 6 KPIs, 6 reports, freg 93 functions in 12 subs.
 *
 * Backend: controllers/a02/m03.py (SURFACES, kpis, 6 REPORTS) over the
 * cd_consignment core — the verified custody chain, POD with OTP, the
 * service-order bridge — plus the M50 COD settlement reads. */

export const MODULE = {
  area: 'A02', code: 'M03', en: 'Service Logistics (Pick & Drop)', title: 'M03 · Service Logistics (Pick & Drop)',
  bn: 'সার্ভিস লজিস্টিকস (পিক অ্যান্ড ড্রপ)', icon: '📦',
  desc: 'Multi-leg consignments, unbroken chain of custody, POD with OTP, rider app, courier partners, COD.',
  kpis: [
    { l: 'In Transit', m: 'in_transit' },
    { l: 'On-Time Delivery', m: 'on_time_delivery' },
    { l: 'Custody Exceptions', m: 'custody_exceptions' },
    { l: 'COD Today', m: 'cod_today' },
    { l: 'Avg Round Trip', m: 'avg_round_trip' },
    { l: 'Rider Shifts Open', m: 'rider_shifts_open' }
  ],
  groups: [
    { en: 'Consignments', screens: [
      { id: 'M03-cons', en: 'Consignments', bn: 'কনসাইনমেন্ট', t: 'g' },
      { id: 'M03-record', en: 'Consignment Record', bn: 'কনসাইনমেন্ট নথি', t: 'f' },
      { id: 'M03-journeys', en: 'Multi-Leg Journeys', bn: 'মাল্টি-লেগ জার্নি', t: 'g' },
      { id: 'M03-manifest', en: 'Item Manifests', bn: 'আইটেম ম্যানিফেস্ট', t: 'g' }
    ]},
    { en: 'Custody & POD', screens: [
      { id: 'M03-custody', en: 'Chain-of-Custody Ledger', bn: 'কাস্টডি চেইন লেজার', t: 'g' },
      { id: 'M03-pod', en: 'Proof of Delivery (OTP)', bn: 'ডেলিভারি প্রমাণ (ওটিপি)', t: 'g' },
      { id: 'M03-seals', en: 'Sealing & Tamper Log', bn: 'সিলিং ও ট্যাম্পার লগ', t: 'g' }
    ]},
    { en: 'Riders & Fleet', screens: [
      { id: 'M03-riders', en: 'Rider Assignment', bn: 'রাইডার নিয়োগ', t: 'g' },
      { id: 'M03-routes', en: 'Route Manifests', bn: 'রুট ম্যানিফেস্ট', t: 'g' },
      { id: 'M03-app', en: 'Rider App (P09) Preview', bn: 'রাইডার অ্যাপ (P09) প্রিভিউ', t: 'd' }
    ]},
    { en: 'Courier Partners', screens: [
      { id: 'M03-couriers', en: 'Courier Partners', bn: 'কুরিয়ার পার্টনার', t: 'g' },
      { id: 'M03-bookings', en: 'Courier Bookings', bn: 'কুরিয়ার বুকিং', t: 'g' },
      { id: 'M03-recon', en: 'Courier Reconciliation', bn: 'কুরিয়ার রিকনসিলিয়েশন', t: 'c' }
    ]},
    { en: 'Exceptions & Billing', screens: [
      { id: 'M03-exc', en: 'Loss / Damage Claims', bn: 'ক্ষতি ও হারানোর দাবি', t: 'g' },
      { id: 'M03-charges', en: 'Distance & Zone Charging', bn: 'দূরত্ব ও জোন চার্জ', t: 'g' },
      { id: 'M03-cod', en: 'COD Reconciliation', bn: 'ক্যাশ অন ডেলিভারি রিকনসিলিয়েশন', t: 'c' }
    ]}
  ],
  reports: ['Consignment Cycle Time', 'Custody Exception Register', 'Courier Performance (Pathao/RedX/Steadfast)', 'COD Settlement Report', 'Reverse Logistics Volume', 'Damage & Insurance Claims'],
  forms: ['Consignment (5 types)', 'Rider Shift Open / Close', 'Courier Booking', 'Damage Claim'],
  cross: ['M01 pick&drop orders', 'M04 counter handover', 'M46 fleet & drivers', 'M50 COD settlement', 'M17 custody chain'],
  freg: {
    src: 93,
    sub: [
      ['1', 'Consignment Creation & Manifest', 10],
      ['2', 'Multi-Leg Journey Planning', 8],
      ['3', 'Chain-of-Custody Scanning', 9],
      ['4', 'POD with OTP Verification', 7],
      ['5', 'Sealing & Tamper Evidence', 6],
      ['6', 'Rider Assignment & Shifts', 9],
      ['7', 'Route Manifest & Load Planning', 8],
      ['8', 'Rider App Offline Sync (P09)', 8],
      ['9', 'Courier Partner Integration', 10],
      ['10', 'COD Collection & Handover', 7],
      ['11', 'Loss / Damage Claims', 6],
      ['12', 'Distance & Zone Charging', 5]
    ]
  }
};

/* In-workspace data screens over the whitelisted consignment models. */
export const SCREENS = {
  'M03-cons': { kind: 'model_list', model: 'fix.consignment', create: false,
    cols: ['name', 'consignment_type', 'state', 'scheduled_date', 'origin_branch_id', 'dest_branch_id', 'rider_id', 'chain_broken'],
    stateField: 'state' },
  'M03-record': { kind: 'model_list', model: 'fix.consignment', create: false,
    cols: ['name', 'consignment_type', 'state', 'service_order_id', 'custody_summary', 'chain_broken',
      'pod_verified_at', 'pod_verified_by', 'create_date'],
    stateField: 'state' },
  'M03-journeys': { kind: 'model_list', model: 'fix.custody.scan', create: false,
    cols: ['consignment_id', 'step', 'scanned_at', 'scanned_by', 'location_branch_id', 'device_serial', 'exception_reason'] },
  'M03-manifest': { kind: 'table_report', module: 'M03', report: 'cycle_time', period: false },
  'M03-custody': { kind: 'model_list', model: 'fix.custody.scan', create: false,
    cols: ['consignment_id', 'step', 'scanned_at', 'exception_reason', 'device_serial'],
    domain: [['exception_reason', '!=', false]] },
  'M03-pod': { kind: 'model_list', model: 'fix.consignment', create: false,
    cols: ['name', 'state', 'service_order_id', 'rider_id', 'pod_verified_at', 'pod_verified_by', 'custody_summary'],
    domain: [['state', 'in', ['confirmed', 'in_transit', 'delivered']]],
    stateField: 'state',
    actions: [
      { m: 'action_generate_otp', l: 'Generate POD OTP' },
      { m: 'action_start_transit', l: 'Start Transit' },
      { m: 'action_verify_pod', l: 'Verify POD (OTP)', ask: 'Customer OTP' }
    ] },
  'M03-seals': { kind: 'table_report', module: 'M03', report: 'custody_exceptions', period: false },
  'M03-riders': { kind: 'model_list', model: 'fix.consignment', create: false,
    cols: ['name', 'rider_id', 'consignment_type', 'state', 'scheduled_date', 'origin_branch_id', 'dest_branch_id'],
    domain: [['rider_id', '!=', false]] },
  'M03-routes': { kind: 'table_report', module: 'M03', report: 'reverse_volume', period: false },
  'M03-app': { kind: 'table_report', module: 'M03', report: 'cycle_time', period: false },
  'M03-couriers': { kind: 'table_report', module: 'M03', report: 'courier_performance', period: false },
  'M03-bookings': { kind: 'table_report', module: 'M03', report: 'courier_performance', period: false },
  'M03-recon': { kind: 'table_report', module: 'M03', report: 'courier_performance', period: false },
  'M03-exc': { kind: 'model_list', model: 'fix.consignment', create: false,
    cols: ['name', 'consignment_type', 'state', 'chain_broken', 'custody_summary', 'rider_id'],
    domain: [['chain_broken', '=', true], ['state', '=', 'lost']] },
  'M03-charges': { kind: 'table_report', module: 'M03', report: 'courier_performance', period: false },
  'M03-cod': { kind: 'table_report', module: 'M03', report: 'cod_settlement', period: false }
};

/* built-in report chips -> the screen that shows that report */
export const REPORT_ROUTES = {
  "M03:Consignment Cycle Time": "M03-cons",
  "M03:Custody Exception Register": "M03-seals",
  "M03:Courier Performance (Pathao/RedX/Steadfast)": "M03-couriers",
  "M03:COD Settlement Report": "M03-cod",
  "M03:Reverse Logistics Volume": "M03-routes",
  "M03:Damage & Insurance Claims": "M03-exc"
};

/* data-entry form chips: consignments are created from the M01 service
 * order (bridge action); rider shifts and courier bookings arrive with
 * their engines and keep the honest toast. */
export const FORM_MODELS = {};

/* the module's "+ New" surface: no generic create — legs start from the
 * service-order hand-over. */
export const CREATE = {};
