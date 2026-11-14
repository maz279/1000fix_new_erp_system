/** @odoo-module **/
/* A12 · Platform & Technology — M29 Identity, Access & Security.
 * Registry-faithful: 4 groups / 13 screens / 5 reports / 4 forms / freg 78.
 * Scope note: individual reads are not logged, so the sensitive-data pack
 * reports the CLASSIFIED exposure surface, never invented read counts.
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
    { l: 'SoD Tests', m: 'sod_tests' },
    { l: 'Critical Vulns Past Due', m: 'critical_vulns_overdue' }
  ],
  groups: [
    { en: 'Record Coverage', screens: [
      { id: 'M29-isolation-tier', en: "Isolation Tier", bn: "Isolation Tier", t: 'g' }
    ]},
    { en: 'Identity', screens: [
      { id: 'M29-users', en: 'Users', bn: 'ব্যবহারকারী', t: 'g' },
      { id: 'M29-sessions', en: 'Sessions & Device Trust', bn: 'সেশন', t: 'g' },
      { id: 'M29-jml', en: 'JML Automation', bn: 'জেএমএল', t: 'g' },
      { id: 'M29-module-permissions', en: 'Module Permissions', bn: 'মডিউল অনুমতি', t: 'g' }
    ]},
    { en: 'Access', screens: [
      { id: 'M29-roles', en: 'Roles & Permission Sets', bn: 'ভূমিকা', t: 'g' },
      { id: 'M29-record', en: 'Record Rules (T0–T5)', bn: 'রেকর্ড নিয়ম', t: 'g' },
      { id: 'M29-fields', en: 'Field-Level Permissions', bn: 'ক্ষেত্র-স্তরের অনুমতি', t: 'g' },
      { id: 'M29-cert-campaigns', en: 'Certification Campaigns', bn: 'সার্টিফিকেশন ক্যাম্পেইন', t: 'g' },
      { id: 'M29-cert', en: 'Access Certification', bn: 'অ্যাক্সেস সার্টিফিকেশন', t: 'g' },
      { id: 'M29-assignments', en: 'Role Assignments', bn: 'ভূমিকা বরাদ্দ', t: 'g' },
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
      { id: 'M29-vulnerabilities', en: 'Vulnerability Register', bn: 'দুর্বলতা নিবন্ধন', t: 'g' },
      { id: 'M29-sod', en: 'SoD Controls', bn: 'SoD নিয়ন্ত্রণ', t: 'g' },
      { id: 'M29-sodtests', en: 'SoD Test Runs', bn: 'SoD পরীক্ষা', t: 'g' },
      { id: 'M29-sod-exceptions', en: 'SoD Exceptions', bn: 'SoD ব্যতিক্রম', t: 'g' },
      { id: 'M29-rpt-sod-violations', en: 'SoD Violations', bn: 'SoD লঙ্ঘন', t: 'r' }
    ]}
  ],
  reports: ['Access Review Pack', 'Privileged Session Log', 'Sensitive-Data Access', 'SoD Test Results', 'Authentication Trends', 'SoD Violations', 'Vulnerability Register'],
  forms: ['User', 'Role', 'Record Rule', 'Access Request'],
  cross: ['M28 credentials', 'M60 controls', 'M24 retention', 'M33 party master'],
  /* Capture audit 2026-11-14: every sub-module page captures the records it
   * covers. Before, Identity & MFA and Monitoring & Audit had no capture at all,
   * SoD Testing and Data Protection offered no form beyond their "+ New", and
   * Certification Campaigns, Role Assignments and SoD Exceptions sat on no page.
   *   1 Identity: logins come from onboarding (employee.joined -> Keycloak SSO),
   *     so the page captures the identity-lifecycle event, not a blank login.
   *   7 Monitoring: the audit trail is system-written; the page reports an
   *     incident (which writes its own audit row), requests break-glass access
   *     and records a vulnerability (spec §10.1 fix.vulnerability). */
  freg: { src: 78, sub: [
    ['1', 'Identity & MFA', 14, { model: 'res.users', cols: ['login', 'partner_id', 'company_id', 'active', 'create_date'], screens: ['M29-users', 'M29-jml', 'M29-module-permissions', 'M29-sessions'], reports: ['Authentication Trends'], forms: ['Provision Login', 'JML Event', 'User'], create: 'M29-form-provision', domain: [['share', '=', false]] }],
    ['2', 'Role & Group Model', 13, { model: 'fix.role', cols: ['code', 'name', 'fix_group_roll', 'keycloak_role', 'active'], screens: ['M29-roles', 'M29-groups', 'M29-acl'], reports: ['Access Review Pack'], forms: ['Role', 'Model Access'] }],
    ['3', 'Record & Field Rules', 15, { model: 'ir.rule', cols: ['name', 'model_id', 'perm_read', 'perm_write', 'global'], screens: ['M29-record', 'M29-fields', 'M29-isolation-tier'], reports: [], forms: ['Record Rule', 'Field Rule', 'Isolation Tier'] }],
    ['4', 'Access Requests', 10, { model: 'fix.access.request', cols: ['name', 'request_type', 'user_id', 'role_id', 'state'], screens: ['M29-requests', 'M29-cert-campaigns', 'M29-cert', 'M29-assignments'], reports: ['Access Review Pack'], forms: ['Access Request', 'Certification Campaign', 'Certification Line'] }],
    ['5', 'SoD Testing', 9, { model: 'fix.sod.test', cols: ['name', 'control_id', 'tested_on', 'violations_found', 'result'], screens: ['M29-sodtests', 'M29-sod', 'M29-sod-exceptions'], reports: ['SoD Test Results', 'SoD Violations'], forms: ['SoD Test Run', 'SoD Control', 'SoD Exception'] }],
    ['6', 'Data Protection', 10, { model: 'fix.sensitive.field', cols: ['model_name', 'field_name', 'sensitivity', 'data_class', 'masking_rule'], screens: ['M29-classification', 'M29-keys', 'M29-residency'], reports: ['Sensitive-Data Access'], forms: ['Sensitive Field', 'Encryption Key'] }],
    ['7', 'Monitoring & Audit', 7, { model: 'fix.security.audit', cols: ['sequence', 'occurred_at', 'actor_id', 'event', 'object_label'], screens: ['M29-audit', 'M29-incidents', 'M29-privileged', 'M29-vulnerabilities'], reports: ['Privileged Session Log', 'Sensitive-Data Access', 'Vulnerability Register'], forms: ['Security Incident', 'Privileged Session', 'Vulnerability'], create: 'M29-form-incident' }]
  ] }
};

