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
    { l: 'Rider Shifts Open', m: 'rider_shifts_open', src: false }
  ],
  groups: [
    { en: 'Record Coverage', screens: [
      { id: 'M03-damage-claim', en: "Damage Claim", bn: "ক্ষতিপূরণ দাবি", t: 'g' }
    ]},
    { en: 'Consignments', screens: [
      { id: 'M03-cons', en: 'Consignments', bn: 'কনসাইনমেন্ট', t: 'g' },
      { id: 'M03-record', en: 'Consignment Record', bn: 'কনসাইনমেন্ট নথি', t: 'g' },
      { id: 'M03-journeys', en: 'Multi-Leg Journeys', bn: 'মাল্টি-লেগ জার্নি', t: 'g' },
      { id: 'M03-manifest', en: 'Item Manifests', bn: 'আইটেম ম্যানিফেস্ট', t: 'r' }
    ]},
    { en: 'Custody & POD', screens: [
      { id: 'M03-custody', en: 'Chain-of-Custody Ledger', bn: 'কাস্টডি চেইন লেজার', t: 'g' },
      { id: 'M03-pod', en: 'Proof of Delivery (OTP)', bn: 'ডেলিভারি প্রমাণ (ওটিপি)', t: 'g' },
      { id: 'M03-seals', en: 'Sealing & Tamper Log', bn: 'সিলিং ও ট্যাম্পার লগ', t: 'r' }
    ]},
    { en: 'Riders & Fleet', screens: [
      { id: 'M03-riders', en: 'Rider Assignment', bn: 'রাইডার নিয়োগ', t: 'g' },
      { id: 'M03-rider-certs', en: 'Restricted-Item Certifications', bn: 'বিপজ্জনক পণ্য বহনের সনদ', t: 'g' },
      { id: 'M03-routes', en: 'Route Manifests', bn: 'রুট ম্যানিফেস্ট', t: 'r' },
      { id: 'M03-app', en: 'Rider App (P09) Preview', bn: 'রাইডার অ্যাপ (P09) প্রিভিউ', t: 'r' }
    ]},
    { en: 'Courier Partners', screens: [
      { id: 'M03-couriers', en: 'Courier Partners', bn: 'কুরিয়ার পার্টনার', t: 'g' },
      { id: 'M03-bookings', en: 'Courier Bookings', bn: 'কুরিয়ার বুকিং', t: 'g' },
      { id: 'M03-recon', en: 'Courier Reconciliation', bn: 'কুরিয়ার রিকনসিলিয়েশন', t: 'r' }
    ]},
    { en: 'Exceptions & Billing', screens: [
      { id: 'M03-exc', en: 'Loss / Damage Claims', bn: 'ক্ষতি ও হারানোর দাবি', t: 'g' },
      { id: 'M03-charges', en: 'Distance & Zone Charging', bn: 'দূরত্ব ও জোন চার্জ', t: 'r' },
      { id: 'M03-cod', en: 'COD Reconciliation', bn: 'ক্যাশ অন ডেলিভারি রিকনসিলিয়েশন', t: 'r' }
    ]}
  ],
  reports: ['Consignment Cycle Time', 'Custody Exception Register', 'Courier Performance (Pathao/RedX/Steadfast)', 'COD Settlement Report', 'Reverse Logistics Volume', 'Damage & Insurance Claims'],
  /* the custody-scan view is evidence, not data entry (it was offered as
   * 'Rider Shift Open / Close' over append-only custody scans).
   * M03 capture audit 2026-11-12: each sub-module page now captures what
   * its function records. The steps that are workflow transitions (seal,
   * hub intake) pick a consignment and run the guarded server method;
   * nothing writes a scan or a seal verdict directly. */
  forms: ['Consignment', 'Next Journey Leg', 'Courier Booking', 'Damage Claim', 'Courier Partner',
    'Seal for Dispatch', 'Hub Intake Scan', 'Proof of Delivery Record', 'Rider & Vehicle Assignment',
    'Rider COD Settlement', 'Courier POD Record', 'Rider Certification'],
  cross: ['M01 pick&drop orders', 'M04 counter handover', 'M46 fleet & drivers', 'M50 COD settlement', 'M17 custody chain'],
  freg: {
    src: 93,
    sub: [
      /* 1 FR-LOG-001: a consignment is created from any source - the M01
       * hand-over makes pickup / delivery legs, and a branch transfer or a
       * return to vendor is raised here. The page had no button at all. */
      ['1', 'Consignment Creation & Manifest', 10, { model: 'fix.consignment', cols: ['name', 'consignment_type', 'state', 'scheduled_date', 'origin_branch_id'], screens: ['M03-cons', 'M03-manifest'], reports: ['Consignment Cycle Time', 'Reverse Logistics Volume'], forms: ['Consignment'] }],
      /* 2 FR-LOG-002: a journey is the chain of legs (consignments) of one
       * service order; planning it is raising the next leg. It listed the
       * custody scans, which are sub-module 3's records.
       * M03 capture audit 2026-11-18: the page offered the same blank
       * consignment as page 1, and the hand-over it relies on raised a second
       * pickup for a collection order whose device had already arrived. The
       * page now plans the next leg of an order's journey (the server picks
       * pickup or the delivery back); a leg with no order (branch transfer,
       * return to vendor) is still a new consignment. */
      ['2', 'Multi-Leg Journey Planning', 8, { model: 'fix.consignment', cols: ['name', 'service_order_id', 'consignment_type', 'origin_branch_id', 'dest_branch_id', 'scheduled_date', 'state'], screens: ['M03-journeys', 'M03-cons'], reports: ['Consignment Cycle Time'], forms: ['Next Journey Leg', 'Consignment'], create: 'M03-form-next-leg' }],
      /* 3 FR-LOG-006: the hub's custody scan is the intake (seal + weight),
       * which stamps the hub scan itself; the rider's scans come from the
       * transitions and the rider app. A typed scan could "explain" a
       * skipped step, so scans are never entered directly. */
      ['3', 'Chain-of-Custody Scanning', 9, { model: 'fix.custody.scan', cols: ['consignment_id', 'step', 'scanned_at', 'scanned_by', 'exception_reason'], screens: ['M03-custody', 'M03-record'], reports: ['Custody Exception Register'], forms: ['Hub Intake Scan'], create: 'M03-form-hub-intake' }],
      /* 4 FR-LOG-008: recipient identity and the signed waybill; the code
       * itself is checked by Verify POD (OTP) on Proof of Delivery. */
      ['4', 'POD with OTP Verification', 7, { model: 'fix.consignment', cols: ['name', 'recipient_name', 'pod_verified_at', 'pod_verified_by', 'state'], screens: ['M03-pod'], reports: ['Consignment Cycle Time'], forms: ['Proof of Delivery Record'], create: 'M03-form-pod', domain: [['state', '=', 'delivered']] }],
      /* 5 FR-LOG-004: packaging, bag, seal and dispatch weight, fixed once
       * the leg leaves dispatch; the inbound side is the hub intake. */
      ['5', 'Sealing & Tamper Evidence', 6, { model: 'fix.consignment', cols: ['name', 'outbound_seal_number', 'inbound_seal_number', 'seal_status', 'weight_variance_g'], screens: ['M03-seals'], reports: ['Custody Exception Register'], forms: ['Seal for Dispatch', 'Hub Intake Scan'], create: 'M03-form-seal' }],
      /* 6/7 FR-LOG-013/014/029: the rider, vehicle and run date of a leg.
       * No rider-shift or route-manifest record exists yet (the manifest is
       * the rider's legs of the day, computed). */
      ['6', 'Rider Assignment & Shifts', 9, { model: 'fix.consignment', cols: ['name', 'rider_id', 'scheduled_date', 'consignment_type', 'state'], screens: ['M03-riders', 'M03-rider-certs'], reports: [], forms: ['Rider & Vehicle Assignment', 'Rider Certification'], create: 'M03-form-rider', domain: [['rider_id', '!=', false]] }],
      ['7', 'Route Manifest & Load Planning', 8, { model: 'fix.consignment', cols: ['name', 'rider_id', 'vehicle_registration', 'chargeable_weight_kg', 'scheduled_date'], screens: ['M03-routes'], reports: [], forms: ['Rider & Vehicle Assignment'], create: 'M03-form-rider', domain: [['state', 'in', ['confirmed', 'in_transit']]] }],
      /* 8: written by the rider app (P09) on sync - nothing to type here */
      ['8', 'Rider App Offline Sync (P09)', 8, { model: 'fix.custody.scan', cols: ['consignment_id', 'step', 'scanned_by', 'scanned_at', 'device_serial'], screens: ['M03-app'], reports: [], forms: [], create: false }],
      ['9', 'Courier Partner Integration', 10, { model: 'fix.courier.booking', cols: ['name', 'partner_id', 'awb_no', 'booked_on', 'state'], screens: ['M03-bookings', 'M03-couriers', 'M03-recon'], reports: ['Courier Performance (Pathao/RedX/Steadfast)'], forms: ['Courier Booking', 'Courier POD Record', 'Courier Partner'] }],
      /* 10 FR-LOG-030: the rider's cash hand-over is the M50 settlement
       * (Finance prepares and settles it; the orders load from delivered COD) */
      ['10', 'COD Collection & Handover', 7, { model: 'fix.cod.settlement', cols: ['name', 'rider_id', 'expected_amount', 'remitted_amount', 'state'], screens: ['M03-cod'], reports: ['COD Settlement Report'], forms: ['Rider COD Settlement'] }],
      ['11', 'Loss / Damage Claims', 6, { model: 'fix.damage.claim', cols: ['name', 'consignment_id', 'damage_kind', 'claimed_amount', 'state'], screens: ['M03-damage-claim', 'M03-exc'], reports: ['Damage & Insurance Claims'], forms: ['Damage Claim'] }],
      /* 12 FR-LOG-022: freight is computed from the courier's tariff (base
       * + per-kg) and the declared value; the tariff is what is captured. */
      ['12', 'Distance & Zone Charging', 5, { model: 'fix.consignment', cols: ['name', 'chargeable_weight_kg', 'base_freight_bdt', 'volumetric_surcharge_bdt', 'insurance_fee_bdt'], screens: ['M03-charges', 'M03-couriers'], reports: [], forms: ['Courier Partner'], create: 'M03-form-courier' }]
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
      { id: 'profile', label: '1. Partner Identity', bn: '১. কুরিয়ার পরিচিতি', icon: '🏢', badge: '9' },
      { id: 'commercial', label: '2. Tariff & Billing', bn: '২. ভাড়া ও বিলিং', icon: '💵', badge: '6' }
    ],
    sections: [
      { tab: 'profile', title: 'Partner Profile & Service Coverage', note: 'A third-party courier account: coverage, contractual delivery SLA and the account manager. Courier Performance measures on-time against this SLA.',
        fields: [
          { name: 'name', required: true, label: 'Partner Name' },
          { name: 'code', required: true, label: 'Code' },
          { name: 'service_area', label: 'Service Area' },
          /* BRU-LOG-10: restricted items only with a valid certification */
          { name: 'restricted_item_certified', label: 'Certified for Restricted Items' },
          { name: 'restricted_cert_valid_until', label: 'Restricted Certification Valid Until' },
          { name: 'sla_delivery_hours', label: 'Contractual Delivery SLA (hours)' },
          { name: 'contact_phone', label: 'Account Manager Phone' },
          { name: 'api_ref', label: 'API Credential Reference (vault://)' },
          { name: 'active', label: 'Active' }
        ] },
      { tab: 'commercial', title: 'Tariff Matrix & COD Settlement Cycle',
        note: 'A leg carried by this courier is priced base + per-kg on its chargeable weight (the greater of actual and volumetric weight).',
        fields: [
          { name: 'base_rate', label: 'Base Rate (BDT)' },
          { name: 'per_kg_rate', label: 'Per-kg Rate (BDT)' },
          { name: 'volumetric_divisor', label: 'Volumetric Divisor (cm³/kg)' },
          { name: 'insurance_max_bdt', label: 'Max Insured Liability (BDT)' },
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
      { id: 'booking', label: '1. Booking & Consignment', bn: '১. বুকিং ও চালান', icon: '📦', badge: '10' },
      { id: 'freight', label: '2. Freight & Volumetric', bn: '২. ভাড়া ও ওজন', icon: '⚖️', badge: '6' }
    ],
    sections: [
      { tab: 'booking', title: 'Courier Booking & AWB Tracking', note: 'A third-party courier booking for one consignment: the AWB number, the recipient, weight and status. The courier’s signed POD is recorded with Record Courier POD; only then can the booking be marked delivered.',
        fields: [
          { name: 'partner_id', required: true, label: 'Courier' },
          { name: 'consignment_id', label: 'Consignment' },
          { name: 'awb_no', label: 'AWB / Tracking No' },
          { name: 'booked_on', required: true, label: 'Booked On' },
          { name: 'recipient_name', label: 'Recipient Name' },
          { name: 'recipient_phone', label: 'Recipient Phone' },
          { name: 'state', label: 'State', readonly: true },
          { name: 'delivered_on', label: 'Delivered On', readonly: true },
          { name: 'pod_attachment_id', label: 'Courier POD Scan', readonly: true },
          { name: 'pod_recorded_by_id', label: 'POD Recorded By', readonly: true }
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

  /* A02 audit M03-11: the lifecycle runs from these buttons; the status
   * field is read-only on the form. The server checks the role, the state,
   * the custody chain and the POD for every one of them.
   * M03 capture audit: "+ New" raises a consignment (a branch transfer, a
   * return to vendor, or a leg the M01 hand-over did not make). */
  'M03-cons': { kind: 'model_list', model: 'fix.consignment',
    cols: ['name', 'consignment_type', 'state', 'scheduled_date', 'origin_branch_id', 'dest_branch_id', 'rider_id', 'chain_broken', 'seal_status'],
    stateField: 'state',
    actions: [
      { m: 'action_confirm', l: 'Confirm for Dispatch' },
      { m: 'action_start_transit', l: 'Start Transit' },
      /* A02 audit M03-P2: one value per press; the intake completes once the
       * seal (if one was fitted) and the weight (if one was dispatched) are in */
      { m: 'action_verify_hub_intake', l: 'Hub Intake: Inbound Seal', ask: 'Inbound seal number', kwarg: 'inbound_seal' },
      { m: 'action_record_receive_weight', l: 'Hub Intake: Receive Weight', ask: 'Receive scale weight in grams', kwarg: 'receive_weight_g' },
      { m: 'action_confirm_receipt', l: 'Confirm Receipt at Hub' },
      { m: 'action_out_for_delivery', l: 'Out for Delivery' },
      { m: 'action_return', l: 'Return to Origin', ask: 'Reason for the return', kwarg: 'reason' },
      { m: 'action_report_lost', l: 'Report Lost', ask: 'What happened', kwarg: 'reason' },
      { m: 'action_release_hold', l: 'Release Exception Hold', ask: 'Reason for releasing the hold', kwarg: 'reason' },
      /* BRU-LOG-03: a second person vouches for a high-value dispatch */
      { m: 'action_countersign_dispatch', l: 'Countersign High-Value Dispatch' }
    ] },
  'M03-record': { kind: 'model_list', model: 'fix.consignment', create: false,
    cols: ['name', 'consignment_type', 'state', 'service_order_id', 'custody_summary', 'chain_broken',
      'chain_problem', 'pod_verified_at', 'pod_verified_by', 'delivered_at', 'create_date'],
    stateField: 'state' },
  /* M03 capture audit 2026-11-18: "Multi-Leg Journeys" listed custody
   * scans (sub-module 3's records, already on Chain-of-Custody). A journey
   * is the legs of one service order: pickup, transfers, the delivery back. */
  'M03-journeys': { kind: 'model_list', model: 'fix.consignment', create: false,
    cols: ['service_order_id', 'name', 'consignment_type', 'origin_branch_id', 'dest_branch_id', 'scheduled_date', 'rider_id', 'state', 'custody_summary'],
    domain: [['service_order_id', '!=', false]],
    stateField: 'state',
    empty: 'No service order has a logistics leg yet. Plan the next leg of a journey from Multi-Leg Journey Planning, or with Hand to Logistics on the service order.' },
  'M03-manifest': { kind: 'table_report', module: 'M03', report: 'manifest_register', title: 'Item Manifests', period: false },
  'M03-custody': { kind: 'model_list', model: 'fix.custody.scan', create: false,
    cols: ['consignment_id', 'step', 'scanned_at', 'exception_reason', 'device_serial'],
    domain: [['exception_reason', '!=', false]],
    empty: 'No custody exception recorded. A scan that finds a problem (seal broken, wrong device, missing item) is listed here with its note.' },
  'M03-pod': { kind: 'model_list', model: 'fix.consignment', create: false,
    cols: ['name', 'state', 'service_order_id', 'rider_id', 'pod_otp_channel', 'pod_verified_at', 'pod_verified_by', 'custody_summary'],
    domain: [['state', 'in', ['confirmed', 'in_transit', 'delivered']]],
    stateField: 'state',
    actions: [
      { m: 'action_start_transit', l: 'Start Transit' },
      { m: 'action_out_for_delivery', l: 'Out for Delivery' },
      { m: 'action_generate_otp', l: 'Send POD Code to Recipient' },
      { m: 'action_verify_pod', l: 'Verify POD (OTP)', ask: 'Code the recipient received by SMS' }
    ] },
  'M03-seals': { kind: 'table_report', module: 'M03', report: 'custody_exceptions', period: false },
  'M03-riders': { kind: 'model_list', model: 'fix.consignment', create: false,
    cols: ['name', 'rider_id', 'consignment_type', 'state', 'scheduled_date', 'origin_branch_id', 'dest_branch_id'],
    domain: [['rider_id', '!=', false]] },
  /* the rider's legs per day ARE the route manifest; this screen showed the
   * reverse-logistics volume report (M03 capture audit 2026-11-12) */
  'M03-routes': { kind: 'table_report', module: 'M03', report: 'route_manifest', title: 'Route Manifests', period: false },
  'M03-app': { kind: 'table_report', module: 'M03', report: 'rider_day', title: 'Rider App (P09) Preview', period: false },
  'M03-couriers': { kind: 'model_list', model: 'fix.courier.partner', cols: ['name', 'code', 'service_area', 'base_rate', 'cod_supported', 'cod_cycle_days', 'active'] },
  'M03-bookings': { kind: 'model_list', model: 'fix.courier.booking', stateField: 'state', cols: ['name', 'partner_id', 'consignment_id', 'awb_no', 'booked_on', 'weight_kg', 'charged_amount', 'cod_amount', 'pod_attachment_id', 'state'], actions: [
      { m: 'action_pick_up', l: 'Handed to Courier' },
      { m: 'action_deliver', l: 'Mark Delivered (needs POD)' }
    ] },
  'M03-recon': { kind: 'table_report', module: 'M03', report: 'courier_performance', title: 'Courier Performance & COD', period: false },
  'M03-exc': { kind: 'model_list', model: 'fix.consignment', create: false,
    cols: ['name', 'consignment_type', 'state', 'chain_broken', 'chain_problem', 'seal_status', 'hold_reason', 'custody_summary', 'rider_id'],
    domain: ['|', '|', ['chain_broken', '=', true], ['state', '=', 'lost'], ['state', '=', 'held']],
    stateField: 'state',
    actions: [
      { m: 'action_release_hold', l: 'Release Exception Hold', ask: 'Reason for releasing the hold', kwarg: 'reason' },
      { m: 'action_return', l: 'Return to Origin', ask: 'Reason for the return', kwarg: 'reason' },
      { m: 'action_report_lost', l: 'Report Lost', ask: 'What happened', kwarg: 'reason' }
    ] },
  'M03-charges': { kind: 'table_report', module: 'M03', report: 'zone_charges', title: 'Distance & Zone Charging', period: false },
  'M03-cod': { kind: 'table_report', module: 'M03', report: 'cod_settlement', period: false },

  /* computed pack that had no screen (closure 2026-10-28) */
  'M03-rpt-damage': { kind: 'table_report', module: 'M03', report: 'damage_claims', title: "Damage & Insurance Claims", period: false },
  /* M03 sweep audit 2026-11-06 (D17): the registry report tiles now open
   * their own computed reports instead of the nearest grid. */
  'M03-rpt-cycletime': { kind: 'table_report', module: 'M03', report: 'cycle_time', title: 'Consignment Cycle Time', period: false },
  'M03-rpt-custody': { kind: 'table_report', module: 'M03', report: 'custody_exceptions', title: 'Custody Exception Register', period: false },
  'M03-rpt-courier': { kind: 'table_report', module: 'M03', report: 'courier_performance', title: 'Courier Performance', period: false },
  'M03-rpt-reverse': { kind: 'table_report', module: 'M03', report: 'reverse_volume', title: 'Reverse Logistics Volume', period: false },

  /* ===== service data-entry forms (registry names) ===== */
  'M03-form-consignment': {
    kind: 'model_form',
    model: 'fix.consignment',
    title: "Consignment",
    back: 'M03-cons',
    status: { field: 'state', labels: { draft: "Draft", confirmed: "Confirmed", in_transit: "In Transit", held: "Exception Hold", delivered: "Delivered", returned: "Returned", lost: "Lost" } },
    tabs: [
      { id: 'journey', label: '1. Journey & Legs', bn: '১. রুট ও স্থানান্তর', icon: '🚚', badge: '14' },
      { id: 'custody', label: '2. Tamper Evident Seals', bn: '২. সিল ও নিরাপত্তা', icon: '🔒', badge: '16' },
      { id: 'volumetric', label: '3. Chargeable Weight', bn: '৩. ওজন ও বিলিং', icon: '⚖️', badge: '16' },
      { id: 'pod', label: '4. OTP Proof of Delivery', bn: '৪. ওটিপি প্রমাণক', icon: '📱', badge: '8' }
    ],
    sections: [
      { tab: 'journey', title: "Multi-Leg Consignment Route & Rider Assignment", note: "One leg of a journey: a pickup or delivery for a service order, a branch transfer, or a return to vendor (name the purchase order: its vendor receives the delivery code). Legs made by the M01 hand-over arrive here filled in. The operating unit defaults to yours; the type is fixed once the leg is confirmed.",
        fields: [
          { name: 'name', label: "Consignment Reference", readonly: true },
          { name: 'consignment_type', required: true, label: "Consignment Type" },
          { name: 'scheduled_date', required: true, label: "Scheduled Date" },
          { name: 'operating_unit_id', required: true, label: "Operating Unit" },
          { name: 'origin_branch_id', label: "Origin Branch" },
          { name: 'dest_branch_id', label: "Destination Branch" },
          { name: 'service_order_id', label: "Service Order Reference" },
          { name: 'purchase_order_id', label: "Purchase Order (return to vendor)" },
          { name: 'rider_id', label: "Assigned Rider" },
          { name: 'courier_partner_id', label: "3PL Courier Partner" },
          { name: 'vehicle_registration', label: "Vehicle / Bike Reg No." },
          /* BRU-LOG-05: carried only by a certified rider or courier */
          { name: 'restricted_item', label: "Carries a Restricted Item" },
          { name: 'restricted_item_class', label: "Restricted Class" },
          { name: 'state', label: "Consignment Status", readonly: true }
        ] },
      { tab: 'custody', title: "Tamper-Evident Security Seals & Scale Verification (FLAW-03.3)",
        note: "Seal numbers and intake scale weights are verified at hub transfers with a strict 20g threshold.",
        fields: [
          { name: 'packaging_type', label: "Protective Packaging" },
          { name: 'security_bag_barcode', label: "Tamper-Evident Bag Barcode" },
          { name: 'outbound_seal_number', label: "Outbound Security Seal No" },
          { name: 'inbound_seal_number', label: "Inbound Received Seal No (hub intake)", readonly: true },
          { name: 'seal_status', label: "Seal Integrity Verdict", readonly: true },
          { name: 'dispatch_weight_g', label: "Dispatch Scale Weight (g)" },
          { name: 'receive_weight_g', label: "Intake Scale Weight (g) (hub intake)", readonly: true },
          { name: 'weight_variance_g', label: "Weight Variance (g)", readonly: true },
          { name: 'shockwatch_triggered', label: "ShockWatch / Tilt Indicator Tripped" },
          { name: 'chain_broken', label: "Custody Chain Broken Alert", readonly: true },
          { name: 'chain_problem', label: "Chain Problem", readonly: true },
          { name: 'hold_reason', label: "Exception Hold Reason", readonly: true },
          /* M03 audit 2026-11-13: the release and the return/loss reason are
           * evidence the model stamps; no screen showed them */
          { name: 'hold_released_by_id', label: "Hold Released By", readonly: true },
          { name: 'hold_released_at', label: "Hold Released At", readonly: true },
          { name: 'hold_release_reason', label: "Hold Release Reason", readonly: true },
          { name: 'rto_flag', label: "Returned to Origin", readonly: true },
          { name: 'exception_note', label: "Return / Loss Reason", readonly: true }
        ] },
      { tab: 'volumetric', title: "IATA Volumetric Weight & Freight Rating (FLAW-03.2)",
        fields: [
          { name: 'actual_weight_kg', label: "Actual Scale Weight (kg)" },
          { name: 'length_cm', label: "Length (cm)" },
          { name: 'width_cm', label: "Width (cm)" },
          { name: 'height_cm', label: "Height (cm)" },
          { name: 'volumetric_divisor', label: "Volumetric Divisor" },
          /* BRU-LOG-12: recorded before collection; drives the insurance fee */
          { name: 'declared_value_bdt', label: "Declared Value (BDT)" },
          /* BRU-LOG-03: above the threshold, insured and countersigned */
          { name: 'insurance_flag', label: "Transit Insurance Taken" },
          { name: 'high_value', label: "High Value (dual signature)", readonly: true },
          { name: 'dispatch_countersigned_by_id', label: "Countersigned By", readonly: true },
          { name: 'dispatch_countersigned_at', label: "Countersigned At", readonly: true },
          { name: 'dispatch_countersigned_value', label: "Value Countersigned (BDT)", readonly: true },
          { name: 'volumetric_weight_kg', label: "Volumetric Weight (kg)", readonly: true },
          { name: 'chargeable_weight_kg', label: "Chargeable Weight (kg)", readonly: true },
          { name: 'base_freight_bdt', label: "Base Freight (BDT)", readonly: true },
          { name: 'volumetric_surcharge_bdt', label: "Volumetric Surcharge (BDT)", readonly: true },
          { name: 'insurance_fee_bdt', label: "Transit Insurance (BDT)", readonly: true }
        ] },
      { tab: 'pod', title: "Proof of Delivery (POD) & OTP Handover",
        fields: [
          { name: 'pod_otp_channel', label: "POD Code Sent To", readonly: true },
          { name: 'pod_otp_issued_at', label: "POD Code Issued At", readonly: true },
          { name: 'pod_verified_at', label: "POD Verified At", readonly: true },
          { name: 'pod_verified_by', label: "POD Verified By", readonly: true },
          { name: 'delivered_at', label: "Delivered At", readonly: true },
          { name: 'recipient_name', label: "Recipient Name" },
          { name: 'recipient_nid_last4', label: "Recipient NID / Phone Last 4" },
          { name: 'waybill_attachment_id', label: "Signed Waybill / Manifest" }
        ] }
    ]
  },

  /* ===== M03 capture audit 2026-11-12: a capture per sub-module =====
   * Each picks the consignment it acts on (the M01 hold pattern). The
   * dispatch evidence below is locked by the model once the leg leaves
   * dispatch, so only draft and confirmed legs are offered. */
  /* M03 capture audit 2026-11-18: sub-module 2's capture. The order's
   * next leg is decided by the server (action_create_consignment ->
   * _fix_next_leg_type): a collection / mail-in order gets its pickup, then
   * the delivery back once it is ready; a second live leg is refused. */
  'M03-form-next-leg': {
    kind: 'model_form',
    model: 'fix.service.order',
    title: 'Next Journey Leg',
    newLabel: 'Plan the Next Leg of a Journey',
    back: 'M03-journeys',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the service order whose device moves next',
      note: 'Open collection and mail-in orders, and any order ready to go back to its customer.',
      search: 'Search order / customer',
      choose: 'Plan this journey',
      cols: ['name', 'customer_id', 'service_type', 'branch_id', 'consignment_count', 'state'],
      domain: [['state', 'in', ['intake', 'diagnostic', 'estimate_pending', 'estimate_sent', 'awaiting_approval',
        'approved', 'in_repair', 'qc_pending', 'qc_failed', 'ready']],
        '|', ['service_type', 'in', ['collection', 'mail_in']], ['state', '=', 'ready']],
      empty: 'No open collection or mail-in order, and no order ready to go back. A leg with no service order (branch transfer, return to vendor) is a new Consignment.'
    },
    saveAction: {
      method: 'action_create_consignment', label: 'Raise the Next Leg',
      done: 'Next leg raised: it is a draft consignment on Consignments, ready to seal and assign',
      kwargs: {}
    },
    sections: [
      { title: 'Step 2 of 2: check the order, then raise its next leg (FR-LOG-002)',
        note: 'A collection or mail-in order gets a pickup (customer to branch); once that pickup is delivered, the next leg is the delivery back, raised when the order is ready. Any other order gets a delivery leg. A second live leg of the same kind is refused.',
        fields: [
          { name: 'name', label: 'Order Reference', readonly: true },
          { name: 'customer_id', label: 'Customer', readonly: true },
          { name: 'device_id', label: 'Device', readonly: true },
          { name: 'service_type', label: 'Intake Channel', readonly: true },
          { name: 'branch_id', label: 'Service Center / Branch', readonly: true },
          { name: 'consignment_count', label: 'Legs So Far', readonly: true },
          { name: 'state', label: 'Current State', readonly: true }
        ] }
    ]
  },

  'M03-form-seal': {
    kind: 'model_form',
    model: 'fix.consignment',
    title: 'Seal for Dispatch',
    newLabel: 'Seal a Consignment for Dispatch',
    back: 'M03-cons',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the consignment to seal',
      note: 'Draft and confirmed consignments. Once a leg is in transit its packaging, bag, seal and dispatch weight are evidence and cannot change.',
      search: 'Search consignment',
      choose: 'Seal this consignment',
      cols: ['name', 'consignment_type', 'origin_branch_id', 'dest_branch_id', 'scheduled_date', 'state'],
      domain: [['state', 'in', ['draft', 'confirmed']]],
      empty: 'No draft or confirmed consignment is waiting for dispatch. Raise one with + New Consignment first.'
    },
    sections: [
      { title: 'Step 2 of 2: Packaging, Seal & Dispatch Weight (FR-LOG-004)',
        note: 'The receiving hub checks the seal number and the weight blind (±20 g); a mismatch puts the leg on exception hold. Confirm for Dispatch on Consignments when the leg is sealed.',
        fields: [
          { name: 'name', label: 'Consignment', readonly: true },
          { name: 'consignment_type', label: 'Type', readonly: true },
          { name: 'state', label: 'Status', readonly: true },
          { name: 'packaging_type', label: 'Protective Packaging' },
          { name: 'security_bag_barcode', label: 'Tamper-Evident Bag Barcode' },
          { name: 'outbound_seal_number', required: true, label: 'Outbound Security Seal No' },
          { name: 'dispatch_weight_g', label: 'Dispatch Scale Weight (g)' },
          { name: 'declared_value_bdt', label: 'Declared Value (BDT)' },
          { name: 'insurance_flag', label: 'Transit Insurance Taken' },
          { name: 'restricted_item', label: 'Carries a Restricted Item' },
          { name: 'restricted_item_class', label: 'Restricted Class' }
        ] }
    ]
  },

  /* The hub's custody scan. action_verify_hub_intake records the seal and
   * the weight it is given, holds the leg on a mismatch, and stamps the hub
   * scan once every check the leg needs is in. The outbound seal and the
   * dispatch weight are NOT shown: the hub reads its own. */
  'M03-form-hub-intake': {
    kind: 'model_form',
    model: 'fix.consignment',
    title: 'Hub Intake Scan',
    newLabel: 'Record a Hub Intake Scan',
    back: 'M03-cons',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the consignment arriving at the hub',
      note: 'Consignments in transit.',
      search: 'Search consignment',
      choose: 'Receive this consignment',
      cols: ['name', 'consignment_type', 'origin_branch_id', 'dest_branch_id', 'rider_id', 'state'],
      domain: [['state', '=', 'in_transit']],
      empty: 'No consignment is in transit.'
    },
    saveAction: {
      method: 'action_verify_hub_intake', label: 'Record Hub Intake',
      done: 'Hub intake recorded: the seal and weight match, the hub scan is stamped',
      kwargs: { inbound_seal: 'inbound_seal_number', receive_weight_g: 'receive_weight_g' }
    },
    sections: [
      { title: 'Step 2 of 2: Inbound Seal & Receive Weight (FR-LOG-006 / 010)',
        note: 'Needs the Logistics Hub Operator role. Read the seal on the bag and weigh it; a recorded seal or weight is evidence and is not replaced. A leg that ends here is then closed with Confirm Receipt at Hub.',
        fields: [
          { name: 'name', label: 'Consignment', readonly: true },
          { name: 'consignment_type', label: 'Type', readonly: true },
          { name: 'dest_branch_id', label: 'Destination Branch', readonly: true },
          { name: 'rider_id', label: 'Rider', readonly: true },
          /* readonly for the generic write (recorded by the intake only); an
           * INPUT here because saveAction carries it to the intake */
          { name: 'inbound_seal_number', label: 'Inbound Seal No (as read)', readonly: true },
          { name: 'receive_weight_g', label: 'Receive Scale Weight (g)', readonly: true },
          { name: 'seal_status', label: 'Seal Verdict', readonly: true },
          { name: 'hold_reason', label: 'Exception Hold Reason', readonly: true }
        ] }
    ]
  },

  'M03-form-pod': {
    kind: 'model_form',
    model: 'fix.consignment',
    title: 'Proof of Delivery Record',
    newLabel: 'Record Recipient & Signed Waybill',
    back: 'M03-pod',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the consignment being handed over',
      note: 'Customer deliveries and returns to vendor in transit.',
      search: 'Search consignment',
      choose: 'Record this hand-over',
      cols: ['name', 'consignment_type', 'service_order_id', 'rider_id', 'pod_otp_channel', 'state'],
      domain: [['state', '=', 'in_transit'], ['consignment_type', 'in', ['delivery', 'return_to_vendor']]],
      empty: 'No delivery or return to vendor is in transit.'
    },
    sections: [
      { title: 'Step 2 of 2: Recipient Identity & Signed Waybill (FR-LOG-008)',
        note: 'Who received it and the signed waybill. The delivery itself closes with Verify POD (OTP) on Proof of Delivery: the code the recipient received by SMS (Send POD Code issues it).',
        fields: [
          { name: 'name', label: 'Consignment', readonly: true },
          { name: 'service_order_id', label: 'Service Order', readonly: true },
          { name: 'pod_otp_channel', label: 'POD Code Sent To', readonly: true },
          { name: 'recipient_name', required: true, label: 'Recipient Name' },
          { name: 'recipient_nid_last4', label: 'Recipient NID / Phone Last 4' },
          { name: 'waybill_attachment_id', label: 'Signed Waybill / Photo' }
        ] }
    ]
  },

  'M03-form-rider': {
    kind: 'model_form',
    model: 'fix.consignment',
    title: 'Rider & Vehicle Assignment',
    newLabel: 'Assign Rider & Vehicle',
    back: 'M03-riders',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the consignment to assign',
      note: 'Draft and confirmed consignments not yet on the road. The rider of a leg in transit holds its custody and closes its POD.',
      search: 'Search consignment',
      choose: 'Assign this consignment',
      cols: ['name', 'consignment_type', 'origin_branch_id', 'dest_branch_id', 'rider_id', 'scheduled_date', 'state'],
      domain: [['state', 'in', ['draft', 'confirmed']]],
      empty: 'No draft or confirmed consignment is waiting for a rider.'
    },
    sections: [
      { title: 'Step 2 of 2: Rider, Vehicle & Run Date (FR-LOG-013 / 014)',
        note: 'An internal rider, or a third-party courier (book it on Courier Bookings). The rider’s legs of the day are the route manifest.',
        fields: [
          { name: 'name', label: 'Consignment', readonly: true },
          { name: 'consignment_type', label: 'Type', readonly: true },
          { name: 'chargeable_weight_kg', label: 'Chargeable Weight (kg)', readonly: true },
          { name: 'rider_id', label: 'Rider' },
          { name: 'courier_partner_id', label: '3PL Courier Partner' },
          { name: 'vehicle_registration', label: 'Vehicle / Bike Reg No.' },
          { name: 'scheduled_date', required: true, label: 'Run Date' }
        ] }
    ]
  },
  /* M03 audit 2026-11-13: a courier booking closes only on a recorded POD,
   * and the POD could not be recorded anywhere (guarded field, method not
   * served) - no courier booking could ever be marked delivered. */
  'M03-form-courier-pod': {
    kind: 'model_form',
    model: 'fix.courier.booking',
    title: 'Courier POD Record',
    newLabel: 'Record Courier POD',
    back: 'M03-bookings',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the courier booking',
      note: 'Bookings the courier has not closed yet (booked or picked up).',
      search: 'Search booking / AWB',
      choose: 'Record its POD',
      cols: ['name', 'partner_id', 'awb_no', 'consignment_id', 'booked_on', 'state'],
      domain: [['state', 'in', ['booked', 'picked_up']]],
      empty: 'No open courier booking.'
    },
    saveAction: {
      method: 'action_record_pod', label: 'Record POD',
      done: 'Courier POD recorded: the booking can now be marked delivered',
      kwargs: { attachment_id: 'pod_attachment_id' }
    },
    sections: [
      { title: 'Step 2 of 2: The Courier’s Signed Waybill / POD Scan (FR-LOG-018)',
        note: 'Needs the Logistics Hub Operator role. Upload the scan the courier returned (PDF or photo, up to 10 MB); then press Mark Delivered on Courier Bookings.',
        fields: [
          { name: 'name', label: 'Booking', readonly: true },
          { name: 'partner_id', label: 'Courier', readonly: true },
          { name: 'awb_no', label: 'AWB / Tracking No', readonly: true },
          { name: 'consignment_id', label: 'Consignment', readonly: true },
          /* readonly for the generic write (guarded); an INPUT here because
           * saveAction carries it to action_record_pod */
          { name: 'pod_attachment_id', required: true, label: 'Signed POD Scan', readonly: true }
        ] }
    ]
  },

  /* BRU-LOG-05: who may carry which restricted class, and until when. A
   * rider without a valid row cannot be assigned a restricted consignment. */
  'M03-rider-certs': { kind: 'model_list', model: 'fix.rider.certification',
    cols: ['employee_id', 'item_class', 'certificate_ref', 'issued_on', 'valid_until', 'active'],
    empty: 'No rider is certified for restricted items yet. A consignment carrying a battery, refrigerant or other hazardous item can only go with a certified rider or a certified courier.' },
  'M03-form-rider-cert': {
    kind: 'model_form',
    model: 'fix.rider.certification',
    title: 'Rider Certification',
    back: 'M03-rider-certs',
    tabs: [
      { id: 'cert', label: '1. Certification', bn: '১. সনদ', icon: '🪪', badge: '6' }
    ],
    sections: [
      { tab: 'cert', title: 'Restricted-Item Certification (BRU-LOG-05)',
        note: 'Recorded by a logistics manager from the certificate the rider holds. It covers its class from the issue date to the valid-until date; after that the rider cannot take that class.',
        fields: [
          { name: 'employee_id', required: true, label: 'Rider' },
          { name: 'item_class', required: true, label: 'Restricted Class' },
          { name: 'certificate_ref', required: true, label: 'Certificate No.' },
          { name: 'issued_on', label: 'Issued On' },
          { name: 'valid_until', required: true, label: 'Valid Until' },
          { name: 'attachment_id', label: 'Certificate Scan' }
        ] }
    ]
  },

  'M03-form-rider-shift': {
    kind: 'model_form',
    model: 'fix.custody.scan',
    title: "Custody Scan",
    back: 'M03-custody',
    /* append-only evidence written by the rider app and the counters */
    create: false, pick: 'A custody scan is recorded by the rider app or at the counter: open one from Chain-of-Custody Scans.',
    tabs: [
      { id: 'scan', label: '1. Custody Hop', bn: '১. স্ক্যান তথ্য', icon: '📡', badge: '7' },
      { id: 'device', label: '2. Device & Serial', bn: '২. ডিভাইস ও অবস্থা', icon: '📱', badge: '1' }
    ],
    sections: [
      { tab: 'scan', title: "Custody Scan & Location Verification", note: "A custody scan is append-only evidence, stamped by the server with who scanned it and when. Scans are recorded by the workflow buttons and the rider app.",
        fields: [
          { name: 'consignment_id', label: "Consignment", readonly: true },
          { name: 'step', label: "Custody Step", readonly: true },
          { name: 'scanned_at', label: "Scanned At", readonly: true },
          { name: 'location_branch_id', label: "At Branch", readonly: true },
          { name: 'scanned_by', label: "Scanned By (Employee)", readonly: true },
          { name: 'scanned_by_user_id', label: "Scanned By (User)", readonly: true },
          { name: 'exception_reason', label: "Custody Exception Note", readonly: true }
        ] },
      { tab: 'device', title: "Device Verification",
        fields: [
          { name: 'device_serial', label: "Scanned Device Serial / IMEI", readonly: true }
        ] }
    ]
  },

  /* ===== triage coverage screens ===== */
  /* A02 audit M03-5/11, B1: the payout is approved from the M63 inbox.
   * Request Approval routes it to a claim approver holding the DOFA tier;
   * the server refuses the claim's creator, caps the payout at the claim and
   * the insured value, and pins the amount. Reject and settle stay here. */
  'M03-damage-claim': { kind: 'model_list', model: 'fix.damage.claim', stateField: 'state',
    cols: ['name', 'state', 'operating_unit_id', 'consignment_id', 'claimed_on', 'claimant', 'claimed_amount', 'approved_amount', 'dofa_tier', 'settled_amount'],
    actions: [
      { m: 'action_request_approval', l: 'Request Payout Approval', ask: 'Justification for the payout', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Approval Request' },
      { m: 'action_reject', l: 'Reject Claim', ask: 'Reason for rejecting', kwarg: 'reason' },
      { m: 'action_settle', l: 'Settle Payout', ask: 'Amount paid in BDT (blank = approved amount)', kwarg: 'settled_amount' }
    ] },

  'M03-form-damage-claim': {
    kind: 'model_form',
    model: 'fix.damage.claim',
    title: "Damage Claim",
    back: 'M03-damage-claim',
    status: { field: 'state' },
    tabs: [
      { id: 'claim', label: '1. Incident Claim', bn: '১. দাবির বিবরণ', icon: '⚠️', badge: '10' },
      { id: 'dofa', label: '2. DOFA & Financial Sign-Off', bn: '২. অনুমোদন ও আর্থিক সিদ্ধান্ত', icon: '✍️', badge: '9' }
    ],
    sections: [
      { tab: 'claim', title: "Transit Damage / Loss Incident Claim", note: "Opened from the module's own record set. Every field here is the model's real field.",
        fields: [
          { name: 'name', required: true, label: "Claim Reference", readonly: true },
          { name: 'state', label: "Claim Status", readonly: true },
          { name: 'consignment_id', required: true, label: "Consignment" },
          /* required by the model and on no form: a claim could not be saved */
          { name: 'operating_unit_id', required: true, label: "Operating Unit" },
          { name: 'claimed_on', required: true, label: "Incident / Claim Date" },
          { name: 'claimant', required: true, label: "Claimant / Consignee" },
          { name: 'damage_kind', required: true, label: "Damage Kind" },
          { name: 'liability', required: true, label: "Liability" },
          { name: 'evidence_ref', label: "Evidence Reference" },
          { name: 'description', required: true, label: "Damage Incident Details", type: "text" }
        ] },
      { tab: 'dofa', title: "DOFA Tier & Settlement Approval",
        fields: [
          { name: 'claimed_amount', label: "Claimed Amount (BDT)" },
          { name: 'requested_payout', label: "Payout Requested (BDT, blank = claimed)" },
          { name: 'approval_state', label: "Approval (M63)", readonly: true },
          { name: 'dofa_tier', label: "Required DOFA Approval Tier", readonly: true },
          { name: 'dofa_justification', label: "Approval Justification (required)", type: "text" },
          { name: 'approved_amount', label: "Approved Payout (BDT)", readonly: true },
          { name: 'approved_by_id', label: "Authorizing Approver", readonly: true },
          { name: 'approved_at', label: "Approved At", readonly: true },
          { name: 'settled_amount', label: "Settled Amount (BDT)", readonly: true },
          { name: 'settled_by_id', label: "Settled By", readonly: true },
          { name: 'incident_photo_attachment_id', label: "Damage Photo / Police GD Proof" }
        ] }
    ]
  },

};

