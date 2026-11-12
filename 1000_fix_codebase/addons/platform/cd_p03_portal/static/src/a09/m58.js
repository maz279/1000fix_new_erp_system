/** @odoo-module **/
/* A09 · People & Workforce — M58 Talent Acquisition.
 * Registry-faithful: 4 groups / 10 screens / 5 reports / 4 forms / freg 50. */

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
      { id: 'M58-budget', en: 'Headcount Budget', bn: 'জনবল বাজেট', t: 'g' }
    ]},
    { en: 'Sourcing', screens: [
      { id: 'M58-postings', en: 'Job Postings', bn: 'চাকরির বিজ্ঞপ্তি', t: 'g' },
      { id: 'M58-candidates', en: 'Candidate Pipeline', bn: 'প্রার্থী', t: 'g' }
    ]},
    { en: 'Selection', screens: [
      { id: 'M58-interviews', en: 'Structured Interviews', bn: 'সাক্ষাৎকার', t: 'g' },
      { id: 'M58-evaluations', en: 'My Panel Evaluations', bn: 'আমার মূল্যায়ন', t: 'g' },
      { id: 'M58-practical', en: 'Practical Assessments', bn: 'ব্যবহারিক মূল্যায়ন', t: 'r' },
      { id: 'M58-checks', en: 'Reference & Background', bn: 'রেফারেন্স', t: 'g' },
      { id: 'M58-offers', en: 'Offers', bn: 'প্রস্তাব', t: 'g' }
    ]},
    { en: 'Onboarding', screens: [
      { id: 'M58-preboard', en: 'Pre-Boarding', bn: 'প্রি-বোর্ডিং', t: 'g' },
      { id: 'M58-onboarding-tasks', en: 'Onboarding Tasks', bn: 'অনবোর্ডিং কাজ', t: 'g' },
      { id: 'M58-first90', en: 'First-90-Days', bn: 'প্রথম ৯০ দিন', t: 'g' }
    ]}
  ],
  reports: ['Funnel & Conversion', 'Time-to-Fill by Role', 'Source Effectiveness', 'First-90 Retention', 'Practical Assessment Results'],
  forms: ['Requisition', 'Candidate', 'Interview Evaluation', 'Offer'],
  cross: ['M21 Workforce', 'M22 Competency', 'M54 Budgeting'],
  freg: { src: 50, sub: [
    ['1', 'Workforce Planning & Requisition', 9, { model: 'fix.job.requisition', cols: ['name', 'department_id', 'position_id', 'openings', 'state'], screens: ['M58-reqs', 'M58-approval'], reports: ['Time-to-Fill by Role'], forms: ['Requisition'] }],
    ['2', 'Sourcing', 7, { model: 'fix.candidate', cols: ['name', 'requisition_id', 'operating_unit_id', 'state'], screens: ['M58-postings', 'M58-candidates'], reports: ['Source Effectiveness', 'Funnel & Conversion'], forms: ['Candidate'] }],
    ['3', 'Screening', 6, { model: 'fix.candidate', cols: ['name', 'requisition_id', 'state', 'create_date'], screens: ['M58-candidates'], reports: ['Funnel & Conversion'], forms: [], create: false, domain: [['state', 'in', ['applied', 'screening']]] }],
    ['4', 'Interviews & Assessments', 11, { model: 'fix.talent.interview', cols: ['name', 'candidate_id', 'scheduled_on', 'score', 'recommendation'], screens: ['M58-interviews', 'M58-practical', 'M58-talent-assessment'], reports: ['Practical Assessment Results'], forms: ['Interview Evaluation'] }],
    ['5', 'Checks & Offers', 7, { model: 'fix.talent.offer', cols: ['name', 'candidate_id', 'position_id', 'joining_date', 'state'], screens: ['M58-checks', 'M58-offers'], reports: ['Funnel & Conversion'], forms: ['Offer'] }],
    ['6', 'Pre-Boarding', 4, { model: 'fix.onboarding.plan', cols: ['name', 'candidate_id', 'joined_date', 'contract_signed', 'state'], screens: ['M58-preboard'], reports: [], forms: [] }],
    ['7', 'Onboarding Orchestration', 6, { model: 'fix.talent.first90', cols: ['name', 'employee_id', 'milestone', 'check_date', 'on_track'], screens: ['M58-first90'], reports: ['First-90 Retention'], forms: [] }]
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
  'M58-postings': { kind: 'model_list', model: 'fix.job.requisition', stateField: 'state',
    cols: ['name', 'department_id', 'openings', 'state'] },
  'M58-candidates': { kind: 'model_list', model: 'fix.candidate', stateField: 'state',
    cols: ['name', 'email', 'phone', 'requisition_id', 'employee_id', 'operating_unit_id', 'state'],
    actions: [
      { m: 'action_screen', l: 'Screen' },
      { m: 'action_interview', l: 'Invite to Interview' },
      { m: 'action_offer', l: 'Move to Offer Stage' },
      { m: 'action_reject', l: 'Reject', ask: 'Outcome communicated to the candidate', kwarg: 'reason' },
      { m: 'action_hire', l: 'Hire (accepted offer)' }
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
    cols: ['name', 'candidate_id', 'requisition_id', 'employee_id', 'joined_date', 'nid_verified', 'contract_signed', 'bank_details_captured', 'safety_kit_issued', 'open_mandatory_tasks', 'state'],
    /* Round 2 (M24, BLA s.5): the appointment letter is generated at hire and
     * acknowledged by the employee (in person, or their signed copy attested
     * by a verifier who did not upload it); every mandatory task is done. */
    actions: [
      { m: 'action_start', l: 'Start Onboarding' },
      { m: 'action_acknowledge_appointment', l: 'Acknowledge My Appointment Letter' },
      { m: 'action_attest_signed_appointment', l: 'Attest Signed Appointment Letter' },
      { m: 'action_complete', l: 'Complete (Provision Identity)' }
    ] },
  'M58-onboarding-tasks': { kind: 'model_list', model: 'fix.onboarding.task', stateField: 'state',
    cols: ['name', 'plan_id', 'function', 'owner_id', 'due_date', 'mandatory', 'overdue', 'completed_by_id', 'state'],
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

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M58-form-req': {
    kind: 'model_form',
    model: 'fix.job.requisition',
    title: 'Job Requisition',
    back: 'M58-reqs',
    status: { field: 'state', labels: {
      draft: 'Draft', open: 'Open', hired: 'Filled', closed: 'Closed' } },
    tabs: [
      { id: 'scope', label: 'Requisition Scope', bn: 'নিয়োগের চাহিদা', icon: '📋', badge: '5' },
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

  'M58-form-candidate': {
    kind: 'model_form',
    model: 'fix.candidate',
    title: 'Candidate Biodata',
    back: 'M58-candidates',
    status: { field: 'state', labels: {
      applied: 'Applied', screening: 'Screening', interview: 'Interview',
      offered: 'Offered', hired: 'Hired', rejected: 'Rejected' } },
    tabs: [
      { id: 'biodata', label: 'Candidate Profile', bn: 'প্রার্থীর তথ্য', icon: '👤', badge: '4' },
      { id: 'pipeline', label: 'Recruitment Stage', bn: 'নিয়োগ পর্যায়', icon: '📊', badge: '2' }
    ],
    sections: [
      {
        tab: 'biodata',
        title: 'Personal Biodata & Contact',
        note: 'Candidate contact details and target recruitment branch.',
        fields: [
          { name: 'name', required: true, label: 'Candidate Full Name' },
          { name: 'email', label: 'Contact Email' },
          { name: 'phone', label: 'Contact Mobile Phone' },
          { name: 'operating_unit_id', label: 'Target Operating Unit' },
          { name: 'source', label: 'Source / Channel' },
          { name: 'date_of_birth', label: 'Date of Birth (verified)' },
          { name: 'nid_number', label: 'NID Number (10 / 13 / 17 digits)' },
          { name: 'consent_given', label: 'Consent to Processing & Retention' },
          { name: 'consent_date', label: 'Consent Recorded On', readonly: true },
          { name: 'retention_until', label: 'Retain Until', readonly: true }
        ]
      },
      {
        tab: 'pipeline',
        title: 'Hiring Funnel & Requisition Mapping',
        note: 'Pipeline progression from application to hire and linked M21 employee master.',
        fields: [
          { name: 'requisition_id', label: 'Linked Job Requisition' },
          { name: 'employee_id', label: 'Created M21 Employee Record', readonly: true },
          { name: 'state', label: 'Recruitment Stage', readonly: true },
          { name: 'rejection_reason', type: 'text', label: 'Outcome Communicated', readonly: true }
        ]
      }
    ]
  },

  'M58-form-interview': {
    kind: 'model_form',
    model: 'fix.talent.interview',
    title: 'Interview Evaluation',
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
      { id: 'package', label: 'Compensation Package', bn: 'বেতন প্যাকেজ', icon: '💵', badge: '4' },
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
          { name: 'joined_date', label: 'Date of Joining' }
        ]
      },
      {
        tab: 'statutory',
        title: 'Statutory Verification Gates',
        note: 'Mandatory statutory onboarding verifications.',
        fields: [
          { name: 'nid_verified', label: 'National ID (NID) Verified', readonly: true },
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
        note: 'Generated from the onboarding template at hire; a mandatory task is never cancelled.',
        fields: [
          { name: 'plan_id', label: 'Onboarding Plan', readonly: true },
          { name: 'name', required: true, label: 'Task' },
          { name: 'function', label: 'Function' },
          { name: 'owner_id', required: true, label: 'Owner' },
          { name: 'due_date', required: true, label: 'Due Date' },
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
  }
};

export const REPORT_ROUTES = {
  'M58:Funnel & Conversion': 'M58-rpt-funnel',
  'M58:Time-to-Fill by Role': 'M58-rpt-ttf',
  'M58:Source Effectiveness': 'M58-rpt-source',
  'M58:First-90 Retention': 'M58-rpt-retention',
  'M58:Practical Assessment Results': 'M58-rpt-practical'
};

export const FORM_MODELS = {
  'M58:Requisition': 'fix.job.requisition',
  'M58:Candidate': 'fix.candidate',
  'M58:Interview Evaluation': 'fix.talent.interview',
  'M58:Offer': 'fix.talent.offer'
};

export const FORM_CHIPS = {
  'M58:Requisition': 'M58-form-req',
  'M58:Candidate': 'M58-form-candidate',
  'M58:Interview Evaluation': 'M58-form-interview',
  'M58:Offer': 'M58-form-offer',
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
    'fix.onboarding.task': 'M58-form-task'
  },
  'M58:__by_screen__': {
    'M58-talent-assessment': 'M58-form-assessment',
    'M58-reqs': 'M58-form-req',
    'M58-approval': 'M58-form-req',
    'M58-postings': 'M58-form-req',
    'M58-candidates': 'M58-form-candidate',
    'M58-interviews': 'M58-form-interview',
    'M58-checks': 'M58-form-check',
    'M58-offers': 'M58-form-offer',
    'M58-preboard': 'M58-form-onboarding',
    'M58-first90': 'M58-form-first90',
    'M58-evaluations': 'M58-form-evaluation',
    'M58-budget': 'M58-form-budget',
    'M58-onboarding-tasks': 'M58-form-task'
  }
};

export const CREATE = {
  M58: { screen: 'M58-form-req', model: 'fix.job.requisition', label: 'Requisition' }
};
