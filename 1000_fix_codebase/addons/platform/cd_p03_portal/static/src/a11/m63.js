/** @odoo-module **/
/* A11 · Insights & Intelligence — M63 Process Automation (full build; the
 * inline stub showed a fake event-stream card).
 * Registry-faithful: 4 groups / 8 screens / 4 reports / 3 forms / freg 54.
 * Backend: cd_workflow_engine (fix.automation AUT register, fix.approval.matrix
 * DoA) + the new ops models (instances, unified task inbox, business rules,
 * approval substitution). */

export const MODULE = {
  area: 'A11', code: 'M63', en: 'Process Automation', title: 'M63 · Process Automation',
  bn: 'প্রসেস অটোমেশন', icon: '⚙️',
  desc: 'Workflow definitions and the instance monitor, scheduled jobs, the delegation-of-authority matrix, substitution and out-of-office, the business-rule repository with simulation, and the unified task inbox with escalation.',
  kpis: [
    { l: 'Automation Rate', m: 'automation_rate', suffix: '%' },
    { l: 'Open Workflows', m: 'open_workflows' },
    { l: 'Avg Approval Time', m: 'avg_approval_time', suffix: ' h' },
    { l: 'Rule Repository', m: 'rule_repository' },
    { l: 'Escalations MTD', m: 'escalations_mtd' },
    { l: 'STP Share', m: 'stp_share', suffix: '%' },
    { l: 'Approvals Pending', m: 'approvals_pending' },
    { l: 'Pending > 72 h', m: 'approvals_overdue' },
    { l: 'Approver = Creator', m: 'approver_is_creator' },
    { l: 'Median Approval', m: 'approval_median_hours', suffix: ' h' },
    { l: 'A02 Variance Self-Approved', m: 'a02_variance_self_approved' },
    { l: 'A02 Cert Self-Verified', m: 'a02_cert_self_verified' },
    { l: 'A02 Delivery OTP', m: 'a02_delivery_otp_pct', suffix: '%' },
    { l: 'A02 Completion Evidence', m: 'a02_completion_evidence_pct', suffix: '%' }
  ],
  groups: [
    { en: 'Engine', screens: [
      { id: 'M63-definitions', en: 'Workflow Definitions', bn: 'ওয়ার্কফ্লো সংজ্ঞা', t: 'g' },
      { id: 'M63-monitor', en: 'Instance Monitor', bn: 'ইনস্ট্যান্স মনিটর', t: 'g' },
      { id: 'M63-jobs', en: 'Scheduled Jobs', bn: 'নির্ধারিত কাজ', t: 'g' }
    ]},
    { en: 'Approvals', screens: [
      { id: 'M63-doa', en: 'Delegation of Authority', bn: 'ক্ষমতার প্রতিনিধিত্ব', t: 'g' },
      { id: 'M63-substitution', en: 'Substitution / OOO', bn: 'প্রতিনিধি', t: 'g' }
    ]},
    { en: 'Rules', screens: [
      { id: 'M63-rules', en: 'Business-Rule Repository', bn: 'ব্যবসায়িক নিয়ম', t: 'g' },
      { id: 'M63-simulation', en: 'Rule Simulation', bn: 'নিয়ম সিমুলেশন', t: 'r' }
    ]},
    { en: 'Task Inbox', screens: [
      { id: 'M63-inbox', en: 'Awaiting My Approval', bn: 'আমার অনুমোদনের অপেক্ষায়', t: 'g' },
      { id: 'M63-tasks', en: 'Unified Task Inbox', bn: 'একত্র কাজের ইনবক্স', t: 'g' },
      { id: 'M63-requests', en: 'Approval Requests', bn: 'অনুমোদনের অনুরোধ', t: 'g' },
      { id: 'M63-history', en: 'Approval History', bn: 'অনুমোদনের ইতিহাস', t: 'g' },
      { id: 'M63-rpt-approval', en: 'Approval KPIs', bn: 'অনুমোদন সূচক', t: 'r' },
      { id: 'M63-rpt-a02', en: 'A02 Control KPIs', bn: 'A02 নিয়ন্ত্রণ সূচক', t: 'r' }
    ]}
  ],
  reports: ['Automation Rate by Process', 'Approval Cycle Time', 'Escalation Analysis', 'Rule Change Log', 'Approval KPIs'],
  forms: ['Workflow Definition', 'Approval Chain', 'Business Rule'],
  cross: ['All modules consume the engine', 'M60 SoD', 'M52 approval matrix', 'M29 access'],
  freg: { src: 54, sub: [
    ['1', 'Workflow Engine', 11, { model: 'fix.automation', cols: ['code', 'trigger', 'engine', 'engine_ref', 'failure_policy', 'active'], screens: ['M63-definitions', 'M63-monitor'] }],
    ['2', 'Approval Chains', 10, { model: 'fix.workflow.task', cols: ['name', 'instance_id', 'assigned_to_id', 'due_at', 'decision', 'state'], screens: ['M63-inbox', 'M63-substitution'], domain: [['task_type', '=', 'approval']] }],
    ['3', 'DoA Matrix', 6, { model: 'fix.approval.matrix', cols: ['decision_domain', 'threshold', 'approver_role', 'notes'], screens: ['M63-doa'] }],
    ['4', 'Business Rules', 9, { model: 'fix.business.rule', cols: ['code', 'name', 'domain_area', 'rule_type', 'version', 'active'], screens: ['M63-rules', 'M63-simulation'] }],
    ['5', 'Scheduled & Event Jobs', 7, { model: 'fix.automation', cols: ['code', 'trigger', 'engine', 'engine_ref', 'active'], screens: ['M63-jobs'], domain: [['engine', '=', 'airflow']] }],
    ['6', 'Task Inbox', 5, { model: 'fix.workflow.task', cols: ['name', 'task_type', 'assigned_to_id', 'due_at', 'state'], screens: ['M63-inbox'] }],
    ['7', 'Audit & Performance', 6, { model: 'fix.workflow.instance', cols: ['name', 'automation_id', 'started_at', 'finished_at', 'escalated', 'state'], screens: ['M63-monitor'] }]
  ] }
};

