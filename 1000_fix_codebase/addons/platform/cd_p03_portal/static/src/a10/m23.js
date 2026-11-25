/** @odoo-module **/
/* A10 · Governance, Risk & Quality — M23 Quality Management (ISO 9001).
 * Registry-faithful: 4 groups / 14 screens / 5 reports / 5 forms / freg 78.
 * M23 capture audit (2026-11-19): each sub-module page captures its own
 * spec records — objectives, change assessments, checklist items, RCA, the
 * CAPA action plan, the audit programme, auditor register, findings and
 * evidence releases (cd_qms_process models/fix_qms_capture.py). */

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
    { en: 'Framework', screens: [
      { id: 'M23-policy', en: 'Policy & Objectives', bn: 'নীতি ও উদ্দেশ্য', t: 'g' },
      { id: 'M23-objectives', en: 'Quality Objectives (cascade)', bn: 'গুণগত উদ্দেশ্য', t: 'g' },
      { id: 'M23-processes', en: 'Process Register (ISO map)', bn: 'প্রক্রিয়া রেজিস্টার', t: 'g' },
      { id: 'M23-changes', en: 'Process Change Assessments', bn: 'প্রক্রিয়া পরিবর্তন মূল্যায়ন', t: 'g' },
      { id: 'M23-checklists', en: 'Checklist Authoring', bn: 'চেকলিস্ট রচনা', t: 'g' },
      { id: 'M23-checklist-items', en: 'Checklist Items', bn: 'চেকলিস্ট আইটেম', t: 'g' },
      { id: 'M23-gates', en: 'Quality Gates', bn: 'গুণগত গেট', t: 'g' }
    ]},
    { en: 'Nonconformance', screens: [
      { id: 'M23-ncr', en: 'NCR Management', bn: 'অসঙ্গতি', t: 'g' },
      { id: 'M23-rca', en: 'RCA (5-Why / Ishikawa / 8D)', bn: 'মূল কারণ', t: 'g' },
      { id: 'M23-capa', en: 'CAPA & Verification', bn: 'ক্যাপা', t: 'g' },
      { id: 'M23-capa-actions', en: 'CAPA Action Plan', bn: 'ক্যাপা কর্মপরিকল্পনা', t: 'g' }
    ]},
    { en: 'Audits', screens: [
      { id: 'M23-programmes', en: 'Annual Audit Programme', bn: 'বার্ষিক অডিট কর্মসূচি', t: 'g' },
      { id: 'M23-internal', en: 'Internal Audits', bn: 'অভ্যন্তরীণ অডিট', t: 'g' },
      { id: 'M23-findings', en: 'Audit Findings', bn: 'অডিট পর্যবেক্ষণ', t: 'g' },
      { id: 'M23-auditors', en: 'Auditor Register', bn: 'অডিটর রেজিস্টার', t: 'g' },
      { id: 'M23-external', en: 'Certification & Surveillance', bn: 'সার্টিফিকেশন', t: 'g' },
      { id: 'M23-evidence', en: 'External Evidence Releases', bn: 'প্রমাণ প্রদান', t: 'g' },
      { id: 'M23-review', en: 'Management Review', bn: 'ব্যবস্থাপনা পর্যালোচনা', t: 'g' },
      { id: 'M23-review-inputs', en: 'Review Inputs (9.3.2)', bn: 'পর্যালোচনা উপাদান', t: 'g' },
      { id: 'M23-review-actions', en: 'Review Actions (9.3.3)', bn: 'পর্যালোচনা কর্ম', t: 'g' }
    ]},
    { en: 'Analytics', screens: [
      { id: 'M23-stat', en: 'Pareto & Control Charts', bn: 'প্যারেটো', t: 'r' },
      { id: 'M23-copq', en: 'Cost of Poor Quality', bn: 'নিম্ন গুণগত ব্যয়', t: 'r' },
      { id: 'M23-qms-copq', en: 'CoPQ Ledger', bn: 'নিম্ন গুণগত ব্যয় খতিয়ান', t: 'g' }
    ]}
  ],
  reports: ['NCR & CAPA Register', 'Audit Programme Status', 'Repeat-Failure Escalation', 'CoPQ Analysis', 'Management Review Pack'],
  forms: ['NCR', 'CAPA', 'Audit Finding', 'Checklist Template', 'Review Action',
          'Quality Objective', 'Process Change Assessment', 'Quality Gate', 'Root-Cause Analysis',
          'Internal Audit', 'Audit Programme', 'Auditor', 'Certification / Surveillance',
          'Evidence Release', 'CoPQ Entry'],
  cross: ['M01 Service Orders', 'M34 Complaints', 'M42 Suppliers', 'M24 Documents'],
  freg: { src: 78, sub: [
    ['1', 'Policy & Objectives', 6, { model: 'fix.qms.policy', cols: ['name', 'year', 'objective', 'target', 'actual', 'state'], screens: ['M23-policy', 'M23-objectives'], reports: [], forms: ['Quality Objective'] }],
    ['2', 'Process Register', 7, { model: 'fix.qms.process', cols: ['code', 'name', 'process_owner_id', 'iso_clause', 'review_due', 'state'], screens: ['M23-processes', 'M23-changes'], reports: [], forms: ['Process Change Assessment'] }],
    ['3', 'Checklists & Gates', 10, { model: 'fix.qms.checklist', cols: ['name', 'checklist_type', 'iso_clause', 'item_count', 'version', 'state'], screens: ['M23-checklists', 'M23-checklist-items', 'M23-gates'], reports: [], forms: ['Checklist Template', 'Quality Gate'] }],
    ['4', 'NCR Management', 12, { model: 'fix.ncr', cols: ['name', 'source', 'nc_type', 'severity', 'containment_due', 'state'], screens: ['M23-ncr'], reports: ['NCR & CAPA Register'], forms: ['NCR'] }],
    ['5', 'RCA & CAPA', 14, { model: 'fix.capa', cols: ['ncr_id', 'severity', 'owner_id', 'due_on', 'open_action_count', 'state'], screens: ['M23-rca', 'M23-capa', 'M23-capa-actions'], reports: ['NCR & CAPA Register', 'Repeat-Failure Escalation'], forms: ['Root-Cause Analysis', 'CAPA'] }],
    ['6', 'Audit Programme', 13, { model: 'fix.internal.audit', cols: ['name', 'branch_id', 'scheduled_on', 'auditor_id', 'scope', 'state'], screens: ['M23-programmes', 'M23-internal', 'M23-findings', 'M23-auditors', 'M23-external', 'M23-evidence'], reports: ['Audit Programme Status'], forms: ['Internal Audit', 'Audit Finding', 'Audit Programme', 'Auditor', 'Certification / Surveillance', 'Evidence Release'] }],
    ['7', 'Management Review', 7, { model: 'fix.qms.review', cols: ['name', 'review_date', 'chairperson_id', 'open_actions', 'state'], screens: ['M23-review', 'M23-review-inputs', 'M23-review-actions'], reports: ['Management Review Pack'], forms: ['Review Action'] }],
    ['8', 'Statistics & CoPQ', 9, { model: 'fix.qms.copq', cols: ['name', 'period', 'category', 'ncr_id', 'attributed_cause', 'amount'], screens: ['M23-stat', 'M23-copq', 'M23-qms-copq'], reports: ['CoPQ Analysis', 'Repeat-Failure Escalation'], forms: ['CoPQ Entry'] }]
  ] }
};

