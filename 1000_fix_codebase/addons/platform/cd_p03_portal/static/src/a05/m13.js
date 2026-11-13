/** @odoo-module **/
/* A05 · Circular Economy — M13 Rental & Equipment-as-a-Service (v2.1 D365 multi-tab standard).
 * 100% Dynamics 365 6-tab forms with Document Vault on all 8 forms.
 * All 7 report packs exposed as chips (including Real-Time Availability & Fleet Health).
 * Zero phantom fields: all fields verified against PostgreSQL fix_dev. */

/* Rentals at a stage that takes a condition report (fix.rental.condition
 * _STAGE_STATES): pre-delivery while draft/reserved, post-return while
 * returned/assessed. Any other pick is refused by the server. */
const RENTAL_AT_INSPECTION = [['state', 'in', ['draft', 'reserved', 'returned', 'damage_assess']]];

export const MODULE = {
  area: 'A05', code: 'M13', en: 'Rental & EaaS', title: 'M13 · Rental & EaaS',
  bn: 'ভাড়া ও ইকুইপমেন্ট', icon: '🎥',
  desc: '8 asset categories — fleet register, real-time availability, kits and accessories, reservations, e-signed agreements, deposits, condition reports, damage recovery, turnaround and re-grade, utilisation and retirement.',
  kpis: [
    { l: 'Fleet Size', m: 'fleet_size' },
    { l: 'Available Now', m: 'available_now' },
    { l: 'Active Rentals', m: 'active_rentals' },
    { l: 'Deposits Held', m: 'deposits_held', prefix: '৳ ' },
    { l: 'Damage Open', m: 'damage_recovery_open' },
    { l: 'Utilisation 30d', m: 'utilization_30d', suffix: '%' }
  ],
  groups: [
    { en: 'Fleet', screens: [
      { id: 'M13-fleet', en: 'Fleet Register', bn: 'ফ্লিট রেজিস্টার', t: 'g' },
      { id: 'M13-availability', en: 'Real-Time Availability', bn: 'রিয়েল-টাইম প্রাপ্যতা', t: 'r' },
      { id: 'M13-kits', en: 'Kits & Accessories', bn: 'কিট ও এক্সেসরিজ', t: 'g' }
    ]},
    { en: 'Booking', screens: [
      { id: 'M13-reservations', en: 'Reservations', bn: 'বুকিং রেজিস্ট্রি', t: 'g' },
      { id: 'M13-agreements', en: 'Rental Agreements', bn: 'ভাড়া চুক্তিপত্র', t: 'g' },
      { id: 'M13-deposits', en: 'Security Deposits', bn: 'জামানত খতিয়ান', t: 'g' }
    ]},
    { en: 'Lifecycle', screens: [
      { id: 'M13-condition', en: 'Condition Reports', bn: 'কন্ডিশন রিপোর্ট', t: 'g' },
      { id: 'M13-damage', en: 'Damage & Recovery', bn: 'ক্ষয়ক্ষতি ও পুনরুদ্ধার', t: 'g' },
      { id: 'M13-turnaround', en: 'Turnaround & Re-Grade', bn: 'টার্নঅ্যারাউন্ড ও রি-গ্রেড', t: 'g' }
    ]},
    { en: 'Analytics', screens: [
      { id: 'M13-utilisation', en: 'Utilisation Analytics', bn: 'ব্যবহার অ্যানালিটিক্স', t: 'r' },
      { id: 'M13-retire', en: 'Fleet Health & Retirement', bn: 'ফ্লিট স্থায়িত্ব ও অবসর', t: 'r' }
    ]}
  ],
  reports: [
    'Utilisation by Category',
    'Damage & Loss Rate',
    'Rental P&L',
    'Late Return Analysis',
    'Deposit Reconciliation',
    'Real-Time Availability',
    'Fleet Health & Retirement'
  ],
  forms: [
    'Reservation Cockpit',
    'Rental Agreement (e-sign)',
    'Condition Report',
    'Damage Assessment & Recovery',
    'Fleet Serialized Asset Master',
    'Rental Kit Bundle',
    'Turnaround & Regrading',
    /* sub-module step forms (capture audit, 2026-11-13) */
    'Security Deposit Collection',
    'Loss Waiver Request',
    'Rental Return',
    'In-Rental Fault Report',
    'Return Collection Booking',
    'Preventive Maintenance Booking',
    /* mastered by M37: a fleet unit cannot be registered without one */
    'Rental SKU (M37)'
  ],
  cross: ['M17 rental assets', 'M08 master agreements', 'M03 logistics', 'M15 rental pool stock'],
  /* Each page offers the capture of ITS function (capture audit 2026-11-13):
   * 3 prepares the agreement (not a second "+ New Reservation"), 4 takes the
   * deposit in its real tender, 6 records the return, 7 the in-rental fault,
   * 8 the turnaround checklist (a turnaround is opened by the return, never
   * typed: its old "+ New" was refused by the server). 9 is computed. */
  freg: { src: 78, sub: [
    ['1', 'Fleet Register', 9, { model: 'fix.rental.asset', cols: ['name', 'category', 'condition_grade', 'battery_health_pct', 'status'], screens: ['M13-fleet', 'M13-kits'], reports: ['Fleet Health & Retirement', 'Utilisation by Category'], forms: ['Fleet Serialized Asset Master', 'Rental Kit Bundle', 'Rental SKU (M37)'] }],
    ['2', 'Availability & Reservation', 12, { model: 'fix.rental.reservation', cols: ['name', 'customer_id', 'rental_asset_id', 'date_from', 'date_to'], screens: ['M13-availability', 'M13-reservations'], reports: ['Real-Time Availability'], forms: ['Reservation Cockpit'] }],
    ['3', 'Agreements', 10, { model: 'fix.rental.reservation', cols: ['name', 'customer_id', 'contract_id', 'agreement_state', 'signed_at'], screens: ['M13-agreements'], reports: [], forms: ['Rental Agreement (e-sign)'], create: 'M13-form-agreement' }],
    ['4', 'Deposits & Waivers', 8, { model: 'fix.rental.deposit', cols: ['name', 'customer_id', 'kind', 'amount', 'method', 'reference'], screens: ['M13-deposits'], reports: ['Deposit Reconciliation'], forms: ['Security Deposit Collection', 'Loss Waiver Request'], create: 'M13-form-deposit-take' }],
    ['5', 'Condition & Damage', 10, { model: 'fix.rental.condition', cols: ['name', 'reservation_id', 'report_type', 'grade', 'reported_on'], screens: ['M13-condition', 'M13-damage'], reports: ['Damage & Loss Rate'], forms: ['Condition Report', 'Damage Assessment & Recovery'] }],
    ['6', 'Returns & Recovery', 8, { model: 'fix.rental.damage', cols: ['reservation_id', 'category', 'cost', 'recovered_amount', 'settled'], screens: ['M13-damage'], reports: ['Late Return Analysis', 'Damage & Loss Rate'], forms: ['Rental Return', 'Damage Assessment & Recovery'], create: 'M13-form-return' }],
    ['7', 'In-Rental Support', 7, { model: 'fix.rental.reservation', cols: ['name', 'customer_id', 'rental_asset_id', 'date_to', 'service_order_id'], screens: ['M13-reservations'], reports: ['Late Return Analysis'], forms: ['In-Rental Fault Report', 'Return Collection Booking'], create: 'M13-form-fault', domain: [['state', 'in', ['delivered', 'active']]] }],
    ['8', 'Turnaround & PM', 7, { model: 'fix.rental.turnaround', cols: ['name', 'rental_asset_id', 'returned_on', 'regrade', 'state'], screens: ['M13-turnaround'], reports: ['Fleet Health & Retirement'], forms: ['Turnaround & Regrading', 'Preventive Maintenance Booking'], create: 'M13-form-turnaround' }],
    ['9', 'Analytics', 7, { model: 'fix.rental.asset', cols: ['name', 'rental_days_total', 'cumulative_revenue', 'net_book_value', 'status'], screens: ['M13-utilisation', 'M13-retire'], reports: ['Utilisation by Category', 'Rental P&L', 'Fleet Health & Retirement'], forms: [], create: false }]
  ] }
};

