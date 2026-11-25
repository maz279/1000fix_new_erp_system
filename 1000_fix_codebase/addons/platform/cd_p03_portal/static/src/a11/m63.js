/** @odoo-module **/
/* A11 · Insights & Intelligence — M63 Process Automation (full build; the
 * inline stub showed a fake event-stream card).
 * Registry contract (scratch/a11_deep/registry_a11.json M63): 4 groups / 8
 * screens / 4 reports / 3 forms / freg 54. This fragment is a SUPERSET and
 * says so: 5 groups / 16 screens / 5 reports / 12 forms / freg 54 (7
 * sub-modules). The 8 registry screens keep the registry's English and
 * Bengali labels; every extra screen is listed here so the drift is visible
 * rather than claimed away.
 * Backend: cd_workflow_engine (fix.automation AUT register with runtime-
 * verified engine bindings, fix.approval.matrix DoA) + the ops models
 * (instances, unified task inbox, business rules, approval substitution). */

export const MODULE = {
  area: 'A11', code: 'M63', en: 'Process Automation', title: 'M63 · Process Automation',
  bn: 'প্রসেস অটোমেশন', icon: '⚙️',
  desc: 'Workflow definitions and the instance monitor, scheduled jobs, the delegation-of-authority matrix, substitution and out-of-office, the business-rule repository with simulation, and the unified task inbox with escalation.',
  kpis: [
    /* The registry's six, in its order. A None value renders "—", never 0:
       automation_rate and stp_share have no denominator until routine work is
       registered (see the captions below). */
    { l: 'Automation Rate', m: 'automation_rate', suffix: '%',
      empty: 'No routine work registered yet — the rate has no denominator' },
    { l: 'Open Workflows', m: 'open_workflows' },
    { l: 'Avg Approval Time', m: 'avg_approval_time', suffix: ' h' },
    { l: 'Rule Repository', m: 'rule_repository' },
    { l: 'Escalations MTD', m: 'escalations_mtd',
      empty: 'No approval history readable — escalations cannot be counted' },
    { l: 'STP Share', m: 'stp_share', suffix: '%',
      empty: 'No routine work registered yet — the straight-through share has no denominator' },
    /* A4-F01: the automation register counts what really executes, not rows.
       implemented = full + verified binding; partial = partial + verified;
       planned = nothing implements it; broken is reported by the gap report. */
    { l: 'Automations Bound', m: 'automations' },
    { l: 'Partially Automated', m: 'automations_partial' },
    { l: 'Planned / Not Implemented', m: 'automations_planned' },
    /* Renamed (A4-F07): it counts in-force DoA MATRIX rows never simulated,
       while Rule Repository counts business rules — two different things. */
    { l: 'DoA Rules Unsimulated', m: 'rules_unsimulated' },
    { l: 'Interventions MTD', m: 'interventions_mtd' },
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
      { id: 'M63-jobs', en: 'Scheduled Jobs', bn: 'নির্ধারিত কাজ', t: 'g' },
      { id: 'M63-events', en: 'Event-Triggered Automations', bn: 'ইভেন্ট-চালিত অটোমেশন', t: 'g' }
    ]},
    { en: 'Approvals', screens: [
      { id: 'M63-doa', en: 'Delegation of Authority', bn: 'ক্ষমতার প্রতিনিধিত্ব', t: 'g' },
      { id: 'M63-substitution', en: 'Substitution / OOO', bn: 'প্রতিনিধি', t: 'g' }
    ]},
    { en: 'Rules', screens: [
      { id: 'M63-rules', en: 'Business-Rule Repository', bn: 'ব্যবসায়িক নিয়ম', t: 'g' },
      { id: 'M63-simulation', en: 'Rule Simulation', bn: 'নিয়ম সিমুলেশন', t: 'g' }
    ]},
    { en: 'Task Inbox', screens: [
      /* The registry names M63-inbox "Unified Task Inbox" with the registry's
       * Bengali label; M63-tasks (extra) is the all-assignees view. */
      { id: 'M63-inbox', en: 'Unified Task Inbox', bn: 'একত্র কাজের ইনবক্স', t: 'g' },
      { id: 'M63-tasks', en: 'All Approval Tasks', bn: 'সব অনুমোদন কাজ', t: 'g' },
      { id: 'M63-requests', en: 'Approval Requests', bn: 'অনুমোদনের অনুরোধ', t: 'g' },
      { id: 'M63-history', en: 'Approval History', bn: 'অনুমোদনের ইতিহাস', t: 'g' },
      { id: 'M63-rpt-approval', en: 'Approval KPIs', bn: 'অনুমোদন সূচক', t: 'r' },
      { id: 'M63-rpt-a02', en: 'A02 Control KPIs', bn: 'A02 নিয়ন্ত্রণ সূচক', t: 'r' }
    ]},
    { en: 'Audit & Performance', screens: [
      { id: 'M63-register', en: 'Routine Work Register', bn: 'নিয়মিত কাজের নিবন্ধন', t: 'g' },
      { id: 'M63-interventions', en: 'Manual Interventions', bn: 'হস্তক্ষেপের রেকর্ড', t: 'g' }
    ]}
  ],
  reports: ['Automation Rate by Process', 'Approval Cycle Time', 'Escalation Analysis', 'Rule Change Log', 'Approval KPIs'],
  forms: ['Workflow Definition', 'Approval Chain', 'Business Rule', 'Substitution / OOO', 'Rule Simulation',
    'Scheduled Workflow', 'Event-Triggered Automation', 'Automation Register Entry', 'Manual Intervention',
    'Authority Ladder', 'Ladder Band', 'Scheduled Job Registration'],
  cross: ['Every module with approvals', 'M60 SoD in approvals', 'M29 identity context'],
  /* M63 capture audit (2026-11-18): each page offers the record it holds.
   * Page 2 captured nothing (its substitution list had no button); page 3
   * could not reach the value ladder the DoA tier comes from; page 4 had no
   * simulation; page 5 showed only scheduled workflows; page 7 typed a
   * workflow instance by hand instead of the routine-work register and the
   * recorded manual intervention. */
  freg: { src: 54, sub: [
    ['1', 'Workflow Engine', 11, { model: 'fix.automation', cols: ['code', 'trigger', 'engine', 'engine_ref', 'implementation', 'binding_state', 'coverage_state', 'executor_active', 'failure_policy', 'active'], screens: ['M63-definitions', 'M63-monitor'], reports: ['Automation Rate by Process'], forms: ['Workflow Definition'] }],
    ['2', 'Approval Chains', 10, { model: 'fix.workflow.task', cols: ['name', 'instance_id', 'assigned_to_id', 'due_at', 'decision', 'state'], screens: ['M63-requests', 'M63-inbox', 'M63-substitution', 'M63-history'], reports: ['Approval Cycle Time', 'Approval KPIs', 'Escalation Analysis'], forms: ['Substitution / OOO', 'Approval Chain'], create: 'M63-form-substitution', domain: [['task_type', '=', 'approval']] }],
    ['3', 'DoA Matrix', 6, { model: 'fix.approval.matrix', cols: ['decision_domain', 'threshold', 'approver_role', 'approver_group_id', 'escalate_to_id', 'date_from', 'date_to', 'approval_policy', 'sla_hours', 'max_escalations', 'final_action', 'active'], screens: ['M63-doa'], reports: [], forms: ['Approval Chain', 'Authority Ladder', 'Ladder Band'] }],
    ['4', 'Business Rules', 9, { model: 'fix.business.rule', cols: ['code', 'name', 'domain_area', 'rule_type', 'version', 'active'], screens: ['M63-rules', 'M63-simulation'], reports: ['Rule Change Log', 'Automation Rate by Process'], forms: ['Business Rule', 'Rule Simulation'] }],
    /* The real scheduled jobs are Odoo ir.cron rows (the new scheduled_jobs
     * pack); the register rows whose engine is odoo_cron are their submissions. */
    ['5', 'Scheduled & Event Jobs', 7, { model: 'fix.automation', cols: ['code', 'trigger', 'engine', 'engine_ref', 'implementation', 'binding_state', 'coverage_state', 'active'], screens: ['M63-jobs', 'M63-events'], reports: [], forms: ['Scheduled Workflow', 'Event-Triggered Automation', 'Scheduled Job Registration'], create: 'M63-form-scheduled', domain: [['engine', '=', 'odoo_cron']] }],
    ['6', 'Task Inbox', 5, { model: 'fix.workflow.task', cols: ['name', 'task_type', 'assigned_to_id', 'due_at', 'state'], screens: ['M63-inbox', 'M63-tasks'], reports: ['Approval Cycle Time'], forms: [], create: false }],
    ['7', 'Audit & Performance', 6, { model: 'fix.workflow.instance', cols: ['name', 'automation_id', 'started_at', 'finished_at', 'escalated', 'state'], screens: ['M63-monitor', 'M63-interventions', 'M63-register'], reports: ['Approval KPIs', 'Escalation Analysis', 'Automation Rate by Process'], forms: ['Manual Intervention', 'Automation Register Entry'], create: 'M63-form-intervention' }]
  ] }
};

