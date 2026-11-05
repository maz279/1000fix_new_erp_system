/** @odoo-module **/
/* A10 · Governance, Risk & Quality — M23 Quality Management (ISO 9001).
 * Registry-faithful: 4 groups / 14 screens / 5 reports / 5 forms / freg 78. */

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
      { id: 'M23-review', en: 'Management Review', bn: 'ব্যবস্থাপনা পর্যালোচনা', t: 'g' },
      { id: 'M23-review-inputs', en: 'Review Inputs (9.3.2)', bn: 'পর্যালোচনা উপাদান', t: 'g' },
      { id: 'M23-review-actions', en: 'Review Actions (9.3.3)', bn: 'পর্যালোচনা কর্ম', t: 'g' }
    ]},
    { en: 'Analytics', screens: [
      { id: 'M23-stat', en: 'Pareto & Control Charts', bn: 'প্যারেটো', t: 'r' },
      { id: 'M23-copq', en: 'Cost of Poor Quality', bn: 'নিম্ন গুণগত ব্যয়', t: 'r' }
    ]}
  ],
  reports: ['NCR & CAPA Register', 'Audit Programme Status', 'Repeat-Failure Escalation', 'CoPQ Analysis', 'Management Review Pack'],
  forms: ['NCR', 'CAPA', 'Audit Finding', 'Checklist Template', 'Review Action'],
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
    actions: [{ m: 'action_approve', l: 'Approve (QM)' }] },
  'M23-processes': { kind: 'model_list', model: 'fix.qms.process',
    cols: ['code', 'name', 'process_owner_id', 'iso_clause', 'process_type', 'state'],
    actions: [{ m: 'action_retire', l: 'Retire (QM)' }] },
  'M23-checklists': { kind: 'model_list', model: 'fix.qms.checklist', stateField: 'state',
    cols: ['name', 'checklist_type', 'iso_clause', 'item_count', 'version', 'state'],
    actions: [{ m: 'action_publish', l: 'Publish (QM)' }, { m: 'action_retire', l: 'Retire (QM)' }] },
  'M23-gates': { kind: 'model_list', model: 'fix.qms.gate',
    cols: ['sequence', 'code', 'name', 'stage', 'mandatory_checklist_id', 'blocking', 'state'],
    actions: [{ m: 'action_retire', l: 'Retire (QM)' }] },
  'M23-ncr': { kind: 'model_list', model: 'fix.ncr', stateField: 'state',
    cols: ['name', 'source', 'severity', 'disposition', 'root_cause', 'state'],
    actions: [
      { m: 'action_set_root_cause', l: 'Set Root Cause',
        asks: [{ label: 'Root cause (5-Why / 8D analysis)', kwarg: 'root_cause' }] },
      { m: 'action_open_capa', l: 'Open CAPA',
        asks: [
          { label: 'Corrective action', kwarg: 'corrective_action' },
          { label: 'Preventive action (major/critical require one)', kwarg: 'preventive_action' },
          { label: 'Owner employee ID', kwarg: 'owner_id', number: true }
        ] },
      { m: 'action_dispose', l: 'Dispose',
        asks: [
          { label: 'Disposition (rework / repair / replace / return / scrap / use_as_is)', kwarg: 'disposition' },
          { label: 'What was done with the output (ISO 9001 8.7.2)', kwarg: 'note' }
        ] },
      { m: 'action_close', l: 'Close' }
    ] },
  'M23-rca': { kind: 'model_list', model: 'fix.ncr', stateField: 'state',
    cols: ['name', 'severity', 'root_cause', 'state'] },
  'M23-capa': { kind: 'model_list', model: 'fix.capa', stateField: 'state',
    cols: ['ncr_id', 'severity', 'owner_id', 'due_on', 'effectiveness_result', 'state'],
    actions: [{ m: 'action_implement', l: 'Implement' },
              { m: 'action_verify', l: 'Verify',
                asks: [
                  { label: 'Verification evidence note (ISO 9001 10.2.2)', kwarg: 'note' },
                  { label: 'Effective? (yes / no)', kwarg: 'effective' }
                ] },
              { m: 'action_close', l: 'Close' }] },
  'M23-internal': { kind: 'model_list', model: 'fix.internal.audit', stateField: 'state',
    cols: ['branch_id', 'scheduled_on', 'auditor_id', 'scope', 'state'],
    actions: [{ m: 'action_execute', l: 'Execute',
                asks: [{ label: 'Checklist capture (P11 offline payload JSON)', kwarg: 'payload' }] },
              { m: 'action_report', l: 'Report' }] },
  'M23-external': { kind: 'model_list', model: 'fix.qms.certification', stateField: 'result',
    cols: ['name', 'standard', 'body', 'audit_type', 'audit_date', 'valid_until', 'result'],
    actions: [{ m: 'action_pass', l: 'Mark Passed' },
              { m: 'action_record_result', l: 'Record Result',
                asks: [{ label: 'Result (minor_ncs / major_ncs / failed / pending)', kwarg: 'result' }] }] },
  'M23-review': { kind: 'model_list', model: 'fix.qms.review', stateField: 'state',
    cols: ['name', 'review_date', 'chairperson_id', 'inputs_missing', 'open_actions', 'state'],
    actions: [{ m: 'action_pull_inputs', l: 'Pull Inputs (9.3.2)' },
              { m: 'action_hold', l: 'Mark Held' },
              { m: 'action_close', l: 'Close — routes to Tier 5',
                asks: [{ label: 'Why is this review ready to close? (routed to top management, DOFA Tier 5)', kwarg: 'justification' }] }] },
  'M23-review-inputs': { kind: 'model_list', model: 'fix.qms.review.input',
    cols: ['review_id', 'kind', 'metric', 'source_count', 'pulled_on', 'summary'] },
  'M23-review-actions': { kind: 'model_list', model: 'fix.qms.review.action', stateField: 'state',
    cols: ['review_id', 'name', 'owner_id', 'due_on', 'state', 'done_on'],
    actions: [{ m: 'action_done', l: 'Mark Done',
                asks: [{ label: 'Completion note (evidence the action happened)', kwarg: 'note' }] }] },
  'M23-stat': { kind: 'table_report', module: 'M23', report: 'repeat_failure', title: 'Pareto — Repeat Failures', period: false },
  'M23-copq': { kind: 'table_report', module: 'M23', report: 'copq_analysis', title: 'Cost of Poor Quality', period: false },

  /* Report chips -> their own computed pack */
  'M23-rpt-ncr': { kind: 'table_report', module: 'M23', report: 'ncr_capa_register', title: 'NCR & CAPA Register', period: false },
  'M23-rpt-audit': { kind: 'table_report', module: 'M23', report: 'audit_programme', title: 'Audit Programme Status', period: false },
  'M23-rpt-repeat': { kind: 'table_report', module: 'M23', report: 'repeat_failure', title: 'Repeat-Failure Escalation', period: false },
  'M23-rpt-copq': { kind: 'table_report', module: 'M23', report: 'copq_analysis', title: 'CoPQ Analysis', period: false },
  'M23-rpt-review': { kind: 'table_report', module: 'M23', report: 'management_review', title: 'Management Review Pack', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  /* A10 Q1–Q3: the workflow fields (state, disposition, verdicts, stamped
   * approvers) are NOT form inputs anymore — they move only through the
   * listed actions, which stamp the acting user and enforce the gates. */
  'M23-form-ncr': {
    kind: 'model_form',
    model: 'fix.ncr',
    title: 'NCR',
    back: 'M23-ncr',
    status: { field: 'state', labels: {
      new: 'New', root_cause: 'Root Cause Identified', capa_open: 'CAPA Open',
      verification: 'Verification', closed: 'Closed' } },
    sections: [
      { title: 'Nonconformance', note: 'Source, severity and what failed; the root cause, disposition and closure move through the row actions (ISO 9001 8.7).',
        fields: [
          { name: 'source', required: true, label: 'Source' },
          { name: 'severity', required: true, label: 'Severity' },
          { name: 'order_id', label: 'Service Order' },
          { name: 'description', required: true, type: 'text', label: 'Description' }
        ] },
      { title: 'Analysis & Disposition', note: 'Working fields — the root cause lands via Set Root Cause, the disposition via Dispose (a use-as-is concession is authorised by the Quality Manager).',
        fields: [
          { name: 'root_cause', type: 'text', label: 'Root Cause' },
          { name: 'containment', type: 'text', label: 'Containment (ISO 9001 8.7.1 f)' },
          { name: 'disposition_note', type: 'text', label: 'Disposition note' }
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
      { title: 'Corrective & Preventive Action', note: 'Open → implemented → verified → closed; the effectiveness verdict is given by the Quality Manager through the Verify action — never the owner or implementer.',
        fields: [
          { name: 'ncr_id', required: true, label: 'NCR' },
          { name: 'severity', required: true, label: 'Severity' },
          { name: 'owner_id', required: true, label: 'Owner' },
          { name: 'due_on', label: 'Due On' },
          { name: 'corrective_action', required: true, type: 'text', label: 'Corrective Action' },
          { name: 'preventive_action', type: 'text', label: 'Preventive Action' }
        ] },
      { title: 'Verification', note: 'Stamps of the implementer and the verifier, with the evidence note — read-only record of who decided (ISO 9001 10.2.2).',
        fields: [
          { name: 'implemented_by_id', label: 'Implemented by' },
          { name: 'verification_note', type: 'text', label: 'Verification evidence' }
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
      { title: 'Internal Audit', note: 'Branch, date, auditor and scope. The audited processes link on the back-office form (an auditor may not own one); the checklist capture and report move through the row actions (ISO 9001 9.2).',
        fields: [
          { name: 'branch_id', required: true, label: 'Branch' },
          { name: 'scheduled_on', required: true, label: 'Scheduled On' },
          { name: 'auditor_id', required: true, label: 'Auditor' },
          { name: 'scope', label: 'Scope' },
          { name: 'offline_payload', type: 'text', label: 'Checklist Capture (P11)' }
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
          { name: 'version', label: 'Version' }
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
          { name: 'owner_id', label: 'Owner' }
        ] },
      { title: 'Policy Text', note: 'The certified statement: once approved the text is frozen — next year brings a new record (A10 S6).', fields: [
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
      { title: 'Certification Audit', note: 'The certificate record — typed by the Quality Manager only; the result moves through Mark Passed (certificate document attached) or Record Result (A10 Q3).',
        fields: [
          { name: 'name', required: true, label: 'Audit Reference' },
          { name: 'standard', required: true, label: 'Standard' },
          { name: 'body', label: 'Certification Body' },
          { name: 'certificate_no', label: 'Certificate No' },
          { name: 'certificate_doc_id', label: 'Certificate Document' },
          { name: 'audit_type', required: true, label: 'Audit Type' },
          { name: 'audit_date', required: true, label: 'Audit Date' },
          { name: 'valid_until', label: 'Valid Until' }
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
      { title: "Management Review (ISO 9.3.1)", note: "Top management conducts the review: the chairperson is named before it is held.",
        fields: [
          { name: 'name', required: true, label: "Name" },
          { name: 'company_id', required: true, label: "Company" },
          { name: 'review_date', required: true, label: "Review Date" },
          { name: 'chairperson_id', label: "Chairperson" },
          { name: 'attendees', label: "Attendees" },
          { name: 'agenda', type: 'text', label: "Agenda" }
        ] },
      { title: "Inputs (ISO 9.3.2)", note: "Pulled by 'Pull Inputs' onto the Review Inputs screen — one line per required kind (audit results, CAPA status, customer feedback, process performance, prior actions, external providers), each a count of records the system holds. Never typed.",
        fields: [
          { name: 'inputs_missing', readonly: true, label: "Missing Inputs" }
        ] },
      { title: "Decisions & Outputs (ISO 9.3.3)", note: "The decisions narrative explains what top management decided; the outputs are TRACKED ACTIONS (Review Actions screen) with owners and due dates. A decision recorded only as prose tracks nothing — the model refuses to close it. Closure routes to DOFA Tier 5.",
        fields: [
          { name: 'decisions', type: 'text', label: "Decisions" },
          { name: 'open_actions', readonly: true, label: "Open Actions" },
          { name: 'approval_state', readonly: true, label: "Approval" },
          { name: 'closed_on', readonly: true, label: "Closed On" },
          { name: 'closed_by_id', readonly: true, label: "Closed By" }
        ] }
    ]
  },

  'M23-form-review-action': {
    kind: 'model_form',
    model: 'fix.qms.review.action',
    title: "Review Action",
    back: 'M23-review-actions',
    sections: [
      { title: "Tracked Action (ISO 9.3.3)", note: "One output of a management review: what was decided, who owns it, when it is due. Completion is stamped by 'Mark Done' — by the owner or the Quality Manager, never typed.",
        fields: [
          { name: 'review_id', required: true, label: "Review" },
          { name: 'name', type: 'text', required: true, label: "Decision / Action" },
          { name: 'owner_id', required: true, label: "Owner" },
          { name: 'due_on', label: "Due" },
          { name: 'state', readonly: true, label: "State" },
          { name: 'done_on', readonly: true, label: "Done On" },
          { name: 'done_by_id', readonly: true, label: "Done By" }
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
  'M23:Checklist Template': 'fix.qms.checklist',
  'M23:Review Action': 'fix.qms.review.action'
};

export const FORM_CHIPS = {
  'M23:QMS Process': 'M23-form-process',
  'M23:Quality Gate': 'M23-form-gate',
  'M23:Management Review': 'M23-form-review',
  'M23:NCR': 'M23-form-ncr',
  'M23:CAPA': 'M23-form-capa',
  'M23:Audit Finding': 'M23-form-audit',
  'M23:Checklist Template': 'M23-form-checklist',
  'M23:Review Action': 'M23-form-review-action',
  'M23:__by_model__': {
    'fix.qms.copq': 'M23-form-qms-copq',
    'fix.qms.process': 'M23-form-process',
    'fix.qms.gate': 'M23-form-gate',
    'fix.qms.review': 'M23-form-review',
    'fix.qms.review.action': 'M23-form-review-action',
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
    'M23-review-actions': 'M23-form-review-action',
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
