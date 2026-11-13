/** @odoo-module **/
/* A12 · Platform & Technology — M28 Integration, API & Events (full build).
 * Registry-faithful: 4 groups / 10 screens / 5 reports / 3 forms / freg 70.
 * Backend: cd_itsm/models/fix_integration.py (API catalogue, consumers/quotas,
 * topics/schemas/subscriptions/DLQ, connectors, credentials, sync conflicts,
 * integration log).
 *
 * A12 finish build: the group "Webhooks & Trust" holds the screens the registry
 * has no line for (subscriptions, credentials, allowed hosts, deliveries, the
 * measured log). The registry is frozen, so they live here.
 * No secrets manager exists (B-8): "rotate" versions a vault reference and records
 * an audit row. Every note on these screens says so; none claims more. */

export const MODULE = {
  area: 'A12', code: 'M28', en: 'Integration, API & Events', title: 'M28 · Integration, API & Events',
  bn: 'ইন্টিগ্রেশন ও এপিআই', icon: '🔌',
  desc: 'The API catalogue with consumers, credentials and rate limits, the event bus (topics, schema registry, subscriptions, dead-letter queue and replay), the 47-connector framework with health, and the offline sync protocol with conflict resolution.',
  kpis: [
    { l: 'API p95', m: 'api_p95', suffix: ' ms' },
    { l: 'Event Delivery', m: 'event_delivery', suffix: '%' },
    { l: 'DLQ Depth', m: 'dlq_depth' },
    { l: 'Connectors Live', m: 'connectors_live' },
    { l: 'Sync Conflicts Today', m: 'sync_conflicts_today' }
  ],
  groups: [
    { en: 'Gateway', screens: [
      { id: 'M28-apis', en: 'API Catalogue', bn: 'এপিআই ক্যাটালগ', t: 'g' },
      { id: 'M28-consumers', en: 'Consumers & Credentials', bn: 'ভোক্তা', t: 'g' },
      { id: 'M28-quotas', en: 'Rate Limits & Quotas', bn: 'সীমা', t: 'g' }
    ]},
    { en: 'Events', screens: [
      { id: 'M28-topics', en: 'Event Topics', bn: 'ইভেন্ট টপিক', t: 'g' },
      { id: 'M28-schemas', en: 'Schema Registry', bn: 'স্কিমা রেজিস্ট্রি', t: 'g' },
      { id: 'M28-dlq', en: 'Dead-Letter Queue', bn: 'ডেড-লেটার', t: 'g' },
      { id: 'M28-replay', en: 'Replay', bn: 'রিপ্লে', t: 'g' }
    ]},
    { en: 'Connectors', screens: [
      { id: 'M28-external', en: '47 External Connectors', bn: 'বাহ্যিক সংযোগ', t: 'g' },
      { id: 'M28-health', en: 'Connector Health', bn: 'সংযোগ স্বাস্থ্য', t: 'r' }
    ]},
    { en: 'Sync', screens: [
      { id: 'M28-offline', en: 'Offline Sync Protocol', bn: 'অফলাইন সিঙ্ক', t: 'r' },
      { id: 'M28-conflicts', en: 'Conflict Resolution', bn: 'দ্বন্দ্ব নিষ্পত্তি', t: 'g' }
    ]},
    { en: 'Webhooks & Trust', screens: [
      { id: 'M28-subscriptions', en: 'Webhook Subscriptions', bn: 'ওয়েবহুক সাবস্ক্রিপশন', t: 'g' },
      { id: 'M28-deliveries', en: 'Webhook Deliveries', bn: 'ওয়েবহুক ডেলিভারি', t: 'g' },
      { id: 'M28-allowlist', en: 'Allowed Hosts', bn: 'অনুমোদিত হোস্ট', t: 'g' },
      { id: 'M28-credentials', en: 'Connector Credentials', bn: 'সংযোগ ক্রেডেনশিয়াল', t: 'g' },
      { id: 'M28-log', en: 'Integration Log', bn: 'ইন্টিগ্রেশন লগ', t: 'g' },
      { id: 'M28-reconciliation', en: 'Reconciliation Runs', bn: 'রিকনসিলিয়েশন', t: 'g' },
      { id: 'M28-suppressions', en: 'Reconciliation Suppressions', bn: 'রিকনসিলিয়েশন স্থগিত', t: 'g' }
    ]}
  ],
  reports: ['API Usage by Consumer', 'Event Delivery SLO', 'Connector Latency', 'DLQ Analysis', 'Webhook Success Rate'],
  /* The registry names three forms. The rest are what the sub-module pages
   * capture (capture audit 2026-11-14): each page offers the record it is
   * about, and its form panel lists every record it covers. */
  forms: ['API Consumer', 'Event Subscription', 'Connector Credential',
    'API Rate Limit', 'API Endpoint', 'Event Topic', 'Event Schema', 'Allowed Host', 'Connector',
    'Sync Conflict Decision', 'Reconciliation Investigation', 'Reconciliation Suppression'],
  cross: ['M29 credentials security', 'M63 automation triggers', 'M48 telemetry', 'M24 evidence'],
  /* Pages map to spec s5: 1 = 5.1 gateway traffic (rate limits, FR-IPF-004),
   * 2 = 5.2 registry/versions/consumers, 3 = 5.3 outbox, topics, schemas,
   * 4 = 5.3 subscriptions + dead letters, 5 = 5.4 webhooks, 6 = 5.5 connectors
   * and credentials, 7 = 5.6 offline sync, 8 = 5.7 reconciliation (FR-IPF-052).
   * Before 2026-11-14 pages 4, 7 and 8 captured nothing, page 8 listed sync
   * conflicts, and page 1 repeated page 2's "+ New API Endpoint". */
  freg: { src: 70, sub: [
    ['1', 'Gateway', 10, { model: 'fix.api.quota', cols: ['consumer_id', 'endpoint_id', 'requests_per_min', 'daily_quota', 'state'], screens: ['M28-quotas', 'M28-apis'], reports: ['API Usage by Consumer'], forms: ['API Rate Limit'], create: 'M28-form-quota' }],
    ['2', 'Versioning & Portals', 6, { model: 'fix.api.endpoint', cols: ['code', 'version', 'path', 'lifecycle', 'sunset_on', 'active'], screens: ['M28-apis', 'M28-consumers'], reports: ['API Usage by Consumer'], forms: ['API Endpoint', 'API Consumer'] }], // gitleaks:allow (screen ids, not a key)
    ['3', 'Outbox & Event Bus', 12, { model: 'fix.event.topic', cols: ['code', 'name', 'schema_id', 'retention_days', 'state'], screens: ['M28-topics', 'M28-schemas'], reports: ['Event Delivery SLO'], forms: ['Event Topic', 'Event Schema'] }],
    ['4', 'Subscriptions & DLQ', 9, { model: 'fix.event.dlq', cols: ['topic_code', 'reason', 'attempts', 'created_at', 'state'], screens: ['M28-dlq', 'M28-replay', 'M28-subscriptions'], reports: ['DLQ Analysis', 'Event Delivery SLO'], forms: ['Event Subscription'], create: 'M28-form-subscription' }],
    ['5', 'Webhooks', 5, { model: 'fix.event.subscription', cols: ['name', 'consumer_id', 'topic_id', 'endpoint_url', 'state'], screens: ['M28-subscriptions', 'M28-deliveries', 'M28-allowlist'], reports: ['Webhook Success Rate', 'Event Delivery SLO'], forms: ['Event Subscription', 'Allowed Host'] }],
    ['6', 'Connector Framework (47)', 12, { model: 'fix.connector', cols: ['name', 'connector_type', 'endpoint', 'last_latency_ms', 'state'], screens: ['M28-external', 'M28-credentials', 'M28-health'], reports: ['Connector Latency'], forms: ['Connector', 'Connector Credential'] }],
    ['7', 'Offline Sync', 10, { model: 'fix.sync.conflict', cols: ['name', 'device_ref', 'res_model', 'detected_at', 'resolution'], screens: ['M28-offline', 'M28-conflicts'], reports: [], forms: ['Sync Conflict Decision'], create: 'M28-form-conflict-resolve' }],
    ['8', 'Reconciliation', 6, { model: 'fix.integration.reconciliation.run', cols: ['run_at', 'check_code', 'records_compared', 'divergences_found', 'state', 'resolved_by_id'], screens: ['M28-reconciliation', 'M28-suppressions', 'M28-health'], reports: ['Connector Latency'], forms: ['Reconciliation Investigation', 'Reconciliation Suppression'], create: 'M28-form-recon-investigation' }]
  ] }
};

