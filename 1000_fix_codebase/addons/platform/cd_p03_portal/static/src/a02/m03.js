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
    { en: 'Record Coverage', screens: [
      { id: 'M03-damage-claim', en: "Damage Claim", bn: "ক্ষতিপূরণ দাবি", t: 'g' }
    ]},
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
  reports: ['Consignment Cycle Time', 'Custody Exception Register', 'Courier Performance (Pathao/RedX/Steadfast)', 'COD Settlement Report', 'Reverse Logistics Volume', 'Damage & Insurance Claims', 'Damage & Claims'],
  forms: ['Consignment (5 types)', 'Rider Shift Open / Close', 'Courier Booking', 'Damage Claim'],
  cross: ['M01 pick&drop orders', 'M04 counter handover', 'M46 fleet & drivers', 'M50 COD settlement', 'M17 custody chain'],
  freg: {
    src: 93,
    sub: [
      ['1', 'Consignment Creation & Manifest', 10, { model: 'fix.consignment', cols: ['name', 'consignment_type', 'state', 'scheduled_date', 'origin_branch_id'], screens: ['M03-cons', 'M03-manifest'] }],
      ['2', 'Multi-Leg Journey Planning', 8, { model: 'fix.custody.scan', cols: ['consignment_id', 'step', 'location_branch_id', 'scanned_at'], screens: ['M03-journeys'] }],
      ['3', 'Chain-of-Custody Scanning', 9, { model: 'fix.custody.scan', cols: ['consignment_id', 'step', 'scanned_at', 'scanned_by', 'exception_reason'], screens: ['M03-custody', 'M03-record'] }],
      ['4', 'POD with OTP Verification', 7, { model: 'fix.consignment', cols: ['name', 'recipient_name', 'pod_verified_at', 'pod_verified_by', 'state'], screens: ['M03-pod'], domain: [['state', '=', 'delivered']] }],
      ['5', 'Sealing & Tamper Evidence', 6, { model: 'fix.consignment', cols: ['name', 'outbound_seal_number', 'inbound_seal_number', 'seal_status', 'weight_variance_g'], screens: ['M03-seals'] }],
      ['6', 'Rider Assignment & Shifts', 9, { model: 'fix.consignment', cols: ['name', 'rider_id', 'scheduled_date', 'consignment_type', 'state'], screens: ['M03-riders'], domain: [['rider_id', '!=', false]] }],
      ['7', 'Route Manifest & Load Planning', 8, { model: 'fix.consignment', cols: ['name', 'rider_id', 'vehicle_registration', 'chargeable_weight_kg', 'scheduled_date'], screens: ['M03-routes'], domain: [['state', 'in', ['confirmed', 'in_transit']]] }],
      ['8', 'Rider App Offline Sync (P09)', 8, { model: 'fix.custody.scan', cols: ['consignment_id', 'step', 'scanned_by', 'scanned_at', 'device_serial'], screens: ['M03-app'] }],
      ['9', 'Courier Partner Integration', 10, { model: 'fix.courier.booking', cols: ['name', 'partner_id', 'awb_no', 'booked_on', 'state'], screens: ['M03-bookings', 'M03-couriers', 'M03-recon'] }],
      ['10', 'COD Collection & Handover', 7, { model: 'fix.cod.settlement', cols: ['name', 'rider_id', 'expected_amount', 'remitted_amount', 'state'], screens: ['M03-cod'] }],
      ['11', 'Loss / Damage Claims', 6, { model: 'fix.damage.claim', cols: ['name', 'consignment_id', 'damage_kind', 'claimed_amount', 'state'], screens: ['M03-damage-claim', 'M03-exc'] }],
      ['12', 'Distance & Zone Charging', 5, { model: 'fix.consignment', cols: ['name', 'chargeable_weight_kg', 'base_freight_bdt', 'volumetric_surcharge_bdt', 'insurance_fee_bdt'], screens: ['M03-charges'] }]
    ]
  }
};

