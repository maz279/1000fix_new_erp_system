/** @odoo-module **/
/* A04 · Commercial & Revenue — M08 Contract Lifecycle (AMC) (v2 rebuild).
 * Registry-faithful: 5 groups / 16 screens / 6 reports / 5 forms / freg 108.
 * Contracts, entitlements and PM visits are real; amendments, renewals and
 * terminations are new. Contract P&L is value-after-SLA-credits (no invented
 * cost); renewal risk is a stated derivation, not a model score. */

export const MODULE = {
  area: 'A04', code: 'M08', en: 'Contract Lifecycle (AMC)', title: 'M08 · Contract Lifecycle (AMC)',
  bn: 'চুক্তি লাইফসাইকেল', icon: '📝',
  desc: 'AMC contracts across 14 product families, coverage and entitlement consumption, SLA credits, PM schedules, amendments, renewals and churn, pricing and profitability.',
  kpis: [
    { l: 'Active Contracts', m: 'active_contracts' },
    { l: 'Contract Base Value', m: 'contract_base_value', prefix: '৳ ' },
    { l: 'Renewal Rate', m: 'renewal_rate', suffix: '%' },
    { l: 'Neg-Margin Contracts', m: 'neg_margin_contracts' },
    { l: 'Entitlement Utilisation', m: 'entitlement_utilisation', suffix: '%' },
    { l: 'PM Visits Due (7d)', m: 'pm_visits_due_7d' }
  ],
  groups: [
    { en: 'Contract Register', screens: [
      { id: 'M08-contracts', en: 'Contracts', bn: 'চুক্তি', t: 'g' },
      { id: 'M08-form-contract', en: 'Contract Record', bn: 'চুক্তি রেকর্ড', t: 'f' },
      { id: 'M08-families', en: 'Contract Product Families', bn: 'পণ্য পরিবার', t: 'g' },
      { id: 'M08-master', en: 'Master Agreements', bn: 'মাস্টার চুক্তি', t: 'g' }
    ]},
    { en: 'Coverage & Entitlement', screens: [
      { id: 'M08-scope', en: 'Covered Assets & Sites', bn: 'কভারেজ', t: 'g' },
      { id: 'M08-entitle', en: 'Entitlement & Consumption', bn: 'এনটাইটেলমেন্ট', t: 'g' },
      { id: 'M08-balance', en: 'Balances, Carry-Over, Top-Up', bn: 'ব্যালেন্স', t: 'g' }
    ]},
    { en: 'Service Commitments', screens: [
      { id: 'M08-sla', en: 'Contract SLA & Credits', bn: 'SLA ক্রেডিট', t: 'g' },
      { id: 'M08-pm', en: 'PM & Calibration Schedules', bn: 'পিএম শিডিউল', t: 'g' },
      { id: 'M08-auto-work', en: 'Contract-Driven Work', bn: 'চুক্তি-চালিত কাজ', t: 'g' }
    ]},
    { en: 'Change & Renewal', screens: [
      { id: 'M08-amend', en: 'Amendments & Variations', bn: 'সংশোধনী', t: 'g' },
      { id: 'M08-renewals', en: 'Renewals & Auto-Renew', bn: 'নবায়ন', t: 'c' },
      { id: 'M08-termination', en: 'Suspension / Termination', bn: 'স্থগিত / বাতিল', t: 'g' },
      { id: 'M08-stampduty', en: 'Stamp Duty Schedule I', bn: 'স্ট্যাম্প ডিউটি তালিকা', t: 'g' },
      { id: 'M08-churn', en: 'Churn & Win-Back', bn: 'চার্ন ও উইন-ব্যাক', t: 'r' }
    ]},
    { en: 'Financials', screens: [
      { id: 'M08-pricing', en: 'Contract Pricing Link', bn: 'মূল্য সংযোগ', t: 'g' },
      { id: 'M08-profit', en: 'Profitability & Alerts', bn: 'লাভজনকতা', t: 'r' }
    ]}
  ],
  reports: ['Contract Base Movement', 'Entitlement Consumption by Client', 'SLA Credit Register', 'PM Compliance Report', 'Renewal Pipeline & Risk', 'Contract P&L'],
  forms: ['Contract (14 families)', 'Amendment', 'Asset Attach/Detach', 'Renewal Quote', 'PM Schedule'],
  cross: ['M05 MSP', 'M01 Service Orders', 'M20 AR', 'M37 Catalogue'],
  freg: { src: 108, sub: [
    ['1', 'Template-Driven Creation', 12, { model: 'fix.contract', cols: ['name', 'customer_id', 'family', 'state', 'date_start', 'date_end', 'annual_value'], screens: ['M08-contracts'] }],
    ['2', 'Parties & Approval', 8, { model: 'fix.contract', cols: ['name', 'customer_id', 'family', 'state', 'date_start', 'date_end', 'annual_value'], screens: ['M08-master'] }],
    ['3', 'Coverage Scope', 10, { model: 'fix.contract.entitlement', cols: ['contract_id', 'device_id', 'entitlement_type', 'quantity_included', 'quantity_remaining'], screens: ['M08-scope', 'M08-entitle'] }],
    ['4', 'Entitlement Engine', 14, { model: 'fix.contract.entitlement', cols: ['contract_id', 'entitlement_type', 'quantity_included', 'quantity_consumed', 'quantity_remaining'], screens: ['M08-entitle', 'M08-balance'] }],
    ['5', 'SLA & Service Credits', 10, { model: 'fix.msp.sla.credit', cols: ['msp_contract_id', 'period_label', 'attainment_pct', 'breach_count', 'credit_amount'], screens: ['M08-sla', 'M08-rpt-sla'] }],
    ['6', 'PM Schedules', 9, { model: 'fix.contract.pm.visit', cols: ['contract_id', 'state'], screens: ['M08-pm', 'M08-rpt-pm'] }],
    ['7', 'Amendments', 8, { model: 'fix.contract.amendment', cols: ['contract_id', 'state'], screens: ['M08-amend'] }],
    ['8', 'Renewal Governance', 9, { model: 'fix.contract.renewal', cols: ['contract_id', 'state'], screens: ['M08-renewals', 'M08-rpt-renew'] }],
    ['9', 'Churn & Win-Back', 6, { model: 'fix.contract.termination', cols: ['contract_id', 'state'], screens: ['M08-termination', 'M08-churn'] }],
    ['10', 'Pricing & Profitability', 10, { model: 'fix.contract', cols: ['name', 'customer_id', 'annual_value', 'total_delivery_cost', 'contract_margin_pct'], screens: ['M08-pricing', 'M08-profit', 'M08-rpt-pnl', 'M08-contracts'] }],
    ['11', 'Documents & Signature', 7, { model: 'fix.contract', cols: ['name', 'state', 'esignature_envelope_id', 'has_signed_contract_doc', 'stamp_duty_cert_no'], screens: ['M08-rpt-base', 'M08-contracts'] }],
    ['12', 'Obligation Calendar', 5, { model: 'fix.contract.pm.visit', cols: ['contract_id', 'device_id', 'scheduled_date', 'service_order_id', 'state'], screens: ['M08-auto-work', 'M08-pm'] }]
  ] }
};

