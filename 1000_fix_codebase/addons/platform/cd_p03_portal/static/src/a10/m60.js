/** @odoo-module **/
/* A10 · Governance, Risk & Quality — M60 Governance, Risk & Compliance.
 * Registry-faithful: 4 groups / 13 screens / 5 reports / 6 forms / freg 70.
 *
 * Capture audit 2026-11-18: pages 3 (SoD & Authority), 6 (Legal & IP) and
 * 7 (PDPA) offered no form chip; page 1 could not record an assessment, a
 * treatment action or a realised event; page 4 had no occurrence to
 * discharge with evidence; page 5 no attestation or exception; page 7 no
 * record of processing, transfer register, breach register or PIA, and its
 * one form ("PDPA Register Entry") was a data-subject request. Each page now
 * captures every record it covers - M29's SoD test and exception, M24's
 * legal hold and retention policy are reused as chips, not duplicated. */

export const MODULE = {
  area: 'A10', code: 'M60', en: 'Governance, Risk & Compliance', title: 'M60 · Governance, Risk & Compliance',
  bn: 'শাসন, ঝুঁকি ও সম্মতি', icon: '🛡️',
  desc: 'Enterprise risk register and appetite aggregation, the internal control framework with testing, segregation-of-duties rules, delegated authority, compliance obligations, the corporate licence register, policy governance and attestation, legal matters, PDPA requests and whistleblowing.',
  kpis: [
    { l: 'Risks Above Appetite', m: 'risks_above_appetite' },
    { l: 'Control Tests Due', m: 'control_tests_due' },
    { l: 'Licence Gaps', m: 'licence_gaps' },
    { l: 'Policy Attestations', m: 'policy_attestations' },
    { l: 'Legal Matters Open', m: 'legal_matters_open' },
    { l: 'DSRs Pending', m: 'dsr_pending' }
  ],
  groups: [
    { en: 'Record Coverage', screens: [
      { id: 'M60-compliance-framework', en: "Compliance Framework", bn: "Compliance Framework", t: 'g' }
    ]},
    { en: 'Risk', screens: [
      { id: 'M60-register', en: 'Enterprise Risk Register', bn: 'ঝুঁকি রেজিস্টার', t: 'g' },
      { id: 'M60-appetite-set', en: 'Risk Appetite', bn: 'ঝুঁকি ক্ষমতা নির্ধারণ', t: 'g' },
      { id: 'M60-appetite', en: 'Appetite & Aggregation', bn: 'ঝুঁকি ক্ষমতা', t: 'r' },
      { id: 'M60-assessments', en: 'Risk Assessments', bn: 'ঝুঁকি মূল্যায়ন', t: 'g' },
      { id: 'M60-treatments', en: 'Treatment Actions', bn: 'ঝুঁকি প্রতিকার', t: 'g' },
      { id: 'M60-events', en: 'Risk Events', bn: 'ঝুঁকি ঘটনা', t: 'g' }
    ]},
    { en: 'Controls', screens: [
      { id: 'M60-framework', en: 'Internal Control Framework', bn: 'অভ্যন্তরীণ নিয়ন্ত্রণ', t: 'g' },
      { id: 'M60-testing', en: 'Control Testing', bn: 'নিয়ন্ত্রণ পরীক্ষা', t: 'g' },
      { id: 'M60-sod', en: 'SoD Rules', bn: 'দায়িত্ব বিভাজন', t: 'g' },
      { id: 'M60-authority', en: 'Delegated Authority', bn: 'প্রতিনিধি ক্ষমতা', t: 'g' },
      { id: 'M60-sod-tests', en: 'SoD Test Runs', bn: 'দায়িত্ব বিভাজন পরীক্ষা', t: 'g' },
      { id: 'M60-sod-exceptions', en: 'SoD Exceptions', bn: 'দায়িত্ব বিভাজন ব্যতিক্রম', t: 'g' }
    ]},
    { en: 'Compliance', screens: [
      { id: 'M60-obligations', en: 'Obligation Register', bn: 'বাধ্যবাধকতা', t: 'g' },
      { id: 'M60-licences', en: 'Licence Register', bn: 'লাইসেন্স রেজিস্টার', t: 'g' },
      { id: 'M60-policies', en: 'Policy Governance', bn: 'নীতি শাসন', t: 'g' },
      { id: 'M60-occurrences', en: 'Obligation Calendar', bn: 'বাধ্যবাধকতা পঞ্জিকা', t: 'g' },
      { id: 'M60-reg-changes', en: 'Regulatory Changes', bn: 'নিয়ন্ত্রক পরিবর্তন', t: 'g' },
      { id: 'M60-attestations', en: 'Policy Attestations', bn: 'নীতি স্বীকৃতি', t: 'g' },
      { id: 'M60-policy-exceptions', en: 'Policy Exceptions', bn: 'নীতি ব্যতিক্রম', t: 'g' },
      { id: 'M60-retention', en: 'Retention Schedule', bn: 'সংরক্ষণ সূচি', t: 'g' }
    ]},
    { en: 'Legal & Data', screens: [
      { id: 'M60-legal', en: 'Legal Matters', bn: 'আইনি বিষয়', t: 'g' },
      { id: 'M60-pdpa', en: 'PDPA Governance', bn: 'পিডিপিএ শাসন', t: 'g' },
      { id: 'M60-whistle', en: 'Whistleblowing', bn: 'হুইসেলব্লোয়িং', t: 'g' },
      { id: 'M60-holds', en: 'Legal Holds', bn: 'আইনি আটক', t: 'g' },
      { id: 'M60-ip', en: 'IP Register', bn: 'মেধাস্বত্ব রেজিস্টার', t: 'g' },
      { id: 'M60-ropa', en: 'Records of Processing', bn: 'প্রক্রিয়াকরণ রেকর্ড', t: 'g' },
      { id: 'M60-transfers', en: 'Cross-Border Transfers', bn: 'আন্তঃসীমান্ত স্থানান্তর', t: 'g' },
      { id: 'M60-breaches', en: 'Breach Register', bn: 'লঙ্ঘন রেজিস্টার', t: 'g' },
      { id: 'M60-pias', en: 'Privacy Impact Assessments', bn: 'গোপনীয়তা প্রভাব মূল্যায়ন', t: 'g' }
    ]}
  ],
  reports: ['Risk Heat Map', 'Control Deficiency Log', 'Licence Expiry Register', 'Attestation Status', 'Board Risk Pack'],
  forms: ['Risk', 'Risk Appetite', 'Risk Assessment', 'Risk Treatment', 'Risk Event',
    'Internal Control', 'Control Test', 'SoD Rule', 'SoD Test Run', 'SoD Exception',
    'Compliance Obligation', 'Compliance Framework', 'Obligation Occurrence', 'Licence', 'Regulatory Change',
    'Policy', 'Policy Attestation', 'Policy Exception', 'Retention Policy',
    'Legal Matter', 'Place Legal Hold', 'IP Asset',
    'Data Subject Request', 'Processing Activity', 'Cross-Border Transfer', 'Data Breach', 'Privacy Impact Assessment',
    'Whistleblow Report'],
  cross: ['M23 QMS', 'M51 Tax', 'M24 Documents', 'M19 GL'],
  freg: { src: 70, sub: [
    ['1', 'Risk Register', 12, { model: 'fix.risk.register', cols: ['name', 'category', 'risk_score', 'residual_band', 'review_date', 'state'], screens: ['M60-register', 'M60-appetite-set', 'M60-assessments', 'M60-treatments', 'M60-events', 'M60-appetite'], reports: ['Risk Heat Map', 'Board Risk Pack'], forms: ['Risk', 'Risk Appetite', 'Risk Assessment', 'Risk Treatment', 'Risk Event'] }],
    ['2', 'Control Framework & Testing', 14, { model: 'fix.control', cols: ['control_code', 'name', 'control_type', 'is_key', 'frequency', 'test_result'], screens: ['M60-framework', 'M60-testing'], reports: ['Control Deficiency Log'], forms: ['Internal Control', 'Control Test'] }],
    ['3', 'SoD & Authority', 8, { model: 'fix.grc.sod.rule', cols: ['name', 'role_a', 'role_b', 'severity', 'enforced_by_id', 'state'], screens: ['M60-sod', 'M60-sod-tests', 'M60-sod-exceptions', 'M60-authority'], reports: [], forms: ['SoD Rule', 'SoD Test Run', 'SoD Exception'] }],
    ['4', 'Compliance Obligations', 9, { model: 'fix.compliance.obligation', cols: ['name', 'framework_id', 'clause_reference', 'owner_id', 'mandatory', 'compliance_status'], screens: ['M60-obligations', 'M60-compliance-framework', 'M60-occurrences', 'M60-licences', 'M60-reg-changes'], reports: ['Licence Expiry Register'], forms: ['Compliance Obligation', 'Compliance Framework', 'Obligation Occurrence', 'Licence', 'Regulatory Change'] }],
    ['5', 'Policy Governance', 6, { model: 'fix.grc.policy', cols: ['code', 'name', 'policy_type', 'review_due', 'attested_count', 'state'], screens: ['M60-policies', 'M60-attestations', 'M60-policy-exceptions', 'M60-retention'], reports: ['Attestation Status'], forms: ['Policy', 'Policy Attestation', 'Policy Exception', 'Retention Policy'] }],
    ['6', 'Legal & IP', 7, { model: 'fix.grc.legal', cols: ['name', 'matter_type', 'counterparty', 'opened_on', 'next_action_on', 'state'], screens: ['M60-legal', 'M60-holds', 'M60-ip'], reports: [], forms: ['Legal Matter', 'Place Legal Hold', 'IP Asset'] }],
    ['7', 'PDPA Governance', 9, { model: 'fix.grc.pdpa', cols: ['name', 'request_type', 'received_on', 'due_on', 'outcome'], screens: ['M60-pdpa', 'M60-ropa', 'M60-transfers', 'M60-breaches', 'M60-pias'], reports: [], forms: ['Data Subject Request', 'Processing Activity', 'Cross-Border Transfer', 'Data Breach', 'Privacy Impact Assessment'] }],
    ['8', 'Whistleblowing', 5, { model: 'fix.grc.whistle', cols: ['name', 'channel', 'category', 'reported_on', 'state'], screens: ['M60-whistle'], reports: [], forms: ['Whistleblow Report'] }]
  ] }
};