/* built-in report chips -> the screen that shows that report */
export const REPORT_ROUTES = {
  "M03:Consignment Cycle Time": "M03-rpt-cycletime",
  "M03:Custody Exception Register": "M03-rpt-custody",
  "M03:Courier Performance (Pathao/RedX/Steadfast)": "M03-rpt-courier",
  "M03:COD Settlement Report": "M03-cod",
  "M03:Reverse Logistics Volume": "M03-rpt-reverse",
  "M03:Damage & Insurance Claims": "M03-rpt-damage"
};

/* every M03 chip names a screen (FORM_CHIPS) */
export const FORM_MODELS = {};

/* the module's "+ New": a consignment. It said "legs start from the
 * service-order hand-over", but FR-LOG-001 raises branch transfers and
 * returns to vendor that have no service order, and fix_real held 0
 * consignments with no way to make one (M03 capture audit 2026-11-12). */
export const CREATE = {
  M03: { screen: 'M03-form-consignment', model: 'fix.consignment', label: 'Consignment' }
};


export const FORM_CHIPS = {
  'M03:Courier Booking': 'M03-form-booking',
  'M03:Damage Claim': 'M03-form-damage-claim',
  'M03:Consignment': 'M03-form-consignment',
  'M03:Next Journey Leg': 'M03-form-next-leg',
  'M03:Courier Partner': 'M03-form-courier',
  'M03:Seal for Dispatch': 'M03-form-seal',
  'M03:Hub Intake Scan': 'M03-form-hub-intake',
  'M03:Proof of Delivery Record': 'M03-form-pod',
  'M03:Rider & Vehicle Assignment': 'M03-form-rider',
  /* the M50 form: the rider's hand-over is a Finance settlement */
  'M03:Rider COD Settlement': 'M50-form-cod',
  'M03:Courier POD Record': 'M03-form-courier-pod',
  'M03:Rider Certification': 'M03-form-rider-cert',
  'M03:__by_model__': {
    'fix.courier.partner': 'M03-form-courier',
    'fix.courier.booking': 'M03-form-booking',
    'fix.damage.claim': 'M03-form-damage-claim',
    'fix.consignment': 'M03-form-consignment',
    'fix.custody.scan': 'M03-form-rider-shift',
    'fix.cod.settlement': 'M50-form-cod',
    'fix.rider.certification': 'M03-form-rider-cert',
  },
  'M03:__by_screen__': {
    'M03-couriers': 'M03-form-courier',
    'M03-bookings': 'M03-form-booking',
    'M03-damage-claim': 'M03-form-damage-claim',
    'M03-cons': 'M03-form-consignment',
    'M03-custody': 'M03-form-rider-shift',
    'M03-rider-certs': 'M03-form-rider-cert',
  }
};
