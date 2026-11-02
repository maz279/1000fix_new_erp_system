/** @odoo-module **/
/* A07 · Assets & Facilities — M48 IoT Telemetry & Predictive (v2 rebuild).
 * Registry-faithful: 4 groups / 10 screens / 4 reports / 3 forms / freg 51.
 * Devices, telemetry rows, alerts and predictions existed; streams, adapters,
 * threshold rules, downsampling, prescriptive actions and consent are new. */

export const MODULE = {
  area: 'A07', code: 'M48', en: 'IoT Telemetry & Predictive', title: 'M48 · IoT Telemetry & Predictive',
  bn: 'আইওটি ও পূর্বাভাস', icon: '📡',
  desc: 'Stream registry and protocol adapters, pipeline observability, threshold alerting and lifecycle, asset health scoring, failure prediction, remaining useful life, prescriptive routing, and telemetry consent.',
  kpis: [
    { l: 'Streams Ingesting', m: 'streams_ingesting' },
    { l: 'Ingest Rate /hr', m: 'ingest_rate_per_hour' },
    { l: 'Open Alerts', m: 'open_alerts' },
    { l: 'Prediction Precision', m: 'prediction_precision', suffix: '%' },
    { l: 'Prescriptive Actions', m: 'prescriptive_actions' },
    { l: 'Retention Compression', m: 'retention_compression', suffix: '%' }
  ],
  groups: [
    { en: 'Record Coverage', screens: [
      { id: 'M48-iot-device', en: "Iot Device", bn: "Iot Device", t: 'g' }
    ]},
    { en: 'Ingestion', screens: [
      { id: 'M48-streams', en: 'Stream Registry', bn: 'স্ট্রিম রেজিস্টার', t: 'g' },
      { id: 'M48-adapters', en: 'Protocol Adapters', bn: 'প্রোটোকল অ্যাডাপ্টার', t: 'g' },
      { id: 'M48-health', en: 'Pipeline Observability', bn: 'পাইপলাইন', t: 'r' }
    ]},
    { en: 'Alerting', screens: [
      { id: 'M48-alerts', en: 'Threshold Alerts', bn: 'থ্রেশহোল্ড অ্যালার্ট', t: 'g' },
      { id: 'M48-lifecycle', en: 'Alert Lifecycle', bn: 'অ্যালার্ট জীবনচক্র', t: 'g' }
    ]},
    { en: 'Intelligence', screens: [
      { id: 'M48-scores', en: 'Asset Health Scoring', bn: 'অ্যাসেট স্বাস্থ্য', t: 'r' },
      { id: 'M48-failure', en: 'Failure Prediction', bn: 'ব্যর্থতা পূর্বাভাস', t: 'g' },
      { id: 'M48-rul', en: 'RUL Estimation', bn: 'অবশিষ্ট আয়ু', t: 'r' },
      { id: 'M48-routing', en: 'Prescriptive Routing', bn: 'নির্দেশনামূলক রুটিং', t: 'g' }
    ]},
    { en: 'Governance', screens: [
      { id: 'M48-consent', en: 'Consent & Access Control', bn: 'সম্মতি ও নিয়ন্ত্রণ', t: 'g' }
    ]}
  ],
  reports: ['Telemetry Coverage', 'Alert Storm Analysis', 'Prediction Outcome Tracking', 'Stream Quality Report'],
  forms: ['Stream Binding', 'Alert Rule', 'Downsampling Policy'],
  cross: ['M17 asset binding', 'M26 prediction models', 'M05 MSP monitoring', 'M01 prescriptive work orders'],
  freg: { src: 51, sub: [
    ['1', 'Stream Registry & Onboarding', 8], ['2', 'Protocol Adapters', 7],
    ['3', 'Ingestion & Storage', 9], ['4', 'Threshold Alerting', 8],
    ['5', 'Health Scoring', 6], ['6', 'Failure Prediction', 7],
    ['7', 'Prescriptive Routing', 6]
  ] }
};

