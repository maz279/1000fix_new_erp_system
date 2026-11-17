/** @odoo-module **/
/* A07 · Assets & Facilities — M48 IoT Telemetry & Predictive (v2 rebuild).
 * Registry-faithful: 4 groups / 10 screens / 4 reports / 3 forms / freg 51.
 * Devices, telemetry rows, alerts and predictions existed; streams, adapters,
 * threshold rules, downsampling, prescriptive actions and consent are new.
 * M48 capture audit (2026-11-17): every sub-module page captures its own
 * records - signals, criticality assessments, file batches, maintenance
 * windows, the health index history, prediction outcomes and the parts and
 * skill of an intervention - and every working list sits on a page. */

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
    { en: 'Onboarding', screens: [
      { id: 'M48-iot-device', en: 'Devices & Gateways', bn: 'ডিভাইস ও গেটওয়ে', t: 'g' },
      { id: 'M48-signals', en: 'Signal Definitions', bn: 'সিগন্যাল সংজ্ঞা', t: 'g' },
      { id: 'M48-scopes', en: 'Monitoring Scope', bn: 'পর্যবেক্ষণ পরিধি', t: 'g' }
    ]},
    { en: 'Ingestion', screens: [
      { id: 'M48-streams', en: 'Stream Registry', bn: 'স্ট্রিম রেজিস্টার', t: 'g' },
      { id: 'M48-adapters', en: 'Protocol Adapters', bn: 'প্রোটোকল অ্যাডাপ্টার', t: 'g' },
      { id: 'M48-file-batches', en: 'File Batch Imports', bn: 'ফাইল ব্যাচ আমদানি', t: 'g' },
      { id: 'M48-health', en: 'Pipeline Observability', bn: 'পাইপলাইন', t: 'r' },
      { id: 'M48-gaps', en: 'Telemetry Gaps', bn: 'টেলিমেট্রি বিরতি', t: 'g' },
      { id: 'M48-telemetry', en: 'Telemetry Readings', bn: 'টেলিমেট্রি রিডিং', t: 'g' },
      { id: 'M48-rollups', en: 'Telemetry Aggregates', bn: 'টেলিমেট্রি সমষ্টি', t: 'g' }
    ]},
    { en: 'Alerting', screens: [
      { id: 'M48-alerts', en: 'Threshold Alerts', bn: 'থ্রেশহোল্ড অ্যালার্ট', t: 'g' },
      { id: 'M48-lifecycle', en: 'Alert Lifecycle', bn: 'অ্যালার্ট জীবনচক্র', t: 'g' },
      { id: 'M48-windows', en: 'Maintenance Windows', bn: 'রক্ষণাবেক্ষণ উইন্ডো', t: 'g' }
    ]},
    { en: 'Intelligence', screens: [
      { id: 'M48-scores', en: 'Asset Health Scoring', bn: 'অ্যাসেট স্বাস্থ্য', t: 'r' },
      { id: 'M48-health-history', en: 'Health Index History', bn: 'স্বাস্থ্য সূচক ইতিহাস', t: 'g' },
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
  forms: ['Stream Binding', 'Alert Rule', 'Downsampling Policy', 'Device / Gateway', 'Signal Definition',
    'Telemetry Consent', 'Criticality Assessment', 'Protocol Adapter', 'File Batch Import', 'Retention Change',
    'Maintenance Window', 'Failure Prediction', 'Prediction Outcome', 'Prescriptive Action'],
  cross: ['M17 asset binding', 'M26 prediction models', 'M05 MSP monitoring', 'M01 prescriptive work orders'],
  /* M48 capture audit (2026-11-17): each page captures the records its spec
   * area (§5.1-§5.5) owns, and every working list sits on a page. Page 3's
   * "+ New" was a device and page 5's a failure prediction. */
  freg: { src: 51, sub: [
    ['1', 'Stream Registry & Onboarding', 8, { model: 'fix.iot.stream', cols: ['name', 'device_id', 'signal_id', 'metric', 'unit', 'state'], screens: ['M48-streams', 'M48-iot-device', 'M48-signals', 'M48-consent', 'M48-scopes'], reports: ['Stream Quality Report', 'Telemetry Coverage'], forms: ['Stream Binding', 'Device / Gateway', 'Signal Definition', 'Telemetry Consent', 'Criticality Assessment'] }],
    ['2', 'Protocol Adapters', 7, { model: 'fix.iot.adapter', cols: ['name', 'protocol', 'endpoint', 'auth_mode', 'state'], screens: ['M48-adapters', 'M48-file-batches'], reports: ['Stream Quality Report'], forms: ['Protocol Adapter', 'File Batch Import'] }],
    ['3', 'Ingestion & Storage', 9, { model: 'fix.iot.downsample', cols: ['name', 'stream_id', 'raw_interval_sec', 'target_interval_sec', 'aggregation', 'state'], screens: ['M48-health', 'M48-downsample', 'M48-retention', 'M48-gaps', 'M48-telemetry', 'M48-rollups'], reports: ['Telemetry Coverage', 'Stream Quality Report'], forms: ['Downsampling Policy', 'Retention Change'] }],
    ['4', 'Threshold Alerting', 8, { model: 'fix.iot.rule', cols: ['name', 'stream_id', 'operator', 'threshold', 'severity', 'state'], screens: ['M48-alerts', 'M48-lifecycle', 'M48-windows', 'M48-asset-alerts'], reports: ['Alert Storm Analysis'], forms: ['Alert Rule', 'Maintenance Window'] }],
    ['5', 'Health Scoring', 6, { model: 'fix.iot.health', create: 'M48-form-scope', cols: ['computed_at', 'device_id', 'index_value', 'band', 'trend'], screens: ['M48-scores', 'M48-health-history', 'M48-scopes'], reports: [], forms: ['Criticality Assessment'] }],
    ['6', 'Failure Prediction', 7, { model: 'fix.predictive.maintenance', cols: ['name', 'equipment_id', 'prediction', 'estimated_days_to_failure', 'outcome'], screens: ['M48-failure', 'M48-rul'], reports: ['Prediction Outcome Tracking'], forms: ['Failure Prediction', 'Prediction Outcome'] }],
    ['7', 'Prescriptive Routing', 6, { model: 'fix.iot.action', cols: ['name', 'equipment_id', 'action_type', 'priority', 'technician_id', 'state'], screens: ['M48-routing'], reports: ['Prediction Outcome Tracking'], forms: ['Prescriptive Action'] }]
  ] }
};

export const SCREENS = {
  'M48-asset-alerts': { kind: 'model_list', model: 'fix.asset.alert', stateField: 'state', create: false,
    note: 'What the scheduled checks found, addressed to the role that must act. Acknowledging says you have seen it; it does not fix the cause.',
    domain: [['module', '=', 'M48']],
    cols: ['name', 'record_label', 'role_group', 'no_holder', 'raise_count', 'last_raised_on', 'acknowledged_by_id', 'state'],
    actions: [{ m: 'action_acknowledge', l: 'Acknowledge' }] },
  'M48-streams': { kind: 'model_list', model: 'fix.iot.stream', stateField: 'state',
    cols: ['name', 'device_id', 'equipment_id', 'signal_id', 'metric', 'unit', 'sample_interval_sec', 'retention_days', 'consent_policy', 'adapter_id', 'last_seen', 'state'],
    actions: [
      { m: 'action_activate', l: 'Activate Stream' },
      { m: 'action_suspend', l: 'Suspend Stream' },
      { m: 'action_decommission', l: 'Decommission Stream (IoT Administrator)', ask: 'Why is this stream decommissioned? Ingestion stops, its open alerts and gaps close, and the series is terminated. History is kept.', kwarg: 'reason' },
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
    empty: 'No alert raised. Alerts are raised by the alert rules when a reading crosses a threshold, or by a device health change.',
    cols: ['name', 'device_id', 'rule_id', 'severity', 'message', 'trigger_value', 'occurrence_count', 'last_occurrence_on', 'acked_by', 'resolved_by', 'state'],
    actions: [
      { m: 'action_ack', l: 'Acknowledge' },
      { m: 'action_resolve', l: 'Resolve', ask: 'How was the alert resolved?', kwarg: 'resolution_note' }
    ] },
  'M48-scores': { kind: 'table_report', module: 'M48', report: 'asset_health', title: 'Asset Health Scoring', period: false },
  'M48-failure': { kind: 'model_list', model: 'fix.predictive.maintenance',
    cols: ['name', 'equipment_id', 'prediction', 'failure_mode', 'confidence', 'estimated_days_to_failure', 'horizon_end', 'model_name', 'model_published', 'outcome', 'outcome_action_id', 'work_order_created'],
    actions: [{ m: 'action_create_preventive_wo', l: 'Request Preventive Work Order' }] },
  'M48-rul': { kind: 'table_report', module: 'M48', report: 'rul_estimation', title: 'RUL Estimation', period: false },
  'M48-routing': { kind: 'model_list', model: 'fix.iot.action', stateField: 'state',
    cols: ['name', 'equipment_id', 'action_type', 'priority', 'skill_code', 'parts_state', 'technician_id', 'scheduled_on', 'approval_state', 'approved_by', 'spine_work_order_id', 'spine_service_order_id', 'outcome', 'revision_note', 'state'],
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
    empty: 'No gap recorded. A gap is written by the liveness check when a stream sends no reading for three sample intervals, and closed when readings resume.',
    cols: ['name', 'stream_id', 'device_id', 'gap_from', 'gap_to', 'detected_at', 'cause', 'had_reading', 'points_expected', 'state'] },
  'M48-telemetry': { kind: 'model_list', model: 'fix.iot.telemetry', create: false,
    empty: 'No reading received. Readings arrive from registered device streams through their protocol adapters.',
    note: 'The readings as they arrived. Nobody types or edits them here. A reading with no device was anonymised after its consent was withdrawn.',
    cols: ['timestamp', 'device_id', 'metric', 'value', 'unit', 'quality_flag', 'anonymised'] },
  'M48-rollups': { kind: 'model_list', model: 'fix.iot.telemetry.rollup', create: false,
    empty: 'No aggregate yet. The daily retention job writes them under each active downsampling policy.',
    note: 'What the daily retention job aggregated under each active downsampling policy. Nobody types or edits them here.',
    cols: ['stream_id', 'downsample_id', 'bucket_start', 'bucket_seconds', 'aggregation', 'value', 'points'] },

  /* ===== M48 capture audit (2026-11-17): the new registers ===== */
  'M48-signals': { kind: 'model_list', model: 'fix.iot.signal',
    note: 'What a stream measures. A stream that names a signal takes its metric, unit and interval from it, and a reading outside the expected range is kept and flagged, never dropped.',
    cols: ['code', 'name', 'data_type', 'canonical_unit', 'expected_min', 'expected_max', 'has_range', 'sampling_interval_sec', 'criticality_class', 'retention_class', 'stream_count', 'active'] },
  'M48-scopes': { kind: 'model_list', model: 'fix.iot.monitoring.scope',
    note: 'Assets are monitored because their failure matters (ISO 17359). Health is scored nightly for the devices on every asset in scope.',
    cols: ['name', 'equipment_id', 'site_id', 'criticality', 'device_count', 'last_scored_on', 'worst_band', 'assessed_by_id', 'assessed_on', 'review_due'],
    actions: [{ m: 'action_score_now', l: 'Score Health Now' }] },
  'M48-health-history': { kind: 'model_list', model: 'fix.iot.health', create: false,
    empty: 'No health score yet. Record a criticality assessment for an asset with a device on it, then Score Health Now, or wait for the nightly run.',
    note: 'The health index as history, so the trend shows. Written by scoring, never typed.',
    cols: ['computed_at', 'device_id', 'equipment_id', 'site_id', 'index_value', 'band', 'previous_index', 'trend', 'open_alerts', 'readings_24h', 'factors'] },
  'M48-file-batches': { kind: 'model_list', model: 'fix.iot.file.batch', stateField: 'state',
    note: 'A periodic export is a first-class channel: every row goes through the same gates and rules as a live reading, and every refused row is reported.',
    cols: ['name', 'adapter_id', 'source_ref', 'batch_filename', 'state', 'rows_total', 'rows_accepted', 'rows_rejected', 'alerts_raised', 'processed_by', 'processed_on'],
    actions: [{ m: 'action_process', l: 'Ingest File (IoT Administrator)' }] },
  'M48-windows': { kind: 'model_list', model: 'fix.iot.maintenance.window', stateField: 'state',
    note: 'While an approved window runs, rule breaches on its device or site raise no alert and are counted on the window.',
    cols: ['name', 'device_id', 'site_id', 'date_from', 'date_to', 'reason', 'state', 'requested_by', 'approved_by', 'suppressed_count'],
    actions: [
      { m: 'action_request', l: 'Request Approval' },
      { m: 'action_approve', l: 'Approve Window (IoT Manager)' },
      { m: 'action_cancel', l: 'Cancel Window', ask: 'Why is this window cancelled?', kwarg: 'reason' }
    ] },

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
    status: { field: 'state', labels: { draft: 'Draft', active: 'Active', silent: 'Silent', suspended: 'Suspended', decommissioned: 'Decommissioned' } },
    tabs: [
      { id: 'binding', label: '1. Binding', bn: '১. বাঁধন', icon: '🔗', badge: '11' },
      { id: 'lifecycle', label: '2. Lifecycle', bn: '২. জীবনচক্র', icon: '⏱', badge: '5' }
    ],
    sections: [
      { tab: 'binding', title: 'Stream', note: 'A stream binds one device metric to a protocol adapter. It activates only when its device is bound to M45 equipment or an M47 site. Its device and metric are fixed once it has left draft. The sample interval is the ingest expectation used by Telemetry Coverage and the liveness check (silent after three intervals with no reading), and it must be positive. Raw retention is set at creation; afterwards it changes only through a Retention Change the CTO approves. Consent Always Required tightens the consent check; only the Consent Officer relaxes it back, with Change Consent Policy.',
        fields: [
          { name: 'name', required: true, label: 'Stream Reference' },
          { name: 'device_id', required: true, label: 'Device', domain: [['decommissioned', '=', false]] },
          { name: 'signal_id', label: 'Signal (fills metric, unit and interval)' },
          { name: 'adapter_id', label: 'Protocol Adapter' },
          { name: 'source_address', label: 'Source Address (topic / node / OID / column)' },
          { name: 'metric', required: true, label: 'Metric' },
          { name: 'unit', label: 'Unit' },
          { name: 'sample_interval_sec', required: true, label: 'Sample Interval (s)' },
          { name: 'retention_days', required: true, label: 'Raw Retention (days)' },
          { name: 'consent_policy', required: true, label: 'Consent Policy' }
        ] },
      { tab: 'lifecycle', title: 'Lifecycle', note: 'Decommission Stream (on the Stream Registry list) stops ingestion for good, closes the open alerts and gaps, and keeps the history.',
        fields: [
          { name: 'state', label: 'State', readonly: true },
          { name: 'activated_on', label: 'Activated On', readonly: true },
          { name: 'decommissioned_on', label: 'Decommissioned On', readonly: true },
          { name: 'decommissioned_by', label: 'Decommissioned By', readonly: true },
          { name: 'decommission_reason', label: 'Why Decommissioned', readonly: true }
        ] }
    ]
  },

  'M48-form-rule': {
    kind: 'model_form',
    model: 'fix.iot.rule',
    title: 'Alert Rule',
    back: 'M48-alerts',
    status: { field: 'state', labels: { active: 'Active', paused: 'Paused' } },
    tabs: [
      { id: 'rule', label: '1. Rule', bn: '১. নিয়ম', icon: '📏', badge: '10' },
      { id: 'suppression', label: '2. Suppression', bn: '২. দমন', icon: '🔕', badge: '15' }
    ],
    sections: [
      { tab: 'rule', title: 'Threshold Rule', note: 'A reading that compares true against the threshold raises an alert at the rule severity. Ingest evaluates only active rules. While the rule\'s last alert is open, further breaches are counted on it; after an alert, none is raised again within the cooldown. Sustained For holds an alert back until the breach has lasted that long only where the dwell switch is on. All of these are set when the rule is created. Afterwards the threshold changes only through Change Threshold, severity, Sustained For and Cooldown only through Change Severity, Dwell or Cooldown, and the stream and operator not at all.',
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
      { tab: 'suppression', title: 'Suppression', note: 'Pausing a rule, loosening its threshold, lowering its severity or lengthening its dwell or cooldown is a suppression: give a reason and an expiry here, then use the matching button. An approver other than the requester and the rule author decides it from the approval inbox. It ends after Suppressed Until, when the rule alerts again as it did before.',
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
    tabs: [
      { id: 'action', label: '1. Action', bn: '১. পদক্ষেপ', icon: '🛠', badge: '9' },
      { id: 'needs', label: '2. Parts & Skill', bn: '২. যন্ত্রাংশ ও দক্ষতা', icon: '🧰', badge: '4' },
      { id: 'decision', label: '3. Approval & Outcome', bn: '৩. অনুমোদন ও ফলাফল', icon: '⚖', badge: '14' }
    ],
    sections: [
      { tab: 'action', title: 'Action', note: 'Proposed → approved → dispatched → done; the state changes only through the actions. Approval is requested here and decided from the approval inbox by the Operations Director (DOFA Tier 2 while nobody holds that role), never the proposer, never on a healthy prediction, one whose model is not a published M26 model, one that already has its outcome, or one with another action under way. Changing the action type, priority or prediction after approval is refused: use Revise Terms. A proposed or approved action can be cancelled with a reason. Dispatch (IoT Operator) needs a technician and hands the work order to M01/M02; completion waits until that order is finished, needs the outcome evidence, is recorded by someone other than the technician, and records whether the failure was confirmed.',
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
      { tab: 'needs', title: 'What the Intervention Needs', note: 'The parts it likely needs are checked against stock (M15) and the skill against the M22 competencies. They are part of what is approved: after approval, Revise Terms first.',
        fields: [
          { name: 'recommended_action', type: 'text', label: 'Recommended Action' },
          { name: 'skill_code', label: 'Skill Required (M22 competency code)' },
          { name: 'skill_name', label: 'Skill', readonly: true },
          { name: 'parts_state', label: 'Parts Availability', readonly: true }
        ] },
      { tab: 'decision', title: 'Approval & Outcome', fields: [
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
    ],
    lines: {
      field: 'part_ids',
      title: 'Parts Likely Needed',
      note: 'Availability is free stock in internal locations, read when the form opens.',
      fields: [
        { name: 'product_id', required: true, label: 'Part' },
        { name: 'quantity', required: true, label: 'Quantity' },
        { name: 'on_hand', readonly: true, label: 'Free Stock' },
        { name: 'availability', readonly: true, label: 'Availability' }
      ]
    }
  },

  'M48-form-alert': {
    kind: 'model_form',
    model: 'fix.iot.alert',
    title: 'IoT Alert',
    back: 'M48-lifecycle',
    create: false,
    pick: 'An alert is raised by an alert rule or a device health change, never typed: open one from Alert Lifecycle.',
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
    tabs: [
      { id: 'grant', label: '1. Consent Given', bn: '১. প্রদত্ত সম্মতি', icon: '📝', badge: '17' },
      { id: 'verification', label: '2. Verification & Withdrawal', bn: '২. যাচাই ও প্রত্যাহার', icon: '✅', badge: '9' }
    ],
    sections: [
      { tab: 'grant', title: 'Consent', note: 'A consent must name its subject (the device, site or customer of its subject type) and cannot end before it is granted. Ingest checks it: an active, verified consent in date covers the device, for the signals it lists. A consent grants nothing until it is verified against its evidence: the disclosure file or where the signed form is filed, who granted it, and the signals it lists. A Consent Officer\'s own consent with all of that is verified as recorded; anyone else\'s, or one missing any of it, waits for an officer who did not record it. Changing a verified consent sends it back for verification. Revoke Consent records who and when, suspends the streams it covered that no other valid consent covers, and applies the treatment agreed at grant to the readings held on them. A revoked consent is never reactivated, and the state changes only through Revoke.',
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
      { tab: 'verification', title: 'Verification & Withdrawal', fields: [
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
    tabs: [
      { id: 'score', label: '1. Score', bn: '১. স্কোর', icon: '📈', badge: '12' },
      { id: 'outcome', label: '2. Outcome', bn: '২. ফলাফল', icon: '✅', badge: '8' }
    ],
    sections: [
      { tab: 'score', title: 'Prediction', note: 'An IoT Operator records the score a published model produced; once saved, it cannot be rewritten: a re-assessment is a new prediction. Confidence must be within 0–1 and days-to-failure cannot be negative (0 means imminent). Model is the code of a published M26 predictive-maintenance model: saving names the choices if it is not one. Request Preventive Work Order is the IoT Operator\'s, on a failure prediction confident enough; it asks once, and can ask again only if the demand it raised is dismissed. The verified outcome is recorded by completing a prescriptive action, never typed.',
        fields: [
          { name: 'name', required: true, label: 'Prediction Reference' },
          { name: 'equipment_id', required: true, label: 'Equipment' },
          { name: 'prediction', required: true, label: 'Prediction' },
          { name: 'failure_mode', label: 'Predicted Failure Mode' },
          { name: 'confidence', required: true, label: 'Confidence (0-1)' },
          { name: 'estimated_days_to_failure', label: 'Days to Failure' },
          { name: 'rul_low_days', label: 'RUL Low (days)' },
          { name: 'rul_high_days', label: 'RUL High (days)' },
          { name: 'model_name', required: true, label: 'Model' },
          { name: 'model_published', label: 'Model Published (M26)', readonly: true },
          { name: 'feature_window_from', label: 'Feature Window From' },
          { name: 'feature_window_to', label: 'Feature Window To' },
          { name: 'last_evaluated', label: 'Last Evaluated', readonly: true }
        ] },
      { tab: 'outcome', title: 'Outcome', note: 'Completing a prescriptive action records what it found. A prediction no action acted on gets its outcome from Record Prediction Outcome, after its horizon for a false alarm.',
        fields: [
          { name: 'horizon_end', label: 'Horizon Ends', readonly: true },
          { name: 'outcome', label: 'Verified Outcome', readonly: true },
          { name: 'outcome_evidence_ref', label: 'Outcome Evidence', readonly: true },
          { name: 'outcome_note', label: 'Outcome Note', readonly: true },
          { name: 'outcome_action_id', label: 'Outcome From Action', readonly: true },
          { name: 'outcome_recorded_by', label: 'Outcome Recorded By', readonly: true },
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
    create: false,
    pick: 'A gap is recorded by the liveness check when a stream falls silent, never typed: open one from Telemetry Gaps.',
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
    note: 'One record per physical device or gateway. A device is decommissioned, never deleted: its streams stop and its history is kept.',
    cols: ['name', 'device_id', 'device_type', 'equipment_id', 'site_id', 'partner_id', 'gateway_id', 'firmware', 'connectivity', 'status', 'last_telemetry', 'decommissioned'],
    actions: [
      { m: 'action_decommission', l: 'Decommission Device (IoT Administrator)', ask: 'Why is this device decommissioned? Every stream it publishes is decommissioned with it.', kwarg: 'reason' }
    ] },

  'M48-form-iot-device': {
    kind: 'model_form',
    model: 'fix.iot.device',
    title: 'Device / Gateway',
    back: 'M48-iot-device',
    tabs: [
      { id: 'identity', label: '1. Identity', bn: '১. পরিচয়', icon: '📟', badge: '8' },
      { id: 'binding', label: '2. Binding & Status', bn: '২. বাঁধন ও অবস্থা', icon: '🔗', badge: '10' }
    ],
    sections: [
      { tab: 'identity', title: 'Device', note: 'One record per physical device or gateway (FR-IOT-002): its identifier is unique. A device that reports through a gateway names it. Credentials live on the protocol adapter, never here.',
        fields: [
          { name: 'name', required: true, label: 'Name' },
          { name: 'device_id', required: true, label: 'Device Identifier' },
          { name: 'device_type', required: true, label: 'Device Type' },
          { name: 'serial_no', label: 'Serial Number' },
          { name: 'firmware', label: 'Firmware Version' },
          { name: 'connectivity', label: 'Connectivity' },
          { name: 'gateway_id', label: 'Reports Through Gateway' },
          { name: 'installed_on', label: 'Installed On' }
        ] },
      { tab: 'binding', title: 'Asset Binding & Status', note: 'A stream activates only when its device is bound to M45 equipment or an M47 site (BRU-IOT-02). A device naming a customer needs a telemetry consent before any reading. Status follows the readings; nobody types it.',
        fields: [
          { name: 'company_id', required: true, label: 'Company' },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'equipment_id', label: 'Equipment (M45)' },
          { name: 'site_id', label: 'Site (M47)' },
          { name: 'partner_id', label: 'Customer (data subject)' },
          { name: 'status', label: 'Status', readonly: true },
          { name: 'last_telemetry', label: 'Last Reading', readonly: true },
          { name: 'decommissioned_on', label: 'Decommissioned On', readonly: true },
          { name: 'decommissioned_by', label: 'Decommissioned By', readonly: true },
          { name: 'decommission_reason', label: 'Why Decommissioned', readonly: true }
        ] }
    ]
  },

  'M48-form-signal': {
    kind: 'model_form',
    model: 'fix.iot.signal',
    title: 'Signal Definition',
    back: 'M48-signals',
    sections: [
      { title: 'Signal', note: 'The code is the metric name the readings carry; once streams carry it, it stays. With Range Checked, a reading outside the expected minimum and maximum is stored and flagged Out of Expected Range (FR-IOT-016). The IoT Administrator defines signals.',
        fields: [
          { name: 'code', required: true, label: 'Signal Code' },
          { name: 'name', required: true, label: 'Signal Name' },
          { name: 'data_type', required: true, label: 'Data Type' },
          { name: 'canonical_unit', label: 'Canonical Unit' },
          { name: 'has_range', label: 'Range Checked' },
          { name: 'expected_min', label: 'Expected Minimum' },
          { name: 'expected_max', label: 'Expected Maximum' },
          { name: 'sampling_interval_sec', required: true, label: 'Sampling Interval (s)' },
          { name: 'criticality_class', required: true, label: 'Criticality Class' },
          { name: 'retention_class', required: true, label: 'Retention Class' },
          { name: 'active', label: 'Active' },
          { name: 'stream_count', label: 'Streams Carrying It', readonly: true }
        ] }
    ]
  },

  'M48-form-scope': {
    kind: 'model_form',
    model: 'fix.iot.monitoring.scope',
    title: 'Criticality Assessment',
    newLabel: 'Assess an Asset for Monitoring',
    back: 'M48-scopes',
    tabs: [
      { id: 'assessment', label: '1. Assessment', bn: '১. মূল্যায়ন', icon: '⚖', badge: '8' },
      { id: 'health', label: '2. Health', bn: '২. স্বাস্থ্য', icon: '❤', badge: '4' }
    ],
    sections: [
      { tab: 'assessment', title: 'Why This Asset Is Monitored', note: 'Name one asset: the M45 equipment or the M47 site. Record what its failure costs and why these signals are collected (ISO 17359, BRU-IOT-20). The IoT Administrator assesses; health is scored for the devices on the asset, nightly and with Score Health Now.',
        fields: [
          { name: 'equipment_id', label: 'Equipment (M45)' },
          { name: 'site_id', label: 'Site (M47)' },
          { name: 'criticality', required: true, label: 'Criticality' },
          { name: 'failure_consequence', type: 'text', required: true, label: 'Failure Consequence' },
          { name: 'signal_ids', label: 'Signals Selected' },
          { name: 'selection_rationale', type: 'text', required: true, label: 'Why These Signals' },
          { name: 'assessed_on', required: true, label: 'Assessed On' },
          { name: 'review_due', required: true, label: 'Review Due' }
        ] },
      { tab: 'health', title: 'Health', fields: [
          { name: 'assessed_by_id', label: 'Assessed By', readonly: true },
          { name: 'device_count', label: 'Devices on the Asset', readonly: true },
          { name: 'last_scored_on', label: 'Last Scored', readonly: true },
          { name: 'worst_band', label: 'Worst Band at Last Score', readonly: true }
        ] }
    ]
  },

  'M48-form-health': {
    kind: 'model_form',
    model: 'fix.iot.health',
    title: 'Health Score',
    back: 'M48-health-history',
    create: false,
    pick: 'A health score is written by scoring, never typed: open one from Health Index History.',
    sections: [
      { title: 'Health Score', note: '100, minus 12 per open alert (at most 60), minus 15 degraded or 30 offline, minus 20 with no reading in 24 hours. Bands: 80 and over healthy, 55 watch, 30 degraded, below critical. The trend compares with the previous score (more than 5 points).',
        fields: [
          { name: 'device_id', label: 'Device', readonly: true },
          { name: 'scope_id', label: 'Scope', readonly: true },
          { name: 'computed_at', label: 'Scored At', readonly: true },
          { name: 'index_value', label: 'Health Index', readonly: true },
          { name: 'band', label: 'Band', readonly: true },
          { name: 'previous_index', label: 'Previous Index', readonly: true },
          { name: 'trend', label: 'Trend', readonly: true },
          { name: 'open_alerts', label: 'Open Alerts', readonly: true },
          { name: 'readings_24h', label: 'Readings 24h', readonly: true },
          { name: 'device_status', label: 'Device Status', readonly: true },
          { name: 'factors', label: 'Contributing Factors', readonly: true }
        ] }
    ]
  },

  'M48-form-file-batch': {
    kind: 'model_form',
    model: 'fix.iot.file.batch',
    title: 'File Batch Import',
    back: 'M48-file-batches',
    status: { field: 'state', labels: { draft: 'Draft', processed: 'Processed' } },
    tabs: [
      { id: 'file', label: '1. File', bn: '১. ফাইল', icon: '📄', badge: '4' },
      { id: 'result', label: '2. Validation Report', bn: '২. যাচাই প্রতিবেদন', icon: '📋', badge: '8' }
    ],
    sections: [
      { tab: 'file', title: 'Export File', note: 'A CSV with the columns stream, timestamp (YYYY-MM-DD HH:MM:SS, UTC) and value, one reading per row, for streams of the chosen adapter. Save, then Ingest File on the File Batch Imports list: each row passes the live ingest gates (adapter enabled and keyed, stream active, consent, duplicates) and the alert rules. At most 5,000 rows.',
        fields: [
          { name: 'adapter_id', required: true, label: 'Protocol Adapter' },
          { name: 'source_ref', label: 'Export Reference' },
          { name: 'batch_file', type: 'file', label: 'Export File (CSV)' },
          { name: 'batch_filename', label: 'File Name' }
        ] },
      { tab: 'result', title: 'Result', fields: [
          { name: 'state', label: 'State', readonly: true },
          { name: 'processed_by', label: 'Processed By', readonly: true },
          { name: 'processed_on', label: 'Processed On', readonly: true },
          { name: 'rows_total', label: 'Rows', readonly: true },
          { name: 'rows_accepted', label: 'Accepted', readonly: true },
          { name: 'rows_rejected', label: 'Refused', readonly: true },
          { name: 'alerts_raised', label: 'Alerts Raised', readonly: true },
          { name: 'report', label: 'Validation Report', readonly: true }
        ] }
    ]
  },

  'M48-form-window': {
    kind: 'model_form',
    model: 'fix.iot.maintenance.window',
    title: 'Maintenance Window',
    newLabel: 'Plan a Maintenance Window',
    back: 'M48-windows',
    status: { field: 'state', labels: { draft: 'Draft', requested: 'Awaiting Approval', approved: 'Approved', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Window', note: 'One device or one site, for at most 30 days: suppression is never open-ended (BRU-IOT-16). Request Approval on the list; an IoT Manager other than the requester approves. While an approved window runs, rule breaches on the asset raise no alert and are counted here. Its terms are fixed once requested.',
        fields: [
          { name: 'device_id', label: 'Device' },
          { name: 'site_id', label: 'Site (every device on it)' },
          { name: 'date_from', required: true, label: 'From' },
          { name: 'date_to', required: true, label: 'Until' },
          { name: 'reason', required: true, label: 'Planned Work' },
          { name: 'state', label: 'State', readonly: true },
          { name: 'requested_by', label: 'Requested By', readonly: true },
          { name: 'approved_by', label: 'Approved By', readonly: true },
          { name: 'approved_on', label: 'Approved On', readonly: true },
          { name: 'cancel_reason', label: 'Why Cancelled', readonly: true },
          { name: 'suppressed_count', label: 'Breaches Suppressed', readonly: true }
        ] }
    ]
  },

  /* The outcome of a prediction no intervention acted on (FR-IOT-044): pick it,
   * record what happened. */
  'M48-form-outcome': {
    kind: 'model_form',
    model: 'fix.predictive.maintenance',
    title: 'Prediction Outcome',
    newLabel: 'Record Prediction Outcome',
    back: 'M48-failure',
    pickRecord: {
      label: 'Step 1 of 2: choose the prediction',
      note: 'Failure and degrading predictions still pending their outcome. One with an action under way gets its outcome when the action completes.',
      search: 'Search reference / equipment',
      choose: 'Record its outcome',
      cols: ['name', 'equipment_id', 'prediction', 'failure_mode', 'confidence', 'estimated_days_to_failure', 'horizon_end', 'model_name'],
      domain: [['outcome', '=', 'pending'], ['prediction', '!=', 'healthy']],
      empty: 'No prediction is waiting for its outcome.'
    },
    saveAction: {
      method: 'action_record_outcome', label: 'Record Outcome',
      done: 'Outcome recorded: it counts towards the model precision unless it is unknown',
      kwargs: { outcome: 'outcome', note: 'outcome_note', evidence_ref: 'outcome_evidence_ref' }
    },
    sections: [
      { title: 'Step 2 of 2: What Happened', note: 'Failure Confirmed needs its evidence (job card, fault report or service order). False Alarm and Unknown wait until the horizon has passed; Unknown is excluded from precision. Whoever recorded the prediction does not record its outcome (FR-IOT-044, BRU-IOT-14).',
        fields: [
          { name: 'name', label: 'Prediction', readonly: true },
          { name: 'equipment_id', label: 'Equipment', readonly: true },
          { name: 'prediction', label: 'Predicted', readonly: true },
          { name: 'horizon_end', label: 'Horizon Ends', readonly: true },
          { name: 'outcome', label: 'Outcome', required: true, readonly: true },
          { name: 'outcome_note', type: 'text', label: 'How It Was Established', required: true, readonly: true },
          { name: 'outcome_evidence_ref', label: 'Evidence Reference', readonly: true }
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
  'M48:Downsampling Policy': 'fix.iot.downsample',
  'M48:Device / Gateway': 'fix.iot.device',
  'M48:Signal Definition': 'fix.iot.signal',
  'M48:Telemetry Consent': 'fix.iot.consent',
  'M48:Criticality Assessment': 'fix.iot.monitoring.scope',
  'M48:Protocol Adapter': 'fix.iot.adapter',
  'M48:File Batch Import': 'fix.iot.file.batch',
  'M48:Retention Change': 'fix.iot.retention.change',
  'M48:Maintenance Window': 'fix.iot.maintenance.window',
  'M48:Failure Prediction': 'fix.predictive.maintenance',
  'M48:Prediction Outcome': 'fix.predictive.maintenance',
  'M48:Prescriptive Action': 'fix.iot.action'
};

export const FORM_CHIPS = {
  'M48:Stream Binding': 'M48-form-stream',
  'M48:Alert Rule': 'M48-form-rule',
  'M48:Downsampling Policy': 'M48-form-downsample',
  'M48:Device / Gateway': 'M48-form-iot-device',
  'M48:Signal Definition': 'M48-form-signal',
  'M48:Telemetry Consent': 'M48-form-consent',
  'M48:Criticality Assessment': 'M48-form-scope',
  'M48:Protocol Adapter': 'M48-form-adapter',
  'M48:File Batch Import': 'M48-form-file-batch',
  'M48:Retention Change': 'M48-form-retention',
  'M48:Maintenance Window': 'M48-form-window',
  'M48:Failure Prediction': 'M48-form-prediction',
  'M48:Prediction Outcome': 'M48-form-outcome',
  'M48:Prescriptive Action': 'M48-form-action',
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
    'fix.iot.alert': 'M48-form-alert',
    'fix.iot.signal': 'M48-form-signal',
    'fix.iot.monitoring.scope': 'M48-form-scope',
    'fix.iot.health': 'M48-form-health',
    'fix.iot.file.batch': 'M48-form-file-batch',
    'fix.iot.maintenance.window': 'M48-form-window'
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
    'M48-lifecycle': 'M48-form-alert',
    'M48-signals': 'M48-form-signal',
    'M48-scopes': 'M48-form-scope',
    'M48-health-history': 'M48-form-health',
    'M48-file-batches': 'M48-form-file-batch',
    'M48-windows': 'M48-form-window'
  }
};

export const CREATE = {
  M48: { screen: 'M48-form-stream', model: 'fix.iot.stream', label: 'Stream' }
};
