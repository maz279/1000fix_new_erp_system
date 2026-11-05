/** @odoo-module **/
/* A12 · Platform & Technology — M29 Identity, Access & Security.
 * Registry-faithful: 4 groups / 13 screens / 5 reports / 4 forms / freg 78.
 * Scope note: field-level reads are not instrumented, so the sensitive-data
 * pack reports the CLASSIFIED exposure surface, never invented read counts. */

export const MODULE = {
  area: 'A12', code: 'M29', en: 'Identity, Access & Security', title: 'M29 · Identity, Access & Security',
  bn: 'পরিচয়, অ্যাক্সেস ও নিরাপত্তা', icon: '🛡️',
  desc: 'Users, business roles and Odoo groups; access requests that really grant or revoke a group; record and field rules; SoD controls with measured conflict tests; privileged sessions; and the sensitive-field classification behind the PDPA review.',
  kpis: [
    { l: 'Active Users', m: 'users_active' },
    { l: 'Active Roles', m: 'roles_active' },
    { l: 'Requests Open', m: 'requests_open' },
    { l: 'Sessions Open', m: 'sessions_open' },
    { l: 'SoD Failures', m: 'sod_failures' }
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
    cols: ['login', 'name', 'login_date', 'active'] },
  'M29-sessions': { kind: 'model_list', model: 'res.device.log', create: false,
    cols: ['user_id', 'platform', 'browser', 'ip_address', 'country', 'last_activity', 'revoked'] },
  'M29-jml': { kind: 'model_list', model: 'fix.jml.event', stateField: 'state',
    cols: ['name', 'event_type', 'employee_id', 'user_id', 'role_id', 'effective_on', 'result_note', 'state'],
    actions: [{ m: 'action_apply', l: 'Apply' }, { m: 'action_cancel', l: 'Cancel' }] },

  /* ---- Access ---- */
  'M29-roles': { kind: 'model_list', model: 'fix.role',
    cols: ['code', 'name', 'group_id', 'keycloak_role', 'active'] },
  'M29-record': { kind: 'model_list', model: 'ir.rule',
    cols: ['name', 'model_id', 'groups', 'perm_read', 'perm_write', 'perm_create', 'perm_unlink'] },
  'M29-fields': { kind: 'model_list', model: 'fix.field.rule',
    cols: ['model_id', 'field_id', 'role_ids', 'permission'] },
  'M29-cert': { kind: 'model_list', model: 'fix.access.certification', stateField: 'decision',
    cols: ['name', 'period', 'user_id', 'role_id', 'reviewer_id', 'decision'],
    actions: [{ m: 'action_certify', l: 'Certify' }, { m: 'action_revoke', l: 'Revoke' }] },
  'M29-requests': { kind: 'model_list', model: 'fix.access.request', stateField: 'state',
    cols: ['name', 'request_type', 'user_id', 'role_id', 'requested_on', 'valid_until', 'state'],
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
  'M29-audit': { kind: 'model_list', model: 'fix.security.audit', create: false,
    cols: ['sequence', 'occurred_at', 'actor_id', 'event', 'object_ref', 'detail', 'entry_hash'] },
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
  'M29-form-user': {
    kind: 'model_form',
    model: 'res.users',
    title: 'User',
    back: 'M29-users',
    sections: [
      { title: 'User', note: 'A login. Groups are NOT edited here — role assignment goes through an access request so the grant is approved and recorded.',
        fields: [
          { name: 'name', required: true, label: 'Full Name' },
          { name: 'login', required: true, label: 'Login' },
          { name: 'email', label: 'Email' },
          { name: 'phone', label: 'Phone' },
          { name: 'active', label: 'Active' }
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
          { name: 'custodian_id', label: 'Custodian' }
        ] }
    ]
  },

  'M29-form-incident': {
    kind: 'model_form',
    model: 'fix.security.incident',
    title: 'Security Incident',
    back: 'M29-incidents',
    status: { field: 'state', labels: { open: 'Open', contained: 'Contained', closed: 'Closed' } },
    sections: [
      { title: 'Incident', note: 'Open → contained (the containment note is required) → closed. Closing also requires a root cause, and a data-leak needs the breach assessment. Severity is set by the Set Severity action under two-person control — a second person must confirm — so it is never typed here.',
        fields: [
          { name: 'title', required: true, label: 'Title' },
          { name: 'category', required: true, label: 'Category' },
          { name: 'detected_at', required: true, label: 'Detected At' },
          { name: 'detected_by_id', label: 'Detected By' },
          { name: 'affected_user_id', label: 'Affected User' },
          { name: 'session_id', label: 'Related Privileged Session' }
        ] },
      { title: 'Narrative', fields: [
          { name: 'description', type: 'text', label: 'What happened' },
          { name: 'containment', type: 'text', label: 'Containment' },
          { name: 'root_cause', type: 'text', label: 'Root cause (required to close)' },
          { name: 'breach_assessment', type: 'text', label: 'Breach assessment (required to close a data leak)' }
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
          { name: 'active', label: 'Active' }
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
          { name: 'actions_count', label: 'Actions Performed' }
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
          { name: 'users_checked', label: 'Users Checked' }
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
    cols: ['name', 'code', 'record_rule_domain', 'requires_step_up', 'requires_audit'] },

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
          { name: 'record_rule_domain', label: "Record Rule Domain" },
          { name: 'requires_step_up', label: "Requires Step Up" },
          { name: 'requires_audit', label: "Requires Audit" }
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