export const SCREENS = {
  'M48-streams': { kind: 'model_list', model: 'fix.iot.stream', stateField: 'state',
    cols: ['name', 'device_id', 'equipment_id', 'metric', 'unit', 'sample_interval_sec', 'adapter_id', 'last_seen', 'state'],
    actions: [
      { m: 'action_activate', l: 'Activate Stream' },
      { m: 'action_suspend', l: 'Suspend Stream' }
    ] },
  'M48-adapters': { kind: 'model_list', model: 'fix.iot.adapter', stateField: 'state',
    cols: ['name', 'protocol', 'endpoint', 'auth_mode', 'state'],
    actions: [
      { m: 'action_enable', l: 'Enable Adapter' },
      { m: 'action_disable', l: 'Disable Adapter' }
    ] },
  'M48-health': { kind: 'table_report', module: 'M48', report: 'pipeline_health', title: 'Pipeline Observability', period: false },
  'M48-alerts': { kind: 'model_list', model: 'fix.iot.rule', stateField: 'state',
    cols: ['name', 'stream_id', 'operator', 'threshold', 'severity', 'duration_min', 'cooldown_min', 'state'],
    actions: [
      { m: 'action_pause', l: 'Pause Rule' },
      { m: 'action_activate', l: 'Activate Rule' }
    ] },
  'M48-lifecycle': { kind: 'model_list', model: 'fix.iot.alert', stateField: 'state', create: false,
    cols: ['name', 'device_id', 'severity', 'message', 'acked_on', 'resolved_on', 'state'],
    actions: [
      { m: 'action_ack', l: 'Acknowledge' },
      { m: 'action_resolve', l: 'Resolve' }
    ] },
  'M48-scores': { kind: 'table_report', module: 'M48', report: 'asset_health', title: 'Asset Health Scoring', period: false },
  'M48-failure': { kind: 'model_list', model: 'fix.predictive.maintenance',
    cols: ['name', 'equipment_id', 'prediction', 'confidence', 'estimated_days_to_failure', 'model_name', 'outcome', 'work_order_created'],
    actions: [{ m: 'action_create_preventive_wo', l: 'Create Preventive WO' }] },
  'M48-rul': { kind: 'table_report', module: 'M48', report: 'rul_estimation', title: 'RUL Estimation', period: false },
  'M48-routing': { kind: 'model_list', model: 'fix.iot.action', stateField: 'state',
    cols: ['name', 'equipment_id', 'action_type', 'priority', 'technician_id', 'scheduled_on', 'state'],
    actions: [
      { m: 'action_approve', l: 'Approve Action' },
      { m: 'action_dispatch', l: 'Dispatch' },
      { m: 'action_done', l: 'Complete' }
    ] },
  'M48-consent': { kind: 'model_list', model: 'fix.iot.consent', stateField: 'state',
    cols: ['name', 'subject_type', 'device_id', 'purpose', 'granted_on', 'valid_to', 'state'],
    actions: [{ m: 'action_revoke', l: 'Revoke Consent' }] },

  /* Report chips -> their own computed pack */
  'M48-rpt-coverage': { kind: 'table_report', module: 'M48', report: 'telemetry_coverage', title: 'Telemetry Coverage', period: false },
  'M48-rpt-storm': { kind: 'table_report', module: 'M48', report: 'alert_storm', title: 'Alert Storm Analysis', period: false },
  'M48-rpt-outcomes': { kind: 'table_report', module: 'M48', report: 'prediction_outcomes', title: 'Prediction Outcome Tracking', period: false },
  'M48-rpt-quality': { kind: 'table_report', module: 'M48', report: 'stream_quality', title: 'Stream Quality Report', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M48-form-stream': {
    kind: 'model_form',
    model: 'fix.iot.stream',
    title: 'Stream Binding',
    back: 'M48-streams',
    status: { field: 'state', labels: { draft: 'Draft', active: 'Active', suspended: 'Suspended' } },
    sections: [
      { title: 'Stream', note: 'A stream binds one device metric to a protocol adapter. The sample interval is the ingest expectation used by Telemetry Coverage, and it must be positive.',
        fields: [
          { name: 'name', required: true, label: 'Stream Reference' },
          { name: 'device_id', required: true, label: 'Device' },
          { name: 'adapter_id', label: 'Protocol Adapter' },
          { name: 'metric', required: true, label: 'Metric' },
          { name: 'unit', label: 'Unit' },
          { name: 'sample_interval_sec', required: true, label: 'Sample Interval (s)' },
          { name: 'retention_days', required: true, label: 'Raw Retention (days)' },
          { name: 'state', required: true, label: 'State' }
        ] }
    ]
  },

  'M48-form-rule': {
    kind: 'model_form',
    model: 'fix.iot.rule',
    title: 'Alert Rule',
    back: 'M48-alerts',
    status: { field: 'state', labels: { active: 'Active', paused: 'Paused' } },
    sections: [
      { title: 'Threshold Rule', note: 'A reading that compares true against the threshold raises an alert at the rule severity. Ingest evaluates only active rules.',
        fields: [
          { name: 'name', required: true, label: 'Rule Reference' },
          { name: 'stream_id', required: true, label: 'Stream' },
          { name: 'operator', required: true, label: 'Operator' },
          { name: 'threshold', required: true, label: 'Threshold' },
          { name: 'severity', required: true, label: 'Severity' },
          { name: 'duration_min', label: 'Sustained For (minutes)' },
          { name: 'cooldown_min', label: 'Cooldown (minutes)' },
          { name: 'state', required: true, label: 'State' }
        ] }
    ]
  },

  'M48-form-downsample': {
    kind: 'model_form',
    model: 'fix.iot.downsample',
    title: 'Downsampling Policy',
    back: 'M48-streams',
    status: { field: 'state', labels: { draft: 'Draft', active: 'Active' } },
    sections: [
      { title: 'Downsampling', note: 'The target interval cannot be shorter than the raw interval (database CHECK). Compression % feeds the Retention Compression KPI.',
        fields: [
          { name: 'name', required: true, label: 'Policy Reference' },
          { name: 'stream_id', required: true, label: 'Stream' },
          { name: 'raw_interval_sec', required: true, label: 'Raw Interval (s)' },
          { name: 'target_interval_sec', required: true, label: 'Target Interval (s)' },
          { name: 'aggregation', required: true, label: 'Aggregation' },
          { name: 'retention_days', label: 'Compressed Retention (days)' },
          { name: 'compression_pct', label: 'Compression %' },
          { name: 'state', required: true, label: 'State' }
        ] }
    ]
  },

  'M48-form-adapter': {
    kind: 'model_form',
    model: 'fix.iot.adapter',
    title: 'Protocol Adapter',
    back: 'M48-adapters',
    status: { field: 'state', labels: { enabled: 'Enabled', disabled: 'Disabled' } },
    sections: [
      { title: 'Adapter', note: 'The endpoint and auth mode are recorded configuration; no live broker connection is claimed by this screen.',
        fields: [
          { name: 'name', required: true, label: 'Adapter Name' },
          { name: 'protocol', required: true, label: 'Protocol' },
          { name: 'endpoint', label: 'Endpoint' },
          { name: 'auth_mode', required: true, label: 'Authentication' },
          { name: 'state', required: true, label: 'State' }
        ] }
    ]
  },

  'M48-form-action': {
    kind: 'model_form',
    model: 'fix.iot.action',
    title: 'Prescriptive Action',
    back: 'M48-routing',
    status: { field: 'state', labels: {
      proposed: 'Proposed', approved: 'Approved', dispatched: 'Dispatched',
      done: 'Done', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Action', note: 'Proposed → approved → dispatched → done; each transition is refused out of order.',
        fields: [
          { name: 'name', required: true, label: 'Action Reference' },
          { name: 'prediction_id', required: true, label: 'Prediction' },
          { name: 'action_type', required: true, label: 'Action Type' },
          { name: 'priority', required: true, label: 'Priority' },
          { name: 'technician_id', label: 'Technician' },
          { name: 'scheduled_on', required: true, label: 'Scheduled On' },
          { name: 'state', required: true, label: 'State' },
          { name: 'notes', label: 'Notes' }
        ] }
    ]
  },

  'M48-form-consent': {
    kind: 'model_form',
    model: 'fix.iot.consent',
    title: 'Telemetry Consent',
    back: 'M48-consent',
    status: { field: 'state', labels: { active: 'Active', revoked: 'Revoked' } },
    sections: [
      { title: 'Consent', note: 'A consent is scoped to a device, site or customer and a purpose; revoking is final for the record.',
        fields: [
          { name: 'name', required: true, label: 'Consent Reference' },
          { name: 'subject_type', required: true, label: 'Subject Type' },
          { name: 'device_id', label: 'Device' },
          { name: 'site_id', label: 'Site' },
          { name: 'partner_id', label: 'Customer' },
          { name: 'purpose', required: true, label: 'Purpose' },
          { name: 'granted_on', required: true, label: 'Granted On' },
          { name: 'valid_to', label: 'Valid To' },
          { name: 'state', required: true, label: 'State' },
          { name: 'notes', label: 'Notes' }
        ] }
    ]
  },

  'M48-form-prediction': {
    kind: 'model_form',
    model: 'fix.predictive.maintenance',
    title: 'Failure Prediction',
    back: 'M48-failure',
    sections: [
      { title: 'Prediction', note: 'Confidence is 0–1; days-to-failure 0 means imminent. Only a failure prediction can create a preventive work order, once.',
        fields: [
          { name: 'name', required: true, label: 'Prediction Reference' },
          { name: 'equipment_id', required: true, label: 'Equipment' },
          { name: 'prediction', required: true, label: 'Prediction' },
          { name: 'confidence', label: 'Confidence (0-1)' },
          { name: 'estimated_days_to_failure', label: 'Days to Failure' },
          { name: 'model_name', label: 'Model' },
          { name: 'outcome', required: true, label: 'Verified Outcome' }
        ] }
    ]
  },

  /* ===== triage coverage screens ===== */
  'M48-iot-device': { kind: 'model_list', model: 'fix.iot.device',
    cols: ['name', 'company_id', 'operating_unit_id', 'device_id', 'device_type', 'equipment_id', 'site_id'] },

  'M48-form-iot-device': {
    kind: 'model_form',
    model: 'fix.iot.device',
    title: "Iot Device",
    back: 'M48-iot-device',
    sections: [
      { title: "Iot Device", note: "Opened from the module's own record set. Every field here is the model's real field; the workflow rules live on the model and are not bypassed by this form.",
        fields: [
          { name: 'name', required: true, label: "Name" },
          { name: 'company_id', required: true, label: "Company" },
          { name: 'device_id', required: true, label: "Device Identifier" },
          { name: 'device_type', required: true, label: "Device Type" },
          { name: 'operating_unit_id', label: "Operating Unit" },
          { name: 'equipment_id', label: "Equipment (M45)" },
          { name: 'site_id', label: "Site (M47)" }
        ] }
    ]
  },

};

