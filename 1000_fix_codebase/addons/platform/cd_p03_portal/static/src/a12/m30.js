/** @odoo-module **/
/* A12 · Platform & Technology — M30 Platform Administration.
 * Registry-faithful: 13 screens (model grids + packs) / 4 reports / 4 forms / freg 64. */

export const MODULE = {
  area: 'A12', code: 'M30', en: 'Platform Administration', title: 'M30 · Platform Administration',
  bn: 'প্ল্যাটফর্ম প্রশাসন', icon: '🛠️',
  desc: 'Branch registry and entity structure, configuration parameters with drift review, feature flag rollout, working calendars and holidays, zones and geofences, and platform announcements.',
  kpis: [
    { l: 'Branches Active', m: 'branches_active' },
    { l: 'Branches Total', m: 'branches' },
    { l: 'Flags Enabled', m: 'flags_on' },
    { l: 'Flags Total', m: 'flags_total' },
    { l: 'Announcements Live', m: 'announcements_live' }
  ],
  groups: [
    { en: 'Registry Completion', screens: [
      { id: 'M30-provisioning', en: 'Branch Provisioning (<1d)', bn: 'Branch Provisioning (<1d)', t: 'g' },
      { id: 'M30-params', en: 'Parameter Registry', bn: 'Parameter Registry', t: 'g' },
      { id: 'M30-jobs', en: 'Scheduled Job Registry', bn: 'Scheduled Job Registry', t: 'g' },
      { id: 'M30-health', en: 'Platform Health Console', bn: 'Platform Health Console', t: 'g' },
      { id: 'M30-env', en: 'Environments', bn: 'Environments', t: 'g' },
      { id: 'M30-backup', en: 'Backup & DR', bn: 'Backup & DR', t: 'g' },
      { id: 'M30-release', en: 'Release Coordination', bn: 'Release Coordination', t: 'g' }
    ]},
    { en: 'Structure', screens: [
      { id: 'M30-branches', en: 'Branch Register (53)', bn: 'শাখা রেজিস্টার', t: 'g' },
      { id: 'M30-entities', en: 'Legal Entities', bn: 'প্রতিষ্ঠান', t: 'g' },
      { id: 'M30-zones', en: 'Dispatch Zones', bn: 'জোন', t: 'g' },
      { id: 'M30-calendars', en: 'Calendars & Shifts', bn: 'ক্যালেন্ডার', t: 'g' }
    ]},
    { en: 'Configuration', screens: [
      { id: 'M30-config', en: 'Config Parameters', bn: 'কনফিগ', t: 'g' },
      { id: 'M30-flags', en: 'Feature Flags & Kill Switches', bn: 'ফিচার ফ্ল্যাগ', t: 'g' },
      { id: 'M30-drift', en: 'Config Drift Review', bn: 'ড্রিফট', t: 'r' }
    ]},
    { en: 'Comms', screens: [
      { id: 'M30-announcements', en: 'System Announcements', bn: 'ঘোষণা', t: 'g' },
      { id: 'M30-notif', en: 'Notification Config', bn: 'নোটিফিকেশন', t: 'g' }
    ]},
    { en: 'Approval Authority (DOFA)', bn: 'অনুমোদন কর্তৃত্ব', screens: [
      { id: 'M30-dofa-rulings', en: 'Open DOFA Rulings', bn: 'অমীমাংসিত অনুমোদন সিদ্ধান্ত', t: 'r' },
      { id: 'M30-dofa-ladders', en: 'Authority Ladders', bn: 'কর্তৃত্ব ল্যাডার', t: 'g' },
      { id: 'M30-form-dofa-ladder', en: 'Authority Ladder', bn: 'ল্যাডার ফর্ম', t: 'f' },
      { id: 'M30-dofa-bands', en: 'Ladder Bands', bn: 'ল্যাডার ব্যান্ড', t: 'g' }
    ]}
  ],
  reports: ['Branch Registry', 'Feature Flag Rollout', 'Config Parameter Inventory', 'Calendar Coverage'],
  forms: ['Branch', 'Config Parameter', 'Feature Flag', 'Announcement', 'Authority Ladder'],
  cross: ['M29 access', 'M04 branch ops', 'M55 attendance calendars', 'M65 entities'],
  freg: { src: 64, sub: [
    ['1', 'Branch Master', 12, { model: 'fix.branch', cols: ['code', 'name', 'entity_id', 'zone_id', 'active'], screens: ['M30-branches', 'M30-provisioning', 'M30-zones'] }],
    ['2', 'Entity Structure', 8, { model: 'fix.entity', cols: ['code', 'legal_name', 'legal_name_bn', 'branch_count', 'active'], screens: ['M30-entities', 'M30-env'] }],
    ['3', 'Config & Flags', 10, { model: 'fix.feature.flag', cols: ['key', 'name', 'enabled', 'scope', 'default_for_new'], screens: ['M30-flags', 'M30-config', 'M30-params', 'M30-jobs'] }],
    ['4', 'Calendars', 9, { model: 'fix.working.calendar', cols: ['name', 'branch_id', 'timezone', 'active'], screens: ['M30-calendars'] }],
    ['5', 'Announcements', 6, { model: 'fix.platform.announcement', cols: ['name', 'severity', 'audience', 'publish_on', 'state'], screens: ['M30-announcements', 'M30-notif'] }],
    ['6', 'Audit', 19, { model: 'fix.dofa.ladder', cols: ['name', 'target_model', 'in_force', 'ruled_by', 'ruled_at'], screens: ['M30-dofa-ladders', 'M30-dofa-rulings', 'M30-drift', 'M30-release'] }]
  ] }
};

