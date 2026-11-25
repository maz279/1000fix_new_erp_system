/** @odoo-module **/
/* A09 · People & Workforce — M22 Learning & Certification.
 * Registry-faithful: 4 groups / 11 screens / 5 reports / 4 forms / freg 52.
 * Capture audit 2026-11-13: every sub-module page captures the records it
 * covers (device categories, role paths, budget, over-budget, waivers).
 * Capture audit pass 2 (2026-11-19): role competency requirements on the
 * path (FR-LMS-002) and the role gap analysis (FR-LMS-005), training needs
 * (FR-LMS-031) and plans (FR-LMS-032), participant feedback (FR-LMS-036),
 * withdrawal / substitution (FR-LMS-021), mentoring and its interactions
 * (FR-LMS-028) and the effectiveness evaluation (FR-LMS-035). */

export const MODULE = {
  area: 'A09', code: 'M22', en: 'Learning & Certification', title: 'M22 · Learning & Certification',
  bn: 'প্রশিক্ষণ ও সার্টিফিকেশন', icon: '🎓',
  desc: 'Competency framework, skill matrix and assessments, the certification register with validity and renewal, dispatch eligibility with a hard block on expired certification, the course catalogue and learning paths, schedule/attendance, OJT mentoring, and ISO/brand audit evidence.',
  kpis: [
    { l: 'Certified Technicians', m: 'certified_technicians' },
    { l: 'Expiring (30d)', m: 'expiring_30d' },
    { l: 'Expired Working', m: 'expired_working' },
    { l: 'OJT Hours /tech', m: 'training_hours' },
    { l: 'Brand Certifications', m: 'brand_certifications' },
    { l: 'Assessment Pass Rate', m: 'assessment_pass_rate', suffix: '%' }
  ],
  groups: [
    { en: 'Competency', screens: [
      { id: 'M22-framework', en: 'Competency Framework', bn: 'দক্ষতা কাঠামো', t: 'g' },
      { id: 'M22-devices', en: 'Device Categories & Tiers', bn: 'ডিভাইস ক্যাটাগরি ও স্তর', t: 'g' },
      { id: 'M22-matrix', en: 'Skill Matrix', bn: 'দক্ষতা ম্যাট্রিক্স', t: 'r' },
      { id: 'M22-role-gaps', en: 'Role Gap Analysis', bn: 'ভূমিকা অনুযায়ী দক্ষতা ঘাটতি', t: 'r' },
      { id: 'M22-assessments', en: 'Assessments', bn: 'মূল্যায়ন', t: 'g' }
    ]},
    { en: 'Certifications', screens: [
      { id: 'M22-register', en: 'Certification Register', bn: 'সার্টিফিকেশন রেজিস্টার', t: 'g' },
      { id: 'M22-expiry', en: 'Validity & Renewal', bn: 'মেয়াদ ও নবায়ন', t: 'r' },
      { id: 'M22-eligibility', en: 'Dispatch Eligibility (hard block)', bn: 'ডিসপ্যাচ যোগ্যতা', t: 'g' },
      { id: 'M22-waivers', en: 'Certification Waivers', bn: 'সার্টিফিকেশন ছাড়', t: 'g' }
    ]},
    { en: 'Training', screens: [
      { id: 'M22-needs', en: 'Training Needs', bn: 'প্রশিক্ষণের প্রয়োজন', t: 'g' },
      { id: 'M22-plans', en: 'Training Plans', bn: 'প্রশিক্ষণ পরিকল্পনা', t: 'g' },
      { id: 'M22-catalogue', en: 'Course Catalogue', bn: 'কোর্স তালিকা', t: 'g' },
      { id: 'M22-paths', en: 'Learning Paths', bn: 'শেখার পথ', t: 'g' },
      { id: 'M22-sessions', en: 'Training Sessions', bn: 'প্রশিক্ষণ সেশন', t: 'g' },
      { id: 'M22-schedule', en: 'Schedule & Attendance', bn: 'সূচি ও উপস্থিতি', t: 'g' },
      { id: 'M22-feedback', en: 'Participant Feedback', bn: 'অংশগ্রহণকারীর মতামত', t: 'g' },
      { id: 'M22-budget', en: 'Training Budget', bn: 'প্রশিক্ষণ বাজেট', t: 'g' },
      { id: 'M22-budget-exceptions', en: 'Over-Budget Requests', bn: 'বাজেট-অতিরিক্ত অনুরোধ', t: 'g' },
      { id: 'M22-ojt', en: 'OJT & Mentoring', bn: 'কর্মস্থল প্রশিক্ষণ', t: 'g' },
      { id: 'M22-mentoring', en: 'Mentoring', bn: 'মেন্টরিং', t: 'g' },
      { id: 'M22-mentoring-log', en: 'Mentoring Interactions', bn: 'মেন্টরিং সাক্ষাৎ', t: 'g' }
    ]},
    { en: 'Evidence', screens: [
      { id: 'M22-iso', en: 'ISO / Brand Audit Evidence', bn: 'আইএসও প্রমাণ', t: 'g' },
      { id: 'M22-effectiveness', en: 'Effectiveness Evaluations', bn: 'প্রশিক্ষণের কার্যকারিতা', t: 'g' }
    ]}
  ],
  reports: ['Certification Coverage by Brand', 'Expiry Forecast', 'Training Effectiveness', 'Skill-Gap Heatmap', 'Audit Evidence Pack', 'Dispatch Gate Readiness'],
  forms: ['Certification', 'Course', 'Learning Path', 'Assessment', 'Device Category', 'Training Session', 'Training Budget', 'Over-Budget Request',
          'Training Need', 'Training Plan', 'Training Feedback', 'Mentoring', 'Mentoring Interaction', 'Effectiveness Evaluation'],
  cross: ['M02 Dispatch eligibility', 'M21 Workforce', 'M57 Incentives'],
  freg: { src: 52, sub: [
    ['1', 'Competency Framework', 8, { model: 'fix.competency', cols: ['code', 'name', 'device_category_id', 'repair_tier', 'required_for_dispatch'], screens: ['M22-framework', 'M22-devices', 'M22-paths'], reports: ['Skill-Gap Heatmap'], forms: ['Device Category', 'Learning Path'] }],
    ['2', 'Skill Matrix & Assessment', 10, { model: 'fix.competency.assessment', cols: ['employee_id', 'competency_id', 'assessed_on', 'level', 'passed'], screens: ['M22-assessments', 'M22-matrix', 'M22-role-gaps', 'M22-needs'], reports: ['Skill-Gap Heatmap'], forms: ['Assessment', 'Training Need'] }],
    ['3', 'Certification Register', 12, { model: 'fix.certification', cols: ['employee_id', 'competency_id', 'repair_tier', 'expires_on', 'status'], screens: ['M22-register', 'M22-expiry', 'M22-eligibility', 'M22-waivers'], reports: ['Certification Coverage by Brand', 'Expiry Forecast', 'Dispatch Gate Readiness'], forms: ['Certification'] }],
    ['4', 'Training Delivery', 12, { model: 'fix.training.enrollment', cols: ['course_id', 'employee_id', 'completed_on', 'state'], screens: ['M22-needs', 'M22-plans', 'M22-catalogue', 'M22-paths', 'M22-sessions', 'M22-schedule', 'M22-feedback', 'M22-budget', 'M22-budget-exceptions'], reports: ['Training Effectiveness'], forms: ['Training Need', 'Training Plan', 'Course', 'Learning Path', 'Training Session', 'Training Feedback', 'Training Budget', 'Over-Budget Request'] }],
    ['5', 'OJT & Mentoring', 5, { model: 'fix.ojt.record', cols: ['name', 'employee_id', 'mentor_id', 'hours', 'outcome'], screens: ['M22-ojt', 'M22-mentoring', 'M22-mentoring-log'], reports: ['Training Effectiveness'], forms: ['Mentoring', 'Mentoring Interaction'] }],
    ['6', 'Evidence & Analytics', 5, { model: 'fix.audit.evidence', cols: ['name', 'evidence_type', 'standard_ref', 'valid_until', 'state'], screens: ['M22-iso', 'M22-effectiveness'], reports: ['Audit Evidence Pack', 'Training Effectiveness'], forms: ['Effectiveness Evaluation'] }]
  ] }
};

