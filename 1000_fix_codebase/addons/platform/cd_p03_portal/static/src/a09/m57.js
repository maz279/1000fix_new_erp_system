/** @odoo-module **/
/* A09 · People & Workforce — M57 Performance & Incentives.
 * Registry-faithful: 3 groups / 10 screens / 5 reports / 4 forms / freg 58.
 * A09 round 2 adds four screens: scheme versions, disputes, clawbacks and
 * compensation proposals. */

export const MODULE = {
  area: 'A09', code: 'M57', en: 'Performance & Incentives', title: 'M57 · Performance & Incentives',
  bn: 'কর্মদক্ষতা ও প্রণোদনা', icon: '🏆',
  desc: 'Goal cascades and KPI definitions, review cycles with calibration, performance improvement plans, technician incentive schemes and calculation runs, recognition awards, compensation review against bands, and succession planning.',
  kpis: [
    { l: 'Reviews On Track', m: 'reviews_on_track', suffix: '%' },
    { l: 'Incentive Pool MTD', m: 'incentive_pool_mtd', prefix: '৳ ' },
    { l: 'Goal Coverage', m: 'goal_coverage', suffix: '%' },
    { l: 'Calibration Sessions', m: 'calibration_sessions' },
    { l: 'PIPs Active', m: 'pips_active' },
    { l: 'Incentive Accuracy', m: 'incentive_accuracy', suffix: '%' }
  ],
  groups: [
    { en: 'Performance', screens: [
      { id: 'M57-goals', en: 'Goal Cascades', bn: 'লক্ষ্য স্তর', t: 'g' },
      { id: 'M57-kpis', en: 'KPI Definitions', bn: 'কেপিআই', t: 'g' },
      { id: 'M57-reviews', en: 'Review Cycles', bn: 'পর্যালোচনা চক্র', t: 'g' },
      { id: 'M57-calibration', en: 'Calibration', bn: 'ক্যালিব্রেশন', t: 'r' },
      { id: 'M57-pips', en: 'PIPs', bn: 'কর্ম উন্নয়ন পরিকল্পনা', t: 'g' }
    ]},
    { en: 'Incentives', screens: [
      { id: 'M57-schemes', en: 'Incentive Schemes', bn: 'প্রণোদনা কর্মসূচি', t: 'g' },
      { id: 'M57-scheme-versions', en: 'Scheme Versions & Approval', bn: 'কর্মসূচি সংস্করণ', t: 'g' },
      { id: 'M57-calc', en: 'Calculation Runs', bn: 'হিসাব রান', t: 'g' },
      { id: 'M57-disputes', en: 'Incentive Disputes', bn: 'প্রণোদনা আপত্তি', t: 'g' },
      { id: 'M57-clawbacks', en: 'Clawbacks', bn: 'প্রণোদনা ফেরত', t: 'g' },
      { id: 'M57-recognition', en: 'Recognition', bn: 'স্বীকৃতি', t: 'g' }
    ]},
    { en: 'Compensation', screens: [
      { id: 'M57-comp', en: 'Compensation Review', bn: 'বেতন পর্যালোচনা', t: 'g' },
      { id: 'M57-proposals', en: 'Compensation Proposals', bn: 'বেতন প্রস্তাব', t: 'g' },
      { id: 'M57-succession', en: 'Succession', bn: 'উত্তরসূরি', t: 'g' }
    ]}
  ],
  reports: ['Rating Distribution', 'Incentive Payout by Scheme', 'Technician Scorecards', 'Calibration Summary', 'PIP Outcomes'],
  forms: ['Goal', 'Review', 'Incentive Scheme', 'Recognition'],
  cross: ['M21 Workforce', 'M56 Payroll', 'M01 Service Orders', 'M54 Costing'],
  freg: { src: 58, sub: [
    ['1', 'Goals & KPIs', 11, { model: 'fix.performance.goal', cols: ['name', 'employee_id', 'period', 'target_value', 'actual_value'], screens: ['M57-goals', 'M57-kpis'] }],
    ['2', 'Review Cycles', 10, { model: 'fix.performance.review', cols: ['name', 'employee_id', 'period', 'reviewer_id', 'state'], screens: ['M57-reviews', 'M57-pips'] }],
    ['3', 'Multi-Source Feedback', 6, { model: 'fix.performance.review', cols: ['employee_id', 'reviewer_id', 'period', 'self_rating', 'manager_rating'], screens: ['M57-reviews'] }],
    ['4', 'Rating & Calibration', 8, { model: 'fix.performance.review', cols: ['employee_id', 'period', 'manager_rating', 'calibrated_rating', 'state'], screens: ['M57-calibration', 'M57-reviews'] }],
    ['5', 'Incentive Design & Calculation', 12, { model: 'fix.incentive.line', cols: ['run_id', 'employee_id', 'scorecard_id', 'amount', 'applied_to_payslip'], screens: ['M57-schemes', 'M57-scheme-versions', 'M57-calc', 'M57-disputes', 'M57-clawbacks'] }],
    ['6', 'Recognition', 4, { model: 'fix.performance.recognition', cols: ['name', 'employee_id', 'award_type', 'awarded_on', 'prize_amount'], screens: ['M57-recognition'] }],
    ['7', 'Compensation Review', 7, { model: 'fix.compensation.band', cols: ['name', 'grade', 'range_min', 'range_mid', 'range_max'], screens: ['M57-comp', 'M57-proposals', 'M57-succession'] }]
  ] }
};

