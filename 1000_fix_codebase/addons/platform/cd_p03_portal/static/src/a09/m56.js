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
        { id: 'M56-offcycle', en: 'Off-Cycle Payments', bn: 'অফ-সাইকেল', t: 'g' },
        { id: 'M56-variance', en: 'Variance Review', bn: 'বেতন পার্থক্য পর্যালোচনা', t: 'g' },
        { id: 'M56-recoveries', en: 'Overpayment Recoveries', bn: 'অতিরিক্ত প্রদান আদায়', t: 'g' },
        { id: 'M56-recovery-lines', en: 'Recovery Deductions', bn: 'আদায় কর্তন', t: 'g' },
        { id: 'M56-bank-checks', en: 'Bank-Change Confirmations', bn: 'ব্যাংক পরিবর্তন নিশ্চিতকরণ', t: 'g' }
      ]
    },
    {
      en: 'Statutory', screens: [
        { id: 'M56-tax', en: 'Income Tax (AY 2026-27)', bn: 'আয়কর', t: 'r' },
        { id: 'M56-pf', en: 'Provident Fund', bn: 'প্রভিডেন্ট ফান্ড', t: 'r' },
        { id: 'M56-gratuity', en: 'Gratuity & Encashment', bn: 'গ্র্যাচুইটি', t: 'r' },
        { id: 'M56-bonus', en: 'Festival Bonus', bn: 'উৎসব বোনাস', t: 'g' },
        { id: 'M56-bonus-lines', en: 'Festival Bonus Lines', bn: 'উৎসব বোনাস লাইন', t: 'g' },
        { id: 'M56-packs', en: 'Statutory Packs', bn: 'বিধিবদ্ধ হার প্যাক', t: 'g' },
        { id: 'M56-gratuity-accrual', en: 'Gratuity Provision', bn: 'গ্র্যাচুইটি সঞ্চিতি', t: 'g' }
      ]
    },
    {
      en: 'Disbursement', screens: [
        { id: 'M56-beftn', en: 'BEFTN Bank Files', bn: 'বিইএফটিএন', t: 'g' },
        { id: 'M56-certificates', en: 'Certificates & Tax Statements', bn: 'সনদ', t: 'g' },
        { id: 'M56-my-payslips', en: 'My Payslips', bn: 'আমার বেতন বিবরণী', t: 'r' },
        { id: 'M56-bank-returns', en: 'BEFTN Bank Returns', bn: 'ব্যাংক ফেরত', t: 'g' },
        { id: 'M56-bank-return-lines', en: 'Bank Return Items', bn: 'ব্যাংক ফেরত আইটেম', t: 'g' },
        { id: 'M56-mfs', en: 'MFS Disbursements', bn: 'এমএফএস বিতরণ', t: 'g' },
        { id: 'M56-mfs-returns', en: 'MFS Provider Returns', bn: 'এমএফএস ফেরত', t: 'g' },
        { id: 'M56-mfs-return-lines', en: 'MFS Return Items', bn: 'এমএফএস ফেরত আইটেম', t: 'g' },
        { id: 'M56-nominee-accounts', en: 'Nominee Accounts (s.19)', bn: 'নমিনি হিসাব', t: 'g' }
      ]
    },
    {
      en: 'Compliance', screens: [
        { id: 'M56-returns', en: 'Withholding Returns (Quarterly)', bn: 'উৎসে কর রিটার্ন', t: 'g' },
        { id: 'M56-settlement', en: 'Final Settlements', bn: 'চূড়ান্ত নিষ্পত্তি', t: 'g' },
        { id: 'M56-wppf', en: 'WPPF Profit Sharing (BLA Ch. XV)', bn: 'ডব্লিউপিপিএফ মুনাফা অংশগ্রহণ', t: 'g' },
        { id: 'M56-wppf-beneficiaries', en: 'WPPF Beneficiaries', bn: 'ডব্লিউপিপিএফ সুবিধাভোগী', t: 'g' }
      ]
    }
  ],
  reports: ['Salary Register', 'Payroll Cost Allocation', 'Tax Deduction Summary', 'PF & Gratuity Provisions', 'Payroll Variance', 'Gratuity Provision'],
  forms: ['Salary Structure', 'Payroll Run', 'Bonus Run', 'Final Settlement'],
  cross: ['M21 Workforce', 'M55 Attendance', 'M19 General Ledger', 'M51 TDS', 'M50 Treasury'],
  freg: {
    src: 82, sub: [
      ['1', 'Gross-to-Net Engine', 14, { model: 'fix.payslip', cols: ['period_id', 'employee_id', 'gross', 'tax_withheld', 'net'], screens: ['M56-payslips', 'M56-structures'], reports: ['Salary Register'], forms: ['Salary Structure'] }],
      ['2', 'BD Income Tax', 12, { model: 'fix.payslip', cols: ['employee_id', 'period_id', 'taxpayer_category', 'annual_taxable_other', 'tax_withheld'], screens: ['M56-tax'], reports: ['Tax Deduction Summary'], forms: [] }],
      ['3', 'Provident Fund', 7, { model: 'fix.payslip', cols: ['employee_id', 'period_id', 'basic', 'pf_employee', 'pf_employer'], screens: ['M56-pf'], reports: ['PF & Gratuity Provisions'], forms: [] }],
      ['4', 'Gratuity', 7, { model: 'fix.payslip', cols: ['employee_id', 'period_id', 'completed_years', 'basic', 'gratuity_amount'], screens: ['M56-gratuity'], reports: ['PF & Gratuity Provisions', 'Gratuity Provision'], forms: [] }],
      ['5', 'Bonus & Encashment', 7, { model: 'fix.payroll.bonus.run', cols: ['name', 'festival', 'bonus_date', 'total_amount', 'state'], screens: ['M56-bonus', 'M56-wppf'], reports: [], forms: ['Bonus Run'] }],
      ['6', 'Loans & Advances', 6, { model: 'fix.payroll.offcycle', cols: ['name', 'employee_id', 'payment_date', 'amount', 'state'], screens: ['M56-offcycle'], reports: [], forms: [], domain: [['payment_type', '=', 'advance']] }],
      ['7', 'Runs & Off-Cycle', 9, { model: 'fix.payroll.period', cols: ['name', 'period_start', 'period_end', 'calculator_id', 'state'], screens: ['M56-runs', 'M56-offcycle'], reports: ['Salary Register', 'Payroll Variance', 'Payroll Cost Allocation'], forms: ['Payroll Run'] }],
      ['8', 'BEFTN & Payslips', 8, { model: 'fix.beftn.batch', cols: ['period_id', 'settlement_date', 'employee_count', 'total_amount', 'state'], screens: ['M56-beftn', 'M56-payslips'], reports: ['Salary Register'], forms: [] }],
      ['9', 'Returns & Certificates', 7, { model: 'fix.payroll.return', cols: ['name', 'period', 'total_tax', 'challan_number', 'state'], screens: ['M56-returns', 'M56-certificates'], reports: ['Tax Deduction Summary'], forms: [] }],
      ['10', 'Final Settlement', 5, { model: 'fix.payroll.offcycle', cols: ['name', 'employee_id', 'payment_date', 'amount', 'state'], screens: ['M56-settlement'], reports: [], forms: ['Final Settlement'], domain: [['payment_type', '=', 'settlement']] }]
    ]
  }
};