export const SCREENS = {
  'M22-framework': { kind: 'model_list', model: 'fix.competency',
    cols: ['code', 'name', 'brand_id', 'device_category_id', 'repair_tier', 'certification_class', 'required_for_dispatch'] },
  'M22-devices': { kind: 'model_list', model: 'fix.device.category',
    cols: ['code', 'name', 'name_bn', 'repair_tier_floor', 'active'] },
  'M22-matrix': { kind: 'table_report', module: 'M22', report: 'skill_gap_heatmap', title: 'Skill Matrix', period: true },
  'M22-assessments': { kind: 'model_list', model: 'fix.competency.assessment',
    cols: ['name', 'employee_id', 'competency_id', 'assessed_on', 'level', 'score', 'passed', 'attempt_escalated', 'retake_granted_by_id'],
    actions: [{ m: 'action_grant_retake', l: 'Grant Retake (Training Manager)', ask: 'Why a further attempt is allowed', kwarg: 'reason' }] },
  'M22-register': { kind: 'model_list', model: 'fix.certification', stateField: 'state',
    cols: ['employee_id', 'competency_id', 'brand_id', 'device_category_id', 'repair_tier', 'issued_on', 'expires_on', 'evidence_ref', 'approval_state', 'state', 'status'],
    actions: [{ m: 'action_grant', l: 'Request Grant (to Verifier)' }, { m: 'action_recall_approval', l: 'Recall Grant Request' },
              { m: 'action_renew', l: 'Renew' },
              { m: 'action_suspend', l: 'Suspend / Block Dispatch', ask: 'Reason for suspending the certification', kwarg: 'reason' },
              { m: 'action_reinstate', l: 'Reinstate (verifier)', ask: 'Reason for lifting the suspension', kwarg: 'reason' },
              { m: 'action_revoke', l: 'Revoke', ask: 'Reason for revoking the certification', kwarg: 'reason' },
              { m: 'action_mark_expired', l: 'Lapse Expired Now' }] },
  'M22-expiry': { kind: 'table_report', module: 'M22', report: 'expiry_forecast', title: 'Validity & Renewal', period: true },
  /* A09 M22-F3: a waiver is one technician on one job, raised from the work
   * or field order and decided in the approver's inbox, never here. */
  'M22-waivers': { kind: 'model_list', model: 'fix.certification.waiver', stateField: 'state', create: false,
    note: 'A waiver is requested from the job itself (Request Certification Waiver on the M02 field or work order) and decided in the Dispatch Override Approver\'s inbox; it is never raised or decided here.',
    cols: ['name', 'employee_id', 'res_model', 'res_id', 'reason', 'valid_until', 'requester_id', 'approved_by_id', 'approved_at', 'state'],
    actions: [{ m: 'action_cancel', l: 'Cancel' }] },
  'M22-eligibility': { kind: 'model_list', model: 'fix.certification', stateField: 'state',
    cols: ['employee_id', 'competency_id', 'brand_id', 'device_category_id', 'repair_tier', 'issued_on', 'expires_on', 'evidence_ref', 'state', 'status'],
    actions: [{ m: 'action_suspend', l: 'Hard Block Dispatch (M02)', ask: 'Reason for blocking dispatch', kwarg: 'reason' },
              { m: 'action_reinstate', l: 'Lift Block (verifier)', ask: 'Reason for lifting the block', kwarg: 'reason' }] },
  'M22-catalogue': { kind: 'model_list', model: 'fix.training.course',
    cols: ['code', 'name', 'competency_id', 'cost_per_seat', 'content_ref'],
    actions: [{ m: 'action_enroll', l: 'Enroll Techs', ask: 'Employee ids to enroll, comma-separated', kwarg: 'employees' }] },
  'M22-paths': { kind: 'model_list', model: 'fix.learning.path',
    cols: ['name', 'target_role', 'position_ids', 'requirement_count', 'min_level', 'active'],
    actions: [{ m: 'action_raise_gap_needs', l: 'Raise Training Needs from Gaps' }] },
  'M22-role-gaps': { kind: 'table_report', module: 'M22', report: 'role_gap_analysis', title: 'Role Gap Analysis', period: true },
  'M22-needs': { kind: 'model_list', model: 'fix.training.need', stateField: 'state',
    cols: ['name', 'employee_id', 'competency_id', 'course_id', 'source', 'priority', 'due_date', 'plan_id', 'enrollment_id', 'state'],
    actions: [{ m: 'action_enrol', l: 'Enrol (closes on a pass)' },
              { m: 'action_cancel', l: 'Cancel Need', ask: 'Why is the need cancelled?', kwarg: 'reason' }] },
  'M22-plans': { kind: 'model_list', model: 'fix.training.plan', stateField: 'state',
    cols: ['name', 'operating_unit_id', 'period', 'year', 'quarter', 'need_count', 'planned_cost', 'budget', 'approved_by_id', 'state'],
    actions: [{ m: 'action_submit', l: 'Submit for Approval' },
              { m: 'action_approve', l: 'Approve (Training Budget Approver)' },
              { m: 'action_return', l: 'Return to Draft', ask: 'Why is the plan returned?', kwarg: 'reason' },
              { m: 'action_cancel', l: 'Cancel Plan' }] },
  'M22-feedback': { kind: 'model_list', model: 'fix.training.feedback',
    cols: ['employee_id', 'course_id', 'session_id', 'trainer_id', 'rating_content', 'rating_trainer', 'rating_applicability', 'would_recommend', 'submitted_on'] },
  'M22-mentoring': { kind: 'model_list', model: 'fix.mentoring', stateField: 'state',
    cols: ['name', 'mentee_id', 'mentor_id', 'competency_id', 'date_start', 'date_end', 'interaction_count', 'last_interaction_on', 'outcome', 'state'],
    actions: [{ m: 'action_start', l: 'Start Mentoring' },
              { m: 'action_close', l: 'Close (mentor)', ask: 'Outcome: achieved, partly or not_achieved', kwarg: 'outcome' },
              { m: 'action_cancel', l: 'Cancel', ask: 'Why is the mentoring cancelled?', kwarg: 'reason' }] },
  'M22-mentoring-log': { kind: 'model_list', model: 'fix.mentoring.interaction',
    cols: ['mentoring_id', 'mentee_id', 'mentor_id', 'date', 'mode', 'duration_hours', 'topics', 'recorded_by_id'] },
  'M22-effectiveness': { kind: 'model_list', model: 'fix.training.effectiveness', stateField: 'state',
    cols: ['name', 'course_id', 'session_id', 'target_measure', 'baseline_value', 'after_value', 'change', 'result', 'evaluated_by_id', 'state'],
    actions: [{ m: 'action_evaluate', l: 'Record Evaluation' }] },
  'M22-sessions': { kind: 'model_list', model: 'fix.training.session', stateField: 'state',
    cols: ['name', 'course_id', 'delivery_mode', 'trainer_id', 'venue', 'date_start', 'date_end', 'capacity', 'seats_taken', 'attended_count', 'state'],
    actions: [{ m: 'action_schedule', l: 'Schedule (publish to the roster)' },
              { m: 'action_mark_held', l: 'Mark Held (attendance recorded)' },
              { m: 'action_cancel', l: 'Cancel Session' }] },
  'M22-schedule': { kind: 'model_list', model: 'fix.training.enrollment', stateField: 'state',
    cols: ['course_id', 'session_id', 'employee_id', 'attendance', 'cost', 'budget_year', 'budget_exception_id', 'completed_on', 'evidence_id', 'state'],
    actions: [{ m: 'action_mark_attended', l: 'Mark Attended' }, { m: 'action_mark_absent', l: 'Mark Absent' },
              { m: 'action_pass', l: 'Mark Passed (drafts the certificate)' }, { m: 'action_fail', l: 'Mark Failed' },
              { m: 'action_withdraw', l: 'Withdraw (frees the seat and its cost)', ask: 'Reason for the withdrawal', kwarg: 'reason' },
              { m: 'action_substitute', l: 'Substitute Trainee', ask: 'Substitute: employee id, name or badge', kwarg: 'employee' }] },
  'M22-budget': { kind: 'model_list', model: 'fix.training.budget',
    cols: ['name', 'year', 'company_id', 'amount', 'consumed', 'remaining'] },
  'M22-budget-exceptions': { kind: 'model_list', model: 'fix.training.budget.exception', stateField: 'state',
    cols: ['name', 'course_id', 'year', 'seats', 'amount', 'requested_by_id', 'approval_state', 'state'],
    actions: [{ m: 'action_request_approval', l: 'Request Approval (Training Budget Approver)' },
              { m: 'action_recall_approval', l: 'Recall Approval' },
              { m: 'action_cancel', l: 'Cancel' }] },
  'M22-ojt': { kind: 'model_list', model: 'fix.ojt.record',
    cols: ['name', 'employee_id', 'mentor_id', 'date_from', 'hours', 'outcome', 'signed_off_by_id'],
    actions: [{ m: 'action_sign_off', l: 'Mentor Sign-off', ask: 'Outcome: competent, extended or discontinued', kwarg: 'outcome' }] },
  'M22-iso': { kind: 'model_list', model: 'fix.audit.evidence', stateField: 'state',
    cols: ['name', 'evidence_type', 'standard_ref', 'collected_on', 'valid_until', 'state'],
    actions: [
      { m: 'action_submit', l: 'Submit' },
      { m: 'action_accept', l: 'Accept (verifier)' },
      { m: 'action_reject', l: 'Return (verifier)', ask: 'Why is the evidence returned?', kwarg: 'reason' },
      { m: 'action_compile_iso_dossier', l: 'Compile ISO 9001 Cl. 7.2 Dossier' }
    ] },

  /* Report chips -> their own computed pack */
  'M22-rpt-coverage': { kind: 'table_report', module: 'M22', report: 'certification_coverage', title: 'Certification Coverage by Brand', period: true },
  'M22-rpt-expiry': { kind: 'table_report', module: 'M22', report: 'expiry_forecast', title: 'Expiry Forecast', period: true },
  'M22-rpt-training': { kind: 'table_report', module: 'M22', report: 'training_effectiveness', title: 'Training Effectiveness', period: true },
  'M22-rpt-skillgap': { kind: 'table_report', module: 'M22', report: 'skill_gap_heatmap', title: 'Skill-Gap Heatmap', period: true },
  'M22-rpt-audit': { kind: 'table_report', module: 'M22', report: 'audit_evidence', title: 'Audit Evidence Pack', period: true },
  /* M22-F2: the dispatch gate's own readiness — ungated device types and
     tier-less gating competencies, next to the eligibility screen. */
  'M22-rpt-gatereadiness': { kind: 'table_report', module: 'M22', report: 'gate_readiness', title: 'Dispatch Gate Readiness', period: false },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M22-form-certification': {
    kind: 'model_form',
    model: 'fix.certification',
    title: 'Brand Certification',
    back: 'M22-register',
    status: { field: 'status', labels: {
      draft: 'Draft', valid: 'Valid', suspended: 'Suspended', lapsed: 'Lapsed', revoked: 'Revoked', superseded: 'Renewed' } },
    tabs: [
      { id: 'scope', label: 'Certificate Scope', bn: 'সনদের বিবরণ', icon: '📜', badge: '3' },
      { id: 'validity', label: 'Validity & Dispatch Gating', bn: 'মেয়াদ ও ডিসপ্যাচ শর্ত', icon: '🛡️', badge: '4' }
    ],
    sections: [
      {
        tab: 'scope',
        title: 'Brand / OEM Certification Record',
        note: 'Authorised technician brand accreditation (Apple, Samsung, Dell, HP, Daikin, Gree, etc.).',
        fields: [
          { name: 'employee_id', required: true, label: 'Technician' },
          { name: 'competency_id', required: true, label: 'Certified Competency' },
          { name: 'brand_id', label: 'OEM Brand Partner' },
          { name: 'device_category_id', label: 'Device Category' },
          { name: 'repair_tier', label: 'Certified Repair Tier (L1-L4)' },
          { name: 'brand_critical', label: 'Brand-Critical (OEM audit; expiry alerts holder AND manager)' },
          { name: 'operating_unit_id', label: 'Operating Unit' }
        ]
      },
      {
        tab: 'validity',
        title: 'Validity Timeline & ISO Audit Reference',
        note: 'A certificate counts for dispatch only once a verifier grants it (passed assessment, expiry and evidence required). A granted certificate is renewed, never re-dated; an expired one lapses automatically.',
        fields: [
          { name: 'issued_on', required: true, label: 'Certificate Issue Date' },
          { name: 'expires_on', required: true, label: 'Expiry Date' },
          { name: 'evidence_ref', label: 'Audit Evidence / Certificate No' },
          { name: 'certificate_file', label: 'Certificate Scan' },
          { name: 'assessment_id', required: true, label: 'Qualifying Assessment' },
          { name: 'status', readonly: true, label: 'Validity (today)' },
          { name: 'state', readonly: true, label: 'Certification State' },
          { name: 'approval_state', readonly: true, label: 'Grant Approval' },
          { name: 'verified_by_id', readonly: true, label: 'Granted By' },
          { name: 'suspension_reason', readonly: true, label: 'Suspension / Revocation Reason' }
        ]
      }
    ]
  },

  'M22-form-course': {
    kind: 'model_form',
    model: 'fix.training.course',
    title: 'Course Catalogue',
    back: 'M22-catalogue',
    tabs: [
      { id: 'curriculum', label: 'Curriculum & Content', bn: 'পাঠ্যক্রম ও বিবরণ', icon: '📚', badge: '4' },
      { id: 'accreditation', label: 'Competency Mapping', bn: 'দক্ষতা ম্যাপিং', icon: '🎖️', badge: '2' }
    ],
    sections: [
      {
        tab: 'curriculum',
        title: 'Course Syllabus Specification',
        note: 'Formal technical training module aligned with OEM technical documentation.',
        fields: [
          { name: 'code', required: true, label: 'Course Code' },
          { name: 'name', required: true, label: 'Course Title (English)' },
          { name: 'name_bn', label: 'Course Title (Bengali)' },
          { name: 'content_ref', label: 'LMS / Syllabus Link' }
        ]
      },
      {
        tab: 'accreditation',
        title: 'Competency & Operating Unit Alignment',
        note: 'Successful course completion earns this core skill on technician matrix.',
        fields: [
          { name: 'competency_id', label: 'Certifies Towards Competency' },
          { name: 'cost_per_seat', label: 'Cost per Seat (BDT, against the training budget)' },
          { name: 'operating_unit_id', label: 'Operating Unit' }
        ]
      }
    ]
  },

  'M22-form-path': {
    kind: 'model_form',
    model: 'fix.learning.path',
    title: 'Learning Path',
    back: 'M22-paths',
    tabs: [
      { id: 'path', label: 'Role, Competencies & Courses', bn: 'ভূমিকা, দক্ষতা ও কোর্স', icon: '🗺️', badge: '5' },
      { id: 'grid', label: 'Competency Requirements', bn: 'দক্ষতার প্রয়োজনীয়তা', icon: '📋', badge: 'FR-002' },
      { id: 'requirements', label: 'Level & Status', bn: 'স্তর ও অবস্থা', icon: '🎖️', badge: '3' }
    ],
    grids: [
      {
        field: 'requirement_ids', tab: 'grid', title: 'Required Competencies and Minimum Levels (FR-LMS-002)',
        addLabel: '+ Add requirement',
        empty: 'No requirement yet. One line per competency the role needs, with its minimum level.',
        note: 'Each line is one competency the role requires, its minimum level, whether it is mandatory and from when it applies. The Role Gap Analysis measures every employee in the positions above against these lines.',
        fields: [
          { name: 'competency_id', label: 'Competency' },
          { name: 'min_level', label: 'Minimum Level' },
          { name: 'mandatory', label: 'Mandatory' },
          { name: 'effective_from', label: 'Effective From' }
        ]
      }
    ],
    sections: [
      {
        tab: 'path',
        title: 'Technician Development Pathway',
        note: 'Progressive learning milestones from Trainee Technician to Master Specialist.',
        fields: [
          { name: 'name', required: true, label: 'Path Title' },
          { name: 'target_role', label: 'Target Role (the role this path qualifies for)' },
          { name: 'position_ids', label: 'Applies to Positions (measured by the Role Gap Analysis)' },
          { name: 'competency_ids', label: 'Target Competencies' },
          { name: 'course_ids', label: 'Courses in the Path (FR-LMS-018)' }
        ]
      },
      {
        tab: 'requirements',
        title: 'Proficiency Level & Activation',
        note: 'Minimum required proficiency level (1–5) and path activation flag.',
        fields: [
          { name: 'min_level', required: true, label: 'Default Minimum Level (L1-L4)' },
          { name: 'company_id', label: 'Company' },
          { name: 'active', label: 'Active Status' }
        ]
      }
    ]
  },

  'M22-form-competency': {
    kind: 'model_form',
    model: 'fix.competency',
    title: 'Technical Competency Definition',
    back: 'M22-framework',
    tabs: [
      { id: 'definition', label: 'Competency Identity', bn: 'দক্ষতা পরিচিতি', icon: '🔧', badge: '4' },
      { id: 'taxonomy', label: 'Brand, Device & Tier Gate', bn: 'ব্র্যান্ড, ডিভাইস ও ডিসপ্যাচ গেট', icon: '🛡️', badge: '5' }
    ],
    sections: [
      {
        tab: 'definition',
        title: 'Core Competency Code & Bilingual Titles',
        note: 'Technical competency identifier in the 1000 FiX skill matrix.',
        fields: [
          { name: 'code', required: true, label: 'Competency Code' },
          { name: 'name', required: true, label: 'Competency Name (English)' },
          { name: 'name_bn', label: 'Competency Name (Bengali)' },
          { name: 'operating_unit_id', label: 'Operating Unit' }
        ]
      },
      {
        tab: 'taxonomy',
        title: 'OEM Brand, Device Category & Repair Tier Gating',
        note: 'Drives M02 fail-closed dispatch eligibility across brand, device type, and L1–L4 repair tier.',
        fields: [
          { name: 'brand_id', label: 'Authorized OEM Brand Partner' },
          { name: 'device_category_id', label: 'Device Category' },
          { name: 'device_type', required: true, label: 'Device Family' },
          { name: 'repair_tier', required: true, label: 'Required Repair Tier (L1-L4)' },
          { name: 'required_for_dispatch', label: 'Mandatory for M02 Work Order Dispatch' },
          { name: 'certification_class', label: 'Certification Class (Statutory / Safety escalates to M59 on lapse)' },
          { name: 'pass_mark', label: 'Assessment Pass Mark (%)' },
          { name: 'attempt_limit', label: 'Assessment Attempt Limit (0 = none)' },
          { name: 'validity_months', label: 'Certificate Validity (months)' }
        ]
      }
    ]
  },

  'M22-form-device': {
    kind: 'model_form',
    model: 'fix.device.category',
    title: 'Device Category & Repair Tier',
    back: 'M22-devices',
    tabs: [
      { id: 'category', label: 'Category Identity', bn: 'ক্যাটাগরি পরিচিতি', icon: '📱', badge: '4' },
      { id: 'tier', label: 'Default Tier & Status', bn: 'ডিফল্ট স্তর ও অবস্থা', icon: '⚙️', badge: '3' }
    ],
    sections: [
      {
        tab: 'category',
        title: 'After-Sales Device Category',
        note: 'Taxonomy category (Inverter AC, Logic Board, Smartphone OLED, Enterprise UPS).',
        fields: [
          { name: 'code', required: true, label: 'Category Code' },
          { name: 'name', required: true, label: 'Category Name (English)' },
          { name: 'name_bn', label: 'Category Name (Bengali)' },
          { name: 'parent_id', label: 'Parent Category' }
        ]
      },
      {
        tab: 'tier',
        title: 'Default Repair Tier & Governance',
        note: 'Default technician repair tier required for this category.',
        fields: [
          { name: 'repair_tier_floor', required: true, label: 'Default Required Repair Tier (L1-L4)' },
          { name: 'company_id', label: 'Company' },
          { name: 'active', label: 'Active' }
        ]
      }
    ]
  },

  'M22-form-assessment': {
    kind: 'model_form',
    model: 'fix.competency.assessment',
    title: 'Technician Competency Assessment',
    back: 'M22-assessments',
    tabs: [
      { id: 'candidate', label: 'Technician & Skill', bn: 'টেকনিশিয়ান ও দক্ষতা', icon: '👤', badge: '4' },
      { id: 'evaluation', label: 'Proficiency & Score', bn: 'দক্ষতা স্তর ও স্কোর', icon: '📊', badge: '4' }
    ],
    sections: [
      {
        tab: 'candidate',
        title: 'Assessment Subject & Competency',
        note: 'Practical bench or field technical assessment record.',
        fields: [
          { name: 'name', label: 'Assessment Reference' },
          { name: 'employee_id', required: true, label: 'Technician / Employee' },
          { name: 'competency_id', required: true, label: 'Evaluated Competency' },
          { name: 'assessor_id', required: true, label: 'Technical Assessor (not the technician)' }
        ]
      },
      {
        tab: 'evaluation',
        title: 'Assessed Level (L1–L4) & Outcome',
        note: 'Feeds the M22 Skill-Gap Heatmap and certification eligibility.',
        fields: [
          { name: 'assessed_on', required: true, label: 'Assessment Date' },
          { name: 'level', required: true, label: 'Assessed Repair Level (L1-L4)' },
          { name: 'score', label: 'Practical Score (0-100)' },
          { name: 'notes', label: 'Method & Evidence (test, practical, supervisor verification)' },
          { name: 'passed', readonly: true, label: 'Assessment Passed (score vs pass mark)' },
          { name: 'attempt_escalated', readonly: true, label: 'Attempt Limit Reached (escalated)' },
          { name: 'retake_granted_by_id', readonly: true, label: 'Retake Granted By' },
          { name: 'retake_reason', readonly: true, label: 'Retake Reason' }
        ]
      }
    ]
  },

  'M22-form-enrollment': {
    kind: 'model_form',
    model: 'fix.training.enrollment',
    title: 'Training Schedule & Enrollment',
    back: 'M22-schedule',
    status: { field: 'state', labels: {
      enrolled: 'Enrolled', passed: 'Passed', failed: 'Failed', withdrawn: 'Withdrawn' } },
    tabs: [
      { id: 'enrollment', label: 'Course, Session & Trainee', bn: 'কোর্স, সেশন ও প্রশিক্ষণার্থী', icon: '📚', badge: '4' },
      { id: 'completion', label: 'Completion & Certification', bn: 'সমাপ্তি ও সনদ', icon: '🎓', badge: '2' }
    ],
    sections: [
      {
        tab: 'enrollment',
        title: 'Technician Course Enrollment',
        note: 'Assigns a technician to a structured technical training course.',
        fields: [
          { name: 'course_id', required: true, label: 'Training Course' },
          { name: 'session_id', label: 'Session (date, trainer, venue)' },
          { name: 'employee_id', required: true, label: 'Enrolled Technician' },
          { name: 'company_id', label: 'Company' }
        ]
      },
      {
        tab: 'completion',
        title: 'Completion Date & Automatic Certification',
        note: 'A pass needs a passed assessment by an independent assessor; it drafts the certificate, which a verifier then grants.',
        fields: [
          { name: 'attendance', readonly: true, label: 'Attendance (recorded by the trainer)' },
          { name: 'completed_on', readonly: true, label: 'Completion Date' },
          { name: 'state', readonly: true, label: 'Enrollment State' },
          { name: 'assessment_id', readonly: true, label: 'Qualifying Assessment' },
          { name: 'certification_id', readonly: true, label: 'Draft Certification' },
          { name: 'cost', readonly: true, label: 'Seat Cost (BDT)' },
          { name: 'budget_year', readonly: true, label: 'Budget Year' },
          { name: 'budget_exception_id', readonly: true, label: 'Over-Budget Approval' },
          { name: 'evidence_id', readonly: true, label: 'Competence Evidence (ISO 9001 cl. 7.2)' },
          { name: 'withdraw_reason', readonly: true, label: 'Withdrawal Reason' },
          { name: 'substitute_of_id', readonly: true, label: 'Substitute For' }
        ]
      }
    ]
  },

  'M22-form-session': {
    kind: 'model_form',
    model: 'fix.training.session',
    title: 'Training Session',
    back: 'M22-sessions',
    status: { field: 'state', labels: {
      planned: 'Planned', scheduled: 'Scheduled', done: 'Held', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'session', label: 'Course, Trainer & Venue', bn: 'কোর্স, প্রশিক্ষক ও স্থান', icon: '🧑‍🏫', badge: '8' },
      { id: 'window', label: 'Dates & Seats', bn: 'তারিখ ও আসন', icon: '📅', badge: '7' }
    ],
    sections: [
      {
        tab: 'session',
        title: 'Scheduled Delivery (FR-LMS-020)',
        note: 'A classroom or practical session names its trainer and venue before it is scheduled; an external one names its provider (FR-LMS-029). Scheduling publishes the window so the trainees\' availability can be taken out of the roster (BRU-LMS-08).',
        fields: [
          { name: 'name', readonly: true, label: 'Session Reference' },
          { name: 'course_id', required: true, label: 'Course' },
          { name: 'delivery_mode', required: true, label: 'Delivery Mode' },
          { name: 'trainer_id', label: 'Trainer (employee)' },
          { name: 'vendor_id', label: 'External Provider' },
          { name: 'external_trainer', label: 'External Trainer' },
          { name: 'venue', label: 'Venue' },
          { name: 'operating_unit_id', label: 'Operating Unit' }
        ]
      },
      {
        tab: 'window',
        title: 'Window, Capacity & Attendance (FR-LMS-021/023)',
        note: 'Enrolments name this session on the Schedule & Attendance list; the trainer records each attendance there. A session is marked held only when every attendance is recorded.',
        fields: [
          { name: 'date_start', required: true, label: 'Starts' },
          { name: 'date_end', required: true, label: 'Ends' },
          { name: 'capacity', label: 'Capacity (0 = no limit)' },
          { name: 'seats_taken', readonly: true, label: 'Seats Taken' },
          { name: 'attended_count', readonly: true, label: 'Attended' },
          { name: 'state', readonly: true, label: 'State' },
          { name: 'notes', type: 'text', label: 'Session Notes' }
        ]
      }
    ]
  },

  'M22-form-budget': {
    kind: 'model_form',
    model: 'fix.training.budget',
    title: 'Training Budget',
    back: 'M22-budget',
    tabs: [
      { id: 'budget', label: 'Year & Amount', bn: 'বছর ও পরিমাণ', icon: '💰', badge: '6' }
    ],
    sections: [
      {
        tab: 'budget',
        title: 'Yearly Training Budget (BRU-LMS-10)',
        note: 'Set by the Training Budget Approver. Every enrolment commits its course seat cost; past the budget an enrolment needs an approved over-budget request. No budget for a year means none is ruled.',
        fields: [
          { name: 'company_id', required: true, label: 'Company' },
          { name: 'year', required: true, label: 'Year' },
          { name: 'amount', required: true, label: 'Budget (BDT)' },
          { name: 'consumed', readonly: true, label: 'Committed (BDT)' },
          { name: 'remaining', readonly: true, label: 'Remaining (BDT)' },
          { name: 'operating_unit_id', label: 'Operating Unit' }
        ]
      }
    ]
  },

  'M22-form-budget-exception': {
    kind: 'model_form',
    model: 'fix.training.budget.exception',
    title: 'Over-Budget Training Request',
    back: 'M22-budget-exceptions',
    status: { field: 'state', labels: {
      draft: 'Draft', pending: 'Awaiting Approval', approved: 'Approved',
      rejected: 'Rejected', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'request', label: 'Request', bn: 'অনুরোধ', icon: '📝', badge: '5' },
      { id: 'decision', label: 'Decision', bn: 'সিদ্ধান্ত', icon: '🖋️', badge: '4' }
    ],
    sections: [
      {
        tab: 'request',
        title: 'Seats Past the Budget',
        note: 'Raised by a Training Manager; decided from the approval inbox by the Training Budget Approver, never by the requester or a technician it names.',
        fields: [
          { name: 'course_id', required: true, label: 'Course' },
          { name: 'year', required: true, label: 'Budget Year' },
          { name: 'seats', required: true, label: 'Seats' },
          { name: 'amount', readonly: true, label: 'Over-Budget Amount (BDT)' },
          { name: 'reason', required: true, type: 'text', label: 'Justification' },
          { name: 'company_id', label: 'Company' }
        ]
      },
      {
        tab: 'decision',
        title: 'Routed Approval',
        note: 'An approved request lets the named technicians (or any, when none is named) take up to its seats.',
        fields: [
          { name: 'state', readonly: true, label: 'State' },
          { name: 'approval_state', readonly: true, label: 'Approval' },
          { name: 'requested_by_id', readonly: true, label: 'Requested By' },
          { name: 'approved_by_id', readonly: true, label: 'Approved By' }
        ]
      }
    ]
  },

  'M22-form-ojt': {
    kind: 'model_form',
    model: 'fix.ojt.record',
    title: 'On-the-Job Training (OJT) & Mentoring',
    back: 'M22-ojt',
    tabs: [
      { id: 'mentoring', label: 'Trainee & Mentor', bn: 'প্রশিক্ষণার্থী ও মেন্টর', icon: '🤝', badge: '4' },
      { id: 'outcome', label: 'Logged Hours & Outcome', bn: 'প্রশিক্ষণ ঘণ্টা ও ফলাফল', icon: '⏱️', badge: '6' }
    ],
    sections: [
      {
        tab: 'mentoring',
        title: 'Workshop / Field OJT Pairing',
        note: 'Supervised practical repair mentoring under a senior L3/L4 specialist.',
        fields: [
          { name: 'name', label: 'OJT Log Reference' },
          { name: 'employee_id', required: true, label: 'Trainee Technician' },
          { name: 'mentor_id', required: true, label: 'Senior Mentor' },
          { name: 'competency_id', label: 'Target Competency' }
        ]
      },
      {
        tab: 'outcome',
        title: 'Supervised Hours & Practical Signoff',
        note: 'Logged OJT hours feed the M22 Training Hours per Technician KPI.',
        fields: [
          { name: 'date_from', required: true, label: 'From' },
          { name: 'date_to', label: 'To' },
          { name: 'hours', required: true, label: 'Supervised Hours' },
          { name: 'notes', label: 'Tasks Observed & Observations (FR-LMS-027)' },
          { name: 'outcome', readonly: true, label: 'Mentor Assessment Outcome' },
          { name: 'signed_off_by_id', readonly: true, label: 'Signed Off By' },
          { name: 'signed_off_at', readonly: true, label: 'Signed Off At' }
        ]
      }
    ]
  },

  'M22-form-need': {
    kind: 'model_form',
    model: 'fix.training.need',
    title: 'Training Need',
    back: 'M22-needs',
    status: { field: 'state', labels: {
      identified: 'Identified', planned: 'Planned', enrolled: 'Enrolled', closed: 'Closed (trained)', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'need', label: 'Employee & Need', bn: 'কর্মী ও প্রয়োজন', icon: '🎯', badge: '6' },
      { id: 'source', label: 'Source & Plan', bn: 'উৎস ও পরিকল্পনা', icon: '🧭', badge: '6' }
    ],
    sections: [
      {
        tab: 'need',
        title: 'Identified Need (FR-LMS-031, lifecycle 8.2)',
        note: 'One employee, the competency they lack or the course that closes it, and why. A need is closed by a passed enrolment; a failed or withdrawn one sends it back to be planned.',
        fields: [
          { name: 'name', readonly: true, label: 'Need Reference' },
          { name: 'employee_id', required: true, label: 'Employee' },
          { name: 'competency_id', label: 'Competency Lacking' },
          { name: 'course_id', label: 'Course to Close It' },
          { name: 'description', required: true, type: 'text', label: 'Need Statement' },
          { name: 'priority', required: true, label: 'Priority (a safety need is always Mandatory)' },
          { name: 'due_date', label: 'Needed By' }
        ]
      },
      {
        tab: 'source',
        title: 'Where the Need Came From',
        note: 'The trigger: a role gap, an M57 performance gap, an M23 non-conformance, an M59 incident, a new product line or brand (BRU-LMS-13), a role change, or a manager request.',
        fields: [
          { name: 'source', required: true, label: 'Source' },
          { name: 'source_ref', label: 'Source Reference (NC / incident / review no.)' },
          { name: 'raised_on', required: true, label: 'Raised On' },
          { name: 'plan_id', label: 'Training Plan (draft plans only)' },
          { name: 'company_id', label: 'Company' },
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'enrollment_id', readonly: true, label: 'Enrolment' },
          { name: 'raised_by_id', readonly: true, label: 'Raised By' },
          { name: 'closed_on', readonly: true, label: 'Closed On' },
          { name: 'cancel_reason', readonly: true, label: 'Cancellation Reason' }
        ]
      }
    ]
  },

  'M22-form-plan': {
    kind: 'model_form',
    model: 'fix.training.plan',
    title: 'Training Plan',
    back: 'M22-plans',
    status: { field: 'state', labels: {
      draft: 'Draft', submitted: 'Submitted', approved: 'Approved', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'period', label: 'Period, Branch & Budget', bn: 'সময়কাল, শাখা ও বাজেট', icon: '📆', badge: '7' },
      { id: 'decision', label: 'Needs & Decision', bn: 'প্রয়োজন ও সিদ্ধান্ত', icon: '🖋️', badge: '6' }
    ],
    sections: [
      {
        tab: 'period',
        title: 'Annual / Quarterly Training Plan (FR-LMS-032)',
        note: 'A plan consolidates training needs for a branch and period. Needs join it from the Training Needs list while it is a draft. It is submitted with every need costed, inside its budget, and approved by a Training Budget Approver other than the submitter; a planned need is enrolled only once its plan is approved.',
        fields: [
          { name: 'name', required: true, label: 'Plan Name' },
          { name: 'period', required: true, label: 'Period' },
          { name: 'year', required: true, label: 'Year' },
          { name: 'quarter', label: 'Quarter (quarterly plans)' },
          { name: 'operating_unit_id', label: 'Branch / Operating Unit' },
          { name: 'target_role', label: 'Role / Population' },
          { name: 'budget', label: 'Plan Budget (BDT)' },
          { name: 'company_id', label: 'Company' }
        ]
      },
      {
        tab: 'decision',
        title: 'Consolidated Needs & Approval',
        note: 'Planned cost = the seat cost of each need\'s course.',
        fields: [
          { name: 'need_count', readonly: true, label: 'Needs in Plan' },
          { name: 'planned_cost', readonly: true, label: 'Planned Cost (BDT)' },
          { name: 'notes', type: 'text', label: 'Notes' },
          { name: 'state', readonly: true, label: 'State' },
          { name: 'submitted_by_id', readonly: true, label: 'Submitted By' },
          { name: 'approved_by_id', readonly: true, label: 'Approved By' },
          { name: 'approved_at', readonly: true, label: 'Approved At' },
          { name: 'return_reason', readonly: true, label: 'Returned Because' }
        ]
      }
    ]
  },

  'M22-form-feedback': {
    kind: 'model_form',
    model: 'fix.training.feedback',
    title: 'Participant Feedback',
    back: 'M22-feedback',
    tabs: [
      { id: 'rating', label: 'Ratings', bn: 'মূল্যায়ন', icon: '⭐', badge: '5' },
      { id: 'about', label: 'Training', bn: 'প্রশিক্ষণ', icon: '📚', badge: '6' }
    ],
    sections: [
      {
        tab: 'rating',
        title: 'Your Feedback (FR-LMS-036)',
        note: 'Given by the trainee after attending (a Training Manager records it for a trainee with no account). One per enrolment; it is not changed once submitted.',
        fields: [
          { name: 'enrollment_id', required: true, label: 'Enrolment (course and trainee)' },
          { name: 'rating_content', required: true, label: 'Content' },
          { name: 'rating_trainer', required: true, label: 'Trainer' },
          { name: 'rating_applicability', required: true, label: 'Applicability to My Work' },
          { name: 'would_recommend', label: 'Would Recommend' },
          { name: 'comments', type: 'text', label: 'Comments' }
        ]
      },
      {
        tab: 'about',
        title: 'The Training Rated',
        note: 'Filled from the enrolment.',
        fields: [
          { name: 'employee_id', readonly: true, label: 'Trainee' },
          { name: 'course_id', readonly: true, label: 'Course' },
          { name: 'session_id', readonly: true, label: 'Session' },
          { name: 'trainer_id', readonly: true, label: 'Trainer' },
          { name: 'submitted_on', readonly: true, label: 'Submitted On' },
          { name: 'recorded_by_id', readonly: true, label: 'Recorded By' }
        ]
      }
    ]
  },

  'M22-form-mentoring': {
    kind: 'model_form',
    model: 'fix.mentoring',
    title: 'Mentoring Assignment',
    back: 'M22-mentoring',
    status: { field: 'state', labels: {
      draft: 'Draft', active: 'Active', closed: 'Closed', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'pair', label: 'Mentee, Mentor & Objectives', bn: 'মেন্টি, মেন্টর ও লক্ষ্য', icon: '🤝', badge: '6' },
      { id: 'progress', label: 'Interactions & Outcome', bn: 'সাক্ষাৎ ও ফলাফল', icon: '📈', badge: '7' }
    ],
    sections: [
      {
        tab: 'pair',
        title: 'Mentor Assignment (FR-LMS-028)',
        note: 'A Training Manager pairs a new technician with a mentor and states what the mentoring should achieve. The pair is fixed once it starts.',
        fields: [
          { name: 'name', readonly: true, label: 'Mentoring Reference' },
          { name: 'mentee_id', required: true, label: 'Mentee' },
          { name: 'mentor_id', required: true, label: 'Mentor' },
          { name: 'competency_id', label: 'Focus Competency' },
          { name: 'objectives', required: true, type: 'text', label: 'Objectives' },
          { name: 'date_start', required: true, label: 'Starts' },
          { name: 'date_end', label: 'Planned End' },
          { name: 'operating_unit_id', label: 'Operating Unit' }
        ]
      },
      {
        tab: 'progress',
        title: 'Recorded Interactions & Closing Outcome',
        note: 'The mentor records each interaction on the Mentoring Interactions list; the mentor or a Training Manager closes the mentoring on that record, never the mentee.',
        fields: [
          { name: 'interaction_count', readonly: true, label: 'Interactions' },
          { name: 'hours_logged', readonly: true, label: 'Hours Logged' },
          { name: 'last_interaction_on', readonly: true, label: 'Last Interaction' },
          { name: 'state', readonly: true, label: 'State' },
          { name: 'outcome', readonly: true, label: 'Outcome' },
          { name: 'closed_by_id', readonly: true, label: 'Closed By' },
          { name: 'closing_note', readonly: true, label: 'Cancellation Note' }
        ]
      }
    ]
  },

  'M22-form-mentoring-log': {
    kind: 'model_form',
    model: 'fix.mentoring.interaction',
    title: 'Mentoring Interaction',
    back: 'M22-mentoring-log',
    tabs: [
      { id: 'meeting', label: 'Interaction', bn: 'সাক্ষাৎ', icon: '🗣️', badge: '6' },
      { id: 'who', label: 'Pair', bn: 'জুটি', icon: '👥', badge: '3' }
    ],
    sections: [
      {
        tab: 'meeting',
        title: 'What Was Covered (FR-LMS-028)',
        note: 'Recorded by the mentor (or a Training Manager) on an active mentoring, after it happens; never by the mentee.',
        fields: [
          { name: 'mentoring_id', required: true, label: 'Mentoring (active)' },
          { name: 'date', required: true, label: 'Date' },
          { name: 'mode', required: true, label: 'Mode' },
          { name: 'duration_hours', label: 'Duration (hours)' },
          { name: 'topics', required: true, type: 'text', label: 'Topics Covered' },
          { name: 'actions_agreed', type: 'text', label: 'Actions Agreed' }
        ]
      },
      {
        tab: 'who',
        title: 'Mentee & Mentor',
        note: 'Follows the mentoring.',
        fields: [
          { name: 'mentee_id', readonly: true, label: 'Mentee' },
          { name: 'mentor_id', readonly: true, label: 'Mentor' },
          { name: 'recorded_by_id', readonly: true, label: 'Recorded By' }
        ]
      }
    ]
  },

  'M22-form-effectiveness': {
    kind: 'model_form',
    model: 'fix.training.effectiveness',
    title: 'Training Effectiveness Evaluation',
    back: 'M22-effectiveness',
    status: { field: 'state', labels: { draft: 'Draft', evaluated: 'Evaluated' } },
    tabs: [
      { id: 'target', label: 'Training & Measure', bn: 'প্রশিক্ষণ ও পরিমাপ', icon: '🎯', badge: '6' },
      { id: 'result', label: 'Before / After & Conclusion', bn: 'আগে / পরে ও সিদ্ধান্ত', icon: '📊', badge: '9' }
    ],
    sections: [
      {
        tab: 'target',
        title: 'What the Training Targeted (FR-LMS-035, BRU-LMS-15)',
        note: 'Name the operational measure the training was meant to move (first-time-fix rate, repeat visits, non-conformances) and its value before. The session must have been held (AUT-LMS-12 evaluates 90 days after).',
        fields: [
          { name: 'name', readonly: true, label: 'Evaluation Reference' },
          { name: 'course_id', required: true, label: 'Course' },
          { name: 'session_id', label: 'Session Evaluated (held)' },
          { name: 'target_measure', required: true, label: 'Operational Measure Targeted' },
          { name: 'measure_unit', label: 'Unit' },
          { name: 'better_when', required: true, label: 'Direction' },
          { name: 'company_id', label: 'Company' }
        ]
      },
      {
        tab: 'result',
        title: 'Before vs After',
        note: 'Record the after-value and its period, then the conclusion; Record Evaluation fixes it. The session\'s trainer does not evaluate their own session.',
        fields: [
          { name: 'baseline_value', required: true, label: 'Before' },
          { name: 'baseline_period', required: true, label: 'Before - Period' },
          { name: 'after_value', label: 'After' },
          { name: 'after_period', label: 'After - Period' },
          { name: 'conclusion', type: 'text', label: 'Conclusion' },
          { name: 'change', readonly: true, label: 'Change' },
          { name: 'result', readonly: true, label: 'Result' },
          { name: 'state', readonly: true, label: 'State' },
          { name: 'evaluated_by_id', readonly: true, label: 'Evaluated By' },
          { name: 'evaluated_on', readonly: true, label: 'Evaluated On' }
        ]
      }
    ]
  },

  'M22-form-evidence': {
    kind: 'model_form',
    model: 'fix.audit.evidence',
    title: 'ISO 9001:2015 Clause 7.2 & Brand Audit Evidence',
    back: 'M22-iso',
    status: { field: 'state', labels: {
      draft: 'Draft', submitted: 'Submitted', accepted: 'Accepted' } },
    tabs: [
      { id: 'evidence', label: 'Clause & Evidence Type', bn: 'মানদণ্ড ও প্রমাণের ধরন', icon: '📑', badge: '6' },
      { id: 'audit', label: 'Validity & Dossier Summary', bn: 'মেয়াদ ও ডসিয়ার সারসংক্ষেপ', icon: '✅', badge: '4' }
    ],
    sections: [
      {
        tab: 'evidence',
        title: 'ISO 9001:2015 Clause 7.2 / OEM Brand Audit Artifact',
        note: 'Competence, training, and certification audit evidence for ISO and OEM auditors.',
        fields: [
          { name: 'name', required: true, label: 'Evidence Title / Reference' },
          { name: 'evidence_type', required: true, label: 'Evidence Classification' },
          { name: 'standard_ref', label: 'Standard Clause (e.g. ISO 9001:2015 Cl. 7.2)' },
          { name: 'employee_id', label: 'Audited Technician / Staff' },
          { name: 'brand_id', label: 'Audited OEM Brand' },
          { name: 'company_id', label: 'Company' }
        ]
      },
      {
        tab: 'audit',
        title: 'Collection Timeline & Compiled Dossier',
        note: 'Validity horizon and compiled technician competence dossier.',
        fields: [
          { name: 'collected_on', required: true, label: 'Collected Date' },
          { name: 'valid_until', label: 'Valid Until Date' },
          { name: 'notes', type: 'text', label: 'Compiled Dossier / Auditor Notes' },
          { name: 'evidence_file', label: 'Audit Evidence Scan (required to submit)' },
          { name: 'reference', label: 'Evidence Reference' },
          { name: 'attachment_note', label: 'Original Held At (location)' },
          { name: 'state', readonly: true, label: 'Verification State' },
          { name: 'submitted_by_id', readonly: true, label: 'Submitted By' },
          { name: 'accepted_by_id', readonly: true, label: 'Accepted By' }
        ]
      }
    ]
  }
};

