/** @odoo-module **/
/* A09 · People & Workforce — M57 Performance & Incentives.
 * Registry-faithful: 3 groups / 10 screens / 5 reports / 4 forms / freg 58. */

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
      { id: 'M57-calc', en: 'Calculation Runs', bn: 'হিসাব রান', t: 'g' },
      { id: 'M57-recognition', en: 'Recognition', bn: 'স্বীকৃতি', t: 'g' }
    ]},
    { en: 'Compensation', screens: [
      { id: 'M57-comp', en: 'Compensation Review', bn: 'বেতন পর্যালোচনা', t: 'g' },
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
    ['5', 'Incentive Design & Calculation', 12, { model: 'fix.incentive.line', cols: ['run_id', 'employee_id', 'scorecard_id', 'amount', 'applied_to_payslip'], screens: ['M57-schemes', 'M57-calc'] }],
    ['6', 'Recognition', 4, { model: 'fix.performance.recognition', cols: ['name', 'employee_id', 'award_type', 'awarded_on', 'prize_amount'], screens: ['M57-recognition'] }],
    ['7', 'Compensation Review', 7, { model: 'fix.compensation.band', cols: ['name', 'grade', 'range_min', 'range_mid', 'range_max'], screens: ['M57-comp', 'M57-succession'] }]
  ] }
};

