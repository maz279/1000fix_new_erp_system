/** @odoo-module **/
/* A09 · People & Workforce — M56 Payroll & Statutory.
 * Registry-faithful: 4 groups / 12 screens / 5 reports / 4 forms / freg 82. */

export const MODULE = {
  area: 'A09', code: 'M56', en: 'Payroll & Statutory', title: 'M56 · Payroll & Statutory',
  bn: 'বেতন ও বিধিবদ্ধ', icon: '💵',
  desc: 'BD gross-to-net engine, income tax AY 2026-27, provident fund, gratuity, festival bonus, BEFTN bank files, payslips and certificates, quarterly withholding returns and final settlements.',
  kpis: [
    { l: 'Payroll Cycle', m: 'payroll_cycle' },
    { l: 'Gross Payroll', m: 'gross_payroll', prefix: '৳ ' },
    { l: 'Payslips', m: 'run_duration' },
    { l: 'Corrections', m: 'corrections' },
    { l: 'Tax Withheld MTD', m: 'tax_withheld_mtd', prefix: '৳ ' },
    { l: 'Bonus Accrued', m: 'festival_bonus_accrued', prefix: '৳ ' }
  ],
  groups: [
    {
      en: 'Payroll Engine', screens: [
        { id: 'M56-runs', en: 'Payroll Runs', bn: 'বেতন রান', t: 'g' },
        { id: 'M56-structures', en: 'Salary Structures', bn: 'বেতন কাঠামো', t: 'g' },
        { id: 'M56-payslips', en: 'Payslips', bn: 'বেতন পত্র', t: 'g' },
        { id: 'M56-offcycle', en: 'Off-Cycle Payments', bn: 'অফ-সাইকেল', t: 'g' }
      ]
    },
    {
      en: 'Statutory', screens: [
        { id: 'M56-tax', en: 'Income Tax (AY 2026-27)', bn: 'আয়কর', t: 'r' },
        { id: 'M56-pf', en: 'Provident Fund', bn: 'প্রভিডেন্ট ফান্ড', t: 'r' },
        { id: 'M56-gratuity', en: 'Gratuity & Encashment', bn: 'গ্র্যাচুইটি', t: 'r' },
        { id: 'M56-bonus', en: 'Festival Bonus', bn: 'উৎসব বোনাস', t: 'g' }
      ]
    },
    {
      en: 'Disbursement', screens: [
        { id: 'M56-beftn', en: 'BEFTN Bank Files', bn: 'বিইএফটিএন', t: 'g' },
        { id: 'M56-certificates', en: 'Certificates & Tax Statements', bn: 'সনদ', t: 'g' }
      ]
    },
    {
      en: 'Compliance', screens: [
        { id: 'M56-returns', en: 'Withholding Returns (Quarterly)', bn: 'উৎসে কর রিটার্ন', t: 'g' },
        { id: 'M56-settlement', en: 'Final Settlements', bn: 'চূড়ান্ত নিষ্পত্তি', t: 'g' },
        { id: 'M56-wppf', en: 'WPPF Profit Sharing (BLA Ch. XV)', bn: 'ডব্লিউপিপিএফ মুনাফা অংশগ্রহণ', t: 'g' }
      ]
    }
  ],
  reports: ['Salary Register', 'Payroll Cost Allocation', 'Tax Deduction Summary', 'PF & Gratuity Provisions', 'Payroll Variance'],
  forms: ['Salary Structure', 'Payroll Run', 'Bonus Run', 'Final Settlement'],
  cross: ['M21 Workforce', 'M55 Attendance', 'M19 General Ledger', 'M51 TDS', 'M50 Treasury'],
  freg: {
    src: 82, sub: [
      ['1', 'Gross-to-Net Engine', 14, { model: 'fix.payslip', cols: ['period_id', 'employee_id', 'gross', 'tax_withheld', 'net'], screens: ['M56-payslips', 'M56-structures'] }],
      ['2', 'BD Income Tax', 12, { model: 'fix.payslip', cols: ['employee_id', 'period_id', 'taxpayer_category', 'annual_taxable_other', 'tax_withheld'], screens: ['M56-tax'] }],
      ['3', 'Provident Fund', 7, { model: 'fix.payslip', cols: ['employee_id', 'period_id', 'basic', 'pf_employee', 'pf_employer'], screens: ['M56-pf'] }],
      ['4', 'Gratuity', 7, { model: 'fix.payslip', cols: ['employee_id', 'period_id', 'completed_years', 'basic', 'gratuity_amount'], screens: ['M56-gratuity'] }],
      ['5', 'Bonus & Encashment', 7, { model: 'fix.payroll.bonus.run', cols: ['name', 'festival', 'bonus_date', 'total_amount', 'state'], screens: ['M56-bonus', 'M56-wppf'] }],
      ['6', 'Loans & Advances', 6, { model: 'fix.payroll.offcycle', cols: ['name', 'employee_id', 'payment_date', 'amount', 'state'], screens: ['M56-offcycle'], domain: [['payment_type', '=', 'advance']] }],
      ['7', 'Runs & Off-Cycle', 9, { model: 'fix.payroll.period', cols: ['name', 'period_start', 'period_end', 'calculator_id', 'state'], screens: ['M56-runs', 'M56-offcycle'] }],
      ['8', 'BEFTN & Payslips', 8, { model: 'fix.beftn.batch', cols: ['period_id', 'settlement_date', 'employee_count', 'total_amount', 'state'], screens: ['M56-beftn', 'M56-payslips'] }],
      ['9', 'Returns & Certificates', 7, { model: 'fix.payroll.return', cols: ['name', 'period', 'total_tax', 'challan_number', 'state'], screens: ['M56-returns', 'M56-certificates'] }],
      ['10', 'Final Settlement', 5, { model: 'fix.payroll.offcycle', cols: ['name', 'employee_id', 'payment_date', 'amount', 'state'], screens: ['M56-settlement'], domain: [['payment_type', '=', 'settlement']] }]
    ]
  }
};