export const SCREENS = {
  'M56-runs': {
    kind: 'model_list', model: 'fix.payroll.period', stateField: 'state',
    cols: ['name', 'period_start', 'period_end', 'slip_count', 'gross_total', 'tax_total', 'net_total', 'state'],
    actions: [{ m: 'action_verify_attendance_locked', l: 'Verify Attendance Lock (M55)' }, { m: 'action_trial_run', l: 'Trial Run (never pays)' }, { m: 'action_calculate', l: 'Calculate Gross-to-Net' }, { m: 'action_prevalidate', l: 'Validate Run' }, { m: 'action_request_approval', l: 'Request Approval' }, { m: 'action_recall_approval', l: 'Recall Approval Request' }, { m: 'action_pay', l: 'Release to Bank (BEFTN)' }, { m: 'action_post', l: 'Post to GL (M19)' }, { m: 'action_publish_payslips', l: 'Publish Payslips' }]
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
    cols: ['name', 'employee_id', 'payment_type', 'payment_date', 'amount', 'approval_state', 'state'],
    actions: [{ m: 'action_request_approval', l: 'Request Approval' }, { m: 'action_recall_approval', l: 'Recall Approval Request' }, { m: 'action_pay', l: 'Release to Bank (BEFTN)' }, { m: 'action_post', l: 'Post to GL (M19)' }, { m: 'action_cancel', l: 'Cancel' }]
  },
  'M56-tax': { kind: 'table_report', module: 'M56', report: 'tax_deduction_summary', title: 'Income Tax (AY 2026-27)', period: true },
  'M56-pf': { kind: 'table_report', module: 'M56', report: 'pf_gratuity', title: 'Provident Fund', period: true },
  'M56-gratuity': { kind: 'table_report', module: 'M56', report: 'pf_gratuity', title: 'Gratuity & Encashment', period: true },
  /* A09 M56-9: computed per employee (one year's service, capped at one
   * month's basic, r.111(5)); never typed. */
  'M56-bonus-lines': { kind: 'model_list', model: 'fix.payroll.bonus.line', create: false,
    cols: ['run_id', 'employee_id', 'completed_years', 'basic', 'base_amount', 'amount', 'capped'] },
  'M56-bonus': {
    kind: 'model_list', model: 'fix.payroll.bonus.run', stateField: 'state',
    cols: ['name', 'festival', 'bonus_date', 'basis', 'multiplier', 'employee_count', 'total_amount', 'approval_state', 'state'],
    actions: [{ m: 'action_compute', l: 'Compute Eligible Bonus' }, { m: 'action_request_approval', l: 'Request Approval' }, { m: 'action_recall_approval', l: 'Recall Approval Request' }, { m: 'action_pay', l: 'Release to Bank (BEFTN)' }, { m: 'action_post', l: 'Post to GL (M19)' }, { m: 'action_cancel', l: 'Cancel' }]
  },
  'M56-beftn': {
    kind: 'model_list', create: false, model: 'fix.beftn.batch', stateField: 'state',
    cols: ['period_id', 'settlement_date', 'employee_count', 'total_amount', 'file_name', 'bank_confirmation_ref', 'state'],
    actions: [{ m: 'action_settle', l: 'Settle (Bank Confirmation)' }]
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
    cols: ['name', 'employee_id', 'payment_date', 'amount', 'reason', 'approval_state', 'state'],
    actions: [{ m: 'action_request_approval', l: 'Request Approval' }, { m: 'action_recall_approval', l: 'Recall Approval Request' }, { m: 'action_pay', l: 'Release to Bank (BEFTN)' }, { m: 'action_post', l: 'Post to GL (M19)' }]
  },
  'M56-wppf': {
    kind: 'model_list', model: 'fix.wppf.allocation', stateField: 'state',
    cols: ['name', 'fiscal_year', 'net_profit', 'total_wppf_pool', 'participatory_fund_amount', 'welfare_fund_amount', 'welfare_foundation_amount', 'eligible_workers_count', 'state'],
    actions: [{ m: 'action_calculate', l: 'Calculate 80:10:10 Split' }, { m: 'action_request_approval', l: 'Request Trustee Approval' }, { m: 'action_recall_approval', l: 'Recall Approval Request' }, { m: 'action_post', l: 'Disburse & Post' }, { m: 'action_pay_bwwf', l: 'Record BWWF Payment (Finance)' }]
  },
  /* ---- A09 round 2 ---- */
  'M56-wppf-beneficiaries': {
    kind: 'model_list', create: false, model: 'fix.wppf.beneficiary',
    cols: ['allocation_id', 'employee_id', 'service_months', 'auto_reason', 'worker_status', 'eligible', 'share_amount', 'tds_amount', 'net_share']
  },
  /* M56-11: approved from the M63 inbox by a second Payroll Manager */
  'M56-packs': {
    kind: 'model_list', model: 'fix.statutory.pack', stateField: 'state',
    cols: ['name', 'company_id', 'version', 'effective_from', 'basis', 'tax_table_rule', 'ot_divisor_hours', 'exemption_ceiling', 'separation_rule', 'approval_state', 'state'],
    actions: [{ m: 'action_request_approval', l: 'Request Approval (second Payroll Manager)' }, { m: 'action_recall_approval', l: 'Recall Approval Request' }, { m: 'action_cancel', l: 'Cancel Draft' }, { m: 'action_new_version', l: 'New Version', ask: 'Effective from (YYYY-MM-DD)', kwarg: 'effective_from' }]
  },
  /* BRU-PAY-06: acknowledged by a reviewer who did not calculate the run */
  'M56-variance': {
    kind: 'model_list', create: false, model: 'fix.payroll.variance',
    cols: ['period_id', 'kind', 'employee_id', 'previous_net', 'current_net', 'variance', 'variance_pct', 'no_comparison', 'over_threshold', 'acknowledged_by_id'],
    actions: [{ m: 'action_acknowledge', l: 'Acknowledge Variance (reviewer)', ask: 'Why is this variance right?', kwarg: 'note' }]
  },
  /* M56-1: confirmed by a second person, never by whoever changed the account */
  'M56-bank-checks': {
    kind: 'model_list', create: false, model: 'fix.payroll.bank.check', stateField: 'state',
    cols: ['period_id', 'employee_id', 'account_hint', 'changed_on', 'confirmed_by_id', 'state'],
    actions: [{ m: 'action_confirm', l: 'Confirm Bank Change (second person)', ask: 'How was the new account confirmed?', kwarg: 'note' }]
  },
  /* M56-4: CSV "account,status[,reason]"; failed items re-issued by Finance */
  'M56-bank-returns': {
    kind: 'model_list', model: 'fix.beftn.return', stateField: 'state',
    cols: ['name', 'batch_id', 'imported_on', 'paid_count', 'failed_count', 'failed_amount', 'state'],
    actions: [{ m: 'action_import', l: 'Import Bank Return' }, { m: 'action_reissue', l: 'Re-issue Failed Items (BEFTN)' }]
  },
  'M56-bank-return-lines': {
    kind: 'model_list', create: false, model: 'fix.beftn.return.line',
    cols: ['return_id', 'employee_id', 'account_no', 'amount', 'status', 'reason', 'reissue_account_no', 'reissue_batch_id']
  },
  'M56-mfs': {
    kind: 'model_list', create: false, model: 'fix.mfs.disbursement', stateField: 'state',
    cols: ['name', 'period_id', 'provider', 'line_count', 'total_amount', 'file_name', 'confirmation_ref', 'state'],
    actions: [{ m: 'action_settle', l: 'Settle (Provider Confirmation)' }]
  },
  /* BRU-PAY-04: routed; deducted after tax from the next runs, capped monthly */
  'M56-recoveries': {
    kind: 'model_list', model: 'fix.payroll.recovery', stateField: 'state',
    cols: ['name', 'employee_id', 'correction_slip_id', 'amount', 'recovered_amount', 'remaining_amount', 'approval_state', 'state'],
    actions: [{ m: 'action_request_approval', l: 'Request Approval' }, { m: 'action_recall_approval', l: 'Recall Approval Request' }, { m: 'action_cancel', l: 'Cancel' }]
  },
  'M56-recovery-lines': {
    kind: 'model_list', create: false, model: 'fix.payroll.recovery.line',
    cols: ['recovery_id', 'slip_id', 'amount']
  },
  /* CSV "wallet,status[,reason]"; failed wallets re-issued by Finance */
  'M56-mfs-returns': {
    kind: 'model_list', model: 'fix.mfs.return', stateField: 'state',
    cols: ['name', 'disbursement_id', 'imported_on', 'paid_count', 'failed_count', 'failed_amount', 'state'],
    actions: [{ m: 'action_import', l: 'Import Provider Return' }, { m: 'action_reissue', l: 'Re-issue Failed Wallets (MFS)' }]
  },
  'M56-mfs-return-lines': {
    kind: 'model_list', create: false, model: 'fix.mfs.return.line',
    cols: ['return_id', 'employee_id', 'provider', 'wallet', 'amount', 'status', 'reason', 'reissue_wallet', 'reissue_id']
  },
  /* BLA s.19: the account a death-in-service nominee is paid into */
  'M56-nominee-accounts': {
    kind: 'model_list', model: 'fix.payroll.nominee.account', stateField: 'state',
    cols: ['employee_id', 'nominee_name', 'bank_name', 'bank_account_no', 'routing_no', 'recorded_by_id', 'verified_by_id', 'state'],
    actions: [{ m: 'action_verify', l: 'Verify (second payroll user)' }, { m: 'action_cancel', l: 'Cancel' }]
  },
  'M56-gratuity-accrual': {
    kind: 'model_list', create: false, model: 'fix.payroll.gratuity.accrual',
    cols: ['month', 'employee_id', 'completed_years', 'basic', 'liability', 'previous_liability', 'accrual', 'move_id']
  },

  'M56-my-payslips': { kind: 'table_report', module: 'M56', report: 'my_payslips', title: 'My Payslips' },

  /* Report chips -> their own computed pack */
  'M56-rpt-register': { kind: 'table_report', module: 'M56', report: 'salary_register', title: 'Salary Register', period: true },
  'M56-rpt-alloc': { kind: 'table_report', module: 'M56', report: 'payroll_cost_allocation', title: 'Payroll Cost Allocation', period: true },
  'M56-rpt-tax': { kind: 'table_report', module: 'M56', report: 'tax_deduction_summary', title: 'Tax Deduction Summary', period: true },
  'M56-rpt-pf': { kind: 'table_report', module: 'M56', report: 'pf_gratuity', title: 'PF & Gratuity Provisions', period: true },
  'M56-rpt-variance': { kind: 'table_report', module: 'M56', report: 'payroll_variance', title: 'Payroll Variance', period: true },
  'M56-rpt-gratuity': { kind: 'table_report', module: 'M56', report: 'gratuity_provision', title: 'Gratuity Provision', period: true },

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
      { id: 'schedule', label: 'Period Scope', bn: 'সময়সীমা ও শাখা', icon: '📅', badge: '6' },
      { id: 'controls', label: 'Processing & Accounting', bn: 'প্রক্রিয়াকরণ ও হিসাব', icon: '⚙️', badge: '10' }
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
          { name: 'operating_unit_id', label: 'Operating Unit' },
          { name: 'company_account_no', label: 'Company Originating Account (BEFTN)' },
          { name: 'company_routing_no', label: 'Company Routing No (9 digits)' }
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
          { name: 'approved_net_total', readonly: true, label: 'Approved Net Total (BDT)' },
          { name: 'approval_state', readonly: true, label: 'Approval (M63 inbox)' },
          { name: 'released_by_id', readonly: true, label: 'Released to Bank By' },
          { name: 'released_on', readonly: true, label: 'Released On' },
          { name: 'payslips_published_on', readonly: true, label: 'Payslips Published On' },
          { name: 'calculation_note', readonly: true, label: 'Calculation Notes (who was paid, prorated or skipped)' },
          { name: 'trial_run_on', readonly: true, label: 'Last Trial Run (nothing paid)' },
          { name: 'trial_note', readonly: true, label: 'Trial Run Result' }
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
        draft: 'Draft', computed: 'Computed', approved: 'Approved', paid: 'Paid', posted: 'Posted', cancelled: 'Cancelled'
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
          { name: 'multiplier', required: true, label: 'Multiplier (capped at one month basic, r.111(5))' },
          { name: 'state', readonly: true, label: 'State' },
          { name: 'approval_state', readonly: true, label: 'Approval (M63 inbox)' },
          { name: 'employee_count', readonly: true, label: 'Eligible Employees' },
          { name: 'total_amount', readonly: true, label: 'Total Bonus (BDT)' },
          { name: 'total_tax', readonly: true, label: 'Tax Withheld (marginal rate, when ruled)' },
          { name: 'total_net', readonly: true, label: 'Net Paid (BDT)' },
          { name: 'total_recovery', readonly: true, label: 'Overpayments Recovered (BDT)' },
          { name: 'computed_by_id', readonly: true, label: 'Computed By' },
          { name: 'approved_by_id', readonly: true, label: 'Approved By' },
          { name: 'released_by_id', readonly: true, label: 'Released By' },
          { name: 'computation_note', readonly: true, label: 'Eligibility Notes' }
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
        draft: 'Draft', approved: 'Approved', paid: 'Paid', posted: 'Posted', cancelled: 'Cancelled'
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
          { name: 'amount', required: true, label: 'Payment Amount (BDT)' },
          { name: 'correction_slip_id', label: 'Corrects Paid Payslip (Post-Payment Correction only)' }
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
          { name: 'approved_on', readonly: true, label: 'Approved On' },
          { name: 'approval_state', readonly: true, label: 'Approval (M63 inbox)' },
          { name: 'bank_account_no', readonly: true, label: 'Payee Account (from the employee master)' },
          { name: 'routing_no', readonly: true, label: 'Payee Routing No' },
          { name: 'released_by_id', readonly: true, label: 'Released By' },
          { name: 'exit_id', readonly: true, label: 'Exit Settlement (I1)' },
          { name: 'hse_incident_ref', readonly: true, label: 'HSE Incident (I5)' },
          { name: 'nominee_name', readonly: true, label: 'Nominee Payee (BLA s.19)' },
          { name: 'nominee_share_pct', readonly: true, label: 'Nominee Share %' },
          { name: 'recovery_deduction', readonly: true, label: 'Overpayment Recovered (at request)' },
          { name: 'net_amount', readonly: true, label: 'Net Paid (BDT)' }
        ]
      }
    ]
  },


  'M56-form-payslip': {
    kind: 'model_form',
    model: 'fix.payslip',
    title: 'Employee Payslip',
    back: 'M56-payslips',
    /* a payslip is computed by its payroll run, never typed in (2026-11-12) */
    create: false, pick: 'A payslip is produced by its payroll run: open one from Payslips.',
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
          { name: 'has_disabled_child', readonly: true, label: 'Disabled Child Tax Relief (+BDT 50,000)' },
          { name: 'paid_days', readonly: true, label: 'Paid Days (prorated for a leaver)' },
          { name: 'statutory_basis', readonly: true, label: 'Statutory Basis (decision flags)' },
          { name: 'statutory_pack_id', readonly: true, label: 'Statutory Pack (pinned)' },
          { name: 'tds_method', readonly: true, label: 'TDS Method' },
          { name: 'payment_channel', readonly: true, label: 'Payment Channel' },
          { name: 'mfs_provider', readonly: true, label: 'MFS Provider' },
          { name: 'cost_operating_unit_id', readonly: true, label: 'Cost Operating Unit (GL)' },
          { name: 'cost_branch_id', readonly: true, label: 'Cost Branch (GL)' },
          { name: 'published', readonly: true, label: 'Published to Employee' },
          { name: 'published_on', readonly: true, label: 'Published On' }
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
          { name: 'annual_taxable', readonly: true, label: 'Projected Annual Taxable Income' },
          { name: 'ytd_prior_income', readonly: true, label: 'Fiscal-Year Income Before This Slip' },
          { name: 'ytd_prior_tax', readonly: true, label: 'Fiscal-Year Tax Before This Slip' },
          { name: 'retro_adjustment_total', readonly: true, label: 'Retro Attendance Adjustments (M55)' },
          { name: 'recovery_deduction', readonly: true, label: 'Overpayment Recovery (after tax)' },
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
        submitted: 'Submitted', settled: 'Settled'
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
          { name: 'file_digest', readonly: true, label: 'File SHA-256' },
          { name: 'submitted_at', readonly: true, label: 'Submitted Timestamp' },
          { name: 'released_by_id', readonly: true, label: 'Released By' },
          { name: 'bank_confirmation_ref', label: 'Bank Confirmation Reference' },
          { name: 'bank_confirmation_file', label: 'Bank Confirmation / Return File', type: 'file' },
          { name: 'settled_by_id', readonly: true, label: 'Settled By' },
          { name: 'settled_on', readonly: true, label: 'Settled On' },
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
          { name: 'issued_by_id', readonly: true, label: 'Issued By' },
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
          { name: 'due_date', readonly: true, label: 'Due Date' },
          { name: 'filed_by_id', readonly: true, label: 'Filed By' },
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
          { name: 'audited_statement_file', label: 'Audited Financial Statements', type: 'file' },
          { name: 'audit_report_ref', label: "Auditor's Report Reference" },
          { name: 'ledger_report_id', label: 'M19 Profit & Loss (ledger, for comparison)' },
          { name: 'ledger_net_profit', readonly: true, label: 'Ledger Net Profit (M19)' },
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
          { name: 'state', readonly: true, label: 'Allocation State' },
          { name: 'approval_state', readonly: true, label: 'Trustee Approval (M63 inbox)' },
          { name: 'trustee_board_resolution_ref', label: 'Board of Trustees Resolution Ref' },
          { name: 'trustee_resolution_file', label: 'Signed Trustee Resolution', type: 'file' }
        ]
      },
      {
        tab: 'distribution',
        title: 'Beneficiary Equal Distribution & 9-Month Statutory Deadline (BLA s.242)',
        note: 'Two-thirds distributed equally in cash to eligible workers (>=9 months service); one-third invested.',
        fields: [
          { name: 'equal_distribution_pool', readonly: true, label: '2/3 Cash Distribution Pool (BDT)' },
          { name: 'investment_pool_share', readonly: true, label: '1/3 Investment Units Pool (BDT)' },
          { name: 'eligible_workers_count', readonly: true, label: 'Eligible Beneficiaries (from the beneficiary lines)' },
          { name: 'per_worker_equal_share', readonly: true, label: 'Equal Cash Share per Worker (BDT)' },
          { name: 'distribution_due_date', readonly: true, label: 'Statutory 9-Month Transfer Deadline' },
          { name: 'bwwf_challan_ref', label: 'BWWF Deposit Challan Ref' },
          { name: 'bwwf_challan_date', label: 'BWWF Challan Date' },
          { name: 'bwwf_challan_file', label: 'BWWF Deposit Challan', type: 'file' },
          { name: 'bwwf_paid_by_id', readonly: true, label: 'BWWF Paid By (Finance)' },
          { name: 'bwwf_paid_on', readonly: true, label: 'BWWF Paid On' }
        ]
      }
    ]
  },
  'M56-form-pack': {
    kind: 'model_form',
    model: 'fix.statutory.pack',
    title: 'Payroll Statutory Pack',
    back: 'M56-packs',
    status: { field: 'state', labels: { baseline: 'As Coded (baseline)', draft: 'Draft', approved: 'Approved', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'figures', label: 'Figures & Effective Date', bn: 'হার ও কার্যকর তারিখ', icon: '📐', badge: '6' },
      { id: 'source', label: 'Source & Approval', bn: 'উৎস ও অনুমোদন', icon: '📜', badge: '8' }
    ],
    sections: [
      {
        tab: 'figures',
        title: 'The figures payroll computes with',
        note: 'A new figure is a new version. Version 1 is the code as it stood, unsourced; a sourced version carries its citation and evidence.',
        fields: [
          { name: 'effective_from', required: true, label: 'Effective From' },
          { name: 'tax_table_rule', required: true, label: 'Salary Tax Table' },
          { name: 'ot_divisor_hours', required: true, label: 'Overtime Divisor (hours / month)' },
          { name: 'exemption_ceiling', required: true, label: 'Para 27 Exemption Ceiling (BDT)' },
          { name: 'separation_rule', required: true, label: 'Gratuity & Resignation Bands' },
          { name: 'basis', required: true, label: 'Basis (as coded / sourced)' }
        ]
      },
      {
        tab: 'source',
        title: 'Citation, Evidence and the Two-Person Approval',
        note: 'Prepared by one Payroll Manager, approved from the M63 inbox by another.',
        fields: [
          { name: 'source_note', label: 'Source / Citation' },
          { name: 'source_file', label: 'Source Evidence', type: 'file' },
          { name: 'version', readonly: true, label: 'Version' },
          { name: 'state', readonly: true, label: 'State' },
          { name: 'approval_state', readonly: true, label: 'Approval (M63 inbox)' },
          { name: 'prepared_by_id', readonly: true, label: 'Prepared By' },
          { name: 'approved_by_id', readonly: true, label: 'Approved By' },
          { name: 'approved_on', readonly: true, label: 'Approved On' }
        ]
      }
    ]
  },

  'M56-form-bank-return': {
    kind: 'model_form',
    model: 'fix.beftn.return',
    title: 'BEFTN Bank Return',
    back: 'M56-bank-returns',
    status: { field: 'state', labels: { draft: 'Draft', imported: 'Imported' } },
    tabs: [
      { id: 'file', label: 'Return File', bn: 'ফেরত ফাইল', icon: '📄', badge: '3' },
      { id: 'result', label: 'Result', bn: 'ফলাফল', icon: '📊', badge: '6' }
    ],
    sections: [
      {
        tab: 'file',
        title: "The bank's per-item answer",
        note: 'CSV with a header row: account,status[,reason]; one row per credit; status paid or failed.',
        fields: [
          { name: 'batch_id', required: true, label: 'BEFTN Batch' },
          { name: 'return_file', required: true, label: 'Bank Return File (CSV)', type: 'file' },
          { name: 'name', readonly: true, label: 'Reference' }
        ]
      },
      {
        tab: 'result',
        title: 'Imported Result',
        note: 'Failed items are re-issued in a new BEFTN batch by Finance, to the account the employee master holds after an approved change.',
        fields: [
          { name: 'state', readonly: true, label: 'State' },
          { name: 'imported_by_id', readonly: true, label: 'Imported By' },
          { name: 'imported_on', readonly: true, label: 'Imported On' },
          { name: 'paid_count', readonly: true, label: 'Paid Items' },
          { name: 'failed_count', readonly: true, label: 'Failed Items' },
          { name: 'failed_amount', readonly: true, label: 'Failed Amount (BDT)' }
        ]
      }
    ]
  },

  'M56-form-mfs': {
    kind: 'model_form',
    model: 'fix.mfs.disbursement',
    title: 'MFS Salary Disbursement',
    back: 'M56-mfs',
    status: { field: 'state', labels: { submitted: 'Submitted', settled: 'Settled' } },
    tabs: [
      { id: 'file', label: 'Disbursement File', bn: 'বিতরণ ফাইল', icon: '📱', badge: '6' },
      { id: 'settle', label: 'Provider Confirmation', bn: 'নিশ্চিতকরণ', icon: '✅', badge: '4' }
    ],
    sections: [
      {
        tab: 'file',
        title: 'Wallet credits of a released run (one file per provider)',
        note: 'CSV: provider,wallet,amount,reference,employee_ref,employee_name.',
        fields: [
          { name: 'period_id', readonly: true, label: 'Payroll Period' },
          { name: 'provider', readonly: true, label: 'MFS Provider' },
          { name: 'line_count', readonly: true, label: 'Wallets' },
          { name: 'total_amount', readonly: true, label: 'Total (BDT)' },
          { name: 'file_name', readonly: true, label: 'File Name' },
          { name: 'file_digest', readonly: true, label: 'File SHA-256' }
        ]
      },
      {
        tab: 'settle',
        title: "The provider's confirmation",
        note: 'Settled by Finance against the provider confirmation, never on the date alone.',
        fields: [
          { name: 'confirmation_ref', label: 'Provider Confirmation Reference' },
          { name: 'confirmation_file', label: 'Provider Confirmation File', type: 'file' },
          { name: 'settled_by_id', readonly: true, label: 'Settled By' },
          { name: 'state', readonly: true, label: 'State' }
        ]
      }
    ]
  },

  'M56-form-recovery': {
    kind: 'model_form',
    model: 'fix.payroll.recovery',
    title: 'Salary Overpayment Recovery',
    back: 'M56-recoveries',
    status: { field: 'state', labels: { draft: 'Draft', approved: 'Approved', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'what', label: 'Overpayment', bn: 'অতিরিক্ত প্রদান', icon: '↩️', badge: '9' }
    ],
    sections: [
      {
        tab: 'what',
        title: 'What was overpaid, and how it comes back',
        note: 'The paid payslip is never edited: the recovery is deducted after tax from the next runs, up to the company monthly cap.',
        fields: [
          { name: 'correction_slip_id', required: true, label: 'Overpaid Payslip' },
          { name: 'amount', required: true, label: 'Overpaid Amount (BDT)' },
          { name: 'reason', required: true, label: 'What was overpaid and why' },
          { name: 'employee_id', readonly: true, label: 'Employee' },
          { name: 'recovered_amount', readonly: true, label: 'Recovered So Far' },
          { name: 'remaining_amount', readonly: true, label: 'Still Owed' },
          { name: 'approval_state', readonly: true, label: 'Approval (M63 inbox)' },
          { name: 'approved_by_id', readonly: true, label: 'Approved By' },
          { name: 'state', readonly: true, label: 'State' }
        ]
      }
    ]
  },

  'M56-form-mfs-return': {
    kind: 'model_form',
    model: 'fix.mfs.return',
    title: 'MFS Provider Return',
    back: 'M56-mfs-returns',
    status: { field: 'state', labels: { draft: 'Draft', imported: 'Imported' } },
    tabs: [
      { id: 'file', label: 'Return File', bn: 'ফেরত ফাইল', icon: '📱', badge: '7' }
    ],
    sections: [
      {
        tab: 'file',
        title: "The provider's per-wallet answer",
        note: 'CSV with a header row: wallet,status[,reason]; one row per credit; status paid or failed.',
        fields: [
          { name: 'disbursement_id', required: true, label: 'MFS Disbursement File' },
          { name: 'return_file', required: true, label: 'Provider Return File (CSV)', type: 'file' },
          { name: 'name', readonly: true, label: 'Reference' },
          { name: 'state', readonly: true, label: 'State' },
          { name: 'paid_count', readonly: true, label: 'Paid' },
          { name: 'failed_count', readonly: true, label: 'Failed' },
          { name: 'failed_amount', readonly: true, label: 'Failed Amount (BDT)' }
        ]
      }
    ]
  },

  'M56-form-nominee-account': {
    kind: 'model_form',
    model: 'fix.payroll.nominee.account',
    title: 'Nominee Payout Account (BLA s.19)',
    back: 'M56-nominee-accounts',
    status: { field: 'state', labels: { draft: 'Recorded', verified: 'Verified', cancelled: 'Cancelled' } },
    tabs: [
      { id: 'account', label: 'Nominee & Account', bn: 'নমিনি ও হিসাব', icon: '🏦', badge: '9' }
    ],
    sections: [
      {
        tab: 'account',
        title: "The nominee's bank account",
        note: 'Recorded by payroll with the cheque leaf or bank letter; verified by a second payroll user before any death-in-service payment is requested.',
        fields: [
          { name: 'employee_id', required: true, label: 'Deceased Employee' },
          { name: 'dependant_id', label: 'Nominee Record' },
          { name: 'nominee_name', required: true, label: 'Nominee Name' },
          { name: 'bank_name', label: 'Bank' },
          { name: 'bank_account_no', required: true, label: 'Account Number' },
          { name: 'routing_no', required: true, label: 'Routing No (9 digits)' },
          { name: 'evidence_file', label: 'Evidence (cheque leaf / bank letter)', type: 'file' },
          { name: 'recorded_by_id', readonly: true, label: 'Recorded By' },
          { name: 'verified_by_id', readonly: true, label: 'Verified By' }
        ]
      }
    ]
  },

  'M56-form-wppf-beneficiary': {
    kind: 'model_form',
    model: 'fix.wppf.beneficiary',
    title: 'WPPF Beneficiary',
    back: 'M56-wppf-beneficiaries',
    tabs: [
      { id: 'who', label: 'Eligibility', bn: 'যোগ্যতা', icon: '👷', badge: '8' }
    ],
    sections: [
      {
        tab: 'who',
        title: 'Worker classification (BLA s.2(65)) and share',
        note: 'Classified on a calculated allocation, before the trustees approve it; the share recomputes over the eligible workers.',
        fields: [
          { name: 'allocation_id', readonly: true, label: 'WPPF Allocation' },
          { name: 'employee_id', readonly: true, label: 'Employee' },
          { name: 'service_months', readonly: true, label: 'Service (months)' },
          { name: 'auto_reason', readonly: true, label: 'Excluded by Rule' },
          { name: 'worker_status', required: true, label: 'Worker Status' },
          { name: 'exclusion_reason', label: 'Why Not a Worker' },
          { name: 'share_amount', readonly: true, label: 'Cash Share (BDT)' },
          { name: 'net_share', readonly: true, label: 'Net of s.88 TDS (BDT)' }
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
  'M56:Payroll Variance': 'M56-rpt-variance',
  'M56:Gratuity Provision': 'M56-rpt-gratuity'
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
    'fix.wppf.allocation': 'M56-form-wppf',
    'fix.statutory.pack': 'M56-form-pack',
    'fix.beftn.return': 'M56-form-bank-return',
    'fix.mfs.disbursement': 'M56-form-mfs',
    'fix.wppf.beneficiary': 'M56-form-wppf-beneficiary',
    'fix.payroll.nominee.account': 'M56-form-nominee-account',
    'fix.payroll.recovery': 'M56-form-recovery',
    'fix.mfs.return': 'M56-form-mfs-return'
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
    'M56-wppf': 'M56-form-wppf',
    'M56-packs': 'M56-form-pack',
    'M56-bank-returns': 'M56-form-bank-return',
    'M56-mfs': 'M56-form-mfs',
    'M56-wppf-beneficiaries': 'M56-form-wppf-beneficiary',
    'M56-nominee-accounts': 'M56-form-nominee-account',
    'M56-recoveries': 'M56-form-recovery',
    'M56-mfs-returns': 'M56-form-mfs-return'
  }
};

export const CREATE = {
  M56: { screen: 'M56-form-run', model: 'fix.payroll.period', label: 'Payroll Run' }
};
