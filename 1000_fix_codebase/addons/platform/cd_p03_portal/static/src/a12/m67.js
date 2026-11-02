/** @odoo-module **/
/* A12 · M67 Projects & Portfolio Management. 3 groups / 11 screens / 5 reports / 4 forms / freg 54. */

export const MODULE = {
  area: 'A12', code: 'M67', en: 'Projects & Portfolio Management', title: 'M67 · Projects & Portfolio Management',
  bn: 'প্রজেক্ট ও পোর্টফোলিও', icon: '📈',
  desc: 'Project register (internal, client, infrastructure), portfolio status with budget vs actual, milestones and tasks with workload, and stage-gate reviews with recorded decisions.',
  kpis: [
    { l: 'Projects Active', m: 'projects_active' },
    { l: 'Projects Total', m: 'projects_total' },
    { l: 'Milestones Due 30d', m: 'milestones_due_30d' },
    { l: 'Tasks Open', m: 'tasks_open' },
    { l: 'Portfolio Budget', m: 'portfolio_budget', prefix: '৳ ' }
  ],
  groups: [
    { en: 'Registry Completion', screens: [
      { id: 'M67-record', en: 'Project Record', bn: 'প্রজেক্ট রেকর্ড', t: 'g' },
      { id: 'M67-templates', en: 'Templates (6 types)', bn: 'Templates (6 types)', t: 'g' },
      { id: 'M67-evm', en: 'Earned Value', bn: 'Earned Value', t: 'g' },
      { id: 'M67-billing', en: 'Milestone Billing', bn: 'Milestone Billing', t: 'g' },
      { id: 'M67-profit', en: 'Project P&L', bn: 'Project P&L', t: 'g' },
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
  reports: ['Portfolio Status', 'Milestone Tracker', 'Task Workload by Assignee', 'Stage-Gate Compliance', 'Budget vs Actual'],
  forms: ['Project (6 types)', 'Milestone', 'Task', 'Stage Gate Review'],
  cross: ['M49 capex budgets', 'M54 costing', 'M21 project staffing'],
  freg: { src: 54, sub: [
    ['1', 'Portfolio', 10], ['2', 'Project Setup', 9], ['3', 'Delivery', 11],
    ['4', 'Governance', 8], ['5', 'Financials', 9], ['6', 'Audit', 7]
  ] }
};

export const SCREENS = {
  'M67-rpt-resutil': { kind: 'table_report', module: 'M67', report: 'resource_utilisation',
    title: 'Resource Utilisation', period: false },
  'M67-rpt-benefits': { kind: 'table_report', module: 'M67', report: 'benefits_realisation',
    title: 'Benefits Realisation', period: false },
  'M67-record': { kind: 'model_form', model: 'fix.project', title: 'Project Record',
    back: 'M67-projects',
    status: { field: 'state', labels: { draft: 'Draft', active: 'Active',
      on_hold: 'On Hold', completed: 'Completed', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Project Record', note: 'The full project record: type, manager, dates, budget and state. Budget variance is computed by the model.',
        fields: [
          { name: 'name', required: true, label: 'Project Name' },
          { name: 'project_type', required: true, label: 'Project Type' },
          { name: 'manager_id', label: 'Project Manager' },
          { name: 'date_start', label: 'Start' },
          { name: 'date_end', label: 'End' },
          { name: 'budget', label: 'Budget' },
          { name: 'state', required: true, label: 'State' }
        ] }
    ] },

  'M67-projects': { kind: 'model_list', model: 'fix.project', stateField: 'state',
    cols: ['name', 'code', 'project_type', 'manager_id', 'date_start', 'date_end', 'budget', 'state'] },
  'M67-portfolio': { kind: 'table_report', module: 'M67', report: 'portfolio_status', title: 'Portfolio Status', period: false },
  'M67-budget': { kind: 'table_report', module: 'M67', report: 'budget_vs_actual', title: 'Budget vs Actual', period: false },
  'M67-milestones': { kind: 'model_list', model: 'fix.project.milestone', stateField: 'state',
    cols: ['name', 'project_id', 'due_date', 'state'] },
  'M67-tracker': { kind: 'table_report', module: 'M67', report: 'milestone_tracker', title: 'Milestone Tracker', period: false },
  'M67-wbs': { kind: 'model_list', model: 'fix.project.task', stateField: 'state',
    cols: ['name', 'project_id', 'milestone_id', 'assigned_to', 'planned_hours', 'actual_hours', 'state'] },
  'M67-resources': { kind: 'table_report', module: 'M67', report: 'task_workload', title: 'Task Workload by Assignee', period: false },
  'M67-gates': { kind: 'model_list', model: 'fix.project.gate', stateField: 'state',
    cols: ['name', 'project_id', 'gate', 'review_on', 'decision', 'checklist_passed', 'state'],
    actions: [{ m: 'action_hold', l: 'Hold Review' }, { m: 'action_close', l: 'Close' }] },
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
      { title: 'Project', note: 'The project code is generated on creation. Budget variance is computed as budget minus actual.',
        fields: [
          { name: 'name', required: true, label: 'Project Name' },
          { name: 'project_type', required: true, label: 'Project Type' },
          { name: 'manager_id', label: 'Project Manager' },
          { name: 'date_start', label: 'Start' },
          { name: 'date_end', label: 'End' },
          { name: 'budget', label: 'Budget' },
          { name: 'state', required: true, label: 'State' }
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
      { title: 'Milestone', note: 'A milestone cannot complete while open tasks remain (model gate on action_complete).',
        fields: [
          { name: 'name', required: true, label: 'Milestone Name' },
          { name: 'project_id', required: true, label: 'Project' },
          { name: 'due_date', label: 'Due Date' },
          { name: 'state', required: true, label: 'State' }
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
      { title: 'Task', note: 'Planned vs actual hours drive the workload report; the milestone is optional grouping.',
        fields: [
          { name: 'name', required: true, label: 'Task Name' },
          { name: 'project_id', required: true, label: 'Project' },
          { name: 'milestone_id', label: 'Milestone' },
          { name: 'assigned_to', label: 'Assigned To' },
          { name: 'planned_hours', label: 'Planned Hours' },
          { name: 'actual_hours', label: 'Actual Hours' },
          { name: 'state', required: true, label: 'State' }
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
      { title: 'Gate Review', note: 'Holding a review requires the decision to be recorded first; the checklist flag is the pre-review result.',
        fields: [
          { name: 'project_id', required: true, label: 'Project' },
          { name: 'gate', required: true, label: 'Gate' },
          { name: 'review_on', required: true, label: 'Review On' },
          { name: 'reviewer_id', label: 'Reviewer' },
          { name: 'checklist_passed', label: 'Checklist Passed' },
          { name: 'decision', label: 'Decision' },
          { name: 'state', required: true, label: 'State' }
        ] },
      { title: 'Findings', fields: [
          { name: 'findings', type: 'text', label: 'Findings' }
        ] }
    ]
  },

  /* registry completion screens */
  'M67-templates': { kind: 'model_list', model: 'fix.project.template', cols: ['name', 'project_type', 'default_duration_days', 'default_budget', 'active'], actions: [{ m: 'action_instantiate', l: 'Create Project' }] },
  'M67-evm': { kind: 'table_report', module: 'M67', report: 'earned_value', title: 'Earned Value', period: false },
  'M67-billing': { kind: 'model_list', model: 'fix.project.billing', stateField: 'state', cols: ['name', 'project_id', 'milestone_id', 'billing_type', 'amount', 'due_on', 'invoice_ref', 'state'], actions: [{ m: 'action_mark_ready', l: 'Ready to Invoice' }, { m: 'action_mark_invoiced', l: 'Mark Invoiced' }] },
  'M67-profit': { kind: 'table_report', module: 'M67', report: 'project_pnl', title: 'Project P&L', period: false },
  'M67-risks': { kind: 'model_list', model: 'fix.project.risk', stateField: 'state', cols: ['name', 'project_id', 'kind', 'title', 'severity_score', 'owner_id', 'state'], actions: [{ m: 'action_mitigate', l: 'Mitigate' }, { m: 'action_close', l: 'Close' }] },


  /* ===== registry completion forms ===== */
  'M67-form-template': {
    kind: 'model_form',
    model: 'fix.project.template',
    title: "Project Template",
    back: 'M67-templates',
    sections: [
      { title: "Project Template", note: "A template carries the default duration, budget, gate plan and milestone plan. 'Create Project' instantiates a real project and its milestones.",
        fields: [
          { name: 'name', required: true, label: "Template Name" },
          { name: 'project_type', required: true, label: "Project Type" },
          { name: 'default_duration_days', label: "Default Duration (days)" },
          { name: 'default_budget', label: "Default Budget" },
          { name: 'gate_plan', label: "Gate Plan" },
          { name: 'active', label: "Active" }
        ] }
    ]
  },
  'M67-form-billing': {
    kind: 'model_form',
    model: 'fix.project.billing',
    title: "Milestone Billing",
    back: 'M67-billing',
    status: { field: 'state', labels: { planned: "Planned", ready: "Ready to Invoice", invoiced: "Invoiced", paid: "Paid" } },
    sections: [
      { title: "Milestone Billing", note: "Billing follows the milestone: planned -> ready -> invoiced (an invoice reference is required) -> paid. Retention is held until closure.",
        fields: [
          { name: 'project_id', required: true, label: "Project" },
          { name: 'milestone_id', label: "Milestone" },
          { name: 'customer_id', label: "Customer" },
          { name: 'billing_type', required: true, label: "Billing Type" },
          { name: 'amount', required: true, label: "Amount" },
          { name: 'due_on', required: true, label: "Due On" },
          { name: 'invoice_ref', label: "Invoice Reference" },
          { name: 'retention_pct', label: "Retention %" },
          { name: 'state', required: true, label: "State" }
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
      { title: "Risk / Issue", note: "Severity is computed as probability x impact (1-9) and the register sorts on it, so risk review starts with the worst exposure.",
        fields: [
          { name: 'project_id', required: true, label: "Project" },
          { name: 'kind', required: true, label: "Kind" },
          { name: 'title', required: true, label: "Title" },
          { name: 'probability', required: true, label: "Probability" },
          { name: 'impact', required: true, label: "Impact" },
          { name: 'owner_id', label: "Owner" },
          { name: 'opened_on', required: true, label: "Opened On" },
          { name: 'state', required: true, label: "State" }
        ] }
    ]
  },

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
  'M67:Budget vs Actual': 'M67-budget'
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