export const SCREENS = {
  'M56-runs': {
    kind: 'model_list', model: 'fix.payroll.period', stateField: 'state',
    cols: ['name', 'period_start', 'period_end', 'slip_count', 'gross_total', 'tax_total', 'net_total', 'state'],
    actions: [{ m: 'action_verify_attendance_locked', l: 'Verify Attendance Lock (M55)' }, { m: 'action_calculate', l: 'Calculate Gross-to-Net' }, { m: 'action_approve', l: 'Approve' }, { m: 'action_pay', l: 'Mark Paid' }, { m: 'action_post', l: 'Post to GL (M19)' }]
  },
  'M56-structures': {
    kind: 'model_list', model: 'fix.payroll.structure',
    cols: ['name', 'grade', 'basic_pct', 'house_rent_pct', 'transport_fixed', 'medical_fixed', 'pf_applicable', 'active']
  },
  'M56-payslips': {
    kind: 'model_list', create: false, model: 'fix.payslip',
    cols: ['period_id', 'employee_id', 'basic', 'house_rent', 'medical_allowance', 'conveyance_allowance', 'technical_allowance', 'overtime', 'incentive', 'gross', 'tax_withheld', 'pf_employee', 'net'],
    actions: [{ m: 'action_compute_separation', l: 'Compute Separation' }, { m: 'action_compute_retrenchment', l: 'Compute Retrenchment' }]
  },
  'M56-offcycle': {
    kind: 'model_list', model: 'fix.payroll.offcycle', stateField: 'state',
    cols: ['name', 'employee_id', 'payment_type', 'payment_date', 'amount', 'state'],
    actions: [{ m: 'action_approve', l: 'Approve' }, { m: 'action_pay', l: 'Pay' }]
  },
  'M56-tax': { kind: 'table_report', module: 'M56', report: 'tax_deduction_summary', title: 'Income Tax (AY 2026-27)', period: true },
  'M56-pf': { kind: 'table_report', module: 'M56', report: 'pf_gratuity', title: 'Provident Fund', period: true },
  'M56-gratuity': { kind: 'table_report', module: 'M56', report: 'pf_gratuity', title: 'Gratuity & Encashment', period: true },
  'M56-bonus': {
    kind: 'model_list', model: 'fix.payroll.bonus.run', stateField: 'state',
    cols: ['name', 'festival', 'bonus_date', 'basis', 'multiplier', 'employee_count', 'total_amount', 'state'],
    actions: [{ m: 'action_approve', l: 'Approve' }, { m: 'action_pay', l: 'Pay' }]
  },
  'M56-beftn': {
    kind: 'model_list', create: false, model: 'fix.beftn.batch', stateField: 'state',
    cols: ['period_id', 'settlement_date', 'employee_count', 'total_amount', 'file_name', 'state'],
    actions: [{ m: 'action_generate_beftn_file', l: 'Generate File' }, { m: 'action_settle', l: 'Settle' }]
  },
  'M56-certificates': {
    kind: 'model_list', model: 'fix.payroll.certificate', stateField: 'state',
    cols: ['name', 'employee_id', 'certificate_type', 'fiscal_year', 'issued_on', 'amount', 'total_tax_withheld', 'reference', 'state'],
    actions: [{ m: 'action_compute_from_payslips', l: 'Compute from Payslips' }, { m: 'action_issue', l: 'Issue Certificate' }]
  },
  'M56-returns': {
    kind: 'model_list', model: 'fix.payroll.return', stateField: 'state',
    cols: ['name', 'period', 'employee_count', 'total_tax', 'challan_number', 'filed_on', 'acknowledgement', 'state'],
    actions: [{ m: 'action_reconcile_payslips', l: 'Reconcile Payslips' }, { m: 'action_file', l: 'File Return' }]
  },
  'M56-settlement': {
    kind: 'model_list', model: 'fix.payroll.offcycle', stateField: 'state',
    cols: ['name', 'employee_id', 'payment_date', 'amount', 'reason', 'state']
  },
  'M56-wppf': {
    kind: 'model_list', model: 'fix.wppf.allocation', stateField: 'state',
    cols: ['name', 'fiscal_year', 'net_profit', 'total_wppf_pool', 'participatory_fund_amount', 'welfare_fund_amount', 'welfare_foundation_amount', 'eligible_workers_count', 'state'],
    actions: [{ m: 'action_calculate', l: 'Calculate 80:10:10 Split' }, { m: 'action_approve', l: 'Trustee Approve' }, { m: 'action_post', l: 'Disburse & Post' }]
  },

  /* Report chips -> their own computed pack */
  'M56-rpt-register': { kind: 'table_report', module: 'M56', report: 'salary_register', title: 'Salary Register', period: true },
  'M56-rpt-alloc': { kind: 'table_report', module: 'M56', report: 'payroll_cost_allocation', title: 'Payroll Cost Allocation', period: true },
  'M56-rpt-tax': { kind: 'table_report', module: 'M56', report: 'tax_deduction_summary', title: 'Tax Deduction Summary', period: true },
  'M56-rpt-pf': { kind: 'table_report', module: 'M56', report: 'pf_gratuity', title: 'PF & Gratuity Provisions', period: true },
  'M56-rpt-variance': { kind: 'table_report', module: 'M56', report: 'payroll_variance', title: 'Payroll Variance', period: true },

  /* ============ D365 IN-WORKSPACE FORMS ============ */
  'M56-form-structure': {
    kind: 'model_form',
    model: 'fix.payroll.structure',
    title: 'Salary Structure',
    back: 'M56-structures',
    tabs: [
      { id: 'profile', label: 'Grade & Scale', bn: 'স্কেল ও পদবী', icon: '🏷️', badge: '3' },
      { id: 'allowances', label: 'Salary Components', bn: 'বেতনের উপাদান', icon: '💵', badge: '4' },
      { id: 'statutory', label: 'Statutory Provisions', bn: 'আইনগত তহবিল', icon: '📉', badge: '2' }
    ],
    sections: [
      {
        tab: 'profile',
        title: 'Salary Grade Profile',
        note: 'Compensation grade reference mapped to establishment register and National Pay Scale alignment.',
        fields: [
          { name: 'name', required: true, label: 'Structure Name' },
          { name: 'grade', label: 'Grade / Pay Band' },
          { name: 'active', label: 'Active Status' }
        ]
      },
      {
        tab: 'allowances',
        title: 'Remuneration & Allowances Breakdown',
        note: 'Percentages of Gross Salary under Bangladesh Labour Act guidelines (Basic minimum 50%, House Rent up to 40%).',
        fields: [
          { name: 'basic_pct', required: true, label: 'Basic Salary % of Gross' },
          { name: 'house_rent_pct', required: true, label: 'House Rent Allowance % of Gross' },
          { name: 'transport_fixed', label: 'Fixed Conveyance Allowance (BDT)' },
          { name: 'medical_fixed', label: 'Fixed Medical Allowance (BDT)' }
        ]
      },
      {
        tab: 'statutory',
        title: 'Statutory Funds & Terminal Benefits',
        note: 'Provident Fund (BLA s.264) and Gratuity (BLA s.2(10)/s.27) calculation flags.',
        fields: [
          { name: 'pf_applicable', label: 'Provident Fund (PF) Applicable' },
          { name: 'gratuity_applicable', label: 'Gratuity Scheme Applicable' }
        ]
      }
    ]
  },

  'M56-form-run': {
    kind: 'model_form',
    model: 'fix.payroll.period',
    title: 'Payroll Run',
    back: 'M56-runs',
    status: {
      field: 'state', labels: {
        draft: 'Draft', attendance_locked: 'Attendance Locked', calculated: 'Calculated',
        approved: 'Approved', paid: 'Paid', posted: 'Posted'
      }
    },
    tabs: [
      { id: 'schedule', label: 'Period Scope', bn: 'সময়সীমা ও শাখা', icon: '📅', badge: '4' },
      { id: 'controls', label: 'Processing & Accounting', bn: 'প্রক্রিয়াকরণ ও হিসাব', icon: '⚙️', badge: '5' }
    ],
    sections: [
      {
        tab: 'schedule',
        title: 'Payroll Cycle Schedule',
        note: 'Monthly payroll run schedule. Requires attendance lock before calculation.',
        fields: [
          { name: 'name', required: true, label: 'Period Reference (e.g. OCT-2026)' },
          { name: 'period_start', required: true, label: 'Period Start Date' },
          { name: 'period_end', required: true, label: 'Period End Date' },
          { name: 'operating_unit_id', label: 'Operating Unit' }
        ]
      },
      {
        tab: 'controls',
        title: 'Workflow & Gating Controls',
        note: 'Draft → attendance locked → calculated → approved → paid → posted. The state and the approval stamps change only through the actions above (maker-checker), never by editing.',
        fields: [
          { name: 'state', readonly: true, label: 'Payroll State' },
          { name: 'calculator_id', readonly: true, label: 'Calculated By' },
          { name: 'approved_by_id', readonly: true, label: 'Approved By' },
          { name: 'approved_on', readonly: true, label: 'Approved On' },
          { name: 'approved_net_total', readonly: true, label: 'Approved Net Total (BDT)' }
        ]
      }
    ]
  },

  'M56-form-bonus': {
    kind: 'model_form',
    model: 'fix.payroll.bonus.run',
    title: 'Festival Bonus Run',
    back: 'M56-bonus',
    status: {
      field: 'state', labels: {
        draft: 'Draft', approved: 'Approved', paid: 'Paid'
      }
    },
    tabs: [
      { id: 'event', label: 'Festival Event', bn: 'উৎসবের বিবরণ', icon: '🎁', badge: '3' },
      { id: 'rules', label: 'Disbursement Rules', bn: 'বিতরণ বিধি', icon: '📊', badge: '3' }
    ],
    sections: [
      {
        tab: 'event',
        title: 'Festival Bonus Event',
        note: 'Statutory festival holiday bonus (Eid-ul-Fitr, Eid-ul-Adha, Durga Puja, Christmas, Buddha Purnima).',
        fields: [
          { name: 'festival', required: true, label: 'Festival Category' },
          { name: 'bonus_date', required: true, label: 'Disbursement Date' },
          { name: 'operating_unit_id', label: 'Branch / Operating Unit' }
        ]
      },
      {
        tab: 'rules',
        title: 'Computation Multiplier & Parameters',
        note: 'Bonus calculated as a fraction or multiple of Basic or Gross wages.',
        fields: [
          { name: 'basis', required: true, label: 'Calculation Basis (Basic / Gross)' },
          { name: 'multiplier', required: true, label: 'Multiplier (Fraction of Basic)' },
          { name: 'state', readonly: true, label: 'State' }
        ]
      }
    ]
  },

  'M56-form-offcycle': {
    kind: 'model_form',
    model: 'fix.payroll.offcycle',
    title: 'Off-Cycle Payment',
    back: 'M56-offcycle',
    status: {
      field: 'state', labels: {
        draft: 'Draft', approved: 'Approved', paid: 'Paid', cancelled: 'Cancelled'
      }
    },
    tabs: [
      { id: 'claim', label: 'Payment Claim', bn: 'দাবির বিবরণ', icon: '💳', badge: '4' },
      { id: 'execution', label: 'Approval & Reason', bn: 'কারণ ও অনুমোদন', icon: '🏦', badge: '5' }
    ],
    sections: [
      {
        tab: 'claim',
        title: 'Off-Cycle Disbursement',
        note: 'Disbursement outside normal payroll run (arrears, field allowance adjustments, separation partial settlement).',
        fields: [
          { name: 'employee_id', required: true, label: 'Employee' },
          { name: 'payment_type', required: true, label: 'Payment Type' },
          { name: 'payment_date', required: true, label: 'Payment Date' },
          { name: 'amount', required: true, label: 'Payment Amount (BDT)' }
        ]
      },
      {
        tab: 'execution',
        title: 'Business Reason & Authorization',
        note: 'Approved by a Payroll Manager other than the preparer; amount and payee freeze at approval.',
        fields: [
          { name: 'reason', label: 'Operational Reason' },
          { name: 'state', readonly: true, label: 'State' },
          { name: 'prepared_by_id', readonly: true, label: 'Prepared By' },
          { name: 'approved_by_id', readonly: true, label: 'Approved By' },
          { name: 'approved_on', readonly: true, label: 'Approved On' }
        ]
      }
    ]
  },


  'M56-form-payslip': {
    kind: 'model_form',
    model: 'fix.payslip',
    title: 'Employee Payslip',
    back: 'M56-payslips',
    tabs: [
      { id: 'employee', label: 'Employee & Tax Profile', bn: 'কর্মী ও কর প্রোফাইল', icon: '👤', badge: '5' },
      { id: 'earnings', label: 'Contract Earnings & Allowances', bn: 'মূল বেতন ও ভাতা', icon: '💵', badge: '9' },
      { id: 'deductions', label: 'OT, Incentives & Deductions', bn: 'অতিরিক্ত সময় ও কর্তন', icon: '📉', badge: '8' },
      { id: 'terminal', label: 'Gratuity & Retrenchment', bn: 'গ্র্যাচুইটি ও নিষ্পত্তি', icon: '🏦', badge: '6' }
    ],
    sections: [
      {
        tab: 'employee',
        title: 'Payslip Period & Taxpayer Classification',
        note: 'Employee payroll period and Income Tax Act 2023 slab classification. A payslip is produced by the payroll run (Calculate Gross-to-Net) and is never typed.',
        fields: [
          { name: 'period_id', readonly: true, label: 'Payroll Period' },
          { name: 'employee_id', readonly: true, label: 'Employee' },
          { name: 'taxpayer_category', readonly: true, label: 'Taxpayer Slab Category' },
          { name: 'minimum_tax_location', readonly: true, label: 'Minimum Tax Jurisdiction' },
          { name: 'has_disabled_child', readonly: true, label: 'Disabled Child Tax Relief (+BDT 50,000)' }
        ]
      },
      {
        tab: 'earnings',
        title: 'Monthly Basic & Contract Allowances (BDT)',
        note: 'Pulled from active employment contract (F-1 contract-to-payslip allowance seam).',
        fields: [
          { name: 'basic', readonly: true, label: 'Basic Salary (BDT)' },
          { name: 'house_rent', readonly: true, label: 'House Rent Allowance (BDT)' },
          { name: 'medical_allowance', readonly: true, label: 'Medical Allowance (BDT)' },
          { name: 'conveyance_allowance', readonly: true, label: 'Conveyance Allowance (BDT)' },
          { name: 'technical_allowance', readonly: true, label: 'Technical Skill Allowance (BDT)' },
          { name: 'other_allowance', readonly: true, label: 'Other Monthly Allowance (BDT)' },
          { name: 'dearness_allowance', readonly: true, label: 'Dearness Allowance (BDT)' },
          { name: 'adhoc_allowance', readonly: true, label: 'Ad-hoc Relief Allowance (BDT)' },
          { name: 'gross', readonly: true, label: 'Total Monthly Gross Pay (BDT)' }
        ]
      },
      {
        tab: 'deductions',
        title: 'Overtime (208 Divisor), Incentives & Statutory Deductions',
        note: 'BLA s.108 double-rate overtime (208-hour divisor), M57 incentives, PF, and ITA 2023 TDS.',
        fields: [
          { name: 'ot_hours', readonly: true, label: 'Approved Overtime Hours' },
          { name: 'overtime', readonly: true, label: 'Overtime Pay (2x Rate, 208 Divisor)' },
          { name: 'incentive', readonly: true, label: 'Performance Incentive (M57)' },
          { name: 'pf_employee_pct', readonly: true, label: 'PF Employee Contribution %' },
          { name: 'pf_employee', readonly: true, label: 'PF Employee Deduction (BDT)' },
          { name: 'pf_employer', readonly: true, label: 'PF Employer Contribution (BDT)' },
          { name: 'tax_withheld', readonly: true, label: 'Monthly Income Tax Withheld (TDS)' },
          { name: 'net', readonly: true, label: 'Net Take-Home Pay (BDT)' }
        ]
      },
      {
        tab: 'terminal',
        title: 'Separation Gratuity & Retrenchment Compensation',
        note: 'BLA s.2(10)/s.27 gratuity, s.117 leave encashment, and s.20 retrenchment.',
        fields: [
          { name: 'completed_years', readonly: true, label: 'Completed Service Years' },
          { name: 'unused_leave_days', readonly: true, label: 'Unavailed Earned Leave Days (Cap 40)' },
          { name: 'gratuity_amount', readonly: true, label: 'Computed Gratuity (BDT)' },
          { name: 'leave_encashment_amount', readonly: true, label: 'Leave Encashment (BDT)' },
          { name: 'retrenchment_compensation', readonly: true, label: 'Retrenchment Compensation (BDT)' },
          { name: 'notice_pay_amount', readonly: true, label: 'Notice Pay (BDT)' }
        ]
      }
    ]
  },

  'M56-form-beftn': {
    kind: 'model_form',
    model: 'fix.beftn.batch',
    title: 'BEFTN Bank Disbursement Batch',
    back: 'M56-beftn',
    status: {
      field: 'state', labels: {
        draft: 'Draft', submitted: 'Submitted', settled: 'Settled', failed: 'Failed'
      }
    },
    tabs: [
      { id: 'batch', label: 'Batch Summary', bn: 'ব্যাচ সারসংক্ষেপ', icon: '🏦', badge: '5' },
      { id: 'file', label: 'BEFTN File & Settlement', bn: 'ফাইল ও নিষ্পত্তি', icon: '📄', badge: '3' }
    ],
    sections: [
      {
        tab: 'batch',
        title: 'Bangladesh Electronic Funds Transfer Network (BEFTN) Batch',
        note: 'Automated salary credit instruction batch for commercial bank clearing.',
        fields: [
          { name: 'period_id', readonly: true, label: 'Payroll Period' },
          { name: 'settlement_date', readonly: true, label: 'Target Settlement Date' },
          { name: 'employee_count', readonly: true, label: 'Payee Count' },
          { name: 'total_amount', readonly: true, label: 'Total Disbursement Amount (BDT)' },
          { name: 'operating_unit_id', readonly: true, label: 'Operating Unit' }
        ]
      },
      {
        tab: 'file',
        title: 'Generated Clearing File & Status',
        note: 'Generated CSV/XML clearing file payload and settlement state.',
        fields: [
          { name: 'file_name', readonly: true, label: 'Generated BEFTN File Name' },
          { name: 'submitted_at', readonly: true, label: 'Submitted Timestamp' },
          { name: 'state', readonly: true, label: 'Settlement State' }
        ]
      }
    ]
  },

  'M56-form-certificate': {
    kind: 'model_form',
    model: 'fix.payroll.certificate',
    title: 'Tax & Salary Certificate (ITA 2023 s.184)',
    back: 'M56-certificates',
    status: { field: 'state', labels: { draft: 'Draft', issued: 'Issued' } },
    tabs: [
      { id: 'scope', label: 'Certificate Scope', bn: 'সনদের বিবরণ', icon: '📜', badge: '6' },
      { id: 'breakdown', label: 'Annual Earnings & Challans', bn: 'বার্ষিক বেতন ও চালান', icon: '🧾', badge: '7' }
    ],
    sections: [
      {
        tab: 'scope',
        title: 'Employee Tax / Salary Certificate Particulars',
        note: 'Annual tax deduction and salary statement under Income Tax Act 2023.',
        fields: [
          { name: 'name', label: 'Certificate Number' },
          { name: 'employee_id', required: true, label: 'Employee' },
          { name: 'certificate_type', required: true, label: 'Certificate Type' },
          { name: 'fiscal_year', required: true, label: 'Fiscal Year (e.g. 2025-26)' },
          { name: 'issued_on', readonly: true, label: 'Issue Date' },
          { name: 'state', readonly: true, label: 'Certificate State' }
        ]
      },
      {
        tab: 'breakdown',
        title: 'Aggregated Annual Remuneration & Treasury Challans',
        note: 'Computed from posted payslips for the fiscal year.',
        fields: [
          { name: 'amount', readonly: true, label: 'Total Certified Amount (BDT)' },
          { name: 'total_gross', readonly: true, label: 'Annual Gross Salary (BDT)' },
          { name: 'total_basic', readonly: true, label: 'Annual Basic Salary (BDT)' },
          { name: 'total_allowances', readonly: true, label: 'Annual Allowances (BDT)' },
          { name: 'total_tax_withheld', readonly: true, label: 'Total Tax Deducted at Source (BDT)' },
          { name: 'total_pf_deducted', readonly: true, label: 'Total PF Employee Contribution (BDT)' },
          { name: 'challan_refs', label: 'Treasury / e-TDS Challan References' }
        ]
      }
    ]
  },

  'M56-form-return': {
    kind: 'model_form',
    model: 'fix.payroll.return',
    title: 'Withholding Tax Return (ITA 2023 s.177)',
    back: 'M56-returns',
    status: { field: 'state', labels: { draft: 'Draft', filed: 'Filed' } },
    tabs: [
      { id: 'summary', label: 'Return Period & Totals', bn: 'রিটার্ন সময়কাল ও কর', icon: '📊', badge: '6' },
      { id: 'challan', label: 'Challan & NBR Filing', bn: 'চালান ও প্রাপ্তিস্বীকার', icon: '🏛️', badge: '5' }
    ],
    sections: [
      {
        tab: 'summary',
        title: 'Withholding Tax Return Summary',
        note: 'Reconciles employee TDS deductions across payroll periods.',
        fields: [
          { name: 'name', label: 'Return Reference' },
          { name: 'period', required: true, label: 'Return Quarter / Period' },
          { name: 'period_start', label: 'Period Start Date' },
          { name: 'period_end', label: 'Period End Date' },
          { name: 'employee_count', readonly: true, label: 'Taxable Employees Count' },
          { name: 'total_tax', readonly: true, label: 'Total Tax Withheld (BDT)' }
        ]
      },
      {
        tab: 'challan',
        title: 'Treasury Challan & NBR Acknowledgement',
        note: 'Bangladesh Bank / Sonali Bank treasury challan deposit and NBR filing receipt.',
        fields: [
          { name: 'challan_number', label: 'Treasury Challan Number' },
          { name: 'challan_date', label: 'Challan Deposit Date' },
          { name: 'tax_zone', label: 'NBR Tax Zone' },
          { name: 'acknowledgement', label: 'NBR Filing Acknowledgement No' },
          { name: 'state', readonly: true, label: 'Filing State' }
        ]
      }
    ]
  },

  'M56-form-wppf': {
    kind: 'model_form',
    model: 'fix.wppf.allocation',
    title: 'WPPF Profit Allocation (BLA Ch. XV)',
    back: 'M56-wppf',
    status: {
      field: 'state', labels: {
        draft: 'Draft', calculated: 'Calculated', approved: 'Trustee Approved', posted: 'Disbursed & Posted'
      }
    },
    tabs: [
      { id: 'profit', label: 'Net Profit & 5% Pool', bn: 'নিট মুনাফা ও ৫% তহবিল', icon: '📈', badge: '5' },
      { id: 'funds', label: '80:10:10 Statutory Split', bn: '৮০:১০:১০ তহবিল বিভাজন', icon: '⚖️', badge: '4' },
      { id: 'distribution', label: 'Equal Distribution & Deadline', bn: 'সমান বণ্টন ও সময়সীমা', icon: '🏦', badge: '6' }
    ],
    sections: [
      {
        tab: 'profit',
        title: 'Fiscal Year Net Profit & 5% Statutory Pool (BLA s.234)',
        note: '5% of audited net profit before tax allocated to Workers Profit Participation Fund.',
        fields: [
          { name: 'name', label: 'Allocation Reference' },
          { name: 'fiscal_year', required: true, label: 'Fiscal Year (e.g. 2025-26)' },
          { name: 'fiscal_year_end_date', required: true, label: 'Fiscal Year End Date' },
          { name: 'net_profit', required: true, label: 'Audited Net Profit Before Tax (BDT)' },
          { name: 'total_wppf_pool', readonly: true, label: 'Total 5% Statutory Allocation (BDT)' }
        ]
      },
      {
        tab: 'funds',
        title: 'Statutory 80 : 10 : 10 Three-Fund Split (BLA s.240)',
        note: '80% Participatory Fund, 10% Employee Welfare Fund, 10% Govt BWWF Foundation.',
        fields: [
          { name: 'participatory_fund_amount', readonly: true, label: '80% Participatory Fund (BDT)' },
          { name: 'welfare_fund_amount', readonly: true, label: '10% Welfare Fund (BDT)' },
          { name: 'welfare_foundation_amount', readonly: true, label: '10% BWWF Govt Foundation Fund (BDT)' },
          { name: 'state', readonly: true, label: 'Allocation State' }
        ]
      },
      {
        tab: 'distribution',
        title: 'Beneficiary Equal Distribution & 9-Month Statutory Deadline (BLA s.242)',
        note: 'Two-thirds distributed equally in cash to eligible workers (>=9 months service); one-third invested.',
        fields: [
          { name: 'equal_distribution_pool', readonly: true, label: '2/3 Cash Distribution Pool (BDT)' },
          { name: 'investment_pool_share', readonly: true, label: '1/3 Investment Units Pool (BDT)' },
          { name: 'eligible_workers_count', label: 'Eligible Beneficiaries Count' },
          { name: 'per_worker_equal_share', readonly: true, label: 'Equal Cash Share per Worker (BDT)' },
          { name: 'distribution_due_date', readonly: true, label: 'Statutory 9-Month Transfer Deadline' },
          { name: 'bwwf_challan_ref', label: 'BWWF Deposit Challan Ref' }
        ]
      }
    ]
  }
};

