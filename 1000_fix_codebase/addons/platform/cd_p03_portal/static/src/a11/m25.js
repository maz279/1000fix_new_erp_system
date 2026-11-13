/** @odoo-module **/
/* A11 · Insights & Intelligence — M25 Business Intelligence (v2 re-audit).
 * Registry-faithful: 4 groups / 13 screens / 6 reports / 3 forms / freg 58.
 * Every dashboard renders inside the shell from /p03/bi/* live reads; every
 * report chip opens its own computed pack (controllers/a11/m25.py).
 *
 * Capture audit 2026-11-13: every sub-module page offers the record IT
 * captures. Standard Report Library and Lifecycle & Usage offered
 * "+ New Dashboard"; Embedded Analytics offered nothing (its sync list had no
 * form); the dashboard lifecycle (review, certification through M63,
 * retirement) was served but on no screen, and the dashboard form had no
 * Data Steward, so review was always refused. The spreadsheet-retirement
 * register (FR-BID-034, model fix.bi.manual.pack) is new. */

/* The packs a Distribution Schedule may send (each is M25:<key> in the
 * controller's REPORTS; the server validates the key again at save). */
const SCHEDULE_REPORTS = [
  ['M25:executive_pack', 'Executive Pack'],
  ['M25:branch_league', 'Branch League'],
  ['M25:service_kpi_pack', 'Service KPI Pack'],
  ['M25:finance_pack', 'Finance Pack'],
  ['M25:people_pack', 'People Pack'],
  ['M25:weekly_exec_review', 'Weekly Executive Review'],
  ['M25:commercial_board', 'CCO Commercial Board']
];

/* The metric bank an alert may watch (controllers/a11/m25.py _metrics). */
const ALERT_METRICS = [
  ['open_orders', 'Open service orders'],
  ['in_repair', 'Orders in repair'],
  ['delivered_mtd', 'Delivered this month'],
  ['qc_failed', 'QC failed'],
  ['sla_overdue', 'SLA overdue'],
  ['estimates_awaiting', 'Estimates awaiting approval'],
  ['revenue_mtd', 'Approved quotes this month (BDT)'],
  ['invoiced_mtd', 'Invoices issued this month'],
  ['invoiced_taxable_mtd', 'Invoiced taxable value this month (BDT)'],
  ['collected_mtd', 'Collected this month (BDT)'],
  ['ar_outstanding', 'AR outstanding (BDT)'],
  ['overdue_gt_60d', 'AR overdue > 60 days (BDT)'],
  ['dunning_active', 'Active dunning cases'],
  ['leads_open', 'Open leads'],
  ['pipeline_value', 'Pipeline value (BDT)'],
  ['loyalty_members', 'Loyalty members'],
  ['complaints_open', 'Open complaints'],
  ['complaints_total', 'Complaints (total)'],
  ['ncr_open', 'Open non-conformances'],
  ['employees_active', 'Active employees'],
  ['present_today', 'Present today'],
  ['requisitions_open', 'Open requisitions']
];