export const SCREENS = {
  'M57-goals': { kind: 'model_list', model: 'fix.performance.goal', stateField: 'state',
    cols: ['name', 'employee_id', 'parent_goal_id', 'period', 'weight', 'target_value', 'actual_value', 'state'],
    actions: [{ m: 'action_activate', l: 'Activate' }, { m: 'action_close', l: 'Close' }] },
  'M57-kpis': { kind: 'model_list', create: false, model: 'fix.performance.scorecard',
    cols: ['employee_id', 'period', 'first_time_fix', 'sla_hit', 'csat', 'salvage_ratio', 'rework_30d_rate', 'rework_rate', 'score'],
    actions: [{ m: 'action_publish', l: 'Publish Scorecard' }] },
  'M57-reviews': { kind: 'model_list', model: 'fix.performance.review', stateField: 'state',
    cols: ['name', 'employee_id', 'period', 'manager_rating', 'calibrated_rating', 'state'],
    actions: [{ m: 'action_manager_review', l: 'Manager Review' }, { m: 'action_calibrate', l: 'Calibrate' },
              { m: 'action_close', l: 'Close' }] },
  'M57-calibration': { kind: 'table_report', module: 'M57', report: 'calibration_summary', title: 'Calibration Summary', period: true },
  'M57-pips': { kind: 'model_list', model: 'fix.performance.pip', stateField: 'state',
    cols: ['name', 'employee_id', 'start_date', 'end_date', 'outcome', 'state'],
    actions: [{ m: 'action_start', l: 'Start' }, { m: 'action_close', l: 'Close' }] },
  'M57-schemes': { kind: 'model_list', model: 'fix.incentive.run', stateField: 'state',
    cols: ['period', 'band_base', 'total', 'state'],
    actions: [{ m: 'action_compute', l: 'Calculate Pool' }, { m: 'action_apply', l: 'Apply to Payroll (M56)' }] },
  'M57-calc': { kind: 'model_list', model: 'fix.incentive.line',
    cols: ['run_id', 'employee_id', 'scorecard_id', 'amount', 'applied_to_payslip'] },
  'M57-recognition': { kind: 'model_list', model: 'fix.performance.recognition',
    cols: ['name', 'employee_id', 'award_type', 'awarded_on', 'prize_amount', 'citation'] },
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
        note: '0–100% weightage across technician scorecards.',
        fields: [
          { name: 'weight', required: true, label: 'Weightage (%)' },
          { name: 'target_value', label: 'Target Value' },
          { name: 'actual_value', label: 'Actual Achieved Value' },
          { name: 'unit', label: 'Measurement Unit' },
          { name: 'state', required: true, label: 'State' }
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
          { name: 'reviewer_id', label: 'Appraising Manager' },
          { name: 'period', required: true, label: 'Review Period' }
        ]
      },
      {
        tab: 'scoring',
        title: 'Multi-Rater Evaluation Ratings (1–5 Scale)',
        note: 'Manager review requires rating; calibration aligns across technical peer groups.',
        fields: [
          { name: 'self_rating', label: 'Self Evaluation (1-5)' },
          { name: 'manager_rating', label: 'Manager Evaluation (1-5)' },
          { name: 'calibrated_rating', label: 'Calibrated Final Rating (1-5)' },
          { name: 'state', required: true, label: 'Review State' }
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
      draft: 'Draft', active: 'Active', passed: 'Passed', extended: 'Extended', failed: 'Failed' } },
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
          { name: 'state', required: true, label: 'PIP Outcome State' }
        ]
      }
    ]
  },

  'M57-form-recognition': {
    kind: 'model_form',
    model: 'fix.performance.recognition',
    title: 'Spot Recognition',
    back: 'M57-recognition',
    tabs: [
      { id: 'award', label: 'Award Particulars', bn: 'পুরস্কারের বিবরণ', icon: '🏆', badge: '4' },
      { id: 'citation', label: 'Merit Citation', bn: 'প্রশংসাপত্র', icon: '📜', badge: '1' }
    ],
    sections: [
      {
        tab: 'award',
        title: 'Recognition Category & Token',
        note: 'Technician of the Month, Customer Delight, First-Time-Fix Champion award.',
        fields: [
          { name: 'employee_id', required: true, label: 'Employee' },
          { name: 'award_type', required: true, label: 'Recognition Category' },
          { name: 'awarded_on', required: true, label: 'Award Date' },
          { name: 'prize_amount', label: 'Cash / Voucher Prize (BDT)' }
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
        note: 'Normalized 0.0–1.0 ratios driving the reachable 1.00 composite score.',
        fields: [
          { name: 'first_time_fix', label: 'First-Time Fix Ratio (0.0 - 1.0)' },
          { name: 'sla_hit', label: 'SLA Compliance Ratio (0.0 - 1.0)' },
          { name: 'csat', label: 'Customer Satisfaction Ratio (0.0 - 1.0)' },
          { name: 'score', label: 'Computed Composite Score (0.0 - 1.0)' }
        ]
      },
      {
        tab: 'salvage',
        title: 'Component Salvage Recovery (15%) & 30-Day Rework Clawback',
        note: 'Board-level salvage value vs target, and 30-day repeat repair penalty ramp above 3% threshold.',
        fields: [
          { name: 'salvage_value', label: 'Actual Salvaged Parts Value (BDT)' },
          { name: 'salvage_target', label: 'Monthly Salvage Target (BDT)' },
          { name: 'salvage_ratio', label: 'Salvage Achievement Ratio (0.0 - 1.0)' },
          { name: 'rework_30d_rate', label: '30-Day Repeat Repair Rate (0.0 - 1.0)' },
          { name: 'rework_rate', label: 'General Rework Rate (0.0 - 1.0)' }
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
      draft: 'Draft', calculated: 'Calculated', approved: 'Approved', paid: 'Applied to Payroll' } },
    tabs: [
      { id: 'pool', label: 'Scheme Pool & Period', bn: 'প্রণোদনা তহবিল ও সময়কাল', icon: '💰', badge: '4' },
      { id: 'status', label: 'Payroll Sync & State', bn: 'বেতন সমন্বয় ও অবস্থা', icon: '⚙️', badge: '2' }
    ],
    sections: [
      {
        tab: 'pool',
        title: 'Incentive Scheme Pool Parameters',
        note: 'Monthly technician incentive pool calculation (15% / 10% / 5% / 0% score bands).',
        fields: [
          { name: 'period', required: true, label: 'Payroll Period (YYYY-MM)' },
          { name: 'band_base', required: true, label: 'Scheme Band Base Amount (BDT)' },
          { name: 'total', label: 'Total Computed Pool Payout (BDT)' },
          { name: 'company_id', label: 'Company' }
        ]
      },
      {
        tab: 'status',
        title: 'Governance & M56 Payslip Push Status',
        note: 'Applying the run pushes incentive line amounts directly to M56 payslips.',
        fields: [
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'state', required: true, label: 'Run State' }
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
        note: 'Computed from technician composite scorecard band.',
        fields: [
          { name: 'run_id', required: true, label: 'Incentive Run' },
          { name: 'employee_id', required: true, label: 'Technician / Employee' },
          { name: 'scorecard_id', required: true, label: 'Source Scorecard' },
          { name: 'amount', label: 'Incentive Payout Amount (BDT)' }
        ]
      },
      {
        tab: 'payroll',
        title: 'M56 Payroll Integration Trace',
        note: 'Tracks idempotent push to the employee monthly payslip.',
        fields: [
          { name: 'applied_to_payslip', label: 'Applied to M56 Payslip' },
          { name: 'payslip_ref_id', label: 'Linked Payslip Record ID' }
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
    'fix.succession.plan': 'M57-form-succession'
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
    'M57-succession': 'M57-form-succession'
  }
};

export const CREATE = {
  M57: { screen: 'M57-form-goal', model: 'fix.performance.goal', label: 'Goal' }
};
