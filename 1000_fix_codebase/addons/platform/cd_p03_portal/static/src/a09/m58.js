/** @odoo-module **/
/* A09 · People & Workforce — M58 Talent Acquisition.
 * Registry-faithful: 4 groups / 10 screens / 5 reports / 4 forms / freg 50,
 * extended by the capture audit of 2026-11-17 and the candidate biodata
 * standard of 2026-11-18 (Candidate Evidence group, multi-grid biodata form). */

export const MODULE = {
  area: 'A09', code: 'M58', en: 'Talent Acquisition', title: 'M58 · Talent Acquisition',
  bn: 'প্রতিভা নিয়োগ', icon: '🧲',
  desc: 'Requisitions against budget, job postings, the candidate pipeline, structured interviews, practical assessments, reference and background checks, offers, pre-boarding and first-90-days reviews.',
  kpis: [
    { l: 'Open Requisitions', m: 'open_requisitions' },
    { l: 'Time-to-Fill (days)', m: 'time_to_fill' },
    { l: 'Pipeline', m: 'pipeline' },
    { l: 'Offer Accept Rate', m: 'offer_accept_rate', suffix: '%' },
    { l: 'Referral Share', m: 'referral_share', suffix: '%' },
    { l: 'First-90 Retention', m: 'first90_retention', suffix: '%' }
  ],
  groups: [
    { en: 'Record Coverage', screens: [
      { id: 'M58-talent-assessment', en: "Talent Assessment", bn: "ব্যবহারিক দক্ষতা মূল্যায়ন", t: 'g' }
    ]},
    { en: 'Requisitions', screens: [
      { id: 'M58-reqs', en: 'Requisitions', bn: 'নিয়োগ অনুরোধ', t: 'g' },
      { id: 'M58-approval', en: 'Approval vs Budget', bn: 'বাজেট অনুমোদন', t: 'g' },
      { id: 'M58-budget', en: 'Headcount Budget', bn: 'জনবল বাজেট', t: 'g' },
      { id: 'M58-job-profiles', en: 'Job Profiles', bn: 'পদের বিবরণ', t: 'g' }
    ]},
    { en: 'Sourcing', screens: [
      { id: 'M58-postings', en: 'Job Postings', bn: 'চাকরির বিজ্ঞপ্তি', t: 'g' },
      { id: 'M58-candidates', en: 'Candidate Pipeline', bn: 'প্রার্থী', t: 'g' },
      { id: 'M58-referrals', en: 'Employee Referrals', bn: 'কর্মী রেফারেল', t: 'g' },
      { id: 'M58-channels', en: 'Channels & Agencies', bn: 'নিয়োগ চ্যানেল', t: 'g' },
      { id: 'M58-costs', en: 'Recruitment Costs', bn: 'নিয়োগ ব্যয়', t: 'g' }
    ]},
    { en: 'Selection', screens: [
      { id: 'M58-interviews', en: 'Structured Interviews', bn: 'সাক্ষাৎকার', t: 'g' },
      { id: 'M58-evaluations', en: 'My Panel Evaluations', bn: 'আমার মূল্যায়ন', t: 'g' },
      { id: 'M58-practical', en: 'Practical Assessments', bn: 'ব্যবহারিক মূল্যায়ন', t: 'r' },
      { id: 'M58-checks', en: 'Reference & Background', bn: 'রেফারেন্স', t: 'g' },
      { id: 'M58-offers', en: 'Offers', bn: 'প্রস্তাব', t: 'g' }
    ]},
    { en: 'Candidate Evidence', screens: [
      { id: 'M58-cand-documents', en: 'Candidate Documents', bn: 'প্রার্থীর কাগজপত্র', t: 'g' },
      { id: 'M58-cand-education', en: 'Academic Qualifications', bn: 'শিক্ষাগত যোগ্যতা যাচাই', t: 'g' },
      { id: 'M58-cand-experience', en: 'Employment History', bn: 'কর্ম অভিজ্ঞতা যাচাই', t: 'g' },
      { id: 'M58-cand-training', en: 'Training & Certificates', bn: 'প্রশিক্ষণ সনদ যাচাই', t: 'g' }
    ]},
    { en: 'Onboarding', screens: [
      { id: 'M58-preboard', en: 'Pre-Boarding', bn: 'প্রি-বোর্ডিং', t: 'g' },
      { id: 'M58-preboard-docs', en: 'Pre-Boarding Documents', bn: 'যোগদান-পূর্ব কাগজপত্র', t: 'g' },
      { id: 'M58-onboarding-tasks', en: 'Onboarding Tasks', bn: 'অনবোর্ডিং কাজ', t: 'g' },
      { id: 'M58-inductions', en: 'Induction Sessions', bn: 'ইন্ডাকশন সেশন', t: 'g' },
      { id: 'M58-templates', en: 'Onboarding Templates', bn: 'অনবোর্ডিং টেমপ্লেট', t: 'g' },
      { id: 'M58-template-lines', en: 'Template Tasks', bn: 'টেমপ্লেটের কাজ', t: 'g' },
      { id: 'M58-first90', en: 'First-90-Days', bn: 'প্রথম ৯০ দিন', t: 'g' }
    ]}
  ],
  reports: ['Funnel & Conversion', 'Time-to-Fill by Role', 'Source Effectiveness', 'First-90 Retention', 'Practical Assessment Results', 'Cost per Hire', 'Day-One Readiness'],
  forms: ['Requisition', 'Candidate', 'Interview Round', 'Offer', 'Headcount Budget', 'Job Profile', 'Job Posting', 'Referral', 'Recruitment Channel', 'Recruitment Cost', 'Practical Assessment', 'Background Check', 'Pre-Boarding Document', 'Onboarding Task', 'Induction Session', 'Onboarding Template', 'Template Task', 'First-90 Review'],
  cross: ['M21 Workforce', 'M22 Competency', 'M54 Budgeting'],
  /* Capture audit 2026-11-17: each page captures the records it covers. The
   * budget and job profiles sat on no page; "Job Postings" listed
   * requisitions; assessments, checks, evaluations and onboarding tasks had
   * no capture on their page; pre-boarding offered a hand-made plan (the
   * hire makes it) and had no documents; onboarding captured only reviews. */
  freg: { src: 50, sub: [
    ['1', 'Workforce Planning & Requisition', 9, { model: 'fix.job.requisition', cols: ['name', 'department_id', 'position_id', 'openings', 'state'], screens: ['M58-reqs', 'M58-approval', 'M58-budget', 'M58-job-profiles'], reports: ['Time-to-Fill by Role'], forms: ['Requisition', 'Headcount Budget', 'Job Profile'] }],
    ['2', 'Sourcing', 7, { model: 'fix.candidate', cols: ['name', 'requisition_id', 'operating_unit_id', 'state'], screens: ['M58-postings', 'M58-candidates', 'M58-referrals', 'M58-channels', 'M58-costs'], reports: ['Source Effectiveness', 'Funnel & Conversion', 'Cost per Hire'], forms: ['Candidate', 'Job Posting', 'Referral', 'Recruitment Channel', 'Recruitment Cost'] }],
    ['3', 'Screening', 6, { model: 'fix.candidate', cols: ['name', 'requisition_id', 'state', 'create_date'], screens: ['M58-candidates', 'M58-cand-documents', 'M58-cand-education', 'M58-cand-experience', 'M58-cand-training'], reports: ['Funnel & Conversion'], forms: [], create: false, domain: [['state', 'in', ['applied', 'screening']]] }],
    ['4', 'Interviews & Assessments', 11, { model: 'fix.talent.interview', cols: ['name', 'candidate_id', 'scheduled_on', 'score', 'recommendation'], screens: ['M58-interviews', 'M58-evaluations', 'M58-practical', 'M58-talent-assessment'], reports: ['Practical Assessment Results'], forms: ['Interview Round', 'Practical Assessment'] }],
    ['5', 'Checks & Offers', 7, { model: 'fix.talent.offer', cols: ['name', 'candidate_id', 'position_id', 'joining_date', 'state'], screens: ['M58-checks', 'M58-offers'], reports: ['Funnel & Conversion'], forms: ['Offer', 'Background Check'] }],
    ['6', 'Pre-Boarding', 4, { model: 'fix.preboarding.document', cols: ['name', 'plan_id', 'document_type', 'mandatory', 'state'], screens: ['M58-preboard-docs', 'M58-preboard'], reports: [], forms: ['Pre-Boarding Document'] }],
    ['7', 'Onboarding Orchestration', 6, { model: 'fix.onboarding.task', cols: ['name', 'plan_id', 'function', 'owner_id', 'due_date', 'state'], screens: ['M58-onboarding-tasks', 'M58-inductions', 'M58-first90', 'M58-templates', 'M58-template-lines'], reports: ['Day-One Readiness', 'First-90 Retention'], forms: ['Onboarding Task', 'Induction Session', 'First-90 Review', 'Onboarding Template', 'Template Task'] }]
  ] }
};

