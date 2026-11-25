/** @odoo-module **/
/* A11 · Insights & Intelligence — M25 Business Intelligence (v2 re-audit).
 * Registry contract: 4 groups / 13 screens / 6 reports / 3 forms / freg 58
 * (the registry's 13 screens carry its exact en/bn labels; the 13 extra
 * pass-2 screens ship AFTER them). This file declares 26 screens / 7 report
 * chips / 9 forms in total (A1-F14: the header used to undercount).
 * Every dashboard renders inside the shell from /p03/bi/* live reads; every
 * report chip opens its own computed pack (controllers/a11/m25.py).
 *
 * Capture audit 2026-11-13: every sub-module page offers the record IT
 * captures. Standard Report Library and Lifecycle & Usage offered
 * "+ New Dashboard"; Embedded Analytics offered nothing (its sync list had no
 * form); the dashboard lifecycle (review, certification through M63,
 * retirement) was served but on no screen, and the dashboard form had no
 * Data Steward, so review was always refused. The spreadsheet-retirement
 * register (FR-BID-034, model fix.bi.manual.pack) is new.
 *
 * Second capture pass 2026-11-19: relevance against spec §5/§10. p1 had no
 * annotation (FR-BID-009) and the dashboard no business owner (BRU-BID-07) or
 * steward verification (BRU-BID-10); p2 captured a schedule, not the library
 * entry with owner and certification (FR-BID-011) or a reproducible run
 * (FR-BID-017); p3 offered a dashboard, not an exploration (FR-BID-018/019);
 * p4 raised nothing to acknowledge or escalate (FR-BID-025/026); p5 offered
 * the sync connection, not the embedded chart placement (FR-BID-029); p6 had
 * no low-bandwidth delivery (FR-BID-028); p7 had no usage telemetry
 * (FR-BID-033). */

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

/* The metric bank an alert may watch (controllers/a11/m25.py _metrics). The
 * AR keys split the invoices leg from the legacy take-on leg (D-L01): the
 * totals are 'ar_outstanding' / 'overdue_gt_60d'. */
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
  ['ar_outstanding_invoices', 'AR outstanding — open invoices (BDT)'],
  ['ar_outstanding_takeon', 'AR outstanding — legacy take-on (BDT)'],
  ['ar_outstanding', 'AR outstanding — total (BDT)'],
  ['overdue_gt_60d_invoices', 'AR overdue > 60d — invoices (BDT)'],
  ['overdue_gt_60d_takeon', 'AR overdue > 60d — take-on (BDT)'],
  ['overdue_gt_60d', 'AR overdue > 60 days — total (BDT)'],
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

/* What an annotation, an exploration or an embedded chart may name: the
 * measured metric bank, the only computation path (T-01). */
const METRIC_CHOICES = ALERT_METRICS;

const ROLE_CHOICES = [
  ['all', 'All Roles'], ['ceo', 'CEO'], ['coo', 'COO / Operations'], ['cfo', 'CFO / Finance'],
  ['cco', 'CCO / Commercial'], ['service', 'Service'], ['finance', 'Finance Analytics'],
  ['people', 'People'], ['quality', 'Quality']
];