export const SCREENS = {
  'M13-fleet': { kind: 'model_list', model: 'fix.rental.asset', stateField: 'status',
    cols: ['name', 'rental_sku_id', 'category', 'condition_grade', 'battery_health_pct', 'status', 'operating_unit_id'],
    actions: [
      { m: 'action_send_to_maintenance', l: 'Send to Maintenance' },
      { m: 'action_ready', l: 'Release via Turnaround' },
      { m: 'action_request_approval', l: 'Request Retirement Approval', ask: 'Justification for writing off the book value', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Approval Request' },
      { m: 'action_retire', l: 'Retire (approved)' }
    ] },
  'M13-availability': { kind: 'table_report', module: 'M13', report: 'availability', title: 'Real-Time Availability', period: false },
  'M13-kits': { kind: 'model_list', model: 'fix.rental.kit',
    cols: ['name', 'rental_sku_id', 'accessory_count', 'deposit', 'active'] },
  'M13-reservations': { kind: 'model_list', model: 'fix.rental.reservation', stateField: 'state',
    cols: ['name', 'customer_id', 'rental_asset_id', 'date_from', 'date_to', 'rental_charge', 'deposit_collected', 'state'],
    actions: [
      { m: 'action_reserve', l: 'Reserve' },
      { m: 'action_deliver', l: 'Deliver' },
      { m: 'action_activate', l: 'Activate' },
      { m: 'action_return', l: 'Return' },
      { m: 'action_assess_damage', l: 'Assess Damage' },
      { m: 'action_close', l: 'Settle & Close' },
      { m: 'action_cancel', l: 'Cancel & Refund Deposit' },
      { m: 'action_generate_delivery_consignment', l: 'Create Delivery (M03)' },
      { m: 'action_generate_return_consignment', l: 'Create Return Pickup (M03)' },
      { m: 'action_issue_rental_invoice', l: 'Issue Mushak 6.3' }
    ] },
  'M13-agreements': { kind: 'model_list', model: 'fix.rental.reservation', stateField: 'agreement_state',
    cols: ['name', 'customer_id', 'contract_id', 'agreement_state', 'signed_at', 'signature_ref'],
    actions: [
      { m: 'action_send_agreement', l: 'Send for Customer Signature' },
      { m: 'action_sign_agreement', l: 'Enter Customer Signing Code', ask: 'Code the customer received by SMS', kwarg: 'code' },
      { m: 'action_reset_agreement', l: 'Reset Unsigned Agreement' }
    ] },
  /* A deposit movement is made by the rental money path (reserve, close, refund)
   * and is guarded: it is a ledger line, never typed in (2026-11-12). */
  'M13-deposits': { kind: 'model_list', model: 'fix.rental.deposit', create: false,
    cols: ['name', 'reservation_id', 'customer_id', 'kind', 'amount', 'method', 'date', 'gl_state'],
    empty: 'No deposit movement yet. A deposit is recorded when a reservation is confirmed and released or applied when the rental closes; movements are ledger entries and cannot be typed in.',
    actions: [
      { m: 'action_repost_gl', l: 'Repost GL' }
    ] },
  'M13-condition': { kind: 'model_list', model: 'fix.rental.condition',
    cols: ['name', 'reservation_id', 'report_type', 'grade', 'battery_health_pct', 'inspector_id', 'reported_on'] },
  'M13-damage': { kind: 'model_list', model: 'fix.rental.damage',
    cols: ['reservation_id', 'category', 'description', 'cost', 'recovered_amount', 'charge_approval_state', 'disputed', 'settled'],
    actions: [
      { m: 'action_request_charge_approval', l: 'Request Charge Approval', ask: 'Basis of the charge (and the dispute resolution, if disputed)', kwarg: 'justification' },
      { m: 'action_recall_charge_approval', l: 'Recall Charge Approval' },
      { m: 'action_raise_dispute', l: 'Record Customer Dispute', ask: 'The customer\'s reason', kwarg: 'reason' },
      { m: 'action_request_approval', l: 'Request Waiver Approval', ask: 'Justification for writing off the loss', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Waiver Request' },
      { m: 'action_waive', l: 'Waive (approved)' }
    ] },
  /* A turnaround is opened by the return (or Send to Maintenance) and is
   * refused when typed: no "+ New" here; its checklist is the step form. */
  'M13-turnaround': { kind: 'model_list', model: 'fix.rental.turnaround', stateField: 'state', create: false,
    empty: 'No unit is in turnaround. A turnaround opens when a rental is returned or a unit is sent to maintenance; record its checklist with Record a Turnaround Checklist.',
    cols: ['name', 'rental_asset_id', 'reservation_id', 'returned_on', 'grade_before', 'regrade', 'state'],
    actions: [
      { m: 'action_ready', l: 'Ready & Re-Grade' },
      { m: 'action_retire', l: 'Retire Asset' }
    ] },
  'M13-utilisation': { kind: 'table_report', module: 'M13', report: 'utilization_by_category', title: 'Utilisation Analytics', period: true },
  'M13-retire': { kind: 'table_report', module: 'M13', report: 'fleet_health', title: 'Fleet Health & Retirement', period: false },

  /* Report chips -> their own computed packs (All 7 active) */
  'M13-rpt-utilization': { kind: 'table_report', module: 'M13', report: 'utilization_by_category', title: 'Utilisation by Category', period: true },
  'M13-rpt-damage': { kind: 'table_report', module: 'M13', report: 'damage_loss_rate', title: 'Damage & Loss Rate', period: true },
  'M13-rpt-pl': { kind: 'table_report', module: 'M13', report: 'rental_pl', title: 'Rental P&L', period: true },
  'M13-rpt-late': { kind: 'table_report', module: 'M13', report: 'late_return', title: 'Late Return Analysis', period: true },
  'M13-rpt-deposits': { kind: 'table_report', module: 'M13', report: 'deposit_reconciliation', title: 'Deposit Reconciliation', period: false },
  'M13-rpt-availability': { kind: 'table_report', module: 'M13', report: 'availability', title: 'Real-Time Availability', period: false },
  'M13-rpt-fleet-health': { kind: 'table_report', module: 'M13', report: 'fleet_health', title: 'Fleet Health & Retirement', period: false },

  /* ============ D365 IN-WORKSPACE FORMS (6-TAB STANDARD) ============ */
  'M13-form-reservation': {
    kind: 'model_form',
    model: 'fix.rental.reservation',
    title: 'Rental Reservation Cockpit',
    back: 'M13-reservations',
    status: { field: 'state', labels: {
      draft: 'Draft', reserved: 'Reserved', delivered: 'Delivered', active: 'Active',
      returned: 'Returned', damage_assess: 'Damage Assessment', closed: 'Closed', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'general', label: '1. General & Customer', bn: '১. সাধারণ ও গ্রাহক', icon: '👤', badge: '7' },
      { id: 'window', label: '2. Schedule & Logistics', bn: '২. সময়সূচী ও লজিস্টিকস', icon: '📅', badge: '7' },
      { id: 'pricing', label: '3. Commercial & Rates', bn: '৩. বাণিজ্যিক ও রেট', icon: '৳', badge: '7' },
      { id: 'inspection', label: '4. Condition & Recovery', bn: '৪. কন্ডিশন ও রিকভারি', icon: '🔍', badge: '3' },
      { id: 'statutory', label: '5. Statutory & DOFA', bn: '৫. সংবিধিবদ্ধ ও কর্তৃত্ব', icon: '⚖️', badge: '3' },
      { id: 'vault', label: '6. Document Vault', bn: '৬. ডকুমেন্ট ভল্ট', icon: '📁', badge: '1' }
    ],
    sections: [
      { tab: 'general', title: 'Customer & Booking Master',
        fields: [
          { name: 'name', label: 'Reservation Reference', readonly: true },
          { name: 'customer_id', required: true, label: 'Customer' },
          { name: 'contract_id', label: 'Rental Contract (M08)' },
          { name: 'service_order_id', label: 'Origin Service Order (M01)' },
          { name: 'state', label: 'Booking Status', readonly: true }
        ] },
      { tab: 'general', title: 'Rental Asset Assignment',
        fields: [
          { name: 'rental_sku_id', required: true, label: 'Rental SKU' },
          { name: 'rental_asset_id', label: 'Fleet Asset Unit' },
          { name: 'device_id', label: 'Device Registry Unit (M17)' }
        ] },
      { tab: 'window', title: 'Rental Schedule Window',
        fields: [
          { name: 'date_from', required: true, label: 'Start Date' },
          { name: 'date_to', required: true, label: 'End Date' },
          { name: 'duration_days', label: 'Duration (Days)', readonly: true },
          { name: 'actual_return_date', label: 'Actual Return Date', readonly: true },
          { name: 'overdue_since', label: 'Overdue Since', readonly: true }
        ] },
      { tab: 'window', title: 'Fulfillment & Logistics (M03)',
        fields: [
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'branch_id', label: 'Booking Branch (GL)' },
          { name: 'delivery_consignment_id', label: 'Outbound Delivery Consignment', readonly: true },
          { name: 'return_consignment_id', label: 'Inbound Return Consignment', readonly: true }
        ] },
      { tab: 'pricing', title: 'Commercial Rates & Rental Charges',
        fields: [
          { name: 'daily_rate', label: 'Daily Rate (BDT)' },
          { name: 'weekly_rate', label: 'Weekly Rate (BDT)' },
          { name: 'monthly_rate', label: 'Monthly Rate (BDT)' },
          { name: 'rental_charge', label: 'Total Rental Charge', readonly: true },
          { name: 'late_fee', label: 'Accrued Late Fees', readonly: true }
        ] },
      { tab: 'pricing', title: 'Security Deposit & Surcharge',
        fields: [
          { name: 'kit_id', label: 'Rental Kit' },
          { name: 'deposit_collected', label: 'Deposit Agreed (BDT)' },
          { name: 'deposit_refunded', label: 'Deposit Refunded (BDT)', readonly: true },
          { name: 'ifrs16_classification', label: 'IFRS 16 Lessor Classification' },
          { name: 'lease_income_per_day', label: 'Lease Income per Day', readonly: true }
        ] },
      { tab: 'inspection', title: 'Condition & Recovery Dossier',
        fields: [
          { name: 'excess_billed', label: 'Excess / Damage Billed (BDT)', readonly: true },
          { name: 'excess_invoice_id', label: 'Excess Charges Invoice (M20)', readonly: true },
          { name: 'mushak_6_3_id', label: 'Rental Mushak 6.3', readonly: true }
        ] },
      { tab: 'statutory', title: 'Statutory Execution & E-Signature',
        fields: [
          { name: 'stamp_duty_cert_no', label: 'Stamp Duty Certificate No' },
          { name: 'signer_mobile', label: 'Customer Signing Mobile' },
          { name: 'agreement_state', label: 'Agreement Execution State', readonly: true },
          { name: 'signed_at', label: 'Signed Timestamp', readonly: true },
          { name: 'signature_ref', label: 'E-Signature Reference', readonly: true }
        ] },
      { tab: 'vault', title: 'Cryptographic Document Vault & Electronic Execution',
        note: 'SHA-256 e-signed rental agreement, stamp paper scan, customer NID scan, and pre/post inspection photos.',
        fields: [] }
    ]
  },

  'M13-form-agreement': {
    kind: 'model_form',
    model: 'fix.rental.reservation',
    title: 'Rental Agreement (e-Sign)',
    /* The agreement IS the booking's terms: it is prepared on a booking made
     * with + New Reservation, never as a second, empty booking (2026-11-13). */
    newLabel: 'Prepare a Rental Agreement',
    back: 'M13-agreements',
    status: { field: 'agreement_state', labels: {
      draft: 'Draft', sent: 'Signature Requested', signed: 'Signed', declined: 'Declined' } },
    pickRecord: {
      label: 'Step 1 of 2: choose the booking whose agreement you are preparing',
      note: 'Bookings whose agreement has not been sent to the customer yet.',
      search: 'Search booking or customer',
      choose: 'Prepare its agreement',
      cols: ['name', 'customer_id', 'rental_asset_id', 'date_from', 'date_to', 'agreement_state', 'state'],
      domain: [['agreement_state', 'in', ['draft', 'declined']], ['state', 'in', ['draft', 'reserved']]],
      empty: 'No booking is waiting for its agreement. Book the rental first with + New Reservation on Availability & Reservation.'
    },
    tabs: [
      { id: 'terms', label: '1. Agreement Terms', bn: '১. চুক্তির শর্তাবলী', icon: '📜', badge: '4' },
      { id: 'esign', label: '2. Digital Execution', bn: '২. ডিজিটাল সম্পাদন', icon: '✍️', badge: '3' },
      { id: 'deposit', label: '3. Security Bond', bn: '৩. জামানত বন্ড', icon: '🛡️', badge: '2' },
      { id: 'schedule', label: '4. Rental Window', bn: '৪. ভাড়ার সময়সীমা', icon: '📅', badge: '3' },
      { id: 'commercial', label: '5. Commercial Rates', bn: '৫. বাণিজ্যিক রেট', icon: '৳', badge: '3' },
      { id: 'vault', label: '6. Document Vault', bn: '৬. ডকুমেন্ট ভল্ট', icon: '📁', badge: '1' }
    ],
    sections: [
      { tab: 'terms', title: 'Contract Scope & Identification',
        note: 'Save the terms, then press Send for Customer Signature on Rental Agreements: the customer signs with the code sent to their mobile, and the terms freeze once sent.',
        fields: [
          { name: 'name', label: 'Reservation Reference', readonly: true },
          { name: 'customer_id', label: 'Customer', readonly: true },
          { name: 'contract_id', label: 'Rental Contract (M08)' },
          { name: 'agreement_state', label: 'Agreement State', readonly: true },
          { name: 'special_terms', type: 'text', label: 'Special Terms & Indemnity' },
          { name: 'liability_cap_amount', label: 'Liability Cap (BDT)' }
        ] },
      { tab: 'esign', title: 'Customer E-Signature (one-time code)',
        note: 'Signed by the customer with the code sent to their mobile; staff never type the signature.',
        fields: [
          { name: 'signer_mobile', label: 'Customer Signing Mobile' },
          { name: 'signed_at', label: 'Signed Timestamp', readonly: true },
          { name: 'signature_ref', label: 'Signature Evidence Token', readonly: true }
        ] },
      { tab: 'deposit', title: 'Security Deposit Bond',
        fields: [
          { name: 'stamp_duty_cert_no', label: 'Stamp Duty Certificate No' },
          { name: 'deposit_collected', label: 'Deposit Agreed (BDT)' },
          { name: 'deposit_refunded', label: 'Deposit Refunded (BDT)', readonly: true }
        ] },
      { tab: 'schedule', title: 'Agreed Usage Window',
        fields: [
          { name: 'date_from', label: 'Start Date' },
          { name: 'date_to', label: 'End Date' },
          { name: 'duration_days', label: 'Duration (Days)', readonly: true }
        ] },
      { tab: 'commercial', title: 'Agreed Tariff Structure',
        fields: [
          { name: 'daily_rate', label: 'Daily Rate' },
          { name: 'rental_charge', label: 'Rental Charge (BDT)', readonly: true },
          { name: 'late_fee', label: 'Late Fee (computed)', readonly: true }
        ] },
      { tab: 'vault', title: 'Cryptographic Document Vault & E-Sign Stamp',
        note: 'Tamper-evident legal agreement copy and customer verification proofs.',
        fields: [] }
    ]
  },

  'M13-form-condition': {
    kind: 'model_form',
    model: 'fix.rental.condition',
    title: 'Condition Inspection Report',
    back: 'M13-condition',
    tabs: [
      { id: 'header', label: '1. Report Header', bn: '১. রিপোর্ট পরিচিতি', icon: '📋', badge: '5' },
      { id: 'checklist', label: '2. Physical Checklist', bn: '২. বাহ্যিক চেকলিস্ট', icon: '🔍', badge: '4' },
      { id: 'battery', label: '3. Battery & Power', bn: '৩. ব্যাটারি ও পাওয়ার', icon: '🔋', badge: '1' },
      { id: 'regrade', label: '4. Regrade & Notes', bn: '৪. রি-গ্রেড ও মন্তব্য', icon: '⭐', badge: '2' },
      { id: 'inspector', label: '5. Inspector Master', bn: '৫. পরিদর্শক ও তারিখ', icon: '👤', badge: '2' },
      { id: 'vault', label: '6. Photographic Vault', bn: '৬. ছবি প্রমাণ ভল্ট', icon: '📸', badge: '1' }
    ],
    sections: [
      { tab: 'header', title: 'Report Identification & Reference',
        fields: [
          { name: 'name', label: 'Report Ref', readonly: true },
          /* only rentals at a stage that takes a report: pre-delivery while
           * draft/reserved, post-return while returned/assessed */
          { name: 'reservation_id', required: true, label: 'Reservation', domain: RENTAL_AT_INSPECTION },
          { name: 'rental_asset_id', label: 'Fleet Asset' },
          { name: 'report_type', required: true, label: 'Inspection Type (Pre/Post)' }
        ] },
      { tab: 'checklist', title: '15-Point Physical Inspection',
        fields: [
          { name: 'charger_ok', label: 'Original Charger Present' },
          { name: 'case_ok', label: 'Protective Bag/Case Present' },
          { name: 'screen_ok', label: 'Display Screen Scratch/Crack Free' },
          { name: 'ports_ok', label: 'Connectors & Ports Functional' },
          { name: 'body_condition_rating', label: 'Body Condition' },
          { name: 'maintenance_required', label: 'Maintenance Required (the turnaround must fix it)' }
        ] },
      { tab: 'battery', title: 'Battery Diagnostics',
        fields: [
          { name: 'battery_health_pct', label: 'Battery Health Percentage (%)' },
          { name: 'charge_cycles', label: 'Charge Cycles (read at inspection)' }
        ] },
      { tab: 'regrade', title: 'Grade Recommendation & Observations',
        fields: [
          { name: 'grade', required: true, label: 'Condition Grade (A/B/C/D)' },
          { name: 'notes', type: 'text', label: 'Inspector Findings & Damage Notes' }
        ] },
      { tab: 'inspector', title: 'Inspector & Submission Date',
        fields: [
          { name: 'inspector_id', label: 'Certified Inspector' },
          { name: 'reported_on', required: true, label: 'Inspection Date' }
        ] },
      { tab: 'vault', title: 'Photographic Evidence Vault',
        note: '360-degree high-resolution inspection photos and diagnostic logs.',
        fields: [
          { name: 'photos_ref', label: 'Cloud Photo Archive URL' }
        ] }
    ]
  },

  'M13-form-damage': {
    kind: 'model_form',
    model: 'fix.rental.damage',
    title: 'Damage Assessment & Recovery',
    back: 'M13-damage',
    tabs: [
      { id: 'incident', label: '1. Incident Dossier', bn: '১. দুর্ঘটনার বিবরণ', icon: '⚠️', badge: '4' },
      { id: 'estimation', label: '2. Repair Costing', bn: '২. মেরামত ব্যয়', icon: '🛠️', badge: '1' },
      { id: 'recovery', label: '3. Recovery & Offset', bn: '৩. আদায় ও সমন্বয়', icon: '৳', badge: '2' },
      { id: 'dispute', label: '4. Customer Dispute', bn: '৪. গ্রাহক বিরোধ', icon: '⚖️', badge: '1' },
      { id: 'governance', label: '5. Governance & DOFA', bn: '৫. অনুমোদন ও সংস্থা', icon: '🏢', badge: '2' },
      { id: 'vault', label: '6. Damage Evidence Vault', bn: '৬. ক্ষয়ক্ষতি প্রমাণ ভল্ট', icon: '📁', badge: '1' }
    ],
    sections: [
      { tab: 'incident', title: 'Damage Incident Classification',
        fields: [
          /* damage is assessed on a returned unit only */
          { name: 'reservation_id', required: true, label: 'Reservation', domain: [['state', 'in', ['returned', 'damage_assess']]] },
          { name: 'category', required: true, label: 'Damage Category' },
          { name: 'description', required: true, type: 'text', label: 'Detailed Failure Description' },
          { name: 'incident_date', label: 'Discovered On' },
          { name: 'inspector_id', label: 'Reporting Inspector' }
        ] },
      { tab: 'estimation', title: 'Estimated Restoration & Parts Cost',
        fields: [
          { name: 'cost', required: true, label: 'Assessed Damage Cost (BDT)' },
          { name: 'estimated_repair_hours', label: 'Estimated Repair Hours' }
        ] },
      { tab: 'recovery', title: 'Deposit Settlement & Financial Recovery',
        fields: [
          { name: 'recovered_amount', label: 'Recovered from Deposit (ledger)', readonly: true },
          { name: 'unrecovered_loss_amount', label: 'Unrecovered Loss', readonly: true },
          { name: 'waived', label: 'Waived (DOFA)', readonly: true },
          { name: 'waived_amount', label: 'Waived Amount', readonly: true },
          { name: 'settled', label: 'Settlement Completed', readonly: true }
        ] },
      { tab: 'dispute', title: 'Customer Arbitration & Objections',
        fields: [
          { name: 'disputed', label: 'Disputed by Customer' },
          { name: 'dispute_reason', label: 'Dispute Reason' },
          { name: 'settlement_notes', type: 'text', label: 'Arbitration / Settlement Notes' },
          { name: 'dispute_resolved_by_id', label: 'Dispute Resolved By', readonly: true }
        ] },
      { tab: 'governance', title: 'Approvals (M63) & Authority',
        fields: [
          { name: 'charge_approval_state', label: 'Charge Approval', readonly: true },
          { name: 'approval_state', label: 'Waiver Approval', readonly: true },
          { name: 'dofa_tier_required', label: 'Waiver DOFA Tier', readonly: true },
          { name: 'dofa_justification', type: 'text', label: 'Waiver Justification' },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'company_id', label: 'Company' }
        ] },
      { tab: 'vault', title: 'Damage Evidence Vault',
        note: 'Forensic photographs of equipment damage, workshop repair estimate sheet, and signed settlement voucher.',
        fields: [
          { name: 'evidence_url', label: 'Forensic Evidence Cloud Link' }
        ] }
    ]
  },

  'M13-form-asset': {
    kind: 'model_form',
    model: 'fix.rental.asset',
    title: 'Fleet Serialized Asset Master',
    back: 'M13-fleet',
    status: { field: 'status', labels: {
      available: 'Available', reserved: 'Reserved', out: 'On Rent',
      maintenance: 'In Maintenance', retired: 'Retired' } },
    tabs: [
      { id: 'identity', label: '1. Asset Identity', bn: '১. সম্পদের পরিচিতি', icon: '🎥', badge: '4' },
      { id: 'lifecycle', label: '2. Operational Status', bn: '২. পরিচালন অবস্থা', icon: '⚙️', badge: '3' },
      { id: 'depreciation', label: '3. IAS 16 Depreciation', bn: '৩. অবচয় হিসাব', icon: '📉', badge: '5' },
      { id: 'condition', label: '4. Health & Battery', bn: '৪. স্বাস্থ্য ও ব্যাটারি', icon: '🔋', badge: '3' },
      { id: 'financial', label: '5. Financial Valuation', bn: '৫. আর্থিক মূল্যমান', icon: '৳', badge: '3' },
      { id: 'vault', label: '6. Document Vault', bn: '৬. ডকুমেন্ট ভল্ট', icon: '📁', badge: '1' }
    ],
    sections: [
      { tab: 'identity', title: 'Asset Master & Registry',
        fields: [
          { name: 'name', required: true, label: 'Asset Code' },
          { name: 'serial_no', label: 'Serial Number' },
          { name: 'rental_sku_id', required: true, label: 'Rental SKU' },
          { name: 'category', required: true, label: 'Asset Category' }
        ] },
      { tab: 'lifecycle', title: 'Operational Status & Allocation',
        fields: [
          { name: 'status', label: 'Operational Status', readonly: true },
          { name: 'device_id', label: 'Hardware Registry Unit (M17)' },
          { name: 'fixed_asset_id', label: 'Fixed Asset (M49)' },
          { name: 'operating_unit_id', label: 'Operating Unit Depot' }
        ] },
      { tab: 'depreciation', title: 'IAS 16 Straight-Line Capital Depreciation',
        fields: [
          { name: 'purchase_cost', label: 'Capital Acquisition Cost (BDT)' },
          { name: 'residual_value', label: 'Residual Value (BDT)' },
          { name: 'useful_life_days', label: 'Statutory Useful Life (Days)' },
          { name: 'daily_depreciation', label: 'Daily Accrued Depreciation (BDT)', readonly: true },
          { name: 'net_book_value', label: 'Net Book Value (BDT)', readonly: true }
        ] },
      { tab: 'condition', title: 'Asset Quality & Battery Diagnostics',
        fields: [
          { name: 'condition_grade', label: 'Condition Grade' },
          { name: 'battery_health_pct', label: 'Battery Health %' },
          { name: 'acquisition_date', label: 'Acquisition Date' }
        ] },
      { tab: 'financial', title: 'Retirement & Disinvestment',
        fields: [
          { name: 'retired_on', label: 'Retirement Date', readonly: true },
          { name: 'retirement_reason', label: 'Reason for Retirement' },
          { name: 'dofa_tier_required', label: 'Retirement DOFA Tier', readonly: true },
          { name: 'approval_state', label: 'Retirement Approval', readonly: true },
          { name: 'dofa_justification', type: 'text', label: 'Retirement Justification' },
          { name: 'disposal_id', label: 'M49 Disposal', readonly: true },
          { name: 'notes', type: 'text', label: 'Asset Service Notes' }
        ] },
      { tab: 'vault', title: 'Asset Provenance & Invoice Vault',
        note: 'Original purchase invoice, manufacturer warranty certificate, calibration records, and equipment photos.',
        fields: [] }
    ]
  },

  'M13-form-kit': {
    kind: 'model_form',
    model: 'fix.rental.kit',
    title: 'Rental Kit Bundle',
    back: 'M13-kits',
    tabs: [
      { id: 'general', label: '1. Kit Setup', bn: '১. কিট পরিচিতি', icon: '📦', badge: '2' },
      { id: 'accessories', label: '2. Included Items', bn: '২. সংযুক্ত সামগ্রী', icon: '🔌', badge: '2' },
      { id: 'pricing', label: '3. Deposit & Rates', bn: '৩. জামানত ও রেট', icon: '৳', badge: '1' },
      { id: 'status', label: '4. Pool Availability', bn: '৪. প্রাপ্যতা স্ট্যাটাস', icon: '🟢', badge: '1' },
      { id: 'governance', label: '5. Governance', bn: '৫. প্রতিষ্ঠান নিয়ন্ত্রণ', icon: '🏢', badge: '1' },
      { id: 'vault', label: '6. Kit Packing Vault', bn: '৬. প্যাকিং গাইড ভল্ট', icon: '📁', badge: '1' }
    ],
    sections: [
      { tab: 'general', title: 'Rental Kit Master',
        fields: [
          { name: 'name', required: true, label: 'Kit Name' },
          { name: 'rental_sku_id', required: true, label: 'Associated Rental SKU' }
        ] },
      { tab: 'accessories', title: 'Manifest of Bundled Accessories',
        fields: [
          { name: 'accessories', type: 'text', label: 'Accessories (one per line)' },
          { name: 'accessory_count', label: 'Count of Bundled Items', readonly: true }
        ] },
      { tab: 'pricing', title: 'Security Bond Surcharge',
        fields: [
          { name: 'deposit', label: 'Required Deposit Surcharge (BDT)' }
        ] },
      { tab: 'status', title: 'Pool Lifecycle',
        fields: [
          { name: 'active', label: 'Active in Rental Catalog' }
        ] },
      { tab: 'governance', title: 'Enterprise Scope',
        fields: [
          { name: 'company_id', label: 'Company' }
        ] },
      { tab: 'vault', title: 'Kit Manifest & Assembly Guide',
        note: 'Standard packing layout photograph, accessory check-sheet, and cable diagram.',
        fields: [] }
    ]
  },

  'M13-form-deposit': {
    kind: 'model_form',
    model: 'fix.rental.deposit',
    title: 'Deposit Movement Ledger',
    back: 'M13-deposits',
    create: false, pick: 'A deposit movement is made by the rental money path: open one from Deposits & Waivers.',
    tabs: [
      { id: 'general', label: '1. Transaction', bn: '১. লেনদেন বিবরণ', icon: '💳', badge: '4' },
      { id: 'payment', label: '2. Payment Channel', bn: '২. পেমেন্ট মাধ্যম', icon: '🏦', badge: '3' },
      { id: 'gl_move', label: '3. Dual-Entry GL', bn: '৩. সাধারণ খতিয়ান', icon: '⚖️', badge: '2' },
      { id: 'customer', label: '4. Customer Master', bn: '৪. গ্রাহক বিবরণ', icon: '👤', badge: '1' },
      { id: 'audit', label: '5. Treasury Audit', bn: '৫. ট্রেজারি নিরীক্ষা', icon: '📝', badge: '1' },
      { id: 'vault', label: '6. Receipt Vault', bn: '৬. রসিদ ভল্ট', icon: '📁', badge: '1' }
    ],
    sections: [
      { tab: 'general', title: 'Deposit Ledger Movement',
        fields: [
          { name: 'name', label: 'Deposit Sequence', readonly: true },
          { name: 'reservation_id', label: 'Reservation', readonly: true },
          { name: 'kind', label: 'Movement Kind', readonly: true },
          { name: 'amount', label: 'Transaction Amount (BDT)', readonly: true }
        ] },
      { tab: 'payment', title: 'Payment Channel & Date',
        fields: [
          { name: 'method', label: 'Payment Method', readonly: true },
          { name: 'reference', label: 'MFS / Bank Transaction Ref' },
          { name: 'date', label: 'Transaction Date', readonly: true }
        ] },
      { tab: 'gl_move', title: 'Financial Dual-Entry Posting',
        note: 'Movements are made by the rental money path and are immutable once posted.',
        fields: [
          { name: 'gl_state', label: 'GL State', readonly: true },
          { name: 'journal_entry_id', label: 'GL Journal Entry (Debit Bank / Credit Liability)', readonly: true },
          { name: 'gl_note', label: 'GL Note', readonly: true },
          { name: 'payment_execution_id', label: 'Refund Instruction (M50)', readonly: true },
          { name: 'note', label: 'Accounting Notes' }
        ] },
      { tab: 'customer', title: 'Enterprise Customer Linkage',
        fields: [
          { name: 'customer_id', label: 'Customer', readonly: true }
        ] },
      { tab: 'audit', title: 'Corporate Controls',
        fields: [
          { name: 'company_id', label: 'Operating Company', readonly: true }
        ] },
      { tab: 'vault', title: 'Bank Voucher & MFS Proof Vault',
        note: 'Bank deposit receipt, customer refund acknowledgment, and signed waiver form.',
        fields: [] }
    ]
  },

  'M13-form-turnaround': {
    kind: 'model_form',
    model: 'fix.rental.turnaround',
    title: 'Turnaround & Regrading Dossier',
    /* opened by the return / Send to Maintenance; this records its checklist */
    newLabel: 'Record a Turnaround Checklist',
    back: 'M13-turnaround',
    status: { field: 'state', labels: {
      pending: 'Pending', cleaning: 'Cleaning', inspection: 'Inspection',
      ready: 'Ready', retired: 'Retired' } },
    pickRecord: {
      label: 'Step 1 of 2: choose the unit in turnaround',
      note: 'Turnarounds not yet released or retired.',
      search: 'Search turnaround',
      choose: 'Record its checklist',
      cols: ['name', 'rental_asset_id', 'reservation_id', 'returned_on', 'grade_before', 'state'],
      domain: [['state', 'in', ['pending', 'cleaning', 'inspection']]],
      empty: 'No unit is in turnaround. A turnaround opens when a rental is returned or a unit is sent to maintenance.'
    },
    tabs: [
      { id: 'general', label: '1. Turnaround Dossier', bn: '১. টার্নঅ্যারাউন্ড বিবরণ', icon: '🔄', badge: '4' },
      { id: 'intake', label: '2. Return Condition', bn: '২. ফেরত অবস্থা', icon: '📋', badge: '1' },
      { id: 'cleaning', label: '3. Sanitization & QC', bn: '৩. পরিচ্ছন্নতা ও কিউসি', icon: '🧼', badge: '2' },
      { id: 'regrade', label: '4. Regrade Decision', bn: '৪. রি-গ্রেড সিদ্ধান্ত', icon: '⭐', badge: '2' },
      { id: 'lifecycle', label: '5. Status Progression', bn: '৫. অগ্রগতি স্ট্যাটাস', icon: '⚙️', badge: '2' },
      { id: 'vault', label: '6. Quality Sign-Off Vault', bn: '৬. কোয়ালিটি অনুমোদন ভল্ট', icon: '📁', badge: '1' }
    ],
    sections: [
      { tab: 'general', title: 'Asset Turnaround Dossier',
        fields: [
          { name: 'name', label: 'Turnaround Ref', readonly: true },
          { name: 'rental_asset_id', label: 'Fleet Asset Unit', readonly: true },
          { name: 'reservation_id', label: 'Completed Reservation', readonly: true },
          { name: 'returned_on', label: 'Return Intake Date', readonly: true }
        ] },
      { tab: 'intake', title: 'Initial Grade Assessment',
        fields: [
          { name: 'grade_before', label: 'Grade Prior to Inspection', readonly: true }
        ] },
      { tab: 'cleaning', title: 'Sanitization, Data Wipe & Technical Checklist',
        note: 'A data-bearing unit is released only on a verified M06 wipe certificate bound to its serial. Save the checklist, then press Ready & Re-Grade on Turnaround & Re-Grade.',
        fields: [
          { name: 'cleaning_done', label: 'Full Physical Decontamination Done' },
          { name: 'sensor_cleaned', label: 'Sensors / Lenses Cleaned' },
          { name: 'connectors_inspected', label: 'Connectors Inspected' },
          { name: 'firmware_updated', label: 'Firmware Updated' },
          { name: 'memory_card_wiped', label: 'Memory Card Wiped' },
          { name: 'internal_storage_factory_reset', label: 'Internal Storage Factory Reset' },
          { name: 'inspection_done', label: 'Diagnostics & Functionality Checked' },
          { name: 'functional_score_pct', label: 'Bench Functional Score %' },
          { name: 'battery_health_after_pm', label: 'Battery Health After PM %' },
          { name: 'technician_id', label: 'Turnaround Technician' },
          { name: 'data_wipe_certificate_id', label: 'Data Wipe Certificate (M06)' },
          { name: 'nist_wipe_hash', label: 'Verified Wipe Hash (from M06)', readonly: true }
        ] },
      { tab: 'regrade', title: 'Official Re-Grading Decision',
        fields: [
          { name: 'regrade', label: 'Final Re-Graded Condition' },
          { name: 'available_on', label: 'Returned to Available Pool On', readonly: true }
        ] },
      { tab: 'lifecycle', title: 'Turnaround State & Observations',
        fields: [
          { name: 'state', label: 'Turnaround State', readonly: true },
          { name: 'notes', label: 'Technician Notes' }
        ] },
      { tab: 'vault', title: 'Turnaround Sign-Off Vault',
        note: 'Quality sign-off certificate, sanitized asset photo, and calibration report.',
        fields: [] }
    ]
  },

  /* ============ SUB-MODULE STEP FORMS (capture audit, 2026-11-13) ============
   * Pick-then-act: each acts on an existing record through its workflow
   * method, which is what records the step (the fields are guarded). */

  /* 4 Deposits & Waivers: the deposit is taken when the booking is confirmed,
   * in the tender the customer paid with. It used to be booked as cash
   * whatever was taken, so a bKash deposit was posted to the cash account and
   * refunded as cash. */
  'M13-form-deposit-take': {
    kind: 'model_form',
    model: 'fix.rental.reservation',
    title: 'Security Deposit Collection',
    newLabel: 'Take a Security Deposit',
    back: 'M13-deposits',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the booking the customer is paying the deposit for',
      note: 'Draft bookings. Taking the deposit confirms the booking and holds the unit.',
      search: 'Search booking or customer',
      choose: 'Take its deposit',
      cols: ['name', 'customer_id', 'rental_asset_id', 'date_from', 'date_to', 'deposit_collected'],
      domain: [['state', '=', 'draft']],
      empty: 'No draft booking is waiting for its deposit. Book the rental first with + New Reservation on Availability & Reservation.'
    },
    saveAction: {
      method: 'action_reserve', label: 'Take Deposit & Confirm Booking',
      done: 'Deposit recorded and the booking confirmed',
      kwargs: { method: 'deposit_method', reference: 'deposit_reference' }
    },
    sections: [
      { title: 'Step 2 of 2: How the Deposit Was Paid (FR-RNT-014)',
        note: 'The amount is the deposit agreed on the booking; it is held as a liability (never revenue) and posted to the General Ledger account of the tender you choose. A refund goes back the same way. A non-cash deposit needs its transaction reference.',
        fields: [
          { name: 'name', label: 'Booking', readonly: true },
          { name: 'customer_id', label: 'Customer', readonly: true },
          { name: 'rental_asset_id', label: 'Fleet Unit', readonly: true },
          { name: 'deposit_collected', label: 'Deposit Agreed (BDT)', readonly: true },
          /* INPUTS: saveAction carries them to action_reserve */
          { name: 'deposit_method', required: true, label: 'Deposit Taken By', readonly: true },
          { name: 'deposit_reference', label: 'bKash / Nagad / Card / Bank Transaction Reference', readonly: true }
        ] }
    ]
  },

  /* 4 Deposits & Waivers: an unrecovered loss is written off only by a routed
   * M63 approval; this is the request (the approver decides in the inbox). */
  'M13-form-waiver': {
    kind: 'model_form',
    model: 'fix.rental.damage',
    title: 'Loss Waiver Request',
    newLabel: 'Request a Loss Waiver',
    back: 'M13-damage',
    status: { field: 'approval_state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the damage whose unrecovered loss is to be waived',
      note: 'Damage lines with a loss the deposit did not cover, not waived and not awaiting a decision.',
      search: 'Search damage',
      choose: 'Request its waiver',
      cols: ['reservation_id', 'category', 'description', 'cost', 'recovered_amount', 'unrecovered_loss_amount', 'approval_state'],
      domain: [['unrecovered_loss_amount', '>', 0], ['waived', '=', false], ['approval_state', 'not in', ['pending', 'approved']]],
      empty: 'No damage carries an unrecovered loss to waive.'
    },
    saveAction: {
      method: 'action_request_approval', label: 'Send Waiver Request',
      done: 'Waiver request sent to the approver\'s inbox',
      kwargs: { justification: 'dofa_justification' }
    },
    sections: [
      { title: 'Step 2 of 2: Justification (BRU-RNT-22, DOFA)',
        note: 'The request is routed to the holders of the tier the loss amount requires, never to you or to whoever assessed the damage. Once approved, press Waive (approved) on Damage & Recovery. A loss already invoiced to the customer is walked back by a credit note, not a waiver.',
        fields: [
          { name: 'reservation_id', label: 'Rental', readonly: true },
          { name: 'description', label: 'Damage', readonly: true },
          { name: 'cost', label: 'Assessed Cost (BDT)', readonly: true },
          { name: 'recovered_amount', label: 'Recovered from Deposit (BDT)', readonly: true },
          { name: 'unrecovered_loss_amount', label: 'Loss to Waive (BDT)', readonly: true },
          { name: 'dofa_tier_required', label: 'Approval Tier', readonly: true },
          /* INPUT: saveAction carries it to action_request_approval */
          { name: 'dofa_justification', required: true, type: 'text', label: 'Why the loss should be written off', readonly: true }
        ] }
    ]
  },

  /* 6 Returns & Recovery: the unit comes back. The return stamps the date,
   * computes any late fee once and opens the unit's turnaround. */
  'M13-form-return': {
    kind: 'model_form',
    model: 'fix.rental.reservation',
    title: 'Rental Return',
    newLabel: 'Record a Rental Return',
    back: 'M13-reservations',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the rental whose unit has come back',
      note: 'Rentals that are out with the customer.',
      search: 'Search rental or customer',
      choose: 'Record its return',
      cols: ['name', 'customer_id', 'rental_asset_id', 'date_from', 'date_to', 'overdue_since'],
      domain: [['state', '=', 'active']],
      empty: 'No rental is out with a customer.'
    },
    saveAction: {
      method: 'action_return', label: 'Record Return',
      done: 'Return recorded; the unit is in turnaround'
    },
    sections: [
      { title: 'Step 2 of 2: Confirm the Return (FR-RNT-017/018)',
        note: 'Today is recorded as the return date. A late return is charged once at the configured rate; an early one is not refunded here. Next: the post-return Condition Report against the outbound one, then any damage on Damage Assessment & Recovery.',
        fields: [
          { name: 'name', label: 'Rental', readonly: true },
          { name: 'customer_id', label: 'Customer', readonly: true },
          { name: 'rental_asset_id', label: 'Fleet Unit', readonly: true },
          { name: 'date_to', label: 'Due Back', readonly: true },
          { name: 'overdue_since', label: 'Overdue Since', readonly: true },
          { name: 'deposit_collected', label: 'Deposit Agreed (BDT)', readonly: true }
        ] }
    ]
  },

  /* 7 In-Rental Support: the customer reports a fault on a unit out on rent. */
  'M13-form-fault': {
    kind: 'model_form',
    model: 'fix.rental.reservation',
    title: 'In-Rental Fault Report',
    newLabel: 'Report a Fault on a Live Rental',
    back: 'M13-reservations',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the live rental with the faulty unit',
      note: 'Rentals delivered to or active with the customer.',
      search: 'Search rental or customer',
      choose: 'Report its fault',
      cols: ['name', 'customer_id', 'rental_asset_id', 'date_to', 'service_order_id'],
      domain: [['state', 'in', ['delivered', 'active']]],
      empty: 'No rental is out with a customer.'
    },
    saveAction: {
      method: 'action_report_fault', label: 'Record Fault',
      done: 'Fault recorded and support to-do raised',
      kwargs: { fault: 'fault_report' }
    },
    sections: [
      { title: 'Step 2 of 2: What Is Wrong (FR-RNT-027)',
        note: 'The fault is written to the rental\'s history with your name and the time, and a to-do with the support / swap deadline goes to whoever booked the rental. A unit swap is not yet recorded by the system.',
        fields: [
          { name: 'name', label: 'Rental', readonly: true },
          { name: 'customer_id', label: 'Customer', readonly: true },
          { name: 'rental_asset_id', label: 'Fleet Unit', readonly: true },
          { name: 'date_to', label: 'Due Back', readonly: true },
          /* INPUT: saveAction carries it to action_report_fault */
          { name: 'fault_report', required: true, type: 'text', label: 'Fault as the Customer Described It', readonly: true }
        ] }
    ]
  },

  /* 7 In-Rental Support: book the M03 collection of a unit from the customer. */
  'M13-form-collection': {
    kind: 'model_form',
    model: 'fix.rental.reservation',
    title: 'Return Collection Booking',
    newLabel: 'Book a Return Collection (M03)',
    back: 'M13-reservations',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the rental to collect the unit from',
      note: 'Live rentals with no collection booked yet.',
      search: 'Search rental or customer',
      choose: 'Book its collection',
      cols: ['name', 'customer_id', 'rental_asset_id', 'date_to', 'operating_unit_id'],
      domain: [['state', 'in', ['delivered', 'active']], ['return_consignment_id', '=', false]],
      empty: 'No live rental is waiting for a collection to be booked.'
    },
    saveAction: {
      method: 'action_generate_return_consignment', label: 'Book Collection',
      done: 'Collection consignment created in M03'
    },
    sections: [
      { title: 'Step 2 of 2: Confirm the Collection (FR-RNT-022)',
        note: 'An M03 pickup consignment is created for the rental\'s operating unit (or yours); logistics schedules the rider from there.',
        fields: [
          { name: 'name', label: 'Rental', readonly: true },
          { name: 'customer_id', label: 'Customer', readonly: true },
          { name: 'rental_asset_id', label: 'Fleet Unit', readonly: true },
          { name: 'date_to', label: 'Due Back', readonly: true },
          { name: 'operating_unit_id', label: 'Operating Unit', readonly: true }
        ] }
    ]
  },

  /* 8 Turnaround & PM: take an available unit out for preventive maintenance. */
  'M13-form-pm': {
    kind: 'model_form',
    model: 'fix.rental.asset',
    title: 'Preventive Maintenance Booking',
    newLabel: 'Send a Unit to Preventive Maintenance',
    back: 'M13-fleet',
    status: { field: 'status' },
    pickRecord: {
      label: 'Step 1 of 2: choose the available unit due for maintenance',
      note: 'Units available in the fleet.',
      search: 'Search asset code',
      choose: 'Send it to maintenance',
      cols: ['name', 'rental_sku_id', 'category', 'condition_grade', 'battery_health_pct', 'operating_unit_id'],
      domain: [['status', '=', 'available']],
      empty: 'No unit is available to take out for maintenance.'
    },
    saveAction: {
      method: 'action_send_to_maintenance', label: 'Send to Maintenance',
      done: 'Unit taken out of availability; turnaround opened'
    },
    sections: [
      { title: 'Step 2 of 2: Confirm (FR-RNT-028, BRU-RNT-21)',
        note: 'The unit leaves availability and a turnaround opens; it comes back only when that turnaround\'s checklist is complete and it is released.',
        fields: [
          { name: 'name', label: 'Asset Code', readonly: true },
          { name: 'rental_sku_id', label: 'Rental SKU', readonly: true },
          { name: 'category', label: 'Category', readonly: true },
          { name: 'condition_grade', label: 'Condition Grade', readonly: true },
          { name: 'battery_health_pct', label: 'Battery Health %', readonly: true }
        ] }
    ]
  }
};

