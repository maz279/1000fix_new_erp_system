/** @odoo-module **/
/* A12 · Platform & Technology — M30 Platform Administration.
 * Registry-faithful: 13 screens (model grids + packs) / 4 reports / 4 forms / freg 64.
 *
 * Capture audit (2026-11-14): every sub-module page names what it captures.
 * Before it, four of the six pages offered one capture for several lists
 * (zones, holidays, environments, releases, ladder bands and notification
 * configs could not be captured from their page), nine screens sat on no page,
 * "Backup & DR" listed CUSTOMER backup plans (M06's), and the job and
 * parameter "registries" were read-only Odoo tables: the spec's job registry,
 * configuration change record, restore tests and DR drills (§10.1) did not
 * exist. They are now models in cd_entity_config (fix_platform_ops3.py).
 *
 * Second pass (2026-11-19), read against FR-ADM-001..040 rather than counted:
 * Branch Master had no capability profile (FR-ADM-004) or zone boundary;
 * Entity Structure captured only the legal entity, not the cost centres,
 * business lines (FR-ADM-006/007) or the effective-dated organisation change
 * (FR-ADM-010/011); Config & Flags had no change freeze, emergency path or
 * licence register (FR-ADM-017/021/028); Calendars had no shift pattern;
 * Announcements had no maintenance window (BRU-ADM-19); Audit had no runbook,
 * alert or capacity review (FR-ADM-036..038). Models: fix_platform_ops4.py.
 * Cost centres and business lines are mastered in M54, shift patterns in M55
 * and geofences in M02: their chips open those forms. */