export const SCREENS = {
  'M63-definitions': { kind: 'model_list', model: 'fix.automation',
    cols: ['code', 'trigger', 'engine', 'engine_ref', 'failure_policy', 'active'] },
  'M63-monitor': { kind: 'model_list', model: 'fix.workflow.instance', stateField: 'state',
    cols: ['name', 'automation_id', 'res_model', 'res_id', 'started_at', 'finished_at', 'escalated', 'state'],
    actions: [
      { m: 'action_complete', l: 'Complete' },
      { m: 'action_fail', l: 'Mark Failed' },
      { m: 'action_escalate', l: 'Escalate' }
    ] },
  'M63-jobs': { kind: 'model_list', model: 'fix.automation',
    cols: ['code', 'trigger', 'engine', 'engine_ref', 'active'],
    domain: [['engine', '=', 'airflow']] },
  'M63-doa': { kind: 'model_list', model: 'fix.approval.matrix',
    cols: ['name', 'decision_domain', 'res_model', 'approval_policy', 'sla_hours', 'max_escalations',
      'final_action', 'date_from', 'date_to', 'active'],
    actions: [{ m: 'action_test_rule', l: 'Test Rule on a Record', ask: 'Record id to simulate against', kwarg: 'res_id' }],
    note: 'The rule book the approval engine reads. The DOFA ladder sets the tier; a row sets how the approval runs. A new ruling is a new dated row, not an edit.' },
  'M63-substitution': { kind: 'model_list', model: 'fix.approval.substitution', stateField: 'state',
    cols: ['name', 'absent_approver_id', 'delegate_id', 'start_date', 'end_date', 'state'],
    actions: [{ m: 'action_activate', l: 'Activate' }, { m: 'action_expire', l: 'Expire' }] },
  'M63-rules': { kind: 'model_list', model: 'fix.business.rule',
    cols: ['code', 'name', 'domain_area', 'rule_type', 'version', 'last_changed_by', 'last_changed_on', 'active'],
    actions: [{ m: 'action_new_version', l: 'New Version' }] },
  'M63-simulation': { kind: 'table_report', module: 'M63', report: 'automation_rate', title: 'Rule Simulation', period: false },
  'M63-inbox': { kind: 'model_list', model: 'fix.workflow.task', stateField: 'state',
    cols: ['name', 'res_name', 'tier', 'amount', 'requested_by_id', 'justification', 'on_behalf_of_id', 'due_at', 'state'],
    domain: [['is_mine', '=', true], ['state', '=', 'pending']],
    actions: [
      { m: 'action_approve', l: 'Approve' },
      { m: 'action_reject', l: 'Reject', ask: 'Why is this rejected?', kwarg: 'comment' },
      { m: 'action_return', l: 'Return for Information', ask: 'What information is needed?', kwarg: 'comment' }
    ],
    note: 'Only tasks assigned to you. Approving runs the record rules (tier, segregation of duties, justification) under your name.' },
  'M63-tasks': { kind: 'model_list', model: 'fix.workflow.task', stateField: 'state',
    cols: ['name', 'task_type', 'res_name', 'assigned_user_id', 'on_behalf_of_id', 'created_at', 'due_at', 'decision', 'state'] },
  'M63-requests': { kind: 'model_list', model: 'fix.approval.request', stateField: 'state',
    cols: ['name', 'res_name', 'res_model', 'tier', 'amount', 'requested_by_id', 'requested_at', 'escalation_level', 'decided_by_id', 'cycle_hours', 'state'] },
  'M63-history': { kind: 'model_list', model: 'fix.approval.history',
    cols: ['at', 'request_id', 'event', 'user_id', 'on_behalf_of_id', 'tier', 'amount', 'comment'],
    note: 'Append-only: the server refuses every edit and deletion.' },
  'M63-rpt-approval': { kind: 'table_report', module: 'M63', report: 'approval_kpis', title: 'Approval KPIs', period: false },
  'M63-rpt-a02': { kind: 'table_report', module: 'M63', report: 'a02_controls', title: 'A02 Control KPIs', period: false },

  /* Report chips -> their own computed pack */
  'M63-rpt-rate': { kind: 'table_report', module: 'M63', report: 'automation_rate', title: 'Automation Rate by Process', period: false },
  'M63-rpt-cycle': { kind: 'table_report', module: 'M63', report: 'approval_cycle_time', title: 'Approval Cycle Time', period: false },
  'M63-rpt-esc': { kind: 'table_report', module: 'M63', report: 'escalation_analysis', title: 'Escalation Analysis', period: false },
  'M63-rpt-rules': { kind: 'table_report', module: 'M63', report: 'rule_change_log', title: 'Rule Change Log', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M63-form-automation': {
    kind: 'model_form',
    model: 'fix.automation',
    title: 'Workflow Definition',
    back: 'M63-definitions',
    sections: [
      { title: 'Definition', note: 'One row of the AUT register with its named engine: an Odoo automated action, an Airflow DAG or a domain service. The trigger records what starts it.',
        fields: [
          { name: 'code', required: true, label: 'Code' },
          { name: 'trigger', required: true, label: 'Trigger' },
          { name: 'engine', required: true, label: 'Engine' },
          { name: 'engine_ref', label: 'Engine Reference' },
          { name: 'failure_policy', label: 'Failure Policy' },
          { name: 'action', required: true, type: 'text', label: 'Action (what runs)' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },

  'M63-form-instance': {
    kind: 'model_form',
    model: 'fix.workflow.instance',
    title: 'Workflow Instance',
    back: 'M63-monitor',
    status: { field: 'state', labels: {
      running: 'Running', completed: 'Completed', failed: 'Failed', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Instance', note: 'A running instance can be completed, failed or escalated; the escalation feeds the escalation report. Its start, finish and state are set by those actions, never typed. The DoA Administrator keeps this register.',
        fields: [
          { name: 'automation_id', label: 'Definition' },
          { name: 'res_model', label: 'Record Model' },
          { name: 'res_id', label: 'Record ID' },
          { name: 'started_at', readonly: true, label: 'Started At' },
          { name: 'finished_at', readonly: true, label: 'Finished At' },
          { name: 'escalated', readonly: true, label: 'Escalated' },
          { name: 'state', readonly: true, label: 'State' }
        ] }
    ]
  },

  'M63-form-doa': {
    kind: 'model_form',
    model: 'fix.approval.matrix',
    title: 'Approval Chain (DoA Level)',
    back: 'M63-doa',
    sections: [
      { title: 'Delegation of Authority', note: 'Only a DoA Administrator changes the rule book. One row per decision domain, model, currency and effective date; a new ruling is a new dated row. The condition must be a valid domain on the target model (checked on save). Threshold and approver role are reference text: the DOFA ladder sets the tier.',
        fields: [
          { name: 'name', label: 'Rule Name' },
          { name: 'decision_domain', required: true, label: 'Decision Domain' },
          { name: 'res_model', label: 'Applies to Model' },
          { name: 'condition', label: 'Condition (domain)' },
          { name: 'threshold', label: 'Threshold' },
          { name: 'approver_role', label: 'Approver Role' },
          { name: 'notes', label: 'Notes' }
        ] },
      { title: 'How the Approval Runs', note: 'An approver group may only narrow who is asked: it must imply the tier group (or the approval\'s own group), else it is ignored, and it must have members. Any one approver or all of them; the SLA before a reminder, counted in working hours on the calendar (empty: the branch calendar, then the company default, then clock hours); how many escalations to the next tier (or the named target); and what happens when those run out too.',
        fields: [
          { name: 'approver_group_id', label: 'Approver Group (no DOFA amount)' },
          { name: 'approval_policy', required: true, label: 'Voting Policy' },
          { name: 'sla_hours', required: true, label: 'SLA (hours)' },
          { name: 'calendar_id', label: 'Working Calendar' },
          { name: 'max_escalations', required: true, label: 'Escalations' },
          { name: 'escalate_to_id', label: 'Escalate To' },
          { name: 'final_action', required: true, label: 'Final Action' },
          { name: 'date_from', label: 'Effective From' },
          { name: 'date_to', label: 'Effective To' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },

  'M63-form-rule': {
    kind: 'model_form',
    model: 'fix.business.rule',
    title: 'Business Rule',
    back: 'M63-rules',
    sections: [
      { title: 'Rule', note: 'Code is unique per company. Validation, derivation, hard-block gate or escalation trigger — the refusal message is what the user sees when a gate fires.',
        fields: [
          { name: 'code', required: true, label: 'Code' },
          { name: 'name', required: true, label: 'Rule Name' },
          { name: 'domain_area', label: 'Process Area' },
          { name: 'rule_type', required: true, label: 'Rule Type' },
          { name: 'expression', required: true, type: 'text', label: 'Rule Expression' },
          { name: 'error_message', label: 'Refusal Message' },
          { name: 'automation_id', label: 'Linked Automation' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },

  'M63-form-substitution': {
    kind: 'model_form',
    model: 'fix.approval.substitution',
    title: 'Substitution / OOO',
    back: 'M63-substitution',
    status: { field: 'state', labels: {
      draft: 'Draft', active: 'Active', expired: 'Expired' } },
    sections: [
      { title: 'Substitution', note: 'Record your own absence (a DoA Administrator or HR manager may record it for you). It starts today or later and is born a draft; you or your manager activate it. The delegate must hold the authority he receives (the same approval tier or higher). While active, the delegate receives your task-inbox items; when it ends they come back to you.',
        fields: [
          { name: 'absent_approver_id', required: true, label: 'Absent Approver' },
          { name: 'delegate_id', required: true, label: 'Delegate' },
          { name: 'start_date', required: true, label: 'Start' },
          { name: 'end_date', required: true, label: 'End' },
          { name: 'reason', label: 'Reason' },
          { name: 'activated_by_id', readonly: true, label: 'Activated By' },
          { name: 'state', readonly: true, label: 'State' }
        ] }
    ]
  },

  'M63-form-task': {
    kind: 'model_form',
    model: 'fix.workflow.task',
    title: 'Task Inbox Entry',
    back: 'M63-inbox',
    status: { field: 'state', labels: {
      pending: 'Pending', done: 'Done', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Task', note: 'Decide it with Approve, Reject or Return. Every field is set by the approval engine and cannot be typed. A task you hold for an absent approver goes back to him if the delegation has ended.',
        fields: [
          { name: 'task_type', readonly: true, label: 'Task Type' },
          { name: 'instance_id', readonly: true, label: 'Workflow Instance' },
          { name: 'res_name', readonly: true, label: 'Record' },
          { name: 'tier', readonly: true, label: 'Tier' },
          { name: 'amount', readonly: true, label: 'Amount' },
          { name: 'requested_by_id', readonly: true, label: 'Requested By' },
          { name: 'assigned_user_id', readonly: true, label: 'Approver' },
          { name: 'on_behalf_of_id', readonly: true, label: 'On Behalf Of' },
          { name: 'assigned_to_id', readonly: true, label: 'Assigned To (employee)' },
          { name: 'created_at', readonly: true, label: 'Created At' },
          { name: 'due_at', readonly: true, label: 'Due At' },
          { name: 'comment', readonly: true, label: 'Decision Comment' },
          { name: 'state', readonly: true, label: 'State' }
        ] }
    ]
  }
};

export const REPORT_ROUTES = {
  'M63:Automation Rate by Process': 'M63-rpt-rate',
  'M63:Approval Cycle Time': 'M63-rpt-cycle',
  'M63:Escalation Analysis': 'M63-rpt-esc',
  'M63:Rule Change Log': 'M63-rpt-rules',
  'M63:Approval KPIs': 'M63-rpt-approval'
};

export const FORM_MODELS = {
  'M63:Workflow Definition': 'fix.automation',
  'M63:Approval Chain': 'fix.approval.matrix',
  'M63:Business Rule': 'fix.business.rule'
};

export const FORM_CHIPS = {
  'M63:Workflow Definition': 'M63-form-automation',
  'M63:Approval Chain': 'M63-form-doa',
  'M63:Business Rule': 'M63-form-rule',
  'M63:__by_model__': {
    'fix.automation': 'M63-form-automation',
    'fix.approval.matrix': 'M63-form-doa',
    'fix.business.rule': 'M63-form-rule',
    'fix.workflow.instance': 'M63-form-instance',
    'fix.approval.substitution': 'M63-form-substitution',
    'fix.workflow.task': 'M63-form-task'
  },
  'M63:__by_screen__': {
    'M63-definitions': 'M63-form-automation',
    'M63-jobs': 'M63-form-automation',
    'M63-doa': 'M63-form-doa',
    'M63-rules': 'M63-form-rule',
    'M63-monitor': 'M63-form-instance',
    'M63-substitution': 'M63-form-substitution',
    'M63-inbox': 'M63-form-task',
    'M63-tasks': 'M63-form-task'
  }
};

export const CREATE = {
  M63: { screen: 'M63-form-automation', model: 'fix.automation', label: 'Workflow Definition' }
};
