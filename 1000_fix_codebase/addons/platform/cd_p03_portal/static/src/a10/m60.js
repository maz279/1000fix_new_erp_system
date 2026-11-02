/** @odoo-module **/
/* A10 · Governance, Risk & Quality — M60 Governance, Risk & Compliance.
 * Registry-faithful: 4 groups / 12 screens / 5 reports / 5 forms / freg 70. */

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
      { id: 'M60-appetite', en: 'Appetite & Aggregation', bn: 'ঝুঁকি ক্ষমতা', t: 'r' }
    ]},
    { en: 'Controls', screens: [
      { id: 'M60-framework', en: 'Internal Control Framework', bn: 'অভ্যন্তরীণ নিয়ন্ত্রণ', t: 'g' },
      { id: 'M60-testing', en: 'Control Testing', bn: 'নিয়ন্ত্রণ পরীক্ষা', t: 'g' },
      { id: 'M60-sod', en: 'SoD Rules', bn: 'দায়িত্ব বিভাজন', t: 'g' },
      { id: 'M60-authority', en: 'Delegated Authority', bn: 'প্রতিনিধি ক্ষমতা', t: 'g' }
    ]},
    { en: 'Compliance', screens: [
      { id: 'M60-obligations', en: 'Obligation Register', bn: 'বাধ্যবাধকতা', t: 'g' },
      { id: 'M60-licences', en: 'Licence Register', bn: 'লাইসেন্স রেজিস্টার', t: 'g' },
      { id: 'M60-policies', en: 'Policy Governance', bn: 'নীতি শাসন', t: 'g' }
    ]},
    { en: 'Legal & Data', screens: [
      { id: 'M60-legal', en: 'Legal Matters', bn: 'আইনি বিষয়', t: 'g' },
      { id: 'M60-pdpa', en: 'PDPA Governance', bn: 'পিডিপিএ শাসন', t: 'g' },
      { id: 'M60-whistle', en: 'Whistleblowing', bn: 'হুইসেলব্লোয়িং', t: 'g' }
    ]}
  ],
  reports: ['Risk Heat Map', 'Control Deficiency Log', 'Licence Expiry Register', 'Attestation Status', 'Board Risk Pack'],
  forms: ['Risk', 'Control Test', 'Licence', 'Policy', 'Whistleblow Report'],
  cross: ['M23 QMS', 'M51 Tax', 'M24 Documents', 'M19 GL'],
  freg: { src: 70, sub: [
    ['1', 'Risk Register', 12], ['2', 'Control Framework & Testing', 14],
    ['3', 'SoD & Authority', 8], ['4', 'Compliance Obligations', 9],
    ['5', 'Policy Governance', 6], ['6', 'Legal & IP', 7],
    ['7', 'PDPA Governance', 9], ['8', 'Whistleblowing', 5]
  ] }
};