export const REPORT_ROUTES = {
  'M13:Utilisation by Category': 'M13-rpt-utilization',
  'M13:Damage & Loss Rate': 'M13-rpt-damage',
  'M13:Rental P&L': 'M13-rpt-pl',
  'M13:Late Return Analysis': 'M13-rpt-late',
  'M13:Deposit Reconciliation': 'M13-rpt-deposits',
  'M13:Real-Time Availability': 'M13-rpt-availability',
  'M13:Fleet Health & Retirement': 'M13-rpt-fleet-health'
};

export const FORM_MODELS = {
  'M13:Reservation Cockpit': 'fix.rental.reservation',
  'M13:Rental Agreement (e-sign)': 'fix.rental.reservation',
  'M13:Condition Report': 'fix.rental.condition',
  'M13:Damage Assessment & Recovery': 'fix.rental.damage',
  'M13:Fleet Serialized Asset Master': 'fix.rental.asset',
  'M13:Rental Kit Bundle': 'fix.rental.kit',
  'M13:Turnaround & Regrading': 'fix.rental.turnaround',
  'M13:Security Deposit Collection': 'fix.rental.reservation',
  'M13:Loss Waiver Request': 'fix.rental.damage',
  'M13:Rental Return': 'fix.rental.reservation',
  'M13:In-Rental Fault Report': 'fix.rental.reservation',
  'M13:Return Collection Booking': 'fix.rental.reservation',
  'M13:Preventive Maintenance Booking': 'fix.rental.asset',
  'M13:Rental SKU (M37)': 'fix.rental.sku'
};

