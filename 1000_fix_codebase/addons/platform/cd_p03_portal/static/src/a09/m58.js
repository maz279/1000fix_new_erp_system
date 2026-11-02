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
      { id: 'M58-approval', en: 'Approval vs Budget', bn: 'বাজেট অনুমোদন', t: 'g' }
    ]},
    { en: 'Sourcing', screens: [
      { id: 'M58-postings', en: 'Job Postings', bn: 'চাকরির বিজ্ঞপ্তি', t: 'g' },
      { id: 'M58-candidates', en: 'Candidate Pipeline', bn: 'প্রার্থী', t: 'g' }
    ]},
    { en: 'Selection', screens: [
      { id: 'M58-interviews', en: 'Structured Interviews', bn: 'সাক্ষাৎকার', t: 'g' },
      { id: 'M58-practical', en: 'Practical Assessments', bn: 'ব্যবহারিক মূল্যায়ন', t: 'r' },
      { id: 'M58-checks', en: 'Reference & Background', bn: 'রেফারেন্স', t: 'g' },
      { id: 'M58-offers', en: 'Offers', bn: 'প্রস্তাব', t: 'g' }
    ]},
    { en: 'Onboarding', screens: [
      { id: 'M58-preboard', en: 'Pre-Boarding', bn: 'প্রি-বোর্ডিং', t: 'g' },
      { id: 'M58-first90', en: 'First-90-Days', bn: 'প্রথম ৯০ দিন', t: 'g' }
    ]}
  ],
  reports: ['Funnel & Conversion', 'Time-to-Fill by Role', 'Source Effectiveness', 'First-90 Retention', 'Practical Assessment Results'],
  forms: ['Requisition', 'Candidate', 'Interview Evaluation', 'Offer'],
  cross: ['M21 Workforce', 'M22 Competency', 'M54 Budgeting'],
  freg: { src: 50, sub: [
    ['1', 'Workforce Planning & Requisition', 9], ['2', 'Sourcing', 7], ['3', 'Screening', 6],
    ['4', 'Interviews & Assessments', 11], ['5', 'Checks & Offers', 7],
    ['6', 'Pre-Boarding', 4], ['7', 'Onboarding Orchestration', 6]
  ] }
};