export const SCREENS = {
  // A04 build (2026-11-04) C3: the contract lifecycle runs by its actions.
  // The value is approved from the DOFA holder's M63 inbox (never here);
  // Legal and Finance decide only what they did not raise.
  'M08-contracts': { kind: 'model_list', model: 'fix.contract', stateField: 'state',
    cols: ['name', 'customer_id', 'family', 'date_start', 'date_end', 'annual_value', 'auto_renew', 'state', 'approval_state'],
    actions: [
      { m: 'action_request_approval', l: 'Submit for Value Approval (DOFA)', states: ['draft'], ask: 'Business justification (mandatory from Tier 2)', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Approval Request', states: ['pending_approval'] },
      { m: 'action_legal_review', l: 'Legal Review (Legal Reviewer)', states: ['pending_approval'], ask: 'Legal review note', kwarg: 'note' },
      { m: 'action_approve_stamp_exemption', l: 'Approve Stamp-Duty Exemption (Finance)', states: ['draft', 'pending_approval', 'pending_signature'] },
      { m: 'action_reset_to_draft', l: 'Reset to Draft', states: ['pending_approval', 'pending_signature'] },
      { m: 'action_activate', l: 'Activate (signed envelope required)', states: ['pending_signature'] },
      { m: 'action_renew', l: 'Draft Renewal Term', states: ['active', 'expiring', 'expired'] },
      { m: 'action_resume', l: 'Resume (Contract Manager)', states: ['suspended'] }
    ] },
  'M08-families': { kind: 'table_report', module: 'M08', report: 'contract_families', title: 'Contract Product Families', period: false },
  'M08-master': { kind: 'model_list', model: 'fix.contract', stateField: 'state',
    domain: [['state', '=', 'active']],
    cols: ['name', 'customer_id', 'family', 'annual_value', 'renewal_lead_days', 'date_end'] },
  'M08-scope': { kind: 'table_report', module: 'M08', report: 'scope_coverage', title: 'Covered Assets & Sites', period: false },
  'M08-entitle': { kind: 'model_list', model: 'fix.contract.entitlement',
    cols: ['contract_id', 'device_id', 'entitlement_type', 'quantity_included', 'quantity_consumed', 'quantity_remaining'] },
  'M08-balance': { kind: 'table_report', module: 'M08', report: 'entitlement_balance', title: 'Balances, Carry-Over, Top-Up', period: false },
  'M08-sla': { kind: 'table_report', module: 'M08', report: 'sla_credit_register', title: 'Contract SLA & Credits', period: false },
  'M08-pm': { kind: 'model_list', model: 'fix.contract.pm.visit', stateField: 'state',
    cols: ['contract_id', 'device_id', 'scheduled_date', 'service_order_id', 'state'],
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
      { m: 'action_cancel', l: 'Cancel Amendment', states: ['draft', 'submitted', 'approved'] }
    ] },
  'M08-renewals': { kind: 'model_list', model: 'fix.contract.renewal', stateField: 'state',
    cols: ['name', 'contract_id', 'proposed_start', 'proposed_end', 'propo_value', 'risk', 'state', 'renewal_contract_id'],
    actions: [
      { m: 'action_quote', l: 'Issue Renewal Quote', states: ['draft'] },
      { m: 'action_mark_won', l: 'Won: Draft the Next Term', states: ['quoted'] },
      { m: 'action_mark_lost', l: 'Lost', states: ['draft', 'quoted'] }
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
  'M08-form-contract': {
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
      { id: 'sla_visits', label: '3. Coverage, SLAs & Visits', bn: '৩. কাভারেজ ও এসএলএ', icon: '🛡️', badge: '4' },
      { id: 'statutory', label: '4. Stamp Duty & Compliance', bn: '৪. স্ট্যাম্প ও সম্মতি', icon: '⚖️', badge: '4' },
      { id: 'governance', label: '5. Governance & DOFA', bn: '৫. নবায়ন ও অনুমোদন', icon: '🏛️', badge: '2' },
      { id: 'vault', label: '6. Document Vault', bn: '৬. নথিপত্র', icon: '📁', badge: '2' }
    ],
    sections: [
      { tab: 'general', title: 'Contract Identity & Master Setup',
        note: 'Master commercial agreement across 14 product families under Bangladesh commercial laws.',
        fields: [
          { name: 'name', required: true, label: 'Contract Title' },
          { name: 'code', required: true, label: 'Contract Code', readonly: true },
          { name: 'customer_id', required: true, label: 'Enterprise Customer' },
          { name: 'family', required: true, label: 'Product Family' },
          { name: 'company_id', required: true, label: 'Operating Company' },
          { name: 'operating_unit_id', required: true, label: 'Operating Unit' },
          { name: 'state', label: 'Lifecycle Status', readonly: true },
          { name: 'template_id', label: 'Contract Template (Legal-signed)' }
        ] },
      { tab: 'financial', title: 'Commercial Value, Delivery Cost & Margins',
        fields: [
          { name: 'annual_value', required: true, label: 'Annual Contract Value (BDT)' },
          { name: 'total_delivery_cost', label: 'Direct Delivery & Service Cost (BDT)', readonly: true },
          { name: 'contract_margin_bdt', label: 'Gross Contract Margin (BDT)', readonly: true },
          { name: 'contract_margin_pct', label: 'Gross Margin (%)', readonly: true },
          { name: 'escalation_pct', label: 'Annual Escalation Rate (%)' },
          { name: 'currency_id', label: 'Currency' },
          { name: 'amendment_version', label: 'Amendment Version', readonly: true },
          { name: 'billed_through_date', label: 'Billed Through', readonly: true }
        ] },
      { tab: 'sla_visits', title: 'Service Commitments & PM Visits',
        fields: [
          { name: 'date_start', required: true, label: 'Coverage Start Date' },
          { name: 'date_end', required: true, label: 'Coverage End Date' },
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
          { name: 'esignature_envelope_id', label: 'Kernel E-Signature Envelope (M24)' },
          { name: 'dofa_tier_required', label: 'DOFA Tier (from the value)', readonly: true },
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

  'M08-form-amendment': {
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
          { name: 'contract_id', required: true, label: 'Contract' },
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
          { name: 'value_after', label: 'Value After', readonly: true }
        ] }
    ]
  },
  'M08-form-entitlement': { kind: 'model_form', model: 'fix.contract.entitlement',
    title: 'Asset Attach / Detach', back: 'M08-entitle',
    tabs: [
      { id: 'general', label: '1. General', bn: '১. সাধারণ তথ্য' },
      { id: 'schedule', label: '2. Schedule', bn: '২. সময়সূচি' },
      { id: 'relations', label: '3. Links', bn: '৩. সংযোগ' },
      { id: 'audit', label: '4. System Audit', bn: '৪. সিস্টেম অডিট' },
      { id: 'docs', label: '5. Documents', bn: '৫. নথি ও প্রমাণক' }
    ],
    sections: [
      { tab: 'general', title: '1. General', fields: [
        { name: 'entitlement_type', label: 'Entitlement Type', required: true },
        { name: 'quantity_included', label: 'Included', required: true },
        { name: 'quantity_consumed', label: 'Consumed', readonly: true },
        { name: 'quantity_remaining', label: 'Remaining', readonly: true }
      ] },
      { tab: 'schedule', title: '3. Schedule', fields: [
        { name: 'my_activity_date_deadline', label: 'My Activity Deadline', readonly: true }
      ] },
      { tab: 'relations', title: '4. Links', fields: [
        { name: 'contract_id', label: 'Contract', required: true },
        { name: 'device_id', label: 'Device' }
      ] },
      { tab: 'audit', title: '8. System Audit', fields: [
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
        { name: 'contract_id', label: 'Contract', required: true },
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
          { name: 'contract_id', required: true, label: 'Contract' },
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
  }
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
  'M08:Contract (14 families)': 'fix.contract',
  'M08:Amendment': 'fix.contract.amendment',
  'M08:Asset Attach/Detach': 'fix.contract.entitlement',
  'M08:Renewal Quote': 'fix.contract.renewal',
  'M08:PM Schedule': 'fix.contract.pm.visit'
};

export const FORM_CHIPS = {
  'M08:Contract (14 families)': 'M08-form-contract',
  'M08:Amendment': 'M08-form-amendment',
  'M08:Asset Attach/Detach': 'M08-form-entitlement',
  'M08:Renewal Quote': 'M08-form-renewal',
  'M08:PM Schedule': 'M08-form-pm',
  'M08:__by_model__': {
    'fix.contract': 'M08-form-contract',
    'fix.contract.amendment': 'M08-form-amendment',
    'fix.contract.entitlement': 'M08-form-entitlement',
    'fix.contract.renewal': 'M08-form-renewal',
    'fix.contract.pm.visit': 'M08-form-pm',
    'fix.contract.termination': 'M08-form-termination'
  },
  'M08:__by_screen__': {
    'M08-contracts': 'M08-form-contract',
    'M08-amend': 'M08-form-amendment',
    'M08-entitle': 'M08-form-entitlement',
    'M08-renewals': 'M08-form-renewal',
    'M08-pm': 'M08-form-pm',
    'M08-stampduty': 'M08-form-stampduty',
    'M08-termination': 'M08-form-termination'
  }
};

export const CREATE = {
  M08: { screen: 'M08-form-contract', model: 'fix.contract', label: 'Contract' }
};