export const MODULE = {
  area: 'A12', code: 'M30', en: 'Platform Administration', title: 'M30 · Platform Administration',
  bn: 'প্ল্যাটফর্ম প্রশাসন', icon: '🛠️',
  desc: 'Branch registry and entity structure, the technical parameter registry with two-person configuration changes, the scheduled job registry, feature flag rollout, working calendars and holidays, zones, platform announcements, and restore-test and DR drill evidence. Configuration changes apply to this environment only: promotion through an environment ladder is not built.',
  kpis: [
    { l: 'Rulings Awaiting Countersignature', m: 'dofa_awaiting_countersign' },
    { l: 'Branches Active', m: 'branches_active' },
    { l: 'Branches Total', m: 'branches' },
    { l: 'Flags Enabled', m: 'flags_on' },
    { l: 'Flags Total', m: 'flags_total' },
    { l: 'Announcements Live', m: 'announcements_live' },
    { l: 'Config Changes Awaiting Apply', m: 'config_changes_pending' },
    { l: 'Registered Jobs Missed', m: 'jobs_missed' },
    { l: 'Emergency Changes Awaiting Record', m: 'emergency_open' },
    { l: 'Maintenance Windows Planned', m: 'maintenance_upcoming' }
  ],
  groups: [
    { en: 'Registry Completion', screens: [
      { id: 'M30-provisioning', en: 'Branch Provisioning (<1d)', bn: 'Branch Provisioning (<1d)', t: 'r' },
      { id: 'M30-params', en: 'Parameter Registry', bn: 'প্যারামিটার রেজিস্ট্রি', t: 'g' },
      { id: 'M30-config-changes', en: 'Configuration Changes', bn: 'কনফিগারেশন পরিবর্তন', t: 'g' },
      { id: 'M30-jobs', en: 'Scheduled Job Registry', bn: 'নির্ধারিত জব রেজিস্ট্রি', t: 'g' },
      { id: 'M30-crons', en: 'Scheduled Actions (Inventory)', bn: 'নির্ধারিত অ্যাকশন', t: 'g' },
      { id: 'M30-health', en: 'Platform Health Console', bn: 'Platform Health Console', t: 'r' },
      { id: 'M30-env', en: 'Environments', bn: 'Environments', t: 'g' },
      { id: 'M30-backup', en: 'Backup Restore Tests', bn: 'ব্যাকআপ রিস্টোর পরীক্ষা', t: 'g' },
      { id: 'M30-dr-drills', en: 'DR Drills', bn: 'ডিআর মহড়া', t: 'g' },
      { id: 'M30-release', en: 'Release Coordination', bn: 'Release Coordination', t: 'g' },
      { id: 'M30-runbooks', en: 'Runbooks', bn: 'রানবুক', t: 'g' },
      { id: 'M30-alerts', en: 'Alert Registry', bn: 'অ্যালার্ট রেজিস্ট্রি', t: 'g' },
      { id: 'M30-capacity', en: 'Capacity Reviews', bn: 'সক্ষমতা পর্যালোচনা', t: 'g' }
    ]},
    { en: 'Structure', screens: [
      { id: 'M30-branches', en: 'Branch Register', bn: 'শাখা রেজিস্টার', t: 'g' },
      { id: 'M30-entities', en: 'Legal Entities', bn: 'প্রতিষ্ঠান', t: 'g' },
      { id: 'M30-zones', en: 'Dispatch Zones', bn: 'জোন', t: 'g' },
      { id: 'M30-calendars', en: 'Calendars & Shifts', bn: 'ক্যালেন্ডার', t: 'g' },
      { id: 'M30-calendar-holidays', en: 'Calendar Holidays', bn: 'ক্যালেন্ডার ছুটি', t: 'g' },
      { id: 'M30-capabilities', en: 'Branch Capability Profiles', bn: 'শাখার সক্ষমতা', t: 'g' },
      { id: 'M30-geofences', en: 'Zone Boundaries', bn: 'জোন সীমানা', t: 'g' },
      { id: 'M30-org-changes', en: 'Organisation Changes', bn: 'সাংগঠনিক পরিবর্তন', t: 'g' },
      { id: 'M30-cost-centres', en: 'Cost Centres', bn: 'ব্যয় কেন্দ্র', t: 'g' },
      { id: 'M30-business-lines', en: 'Business Lines', bn: 'ব্যবসায়িক লাইন', t: 'g' },
      { id: 'M30-shifts', en: 'Shift Patterns', bn: 'শিফট প্যাটার্ন', t: 'g' }
    ]},
    { en: 'Configuration', screens: [
      { id: 'M30-config', en: 'Config Parameters (Inventory)', bn: 'কনফিগ', t: 'g' },
      { id: 'M30-flags', en: 'Feature Flags & Kill Switches', bn: 'ফিচার ফ্ল্যাগ', t: 'g' },
      { id: 'M30-drift', en: 'Config Drift Review (Inventory, No Drift Computed)', bn: 'ড্রিফট', t: 'r' },
      { id: 'M30-freezes', en: 'Change Freezes', bn: 'পরিবর্তন স্থগিত', t: 'g' },
      { id: 'M30-licences', en: 'Component Licences', bn: 'কম্পোনেন্ট লাইসেন্স', t: 'g' }
    ]},
    { en: 'Comms', screens: [
      { id: 'M30-announcements', en: 'System Announcements', bn: 'ঘোষণা', t: 'g' },
      { id: 'M30-notif', en: 'Notification Config (Policy Record)', bn: 'নোটিফিকেশন', t: 'g' },
      { id: 'M30-maintenance', en: 'Maintenance Windows', bn: 'রক্ষণাবেক্ষণ সময়', t: 'g' }
    ]},
    { en: 'Approval Authority (DOFA)', bn: 'অনুমোদন কর্তৃত্ব', screens: [
      { id: 'M30-dofa-rulings', en: 'Open DOFA Rulings', bn: 'অমীমাংসিত অনুমোদন সিদ্ধান্ত', t: 'r' },
      { id: 'M30-dofa-ladders', en: 'Authority Ladders', bn: 'কর্তৃত্ব ল্যাডার', t: 'g' },
      { id: 'M30-form-dofa-ladder', en: 'Authority Ladder', bn: 'ল্যাডার ফর্ম', t: 'f' },
      { id: 'M30-dofa-bands', en: 'Ladder Bands', bn: 'ল্যাডার ব্যান্ড', t: 'g' }
    ]}
  ],
  reports: ['Branch Registry', 'Feature Flag Rollout', 'Config Parameter Inventory', 'Calendar Coverage', 'DOFA Coverage'],
  forms: ['Branch', 'Zone', 'Legal Entity', 'Feature Flag', 'Configuration Change', 'Registered Parameter', 'Scheduled Job', 'Environment',
    'Working Calendar', 'Calendar Holiday', 'Announcement', 'Notification Configuration',
    'Authority Ladder', 'Ladder Band', 'Release', 'Backup Restore Test', 'DR Drill',
    'Branch Capability', 'Zone Boundary', 'Organisation Change', 'Cost Centre', 'Business Line',
    'Change Freeze', 'Component Licence', 'Shift Pattern', 'Maintenance Window',
    'Runbook', 'Alert', 'Capacity Review'],
  cross: ['M29 access', 'M04 branch ops', 'M55 attendance calendars', 'M65 entities'],
  freg: { src: 64, sub: [
    // Each page names its own capture first, then every other record its lists show.
    ['1', 'Branch Master', 12, { model: 'fix.branch', cols: ['code', 'name', 'entity_id', 'zone_id', 'active'], screens: ['M30-branches', 'M30-provisioning', 'M30-zones', 'M30-capabilities', 'M30-geofences'], reports: ['Branch Registry', 'Branch Provisioning Time'], forms: ['Branch', 'Zone', 'Branch Capability', 'Zone Boundary'], create: 'M30-form-branch' }],
    ['2', 'Entity Structure', 8, { model: 'fix.entity', cols: ['code', 'legal_name', 'legal_name_bn', 'branch_count', 'active'], screens: ['M30-entities', 'M30-org-changes', 'M30-cost-centres', 'M30-business-lines'], reports: [], forms: ['Legal Entity', 'Organisation Change', 'Cost Centre', 'Business Line'], create: 'M30-form-entity' }],
    ['3', 'Config & Flags', 10, { model: 'fix.feature.flag', cols: ['key', 'name', 'enabled', 'scope', 'default_for_new'], screens: ['M30-flags', 'M30-params', 'M30-config-changes', 'M30-freezes', 'M30-config', 'M30-jobs', 'M30-crons', 'M30-env', 'M30-licences'], reports: ['Feature Flag Rollout', 'Config Parameter Inventory', 'Job Success Rate'], forms: ['Feature Flag', 'Configuration Change', 'Change Freeze', 'Registered Parameter', 'Scheduled Job', 'Environment', 'Component Licence'], create: 'M30-form-flag' }],
    ['4', 'Calendars', 9, { model: 'fix.working.calendar', cols: ['name', 'branch_id', 'timezone', 'active'], screens: ['M30-calendars', 'M30-calendar-holidays', 'M30-shifts'], reports: ['Calendar Coverage'], forms: ['Working Calendar', 'Calendar Holiday', 'Shift Pattern'], create: 'M30-form-calendar' }],
    ['5', 'Announcements', 6, { model: 'fix.platform.announcement', cols: ['name', 'severity', 'audience', 'publish_on', 'state'], screens: ['M30-announcements', 'M30-maintenance', 'M30-notif'], reports: [], forms: ['Announcement', 'Maintenance Window', 'Notification Configuration'], create: 'M30-form-announcement' }],
    ['6', 'Audit', 19, { model: 'fix.dofa.ladder', cols: ['name', 'target_model', 'in_force', 'ruled_by', 'ruled_at'], screens: ['M30-dofa-ladders', 'M30-dofa-bands', 'M30-dofa-rulings', 'M30-release', 'M30-health', 'M30-backup', 'M30-dr-drills', 'M30-runbooks', 'M30-alerts', 'M30-capacity', 'M30-drift'], reports: ['DOFA Coverage', 'Config Parameter Inventory', 'Platform Health'], forms: ['Authority Ladder', 'Ladder Band', 'Release', 'Backup Restore Test', 'DR Drill', 'Runbook', 'Alert', 'Capacity Review'], create: 'M30-form-dofa-ladder' }]
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
    cols: ['key', 'name', 'enabled', 'scope', 'default_for_new', 'owning_module', 'planned_removal_date', 'stale'] },
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
          { name: 'default_for_new', label: 'Default for New Branches' },
          { name: 'owning_module', label: 'Owning Module' },
          { name: 'planned_removal_date', label: 'Planned Removal (stale after)' },
          { name: 'stale', readonly: true, label: 'Past Removal Date' }
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
          { name: 'name_bn', label: 'Title (Bengali)' },
          { name: 'kind', required: true, label: 'Kind' },
          { name: 'severity', required: true, label: 'Severity' },
          { name: 'audience', required: true, label: 'Audience' },
          { name: 'publish_on', required: true, label: 'Publish On' },
          { name: 'expires_on', label: 'Expires On' },
          { name: 'maintenance_start', label: 'Maintenance Starts' }
        ] },
      { title: 'Body', fields: [
          { name: 'body', type: 'text', label: 'Message' },
          { name: 'body_bn', type: 'text', label: 'Message (Bengali)' }
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
  // The registry of technical settings the workspace may change, and the changes
  // themselves. A system administrator registers a key; a Platform Admin
  // proposes a change citing its approved change record and a SECOND Platform
  // Admin applies it (BRU-ADM-02). The previous value is kept for roll-back.
  'M30-params': { kind: 'model_list', model: 'fix.config.parameter',
    cols: ['key', 'description', 'value_type', 'current_value', 'default_value', 'owning_module', 'active'],
    note: 'Only a key registered here can be changed from the workspace, and only a system administrator registers one. Credentials never enter it.' },
  'M30-config-changes': { kind: 'model_list', model: 'fix.config.change', stateField: 'state',
    cols: ['name', 'key', 'new_value', 'previous_value', 'change_reference', 'emergency', 'regularise_by', 'proposed_by_id', 'applied_by_id', 'applied_on', 'state'],
    actions: [
      { m: 'action_apply', l: 'Apply (second person)' },
      { m: 'action_apply_emergency', l: 'Apply as Emergency (tells every Platform Admin)' },
      { m: 'action_regularise', l: 'File Change Record (emergency)', ask: 'The approved change record (M66) for this emergency change', kwarg: 'reference' },
      { m: 'action_reject', l: 'Reject / Withdraw', ask: 'Why is this change rejected or withdrawn?', kwarg: 'reason' },
      { m: 'action_rollback', l: 'Roll Back', ask: 'Why is this change being rolled back?', kwarg: 'reason' }
    ] },
  // BRU-ADM-11: every job registered with an owner, an expected duration and a
  // failure impact. Its run state is read from the scheduled action itself.
  'M30-jobs': { kind: 'model_list', model: 'fix.scheduled.job',
    cols: ['name', 'owning_module', 'owner_id', 'failure_impact', 'expected_duration_min', 'schedule', 'last_run', 'next_run', 'run_state'] },
  'M30-crons': { kind: 'model_list', model: 'ir.cron', create: false, cols: ['name', 'active', 'interval_number', 'interval_type', 'lastcall', 'nextcall'] },
  'M30-health': { kind: 'table_report', module: 'M30', report: 'platform_health', title: 'Platform Health Console', period: false },
  'M30-env': { kind: 'model_list', model: 'fix.platform.environment', stateField: 'state', cols: ['name', 'kind', 'base_url', 'release_channel', 'data_residency', 'masking_state', 'state'],
    actions: [
      { m: 'action_go_live', l: 'Go Live' },
      { m: 'action_mark_degraded', l: 'Mark Degraded', ask: 'What is degraded?', kwarg: 'reason' },
      { m: 'action_take_offline', l: 'Take Offline', ask: 'Why is this environment going offline?', kwarg: 'reason' },
      { m: 'action_record_masking', l: 'Record Masking Evidence', ask: 'The run, ticket or report that shows personal data is masked', kwarg: 'evidence' }
    ] },
  // Platform continuity evidence (BRU-ADM-17/18). Customer backup plans are M06's.
  'M30-backup': { kind: 'model_list', model: 'fix.backup.verification',
    cols: ['name', 'backup_type', 'backup_ref', 'taken_at', 'restore_tested_at', 'restore_duration_min', 'result', 'tested_by_id'] },
  'M30-dr-drills': { kind: 'model_list', model: 'fix.dr.drill', stateField: 'state',
    cols: ['name', 'drill_date', 'scenario', 'scope', 'rpo_achieved_min', 'rpo_met', 'rto_achieved_min', 'rto_met', 'signed_off_by_id', 'state'],
    actions: [{ m: 'action_sign_off', l: 'Sign Off (second person)' }] },
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


  /* ===== capture audit forms (2026-11-14) ===== */
  'M30-form-param': {
    kind: 'model_form',
    model: 'fix.config.parameter',
    title: 'Registered Parameter',
    back: 'M30-params',
    sections: [
      { title: 'Parameter', note: 'Registering a key lets Platform Admins change it through a two-person change record. Only a system administrator registers or edits a key, and a key that looks like a credential is refused. A business threshold (a discount ceiling, an approval limit) belongs to master data (M64), not here.',
        fields: [
          { name: 'key', required: true, label: 'Key' },
          { name: 'description', required: true, label: 'What It Controls' },
          { name: 'value_type', required: true, label: 'Type' },
          { name: 'min_value', label: 'Minimum (0 = none)' },
          { name: 'max_value', label: 'Maximum (0 = none)' },
          { name: 'allowed_values', label: 'Allowed Values (text, comma-separated)' },
          { name: 'default_value', label: 'Default' },
          { name: 'owning_module', label: 'Owning Module' },
          { name: 'business_impact', required: true, label: 'Impact If Wrong' },
          { name: 'current_value', readonly: true, label: 'Current Value' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },
  'M30-form-config-change': {
    kind: 'model_form',
    model: 'fix.config.change',
    title: 'Configuration Change',
    newLabel: 'Propose a Configuration Change',
    back: 'M30-config-changes',
    status: { field: 'state', labels: { proposed: 'Proposed', applied: 'Applied', rejected: 'Rejected', rolled_back: 'Rolled Back' } },
    sections: [
      { title: 'Change', note: 'The value is checked against the parameter type and range when you save. A second Platform Admin applies it on the Configuration Changes list; it takes effect at once, without a restart, and the previous value is kept so one action rolls it back. During a change freeze it cannot be applied. An emergency change is applied by you alone with Apply as Emergency: every Platform Admin is told at once, and without its change record within 24 hours it is reverted automatically. Each step is on the audit trail (key and change number, never the value).',
        fields: [
          { name: 'parameter_id', required: true, label: 'Parameter' },
          { name: 'new_value', required: true, label: 'New Value' },
          { name: 'change_reference', label: 'Approved Change Record (M66; an emergency files it within 24 h)' },
          { name: 'emergency', label: 'Emergency Change' },
          { name: 'reason', type: 'text', required: true, label: 'Reason' }
        ] },
      { title: 'Record', fields: [
          { name: 'name', readonly: true, label: 'Reference' },
          { name: 'previous_value', readonly: true, label: 'Previous Value' },
          { name: 'proposed_by_id', readonly: true, label: 'Proposed By' },
          { name: 'applied_by_id', readonly: true, label: 'Applied By' },
          { name: 'applied_on', readonly: true, label: 'Applied On' },
          { name: 'regularise_by', readonly: true, label: 'Change Record Due By' },
          { name: 'closed_by_id', readonly: true, label: 'Rejected / Rolled Back By' },
          { name: 'close_reason', readonly: true, label: 'Rejection / Rollback Reason' }
        ] }
    ]
  },
  'M30-form-job': {
    kind: 'model_form',
    model: 'fix.scheduled.job',
    title: 'Scheduled Job',
    newLabel: 'Register a Scheduled Job',
    back: 'M30-jobs',
    tabs: [
      { id: 'job', label: '1. Registration', bn: '১. নিবন্ধন', icon: '🗓️' },
      { id: 'run', label: '2. Run State', bn: '২. চলার অবস্থা', icon: '⏱️' }
    ],
    sections: [
      { tab: 'job', title: 'Registration', note: 'Every scheduled job needs an owner, an expected duration and a failure impact. Registering a job does not change its schedule. A job whose next run is overdue by more than its expected duration shows as Missed Run.',
        fields: [
          { name: 'cron_id', required: true, label: 'Scheduled Action' },
          { name: 'name', label: 'Job Name (blank: the action name)' },
          { name: 'owning_module', label: 'Owning Module' },
          { name: 'owner_id', required: true, label: 'Job Owner' },
          { name: 'expected_duration_min', required: true, label: 'Expected Duration (min)' },
          { name: 'sla_minutes', label: 'SLA (min)' },
          { name: 'concurrent_safe', label: 'Concurrent-Safe' },
          { name: 'failure_impact', required: true, label: 'Failure Impact' },
          { name: 'failure_note', label: 'What Breaks If It Fails' },
          { name: 'runbook_ref', label: 'Runbook (reference)' },
          { name: 'runbook_id', label: 'Runbook Record' },
          { name: 'active', label: 'Active' }
        ] },
      { tab: 'run', title: 'Run State', note: 'Read from the scheduled action itself.',
        fields: [
          { name: 'schedule', readonly: true, label: 'Schedule' },
          { name: 'cron_active', readonly: true, label: 'Action Enabled' },
          { name: 'last_run', readonly: true, label: 'Last Run' },
          { name: 'next_run', readonly: true, label: 'Next Run' },
          { name: 'run_state', readonly: true, label: 'Run State' }
        ] }
    ]
  },
  'M30-form-backup': {
    kind: 'model_form',
    model: 'fix.backup.verification',
    title: 'Backup Restore Test',
    newLabel: 'Record a Restore Test',
    back: 'M30-backup',
    sections: [
      { title: 'Restore Test', note: 'Backups are restore-tested weekly; a backup that was never restored counts as no backup. Record the backup, where it was restored and the evidence. Once filed, only the note can change.',
        fields: [
          { name: 'backup_ref', required: true, label: 'Backup (snapshot or file)' },
          { name: 'backup_type', required: true, label: 'Backup Type' },
          { name: 'source_environment_id', label: 'Backed-Up Environment' },
          { name: 'restored_into_id', label: 'Restored Into' },
          { name: 'taken_at', required: true, label: 'Backup Taken' },
          { name: 'restore_tested_at', required: true, label: 'Restore Tested' },
          { name: 'restore_duration_min', label: 'Restore Duration (min)' },
          { name: 'result', required: true, label: 'Result' },
          { name: 'evidence', required: true, label: 'Evidence (log, ticket, report)' },
          { name: 'note', type: 'text', label: 'Note' },
          { name: 'tested_by_id', readonly: true, label: 'Tested By' }
        ] }
    ]
  },
  'M30-form-drill': {
    kind: 'model_form',
    model: 'fix.dr.drill',
    title: 'DR Drill',
    newLabel: 'Record a DR Drill',
    back: 'M30-dr-drills',
    status: { field: 'state', labels: { recorded: 'Recorded', signed_off: 'Signed Off' } },
    sections: [
      { title: 'Drill', note: 'Disaster recovery is exercised twice a year against an RPO of 15 minutes and an RTO of 2 hours. A second Platform Admin signs the result off on the DR Drills list; a drill that missed a target needs its issues recorded first. A signed-off drill is frozen.',
        fields: [
          { name: 'drill_date', required: true, label: 'Drill Date' },
          { name: 'scenario', required: true, label: 'Scenario' },
          { name: 'scope', required: true, label: 'Scope' },
          { name: 'environment_id', label: 'DR Environment' },
          { name: 'rpo_achieved_min', required: true, label: 'RPO Achieved (min)' },
          { name: 'rto_achieved_min', required: true, label: 'RTO Achieved (min)' },
          { name: 'issues_found', type: 'text', label: 'Issues Found' },
          { name: 'actions', type: 'text', label: 'Follow-Up Actions' }
        ] },
      { title: 'Result', fields: [
          { name: 'name', readonly: true, label: 'Reference' },
          { name: 'rpo_met', readonly: true, label: 'RPO Met' },
          { name: 'rto_met', readonly: true, label: 'RTO Met' },
          { name: 'signed_off_by_id', readonly: true, label: 'Signed Off By' },
          { name: 'signed_off_on', readonly: true, label: 'Signed Off On' }
        ] }
    ]
  },


  /* ===== capture audit, second pass (2026-11-19) ===== */
  'M30-capabilities': { kind: 'model_list', model: 'fix.branch.capability',
    cols: ['branch_id', 'service_kind', 'device_category', 'max_repair_level', 'effective_from', 'active'],
    note: 'What each branch may perform (FR-ADM-004). The workshop refuses a job above the profile of its branch; a branch with no profile is not yet restricted.' },
  'M30-geofences': { kind: 'model_list', model: 'fix.geofence', create: false, cols: ['name', 'zone_id', 'geofence_type', 'active'],
    note: 'The geographic boundary of each dispatch zone (FR-ADM-005). Mastered with M02 dispatch.' },
  'M30-org-changes': { kind: 'model_list', model: 'fix.org.change', stateField: 'state',
    cols: ['name', 'branch_id', 'change_type', 'previous_state', 'new_state', 'effective_from', 'proposed_by_id', 'approved_by_id', 'state'],
    actions: [
      { m: 'action_approve', l: 'Approve (second person)' },
      { m: 'action_reject', l: 'Reject / Withdraw', ask: 'Why is this change rejected or withdrawn?', kwarg: 'reason' }
    ] },
  'M30-cost-centres': { kind: 'model_list', model: 'fix.cost.centre', create: false,
    cols: ['code', 'name', 'parent_id', 'branch_id', 'owner_id', 'centre_type', 'date_from', 'date_to', 'active'],
    note: 'The cost-centre hierarchy (FR-ADM-006). M54 budgets against it; add one with the Cost Centre chip.' },
  'M30-business-lines': { kind: 'model_list', model: 'fix.business.line', create: false,
    cols: ['code', 'name', 'revenue_stream_no', 'is_profit_centre'],
    note: 'The business-line dimension (FR-ADM-007), shared with M54 profitability; add one with the Business Line chip.' },
  'M30-shifts': { kind: 'model_list', model: 'fix.shift.template', create: false,
    cols: ['name', 'start_hour', 'end_hour', 'operating_unit_id'],
    note: 'Shift patterns (FR-ADM-008) that M55 rosters use; add one with the Shift Pattern chip.' },
  'M30-freezes': { kind: 'model_list', model: 'fix.change.freeze',
    cols: ['name', 'date_from', 'date_to', 'scope', 'status', 'declared_by_id', 'lifted_by_id'],
    actions: [{ m: 'action_lift', l: 'Lift Early', ask: 'Why is the freeze lifted early?', kwarg: 'reason' }] },
  'M30-licences': { kind: 'model_list', model: 'fix.component.licence',
    cols: ['component', 'version', 'licence', 'licence_class', 'owner_id', 'next_review_due', 'review_overdue', 'active'] },
  'M30-maintenance': { kind: 'model_list', model: 'fix.maintenance.window', stateField: 'state',
    cols: ['name', 'scheduled_from', 'scheduled_to', 'planned_minutes', 'scope', 'impact', 'announcement_state', 'actual_from', 'actual_to', 'overran', 'state'],
    actions: [
      { m: 'action_raise_announcement', l: 'Draft the Announcement' },
      { m: 'action_start', l: 'Start (announced only)' },
      { m: 'action_complete', l: 'Complete' },
      { m: 'action_cancel', l: 'Cancel', ask: 'Why is the maintenance cancelled?', kwarg: 'reason' }
    ] },
  'M30-runbooks': { kind: 'model_list', model: 'fix.runbook',
    cols: ['code', 'name', 'scope', 'reference', 'owner_id', 'last_reviewed_on', 'next_review_due', 'review_overdue', 'active'],
    actions: [{ m: 'action_mark_reviewed', l: 'Mark Reviewed Today' }] },
  'M30-alerts': { kind: 'model_list', model: 'fix.platform.alert',
    cols: ['code', 'name', 'source', 'severity', 'threshold_expression', 'routing', 'runbook_id', 'active'] },
  'M30-capacity': { kind: 'model_list', model: 'fix.capacity.metric',
    cols: ['name', 'resource', 'dimension', 'measured_on', 'current_value', 'capacity_value', 'headroom_pct', 'growth_rate_pct', 'projected_exhaustion', 'scaling_action'] },

  'M30-form-capability': {
    kind: 'model_form', model: 'fix.branch.capability', title: 'Branch Capability',
    newLabel: 'Record a Branch Capability', back: 'M30-capabilities',
    sections: [
      { title: 'Capability', note: 'One row per service and device category the branch performs, with the highest repair level it can take. A workshop job above that level at this branch is refused. Leave the category blank to cover every category.',
        fields: [
          { name: 'branch_id', required: true, label: 'Branch' },
          { name: 'service_kind', required: true, label: 'Service' },
          { name: 'device_category', label: 'Device Category (blank: all)' },
          { name: 'max_repair_level', required: true, label: 'Highest Repair Level' },
          { name: 'effective_from', required: true, label: 'Effective From' },
          { name: 'note', label: 'Note' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },
  'M30-form-org-change': {
    kind: 'model_form', model: 'fix.org.change', title: 'Organisation Change',
    newLabel: 'Propose an Organisation Change', back: 'M30-org-changes',
    status: { field: 'state', labels: { proposed: 'Proposed', approved: 'Approved (awaiting date)', applied: 'In Force', rejected: 'Rejected' } },
    sections: [
      { title: 'Change', note: 'Renames, zone moves and relocations of a branch take effect from a date, never backwards, so reports keep the structure that was in force at the time. A second Platform Admin approves on the Organisation Changes list; a change dated today applies at once, a later one on its date. The structure before it is kept on the record.',
        fields: [
          { name: 'branch_id', required: true, label: 'Branch' },
          { name: 'change_type', required: true, label: 'Change' },
          { name: 'new_name', label: 'New Name (rename)' },
          { name: 'new_name_bn', label: 'New Name in Bengali (rename)' },
          { name: 'new_zone_id', label: 'New Zone (zone move)' },
          { name: 'new_address_id', label: 'New Address (relocation)' },
          { name: 'effective_from', required: true, label: 'Effective From' },
          { name: 'reason', type: 'text', required: true, label: 'Reason' }
        ] },
      { title: 'Record', fields: [
          { name: 'name', readonly: true, label: 'Reference' },
          { name: 'previous_state', readonly: true, label: 'Structure Before' },
          { name: 'new_state', readonly: true, label: 'Structure After' },
          { name: 'proposed_by_id', readonly: true, label: 'Proposed By' },
          { name: 'approved_by_id', readonly: true, label: 'Approved By' },
          { name: 'applied_on', readonly: true, label: 'In Force Since' }
        ] }
    ]
  },
  'M30-form-freeze': {
    kind: 'model_form', model: 'fix.change.freeze', title: 'Change Freeze',
    newLabel: 'Declare a Change Freeze', back: 'M30-freezes',
    sections: [
      { title: 'Freeze', note: 'While a freeze is in force no configuration change can be applied and no feature flag changed, except switching a flag off (the kill switch) and the emergency change path. A freeze cannot be edited once it starts; it can only be lifted early, with a reason.',
        fields: [
          { name: 'name', required: true, label: 'Name' },
          { name: 'date_from', required: true, label: 'Starts' },
          { name: 'date_to', required: true, label: 'Ends' },
          { name: 'scope', required: true, label: 'Blocks' },
          { name: 'reason', type: 'text', required: true, label: 'Reason' },
          { name: 'status', readonly: true, label: 'Status' },
          { name: 'declared_by_id', readonly: true, label: 'Declared By' }
        ] }
    ]
  },
  'M30-form-licence': {
    kind: 'model_form', model: 'fix.component.licence', title: 'Component Licence',
    newLabel: 'Register a Component Licence', back: 'M30-licences',
    sections: [
      { title: 'Licence', note: 'Open-source and commercial components of the platform (employee software licences are M66). Anything other than a permissive licence needs a note on how we meet its obligations.',
        fields: [
          { name: 'component', required: true, label: 'Component' },
          { name: 'version', required: true, label: 'Version' },
          { name: 'licence', required: true, label: 'Licence (SPDX)' },
          { name: 'licence_class', required: true, label: 'Class' },
          { name: 'obligation_summary', type: 'text', label: 'Obligations' },
          { name: 'compliance_note', type: 'text', label: 'How We Comply' },
          { name: 'owner_id', label: 'Owner' },
          { name: 'reviewed_on', label: 'Last Reviewed' },
          { name: 'next_review_due', required: true, label: 'Next Review Due' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },
  'M30-form-maintenance': {
    kind: 'model_form', model: 'fix.maintenance.window', title: 'Maintenance Window',
    newLabel: 'Plan a Maintenance Window', back: 'M30-maintenance',
    status: { field: 'state', labels: { planned: 'Planned', in_progress: 'In Progress', completed: 'Completed', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Window', note: 'Planned maintenance runs between 23:00 and 08:00 Dhaka time, at most 4 hours a month, and is announced 72 hours ahead (BRU-ADM-19). Save, then Draft the Announcement on the list; a second Platform Admin publishes it. The work can start only once it is published, and an announced window is not moved: cancel it and plan another.',
        fields: [
          { name: 'scheduled_from', required: true, label: 'Starts' },
          { name: 'scheduled_to', required: true, label: 'Ends' },
          { name: 'scope', required: true, label: 'What Is Done' },
          { name: 'impact', required: true, label: 'User Impact' },
          { name: 'environment_id', label: 'Environment' },
          { name: 'outcome_note', type: 'text', label: 'Outcome' }
        ] },
      { title: 'Record', fields: [
          { name: 'name', readonly: true, label: 'Reference' },
          { name: 'planned_minutes', readonly: true, label: 'Planned (min)' },
          { name: 'announcement_id', readonly: true, label: 'Announcement' },
          { name: 'announcement_state', readonly: true, label: 'Announcement Status' },
          { name: 'actual_from', readonly: true, label: 'Actually Started' },
          { name: 'actual_to', readonly: true, label: 'Actually Ended' },
          { name: 'overran', readonly: true, label: 'Overran' }
        ] }
    ]
  },
  'M30-form-runbook': {
    kind: 'model_form', model: 'fix.runbook', title: 'Runbook',
    newLabel: 'Register a Runbook', back: 'M30-runbooks',
    sections: [
      { title: 'Runbook', note: 'Every module and every alert has an operational runbook (NFR-091). Give the steps here or link the document that holds them. A runbook an active alert relies on cannot be archived.',
        fields: [
          { name: 'code', required: true, label: 'Code' },
          { name: 'name', required: true, label: 'Title' },
          { name: 'scope', required: true, label: 'Covers a' },
          { name: 'reference', label: 'Module / Job / Procedure' },
          { name: 'document_url', label: 'Document Link' },
          { name: 'steps', type: 'text', label: 'Steps' },
          { name: 'owner_id', required: true, label: 'Owner' },
          { name: 'last_reviewed_on', label: 'Last Reviewed' },
          { name: 'review_months', required: true, label: 'Review Every (months)' },
          { name: 'next_review_due', readonly: true, label: 'Next Review Due' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },
  'M30-form-alert': {
    kind: 'model_form', model: 'fix.platform.alert', title: 'Alert',
    newLabel: 'Register an Alert', back: 'M30-alerts',
    sections: [
      { title: 'Alert', note: 'An alert without an action is noise, so every alert names its runbook (BRU-ADM-14), when it fires and who it pages. This register records the alert; the monitoring stack fires it.',
        fields: [
          { name: 'code', required: true, label: 'Code' },
          { name: 'name', required: true, label: 'Name' },
          { name: 'source', required: true, label: 'Source' },
          { name: 'severity', required: true, label: 'Severity' },
          { name: 'threshold_expression', required: true, label: 'Fires When' },
          { name: 'routing', required: true, label: 'Routed To' },
          { name: 'runbook_id', required: true, label: 'Runbook' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },
  'M30-form-capacity': {
    kind: 'model_form', model: 'fix.capacity.metric', title: 'Capacity Review',
    newLabel: 'Record a Capacity Review', back: 'M30-capacity',
    sections: [
      { title: 'Measurement', note: 'Reviewed monthly against growth (OPS-08). Headroom and the projected date the resource fills are computed. Below 20% headroom the review must decide to monitor or scale. Once saved only the decision and note change.',
        fields: [
          { name: 'resource', required: true, label: 'Resource' },
          { name: 'dimension', required: true, label: 'Measured As' },
          { name: 'measured_on', required: true, label: 'Measured On' },
          { name: 'current_value', required: true, label: 'In Use' },
          { name: 'capacity_value', required: true, label: 'Capacity' },
          { name: 'growth_rate_pct', label: 'Growth per Month (%)' },
          { name: 'scaling_action', required: true, label: 'Decision' },
          { name: 'review_note', type: 'text', required: true, label: 'Review Note' }
        ] },
      { title: 'Result', fields: [
          { name: 'name', readonly: true, label: 'Reference' },
          { name: 'headroom_pct', readonly: true, label: 'Headroom (%)' },
          { name: 'projected_exhaustion', readonly: true, label: 'Projected Full' },
          { name: 'reviewed_by_id', readonly: true, label: 'Reviewed By' }
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
          // computed from the code, never stored: shown, not typed
          { name: 'matches_implementation', readonly: true, label: 'Matches Current Code (fact, not a ruling)' }
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
  'M30:DOFA Coverage': 'M30-dofa-coverage',
  'M30:Config Change Log': 'M30-drift',
  'M30:Job Success Rate': 'M30-rpt-jobs',
  'M30:Environment Inventory': 'M30-env',
  'M30:Branch Provisioning Time': 'M30-provisioning',
  'M30:Branch Registry': 'M30-rpt-branches',
  'M30:Feature Flag Rollout': 'M30-rpt-flags',
  'M30:Config Parameter Inventory': 'M30-drift',
  'M30:Calendar Coverage': 'M30-rpt-calendar',
  'M30:Platform Health': 'M30-health'
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
  'M30:Announcement': 'fix.platform.announcement',
  'M30:Zone': 'fix.zone',
  'M30:Legal Entity': 'fix.entity',
  // the registry of governed keys, not ir.config_parameter itself
  'M30:Registered Parameter': 'fix.config.parameter',
  'M30:Configuration Change': 'fix.config.change',
  'M30:Scheduled Job': 'fix.scheduled.job',
  'M30:Environment': 'fix.platform.environment',
  'M30:Working Calendar': 'fix.working.calendar',
  'M30:Calendar Holiday': 'fix.working.calendar.holiday',
  'M30:Notification Configuration': 'fix.notification.config',
  'M30:Ladder Band': 'fix.dofa.threshold',
  'M30:Release': 'fix.platform.release',
  'M30:Backup Restore Test': 'fix.backup.verification',
  'M30:DR Drill': 'fix.dr.drill',
  'M30:Branch Capability': 'fix.branch.capability',
  'M30:Zone Boundary': 'fix.geofence',
  'M30:Organisation Change': 'fix.org.change',
  'M30:Cost Centre': 'fix.cost.centre',
  'M30:Business Line': 'fix.business.line',
  'M30:Change Freeze': 'fix.change.freeze',
  'M30:Component Licence': 'fix.component.licence',
  'M30:Shift Pattern': 'fix.shift.template',
  'M30:Maintenance Window': 'fix.maintenance.window',
  'M30:Runbook': 'fix.runbook',
  'M30:Alert': 'fix.platform.alert',
  'M30:Capacity Review': 'fix.capacity.metric'
};

export const FORM_CHIPS = {
  'M30:Authority Ladder': 'M30-form-dofa-ladder',
  'M30:Branch': 'M30-form-branch',
  'M30:Feature Flag': 'M30-form-flag',
  'M30:Announcement': 'M30-form-announcement',
  'M30:Zone': 'M30-form-zone',
  'M30:Legal Entity': 'M30-form-entity',
  'M30:Registered Parameter': 'M30-form-param',
  'M30:Configuration Change': 'M30-form-config-change',
  'M30:Scheduled Job': 'M30-form-job',
  'M30:Environment': 'M30-form-env',
  'M30:Working Calendar': 'M30-form-calendar',
  'M30:Calendar Holiday': 'M30-form-holiday',
  'M30:Notification Configuration': 'M30-form-notif',
  'M30:Ladder Band': 'M30-form-dofa-band',
  'M30:Release': 'M30-form-release',
  'M30:Backup Restore Test': 'M30-form-backup',
  'M30:DR Drill': 'M30-form-drill',
  'M30:Branch Capability': 'M30-form-capability',
  // Mastered by the module that owns the behaviour: the chip opens its form.
  'M30:Zone Boundary': 'M02-form-zone',
  'M30:Cost Centre': 'M54-form-centre',
  'M30:Business Line': 'M54-form-bline',
  'M30:Shift Pattern': 'M55-form-shift',
  'M30:Organisation Change': 'M30-form-org-change',
  'M30:Change Freeze': 'M30-form-freeze',
  'M30:Component Licence': 'M30-form-licence',
  'M30:Maintenance Window': 'M30-form-maintenance',
  'M30:Runbook': 'M30-form-runbook',
  'M30:Alert': 'M30-form-alert',
  'M30:Capacity Review': 'M30-form-capacity',
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
    'fix.dofa.threshold': 'M30-form-dofa-band',
    'fix.config.parameter': 'M30-form-param',
    'fix.config.change': 'M30-form-config-change',
    'fix.scheduled.job': 'M30-form-job',
    'fix.backup.verification': 'M30-form-backup',
    'fix.dr.drill': 'M30-form-drill',
    'fix.branch.capability': 'M30-form-capability',
    'fix.org.change': 'M30-form-org-change',
    'fix.change.freeze': 'M30-form-freeze',
    'fix.component.licence': 'M30-form-licence',
    'fix.maintenance.window': 'M30-form-maintenance',
    'fix.runbook': 'M30-form-runbook',
    'fix.platform.alert': 'M30-form-alert',
    'fix.capacity.metric': 'M30-form-capacity'
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
    'M30-dofa-bands': 'M30-form-dofa-band',
    'M30-params': 'M30-form-param',
    'M30-config-changes': 'M30-form-config-change',
    'M30-jobs': 'M30-form-job',
    'M30-backup': 'M30-form-backup',
    'M30-dr-drills': 'M30-form-drill',
    'M30-capabilities': 'M30-form-capability',
    'M30-org-changes': 'M30-form-org-change',
    'M30-freezes': 'M30-form-freeze',
    'M30-licences': 'M30-form-licence',
    'M30-maintenance': 'M30-form-maintenance',
    'M30-runbooks': 'M30-form-runbook',
    'M30-alerts': 'M30-form-alert',
    'M30-capacity': 'M30-form-capacity'
  }
};

export const CREATE = {
  M30: { screen: 'M30-form-branch', model: 'fix.branch', label: 'Branch' }
};