export const SCREENS = {
  'M30-rpt-jobs': { kind: 'table_report', module: 'M30', report: 'job_success_rate',
    title: 'Job Success Rate', period: false },
  'M30-branches': { kind: 'model_list', model: 'fix.branch',
    cols: ['name', 'code', 'entity_id', 'zone_id', 'active'] },
  'M30-entities': { kind: 'model_list', model: 'fix.entity',
    cols: ['code', 'legal_name', 'legal_name_bn', 'active'] },
  'M30-zones': { kind: 'model_list', model: 'fix.zone',
    cols: ['code', 'name', 'name_bn', 'active'] },
  'M30-calendars': { kind: 'model_list', model: 'fix.working.calendar',
    cols: ['name', 'active'] },
  // Parameters are provisioned by platform administrators (deployment config,
  // not ad-hoc master data); this screen is a read-only inventory.
  'M30-config': { kind: 'model_list', model: 'ir.config_parameter', create: false,
    cols: ['key', 'create_date', 'write_date'] },
  'M30-flags': { kind: 'model_list', model: 'fix.feature.flag',
    cols: ['key', 'name', 'enabled', 'scope', 'default_for_new'] },
  'M30-drift': { kind: 'table_report', module: 'M30', report: 'config_drift', title: 'Config Drift Review', period: false },
  'M30-announcements': { kind: 'model_list', model: 'fix.platform.announcement', stateField: 'state',
    cols: ['name', 'severity', 'audience', 'publish_on', 'expires_on', 'state'],
    actions: [{ m: 'action_publish', l: 'Publish' }, { m: 'action_retire', l: 'Retire' }] },
  'M30-notif': { kind: 'model_list', model: 'fix.notification.config',
    cols: ['name', 'consent_class', 'channel', 'frequency_cap'] },

  /* Report chips */
  'M30-rpt-branches': { kind: 'table_report', module: 'M30', report: 'branch_registry', title: 'Branch Registry', period: false },
  'M30-rpt-flags': { kind: 'table_report', module: 'M30', report: 'flag_rollout', title: 'Feature Flag Rollout', period: false },
  'M30-rpt-calendar': { kind: 'table_report', module: 'M30', report: 'calendar_coverage', title: 'Calendar Coverage', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M30-form-branch': {
    kind: 'model_form',
    model: 'fix.branch',
    title: 'Branch',
    back: 'M30-branches',
    sections: [
      { title: 'Branch', note: 'The branch master every picker reads. The entity roll-up drives multi-entity reporting (M65).',
        fields: [
          { name: 'name', required: true, label: 'Branch Name' },
          { name: 'code', required: true, label: 'Branch Code' },
          { name: 'entity_id', required: true, label: 'Legal Entity' },
          { name: 'zone_id', label: 'Zone' },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },

  'M30-form-flag': {
    kind: 'model_form',
    model: 'fix.feature.flag',
    title: 'Feature Flag',
    back: 'M30-flags',
    sections: [
      { title: 'Feature Flag', note: 'The key gates the feature; scope decides who evaluates it. Enabled flags are live immediately.',
        fields: [
          { name: 'key', required: true, label: 'Flag Key' },
          { name: 'name', required: true, label: 'Description' },
          { name: 'enabled', label: 'Enabled' },
          { name: 'scope', required: true, label: 'Scope' },
          { name: 'default_for_new', label: 'Default for New Branches' }
        ] }
    ]
  },

  'M30-form-announcement': {
    kind: 'model_form',
    model: 'fix.platform.announcement',
    title: 'Announcement',
    back: 'M30-announcements',
    status: { field: 'state', labels: { draft: 'Draft', published: 'Published', retired: 'Retired' } },
    sections: [
      { title: 'Announcement', note: 'Draft → published → retired. Publishing is the action button on the list screen — the state is never typed in (an announcement is published by decision, not by save). The expiry date retires it from the live count automatically.',
        fields: [
          { name: 'name', required: true, label: 'Title' },
          { name: 'severity', required: true, label: 'Severity' },
          { name: 'audience', required: true, label: 'Audience' },
          { name: 'publish_on', required: true, label: 'Publish On' },
          { name: 'expires_on', label: 'Expires On' }
        ] },
      { title: 'Body', fields: [
          { name: 'body', type: 'text', label: 'Message' }
        ] }
    ]
  },

  'M30-form-entity': {
    kind: 'model_form',
    model: 'fix.entity',
    title: 'Legal Entity',
    back: 'M30-entities',
    sections: [
      { title: 'Entity', note: 'A legal company of the group; branches roll up to entities.',
        fields: [
          { name: 'code', required: true, label: 'Entity Code' },
          { name: 'legal_name', required: true, label: 'Legal Name' },
          { name: 'legal_name_bn', label: 'Legal Name (Bengali)' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },

  'M30-form-calendar': {
    kind: 'model_form',
    model: 'fix.working.calendar',
    title: 'Working Calendar',
    back: 'M30-calendars',
    sections: [
      { title: 'Calendar', note: 'Working lines and holidays are held on the calendar; attendance, SLA and payroll windows read it.',
        fields: [
          { name: 'name', required: true, label: 'Calendar Name' },
          { name: 'template_id', label: 'Template' },
          { name: 'branch_id', label: 'Branch' },
          { name: 'timezone', label: 'Timezone' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },

  'M30-form-notif': {
    kind: 'model_form',
    model: 'fix.notification.config',
    title: 'Notification Configuration',
    back: 'M30-notif',
    sections: [
      { title: 'Consent & Channel', note: 'One configuration per consent class and channel; the frequency cap is enforced on send.',
        fields: [
          { name: 'consent_class', required: true, label: 'Consent Class' },
          { name: 'channel', required: true, label: 'Channel' },
          { name: 'send_window', label: 'Send Window' },
          { name: 'frequency_cap', label: 'Frequency Cap' },
          { name: 'combined_cap_non_transactional', label: 'Combined Cap (Non-Transactional)' },
          { name: 'sms_route', label: 'SMS Route' },
          { name: 'stale_discard_hours', label: 'Stale Discard (hours)' }
        ] }
    ]
  },

  'M30-form-zone': {
    kind: 'model_form',
    model: 'fix.zone',
    title: 'Zone',
    back: 'M30-zones',
    sections: [
      { title: 'Zone', note: 'Service zones group branches for logistics and coverage.',
        fields: [
          { name: 'code', required: true, label: 'Zone Code' },
          { name: 'name', required: true, label: 'Zone Name' },
          { name: 'name_bn', label: 'Zone Name (Bengali)' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },

  /* registry completion screens */
  'M30-provisioning': { kind: 'table_report', module: 'M30', report: 'branch_provisioning', title: 'Branch Provisioning (<1d)', period: false },
  'M30-params': { kind: 'model_list', model: 'ir.config_parameter', create: false, cols: ['key', 'create_date', 'write_date'] },
  'M30-jobs': { kind: 'model_list', model: 'ir.cron', create: false, cols: ['name', 'active', 'interval_number', 'nextcall'] },
  'M30-health': { kind: 'table_report', module: 'M30', report: 'platform_health', title: 'Platform Health Console', period: false },
  'M30-env': { kind: 'model_list', model: 'fix.platform.environment', stateField: 'state', cols: ['name', 'kind', 'base_url', 'release_channel', 'data_residency', 'state'] },
  'M30-backup': { kind: 'model_list', model: 'fix.data.backup.plan', create: false, cols: ['name', 'state'] },
  'M30-release': { kind: 'model_list', model: 'fix.platform.release', stateField: 'state', cols: ['version', 'name', 'environment_id', 'planned_on', 'released_on', 'state'], actions: [{ m: 'action_release', l: 'Release' }] },


  /* ===== registry completion forms ===== */
  'M30-form-env': {
    kind: 'model_form',
    model: 'fix.platform.environment',
    title: "Environment",
    back: 'M30-env',
    status: { field: 'state', labels: { provisioning: "Provisioning", live: "Live", degraded: "Degraded", offline: "Offline" } },
    sections: [
      { title: "Environment", note: "Each environment states its URL, database, release channel and data residency. Production and DR are separate rows, not labels. The state column is operational fact (badge only) — an environment goes live through provisioning, not a form save.",
        fields: [
          { name: 'name', required: true, label: "Environment Name" },
          { name: 'kind', required: true, label: "Kind" },
          { name: 'base_url', required: true, label: "Base URL" },
          { name: 'database_name', label: "Database" },
          { name: 'release_channel', required: true, label: "Release Channel" },
          { name: 'data_residency', label: "Data Residency" },
          { name: 'owner_id', label: "Owner" },
          { name: 'notes', type: 'text', label: "Notes" }
        ] }
    ]
  },
  'M30-form-release': {
    kind: 'model_form',
    model: 'fix.platform.release',
    title: "Release",
    back: 'M30-release',
    status: { field: 'state', labels: { planned: "Planned", in_test: "In Test", released: "Released", rolled_back: "Rolled Back" } },
    sections: [
      { title: "Release", note: "Releasing is the action on the list screen and requires the rollback plan and the linked approved change first — the model refuses otherwise. The state badge is fact, not a field.",
        fields: [
          { name: 'version', required: true, readonly: true, label: "Version" },
          { name: 'name', required: true, readonly: true, label: "Release Name" },
          { name: 'environment_id', readonly: true, label: "Target Environment" },
          { name: 'planned_on', required: true, label: "Planned On" },
          { name: 'owner_id', readonly: true, label: "Release Owner" },
          { name: 'itsm_change_id', label: "Approved Change (M66)" },
          { name: 'rollback_plan', type: 'text', label: "Rollback Plan" }
        ] }
    ]
  },


  /* ==================================================================
   * Approval authority (DOFA) — the ladders as governed configuration.
   * Putting one in force IS the ruling, which is why it needs a stated
   * authority and is tracked on the record.
   * ================================================================== */
  'M30-dofa-rulings': { kind: 'table_report', module: 'M30', report: 'open_dofa_rulings',
    title: 'Open DOFA Rulings', period: false },
  'M30-dofa-coverage': { kind: 'table_report', module: 'M30', report: 'dofa_coverage',
    title: 'DOFA Coverage (one DoA)', period: false },
  'M30-dofa-ladders': { kind: 'model_list', model: 'fix.dofa.ladder', create: true,
    cols: ['target_model', 'name', 'basis', 'matches_implementation', 'in_force', 'ruled_by', 'ruled_at', 'ruling_reference'],
    actions: [
      { m: 'action_put_in_force', l: 'Put In Force (ruling)',
        ask: 'Ruling reference (minute / memo number)', kwarg: 'reference' }
    ],
    note: 'Exactly one ladder per model may be in force. With none in force the model keeps its own coded default, so behaviour is unchanged until somebody rules. Ruling needs a stated authority and TWO different authority holders (acting + countersigning, Tier 4 and Tier 5).' },
  'M30-dofa-bands': { kind: 'model_list', model: 'fix.dofa.threshold', create: true,
    cols: ['ladder_id', 'upper_bound', 'tier', 'note'],
    note: 'Each band is an inclusive upper bound and the tier that applies at or below it.' },
  'M30-form-dofa-ladder': {
    lines: {
      field: 'threshold_ids',
      title: 'Authority Bands',
      note: 'Ascending by bound; the highest band is the ceiling tier applied above every bound.',
      fields: [
        { name: 'upper_bound', label: 'Up To (inclusive)', required: true },
        { name: 'tier', label: 'Tier Required', required: true },
        { name: 'note', label: 'Note' }
      ]
    },
    kind: 'model_form', model: 'fix.dofa.ladder',
    title: 'DOFA Authority Ladder', back: 'M30-dofa-ladders',
    status: { field: 'in_force', labels: { true: 'In Force', false: 'Not in force' } },
    tabs: [
      { id: 'identity', label: '1. Ladder', bn: '১. ল্যাডার', icon: '⚖️' },
      { id: 'ruling', label: '2. Ruling', bn: '২. সিদ্ধান্ত', icon: '✍️' }
    ],
    sections: [
      {
        tab: 'identity',
        title: 'Which Authority This Governs',
        note: 'The basis records WHERE the bands come from. Keeping both the specification prose and the authority matrix on file is the point: the conflict between them is a fact about the specification and belongs on a screen, not in a source comment.',
        fields: [
          { name: 'name', label: 'Ladder Name', required: true },
          { name: 'target_model', label: 'Governs Model', required: true },
          { name: 'basis', label: 'Basis', required: true },
          { name: 'matches_implementation', label: 'Matches Current Code (fact, not a ruling)' }
        ]
      },
      {
        tab: 'ruling',
        title: 'The Ruling',
        note: 'Putting a ladder in force changes who may approve what. The ruling itself is made by the Put In Force action on the ladders screen — it asks for the authorising minute or memo, needs two different authority holders (Tier 4 acting, Tier 5 in the pair, the countersigner recorded here), and stamps who ruled and when. Nothing on this tab is typed in.',
        fields: [
          { name: 'countersigned_by', label: 'Countersigning Authority' },
          { name: 'ruling_reference', readonly: true, label: 'Authority (minute / memo)' },
          { name: 'ruled_by', readonly: true, label: 'Ruled By' },
          { name: 'ruled_at', readonly: true, label: 'Ruled At' }
        ]
      }
    ]
  },
};

export const REPORT_ROUTES = {
  open_dofa_rulings: 'open_dofa_rulings',
  'DOFA Coverage': 'M30-dofa-coverage',
  'M30:Config Change Log': 'M30-drift',
  'M30:Job Success Rate': 'M30-rpt-jobs',
  'M30:Environment Inventory': 'M30-env',
  'M30:Branch Provisioning Time': 'M30-provisioning',
  'M30:Branch Registry': 'M30-rpt-branches',
  'M30:Feature Flag Rollout': 'M30-rpt-flags',
  'M30:Config Parameter Inventory': 'M30-drift',
  'M30:Calendar Coverage': 'M30-rpt-calendar'
};

export const FORM_MODELS = {
  'M30:Authority Ladder': 'fix.dofa.ladder',
  'M30:Branch': 'fix.branch',
  'M30:Config Parameter': 'ir.config_parameter',
  'M30:Feature Flag': 'fix.feature.flag',
  'M30:Announcement': 'fix.platform.announcement'
};

export const FORM_CHIPS = {
  'M30:Authority Ladder': 'M30-form-dofa-ladder',
  'M30:Branch': 'M30-form-branch',
  'M30:Config Parameter': 'M30-form-config',
  'M30:Feature Flag': 'M30-form-flag',
  'M30:Announcement': 'M30-form-announcement',
  'M30:__by_model__': {
    'fix.platform.environment': 'M30-form-env',
    'fix.platform.release': 'M30-form-release',
    'fix.branch': 'M30-form-branch',
    'fix.feature.flag': 'M30-form-flag',
    'fix.platform.announcement': 'M30-form-announcement',
    'fix.entity': 'M30-form-entity',
    'fix.zone': 'M30-form-zone',
    'fix.working.calendar': 'M30-form-calendar',
    'fix.notification.config': 'M30-form-notif'
  },
  'M30:__by_screen__': {
    'M30-env': 'M30-form-env',
    'M30-release': 'M30-form-release',
    'M30-branches': 'M30-form-branch',
    'M30-flags': 'M30-form-flag',
    'M30-announcements': 'M30-form-announcement',
    'M30-entities': 'M30-form-entity',
    'M30-zones': 'M30-form-zone',
    'M30-calendars': 'M30-form-calendar',
    'M30-notif': 'M30-form-notif'
  }
};

export const CREATE = {
  M30: { screen: 'M30-form-branch', model: 'fix.branch', label: 'Branch' }
};