export const SCREENS = {
  'M58-talent-assessment': { kind: 'model_list', model: 'fix.talent.assessment',
    cols: ['name', 'candidate_id', 'requisition_id', 'competency_code', 'assessed_on', 'score', 'passed', 'assessor_id'] },
  'M58-reqs': { kind: 'model_list', model: 'fix.job.requisition', stateField: 'state',
    cols: ['name', 'department_id', 'position_id', 'openings', 'hiring_manager_id', 'budget_year', 'over_budget', 'operating_unit_id', 'approval_state', 'approved_by_id', 'state'],
    /* A09 audit M58-F3: "Approve Requisition" was the requester's own state
     * flip. The requester asks; an approver decides from the M63 inbox. A
     * requisition fills itself when its hires reach the approved headcount. */
    actions: [
      { m: 'action_request_approval', l: 'Request Approval' },
      { m: 'action_recall_approval', l: 'Recall Approval' },
      { m: 'action_close', l: 'Close Requisition' }
    ] },
  'M58-approval': { kind: 'model_list', model: 'fix.job.requisition', stateField: 'state',
    cols: ['name', 'position_id', 'openings', 'budget_id', 'over_budget', 'approval_state', 'approved_by_id', 'approved_on', 'state'] },
  /* Round 2 (BRU-TAO-01): the approved headcount per position or department
   * and year, decided by the CFO tier. A requisition beyond it is refused,
   * or routed to the CFO tier with its justification. */
  'M58-budget': { kind: 'model_list', model: 'fix.headcount.budget', stateField: 'state',
    cols: ['name', 'year', 'position_id', 'department_id', 'approved_headcount', 'used_headcount', 'approval_state', 'approved_by_id', 'state'],
    actions: [
      { m: 'action_request_approval', l: 'Request Approval (CFO)' },
      { m: 'action_recall_approval', l: 'Recall Approval' },
      { m: 'action_close', l: 'Close Budget' }
    ] },
  /* Capture audit 2026-11-17: "Job Postings" listed requisitions. A posting
   * is published only for an open, approved requisition (BRU-TAO-02), and an
   * external one only after the internal window (FR-TAO-006). */
  'M58-postings': { kind: 'model_list', model: 'fix.job.posting', stateField: 'state',
    cols: ['name', 'title', 'requisition_id', 'audience', 'channel_id', 'published_on', 'internal_only_until', 'closes_on', 'candidate_count', 'state'],
    actions: [
      { m: 'action_publish', l: 'Publish' },
      { m: 'action_close', l: 'Close Posting' }
    ] },
  'M58-job-profiles': { kind: 'model_list', model: 'fix.job.profile',
    cols: ['name', 'position_id', 'min_experience_years', 'band_id', 'active'] },
  'M58-referrals': { kind: 'model_list', model: 'fix.talent.referral', stateField: 'reward_state',
    cols: ['name', 'candidate_id', 'referring_employee_id', 'requisition_id', 'candidate_state', 'reward_amount', 'reward_state', 'decided_by_id'],
    actions: [
      { m: 'action_approve_reward', l: 'Approve Reward (HR Manager)' },
      { m: 'action_decline_reward', l: 'No Reward', ask: 'Why is no reward due?', kwarg: 'reason' }
    ] },
  'M58-channels': { kind: 'model_list', model: 'fix.recruitment.channel',
    cols: ['name', 'channel_type', 'partner_id', 'cost_model', 'fee', 'contract_ref', 'active'] },
  'M58-costs': { kind: 'model_list', model: 'fix.recruitment.cost',
    cols: ['name', 'requisition_id', 'channel_id', 'cost_type', 'amount', 'incurred_on', 'invoice_ref'] },
  'M58-candidates': { kind: 'model_list', model: 'fix.candidate', stateField: 'state',
    cols: ['name', 'email', 'phone', 'requisition_id', 'employee_id', 'operating_unit_id', 'state'],
    actions: [
      { m: 'action_screen', l: 'Screen' },
      { m: 'action_interview', l: 'Invite to Interview' },
      { m: 'action_offer', l: 'Move to Offer Stage' },
      { m: 'action_reject', l: 'Reject', ask: 'Outcome communicated to the candidate', kwarg: 'reason' },
      { m: 'action_hire', l: 'Hire (accepted offer)' }
    ] },
  /* Candidate biodata standard (18 Nov 2026): the evidence a candidate gives
   * on the Candidate Biodata form, decided by a Background Verifier who did
   * not key or upload it. Rows are added on the candidate form, never here. */
  'M58-cand-documents': { kind: 'model_list', model: 'fix.candidate.document', stateField: 'verification_state',
    create: false,
    empty: 'No candidate document yet. Documents are added on the Candidate Biodata form (Documents & Attachments tab).',
    cols: ['candidate_id', 'document_type', 'description', 'reference', 'candidate_state', 'uploaded_by_id', 'verification_state', 'verified_by_id', 'verified_on', 'verification_note'],
    actions: [
      { m: 'action_verify', l: 'Verify (Background Verifier)' },
      { m: 'action_flag_discrepancy', l: 'Flag Discrepancy', ask: 'What does the document not support?', kwarg: 'reason' }
    ] },
  'M58-cand-education': { kind: 'model_list', model: 'fix.candidate.education', stateField: 'verification_state',
    create: false,
    empty: 'No qualification yet. Qualifications are added on the Candidate Biodata form (Education tab).',
    cols: ['candidate_id', 'level', 'exam_title', 'institute', 'board', 'passing_year', 'result_type', 'result', 'roll_number', 'registration_number', 'verification_state', 'verified_by_id'],
    actions: [
      { m: 'action_verify', l: 'Verify (Background Verifier)' },
      { m: 'action_flag_discrepancy', l: 'Flag Discrepancy', ask: 'What does the board / university record show?', kwarg: 'reason' }
    ] },
  'M58-cand-experience': { kind: 'model_list', model: 'fix.candidate.experience', stateField: 'verification_state',
    create: false,
    empty: 'No employment yet. Employment is added on the Candidate Biodata form (Employment History tab).',
    cols: ['candidate_id', 'employer', 'designation', 'start_date', 'end_date', 'duration_years', 'supervisor_name', 'supervisor_phone', 'may_contact', 'verification_state', 'verified_by_id'],
    actions: [
      { m: 'action_verify', l: 'Verify (Background Verifier)' },
      { m: 'action_flag_discrepancy', l: 'Flag Discrepancy', ask: 'What did the employer or letter show?', kwarg: 'reason' }
    ] },
  'M58-cand-training': { kind: 'model_list', model: 'fix.candidate.training', stateField: 'verification_state',
    create: false,
    empty: 'No training yet. Training and certificates are added on the Candidate Biodata form.',
    cols: ['candidate_id', 'kind', 'title', 'institute', 'end_date', 'certificate_no', 'expiry_date', 'verification_state', 'verified_by_id'],
    actions: [
      { m: 'action_verify', l: 'Verify (Background Verifier)' },
      { m: 'action_flag_discrepancy', l: 'Flag Discrepancy', ask: 'What does the issuer record show?', kwarg: 'reason' }
    ] },
  /* Round 2 (BRU-TAO-07): each panelist evaluates on their own; the round's
   * score and recommendation appear only once every panelist submitted. */
  'M58-interviews': { kind: 'model_list', model: 'fix.talent.interview', stateField: 'state',
    cols: ['name', 'candidate_id', 'interviewer_id', 'scheduled_on', 'round_no', 'panel_size', 'panel_submitted', 'score', 'recommendation', 'state'],
    actions: [
      { m: 'action_add_panelist', l: 'Add Panelist', ask: 'Employee id, code or full name', kwarg: 'panelist' },
      { m: 'action_remove_panelist', l: 'Remove Panelist', ask: 'Employee id, code or full name', kwarg: 'panelist' },
      { m: 'action_done', l: 'Complete Round' },
      { m: 'action_cancel', l: 'Cancel' }
    ] },
  'M58-evaluations': { kind: 'model_list', model: 'fix.talent.evaluation', stateField: 'state',
    /* opened by naming the panelist on the interview round, never typed */
    create: false,
    empty: 'No evaluation for you yet. An evaluation opens when you are named on an interview panel; you then score and submit it here.',
    cols: ['candidate_name', 'round_no', 'scheduled_on', 'panelist_id', 'score', 'recommendation', 'submitted_on', 'state'],
    actions: [{ m: 'action_submit', l: 'Submit My Evaluation' }] },
  'M58-practical': { kind: 'table_report', module: 'M58', report: 'practical_results', title: 'Practical Assessment Results', period: true },
  'M58-checks': { kind: 'model_list', model: 'fix.talent.check', stateField: 'result',
    cols: ['name', 'candidate_id', 'check_type', 'requested_on', 'completed_on', 'result', 'verified_by_id', 'approval_state'],
    /* A09 audit M58-F5: a check is cleared by a Background Verifier, not the
     * recruiter, on the evidence attached to it. */
    actions: [
      { m: 'action_request_approval', l: 'Send for Verification' },
      { m: 'action_recall_approval', l: 'Recall' },
      { m: 'action_mark_failed', l: 'Record Failed', ask: 'What did the check find?', kwarg: 'reason' },
      { m: 'action_mark_discrepancy', l: 'Record Discrepancy', ask: 'What did the check find?', kwarg: 'reason' }
    ] },
  'M58-offers': { kind: 'model_list', model: 'fix.talent.offer', stateField: 'state',
    cols: ['name', 'candidate_id', 'position_id', 'gross_salary', 'basic_salary', 'in_band', 'issued_on', 'joining_date', 'approval_state', 'state'],
    /* A09 audit M58-F4: an offer is issued by its approver (the CFO tier when
     * it is outside the M57 band); acceptance is the candidate's signed act. */
    actions: [
      { m: 'action_request_approval', l: 'Request Approval to Issue' },
      { m: 'action_recall_approval', l: 'Recall Approval' },
      { m: 'action_accept', l: 'Record Signed Acceptance' },
      { m: 'action_decline', l: 'Record Decline' }
    ] },
  'M58-preboard': { kind: 'model_list', model: 'fix.onboarding.plan',
    /* the hire opens the plan from the accepted offer; it is never typed */
    create: false,
    empty: 'No onboarding plan yet. A plan opens when an accepted offer completes the hire.',
    cols: ['name', 'candidate_id', 'requisition_id', 'employee_id', 'joined_date', 'mentor_id', 'documents_required', 'documents_verified', 'nid_verified', 'contract_signed', 'bank_details_captured', 'safety_kit_issued', 'open_mandatory_tasks', 'state'],
    /* Round 2 (M24, BLA s.5): the appointment letter is generated at hire and
     * acknowledged by the employee (in person, or their signed copy attested
     * by a verifier who did not upload it); every mandatory task is done. */
    actions: [
      { m: 'action_start', l: 'Start Onboarding' },
      { m: 'action_acknowledge_appointment', l: 'Acknowledge My Appointment Letter' },
      { m: 'action_attest_signed_appointment', l: 'Attest Signed Appointment Letter' },
      { m: 'action_complete', l: 'Complete (Provision Identity)' }
    ] },
  /* Capture audit 2026-11-17: verified by someone other than the uploader
   * (FR-TAO-024); onboarding completes only when every mandatory one is. */
  'M58-preboard-docs': { kind: 'model_list', model: 'fix.preboarding.document', stateField: 'state',
    cols: ['name', 'plan_id', 'candidate_id', 'document_type', 'mandatory', 'submitted_on', 'uploaded_by_id', 'verified_by_id', 'verified_on', 'state'],
    actions: [
      { m: 'action_verify', l: 'Verify (Background Verifier)' },
      { m: 'action_reject', l: 'Reject', ask: 'What is wrong with the document?', kwarg: 'reason' }
    ] },
  'M58-inductions': { kind: 'model_list', model: 'fix.onboarding.induction', stateField: 'state',
    cols: ['name', 'plan_id', 'employee_id', 'session_type', 'scheduled_at', 'conductor_id', 'venue', 'recorded_by_id', 'state'],
    actions: [
      { m: 'action_mark_attended', l: 'Record Attended (conductor)' },
      { m: 'action_mark_missed', l: 'Record Missed (conductor)', ask: 'Why was the session missed?', kwarg: 'reason' },
      { m: 'action_cancel', l: 'Cancel', ask: 'Why is the session cancelled?', kwarg: 'reason' }
    ] },
  'M58-templates': { kind: 'model_list', model: 'fix.onboarding.template',
    cols: ['name', 'company_id', 'is_default', 'active'] },
  'M58-template-lines': { kind: 'model_list', model: 'fix.onboarding.template.line',
    cols: ['template_id', 'sequence', 'name', 'function', 'owner_user_id', 'due_offset_days', 'mandatory', 'evidence_required', 'field_role_only'] },
  'M58-onboarding-tasks': { kind: 'model_list', model: 'fix.onboarding.task', stateField: 'state',
    cols: ['name', 'plan_id', 'function', 'owner_id', 'due_date', 'depends_on_id', 'mandatory', 'overdue', 'completed_by_id', 'state'],
    actions: [
      { m: 'action_done', l: 'Mark Done (owner)' },
      { m: 'action_cancel', l: 'Cancel (optional task)', ask: 'Why is the task cancelled?', kwarg: 'reason' }
    ] },
  'M58-first90': { kind: 'model_list', model: 'fix.talent.first90',
    cols: ['name', 'employee_id', 'milestone', 'check_date', 'rating', 'on_track'] },

  /* Report chips -> their own computed pack */
  'M58-rpt-funnel': { kind: 'table_report', module: 'M58', report: 'funnel_conversion', title: 'Funnel & Conversion', period: true },
  'M58-rpt-ttf': { kind: 'table_report', module: 'M58', report: 'time_to_fill', title: 'Time-to-Fill by Role', period: true },
  'M58-rpt-source': { kind: 'table_report', module: 'M58', report: 'source_effectiveness', title: 'Source Effectiveness', period: true },
  'M58-rpt-retention': { kind: 'table_report', module: 'M58', report: 'first90_retention', title: 'First-90 Retention', period: true },
  'M58-rpt-practical': { kind: 'table_report', module: 'M58', report: 'practical_results', title: 'Practical Assessment Results', period: true },
  'M58-rpt-cost': { kind: 'table_report', module: 'M58', report: 'cost_per_hire', title: 'Cost per Hire', period: true },
  'M58-rpt-readiness': { kind: 'table_report', module: 'M58', report: 'day_one_readiness', title: 'Day-One Readiness', period: true },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M58-form-req': {
    kind: 'model_form',
    model: 'fix.job.requisition',
    title: 'Job Requisition',
    back: 'M58-reqs',
    status: { field: 'state', labels: {
      draft: 'Draft', open: 'Open', hired: 'Filled', closed: 'Closed' } },
    tabs: [
      { id: 'scope', label: 'Requisition Scope', bn: 'নিয়োগের চাহিদা', icon: '📋', badge: '10' },
      { id: 'workflow', label: 'Status & Approval', bn: 'অবস্থা ও অনুমোদন', icon: '⚙️', badge: '1' }
    ],
    sections: [
      {
        tab: 'scope',
        title: 'Manpower Requisition Particulars',
        note: 'Approved headcount requisition under company workforce budget.',
        fields: [
          { name: 'name', required: true, label: 'Requisition Title' },
          { name: 'department_id', required: true, label: 'Target Department' },
          { name: 'position_id', required: true, label: 'Target Establishment Position' },
          { name: 'openings', required: true, label: 'Open Positions (Headcount)' },
          { name: 'operating_unit_id', label: 'Branch / Operating Unit' },
          { name: 'is_field_role', label: 'Field / In-Home Role (PCC & Assessment)' },
          { name: 'assessment_pass_mark', label: 'Practical Assessment Pass Mark (%)' },
          { name: 'hiring_manager_id', label: 'Hiring Manager' },
          { name: 'job_profile_id', label: 'Job Profile (FR-TAO-004)' },
          { name: 'onboarding_template_id', label: 'Onboarding Template' }
        ]
      },
      {
        tab: 'workflow',
        title: 'Headcount Budget (BRU-TAO-01)',
        note: 'Checked at submission against the approved budget of the position, else the department, for the year.',
        fields: [
          { name: 'budget_year', required: true, label: 'Budget Year' },
          { name: 'over_budget_reason', type: 'text', label: 'Over-Budget Justification (routes to the CFO tier)' },
          { name: 'budget_id', label: 'Headcount Budget', readonly: true },
          { name: 'over_budget', label: 'Beyond Budget', readonly: true }
        ]
      },
      {
        tab: 'workflow',
        title: 'Requisition Lifecycle Status',
        note: 'Budget and department authorization.',
        fields: [
          { name: 'state', label: 'Requisition State', readonly: true },
          { name: 'approval_state', label: 'Approval', readonly: true },
          { name: 'approved_by_id', label: 'Approved By', readonly: true },
          { name: 'approved_on', label: 'Approved On', readonly: true },
          { name: 'openings_left', label: 'Openings Left', readonly: true }
        ]
      }
    ]
  },

  /* Candidate biodata standard (18 Nov 2026). The form held twelve fields:
   * no education, training, work history, languages, referees, family or
   * documents could be recorded. Each register is now an add-more-lines grid
   * with a scan or photo per row; header fields are grouped by the stage at
   * which they may be asked (sensitive joining particulars only from the
   * offer stage, PDPO 2025 data minimisation). Evidence rows are verified on
   * the Candidate Evidence lists by a verifier who did not key them. */
  'M58-form-candidate': {
    kind: 'model_form',
    model: 'fix.candidate',
    title: 'Candidate Biodata',
    back: 'M58-candidates',
    status: { field: 'state', labels: {
      applied: 'Applied', screening: 'Screening', interview: 'Interview',
      offered: 'Offered', hired: 'Hired', rejected: 'Rejected' } },
    tabs: [
      { id: 'biodata', label: 'Personal & Contact', bn: 'ব্যক্তিগত তথ্য ও যোগাযোগ', icon: '👤', badge: '24' },
      { id: 'application', label: 'Application & Screening', bn: 'আবেদন ও বাছাই', icon: '📋', badge: '30' },
      { id: 'education', label: 'Education', bn: 'শিক্ষাগত যোগ্যতা', icon: '🎓', badge: '+' },
      { id: 'training', label: 'Training & Certifications', bn: 'প্রশিক্ষণ ও সনদ', icon: '📜', badge: '+' },
      { id: 'experience', label: 'Employment History', bn: 'কর্ম অভিজ্ঞতা', icon: '💼', badge: '+' },
      { id: 'skills', label: 'Skills, Languages & Referees', bn: 'দক্ষতা, ভাষা ও রেফারেন্স', icon: '🗣️', badge: '+' },
      { id: 'documents', label: 'Documents & Attachments', bn: 'কাগজপত্র ও সংযুক্তি', icon: '📎', badge: '+' },
      { id: 'joining', label: 'Joining Particulars & Family', bn: 'যোগদান তথ্য ও পরিবার', icon: '🏠', badge: '6' },
      { id: 'consent', label: 'Consent & Declaration', bn: 'সম্মতি ও ঘোষণা', icon: '✅', badge: '6' },
      { id: 'pipeline', label: 'Recruitment Stage', bn: 'নিয়োগ পর্যায়', icon: '📊', badge: '3' }
    ],
    sections: [
      {
        tab: 'biodata',
        title: 'Identity',
        note: 'Father’s and mother’s names, NID or birth registration are asked from a shortlisted candidate; they become the Form 7 service book entries at hire.',
        fields: [
          { name: 'name', required: true, label: 'Full Name (English, as on NID / certificate)' },
          { name: 'name_bn', label: 'Full Name (Bangla)' },
          { name: 'photo', type: 'image', label: 'Photograph' },
          { name: 'date_of_birth', label: 'Date of Birth (verified)' },
          { name: 'nationality_id', label: 'Nationality' },
          { name: 'nid_number', label: 'NID Number (10 / 13 / 17 digits)' },
          { name: 'birth_reg_number', label: 'Birth Registration No. (if no NID)' },
          { name: 'passport_number', label: 'Passport No.' },
          { name: 'father_name', label: 'Father’s Name' },
          { name: 'mother_name', label: 'Mother’s Name' }
        ]
      },
      {
        tab: 'biodata',
        title: 'Contact',
        note: 'Many technicians have no email: the mobile number is the main contact.',
        fields: [
          { name: 'phone', label: 'Mobile Phone' },
          { name: 'alt_phone', label: 'Alternative Mobile' },
          { name: 'email', label: 'Email' }
        ]
      },
      {
        tab: 'biodata',
        title: 'Present Address',
        note: 'Used to route the application to the nearest branch.',
        fields: [
          { name: 'present_address', label: 'House / Road / Village' },
          { name: 'present_upazila', label: 'Upazila / Thana' },
          { name: 'present_district', label: 'District' },
          { name: 'present_division', label: 'Division' },
          { name: 'present_post_code', label: 'Post Code' }
        ]
      },
      {
        tab: 'biodata',
        title: 'Permanent Address',
        note: 'The statutory permanent (home) address. Tick the box to copy the present address.',
        fields: [
          { name: 'permanent_same_as_present', label: 'Same as Present Address' },
          { name: 'permanent_address', label: 'Village / Road / Post Office' },
          { name: 'permanent_upazila', label: 'Upazila / Thana' },
          { name: 'permanent_district', label: 'District' },
          { name: 'permanent_division', label: 'Division' },
          { name: 'permanent_post_code', label: 'Post Code' }
        ]
      },
      {
        tab: 'application',
        title: 'Application',
        note: 'The requisition, branch and channel the application came through, and the CV.',
        fields: [
          { name: 'requisition_id', label: 'Job Requisition' },
          { name: 'operating_unit_id', label: 'Target Branch / Operating Unit' },
          { name: 'source', label: 'Source / Channel' },
          { name: 'posting_id', label: 'Applied Through Posting' },
          { name: 'channel_id', label: 'Channel / Agency' },
          { name: 'applied_on', label: 'Applied On' },
          { name: 'current_employer', label: 'Current / Last Employer' },
          { name: 'current_designation', label: 'Current / Last Designation' },
          { name: 'highest_education_level', label: 'Highest Qualification (from Education)', readonly: true },
          { name: 'total_experience_years', label: 'Total Experience in Years (from History)', readonly: true },
          { name: 'cv_file', type: 'binary', label: 'CV / Resume' },
          { name: 'cv_filename', label: 'CV File Name' },
          { name: 'career_summary', type: 'text', label: 'Career Objective / Summary' },
          { name: 'key_skills', type: 'text', label: 'Key Skills (summary)' }
        ]
      },
      {
        tab: 'application',
        title: 'Screening',
        note: 'Salary fields are visible to Recruitment only. Licence and motorcycle matter for field technicians.',
        fields: [
          { name: 'current_salary', label: 'Current Gross Salary (BDT / month)' },
          { name: 'expected_salary', label: 'Expected Gross Salary (BDT / month)' },
          { name: 'notice_period_days', label: 'Notice Period (days)' },
          { name: 'earliest_joining_date', label: 'Earliest Joining Date' },
          { name: 'preferred_locations', label: 'Preferred Work Locations' },
          { name: 'willing_to_relocate', label: 'Willing to Relocate' },
          { name: 'willing_to_travel', label: 'Willing to Travel / Field Work' },
          { name: 'shift_work_ok', label: 'Can Work Shifts / Nights' },
          { name: 'owns_motorcycle', label: 'Owns a Motorcycle / Bicycle' },
          { name: 'driving_licence_held', label: 'Holds a Driving Licence' },
          { name: 'driving_licence_no', label: 'Driving Licence No.' },
          { name: 'driving_licence_class', label: 'Driving Licence Class' },
          { name: 'driving_licence_expiry', label: 'Driving Licence Expiry' }
        ]
      },
      {
        tab: 'application',
        title: 'Disclosures',
        note: 'Conflict of interest, previous history with 1000 FiX and the criminal-record declaration (restricted to Recruitment).',
        fields: [
          { name: 'previously_applied', label: 'Applied to 1000 FiX Before' },
          { name: 'previously_employed', label: 'Worked at 1000 FiX Before' },
          { name: 'previous_employee_code', label: 'Previous Employee ID' },
          { name: 'relative_in_company', label: 'Relative Works at 1000 FiX' },
          { name: 'relative_details', label: 'Relative’s Name, Relation and Branch' },
          { name: 'criminal_record', label: 'Criminal Record Declaration' },
          { name: 'criminal_record_details', type: 'text', label: 'Conviction Details' },
          { name: 'accommodation_needs', type: 'text', label: 'Accommodation Needs (voluntary)' }
        ]
      },
      {
        tab: 'documents',
        title: 'Evidence Status',
        note: 'Each certificate, letter and document is verified on the Candidate Evidence lists by a Background Verifier who did not key or upload it. A discrepancy blocks the offer stage and the hire.',
        fields: [
          { name: 'evidence_pending', label: 'Awaiting Verification', readonly: true },
          { name: 'evidence_discrepancies', label: 'Discrepancies', readonly: true }
        ]
      },
      {
        tab: 'joining',
        title: 'Joining Particulars (offer stage onward)',
        note: 'Sensitive personal data is asked only once the candidate reaches the offer stage; before that these inputs stay locked (data minimisation). They become the employee master at hire.',
        fields: [
          { name: 'sex', label: 'Gender' },
          { name: 'marital_status', label: 'Marital Status' },
          { name: 'spouse_name', label: 'Spouse’s Name' },
          { name: 'religion', label: 'Religion' },
          { name: 'blood_group', label: 'Blood Group' },
          { name: 'identification_mark', label: 'Identification Mark (Form 7)' }
        ]
      },
      {
        tab: 'consent',
        title: 'Consent & Declaration',
        note: 'Consent to process this application, a separate consent to keep the record in the talent pool, and the candidate’s declaration that everything given is true. The hire needs the declaration.',
        fields: [
          { name: 'consent_given', label: 'Consent to Processing & Retention' },
          { name: 'consent_date', label: 'Consent Recorded On', readonly: true },
          { name: 'talent_pool_consent', label: 'Consent to Keep in Talent Pool' },
          { name: 'declaration_accepted', label: 'Declaration of Truth Accepted' },
          { name: 'declaration_on', label: 'Declaration Recorded On', readonly: true },
          { name: 'retention_until', label: 'Retain Until', readonly: true }
        ]
      },
      {
        tab: 'pipeline',
        title: 'Hiring Funnel',
        note: 'Pipeline progression from application to hire and the linked M21 employee master.',
        fields: [
          { name: 'employee_id', label: 'Created M21 Employee Record', readonly: true },
          { name: 'state', label: 'Recruitment Stage', readonly: true },
          { name: 'rejection_reason', type: 'text', label: 'Outcome Communicated', readonly: true }
        ]
      }
    ],
    grids: [
      {
        field: 'education_ids', tab: 'education', title: 'Academic Qualifications',
        addLabel: '+ Add qualification',
        empty: 'No qualification yet. Add SSC / Dakhil onward, one line per exam or degree.',
        note: 'One line per exam or degree, highest last or first. Attach the certificate and the transcript / mark sheet of each line. Result: GPA out of 5 (SSC / HSC), CGPA out of 4 (university), or the division / class of older results.',
        fields: [
          { name: 'level', label: 'Level' },
          { name: 'exam_title', label: 'Exam / Degree' },
          { name: 'major', label: 'Group / Major' },
          { name: 'board', label: 'Board' },
          { name: 'institute', label: 'Institute' },
          { name: 'passing_year', label: 'Year' },
          { name: 'result_type', label: 'Result Type' },
          { name: 'result', label: 'Result' },
          { name: 'duration_years', label: 'Duration (yrs)' },
          { name: 'roll_number', label: 'Roll No.' },
          { name: 'registration_number', label: 'Reg. No.' },
          { name: 'achievement', label: 'Achievement' },
          { name: 'certificate_file', label: 'Certificate' },
          { name: 'certificate_filename', label: 'Certificate File Name' },
          { name: 'transcript_file', label: 'Transcript' },
          { name: 'transcript_filename', label: 'Transcript File Name' },
          { name: 'verification_state', label: 'Verification', readonly: true },
          { name: 'verified_by_id', label: 'Verified By', readonly: true }
        ]
      },
      {
        field: 'training_ids', tab: 'training', title: 'Training, Certifications & Licences',
        addLabel: '+ Add training / certificate',
        empty: 'No training or certificate yet.',
        note: 'Training courses, NTVQF / BNQF skills certificates, OEM brand accreditations and professional licences, each with its certificate.',
        fields: [
          { name: 'kind', label: 'Type' },
          { name: 'title', label: 'Title' },
          { name: 'topic', label: 'Topics' },
          { name: 'institute', label: 'Institute / Issuer' },
          { name: 'country_id', label: 'Country' },
          { name: 'location', label: 'Location' },
          { name: 'start_date', label: 'From' },
          { name: 'end_date', label: 'To / Issued' },
          { name: 'duration', label: 'Duration' },
          { name: 'level', label: 'NTVQF Level' },
          { name: 'certificate_no', label: 'Certificate No.' },
          { name: 'expiry_date', label: 'Valid Until' },
          { name: 'certificate_file', label: 'Certificate' },
          { name: 'certificate_filename', label: 'Certificate File Name' },
          { name: 'verification_state', label: 'Verification', readonly: true },
          { name: 'verified_by_id', label: 'Verified By', readonly: true }
        ]
      },
      {
        field: 'experience_ids', tab: 'experience', title: 'Employment History',
        addLabel: '+ Add employment',
        empty: 'No employment yet (a fresh graduate may leave this empty).',
        note: 'Most recent first. Tick Currently Working and leave To empty for the present job. Attach the experience or release letter; the referee check reads the supervisor contact.',
        fields: [
          { name: 'employer', label: 'Employer' },
          { name: 'business_type', label: 'Business Type' },
          { name: 'employer_address', label: 'Employer Address' },
          { name: 'designation', label: 'Designation' },
          { name: 'department', label: 'Department' },
          { name: 'start_date', label: 'From' },
          { name: 'end_date', label: 'To' },
          { name: 'currently_working', label: 'Current' },
          { name: 'duration_years', label: 'Years', readonly: true },
          { name: 'responsibilities', type: 'text', label: 'Responsibilities' },
          { name: 'last_salary', label: 'Last Gross Salary' },
          { name: 'reason_for_leaving', label: 'Reason for Leaving' },
          { name: 'supervisor_name', label: 'Supervisor' },
          { name: 'supervisor_phone', label: 'Supervisor Phone' },
          { name: 'may_contact', label: 'May Contact' },
          { name: 'experience_letter_file', label: 'Experience / Release Letter' },
          { name: 'experience_letter_filename', label: 'Letter File Name' },
          { name: 'verification_state', label: 'Verification', readonly: true },
          { name: 'verified_by_id', label: 'Verified By', readonly: true }
        ]
      },
      {
        field: 'skill_ids', tab: 'skills', title: 'Skills',
        addLabel: '+ Add skill',
        empty: 'No skill yet.',
        note: 'Technical skills by device category (e.g. chip-level mobile repair, BGA rework, inverter AC) and the brands handled.',
        fields: [
          { name: 'category', label: 'Category' },
          { name: 'skill', label: 'Skill' },
          { name: 'level', label: 'Level' },
          { name: 'years', label: 'Years' },
          { name: 'brands', label: 'Brands / Products' }
        ]
      },
      {
        field: 'language_ids', tab: 'skills', title: 'Languages',
        addLabel: '+ Add language',
        empty: 'No language yet.',
        fields: [
          { name: 'language', label: 'Language' },
          { name: 'other_language', label: 'Other Language' },
          { name: 'reading', label: 'Reading' },
          { name: 'writing', label: 'Writing' },
          { name: 'speaking', label: 'Speaking' }
        ]
      },
      {
        field: 'reference_ids', tab: 'skills', title: 'Referees',
        addLabel: '+ Add referee',
        empty: 'No referee yet. Two non-relative referees are usual.',
        note: 'Professional or academic referees, not relatives. The reference check itself is recorded on Reference & Background.',
        fields: [
          { name: 'name', label: 'Name' },
          { name: 'designation', label: 'Designation' },
          { name: 'organisation', label: 'Organisation' },
          { name: 'relation', label: 'Relation' },
          { name: 'phone', label: 'Phone' },
          { name: 'email', label: 'Email' },
          { name: 'address', label: 'Address' },
          { name: 'years_known', label: 'Years Known' },
          { name: 'consent_to_contact', label: 'May Contact' }
        ]
      },
      {
        field: 'document_ids', tab: 'documents', title: 'Documents & Attachments',
        addLabel: '+ Add document',
        empty: 'No document yet. Add the CV, photograph, NID, certificates, transcripts, testimonials, release letters, PCC and others, one line each.',
        note: 'One line per document, with its scan or photo (PDF, JPG, PNG or DOCX, up to 10 MB). Bank, nominee, e-TIN and medical documents are asked from the offer stage. Verified documents carry into the employee dossier and the pre-boarding checklist at hire.',
        fields: [
          { name: 'document_type', label: 'Document Type' },
          { name: 'description', label: 'Description' },
          { name: 'issued_by', label: 'Issued By' },
          { name: 'reference', label: 'Document No.' },
          { name: 'issued_on', label: 'Issued On' },
          { name: 'expiry_date', label: 'Valid Until' },
          { name: 'original_seen', label: 'Original Seen' },
          { name: 'document_file', label: 'File' },
          { name: 'document_filename', label: 'File Name' },
          { name: 'verification_state', label: 'Verification', readonly: true },
          { name: 'verified_by_id', label: 'Verified By', readonly: true }
        ]
      },
      {
        field: 'family_ids', tab: 'joining', title: 'Family, Emergency Contacts & Nominees',
        addLabel: '+ Add family member',
        empty: 'Asked from the offer stage: family members, at least one emergency contact, and the statutory nominees (shares up to 100%).',
        note: 'Nominees receive the death benefit, provident fund and gratuity under the Labour Act; a minor nominee needs a guardian.',
        fields: [
          { name: 'name', label: 'Name' },
          { name: 'relation', label: 'Relation' },
          { name: 'date_of_birth', label: 'Date of Birth' },
          { name: 'occupation', label: 'Occupation' },
          { name: 'phone', label: 'Phone' },
          { name: 'address', label: 'Address' },
          { name: 'is_emergency_contact', label: 'Emergency Contact' },
          { name: 'is_nominee', label: 'Nominee' },
          { name: 'nominee_pct', label: 'Share %' },
          { name: 'guardian_name', label: 'Guardian (minor)' }
        ]
      }
    ]
  },

  'M58-form-interview': {
    kind: 'model_form',
    model: 'fix.talent.interview',
    title: 'Interview Round',
    back: 'M58-interviews',
    status: { field: 'state', labels: {
      scheduled: 'Scheduled', done: 'Completed', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'schedule', label: 'Interview Round', bn: 'সাক্ষাৎকার রাউন্ড', icon: '🗓️', badge: '5' },
      { id: 'evaluation', label: 'Scoring & Notes', bn: 'রেটিং ও মন্তব্য', icon: '✍️', badge: '4' }
    ],
    sections: [
      {
        tab: 'schedule',
        title: 'Interview Schedule & Focus Area',
        note: 'Structured technical and behavioral assessment rounds.',
        fields: [
          { name: 'candidate_id', required: true, label: 'Candidate' },
          { name: 'requisition_id', label: 'Job Requisition', readonly: true },
          { name: 'interviewer_id', label: 'Lead Interviewer (joins the panel)' },
          { name: 'scheduled_on', required: true, label: 'Scheduled Date & Time' },
          { name: 'round_no', required: true, label: 'Round Number' }
        ]
      },
      {
        tab: 'evaluation',
        title: 'Panel Result (BRU-TAO-07)',
        note: 'Each panelist submits their own evaluation; the panel result appears only when all have.',
        fields: [
          { name: 'competency_code', label: 'Primary Competency Evaluated' },
          { name: 'panel_size', label: 'Panel Size', readonly: true },
          { name: 'panel_submitted', label: 'Evaluations Submitted', readonly: true },
          { name: 'panel_complete', label: 'Panel Complete', readonly: true },
          { name: 'score', label: 'Panel Score (1-5)', readonly: true },
          { name: 'recommendation', label: 'Panel Recommendation', readonly: true },
          { name: 'notes', type: 'text', label: 'Coordinator Notes (logistics only)' }
        ]
      }
    ]
  },

  'M58-form-offer': {
    kind: 'model_form',
    model: 'fix.talent.offer',
    title: 'Job Offer',
    back: 'M58-offers',
    status: { field: 'state', labels: {
      draft: 'Draft', issued: 'Issued', accepted: 'Accepted', declined: 'Declined',
      expired: 'Expired' } },
    tabs: [
      { id: 'package', label: 'Compensation Package', bn: 'বেতন প্যাকেজ', icon: '💵', badge: '11' },
      { id: 'terms', label: 'Timeline & Acceptance', bn: 'শর্তাবলী ও সম্মতি', icon: '📝', badge: '4' }
    ],
    sections: [
      {
        tab: 'package',
        title: 'Remuneration Offer',
        note: 'Monthly gross compensation offered to candidate.',
        fields: [
          { name: 'candidate_id', required: true, label: 'Candidate' },
          { name: 'requisition_id', label: 'Job Requisition', readonly: true },
          { name: 'position_id', label: 'Offered Position' },
          { name: 'gross_salary', label: 'Gross Monthly Salary (BDT)' },
          { name: 'basic_salary', label: 'Basic Monthly Salary (BDT)' },
          { name: 'contract_type', label: 'Contract Type' },
          { name: 'probation_class', label: 'Probation Class (BLA s.4(8))' },
          { name: 'probation_months', label: 'Probation (months)' },
          { name: 'benefits', type: 'text', label: 'Benefits' },
          { name: 'band_id', label: 'M57 Pay Band', readonly: true },
          { name: 'in_band', label: 'Within Band', readonly: true }
        ]
      },
      {
        tab: 'terms',
        title: 'Offer Timeline & Acceptance',
        note: 'Validity dates and formal candidate acceptance status.',
        fields: [
          { name: 'issued_on', label: 'Offer Issued Date', readonly: true },
          { name: 'valid_until', label: 'Offer Valid Until' },
          { name: 'joining_date', label: 'Expected Date of Joining' },
          { name: 'state', label: 'Offer Acceptance State', readonly: true },
          { name: 'approval_state', label: 'Approval', readonly: true },
          { name: 'approved_by_id', label: 'Approved By', readonly: true },
          { name: 'acceptance_ref', label: 'Candidate Acceptance Reference' },
          { name: 'acceptance_file', type: 'binary', label: 'Signed Acceptance (candidate)' },
          { name: 'responded_on', label: 'Candidate Responded On', readonly: true }
        ]
      }
    ]
  },

  'M58-form-onboarding': {
    kind: 'model_form',
    model: 'fix.onboarding.plan',
    title: 'Onboarding Plan',
    back: 'M58-preboard',
    create: false, pick: 'An onboarding plan opens when an accepted offer completes the hire: open one from Pre-Boarding.',
    status: { field: 'state', labels: {
      draft: 'Draft', in_progress: 'In Progress', completed: 'Completed' } },
    tabs: [
      { id: 'placement', label: 'Placement & Org', bn: 'নিয়োগ ও অবস্থান', icon: '🏢', badge: '6' },
      { id: 'statutory', label: 'Compliance Gates', bn: 'আইনগত শর্তপূরণ', icon: '⚖️', badge: '3' },
      { id: 'provisioning', label: 'IT & Kit Allocation', bn: 'আইটি ও সরঞ্জাম', icon: '🔑', badge: '4' }
    ],
    sections: [
      {
        tab: 'placement',
        title: 'Candidate Placement Particulars',
        note: 'Transition from candidate to verified active employee.',
        fields: [
          { name: 'name', required: true, label: 'Plan Reference' },
          { name: 'candidate_id', label: 'Candidate' },
          { name: 'employee_id', label: 'Created Employee Record', readonly: true },
          { name: 'position_id', label: 'Establishment Position' },
          { name: 'department_id', label: 'Department' },
          { name: 'joined_date', label: 'Date of Joining' },
          { name: 'mentor_id', label: 'Mentor / Buddy (FR-TAO-031)' }
        ]
      },
      {
        tab: 'statutory',
        title: 'Statutory Verification Gates',
        note: 'Mandatory statutory onboarding verifications.',
        fields: [
          { name: 'nid_verified', label: 'National ID (NID) Verified', readonly: true },
          { name: 'documents_required', label: 'Mandatory Pre-Boarding Documents', readonly: true },
          { name: 'documents_verified', label: 'Of Which Verified', readonly: true },
          { name: 'appointment_letter_id', label: 'Generated Appointment Letter (M24)', readonly: true },
          { name: 'signed_contract_file', type: 'binary', label: 'Employee-Signed Appointment Letter' },
          { name: 'appointment_ack_method', label: 'Acknowledged By', readonly: true },
          { name: 'appointment_ack_attested_by_id', label: 'Signature Attested By', readonly: true },
          { name: 'contract_signed', label: 'Appointment Letter Acknowledged', readonly: true },
          { name: 'bank_details_captured', label: 'Bank / MFS Wallet Captured', readonly: true },
          { name: 'contract_id', label: 'Draft Employment Contract', readonly: true },
          { name: 'open_mandatory_tasks', label: 'Mandatory Tasks Still Open', readonly: true }
        ]
      },
      {
        tab: 'provisioning',
        title: 'IT Assets & Safety Equipment Handover',
        note: 'Equipment and identity provisioning tracking.',
        fields: [
          { name: 'it_assets_allocated', label: 'Mobile Device / Laptop Issued' },
          { name: 'keycloak_provisioned', label: 'Single Sign-On (IdP) Provisioned', readonly: true },
          { name: 'safety_kit_issued', label: 'Standard PPE Kit Issued', readonly: true },
          { name: 'state', label: 'Onboarding Plan State', readonly: true }
        ]
      }
    ]
  },

  'M58-form-assessment': {
    kind: 'model_form',
    model: 'fix.talent.assessment',
    title: 'Practical Bench Assessment',
    back: 'M58-talent-assessment',
    tabs: [
      { id: 'candidate', label: 'Candidate & Competency', bn: 'প্রার্থী ও দক্ষতা', icon: '👤', badge: '4' },
      { id: 'evaluation', label: 'Bench Score & Outcome', bn: 'ব্যবহারিক স্কোর ও ফলাফল', icon: '🔬', badge: '4' }
    ],
    sections: [
      {
        tab: 'candidate',
        title: 'Candidate & Practical Competency Scope',
        note: 'Hands-on micro-soldering, diagnostic, or HVAC practical bench test.',
        fields: [
          { name: 'candidate_id', required: true, label: 'Candidate' },
          { name: 'requisition_id', label: 'Job Requisition', readonly: true },
          { name: 'competency_id', label: 'M22 Competency Tested (becomes the baseline)' },
          { name: 'competency_code', label: 'Tested Competency Code', readonly: true },
          { name: 'level', label: 'Observed Level' },
          { name: 'assessor_id', label: 'Bench Technical Assessor' },
          { name: 'baseline_id', label: 'M22 Baseline Assessment', readonly: true }
        ]
      },
      {
        tab: 'evaluation',
        title: 'Practical Test Score & Hiring Gate',
        note: 'A failed practical assessment blocks candidate hire under RAP-M58-05.',
        fields: [
          { name: 'assessed_on', required: true, label: 'Assessment Date' },
          { name: 'score', label: 'Practical Score (0-100)' },
          { name: 'pass_mark', label: 'Approved Pass Mark (%)', readonly: true },
          { name: 'passed', label: 'Passed Bench Assessment', readonly: true },
          { name: 'tasks_performed', type: 'text', label: 'Tasks Performed (FR-TAO-016)' },
          { name: 'evidence_file', type: 'binary', label: 'Assessment Evidence (photos, job card)' },
          { name: 'notes', type: 'text', label: 'Assessor Observations' }
        ]
      }
    ]
  },

  'M58-form-check': {
    kind: 'model_form',
    model: 'fix.talent.check',
    title: 'Reference & Background Check',
    back: 'M58-checks',
    status: { field: 'result', labels: {
      pending: 'Pending', clear: 'Clear', discrepancy: 'Discrepancy', failed: 'Failed' } },
    tabs: [
      { id: 'check', label: 'Verification Request', bn: 'যাচাইয়ের বিবরণ', icon: '🔍', badge: '4' },
      { id: 'outcome', label: 'Clearance & Notes', bn: 'ফলাফল ও মন্তব্য', icon: '✅', badge: '3' }
    ],
    sections: [
      {
        tab: 'check',
        title: 'Pre-Employment Background & PCC Verification',
        note: 'Reference, NID, Police Clearance (PCC), and academic verification.',
        fields: [
          { name: 'candidate_id', required: true, label: 'Candidate' },
          { name: 'check_type', required: true, label: 'Verification Type' },
          { name: 'requested_on', required: true, label: 'Requested Date' },
          { name: 'reference_contact', label: 'Referee / Issuing Authority Contact' },
          { name: 'company_id', label: 'Company' }
        ]
      },
      {
        tab: 'outcome',
        title: 'Verification Outcome & Hire Gate',
        note: 'Discrepancy or failed background check blocks candidate hire.',
        fields: [
          { name: 'completed_on', label: 'Completed Date', readonly: true },
          { name: 'result', label: 'Verification Result', readonly: true },
          { name: 'evidence_file', type: 'binary', label: 'Verification Evidence' },
          { name: 'verified_by_id', label: 'Verified By', readonly: true },
          { name: 'approval_state', label: 'Verification Request', readonly: true },
          { name: 'notes', type: 'text', label: 'Verification Remarks & Reference Notes' }
        ]
      }
    ]
  },

  'M58-form-evaluation': {
    kind: 'model_form',
    model: 'fix.talent.evaluation',
    title: 'My Panel Evaluation',
    back: 'M58-evaluations',
    create: false, pick: 'An evaluation opens when you are named on an interview panel: open yours from My Panel Evaluations.',
    status: { field: 'state', labels: { draft: 'Not Submitted', submitted: 'Submitted' } },
    tabs: [
      { id: 'round', label: 'Interview Round', bn: 'সাক্ষাৎকার', icon: '🗓️', badge: '4' },
      { id: 'evaluation', label: 'My Evaluation', bn: 'আমার মূল্যায়ন', icon: '✍️', badge: '3' }
    ],
    sections: [
      {
        tab: 'round',
        title: 'Round',
        note: 'You see only your own evaluation; nobody sees it before the whole panel has submitted.',
        fields: [
          { name: 'candidate_name', label: 'Candidate', readonly: true },
          { name: 'round_no', label: 'Round', readonly: true },
          { name: 'scheduled_on', label: 'Scheduled', readonly: true },
          { name: 'panelist_id', label: 'Panelist', readonly: true }
        ]
      },
      {
        tab: 'evaluation',
        title: 'Independent Evaluation (BRU-TAO-07)',
        note: 'Final once submitted.',
        fields: [
          { name: 'score', label: 'Score (1-5)' },
          { name: 'recommendation', label: 'Recommendation' },
          { name: 'notes', type: 'text', label: 'Evaluation Notes' },
          { name: 'submitted_on', label: 'Submitted On', readonly: true },
          { name: 'state', label: 'State', readonly: true }
        ]
      }
    ]
  },

  'M58-form-budget': {
    kind: 'model_form',
    model: 'fix.headcount.budget',
    title: 'Headcount Budget',
    back: 'M58-budget',
    status: { field: 'state', labels: { draft: 'Draft', approved: 'Approved', closed: 'Closed' } },
    tabs: [
      { id: 'scope', label: 'Scope & Figure', bn: 'পরিধি ও সংখ্যা', icon: '📊', badge: '5' },
      { id: 'workflow', label: 'Approval', bn: 'অনুমোদন', icon: '⚙️', badge: '4' }
    ],
    sections: [
      {
        tab: 'scope',
        title: 'Approved Headcount per Position or Department and Year',
        note: 'One position or one department per budget. In post plus open requisitions may not exceed it without the CFO tier.',
        fields: [
          { name: 'year', required: true, label: 'Year' },
          { name: 'position_id', label: 'Position' },
          { name: 'department_id', label: 'Department' },
          { name: 'approved_headcount', required: true, label: 'Budgeted Headcount' },
          { name: 'basis', type: 'text', label: 'Budget Basis (M54 plan)' }
        ]
      },
      {
        tab: 'workflow',
        title: 'Approval (CFO tier)',
        note: 'Approved from the M63 inbox by someone other than its requester.',
        fields: [
          { name: 'used_headcount', label: 'In Post + Open', readonly: true },
          { name: 'approval_state', label: 'Approval', readonly: true },
          { name: 'approved_by_id', label: 'Approved By', readonly: true },
          { name: 'state', label: 'State', readonly: true }
        ]
      }
    ]
  },

  'M58-form-task': {
    kind: 'model_form',
    model: 'fix.onboarding.task',
    title: 'Onboarding Task',
    back: 'M58-onboarding-tasks',
    status: { field: 'state', labels: { open: 'Open', done: 'Done', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'task', label: 'Task & Owner', bn: 'কাজ ও দায়িত্ব', icon: '📋', badge: '5' },
      { id: 'evidence', label: 'Completion Evidence', bn: 'সম্পাদনের প্রমাণ', icon: '✅', badge: '4' }
    ],
    sections: [
      {
        tab: 'task',
        title: 'Task (FR-TAO-027)',
        note: 'Generated from the onboarding template at hire; a task added here is optional. A mandatory task is never cancelled.',
        fields: [
          { name: 'plan_id', required: true, label: 'Onboarding Plan' },
          { name: 'name', required: true, label: 'Task' },
          { name: 'function', label: 'Function' },
          { name: 'owner_id', required: true, label: 'Owner' },
          { name: 'due_date', required: true, label: 'Due Date' },
          { name: 'depends_on_id', label: 'Depends On (done first)' },
          { name: 'mandatory', label: 'Mandatory', readonly: true }
        ]
      },
      {
        tab: 'evidence',
        title: 'Evidence (the owner completes the task)',
        note: 'What was done, with the file where the task asks for one.',
        fields: [
          { name: 'evidence_note', type: 'text', label: 'Completion Evidence' },
          { name: 'evidence_file', type: 'binary', label: 'Evidence File' },
          { name: 'completed_by_id', label: 'Completed By', readonly: true },
          { name: 'completed_on', label: 'Completed On', readonly: true },
          { name: 'state', label: 'State', readonly: true }
        ]
      }
    ]
  },

  'M58-form-first90': {
    kind: 'model_form',
    model: 'fix.talent.first90',
    title: 'First-90-Days Probation Review',
    back: 'M58-first90',
    tabs: [
      { id: 'review', label: 'Employee & Milestone', bn: 'কর্মী ও মাইলফলক', icon: '📅', badge: '4' },
      { id: 'outcome', label: 'Rating & Retention', bn: 'রেটিং ও মূল্যায়ন', icon: '⭐', badge: '3' }
    ],
    sections: [
      {
        tab: 'review',
        title: 'New Hire Probation Checkpoint (30 / 60 / 90 Days)',
        note: 'Structured post-onboarding milestone review.',
        fields: [
          { name: 'employee_id', required: true, label: 'New Hire Employee' },
          { name: 'plan_id', label: 'Onboarding Plan' },
          { name: 'milestone', required: true, label: 'Checkpoint Milestone (30d / 60d / 90d)' },
          { name: 'check_date', required: true, label: 'Review Date' },
          { name: 'reviewer_id', label: 'Reviewing Supervisor' }
        ]
      },
      {
        tab: 'outcome',
        title: 'Performance Rating & Retention Status',
        note: 'Feeds the M58 First-90 Retention KPI.',
        fields: [
          { name: 'rating', label: 'Checkpoint Rating (1-5)' },
          { name: 'on_track', label: 'On Track for Confirmation' },
          { name: 'notes', type: 'text', label: 'Coaching & Probation Notes' }
        ]
      }
    ]
  },

  /* ============ CAPTURE AUDIT 2026-11-17: records the pages cover ============ */
  'M58-form-job-profile': {
    kind: 'model_form',
    model: 'fix.job.profile',
    title: 'Job Profile',
    back: 'M58-job-profiles',
    tabs: [
      { id: 'role', label: 'Role', bn: 'পদ', icon: '📋', badge: '5' },
      { id: 'requirements', label: 'Requirements', bn: 'যোগ্যতা', icon: '🎓', badge: '3' }
    ],
    sections: [
      {
        tab: 'role',
        title: 'Role Definition (FR-TAO-004)',
        note: 'Named on a requisition; the position itself stays in M21.',
        fields: [
          { name: 'name', required: true, label: 'Profile Name' },
          { name: 'position_id', label: 'Position (M21)' },
          { name: 'band_id', label: 'Pay Band (M57)' },
          { name: 'responsibilities', type: 'text', required: true, label: 'Responsibilities' },
          { name: 'active', label: 'Active' }
        ]
      },
      {
        tab: 'requirements',
        title: 'Competencies, Qualifications and Experience',
        note: 'Competencies come from the M22 framework.',
        fields: [
          { name: 'competency_ids', label: 'Required Competencies (M22)' },
          { name: 'qualifications', type: 'text', label: 'Qualifications' },
          { name: 'min_experience_years', label: 'Minimum Experience (years)' }
        ]
      }
    ]
  },

  'M58-form-posting': {
    kind: 'model_form',
    model: 'fix.job.posting',
    title: 'Job Posting',
    back: 'M58-postings',
    status: { field: 'state', labels: { draft: 'Draft', published: 'Published', closed: 'Closed' } },
    tabs: [
      { id: 'opening', label: 'Opening', bn: 'বিজ্ঞপ্তি', icon: '📣', badge: '6' },
      { id: 'publication', label: 'Publication', bn: 'প্রকাশ', icon: '📅', badge: '4' }
    ],
    sections: [
      {
        tab: 'opening',
        title: 'What Is Posted (FR-TAO-005)',
        note: 'Published only for an open, approved requisition (BRU-TAO-02). External postings name their channel.',
        fields: [
          { name: 'title', required: true, label: 'Posting Title' },
          { name: 'requisition_id', required: true, label: 'Requisition' },
          { name: 'audience', required: true, label: 'Audience' },
          { name: 'channel_id', label: 'Channel (external)' },
          { name: 'closes_on', label: 'Applications Close' },
          { name: 'description', type: 'text', label: 'Posting Text' }
        ]
      },
      {
        tab: 'publication',
        title: 'Internal Consideration First (FR-TAO-006)',
        note: 'An internal posting holds external posting of the opening for the configured window.',
        fields: [
          { name: 'published_on', label: 'Published On', readonly: true },
          { name: 'internal_only_until', label: 'Internal Only Until', readonly: true },
          { name: 'candidate_count', label: 'Applicants', readonly: true },
          { name: 'state', label: 'State', readonly: true }
        ]
      }
    ]
  },

  'M58-form-referral': {
    kind: 'model_form',
    model: 'fix.talent.referral',
    title: 'Employee Referral',
    back: 'M58-referrals',
    status: { field: 'reward_state', labels: { open: 'Open', approved: 'Reward Approved', declined: 'No Reward' } },
    tabs: [
      { id: 'referral', label: 'Referral', bn: 'রেফারেল', icon: '🤝', badge: '3' },
      { id: 'reward', label: 'Reward', bn: 'পুরস্কার', icon: '🎁', badge: '5' }
    ],
    sections: [
      {
        tab: 'referral',
        title: 'Who Referred Whom (FR-TAO-007)',
        note: 'One referral per candidate; nobody refers themself.',
        fields: [
          { name: 'candidate_id', required: true, label: 'Candidate' },
          { name: 'referring_employee_id', required: true, label: 'Referred By' },
          { name: 'relationship', label: 'Relationship to Candidate' }
        ]
      },
      {
        tab: 'reward',
        title: 'Reward Decision (AUT-TAO-17)',
        note: 'Approved after the hire by an HR manager who neither recorded nor made the referral; paid through payroll.',
        fields: [
          { name: 'reward_amount', label: 'Referral Reward' },
          { name: 'candidate_state', label: 'Candidate Outcome', readonly: true },
          { name: 'reward_state', label: 'Reward', readonly: true },
          { name: 'decided_by_id', label: 'Decided By', readonly: true },
          { name: 'decision_note', label: 'Decision Note', readonly: true }
        ]
      }
    ]
  },

  'M58-form-channel': {
    kind: 'model_form',
    model: 'fix.recruitment.channel',
    title: 'Recruitment Channel',
    back: 'M58-channels',
    sections: [
      {
        title: 'Channel or Agency (FR-TAO-008)',
        note: 'A charging channel records its agreed fee; an agency names the agency.',
        fields: [
          { name: 'name', required: true, label: 'Channel Name' },
          { name: 'channel_type', required: true, label: 'Type' },
          { name: 'partner_id', label: 'Agency / Provider' },
          { name: 'cost_model', required: true, label: 'Cost Model' },
          { name: 'fee', label: 'Agreed Fee' },
          { name: 'contract_ref', label: 'Contract Reference' },
          { name: 'active', label: 'Active' }
        ]
      }
    ]
  },

  'M58-form-cost': {
    kind: 'model_form',
    model: 'fix.recruitment.cost',
    title: 'Recruitment Cost',
    back: 'M58-costs',
    sections: [
      {
        title: 'Cost Incurred for a Requisition (FR-TAO-034)',
        note: 'Only on an approved requisition (BRU-TAO-02). Feeds Cost per Hire; Finance pays the bill in M20.',
        fields: [
          { name: 'requisition_id', required: true, label: 'Requisition' },
          { name: 'cost_type', required: true, label: 'Cost Type' },
          { name: 'channel_id', label: 'Channel / Agency' },
          { name: 'amount', required: true, label: 'Amount' },
          { name: 'incurred_on', required: true, label: 'Incurred On' },
          { name: 'invoice_ref', label: 'Invoice / Bill Reference' },
          { name: 'notes', type: 'text', label: 'Notes' }
        ]
      }
    ]
  },

  'M58-form-document': {
    kind: 'model_form',
    model: 'fix.preboarding.document',
    title: 'Pre-Boarding Document',
    back: 'M58-preboard-docs',
    status: { field: 'state', labels: { requested: 'Requested', submitted: 'Submitted', verified: 'Verified', rejected: 'Rejected' } },
    tabs: [
      { id: 'document', label: 'Document', bn: 'কাগজপত্র', icon: '📄', badge: '5' },
      { id: 'verification', label: 'Verification', bn: 'যাচাই', icon: '✅', badge: '6' }
    ],
    sections: [
      {
        tab: 'document',
        title: 'Collected Document (FR-TAO-023)',
        note: 'The hire issues the checklist; Recruitment uploads what the new hire hands in.',
        fields: [
          { name: 'plan_id', required: true, label: 'Onboarding Plan' },
          { name: 'document_type', required: true, label: 'Document Type' },
          { name: 'document_file', type: 'binary', label: 'Document' },
          { name: 'mandatory', label: 'Mandatory', readonly: true },
          { name: 'notes', type: 'text', label: 'Notes' }
        ]
      },
      {
        tab: 'verification',
        title: 'Verification (FR-TAO-024, T-08)',
        note: 'A Background Verifier who did not upload it verifies or rejects it; its fingerprint is kept.',
        fields: [
          { name: 'submitted_on', label: 'Submitted On', readonly: true },
          { name: 'uploaded_by_id', label: 'Uploaded By', readonly: true },
          { name: 'file_sha256', label: 'SHA-256', readonly: true },
          { name: 'verified_by_id', label: 'Verified By', readonly: true },
          { name: 'verified_on', label: 'Verified On', readonly: true },
          { name: 'rejection_reason', label: 'Rejected Because', readonly: true }
        ]
      }
    ]
  },

  'M58-form-induction': {
    kind: 'model_form',
    model: 'fix.onboarding.induction',
    title: 'Induction Session',
    back: 'M58-inductions',
    status: { field: 'state', labels: { scheduled: 'Scheduled', attended: 'Attended', missed: 'Missed', cancelled: 'Cancelled' } },
    sections: [
      {
        title: 'Induction (FR-TAO-029)',
        note: 'The conductor records attendance after the session starts; an unrecorded session holds the onboarding open.',
        fields: [
          { name: 'plan_id', required: true, label: 'Onboarding Plan' },
          { name: 'session_type', required: true, label: 'Session' },
          { name: 'scheduled_at', required: true, label: 'Scheduled At' },
          { name: 'conductor_id', required: true, label: 'Conducted By' },
          { name: 'venue', label: 'Venue' },
          { name: 'recorded_by_id', label: 'Recorded By', readonly: true },
          { name: 'outcome_note', label: 'Outcome Note', readonly: true }
        ]
      }
    ]
  },

  'M58-form-template': {
    kind: 'model_form',
    model: 'fix.onboarding.template',
    title: 'Onboarding Template',
    back: 'M58-templates',
    sections: [
      {
        title: 'Task Set by Role (FR-TAO-027)',
        note: 'Named on a requisition; the default template applies when none is named. Its tasks are listed under Template Tasks.',
        fields: [
          { name: 'name', required: true, label: 'Template Name' },
          { name: 'is_default', label: 'Default Template' },
          { name: 'active', label: 'Active' }
        ]
      }
    ]
  },

  'M58-form-template-line': {
    kind: 'model_form',
    model: 'fix.onboarding.template.line',
    title: 'Template Task',
    back: 'M58-template-lines',
    sections: [
      {
        title: 'Task Generated at Hire (FR-TAO-027)',
        note: 'Owner, due date (days from joining) and whether evidence is needed.',
        fields: [
          { name: 'template_id', required: true, label: 'Template' },
          { name: 'sequence', label: 'Order' },
          { name: 'name', required: true, label: 'Task' },
          { name: 'function', required: true, label: 'Function' },
          { name: 'owner_user_id', label: 'Owner' },
          { name: 'due_offset_days', label: 'Due (days from joining)' },
          { name: 'mandatory', label: 'Mandatory' },
          { name: 'evidence_required', label: 'Evidence File Required' },
          { name: 'field_role_only', label: 'Field Roles Only' }
        ]
      }
    ]
  }
};