export const REPORT_ROUTES = {
  'M56:Salary Register': 'M56-rpt-register',
  'M56:Payroll Cost Allocation': 'M56-rpt-alloc',
  'M56:Tax Deduction Summary': 'M56-rpt-tax',
  'M56:PF & Gratuity Provisions': 'M56-rpt-pf',
  'M56:Payroll Variance': 'M56-rpt-variance'
};

export const FORM_MODELS = {
  'M56:Salary Structure': 'fix.payroll.structure',
  'M56:Payroll Run': 'fix.payroll.period',
  'M56:Bonus Run': 'fix.payroll.bonus.run',
  'M56:Final Settlement': 'fix.payroll.offcycle'
};

export const FORM_CHIPS = {
  'M56:Salary Structure': 'M56-form-structure',
  'M56:Payroll Run': 'M56-form-run',
  'M56:Bonus Run': 'M56-form-bonus',
  'M56:Final Settlement': 'M56-form-offcycle',
  'M56:__by_model__': {
    'fix.payroll.structure': 'M56-form-structure',
    'fix.payroll.period': 'M56-form-run',
    'fix.payslip': 'M56-form-payslip',
    'fix.beftn.batch': 'M56-form-beftn',
    'fix.payroll.bonus.run': 'M56-form-bonus',
    'fix.payroll.offcycle': 'M56-form-offcycle',
    'fix.payroll.certificate': 'M56-form-certificate',
    'fix.payroll.return': 'M56-form-return',
    'fix.wppf.allocation': 'M56-form-wppf'
  },
  'M56:__by_screen__': {
    'M56-structures': 'M56-form-structure',
    'M56-runs': 'M56-form-run',
    'M56-payslips': 'M56-form-payslip',
    'M56-beftn': 'M56-form-beftn',
    'M56-bonus': 'M56-form-bonus',
    'M56-settlement': 'M56-form-offcycle',
    'M56-offcycle': 'M56-form-offcycle',
    'M56-certificates': 'M56-form-certificate',
    'M56-returns': 'M56-form-return',
    'M56-wppf': 'M56-form-wppf'
  }
};

export const CREATE = {
  M56: { screen: 'M56-form-run', model: 'fix.payroll.period', label: 'Payroll Run' }
};
