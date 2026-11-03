/** @odoo-module **/
/* A11 · Insights & Intelligence — M25 Business Intelligence (v2 re-audit).
 * Registry-faithful: 4 groups / 13 screens / 6 reports / 3 forms / freg 58.
 * Every dashboard renders inside the shell from /p03/bi/* live reads; every
 * report chip opens its own computed pack (controllers/a11/m25.py). */

export const MODULE = {
  area: 'A11', code: 'M25', en: 'Business Intelligence', title: 'M25 · Business Intelligence',
  bn: 'বিজনেস ইন্টেলিজেন্স', icon: '📊',
  desc: 'Role dashboards, standard report library, certified datasets, scheduled distribution, threshold alerts.',
  kpis: [
    { l: 'Dashboards Live', m: 'dashboards_live' },
    { l: 'Standard Reports', m: 'standard_reports' },
    { l: 'Weekly Manager Usage', m: 'weekly_manager_usage' },
    { l: 'Load Time p95 (ms)', m: 'load_time_p95' },
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
      { id: 'M25-service', en: 'Service Analytics', bn: 'সার্ভিস অ্যানালিটিক্স', t: 'd' },
      { id: 'M25-branch', en: 'Branch League Table', bn: 'শাখা লীগ', t: 'r' },
      { id: 'M25-finance', en: 'Finance Analytics', bn: 'ফিন্যান্স অ্যানালিটিক্স', t: 'd' },
      { id: 'M25-people', en: 'People Analytics', bn: 'পিপল অ্যানালিটিক্স', t: 'd' },
      { id: 'M25-quality', en: 'Quality Analytics', bn: 'কোয়ালিটি অ্যানালিটিক্স', t: 'd' }
    ]},
    { en: 'Self-Service', screens: [
      { id: 'M25-datasets', en: 'Certified Datasets', bn: 'সার্টিফাইড ডেটাসেট', t: 'g' },
      { id: 'M25-builder', en: 'Dashboard Builder', bn: 'ড্যাশবোর্ড বিল্ডার', t: 'c' },
      { id: 'M25-bi', en: 'BI Role Explorer', bn: 'বিআই রোল এক্সপ্লোরার', t: 'c' }
    ]},
    { en: 'Operations', screens: [
      { id: 'M25-schedules', en: 'Scheduled Distribution', bn: 'নির্ধারিত বিতরণ', t: 'g' },
      { id: 'M25-alerts', en: 'Threshold Alerts', bn: 'থ্রেশহোল্ড অ্যালার্ট', t: 'g' },
      { id: 'M25-sync', en: 'Sync Connections', bn: 'সিঙ্ক সংযোগ', t: 'g' },
      { id: 'M25-logs', en: 'Sync Logs', bn: 'সিঙ্ক লগ', t: 'g' }
    ]}
  ],
  reports: ['Executive Pack', 'Branch League', 'Service KPI Pack', 'Finance Pack', 'People Pack', 'Any dashboard → export'],
  forms: ['Dashboard', 'Distribution Schedule', 'Alert Subscription'],
  cross: ['All Modules'],
  freg: { src: 58, sub: [
    ['1', 'Role Dashboards', 12, { model: 'fix.bi.dashboard', cols: ['name', 'role', 'owner_id', 'is_shared', 'last_viewed_at'], screens: ['M25-ceo', 'M25-coo', 'M25-cfo', 'M25-ccO'] }],
    ['2', 'Standard Report Library', 10, { model: 'fix.bi.dashboard', cols: ['name', 'role', 'is_shared', 'owner_id'], screens: ['M25-weekly', 'M25-branch', 'M25-service', 'M25-finance'] }],
    ['3', 'Self-Service', 8, { model: 'fix.bi.dashboard', cols: ['name', 'role', 'owner_id', 'is_shared', 'last_viewed_at'], screens: ['M25-builder', 'M25-datasets', 'M25-bi'] }],
    ['4', 'Distribution & Alerting', 9, { model: 'fix.bi.distribution.schedule', cols: ['name', 'report_key', 'cadence', 'format', 'last_status'], screens: ['M25-schedules', 'M25-alerts'] }],
    ['5', 'Embedded Analytics', 7, { model: 'fix.bi.sync.config', cols: ['name', 'dataset_scope', 'target_workspace', 'sync_frequency', 'enabled'], screens: ['M25-sync', 'M25-logs'] }],
    ['6', 'Mobile', 5, { model: 'fix.bi.dashboard', cols: ['name', 'role', 'owner_id', 'last_viewed_at'], screens: ['M25-coo', 'M25-people', 'M25-quality'] }],
    ['7', 'Lifecycle & Usage', 7, { model: 'fix.bi.dashboard', cols: ['name', 'owner_id', 'last_viewed_at', 'is_shared'], screens: ['M25-builder', 'M25-logs'] }]
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

  /* Self-service + operations. */
  'M25-datasets': { kind: 'table_report', module: 'M25', report: 'dataset_catalog', title: 'Certified Datasets', period: false },
  'M25-builder': { kind: 'model_list', model: 'fix.bi.dashboard',
    cols: ['name', 'role', 'is_shared', 'owner_id', 'last_viewed_at'] },
  'M25-schedules': { kind: 'model_list', model: 'fix.bi.distribution.schedule', stateField: 'last_status',
    cols: ['name', 'report_key', 'cadence', 'recipients', 'format', 'active', 'last_status', 'last_sent_at'] },
  'M25-alerts': { kind: 'model_list', model: 'fix.bi.alert.subscription', stateField: 'active',
    cols: ['name', 'metric_key', 'comparator', 'threshold', 'recipients', 'active', 'last_value'] },

  /* Platform surfaces kept from the first build (extra, not registry). */
  'M25-bi': { kind: 'bi_exec' },
  'M25-sync': { kind: 'model_list', model: 'fix.bi.sync.config', create: false,
    cols: ['name', 'dataset_scope', 'sync_frequency', 'target_workspace', 'enabled',
      'last_test_status', 'last_test_note', 'last_sync_at'] },
  'M25-logs': { kind: 'model_list', model: 'fix.bi.sync.log', create: false,
    cols: ['config_id', 'dataset_scope', 'ran_at', 'status', 'notes'],
    stateField: 'status' },

  /* ============ D365 IN-WORKSPACE FORMS (registry's three) ============ */
  'M25-form-dashboard': {
    kind: 'model_form',
    model: 'fix.bi.dashboard',
    title: 'Dashboard',
    back: 'M25-builder',
    status: { field: 'role', labels: { all: 'All Roles', ceo: 'CEO', coo: 'COO', cfo: 'CFO', cco: 'CCO', service: 'Service', finance: 'Finance', people: 'People', quality: 'Quality' } },
    sections: [
      {
        title: 'Dashboard Definition',
        note: 'A saved dashboard binds a name to one role cockpit. The layout contract is JSON; empty means the role standard pack.',
        fields: [
          { name: 'name', required: true, label: 'Dashboard Name' },
          { name: 'role', required: true, label: 'Target Role' },
          { name: 'description', label: 'Description', type: 'text' },
          { name: 'is_shared', label: 'Shared with every internal user' }
        ]
      },
      {
        title: 'Governance (system)',
        fields: [
          { name: 'owner_id', readonly: true, label: 'Owner' },
          { name: 'last_viewed_at', readonly: true, label: 'Last Viewed' }
        ]
      }
    ]
  },

  'M25-form-schedule': {
    kind: 'model_form',
    model: 'fix.bi.distribution.schedule',
    title: 'Distribution Schedule',
    back: 'M25-schedules',
    status: { field: 'last_status', labels: { never: 'Never Sent', sent: 'Sent', failed: 'Failed' } },
    sections: [
      {
        title: 'Distribution',
        note: 'One report pack, one cadence, named recipients. The scheduler transport is porting phase — configuration is real, sends are never simulated.',
        fields: [
          { name: 'name', required: true, label: 'Schedule Name' },
          { name: 'report_key', required: true, label: 'Report (module:report)' },
          { name: 'cadence', required: true, label: 'Cadence' },
          { name: 'recipients', required: true, label: 'Recipients (comma-separated)' },
          { name: 'format', required: true, label: 'Format' },
          { name: 'active', label: 'Active' }
        ]
      },
      {
        title: 'Delivery History (system)',
        fields: [
          { name: 'last_status', readonly: true, label: 'Last Status' },
          { name: 'last_sent_at', readonly: true, label: 'Last Sent At' }
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
        note: 'Watches one KPI key (e.g. overdue_gt_60d) against a threshold. The metric is visible live on the role dashboards; outbound notification transport is porting phase.',
        fields: [
          { name: 'name', required: true, label: 'Alert Name' },
          { name: 'metric_key', required: true, label: 'KPI Metric Key' },
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
  'M25:Any dashboard → export': 'M25-rpt-export'
};

export const FORM_MODELS = {
  'M25:Dashboard': 'fix.bi.dashboard',
  'M25:Distribution Schedule': 'fix.bi.distribution.schedule',
  'M25:Alert Subscription': 'fix.bi.alert.subscription'
};

export const FORM_CHIPS = {
  'M25:Dashboard': 'M25-form-dashboard',
  'M25:Distribution Schedule': 'M25-form-schedule',
  'M25:Alert Subscription': 'M25-form-alert',
  'M25:__by_model__': {
    'fix.bi.dashboard': 'M25-form-dashboard',
    'fix.bi.distribution.schedule': 'M25-form-schedule',
    'fix.bi.alert.subscription': 'M25-form-alert'
  },
  'M25:__by_screen__': {
    'M25-builder': 'M25-form-dashboard',
    'M25-schedules': 'M25-form-schedule',
    'M25-alerts': 'M25-form-alert'
  }
};

export const CREATE = {
  M25: { screen: 'M25-form-dashboard', model: 'fix.bi.dashboard', label: 'Dashboard' }
};