export const REPORT_ROUTES = {
  'M58:Funnel & Conversion': 'M58-rpt-funnel',
  'M58:Time-to-Fill by Role': 'M58-rpt-ttf',
  'M58:Source Effectiveness': 'M58-rpt-source',
  'M58:First-90 Retention': 'M58-rpt-retention',
  'M58:Practical Assessment Results': 'M58-rpt-practical',
  'M58:Cost per Hire': 'M58-rpt-cost',
  'M58:Day-One Readiness': 'M58-rpt-readiness'
};

export const FORM_MODELS = {
  'M58:Requisition': 'fix.job.requisition',
  'M58:Candidate': 'fix.candidate',
  'M58:Interview Round': 'fix.talent.interview',
  'M58:Offer': 'fix.talent.offer',
  'M58:Headcount Budget': 'fix.headcount.budget',
  'M58:Job Profile': 'fix.job.profile',
  'M58:Job Posting': 'fix.job.posting',
  'M58:Referral': 'fix.talent.referral',
  'M58:Recruitment Channel': 'fix.recruitment.channel',
  'M58:Recruitment Cost': 'fix.recruitment.cost',
  'M58:Practical Assessment': 'fix.talent.assessment',
  'M58:Background Check': 'fix.talent.check',
  'M58:Pre-Boarding Document': 'fix.preboarding.document',
  'M58:Onboarding Task': 'fix.onboarding.task',
  'M58:Induction Session': 'fix.onboarding.induction',
  'M58:Onboarding Template': 'fix.onboarding.template',
  'M58:Template Task': 'fix.onboarding.template.line',
  'M58:First-90 Review': 'fix.talent.first90'
};

