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
      { id: 'M48-gaps', en: 'Telemetry Gaps', bn: 'টেলিমেট্রি বিরতি', t: 'g' },
      { id: 'M48-telemetry', en: 'Telemetry Readings', bn: 'টেলিমেট্রি রিডিং', t: 'g' },
      { id: 'M48-rollups', en: 'Telemetry Aggregates', bn: 'টেলিমেট্রি সমষ্টি', t: 'g' }
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
    { en: 'Alerts', screens: [
      { id: 'M48-asset-alerts', en: 'Alerts', bn: 'সতর্কতা', t: 'g' }
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
  'M48-asset-alerts': { kind: 'model_list', model: 'fix.asset.alert', stateField: 'state', create: false,
    note: 'What the scheduled checks found, addressed to the role that must act. Acknowledging says you have seen it; it does not fix the cause.',
    domain: [['module', '=', 'M48']],
    cols: ['name', 'record_label', 'role_group', 'no_holder', 'raise_count', 'last_raised_on', 'acknowledged_by_id', 'state'],
    actions: [{ m: 'action_acknowledge', l: 'Acknowledge' }] },
  'M48-streams': { kind: 'model_list', model: 'fix.iot.stream', stateField: 'state',
    cols: ['name', 'device_id', 'equipment_id', 'metric', 'unit', 'sample_interval_sec', 'retention_days', 'consent_policy', 'adapter_id', 'last_seen', 'state'],
    actions: [
      { m: 'action_activate', l: 'Activate Stream' },
      { m: 'action_suspend', l: 'Suspend Stream' },
      { m: 'action_set_consent_policy', l: 'Change Consent Policy (Consent Officer)', asks: [
        { label: 'New policy: type inherit (module default) or required (consent always required)', kwarg: 'policy' },
        { label: 'Why is the policy changing?', kwarg: 'reason' }
      ] }
    ] },
  'M48-adapters': { kind: 'model_list', model: 'fix.iot.adapter', stateField: 'state',
    cols: ['name', 'protocol', 'endpoint', 'auth_mode', 'credential_ref', 'key_set', 'key_rotated_on', 'disabled_by', 'disabled_on', 'state'],
    actions: [
      /* A07 P1: any internal user may disable (it only stops collection);
       * enabling needs the IoT Administrator, a credential reference and a key. */
      { m: 'action_rotate_key', l: 'Rotate Key (IoT Administrator)', ask: 'Paste a new key of at least 32 characters from your secret store, or leave this blank to have one generated. A generated key is shown only once.', kwarg: 'key' },
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
      { m: 'action_change_settings', l: 'Change Severity, Dwell or Cooldown', asks: [
        { label: 'Severity: minor or major (leave blank to keep it)', kwarg: 'severity' },
        { label: 'Sustained for, in minutes (leave blank to keep it)', kwarg: 'duration_min' },
        { label: 'Cooldown, in minutes (leave blank to keep it)', kwarg: 'cooldown_min' },
        { label: 'Reason (a lower severity or longer time needs approval, and Suppressed Until on the rule)', kwarg: 'reason' }
      ] },
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
    actions: [{ m: 'action_create_preventive_wo', l: 'Request Preventive Work Order' }] },
  'M48-rul': { kind: 'table_report', module: 'M48', report: 'rul_estimation', title: 'RUL Estimation', period: false },
  'M48-routing': { kind: 'model_list', model: 'fix.iot.action', stateField: 'state',
    cols: ['name', 'equipment_id', 'action_type', 'priority', 'technician_id', 'scheduled_on', 'approval_state', 'approved_by', 'spine_work_order_id', 'spine_service_order_id', 'outcome', 'revision_note', 'state'],
    actions: [
      /* A07 P0 recipe (M48-2): an approver other than the proposer decides
       * from the M63 inbox; this only asks. The Operations Director (M47 role)
       * decides; DOFA Tier 2 while nobody holds that role.
       * Dispatch and completion are the IoT Operator's. */
      { m: 'action_request_approval', l: 'Request Approval (Operations Director, or DOFA Tier 2 if none)', ask: 'Why is this intervention needed?', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Approval Request' },
      /* A07 P1 M48-12: approved terms are refused; this withdraws the approval. */
      { m: 'action_revise_terms', l: 'Revise Terms (withdraw approval)', ask: 'Why must the approved action change?', kwarg: 'reason' },
      { m: 'action_cancel', l: 'Cancel Action', ask: 'Why is this action cancelled?', kwarg: 'reason' },
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
      { m: 'action_record_treatment', l: 'Anonymise the Held Readings (Consent Officer)', ask: 'This cannot be undone: the readings lose their device and exact time, and location readings and aggregates are deleted. Note for the record: why, and under what authority?', kwarg: 'note' }
    ] },
  'M48-downsample': { kind: 'model_list', model: 'fix.iot.downsample', stateField: 'state',
    cols: ['name', 'stream_id', 'raw_interval_sec', 'target_interval_sec', 'aggregation', 'retention_days', 'compression_pct', 'measured_compression_pct', 'rollup_points', 'last_rollup_on', 'state'],
    actions: [
      /* A07 P1 (BRU-IOT-06): activation is a retention change the CTO approves. */
      { m: 'action_activate', l: 'Request Activation (CTO approval)' },
      { m: 'action_request_deactivation', l: 'Request Switch Off (CTO approval)', ask: 'Why should this policy stop?', kwarg: 'reason' }
    ] },
  'M48-retention': { kind: 'model_list', model: 'fix.iot.retention.change', stateField: 'state',
    cols: ['name', 'change_type', 'stream_id', 'downsample_id', 'current_days', 'proposed_days', 'reason', 'requested_by', 'approval_state', 'applied_by', 'state'],
    actions: [
      { m: 'action_request_approval', l: 'Request CTO Approval', ask: 'Note for the approver', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Request' }
    ] },
  'M48-gaps': { kind: 'model_list', model: 'fix.iot.gap', stateField: 'state', create: false,
    cols: ['name', 'stream_id', 'device_id', 'gap_from', 'gap_to', 'detected_at', 'cause', 'had_reading', 'points_expected', 'state'] },
  'M48-telemetry': { kind: 'model_list', model: 'fix.iot.telemetry', create: false,
    note: 'The readings as they arrived. Nobody types or edits them here. A reading with no device was anonymised after its consent was withdrawn.',
    cols: ['timestamp', 'device_id', 'metric', 'value', 'unit', 'anonymised'] },
  'M48-rollups': { kind: 'model_list', model: 'fix.iot.telemetry.rollup', create: false,
    note: 'What the daily retention job aggregated under each active downsampling policy. Nobody types or edits them here.',
    cols: ['stream_id', 'downsample_id', 'bucket_start', 'bucket_seconds', 'aggregation', 'value', 'points'] },

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
    status: { field: 'state', labels: { draft: 'Draft', active: 'Active', silent: 'Silent', suspended: 'Suspended' } },
    sections: [
      { title: 'Stream', note: 'A stream binds one device metric to a protocol adapter. It activates only when its device is bound to M45 equipment or an M47 site. Its device and metric are fixed once it has left draft. The sample interval is the ingest expectation used by Telemetry Coverage and the liveness check (silent after three intervals with no reading), and it must be positive. Raw retention is set at creation; afterwards it changes only through a Retention Change the CTO approves. Consent Always Required tightens the consent check; only the Consent Officer relaxes it back, with Change Consent Policy.',
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
      { title: 'Threshold Rule', note: 'A reading that compares true against the threshold raises an alert at the rule severity. Ingest evaluates only active rules. While the rule\'s last alert is open, further breaches are counted on it; after an alert, none is raised again within the cooldown. Sustained For holds an alert back until the breach has lasted that long only where the dwell switch is on. All of these are set when the rule is created. Afterwards the threshold changes only through Change Threshold, severity, Sustained For and Cooldown only through Change Severity, Dwell or Cooldown, and the stream and operator not at all.',
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
      { title: 'Suppression', note: 'Pausing a rule, loosening its threshold, lowering its severity or lengthening its dwell or cooldown is a suppression: give a reason and an expiry here, then use the matching button. An approver other than the requester and the rule author decides it from the approval inbox. It ends after Suppressed Until, when the rule alerts again as it did before.',
        fields: [
          { name: 'suppression_reason', label: 'Suppression Reason' },
          { name: 'suppression_until', label: 'Suppressed Until' },
          { name: 'suppression_kind', label: 'Suppression', readonly: true },
          { name: 'proposed_threshold', label: 'Proposed Threshold', readonly: true },
          { name: 'proposed_severity', label: 'Proposed Severity', readonly: true },
          { name: 'proposed_duration_min', label: 'Proposed Sustained For (minutes)', readonly: true },
          { name: 'proposed_cooldown_min', label: 'Proposed Cooldown (minutes)', readonly: true },
          { name: 'baseline_threshold', label: 'Threshold Before Suppression', readonly: true },
          { name: 'baseline_severity', label: 'Severity Before Suppression', readonly: true },
          { name: 'baseline_duration_min', label: 'Sustained For Before Suppression', readonly: true },
          { name: 'baseline_cooldown_min', label: 'Cooldown Before Suppression', readonly: true },
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
    back: 'M48-downsample',
    status: { field: 'state', labels: { draft: 'Draft', active: 'Active' } },
    sections: [
      { title: 'Downsampling', note: 'The target interval cannot be shorter than the raw interval. A draft policy is edited freely until Request Activation sends it to the CTO: its terms are then frozen until the request is decided or recalled. An active policy changes only through a Retention Change, or Request Switch Off, which returns it to draft once the CTO approves. Design Reduction is the planning figure 1 - raw / target. The Retention Compression KPI uses only the Measured Compression, which the daily retention job computes from the aggregates it actually wrote.',
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
      { title: 'Adapter', note: 'The endpoint and auth mode are recorded configuration; no live broker connection is claimed by this screen. A new adapter is disabled. To enable it, choose Bearer Token or Mutual TLS, record where the credential is kept in Credential Reference, and Rotate Key. Readings arrive at POST /iot/v1/ingest with that key in the X-Adapter-Key header, only for this adapter\'s streams; ingest refuses a disabled adapter, an unauthenticated one and one with no key. Never type a password into the endpoint.',
        fields: [
          { name: 'name', required: true, label: 'Adapter Name' },
          { name: 'protocol', required: true, label: 'Protocol' },
          { name: 'endpoint', label: 'Endpoint' },
          { name: 'auth_mode', required: true, label: 'Authentication' },
          { name: 'credential_ref', label: 'Credential Reference' },
          { name: 'credential_rotated_on', label: 'Credential Rotated On', readonly: true },
          { name: 'key_set', label: 'Key Set', readonly: true },
          { name: 'key_rotated_by', label: 'Key Rotated By', readonly: true },
          { name: 'key_rotated_on', label: 'Key Rotated On', readonly: true },
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
      { title: 'Action', note: 'Proposed → approved → dispatched → done; the state changes only through the actions. Approval is requested here and decided from the approval inbox by the Operations Director (DOFA Tier 2 while nobody holds that role), never the proposer, never on a healthy prediction, one whose model is not a published M26 model, one that already has its outcome, or one with another action under way. Changing the action type, priority or prediction after approval is refused: use Revise Terms. A proposed or approved action can be cancelled with a reason. Dispatch (IoT Operator) needs a technician and hands the work order to M01/M02; completion waits until that order is finished, needs the outcome evidence, is recorded by someone other than the technician, and records whether the failure was confirmed.',
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
          { name: 'revision_note', label: 'Last Terms Revision', readonly: true },
          { name: 'spine_work_order_id', label: 'Work Order', readonly: true },
          { name: 'spine_service_order_id', label: 'Service Order (M01)', readonly: true },
          { name: 'dispatched_on', label: 'Dispatched On', readonly: true },
          { name: 'completed_by', label: 'Completed By', readonly: true },
          { name: 'completed_on', label: 'Completed On', readonly: true },
          { name: 'outcome', label: 'Outcome', readonly: true },
          { name: 'outcome_note', label: 'Outcome Note', readonly: true },
          { name: 'cancelled_by', label: 'Cancelled By', readonly: true },
          { name: 'cancelled_on', label: 'Cancelled On', readonly: true },
          { name: 'cancel_reason', label: 'Why Cancelled', readonly: true }
        ] }
    ]
  },

  'M48-form-alert': {
    kind: 'model_form',
    model: 'fix.iot.alert',
    title: 'IoT Alert',
    back: 'M48-lifecycle',
    status: { field: 'state', labels: { new: 'New', acked: 'Acknowledged', resolved: 'Resolved' } },
    sections: [
      { title: 'Alert', note: 'Raised by the rule engine or a device health change; nobody types it. Acknowledge and Resolve are on the Alert Lifecycle list.',
        fields: [
          { name: 'name', label: 'Alert', readonly: true },
          { name: 'device_id', label: 'Device', readonly: true },
          { name: 'stream_id', label: 'Stream', readonly: true },
          { name: 'rule_id', label: 'Rule', readonly: true },
          { name: 'severity', label: 'Severity', readonly: true },
          { name: 'message', label: 'Message', readonly: true },
          { name: 'trigger_value', label: 'Trigger Value', readonly: true },
          { name: 'last_value', label: 'Latest Value', readonly: true },
          { name: 'occurrence_count', label: 'Occurrences', readonly: true },
          { name: 'last_occurrence_on', label: 'Last Occurrence', readonly: true }
        ] },
      { title: 'Handling', fields: [
          { name: 'acked_by', label: 'Acknowledged By', readonly: true },
          { name: 'acked_on', label: 'Acknowledged On', readonly: true },
          { name: 'resolved_by', label: 'Resolved By', readonly: true },
          { name: 'resolved_on', label: 'Resolved On', readonly: true },
          { name: 'resolution_note', label: 'Resolution', readonly: true }
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
      { title: 'Consent', note: 'A consent must name its subject (the device, site or customer of its subject type) and cannot end before it is granted. Ingest checks it: an active, verified consent in date covers the device, for the signals it lists. A consent grants nothing until it is verified against its evidence: the disclosure file or where the signed form is filed, who granted it, and the signals it lists. A Consent Officer\'s own consent with all of that is verified as recorded; anyone else\'s, or one missing any of it, waits for an officer who did not record it. Changing a verified consent sends it back for verification. Revoke Consent records who and when, suspends the streams it covered that no other valid consent covers, and applies the treatment agreed at grant to the readings held on them. A revoked consent is never reactivated, and the state changes only through Revoke.',
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
          { name: 'disclosure_name', label: 'Disclosure On File', readonly: true },
          { name: 'disclosure_file', type: 'file', label: 'Upload the Disclosure Given' },
          { name: 'disclosure_filename', label: 'Disclosure File Name' },
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
      { title: 'Prediction', note: 'An IoT Operator records the score a published model produced; once saved, it cannot be rewritten: a re-assessment is a new prediction. Confidence must be within 0–1 and days-to-failure cannot be negative (0 means imminent). Model is the code of a published M26 predictive-maintenance model: saving names the choices if it is not one. Request Preventive Work Order is the IoT Operator\'s, on a failure prediction confident enough; it asks once, and can ask again only if the demand it raised is dismissed. The verified outcome is recorded by completing a prescriptive action, never typed.',
        fields: [
          { name: 'name', required: true, label: 'Prediction Reference' },
          { name: 'equipment_id', required: true, label: 'Equipment' },
          { name: 'prediction', required: true, label: 'Prediction' },
          { name: 'confidence', required: true, label: 'Confidence (0-1)' },
          { name: 'estimated_days_to_failure', label: 'Days to Failure' },
          { name: 'model_name', required: true, label: 'Model' },
          { name: 'model_published', label: 'Model Published (M26)', readonly: true },
          { name: 'feature_window_from', label: 'Feature Window From' },
          { name: 'feature_window_to', label: 'Feature Window To' },
          { name: 'outcome', label: 'Verified Outcome', readonly: true },
          { name: 'outcome_note', label: 'Outcome Note', readonly: true },
          { name: 'outcome_action_id', label: 'Outcome From Action', readonly: true },
          { name: 'outcome_recorded_by', label: 'Outcome Recorded By', readonly: true },
          { name: 'last_evaluated', label: 'Last Evaluated', readonly: true },
          { name: 'work_order_created', label: 'Preventive Work Order Requested', readonly: true }
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
      { title: 'Change', note: 'A stream\'s raw retention, a policy\'s compressed retention, and switching a policy on or off change only with CTO approval. Name exactly one target, and one change at a time for it. Request CTO Approval routes it to an IoT Manager who neither requested nor created it; the change applies when they approve it from the inbox, and its terms are frozen once requested.',
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
    'fix.iot.gap': 'M48-form-gap',
    'fix.iot.alert': 'M48-form-alert'
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
    'M48-gaps': 'M48-form-gap',
    'M48-lifecycle': 'M48-form-alert'
  }
};

export const CREATE = {
  M48: { screen: 'M48-form-stream', model: 'fix.iot.stream', label: 'Stream' }
};
