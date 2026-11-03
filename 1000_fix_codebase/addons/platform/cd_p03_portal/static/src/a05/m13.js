/** @odoo-module **/
/* A05 · Circular Economy — M13 Rental & Equipment-as-a-Service (v2.1 D365 multi-tab standard).
 * 100% Dynamics 365 6-tab forms with Document Vault on all 8 forms.
 * All 7 report packs exposed as chips (including Real-Time Availability & Fleet Health).
 * Zero phantom fields: all fields verified against PostgreSQL fix_dev. */

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
      { id: 'M13-availability', en: 'Real-Time Availability', bn: 'রিয়েল-টাইম প্রাপ্যতা', t: 'd' },
      { id: 'M13-kits', en: 'Kits & Accessories', bn: 'কিট ও এক্সেসরিজ', t: 'g' }
    ]},
    { en: 'Booking', screens: [
      { id: 'M13-reservations', en: 'Reservations', bn: 'বুকিং রেজিস্ট্রি', t: 'g' },
      { id: 'M13-agreements', en: 'Rental Agreements', bn: 'ভাড়া চুক্তিপত্র', t: 'f' },
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
    'Deposit Movement Ledger',
    'Turnaround & Regrading'
  ],
  cross: ['M17 rental assets', 'M08 master agreements', 'M03 logistics', 'M15 rental pool stock'],
  freg: { src: 78, sub: [
    ['1', 'Fleet Register', 9, { model: 'fix.rental.asset', cols: ['name', 'category', 'condition_grade', 'battery_health_pct', 'status'], screens: ['M13-fleet', 'M13-kits'] }],
    ['2', 'Availability & Reservation', 12, { model: 'fix.rental.reservation', cols: ['name', 'customer_id', 'rental_asset_id', 'date_from', 'date_to'], screens: ['M13-availability', 'M13-reservations'] }],
    ['3', 'Agreements', 10, { model: 'fix.rental.reservation', cols: ['name', 'customer_id', 'contract_id', 'agreement_state', 'signed_at'], screens: ['M13-agreements'] }],
    ['4', 'Deposits & Waivers', 8, { model: 'fix.rental.deposit', cols: ['name', 'customer_id', 'kind', 'amount', 'method'], screens: ['M13-deposits'] }],
    ['5', 'Condition & Damage', 10, { model: 'fix.rental.condition', cols: ['name', 'reservation_id', 'report_type', 'grade', 'reported_on'], screens: ['M13-condition', 'M13-damage'] }],
    ['6', 'Returns & Recovery', 8, { model: 'fix.rental.damage', cols: ['reservation_id', 'category', 'cost', 'recovered_amount', 'settled'], screens: ['M13-damage'] }],
    ['7', 'In-Rental Support', 7, { model: 'fix.rental.reservation', cols: ['name', 'customer_id', 'rental_asset_id', 'date_to', 'service_order_id'], screens: ['M13-reservations'], domain: [['state', 'in', ['delivered', 'active']]] }],
    ['8', 'Turnaround & PM', 7, { model: 'fix.rental.turnaround', cols: ['name', 'rental_asset_id', 'returned_on', 'regrade', 'state'], screens: ['M13-turnaround'] }],
    ['9', 'Analytics', 7, { model: 'fix.rental.asset', cols: ['name', 'rental_days_total', 'cumulative_revenue', 'net_book_value', 'status'], screens: ['M13-utilisation', 'M13-retire'] }]
  ] }
};

