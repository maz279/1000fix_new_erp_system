/** @odoo-module **/
/* A12 · M67 Projects & Portfolio Management. 3 groups / 12 screens / 7 reports / 4 forms / freg 54.
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
    { l: 'Portfolio Budget', m: 'portfolio_budget', prefix: '৳ ' }
  ],
  groups: [
    { en: 'Registry Completion', screens: [
      { id: 'M67-templates', en: 'Templates (6 types)', bn: 'Templates (6 types)', t: 'g' },
      { id: 'M67-evm', en: 'Earned Value', bn: 'Earned Value', t: 'r' },
      { id: 'M67-billing', en: 'Milestone Billing', bn: 'Milestone Billing', t: 'g' },
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
      { id: 'M67-resources', en: 'Resource Planning', bn: 'ওয়ার্কলোড', t: 'r' }
    ]},
    { en: 'Governance', screens: [
      { id: 'M67-gates', en: 'Stage Gates', bn: 'স্টেজ-গেট', t: 'g' },
      { id: 'M67-compliance', en: 'Gate Compliance', bn: 'সম্মতি', t: 'r' }
    ]}
  ],
  reports: ['Portfolio Status', 'Milestone Tracker', 'Task Workload by Assignee', 'Stage-Gate Compliance', 'Budget vs Actual', 'Billing Status'],
  forms: ['Project (6 types)', 'Milestone', 'Task', 'Stage Gate Review'],
  cross: ['M49 capex budgets', 'M54 costing', 'M21 project staffing', 'M60 enterprise register (project.risk_escalated)'],
  freg: { src: 54, sub: [
    ['1', 'Portfolio', 10, { model: 'fix.project', cols: ['name', 'code', 'project_type', 'manager_id', 'state'], screens: ['M67-projects', 'M67-portfolio', 'M67-budget'], reports: ['Portfolio Status', 'Budget vs Actual'], forms: ['Project (6 types)'] }],
    ['2', 'Project Setup', 9, { model: 'fix.project.template', cols: ['name', 'project_type', 'default_duration_days', 'default_budget', 'active'], screens: ['M67-templates', 'M67-projects'], reports: [], forms: ['Project (6 types)'] }],
    ['3', 'Delivery', 11, { model: 'fix.project.task', cols: ['name', 'project_id', 'milestone_id', 'assigned_to', 'state'], screens: ['M67-wbs', 'M67-milestones', 'M67-tracker', 'M67-resources'], reports: ['Milestone Tracker', 'Task Workload by Assignee'], forms: ['Task', 'Milestone'] }],
    ['4', 'Governance', 8, { model: 'fix.project.gate', cols: ['name', 'project_id', 'gate', 'decision', 'state'], screens: ['M67-gates', 'M67-compliance'], reports: ['Stage-Gate Compliance'], forms: ['Stage Gate Review'] }],
    ['5', 'Financials', 9, { model: 'fix.project.billing', cols: ['name', 'project_id', 'billing_type', 'amount', 'invoice_id', 'state'], screens: ['M67-billing', 'M67-billstatus', 'M67-evm', 'M67-profit'], reports: ['Billing Status', 'Budget vs Actual'], forms: [] }],
    ['6', 'Audit', 7, { model: 'fix.project.risk', cols: ['name', 'project_id', 'kind', 'title', 'severity_score', 'escalated', 'state'], screens: ['M67-risks'], reports: [], forms: [] }]
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
  'M67:Stage Gate Review': 'fix.project.gate'
};

export const FORM_CHIPS = {
  'M67:Project (6 types)': 'M67-form-project',
  'M67:Milestone': 'M67-form-milestone',
  'M67:Task': 'M67-form-task',
  'M67:Stage Gate Review': 'M67-form-gate',
  'M67:__by_model__': {
    'fix.project.template': 'M67-form-template',
    'fix.project.billing': 'M67-form-billing',
    'fix.project.risk': 'M67-form-risk',
    'fix.project': 'M67-form-project',
    'fix.project.milestone': 'M67-form-milestone',
    'fix.project.task': 'M67-form-task',
    'fix.project.gate': 'M67-form-gate'
  },
  'M67:__by_screen__': {
    'M67-templates': 'M67-form-template',
    'M67-billing': 'M67-form-billing',
    'M67-risks': 'M67-form-risk',
    'M67-projects': 'M67-form-project',
    'M67-milestones': 'M67-form-milestone',
    'M67-wbs': 'M67-form-task',
    'M67-gates': 'M67-form-gate'
  }
};

export const CREATE = {
  M67: { screen: 'M67-form-project', model: 'fix.project', label: 'Project' }
};
