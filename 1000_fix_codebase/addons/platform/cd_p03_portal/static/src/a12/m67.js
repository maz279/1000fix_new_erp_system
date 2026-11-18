/** @odoo-module **/
/* A12 · M67 Projects & Portfolio Management. 5 groups / 20 screens / 8 reports / 12 forms / freg 54.
 *
 * A12 workflow audit (2026-11-04) R4/X5: the forms posted `state` (and the
 * gate's `decision`) as ordinary inputs — the badge at the top of each form
 * is now the ONLY place state appears, and every lifecycle button is an
 * action with its server-side checks: project activation needs the DOFA
 * budget approval, a milestone completes only with customer acceptance
 * evidence, "Mark invoiced" creates the real customer invoice, and the gate
 * decision is prompted (pass / conditional / fail) and recorded by the
 * reviewer — never typed into a field.
 *
 * A12 finish (2026-11-07): every button whose method needs a value now asks for
 * it. Request Budget Approval carries its justification (F1), Mitigate its
 * mitigation (F4), Cancel its reason (F9). Finance invoices a ready line and
 * confirms the billing posted; a sponsor closes the project (F14, F18). Actual
 * cost is measured, so it is shown and never typed (F13). */

export const MODULE = {
  area: 'A12', code: 'M67', en: 'Projects & Portfolio Management', title: 'M67 · Projects & Portfolio Management',
  bn: 'প্রজেক্ট ও পোর্টফোলিও', icon: '📈',
  desc: 'Project register (internal, client, infrastructure) with DOFA-routed budget approval and baselines, portfolio status with budget vs actual, milestones with customer acceptance and overdue flagging, tasks, milestone billing that creates real invoices under the contract ceiling, and independent stage-gate reviews.',
  kpis: [
    { l: 'Projects Active', m: 'projects_active' },
    { l: 'Milestones Due 30d', m: 'milestones_due_30d' },
    { l: 'Milestones Overdue', m: 'milestones_overdue' },
    { l: 'Invoiced (real)', m: 'billings_invoiced' },
    { l: 'Portfolio Budget', m: 'portfolio_budget', prefix: '৳ ' },
    { l: 'Scope Changes Pending', m: 'changes_pending' },
    { l: 'Deliverables Awaiting Acceptance', m: 'deliverables_awaiting' }
  ],
  groups: [
    { en: 'Registry Completion', screens: [
      { id: 'M67-templates', en: 'Templates (6 types)', bn: 'Templates (6 types)', t: 'g' },
      { id: 'M67-evm', en: 'Earned Value', bn: 'Earned Value', t: 'r' },
      { id: 'M67-billing', en: 'Milestone Billing', bn: 'Milestone Billing', t: 'g' },
      { id: 'M67-budget-lines', en: 'Budget by Category', bn: 'খাতভিত্তিক বাজেট', t: 'g' },
      { id: 'M67-billstatus', en: 'Billing Status', bn: 'বিলিং স্ট্যাটাস', t: 'r' },
      { id: 'M67-profit', en: 'Project P&L', bn: 'Project P&L', t: 'r' },
      { id: 'M67-risks', en: 'Risk & Issue Registers', bn: 'Risk & Issue Registers', t: 'g' }
    ]},
    { en: 'Portfolio', screens: [
      { id: 'M67-projects', en: 'Projects', bn: 'প্রজেক্ট', t: 'g' },
      { id: 'M67-portfolio', en: 'Portfolio Board', bn: 'স্ট্যাটাস', t: 'r' },
      { id: 'M67-budget', en: 'Budget vs Actual', bn: 'বাজেট', t: 'r' }
    ]},
    { en: 'Delivery', screens: [
      { id: 'M67-milestones', en: 'Milestones', bn: 'মাইলস্টোন', t: 'g' },
      { id: 'M67-tracker', en: 'Milestone Tracker', bn: 'ট্র্যাকার', t: 'r' },
      { id: 'M67-wbs', en: 'WBS & Tasks', bn: 'টাস্ক', t: 'g' },
      { id: 'M67-deliverables', en: 'Deliverables', bn: 'ডেলিভারেবল', t: 'g' },
      { id: 'M67-resources', en: 'Resource Planning', bn: 'ওয়ার্কলোড', t: 'r' },
      { id: 'M67-rpt-resutil', en: 'Resource Utilisation', bn: 'রিসোর্স ব্যবহার', t: 'r' }
    ]},
    { en: 'Governance', screens: [
      { id: 'M67-gates', en: 'Stage Gates', bn: 'স্টেজ-গেট', t: 'g' },
      { id: 'M67-changes', en: 'Scope Changes', bn: 'স্কোপ পরিবর্তন', t: 'g' },
      { id: 'M67-compliance', en: 'Gate Compliance', bn: 'সম্মতি', t: 'r' }
    ]},
    { en: 'Closure', screens: [
      { id: 'M67-lessons', en: 'Lessons Learned', bn: 'শিক্ষণীয় বিষয়', t: 'g' },
      { id: 'M67-benefits', en: 'Benefit Realisation', bn: 'সুফল বাস্তবায়ন', t: 'g' },
      { id: 'M67-rpt-benefits', en: 'Benefits Realisation Report', bn: 'সুফল প্রতিবেদন', t: 'r' }
    ]}
  ],
  reports: ['Portfolio Status', 'Milestone Tracker', 'Task Workload by Assignee', 'Resource Utilisation', 'Stage-Gate Compliance', 'Budget vs Actual', 'Billing Status', 'Benefits Realisation'],
  forms: ['Project (6 types)', 'Project Template', 'Milestone', 'Task', 'Deliverable', 'Stage Gate Review', 'Scope Change', 'Milestone Billing', 'Budget Line', 'Risk / Issue', 'Lesson Learned', 'Benefit Measurement'],
  cross: ['M49 capex budgets', 'M54 costing', 'M21 project staffing', 'M60 enterprise register (project.risk_escalated)'],
  freg: { src: 54, sub: [
    ['1', 'Portfolio', 10, { model: 'fix.project', cols: ['name', 'code', 'project_type', 'manager_id', 'state'], screens: ['M67-projects', 'M67-portfolio', 'M67-budget'], reports: ['Portfolio Status', 'Budget vs Actual'], forms: ['Project (6 types)'] }],
    ['2', 'Project Setup', 9, { model: 'fix.project.template', cols: ['name', 'project_type', 'default_duration_days', 'default_budget', 'active'], screens: ['M67-templates', 'M67-projects'], reports: [], forms: ['Project Template', 'Project (6 types)'] }],
    ['3', 'Delivery', 11, { model: 'fix.project.task', cols: ['name', 'project_id', 'milestone_id', 'assigned_to', 'state'], screens: ['M67-wbs', 'M67-milestones', 'M67-deliverables', 'M67-tracker', 'M67-resources', 'M67-rpt-resutil'], reports: ['Milestone Tracker', 'Task Workload by Assignee', 'Resource Utilisation'], forms: ['Task', 'Milestone', 'Deliverable'] }],
    ['4', 'Governance', 8, { model: 'fix.project.gate', cols: ['name', 'project_id', 'gate', 'decision', 'state'], screens: ['M67-gates', 'M67-changes', 'M67-compliance'], reports: ['Stage-Gate Compliance'], forms: ['Stage Gate Review', 'Scope Change'] }],
    ['5', 'Financials', 9, { model: 'fix.project.billing', cols: ['name', 'project_id', 'billing_type', 'amount', 'invoice_id', 'state'], screens: ['M67-billing', 'M67-budget-lines', 'M67-billstatus', 'M67-evm', 'M67-profit'], reports: ['Billing Status', 'Budget vs Actual'], forms: ['Milestone Billing', 'Budget Line'] }],
    ['6', 'Risks, Issues & Closure', 7, { model: 'fix.project.risk', cols: ['name', 'project_id', 'kind', 'title', 'severity_score', 'escalated', 'state'], screens: ['M67-risks', 'M67-lessons', 'M67-benefits', 'M67-rpt-benefits'], reports: ['Benefits Realisation'], forms: ['Risk / Issue', 'Lesson Learned', 'Benefit Measurement'] }]
  ] }
};