export const SCREENS = {
  'M60-register': { kind: 'model_list', model: 'fix.risk.register', stateField: 'state',
    cols: ['name', 'category', 'likelihood', 'impact', 'risk_score', 'owner_id', 'review_date', 'state', 'residual_score', 'residual_band', 'residual_accepted_by_id'] },
  'M60-appetite': { kind: 'table_report', module: 'M60', report: 'risk_heat_map', title: 'Appetite & Aggregation', period: false },
  'M60-framework': { kind: 'model_list', model: 'fix.control',
    cols: ['control_code', 'name', 'control_type', 'frequency', 'risk_id', 'last_tested', 'test_result'] },
  'M60-testing': { kind: 'model_list', model: 'fix.grc.control.test', stateField: 'result',
    cols: ['name', 'control_id', 'tested_on', 'tester_id', 'sample_size', 'exceptions', 'result'] },
  'M60-sod': { kind: 'model_list', model: 'fix.grc.sod.rule', stateField: 'state',
    cols: ['name', 'role_a', 'role_b', 'conflict_area', 'severity', 'state'],
    actions: [{ m: 'action_waive', l: 'Waive Rule' }] },
  'M60-authority': { kind: 'model_list', model: 'fix.grc.authority',
    cols: ['name', 'role_title', 'amount_limit', 'authority_scope', 'delegate_to', 'effective_from'] },
  'M60-obligations': { kind: 'model_list', model: 'fix.compliance.obligation',
    cols: ['name', 'framework_id', 'clause_reference', 'mandatory', 'compliance_status'] },
  'M60-licences': { kind: 'model_list', model: 'fix.grc.licence', stateField: 'state',
    cols: ['name', 'licence_type', 'number', 'authority', 'valid_to', 'responsible_id', 'state'] },
  'M60-policies': { kind: 'model_list', model: 'fix.grc.policy', stateField: 'state',
    cols: ['code', 'name', 'policy_type', 'version', 'owner_id', 'review_due', 'attestation_required', 'state'],
    actions: [{ m: 'action_approve', l: 'Approve Policy' }] },
  'M60-legal': { kind: 'model_list', model: 'fix.grc.legal', stateField: 'state',
    cols: ['name', 'matter_type', 'counterparty', 'opened_on', 'counsel', 'exposure', 'state'],
    actions: [{ m: 'action_close', l: 'Close Matter' }] },
  'M60-pdpa': { kind: 'model_list', model: 'fix.grc.pdpa', stateField: 'outcome',
    cols: ['name', 'request_type', 'subject_name', 'received_on', 'due_on', 'outcome'],
    actions: [{ m: 'action_fulfil', l: 'Mark Fulfilled' }] },
  'M60-whistle': { kind: 'model_list', model: 'fix.grc.whistle', stateField: 'state',
    cols: ['name', 'channel', 'category', 'reported_on', 'anonymous', 'state'],
    actions: [{ m: 'action_investigate', l: 'Investigate' }] },

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
      draft: 'Draft', assessed: 'Assessed', mitigated: 'Mitigated', closed: 'Closed' } },
    sections: [
      { title: 'Enterprise Risk', note: 'Inherent score is likelihood × impact (1–5 each); category drives the register view.',
        fields: [
          { name: 'name', required: true, label: 'Risk Description' },
          { name: 'category', required: true, label: 'Category' },
          { name: 'likelihood', required: true, label: 'Likelihood (1-5)' },
          { name: 'impact', required: true, label: 'Impact (1-5)' },
          { name: 'owner_id', label: 'Risk Owner' },
          { name: 'review_date', label: 'Next Review Date' },
          { name: 'state', required: true, label: 'State' }
        ] },
      { title: 'Treatment', fields: [
          { name: 'mitigation', type: 'text', label: 'Mitigation & Treatment Strategy' }
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
      { title: 'Control Test', note: 'Sample size and exceptions; the result is the test conclusion the deficiency log reads.',
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
          { name: 'responsible_id', label: 'Responsible' },
          { name: 'state', required: true, label: 'State' }
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
          { name: 'state', required: true, label: 'State' }
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
      { title: 'Report', note: 'Channel and category; the summary is the reporter\'s account, kept as received.',
        fields: [
          { name: 'channel', required: true, label: 'Channel' },
          { name: 'category', required: true, label: 'Category' },
          { name: 'reported_on', required: true, label: 'Reported On' },
          { name: 'anonymous', label: 'Anonymous' },
          { name: 'investigator_id', label: 'Investigator' },
          { name: 'state', required: true, label: 'State' }
        ] },
      { title: 'Account', fields: [
          { name: 'summary', required: true, type: 'text', label: 'Summary' }
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
      { title: 'Segregation of Duties', note: 'Two incompatible roles and the compensating control that allows an exception.',
        fields: [
          { name: 'name', required: true, label: 'Rule' },
          { name: 'role_a', required: true, label: 'First Role' },
          { name: 'role_b', required: true, label: 'Incompatible Role' },
          { name: 'conflict_area', label: 'Process Area' },
          { name: 'severity', required: true, label: 'Severity' },
          { name: 'compensating_control', label: 'Compensating Control' },
          { name: 'state', required: true, label: 'State' }
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
          { name: 'state', required: true, label: 'State' }
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
      { title: "Internal Control", note: "A control in the framework: the risk it addresses, its owner and its test frequency.",
        fields: [
          { name: 'company_id', required: true, label: "Company" },
          { name: 'name', required: true, label: "Control Title" },
          { name: 'control_type', required: true, label: "Control Type" },
          { name: 'frequency', required: true, label: "Frequency" },
          { name: 'state', required: true, label: "State" },
          { name: 'control_code', label: "Control Code (e.g. CTL-SEC-01)" },
          { name: 'risk_id', label: "Risk Addressed" },
          { name: 'last_tested', label: "Last Assessment Date" }
        ] }
    ]
  },
  'M60-form-authority': {
    kind: 'model_form',
    model: 'fix.grc.authority',
    title: "Delegated Authority",
    back: 'M60-authority',
    sections: [
      { title: "Delegated Authority", note: "A delegation of authority: who may commit what value, to which limit.",
        fields: [
          { name: 'name', required: true, label: "Name" },
          { name: 'company_id', required: true, label: "Company" },
          { name: 'role_title', required: true, label: "Role / Position" },
          { name: 'currency_id', required: true, label: "Currency" },
          { name: 'effective_from', required: true, label: "Effective From" },
          { name: 'amount_limit', label: "Authority Limit" },
          { name: 'authority_scope', label: "Scope" },
          { name: 'delegate_to', label: "May Delegate To" }
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
          { name: 'compliance_status', required: true, label: "Compliance Status" },
          { name: 'mandatory', label: "Mandatory Statutory Requirement" },
          { name: 'evidence_doc_id', label: "Compliance Evidence (M24 Document)" },
          { name: 'notes', type: 'text', label: "Audit & Assessment Notes" }
        ] }
    ]
  },
  'M60-form-pdpa': {
    kind: 'model_form',
    model: 'fix.grc.pdpa',
    title: "PDPA Register Entry",
    back: 'M60-pdpa',
    sections: [
      { title: "PDPA Register Entry", note: "A personal-data processing record for the Bangladesh PDPA: purpose, legal basis and retention.",
        fields: [
          { name: 'name', required: true, label: "Name" },
          { name: 'company_id', required: true, label: "Company" },
          { name: 'request_type', required: true, label: "Request Type" },
          { name: 'subject_name', required: true, label: "Data Subject" },
          { name: 'received_on', required: true, label: "Received On" },
          { name: 'outcome', required: true, label: "Outcome" },
          { name: 'due_on', label: "SLA Due" },
          { name: 'handled_by_id', label: "Handled By" }
        ] }
    ]
  },


  /* ===== triage coverage screens ===== */
  'M60-compliance-framework': { kind: 'model_list', model: 'fix.compliance.framework', stateField: 'state',
    cols: ['name', 'code', 'state', 'active', 'company_id', 'operating_unit_id', 'standard_edition'] },

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
          { name: 'state', required: true, label: "State" },
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
  'M60:Control Test': 'fix.grc.control.test',
  'M60:Licence': 'fix.grc.licence',
  'M60:Policy': 'fix.grc.policy',
  'M60:Whistleblow Report': 'fix.grc.whistle'
};

export const FORM_CHIPS = {
  'M60:Internal Control': 'M60-form-control',
  'M60:Delegated Authority': 'M60-form-authority',
  'M60:Compliance Obligation': 'M60-form-obligation',
  'M60:PDPA Register Entry': 'M60-form-pdpa',
  'M60:Risk': 'M60-form-risk',
  'M60:Control Test': 'M60-form-test',
  'M60:Licence': 'M60-form-licence',
  'M60:Policy': 'M60-form-policy',
  'M60:Whistleblow Report': 'M60-form-whistle',
  'M60:__by_model__': {
    'fix.compliance.framework': 'M60-form-compliance-framework',
    'fix.control': 'M60-form-control',
    'fix.grc.authority': 'M60-form-authority',
    'fix.compliance.obligation': 'M60-form-obligation',
    'fix.grc.pdpa': 'M60-form-pdpa',
    'fix.risk.register': 'M60-form-risk',
    'fix.grc.control.test': 'M60-form-test',
    'fix.grc.licence': 'M60-form-licence',
    'fix.grc.policy': 'M60-form-policy',
    'fix.grc.whistle': 'M60-form-whistle',
    'fix.grc.sod.rule': 'M60-form-sod',
    'fix.grc.legal': 'M60-form-legal'
  },
  'M60:__by_screen__': {
    'M60-compliance-framework': 'M60-form-compliance-framework',
    'M60-framework': 'M60-form-control',
    'M60-authority': 'M60-form-authority',
    'M60-obligations': 'M60-form-obligation',
    'M60-pdpa': 'M60-form-pdpa',
    'M60-register': 'M60-form-risk',
    'M60-appetite': 'M60-form-risk',
    'M60-testing': 'M60-form-test',
    'M60-licences': 'M60-form-licence',
    'M60-policies': 'M60-form-policy',
    'M60-whistle': 'M60-form-whistle',
    'M60-sod': 'M60-form-sod',
    'M60-legal': 'M60-form-legal'
  }
};

export const CREATE = {
  M60: { screen: 'M60-form-risk', model: 'fix.risk.register', label: 'Risk' }
};
