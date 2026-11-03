/** @odoo-module **/
/* A10 · Governance, Risk & Quality — M23 Quality Management (ISO 9001).
 * Registry-faithful: 4 groups / 12 screens / 5 reports / 4 forms / freg 78. */

export const MODULE = {
  area: 'A10', code: 'M23', en: 'Quality Management (ISO)', title: 'M23 · Quality Management (ISO)',
  bn: 'গুণমান ব্যবস্থাপনা (আইএসও)', icon: '✅',
  desc: 'Quality policy and objectives, the ISO process register, checklist authoring and quality gates, NCR management with RCA (5-Why/8D), CAPA with verification, the internal audit programme, certification and surveillance, management review, and Pareto/CoPQ analytics.',
  kpis: [
    { l: 'Major NCs', m: 'major_ncs' },
    { l: 'CAPA On-Time', m: 'capa_on_time', suffix: '%' },
    { l: 'Open NCRs', m: 'open_ncrs' },
    { l: 'Open Audit Findings', m: 'audit_findings' },
    { l: 'First-Pass QC', m: 'first_pass_qc', suffix: '%' },
    { l: 'CoPQ', m: 'copq', prefix: '৳ ' }
  ],
  groups: [
    { en: 'Record Coverage', screens: [
      { id: 'M23-qms-copq', en: "Qms Copq", bn: "Qms Copq", t: 'g' }
    ]},
    { en: 'Framework', screens: [
      { id: 'M23-policy', en: 'Policy & Objectives', bn: 'নীতি ও উদ্দেশ্য', t: 'g' },
      { id: 'M23-processes', en: 'Process Register (ISO map)', bn: 'প্রক্রিয়া রেজিস্টার', t: 'g' },
      { id: 'M23-checklists', en: 'Checklist Authoring', bn: 'চেকলিস্ট রচনা', t: 'g' },
      { id: 'M23-gates', en: 'Quality Gates', bn: 'গুণগত গেট', t: 'g' }
    ]},
    { en: 'Nonconformance', screens: [
      { id: 'M23-ncr', en: 'NCR Management', bn: 'অসঙ্গতি', t: 'g' },
      { id: 'M23-rca', en: 'RCA (5-Why / 8D)', bn: 'মূল কারণ', t: 'g' },
      { id: 'M23-capa', en: 'CAPA & Verification', bn: 'ক্যাপা', t: 'g' }
    ]},
    { en: 'Audits', screens: [
      { id: 'M23-internal', en: 'Internal Audit Programme', bn: 'অভ্যন্তরীণ অডিট', t: 'g' },
      { id: 'M23-external', en: 'Certification & Surveillance', bn: 'সার্টিফিকেশন', t: 'g' },
      { id: 'M23-review', en: 'Management Review', bn: 'ব্যবস্থাপনা পর্যালোচনা', t: 'g' }
    ]},
    { en: 'Analytics', screens: [
      { id: 'M23-stat', en: 'Pareto & Control Charts', bn: 'প্যারেটো', t: 'r' },
      { id: 'M23-copq', en: 'Cost of Poor Quality', bn: 'নিম্ন গুণগত ব্যয়', t: 'r' }
    ]}
  ],
  reports: ['NCR & CAPA Register', 'Audit Programme Status', 'Repeat-Failure Escalation', 'CoPQ Analysis', 'Management Review Pack'],
  forms: ['NCR', 'CAPA', 'Audit Finding', 'Checklist Template'],
  cross: ['M01 Service Orders', 'M34 Complaints', 'M42 Suppliers', 'M24 Documents'],
  freg: { src: 78, sub: [
    ['1', 'Policy & Objectives', 6, { model: 'fix.qms.policy', cols: ['name', 'year', 'objective', 'target', 'actual'], screens: ['M23-policy'] }],
    ['2', 'Process Register', 7, { model: 'fix.qms.process', cols: ['code', 'name', 'process_owner_id', 'iso_clause', 'state'], screens: ['M23-processes'] }],
    ['3', 'Checklists & Gates', 10, { model: 'fix.qms.checklist', cols: ['name', 'checklist_type', 'iso_clause', 'version', 'state'], screens: ['M23-checklists', 'M23-gates'] }],
    ['4', 'NCR Management', 12, { model: 'fix.ncr', cols: ['name', 'source', 'severity', 'disposition', 'state'], screens: ['M23-ncr'] }],
    ['5', 'RCA & CAPA', 14, { model: 'fix.capa', cols: ['ncr_id', 'severity', 'owner_id', 'due_on', 'state'], screens: ['M23-rca', 'M23-capa'] }],
    ['6', 'Audit Programme', 13, { model: 'fix.internal.audit', cols: ['branch_id', 'scheduled_on', 'auditor_id', 'scope', 'state'], screens: ['M23-internal', 'M23-external'] }],
    ['7', 'Management Review', 7, { model: 'fix.qms.review', cols: ['name', 'review_date', 'chairperson_id', 'open_actions', 'state'], screens: ['M23-review'] }],
    ['8', 'Statistics & CoPQ', 9, { model: 'fix.qms.copq', cols: ['name', 'period', 'category', 'amount'], screens: ['M23-stat', 'M23-copq', 'M23-qms-copq'] }]
  ] }
};