export const SCREENS = {
  /* A4-F01: the reader must be able to see WHAT executes each row. Binding /
   * Coverage / Executor active are computed from the engine reference at read
   * time, never stored, and matching with the gap report by construction. */
  'M63-definitions': { kind: 'model_list', model: 'fix.automation',
    cols: ['code', 'trigger', 'engine', 'engine_ref', 'implementation', 'binding_state', 'coverage_state', 'executor_active', 'failure_policy', 'active'],
    note: 'Engine names the mechanism that really executes the row: odoo_cron (cron:<module>.<xmlid>), odoo_method (method:<model>.<method>), event_consumer (consumer:<event_type>) or manual (nothing executes it). Implementation says how much of the action the executor performs; Binding/Coverage are verified at read time.' },
  'M63-monitor': { kind: 'model_list', model: 'fix.workflow.instance', stateField: 'state', create: false,
    cols: ['name', 'automation_id', 'res_model', 'res_id', 'started_at', 'finished_at', 'escalated', 'state'],
    /* Each button is a recorded manual intervention (FR-BPA-008): it asks why,
     * and the operator, time, reason and state before and after are kept. */
    actions: [
      { m: 'action_complete', l: 'Complete', ask: 'Why is this instance completed by hand?', kwarg: 'reason' },
      { m: 'action_fail', l: 'Mark Failed', ask: 'Why is this instance marked failed?', kwarg: 'reason' },
      { m: 'action_escalate', l: 'Escalate', ask: 'Why is this instance escalated?', kwarg: 'reason' },
      { m: 'action_terminate', l: 'Terminate', ask: 'Why is this instance terminated?', kwarg: 'reason' }
    ],
    empty: 'No workflow instance yet. An instance is started by its automation engine; an operator acts on a running one with a recorded intervention.' },
  /* A11 pass 1, D-L13: this screen listed the 16 register rows whose engine
   * claimed Airflow — DAGs that do not exist. It now serves the scheduled_jobs
   * report: the REAL ir.cron estate, its owning module and its next run. */
  'M63-jobs': { kind: 'table_report', module: 'M63', report: 'scheduled_jobs',
    title: 'Scheduled Jobs', period: false },
  'M63-events': { kind: 'model_list', model: 'fix.automation',
    cols: ['code', 'trigger', 'engine', 'engine_ref', 'implementation', 'binding_state', 'coverage_state', 'executor_active', 'failure_policy', 'active'],
    domain: [['engine', '=', 'event_consumer']],
    note: 'Automations executed by an outbox event consumer (consumer:<event_type>): the published event type names the consumer row that does the work. The register records which event starts it; the consumer itself lives in the owning module.' },
  'M63-doa': { kind: 'model_list', model: 'fix.approval.matrix',
    /* A11 pass 1, D-L12: the grid showed neither who approves nor up to how
     * much. Threshold is money (৳), approver_role the reconciled R-nn role. */
    cols: ['name', 'decision_domain', 'res_model', 'threshold', 'approver_role', 'approver_group_id',
      'approval_policy', 'sla_hours', 'max_escalations', 'escalate_to_id', 'final_action',
      'date_from', 'date_to', 'active'],
    actions: [{ m: 'action_test_rule', l: 'Test Rule on a Record', ask: 'Record id to simulate against', kwarg: 'res_id' }],
    note: 'The rule book the approval engine reads. The DOFA ladder sets the tier; a row sets how the approval runs. Threshold is the displayed authority limit in ৳ and approver_role the reconciled role — both reference text: the coded group or the ladder authorises, the row only narrows and times it. A new ruling is a new dated row, not an edit.' },
  'M63-substitution': { kind: 'model_list', model: 'fix.approval.substitution', stateField: 'state',
    cols: ['name', 'absent_approver_id', 'delegate_id', 'start_date', 'end_date', 'state'],
    actions: [{ m: 'action_activate', l: 'Activate' }, { m: 'action_expire', l: 'Expire' }] },
  'M63-rules': { kind: 'model_list', model: 'fix.business.rule',
    cols: ['code', 'name', 'domain_area', 'rule_type', 'version', 'last_changed_by', 'last_changed_on', 'active'],
    actions: [{ m: 'action_new_version', l: 'New Version' }] },
  /* Was the automation-rate report under this name (2026-11-18). */
  'M63-simulation': { kind: 'model_list', model: 'fix.rule.simulation',
    cols: ['name', 'matrix_id', 'date_from', 'date_to', 'evaluated_count', 'matched_count', 'changed_count', 'run_by_id', 'run_at'],
    empty: 'No rule has been simulated yet. Simulate an approval rule over a past period before it takes effect.',
    note: 'Each run shows what an approval rule would have changed over a past period. It reads only: nothing is requested, sent or posted.' },
  'M63-register': { kind: 'model_list', model: 'fix.automation.register',
    cols: ['name', 'process_area', 'owning_module', 'volume_per_month', 'automated', 'automation_id', 'stp_rate', 'automated_volume', 'last_reviewed_on'],
    actions: [{ m: 'action_mark_reviewed', l: 'Mark Reviewed' }],
    empty: 'No routine work registered. Every recurring operational task, with its monthly volume, is the denominator of the 85% automation target.',
    note: 'The automation rate is the automated volume over all registered volume. A task counts as automated only when it names the automation that does it.' },
  'M63-interventions': { kind: 'model_list', model: 'fix.workflow.intervention',
    cols: ['name', 'instance_id', 'action', 'reason', 'operator_id', 'at', 'state_before', 'state_after'],
    empty: 'No manual intervention recorded.',
    note: 'Append-only: the server refuses every edit and deletion.' },
  /* An approval task is raised by the engine when a document needs a decision;
   * it is evidence of who decided what, and is never typed in (2026-11-12). */
  'M63-inbox': { kind: 'model_list', model: 'fix.workflow.task', stateField: 'state', create: false,
    empty: 'Nothing waits for your decision. A task arrives here when a document you may approve is submitted; tasks are raised by the approval engine and cannot be typed in.',
    cols: ['name', 'res_name', 'tier', 'amount', 'requested_by_id', 'justification', 'on_behalf_of_id', 'due_at', 'state'],
    domain: [['is_mine', '=', true], ['state', '=', 'pending']],
    actions: [
      { m: 'action_approve', l: 'Approve' },
      { m: 'action_reject', l: 'Reject', ask: 'Why is this rejected?', kwarg: 'comment' },
      { m: 'action_return', l: 'Return for Information', ask: 'What information is needed?', kwarg: 'comment' }
    ],
    note: 'Only tasks assigned to you. Approving runs the record rules (tier, segregation of duties, justification) under your name.' },
  'M63-tasks': { kind: 'model_list', model: 'fix.workflow.task', stateField: 'state', create: false,
    empty: 'No approval task yet. The approval engine raises a task whenever a document needs a decision.',
    cols: ['name', 'task_type', 'res_name', 'assigned_user_id', 'on_behalf_of_id', 'created_at', 'due_at', 'decision', 'state'] },
  'M63-requests': { kind: 'model_list', model: 'fix.approval.request', create: false, stateField: 'state',
    cols: ['name', 'res_name', 'res_model', 'tier', 'amount', 'requested_by_id', 'requested_at', 'escalation_level', 'decided_by_id', 'cycle_hours', 'state'] },
  'M63-history': { kind: 'model_list', model: 'fix.approval.history', create: false,
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
      { title: 'Definition', note: 'One row of the AUT register. Engine names what really executes it: odoo_cron (a scheduled action, reference cron:<module>.<xmlid>), odoo_method (a model method run on a document step, method:<model>.<method>), event_consumer (an outbox event consumer, consumer:<event_type>) or manual (no automation — implementation must then be "none"). An active row whose reference does not resolve is refused on save.',
        fields: [
          { name: 'code', required: true, label: 'Code' },
          { name: 'trigger', required: true, label: 'Trigger' },
          { name: 'engine', required: true, label: 'Engine' },
          { name: 'engine_ref', label: 'Engine Reference (cron: | method: | consumer:)' },
          { name: 'implementation', required: true, label: 'Implementation' },
          { name: 'failure_policy', label: 'Failure Policy' },
          { name: 'action', required: true, type: 'text', label: 'Action (what runs)' },
          { name: 'executor_note', type: 'text', label: 'Executor Note (module + file:line)' },
          { name: 'active', label: 'Active' }
        ] },
      { title: 'Verified Binding', note: 'Computed at read time from the engine reference: Binding (verified / unresolved / manual), Coverage (implemented = full + verified, partial, planned, broken = claims an implementation its reference cannot back) and whether the executor itself is switched on. Never typed.',
        fields: [
          { name: 'binding_state', readonly: true, label: 'Binding' },
          { name: 'coverage_state', readonly: true, label: 'Coverage' },
          { name: 'executor_active', readonly: true, label: 'Executor Active' }
        ] }
    ]
  },

  /* Read-only since the capture audit (2026-11-18): an instance is started by
   * its automation engine and changed only by a recorded intervention. */
  'M63-form-instance': {
    kind: 'model_form',
    model: 'fix.workflow.instance',
    title: 'Workflow Instance',
    back: 'M63-monitor',
    create: false, pick: 'A workflow instance is started by its automation engine: open one from the Instance Monitor.',
    status: { field: 'state', labels: {
      running: 'Running', completed: 'Completed', failed: 'Failed', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Instance', note: 'Complete, Mark Failed, Escalate and Terminate on the monitor each record a manual intervention with its reason; the intervention count shows how many.',
        fields: [
          { name: 'automation_id', readonly: true, label: 'Definition' },
          { name: 'res_model', readonly: true, label: 'Record Model' },
          { name: 'res_id', readonly: true, label: 'Record ID' },
          { name: 'started_at', readonly: true, label: 'Started At' },
          { name: 'finished_at', readonly: true, label: 'Finished At' },
          { name: 'escalated', readonly: true, label: 'Escalated' },
          { name: 'intervention_count', readonly: true, label: 'Manual Interventions' },
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

  'M63-form-simulation': {
    kind: 'model_form',
    model: 'fix.rule.simulation',
    title: 'Rule Simulation',
    back: 'M63-simulation',
    tabs: [
      { id: 'run', label: 'Rule & Period', bn: 'নিয়ম ও সময়কাল', icon: '🧪', badge: '3' },
      { id: 'outcome', label: 'What Would Change', bn: 'কী বদলাত', icon: '📊', badge: '11' }
    ],
    sections: [
      { tab: 'run', title: 'Candidate Rule (BRU-BPA-04)', note: 'Choose the approval rule to test, usually a new version not yet in force, and a past period. Saving runs the simulation over the records of that period: for each one the rule selects, it compares how the approval would run under this rule with how it ran (or would run today). Nothing is requested, sent or posted, and the result is kept as evidence.',
        fields: [
          { name: 'matrix_id', required: true, label: 'Candidate Rule' },
          { name: 'date_from', required: true, label: 'Period From' },
          { name: 'date_to', required: true, label: 'Period To' }
        ] },
      { tab: 'outcome', title: 'Outcome', note: 'Set by the run. A rule written for a model outranks a decision-domain rule, so some records may stay where they are.',
        fields: [
          { name: 'rule_snapshot', readonly: true, type: 'text', label: 'Rule as Simulated' },
          { name: 'target_models', readonly: true, label: 'Records Of' },
          { name: 'evaluated_count', readonly: true, label: 'Records Evaluated' },
          { name: 'matched_count', readonly: true, label: 'Selected by the Rule' },
          { name: 'changed_count', readonly: true, label: 'Would Route Differently' },
          { name: 'unreached_count', readonly: true, label: 'Kept by a More Specific Rule' },
          { name: 'truncated', readonly: true, label: 'Capped' },
          { name: 'summary', readonly: true, type: 'text', label: 'Outcome' },
          { name: 'sample_differences', readonly: true, type: 'text', label: 'Sample Differences' },
          { name: 'run_by_id', readonly: true, label: 'Run By' },
          { name: 'run_at', readonly: true, label: 'Run At' }
        ] }
    ]
  },

  'M63-form-register': {
    kind: 'model_form',
    model: 'fix.automation.register',
    title: 'Automation Register Entry',
    back: 'M63-register',
    tabs: [
      { id: 'task', label: 'Routine Task', bn: 'নিয়মিত কাজ', icon: '📋', badge: '5' },
      { id: 'automation', label: 'Automation', bn: 'অটোমেশন', icon: '⚙️', badge: '4' },
      { id: 'review', label: 'Review', bn: 'পর্যালোচনা', icon: '🔍', badge: '3' }
    ],
    sections: [
      { tab: 'task', title: 'Routine Operational Work (AUT-BPA-21)', note: 'One recurring task people or the system do, with how often it happens in a month. Together these rows are the denominator of the 85% automation target.',
        fields: [
          { name: 'name', required: true, label: 'Routine Task' },
          { name: 'process_area', required: true, label: 'Process Area' },
          { name: 'owning_module', label: 'Owning Module (e.g. M19)' },
          { name: 'volume_per_month', required: true, label: 'Volume per Month' },
          { name: 'notes', type: 'text', label: 'Notes' }
        ] },
      { tab: 'automation', title: 'How Much Is Automated', note: 'A task counts as automated only when it names the active automation that does it. The straight-through share is the part completed with no human step; the automated volume follows from it.',
        fields: [
          { name: 'automated', label: 'Automated' },
          { name: 'automation_id', label: 'Automated By' },
          { name: 'stp_rate', label: 'Straight-Through %' },
          { name: 'automated_volume', readonly: true, label: 'Automated Volume' }
        ] },
      { tab: 'review', title: 'Review', note: 'Mark Reviewed on the register list stamps who last confirmed the row and when.',
        fields: [
          { name: 'last_reviewed_on', readonly: true, label: 'Last Reviewed' },
          { name: 'reviewed_by_id', readonly: true, label: 'Reviewed By' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },

  'M63-form-intervention': {
    kind: 'model_form',
    model: 'fix.workflow.intervention',
    title: 'Manual Intervention',
    back: 'M63-interventions',
    sections: [
      { title: 'Intervention (FR-BPA-008, BRU-BPA-23)', note: 'A DoA Administrator or Platform Admin acts on a stuck instance: complete, mark failed or terminate a running one, or escalate it. The reason is required; the operator, time and the state before and after are recorded and never changed. You cannot complete an instance you started yourself.',
        fields: [
          { name: 'instance_id', required: true, label: 'Workflow Instance' },
          { name: 'action', required: true, label: 'Intervention' },
          { name: 'reason', required: true, type: 'text', label: 'Reason' },
          { name: 'operator_id', readonly: true, label: 'Operator' },
          { name: 'at', readonly: true, label: 'At' },
          { name: 'state_before', readonly: true, label: 'State Before' },
          { name: 'state_after', readonly: true, label: 'State After' }
        ] }
    ]
  },

  'M63-form-task': {
    kind: 'model_form',
    model: 'fix.workflow.task',
    title: 'Task Inbox Entry',
    back: 'M63-inbox',
    create: false, pick: 'An approval task is raised by the approval engine: open one from your Task Inbox.',
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

/* Page 5 captures workflow definitions of either trigger kind: the same AUT
 * register row, opened with its engine filled in so it shows on its list. */
SCREENS['M63-form-scheduled'] = { ...SCREENS['M63-form-automation'], title: 'Scheduled Workflow',
  back: 'M63-jobs', presets: { engine: 'odoo_cron' } };
SCREENS['M63-form-event'] = { ...SCREENS['M63-form-automation'], title: 'Event-Triggered Automation',
  back: 'M63-events', presets: { engine: 'event_consumer' } };
/* The third capture form on page 5 registers the row the scheduled_jobs
 * report will show: an odoo_cron binding (cron:<module>.<xmlid>). It used to
 * open M30's fix.scheduled.job form, which carries no engine reference at
 * all — nothing to verify. */
SCREENS['M63-form-job-registration'] = { ...SCREENS['M63-form-automation'],
  title: 'Scheduled Job Registration', back: 'M63-jobs', presets: { engine: 'odoo_cron' } };

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
  'M63:Business Rule': 'fix.business.rule',
  'M63:Substitution / OOO': 'fix.approval.substitution',
  'M63:Rule Simulation': 'fix.rule.simulation',
  'M63:Scheduled Workflow': 'fix.automation',
  'M63:Event-Triggered Automation': 'fix.automation',
  'M63:Automation Register Entry': 'fix.automation.register',
  'M63:Manual Intervention': 'fix.workflow.intervention',
  'M63:Authority Ladder': 'fix.dofa.ladder',
  'M63:Ladder Band': 'fix.dofa.threshold',
  'M63:Scheduled Job Registration': 'fix.automation'
};

export const FORM_CHIPS = {
  'M63:Workflow Definition': 'M63-form-automation',
  'M63:Approval Chain': 'M63-form-doa',
  'M63:Business Rule': 'M63-form-rule',
  'M63:Substitution / OOO': 'M63-form-substitution',
  'M63:Rule Simulation': 'M63-form-simulation',
  'M63:Scheduled Workflow': 'M63-form-scheduled',
  'M63:Event-Triggered Automation': 'M63-form-event',
  'M63:Automation Register Entry': 'M63-form-register',
  'M63:Manual Intervention': 'M63-form-intervention',
  /* the value ladder the DoA tier comes from is kept by M30: its own forms,
   * offered here. The scheduled-job registration is an AUT row with an
   * odoo_cron binding, captured in-workspace (see M63-form-job-registration). */
  'M63:Authority Ladder': 'M30-form-dofa-ladder',
  'M63:Ladder Band': 'M30-form-dofa-band',
  'M63:Scheduled Job Registration': 'M63-form-job-registration',
  'M63:__by_model__': {
    'fix.automation': 'M63-form-automation',
    'fix.approval.matrix': 'M63-form-doa',
    'fix.business.rule': 'M63-form-rule',
    'fix.workflow.instance': 'M63-form-instance',
    'fix.approval.substitution': 'M63-form-substitution',
    'fix.workflow.task': 'M63-form-task',
    'fix.rule.simulation': 'M63-form-simulation',
    'fix.automation.register': 'M63-form-register',
    'fix.workflow.intervention': 'M63-form-intervention'
  },
  'M63:__by_screen__': {
    'M63-definitions': 'M63-form-automation',
    /* M63-jobs is the scheduled_jobs report, not a list: its +New comes from
     * freg sub 5's create (M63-form-scheduled), never from the report screen. */
    'M63-events': 'M63-form-event',
    'M63-simulation': 'M63-form-simulation',
    'M63-register': 'M63-form-register',
    'M63-interventions': 'M63-form-intervention',
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
