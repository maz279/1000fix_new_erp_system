/** @odoo-module **/
/* A12 · Platform & Technology — M30 Platform Administration.
 * Registry-faithful: 13 screens (model grids + packs) / 4 reports / 4 forms / freg 64. */

export const MODULE = {
  area: 'A12', code: 'M30', en: 'Platform Administration', title: 'M30 · Platform Administration',
  bn: 'প্ল্যাটফর্ম প্রশাসন', icon: '🛠️',
  desc: 'Branch registry and entity structure, configuration parameter and job inventories, feature flag rollout, working calendars and holidays, zones, and platform announcements. The config and job screens are inventories: no config registry, promotion or job registry is built yet.',
  kpis: [
    { l: 'Rulings Awaiting Countersignature', m: 'dofa_awaiting_countersign' },
    { l: 'Branches Active', m: 'branches_active' },
    { l: 'Branches Total', m: 'branches' },
    { l: 'Flags Enabled', m: 'flags_on' },
    { l: 'Flags Total', m: 'flags_total' },
    { l: 'Announcements Live', m: 'announcements_live' }
  ],
  groups: [
    { en: 'Registry Completion', screens: [
      { id: 'M30-provisioning', en: 'Branch Provisioning (<1d)', bn: 'Branch Provisioning (<1d)', t: 'g' },
      { id: 'M30-params', en: 'Parameter Registry (Inventory Only)', bn: 'Parameter Registry', t: 'g' },
      { id: 'M30-jobs', en: 'Scheduled Job Registry (Inventory Only)', bn: 'Scheduled Job Registry', t: 'g' },
      { id: 'M30-health', en: 'Platform Health Console', bn: 'Platform Health Console', t: 'g' },
      { id: 'M30-env', en: 'Environments', bn: 'Environments', t: 'g' },
      { id: 'M30-backup', en: 'Backup & DR (Customer Plans)', bn: 'Backup & DR', t: 'g' },
      { id: 'M30-release', en: 'Release Coordination', bn: 'Release Coordination', t: 'g' }
    ]},
    { en: 'Structure', screens: [
      { id: 'M30-branches', en: 'Branch Register (53)', bn: 'শাখা রেজিস্টার', t: 'g' },
      { id: 'M30-entities', en: 'Legal Entities', bn: 'প্রতিষ্ঠান', t: 'g' },
      { id: 'M30-zones', en: 'Dispatch Zones', bn: 'জোন', t: 'g' },
      { id: 'M30-calendars', en: 'Calendars & Shifts', bn: 'ক্যালেন্ডার', t: 'g' },
      { id: 'M30-calendar-holidays', en: 'Calendar Holidays', bn: 'ক্যালেন্ডার ছুটি', t: 'g' }
    ]},
    { en: 'Configuration', screens: [
      { id: 'M30-config', en: 'Config Parameters (Inventory Only)', bn: 'কনফিগ', t: 'g' },
      { id: 'M30-flags', en: 'Feature Flags & Kill Switches', bn: 'ফিচার ফ্ল্যাগ', t: 'g' },
      { id: 'M30-drift', en: 'Config Drift Review (Inventory, No Drift Computed)', bn: 'ড্রিফট', t: 'r' }
    ]},
    { en: 'Comms', screens: [
      { id: 'M30-announcements', en: 'System Announcements', bn: 'ঘোষণা', t: 'g' },
      { id: 'M30-notif', en: 'Notification Config (Policy Record)', bn: 'নোটিফিকেশন', t: 'g' }
    ]},
    { en: 'Approval Authority (DOFA)', bn: 'অনুমোদন কর্তৃত্ব', screens: [
      { id: 'M30-dofa-rulings', en: 'Open DOFA Rulings', bn: 'অমীমাংসিত অনুমোদন সিদ্ধান্ত', t: 'r' },
      { id: 'M30-dofa-ladders', en: 'Authority Ladders', bn: 'কর্তৃত্ব ল্যাডার', t: 'g' },
      { id: 'M30-form-dofa-ladder', en: 'Authority Ladder', bn: 'ল্যাডার ফর্ম', t: 'f' },
      { id: 'M30-dofa-bands', en: 'Ladder Bands', bn: 'ল্যাডার ব্যান্ড', t: 'g' }
    ]}
  ],
  reports: ['Branch Registry', 'Feature Flag Rollout', 'Config Parameter Inventory', 'Calendar Coverage', 'DOFA Coverage'],
  forms: ['Branch', 'Feature Flag', 'Announcement', 'Authority Ladder'],
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
  'M30-branches': { kind: 'model_list', model: 'fix.branch', stateField: 'state',
    cols: ['name', 'code', 'entity_id', 'zone_id', 'manager_id', 'state', 'active'],
    actions: [
      { m: 'action_go_live', l: 'Go Live' },
      { m: 'action_suspend', l: 'Suspend', ask: 'Why is this branch being suspended?', kwarg: 'reason' },
      { m: 'action_request_closure', l: 'Request Closure', ask: 'Why is this branch closing? A second Platform Admin must confirm.', kwarg: 'reason' },
      { m: 'action_confirm_closure', l: 'Confirm Closure (second person)' }
    ] },
  'M30-entities': { kind: 'model_list', model: 'fix.entity',
    cols: ['code', 'legal_name', 'legal_name_bn', 'active'] },
  'M30-zones': { kind: 'model_list', model: 'fix.zone',
    cols: ['code', 'name', 'name_bn', 'active'] },
  'M30-calendars': { kind: 'model_list', model: 'fix.working.calendar',
    cols: ['name', 'branch_id', 'pending_closure_name', 'pending_closure_from', 'pending_closure_to', 'active'],
    actions: [
      { m: 'action_propose_closure', l: 'Propose Long Closure',
        asks: [{ label: 'Closure name', kwarg: 'name' }, { label: 'First day (YYYY-MM-DD)', kwarg: 'date_from' }, { label: 'Last day (YYYY-MM-DD)', kwarg: 'date_to' }] },
      { m: 'action_confirm_closure', l: 'Confirm Closure (second person)' }
    ] },
  'M30-calendar-holidays': { kind: 'model_list', model: 'fix.working.calendar.holiday',
    cols: ['calendar_id', 'name', 'name_bn', 'date_from', 'date_to', 'pack_line_id'] },
  // Parameters are provisioned by platform administrators (deployment config,
  // not ad-hoc master data); this screen is a read-only inventory.
  'M30-config': { kind: 'model_list', model: 'ir.config_parameter', create: false,
    cols: ['key', 'create_date', 'write_date'] },
  'M30-flags': { kind: 'model_list', model: 'fix.feature.flag',
    cols: ['key', 'name', 'enabled', 'scope', 'default_for_new'] },
  'M30-drift': { kind: 'table_report', module: 'M30', report: 'config_drift', title: 'Config Drift Review', period: false },
  'M30-announcements': { kind: 'model_list', model: 'fix.platform.announcement', stateField: 'state',
    cols: ['name', 'kind', 'severity', 'audience', 'publish_on', 'expires_on', 'published_by_id', 'acknowledged_count', 'acknowledged_by_me', 'state'],
    actions: [{ m: 'action_publish', l: 'Publish (second person)' }, { m: 'action_retire', l: 'Retire' }, { m: 'action_acknowledge', l: 'Acknowledge' }] },
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
    status: { field: 'state', labels: { provisioning: 'Provisioning', live: 'Live', suspended: 'Suspended', closed: 'Closed' } },
    sections: [
      { title: 'Branch', note: 'The branch master every picker reads. The entity roll-up drives multi-entity reporting (M65). A branch moves through Go Live, Suspend and a two-person closure on the list screen; it is never closed by a toggle.',
        fields: [
          { name: 'name', required: true, label: 'Branch Name' },
          { name: 'name_bn', label: 'Branch Name (Bengali)' },
          { name: 'code', required: true, label: 'Branch Code' },
          { name: 'entity_id', required: true, label: 'Legal Entity' },
          { name: 'operating_unit_id', required: true, label: 'Operating Unit' },
          { name: 'zone_id', label: 'Zone' },
          { name: 'address_id', label: 'Address' }
        ] },
      { title: 'Contact & Calendar', note: 'The working calendar is what SLA clocks resolve through. Manager and calendar changes leave an audit row, and you cannot appoint yourself manager.',
        fields: [
          { name: 'manager_id', label: 'Branch Manager' },
          { name: 'calendar_id', label: 'Working Calendar' },
          { name: 'phone', label: 'Phone' },
          { name: 'email', label: 'Email' }
        ] }
    ]
  },

  'M30-form-flag': {
    kind: 'model_form',
    model: 'fix.feature.flag',
    title: 'Feature Flag',
    back: 'M30-flags',
    sections: [
      { title: 'Feature Flag', note: 'The key gates the feature; scope decides who evaluates it. Enabled flags are live immediately. Only a key the code really reads can be registered, and today that is one kill switch: new capabilities do not yet ship behind flags. Enabled Branches applies only to the Per Branch scope.',
        fields: [
          { name: 'key', required: true, label: 'Flag Key' },
          { name: 'name', required: true, label: 'Description' },
          { name: 'enabled', label: 'Enabled' },
          { name: 'scope', required: true, label: 'Scope' },
          { name: 'branch_ids', label: 'Enabled Branches' },
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
      { title: 'Announcement', note: 'Draft → published → retired. A second Platform Admin publishes from the list screen: the author cannot. Planned maintenance needs its start time and 72 hours of lead. Users acknowledge on the list screen; that screen is the only place an announcement appears, because no banner pushes it to other screens.',
        fields: [
          { name: 'name', required: true, label: 'Title' },
          { name: 'kind', required: true, label: 'Kind' },
          { name: 'severity', required: true, label: 'Severity' },
          { name: 'audience', required: true, label: 'Audience' },
          { name: 'publish_on', required: true, label: 'Publish On' },
          { name: 'expires_on', label: 'Expires On' },
          { name: 'maintenance_start', label: 'Maintenance Starts' }
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
    tabs: [
      { id: 'identity', label: '1. Entity', bn: '১. প্রতিষ্ঠান', icon: '🏢' },
      { id: 'statutory', label: '2. Statutory', bn: '২. বিধিবদ্ধ', icon: '📜' }
    ],
    sections: [
      { tab: 'identity', title: 'Entity', note: 'A legal company of the group; branches roll up to entities. The company is set when the entity is created and cannot then be moved.',
        fields: [
          { name: 'code', required: true, label: 'Entity Code' },
          { name: 'legal_name', required: true, label: 'Legal Name' },
          { name: 'legal_name_bn', label: 'Legal Name (Bengali)' },
          { name: 'company_id', required: true, label: 'Company' },
          { name: 'operating_unit_id', label: 'Primary Operating Unit' },
          { name: 'country_id', required: true, label: 'Country' },
          { name: 'currency_id', label: 'Currency' },
          { name: 'active', label: 'Active' }
        ] },
      { tab: 'statutory', title: 'Statutory Registration', note: 'Record the real NBR registrations: the format is checked, whether a number is genuine is not. Changing the VAT due day or calendar rule moves a statutory date, so it also needs a finance manager. Every change here is tracked and audited.',
        fields: [
          { name: 'bin_number', label: 'BIN (13 digits)' },
          { name: 'tin_number', label: 'e-TIN (12 digits)' },
          { name: 'vat_statutory_day', label: 'VAT Due Day of Month' },
          { name: 'statutory_calendar_rule', required: true, label: 'Tax Calendar Rule' },
          { name: 'incorporation_date', label: 'Incorporation Date' }
        ] }
    ]
  },

  'M30-form-calendar': {
    kind: 'model_form',
    model: 'fix.working.calendar',
    title: 'Working Calendar',
    back: 'M30-calendars',
    lines: {
      field: 'line_ids',
      title: 'Working Hours',
      note: 'One window per weekday, local Dhaka time. Every change leaves an audit row.',
      fields: [
        { name: 'weekday', label: 'Weekday', required: true },
        { name: 'hour_from', label: 'From (hour)', required: true },
        { name: 'hour_to', label: 'To (hour)', required: true }
      ]
    },
    sections: [
      { title: 'Calendar', note: 'Attendance, SLA and payroll windows read this calendar. Holidays are on the Calendar Holidays screen; a closure longer than the direct limit is proposed here on the list screen and confirmed by a second Platform Admin.',
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
      { title: 'Consent & Channel', note: 'One configuration per consent class and channel. This register records the NT-003 policy and keeps it consistent (class window, caps, BD-02 route). The notification dispatcher reads its own registry file, not this screen, so a change here does not by itself change what is sent.',
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
          { name: 'description', label: 'Description' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },

  /* registry completion screens */
  'M30-provisioning': { kind: 'table_report', module: 'M30', report: 'branch_provisioning', title: 'Branch Provisioning (<1d)', period: false },
  'M30-params': { kind: 'model_list', model: 'ir.config_parameter', create: false, cols: ['key', 'create_date', 'write_date'] },
  'M30-jobs': { kind: 'model_list', model: 'ir.cron', create: false, cols: ['name', 'active', 'interval_number', 'nextcall'] },
  'M30-health': { kind: 'table_report', module: 'M30', report: 'platform_health', title: 'Platform Health Console', period: false },
  'M30-env': { kind: 'model_list', model: 'fix.platform.environment', stateField: 'state', cols: ['name', 'kind', 'base_url', 'release_channel', 'data_residency', 'masking_state', 'state'],
    actions: [
      { m: 'action_go_live', l: 'Go Live' },
      { m: 'action_mark_degraded', l: 'Mark Degraded', ask: 'What is degraded?', kwarg: 'reason' },
      { m: 'action_take_offline', l: 'Take Offline', ask: 'Why is this environment going offline?', kwarg: 'reason' },
      { m: 'action_record_masking', l: 'Record Masking Evidence', ask: 'The run, ticket or report that shows personal data is masked', kwarg: 'evidence' }
    ] },
  'M30-backup': { kind: 'model_list', model: 'fix.data.backup.plan', create: false, cols: ['name', 'customer_id', 'plan_type', 'rpo_hours', 'rto_hours'] },
  'M30-release': { kind: 'model_list', model: 'fix.platform.release', stateField: 'state', cols: ['version', 'name', 'environment_id', 'itsm_change_id', 'planned_on', 'released_on', 'released_by_id', 'state'],
    actions: [
      { m: 'action_start_test', l: 'Start Test' },
      { m: 'action_release', l: 'Release (second person)' },
      { m: 'action_rollback', l: 'Roll Back', ask: 'Why is this release being rolled back?', kwarg: 'reason' }
    ] },


  /* ===== registry completion forms ===== */
  'M30-form-env': {
    kind: 'model_form',
    model: 'fix.platform.environment',
    title: "Environment",
    back: 'M30-env',
    status: { field: 'state', labels: { provisioning: "Provisioning", live: "Live", degraded: "Degraded", offline: "Offline" } },
    sections: [
      { title: "Environment", note: "Each environment states its URL, database, release channel and data residency. Production and DR are separate rows, not labels. A new environment starts in Provisioning and moves through the actions on the list screen. A dev or staging copy goes live only after a second person records masking evidence; this system records that statement and does not inspect the data.",
        fields: [
          { name: 'name', required: true, label: "Environment Name" },
          { name: 'kind', required: true, label: "Kind" },
          { name: 'base_url', required: true, label: "Base URL" },
          { name: 'database_name', label: "Database" },
          { name: 'release_channel', required: true, label: "Release Channel" },
          { name: 'data_residency', label: "Data Residency" },
          { name: 'owner_id', label: "Owner" },
          { name: 'notes', type: 'text', label: "Notes" },
          { name: 'masking_state', readonly: true, label: "Data Masking" },
          { name: 'masking_evidence', readonly: true, label: "Masking Evidence" },
          { name: 'masking_recorded_by_id', readonly: true, label: "Evidence Recorded By" }
        ] }
    ]
  },
  'M30-form-holiday': {
    kind: 'model_form',
    model: 'fix.working.calendar.holiday',
    title: 'Calendar Holiday',
    back: 'M30-calendar-holidays',
    sections: [
      { title: 'Holiday', note: 'A holiday stops the SLA clock, so each change leaves an audit row. A closure longer than the direct limit (default 3 days) is refused here: propose it on the calendar and a second Platform Admin confirms it. National holidays come from a certified country pack.',
        fields: [
          { name: 'calendar_id', required: true, label: 'Calendar' },
          { name: 'name', required: true, label: 'Holiday' },
          { name: 'name_bn', label: 'Holiday (Bengali)' },
          { name: 'date_from', required: true, label: 'From' },
          { name: 'date_to', required: true, label: 'To' }
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
      { title: "Release", note: "Releasing is the action on the list screen. It needs a target environment, the rollback plan and an approved change that has not shipped in another release, and a person other than the creator or owner presses it. Once released, this record is frozen.",
        fields: [
          { name: 'version', required: true, label: "Version" },
          { name: 'name', required: true, label: "Release Name" },
          { name: 'environment_id', label: "Target Environment" },
          { name: 'planned_on', required: true, label: "Planned On" },
          { name: 'owner_id', label: "Release Owner" },
          { name: 'itsm_change_id', label: "Approved Change (M66)" },
          { name: 'change_summary', type: 'text', label: "Change Summary" },
          { name: 'rollback_plan', type: 'text', label: "Rollback Plan" },
          { name: 'released_by_id', readonly: true, label: "Released By" },
          { name: 'rolled_back_reason', readonly: true, label: "Rollback Reason" }
        ] }
    ]
  },


  /* ==================================================================
   * Approval authority (DOFA) — the ladders as governed configuration.
   * A ruling is two acts by two people: a Tier 4 holder proposes, the named
   * Tier 5 holder countersigns. Only the countersignature puts it in force.
   * ================================================================== */
  'M30-dofa-rulings': { kind: 'table_report', module: 'M30', report: 'open_dofa_rulings',
    title: 'Open DOFA Rulings', period: false },
  'M30-dofa-coverage': { kind: 'table_report', module: 'M30', report: 'dofa_coverage',
    title: 'DOFA Coverage (one DoA)', period: false },
  'M30-dofa-ladders': { kind: 'model_list', model: 'fix.dofa.ladder', create: true, stateField: 'ruling_state',
    cols: ['target_model', 'name', 'basis', 'version', 'matches_implementation', 'ruling_state', 'proposed_by', 'countersigned_by', 'ruled_by', 'ruled_at', 'ruling_reference', 'proposed_reference'],
    actions: [
      { m: 'action_propose_ruling', l: 'Propose Ruling (Tier 4)',
        ask: 'Ruling reference (minute / memo number). Choose the countersigner on the ladder form first.', kwarg: 'reference' },
      { m: 'action_countersign', l: 'Countersign (named Tier 5)',
        ask: 'Ruling reference: restate exactly what was proposed', kwarg: 'reference' },
      { m: 'action_withdraw_ruling', l: 'Withdraw / Decline', ask: 'Why is this proposal being withdrawn?', kwarg: 'reason' }
    ],
    note: 'Exactly one ladder per model may be in force. With none in force the model keeps its own coded default, so behaviour is unchanged until somebody rules. A ruling is a Tier 4 proposal plus a Tier 5 countersignature, by two different people, each from their own session.' },
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
    status: { field: 'ruling_state', labels: { draft: 'Draft', proposed: 'Awaiting Countersignature', in_force: 'In Force', superseded: 'Superseded' } },
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
          { name: 'version', readonly: true, label: 'Version' },
          { name: 'matches_implementation', label: 'Matches Current Code (fact, not a ruling)' }
        ]
      },
      {
        tab: 'ruling',
        title: 'The Ruling',
        note: 'A ruling changes who may approve what, so it takes two people. Choose the Tier 5 countersigner here and save. A Tier 4 holder then presses Propose Ruling on the ladders screen and cites the minute or memo. The ladder is NOT in force until the named countersigner presses Countersign from their own login and restates the authority. Everything below the picker is stamped by the system.',
        fields: [
          { name: 'countersigner_choice', label: 'Countersigning Authority (Tier 5 holders)' },
          { name: 'proposed_by', readonly: true, label: 'Proposed By' },
          { name: 'proposed_at', readonly: true, label: 'Proposed At' },
          { name: 'proposed_reference', readonly: true, label: 'Proposed Authority' },
          { name: 'countersigned_by', readonly: true, label: 'Countersigner' },
          { name: 'countersigned_at', readonly: true, label: 'Countersigned At (only when they acted)' },
          { name: 'ruling_reference', readonly: true, label: 'Authority (minute / memo)' },
          { name: 'ruled_by', readonly: true, label: 'Ruled By' },
          { name: 'ruled_at', readonly: true, label: 'Ruled At' },
          { name: 'superseded_by_id', readonly: true, label: 'Superseded By' },
          { name: 'superseded_at', readonly: true, label: 'Superseded At' }
        ]
      }
    ]
  },
  'M30-form-dofa-band': {
    kind: 'model_form', model: 'fix.dofa.threshold',
    title: 'Ladder Band', back: 'M30-dofa-bands',
    sections: [
      { title: 'Band', note: 'An inclusive upper bound and the tier required at or below it. The bands of a proposed or ruled ladder are frozen: an amendment is a new ladder.',
        fields: [
          { name: 'ladder_id', required: true, label: 'Ladder' },
          { name: 'upper_bound', required: true, label: 'Up To (inclusive)' },
          { name: 'tier', required: true, label: 'Tier Required' },
          { name: 'note', label: 'Note' }
        ] }
    ]
  },
};

export const REPORT_ROUTES = {
  open_dofa_rulings: 'open_dofa_rulings',
  'DOFA Coverage': 'M30-dofa-coverage',
  'M30:DOFA Coverage': 'M30-dofa-coverage',
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
  // No 'Config Parameter' entry: the Parameter Registry is a governed
  // read-only register (M30 WRITABLE = () for ir.config_parameter, grid
  // create:false) — a create chip could only fall back to a native Odoo
  // dialog that blocks the workspace. The registry screen + Config Drift
  // Review own the function (A12 sweep 2026-11-05).
  'M30:Feature Flag': 'fix.feature.flag',
  'M30:Announcement': 'fix.platform.announcement'
};

export const FORM_CHIPS = {
  'M30:Authority Ladder': 'M30-form-dofa-ladder',
  'M30:Branch': 'M30-form-branch',
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
    'fix.working.calendar.holiday': 'M30-form-holiday',
    'fix.notification.config': 'M30-form-notif',
    'fix.dofa.ladder': 'M30-form-dofa-ladder',
    'fix.dofa.threshold': 'M30-form-dofa-band'
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
    'M30-calendar-holidays': 'M30-form-holiday',
    'M30-notif': 'M30-form-notif',
    'M30-dofa-ladders': 'M30-form-dofa-ladder',
    'M30-dofa-bands': 'M30-form-dofa-band'
  }
};

export const CREATE = {
  M30: { screen: 'M30-form-branch', model: 'fix.branch', label: 'Branch' }
};