export const SCREENS = {
  'M23-policy': { kind: 'model_list', model: 'fix.qms.policy', stateField: 'state',
    cols: ['name', 'year', 'objective', 'target', 'actual', 'unit', 'state'],
    actions: [{ m: 'action_approve', l: 'Approve' }] },
  'M23-processes': { kind: 'model_list', model: 'fix.qms.process',
    cols: ['code', 'name', 'process_owner_id', 'iso_clause', 'process_type', 'state'] },
  'M23-checklists': { kind: 'model_list', model: 'fix.qms.checklist', stateField: 'state',
    cols: ['name', 'checklist_type', 'iso_clause', 'item_count', 'version', 'state'],
    actions: [{ m: 'action_publish', l: 'Publish' }] },
  'M23-gates': { kind: 'model_list', model: 'fix.qms.gate',
    cols: ['sequence', 'code', 'name', 'stage', 'mandatory_checklist_id', 'blocking', 'state'] },
  'M23-ncr': { kind: 'model_list', model: 'fix.ncr', stateField: 'state',
    cols: ['name', 'source', 'severity', 'disposition', 'root_cause', 'state'] },
  'M23-rca': { kind: 'model_list', model: 'fix.ncr', stateField: 'state',
    cols: ['name', 'severity', 'root_cause', 'state'] },
  'M23-capa': { kind: 'model_list', model: 'fix.capa', stateField: 'state',
    cols: ['ncr_id', 'severity', 'owner_id', 'due_on', 'effectiveness_result', 'state'],
    actions: [{ m: 'action_implement', l: 'Implement' }, { m: 'action_verify', l: 'Verify' },
              { m: 'action_close', l: 'Close' }] },
  'M23-internal': { kind: 'model_list', model: 'fix.internal.audit', stateField: 'state',
    cols: ['branch_id', 'scheduled_on', 'auditor_id', 'scope', 'state'],
    actions: [{ m: 'action_execute', l: 'Execute' }, { m: 'action_report', l: 'Report' }] },
  'M23-external': { kind: 'model_list', model: 'fix.qms.certification', stateField: 'result',
    cols: ['name', 'standard', 'body', 'audit_type', 'audit_date', 'valid_until', 'result'],
    actions: [{ m: 'action_pass', l: 'Mark Passed' }] },
  'M23-review': { kind: 'model_list', model: 'fix.qms.review', stateField: 'state',
    cols: ['name', 'review_date', 'chairperson_id', 'open_actions', 'state'],
    actions: [{ m: 'action_hold', l: 'Mark Held' }, { m: 'action_close', l: 'Close' }] },
  'M23-stat': { kind: 'table_report', module: 'M23', report: 'repeat_failure', title: 'Pareto — Repeat Failures', period: false },
  'M23-copq': { kind: 'table_report', module: 'M23', report: 'copq_analysis', title: 'Cost of Poor Quality', period: false },

  /* Report chips -> their own computed pack */
  'M23-rpt-ncr': { kind: 'table_report', module: 'M23', report: 'ncr_capa_register', title: 'NCR & CAPA Register', period: false },
  'M23-rpt-audit': { kind: 'table_report', module: 'M23', report: 'audit_programme', title: 'Audit Programme Status', period: false },
  'M23-rpt-repeat': { kind: 'table_report', module: 'M23', report: 'repeat_failure', title: 'Repeat-Failure Escalation', period: false },
  'M23-rpt-copq': { kind: 'table_report', module: 'M23', report: 'copq_analysis', title: 'CoPQ Analysis', period: false },
  'M23-rpt-review': { kind: 'table_report', module: 'M23', report: 'management_review', title: 'Management Review Pack', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M23-form-ncr': {
    kind: 'model_form',
    model: 'fix.ncr',
    title: 'NCR',
    back: 'M23-ncr',
    status: { field: 'state', labels: {
      new: 'New', root_cause: 'Root Cause Identified', capa_open: 'CAPA Open',
      verification: 'Verification', closed: 'Closed' } },
    sections: [
      { title: 'Nonconformance', note: 'Source, severity and description; identify the root cause, then open a CAPA from the NCR record.',
        fields: [
          { name: 'source', required: true, label: 'Source' },
          { name: 'severity', required: true, label: 'Severity' },
          { name: 'order_id', label: 'Service Order' },
          { name: 'description', required: true, type: 'text', label: 'Description' },
          { name: 'root_cause', type: 'text', label: 'Root Cause' },
          { name: 'disposition', required: true, label: 'Disposition (ISO 9001 8.7.1)' },
          { name: 'concession_approved_by_id', label: 'Concession approved by' },
          { name: 'disposition_note', type: 'text', label: 'Disposition note' },
          { name: 'state', required: true, label: 'State' }
        ] }
    ]
  },

  'M23-form-capa': {
    kind: 'model_form',
    model: 'fix.capa',
    title: 'CAPA',
    back: 'M23-capa',
    status: { field: 'state', labels: {
      open: 'Open', implemented: 'Implemented', verified: 'Verified', closed: 'Closed' } },
    sections: [
      { title: 'Corrective & Preventive Action', note: 'Open → implemented → verified → closed; verification needs a note recorded on the CAPA.',
        fields: [
          { name: 'ncr_id', required: true, label: 'NCR' },
          { name: 'owner_id', required: true, label: 'Owner' },
          { name: 'due_on', label: 'Due On' },
          { name: 'corrective_action', required: true, type: 'text', label: 'Corrective Action' },
          { name: 'preventive_action', type: 'text', label: 'Preventive Action' },
          { name: 'effectiveness_result', label: 'Effectiveness (ISO 9001 10.2.1)' },
          { name: 'verified_by_id', label: 'Verified by' },
          { name: 'verification_note', type: 'text', label: 'Verification evidence' },
          { name: 'state', required: true, label: 'State' }
        ] }
    ]
  },

  'M23-form-audit': {
    kind: 'model_form',
    model: 'fix.internal.audit',
    title: 'Audit Finding',
    back: 'M23-internal',
    status: { field: 'state', labels: {
      planned: 'Planned', executed: 'Executed', reported: 'Reported' } },
    sections: [
      { title: 'Internal Audit', note: 'Branch, date, auditor and scope; executing the audit lets findings (NCRs) be linked to it.',
        fields: [
          { name: 'branch_id', required: true, label: 'Branch' },
          { name: 'scheduled_on', required: true, label: 'Scheduled On' },
          { name: 'auditor_id', required: true, label: 'Auditor' },
          { name: 'scope', label: 'Scope' },
          { name: 'state', required: true, label: 'State' }
        ] }
    ]
  },

  'M23-form-checklist': {
    kind: 'model_form',
    model: 'fix.qms.checklist',
    title: 'Checklist Template',
    back: 'M23-checklists',
    status: { field: 'state', labels: {
      draft: 'Draft', published: 'Published', retired: 'Retired' } },
    sections: [
      { title: 'Checklist Template', note: 'Type, ISO clause, item count and version; publishing makes it available to quality gates.',
        fields: [
          { name: 'name', required: true, label: 'Checklist Name' },
          { name: 'checklist_type', required: true, label: 'Type' },
          { name: 'iso_clause', label: 'ISO Clause' },
          { name: 'item_count', label: 'Items' },
          { name: 'version', label: 'Version' },
          { name: 'state', required: true, label: 'State' }
        ] }
    ]
  },

  'M23-form-policy': {
    kind: 'model_form',
    model: 'fix.qms.policy',
    title: 'Policy & Objective',
    back: 'M23-policy',
    status: { field: 'state', labels: {
      draft: 'Draft', approved: 'Approved', reviewed: 'Reviewed' } },
    sections: [
      { title: 'Objective', note: 'One quality objective with target and actual; approving it is the management commitment.',
        fields: [
          { name: 'name', required: true, label: 'Policy / Objective Name' },
          { name: 'year', required: true, label: 'Year' },
          { name: 'objective', label: 'Quality Objective' },
          { name: 'target', label: 'Target' },
          { name: 'actual', label: 'Actual' },
          { name: 'unit', label: 'Unit' },
          { name: 'owner_id', label: 'Owner' },
          { name: 'state', required: true, label: 'State' }
        ] },
      { title: 'Policy Text', fields: [
          { name: 'policy_text', type: 'text', label: 'Policy Statement' }
        ] }
    ]
  },

  'M23-form-certification': {
    kind: 'model_form',
    model: 'fix.qms.certification',
    title: 'Certification / Surveillance',
    back: 'M23-external',
    status: { field: 'result', labels: {
      pending: 'Pending', passed: 'Passed', minor_ncs: 'Passed with Minor NCs',
      major_ncs: 'Major NCs', failed: 'Failed' } },
    sections: [
      { title: 'Certification Audit', note: 'Stage 1/2, surveillance or recertification; the result and validity date are the certificate record.',
        fields: [
          { name: 'name', required: true, label: 'Audit Reference' },
          { name: 'standard', required: true, label: 'Standard' },
          { name: 'body', label: 'Certification Body' },
          { name: 'certificate_no', label: 'Certificate No' },
          { name: 'audit_type', required: true, label: 'Audit Type' },
          { name: 'audit_date', required: true, label: 'Audit Date' },
          { name: 'valid_until', label: 'Valid Until' },
          { name: 'result', required: true, label: 'Result' }
        ] }
    ]
  },


  /* ===== master-data forms (batch 2) — D365 in-workspace ===== */
  'M23-form-process': {
    kind: 'model_form',
    model: 'fix.qms.process',
    title: "QMS Process",
    back: 'M23-processes',
    sections: [
      { title: "QMS Process", note: "A QMS process: the owner, the inputs/outputs and the KPIs that show it is in control.",
        fields: [
          { name: 'name', required: true, label: "Name" },
          { name: 'code', required: true, label: "Code" },
          { name: 'company_id', required: true, label: "Company" },
          { name: 'process_type', required: true, label: "Process Type" },
          { name: 'state', required: true, label: "State" },
          { name: 'process_owner_id', label: "Process Owner" },
          { name: 'iso_clause', label: "ISO 9001 Clause" },
          { name: 'inputs', label: "Inputs" }
        ] }
    ]
  },
  'M23-form-gate': {
    kind: 'model_form',
    model: 'fix.qms.gate',
    title: "Quality Gate",
    back: 'M23-gates',
    sections: [
      { title: "Quality Gate", note: "A quality gate that must pass before the next stage; the checklist result is recorded.",
        fields: [
          { name: 'name', required: true, label: "Name" },
          { name: 'code', required: true, label: "Code" },
          { name: 'company_id', required: true, label: "Company" },
          { name: 'state', required: true, label: "State" },
          { name: 'sequence', label: "Sequence" },
          { name: 'stage', label: "Process Stage" },
          { name: 'mandatory_checklist_id', label: "Mandatory Checklist" },
          { name: 'blocking', label: "Blocks Progression" }
        ] }
    ]
  },
  'M23-form-review': {
    kind: 'model_form',
    model: 'fix.qms.review',
    title: "Management Review",
    back: 'M23-review',
    sections: [
      { title: "Management Review", note: "A management review record: the inputs reviewed and the decisions taken.",
        fields: [
          { name: 'name', required: true, label: "Name" },
          { name: 'company_id', required: true, label: "Company" },
          { name: 'review_date', required: true, label: "Review Date" },
          { name: 'state', required: true, label: "State" },
          { name: 'chairperson_id', label: "Chairperson" },
          { name: 'attendees', label: "Attendees" },
          { name: 'agenda', type: 'text', label: "Agenda" },
          { name: 'decisions', type: 'text', label: "Decisions" }
        ] }
    ]
  },


  /* ===== triage coverage screens ===== */
  'M23-qms-copq': { kind: 'model_list', model: 'fix.qms.copq',
    cols: ['name', 'amount', 'company_id', 'period', 'category', 'currency_id', 'source_ref'] },

  'M23-form-qms-copq': {
    kind: 'model_form',
    model: 'fix.qms.copq',
    title: "Qms Copq",
    back: 'M23-qms-copq',
    sections: [
      { title: "Qms Copq", note: "Opened from the module's own record set. Every field here is the model's real field; the workflow rules live on the model and are not bypassed by this form.",
        fields: [
          { name: 'name', required: true, label: "Name" },
          { name: 'amount', required: true, label: "Amount" },
          { name: 'company_id', required: true, label: "Company" },
          { name: 'period', required: true, label: "Period" },
          { name: 'category', required: true, label: "Category" },
          { name: 'currency_id', required: true, label: "Currency" },
          { name: 'source_ref', label: "Source Ref" }
        ] }
    ]
  },

};