export const FORM_CHIPS = {
  'M58:Requisition': 'M58-form-req',
  'M58:Candidate': 'M58-form-candidate',
  'M58:Interview Round': 'M58-form-interview',
  'M58:Offer': 'M58-form-offer',
  'M58:Headcount Budget': 'M58-form-budget',
  'M58:Job Profile': 'M58-form-job-profile',
  'M58:Job Posting': 'M58-form-posting',
  'M58:Referral': 'M58-form-referral',
  'M58:Recruitment Channel': 'M58-form-channel',
  'M58:Recruitment Cost': 'M58-form-cost',
  'M58:Practical Assessment': 'M58-form-assessment',
  'M58:Background Check': 'M58-form-check',
  'M58:Pre-Boarding Document': 'M58-form-document',
  'M58:Onboarding Task': 'M58-form-task',
  'M58:Induction Session': 'M58-form-induction',
  'M58:Onboarding Template': 'M58-form-template',
  'M58:Template Task': 'M58-form-template-line',
  'M58:First-90 Review': 'M58-form-first90',
  'M58:__by_model__': {
    'fix.job.requisition': 'M58-form-req',
    'fix.candidate': 'M58-form-candidate',
    'fix.talent.interview': 'M58-form-interview',
    'fix.talent.assessment': 'M58-form-assessment',
    'fix.talent.check': 'M58-form-check',
    'fix.talent.offer': 'M58-form-offer',
    'fix.onboarding.plan': 'M58-form-onboarding',
    'fix.talent.first90': 'M58-form-first90',
    'fix.talent.evaluation': 'M58-form-evaluation',
    'fix.headcount.budget': 'M58-form-budget',
    'fix.onboarding.task': 'M58-form-task',
    'fix.job.profile': 'M58-form-job-profile',
    'fix.job.posting': 'M58-form-posting',
    'fix.talent.referral': 'M58-form-referral',
    'fix.recruitment.channel': 'M58-form-channel',
    'fix.recruitment.cost': 'M58-form-cost',
    'fix.preboarding.document': 'M58-form-document',
    'fix.onboarding.induction': 'M58-form-induction',
    'fix.onboarding.template': 'M58-form-template',
    'fix.onboarding.template.line': 'M58-form-template-line'
  },
  'M58:__by_screen__': {
    'M58-talent-assessment': 'M58-form-assessment',
    'M58-reqs': 'M58-form-req',
    'M58-approval': 'M58-form-req',
    'M58-postings': 'M58-form-posting',
    'M58-candidates': 'M58-form-candidate',
    'M58-interviews': 'M58-form-interview',
    'M58-checks': 'M58-form-check',
    'M58-offers': 'M58-form-offer',
    'M58-preboard': 'M58-form-onboarding',
    'M58-first90': 'M58-form-first90',
    'M58-evaluations': 'M58-form-evaluation',
    'M58-budget': 'M58-form-budget',
    'M58-onboarding-tasks': 'M58-form-task',
    'M58-job-profiles': 'M58-form-job-profile',
    'M58-referrals': 'M58-form-referral',
    'M58-channels': 'M58-form-channel',
    'M58-costs': 'M58-form-cost',
    'M58-preboard-docs': 'M58-form-document',
    'M58-inductions': 'M58-form-induction',
    'M58-templates': 'M58-form-template',
    'M58-template-lines': 'M58-form-template-line'
  }
};

export const CREATE = {
  M58: { screen: 'M58-form-req', model: 'fix.job.requisition', label: 'Requisition' }
};