export const SCREENS = {
  'M57-goals': { kind: 'model_list', model: 'fix.performance.goal', stateField: 'state',
    cols: ['name', 'employee_id', 'parent_goal_id', 'period', 'weight', 'target_value', 'actual_value', 'state'],
    actions: [{ m: 'action_agree', l: 'Agree Goal (employee / manager)' }, { m: 'action_activate', l: 'Activate' },
              { m: 'action_close', l: 'Close' }] },
  'M57-kpis': { kind: 'model_list', create: false, model: 'fix.performance.scorecard',
    cols: ['employee_id', 'period', 'first_time_fix', 'sla_hit', 'csat', 'salvage_ratio', 'rework_30d_rate', 'rework_rate', 'score', 'state'],
    actions: [{ m: 'action_compute_from_orders', l: 'Compute from Service Orders' }, { m: 'action_publish', l: 'Publish Scorecard' }] },
  'M57-reviews': { kind: 'model_list', model: 'fix.performance.review', stateField: 'state',
    cols: ['name', 'employee_id', 'reviewer_id', 'period', 'self_rating', 'manager_rating', 'calibrated_rating', 'approval_state', 'state'],
    actions: [{ m: 'action_start', l: 'Open Self-Assessment' },
              { m: 'action_record_self_rating', l: 'Record My Self Rating', ask: 'Your self rating, 1 to 5', kwarg: 'rating' },
              { m: 'action_submit_self_assessment', l: 'Submit Self-Assessment' },
              { m: 'action_record_manager_rating', l: 'Record Manager Rating', ask: 'Your rating of this report, 1 to 5', kwarg: 'rating' },
              { m: 'action_manager_review', l: 'Submit Manager Rating (to Calibration)' },
              { m: 'action_recall_calibration', l: 'Recall Calibration (manager)' },
              { m: 'action_close', l: 'Close' },
              { m: 'action_propose_compensation', l: 'Propose Compensation (line manager)', ask: 'Proposed monthly basic (BDT) and the justification, e.g. 32000 consistently exceeds targets', kwarg: 'proposal' }] },
  'M57-calibration': { kind: 'table_report', module: 'M57', report: 'calibration_summary', title: 'Calibration Summary', period: true },
  'M57-pips': { kind: 'model_list', model: 'fix.performance.pip', stateField: 'state',
    cols: ['name', 'employee_id', 'start_date', 'end_date', 'outcome', 'state'],
    actions: [{ m: 'action_start', l: 'Start' }, { m: 'action_close', l: 'Close' }] },
  'M57-schemes': { kind: 'model_list', model: 'fix.incentive.run', stateField: 'state',
    cols: ['period', 'scheme_id', 'scheme_version_id', 'band_base', 'total', 'dispute_deadline', 'approval_state', 'state'],
    actions: [{ m: 'action_compute', l: 'Calculate Pool' }, { m: 'action_request_approval', l: 'Request Approval' },
              { m: 'action_recall_approval', l: 'Recall Approval' }, { m: 'action_reset_draft', l: 'Reset to Draft' }] },
  'M57-calc': { kind: 'model_list', model: 'fix.incentive.line',
    cols: ['run_id', 'employee_id', 'line_type', 'gross_amount', 'proration_factor', 'amount', 'eligibility_note', 'run_state', 'applied_to_payslip'],
    actions: [{ m: 'action_raise_dispute', l: 'Dispute My Line', ask: 'What is wrong with the figure, and on what evidence?', kwarg: 'reason' }] },
  'M57-scheme-versions': { kind: 'model_list', model: 'fix.incentive.scheme.version', stateField: 'state',
    cols: ['name', 'scheme_id', 'date_from', 'date_to', 'cut_top', 'rate_top', 'cut_mid', 'rate_mid', 'cut_low', 'rate_low', 'approval_state', 'state'],
    actions: [{ m: 'action_request_approval', l: 'Request Approval (HR Director, then CFO)' },
              { m: 'action_recall_approval', l: 'Recall Approval' },
              { m: 'action_reset_draft', l: 'Reopen Rejected Version' }] },
  'M57-disputes': { kind: 'model_list', model: 'fix.incentive.dispute', stateField: 'state', create: false,
    cols: ['name', 'employee_id', 'run_id', 'disputed_amount', 'raised_at', 'state', 'resolved_by_id'],
    actions: [{ m: 'action_uphold', l: 'Uphold (recompute the run)', ask: 'The answer and its basis', kwarg: 'resolution' },
              { m: 'action_reject', l: 'Reject', ask: 'The answer and its basis', kwarg: 'resolution' }] },
  'M57-clawbacks': { kind: 'model_list', model: 'fix.incentive.clawback', stateField: 'state', create: false,
    cols: ['name', 'employee_id', 'source_run_id', 'service_order_id', 'trigger', 'trigger_ref', 'amount', 'recovered_amount', 'remaining_amount', 'state'] },
  'M57-proposals': { kind: 'model_list', model: 'fix.compensation.proposal', stateField: 'state', create: false,
    cols: ['name', 'employee_id', 'proposal_type', 'current_basic', 'proposed_basic', 'increase_pct', 'effective_date', 'approval_state', 'state'],
    actions: [{ m: 'action_calibration_review', l: 'Calibrate and Route to Compensation', ask: 'Calibration note (optionally start with an adjusted basic, e.g. 31000 aligned with peers)', kwarg: 'calibration' },
              { m: 'action_calibration_return', l: 'Return to Manager', ask: 'Why it is returned', kwarg: 'note' },
              { m: 'action_withdraw', l: 'Withdraw (proposer)' }] },
  'M57-recognition': { kind: 'model_list', model: 'fix.performance.recognition', stateField: 'state',
    cols: ['name', 'employee_id', 'award_type', 'awarded_on', 'prize_amount', 'citation', 'approval_state', 'state'],
    actions: [{ m: 'action_award', l: 'Award (no prize)' }, { m: 'action_request_approval', l: 'Request Prize Approval' },
              { m: 'action_recall_approval', l: 'Recall Approval' }, { m: 'action_cancel', l: 'Cancel' }] },
  'M57-comp': { kind: 'model_list', model: 'fix.compensation.band',
    cols: ['name', 'grade', 'range_min', 'range_mid', 'range_max', 'company_id'] },
  'M57-succession': { kind: 'model_list', model: 'fix.succession.plan',
    cols: ['position_name', 'incumbent_id', 'successor_id', 'readiness', 'risk', 'company_id'] },

  /* Report chips -> their own computed pack */
  'M57-rpt-ratings': { kind: 'table_report', module: 'M57', report: 'rating_distribution', title: 'Rating Distribution', period: true },
  'M57-rpt-payout': { kind: 'table_report', module: 'M57', report: 'incentive_payout', title: 'Incentive Payout by Scheme', period: true },
  'M57-rpt-scorecards': { kind: 'table_report', module: 'M57', report: 'technician_scorecards', title: 'Technician Scorecards', period: true },
  'M57-rpt-calib': { kind: 'table_report', module: 'M57', report: 'calibration_summary', title: 'Calibration Summary', period: true },
  'M57-rpt-pip': { kind: 'table_report', module: 'M57', report: 'pip_outcomes', title: 'PIP Outcomes', period: true },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M57-form-goal': {
    kind: 'model_form',
    model: 'fix.performance.goal',
    title: 'Cascaded Goal',
    back: 'M57-goals',
    status: { field: 'state', labels: {
      draft: 'Draft', active: 'Active', achieved: 'Achieved', missed: 'Missed' } },
    tabs: [
      { id: 'milestone', label: 'OKR Milestone', bn: 'লক্ষ্যমাত্রা', icon: '🎯', badge: '4' },
      { id: 'evaluation', label: 'Weight & Progress', bn: 'ওজন ও মূল্যায়ন', icon: '⚖️', badge: '5' }
    ],
    sections: [
      {
        tab: 'milestone',
        title: 'Goal Specification & Cascade',
        note: 'Goal cascades from organizational OKRs down to individual technician KPI scorecard.',
        fields: [
          { name: 'name', required: true, label: 'Goal Title' },
          { name: 'employee_id', required: true, label: 'Employee' },
          { name: 'parent_goal_id', label: 'Cascaded From Corporate Goal' },
          { name: 'period', required: true, label: 'Performance Period (YYYY-MM)' }
        ]
      },
      {
        tab: 'evaluation',
        title: 'Weightage & Evaluation Targets',
        note: 'Weights of one employee-period total 100%. The employee and the line manager both agree a goal before it is activated; a closed goal is final.',
        fields: [
          { name: 'weight', required: true, label: 'Weightage (%)' },
          { name: 'target_value', label: 'Target Value' },
          { name: 'actual_value', label: 'Actual Achieved Value' },
          { name: 'unit', label: 'Measurement Unit' },
          { name: 'state', readonly: true, label: 'State' },
          { name: 'employee_agreed_by_id', readonly: true, label: 'Agreed by Employee' },
          { name: 'manager_agreed_by_id', readonly: true, label: 'Agreed by Manager' },
          { name: 'closed_by_id', readonly: true, label: 'Closed By' }
        ]
      }
    ]
  },

  'M57-form-review': {
    kind: 'model_form',
    model: 'fix.performance.review',
    title: '360 Review',
    back: 'M57-reviews',
    status: { field: 'state', labels: {
      draft: 'Draft', self_review: 'Self Review', manager_review: 'Manager Review',
      calibrated: 'Calibrated', closed: 'Closed' } },
    tabs: [
      { id: 'cycle', label: 'Review Period', bn: 'পর্যালোচনা সময়সীমা', icon: '🔄', badge: '3' },
      { id: 'scoring', label: 'Multi-Rater Scoring', bn: 'রেটিং ও মূল্যায়ন', icon: '👥', badge: '4' }
    ],
    sections: [
      {
        tab: 'cycle',
        title: 'Review Cycle Particulars',
        note: 'Performance appraisal cycle parameters and participants.',
        fields: [
          { name: 'employee_id', required: true, label: 'Employee' },
          { name: 'reviewer_id', label: 'Appraising Manager (the line manager)' },
          { name: 'period', required: true, label: 'Review Period' }
        ]
      },
      {
        tab: 'scoring',
        title: 'Multi-Rater Evaluation Ratings (1–5 Scale)',
        note: 'The employee records the self rating and the line manager the manager rating with the list actions; a calibrator who is neither decides the calibration from the approval inbox. A closed review is final.',
        fields: [
          { name: 'self_rating', readonly: true, label: 'Self Evaluation (1-5)' },
          { name: 'manager_rating', readonly: true, label: 'Manager Evaluation (1-5)' },
          { name: 'calibrated_rating', readonly: true, label: 'Calibrated Final Rating (1-5)' },
          { name: 'state', readonly: true, label: 'Review State' },
          { name: 'approval_state', readonly: true, label: 'Calibration Approval' },
          { name: 'manager_rated_by_id', readonly: true, label: 'Rated By' },
          { name: 'calibrated_by_id', readonly: true, label: 'Calibrated By' },
          { name: 'closed_by_id', readonly: true, label: 'Closed By' }
        ]
      }
    ]
  },

  'M57-form-pip': {
    kind: 'model_form',
    model: 'fix.performance.pip',
    title: 'Performance Improvement Plan',
    back: 'M57-pips',
    status: { field: 'state', labels: {
      draft: 'Draft', active: 'Active', closed: 'Closed' } },
    tabs: [
      { id: 'deficiencies', label: 'Remediation Scope', bn: 'উন্নতির ক্ষেত্র', icon: '⚠️', badge: '5' },
      { id: 'outcome', label: 'Milestones & Outcome', bn: 'ফলাফল ও সিদ্ধান্ত', icon: '📅', badge: '2' }
    ],
    sections: [
      {
        tab: 'deficiencies',
        title: 'Performance Gaps & Remediation Plan',
        note: 'Governed structured improvement plan before any adverse employment action under BLA 2006.',
        fields: [
          { name: 'employee_id', required: true, label: 'Employee' },
          { name: 'mentor_id', label: 'Assigned Senior Mentor' },
          { name: 'start_date', required: true, label: 'PIP Start Date' },
          { name: 'end_date', required: true, label: 'PIP End Date' },
          { name: 'reason', type: 'text', label: 'Deficiencies & Required Milestones' }
        ]
      },
      {
        tab: 'outcome',
        title: 'Evaluation Checkpoint & Outcome',
        note: 'Final assessment by HR and department head.',
        fields: [
          { name: 'outcome', label: 'Final Assessment Summary' },
          { name: 'state', readonly: true, label: 'PIP State' },
          { name: 'started_by_id', readonly: true, label: 'Started By' },
          { name: 'closed_by_id', readonly: true, label: 'Closed By' }
        ]
      }
    ]
  },

  'M57-form-recognition': {
    kind: 'model_form',
    model: 'fix.performance.recognition',
    title: 'Spot Recognition',
    back: 'M57-recognition',
    status: { field: 'state', labels: {
      draft: 'Draft', awarded: 'Awarded', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'award', label: 'Award Particulars', bn: 'পুরস্কারের বিবরণ', icon: '🏆', badge: '4' },
      { id: 'citation', label: 'Merit Citation', bn: 'প্রশংসাপত্র', icon: '📜', badge: '1' }
    ],
    sections: [
      {
        tab: 'award',
        title: 'Recognition Category & Token',
        note: 'A prize is a payment: it is approved by the Incentive Approver and paid and taxed through payroll. Nobody awards themself.',
        fields: [
          { name: 'employee_id', required: true, label: 'Employee' },
          { name: 'award_type', required: true, label: 'Recognition Category' },
          { name: 'awarded_on', required: true, label: 'Award Date' },
          { name: 'prize_amount', label: 'Cash / Voucher Prize (BDT)' },
          { name: 'state', readonly: true, label: 'State' },
          { name: 'approval_state', readonly: true, label: 'Prize Approval' },
          { name: 'awarded_by_id', readonly: true, label: 'Awarded / Approved By' }
        ]
      },
      {
        tab: 'citation',
        title: 'Merit Citation & Justification',
        note: 'Recognized achievement details.',
        fields: [
          { name: 'citation', type: 'text', label: 'Merit Citation' }
        ]
      }
    ]
  },

  'M57-form-scorecard': {
    kind: 'model_form',
    model: 'fix.performance.scorecard',
    title: 'Technician Performance Scorecard',
    back: 'M57-kpis',
    tabs: [
      { id: 'employee', label: 'Technician & Period', bn: 'টেকনিশিয়ান ও সময়কাল', icon: '👤', badge: '3' },
      { id: 'metrics', label: 'Core KPIs (FTFR / SLA / CSAT)', bn: 'মূল কেপিআই স্কোর', icon: '📊', badge: '4' },
      { id: 'salvage', label: 'Salvage & 30d Rework Clawback', bn: 'সালভেজ ও রিওয়ার্ক জরিমানা', icon: '♻️', badge: '5' }
    ],
    sections: [
      {
        tab: 'employee',
        title: 'Scorecard Subject & Evaluation Period',
        note: 'Monthly technician performance evaluation card.',
        fields: [
          { name: 'employee_id', required: true, label: 'Technician / Employee' },
          { name: 'period', required: true, label: 'Evaluation Period (YYYY-MM)' },
          { name: 'operating_unit_id', label: 'Operating Unit' }
        ]
      },
      {
        tab: 'metrics',
        title: 'Weighted Service Delivery KPIs (40% FTFR + 25% SLA + 20% CSAT)',
        note: 'Computed from the completed service orders (M01) and survey ratings (M34) by Compute from Service Orders; never typed (BRU-PIC-03).',
        fields: [
          { name: 'first_time_fix', readonly: true, label: 'First-Time Fix Ratio (0.0 - 1.0)' },
          { name: 'sla_hit', readonly: true, label: 'SLA Compliance Ratio (0.0 - 1.0)' },
          { name: 'csat', readonly: true, label: 'Customer Satisfaction Ratio (0.0 - 1.0)' },
          { name: 'score', readonly: true, label: 'Computed Composite Score (0.0 - 1.0)' },
          { name: 'facts_orders', readonly: true, label: 'Service Orders Counted' },
          { name: 'facts_basis', readonly: true, label: 'Computation Basis' },
          { name: 'state', readonly: true, label: 'Scorecard State' }
        ]
      },
      {
        tab: 'salvage',
        title: 'Component Salvage Recovery (15%) & 30-Day Rework Clawback',
        note: 'Board-level salvage value vs target, and 30-day repeat repair penalty ramp above 3% threshold.',
        fields: [
          { name: 'salvage_value', readonly: true, label: 'Actual Salvaged Parts Value (BDT)' },
          { name: 'salvage_target', label: 'Monthly Salvage Target (BDT)' },
          { name: 'salvage_ratio', readonly: true, label: 'Salvage Achievement Ratio (0.0 - 1.0)' },
          { name: 'rework_30d_rate', readonly: true, label: '30-Day Repeat Repair Rate (0.0 - 1.0)' },
          { name: 'rework_rate', readonly: true, label: 'General Rework Rate (0.0 - 1.0)' }
        ]
      }
    ]
  },

  'M57-form-scheme': {
    kind: 'model_form',
    model: 'fix.incentive.run',
    title: 'Incentive Calculation Run',
    back: 'M57-schemes',
    status: { field: 'state', labels: {
      draft: 'Draft', computed: 'Computed', approved: 'Approved' } },
    tabs: [
      { id: 'pool', label: 'Scheme Pool & Period', bn: 'প্রণোদনা তহবিল ও সময়কাল', icon: '💰', badge: '4' },
      { id: 'status', label: 'Payroll Sync & State', bn: 'বেতন সমন্বয় ও অবস্থা', icon: '⚙️', badge: '2' }
    ],
    sections: [
      {
        tab: 'pool',
        title: 'Incentive Scheme Pool Parameters',
        note: 'The run computes under the scheme version approved by the HR Director and the CFO and in force for the period, and pins it: its band rates, score cut-offs, eligibility and band base. Joiners, leavers and long leave are prorated by days. One run per period and company.',
        fields: [
          { name: 'period', required: true, label: 'Payroll Period (YYYY-MM)' },
          { name: 'scheme_id', label: 'Incentive Scheme' },
          { name: 'scheme_version_id', readonly: true, label: 'Scheme Version Applied' },
          { name: 'band_base', readonly: true, label: 'Band Base (from the version, BDT)' },
          { name: 'total', readonly: true, label: 'Total Computed Pool Payout (BDT)' },
          { name: 'company_id', label: 'Company' }
        ]
      },
      {
        tab: 'status',
        title: 'Governance & M56 Payslip Push Status',
        note: 'An approved run is final; payroll (M56) picks its lines up. M57 never writes a payslip (BRU-PIC-09). The approver is never the preparer or anyone with a line on the run.',
        fields: [
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'state', readonly: true, label: 'Run State' },
          { name: 'approval_state', readonly: true, label: 'Approval' },
          { name: 'dispute_deadline', readonly: true, label: 'Disputes Close On' },
          { name: 'computed_by_id', readonly: true, label: 'Computed By' },
          { name: 'approved_by_id', readonly: true, label: 'Approved By' },
          { name: 'approved_total', readonly: true, label: 'Approved Total (BDT)' }
        ]
      }
    ]
  },

  'M57-form-calc': {
    kind: 'model_form',
    model: 'fix.incentive.line',
    title: 'Technician Incentive Payout Line',
    back: 'M57-calc',
    tabs: [
      { id: 'payout', label: 'Scorecard & Payout', bn: 'স্কোরকার্ড ও প্রণোদনা', icon: '💵', badge: '4' },
      { id: 'payroll', label: 'Payslip Link (M56)', bn: 'পে-স্লিপ সংযোগ', icon: '🔗', badge: '2' }
    ],
    sections: [
      {
        tab: 'payout',
        title: 'Individual Technician Incentive Calculation',
        note: 'Computed by the run from the published scorecard band; lines are never typed.',
        fields: [
          { name: 'run_id', readonly: true, label: 'Incentive Run' },
          { name: 'employee_id', readonly: true, label: 'Technician / Employee' },
          { name: 'scorecard_id', readonly: true, label: 'Source Scorecard' },
          { name: 'line_type', readonly: true, label: 'Line Type' },
          { name: 'gross_amount', readonly: true, label: 'Banded Amount (BDT)' },
          { name: 'proration_factor', readonly: true, label: 'Proration' },
          { name: 'eligible', readonly: true, label: 'Eligible' },
          { name: 'eligibility_note', readonly: true, label: 'Eligibility / Proration Basis' },
          { name: 'clawback_id', readonly: true, label: 'Clawback Recovered' },
          { name: 'amount', readonly: true, label: 'Incentive Payout Amount (BDT)' }
        ]
      },
      {
        tab: 'payroll',
        title: 'M56 Payroll Integration Trace',
        note: 'Set by payroll (M56) when it pays the approved line; a line is paid on one payslip only.',
        fields: [
          { name: 'applied_to_payslip', readonly: true, label: 'Applied to M56 Payslip' },
          { name: 'payslip_ref_id', readonly: true, label: 'Linked Payslip Record ID' }
        ]
      }
    ]
  },

  'M57-form-scheme-def': {
    kind: 'model_form',
    model: 'fix.incentive.scheme',
    title: 'Incentive Scheme',
    back: 'M57-scheme-versions',
    tabs: [
      { id: 'scheme', label: 'Scheme', bn: 'কর্মসূচি', icon: '📋', badge: '4' }
    ],
    sections: [
      {
        tab: 'scheme',
        title: 'Incentive Scheme',
        note: 'A scheme holds effective-dated versions; the figures live on the version, which the HR Director and the CFO approve.',
        fields: [
          { name: 'name', required: true, label: 'Scheme Name' },
          { name: 'code', required: true, label: 'Code' },
          { name: 'company_id', required: true, label: 'Company' },
          { name: 'description', type: 'text', label: 'Description' },
          { name: 'current_version_id', readonly: true, label: 'Version in Force Today' }
        ]
      }
    ]
  },

  'M57-form-scheme-version': {
    kind: 'model_form',
    model: 'fix.incentive.scheme.version',
    title: 'Incentive Scheme Version',
    back: 'M57-scheme-versions',
    status: { field: 'state', labels: {
      draft: 'Draft', hr_review: 'Awaiting HR Director', cfo_review: 'Awaiting CFO',
      approved: 'Approved', rejected: 'Rejected' } },
    tabs: [
      { id: 'terms', label: 'Bands & Base', bn: 'ব্যান্ড ও ভিত্তি', icon: '📊', badge: '9' },
      { id: 'eligibility', label: 'Eligibility', bn: 'যোগ্যতা', icon: '✅', badge: '2' },
      { id: 'approval', label: 'Approval (HR Director + CFO)', bn: 'অনুমোদন', icon: '🖋️', badge: '6' }
    ],
    sections: [
      {
        tab: 'terms',
        title: 'Effective Dates, Band Rates and Score Cut-offs',
        note: 'BRU-PIC-01/02. Version 1 carries the figures the code used, marked as coded and unsourced: set the band base and the basis before requesting approval.',
        fields: [
          { name: 'scheme_id', required: true, label: 'Scheme' },
          { name: 'version_no', readonly: true, label: 'Version' },
          { name: 'date_from', required: true, label: 'Effective From' },
          { name: 'date_to', label: 'Effective To' },
          { name: 'basis', label: 'Source of the Figures' },
          { name: 'band_base', label: 'Band Base (BDT)' },
          { name: 'cut_top', label: 'Top Band From Score (0-1)' },
          { name: 'rate_top', label: 'Top Band Rate %' },
          { name: 'cut_mid', label: 'Middle Band From Score (0-1)' },
          { name: 'rate_mid', label: 'Middle Band Rate %' },
          { name: 'cut_low', label: 'Lower Band From Score (0-1)' },
          { name: 'rate_low', label: 'Lower Band Rate %' }
        ]
      },
      {
        tab: 'eligibility',
        title: 'Eligibility and Proration (FR-PIC-028/032)',
        note: 'Joiners and leavers are always prorated by calendar days. 0 = not ruled.',
        fields: [
          { name: 'min_service_days', label: 'Minimum Service (days)' },
          { name: 'long_leave_days', label: 'Long Leave Prorated From (days)' }
        ]
      },
      {
        tab: 'approval',
        title: 'Two Signatures',
        note: 'Request Approval routes the version to the HR Director; the HR Director\'s approval routes it to the CFO. Neither signs a version they requested, and they are two different people.',
        fields: [
          { name: 'state', readonly: true, label: 'State' },
          { name: 'approval_state', readonly: true, label: 'Approval' },
          { name: 'requested_by_id', readonly: true, label: 'Requested By' },
          { name: 'hr_director_id', readonly: true, label: 'HR Director' },
          { name: 'hr_director_at', readonly: true, label: 'HR Director Approved At' },
          { name: 'cfo_id', readonly: true, label: 'CFO' },
          { name: 'cfo_at', readonly: true, label: 'CFO Approved At' }
        ]
      }
    ]
  },

  'M57-form-dispute': {
    kind: 'model_form',
    model: 'fix.incentive.dispute',
    title: 'Incentive Dispute',
    back: 'M57-disputes',
    status: { field: 'state', labels: { open: 'Open', upheld: 'Upheld', rejected: 'Rejected' } },
    tabs: [
      { id: 'dispute', label: 'Dispute', bn: 'আপত্তি', icon: '⚖️', badge: '5' },
      { id: 'answer', label: 'Answer', bn: 'উত্তর', icon: '✉️', badge: '3' }
    ],
    sections: [
      {
        tab: 'dispute',
        title: 'The Disputed Line (BRU-PIC-12)',
        note: 'Raised by the employee from their own computed line, inside the dispute window. An open dispute blocks the run\'s approval.',
        fields: [
          { name: 'employee_id', readonly: true, label: 'Employee' },
          { name: 'run_id', readonly: true, label: 'Incentive Run' },
          { name: 'line_id', readonly: true, label: 'Disputed Line' },
          { name: 'disputed_amount', readonly: true, label: 'Disputed Amount (BDT)' },
          { name: 'reason', readonly: true, type: 'text', label: 'Reason and Evidence' },
          { name: 'raised_at', readonly: true, label: 'Raised At' }
        ]
      },
      {
        tab: 'answer',
        title: 'Answer by an Incentive Officer',
        note: 'Upheld: reset and recompute the run before approval. Nobody answers their own dispute.',
        fields: [
          { name: 'state', readonly: true, label: 'State' },
          { name: 'resolved_by_id', readonly: true, label: 'Answered By' },
          { name: 'resolution', readonly: true, type: 'text', label: 'Answer' }
        ]
      }
    ]
  },

  'M57-form-clawback': {
    kind: 'model_form',
    model: 'fix.incentive.clawback',
    title: 'Incentive Clawback',
    back: 'M57-clawbacks',
    tabs: [
      { id: 'trigger', label: 'Trigger', bn: 'কারণ', icon: '♻️', badge: '6' },
      { id: 'recovery', label: 'Recovery', bn: 'আদায়', icon: '💵', badge: '4' }
    ],
    sections: [
      {
        tab: 'trigger',
        title: 'Rework or Credit within the Clawback Window (BRU-PIC-11)',
        note: 'Raised by the incentive computation for an order paid in an approved run that was reworked or credited within the window. Never typed.',
        fields: [
          { name: 'employee_id', readonly: true, label: 'Employee' },
          { name: 'source_run_id', readonly: true, label: 'Paid In Run' },
          { name: 'source_line_id', readonly: true, label: 'Paid Line' },
          { name: 'service_order_id', readonly: true, label: 'Service Order' },
          { name: 'trigger', readonly: true, label: 'Trigger' },
          { name: 'trigger_ref', readonly: true, label: 'Rework / Credit' }
        ]
      },
      {
        tab: 'recovery',
        title: 'Recovered from Later Runs',
        note: 'Recovered from the employee\'s incentive in the next runs, never more than they earn in a run.',
        fields: [
          { name: 'amount', readonly: true, label: 'To Recover (BDT)' },
          { name: 'recovered_amount', readonly: true, label: 'Recovered (BDT)' },
          { name: 'remaining_amount', readonly: true, label: 'Remaining (BDT)' },
          { name: 'state', readonly: true, label: 'State' }
        ]
      }
    ]
  },

  'M57-form-proposal': {
    kind: 'model_form',
    model: 'fix.compensation.proposal',
    title: 'Compensation Proposal',
    back: 'M57-proposals',
    status: { field: 'state', labels: {
      submitted: 'Awaiting Calibration', calibrated: 'Awaiting Compensation Approval',
      approved: 'Approved', returned: 'Returned', rejected: 'Rejected', withdrawn: 'Withdrawn' } },
    tabs: [
      { id: 'proposal', label: 'Proposal', bn: 'প্রস্তাব', icon: '💼', badge: '8' },
      { id: 'decision', label: 'Calibration & Approval', bn: 'অনুমোদন', icon: '🖋️', badge: '7' }
    ],
    sections: [
      {
        tab: 'proposal',
        title: 'Raised by the Line Manager (BRU-PIC-17)',
        note: 'Proposed from a closed review by the employee\'s line manager, inside the pay band. The figure, contract and date are pinned once raised.',
        fields: [
          { name: 'employee_id', readonly: true, label: 'Employee' },
          { name: 'contract_id', readonly: true, label: 'Active Contract' },
          { name: 'review_id', readonly: true, label: 'Review Cycle' },
          { name: 'proposal_type', readonly: true, label: 'Type' },
          { name: 'current_basic', readonly: true, label: 'Current Basic (BDT)' },
          { name: 'proposed_basic', readonly: true, label: 'Proposed Basic (BDT)' },
          { name: 'increase_pct', readonly: true, label: 'Increase %' },
          { name: 'effective_date', readonly: true, label: 'Effective From' },
          { name: 'justification', readonly: true, type: 'text', label: 'Justification' }
        ]
      },
      {
        tab: 'decision',
        title: 'Calibration, then the Compensation Manager',
        note: 'Approval opens a new contract VERSION with the new basic; it then goes through legal sign-off and activation (M21). The proposer, the calibrator and the employee never approve it.',
        fields: [
          { name: 'state', readonly: true, label: 'State' },
          { name: 'approval_state', readonly: true, label: 'Approval' },
          { name: 'proposed_by_id', readonly: true, label: 'Proposed By' },
          { name: 'calibrated_by_id', readonly: true, label: 'Calibrated By' },
          { name: 'calibration_note', readonly: true, type: 'text', label: 'Calibration Note' },
          { name: 'approved_by_id', readonly: true, label: 'Approved By' },
          { name: 'new_contract_id', readonly: true, label: 'New Contract Version' }
        ]
      }
    ]
  },

  'M57-form-comp': {
    kind: 'model_form',
    model: 'fix.compensation.band',
    title: 'Corporate Compensation Band',
    back: 'M57-comp',
    tabs: [
      { id: 'band', label: 'Grade & Band Identity', bn: 'গ্রেড ও ব্যান্ড', icon: '🏷️', badge: '3' },
      { id: 'ranges', label: 'Salary Range (Min / Mid / Max)', bn: 'বেতন সীমা', icon: '📊', badge: '4' }
    ],
    sections: [
      {
        tab: 'band',
        title: 'Corporate Grade Classification',
        note: 'Establishment pay grade band.',
        fields: [
          { name: 'name', required: true, label: 'Band Title' },
          { name: 'grade', required: true, label: 'Grade Code' },
          { name: 'company_id', required: true, label: 'Company' }
        ]
      },
      {
        tab: 'ranges',
        title: 'Monthly Salary Band Guardrails (BDT)',
        note: 'Minimum, midpoint, and maximum monthly gross compensation.',
        fields: [
          { name: 'range_min', required: true, label: 'Band Minimum (BDT)' },
          { name: 'range_mid', required: true, label: 'Band Midpoint (BDT)' },
          { name: 'range_max', required: true, label: 'Band Maximum (BDT)' },
          { name: 'currency_id', label: 'Currency' }
        ]
      }
    ]
  },

  'M57-form-succession': {
    kind: 'model_form',
    model: 'fix.succession.plan',
    title: 'Key Position Succession Plan',
    back: 'M57-succession',
    tabs: [
      { id: 'seat', label: 'Critical Role & Incumbent', bn: 'গুরুত্বপূর্ণ পদ ও বর্তমান কর্মী', icon: '🏢', badge: '4' },
      { id: 'readiness', label: 'Successor Readiness & Risk', bn: 'উত্তরসূরি প্রস্তুতি ও ঝুঁকি', icon: '🛡️', badge: '3' }
    ],
    sections: [
      {
        tab: 'seat',
        title: 'Critical Position & Incumbent',
        note: 'Key technical lead or branch manager position requiring succession coverage.',
        fields: [
          { name: 'position_name', required: true, label: 'Target Critical Position' },
          { name: 'incumbent_id', label: 'Current Incumbent' },
          { name: 'successor_id', required: true, label: 'Designated Successor' },
          { name: 'company_id', required: true, label: 'Company' }
        ]
      },
      {
        tab: 'readiness',
        title: 'Readiness Horizon & Flight Risk',
        note: 'Readiness timeline and retention risk assessment.',
        fields: [
          { name: 'readiness', required: true, label: 'Successor Readiness' },
          { name: 'risk', label: 'Vacancy / Flight Risk' },
          { name: 'notes', type: 'text', label: 'Development Action Notes' }
        ]
      }
    ]
  }
};