export const SCREENS = {
  /* ---- Identity ---- */
  // logins are never typed blank: "+ Provision a New Login" files the joiner
  // event that creates the login when a second person applies it
  'M29-users': { kind: 'model_list', model: 'res.users', create: false, newForm: 'M29-form-provision',
    cols: ['login', 'name', 'fix_role_codes', 'company_id', 'default_operating_unit_id', 'login_date', 'active'] },
  'M29-sessions': { kind: 'model_list', model: 'res.device.log', create: false,
    cols: ['user_id', 'platform', 'browser', 'ip_address', 'country', 'last_activity', 'revoked'] },
  // who has narrowed access to which module (written by applied events only)
  'M29-module-permissions': { kind: 'model_list', model: 'fix.module.permission', create: false,
    empty: 'No narrowed module permissions: every user has exactly what their roles give.',
    cols: ['user_id', 'area', 'module_name', 'level', 'can_approve', 'can_print', 'can_export', 'can_email', 'event_id', 'set_on'] },
  'M29-jml': { kind: 'model_list', model: 'fix.jml.event', stateField: 'state',
    cols: ['name', 'event_type', 'employee_id', 'user_id', 'role_id', 'effective_on', 'applied_on', 'result_note', 'state'],
    actions: [{ m: 'action_apply', l: 'Apply' }, { m: 'action_cancel', l: 'Cancel' }] },
  // What "held" means: who was actually given which role. Written by the grant paths only.
  'M29-assignments': { kind: 'model_list', model: 'fix.role.assignment', create: false,
    cols: ['user_id', 'role_id', 'request_id', 'granted_on', 'ended_on', 'end_reason', 'is_live'] },

  /* ---- Access ---- */
  'M29-roles': { kind: 'model_list', model: 'fix.role',
    cols: ['code', 'name', 'fix_group_roll', 'keycloak_role', 'active'] },
  'M29-record': { kind: 'model_list', model: 'ir.rule',
    cols: ['name', 'model_id', 'groups', 'perm_read', 'perm_write', 'perm_create', 'perm_unlink'] },
  'M29-fields': { kind: 'model_list', model: 'fix.field.rule',
    cols: ['model_id', 'field_id', 'fix_role_roll', 'permission', 'active'] },
  // E17: one review period. Generate writes a locked line per user and role held.
  'M29-cert-campaigns': { kind: 'model_list', model: 'fix.access.certification.campaign', stateField: 'state',
    cols: ['name', 'period', 'due_on', 'line_count', 'pending_count', 'generated_on', 'generated_by_id', 'no_reviewer_note', 'state'],
    actions: [{ m: 'action_generate', l: 'Generate Lines' }] },
  'M29-cert': { kind: 'model_list', model: 'fix.access.certification', stateField: 'decision',
    cols: ['name', 'campaign_id', 'period', 'user_id', 'role_id', 'reviewer_id', 'due_on', 'decided_on', 'decision'],
    actions: [{ m: 'action_certify', l: 'Certify' }, { m: 'action_revoke', l: 'Revoke' }] },
  'M29-requests': { kind: 'model_list', model: 'fix.access.request', stateField: 'state',
    cols: ['name', 'request_type', 'user_id', 'role_id', 'requested_by_id', 'approver_id', 'requested_on', 'valid_until', 'state'],
    actions: [{ m: 'action_approve', l: 'Approve' },
              { m: 'action_reject', l: 'Reject', ask: 'Why is this request rejected?', kwarg: 'reason' },
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
    actions: [{ m: 'action_rotate', l: 'Register Rotation', ask: 'New vault reference (vault://...) of the key you rotated in the secret manager', kwarg: 'new_vault_ref' }] },

  /* ---- Monitoring ---- */
  // Append-only: entries are written by the system, never typed (+ New suppressed).
  // Verify Chain (R5) recomputes every row's hash and checks the links —
  // the summary (entries checked, discontinuities) is the report.
  'M29-audit': { kind: 'model_list', model: 'fix.security.audit', create: false,
    cols: ['sequence', 'occurred_at', 'actor_id', 'event', 'object_label', 'detail', 'entry_hash'],
    actions: [{ m: 'action_verify_chain', l: 'Verify Chain' }] },
  'M29-privileged': { kind: 'model_list', model: 'fix.privileged.session', stateField: 'state',
    cols: ['name', 'user_id', 'access_kind', 'ticket_ref', 'approver_id', 'started_at', 'expires_at', 'duration_minutes', 'state'],
    actions: [{ m: 'action_approve', l: 'Approve' },
              { m: 'action_reject', l: 'Reject', ask: 'Why is this session refused?', kwarg: 'reason' },
              { m: 'action_open', l: 'Open Session' },
              { m: 'action_close', l: 'Close Session' }] },
  'M29-incidents': { kind: 'model_list', model: 'fix.security.incident', stateField: 'state',
    cols: ['name', 'title', 'category', 'severity', 'severity_pending', 'detected_at', 'affected_user_id', 'state'],
    actions: [{ m: 'action_contain', l: 'Contain' }, { m: 'action_close', l: 'Close' },
              { m: 'action_set_severity', l: 'Propose Severity', ask: 'New severity: low, medium, high or critical', kwarg: 'severity' },
              { m: 'action_confirm_severity', l: 'Confirm Severity' },
              { m: 'action_reject_severity', l: 'Refuse Severity Change' }] },
  // Capture audit 2026-11-14 (spec §10.1, BRU-SEC-21, AC-23): scan and pen-test
  // findings tracked to a second person's verified closure. A reporter and the
  // remediation owner see their own findings; a Security Officer sees all.
  'M29-vulnerabilities': { kind: 'model_list', model: 'fix.vulnerability', stateField: 'state',
    cols: ['name', 'title', 'severity', 'source', 'component', 'owner_id', 'discovered_on', 'sla_due', 'is_overdue', 'state'],
    actions: [{ m: 'action_remediate', l: 'Mark Remediated', ask: 'What was done to remediate it?', kwarg: 'note', states: ['open'] },
              { m: 'action_verify', l: 'Verify Closed', states: ['remediated'] },
              { m: 'action_reopen', l: 'Send Back', ask: 'Why did the remediation not hold?', kwarg: 'note', states: ['remediated'] },
              { m: 'action_accept_risk', l: 'Accept Risk', ask: 'Reason and mitigating control for accepting this risk (runs for the configured period, 90 days by default)', kwarg: 'reason', states: ['open'] }] },
  'M29-sod': { kind: 'model_list', model: 'fix.sod.control',
    cols: ['code', 'name', 'control_type', 'pair_label', 'measurable', 'conflict_action', 'active'] },
  // A08 S4 / FR-SEC-024: the only way past a blocked duty conflict is a time-boxed
  // exception with a mitigating control, approved by someone other than the grantee.
  'M29-sod-exceptions': { kind: 'model_list', model: 'fix.sod.mitigation', stateField: 'state',
    cols: ['name', 'control_id', 'user_id', 'valid_from', 'valid_until', 'approved_by_id', 'is_live', 'state'],
    actions: [{ m: 'action_approve', l: 'Approve' }, { m: 'action_reject', l: 'Reject' }, { m: 'action_revoke', l: 'Revoke' }] },
  'M29-sodtests': { kind: 'model_list', model: 'fix.sod.test', stateField: 'result',
    cols: ['name', 'control_id', 'tested_on', 'users_checked', 'violations_found', 'result'],
    actions: [{ m: 'action_run', l: 'Run Test' }] },

  /* ---- report screens (own pack each) ---- */
  'M29-rpt-review': { kind: 'table_report', module: 'M29', report: 'access_review', title: 'Access Review Pack', period: false },
  'M29-rpt-sessions': { kind: 'table_report', module: 'M29', report: 'privileged_sessions', title: 'Privileged Session Log', period: false },
  'M29-rpt-sensitive': { kind: 'table_report', module: 'M29', report: 'sensitive_access', title: 'Sensitive-Data Access', period: false },
  'M29-rpt-sod': { kind: 'table_report', module: 'M29', report: 'sod_results', title: 'SoD Test Results', period: false },
  'M29-rpt-sod-violations': { kind: 'table_report', module: 'M29', report: 'sod_violations', title: 'SoD Violations', period: false },
  'M29-rpt-auth': { kind: 'table_report', module: 'M29', report: 'auth_trends', title: 'Authentication Trends', period: false },
  'M29-rpt-vulns': { kind: 'table_report', module: 'M29', report: 'vulnerability_register', title: 'Vulnerability Register', period: false },

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
    // a login is provisioned by onboarding (employee.joined -> Keycloak SSO), never
    // typed here: a blank create skipped the joiner path, its SoD gate and its audit
    create: false,
    pick: 'Logins come from onboarding (Keycloak SSO). Open a user from the list, or record a Joiner / Mover / Leaver event.',
    status: { field: 'active', labels: { true: 'Active', false: 'Inactive' } },
    tabs: [
      { id: 'general', label: '1. General & Photo', bn: '১. সাধারণ তথ্য ও ছবি', icon: '👤', badge: '9' },
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
          { name: 'work_email', label: 'Work Email' }
        ] },
      { tab: 'general', title: 'Account State', note: 'Deactivating here only switches the login off, and is audited. For a leaver use the JML leaver event: it also removes every group and API key and unassigns ITSM assets. A login deprovisioned by a leaver event comes back only through a joiner event.',
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
      { tab: 'org', title: 'Data Isolation', note: 'Rows are scoped by company and by the record rules (Record Rules screen). The tiers T0–T5 on the Isolation Tier screen are a documented register, not a gate. Allowed companies is a data-scope change owned by the multi-entity substrate — shown read-only.',
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
      { tab: 'access', title: 'Entitlement (read-only)', note: 'What this user holds: roles actually assigned (Role Assignments screen), the employee master, and groups only one role maps to. A group several roles share names none of them. The same measurement the Access Review pack reports. Groups are NOT edited here: every grant goes through an approved access request (two-person, SoD-checked). Use the Access Requests screen to grant or revoke.',
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
    newLabel: 'Record a Joiner / Mover / Leaver',
    back: 'M29-jml',
    status: { field: 'state', labels: { pending: 'Pending', applied: 'Applied', cancelled: 'Cancelled' } },
    sections: [
      { title: 'Joiner / Mover / Leaver', note: 'Applying a joiner grants every Odoo group mapped to the chosen role (blocked if a SoD control forbids the combination). A mover also revokes the roles previously assigned. A leaver removes ALL groups and API keys and deactivates the user, and cannot be applied before its date. The login is the employee\'s own; for an employee with no login, a joiner creates it from the work email when it is applied (or use Provision a New Login). Additional roles pass the same SoD gate; the data scope sets the operating units the person sees (a mover replaces it). A second person applies: not the one affected and not the one who filed it.',
        fields: [
          { name: 'event_type', required: true, label: 'Event Type' },
          { name: 'employee_id', required: true, label: 'Employee' },
          { name: 'user_id', label: 'Portal User' },
          { name: 'role_id', label: 'Role to Apply' },
          { name: 'extra_role_ids', type: 'many2many', label: 'Additional Roles' },
          { name: 'operating_unit_ids', type: 'many2many', label: 'Allowed Operating Units' },
          { name: 'default_operating_unit_id', label: 'Default Operating Unit' },
          { name: 'effective_on', required: true, label: 'Effective On' },
          { name: 'valid_until', label: 'Access Valid Until' },
          { name: 'reason', type: 'text', label: 'Business Justification' }
        ] },
      { title: 'What This Grants (read-only)', note: 'Computed when you save: the permission groups of each role, the data scope and any duty conflict between the chosen roles. Nothing is granted yet: a second person (an Access Approver who is neither you nor the person) applies it from JML Automation.',
        fields: [
          { name: 'proposed_login', readonly: true, label: 'Login' },
          { name: 'permission_preview', type: 'text', readonly: true, label: 'Permission Preview' }
        ] },
      { title: 'Application Result (read-only)', note: 'Stamped by the Apply action: when it ran and exactly what it did (groups granted, or the leaver deprovisioning count).',
        fields: [
          { name: 'applied_on', readonly: true, label: 'Applied On' },
          { name: 'result_note', readonly: true, label: 'Result' }
        ] }
    ],
    lines: {
      field: 'permission_line_ids',
      title: 'Module Permissions (joiner / mover)',
      fixedRows: true,
      note: 'Fills in from the roles when you save. Narrow a module by lowering its Access Level (No access denies it) or unticking Approve, Print, Export or E-mail. A mover replaces the person\'s previous narrowing.',
      fields: [
        { name: 'area', readonly: true, label: 'Business Area' },
        { name: 'module_name', readonly: true, label: 'Module' },
        { name: 'allowed_label', readonly: true, label: 'Roles Allow' },
        { name: 'level', type: 'selection', label: 'Access Level' },
        { name: 'can_approve', type: 'boolean', label: 'Approve' },
        { name: 'can_print', type: 'boolean', label: 'Print' },
        { name: 'can_export', type: 'boolean', label: 'Export' },
        { name: 'can_email', type: 'boolean', label: 'E-mail' }
      ]
    }
  },

  /* Provision a New Login (M29 capture audit 2026-11-14, FR-SEC-001/027,
   * AUT-SEC-01). A joiner event for an employee with no login, stating what
   * the person may access: the roles (each through the SoD gate) and the data
   * scope. Applying it - by a second person - creates the login from the work
   * email, links it to the employee, grants the roles, sets the scope, queues
   * the invitation and writes the audit row. */
  'M29-form-provision': {
    kind: 'model_form',
    model: 'fix.jml.event',
    title: 'New User',
    newLabel: 'Provision a New Login',
    back: 'M29-users',
    status: { field: 'state', labels: { pending: 'Draft - awaiting a second approver', applied: 'Login Created', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'person', label: '1. Person', bn: '১. ব্যক্তি', icon: '👤', badge: '9' },
      { id: 'roles', label: '2. Roles', bn: '২. ভূমিকা', icon: '🗝️', badge: '3' },
      { id: 'scope', label: '3. Data Scope', bn: '৩. ডেটা পরিধি', icon: '🏢', badge: '2' },
      { id: 'perms', label: '4. Module Permissions', bn: '৪. মডিউল অনুমতি', icon: '☑️', badge: 'Checklist' },
      { id: 'validity', label: '5. Validity & Security', bn: '৫. মেয়াদ ও নিরাপত্তা', icon: '⏳', badge: '2' },
      { id: 'review', label: '6. Review & Approval', bn: '৬. পর্যালোচনা ও অনুমোদন', icon: '✅', badge: '3' }
    ],
    sections: [
      { tab: 'person', title: 'Who is joining', note: 'Step 1 of 6. Pick the employee from HR - only people who do not have a login yet are listed. Their HR details below come from the employee master (read-only) and appear when you save the draft.',
        fields: [
          { name: 'employee_id', required: true, label: 'Employee', domain: [['user_id', '=', false]] },
          { name: 'effective_on', required: true, label: 'Start Date' },
          { name: 'emp_code', readonly: true, label: 'Employee Code' },
          { name: 'emp_job', readonly: true, label: 'Job Title' },
          { name: 'emp_department', readonly: true, label: 'Department' },
          { name: 'emp_unit', readonly: true, label: 'Operating Unit' },
          { name: 'emp_manager', readonly: true, label: 'Line Manager' },
          { name: 'emp_phone', readonly: true, label: 'Work Phone' }
        ] },
      { tab: 'person', title: 'Login & preferences', note: 'The login is the work email from the employee master (the 1000 FiX convention). If it is empty, set it in HR first. An address that is already a login is refused, never duplicated.',
        fields: [
          { name: 'proposed_login', readonly: true, label: 'Login (work email)' },
          { name: 'lang', label: 'Interface Language' },
          { name: 'tz', label: 'Time Zone' }
        ] },
      { tab: 'roles', title: 'Business roles', note: 'Step 2 of 6. A role is a ready-made bundle of permissions for a job (e.g. Front-Desk Officer, Store Keeper). Choose the main role, and add more only if the job truly needs them. Every role is checked against the segregation-of-duties rules. Save after choosing: the Module Permissions checklist then fills in from these roles.',
        fields: [
          { name: 'role_id', required: true, label: 'Main Role' },
          { name: 'extra_role_ids', type: 'many2many', label: 'Additional Roles' },
          { name: 'reason', type: 'text', required: true, label: 'Business Justification (why this access is needed)' }
        ] },
      { tab: 'scope', title: 'Which branches the person works with', note: 'Step 3 of 6. Records are scoped by operating unit (branch / service centre). Leave empty to use the employee\'s own unit. The default unit is where their new records start.',
        fields: [
          { name: 'operating_unit_ids', type: 'many2many', label: 'Allowed Operating Units' },
          { name: 'default_operating_unit_id', label: 'Default Operating Unit' }
        ] },
      { tab: 'perms', title: 'Set every module at once', note: 'Step 4 of 6. Start from a preset, then adjust single modules in the checklist below. The preset applies when you save and never gives more than the roles allow.',
        fields: [
          { name: 'permission_bulk', label: 'Quick preset for all modules' }
        ] },
      { tab: 'validity', title: 'How long the access lasts', note: 'Step 5 of 6. For a contractor, intern or temporary cover, set an end date: the login is deactivated automatically the day after (groups, API keys and sessions removed, audited). Leave empty for a permanent employee.',
        fields: [
          { name: 'valid_until', label: 'Access Valid Until' }
        ] },
      { tab: 'validity', title: 'Security', note: 'Sign-in: the person receives the standard invitation e-mail to sign in with 1000 FiX single sign-on (Keycloak) or set a password. Multi-factor authentication and session time-outs are enforced by single sign-on for the roles that require them. A second person must approve: this form never creates a login on its own.',
        fields: [] },
      { tab: 'review', title: 'What this grants', note: 'Step 6 of 6. Read this summary before asking for approval: every role\'s permission groups, the branch scope, and any DUTY CONFLICT between the chosen roles (a blocked conflict stops the whole request).',
        fields: [
          { name: 'permission_preview', type: 'text', readonly: true, label: 'Access Summary' }
        ] },
      { tab: 'review', title: 'Approval', note: 'Save, then an Access Approver who is neither you nor the new user opens JML Automation and presses Apply. Applying creates the login, grants every role, applies the checklist and the scope, sends the invitation and writes the audit record - all at once, or nothing if any check refuses.',
        fields: [
          { name: 'applied_on', readonly: true, label: 'Approved & Applied On' },
          { name: 'result_note', readonly: true, label: 'What Was Done' }
        ] }
    ],
    lines: {
      field: 'permission_line_ids',
      tab: 'perms',
      title: 'Module Permissions - what this person may do in each module',
      fixedRows: true,
      note: 'One row per module the chosen roles reach (filled in when you save the roles). Access Level is a ladder - each level includes the ones before it: No access (the module is denied) < View (read only) < Create (view + add new records) < Edit (view + add + change). Approve covers workflow decisions (approve, reject, post, close); Print is PDF; Export is Excel / CSV; E-mail sends reports. "Roles Allow" is the most the roles give: you can narrow any row but never exceed it - for more, add a role. The workspace enforces every choice on each screen, save, approval, print, export and e-mail.',
      fields: [
        { name: 'area', readonly: true, label: 'Business Area' },
        { name: 'module_name', readonly: true, label: 'Module' },
        { name: 'allowed_label', readonly: true, label: 'Roles Allow' },
        { name: 'level', type: 'selection', label: 'Access Level' },
        { name: 'can_approve', type: 'boolean', label: 'Approve' },
        { name: 'can_print', type: 'boolean', label: 'Print' },
        { name: 'can_export', type: 'boolean', label: 'Export' },
        { name: 'can_email', type: 'boolean', label: 'E-mail' }
      ]
    }
  },

  'M29-form-cert': {
    kind: 'model_form',
    model: 'fix.access.certification',
    title: 'Access Certification Line',
    back: 'M29-cert',
    status: { field: 'decision', labels: { pending: 'Pending', certified: 'Certified', revoked: 'Revoked' } },
    sections: [
      { title: 'Certification', note: 'One line per user and role held, normally generated by a Certification Campaign. Empty reviewer: the user\'s manager, or an Access Approver. User, role and reviewer lock once saved. Certifying confirms the access is still needed; revoking removes the role\'s Odoo groups from the user — a real change. The decision comes from the Certify / Revoke actions, and only the reviewer (never the user under review) may make it. Unconfirmed lines past their due date are revoked by the close-out job.',
        fields: [
          { name: 'period', required: true, label: 'Period' },
          { name: 'campaign_id', readonly: true, label: 'Campaign' },
          { name: 'user_id', required: true, label: 'User Under Review' },
          { name: 'role_id', required: true, label: 'Role Held' },
          { name: 'reviewer_id', label: 'Reviewer' },
          { name: 'due_on', label: 'Due On (close-out deadline)' },
          { name: 'decided_on', readonly: true, label: 'Decided On' },
          { name: 'note', label: 'Note' }
        ] }
    ]
  },

  'M29-form-campaign': {
    kind: 'model_form',
    model: 'fix.access.certification.campaign',
    title: 'Certification Campaign',
    back: 'M29-cert-campaigns',
    status: { field: 'state', labels: { draft: 'Draft', generated: 'Generated' } },
    sections: [
      { title: 'Campaign', note: 'Generate Lines writes one locked certification line per internal user and role held, reviewed by the user\'s manager or, failing that, an Access Approver, and never by the user. Lines still pending after the due date are revoked by the close-out job.',
        fields: [
          { name: 'period', required: true, label: 'Period (e.g. 2026-Q4)' },
          { name: 'due_on', required: true, label: 'Due On' },
          { name: 'line_count', readonly: true, label: 'Lines' },
          { name: 'pending_count', readonly: true, label: 'Pending' },
          { name: 'generated_on', readonly: true, label: 'Generated On' },
          { name: 'generated_by_id', readonly: true, label: 'Generated By' },
          { name: 'no_reviewer_note', readonly: true, label: 'Skipped (no reviewer)' }
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
      { title: 'Key', note: 'This register stores a VAULT REFERENCE only — key material is never entered into or stored by this database (SEC-101), and only custodians can read the reference. It must start with vault://; no secret manager is contacted to confirm the path. After saving, the reference changes only through Register Rotation (custodian only), which records a rotation done in the secret manager, retires this key and starts the clock on its successor.',
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
    newLabel: 'Report a Security Incident',
    back: 'M29-incidents',
    status: { field: 'state', labels: { open: 'Open', contained: 'Contained', closed: 'Closed' } },
    tabs: [
      { id: 'facts', label: '1. Incident Facts', bn: '১. ঘটনার তথ্য', icon: '🚨', badge: '7' },
      { id: 'narrative', label: '2. Narrative & Closure', bn: '২. বিবরণ ও সমাপ্তি', icon: '📝', badge: '9' }
    ],
    sections: [
      { tab: 'facts', title: 'Incident', note: 'Anyone may report an incident and read their own reports; a Security Officer handles it and reads them all. Open → contained (the containment note is required) → closed. Closing also requires a root cause, and a data leak needs the breach assessment and stays a data leak. The reporter sets the severity; after that one officer proposes a change and a second officer confirms it. A closed record cannot change.',
        fields: [
          { name: 'title', required: true, label: 'Title' },
          { name: 'category', required: true, label: 'Category' },
          { name: 'severity', required: true, label: 'Severity' },
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
          { name: 'severity_pending', readonly: true, label: 'Severity Proposed' },
          { name: 'severity_proposed_by_id', readonly: true, label: 'Severity Proposed By' },
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
      { title: 'Role', note: 'Role code is R-nn. The role\'s permission groups, listed below, are what an access request actually grants.',
        fields: [
          { name: 'code', required: true, label: 'Role Code (R-nn)' },
          { name: 'name', required: true, label: 'Role Name' },
          { name: 'name_bn', label: 'Role Name (Bengali)' },
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
    back: 'M29-record',
    sections: [
      { title: 'Record Rule', note: 'A record rule restricts which rows a group can see. A global rule (no group) applies to everyone — treat it as a security change.',
        fields: [
          { name: 'name', required: true, label: 'Rule Name' },
          { name: 'fix_model_name', required: true, label: 'Model (technical name, e.g. res.partner)' },
          { name: 'model_id', readonly: true, label: 'Model' },
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
          { name: 'fix_model_name', required: true, label: 'Model (technical name, e.g. res.partner)' },
          { name: 'model_id', readonly: true, label: 'Model' },
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
    back: 'M29-fields',
    sections: [
      { title: 'Field Permission', note: 'Enforced on the P03 workspace screens, in lists and forms: Hidden strips the field, Masked shows ***. Not enforced in the Odoo back end, report packs or exports. An empty role list applies the rule to every caller who is not cleared. A system administrator and a Sensitive Data Clearance holder are always cleared; Read or Write with roles clears those roles for this field.',
        fields: [
          { name: 'fix_model_name', required: true, label: 'Model (technical name, e.g. res.partner)' },
          { name: 'fix_field_name', required: true, label: 'Field (technical name, e.g. phone)' },
          { name: 'model_id', readonly: true, label: 'Model' },
          { name: 'field_id', readonly: true, label: 'Field' },
          { name: 'permission', required: true, label: 'Permission' },
          { name: 'role_ids', type: 'many2many', label: 'Roles' },
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
      { title: 'Segregation of Duties', note: 'A control states two roles that must never be held by the same person. The action decides whether a conflict blocks the grant or only raises a finding, and an approved SoD exception lets one person past it for a stated time. Measurable is false when the two roles share a group. The SoD Test Runs measure it for real.',
        fields: [
          { name: 'code', required: true, label: 'SoD Code' },
          { name: 'name', required: true, label: 'Control Description' },
          { name: 'control_type', required: true, label: 'Pairs' },
          { name: 'role_a_id', label: 'Role A (role pair)' },
          { name: 'role_b_id', label: 'Role B (role pair)' },
          { name: 'group_a_id', label: 'Group A (duty pair)' },
          { name: 'group_b_id', label: 'Group B (duty pair)' },
          { name: 'pair_label', readonly: true, label: 'Pair' },
          { name: 'measurable', readonly: true, label: 'Measurable' },
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
      { title: 'Request', note: 'Submitted → approved → granted. Granting writes the role\'s Odoo groups onto the user (a real change); a revoke removes the groups no other assigned role needs. What was approved cannot change after submission. The decision is made by the Approve / Reject actions — never typed (X1: the requester and the beneficiary cannot decide their own request, or execute it). A temporary elevation runs at most the configured number of days and is revoked by a daily job.',
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
    back: 'M29-privileged',
    status: { field: 'state', labels: { requested: 'Requested', approved: 'Approved', rejected: 'Rejected', open: 'Open', closed: 'Closed', expired: 'Approval Lapsed' } },
    sections: [
      { title: 'Break-Glass Request', note: 'Requested in your own name → an Access Approver who is not you approves it, and the approval sets when it expires → you open it, which writes the audit row and notifies the approvers → you close it, or the timeout job does. This record is the control around privileged work: it does not itself hand out database access.',
        fields: [
          { name: 'access_kind', required: true, label: 'Access Kind' },
          { name: 'reason', required: true, label: 'Reason' },
          { name: 'ticket_ref', label: 'Ticket / Change Ref' },
          { name: 'duration_hours', label: 'Hours Needed (empty = the maximum allowed)' },
          { name: 'actions_count', label: 'Actions Performed' }
        ] },
      { title: 'Decision & Timing (read-only)', note: 'Stamped by the actions. The duration is measured from the timestamps, never typed.',
        fields: [
          { name: 'user_id', readonly: true, label: 'User' },
          { name: 'approver_id', readonly: true, label: 'Approver' },
          { name: 'decided_on', readonly: true, label: 'Decided On' },
          { name: 'decision_note', readonly: true, label: 'Decision Note' },
          { name: 'expires_at', readonly: true, label: 'Expires At' },
          { name: 'started_at', readonly: true, label: 'Started At' },
          { name: 'ended_at', readonly: true, label: 'Ended At' },
          { name: 'duration_minutes', readonly: true, label: 'Duration (minutes, measured)' }
        ] }
    ]
  },

  'M29-form-vulnerability': {
    kind: 'model_form',
    model: 'fix.vulnerability',
    title: 'Vulnerability',
    back: 'M29-vulnerabilities',
    status: { field: 'state', labels: { open: 'Open', remediated: 'Remediated', verified: 'Verified Closed', accepted: 'Risk Accepted' } },
    sections: [
      { title: 'Finding', note: 'A scan, penetration-test or reported weakness. The remediation due date follows the severity: a critical finding is due in 7 days and is escalated if still open after that (BRU-SEC-21). After filing, only a Security Officer re-rates the severity (audited), and nothing about the finding changes once it leaves Open. You and the remediation owner see this record; Security Officers see all.',
        fields: [
          { name: 'title', required: true, label: 'Title' },
          { name: 'severity', required: true, label: 'Severity' },
          { name: 'source', required: true, label: 'Source' },
          { name: 'identifier', label: 'Identifier (CVE / rule / finding ref)' },
          { name: 'component', required: true, label: 'Affected Component' },
          { name: 'discovered_on', required: true, label: 'Discovered On' },
          { name: 'owner_id', label: 'Remediation Owner' },
          { name: 'detail', type: 'text', label: 'Description' }
        ] },
      { title: 'Remediation & Closure (read-only)', note: 'Stamped by the actions: the owner or an officer marks it remediated with a note; a Security Officer who did not remediate it verifies the closure or sends it back. A risk acceptance is an officer decision with a reason, by someone who neither reported nor owns it, and it lapses on its end date.',
        fields: [
          { name: 'sla_due', readonly: true, label: 'Remediation Due' },
          { name: 'reported_by_id', readonly: true, label: 'Reported By' },
          { name: 'remediation_note', readonly: true, label: 'Remediation Note' },
          { name: 'remediated_by_id', readonly: true, label: 'Remediated By' },
          { name: 'remediated_on', readonly: true, label: 'Remediated On' },
          { name: 'verified_by_id', readonly: true, label: 'Verified By' },
          { name: 'verified_on', readonly: true, label: 'Verified On' },
          { name: 'acceptance_reason', readonly: true, label: 'Risk Acceptance Reason' },
          { name: 'accepted_by_id', readonly: true, label: 'Risk Accepted By' },
          { name: 'accepted_until', readonly: true, label: 'Accepted Until' },
          { name: 'escalated_on', readonly: true, label: 'Escalated On' }
        ] }
    ]
  },

  'M29-form-sodexception': {
    kind: 'model_form',
    model: 'fix.sod.mitigation',
    title: 'SoD Exception',
    back: 'M29-sod-exceptions',
    status: { field: 'state', labels: { draft: 'Requested', approved: 'Approved', rejected: 'Rejected', revoked: 'Revoked' } },
    sections: [
      { title: 'Exception', note: 'A time-boxed exception lets one person hold both sides of a duty conflict. It takes effect only when someone other than the grantee and the requester approves it, and it ends on its own date.',
        fields: [
          { name: 'control_id', required: true, label: 'SoD Control' },
          { name: 'user_id', required: true, label: 'Person' },
          { name: 'valid_from', required: true, label: 'Valid From' },
          { name: 'valid_until', required: true, label: 'Valid Until' },
          { name: 'requested_by_id', readonly: true, label: 'Requested By' },
          { name: 'approved_by_id', readonly: true, label: 'Approved By' },
          { name: 'decided_on', readonly: true, label: 'Decided On' },
          { name: 'is_live', readonly: true, label: 'In Force Today' }
        ] },
      { title: 'Justification', fields: [
          { name: 'mitigating_control', type: 'text', required: true, label: 'Mitigating Control' },
          { name: 'reason', type: 'text', required: true, label: 'Reason' }
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
      { title: 'Test', note: 'Running the test measures users who hold BOTH roles (what was assigned, the employee master, groups that name a role). The date, the tester, the counts and the result are stamped by the run, never typed, and a run stays on its control. To re-measure, file a new run; a job also measures every control weekly.',
        fields: [
          { name: 'control_id', required: true, label: 'SoD Control' },
          { name: 'tested_on', readonly: true, label: 'Tested On' },
          { name: 'tested_by_id', readonly: true, label: 'Tested By' },
          { name: 'users_checked', readonly: true, label: 'Users Checked' },
          { name: 'violations_found', readonly: true, label: 'Conflicts Found' },
          { name: 'users_in_conflict', readonly: true, label: 'Conflicting Users' }
        ] }
    ]
  },

  'M29-form-sensitive': {
    kind: 'model_form',
    model: 'fix.sensitive.field',
    title: 'Sensitive Field',
    back: 'M29-classification',
    sections: [
      { title: 'Classification', note: 'A field is classified once per company (database UNIQUE). The masking rule is applied on the P03 workspace screens, in lists and forms, to callers without Sensitive Data Clearance; it is not applied in the Odoo back end, report packs or exports. The lawful basis is the PDPA basis for processing it.',
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
      { title: "Isolation Tier", note: "A documented register: it states what each tier is meant to mean. Nothing reads it to decide access, and the domain here is text, not a live rule. Row scoping is enforced by the Record Rules screen, and residency-classified data by the write-time residency mixin. Only a system administrator edits this.",
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
  'M29:Authentication Trends': 'M29-rpt-auth',
  'M29:SoD Violations': 'M29-rpt-sod-violations',
  'M29:Vulnerability Register': 'M29-rpt-vulns'
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
  'M29:Provision Login': 'M29-form-provision',
  'M29:Certification Campaign': 'M29-form-campaign',
  'M29:Isolation Tier': 'M29-form-isolation-tier',
  'M29:SoD Test Run': 'M29-form-sodtest',
  'M29:SoD Exception': 'M29-form-sodexception',
  'M29:Sensitive Field': 'M29-form-sensitive',
  'M29:Privileged Session': 'M29-form-session',
  'M29:Vulnerability': 'M29-form-vulnerability',
  'M29:__by_model__': {
    'fix.isolation.tier': 'M29-form-isolation-tier',
    'res.users': 'M29-form-user',
    'fix.role': 'M29-form-role',
    'ir.rule': 'M29-form-rule',
    'fix.field.rule': 'M29-form-fieldrule',
    'ir.model.access': 'M29-form-acl',
    'fix.access.request': 'M29-form-request',
    'fix.access.certification': 'M29-form-cert',
    'fix.access.certification.campaign': 'M29-form-campaign',
    'fix.jml.event': 'M29-form-jml',
    'fix.sensitive.field': 'M29-form-sensitive',
    'fix.encryption.key': 'M29-form-key',
    'fix.security.incident': 'M29-form-incident',
    'fix.privileged.session': 'M29-form-session',
    'fix.sod.test': 'M29-form-sodtest',
    'fix.sod.control': 'M29-form-sodcontrol',
    'fix.sod.mitigation': 'M29-form-sodexception',
    'fix.vulnerability': 'M29-form-vulnerability'
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
    'M29-cert-campaigns': 'M29-form-campaign',
    'M29-jml': 'M29-form-jml',
    'M29-classification': 'M29-form-sensitive',
    'M29-keys': 'M29-form-key',
    'M29-incidents': 'M29-form-incident',
    'M29-privileged': 'M29-form-session',
    'M29-sod-exceptions': 'M29-form-sodexception',
    'M29-sodtests': 'M29-form-sodtest',
    'M29-sod': 'M29-form-sodcontrol',
    'M29-vulnerabilities': 'M29-form-vulnerability'
  }
};

export const CREATE = {
  M29: { screen: 'M29-form-request', model: 'fix.access.request', label: 'Access Request' }
};
