/** @odoo-module **/
/* A12 · Platform & Technology — M29 Identity, Access & Security.
 * Registry-faithful: 4 groups / 13 screens / 5 reports / 4 forms / freg 78.
 * Scope note: field-level reads are not instrumented, so the sensitive-data
 * pack reports the CLASSIFIED exposure surface, never invented read counts.
 *
 * Workspace wiring pass (2026-11-05): the User master is the comprehensive
 * 7-tab form (identity editable; entitlement / DOFA authority / lifecycle
 * panels read-only computes over the real registers), every form carries
 * its decision-stamp and measurement fields read-only, the grids show the
 * governance columns, and the audit trail exposes the chain verification. */

export const MODULE = {
  area: 'A12', code: 'M29', en: 'Identity, Access & Security', title: 'M29 · Identity, Access & Security',
  bn: 'পরিচয়, অ্যাক্সেস ও নিরাপত্তা', icon: '🛡️',
  desc: 'Users, business roles and Odoo groups; access requests that really grant or revoke a group; record and field rules; SoD controls with measured conflict tests; privileged sessions; and the sensitive-field classification behind the PDPA review.',
  kpis: [
    { l: 'Active Users', m: 'users_active' },
    { l: 'Active Roles', m: 'roles_active' },
    { l: 'Requests Open', m: 'requests_open' },
    { l: 'Sessions Open', m: 'sessions_open' },
    { l: 'SoD Failures', m: 'sod_failures' },
    { l: 'SoD Tests', m: 'sod_tests' }
  ],
  groups: [
    { en: 'Record Coverage', screens: [
      { id: 'M29-isolation-tier', en: "Isolation Tier", bn: "Isolation Tier", t: 'g' }
    ]},
    { en: 'Identity', screens: [
      { id: 'M29-users', en: 'Users', bn: 'ব্যবহারকারী', t: 'g' },
      { id: 'M29-sessions', en: 'Sessions & Device Trust', bn: 'সেশন', t: 'g' },
      { id: 'M29-jml', en: 'JML Automation', bn: 'জেএমএল', t: 'g' }
    ]},
    { en: 'Access', screens: [
      { id: 'M29-roles', en: 'Roles & Permission Sets', bn: 'ভূমিকা', t: 'g' },
      { id: 'M29-record', en: 'Record Rules (T0–T5)', bn: 'রেকর্ড নিয়ম', t: 'g' },
      { id: 'M29-fields', en: 'Field-Level Permissions', bn: 'ক্ষেত্র-স্তরের অনুমতি', t: 'g' },
      { id: 'M29-cert', en: 'Access Certification', bn: 'অ্যাক্সেস সার্টিফিকেশন', t: 'g' },
      { id: 'M29-requests', en: 'Access Requests', bn: 'অ্যাক্সেস অনুরোধ', t: 'g' },
      { id: 'M29-groups', en: 'Odoo Groups', bn: 'গ্রুপ', t: 'g' },
      { id: 'M29-acl', en: 'Model Access', bn: 'মডেল অ্যাক্সেস', t: 'g' }
    ]},
    { en: 'Data Protection', screens: [
      { id: 'M29-classification', en: 'Classification (S0–S3)', bn: 'শ্রেণিবিন্যাস', t: 'g' },
      { id: 'M29-residency', en: 'Residency Enforcement', bn: 'আবাসিক প্রয়োগ', t: 'g' },
      { id: 'M29-keys', en: 'Encryption & Keys', bn: 'এনক্রিপশন', t: 'g' }
    ]},
    { en: 'Monitoring', screens: [
      { id: 'M29-audit', en: 'Immutable Audit Trail', bn: 'অডিট ট্রেইল', t: 'g' },
      { id: 'M29-privileged', en: 'Privileged Access', bn: 'বিশেষ সুবিধাভোগী', t: 'g' },
      { id: 'M29-incidents', en: 'Security Incidents', bn: 'নিরাপত্তা ঘটনা', t: 'g' },
      { id: 'M29-sod', en: 'SoD Controls', bn: 'SoD নিয়ন্ত্রণ', t: 'g' },
      { id: 'M29-sodtests', en: 'SoD Test Runs', bn: 'SoD পরীক্ষা', t: 'g' }
    ]}
  ],
  reports: ['Access Review Pack', 'Privileged Session Log', 'Sensitive-Data Access', 'SoD Test Results', 'Authentication Trends'],
  forms: ['User', 'Role', 'Record Rule', 'Access Request'],
  cross: ['M28 credentials', 'M60 controls', 'M24 retention', 'M33 party master'],
  freg: { src: 78, sub: [
    ['1', 'Identity & MFA', 14, { model: 'res.users', cols: ['login', 'partner_id', 'company_id', 'active', 'create_date'], screens: ['M29-users', 'M29-sessions'], domain: [['share', '=', false]] }],
    ['2', 'Role & Group Model', 13, { model: 'fix.role', cols: ['code', 'name', 'group_id', 'keycloak_role', 'active'], screens: ['M29-roles', 'M29-groups', 'M29-acl'] }],
    ['3', 'Record & Field Rules', 15, { model: 'ir.rule', cols: ['name', 'model_id', 'perm_read', 'perm_write', 'global'], screens: ['M29-record', 'M29-fields', 'M29-isolation-tier'] }],
    ['4', 'Access Requests', 10, { model: 'fix.access.request', cols: ['name', 'request_type', 'user_id', 'role_id', 'state'], screens: ['M29-requests', 'M29-cert', 'M29-jml'] }],
    ['5', 'SoD Testing', 9, { model: 'fix.sod.test', cols: ['name', 'control_id', 'tested_on', 'violations_found', 'result'], screens: ['M29-sodtests', 'M29-sod'] }],
    ['6', 'Data Protection', 10, { model: 'fix.sensitive.field', cols: ['model_name', 'field_name', 'sensitivity', 'data_class', 'masking_rule'], screens: ['M29-classification', 'M29-keys', 'M29-residency'] }],
    ['7', 'Monitoring & Audit', 7, { model: 'fix.security.audit', cols: ['sequence', 'occurred_at', 'actor_id', 'event', 'object_ref'], screens: ['M29-audit', 'M29-privileged', 'M29-incidents'] }]
  ] }
};

