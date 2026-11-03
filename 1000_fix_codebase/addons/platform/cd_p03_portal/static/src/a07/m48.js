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
    ['1', 'Stream Registry & Onboarding', 8, { model: 'fix.iot.stream', cols: ['name', 'device_id', 'metric', 'unit', 'state'], screens: ['M48-streams', 'M48-iot-device', 'M48-consent'] }],
    ['2', 'Protocol Adapters', 7, { model: 'fix.iot.adapter', cols: ['name', 'protocol', 'endpoint', 'auth_mode', 'state'], screens: ['M48-adapters'] }],
    ['3', 'Ingestion & Storage', 9, { model: 'fix.iot.device', cols: ['name', 'device_id', 'device_type', 'last_telemetry', 'status'], screens: ['M48-health', 'M48-iot-device'] }],
    ['4', 'Threshold Alerting', 8, { model: 'fix.iot.rule', cols: ['name', 'stream_id', 'operator', 'threshold', 'severity', 'state'], screens: ['M48-alerts', 'M48-lifecycle'] }],
    ['5', 'Health Scoring', 6, { model: 'fix.predictive.maintenance', cols: ['equipment_id', 'prediction', 'confidence', 'last_evaluated', 'model_name'], screens: ['M48-scores'] }],
    ['6', 'Failure Prediction', 7, { model: 'fix.predictive.maintenance', cols: ['name', 'equipment_id', 'prediction', 'estimated_days_to_failure', 'outcome'], screens: ['M48-failure', 'M48-rul'] }],
    ['7', 'Prescriptive Routing', 6, { model: 'fix.iot.action', cols: ['name', 'equipment_id', 'action_type', 'priority', 'technician_id', 'state'], screens: ['M48-routing'] }]
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
    cols: ['name', 'stream_id', 'operator', 'threshold', 'severity', 'duration_min', 'cooldown_min', 'suppression_kind', 'suppression_until', 'approval_state', 'state'],
    actions: [
      /* A07 P0 recipe (M48-3): pausing or loosening is a suppression with a
       * reason and an expiry, decided from the M63 inbox by someone other
       * than the requester and the rule's author. Tightening and resuming
       * apply at once. */
      { m: 'action_pause', l: 'Request Pause (approval)', ask: 'Why pause this rule? (set Suppressed Until on the rule first)', kwarg: 'reason' },
      { m: 'action_change_threshold', l: 'Change Threshold', ask: 'New threshold (tightening applies now; loosening needs the rule Suppression Reason and Suppressed Until, and approval)', kwarg: 'threshold' },
      { m: 'action_request_approval', l: 'Re-request Suppression Approval', ask: 'Note for the approver', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Suppression Request' },
      { m: 'action_activate', l: 'Resume Rule / Lift Suppression' }
    ] },
  'M48-lifecycle': { kind: 'model_list', model: 'fix.iot.alert', stateField: 'state', create: false,
    cols: ['name', 'device_id', 'severity', 'message', 'acked_on', 'acked_by', 'resolved_on', 'resolved_by', 'state'],
    actions: [
      { m: 'action_ack', l: 'Acknowledge' },
      { m: 'action_resolve', l: 'Resolve', ask: 'How was the alert resolved?', kwarg: 'resolution_note' }
    ] },
  'M48-scores': { kind: 'table_report', module: 'M48', report: 'asset_health', title: 'Asset Health Scoring', period: false },
  'M48-failure': { kind: 'model_list', model: 'fix.predictive.maintenance',
    cols: ['name', 'equipment_id', 'prediction', 'confidence', 'estimated_days_to_failure', 'model_name', 'outcome', 'outcome_action_id', 'work_order_created'],
    actions: [{ m: 'action_create_preventive_wo', l: 'Create Preventive WO' }] },
  'M48-rul': { kind: 'table_report', module: 'M48', report: 'rul_estimation', title: 'RUL Estimation', period: false },
  'M48-routing': { kind: 'model_list', model: 'fix.iot.action', stateField: 'state',
    cols: ['name', 'equipment_id', 'action_type', 'priority', 'technician_id', 'scheduled_on', 'approval_state', 'approved_by', 'outcome', 'state'],
    actions: [
      /* A07 P0 recipe (M48-2): a DOFA Tier 2 (operations manager) approver
       * other than the proposer decides from the M63 inbox; this only asks. */
      { m: 'action_request_approval', l: 'Request Approval (Tier 2)', ask: 'Why is this intervention needed?', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Approval Request' },
      { m: 'action_dispatch', l: 'Dispatch' },
      { m: 'action_done_confirmed', l: 'Complete: Failure Confirmed', ask: 'What did the intervention find?', kwarg: 'note' },
      { m: 'action_done_not_confirmed', l: 'Complete: Failure Not Confirmed', ask: 'What did the intervention find?', kwarg: 'note' }
    ] },
  'M48-consent': { kind: 'model_list', model: 'fix.iot.consent', stateField: 'state',
    cols: ['name', 'subject_type', 'device_id', 'site_id', 'partner_id', 'purpose', 'granted_on', 'valid_to', 'revoked_on', 'state'],
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
          { name: 'state', label: 'State', readonly: true }
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
      { title: 'Threshold Rule', note: 'A reading that compares true against the threshold raises an alert at the rule severity. Ingest evaluates only active rules. Stream, operator and threshold are set when the rule is created; afterwards the threshold changes only through Change Threshold, and the stream and operator not at all.',
        fields: [
          { name: 'name', required: true, label: 'Rule Reference' },
          { name: 'stream_id', required: true, label: 'Stream' },
          { name: 'operator', required: true, label: 'Operator' },
          { name: 'threshold', required: true, label: 'Threshold' },
          { name: 'severity', required: true, label: 'Severity' },
          { name: 'duration_min', label: 'Sustained For (minutes)' },
          { name: 'cooldown_min', label: 'Cooldown (minutes)' },
          { name: 'state', label: 'State', readonly: true }
        ] },
      { title: 'Suppression', note: 'Pausing a rule or loosening its threshold is a suppression: give a reason and an expiry here, then Request Pause or Change Threshold. An approver other than the requester and the rule author decides it from the approval inbox. It ends after Suppressed Until, when the rule alerts again at its earlier threshold.',
        fields: [
          { name: 'suppression_reason', label: 'Suppression Reason' },
          { name: 'suppression_until', label: 'Suppressed Until' },
          { name: 'suppression_kind', label: 'Suppression', readonly: true },
          { name: 'proposed_threshold', label: 'Proposed Threshold', readonly: true },
          { name: 'baseline_threshold', label: 'Threshold Before Suppression', readonly: true },
          { name: 'approval_state', label: 'Approval', readonly: true },
          { name: 'suppression_requested_by', label: 'Requested By', readonly: true },
          { name: 'suppressed_by', label: 'Approved By', readonly: true },
          { name: 'suppressed_on', label: 'Approved On', readonly: true }
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
          { name: 'state', label: 'State', readonly: true }
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
      { title: 'Action', note: 'Proposed → approved → dispatched → done; the state changes only through the actions. Approval is requested here and decided from the approval inbox by a Tier 2 approver other than the proposer, never on a healthy prediction. Changing the action type, priority or prediction after approval withdraws it. Dispatch needs a technician; completion records whether the failure was confirmed.',
        fields: [
          { name: 'name', required: true, label: 'Action Reference' },
          { name: 'prediction_id', required: true, label: 'Prediction' },
          { name: 'action_type', required: true, label: 'Action Type' },
          { name: 'priority', required: true, label: 'Priority' },
          { name: 'technician_id', label: 'Technician' },
          { name: 'scheduled_on', required: true, label: 'Scheduled On' },
          { name: 'state', label: 'State', readonly: true },
          { name: 'notes', label: 'Notes' }
        ] },
      { title: 'Approval & Outcome', fields: [
          { name: 'approval_state', label: 'Approval', readonly: true },
          { name: 'approved_by', label: 'Approved By', readonly: true },
          { name: 'approved_on', label: 'Approved On', readonly: true },
          { name: 'dispatched_on', label: 'Dispatched On', readonly: true },
          { name: 'completed_by', label: 'Completed By', readonly: true },
          { name: 'completed_on', label: 'Completed On', readonly: true },
          { name: 'outcome', label: 'Outcome', readonly: true },
          { name: 'outcome_note', label: 'Outcome Note', readonly: true }
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
      { title: 'Consent', note: 'A consent must name its subject (the device, site or customer of its subject type) and cannot end before it is granted. Ingest checks it: an active consent in date covers the device. Revoke Consent records who and when, and suspends the streams it covered that no other valid consent covers. A revoked consent is never reactivated, and the state changes only through Revoke.',
        fields: [
          { name: 'name', required: true, label: 'Consent Reference' },
          { name: 'subject_type', required: true, label: 'Subject Type' },
          { name: 'device_id', label: 'Device' },
          { name: 'site_id', label: 'Site' },
          { name: 'partner_id', label: 'Customer' },
          { name: 'purpose', required: true, label: 'Purpose' },
          { name: 'granted_on', required: true, label: 'Granted On' },
          { name: 'valid_to', label: 'Valid To' },
          { name: 'state', label: 'State', readonly: true },
          { name: 'revoked_by', label: 'Revoked By', readonly: true },
          { name: 'revoked_on', label: 'Revoked On', readonly: true },
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
      { title: 'Prediction', note: 'Confidence must be within 0–1 and days-to-failure cannot be negative (0 means imminent). Only a failure prediction can create a preventive work order, once. The verified outcome is recorded by completing a prescriptive action, never typed.',
        fields: [
          { name: 'name', required: true, label: 'Prediction Reference' },
          { name: 'equipment_id', required: true, label: 'Equipment' },
          { name: 'prediction', required: true, label: 'Prediction' },
          { name: 'confidence', label: 'Confidence (0-1)' },
          { name: 'estimated_days_to_failure', label: 'Days to Failure' },
          { name: 'model_name', label: 'Model' },
          { name: 'outcome', label: 'Verified Outcome', readonly: true },
          { name: 'outcome_note', label: 'Outcome Note', readonly: true },
          { name: 'outcome_action_id', label: 'Outcome From Action', readonly: true },
          { name: 'outcome_recorded_by', label: 'Outcome Recorded By', readonly: true },
          { name: 'work_order_created', label: 'Work Order Created', readonly: true }
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
          { name: 'site_id', label: "Site (M47)" },
          { name: 'partner_id', label: "Customer (data subject)" }
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
