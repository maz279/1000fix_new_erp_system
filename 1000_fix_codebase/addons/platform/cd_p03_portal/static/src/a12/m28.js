/** @odoo-module **/
/* A12 · Platform & Technology — M28 Integration, API & Events (full build).
 * Registry-faithful: 4 groups / 10 screens / 5 reports / 3 forms / freg 70.
 * Backend: cd_itsm/models/fix_integration.py (API catalogue, consumers/quotas,
 * topics/schemas/subscriptions/DLQ, connectors, credentials, sync conflicts,
 * integration log). */

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
    ]}
  ],
  reports: ['API Usage by Consumer', 'Event Delivery SLO', 'Connector Latency', 'DLQ Analysis', 'Webhook Success Rate'],
  forms: ['API Consumer', 'Event Subscription', 'Connector Credential'],
  cross: ['M29 credentials security', 'M63 automation triggers', 'M48 telemetry', 'M24 evidence'],
  freg: { src: 70, sub: [
    ['1', 'Gateway', 10, { model: 'fix.api.endpoint', cols: ['code', 'path', 'method', 'auth_type', 'active'], screens: ['M28-apis', 'M28-quotas'] }],
    ['2', 'Versioning & Portals', 6, { model: 'fix.api.endpoint', cols: ['code', 'name', 'version', 'path', 'active'], screens: ['M28-apis', 'M28-consumers'] }], // gitleaks:allow (screen ids, not a key)
    ['3', 'Outbox & Event Bus', 12, { model: 'fix.event.topic', cols: ['code', 'name', 'schema_id', 'retention_days', 'state'], screens: ['M28-topics', 'M28-schemas'] }],
    ['4', 'Subscriptions & DLQ', 9, { model: 'fix.event.dlq', cols: ['topic_code', 'reason', 'attempts', 'created_at', 'state'], screens: ['M28-dlq', 'M28-replay'] }],
    ['5', 'Webhooks', 5, { model: 'fix.event.subscription', cols: ['name', 'consumer_id', 'topic_id', 'endpoint_url', 'state'], screens: ['M28-topics', 'M28-consumers'] }],
    ['6', 'Connector Framework (47)', 12, { model: 'fix.connector', cols: ['name', 'connector_type', 'endpoint', 'last_latency_ms', 'state'], screens: ['M28-external', 'M28-health'] }],
    ['7', 'Offline Sync', 10, { model: 'fix.sync.conflict', cols: ['name', 'device_ref', 'res_model', 'detected_at', 'resolution'], screens: ['M28-offline', 'M28-conflicts'] }],
    ['8', 'Reconciliation', 6, { model: 'fix.sync.conflict', cols: ['res_model', 'res_id', 'field_name', 'local_value', 'remote_value'], screens: ['M28-conflicts', 'M28-health'] }]
  ] }
};