export const SCREENS = {
  'M67-rpt-resutil': { kind: 'table_report', module: 'M67', report: 'resource_utilisation',
    title: 'Resource Utilisation', period: false },
  'M67-rpt-benefits': { kind: 'table_report', module: 'M67', report: 'benefits_realisation',
    title: 'Benefits Realisation', period: false },
  'M67-projects': { kind: 'model_list', model: 'fix.project', stateField: 'state',
    cols: ['name', 'code', 'project_type', 'manager_id', 'date_start', 'date_end', 'budget', 'baseline_budget', 'contract_value', 'billed_revenue', 'cost_basis', 'approval_state', 'billing_confirmed_by_id', 'state'],
    actions: [
      { m: 'action_request_approval', l: 'Request Budget Approval', states: ['draft', 'active', 'on_hold'], ask: 'Why this budget is needed (the approver reads this)', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Approval', states: ['draft', 'active', 'on_hold'] },
      { m: 'action_activate', l: 'Activate', states: ['draft'] },
      { m: 'action_hold', l: 'Hold', states: ['active'] },
      { m: 'action_resume', l: 'Resume', states: ['on_hold'] },
      { m: 'action_cancel', l: 'Cancel', states: ['draft', 'active', 'on_hold'] },
      { m: 'action_confirm_billing', l: 'Confirm Billing Posted (Finance)', states: ['active'] },
      { m: 'action_complete', l: 'Close Project (Sponsor)', states: ['active'] }
    ] },
  'M67-portfolio': { kind: 'table_report', module: 'M67', report: 'portfolio_status', title: 'Portfolio Status', period: false },
  'M67-budget': { kind: 'table_report', module: 'M67', report: 'budget_vs_actual', title: 'Budget vs Actual', period: false },
  'M67-milestones': { kind: 'model_list', model: 'fix.project.milestone', stateField: 'state',
    cols: ['name', 'project_id', 'due_date', 'overdue', 'accepted_by_id', 'accepted_on', 'acceptance_note', 'state'],
    actions: [
      { m: 'action_accept', l: 'Accept (Sponsor)', states: ['pending'], ask: 'Customer acceptance evidence (required)', kwarg: 'acceptance_note' },
      { m: 'action_complete', l: 'Complete', states: ['pending'] }
    ] },
  'M67-tracker': { kind: 'table_report', module: 'M67', report: 'milestone_tracker', title: 'Milestone Tracker', period: false },
  'M67-wbs': { kind: 'model_list', model: 'fix.project.task', stateField: 'state',
    cols: ['name', 'project_id', 'milestone_id', 'assigned_to', 'planned_hours', 'actual_hours', 'state'],
    actions: [
      { m: 'action_start', l: 'Start', states: ['todo'] },
      { m: 'action_log_hours', l: 'Log Hours', states: ['todo', 'in_progress'], asks: [{ label: 'Hours worked', kwarg: 'hours', number: true }] },
      { m: 'action_done', l: 'Done', states: ['todo', 'in_progress'] },
      { m: 'action_cancel', l: 'Cancel', states: ['todo', 'in_progress'] }
    ] },
  'M67-resources': { kind: 'table_report', module: 'M67', report: 'task_workload', title: 'Task Workload by Assignee', period: false },
  'M67-gates': { kind: 'model_list', model: 'fix.project.gate', stateField: 'state',
    cols: ['name', 'project_id', 'gate', 'review_on', 'reviewer_id', 'decision', 'checklist_passed', 'state'],
    actions: [
      { m: 'action_record_decision', l: 'Record Decision', states: ['scheduled'], asks: [
        { label: 'Decision — pass / conditional / fail', kwarg: 'decision' },
        { label: 'Checklist passed? yes / no', kwarg: 'checklist_passed' },
        { label: 'Findings (required for a fail)', kwarg: 'findings' }
      ] },
      { m: 'action_hold', l: 'Hold Review', states: ['scheduled'] },
      { m: 'action_close', l: 'Close', states: ['held'] }
    ] },
  'M67-compliance': { kind: 'table_report', module: 'M67', report: 'gate_compliance', title: 'Stage-Gate Compliance', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M67-form-project': {
    kind: 'model_form',
    model: 'fix.project',
    title: 'Project',
    back: 'M67-projects',
    status: { field: 'state', labels: {
      draft: 'Draft', active: 'Active', on_hold: 'On Hold',
      completed: 'Completed', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Project', note: 'The project code is generated on creation (PRJ/year). Activation needs the DOFA budget approval, the contract value of a client project and gates G1 and G2 passed; the baseline, the contract value and the manager freeze at activation, and billing may not exceed the contract value (or the baseline where no contract is recorded).',
        fields: [
          { name: 'name', required: true, label: 'Project Name' },
          { name: 'project_type', required: true, label: 'Project Type' },
          { name: 'manager_id', label: 'Project Manager' },
          { name: 'date_start', label: 'Start' },
          { name: 'date_end', label: 'End' },
          { name: 'budget', label: 'Budget' },
          { name: 'contract_value', label: 'Contract Value' },
          { name: 'dofa_justification', type: 'text', label: 'Budget Justification', bn: 'বাজেটের যৌক্তিকতা' }
        ] },
      { title: 'Overrun on a running project', note: 'Enter the new figure here and use Request Budget Approval. It routes at the tier of the new amount; when granted it becomes the budget and the new baseline. The budget itself cannot be raised after activation.',
        fields: [
          { name: 'baseline_budget', label: 'Baselined Budget', bn: 'বেসলাইন বাজেট', readonly: true },
          { name: 'budget_requested', label: 'Requested Budget', bn: 'অনুরোধকৃত বাজেট' },
          { name: 'contract_value_requested', label: 'Requested Contract Value', bn: 'অনুরোধকৃত চুক্তি মূল্য' }
        ] },
      { title: 'Measured results', note: 'Computed, never typed. With no ledger postings tagged with the project code and no hourly rate configured, the cost basis says Not measured.',
        fields: [
          { name: 'actual_cost', label: 'Actual Cost', bn: 'প্রকৃত খরচ', readonly: true },
          { name: 'cost_basis', label: 'Cost Basis', bn: 'খরচের ভিত্তি', readonly: true },
          { name: 'billed_revenue', label: 'Billed Revenue', bn: 'বিল করা আয়', readonly: true }
        ] }
    ]
  },

  'M67-form-milestone': {
    kind: 'model_form',
    model: 'fix.project.milestone',
    title: 'Milestone',
    back: 'M67-milestones',
    status: { field: 'state', labels: { pending: 'Pending', done: 'Done' } },
    sections: [
      { title: 'Milestone', note: 'Completion needs open tasks closed AND the acceptance recorded with evidence by a sponsor who does not manage the project (list actions); the daily cron flags overdue pending milestones.',
        fields: [
          { name: 'name', required: true, label: 'Milestone Name' },
          { name: 'project_id', required: true, label: 'Project' },
          { name: 'due_date', label: 'Due Date' }
        ] }
    ]
  },

  'M67-form-task': {
    kind: 'model_form',
    model: 'fix.project.task',
    title: 'Task',
    back: 'M67-wbs',
    status: { field: 'state', labels: {
      todo: 'To Do', in_progress: 'In Progress', done: 'Done', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Task', note: 'Planned vs actual hours drive the workload report and the measured cost; the milestone is optional grouping and must belong to the same project. State moves through the list actions, and the assignee can work his own task and log hours there.',
        fields: [
          { name: 'name', required: true, label: 'Task Name' },
          { name: 'project_id', required: true, label: 'Project' },
          { name: 'milestone_id', label: 'Milestone' },
          { name: 'assigned_to', label: 'Assigned To' },
          { name: 'planned_hours', label: 'Planned Hours' },
          { name: 'actual_hours', label: 'Actual Hours' }
        ] }
    ]
  },

  'M67-form-gate': {
    kind: 'model_form',
    model: 'fix.project.gate',
    title: 'Stage Gate Review',
    back: 'M67-gates',
    status: { field: 'state', labels: {
      scheduled: 'Scheduled', held: 'Held', closed: 'Closed' } },
    sections: [
      { title: 'Gate Review', note: 'The project manager or a sponsor schedules the review; the reviewer is independent of the project manager (constraint). The DECISION, checklist and findings are the reviewer\'s, recorded through the list action. The latest decision per gate counts: a failed gate blocks activation and completion until a re-review passes it. G1 and G2 must be closed with a pass before activation.',
        fields: [
          { name: 'project_id', required: true, label: 'Project' },
          { name: 'gate', required: true, label: 'Gate' },
          { name: 'review_on', required: true, label: 'Review On' },
          { name: 'reviewer_id', label: 'Reviewer' },
          { name: 'checklist_passed', label: 'Checklist Passed' }
        ] },
      { title: 'Findings', fields: [
          { name: 'findings', type: 'text', label: 'Findings' }
        ] }
    ]
  },

  /* registry completion screens */
  'M67-templates': { kind: 'model_list', model: 'fix.project.template', cols: ['name', 'project_type', 'default_duration_days', 'default_budget', 'active'], actions: [{ m: 'action_instantiate', l: 'Create Project' }] },
  'M67-evm': { kind: 'table_report', module: 'M67', report: 'earned_value', title: 'Earned Value', period: false },
  'M67-billing': { kind: 'model_list', model: 'fix.project.billing', stateField: 'state', cols: ['name', 'project_id', 'milestone_id', 'customer_id', 'billing_type', 'amount', 'retention_pct', 'net_amount', 'due_on', 'invoice_id', 'invoice_ref', 'state'], actions: [
    { m: 'action_mark_ready', l: 'Ready to Invoice', states: ['planned'] },
    { m: 'action_mark_invoiced', l: 'Invoice & Post (Finance)', states: ['ready'] },
    { m: 'action_cancel', l: 'Cancel Line', states: ['planned', 'ready'], ask: 'Why is this billing line cancelled? (required)', kwarg: 'reason' }
  ] },
  'M67-billstatus': { kind: 'table_report', module: 'M67', report: 'billing_status', title: 'Billing Status', period: false },
  'M67-profit': { kind: 'table_report', module: 'M67', report: 'project_pnl', title: 'Project P&L', period: false },
  'M67-risks': { kind: 'model_list', model: 'fix.project.risk', stateField: 'state', cols: ['name', 'project_id', 'kind', 'title', 'severity_score', 'escalated', 'owner_id', 'state'], actions: [
    { m: 'action_mitigate', l: 'Mitigate', states: ['open'], ask: 'Mitigation taken (required)', kwarg: 'mitigation' },
    { m: 'action_close', l: 'Close', states: ['open', 'mitigating'] },
    { m: 'action_reopen', l: 'Reopen', states: ['closed'] }
  ] },


  /* ===== registry completion forms ===== */
  'M67-form-template': {
    kind: 'model_form',
    model: 'fix.project.template',
    title: "Project Template",
    back: 'M67-templates',
    sections: [
      { title: "Project Template", note: "A template carries the default duration, budget, gate plan, milestone plan and WBS. 'Create Project' instantiates a real project, its milestones, tasks and gates, and stamps the template version used.",
        fields: [
          { name: 'name', required: true, label: "Template Name" },
          { name: 'project_type', required: true, label: "Project Type" },
          { name: 'default_duration_days', label: "Default Duration (days)" },
          { name: 'default_budget', label: "Default Budget" },
          { name: 'gate_plan', label: "Gate Plan" },
          { name: 'milestone_plan', type: 'text', label: "Milestone Plan" },
          { name: 'wbs_plan', type: 'text', label: "WBS Plan" },
          { name: 'active', label: "Active" }
        ] }
    ]
  },
  'M67-form-billing': {
    kind: 'model_form',
    model: 'fix.project.billing',
    title: "Milestone Billing",
    back: 'M67-billing',
    status: { field: 'state', labels: { planned: "Planned", ready: "Ready to Invoice", invoiced: "Invoiced", paid: "Paid", cancelled: "Cancelled" } },
    sections: [
      { title: "Milestone Billing", note: "Planned → ready (the project manager; a milestone line needs the milestone accepted and done) → invoiced (Finance posts the real customer invoice) → paid (follows the invoice's payment state). The terms freeze at ready. Retention is deducted on the invoice, and billing net of retention may not exceed the project's contract value, or its baseline where no contract is recorded.",
        fields: [
          { name: 'project_id', required: true, label: "Project" },
          { name: 'milestone_id', label: "Milestone" },
          { name: 'customer_id', label: "Customer" },
          { name: 'billing_type', required: true, label: "Billing Type" },
          { name: 'amount', required: true, label: "Amount" },
          { name: 'due_on', required: true, label: "Due On" },
          { name: 'retention_pct', label: "Retention %" }
        ] }
    ]
  },
  'M67-form-risk': {
    kind: 'model_form',
    model: 'fix.project.risk',
    title: "Risk / Issue",
    back: 'M67-risks',
    status: { field: 'state', labels: { open: "Open", mitigating: "Mitigating", closed: "Closed" } },
    sections: [
      { title: "Risk / Issue", note: "Severity is computed as probability x impact (1-9). At or above the escalation threshold (default 9) the risk reaches the enterprise register. Mitigate and Close need the mitigation written; the owner, a project manager or a sponsor works the risk, and at or above severity 9 only a sponsor who does not manage the project closes it.",
        fields: [
          { name: 'project_id', required: true, label: "Project" },
          { name: 'kind', required: true, label: "Kind" },
          { name: 'title', required: true, label: "Title" },
          { name: 'description', type: 'text', label: "Description" },
          { name: 'probability', required: true, label: "Probability" },
          { name: 'impact', required: true, label: "Impact" },
          { name: 'owner_id', label: "Owner" },
          { name: 'mitigation', type: 'text', label: "Mitigation", bn: 'প্রশমন' },
          { name: 'opened_on', required: true, label: "Opened On" }
        ] }
    ]
  }

};

/* ===== M67 capture audit (2026-11-18): the records the spec makes M67 own that no
 * page could capture: deliverables (FR-PPM-004), scope changes (FR-PPM-013,
 * BRU-PPM-06), the budget by category (FR-PPM-024), lessons learned and benefit
 * realisation (FR-PPM-032, BRU-PPM-14/15). States, decisions and stamps move only
 * through the list actions. */
Object.assign(SCREENS, {
  'M67-deliverables': { kind: 'model_list', model: 'fix.project.deliverable', stateField: 'state',
    cols: ['name', 'title', 'project_id', 'milestone_id', 'reviewer_id', 'submitted_by_id', 'decided_by_id', 'rejection_reason', 'state'],
    actions: [
      { m: 'action_submit', l: 'Submit for Acceptance', states: ['draft', 'rework'] },
      { m: 'action_accept', l: 'Accept (Reviewer)', states: ['submitted'] },
      { m: 'action_send_back', l: 'Send Back', states: ['submitted'], ask: 'What must be reworked (required)', kwarg: 'reason' }
    ] },
  'M67-form-deliverable': {
    kind: 'model_form', model: 'fix.project.deliverable', title: 'Deliverable', back: 'M67-deliverables',
    status: { field: 'state', labels: { draft: 'Draft', submitted: 'Submitted', accepted: 'Accepted', rework: 'Sent Back' } },
    sections: [
      { title: 'Deliverable', note: 'Register what the project hands over and how it is accepted. Submission needs the evidence attached and a reviewer who is not the submitter; the reviewer (or a sponsor) accepts it or sends it back with the reason. A milestone with deliverables completes only when all of them are accepted.',
        fields: [
          { name: 'title', required: true, label: 'Deliverable', bn: 'ডেলিভারেবল' },
          { name: 'project_id', required: true, label: 'Project' },
          { name: 'milestone_id', label: 'Milestone' },
          { name: 'acceptance_criteria', type: 'text', required: true, label: 'Acceptance Criteria', bn: 'গ্রহণযোগ্যতার মানদণ্ড' },
          { name: 'evidence_requirement', label: 'Evidence Required' },
          { name: 'reviewer_id', label: 'Reviewer' },
          { name: 'evidence_file', label: 'Evidence', type: 'file' }
        ] },
      { title: 'Review', fields: [
          { name: 'submitted_by_id', label: 'Submitted By', readonly: true },
          { name: 'decided_by_id', label: 'Decided By', readonly: true },
          { name: 'rejection_reason', type: 'text', label: 'Sent Back Because', readonly: true }
        ] }
    ]
  },
  'M67-changes': { kind: 'model_list', model: 'fix.project.change', stateField: 'state',
    cols: ['name', 'project_id', 'title', 'cost_impact', 'schedule_impact_days', 'requested_by_id', 'decided_by_id', 'decision_note', 'state'],
    actions: [
      { m: 'action_submit', l: 'Submit for Decision', states: ['draft'] },
      { m: 'action_approve', l: 'Approve (Sponsor)', states: ['submitted'] },
      { m: 'action_reject', l: 'Reject (Sponsor)', states: ['submitted'], ask: 'Why is the change rejected? (required)', kwarg: 'note' },
      { m: 'action_withdraw', l: 'Withdraw', states: ['draft', 'submitted'] }
    ] },
  'M67-form-change': {
    kind: 'model_form', model: 'fix.project.change', title: 'Scope Change', back: 'M67-changes',
    status: { field: 'state', labels: { draft: 'Draft', submitted: 'Submitted', approved: 'Approved', rejected: 'Rejected', withdrawn: 'Withdrawn' } },
    sections: [
      { title: 'Scope Change', note: 'Price the change before work proceeds on it (BRU-PPM-06). A sponsor who does not deliver the project decides it. On approval the schedule impact moves the planned end, and on a running project a cost increase becomes the Requested Budget, which re-baselines the project only through its DOFA budget approval. A submitted change cannot be rewritten.',
        fields: [
          { name: 'project_id', required: true, label: 'Project' },
          { name: 'title', required: true, label: 'Change', bn: 'পরিবর্তন' },
          { name: 'description', type: 'text', required: true, label: 'Scope Change' },
          { name: 'justification', type: 'text', required: true, label: 'Justification', bn: 'যৌক্তিকতা' },
          { name: 'cost_impact', label: 'Cost Impact' },
          { name: 'schedule_impact_days', label: 'Schedule Impact (days)' },
          { name: 'resource_impact', type: 'text', label: 'Resource Impact' }
        ] },
      { title: 'Decision', fields: [
          { name: 'requested_by_id', label: 'Requested By', readonly: true },
          { name: 'decided_by_id', label: 'Decided By', readonly: true },
          { name: 'decision_note', type: 'text', label: 'Decision Note', readonly: true }
        ] }
    ]
  },
  'M67-budget-lines': { kind: 'model_list', model: 'fix.project.budget.line',
    cols: ['project_id', 'category', 'amount', 'note'] },
  'M67-form-budget-line': {
    kind: 'model_form', model: 'fix.project.budget.line', title: 'Budget Line', back: 'M67-budget-lines',
    sections: [
      { title: 'Budget by Category', note: 'Split the project budget by cost category (FR-PPM-024): labour, parts, subcontract, travel, equipment, overhead. The lines never add up to more than the budget, and they freeze when the project is activated and its budget baselined.',
        fields: [
          { name: 'project_id', required: true, label: 'Project' },
          { name: 'category', required: true, label: 'Cost Category', bn: 'খরচের খাত' },
          { name: 'amount', required: true, label: 'Amount' },
          { name: 'note', label: 'Note' }
        ] }
    ]
  },
  'M67-lessons': { kind: 'model_list', model: 'fix.project.lesson', stateField: 'state',
    cols: ['name', 'project_id', 'category', 'observation', 'recommendation', 'recorded_by_id', 'shared_on', 'state'],
    actions: [{ m: 'action_share', l: 'Pass to Quality (M23)', states: ['draft'] }] },
  'M67-form-lesson': {
    kind: 'model_form', model: 'fix.project.lesson', title: 'Lesson Learned', back: 'M67-lessons',
    status: { field: 'state', labels: { draft: 'Recorded', shared: 'Passed to Quality (M23)' } },
    sections: [
      { title: 'Lesson Learned', note: 'A project closes only with at least one lesson recorded and passed to Quality (M23) (BRU-PPM-14). Once passed it is not edited: record a new lesson instead.',
        fields: [
          { name: 'project_id', required: true, label: 'Project' },
          { name: 'category', required: true, label: 'Category' },
          { name: 'observation', type: 'text', required: true, label: 'What Happened', bn: 'কী ঘটেছিল' },
          { name: 'recommendation', type: 'text', required: true, label: 'What To Do Next Time', bn: 'পরবর্তীতে করণীয়' }
        ] }
    ]
  },
  'M67-benefits': { kind: 'model_list', model: 'fix.project.benefit', stateField: 'state',
    cols: ['name', 'project_id', 'business_case_target', 'unit', 'measured_value', 'realised_pct', 'measured_on', 'measured_by_id', 'state'],
    actions: [
      { m: 'action_record_measurement', l: 'Record Measurement (Sponsor)', states: ['planned'], asks: [
        { label: 'Measured value', kwarg: 'measured_value', number: true },
        { label: 'Evidence of the measurement: report, data source, period (required)', kwarg: 'evidence' }
      ] }
    ] },
  'M67-form-benefit': {
    kind: 'model_form', model: 'fix.project.benefit', title: 'Benefit Measurement', back: 'M67-benefits',
    status: { field: 'state', labels: { planned: 'Planned', measured: 'Measured' } },
    sections: [
      { title: 'Benefit', note: 'For an internal initiative: the benefit its business case promised and how it is measured. A sponsor who does not deliver the initiative records the measurement from the list; the initiative closes only with a benefit measured (BRU-PPM-15). The target is fixed once measured.',
        fields: [
          { name: 'name', required: true, label: 'Benefit', bn: 'সুফল' },
          { name: 'project_id', required: true, label: 'Internal Initiative' },
          { name: 'business_case_target', required: true, label: 'Business Case Target' },
          { name: 'unit', required: true, label: 'Unit (e.g. BDT per year)' },
          { name: 'measurement_method', type: 'text', required: true, label: 'Measurement Method' },
          { name: 'owner_id', label: 'Benefit Owner' }
        ] },
      { title: 'Measurement', fields: [
          { name: 'measured_value', label: 'Measured Value', readonly: true },
          { name: 'realised_pct', label: 'Realised %', readonly: true },
          { name: 'measured_by_id', label: 'Measured By', readonly: true },
          { name: 'measurement_evidence', type: 'text', label: 'Evidence', readonly: true }
        ] }
    ]
  }
});

export const REPORT_ROUTES = {
  'M67:Portfolio Health': 'M67-portfolio',
  'M67:Earned Value Analysis': 'M67-evm',
  'M67:Milestone Billing Register': 'M67-billing',
  'M67:Resource Utilisation': 'M67-rpt-resutil',
  'M67:Benefits Realisation': 'M67-rpt-benefits',
  'M67:Portfolio Status': 'M67-portfolio',
  'M67:Milestone Tracker': 'M67-tracker',
  'M67:Task Workload by Assignee': 'M67-resources',
  'M67:Stage-Gate Compliance': 'M67-compliance',
  'M67:Budget vs Actual': 'M67-budget',
  'M67:Billing Status': 'M67-billstatus'
};

export const FORM_MODELS = {
  'M67:Project (6 types)': 'fix.project',
  'M67:Milestone': 'fix.project.milestone',
  'M67:Task': 'fix.project.task',
  'M67:Stage Gate Review': 'fix.project.gate',
  'M67:Project Template': 'fix.project.template',
  'M67:Deliverable': 'fix.project.deliverable',
  'M67:Scope Change': 'fix.project.change',
  'M67:Milestone Billing': 'fix.project.billing',
  'M67:Budget Line': 'fix.project.budget.line',
  'M67:Risk / Issue': 'fix.project.risk',
  'M67:Lesson Learned': 'fix.project.lesson',
  'M67:Benefit Measurement': 'fix.project.benefit'
};

export const FORM_CHIPS = {
  'M67:Project (6 types)': 'M67-form-project',
  'M67:Milestone': 'M67-form-milestone',
  'M67:Task': 'M67-form-task',
  'M67:Stage Gate Review': 'M67-form-gate',
  'M67:Project Template': 'M67-form-template',
  'M67:Deliverable': 'M67-form-deliverable',
  'M67:Scope Change': 'M67-form-change',
  'M67:Milestone Billing': 'M67-form-billing',
  'M67:Budget Line': 'M67-form-budget-line',
  'M67:Risk / Issue': 'M67-form-risk',
  'M67:Lesson Learned': 'M67-form-lesson',
  'M67:Benefit Measurement': 'M67-form-benefit',
  'M67:__by_model__': {
    'fix.project.template': 'M67-form-template',
    'fix.project.billing': 'M67-form-billing',
    'fix.project.risk': 'M67-form-risk',
    'fix.project': 'M67-form-project',
    'fix.project.milestone': 'M67-form-milestone',
    'fix.project.task': 'M67-form-task',
    'fix.project.gate': 'M67-form-gate',
    'fix.project.deliverable': 'M67-form-deliverable',
    'fix.project.change': 'M67-form-change',
    'fix.project.budget.line': 'M67-form-budget-line',
    'fix.project.lesson': 'M67-form-lesson',
    'fix.project.benefit': 'M67-form-benefit'
  },
  'M67:__by_screen__': {
    'M67-templates': 'M67-form-template',
    'M67-billing': 'M67-form-billing',
    'M67-risks': 'M67-form-risk',
    'M67-projects': 'M67-form-project',
    'M67-milestones': 'M67-form-milestone',
    'M67-wbs': 'M67-form-task',
    'M67-gates': 'M67-form-gate',
    'M67-deliverables': 'M67-form-deliverable',
    'M67-changes': 'M67-form-change',
    'M67-budget-lines': 'M67-form-budget-line',
    'M67-lessons': 'M67-form-lesson',
    'M67-benefits': 'M67-form-benefit'
  }
};

export const CREATE = {
  M67: { screen: 'M67-form-project', model: 'fix.project', label: 'Project' }
};