export const REPORT_ROUTES = {
  'M57:Rating Distribution': 'M57-rpt-ratings',
  'M57:Incentive Payout by Scheme': 'M57-rpt-payout',
  'M57:Technician Scorecards': 'M57-rpt-scorecards',
  'M57:Calibration Summary': 'M57-rpt-calib',
  'M57:PIP Outcomes': 'M57-rpt-pip'
};

export const FORM_MODELS = {
  'M57:Goal': 'fix.performance.goal',
  'M57:Review': 'fix.performance.review',
  'M57:Incentive Scheme': 'fix.incentive.run',
  'M57:Recognition': 'fix.performance.recognition'
};

export const FORM_CHIPS = {
  'M57:Goal': 'M57-form-goal',
  'M57:Review': 'M57-form-review',
  'M57:Incentive Scheme': 'M57-form-scheme',
  'M57:Recognition': 'M57-form-recognition',
  'M57:__by_model__': {
    'fix.performance.goal': 'M57-form-goal',
    'fix.performance.scorecard': 'M57-form-scorecard',
    'fix.performance.review': 'M57-form-review',
    'fix.performance.pip': 'M57-form-pip',
    'fix.incentive.run': 'M57-form-scheme',
    'fix.incentive.line': 'M57-form-calc',
    'fix.performance.recognition': 'M57-form-recognition',
    'fix.compensation.band': 'M57-form-comp',
    'fix.succession.plan': 'M57-form-succession',
    'fix.incentive.scheme': 'M57-form-scheme-def',
    'fix.incentive.scheme.version': 'M57-form-scheme-version',
    'fix.incentive.dispute': 'M57-form-dispute',
    'fix.incentive.clawback': 'M57-form-clawback',
    'fix.compensation.proposal': 'M57-form-proposal'
  },
  'M57:__by_screen__': {
    'M57-goals': 'M57-form-goal',
    'M57-kpis': 'M57-form-scorecard',
    'M57-reviews': 'M57-form-review',
    'M57-pips': 'M57-form-pip',
    'M57-schemes': 'M57-form-scheme',
    'M57-calc': 'M57-form-calc',
    'M57-recognition': 'M57-form-recognition',
    'M57-comp': 'M57-form-comp',
    'M57-succession': 'M57-form-succession',
    'M57-scheme-versions': 'M57-form-scheme-version',
    'M57-disputes': 'M57-form-dispute',
    'M57-clawbacks': 'M57-form-clawback',
    'M57-proposals': 'M57-form-proposal'
  }
};

export const CREATE = {
  M57: { screen: 'M57-form-goal', model: 'fix.performance.goal', label: 'Goal' }
};