export const FORM_CHIPS = {
  'M13:Reservation Cockpit': 'M13-form-reservation',
  'M13:Rental Agreement (e-sign)': 'M13-form-agreement',
  'M13:Condition Report': 'M13-form-condition',
  'M13:Damage Assessment & Recovery': 'M13-form-damage',
  'M13:Fleet Serialized Asset Master': 'M13-form-asset',
  'M13:Rental Kit Bundle': 'M13-form-kit',
  'M13:Turnaround & Regrading': 'M13-form-turnaround',
  'M13:Security Deposit Collection': 'M13-form-deposit-take',
  'M13:Loss Waiver Request': 'M13-form-waiver',
  'M13:Rental Return': 'M13-form-return',
  'M13:In-Rental Fault Report': 'M13-form-fault',
  'M13:Return Collection Booking': 'M13-form-collection',
  'M13:Preventive Maintenance Booking': 'M13-form-pm',
  'M13:Rental SKU (M37)': 'M37-form-rentalsku',
  'M13:__by_model__': {
    'fix.rental.reservation': 'M13-form-reservation',
    'fix.rental.condition': 'M13-form-condition',
    'fix.rental.damage': 'M13-form-damage',
    'fix.rental.asset': 'M13-form-asset',
    'fix.rental.kit': 'M13-form-kit',
    'fix.rental.deposit': 'M13-form-deposit',
    'fix.rental.turnaround': 'M13-form-turnaround'
  },
  'M13:__by_screen__': {
    'M13-fleet': 'M13-form-asset',
    'M13-kits': 'M13-form-kit',
    'M13-reservations': 'M13-form-reservation',
    'M13-agreements': 'M13-form-agreement',
    'M13-deposits': 'M13-form-deposit',
    'M13-condition': 'M13-form-condition',
    'M13-damage': 'M13-form-damage',
    'M13-turnaround': 'M13-form-turnaround'
  }
};

export const CREATE = {
  M13: { screen: 'M13-form-reservation', model: 'fix.rental.reservation', label: 'Reservation' }
};