export const SCREENS = {
  'M60-register': { kind: 'model_list', model: 'fix.risk.register', stateField: 'state',
    cols: ['name', 'category', 'likelihood', 'impact', 'risk_score', 'owner_id', 'review_date', 'state', 'residual_score', 'residual_band', 'above_appetite', 'residual_accepted_by_id'],
    actions: [
      { m: 'action_accept_residual', l: 'Accept Residual',
        asks: [{ label: 'Why is this residual acceptable? (routed to the Delegated Authority Owner when it is above the stated appetite)', kwarg: 'justification' }] },
      { m: 'action_close', l: 'Close Risk' },
      { m: 'action_reopen', l: 'Reopen Risk' }
    ] },
  'M60-appetite-set': { kind: 'model_list', model: 'fix.risk.appetite',
    cols: ['category', 'max_residual_score', 'company_id', 'note'] },
  'M60-appetite': { kind: 'table_report', module: 'M60', report: 'risk_heat_map', title: 'Appetite & Aggregation', period: false },
  'M60-framework': { kind: 'model_list', model: 'fix.control',
    cols: ['control_code', 'name', 'control_type', 'nature', 'is_key', 'frequency', 'risk_id', 'owner_id', 'last_tested', 'test_result'],
    actions: [{ m: 'action_activate', l: 'Activate' }, { m: 'action_retire', l: 'Retire' }] },
  'M60-testing': { kind: 'model_list', model: 'fix.grc.control.test', stateField: 'result',
    cols: ['name', 'control_id', 'tested_on', 'tester_id', 'sample_size', 'exceptions', 'result'] },
  'M60-sod': { kind: 'model_list', model: 'fix.grc.sod.rule', stateField: 'state',
    cols: ['name', 'role_a', 'role_b', 'conflict_area', 'severity', 'enforced_by_id', 'test_method', 'state'],
    actions: [{ m: 'action_waive', l: 'Waive Rule',
      asks: [{ label: 'Why is the rule waived? The compensating control is part of the record', kwarg: 'reason' }] }] },
  /* Derived from the approval matrix: the model refuses a typed entry (2026-11-12). */
  'M60-authority': { kind: 'model_list', model: 'fix.grc.authority', create: false,
    empty: 'The delegated authority register is built from the approval matrix (M63): use Rebuild Register to refresh it. Entries cannot be typed in.',
    cols: ['name', 'role_title', 'amount_limit', 'authority_scope', 'source', 'synced_at', 'effective_from'],
    actions: [{ m: 'action_rebuild', l: 'Rebuild Register' }] },
  'M60-obligations': { kind: 'model_list', model: 'fix.compliance.obligation',
    cols: ['name', 'framework_id', 'clause_reference', 'owner_id', 'recurrence', 'mandatory', 'compliance_status'],
    actions: [
      { m: 'action_assess', l: 'Assess Compliance (Officer)',
        asks: [
          { label: 'Verdict: compliant, partially_compliant, non_compliant or not_applicable', kwarg: 'status' },
          { label: 'Assessment note (optional)', kwarg: 'notes', optional: true }
        ] }
    ] },
  'M60-licences': { kind: 'model_list', model: 'fix.grc.licence', stateField: 'state',
    cols: ['name', 'licence_type', 'number', 'authority', 'valid_to', 'responsible_id', 'state'],
    actions: [
      { m: 'action_suspend', l: 'Suspend',
        asks: [{ label: 'Why is the licence suspended? The reason is the record', kwarg: 'reason' }] },
      { m: 'action_reinstate', l: 'Reinstate' }
    ] },
  'M60-policies': { kind: 'model_list', model: 'fix.grc.policy', stateField: 'state',
    cols: ['code', 'name', 'policy_type', 'version', 'owner_id', 'review_due', 'attestation_required', 'attested_count', 'state'],
    actions: [{ m: 'action_approve', l: 'Approve Policy' }, { m: 'action_retire', l: 'Retire Policy' }] },
  'M60-legal': { kind: 'model_list', model: 'fix.grc.legal', stateField: 'state',
    cols: ['name', 'matter_type', 'counterparty', 'opened_on', 'counsel', 'exposure', 'provision', 'next_action_on', 'state'],
    actions: [{ m: 'action_close', l: 'Close Matter',
      asks: [{ label: 'Outcome (settled / withdrawn / dismissed / won / lost)', kwarg: 'outcome' },
             { label: 'Closing note (settlement terms or judgment reference)', kwarg: 'close_note' }] }] },
  'M60-pdpa': { kind: 'model_list', model: 'fix.grc.pdpa', stateField: 'outcome',
    cols: ['name', 'request_type', 'subject_name', 'received_on', 'due_on', 'outcome'],
    actions: [
      { m: 'action_fulfil', l: 'Mark Fulfilled' },
      { m: 'action_refuse', l: 'Refuse Request',
        asks: [{ label: 'Refusal ground (PDPA refusals answer to the law)', kwarg: 'reason' }] }
    ] },
  'M60-whistle': { kind: 'model_list', model: 'fix.grc.whistle', stateField: 'state',
    cols: ['name', 'channel', 'category', 'reported_on', 'anonymous', 'state'],
    actions: [
      { m: 'action_assign_investigator', l: 'Assign Investigator',
        asks: [{ label: 'Investigator employee ID', kwarg: 'investigator_id', number: true }] },
      { m: 'action_investigate', l: 'Start Investigation' },
      { m: 'action_close', l: 'Close Report',
        ask: 'Finding (substantiated / unsubstantiated / unfounded / policy_gap)', kwarg: 'finding' },
      { m: 'action_reveal_reporter', l: 'Reveal Reporter',
        ask: 'Reason for revealing the reporter identity (logged)', kwarg: 'reason' }
    ] },

  /* ---- capture audit 2026-11-18: the registers the pages could not capture ---- */
  'M60-assessments': { kind: 'model_list', model: 'fix.risk.assessment',
    cols: ['risk_id', 'assessed_on', 'assessed_by_id', 'inherent_score', 'residual_score', 'previous_residual', 'next_review_date'] },
  'M60-treatments': { kind: 'model_list', model: 'fix.risk.treatment', stateField: 'state',
    cols: ['name', 'risk_id', 'strategy', 'owner_id', 'due_on', 'target_residual_score', 'state'],
    actions: [
      { m: 'action_start', l: 'Start' },
      { m: 'action_complete', l: 'Complete', asks: [{ label: 'What was done, and where is the evidence?', kwarg: 'note' }] },
      { m: 'action_cancel', l: 'Cancel (Officer)', asks: [{ label: 'Why is the action cancelled?', kwarg: 'reason' }] }
    ] },
  'M60-events': { kind: 'model_list', model: 'fix.risk.event',
    cols: ['name', 'risk_id', 'event_type', 'occurred_on', 'source_module', 'loss_amount', 'reassessment_due'] },
  'M60-sod-tests': { kind: 'model_list', model: 'fix.sod.test', stateField: 'result',
    cols: ['name', 'control_id', 'tested_on', 'users_checked', 'violations_found', 'result'],
    actions: [{ m: 'action_run', l: 'Run Test' }] },
  'M60-sod-exceptions': { kind: 'model_list', model: 'fix.sod.mitigation', stateField: 'state',
    cols: ['name', 'control_id', 'user_id', 'valid_from', 'valid_until', 'approved_by_id', 'is_live', 'state'],
    actions: [{ m: 'action_approve', l: 'Approve' }, { m: 'action_reject', l: 'Reject' }, { m: 'action_revoke', l: 'Revoke' }] },
  'M60-occurrences': { kind: 'model_list', model: 'fix.compliance.obligation.occurrence', stateField: 'state',
    cols: ['name', 'obligation_id', 'period', 'due_on', 'owner_id', 'evidence_ref', 'overdue', 'state'],
    actions: [
      { m: 'action_discharge', l: 'Discharge', asks: [{ label: 'Discharge note (optional). Without evidence attached the discharge is recorded as a control failure.', kwarg: 'note', optional: true }] },
      { m: 'action_verify', l: 'Verify (Officer)' },
      { m: 'action_record_breach', l: 'Record Breach', asks: [{ label: 'Consequence and escalation of the breach', kwarg: 'reason' }] },
      { m: 'action_not_applicable', l: 'Not Applicable', asks: [{ label: 'Why does this occurrence not apply?', kwarg: 'reason' }] }
    ] },
  'M60-reg-changes': { kind: 'model_list', model: 'fix.grc.regulatory.change', stateField: 'state',
    cols: ['name', 'source', 'published_on', 'effective_on', 'state'],
    actions: [
      { m: 'action_assess', l: 'Assess Impact', asks: [{ label: 'Impact on obligations, controls and processes', kwarg: 'impact' }] },
      { m: 'action_close', l: 'Close' }
    ] },
  'M60-attestations': { kind: 'model_list', model: 'fix.grc.policy.attestation',
    cols: ['policy_id', 'version', 'employee_id', 'acknowledged_at', 'method'] },
  'M60-policy-exceptions': { kind: 'model_list', model: 'fix.grc.policy.exception', stateField: 'state',
    cols: ['name', 'policy_id', 'requested_by_id', 'valid_from', 'valid_to', 'decided_by_id', 'state'],
    actions: [
      { m: 'action_approve', l: 'Approve (Officer)' },
      { m: 'action_reject', l: 'Reject', asks: [{ label: 'Why is the exception rejected?', kwarg: 'reason' }] }
    ] },
  'M60-retention': { kind: 'model_list', model: 'fix.retention.class',
    cols: ['name', 'retention_years', 'expiry_action'] },
  'M60-holds': { kind: 'model_list', create: false, model: 'fix.legal.hold',
    cols: ['matter_ref', 'document_id', 'placed_by_id', 'placed_on', 'state', 'released_on'],
    empty: 'No legal hold is in place. Place one on a document with the Place Legal Hold chip, naming the matter it preserves.',
    actions: [{ m: 'action_release', l: 'Release Hold', asks: [{ label: 'Why is the hold released?', kwarg: 'reason' }] }] },
  'M60-ip': { kind: 'model_list', model: 'fix.grc.ip.asset',
    cols: ['name', 'ip_type', 'identifier', 'jurisdiction', 'renews_on', 'owner_id', 'renewal_due'] },
  'M60-ropa': { kind: 'model_list', model: 'fix.grc.processing.activity', stateField: 'state',
    cols: ['name', 'lawful_basis', 'subject_categories', 'retention_months', 'high_risk', 'owner_id', 'state'],
    actions: [{ m: 'action_activate', l: 'Put in Force' }, { m: 'action_retire', l: 'Retire' }] },
  'M60-transfers': { kind: 'model_list', model: 'fix.grc.data.transfer', stateField: 'state',
    cols: ['name', 'activity_id', 'destination_country_id', 'recipient', 'basis', 'approved_by_id', 'state'],
    actions: [
      { m: 'action_approve', l: 'Approve' },
      { m: 'action_suspend', l: 'Suspend', asks: [{ label: 'Why is the transfer suspended?', kwarg: 'reason' }] }
    ] },
  'M60-breaches': { kind: 'model_list', model: 'fix.grc.data.breach', stateField: 'state',
    cols: ['name', 'detected_on', 'data_categories', 'subjects_affected', 'notification_decision', 'state'],
    actions: [{ m: 'action_contain', l: 'Mark Contained' }, { m: 'action_close', l: 'Close (Officer)' }] },
  'M60-pias': { kind: 'model_list', model: 'fix.grc.privacy.impact', stateField: 'state',
    cols: ['name', 'activity_id', 'residual_risk', 'author_id', 'approved_by_id', 'state'],
    actions: [
      { m: 'action_approve', l: 'Approve' },
      { m: 'action_reject', l: 'Reject', asks: [{ label: 'Why is the assessment rejected?', kwarg: 'reason' }] }
    ] },

  /* Report chips -> their own computed pack */
  'M60-rpt-heat': { kind: 'table_report', module: 'M60', report: 'risk_heat_map', title: 'Risk Heat Map', period: false },
  'M60-rpt-def': { kind: 'table_report', module: 'M60', report: 'control_deficiency', title: 'Control Deficiency Log', period: false },
  'M60-rpt-lic': { kind: 'table_report', module: 'M60', report: 'licence_expiry', title: 'Licence Expiry Register', period: false },
  'M60-rpt-attest': { kind: 'table_report', module: 'M60', report: 'attestation', title: 'Attestation Status', period: false },
  'M60-rpt-board': { kind: 'table_report', module: 'M60', report: 'board_risk_pack', title: 'Board Risk Pack', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M60-form-risk': {
    kind: 'model_form',
    model: 'fix.risk.register',
    title: 'Risk',
    back: 'M60-register',
    status: { field: 'state', labels: {
      open: 'Open', mitigating: 'Mitigating', accepted: 'Residual Accepted', closed: 'Closed' } },
    sections: [
      { title: 'Enterprise Risk', note: 'Inherent score is likelihood × impact (1–5 each); category drives the register view. The state and the acceptance record change only through the register actions (R1).',
        fields: [
          { name: 'name', required: true, label: 'Risk Description' },
          { name: 'category', required: true, label: 'Category' },
          { name: 'likelihood', required: true, label: 'Likelihood (1-5)' },
          { name: 'impact', required: true, label: 'Impact (1-5)' },
          { name: 'owner_id', label: 'Risk Owner' },
          { name: 'review_date', label: 'Next Review Date' }
        ] },
      { title: 'Treatment', note: 'A residual below the inherent score must be grounded in linked ACTIVE controls (an ineffective control grounds nothing), and may not exceed the inherent score. Within the stated appetite the Risk Owner accepts; above it the acceptance is routed through M63 to the Delegated Authority Owner, who is stamped as the acceptor (P1-5).',
        fields: [
          { name: 'mitigation', type: 'text', label: 'Mitigation & Treatment Strategy' },
          { name: 'residual_likelihood', label: 'Residual Likelihood (1-5)' },
          { name: 'residual_impact', label: 'Residual Impact (1-5)' },
          { name: 'appetite_limit', readonly: true, label: 'Category Appetite (max residual)' },
          { name: 'above_appetite', readonly: true, label: 'Above Appetite (routes through M63)' },
          { name: 'control_deficient', readonly: true, label: 'Deficient Control (latest test not fully effective)' },
          { name: 'approval_state', readonly: true, label: 'M63 Approval (pending/approved by the routed decision)' },
          { name: 'residual_accepted_by_id', readonly: true, label: 'Residual Accepted By (Accept Residual action)' },
          { name: 'residual_accepted_on', readonly: true, label: 'Residual Accepted On' }
        ] },
      { title: 'Reported by the Source Modules', note: 'Each lapse, incident and decision the asset and facility modules reported on this subject. It is added to automatically; closing the entry stays with the risk owner.',
        fields: [
          { name: 'bridge_subject_ref', readonly: true, label: 'Subject' },
          { name: 'bridge_lapse_log', type: 'text', readonly: true, label: 'What Was Reported' }
        ] }
    ]
  },

  'M60-form-appetite': {
    kind: 'model_form',
    model: 'fix.risk.appetite',
    title: 'Risk Appetite',
    back: 'M60-appetite-set',
    sections: [
      { title: 'Risk Appetite', note: 'The maximum residual score tolerated for one category — one statement per category and company, maintained by the Compliance Officer. A residual above it is accepted only through M63 by someone other than the risk owner; a category with no statement bounds nothing (P1-5).',
        fields: [
          { name: 'company_id', required: true, label: 'Company' },
          { name: 'category', required: true, label: 'Category' },
          { name: 'max_residual_score', required: true, label: 'Maximum Residual Score (1-25)' },
          { name: 'note', type: 'text', label: 'Appetite Statement' }
        ] }
    ]
  },

  'M60-form-test': {
    kind: 'model_form',
    model: 'fix.grc.control.test',
    title: 'Control Test',
    back: 'M60-testing',
    status: { field: 'result', labels: {
      effective: 'Effective', partially_effective: 'Partially Effective',
      ineffective: 'Ineffective' } },
    sections: [
      { title: 'Control Test', note: 'The tester is stamped from your session (you may name a third-party tester) and may not be the control’s owner. The result stamps the control’s assessment record; a result short of Effective raises the deficiency (an NCR) and a CAPA owned by the control owner (P1-5).',
        fields: [
          { name: 'control_id', required: true, label: 'Control' },
          { name: 'tested_on', required: true, label: 'Tested On' },
          { name: 'tester_id', label: 'Tester' },
          { name: 'sample_size', label: 'Sample Size' },
          { name: 'exceptions', label: 'Exceptions Found' },
          { name: 'result', required: true, label: 'Result' },
          { name: 'notes', type: 'text', label: 'Notes' }
        ] }
    ]
  },

  'M60-form-licence': {
    kind: 'model_form',
    model: 'fix.grc.licence',
    title: 'Licence',
    back: 'M60-licences',
    status: { field: 'state', labels: {
      valid: 'Valid', expiring: 'Expiring Soon', expired: 'Expired', suspended: 'Suspended' } },
    sections: [
      { title: 'Corporate Licence', note: 'Type, number, issuing authority and validity; the register view orders by expiry date.',
        fields: [
          { name: 'name', required: true, label: 'Licence' },
          { name: 'licence_type', required: true, label: 'Licence Type' },
          { name: 'number', label: 'Licence Number' },
          { name: 'authority', label: 'Issuing Authority' },
          { name: 'issued_on', label: 'Issued On' },
          { name: 'valid_to', label: 'Valid To' },
          { name: 'responsible_id', label: 'Responsible' }
        ] }
    ]
  },

  'M60-form-policy': {
    kind: 'model_form',
    model: 'fix.grc.policy',
    title: 'Policy',
    back: 'M60-policies',
    status: { field: 'state', labels: {
      draft: 'Draft', approved: 'Approved', retired: 'Retired' } },
    sections: [
      { title: 'Policy', note: 'Code is unique per company; approving stamps the date. Attestation-required policies feed the attestation status report.',
        fields: [
          { name: 'code', required: true, label: 'Policy Code' },
          { name: 'name', required: true, label: 'Policy Name' },
          { name: 'policy_type', required: true, label: 'Policy Type' },
          { name: 'version', label: 'Version' },
          { name: 'owner_id', label: 'Policy Owner' },
          { name: 'review_due', label: 'Review Due' },
          { name: 'attestation_required', label: 'Attestation Required' },
          { name: 'document_id', label: 'Controlled Document (M24)' },
          { name: 'approved_on', readonly: true, label: 'Approved On (Approve Policy action)' },
          { name: 'attested_count', readonly: true, label: 'Acknowledged (this version)' }
        ] }
    ]
  },

  'M60-form-whistle': {
    kind: 'model_form',
    model: 'fix.grc.whistle',
    title: 'Whistleblow Report',
    back: 'M60-whistle',
    status: { field: 'state', labels: {
      received: 'Received', investigating: 'Investigating', substantiated: 'Substantiated',
      unsubstantiated: 'Unsubstantiated', closed: 'Closed' } },
    sections: [
      { title: 'Report', note: 'Intake files the report; the facts are kept as received (W1). The investigator is assigned by the Audit Committee through the Assign Investigator action.',
        fields: [
          { name: 'channel', required: true, label: 'Channel' },
          { name: 'category', required: true, label: 'Category' },
          { name: 'reported_on', required: true, label: 'Reported On' },
          { name: 'anonymous', label: 'Anonymous' }
        ] },
      { title: 'Account', fields: [
          { name: 'summary', required: true, type: 'text', label: 'Summary' }
        ] },
      { title: 'Investigation', note: 'Working notes stay editable until closure; the finding, second reviewer and reveal count change only through the workflow actions.',
        fields: [
          { name: 'investigator_id', readonly: true, label: 'Investigator (assigned)' },
          { name: 'investigation_notes', type: 'text', label: 'Investigation Notes' },
          { name: 'finding', readonly: true, label: 'Finding (Close Report action)' },
          { name: 'follow_up', readonly: true, label: 'Follow-up Action' },
          { name: 'reviewer_id', readonly: true, label: 'Second Reviewer (stamped)' },
          { name: 'revealed_count', readonly: true, label: 'Identity Reveals (logged)' }
        ] }
    ]
  },

  'M60-form-sod': {
    kind: 'model_form',
    model: 'fix.grc.sod.rule',
    title: 'SoD Rule',
    back: 'M60-sod',
    status: { field: 'state', labels: { active: 'Active', waived: 'Waived' } },
    sections: [
      { title: 'Segregation of Duties', note: 'Two incompatible roles (picked from the reconciled register M29 checks on every grant) and the compensating control that allows an exception.',
        fields: [
          { name: 'name', required: true, label: 'Rule' },
          { name: 'role_a', required: true, label: 'First Role' },
          { name: 'role_b', required: true, label: 'Incompatible Role' },
          { name: 'conflict_area', label: 'Process Area' },
          { name: 'severity', required: true, label: 'Severity' },
          { name: 'compensating_control', label: 'Compensating Control' },
          { name: 'enforced_by_id', label: 'Enforced By (the M29 SoD control that blocks it)' },
          { name: 'test_method', label: 'Test Method' },
          { name: 'last_test_result', readonly: true, label: 'Latest Test of the Enforcing Control' },
          { name: 'waived_by_id', readonly: true, label: 'Waived By (Waive Rule action)' },
          { name: 'waived_on', readonly: true, label: 'Waived On' }
        ] }
    ]
  },

  'M60-form-legal': {
    kind: 'model_form',
    model: 'fix.grc.legal',
    title: 'Legal Matter',
    back: 'M60-legal',
    status: { field: 'state', labels: {
      open: 'Open', negotiation: 'Negotiation', closed: 'Closed', judgment: 'Judgment' } },
    sections: [
      { title: 'Matter', note: 'Matter type, counterparty, counsel and exposure; closing records the resolution state.',
        fields: [
          { name: 'matter_type', required: true, label: 'Matter Type' },
          { name: 'counterparty', label: 'Counterparty' },
          { name: 'opened_on', required: true, label: 'Opened On' },
          { name: 'counsel', label: 'External Counsel' },
          { name: 'exposure', label: 'Exposure' },
          { name: 'provision', label: 'Provision' },
          { name: 'next_action', label: 'Next Action' },
          { name: 'next_action_on', label: 'Next Action Due' },
          { name: 'hold_note', label: 'What Must Be Preserved (place each hold with Place Legal Hold)' },
          { name: 'outcome', readonly: true, label: 'Outcome (Close Matter action)' },
          { name: 'close_note', readonly: true, label: 'Closing Note' },
          { name: 'closed_on', readonly: true, label: 'Closed On' }
        ] }
    ]
  },


  /* ===== master-data forms (batch 2) — D365 in-workspace ===== */
  'M60-form-control': {
    kind: 'model_form',
    model: 'fix.control',
    title: "Internal Control",
    back: 'M60-framework',
    sections: [
      { title: "Internal Control", note: "A control in the framework: the risk it addresses, its accountable owner and its test frequency. The assessment record is stamped by the control tests — nothing is typed here (P1-5).",
        fields: [
          { name: 'company_id', required: true, label: "Company" },
          { name: 'name', required: true, label: "Control Title" },
          { name: 'control_type', required: true, label: "Control Type" },
          { name: 'frequency', required: true, label: "Frequency" },
          { name: 'control_code', label: "Control Code (e.g. CTL-SEC-01)" },
          { name: 'objective', type: 'text', label: "Control Objective" },
          { name: 'nature', label: "Nature (manual / automated / hybrid)" },
          { name: 'is_key', label: "Key Control (in the testing programme)" },
          { name: 'risk_id', label: "Risk Addressed" },
          { name: 'obligation_ids', label: "Obligations Discharged" },
          { name: 'owner_id', label: "Control Owner (accountable; may not test their own control)" },
          { name: 'last_tested', readonly: true, label: "Last Assessment Date (stamped by the test)" },
          { name: 'test_result', readonly: true, label: "Test Result (stamped by the test)" }
        ] }
    ]
  },
  'M60-form-authority': {
    kind: 'model_form',
    model: 'fix.grc.authority',
    title: "Delegated Authority",
    back: 'M60-authority',
    create: false, pick: 'The register is built from the approval matrix: open an entry from the Delegated Authority register.',
    sections: [
      { title: "Delegated Authority (derived)", note: "One enforced authority limit, read from the DOFA ladder in force or the M63 approval matrix. Every field is a view onto machinery that actually refuses a document above the limit — change the ladder (M30) or the matrix (M63), then rebuild this register; nothing is typed here (P1-4).",
        fields: [
          { name: 'name', readonly: true, label: "Name" },
          { name: 'company_id', readonly: true, label: "Company" },
          { name: 'role_title', readonly: true, label: "Role / Position" },
          { name: 'currency_id', readonly: true, label: "Currency" },
          { name: 'effective_from', readonly: true, label: "Effective From" },
          { name: 'amount_limit', readonly: true, label: "Authority Limit" },
          { name: 'authority_scope', readonly: true, label: "Scope" },
          { name: 'delegate_to', readonly: true, label: "May Delegate To" },
          { name: 'source', readonly: true, label: "Enforced Source" },
          { name: 'source_ref', readonly: true, label: "Source Record" },
          { name: 'synced_at', readonly: true, label: "Rebuilt At" }
        ] }
    ]
  },
  'M60-form-obligation': {
    kind: 'model_form',
    model: 'fix.compliance.obligation',
    title: "Compliance Obligation",
    back: 'M60-obligations',
    sections: [
      { title: "Compliance Obligation", note: "A statutory/regulatory obligation with its owner, cadence and evidence requirement.",
        fields: [
          { name: 'company_id', required: true, label: "Company" },
          { name: 'framework_id', required: true, label: "Compliance Framework" },
          { name: 'name', required: true, label: "Requirement Title" },
          { name: 'clause_reference', required: true, label: "Clause / Section Reference" },
          { name: 'compliance_status', readonly: true, label: "Compliance Status (Assess Compliance sets it — an obligation is compliant only once assessed)" },
          { name: 'mandatory', label: "Mandatory Statutory Requirement" },
          { name: 'source_type', label: "Source" },
          { name: 'owner_id', label: "Obligation Owner (discharges each occurrence)" },
          { name: 'recurrence', label: "Recurrence" },
          { name: 'lead_days', label: "Advance Notice (days)" },
          { name: 'consequence', type: 'text', label: "Consequence of Breach" },
          { name: 'evidence_doc_id', label: "Compliance Evidence (M24 Document)" },
          { name: 'next_review_date', label: "Next Review Due (the clock nags daily once due)" },
          { name: 'notes', type: 'text', label: "Audit & Assessment Notes" }
        ] }
    ]
  },
  'M60-form-pdpa': {
    kind: 'model_form',
    model: 'fix.grc.pdpa',
    title: "Data Subject Request",
    back: 'M60-pdpa',
    status: { field: 'outcome', labels: {
      pending: 'Pending', fulfilled: 'Fulfilled', refused: 'Refused', partially: 'Partially Fulfilled' } },
    sections: [
      { title: "Data Subject Request", note: "A request from a person about their own personal data under the Bangladesh PDPA: access, erasure, correction, portability or objection. The statutory deadline is derived from the date received and never typed; the outcome is the Compliance Officer's act (Mark Fulfilled or Refuse Request, with the legal ground).",
        fields: [
          { name: 'name', readonly: true, label: "Reference (numbered on save)" },
          { name: 'company_id', required: true, label: "Company" },
          { name: 'request_type', required: true, label: "Request Type" },
          { name: 'subject_name', required: true, label: "Data Subject" },
          { name: 'received_on', required: true, label: "Received On" },
          { name: 'due_on', readonly: true, label: "SLA Due (derived: received + 30 days)" },
          { name: 'handled_by_id', label: "Handled By" },
          { name: 'notes', label: "Verification and Routing Note" },
          { name: 'outcome', readonly: true, label: "Outcome (Mark Fulfilled / Refuse Request)" }
        ] }
    ]
  },

  /* ===== capture audit 2026-11-18: forms for the registers the pages lacked ===== */
  'M60-form-assessment': {
    kind: 'model_form',
    model: 'fix.risk.assessment',
    title: 'Risk Assessment',
    back: 'M60-assessments',
    tabs: [
      { id: 'score', label: 'Scores', bn: 'স্কোর', icon: '🎯', badge: '6' },
      { id: 'record', label: 'Record', bn: 'রেকর্ড', icon: '🗂️', badge: '6' }
    ],
    sections: [
      { tab: 'score', title: 'Inherent and Residual Scores',
        note: 'A dated assessment by a Risk Owner or the Compliance Officer. It becomes the risk\'s current position and the earlier assessments stay exactly as they were: nothing is overwritten. A risk is not scored before the appetite of its category is stated.',
        fields: [
          { name: 'risk_id', required: true, label: 'Risk' },
          { name: 'likelihood', required: true, label: 'Inherent Likelihood (1-5)' },
          { name: 'impact', required: true, label: 'Inherent Impact (1-5)' },
          { name: 'residual_likelihood', label: 'Residual Likelihood (1-5, after controls)' },
          { name: 'residual_impact', label: 'Residual Impact (1-5, after controls)' },
          { name: 'rationale', required: true, type: 'text', label: 'Rationale' },
          { name: 'next_review_date', required: true, label: 'Next Review Due' }
        ] },
      { tab: 'record', title: 'What Was Recorded',
        note: 'Stamped on save: who assessed, when, the controls relied on at that moment and the residual it replaced.',
        fields: [
          { name: 'assessed_on', readonly: true, label: 'Assessed On' },
          { name: 'assessed_by_id', readonly: true, label: 'Assessed By' },
          { name: 'inherent_score', readonly: true, label: 'Inherent Score' },
          { name: 'residual_score', readonly: true, label: 'Residual Score' },
          { name: 'previous_residual', readonly: true, label: 'Previous Residual Score' },
          { name: 'controls_relied_on', readonly: true, label: 'Controls Relied On' }
        ] }
    ]
  },

  'M60-form-treatment': {
    kind: 'model_form',
    model: 'fix.risk.treatment',
    title: 'Risk Treatment',
    back: 'M60-treatments',
    status: { field: 'state', labels: {
      planned: 'Planned', in_progress: 'In Progress', done: 'Completed', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'decision', label: 'Decision', bn: 'সিদ্ধান্ত', icon: '🧭', badge: '5' },
      { id: 'action', label: 'Action', bn: 'পদক্ষেপ', icon: '🛠️', badge: '7' }
    ],
    sections: [
      { tab: 'decision', title: 'Treatment Decision',
        note: 'Mitigate, transfer, avoid or accept, with the reason. A transfer names its instrument (the insurance policy or contract clause that carries the risk). A Risk Owner or the Compliance Officer decides it; planning one puts an open risk under treatment.',
        fields: [
          { name: 'risk_id', required: true, label: 'Risk' },
          { name: 'strategy', required: true, label: 'Strategy' },
          { name: 'rationale', required: true, type: 'text', label: 'Rationale' },
          { name: 'transfer_instrument', label: 'Transfer Instrument (policy no. / contract clause)' },
          { name: 'target_residual_score', label: 'Target Residual Score' }
        ] },
      { tab: 'action', title: 'Action, Owner and Date',
        note: 'The owner is given a to-do for the due date. Completing it needs a note of what was done and where the evidence is; then reassess the residual.',
        fields: [
          { name: 'name', required: true, label: 'Action' },
          { name: 'owner_id', required: true, label: 'Action Owner' },
          { name: 'due_on', required: true, label: 'Due' },
          { name: 'overdue', readonly: true, label: 'Overdue' },
          { name: 'completion_note', readonly: true, label: 'Completion Note (Complete action)' },
          { name: 'completed_on', readonly: true, label: 'Completed On' },
          { name: 'completed_by_id', readonly: true, label: 'Completed By' }
        ] }
    ]
  },

  'M60-form-event': {
    kind: 'model_form',
    model: 'fix.risk.event',
    title: 'Risk Event',
    back: 'M60-events',
    tabs: [
      { id: 'event', label: 'Event', bn: 'ঘটনা', icon: '⚡', badge: '6' },
      { id: 'source', label: 'Source', bn: 'উৎস', icon: '🔗', badge: '4' }
    ],
    sections: [
      { tab: 'event', title: 'What Happened',
        note: 'A realised loss, incident, claim, non-conformance or breach, linked to the risk that materialised. It is kept as reported. The risk owner is asked to reassess; a loss, claim or breach on a risk scored below a Major impact is flagged as challenging the assessment.',
        fields: [
          { name: 'risk_id', required: true, label: 'Risk That Materialised' },
          { name: 'name', required: true, label: 'What Happened' },
          { name: 'event_type', required: true, label: 'Event Type' },
          { name: 'occurred_on', required: true, label: 'Occurred On' },
          { name: 'loss_amount', label: 'Loss Amount (BDT)' },
          { name: 'description', required: true, type: 'text', label: 'Description' }
        ] },
      { tab: 'source', title: 'Where It Was Recorded',
        fields: [
          { name: 'source_module', label: 'Source Module (e.g. M59, M23, M29)' },
          { name: 'source_ref', label: 'Source Reference' },
          { name: 'reported_by_id', readonly: true, label: 'Reported By' },
          { name: 'reassessment_due', readonly: true, label: 'Challenges the Assessment' }
        ] }
    ]
  },

  'M60-form-occurrence': {
    kind: 'model_form',
    model: 'fix.compliance.obligation.occurrence',
    title: 'Obligation Occurrence',
    back: 'M60-occurrences',
    status: { field: 'state', labels: {
      scheduled: 'Scheduled', discharged: 'Discharged', failed: 'Control Failure', verified: 'Verified',
      breached: 'Breached', not_applicable: 'Not Applicable' } },
    tabs: [
      { id: 'due', label: 'Due Instance', bn: 'নির্ধারিত', icon: '📅', badge: '5' },
      { id: 'decision', label: 'Discharge & Verification', bn: 'নিষ্পত্তি', icon: '✅', badge: '6' }
    ],
    sections: [
      { tab: 'due', title: 'Due Instance and Evidence',
        note: 'One due instance of an obligation, scheduled by the Compliance Officer; its owner gets a to-do for the due date. Attach the evidence (a filing receipt, certificate or return) before discharging: a discharge without evidence is recorded as a control failure, not as a discharge.',
        fields: [
          { name: 'obligation_id', required: true, label: 'Obligation' },
          { name: 'period', required: true, label: 'Period (e.g. 2026-Q4)' },
          { name: 'due_on', required: true, label: 'Due On' },
          { name: 'evidence_attachment_id', label: 'Evidence of Discharge' },
          { name: 'evidence_ref', label: 'Evidence Reference (filing / certificate no.)' }
        ] },
      { tab: 'decision', title: 'Discharge, Verification and Breach',
        note: 'The owner discharges; a Compliance Officer who did not discharge it verifies the evidence. A missed occurrence is recorded as a breach with its consequence, never quietly closed.',
        fields: [
          { name: 'owner_id', readonly: true, label: 'Obligation Owner' },
          { name: 'overdue', readonly: true, label: 'Overdue' },
          { name: 'discharged_by_id', readonly: true, label: 'Discharged By' },
          { name: 'discharged_on', readonly: true, label: 'Discharged On' },
          { name: 'verified_by_id', readonly: true, label: 'Verified By' },
          { name: 'decision_note', readonly: true, label: 'Decision Note' }
        ] }
    ]
  },

  'M60-form-regchange': {
    kind: 'model_form',
    model: 'fix.grc.regulatory.change',
    title: 'Regulatory Change',
    back: 'M60-reg-changes',
    status: { field: 'state', labels: { logged: 'Logged', assessed: 'Impact Assessed', closed: 'Actions Closed' } },
    tabs: [
      { id: 'change', label: 'Change', bn: 'পরিবর্তন', icon: '📜', badge: '5' },
      { id: 'impact', label: 'Impact', bn: 'প্রভাব', icon: '🎯', badge: '4' }
    ],
    sections: [
      { tab: 'change', title: 'The Change',
        note: 'A new or amended law, SRO, circular or regulator notice, logged by the Compliance Officer with its source and effective date.',
        fields: [
          { name: 'name', required: true, label: 'Change' },
          { name: 'source', required: true, label: 'Source (gazette, SRO, circular, counsel)' },
          { name: 'published_on', label: 'Published On' },
          { name: 'effective_on', required: true, label: 'Effective On' },
          { name: 'description', required: true, type: 'text', label: 'What Changes' }
        ] },
      { tab: 'impact', title: 'Impact on Obligations and Controls',
        note: 'Name what it touches; Assess Impact records the written assessment and who made it.',
        fields: [
          { name: 'obligation_ids', label: 'Affected Obligations' },
          { name: 'control_ids', label: 'Affected Controls' },
          { name: 'impact_assessment', readonly: true, label: 'Impact Assessment (Assess Impact action)' },
          { name: 'assessed_by_id', readonly: true, label: 'Assessed By' }
        ] }
    ]
  },

  'M60-form-attestation': {
    kind: 'model_form',
    model: 'fix.grc.policy.attestation',
    title: 'Policy Attestation',
    back: 'M60-attestations',
    tabs: [
      { id: 'ack', label: 'Acknowledge', bn: 'স্বীকৃতি', icon: '✍️', badge: '3' },
      { id: 'record', label: 'Record', bn: 'রেকর্ড', icon: '🗂️', badge: '4' }
    ],
    sections: [
      { tab: 'ack', title: 'I Have Read and Understood',
        note: 'Saving records YOUR acknowledgement of the current version of an approved policy that requires attestation, stamped with your name and the time. A signed paper copy is recorded by the Compliance Officer, who names the employee. It is kept as recorded.',
        fields: [
          { name: 'policy_id', required: true, label: 'Policy' },
          { name: 'method', required: true, label: 'How' },
          { name: 'paper_employee_id', label: 'Employee (signed paper copy only)' }
        ] },
      { tab: 'record', title: 'What Was Recorded',
        fields: [
          { name: 'version', readonly: true, label: 'Version Acknowledged' },
          { name: 'employee_id', readonly: true, label: 'Employee' },
          { name: 'acknowledged_at', readonly: true, label: 'Acknowledged At' },
          { name: 'recorded_by_id', readonly: true, label: 'Recorded By' }
        ] }
    ]
  },

  'M60-form-policy-exception': {
    kind: 'model_form',
    model: 'fix.grc.policy.exception',
    title: 'Policy Exception',
    back: 'M60-policy-exceptions',
    status: { field: 'state', labels: { requested: 'Requested', approved: 'Approved', rejected: 'Rejected', expired: 'Expired' } },
    tabs: [
      { id: 'request', label: 'Request', bn: 'অনুরোধ', icon: '📝', badge: '6' },
      { id: 'decision', label: 'Decision', bn: 'সিদ্ধান্ত', icon: '🖋️', badge: '4' }
    ],
    sections: [
      { tab: 'request', title: 'The Exception',
        note: 'A time-boxed departure from a policy (at most a year) with the control that compensates while it lasts. It ends on its own date and is never extended silently.',
        fields: [
          { name: 'policy_id', required: true, label: 'Policy' },
          { name: 'justification', required: true, type: 'text', label: 'Justification' },
          { name: 'compensating_control', required: true, type: 'text', label: 'Compensating Control' },
          { name: 'control_id', label: 'Compensating Control (register)' },
          { name: 'valid_from', required: true, label: 'Valid From' },
          { name: 'valid_to', required: true, label: 'Valid To' }
        ] },
      { tab: 'decision', title: 'Decision',
        note: 'Approved or rejected by a Compliance Officer who did not request it.',
        fields: [
          { name: 'requested_by_id', readonly: true, label: 'Requested By' },
          { name: 'decided_by_id', readonly: true, label: 'Decided By' },
          { name: 'decided_on', readonly: true, label: 'Decided On' },
          { name: 'decision_note', readonly: true, label: 'Decision Note' }
        ] }
    ]
  },

  'M60-form-ip': {
    kind: 'model_form',
    model: 'fix.grc.ip.asset',
    title: 'IP Asset',
    back: 'M60-ip',
    tabs: [
      { id: 'asset', label: 'Asset', bn: 'সম্পদ', icon: '™️', badge: '5' },
      { id: 'renewal', label: 'Renewal', bn: 'নবায়ন', icon: '🔁', badge: '5' }
    ],
    sections: [
      { tab: 'asset', title: 'Intellectual Property Held',
        note: 'A trademark, domain name, software licence held, copyright or design, kept by Legal Counsel or the Compliance Officer.',
        fields: [
          { name: 'name', required: true, label: 'Name' },
          { name: 'ip_type', required: true, label: 'Type' },
          { name: 'identifier', required: true, label: 'Registration No. / Domain / Licence Reference' },
          { name: 'jurisdiction', label: 'Jurisdiction' },
          { name: 'owner_id', label: 'Responsible' }
        ] },
      { tab: 'renewal', title: 'Renewal and Infringement Watch',
        note: 'Renewal is flagged 60 days ahead.',
        fields: [
          { name: 'registered_on', label: 'Registered On' },
          { name: 'renews_on', label: 'Renews / Expires On' },
          { name: 'renewal_due', readonly: true, label: 'Renewal Due (60 days)' },
          { name: 'infringement_note', type: 'text', label: 'Infringement Watch' },
          { name: 'company_id', required: true, label: 'Company' }
        ] }
    ]
  },

  'M60-form-ropa': {
    kind: 'model_form',
    model: 'fix.grc.processing.activity',
    title: 'Processing Activity',
    back: 'M60-ropa',
    status: { field: 'state', labels: { draft: 'Draft', active: 'In Force', retired: 'Retired' } },
    tabs: [
      { id: 'purpose', label: 'Purpose & Basis', bn: 'উদ্দেশ্য ও ভিত্তি', icon: '🎯', badge: '6' },
      { id: 'data', label: 'Data & Safeguards', bn: 'তথ্য ও সুরক্ষা', icon: '🔐', badge: '8' }
    ],
    sections: [
      { tab: 'purpose', title: 'Record of Processing',
        note: 'One processing activity under the Bangladesh PDPA: why personal data is processed and on which lawful basis. It is put in force by the Compliance Officer only with its retention and safeguards recorded, and a high-risk activity first needs an approved privacy impact assessment. Records are kept at least five years: retire, never delete.',
        fields: [
          { name: 'name', required: true, label: 'Processing Activity' },
          { name: 'purpose', required: true, type: 'text', label: 'Purpose' },
          { name: 'lawful_basis', required: true, label: 'Lawful Basis' },
          { name: 'owner_id', label: 'Process Owner' },
          { name: 'systems', label: 'Systems / Modules' },
          { name: 'high_risk', label: 'High-Risk Processing (needs an approved PIA)' }
        ] },
      { tab: 'data', title: 'Data, Recipients and Safeguards',
        fields: [
          { name: 'data_categories', required: true, label: 'Personal Data Categories' },
          { name: 'subject_categories', required: true, label: 'Data Subjects' },
          { name: 'recipients', label: 'Recipients' },
          { name: 'retention_months', label: 'Retention (months)' },
          { name: 'safeguards', type: 'text', label: 'Safeguards' },
          { name: 'company_id', required: true, label: 'Company' },
          { name: 'activated_by_id', readonly: true, label: 'Put in Force By' },
          { name: 'activated_on', readonly: true, label: 'In Force Since' }
        ] }
    ]
  },

  'M60-form-transfer': {
    kind: 'model_form',
    model: 'fix.grc.data.transfer',
    title: 'Cross-Border Transfer',
    back: 'M60-transfers',
    status: { field: 'state', labels: { draft: 'Draft', approved: 'Approved', suspended: 'Suspended' } },
    tabs: [
      { id: 'transfer', label: 'Transfer', bn: 'স্থানান্তর', icon: '🌐', badge: '6' },
      { id: 'approval', label: 'Approval', bn: 'অনুমোদন', icon: '🖋️', badge: '3' }
    ],
    sections: [
      { tab: 'transfer', title: 'Where Personal Data Goes',
        note: 'Every transfer of personal data out of Bangladesh, with its basis and safeguards, over a processing activity that is in force. Personal data does not leave without an approved entry here.',
        fields: [
          { name: 'activity_id', required: true, label: 'Processing Activity' },
          { name: 'destination_country_id', required: true, label: 'Destination Country' },
          { name: 'recipient', required: true, label: 'Recipient' },
          { name: 'basis', required: true, label: 'Transfer Basis' },
          { name: 'safeguards', required: true, type: 'text', label: 'Safeguards' },
          { name: 'volume_class', label: 'Volume' }
        ] },
      { tab: 'approval', title: 'Approval',
        note: 'Approved by a Compliance Officer who did not request it.',
        fields: [
          { name: 'effective_from', label: 'Effective From' },
          { name: 'requested_by_id', readonly: true, label: 'Requested By' },
          { name: 'approved_by_id', readonly: true, label: 'Approved By' }
        ] }
    ]
  },

  'M60-form-breach': {
    kind: 'model_form',
    model: 'fix.grc.data.breach',
    title: 'Data Breach',
    back: 'M60-breaches',
    status: { field: 'state', labels: { open: 'Open', contained: 'Contained', closed: 'Closed' } },
    tabs: [
      { id: 'breach', label: 'Breach', bn: 'লঙ্ঘন', icon: '🚨', badge: '6' },
      { id: 'response', label: 'Response', bn: 'প্রতিক্রিয়া', icon: '🛡️', badge: '7' }
    ],
    sections: [
      { tab: 'breach', title: 'What Happened',
        note: 'Restricted register: only the Compliance Officer and Legal Counsel read it. Bangladesh law does not oblige breach notification, but contracts with corporate customers and brand partners can: the decision is recorded either way.',
        fields: [
          { name: 'detected_on', required: true, label: 'Detected At' },
          { name: 'description', required: true, type: 'text', label: 'Description' },
          { name: 'data_categories', label: 'Data Categories Affected' },
          { name: 'subjects_affected', label: 'Subjects Affected (estimate)' },
          { name: 'activity_id', label: 'Processing Activity' },
          { name: 'company_id', required: true, label: 'Company' }
        ] },
      { tab: 'response', title: 'Containment, Assessment and Notification',
        note: 'Mark Contained needs the containment written; closing needs the assessment, the notification decision and, when someone was notified, who.',
        fields: [
          { name: 'containment', type: 'text', label: 'Containment' },
          { name: 'assessment', type: 'text', label: 'Risk Assessment' },
          { name: 'notification_decision', label: 'Notification Decision' },
          { name: 'notified_parties', label: 'Notified Parties' },
          { name: 'reported_by_id', readonly: true, label: 'Reported By' },
          { name: 'closed_by_id', readonly: true, label: 'Closed By' },
          { name: 'closed_on', readonly: true, label: 'Closed On' }
        ] }
    ]
  },

  'M60-form-pia': {
    kind: 'model_form',
    model: 'fix.grc.privacy.impact',
    title: 'Privacy Impact Assessment',
    back: 'M60-pias',
    status: { field: 'state', labels: { draft: 'Draft', approved: 'Approved', rejected: 'Rejected' } },
    tabs: [
      { id: 'assessment', label: 'Assessment', bn: 'মূল্যায়ন', icon: '🔍', badge: '4' },
      { id: 'approval', label: 'Approval', bn: 'অনুমোদন', icon: '🖋️', badge: '3' }
    ],
    sections: [
      { tab: 'assessment', title: 'Risks to the People Whose Data It Is',
        note: 'Required before a high-risk processing activity is put in force. An assessment that leaves a high residual risk is not approved.',
        fields: [
          { name: 'activity_id', required: true, label: 'Processing Activity' },
          { name: 'risk_summary', required: true, type: 'text', label: 'Risks to Data Subjects' },
          { name: 'mitigations', required: true, type: 'text', label: 'Mitigations' },
          { name: 'residual_risk', required: true, label: 'Residual Risk' }
        ] },
      { tab: 'approval', title: 'Approval',
        note: 'Approved by a Compliance Officer who did not author it.',
        fields: [
          { name: 'author_id', readonly: true, label: 'Author' },
          { name: 'approved_by_id', readonly: true, label: 'Approved By' },
          { name: 'approved_on', readonly: true, label: 'Approved On' }
        ] }
    ]
  },


  /* ===== triage coverage screens ===== */
  'M60-compliance-framework': { kind: 'model_list', model: 'fix.compliance.framework', stateField: 'state',
    cols: ['name', 'code', 'state', 'active', 'company_id', 'operating_unit_id', 'standard_edition'],
    actions: [{ m: 'action_activate', l: 'Enforce' }, { m: 'action_archive', l: 'Archive' }] },

  'M60-form-compliance-framework': {
    kind: 'model_form',
    model: 'fix.compliance.framework',
    title: "Compliance Framework",
    back: 'M60-compliance-framework',
    status: { field: 'state' },
    sections: [
      { title: "Compliance Framework", note: "Opened from the module's own record set. Every field here is the model's real field; the workflow rules live on the model and are not bypassed by this form.",
        fields: [
          { name: 'name', required: true, label: "Framework Name" },
          { name: 'code', required: true, label: "Framework Identifier" },
          { name: 'company_id', required: true, label: "Company" },
          { name: 'active', label: "Active" },
          { name: 'operating_unit_id', label: "Operating Unit" },
          { name: 'standard_edition', label: "Edition / Revision" }
        ] }
    ]
  },

};

