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
    { l: 'STP Share', m: 'stp_share', suffix: '%' }
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
      { id: 'M63-inbox', en: 'Unified Task Inbox', bn: 'একত্র কাজের ইনবক্স', t: 'g' }
    ]}
  ],
  reports: ['Automation Rate by Process', 'Approval Cycle Time', 'Escalation Analysis', 'Rule Change Log'],
  forms: ['Workflow Definition', 'Approval Chain', 'Business Rule'],
  cross: ['All modules consume the engine', 'M60 SoD', 'M52 approval matrix', 'M29 access'],
  freg: { src: 54, sub: [
    ['1', 'Workflow Engine', 11], ['2', 'Approval Chains', 10], ['3', 'DoA Matrix', 6],
    ['4', 'Business Rules', 9], ['5', 'Scheduled & Event Jobs', 7],
    ['6', 'Task Inbox', 5], ['7', 'Audit & Performance', 6]
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
    cols: ['decision_domain', 'threshold', 'approver_role', 'notes'] },
  'M63-substitution': { kind: 'model_list', model: 'fix.approval.substitution', stateField: 'state',
    cols: ['name', 'absent_approver_id', 'delegate_id', 'start_date', 'end_date', 'state'],
    actions: [{ m: 'action_activate', l: 'Activate' }, { m: 'action_expire', l: 'Expire' }] },
  'M63-rules': { kind: 'model_list', model: 'fix.business.rule',
    cols: ['code', 'name', 'domain_area', 'rule_type', 'version', 'last_changed_by', 'last_changed_on', 'active'],
    actions: [{ m: 'action_new_version', l: 'New Version' }] },
  'M63-simulation': { kind: 'table_report', module: 'M63', report: 'automation_rate', title: 'Rule Simulation', period: false },
  'M63-inbox': { kind: 'model_list', model: 'fix.workflow.task', stateField: 'state',
    cols: ['name', 'task_type', 'instance_id', 'assigned_to_id', 'created_at', 'due_at', 'decision', 'state'],
    actions: [
      { m: 'action_approve', l: 'Approve' },
      { m: 'action_reject', l: 'Reject' }
    ] },

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
      { title: 'Instance', note: 'A running instance can be completed, failed or escalated; the escalation feeds the escalation report.',
        fields: [
          { name: 'automation_id', label: 'Definition' },
          { name: 'res_model', label: 'Record Model' },
          { name: 'res_id', label: 'Record ID' },
          { name: 'started_at', required: true, label: 'Started At' },
          { name: 'state', required: true, label: 'State' }
        ] }
    ]
  },

  'M63-form-doa': {
    kind: 'model_form',
    model: 'fix.approval.matrix',
    title: 'Approval Chain (DoA Level)',
    back: 'M63-doa',
    sections: [
      { title: 'Delegation of Authority', note: 'One threshold per decision domain and currency (database UNIQUE). The approver role is the chain level that owns decisions above this amount.',
        fields: [
          { name: 'decision_domain', required: true, label: 'Decision Domain' },
          { name: 'threshold', required: true, label: 'Threshold' },
          { name: 'approver_role', required: true, label: 'Approver Role' },
          { name: 'notes', label: 'Notes' }
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
      { title: 'Substitution', note: 'While active, the delegate receives the absent approver\'s task-inbox items; end cannot precede start (database CHECK).',
        fields: [
          { name: 'absent_approver_id', required: true, label: 'Absent Approver' },
          { name: 'delegate_id', required: true, label: 'Delegate' },
          { name: 'start_date', required: true, label: 'Start' },
          { name: 'end_date', required: true, label: 'End' },
          { name: 'reason', label: 'Reason' },
          { name: 'state', required: true, label: 'State' }
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
      { title: 'Task', note: 'Approve or reject records the decision and stamps the time — the cycle-time report reads those stamps.',
        fields: [
          { name: 'task_type', required: true, label: 'Task Type' },
          { name: 'instance_id', label: 'Workflow Instance' },
          { name: 'assigned_to_id', label: 'Assigned To' },
          { name: 'created_at', required: true, label: 'Created At' },
          { name: 'due_at', label: 'Due At' },
          { name: 'state', required: true, label: 'State' }
        ] }
    ]
  }
};

export const REPORT_ROUTES = {
  'M63:Automation Rate by Process': 'M63-rpt-rate',
  'M63:Approval Cycle Time': 'M63-rpt-cycle',
  'M63:Escalation Analysis': 'M63-rpt-esc',
  'M63:Rule Change Log': 'M63-rpt-rules'
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
    'M63-inbox': 'M63-form-task'
  }
};

export const CREATE = {
  M63: { screen: 'M63-form-automation', model: 'fix.automation', label: 'Workflow Definition' }
};