export const SCREENS = {
  'M58-talent-assessment': { kind: 'model_list', model: 'fix.talent.assessment',
    cols: ['name', 'candidate_id', 'requisition_id', 'competency_code', 'assessed_on', 'score', 'passed', 'assessor_id'] },
  'M58-reqs': { kind: 'model_list', model: 'fix.job.requisition', stateField: 'state',
    cols: ['name', 'department_id', 'position_id', 'openings', 'operating_unit_id', 'state'],
    actions: [{ m: 'action_open', l: 'Approve Requisition' }, { m: 'action_hired', l: 'Mark Hired' }] },
  'M58-approval': { kind: 'model_list', model: 'fix.job.requisition', stateField: 'state',
    cols: ['name', 'position_id', 'openings', 'state'] },
  'M58-postings': { kind: 'model_list', model: 'fix.job.requisition', stateField: 'state',
    cols: ['name', 'department_id', 'openings', 'state'] },
  'M58-candidates': { kind: 'model_list', model: 'fix.candidate', stateField: 'state',
    cols: ['name', 'email', 'phone', 'requisition_id', 'employee_id', 'operating_unit_id', 'state'],
    actions: [{ m: 'action_screen', l: 'Screen' }, { m: 'action_interview', l: 'Invite to Interview' }, { m: 'action_offer', l: 'Generate Offer' }, { m: 'action_hire', l: 'Hire' }] },
  'M58-interviews': { kind: 'model_list', model: 'fix.talent.interview', stateField: 'state',
    cols: ['name', 'candidate_id', 'interviewer_id', 'scheduled_on', 'round_no', 'score', 'recommendation', 'state'],
    actions: [{ m: 'action_done', l: 'Complete Interview' }] },
  'M58-practical': { kind: 'table_report', module: 'M58', report: 'practical_results', title: 'Practical Assessment Results', period: true },
  'M58-checks': { kind: 'model_list', model: 'fix.talent.check', stateField: 'result',
    cols: ['name', 'candidate_id', 'check_type', 'requested_on', 'completed_on', 'result'],
    actions: [{ m: 'action_clear', l: 'Mark Clear' }] },
  'M58-offers': { kind: 'model_list', model: 'fix.talent.offer', stateField: 'state',
    cols: ['name', 'candidate_id', 'position_id', 'gross_salary', 'issued_on', 'joining_date', 'state'],
    actions: [{ m: 'action_issue', l: 'Issue Offer' }, { m: 'action_accept', l: 'Accept' },
              { m: 'action_decline', l: 'Decline' }] },
  'M58-preboard': { kind: 'model_list', model: 'fix.onboarding.plan',
    cols: ['name', 'candidate_id', 'requisition_id', 'employee_id', 'joined_date', 'nid_verified', 'contract_signed', 'it_assets_allocated'],
    actions: [{ m: 'action_start', l: 'Start Onboarding' }, { m: 'action_complete', l: 'Complete (Create Employee)' }] },
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
      draft: 'Draft', approved: 'Approved', active: 'Open', filled: 'Filled', cancelled: 'Cancelled' } },
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
          { name: 'operating_unit_id', label: 'Branch / Operating Unit' }
        ]
      },
      {
        tab: 'workflow',
        title: 'Requisition Lifecycle Status',
        note: 'Budget and department authorization.',
        fields: [
          { name: 'state', required: true, label: 'Requisition State' }
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
          { name: 'operating_unit_id', label: 'Target Operating Unit' }
        ]
      },
      {
        tab: 'pipeline',
        title: 'Hiring Funnel & Requisition Mapping',
        note: 'Pipeline progression from application to hire and linked M21 employee master.',
        fields: [
          { name: 'requisition_id', label: 'Linked Job Requisition' },
          { name: 'employee_id', label: 'Created M21 Employee Record' },
          { name: 'state', required: true, label: 'Recruitment Stage' }
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
          { name: 'requisition_id', label: 'Job Requisition' },
          { name: 'interviewer_id', label: 'Lead Interviewer' },
          { name: 'scheduled_on', required: true, label: 'Scheduled Date & Time' },
          { name: 'round_no', required: true, label: 'Round Number' }
        ]
      },
      {
        tab: 'evaluation',
        title: 'Competency Scoring & Recommendation',
        note: '1–5 standardized technical rating and hire recommendation.',
        fields: [
          { name: 'competency_code', label: 'Primary Competency Evaluated' },
          { name: 'score', label: 'Evaluation Score (1-5)' },
          { name: 'recommendation', label: 'Hiring Recommendation' },
          { name: 'notes', type: 'text', label: 'Interviewer Notes' }
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
          { name: 'requisition_id', label: 'Job Requisition' },
          { name: 'position_id', label: 'Offered Position' },
          { name: 'gross_salary', label: 'Gross Monthly Salary (BDT)' }
        ]
      },
      {
        tab: 'terms',
        title: 'Offer Timeline & Acceptance',
        note: 'Validity dates and formal candidate acceptance status.',
        fields: [
          { name: 'issued_on', required: true, label: 'Offer Issued Date' },
          { name: 'valid_until', label: 'Offer Valid Until' },
          { name: 'joining_date', label: 'Expected Date of Joining' },
          { name: 'state', required: true, label: 'Offer Acceptance State' }
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
          { name: 'employee_id', label: 'Created Employee Record' },
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
          { name: 'nid_verified', label: 'National ID (NID) Verified' },
          { name: 'contract_signed', label: 'Statutory Form 6 Contract Signed' },
          { name: 'bank_details_captured', label: 'Bank / MFS Wallet Captured' }
        ]
      },
      {
        tab: 'provisioning',
        title: 'IT Assets & Safety Equipment Handover',
        note: 'Equipment and identity provisioning tracking.',
        fields: [
          { name: 'it_assets_allocated', label: 'Mobile Device / Laptop Issued' },
          { name: 'keycloak_provisioned', label: 'Single Sign-On (IdP) Provisioned' },
          { name: 'safety_kit_issued', label: 'Standard PPE Kit Issued' },
          { name: 'state', required: true, label: 'Onboarding Plan State' }
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
          { name: 'requisition_id', label: 'Job Requisition' },
          { name: 'competency_code', label: 'Tested Competency Code' },
          { name: 'assessor_id', label: 'Bench Technical Assessor' }
        ]
      },
      {
        tab: 'evaluation',
        title: 'Practical Test Score & Hiring Gate',
        note: 'A failed practical assessment blocks candidate hire under RAP-M58-05.',
        fields: [
          { name: 'assessed_on', required: true, label: 'Assessment Date' },
          { name: 'score', label: 'Practical Score (0-100)' },
          { name: 'passed', label: 'Passed Bench Assessment' },
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
          { name: 'completed_on', label: 'Completed Date' },
          { name: 'result', required: true, label: 'Verification Result' },
          { name: 'notes', type: 'text', label: 'Verification Remarks & Reference Notes' }
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
    'fix.talent.first90': 'M58-form-first90'
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
    'M58-first90': 'M58-form-first90'
  }
};

export const CREATE = {
  M58: { screen: 'M58-form-req', model: 'fix.job.requisition', label: 'Requisition' }
};