export const REPORT_ROUTES = {
  'M22:Certification Coverage by Brand': 'M22-rpt-coverage',
  'M22:Expiry Forecast': 'M22-rpt-expiry',
  'M22:Training Effectiveness': 'M22-rpt-training',
  'M22:Skill-Gap Heatmap': 'M22-rpt-skillgap',
  'M22:Audit Evidence Pack': 'M22-rpt-audit',
  'M22:Dispatch Gate Readiness': 'M22-rpt-gatereadiness'
};

export const FORM_MODELS = {
  'M22:Certification': 'fix.certification',
  'M22:Course': 'fix.training.course',
  'M22:Learning Path': 'fix.learning.path',
  'M22:Assessment': 'fix.competency.assessment',
  'M22:Device Category': 'fix.device.category',
  'M22:Training Session': 'fix.training.session',
  'M22:Training Budget': 'fix.training.budget',
  'M22:Over-Budget Request': 'fix.training.budget.exception',
  'M22:Training Need': 'fix.training.need',
  'M22:Training Plan': 'fix.training.plan',
  'M22:Training Feedback': 'fix.training.feedback',
  'M22:Mentoring': 'fix.mentoring',
  'M22:Mentoring Interaction': 'fix.mentoring.interaction',
  'M22:Effectiveness Evaluation': 'fix.training.effectiveness'
};

