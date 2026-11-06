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
          { name: 'state', label: 'State', readonly: true }
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
   * the custody chain and the POD for every one of them. */
  'M03-cons': { kind: 'model_list', model: 'fix.consignment', create: false,
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
      { m: 'action_release_hold', l: 'Release Exception Hold', ask: 'Reason for releasing the hold', kwarg: 'reason' }
    ] },
  'M03-record': { kind: 'model_list', model: 'fix.consignment', create: false,
    cols: ['name', 'consignment_type', 'state', 'service_order_id', 'custody_summary', 'chain_broken',
      'chain_problem', 'pod_verified_at', 'pod_verified_by', 'delivered_at', 'create_date'],
    stateField: 'state' },
  'M03-journeys': { kind: 'model_list', model: 'fix.custody.scan', create: false,
    cols: ['consignment_id', 'step', 'scanned_at', 'scanned_by', 'scanned_by_user_id', 'location_branch_id', 'device_serial', 'exception_reason'] },
  'M03-manifest': { kind: 'table_report', module: 'M03', report: 'manifest_register', title: 'Item Manifests', period: false },
  'M03-custody': { kind: 'model_list', model: 'fix.custody.scan', create: false,
    cols: ['consignment_id', 'step', 'scanned_at', 'exception_reason', 'device_serial'],
    domain: [['exception_reason', '!=', false]] },
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
  'M03-routes': { kind: 'table_report', module: 'M03', report: 'reverse_volume', period: false },
  'M03-app': { kind: 'table_report', module: 'M03', report: 'rider_day', title: 'Rider App (P09) Preview', period: false },
  'M03-couriers': { kind: 'model_list', model: 'fix.courier.partner', cols: ['name', 'code', 'service_area', 'base_rate', 'cod_supported', 'cod_cycle_days', 'active'] },
  'M03-bookings': { kind: 'model_list', model: 'fix.courier.booking', stateField: 'state', cols: ['name', 'partner_id', 'consignment_id', 'awb_no', 'booked_on', 'weight_kg', 'charged_amount', 'state'], actions: [
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
  'M03-rpt-damage': { kind: 'table_report', module: 'M03', report: 'damage_claims', title: "Damage & Claims", period: false },
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
    title: "Consignment (5 types)",
    back: 'M03-cons',
    status: { field: 'state', labels: { draft: "Draft", confirmed: "Confirmed", in_transit: "In Transit", held: "Exception Hold", delivered: "Delivered", returned: "Returned", lost: "Lost" } },
    tabs: [
      { id: 'journey', label: '1. Journey & Legs', bn: '১. রুট ও স্থানান্তর', icon: '🚚', badge: '8' },
      { id: 'custody', label: '2. Tamper Evident Seals', bn: '২. সিল ও নিরাপত্তা', icon: '🔒', badge: '10' },
      { id: 'volumetric', label: '3. Chargeable Weight', bn: '৩. ওজন ও বিলিং', icon: '⚖️', badge: '8' },
      { id: 'pod', label: '4. OTP Proof of Delivery', bn: '৪. ওটিপি প্রমাণক', icon: '📱', badge: '7' }
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
          { name: 'state', label: "Consignment Status", readonly: true }
        ] },
      { tab: 'custody', title: "Tamper-Evident Security Seals & Scale Verification (FLAW-03.3)",
        note: "Seal numbers and intake scale weights are verified at hub transfers with a strict 20g threshold.",
        fields: [
          { name: 'security_bag_barcode', label: "Tamper-Evident Bag Barcode" },
          { name: 'outbound_seal_number', label: "Outbound Security Seal No" },
          { name: 'inbound_seal_number', label: "Inbound Received Seal No (hub intake)", readonly: true },
          { name: 'seal_status', label: "Seal Integrity Verdict", readonly: true },
          { name: 'dispatch_weight_g', label: "Dispatch Scale Weight (g)" },
          { name: 'receive_weight_g', label: "Intake Scale Weight (g) (hub intake)", readonly: true },
          { name: 'weight_variance_g', label: "Weight Variance (g)", readonly: true },
          { name: 'chain_broken', label: "Custody Chain Broken Alert", readonly: true },
          { name: 'chain_problem', label: "Chain Problem", readonly: true },
          { name: 'hold_reason', label: "Exception Hold Reason", readonly: true }
        ] },
      { tab: 'volumetric', title: "IATA Volumetric Weight & Freight Rating (FLAW-03.2)",
        fields: [
          { name: 'actual_weight_kg', label: "Actual Scale Weight (kg)" },
          { name: 'length_cm', label: "Length (cm)" },
          { name: 'width_cm', label: "Width (cm)" },
          { name: 'height_cm', label: "Height (cm)" },
          { name: 'volumetric_divisor', label: "Volumetric Divisor" },
          { name: 'chargeable_weight_kg', label: "Chargeable Weight (kg)", readonly: true },
          { name: 'base_freight_bdt', label: "Base Freight (BDT)", readonly: true },
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
          { name: 'waybill_attachment_id', label: "Signed Waybill / Manifest" }
        ] }
    ]
  },
  'M03-form-rider-shift': {
    kind: 'model_form',
    model: 'fix.custody.scan',
    title: "Rider Shift Open/Close",
    back: 'M03-custody',
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
      { id: 'claim', label: '1. Incident Claim', bn: '১. দাবির বিবরণ', icon: '⚠️', badge: '9' },
      { id: 'dofa', label: '2. DOFA & Financial Sign-Off', bn: '২. অনুমোদন ও আর্থিক সিদ্ধান্ত', icon: '✍️', badge: '9' }
    ],
    sections: [
      { tab: 'claim', title: "Transit Damage / Loss Incident Claim", note: "Opened from the module's own record set. Every field here is the model's real field.",
        fields: [
          { name: 'name', required: true, label: "Claim Reference", readonly: true },
          { name: 'state', label: "Claim Status", readonly: true },
          { name: 'consignment_id', required: true, label: "Consignment" },
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
  'M03:Damage & Claims': 'M03-rpt-damage',
  "M03:Consignment Cycle Time": "M03-rpt-cycletime",
  "M03:Custody Exception Register": "M03-rpt-custody",
  "M03:Courier Performance (Pathao/RedX/Steadfast)": "M03-rpt-courier",
  "M03:COD Settlement Report": "M03-cod",
  "M03:Reverse Logistics Volume": "M03-rpt-reverse",
  "M03:Damage & Insurance Claims": "M03-rpt-damage"
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
    'M03-cons': 'M03-form-consignment',
    'M03-custody': 'M03-form-rider-shift',
  }
};