export const MODULE = {
  area: 'A11', code: 'M25', en: 'Business Intelligence', title: 'M25 · Business Intelligence',
  bn: 'বিজনেস ইন্টেলিজেন্স', icon: '📊',
  desc: 'Role dashboards, standard report library, certified datasets, scheduled distribution, threshold alerts.',
  kpis: [
    { l: 'Dashboards Live', m: 'dashboards_live' },
    { l: 'Standard Reports', m: 'standard_reports' },
    { l: 'Weekly Manager Usage', m: 'weekly_manager_usage' },
    { l: 'Load Time p95 (ms)', m: 'load_time_p95', src: false },
    { l: 'Scheduled Distributions', m: 'scheduled_distributions' },
    { l: 'Spreadsheets Retired', m: 'spreadsheets_retired' }
  ],
  groups: [
    { en: 'Executive', screens: [
      { id: 'M25-ceo', en: 'CEO Cockpit', bn: 'সিইও ককপিট', t: 'd' },
      { id: 'M25-coo', en: 'COO / Ops Board (Live)', bn: 'সিওও অপস বোর্ড', t: 'd' },
      { id: 'M25-cfo', en: 'CFO Dashboard', bn: 'সিএফও ড্যাশবোর্ড', t: 'd' },
      { id: 'M25-ccO', en: 'CCO Commercial', bn: 'সিসিও কমার্শিয়াল', t: 'd' },
      { id: 'M25-weekly', en: 'Weekly Executive Review', bn: 'সাপ্তাহিক নির্বাহী রিভিউ', t: 'r' }
    ]},
    { en: 'Functional', screens: [
      { id: 'M25-library', en: 'Standard Report Library', bn: 'স্ট্যান্ডার্ড রিপোর্ট লাইব্রেরি', t: 'r' },
      { id: 'M25-service', en: 'Service Analytics', bn: 'সার্ভিস অ্যানালিটিক্স', t: 'd' },
      { id: 'M25-branch', en: 'Branch League Table', bn: 'শাখা লীগ', t: 'r' },
      { id: 'M25-finance', en: 'Finance Analytics', bn: 'ফিন্যান্স অ্যানালিটিক্স', t: 'd' },
      { id: 'M25-people', en: 'People Analytics', bn: 'পিপল অ্যানালিটিক্স', t: 'd' },
      { id: 'M25-quality', en: 'Quality Analytics', bn: 'কোয়ালিটি অ্যানালিটিক্স', t: 'd' }
    ]},
    { en: 'Self-Service', screens: [
      { id: 'M25-datasets', en: 'Certified Datasets', bn: 'সার্টিফাইড ডেটাসেট', t: 'r' },
      { id: 'M25-builder', en: 'Dashboard Builder', bn: 'ড্যাশবোর্ড বিল্ডার', t: 'g' },
      { id: 'M25-bi', en: 'BI Role Explorer', bn: 'বিআই রোল এক্সপ্লোরার', t: 'c' }
    ]},
    { en: 'Operations', screens: [
      { id: 'M25-schedules', en: 'Scheduled Distribution', bn: 'নির্ধারিত বিতরণ', t: 'g' },
      { id: 'M25-alerts', en: 'Threshold Alerts', bn: 'থ্রেশহোল্ড অ্যালার্ট', t: 'g' },
      { id: 'M25-sync', en: 'Sync Connections', bn: 'সিঙ্ক সংযোগ', t: 'g' },
      { id: 'M25-logs', en: 'Sync Logs', bn: 'সিঙ্ক লগ', t: 'g' },
      { id: 'M25-packs', en: 'Spreadsheet Retirement', bn: 'স্প্রেডশিট অবসর রেজিস্টার', t: 'g' }
    ]}
  ],
  reports: ['Executive Pack', 'Branch League', 'Service KPI Pack', 'Finance Pack', 'People Pack', 'Any dashboard → export', 'Standard Report Library'],
  forms: ['Dashboard', 'Distribution Schedule', 'Alert Subscription', 'Sync Connection', 'Manual Pack'],
  cross: ['All Modules'],
  freg: { src: 58, sub: [
    /* a role dashboard is a saved dashboard bound to one role cockpit */
    ['1', 'Role Dashboards', 12, { model: 'fix.bi.dashboard', cols: ['name', 'role', 'state', 'steward_id', 'owner_id', 'is_shared'], screens: ['M25-ceo', 'M25-coo', 'M25-cfo', 'M25-ccO'], reports: ['Executive Pack'], forms: ['Dashboard'] }],
    /* the library is the computed packs themselves - nothing is typed into
     * them; what a person captures here is the schedule that sends one */
    ['2', 'Standard Report Library', 10, { report: 'report_library', create: 'M25-form-schedule', screens: ['M25-library', 'M25-weekly', 'M25-branch', 'M25-service', 'M25-finance'], reports: ['Standard Report Library', 'Executive Pack', 'Branch League', 'Service KPI Pack', 'Finance Pack', 'People Pack'], forms: ['Distribution Schedule'] }],
    ['3', 'Self-Service', 8, { model: 'fix.bi.dashboard', cols: ['name', 'role', 'state', 'owner_id', 'steward_id', 'is_shared'], screens: ['M25-builder', 'M25-datasets', 'M25-bi'], reports: ['Any dashboard → export'], forms: ['Dashboard'] }],
    ['4', 'Distribution & Alerting', 9, { model: 'fix.bi.distribution.schedule', cols: ['name', 'report_key', 'cadence', 'format', 'last_status'], screens: ['M25-schedules', 'M25-alerts'], reports: [], forms: ['Distribution Schedule', 'Alert Subscription'] }],
    /* the analytics datasets the external BI workspace embeds from */
    ['5', 'Embedded Analytics', 7, { model: 'fix.bi.sync.config', cols: ['name', 'dataset_scope', 'target_workspace', 'sync_frequency', 'enabled', 'last_test_status'], screens: ['M25-sync', 'M25-logs', 'M25-datasets'], reports: [], forms: ['Sync Connection'] }],
    /* mobile renders the role dashboards; a low-bandwidth summary is a schedule (FR-BID-028) */
    ['6', 'Mobile', 5, { model: 'fix.bi.dashboard', cols: ['name', 'role', 'state', 'owner_id'], screens: ['M25-coo', 'M25-people', 'M25-quality'], reports: ['Service KPI Pack', 'People Pack'], forms: ['Dashboard', 'Distribution Schedule'] }],
    /* FR-BID-022 content lifecycle (on the Dashboard Builder) and FR-BID-034
     * the spreadsheet-retirement register, which this page captures */
    ['7', 'Lifecycle & Usage', 7, { model: 'fix.bi.manual.pack', cols: ['name', 'function_area', 'owner_id', 'frequency', 'effort_hours', 'state', 'reconciliation_result', 'retired_at'], screens: ['M25-packs', 'M25-builder'], reports: ['Any dashboard → export'], forms: ['Manual Pack', 'Dashboard'] }]
  ] }
};