export const SCREENS = {
  /* ---- Identity ---- */
  'M29-users': { kind: 'model_list', model: 'res.users', create: false,
    cols: ['login', 'name', 'fix_role_codes', 'company_id', 'default_operating_unit_id', 'login_date', 'active'] },
  'M29-sessions': { kind: 'model_list', model: 'res.device.log', create: false,
    cols: ['user_id', 'platform', 'browser', 'ip_address', 'country', 'last_activity', 'revoked'] },
  'M29-jml': { kind: 'model_list', model: 'fix.jml.event', stateField: 'state',
    cols: ['name', 'event_type', 'employee_id', 'user_id', 'role_id', 'effective_on', 'applied_on', 'result_note', 'state'],
    actions: [{ m: 'action_apply', l: 'Apply' }, { m: 'action_cancel', l: 'Cancel' }] },

  /* ---- Access ---- */
  'M29-roles': { kind: 'model_list', model: 'fix.role',
    cols: ['code', 'name', 'group_id', 'keycloak_role', 'active'] },
  'M29-record': { kind: 'model_list', model: 'ir.rule',
    cols: ['name', 'model_id', 'groups', 'perm_read', 'perm_write', 'perm_create', 'perm_unlink'] },
  'M29-fields': { kind: 'model_list', model: 'fix.field.rule',
    cols: ['model_id', 'field_id', 'role_ids', 'permission'] },
  'M29-cert': { kind: 'model_list', model: 'fix.access.certification', stateField: 'decision',
    cols: ['name', 'period', 'user_id', 'role_id', 'reviewer_id', 'due_on', 'decided_on', 'decision'],
    actions: [{ m: 'action_certify', l: 'Certify' }, { m: 'action_revoke', l: 'Revoke' }] },
  'M29-requests': { kind: 'model_list', model: 'fix.access.request', stateField: 'state',
    cols: ['name', 'request_type', 'user_id', 'role_id', 'requested_by_id', 'approver_id', 'requested_on', 'valid_until', 'state'],
    actions: [{ m: 'action_approve', l: 'Approve' }, { m: 'action_reject', l: 'Reject' },
              { m: 'action_grant', l: 'Grant / Revoke' }] },
  'M29-groups': { kind: 'model_list', model: 'res.groups', create: false,
    cols: ['name'] },
  'M29-acl': { kind: 'model_list', model: 'ir.model.access',
    cols: ['name', 'model_id', 'group_id', 'perm_read', 'perm_write', 'perm_create', 'perm_unlink'] },

  /* ---- Data protection ---- */
  'M29-classification': { kind: 'model_list', model: 'fix.sensitive.field',
    cols: ['model_name', 'field_name', 'sensitivity', 'data_class', 'masking_rule', 'lawful_basis', 'active'] },
  // Residency is enforced by the write-time mixin; this screen is its per-read log.
  'M29-residency': { kind: 'model_list', model: 'fix.z4.access.audit', create: false,
    cols: ['user_id', 'access_time', 'access_type', 'case_id'] },
  'M29-keys': { kind: 'model_list', model: 'fix.encryption.key', stateField: 'state',
    cols: ['code', 'name', 'purpose', 'algorithm', 'vault_ref', 'last_rotated_on', 'next_rotation_on', 'state'],
    actions: [{ m: 'action_rotate', l: 'Rotate' }] },

  /* ---- Monitoring ---- */
  // Append-only: entries are written by the system, never typed (+ New suppressed).
  // Verify Chain (R5) recomputes every row's hash and checks the links —
  // the summary (entries checked, discontinuities) is the report.
  'M29-audit': { kind: 'model_list', model: 'fix.security.audit', create: false,
    cols: ['sequence', 'occurred_at', 'actor_id', 'event', 'object_ref', 'detail', 'entry_hash'],
    actions: [{ m: 'action_verify_chain', l: 'Verify Chain' }] },
  'M29-privileged': { kind: 'model_list', model: 'fix.privileged.session', stateField: 'state',
    cols: ['name', 'user_id', 'access_kind', 'ticket_ref', 'started_at', 'duration_minutes', 'state'],
    actions: [{ m: 'action_close', l: 'Close Session' }] },
  'M29-incidents': { kind: 'model_list', model: 'fix.security.incident', stateField: 'state',
    cols: ['name', 'title', 'category', 'severity', 'detected_at', 'affected_user_id', 'state'],
    actions: [{ m: 'action_contain', l: 'Contain' }, { m: 'action_close', l: 'Close' }, { m: 'action_set_severity', l: 'Set Severity' }] },
  'M29-sod': { kind: 'model_list', model: 'fix.sod.control',
    cols: ['code', 'name', 'role_a_id', 'role_b_id', 'conflict_action', 'active'] },
  'M29-sodtests': { kind: 'model_list', model: 'fix.sod.test', stateField: 'result',
    cols: ['name', 'control_id', 'tested_on', 'users_checked', 'violations_found', 'result'],
    actions: [{ m: 'action_run', l: 'Run Test' }] },

  /* ---- report screens (own pack each) ---- */
  'M29-rpt-review': { kind: 'table_report', module: 'M29', report: 'access_review', title: 'Access Review Pack', period: false },
  'M29-rpt-sessions': { kind: 'table_report', module: 'M29', report: 'privileged_sessions', title: 'Privileged Session Log', period: false },
  'M29-rpt-sensitive': { kind: 'table_report', module: 'M29', report: 'sensitive_access', title: 'Sensitive-Data Access', period: false },
  'M29-rpt-sod': { kind: 'table_report', module: 'M29', report: 'sod_results', title: 'SoD Test Results', period: false },
  'M29-rpt-auth': { kind: 'table_report', module: 'M29', report: 'auth_trends', title: 'Authentication Trends', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  /* The User master (M29 wiring pass 2026-11-05): comprehensive, 7 tabs.
   * Identity / scope / preferences are EDITABLE; entitlements, authority
   * and lifecycle panels are READ-ONLY computes over the real registers
   * (fix.role mapping, DOFA tier groups, certifications, access requests).
   * group_ids is deliberately absent: every privilege change goes through
   * an approved access request so the grant is approved, SoD-checked and
   * recorded. */
  'M29-form-user': {
    kind: 'model_form',
    model: 'res.users',
    title: 'User',
    back: 'M29-users',
    status: { field: 'active', labels: { true: 'Active', false: 'Inactive' } },
    tabs: [
      { id: 'general', label: '1. General & Photo', bn: '১. সাধারণ তথ্য ও ছবি', icon: '👤', badge: '10' },
      { id: 'org', label: '2. Organisation & Data Scope', bn: '২. প্রতিষ্ঠান ও ডেটা পরিধি', icon: '🏢', badge: '6' },
      { id: 'prefs', label: '3. Preferences & Comms', bn: '৩. পছন্দ ও যোগাযোগ', icon: '⚙️', badge: '9' },
      { id: 'security', label: '4. Security & Authentication', bn: '৪. নিরাপত্তা ও প্রমাণীকরণ', icon: '🔐', badge: '6' },
      { id: 'access', label: '5. Access & Roles', bn: '৫. অ্যাক্সেস ও ভূমিকা', icon: '🗝️', badge: '4' },
      { id: 'authority', label: '6. Approver & Financial Authority', bn: '৬. অনুমোদন ও আর্থিক ক্ষমতা', icon: '🧾', badge: '3' },
      { id: 'lifecycle', label: '7. Lifecycle & Audit', bn: '৭. জীবনচক্র ও অডিট', icon: '📜', badge: '2' }
    ],
    sections: [
      { tab: 'general', title: 'Identity', note: 'Who the login belongs to. The photo and the Bengali name follow the estate bilingual master-data rule (DE-17).',
        fields: [
          { name: 'image_1920', label: 'User Photo', type: 'image' },
          { name: 'name', required: true, label: 'Full Name (English)' },
          { name: 'name_bn', label: 'Full Name (Bengali)' },
          { name: 'login', required: true, label: 'Login' },
          { name: 'email', label: 'Email' }
        ] },
      { tab: 'general', title: 'Contact Channels', note: 'Official channels first — these drive notifications and the directory.',
        fields: [
          { name: 'phone', label: 'Phone' },
          { name: 'mobile_phone', label: 'Work Mobile' },
          { name: 'work_email', label: 'Work Email' },
          { name: 'barcode', label: 'Badge / Attendance PIN' }
        ] },
      { tab: 'general', title: 'Account State', note: 'Deactivating a leaver here only switches the login off — the JML leaver action additionally removes EVERY group and unassigns ITSM assets. Prefer the JML action for leavers.',
        fields: [
          { name: 'active', label: 'Active' }
        ] },
      { tab: 'org', title: 'Placement', note: 'The company (startup context) and the operating unit scope the records this user sees through record rules.',
        fields: [
          { name: 'company_id', required: true, label: 'Company' },
          { name: 'default_operating_unit_id', label: 'Default Operating Unit' },
          { name: 'work_location_id', label: 'Work Location' },
          { name: 'work_location_type', label: 'Location Type' },
          { name: 'employee_id', readonly: true, label: 'Linked Employee (HR Master)' }
        ] },
      { tab: 'org', title: 'Data Isolation', note: 'Rows are further isolated by the six tiers T0–T5 (Isolation Tier screen); allowed companies is a data-scope change owned by the multi-entity substrate — shown read-only.',
        fields: [
          { name: 'fix_allowed_companies', readonly: true, label: 'Allowed Companies' }
        ] },
      { tab: 'prefs', title: 'Interface', note: 'Bengali and English are first-class interface languages (bn_BD / en_US).',
        fields: [
          { name: 'lang', label: 'Interface Language' },
          { name: 'tz', label: 'Timezone' },
          { name: 'preferred_language', label: 'Preferred Correspondence Language' }
        ] },
      { tab: 'prefs', title: 'Communication', note: 'How this user receives notifications; the signature stamps outgoing messages.',
        fields: [
          { name: 'notification_type', label: 'Notifications' },
          { name: 'signature', type: 'text', label: 'Signature' },
          { name: 'out_of_office_from', label: 'Out of Office From' },
          { name: 'out_of_office_to', label: 'Out of Office To' },
          { name: 'out_of_office_message', type: 'text', label: 'Out-of-Office Message' },
          { name: 'comment', type: 'text', label: 'Internal Note' }
        ] },
      { tab: 'security', title: 'Authentication Posture', note: 'Read-only, measured from the login records. MFA (TOTP) status feeds the ISO 27001 A.5.17 review; the 90-day login-recency review drives the account-review trigger. Passwords are never typed here — use the Odoo invitation / reset flow.',
        fields: [
          { name: 'totp_enabled', readonly: true, label: 'MFA (TOTP) Enabled' },
          { name: 'login_date', readonly: true, label: 'Last Login' },
          { name: 'share', readonly: true, label: 'Internal / Portal' },
          { name: 'is_system', readonly: true, label: 'System Administrator' },
          { name: 'create_date', readonly: true, label: 'Created On' },
          { name: 'write_date', readonly: true, label: 'Last Updated' }
        ] },
      { tab: 'access', title: 'Entitlement (read-only)', note: 'What this user can access — resolved from REAL group membership through the 53-role register (the same measurement the Access Review pack reports). Groups are NOT edited here: every grant goes through an approved access request (two-person, SoD-checked). Use the Access Requests screen to grant or revoke.',
        fields: [
          { name: 'fix_role_codes', readonly: true, label: 'Business Roles Held' },
          { name: 'fix_role_count', readonly: true, label: 'Roles Held' },
          { name: 'fix_group_names', readonly: true, label: 'Permission Groups' },
          { name: 'fix_workspaces', readonly: true, label: 'Workspace Access' }
        ] },
      { tab: 'authority', title: 'Approver & Authoriser (read-only)', note: 'Financial authority is group-derived, never typed: the DOFA tier groups decide which approvals this user may sign, and the threshold amounts live in the two-person-ruled DOFA ladders (M30). Approver/custodian appointments are granted like any other access — via approved requests.',
        fields: [
          { name: 'fix_dofa_tier', readonly: true, label: 'DOFA Tier Held' },
          { name: 'fix_authority', readonly: true, label: 'Security Authority' },
          { name: 'fix_approver_groups', readonly: true, label: 'Approver Appointments' }
        ] },
      { tab: 'lifecycle', title: 'Review & Requests (read-only)', note: 'Certification history and pending requests. Unconfirmed certification lines past their due date are revoked automatically; granted elevations expire on their valid-until date. Full history: JML Automation, Privileged Access, Device Trust (Sessions) and the Immutable Audit Trail screens.',
        fields: [
          { name: 'fix_last_certification', readonly: true, label: 'Last Certification' },
          { name: 'fix_open_requests', readonly: true, label: 'Open Access Requests' }
        ] }
    ]
  },

  'M29-form-jml': {
    kind: 'model_form',
    model: 'fix.jml.event',
    title: 'JML Event',
    back: 'M29-jml',
    status: { field: 'state', labels: { pending: 'Pending', applied: 'Applied', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Joiner / Mover / Leaver', note: 'Applying a joiner or mover grants every Odoo group mapped to the chosen role (blocked if a SoD control forbids the combination); applying a leaver removes ALL groups and deactivates the user. The state moves only through the Apply / Cancel actions.',
        fields: [
          { name: 'event_type', required: true, label: 'Event Type' },
          { name: 'employee_id', required: true, label: 'Employee' },
          { name: 'user_id', label: 'Portal User' },
          { name: 'role_id', label: 'Role to Apply' },
          { name: 'effective_on', required: true, label: 'Effective On' }
        ] },
      { title: 'Application Result (read-only)', note: 'Stamped by the Apply action: when it ran and exactly what it did (groups granted, or the leaver deprovisioning count).',
        fields: [
          { name: 'applied_on', readonly: true, label: 'Applied On' },
          { name: 'result_note', readonly: true, label: 'Result' }
        ] }
    ]
  },

  'M29-form-cert': {
    kind: 'model_form',
    model: 'fix.access.certification',
    title: 'Access Certification Line',
    back: 'M29-cert',
    status: { field: 'decision', labels: { pending: 'Pending', certified: 'Certified', revoked: 'Revoked' } },
    sections: [
      { title: 'Certification', note: 'One line per user and role held. Certifying confirms the access is still needed; revoking removes the role\'s Odoo groups from the user — a real change. The decision comes from the Certify / Revoke actions, and only the reviewer (never the user under review) may make it. Unconfirmed lines past their due date are revoked by the close-out cron.',
        fields: [
          { name: 'period', required: true, label: 'Period' },
          { name: 'user_id', required: true, label: 'User Under Review' },
          { name: 'role_id', required: true, label: 'Role Held' },
          { name: 'reviewer_id', label: 'Reviewer' },
          { name: 'due_on', label: 'Due On (close-out deadline)' },
          { name: 'decided_on', readonly: true, label: 'Decided On' },
          { name: 'note', label: 'Note' }
        ] }
    ]
  },

  'M29-form-key': {
    kind: 'model_form',
    model: 'fix.encryption.key',
    title: 'Encryption Key',
    back: 'M29-keys',
    status: { field: 'state', labels: { active: 'Active', rotating: 'Rotating', retired: 'Retired' } },
    sections: [
      { title: 'Key', note: 'This register stores a VAULT REFERENCE only — key material is never entered into or stored by this database (SEC-101). The reference must start with vault:// or the save is refused. State and the rotation dates are set by the Rotate action (custodian only) — never typed.',
        fields: [
          { name: 'code', required: true, label: 'Key Code' },
          { name: 'name', required: true, label: 'Key Name' },
          { name: 'purpose', required: true, label: 'Purpose' },
          { name: 'algorithm', required: true, label: 'Algorithm' },
          { name: 'vault_ref', required: true, label: 'Vault Reference' },
          { name: 'rotations_per_year', label: 'Rotations / Year' },
          { name: 'custodian_id', label: 'Custodian' },
          { name: 'successor_id', readonly: true, label: 'Rotated Into' }
        ] }
    ]
  },

  'M29-form-incident': {
    kind: 'model_form',
    model: 'fix.security.incident',
    title: 'Security Incident',
    back: 'M29-incidents',
    status: { field: 'state', labels: { open: 'Open', contained: 'Contained', closed: 'Closed' } },
    tabs: [
      { id: 'facts', label: '1. Incident Facts', bn: '১. ঘটনার তথ্য', icon: '🚨', badge: '6' },
      { id: 'narrative', label: '2. Narrative & Closure', bn: '২. বিবরণ ও সমাপ্তি', icon: '📝', badge: '4' }
    ],
    sections: [
      { tab: 'facts', title: 'Incident', note: 'Open → contained (the containment note is required) → closed. Closing also requires a root cause, and a data-leak needs the breach assessment. Severity is set by the Set Severity action under two-person control — a second person must confirm — so it is never typed here.',
        fields: [
          { name: 'title', required: true, label: 'Title' },
          { name: 'category', required: true, label: 'Category' },
          { name: 'detected_at', required: true, label: 'Detected At' },
          { name: 'detected_by_id', label: 'Detected By' },
          { name: 'affected_user_id', label: 'Affected User' },
          { name: 'session_id', label: 'Related Privileged Session' }
        ] },
      { tab: 'narrative', title: 'Narrative', note: 'The containment note gates Contained; the root cause (and, for a data leak, the breach assessment) gates Closed.',
        fields: [
          { name: 'description', type: 'text', label: 'What happened' },
          { name: 'containment', type: 'text', label: 'Containment' },
          { name: 'root_cause', type: 'text', label: 'Root cause (required to close)' },
          { name: 'breach_assessment', type: 'text', label: 'Breach assessment (required to close a data leak)' },
          { name: 'severity_set_by_id', readonly: true, label: 'Severity Set By' },
          { name: 'severity_confirmed_by_id', readonly: true, label: 'Severity Confirmed By' },
          { name: 'resolved_on', readonly: true, label: 'Resolved On' }
        ] }
    ]
  },

  'M29-form-role': {
    kind: 'model_form',
    model: 'fix.role',
    title: 'Business Role',
    back: 'M29-roles',
    sections: [
      { title: 'Role', note: 'Role code is R-nn. Mapping the role to an Odoo group is what lets an access request actually grant it.',
        fields: [
          { name: 'code', required: true, label: 'Role Code (R-nn)' },
          { name: 'name', required: true, label: 'Role Name' },
          { name: 'name_bn', label: 'Role Name (Bengali)' },
          { name: 'group_id', label: 'Odoo Group' },
          { name: 'keycloak_role', label: 'Keycloak Realm Role' },
          { name: 'company_id', label: 'Company' },
          { name: 'active', label: 'Active' }
        ] },
      { title: 'Mapping & Scope (read-only)', note: 'The full permission-group register, isolation tiers and OU scope this role carries — shown read-only (the workspace form has no m2m editor; the governed mapping is maintained Odoo-side and is what grants actually apply).',
        fields: [
          { name: 'fix_group_roll', readonly: true, label: 'Mapped Permission Groups' },
          { name: 'fix_tier_roll', readonly: true, label: 'Isolation Tiers (T0–T5)' },
          { name: 'fix_ou_roll', readonly: true, label: 'Operating-Unit Scope' }
        ] },
      { title: 'Description', fields: [
          { name: 'description', type: 'text', label: 'Description' }
        ] }
    ]
  },

  'M29-form-rule': {
    kind: 'model_form',
    model: 'ir.rule',
    title: 'Record Rule',
    back: 'M29-recordrules',
    sections: [
      { title: 'Record Rule', note: 'A record rule restricts which rows a group can see. A global rule (no group) applies to everyone — treat it as a security change.',
        fields: [
          { name: 'name', required: true, label: 'Rule Name' },
          { name: 'model_id', required: true, label: 'Model' },
          { name: 'domain_force', required: true, type: 'text', label: 'Domain' },
          { name: 'perm_read', label: 'Read' },
          { name: 'perm_write', label: 'Write' },
          { name: 'perm_create', label: 'Create' },
          { name: 'perm_unlink', label: 'Delete' }
        ] }
    ]
  },

  'M29-form-acl': {
    kind: 'model_form',
    model: 'ir.model.access',
    title: 'Model Access',
    back: 'M29-acl',
    sections: [
      { title: 'Access Right', note: 'One row grants a group CRUD rights on one model. Granting is additive — nothing here removes rights held elsewhere.',
        fields: [
          { name: 'name', required: true, label: 'Description' },
          { name: 'model_id', required: true, label: 'Model' },
          { name: 'group_id', label: 'Group' },
          { name: 'perm_read', label: 'Read' },
          { name: 'perm_write', label: 'Write' },
          { name: 'perm_create', label: 'Create' },
          { name: 'perm_unlink', label: 'Delete' }
        ] }
    ]
  },

  'M29-form-fieldrule': {
    kind: 'model_form',
    model: 'fix.field.rule',
    title: 'Field Rule',
    back: 'M29-fieldrules',
    sections: [
      { title: 'Field Permission', note: 'Hides or masks one field for a set of roles. An empty role list is the deny-all default — it applies to every role, so treat a blank list as a deliberate choice.',
        fields: [
          { name: 'model_id', required: true, label: 'Model' },
          { name: 'field_id', required: true, label: 'Field' },
          { name: 'permission', required: true, label: 'Permission' },
          { name: 'fix_role_roll', readonly: true, label: 'Roles (read-only roll)' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },

  'M29-form-sodcontrol': {
    kind: 'model_form',
    model: 'fix.sod.control',
    title: 'SoD Control',
    back: 'M29-sod',
    sections: [
      { title: 'Segregation of Duties', note: 'A control states two roles that must never be held by the same person. The action decides whether a conflict blocks the grant or only raises a finding; the SoD Test Runs measure it for real.',
        fields: [
          { name: 'code', required: true, label: 'SoD Code' },
          { name: 'name', required: true, label: 'Control Description' },
          { name: 'role_a_id', required: true, label: 'Role A' },
          { name: 'role_b_id', required: true, label: 'Role B' },
          { name: 'conflict_action', required: true, label: 'Conflict Action' },
          { name: 'company_id', label: 'Company' },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'active', label: 'Active' }
        ] },
      { title: 'Rationale', fields: [
          { name: 'rationale', type: 'text', label: 'Why these roles conflict' }
        ] }
    ]
  },

  'M29-form-request': {
    kind: 'model_form',
    model: 'fix.access.request',
    title: 'Access Request',
    back: 'M29-requests',
    status: { field: 'state', labels: {
      submitted: 'Submitted', approved: 'Approved', rejected: 'Rejected',
      granted: 'Granted', revoked: 'Revoked' } },
    sections: [
      { title: 'Request', note: 'Submitted → approved → granted. Granting writes the role\'s Odoo groups onto the user (a real change); a revoke removes them. The decision is made by the Approve / Reject actions — never typed (X1: the requester and the beneficiary cannot decide their own request).',
        fields: [
          { name: 'request_type', required: true, label: 'Request Type' },
          { name: 'user_id', required: true, label: 'User' },
          { name: 'role_id', required: true, label: 'Role' },
          { name: 'requested_on', required: true, label: 'Requested On' },
          { name: 'valid_until', label: 'Valid Until' }
        ] },
      { title: 'Justification', fields: [
          { name: 'reason', required: true, type: 'text', label: 'Reason' }
        ] },
      { title: 'Decision Record (read-only)', note: 'The approval is written by the Approve / Reject actions under two-person control (X1) — the requester and the beneficiary can never decide their own request, so the stamp is never typed.',
        fields: [
          { name: 'requested_by_id', readonly: true, label: 'Requested By' },
          { name: 'approver_id', readonly: true, label: 'Approver' },
          { name: 'decided_on', readonly: true, label: 'Decided On' },
          { name: 'decision_note', readonly: true, label: 'Decision Note' }
        ] }
    ]
  },

  'M29-form-session': {
    kind: 'model_form',
    model: 'fix.privileged.session',
    title: 'Privileged Session',
    back: 'M29-sessions',
    status: { field: 'state', labels: { open: 'Open', closed: 'Closed' } },
    sections: [
      { title: 'Session', note: 'Opened before sudo/admin work; closing measures the duration from the timestamps. Every privileged session must carry a reason. State changes only through the Close Session action (your own session) or the timeout cron.',
        fields: [
          { name: 'user_id', required: true, label: 'User' },
          { name: 'access_kind', required: true, label: 'Access Kind' },
          { name: 'reason', required: true, label: 'Reason' },
          { name: 'ticket_ref', label: 'Ticket / Change Ref' },
          { name: 'started_at', label: 'Started At' },
          { name: 'actions_count', label: 'Actions Performed' },
          { name: 'ended_at', readonly: true, label: 'Ended At' },
          { name: 'duration_minutes', readonly: true, label: 'Duration (minutes, measured)' }
        ] }
    ]
  },

  'M29-form-sodtest': {
    kind: 'model_form',
    model: 'fix.sod.test',
    title: 'SoD Test Run',
    back: 'M29-sodtests',
    status: { field: 'result', labels: { pass: 'Pass', fail: 'Fail' } },
    sections: [
      { title: 'Test', note: 'Running the test measures users who actually hold BOTH roles\' Odoo groups — the result and the conflicting logins are computed, not typed.',
        fields: [
          { name: 'control_id', required: true, label: 'SoD Control' },
          { name: 'tested_on', required: true, label: 'Tested On' },
          { name: 'tested_by_id', label: 'Tested By' },
          { name: 'users_checked', label: 'Users Checked' },
          { name: 'violations_found', readonly: true, label: 'Conflicts Found' },
          { name: 'users_in_conflict', readonly: true, label: 'Conflicting Users' }
        ] }
    ]
  },

  'M29-form-sensitive': {
    kind: 'model_form',
    model: 'fix.sensitive.field',
    title: 'Sensitive Field',
    back: 'M29-sensitive',
    sections: [
      { title: 'Classification', note: 'A field is classified once per company (database UNIQUE). The masking rule states how it is rendered; the lawful basis is the PDPA basis for processing it.',
        fields: [
          { name: 'model_name', required: true, label: 'Model' },
          { name: 'field_name', required: true, label: 'Field' },
          { name: 'sensitivity', required: true, label: 'Sensitivity (S0–S3)' },
          { name: 'data_class', required: true, label: 'Data Class' },
          { name: 'masking_rule', required: true, label: 'Masking Rule' },
          { name: 'lawful_basis', label: 'Lawful Basis' },
          { name: 'retention_note', label: 'Retention Note' },
          { name: 'active', label: 'Active' }
        ] }
    ]
  },

  /* ===== triage coverage screens ===== */
  'M29-isolation-tier': { kind: 'model_list', model: 'fix.isolation.tier',
    cols: ['name', 'code', 'record_rule_domain', 'requires_step_up', 'requires_audit', 'fix_role_roll'] },

  'M29-form-isolation-tier': {
    kind: 'model_form',
    model: 'fix.isolation.tier',
    title: "Isolation Tier",
    back: 'M29-isolation-tier',
    sections: [
      { title: "Isolation Tier", note: "Opened from the module's own record set. Every field here is the model's real field; the workflow rules live on the model and are not bypassed by this form.",
        fields: [
          { name: 'code', required: true, label: "Tier" },
          { name: 'name', label: "Name" },
          { name: 'description', type: 'text', label: "Description" },
          { name: 'record_rule_domain', label: "Record Rule Domain" },
          { name: 'requires_step_up', label: "Requires Step Up" },
          { name: 'requires_audit', label: "Requires Audit" },
          { name: 'fix_role_roll', readonly: true, label: "Roles with Access (read-only roll)" }
        ] }
    ]
  },

};

export const REPORT_ROUTES = {
  'M29:Access Review Pack': 'M29-rpt-review',
  'M29:Privileged Session Log': 'M29-rpt-sessions',
  'M29:Sensitive-Data Access': 'M29-rpt-sensitive',
  'M29:SoD Test Results': 'M29-rpt-sod',
  'M29:Authentication Trends': 'M29-rpt-auth'
};

export const FORM_MODELS = {
  'M29:User': 'res.users',
  'M29:Role': 'fix.role',
  'M29:Record Rule': 'ir.rule',
  'M29:Access Request': 'fix.access.request'
};

export const FORM_CHIPS = {
  'M29:User': 'M29-form-user',
  'M29:Role': 'M29-form-role',
  'M29:Record Rule': 'M29-form-rule',
  'M29:Access Request': 'M29-form-request',
  'M29:SoD Control': 'M29-form-sodcontrol',
  'M29:Field Rule': 'M29-form-fieldrule',
  'M29:JML Event': 'M29-form-jml',
  'M29:Certification Line': 'M29-form-cert',
  'M29:Encryption Key': 'M29-form-key',
  'M29:Security Incident': 'M29-form-incident',
  'M29:Model Access': 'M29-form-acl',
  'M29:__by_model__': {
    'fix.isolation.tier': 'M29-form-isolation-tier',
    'res.users': 'M29-form-user',
    'fix.role': 'M29-form-role',
    'ir.rule': 'M29-form-rule',
    'fix.field.rule': 'M29-form-fieldrule',
    'ir.model.access': 'M29-form-acl',
    'fix.access.request': 'M29-form-request',
    'fix.access.certification': 'M29-form-cert',
    'fix.jml.event': 'M29-form-jml',
    'fix.sensitive.field': 'M29-form-sensitive',
    'fix.encryption.key': 'M29-form-key',
    'fix.security.incident': 'M29-form-incident',
    'fix.privileged.session': 'M29-form-session',
    'fix.sod.test': 'M29-form-sodtest',
    'fix.sod.control': 'M29-form-sodcontrol'
  },
  'M29:__by_screen__': {
    'M29-isolation-tier': 'M29-form-isolation-tier',
    'M29-users': 'M29-form-user',
    'M29-roles': 'M29-form-role',
    'M29-record': 'M29-form-rule',
    'M29-fields': 'M29-form-fieldrule',
    'M29-acl': 'M29-form-acl',
    'M29-requests': 'M29-form-request',
    'M29-cert': 'M29-form-cert',
    'M29-jml': 'M29-form-jml',
    'M29-classification': 'M29-form-sensitive',
    'M29-keys': 'M29-form-key',
    'M29-incidents': 'M29-form-incident',
    'M29-privileged': 'M29-form-session',
    'M29-sodtests': 'M29-form-sodtest',
    'M29-sod': 'M29-form-sodcontrol'
  }
};

export const CREATE = {
  M29: { screen: 'M29-form-request', model: 'fix.access.request', label: 'Access Request' }
};