export const REPORT_ROUTES = {
  'M60:Risk Heat Map': 'M60-rpt-heat',
  'M60:Control Deficiency Log': 'M60-rpt-def',
  'M60:Licence Expiry Register': 'M60-rpt-lic',
  'M60:Attestation Status': 'M60-rpt-attest',
  'M60:Board Risk Pack': 'M60-rpt-board'
};

export const FORM_MODELS = {
  'M60:Risk': 'fix.risk.register',
  'M60:Risk Appetite': 'fix.risk.appetite',
  'M60:Control Test': 'fix.grc.control.test',
  'M60:Licence': 'fix.grc.licence',
  'M60:Policy': 'fix.grc.policy',
  'M60:Whistleblow Report': 'fix.grc.whistle'
};

export const FORM_CHIPS = {
  'M60:Risk': 'M60-form-risk',
  'M60:Risk Appetite': 'M60-form-appetite',
  'M60:Risk Assessment': 'M60-form-assessment',
  'M60:Risk Treatment': 'M60-form-treatment',
  'M60:Risk Event': 'M60-form-event',
  'M60:Internal Control': 'M60-form-control',
  'M60:Control Test': 'M60-form-test',
  'M60:SoD Rule': 'M60-form-sod',
  'M60:SoD Test Run': 'M29-form-sodtest',
  'M60:SoD Exception': 'M29-form-sodexception',
  'M60:Delegated Authority': 'M60-form-authority',
  'M60:Compliance Obligation': 'M60-form-obligation',
  'M60:Compliance Framework': 'M60-form-compliance-framework',
  'M60:Obligation Occurrence': 'M60-form-occurrence',
  'M60:Licence': 'M60-form-licence',
  'M60:Regulatory Change': 'M60-form-regchange',
  'M60:Policy': 'M60-form-policy',
  'M60:Policy Attestation': 'M60-form-attestation',
  'M60:Policy Exception': 'M60-form-policy-exception',
  'M60:Retention Policy': 'M24-form-retention',
  'M60:Legal Matter': 'M60-form-legal',
  'M60:Place Legal Hold': 'M24-form-hold',
  'M60:IP Asset': 'M60-form-ip',
  'M60:Data Subject Request': 'M60-form-pdpa',
  'M60:Processing Activity': 'M60-form-ropa',
  'M60:Cross-Border Transfer': 'M60-form-transfer',
  'M60:Data Breach': 'M60-form-breach',
  'M60:Privacy Impact Assessment': 'M60-form-pia',
  'M60:Whistleblow Report': 'M60-form-whistle',
  'M60:__by_model__': {
    'fix.compliance.framework': 'M60-form-compliance-framework',
    'fix.control': 'M60-form-control',
    'fix.grc.authority': 'M60-form-authority',
    'fix.compliance.obligation': 'M60-form-obligation',
    'fix.compliance.obligation.occurrence': 'M60-form-occurrence',
    'fix.grc.regulatory.change': 'M60-form-regchange',
    'fix.grc.pdpa': 'M60-form-pdpa',
    'fix.risk.register': 'M60-form-risk',
    'fix.risk.appetite': 'M60-form-appetite',
    'fix.risk.assessment': 'M60-form-assessment',
    'fix.risk.treatment': 'M60-form-treatment',
    'fix.risk.event': 'M60-form-event',
    'fix.grc.control.test': 'M60-form-test',
    'fix.grc.licence': 'M60-form-licence',
    'fix.grc.policy': 'M60-form-policy',
    'fix.grc.policy.attestation': 'M60-form-attestation',
    'fix.grc.policy.exception': 'M60-form-policy-exception',
    'fix.grc.whistle': 'M60-form-whistle',
    'fix.grc.sod.rule': 'M60-form-sod',
    'fix.sod.test': 'M29-form-sodtest',
    'fix.sod.mitigation': 'M29-form-sodexception',
    'fix.retention.class': 'M24-form-retention',
    'fix.grc.legal': 'M60-form-legal',
    'fix.grc.ip.asset': 'M60-form-ip',
    'fix.grc.processing.activity': 'M60-form-ropa',
    'fix.grc.data.transfer': 'M60-form-transfer',
    'fix.grc.data.breach': 'M60-form-breach',
    'fix.grc.privacy.impact': 'M60-form-pia'
  },
  'M60:__by_screen__': {
    'M60-compliance-framework': 'M60-form-compliance-framework',
    'M60-framework': 'M60-form-control',
    'M60-authority': 'M60-form-authority',
    'M60-obligations': 'M60-form-obligation',
    'M60-occurrences': 'M60-form-occurrence',
    'M60-reg-changes': 'M60-form-regchange',
    'M60-pdpa': 'M60-form-pdpa',
    'M60-register': 'M60-form-risk',
    'M60-appetite': 'M60-form-risk',
    'M60-appetite-set': 'M60-form-appetite',
    'M60-assessments': 'M60-form-assessment',
    'M60-treatments': 'M60-form-treatment',
    'M60-events': 'M60-form-event',
    'M60-testing': 'M60-form-test',
    'M60-licences': 'M60-form-licence',
    'M60-policies': 'M60-form-policy',
    'M60-attestations': 'M60-form-attestation',
    'M60-policy-exceptions': 'M60-form-policy-exception',
    'M60-retention': 'M24-form-retention',
    'M60-whistle': 'M60-form-whistle',
    'M60-sod': 'M60-form-sod',
    'M60-sod-tests': 'M29-form-sodtest',
    'M60-sod-exceptions': 'M29-form-sodexception',
    'M60-legal': 'M60-form-legal',
    'M60-holds': 'M24-form-hold',
    'M60-ip': 'M60-form-ip',
    'M60-ropa': 'M60-form-ropa',
    'M60-transfers': 'M60-form-transfer',
    'M60-breaches': 'M60-form-breach',
    'M60-pias': 'M60-form-pia'
  }
};

export const CREATE = {
  M60: { screen: 'M60-form-risk', model: 'fix.risk.register', label: 'Risk' }
};
