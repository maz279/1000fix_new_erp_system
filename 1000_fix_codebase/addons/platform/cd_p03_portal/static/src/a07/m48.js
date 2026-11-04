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
      { id: 'M48-health', en: 'Pipeline Observability', bn: 'পাইপলাইন', t: 'r' },
      { id: 'M48-gaps', en: 'Telemetry Gaps', bn: 'টেলিমেট্রি বিরতি', t: 'g' }
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
      { id: 'M48-consent', en: 'Consent & Access Control', bn: 'সম্মতি ও নিয়ন্ত্রণ', t: 'g' },
      { id: 'M48-downsample', en: 'Downsampling Policies', bn: 'ডাউনস্যাম্পলিং নীতি', t: 'g' },
      { id: 'M48-retention', en: 'Retention Changes', bn: 'সংরক্ষণ পরিবর্তন', t: 'g' }
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
    cols: ['name', 'device_id', 'equipment_id', 'metric', 'unit', 'sample_interval_sec', 'retention_days', 'consent_policy', 'adapter_id', 'last_seen', 'state'],
    actions: [
      { m: 'action_activate', l: 'Activate Stream' },
      { m: 'action_suspend', l: 'Suspend Stream' }
    ] },
  'M48-adapters': { kind: 'model_list', model: 'fix.iot.adapter', stateField: 'state',
    cols: ['name', 'protocol', 'endpoint', 'auth_mode', 'credential_ref', 'disabled_by', 'disabled_on', 'state'],
    actions: [
      /* A07 P1: any internal user may disable (it only stops collection);
       * enabling needs the IoT Administrator and a credential reference. */
      { m: 'action_enable', l: 'Enable Adapter (IoT Administrator)' },
      { m: 'action_disable', l: 'Disable Adapter', ask: 'Why disable this adapter?', kwarg: 'reason' }
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
    cols: ['name', 'device_id', 'rule_id', 'severity', 'message', 'trigger_value', 'occurrence_count', 'last_occurrence_on', 'acked_by', 'resolved_by', 'state'],
    actions: [
      { m: 'action_ack', l: 'Acknowledge' },
      { m: 'action_resolve', l: 'Resolve', ask: 'How was the alert resolved?', kwarg: 'resolution_note' }
    ] },
  'M48-scores': { kind: 'table_report', module: 'M48', report: 'asset_health', title: 'Asset Health Scoring', period: false },
  'M48-failure': { kind: 'model_list', model: 'fix.predictive.maintenance',
    cols: ['name', 'equipment_id', 'prediction', 'confidence', 'estimated_days_to_failure', 'model_name', 'model_published', 'outcome', 'outcome_action_id', 'work_order_created'],
    actions: [{ m: 'action_create_preventive_wo', l: 'Create Preventive WO' }] },
  'M48-rul': { kind: 'table_report', module: 'M48', report: 'rul_estimation', title: 'RUL Estimation', period: false },
  'M48-routing': { kind: 'model_list', model: 'fix.iot.action', stateField: 'state',
    cols: ['name', 'equipment_id', 'action_type', 'priority', 'technician_id', 'scheduled_on', 'approval_state', 'approved_by', 'outcome', 'state'],
    actions: [
      /* A07 P0 recipe (M48-2): an approver other than the proposer decides
       * from the M63 inbox; this only asks. A07 P1: the Operations Director
       * (M47 role) decides; the DOFA Tier 2 stand-in until it is installed.
       * Dispatch and completion are the IoT Operator's. */
      { m: 'action_request_approval', l: 'Request Approval (Operations Director)', ask: 'Why is this intervention needed?', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Approval Request' },
      { m: 'action_dispatch', l: 'Dispatch' },
      { m: 'action_done_confirmed', l: 'Complete: Failure Confirmed', ask: 'What did the intervention find?', kwarg: 'note' },
      { m: 'action_done_not_confirmed', l: 'Complete: Failure Not Confirmed', ask: 'What did the intervention find?', kwarg: 'note' }
    ] },
  'M48-consent': { kind: 'model_list', model: 'fix.iot.consent', stateField: 'state',
    cols: ['name', 'subject_type', 'device_id', 'site_id', 'partner_id', 'purpose', 'signal_groups_permitted', 'granted_on', 'valid_to', 'verification', 'revocation_treatment', 'treatment_state', 'revoked_at', 'state'],
    actions: [
      /* A07 P1: a Consent Officer who did not record the consent verifies it;
       * anyone may record a withdrawal (it only stops collection). */
      { m: 'action_verify', l: 'Verify Consent (Consent Officer)' },
      { m: 'action_revoke', l: 'Revoke Consent', ask: 'Withdrawal evidence (letter, call or ticket reference)', kwarg: 'evidence_ref' },
      { m: 'action_record_treatment', l: 'Record Anonymisation Done', ask: 'How were the readings anonymised?', kwarg: 'note' }
    ] },
  'M48-downsample': { kind: 'model_list', model: 'fix.iot.downsample', stateField: 'state',
    cols: ['name', 'stream_id', 'raw_interval_sec', 'target_interval_sec', 'aggregation', 'retention_days', 'compression_pct', 'measured_compression_pct', 'rollup_points', 'last_rollup_on', 'state'],
    actions: [
      /* A07 P1 (BRU-IOT-06): activation is a retention change the CTO approves. */
      { m: 'action_activate', l: 'Request Activation (CTO approval)' }
    ] },
  'M48-retention': { kind: 'model_list', model: 'fix.iot.retention.change', stateField: 'state',
    cols: ['name', 'change_type', 'stream_id', 'downsample_id', 'current_days', 'proposed_days', 'reason', 'requested_by', 'approval_state', 'applied_by', 'state'],
    actions: [
      { m: 'action_request_approval', l: 'Request CTO Approval', ask: 'Note for the approver', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Request' }
    ] },
  'M48-gaps': { kind: 'model_list', model: 'fix.iot.gap', stateField: 'state', create: false,
    cols: ['name', 'stream_id', 'device_id', 'gap_from', 'gap_to', 'detected_at', 'cause', 'had_reading', 'points_expected', 'state'] },

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
      { title: 'Stream', note: 'A stream binds one device metric to a protocol adapter. It activates only when its device is bound to M45 equipment or an M47 site. The sample interval is the ingest expectation used by Telemetry Coverage and the liveness check (silent after three intervals with no reading), and it must be positive. Raw retention is set at creation; afterwards it changes only through a Retention Change the CTO approves. Consent Always Required tightens the consent check; relaxing it back needs the Consent Officer.',
        fields: [
          { name: 'name', required: true, label: 'Stream Reference' },
          { name: 'device_id', required: true, label: 'Device' },
          { name: 'adapter_id', label: 'Protocol Adapter' },
          { name: 'metric', required: true, label: 'Metric' },
          { name: 'unit', label: 'Unit' },
          { name: 'sample_interval_sec', required: true, label: 'Sample Interval (s)' },
          { name: 'retention_days', required: true, label: 'Raw Retention (days)' },
          { name: 'consent_policy', required: true, label: 'Consent Policy' },
          { name: 'state', label: 'State', readonly: true },
          { name: 'activated_on', label: 'Activated On', readonly: true }
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
      { title: 'Threshold Rule', note: 'A reading that compares true against the threshold raises an alert at the rule severity. Ingest evaluates only active rules. While the rule\'s last alert is open, further breaches are counted on it; after an alert, none is raised again within the cooldown. Sustained For holds an alert back until the breach has lasted that long only where the dwell switch is on. Stream, operator and threshold are set when the rule is created; afterwards the threshold changes only through Change Threshold, and the stream and operator not at all.',
        fields: [
          { name: 'name', required: true, label: 'Rule Reference' },
          { name: 'stream_id', required: true, label: 'Stream' },
          { name: 'operator', required: true, label: 'Operator' },
          { name: 'threshold', required: true, label: 'Threshold' },
          { name: 'severity', required: true, label: 'Severity' },
          { name: 'duration_min', label: 'Sustained For (minutes)' },
          { name: 'cooldown_min', label: 'Cooldown (minutes)' },
          { name: 'state', label: 'State', readonly: true },
          { name: 'last_alert_on', label: 'Last Alert Raised', readonly: true },
          { name: 'cooldown_suppressed', label: 'Breaches Held by Cooldown', readonly: true }
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
      { title: 'Downsampling', note: 'The target interval cannot be shorter than the raw interval (database CHECK). A draft policy is edited freely; Request Activation sends it to the CTO, and an active policy changes only through a Retention Change. Design Reduction is the planning figure 1 - raw / target. The Retention Compression KPI uses only the Measured Compression, which the daily retention job computes from the aggregates it actually wrote.',
        fields: [
          { name: 'name', required: true, label: 'Policy Reference' },
          { name: 'stream_id', required: true, label: 'Stream' },
          { name: 'raw_interval_sec', required: true, label: 'Raw Interval (s)' },
          { name: 'target_interval_sec', required: true, label: 'Target Interval (s)' },
          { name: 'aggregation', required: true, label: 'Aggregation' },
          { name: 'retention_days', label: 'Compressed Retention (days)' },
          { name: 'compression_pct', label: 'Design Reduction %', readonly: true },
          { name: 'state', label: 'State', readonly: true }
        ] },
      { title: 'Measured', fields: [
          { name: 'activated_on', label: 'Activated On', readonly: true },
          { name: 'rolled_until', label: 'Aggregated Up To', readonly: true },
          { name: 'raw_points_rolled', label: 'Raw Readings Aggregated', readonly: true },
          { name: 'rollup_points', label: 'Aggregates Written', readonly: true },
          { name: 'measured_compression_pct', label: 'Measured Compression %', readonly: true },
          { name: 'last_rollup_on', label: 'Last Aggregation Run', readonly: true }
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
      { title: 'Adapter', note: 'The endpoint and auth mode are recorded configuration; no live broker connection is claimed by this screen. An enabled adapter must authenticate (Bearer Token or Mutual TLS), and ingest refuses readings through a disabled or unauthenticated one. Never type a password into the endpoint: record where the credential is kept in Credential Reference.',
        fields: [
          { name: 'name', required: true, label: 'Adapter Name' },
          { name: 'protocol', required: true, label: 'Protocol' },
          { name: 'endpoint', label: 'Endpoint' },
          { name: 'auth_mode', required: true, label: 'Authentication' },
          { name: 'credential_ref', label: 'Credential Reference' },
          { name: 'credential_rotated_on', label: 'Credential Rotated On' },
          { name: 'state', label: 'State', readonly: true },
          { name: 'disabled_by', label: 'Disabled By', readonly: true },
          { name: 'disabled_on', label: 'Disabled On', readonly: true },
          { name: 'disable_reason', label: 'Disable Reason', readonly: true }
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
      { title: 'Action', note: 'Proposed → approved → dispatched → done; the state changes only through the actions. Approval is requested here and decided from the approval inbox by the Operations Director (DOFA Tier 2 until that role is installed), never the proposer, never on a healthy prediction or one whose model is not a published M26 model. Changing the action type, priority or prediction after approval withdraws it. Dispatch (IoT Operator) needs a technician and hands the work order to M01/M02; completion needs the outcome evidence, is recorded by someone other than the technician, and records whether the failure was confirmed.',
        fields: [
          { name: 'name', required: true, label: 'Action Reference' },
          { name: 'prediction_id', required: true, label: 'Prediction' },
          { name: 'action_type', required: true, label: 'Action Type' },
          { name: 'priority', required: true, label: 'Priority' },
          { name: 'technician_id', label: 'Technician' },
          { name: 'scheduled_on', required: true, label: 'Scheduled On' },
          { name: 'state', label: 'State', readonly: true },
          { name: 'notes', label: 'Notes' },
          { name: 'outcome_evidence_ref', label: 'Outcome Evidence' }
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
      { title: 'Consent', note: 'A consent must name its subject (the device, site or customer of its subject type) and cannot end before it is granted. Ingest checks it: an active, verified consent in date covers the device, for the signals it lists. A consent recorded by someone other than a Consent Officer grants nothing until an officer who did not record it verifies it against its evidence; changing a verified consent sends it back for verification. Revoke Consent records who and when, suspends the streams it covered that no other valid consent covers, and applies the treatment agreed at grant to the readings held. A revoked consent is never reactivated, and the state changes only through Revoke.',
        fields: [
          { name: 'name', required: true, label: 'Consent Reference' },
          { name: 'subject_type', required: true, label: 'Subject Type' },
          { name: 'device_id', label: 'Device' },
          { name: 'site_id', label: 'Site' },
          { name: 'partner_id', label: 'Customer' },
          { name: 'purpose', required: true, label: 'Purpose' },
          { name: 'granted_on', required: true, label: 'Granted On' },
          { name: 'valid_to', label: 'Valid To' },
          { name: 'signal_groups_permitted', label: 'Signals Permitted' },
          { name: 'granted_by', label: 'Granted By' },
          { name: 'disclosure_document_id', label: 'Disclosure Given' },
          { name: 'evidence_ref', label: 'Grant Evidence' },
          { name: 'revocation_treatment', required: true, label: 'Treatment on Revocation' },
          { name: 'state', label: 'State', readonly: true },
          { name: 'notes', label: 'Notes' }
        ] },
      { title: 'Verification & Withdrawal', fields: [
          { name: 'verification', label: 'Verification', readonly: true },
          { name: 'verified_by', label: 'Verified By', readonly: true },
          { name: 'verified_on', label: 'Verified On', readonly: true },
          { name: 'revoked_by', label: 'Revoked By', readonly: true },
          { name: 'revoked_at', label: 'Revoked At', readonly: true },
          { name: 'revocation_evidence_ref', label: 'Withdrawal Evidence', readonly: true },
          { name: 'treatment_state', label: 'Treatment', readonly: true },
          { name: 'treatment_note', label: 'Treatment Record', readonly: true },
          { name: 'readings_treated', label: 'Readings Treated', readonly: true }
        ] }
    ]
  },

  'M48-form-prediction': {
    kind: 'model_form',
    model: 'fix.predictive.maintenance',
    title: 'Failure Prediction',
    back: 'M48-failure',
    sections: [
      { title: 'Prediction', note: 'Confidence must be within 0–1 and days-to-failure cannot be negative (0 means imminent). Model is the code of a published M26 predictive-maintenance model; a prediction whose model is not published is recorded but never applied (no approved action, no work order). Only a failure prediction can create a preventive work order, once. The verified outcome is recorded by completing a prescriptive action, never typed.',
        fields: [
          { name: 'name', required: true, label: 'Prediction Reference' },
          { name: 'equipment_id', required: true, label: 'Equipment' },
          { name: 'prediction', required: true, label: 'Prediction' },
          { name: 'confidence', label: 'Confidence (0-1)' },
          { name: 'estimated_days_to_failure', label: 'Days to Failure' },
          { name: 'model_name', label: 'Model' },
          { name: 'model_published', label: 'Model Published (M26)', readonly: true },
          { name: 'feature_window_from', label: 'Feature Window From' },
          { name: 'feature_window_to', label: 'Feature Window To' },
          { name: 'outcome', label: 'Verified Outcome', readonly: true },
          { name: 'outcome_note', label: 'Outcome Note', readonly: true },
          { name: 'outcome_action_id', label: 'Outcome From Action', readonly: true },
          { name: 'outcome_recorded_by', label: 'Outcome Recorded By', readonly: true },
          { name: 'work_order_created', label: 'Work Order Created', readonly: true }
        ] }
    ]
  },

  'M48-form-retention': {
    kind: 'model_form',
    model: 'fix.iot.retention.change',
    title: 'Retention Change',
    back: 'M48-retention',
    status: { field: 'state', labels: { draft: 'Draft', requested: 'Awaiting CTO Approval', applied: 'Applied', rejected: 'Rejected' } },
    sections: [
      { title: 'Change', note: 'BRU-IOT-06: a stream\'s raw retention, a policy\'s compressed retention and a policy\'s activation change only with CTO approval. Name exactly one target. Request CTO Approval routes it to an IoT Manager who neither requested nor created it; the change applies when they approve it from the inbox, and its terms are frozen once requested.',
        fields: [
          { name: 'name', required: true, label: 'Change Reference' },
          { name: 'change_type', required: true, label: 'Change' },
          { name: 'stream_id', label: 'Stream (raw retention)' },
          { name: 'downsample_id', label: 'Downsampling Policy' },
          { name: 'proposed_days', label: 'Proposed Retention (days)' },
          { name: 'reason', required: true, label: 'Reason' },
          { name: 'current_days', label: 'Current Retention (days)', readonly: true },
          { name: 'state', label: 'State', readonly: true },
          { name: 'approval_state', label: 'Approval', readonly: true },
          { name: 'requested_by', label: 'Requested By', readonly: true },
          { name: 'applied_by', label: 'Approved By', readonly: true },
          { name: 'applied_on', label: 'Applied On', readonly: true }
        ] }
    ]
  },

  'M48-form-gap': {
    kind: 'model_form',
    model: 'fix.iot.gap',
    title: 'Telemetry Gap',
    back: 'M48-gaps',
    status: { field: 'state', labels: { open: 'Open', closed: 'Closed' } },
    sections: [
      { title: 'Gap', note: 'Recorded by the liveness check when a stream received no reading for three sample intervals (at least five minutes); closed when the next reading arrives. A silent stream is never shown as a zero. Gaps are platform records: nobody edits or deletes them.',
        fields: [
          { name: 'name', label: 'Gap Reference', readonly: true },
          { name: 'stream_id', label: 'Stream', readonly: true },
          { name: 'device_id', label: 'Device', readonly: true },
          { name: 'gap_from', label: 'Silent Since', readonly: true },
          { name: 'gap_to', label: 'Resumed At', readonly: true },
          { name: 'detected_at', label: 'Detected At', readonly: true },
          { name: 'cause', label: 'Cause', readonly: true },
          { name: 'had_reading', label: 'Stream Had Readings', readonly: true },
          { name: 'points_expected', label: 'Readings Missed', readonly: true },
          { name: 'state', label: 'State', readonly: true }
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
    'fix.predictive.maintenance': 'M48-form-prediction',
    'fix.iot.retention.change': 'M48-form-retention',
    'fix.iot.gap': 'M48-form-gap'
  },
  'M48:__by_screen__': {
    'M48-iot-device': 'M48-form-iot-device',
    'M48-streams': 'M48-form-stream',
    'M48-adapters': 'M48-form-adapter',
    'M48-alerts': 'M48-form-rule',
    'M48-routing': 'M48-form-action',
    'M48-consent': 'M48-form-consent',
    'M48-failure': 'M48-form-prediction',
    'M48-downsample': 'M48-form-downsample',
    'M48-retention': 'M48-form-retention',
    'M48-gaps': 'M48-form-gap'
  }
};

export const CREATE = {
  M48: { screen: 'M48-form-stream', model: 'fix.iot.stream', label: 'Stream' }
};