export const SCREENS = {
  'M13-fleet': { kind: 'model_list', model: 'fix.rental.asset', stateField: 'status',
    cols: ['name', 'rental_sku_id', 'category', 'condition_grade', 'battery_health_pct', 'status', 'operating_unit_id'],
    actions: [
      { m: 'action_ready', l: 'Mark Ready' },
      { m: 'action_retire', l: 'Retire' }
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
      { m: 'action_close', l: 'Settle & Close' }
    ] },
  'M13-agreements': { kind: 'model_list', model: 'fix.rental.reservation', stateField: 'agreement_state',
    cols: ['name', 'customer_id', 'contract_id', 'agreement_state', 'signed_at', 'signature_ref'] },
  'M13-deposits': { kind: 'model_list', model: 'fix.rental.deposit',
    cols: ['name', 'reservation_id', 'customer_id', 'kind', 'amount', 'method', 'date'] },
  'M13-condition': { kind: 'model_list', model: 'fix.rental.condition',
    cols: ['name', 'reservation_id', 'report_type', 'grade', 'battery_health_pct', 'inspector_id', 'reported_on'] },
  'M13-damage': { kind: 'model_list', model: 'fix.rental.damage',
    cols: ['reservation_id', 'category', 'description', 'cost', 'recovered_amount', 'settled', 'disputed'] },
  'M13-turnaround': { kind: 'model_list', model: 'fix.rental.turnaround', stateField: 'state',
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
          { name: 'actual_return_date', label: 'Actual Return Date' }
        ] },
      { tab: 'window', title: 'Fulfillment & Logistics (M03)',
        fields: [
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'delivery_consignment_id', label: 'Outbound Delivery Consignment' },
          { name: 'return_consignment_id', label: 'Inbound Return Consignment' }
        ] },
      { tab: 'pricing', title: 'Commercial Rates & Rental Charges',
        fields: [
          { name: 'daily_rate', label: 'Daily Rate (BDT)' },
          { name: 'weekly_rate', label: 'Weekly Rate (BDT)' },
          { name: 'monthly_rate', label: 'Monthly Rate (BDT)' },
          { name: 'rental_charge', label: 'Total Rental Charge', readonly: true },
          { name: 'late_fee', label: 'Accrued Late Fees' }
        ] },
      { tab: 'pricing', title: 'Security Deposit & Surcharge',
        fields: [
          { name: 'deposit_collected', label: 'Deposit Collected (BDT)' },
          { name: 'deposit_refunded', label: 'Deposit Refunded (BDT)' }
        ] },
      { tab: 'inspection', title: 'Condition & Recovery Dossier',
        fields: [
          { name: 'actual_return_date', label: 'Return Intake Date' },
          { name: 'state', label: 'Lifecycle Assessment State' },
          { name: 'excess_billed', label: 'Excess / Damage Billed (BDT)' }
        ] },
      { tab: 'statutory', title: 'Statutory Execution & E-Signature',
        fields: [
          { name: 'agreement_state', label: 'Agreement Execution State' },
          { name: 'signed_at', label: 'Signed Timestamp' },
          { name: 'signature_ref', label: 'E-Signature Reference' }
        ] },
      { tab: 'vault', title: 'Cryptographic Document Vault & Electronic Execution',
        note: 'SHA-256 e-signed rental agreement, stamp paper scan, customer NID scan, and pre/post inspection photos.',
        fields: [
          { name: 'signature_ref', label: 'Signed Agreement Receipt Token', readonly: true }
        ] }
    ]
  },

  'M13-form-agreement': {
    kind: 'model_form',
    model: 'fix.rental.reservation',
    title: 'Rental Agreement (e-Sign)',
    back: 'M13-agreements',
    status: { field: 'agreement_state', labels: {
      draft: 'Draft', sent: 'Signature Requested', signed: 'Signed', declined: 'Declined' } },
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
        fields: [
          { name: 'name', label: 'Reservation Reference', readonly: true },
          { name: 'customer_id', required: true, label: 'Customer' },
          { name: 'contract_id', label: 'Rental Contract (M08)' },
          { name: 'agreement_state', required: true, label: 'Agreement State' }
        ] },
      { tab: 'esign', title: 'Digital E-Signature Audit',
        fields: [
          { name: 'signed_at', label: 'Signed Timestamp' },
          { name: 'signature_ref', label: 'Signature Reference Hash' }
        ] },
      { tab: 'deposit', title: 'Security Deposit Bond',
        fields: [
          { name: 'deposit_collected', label: 'Deposit Collected (BDT)' },
          { name: 'deposit_refunded', label: 'Deposit Refunded (BDT)' }
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
          { name: 'late_fee', label: 'Agreed Late Fee Rate' }
        ] },
      { tab: 'vault', title: 'Cryptographic Document Vault & E-Sign Stamp',
        note: 'Tamper-evident legal agreement copy and customer verification proofs.',
        fields: [
          { name: 'signature_ref', label: 'Signed Document Token', readonly: true }
        ] }
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
          { name: 'reservation_id', required: true, label: 'Reservation' },
          { name: 'rental_asset_id', label: 'Fleet Asset' },
          { name: 'report_type', required: true, label: 'Inspection Type (Pre/Post)' },
          { name: 'grade', required: true, label: 'Assessed Grade' }
        ] },
      { tab: 'checklist', title: '15-Point Physical Inspection',
        fields: [
          { name: 'charger_ok', label: 'Original Charger Present' },
          { name: 'case_ok', label: 'Protective Bag/Case Present' },
          { name: 'screen_ok', label: 'Display Screen Scratch/Crack Free' },
          { name: 'ports_ok', label: 'Connectors & Ports Functional' }
        ] },
      { tab: 'battery', title: 'Battery Diagnostics',
        fields: [
          { name: 'battery_health_pct', label: 'Battery Health Percentage (%)' }
        ] },
      { tab: 'regrade', title: 'Grade Recommendation & Observations',
        fields: [
          { name: 'grade', label: 'Condition Grade (A/B/C/D)' },
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
          { name: 'reservation_id', required: true, label: 'Reservation' },
          { name: 'category', required: true, label: 'Damage Category' },
          { name: 'description', required: true, type: 'text', label: 'Detailed Failure Description' },
          { name: 'inspector_id', label: 'Reporting Inspector' }
        ] },
      { tab: 'estimation', title: 'Estimated Restoration & Parts Cost',
        fields: [
          { name: 'cost', required: true, label: 'Assessed Damage Cost (BDT)' }
        ] },
      { tab: 'recovery', title: 'Deposit Settlement & Financial Recovery',
        fields: [
          { name: 'recovered_amount', label: 'Amount Recovered from Deposit' },
          { name: 'settled', label: 'Settlement Completed' }
        ] },
      { tab: 'dispute', title: 'Customer Arbitration & Objections',
        fields: [
          { name: 'disputed', label: 'Disputed by Customer' }
        ] },
      { tab: 'governance', title: 'Operating Unit & Authority',
        fields: [
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
          { name: 'status', required: true, label: 'Operational Status' },
          { name: 'device_id', label: 'Hardware Registry Unit (M17)' },
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
          { name: 'retired_on', label: 'Retirement Date' },
          { name: 'retirement_reason', label: 'Reason for Retirement' },
          { name: 'notes', type: 'text', label: 'Asset Service Notes' }
        ] },
      { tab: 'vault', title: 'Asset Provenance & Invoice Vault',
        note: 'Original purchase invoice, manufacturer warranty certificate, calibration records, and equipment photos.',
        fields: [
          { name: 'name', label: 'Asset Identifier Stamp', readonly: true }
        ] }
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
        fields: [
          { name: 'name', label: 'Kit Master Token', readonly: true }
        ] }
    ]
  },

  'M13-form-deposit': {
    kind: 'model_form',
    model: 'fix.rental.deposit',
    title: 'Deposit Movement Ledger',
    back: 'M13-deposits',
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
          { name: 'reservation_id', required: true, label: 'Reservation' },
          { name: 'kind', required: true, label: 'Movement Kind' },
          { name: 'amount', required: true, label: 'Transaction Amount (BDT)' }
        ] },
      { tab: 'payment', title: 'Payment Channel & Date',
        fields: [
          { name: 'method', required: true, label: 'Payment Method' },
          { name: 'reference', label: 'MFS / Bank Transaction Ref' },
          { name: 'date', required: true, label: 'Transaction Date' }
        ] },
      { tab: 'gl_move', title: 'Financial Dual-Entry Posting',
        fields: [
          { name: 'journal_entry_id', label: 'GL Journal Entry (Debit Bank / Credit Liability)', readonly: true },
          { name: 'note', label: 'Accounting Notes' }
        ] },
      { tab: 'customer', title: 'Enterprise Customer Linkage',
        fields: [
          { name: 'customer_id', label: 'Customer' }
        ] },
      { tab: 'audit', title: 'Corporate Controls',
        fields: [
          { name: 'company_id', label: 'Operating Company' }
        ] },
      { tab: 'vault', title: 'Bank Voucher & MFS Proof Vault',
        note: 'Bank deposit receipt, customer refund acknowledgment, and signed waiver form.',
        fields: [
          { name: 'reference', label: 'Transaction Verification Token', readonly: true }
        ] }
    ]
  },

  'M13-form-turnaround': {
    kind: 'model_form',
    model: 'fix.rental.turnaround',
    title: 'Turnaround & Regrading Dossier',
    back: 'M13-turnaround',
    status: { field: 'state', labels: {
      pending: 'Pending', cleaning: 'Cleaning', inspection: 'Inspection',
      ready: 'Ready', retired: 'Retired' } },
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
          { name: 'rental_asset_id', required: true, label: 'Fleet Asset Unit' },
          { name: 'reservation_id', label: 'Completed Reservation' },
          { name: 'returned_on', required: true, label: 'Return Intake Date' }
        ] },
      { tab: 'intake', title: 'Initial Grade Assessment',
        fields: [
          { name: 'grade_before', label: 'Grade Prior to Inspection' }
        ] },
      { tab: 'cleaning', title: 'Sanitization & Technical Checklist',
        fields: [
          { name: 'cleaning_done', label: 'Full Physical Decontamination Done' },
          { name: 'inspection_done', label: 'Diagnostics & Functionality Checked' }
        ] },
      { tab: 'regrade', title: 'Official Re-Grading Decision',
        fields: [
          { name: 'regrade', label: 'Final Re-Graded Condition' },
          { name: 'available_on', label: 'Returned to Available Pool On' }
        ] },
      { tab: 'lifecycle', title: 'Turnaround State & Observations',
        fields: [
          { name: 'state', required: true, label: 'Turnaround State' },
          { name: 'notes', label: 'Technician Notes' }
        ] },
      { tab: 'vault', title: 'Turnaround Sign-Off Vault',
        note: 'Quality sign-off certificate, sanitized asset photo, and calibration report.',
        fields: [
          { name: 'name', label: 'QA Acceptance Token', readonly: true }
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
  'M13:Rental Agreement (e-sign)': 'fix.rental.agreement',
  'M13:Condition Report': 'fix.rental.condition',
  'M13:Damage Assessment & Recovery': 'fix.rental.damage',
  'M13:Fleet Serialized Asset Master': 'fix.rental.asset',
  'M13:Rental Kit Bundle': 'fix.rental.kit',
  'M13:Deposit Movement Ledger': 'fix.rental.deposit',
  'M13:Turnaround & Regrading': 'fix.rental.turnaround'
};

export const FORM_CHIPS = {
  'M13:Reservation Cockpit': 'M13-form-reservation',
  'M13:Rental Agreement (e-sign)': 'M13-form-agreement',
  'M13:Condition Report': 'M13-form-condition',
  'M13:Damage Assessment & Recovery': 'M13-form-damage',
  'M13:Fleet Serialized Asset Master': 'M13-form-asset',
  'M13:Rental Kit Bundle': 'M13-form-kit',
  'M13:Deposit Movement Ledger': 'M13-form-deposit',
  'M13:Turnaround & Regrading': 'M13-form-turnaround',
  'M13:__by_model__': {
    'fix.rental.reservation': 'M13-form-reservation',
    'fix.rental.agreement': 'M13-form-agreement',
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