export const SCREENS = {
  'M23-policy': { kind: 'model_list', model: 'fix.qms.policy', stateField: 'state',
    cols: ['name', 'year', 'objective', 'target', 'actual', 'unit', 'state'],
    actions: [{ m: 'action_approve', l: 'Approve (QM)' }] },
  'M23-objectives': { kind: 'model_list', model: 'fix.qms.objective',
    cols: ['name', 'policy_id', 'scope_level', 'measure', 'target', 'actual', 'unit', 'attainment', 'owner_id', 'period'] },
  'M23-processes': { kind: 'model_list', model: 'fix.qms.process',
    cols: ['code', 'name', 'process_owner_id', 'iso_clause', 'process_type', 'review_due', 'state'],
    actions: [{ m: 'action_retire', l: 'Retire (QM)' }] },
  'M23-changes': { kind: 'model_list', model: 'fix.qms.change.assessment', stateField: 'state',
    cols: ['name', 'process_id', 'change_summary', 'affects_documents', 'affects_checklists', 'affects_training', 'assessed_by_id', 'state'],
    actions: [{ m: 'action_assess', l: 'Record Assessment' },
              { m: 'action_release', l: 'Release (QM)' },
              { m: 'action_reject', l: 'Reject (QM)',
                asks: [{ label: 'Why is the change rejected?', kwarg: 'reason' }] }] },
  'M23-checklists': { kind: 'model_list', model: 'fix.qms.checklist', stateField: 'state',
    cols: ['name', 'checklist_type', 'iso_clause', 'item_count', 'version', 'state'],
    actions: [{ m: 'action_publish', l: 'Publish (QM)' }, { m: 'action_retire', l: 'Retire (QM)' },
              { m: 'action_new_version', l: 'New Version (QM)' }] },
  'M23-checklist-items': { kind: 'model_list', model: 'fix.qms.checklist.item', create: false,
    cols: ['checklist_id', 'sequence', 'section', 'name', 'response_type', 'acceptance_criteria', 'evidence_required', 'reportable'],
    empty: 'No checklist item yet. Items are authored on a draft checklist template (Checklist Template form, Items grid); a published version is frozen and changes through New Version.' },
  'M23-gates': { kind: 'model_list', model: 'fix.qms.gate',
    cols: ['sequence', 'code', 'name', 'stage', 'mandatory_checklist_id', 'blocking', 'independence_required', 'state'],
    actions: [{ m: 'action_retire', l: 'Retire (QM)' }] },
  'M23-ncr': { kind: 'model_list', model: 'fix.ncr', stateField: 'state',
    cols: ['name', 'source', 'nc_type', 'severity', 'containment_due', 'containment_done_on', 'disposition', 'root_cause', 'state'],
    actions: [
      { m: 'action_record_containment', l: 'Confirm Containment',
        asks: [{ label: 'Containment action taken (leave empty to keep the recorded one)', kwarg: 'note' }] },
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
  'M23-rca': { kind: 'model_list', model: 'fix.qms.rca', stateField: 'state',
    cols: ['name', 'ncr_id', 'ncr_severity', 'method', 'root_cause', 'completed_by_id', 'state'],
    actions: [{ m: 'action_complete', l: 'Complete Analysis' }] },
  'M23-capa': { kind: 'model_list', model: 'fix.capa', stateField: 'state',
    cols: ['ncr_id', 'severity', 'owner_id', 'due_on', 'open_action_count', 'verification_due_on', 'effectiveness_result', 'state'],
    actions: [{ m: 'action_implement', l: 'Implement' },
              { m: 'action_verify', l: 'Verify',
                asks: [
                  { label: 'Verification evidence note (ISO 9001 10.2.2)', kwarg: 'note' },
                  { label: 'Effective? (yes / no)', kwarg: 'effective' }
                ] },
              { m: 'action_close', l: 'Close' }] },
  'M23-capa-actions': { kind: 'model_list', model: 'fix.capa.action', stateField: 'state',
    cols: ['capa_id', 'name', 'owner_id', 'executing_module', 'external_ref', 'due_on', 'done_on', 'state'],
    actions: [{ m: 'action_done', l: 'Mark Done',
                asks: [{ label: 'Evidence the action was done', kwarg: 'note' }] }] },
  'M23-programmes': { kind: 'model_list', model: 'fix.qms.audit.programme', stateField: 'state',
    cols: ['name', 'year', 'planned_count', 'uncovered_processes', 'approved_by_id', 'state'],
    actions: [{ m: 'action_approve', l: 'Approve (QM)' }, { m: 'action_close', l: 'Close (QM)' }] },
  'M23-internal': { kind: 'model_list', model: 'fix.internal.audit', stateField: 'state',
    cols: ['name', 'programme_id', 'branch_id', 'scheduled_on', 'auditor_id', 'scope', 'auditee_acknowledged_on', 'state'],
    actions: [{ m: 'action_execute', l: 'Execute',
                asks: [{ label: 'Checklist capture (P11 offline payload JSON)', kwarg: 'payload' }] },
              { m: 'action_report', l: 'Report' },
              { m: 'action_acknowledge', l: 'Auditee Acknowledges' }] },
  'M23-findings': { kind: 'model_list', model: 'fix.qms.audit.finding', stateField: 'state',
    cols: ['name', 'audit_id', 'classification', 'clause_ref', 'statement', 'ncr_id', 'ncr_state', 'state'],
    actions: [{ m: 'action_raise_ncr', l: 'Raise NCR' },
              { m: 'action_close', l: 'Close (QM)',
                asks: [{ label: 'How the observation / OFI was considered', kwarg: 'note' }] }] },
  'M23-auditors': { kind: 'model_list', model: 'fix.qms.auditor',
    cols: ['employee_id', 'standards', 'qualified_on', 'excluded_branch_ids', 'excluded_process_ids', 'active'] },
  'M23-evidence': { kind: 'model_list', model: 'fix.qms.evidence.release', stateField: 'state',
    cols: ['name', 'certification_id', 'external_party', 'request_note', 'approved_by_id', 'released_on', 'state'],
    actions: [{ m: 'action_approve', l: 'Approve (QM)' },
              { m: 'action_release', l: 'Release' },
              { m: 'action_refuse', l: 'Refuse (QM)',
                asks: [{ label: 'Why is the release refused?', kwarg: 'reason' }] }] },
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
  'M23-review-inputs': { kind: 'model_list', model: 'fix.qms.review.input', create: false,
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
      { title: 'Nonconformance', note: 'Where it came from, what kind it is, how severe and which ISO clause it breaches; any employee may raise one, with a photograph (FR-QMS-021..023, 031).',
        fields: [
          { name: 'source', required: true, label: 'Source' },
          { name: 'nc_type', required: true, label: 'Type' },
          { name: 'severity', required: true, label: 'Severity' },
          { name: 'clause_ref', label: 'ISO Clause Affected' },
          { name: 'order_id', label: 'Service Order' },
          { name: 'description', required: true, type: 'text', label: 'Description' },
          { name: 'evidence_attachment_id', label: 'Photo / Evidence' }
        ] },
      { title: 'Containment', note: 'The interim action, its owner and its deadline, distinct from the corrective action; Confirm Containment stamps it done (FR-QMS-024, ISO 9001 8.7.1 f). A major non-conformance is contained within the declared interval (BRU-QMS-14).',
        fields: [
          { name: 'containment', type: 'text', label: 'Containment Action' },
          { name: 'containment_owner_id', label: 'Containment Owner' },
          { name: 'containment_due', label: 'Containment Due' },
          { name: 'containment_done_on', readonly: true, label: 'Confirmed On' }
        ] },
      { title: 'Analysis & Disposition', note: 'The root cause lands from a completed Root-Cause Analysis (5-Why, Ishikawa or 8D, never a repeat of the symptom); the disposition via Dispose (a use-as-is concession is authorised by the Quality Manager).',
        fields: [
          { name: 'root_cause', readonly: true, type: 'text', label: 'Root Cause' },
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
      { title: 'Verification', note: 'The effectiveness check falls due the observation window after implementation and cannot be given earlier (FR-QMS-035). Stamps of the implementer and the verifier, with the evidence note — read-only record of who decided (ISO 9001 10.2.2).',
        fields: [
          { name: 'observation_window_days', label: 'Observation Window (days)' },
          { name: 'verification_due_on', readonly: true, label: 'Verification Due' },
          { name: 'implemented_by_id', readonly: true, label: 'Implemented by' },
          { name: 'verification_note', type: 'text', label: 'Verification evidence' }
        ] }
    ],
    lines: { field: 'action_ids', title: 'Action Plan',
      note: 'One line per action, with its owner and due date; an action executed in another module (training in M22, a document change in M24, a supplier action in M42) names the record there. The CAPA is implemented only when every action is done with its evidence (FR-QMS-033, BRU-QMS-18).',
      fields: [
        { name: 'name', label: 'Action', required: true },
        { name: 'owner_id', label: 'Owner', required: true },
        { name: 'executing_module', label: 'Executed In', required: true },
        { name: 'external_ref', label: 'Record in That Module' },
        { name: 'due_on', label: 'Due' },
        { name: 'expected_outcome', label: 'Expected Outcome' }
      ] }
  },

  'M23-form-audit': {
    kind: 'model_form',
    model: 'fix.internal.audit',
    title: 'Internal Audit',
    back: 'M23-internal',
    status: { field: 'state', labels: {
      planned: 'Planned', executed: 'Executed', reported: 'Reported' } },
    sections: [
      { title: 'Internal Audit', note: 'The programme it belongs to, the branch, date, auditor, scope and the processes audited. Once the auditor register is kept, the auditor is a registered one and never audits their own area, work or process (BRU-QMS-07); the checklist capture and report move through the row actions (ISO 9001 9.2).',
        fields: [
          { name: 'name', readonly: true, label: 'Reference' },
          { name: 'programme_id', label: 'Programme' },
          { name: 'branch_id', required: true, label: 'Branch' },
          { name: 'scheduled_on', required: true, label: 'Scheduled On' },
          { name: 'auditor_id', required: true, label: 'Auditor' },
          { name: 'scope', required: true, label: 'Scope' },
          { name: 'process_ids', label: 'Audited Processes' },
          { name: 'offline_payload', type: 'text', label: 'Checklist Capture (P11)' }
        ] }
    ],
    grids: [
      { field: 'finding_ids', title: 'Findings', readonlyGrid: true,
        empty: 'No finding yet. While the audit is executed, record each one with the Audit Finding chip; a major or minor finding raises its NCR, and Report raises any still missing.',
        fields: [
          { name: 'name', label: 'Finding' },
          { name: 'classification', label: 'Classification' },
          { name: 'clause_ref', label: 'Clause' },
          { name: 'ncr_id', label: 'NCR' },
          { name: 'state', label: 'State' }
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
    tabs: [
      { id: 'template', label: '1. Template & Items', bn: '১. টেমপ্লেট ও আইটেম', icon: '📋', badge: '5' },
      { id: 'applies', label: '2. Applicability', bn: '২. প্রযোজ্যতা', icon: '🎯', badge: '7' }
    ],
    sections: [
      { tab: 'template', title: 'Checklist Template', note: 'Type, ISO clause and version. The items are authored below; a template with no item is not published, and a published version is frozen — a change is a New Version, so an executed checklist keeps the version it used (FR-QMS-011/012, BRU-QMS-03).',
        fields: [
          { name: 'name', required: true, label: 'Checklist Name' },
          { name: 'checklist_type', required: true, label: 'Type' },
          { name: 'iso_clause', label: 'ISO Clause' },
          { name: 'version', label: 'Version' },
          { name: 'item_count', readonly: true, label: 'Items' }
        ] },
      { tab: 'applies', title: 'Where It Applies', note: 'Which jobs this checklist applies to: device category, brand, repair level, order value band, delivery mode, customer type and branches; an empty rule applies everywhere (FR-QMS-013).',
        fields: [
          { name: 'applies_device_category', label: 'Device Category' },
          { name: 'applies_brand', label: 'Brand' },
          { name: 'applies_repair_level', label: 'Repair Level' },
          { name: 'applies_value_min', label: 'Value From (BDT)' },
          { name: 'applies_value_max', label: 'Value To (BDT)' },
          { name: 'applies_delivery_mode', label: 'Delivery Mode' },
          { name: 'applies_customer_type', label: 'Customer Type' },
          { name: 'applies_branch_ids', label: 'Branches (empty = all)' }
        ] }
    ],
    lines: { field: 'item_ids', title: 'Items',
      note: 'One line per check: what is checked, how it is answered, the acceptance criteria (required for a measurement or reading), the evidence it needs and whether a failure raises an NCR (FR-QMS-011/016/019).',
      fields: [
        { name: 'sequence', label: 'No.' },
        { name: 'section', label: 'Section' },
        { name: 'name', label: 'Item (English)', required: true },
        { name: 'name_bn', label: 'Item (Bengali)' },
        { name: 'response_type', label: 'Response', required: true },
        { name: 'acceptance_criteria', label: 'Acceptance Criteria' },
        { name: 'evidence_required', label: 'Evidence', required: true },
        { name: 'reportable', label: 'Failure Raises NCR' }
      ] }
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
      { title: "QMS Process", note: "A QMS process: its owner, purpose and the ISO 9001 clause it satisfies (FR-QMS-003/005).",
        fields: [
          { name: 'name', required: true, label: "Name" },
          { name: 'code', required: true, label: "Code" },
          { name: 'company_id', required: true, label: "Company" },
          { name: 'process_type', required: true, label: "Process Type" },
          { name: 'process_owner_id', label: "Process Owner" },
          { name: 'iso_clause', label: "ISO 9001 Clause" },
          { name: 'purpose', type: 'text', label: "Purpose" },
          { name: 'review_due', label: "Next Review" }
        ] },
      { title: "Inputs, Outputs & Control", note: "What enters and leaves the process, the processes it interacts with, its controls, the KPI that shows it is in control, and its process map or work instruction controlled in M24 (FR-QMS-003/004). A change to a registered process is released through a Process Change Assessment (BRU-QMS-10).",
        fields: [
          { name: 'inputs', label: "Inputs" },
          { name: 'outputs', label: "Outputs" },
          { name: 'interactions', label: "Interactions" },
          { name: 'controls', type: 'text', label: "Controls" },
          { name: 'kpi_definition', label: "Process KPI" },
          { name: 'work_instruction_id', label: "Process Map / Work Instruction" }
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
          { name: 'checkpoint', required: true, label: "Checkpoint (where the gate bites)" },
          { name: 'mandatory_checklist_id', label: "Mandatory Checklist" },
          { name: 'blocking', label: "Blocks Progression" }
        ] },
      { title: "Independent Inspection", note: "Where a second person, not the technician, must perform the inspection: always, or above an order value; the risk basis is recorded and published to the executing modules (FR-QMS-015, BRU-QMS-02).",
        fields: [
          { name: 'independence_required', label: "Independent Inspection" },
          { name: 'independence_value_threshold', label: "Independent Above (BDT)" },
          { name: 'independence_note', label: "Risk Basis" }
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
    cols: ['name', 'period', 'category', 'ncr_id', 'attributed_cause', 'amount', 'currency_id', 'source_ref'] },

  'M23-form-qms-copq': {
    kind: 'model_form',
    model: 'fix.qms.copq',
    title: "CoPQ Entry",
    back: 'M23-qms-copq',
    sections: [
      { title: "Cost of Poor Quality", note: "One cost of a quality failure in a period: its category (rework, scrap, warranty, complaint handling, inspection, downtime), the amount and the record it comes from (FR-QMS-030).",
        fields: [
          { name: 'period', required: true, label: "Period (YYYY-MM)" },
          { name: 'category', required: true, label: "Category" },
          { name: 'amount', required: true, label: "Amount" },
          { name: 'currency_id', required: true, label: "Currency" },
          { name: 'source_ref', label: "Source Record" },
          { name: 'notes', label: "Notes" }
        ] },
      { title: "Attribution", note: "The non-conformance it belongs to and the cause it is attributed to — process, person, supplier, seller, model, part or training gap — with the basis of the attribution (FR-QMS-029/030).",
        fields: [
          { name: 'ncr_id', label: "NCR" },
          { name: 'attributed_cause', required: true, label: "Attributed Cause" },
          { name: 'attribution_basis', label: "Attribution Basis" }
        ] }
    ]
  },

  /* ===== M23 capture audit (2026-11-19): the spec records each page lacked ===== */
  'M23-form-objective': {
    kind: 'model_form',
    model: 'fix.qms.objective',
    title: 'Quality Objective',
    back: 'M23-objectives',
    sections: [
      { title: 'Objective', note: 'A measurable quality objective of a policy year, with its owner and how it is measured; cascade it from a higher objective to a branch, process or role (ISO 9001 6.2, FR-QMS-001/002).',
        fields: [
          { name: 'name', required: true, label: 'Objective' },
          { name: 'policy_id', required: true, label: 'Quality Policy' },
          { name: 'parent_id', label: 'Cascaded From' },
          { name: 'scope_level', required: true, label: 'Applies To' },
          { name: 'branch_id', label: 'Branch' },
          { name: 'process_id', label: 'Process' },
          { name: 'role', label: 'Role' },
          { name: 'owner_id', required: true, label: 'Owner' }
        ] },
      { title: 'Target & Attainment', note: 'The measurement basis, the target and the actual; attainment is computed (for lower-is-better objectives such as the rework rate, from the target over the actual).',
        fields: [
          { name: 'measure', required: true, label: 'Measurement Basis' },
          { name: 'target', required: true, label: 'Target' },
          { name: 'actual', label: 'Actual' },
          { name: 'unit', label: 'Unit' },
          { name: 'higher_is_better', label: 'Higher Is Better' },
          { name: 'period', required: true, label: 'Period (YYYY or YYYY-MM)' },
          { name: 'review_due', label: 'Next Review' },
          { name: 'attainment', readonly: true, label: 'Attainment %' }
        ] }
    ]
  },

  'M23-form-change': {
    kind: 'model_form',
    model: 'fix.qms.change.assessment',
    title: 'Process Change Assessment',
    back: 'M23-changes',
    status: { field: 'state', labels: {
      draft: 'Draft', assessed: 'Assessed', released: 'Released', rejected: 'Rejected' } },
    sections: [
      { title: 'Proposed Change', note: 'The registered process that changes, what changes and why. The change is released by the Quality Manager only after its QMS impact is assessed and every affected document, checklist and training item is updated (BRU-QMS-10).',
        fields: [
          { name: 'name', readonly: true, label: 'Reference' },
          { name: 'process_id', required: true, label: 'Process' },
          { name: 'change_summary', required: true, type: 'text', label: 'Proposed Change' },
          { name: 'reason', type: 'text', label: 'Reason' }
        ] },
      { title: 'QMS Impact', note: 'Which documents, checklists and training the change touches, and the tick when each is updated; Release refuses while any affected item is not.',
        fields: [
          { name: 'impact_note', type: 'text', label: 'QMS Impact Assessment' },
          { name: 'affects_documents', label: 'Affects Documents' },
          { name: 'documents_updated', label: 'Documents Updated' },
          { name: 'affects_checklists', label: 'Affects Checklists' },
          { name: 'checklists_updated', label: 'Checklists Updated' },
          { name: 'affects_training', label: 'Affects Training' },
          { name: 'training_updated', label: 'Training Updated' },
          { name: 'assessed_by_id', readonly: true, label: 'Assessed By' },
          { name: 'released_by_id', readonly: true, label: 'Released By' }
        ] }
    ]
  },

  'M23-form-rca': {
    kind: 'model_form',
    model: 'fix.qms.rca',
    title: 'Root-Cause Analysis',
    back: 'M23-rca',
    status: { field: 'state', labels: { draft: 'Draft', completed: 'Completed' } },
    tabs: [
      { id: 'problem', label: '1. Problem', bn: '১. সমস্যা', icon: '🔎', badge: '3' },
      { id: 'why', label: '2. 5-Why', bn: '২. ৫-কেন', icon: '❓', badge: '5' },
      { id: 'fish', label: '3. Ishikawa', bn: '৩. ইশিকাওয়া', icon: '🐟', badge: '6' },
      { id: 'eightd', label: '4. 8D', bn: '৪. ৮ডি', icon: '8️⃣', badge: '7' },
      { id: 'cause', label: '5. Root Cause', bn: '৫. মূল কারণ', icon: '🎯', badge: '2' }
    ],
    sections: [
      { tab: 'problem', title: 'Non-Conformance & Method', note: 'The NCR investigated, the method and the symptom as observed. A major or critical non-conformance is investigated by 8D (BRU-QMS-14).',
        fields: [
          { name: 'ncr_id', required: true, label: 'NCR' },
          { name: 'method', required: true, label: 'Method' },
          { name: 'symptom', required: true, type: 'text', label: 'Symptom (what was observed)' }
        ] },
      { tab: 'why', title: '5-Why', note: 'At least three answered whys, each the cause of the one before.',
        fields: [
          { name: 'why_1', label: 'Why 1' },
          { name: 'why_2', label: 'Why 2' },
          { name: 'why_3', label: 'Why 3' },
          { name: 'why_4', label: 'Why 4' },
          { name: 'why_5', label: 'Why 5' }
        ] },
      { tab: 'fish', title: 'Ishikawa (fishbone)', note: 'The candidate causes by category; at least one category is filled.',
        fields: [
          { name: 'cause_people', type: 'text', label: 'People' },
          { name: 'cause_method', type: 'text', label: 'Method' },
          { name: 'cause_machine', type: 'text', label: 'Machine / Tools' },
          { name: 'cause_material', type: 'text', label: 'Material / Parts' },
          { name: 'cause_measurement', type: 'text', label: 'Measurement' },
          { name: 'cause_environment', type: 'text', label: 'Environment' }
        ] },
      { tab: 'eightd', title: '8D Disciplines', note: 'All eight disciplines are recorded for an 8D; D4 is the root cause on the next tab (FR-QMS-027).',
        fields: [
          { name: 'd1_team', type: 'text', label: 'D1 Team' },
          { name: 'd2_problem', type: 'text', label: 'D2 Problem Description' },
          { name: 'd3_containment', type: 'text', label: 'D3 Interim Containment' },
          { name: 'd5_corrective', type: 'text', label: 'D5 Permanent Corrective Action' },
          { name: 'd6_implementation', type: 'text', label: 'D6 Implementation & Validation' },
          { name: 'd7_prevention', type: 'text', label: 'D7 Prevent Recurrence' },
          { name: 'd8_recognition', type: 'text', label: 'D8 Team Recognition / Closure' }
        ] },
      { tab: 'cause', title: 'Root Cause', note: 'Why it happened — never a repeat of the symptom (BRU-QMS-04). Complete Analysis lands it on the NCR, which can then open its CAPA.',
        fields: [
          { name: 'root_cause', required: true, type: 'text', label: 'Root Cause (D4)' },
          { name: 'contributing_factors', type: 'text', label: 'Contributing Factors' }
        ] }
    ]
  },

  'M23-form-capa-action': {
    kind: 'model_form',
    model: 'fix.capa.action',
    title: 'CAPA Action',
    back: 'M23-capa-actions',
    status: { field: 'state', labels: { open: 'Open', done: 'Done' } },
    sections: [
      { title: 'Planned Action', note: 'One action of a CAPA, its owner and due date. Mark Done records the evidence; an action executed in another module names the record there (BRU-QMS-18).',
        fields: [
          { name: 'capa_id', required: true, label: 'CAPA' },
          { name: 'name', required: true, type: 'text', label: 'Action' },
          { name: 'owner_id', required: true, label: 'Owner' },
          { name: 'executing_module', required: true, label: 'Executed In' },
          { name: 'external_ref', label: 'Record in That Module' },
          { name: 'expected_outcome', label: 'Expected Outcome' },
          { name: 'due_on', label: 'Due' },
          { name: 'evidence_note', readonly: true, type: 'text', label: 'Completion Evidence' }
        ] }
    ]
  },

  'M23-form-programme': {
    kind: 'model_form',
    model: 'fix.qms.audit.programme',
    title: 'Audit Programme',
    back: 'M23-programmes',
    status: { field: 'state', labels: { draft: 'Draft', approved: 'Approved', closed: 'Closed' } },
    sections: [
      { title: 'Annual Plan', note: 'The year\'s internal audit plan: the processes and branches in scope, the supplier and seller classes, and the frequency rules; the Quality Manager approves it. Each audit then names its programme (FR-QMS-040, BRU-QMS-17).',
        fields: [
          { name: 'name', required: true, label: 'Programme' },
          { name: 'year', required: true, label: 'Year' },
          { name: 'process_ids', label: 'Processes In Scope' },
          { name: 'branch_ids', label: 'Branches / Workshops In Scope' },
          { name: 'supplier_seller_scope', label: 'Supplier & Seller Classes' },
          { name: 'frequency_note', type: 'text', label: 'Frequency Rules' },
          { name: 'planned_count', readonly: true, label: 'Audits Planned' },
          { name: 'uncovered_processes', readonly: true, label: 'Processes Without an Audit' }
        ] }
    ]
  },

  'M23-form-auditor': {
    kind: 'model_form',
    model: 'fix.qms.auditor',
    title: 'Auditor',
    back: 'M23-auditors',
    sections: [
      { title: 'Auditor Register', note: 'Kept by the Quality Manager: the auditor, the standards they audit, the competence evidence and their own area and work, which they may never audit. Once a company registers an auditor, every audit is assigned from this register (FR-QMS-041, BRU-QMS-07).',
        fields: [
          { name: 'employee_id', required: true, label: 'Auditor' },
          { name: 'standards', required: true, label: 'Standards' },
          { name: 'competence_note', required: true, type: 'text', label: 'Competence Evidence' },
          { name: 'competence_attachment_id', label: 'Certificate' },
          { name: 'qualified_on', required: true, label: 'Qualified On' },
          { name: 'excluded_branch_ids', label: 'Own Area (excluded branches)' },
          { name: 'excluded_process_ids', label: 'Own Work (excluded processes)' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },

  'M23-form-finding': {
    kind: 'model_form',
    model: 'fix.qms.audit.finding',
    title: 'Audit Finding',
    back: 'M23-findings',
    status: { field: 'state', labels: { open: 'Open', ncr_raised: 'NCR Raised', closed: 'Closed' } },
    sections: [
      { title: 'Finding', note: 'Raised while the audit is executed: major or minor non-conformity, observation or opportunity for improvement, with the clause and the objective evidence. A non-conformity raises its NCR (Raise NCR, or automatically when the report is issued) (FR-QMS-043, AUT-QMS-14).',
        fields: [
          { name: 'audit_id', required: true, label: 'Audit' },
          { name: 'classification', required: true, label: 'Classification' },
          { name: 'clause_ref', required: true, label: 'ISO Clause' },
          { name: 'statement', required: true, type: 'text', label: 'Finding' },
          { name: 'evidence', required: true, type: 'text', label: 'Objective Evidence' },
          { name: 'evidence_attachment_id', label: 'Evidence File' },
          { name: 'owner_id', label: 'Auditee Owner' },
          { name: 'ncr_id', readonly: true, label: 'NCR' }
        ] }
    ]
  },

  'M23-form-evidence': {
    kind: 'model_form',
    model: 'fix.qms.evidence.release',
    title: 'Evidence Release',
    back: 'M23-evidence',
    status: { field: 'state', labels: {
      requested: 'Requested', approved: 'Approved', released: 'Released', refused: 'Refused' } },
    sections: [
      { title: 'Evidence Request', note: 'What an external auditor (certification body, brand partner, corporate customer) asked for and the evidence to release. It is released only after a Quality Manager other than the one who recorded it approves, and every release is logged (FR-QMS-046, BRU-QMS-15).',
        fields: [
          { name: 'certification_id', label: 'External Audit' },
          { name: 'external_party', required: true, label: 'Requested By (auditor / body)' },
          { name: 'request_note', required: true, type: 'text', label: 'Evidence Requested' },
          { name: 'document_id', label: 'Document (M24)' },
          { name: 'attachment_id', label: 'Evidence File' },
          { name: 'access_until', label: 'Access Until' },
          { name: 'approved_by_id', readonly: true, label: 'Approved By' }
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
  'M23:Audit Finding': 'fix.qms.audit.finding',
  'M23:Checklist Template': 'fix.qms.checklist',
  'M23:Review Action': 'fix.qms.review.action',
  'M23:Quality Objective': 'fix.qms.objective',
  'M23:Process Change Assessment': 'fix.qms.change.assessment',
  'M23:Quality Gate': 'fix.qms.gate',
  'M23:Root-Cause Analysis': 'fix.qms.rca',
  'M23:Internal Audit': 'fix.internal.audit',
  'M23:Audit Programme': 'fix.qms.audit.programme',
  'M23:Auditor': 'fix.qms.auditor',
  'M23:Certification / Surveillance': 'fix.qms.certification',
  'M23:Evidence Release': 'fix.qms.evidence.release',
  'M23:CoPQ Entry': 'fix.qms.copq'
};

export const FORM_CHIPS = {
  'M23:QMS Process': 'M23-form-process',
  'M23:Quality Gate': 'M23-form-gate',
  'M23:Management Review': 'M23-form-review',
  'M23:NCR': 'M23-form-ncr',
  'M23:CAPA': 'M23-form-capa',
  'M23:Audit Finding': 'M23-form-finding',
  'M23:Checklist Template': 'M23-form-checklist',
  'M23:Review Action': 'M23-form-review-action',
  'M23:Quality Objective': 'M23-form-objective',
  'M23:Process Change Assessment': 'M23-form-change',
  'M23:Root-Cause Analysis': 'M23-form-rca',
  'M23:Internal Audit': 'M23-form-audit',
  'M23:Audit Programme': 'M23-form-programme',
  'M23:Auditor': 'M23-form-auditor',
  'M23:Certification / Surveillance': 'M23-form-certification',
  'M23:Evidence Release': 'M23-form-evidence',
  'M23:CoPQ Entry': 'M23-form-qms-copq',
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
    'fix.qms.certification': 'M23-form-certification',
    'fix.qms.objective': 'M23-form-objective',
    'fix.qms.change.assessment': 'M23-form-change',
    'fix.qms.rca': 'M23-form-rca',
    'fix.capa.action': 'M23-form-capa-action',
    'fix.qms.audit.programme': 'M23-form-programme',
    'fix.qms.auditor': 'M23-form-auditor',
    'fix.qms.audit.finding': 'M23-form-finding',
    'fix.qms.evidence.release': 'M23-form-evidence'
  },
  'M23:__by_screen__': {
    'M23-qms-copq': 'M23-form-qms-copq',
    'M23-processes': 'M23-form-process',
    'M23-gates': 'M23-form-gate',
    'M23-review': 'M23-form-review',
    'M23-review-actions': 'M23-form-review-action',
    'M23-ncr': 'M23-form-ncr',
    'M23-rca': 'M23-form-rca',
    'M23-capa': 'M23-form-capa',
    'M23-internal': 'M23-form-audit',
    'M23-checklists': 'M23-form-checklist',
    'M23-policy': 'M23-form-policy',
    'M23-external': 'M23-form-certification',
    'M23-objectives': 'M23-form-objective',
    'M23-changes': 'M23-form-change',
    'M23-capa-actions': 'M23-form-capa-action',
    'M23-programmes': 'M23-form-programme',
    'M23-auditors': 'M23-form-auditor',
    'M23-findings': 'M23-form-finding',
    'M23-evidence': 'M23-form-evidence'
  }
};

export const CREATE = {
  M23: { screen: 'M23-form-ncr', model: 'fix.ncr', label: 'NCR' }
};
