/** @odoo-module **/
/* A04 · Commercial & Revenue — M08 Contract Lifecycle (AMC) (v2 rebuild).
 * Registry-faithful: 5 groups / 16 screens / 6 reports / 5 forms / freg 108
 * (capture passes 13 and 18 Nov 2026 added the spec's registers and forms).
 * Contracts, entitlements and PM visits are real; amendments, renewals and
 * terminations are new. Contract P&L is value-after-SLA-credits (no invented
 * cost); renewal risk is a stated derivation, not a model score. */

export const MODULE = {
  area: 'A04', code: 'M08', en: 'Contract Lifecycle (AMC)', title: 'M08 · Contract Lifecycle (AMC)',
  bn: 'চুক্তি লাইফসাইকেল', icon: '📝',
  desc: 'Contracts in the five product families the engine carries (AMC, RAMC, managed services, rental, marketplace), coverage and entitlement consumption, SLA credits, PM schedules, amendments, renewals and churn, pricing and profitability.',
  kpis: [
    { l: 'Active Contracts', m: 'active_contracts' },
    { l: 'Contract Base Value', m: 'contract_base_value', prefix: '৳ ' },
    { l: 'Renewal Rate', m: 'renewal_rate', suffix: '%' },
    { l: 'Neg-Margin Contracts', m: 'neg_margin_contracts' },
    { l: 'Entitlement Utilisation', m: 'entitlement_utilisation', suffix: '%' },
    { l: 'PM Visits Due (7d)', m: 'pm_visits_due_7d' },
    { l: 'Expiring (90d)', m: 'expiring_90d' },
    { l: 'Expiring Value (90d)', m: 'expiring_90d_value', prefix: '৳ ' }
  ],
  groups: [
    { en: 'Contract Register', screens: [
      { id: 'M08-contracts', en: 'Contracts', bn: 'চুক্তি', t: 'g' },
      { id: 'M08-record', en: 'Contract Record', bn: 'চুক্তি রেকর্ড', t: 'f' },
      { id: 'M08-families', en: 'Contract Product Families', bn: 'পণ্য পরিবার', t: 'r' },
      { id: 'M08-master', en: 'Master Agreements', bn: 'মাস্টার চুক্তি', t: 'g' },
      { id: 'M08-parties', en: 'Parties & Signatories', bn: 'পক্ষ ও স্বাক্ষরকারী', t: 'g' }
    ]},
    { en: 'Coverage & Entitlement', screens: [
      { id: 'M08-scope', en: 'Covered Assets & Sites', bn: 'কভারেজ', t: 'r' },
      { id: 'M08-entitle', en: 'Entitlement & Consumption', bn: 'এনটাইটেলমেন্ট', t: 'g' },
      { id: 'M08-balance', en: 'Balances, Carry-Over, Top-Up', bn: 'ব্যালেন্স', t: 'r' },
      { id: 'M08-exclusions', en: 'Coverage Exclusions', bn: 'কভারেজ বহির্ভূত', t: 'g' },
      { id: 'M08-coverage-rules', en: 'Coverage Rules', bn: 'কভারেজ নিয়ম', t: 'g' },
      { id: 'M08-topups', en: 'Entitlement Top-Ups', bn: 'এনটাইটেলমেন্ট টপ-আপ', t: 'g' },
      { id: 'M08-ledger', en: 'Entitlement Ledger', bn: 'এনটাইটেলমেন্ট খতিয়ান', t: 'g' }
    ]},
    { en: 'Service Commitments', screens: [
      { id: 'M08-sla', en: 'Contract SLA & Credits', bn: 'SLA ক্রেডিট', t: 'r' },
      { id: 'M08-pm', en: 'PM & Calibration Schedules', bn: 'পিএম শিডিউল', t: 'g' },
      { id: 'M08-auto-work', en: 'Contract-Driven Work', bn: 'চুক্তি-চালিত কাজ', t: 'r' },
      { id: 'M08-obligations', en: 'Obligation Register', bn: 'দায়বদ্ধতা নিবন্ধন', t: 'g' },
      { id: 'M08-credit-schemes', en: 'Service Credit Schemes', bn: 'সার্ভিস ক্রেডিট স্কিম', t: 'g' },
      { id: 'M08-pm-plans', en: 'PM & Calibration Plans', bn: 'পিএম ও ক্যালিব্রেশন পরিকল্পনা', t: 'g' }
    ]},
    { en: 'Change & Renewal', screens: [
      { id: 'M08-amend', en: 'Amendments & Variations', bn: 'সংশোধনী', t: 'g' },
      { id: 'M08-renewals', en: 'Renewals & Auto-Renew', bn: 'নবায়ন', t: 'g' },
      { id: 'M08-termination', en: 'Suspension / Termination', bn: 'স্থগিত / বাতিল', t: 'g' },
      { id: 'M08-suspensions', en: 'Suspension Windows (not billed)', bn: 'স্থগিতকাল', t: 'g' },
      { id: 'M08-stampduty', en: 'Stamp Duty Schedule I', bn: 'স্ট্যাম্প ডিউটি তালিকা', t: 'g' },
      { id: 'M08-churn', en: 'Churn & Win-Back', bn: 'চার্ন ও উইন-ব্যাক', t: 'r' },
      { id: 'M08-disputes', en: 'Disputes & Legal Hold', bn: 'বিরোধ ও আইনি স্থগিতাদেশ', t: 'g' }
    ]},
    { en: 'Financials', screens: [
      { id: 'M08-pricing', en: 'Contract Pricing Link', bn: 'মূল্য সংযোগ', t: 'r' },
      { id: 'M08-profit', en: 'Profitability & Alerts', bn: 'লাভজনকতা', t: 'r' }
    ]}
  ],
  reports: ['Contract Base Movement', 'Entitlement Consumption by Client', 'SLA Credit Register', 'PM Compliance Report', 'Renewal Pipeline & Risk', 'Contract P&L'],
  /* M08 capture audit 2026-11-13: 'Asset Attach/Detach' opened the
   * ENTITLEMENT form, so no form anywhere set a contract's covered assets or
   * its SLAs - and activation generates PM visits only for covered assets.
   * It now opens the cover form; the entitlement form is its own chip. The
   * steps a person performs on an existing contract (submit, Legal review,
   * price revision, signature and stamp duty) are forms of their own; the
   * SLA credit and the signature envelope are mastered by M05 and M24 and
   * open THEIR forms. */
  forms: ['Contract (5 families)', 'Amendment', 'Asset Attach/Detach', 'Renewal Quote', 'PM Schedule',
    'Entitlement', 'Submit for Value Approval', 'Legal Review', 'SLA Credit', 'Suspension / Termination Notice',
    'Price Revision', 'Signature & Stamp Duty', 'Signature Envelope', 'Stamp Duty Rate',
    'Contract Party', 'Coverage Exclusion', 'Contract Obligation', 'Lost Renewal',
    /* capture pass 2 (2026-11-18) */
    'Coverage Rule', 'Entitlement Top-Up', 'Service Credit Scheme', 'PM Visit',
    'Contract Dispute', 'Reinstatement', 'Wet-Ink Signature Verification'],
  cross: ['M05 MSP', 'M01 Service Orders', 'M20 AR', 'M37 Catalogue'],
  freg: { src: 108, sub: [
    ['1', 'Template-Driven Creation', 12, { model: 'fix.contract', cols: ['name', 'customer_id', 'family', 'state', 'date_start', 'date_end', 'annual_value', 'owner_id', 'parent_contract_id'], screens: ['M08-contracts', 'M08-master'], reports: [], forms: ['Contract (5 families)'] }],
    ['2', 'Parties & Approval', 8, { model: 'fix.contract', cols: ['name', 'customer_id', 'family', 'state', 'approval_state', 'legal_review_required', 'annual_value'], screens: ['M08-contracts', 'M08-master', 'M08-parties'], reports: [], forms: ['Submit for Value Approval', 'Legal Review', 'Contract Party'], create: 'M08-form-submit' }],
    ['3', 'Coverage Scope', 10, { model: 'fix.contract.entitlement', cols: ['contract_id', 'device_id', 'entitlement_type', 'quantity_included', 'quantity_remaining'], screens: ['M08-scope', 'M08-coverage-rules', 'M08-entitle', 'M08-exclusions'], reports: ['Entitlement Consumption by Client'], forms: ['Asset Attach/Detach', 'Coverage Rule', 'Entitlement', 'Coverage Exclusion'], create: 'M08-form-coverage' }],
    ['4', 'Entitlement Engine', 14, { model: 'fix.contract.entitlement', cols: ['contract_id', 'entitlement_type', 'quantity_included', 'quantity_consumed', 'quantity_remaining'], screens: ['M08-entitle', 'M08-topups', 'M08-ledger', 'M08-balance'], reports: ['Entitlement Consumption by Client'], forms: ['Entitlement Top-Up', 'Entitlement'], create: 'M08-form-topup' }],
    ['5', 'SLA & Service Credits', 10, { model: 'fix.contract.credit.scheme', cols: ['contract_id', 'breach_type', 'priority', 'credit_basis', 'credit_value', 'cumulative_rule', 'cap_pct'], screens: ['M08-credit-schemes', 'M08-sla', 'M08-rpt-sla'], reports: ['SLA Credit Register'], forms: ['Service Credit Scheme', 'SLA Credit'], create: 'M08-form-creditscheme' }],
    ['6', 'PM Schedules', 9, { model: 'fix.contract.pm.plan', cols: ['name', 'contract_id', 'schedule_type', 'device_id', 'interval_months', 'lead_days', 'visit_count'], screens: ['M08-pm-plans', 'M08-pm', 'M08-rpt-pm'], reports: ['PM Compliance Report'], forms: ['PM Schedule', 'PM Visit'], create: 'M08-form-pmplan' }],
    ['7', 'Amendments', 8, { model: 'fix.contract.amendment', cols: ['contract_id', 'state'], screens: ['M08-amend'], reports: [], forms: ['Amendment'] }],
    ['8', 'Renewal Governance', 9, { model: 'fix.contract.renewal', cols: ['contract_id', 'state'], screens: ['M08-renewals', 'M08-rpt-renew'], reports: ['Renewal Pipeline & Risk'], forms: ['Renewal Quote'] }],
    ['9', 'Churn & Win-Back', 6, { model: 'fix.contract.termination', cols: ['contract_id', 'state'], screens: ['M08-termination', 'M08-disputes', 'M08-churn', 'M08-renewals'], reports: ['Contract Base Movement', 'Renewal Pipeline & Risk'], forms: ['Suspension / Termination Notice', 'Contract Dispute', 'Reinstatement', 'Lost Renewal'] }],
    ['10', 'Pricing & Profitability', 10, { model: 'fix.contract', cols: ['name', 'customer_id', 'annual_value', 'total_delivery_cost', 'contract_margin_pct'], screens: ['M08-pricing', 'M08-profit', 'M08-rpt-pnl', 'M08-contracts'], reports: ['Contract P&L'], forms: ['Price Revision'], create: 'M08-form-price' }],
    ['11', 'Documents & Signature', 7, { model: 'fix.contract', cols: ['name', 'state', 'signature_method', 'esignature_envelope_id', 'wet_signed_on', 'has_signed_contract_doc', 'stamp_duty_cert_no'], screens: ['M08-rpt-base', 'M08-contracts', 'M08-stampduty'], reports: ['Contract Base Movement'], forms: ['Signature & Stamp Duty', 'Wet-Ink Signature Verification', 'Signature Envelope', 'Stamp Duty Rate'], create: 'M08-form-signature' }],
    ['12', 'Obligation Calendar', 5, { model: 'fix.contract.obligation', cols: ['name', 'contract_id', 'obligation_type', 'due_date', 'owner_id', 'state'], screens: ['M08-obligations', 'M08-pm', 'M08-auto-work'], reports: ['PM Compliance Report'], forms: ['Contract Obligation', 'PM Schedule'] }]
  ] }
};