export const MODULE = {
  area: 'A11', code: 'M25', en: 'Business Intelligence', title: 'M25 · Business Intelligence',
  bn: 'বিজনেস ইন্টেলিজেন্স', icon: '📊',
  desc: 'Role dashboards, standard report library, certified datasets, scheduled distribution, threshold alerts. KPI bases: Dashboards Live = certified dashboards only; Standard Reports = the canonical six; Weekly Manager Usage = distinct BI content viewers in 7 days; Scheduled Distributions = active schedules in your companies; Spreadsheets Retired = packs retired on the register.',
  kpis: [
    /* registry labels; `c` states the measured basis (A1-F03) */
    { l: 'Dashboards Live', m: 'dashboards_live', c: 'certified dashboards only (drafts are the author\'s workspace)' },
    { l: 'Standard Reports', m: 'standard_reports', c: 'the canonical six-pack library, not the catalogues' },
    { l: 'Weekly Manager Usage', m: 'weekly_manager_usage', c: 'distinct users who viewed BI content in 7 days (fix.bi.content.usage)' },
    { l: 'Load Time p95', m: 'load_time_p95', src: false },
    { l: 'Scheduled Distributions', m: 'scheduled_distributions', c: 'active distribution schedules in your companies' },
    { l: 'Spreadsheets Retired', m: 'spreadsheets_retired', c: 'packs retired on the spreadsheet-retirement register' }
  ],
  groups: [
    { en: 'Executive', screens: [
      { id: 'M25-ceo', en: 'CEO Cockpit', bn: 'সিইও ককপিট', t: 'd' },
      { id: 'M25-coo', en: 'COO / Ops Board (Live)', bn: 'অপারেশন বোর্ড', t: 'd' },
      { id: 'M25-cfo', en: 'CFO Dashboard', bn: 'সিএফও', t: 'd' },
      { id: 'M25-ccO', en: 'CCO Commercial', bn: 'সিসিও', t: 'd' },
      { id: 'M25-weekly', en: 'Weekly Executive Review', bn: 'সাপ্তাহিক নির্বাহী রিভিউ', t: 'r' },
      { id: 'M25-annotations', en: 'Annotations', bn: 'টীকা', t: 'g' }
    ]},
    { en: 'Functional', screens: [
      { id: 'M25-library', en: 'Standard Report Library', bn: 'স্ট্যান্ডার্ড রিপোর্ট লাইব্রেরি', t: 'r' },
      { id: 'M25-reportdefs', en: 'Report Definitions', bn: 'রিপোর্ট সংজ্ঞা', t: 'g' },
      { id: 'M25-runs', en: 'Report Runs', bn: 'রিপোর্ট রান', t: 'g' },
      { id: 'M25-service', en: 'Service Analytics', bn: 'সার্ভিস বিশ্লেষণ', t: 'd' },
      { id: 'M25-branch', en: 'Branch League Table', bn: 'শাখা লিগ টেবিল', t: 'r' },
      { id: 'M25-finance', en: 'Finance Analytics', bn: 'আর্থিক বিশ্লেষণ', t: 'd' },
      { id: 'M25-people', en: 'People Analytics', bn: 'জনবল বিশ্লেষণ', t: 'd' },
      { id: 'M25-quality', en: 'Quality Analytics', bn: 'গুণগত বিশ্লেষণ', t: 'd' }
    ]},
    { en: 'Self-Service', screens: [
      { id: 'M25-explorations', en: 'Explorations', bn: 'অনুসন্ধান', t: 'g' },
      { id: 'M25-datasets', en: 'Certified Datasets', bn: 'প্রত্যয়িত ডেটাসেট', t: 'r' },
      { id: 'M25-builder', en: 'Dashboard Builder', bn: 'ড্যাশবোর্ড নির্মাতা', t: 'g' },
      { id: 'M25-bi', en: 'BI Role Explorer', bn: 'বিআই রোল এক্সপ্লোরার', t: 'c' }
    ]},
    { en: 'Operations', screens: [
      { id: 'M25-schedules', en: 'Scheduled Distribution', bn: 'নির্ধারিত বিতরণ', t: 'g' },
      { id: 'M25-alerts', en: 'Threshold Alerts', bn: 'সতর্কতা', t: 'g' },
      { id: 'M25-alert-raised', en: 'Raised Alerts', bn: 'উত্থাপিত অ্যালার্ট', t: 'g' },
      { id: 'M25-embedded', en: 'Embedded Surfaces', bn: 'এমবেডেড সারফেস', t: 'g' },
      { id: 'M25-sync', en: 'Sync Connections', bn: 'সিঙ্ক সংযোগ', t: 'g' },
      { id: 'M25-logs', en: 'Sync Logs', bn: 'সিঙ্ক লগ', t: 'g' },
      { id: 'M25-packs', en: 'Spreadsheet Retirement', bn: 'স্প্রেডশিট অবসর রেজিস্টার', t: 'g' },
      { id: 'M25-usage', en: 'Content Usage', bn: 'কনটেন্ট ব্যবহার', t: 'g' }
    ]}
  ],
  reports: ['Executive Pack', 'Branch League', 'Service KPI Pack', 'Finance Pack', 'People Pack', 'Any dashboard → export', 'Standard Report Library'],
  forms: ['Dashboard', 'Distribution Schedule', 'Alert Subscription', 'Sync Connection', 'Manual Pack',
    'Annotation', 'Report Definition', 'Exploration', 'Embedded Surface'],
  cross: ['M62 semantic layer', 'M26 model outputs', 'P06 analytics portal', 'M54 FP&A'],
  freg: { src: 58, sub: [
    /* a role dashboard is a saved dashboard bound to one role cockpit; its
     * business owner explains a figure with an annotation (FR-BID-009) */
    ['1', 'Role Dashboards', 12, { model: 'fix.bi.dashboard', cols: ['name', 'role', 'tier', 'state', 'business_owner_id', 'steward_id', 'verified_at'], screens: ['M25-ceo', 'M25-coo', 'M25-cfo', 'M25-ccO', 'M25-annotations'], reports: ['Executive Pack'], forms: ['Dashboard', 'Annotation'] }],
    /* the library entry: a pack's business owner, definition and
     * certification (FR-BID-011); its runs are stamped for reproduction */
    ['2', 'Standard Report Library', 10, { report: 'report_library', create: 'M25-form-reportdef', screens: ['M25-library', 'M25-reportdefs', 'M25-runs', 'M25-weekly', 'M25-branch', 'M25-service', 'M25-finance'], reports: ['Standard Report Library', 'Executive Pack', 'Branch League', 'Service KPI Pack', 'Finance Pack', 'People Pack'], forms: ['Report Definition', 'Distribution Schedule'] }],
    /* governed exploration: a saved question in a personal workspace,
     * promoted to a draft dashboard for certification (FR-BID-018..020) */
    ['3', 'Self-Service', 8, { model: 'fix.bi.exploration', cols: ['name', 'metric_key', 'metric_key_2', 'target_role', 'workspace', 'state', 'author_id', 'last_run_at'], screens: ['M25-explorations', 'M25-builder', 'M25-datasets', 'M25-bi'], reports: ['Any dashboard → export'], forms: ['Exploration', 'Dashboard'] }],
    ['4', 'Distribution & Alerting', 9, { model: 'fix.bi.distribution.schedule', cols: ['name', 'report_key', 'cadence', 'channel', 'format', 'last_status'], screens: ['M25-schedules', 'M25-alerts', 'M25-alert-raised'], reports: [], forms: ['Distribution Schedule', 'Alert Subscription'] }],
    /* the chart placed inside an operational screen or portal (FR-BID-029..032) */
    ['5', 'Embedded Analytics', 7, { model: 'fix.bi.embedded.surface', cols: ['name', 'host_module', 'host_screen', 'audience', 'context_binding', 'metric_key', 'token_ttl_seconds', 'state'], screens: ['M25-embedded', 'M25-sync', 'M25-logs', 'M25-datasets'], reports: [], forms: ['Embedded Surface', 'Sync Connection'] }],
    /* mobile renders the role cockpits; what a branch on a poor connection
     * gets is a low-bandwidth text summary (FR-BID-028) */
    ['6', 'Mobile', 5, { model: 'fix.bi.distribution.schedule', create: 'M25-form-schedule', createLabel: 'New Low-Bandwidth Summary', cols: ['name', 'report_key', 'cadence', 'recipients', 'last_status', 'last_sent_at'], screens: ['M25-coo', 'M25-people', 'M25-quality', 'M25-schedules'], reports: ['Service KPI Pack', 'People Pack'], forms: ['Distribution Schedule', 'Dashboard'], domain: [['channel', '=', 'low_bandwidth']] }],
    /* FR-BID-022 content lifecycle (on the Dashboard Builder), FR-BID-033
     * usage and FR-BID-034 the spreadsheet-retirement register */
    ['7', 'Lifecycle & Usage', 7, { model: 'fix.bi.manual.pack', cols: ['name', 'function_area', 'owner_id', 'frequency', 'effort_hours', 'state', 'reconciliation_result', 'retired_at'], screens: ['M25-packs', 'M25-builder', 'M25-usage'], reports: ['Any dashboard → export'], forms: ['Manual Pack', 'Dashboard'] }]
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
    cols: ['name', 'role', 'tier', 'state', 'business_owner_id', 'steward_id', 'verified_at', 'is_shared', 'owner_id', 'certified_by'],
    empty: 'No dashboard is saved yet. + New saves one as a draft for a role; name its business owner and Data Steward, submit it for review, have the steward verify it and request certification.',
    actions: [
      { m: 'action_submit_review', l: 'Submit for Review', states: ['draft'] },
      { m: 'action_steward_verify', l: 'Verify Content', states: ['review'],
        asks: [{ label: 'What was verified? (definition, scope behaviour, Bengali rendering)', kwarg: 'note' }] },
      { m: 'action_request_approval', l: 'Request Certification', states: ['review'],
        asks: [{ label: 'Why should this dashboard be certified? (decision it supports)', kwarg: 'justification' }] },
      { m: 'action_retire', l: 'Retire Dashboard', states: ['certified'] }
    ] },
  'M25-schedules': { kind: 'model_list', model: 'fix.bi.distribution.schedule', stateField: 'last_status',
    cols: ['name', 'report_key', 'cadence', 'channel', 'recipients', 'format', 'active', 'last_status', 'last_sent_at', 'last_note'],
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

  /* ---- second capture pass (2026-11-19) ---- */
  'M25-annotations': { kind: 'model_list', model: 'fix.bi.annotation',
    cols: ['name', 'role', 'dashboard_id', 'metric_key', 'period', 'author_id', 'active'],
    empty: 'No annotation yet. + New explains a figure or a period on a role cockpit; its audience sees it under the tiles (FR-BID-009).' },
  'M25-reportdefs': { kind: 'model_list', model: 'fix.bi.report.definition', stateField: 'certification_state',
    cols: ['name', 'report_key', 'business_owner_id', 'layout_type', 'retention_to_m24', 'certification_state', 'certified_by', 'run_count'],
    empty: 'No library report is registered. + New names a pack’s business owner and definition; a steward who is neither certifies it.',
    actions: [
      { m: 'action_generate_run', l: 'Generate Run', states: ['draft', 'certified'],
        asks: [{ label: 'Period from (YYYY-MM-DD, optional)', kwarg: 'date_from' }, { label: 'Period to (YYYY-MM-DD, optional)', kwarg: 'date_to' }] },
      { m: 'action_certify', l: 'Certify', states: ['draft'] },
      { m: 'action_retire', l: 'Retire', states: ['draft', 'certified'] }
    ] },
  'M25-runs': { kind: 'model_list', model: 'fix.bi.report.run', create: false,
    cols: ['report_key', 'generated_at', 'requested_by', 'period_from', 'period_to', 'scope_applied', 'row_count', 'duration_ms', 'definition_certified', 'restatement_flag', 'restatement_reference'],
    empty: 'No run yet. Generate Run on a report definition records one, stamped with its data as-of time, scope and definition version.',
    actions: [
      { m: 'action_flag_restatement', l: 'Flag Restatement',
        asks: [{ label: 'Restatement reference (M62 / M19)', kwarg: 'reference' }] }
    ] },
  'M25-explorations': { kind: 'model_list', model: 'fix.bi.exploration', stateField: 'state',
    cols: ['name', 'metric_key', 'metric_key_2', 'metric_key_3', 'target_role', 'workspace', 'state', 'author_id', 'last_run_at'],
    empty: 'No saved question yet. + New composes one from measured metrics in your personal workspace; Run answers it, Promote builds a draft dashboard for certification.',
    actions: [
      { m: 'action_run', l: 'Run Question' },
      { m: 'action_share', l: 'Share with Analysts', states: ['open'] },
      { m: 'action_promote', l: 'Promote to Dashboard', states: ['open'] }
    ] },
  'M25-alert-raised': { kind: 'model_list', model: 'fix.bi.alert.instance', create: false, stateField: 'state',
    cols: ['alert_id', 'metric_key', 'observed_value', 'threshold', 'raised_at', 'repeat_count', 'state', 'acknowledged_by', 'escalated_to_id', 'closed_at'],
    empty: 'No alert has been raised. The hourly evaluator raises one when a threshold is crossed; a repeat inside the suppression window adds to it.',
    actions: [
      { m: 'action_acknowledge', l: 'Acknowledge', states: ['open', 'escalated'],
        asks: [{ label: 'What is being done about it?', kwarg: 'note' }] },
      { m: 'action_close', l: 'Close', states: ['acknowledged'],
        asks: [{ label: 'Why is the alert closed?', kwarg: 'note' }] }
    ] },
  'M25-embedded': { kind: 'model_list', model: 'fix.bi.embedded.surface', stateField: 'state',
    cols: ['name', 'host_module', 'host_screen', 'audience', 'context_binding', 'metric_key', 'token_ttl_seconds', 'state', 'activated_by'],
    empty: 'No embedded chart yet. + New places a chart on an operational screen or portal; a steward who is not the author activates it.',
    actions: [
      { m: 'action_activate', l: 'Activate', states: ['draft'] },
      { m: 'action_retire', l: 'Retire', states: ['draft', 'active'] }
    ] },
  'M25-usage': { kind: 'model_list', model: 'fix.bi.content.usage', create: false,
    cols: ['content_type', 'content_ref', 'user_id', 'device_class', 'viewed_at'],
    empty: 'No view recorded yet. Each opening of a role cockpit is logged here with its device class (FR-BID-033).' },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M25-form-dashboard': {
    kind: 'model_form',
    model: 'fix.bi.dashboard',
    title: 'Dashboard',
    back: 'M25-builder',
    status: { field: 'state', labels: { draft: 'Draft', review: 'In Review', certified: 'Certified', retired: 'Retired' } },
    tabs: [
      { id: 'definition', label: '1. Definition', bn: '১. সংজ্ঞা', icon: '📊', badge: '6' },
      { id: 'ownership', label: '2. Ownership & Review', bn: '২. মালিকানা ও পর্যালোচনা', icon: '👤', badge: '5' },
      { id: 'governance', label: '3. Verification & Certification', bn: '৩. যাচাই ও সার্টিফিকেশন', icon: '✅', badge: '6' }
    ],
    sections: [
      {
        tab: 'definition',
        title: 'Dashboard Definition',
        note: 'A saved dashboard binds a name to one role cockpit and is born a draft.',
        fields: [
          { name: 'name', required: true, label: 'Dashboard Name' },
          { name: 'name_bn', label: 'Dashboard Name (Bengali)' },
          { name: 'role', required: true, label: 'Target Role' },
          { name: 'tier', required: true, label: 'Tier' },
          { name: 'description', label: 'Description', type: 'text' },
          { name: 'is_shared', label: 'Shared with every internal user (certified dashboards only)' }
        ]
      },
      {
        tab: 'ownership',
        title: 'Business Owner and Steward',
        note: 'Every published dashboard has a named business owner who is not its author (BRU-BID-07). Review needs a named Data Steward.',
        fields: [
          { name: 'business_owner_id', label: 'Business Owner (accepts the content)' },
          { name: 'decision_supported', label: 'Decision It Supports', type: 'text' },
          { name: 'steward_id', label: 'Data Steward (verifies before certification)' },
          { name: 'review_cycle', required: true, label: 'Periodic Review' },
          { name: 'owner_id', readonly: true, label: 'Author' }
        ]
      },
      {
        tab: 'governance',
        title: 'Verification and Certification (system)',
        note: 'The steward verifies definition, scope and the Bengali rendering (BRU-BID-10); a certifier who is not the author decides the request (M63). Editing the content voids the verification.',
        fields: [
          { name: 'verified_by', readonly: true, label: 'Verified By' },
          { name: 'verified_at', readonly: true, label: 'Verified At' },
          { name: 'verification_note', readonly: true, label: 'What Was Verified' },
          { name: 'certified_by', readonly: true, label: 'Certified By' },
          { name: 'certified_at', readonly: true, label: 'Certified At' },
          { name: 'retired_at', readonly: true, label: 'Retired At' }
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
          { name: 'channel', required: true, label: 'Channel (low-bandwidth: text summary, no attachment)' },
          { name: 'format', required: true, label: 'Format (attachment)' },
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
        title: 'Ownership, Suppression and Escalation',
        note: 'The receiving role owns the threshold (BRU-BID-13). A repeat inside the suppression window adds to the open alert (T-14); an alert nobody acknowledges escalates (BRU-BID-14).',
        fields: [
          { name: 'owner_id', label: 'Threshold Owner' },
          { name: 'suppression_hours', label: 'Suppression Window (hours)' },
          { name: 'escalate_after_hours', label: 'Escalate After (hours)' },
          { name: 'escalate_to_id', label: 'Escalate To' }
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
  },

  /* ---- second capture pass forms (2026-11-19) ---- */
  'M25-form-annotation': {
    kind: 'model_form',
    model: 'fix.bi.annotation',
    title: 'Annotation',
    back: 'M25-annotations',
    sections: [
      {
        title: 'Explain a Figure',
        note: 'Shown under the tiles of the role cockpit to its audience. On a dashboard with a business owner, that owner (or a steward) writes it (FR-BID-009).',
        fields: [
          { name: 'name', required: true, label: 'Headline' },
          { name: 'role', required: true, label: 'Shown On (Role Cockpit)', type: 'selection', choices: ROLE_CHOICES },
          { name: 'dashboard_id', label: 'Saved Dashboard (optional)' },
          { name: 'metric_key', label: 'Metric', type: 'selection', choices: METRIC_CHOICES },
          { name: 'period', required: true, label: 'Period (e.g. 2026-11, Week 46)' },
          { name: 'text_en', required: true, label: 'Explanation (English)', type: 'text' },
          { name: 'text_bn', label: 'Explanation (Bengali)', type: 'text' },
          { name: 'active', label: 'Visible' }
        ]
      }
    ]
  },

  'M25-form-reportdef': {
    kind: 'model_form',
    model: 'fix.bi.report.definition',
    title: 'Report Definition',
    back: 'M25-reportdefs',
    status: { field: 'certification_state', labels: { draft: 'Draft', certified: 'Certified', retired: 'Retired' } },
    sections: [
      {
        title: 'Library Report',
        note: 'Registers one standard pack with its business owner and definition (FR-BID-011). The figures stay computed by the pack; a steward who neither registered nor owns it certifies it.',
        fields: [
          { name: 'report_key', required: true, label: 'Report', type: 'selection', choices: SCHEDULE_REPORTS },
          { name: 'name', required: true, label: 'Report Name' },
          { name: 'name_bn', label: 'Report Name (Bengali)' },
          { name: 'owning_module', required: true, label: 'Owning Module' },
          { name: 'business_owner_id', required: true, label: 'Business Owner' },
          { name: 'definition', required: true, label: 'Definition (what it measures, for whom)', type: 'text' }
        ]
      },
      {
        title: 'Rendering and Retention',
        fields: [
          { name: 'layout_type', required: true, label: 'Layout' },
          { name: 'fmt_csv', label: 'CSV' },
          { name: 'fmt_xlsx', label: 'XLSX' },
          { name: 'fmt_pdf', label: 'PDF' },
          { name: 'retention_to_m24', label: 'File runs as records (M24)' },
          { name: 'certified_by', readonly: true, label: 'Certified By' },
          { name: 'certified_at', readonly: true, label: 'Certified At' }
        ]
      }
    ]
  },

  'M25-form-exploration': {
    kind: 'model_form',
    model: 'fix.bi.exploration',
    title: 'Exploration',
    back: 'M25-explorations',
    status: { field: 'state', labels: { open: 'Exploring', promoted: 'Promoted to Dashboard' } },
    sections: [
      {
        title: 'The Question',
        note: 'Composed from measured metrics only; a metric is never redefined here (FR-BID-018). It stays in your personal workspace until you share it, and reaches a management audience only as a certified dashboard (BRU-BID-06).',
        fields: [
          { name: 'name', required: true, label: 'Title' },
          { name: 'question', required: true, label: 'Question', type: 'text' },
          { name: 'metric_key', required: true, label: 'Metric', type: 'selection', choices: METRIC_CHOICES },
          { name: 'metric_key_2', label: 'Second Metric', type: 'selection', choices: METRIC_CHOICES },
          { name: 'metric_key_3', label: 'Third Metric', type: 'selection', choices: METRIC_CHOICES },
          { name: 'target_role', required: true, label: 'Role It Would Serve', type: 'selection', choices: ROLE_CHOICES }
        ]
      },
      {
        title: 'Answer (system)',
        fields: [
          { name: 'workspace', readonly: true, label: 'Workspace' },
          { name: 'last_run_at', readonly: true, label: 'Last Run' },
          { name: 'last_result', readonly: true, label: 'Last Answer' },
          { name: 'dashboard_id', readonly: true, label: 'Promoted Dashboard' }
        ]
      }
    ]
  },

  'M25-form-embedded': {
    kind: 'model_form',
    model: 'fix.bi.embedded.surface',
    title: 'Embedded Surface',
    back: 'M25-embedded',
    status: { field: 'state', labels: { draft: 'Draft', active: 'Active', retired: 'Retired' } },
    sections: [
      {
        title: 'Placement',
        note: 'The chart that sits inside an operational screen or a portal, scoped to the record in context (FR-BID-029). A portal chart shows only the viewing party (BRU-BID-18).',
        fields: [
          { name: 'name', required: true, label: 'Chart Name' },
          { name: 'host_module', required: true, label: 'Host Module (M01-M69, P01-P07)' },
          { name: 'host_screen', required: true, label: 'Host Screen' },
          { name: 'metric_key', required: true, label: 'Metric', type: 'selection', choices: METRIC_CHOICES },
          { name: 'metric_key_2', label: 'Second Metric', type: 'selection', choices: METRIC_CHOICES }
        ]
      },
      {
        title: 'Audience and Token',
        note: 'Every view gets a signed token bound to the viewer and the context, living the seconds below (30-900) and redeemable once (BRU-BID-12).',
        fields: [
          { name: 'audience', required: true, label: 'Audience' },
          { name: 'audience_group_id', label: 'Internal Audience Group' },
          { name: 'context_binding', required: true, label: 'Bound To' },
          { name: 'token_ttl_seconds', label: 'Token Lifetime (seconds; blank = 300)' },
          { name: 'activated_by', readonly: true, label: 'Activated By' }
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
  'M25:Manual Pack': 'fix.bi.manual.pack',
  'M25:Annotation': 'fix.bi.annotation',
  'M25:Report Definition': 'fix.bi.report.definition',
  'M25:Exploration': 'fix.bi.exploration',
  'M25:Embedded Surface': 'fix.bi.embedded.surface'
};

export const FORM_CHIPS = {
  'M25:Dashboard': 'M25-form-dashboard',
  'M25:Distribution Schedule': 'M25-form-schedule',
  'M25:Alert Subscription': 'M25-form-alert',
  'M25:Sync Connection': 'M25-form-sync',
  'M25:Manual Pack': 'M25-form-pack',
  'M25:Annotation': 'M25-form-annotation',
  'M25:Report Definition': 'M25-form-reportdef',
  'M25:Exploration': 'M25-form-exploration',
  'M25:Embedded Surface': 'M25-form-embedded',
  'M25:__by_model__': {
    'fix.bi.dashboard': 'M25-form-dashboard',
    'fix.bi.distribution.schedule': 'M25-form-schedule',
    'fix.bi.alert.subscription': 'M25-form-alert',
    'fix.bi.sync.config': 'M25-form-sync',
    'fix.bi.manual.pack': 'M25-form-pack',
    'fix.bi.annotation': 'M25-form-annotation',
    'fix.bi.report.definition': 'M25-form-reportdef',
    'fix.bi.exploration': 'M25-form-exploration',
    'fix.bi.embedded.surface': 'M25-form-embedded'
  },
  'M25:__by_screen__': {
    'M25-builder': 'M25-form-dashboard',
    'M25-schedules': 'M25-form-schedule',
    'M25-alerts': 'M25-form-alert',
    'M25-sync': 'M25-form-sync',
    'M25-packs': 'M25-form-pack',
    'M25-annotations': 'M25-form-annotation',
    'M25-reportdefs': 'M25-form-reportdef',
    'M25-explorations': 'M25-form-exploration',
    'M25-embedded': 'M25-form-embedded'
  }
};

export const CREATE = {
  M25: { screen: 'M25-form-dashboard', model: 'fix.bi.dashboard', label: 'Dashboard' }
};
