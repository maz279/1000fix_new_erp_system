import os

a09_dir = os.path.abspath("addons/platform/cd_p03_portal/static/src/a09")


def update_file(filename, mutator_fn):
    p = os.path.join(a09_dir, filename)
    with open(p, encoding="utf-8") as f:
        content = f.read()
    new_content = mutator_fn(content)
    if new_content != content:
        with open(p, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Successfully upgraded {filename}")
    else:
        print(f"No changes made to {filename}")


# ==================== M21 ====================
def upgrade_m21(c):
    # Enable period: true on reports
    c = c.replace(
        "'M21-orgchart': { kind: 'table_report', module: 'M21', report: 'org_distribution', title: 'Org Distribution', period: false }",
        "'M21-orgchart': { kind: 'table_report', module: 'M21', report: 'org_distribution', title: 'Org Distribution', period: true }",
    )
    c = c.replace(
        "'M21-movement': { kind: 'table_report', module: 'M21', report: 'headcount_movement', title: 'Movement History', period: false }",
        "'M21-movement': { kind: 'table_report', module: 'M21', report: 'headcount_movement', title: 'Movement History', period: true }",
    )
    c = c.replace(
        "'M21-ess': { kind: 'table_report', module: 'M21', report: 'probation_conversion', title: 'ESS / MSS — Probation Conversions Due', period: false }",
        "'M21-ess': { kind: 'table_report', module: 'M21', report: 'probation_conversion', title: 'ESS / MSS — Probation Conversions Due', period: true }",
    )
    c = c.replace(
        "'M21-rpt-headcount': { kind: 'table_report', module: 'M21', report: 'headcount_movement', title: 'Headcount & Movement', period: false }",
        "'M21-rpt-headcount': { kind: 'table_report', module: 'M21', report: 'headcount_movement', title: 'Headcount & Movement', period: true }",
    )
    c = c.replace(
        "'M21-rpt-attrition': { kind: 'table_report', module: 'M21', report: 'attrition_analysis', title: 'Attrition Analysis', period: false }",
        "'M21-rpt-attrition': { kind: 'table_report', module: 'M21', report: 'attrition_analysis', title: 'Attrition Analysis', period: true }",
    )
    c = c.replace(
        "'M21-rpt-probation': { kind: 'table_report', module: 'M21', report: 'probation_conversion', title: 'Probation Conversion', period: false }",
        "'M21-rpt-probation': { kind: 'table_report', module: 'M21', report: 'probation_conversion', title: 'Probation Conversion', period: true }",
    )
    c = c.replace(
        "'M21-rpt-establishment': { kind: 'table_report', module: 'M21', report: 'establishment_register', title: 'Establishment Register', period: false }",
        "'M21-rpt-establishment': { kind: 'table_report', module: 'M21', report: 'establishment_register', title: 'Establishment Register', period: true }",
    )

    # Wire workflow actions into M21-hire
    c = c.replace(
        "'M21-hire': { kind: 'model_list', model: 'fix.employment.contract', stateField: 'state',\n    cols: ['employee_id', 'contract_type', 'joining_date', 'probation_end', 'basic_monthly', 'legal_signoff_state', 'state'] }",
        "'M21-hire': { kind: 'model_list', model: 'fix.employment.contract', stateField: 'state',\n    cols: ['employee_id', 'contract_type', 'joining_date', 'probation_end', 'basic_monthly', 'legal_signoff_state', 'state'],\n    actions: [\n      { m: 'action_request_legal_signoff', l: 'Request Legal Signoff' },\n      { m: 'action_approve_legal_signoff', l: 'Approve Legal Signoff' },\n      { m: 'action_activate', l: 'Activate' },\n      { m: 'action_terminate', l: 'Terminate' }\n    ] }",
    )
    # Positions cols
    c = c.replace(
        "'M21-positions': { kind: 'model_list', model: 'fix.org.position',\n    cols: ['name', 'parent_id', 'grade', 'operating_unit_id'] }",
        "'M21-positions': { kind: 'model_list', model: 'fix.org.position',\n    cols: ['name', 'parent_id', 'grade', 'operating_unit_id', 'company_id'] }",
    )
    return c


# ==================== M55 ====================
def upgrade_m55(c):
    # Enable period: true
    c = c.replace(
        "'M55-balances': { kind: 'table_report', module: 'M55', report: 'leave_utilisation', title: 'Leave Utilisation', period: false }",
        "'M55-balances': { kind: 'table_report', module: 'M55', report: 'leave_utilisation', title: 'Leave Utilisation', period: true }",
    )
    c = c.replace(
        "'M55-rpt-leave': { kind: 'table_report', module: 'M55', report: 'leave_utilisation', title: 'Leave Utilisation', period: false }",
        "'M55-rpt-leave': { kind: 'table_report', module: 'M55', report: 'leave_utilisation', title: 'Leave Utilisation', period: true }",
    )

    # Wire M55-devices
    c = c.replace(
        "'M55-devices': { kind: 'model_list', model: 'fix.biometric.device',\n    cols: ['name', 'device_id', 'model_type', 'branch_id', 'ip_address', 'active'] }",
        "'M55-devices': { kind: 'model_list', model: 'fix.biometric.device',\n    cols: ['name', 'device_id', 'model_type', 'branch_id', 'ip_address', 'location_desc', 'status', 'active'],\n    actions: [{ m: 'action_ingest_punch', l: 'Ingest Punches' }] }",
    )
    # Wire M55-leave actions
    c = c.replace(
        "'M55-leave': { kind: 'model_list', model: 'fix.leave.request', stateField: 'state',\n    cols: ['employee_id', 'leave_type_id', 'date_from', 'date_to', 'days', 'state'] }",
        "'M55-leave': { kind: 'model_list', model: 'fix.leave.request', stateField: 'state',\n    cols: ['employee_id', 'leave_type_id', 'date_from', 'date_to', 'days', 'reason', 'state'],\n    actions: [{ m: 'action_approve', l: 'Approve' }] }",
    )
    # Wire M55-attendance-lock
    c = c.replace(
        "'M55-attendance-lock': { kind: 'model_list', model: 'fix.attendance.lock',\n    cols: ['name', 'period_start', 'period_end', 'state'] }",
        "'M55-attendance-lock': { kind: 'model_list', model: 'fix.attendance.lock', stateField: 'state',\n    cols: ['name', 'period_start', 'period_end', 'operating_unit_id', 'state'],\n    actions: [{ m: 'action_lock', l: 'Lock Period' }, { m: 'action_unlock', l: 'Unlock' }] }",
    )
    # Add form for attendance lock if not present
    if "'M55-form-attendance-lock'" not in c:
        form_lock = """  'M55-form-attendance-lock': {
    kind: 'model_form',
    model: 'fix.attendance.lock',
    title: 'Attendance Lock Period',
    back: 'M55-attendance-lock',
    status: { field: 'state', labels: { draft: 'Draft', locked: 'Locked' } },
    sections: [
      { title: 'Lock Period', note: 'Attendance verification lock prevents alterations to punch logs for payroll cycle.',
        fields: [
          { name: 'name', required: true, label: 'Period Reference' },
          { name: 'period_start', required: true, label: 'Start Date' },
          { name: 'period_end', required: true, label: 'End Date' },
          { name: 'operating_unit_id', label: 'Operating Unit / Branch' },
          { name: 'state', required: true, label: 'State' }
        ] }
    ]
  },
"""
        c = c.replace("export const FORM_MODELS =", form_lock + "export const FORM_MODELS =")
        c = c.replace("'M55-attendance-lock': 'M55-form-attendance-lock'", "")
        c = c.replace("'fix.attendance.lock': 'M55-form-attendance-lock'", "")
        c = c.replace(
            "'M55:__by_model__': {",
            "'M55:__by_model__': {\n    'fix.attendance.lock': 'M55-form-attendance-lock',",
        )
        c = c.replace(
            "'M55:__by_screen__': {",
            "'M55:__by_screen__': {\n    'M55-attendance-lock': 'M55-form-attendance-lock',",
        )
    return c


# ==================== M56 ====================
def upgrade_m56(c):
    # Enable period: true
    c = c.replace(
        "'M56-tax': { kind: 'table_report', module: 'M56', report: 'tax_deduction_summary', title: 'Income Tax (AY 2026-27)', period: false }",
        "'M56-tax': { kind: 'table_report', module: 'M56', report: 'tax_deduction_summary', title: 'Income Tax (AY 2026-27)', period: true }",
    )
    c = c.replace(
        "'M56-pf': { kind: 'table_report', module: 'M56', report: 'pf_gratuity', title: 'Provident Fund', period: false }",
        "'M56-pf': { kind: 'table_report', module: 'M56', report: 'pf_gratuity', title: 'Provident Fund', period: true }",
    )
    c = c.replace(
        "'M56-gratuity': { kind: 'table_report', module: 'M56', report: 'pf_gratuity', title: 'Gratuity & Encashment', period: false }",
        "'M56-gratuity': { kind: 'table_report', module: 'M56', report: 'pf_gratuity', title: 'Gratuity & Encashment', period: true }",
    )
    c = c.replace(
        "'M56-rpt-register': { kind: 'table_report', module: 'M56', report: 'salary_register', title: 'Salary Register', period: false }",
        "'M56-rpt-register': { kind: 'table_report', module: 'M56', report: 'salary_register', title: 'Salary Register', period: true }",
    )
    c = c.replace(
        "'M56-rpt-alloc': { kind: 'table_report', module: 'M56', report: 'payroll_cost_allocation', title: 'Payroll Cost Allocation', period: false }",
        "'M56-rpt-alloc': { kind: 'table_report', module: 'M56', report: 'payroll_cost_allocation', title: 'Payroll Cost Allocation', period: true }",
    )
    c = c.replace(
        "'M56-rpt-tax': { kind: 'table_report', module: 'M56', report: 'tax_deduction_summary', title: 'Tax Deduction Summary', period: false }",
        "'M56-rpt-tax': { kind: 'table_report', module: 'M56', report: 'tax_deduction_summary', title: 'Tax Deduction Summary', period: true }",
    )
    c = c.replace(
        "'M56-rpt-pf': { kind: 'table_report', module: 'M56', report: 'pf_gratuity', title: 'PF & Gratuity Provisions', period: false }",
        "'M56-rpt-pf': { kind: 'table_report', module: 'M56', report: 'pf_gratuity', title: 'PF & Gratuity Provisions', period: true }",
    )
    c = c.replace(
        "'M56-rpt-variance': { kind: 'table_report', module: 'M56', report: 'payroll_variance', title: 'Payroll Variance', period: false }",
        "'M56-rpt-variance': { kind: 'table_report', module: 'M56', report: 'payroll_variance', title: 'Payroll Variance', period: true }",
    )

    # Wire M56-runs actions
    c = c.replace(
        "actions: [{ m: 'action_calculate', l: 'Calculate' }, { m: 'action_approve', l: 'Approve' },\n              { m: 'action_pay', l: 'Mark Paid' }, { m: 'action_post', l: 'Post' }]",
        "actions: [{ m: 'action_verify_attendance_locked', l: 'Verify Attendance Lock (M55)' }, { m: 'action_calculate', l: 'Calculate Gross-to-Net' }, { m: 'action_approve', l: 'Approve' }, { m: 'action_pay', l: 'Mark Paid' }, { m: 'action_post', l: 'Post to GL (M19)' }]",
    )
    # Wire M56-payslips
    c = c.replace(
        "'M56-payslips': { kind: 'model_list', create: false, model: 'fix.payslip',\n    cols: ['period_id', 'employee_id', 'basic', 'gross', 'overtime', 'pf_employee', 'tax_withheld', 'net'] }",
        "'M56-payslips': { kind: 'model_list', create: false, model: 'fix.payslip',\n    cols: ['period_id', 'employee_id', 'basic', 'ot_hours', 'incentive', 'pf_employee_pct', 'pf_employer_pct', 'annual_taxable_other', 'taxpayer_category'],\n    actions: [{ m: 'action_compute_separation', l: 'Compute Separation' }, { m: 'action_compute_retrenchment', l: 'Compute Retrenchment' }] }",
    )
    return c


# ==================== M57 ====================
def upgrade_m57(c):
    # Enable period: true
    c = c.replace(
        "'M57-calibration': { kind: 'table_report', module: 'M57', report: 'calibration_summary', title: 'Calibration Summary', period: false }",
        "'M57-calibration': { kind: 'table_report', module: 'M57', report: 'calibration_summary', title: 'Calibration Summary', period: true }",
    )
    c = c.replace(
        "'M57-rpt-ratings': { kind: 'table_report', module: 'M57', report: 'rating_distribution', title: 'Rating Distribution', period: false }",
        "'M57-rpt-ratings': { kind: 'table_report', module: 'M57', report: 'rating_distribution', title: 'Rating Distribution', period: true }",
    )
    c = c.replace(
        "'M57-rpt-payout': { kind: 'table_report', module: 'M57', report: 'incentive_payout', title: 'Incentive Payout by Scheme', period: false }",
        "'M57-rpt-payout': { kind: 'table_report', module: 'M57', report: 'incentive_payout', title: 'Incentive Payout by Scheme', period: true }",
    )
    c = c.replace(
        "'M57-rpt-scorecards': { kind: 'table_report', module: 'M57', report: 'technician_scorecards', title: 'Technician Scorecards', period: false }",
        "'M57-rpt-scorecards': { kind: 'table_report', module: 'M57', report: 'technician_scorecards', title: 'Technician Scorecards', period: true }",
    )
    c = c.replace(
        "'M57-rpt-calib': { kind: 'table_report', module: 'M57', report: 'calibration_summary', title: 'Calibration Summary', period: false }",
        "'M57-rpt-calib': { kind: 'table_report', module: 'M57', report: 'calibration_summary', title: 'Calibration Summary', period: true }",
    )
    c = c.replace(
        "'M57-rpt-pip': { kind: 'table_report', module: 'M57', report: 'pip_outcomes', title: 'PIP Outcomes', period: false }",
        "'M57-rpt-pip': { kind: 'table_report', module: 'M57', report: 'pip_outcomes', title: 'PIP Outcomes', period: true }",
    )

    # Wire M57-kpis
    c = c.replace(
        "'M57-kpis': { kind: 'model_list', create: false, model: 'fix.performance.scorecard',\n    cols: ['employee_id', 'period', 'first_time_fix', 'sla_hit', 'csat', 'rework_rate', 'score'] }",
        "'M57-kpis': { kind: 'model_list', create: false, model: 'fix.performance.scorecard',\n    cols: ['employee_id', 'period', 'first_time_fix', 'sla_hit', 'csat', 'rework_rate', 'score'],\n    actions: [{ m: 'action_publish', l: 'Publish Scorecard' }] }",
    )
    # Wire M57-schemes
    c = c.replace(
        "'M57-schemes': { kind: 'model_list', model: 'fix.incentive.run', stateField: 'state',\n    cols: ['period', 'band_base', 'total', 'state'] }",
        "'M57-schemes': { kind: 'model_list', model: 'fix.incentive.run', stateField: 'state',\n    cols: ['period', 'band_base', 'total', 'state'],\n    actions: [{ m: 'action_compute', l: 'Calculate Pool' }, { m: 'action_apply', l: 'Apply to Payroll (M56)' }] }",
    )
    # Enrich M57-comp and M57-succession
    c = c.replace(
        "'M57-comp': { kind: 'model_list', model: 'fix.compensation.band',\n    cols: ['name', 'grade', 'range_min', 'range_mid', 'range_max'] }",
        "'M57-comp': { kind: 'model_list', model: 'fix.compensation.band',\n    cols: ['name', 'grade', 'range_min', 'range_mid', 'range_max', 'company_id'] }",
    )
    c = c.replace(
        "'M57-succession': { kind: 'model_list', model: 'fix.succession.plan',\n    cols: ['position_name', 'incumbent_id', 'successor_id', 'readiness', 'risk'] }",
        "'M57-succession': { kind: 'model_list', model: 'fix.succession.plan',\n    cols: ['position_name', 'incumbent_id', 'successor_id', 'readiness', 'risk', 'company_id'] }",
    )
    return c


# ==================== M22 ====================
def upgrade_m22(c):
    # Enable period: true
    c = c.replace(
        "'M22-matrix': { kind: 'table_report', module: 'M22', report: 'skill_gap_heatmap', title: 'Skill Matrix', period: false }",
        "'M22-matrix': { kind: 'table_report', module: 'M22', report: 'skill_gap_heatmap', title: 'Skill Matrix', period: true }",
    )
    c = c.replace(
        "'M22-expiry': { kind: 'table_report', module: 'M22', report: 'expiry_forecast', title: 'Validity & Renewal', period: false }",
        "'M22-expiry': { kind: 'table_report', module: 'M22', report: 'expiry_forecast', title: 'Validity & Renewal', period: true }",
    )
    c = c.replace(
        "'M22-rpt-coverage': { kind: 'table_report', module: 'M22', report: 'certification_coverage', title: 'Certification Coverage by Brand', period: false }",
        "'M22-rpt-coverage': { kind: 'table_report', module: 'M22', report: 'certification_coverage', title: 'Certification Coverage by Brand', period: true }",
    )
    c = c.replace(
        "'M22-rpt-expiry': { kind: 'table_report', module: 'M22', report: 'expiry_forecast', title: 'Expiry Forecast', period: false }",
        "'M22-rpt-expiry': { kind: 'table_report', module: 'M22', report: 'expiry_forecast', title: 'Expiry Forecast', period: true }",
    )
    c = c.replace(
        "'M22-rpt-training': { kind: 'table_report', module: 'M22', report: 'training_effectiveness', title: 'Training Effectiveness', period: false }",
        "'M22-rpt-training': { kind: 'table_report', module: 'M22', report: 'training_effectiveness', title: 'Training Effectiveness', period: true }",
    )
    c = c.replace(
        "'M22-rpt-skillgap': { kind: 'table_report', module: 'M22', report: 'skill_gap_heatmap', title: 'Skill-Gap Heatmap', period: false }",
        "'M22-rpt-skillgap': { kind: 'table_report', module: 'M22', report: 'skill_gap_heatmap', title: 'Skill-Gap Heatmap', period: true }",
    )
    c = c.replace(
        "'M22-rpt-audit': { kind: 'table_report', module: 'M22', report: 'audit_evidence', title: 'Audit Evidence Pack', period: false }",
        "'M22-rpt-audit': { kind: 'table_report', module: 'M22', report: 'audit_evidence', title: 'Audit Evidence Pack', period: true }",
    )

    # Wire M22-register and M22-eligibility
    c = c.replace(
        "'M22-register': { kind: 'model_list', model: 'fix.certification', stateField: 'status',\n    cols: ['employee_id', 'competency_id', 'issued_on', 'expires_on', 'evidence_ref', 'status'] }",
        "'M22-register': { kind: 'model_list', model: 'fix.certification', stateField: 'status',\n    cols: ['employee_id', 'competency_id', 'issued_on', 'expires_on', 'evidence_ref', 'status'],\n    actions: [{ m: 'action_grant', l: 'Grant Certification' }, { m: 'action_mark_expired', l: 'Mark Expired / Block' }] }",
    )
    c = c.replace(
        "'M22-eligibility': { kind: 'model_list', model: 'fix.certification', stateField: 'status',\n    cols: ['employee_id', 'competency_id', 'expires_on', 'status'] }",
        "'M22-eligibility': { kind: 'model_list', model: 'fix.certification', stateField: 'status',\n    cols: ['employee_id', 'competency_id', 'issued_on', 'expires_on', 'evidence_ref', 'status'],\n    actions: [{ m: 'action_grant', l: 'Grant Certification' }, { m: 'action_mark_expired', l: 'Hard Block Dispatch (M02)' }] }",
    )
    # Wire M22-catalogue
    c = c.replace(
        "'M22-catalogue': { kind: 'model_list', model: 'fix.training.course',\n    cols: ['code', 'name', 'competency_id', 'content_ref'] }",
        "'M22-catalogue': { kind: 'model_list', model: 'fix.training.course',\n    cols: ['code', 'name', 'competency_id', 'content_ref'],\n    actions: [{ m: 'action_enroll', l: 'Enroll Techs' }] }",
    )
    # Wire M22-schedule
    c = c.replace(
        "'M22-schedule': { kind: 'model_list', model: 'fix.training.enrollment', stateField: 'state',\n    cols: ['course_id', 'employee_id', 'state', 'completed_on'] }",
        "'M22-schedule': { kind: 'model_list', model: 'fix.training.enrollment', stateField: 'state',\n    cols: ['course_id', 'employee_id', 'completed_on', 'state'],\n    actions: [{ m: 'action_pass', l: 'Mark Passed / Certified' }] }",
    )
    return c


# ==================== M58 ====================
def upgrade_m58(c):
    # Enable period: true
    c = c.replace(
        "'M58-practical': { kind: 'table_report', module: 'M58', report: 'practical_results', title: 'Practical Assessment Results', period: false }",
        "'M58-practical': { kind: 'table_report', module: 'M58', report: 'practical_results', title: 'Practical Assessment Results', period: true }",
    )
    c = c.replace(
        "'M58-rpt-funnel': { kind: 'table_report', module: 'M58', report: 'funnel_conversion', title: 'Funnel & Conversion', period: false }",
        "'M58-rpt-funnel': { kind: 'table_report', module: 'M58', report: 'funnel_conversion', title: 'Funnel & Conversion', period: true }",
    )
    c = c.replace(
        "'M58-rpt-ttf': { kind: 'table_report', module: 'M58', report: 'time_to_fill', title: 'Time-to-Fill by Role', period: false }",
        "'M58-rpt-ttf': { kind: 'table_report', module: 'M58', report: 'time_to_fill', title: 'Time-to-Fill by Role', period: true }",
    )
    c = c.replace(
        "'M58-rpt-source': { kind: 'table_report', module: 'M58', report: 'source_effectiveness', title: 'Source Effectiveness', period: false }",
        "'M58-rpt-source': { kind: 'table_report', module: 'M58', report: 'source_effectiveness', title: 'Source Effectiveness', period: true }",
    )
    c = c.replace(
        "'M58-rpt-retention': { kind: 'table_report', module: 'M58', report: 'first90_retention', title: 'First-90 Retention', period: false }",
        "'M58-rpt-retention': { kind: 'table_report', module: 'M58', report: 'first90_retention', title: 'First-90 Retention', period: true }",
    )
    c = c.replace(
        "'M58-rpt-practical': { kind: 'table_report', module: 'M58', report: 'practical_results', title: 'Practical Assessment Results', period: false }",
        "'M58-rpt-practical': { kind: 'table_report', module: 'M58', report: 'practical_results', title: 'Practical Assessment Results', period: true }",
    )

    # Wire M58-reqs
    c = c.replace(
        "'M58-reqs': { kind: 'model_list', model: 'fix.job.requisition', stateField: 'state',\n    cols: ['name', 'department_id', 'position_id', 'openings', 'state'] }",
        "'M58-reqs': { kind: 'model_list', model: 'fix.job.requisition', stateField: 'state',\n    cols: ['name', 'department_id', 'position_id', 'openings', 'operating_unit_id', 'state'],\n    actions: [{ m: 'action_open', l: 'Approve Requisition' }, { m: 'action_hired', l: 'Mark Hired' }] }",
    )
    # Wire M58-candidates
    c = c.replace(
        "'M58-candidates': { kind: 'model_list', model: 'fix.candidate', stateField: 'state',\n    cols: ['name', 'email', 'phone', 'requisition_id', 'state'] }",
        "'M58-candidates': { kind: 'model_list', model: 'fix.candidate', stateField: 'state',\n    cols: ['name', 'email', 'phone', 'requisition_id', 'operating_unit_id', 'state'],\n    actions: [{ m: 'action_screen', l: 'Screen' }, { m: 'action_interview', l: 'Invite to Interview' }, { m: 'action_offer', l: 'Generate Offer' }, { m: 'action_hire', l: 'Hire' }] }",
    )
    # Wire M58-preboard
    c = c.replace(
        "'M58-preboard': { kind: 'model_list', model: 'fix.onboarding.plan',\n    cols: ['name', 'candidate_id', 'position_id', 'joined_date', 'employee_id'] }",
        "'M58-preboard': { kind: 'model_list', model: 'fix.onboarding.plan',\n    cols: ['name', 'candidate_id', 'requisition_id', 'employee_id', 'joined_date', 'nid_verified', 'contract_signed', 'it_assets_allocated'],\n    actions: [{ m: 'action_start', l: 'Start Onboarding' }, { m: 'action_complete', l: 'Complete (Create Employee)' }] }",
    )
    # Wire M58-talent-assessment
    c = c.replace(
        "'M58-talent-assessment': { kind: 'model_list', model: 'fix.talent.assessment',\n    cols: ['name'] }",
        "'M58-talent-assessment': { kind: 'model_list', model: 'fix.talent.assessment',\n    cols: ['name', 'candidate_id', 'competency_code', 'assessor_id', 'assessed_on', 'score', 'passed'] }",
    )
    return c


# ==================== M59 ====================
def upgrade_m59(c):
    # Enable period: true
    c = c.replace(
        "'M59-statutory': { kind: 'table_report', module: 'M59', report: 'statutory_compliance', title: 'Statutory Notification Clock', period: false }",
        "'M59-statutory': { kind: 'table_report', module: 'M59', report: 'statutory_compliance', title: 'Statutory Notification Clock', period: true }",
    )
    c = c.replace(
        "'M59-rpt-incidents': { kind: 'table_report', module: 'M59', report: 'incident_statistics', title: 'Incident Statistics', period: false }",
        "'M59-rpt-incidents': { kind: 'table_report', module: 'M59', report: 'incident_statistics', title: 'Incident Statistics', period: true }",
    )
    c = c.replace(
        "'M59-rpt-leading': { kind: 'table_report', module: 'M59', report: 'leading_indicators', title: 'Leading Indicators', period: false }",
        "'M59-rpt-leading': { kind: 'table_report', module: 'M59', report: 'leading_indicators', title: 'Leading Indicators', period: true }",
    )
    c = c.replace(
        "'M59-rpt-statutory': { kind: 'table_report', module: 'M59', report: 'statutory_compliance', title: 'Statutory Compliance', period: false }",
        "'M59-rpt-statutory': { kind: 'table_report', module: 'M59', report: 'statutory_compliance', title: 'Statutory Compliance', period: true }",
    )
    c = c.replace(
        "'M59-rpt-ppe': { kind: 'table_report', module: 'M59', report: 'ppe_compliance', title: 'PPE Compliance', period: false }",
        "'M59-rpt-ppe': { kind: 'table_report', module: 'M59', report: 'ppe_compliance', title: 'PPE Compliance', period: true }",
    )
    c = c.replace(
        "'M59-rpt-drills': { kind: 'table_report', module: 'M59', report: 'drill_coverage', title: 'Drill Calendar Coverage', period: false }",
        "'M59-rpt-drills': { kind: 'table_report', module: 'M59', report: 'drill_coverage', title: 'Drill Calendar Coverage', period: true }",
    )

    # Wire M59-battery
    c = c.replace(
        "'M59-battery': { kind: 'model_list', model: 'fix.hazardous.substance.register',\n    cols: ['name'] }",
        "'M59-battery': { kind: 'model_list', model: 'fix.hazardous.substance.register', stateField: 'state',\n    cols: ['name', 'un_number', 'storage_location', 'current_stock_litres', 'max_allowable_litres', 'msds_on_file', 'fire_suppression_type', 'state'] }",
    )
    # Wire M59-ppe
    c = c.replace(
        "'M59-ppe': { kind: 'model_list', model: 'fix.ppe.register',\n    cols: ['name', 'item_type', 'regulatory_standard', 'stock_quantity'] }",
        "'M59-ppe': { kind: 'model_list', model: 'fix.ppe.register', stateField: 'state',\n    cols: ['name', 'item_type', 'regulatory_standard', 'stock_quantity', 'min_required_quantity', 'state'],\n    actions: [{ m: 'check_replenishment', l: 'Check Replenishment' }] }",
    )
    # Wire M59-statutory-accident-register
    c = c.replace(
        "'M59-statutory-accident-register': { kind: 'model_list', model: 'fix.statutory.accident.register',\n    cols: ['name'] }",
        "'M59-statutory-accident-register': { kind: 'model_list', model: 'fix.statutory.accident.register',\n    cols: ['name', 'incident_id', 'employee_id', 'accident_date', 'nature_of_injury', 'affected_body_part', 'lost_work_days', 'dife_notified', 'dife_notification_date', 'statutory_compensation_bdt'],\n    actions: [{ m: 'action_notify_dife', l: 'Notify DIFE (Statutory Clock)' }] }",
    )
    # Wire M59-safety-inspection
    c = c.replace(
        "'M59-safety-inspection': { kind: 'model_list', model: 'fix.safety.inspection',\n    cols: ['name'] }",
        "'M59-safety-inspection': { kind: 'model_list', model: 'fix.safety.inspection',\n    cols: ['name', 'branch_id', 'inspected_on', 'inspector_id', 'fire_extinguisher_ok', 'emergency_exit_ok', 'first_aid_ok', 'electrical_ok', 'esd_grounding_ok', 'fume_extraction_ok'],\n    actions: [{ m: 'action_complete', l: 'Complete Inspection' }] }",
    )
    # Wire M59-committee
    c = c.replace(
        "'M59-committee': { kind: 'model_list', model: 'fix.safety.committee',\n    cols: ['name', 'branch_id', 'formation_date', 'chairperson_id', 'secretary_id', 'member_count'] }",
        "'M59-committee': { kind: 'model_list', model: 'fix.safety.committee',\n    cols: ['name', 'branch_id', 'formation_date', 'chairperson_id', 'secretary_id', 'member_count', 'meeting_frequency', 'last_meeting_date', 'next_meeting_date'],\n    actions: [{ m: 'action_record_meeting', l: 'Record Meeting' }] }",
    )
    # Wire M59-wellbeing
    c = c.replace(
        "'M59-wellbeing': { kind: 'model_list', model: 'fix.hse.health', stateField: 'state',\n    cols: ['name', 'employee_id', 'record_type', 'record_date', 'valid_until', 'fitness', 'state'] }",
        "'M59-wellbeing': { kind: 'model_list', model: 'fix.hse.health', stateField: 'state',\n    cols: ['name', 'employee_id', 'record_type', 'record_date', 'valid_until', 'fitness', 'restrictions', 'clinician', 'state'],\n    actions: [{ m: 'action_close', l: 'Close Record' }] }",
    )
    return c


update_file("m21.js", upgrade_m21)
update_file("m55.js", upgrade_m55)
update_file("m56.js", upgrade_m56)
update_file("m57.js", upgrade_m57)
update_file("m22.js", upgrade_m22)
update_file("m58.js", upgrade_m58)
update_file("m59.js", upgrade_m59)
