/** @odoo-module **/
/* A02 · Service Operations — M01 Service Requests & Orders.
 * One file per module (merged into P03_MODULES and the screen maps by
 * p03_modules_meta.js): the registry entry, the in-workspace data screens,
 * built-in report routes, data-entry form chips and the "+ New" surface.
 *
 * Backend: controllers/a02/m01.py (SURFACES, kpis, REPORTS) plus the
 * bespoke /p03/orders/list scopes and /p03/stats in p03_service_order_api.
 * Every screen renders INSIDE the shell from live data — the order grid,
 * operations board, intake console, model lists and table reports. */

export const MODULE = {
  area: 'A02', code: 'M01', en: 'Service Requests & Orders', title: 'M01 · Service Requests & Orders',
  bn: 'সার্ভিস অর্ডার', icon: '📋',
  desc: 'Master record of every service need from 12 intake channels — lifecycle, entitlement, estimates, SLA.',
  kpis: [
    { l: 'Open Orders', m: 'open_orders' },
    { l: 'SLA At-Risk', m: 'sla_at_risk' },
    { l: 'TAT < 24h (IT)', m: 'tat_under_24h' },
    { l: 'Estimate Conv.', m: 'estimate_conversion' },
    { l: 'Intake < 3 min', m: 'intake_minutes' },
    { l: 'Rework Rate', m: 'rework_rate' }
  ],
  groups: [
    { en: 'Intake & Channels', screens: [
      { id: 'M01-board', en: 'Order Operations Board', bn: 'অর্ডার অপারেশন্স বোর্ড', t: 'd' },
      { id: 'M01-all', en: 'All Service Orders', bn: 'সকল সার্ভিস অর্ডার', t: 'g' },
      { id: 'M01-intake', en: 'Omni-Channel Intake', bn: 'অমনি-চ্যানেল ইনটেক', t: 'c' },
      { id: 'M01-channels', en: 'Channel Performance', bn: 'চ্যানেল পারফরম্যান্স', t: 'r' },
      { id: 'M01-hotline', en: 'Hotline 16743 Queue', bn: 'হটলাইন ১৬৭৪৩ কিউ', t: 'g' }
    ]},
    { en: 'Order Lifecycle', screens: [
      { id: 'M01-order', en: 'Service Order Record', bn: 'সার্ভিস অর্ডার নথি', t: 'f' },
      { id: 'M01-types', en: 'Order Types (12 Streams)', bn: 'অর্ডার ক্যাটাগরি', t: 'g' },
      { id: 'M01-wip', en: 'WIP & Ageing Analysis', bn: 'চলমান কাজ ও এজিং', t: 'r' },
      { id: 'M01-holds', en: 'Hold Management', bn: 'হোল্ড ব্যবস্থাপনা', t: 'g' },
      { id: 'M01-rework', en: 'Rework Detection', bn: 'রিওয়ার্ক শনাক্তকরণ', t: 'g' }
    ]},
    { en: 'Diagnosis & Estimates', screens: [
      { id: 'M01-templates', en: 'Diagnostic Templates', bn: 'ডায়াগনস্টিক টেমপ্লেট', t: 'g' },
      { id: 'M01-fault', en: 'Fault & Symptom Coding', bn: 'ত্রুটি ও লক্ষণ কোডিং', t: 'g' },
      { id: 'M01-estimates', en: 'Estimates & Approvals', bn: 'অনুমান ও অনুমোদন', t: 'g' },
      { id: 'M01-thresholds', en: 'Approval Thresholds', bn: 'অনুমোদন সীমা', t: 'g' }
    ]},
    { en: 'Entitlement & SLA', screens: [
      { id: 'M01-entitle', en: 'Entitlement Evaluation', bn: 'সুবিধা ও ওয়ারেন্টি যাচাই', t: 'g' },
      { id: 'M01-sla', en: 'SLA Policies & Clocks', bn: 'এসএলএ পলিসি ও কাউন্টডাউন', t: 'g' },
      { id: 'M01-esc', en: 'Escalation Rules', bn: 'এসকেলেশন রুলস', t: 'g' },
      { id: 'M01-sla-rep', en: 'SLA Compliance Report', bn: 'এসএলএ সম্মতি রিপোর্ট', t: 'r' }
    ]},
    { en: 'Quality & Release', screens: [
      { id: 'M01-qc', en: 'QC Checkpoints & Inspection', bn: 'কিউসি পরিদর্শন', t: 'g' },
      { id: 'M01-reports', en: 'Service Reports & Proof', bn: 'সার্ভিস রিপোর্ট ও প্রমাণক', t: 'g' },
      { id: 'M01-rwty', en: 'Repair Warranty Issuance', bn: 'মেরামত ওয়ারেন্টি সার্টিফিকেট', t: 'g' }
    ]}
  ],
  reports: [
    'Daily Intake by Channel', 'WIP Ageing by Branch', 'SLA Compliance & Escalations',
    'Estimate Conversion Funnel', 'Rework & Repeat-Fault Analysis', 'Order Cycle-Time (TAT) Distribution', 'Uncollected Device Register'
  ],
  forms: [
    'New Service Order (12 channels, 34 fields)', 'Diagnostic Estimate Request', 'Hold / Release Reason', 'QC Checklist Inspection'
  ],
  cross: [
    'M02 Field Dispatch Handoff', 'M31 Workshop Routing', 'M09 Brand Warranty Check', 'M20 Mushak 6.3 Invoicing', 'M17 Device History'
  ],
  freg: {
    src: 128,
    sub: [
      ['1', 'Omni-Channel Intake (12 channels)', 14],
      ['2', 'Lifecycle State Machine & Stepper', 9],
      ['3', 'Entitlement Evaluation & SLA Clock', 8],
      ['4', 'Complaint & Fault Taxonomy Coding', 10],
      ['5', 'Diagnostic Templates & Benchmarks', 7],
      ['6', 'Estimate & Customer Approval Loop', 12],
      ['7', 'Assignment & Field Dispatch Handoff', 6],
      ['8', 'SLA Policy, Clock & Escalations', 13],
      ['9', 'Customer Hold & Release Management', 5],
      ['10', 'QC Checkpoints & Rework Detection', 11],
      ['11', 'Service Reports & Repair Warranty', 12],
      ['12', 'Operations Boards & WIP Analysis', 11],
      ['13', 'API & Domain Event Broadcasting', 10]
    ]
  }
};