export const REPORT_ROUTES = {
  'M23:NCR & CAPA Register': 'M23-rpt-ncr',
  'M23:Audit Programme Status': 'M23-rpt-audit',
  'M23:Repeat-Failure Escalation': 'M23-rpt-repeat',
  'M23:CoPQ Analysis': 'M23-rpt-copq',
  'M23:Management Review Pack': 'M23-rpt-review'
};

export const FORM_MODELS = {
  'M23:NCR': 'fix.ncr',
  'M23:CAPA': 'fix.capa',
  'M23:Audit Finding': 'fix.internal.audit',
  'M23:Checklist Template': 'fix.qms.checklist'
};

export const FORM_CHIPS = {
  'M23:QMS Process': 'M23-form-process',
  'M23:Quality Gate': 'M23-form-gate',
  'M23:Management Review': 'M23-form-review',
  'M23:NCR': 'M23-form-ncr',
  'M23:CAPA': 'M23-form-capa',
  'M23:Audit Finding': 'M23-form-audit',
  'M23:Checklist Template': 'M23-form-checklist',
  'M23:__by_model__': {
    'fix.qms.copq': 'M23-form-qms-copq',
    'fix.qms.process': 'M23-form-process',
    'fix.qms.gate': 'M23-form-gate',
    'fix.qms.review': 'M23-form-review',
    'fix.ncr': 'M23-form-ncr',
    'fix.capa': 'M23-form-capa',
    'fix.internal.audit': 'M23-form-audit',
    'fix.qms.checklist': 'M23-form-checklist',
    'fix.qms.policy': 'M23-form-policy',
    'fix.qms.certification': 'M23-form-certification'
  },
  'M23:__by_screen__': {
    'M23-qms-copq': 'M23-form-qms-copq',
    'M23-processes': 'M23-form-process',
    'M23-gates': 'M23-form-gate',
    'M23-review': 'M23-form-review',
    'M23-ncr': 'M23-form-ncr',
    'M23-rca': 'M23-form-ncr',
    'M23-capa': 'M23-form-capa',
    'M23-internal': 'M23-form-audit',
    'M23-checklists': 'M23-form-checklist',
    'M23-policy': 'M23-form-policy',
    'M23-external': 'M23-form-certification'
  }
};

export const CREATE = {
  M23: { screen: 'M23-form-ncr', model: 'fix.ncr', label: 'NCR' }
};