export const SCREENS = {
  /* Registry role dashboards — one live payload per role. */
  'M25-ceo': { kind: 'bi_role', role: 'ceo', title: 'CEO Cockpit' },
  'M25-coo': { kind: 'bi_role', role: 'coo', title: 'COO / Ops Board (Live)' },
  'M25-cfo': { kind: 'bi_role', role: 'cfo', title: 'CFO Dashboard' },
  'M25-ccO': { kind: 'bi_role', role: 'cco', title: 'CCO Commercial' },
  'M25-service': { kind: 'bi_role', role: 'service', title: 'Service Analytics' },
  'M25-finance': { kind: 'bi_role', role: 'finance', title: 'Finance Analytics' },
  'M25-people': { kind: 'bi_role', role: 'people', title: 'People Analytics' },
  'M25-quality': { kind: 'bi_role', role: 'quality', title: 'Quality Analytics' },

  /* The six registry report packs — every chip opens its OWN computation. */
  'M25-rpt-exec': { kind: 'table_report', module: 'M25', report: 'executive_pack', title: 'Executive Pack', period: false },
  'M25-rpt-branch': { kind: 'table_report', module: 'M25', report: 'branch_league', title: 'Branch League', period: false },
  'M25-rpt-service': { kind: 'table_report', module: 'M25', report: 'service_kpi_pack', title: 'Service KPI Pack', period: false },
  'M25-rpt-finance': { kind: 'table_report', module: 'M25', report: 'finance_pack', title: 'Finance Pack', period: false },
  'M25-rpt-people': { kind: 'table_report', module: 'M25', report: 'people_pack', title: 'People Pack', period: false },
  'M25-rpt-export': { kind: 'table_report', module: 'M25', report: 'export_catalog', title: 'Any dashboard → export', period: false },
  'M25-branch': { kind: 'table_report', module: 'M25', report: 'branch_league', title: 'Branch League Table', period: false },
  'M25-weekly': { kind: 'table_report', module: 'M25', report: 'weekly_exec_review', title: 'Weekly Executive Business Review', period: false },
  'M25-library': { kind: 'table_report', module: 'M25', report: 'report_library', title: 'Standard Report Library', period: false },

  /* Self-service + operations. */
  'M25-datasets': { kind: 'table_report', module: 'M25', report: 'dataset_catalog', title: 'Certified Datasets', period: false },
  /* the content lifecycle (spec §8.1): review needs a named steward;
   * certification is decided in a certifier's inbox (M63), never by the
   * author; retirement is a steward act */
  'M25-builder': { kind: 'model_list', model: 'fix.bi.dashboard', stateField: 'state',
    cols: ['name', 'role', 'state', 'steward_id', 'is_shared', 'owner_id', 'certified_by', 'certified_at'],
    empty: 'No dashboard is saved yet. + New saves one as a draft for a role; name its Data Steward, submit it for review and request certification.',
    actions: [
      { m: 'action_submit_review', l: 'Submit for Review', states: ['draft'] },
      { m: 'action_request_approval', l: 'Request Certification', states: ['draft', 'review'],
        asks: [{ label: 'Why should this dashboard be certified? (decision it supports)', kwarg: 'justification' }] },
      { m: 'action_retire', l: 'Retire Dashboard', states: ['certified'] }
    ] },
  'M25-schedules': { kind: 'model_list', model: 'fix.bi.distribution.schedule', stateField: 'last_status',
    cols: ['name', 'report_key', 'cadence', 'recipients', 'format', 'active', 'last_status', 'last_sent_at', 'last_note'],
    empty: 'No distribution is scheduled. + New sends one standard pack to named internal users on a cadence.',
    actions: [
      { m: 'action_send_now', l: 'Send Now' }
    ] },
  'M25-alerts': { kind: 'model_list', model: 'fix.bi.alert.subscription', stateField: 'active',
    cols: ['name', 'metric_key', 'comparator', 'threshold', 'recipients', 'active', 'last_value', 'last_fired_at'],
    empty: 'No threshold alert yet. + New watches one measured metric against a threshold; the evaluator checks it hourly.' },

  /* Platform surfaces kept from the first build (extra, not registry). */
  'M25-bi': { kind: 'bi_exec' },
  /* creating and running a sync is a BI Sync Operator act (ACL + server) */
  'M25-sync': { kind: 'model_list', model: 'fix.bi.sync.config',
    cols: ['name', 'dataset_scope', 'sync_frequency', 'target_workspace', 'enabled',
      'last_test_status', 'last_test_note', 'last_sync_at'],
    empty: 'No analytics dataset connection yet. A BI Sync Operator adds one with + New; Run Snapshot Now records the first measured snapshot.',
    actions: [
      { m: 'action_test_connection', l: 'Test Configuration' },
      { m: 'action_run_sync', l: 'Run Snapshot Now' }
    ] },
  'M25-logs': { kind: 'model_list', model: 'fix.bi.sync.log', create: false,
    cols: ['config_id', 'dataset_scope', 'ran_at', 'ran_by', 'status', 'notes'],
    stateField: 'status',
    empty: 'No snapshot has run. Each run of a sync connection (operator button or the daily cron) writes one row here; the log is append-only.' },
  /* FR-BID-034 the spreadsheet-retirement register (KPI-094 -> zero) */
  'M25-packs': { kind: 'model_list', model: 'fix.bi.manual.pack', stateField: 'state',
    cols: ['name', 'function_area', 'owner_id', 'frequency', 'effort_hours', 'replacement_dashboard_id', 'replacement_report_key', 'state', 'reconciliation_result', 'retired_at'],
    empty: 'No manual pack is registered. + New registers a spreadsheet pack with its owner and effort; name its replacement, run both in parallel, reconcile, then retire it.',
    actions: [
      { m: 'action_start_parallel_run', l: 'Start Parallel Run', states: ['registered', 'investigated'] },
      { m: 'action_reconcile_matched', l: 'Reconciled: Figures Match', states: ['parallel_run'],
        asks: [{ label: 'Reconciliation note (periods compared)', kwarg: 'note' }] },
      { m: 'action_reconcile_discrepancy', l: 'Record Discrepancy', states: ['parallel_run'],
        asks: [{ label: 'What differs? (investigated against the M62 metric)', kwarg: 'note' }] },
      { m: 'action_retire', l: 'Retire Pack', states: ['accepted'] }
    ] },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M25-form-dashboard': {
    kind: 'model_form',
    model: 'fix.bi.dashboard',
    title: 'Dashboard',
    back: 'M25-builder',
    status: { field: 'state', labels: { draft: 'Draft', review: 'In Review', certified: 'Certified', retired: 'Retired' } },
    sections: [
      {
        title: 'Dashboard Definition',
        note: 'A saved dashboard binds a name to one role cockpit and is born a draft. Review needs a named Data Steward; certification is decided by a certifier who is not the author (M63).',
        fields: [
          { name: 'name', required: true, label: 'Dashboard Name' },
          { name: 'role', required: true, label: 'Target Role' },
          { name: 'description', label: 'Description', type: 'text' },
          { name: 'steward_id', label: 'Data Steward (reviews before certification)' },
          { name: 'is_shared', label: 'Shared with every internal user (certified dashboards only)' }
        ]
      },
      {
        title: 'Governance (system)',
        fields: [
          { name: 'owner_id', readonly: true, label: 'Author' },
          { name: 'certified_by', readonly: true, label: 'Certified By' },
          { name: 'certified_at', readonly: true, label: 'Certified At' }
        ]
      }
    ]
  },

  'M25-form-schedule': {
    kind: 'model_form',
    model: 'fix.bi.distribution.schedule',
    title: 'Distribution Schedule',
    back: 'M25-schedules',
    status: { field: 'last_status', labels: { never: 'Never Sent', sent: 'Sent', failed: 'Failed', partial: 'Partial' } },
    sections: [
      {
        title: 'Distribution',
        note: 'One standard pack, one cadence, named recipients. Every recipient must be an active internal user; their entitlement to the pack is checked again at every send, and every send is logged.',
        fields: [
          { name: 'name', required: true, label: 'Schedule Name' },
          { name: 'report_key', required: true, label: 'Report', type: 'selection', choices: SCHEDULE_REPORTS },
          { name: 'cadence', required: true, label: 'Cadence' },
          { name: 'recipients', required: true, label: 'Recipients (internal user e-mails, comma-separated)' },
          { name: 'format', required: true, label: 'Format' },
          { name: 'active', label: 'Active' }
        ]
      },
      {
        title: 'Delivery History (system)',
        fields: [
          { name: 'last_status', readonly: true, label: 'Last Status' },
          { name: 'last_sent_at', readonly: true, label: 'Last Sent At' },
          { name: 'last_note', readonly: true, label: 'Last Run Note' }
        ]
      }
    ]
  },

  'M25-form-alert': {
    kind: 'model_form',
    model: 'fix.bi.alert.subscription',
    title: 'Alert Subscription',
    back: 'M25-alerts',
    status: { field: 'active', labels: { true: 'Active', false: 'Inactive' } },
    sections: [
      {
        title: 'Threshold',
        note: 'Watches one measured metric against a threshold; the evaluator checks it hourly under this alert’s company and stamps the value. Outbound notification transport is porting phase and is never simulated.',
        fields: [
          { name: 'name', required: true, label: 'Alert Name' },
          { name: 'metric_key', required: true, label: 'Metric', type: 'selection', choices: ALERT_METRICS },
          { name: 'comparator', required: true, label: 'Comparator' },
          { name: 'threshold', required: true, label: 'Threshold Value' },
          { name: 'recipients', required: true, label: 'Recipients (comma-separated)' },
          { name: 'active', label: 'Active' }
        ]
      },
      {
        title: 'Last Evaluation (system)',
        fields: [
          { name: 'last_value', readonly: true, label: 'Last Measured Value' },
          { name: 'last_checked_at', readonly: true, label: 'Last Checked' },
          { name: 'last_fired_at', readonly: true, label: 'Last Fired' }
        ]
      }
    ]
  },

  'M25-form-sync': {
    kind: 'model_form',
    model: 'fix.bi.sync.config',
    title: 'Sync Connection',
    back: 'M25-sync',
    status: { field: 'last_test_status', labels: { never: 'Not Tested', ok: 'Configuration Valid', fail: 'Configuration Invalid' } },
    sections: [
      {
        title: 'Dataset Connection',
        note: 'Defines one analytics dataset the external BI workspace draws from. Snapshots are measured from the live tables under this connection’s company; the outbound transport stays closed until operator credentials exist. BI Sync Operators only.',
        fields: [
          { name: 'name', required: true, label: 'Connection Name' },
          { name: 'dataset_scope', required: true, label: 'Dataset Scope' },
          { name: 'sync_frequency', required: true, label: 'Snapshot Frequency' },
          { name: 'target_workspace', label: 'Target Workspace' },
          { name: 'enabled', label: 'Enabled' },
          { name: 'notes', label: 'Notes', type: 'text' }
        ]
      },
      {
        title: 'Status (system)',
        fields: [
          { name: 'last_test_note', readonly: true, label: 'Last Test Note' },
          { name: 'last_sync_at', readonly: true, label: 'Last Snapshot' }
        ]
      }
    ]
  },

  'M25-form-pack': {
    kind: 'model_form',
    model: 'fix.bi.manual.pack',
    title: 'Manual Pack',
    newLabel: 'Register a Manual Pack',
    back: 'M25-packs',
    status: { field: 'state', labels: { registered: 'Registered', parallel_run: 'Parallel Run', investigated: 'Discrepancy Investigated', accepted: 'Replacement Accepted', retired: 'Retired' } },
    sections: [
      {
        title: 'The Manual Pack',
        note: 'A spreadsheet or hand-made management pack on the register. KPI-094 counts these down to zero.',
        fields: [
          { name: 'name', required: true, label: 'Pack Name' },
          { name: 'function_area', required: true, label: 'Function' },
          { name: 'owner_id', required: true, label: 'Pack Owner (assembles it today)' },
          { name: 'frequency', required: true, label: 'Frequency' },
          { name: 'effort_hours', label: 'Effort (hours per cycle)' },
          { name: 'metrics_harvested', label: 'Metrics in the Pack', type: 'text' }
        ]
      },
      {
        title: 'Replacement',
        note: 'A certified dashboard or a standard report. The parallel run starts only when one is named.',
        fields: [
          { name: 'replacement_dashboard_id', label: 'Replacement Dashboard' },
          { name: 'replacement_report_key', label: 'Replacement Report', type: 'selection', choices: SCHEDULE_REPORTS }
        ]
      },
      {
        title: 'Retirement (system)',
        note: 'Recorded by the register’s actions: a Data Steward reconciles the parallel run; another steward than the owner retires the pack (BRU-BID-16/17).',
        fields: [
          { name: 'parallel_run_started_at', readonly: true, label: 'Parallel Run Started' },
          { name: 'reconciliation_result', readonly: true, label: 'Reconciliation' },
          { name: 'reconciliation_note', readonly: true, label: 'Reconciliation Note' },
          { name: 'reconciled_by', readonly: true, label: 'Reconciled By' },
          { name: 'retired_by', readonly: true, label: 'Retired By' },
          { name: 'retired_at', readonly: true, label: 'Retired At (source data closed)' }
        ]
      }
    ]
  }
};