/* In-workspace data screens. so_list/so_board/so_intake are the bespoke
 * order surfaces (/p03/orders/list scopes + /p03/stats); model_list uses the
 * generic whitelisted reader (/p03/model/records + /p03/model/action);
 * table_report calls the module's REPORTS (/p03/model/report). */
export const SCREENS = {
  'M01-board': { kind: 'so_board' },
  'M01-all': { kind: 'so_list', scope: 'all' },
  'M01-intake': { kind: 'so_intake' },
  'M01-channels': { kind: 'table_report', module: 'M01', report: 'channel_intake', period: true },
  'M01-hotline': { kind: 'model_list', model: 'fix.token.queue', create: false,
    cols: ['token_display', 'counter_number', 'service_type', 'customer_id', 'state', 'create_date'],
    stateField: 'state' },
  'M01-order': { kind: 'so_list', scope: 'all' },
  'M01-types': { kind: 'table_report', module: 'M01', report: 'type_matrix', period: false },
  'M01-wip': { kind: 'so_list', scope: 'wip' },
  'M01-holds': { kind: 'so_list', scope: 'holds' },
  'M01-rework': { kind: 'so_list', scope: 'rework' },
  'M01-templates': { kind: 'model_list', model: 'fix.diagnostic.node', create: false,
    cols: ['code', 'name', 'parent_id', 'is_terminal', 'fault_code', 'recommended_action'] },
  'M01-fault': { kind: 'model_list', model: 'fix.fault.code', create: false,
    cols: ['code', 'name', 'category', 'default_severity', 'active'] },
  'M01-estimates': { kind: 'model_list', model: 'fix.estimate',
    cols: ['order_id', 'version', 'parts_total', 'labour_total', 'grand_total', 'state', 'customer_approval_ref', 'manager_approval_uid'],
    stateField: 'state' },
  'M01-thresholds': { kind: 'table_report', module: 'M01', report: 'approval_thresholds', period: false },
  'M01-entitle': { kind: 'model_list', model: 'fix.warranty', create: false,
    cols: ['device_id', 'warranty_type', 'status', 'start_date', 'end_date'],
    stateField: 'status' },
  'M01-sla': { kind: 'model_list', model: 'fix.sla.policy', create: false,
    cols: ['code', 'service_type', 'priority', 'response_hours', 'resolution_hours', 'active'] },
  'M01-esc': { kind: 'model_list', model: 'fix.sla.policy', create: false,
    cols: ['code', 'service_type', 'priority', 'resolution_hours', 'escalation_template_id', 'active'] },
  'M01-sla-rep': { kind: 'table_report', module: 'M01', report: 'sla_compliance', period: false },
  'M01-qc': { kind: 'model_list', model: 'fix.qc.checklist',
    cols: ['order_id', 'inspector_id', 'state', 'all_passed', 'checked_at'],
    stateField: 'state' },
  'M01-reports': { kind: 'model_list', model: 'fix.device.history', create: false,
    cols: ['event_type', 'description', 'device_id', 'service_order_id', 'create_date'],
    domain: [['event_type', 'in', ['service_order', 'qc', 'warranty', 'repair']]] },
  'M01-rwty': { kind: 'so_list', scope: 'rwty' }
};

/* built-in report chips -> the screen that shows that report */
export const REPORT_ROUTES = {
  "M01:Daily Intake by Channel": "M01-channels",
  "M01:WIP Ageing by Branch": "M01-wip",
  "M01:SLA Compliance & Escalations": "M01-sla-rep",
  "M01:Estimate Conversion Funnel": "M01-estimates",
  "M01:Rework & Repeat-Fault Analysis": "M01-rework",
  "M01:Order Cycle-Time (TAT) Distribution": "M01-wip",
  "M01:Uncollected Device Register": "M01-rwty"
};

/* data-entry form chips: M01's New Service Order opens the in-shell 5-tab
 * intake modal (openNewForm), not a stock Odoo form — the rest arrive with
 * their engines in later iterations and keep the honest toast. */
export const FORM_MODELS = {};

/* the module's "+ New" surface: no entry — the workspace's bespoke service
 * order intake modal stays the default for this module. */
export const CREATE = {};