export const REPORT_ROUTES = {
  'M48:Telemetry Coverage': 'M48-rpt-coverage',
  'M48:Alert Storm Analysis': 'M48-rpt-storm',
  'M48:Prediction Outcome Tracking': 'M48-rpt-outcomes',
  'M48:Stream Quality Report': 'M48-rpt-quality'
};

export const FORM_MODELS = {
  'M48:Stream Binding': 'fix.iot.stream',
  'M48:Alert Rule': 'fix.iot.rule',
  'M48:Downsampling Policy': 'fix.iot.downsample'
};

export const FORM_CHIPS = {
  'M48:Stream Binding': 'M48-form-stream',
  'M48:Alert Rule': 'M48-form-rule',
  'M48:Downsampling Policy': 'M48-form-downsample',
  'M48:__by_model__': {
    'fix.iot.device': 'M48-form-iot-device',
    'fix.iot.stream': 'M48-form-stream',
    'fix.iot.rule': 'M48-form-rule',
    'fix.iot.downsample': 'M48-form-downsample',
    'fix.iot.adapter': 'M48-form-adapter',
    'fix.iot.action': 'M48-form-action',
    'fix.iot.consent': 'M48-form-consent',
    'fix.predictive.maintenance': 'M48-form-prediction'
  },
  'M48:__by_screen__': {
    'M48-iot-device': 'M48-form-iot-device',
    'M48-streams': 'M48-form-stream',
    'M48-adapters': 'M48-form-adapter',
    'M48-alerts': 'M48-form-rule',
    'M48-routing': 'M48-form-action',
    'M48-consent': 'M48-form-consent',
    'M48-failure': 'M48-form-prediction'
  }
};

export const CREATE = {
  M48: { screen: 'M48-form-stream', model: 'fix.iot.stream', label: 'Stream' }
};