export const SCREENS = {
  // A04 build (2026-11-04) C3: the contract lifecycle runs by its actions.
  // The value is approved from the DOFA holder's M63 inbox (never here);
  // Legal and Finance decide only what they did not raise.
  'M08-contracts': { kind: 'model_list', model: 'fix.contract', stateField: 'state',
    cols: ['name', 'customer_id', 'family', 'date_start', 'date_end', 'annual_value', 'term_value', 'billing_frequency', 'auto_renew', 'owner_id', 'signature_method', 'in_dispute', 'state', 'approval_state'],
    actions: [
      /* A04 ERP audit M08-F20: the contract's professional document */
      { m: 'p03_print_document', print: 'a4', l: 'Print Contract' },
      { m: 'action_request_approval', l: 'Submit for Value Approval (DOFA)', states: ['draft'], ask: 'Business justification (mandatory from Tier 2)', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Approval Request', states: ['pending_approval'] },
      { m: 'action_legal_review', l: 'Legal Review (Legal Reviewer)', states: ['pending_approval'], ask: 'Legal review note', kwarg: 'note' },
      { m: 'action_approve_stamp_exemption', l: 'Approve Stamp-Duty Exemption (Finance)', states: ['draft', 'pending_approval', 'pending_signature'] },
      { m: 'action_reset_to_draft', l: 'Reset to Draft', states: ['pending_approval', 'pending_signature'] },
      { m: 'action_activate', l: 'Activate (signed envelope required)', states: ['pending_signature'] },
      { m: 'action_renew', l: 'Draft Renewal Term', states: ['active', 'expiring', 'expired'] },
      { m: 'action_verify_wet_signature', l: 'Verify Wet-Ink Signature (second officer)', states: ['draft', 'pending_approval', 'pending_signature'] },
      { m: 'action_print_contract', l: 'Print Contract (PDF)', states: ['draft', 'pending_approval', 'pending_signature', 'active', 'expiring', 'expired', 'suspended', 'terminated'] }
      /* Resume now declares the treatment of the suspended period:
       * + Reinstate a Suspended Contract (capture pass 2) */
    ] },
  'M08-families': { kind: 'table_report', module: 'M08', report: 'contract_families', title: 'Contract Product Families', period: false },
  'M08-master': { kind: 'model_list', model: 'fix.contract', stateField: 'state',
    /* FR-CTR-006: a master agreement is a contract with subsidiaries. This
     * list used to show every active contract under that name. */
    domain: [['is_master_agreement', '=', true]],
    empty: 'No master agreement yet: a contract becomes one when a subsidiary contract names it as its Master Agreement.',
    cols: ['name', 'customer_id', 'family', 'subsidiary_count', 'annual_value', 'owner_id', 'date_end', 'state'] },
  'M08-scope': { kind: 'table_report', module: 'M08', report: 'scope_coverage', title: 'Covered Assets & Sites', period: false },
  'M08-entitle': { kind: 'model_list', model: 'fix.contract.entitlement',
    cols: ['contract_id', 'device_id', 'entitlement_type', 'quantity_included', 'quantity_consumed', 'quantity_remaining'] },
  'M08-balance': { kind: 'table_report', module: 'M08', report: 'entitlement_balance', title: 'Balances, Carry-Over, Top-Up', period: false },
  'M08-sla': { kind: 'table_report', module: 'M08', report: 'sla_credit_register', title: 'Contract SLA & Credits', period: false },
  'M08-pm': { kind: 'model_list', model: 'fix.contract.pm.visit', stateField: 'state',
    cols: ['contract_id', 'device_id', 'visit_type', 'plan_id', 'scheduled_date', 'dispatch_from', 'service_order_id', 'state'],
    actions: [
      { m: 'action_create_service_order', l: 'Dispatch (open the service order)', states: ['scheduled'] },
      { m: 'action_complete', l: 'Complete (order delivered)', states: ['dispatched'] },
      { m: 'action_skip', l: 'Skip Visit (Contract Manager)', states: ['scheduled'], ask: 'Why is this visit skipped?', kwarg: 'reason' }
    ] },
  'M08-auto-work': { kind: 'table_report', module: 'M08', report: 'contract_driven_work', title: 'Contract-Driven Work', period: false },
  // An amendment applies itself once approved (from the M63 inbox) and
  // versions the contract; a billed period cannot be amended.
  'M08-amend': { kind: 'model_list', model: 'fix.contract.amendment', stateField: 'state',
    cols: ['name', 'contract_id', 'kind', 'delta_value', 'effective_from', 'version_no', 'state', 'approval_state'],
    actions: [
      { m: 'action_request_approval', l: 'Submit for Approval', states: ['draft'], ask: 'Business justification (mandatory from Tier 2)', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Approval Request', states: ['submitted'] },
      { m: 'action_cancel', l: 'Cancel Amendment', states: ['draft', 'submitted', 'approved'] },
      { m: 'action_legal_review', l: 'Legal Review (crosses BDT 1M)', states: ['submitted', 'approved'], ask: 'Legal review note', kwarg: 'note' }
    ] },
  'M08-renewals': { kind: 'model_list', model: 'fix.contract.renewal', stateField: 'state',
    cols: ['name', 'contract_id', 'proposed_start', 'proposed_end', 'propo_value', 'risk', 'state', 'renewal_contract_id'],
    actions: [
      { m: 'action_quote', l: 'Issue Renewal Quote', states: ['draft'] },
      { m: 'action_mark_won', l: 'Won: Draft the Next Term', states: ['quoted'] }
      /* 'Lost' now records the churn reason: + Record a Lost Renewal */
    ] },
  // Stamp Act 1899 Schedule I. A DRAFT row is not in force - until Finance
  // confirms a rate against the current Finance Act the instrument stays
  // chargeable, so an empty or unconfirmed table never waives duty.
  'M08-stampduty': { kind: 'model_list', model: 'fix.stamp.duty.schedule',
    stateField: 'state', create: true,
    cols: ['article', 'name', 'state', 'date_from', 'date_to',
      'exemption_floor_bdt', 'duty_rate_pct', 'duty_fixed_bdt',
      'statutory_reference', 'confirmed_by'] },
  'M08-form-stampduty': { kind: 'model_form', model: 'fix.stamp.duty.schedule',
    title: 'Stamp Act 1899 \u2014 Schedule I Rate', back: 'M08-stampduty',
    status: { field: 'state' },
    tabs: [
      { id: 'head', label: '1. Head of Charge', bn: '\u09e7. \u0995\u09b0 \u09b6\u09bf\u09b0\u09cb\u09a8\u09be\u09ae' },
      { id: 'rate', label: '2. Rate & Threshold', bn: '\u09e8. \u09b9\u09be\u09b0 \u0993 \u09b8\u09c0\u09ae\u09be' },
      { id: 'window', label: '3. Effective Window', bn: '\u09e9. \u0995\u09be\u09b0\u09cd\u09af\u0995\u09b0 \u09b8\u09ae\u09af\u09bc' },
      { id: 'source', label: '4. Statutory Source', bn: '\u09ea. \u0986\u0987\u09a8\u09bf \u0989\u09ce\u09b8' },
      { id: 'audit', label: '5. Confirmation', bn: '\u09eb. \u09a8\u09bf\u09b6\u09cd\u099a\u09bf\u09a4\u0995\u09b0\u09a3' }
    ],
    sections: [
      { tab: 'head', title: '1. Head of Charge', fields: [
        { name: 'article', label: 'Schedule I Article', required: true },
        { name: 'name', label: 'Description', required: true },
        { name: 'company_id', label: 'Company', required: true }
      ] },
      { tab: 'rate', title: '2. Rate & Threshold', fields: [
        { name: 'exemption_floor_bdt', label: 'Duty-Free Threshold (BDT)' },
        { name: 'duty_rate_pct', label: 'Ad Valorem Rate (%)' },
        { name: 'duty_fixed_bdt', label: 'Fixed Duty (BDT)' },
        { name: 'currency_id', label: 'Currency', required: true }
      ] },
      { tab: 'window', title: '3. Effective Window', fields: [
        { name: 'date_from', label: 'Effective From', required: true },
        { name: 'date_to', label: 'Effective To' },
        { name: 'active', label: 'Active' }
      ] },
      { tab: 'source', title: '4. Statutory Source', fields: [
        { name: 'statutory_reference', label: 'Finance Act / SRO', required: true }
      ] },
      { tab: 'audit', title: '5. Confirmation', fields: [
        { name: 'state', label: 'Status', readonly: true },
        { name: 'confirmed_by', label: 'Confirmed By', readonly: true },
        { name: 'confirmed_on', label: 'Confirmed On', readonly: true }
      ] }
    ],
    actions: [
      { m: 'action_confirm', label: 'Confirm Rate' },
      { m: 'action_reset_to_draft', label: 'Withdraw' }
    ] },
  // The DOFA tier is derived from the unexpired value plus the penalty and
  // approved from the tier holder's M63 inbox; the penalty is pinned.
  'M08-termination': { kind: 'model_list', model: 'fix.contract.termination', stateField: 'state',
    cols: ['name', 'contract_id', 'kind', 'reason', 'effective_date', 'penalty_amount', 'dofa_tier_required', 'notice_ok', 'state', 'approval_state'],
    actions: [
      { m: 'action_request_approval', l: 'Submit for DOFA Approval', states: ['draft'], ask: 'Business justification (mandatory from Tier 2)', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Approval Request', states: ['submitted'] },
      { m: 'action_execute_termination', l: 'Execute (Contract Manager)', states: ['approved'] },
      { m: 'action_cancel', l: 'Cancel Notice', states: ['draft', 'submitted', 'approved'] }
    ] },
  // A04 ERP audit M08-F1: the days a contract was suspended; never billed.
  // Written by the engine (suspension, resume, termination), read-only here.
  'M08-suspensions': { kind: 'model_list', model: 'fix.contract.suspension', create: false,
    cols: ['contract_id', 'date_from', 'date_to', 'compensated', 'treatment'] },
  'M08-churn': { kind: 'table_report', module: 'M08', report: 'churn_risk', title: 'Churn & Win-Back', period: false },
  'M08-pricing': { kind: 'table_report', module: 'M08', report: 'contract_pricing', title: 'Contract Pricing Link', period: false },
  'M08-profit': { kind: 'table_report', module: 'M08', report: 'contract_pnl', title: 'Profitability & Alerts', period: false },

  /* Report chips -> their own computed pack */
  'M08-rpt-base': { kind: 'table_report', module: 'M08', report: 'contract_base_movement', title: 'Contract Base Movement', period: false },
  'M08-rpt-entitle': { kind: 'table_report', module: 'M08', report: 'entitlement_consumption', title: 'Entitlement Consumption by Client', period: false },
  'M08-rpt-sla': { kind: 'table_report', module: 'M08', report: 'sla_credit_register', title: 'SLA Credit Register', period: false },
  'M08-rpt-pm': { kind: 'table_report', module: 'M08', report: 'pm_compliance', title: 'PM Compliance Report', period: false },
  'M08-rpt-renew': { kind: 'table_report', module: 'M08', report: 'renewal_pipeline', title: 'Renewal Pipeline & Risk', period: false },
  'M08-rpt-pnl': { kind: 'table_report', module: 'M08', report: 'contract_pnl', title: 'Contract P&L', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M08-record': {
    lines: {
      field: 'entitlement_ids',
      title: 'Contract Entitlements — what the customer may draw',
      note: 'Quantity remaining is consumed as service orders are delivered against this contract.',
      fields: [
        { name: 'entitlement_type', label: 'Entitlement', required: true },
        { name: 'device_id', label: 'Device' },
        { name: 'quantity_included', label: 'Included', required: true },
        { name: 'quantity_consumed', label: 'Consumed', readonly: true },
        { name: 'quantity_remaining', label: 'Remaining', readonly: true }
      ]
    },
    kind: 'model_form',
    model: 'fix.contract',
    title: 'Enterprise Service Contract',
    back: 'M08-contracts',
    status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. General Profile', bn: '১. সাধারণ চুক্তি', icon: '📜', badge: '7' },
      { id: 'financial', label: '2. Commercial & Escalation', bn: '২. আর্থিক ও মূল্য', icon: '💰', badge: '6' },
      { id: 'sla_visits', label: '3. Coverage, SLAs & Visits', bn: '৩. কাভারেজ ও এসএলএ', icon: '🛡️', badge: '6' },
      { id: 'statutory', label: '4. Stamp Duty & Compliance', bn: '৪. স্ট্যাম্প ও সম্মতি', icon: '⚖️', badge: '4' },
      { id: 'governance', label: '5. Governance & DOFA', bn: '৫. নবায়ন ও অনুমোদন', icon: '🏛️', badge: '2' },
      { id: 'vault', label: '6. Document Vault', bn: '৬. নথিপত্র', icon: '📁', badge: '2' }
    ],
    sections: [
      { tab: 'general', title: 'Contract Identity & Master Setup',
        note: 'One engine for the five product families it carries: AMC, RAMC, managed services, rental and marketplace agreements. A new family is added to the family registry first.',
        fields: [
          { name: 'name', required: true, label: 'Contract Title' },
          { name: 'code', required: true, label: 'Contract Code', readonly: true },
          { name: 'customer_id', required: true, label: 'Enterprise Customer' },
          { name: 'family', required: true, label: 'Product Family' },
          { name: 'company_id', required: true, label: 'Operating Company' },
          { name: 'operating_unit_id', required: true, label: 'Operating Unit' },
          { name: 'state', label: 'Lifecycle Status', readonly: true },
          { name: 'template_id', label: 'Contract Template (Legal-signed)' },
          { name: 'owner_id', label: 'Contract Owner (1000FiX)' },
          { name: 'parent_contract_id', label: 'Master Agreement (for a subsidiary contract)' }
        ] },
      { tab: 'financial', title: 'Commercial Value, Delivery Cost & Margins',
        fields: [
          { name: 'annual_value', required: true, label: 'Annual Contract Value (BDT)' },
          { name: 'term_value', label: 'Term Value, excl. VAT (BDT)', readonly: true },
          { name: 'accepted_total', label: 'Accepted Total, incl. VAT (BDT)', readonly: true },
          { name: 'billing_frequency', required: true, label: 'Billing Frequency' },
          { name: 'billing_timing', required: true, label: 'Billed In Arrears / In Advance' },
          { name: 'retention_pct', label: 'Retention Withheld (%)' },
          { name: 'total_delivery_cost', label: 'Cost to Serve over the Term (BDT)', readonly: true },
          { name: 'contract_margin_bdt', label: 'Gross Contract Margin (BDT)', readonly: true },
          { name: 'contract_margin_pct', label: 'Gross Margin (%)', readonly: true },
          { name: 'escalation_pct', label: 'Annual Escalation Rate (%)' },
          { name: 'currency_id', label: 'Currency' },
          { name: 'amendment_version', label: 'Amendment Version', readonly: true },
          { name: 'billed_through_date', label: 'Billed Through', readonly: true },
          { name: 'terminated_on', label: 'Terminated With Effect From', readonly: true }
        ] },
      /* the tab was named for coverage and SLAs and held neither: no form set
       * the covered assets, so an activated contract generated no PM visit
       * and no device of it counted as covered (M08 capture audit 2026-11-13) */
      { tab: 'sla_visits', title: 'Service Commitments & PM Visits',
        note: 'Preventive visits are generated at activation for every covered asset. Cover and SLAs are set while the contract is a draft; they are fixed once it is submitted. Devices are registered in the Asset Registry (M17).',
        fields: [
          { name: 'date_start', required: true, label: 'Coverage Start Date' },
          { name: 'date_end', required: true, label: 'Coverage End Date' },
          { name: 'covered_device_ids', label: 'Covered Assets (devices)' },
          { name: 'sla_policy_ids', label: 'Contract SLAs' },
          { name: 'auto_renew', label: 'Auto-Renewal Enabled' },
          { name: 'renewal_lead_days', label: 'Renewal Notification Lead (Days)' }
        ] },
      { tab: 'statutory', title: 'Statutory Stamp Duty (Stamp Act 1899)',
        note: 'Statutory Stamp Duty registration pursuant to Stamp Act 1899 Schedule I.',
        fields: [
          { name: 'stamp_duty_cert_no', label: 'Stamp Duty Certificate Number' },
          { name: 'stamp_duty_amount', label: 'Stamp Duty Amount Paid (BDT)' },
          { name: 'stamp_act_article', label: 'Stamp Act Article (Schedule I)' },
          { name: 'stamp_duty_applicable', label: 'Chargeable Under Schedule I' },
          { name: 'stamp_duty_exemption_reason', label: 'Non-Chargeable Reason' },
          { name: 'stamp_exemption_approved_by', label: 'Exemption Approved By (Finance)', readonly: true },
          { name: 'has_signed_contract_doc', label: 'Signed Contract PDF Verified', readonly: true }
        ] },
      { tab: 'governance', title: 'OCA Architecture & E-Signature Governance',
        fields: [
          { name: 'oca_contract_id', label: 'OCA Contract Reference', readonly: true },
          { name: 'signature_method', label: 'Signature Method' },
          { name: 'esignature_envelope_id', label: 'Kernel E-Signature Envelope (M24)' },
          { name: 'dofa_tier_required', label: 'DOFA Tier (from the total contract value)', readonly: true },
          { name: 'approval_state', label: 'Value Approval', readonly: true },
          { name: 'dofa_approved_by', label: 'Value Approved By', readonly: true },
          { name: 'legal_review_required', label: 'Legal Review Required', readonly: true },
          { name: 'legal_reviewed_by', label: 'Legal Review By', readonly: true },
          { name: 'activated_by', label: 'Activated By', readonly: true }
        ] },
      { tab: 'vault', title: 'Legal & Contract Document Vault',
        note: 'Archived physical copies, bilateral agreements, and verified digital signatures.',
        fields: [] }
    ]
  },

  /* A scope amendment carries its changes as lines, applied on approval
   * (M08 gaps 2026-11-13): before, a scope amendment versioned the contract
   * and changed nothing. Pricing and term amendments carry no lines. */
  'M08-form-amendment': {
    lines: {
      field: 'line_ids',
      title: 'Scope Changes (scope amendments only)',
      note: 'One row per change: attach or detach a covered asset, add an entitlement or change its quantity, add or remove an SLA or an exclusion. They apply when the amendment is approved and effective; an attached asset gets its preventive visits from that date.',
      fields: [
        { name: 'action', label: 'Change', required: true },
        { name: 'device_id', label: 'Device' },
        { name: 'entitlement_type', label: 'New Entitlement' },
        { name: 'entitlement_id', label: 'Existing Entitlement' },
        { name: 'quantity', label: 'Quantity' },
        { name: 'sla_policy_id', label: 'SLA' },
        { name: 'exclusion_type', label: 'Exclusion Type' },
        { name: 'exclusion_text', label: 'Exclusion Wording' },
        { name: 'exclusion_id', label: 'Exclusion to Remove' }
      ]
    },
    kind: 'model_form',
    model: 'fix.contract.amendment',
    title: 'Contract Variation & Amendment',
    back: 'M08-amend',
    status: { field: 'state' },
    tabs: [
      { id: 'amendment_core', label: '1. Amendment Details', bn: '১. সংশোধনীর বিবরণ', icon: '📝', badge: '4' },
      { id: 'financial_impact', label: '2. Financial Impact', bn: '২. আর্থিক প্রভাব', icon: '💰', badge: '2' },
      { id: 'governance', label: '3. Approval & Status', bn: '৩. অনুমোদন ও অবস্থা', icon: '✅', badge: '1' }
    ],
    sections: [
      { tab: 'amendment_core', title: 'Amendment Identification', note: 'A pricing, scope or term variation under the master contract.',
        fields: [
          { name: 'name', required: true, label: 'Amendment Name' },
          { name: 'contract_id', required: true, label: 'Contract (in force)', domain: [['state', 'in', ['active', 'expiring']]] },
          { name: 'kind', required: true, label: 'Variation Kind' },
          { name: 'effective_from', required: true, label: 'Effective From' }
        ] },
      { tab: 'financial_impact', title: 'Financial Value & Variation Scope', note: 'Financial impact applied upon final approval.',
        fields: [
          { name: 'delta_value', label: 'Value Change (BDT)' },
          { name: 'new_date_end', label: 'New Term End (term change)' },
          { name: 'note', label: 'Variation Narrative / Justification', type: 'text' }
        ] },
      { tab: 'governance', title: 'Governance & Lifecycle State', fields: [
          { name: 'state', label: 'Lifecycle State', readonly: true },
          { name: 'dofa_tier_required', label: 'DOFA Tier (from the change)', readonly: true },
          { name: 'approval_state', label: 'Approval', readonly: true },
          { name: 'version_no', label: 'Contract Version', readonly: true },
          { name: 'value_before', label: 'Value Before', readonly: true },
          { name: 'value_after', label: 'Value After', readonly: true },
          { name: 'legal_review_required', label: 'Legal Review Required (crosses BDT 1M)', readonly: true },
          { name: 'legal_reviewed_by', label: 'Legal Review By', readonly: true }
        ] }
    ]
  },
  /* It was titled "Asset Attach / Detach" and captured an entitlement: the
   * registry's attach/detach form is M08-form-coverage. An entitlement is
   * added while its contract is a draft (the model refuses it after). The
   * "My Activity Deadline" tab it carried showed nothing of the entitlement. */
  'M08-form-entitlement': { kind: 'model_form', model: 'fix.contract.entitlement',
    title: 'Contract Entitlement', back: 'M08-entitle',
    /* the balance is the sum of these movements (T-01): written by the
     * engine, shown here, never typed */
    lines: {
      field: 'movement_ids',
      readonlyGrid: true,
      title: 'Entitlement Ledger',
      note: 'Granted at activation, drawn down by delivered orders, restored on cancellation, grown by top-ups.',
      fields: [
        { name: 'moved_on', label: 'When', readonly: true },
        { name: 'movement_type', label: 'Movement', readonly: true },
        { name: 'quantity', label: 'Quantity', readonly: true },
        { name: 'balance_after', label: 'Balance After', readonly: true },
        { name: 'source_ref', label: 'Source Document', readonly: true }
      ]
    },
    tabs: [
      { id: 'general', label: '1. Entitlement', bn: '১. এনটাইটেলমেন্ট' },
      { id: 'relations', label: '2. Contract & Device', bn: '২. চুক্তি ও ডিভাইস' },
      { id: 'audit', label: '3. System Audit', bn: '৩. সিস্টেম অডিট' },
      { id: 'docs', label: '4. Documents', bn: '৪. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'general', title: '1. What the Customer May Draw', note: 'State the quantity: 0 is an unlimited entitlement and must be entered on purpose. A monthly or annual entitlement starts again at its full quantity each period (no carry-over). Consumption is recorded by the service orders delivered against the contract, never typed.', fields: [
        { name: 'entitlement_type', label: 'Entitlement Type', required: true },
        { name: 'quantity_included', label: 'Included (0 = unlimited)', required: true },
        { name: 'reset_period', label: 'Renewed', required: true },
        { name: 'exhaustion_policy', label: 'When Used Up', required: true },
        { name: 'quantity_consumed', label: 'Consumed', readonly: true },
        { name: 'quantity_remaining', label: 'Remaining', readonly: true }
      ] },
      { tab: 'relations', title: '2. Contract & Device', note: 'Only draft contracts are offered: once a contract is submitted for approval its entitlements are fixed.', fields: [
        { name: 'contract_id', label: 'Contract', required: true, domain: [['state', '=', 'draft']] },
        { name: 'device_id', label: 'Device (blank = the whole contract)' }
      ] },
      { tab: 'audit', title: '3. System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true },
        { name: 'write_uid', label: 'Last Updated by', readonly: true },
        { name: 'write_date', label: 'Last Updated on', readonly: true }
      ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'Related collections (related records) and file evidence attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] },
    ] },

  'M08-form-renewal': { kind: 'model_form', model: 'fix.contract.renewal',
    title: 'Renewal Quote', back: 'M08-renewals',
    status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ তথ্য' },
      { id: 'commercial', label: '2. Commercial', bn: '২. বাণিজ্যিক শর্ত' },
      { id: 'schedule', label: '3. Schedule', bn: '৩. সময়সূচি' },
      { id: 'relations', label: '4. Links', bn: '৪. সংযোগ' },
      { id: 'audit', label: '5. System Audit', bn: '৫. সিস্টেম অডিট' },
      { id: 'docs', label: '6. Documents', bn: '৬. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'general', title: '1. General', fields: [
        { name: 'name', label: 'Renewal Name', required: true },
        { name: 'risk', label: 'Risk', required: true },
        { name: 'state', label: 'State', readonly: true },
        { name: 'renewal_contract_id', label: 'Next Term', readonly: true }
      ] },
      { tab: 'commercial', title: '2. Commercial', fields: [
        { name: 'propo_value', label: 'Proposed Value' }
      ] },
      { tab: 'schedule', title: '3. Schedule', fields: [
        { name: 'proposed_start', label: 'Proposed Start', required: true },
        { name: 'proposed_end', label: 'Proposed End', required: true }
      ] },
      { tab: 'relations', title: '4. Links', fields: [
        { name: 'contract_id', label: 'Contract (in force or expired)', required: true, domain: [['state', 'in', ['active', 'expiring', 'expired']]] },
        { name: 'currency_id', label: 'Currency', required: true }
      ] },
      { tab: 'audit', title: '8. System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true },
        { name: 'write_uid', label: 'Last Updated by', readonly: true },
        { name: 'write_date', label: 'Last Updated on', readonly: true }
      ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'Related collections (related records) and file evidence attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] },
    ] },

  'M08-form-pm': { kind: 'model_form', model: 'fix.contract.pm.visit',
    title: 'PM Schedule', back: 'M08-pm',
    status: { field: 'state' },
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ তথ্য' },
      { id: 'schedule', label: '2. Schedule', bn: '২. সময়সূচি' },
      { id: 'relations', label: '3. Links', bn: '৩. সংযোগ' },
      { id: 'audit', label: '4. System Audit', bn: '৪. সিস্টেম অডিট' },
      { id: 'docs', label: '5. Documents', bn: '৫. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'general', title: '1. General', fields: [
        { name: 'state', label: 'State', readonly: true },
        { name: 'skip_reason', label: 'Skip Reason', readonly: true }
      ] },
      { tab: 'schedule', title: '3. Schedule', fields: [
        { name: 'scheduled_date', label: 'Scheduled Date', required: true }
      ] },
      { tab: 'relations', title: '4. Links', fields: [
        { name: 'contract_id', label: 'Contract', required: true },
        { name: 'device_id', label: 'Device', required: true },
        { name: 'service_order_id', label: 'Service Order', readonly: true }
      ] },
      { tab: 'audit', title: '8. System Audit', fields: [
        { name: 'create_uid', label: 'Created by', readonly: true },
        { name: 'create_date', label: 'Created on', readonly: true },
        { name: 'write_uid', label: 'Last Updated by', readonly: true },
        { name: 'write_date', label: 'Last Updated on', readonly: true }
      ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'Related collections (related records) and file evidence attach to this record; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] },
    ] },

  /* ===== M08 capture audit 2026-11-13: a capture per sub-module =====
   * Measured with the page rule (fregCreate) over this registry: pages 2, 5,
   * 10 and 11 offered nothing, 3 and 4 offered the same entitlement form
   * under the name "Asset Attach / Detach", and 9 offered a form no chip
   * named. fix_real held no M08 record at all, so these buttons are the only
   * way the contract base can start. */

  /* 3 Coverage Scope: FR-CTR-013/015. The covered assets and the contract
   * SLAs were on NO form, while activation generates PM visits only for
   * covered assets and an AMC order is accepted only for a covered device
   * (BRU-SRM-03). Cover is a term of the contract: editable while it is a
   * draft, fixed once it is submitted (the model refuses a later change). */
  'M08-form-coverage': { kind: 'model_form', model: 'fix.contract',
    title: 'Covered Assets & Contract SLAs', back: 'M08-contracts',
    newLabel: 'Attach / Detach Covered Assets',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the draft contract whose cover you set',
      note: 'Draft contracts only: once a contract is submitted for approval, what it covers is fixed with its other terms.',
      search: 'Search contract / customer',
      choose: 'Set the cover of this contract',
      cols: ['code', 'name', 'customer_id', 'family', 'date_start', 'date_end'],
      domain: [['state', '=', 'draft']],
      empty: 'There is no draft contract. Create the contract first with + New Contract; its cover is set before it is submitted.',
      emptyNew: true
    },
    tabs: [
      { id: 'cover', label: '1. Covered Assets & SLAs', bn: '১. কভারেজ ও এসএলএ', icon: '🛡️', badge: '2' },
      { id: 'contract', label: '2. Contract', bn: '২. চুক্তি', icon: '📜', badge: '5' }
    ],
    sections: [
      { tab: 'cover', title: 'Step 2 of 2: What the Contract Covers',
        note: 'Every covered asset gets its preventive visits when the contract is activated, and only a covered device can be booked as contract work. Add or remove devices; the save replaces the list. Devices are registered in the Asset Registry (M17): a device not yet registered is not offered.',
        fields: [
          { name: 'covered_device_ids', label: 'Covered Assets (devices)' },
          { name: 'sla_policy_ids', label: 'Contract SLAs (override the standard SLA)' }
        ] },
      { tab: 'contract', title: 'Contract', fields: [
        { name: 'code', label: 'Contract No.', readonly: true },
        { name: 'name', label: 'Contract Title', readonly: true },
        { name: 'customer_id', label: 'Customer', readonly: true },
        { name: 'family', label: 'Product Family', readonly: true },
        { name: 'state', label: 'Status', readonly: true }
      ] }
    ] },

  /* 2 Parties & Approval: FR-CTR-012 and the lifecycle's Draft -> Pending
   * Approval. The value goes to the DOFA tier holder's M63 inbox; the terms
   * freeze from here. action_request_approval checks the role, the value
   * and the stamp-duty claim. */
  'M08-form-submit': { kind: 'model_form', model: 'fix.contract',
    title: 'Submit Contract for Value Approval', back: 'M08-contracts',
    newLabel: 'Submit a Contract for Approval',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the draft contract to submit',
      note: 'Draft contracts. Set the cover, entitlements and stamp duty first: they are fixed once the contract is submitted.',
      search: 'Search contract / customer',
      choose: 'Submit this contract',
      cols: ['code', 'name', 'customer_id', 'annual_value', 'dofa_tier_required', 'legal_review_required'],
      domain: [['state', '=', 'draft']],
      empty: 'There is no draft contract to submit. Create one with + New Contract.',
      emptyNew: true
    },
    saveAction: {
      method: 'action_request_approval', label: 'Submit for Approval',
      done: 'Submitted: the value approval is in the approver inbox',
      kwargs: { justification: 'dofa_justification' }
    },
    tabs: [
      { id: 'submit', label: '1. Justification', bn: '১. যৌক্তিকতা', icon: '✍️', badge: '1' },
      { id: 'contract', label: '2. Contract & Approval Route', bn: '২. চুক্তি ও অনুমোদন', icon: '📜', badge: '7' }
    ],
    sections: [
      { tab: 'submit', title: 'Step 2 of 2: Business Justification',
        note: 'Mandatory from DOFA Tier 2. The approver decides in the M63 inbox; you can recall the request until it is decided.',
        fields: [
          /* readonly for the generic write; an INPUT here because saveAction
           * carries it to action_request_approval */
          { name: 'dofa_justification', label: 'Business Justification', type: 'text', readonly: true }
        ] },
      { tab: 'contract', title: 'Contract & Approval Route', fields: [
        { name: 'code', label: 'Contract No.', readonly: true },
        { name: 'name', label: 'Contract Title', readonly: true },
        { name: 'customer_id', label: 'Customer', readonly: true },
        { name: 'annual_value', label: 'Annual Value (BDT)', readonly: true },
        { name: 'dofa_tier_required', label: 'DOFA Tier (from the value)', readonly: true },
        { name: 'legal_review_required', label: 'Legal Review Required', readonly: true },
        { name: 'stamp_duty_applicable', label: 'Chargeable Under Schedule I', readonly: true }
      ] }
    ] },

  /* 2 Parties & Approval: Legal clears the terms of a contract awaiting
   * approval - a Legal reviewer who neither raised nor approved it. */
  'M08-form-legal': { kind: 'model_form', model: 'fix.contract',
    title: 'Legal Review of Contract Terms', back: 'M08-contracts',
    newLabel: 'Record a Legal Review',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the contract Legal has reviewed',
      note: 'Contracts awaiting approval that need Legal review and have none yet.',
      search: 'Search contract / customer',
      choose: 'Review this contract',
      cols: ['code', 'name', 'customer_id', 'family', 'annual_value'],
      domain: [['state', '=', 'pending_approval'], ['legal_review_required', '=', true], ['legal_reviewed_by', '=', false]],
      empty: 'No contract is waiting for Legal review.'
    },
    saveAction: {
      method: 'action_legal_review', label: 'Record Legal Review',
      done: 'Legal review recorded',
      kwargs: { note: 'legal_review_note' }
    },
    tabs: [
      { id: 'review', label: '1. Review Note', bn: '১. পর্যালোচনা', icon: '⚖️', badge: '1' },
      { id: 'contract', label: '2. Contract', bn: '২. চুক্তি', icon: '📜', badge: '5' }
    ],
    sections: [
      { tab: 'review', title: 'Step 2 of 2: Legal Review Note',
        note: 'Needs the Legal Reviewer role. Segregation of duties: whoever raised the contract or approved its value cannot review it.',
        fields: [
          /* readonly for the generic write; an INPUT here because saveAction
           * carries it to action_legal_review */
          { name: 'legal_review_note', label: 'Review Note', type: 'text', readonly: true }
        ] },
      { tab: 'contract', title: 'Contract', fields: [
        { name: 'code', label: 'Contract No.', readonly: true },
        { name: 'name', label: 'Contract Title', readonly: true },
        { name: 'customer_id', label: 'Customer', readonly: true },
        { name: 'family', label: 'Product Family', readonly: true },
        { name: 'annual_value', label: 'Annual Value (BDT)', readonly: true }
      ] }
    ] },

  /* 10 Pricing & Profitability: FR-CTR-036/047. The price of a live
   * contract changes only through a PRICING amendment approved under DOFA on
   * the change (a draft is simply edited on its own form). */
  'M08-form-price': { kind: 'model_form', model: 'fix.contract.amendment',
    title: 'Price Revision', back: 'M08-amend',
    newLabel: 'Raise a Price Revision',
    presets: { kind: 'pricing' },
    status: { field: 'state' },
    tabs: [
      { id: 'price', label: '1. Price Change', bn: '১. মূল্য পরিবর্তন', icon: '💰', badge: '6' },
      { id: 'governance', label: '2. Approval', bn: '২. অনুমোদন', icon: '✅', badge: '4' }
    ],
    sections: [
      { tab: 'price', title: 'Price Change on a Contract in Force',
        note: 'Submit it for approval from Amendments & Variations; it applies itself once approved and versions the contract. It cannot take effect inside a billed period.',
        fields: [
          { name: 'name', required: true, label: 'Revision Name' },
          { name: 'contract_id', required: true, label: 'Contract (in force)', domain: [['state', 'in', ['active', 'expiring']]] },
          { name: 'kind', required: true, label: 'Variation Kind', choices: [['pricing', 'Pricing change']] },
          { name: 'delta_value', required: true, label: 'Value Change (BDT, negative to reduce)' },
          { name: 'effective_from', required: true, label: 'Effective From' },
          { name: 'note', label: 'Reason / Escalation Basis' }
        ] },
      { tab: 'governance', title: 'Approval', fields: [
        { name: 'state', label: 'State', readonly: true },
        { name: 'dofa_tier_required', label: 'DOFA Tier (from the change)', readonly: true },
        { name: 'value_before', label: 'Value Before', readonly: true },
        { name: 'value_after', label: 'Value After', readonly: true }
      ] }
    ] },

  /* 11 Documents & Signature: FR-CTR-010/011 and Stamp Act 1899. Activation
   * requires a completed e-signature envelope (M24) and the stamp duty
   * discharged or the exemption approved. The envelope can be attached until
   * signature; the stamp-duty terms only while the contract is a draft. */
  'M08-form-signature': { kind: 'model_form', model: 'fix.contract',
    title: 'Signature & Stamp Duty', back: 'M08-contracts',
    newLabel: 'Record Signature & Stamp Duty',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the contract to record its signature or stamp duty',
      note: 'Contracts not yet active. Stamp duty is recorded while the contract is a draft; the signature envelope until the contract is signed.',
      search: 'Search contract / customer',
      choose: 'Record for this contract',
      cols: ['code', 'name', 'customer_id', 'state', 'esignature_envelope_id', 'stamp_duty_cert_no'],
      domain: [['state', 'in', ['draft', 'pending_approval', 'pending_signature']]],
      empty: 'No contract is waiting for its signature or stamp duty.'
    },
    tabs: [
      { id: 'signature', label: '1. E-Signature', bn: '১. ই-স্বাক্ষর', icon: '✍️', badge: '2' },
      { id: 'stamp', label: '2. Stamp Duty', bn: '২. স্ট্যাম্প ডিউটি', icon: '⚖️', badge: '6' },
      { id: 'contract', label: '3. Contract', bn: '৩. চুক্তি', icon: '📜', badge: '4' }
    ],
    sections: [
      { tab: 'signature', title: 'Step 2 of 2: Signature Envelope',
        note: 'Electronic: the envelope is prepared and completed in Document Management (M24); activation checks it is completed, every signer signed, the customer is among them and the signed document is on file. Wet ink: upload the scan of the signed original and its date; a second officer verifies it (Verify a Wet-Ink Signature) before activation.',
        fields: [
          { name: 'signature_method', label: 'Signature Method', required: true },
          { name: 'esignature_envelope_id', label: 'E-Signature Envelope (M24) - electronic' },
          { name: 'wet_signed_on', label: 'Signed On - wet ink' },
          { name: 'wet_signed_file_id', label: 'Scanned Signed Original - wet ink' },
          { name: 'wet_signed_document_id', label: 'Filed in M24 as', readonly: true },
          { name: 'wet_signature_verified_by', label: 'Ink Signature Verified By', readonly: true },
          { name: 'has_signed_contract_doc', label: 'Signed Contract Verified', readonly: true }
        ] },
      { tab: 'stamp', title: 'Stamp Duty (Stamp Act 1899, Schedule I)',
        note: 'A claimed exemption needs a reason and Finance approval (Approve Stamp-Duty Exemption on the contract list).',
        fields: [
          { name: 'stamp_act_article', label: 'Stamp Act Article (Schedule I)' },
          { name: 'stamp_duty_applicable', label: 'Chargeable Under Schedule I' },
          { name: 'stamp_duty_cert_no', label: 'Stamp Duty Certificate Number' },
          { name: 'stamp_duty_amount', label: 'Stamp Duty Paid (BDT)' },
          { name: 'stamp_duty_exemption_reason', label: 'Non-Chargeable Reason' },
          { name: 'stamp_exemption_approved_by', label: 'Exemption Approved By (Finance)', readonly: true }
        ] },
      { tab: 'contract', title: 'Contract', fields: [
        { name: 'code', label: 'Contract No.', readonly: true },
        { name: 'name', label: 'Contract Title', readonly: true },
        { name: 'customer_id', label: 'Customer', readonly: true },
        { name: 'state', label: 'Status', readonly: true }
      ] }
    ] },

  /* ===== M08 gaps 2026-11-13: parties, exclusions, obligations, churn ===== */

  /* FR-CTR-004: parties and signatories. Signatories freeze once the
   * contract is signed; requesters, approvers and notice parties can change
   * until it closes. */
  'M08-parties': { kind: 'model_list', model: 'fix.contract.party',
    cols: ['contract_id', 'partner_id', 'role', 'designation', 'email', 'phone', 'portal_access', 'contract_state'] },
  'M08-form-party': { kind: 'model_form', model: 'fix.contract.party',
    title: 'Contract Party', back: 'M08-parties',
    tabs: [
      { id: 'party', label: '1. Party & Role', bn: '১. পক্ষ ও ভূমিকা', icon: '👥', badge: '5' },
      { id: 'contact', label: '2. Contact & Notice', bn: '২. যোগাযোগ ও নোটিশ', icon: '✉️', badge: '4' }
    ],
    sections: [
      { tab: 'party', title: 'Who and in What Role',
        note: 'A signatory cannot be added or changed once the contract is signed. A notice party needs a postal address or an e-mail.',
        fields: [
          { name: 'contract_id', label: 'Contract', required: true, domain: [['state', 'not in', ['expired', 'terminated']]] },
          { name: 'partner_id', label: 'Person / Entity', required: true },
          { name: 'role', label: 'Role', required: true },
          { name: 'designation', label: 'Designation' },
          { name: 'is_primary', label: 'Primary for this Role' }
        ] },
      { tab: 'contact', title: 'Contact & Portal Access', fields: [
        { name: 'email', label: 'E-mail' },
        { name: 'phone', label: 'Phone' },
        { name: 'notice_address', label: 'Notice Address', type: 'text' },
        { name: 'portal_access', label: 'Corporate Portal Access (P04)' }
      ] }
    ] },

  /* FR-CTR-016: exclusions override inclusion. A term of the contract:
   * typed while it is a draft, changed afterwards by a scope amendment. */
  'M08-exclusions': { kind: 'model_list', model: 'fix.contract.exclusion',
    cols: ['contract_id', 'exclusion_type', 'name', 'name_bn', 'contract_state'] },
  'M08-form-exclusion': { kind: 'model_form', model: 'fix.contract.exclusion',
    title: 'Coverage Exclusion', back: 'M08-exclusions',
    tabs: [
      { id: 'exclusion', label: '1. Exclusion', bn: '১. বহির্ভূত', icon: '🚫', badge: '4' }
    ],
    sections: [
      { tab: 'exclusion', title: 'What the Contract Does Not Cover',
        note: 'Draft contracts only. On a contract in force, raise a scope amendment with an Add exclusion or Remove exclusion row.',
        fields: [
          { name: 'contract_id', label: 'Contract (draft)', required: true, domain: [['state', '=', 'draft']] },
          { name: 'exclusion_type', label: 'Exclusion Type', required: true },
          { name: 'name', label: 'Exclusion Wording', required: true },
          { name: 'name_bn', label: 'Exclusion Wording (Bangla)' }
        ] }
    ] },

  /* FR-CTR-032/033, AUT-CTR-16: every post-signature obligation, with its
   * owner, due date and evidence. A daily job reminds the owner a week ahead
   * and marks a missed one overdue; a mandatory one cannot be waived. */
  'M08-obligations': { kind: 'model_list', model: 'fix.contract.obligation', stateField: 'state',
    cols: ['name', 'contract_id', 'obligation_type', 'owed_by', 'mandatory', 'due_date', 'recurrence', 'owner_id', 'state'],
    actions: [
      { m: 'action_complete', l: 'Discharge (with evidence)', states: ['open', 'overdue'], ask: 'Evidence: certificate number, report reference or where the proof is filed', kwarg: 'evidence' },
      { m: 'action_waive', l: 'Waive (Contract Manager)', states: ['open', 'overdue'], ask: 'Why is this obligation waived?', kwarg: 'reason' }
    ] },
  'M08-form-obligation': { kind: 'model_form', model: 'fix.contract.obligation',
    title: 'Contract Obligation', back: 'M08-obligations',
    status: { field: 'state' },
    tabs: [
      { id: 'what', label: '1. Obligation', bn: '১. দায়বদ্ধতা', icon: '📋', badge: '6' },
      { id: 'when', label: '2. Due Date & Owner', bn: '২. তারিখ ও দায়িত্ব', icon: '📅', badge: '3' },
      { id: 'proof', label: '3. Evidence', bn: '৩. প্রমাণ', icon: '📎', badge: '5' }
    ],
    sections: [
      { tab: 'what', title: 'What Is Owed, and by Whom', fields: [
        { name: 'contract_id', label: 'Contract', required: true, domain: [['state', 'not in', ['expired', 'terminated']]] },
        { name: 'name', label: 'Obligation', required: true },
        { name: 'obligation_type', label: 'Type', required: true },
        { name: 'owed_by', label: 'Owed By', required: true },
        { name: 'mandatory', label: 'Mandatory (blocks compliance sign-off)' },
        { name: 'description', label: 'Details', type: 'text' }
      ] },
      { tab: 'when', title: 'Due Date, Recurrence & Owner',
        note: 'The owner gets a to-do a week before the due date; a missed obligation turns overdue and is escalated.',
        fields: [
          { name: 'due_date', label: 'Due Date', required: true },
          { name: 'recurrence', label: 'Recurrence', required: true },
          { name: 'owner_id', label: 'Owner', required: true }
        ] },
      { tab: 'proof', title: 'Completion Evidence',
        note: 'Discharge it from the Obligation Register with the evidence; a recurring obligation then opens its next occurrence.',
        fields: [
          { name: 'evidence_document_id', label: 'Evidence Document (M24)' },
          { name: 'state', label: 'Status', readonly: true },
          { name: 'evidence_note', label: 'Evidence Recorded', readonly: true },
          { name: 'completed_by', label: 'Discharged By', readonly: true },
          { name: 'next_obligation_id', label: 'Next Occurrence', readonly: true }
        ] }
    ] },

  /* FR-CTR-050/051: a lost renewal is churn, recorded with its reason, the
   * competitor where known and win-back candidacy (announced for M35). */
  'M08-form-lost': { kind: 'model_form', model: 'fix.contract.renewal',
    title: 'Lost Renewal (Churn)', back: 'M08-renewals',
    newLabel: 'Record a Lost Renewal',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the renewal the customer declined',
      note: 'Open renewals (draft or quoted).',
      search: 'Search renewal / contract',
      choose: 'Record this loss',
      cols: ['name', 'contract_id', 'proposed_start', 'propo_value', 'risk', 'state'],
      domain: [['state', 'in', ['draft', 'quoted']]],
      empty: 'No renewal is open. A renewal is drafted at the contract lead time or from Renewals & Auto-Renew.'
    },
    saveAction: {
      method: 'action_mark_lost', label: 'Record as Lost',
      done: 'Renewal recorded as lost, with its churn reason',
      kwargs: { reason: 'churn_reason', competitor: 'competitor', winback: 'winback_eligible', note: 'lost_note' }
    },
    tabs: [
      { id: 'churn', label: '1. Churn Reason', bn: '১. হারানোর কারণ', icon: '📉', badge: '6' }
    ],
    sections: [
      { tab: 'churn', title: 'Step 2 of 2: Why It Was Lost',
        note: 'A move to a competitor names the competitor. A win-back candidate is fed to Marketing (M35) for a win-back campaign.',
        fields: [
          /* readonly for the generic write; INPUTS here because saveAction
           * carries them to action_mark_lost */
          { name: 'churn_reason', label: 'Churn Reason', required: true, readonly: true },
          { name: 'competitor', label: 'Competitor', readonly: true },
          { name: 'winback_eligible', label: 'Win-Back Candidate', readonly: true },
          { name: 'lost_note', label: 'Loss Note', type: 'text', readonly: true },
          { name: 'contract_id', label: 'Contract', readonly: true },
          { name: 'propo_value', label: 'Proposed Value', readonly: true }
        ] }
    ] },

  'M08-form-termination': {
    kind: 'model_form',
    model: 'fix.contract.termination',
    title: 'Contract Suspension / Termination',
    back: 'M08-termination',
    status: { field: 'state' },
    tabs: [
      { id: 'notice', label: '1. Termination Notice', bn: '১. সমাপ্তির নোটিশ', icon: '📄', badge: '4' },
      { id: 'timeline', label: '2. Effective Date & Notice Check', bn: '২. কার্যকর তারিখ ও নোটিশ', icon: '📅', badge: '2' },
      { id: 'dofa_governance', label: '3. DOFA Governance Gate', bn: '৩. ডোফা অনুমোদন গেট', icon: '🛡️', badge: '3' }
    ],
    sections: [
      { tab: 'notice', title: 'Notice Identification & Cause', note: 'A suspension or termination notice with its statutory grounds.',
        fields: [
          { name: 'name', required: true, label: 'Notice Name / Reference' },
          { name: 'contract_id', required: true, label: 'Contract (in force or suspended)', domain: [['state', 'in', ['active', 'expiring', 'suspended']]] },
          { name: 'kind', required: true, label: 'Action Kind' },
          { name: 'reason', required: true, label: 'Termination Grounds / Reason' }
        ] },
      { tab: 'timeline', title: 'Statutory Notice & Effective Timing', fields: [
          { name: 'effective_date', required: true, label: 'Effective Date' },
          { name: 'penalty_amount', label: 'Penalty / Break Fee (BDT)' },
          { name: 'notice_ok', label: 'Notice Period Satisfied (computed)', readonly: true }
        ] },
      { tab: 'dofa_governance', title: 'DOFA Approval & Execution Gate', note: 'Mandatory tier escalation under financial delegation rules.',
        fields: [
          { name: 'dofa_tier', label: 'DOFA Tier (derived from the amount)', readonly: true },
          { name: 'dofa_justification', label: 'DOFA Justification', type: 'text' },
          { name: 'dofa_approved', label: 'DOFA Sign-off Completed', readonly: true },
          { name: 'dofa_approved_by', label: 'Approved By', readonly: true },
          { name: 'state', label: 'Execution State', readonly: true }
        ] }
    ]
  },

  /* ===== M08 capture audit pass 2 (2026-11-18) =====
   * Every page had a "+ New" after 13 Nov, but measured against the M08 spec
   * several captured the wrong record and the records the spec asks a person
   * to enter had no model: the PM / calibration plan (page 6 made one ad-hoc
   * visit), coverage by asset type or site, entitlement top-ups and the
   * movement ledger, the service credit scheme, disputes with legal hold, the
   * declared treatment of a suspended period, and the wet-ink signature
   * (activation demanded an e-signature envelope, so a contract signed on
   * paper could never go live). */

  /* 6 PM Schedules: FR-CTR-031/032. The plan is the schedule; the visits
   * are generated from it at activation (or from today when a manager adds a
   * plan to a contract in force). */
  'M08-pm-plans': { kind: 'model_list', model: 'fix.contract.pm.plan',
    cols: ['name', 'contract_id', 'schedule_type', 'device_id', 'interval_months', 'first_due', 'lead_days', 'access_window', 'visit_count', 'contract_state'] },
  'M08-form-pmplan': { kind: 'model_form', model: 'fix.contract.pm.plan',
    title: 'PM / Calibration Plan', back: 'M08-pm-plans',
    lines: {
      field: 'visit_ids',
      readonlyGrid: true,
      title: 'Visits Generated from this Plan',
      note: 'Generated when the contract is activated (or from today for a plan added to a contract in force); dispatched from PM & Calibration Schedules.',
      fields: [
        { name: 'scheduled_date', label: 'Visit Date', readonly: true },
        { name: 'dispatch_from', label: 'Dispatch From', readonly: true },
        { name: 'device_id', label: 'Asset', readonly: true },
        { name: 'state', label: 'Status', readonly: true }
      ]
    },
    newLabel: 'Set a PM / Calibration Plan',
    tabs: [
      { id: 'plan', label: '1. What & How Often', bn: '১. কী ও কতবার', icon: '📅', badge: '6' },
      { id: 'site', label: '2. Lead Time & Site Access', bn: '২. অগ্রিম সময় ও সাইট', icon: '🔑', badge: '3' },
      { id: 'docs', label: '3. Documents', bn: '৩. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'plan', title: 'The Preventive, Calibration or Inspection Schedule',
        note: 'Set while the contract is a draft: activation generates every visit of the term from it. On a contract in force a Contract Manager may add a plan (its visits start today) or retire one (its future visits are skipped). Without a plan, the family\'s standard interval applies.',
        fields: [
          { name: 'contract_id', label: 'Contract', required: true, domain: [['state', 'not in', ['expired', 'terminated']]] },
          { name: 'name', label: 'Plan Name', required: true },
          { name: 'schedule_type', label: 'Type', required: true },
          { name: 'device_id', label: 'Asset (blank = every covered asset)' },
          { name: 'interval_months', label: 'Every (months)', required: true },
          { name: 'first_due', label: 'First Visit Due (blank = one interval after the start)' }
        ] },
      { tab: 'site', title: 'Lead Time & Site Access', fields: [
        { name: 'lead_days', label: 'Dispatch Lead Time (days)' },
        { name: 'access_window', label: 'Site Access Window' },
        { name: 'active', label: 'Active (untick to retire the plan)' }
      ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'Calibration certificates, site access letters and the schedule annex attach here; the checksummed repository (fix.document, M24) is the estate evidence path.', fields: [] }
    ] },

  /* 3 Coverage Scope: FR-CTR-014, BRU-CTR-01. Cover by asset type, brand or
   * site where the customer's estate is fluid; an AMC contract activates
   * only with listed assets or a rule. */
  'M08-coverage-rules': { kind: 'model_list', model: 'fix.contract.coverage.rule',
    cols: ['contract_id', 'device_type', 'brand_id', 'site_partner_id', 'cover_from', 'cover_to', 'note', 'contract_state'] },
  'M08-form-covrule': { kind: 'model_form', model: 'fix.contract.coverage.rule',
    title: 'Coverage Rule', back: 'M08-coverage-rules',
    tabs: [
      { id: 'rule', label: '1. What Is Covered', bn: '১. কী কভার', icon: '🛡️', badge: '5' },
      { id: 'window', label: '2. Cover Window', bn: '২. কভারের সময়', icon: '📅', badge: '2' },
      { id: 'docs', label: '3. Documents', bn: '৩. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'rule', title: 'Every Asset of the Customer That Matches',
        note: 'Draft contracts only. Name at least one of asset type, brand or site; an asset matches when it belongs to the customer and fits every condition named. Listed assets are set on Attach / Detach Covered Assets.',
        fields: [
          { name: 'contract_id', label: 'Contract (draft)', required: true, domain: [['state', '=', 'draft']] },
          { name: 'device_type', label: 'Asset Type' },
          { name: 'brand_id', label: 'Brand' },
          { name: 'site_partner_id', label: 'Site / Department (an address of the customer)' },
          { name: 'note', label: 'Rule Wording (as in the contract)' }
        ] },
      { tab: 'window', title: 'Cover Window', note: 'Blank = the whole contract term.', fields: [
        { name: 'cover_from', label: 'Cover From' },
        { name: 'cover_to', label: 'Cover To' }
      ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'The coverage schedule or site list the rule comes from attaches here.', fields: [] }
    ] },

  /* 4 Entitlement Engine: FR-CTR-020/022, T-01. A top-up is the live
   * contract's capture (a draft's entitlement is simply edited); the ledger
   * is written by the engine. */
  'M08-topups': { kind: 'model_list', model: 'fix.contract.entitlement.topup', stateField: 'state',
    cols: ['name', 'contract_id', 'entitlement_id', 'quantity', 'amount', 'customer_reference', 'requested_by', 'decided_by', 'state'],
    actions: [
      { m: 'action_submit', l: 'Submit to the Contract Manager', states: ['draft'] },
      { m: 'action_apply', l: 'Apply Top-Up (Contract Manager)', states: ['submitted'] },
      { m: 'action_reject', l: 'Reject (Contract Manager)', states: ['submitted'], ask: 'Why is the top-up rejected?', kwarg: 'reason' }
    ] },
  'M08-form-topup': { kind: 'model_form', model: 'fix.contract.entitlement.topup',
    title: 'Entitlement Top-Up', back: 'M08-topups',
    newLabel: 'Top Up an Entitlement',
    status: { field: 'state' },
    tabs: [
      { id: 'topup', label: '1. Top-Up', bn: '১. টপ-আপ', icon: '➕', badge: '6' },
      { id: 'decision', label: '2. Decision', bn: '২. সিদ্ধান্ত', icon: '✅', badge: '4' },
      { id: 'docs', label: '3. Documents', bn: '৩. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'topup', title: 'Additional Entitlement Sold Mid-Term',
        note: 'For a contract in force: the customer accepted a quotation or sent a purchase order. Submit it; a Contract Manager who did not raise it applies it, the balance grows and the ledger records it. An unlimited entitlement is not topped up.',
        fields: [
          { name: 'name', label: 'Top-Up Reference', required: true },
          { name: 'entitlement_id', label: 'Entitlement', required: true, domain: [['contract_state', 'in', ['active', 'expiring']], ['quantity_included', '>', 0]] },
          { name: 'quantity', label: 'Additional Quantity', required: true },
          { name: 'customer_reference', label: 'Customer Acceptance (quotation / PO no.)', required: true },
          { name: 'amount', label: 'Price Charged (BDT)' },
          { name: 'reason', label: 'Why', type: 'text' }
        ] },
      { tab: 'decision', title: 'Decision', fields: [
        { name: 'state', label: 'Status', readonly: true },
        { name: 'requested_by', label: 'Raised By', readonly: true },
        { name: 'decided_by', label: 'Decided By', readonly: true },
        { name: 'reject_reason', label: 'Rejection Reason', readonly: true }
      ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'The accepted quotation or the customer purchase order attaches here.', fields: [] }
    ] },
  'M08-ledger': { kind: 'model_list', model: 'fix.contract.entitlement.movement', create: false,
    empty: 'No movement yet: entitlements are granted when a contract is activated, then drawn down, restored and topped up by the engine.',
    cols: ['moved_on', 'contract_id', 'entitlement_id', 'movement_type', 'quantity', 'balance_after', 'source_ref', 'actor_id'] },

  /* 5 SLA & Service Credits: FR-CTR-028. What a breach earns the customer,
   * by type, priority, frequency and cap - a term of the contract. The
   * credit itself is computed and approved (M05), never typed here. */
  'M08-credit-schemes': { kind: 'model_list', model: 'fix.contract.credit.scheme',
    cols: ['contract_id', 'breach_type', 'priority', 'credit_basis', 'credit_value', 'cumulative_rule', 'cap_pct', 'note', 'contract_state'] },
  'M08-form-creditscheme': { kind: 'model_form', model: 'fix.contract.credit.scheme',
    title: 'Service Credit Rule', back: 'M08-credit-schemes',
    newLabel: 'Add a Service Credit Rule',
    tabs: [
      { id: 'breach', label: '1. Breach', bn: '১. লঙ্ঘন', icon: '⏱️', badge: '3' },
      { id: 'credit', label: '2. Credit & Cap', bn: '২. ক্রেডিট ও সীমা', icon: '💳', badge: '5' },
      { id: 'docs', label: '3. Documents', bn: '৩. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'breach', title: 'Which Breach',
        note: 'Draft contracts only: the credit scheme is a term of the contract.',
        fields: [
          { name: 'contract_id', label: 'Contract (draft)', required: true, domain: [['state', '=', 'draft']] },
          { name: 'breach_type', label: 'Breach Type', required: true },
          { name: 'priority', label: 'Priority', required: true }
        ] },
      { tab: 'credit', title: 'What It Earns',
        note: 'Escalating: the second breach in a period earns twice the credit, the third three times. The cap bounds what this rule can credit in one period.',
        fields: [
          { name: 'credit_basis', label: 'Credit Basis', required: true },
          { name: 'credit_value', label: 'Credit per Breach (% or BDT)', required: true },
          { name: 'cumulative_rule', label: 'Repeated Breaches', required: true },
          { name: 'cap_pct', label: 'Cap (% of the period fee)', required: true },
          { name: 'note', label: 'Contract Clause' }
        ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'The SLA schedule or credit clause of the agreement attaches here.', fields: [] }
    ] },

  /* 9 Churn & Win-Back: FR-CTR-043, BRU-CTR-12. While a dispute is open the
   * contract's documents are on legal hold (M24 register) and it neither
   * auto-renews nor escalates. */
  'M08-disputes': { kind: 'model_list', model: 'fix.contract.dispute', stateField: 'state',
    cols: ['name', 'contract_id', 'raised_by_party', 'opened_on', 'state', 'resolved_by', 'resolved_on'],
    actions: [
      { m: 'action_resolve', l: 'Resolve (Contract Manager)', states: ['open'], ask: 'How was the dispute resolved?', kwarg: 'resolution' }
    ] },
  'M08-form-dispute': { kind: 'model_form', model: 'fix.contract.dispute',
    title: 'Contract Dispute', back: 'M08-disputes',
    newLabel: 'Flag a Contract Dispute',
    status: { field: 'state' },
    tabs: [
      { id: 'dispute', label: '1. Dispute', bn: '১. বিরোধ', icon: '⚖️', badge: '5' },
      { id: 'outcome', label: '2. Hold & Outcome', bn: '২. স্থগিতাদেশ ও ফলাফল', icon: '🔒', badge: '4' },
      { id: 'docs', label: '3. Documents', bn: '৩. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'dispute', title: 'What Is Disputed',
        note: 'On save the contract\'s documents go on legal hold and the contract stops auto-renewing and escalating until a Contract Manager who did not open the dispute resolves it.',
        fields: [
          { name: 'contract_id', label: 'Contract', required: true, domain: [['state', '!=', 'draft']] },
          { name: 'name', label: 'Dispute', required: true },
          { name: 'raised_by_party', label: 'Raised By', required: true },
          { name: 'opened_on', label: 'Opened On', required: true },
          { name: 'description', label: 'What Is Disputed', type: 'text', required: true }
        ] },
      { tab: 'outcome', title: 'Legal Hold & Outcome', fields: [
        { name: 'held_document_ids', label: 'Documents on Legal Hold', readonly: true },
        { name: 'state', label: 'Status', readonly: true },
        { name: 'resolution', label: 'Resolution', readonly: true },
        { name: 'resolved_by', label: 'Resolved By', readonly: true }
      ] },
      { tab: 'docs', title: 'Documents & Evidence', note: 'Correspondence, job cards and other evidence of the dispute attach here; the contract documents themselves are on legal hold.', fields: [] }
    ] },

  /* 9 Churn & Win-Back: FR-CTR-040. A suspended contract resumes with the
   * treatment of the suspended period declared - and applied. */
  'M08-form-reinstate': { kind: 'model_form', model: 'fix.contract',
    title: 'Reinstate a Suspended Contract', back: 'M08-contracts',
    newLabel: 'Reinstate a Suspended Contract',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the suspended contract',
      note: 'Contracts suspended for non-payment, a customer request or a dispute.',
      search: 'Search contract / customer',
      choose: 'Reinstate this contract',
      cols: ['code', 'name', 'customer_id', 'suspended_on', 'date_end'],
      domain: [['state', '=', 'suspended']],
      empty: 'No contract is suspended.'
    },
    saveAction: {
      method: 'action_resume', label: 'Reinstate',
      done: 'Contract reinstated with the declared treatment',
      kwargs: { treatment: 'reinstatement_treatment', note: 'reinstatement_note' }
    },
    tabs: [
      { id: 'treatment', label: '1. Suspended Period', bn: '১. স্থগিত সময়', icon: '▶️', badge: '2' },
      { id: 'contract', label: '2. Contract', bn: '২. চুক্তি', icon: '📜', badge: '5' }
    ],
    sections: [
      { tab: 'treatment', title: 'Step 2 of 2: How the Suspended Days Are Treated',
        note: 'Needs the Contract Manager role. Restored extends the term by the suspended days; Forfeited leaves the term as it is; Prorated reduces each counted entitlement for the suspended days (the ledger records it).',
        fields: [
          /* readonly for the generic write; INPUTS here because saveAction
           * carries them to action_resume */
          { name: 'reinstatement_treatment', label: 'Treatment of the Suspended Period', required: true, readonly: true },
          { name: 'reinstatement_note', label: 'Note', type: 'text', readonly: true }
        ] },
      { tab: 'contract', title: 'Contract', fields: [
        { name: 'code', label: 'Contract No.', readonly: true },
        { name: 'name', label: 'Contract Title', readonly: true },
        { name: 'customer_id', label: 'Customer', readonly: true },
        { name: 'suspended_on', label: 'Suspended Since', readonly: true },
        { name: 'date_end', label: 'Term Ends', readonly: true }
      ] }
    ] },

  /* 11 Documents & Signature: FR-CTR-011. A contract signed in ink is
   * activated on its scanned original, checked by a second officer. */
  'M08-form-wetverify': { kind: 'model_form', model: 'fix.contract',
    title: 'Verify a Wet-Ink Signature', back: 'M08-contracts',
    newLabel: 'Verify a Wet-Ink Signature',
    status: { field: 'state' },
    pickRecord: {
      label: 'Step 1 of 2: choose the contract whose signed original you checked',
      note: 'Contracts signed in ink whose scanned original is not verified yet.',
      search: 'Search contract / customer',
      choose: 'Verify this signature',
      cols: ['code', 'name', 'customer_id', 'wet_signed_on', 'wet_signature_recorded_by', 'state'],
      domain: [['signature_method', '=', 'wet'], ['wet_signature_verified_by', '=', false], ['state', 'in', ['draft', 'pending_approval', 'pending_signature']]],
      empty: 'No ink-signed contract is waiting for verification. Record the scan on Record Signature & Stamp Duty first.'
    },
    saveAction: {
      method: 'action_verify_wet_signature', label: 'Confirm the Signature',
      done: 'Wet-ink signature verified: the contract can be activated',
      kwargs: {}
    },
    tabs: [
      { id: 'check', label: '1. Signed Original', bn: '১. স্বাক্ষরিত মূল কপি', icon: '✍️', badge: '6' }
    ],
    sections: [
      { tab: 'check', title: 'Step 2 of 2: Check the Scan Against the Original',
        note: 'The customer\'s signature, the date and every page initialled. Whoever recorded the scan cannot verify it.',
        fields: [
          { name: 'code', label: 'Contract No.', readonly: true },
          { name: 'customer_id', label: 'Customer', readonly: true },
          { name: 'wet_signed_on', label: 'Signed On', readonly: true },
          { name: 'wet_signed_document_id', label: 'Signed Original (M24)', readonly: true },
          { name: 'wet_signature_recorded_by', label: 'Recorded By', readonly: true },
          { name: 'annual_value', label: 'Annual Value (BDT)', readonly: true }
        ] }
    ] }
};

export const REPORT_ROUTES = {
  'M08:Contract Base Movement': 'M08-rpt-base',
  'M08:Entitlement Consumption by Client': 'M08-rpt-entitle',
  'M08:SLA Credit Register': 'M08-rpt-sla',
  'M08:PM Compliance Report': 'M08-rpt-pm',
  'M08:Renewal Pipeline & Risk': 'M08-rpt-renew',
  'M08:Contract P&L': 'M08-rpt-pnl'
};

export const FORM_MODELS = {
  'M08:Contract (5 families)': 'fix.contract',
  'M08:Amendment': 'fix.contract.amendment',
  'M08:Asset Attach/Detach': 'fix.contract',
  'M08:Renewal Quote': 'fix.contract.renewal',
  'M08:PM Schedule': 'fix.contract.pm.plan',
  'M08:Entitlement': 'fix.contract.entitlement',
  'M08:Submit for Value Approval': 'fix.contract',
  'M08:Legal Review': 'fix.contract',
  'M08:SLA Credit': 'fix.msp.sla.credit',
  'M08:Suspension / Termination Notice': 'fix.contract.termination',
  'M08:Price Revision': 'fix.contract.amendment',
  'M08:Signature & Stamp Duty': 'fix.contract',
  'M08:Signature Envelope': 'fix.esignature.envelope',
  'M08:Stamp Duty Rate': 'fix.stamp.duty.schedule',
  'M08:Contract Party': 'fix.contract.party',
  'M08:Coverage Exclusion': 'fix.contract.exclusion',
  'M08:Contract Obligation': 'fix.contract.obligation',
  'M08:Lost Renewal': 'fix.contract.renewal',
  'M08:Coverage Rule': 'fix.contract.coverage.rule',
  'M08:Entitlement Top-Up': 'fix.contract.entitlement.topup',
  'M08:Service Credit Scheme': 'fix.contract.credit.scheme',
  'M08:PM Visit': 'fix.contract.pm.visit',
  'M08:Contract Dispute': 'fix.contract.dispute',
  'M08:Reinstatement': 'fix.contract',
  'M08:Wet-Ink Signature Verification': 'fix.contract'
};

export const FORM_CHIPS = {
  'M08:Contract (5 families)': 'M08-record',
  'M08:Amendment': 'M08-form-amendment',
  /* the registry's attach/detach form sets the contract's covered assets;
   * it opened the entitlement form until the 2026-11-13 capture audit */
  'M08:Asset Attach/Detach': 'M08-form-coverage',
  'M08:Renewal Quote': 'M08-form-renewal',
  /* the PM schedule is the plan the visits come from (pass 2); a single
   * extra visit is the PM Visit form */
  'M08:PM Schedule': 'M08-form-pmplan',
  'M08:PM Visit': 'M08-form-pm',
  'M08:Coverage Rule': 'M08-form-covrule',
  'M08:Entitlement Top-Up': 'M08-form-topup',
  'M08:Service Credit Scheme': 'M08-form-creditscheme',
  'M08:Contract Dispute': 'M08-form-dispute',
  'M08:Reinstatement': 'M08-form-reinstate',
  'M08:Wet-Ink Signature Verification': 'M08-form-wetverify',
  'M08:Entitlement': 'M08-form-entitlement',
  'M08:Submit for Value Approval': 'M08-form-submit',
  'M08:Legal Review': 'M08-form-legal',
  'M08:Suspension / Termination Notice': 'M08-form-termination',
  'M08:Price Revision': 'M08-form-price',
  'M08:Signature & Stamp Duty': 'M08-form-signature',
  'M08:Stamp Duty Rate': 'M08-form-stampduty',
  'M08:Contract Party': 'M08-form-party',
  'M08:Coverage Exclusion': 'M08-form-exclusion',
  'M08:Contract Obligation': 'M08-form-obligation',
  'M08:Lost Renewal': 'M08-form-lost',
  /* records other modules master open THEIR forms: the SLA credit is
   * computed and approved in M05, the signature envelope lives in M24 */
  'M08:SLA Credit': 'M05-form-credit',
  'M08:Signature Envelope': 'M24-form-envelope',
  'M08:__by_model__': {
    'fix.contract': 'M08-record',
    'fix.contract.amendment': 'M08-form-amendment',
    'fix.contract.entitlement': 'M08-form-entitlement',
    'fix.contract.renewal': 'M08-form-renewal',
    'fix.contract.pm.visit': 'M08-form-pm',
    'fix.contract.termination': 'M08-form-termination',
    'fix.contract.party': 'M08-form-party',
    'fix.contract.exclusion': 'M08-form-exclusion',
    'fix.contract.obligation': 'M08-form-obligation',
    'fix.contract.pm.plan': 'M08-form-pmplan',
    'fix.contract.coverage.rule': 'M08-form-covrule',
    'fix.contract.entitlement.topup': 'M08-form-topup',
    'fix.contract.credit.scheme': 'M08-form-creditscheme',
    'fix.contract.dispute': 'M08-form-dispute'
  },
  'M08:__by_screen__': {
    'M08-contracts': 'M08-record',
    'M08-amend': 'M08-form-amendment',
    'M08-entitle': 'M08-form-entitlement',
    'M08-renewals': 'M08-form-renewal',
    'M08-pm': 'M08-form-pm',
    'M08-stampduty': 'M08-form-stampduty',
    'M08-termination': 'M08-form-termination',
    'M08-parties': 'M08-form-party',
    'M08-exclusions': 'M08-form-exclusion',
    'M08-obligations': 'M08-form-obligation',
    'M08-pm-plans': 'M08-form-pmplan',
    'M08-coverage-rules': 'M08-form-covrule',
    'M08-topups': 'M08-form-topup',
    'M08-credit-schemes': 'M08-form-creditscheme',
    'M08-disputes': 'M08-form-dispute'
  }
};

export const CREATE = {
  M08: { screen: 'M08-record', model: 'fix.contract', label: 'Contract' }
};
