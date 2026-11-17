/** @odoo-module **/
/* A09 · People & Workforce — M57 Performance & Incentives.
 * Registry-faithful: 3 groups / 10 screens / 5 reports / 4 forms / freg 58.
 * A09 round 2 adds four screens: scheme versions, disputes, clawbacks and
 * compensation proposals. The capture audit (2026-11-17) adds KPI
 * definitions, review cycles, multi-source feedback, calibration sessions,
 * incentive adjustments and compensation cycles, and gives every sub-module
 * page a capture for each record it covers. */

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
      { id: 'M57-kpi-defs', en: 'KPI Definitions', bn: 'কেপিআই সংজ্ঞা', t: 'g' },
      { id: 'M57-kpis', en: 'Technician Scorecards', bn: 'টেকনিশিয়ান স্কোরকার্ড', t: 'g' },
      { id: 'M57-review-cycles', en: 'Review Cycle Set-Up', bn: 'পর্যালোচনা চক্র নির্ধারণ', t: 'g' },
      { id: 'M57-reviews', en: 'Reviews', bn: 'পর্যালোচনা', t: 'g' },
      { id: 'M57-feedback', en: 'Multi-Source Feedback', bn: 'বহুমুখী মতামত', t: 'g' },
      { id: 'M57-calibration-sessions', en: 'Calibration Sessions', bn: 'ক্যালিব্রেশন সভা', t: 'g' },
      { id: 'M57-calibration', en: 'Calibration Summary', bn: 'ক্যালিব্রেশন', t: 'r' },
      { id: 'M57-pips', en: 'PIPs', bn: 'কর্ম উন্নয়ন পরিকল্পনা', t: 'g' }
    ]},
    { en: 'Incentives', screens: [
      { id: 'M57-scheme-defs', en: 'Incentive Schemes', bn: 'প্রণোদনা কর্মসূচি', t: 'g' },
      { id: 'M57-scheme-versions', en: 'Scheme Versions & Approval', bn: 'কর্মসূচি সংস্করণ', t: 'g' },
      { id: 'M57-schemes', en: 'Calculation Runs', bn: 'হিসাব রান', t: 'g' },
      { id: 'M57-calc', en: 'Payout Lines', bn: 'প্রণোদনা লাইন', t: 'g' },
      { id: 'M57-adjustments', en: 'Incentive Adjustments', bn: 'প্রণোদনা সমন্বয়', t: 'g' },
      { id: 'M57-disputes', en: 'Incentive Disputes', bn: 'প্রণোদনা আপত্তি', t: 'g' },
      { id: 'M57-clawbacks', en: 'Clawbacks', bn: 'প্রণোদনা ফেরত', t: 'g' },
      { id: 'M57-recognition', en: 'Recognition', bn: 'স্বীকৃতি', t: 'g' }
    ]},
    { en: 'Compensation', screens: [
      { id: 'M57-comp-cycles', en: 'Compensation Review Cycles', bn: 'বেতন পর্যালোচনা চক্র', t: 'g' },
      { id: 'M57-comp', en: 'Salary Bands', bn: 'বেতন ব্যান্ড', t: 'g' },
      { id: 'M57-proposals', en: 'Compensation Proposals', bn: 'বেতন প্রস্তাব', t: 'g' },
      { id: 'M57-succession', en: 'Succession', bn: 'উত্তরসূরি', t: 'g' }
    ]}
  ],
  reports: ['Rating Distribution', 'Incentive Payout by Scheme', 'Technician Scorecards', 'Calibration Summary', 'PIP Outcomes'],
  forms: ['Goal', 'KPI Definition', 'Technician Scorecard', 'Review Cycle', 'Review', 'PIP',
    'Feedback Request', 'Calibration Session', 'Incentive Scheme', 'Scheme Version', 'Incentive Run',
    'Incentive Adjustment', 'Recognition', 'Compensation Cycle', 'Salary Band', 'Succession Plan'],
  cross: ['M21 Workforce', 'M56 Payroll', 'M01 Service Orders', 'M54 Costing'],
  freg: { src: 58, sub: [
    ['1', 'Goals & KPIs', 11, { model: 'fix.performance.goal', cols: ['name', 'employee_id', 'period', 'target_value', 'actual_value'], screens: ['M57-goals', 'M57-kpi-defs', 'M57-kpis'], reports: ['Technician Scorecards'], forms: ['Goal', 'KPI Definition', 'Technician Scorecard'] }],
    ['2', 'Review Cycles', 10, { model: 'fix.performance.review', create: 'M57-form-review-cycle', cols: ['name', 'employee_id', 'period', 'reviewer_id', 'cycle_id', 'state'], screens: ['M57-review-cycles', 'M57-reviews', 'M57-pips'], reports: ['PIP Outcomes', 'Rating Distribution'], forms: ['Review Cycle', 'Review', 'PIP'] }],
    ['3', 'Multi-Source Feedback', 6, { model: 'fix.performance.feedback', cols: ['name', 'employee_id', 'respondent_id', 'relationship', 'due_date', 'state'], screens: ['M57-feedback'], reports: [], forms: ['Feedback Request'] }],
    ['4', 'Rating & Calibration', 8, { model: 'fix.performance.review', create: 'M57-form-calibration', cols: ['employee_id', 'period', 'manager_rating', 'calibrated_rating', 'state'], screens: ['M57-calibration-sessions', 'M57-calibration'], reports: ['Rating Distribution', 'Calibration Summary'], forms: ['Calibration Session'] }],
    ['5', 'Incentive Design & Calculation', 12, { model: 'fix.incentive.line', create: 'M57-form-scheme-def', cols: ['run_id', 'employee_id', 'line_type', 'amount', 'applied_to_payslip'], screens: ['M57-scheme-defs', 'M57-scheme-versions', 'M57-schemes', 'M57-calc', 'M57-adjustments', 'M57-disputes', 'M57-clawbacks'], reports: ['Incentive Payout by Scheme'], forms: ['Incentive Scheme', 'Scheme Version', 'Incentive Run', 'Incentive Adjustment'] }],
    ['6', 'Recognition', 4, { model: 'fix.performance.recognition', cols: ['name', 'employee_id', 'award_type', 'awarded_on', 'prize_amount'], screens: ['M57-recognition'], reports: [], forms: ['Recognition'] }],
    ['7', 'Compensation Review', 7, { model: 'fix.compensation.band', create: 'M57-form-comp-cycle', cols: ['name', 'grade', 'range_min', 'range_mid', 'range_max'], screens: ['M57-comp-cycles', 'M57-comp', 'M57-proposals', 'M57-succession'], reports: [], forms: ['Compensation Cycle', 'Salary Band', 'Succession Plan'] }]
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
    cols: ['name', 'employee_id', 'reviewer_id', 'period', 'cycle_id', 'self_rating', 'manager_rating', 'calibrated_rating', 'feedback_count', 'approval_state', 'state'],
    actions: [{ m: 'action_start', l: 'Open Self-Assessment' },
              { m: 'action_record_self_rating', l: 'Record My Self Rating', ask: 'Your self rating, 1 to 5', kwarg: 'rating' },
              { m: 'action_submit_self_assessment', l: 'Submit Self-Assessment' },
              { m: 'action_record_manager_rating', l: 'Record Manager Rating', ask: 'Your rating of this report, 1 to 5', kwarg: 'rating' },
              { m: 'action_manager_review', l: 'Submit Manager Rating (to Calibration)' },
              { m: 'action_recall_calibration', l: 'Recall Calibration (manager)' },
              { m: 'action_close', l: 'Close' },
              { m: 'action_propose_compensation', l: 'Propose Compensation (line manager)', ask: 'Proposed monthly basic (BDT) and the justification, e.g. 32000 consistently exceeds targets', kwarg: 'proposal' }] },
  'M57-kpi-defs': { kind: 'model_list', model: 'fix.kpi.definition', stateField: 'state',
    cols: ['code', 'name', 'role_profile', 'measure', 'kind', 'target', 'threshold', 'version_no', 'date_from', 'date_to', 'state'],
    actions: [{ m: 'action_submit', l: 'Submit for Approval' },
              { m: 'action_approve', l: 'Approve (HR Manager, not the preparer)' },
              { m: 'action_reject', l: 'Reject', ask: 'Why it is rejected', kwarg: 'reason' },
              { m: 'action_retire', l: 'Retire From', ask: 'Retire from which date (YYYY-MM-DD, today or later)?', kwarg: 'retire_on' }] },
  'M57-review-cycles': { kind: 'model_list', model: 'fix.performance.review.cycle', stateField: 'state',
    cols: ['name', 'cycle_type', 'period', 'department_id', 'self_deadline', 'manager_deadline', 'calibration_deadline', 'review_count', 'closed_count', 'overdue_count', 'state'],
    actions: [{ m: 'action_open', l: 'Open Cycle (raise the reviews)' }, { m: 'action_close', l: 'Close Cycle' }] },
  'M57-feedback': { kind: 'model_list', model: 'fix.performance.feedback', stateField: 'state',
    cols: ['name', 'employee_id', 'period', 'respondent_id', 'relationship', 'due_date', 'rating', 'state'],
    actions: [{ m: 'action_submit_feedback', l: 'Give My Feedback (respondent)', ask: 'Your rating 1 to 5 and what it rests on, e.g. 4 solves hard faults quickly and helps juniors', kwarg: 'feedback' },
              { m: 'action_decline', l: 'Decline (respondent)', ask: 'Why you decline, e.g. I have not worked with them', kwarg: 'reason' }] },
  'M57-calibration-sessions': { kind: 'model_list', model: 'fix.performance.calibration.session', stateField: 'state',
    cols: ['name', 'period', 'cycle_id', 'session_date', 'pending_count', 'distribution_before', 'distribution_after', 'state'],
    actions: [{ m: 'action_start', l: 'Start Session (measure the distribution)' },
              { m: 'action_conclude', l: 'Conclude (apply the rating changes)' }] },
  'M57-scheme-defs': { kind: 'model_list', model: 'fix.incentive.scheme',
    cols: ['code', 'name', 'current_version_id', 'company_id'] },
  'M57-adjustments': { kind: 'model_list', model: 'fix.incentive.adjustment', stateField: 'state',
    cols: ['name', 'employee_id', 'period', 'adjustment_type', 'amount', 'reason', 'approval_state', 'applied_run_id', 'state'],
    actions: [{ m: 'action_request_approval', l: 'Request Approval (Incentive Approver)' },
              { m: 'action_recall_approval', l: 'Recall Approval' },
              { m: 'action_cancel', l: 'Cancel' }] },
  'M57-comp-cycles': { kind: 'model_list', model: 'fix.compensation.cycle', stateField: 'state',
    cols: ['name', 'date_from', 'date_to', 'budget', 'committed_amount', 'pending_amount', 'remaining_amount', 'guideline_pct', 'state'],
    actions: [{ m: 'action_open', l: 'Open Cycle' }, { m: 'action_close', l: 'Close Cycle' }] },
  'M57-calibration': { kind: 'table_report', module: 'M57', report: 'calibration_summary', title: 'Calibration Summary', period: true },
  'M57-pips': { kind: 'model_list', model: 'fix.performance.pip', stateField: 'state',
    cols: ['name', 'employee_id', 'start_date', 'end_date', 'outcome', 'state'],
    actions: [{ m: 'action_start', l: 'Start' }, { m: 'action_close', l: 'Close' }] },
  'M57-schemes': { kind: 'model_list', model: 'fix.incentive.run', stateField: 'state',
    cols: ['period', 'scheme_id', 'scheme_version_id', 'band_base', 'total', 'dispute_deadline', 'approval_state', 'state'],
    actions: [{ m: 'action_compute', l: 'Calculate Pool' }, { m: 'action_request_approval', l: 'Request Approval' },
              { m: 'action_recall_approval', l: 'Recall Approval' }, { m: 'action_reset_draft', l: 'Reset to Draft' }] },
  /* payout lines are calculated by the incentive run: nothing is typed in here */
  'M57-calc': { kind: 'model_list', model: 'fix.incentive.line', create: false,
    empty: 'No payout line calculated yet. Lines are produced when an incentive run is calculated from the approved scheme; they cannot be typed in.',
    cols: ['run_id', 'employee_id', 'line_type', 'gross_amount', 'proration_factor', 'amount', 'eligibility_note', 'adjustment_id', 'run_state', 'applied_to_payslip'],
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
    cols: ['name', 'employee_id', 'cycle_id', 'proposal_type', 'current_basic', 'proposed_basic', 'increase_pct', 'over_budget', 'effective_date', 'approval_state', 'state'],
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
  'M57-form-kpi': {
    kind: 'model_form',
    model: 'fix.kpi.definition',
    title: 'KPI Definition',
    back: 'M57-kpi-defs',
    status: { field: 'state', labels: {
      draft: 'Draft', submitted: 'Submitted', approved: 'Approved', rejected: 'Rejected' } },
    tabs: [
      { id: 'definition', label: 'Definition', bn: 'সংজ্ঞা', icon: '📐', badge: '5' },
      { id: 'target', label: 'Target & Effective Date', bn: 'লক্ষ্য ও কার্যকর তারিখ', icon: '🎯', badge: '7' },
      { id: 'approval', label: 'Version & Approval', bn: 'সংস্করণ ও অনুমোদন', icon: '🖋️', badge: '7' }
    ],
    sections: [
      {
        tab: 'definition',
        title: 'What Is Measured (FR-PIC-006)',
        note: 'A KPI is read from operational facts only (BRU-PIC-03): the measure names the fact and its source. The formula is written so the employee can follow it.',
        fields: [
          { name: 'code', required: true, label: 'Code' },
          { name: 'name', required: true, label: 'KPI Name' },
          { name: 'role_profile', required: true, label: 'Role Profile' },
          { name: 'measure', required: true, label: 'Measure' },
          { name: 'formula', required: true, type: 'text', label: 'How It Is Worked Out' }
        ]
      },
      {
        tab: 'target',
        title: 'Target, Threshold and Effective Date',
        note: 'Rates are percentages (0-100); jobs completed is a count. When higher is better the threshold is at or below the target, when lower is better at or above it. A replacement version takes effect from today or later.',
        fields: [
          { name: 'target', required: true, label: 'Target' },
          { name: 'threshold', required: true, label: 'Threshold (the least accepted)' },
          { name: 'date_from', required: true, label: 'Effective From' },
          { name: 'kind', readonly: true, label: 'Volume or Quality' },
          { name: 'unit', readonly: true, label: 'Unit' },
          { name: 'direction', readonly: true, label: 'Direction' },
          { name: 'source_module', readonly: true, label: 'Fact Source' }
        ]
      },
      {
        tab: 'approval',
        title: 'Versioned and Approved (T-01, BRU-PIC-04)',
        note: 'Approved by an HR Manager who neither prepared nor submitted it; approval closes the previous version the day before. A volume KPI is approved only with a quality KPI in force for the same role. An approved definition is frozen: a change is a new version.',
        fields: [
          { name: 'version_no', readonly: true, label: 'Version' },
          { name: 'date_to', readonly: true, label: 'Effective To' },
          { name: 'state', readonly: true, label: 'State' },
          { name: 'submitted_by_id', readonly: true, label: 'Submitted By' },
          { name: 'approved_by_id', readonly: true, label: 'Approved By' },
          { name: 'approved_at', readonly: true, label: 'Approved At' },
          { name: 'rejection_reason', readonly: true, type: 'text', label: 'Rejection Reason' }
        ]
      }
    ]
  },

  'M57-form-review-cycle': {
    kind: 'model_form',
    model: 'fix.performance.review.cycle',
    title: 'Review Cycle',
    back: 'M57-review-cycles',
    status: { field: 'state', labels: { draft: 'Draft', open: 'Open', closed: 'Closed' } },
    tabs: [
      { id: 'cycle', label: 'Cycle', bn: 'চক্র', icon: '🔄', badge: '4' },
      { id: 'population', label: 'Population', bn: 'অন্তর্ভুক্ত কর্মী', icon: '👥', badge: '3' },
      { id: 'deadlines', label: 'Stage Deadlines', bn: 'ধাপের সময়সীমা', icon: '📅', badge: '3' },
      { id: 'progress', label: 'Progress', bn: 'অগ্রগতি', icon: '📊', badge: '6' }
    ],
    sections: [
      {
        tab: 'cycle',
        title: 'Review Cycle (FR-PIC-016)',
        note: 'Set up by an HR Manager. Opening the cycle raises one review per employee of the population, each reviewed by their line manager.',
        fields: [
          { name: 'name', required: true, label: 'Cycle Name' },
          { name: 'cycle_type', required: true, label: 'Cycle Type' },
          { name: 'period', required: true, label: 'Period Covered (YYYY-MM, YYYY-Qn, YYYY-Hn or YYYY)' },
          { name: 'company_id', required: true, label: 'Company' }
        ]
      },
      {
        tab: 'population',
        title: 'Who Is Reviewed',
        note: 'Named employees, else the department, else the whole company. A probation cycle takes the employees whose probation ends by the date given (FR-PIC-017). Employees without a line manager are listed as not raised.',
        fields: [
          { name: 'department_id', label: 'Department' },
          { name: 'employee_ids', label: 'Named Employees' },
          { name: 'probation_until', label: 'Probation Ending By (probation cycles)' }
        ]
      },
      {
        tab: 'deadlines',
        title: 'Stage Deadlines (AUT-PIC-11)',
        note: 'In order. A daily job gives whoever holds an overdue stage a to-do, and their own manager one too.',
        fields: [
          { name: 'self_deadline', required: true, label: 'Self-Assessment Due' },
          { name: 'manager_deadline', required: true, label: 'Manager Assessment Due' },
          { name: 'calibration_deadline', required: true, label: 'Calibration Due' }
        ]
      },
      {
        tab: 'progress',
        title: 'Progress',
        note: 'A cycle closes when every review in it is closed.',
        fields: [
          { name: 'state', readonly: true, label: 'State' },
          { name: 'review_count', readonly: true, label: 'Reviews Raised' },
          { name: 'closed_count', readonly: true, label: 'Reviews Closed' },
          { name: 'overdue_count', readonly: true, label: 'Reviews Overdue' },
          { name: 'skipped_note', readonly: true, type: 'text', label: 'Not Raised' },
          { name: 'opened_by_id', readonly: true, label: 'Opened By' }
        ]
      }
    ]
  },

  'M57-form-feedback': {
    kind: 'model_form',
    model: 'fix.performance.feedback',
    title: 'Feedback Request',
    back: 'M57-feedback',
    status: { field: 'state', labels: { requested: 'Requested', submitted: 'Submitted', declined: 'Declined' } },
    tabs: [
      { id: 'request', label: 'Request', bn: 'অনুরোধ', icon: '✉️', badge: '4' },
      { id: 'answer', label: 'Answer', bn: 'উত্তর', icon: '💬', badge: '6' }
    ],
    sections: [
      {
        tab: 'request',
        title: 'Who Is Asked About Whom (FR-PIC-020)',
        note: 'Requested by HR on a review that is not yet calibrated. The respondent is neither the employee nor their line manager. The employee never sees who said what: the review shows only the count and the average.',
        fields: [
          { name: 'review_id', required: true, label: 'Review' },
          { name: 'respondent_id', required: true, label: 'Respondent' },
          { name: 'relationship', required: true, label: 'Relationship to the Employee' },
          { name: 'due_date', label: 'Answer By' }
        ]
      },
      {
        tab: 'answer',
        title: 'The Respondent\'s Answer',
        note: 'Only the respondent answers, with Give My Feedback or Decline on the list. An answer is final.',
        fields: [
          { name: 'state', readonly: true, label: 'State' },
          { name: 'rating', readonly: true, label: 'Rating (1-5)' },
          { name: 'strengths', readonly: true, type: 'text', label: 'Comments' },
          { name: 'improvements', readonly: true, type: 'text', label: 'To Improve' },
          { name: 'decline_reason', readonly: true, type: 'text', label: 'Why Declined' },
          { name: 'submitted_at', readonly: true, label: 'Answered At' }
        ]
      }
    ]
  },

  'M57-form-calibration': {
    kind: 'model_form',
    model: 'fix.performance.calibration.session',
    title: 'Calibration Session',
    back: 'M57-calibration-sessions',
    status: { field: 'state', labels: { draft: 'Draft', in_session: 'In Session', concluded: 'Concluded' } },
    tabs: [
      { id: 'session', label: 'Session', bn: 'সভা', icon: '⚖️', badge: '6' },
      { id: 'outcome', label: 'Distribution & Outcome', bn: 'বণ্টন ও ফলাফল', icon: '📊', badge: '6' }
    ],
    lines: { field: 'line_ids', title: 'Rating Changes (added once the session has started)',
      note: 'Each change names the review, the calibrated rating and why. Only a calibrated, not yet closed rating moves. The changes are applied when the session is concluded.',
      fields: [
        { name: 'review_id', label: 'Review', required: true },
        { name: 'manager_rating', label: 'Manager Rating', readonly: true },
        { name: 'new_rating', label: 'Calibrated Rating (1-5)', required: true },
        { name: 'reason', label: 'Why', required: true }
      ] },
    sections: [
      {
        tab: 'session',
        title: 'Ratings Compared Across Managers (FR-PIC-021, BRU-PIC-13)',
        note: 'Opened by HR or a Performance Calibrator for one review period (and cycle). While a session over a period is open, no review of that period is closed.',
        fields: [
          { name: 'period', required: true, label: 'Review Period' },
          { name: 'cycle_id', label: 'Review Cycle' },
          { name: 'scope', label: 'Teams or Branches Compared' },
          { name: 'session_date', required: true, label: 'Session Date' },
          { name: 'participant_ids', label: 'Managers Taking Part' },
          { name: 'company_id', required: true, label: 'Company' }
        ]
      },
      {
        tab: 'outcome',
        title: 'Before and After',
        note: 'The distribution before is measured from the managers\' ratings when the session starts; the distribution after from the calibrated ratings when it concludes. Concluding needs every rating in scope calibrated, and is done by someone who neither gave nor received a changed rating.',
        fields: [
          { name: 'pending_count', readonly: true, label: 'Ratings Still Awaiting Calibration' },
          { name: 'distribution_before', readonly: true, label: 'Distribution Before' },
          { name: 'distribution_after', readonly: true, label: 'Distribution After' },
          { name: 'minutes', type: 'text', label: 'Minutes' },
          { name: 'state', readonly: true, label: 'State' },
          { name: 'concluded_by_id', readonly: true, label: 'Concluded By' }
        ]
      }
    ]
  },

  'M57-form-adjustment': {
    kind: 'model_form',
    model: 'fix.incentive.adjustment',
    title: 'Incentive Adjustment',
    back: 'M57-adjustments',
    status: { field: 'state', labels: {
      draft: 'Draft', approved: 'Approved', applied: 'Applied', rejected: 'Rejected', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'change', label: 'The Change', bn: 'পরিবর্তন', icon: '✏️', badge: '7' },
      { id: 'approval', label: 'Approval & Application', bn: 'অনুমোদন ও প্রয়োগ', icon: '🖋️', badge: '6' }
    ],
    sections: [
      {
        tab: 'change',
        title: 'Reason and Evidence (BRU-PIC-10/11)',
        note: 'Raised by an Incentive Officer, never for their own pay, for a period whose run is not approved (an approved period is locked: adjust a later one). A reversal of a fraudulent or invalid job is negative and names its evidence. The reason is shown to the employee on their incentive line.',
        fields: [
          { name: 'employee_id', required: true, label: 'Employee' },
          { name: 'period', required: true, label: 'Paid In Period (YYYY-MM)' },
          { name: 'adjustment_type', required: true, label: 'Type' },
          { name: 'amount', required: true, label: 'Amount (BDT; negative recovers)' },
          { name: 'reason', required: true, type: 'text', label: 'Reason' },
          { name: 'evidence_ref', label: 'Evidence' },
          { name: 'service_order_id', label: 'Service Order' }
        ]
      },
      {
        tab: 'approval',
        title: 'Routed to the Incentive Approver',
        note: 'Approved by an Incentive Approver who neither raised it nor is its subject; the employee is told when it is approved. It becomes a line of the period\'s run when the run is computed (reset and recompute a computed run). Nobody\'s incentive in a run goes below zero.',
        fields: [
          { name: 'state', readonly: true, label: 'State' },
          { name: 'approval_state', readonly: true, label: 'Approval' },
          { name: 'approved_by_id', readonly: true, label: 'Approved By' },
          { name: 'approved_at', readonly: true, label: 'Approved At' },
          { name: 'applied_run_id', readonly: true, label: 'Applied In Run' },
          { name: 'applied_line_id', readonly: true, label: 'Applied Line' }
        ]
      }
    ]
  },

  'M57-form-comp-cycle': {
    kind: 'model_form',
    model: 'fix.compensation.cycle',
    title: 'Compensation Review Cycle',
    back: 'M57-comp-cycles',
    status: { field: 'state', labels: { draft: 'Draft', open: 'Open', closed: 'Closed' } },
    tabs: [
      { id: 'cycle', label: 'Window & Budget', bn: 'সময়সীমা ও বাজেট', icon: '💼', badge: '6' },
      { id: 'spend', label: 'Spend Against Budget', bn: 'বাজেট ব্যবহার', icon: '📊', badge: '5' }
    ],
    sections: [
      {
        tab: 'cycle',
        title: 'Salary Review Cycle (FR-PIC-038)',
        note: 'Set up and opened by the Compensation Manager. A proposal whose raise takes effect inside the window belongs to the cycle. The window and budget are fixed once open.',
        fields: [
          { name: 'name', required: true, label: 'Cycle Name' },
          { name: 'date_from', required: true, label: 'Raises Effective From' },
          { name: 'date_to', required: true, label: 'Raises Effective To' },
          { name: 'budget', required: true, label: 'Monthly Increase Budget (BDT)' },
          { name: 'guideline_pct', label: 'Guideline Increase %' },
          { name: 'guidelines', type: 'text', label: 'Guidelines for Managers' }
        ]
      },
      {
        tab: 'spend',
        title: 'Budget Guardrail (BRU-PIC-17)',
        note: 'A proposal that would take the approved increases over the budget is routed to the CFO, and only the CFO approves it.',
        fields: [
          { name: 'committed_amount', readonly: true, label: 'Approved Increases (BDT / month)' },
          { name: 'pending_amount', readonly: true, label: 'Awaiting Decision (BDT / month)' },
          { name: 'remaining_amount', readonly: true, label: 'Budget Remaining (BDT / month)' },
          { name: 'state', readonly: true, label: 'State' },
          { name: 'opened_by_id', readonly: true, label: 'Opened By' }
        ]
      }
    ]
  },

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
          { name: 'period', required: true, label: 'Review Period' },
          { name: 'cycle_id', readonly: true, label: 'Raised by Cycle' }
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
          { name: 'closed_by_id', readonly: true, label: 'Closed By' },
          { name: 'feedback_count', readonly: true, label: 'Multi-Source Feedback Received' },
          { name: 'feedback_avg', readonly: true, label: 'Feedback Average (1-5, respondents not named)' }
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
      { id: 'salvage', label: 'Salvage & 30d Rework Clawback', bn: 'সালভেজ ও রিওয়ার্ক জরিমানা', icon: '♻️', badge: '5' },
      { id: 'kpi', label: 'KPI Attainment', bn: 'কেপিআই অর্জন', icon: '🎯', badge: '2' }
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
      },
      {
        tab: 'kpi',
        title: 'Against the Approved KPI Definitions (FR-PIC-006/012)',
        note: 'Each KPI definition approved for field technicians and in force at the period end, with this scorecard\'s value against its target and threshold. The definitions do not change the composite or the pay: those are the approved scheme\'s.',
        fields: [
          { name: 'kpi_attainment', readonly: true, type: 'text', label: 'Value Against Target and Threshold' },
          { name: 'kpi_breaches', readonly: true, label: 'KPIs Below Threshold' }
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
    /* a payout line is calculated by its incentive run (2026-11-12) */
    create: false, pick: 'A payout line is calculated by its incentive run: open one from Calculation Runs.',
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
          { name: 'adjustment_id', readonly: true, label: 'Approved Adjustment' },
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
    back: 'M57-scheme-defs',
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
    create: false, pick: 'A dispute is raised from its payout line: open one from Incentive Disputes.',
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
    create: false, pick: 'A clawback is raised by its trigger (a rework or a reversal): open one from Clawbacks.',
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
    create: false, pick: 'A compensation proposal is raised in the review cycle: open one from Compensation Proposals.',
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
          { name: 'justification', readonly: true, type: 'text', label: 'Justification' },
          { name: 'cycle_id', readonly: true, label: 'Compensation Cycle' },
          { name: 'over_budget', readonly: true, label: 'Over the Cycle Budget (the CFO decides)' }
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
    title: 'Salary Band',
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
  'M57:KPI Definition': 'fix.kpi.definition',
  'M57:Technician Scorecard': 'fix.performance.scorecard',
  'M57:Review Cycle': 'fix.performance.review.cycle',
  'M57:Review': 'fix.performance.review',
  'M57:PIP': 'fix.performance.pip',
  'M57:Feedback Request': 'fix.performance.feedback',
  'M57:Calibration Session': 'fix.performance.calibration.session',
  'M57:Incentive Scheme': 'fix.incentive.scheme',
  'M57:Scheme Version': 'fix.incentive.scheme.version',
  'M57:Incentive Run': 'fix.incentive.run',
  'M57:Incentive Adjustment': 'fix.incentive.adjustment',
  'M57:Recognition': 'fix.performance.recognition',
  'M57:Compensation Cycle': 'fix.compensation.cycle',
  'M57:Salary Band': 'fix.compensation.band',
  'M57:Succession Plan': 'fix.succession.plan'
};

export const FORM_CHIPS = {
  'M57:Goal': 'M57-form-goal',
  'M57:KPI Definition': 'M57-form-kpi',
  'M57:Technician Scorecard': 'M57-form-scorecard',
  'M57:Review Cycle': 'M57-form-review-cycle',
  'M57:Review': 'M57-form-review',
  'M57:PIP': 'M57-form-pip',
  'M57:Feedback Request': 'M57-form-feedback',
  'M57:Calibration Session': 'M57-form-calibration',
  'M57:Incentive Scheme': 'M57-form-scheme-def',
  'M57:Scheme Version': 'M57-form-scheme-version',
  'M57:Incentive Run': 'M57-form-scheme',
  'M57:Incentive Adjustment': 'M57-form-adjustment',
  'M57:Recognition': 'M57-form-recognition',
  'M57:Compensation Cycle': 'M57-form-comp-cycle',
  'M57:Salary Band': 'M57-form-comp',
  'M57:Succession Plan': 'M57-form-succession',
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
    'fix.compensation.proposal': 'M57-form-proposal',
    'fix.kpi.definition': 'M57-form-kpi',
    'fix.performance.review.cycle': 'M57-form-review-cycle',
    'fix.performance.feedback': 'M57-form-feedback',
    'fix.performance.calibration.session': 'M57-form-calibration',
    'fix.incentive.adjustment': 'M57-form-adjustment',
    'fix.compensation.cycle': 'M57-form-comp-cycle'
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
    'M57-proposals': 'M57-form-proposal',
    'M57-kpi-defs': 'M57-form-kpi',
    'M57-review-cycles': 'M57-form-review-cycle',
    'M57-feedback': 'M57-form-feedback',
    'M57-calibration-sessions': 'M57-form-calibration',
    'M57-scheme-defs': 'M57-form-scheme-def',
    'M57-adjustments': 'M57-form-adjustment',
    'M57-comp-cycles': 'M57-form-comp-cycle'
  }
};

export const CREATE = {
  M57: { screen: 'M57-form-goal', model: 'fix.performance.goal', label: 'Goal' }
};