export const SCREENS = {
  'M28-apis': { kind: 'model_list', model: 'fix.api.endpoint',
    cols: ['code', 'version', 'path', 'method', 'auth_type', 'active'] },
  'M28-consumers': { kind: 'model_list', model: 'fix.api.consumer',
    cols: ['name', 'partner_id', 'key_ref', 'request_count', 'active'],
    actions: [{ m: 'action_rotate_key', l: 'Rotate Key Reference' }] },
  'M28-quotas': { kind: 'model_list', model: 'fix.api.quota', stateField: 'state',
    cols: ['consumer_id', 'endpoint_id', 'requests_per_min', 'daily_quota', 'state'] },
  'M28-topics': { kind: 'model_list', model: 'fix.event.topic', stateField: 'state',
    cols: ['code', 'name', 'schema_id', 'retention_days', 'state'],
    actions: [
      { m: 'action_pause', l: 'Pause' },
      { m: 'action_resume', l: 'Resume' }
    ] },
  'M28-schemas': { kind: 'model_list', model: 'fix.event.schema', stateField: 'state',
    cols: ['code', 'version', 'state'],
    actions: [{ m: 'action_publish', l: 'Publish Schema' }] },
  'M28-dlq': { kind: 'model_list', model: 'fix.event.dlq', stateField: 'state', create: false, // engine-raised: DLQ entries come from failed deliveries
    cols: ['display_label', 'topic_code', 'reason', 'attempts', 'created_at', 'state'],
    actions: [
      { m: 'action_replay', l: 'Replay' },
      { m: 'action_discard', l: 'Discard' }
    ] },
  'M28-replay': { kind: 'model_list', model: 'fix.event.dlq', stateField: 'state', create: false,
    cols: ['display_label', 'topic_code', 'reason', 'attempts', 'replayed_at', 'state'],
    domain: [['state', 'in', ['pending', 'replayed']]],
    actions: [
      { m: 'action_replay', l: 'Replay' },
      { m: 'action_discard', l: 'Discard' }
    ] },
  'M28-external': { kind: 'model_list', model: 'fix.connector', stateField: 'state',
    cols: ['name', 'connector_type', 'endpoint', 'credential_id', 'last_latency_ms', 'state'],
    actions: [
      { m: 'action_mark_degraded', l: 'Mark Degraded' },
      { m: 'action_mark_live', l: 'Mark Live' }
    ] },
  'M28-health': { kind: 'table_report', module: 'M28', report: 'connector_latency', title: 'Connector Health', period: false },
  'M28-offline': { kind: 'table_report', module: 'M28', report: 'dlq_analysis', title: 'Offline Sync Protocol', period: false },
  'M28-conflicts': { kind: 'model_list', model: 'fix.sync.conflict', stateField: 'resolution',
    cols: ['name', 'device_ref', 'res_model', 'res_id', 'field_name', 'local_value', 'remote_value', 'resolution'],
    actions: [
      { m: 'action_local_wins', l: 'Local Wins' },
      { m: 'action_remote_wins', l: 'Remote Wins' },
      { m: 'action_merged', l: 'Mark Merged' }
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
      { title: 'Endpoint', note: 'Code + version is unique per company. The auth type decides what the gateway enforces before the request reaches the service.',
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
      { title: 'Consumer', note: 'The key reference is a vault path - the key value itself never lands in this model (SEC-101). It changes only through the Rotate Key Reference action, which bumps the vault version and is audited. Request counts are measured from the log.',
        fields: [
          { name: 'name', required: true, label: 'Consumer Name' },
          { name: 'partner_id', label: 'Linked Partner' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },

  'M28-form-quota': {
    kind: 'model_form',
    model: 'fix.api.quota',
    title: 'Quota',
    back: 'M28-quotas',
    status: { field: 'state', labels: { active: 'Active', throttled: 'Throttled' } },
    sections: [
      { title: 'Rate Limit', note: 'Limits must be positive (database CHECK) and take effect on the next request — no pause/resume needed. Throttled is the gateway\'s measured verdict and changes only there.',
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
    back: 'M28-topics',
    status: { field: 'state', labels: { active: 'Active', paused: 'Paused', failing: 'Failing' } },
    tabs: [
      { id: 'binding', label: '1. Binding', bn: '১. বাইন্ডিং', icon: '🔗', badge: '3' },
      { id: 'secret', label: '2. Delivery Security', bn: '২. ডেলিভারি সিকিউরিটি', icon: '🔐', badge: '1' }
    ],
    sections: [
      { tab: 'binding', title: 'Subscription Binding', note: 'A webhook binding: every event on the topic is delivered to the consumer URL. The URL must be https and on the integration allow-list (fix.integration.webhook_allowlist).',
        fields: [
          { name: 'consumer_id', required: true, label: 'Consumer' },
          { name: 'topic_id', required: true, label: 'Topic' },
          { name: 'endpoint_url', required: true, label: 'Endpoint URL' }
        ] },
      { tab: 'secret', title: 'Delivery Security', note: 'The signing secret is referenced by vault:// alias only — the value itself never enters this model.',
        fields: [
          { name: 'secret_ref', required: true, label: 'Signing Secret Reference (vault://)' }
        ] }
    ]
  },

  'M28-form-credential': {
    kind: 'model_form',
    model: 'fix.connector.credential',
    title: 'Connector Credential',
    back: 'M28-external',
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
      { tab: 'secret', title: 'Vault Reference & Expiry', note: 'Rotation goes through the Rotate Key action, which versions the vault entry — never by editing the reference by hand.',
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
      { title: 'Topic', note: 'A topic carries one published schema; the retention days drive the bus purge policy (minimum 1 day). Pause/Resume are the topic\'s actions on the list.',
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
      { title: 'Schema', note: 'The JSON Schema payload contract. Draft → published; once published the code, version and contract are frozen - a correction ships as a NEW version (BRU-IPF-06).',
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
      { title: 'Connector', note: 'Live / degraded / down / disabled are health states measured by the platform (probe / circuit breaker); the mark actions are the operator\'s privileged override. Latency is the last recorded probe.',
        fields: [
          { name: 'name', required: true, label: 'Connector Name' },
          { name: 'connector_type', required: true, label: 'Type' },
          { name: 'endpoint', label: 'Endpoint' },
          { name: 'credential_id', label: 'Credential' }
        ] }
    ]
  },

  'M28-form-conflict': {
    kind: 'model_form',
    model: 'fix.sync.conflict',
    title: 'Sync Conflict',
    back: 'M28-conflicts',
    status: { field: 'resolution', labels: {
      pending: 'Pending', local_wins: 'Local Wins', remote_wins: 'Remote Wins',
      merged: 'Manually Merged' } },
    sections: [
      { title: 'Conflict', note: 'An offline edit that collided with the server record. The collided values are evidence - they change only through the resolution actions (local wins / remote wins / merged), which are privileged and audited.',
        fields: [
          { name: 'device_ref', required: true, label: 'Device / Client' },
          { name: 'res_model', required: true, label: 'Record Model' },
          { name: 'res_id', required: true, label: 'Record ID' },
          { name: 'field_name', required: true, label: 'Field' }
        ] }
    ]
  }
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
  'M28:Connector Credential': 'fix.connector.credential'
};

export const FORM_CHIPS = {
  'M28:API Consumer': 'M28-form-consumer',
  'M28:Event Subscription': 'M28-form-subscription',
  'M28:Connector Credential': 'M28-form-credential',
  'M28:__by_model__': {
    'fix.api.consumer': 'M28-form-consumer',
    'fix.event.subscription': 'M28-form-subscription',
    'fix.connector.credential': 'M28-form-credential',
    'fix.api.endpoint': 'M28-form-endpoint',
    'fix.api.quota': 'M28-form-quota',
    'fix.event.topic': 'M28-form-topic',
    'fix.event.schema': 'M28-form-schema',
    'fix.connector': 'M28-form-connector',
    'fix.sync.conflict': 'M28-form-conflict'
  },
  'M28:__by_screen__': {
    'M28-consumers': 'M28-form-consumer',
    'M28-topics': 'M28-form-topic',
    'M28-external': 'M28-form-connector',
    'M28-apis': 'M28-form-endpoint',
    'M28-quotas': 'M28-form-quota',
    'M28-schemas': 'M28-form-schema',
    'M28-conflicts': 'M28-form-conflict'
  }
};

export const CREATE = {
  M28: { screen: 'M28-form-endpoint', model: 'fix.api.endpoint', label: 'API Endpoint' }
};