/* In-workspace data screens over the whitelisted consignment models. */
export const SCREENS = {
  'M03-form-courier': {
    kind: 'model_form',
    model: 'fix.courier.partner',
    title: 'Courier Partner',
    back: 'M03-couriers',
    tabs: [
      { id: 'profile', label: '1. Partner Identity', bn: '১. কুরিয়ার পরিচিতি', icon: '🏢', badge: '5' },
      { id: 'commercial', label: '2. Tariff & Billing', bn: '২. ভাড়া ও বিলিং', icon: '💵', badge: '4' }
    ],
    sections: [
      { tab: 'profile', title: 'Partner Profile & Service Coverage', note: 'A third-party courier account: coverage, rate basis and COD settlement cycle.',
        fields: [
          { name: 'name', required: true, label: 'Partner Name' },
          { name: 'code', required: true, label: 'Code' },
          { name: 'service_area', label: 'Service Area' },
          { name: 'api_ref', label: 'API Credential Reference' },
          { name: 'active', label: 'Active' }
        ] },
      { tab: 'commercial', title: 'Tariff Matrix & COD Settlement Cycle',
        fields: [
          { name: 'base_rate', label: 'Base Rate (BDT)' },
          { name: 'per_kg_rate', label: 'Per-kg Rate (BDT)' },
          { name: 'cod_supported', label: 'COD Supported' },
          { name: 'cod_cycle_days', label: 'COD Cycle (days)' }
        ] }
    ]
  },

  'M03-form-booking': {
    kind: 'model_form',
    model: 'fix.courier.booking',
    title: 'Courier Booking',
    back: 'M03-bookings',
    status: { field: 'state', labels: { booked: 'Booked', picked_up: 'Picked Up',
      delivered: 'Delivered', returned: 'Returned', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'booking', label: '1. Booking & Consignment', bn: '১. বুকিং ও চালান', icon: '📦', badge: '5' },
      { id: 'freight', label: '2. Freight & Volumetric', bn: '২. ভাড়া ও ওজন', icon: '⚖️', badge: '6' }
    ],
    sections: [
      { tab: 'booking', title: 'Courier Booking & AWB Tracking', note: 'A third-party courier booking for one consignment: the AWB number, weight, and status.',
        fields: [
          { name: 'partner_id', required: true, label: 'Courier' },
          { name: 'consignment_id', label: 'Consignment' },
          { name: 'awb_no', label: 'AWB / Tracking No' },
          { name: 'booked_on', required: true, label: 'Booked On' },
          { name: 'state', required: true, label: 'State' }
        ] },
      { tab: 'freight', title: 'Weight & Volumetric Pricing (FLAW-03.2)',
        fields: [
          { name: 'weight_kg', label: 'Actual Weight (kg)' },
          { name: 'length_cm', label: 'Length (cm)' },
          { name: 'width_cm', label: 'Width (cm)' },
          { name: 'height_cm', label: 'Height (cm)' },
          { name: 'charged_amount', label: 'Charged Amount (BDT)' },
          { name: 'cod_amount', label: 'COD Amount (BDT)' }
        ] }
    ]
  },

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
  'M03-couriers': { kind: 'model_list', model: 'fix.courier.partner', cols: ['name', 'code', 'service_area', 'base_rate', 'cod_supported', 'cod_cycle_days', 'active'] },
  'M03-bookings': { kind: 'model_list', model: 'fix.courier.booking', stateField: 'state', cols: ['name', 'partner_id', 'consignment_id', 'awb_no', 'booked_on', 'weight_kg', 'charged_amount', 'state'], actions: [{ m: 'action_deliver', l: 'Mark Delivered' }] },
  'M03-recon': { kind: 'table_report', module: 'M03', report: 'courier_performance', title: 'Courier Performance & COD', period: false },
  'M03-exc': { kind: 'model_list', model: 'fix.consignment', create: false,
    cols: ['name', 'consignment_type', 'state', 'chain_broken', 'custody_summary', 'rider_id'],
    domain: [['chain_broken', '=', true], ['state', '=', 'lost']] },
  'M03-charges': { kind: 'table_report', module: 'M03', report: 'courier_performance', title: 'Courier Charges', period: false },
  'M03-cod': { kind: 'table_report', module: 'M03', report: 'cod_settlement', period: false },

  /* computed pack that had no screen (closure 2026-10-28) */
  'M03-rpt-damage': { kind: 'table_report', module: 'M03', report: 'damage_claims', title: "Damage & Claims", period: false },

  /* ===== service data-entry forms (registry names) ===== */
  'M03-form-consignment': {
    kind: 'model_form',
    model: 'fix.consignment',
    title: "Consignment (5 types)",
    back: 'M03-consignments',
    status: { field: 'state', labels: { draft: "Draft", assigned: "Assigned", in_transit: "In Transit", delivered: "Delivered", cancelled: "Cancelled" } },
    tabs: [
      { id: 'journey', label: '1. Journey & Legs', bn: '১. রুট ও স্থানান্তর', icon: '🚚', badge: '8' },
      { id: 'custody', label: '2. Tamper Evident Seals', bn: '২. সিল ও নিরাপত্তা', icon: '🔒', badge: '8' },
      { id: 'volumetric', label: '3. Chargeable Weight', bn: '৩. ওজন ও বিলিং', icon: '⚖️', badge: '8' },
      { id: 'pod', label: '4. OTP Proof of Delivery', bn: '৪. ওটিপি প্রমাণক', icon: '📱', badge: '6' }
    ],
    sections: [
      { tab: 'journey', title: "Multi-Leg Consignment Route & Rider Assignment", note: "A pick-and-drop job: origin and destination branch, rider, service order, and custody chain.",
        fields: [
          { name: 'name', label: "Consignment Reference", readonly: true },
          { name: 'consignment_type', required: true, label: "Consignment Type" },
          { name: 'scheduled_date', required: true, label: "Scheduled Date" },
          { name: 'origin_branch_id', label: "Origin Branch" },
          { name: 'dest_branch_id', label: "Destination Branch" },
          { name: 'rider_id', label: "Assigned Rider" },
          { name: 'service_order_id', label: "Service Order Reference" },
          { name: 'state', required: true, label: "Consignment Status" }
        ] },
      { tab: 'custody', title: "Tamper-Evident Security Seals & Scale Verification (FLAW-03.3)",
        note: "Seal numbers and intake scale weights are verified at hub transfers with a strict 20g threshold.",
        fields: [
          { name: 'security_bag_barcode', label: "Tamper-Evident Bag Barcode" },
          { name: 'outbound_seal_number', label: "Outbound Security Seal No" },
          { name: 'inbound_seal_number', label: "Inbound Received Seal No" },
          { name: 'seal_status', label: "Seal Integrity Verdict" },
          { name: 'dispatch_weight_g', label: "Dispatch Scale Weight (g)" },
          { name: 'receive_weight_g', label: "Intake Scale Weight (g)" },
          { name: 'weight_variance_g', label: "Weight Variance (g)", readonly: true },
          { name: 'chain_broken', label: "Custody Chain Broken Alert" }
        ] },
      { tab: 'volumetric', title: "IATA Volumetric Weight & Freight Rating (FLAW-03.2)",
        fields: [
          { name: 'actual_weight_kg', label: "Actual Scale Weight (kg)" },
          { name: 'length_cm', label: "Length (cm)" },
          { name: 'width_cm', label: "Width (cm)" },
          { name: 'height_cm', label: "Height (cm)" },
          { name: 'volumetric_divisor', label: "Volumetric Divisor" },
          { name: 'chargeable_weight_kg', label: "Chargeable Weight (kg)", readonly: true },
          { name: 'base_freight_bdt', label: "Base Freight (BDT)" },
          { name: 'insurance_fee_bdt', label: "Transit Insurance (BDT)" }
        ] },
      { tab: 'pod', title: "Proof of Delivery (POD) & OTP Handover",
        fields: [
          { name: 'pod_otp_code', label: "POD Customer OTP Code" },
          { name: 'pod_verified_at', label: "POD OTP Verified At", readonly: true },
          { name: 'pod_verified_by', label: "Verified Recipient Name" },
          { name: 'cod_amount_collected', label: "COD Cash Collected (BDT)" },
          { name: 'cod_settlement_ref', label: "COD Settlement Ref (M50)" },
          { name: 'pod_signature_attachment_id', label: "Signed POD Sheet / Photo Proof" }
        ] }
    ]
  },
  'M03-form-rider-shift': {
    kind: 'model_form',
    model: 'fix.custody.scan',
    title: "Rider Shift Open/Close",
    back: 'M03-custody',
    tabs: [
      { id: 'scan', label: '1. Custody Hop', bn: '১. স্ক্যান তথ্য', icon: '📡', badge: '6' },
      { id: 'device', label: '2. Device & Serial', bn: '২. ডিভাইস ও অবস্থা', icon: '📱', badge: '3' }
    ],
    sections: [
      { tab: 'scan', title: "Custody Scan & Location Verification", note: "A custody scan: each hop of the chain is a scanned step with who scanned it and where.",
        fields: [
          { name: 'consignment_id', required: true, label: "Consignment" },
          { name: 'step', required: true, label: "Custody Step" },
          { name: 'scanned_at', required: true, label: "Scanned At" },
          { name: 'location_branch_id', label: "At Branch" },
          { name: 'scanned_by', label: "Scanned By User" },
          { name: 'exception_reason', label: "Custody Exception Note" }
        ] },
      { tab: 'device', title: "Device & Seal Verification",
        fields: [
          { name: 'device_serial', label: "Scanned Device Serial / IMEI" },
          { name: 'seal_number_scanned', label: "Scanned Security Seal" },
          { name: 'weight_at_scan_g', label: "Scale Weight at Scan (g)" }
        ] }
    ]
  },

  /* ===== triage coverage screens ===== */
  'M03-damage-claim': { kind: 'model_list', model: 'fix.damage.claim', stateField: 'state',
    cols: ['name', 'state', 'company_id', 'operating_unit_id', 'consignment_id', 'claimed_on', 'claimant', 'claimed_amount_bdt', 'dofa_tier'] },

  'M03-form-damage-claim': {
    kind: 'model_form',
    model: 'fix.damage.claim',
    title: "Damage Claim",
    back: 'M03-damage-claim',
    status: { field: 'state' },
    tabs: [
      { id: 'claim', label: '1. Incident Claim', bn: '১. দাবির বিবরণ', icon: '⚠️', badge: '6' },
      { id: 'dofa', label: '2. DOFA & Financial Sign-Off', bn: '২. অনুমোদন ও আর্থিক সিদ্ধান্ত', icon: '✍️', badge: '5' }
    ],
    sections: [
      { tab: 'claim', title: "Transit Damage / Loss Incident Claim", note: "Opened from the module's own record set. Every field here is the model's real field.",
        fields: [
          { name: 'name', required: true, label: "Claim Reference", readonly: true },
          { name: 'state', required: true, label: "Claim Status" },
          { name: 'consignment_id', required: true, label: "Consignment" },
          { name: 'claimed_on', required: true, label: "Incident / Claim Date" },
          { name: 'claimant', required: true, label: "Claimant / Consignee" },
          { name: 'description', label: "Damage Incident Details", type: "text" }
        ] },
      { tab: 'dofa', title: "DOFA Tier & Settlement Approval",
        fields: [
          { name: 'claimed_amount_bdt', label: "Claimed Amount (BDT)" },
          { name: 'approved_amount_bdt', label: "Approved Settlement (BDT)" },
          { name: 'dofa_tier', label: "Required DOFA Approval Tier", readonly: true },
          { name: 'approved_by_id', label: "Authorizing Manager / Director", readonly: true },
          { name: 'incident_photo_attachment_id', label: "Damage Photo / Police GD Proof" }
        ] }
    ]
  },

};

/* built-in report chips -> the screen that shows that report */
export const REPORT_ROUTES = {
  'M03:Damage & Claims': 'M03-rpt-damage',
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


export const FORM_CHIPS = {
  'M03:Courier Booking': 'M03-form-booking',
  'M03:Damage Claim': 'M03-form-damage-claim',
  'M03:Consignment (5 types)': 'M03-form-consignment',
  'M03:Rider Shift Open/Close': 'M03-form-rider-shift',
  'M03:__by_model__': {
    'fix.courier.partner': 'M03-form-courier',
    'fix.courier.booking': 'M03-form-booking',
    'fix.damage.claim': 'M03-form-damage-claim',
    'fix.consignment': 'M03-form-consignment',
    'fix.custody.scan': 'M03-form-rider-shift',
  },
  'M03:__by_screen__': {
    'M03-couriers': 'M03-form-courier',
    'M03-bookings': 'M03-form-booking',
    'M03-damage-claim': 'M03-form-damage-claim',
    'M03-consignments': 'M03-form-consignment',
    'M03-custody': 'M03-form-rider-shift',
  }
};