/* built-in report chips -> their computed pack (D17) */
export const REPORT_ROUTES = {
  'M25:CCO Commercial': 'M25-ccO',
  'M25:Executive Pack': 'M25-rpt-exec',
  'M25:Branch League': 'M25-rpt-branch',
  'M25:Service KPI Pack': 'M25-rpt-service',
  'M25:Finance Pack': 'M25-rpt-finance',
  'M25:People Pack': 'M25-rpt-people',
  'M25:Any dashboard → export': 'M25-rpt-export',
  'M25:Standard Report Library': 'M25-library'
};

export const FORM_MODELS = {
  'M25:Dashboard': 'fix.bi.dashboard',
  'M25:Distribution Schedule': 'fix.bi.distribution.schedule',
  'M25:Alert Subscription': 'fix.bi.alert.subscription',
  'M25:Sync Connection': 'fix.bi.sync.config',
  'M25:Manual Pack': 'fix.bi.manual.pack'
};

export const FORM_CHIPS = {
  'M25:Dashboard': 'M25-form-dashboard',
  'M25:Distribution Schedule': 'M25-form-schedule',
  'M25:Alert Subscription': 'M25-form-alert',
  'M25:Sync Connection': 'M25-form-sync',
  'M25:Manual Pack': 'M25-form-pack',
  'M25:__by_model__': {
    'fix.bi.dashboard': 'M25-form-dashboard',
    'fix.bi.distribution.schedule': 'M25-form-schedule',
    'fix.bi.alert.subscription': 'M25-form-alert',
    'fix.bi.sync.config': 'M25-form-sync',
    'fix.bi.manual.pack': 'M25-form-pack'
  },
  'M25:__by_screen__': {
    'M25-builder': 'M25-form-dashboard',
    'M25-schedules': 'M25-form-schedule',
    'M25-alerts': 'M25-form-alert',
    'M25-sync': 'M25-form-sync',
    'M25-packs': 'M25-form-pack'
  }
};

export const CREATE = {
  M25: { screen: 'M25-form-dashboard', model: 'fix.bi.dashboard', label: 'Dashboard' }
};