const DLQ_ACTIONS = [
  { m: 'action_replay', l: 'Replay', states: ['pending'], asks: [
    { label: 'Why replay this dead letter? (required)', kwarg: 'reason' },
    { label: 'Authenticator code (leave empty if you have none enrolled)', kwarg: 'otp' }
  ] },
  { m: 'action_discard', l: 'Request Discard', states: ['pending'], ask: 'Why can this dead letter be discarded? A second Integration Admin decides.', kwarg: 'reason' },
  { m: 'action_recall_approval', l: 'Recall Request' }
];

export const SCREENS = {
  'M28-apis': { kind: 'model_list', model: 'fix.api.endpoint',
    cols: ['code', 'version', 'path', 'method', 'auth_type', 'lifecycle', 'deprecated_on', 'sunset_on', 'active', 'approval_state'],
    actions: [
      { m: 'action_publish_endpoint', l: 'Publish Version' },
      { m: 'action_deprecate', l: 'Deprecate', ask: 'Sunset date, YYYY-MM-DD: at least six months away (empty takes exactly six months)', kwarg: 'sunset_on' },
      { m: 'action_sunset', l: 'Sunset', ask: 'Why can this version go? Blocked inside the notice, or while a registered consumer still calls it.', kwarg: 'reason' },
      { m: 'action_request_public', l: 'Request Public Access', ask: 'Why should this endpoint be public? A second Integration Admin decides.', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Request' }
    ] },
  'M28-consumers': { kind: 'model_list', model: 'fix.api.consumer',
    cols: ['name', 'partner_id', 'key_ref', 'request_count', 'registration_state', 'approval_state', 'active'],
    actions: [
      { m: 'action_request_registration', l: 'Request Registration', ask: 'Why should this consumer be registered? A second Integration Admin decides.', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Request' },
      { m: 'action_issue_key', l: 'Issue Key Reference' },
      { m: 'action_rotate_key', l: 'Rotate Key Reference' }
    ] },
  'M28-quotas': { kind: 'model_list', model: 'fix.api.quota', stateField: 'state',
    cols: ['consumer_id', 'endpoint_id', 'requests_per_min', 'daily_quota', 'state', 'approval_state', 'proposed_requests_per_min', 'proposed_daily_quota'],
    actions: [
      { m: 'action_request_increase', l: 'Request Limit Increase', asks: [
        { label: 'New requests per minute', kwarg: 'requests_per_min', number: true },
        { label: 'New daily quota', kwarg: 'daily_quota', number: true },
        { label: 'Why does this consumer need more? A second Integration Admin decides.', kwarg: 'justification' }
      ] },
      { m: 'action_recall_approval', l: 'Recall Request' }
    ] },
  'M28-topics': { kind: 'model_list', model: 'fix.event.topic', stateField: 'state',
    cols: ['code', 'name', 'schema_id', 'retention_days', 'state', 'paused_at', 'pause_reason'],
    actions: [
      { m: 'action_pause', l: 'Pause', states: ['active'], ask: 'Why pause this topic? Its events are held until resume.', kwarg: 'reason' },
      { m: 'action_resume', l: 'Resume', states: ['paused'] }
    ] },
  'M28-schemas': { kind: 'model_list', model: 'fix.event.schema', stateField: 'state',
    cols: ['code', 'version', 'state', 'approval_state'],
    actions: [
      { m: 'action_publish', l: 'Publish Schema', states: ['draft'] },
      { m: 'action_request_breaking_exception', l: 'Request Breaking-Change Exception', states: ['draft'], ask: 'Why is this breaking change needed? A second Integration Admin decides; you cannot approve your own.', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Request' },
      { m: 'action_deprecate', l: 'Deprecate', states: ['published'] }
    ] },
  'M28-subscriptions': { kind: 'model_list', model: 'fix.event.subscription', stateField: 'state',
    cols: ['name', 'consumer_id', 'topic_id', 'endpoint_url', 'secret_ref', 'consecutive_failures', 'pause_reason', 'approval_state', 'state'],
    actions: [
      { m: 'action_request_go_live', l: 'Request Go-Live', states: ['draft', 'paused'], ask: 'Why should this webhook go live? A second Integration Admin decides.', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Request' },
      { m: 'action_pause', l: 'Pause', states: ['active', 'failing'], ask: 'Why pause this webhook?', kwarg: 'reason' },
      { m: 'action_resume', l: 'Resume', states: ['paused'], ask: 'Why can this webhook resume? Missed events are not replayed automatically.', kwarg: 'reason' },
      { m: 'action_rotate_secret', l: 'Rotate Signing Secret Reference' }
    ] },
  'M28-deliveries': { kind: 'model_list', model: 'fix.webhook.delivery', stateField: 'state', create: false, // engine-raised: one row per event per subscription
    cols: ['event_type', 'subscription_id', 'state', 'attempts', 'next_attempt_at', 'last_outcome', 'last_status_code', 'sent_at'],
    empty: 'No webhook delivery yet. A delivery is recorded automatically for each event sent to a subscriber; deliveries are evidence and cannot be typed in.' },
  'M28-allowlist': { kind: 'model_list', model: 'fix.integration.allowed.host', stateField: 'state',
    cols: ['host', 'reason', 'state', 'listed_by_id', 'listed_at', 'removed_by_id', 'removal_reason'],
    actions: [
      { m: 'action_remove', l: 'Remove Host', states: ['listed'], ask: 'Why remove this host? Webhooks on it pause at once.', kwarg: 'reason' }
    ] },
  'M28-credentials': { kind: 'model_list', model: 'fix.connector.credential',
    cols: ['name', 'auth_type', 'secret_ref', 'expires_on', 'rotated_at', 'rotated_by_id', 'expiry_alerted_on', 'active'],
    actions: [
      { m: 'action_rotate', l: 'Rotate Reference', ask: 'New expiry date, YYYY-MM-DD (empty keeps the current date). This versions the reference and records an audit row; load the new value in the vault yourself.', kwarg: 'expires_on' }
    ] },
  'M28-reconciliation': { kind: 'model_list', model: 'fix.integration.reconciliation.run', stateField: 'state', create: false, // nightly job: no role can switch it off
    cols: ['run_at', 'check_code', 'records_compared', 'divergences_found', 'state', 'alerted', 'detail', 'suppression_id', 'resolved_by_id', 'resolution_note'],
    actions: [
      { m: 'action_resolve', l: 'Record Investigation', states: ['divergent', 'suppressed'], ask: 'What was found and done?', kwarg: 'note' }
    ] },
  'M28-suppressions': { kind: 'model_list', model: 'fix.integration.reconciliation.suppression', stateField: 'status',
    cols: ['check_code', 'reason', 'valid_until', 'status', 'approval_state', 'in_force_from', 'ended_at'],
    actions: [
      { m: 'action_request_suppression', l: 'Request Suppression', ask: 'Why should this alert be held back? A second person decides.', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Request' },
      { m: 'action_end', l: 'End Now' }
    ] },
  'M28-log': { kind: 'model_list', model: 'fix.integration.log', stateField: 'status', create: false, // system-written only
    cols: ['created_at', 'kind', 'status', 'measured', 'consumer_id', 'endpoint_id', 'route', 'topic_code', 'subscription_id', 'connector_id', 'status_code', 'latency_ms', 'outcome'],
    empty: 'No integration call logged yet. Every API call, event and connector probe is logged automatically; the log is audit evidence and cannot be typed in.' },
  'M28-dlq': { kind: 'model_list', model: 'fix.event.dlq', stateField: 'state', create: false, // engine-raised: DLQ entries come from failed deliveries
    cols: ['display_label', 'topic_code', 'reason', 'origin', 'attempts', 'created_at', 'decision_reason', 'approval_state', 'state'],
    empty: 'No dead letter. An event lands here automatically when its delivery fails after every retry; select one to replay or discard it with a reason.',
    actions: DLQ_ACTIONS },
  'M28-replay': { kind: 'model_list', model: 'fix.event.dlq', stateField: 'state', create: false,
    cols: ['display_label', 'topic_code', 'reason', 'origin', 'attempts', 'replayed_at', 'replayed_by', 'decision_reason', 'approval_state', 'state'],
    domain: [['state', 'in', ['pending', 'replayed']]],
    actions: DLQ_ACTIONS },
  'M28-external': { kind: 'model_list', model: 'fix.connector', stateField: 'state',
    cols: ['name', 'connector_type', 'endpoint', 'credential_id', 'fallback_connector_id', 'last_latency_ms', 'last_probe_at', 'last_probe_note', 'approval_state', 'state'],
    actions: [
      { m: 'action_request_go_live', l: 'Request Go-Live', states: ['registered', 'degraded'], ask: 'Why should this connector go live? A second Integration Admin decides.', kwarg: 'justification' },
      { m: 'action_recall_approval', l: 'Recall Request' },
      { m: 'action_probe', l: 'Probe' },
      { m: 'action_mark_degraded', l: 'Mark Degraded', ask: 'Why is this connector degraded?', kwarg: 'reason' },
      { m: 'action_mark_down', l: 'Mark Down', ask: 'Why is this connector down?', kwarg: 'reason' },
      { m: 'action_mark_live', l: 'Mark Live', ask: 'What shows this connector is live? A down connector also needs a measured success.', kwarg: 'reason' },
      { m: 'action_disable', l: 'Disable', ask: 'Why is this connector being disabled?', kwarg: 'reason' }
    ] },
  'M28-health': { kind: 'table_report', module: 'M28', report: 'connector_latency', title: 'Connector Health', period: false },
  'M28-offline': { kind: 'table_report', module: 'M28', report: 'offline_sync', title: 'Offline Sync Protocol', period: false },
  'M28-conflicts': { kind: 'model_list', model: 'fix.sync.conflict', stateField: 'resolution', create: false, // engine-raised: conflicts come from the offline ledger
    cols: ['name', 'device_ref', 'res_model', 'res_id', 'field_name', 'policy_class', 'local_value', 'remote_value', 'engine_note', 'resolution', 'resolved_by_id', 'resolution_note'],
    empty: 'No sync conflict. A conflict is raised automatically when an offline change collides with the server record; select one to decide which value wins.',
    actions: [
      { m: 'action_local_wins', l: 'Local Wins' },
      { m: 'action_remote_wins', l: 'Remote Wins' },
      { m: 'action_merged', l: 'Mark Merged', ask: 'How was this reconciled by hand?', kwarg: 'note' },
      { m: 'action_dismiss', l: 'Close, Nothing Applied', ask: 'Why is this closed with nothing applied?', kwarg: 'note' }
    ] },

  /* Report chips -> their own computed pack */
  'M28-rpt-usage': { kind: 'table_report', module: 'M28', report: 'api_usage', title: 'API Usage by Consumer', period: false },
  'M28-rpt-slo': { kind: 'table_report', module: 'M28', report: 'event_delivery_slo', title: 'Event Delivery SLO', period: false },
  'M28-rpt-latency': { kind: 'table_report', module: 'M28', report: 'connector_latency', title: 'Connector Latency', period: false },
  'M28-rpt-dlq': { kind: 'table_report', module: 'M28', report: 'dlq_analysis', title: 'DLQ Analysis', period: false },
  'M28-rpt-webhook': { kind: 'table_report', module: 'M28', report: 'webhook_success', title: 'Webhook Success Rate', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M28-form-endpoint': {
    kind: 'model_form',
    model: 'fix.api.endpoint',
    title: 'API Endpoint',
    back: 'M28-apis',
    sections: [
      { title: 'Endpoint', note: 'Code + version is unique per company. There is no gateway yet: the API edge gates and logs the routes it is wired to, matching them on Path, and each route checks its own authentication. Public access goes through Request Public Access, and a second Integration Admin decides. Lifecycle: Designed, Published, Deprecated, Sunset. Deprecate starts six months of notice; Sunset is blocked inside the notice and while a registered consumer still calls it.',
        fields: [
          { name: 'code', required: true, label: 'Code' },
          { name: 'name', required: true, label: 'Name' },
          { name: 'version', required: true, label: 'Version' },
          { name: 'path', required: true, label: 'Path' },
          { name: 'method', required: true, label: 'Method' },
          { name: 'auth_type', required: true, label: 'Auth' },
          { name: 'description', label: 'Description' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },

  'M28-form-consumer': {
    kind: 'model_form',
    model: 'fix.api.consumer',
    title: 'API Consumer',
    back: 'M28-consumers',
    sections: [
      { title: 'Consumer', note: 'The key reference is a vault path - the key value itself never lands in this model (SEC-101). Set it here on a new consumer, or leave it empty and use Issue Key Reference. After that it changes only through Rotate Key Reference, which versions the reference and records an audit row. No secrets manager is attached: rotating does not issue a key, and you load the new value in the vault yourself. The Linked Partner is how the API edge recognises this consumer, and only once it is registered: a new consumer waits for Request Registration, and a second Integration Admin decides. Request counts are measured from the log.',
        fields: [
          { name: 'name', required: true, label: 'Consumer Name', bn: 'ভোক্তার নাম' },
          { name: 'partner_id', label: 'Linked Partner', bn: 'সংযুক্ত পার্টনার' },
          { name: 'key_ref', label: 'Key Reference (vault://)', bn: 'কী রেফারেন্স (vault://)' },
          { name: 'active', label: 'Active', bn: 'সক্রিয়' }
        ] }
    ]
  },

  'M28-form-quota': {
    kind: 'model_form',
    model: 'fix.api.quota',
    title: 'API Rate Limit',
    back: 'M28-quotas',
    status: { field: 'state', labels: { active: 'Active', throttled: 'Throttled' } },
    sections: [
      { title: 'Rate Limit', note: 'Limits must be positive and take effect on the next request. A limit goes down here; raising one needs Request Limit Increase, and a second Integration Admin decides. Throttled is measured from the log, on the routes the API edge is wired to.',
        fields: [
          { name: 'consumer_id', required: true, label: 'Consumer' },
          { name: 'endpoint_id', label: 'Endpoint' },
          { name: 'requests_per_min', required: true, label: 'Requests / minute' },
          { name: 'daily_quota', required: true, label: 'Daily Quota' }
        ] }
    ]
  },

  'M28-form-subscription': {
    kind: 'model_form',
    model: 'fix.event.subscription',
    title: 'Event Subscription',
    back: 'M28-subscriptions',
    status: { field: 'state', labels: { active: 'Active', paused: 'Paused', failing: 'Failing' } },
    tabs: [
      { id: 'binding', label: '1. Binding', bn: '১. বাইন্ডিং', icon: '🔗', badge: '3' },
      { id: 'secret', label: '2. Delivery Security', bn: '২. ডেলিভারি সিকিউরিটি', icon: '🔐', badge: '1' }
    ],
    sections: [
      { tab: 'binding', title: 'Subscription Binding', note: 'A webhook binding: each event on the topic is posted to the consumer URL, signed, with three attempts before the dead-letter queue. Five failures in a row disable it. The URL must be https and on Allowed Hosts, checked again at each send. A new webhook sends nothing until Request Go-Live is approved by a second Integration Admin; changing the URL, topic or consumer takes it out of service again. Real sending also needs a system administrator to turn on fix.integration.dispatch_enabled; while off, each delivery records not sent.',
        fields: [
          { name: 'consumer_id', required: true, label: 'Consumer' },
          { name: 'topic_id', required: true, label: 'Topic' },
          { name: 'endpoint_url', required: true, label: 'Endpoint URL' }
        ] },
      { tab: 'secret', title: 'Delivery Security', note: 'The signing secret is referenced by vault:// alias only — the value itself never enters this model. Set it here on a new subscription; after that it changes only through Rotate Signing Secret Reference, which versions the reference and records an audit row. No secrets manager is attached, so you load the new value yourself.',
        fields: [
          { name: 'secret_ref', required: true, label: 'Signing Secret Reference (vault://)' }
        ] }
    ]
  },

  'M28-form-credential': {
    kind: 'model_form',
    model: 'fix.connector.credential',
    title: 'Connector Credential',
    back: 'M28-credentials',
    tabs: [
      { id: 'identity', label: '1. Credential', bn: '১. ক্রেডেনশিয়াল', icon: '🪪', badge: '3' },
      { id: 'secret', label: '2. Vault & Expiry', bn: '২. ভল্ট ও মেয়াদ', icon: '🔐', badge: '2' }
    ],
    sections: [
      { tab: 'identity', title: 'Credential Identity', note: 'Only the vault reference is stored. The secret value lives in the vault and is never written to this model (SEC-101).',
        fields: [
          { name: 'name', required: true, label: 'Credential Name' },
          { name: 'auth_type', required: true, label: 'Auth Type' },
          { name: 'active', label: 'Active' }
        ] },
      { tab: 'secret', title: 'Vault Reference & Expiry', note: 'Set the reference on a new credential. After that it changes only through Rotate Reference on the Connector Credentials list. That action versions the reference and records an audit row. No secrets manager is attached, so it changes no secret: you load the new value at the new path in the vault. Thirty days before expiry the Integration Admins get a to-do.',
        fields: [
          { name: 'secret_ref', required: true, label: 'Vault Reference' },
          { name: 'expires_on', label: 'Expires On' }
        ] }
    ]
  },

  'M28-form-topic': {
    kind: 'model_form',
    model: 'fix.event.topic',
    title: 'Event Topic',
    back: 'M28-topics',
    status: { field: 'state', labels: { active: 'Active', paused: 'Paused' } },
    sections: [
      { title: 'Topic', note: 'The code is the exact event type. A published schema is checked at emit, and a payload that breaks it is refused. Events past the retention days are deleted daily once settled (minimum 1 day). Pause holds the topic: nothing reaches a consumer or webhook until Resume, which delivers what was held.',
        fields: [
          { name: 'code', required: true, label: 'Topic Code' },
          { name: 'name', required: true, label: 'Name' },
          { name: 'schema_id', label: 'Schema' },
          { name: 'retention_days', required: true, label: 'Retention (days)' }
        ] }
    ]
  },

  'M28-form-schema': {
    kind: 'model_form',
    model: 'fix.event.schema',
    title: 'Event Schema',
    back: 'M28-schemas',
    status: { field: 'state', labels: {
      draft: 'Draft', published: 'Published', deprecated: 'Deprecated' } },
    sections: [
      { title: 'Schema', note: 'The JSON Schema payload contract. Draft → published → deprecated; once published the code, version and contract are frozen - a correction ships as a NEW version (BRU-IPF-06). A new version that breaks the one in force needs Request Breaking-Change Exception: a second Integration Admin decides, and you cannot approve a schema you registered. Checked at emit: type, required, properties, enum, items, additionalProperties.',
        fields: [
          { name: 'code', required: true, label: 'Schema Code' },
          { name: 'version', required: true, label: 'Version' },
          { name: 'schema_text', required: true, type: 'text', label: 'JSON Schema' }
        ] }
    ]
  },

  'M28-form-connector': {
    kind: 'model_form',
    model: 'fix.connector',
    title: 'Connector',
    back: 'M28-external',
    status: { field: 'state', labels: {
      live: 'Live', degraded: 'Degraded', down: 'Down', disabled: 'Disabled' } },
    sections: [
      { title: 'Connector', note: 'A new connector is not live until Request Go-Live is approved by a second Integration Admin, and changing its endpoint or credential takes it back. The endpoint must be https and on Allowed Hosts; a change is audited. Probe measures from recorded traffic, the credential expiry and, when dispatch is on, one real request; the note says what was measured. The mark actions are an audited override, and a down connector needs a measured success before it can be marked live. Traffic does not flow through this register yet, so the fallback is a record: it switches nothing.',
        fields: [
          { name: 'name', required: true, label: 'Connector Name', bn: 'সংযোগের নাম' },
          { name: 'connector_type', required: true, label: 'Type', bn: 'ধরন' },
          { name: 'endpoint', label: 'Endpoint', bn: 'এন্ডপয়েন্ট' },
          { name: 'credential_id', label: 'Credential', bn: 'ক্রেডেনশিয়াল' },
          { name: 'fallback_connector_id', label: 'Fallback Connector', bn: 'বিকল্প সংযোগ' }
        ] }
    ]
  },

  'M28-form-conflict': {
    kind: 'model_form',
    model: 'fix.sync.conflict',
    title: 'Sync Conflict',
    back: 'M28-conflicts',
    /* raised by the sync engine, never typed: opened only from its list */
    create: false, pick: 'A sync conflict is raised by the offline sync engine: open one from Sync Conflicts.',
    status: { field: 'resolution', labels: {
      pending: 'Pending', local_wins: 'Local Wins', remote_wins: 'Remote Wins',
      merged: 'Manually Merged', dismissed: 'Closed, Nothing Applied' } },
    sections: [
      { title: 'Conflict', note: 'An offline command that collided with the server record, raised by the sync engine from the offline ledger. Nobody types these. The target and values are evidence and do not change. BRU-IPF-17 decides what a resolution can do: the device wins only on notes and evidence; on state, price, stock and assignment the server value stands. Targets outside the sync allow-list cannot be written at all. Each resolution is audited.',
        fields: [
          { name: 'device_ref', readonly: true, label: 'Device / Client', bn: 'ডিভাইস' },
          { name: 'res_model', readonly: true, label: 'Record Model', bn: 'রেকর্ড মডেল' },
          { name: 'res_id', readonly: true, label: 'Record ID', bn: 'রেকর্ড আইডি' },
          { name: 'field_name', readonly: true, label: 'Field', bn: 'ফিল্ড' },
          { name: 'policy_class', readonly: true, label: 'Field Class', bn: 'ফিল্ডের শ্রেণি' },
          { name: 'local_value', readonly: true, label: 'Device Value', bn: 'ডিভাইসের মান' },
          { name: 'remote_value', readonly: true, label: 'Server Value', bn: 'সার্ভারের মান' },
          { name: 'engine_note', readonly: true, label: 'Engine Note', bn: 'ইঞ্জিনের নোট' },
          { name: 'resolution_note', readonly: true, label: 'Resolution Note', bn: 'নিষ্পত্তির নোট' }
        ] }
    ]
  }
};

SCREENS['M28-form-allowed-host'] = {
  kind: 'model_form',
  model: 'fix.integration.allowed.host',
  title: 'Allowed Host',
  back: 'M28-allowlist',
  status: { field: 'state', labels: { listed: 'Listed', removed: 'Removed' } },
  sections: [
    { title: 'Allowed Host', note: 'Listing a host lets webhooks and connectors send Company data to it, once dispatch is on. Each change is audited with your name and reason. A system administrator can also set the parameter directly: the list follows it hourly.',
      fields: [
        { name: 'host', required: true, label: 'Host (hooks.example.com or *.example.com)', bn: 'হোস্ট' },
        { name: 'reason', required: true, label: 'Why may this host receive data?', bn: 'এই হোস্ট কেন ডেটা পাবে?' }
      ] }
  ]
};

SCREENS['M28-form-suppression'] = {
  kind: 'model_form',
  model: 'fix.integration.reconciliation.suppression',
  title: 'Reconciliation Suppression',
  back: 'M28-suppressions',
  sections: [
    { title: 'Suppression', note: 'Holds back the alert of one check for a limited time, at most seven days unless a system administrator sets otherwise. It stops the alert, not the check: each night still records what disagrees. It takes effect only when a second person approves it, from their approvals inbox. No role can switch the reconciliation job off.',
      fields: [
        { name: 'check_code', required: true, label: 'Check', bn: 'যাচাই' },
        { name: 'reason', required: true, label: 'Reason', bn: 'কারণ' },
        { name: 'valid_until', required: true, label: 'Ends At', bn: 'শেষ হবে' }
      ] }
  ]
};

/* Offline Sync (FR-IPF-049, BRU-IPF-17): a conflict is raised by the sync
 * engine and never typed, so what a person captures here is the DECISION on
 * one. action_resolve_decision runs the same _resolve as the four row buttons
 * on Sync Conflicts: Integration Admin only, the field-class policy, the note
 * rules and the audit row all still decide. */
SCREENS['M28-form-conflict-resolve'] = {
  kind: 'model_form',
  model: 'fix.sync.conflict',
  title: 'Sync Conflict Decision', newLabel: 'Decide a Sync Conflict', back: 'M28-conflicts',
  pickRecord: {
    label: 'Step 1 of 2: choose the conflict you are deciding',
    note: 'Pending conflicts the offline sync engine raised: a device change that collided with the server record. Field Class says which side may win.',
    search: 'Search conflict / device / record',
    choose: 'Decide this conflict',
    cols: ['name', 'device_ref', 'res_model', 'res_id', 'field_name', 'policy_class', 'detected_at'],
    domain: [['resolution', '=', 'pending']],
    empty: 'No conflict is pending. The offline sync engine raises one when a technician, rider or auditor device sends a change over a newer server value.'
  },
  saveAction: {
    method: 'action_resolve_decision', label: 'Record Decision', done: 'Conflict decided and audited',
    kwargs: { decision: 'resolution', note: 'resolution_note' }
  },
  sections: [
    { title: 'Step 2 of 2: Decision', note: 'Server-class fields (assignment, pricing, stock, state) keep the server value: only Remote Wins is accepted. Client-class fields (notes, evidence, timestamps) may take the device value. A target outside the sync allow-list can only be closed with nothing applied. Manually Merged and Closed, Nothing Applied need a note. Only an Integration Admin can decide, and each decision is audited.',
      fields: [
        { name: 'device_ref', readonly: true, label: 'Device / Client', bn: 'ডিভাইস' },
        { name: 'res_model', readonly: true, label: 'Record Model', bn: 'রেকর্ড মডেল' },
        { name: 'res_id', readonly: true, label: 'Record ID', bn: 'রেকর্ড আইডি' },
        { name: 'field_name', readonly: true, label: 'Field', bn: 'ফিল্ড' },
        { name: 'policy_class', readonly: true, label: 'Field Class', bn: 'ফিল্ডের শ্রেণি' },
        { name: 'local_value', readonly: true, label: 'Device Value', bn: 'ডিভাইসের মান' },
        { name: 'remote_value', readonly: true, label: 'Server Value', bn: 'সার্ভারের মান' },
        { name: 'engine_note', readonly: true, label: 'Engine Note', bn: 'ইঞ্জিনের নোট' },
        /* inputs carried to action_resolve_decision; the generic write refuses them */
        { name: 'resolution', required: true, label: 'Decision', bn: 'সিদ্ধান্ত', type: 'selection',
          choices: [['local_wins', 'Local Wins'], ['remote_wins', 'Remote Wins'],
            ['merged', 'Manually Merged'], ['dismissed', 'Closed, Nothing Applied']] },
        { name: 'resolution_note', label: 'Note (required to merge or close)', bn: 'নোট' }
      ] }
  ]
};

/* Reconciliation (FR-IPF-052, BRU-IPF-19): the nightly job writes the runs; a
 * divergence "is investigated, never absorbed". The investigation is the
 * human record: pick an open divergence and say what was found and done. */
SCREENS['M28-form-recon-investigation'] = {
  kind: 'model_form',
  model: 'fix.integration.reconciliation.run',
  title: 'Reconciliation Investigation', newLabel: 'Record a Reconciliation Investigation', back: 'M28-reconciliation',
  status: { field: 'state', labels: { clean: 'Clean', divergent: 'Divergent', suppressed: 'Divergent, Alert Suppressed', not_run: 'Not Run' } },
  pickRecord: {
    label: 'Step 1 of 2: choose the divergence you investigated',
    note: 'Nightly runs that found a disagreement and have no investigation yet, suppressed ones included: a suppression holds back the alert, not the finding.',
    search: 'Search check',
    choose: 'Record the investigation',
    cols: ['run_at', 'check_code', 'records_compared', 'divergences_found', 'state', 'detail'],
    domain: [['state', 'in', ['divergent', 'suppressed']], ['resolved_at', '=', false]],
    empty: 'No open divergence. The nightly reconciliation compares the outbox, dead letters, webhook deliveries and offline sync; a disagreement lands here for investigation.'
  },
  saveAction: {
    method: 'action_resolve', label: 'Record Investigation', done: 'Investigation recorded; tomorrow\'s run checks it again',
    kwargs: { note: 'resolution_note' }
  },
  sections: [
    { title: 'Step 2 of 2: What Was Found and Done', note: 'Recording an investigation does not clear the finding: if the systems still disagree, the next nightly run says so. Only an Integration Admin can record one, and it is audited with your name.',
      fields: [
        { name: 'check_code', readonly: true, label: 'Check', bn: 'যাচাই' },
        { name: 'run_at', readonly: true, label: 'Run At', bn: 'চালানোর সময়' },
        { name: 'records_compared', readonly: true, label: 'Records Compared', bn: 'তুলনা করা রেকর্ড' },
        { name: 'divergences_found', readonly: true, label: 'Divergences Found', bn: 'অমিল' },
        { name: 'detail', readonly: true, label: 'Detail', bn: 'বিস্তারিত' },
        /* an input carried to action_resolve; the generic write refuses it */
        { name: 'resolution_note', required: true, label: 'What was found and done', bn: 'কী পাওয়া গেল ও কী করা হলো' }
      ] }
  ]
};

export const REPORT_ROUTES = {
  'M28:API Usage by Consumer': 'M28-rpt-usage',
  'M28:Event Delivery SLO': 'M28-rpt-slo',
  'M28:Connector Latency': 'M28-rpt-latency',
  'M28:DLQ Analysis': 'M28-rpt-dlq',
  'M28:Webhook Success Rate': 'M28-rpt-webhook'
};

export const FORM_MODELS = {
  'M28:API Consumer': 'fix.api.consumer',
  'M28:Event Subscription': 'fix.event.subscription',
  'M28:Connector Credential': 'fix.connector.credential',
  'M28:API Rate Limit': 'fix.api.quota',
  'M28:API Endpoint': 'fix.api.endpoint',
  'M28:Event Topic': 'fix.event.topic',
  'M28:Event Schema': 'fix.event.schema',
  'M28:Allowed Host': 'fix.integration.allowed.host',
  'M28:Connector': 'fix.connector',
  'M28:Sync Conflict Decision': 'fix.sync.conflict',
  'M28:Reconciliation Investigation': 'fix.integration.reconciliation.run',
  'M28:Reconciliation Suppression': 'fix.integration.reconciliation.suppression'
};

export const FORM_CHIPS = {
  'M28:API Consumer': 'M28-form-consumer',
  'M28:Event Subscription': 'M28-form-subscription',
  'M28:Connector Credential': 'M28-form-credential',
  'M28:API Rate Limit': 'M28-form-quota',
  'M28:API Endpoint': 'M28-form-endpoint',
  'M28:Event Topic': 'M28-form-topic',
  'M28:Event Schema': 'M28-form-schema',
  'M28:Allowed Host': 'M28-form-allowed-host',
  'M28:Connector': 'M28-form-connector',
  'M28:Sync Conflict Decision': 'M28-form-conflict-resolve',
  'M28:Reconciliation Investigation': 'M28-form-recon-investigation',
  'M28:Reconciliation Suppression': 'M28-form-suppression',
  'M28:__by_model__': {
    'fix.api.consumer': 'M28-form-consumer',
    'fix.event.subscription': 'M28-form-subscription',
    'fix.connector.credential': 'M28-form-credential',
    'fix.api.endpoint': 'M28-form-endpoint',
    'fix.api.quota': 'M28-form-quota',
    'fix.event.topic': 'M28-form-topic',
    'fix.event.schema': 'M28-form-schema',
    'fix.connector': 'M28-form-connector',
    'fix.sync.conflict': 'M28-form-conflict',
    'fix.integration.allowed.host': 'M28-form-allowed-host',
    'fix.integration.reconciliation.suppression': 'M28-form-suppression'
  },
  'M28:__by_screen__': {
    'M28-consumers': 'M28-form-consumer',
    'M28-topics': 'M28-form-topic',
    'M28-external': 'M28-form-connector',
    'M28-apis': 'M28-form-endpoint',
    'M28-quotas': 'M28-form-quota',
    'M28-schemas': 'M28-form-schema',
    'M28-conflicts': 'M28-form-conflict',
    'M28-subscriptions': 'M28-form-subscription',
    'M28-credentials': 'M28-form-credential',
    'M28-allowlist': 'M28-form-allowed-host',
    'M28-suppressions': 'M28-form-suppression'
  }
};

export const CREATE = {
  M28: { screen: 'M28-form-endpoint', model: 'fix.api.endpoint', label: 'API Endpoint' }
};
