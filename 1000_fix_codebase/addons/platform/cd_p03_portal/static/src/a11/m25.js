/** @odoo-module **/
/* A11 · Insights & Intelligence — M25 Business Intelligence.
 * Backend: controllers/a11/m25.py (SURFACES, REPORTS, /p03/bi/kpis,
 * /p03/bi/exec) + domain/j_data_analytics/cd_bi_reporting (sync config and
 * the snapshot engine behind the BI Data Freshness KPI). Every screen
 * renders INSIDE the shell from live data: the executive C-Suite KPI
 * dashboard over the real order/estimate/invoice tables, the Weekly
 * Executive Business Review report, and the sync configuration + measured
 * run log surfaces. */

export const MODULE = {
  area: 'A11', code: 'M25', en: 'Business Intelligence', title: 'M25 · Business Intelligence',
  bn: 'বিজনেস ইন্টেলিজেন্স', icon: '📊',
  desc: 'Role dashboards, standard report library, embedded analytics, scheduled bursting, spreadsheet retirement.',
  kpis: [
    { l: 'BI Data Freshness (min)', m: 'bi_data_freshness' },
    { l: 'Open Orders', m: 'open_orders' },
    { l: 'In Repair Now', m: 'in_repair' },
    { l: 'Delivered MTD', m: 'delivered_mtd' },
    { l: 'Revenue MTD (est. ৳)', m: 'revenue_mtd' },
    { l: 'Invoices Issued MTD', m: 'invoiced_mtd' }
  ],
  groups: [
    { en: 'BI Dashboards', screens: [
      { id: 'M25-bi', en: 'Executive C-Suite KPI Dashboard', bn: 'এক্সিকিউটিভ ড্যাশবোর্ড', t: 'd' }
    ]},
    { en: 'Report Library', screens: [
      { id: 'M25-weekly', en: 'Weekly Executive Business Review', bn: 'সাপ্তাহিক নির্বাহী পর্যালোচনা', t: 'r' }
    ]},
    { en: 'Data Sync & Freshness', screens: [
      { id: 'M25-sync', en: 'Power BI Sync Configurations', bn: 'পাওয়ার বাইআই সিঙ্ক কনফিগ', t: 'g' },
      { id: 'M25-logs', en: 'Sync Run Log (measured snapshots)', bn: 'সিঙ্ক রান লগ', t: 'g' }
    ]}
  ],
  reports: ['Weekly Executive Business Review'],
  forms: ['Configure Power BI Sync'],
  cross: ['All Modules'],
  freg: {
    src: 88,
    sub: [
      ['1', 'Data Warehouse ETL Extraction', 10],
      ['2', 'Executive Metric Aggregator', 10]
    ]
  }
};

/* In-workspace data screens. bi_exec is the bespoke executive dashboard;
 * the weekly review rides the module REPORTS; sync surfaces ride the
 * whitelisted generic reader with the module's own actions. */
export const SCREENS = {
  'M25-bi': { kind: 'bi_exec' },
  'M25-weekly': { kind: 'table_report', module: 'M25', report: 'weekly_exec_review', period: false },
  'M25-sync': { kind: 'model_list', model: 'fix.bi.sync.config', create: false,
    cols: ['name', 'dataset_scope', 'sync_frequency', 'target_workspace', 'enabled',
      'last_test_status', 'last_test_note', 'last_sync_at'] },
  'M25-logs': { kind: 'model_list', model: 'fix.bi.sync.log', create: false,
    cols: ['config_id', 'dataset_scope', 'ran_at', 'status', 'notes'],
    stateField: 'status' }
};

/* built-in report chips -> the screen that shows that report */
export const REPORT_ROUTES = {
  'M25:Weekly Executive Business Review': 'M25-weekly'
};

/* data-entry form chips -> real model forms */
export const FORM_MODELS = {
  'M25:Configure Power BI Sync': 'fix.bi.sync.config'
};

/* the module's "+ New" surface */
export const CREATE = {
  M25: { model: 'fix.bi.sync.config', label: 'BI Sync Config' }
};
