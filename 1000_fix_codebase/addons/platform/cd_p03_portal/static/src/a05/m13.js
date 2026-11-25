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
      { id: 'M13-kits', en: 'Kits & Accessories', bn: 'কিট ও এক্সেসরিজ', t: 'g' },
      { id: 'M13-redeploy', en: 'Fleet Redeployments', bn: 'শাখান্তর স্থানান্তর', t: 'g' },
      { id: 'M13-pm-plans', en: 'PM Plans', bn: 'রক্ষণাবেক্ষণ পরিকল্পনা', t: 'g' }
    ]},
    { en: 'Booking', screens: [
      { id: 'M13-reservations', en: 'Reservations', bn: 'বুকিং রেজিস্ট্রি', t: 'g' },
      { id: 'M13-agreements', en: 'Rental Agreements', bn: 'ভাড়া চুক্তিপত্র', t: 'g' },
      { id: 'M13-deposits', en: 'Security Deposits', bn: 'জামানত খতিয়ান', t: 'g' },
      { id: 'M13-extensions', en: 'Rental Extensions', bn: 'মেয়াদ বৃদ্ধি', t: 'g' },
      { id: 'M13-waiver-plans', en: 'Damage Waiver Plans', bn: 'ক্ষতি মওকুফ পরিকল্পনা', t: 'g' },
      { id: 'M13-exposure', en: 'Exposure Limits', bn: 'ঝুঁকি সীমা', t: 'g' },
      { id: 'M13-overrides', en: 'Exposure Overrides', bn: 'ঝুঁকি সীমা ব্যতিক্রম', t: 'g' }
    ]},
    { en: 'Lifecycle', screens: [
      { id: 'M13-condition', en: 'Condition Reports', bn: 'কন্ডিশন রিপোর্ট', t: 'g' },
      { id: 'M13-damage', en: 'Damage & Recovery', bn: 'ক্ষয়ক্ষতি ও পুনরুদ্ধার', t: 'g' },
      { id: 'M13-turnaround', en: 'Turnaround & Re-Grade', bn: 'টার্নঅ্যারাউন্ড ও রি-গ্রেড', t: 'g' },
      { id: 'M13-photos', en: 'Condition Photographs', bn: 'কন্ডিশন ছবি', t: 'g' },
      { id: 'M13-swaps', en: 'Unit Swaps', bn: 'ইউনিট বদল', t: 'g' },
      { id: 'M13-losses', en: 'Loss & Non-Return', bn: 'হারানো ও অফেরত', t: 'g' }
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
    'Rental SKU (M37)',
    /* capture pass 2 (2026-11-19): the records the spec names that had no model */
    'Fleet Redeployment',
    'Preventive Maintenance Plan',
    'Rental Exposure Limit',
    'Exposure Override Request',
    'Allocate a Fleet Unit',
    'Rental Extension',
    'Damage Waiver Plan',
    'Damage Waiver Election',
    'Condition Photograph',
    'Loss / Non-Return Case',
    'Unit Swap-Out'
  ],
  cross: ['M17 rental assets', 'M08 master agreements', 'M03 logistics', 'M15 rental pool stock'],
  /* Each page offers the capture of ITS function (capture audit 2026-11-13):
   * 3 prepares the agreement (not a second "+ New Reservation"), 4 takes the
   * deposit in its real tender, 6 records the return, 7 the in-rental fault,
   * 8 the turnaround checklist (a turnaround is opened by the return, never
   * typed: its old "+ New" was refused by the server). 9 is computed.
   * Capture pass 2 (2026-11-19) adds, as chips, the records the spec names
   * on each page that had no model: 1 redeployment, 2 allocation, exposure
   * limit and override, 3 extension, 4 damage waiver plan and election,
   * 5 photographs, 6 loss / non-return, 7 swap-out, 8 PM plan. */
  freg: { src: 78, sub: [
    ['1', 'Fleet Register', 9, { model: 'fix.rental.asset', cols: ['name', 'category', 'condition_grade', 'battery_health_pct', 'status'], screens: ['M13-fleet', 'M13-kits', 'M13-redeploy'], reports: ['Fleet Health & Retirement', 'Utilisation by Category'], forms: ['Fleet Serialized Asset Master', 'Rental Kit Bundle', 'Rental SKU (M37)', 'Fleet Redeployment'] }],
    ['2', 'Availability & Reservation', 12, { model: 'fix.rental.reservation', cols: ['name', 'customer_id', 'rental_asset_id', 'date_from', 'date_to'], screens: ['M13-availability', 'M13-reservations', 'M13-exposure', 'M13-overrides'], reports: ['Real-Time Availability'], forms: ['Reservation Cockpit', 'Allocate a Fleet Unit', 'Rental Exposure Limit', 'Exposure Override Request'] }],
    ['3', 'Agreements', 10, { model: 'fix.rental.reservation', cols: ['name', 'customer_id', 'contract_id', 'agreement_state', 'signed_at'], screens: ['M13-agreements', 'M13-extensions'], reports: [], forms: ['Rental Agreement (e-sign)', 'Rental Extension', 'Damage Waiver Election'], create: 'M13-form-agreement' }],
    ['4', 'Deposits & Waivers', 8, { model: 'fix.rental.deposit', cols: ['name', 'customer_id', 'kind', 'amount', 'method', 'reference'], screens: ['M13-deposits', 'M13-waiver-plans'], reports: ['Deposit Reconciliation'], forms: ['Security Deposit Collection', 'Damage Waiver Election', 'Damage Waiver Plan', 'Loss Waiver Request'], create: 'M13-form-deposit-take' }],
    ['5', 'Condition & Damage', 10, { model: 'fix.rental.condition', cols: ['name', 'reservation_id', 'report_type', 'grade', 'reported_on'], screens: ['M13-condition', 'M13-damage', 'M13-photos'], reports: ['Damage & Loss Rate'], forms: ['Condition Report', 'Condition Photograph', 'Damage Assessment & Recovery'] }],
    ['6', 'Returns & Recovery', 8, { model: 'fix.rental.damage', cols: ['reservation_id', 'category', 'cost', 'recovered_amount', 'settled'], screens: ['M13-damage', 'M13-losses'], reports: ['Late Return Analysis', 'Damage & Loss Rate'], forms: ['Rental Return', 'Damage Assessment & Recovery', 'Loss / Non-Return Case'], create: 'M13-form-return' }],
    ['7', 'In-Rental Support', 7, { model: 'fix.rental.reservation', cols: ['name', 'customer_id', 'rental_asset_id', 'date_to', 'service_order_id'], screens: ['M13-reservations', 'M13-swaps'], reports: ['Late Return Analysis'], forms: ['In-Rental Fault Report', 'Unit Swap-Out', 'Return Collection Booking'], create: 'M13-form-fault', domain: [['state', 'in', ['delivered', 'active']]] }],
    ['8', 'Turnaround & PM', 7, { model: 'fix.rental.turnaround', cols: ['name', 'rental_asset_id', 'returned_on', 'regrade', 'state'], screens: ['M13-turnaround', 'M13-pm-plans'], reports: ['Fleet Health & Retirement'], forms: ['Turnaround & Regrading', 'Preventive Maintenance Booking', 'Preventive Maintenance Plan'], create: 'M13-form-turnaround' }],
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

  /* ---- capture pass 2 (2026-11-19): the spec's missing registers ---- */
  'M13-redeploy': { kind: 'model_list', model: 'fix.rental.redeployment', stateField: 'state',
    cols: ['name', 'rental_asset_id', 'from_operating_unit_id', 'to_operating_unit_id', 'dispatched_on', 'received_on', 'state'],
    empty: 'No unit has been moved between branches. Use Redeploy a Unit to Another Branch.',
    actions: [
      { m: 'action_dispatch', l: 'Dispatch (M03 branch transfer)' },
      { m: 'action_receive', l: 'Confirm Receipt at New Branch' },
      { m: 'action_cancel', l: 'Cancel Redeployment' }
    ] },
  'M13-pm-plans': { kind: 'model_list', model: 'fix.rental.pm.plan',
    cols: ['name', 'rental_sku_id', 'category', 'interval_days', 'usage_rental_days', 'active'],
    empty: 'No preventive maintenance plan yet: units fall due only when a plan says when (every N days, or after N days on rent).' },
  'M13-exposure': { kind: 'model_list', model: 'fix.rental.exposure',
    cols: ['partner_id', 'risk_tier', 'exposure_limit', 'current_exposure', 'headroom', 'open_rental_count', 'reviewed_by', 'reviewed_on'],
    empty: 'No party has a rental exposure limit yet. Finance records one per party (FR-RNT-010); a party without one is limited only by its deposit.' },
  'M13-overrides': { kind: 'model_list', model: 'fix.rental.exposure.override', stateField: 'state',
    cols: ['name', 'reservation_id', 'customer_id', 'exposure_limit', 'exposure_after', 'excess', 'requested_by', 'state'],
    actions: [
      { m: 'action_approve', l: 'Approve Override' },
      { m: 'action_reject', l: 'Reject Override', ask: 'Why the override is refused', kwarg: 'reason' }
    ] },
  'M13-extensions': { kind: 'model_list', model: 'fix.rental.extension', stateField: 'state',
    cols: ['name', 'reservation_id', 'customer_id', 'old_date_to', 'new_date_to', 'charge_delta', 'availability_result', 'state'],
    actions: [
      { m: 'action_apply', l: 'Apply Extension (agreement v+1)' },
      { m: 'action_reject', l: 'Refuse Extension', ask: 'Why the extension is refused', kwarg: 'reason' }
    ] },
  'M13-waiver-plans': { kind: 'model_list', model: 'fix.rental.waiver.plan', stateField: 'state',
    cols: ['name', 'fee_pct', 'excess_amount', 'covers_accessories', 'covers_theft', 'legal_review_ref', 'election_count', 'state'],
    empty: 'No damage waiver is offered. Finance configures a plan; another person publishes it once Legal has reviewed it (spec Q-04).',
    actions: [
      { m: 'action_publish', l: 'Publish Plan' },
      { m: 'action_retire', l: 'Retire Plan' }
    ] },
  'M13-photos': { kind: 'model_list', model: 'fix.rental.condition.photo',
    cols: ['condition_id', 'reservation_id', 'report_type', 'view_code', 'captured_by', 'captured_at', 'sha256', 'integrity_ok'] },
  'M13-losses': { kind: 'model_list', model: 'fix.rental.loss', stateField: 'state',
    cols: ['name', 'reservation_id', 'customer_id', 'rental_asset_id', 'kind', 'escalation_stage', 'valuation', 'state'],
    actions: [
      { m: 'action_escalate', l: 'Escalate (notice > recovery > legal)' },
      { m: 'action_recover', l: 'Unit Recovered' },
      { m: 'action_request_writeoff', l: 'Request Write-Off Approval', ask: 'Justification for writing the unit off', kwarg: 'justification' },
      { m: 'action_write_off', l: 'Write Off (approved)' }
    ] },
  'M13-swaps': { kind: 'model_list', model: 'fix.rental.swap', stateField: 'state',
    cols: ['name', 'reservation_id', 'customer_id', 'out_asset_id', 'in_asset_id', 'sla_target', 'executed_at', 'sla_met', 'state'],
    actions: [
      { m: 'action_execute', l: 'Execute Swap' },
      { m: 'action_cancel', l: 'Cancel Swap' }
    ] },

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
          { name: 'lease_income_per_day', label: 'Lease Income per Day', readonly: true },
          { name: 'waiver_plan_id', label: 'Damage Waiver Elected', domain: [['state', '=', 'published']] },
          { name: 'waiver_fee', label: 'Damage Waiver Fee', readonly: true }
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
          { name: 'signature_ref', label: 'E-Signature Reference', readonly: true },
          { name: 'agreement_version', label: 'Agreement Version', readonly: true },
          { name: 'identity_verified', label: 'Identity Verified (M33)', readonly: true }
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
          { name: 'late_fee', label: 'Late Fee (computed)', readonly: true },
          { name: 'waiver_plan_id', label: 'Damage Waiver Elected', domain: [['state', '=', 'published']] },
          { name: 'waiver_fee', label: 'Damage Waiver Fee', readonly: true }
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
    /* capture pass 2: the hashed photographs (added with Add a Condition
     * Photograph) and, on a post-return report, the outbound ones beside
     * them (FR-RNT-023) */
    grids: [
      { field: 'photo_ids', tab: 'vault', title: 'Photographs of This Report', readonlyGrid: true,
        empty: 'No photograph yet. Handover, assessment and close need them: use Add a Condition Photograph.',
        fields: [
          { name: 'view_code', label: 'View' },
          { name: 'captured_by', label: 'Captured By' },
          { name: 'captured_at', label: 'Captured At' },
          { name: 'sha256', label: 'SHA-256' },
          { name: 'integrity_ok', label: 'Intact' }
        ] },
      { field: 'outbound_photo_ids', tab: 'vault', title: 'Outbound Photographs (side-by-side comparison)', readonlyGrid: true,
        empty: 'Shown on a post-return report: the photographs taken before delivery.',
        fields: [
          { name: 'view_code', label: 'View' },
          { name: 'captured_at', label: 'Captured At' },
          { name: 'sha256', label: 'SHA-256' }
        ] }
    ],
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
          { name: 'settled', label: 'Settlement Completed', readonly: true },
          /* capture pass 2: the elected damage waiver applies at assessment */
          { name: 'waiver_exclusion', label: 'Waiver Exclusion (BRU-RNT-10)' },
          { name: 'police_report_ref', label: 'Police Report (theft)' },
          { name: 'waiver_relief', label: 'Waived by the Damage Waiver', readonly: true }
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
  },

  /* ============ CAPTURE PASS 2 FORMS (2026-11-19) ============
   * The records the spec asks a person to enter that had no model at all:
   * redeployment, PM plan, exposure limit and override, allocation,
   * extension, damage waiver (plan and election), condition photographs,
   * loss / non-return and swap-out. */

  /* 1 Fleet Register: FR-RNT-031 */
  'M13-form-redeploy': {
    kind: 'model_form',
    model: 'fix.rental.redeployment',
    title: 'Fleet Redeployment',
    newLabel: 'Redeploy a Unit to Another Branch',
    back: 'M13-redeploy',
    status: { field: 'state', labels: { draft: 'Draft', in_transit: 'In Transit', received: 'Received', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'move', label: '1. Unit & Destination', bn: '১. ইউনিট ও গন্তব্য', icon: '🚚', badge: '4' },
      { id: 'custody', label: '2. Custody (M03)', bn: '২. হেফাজত', icon: '📦', badge: '5' },
      { id: 'vault', label: '3. Transfer Documents', bn: '৩. স্থানান্তর নথি', icon: '📁', badge: '1' }
    ],
    sections: [
      { tab: 'move', title: 'Which Unit Moves Where (FR-RNT-031)',
        note: 'Only an available unit with no open booking moves. Save, then press Dispatch on Fleet Redeployments; the receiving branch (another person) confirms receipt and the unit is re-homed there. Its rental and utilisation history stay on the unit.',
        fields: [
          { name: 'name', label: 'Redeployment Ref', readonly: true },
          { name: 'rental_asset_id', required: true, label: 'Fleet Unit', domain: [['status', '=', 'available']] },
          { name: 'from_operating_unit_id', label: 'From Branch', readonly: true },
          { name: 'to_operating_unit_id', required: true, label: 'To Branch' },
          { name: 'reason', required: true, type: 'text', label: 'Why (demand at the new branch / idle here)' }
        ] },
      { tab: 'custody', title: 'Branch Transfer & Custody',
        fields: [
          { name: 'state', label: 'Status', readonly: true },
          { name: 'consignment_id', label: 'Branch Transfer Consignment (M03)', readonly: true },
          { name: 'dispatched_by', label: 'Dispatched By', readonly: true },
          { name: 'dispatched_on', label: 'Dispatched On', readonly: true },
          { name: 'received_by', label: 'Received By', readonly: true },
          { name: 'received_on', label: 'Received On', readonly: true }
        ] },
      { tab: 'vault', title: 'Transfer Documents', note: 'Gate pass and the receiving branch acknowledgement.', fields: [] }
    ]
  },

  /* 8 Turnaround & PM: FR-RNT-028 / AUT-RNT-12 */
  'M13-form-pm-plan': {
    kind: 'model_form',
    model: 'fix.rental.pm.plan',
    title: 'Preventive Maintenance Plan',
    newLabel: 'Set a Preventive Maintenance Plan',
    back: 'M13-pm-plans',
    tabs: [
      { id: 'scope', label: '1. What It Covers', bn: '১. আওতা', icon: '🎯', badge: '3' },
      { id: 'when', label: '2. When It Falls Due', bn: '২. কখন', icon: '📅', badge: '2' },
      { id: 'work', label: '3. Maintenance Work', bn: '৩. রক্ষণাবেক্ষণ', icon: '🛠️', badge: '2' }
    ],
    sections: [
      { tab: 'scope', title: 'Plan Scope',
        note: 'A unit follows the plan of its rental SKU, else the plan of its fleet category. One active plan per SKU or category.',
        fields: [
          { name: 'name', required: true, label: 'Plan Name' },
          { name: 'rental_sku_id', label: 'Rental SKU' },
          { name: 'category', label: 'Or Fleet Category' }
        ] },
      { tab: 'when', title: 'Calendar or Usage (whichever first)',
        note: 'Every day the system takes an available unit whose maintenance has fallen due out of availability and opens its turnaround (BRU-RNT-21: it cannot be rented "just this once"). Completing the turnaround sets the next due date.',
        fields: [
          { name: 'interval_days', label: 'Every N Calendar Days' },
          { name: 'usage_rental_days', label: 'Or After N Days on Rent' }
        ] },
      { tab: 'work', title: 'Checklist',
        fields: [
          { name: 'checklist', type: 'text', label: 'Maintenance Checklist' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },

  /* 2 Availability & Reservation: FR-RNT-010 (P1) */
  'M13-form-exposure': {
    kind: 'model_form',
    model: 'fix.rental.exposure',
    title: 'Rental Exposure Limit',
    newLabel: 'Set a Party Exposure Limit',
    back: 'M13-exposure',
    tabs: [
      { id: 'limit', label: '1. Party & Limit', bn: '১. পক্ষ ও সীমা', icon: '🛡️', badge: '4' },
      { id: 'usage', label: '2. Open Exposure', bn: '২. চলমান ঝুঁকি', icon: '📊', badge: '5' },
      { id: 'vault', label: '3. Evidence', bn: '৩. প্রমাণ', icon: '📁', badge: '1' }
    ],
    sections: [
      { tab: 'limit', title: 'Exposure Limit (FR-RNT-010)',
        note: 'Open exposure = for each open rental, the unit book value less the deposit agreed on it. A booking above the limit is refused at reservation unless an exposure override is approved by someone other than whoever asked (BRU-RNT-05).',
        fields: [
          { name: 'partner_id', required: true, label: 'Party (company or person)' },
          { name: 'risk_tier', required: true, label: 'Risk Tier' },
          { name: 'exposure_limit', required: true, label: 'Exposure Limit (BDT)' },
          { name: 'basis', required: true, type: 'text', label: 'Basis: identity, deposit tier, rental history' }
        ] },
      { tab: 'usage', title: 'Live Position',
        fields: [
          { name: 'current_exposure', label: 'Open Exposure (BDT)', readonly: true },
          { name: 'headroom', label: 'Headroom (BDT)', readonly: true },
          { name: 'open_rental_count', label: 'Open Rentals', readonly: true },
          { name: 'reviewed_by', label: 'Last Set By', readonly: true },
          { name: 'reviewed_on', label: 'Last Set On', readonly: true }
        ] },
      { tab: 'vault', title: 'Evidence', note: 'Credit references, trade licence, corporate guarantee.', fields: [] }
    ]
  },

  /* 2 Availability & Reservation: BRU-RNT-05 */
  'M13-form-override': {
    kind: 'model_form',
    model: 'fix.rental.exposure.override',
    title: 'Exposure Override Request',
    newLabel: 'Request an Exposure Override',
    back: 'M13-overrides',
    status: { field: 'state', labels: { requested: 'Requested', approved: 'Approved', rejected: 'Rejected' } },
    tabs: [
      { id: 'request', label: '1. Request', bn: '১. অনুরোধ', icon: '📝', badge: '2' },
      { id: 'figures', label: '2. Figures & Decision', bn: '২. হিসাব ও সিদ্ধান্ত', icon: '⚖️', badge: '7' }
    ],
    sections: [
      { tab: 'request', title: 'Booking Above the Party Limit (BRU-RNT-05)',
        note: 'For a draft booking the reservation refused for exposure. The figures are computed by the system when you save; another person approves or rejects it on Exposure Overrides.',
        fields: [
          { name: 'name', label: 'Override Ref', readonly: true },
          { name: 'reservation_id', required: true, label: 'Booking', domain: [['state', '=', 'draft']] },
          { name: 'justification', required: true, type: 'text', label: 'Justification' }
        ] },
      { tab: 'figures', title: 'Exposure & Decision',
        fields: [
          { name: 'customer_id', label: 'Customer', readonly: true },
          { name: 'exposure_limit', label: 'Limit (BDT)', readonly: true },
          { name: 'exposure_after', label: 'Exposure With This Booking', readonly: true },
          { name: 'excess', label: 'Above the Limit', readonly: true },
          { name: 'state', label: 'Decision', readonly: true },
          { name: 'requested_by', label: 'Requested By', readonly: true },
          { name: 'decided_by', label: 'Decided By', readonly: true },
          { name: 'decision_note', label: 'Decision Note', readonly: true }
        ] }
    ]
  },

  /* 2 Availability & Reservation: FR-RNT-032 allocation at pick */
  'M13-form-allocate': {
    kind: 'model_form',
    model: 'fix.rental.reservation',
    title: 'Allocate a Fleet Unit',
    newLabel: 'Allocate a Unit to a Pool Booking',
    back: 'M13-reservations',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the confirmed booking that has no unit yet',
      note: 'Bookings reserved against a rental SKU (the pool) whose unit is chosen at pick.',
      search: 'Search booking or customer',
      choose: 'Allocate its unit',
      cols: ['name', 'customer_id', 'rental_sku_id', 'date_from', 'date_to', 'agreement_state'],
      domain: [['state', '=', 'reserved'], ['rental_asset_id', '=', false]],
      empty: 'No confirmed booking is waiting for a unit.'
    },
    sections: [
      { title: 'Step 2 of 2: The Unit (FR-RNT-032)',
        note: 'Choose an available unit of the SKU the customer booked; the server refuses another SKU, a unit booked for an overlapping window (with turnaround padding) or one not available. The unit is held for this booking. Allocate before the agreement is sent: the unit is one of its terms.',
        fields: [
          { name: 'name', label: 'Booking', readonly: true },
          { name: 'customer_id', label: 'Customer', readonly: true },
          { name: 'rental_sku_id', label: 'Rental SKU Booked', readonly: true },
          { name: 'date_from', label: 'From', readonly: true },
          { name: 'date_to', label: 'To', readonly: true },
          { name: 'rental_asset_id', required: true, label: 'Fleet Unit', domain: [['status', '=', 'available']] }
        ] }
    ]
  },

  /* 3 Agreements: FR-RNT-016 / FR-RNT-033 */
  'M13-form-extension': {
    kind: 'model_form',
    model: 'fix.rental.extension',
    title: 'Rental Extension',
    newLabel: 'Extend a Live Rental',
    back: 'M13-extensions',
    status: { field: 'state', labels: { requested: 'Requested', applied: 'Applied', rejected: 'Refused' } },
    tabs: [
      { id: 'request', label: '1. Extension Request', bn: '১. মেয়াদ বৃদ্ধির অনুরোধ', icon: '📅', badge: '3' },
      { id: 'check', label: '2. Availability & Re-Price', bn: '২. প্রাপ্যতা ও মূল্য', icon: '৳', badge: '5' },
      { id: 'approval', label: '3. Variation Record', bn: '৩. সংশোধন রেকর্ড', icon: '✍️', badge: '5' },
      { id: 'vault', label: '4. Customer Request', bn: '৪. গ্রাহকের অনুরোধ', icon: '📁', badge: '1' }
    ],
    sections: [
      { tab: 'request', title: 'New Return Date (FR-RNT-016)',
        note: 'For a rental out with the customer. Save to see whether the unit is free (turnaround padding included) and the re-priced charge on the rate ladder; another person applies it on Rental Extensions, which moves the agreement to its next version.',
        fields: [
          { name: 'name', label: 'Extension Ref', readonly: true },
          { name: 'reservation_id', required: true, label: 'Rental', domain: [['state', 'in', ['delivered', 'active']]] },
          { name: 'new_date_to', required: true, label: 'New Return Date' },
          { name: 'reason', required: true, type: 'text', label: 'Customer Request' }
        ] },
      { tab: 'check', title: 'Availability & Rate Ladder (FR-RNT-035)',
        fields: [
          { name: 'old_date_to', label: 'Due Back Before', readonly: true },
          { name: 'availability_result', label: 'Availability', readonly: true },
          { name: 'old_charge', label: 'Rental Charge Before', readonly: true },
          { name: 'new_charge', label: 'Rental Charge After', readonly: true },
          { name: 'charge_delta', label: 'Additional Charge', readonly: true }
        ] },
      { tab: 'approval', title: 'Agreement Variation (FR-RNT-033)',
        fields: [
          { name: 'state', label: 'Status', readonly: true },
          { name: 'requested_by', label: 'Requested By', readonly: true },
          { name: 'approved_by', label: 'Applied By', readonly: true },
          { name: 'applied_on', label: 'Applied On', readonly: true },
          { name: 'agreement_version', label: 'Agreement Version', readonly: true },
          { name: 'rejection_reason', label: 'Why Refused', readonly: true }
        ] },
      { tab: 'vault', title: 'Customer Request', note: 'The customer written or portal request.', fields: [] }
    ]
  },

  /* 4 Deposits & Waivers: FR-RNT-036 — the product */
  'M13-form-waiver-plan': {
    kind: 'model_form',
    model: 'fix.rental.waiver.plan',
    title: 'Damage Waiver Plan',
    newLabel: 'Configure a Damage Waiver Plan',
    back: 'M13-waiver-plans',
    status: { field: 'state', labels: { draft: 'Draft', published: 'Published', retired: 'Retired' } },
    tabs: [
      { id: 'price', label: '1. Fee & Excess', bn: '১. ফি ও অতিরিক্ত', icon: '৳', badge: '3' },
      { id: 'cover', label: '2. Cover & Exclusions', bn: '২. আওতা ও বর্জন', icon: '🛡️', badge: '3' },
      { id: 'legal', label: '3. Legal & Publication', bn: '৩. আইনি ও প্রকাশ', icon: '⚖️', badge: '5' },
      { id: 'vault', label: '4. Published Terms', bn: '৪. প্রকাশিত শর্ত', icon: '📁', badge: '1' }
    ],
    sections: [
      { tab: 'price', title: 'Waiver Fee and Excess (FR-RNT-036)',
        note: 'The fee is a % of the gross rental, charged as its own line on the rental invoice. On a covered damage the customer pays the excess and the rest is waived automatically at assessment.',
        fields: [
          { name: 'name', required: true, label: 'Plan Name' },
          { name: 'fee_pct', required: true, label: 'Fee (% of gross rental)' },
          { name: 'excess_amount', required: true, label: 'Excess per Incident (BDT)' }
        ] },
      { tab: 'cover', title: 'What Is Covered (BRU-RNT-10)',
        fields: [
          { name: 'covers_accessories', label: 'Covers Missing Accessories' },
          { name: 'covers_theft', label: 'Covers Theft (only with a police report)' },
          { name: 'exclusions', required: true, type: 'text', label: 'Published Exclusions' }
        ] },
      { tab: 'legal', title: 'Not Insurance: Legal Review (spec Q-04)',
        note: 'A plan is offered only once published, and published only with the Legal review reference, by someone other than whoever configured it. Published terms never change: retire the plan and configure a new one.',
        fields: [
          { name: 'legal_review_ref', label: 'Legal Review Reference' },
          { name: 'state', label: 'Status', readonly: true },
          { name: 'published_by', label: 'Published By', readonly: true },
          { name: 'published_on', label: 'Published On', readonly: true },
          { name: 'election_count', label: 'Agreements Electing It', readonly: true }
        ] },
      { tab: 'vault', title: 'Published Terms', note: 'Customer-facing waiver terms and the Legal opinion.', fields: [] }
    ]
  },

  /* 4 Deposits & Waivers: FR-RNT-036 — the customer's election */
  'M13-form-waiver-elect': {
    kind: 'model_form',
    model: 'fix.rental.reservation',
    title: 'Damage Waiver Election',
    newLabel: 'Record a Damage Waiver Election',
    back: 'M13-agreements',
    status: { field: 'agreement_state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the booking whose customer elects the waiver',
      note: 'Draft bookings whose agreement has not been sent: the election is a term of the agreement.',
      search: 'Search booking or customer',
      choose: 'Record the election',
      cols: ['name', 'customer_id', 'rental_asset_id', 'date_from', 'date_to', 'rental_charge'],
      domain: [['state', '=', 'draft'], ['agreement_state', 'in', ['draft', 'declined']]],
      empty: 'No draft booking is open to an election. The waiver is chosen before the agreement is sent.'
    },
    sections: [
      { title: 'Step 2 of 2: The Plan Elected (FR-RNT-036)',
        note: 'Only published plans are offered. The fee is added as its own line to the rental Mushak 6.3; damage assessed on this rental applies the plan excess automatically, except its exclusions (BRU-RNT-10). Leave empty to decline the waiver.',
        fields: [
          { name: 'name', label: 'Booking', readonly: true },
          { name: 'customer_id', label: 'Customer', readonly: true },
          { name: 'rental_charge', label: 'Gross Rental (BDT)', readonly: true },
          { name: 'waiver_plan_id', label: 'Damage Waiver Plan', domain: [['state', '=', 'published']] },
          { name: 'waiver_fee', label: 'Waiver Fee (BDT)', readonly: true }
        ] }
    ]
  },

  /* 5 Condition & Damage: FR-RNT-021/023, T-04, BRU-RNT-01/19 */
  'M13-form-photo': {
    kind: 'model_form',
    model: 'fix.rental.condition.photo',
    title: 'Condition Photograph',
    newLabel: 'Add a Condition Photograph',
    back: 'M13-photos',
    tabs: [
      { id: 'photo', label: '1. Photograph', bn: '১. ছবি', icon: '📸', badge: '5' },
      { id: 'evidence', label: '2. Evidence Integrity', bn: '২. প্রমাণের সততা', icon: '🔐', badge: '5' }
    ],
    sections: [
      { tab: 'photo', title: 'Photograph of the Unit (BRU-RNT-01)',
        note: 'For a condition report still at its stage: pre-delivery while the booking is draft or reserved, post-return while it is returned or under assessment. Handover, assessment and close each need at least the minimum number of photographs. A photograph is never replaced: add another and delete this one while the report is open.',
        fields: [
          { name: 'condition_id', required: true, label: 'Condition Report', domain: ['|', '&', ['report_type', '=', 'pre_delivery'], ['reservation_id.state', 'in', ['draft', 'reserved']], '&', ['report_type', '=', 'post_return'], ['reservation_id.state', 'in', ['returned', 'damage_assess']]] },
          { name: 'view_code', required: true, label: 'View' },
          { name: 'attachment_id', required: true, label: 'Photograph (upload)' },
          { name: 'device_ref', label: 'Capture Device' },
          { name: 'note', label: 'Note' }
        ] },
      { tab: 'evidence', title: 'Hashed at Capture, Filed in M24 (T-04)',
        fields: [
          { name: 'sha256', label: 'SHA-256 at Capture', readonly: true },
          { name: 'integrity_ok', label: 'Integrity Verified', readonly: true },
          { name: 'document_id', label: 'M24 Document', readonly: true },
          { name: 'captured_by', label: 'Captured By', readonly: true },
          { name: 'captured_at', label: 'Captured At', readonly: true }
        ] }
    ]
  },

  /* 6 Returns & Recovery: FR-RNT-025, BRU-RNT-11/22 */
  'M13-form-loss': {
    kind: 'model_form',
    model: 'fix.rental.loss',
    title: 'Loss / Non-Return Case',
    newLabel: 'Report a Lost or Unreturned Unit',
    back: 'M13-losses',
    status: { field: 'state', labels: { open: 'Open', recovered: 'Recovered', written_off: 'Written Off' } },
    tabs: [
      { id: 'case', label: '1. The Case', bn: '১. ঘটনা', icon: '🚨', badge: '5' },
      { id: 'value', label: '2. Valuation & Claim', bn: '২. মূল্যায়ন ও দাবি', icon: '৳', badge: '4' },
      { id: 'outcome', label: '3. Escalation & Outcome', bn: '৩. অগ্রগতি ও ফলাফল', icon: '⚖️', badge: '8' },
      { id: 'vault', label: '4. Evidence Vault', bn: '৪. প্রমাণ ভল্ট', icon: '📁', badge: '1' }
    ],
    sections: [
      { tab: 'case', title: 'What Happened (FR-RNT-025)',
        note: 'Escalate on Loss & Non-Return: formal notice, recovery, legal. A recovered unit stays Company property whatever was paid (BRU-RNT-11); record its return as usual.',
        fields: [
          { name: 'name', label: 'Case Ref', readonly: true },
          { name: 'reservation_id', required: true, label: 'Rental', domain: [['state', 'in', ['delivered', 'active']]] },
          { name: 'kind', required: true, label: 'Kind' },
          { name: 'circumstances', required: true, type: 'text', label: 'Circumstances' },
          { name: 'police_report_ref', label: 'Police Report (GD / FIR) No' }
        ] },
      { tab: 'value', title: 'Valuation & Insurance (BRU-RNT-22)',
        note: 'The write-off forfeits the deposit up to the valuation and invoices the rest through M20. It needs the claim reference or a documented decision not to claim, and the unit routed write-off approval (Request Write-Off Approval).',
        fields: [
          { name: 'valuation', label: 'Agreed Replacement Valuation (BDT)' },
          { name: 'claim_decision', label: 'Insurance' },
          { name: 'claim_ref', label: 'Claim Reference' },
          { name: 'no_claim_reason', type: 'text', label: 'Why No Claim' }
        ] },
      { tab: 'outcome', title: 'Escalation & Outcome',
        fields: [
          { name: 'escalation_stage', label: 'Escalation Stage', readonly: true },
          { name: 'state', label: 'Status', readonly: true },
          { name: 'reported_by', label: 'Reported By', readonly: true },
          { name: 'reported_at', label: 'Reported At', readonly: true },
          { name: 'recovered_on', label: 'Recovered On', readonly: true },
          { name: 'written_off_on', label: 'Written Off On', readonly: true },
          { name: 'forfeited_amount', label: 'Deposit Forfeited', readonly: true },
          { name: 'invoiced_amount', label: 'Invoiced (M20)', readonly: true }
        ] },
      { tab: 'vault', title: 'Evidence', note: 'Police report, formal notices, insurer correspondence.', fields: [] }
    ]
  },

  /* 7 In-Rental Support: FR-RNT-027 */
  'M13-form-swap': {
    kind: 'model_form',
    model: 'fix.rental.swap',
    title: 'Unit Swap-Out',
    newLabel: 'Swap a Faulty Unit on a Live Rental',
    back: 'M13-swaps',
    status: { field: 'state', labels: { open: 'Open', executed: 'Executed', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'fault', label: '1. Fault & Replacement', bn: '১. ত্রুটি ও প্রতিস্থাপন', icon: '🔁', badge: '4' },
      { id: 'condition', label: '2. Condition of Both Units', bn: '২. দুই ইউনিটের অবস্থা', icon: '🔍', badge: '4' },
      { id: 'sla', label: '3. SLA & Record', bn: '৩. এসএলএ ও রেকর্ড', icon: '⏱️', badge: '7' }
    ],
    sections: [
      { tab: 'fault', title: 'The Fault and the Replacement (FR-RNT-027)',
        note: 'The SLA clock starts when you save. Execute it on Unit Swaps once the replacement is with the customer: the rental moves to the replacement, the faulty unit goes to turnaround and a condition report is recorded for each.',
        fields: [
          { name: 'name', label: 'Swap Ref', readonly: true },
          { name: 'reservation_id', required: true, label: 'Rental', domain: [['state', 'in', ['delivered', 'active']]] },
          { name: 'fault', required: true, type: 'text', label: 'Fault' },
          { name: 'in_asset_id', required: true, label: 'Replacement Unit', domain: [['status', '=', 'available']] }
        ] },
      { tab: 'condition', title: 'Condition of Both Units',
        fields: [
          { name: 'out_grade', label: 'Faulty Unit: Grade on Receipt' },
          { name: 'out_notes', type: 'text', label: 'Faulty Unit: Condition' },
          { name: 'in_grade', label: 'Replacement: Grade at Dispatch' },
          { name: 'in_notes', type: 'text', label: 'Replacement: Condition' }
        ] },
      { tab: 'sla', title: 'SLA and the Record',
        fields: [
          { name: 'out_asset_id', label: 'Faulty Unit', readonly: true },
          { name: 'sla_hours', label: 'SLA (hours)', readonly: true },
          { name: 'sla_target', label: 'Due By', readonly: true },
          { name: 'executed_at', label: 'Executed At', readonly: true },
          { name: 'sla_met', label: 'SLA Met', readonly: true },
          { name: 'returned_report_id', label: 'Report: Faulty Unit', readonly: true },
          { name: 'replacement_report_id', label: 'Report: Replacement', readonly: true }
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
  'M13:Rental SKU (M37)': 'fix.rental.sku',
  'M13:Fleet Redeployment': 'fix.rental.redeployment',
  'M13:Preventive Maintenance Plan': 'fix.rental.pm.plan',
  'M13:Rental Exposure Limit': 'fix.rental.exposure',
  'M13:Exposure Override Request': 'fix.rental.exposure.override',
  'M13:Allocate a Fleet Unit': 'fix.rental.reservation',
  'M13:Rental Extension': 'fix.rental.extension',
  'M13:Damage Waiver Plan': 'fix.rental.waiver.plan',
  'M13:Damage Waiver Election': 'fix.rental.reservation',
  'M13:Condition Photograph': 'fix.rental.condition.photo',
  'M13:Loss / Non-Return Case': 'fix.rental.loss',
  'M13:Unit Swap-Out': 'fix.rental.swap'
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
  'M13:Fleet Redeployment': 'M13-form-redeploy',
  'M13:Preventive Maintenance Plan': 'M13-form-pm-plan',
  'M13:Rental Exposure Limit': 'M13-form-exposure',
  'M13:Exposure Override Request': 'M13-form-override',
  'M13:Allocate a Fleet Unit': 'M13-form-allocate',
  'M13:Rental Extension': 'M13-form-extension',
  'M13:Damage Waiver Plan': 'M13-form-waiver-plan',
  'M13:Damage Waiver Election': 'M13-form-waiver-elect',
  'M13:Condition Photograph': 'M13-form-photo',
  'M13:Loss / Non-Return Case': 'M13-form-loss',
  'M13:Unit Swap-Out': 'M13-form-swap',
  'M13:__by_model__': {
    'fix.rental.reservation': 'M13-form-reservation',
    'fix.rental.condition': 'M13-form-condition',
    'fix.rental.damage': 'M13-form-damage',
    'fix.rental.asset': 'M13-form-asset',
    'fix.rental.kit': 'M13-form-kit',
    'fix.rental.deposit': 'M13-form-deposit',
    'fix.rental.turnaround': 'M13-form-turnaround',
    'fix.rental.redeployment': 'M13-form-redeploy',
    'fix.rental.pm.plan': 'M13-form-pm-plan',
    'fix.rental.exposure': 'M13-form-exposure',
    'fix.rental.exposure.override': 'M13-form-override',
    'fix.rental.extension': 'M13-form-extension',
    'fix.rental.waiver.plan': 'M13-form-waiver-plan',
    'fix.rental.condition.photo': 'M13-form-photo',
    'fix.rental.loss': 'M13-form-loss',
    'fix.rental.swap': 'M13-form-swap'
  },
  'M13:__by_screen__': {
    'M13-fleet': 'M13-form-asset',
    'M13-kits': 'M13-form-kit',
    'M13-reservations': 'M13-form-reservation',
    'M13-agreements': 'M13-form-agreement',
    'M13-deposits': 'M13-form-deposit',
    'M13-condition': 'M13-form-condition',
    'M13-damage': 'M13-form-damage',
    'M13-turnaround': 'M13-form-turnaround',
    'M13-redeploy': 'M13-form-redeploy',
    'M13-pm-plans': 'M13-form-pm-plan',
    'M13-exposure': 'M13-form-exposure',
    'M13-overrides': 'M13-form-override',
    'M13-extensions': 'M13-form-extension',
    'M13-waiver-plans': 'M13-form-waiver-plan',
    'M13-photos': 'M13-form-photo',
    'M13-losses': 'M13-form-loss',
    'M13-swaps': 'M13-form-swap'
  }
};

export const CREATE = {
  M13: { screen: 'M13-form-reservation', model: 'fix.rental.reservation', label: 'Reservation' }
};