export const FORM_CHIPS = {
  'M22:Certification': 'M22-form-certification',
  'M22:Course': 'M22-form-course',
  'M22:Learning Path': 'M22-form-path',
  'M22:Assessment': 'M22-form-assessment',
  'M22:Device Category': 'M22-form-device',
  'M22:Training Session': 'M22-form-session',
  'M22:Training Budget': 'M22-form-budget',
  'M22:Over-Budget Request': 'M22-form-budget-exception',
  'M22:Training Need': 'M22-form-need',
  'M22:Training Plan': 'M22-form-plan',
  'M22:Training Feedback': 'M22-form-feedback',
  'M22:Mentoring': 'M22-form-mentoring',
  'M22:Mentoring Interaction': 'M22-form-mentoring-log',
  'M22:Effectiveness Evaluation': 'M22-form-effectiveness',
  'M22:__by_model__': {
    'fix.competency': 'M22-form-competency',
    'fix.device.category': 'M22-form-device',
    'fix.certification': 'M22-form-certification',
    'fix.training.course': 'M22-form-course',
    'fix.learning.path': 'M22-form-path',
    'fix.competency.assessment': 'M22-form-assessment',
    'fix.training.enrollment': 'M22-form-enrollment',
    'fix.training.session': 'M22-form-session',
    'fix.ojt.record': 'M22-form-ojt',
    'fix.audit.evidence': 'M22-form-evidence',
    'fix.training.budget': 'M22-form-budget',
    'fix.training.budget.exception': 'M22-form-budget-exception',
    'fix.training.need': 'M22-form-need',
    'fix.training.plan': 'M22-form-plan',
    'fix.training.feedback': 'M22-form-feedback',
    'fix.mentoring': 'M22-form-mentoring',
    'fix.mentoring.interaction': 'M22-form-mentoring-log',
    'fix.training.effectiveness': 'M22-form-effectiveness'
  },
  'M22:__by_screen__': {
    'M22-framework': 'M22-form-competency',
    'M22-devices': 'M22-form-device',
    'M22-assessments': 'M22-form-assessment',
    'M22-register': 'M22-form-certification',
    'M22-eligibility': 'M22-form-certification',
    'M22-catalogue': 'M22-form-course',
    'M22-paths': 'M22-form-path',
    'M22-schedule': 'M22-form-enrollment',
    'M22-sessions': 'M22-form-session',
    'M22-ojt': 'M22-form-ojt',
    'M22-iso': 'M22-form-evidence',
    'M22-budget': 'M22-form-budget',
    'M22-budget-exceptions': 'M22-form-budget-exception',
    'M22-needs': 'M22-form-need',
    'M22-plans': 'M22-form-plan',
    'M22-feedback': 'M22-form-feedback',
    'M22-mentoring': 'M22-form-mentoring',
    'M22-mentoring-log': 'M22-form-mentoring-log',
    'M22-effectiveness': 'M22-form-effectiveness'
  }
};

export const CREATE = {
  M22: { screen: 'M22-form-certification', model: 'fix.certification', label: 'Certification' }
};
